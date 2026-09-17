# Metric và quy ước cần xác minh

Theo Reading trang 5–6:

- `Question Score = 0.85 * ANLS + 0.15 * Evidence-F1`.
- ANLS đánh giá đáp án; Evidence-F1 đánh giá vùng bằng chứng.
- Một bbox khớp khi cùng trang và IoU ≥ 0.5.
- Submission gồm `question_id`, `answer`, `evidence`; mỗi evidence có `page`, `bbox`.
- Bbox có dạng `[x1, y1, x2, y2]`, chuẩn hóa theo chiều rộng/cao về [0, 1].

Trước khi chạy, đọc evaluator tham khảo để xác nhận:

- Chuẩn hóa đáp án và ngưỡng ANLS.
- Quy tắc ghép một-một giữa các bbox; xử lý evidence rỗng/trùng.
- Quy ước chỉ số trang và cách tổng hợp điểm.
- Quy tắc với prediction thiếu, sai định dạng hoặc nhiều đáp án chấp nhận.

Chưa triển khai evaluator riêng. EM/F1 trong các paper như TAT-DQA không đồng nhất với ANLS/Evidence-F1 của đề này.
