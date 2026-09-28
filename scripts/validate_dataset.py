"""Check the local TACVU2 split layout before running notebooks.

Uses only the Python standard library. Dataset files remain outside Git.
"""

import argparse
from collections import Counter
import json
from pathlib import Path


SPLITS = ("training_set", "public_test", "private_test")


def read_jsonl(path: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"{path}:{line_number}: {error}") from error


def referenced_file(split_dir: Path, relative_path: str) -> Path:
    path = (split_dir / relative_path).resolve()
    if not path.is_relative_to(split_dir.resolve()):
        raise ValueError(f"Path escapes split directory: {relative_path}")
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def validate_split(split_dir: Path, split: str) -> dict[str, int | str]:
    manifests = list(read_jsonl(split_dir / "manifest.jsonl"))
    questions = list(read_jsonl(split_dir / "questions.jsonl"))
    document_ids = [item["id"] for item in manifests]
    question_ids = [item["question_id"] for item in questions]
    if len(set(document_ids)) != len(document_ids):
        raise ValueError(f"{split}: duplicate document IDs")
    if len(set(question_ids)) != len(question_ids):
        raise ValueError(f"{split}: duplicate question IDs")

    document_id_set = set(document_ids)
    question_counts = Counter(item["document_id"] for item in questions)
    unknown_documents = question_counts.keys() - document_id_set
    if unknown_documents:
        raise ValueError(f"{split}: questions reference unknown documents: {sorted(unknown_documents)[:5]}")

    image_count = 0
    for manifest in manifests:
        images = manifest["image_paths"]
        if len(images) != manifest["page_count"]:
            raise ValueError(f"{split}: image/page count mismatch in {manifest['id']}")
        if question_counts[manifest["id"]] != manifest["question_count"]:
            raise ValueError(f"{split}: question count mismatch in {manifest['id']}")
        for relative_path in images:
            referenced_file(split_dir, relative_path)
        image_count += len(images)
        ocr_path = referenced_file(split_dir, manifest["ocr_path"])
        with ocr_path.open(encoding="utf-8") as stream:
            ocr = json.load(stream)
        if len(ocr["pages"]) != manifest["page_count"]:
            raise ValueError(f"{split}: OCR/page count mismatch in {manifest['id']}")

    result: dict[str, int | str] = {
        "split": split,
        "documents": len(manifests),
        "questions": len(questions),
        "images": image_count,
    }
    if split == "training_set":
        label_ids = [item["question_id"] for item in read_jsonl(split_dir / "labels.jsonl")]
        if len(label_ids) != len(set(label_ids)) or set(label_ids) != set(question_ids):
            raise ValueError("training_set: label IDs must match question IDs exactly")
        annotations = 0
        for annotation in read_jsonl(split_dir / "cell_annotations.jsonl"):
            if annotation["document_id"] not in document_id_set:
                raise ValueError(f"training_set: annotation references unknown document: {annotation['document_id']}")
            annotations += 1
        result["labels"] = len(label_ids)
        result["annotations"] = annotations
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing training_set/, public_test/, and private_test/",
    )
    parser.add_argument("--splits", nargs="+", choices=SPLITS, default=SPLITS)
    args = parser.parse_args()
    for split in args.splits:
        print(json.dumps(validate_split(args.data_root / split, split), ensure_ascii=False))


if __name__ == "__main__":
    main()
