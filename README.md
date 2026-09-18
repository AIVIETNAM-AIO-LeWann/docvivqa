# DocViVQA — Hỏi đáp trên ảnh tài liệu tiếng Việt

Workspace nghiên cứu cải thiện baseline DocViVQA, tập trung vào **Visual Bold Lookup, Argmax, Argmin**, đồng thời khảo sát tích hợp **LLM/VLM**.

**Trạng thái:** đã nhập code baseline upstream ngay tại gốc repo; xem [hướng dẫn baseline](docs/baseline-setup.md). Chưa nhập dữ liệu, chạy mô hình hoặc có kết quả thực nghiệm của nhóm.

## Bắt đầu

1. Điền [outline tuần 1](docs/weekly/WEEK01-outline.md).
2. Mở [Paper Tracker](docs/papers/paper-tracker.csv) bằng bảng tính; dùng [mẫu ghi chú](docs/papers/reading-template.md) khi đọc từng bài.
3. Đặt dữ liệu tải từ nguồn của chương trình trong `data/training_set/` để chạy baseline; xem [quy ước dữ liệu](data/README.md).
4. Khi tái hiện baseline, ghi phiên bản và lệnh chạy vào [hồ sơ baseline](docs/baseline.md).
5. Lưu mỗi thực nghiệm riêng theo [mẫu nhật ký](docs/experiments/experiment-template.md).

## Cấu trúc

```text
docvivqa/
├── artifacts/           # Phân tích upstream và checkpoint tại máy
├── images/              # Hình và tài liệu minh họa upstream
├── scripts/             # Script đánh giá baseline
├── configs/             # Cấu hình và hồ sơ các lần chạy
├── data/
│   ├── training_set/    # Dữ liệu cho baseline (tải riêng)
│   ├── raw/             # Bản dữ liệu gốc lưu trữ nếu cần
│   ├── processed/       # Dữ liệu đã xử lý
│   └── splits/          # Danh sách document thuộc từng tập
├── docs/
│   ├── papers/          # Paper Tracker và ghi chú đọc
│   ├── weekly/          # Outline và kết quả theo tuần
│   └── experiments/     # Giả thuyết, thiết lập và phân tích thực nghiệm
├── notebooks/           # Pipeline baseline, train bold và khám phá dữ liệu
├── references/          # PDF đọc tại máy; không đưa vào Git
├── src/docvivqa/         # Code dùng lại trong dự án
└── outputs/             # Predictions, metrics, hình minh họa, log tại máy
```

## Môi trường Python

Chạy từ thư mục dự án:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Lệnh trên chỉ cài package khởi tạo; chưa cài các thư viện cần cho notebook baseline. Thêm thư viện cần thiết khi triển khai từng bước; chưa chọn model/provider. Ghi lại phiên bản môi trường cho các lần chạy.

## Nguyên tắc thực nghiệm

- Mốc so sánh là baseline tutorial, cần ghi rõ commit và cấu hình thực tế.
- Chia tập theo document, không tách các câu hỏi của cùng document qua nhiều tập.
- Nhãn answer/evidence/cell chỉ dùng cho huấn luyện, phát triển hoặc đánh giá đúng vai trò; không đưa nhãn vào đầu vào suy luận để chấm điểm.
- So sánh từng thay đổi trên cùng dữ liệu; lưu cả trường hợp sửa đúng và làm sai thêm.
- Theo đề: `Score = 0.85 × ANLS + 0.15 × Evidence-F1`. Dùng evaluator tham khảo và xác minh quy ước trong [metrics](docs/metrics.md).
- Không commit dữ liệu, PDF paper cá nhân, model weights, API key hoặc kết quả thô mới. Các tài liệu và kết quả đi kèm snapshot upstream được giữ lại để đối chiếu.
- Chưa chọn giấy phép cho code dự án. Khi sử dụng code/dữ liệu bên ngoài, kiểm tra và giữ thông tin nguồn, giấy phép tương ứng.

## Nguồn tham khảo

- [Repository tutorial](https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round)
- Tài liệu chương trình: `[Reading]-OlympicAI2026-Problem1.pdf`, `[Slide]-DocViVQA.pdf`, hướng dẫn Topic Team.

`docs/weekly/` phục vụ chuẩn bị và lưu bản làm việc tại máy. Cuối tuần cập nhật vào Working Files của nhóm; Paper Tracker của chương trình dùng Google Sheets. Leader cập nhật Google Form theo lịch của chương trình.
