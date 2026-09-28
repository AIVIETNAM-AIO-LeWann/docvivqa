# Dữ liệu và kết quả tại máy

Đặt dữ liệu đã giải nén vào ba thư mục cùng cấp ở gốc repo:

```text
data/
├── training_set/    # manifest, questions, labels, cell annotations, images/, ocr/
├── public_test/     # manifest, questions, images/, ocr/
└── private_test/    # manifest, questions, images/, ocr/
```

Giữ nguyên cấu trúc bên trong từng split và đường dẫn tương đối trong
`manifest.jsonl`; không chuyển ảnh/OCR ra khỏi split. File ZIP nguồn chỉ dùng để
phân phối hoặc sao lưu, không cần đặt trong `data/` để chạy notebook.

### Bản dữ liệu local được kiểm tra ngày 28/09/2026

| Split | Tài liệu | Câu hỏi | Tệp | Dung lượng byte |
|---|---:|---:|---:|---:|
| `training_set` | 1.100 | 11.000 | 2.530 | 739.735.469 |
| `public_test` | 100 | 1.000 | 233 | 62.339.745 |
| `private_test` | 200 | 2.000 | 467 | 122.614.016 |

Đã kiểm tra 3.230 tệp giống hệt bản nguồn theo nội dung, không chỉ theo tên và
dung lượng. Tất cả đường dẫn ảnh/OCR trong manifest tồn tại; ID tài liệu/câu hỏi
không trùng, câu hỏi trỏ đến tài liệu hợp lệ và training có đủ 11.000 nhãn.
Thông tin đường dẫn nguồn của bản sao được lưu trong `data/README.local.md` trên
máy này. Vì toàn bộ `data/` nằm trong `.gitignore`, bảng trên là mốc kiểm tra
cho bản local, không phải cam kết về nội dung của mọi bản tải sau này.

Khi thay dataset, nên thay trọn từng thư mục split bằng cùng một phiên bản và
kiểm tra lại manifest trước khi chạy; tránh chép đè gây sót tệp cũ. Không dùng
nhãn training làm đầu vào suy luận. `public_test` và `private_test` không có nhãn
trong bản dữ liệu này.

Kiểm tra lại cấu trúc sau khi tải/cập nhật bằng
`python scripts/validate_dataset.py --data-root data` (chỉ dùng thư viện chuẩn).
Script kiểm tra JSONL, ID, số trang/câu hỏi, đường dẫn ảnh/OCR và nhãn training.

Dataset và PDF paper chỉ lưu tại máy, không đưa vào GitHub. Ghi nguồn, phiên
bản và ngày tải khi chuẩn bị dữ liệu.

- Danh sách chia tập theo document: `data/splits/` (ghi seed và phương pháp chia).
- Checkpoint bold: `artifacts/models/bold_pair_resnet18.pt`. Bản cũ không có
  trên máy này; bản mới đã train từ dataset local và được ghi lại trong
  [mốc R&D](experiments/2026-09-28-rnd-baseline.md). Giữ cố định checkpoint
  khi so sánh các thay đổi pipeline.
- Predictions và kết quả thô: `outputs/<run-id>/`.
- Kết quả tổng hợp, cấu hình và cách tái hiện: [nhật ký thực nghiệm](experiments/experiment-template.md).

Các thư mục dữ liệu, checkpoint và output được tạo khi cần và bỏ qua bởi Git. Nếu cần đưa danh sách split vào repo, chỉ theo dõi các file đã kiểm tra nội dung.
