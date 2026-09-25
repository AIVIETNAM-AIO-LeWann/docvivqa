# DocViVQA

Nghiên cứu cải thiện hỏi đáp trên ảnh tài liệu tiếng Việt và định vị vùng bằng chứng, tập trung vào **Visual Bold Lookup, Argmax, Argmin**, đồng thời khảo sát LLM/VLM.

Branch cải thiện các nhánh của baseline. Bản sửa hiện tại loại đường kẻ bảng trước khi đo độ đậm ở Visual Bold Lookup. Code nằm trong `notebooks/` và `scripts/`.

## Bản sửa Bold đang sử dụng

Mở **[submission_pipeline_bold_grid_clean.ipynb](notebooks/submission_pipeline_bold_grid_clean.ipynb)** để chạy pipeline đầy đủ. Đặt dữ liệu ở `data/<split>/` và checkpoint đã train tại `artifacts/models/bold_pair_resnet18.pt`, rồi chạy notebook từ đầu. Checkpoint và dữ liệu không được lưu trong Git.

| Đánh giá | Trước sửa | Sau sửa |
|---|---:|---:|
| Bold trên toàn training_set | 515/535 | **535/535** |
| Bold trên validation của checkpoint | 102/107 | **107/107** |
| Private test — raw score so với bài nộp trước của dự án | 95,71 | **95,82** |

Sửa 20 lỗi Bold, không làm sai thêm trên 535 câu đã khảo sát. Validation đã được dùng trong quá trình train/phân tích lỗi. Bài nộp private trước dùng phương pháp kết hợp ô tham chiếu, nên hàng private không phải phép so sánh riêng với baseline gốc.

Xem **[báo cáo và hướng dẫn chạy](docs/experiments/2026-09-25-bold-grid-cleanup.md)**. Script [generate_bold_grid_submission.py](scripts/generate_bold_grid_submission.py) sinh ZIP và kiểm tra ID/cấu trúc:

```bash
python scripts/generate_bold_grid_submission.py \
  --data data/private_test \
  --out outputs/private-submission-bold-grid-cleanup \
  --expected-questions 2000
```

Cần môi trường Python có PyTorch, torchvision, OpenCV, NumPy và Pillow.

## Điều hướng

- [Outline và kế hoạch](docs/weekly/WEEK01-outline.md)
- [Paper Tracker](docs/papers/paper-tracker.csv)
- [Baseline và hướng dẫn chạy](docs/baseline.md)
- [Chuẩn bị dữ liệu](docs/data.md)
- [Metric đánh giá](docs/metrics.md)
- [Mẫu nhật ký thực nghiệm](docs/experiments/experiment-template.md)

Outline và Paper Tracker trong repo vẫn là bản khởi tạo; bản hoàn thiện trên Working Files/Google Sheets chưa được đồng bộ hoặc gắn link tại đây.

## Dataset

Dữ liệu TACVU2: [lequangaio070206/tacvu2-docvivqa trên Hugging Face](https://huggingface.co/datasets/lequangaio070206/tacvu2-docvivqa/tree/main).

- `training_set/`: ảnh, OCR, câu hỏi, đáp án và chú giải ô bảng.
- `public_test/`: ảnh, OCR và câu hỏi; không có nhãn đáp án đi kèm.
- Nếu dataset đang để **Private**, cần đăng nhập bằng tài khoản có quyền truy cập để xem hoặc tải dữ liệu.

Xem [hướng dẫn chuẩn bị dữ liệu](docs/data.md) để đặt dữ liệu đúng cấu trúc chạy baseline. Dữ liệu không được commit vào GitHub.

## Branch

| Branch | Nội dung |
|---|---|
| [main](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/main) | Tài liệu và kế hoạch nghiên cứu |
| [baseline](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/baseline) | Code baseline upstream và tài liệu tái hiện |
| [improve/baseline-branches](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/improve/baseline-branches) | Cải thiện Bold và kết quả thực nghiệm |

## Cấu trúc

```text
docvivqa/
├── docs/
│   ├── baseline.md          # Nguồn baseline và hướng dẫn chạy
│   ├── data.md              # Chuẩn bị dữ liệu
│   ├── metrics.md           # Metric và quy ước cần xác minh
│   ├── papers/              # Paper Tracker và mẫu ghi chú
│   ├── weekly/              # Outline và kế hoạch
│   └── experiments/         # Nhật ký thực nghiệm
├── notebooks/              # Pipeline, khám phá dữ liệu, train bold
├── scripts/                # Script đánh giá upstream
└── README.md
```

Dataset, PDF paper, checkpoint và kết quả thô được giữ tại máy và bỏ qua bởi Git. Các thư mục phục vụ chạy chương trình được tạo khi cần; xem [hướng dẫn dữ liệu](docs/data.md).

## Thực nghiệm

Chia tập theo document và so sánh các phiên bản trên cùng tập đánh giá. Báo cáo ANLS, Evidence-F1 và điểm tổng hợp theo đề. Báo cáo sửa Bold dùng evaluator gốc ở commit `2bc3653` để đối chiếu ANLS/Evidence-F1. Script `scripts/evaluate_predictions.py` cũ trong repository chỉ tính coverage/accuracy.

[Nguồn baseline](https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round) · Bản cải thiện Bold dựa trên commit `2bc3653`; các notebook baseline cũ giữ nguồn `2aa3ac7`.
