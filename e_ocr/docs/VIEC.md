# VIỆC — danh sách việc duy nhất của project `e_ocr`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc tài liệu cổng và engine; nhận kế hoạch các lát theo `GIAO-CODEX-e_ocr.md` | — | Xong 14/11/2026 | Thực hiện OCR-0 theo phiếu Anh giao; ước tính 2 giờ |
| OCR-0 | Khung SDK 2.0, cấu hình máy, kho tạm, schema chung và kiểm độc lập | OCR-6 | Xong 14/11/2026 | PR: **chờ lead mở**. Đã đạt tiêu chí riêng của OCR-0; kết quả DEMO chung và giới hạn xem bên dưới |
| 1 | Đóng gói độc lập theo cổng chung; thay hàm SDK riêng `ocr_*_luot` bằng lượt bền chung khi Core có | OCR-6, 13 | Đang làm 14/11/2026 | Có khung OCR-0; chuyển lõi ở OCR-1…OCR-4, không sửa `ma-nguon/` |
| 2 | Bổ sung dependency cho nguồn dự phòng mask_ocr | OCR-8 | Chờ làm |  |
| 3 | Màn hạn mức ABBYY / trạng thái máy (giao diện của engine) | OCR-8 | Chờ làm |  |
| 4 | Bài máy test ca 1, 3, 8 | OCR-11 | Chờ làm |  |
| 5 | Lát 9: ABBYY thật trên máy hiện tại bằng PDF DEMO (Anh đã cho phép mở kết nối tạm) | OCR-12 | Chờ làm | Không chép `in\ out\ jobs\ state\` |
| 6 | Ghép Core (K1–K6) → nghiệm thu tổng thể | — | Chờ Core |  |

## Cần Core (chuyển lead Core qua Anh)
- Theo SDK 2.0.0 và `GIAO-CODEX-THU-TU.md` §3: đưa cấu hình từ `san-sang` tới engine, kèm schema để Core dựng form. Tạm đọc JSON ngoài gói bằng `KTT_ENGINE_CAU_HINH`.
- Ngăn dữ liệu engine: ghi theo lô nguyên tử, CAS/`row_version`, ràng buộc duy nhất/lấy hoặc tạo. Tạm dùng `KTT_ENGINE_DU_LIEU`; `doc` và `ghi` là các thao tác riêng lẻ, không có giao dịch đọc–sửa nhiều lời gọi.
- Lượt bền chung #10 giữ/chốt/đọc (đợt 2): thay phần lưu lượt tạm ở OCR-4 khi Core có. Không dùng hàm `ocr_*_luot` cũ.
- Bí mật theo tên, nhật ký kỹ thuật và thẻ trạng thái chung để thay phần trạng thái/hạn mức ABBYY; đợt 1 không làm giao diện riêng hay cầu nối có khóa.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

## Bằng chứng OCR-0 — 14/11/2026

- Nhánh: `codex/e_ocr-ocr-0`; PR: **chờ lead mở**. Lead commit và mở PR.
- Thời gian thực tế: **14/11/2026, 22:18–22:38** (20 phút, khoảng **0,33 giờ**),
  so với **2 giờ ước tính** trong phiếu; giờ Việt Nam.
- Gói mới: `goi/e_ocr/`, bốn tệp mã Python; chỉ thư viện chuẩn + SDK 2.0.0.
  Không sửa mã cũ hoặc tài liệu SDK/Core. Hàm tạm của cả ba năng lực trả
  `LoiNghiepVu("CHUA_LAM", ...)`, không nộp kết quả giả.
- Schema `van_ban_tai_lieu` được tạo theo `LOAI-DU-LIEU-RIENG.md` §2.1 và
  chép nguyên tệp vào gói; test so SHA-256. Khi gộp với AI-0, lead chọn một
  bản chung và chép nguyên byte vào các gói trước khi chạy lại test so băm.
- Cấu hình máy và dữ liệu tạm đều ngoài gói, không chứa bí mật/nội dung tài
  liệu. Khóa thật bằng `msvcrt`/`fcntl`; test hai tiến trình `spawn` đồng thời,
  giữ khóa, hết hạn khóa, lỗi thay tệp, kho hỏng, khởi tạo lại và từ chối bytes.
- **Đã kiểm bằng Core giả (CoreGia)** trên Windows x64, Python 3.13.14.
  Chưa chạy Linux, Core thật hoặc nguồn OCR thật. Test không phụ thuộc Windows
  API ngoài nhánh khóa tệp chuẩn; dùng `spawn` trên cả hai nền tảng.
- SDK cài offline trong `.venv`, phiên bản `2.0.0`; băm wheel khớp
  `SHA256SUMS.txt`. `.venv` dùng `--system-site-packages` để dùng pytest có sẵn,
  không tải thêm thư viện; chưa phải bài cài máy sạch của OCR-6.

### Kết quả ba lệnh bắt buộc

Đầu ra thực tế lượt kiểm cuối; đã đặt `PYTHONDONTWRITEBYTECODE=1` và
`PYTHONUTF8=1`, không phát sinh bytecode trong gói:

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
Phiếu chưa có ví dụ chay_thu_demo.
Mã thoát: 1; chưa có ví dụ (0/0), chưa đạt kiểm DEMO chung.

> .venv\Scripts\python -m pytest e_ocr/tests -q
........................................................................ [ 86%]
...........                                                              [100%]
83 passed in 5.88s
Mã thoát: 0; 0 skipped.

> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát: 0.
```

Kiểm bổ sung: `tu_khai_bao: e_ocr 3`; kiểm schema draft 2020-12 và các mẫu
DEMO hợp lệ bằng công cụ `jsonschema` có sẵn trong môi trường (không là
dependency của engine). So băm nguồn gói theo `NGUON.md`; `git diff --check`
không báo lỗi. Mã schema chung:
`f3756741eea1e5c9c9451b8a8df8a5416817f04adffe4bf1b44c24b19c3e7f93`.

### Quyết định tạm và phần còn lại

- `chay_thu_demo` rỗng tới OCR-5. SDK 2.0.0 coi phiếu không có ví dụ là mã
  thoát 1; CLI chỉ chấp nhận ví dụ kết thúc `XONG`. Vì OCR-0 bắt buộc hàm tạm
  `CHUA_LAM`, **chưa đạt điều kiện DEMO chung AGENTS.md §5**. Tiêu chí riêng
  OCR-0 vẫn là `tu_khai_bao` không lỗi, pytest xanh, kiểm độc lập mã 0.
- Giới hạn lớp bọc tạm: cấu hình/giá trị kho 64 KiB, toàn kho 8 MiB; chuỗi mã
  ASCII tối đa 200 ký tự, độ sâu 16, vượt trần thì từ chối. Không CAS nhiều
  lời gọi; cần bổ sung giao dịch ở lát nghiệp vụ trước khi cộng hạn mức/giữ
  lượt có điều kiện. Mặc định ABBYY tắt, thời hạn cấu hình 900 giây.
- Mã cũ giữ nguyên để chuyển lõi ở lát sau. Vỏ `chay.py`, `lib/cong_ocr.py`
  cũ, shim và hàm SDK riêng không dùng trong gói mới; ghi nhận để chuyển
  `LUU-TRU/` sau, không xóa trong OCR-0.
- Không phát sinh câu hỏi mới cần Anh quyết định; giữ các mục chờ Anh trong
  phiếu giao (Q1/Q2/Q3 và các việc trước khi thử ABBYY thật).
