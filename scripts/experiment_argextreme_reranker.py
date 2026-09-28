"""Test an OCR-only Argmin/Argmax reranker with document-grouped CV.

Archived candidate rows are an approximation of current inference; this script
screens the idea and never writes a private prediction or a submission ZIP.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import statistics
import subprocess
from pathlib import Path

import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = "861409e:artifacts/analysis/diagnostics/argextreme_oracle_ranked.csv"
BASELINE = ROOT / "outputs/pipeline-rnd/argextreme-no-suffix/predictions_training_set.jsonl"


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def fold_for(document_id: str) -> int:
    return int.from_bytes(hashlib.sha256(document_id.encode()).digest()[:4], "big") % 5


def features_for(rows: list[dict], question: dict) -> list[list[float]]:
    kind = question["reasoning_type"]
    sign = 1 if kind == "argmax" else -1
    values = [sign * float(row["value"]) for row in rows]
    low, high = min(values), max(values)
    spread = max(high - low, 1e-6)
    median = statistics.median(values)
    ranks = {index: rank for rank, index in enumerate(sorted(range(len(rows)), key=lambda i: values[i], reverse=True))}
    names = [row["return"] for row in rows]
    count = len(rows)
    total_rows = max(int(question["num_logical_rows"]), count, 2)
    result = []
    for index, row in enumerate(rows):
        name = row["return"]
        occurrences = [i for i, text in enumerate(names) if text == name]
        position = int(row["logical_row"]) / (total_rows - 1)
        result.append([
            (values[index] - low) / spread,
            (high - values[index]) / spread,
            ranks[index] / max(count - 1, 1),
            max(-5.0, min(5.0, (values[index] - median) / max(abs(median), 1.0))),
            position,
            1.0 - position,
            len(occurrences) / count,
            float(index == occurrences[0]),
            float(index == occurrences[-1]),
            min(len(name), 40) / 40,
            float(any(char.isdigit() for char in name)),
            min(count, 25) / 25,
            float(kind == "argmax"),
        ])
    return result


def load_examples() -> list[dict]:
    raw = subprocess.check_output(["git", "show", ARCHIVE], cwd=ROOT).decode("utf-8-sig")
    examples = []
    for question in csv.DictReader(io.StringIO(raw)):
        candidates = json.loads(question["all_values"])
        clean = [row for row in candidates if not row["return"].endswith(" Đã đối chiếu")]
        rows = clean or candidates
        positives = [row["return"] == question["expected_answer"] for row in rows]
        if not rows or not any(positives):
            continue
        examples.append({
            "question_id": question["question_id"],
            "document_id": question["document_id"],
            "expected": question["expected_answer"],
            "names": [row["return"] for row in rows],
            "features": features_for(rows, question),
            "positives": positives,
            "fold": fold_for(question["document_id"]),
        })
    return examples


def pack(examples: list[dict]):
    rows = len(examples)
    max_candidates = max(len(item["names"]) for item in examples)
    feature_count = len(examples[0]["features"][0])
    values = torch.zeros((rows, max_candidates, feature_count), dtype=torch.float32)
    valid = torch.zeros((rows, max_candidates), dtype=torch.bool)
    positive = torch.zeros_like(valid)
    for index, item in enumerate(examples):
        count = len(item["names"])
        values[index, :count] = torch.tensor(item["features"], dtype=torch.float32)
        valid[index, :count] = True
        positive[index, :count] = torch.tensor(item["positives"], dtype=torch.bool)
    return values, valid, positive


def build_model(feature_count: int, kind: str) -> nn.Module:
    if kind == "linear":
        return nn.Linear(feature_count, 1)
    return nn.Sequential(nn.Linear(feature_count, 16), nn.ReLU(), nn.Linear(16, 1))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("linear", "mlp"), default="linear")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    torch.manual_seed(20260928)
    torch.set_num_threads(4)
    examples = load_examples()
    values, valid, positive = pack(examples)
    baseline = {item["question_id"]: item["answer"] for item in read_jsonl(BASELINE)}
    records = []
    fold_results = []
    for fold in range(5):
        train_indices = [i for i, item in enumerate(examples) if item["fold"] != fold]
        test_indices = [i for i, item in enumerate(examples) if item["fold"] == fold]
        model = build_model(values.shape[-1], args.model)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=0.05)
        for _ in range(args.epochs):
            model.train()
            scores = model(values[train_indices]).squeeze(-1)
            all_lse = torch.logsumexp(scores.masked_fill(~valid[train_indices], -1e6), dim=1)
            pos_lse = torch.logsumexp(scores.masked_fill(~positive[train_indices], -1e6), dim=1)
            loss = (all_lse - pos_lse).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            scores = model(values[test_indices]).squeeze(-1)
            probabilities = scores.masked_fill(~valid[test_indices], -1e6).softmax(dim=1)
            winners = probabilities.argmax(dim=1).tolist()
        correct_model = correct_baseline = 0
        for position, (index, winner) in enumerate(zip(test_indices, winners)):
            item = examples[index]
            answer = item["names"][winner]
            records.append({"question_id": item["question_id"], "expected": item["expected"],
                            "baseline": baseline[item["question_id"]], "model": answer,
                            "confidence": float(probabilities[position, winner])})
            correct_model += answer == item["expected"]
            correct_baseline += baseline[item["question_id"]] == item["expected"]
        fold_results.append({"fold": fold, "questions": len(test_indices), "model_correct": correct_model,
                             "baseline_correct": correct_baseline})
    total_model = sum(item["model_correct"] for item in fold_results)
    total_baseline = sum(item["baseline_correct"] for item in fold_results)
    result = {"model": args.model, "epochs": args.epochs, "questions": len(examples),
              "model_correct": total_model, "baseline_correct": total_baseline,
              "delta_correct": total_model - total_baseline, "folds": fold_results}
    result["hybrid"] = []
    for threshold in (0.7, 0.8, 0.9, 0.95):
        switched = [row for row in records if row["model"] != row["baseline"] and row["confidence"] >= threshold]
        fixed = sum(row["model"] == row["expected"] for row in switched)
        broken = sum(row["baseline"] == row["expected"] for row in switched)
        result["hybrid"].append({"threshold": threshold, "switched": len(switched),
                                 "fixed": fixed, "broken": broken, "net": fixed - broken})
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
