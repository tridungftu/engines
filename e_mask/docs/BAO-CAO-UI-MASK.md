# Báo cáo UI-MASK — 21/11/2026

**Kết luận: Chưa đạt nghiệm thu chung.** Đã triển khai phần mã UI theo §4 phiếu, 61/61 test UI đạt; full pytest còn 3 lỗi hiệu năng, CLI chuẩn còn nợ quyền Core cũ và chưa có ảnh chụp/browser QA vì công cụ browser không được phê duyệt.

**PR: chờ lead mở.** Nhánh `codex/e_mask-ui-mask`; không commit/push. Bắt đầu theo mốc lead: **21:41 ngày 21/11/2026 (UTC+07)**. Ước tính trong phiếu: **2 giờ**. Kết thúc **22:59:31 ngày 21/11/2026 (UTC+07)**; thực tế **1.31 giờ**, gồm đọc, triển khai, xử lý môi trường và hai lượt full.

## Đã làm

- `ui/cau_hinh.js` và `ui/cau_hinh.css`: màn theo thẻ, hai cột ở màn rộng/một cột dưới 720 px, nhãn trạng thái, focus bàn phím. Thời hạn ánh xạ số nguyên 60–900 giây, mặc định 600; hướng dẫn và mẫu tại ô, lỗi chỉ rõ trường; chỉ giữ phiên CAS trong RAM.
- Đọc/lưu qua `KttCore.engine("e_mask").cau_hinh`; khóa khi chưa đọc/lưu đang chạy; CAS tranh chấp hoặc thiếu ACK yêu cầu tải lại, không tự gửi lại. Trường lạ hoặc bản đọc sai bị từ chối để tránh làm mất cấu hình.
- Thẻ chỉ đọc bộ tiền tố và bốn từ điển của gói. Test đối chiếu với `CAC_TIEN_TO`, `TEN_TAI_NGUYEN` và SHA thật; tên tệp đặt ở Nâng cao. Đây là thông tin tài nguyên của gói, không giả kết quả kiểm sức khỏe tiến trình.
- Gộp màn duyệt; bỏ xưng hô, đưa ID vào Nâng cao, thêm hướng dẫn/mẫu mã đối tác. Giữ nguyên đường kiểm quyền/vé/CAS, chỉ nhận metadata, không ghi ngăn từ trình duyệt.
- Schema có title/description/examples đầy đủ, diễn giải cấu trúc và mẫu. Chỉ khai dự kiến màn trong `KHAI-SDK-2.1.json`; không thêm khóa SDK chưa nhận vào engine.json.
- Cập nhật README/CHANGELOG/VIEC và kiểm kê gói bằng bytes/SHA. Không sửa runtime Python, hành vi xử lý việc, engine.json, API v1, nguồn từ điển hoặc dependency chạy của engine; bổ sung dependency SDK vào lock của bộ kiểm. Không cần sinh lại danh mục engine.

## Kiểm thật

Đã kiểm bằng Core giả (CoreGia), không phải Core thật. Node dùng KttCore giả trong bộ nhớ, không mạng.

| Lệnh | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**; cả hai DEMO: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Nợ C-MS22-01 cũ, không hạ kiểm quyền |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q --tb=short` | **4.660 passed, 3 failed, 4 xfailed, 188 subtests passed, 0 skipped**, 1.473,57 giây, **mã 1**; log `.venv/ui-mask-pytest-cuoi.txt` |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; không tham chiếu bị cấm/tệp biên dịch |
| `node --test e_mask/tests/ui/cau_hinh.test.mjs e_mask/tests/ui/duyet_dinh_danh.test.mjs` | **61 passed, 0 failed/skipped, mã 0**, 0,41 giây; log `.venv/ui-mask-node.txt` |
| Pytest nhóm `test_ui.py`, `test_ui_mask.py`, `test_mask_s22.py` | **10 passed, 0 skipped, mã 0**, 1,82 giây sau bản nạp ESM tương thích Node 18+ |
| Kiểm kê gói | **63/63 tệp**, bytes/SHA khớp, phiên bản theo engine.json **1.6.1** |
| `git diff --check` | **Mã 0** |

Các đường đã phủ: đọc/lưu, mặc định và hai biên, lỗi nhập và sửa lỗi, bản đọc sai/null/trường lạ, CAS và tải lại, lỗi nguồn không lộ thông điệp, mất ACK, bấm lặp, submit bàn phím, điểm nạp/dọn màn module; hồi quy duyệt thành công/từ chối, thiếu cửa/quyền, vé sai, CAS, dữ liệu bí mật không vào DOM. CSS có breakpoint và focus; **chưa xác nhận bố cục bằng browser thật**.

Lát UI-MASK không có máy/dịch vụ ngoài, nút kiểm kết nối hoặc API key (`bi_mat: []`). Ca kiểm máy và API key hiện bốn ký tự cuối **không áp dụng**; test bảo đảm màn không gọi cửa bí mật, không thêm bí mật DEMO để tạo chức năng ngoài phiếu.

Môi trường: Python 3.13, Node 24; SDK 2.2.0 cài offline từ wheel trong repo, SHA-256 khớp `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`. Công cụ pytest/dependency được sao offline vào venv từ môi trường sẵn có, đúng phiên bản đã ghim. Sau lượt full đầu, bổ sung offline `jsonschema` và dependency (đã được SDK khai `Requires-Dist: jsonschema>=4.18,<5`), ghim trong `tests/requirements.lock` để CoreGia kiểm đầy đủ minimum/maximum; không thêm import hoặc dependency chạy riêng cho engine. Bộ nạp ESM của test dùng API Node 18+; chưa chạy Node 18 hoặc Linux thật.

Lượt full đầu trước sửa môi trường: **8 failed, 4.656 passed, 4 xfailed, 187 subtests passed**, 1.794,07 giây, mã 1. Hai ca TTL 59/901 không bị CoreGia từ chối do thiếu jsonschema. Fixture `demo_mask_r3.json` chỉ bị checkout CRLF (42 dòng); đã đối chiếu `raw.replace(CRLF, LF)` bằng đúng blob Git rồi khôi phục byte LF, SHA giữ nguyên `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`. Không đổi nội dung/gold, không có diff nội dung fixture.

Chạy lại riêng nhóm lỗi sau sửa môi trường: toàn bộ ca schema và hash đạt; còn một subtest chuỗi `1, ` mất **6,454 giây** so với trần **5 giây**, và hai ca dò alias mất **2,064 / 2,407 giây** so với trần **2 giây**. Đây là các phép đo hiệu năng có sẵn trong phiên này; chưa kết luận nguyên nhân tải máy. Không sửa runtime, không nới ngưỡng hoặc thêm skip/xfail. Lượt full cuối đang chạy trên môi trường đã đủ dependency, log `.venv/ui-mask-pytest-cuoi.txt`.

## Ba lỗi còn lại trong full cuối

| Ca có sẵn trong bộ kiểm | Đo được | Ngưỡng giữ nguyên |
|---|---:|---:|
| `CheVanBanDemoTests.test_hieu_nang_ba_chuoi_benh_ly_500_nghin_ky_tu`, subtest `1, ` | 5,508 giây | ≤ 5 giây |
| Cùng test, subtest `1 ` | 6,154 giây | ≤ 5 giây |
| `test_do_1000_alias_500000_ky_tu_duoi_2_giay`, mẫu `[[P{:04d}-DEMO-001]]` | 2,170 giây | < 2 giây |

Không thêm skip/xfail, không sửa ngưỡng hoặc runtime để làm xanh. Bốn xfailed cũ thuộc `test_mask_2b.py::test_held_out_ten_khong_lot`, lý do “giới hạn quy tắc, nợ CAO”. Chưa phân lập nguyên nhân tải máy/baseline của các ca hiệu năng; không khẳng định do môi trường. Lead cần xử lý ở lát riêng, không mở rộng UI-MASK. Ba lỗi môi trường/schema/hash ở lượt đầu đã hết trong full cuối.

## Lệch khỏi phiếu / phần còn thiếu

- **Chưa có ảnh chụp**, không nhận là đã đối chiếu bố cục browser. [Fixture và cách dựng](anh-ui-mask/README.md); KttCore giả nằm ngoài gói chạy. CUA timeout; Chrome headless không dựng được PNG. Computer Use từ chối Edge/Chrome vì chưa được phê duyệt; không vượt qua kiểm quyền công cụ.
- Không thêm thao tác Python mới vì UI-MASK không cần máy ngoài hoặc thay đổi quản trị backend; màn duyệt kế thừa cửa C-P4-06 chưa có binding SDK. Không dựng backend giả trong gói.
- Cập nhật test S22 cũ vốn cấm mọi tệp KHAI-SDK-2.1: nay kiểm tệp này chỉ chứa cửa màn còn thiếu, không đưa ngăn/cấu hình về cổng tạm. Đây là thay đổi để đáp ứng phiếu UI hiện hành.

## Cần Core / Chờ Anh

- **C-UI-MASK-01:** cửa D nạp màn/stylesheet và xác nhận hợp đồng API trình duyệt đọc `{gia_tri, phien_ban_cau_hinh}`, lưu trả phiên mới, schema/CAS/quyền admin_core.
- Kế thừa **C-P4-06** (xem/duyệt tin cậy) và **C-MS22-01** (quyền CLI chuẩn); không có cửa backend/bí mật/máy ngoài mới.
- Cần quyền công cụ browser để chụp ảnh và hoàn thành QA bố cục; chưa có quyết định nghiệp vụ mới cần Anh.
