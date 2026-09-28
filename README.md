# DocViVQA

Nghiên cứu cải thiện hỏi đáp trên ảnh tài liệu tiếng Việt và định vị vùng bằng chứng, tập trung vào **Visual Bold Lookup, Argmax, Argmin**, đồng thời khảo sát LLM/VLM.

Branch `main` là phiên bản làm việc chung mới nhất, đã tích hợp sửa Bold, evidence và Argmin/Argmax vào `notebooks/submission_pipeline.ipynb`. Bản trước chỉ sửa Bold + evidence đạt private raw **95,84**. Candidate trên nhánh `codex/pipeline-rnd` đạt raw **97,683267857**, sau đó biến thể loại hậu tố OCR `Đã đối chiếu` đạt **98,2605** cho 2.000 câu theo kết quả người dùng cung cấp ngày 28/09/2026; xem [báo cáo vòng private](docs/experiments/2026-09-28-private-round-readiness.md) và [thử nghiệm](docs/experiments/2026-09-28-argextreme-no-suffix.md). Các cải tiến tiếp theo được thử riêng trên nhánh R&D.

## Chạy pipeline hiện tại

Mở **[notebooks/submission_pipeline.ipynb](notebooks/submission_pipeline.ipynb)**, đặt dữ liệu ở `data/<split>/`, checkpoint đã train ở `artifacts/models/bold_pair_resnet18.pt`, chọn `SPLIT` trong cell cấu hình và chạy từ đầu đến cuối. Cần PyTorch, torchvision, OpenCV, NumPy và Pillow. Khi nộp bài, chọn đúng tập test; ZIP chứa `predictions.jsonl` được notebook sinh tự động.

Thay đổi: loại đường kẻ dài khỏi mask Otsu trước khi đo độ đậm; giữ các ngưỡng và ResNet fallback. Evidence Argmin/Argmax kiểm tra tên trùng trên các hàng trước khi lọc số, giúp giữ đủ ô nhận diện hàng. Argmin/Argmax chỉ xét hàng vật lý đầu mà mỗi ID ô tên phủ xuống (kể cả khi số ở hàng đó thiếu); nếu không còn ứng viên thì dùng danh sách gốc. Không cần script xử lý phụ.

| Đánh giá | Trước | Sau |
|---|---:|---:|
| Bold trên training_set | 515/535 | **535/535** |
| Bold trên validation của checkpoint | 102/107 | **107/107** |
| Private test — bản sửa Bold, trước sửa evidence | 95,71 | **95,82** |
| Private test — thêm sửa evidence (bài 28084) | 95,82 | **95,84** |
| Evidence-F1 trên 11.000 câu, thêm sửa evidence sau Bold | 95,9939% | **96,1182%** |

Bản sửa evidence khắc phục đủ 67 câu thiếu ô ngữ cảnh; không giảm Evidence-F1 trên 11.000 câu và không đổi đáp án. Bài nộp 28084 ngày 27/09/2026 đạt raw 95,84 theo kết quả người dùng cung cấp; so với bản Bold, chỉ evidence của 10 câu private thay đổi, mọi đáp án giữ nguyên. Không có lỗi Bold mới trên 535 câu đã khảo sát. Validation đã được dùng khi train/phân tích lỗi; bài nộp private trước dùng phương pháp kết hợp ô tham chiếu, không phải baseline gốc. Dữ liệu, checkpoint, ZIP và báo cáo thử nghiệm chi tiết được giữ ngoài Git.

### Kết quả thêm sửa Argmin/Argmax

So với bản Bold + evidence, trên toàn bộ 11.000 câu training:

| Chỉ số | Trước | Sau |
|---|---:|---:|
| ANLS | 96,4040% | 98,0101% |
| Evidence-F1 | 96,1182% | 97,8545% |
| Điểm tổng hợp /100 | 96,3611 | 97,9868 |
| Đúng đáp án Argmin | 1664/1874 | 1751/1874 |
| Đúng đáp án Argmax | 1705/1898 | 1796/1898 |

Sửa đúng 180 đáp án, làm sai mới 2 đáp án Argmax (`B-train-00268-q10`, `B-train-00355-q01`). Điểm từng câu tăng ở 203 câu, giảm ở 2 câu. Full run trùng kết quả thử nghiệm; các nhánh ngoài Argmin/Argmax giữ nguyên. Đây là đánh giá hồi cứu trên tập đã phân tích. Candidate private có 41 câu đổi đáp án và 5 câu chỉ đổi evidence so với bản Bold + evidence trước đó; điểm raw do người dùng cung cấp là 97,683267857, cao hơn mốc 95,84 khoảng 1,84 điểm. Không có nhãn private để phân tích lỗi từng câu.

Quy tắc dùng ID ô và bbox OCR, không dùng chú giải/nhãn khi suy luận. Giữ toàn bộ hàng trước lọc số để chọn evidence. Các ca ô gộp, phạm vi hàng và đồng hạng còn lại cần tiếp tục xác minh.

## Ưu tiên cải tiến tiếp theo

- **Argmin/Argmax:** làm rõ phạm vi hàng hợp lệ, ô gộp, tên trùng và đồng hạng; đối chiếu ảnh/OCR/nhãn trước khi đổi quy tắc chọn cực trị.
- **Bold:** giữ bản hiện tại làm mốc; đã đúng 535/535 câu trên tập đã kiểm tra, chưa có bằng chứng đúng tuyệt đối trên dữ liệu mới. Chạy kiểm tra hồi quy nếu thay đổi xử lý bảng hoặc ảnh.
- **Evidence:** giữ sửa lỗi thiếu ô nhận diện; tiếp tục kiểm tra các ca còn khác ô số sau thay đổi Argmin/Argmax.

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
| [main](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/main) | Phiên bản mới nhất: Bold + evidence + Argmin/Argmax; đang chờ điểm private |
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
