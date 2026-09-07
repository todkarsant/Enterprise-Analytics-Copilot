from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research.spider_adapter import SpiderDataset, dataset_manifest


def holdout_db(db_id: str, fraction: float, seed: str) -> bool:
    digest = hashlib.sha256(f"{seed}:{db_id}".encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    return bucket < fraction


def write_unseen_schema_split(dataset: SpiderDataset, output: Path, fraction: float, seed: str) -> dict:
    if not 0.0 < fraction < 1.0:
        raise ValueError("unseen fraction must be between 0 and 1")
    dataset.validate()
    selected = [case for case in dataset.cases() if holdout_db(case.db_id, fraction, seed)]
    if not selected:
        raise ValueError("Unseen-schema split selected zero databases")
    rows = [
        {"question": case.question, "db_id": case.db_id, "query": case.gold_sql}
        for case in selected
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return {
        "fraction": fraction,
        "seed": seed,
        "database_count": len({case.db_id for case in selected}),
        "question_count": len(selected),
        "database_ids": sorted({case.db_id for case in selected}),
        "policy_boundary": "This file is evaluator input only; policy code receives question/schema, never gold SQL.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a local Spider 1.0 checkout.")
    parser.add_argument("--root", default="data/spider")
    parser.add_argument("--write-manifest", default=None)
    parser.add_argument("--write-unseen", default=None)
    parser.add_argument("--unseen-fraction", type=float, default=0.20)
    parser.add_argument("--unseen-seed", default="1729")
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
    if args.write_unseen:
        summary["unseen_schema_holdout"] = write_unseen_schema_split(
            dataset,
            Path(args.write_unseen),
            args.unseen_fraction,
            args.unseen_seed,
        )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
