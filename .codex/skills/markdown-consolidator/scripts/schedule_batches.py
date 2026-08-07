#!/usr/bin/env python3
"""Build bounded task waves from a JSON item list."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from common import SCHEMA_VERSION, dump_json, load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Partition JSON items into bounded batches and waves.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--items-path", required=True, help="Dot path to a JSON array, e.g. sources or topics.")
    parser.add_argument("--id-field", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--logical-prefix", required=True)
    parser.add_argument("--max-concurrency", type=int, default=3)
    parser.add_argument("--max-items-per-batch", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def get_path(data: Any, path: str) -> Any:
    current = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Missing JSON path {path!r}")
        current = current[part]
    return current


def main() -> int:
    args = parse_args()
    if args.max_concurrency < 1 or args.max_items_per_batch < 1:
        raise SystemExit("max-concurrency and max-items-per-batch must be positive")
    data = load_json(args.input)
    items = get_path(data, args.items_path)
    if not isinstance(items, list):
        raise SystemExit(f"{args.items_path!r} is not an array")

    ids: list[str] = []
    for item in items:
        if not isinstance(item, dict) or not item.get(args.id_field):
            raise SystemExit(f"Every item must contain {args.id_field!r}")
        ids.append(str(item[args.id_field]))
    if len(ids) != len(set(ids)):
        raise SystemExit("Item identifiers are not unique")

    batches: list[dict[str, Any]] = []
    for index in range(0, len(ids), args.max_items_per_batch):
        batch_ids = ids[index : index + args.max_items_per_batch]
        batch_number = len(batches) + 1
        batches.append(
            {
                "logical_task_id": f"{args.logical_prefix}-{batch_number:03d}",
                "phase": args.phase,
                "role": args.role,
                "item_ids": batch_ids,
            }
        )

    waves: list[dict[str, Any]] = []
    for index in range(0, len(batches), args.max_concurrency):
        wave_batches = batches[index : index + args.max_concurrency]
        waves.append(
            {
                "wave": len(waves) + 1,
                "logical_task_ids": [batch["logical_task_id"] for batch in wave_batches],
            }
        )

    output = {
        "schema_version": SCHEMA_VERSION,
        "phase": args.phase,
        "role": args.role,
        "item_count": len(ids),
        "batch_count": len(batches),
        "wave_count": len(waves),
        "max_concurrency": args.max_concurrency,
        "max_items_per_batch": args.max_items_per_batch,
        "minimum_wave_count": math.ceil(len(batches) / args.max_concurrency) if batches else 0,
        "batches": batches,
        "waves": waves,
    }
    dump_json(args.output, output)
    print(f"Created {len(batches)} batch(es) in {len(waves)} wave(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
