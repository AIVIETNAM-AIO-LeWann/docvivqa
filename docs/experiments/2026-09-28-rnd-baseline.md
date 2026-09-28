# EXP-RND-001 — Mốc pipeline với checkpoint Bold train lại trên GPU

- Ngày: 28/09/2026.
- Nhánh: `codex/pipeline-rnd`, xuất phát từ `main` commit `eca7eac6`.
- Trạng thái: đã chạy, **chưa thay đổi thuật toán suy luận**.
- Dataset: ba split local mô tả tại [`docs/data.md`](../data.md).
- Pipeline: `notebooks/submission_pipeline.ipynb` qua `scripts/run_pipeline.py`.
- Checkpoint: `artifacts/models/bold_pair_resnet18.pt` (ngoài Git), SHA-256
  `06f850b893f97e5469dc320ab4455ac5d4db131b492ea331f32b7b88bc30db60`.
- Notebook pipeline SHA-256:
  `fbb318cf8c465837f61e0bc30c8a370673656842417f8ebdb51b200fd6b509a1`.

## Môi trường và checkpoint

RTX 4050 Laptop GPU (6 GB), Python 3.12.14, PyTorch 2.14.0+cu130,
torchvision 0.29.0+cu130, OpenCV headless 5.0.0, NumPy 2.5.2. GPU đã qua phép
tính tensor thử. Môi trường ở `.venv/`; cache tải package và trọng số pretrained
ở `artifacts/`, đều nằm ngoài Git.

Thiết lập lại các phụ thuộc chính trên Windows bằng `uv`:

```powershell
$env:UV_CACHE_DIR='D:\Projects\docvivqa\artifacts\uv-cache'
uv venv .venv --python 3.12
uv pip install --python .venv\Scripts\python.exe 'torch==2.14.0+cu130' 'torchvision==0.29.0+cu130' --index-url https://download.pytorch.org/whl/cu130
uv pip install --python .venv\Scripts\python.exe 'opencv-python-headless==5.0.0.93'
```

Wheel CUDA được lấy từ [chỉ dẫn cài đặt PyTorch](https://docs.pytorch.org/get-started/locally/);
NumPy và Pillow được cài cùng các phụ thuộc của hai package trên. Kiểm tra
`torch.cuda.is_available()` trước khi train.

Train từ `notebooks/train_bold_pair_local.ipynb` qua `scripts/train_bold_pair.py`:
seed 20260813, batch 16, 12 epoch, 535 cặp Bold; 428 cặp train và 107 cặp
validation chia theo `document_id`. Trên Windows dùng 0 DataLoader worker và
cache tensor sau lần đọc đầu; nội dung ảnh cắt/nhãn/phép biến đổi giữ nguyên.
Validation của **bộ chọn cặp riêng lẻ** sau epoch 12 là 98/107 (91,59%). Đây
không phải độ đúng của nhánh Bold đầy đủ. Thông số và hash chi tiết ở
`artifacts/models/bold_pair_resnet18.metadata.json`; log ở
`outputs/bold-pair-rnd/train.log`.

## Đánh giá training_set

Evaluator lấy từ
[`T-Sunm/olp-ai-ptit-2026-preliminary-round` commit `2bc3653`](https://raw.githubusercontent.com/T-Sunm/olp-ai-ptit-2026-preliminary-round/2bc365327e92152219bf9bc3c4fd6797a150c4c7/DocViVQA/scripts/evaluate_predictions.py),
lưu local tại `artifacts/reference/upstream_evaluate_predictions.py`, SHA-256
`89d8b4a6508958fbcb20cdafc845cd7d2382a8f6f7c6bd8233b8969f001d611a`.
Không dùng `scripts/evaluate_predictions.py` của repo để báo ANLS/Evidence-F1
vì script đó chỉ tính answer accuracy.

| Nhóm | Câu | Đúng nguyên văn | ANLS | Evidence-F1 | Điểm /100 |
|---|---:|---:|---:|---:|---:|
| Argmax | 1.898 | 1.796 | 94,7768% | 94,4152% | 94,7225 |
| Argmin | 1.874 | 1.751 | 93,6100% | 93,0630% | 93,5279 |
| Sáu nhóm còn lại | 7.228 | 7.228 | 100% | 100% | 100 |
| **Toàn bộ** | **11.000** | **10.775** | **98,0101%** | **97,8545%** | **97,9868** |

Cả 11.000 câu đều có đáp án. Evaluator ghi 236 câu chưa đạt điểm tối đa:
225 sai đáp án (102 Argmax, 123 Argmin) và 11 đúng đáp án nhưng Evidence-F1
bằng 0 (4 Argmax, 7 Argmin). Kết quả training này khớp các số đã ghi trong
README; training đã được dùng để phân tích lỗi nên không đại diện cho test độc lập.

Output local ở `outputs/pipeline-rnd/baseline-new-checkpoint/` gồm predictions,
ZIP và `run_<split>.json` cho từng split, cùng `official_failures.jsonl` cho
training. Tại thời điểm ghi mốc baseline chưa nộp ZIP; sau đó người dùng xác nhận
đã nộp ZIP staging chứa cùng predictions và báo raw score 97,683267857/100.
Xem [báo cáo vòng private](2026-09-28-private-round-readiness.md).

## Public và private test

Pipeline tạo 1.000/1.000 câu public và 2.000/2.000 câu private. Bộ chọn ResNet
dự phòng được gọi 1 lần ở public, 0 lần ở private, 0 lần ở training. Vì vậy
checkpoint train lại **không tác động** đến dự đoán training/private của lần chạy
này; nó có thể ảnh hưởng một câu public. Không có nhãn test để tính điểm.

## Chẩn đoán ban đầu của Argmin/Argmax

Join 225 lỗi đáp án hiện tại với CSV chẩn đoán baseline lưu trong Git ở commit
`861409e`: cả 225 đáp án nhãn đều có ứng viên trong bảng; 140 ở hạng số 2,
48 ở hạng 3, 18 ở hạng 4 và phần còn lại ở các hạng khác (4 ở hạng 1).
So với baseline cũ, quy tắc hiện tại sửa đúng 180 đáp án và làm sai mới 2.

Hai ca làm sai mới `B-train-00268-q10` và `B-train-00355-q01` đã được đối chiếu
với ảnh, OCR, annotation và label. Với cách đọc tất cả hàng số trong cột được
hỏi, ô số của đáp án nhãn (lần lượt `5.831` và `3.777`) không phải cực đại
toàn cục. Ô tên của đáp án phủ nhiều hàng vật lý. Ở 11 ca chỉ sai evidence,
pipeline chọn đúng text đáp án nhưng lấy bbox của một hàng trùng tên khác.
Các quan sát này đòi hỏi kiểm tra phạm vi hàng hợp lệ và quy ước gán evidence
của dataset trước khi sửa luật chọn cực trị; chưa đủ để kết luận nhãn sai.

### Đối chiếu toàn bộ 236 lỗi còn lại

`scripts/analyze_argextreme_failures.py` nối predictions mới, labels, cell
annotations và CSV thứ hạng ứng viên lịch sử theo `question_id`/`block_id`.
Kết quả ở `outputs/pipeline-rnd/argextreme-diagnostics/` (ngoài Git). Toàn bộ
bbox dự đoán trong nhóm lỗi đều khớp chính xác một ô annotation; chưa thấy lỗi
định dạng tọa độ ở nhóm này.

- 221/225 câu sai đáp án có giá trị ở ô evidence của nhãn **không đứng hạng 1**
  khi xếp toàn bộ giá trị ứng viên mà solver cũ dựng lại: hạng 2 có 140 câu,
  hạng 3 có 48 câu, hạng 4 có 18 câu, hạng 5–9 có 15 câu. Đây là thứ hạng
  của bộ phân tích lịch sử, chưa phải xác nhận rằng mọi hàng trong bộ đó đều
  hợp lệ theo ý nghĩa câu hỏi.
- 83/225 câu sai đáp án có cùng text với ô tên nhãn ở hơn một ô cùng cột/bảng.
  Còn 142 câu không thuộc nhóm tên trùng này, nên quy tắc khử trùng tên không
  thể tự giải hết lỗi.
- Cả 11 câu chỉ sai evidence đều có tên đáp án lặp trong bảng. Pipeline trả
  đúng text nhưng lấy ô tên và cả hàng evidence ở vị trí khác với nhãn; 11/11
  evidence có hàng annotation khác. Ví dụ `B-train-00161-q06`: nhãn ở hàng 10,
  dự đoán ở hàng 5.
- Bốn câu sai đáp án còn lại có giá trị nhãn ở hạng 1 của bộ ứng viên lịch sử;
  cả bốn đều có ít nhất một ứng viên hòa giá trị. Có trường hợp OCR gộp thêm
  chữ `Đã đối chiếu` vào tên. Cần khảo sát riêng tie-break và tách text OCR.

Các ca hạng sâu cho thấy không thể mặc định câu hỏi luôn trỏ tới cực trị số
trên **tất cả** hàng mà bộ dựng bảng hiện đọc được. Chẳng hạn
`B-train-00109-q02` hỏi `Lượt khám nhỏ nhất`, ô nhãn `Sản | 316` ở hạng 8
trong khi bảng ứng viên còn `Mắt | 72`; `B-train-00261-q03` hỏi
`Giá trị hợp đồng lớn nhất`, ô nhãn `Đồng Nai | 8.760` ở hạng 9 trong khi
ứng viên có `Trường liên cấp | 28.030`. Có thể là phạm vi hàng, cấu trúc bảng,
hoặc quy trình tạo nhãn; cần đối chiếu ảnh và provenance trước khi quyết định
luật sửa. Không dùng nhãn để chọn hàng tại inference.

Đã mở ảnh gốc của hai ví dụ này: các số vừa nêu đều đọc được ngay trong cột
được hỏi của cùng `Bảng 1`. Riêng câu hỏi không ghi điều kiện lọc hàng bổ sung.
Điều đó củng cố việc cần kiểm tra tính nhất quán của nhãn/qui trình tạo câu hỏi,
nhưng chưa cho biết tỷ lệ bất nhất trên toàn tập hay cách xử lý tốt nhất trên test.

Lệnh tái tạo chẩn đoán:

```powershell
.venv\Scripts\python.exe scripts\analyze_argextreme_failures.py
```

## Tái chạy

```powershell
$env:TORCH_HOME='D:\Projects\docvivqa\artifacts\torch-cache'
.venv\Scripts\python.exe scripts\train_bold_pair.py --num-workers 0 --batch-size 16
.venv\Scripts\python.exe scripts\run_pipeline.py --split training_set --out outputs\pipeline-rnd\baseline-new-checkpoint
.venv\Scripts\python.exe artifacts\reference\upstream_evaluate_predictions.py outputs\pipeline-rnd\baseline-new-checkpoint\predictions_training_set.jsonl --labels data\training_set\labels.jsonl
```

Train lại có thể cho checkpoint khác; so sánh cải tiến cần giữ cố định
checkpoint SHA-256 và cùng tập đánh giá.
