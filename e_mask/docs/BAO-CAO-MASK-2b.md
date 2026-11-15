# Bàn giao MASK-2b — 15/11/2026

**Kết luận:** Đạt phạm vi đóng nợ CAO tên người viết thường không nhãn; đã kiểm bằng Core giả (CoreGia). Chưa đạt nghiệm thu chung CLI SDK chuẩn do thiếu nguồn quyền Core, đúng giới hạn đã có. PR: **chờ lead mở**; không commit/push.

**Đã làm:** Hai tệp runtime: thêm `ten_nguoi.py`, sửa `che_van_ban.py`. Dò họ từ từ điển sạch theo sau bởi 1–3 âm tiết, so sau bỏ dấu/hoa thường, giữ ánh xạ NFC/NFD/Cf/xuống dòng về nguyên văn. Tên có danh xưng hoặc khớp đúng một tên chính thức được che bằng bí danh; khớp bỏ dấu vẫn dùng bí danh chính thức. Tên chưa đủ tin cậy vào `con_sot` với lý do **“nghi tên người viết thường”**, không trả nội dung che hoặc phong bì `van_ban_da_che`. “và”/ngoặc chức danh củng cố nghi vấn; bí danh tạm chưa phải tên đã duyệt.

**Kết quả kiểm:** `kho_tri_thuc_sdk.thu` chuẩn **0/2 ĐẠT, mã 1**, cả hai báo thiếu nguồn quyền tin cậy. Cổng thay thế được phép `chay_demo.py` **2/2 ĐẠT, mã 0**. `pytest e_mask/tests -q --basetemp=.pytest-tmp`: **545 passed, 190 subtests passed, 0 skipped, 29,81 giây, mã 0**; gồm **107 test MASK-2b**. `kiem_doc_lap.py` **ĐẠT, mã 0**. Đã kiểm bằng Core giả (CoreGia), không nối Core thật. Kết quả lệnh nguyên văn ở [KET-QUA-KIEM-MASK-2b.txt](KET-QUA-KIEM-MASK-2b.txt).

**Thời gian thực tế:** Bắt đầu **09:19**, chốt báo cáo **09:42:22 ngày 15/11/2026 (UTC+07)**, khoảng **0.39 giờ**. Phiếu không có ước tính riêng MASK-2b; MASK-2 gốc là **3 giờ ước tính**, không lấy đó làm dự toán riêng đã duyệt cho MASK-2b.

Môi trường kiểm: Windows x64, Python **3.13.14**; `.venv` dùng pytest **9.1.1** có sẵn qua `--system-site-packages`. SDK **2.0.0** cài offline từ wheel repo bằng `--no-index --no-deps`; SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; không có mã biên dịch trong gói.

Chặn tên chỉ che được prefix, tên dài và danh mục có nhiều tên trùng sau bỏ dấu. Bộ hậu kiểm mới chạy độc lập detector cũ; NUL do caller chèn không được giả làm bí danh đã che. Bộ dò cũ vẫn che tên chữ hoa như trước nếu đã che đủ; phát hiện mới không tự thay phạm vi nghiệp vụ đó. Chỉ danh xưng ở đúng lần xuất hiện mới tăng tin cậy, không nâng tất cả lần gặp cùng tên. Không trả tên gốc trong `con_sot`/lỗi/log.

**Lệch khỏi phiếu / quyết định tạm:** Không mở rộng ngoài lát, chỉ hai tệp runtime, không dependency mới. Giữ nguyên `_chung/**`, `ngan.py`, `cau_hinh.py`, bốn từ điển và nguồn cũ. Điều chỉnh test lưới nhãn để giả lập cả hai bộ dò không tìm thấy, vì bộ dò mới giờ đã nhận ra tên sau Ông/Bà. CLI SDK dùng cổng thay thế DEMO đã được phiếu MASK-5 cho phép; không đổi quyền để làm xanh CLI.

**Cần Core / Chờ Anh mới phát sinh:** Không. Các việc ngăn/quyền thật và kiểm nguồn sinh `van_ban_da_che` trước Cloud giữ nguyên trong VIEC. Cloud không được gọi; chưa kiểm Linux hoặc Core thật.

## Đo báo nhầm

Đã đo thật trước khi nối bộ dò vào lõi và sau khi sửa, trên Windows/Python 3.13.14, SDK 2.0.0. Nền trước sửa: `35bd626ffa81b01d5b23652a369063b24c82162a`. Cùng tập đầu vào và bốn từ điển sạch ở cả hai mốc. Dữ liệu đều giả DEMO; không có fixture recall được Git quản lý trong repo. Đây là mẫu nhỏ gán nhãn thủ công, không đại diện tỉ lệ ngoài vận hành.

Tập cũ gồm **14 đoạn/câu literal có sẵn** trong ba tệp test; công cụ kiểm lại nguồn bằng AST, không sinh mẫu thay thế. Tập mới gồm **30 câu** nghiệp vụ kế toán/hợp đồng không chứa tên người/tổ chức nhạy cảm. Mẫu và thứ tự tại `tests/do_mask_2b.py`; số đo máy đọc tại [SO-DO-MASK-2b.json](SO-DO-MASK-2b.json). Báo nhầm = có che thừa **hoặc** bị chặn, đếm hợp của hai nhóm, không suy từ toàn bộ số test passed.

| Tập | Trước: chặn / che thừa | Sau: chặn / che thừa | Báo nhầm trước → sau | Báo nhầm tăng thêm |
|---|---|---|---|---|
| 14 mẫu có sẵn | 0 / 1 | 0 / 1 | 1/14 (7,14%) → 1/14 (7,14%) | 0 |
| 30 câu bổ sung | 1 / 1 | 1 / 1 | 2/30 (6,67%) → 2/30 (6,67%) | 0 |

Không giấu ba ca nền:

- Mẫu cũ 10: “— nội dung DEMO giữ nguyên;” bị che thừa chữ DEMO.
- Mẫu mới 15: “Đáo hạn khoản vay vào ngày 2026-10-30.” bị lớp số/ngày cũ báo `GIAY_TO`/`TAI_KHOAN`. Tên người không gây chặn mới ở ca này; chưa sửa bộ số/ngày trong lát MASK-2b.
- Mẫu mới 30: “Dữ liệu giả DEMO dùng để kiểm tra quy trình kế toán.” bị che thừa chữ DEMO. Cả 30 câu vẫn nằm trong phép đo; **29 câu không bị chặn** có test riêng, vượt yêu cầu ít nhất 20 câu.

Bốn ví dụ giao việc trước sửa đều phát hành nguyên tên (**4/4 lọt**). Sau sửa: ví dụ 1 và 4 bị chặn bởi nghi tên người; ví dụ 2 và 3 che tên bằng bí danh tạm rồi phát hành. **0/4 lọt** trên bốn ví dụ gốc. Test thêm không dấu, chữ hoa toàn bộ, xuống dòng/tab/NBSP, NFD và Cf; không suy rộng thành recall 100% cho mọi tên.

Chạy lại số đo sau sửa:

```text
.venv/Scripts/python e_mask/tests/do_mask_2b.py --moc sau
```

Mốc `truoc` đã ghi khi chưa nối mã; không chạy `--moc truoc` trên bản sau sửa để thay số nền.

## Ngoại lệ và giới hạn

- `leftover_allowlist`, `vn_places`, `common_acronyms` được so sau bỏ dấu/hoa thường, giữ ranh giới từ. Danh sách cụm thông dụng trùng họ ở `_CUM_THONG_DUNG` trong `ten_nguoi.py`, ví dụ “lê thê”, “lý do”, “nghiệm thu”, “phân bổ”, “giữ nguyên”. Không miễn toàn bộ các từ “lê”, “lý”, “cao”. Danh xưng/tên chính thức ưu tiên hơn ngoại lệ; nhiều tên chính thức trùng nhau sau bỏ dấu phải duyệt.
- Họ + 1–3 âm tiết là cửa chọn che; đoạn có 5 âm tiết nghi tên không tự cắt để báo đạt. Từ nối/lời văn được tách bằng quy tắc hữu hạn, tên hiếm vẫn có thể báo nhầm hoặc không được nhận diện. Chú không dấu trùng họ Chu được xử lý bảo thủ.
- Họ ngoài từ điển, tên viết tắt N.V. An, tên trùng hẳn địa danh/cụm miễn và cách viết ngoài dạng âm tiết chữ Việt chưa có chứng minh nhận diện đầy đủ. Ngoại lệ theo cụm có thể loại cả tên thật trùng cụm đó khi thiếu danh xưng/danh mục chính thức. Đây không phải chứng nhận đủ điều kiện bật Cloud.
- `con_sot` chỉ chứa nhóm/vị trí/lý do. Vị trí cảnh báo từ bản hậu kiểm thuộc bản đã che; cảnh báo một ứng viên bị che dở hoặc chưa đủ tin cậy giữ vị trí bản gốc để không mất phần đuôi.
