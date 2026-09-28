# Baseline DocViVQA

## Nguồn và phiên bản

- [Repository upstream](https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round), thư mục `DocViVQA/`.
- Commit nguồn: `2aa3ac75343abe87a4a487e964c7cae47e568e6a`.
- [Code baseline của dự án](https://github.com/AIVIETNAM-AIO-LeWann/docvivqa/tree/baseline).
- Code nằm trên branch `baseline`; phần dọn repository chỉ thay đổi tổ chức tài liệu và output notebook, không thay đổi logic baseline. Hình và CSV tham khảo upstream không còn được theo dõi trên GitHub; có thể xem lại ở repo nguồn hoặc commit nhập ban đầu `2f9b38d`.
- Chưa tìm thấy LICENSE trong snapshot upstream; chưa gán giấy phép mới cho code nhập từ nguồn này.

## Phiên bản làm việc hiện tại

`main` đã tích hợp Bold, evidence và quy tắc hàng đầu cho Argmin/Argmax.
Bản trước chỉ sửa Bold + evidence đạt private raw **95,84** (bài 28084, 27/09/2026,
kết quả người dùng cung cấp). Candidate trên `codex/pipeline-rnd` với Argmin/Argmax
và checkpoint Bold train lại được người dùng báo private raw **97,683267857**;
biến thể tiếp theo loại hậu tố OCR `Đã đối chiếu` đạt **98,2605** (28/09/2026,
2.000 câu). Training hồi cứu của candidate đầu đạt 97,9868 điểm tổng hợp,
có 2 đáp án Argmax bị làm sai mới. Xem README để biết giới hạn.
Dùng main làm điểm xuất phát; branch baseline giữ bản gốc. Pipeline main dựa trên
upstream `2bc3653`; commit `2aa3ac7` ở trên mô tả bản baseline lưu trữ.

Mở `notebooks/submission_pipeline.ipynb` trên main, chuẩn bị `data/<split>/` và checkpoint
`artifacts/models/bold_pair_resnet18.pt`, chọn SPLIT rồi chạy từ đầu đến cuối.
Xem [README](../README.md) để biết kết quả và các vấn đề Argmin/Argmax còn lại.

## Chạy baseline

1. Chuyển sang branch `baseline`.
2. Chuẩn bị dataset theo [hướng dẫn dữ liệu](data.md).
3. Chuẩn bị môi trường Python với các thư viện dùng trong notebook: PyTorch, torchvision, NumPy, OpenCV, Pillow và Jupyter/ipykernel. Chưa chốt phiên bản thư viện hoặc cấu hình CPU/GPU.
4. Mở `notebooks/submission_pipeline.ipynb` và đặt working directory của kernel là `notebooks/`. Kiểm tra `ROOT` trỏ về gốc repo; `SPLIT` mặc định là `training_set`.
5. Ghi checkpoint sử dụng, cấu hình và kết quả vào [nhật ký thực nghiệm](experiments/experiment-template.md).

### Vai trò notebook

| File trong `notebooks/` | Mục đích |
|---|---|
| `submission_pipeline.ipynb` | Pipeline chính, tạo answer và evidence |
| `explore_dataset.ipynb` | Khám phá dataset |
| `train_bold_pair_local.ipynb` | Huấn luyện bộ chọn dòng đậm tại máy |
| `train_bold_pair_colab.ipynb` | Phiên bản huấn luyện cho Colab |
| `baseline.ipynb` | Bản tham khảo upstream, không phải pipeline chính |

Checkpoint dự kiến: `artifacts/models/bold_pair_resnet18.pt`. Khi chưa có checkpoint, pipeline vẫn thử luật thị giác nhưng không sử dụng được bộ chọn cặp dòng ResNet18 dự phòng.

## Đánh giá

`scripts/evaluate_predictions.py` chỉ tính coverage và accuracy đối chiếu answer; chưa tính ANLS, Evidence-F1 hoặc điểm tổng hợp của đề. Cần xác minh evaluator, chia tập theo document và kiểm tra dữ liệu huấn luyện của checkpoint trước khi đánh giá. Xem [quy ước metric](metrics.md).

## Kết quả tutorial — chỉ để tham khảo

Nguồn: `[Reading]-OlympicAI2026-Problem1.pdf`, trang 28. Đây là kết quả tác giả báo cáo trên **training**, không phải validation độc lập hay kết quả của nhóm.

| Loại | ANLS (%) | Evidence-F1 (%) | Tổng hợp (%) |
|---|---:|---:|---:|
| Argmax | 90.02 | 77.52 | 88.14 |
| Argmin | 89.00 | 76.49 | 87.12 |
| Visual Bold Lookup | 96.90 | 74.82 | 93.59 |
| Toàn bộ training | 96.25 | 90.89 | 95.45 |

## Kết quả tự tái hiện

Đã tái hiện baseline gốc với checkpoint ResNet18 trên 11.000 câu training và phân tích lỗi. Bản sửa Bold đạt 535/535 câu Bold; bản sửa evidence khắc phục thêm 67 ca thiếu ô ngữ cảnh, không giảm Evidence-F1 trên tập đã kiểm tra và giữ nguyên mọi đáp án so với bản Bold. Đây là đánh giá hồi cứu, không phải validation độc lập. Xem [kết quả hiện tại](../README.md). Evaluator upstream `2bc3653` đã được dùng cho các kết quả này; script đánh giá cũ trong repo vẫn chỉ tính coverage và accuracy.
