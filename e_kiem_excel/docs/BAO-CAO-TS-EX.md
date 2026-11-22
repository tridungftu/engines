# TS-EX — 21/11/2026 · PR: chờ lead mở

Kết luận: **Đạt phần mã và kiểm nghiệm thu của TS-EX**; đã kiểm bằng Core giả
(CoreGia), chưa nối Core thật. Cửa D2 phía Core còn chờ.

Đã làm:

- Trình soạn dùng chung hai năng lực, ở `goi/e_kiem_excel/ui/`: chọn/nhập
  sheet và ô hoặc nhãn tìm; bộ nhóm theo thứ tự với điều kiện OR, cụm AND,
  từ khóa OR, vùng và loại trừ; khuôn cột với kiểu/bắt buộc và nhãn dòng dừng.
  Thêm/bỏ/đổi thứ tự, chèn mẫu DEMO, để trống, lỗi cạnh trường; JSON chỉ đọc.
- Giữ nguyên JSON v1, trần và mọi mã Python xử lý việc. Không thêm dependency
  runtime, ngăn/cấu hình/bí mật, thao tác quản trị hoặc mạng ngoài. Không có
  `cau_hinh.schema.json`, dịch vụ ngoài/key nên các kiểm tương ứng không áp dụng.
- Hợp đồng nhúng D2 **dự kiến** trong `KHAI-SDK-2.1.json`, không thêm khóa
  chưa được SDK nhận vào manifest. Callback lưu của màn bước kiểm CAS,
  lỗi/xung đột không lộ chi tiết, giữ bản sửa và buộc tải lại. Không lưu
  tham số quy trình vào `.cau_hinh`/`.ngan` của engine.
- `mo_ta` tiếng Việt cho ba tham số JSON, bảng cấu trúc từng cấp/hướng dẫn/mẫu
  đầy đủ trong README. Đã sinh lại danh mục bằng công cụ quy định; nội dung
  danh mục không đổi vì chỉ thêm mô tả. Không sửa tay danh mục.
- [Ba ảnh desktop/mobile](anh-TS-EX/README.md) dựng bằng KttCore giả, đã xem
  và đối chiếu ảnh mẫu. Trình duyệt headless kiểm không tràn ngang ở 1180 px
  và 390 px; nút Kiểm tra cài đặt hoạt động trên DOM thật.

Kết quả kiểm thật trên Windows x64, Python 3.13.14, SDK 2.2.0, Node 24.18.0:

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 5/5 [ĐẠT], mọi ví dụ DEMO đều đạt; mã thoát 0.

.venv/Scripts/python -B -m pytest e_kiem_excel/tests -q
→ 241 passed in 74.31s (0:01:14), 0 skipped; mã thoát 0.

.venv/Scripts/python -B e_kiem_excel/tests/kiem_doc_lap.py
→ [ĐẠT] AST, cây gói, import cô lập; đã kiểm bằng Core giả (CoreGia):
  5/5 DEMO XONG (toàn vẹn K1–K8, đọc bảng EX-4/EX-5); mã thoát 0.

node --test e_kiem_excel/tests/ui/tham_so.test.mjs
→ 12 tests, 12 pass, 0 fail, 0 skipped; mã thoát 0.

node e_kiem_excel/tests/ui/chup_man.mjs
→ ĐẠT: 3 ảnh desktop/mobile, không tràn ngang, nút kiểm DOM thật hoạt động.

.venv/Scripts/python -B e_kiem_excel/tests/kiem_bam_goi.py --cap-nhat
→ [ĐẠT] SHA-256 nguyên trạng 25/25 tệp, gồm NGUON.md.

.venv/Scripts/python -B _chung/cong-cu/sinh_danh_muc_engine.py
→ Đã ghi _chung/docs/DANH-MUC-ENGINE-CHO-MODULE.md; mã thoát 0.

git diff --check
→ mã thoát 0.
```

Các lệnh Python bật `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`.
SDK được cài offline từ wheel repo, SHA-256 khớp `SHA256SUMS.txt`.
Ba dependency runtime cài offline từ kho wheel cục bộ với hash trong lock;
không thêm thư viện mới. Chưa chạy Linux trong lượt này.

12 test UI bao gồm đọc/lưu/lỗi nguồn, lỗi nhập, nút kiểm đạt/không đạt,
hai màn cùng sửa gây CAS, chống gửi hai lần, trần UTF-8, thứ tự/điều kiện
lồng nhau, round-trip 5 DEMO và an toàn hiển thị. Pytest còn cho **6 bộ tham
số do UI thực sự xuất** qua parser gốc và CoreGia: đều XONG. Không giả kiểm
bí mật 4 ký tự cuối vì engine không có bí mật hoặc API key.

Lệch khỏi phiếu / quyết định tạm đã dùng:

- SDK giới hạn `mo_ta` 500 ký tự; manifest dùng mô tả rút gọn kèm mẫu,
  README có bản đầy đủ. Không sửa/nới SDK.
- D2 chưa có hợp đồng SDK được phát hành: callback đọc/lưu bước là bản đề
  xuất để lead Core nối. UI có thể trả chuỗi tham số qua `xuat()`; không tự
  sáng tạo API lưu trong nhóm engine. Không có cửa lưu/phiên bản thì khóa lưu.

Cần Core / Chờ Anh mới phát sinh:

- Nạp trình soạn D2; cấp tham số/sheet/phiên bản và kiểm quyền/CAS/lưu bước
  đúng quy trình. Hiển thị mô tả và hướng dẫn đầy đủ trong ô JSON chung
  trong lúc chưa nạp màn. Chi tiết đã ghi mục Cần Core trong VIEC.md.
- Không có câu chờ Anh. Không commit/push; lead commit và mở PR.
  Tiêu đề dự kiến: `[e_kiem_excel] TS-EX — Trình soạn Cài đặt bước Excel`.

Thời gian thực tế: 0.68 giờ, từ 21/11/2026 21:40:00 đến 21/11/2026 22:21:02 (UTC+7); ước tính trong phiếu: 4 giờ.
