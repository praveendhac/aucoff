"""The JWKS fetch must use TLS and verify the identity provider's certificate (ZT-4)."""

import datetime
import json
import ssl
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import jwt
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.core.security import AuthenticationError, JWKSKeyResolver, TokenVerifier


def _cert(tmp: Path) -> tuple[Path, Path]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(hours=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    cert_file, key_file = tmp / "c.pem", tmp / "k.pem"
    cert_file.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_file.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return cert_file, key_file


@pytest.fixture
def idp(tmp_path: Path):  # type: ignore[no-untyped-def]
    signing = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(signing.public_key()))
    jwk.update({"kid": "k1", "use": "sig", "alg": "RS256"})
    body = json.dumps({"keys": [jwk]}).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: object) -> None:
            pass

    cert_file, key_file = _cert(tmp_path)
    server = HTTPServer(("127.0.0.1", 0), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"https://localhost:{server.server_port}/certs", cert_file, signing
    server.shutdown()


def _token(signing: rsa.RSAPrivateKey) -> str:
    now = datetime.datetime.now(datetime.UTC)
    claims = {
        "iss": "i",
        "aud": "a",
        "sub": "s",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=5),
    }
    return jwt.encode(claims, signing, algorithm="RS256", headers={"kid": "k1"})


def test_keys_are_fetched_over_tls_with_the_configured_ca(idp) -> None:  # type: ignore[no-untyped-def]
    url, ca, signing = idp
    verifier = TokenVerifier(JWKSKeyResolver(url, str(ca)), "i", "a")
    assert verifier.verify(_token(signing)).subject == "s"


def test_untrusted_certificate_is_rejected(idp) -> None:  # type: ignore[no-untyped-def]
    url, _ca, signing = idp
    verifier = TokenVerifier(JWKSKeyResolver(url), "i", "a")  # system store does not trust it
    with pytest.raises(AuthenticationError):
        verifier.verify(_token(signing))


def test_plain_http_jwks_url_is_refused() -> None:
    with pytest.raises(ValueError):
        JWKSKeyResolver("http://idp/certs")
