"""Generate a no-suffix Argmin/Argmax notebook variant from the baseline."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "notebooks/submission_pipeline.ipynb"
DEFAULT_OUT = ROOT / "outputs/pipeline-rnd/variants/argextreme_no_suffix.ipynb"
NEEDLE = (
    "    if not candidates:\n"
    "        return None\n\n"
    "    # Retain the first physical row covered by each name cell, even if its number is missing.\n"
)
REPLACEMENT = (
    "    if not candidates:\n"
    "        return None\n\n"
    "    # OCR can append the verification note to an entity's name cell.\n"
    "    # Such a cell is not an eligible entity when a clean alternative exists.\n"
    "    clean_candidates = [candidate for candidate in candidates\n"
    "                        if not candidate[1]['text'].strip().endswith('Đã đối chiếu')]\n"
    "    candidates = clean_candidates or candidates\n\n"
    "    # Retain the first physical row covered by each name cell, even if its number is missing.\n"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    notebook = json.loads(BASE.read_text(encoding="utf-8"))
    source = "".join(notebook["cells"][29]["source"])
    if source.count(NEEDLE) != 1:
        raise ValueError("Argmin/Argmax source has changed; inspect before generating the variant")
    notebook["cells"][29]["source"] = source.replace(NEEDLE, REPLACEMENT).splitlines(keepends=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(args.out.resolve())


if __name__ == "__main__":
    main()
