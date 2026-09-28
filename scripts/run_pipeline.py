"""Run the current submission notebook with an explicit split and output folder."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "submission_pipeline_no_suffix.ipynb"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("training_set", "public_test", "private_test"), default="training_set")
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "pipeline-rnd" / "current-no-suffix")
    parser.add_argument("--notebook", type=Path, default=NOTEBOOK)
    args = parser.parse_args()
    notebook_path = args.notebook.resolve()
    output_dir = args.out.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not (ROOT / "data" / args.split / "questions.jsonl").is_file():
        parser.error(f"Missing data split: {args.split}")

    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    namespace: dict = {"__name__": "__main__"}
    os.chdir(ROOT)
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    fallback_calls = 0

    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        print(f"Running pipeline cell {index}/{len(notebook['cells']) - 1}", flush=True)
        exec(compile("".join(cell["source"]), f"{notebook_path.name}:cell_{index}", "exec"), namespace)
        if index == 5:
            namespace["SPLIT"] = args.split
            namespace["RUNS"] = output_dir
            print(f"Runner configuration: SPLIT={args.split} | RUNS={output_dir}", flush=True)
        if index == 36:
            original = namespace["pairwise_bold_winner"]

            def tracked_fallback(*call_args, **call_kwargs):
                nonlocal fallback_calls
                fallback_calls += 1
                return original(*call_args, **call_kwargs)

            namespace["pairwise_bold_winner"] = tracked_fallback

    predictions_path: Path = namespace["PREDICTIONS_PATH"]
    predictions = read_jsonl(predictions_path)
    questions = namespace["questions"]
    expected_ids = {item["question_id"] for item in questions}
    actual_ids = [item["question_id"] for item in predictions]
    if len(predictions) != len(questions) or len(set(actual_ids)) != len(actual_ids) or set(actual_ids) != expected_ids:
        raise ValueError("Prediction IDs do not match the input questions")

    checkpoint = ROOT / "artifacts" / "models" / "bold_pair_resnet18.pt"
    torch = namespace["torch"]
    metadata = {
        "started_at_utc": started_at,
        "duration_seconds": round(time.monotonic() - started, 2),
        "split": args.split,
        "questions": len(questions),
        "answered": sum(row["answer"] != "không xác định" for row in predictions),
        "fallback_calls": fallback_calls,
        "notebook_sha256": sha256(notebook_path),
        "checkpoint_sha256": sha256(checkpoint),
        "predictions_sha256": sha256(predictions_path),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "torchvision": __import__("torchvision").__version__,
        "opencv": namespace["cv2"].__version__,
        "numpy": namespace["np"].__version__,
        "device": str(namespace["DEVICE"]),
    }
    metadata_path = output_dir / f"run_{args.split}.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved metadata: {metadata_path}", flush=True)


if __name__ == "__main__":
    main()
