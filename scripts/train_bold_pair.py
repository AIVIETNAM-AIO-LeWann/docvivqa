"""Run the local Bold training notebook reproducibly from the repository root.

The notebook remains the source of the training algorithm. On Windows, its
DataLoader worker count defaults to zero so execution from a script is reliable.
"""

import argparse
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import time


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "train_bold_pair_local.ipynb"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--num-workers", type=int, default=0 if os.name == "nt" else 2)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    if args.num_workers < 0 or args.batch_size < 1:
        parser.error("num-workers must be nonnegative and batch-size must be positive")

    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace: dict = {"__name__": "__main__"}
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    os.chdir(ROOT / "notebooks")  # The existing notebook computes PROJECT_ROOT from cwd.

    for index in range(1, 9):
        source = "".join(notebook["cells"][index]["source"])
        if notebook["cells"][index]["cell_type"] != "code":
            raise ValueError(f"Expected code in notebook cell {index}")
        if index == 1:
            for name, value in (("NUM_WORKERS", args.num_workers), ("BATCH_SIZE", args.batch_size)):
                source, replacements = re.subn(
                    rf"(?m)^{name} = \d+$", f"{name} = {value}", source, count=1
                )
                if replacements != 1:
                    raise ValueError(f"Cannot find {name} in notebook configuration")
        print(f"Running training notebook cell {index}/8", flush=True)
        exec(compile(source, f"{NOTEBOOK.name}:cell_{index}", "exec"), namespace)
        if index == 4 and args.num_workers == 0:
            # The notebook's crop/resize pipeline is deterministic. Reuse each
            # sample after its first read to avoid decoding images every epoch.
            dataset_class = namespace["BoldPairDataset"]
            dataset_class.__getitem__ = lru_cache(maxsize=None)(dataset_class.__getitem__)
            print("Caching training tensors after their first read", flush=True)

    checkpoint: Path = namespace["CHECKPOINT_PATH"]
    torch = namespace["torch"]
    metadata = {
        "started_at_utc": started_at,
        "duration_seconds": round(time.monotonic() - started, 2),
        "notebook_sha256": sha256(NOTEBOOK),
        "checkpoint_sha256": sha256(checkpoint),
        "checkpoint_path": str(checkpoint),
        "seed": namespace["SEED"],
        "epochs": namespace["EPOCHS"],
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "tensor_cache": args.num_workers == 0,
        "train_pairs": len(namespace["train_pairs"]),
        "validation_pairs": len(namespace["validation_pairs"]),
        "device": str(namespace["DEVICE"]),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "python": platform.python_version(),
        "torch": torch.__version__,
        "torchvision": __import__("torchvision").__version__,
        "opencv": namespace["cv2"].__version__,
        "numpy": namespace["np"].__version__,
    }
    metadata_path = checkpoint.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved metadata: {metadata_path}", flush=True)


if __name__ == "__main__":
    main()
