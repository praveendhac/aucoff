"""Run the Kubernetes scanner once and write a report (T-203).

    python -m services.k8s_scanner.run --server https://... --ca ca.crt --token-file token \\
        --rule-pack ../data/checks/kubernetes.yaml --controls ../data/controls --out out/

The credential is read from a file or the AUCOFF_K8S_TOKEN environment variable, never from a
command-line argument, and is not written anywhere. Exit code 2 means the credential is too broad or
too narrow (validation failed), 1 means a collection error, 0 success.
"""

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.domain.controls import load_catalogue
from app.domain.scanning import Scope, load_rule_pack, rollup, validate_rule_pack
from services.common.evidence_store import FilesystemEvidenceStore
from services.k8s_scanner.adapter import KubernetesAdapter
from services.k8s_scanner.client import KubeApi
from services.k8s_scanner.connector import KubernetesConnector


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--server", required=True)
    ap.add_argument("--ca", required=True, help="CA certificate file for the API server")
    ap.add_argument("--token-file", help="file holding the bearer token (or set AUCOFF_K8S_TOKEN)")
    ap.add_argument("--rule-pack", required=True, type=Path)
    ap.add_argument("--controls", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--namespace", action="append", help="limit to a namespace (repeatable)")
    args = ap.parse_args(argv)

    token = (
        Path(args.token_file).read_text().strip()
        if args.token_file
        else os.environ.get("AUCOFF_K8S_TOKEN", "")
    )
    if not token:
        print("no credential: use --token-file or AUCOFF_K8S_TOKEN", file=sys.stderr)
        return 2

    pack = load_rule_pack(args.rule_pack)
    controls = load_catalogue(args.controls)
    problems = validate_rule_pack(pack, controls)
    if problems:
        print("rule pack problems: " + "; ".join(problems), file=sys.stderr)
        return 2

    connector = KubernetesConnector(KubeApi(args.server, token, args.ca))
    report = connector.validate()
    if not report.ok:
        print(
            f"credential not acceptable. missing: {report.missing}; "
            f"must not be granted: {report.excessive}",
            file=sys.stderr,
        )
        return 2

    scope = Scope(namespaces=frozenset(args.namespace) if args.namespace else None)
    now = datetime.now(UTC)
    collection = connector.collect(scope)
    store = FilesystemEvidenceStore(args.out / "evidence")
    adapter = KubernetesAdapter(pack)
    info = adapter.describe()
    documents = {}
    evidence = []
    for doc in collection.documents:
        ev = store.put(
            doc,
            source_type="k8s",
            collector=info.tool,
            collector_version=info.tool_version,
            collected_at=now,
        )
        documents[doc.name] = (doc, ev.sha256)
        evidence.append(ev)
    results = adapter.normalise(documents, now)
    proposals = rollup(results, pack)

    args.out.mkdir(parents=True, exist_ok=True)
    out = {
        "scanner": asdict(info),
        "observed_at": now,
        "collection_errors": collection.errors,
        "evidence": [asdict(e) for e in evidence],
        "check_results": [asdict(r) for r in results],
        "proposed_control_results": [asdict(p) for p in proposals],
        "note": "Proposed results are advisory; a person approves the final control result.",
    }
    (args.out / "report.json").write_text(json.dumps(out, indent=2, default=_json_default))
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r.status.value] = by_status.get(r.status.value, 0) + 1
    print(
        f"{len(results)} check results {by_status}; {len(proposals)} proposed control results; "
        f"{len(collection.errors)} collection errors; report: {args.out / 'report.json'}"
    )
    return 1 if collection.errors else 0


if __name__ == "__main__":
    sys.exit(main())
