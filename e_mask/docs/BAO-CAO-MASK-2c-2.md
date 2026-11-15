# Bàn giao MASK-2c-2 — 15/11/2026

**Kết luận: Đạt phạm vi MASK-2c-2 bằng CoreGia; chưa đạt nghiệm thu tích hợp CLI SDK chuẩn vì thiếu nguồn quyền Core.** Đã kiểm bằng Core giả (CoreGia); chưa kiểm Core/model thật hoặc Linux thực tế. PR: **chờ lead mở**, không commit/push.

**Đã làm:** Đúng năm tệp mã được giao: `chuan_bi_ai.py`, `chay.py`, `phong_bi.py`, `kho_dinh_danh.py`, `engine.json`. Bản gói 1.1.0 đăng ký `mask.chuan_bi_ai_cuc_bo@1`, nhận `van_ban`/`van_ban_tai_lieu`/`tep` JSON như che hiện tại, chỉ trả `yeu_cau_ai`; hai năng lực cũ giữ nguyên `tra`. Chạy đầy đủ MASK-2b qua cửa map MASK-2c-1; còn sót, thiếu tài nguyên, lỗi tiền/ngày vẫn chặn. Không trả `van_ban_da_che` trung gian.

Kế hoạch phủ đủ gốc với vùng chính liên tiếp, đoạn tối đa 8.000 code point gồm overlap 512 mỗi phía được làm tròn vào biên an toàn. Khi còn đủ nguồn, overlap không dưới 300; không tìm được biên phù hợp thì từ chối. Tối đa 128 đoạn; giữ trần 500.000, không bỏ đuôi/cắt từ/NFD/Cf. Span gốc đã nhận diện dài hơn 300, kể cả NFD/Cf trong tên, bị chặn; khuôn AI cũng giới hạn nguyên văn 300, yêu cầu không cắt tên để trả hoàn tất giả. Nhận diện tên dài chưa được lớp quy tắc biết vẫn phụ thuộc AI-9/hậu kiểm ở các lát sau.

Snapshot bất biến ở kho Core bao nguyên `HoSoAI` cùng kết quả quy tắc đạt, prompt của module/quy trình có mã/phiên bản, khuôn, profile và biên nhận model/budget/deadline. Ngăn chỉ lưu chỉ mục băm/tham chiếu, ghim từ đầu bằng `lay_hoac_tao`, chốt tham chiếu có CAS. Cùng mã yêu cầu/quyền, input và các băm qua retry; không dùng mã tự khai trong payload. Snapshot được đọc lại kiểm bytes/kích thước/SHA/ACL trước phát hành; mất snapshot, đổi quyền/pháp nhân hoặc hết hạn đều chặn.

`tai_lieu` là đoạn GỐC nguyên NFD/Cf/selector/tab/NBSP, chỉ Local. `chuyen_tiep.mask_2c` đúng sổ chung §6 đã được lead duyệt, chỉ mã opaque/tham chiếu/băm/chỉ số, không tên/map/gốc. Khuôn nằm trong `chuan_bi_ai.py`, đủ `da_quet_het`, ba loại thực thể, `nguyen_van`, offset và mức chắc/nghi ngờ; object đóng, cho phép mảng rỗng, giữ mỗi lần xuất hiện. Profile và khuôn băm JSON chuẩn, prompt băm UTF-8, profile không tự chứa băm chính nó. Không thêm kho prompt engine.

**Kết quả kiểm:** Lượt cuối dùng `.venv/Scripts/python -B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

| Lệnh | Kết quả thật | Mã thoát |
|---|---|---|
| `-m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT**, cả hai bị chặn: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” | 1 |
| `-m pytest e_mask/tests -q` | **972 passed, 4 xfailed, 190 subtests passed in 89.92s (0:01:29)**; 0 skipped | 0 |
| `e_mask/tests/kiem_doc_lap.py` | **ĐẠT**, không tham chiếu bị cấm/tệp biên dịch; kiểm lại sau cập nhật tài liệu vẫn đạt | 0 |
| `e_mask/tests/chay_demo.py` | **2/2 ĐẠT** qua ngăn và quyền DEMO được tiêm ngoài gói | 0 |
| `git diff --check` | Không lỗi khoảng trắng | 0 |

[Đầu ra lệnh thực tế](KET-QUA-KIEM-MASK-2c-2.txt) giữ cả lượt hồi quy đầu **3 failed, 969 passed, 4 xfailed**, và lượt cuối đạt. Ba lỗi đầu thuộc adapter MASK-3 lịch sử nạp toàn manifest mới nhưng chỉ đăng ký hai handler cũ; fixture đã chuyển sang phiếu con của chính hai năng lực đang kiểm. Không thêm stub, bỏ ca hoặc nới kiểm chống trùng. Hai test danh sách năng lực cập nhật theo đăng ký mới. Đường dẫn thư mục tạm DEMO trong traceback được ẩn; thông báo lỗi và số đếm giữ nguyên.

Có **106 test mới**, kiểm cấu trúc/contract yêu cầu, SHA profile/khuôn/prompt/snapshot, Local bắt buộc, gốc Unicode, map không rò chuyển tiếp, độ phủ/overlap/biên/tên lặp, 500.000/500.001 và các trần, budget cả đoạn cuối, prompt injection chỉ là dữ liệu, thiếu cổng/quyền/snapshot/tài nguyên, deadline từng mốc, CAS, hủy, ChuaRo sau lưu, retry/mất ACK không tăng alias/đếm gặp, lỗi cổng/ngăn không rò gốc, và không gọi Cloud/engine khác. Bốn xfail strict held-out giữ nguyên: giới hạn lớp 1, nợ CAO chưa đóng. **0 lượt Cloud, 0 lượt gọi engine khác từ Mask.** Chưa chạy AI-9, hậu kiểm lớp hai hoặc đo tỷ lệ lọt Local thật.

Môi trường Windows x64, Python 3.13.14; venv dùng pytest 9.1.1 sẵn có qua `--system-site-packages`, SDK 2.0.0 cài offline `--no-index --no-deps`. SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Không thêm dependency runtime.

**Thời gian thực tế:** 13:02:00–13:31:40 ngày 15/11/2026 (UTC+07), 0.49 giờ; so với **6 giờ ƯỚC TÍNH**, độ khó **kho** trong phiếu. Mốc bắt đầu theo lệnh lead.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** Không vượt năm tệp mã. Dùng port Core nội bộ đề nghị và RAM CoreGia ngoài gói đúng ủy quyền; không giả SDK 2.0 đã có API chuỗi. Snapshot chuẩn bị bao cấu trúc MASK-2c-1 trong cùng tệp, không sửa `ho_so_ai.py`. Khai bảng chỉ mục mới bằng hằng nội bộ, chưa sửa khai báo SDK 2.1 hoặc schema chung. Các trần kỹ thuật mới được ghi rõ trong profile: prompt 16.000 code point, 2.000 thực thể/đoạn, JSON phản hồi 1 MiB; khuôn 32 KiB, chuyển tiếp 64 KiB, snapshot 64 MiB theo giới hạn trước. Đây là trần từ chối, chưa phải sức chứa đã đo của model.

**Cần Core / Chờ Anh mới phát sinh:** Đã cụ thể hóa C-M2C-01/02/05 trong [VIEC.md](VIEC.md): nối `CongChuanBiAI` với kho tệp có ACL/lease và mã yêu cầu ổn định; cấp/ghim prompt module; tokenizer/model thực và deadline bất biến cho mọi đoạn; bàn giao toàn kế hoạch và nguồn; bảng ngăn `chuan_bi_ai` có CAS/chống lặp/vòng đời tệp. `cau_hinh`, `kiem_ngan_sach`, `kiem_han`, `ban_giao` là phương thức port đề nghị, **chưa phải API SDK thật**. Thiếu bất kỳ cửa bắt buộc thì runtime từ chối. Biên nhận token/deadline trong adapter là fixture, không chứng nhận model thật hoặc khả năng chạy dài. C-M2C-03/04, AI-9 và MASK-2c-3/4 vẫn là phụ thuộc sau; Cloud giữ tắt. Không có câu chờ Anh mới.
