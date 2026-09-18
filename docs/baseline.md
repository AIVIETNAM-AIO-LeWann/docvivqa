# Hồ sơ baseline

## Nguồn

- Repository: https://github.com/T-Sunm/olp-ai-ptit-2026-preliminary-round
- Phần cần xem: `DocViVQA/`.
- Commit upstream: `2aa3ac75343abe87a4a487e964c7cae47e568e6a`
- Vị trí code tại máy: [baselines/DocViVQA/](../baselines/DocViVQA/)
- Thay đổi so với upstream: không sửa nội dung; giữ nguyên toàn bộ file được Git theo dõi trong thư mục `DocViVQA/`. Xem [hướng dẫn nhập baseline](../baselines/README.md).
- Cấu hình/checkpoint, môi trường, evaluator và lệnh chạy: [Điền khi tái hiện]

## Kết quả tutorial — chỉ để tham khảo

Nguồn: `[Reading]-OlympicAI2026-Problem1.pdf`, trang 28. Đây là kết quả tác giả báo cáo trên **training**, không phải validation độc lập hay kết quả của nhóm.

| Loại | ANLS (%) | Evidence-F1 (%) | Tổng hợp (%) |
|---|---:|---:|---:|
| Argmax | 90.02 | 77.52 | 88.14 |
| Argmin | 89.00 | 76.49 | 87.12 |
| Visual Bold Lookup | 96.90 | 74.82 | 93.59 |
| Toàn bộ training | 96.25 | 90.89 | 95.45 |

## Kết quả tự tái hiện

Chưa chạy. Khi có kết quả, ghi dataset/split, số câu hỏi, cấu hình, evaluator, lệnh chạy và link tới experiment tương ứng. Không so sánh trực tiếp các điểm đo trên tập khác nhau.
