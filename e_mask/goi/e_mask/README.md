# e_mask — Che định danh văn bản

MASK-S22, 15/11/2026: bản gói 1.3.0, SDK 2.2.0. Đã kiểm bằng Core giả (CoreGia). Cấu hình khai bằng `cau_hinh.schema.json`, đọc bản chụp `viec.cau_hinh`; hiện chưa có trường cấu hình engine, giá trị hợp lệ là `{}`. Prompt/model Local thuộc module/quy trình và vẫn do cổng Core tin cậy cấp. Không đưa chúng vào cấu hình Mask hoặc tự cấp quyền từ cấu hình. Không cần callback đổi cấu hình vì engine chưa có đệm phụ thuộc cấu hình.

Theo chỉ dẫn Lead riêng MASK-S22 và CĐ-36, kho bí danh giữ RAM qua cổng hiện tại (`app.kho_bi_danh_ram`), tách khỏi `app.ngan`/`viec.ngan` của SDK. Khởi động lại mất dữ liệu. Chưa chuyển kho bí danh sang Core; thiết kế mở che theo CĐ-36 thuộc MASK-P3, không có đường giải mã mới. Không khai bảng ngăn hoặc migration cho kho này. Màn duyệt giữ nguyên để kiểm hồi quy với KttCore giả; chưa nối ngăn Core thật. Cloud giữ tắt.

Từ MASK-2c-2 (1.1.0), gói có `mask.chuan_bi_ai_cuc_bo@1`: chạy nguyên lớp quy tắc, giữ snapshot nội bộ ở Core, trả `yeu_cau_ai` cho đoạn gốc đầu tiên và bắt buộc Local. Core điều phối các đoạn tiếp theo từ kế hoạch đã ghim; engine không thực hiện lượt AI. Hai năng lực che/mở cũ giữ nguyên loại trả. MASK-2c-3 đã bổ sung `mask.hau_kiem_ai_cuc_bo@1` để hậu kiểm Local và che thêm; Cloud tiếp tục tắt.

Tích hợp cần `tao_app(ngan=..., quyen=..., cong_chuan_bi_ai=...)`. `CongChuanBiAI` trong `chuan_bi_ai.py` là **port nội bộ đề nghị, chưa có transport tương ứng trong SDK 2.2.0**: Core cấp prompt của module/quy trình gồm chỉ dẫn profile, mã/phiên bản và model; đo budget bằng tokenizer thực cho cả prompt/khuôn/từng đoạn/đầu ra; giữ deadline gốc; lưu/đọc snapshot với ACL/lease và ghim bàn giao. Kho RAM cần bảng `chuan_bi_ai` theo `KHAI_NGAN_CHUAN_BI_AI`; chỉ mục chỉ chứa băm/tham chiếu. Snapshot bao nguyên `HoSoAI` MASK-2c-1 cùng kết quả quy tắc, prompt, khuôn, profile và biên nhận; đọc bằng `doc_snapshot`. Không tự nối các bảng RAM này vào ngăn Core.

Đoạn tối đa 8.000 code point, overlap 512 mỗi phía được làm tròn vào biên khoảng trắng/câu an toàn, giữ ít nhất 300 khi còn đủ nguồn; vùng chính phủ đủ gốc, tối đa 128 đoạn. Không cắt từ/NFD/Cf hoặc vượt 500.000. Span nhận diện dài hơn 300 thì từ chối. `tai_lieu` giữ nguyên gốc kể cả NFD/Cf; metadata chuyển tiếp chỉ có mã opaque, tham chiếu, băm và chỉ số. Thiếu cổng/quyền/snapshot/budget/deadline thì từ chối. Các số token trong adapter DEMO là fixture, chưa là số đo model thật hoặc bằng chứng chạy dài.

MASK-3b, MASK-4, MASK-5, MASK-6 đã được kiểm bằng Core giả (CoreGia) với port quyền DEMO được tiêm ngoài gói. Hai năng lực che/mở che văn bản đã có handler; phần tệp Word/Excel/PDF chưa được công bố. Không gọi Cloud hoặc engine khác.

Mọi trạng thái đi qua `Ngan`: định danh, bí danh tạm, danh sách chờ, mã yêu cầu, dấu gặp/chống trùng. Chốt trong một lô có CAS chung; xung đột trả `MASK_XUNG_DOT`, thử lại được. MASK-S22 chủ động giữ RAM theo chỉ dẫn Lead, không tự chọn ngăn SDK khi cổng đó tồn tại. Khởi động lại mất dữ liệu RAM. Hai tệp `kho_tam.py`, `cau_hinh_may.py` cùng schema cấu hình cũ đã chuyển nguyên nội dung sang `e_mask/LUU-TRU/mask_truoc_ngan/`, nằm ngoài gói. Các test lịch sử nạp chúng qua helper riêng.

Trước khi phát hiện, bản dò bỏ mọi ký tự Unicode nhóm `Cf` và variation selector (kể cả ngoài BMP), rồi chuẩn hóa NFC. Ánh xạ khoảng ký tự về nguyên văn bảo đảm che cả ký tự vô hình chen giữa định danh; tab, NBSP và dấu xuống dòng vẫn được xét khi dò tên. Các ký tự vô hình ngoài đoạn đã che cũng bị bỏ. Phong bì từ chối kết quả còn ký tự này; không ánh xạ được thì trả `MASK_DAU_VAO`. Tiền/ngày được đối chiếu thực tế sau khi bỏ ký tự vô hình ở cả hai bản, không đổi chữ số hay giá trị.

Bí danh **tạm** chỉ mở bằng đúng `ma_yeu_cau` đã sinh ra nó, kể cả bí danh chưa duyệt mang tiền tố khác `MASKTAM` hoặc mã tạm cũ sau khi duyệt. Hai yêu cầu độc lập che cùng cụm chưa duyệt nhận hai bí danh tạm khác nhau; danh sách chờ vẫn gộp cụm và đếm gặp một lần cho mỗi yêu cầu. Không nhận tham chiếu bí danh tạm của yêu cầu khác. Khi mở bằng mã khác, giữ nguyên alias, liệt kê vị trí, trả `mo_day_du=false` và giữ yêu cầu đang xử lý. Bí danh **chính thức đã duyệt** ổn định giữa các tài liệu, vẫn mở được trong cùng pháp nhân sau kiểm quyền Core, kể cả yêu cầu chưa từng dùng mã đó. Công ty đã duyệt với mã Junsky được che thành `[[<mã Junsky>]]`.

Lỗi bất ngờ của ngăn/port được bọc thành `LoiNghiepVu` với câu cố định và bỏ chuỗi nguyên nhân, trước khi SDK có thể in traceback. Kiểm hồi quy bắt cả stdout/stderr của che, mở che, duyệt và các đường lỗi; giữ nguyên tín hiệu hủy và chốt chưa rõ.

Nguồn quyền/mã yêu cầu phải do Core tin cậy cấp. `tao_app(ngan=..., quyen=...)` dành cho bên tích hợp; không nhận port hay danh tính từ dữ liệu việc. Thiếu nguồn quyền, engine trả `MASK_NGU_CANH_CHUA_XAC_MINH`. CLI SDK 2.2.0 chưa có cửa tiêm nguồn này nên hai ví dụ vẫn bị chặn, không báo thành công giả; đây là điều kiện nghiệm thu chưa đạt, đã ghi Cần Core trong VIEC.

Kiểm từ thư mục repo sau cài `requirements.lock` offline:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
.venv/Scripts/python -m pytest e_mask/tests -q --basetemp=.pytest-tmp
.venv/Scripts/python e_mask/tests/kiem_doc_lap.py
```

Linux dùng Python trong môi trường tương ứng. Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` trước khi kiểm gói. Lệnh đầu hiện trả mã 1 vì thiếu quyền/mã yêu cầu tin cậy; không dùng runner khác thay tiêu chí này. `tests/chay_demo.py` chỉ còn là fixture hồi quy có quyền ngoài gói, không là kết quả nghiệm thu CLI chuẩn.

Bốn từ điển sạch đã được lead cấp theo lệnh giao 15/11, nằm tại `e_mask/tu_dien/`; kiểm SHA khi nạp. Thiếu/sai SHA bị chặn. Bộ đọc cấu hình tạm và bản khai dự kiến đã chuyển nguyên byte vào `e_mask/LUU-TRU/sdk_truoc_2_2/`. Bỏ test so băm mẫu ngăn/cấu hình; giữ các ca hành vi và so băm từ điển sau đổi CRLF thành LF. `ngan.py` chỉ giữ cổng kho RAM theo ngoại lệ Lead, không có bảng cấu hình; khai báo RAM nằm trong `kho_ngan.py`.

Trần văn bản 500.000 ký tự, danh sách đã biết 500 mục, giá trị 300 ký tự, nhóm 20 ký tự. Không cắt ngầm. Lô ngăn hiện tối đa 100 lệnh: nếu toàn bộ thay đổi vượt mức này, từ chối cả việc; cần Core hỗ trợ giao dịch lớn để xử lý nhiều cụm. JSON tệp đầu vào tạm có trần kỹ thuật 4 MiB, chưa phải trần tệp nghiệp vụ đã được Anh chốt. Không dùng trần đầu vào làm trần đầu ra.

Màn `ui/duyet_dinh_danh.js` gọi `KttCore.engine("e_mask").ngan`; Core phải kiểm `admin_core` khi đọc/ghi và nạp màn. Duyệt/từ chối giữ bí danh tạm còn tham chiếu; dọn dùng cùng CAS với che/mở che. Màn đã kiểm bằng Node/KttCore giả, chưa kiểm trong trình duyệt Core thật. Khai báo cũ đã lưu trữ; màn này chưa hoạt động trên ngăn Core 2.2.0, chờ MASK-P3 thiết kế lại.

MASK-2b dò họ trong `vn_surnames.txt` theo sau bởi 1–3 âm tiết chữ Việt, không phụ thuộc hoa thường/dấu. Danh xưng hoặc đúng một tên chính thức đã duyệt cho phép che bằng bí danh; biến thể bỏ dấu dùng lại bí danh chính thức. Ứng viên chưa đủ tin cậy đưa vào `con_sot` với lý do “nghi tên người viết thường”; không phát hành `van_ban_da_che`. “và” và ngoặc chức danh củng cố nghi vấn, chưa tự cho phép phát hành. Bí danh tạm có sẵn không thay cho tên đã duyệt. Tên dài hoặc phần đuôi chưa che vẫn chặn; lỗi bộ dò cũng chặn.

Bộ dò dùng lại allowlist/địa danh/viết tắt và các cụm thông dụng trùng họ khai tường minh trong `ten_nguoi.py`, ví dụ “lê thê”, “lý do”, “nghiệm thu”. Ngoại lệ so theo cả cụm; danh xưng/tên chính thức ưu tiên hơn ngoại lệ. Họ ngoài từ điển, tên viết tắt như N.V. An và tên trùng hẳn địa danh/cụm miễn còn là giới hạn heuristic. Các bộ dò chữ hoa đã có vẫn được giữ; chưa có bằng chứng nhận diện mọi tên. Không dùng test DEMO để xác nhận đủ điều kiện bật Cloud.

Đo báo nhầm và đọc các mẫu có nguồn: `.venv/Scripts/python e_mask/tests/do_mask_2b.py --moc sau`, chạy từ repo; số đo ở `e_mask/docs/SO-DO-MASK-2b.json`. Trên 14 đoạn/câu cũ: 0 chặn nhầm, 1 che thừa; 30 câu bổ sung: 1 chặn nhầm, 1 che thừa, đều đã có ở bản nền. 29 câu nghiệp vụ không bị chặn được kiểm riêng. Xem `NGUON.md` và báo cáo MASK-2b trong `e_mask/docs/`. Chỉ dùng thư viện chuẩn và SDK 2.2.0.

Công cụ Local ngoài gói (`cong-cu/thu_mask_local_ai_that.py`) dùng `CoreGia.dat_cau_hinh` cho Hỏi AI 2.2.0 và `xem_ngan` xem kết quả discovery; không còn ghi bảng cấu hình ngăn. Kiểm deadline phía cha dùng checkpoint và tín hiệu hết hạn xác định; các test Local HTTP giả và child CLI khác vẫn chạy thật.
