# Phiếu kế hoạch tổng thể — Hỏi đáp AI và cổng AI dùng chung

**Cập nhật DOC-PHIEU-0808 theo mốc 05:55 ngày 08/11/2026:** chuỗi 1b đã gộp `87230f4b`; lát 3 khóa gói đã gộp `1badb01e`; công cụ lát 8 đã gộp `556b001c`, còn thử máy AI thật (**CAN-ANH 0h**). Lát 10 gồm máy chủ 10a và màn 10b đang PG/review theo QD-TAM-20261108-02/03/04; lát 14 chưa làm. Căn cứ: [quyết định đêm 08/11](../../QUYET-DINH.md) và [TRANG-THAI các lượt 03:00, 03:45, 04:45, 05:55 (08/11)](../../46-chuyen-doi-dieu-phoi/TRANG-THAI.md). Giờ đã làm **chưa đo**; các dự toán cũ bên dưới giữ để đối chiếu, không dùng làm tổng giờ còn lại hiện hành.

**Lịch sử DOC-CD111 ngày 07/11/2026:** 1b-01 **DUYỆT (Anh 21:31: “1b-01 đồng ý”)**; 1b-06 **KHÔNG làm đường riêng**, 1b-07/08 bỏ dạng gọi AI giữa chừng. Việc cần AI nối bằng chuỗi Core theo CD-110; giữ rào Local, không giữ transaction khi chờ AI và không chuyển Cloud khi mất kết nối cho **bước Hỏi AI trong chuỗi**. Dự toán tại thời điểm đó ở §2.1.1: **36–44 giờ công, ước tính**, giảm khoảng 4 giờ so mốc 40–48 giờ lúc 21:25. Căn cứ CD-111 là handoff được giao; tệp chỉ đạo trong worktree chưa có CD-111. Nội dung cũ gạch/ghi lịch sử để đối chiếu, không dùng làm lệnh triển khai.

| BẢNG TÓM TẮT | Nội dung trình Anh |
|---|---|
| Khi xong, Anh thấy và làm được gì | **Bản 1 chỉ Local AI, 0 lượt Cloud.** Gửi câu hỏi theo function của module, nhận trả lời có trích dẫn; không có thông tin thì báo “không thấy căn cứ”. Local lỗi thì báo rõ và cho thử lại. Xem lịch sử/thống kê sau khởi động lại. Màn Chạy thử DEMO chỉ Admin vào được. |
| Tổng số lát còn lại | **Bản 1: 3 lát chưa nghiệm thu — 10, 8, 14.** Chuỗi 1b đã gộp `87230f4b`, lát 3 đã gộp `1badb01e`; công cụ lát 8 đã gộp `556b001c`, chưa thử máy thật. Lát 10 máy chủ + màn đang PG/review; lát 14 chưa làm. Phụ thuộc chung đối chiếu §2.1.1, không giao lại phần đã gộp. **Bản 2: 4 lát — AI-3, 5+9 gộp, 6, AI-DINH-TUYEN.** Lát 7 gộp vào bài cuối; bỏ AI-PROMPT. |
| Tổng giờ ước còn lại | **Bản 1: chờ lead ước lại sau gộp; giờ đã làm chưa đo.** Quỹ 8 giờ phần riêng và 36–44 giờ theo CD-111 là dự toán lịch sử tại §2.1.1, không phải giờ còn lại ngày 08/11. Không tự trừ quỹ dự toán thành giờ thực. Bản 2 giữ **11 giờ** cũ + AI-DINH-TUYEN **chưa ước lượng**; không gồm chờ hoặc sửa lỗi phát sinh. |
| Việc chờ Anh | **Lát 8 — CAN-ANH 0h:** máy AI bật và có địa chỉ trên màn Cổng Local AI, rồi lead kết nối/thử thật. CD-106 đã kê khai gpt-oss-20b, Qwen3 8B, Gemma; không hỏi lại model. 1b-01 đã duyệt và chuỗi đã gộp; không xin duyệt 1b-06. Bảy câu schema Mask thuộc phiếu Mask, không phải điều kiện bản 1. |
| Cách triển khai | **Sau gộp chuỗi 1b và lát 3:** hoàn tất PG/review máy chủ 10a + màn 10b, thử Local thật ở lát 8 khi có máy AI → bài cuối lát 14. Lát 10 theo QD-TAM-20261108-02/03/04: bốn route Admin, bảng chạy thử migration 129, việc qua engine `ai.hoi@1`, kết quả ghi khi Core nhận ACK; chỉ DEMO/Local. Chuỗi trích dùng bước chuẩn bị / Hỏi AI / hậu kiểm do Core điều phối, G3-GOI-34 ở phần tích hợp trích. Giữ cổng AI, prompt thuộc module, giao diện song song back end. Số lát song song do lead quyết; không tự mở lát mới của phiếu chuỗi chưa duyệt lại (CD-110). |

Sửa theo **CD-098 ngày 06/11/2026** và [Quyết định cuối e_hoi_ai](QUYET-DINH-CUOI-e_hoi_ai.md) §1–§5; **văn bản gốc thắng khi có khác biệt**. CD-098 và quyết định gốc được đọc ở thư mục dự án chính vì bản worktree này chưa có hai cập nhật đó. Bảng hiện trạng giữ mốc khảo sát **`4f180f92`** cho phần cũ; các hàng ghi 08/11 cập nhật theo quyết định và TRANG-THAI nêu trên. Căn cứ kỹ thuật: [đóng gói §5.2, §6.1–§6.6](KE-HOACH-G3-GOI.md), [các lát G3](../g2/KE-HOACH-LAT-G2-G3.md), [schema Mask](TOM-TAT-SCHEMA-MASK-CHO-ANH.md). Toàn bộ số giờ là ước tính, chưa phải thời gian đã đo.

## 1. Hiện trạng — cổng đã có, phần chưa đủ điều kiện còn phải làm

Mốc khảo sát cũ dựa trên `git log --oneline hop-nhat-20261023 --regexp-ignore-case --grep='gộp'`, CD-091 cập nhật 10:25/nhật ký 10:00. Cập nhật đêm 08/11 dùng bằng chứng gộp và trạng thái PG/review ghi trong TRANG-THAI đến 05:55. Lead kiểm lại trước giao vì nhánh tích hợp tiếp tục thay đổi.

| Trạng thái | Nội dung nghiệp vụ | Cột phụ: mã / bằng chứng |
|---|---|---|
| Đã gộp | Kiểu câu hỏi/trả lời, cờ chỉ AI nội bộ, adapter đi qua cổng chung | G3 AI-1a `0b0faaea`, AI-1b `6c4c4f3d`, AI-2 `f2fdebe4`. Cờ chỉ Local đã có test không gọi Cloud; không xin duyệt lại schema đầu vào này như thể chưa làm. |
| Đã gộp | Nhận bí mật trong bộ nhớ, nhật ký và thử vận hành qua cổng giả | AI-4b `af1d1870`, AI-5a `b7797171`, AI-5b/5c/5d/5e/5f `61b9b7b9`. Cổng giả không chứng minh Cloud/Windows thật đạt. |
| Đã gộp | Gói AI mẫu, lõi cổng và AI nội bộ, adapter, nhật ký dùng lõi trong gói | G3-GOI-01 `32bc97ba`, 06 `b4da0146`, 07 `d8e91e7c`, 08 `8a380c45`; ghi CSDL nhật ký giữ phía Core. |
| Đã gộp, dùng chung | SDK/bridge, bộ phát hiện gói, màn quản lý và đường kiểm kê | G3-GOI-03/04/05, 10/11/12, 13/13b `df35defc`, 14 `b5e6c301`. Root gói thật vẫn chưa bật. |
| Đã gộp — 08/11 04:45 | Khóa nguồn, phiên bản thư viện và SDK của gói Hỏi AI | Lát 3 / G3-GOI-09 `1badb01e`. Giữ kiểm SDK/alias áp dụng; không đổi bản ghim SDK từ phiếu này, wheel 1.4.1 vẫn chỉ candidate theo §6.3. |
| Đã gộp — 08/11 03:00 | Chuỗi Hỏi AI bản 1: runtime, khai báo function/prompt, chọn model, binding/nguồn Core và nhật ký | Chuỗi 1b `87230f4b` (0405 + KHAI + CHON + NOI v1–v6 + 1b-09); PG 15 module, 569 ca, 0 lỗi, 0 skip theo TRANG-THAI. |
| Công cụ đã gộp; chưa thử máy thật — 08/11 04:45 | Công cụ thử ba model Local cho lát 8 | `556b001c`; chờ máy AI bật và địa chỉ trên màn Cổng Local AI — **CAN-ANH 0h**. Không suy công cụ đạt là Local thật đã đạt. |
| Đang PG/review — 08/11 05:55 | Lát 10: máy chủ 10a và màn Chạy thử DEMO 10b | 10a v6 `fc7d166c` đã ghép 10b; PG 23 module đang chạy, review Opus vòng 2. QD-TAM-20261108-02/03/04; chưa xác nhận gộp/nghiệm thu. |
| Chưa làm — 08/11 | Lát 14: bài test cuối bản 1 | Chờ lát 10 và thử Local thật ở lát 8; lát 3 đã gộp. |
| Chưa đủ điều kiện | Nối che/mở qua engine Mask cho Cloud của kiến trúc G3 | **G3 AI-3**, chờ G3 MASK-2/schema/nguồn cấp khóa. Mask hiện chưa có manifest công bố năng lực, không gọi thẳng nội bộ của engine khác để lấp chỗ thiếu. |
| Đã gộp nhưng là việc cũ khác phạm vi | Chuyển đường Cloud engine cũ số 6 qua cổng AI | Commit **`30d5478f` mang tên AI-3** thuộc đợt 25/10. Không dùng nó chứng minh **G3 AI-3** (nối `e_mask`) đã xong. |
| Đã gộp một phần; hàng chờ còn đang làm | Chuỗi và thông báo hàng chờ | CE-2 đã gộp `4f180f92`, mới hơn báo cáo CD-091; HC-1/HC-2 chưa thấy gộp. CE-0 `02cec4bc`, CE-1 `78add174`, CE-9 `a47242fe` đã gộp. Không giao lại ở phiếu AI. |
| Chưa thấy gộp / chưa kiểm thật tại mốc khảo sát | ~~Kênh AI qua SDK~~ **Thay theo CD-111: bước Hỏi AI trong chuỗi Core**, cài gói độc lập, root thật, cách ly tài khoản và nghiệm thu cuối | G3-GOI-34/38/39, phần cuối 40, 13c. ~~§6 còn yêu cầu xác minh wire/transport trước 34.~~ Không làm transport gọi AI riêng; SDK 1.5.0 đã phát hành cho CRM theo QD-TAM-20261107-11, engine giữ bản ghim. Không tự coi Local đang sẵn sàng khi chưa kiểm máy/model. |

Tại mốc khảo sát cũ chưa có bằng chứng một màn nghiệp vụ hiện hữu đã nối trọn vào năng lực Hỏi AI của G3. Đến 08/11 05:55, lát **10 — Chạy thử DEMO** chỉ Admin đã có máy chủ + màn ghép, đang PG/review; chưa xác nhận nghiệm thu trình duyệt thật. Module vay M9 luôn chỉ dùng Local, kể cả khi bản 2 mở Cloud cho module khác.

Đối chiếu đủ bảng 40 lát tại mốc khảo sát cũ: đã có gộp **01–08, 10–16, 21–24, 27, 29–33, 40**; **30 và 40 mới xong phần tài liệu/hiện trạng**. Khi đó chưa thấy gộp **09, 17–20, 25–26, 28, 34–39**; **bổ sung ngày 08/11: 09 đã gộp cùng lát 3 `1badb01e`**. Tài liệu G3-GOI-40 ghi route 13 chờ đã cũ: git xác nhận 13/13b đã gộp; phần bật root chuyển 13c/39 theo §6.5.

## 2. Các lát giữ / gộp / chuyển / bỏ theo CD-098

### 2.1. Bản 1 — chỉ Local AI

Engine nhận prompt của function, tài liệu, mã module và mã function; ghép khung chung bắt buộc có trích dẫn và nói “không thấy căn cứ” khi tài liệu không có thông tin; gửi Local AI qua cổng chung; Python kiểm trích dẫn; trả kết quả về module. Nhật ký ghi module, function, phiên bản prompt, thời gian và kết quả kiểm. Máy Local AI là máy riêng, có GPU, kết nối theo TL 48 §1.2.

**Prompt thuộc module:** mỗi function một prompt riêng có mã và phiên bản, khai báo trong gói module; khi module gửi lượt, engine kéo đúng prompt của function đó. Thiếu prompt → từ chối có lý do, không có prompt mặc định chung. Admin module xem/sửa prompt của module mình; Admin Core sửa tất cả. Việc xem/sửa này làm **trong module**; **bỏ AI-PROMPT**, không làm quản lý prompt trong engine.

**T** = test thuần nhanh + review chéo Codex. **N** = T + PostgreSQL đầy đủ + Opus khi đổi CSDL/quyền/tiền/bí mật/xóa. **M** = lead thử trên giao diện DEMO/máy được phép. Khi phát sinh thay đổi nhạy cảm, nâng mức kiểm tương ứng; không mặc nhiên chạy PG toàn bộ chỉ vì xem nhật ký. Worker chỉ test thuần/mock; PG và vận hành thật do lead.

| Ưu tiên / lát gốc | Việc | Phụ thuộc / điều kiện trước | Giờ ước ban đầu | Giờ đã làm | Kiểm | Mã / phạm vi / trạng thái 08/11 |
|---|---|---|---:|---|---|---|
| 1 · Lát 10 | Thêm màn Chạy thử DEMO ở chi tiết Hỏi AI: chọn function DEMO, nhập tài liệu giả/câu hỏi, gửi Local và xem trả lời/lịch sử. **Chỉ Admin vào được** | Chuỗi 1b và lát 3 đã gộp; thử Local thật còn phụ thuộc lát 8. Hàng chờ dùng CE/HC, không làm lại ở AI | 3 | Chưa đo | T + M; N nếu đổi quyền | AI-UI-NOI; **10a máy chủ + 10b màn đã ghép, đang PG 23 module/review Opus vòng 2 lúc 05:55**, chưa xác nhận gộp. Theo QD-TAM-20261108-02/03/04; chỉ DEMO/Local, 0 lượt Cloud; giữ kiểm quyền quản trị hiện có |
| 2 · Lát 3 | Khóa nguồn, phiên bản thư viện và SDK của Hỏi AI; cài gói ở môi trường sạch | G3-GOI-08 và contract/runtime/binding của Hỏi AI đã gộp; không chờ operation riêng hoặc tách trích. Giữ kiểm SDK/alias áp dụng và không ghim wheel SDK 1.4.1 candidate | 2 | Chưa đo | T | G3-GOI-09; **đã gộp `1badb01e` lúc 04:45**, không giao lại hoặc giao trùng hàng 09 của G3-GOI |
| 3 · Lát 8 | Thử Local thật qua cổng chung: chỉ Local, máy mất kết nối, model chưa sẵn sàng. **Local lỗi → báo rõ và cho thử lại; 0 lượt Cloud** | Lát 3 đã gộp; CD-106 đã kê khai ba model. Chờ máy AI bật + địa chỉ trên màn Cổng Local AI (**CAN-ANH 0h**); lead thử cả ba model trên DEMO | 2 | Chưa đo | T + M | AI-LOCAL-NT; **công cụ đã gộp `556b001c` lúc 04:45, chưa thử máy AI thật**; không đổi sang Cloud khi lỗi |
| 4 · Lát 14 | Thử hỏi–đáp–xem lại qua màn nghiệp vụ theo bài test cuối §4, đối chiếu quyết định gốc §5 | Lát 10 và 8 chưa nghiệm thu; lát 3 đã gộp. Core/CE/HC cung cấp phần nhật ký/quyền/hàng chờ cần cho ca cuối; không chờ Mask/Cloud bản 2 | 1 | Chưa đo | T + M; N nếu phải sửa CSDL/quyền | AI-NT; **chưa làm**; khoảng 40 phút. **Lát 7 gộp vào bài này:** lịch sử/thống kê sau khởi động lại, mỗi việc chỉ ghi một lượt |
| | **Bốn lát theo kế hoạch; còn 10, 8, 14 chưa nghiệm thu** | Chưa gồm các phụ thuộc dùng chung ở G3-GOI; lead ước lại giờ còn lại sau gộp | **8 (dự toán cũ)** | **Chưa đo** | | |

### 2.1.1. Trạng thái sau gộp và lịch sử dự toán CD-111

**Bảng bốn lát / 8 giờ trên giữ dự toán ban đầu của phần riêng, không phải giờ còn lại sau gộp hoặc toàn bộ Hỏi AI bản 1.** Trạng thái dưới đây cập nhật theo CD-111, CD-106 và TRANG-THAI đến lượt 05:55 ngày 08/11/2026; lead đối chiếu kết quả gộp mới trước khi giao, không làm lại phần đã xong. Giờ đã làm của chuỗi 1b và các lát: **chưa đo**.

| Nhóm việc triển khai / kiểm | Trạng thái và phạm vi cập nhật 08/11 |
|---|---|
| 1b-01 — metadata prompt/function và contract | **Đã duyệt và đã gộp**, là nền contract của chuỗi `87230f4b` gộp lúc 03:00; không còn chờ triển khai/duyệt lại. Không đổi âm thầm bản đã ghim. |
| 1b-02, 1b-04 — ví dụ/manifest và runtime | **Đã gộp**, gồm nền ví dụ/manifest và runtime trong chuỗi `87230f4b` (0405 + KHAI + CHON + NOI v1–v6 + 1b-09). Giữ phạm vi contract đã duyệt, adapter thật/readiness; Local không cần Mask hoặc khóa Cloud; ACK/drain. |
| 1b-05 — binding và nguồn Core | **Đã gộp trong chuỗi `87230f4b`**; không còn chặn bởi 1b-01. Phạm vi xác minh module/function/prompt/nguồn, quyền/pháp nhân/lease của **bước Hỏi AI trong chuỗi**; không giao lại. |
| 1b-09 — nhật ký | **Đã gộp trong chuỗi `87230f4b`**; không còn chặn bởi 1b-01. Phạm vi provenance đã xác minh, thời gian/kiểm/model/lý do chọn; ACK/phát lại không trùng, không lưu tài liệu/prompt/khóa vào metadata. |
| 1b-03 và ràng buộc chuyển từ 1b-07/08 | **1b-03 đã xong theo lượt 21:25**, không giao lại. Khi tích hợp bước Hỏi AI vẫn kiểm ép Local kể cả cờ thiếu/false hoặc Cloud bật; **không giữ transaction trong khi chờ AI; mất kết nối/model lỗi không sang Cloud**. Dùng 1b-03/04/05 và ca cuối để kiểm, không tạo ba lát đường riêng thay tên. |
| ~~1b-06/07/08 dạng gọi AI giữa chừng~~ | **Bỏ, thay theo CD-111.** Không operation wire, method SDK hoặc dispatch riêng để engine trích gọi AI. Dùng chuỗi Core theo CD-110; tách trích chuẩn bị / hậu kiểm tại G3-GOI-34. |
| CD-106 — phát hiện/chọn model và hai màn cổng | AI-MODEL-DO và AI-MAN đã gộp theo lịch sử TRANG-THAI; AI-MODEL-CHON đã gộp trong chuỗi `87230f4b`. Còn thử tích hợp/máy thật ở lát 8, Cloud bản 1 vẫn khóa. Không hỏi lại danh sách model đã kê khai. |
| Bốn lát riêng 10, 3, 8, 14 | Lát 3 đã gộp `1badb01e`; công cụ lát 8 đã gộp `556b001c`, thử thật chờ máy AI — **CAN-ANH 0h**. Máy chủ 10a + màn 10b đang PG/review theo QD-TAM-20261108-02/03/04; lát 14 chưa làm. Quỹ 8 giờ là dự toán cũ, giờ đã làm chưa đo; lead ước lại phần còn lại. |
| Phụ thuộc chung | Sáu mã AI-KENH, 34, 13c, 38, 39, phần cuối 40 theo phiếu chủ trì; dùng lại kết quả, không giao/cộng trùng. **34 đổi mục tiêu sang tách bước trích**, không mở API AI riêng; 38/39 đủ năm gói là mốc tổng thể, không ép bản 1 Local chờ Mask/Cloud. SDK 1.5.0 đã phát hành cho CRM, không đổi bản ghim engine từ phiếu này. |

**Lịch sử cách tính ngày 07/11 — ước tính, chưa đo:** giữ cùng phạm vi/cơ sở của [TRANG-THAI lượt 21:25](../../46-chuyen-doi-dieu-phoi/TRANG-THAI.md), đã ghi **khoảng 40–48 giờ** từ bốn lát riêng 8 giờ, nhóm 1b khoảng 12 giờ/9 việc, CD-106 khoảng 6 giờ và sáu việc chung G3-GOI 22 giờ. Các quỹ là đầu vào lịch sử của khoảng tổng hợp, **không cộng lại thành số giờ mới**, không lấy 19 giờ CD-098 cộng thêm 22 giờ của mốc đó.

Để ước nhanh tác động đổi kiến trúc, **giả định phân bổ đều** quỹ 1b cũ: `12 / 9 ≈ 1,33 giờ/việc`; bỏ ba việc đường riêng 1b-06/07/08 tiết kiệm **khoảng 4 giờ**. Nhóm 1b theo cùng cơ sở dự toán giảm từ khoảng 12 xuống khoảng 8 giờ; đây không phải đo giờ từng lát hoặc xác nhận mọi việc có cùng độ khó. Các ràng buộc Local/transaction/kết nối được gộp vào bước Hỏi AI và kiểm tích hợp đang có, không trừ mất hoặc cộng lại thành lát mới. Vì vậy **ước tính sau CD-111 tại mốc 07/11: (40–48) − 4 = 36–44 giờ công, giảm khoảng 4 giờ ở cả hai đầu**.

Tại mốc dự toán đó, không trừ lại khoảng 6–8 giờ đã làm được nêu ở lượt 21:25 hoặc SDK CRM/AI-MAN/1b-03 lần nữa; công tách trích trong 34 chưa đo lại. Khoảng 36–44 **chỉ so trên cùng phạm vi dự toán cũ**, không phải giờ còn lại sau gộp ngày 08/11, cam kết mốc AI độc lập hoặc thời gian đồng hồ. Công điều phối chuỗi mới nằm ở phiếu chuỗi, không ngầm cho là miễn phí hoặc cộng trùng. **Giờ đã làm chưa đo**; lead cần ước lại phần còn lại của lát 10/8/14 và phụ thuộc chung, chốt ranh giới nghiệm thu Local / tổng thể trước khi dùng làm lịch; không lấy dự toán phần đã gộp làm số giờ thực để trừ.

### 2.2. Bản 2 — ghi kế hoạch, chưa triển khai

| Thứ tự / lát gốc | Nội dung giữ lại / bổ sung | Phụ thuộc / điều kiện | Giờ ước | Kiểm |
|---|---|---|---:|---|
| 1 · Lát 4 — G3 AI-3 | Nối engine AI với che/mở văn bản của Mask v2 qua đường chuẩn, kiểm cả chỉ dẫn; không nhầm AI-3 cũ `30d5478f` | Sau G3 MASK-2; schema đã duyệt; nguồn/khóa và capability hợp lệ; AI-2 đã gộp | 4 | N |
| 2 · **Lát 5+9 gộp** | Kiểm Mask chưa mở, sót tên, hết lượt, mở che sai; chặn trước gửi. Thử Cloud giả qua Mask: che trước, giữ nguyên tiền/ngày, mở che đúng sau trả lời | Sau G3 AI-3; chỉ dữ liệu DEMO, provider Cloud giả; không dựng bộ che riêng. Ca Cloud thật chỉ sau khi đủ điều kiện và được phép | 4 (2+2 cũ) | N + M |
| 3 · Lát 6 | Kiểm nhận/thu hồi khóa trong bộ nhớ và cách ly tài khoản AI thực trên Windows | AI-4b đã gộp; **cách giữ khóa quyết khi làm bản 2**. Tài khoản/ACL và cấp khóa theo cơ chế được duyệt; worker không đọc két hoặc ghi khóa ra log/đĩa | 3 | N + M |
| 4 · **Thêm AI-DINH-TUYEN** | Định tuyến Cloud, đo độ chính xác Local theo từng function và kiểm xác suất theo A1/A2 của quyết định gốc | Sau lát 6; công tắc Cloud theo module mặc định tắt; mọi lượt Cloud qua Mask | Chưa ước lượng | Lead phân loại theo thay đổi thực tế |
| | **Tổng bản 2: 4 lát** | Giữ 11 giờ của các lát cũ; phần thêm chưa có ước lượng | **11 + AI-DINH-TUYEN chưa ước lượng** | |

Quy tắc từ bản 2 theo TL 48 §1.5–§1.6 và A1/A2: module đã bật Cloud thì tự chuyển khi Local không chạy, Local không chắc, và ở các lượt kiểm xác suất. Đo độ chính xác theo từng function; lịch kiểm **20% → 10% → 5%, không về 0; tụt dưới 90% thì quay lại 20%**. Mọi lượt Cloud qua Mask, còn định danh thì chặn, tiền/ngày giữ nguyên. **M9 luôn chỉ Local.** Các quy tắc này không áp dụng để mở Cloud ở bản 1.

### 2.3. Việc chuyển và ngoài phạm vi

- **Chuyển từ phiếu e_hoi_ai theo CD-098:** lát 1 (AI-KENH, tách 1a xác minh / 1b nối thêm nếu thiếu), 2 (G3-GOI-34), 11 (13c), 12 (38), 13 (39), 15 (phần cuối 40) sang [G3-GOI §6.6](KE-HOACH-G3-GOI.md#66-các-việc-chuyển-từ-phiếu-e_hoi_ai-theo-cd-098). ~~Sáu việc chung giữ 19 giờ ước cũ; chỉ 1b nếu cần~~ **Thay theo CD-111:** 19 giờ là lịch sử CD-098, dự toán điều phối hiện hành 22 giờ theo CD-100/TRANG-THAI; 1a đã xác minh thiếu, 1b-01 đã duyệt, bỏ 1b-06/07/08 dạng cũ. Không cộng trùng giữa các phiếu; số tổng ước lại xem §2.1.1. Nội dung/phụ thuộc cũ được giữ tại nơi nhận để đối chiếu.
- Lát 7 không còn là lát riêng; bài test cuối bao gồm lịch sử/thống kê sau khởi động lại và kiểm gửi lặp. Theo quyết định gốc §3, lát 14 giữ dự toán 1 giờ, **chưa làm**; 8 giờ phần riêng và 36–44 giờ theo CD-111 là **dự toán lịch sử trước gộp ngày 08/11**, xem §2.1.1; không cộng thêm 2 giờ của lát 7 cũ.
- Vector `ai.nhung_vector@1` → phiếu **e_tra_cuu**. Hàng chờ/thông báo hàng chờ → chuỗi **CE/HC**; bài test cuối chỉ dùng kết quả tích hợp, không mở lát hàng chờ ở engine AI.
- Schema/nguồn/capability Mask, giấy phép OCR/hóa đơn, đóng gói năm engine thuộc phiếu chủ trì. Chúng không được dùng để mở rộng bản 1 thành nghiệm thu Cloud hoặc nghiệm thu đủ năm gói.

## 3. Thứ tự và việc chờ Anh

**Thứ tự bản 1 sau gộp đêm 08/11:** chuỗi 1b `87230f4b` và lát 3 `1badb01e` đã gộp; hoàn tất PG/review máy chủ 10a + màn 10b theo QD-TAM-20261108-02/03/04; công cụ lát 8 `556b001c` đã gộp, thử Local thật khi có máy AI (**CAN-ANH 0h**) → lát 14 (chưa làm). Chuỗi cần AI dùng bước Hỏi AI; tích hợp trích chuẩn bị / Hỏi AI / hậu kiểm theo 34 và phiếu chuỗi sửa, không thiết kế operation riêng. CD-110 chưa cho mở lát mới của phiếu chuỗi trước duyệt lại. **Bản 2:** AI-3 sau MASK-2 → 5+9 gộp → 6 → AI-DINH-TUYEN. Số lát song song do lead quyết; phần chờ thì chuyển sang việc đủ điều kiện.

| Việc chờ / đã chốt | Xử lý |
|---|---|
| **Lát 8 — CAN-ANH 0h; model đã kê khai theo CD-106** | Chờ máy AI bật + địa chỉ trên màn Cổng Local AI. Công cụ `556b001c` đã gộp; lead còn kết nối/thử thật và ghi thời gian/độ đúng gpt-oss-20b, Qwen3 8B, Gemma. Không xin kê khai lại. |
| **Chuỗi 1b đã gộp; 1b-06 không làm đường riêng** | Anh chốt 21:31 theo CD-111; chuỗi đã gộp `87230f4b` lúc 03:00 ngày 08/11. Không giao lại 1b-01/02/04/05/09 hoặc 1b-07/08 dạng gọi AI giữa chừng; giữ phạm vi bước Hỏi AI và 34. |
| **Ước lại giờ sau gộp và ranh giới nghiệm thu** | Giờ đã làm chưa đo; lead ước lại phần còn lại từng nhóm và công tách trích/chuỗi. Quỹ 8 giờ và 36–44 giờ ở §2.1.1 là dự toán lịch sử, không phải giờ còn lại hiện hành hoặc thời gian đồng hồ. |
| **Bảy câu schema Mask** | Chưa chốt ở phiếu AI; thuộc phiếu Mask và [tóm tắt schema](TOM-TAT-SCHEMA-MASK-CHO-ANH.md). Không chặn bản 1 chỉ Local |
| Phạm vi, cơ cấu lát, prompt và màn DEMO | Đã chốt ở quyết định gốc §4: bản 1 chỉ Local; prompt theo module/function; thiếu prompt từ chối có lý do; màn DEMO chỉ Admin. Không xin duyệt lại tổng thể 15 lát cũ |
| Cloud, độ chính xác và kiểm xác suất | A1/A2 đã chốt cho bản 2 theo TL 48; cách giữ khóa quyết khi làm bản 2. Không yêu cầu tài khoản/khóa Cloud để hoàn thành bản 1 |

## 4. Bài test tổng thể cuối bản 1 — theo quyết định gốc §5

**Lát 14 chưa làm đến mốc 05:55 ngày 08/11/2026. Khoảng 40 phút, chưa đo**, tính trong dự toán 1 giờ của lát 14. Chỉ dữ liệu giả có nhãn DEMO; **0 lượt Cloud trong toàn bài**. Lead chuẩn bị Core thử và tự chạy trọn luồng trước khi mời thử; không suy cổng đang sẵn sàng từ số cổng.

Dữ liệu chuẩn bị: một function DEMO có prompt khai báo trong gói module, có mã và phiên bản; đoạn hợp đồng **GIẢ DEMO** có “Công ty DEMO Ánh Dương”, hợp đồng “DEMO-001”, tiền **1.000.000 VND**, ngày **30/10/2026**; câu hỏi mà tài liệu không có đáp án; một function DEMO chưa khai báo prompt; hai pháp nhân DEMO.

**Đường vào (vai Admin):** Quản trị Core → Quản lý engine → Hỏi AI → Chạy thử DEMO. Các bước mô tả luồng đích, chưa phải kết quả đã quan sát. Vai không phải Admin bị chặn; giao diện dùng tiếng Việt nghiệp vụ, không xưng “Anh”/“bạn”, ngày dd/mm/yyyy; mã module/function/prompt dùng trong nhật ký kỹ thuật, không làm nhãn nghiệp vụ trên màn.

| Bước | Thao tác | Kết quả cần thấy | Phút |
|---|---|---|---:|
| 1 | Chọn function DEMO, dán tài liệu giả, hỏi “số tiền và ngày thanh toán là bao nhiêu”, bấm Gửi | Đúng **1.000.000 VND**, **30/10/2026**, có trích dẫn. Engine dùng đúng prompt của function; nhật ký ghi module, function, phiên bản prompt. **0 lượt Cloud** | 10 |
| 2 | Gửi hai câu liên tiếp, xem Việc của tôi. Hỏi câu tài liệu không có đáp án. Gửi lượt từ function chưa khai báo prompt | CE/HC hiện vị trí chờ/thời gian ước. Mỗi việc chỉ ghi một lượt. Không có đáp án thì trả **“không thấy căn cứ”**, không bịa. Thiếu prompt thì từ chối, có lý do | 10 |
| 3 | Lead tạm tắt Local bằng cấu hình thử; gửi câu hỏi. Bật lại Local rồi thử lại; đối chiếu ca kiểm bước Hỏi AI của chuỗi | Báo rõ **“không sẵn sàng / thử lại”**, **0 lượt Cloud** kể cả cờ thiếu/false hoặc Cloud bật trong cấu hình thử. Có bằng chứng kỹ thuật **không giữ transaction CSDL khi chờ AI**; quyền/pháp nhân/lease đúng, không gọi AI giữa chừng từ engine trích. Phục hồi Local thì thử lại được. Phần kiểm kỹ thuật chuẩn bị trước, không kéo dài buổi xem màn | 5 |
| 4 | Mở Lịch sử/thống kê. Lead khởi động lại tiến trình DEMO theo quyền, tải lại trang. Thử vai thuộc pháp nhân khác | Lịch sử/thống kê vẫn còn; vai khác pháp nhân không xem được nội dung trái quyền. Nhật ký không lưu nội dung nhạy cảm ngoài quy định | 10 |
| 5 | Ghi kết quả từng ca, ảnh chụp, số phút chờ và chạy | Phân biệt rõ dữ liệu DEMO với phần vận hành thật chưa kiểm | 5 |
| | **Tổng** | | **40** |

Điều kiện đạt: không có lỗi mới so [nền test](../../46-chuyen-doi-dieu-phoi/NEN-TEST.md), không tăng skip không giải thích; chạy bài này hằng ngày/trước mỗi mốc và ghi riêng phút test từng lát với phút test tổng thể. PostgreSQL toàn bộ chỉ một lần mỗi đêm, do lead. Không dùng dữ liệu thật, không có lượt Cloud nào ở bản 1. **Lát AI-PHIEU chỉ sửa tài liệu; không chạy PG, server, AI, mạng ngoài hoặc thao tác két bí mật.**
