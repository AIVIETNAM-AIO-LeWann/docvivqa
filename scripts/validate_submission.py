"""Validate a TACVU2 submission ZIP against a split without reading labels."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import zipfile


def read_jsonl(lines):
    for number, raw in enumerate(lines, 1):
        if raw.strip():
            try:
                yield json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {number}: {error}") from error


def validate(zip_path: Path, questions_path: Path) -> dict:
    with questions_path.open(encoding="utf-8") as stream:
        expected = {item["question_id"] for item in read_jsonl(stream)}
    if not expected:
        raise ValueError("Questions file is empty")

    with zipfile.ZipFile(zip_path) as archive:
        members = [name for name in archive.namelist() if not name.endswith("/")]
        prediction_members = [name for name in members if Path(name).name == "predictions.jsonl"]
        if len(prediction_members) != 1:
            raise ValueError("ZIP must contain exactly one predictions.jsonl")
        with archive.open(prediction_members[0]) as stream:
            predictions = list(read_jsonl(line.decode("utf-8") for line in stream))

    seen = set()
    for number, item in enumerate(predictions, 1):
        if not isinstance(item, dict) or set(item) != {"question_id", "answer", "evidence"}:
            raise ValueError(f"Prediction {number} must have exactly question_id, answer, evidence")
        qid = item["question_id"]
        if not isinstance(qid, str) or qid in seen:
            raise ValueError(f"Invalid or duplicate question_id at prediction {number}: {qid!r}")
        seen.add(qid)
        if not isinstance(item["answer"], str) or not item["answer"].strip():
            raise ValueError(f"Invalid answer for {qid}")
        if not isinstance(item["evidence"], list):
            raise ValueError(f"Evidence must be a list for {qid}")
        for evidence in item["evidence"]:
            if not isinstance(evidence, dict) or set(evidence) != {"page", "bbox"}:
                raise ValueError(f"Invalid evidence fields for {qid}")
            page, box = evidence["page"], evidence["bbox"]
            if isinstance(page, bool) or not isinstance(page, int) or page < 1:
                raise ValueError(f"Invalid page for {qid}")
            if not isinstance(box, list) or len(box) != 4 or any(
                isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
                for value in box
            ):
                raise ValueError(f"Invalid bbox for {qid}")
            x1, y1, x2, y2 = box
            if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
                raise ValueError(f"Out-of-range bbox for {qid}")

    missing = expected - seen
    extra = seen - expected
    if missing or extra:
        raise ValueError(f"Question IDs differ: {len(missing)} missing, {len(extra)} extra")
    return {"zip": str(zip_path), "questions": len(expected), "predictions": len(predictions), "valid": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission", type=Path)
    parser.add_argument("--questions", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.submission, args.questions), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
