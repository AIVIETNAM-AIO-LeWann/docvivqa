# Sửa Bold: loại đường kẻ trước khi đo độ dày — 25/09/2026

## Thay đổi

Trong `cell_stroke_width`, sau Otsu và xóa mép 3%, loại các pixel thuộc cấu trúc nét ngang/dọc dài trước khi tính distance transform. Giữ nguyên vùng cắt, công thức đo, phép median, ngưỡng 0,02, ngưỡng bỏ phiếu 4 và fallback ResNet với ngưỡng 0,60.

Luồng mới:

```text
Ảnh ô → ảnh xám → Otsu → xóa mép → bỏ nét kẻ dài
       → điểm độ dày nét → median hàng → bỏ phiếu → ResNet khi cần
```

Kernel ngang: `1 × max(15, round(0.55 × chiều rộng))`.
Kernel dọc: `max(15, round(0.80 × chiều cao)) × 1`.
Các thông số được giữ từ thí nghiệm chẩn đoán trước đó, không chỉnh sau khi xem kết quả 535 câu.
Mask còn dưới 10 pixel tiền cảnh trả `None` như cơ chế bỏ qua ô không đo được của baseline.

## Đối chiếu đầy đủ

| Phạm vi | Baseline đầy đủ | Sau sửa | Sửa đúng | Làm sai mới |
|---|---:|---:|---:|---:|
| Tất cả Bold | 515/535 | **535/535** | 20 | 0 |
| Train của checkpoint | 413/428 | **428/428** | 15 | 0 |
| Validation của checkpoint | 102/107 | **107/107** | 5 | 0 |

- ANLS của Bold: 96,90% → **100%**.
- Evidence-F1 của Bold: 99,12% → **100%**.
- Số lần gọi ResNet: 12 → **0** trên 535 câu này. ResNet vẫn được giữ làm fallback cho dữ liệu khác.
- Tất cả 10.465 câu ngoài Bold có dự đoán **giống hệt** bản gốc, gồm cả answer và evidence.
- Câu `B-train-00696-q02` trả lời đúng sau khi chọn đúng hàng; quy tắc fallback lấy ô gần nhất chưa sửa. Nguy cơ đó vẫn tồn tại ở trường hợp khác.
- Không sửa Argmin/Argmax, parser hay quy tắc evidence của baseline đã được kiểm toán.

Đây là đánh giá hồi cứu trên training_set. Validation đã được theo dõi khi train và khi chẩn đoán lỗi. Kết quả 100% không phải đánh giá trên test độc lập; kết quả private test sau đó được ghi ở mục dưới. Cần lưu ý khả năng nét chữ dài bị bộ lọc nhận nhầm trên dữ liệu khác.

## Kết quả private test do người dùng cung cấp

| Submission | Phiên bản | Raw | Chuẩn hóa |
|---|---|---:|---:|
| 27793 | Bài nộp trước, kết hợp ô tham chiếu | 95,71 | 97,96 |
| 27890 | Bỏ đường kẻ trước khi đo Bold | **95,82** | **98,17** |

Điểm raw tăng **0,11 điểm**. Đối chiếu hai ZIP: 3/2.000 câu thay đổi cả answer và evidence, đều là Bold; 1.997 câu còn lại không đổi. Không có nhãn private để kết luận riêng từng câu thay đổi là đúng hay sai.

Mức tăng private này so với phiên bản trước của dự án, không phải so riêng với baseline gốc. Điểm chuẩn hóa phụ thuộc bảng xếp hạng; dùng raw để so sánh.

## Mã và notebook để sử dụng

- [Hàm xử lý](../../scripts/bold_grid_cleanup.py): `remove_grid_lines`, `cell_stroke_width`.
- [Bộ đối chiếu](../../scripts/experiment_bold_grid_cleanup.py): chạy lại baseline gốc cho đủ 535 câu, đối chiếu với kết quả đã lưu; chạy bản sửa trên 11.000 câu và kiểm tra các nhánh khác không đổi.
- **[Notebook chạy đầy đủ](../../notebooks/submission_pipeline_bold_grid_clean.ipynb)**: bản chạy đã tích hợp sửa Bold, giữ các solver của pipeline gốc commit `2bc365327e92152219bf9bc3c4fd6797a150c4c7` được dùng trong báo cáo 24/09.

Notebook này là bản nên dùng để tái hiện kết quả trong báo cáo. Notebook `submission_pipeline.ipynb` cũ và các notebook thử nghiệm reference-pixel trước đó không bị ghi đè.

Notebook mới có phần xử lý nhúng sẵn để chạy độc lập, không cần import từ thư mục scripts. Thay đổi nguồn so với bản kiểm toán chỉ ở phần giới thiệu, cấu hình đường dẫn, giải thích Bold và cell 34 đo nét. Ngoài ra, sửa bbox dữ liệu giả trong self-test ở cell 43: chiều cao hàng từ 0,10 xuống 0,02 để hợp lệ với điều kiện `data_rows < 0,06`. Self-test gốc thất bại vì chính fixture bị lọc bỏ; không thay solver Argmin/Argmax.

### Chạy notebook trên máy hiện tại

1. Mở `notebooks/submission_pipeline_bold_grid_clean.ipynb`.
2. Chọn môi trường `.venv` của dự án.
3. Chạy từ đầu tới cuối; `SPLIT = 'training_set'` ở cell cấu hình.
4. Trên máy đã làm thực nghiệm, checkpoint thật nằm tại `artifacts/models/bold_pair_resnet18.pt`; không cần train lại. Sau khi clone ở máy khác, cần tự đặt checkpoint đã train vào đường dẫn này (hoặc truyền `--checkpoint` khi chạy script tạo ZIP).
5. Kết quả notebook ở `outputs/bold-grid-cleanup/inference/`.

ZIP được tạo cho training_set chỉ dùng kiểm tra, không dùng nộp thay cho public/private test. Nếu chuyển máy cần mang theo checkpoint, mã và dữ liệu; notebook sẽ báo lỗi nếu checkpoint thiếu.

### Tái chạy đối chiếu A/B

```bash
cd /home/lequang/AIO_2026/docvivqa
.venv/bin/python scripts/experiment_bold_grid_cleanup.py
```

Bộ đối chiếu dùng dữ liệu local, nguồn baseline và checkpoint trong `outputs/baseline-full-error-analysis/` từ lượt phân tích 24/09.

## Kết quả lưu

Các đường dẫn sau là kết quả local, nằm trong `.gitignore` và không được tải lên GitHub:

- `outputs/bold-grid-cleanup/index.html`: báo cáo so sánh.
- `outputs/bold-grid-cleanup/comparison.csv`: 535 câu trước/sau.
- `outputs/bold-grid-cleanup/summary.json`: metrics, hash nguồn/checkpoint/hàm sửa và phiên bản thư viện.
- `outputs/bold-grid-cleanup/predictions-training_set.jsonl`: đủ 11.000 dự đoán.

## Kiểm tra

- Baseline chạy lại trùng khớp toàn bộ 535 dự đoán Bold đã lưu.
- So sánh đủ 535 câu, tách 428 train / 107 validation theo metadata checkpoint thật.
- 10.465 dự đoán ngoài Bold không đổi.
- Evaluator gốc được chạy độc lập để đối chiếu ANLS/Evidence-F1.
- Notebook chạy từ đầu đến cuối, gồm regression checks gốc; 11.000 dự đoán trùng bộ đối chiếu, ZIP chỉ chứa `predictions.jsonl` với đủ ID duy nhất.
