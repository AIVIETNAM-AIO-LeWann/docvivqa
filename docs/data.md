# Dữ liệu và kết quả tại máy

Đặt dữ liệu giải nén vào `data/training_set/` ở gốc repo. Giữ đúng đường dẫn ảnh và OCR được khai báo trong `manifest.jsonl`. Các file đầu vào gồm manifest, questions, labels, OCR, ảnh và nhãn đi kèm. `public_test/` và `private_test/` đặt cùng cấp nếu được cung cấp.

Chưa có dataset trong repository. Dataset và PDF paper chỉ lưu tại máy, không đưa vào GitHub. Ghi nguồn, phiên bản và ngày tải khi chuẩn bị dữ liệu.

- Danh sách chia tập theo document: `data/splits/` (ghi seed và phương pháp chia).
- Checkpoint bold: `artifacts/models/bold_pair_resnet18.pt`.
- Predictions và kết quả thô: `outputs/<run-id>/`.
- Kết quả tổng hợp, cấu hình và cách tái hiện: [nhật ký thực nghiệm](experiments/experiment-template.md).

Các thư mục dữ liệu, checkpoint và output được tạo khi cần và bỏ qua bởi Git. Nếu cần đưa danh sách split vào repo, chỉ theo dõi các file đã kiểm tra nội dung.
