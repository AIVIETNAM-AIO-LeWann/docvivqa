# Baseline DocViVQA gốc

- Nguồn: https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round
- Commit: `2aa3ac75343abe87a4a487e964c7cae47e568e6a`
- Ngày nhập: 2026-09-18.
- Toàn bộ file được Git theo dõi trong `DocViVQA/` được sao chép nguyên trạng vào [DocViVQA/](DocViVQA/). Không sửa notebook, script hay output có sẵn trong notebook.
- Các CSV, hình và output notebook đi kèm là của upstream, không phải kết quả nhóm tự chạy.
- Không tìm thấy file LICENSE trong snapshot upstream; không gán giấy phép của dự án này cho code nhập từ upstream.

## Điểm bắt đầu

Đọc [README gốc](DocViVQA/README.md), sau đó mở [pipeline chính](DocViVQA/notebooks/submission_pipeline.ipynb). `baseline.ipynb` chỉ là bản tham khảo của upstream.

Để giữ nguyên đường dẫn của code gốc:

1. Chuẩn bị dữ liệu tại `baselines/DocViVQA/data/training_set/` (gồm manifest, questions, labels, OCR, ảnh và các file do bộ dữ liệu cung cấp).
2. Chạy notebook với working directory là `baselines/DocViVQA/notebooks/`. Notebook tính thư mục gốc từ thư mục làm việc của kernel; kiểm tra giá trị `ROOT` được in ra.
3. Checkpoint bold, nếu có, nằm trong `baselines/DocViVQA/artifacts/models/`; predictions được ghi vào `baselines/DocViVQA/outputs/`.

Dữ liệu, checkpoint và output mới được bỏ qua bởi Git. Chưa cài môi trường hay chạy pipeline. Lệnh cài package ở README dự án chỉ cài scaffold, chưa cài các thư viện cho baseline.

## Đánh giá

Pipeline mặc định chạy `training_set`. Script `evaluate_predictions.py` báo coverage và accuracy bằng đối chiếu answer với danh sách đáp án; chưa tính ANLS, Evidence-F1 hoặc điểm tổng hợp của đề. Cần xác minh evaluator trước khi báo cáo kết quả. Chia tập theo document và kiểm tra tập huấn luyện của checkpoint trước khi dùng làm mốc so sánh.
