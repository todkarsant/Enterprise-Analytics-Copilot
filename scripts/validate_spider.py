from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.spider_adapter import SpiderDataset, dataset_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a local Spider 1.0 checkout.")
    parser.add_argument("--root", default="data/spider")
    parser.add_argument("--write-manifest", default=None)
    args = parser.parse_args()

    dataset = SpiderDataset(Path(args.root))
    dataset.validate()
    schemas = dataset.schemas()
    cases = list(dataset.cases())
    manifest = dataset_manifest(args.root)

    summary = {
        "status": "validated",
        "benchmark": "Spider 1.0",
        "split": "dev",
        "cases": len(cases),
        "databases": len(schemas),
        "manifest": manifest,
    }
    if args.write_manifest:
        Path(args.write_manifest).parent.mkdir(parents=True, exist_ok=True)
        Path(args.write_manifest).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
