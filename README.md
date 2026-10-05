# DocViVQA

**Hỏi đáp trên ảnh tài liệu tiếng Việt, kèm vùng bằng chứng.**

Từ một ảnh tài liệu và câu hỏi, hệ thống xác định thông tin cần tìm, trả lời và chỉ ra vị trí chứng minh trên trang. Dự án phát triển từ baseline của cuộc thi, tập trung cải thiện **nhận diện chữ in đậm**, **Argmin/Argmax** và **định vị bằng chứng**.

**Kết quả private test: 100,00 điểm raw** · Python · PyTorch · OpenCV

## Tổng quan

```text
Ảnh tài liệu + OCR + Câu hỏi
              ↓
     Xác định bảng, hàng và cột
              ↓
  Kiểm tra ngữ cảnh · Chọn hàng · Tính toán
              ↓
       Đáp án + Vùng bằng chứng
              ↓
       predictions.jsonl → ZIP
```

Pipeline hỗ trợ tra cứu, đếm, tính tổng, so sánh, tìm giá trị nhỏ/lớn nhất, tổng qua nhiều trang và tra cứu theo hàng in đậm.

### Các cải tiến chính

| Thành phần | Cách cải thiện |
|---|---|
| **Visual Bold Lookup** | Loại đường kẻ bảng trước khi đo độ dày nét; giữ ResNet18 làm phương án dự phòng. |
| **Argmin / Argmax** | Xử lý ô tên gộp; kiểm tra ngữ cảnh đủ và duy nhất trước khi chọn hàng có giá trị cực trị. |
| **Evidence** | Xét cả những hàng thiếu số khi xác định các ô cần thiết để phân biệt hàng trả lời. |

Mã suy luận sử dụng câu hỏi, ảnh và OCR; nhãn và chú giải chỉ phục vụ huấn luyện, đánh giá hoặc phân tích lỗi.

## Kết quả

| Phiên bản | Điểm raw trên private |
|---|---:|
| Baseline của tác giả | 94,99 |
| Cải thiện Bold | 95,82 |
| Bổ sung sửa evidence | 95,84 |
| Cải thiện xử lý hàng và ngữ cảnh Argmin/Argmax | 98,35 |
| Phiên bản hiện tại | **100,00** |

Các mốc phản ánh kết quả các phiên bản, không phải mọi mốc đều chỉ thay đổi một yếu tố. Trên 11.000 câu training, phiên bản hiện tại đạt ANLS và Evidence-F1 bằng 100%. Training đã được dùng để phân tích và chọn quy tắc; kết quả này là đánh giá hồi cứu. Khả năng tổng quát trên dữ liệu ngoài cuộc thi cần được kiểm tra thêm.

## Bắt đầu

### 1. Chuẩn bị môi trường

```bash
git clone https://github.com/AIVIETNAM-AIO-LeWann/docvivqa.git
cd docvivqa
python3 -m venv .venv
source .venv/bin/activate
python -m pip install torch torchvision opencv-python numpy pillow jupyter
```

### 2. Chuẩn bị dữ liệu và checkpoint

Dataset: [TACVU2 / DocViVQA trên Hugging Face](https://huggingface.co/datasets/lequangaio070206/tacvu2-docvivqa).

Giữ nguyên đường dẫn ảnh và OCR trong từng split:

```text
data/
├── training_set/
├── public_test/
└── private_test/
artifacts/models/
└── bold_pair_resnet18.pt
```

Mỗi split cần `manifest.jsonl`, `questions.jsonl`, `images/` và `ocr/`. Training có thêm nhãn và chú giải. Chuẩn bị riêng dữ liệu của vòng thi cần chạy; quyền truy cập dataset phụ thuộc cấu hình trên Hugging Face.

Đặt checkpoint đã train vào đường dẫn trên. Nếu chưa có, sử dụng [notebook train local](notebooks/train_bold_pair_local.ipynb) hoặc [notebook train Colab](notebooks/train_bold_pair_colab.ipynb). Dữ liệu và checkpoint không được lưu trong Git.

### 3. Chạy pipeline

Mở [notebook suy luận](notebooks/submission_pipeline_context_structure.ipynb), chọn `SPLIT` và chạy toàn bộ cell. Notebook chứa đầy đủ các hàm xử lý và kiểm tra hồi quy.

Hoặc chạy từ terminal:

```bash
python scripts/run_pipeline.py --split private_test --out outputs/private
```

Kết quả ở `outputs/private/submission_private_test.zip`. Kiểm tra trước khi nộp:

```bash
python scripts/validate_submission.py outputs/private/submission_private_test.zip \
  --questions data/private_test/questions.jsonl
```

ZIP chứa `predictions.jsonl`; mỗi dòng có đúng ba trường:

```json
{"question_id":"<id trong questions.jsonl>","answer":"7","evidence":[{"page":1,"bbox":[0.10,0.20,0.30,0.40]}]}
```

Chọn đúng split của vòng thi. Không dùng ZIP training hoặc public để nộp cho private.

## Cấu trúc repository

```text
docvivqa/
├── notebooks/
│   ├── submission_pipeline_context_structure.ipynb  # Suy luận phiên bản hiện tại
│   ├── train_bold_pair_local.ipynb                 # Train Bold tại máy
│   └── train_bold_pair_colab.ipynb                 # Train Bold trên Colab
├── scripts/
│   ├── run_pipeline.py                            # Chạy notebook bằng CLI
│   ├── train_bold_pair.py                         # Chạy train local bằng CLI
│   ├── validate_dataset.py                       # Kiểm tra cấu trúc dữ liệu
│   ├── validate_submission.py                    # Kiểm tra ZIP và question_id
│   └── evaluate_predictions.py                   # Accuracy đáp án và coverage
└── docs/                                         # Dữ liệu, phương pháp và thực nghiệm
```

Script `evaluate_predictions.py` chỉ tính accuracy đáp án và coverage, không thay thế trình chấm ANLS/Evidence-F1 của cuộc thi. Xem [quy ước đánh giá](docs/metrics.md).

## Hai phiên bản để đối chiếu

| Branch | Mục đích |
|---|---|
| [main](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/main) | Pipeline cải tiến hiện tại, dùng làm điểm xuất phát cho phát triển tiếp. |
| [baseline](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/baseline) | Pipeline gốc và notebook train để tái hiện, đối chiếu. |

Các phiên bản trung gian vẫn có trong lịch sử Git. Dataset, checkpoint và kết quả chạy được giữ ngoài repository.

## Tài liệu

- [Nguồn baseline và cách tái hiện](docs/baseline.md)
- [Chuẩn bị dữ liệu](docs/data.md)
- [Metric đánh giá](docs/metrics.md)
- [Phân tích cải tiến ngữ cảnh hàng](docs/experiments/2026-10-05-argextreme-context-structure.md)
- [Paper Tracker](docs/papers/paper-tracker.csv)

## Nguồn kế thừa

Dự án phát triển từ [baseline DocViVQA của T-Sunm](https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round). Các cải tiến tập trung vào xử lý ảnh ô bảng, lựa chọn hàng và xây dựng vùng bằng chứng trên pipeline này.
