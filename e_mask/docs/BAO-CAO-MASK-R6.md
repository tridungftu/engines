# MASK-R6 — mở che văn bản/AI từ RAM, 16/11/2026

**Kết luận: Chưa đạt nghiệm thu chung — đã triển khai trong bốn runtime; còn cửa Core và kiểm kê gói ngoài closure.** PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia), chưa Core/Local/Office/Linux thật.

**Đã làm:**

- Đúng bốn tệp bảng MASK-P4 §4: `e_mask/mo_che_ram.py`, `e_mask/che_van_ban.py`, `e_mask/chay.py`, `e_mask/phong_bi.py`. Nối hai handler R5 vào chính kho R4 của app; không dựng kho RAM lịch sử hoặc nhận map từ payload. Bước che quy tắc riêng giữ cửa chặn chất lượng R3, chuỗi Local dùng R5. Không thay `nhan/tra`, manifest/schema chung, Core/SDK, dependency hoặc nguồn cũ; không commit/push.
- Mã chuỗi do port quyền xác minh trước parse; payload phải khớp. R4 kiểm scope/instance/phiên RAM, TTL/deadline, một chủ và tiêu thụ một lần. Map mở chỉ từ phép thay thực sự của `anh_xa_cuoi` ở giai đoạn `DA_HAU_KIEM`, đối chiếu bản đồ alias trong RAM. Không đọc ngăn, tải nguồn/snapshot hoặc tra danh mục để gỡ; alias ngoài yêu cầu bị chặn.
- Mở `tra_loi`, mọi giá trị chuỗi lồng `du_lieu`, câu trích và trích dẫn lồng; giữ khóa, số/tiền/ngày/boolean/null, metadata nguồn/model/chuyển tiếp và nội dung AI mới. Giữ nguyên NFD/Cf/khoảng trắng của nguyên văn đã ghim; case/space mềm chỉ khi duy nhất. Cùng alias nhiều nguyên văn, alias hỏng/thiếu/lạ hoặc mất RAM trả lỗi Việt cố định, không kết quả một phần.
- Khi thay chữ, hạ `kiem_trich_dan.dat` và `trang_thai`, thêm yêu cầu kiểm lại. Tái tính vị trí trên gốc đang RAM bằng map/offset đã ghim hoặc câu xuất hiện duy nhất; không xác định được thì tọa độ `null`, không giữ offset bản che làm chứng cứ. Đây là dữ liệu JSON trong bộ M, không đổi schema `tra_loi_ai` chung hoặc quảng bá thành kết quả đã kiểm nguyên văn.
- `dong_viec=false` cũ vẫn tiêu thụ map, trả `DA_DONG`; thông báo chuyển quy trình qua tiến độ SDK (dưới 200 ký tự) và cảnh báo trong AI. Map dọn sau thành công/lỗi/hủy/ChuaRo; callback/timer R4 giữ nguyên. Ngắt cell đệ quy và dọn map phụ trong `finally`, kiểm bằng weakref khi tắt GC; không tuyên bố ghi đè vật lý mọi bản sao RAM của Python.
- Cửa bàn giao cuối là protocol đề nghị trong R6, chưa có binding SDK: Core giữ quyền/lease/deadline và kết quả chưa phát hành, chỉ phát hành sau R4 tiêu thụ. Mất ACK sau nhận trả `ChuaRo` với mã tương quan cố định từ mã lượt Core; Core có thể giao lại kết quả cuối đã nhận đúng quyền, engine không cache bản rõ hoặc chạy mở lại. Không Cloud, kênh mạng riêng hoặc engine-to-engine.

**Kết quả kiểm:** [lệnh/kết quả thật](KET-QUA-KIEM-MASK-R6.txt), [full pytest sau sửa cuối](KET-QUA-KIEM-MASK-R6-PYTEST.txt). Không dùng focused hoặc bản sao gói thay kết quả gói gốc.

| Lệnh / phép kiểm | Kết quả thật |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**, hai DEMO thiếu quyền Core (`MASK_NGU_CANH_CHUA_XAC_MINH`). |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **2646 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests passed, 0 skipped; 390,44 giây; mã 1**. Failure duy nhất `test_kiem_ke_day_du_bytes_va_sha_tung_tep`, không bỏ/deselect hoặc sửa bộ kiểm. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **Mã 1**, duy nhất kiểm kê gói chưa khớp; không tham chiếu cấm/bytecode/symlink phát sinh. |
| R6 riêng sau sửa cuối | **124 passed, 0 failed/skip/xfail, 2,19 giây, mã 0**, gồm bốn ca weakref/GC tắt. CoreGia bổ sung alias tạm + Junsky case/space mềm **2/2 ĐẠT**. |
| Kiểm kê đề nghị ngoài gói / bản sao | **53/53** tệp đúng bytes/SHA sau sửa cuối. Bản sao chỉ thay kiểm kê qua bộ kiểm độc lập nguyên trạng **ĐẠT, mã 0**; gói gốc vẫn chưa đạt. |
| `git diff --check` | **Mã 0**. |

Bốn xfailed MASK-2b giữ lý do cũ **“giới hạn quy tắc, nợ CAO”**. Lượt full đầu **2582 passed, 59 failed, 4 xfailed, 190 subtests; 390,94 giây**; lượt full trước sửa GC **2642 passed, 1 failed kiểm kê, 4 xfailed, 190 subtests; 377,00 giây**. Giữ log các lượt trong docs, không dùng chúng thay lượt full chốt trên.

**Thời gian thực tế:** **00:52:00–01:41:32 ngày 16/11/2026 (UTC+07), 0,83 giờ**, tại mốc chốt kiểm/báo cáo; bắt đầu theo lead. Phiếu **4–6 giờ ƯỚC TÍNH**, độ khó `kho`.

**Lệch khỏi phiếu / quyết định tạm đã dùng:**

- Không thêm runtime thứ năm. `sql/kiem_ke.json` cần đổi theo toàn bộ bytes gói nhưng ngoài bốn tệp được phép; giữ nguyên gói, cung cấp `KIEM-KE-MASK-R6-DE-NGHI.json` (53 tệp) để lead áp sau khi gộp. Bản sao chỉ thay kiểm kê đã qua bộ kiểm độc lập, không biến kết quả gói gốc thành đạt.
- Áp trần bảo thủ **500.000 ký tự tổng nội dung sau mở** để chặn phình RAM trước ghép kết quả; vượt thì từ chối, không cắt ngầm. Đây là giới hạn kỹ thuật thử nghiệm của R6, chưa là bằng chứng budget production/Local hoặc quyết định mới của Anh.
- Giữ vỏ và hàm mở che cũ trong hai fixture ngoài gói, mười tệp test/công cụ lịch sử chỉ đổi import/điểm gọi tương ứng; không dùng các ca tra ngược/partial/giữ map cũ làm bằng chứng R6. Fixture R5 chỉ seed catalogue qua ngăn SDK, gọi handler runtime thật; ca âm snapshot dùng port chỉ có luu/doc thay vì adapter RAM hiện hành. Giữ assertion an toàn, ngưỡng và bốn xfailed cũ, không thêm skip/xfail.
- Gold R3 được khôi phục **nguyên blob Git LF**, SHA-256 `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`; không đổi dữ liệu/hash/gold. Lượt full đầu có 57 lỗi điểm gọi mở lịch sử, một lỗi CRLF gold và một lỗi kiểm kê; log giữ nguyên để truy vết.

**Cần Core / Chờ Anh mới phát sinh:**

- **C-P4-02:** binding chung cho `CongMoCheRAM.ban_giao_cuoi` và quyền của R4. Context manager giữ scope/instance/lease/deadline cùng đầu vào bất biến, không nuốt ngoại lệ; nhận bytes kết quả vào vùng chưa phát hành, chốt sau tiêu thụ RAM, hủy/lỗi/quá hạn thì bỏ vùng chờ. Tín hiệu toàn chuỗi phải tới Mask khi rảnh, kể cả khi việc bị hủy trước SDK gọi handler. Không gọi mở lại sau tiêu thụ/restart; mất ACK bàn giao cuối dùng ChuaRo và Core quản kết quả đã tiếp nhận đúng quyền. Port này chưa là API SDK 2.2.0 đã có.
- **C-P4-05:** quyền đọc JSON mẫu 3 chỉ cho đầu vào việc hiện tại, không tải nguồn/snapshot để khôi phục; cách ly bàn giao khỏi module/người khác và Cloud; không log payload/bản rõ/map/traceback/local variables hoặc crash dump. Cần xác nhận trần bytes/413/budget RAM/CPU/thời gian thật, sự đồng bộ tín hiệu hủy với bàn giao và hành vi SDK mất mọi ACK sau handler. Kiểm CoreGia không chứng minh ACL hoặc độ bền Core thật.
- Kế thừa **C-P4-01/03/04** và **C-MS22-01**: ghim tiến trình, kho bí mật/duy nhất và Local đủ đoạn; CLI DEMO chuẩn chưa có quyền. Giữ phối hợp AI-13 về metadata RAM của AI-9, không sửa consumer/SDK để giả đã nối. Không có câu nghiệp vụ mới chờ Anh chọn lại.
