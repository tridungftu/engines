# Phiếu kế hoạch tổng thể — Hóa đơn điện tử

| BẢNG TÓM TẮT | Nội dung để Anh quyết định |
|---|---|
| Khi xong, Anh thấy và làm được | Nộp hóa đơn XML DEMO, xem kết quả đọc và vấn đề; thử ZIP/bảng kê sau khi duyệt mẫu; xem hàng việc, kết quả tải giả theo tháng, lỗi từng nhóm và file đầu ra. Giữ đúng số hóa đơn, tiền, thuế và dấu vết nguồn; tài khoản khác pháp nhân không xem được. |
| Tổng số lát còn lại | **9 lát**, gồm phần nguồn/ghim còn thiếu của kế hoạch đóng gói và các lát nối vận hành DEMO còn thiếu. Không tính lại phần đã gộp. |
| Tổng giờ ước còn lại | **29 giờ công**, gồm kiểm nhanh/review, kiểm Windows và bài tổng thể 2 giờ; chưa gồm chờ giấy phép/tài khoản, sửa lỗi chưa biết và cổng dùng chung. Không phải thời gian lịch. |
| Việc chờ Anh | Quyền dùng nguồn Node; mẫu dữ liệu ZIP/bảng kê và phạm vi năng lực công bố; tài khoản Windows có màn hình; xác nhận cách kiểm kê gói đang áp tạm. Tải từ cổng thuế thật vẫn cần lệnh riêng. |
| Trạng thái phiếu | **Đề xuất, chờ Anh đồng ý trước khi mở lát mới** theo CD-091 sửa 10:02; số lát chạy đồng thời chốt lúc triển khai. |

## 1. Căn cứ và phạm vi

Theo [CD-091 và sửa 10:02](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md), mục 0b `CLAUDE.md` tại thư mục chính, [G3-GOI §5.2, §6.1–6.5](KE-HOACH-G3-GOI.md), [G2–G3, hàng HD](../g2/KE-HOACH-LAT-G2-G3.md), [bản giao hóa đơn trong ENGINE-2](../engine/GIAO-ENGINE-2.md). Bản `CLAUDE.md` đã commit trong worktree chưa có mục 0b; đã đọc bản thư mục chính, không sửa tệp đó.

Lịch sử gộp được kiểm bằng `git log --oneline hop-nhat-20261023` và lọc “gộp” không phân biệt hoa/thường, mốc cố định **`2f6a05a9`** ngày 06/11/2026; HEAD worktree lúc bắt đầu `462975b4`. Không thấy gộp không có nghĩa chưa có mã ở nhánh khác; chỉ nghĩa chưa có bằng chứng nhập nhánh hợp nhất tại mốc này. Số giờ là ước lượng của phiếu, mã ghi “đề xuất” chưa phải lát đã giao.

Mốc trọn vẹn của phiếu là **vận hành qua Core bằng DEMO**, gồm phiên trình duyệt thật trên nguồn thuế giả. Nó không chứng minh đã gọi cổng thuế thật. Việc đọc XML, việc tải và việc nhận vào nghiệp vụ kế toán là ba kết quả khác nhau; tải xong không tự coi là đã đọc/đã hạch toán.

## 2. Hiện trạng đã đối chiếu thật

| Việc đã có / còn thiếu | Bằng chứng git / cột phụ kỹ thuật |
|---|---|
| Đã gộp bộ đọc XML/ZIP sang mẫu hóa đơn | HD-1 — `8c0d6293`; không suy là báo cáo ZIP đã có schema công bố đầy đủ. |
| Đã gộp tải với cổng giả, xuất bảng kê, khung chạy | HD-2a — `d67ce1c5`; HD-2B — `6242af70`; HD-3A — `1dfa116e`. |
| Đã gộp khung phiên có màn hình và kiểm vòng đời phiên bằng seam DEMO | HD-2c — `c4109552`; HD-3b — `0d4e0914`. Chưa thay bằng chứng tài khoản/ACL/Chromium thật. |
| Đã gộp đóng gói, bộ đọc nội bộ, ánh xạ trạng thái và lớp phiên dùng SDK | G3-GOI-21 — `8bbecffe`; 22 — `ce6cba38`; 23 — `f9736561`; 24 — `8c410cee`. |
| Chưa gộp nguồn Node sạch và ghim cuối | G3-GOI-25/26 chưa có dòng gộp tại mốc khảo sát; §6.4 giữ chờ giấy phép/nguồn gốc. Khung tải nguồn thật còn chưa kiểm. |
| Khai báo năng lực hiện công bố chỉ đọc XML | Manifest hiện có `hoa_don.doc_xml@1`; ZIP/bảng kê/tải không tự thành năng lực đã kiểm. |
| Không có lát hóa đơn điện tử đang chạy được CD-091 nêu tại 10:25 | LHD-C1/C2/E2 đang làm là **loại hợp đồng** của trích xuất, không phải hóa đơn điện tử. Không cộng các lát LHD vào phiếu này. |

Đã đối chiếu bảng 40 lát: phần riêng hóa đơn là 21–26, trong đó 21–24 gộp, 25–26 còn lại. Phần chung 01–05, 10–14 đã có gộp; 13/13b chỉ nối kiểm kê, chưa bật thư mục gói thật. Các nợ chung 13c/34/38/39/40b và ghim của engine khác được kê ở [phiếu chuỗi](PHIEU-ENGINE-chuoi.md), không làm lại trong phiếu này.

## 3. Đủ mọi lát còn lại và thứ tự

**Loại kiểm:** T = test thuần nhanh DEMO/mock + review chéo Codex. N = T + PG đầy đủ cho phần liên quan do lead chạy + Opus khi đụng CSDL/quyền/tiền/bí mật/xóa; thêm Windows thật nếu áp dụng. PG kiểm cửa Core, không thay kiểm tài khoản/phiên trình duyệt. Không tạo CSDL cho phần chỉ thuần. Hằng ngày chạy bài đầu–cuối; PG toàn bộ một lần/đêm. So mã lỗi/skip với nền hiện hành, bộ mới đo trước/sau cùng môi trường; ghi phút kiểm từng lát riêng.

| Thứ tự | Việc bằng lời dễ hiểu | Phụ thuộc / điều kiện mở | Giờ | Kiểm và lý do | Cột phụ: mã lát |
|---|---|---|---:|---|---|
| 1 | Mang đúng phần nguồn xuất bảng kê vào gói, bỏ đường dẫn cố định tới máy phát triển, chốt thư viện Node | Anh xác nhận quyền dùng; lead kiểm nguồn gốc/tập tệp sạch trước giao | 5 | N — thuật toán/bảng kê tiền, không được đổi số; thuế giả | G3-GOI-25 |
| 2, cùng màn mẫu ở 5 | Nối nguồn job/portal thật vào khung phiên; cấp mật khẩu DEMO qua bộ nhớ, profile riêng mỗi pháp nhân/phiên | 1; bằng chứng nguồn có các điểm nối cần dùng, Anh cho phép tài khoản | 4 | N — bí mật/quyền/xóa profile; Windows/Chromium thật, nguồn thuế giả | HD-NOI-PHIEN, đề xuất; không làm lại HD-2c giả |
| 3 | Hoàn thiện mẫu kết quả ZIP/bảng kê/tải theo dữ liệu nguồn, rồi mới công bố năng lực nào đủ bằng chứng | Anh duyệt phần schema còn thiếu; 1–2; tái dùng mẫu chung đã có | 3 | N — tiền/bí mật; contract vào/ra, không công bố capability giả | HD-CONG-BO, đề xuất |
| 4 | Core nhận tệp/kỳ tải, giao đúng engine, lưu tham chiếu và kết quả đúng pháp nhân, không nhận trùng | 3; quyền nguồn theo pháp nhân; đường công bố qua Core hiện có | 3 | N — CSDL/quyền/tiền; không SQL sang module khác | HD-NOI-CORE, đề xuất |
| 5, bắt đầu mẫu cùng 2 | Màn Đọc hóa đơn/Thử tải có chọn tháng, tiến độ, lỗi nhóm, tải file kết quả; mẫu có nhãn trước rồi nối API | 3 cho tên trường, 4 cho bản nối; vị trí màn Anh chốt | 4 | N — quyền xem hóa đơn/tiền và chống lộ kết quả | HD-GIAO-DIEN, đề xuất |
| 6 | Kiểm tiền, số hóa đơn, bảng kê/PDF khớp nguồn; ZIP lỗi một phần không thành “đầy đủ” | 1, 3–5; dùng bộ hóa đơn DEMO có đáp án | 3 | N — tiền; XML strict, số 0 đầu, Decimal, hash và coverage | HD-SO-TIEN, đề xuất |
| 7 | Chứng minh phiên Windows riêng, CAPTCHA tại màn hình máy chủ, hết phiên không dùng lại profile; lỗi dọn phải chặn phiên mới | 2, 4–5; Anh cho phép Windows; không đưa bí mật vào env/args/file | 3 | N — quyền/bí mật/xóa profile; chỉ nơi thử DEMO đã cấp | HD-WIN, đề xuất phần thật HD-3b còn thiếu |
| 8 | Chốt bản gói/phụ thuộc/mã băm cuối, hướng dẫn và cách quay về bản đã ghim | 1–3, 6–7; SDK cuối G3-GOI-34 | 2 | T — gói độc lập/lock, không đổi thuật toán | G3-GOI-26 |
| 9 | Anh thử trọn luồng XML, ZIP, bảng kê và tải giả; lưu ảnh/kết luận có hoặc không đủ điều kiện | 5–8 và cổng dùng chung; nếu thiếu schema chỉ nghiệm thu XML một phần | 2 | N — bài tổng thể tiền/quyền/bí mật | HD-TONG, đề xuất |
| | **Tổng 9 lát còn lại** | | **29** | | |

**Không cộng trùng:** 13c nối gói thật phải giải quyết đủ §6.1/6.5; 34 chốt SDK, alias lớp giữ hash và bỏ helper ngoài SDK, kèm 34b dự phòng đường AI nếu thiếu; 38 kiểm độc lập; 39 kiểm registry/quyền/phiên bản/giao diện; 40b bổ sung tài liệu còn nợ. Giờ chung chỉ tính trong phiếu chuỗi. Lát 38 còn chờ ghim AI/OCR/Mask/trích, nên 29 giờ không bảo đảm ngày hoàn tất khi các engine kia còn chờ. §6.2 đo trích không thuộc hóa đơn. §6.3 giữ nguyên danh tính các lớp và dấu vết số liệu, không ghim wheel 1.4.1 ứng viên. §6.4 cấm mang nguồn Node vào gói khi chưa rõ quyền phân phối.

Nếu khảo sát phát hiện phải sửa nguồn ngoài phạm vi hoặc thiếu điểm nối portal, dừng riêng lát 1/2 và báo lead mở phạm vi sau duyệt; ước 29 giờ phải điều chỉnh có giải thích, không tự viết bộ tải/parser thứ hai. Gọi thuế thật là mốc sau, chưa có giờ cam kết vì chưa được phép và chưa rõ môi trường; không dùng nó làm điều kiện giả để báo DEMO đạt.

## 4. Việc chờ Anh

| Việc cần Anh chốt | ☑ Phương án đề xuất | Phương án khác / điều kiện | Cột phụ |
|---|---|---|---|
| Giấy phép nguồn xuất bảng kê và nguồn portal | ☑ Anh xác nhận quyền chép tập nguồn nội bộ tối thiểu; lead ghi đúng nguồn, bản và mã băm trước gộp | Chưa xác nhận thì giữ Chờ, tiếp tục màn DEMO/thiết kế độc lập | G3-GOI-25/26, §6.4; không tự đặt LICENSE |
| Mẫu trao đổi còn thiếu cho ZIP/bảng kê | ☑ Duyệt sau khi lead trình mẫu DEMO có từng tệp, lỗi từng nhóm, phạm vi tải được và tham chiếu nguồn; XML hiện có giữ tương thích | Mốc đầu chỉ XML, các năng lực khác tiếp tục chờ, không gắn nhãn ready | `hoa_don.doc_zip_bang_ke@1`, `hoa_don.tai_cong_thue@1` mới là tên đề xuất trong bản giao |
| Tài khoản và màn hình Windows | ☑ Tài khoản riêng cho tải hóa đơn, khác Core/module/engine khác; CAPTCHA gõ tại máy chủ; profile riêng mỗi pháp nhân/phiên | Hoãn đổi Windows thì chỉ báo kiểm giả, không nghiệm thu vận hành thật | CD-038 câu 2A/3A; không xin mật khẩu qua chat |
| Quyền và vị trí màn | ☑ Thử trong màn nghiệp vụ hóa đơn dùng Core, chỉ người được phép mới chọn nguồn/xem file; Quản lý engine chỉ xem tình trạng và cấu hình | Anh chọn màn thử riêng trên Core DEMO nếu module hóa đơn chưa nối; phải ghi rõ chưa nghiệm thu module | HD-GIAO-DIEN; không để mã kỹ thuật ở màn chính |
| Cách kiểm kê đang áp tạm | ☑ Giữ đường kiểm kê riêng, quyền xem engine theo phương án đang có | Đổi cơ chế trước công bố; lead có lát sửa tương thích | QD-TAM-20261106-03; chưa coi là Anh duyệt chính thức |
| Thời điểm được thử cổng thuế thật | ☑ Hoàn tất toàn bộ DEMO trước; Anh ra lệnh riêng sau khi xem bằng chứng và phạm vi tài khoản/kỳ tải | Tiếp tục chỉ DEMO; không có kết nối cổng thuế trong lát tài liệu hoặc bài test này | Không xin cung cấp credential; không tải thật để “kiểm nhanh” |

## 5. Bài test tổng thể cuối — 120 phút, chưa chạy

Lead cấp bản Core thử và xác nhận đường `http://127.0.0.1:8790`, pháp nhân DEMO A/B, người có quyền/người không có quyền. Mẫu DEMO gồm: XML hóa đơn số “0000123”; tiền hàng 1.000.000 VND, thuế 100.000 VND, tổng 1.100.000 VND; một mẫu có số lẻ; XML hỏng; ZIP có một tệp hợp lệ, một tệp hỏng, một tệp trùng; kỳ tháng 02/2024 và 12/2025–01/2026; nguồn thuế giả trả đủ và thiếu một nhóm. Đây là bộ cần chuẩn bị, không khẳng định fixture đã có đủ. Tuyệt đối không chép hóa đơn thật.

Tên màn/nút dưới đây là tiêu chí dự kiến sau nối giao diện. Thiếu màn hoặc quyền thì ghi chưa kiểm, không thử API thay cho bài bấm của Anh.

| Phút | Anh bấm gì | Phải thấy gì |
|---:|---|---|
| 10 | Quản trị Core → Quản lý engine → Hóa đơn điện tử | Năng lực nào đã kiểm thì hiện đúng; nguồn chưa kiểm không hiện là sẵn sàng. |
| 20 | Màn Đọc hóa đơn → Chọn XML DEMO → Gửi → Việc của tôi → Xem kết quả | Số “0000123” giữ số 0 đầu; đúng tiền/thuế/tổng, đơn vị tiền và tham chiếu XML; không tự sửa tổng nguồn. Mẫu số lẻ không sai vì làm tròn float. |
| 15 | Nộp XML hỏng, ZIP hỗn hợp và nộp lại XML đã gửi | Lỗi dễ hiểu; báo phần được/phần lỗi; không nhận trùng hoặc báo đầy đủ khi còn lỗi. Chỉ bật ZIP sau duyệt mẫu. |
| 15 | Từ kết quả chọn Xuất bảng kê/PDF DEMO | File mở được, các tổng khớp XML nguồn và có dấu vết; không dùng bộ đọc chỉ để hiển thị thay bộ đọc kiểm chặt. |
| 20 | Thử tải → nguồn DEMO → tháng 02/2024 → Gửi; thử chọn kỳ thiếu ngày; thử tháng đổi năm | Kỳ hợp lệ nhận đúng tháng nhuận/đổi năm; kỳ lẻ tháng bị từ chối, không tự nới kỳ. Việc ghi rõ nguồn giả. |
| 15 | Trong phiên máy chủ DEMO nhập CAPTCHA giả; chọn nguồn giả lỗi một nhóm; bấm Hủy khi đang chờ | Có trạng thái chờ nhập; thiếu một nhóm báo chưa đầy đủ kèm phạm vi; hủy không sinh kết quả thành công và không tự nhận nghiệp vụ. |
| 15 | Đổi pháp nhân/người dùng DEMO B; thử xem file A; kết thúc phiên và mở phiên mới | Từ chối chéo pháp nhân; phiên mới không dùng lại profile/cookie cũ. Lead chạy ca dọn profile thất bại có kiểm soát: chặn phiên tiếp, không xóa ngoài phạm vi DEMO được phép. |
| 10 | Tải lại trang, mở lịch sử việc và chi tiết nguồn | Kết quả/trạng thái còn đúng, không lộ credential hoặc đường dẫn nhạy cảm; lưu ảnh và phút kiểm. |

Không gọi cổng thuế, Junsky, Cloud hay Word COM trong bài này. Phần xóa profile là việc vận hành tương lai phải có phạm vi DEMO được cấp, không thực hiện trong lát tài liệu. Chạy đầu–cuối hằng ngày/trước báo xong; PG toàn bộ một lần/đêm. Phiếu chỉ lập kế hoạch: **chưa chạy bài giao diện, PG hay Windows, chưa khẳng định engine vận hành thật đạt**.
