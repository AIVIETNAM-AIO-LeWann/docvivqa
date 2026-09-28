# EXP-RND-002 — loại hàng có ghi chú OCR trong ô tên

- Ngày: 28/09/2026; nhánh `codex/pipeline-rnd`.
- Mốc: [EXP-RND-001](2026-09-28-rnd-baseline.md), cùng dataset và checkpoint
  `06f850b893f97e5469dc320ab4455ac5d4db131b492ea331f32b7b88bc30db60`.
- Giả thuyết: OCR có thể nối `Đã đối chiếu` vào cuối text của ô tên hàng. Khi
  còn tên khác hợp lệ, hàng bị nối ghi chú không nên tranh cực trị.
- Thay đổi duy nhất: trong `solve_argextreme`, bỏ ứng viên có text ô tên kết
  thúc bằng `Đã đối chiếu` nếu còn ứng viên khác. Giữ quy tắc hàng vật lý đầu,
  tie-break và các solver khác. Biến thể được sinh từ notebook gốc bằng
  `scripts/make_argextreme_variant.py` vào `outputs/pipeline-rnd/variants/`
  (ngoài Git); notebook gốc chưa sửa.

Sau khi xác nhận điểm private, cùng biến thể notebook này được lưu trong Git tại
`notebooks/submission_pipeline_no_suffix.ipynb` và trở thành pipeline mặc định
trên `main`. Notebook gốc vẫn giữ để đối chiếu.

## Sàng lọc trước full run

`scripts/experiment_argextreme_rules.py` dùng CSV ứng viên lịch sử ở commit
`861409e`. Cách bỏ hậu tố sửa 47 đáp án, không làm sai mới khi so với solver
**cũ** trong CSV. Các quy tắc bỏ toàn bộ tên trùng, giữ nửa đầu bảng hoặc bỏ
phần cuối bảng đều gây nhiều hồi quy, nên không dùng. Đây chỉ là phép sàng lọc
vì CSV được tạo từ solver cũ.

## Full training với evaluator upstream

| Chỉ số | Mốc | Biến thể | Chênh lệch |
|---|---:|---:|---:|
| ANLS | 98,010131% | 98,487972% | +0,477841 điểm |
| Evidence-F1 | 97,854545% | 98,327273% | +0,472727 điểm |
| Tổng hợp /100 | 97,986793 | **98,463867** | **+0,477074** |
| Câu chưa đạt điểm tối đa | 236 | 184 | −52 |

`scripts/compare_pipeline_runs.py` đối chiếu từng ID: 53/11.000 dự đoán đổi
answer và evidence trên 45 tài liệu; 53 câu tăng điểm, 0 câu giảm. 52 câu từ 0 lên 1 điểm, một
câu (`B-train-00999-q07`) từ 0 lên 0,478125: sau khi bỏ hàng OCR có ghi chú,
ứng viên còn lại vẫn khác nhãn `Khu vực đô thị`. Điều này phù hợp với vấn đề
nhãn cực trị chưa nhất quán ở một số bảng; không xem 53/0 là bảo đảm cho private.
Sáu kiểu câu hỏi ngoài Argmin/Argmax vẫn đạt 100% trong lần chạy này.

Output training ở `outputs/pipeline-rnd/argextreme-no-suffix/`, gồm predictions,
ZIP, failures của evaluator và `changes_training_set.jsonl`. Chạy lại bằng:

```powershell
python scripts/make_argextreme_variant.py
python scripts/run_pipeline.py --split training_set --notebook outputs/pipeline-rnd/variants/argextreme_no_suffix.ipynb --out outputs/pipeline-rnd/argextreme-no-suffix
python artifacts/reference/upstream_evaluate_predictions.py outputs/pipeline-rnd/argextreme-no-suffix/predictions_training_set.jsonl --labels data/training_set/labels.jsonl
```

## Private: chỉ đo thay đổi, chưa có nhãn

Biến thể tạo đủ 2.000 dự đoán và ZIP qua `scripts/validate_submission.py`.
So với candidate đạt raw 97,683267857 trước đó, chỉ **12 đáp án và evidence**
đổi trên 12 tài liệu khác nhau; cả 12 đáp án cũ đều có hậu tố `Đã đối chiếu`.
Người dùng đã nộp ZIP staging của biến thể và báo điểm private cho 2.000 câu:

| Chỉ số | Candidate trước | Biến thể | Chênh lệch |
|---|---:|---:|---:|
| Answer score | 97,706785714 | 98,28 | +0,573214286 |
| Evidence score | 97,55 | 98,15 | +0,60 |
| Raw score /100 | 97,683267857 | **98,2605** | **+0,577232143** |

`0,85 × 98,28 + 0,15 × 98,15 = 98,2605`, khớp công thức. Mức tăng này là
kết quả private do người dùng cung cấp, không phải điểm tính từ nhãn local.

Sau thay đổi, training còn 184 câu chưa đạt tối đa: 173 sai đáp án và 11 chỉ
sai evidence, đều ở Argmin/Argmax. Đối chiếu bảng ứng viên lịch sử, 172/173
đáp án nhãn của nhóm sai còn lại nằm dưới hạng số 1; câu còn lại là hòa số.
Không còn đáp án dự đoán sai chứa hậu tố `Đã đối chiếu`. Vì vậy, phép thử tiếp
theo cần giả thuyết mới về phạm vi hàng/tie-break hoặc cách tạo nhãn và phải
đo hồi quy trên toàn tập, không thêm bộ lọc tên theo cảm tính.

### Sàng lọc giả thuyết số cực đoan

Đã thử loại số nằm ngoài median ± `k × 1,4826 × MAD` trên bảng ứng viên lịch
sử, với `k = 2, 3, 4`. So với solver cũ, số câu sửa đúng/làm sai mới lần lượt
là **46/693**, **19/287**, **9/123**. Đây là phép sàng lọc, không phải full run;
mọi cấu hình đều lùi rất xa nên không đưa vào pipeline và không tạo ZIP private.

Bản staging độc lập ở `outputs/final-staging/TACVU2-no-suffix/` có checkpoint,
`generate_result.ipynb`, `private_submission.zip` và manifest. Đã chạy lại
notebook staging: predictions SHA-256
`ca6ba7361920eff9308ef35d9419bc702b11dcf3b61a703c19a94ba66c41f7c0`
và ZIP SHA-256
`418fa3e393b08a499410d68c5bb6cd942f9365eb894c9d1a775ffd3d340a2456`
đúng manifest; 2.000/2.000 ID, đúng schema. Đây là **bản có raw score private
cao nhất đã được ghi nhận trong repo**. Mã lượt nộp chưa được cung cấp.

Trước khi nộp, vẫn cần kiểm tra điều kiện pretrained/checkpoint trong môi trường
thi như [báo cáo vòng private](2026-09-28-private-round-readiness.md) đã ghi.
