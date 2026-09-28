# TACVU2 — kiểm tra điều kiện vòng private

Nguồn quy định: đặc tả TACVU2 do người dùng cung cấp trong cuộc trò chuyện ngày
28/09/2026 và văn bản đính kèm. Vòng hiện tại chỉ đánh giá `private_test`.
Mật khẩu ZIP không được ghi vào repo, log hoặc notebook.

## Những điều kiện ảnh hưởng trực tiếp đến pipeline

- File nộp là ZIP có `predictions.jsonl`; mỗi dòng có đúng ba trường
  `question_id`, `answer` không rỗng và `evidence` chỉ gồm `page`, `bbox`.
  Mỗi ID trong `private_test/questions.jsonl` phải xuất hiện đúng một lần.
- Điểm TACVU2 là trung bình `0,85 × ANLS + 0,15 × Evidence-F1`, nhân 100.
  Evidence khớp khi cùng trang và IoU ≥ 0,5. Scoreboard còn chuẩn hóa theo
  Min/Max, nên điểm training không phải điểm hiện trên bảng xếp hạng.
- Chỉ có 10 lượt nộp private tính chung cho hai tác vụ. Private không có nhãn
  local; không thể xác định phiên bản nào có điểm private cao nhất bằng cách
  chấm offline.
- Chỉ các kiến trúc/trọng số pretrained trong `/cache_models` được phép dùng
  ở môi trường thi; `resnet18` có trong danh sách cho phép. Môi trường thi không
  có Internet, có H100 MIG 10 GB. Notebook cuối cùng phải tự sinh lại đúng
  predictions private và được đặt cùng checkpoint/ZIP tại
  `/home/user/FINAL/TACVU2`.
- Không sửa thủ công dữ liệu đầu vào hoặc kết quả đầu ra. Script kiểm tra định
  dạng chỉ đọc ZIP và câu hỏi, không thay predictions.

## Đã xác minh trên máy này

Nguồn local là `private_test.zip` trong bộ dữ liệu người dùng đã tải. Chi tiết
đường dẫn trên máy nằm trong `data/README.local.md` (ngoài Git).
467/467 tệp sau giải mã ZIP **giống byte** với `data/private_test/`; trước đó
thư mục workspace cũng được so byte với thư mục nguồn. Không cần tải lại từ
Google Drive; liên kết Drive không mở được qua công cụ duyệt web ở phiên này.

Pipeline hiện tại đã sinh `outputs/pipeline-rnd/baseline-new-checkpoint/
submission_private_test.zip`: đủ 2.000/2.000 ID, đúng schema/ZIP theo
`scripts/validate_submission.py`. Không có nhãn private để tính ANLS/F1 local.

Đã dựng bản staging đầu tiên ở `outputs/final-staging/TACVU2/` bằng
`scripts/build_final_tacvu2.py` với tham số source/notebook của candidate cũ,
gồm `best_model.pt`, `private_submission.zip`,
`generate_result.ipynb` và `candidate_manifest.json`. Notebook chứa quy trình
train Bold tùy chọn và toàn bộ suy luận private, mặc định chỉ inference từ
checkpoint local. Đã chạy lại **chính notebook staging** từ thư mục staging:
2.000/2.000 câu, prediction SHA-256
`ad05f94ac4d115e1730f3468fbf7992ae7c4dbeca630c7b0fbaddac42b524256`
giống baseline. ZIP được tạo xác định, hash sau khi notebook chạy đúng manifest,
và validator chấp nhận cấu trúc. Đây là bản local tương ứng với nội dung cần
đưa vào `/home/user/FINAL/TACVU2` sau khi kiểm tra điều kiện môi trường thi.

## Điểm private do người dùng cung cấp

Ngày 28/09/2026, người dùng xác nhận đã nộp đúng ZIP staging
`outputs/final-staging/TACVU2/private_submission.zip` và nhận kết quả:

| Chỉ số | Giá trị /100 |
|---|---:|
| Answer score (ANLS) | 97,70678571428572 |
| Evidence score | 97,55 |
| Raw score | **97,68326785714285** |
| Số câu | 2.000 |

`0,85 × 97,70678571428572 + 0,15 × 97,55 = 97,68326785714285`, khớp
chính xác công thức TACVU2. So với bản Bold + evidence được báo raw 95,84,
candidate này cao hơn **1,843267857** điểm raw. Đây là bản có điểm private cao
nhất **đã được ghi nhận trong repo**, không chứng minh từng thay đổi riêng lẻ là
nguyên nhân của toàn bộ mức tăng. Chưa có mã lượt nộp hoặc bản xuất kết quả từ
scoreboard; nguồn số liệu là báo cáo trực tiếp của người dùng. Hash ZIP staging
và chi tiết score được lưu trong `candidate_manifest.json` (ngoài Git).

Khoảng hụt so với 100 điểm raw là 2,316732143: thành phần answer đóng góp
1,949232143 điểm, evidence đóng góp 0,3675 điểm. Vì thế lần R&D kế tiếp ưu
tiên sửa đáp án sai trên training theo document, đo riêng hồi quy evidence,
và chỉ dùng lượt nộp private khi một thay đổi đã qua đánh giá độc lập.

Đã có một [biến thể R&D tiếp theo](2026-09-28-argextreme-no-suffix.md) sửa
53 câu training, không gây hồi quy trong full run và làm đổi 12 dự đoán private.
Người dùng báo ZIP biến thể ở `outputs/final-staging/TACVU2-no-suffix/` đạt
**98,2605 raw** (answer 98,28; evidence 98,15), cao hơn ZIP trước
**0,577232143 điểm**. Đây là candidate tốt nhất đã chấm. ZIP 97,683267857
vẫn được giữ nguyên ở `outputs/final-staging/TACVU2/` để đối chiếu.

Ở lần chạy private hiện tại, ResNet18 fallback được gọi 0 lần. Code inference
khởi tạo `resnet18(weights=None)` rồi chỉ nạp checkpoint local; không cần tải
pretrained khi suy luận. Checkpoint local đã được train bằng torchvision
`ResNet18_Weights.DEFAULT` trên máy cá nhân. Nếu tái train trong môi trường thi,
notebook train hiện tại cần đổi cách nạp trọng số sang file được phép ở
`/cache_models` và chạy thử offline; notebook staging đã thay nguồn nạp này
nhưng **chưa xác minh cấu trúc file cache** ở máy thi. Cũng chưa xác minh rằng
checkpoint train trên máy cá nhân đáp ứng cách BTC diễn giải điều kiện
"trọng số nằm trong `/cache_models`"; cần kiểm tra trước khi dùng làm bản nộp
cuối cùng. Inference đã chạy local không cần tải trọng số từ Internet.
File pretrained ResNet18 mà torchvision đã dùng trên máy này có SHA-256
`f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec`;
hash này có thể đối chiếu với file ResNet18 trong `/cache_models` nếu cần xác
minh nguồn trọng số.

Trước khi nhận được quy định về thời điểm mở khóa, repo đã được cung cấp thư
mục `private_test` local và pipeline đã chạy trên đó một lần. Lần chạy chỉ tạo
predictions tự động; không có nhãn và không sửa dữ liệu. Thời điểm BTC mở khóa
so với lần chạy này không thể xác minh từ repo. Những lần chạy tiếp theo cần
tuân theo trạng thái vòng thi do người dùng xác nhận.

## Hướng tiếp theo

1. Giữ nguyên candidate private và hash làm mốc; tiếp tục phân tích/trial trên
   training theo document, tránh dùng private để chỉnh quy tắc vì không có
   nhãn và lượt nộp bị giới hạn.
2. Chỉ nộp một candidate sau khi đã kiểm tra ZIP, khả năng tái chạy offline,
   các thay đổi answer/evidence so với candidate trước và rủi ro hồi quy.
3. Với candidate đã có điểm, giữ ZIP/checkpoint/notebook cố định. Ghi thêm mã
   lượt nộp nếu có; chỉ thay bản staging khi một candidate khác có score raw
   cao hơn và đã qua kiểm tra điều kiện môi trường thi.

Kiểm tra candidate tốt nhất hiện tại (sau khi đã tạo notebook biến thể và chạy
pipeline cho private như [EXP-RND-002](2026-09-28-argextreme-no-suffix.md)):

```powershell
python scripts/build_final_tacvu2.py
python scripts/validate_submission.py outputs/final-staging/TACVU2-no-suffix/private_submission.zip --questions data/private_test/questions.jsonl
```
