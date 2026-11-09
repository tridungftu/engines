# Phiếu kế hoạch tổng thể — Chuỗi xử lý engine

```text
Gói module khai sẵn: [Bước 1] -> [Bước 2] -> [Bước 3 nếu có]
                                  |
                                  v
CORE — dịch vụ lõi điều phối chuỗi, khu mã riêng
  Kiểm khi khai: đầu ra bước trước khớp đầu vào bước sau
  Dùng lại hàng việc hiện có, không tạo hàng việc thứ hai

Module gửi việc -> Core xếp bước 1 -> Engine xử lý -> Báo xong về Core
                                                        |
                                                        v
                                              Core lưu kết quả
                                                        |
                              Còn bước: xếp bước kế <----+
                              Hết bước: trả kết quả về module

Người dùng: Việc của tôi — một dòng -> mở xem từng bước
```

**Cơ chế đã chốt (A), ngày 07/11/2026 lúc 21:21:** bộ điều phối là **dịch vụ lõi trong Core**, không phải engine riêng. Engine không gọi engine; Core chuyển dữ liệu giữa các bước. Mỗi engine khai **phiếu đăng ký đầu vào/đầu ra**: nhận loại dữ liệu gì, trả loại dữ liệu gì. Chuỗi là danh sách bước theo đúng thứ tự Anh khai; Core kiểm khớp đầu ra/đầu vào khi khai chuỗi. Khi chạy, Core lặp việc **xếp bước → nhận báo xong → lưu kết quả → đẩy bước kế → hết bước thì trả module**. Thêm engine mới chỉ đăng ký rồi đưa vào chuỗi, không sửa bộ điều phối hoặc engine cũ. Có engine nào, kể cả Mask, do Anh chọn khi khai; phiếu không ấn định một luồng nghiệp vụ hay nhánh Cloud.

**Giao diện v1 đã chốt:** chuỗi khai sẵn trong **gói module**; màn đặt trong **phần quản lý của từng module**, hiện các bước theo thứ tự. Sửa qua **Lưu nháp → Áp dụng**; việc đang chạy giữ nguyên phiên bản chuỗi cũ, việc mới dùng bản đã áp dụng. **Admin module** sửa chuỗi của module mình; **Admin Core** xem và sửa tất cả. Người dùng thường chỉ thấy **một dòng trong Việc của tôi**, bấm mở từng bước. Trình dựng kéo-thả đầy đủ để sau.

| Tóm tắt trình Anh | Nội dung |
|---|---|
| Kết quả cần đạt | Một module gửi việc một lần; Core chạy chuỗi 2–3 engine theo thứ tự đã khai, giữ kết quả từng bước rồi trả kết quả về màn module. Có hàng chờ, hủy, chạy lại từ bước lỗi và lịch sử. |
| Phạm vi còn lại | **8 lát, 28 giờ công — ước tính**, chỉ gồm lõi điều phối, hàng chờ, hủy/chạy lại, màn xem/quản lý chuỗi và bài nghiệm thu. CE-1, CE-2, HC-1, HC-2 đã gộp, không giao lại hoặc tính giờ làm lại. |
| Ngày dự kiến chuỗi chạy được | **12/11/2026, buổi 17:00 — ước tính có điều kiện**, với giả định bắt đầu 09/11/2026, đủ quỹ 8 giờ công/ngày cho chuỗi và có sẵn module cùng 2–3 engine chạy được. Chi tiết ở mục 4; đây chưa phải lịch đã được cấp nguồn lực. |
| Ngoài mốc chuỗi | Sáu việc đóng gói chung 34b, 34, 13c, 38, 39, 40b; CE-K; màn tình trạng engine 7 ngày. Không cộng giờ hoặc lấy việc đủ năm gói làm điều kiện nghiệm thu chuỗi. |
| Trạng thái | **Phiếu sửa để trình lại theo CD-110; chưa mở lát mới tới khi Anh duyệt phiếu sửa.** Phần A ở trên đã chốt, không hỏi lại. Trong lúc chờ, khe trống theo CD-108/109, CRM vẫn ưu tiên số 1. |

## 1. Căn cứ và ranh giới v1

Căn cứ chính: [CD-110, ghi ngày 07/11/2026 lúc 21:25, nguồn Anh chốt 21:21](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md) và [văn bản gốc mục A–C](CHI-DAO-PHIEU-ENGINE-chuoi-20261107.md); văn bản gốc thắng khi khác biệt. Hai nguồn mới chưa có trong worktree lúc sửa, đã đọc **chỉ tài liệu** từ cùng đường dẫn dưới thư mục dự án chính `D:\Claude\Phan mem ho tro ke toan\Phần mềm kho tri thức`; không chép hoặc sửa nguồn. CD-110 đã ghi nhận QD-20261107-07, CE-2/HC-1/HC-2 đã gộp.

Dùng lại bộ chạy quy trình, bộ kiểm/ghim chuỗi, hàng việc, thông báo và màn mẫu đã có. Chỉ hoàn thiện nối theo thứ tự; không xây thêm cơ chế chọn engine, tự suy thứ tự, trình dựng kéo-thả hoặc cổng AI riêng. Các bước luôn đi qua Core và dùng quyền hiện có; chuỗi không nới quyền của module hay engine.

Việc riêng về nguồn, khả năng xử lý, bộ tham số, model, giấy phép, kết nối và bài đo của từng engine thuộc **phiếu engine đó**. Phiếu này không đặt câu hỏi hoặc quyết định thay cho engine. Lead chọn module DEMO và 2–3 engine đã sẵn sàng theo chuỗi được khai, ghi vào biên bản nghiệm thu; không bắt buộc phải đủ cả năm engine.

## 2. Trạng thái thật — đã gộp khác với đã nghiệm thu

Đối chiếu tại **`hop-nhat-20261023 = 608465a2`** ngày 07/11/2026; HEAD worktree khi bắt đầu là `32b8b9b8`. Mỗi lệnh bên dưới đã trả **mã 0**, xác nhận đầu nhánh là tổ tiên của nhánh hợp nhất. Commit gộp/ghi nhận tương ứng cũng đã kiểm chứa đầu nhánh đó; các commit ghi nhận HC-1/HC-2 có một parent, không gọi chúng là merge commit.

| Thành phần | Lát và việc đã có | Đầu nhánh | Commit gộp/ghi nhận trong hợp nhất | Kiểm đã chạy |
|---|---|---|---|---|
| Lõi điều phối | **CE-1 — ĐÃ GỘP**, bộ chạy chuỗi và xử lý gián đoạn | `ff579b6a` | `78add174`, 06/11/2026 10:21 | `git merge-base --is-ancestor lat/ce-1 hop-nhat-20261023` → 0 |
| Lõi điều phối | **CE-2 — ĐÃ GỘP**, kiểm/biên dịch chuỗi và ghim engine | `f7a97394` | `4f180f92`, 06/11/2026 10:25 | `git merge-base --is-ancestor lat/ce-2 hop-nhat-20261023` → 0 |
| Hàng chờ | **HC-1 — ĐÃ GỘP**, cửa đọc hàng chờ và số đo | `d2dd6c1d` | `3e99bca4`, 06/11/2026 11:56 | `git merge-base --is-ancestor lat/hc-1 hop-nhat-20261023` → 0 |
| Hàng chờ / màn xem | **HC-2 — ĐÃ GỘP**, thông báo và Việc của tôi | `0f8fa8ef` | `72e8c390`, 06/11/2026 14:40 | `git merge-base --is-ancestor lat/hc-2 hop-nhat-20261023` → 0 |

Nền dùng lại còn có **CE-0** (màn mẫu, `02cec4bc`) và **CE-9** (tài liệu dịch vụ chuỗi, `a47242fe`) theo phiếu trước; màn mẫu không chứng minh chuỗi thật đã chạy. Chỉ lập kế hoạch hoàn thiện sau các lát đã gộp, không suy đã nghiệm thu đầu–cuối từ trạng thái git.

**Phân biệt tên HC-3:** “HC-3” trong phiếu cũ là **Tình trạng hệ thống theo engine 7 ngày**; đổi tên công việc dự kiến này thành **TINH-TRANG-7N**, **để sau, ngoài v1**. Nó không phải nhánh **`lat/hc-3` đã gộp ngày 06/11/2026**, sửa route việc nhận/trả dữ liệu 1.3 và lỗi 422 của chuông Việc của tôi. Giữ nguyên bản sửa đã gộp: commit triển khai `436a6921`, đầu nhánh `c4c2d31e`, commit ghi nhận `fe59f433` lúc 21:39; `git merge-base --is-ancestor lat/hc-3 hop-nhat-20261023` → 0. CD-110 ghi mốc 21:38; giờ commit ghi nhận là 21:39:42, cùng bản sửa route, không phải màn 7 ngày.

## 3. Các lát còn lại của chuỗi

**T** = test thuần/mock nhanh + review chéo; **N** = T + kiểm PostgreSQL phần liên quan và review thay đổi CSDL/quyền do lead tổ chức; **M** = lead chạy trọn giao diện trên DEMO, có ảnh và phút thực tế. Worker không chạy/dừng PostgreSQL hay server. So lỗi và skip với nền hiện hành [NEN-TEST, mục 00 — v6](../../46-chuyen-doi-dieu-phoi/NEN-TEST.md), đồng thời đo trước/sau các bộ liên quan. Màn mẫu làm song song phần lõi theo CD-058; chỉ ghi đã nối khi có bằng chứng chạy thật.

| Lát | Thuộc thành phần | Kết quả phải có, phần dùng lại | Phụ thuộc / thứ tự | Giờ còn lại — ước tính | Kiểm |
|---|---|---|---|---:|---|
| CE-3 | Hủy/chạy lại | Dùng trạng thái của CE-1/2: hủy an toàn; lỗi dừng ở đúng bước; chạy lại từ bước lỗi tạo lần mới, giữ lịch sử và kết quả trước còn dùng được; kết quả không còn thì báo cần chạy từ đầu | Sau CE-1/2 đã gộp; kiểm quyền chủ việc và phiên bản cập nhật | 4 | N |
| CE-4a | Lõi điều phối | Dùng phiếu đăng ký và bộ kiểm CE-2: kiểm khớp ra/vào khi nhận chuỗi từ gói module và khi Áp dụng; bước sau chỉ nhận đúng dữ liệu đã lưu của bước trước theo thứ tự khai. Thêm engine chỉ đăng ký/khai chuỗi, không sửa engine cũ hoặc điều phối | Sau CE-2 đã gộp; kiểm qua quyền/lease hiện có | 3 | N |
| CE-4b | Lõi điều phối / hàng chờ | Dùng bộ chạy CE-1 và hàng việc HC-1: nhận xong → lưu kết quả → mới đẩy bước kế; hết bước trả module. Gián đoạn không mất kết quả hay tạo trùng bước; việc đang chạy giữ định nghĩa và phiên bản đã ghim | Sau CE-4a; không tạo hàng việc thứ hai | 5 | N |
| CE-5a | Lõi điều phối | Hoàn thiện các thao tác bắt đầu/xem/hủy/chạy lại và báo kết thúc qua kênh Core hiện có, đúng phạm vi; không mở cổng gọi engine trực tiếp | Sau CE-3 và CE-4b | 2 | N |
| CE-5b | Lõi điều phối / nối module | Dùng SDK và kênh được duyệt để module gửi một việc, theo dõi và nhận kết quả; kiểm tương thích bộ lệnh chuỗi. Phạm vi chỉ phục vụ chuỗi, không làm lại phát hành SDK chung | Sau CE-5a; dùng bản SDK hợp lệ đang được phép, không ghim wheel candidate | 2 | N |
| CE-6 | Màn xem / thao tác chuỗi | Dùng cửa trình duyệt đã đăng ký để xem/hủy/chạy lại và lưu/áp dụng chuỗi; Admin module chỉ sửa của mình, Admin Core xem/sửa tất cả, người thường không sửa; kiểm tại Core | Sau CE-3/4b; nối dần cùng CE-5a, màn mẫu làm sớm | 3 | N |
| CE-7 | Màn xem / quản lý chuỗi | Dùng CE-0/HC-2: màn trong phần quản lý từng module hiện bước theo thứ tự, **Lưu nháp → Áp dụng**; bản nháp không đổi việc đang chạy. Một dòng trong Việc của tôi, mở chi tiết bước, vị trí chờ, lỗi và kết quả; không dựng màn quản lý chuỗi riêng ngoài module | Mẫu song song CE-3/4a; nối CE-5b/6 và dữ liệu HC-1/2 đã gộp | 5 | T + M; quyền kiểm ở CE-6 |
| CE-8 | Bài nghiệm thu | Chuẩn bị và chạy bài 2–3 engine qua màn module; đo thời gian, ảnh, ca lỗi/quyền/hủy/chạy lại, kiểm bản chuỗi cũ/mới. Gộp phần cập nhật hướng dẫn/chuẩn còn nợ CE-9b vào đầu ra của lát này | Sau các lát trên; module và engine được chọn chạy được trên DEMO | 4 | T + N + M; bản đầy đủ tại mốc |
| **Tổng** | **5 nhóm thành phần trong phạm vi CD-110** | **8 lát cần mở sau khi phiếu sửa được duyệt** | CE-1/2, HC-1/2 không giao lại | **28** | Chưa tính thời gian chờ hoặc lỗi chưa biết |

**Luồng phụ thuộc chính:** CE-4a → CE-4b → CE-5a → CE-5b; CE-3 song song CE-4a, rồi hợp vào CE-5a/6. CE-7 dựng mẫu từ đầu, nối cùng CE-6; CE-8 sau khi cả đường module và giao diện đã nối. Lõi dùng lại HC-1/2, không giao thêm lát hàng chờ trùng. Lead khóa tệp và quyết số lát song song khi mở triển khai; bảng này không mở quyền sửa mã.

**Quy tắc giao diện:** tên bước và thông báo dùng tiếng Việt nghiệp vụ; ngày **dd/mm/yyyy**, không xưng “Anh”/“bạn” trên màn. Không hiện mã contract, schema, UUID, băm hoặc số phiên bản kỹ thuật trên màn nghiệp vụ; thông tin hỗ trợ thu gọn, thông tin quản trị kỹ thuật theo CD-102. Ví dụ nút/nhãn: “Lưu nháp”, “Áp dụng”, “Đang chờ”, “Dừng ở bước…”, “Chạy lại từ bước lỗi”.

### Tách khỏi mốc nghiệm thu chuỗi

| Việc cũ | Nơi theo dõi / xử lý sau CD-110 |
|---|---|
| **34b, 34, 13c, 38, 39, 40b** | Đóng gói chung, theo [KE-HOACH-G3-GOI](KE-HOACH-G3-GOI.md) và [phiếu nghiệm thu tổng thể](PHIEU-NGHIEM-THU-TONG-THE.md); **không là lát/gate của CE-8, không tính giờ tại phiếu chuỗi**. Không sửa các phiếu chủ trì trong lát tài liệu này. |
| **CE-K — kiểm chéo Cloud** | **Bỏ khỏi v1**, không cộng giờ, không có ca nghiệm thu riêng tại phiếu chuỗi. Khả năng/an toàn Cloud thuộc phiếu Hỏi AI/Mask; chuỗi chỉ nối engine được khai và đã sẵn sàng, không tự mở nhánh Cloud. |
| **TINH-TRANG-7N** (tên cũ HC-3 trong phiếu) | **Bỏ khỏi v1, để sau**: màn tình trạng hệ thống theo engine 7 ngày. Không bỏ hoặc làm lại bản sửa `lat/hc-3` về route việc 1.3 đã gộp. |
| **CE-9b — cập nhật tài liệu** | Không mở lát độc lập; đầu ra hướng dẫn/chuẩn phản ánh kết quả nằm trong CE-8. CE-9 đã gộp vẫn dùng lại. |

Tách đóng gói không có nghĩa bỏ kiểm an toàn: mốc chuỗi vẫn cần các engine **được chọn** đăng ký hợp lệ, đầu ra/đầu vào khớp, quyền đúng và kênh/SDK đang dùng chạy được. Nếu thiếu một khả năng thực sự cần cho chuỗi, lead ghi đúng phần thiếu và điều chỉnh lịch; không mặc nhiên bắt chờ đủ sáu lát chung hoặc đủ năm gói. **Wheel SDK 1.4.1 vẫn chỉ candidate theo G3-GOI §6.3**; phiếu này không đổi version, phát hành hoặc cho phép ghim candidate.

## 4. Ước giờ và ngày chuỗi chạy được

| Thay đổi so phiếu 06/11/2026 | Giờ công — ước tính |
|---|---:|
| Tổng cũ | 60 |
| Tách sáu việc đóng gói chung, giờ cũ chỉ để đối chiếu, không phải dự toán hiện hành của phiếu đóng gói | −20 |
| Bỏ CE-K khỏi v1 | −4 |
| Bỏ màn tình trạng 7 ngày khỏi v1 | −3 |
| CE-2/HC-1/HC-2 đã gộp: bỏ giờ còn lại ghi trong bản cũ, không làm lại | −7 |
| CE-7: thêm quản lý bản nháp/áp dụng trong module, thay thiết kế màn chỉ đọc cũ | +2 |
| **Còn lại trong phiếu sửa** | **28** |

CE-9b được gộp vào CE-8 nên **không mất phần việc hoặc cộng thêm giờ**: CE-8 cũ 3 giờ + tài liệu 1 giờ = 4 giờ. Quỹ này gồm chuẩn bị, lần chạy đầy đủ đầu tiên, tổng hợp bằng chứng và cập nhật hướng dẫn; chưa gồm sửa lỗi chưa biết hoặc các lượt chạy lặp hằng ngày. 28 giờ là giờ công còn lại, không phải thời gian chờ xử lý của engine hay số giờ lịch liên tục.

**Ngày chuỗi chạy được: 12/11/2026 lúc 17:00 — ước tính có điều kiện.** Tại ngày lập phiếu 07/11/2026, giả định: Anh duyệt phiếu trước khi mở lát; lead có thể bắt đầu ngày **09/11/2026**, cấp ít nhất **8 giờ công/ngày** cho chuỗi trong bốn ngày 09–12/11/2026; có module DEMO và 2–3 engine được chọn đã chạy được, quyền/kênh hiện có đáp ứng. Khi đó quỹ 28 giờ vừa trong 32 giờ dự kiến; màn mẫu và phần lõi làm song song theo mục 3, dành buổi 17:00 ngày 12/11 để xem kết quả.

Đây là **mốc để lead cân đối và trình lại, chưa phải cam kết nguồn lực hoặc báo SẴN SÀNG**. CRM ưu tiên số 1; phần engine theo CD-108/109: Hỏi AI → OCR → Mask → Trích xuất, chuỗi nhận khe trống theo điều phối. Nếu ngày bắt đầu, quỹ giờ hoặc engine DEMO chưa đáp ứng, lead cập nhật ngày dự kiến theo phụ thuộc thực tế trước khi hẹn chạy; không tự lấy ngày 12/11 làm bằng chứng các engine đã xong. Phiếu không yêu cầu chốt lại việc riêng của engine.

**Điểm trình lại:** duyệt phạm vi 8 lát, dự toán 28 giờ và mốc ước tính cùng giả định nguồn lực. Phần cơ chế A và giao diện v1 đã chốt; không đặt lại bảng lựa chọn cũ. Trong lúc chưa duyệt, không mở lát mới của phiếu chuỗi, chuyển khe trống sang việc độc lập theo CD-110 mục C.

## 5. Bài nghiệm thu — DEMO qua màn module

**Chưa chạy trong lát tài liệu này.** Lead chuẩn bị Core thử/cổng DEMO được cấp, module đã bật, chuỗi 2–3 engine sẵn sàng do Anh khai, dữ liệu giả có nhãn DEMO và kết quả mong đợi. Dùng hai Admin module khác phạm vi, một Admin Core và người dùng thường bằng tài khoản DEMO để kiểm quyền. Không dùng hồ sơ thật. Chỉ lead tổ chức PostgreSQL, engine thật và trình duyệt; worker kiểm thuần/mock.

Bắt buộc **đăng nhập → vào module từ trang chủ → gửi việc → mở Việc của tôi → xem từng bước → mở kết quả trong module → F5 → về trang chủ**, có ảnh và phút thực tế. Gọi API hoặc màn mẫu không thay cho bằng chứng đầu–cuối. Thời lượng dưới đây là dự trù thao tác; lead chạy trước phần chờ engine và ghi riêng thời gian chờ thực, không hứa hiệu năng chưa đo.

### Bản rút gọn hằng ngày — buổi 17:00, khoảng 15–20 phút

1. Trước 16:45, lead chạy trước chuỗi DEMO 2–3 engine qua màn module, giữ kết quả, ảnh và ghi nhận phần chưa đạt; không hẹn sẵn sàng khi chưa tự chạy trọn.
2. Buổi 17:00: từ màn module mở chuỗi đã áp dụng, gửi một việc DEMO ngắn hoặc mở việc lead đã chạy nếu engine xử lý lâu; xem một dòng trong Việc của tôi, các bước theo đúng thứ tự, kết quả về module, tải lại trang.
3. Đối chiếu kết quả mong đợi và ghi đạt/chưa đạt, thời gian thực, lỗi và ảnh. Lượt chỉ xem kết quả sẵn ghi rõ, không coi là vừa chạy một chuỗi mới. Khi mốc chưa nối đủ, ghi “Chưa chạy được trọn chuỗi” và bước đang thiếu.

Không chạy lại toàn bộ bài nặng mỗi ngày; bản rút gọn phục vụ buổi 17:00 theo CD-110. Lead vẫn chạy kiểm PostgreSQL theo lịch chung của dự án, không đưa việc đó vào sandbox worker.

### Bản đầy đủ khi báo xong mốc — khoảng 90 phút thao tác, cộng thời gian engine thực tế

| Phút — ước tính | Thao tác qua màn module / Việc của tôi | Phải đạt và lưu bằng chứng |
|---:|---|---|
| 10 | Admin module mở phần quản lý chuỗi khai từ gói, xem bước; Lưu nháp rồi Áp dụng | Đúng thứ tự đã khai; lưu nháp chưa tác động việc mới, áp dụng thành công mới dùng bản mới. Không có trình dựng kéo-thả v1. |
| 10 | Khai một cặp bước DEMO không khớp đầu ra/đầu vào, thử Áp dụng | Core từ chối, báo tiếng Việt dễ hiểu; bản đang dùng vẫn nguyên, chưa xếp việc từ bản sai. |
| 20 | Chạy chuỗi 2 engine, rồi đăng ký thêm engine thứ ba và chạy chuỗi 3 engine theo khai báo | Engine không gọi nhau; Core lưu xong mới đẩy bước kế, cuối trả đúng kết quả về module. Bổ sung engine chỉ qua đăng ký/chuỗi, không sửa điều phối/engine cũ; lead đối chiếu log và thay đổi mã. |
| 10 | Giữ một việc đang chạy, áp dụng bản nháp khác thứ tự đã khai hợp lệ, gửi việc mới | Việc cũ giữ nguyên định nghĩa/phiên bản ghim, việc mới dùng bản vừa áp dụng; không thay giữa chừng hoặc trộn kết quả. |
| 10 | Gửi nhiều việc DEMO, theo dõi một dòng chuỗi, mở chi tiết, F5 | Vị trí chờ/thông báo đúng dữ liệu HC-1/2; từng bước và kết quả không mất sau F5. Chưa đủ mẫu thì không bịa thời gian ước tính. |
| 10 | Tạo lỗi ở bước giữa; hủy khi chờ/đang chạy; chạy lại từ bước lỗi | Không chạy bước sau lỗi/hủy; chạy lại thành lần mới và giữ lịch sử; kết quả trước chỉ dùng lại khi còn hợp lệ. |
| 10 | Lead mô phỏng gián đoạn trên Core thử được phép, khôi phục và xem lại qua module | Không nhân đôi bước, không mất kết quả đã lưu; trả module đúng một kết quả của lần chạy. Không tác động server đang dùng hoặc chạy/dừng dịch vụ trong sandbox worker. |
| 10 | Đổi tài khoản DEMO, thử xem/sửa/hủy việc ngoài phạm vi; Admin Core kiểm các module; quay trang chủ | Admin module chỉ sửa chuỗi của mình, Admin Core xem/sửa tất cả, người thường chỉ thao tác việc được phép; không lộ dữ liệu. Màn đúng tiếng Việt/ngày dd/mm/yyyy, ẩn mã kỹ thuật và không xưng hô. |
| **90** | **Tổng dự trù thao tác bản đầy đủ** | Kết quả từng ca, ảnh, log không bí mật, phút thực tế và phần chưa kiểm được ghi trong biên bản mốc. |

Chỉ báo xong mốc chuỗi khi bản đầy đủ đạt trên DEMO qua màn module, bằng mã đã gộp, có ảnh và phút thực tế. Không dùng mốc này để báo đủ năm gói hoặc nghiệm thu từng engine. Nếu thiếu ca nào, ghi “Chưa kiểm” cùng lý do; không tạo kết quả hay ảnh giả.

## 6. Kiểm của lát PHIEU-CHUOI-SUA

Chỉ sửa phiếu này; chưa chạy DEMO, PostgreSQL, engine hoặc dịch vụ ngoài, chưa có kết luận nghiệm thu vận hành. Test thuần/mock liên quan được đo trước/sau theo cùng lệnh: Python `test_chuoi_1`, `test_chuoi_2`, `test_hang_cho_1`; Node `tests/ui_hang_cho.cjs`, `tests/chuoi_mau.cjs`. Kết quả và kiểm UTF-8, phạm vi tệp, `git diff --check` ghi trong báo cáo trả lead. Bản trước CD-110 bên dưới được giữ nguyên, chỉ làm tư liệu lịch sử; các trạng thái, giờ và câu chờ duyệt cũ không điều khiển phiếu sửa.

## Phụ lục — bản trước CD-110

# Phiếu kế hoạch tổng thể — Chuỗi xử lý engine

| BẢNG TÓM TẮT | Nội dung để Anh quyết định |
|---|---|
| Khi xong, Anh thấy và làm được | Từ CRM gửi hợp đồng DEMO một lần; phần mềm tự nhận dạng chữ nếu cần, trích tham số theo loại hợp đồng, hiện ô cần soát; Anh theo dõi một dòng việc, mở từng bước, biết hàng chờ, hủy hoặc chạy lại từ bước lỗi. Quản trị thấy số đo 7 ngày. Kiểm chéo Cloud là nhánh riêng có điều kiện, mặc định tắt. |
| Tổng số lát còn lại | **20 lát: 14 lát chuỗi/hàng chờ/tài liệu, gồm 1 lát Cloud có điều kiện; 6 lát dùng chung, gồm 1 lát dự phòng nối kênh AI nếu thiếu, tính một lần tại phiếu này.** Trong 20 lát, 3 lát đã giao dở được làm nốt theo CD-091. |
| Tổng giờ ước còn lại | **60 giờ công = 40 giờ chuỗi + 20 giờ dùng chung**, gồm bài DEMO cuối 3 giờ. Trong đó 4 giờ Cloud và 3 giờ nối kênh AI có điều kiện; nền là 53 giờ khi không cần hai phần này. Chưa gồm giờ làm OCR/trích/Mask/Hỏi AI/hóa đơn ở phiếu khác, chờ Anh hoặc sửa lỗi chưa biết. |
| Việc chờ Anh | Xác nhận 5 lựa chọn chuỗi đang áp tạm, cách thử lại sau gián đoạn, API/contract mới, hạn giữ tệp, tài khoản Windows, giấy phép nguồn và các phụ thuộc engine. Mỗi việc có ☑ tại mục 4. |
| Trạng thái phiếu | **Đề xuất, chờ Anh đồng ý trước khi mở lát mới** theo CD-091 sửa 10:02. Số lát giao song song sẽ chốt lúc triển khai, không giới hạn tổng thể ở 10 lát. |

## 1. Căn cứ và phạm vi

Theo [CD-091, sửa 10:02 và trạng thái nhận 10:25](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md), mục 0b `CLAUDE.md` tại thư mục chính, [dự thảo chuỗi §C1–C3](../chuan/DU-THAO-CHUOI-ENGINE-v1.md), [kế hoạch G3-GOI §5.2, §6.1–6.5](KE-HOACH-G3-GOI.md), [kế hoạch loại hợp đồng](KE-HOACH-LOAI-HOP-DONG.md) và [sổ quyết định tạm](../../QUYET-DINH.md). Mục 0b chưa có trong `CLAUDE.md` đã commit của worktree; đã đọc bản thư mục chính, không sửa bản đó.

Đã chạy `git log --oneline hop-nhat-20261023` lọc “gộp” không phân biệt hoa/thường bằng PowerShell, cố định mốc **`2f6a05a9`** ngày 06/11/2026; HEAD worktree lúc bắt đầu `462975b4`. Trạng thái đang làm lấy từ CD-091 lúc 10:25 và TRANG-THAI lượt 10:00; không coi một commit trên nhánh lát là đã gộp. Giờ là **ước lượng còn lại của phiếu**, gồm kiểm theo rủi ro, chưa phải số đo. Các mã có chữ “đề xuất” chưa được giao.

Kiến trúc giữ như Anh đã chọn: module gửi yêu cầu cho Core; Core điều phối các engine và giữ kết quả trung gian. Engine không gọi engine khác. Dùng lại hàng việc/quy trình hiện có, không dựng một hàng việc thứ hai. Phạm vi đầu–cuối là OCR → trích theo loại → kết quả CRM; Mask → AI qua cổng chung là nhánh mở sau khi đủ chốt an toàn.

## 2. Hiện trạng — gộp khác với đã chạy được

| Trạng thái tại mốc đối chiếu | Việc bằng lời dễ hiểu | Cột phụ: lát / bằng chứng |
|---|---|---|
| Đã gộp | Màn chuỗi mẫu, có nhãn dữ liệu giả | CE-0 — `02cec4bc`; chưa phải màn chạy thật. |
| Đã gộp | Bộ chạy nền: rẽ nhánh, truyền dữ liệu, thứ tự hàng chờ, xử lý gián đoạn theo quyết định tạm | CE-1 — `78add174`, migration 105; không còn giao lại lát này. |
| Đã gộp tài liệu | Bổ sung dịch vụ chuỗi và checklist hiệu năng/hàng chờ | CE-9 — `a47242fe`; vẫn chờ Anh duyệt chính thức. |
| Đang làm, chưa thấy gộp ở mốc | Bộ kiểm/biên dịch chuỗi; đọc hàng chờ; thông báo trên giao diện | CE-2 đang PG theo CD-091 10:25; HC-1 đã commit vòng 2, chờ PG theo TRANG-THAI 10:00; HC-2 đã giao 10:13, CD-091 cho làm nốt dù giao sau chỉ đạo. |
| Chưa thấy gộp | Hủy/chạy lại, bàn giao từng bước, SDK, route, màn thật, số đo tổng hợp, nghiệm thu cuối, nhánh Cloud | CE-3, CE-4a/4b, CE-5a/5b, CE-6/7/8/K, HC-3. |
| Đã gộp phụ thuộc loại hợp đồng | Công cụ kiểm nhanh, 5 biến thể xây dựng DEMO, 3 hợp đồng dịch vụ DEMO, bộ kiểm danh mục và màn mẫu | LHD-01 `0a1d7f1a`; 02 `c3604ddd`; 02b `be93c82d`; E1 `90839d31`; U1a/U1b `20d0e39a`. LHD là loại hợp đồng, không phải hóa đơn điện tử. |
| Đang làm phụ thuộc loại hợp đồng | Sổ phiên bản danh mục, route và engine nhận loại | LHD-C1/C2/E2 theo CD-091 10:25; chưa thấy gộp tại mốc. |
| Chưa đủ bằng chứng nghiệm thu phụ thuộc | Ghim loại, nối màn thật, logic/hỏi thêm/công bố đầu vào mới, so kết quả và thử toàn luồng | LHD-C3/C4, E3/E4/E5/E6, các bước lead LHD-00/N1/N2; chưa thấy gộp. Đây là phần phiếu trích xuất, không cộng lại giờ tại đây. |

### Đối chiếu đủ bảng 40 lát đóng gói

“Có gộp” bên dưới chỉ là có bằng chứng mã lát, không xóa nợ điều kiện ở §6. Chia nhóm để Anh không phải đọc lại 40 dòng kỹ thuật.

| Nhóm | Đã có bằng chứng gộp | Chưa có bằng chứng gộp / nợ còn lại | Cột phụ: commit tiêu biểu |
|---|---|---|---|
| Mẫu, SDK và Hỏi AI, 01–09 | 01–08 | 09 ghim cuối sau 34 | 01 `32bc97ba`; 03 `3197a08d`; 04 `ae193eb0`; 05 `770d01bb`; 06 `b4da0146`; 07 `d8e91e7c`; 08 `8a380c45`; 02 `372d83a8` |
| Phát hiện gói/quản trị, 10–14 | 10, 11, 12, 13/13b, 14 | **13c chưa có**, xử lý nối thư mục thật; 13/13b chưa làm phần này | 10 `5a6ffa10`; 11 `f73d8a13`; 12 `058cd6a3`; 13/13b `df35defc`; 14 `b5e6c301` |
| Nhận dạng chữ, 15–20 | 15, 16 | 17–20 chờ nguồn/giấy phép và ghim cuối | 15 `11d86468`; 16 `331c5620` |
| Hóa đơn, 21–26 | 21–24 | 25–26 chờ giấy phép/nguồn Node, ghim | 21 `8bbecffe`; 22 `ce6cba38`; 23 `f9736561`; 24 `8c410cee` |
| Che định danh, 27–30 | 27, 29, 30 phần tài liệu | 28 công bố năng lực; **30 còn nguồn/lock**, kê 30b ở phiếu Mask | 27 `fa9d40a6`; 29 `08b375b6`; 30 `18c726c1` |
| Trích xuất, 31–37 | 31, 32, 33 | 34–37; 33 vẫn nợ độ chính xác Track Changes §6.2 | 31 `75585712`; 32 `51aab416`; 33 `97846a95` |
| Cổng cuối, 38–40 | 40 tài liệu đã gộp sớm | 38, 39; 40 cần bổ sung sự thật sau nghiệm thu, kê 40b | 40 `5127989a`; commit đã nhắc tài liệu còn ghi 13 chờ dù 13 đã gộp |

Có dòng gộp cho **26/40 mã gốc**, 14 mã chưa thấy gộp: 09, 17–20, 25–26, 28, 34–39. Trong 26 mã có gộp, 13, 30 và 40 vẫn có nợ nêu trên; không báo 26 lát hoàn tất vận hành. Phần riêng từng engine ở phiếu tương ứng; 6 lát chung, kể cả dự phòng nối kênh AI, tính duy nhất trong mục 3 dưới đây.

## 3. Đủ mọi lát còn lại, thứ tự và giờ

**Loại kiểm:** T = test thuần nhanh DEMO/mock + review chéo Codex. N = T + PG đầy đủ cho phần liên quan do lead chạy + Opus, dùng khi đụng CSDL/quyền/tiền/bí mật/xóa; có Windows thật khi cần. Các bảng hiển thị thuần chỉ T; nếu phát sinh sửa quyền/CSDL phải phân loại lại N trước giao. Lát mới so mã lỗi và skip với nền hiện hành; bộ ngoài nền đo trước/sau cùng môi trường, không nới kiểm để xanh.

| Thứ tự | Việc Anh nhận được | Phụ thuộc / tình trạng | Giờ còn lại | Kiểm và lý do | Cột phụ: mã lát |
|---|---|---|---:|---|---|
| 1 | Chuỗi của module được kiểm đúng cấu trúc và ghim đúng engine/phiên bản, nhánh ra Cloud không vượt Mask | CE-1 đã gộp; **đang PG**, làm nốt; contract mới còn chờ Anh | 3 | N — ghim/quyền/bí mật khi ra Cloud | CE-2 |
| 2, cùng 1 | Hàng chờ có vị trí và số đo thời gian đúng pháp nhân | CE-1; **đang chờ PG** sau commit vòng 2, làm nốt | 2 | N — CSDL/quyền đọc việc | HC-1, migration 106 |
| 3, cùng 2 | Thông báo đã gửi, vị trí chờ, chuông báo và thời gian ước khi đủ mẫu | HC-1; **đã giao 10:13**, được làm nốt; mẫu trước, nối sau | 2 | T — giao diện, không đổi quyền | HC-2 |
| 4 | Hủy an toàn; chạy lại từ bước lỗi thành lần mới, giữ lịch sử | CE-1/2; đủ quyền chủ việc, kiểm phiên bản khi cập nhật | 4 | N — CSDL/quyền | CE-3, migration 107 thay số 105 trong dự thảo cũ |
| 5 | Bước sau nhận đúng dữ liệu bước trước, kiểm dấu vân tay tệp và mẫu đầu vào | CE-2; dùng lease đang hiệu lực | 3 | N — quyền đọc dữ liệu/lease | CE-4a |
| 6 | Kết quả từng bước lưu xong mới đẩy bước sau; khởi động lại không mất/nhân đôi chuỗi | CE-4a; ghi kết quả và hoàn tất cùng giao dịch; phiên ủy nhiệm đúng phạm vi | 5 | N — CSDL/quyền/phiên ủy nhiệm | CE-4b |
| 7 | Các thao tác chuỗi dùng được qua kênh Core | CE-3, CE-4b | 2 | N — quyền/ủy nhiệm kênh | CE-5a |
| 8 | Module có bộ lệnh bắt đầu/xem/hủy/chạy lại, nhận thông báo kết thúc | CE-5a; wheel SDK cuối phải tương thích cổng đóng gói | 2 | N — truyền danh tính/quyền qua SDK | CE-5b |
| 9, có thể cùng 7 | Trình duyệt xem/hủy/chạy lại qua đúng cửa đã đăng ký trong ứng dụng thật | CE-3, CE-4b; kiểm cả thiếu quyền/chuyển pháp nhân | 3 | N — quyền và thao tác ghi | CE-6 |
| 10, mẫu sớm đã có | Một dòng chuỗi trong Việc của tôi, mở chi tiết từng bước; màn Chuỗi của module chỉ đọc | CE-0 đã gộp, CE-6, dữ liệu thật từ 2/6; không chỉ đổi màn mẫu | 3 | T — giao diện theo quyền API đã kiểm | CE-7 |
| 11 | Tình trạng hệ thống theo engine 7 ngày; cây Xem dữ liệu có nhánh Core | HC-1; bố cục CD-075/077; giữ khóa tệp UI | 3 | T — hiển thị số tổng hợp từ cửa đọc hiện có | HC-3 |
| 12a, dùng chung, có điều kiện | Nối đường gửi/nhận AI còn thiếu giữa SDK và cổng chung; nếu đã đủ thì chứng minh và bỏ dự phòng | Lead khảo sát wire theo §6, trình phần vượt chuẩn để Anh duyệt trước giao; không thêm client AI hay RPC tổng quát | 3 | N — bí mật/quyền qua kênh Core | G3-GOI-34b, đề xuất dự phòng; phải hoàn tất trước chốt 34 |
| 12b, dùng chung | Đường AI trong trích qua SDK/cổng chung, chốt SDK mới; lớp cũ và dấu vết không đổi | 05/07/22/33 và LHD-E2 đang sửa cùng tệp; wire đã kiểm hoặc 34b xong | 4 | N — bí mật/quyền, wheel sạch/alias/hash | G3-GOI-34 |
| 13, dùng chung | Nối thư mục gói thật sau đủ chốt an toàn và so mã băm registry | Bốn điều kiện §6.1/6.5; mọi pin có gói đúng; quyền kiểm kê mọi pháp nhân | 4 | N — quyền/độ tin cậy mã chạy | G3-GOI-13c, phần đã chuyển từ 13 |
| 14, dùng chung | Đủ năm gói chạy độc lập ngoài repo chỉ với SDK/phụ thuộc đã ghim | Ghim 09/20/26/30b/37 sau 34; nguồn Mask và manifest 28 đủ | 4 | T — kiểm package/contract độc lập; không chạy dịch vụ thật | G3-GOI-38 |
| 15, dùng chung | Kiểm gói → sổ đăng ký → phiên bản đang dùng → giao diện và chạy việc đúng | 13c, 38, 11–14; chưa đủ Mask thì chỉ báo mốc một phần | 4 | N — CSDL/quyền/bí mật; Windows/browser DEMO | G3-GOI-39 |
| 16, có điều kiện | Kiểm chéo Cloud qua Mask; bị chặn thì vẫn trả kết quả nội bộ kèm cảnh báo theo phương án đề xuất | AI-3 của G3 + Mask công bố capability/schema + Anh duyệt; Local vẫn đủ dùng | 4 | N — bí mật/quyền/tiền, Cloud giả trước; không tự gọi dịch vụ ngoài | CE-K |
| 17 | Anh bấm trọn luồng trên DEMO, có ảnh và giờ từng bước, thử lỗi/hủy/chạy lại | CE-1…7; HC-1…3; OCR/trích/CRM và các gate sẵn sàng; CE-K nếu nghiệm thu nhánh đó | 3 | N — bài cuối quyền/tiền/bí mật; lead chạy Windows/PG | CE-8 |
| 18 | Chuẩn chuỗi/hướng dẫn module/checklist phản ánh đúng điều đã nghiệm thu | CE-9 đã gộp; cập nhật sau CE-8, ghi quyết định chính thức của Anh | 1 | T — tài liệu UTF-8 | CE-9b, đề xuất phần bổ sung |
| 19, dùng chung | Tài liệu engine có ảnh/đường mở thực tế, sửa nhận định cũ về 13 và trạng thái chờ | 39, CE-8; 40 đã gộp, không giao lại toàn bộ | 1 | T — tài liệu và ảnh đã quan sát | G3-GOI-40b, đề xuất phần còn nợ |
| | **Tổng 20 lát** | **14 riêng chuỗi + 6 chung** | **60** | **40 + 20 giờ** | |

Sáu lát chung là 34b, 34, 13c, 38, 39, 40b; không cộng chúng lần nữa vào phiếu Mask/hóa đơn. Ba lát đang dở CE-2/HC-1/HC-2 có tổng **7 giờ còn lại ước**, không phải tổng giờ đã làm. Nhánh Cloud 4 giờ chỉ mở khi đủ điều kiện; 34b dự phòng 3 giờ vì §6 chưa chứng minh wire đủ. Nếu phát sinh thiết kế transport lớn hơn, lead phải trình lại giờ/phạm vi trước giao, không coi 3 giờ là trần. Lát CE-9b/40b là nợ cập nhật tài liệu cụ thể, không tạo quy trình kiểm hoặc handoff mới.

### Các phụ thuộc phải nhìn thấy trước khi hẹn ngày

| Cổng / phần còn thiếu | Cách xử lý trong tổng thể, tránh bỏ sót hoặc cộng trùng |
|---|---|
| Nguồn OCR, gói 17–20 và nghiệm thu ABBYY/OCR-5b thật | Thuộc phiếu OCR. Được phép nguồn trước; tài khoản Windows và kết quả DOCX/hash đúng mới mở CE-8 nhánh PDF. Màn engine giả không thay bằng chứng này. |
| Trích 34–37 và loại hợp đồng | 34 là cổng chung tính tại đây. 35/36/37, LHD-C1…C4, E2…E6 và 00/N1/N2 thuộc phiếu trích. Các lát đã gộp không giao lại. C3 ghim danh mục phối hợp CE-2/4a; C4 nối màn; E5 công bố mẫu đầu vào mới theo duyệt của Anh. |
| Đo trích sau đổi nguồn, §6.2 | G3-GOI-33 đã gộp nhưng Track Changes còn nợ: kiểm nhanh đúng phương pháp được CD-071/072 cho phép, so trước/sau cùng mẫu/cách chấm, thấp hơn thì báo Anh. Không phục hồi phép đo lớn TRICH-4b đã bị CD-071 hủy; không dùng hồ sơ thật. Tệp .doc không đưa Word COM vào engine; catalog ngoài git phải kiểm đúng mã băm. |
| SDK, §6.3 | Wheel 1.4.1 dựng sau lát 04 chỉ là ứng viên. 34 chốt phiên bản mới và alias lớp cũ, giữ hash/tiền/Issue; kiểm import sạch, pickle/type hints khi cần. Sau đó mới khóa 09/20/26/30b/37; không ghi đè cùng version khác nội dung. |
| Nguồn/giấy phép, §6.4 | OCR 17 và hóa đơn 25 chưa có quyền nguồn đủ bằng chứng thì giữ Chờ; chuỗi không tự cấp phép. Hóa đơn không nằm trong luồng hợp đồng nhưng chặn mốc nghiệm thu đủ năm gói ở 38/39. |
| Nối gói thật, §6.1/6.5 | 13c phải chặn bộ nhớ đệm bytecode và tắt ghi bytecode khi chạy; root trùng nơi shim nạp; chỉ đọc gói đã ghim mỗi lượt; log loại lỗi cố định không lộ đường dẫn; so mã băm registry/gói, kiểm quyền trên mọi pháp nhân. Kiểm mã trên đĩa không được gọi là chứng thực mã đã nạp. |
| Mask/Hỏi AI | Schema/source/cấp khóa an toàn và AI-3 của G3 chưa đủ thì CE-K giữ Chờ; không nhận commit AI-3 lịch sử của engine #6 là tích hợp G3 đã xong. |
| CRM và dữ liệu DEMO | CRM phải khai chuỗi, chọn loại và nhận kết quả qua SDK (CR9a tại repo CRM do lead điều phối); không sửa repo CRM trong lát phiếu này. Chỉ dữ liệu giả có nhãn và pháp nhân DEMO; màn CRM chưa bật được thì bài CE-8 chưa kiểm. |

## 4. Việc chờ Anh — ☑ là đề xuất, chưa phải duyệt chính thức

| Câu cần Anh xác nhận | ☑ Phương án đề xuất | Phương án khác / cách đổi lại | Cột phụ |
|---|---|---|---|
| Cách hiện chuỗi | ☑ Một dòng, bấm mở từng bước và giờ chạy | Mỗi bước một dòng; đổi màn nhóm việc | C3-1; QD-TAM-20261106-01 |
| Khi lỗi | ☑ Dừng ở bước lỗi; chạy lại từ bước lỗi thành lần mới, giữ lịch sử và kết quả còn hạn | Chạy từ đầu mỗi lần; đổi CE-3/7 | C3-2; QD-TAM-01 |
| Kiểm chéo Cloud | ☑ Mặc định tắt theo module; còn sót thì không gửi, vẫn trả kết quả nội bộ kèm cảnh báo chưa kiểm chéo | Dừng cả chuỗi khi không che được; hoặc chưa làm Cloud trong v1 | C3-3; QD-TAM-01; luôn qua Mask và cổng AI |
| Loại hợp đồng và phiên bản danh mục | ☑ Đầu vào mới mang tệp + loại + phiên bản/mã băm; giữ bản cũ trong thời gian chuyển | Khai chuỗi riêng cho từng loại với mẫu vào cũ; đổi CE-2/LHD-E5 | C3-4; QD-TAM-01; `yeu_cau_trich.v1`, `trich.tham_so_hop_dong@2`; không đăng ký trước duyệt |
| Thứ tự hàng chờ, số phút dự kiến | ☑ Mỗi engine một hàng; bước tiếp dùng giờ gửi chuỗi; chỉ hiện phút khi có ít nhất 5 lần xong trong 7 ngày | Xếp theo giờ tạo từng bước, hoặc hiện sớm kèm độ tin cậy thấp | C3-5; QD-TAM-01; HC-1/2 |
| Gián đoạn còn lượt thử | ☑ Chưa dừng chuỗi khi còn xếp lại được; hết lượt/lỗi kết thúc mới dừng | Dừng ngay theo câu cũ của dự thảo; sửa tiếp ở CE-3 vì CE-1 đã gộp | QD-TAM-20261106-06; khác dự thảo B3 cũ |
| Phạm vi chuẩn mới | ☑ Duyệt dịch vụ chuỗi, kênh, ba cửa trình duyệt, mẫu hiển thị việc và thông báo kết thúc kèm 5 câu trên | Giữ dự thảo, chưa công bố phần vượt chuẩn | Dự thảo B5/C3; CE-9 gộp tạm; DTO 1.3, 4 operation, sự kiện kết thúc |
| Các mặc định chưa thành quyết định chính thức | ☑ Không thêm bảng log; tệp trung gian giữ 30 ngày theo cơ chế có sẵn; mốc đã xem chuông lưu trình duyệt; định nghĩa chuỗi nạp theo pháp nhân ở lần dùng đầu và kiểm mã băm | Anh đổi hạn giữ/cách ghi nhận; quá hạn thì chạy lại từ đầu. Không thực hiện xóa để nghiệm thu khi chưa có phép | Dự thảo C2; cần xác nhận riêng, không suy đã nằm trong QD-TAM-01 |
| Danh mục theo loại, cách cấp catalog và SDK | ☑ Xác nhận các lựa chọn tạm đã ghi; contract nghiệp vụ vẫn phải duyệt trước đăng ký | Đổi phạm vi dùng chung/quyền kích hoạt/cách cấp catalog thì lead sửa các lát liên quan | QD-TAM-20261106-02, -04, -05, -07; chi tiết thuộc phiếu trích; -07 giữ con trỏ Đang dùng bằng dòng dữ liệu, không nhét vào cấu hình hồ sơ |
| Màn kiểm kê năm engine | ☑ Giữ đường kiểm kê riêng có kiểm quyền, dữ liệu thật/giả/chờ rõ ràng | Đổi cách phiên bản hóa đường kiểm kê trước công bố | QD-TAM-20261106-03 |
| Giấy phép và tài khoản Windows | ☑ Anh xác nhận quyền nguồn OCR/Node/Mask và tài khoản riêng cho từng engine trước vận hành thật | Giữ nhánh cần quyền ở Chờ, tiếp tục phần mẫu/thuần đã được duyệt | Không dùng QD-TAM thay phép phần mềm, đổi Windows, ghi két hoặc đụng dữ liệu thật |

CD-091 thắng các câu “làm ngay sau QD-TAM” trước đây: phần engine mới chỉ mở khi Anh đồng ý phiếu. Trong khi chờ, lead làm việc độc lập khác; các lát đã giao dở nêu ở đầu được làm nốt.

## 5. Bài test tổng thể cuối — 180 phút, chưa chạy

Lead chuẩn bị Core thử được cấp tại `http://127.0.0.1:8790` hoặc cổng thử đã xác nhận; CRM đã bật, pháp nhân DEMO, hai tài khoản DEMO khác phạm vi, OCR/Local/engine cần dùng đã kiểm sẵn sàng. Có các tệp tự tạo ghi “Dữ liệu giả — DEMO”: một hợp đồng PDF, bản DOCX cùng nội dung; mẫu xây dựng có đáp án 37 tham số, mẫu dịch vụ từ bộ 3 hợp đồng DEMO; một tệp hỏng, một ca cố ý sai mã băm/mẫu dữ liệu và tệp trung gian giả lập quá hạn. Không lấy hồ sơ thật làm mẫu; không đổi máy chủ hay khởi động dịch vụ trong sandbox worker.

Tên nút là tiêu chí của giao diện đích, chưa khẳng định hiện đã nối. Bài bắt buộc đi qua màn CRM; API hay engine giả chỉ phục vụ chẩn đoán, không thay kết quả chạy đầu–cuối.

| Phút | Anh bấm gì / ai hỗ trợ | Phải thấy gì và lưu bằng chứng nào |
|---:|---|---|
| 10 | Quản trị Core → Quản lý engine; mở CRM → Hợp đồng → Tải hợp đồng mẫu | Đúng phiên bản, trạng thái thật/giả/chờ; chọn đúng loại và danh mục đang dùng. Không ngầm mượn danh mục xây dựng khi loại thiếu. |
| 25 | Chọn PDF DEMO → Đọc hợp đồng → Việc của tôi → mở dòng chuỗi | Một dòng, OCR rồi trích, giờ từng bước; Core giữ tệp trung gian và dấu vết. Cuối có bảng tham số và ô vàng cần soát trong CRM; đối chiếu đáp án DEMO, không mặc định 37 mã cho mọi loại. |
| 20 | Chọn DOCX DEMO cùng nội dung; chạy mẫu dịch vụ với đúng danh mục | DOCX bỏ qua OCR có lý do; mẫu xây dựng khớp đáp án, dịch vụ dùng bộ tham số của dịch vụ. Giao diện không treo vì chờ máy AI. |
| 15 | Gửi nhiều việc DEMO cho cùng engine; mở chuông/Việc của tôi/Hàng việc | Vị trí, số việc trước và thứ tự đúng; bước kế ưu tiên theo giờ gửi chuỗi. Chưa đủ 5 lần xong trong 7 ngày thì không bịa số phút; sau đủ mẫu mới hiện ước tính. |
| 25 | Chạy tệp lỗi; xem bước dừng; bấm Chạy lại từ bước lỗi; chạy ca trung gian quá hạn | Không chạy bước sau khi lỗi; lần chạy lại mới giữ lịch sử, tận dụng bước trước còn hạn; quá hạn yêu cầu chạy từ đầu. Sai mã băm/mẫu dữ liệu bị từ chối trước bàn giao. |
| 20 | Bấm Hủy lúc đang chờ/đang chạy; lead mô phỏng gián đoạn có kiểm soát và khởi động lại Core thử | Dừng an toàn, không có kết quả giả thành công; không nhân đôi bước sau khởi động lại; còn lượt thử thì chờ/thử lại, hết lượt mới dừng theo quyết định tạm đã được xác nhận. |
| 15 | Đổi tài khoản/pháp nhân DEMO, thử xem/hủy/chạy lại chuỗi của người ngoài phạm vi | Từ chối đúng quyền; không lộ tệp trung gian hoặc nội dung tham số. Quay tài khoản có quyền thấy đúng lịch sử. |
| 20 | Để cờ Cloud tắt, chạy mẫu; nếu đủ CE-K thì bật nhánh với bộ thu Cloud giả, thử Mask còn sót và danh mục khóa | Khi tắt không có lượt Cloud. Khi Mask chặn không chuyển bản gốc; kết quả nội bộ kèm cảnh báo theo phương án đã chốt. Khi an toàn chỉ bản đã che tới bộ thu giả. Không gọi dịch vụ Cloud ngoài trong bài này. |
| 15 | Tình trạng hệ thống → từng engine; Hàng việc → lọc engine; tải lại trang | Số việc/giờ chạy 7 ngày khớp các việc DEMO, chuông/chi tiết không sai sau tải lại. Ghi rõ tài khoản Windows OCR đã thực sự dùng, không đưa mật khẩu vào ảnh. |
| 15 | Anh xem bộ ảnh CRM, từng bước, lỗi/chạy lại và số đo; lead đối chiếu cả năm gói | Ghi đạt/chưa đạt theo từng mốc, phút kiểm từng lát so với tổng thể; thiếu Mask/nguồn/Windows thì báo mốc một phần, không tuyên bố đủ năm engine. |

Chạy bài đầu–cuối **hằng ngày và trước khi báo xong mốc**, PG toàn bộ **một lần/đêm** theo CD-091; không nhân thời gian này vào từng lát. 180 phút là dự trù thao tác và chờ trên DEMO, sẽ đo lại; không phải cam kết hiệu năng OCR/AI. Phiếu này chỉ khảo sát/lập kế hoạch: **chưa chạy bài DEMO, PG, engine hay dịch vụ ngoài; chưa có kết luận nghiệm thu vận hành**.
