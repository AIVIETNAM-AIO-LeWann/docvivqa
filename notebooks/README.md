# Notebook

## Baseline upstream đã nhập

- `explore_dataset.ipynb`: khám phá dữ liệu.
- `train_bold_pair_local.ipynb`: huấn luyện mô hình chọn dòng in đậm tại máy.
- `train_bold_pair_colab.ipynb`: phiên bản cho Colab.
- `submission_pipeline.ipynb`: pipeline chính, tạo predictions.
- `baseline.ipynb`: bản tham khảo của upstream.

Chạy notebook local với working directory là thư mục `notebooks/` này. Xem [hướng dẫn baseline](../docs/baseline-setup.md).

## Notebook nghiên cứu dự kiến

1. `01_inspect_dataset.ipynb`: xem schema, ảnh, OCR, câu hỏi và nhãn.
2. `02_visualize_evidence.ipynb`: kiểm tra hệ tọa độ, trang và evidence.
3. `03_baseline_error_analysis.ipynb`: phân tích Visual Bold Lookup, Argmax, Argmin.
4. `04_compare_experiments.ipynb`: so sánh từng thay đổi, LLM và VLM.

Các notebook nghiên cứu trên chưa được tạo. Chuyển code dùng lại sang `src/docvivqa/`; lưu kết quả lớn vào `outputs/`.
