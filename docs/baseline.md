# Baseline và phiên bản cải tiến

## Nguồn

- Upstream: https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round, thư mục DocViVQA.
- Branch `baseline` lưu mã gốc từ snapshot `2aa3ac75343abe87a4a487e964c7cae47e568e6a`.
- Pipeline cải tiến và lượt kiểm toán baseline sử dụng upstream `2bc365327e92152219bf9bc3c4fd6797a150c4c7`.
- Chưa tìm thấy LICENSE trong snapshot upstream; không gán giấy phép mới cho mã kế thừa.

## Chọn phiên bản

| Branch | Notebook suy luận |
|---|---|
| main | `notebooks/submission_pipeline_context_structure.ipynb` |
| baseline | `notebooks/submission_pipeline.ipynb` |

Chuyển branch khi các thay đổi đang làm đã được lưu. Hướng dẫn chạy phiên bản hiện tại nằm trong [README](../README.md). Branch baseline có README riêng cho cấu hình gốc.

Cả hai branch giữ notebook train Bold local và Colab. Checkpoint, dataset và kết quả không được commit. Các bản notebook trung gian có thể xem trong lịch sử Git.

## Kết quả và giới hạn

Phiên bản hiện tại đạt private raw 100,00. Chi tiết thay đổi và phép kiểm tra được ghi trong [báo cáo ngữ cảnh hàng](experiments/2026-10-05-argextreme-context-structure.md).

Training đã dùng nhiều vòng để phân tích lỗi; không xem kết quả training là validation độc lập. Script `scripts/evaluate_predictions.py` chỉ tính accuracy đáp án và coverage. Kết quả ANLS/Evidence-F1 trong báo cáo dùng evaluator upstream.
