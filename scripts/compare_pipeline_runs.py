"""Compare two scored prediction runs by question ID and official question score."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def keyed_jsonl(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    result = {row["question_id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate question IDs in {path}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_predictions", type=Path)
    parser.add_argument("candidate_predictions", type=Path)
    parser.add_argument("baseline_failures", type=Path)
    parser.add_argument("candidate_failures", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    baseline = keyed_jsonl(args.baseline_predictions)
    candidate = keyed_jsonl(args.candidate_predictions)
    if set(baseline) != set(candidate):
        raise ValueError("Prediction ID sets differ")
    old_fail = keyed_jsonl(args.baseline_failures)
    new_fail = keyed_jsonl(args.candidate_failures)
    changes = []
    for qid in sorted(baseline):
        old = baseline[qid]
        new = candidate[qid]
        old_score = old_fail.get(qid, {}).get("question_score", 1.0)
        new_score = new_fail.get(qid, {}).get("question_score", 1.0)
        if old != new or old_score != new_score:
            changes.append({
                "question_id": qid,
                "old_answer": old["answer"],
                "new_answer": new["answer"],
                "answer_changed": old["answer"] != new["answer"],
                "evidence_changed": old["evidence"] != new["evidence"],
                "old_score": old_score,
                "new_score": new_score,
                "delta_score": new_score - old_score,
            })
    summary = {
        "questions": len(baseline),
        "predictions_changed": len(changes),
        "answers_changed": sum(row["answer_changed"] for row in changes),
        "evidence_only_changed": sum(not row["answer_changed"] and row["evidence_changed"] for row in changes),
        "improved": sum(row["delta_score"] > 0 for row in changes),
        "regressed": sum(row["delta_score"] < 0 for row in changes),
        "same_score": sum(row["delta_score"] == 0 for row in changes),
        "baseline_failures": len(old_fail),
        "candidate_failures": len(new_fail),
        "delta_points_per_100": 100 * sum(row["delta_score"] for row in changes) / len(baseline),
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as stream:
            for row in changes:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("first_changes", json.dumps(changes[:8], ensure_ascii=False))


if __name__ == "__main__":
    main()
