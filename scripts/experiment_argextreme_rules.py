"""Screen simple Argmin/Argmax row rules on archived candidate tables.

This is an exploratory filter. Archived rows were built by an older solver;
promising rules still require a full pipeline run and official evaluation.
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = "861409e:artifacts/analysis/diagnostics/argextreme_oracle_ranked.csv"


def unique_rows(rows, keep_last=False):
    ordered = reversed(rows) if keep_last else rows
    seen = set()
    kept = []
    for row in ordered:
        name = row["return"]
        if name not in seen:
            kept.append(row)
            seen.add(name)
    return list(reversed(kept)) if keep_last else kept


def choose(rows, kind):
    return (max if kind == "argmax" else min)(rows, key=lambda row: row["value"])["return"]


def main():
    raw = subprocess.check_output(["git", "show", ARCHIVE], cwd=ROOT).decode("utf-8-sig")
    archived = list(csv.DictReader(io.StringIO(raw)))
    methods = ("all", "first_name", "last_name", "first_half", "first_75pct", "no_suffix")
    accuracy = Counter()
    against_all = Counter()
    examples = {method: [] for method in methods}
    for item in archived:
        rows = json.loads(item["all_values"])
        if not rows:
            continue
        baseline = choose(rows, item["reasoning_type"])
        expected = item["expected_answer"]
        for method in methods:
            eligible = rows
            if method == "first_name":
                eligible = unique_rows(rows)
            elif method == "last_name":
                eligible = unique_rows(rows, keep_last=True)
            elif method == "first_half":
                eligible = rows[:max(1, len(rows) // 2)]
            elif method == "first_75pct":
                eligible = rows[:max(1, round(len(rows) * .75))]
            elif method == "no_suffix":
                eligible = [row for row in rows if not row["return"].endswith(" Đã đối chiếu")] or rows
            answer = choose(eligible, item["reasoning_type"])
            accuracy[(method, answer == expected)] += 1
            if method != "all" and answer != baseline:
                direction = "fixed" if answer == expected else "broken" if baseline == expected else "changed_wrong"
                against_all[(method, direction)] += 1
                if len(examples[method]) < 5:
                    examples[method].append((item["question_id"], baseline, answer, expected))
    print("questions", len(archived))
    for method in methods:
        print(method, "correct", accuracy[(method, True)], "wrong", accuracy[(method, False)],
              "fixed", against_all[(method, "fixed")], "broken", against_all[(method, "broken")],
              "changed_wrong", against_all[(method, "changed_wrong")])
        if method != "all":
            print("  examples", examples[method])


if __name__ == "__main__":
    main()
