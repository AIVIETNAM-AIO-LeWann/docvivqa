# DocViVQA — Baseline

**Pipeline gốc cho hỏi đáp trên ảnh tài liệu tiếng Việt và định vị vùng bằng chứng.**

Branch này giữ mã baseline để tái hiện và đối chiếu. Phiên bản cải tiến nằm trên [main](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/main).

## Nguồn

Kế thừa thư mục DocViVQA của [T-Sunm/olp-ai-ptit-2026-preliminary-round](https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round), snapshot `2aa3ac75343abe87a4a487e964c7cae47e568e6a`. Việc dọn repository không thay đổi code trong các notebook được giữ lại.

## Chạy baseline

1. Cài Python cùng PyTorch, torchvision, OpenCV, NumPy, Pillow và Jupyter.
2. Đặt dataset tại `data/<split>/`, giữ nguyên cấu trúc manifest, questions, images và OCR.
3. Train Bold bằng notebook local/Colab, hoặc chuẩn bị checkpoint đã train tại `artifacts/models/bold_pair_resnet18.pt`.
4. Mở `notebooks/submission_pipeline.ipynb` với working directory là `notebooks/`; kiểm tra đường dẫn ROOT, checkpoint và SPLIT trong cell cấu hình rồi chạy từ đầu đến cuối.
5. Chọn đúng tập kiểm tra khi tạo bài nộp. ZIP phải chứa `predictions.jsonl`.

Dataset: [TACVU2 trên Hugging Face](https://huggingface.co/datasets/lequangaio070206/tacvu2-docvivqa). Dữ liệu và checkpoint không nằm trong Git.

## Các file chính

| File | Vai trò |
|---|---|
| `notebooks/submission_pipeline.ipynb` | Pipeline suy luận baseline |
| `notebooks/train_bold_pair_local.ipynb` | Train ResNet18 Bold tại máy |
| `notebooks/train_bold_pair_colab.ipynb` | Train Bold trên Colab |
| `scripts/evaluate_predictions.py` | Coverage và accuracy đáp án; không tính ANLS/Evidence-F1 |

## Tài liệu

- [Baseline](docs/baseline.md)
- [Dữ liệu](docs/data.md)
- [Metric](docs/metrics.md)

Chỉ giữ hai branch: `baseline` để đối chiếu mã gốc và `main` để sử dụng, phát triển bản cải tiến. Các notebook tham khảo đã dọn vẫn có trong lịch sử Git.
