# DocViVQA

Nghiên cứu cải thiện hỏi đáp trên ảnh tài liệu tiếng Việt và định vị vùng bằng chứng, tập trung vào **Visual Bold Lookup, Argmax, Argmin**, đồng thời khảo sát LLM/VLM.

Branch `main` có pipeline đạt private **raw 100,00**, chuẩn hóa **100,00**, bài nộp **28721** ngày **05/10/2026**, theo kết quả người dùng cung cấp. Phiên bản trước đạt raw 98,35. Xem [báo cáo cải tiến ngữ cảnh hàng](docs/experiments/2026-10-05-argextreme-context-structure.md).

## Chạy pipeline hiện tại

Mở **[notebooks/submission_pipeline_context_structure.ipynb](notebooks/submission_pipeline_context_structure.ipynb)**:

1. Chuẩn bị dữ liệu tại `data/<split>/`, gồm manifest, questions, OCR và images theo cấu trúc gốc.
2. Đặt checkpoint đã train tại `artifacts/models/bold_pair_resnet18.pt`. Dữ liệu và checkpoint được giữ ngoài Git; repository có notebook huấn luyện Bold.
3. Cài PyTorch, torchvision, OpenCV, NumPy và Pillow; chạy notebook từ thư mục dự án hoặc `notebooks/`.
4. Chọn `SPLIT = 'private_test'` để nộp vòng private; mặc định `training_set` dùng kiểm tra local.
5. Chạy từ đầu đến cuối. ZIP ở `outputs/argextreme-context-structure/inference/submission_<split>.zip`, chứa `predictions.jsonl`.

Notebook chứa đầy đủ hàm xử lý và self-test, không cần script thực nghiệm phụ. Các notebook phiên bản trước được giữ để đối chiếu.

## Những cải tiến đã tích hợp

- **Bold:** loại đường kẻ dài khỏi mask Otsu trước khi đo độ dày nét; giữ ResNet18 dự phòng.
- **Evidence:** xét cả hàng thiếu số khi tìm các ô cần để phân biệt hàng.
- **Argmin/Argmax:** xử lý hàng đầu của ô tên gộp; lọc ghi chú trong phần nhận diện; kiểm tra ngữ cảnh duy nhất, không thiếu ô cần thiết và không trùng phần đầu của hàng khác.
- Nếu một bộ lọc loại hết ứng viên, giữ danh sách trước bộ lọc đó. Suy luận chỉ dùng câu hỏi, ảnh và OCR, không dùng nhãn/chú giải.

| Mốc private | Raw |
|---|---:|
| Baseline tác giả, kết quả được cung cấp | 94,99 |
| Bài thử ô tham chiếu của nhóm | 95,71 |
| Làm sạch đường kẻ cho Bold | 95,82 |
| Sửa evidence | 95,84 |
| Hàng đầu ô gộp, giai đoạn có checkpoint train lại | 97,6833 |
| Lọc hậu tố ghi chú ô tên | 98,2605 |
| Lọc ghi chú trong ngữ cảnh cần dùng | 98,35 |
| Kiểm tra tính duy nhất và đầy đủ của ngữ cảnh | **100,00** |

Đây là lịch sử phiên bản; không phải mọi mốc chỉ thay một yếu tố. So với bản raw 98,35, bản cuối sửa 142 đáp án và 7 ca chỉ sai evidence trên 11.000 câu training, không câu giảm điểm. ANLS và Evidence-F1 training đều đạt 100%; private có 33 đáp án thay đổi.

**Giới hạn:** training đã được dùng nhiều vòng để chẩn đoán và chọn quy tắc, nên kết quả training là hồi cứu. Raw 100 là kết quả trên tập private của cuộc thi; chưa đánh giá khả năng tổng quát trên dữ liệu khác. Không bổ sung LLM/VLM trong phiên bản này.

## Điều hướng

- [Outline và kế hoạch](docs/weekly/WEEK01-outline.md)
- [Paper Tracker](docs/papers/paper-tracker.csv)
- [Baseline và hướng dẫn chạy](docs/baseline.md)
- [Chuẩn bị dữ liệu](docs/data.md)
- [Metric đánh giá](docs/metrics.md)
- [Mẫu nhật ký thực nghiệm](docs/experiments/experiment-template.md)
- [Kiểm tra điều kiện vòng private và candidate offline](docs/experiments/2026-09-28-private-round-readiness.md)
- [Thử nghiệm loại ghi chú OCR trong Argmin/Argmax](docs/experiments/2026-09-28-argextreme-no-suffix.md)
- [Sàng lọc reranker Argmin/Argmax theo tài liệu](docs/experiments/2026-09-28-reranker-screen.md)

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
| [main](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/main) | Phiên bản đạt private raw 100,00: Bold + evidence + kiểm tra ngữ cảnh Argmin/Argmax |
| [baseline](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/baseline) | Code baseline upstream và tài liệu tái hiện |
| [improve/baseline-branches](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/improve/baseline-branches) | Nhánh phát triển Bold + evidence đã được merge vào main |

Nhánh [improve/argmin-argmax-first-row](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/improve/argmin-argmax-first-row) lưu phần thay đổi Argmin/Argmax.

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

Chia tập theo document và so sánh các phiên bản trên cùng tập đánh giá. Báo cáo ANLS, Evidence-F1 và điểm tổng hợp theo đề. Kết quả sửa Bold đã được đối chiếu bằng evaluator upstream ở commit `2bc3653`. Script `scripts/evaluate_predictions.py` cũ trong repo chỉ tính coverage và accuracy.

[Nguồn baseline](https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round) · Pipeline cải thiện dựa trên commit `2bc3653`; các notebook baseline khác giữ nguồn `2aa3ac7`.
