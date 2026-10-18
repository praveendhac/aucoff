#!/usr/bin/env python3
"""End-to-end browser-style login test for the web app (T-301).

Drives the real flow the way a browser does, without a browser: Auth.js starts the authorization
code + PKCE flow, Keycloak shows its login form, the synthetic local user signs in, the callback
sets the encrypted session cookie, and the BFF proxy then calls the API with the user's token.
Requires `kubectl port-forward svc/aucoff-keycloak 8443:8443` and the local CA file as argv[1];
the dev user's password is read from the cluster and never printed.
"""
import html
import http.cookiejar
import json
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

APP = "https://aucoff.localtest.me"
ca = sys.argv[1]
USER = sys.argv[2] if len(sys.argv) > 2 else "dev.admin"
EXPECT_HEALTH = int(sys.argv[3]) if len(sys.argv) > 3 else 200
EXPECT_DASH = int(sys.argv[4]) if len(sys.argv) > 4 else 200


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


jar = http.cookiejar.CookieJar()
ctx = ssl.create_default_context(cafile=ca)
opener = urllib.request.build_opener(
    NoRedirect, urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPSHandler(context=ctx)
)


def call(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        r = opener.open(urllib.request.Request(url, data=body), timeout=20)
    except urllib.error.HTTPError as e:
        r = e
    return r.status if hasattr(r, "status") else r.code, r.headers, r.read().decode()


def follow(url, data=None, limit=10):
    for _ in range(limit):
        status, headers, text = call(url, data)
        if status in (301, 302, 303, 307, 308):
            url = urllib.parse.urljoin(url, headers["Location"])
            data = None
            if url.startswith(APP + "/api/auth/callback"):
                print("  callback reached")
            continue
        return status, url, text
    raise SystemExit("too many redirects")


failed = False


def check(name, ok, detail=""):
    global failed
    print(f"  {'ok  ' if ok else 'FAIL'}  {name} {detail}")
    failed |= not ok


status, _, text = call(f"{APP}/api/auth/session")
check("no session before login", status == 200 and json.loads(text) == {})
status, _, text = call(f"{APP}/bff/health")
check("BFF refuses before login", status == 401, f"({status})")

status, _, text = call(f"{APP}/api/auth/csrf")
csrf = json.loads(text)["csrfToken"]
status, headers, _ = call(f"{APP}/api/auth/signin/keycloak", {"csrfToken": csrf, "callbackUrl": APP + "/"})
check("sign-in redirects to the identity provider", status == 302, f"({status})")
auth_url = headers["Location"]
check("redirect uses PKCE S256 and state", "code_challenge_method=S256" in auth_url and "state=" in auth_url)
check("redirect goes to the public issuer over https", auth_url.startswith("https://idp.localtest.me:8443/realms/aucoff/"))

status, url, page = follow(auth_url)
action = re.search(r'<form[^>]*id="kc-form-login"[^>]*action="([^"]+)"', page)
check("Keycloak login form is shown", status == 200 and action is not None)
password = subprocess.check_output(
    "kubectl -n aucoff-identity get secret aucoff-keycloak-clients -o jsonpath='{.data.DEV_USER_PASSWORD}' | base64 -d",
    shell=True,
).decode()
status, url, text = follow(html.unescape(action.group(1)), {"username": USER, "password": password, "credentialId": ""})
check("login with the synthetic user lands back in the app", url.startswith(APP) and status == 200, f"({status} {url})")

status, _, text = call(f"{APP}/api/auth/session")
session = json.loads(text)
check("session exists and carries the tenant", session.get("tenantId") == "00000000-0000-4000-8000-000000000001")
check("session never contains tokens", "accessToken" not in text and "refreshToken" not in text)
status, _, text = call(f"{APP}/bff/health")
check(f"BFF reaches the API with the user's token (health expects {EXPECT_HEALTH})", status == EXPECT_HEALTH, f"({status})")
status, _, text = call(f"{APP}/bff/dashboards/posture")
check(f"dashboard through the BFF (expects {EXPECT_DASH} for this role)", status == EXPECT_DASH, f"({status})")
if status == 200:
    check("dashboard data is labelled synthetic", json.loads(text)["data_source"] == "synthetic")
status, _, text = call(f"{APP}/")
check("app shell page renders for a signed-in user", status == 200 and "Compliance posture" in text, f"({status})")
status, _, text = call(f"{APP}/bff/openapi.json")
check("API docs need only a signed-in user (docs:read is in every role)", status == 200, f"({status})")

session_cookies = [c for c in jar if "session-token" in c.name]
check("session cookie is httpOnly and Secure", bool(session_cookies) and all(c.has_nonstandard_attr("HttpOnly") and c.secure for c in session_cookies))
sys.exit(1 if failed else 0)
