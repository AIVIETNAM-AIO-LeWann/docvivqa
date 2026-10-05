# Argmin/Argmax: kiểm tra ngữ cảnh nhận diện hàng

Ngày: 05/10/2026.

## Kết quả

Bản thử nghiệm phát triển từ `notebooks/submission_pipeline_context_notes.ipynb` — phiên bản người dùng báo điểm private raw 98,35. Mã mới ở `notebooks/submission_pipeline_context_structure.ipynb`.

| Phạm vi training | Số câu | Sửa đáp án | Chỉ sửa evidence | Câu giảm điểm | Điểm trước → sau |
|---|---:|---:|---:|---:|---:|
| Argmin | 1.874 | 64 | 5 | 0 | 96,6639 → 100 |
| Argmax | 1.898 | 78 | 2 | 0 | 95,9642 → 100 |
| Toàn bộ | 11.000 | 142 | 7 | 0 | 98,7353 → 100 |

Điểm local = 100 × (0,85 × ANLS + 0,15 × Evidence-F1). Toàn tập: ANLS từ 98,7512 lên 100; Evidence-F1 từ 98,6455 lên 100; đáp án khớp một đáp án chuẩn từ 10.858 lên 11.000. Các nhánh ngoài Argmin/Argmax có dự đoán giống hệt bản đối chiếu.

**Đây là đánh giá hồi cứu trên training đã được dùng nhiều vòng để phân tích lỗi và lựa chọn quy tắc. Không phải kết quả trên tập giữ riêng. Người dùng đã cung cấp kết quả bài nộp 28721 ngày 05/10/2026: private raw **100,00**, chuẩn hóa **100,00** (tăng 1,65 điểm raw từ 98,35).** Đạt 100% ở đây không chứng minh thuật toán đúng trên mọi bảng hoặc dữ liệu thực tế.

## Vấn đề và cách xử lý

Phép so sánh số min/max vẫn đúng. Khác biệt nằm ở việc xác định những hàng nào được tham gia so sánh. Các quy tắc dưới đây là giả thuyết thực nghiệm phù hợp nhãn training, chưa có xác nhận độc lập về quy tắc sinh câu hỏi của bộ dữ liệu.

### 1. Nội dung trước cột giá trị không phân biệt được hai hàng

Hai hàng có thể có cùng tên và cùng toàn bộ nội dung bên trái cột số nhưng là các ô OCR khác nhau. Bản trước vẫn chọn số cực trị trong các hàng đó. Bản mới kiểm tra chuỗi nội dung bên trái cột số và danh tính ô OCR để loại ứng viên không xác định duy nhất khi còn ứng viên khác.

Không loại mọi tên lặp: hai hàng cùng tên nhưng được phân biệt bằng một cột ngữ cảnh khác vẫn có thể hợp lệ. Ô gộp dùng lại cùng ID cũng không tự động bị xem là hai thực thể khác nhau. Khi kiểm tra sự trùng lặp, xét cả hàng không có số hợp lệ vì hàng đó vẫn có thể làm tên/ngữ cảnh bị mơ hồ.

### 2. Thiếu ô trong phần ngữ cảnh cần dùng

Một hàng thiếu ô có thể khiến danh sách OCR nối hai ô không liền nhau và tạo cảm giác ngữ cảnh đã đầy đủ. Bản mới xác định chuỗi ô ngắn nhất đủ phân biệt hàng; trong chuỗi này, kiểm tra khe hở ngang giữa bbox của hai ô liên tiếp.

Nếu `x_left` của ô sau lớn hơn `x_right` của ô trước quá `1e-6`, coi ngữ cảnh cần dùng có khoảng thiếu. Chỉ kiểm tra phần cần để nhận diện hàng; không loại hàng chỉ vì một ô không liên quan ở phía sau bị trống.

Giả định quan trọng: bbox trong dữ liệu này biểu diễn vùng ô bảng. Quy tắc khe hở không áp dụng nguyên xi cho OCR bbox chỉ bao nét chữ, vì khoảng trắng giữa các từ/ô khi đó là bình thường.

### 3. Chuỗi ngắn phải so với phần đầu chuỗi dài

Ví dụ hàng A chỉ có ngữ cảnh `[A]`, hàng khác có `[A, 20]`. So sánh toàn chuỗi sẽ cho rằng hai chuỗi khác nhau. Tuy nhiên chỉ đọc `A` chưa đủ phân biệt hàng đầu với hàng thứ hai.

Bản mới so sánh ngữ cảnh ứng viên với phần đầu cùng độ dài của mọi hàng khác. Nhờ đó việc mất ô không làm chuỗi ngắn bị nhận nhầm là duy nhất.

Sau mỗi bộ lọc, nếu không còn ứng viên nào thì giữ danh sách trước bộ lọc đó để tránh bỏ trống đáp án. Cuối cùng lấy min/max trong các ứng viên còn lại và tạo evidence bằng logic hiện có.

## Thử nghiệm theo từng bước

| Bước | Thay đổi | Sửa thêm đáp án | Sửa thêm evidence | Câu giảm điểm | Điểm toàn tập |
|---|---|---:|---:|---:|---:|
| Bản đối chiếu | Context notes | — | — | — | 98,7353 |
| 1 | Ngữ cảnh toàn phần phải duy nhất | 96 | 0 | 0 | 99,5949 |
| 2 | Không thiếu ô trong phần nhận diện cần dùng | 37 | 7 | 0 | 99,9251 |
| 3 | Đối chiếu chuỗi ngắn với phần đầu chuỗi dài | 9 | 0 | 0 | 100 |

Đã khảo sát 5 phương án qua 3 bước. Một phương án kiểm tra mọi khe hở trong toàn bộ phần bên trái cột số gây 205 câu giảm điểm so với bước 1, nên không chọn. Phương án chỉ xét sự trùng lặp giữa các ứng viên còn lại cũng kém hơn xét toàn bộ hàng.

Không thêm ngoại lệ theo question_id/document_id, không đọc `labels.jsonl` hoặc `cell_annotations.jsonl` để suy luận. Nhãn chỉ dùng sau khi sinh dự đoán để đo kết quả và phân tích lỗi. Không thêm mô hình tiền huấn luyện mới.

## Kiểm chứng và bài nộp

Đã chạy notebook đầy đủ trên training (11.000 câu) và private (2.000 câu), có kiểm tra các tình huống giả lập: tên lặp nhưng ngữ cảnh khác; thiếu ô cần thiết; thiếu ô không liên quan; toàn bộ ứng viên mơ hồ; chuỗi ngắn trùng phần đầu chuỗi dài. Dự đoán training của lần chạy đầy đủ khớp chính xác dự đoán của thí nghiệm lựa chọn cuối.

Private có 33 câu đổi đáp án so với bản raw 98,35. **Không có nhãn private nên không thể kết luận 33 thay đổi này đều đúng.** Không dùng điểm/nhãn private để lựa chọn phương án mới.

ZIP cuối:

`outputs/argextreme-context-structure/private-final/private_submission_argextreme_unique_context.zip`

- Chứa `predictions.jsonl`, đủ đúng 2.000 ID, mỗi ID một lần.
- Đã kiểm tra đúng ba trường, answer không rỗng, page hợp lệ, bbox chuẩn hóa, evidence không rỗng và đọc lại ZIP thành công.
- SHA256: `e6afaa077d4a9e2cb390a18caf29ee78184be3d9956f059f93a687c83ef234f4`.
- `private-final/run.json` lưu hash mã nguồn, checkpoint, dữ liệu đầu vào và kết quả.
- Có nạp checkpoint ResNet18 thật; lần chạy private không cần gọi nhánh ResNet dự phòng.
- Người dùng đã nộp ZIP và báo kết quả raw 100,00; mã bài nộp 28721. Notebook công bố chỉ cập nhật phần mô tả kết quả sau lượt chạy, các cell code giữ nguyên so với snapshot đã tạo ZIP.

## Tái hiện

1. Cài PyTorch, torchvision, OpenCV, NumPy và Pillow trong môi trường notebook.
2. Đặt dữ liệu tại `data/private_test/` gồm manifest, questions, OCR và ảnh theo cấu trúc gốc.
3. Đặt checkpoint đã train tại `artifacts/models/bold_pair_resnet18.pt`. Checkpoint và dữ liệu không nằm trong Git; dùng các notebook train Bold trong repository nếu cần tạo checkpoint.
4. Mở `notebooks/submission_pipeline_context_structure.ipynb` từ thư mục dự án hoặc `notebooks/`.
5. Đặt `SPLIT = 'private_test'` ở cell cấu hình và chạy từ đầu đến cuối. Các kiểm tra hồi quy chạy trước khi sinh dự đoán.
6. ZIP nằm tại `outputs/argextreme-context-structure/inference/submission_private_test.zip`, chứa `predictions.jsonl`.

Notebook chứa đầy đủ các hàm xử lý, không cần script thực nghiệm local. Muốn kiểm tra training, đặt `SPLIT = 'training_set'`; ZIP training không dùng để nộp private.

## Tài liệu đối chiếu

Các đường dẫn bên dưới là artifact local, được bỏ qua bởi Git. Chúng không phải phụ thuộc để chạy notebook.

- `outputs/argextreme-context-structure/summary.json`: số liệu tổng hợp cuối.
- `outputs/argextreme-context-structure/comparison.csv`: đối chiếu toàn bộ training.
- `outputs/argextreme-context-structure/index.html`: 149 câu thay đổi.
- `outputs/argextreme-context-structure/private-final/changes-vs-98.35.json`: 33 câu private thay đổi.
- `outputs/argextreme-context-structure/training-final/`: lần chạy training cuối.
- `outputs/argextreme-unique-context/`, `outputs/argextreme-context-gaps/`, `outputs/argextreme-prefix-validation/`: các phương án đã khảo sát.
- Các thư mục `training/`, `private/` và `intermediate-remaining-errors.json` trong `argextreme-context-structure/` là kết quả trung gian sau bước 2; dùng thư mục có hậu tố `-final` để lấy kết quả cuối.
