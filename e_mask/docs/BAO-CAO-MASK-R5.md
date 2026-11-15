# Báo cáo MASK-R5 — 15/11/2026

Kết luận: **Chưa đạt** — lõi RAM và adapter R5 đã kiểm, nhưng full pytest cũ chưa xanh; chưa nối runtime thật.

Đã làm: đúng năm runtime của MASK-P4 §4. Hồ sơ MASK-2c và map/gốc/bản quy tắc/kế hoạch/phiên bản chỉ trong `KhoAnhXaRAM` R4; đóng kho snapshot Core/chỉ mục cũ. Core chọn từng đoạn và nhận đúng phong bì Local cần thiết; không gọi Hỏi AI/model trong Mask. Chuyển tiếp chỉ mã RAM/băm/chỉ số/profile an toàn. Hậu kiểm dựng yêu cầu chuẩn từ RAM, kiểm đủ đoạn/nguồn/span/Unicode/overlap/trích dẫn/tiền-ngày và chặn replay/tệp đổi. Timer/quyền/hủy/lease/TTL R4 bao toàn bước; terminal lỗi dọn map. Local `ChuaRo` chỉ giữ trong hạn tuyệt đối. Tên mới chưa có bảo đảm C-P4-03 bị chặn, không ghi map vào ngăn.

Kết quả kiểm: **đã kiểm bằng Core giả (CoreGia)**. Python 3.13.14, SDK 2.2.0 cài offline `--no-index --no-deps` từ wheel repo, SHA-256 khớp `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`. Venv có jsonschema từ system site packages, pytest 9.1.1; không đổi dependency/lock. Các lệnh đều dùng `.venv/Scripts/python -B`, không bytecode. Ba lệnh nghiệm thu và diff đã chạy đủ; bảng số chốt bên dưới. Log thật: [KET-QUA-KIEM-MASK-R5.txt](KET-QUA-KIEM-MASK-R5.txt).

Thời gian thực tế: bắt đầu **22:17:00 ngày 15/11/2026 (UTC+07)** theo lead. Chốt kiểm **22:52:53 ngày 15/11/2026 (UTC+07)**, thực tế **0,60 giờ**. Ước tính phiếu **6–8 giờ**, độ khó **kho**.

Lệch khỏi phiếu / quyết định tạm đã dùng: không vượt năm runtime; kiểm kê/tài liệu/test ngoài giới hạn mã theo lệnh lead. Không commit/push/Core/SDK/schema/contract chung/dependency. **Điều kiện toàn bộ test cũ xanh chưa đạt**: không bỏ hoặc sửa test snapshot cũ để nhận giả luồng RAM đã tích hợp. Giữ nguyên test an toàn/skip/xfail/ngưỡng; bộ adapter/test R5 mới không thay số full. `chay.py` không thuộc R5 nên lời gọi cũ chưa truyền `ram`; runtime từ chối. Không giả tham chiếu tệp hoặc lưu snapshot để đáp ứng AI-9 hiện hành.

Cần Core / Chờ Anh mới phát sinh: **C-P4-01/02/04** còn mở, chi tiết ở VIEC. Core phải ghim instance/phiên RAM và nguồn/quyền xuyên bước, thông báo vòng đời khi rảnh, điều phối Local đủ đoạn và thay phụ thuộc snapshot của AI-9; cách ly chứng cứ/kết quả tới chốt SDK/ACK còn quyền/còn hạn. R6/lead nối kho app vào hai handler và phối hợp cập nhật profile/công cụ/fixture cũ. C-P4-03/05 kế thừa. Không thêm câu hỏi nghiệp vụ. Chưa Core/Local/Office/Linux thật; Cloud tắt. PR: **chờ lead mở**.

## Bàn giao API nội bộ cho R6 / lead

- Hai constructor `ChuanBiAI` / `HauKiemAI` thêm `ram=app.kho_anh_xa_ram`; không tạo kho mới hoặc lấy từ dữ liệu việc. Adapter `tests/ho_tro_mask_r5.py` minh họa đúng kho R4, chỉ ngoài gói. `chay.py` chưa sửa vì không thuộc năm runtime được giao.
- `CongChuanBiAI`: `cau_hinh`, `kiem_ngan_sach`, `kiem_han`, `chi_so_doan(..., so_doan)` và `ban_giao(..., dau=DauHoSoRAM, yeu_cau=bytes)`. Core chọn mỗi chỉ số theo thứ tự, retry giữ đúng chỉ số/yêu cầu; Mask tự dựng nội dung từ RAM. Port không nhận map/gốc phụ trợ hoặc hồ sơ phục hồi. Yêu cầu Local có chính `tai_lieu` của đoạn theo contract, không gửi metadata chuyển tiếp cho model.
- `CongHauKiemAI.nhan_phan_hoi(..., dau, bam_dau_vao)` trả bytes JSON chuẩn `{phien_ban, ma_yeu_cau, phan_hoi:[{tra_loi_ai, nguon}]}`. Không tệp snapshot hoặc yêu cầu có bản gốc lặp trong tập này. `chung_thuc` đối chiếu băm/scope/nguồn hoàn tất từ sổ Core; Mask kiểm độc lập mọi phản hồi và yêu cầu RAM. Mỗi phản hồi giữ nguyên `chuyen_tiep`, bản giao cuối là phản hồi cuối, không bổ sung tham chiếu tập tệp.
- `ban_giao(chung_cu, ket_qua)` của hậu kiểm chỉ staging bản che/chứng cứ; không tự chứng minh phát hành hoặc quyền Cloud. Core phải đồng bộ ACK với lease/quyền/deadline C-P4-02. Mất ACK sau chốt không cache bản rõ hoặc chạy lại handler để tái dựng.
- Dữ liệu R6 cần dùng nằm dưới `handle.du_lieu`: `alias_nguyen_van`, `anh_xa_cuoi`, hồ sơ `ho_so_ai`, `dau_ho_so_ai`, giai đoạn `DA_HAU_KIEM`; vẫn cùng hạn tuyệt đối R4. Không đưa dictionary này ra port/chuyen_tiep/ngăn. Tên mới/đếm gặp cần C-P4-03, R5 chỉ dùng alias chính thức đã được Core xác minh.

## Kiểm bổ sung và giới hạn bằng chứng

- R5: **109 passed, 19,17 giây**, không skip/xfail (lượt trên bản mã cuối trước ba lệnh nghiệm thu). Ca gồm spy các port/ngăn ghi/upload/tệp/log/stderr, nguồn sai, nhiều đoạn/thiếu/trùng/đổi thứ tự, Unicode NFD/Cf/selector, span sai/bool/tiền/ngày/nghi vấn, sửa RAM/profile/prompt, bytes tệp đổi cùng ref/kích thước, quyền đổi trong RPC, TTL đang chạy/chờ, replay/restart/khác instance, Local chưa rõ và lỗi terminal.
- R3 + R5 ở lượt trước bổ sung chín ca R5 cuối: **124 passed, 17,29 giây**, mã 0. Không nhận đây là full suite. Hai ca primitive R3 vẫn đi cửa chặn lịch sử, không rơi về kho bản rõ. Gold R3 checkout CRLF đã đưa về bytes LF đúng băm đóng băng; không đổi nội dung/đáp án hoặc nới phép so.
- Lượt full đầu trước sửa cửa primitive R3/kiểm kê: **222 failed, 2193 passed, 4 xfailed cũ, 190 subtests passed, 140,43 giây, mã 1**. Các fixture snapshot cũ dừng trước kiểm an toàn phía sau; vì vậy số pass R5 không đủ để nhận mọi kiểm cũ đã được thực hiện trên RAM. Log lịch sử: `KET-QUA-KIEM-MASK-R5-DAU.txt`.
- Python chỉ bỏ tham chiếu RAM, không bảo đảm ghi đè vật lý mọi bản sao. Adapter không chứng minh ACL/ghim/egress/tokenizer/model thật hoặc giao dịch ACK xuyên mạng. Không phát biểu 0 lọt hoặc runtime thật đã đạt.

## Kết quả ba lệnh nghiệm thu cuối

| Lệnh | Kết quả thật | Mã thoát |
|---|---|---:|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT**; hai ví dụ thiếu quyền tin cậy `MASK_NGU_CANH_CHUA_XAC_MINH` | 1 |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **2256 passed, 216 failed, 4 xfailed cũ, 190 subtests passed, 0 skipped; 160,69 giây** | 1 |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT**, không tham chiếu cấm/bytecode/symlink trong gói | 0 |
| `git diff --check` | **ĐẠT**, chỉ cảnh báo chuyển LF→CRLF đối với tài liệu/gold ngoài gói | 0 |
| Kiểm kê `sql/kiem_ke.json` | **52/52 tệp**, bytes LF/SHA-256 khớp, trừ chính kiểm kê | 0 |

216 lỗi còn lại: `test_mask_2c_1.py` **18**, `test_mask_2c_2.py` **39**, `test_mask_2c_3.py` **133**, `test_mask_2c_4.py` **26**. Phần lớn dừng ở setup fixture chuẩn bị snapshot hoặc cửa `KhoHoSoAI` đã đóng; chưa chạy tới phần kiểm nguồn/span phía sau. Công cụ Local cũ còn đọc `ho_so` và dựng yêu cầu AI-9 theo snapshot nên chưa tương thích. **Không coi các lỗi này là test đã đạt chỉ vì đường cũ bị chặn.** Giữ nguyên toàn bộ test cũ, không thêm skip/xfail hoặc đổi đáp án/ngưỡng. Bốn xfail strict MASK-2b giữ lý do cũ “giới hạn quy tắc, nợ CAO”. R1/R2/R3/R4 và bộ R5 không còn failure trong lượt full cuối.

Lượt full trước ghim chỉ số đoạn theo `ma_luot`: **2255 passed, 216 failed, 4 xfailed, 190 subtests passed, 157,92 giây**; lúc đó diff phát hiện một dòng trống cuối VIEC, đã sửa. Sau đó bổ sung chặn cùng lượt đổi sang chỉ số hợp lệ khác và ca hồi quy tương ứng; chạy lại đủ ba lệnh như bảng. Không dùng số kiểm trước sửa làm số chốt. File số đo thời gian tiến trình (bao khởi động Python): [SO-DO-KIEM-MASK-R5.json](SO-DO-KIEM-MASK-R5.json).
