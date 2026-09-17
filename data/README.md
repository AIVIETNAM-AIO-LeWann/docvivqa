# Dữ liệu

- `raw/`: dữ liệu gốc tải từ nguồn của chương trình; giữ nguyên cấu trúc khi giải nén.
- `processed/`: dữ liệu được tạo từ script/notebook, có thể tái tạo.
- `splits/`: danh sách document ID cho train/dev/held-out, lưu seed và cách chia.

Chưa có dữ liệu trong repository. Chỉ chuyển đổi định dạng sau khi kiểm tra schema thực tế; không giả định OCR block luôn bằng một cell.

Ghi nguồn tải, phiên bản, ngày tải, checksum nếu có và điều kiện sử dụng tại đây khi nhập dữ liệu. Không commit dữ liệu theo mặc định. Nếu công bố danh sách split, kiểm tra nội dung trước khi theo dõi bằng Git.
