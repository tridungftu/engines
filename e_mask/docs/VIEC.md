# VIỆC — danh sách việc duy nhất của project `e_mask`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc yêu cầu chung/SDK 2.0, yêu cầu Mask và lập kế hoạch lát có giờ ước tính; trình Anh qua lead | MASK-P | Xong — 14/11/2026 (lập phiếu) | [GIAO-CODEX-e_mask.md](GIAO-CODEX-e_mask.md): 14 lát MASK-0…13, 52–62 giờ ước tính chưa đo; phần tệp có điều kiện, chưa triển khai; PR: **chờ lead mở** |
| 1 | Chuyển kho bí danh sang **ngăn của engine** theo cổng chung (thay `mask.py`/`kho_mask.py`/SQL 113, 117–120 trong Core) | MK-10, 19 | Chờ Core | Bàn cùng lead Core qua Anh |
| 2 | J8b: đối soát mất xác nhận | — | Chờ làm |  |
| 3 | Lát 4: màn duyệt danh sách chờ (Admin) — giao diện của engine | MK-15, 16 | Chờ làm |  |
| 4 | Lát 5: màn thử che/mở che DEMO | — | Chờ Anh | Duyệt `PHIEU-MASK-CHAY-THU-DEMO.md` |
| 5 | Lát 8: che/mở che Word/Excel (mẫu 5–8) | §1.3 | Chờ làm |  |
| 6 | Lát 6: 8 contract (Anh duyệt tên) → lát 7: bài 11 bước | — | Chờ làm |  |
| MASK-P | Lập phiếu giao Codex theo SDK 2.0; chỉ tài liệu, không tạo gói/không sửa nguồn | MK-1…6, 10…22 | Xong — 14/11/2026 | [Phiếu giao](GIAO-CODEX-e_mask.md): 14 lát, 52–62 giờ ước tính có điều kiện. Regex 14/14 khối đạt; 5 mục/bảng lát/tổng giờ khớp; UTF-8/NFC và kiểm khoảng trắng đạt, `git diff --check` mã 0. Ba lệnh kiểm gói AGENTS.md §5 không áp dụng theo ngoại lệ lát chỉ tài liệu; không chạy hoặc nhận là đã kiểm bằng CoreGia. Đề xuất `van_ban_da_che` ở cuối sổ chung mang nhãn **ĐỀ XUẤT MASK-P, chờ Anh**. Không commit/push; PR: **chờ lead mở** |

Các số “lát 1…8/J8b” ở các dòng lịch sử là mã kế hoạch cũ; kế hoạch giao SDK 2.0 dùng `MASK-0…MASK-13` trong phiếu mới. Hoàn tất MASK-P không có nghĩa đã code, kiểm bằng CoreGia hoặc nối Core thật. MASK-P ước tính 1 giờ; tổng giờ 52–62 là dự toán triển khai sau, cập nhật lại sau khảo sát tệp MASK-7.

## MASK-0 — 14/11/2026

- Xong khung MASK-0; PR: **chờ lead mở**. Hai năng lực văn bản trả `CHUA_LAM`, chưa kích hoạt vận hành. Cấu hình chỉ chấp nhận đối tượng rỗng, chờ whitelist tài nguyên detector; Linux dùng đường DEMO tường minh.
- Đã kiểm bằng Core giả (CoreGia): hai handler trả lỗi, không báo `XONG`; cổng DEMO nghiệp vụ **chưa đạt** do stub. `kho_tri_thuc_sdk.thu`: 0/2 ĐẠT, mã thoát 1; pytest: 9 passed, 0 skipped; kiểm độc lập: mã thoát 0.
- Mã cũ giữ nguyên; hiện vật không mang sang gói theo mục MASK-P để lead xem xét lưu trữ sau. Nhu cầu Core đã ghi bên dưới; MASK-0 không phát sinh yêu cầu mới.

## MASK-1 — 14/11/2026

- **Xong phạm vi lõi thuần**, chỉ DEMO; PR: **chờ lead mở**. Bắt đầu 23:53 ngày 14/11/2026, kết thúc 00:03:55 15/11/2026 (UTC+07), khoảng **0.18 giờ thực tế**, so với **3 giờ ước tính** trong phiếu. Lát qua nửa đêm; giữ ngày giao 14/11 theo handoff.
- Chép đúng năm tệp `nguon/privacy/{__init__,types,core,company_names,person_names}.py` vào gói. Giữ KnownText, chuẩn hóa/vị trí, tên dài ưu tiên, bảo vệ số, numeric_review; hỗ trợ NFC/NFD bằng bản dò có ánh xạ vị trí gốc. Đổi sang `[[...]]`, giữ mã Junsky, không cắt số thứ tự lớn. [NGUON.md](../goi/e_mask/NGUON.md) có đường nguồn, SHA byte trước/sau và SHA LF cho checkout Linux/Windows.
- Bản chép đã tách encrypt/decrypt bảng, xuất Word/TXT/ZIP và import cryptography/python-docx. Không thêm thư viện chạy ngoài SDK. Detector import khi gọi; thiếu thì từ chối, không trả kiểm giả. `suggest` chỉ gợi ý thủ công có trần 500 dòng, không dùng che tự động. Phần nguồn cũ giữ nguyên, để lead xét chuyển lưu trữ sau, không xóa/di chuyển.
- **Đã kiểm bằng Core giả (CoreGia)**: pytest **54 passed, 0 skipped**, mã 0; gồm 9 ca MASK-0 và 45 ca MASK-1. Kiểm độc lập **ĐẠT**, mã 0. Ca thuần kiểm NFC/NFD/khoảng trắng/vị trí, tên dài, giữ Junsky, số tự sinh lớn, mã số DEMO không nhầm tiền/ngày, giữ `1.000.000 VND` và `30/10/2026`, phát hiện mất/thêm/đổi số; import sạch chỉ với thư viện chuẩn không đọc tài nguyên/ghi tệp/chạy nguồn ngoài.
- Cổng vẫn giữ nguyên hai handler MASK-0, trả `LoiNghiepVu("CHUA_LAM", "Chức năng này chưa được hoàn tất.")`, không xuất văn bản hoặc cụm gốc. CLI SDK **0/2 ĐẠT, mã 1** do hai stub theo phiếu; **chưa đạt DEMO nghiệp vụ, chưa hoàn tất che/mở che, chưa kích hoạt vận hành**. numeric_review chưa thay hậu kiểm tiền/ngày độc lập ở MASK-2.
- Lệch nền checkout: lúc bắt đầu nhánh chưa chứa MASK-0. Đã khôi phục đúng 10 tệp `e_mask/` từ commit `c3e68148b5db837912a40ea39aa4539f53c3fca0` (đọc Git object vào worktree; giữ nguyên năm tệp mã/phiếu của MASK-0). Lệnh Git restore không ghi được index của worktree ngoài vùng cho phép nên dùng đọc object; không đổi index, không commit/push. Lead đồng bộ dependency trước khi mở PR để diff MASK-1 chỉ còn năm tệp lõi, test và tài liệu.
- Quyết định tạm: dùng họ tiền tố MASK đã có trong fixture cũ, chỉ cho helper DEMO; còn chờ lead xác nhận không trùng mã Junsky thật. Kho cấp mã chung/kiểm quyền thuộc MASK-3. Không có yêu cầu Core mới phát sinh; các mục Cần Core phía dưới giữ nguyên.

Ba lệnh bắt buộc đã chạy bằng `.venv/Scripts/python`, với `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chức năng này chưa được hoàn tất."
[LỖI] Mở che DEMO: "Chức năng này chưa được hoàn tất."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1 (0/2 ĐẠT, đúng giới hạn stub của MASK-1).

python -m pytest e_mask/tests -q
54 passed in 0.59s
Mã thoát: 0; 0 skipped.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát: 0.
```

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

### Bổ sung MASK-P — 14/11/2026

- Hợp đồng API v1/SDK 2.0 đã khóa; các yêu cầu cổng lịch sử phía trên phải đối chiếu lại theo [phiếu SDK 2.0](GIAO-CODEX-e_mask.md#5-cần-core--chờ-anh-của-engine-này), không khôi phục socket/route/SQL riêng Mask.
- **Ngăn engine + CAS/ghi lô nguyên tử/duy nhất:** bảng tên gốc–bí danh, cụm chờ, yêu cầu và tham chiếu tạm là dữ liệu lâu dài. `kho_tam.py` theo quyết định tạm chỉ lưu mã/băm/số đếm, không được lưu tên gốc/toàn văn/kết quả mở che. Băm không khôi phục tên gốc; khi chưa có port ngăn thì xử lý thật phải `MASK_KHO_CHUA_NOI`, kho DEMO chỉ ở fixture ngoài gói. Cần Core chốt chuyển dữ liệu/cửa 113, 117–120 sang ngăn chung.
- **Danh tính/mã yêu cầu:** SDK hiện chỉ có `viec_id`, `buoc`, `phap_nhan_id`, thiếu module/người gửi/tài liệu đã xác minh. Core phải cấp mã ổn định và kiểm quyền khi snapshot/chốt/mở che/đọc lại/tải tệp; không nhận danh tính tự khai trong tham số/config, không lấy pháp nhân làm quyền mở che. Cần xác nhận tham chiếu tệp con trong JSON cùng việc đi qua `mo_tep`.
- **Chốt và mất ACK (J8b):** đối soát ghi kho/kết quả, giao lại không cấp/đếm/đóng trùng; lượt bền #10 khi bên lưu trữ đã nhận chốt mà chưa trả. Chưa có API ngăn/giữ-chốt-đọc thì chỉ kiểm bằng port giả; không tự khai API mới.
- Kênh cấu hình tới `Engine`, nhật ký/thẻ trạng thái, UI ngăn/màn thử chung chỉ Admin; màn duyệt/lọc kiểu Excel còn thiếu, không tự nối màn riêng cũ. Core kiểm nguồn sinh `van_ban_da_che` và chuỗi Mask → Cloud, kiểm quyền cả đọc kết quả/tệp, không chỉ tin mã loại/cờ caller. Hỏi AI bản 1 vẫn tắt Cloud.
- Tên tám contract lịch sử/`noi_dung_da_che.v1` cần lead đối chiếu cổng mới; không đổi nghĩa lượt/hạn/danh mục của bản đã công bố. Bộ kết quả mở che `truong` không tự nối vào Trích xuất đang nhận `tra_loi_ai`; cần thiết kế riêng nếu có chuỗi đó.

## Chờ Anh / lead — MASK-P

- Chốt đề xuất bổ sung `van_ban_da_che` ở [cuối sổ loại riêng](../../_chung/docs/LOAI-DU-LIEU-RIENG.md#3-đề-xuất-mask-p-chờ-anh--chi-tiết-van_ban_da_che), Q1/Q3/Q4 theo phiếu thứ tự; không coi Q2 dành cho OCR là quyền lưu tên gốc của Mask xuống JSON.
- Cấp whitelist bốn tài nguyên detector sạch, chốt tiền tố tự sinh/tạm không trùng Junsky và đặc tả bản xuất danh mục sạch/quan hệ tên khác. Không dùng danh mục thật làm fixture; chuyển thật cần Anh xác nhận số dòng trước/sau.
- MASK-7 trình số đo DEMO, trần tệp/đầu ra, nguồn hoặc phương án cho Word giữ bố cục, sheet/chart Excel và mở che tệp còn thiếu; chỉ triển khai phần thiếu sau khi được chốt, ước lại giờ trước làm.
- Giữ việc chờ duyệt màn thử DEMO/tên contract theo cổng chung; Anh/lead chạy công cụ Windows và bài 11 bước sau khi Core đủ cửa, ca OCR chưa nối ghi “chưa kiểm”.

## Hiện vật không mang sang gói — ghi nhận MASK-P

Vỏ `ma-nguon/chay.py`, `vong_doi.py`, shim, contract bốn mẫu cũ, helper mã hóa bảng và các bản tham chiếu SQL/route/UI không dùng cho gói SDK 2.0. Giữ nguyên, không xóa/di chuyển trong MASK-P; lead xem xét chuyển `LUU-TRU/` sau khi có gói thay thế và kiểm đủ.
