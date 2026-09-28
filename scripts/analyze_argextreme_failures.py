"""Join current Argmin/Argmax errors with source cells and archived candidate ranks."""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/training_set"
RUN = ROOT / "outputs/pipeline-rnd/baseline-new-checkpoint"
OUT = ROOT / "outputs/pipeline-rnd/argextreme-diagnostics"


def jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def archived_rows(path: str):
    raw = subprocess.check_output(
        ["git", "show", f"861409e:artifacts/analysis/diagnostics/{path}"],
        cwd=ROOT,
    ).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(raw)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    labels = {x["question_id"]: x for x in jsonl(DATA / "labels.jsonl")}
    predictions = {x["question_id"]: x for x in jsonl(RUN / "predictions_training_set.jsonl")}
    failures = list(jsonl(RUN / "official_failures.jsonl"))
    historical = {x["question_id"]: x for x in archived_rows("argextreme_oracle_ranked.csv")}
    old_rank2 = {x["question_id"]: x for x in archived_rows("argextreme_rank2_failures.csv")}

    cells_by_id = {}
    cells_by_bbox = {}
    cells_by_table = defaultdict(list)
    for cell in jsonl(DATA / "cell_annotations.jsonl"):
        doc = cell["document_id"]
        cells_by_id[(doc, cell["block_id"])] = cell
        cells_by_bbox[(doc, cell["page"], tuple(cell["bbox"]))] = cell
        cells_by_table[(doc, cell["page"], cell["table"])].append(cell)

    rows = []
    for failure in failures:
        qid = failure["question_id"]
        doc = qid.rsplit("-q", 1)[0]
        label = labels[qid]
        pred = predictions[qid]
        old = historical[qid]
        expected_ids = [x["block_id"] for x in label["evidence"]]
        expected_cells = [cells_by_id.get((doc, bid)) for bid in expected_ids]
        predicted_cells = [
            cells_by_bbox.get((doc, x["page"], tuple(x["bbox"])))
            for x in pred["evidence"]
        ]
        return_cell = cells_by_id.get((doc, old["expected_block_id"]))
        predicted_return = predicted_cells[0] if predicted_cells else None
        table_cells = cells_by_table[(doc, return_cell["page"], return_cell["table"])] if return_cell else []
        same_name_cells = [
            cell for cell in table_cells
            if cell["column"] == return_cell["column"]
            and cell["clean_text"] == return_cell["clean_text"]
        ] if return_cell else []
        rows.append({
            "question_id": qid,
            "reasoning_type": failure["type"],
            "answer_correct": failure["anls"] == 1.0,
            "expected_answer": label["answers"][0],
            "predicted_answer": pred["answer"],
            "expected_value_rank": int(old["expected_value_rank"]),
            "expected_value_text": old["expected_value_text"],
            "solver_value_text_old": old["solver_value_text"],
            "expected_return_id": old["expected_block_id"],
            "expected_return_row": return_cell["row"] if return_cell else None,
            "expected_return_bbox": return_cell["bbox"] if return_cell else None,
            "expected_return_same_text_cells": len(same_name_cells),
            "predicted_return_id": predicted_return["block_id"] if predicted_return else None,
            "predicted_return_row": predicted_return["row"] if predicted_return else None,
            "expected_evidence_ids": expected_ids,
            "expected_evidence_rows": [x["row"] if x else None for x in expected_cells],
            "predicted_evidence_ids": [x["block_id"] if x else None for x in predicted_cells],
            "predicted_evidence_rows": [x["row"] if x else None for x in predicted_cells],
            "old_expected_entity_physical_cell_count": old_rank2.get(qid, {}).get("expected_entity_physical_cell_count"),
            "old_solver_seen_before": old_rank2.get(qid, {}).get("solver_seen_before"),
        })

    with (OUT / "failures.jsonl").open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    answer_wrong = [x for x in rows if not x["answer_correct"]]
    evidence_only = [x for x in rows if x["answer_correct"]]
    summary = {
        "total_failures": len(rows),
        "answer_wrong": len(answer_wrong),
        "evidence_only": len(evidence_only),
        "answer_wrong_rank": dict(sorted(Counter(x["expected_value_rank"] for x in answer_wrong).items())),
        "answer_wrong_repeated_expected_name": sum(x["expected_return_same_text_cells"] > 1 for x in answer_wrong),
        "answer_wrong_predicted_return_differs_from_archived": sum(
            x["predicted_return_id"] != historical[x["question_id"]]["solver_block_id"] for x in answer_wrong
        ),
        "evidence_only_repeated_expected_name": sum(x["expected_return_same_text_cells"] > 1 for x in evidence_only),
        "evidence_only_return_cell_differs": sum(x["expected_return_id"] != x["predicted_return_id"] for x in evidence_only),
        "unmapped_predicted_cells": sum(
            bid is None for x in rows for bid in x["predicted_evidence_ids"]
        ),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("evidence_only:")
    for row in evidence_only:
        print(row["question_id"], row["expected_return_row"], row["predicted_return_row"], row["expected_evidence_rows"], row["predicted_evidence_rows"])


if __name__ == "__main__":
    main()
