# Bàn giao sửa MASK-2b theo kiểm độc lập — 15/11/2026

**Kết luận: Đạt phạm vi sửa MASK-2b** — 0/32 ca t9 lọt, báo nhầm t10 2/41 (4,88%); đã kiểm bằng Core giả (CoreGia). CLI SDK chuẩn vẫn 0/2 vì thiếu nguồn quyền Core thật, chưa đạt nghiệm thu tích hợp. Bản này thay kết luận bàn giao 09:42 đã bị lead đánh giá **KHÔNG ĐẠT**. PR: **chờ lead mở**; không commit/push.

**Đã làm:** Thay bộ dò tên bằng chấm điểm có căn cứ; thêm 15 họ hiếm do lead cấp, danh sách âm tiết tên/đệm và cụm từ thông dụng tự soạn. Nhận danh xưng đầy đủ/viết tắt và tên Latin có ngữ cảnh; giữ số văn bản `số 01/2026`. Chỉ sửa **hai tệp runtime**: `ten_nguoi.py`, `che_van_ban.py`. Giữ nguyên API, `_chung/**`, `ngan.py`, `cau_hinh.py`, bốn tệp từ điển và nguồn cũ; không thêm dependency.

**Kết quả kiểm:** `kho_tri_thuc_sdk.thu` chuẩn → **0/2 ĐẠT, mã 1**, hai lỗi “Chưa xác minh được phiên và quyền xử lý yêu cầu.”; cổng thay thế `chay_demo.py` theo phiếu MASK-5 → **2/2 ĐẠT, mã 0**. `pytest e_mask/tests -q --basetemp=.pytest-tmp` → **717 passed, 190 subtests passed, 0 skipped, 43,68 giây, mã 0**; gồm **172 test mới** trong `test_mask_2b_rv.py` và toàn bộ 545 test cũ. `kiem_doc_lap.py` → **ĐẠT, mã 0**. [Đầu ra lệnh thực tế](KET-QUA-KIEM-MASK-2b.txt). Đã kiểm bằng Core giả (CoreGia); chưa chạy Linux hoặc Core thật, không gọi Cloud.

**Thời gian thực tế:** 09:47:00–10:15:57 ngày 15/11/2026 (UTC+07), **0.48 giờ thực tế**. Phiếu không có ước tính riêng cho MASK-2b/lượt sửa này; MASK-2 gốc là **3 giờ ước tính**, không coi là dự toán riêng đã duyệt cho lượt sửa.

**Lệch khỏi phiếu / quyết định tạm:** Không vượt phạm vi hai tệp runtime. CLI SDK chuẩn dùng cổng thay thế DEMO có quyền tin cậy ngoài gói theo phiếu MASK-5; không nới quyền để làm xanh CLI. Điểm ngữ cảnh hỗ trợ thêm động từ ngay sau tên và nhãn “tên người nước ngoài” để chặn cả hai ca Latin t9. Cho qua nghi vấn Latin chỉ khi cả cụm đã được che đầy đủ bằng một vùng công ty, nhằm giữ recall công ty/Cf cũ; không cho qua khi chỉ che prefix.

**Cần Core / Chờ Anh mới phát sinh:** Không. Các phụ thuộc ngăn/quyền, xác minh nguồn sinh `van_ban_da_che` trước Cloud giữ nguyên trong VIEC. Nợ tên nước ngoài thiếu ngữ cảnh, N.V. An và báo nhầm do lớp số/công ty còn ghi rõ bên dưới.

## Số đo độc lập trên t9/t10

Chuyển đủ **32 + 41 literal** DEMO thành pytest tham số hóa ở `tests/test_mask_2b_rv.py`; không thực thi script tham khảo hoặc import `h2`. Chuyển nguyên hai tệp `.py.txt` sang `LUU-TRU/rv_mask_2b/`; test đối chiếu lại literal bằng AST, đã so SHA-256 theo LF với blob HEAD. Không bỏ câu mập mờ khỏi mẫu số.

Đo thật trước khi sửa runtime và sau khi sửa bằng cùng CoreGia + NganBoNho + QuyenNganDemo, không danh mục người thật. Trạng thái lỗi chỉ được tính là chặn hợp lệ nếu cổng trả `MASK_DINH_DANH_CHUA_DAT`; test không chấp nhận lỗi kỹ thuật thay cho chặn. Phép dò lọt độc lập bỏ dấu, khoảng trắng, Cf và dấu câu; dấu chấm của `a. long`/`c. hoa` cũng được bỏ, tránh đếm thiếu hai ca này.

| Tập | Trước sửa | Sau sửa |
|---|---|---|
| t9, 30 ca tiếng Việt | 4 lọt, 21 chặn, 5 che | **0 lọt, 22 chặn, 8 che** |
| t9, 2 ca nước ngoài | 2 lọt | **0 lọt, 2 chặn** |
| t9 tổng, 32 ca | 6 lọt, 21 chặn, 5 che | **0 lọt, 24 chặn, 8 che** |
| t10, 41 câu | 28 chặn + 1 che thừa; **29/41 (70,73%)** báo nhầm | 2 chặn + 0 che thừa; **2/41 (4,88%)** |

Chênh với ghi chú 28/41 của lead: đo lại xác nhận **28/41 câu bị chặn (68,29%)**, đồng thời câu 1 bị che thừa `01/2026`; tính hợp hai nhóm là **29/41**. Các số nền được lưu trước khi sửa, không suy từ số test passed.

Hai câu t10 còn bị chặn, đều được giữ trong tỉ lệ 4,88%:

| Ca | Nguyên văn DEMO | Lý do |
|---|---|---|
| 2 | Công ty đã giao hàng tại hà nội và lê thị hoa đơn gốc. | `lê thị` đạt 4 điểm (họ + âm tiết tên), giữ nghi vấn khi gặp cụm `hoa đơn`; đồng thời lớp công ty cũ thấy “Công ty …”. Không phân định chắc đây là tên hay lỗi gõ hóa đơn nên chặn. |
| 7 | Mai sau khi nhận hóa đơn sẽ hạch toán vào tài khoản 331. | Bộ hậu kiểm nhãn `TAI_KHOAN` cũ còn coi **331** là giá trị tài khoản. Bộ tên không còn cảnh báo; chưa sửa bộ phân biệt tài khoản sổ cái/tài khoản ngân hàng trong lát này. |

Cả 39 câu còn lại giữ nguyên văn, `so_cho_thay=0`, tiền/ngày được kiểm thật. `số 01/2026` có test riêng, còn mã `01/2026/HD-DEMO` và tài khoản số dài vẫn bị che/chặn.

[Số đo máy đọc](SO-DO-MASK-2b.json): giữ các mốc cũ `truoc`/`sau`, bổ sung `rv_truoc`/`rv_sau` với từng ca, trạng thái, nhóm/vị trí/căn cứ chặn. Chạy lại mốc sau:

```text
.venv/Scripts/python e_mask/tests/test_mask_2b_rv.py --moc rv_sau
.venv/Scripts/python e_mask/tests/do_mask_2b.py --moc sau
```

Không chạy lại `rv_truoc` trên mã sau sửa để thay nền.

## Điểm, ngưỡng và căn cứ

| Tín hiệu | Điểm |
|---|---:|
| Họ chỉ thuộc `vn_surnames` hoặc 15 họ bổ sung của lead | +3 |
| Mỗi âm tiết đệm/tên thuộc danh sách tự soạn | +1, tối đa +2 |
| Có ít nhất 3 âm tiết và âm tiết thứ hai là đệm phổ biến | +1 |
| Mỗi âm tiết sau họ chưa biết, khi không có danh xưng | −1 |
| Tất cả âm tiết trong tên viết hoa đầu âm tiết | +4 |
| Danh xưng đầy đủ hoặc a./c./ô./b. ngay trước | +5 |
| Sau danh xưng là 1–3 âm tiết, không bắt đầu bằng họ | +3 |
| ký/gửi/với/giữa/bởi/của ngay trước | +1 |
| Ngoặc chức danh ngay sau | +1 |
| Hai+ từ Latin không dấu có ngữ cảnh, chưa có họ Việt hoặc có âm tiết lạ | +4; bắt buộc duyệt |
| Cụm từ ghép thông dụng/địa danh/allowlist hoặc viết tắt miễn | −8 |
| Khớp đúng một tên chính thức sau bỏ dấu | +8, giữ bí danh chính thức |

**Điểm ≥8 → che; 4–7 → `con_sot`, không phát hành; <4 → bỏ qua.** Tên dài, ranh giới chữ/số hỏng, trùng nhiều tên chính thức sau bỏ dấu và tên nước ngoài bị giới hạn điểm tối đa 7. Danh xưng rõ nhưng vướng cụm thường giữ tối thiểu 4 để duyệt; không miễn ngầm tên sau danh xưng. Mỗi điều chỉnh điểm có mã căn cứ nội bộ, cảnh báo chỉ chứa nhóm/vị trí/điểm/căn cứ, không chứa tên gốc.

Không sinh họ từ từ thông dụng hoặc từ tên/đệm. Danh sách họ mới lấy nguyên từ lệnh lead: **Ưng, Âu, Khúc, Lục, Thân, Ninh, Quan, Ông, Vi, Mẫn, Khổng, Bế, Nông, Lò, Hầu**; nguồn và SHA LF ở NGUON. Danh sách tên/đệm chỉ gồm âm tiết đơn tự soạn, không tổ hợp tên thật. Cụm ghép áp dụng ở mọi vị trí, kể cả “cáo” trong “báo cáo”, “lý” trong “thanh lý”, “tăng” trong “gia tăng”; gặp cụm nghiệp vụ phía sau thì kết thúc ứng viên trước cụm đó. “Phan” không bị miễn toàn cục vì “phân bổ”. Dấu của “có/cô”, “chủ/chú”, “chí/chị” được phân biệt; `chi phí`, `chu kỳ` không tự trở thành danh xưng không dấu.

Latin: sau các động từ nêu trên hoặc danh xưng → duyệt, có bổ sung động từ ký/gửi ngay sau và nhãn người nước ngoài. Vì vậy cả `john smith đã ký hợp đồng` và ca có nhãn `michael johnson` đều bị chặn. Chuỗi Latin không ngữ cảnh như tên đứng trần, tên nối gạch/nháy, cách viết không thuộc dạng đang dò vẫn là nợ; không tuyên bố phủ hết tên nước ngoài.

## Hồi quy và giới hạn còn lại

- Toàn bộ ca cũ Cf/selector, NFD/tab/NBSP/xuống dòng, bí danh, quyền/ngăn, tiền/ngày và bốn ví dụ MASK-2b vẫn đạt. Tên quá dài, che prefix, trùng bỏ dấu và bí danh tạm chưa duyệt vẫn chặn; hậu kiểm mới độc lập detector cũ.
- Đo lại 14 mẫu cũ: 1/14 che thừa chữ DEMO; 30 câu cũ bổ sung: ca 15 ngày ISO bị lớp số/ngày chặn và ca 30 che thừa DEMO, tổng 2/30. Không tăng trên hai tập này; không bỏ ca lỗi nền.
- Hai báo nhầm t10 nêu trên vẫn còn. Các lớp dò công ty/số cũ tiếp tục độc lập, có thể còn che thừa với cách viết khác ngoài tập đo; bộ từ ghép tên không thay bộ phân loại mọi định danh.
- N.V. An, tên/âm tiết ngoài danh sách không danh xưng, tên trùng hẳn địa danh/cụm thường và ngữ cảnh ngoài quy tắc hữu hạn chưa có chứng minh recall. Chỉ có số đo DEMO, không suy ra tỉ lệ vận hành hoặc đủ điều kiện bật Cloud.

Môi trường: Windows x64, Python 3.13.14, pytest 9.1.1 từ môi trường sẵn có; `.venv` dùng SDK 2.0.0 cài offline từ wheel repo. SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Mọi lệnh đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; gói không có mã biên dịch. Không sửa Core, không lưu dữ liệu runtime xuống đĩa.
