# Pipeline R&D: audit ban đầu

Ngày 28/09/2026. Nhánh `codex/pipeline-rnd`, xuất phát từ `main` tại
`eca7eac6ee11919e9173806c50cf208c4d2bfc2e`.

## Mục tiêu và giới hạn bằng chứng

Mục tiêu là tăng điểm ANLS và Evidence-F1 của pipeline nộp bài, ưu tiên thay đổi
có thể giải thích, đo riêng và tái hiện. Đây là audit ban đầu, **chưa phải kết
quả thực nghiệm mới** tại thời điểm viết: dữ liệu được sao chép vào workspace
sau audit; checkpoint cũ và output cũ không có trong Git. Sau đó đã train
checkpoint mới, chạy đủ ba split và đo training bằng evaluator upstream;
xem [`EXP-RND-001`](2026-09-28-rnd-baseline.md). README ghi bản Bold + evidence
đạt private raw 95,84; bản Argmin/Argmax hiện tại đạt 97,9868/100 trên training.
Sau audit, người dùng báo candidate private trên nhánh này đạt 97,683267857/100;
biến thể [loại hậu tố OCR](2026-09-28-argextreme-no-suffix.md) sau đó đạt
98,2605/100. Xem [báo cáo vòng private](2026-09-28-private-round-readiness.md).
Training đã được dùng để phân tích lỗi, nên điểm training
không ước lượng tin cậy hiệu quả trên tài liệu chưa thấy.

## Luồng hiện tại và nơi có thể mất điểm

1. `parse_intent`: regex khớp nguyên mẫu, sau đó heuristic để xác định kiểu và
   trích trường. Nếu thiếu trường, câu được trả `không xác định`.
2. `table_blocks`, `group_rows`, `header_block`, `cell_under`: chia bảng theo tiêu
   đề, gom hàng bằng `y1` làm tròn, khớp tên cột nguyên văn, rồi gán ô theo tâm
   header. `cell_under` có nhánh chọn ô gần nhất khi không có ô phủ tâm header.
3. Solver cho tám kiểu câu hỏi: lookup/count/sum/compare/cross-page sum,
   Argmin/Argmax, Visual Bold Lookup. Argmin/Argmax dựng lại hàng bị ô gộp phủ;
   chỉ ưu tiên hàng vật lý đầu của mỗi ID ô tên, rồi chọn cực trị. Nếu không còn
   ứng viên, solver quay về toàn bộ ứng viên cũ. Đồng hạng dùng thứ tự xuất hiện.
4. `build_evidence` chuyển OCR block thành bbox và loại trùng theo `block_id`.
   Với Argmin/Argmax, ô nhận diện hàng được chọn qua tiền tố đủ phân biệt các
   hàng có cùng text trước cột số.
5. Visual Bold Lookup thử median nét chữ, bỏ phiếu từng ô, rồi ResNet18 khi
   chưa quyết định được. Mã hiện tại yêu cầu checkpoint tồn tại ngay từ cell cấu
   hình, dù tài liệu baseline có câu nói checkpoint là tùy chọn.

Các mô tả trên là hành vi của mã, chưa khẳng định từng giả định là sai trên dữ
liệu. Cần đo số câu rơi ở mỗi bước và đối chiếu ảnh/OCR/nhãn trước khi sửa.

## Giả thuyết cần kiểm tra, theo thứ tự

| Nhóm | Giả thuyết từ audit | Phép kiểm tra phân biệt nguyên nhân |
|---|---|---|
| Argmin/Argmax | Ô gộp, hàng đầu thiếu số, phạm vi tiêu đề/tổng và đồng hạng có thể làm tập ứng viên sai. | Với từng câu sai hoặc thay đổi: ghi bảng ứng viên `(block_id tên, hàng vật lý, block_id số, giá trị)`, đánh dấu hàng bị loại và so ảnh/OCR/nhãn. Xem riêng hai lỗi mới `B-train-00268-q10`, `B-train-00355-q01`. |
| Evidence | Đáp án đúng nhưng thiếu/thừa ô nhận diện hoặc ô số. | Tách lỗi answer và evidence; ghi IoU, số bbox dự đoán/nhãn, kiểm tra ví dụ tên trùng và ô gộp. Thử thay đổi evidence độc lập với đáp án. |
| Truy xuất ô | Khớp nguyên văn header/giá trị và nhánh lấy ô gần nhất có thể bỏ sót hoặc chọn nhầm cột. | Thống kê thất bại theo `header_block`, `matching_rows`, `cell_under`; đối chiếu `cell_annotations` với OCR trên các ca sai. Chỉ thêm chuẩn hóa hoặc fallback cho nhóm lỗi đã xác nhận. |
| Số học | `parse_number` xem dấu chấm là phân cách hàng nghìn, dấu phẩy là thập phân; `format_number` tối đa hai chữ số thập phân. | Liệt kê định dạng số thực có trong nhãn/OCR, đối chiếu từng phép sum/compare/extreme trước khi đổi parser. |
| Bold | Kết quả 535/535 trên tập đã khảo sát có thể không giữ trên ảnh/bảng mới. | Giữ baseline, đo tỷ lệ quyết định ở từng tầng và lỗi trên tài liệu chưa dùng để chọn ngưỡng; không chỉnh ngưỡng theo chính 535 câu. |
| Parser | Mẫu câu khác template có thể rơi vào heuristic chưa trích đủ trường. | Log `route_source`, trường thiếu và tỷ lệ trả lời theo kiểu câu; kiểm tra nhãn của câu chưa giải được. |

## Quy trình đo trước khi thay thuật toán

1. Khôi phục đúng dataset, checkpoint, predictions và evaluator tham chiếu; ghi
   hash/phiên bản. Chạy pipeline `main` để xác nhận đầu ra và các số đang ghi.
   `scripts/evaluate_predictions.py` chỉ đo coverage/accuracy, không đủ để đo
   điểm của đề.
2. Tạo bảng lỗi theo `question_id`, `document_id`, kiểu câu, answer đúng/sai,
   ANLS, Evidence-F1, bước thất bại và bbox/ô liên quan. Không dùng nhãn khi
   suy luận. Dùng nhãn chỉ để phân tích và đánh giá.
3. Chia tập theo `document_id` khi thử thay đổi. Vì toàn bộ training đã được
   phân tích trước đây, gọi đây là tập phát triển, không coi là test độc lập.
   Không dùng điểm private để chỉnh từng quy tắc.
4. Mỗi giả thuyết cần một thay đổi đơn lẻ, so cùng tập câu với baseline đã đóng
   băng: điểm tổng hợp, ANLS, Evidence-F1, từng kiểu câu, số câu sửa đúng/làm sai
   mới và danh sách `question_id` thay đổi. Kiểm tra cả answer lẫn evidence.
5. Chỉ kết hợp các thay đổi sau khi thử riêng và kiểm tra hồi quy toàn pipeline.
   Giữ kết quả thô, cấu hình, commit và giới hạn của phép thử trong nhật ký.

## Liên hệ tài liệu nghiên cứu

- [PubTables-1M (CVPR 2022)](https://openaccess.thecvf.com/content/CVPR2022/html/Smock_PubTables-1M_Towards_Comprehensive_Table_Extraction_From_Unstructured_Documents_CVPR_2022_paper.html) bàn về cấu trúc bảng và chuẩn hóa ô bị chia quá mức. Đây là cơ sở để xem lại biểu diễn hàng/cột/ô gộp; chưa chứng minh một mô hình nhận dạng bảng mới sẽ cải thiện TACVU2.
- [TAT-DQA / MHST (ACM MM 2022)](https://arxiv.org/abs/2207.11871) và [Doc2SoarGraph (LREC-COLING 2024)](https://aclanthology.org/2024.lrec-main.456/) nghiên cứu suy luận rời rạc trên tài liệu có bảng, text và bố cục. Chúng gợi ý việc biểu diễn rõ quan hệ giữa ô, số và câu hỏi; metric/dataset của chúng khác ANLS + Evidence-F1 ở đây.

Đây mới là đối chiếu mục tiêu và abstract/metadata của paper, chưa phải đánh giá
đầy đủ phương pháp hay khả năng chuyển giao. LLM/VLM chỉ nên được định vị sau
khi biết phần lỗi còn lại nằm ở parser, OCR, cấu trúc bảng, thị giác hay suy luận.

## Nguồn và dấu vết đã tìm thấy trong repository

- README trỏ tới dataset
  `https://huggingface.co/datasets/lequangaio070206/tacvu2-docvivqa/tree/main`.
  Cell đầu của `notebooks/train_bold_pair_colab.ipynb` còn chứa một Google Drive
  file ID để tải `tacvu2.zip`. Đây là **hai nguồn được mã/tài liệu nhắc tới**;
  chưa xác nhận quyền truy cập hay phiên bản của hai link. Bản dữ liệu local
  được sao chép từ thư mục Downloads và kiểm tra riêng; xem `docs/data.md`.
- `notebooks/train_bold_pair_local.ipynb` và bản Colab có đủ mã tạo một
  checkpoint Bold mới từ training_set. Checkpoint đã dùng cho kết quả báo cáo
  không nằm trong Git, nên train lại không bảo đảm có cùng trọng số hoặc cùng
  predictions; thư viện cũng chưa được khóa phiên bản.
- Commit `861409e` còn giữ năm CSV chẩn đoán Argmin/Argmax và các CSV mẫu trong
  `artifacts/analysis/`. Chúng được nhập từ baseline upstream, **không phải
  phép chạy R&D mới**. `argextreme_oracle_ranked.csv` có 3.772 câu (1.898 Argmax,
  1.874 Argmin); solver cũ sai 403 câu, trong đó 315 câu có giá trị đáp án ở
  hạng 2. CSV ghi nhận ứng viên đáp án có mặt ở cả 3.772 câu; trong 315 ca
  hạng 2, 220 ca đánh dấu ô tên của hàng solver đã xuất hiện trước đó. Đây là
  tín hiệu để kiểm tra ô gộp/tên lặp, chưa chứng minh nguyên nhân cho mọi ca.
  Hai ID bị phiên bản hiện tại làm sai mới đều được baseline cũ trả đúng. CSV
  giúp lập giả thuyết và chọn ca kiểm tra mà không cần tải dataset,
  nhưng không thay thế ảnh/OCR/nhãn hay phép chạy pipeline hiện tại.
- Script lịch sử tại commit `837905e` gọi evaluator từ
  `outputs/baseline-full-error-analysis/source/evaluate_predictions.py` và đối
  chiếu hash checkpoint. Các tệp trong `outputs/` đó không có ở checkout/Git.
  Evaluator gốc được nhắc tới là upstream commit `2bc3653`, không phải
  `scripts/evaluate_predictions.py` hiện tại.

## Tình trạng sau khi dựng mốc mới

- Dataset hiện đã có ở `data/training_set/`, `public_test/`, `private_test/` và
  được kiểm tra cấu trúc/nội dung; xem `docs/data.md`.
- Checkpoint **cũ** không có nên không thể đối chiếu trọng số một-một, nhưng
  checkpoint mới và metadata/hash đã được lưu local. Giữ checkpoint này cố định
  trong các phép so R&D.
- Evaluator upstream commit `2bc3653` đã lấy về và chạy; kết quả training mới
  khớp số README. Predictions cũ vẫn không có trong Git, nên so sánh thay đổi
  sẽ lấy predictions mới ở `outputs/pipeline-rnd/baseline-new-checkpoint/` làm mốc.
