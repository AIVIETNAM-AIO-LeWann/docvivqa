# EXP-RND-003 — sàng lọc bộ xếp hạng Argmin/Argmax

- Ngày: 28/09/2026; nhánh `codex/pipeline-rnd`.
- Mục đích: kiểm tra xem đặc trưng OCR/bố cục có giúp chọn đáp án trong nhóm
  Argmin/Argmax còn sai hay không, trước khi thử full pipeline/private.
- Dữ liệu: 3.772 câu Argmin/Argmax training; bảng ứng viên từ CSV lịch sử ở
  commit `861409e`. Loại ứng viên có hậu tố OCR `Đã đối chiếu` khi có ứng viên
  sạch, giống biến thể [EXP-RND-002](2026-09-28-argextreme-no-suffix.md).
- Nhãn private, ảnh private và score private **không** đi vào huấn luyện.

Chia năm fold bằng SHA-256 của `document_id`, nên mọi câu của cùng tài liệu ở
cùng fold. Với từng fold, train trên bốn fold còn lại; báo dự đoán ngoài fold.
Đặc trưng gồm hạng số, giá trị tương đối, vị trí hàng, số lần tên xuất hiện,
độ dài tên và kiểu Argmin/Argmax. Thử mô hình tuyến tính và MLP một tầng ẩn,
200 epoch cố định, cùng seed. Script: `scripts/experiment_argextreme_reranker.py`.

| Mô hình | Đúng / 3.772 | Chênh so với pipeline hiện tại |
|---|---:|---:|
| Pipeline `argextreme-no-suffix` | **3.599** | Mốc |
| Linear reranker | 3.252 | −347 |
| MLP reranker | 3.425 | −174 |

Cả năm fold của MLP đều kém pipeline. Thử chỉ dùng MLP khi xác suất top ≥
0,70/0,80/0,90/0,95: số câu đổi lần lượt 83/54/30/15; **0 câu sai cũ được
sửa**, làm sai mới lần lượt 75/50/27/15. Những ngưỡng này được xem sau khi
chạy cross-validation nên chỉ là sàng lọc, không phải ước lượng hiệu năng độc
lập của một chính sách đã chốt.

Giới hạn: CSV ứng viên được dựng bằng solver cũ, không tái hiện hoàn toàn quy
tắc hàng vật lý đầu của pipeline hiện tại. Vì kết quả đã kém xa ngay ở mức
sàng lọc, không đưa reranker vào notebook và không tạo ZIP private. Candidate
private có điểm 98,2605 giữ nguyên.

Tái chạy:

```powershell
python scripts/experiment_argextreme_reranker.py --model linear --epochs 200 --out outputs/pipeline-rnd/reranker-linear-200-cv.json
python scripts/experiment_argextreme_reranker.py --model mlp --epochs 200 --out outputs/pipeline-rnd/reranker-mlp-200-cv.json
```
