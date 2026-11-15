# Bàn giao MASK-2c-1 — 15/11/2026

**Kết luận: Đạt phạm vi MASK-2c-1 bằng CoreGia; chưa đạt nghiệm thu tích hợp CLI SDK chuẩn do thiếu nguồn quyền Core.** PR: **chờ lead mở**, không commit/push.

**Đã làm:** Đúng bốn tệp mã theo phiếu: `anh_xa_ai.py`, `ho_so_ai.py`, `che_van_ban.py`, `nguon/privacy/types.py`. Ghi khoảng ngay trong vòng thay tên, không suy từ chênh chiều dài hoặc tìm lần xuất hiện đầu. Giữ ba hệ gốc Unicode, bản dò NFC/Cf và bản che. Script gốc → bỏ Cf/selector, bản sạch → NFC, gốc → che; chuyển bản dò ↔ bản che bằng hợp thành qua gốc. NFD/Cf/alias là quan hệ khoảng; chỉ alias bao trọn khoảng gốc mới chứng minh đã che tên. Map có SHA UTF-8, phiên bản và bảng Unicode, kiểm phủ/ngữ nghĩa/script trước phát hành.

Snapshot bất biến chứa gốc/bản dò/bản che/map/kế hoạch đoạn, JSON chuẩn có băm bytes. RAM hoặc port tệp tạm Core có quyền; Ngan chỉ giữ chỉ mục băm/tham chiếu, không toàn văn/map. Chưa có Core thật: adapter kho tệp CoreGia DEMO ở `tests/ho_tro_ho_so_ai.py`, ngoài gói. Thiếu quyền/tệp/chỉ mục, sai map/băm/kế hoạch thì từ chối; retry cùng mã+băm không tạo lại chỉ mục/tệp; giữ ChuaRo/hủy/CAS. `che_co_anh_xa` chỉ nội bộ, lớp 1 chặn vẫn chặn. Giữ nguyên API/manifest/kết quả công khai, bốn xfail held-out và Cloud tắt; không gọi engine khác.

**Kết quả kiểm:** Lượt cuối bằng `.venv/Scripts/python -B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

| Lệnh | Kết quả thật | Mã thoát |
|---|---|---|
| `-m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | 0/2 ĐẠT; hai lỗi “Chưa xác minh được phiên và quyền xử lý yêu cầu.” | 1 |
| `-m pytest e_mask/tests -q` | **866 passed, 4 xfailed, 190 subtests passed in 78.34s (0:01:18)**; 0 skipped | 0 |
| `e_mask/tests/kiem_doc_lap.py` | ĐẠT, không tham chiếu bị cấm/tệp biên dịch | 0 |
| `e_mask/tests/chay_demo.py` | **2/2 ĐẠT**, che và mở che qua quyền/ngăn DEMO | 0 |
| `git diff --check` | Không lỗi khoảng trắng | 0 |

**Đã kiểm bằng Core giả (CoreGia)**; chưa kiểm Core thật, Linux thực tế hoặc Local AI thật. Gồm 125 test mới; bốn xfail strict held-out là giới hạn lớp 1, không nới hoặc vá từng tên. Bộ mới kiểm round-trip phần giữ nguyên (cả NFD/ngoài BMP), quan hệ bao tên, Cf bị bỏ/thay dấu cách, selector/tab/NBSP, alias dài/ngắn/lặp/chồng/prefix, tiền/ngày, 500000/500001, JSON/map/băm/phiên bản/kế hoạch sai, quyền/tệp/chỉ mục thiếu, đọc qua hai bước, retry, ChuaRo/hủy/CAS và không ghi đĩa.

[Đầu ra thực tế](KET-QUA-KIEM-MASK-2c-1.txt) giữ cả các lượt lỗi hiệu năng trước lượt cuối: trước tối ưu ASCII có 2 subtest lỗi (timeout 12 giây và 8,474 giây); sau tối ưu ASCII còn ca `1 ` mất 6,734 giây. Ca này không chạy map. Đã tối ưu định vị nghi vấn số dài trùng toàn văn, đối chiếu cùng offset/cờ chặn với KnownText; một lượt kiểm riêng còn dao động 5,059 giây. Lượt toàn bộ cuối đạt tất cả ngưỡng cũ 5 giây/timeout 12 giây; không sửa test, skip hoặc tăng ngưỡng. cProfile của ca số giảm từ 5.257.903 xuống 1.507.887 lời gọi. Không suy số đo hiệu năng này thành bảo đảm cho mọi văn bản/model.

Môi trường: Windows x64, Python 3.13.14, pytest 9.1.1 sẵn có qua venv `--system-site-packages`; SDK 2.0.0 cài offline `--no-index --no-deps`. SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Không thêm dependency runtime.

**Thời gian thực tế:** **12:12:00–12:59:54 ngày 15/11/2026 (UTC+07), 0.80 giờ**, so với **6 giờ ƯỚC TÍNH** trong phiếu. Mốc bắt đầu theo lệnh lead.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** Không vượt bốn tệp mã. Port nội bộ CoreGia/RAM tạm theo phiếu; không giả transport SDK đã có. Thêm giới hạn kỹ thuật snapshot 64 MiB (vượt từ chối), không đổi trần công khai. Hai tối ưu hiệu năng tương đương nêu trên nằm trong hai tệp được phép, giữ nguyên kết quả chặn. MASK-2c-1 chỉ lưu/kiểm kế hoạch Core cấp (phủ đủ, biên từ/NFD/Cf, SHA, trần 8.000/512/128); thuật toán lập đoạn, prompt/khuôn/profile và Local thuộc các lát sau. Profile `chuyen_tiep.mask_2c` theo lead duyệt 15/11, không đổi schema chung.

**Cần Core / Chờ Anh mới phát sinh:** Cụ thể hóa C-M2C-01/02/05 trong [VIEC.md](VIEC.md): kho tệp snapshot có ACL/lease nguyên tử và vòng đời/dọn tệp chưa có chỉ mục; bàn giao kế hoạch và quyền qua các bước; bảng chỉ mục `ho_so_ai` qua Ngan thật. Thiếu cửa vẫn từ chối; test CoreGia không chứng nhận giao dịch/quyền Core thật. Không có câu chờ Anh mới. Các cửa chứng thực AI-9 và trước Cloud giữ nguyên phụ thuộc đã ghi; chưa triển khai trong lát này.
