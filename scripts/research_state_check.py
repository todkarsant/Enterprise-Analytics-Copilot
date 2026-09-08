from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    "DESIGNED": ["docs/PROJECT1_P6_IP_DESIGN.md"],
    "IMPLEMENTED": ["research/p6_ip_runner.py", "tests/test_p6_ip.py"],
    "CI_VALIDATED": [".github/workflows/research-ci.yml"],
    "EXECUTED": [], "ARTIFACT_VALIDATED": [], "ANALYZED": [],
    "SCIENTIFIC_DECISION": [], "PAPER_LOCKED": [],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True, choices=REQUIRED)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--manifest", type=Path)
    args = ap.parse_args()
    missing = [p for p in REQUIRED[args.state] if not (args.root / p).exists()]
    if missing:
        raise SystemExit(f"STATE_CHECK_FAILED state={args.state} missing={missing}")
    if args.manifest:
        if not args.manifest.exists():
            raise SystemExit(f"STATE_CHECK_FAILED missing manifest: {args.manifest}")
        obj = json.loads(args.manifest.read_text(encoding="utf-8"))
        if obj.get("state") != args.state:
            raise SystemExit(f"STATE_CHECK_FAILED manifest state={obj.get('state')!r} expected={args.state!r}")
    print(f"STATE_CHECK_OK state={args.state}")


if __name__ == "__main__":
    main()
