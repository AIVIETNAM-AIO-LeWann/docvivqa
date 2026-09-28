"""Stage an offline, reproducible TACVU2 private candidate under outputs/."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from validate_submission import validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "outputs/pipeline-rnd/argextreme-no-suffix/submission_private_test.zip"
DEFAULT_TARGET = ROOT / "outputs/final-staging/TACVU2-no-suffix"
DEFAULT_NOTEBOOK = ROOT / "outputs/pipeline-rnd/variants/argextreme_no_suffix.ipynb"
MODEL = ROOT / "artifacts/models/bold_pair_resnet18.pt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deterministic_submission(path: Path, predictions: bytes) -> None:
    info = zipfile.ZipInfo("predictions.jsonl", date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(info, predictions)


def source_lines(source: str) -> list[str]:
    return source.splitlines(keepends=True)


def code_cell(source: str, cell_id: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "id": cell_id, "metadata": {}, "outputs": [], "source": source_lines(source)}


def markdown_cell(source: str, cell_id: str) -> dict:
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": source_lines(source)}


def optional_training_source(source: str) -> str:
    return "if RUN_TRAINING:\n" + "".join("    " + line if line.strip() else line for line in source.splitlines(keepends=True))


def make_notebook(inference_notebook: Path) -> dict:
    training = json.loads((ROOT / "notebooks/train_bold_pair_local.ipynb").read_text(encoding="utf-8"))
    inference = json.loads(inference_notebook.read_text(encoding="utf-8"))
    cells = [
        markdown_cell(
            "# TACVU2 — train Bold và sinh kết quả private\n\n"
            "Chạy notebook từ thư mục chứa file này. Mặc định dùng `best_model.pt` đã train "
            "trên `training_set` và suy luận trên `private_test`; không cần Internet hay nhãn private. "
            "Đặt thư mục dữ liệu tại `/home/user/TACVU2/data` trong môi trường thi. "
            "Nếu cần train lại, đặt `RUN_TRAINING = True` và bảo đảm pretrained ResNet18 "
            "được phép đã có trong `/cache_models`.\n",
            "overview",
        ),
        code_cell(
            "from pathlib import Path\n"
            "import os\n"
            "import torch\n\n"
            "PACKAGE_DIR = Path.cwd().resolve()\n"
            "RUN_TRAINING = False\n"
            "candidates = [Path('/home/user/TACVU2'), PACKAGE_DIR, *PACKAGE_DIR.parents]\n"
            "DATA_PROJECT = next((p for p in candidates if (p / 'data' / 'private_test' / 'questions.jsonl').is_file()), None)\n"
            "if DATA_PROJECT is None:\n"
            "    raise FileNotFoundError('Không tìm thấy TACVU2/data/private_test/questions.jsonl')\n"
            "def load_allowed_resnet18(backbone):\n"
            "    cache = Path('/cache_models')\n"
            "    paths = sorted(cache.rglob('*resnet18*.pth')) if cache.is_dir() else []\n"
            "    if not paths:\n"
            "        raise FileNotFoundError('Thiếu pretrained ResNet18 trong /cache_models')\n"
            "    payload = torch.load(paths[0], map_location='cpu', weights_only=True)\n"
            "    state = payload.get('state_dict', payload) if isinstance(payload, dict) else payload\n"
            "    backbone.load_state_dict(state)\n"
            "    print('Đã nạp pretrained từ', paths[0])\n"
            "    return backbone\n"
            "print('Data:', DATA_PROJECT / 'data', '| Package:', PACKAGE_DIR)\n",
            "runtime-config",
        ),
        markdown_cell(
            "## Huấn luyện tùy chọn\n\n"
            "Các cell dưới đây là toàn bộ quy trình tạo cặp, chia validation theo tài liệu, "
            "fine-tune head ResNet18 và lưu checkpoint. Mặc định bỏ qua vì `best_model.pt` "
            "đã nằm trong package. Chỉ bật train lại khi có dữ liệu huấn luyện và pretrained "
            "đúng quy định trong `/cache_models`.\n",
            "training-heading",
        ),
    ]

    for index in range(1, 9):
        source = "".join(training["cells"][index]["source"])
        if index == 1:
            source = source.replace("NUM_WORKERS = 2", "NUM_WORKERS = 0")
            source = source.replace(
                "CHECKPOINT_PATH = Path.cwd().resolve().parent / 'artifacts' / 'models' / 'bold_pair_resnet18.pt'",
                "CHECKPOINT_PATH = PACKAGE_DIR / 'best_model.pt'",
            )
            source = source.replace("PROJECT_ROOT = Path.cwd().resolve().parent", "PROJECT_ROOT = DATA_PROJECT")
        if index == 5:
            source = source.replace(
                "backbone = resnet18(weights=ResNet18_Weights.DEFAULT)",
                "backbone = load_allowed_resnet18(resnet18(weights=None))",
            )
        if index == 4:
            source += "\n# Reuse deterministic image crops across epochs when workers=0.\n"
            source += "BoldPairDataset.__getitem__ = lru_cache(maxsize=None)(BoldPairDataset.__getitem__)\n"
        cells.append(code_cell(optional_training_source(source), f"train-{index:02d}"))

    cells.append(markdown_cell("## Suy luận private và tạo ZIP\n\nĐọc OCR/ảnh, suy luận toàn bộ câu hỏi và ghi `private_submission.zip`.\n", "inference-heading"))
    for index, cell in enumerate(inference["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if index == 5:
            source = (
                "torch.backends.cudnn.deterministic = True\n"
                "torch.backends.cudnn.benchmark = False\n"
                "torch.use_deterministic_algorithms(True, warn_only=True)\n"
                "ROOT = DATA_PROJECT\n"
                "DATA = ROOT / 'data'\n"
                "TRAIN_DIR = DATA / 'training_set'\n"
                "SPLIT = 'private_test'\n"
                "checkpoint_path = PACKAGE_DIR / 'best_model.pt'\n"
                "if not checkpoint_path.is_file():\n"
                "    raise FileNotFoundError(checkpoint_path)\n"
                "RUNS = PACKAGE_DIR\n"
                "DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n"
                "if DEVICE.type == 'cpu':\n"
                "    torch.set_num_threads(2)\n"
                "print(f'Data={DATA} | SPLIT={SPLIT} | DEVICE={DEVICE}')\n"
            )
        elif index == 36:
            source = source.replace(
                'BOLD_PAIR_CHECKPOINT = ROOT / "artifacts" / "models" / "bold_pair_resnet18.pt"',
                "BOLD_PAIR_CHECKPOINT = checkpoint_path",
            )
        elif index == 47:
            source = (
                "SUBMISSION_PATH = PACKAGE_DIR / 'private_submission.zip'\n"
                "info = zipfile.ZipInfo('predictions.jsonl', date_time=(1980, 1, 1, 0, 0, 0))\n"
                "info.compress_type = zipfile.ZIP_DEFLATED\n"
                "with zipfile.ZipFile(SUBMISSION_PATH, 'w', zipfile.ZIP_DEFLATED) as archive:\n"
                "    archive.writestr(info, PREDICTIONS_PATH.read_bytes())\n"
                "print(f'Đã tạo {SUBMISSION_PATH}')\n"
            )
        cells.append(code_cell(source, f"infer-{index:02d}"))

    return {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--inference-notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--candidate", default="argextreme-no-suffix")
    args = parser.parse_args()
    questions = ROOT / "data/private_test/questions.jsonl"
    validate(args.source_zip, questions)
    if not MODEL.is_file():
        raise FileNotFoundError(MODEL)
    args.out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.source_zip) as archive:
        predictions = archive.read("predictions.jsonl")
    deterministic_submission(args.out / "private_submission.zip", predictions)
    shutil.copyfile(MODEL, args.out / "best_model.pt")
    notebook_path = args.out / "generate_result.ipynb"
    notebook_path.write_text(json.dumps(make_notebook(args.inference_notebook), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    manifest = {
        "candidate": args.candidate,
        "private_score": None,
        "submission_sha256": sha256(args.out / "private_submission.zip"),
        "predictions_sha256": hashlib.sha256(predictions).hexdigest(),
        "model_sha256": sha256(args.out / "best_model.pt"),
        "notebook_sha256": sha256(notebook_path),
        "source_zip": str(args.source_zip),
        "inference_notebook": str(args.inference_notebook),
    }
    manifest_path = args.out / "candidate_manifest.json"
    if manifest_path.is_file():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous.get("submission_sha256") == manifest["submission_sha256"]:
            manifest["private_score"] = previous.get("private_score")
            if "private_result" in previous:
                manifest["private_result"] = previous["private_result"]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"target": str(args.out), **manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
