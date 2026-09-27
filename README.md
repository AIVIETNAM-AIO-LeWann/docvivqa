# DocViVQA

Nghiên cứu cải thiện hỏi đáp trên ảnh tài liệu tiếng Việt và định vị vùng bằng chứng, tập trung vào **Visual Bold Lookup, Argmax, Argmin**, đồng thời khảo sát LLM/VLM.

Branch `main` là phiên bản làm việc chung mới nhất, đã tích hợp sửa Bold và evidence vào `notebooks/submission_pipeline.ipynb`, đạt private raw **95,84**. Các cải tiến tiếp theo nên tạo nhánh từ `main`.

## Chạy bản sửa Bold và evidence

Mở **[notebooks/submission_pipeline.ipynb](notebooks/submission_pipeline.ipynb)**, đặt dữ liệu ở `data/<split>/`, checkpoint đã train ở `artifacts/models/bold_pair_resnet18.pt`, chọn `SPLIT` trong cell cấu hình và chạy từ đầu đến cuối. Cần PyTorch, torchvision, OpenCV, NumPy và Pillow. Khi nộp bài, chọn đúng tập test; ZIP chứa `predictions.jsonl` được notebook sinh tự động.

Thay đổi: loại đường kẻ dài khỏi mask Otsu trước khi đo độ đậm; giữ các ngưỡng và ResNet fallback. Evidence Argmin/Argmax kiểm tra tên trùng trên các hàng trước khi lọc số, giúp giữ đủ ô nhận diện hàng. Không cần script xử lý phụ.

| Đánh giá | Trước | Sau |
|---|---:|---:|
| Bold trên training_set | 515/535 | **535/535** |
| Bold trên validation của checkpoint | 102/107 | **107/107** |
| Private test — bản sửa Bold, trước sửa evidence | 95,71 | **95,82** |
| Private test — thêm sửa evidence (bài 28084) | 95,82 | **95,84** |
| Evidence-F1 trên 11.000 câu, thêm sửa evidence sau Bold | 95,9939% | **96,1182%** |

Bản sửa evidence khắc phục đủ 67 câu thiếu ô ngữ cảnh; không giảm Evidence-F1 trên 11.000 câu và không đổi đáp án. Bài nộp 28084 ngày 27/09/2026 đạt raw 95,84 theo kết quả người dùng cung cấp; so với bản Bold, chỉ evidence của 10 câu private thay đổi, mọi đáp án giữ nguyên. Không có lỗi Bold mới trên 535 câu đã khảo sát. Validation đã được dùng khi train/phân tích lỗi; bài nộp private trước dùng phương pháp kết hợp ô tham chiếu, không phải baseline gốc. Dữ liệu, checkpoint, ZIP và báo cáo thử nghiệm chi tiết được giữ ngoài Git.

Argmin/Argmax vẫn còn các ca khác nhãn về phạm vi hàng, ô gộp và đồng hạng cần làm rõ. Bản sửa này chỉ thay cách chọn evidence, chưa giải quyết các ca đó.

## Ưu tiên cải tiến tiếp theo

- **Argmin/Argmax:** làm rõ phạm vi hàng hợp lệ, ô gộp, tên trùng và đồng hạng; đối chiếu ảnh/OCR/nhãn trước khi đổi quy tắc chọn cực trị.
- **Bold:** giữ bản hiện tại làm mốc; đã đúng 535/535 câu trên tập đã kiểm tra, chưa có bằng chứng đúng tuyệt đối trên dữ liệu mới. Chạy kiểm tra hồi quy nếu thay đổi xử lý bảng hoặc ảnh.
- **Evidence:** giữ sửa lỗi thiếu ô nhận diện; 36 ca đúng chuỗi đáp án nhưng khác ô số cần xử lý cùng vấn đề Argmin/Argmax.

Tạo nhánh công việc mới từ main đã cập nhật (khi working tree sạch):

```bash
git switch main
git pull --ff-only origin main
git switch -c improve/argmin-argmax
```

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
| [main](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/main) | Phiên bản mới nhất: Bold + evidence, private raw 95,84 |
| [baseline](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/baseline) | Code baseline upstream và tài liệu tái hiện |
| [improve/baseline-branches](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/improve/baseline-branches) | Nhánh phát triển Bold + evidence đã được merge vào main |

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
