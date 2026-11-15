# MASK-P3 — Mở che và kho bí danh theo SDK 2.2.0

*Ngày 15/11/2026 · Codex trình lead/Anh · CHỈ TÀI LIỆU · PR: chờ lead mở.*

## 1. Kết luận và căn cứ

**Đề xuất A: kết quả giữ bí danh, kèm mã tham chiếu nội bộ; người có quyền xem bản rõ tại cửa Xem dữ liệu của Core.** Engine không khôi phục bản rõ từ dữ liệu đã lưu. Đây là thay đổi nghiệp vụ so với MASK-5 và MASK-B8, cần Anh chọn trước khi giao code. Giữ định dạng Word/Excel vẫn là mục tiêu; trả tệp có tên gốc sau AI sửa không còn là tiêu chí của A.

**CĐ-36 — Anh, 15/11/2026 16:28 (ghi nguyên văn ý theo lệnh giao):**

> KHÔNG mở đường Core giải mã hộ engine. Trường bi_mat chỉ mã hóa khi ghi, tìm theo băm, engine đọc ra null. Mask phải đổi cách gỡ che (ví dụ trả về bí danh hoặc mã tham chiếu, bản rõ chỉ người có quyền xem qua cửa Xem dữ liệu của Core). Không làm đường giải mã nào khác.

Quyết định này đóng hướng “chờ đường giải mã cho Mask” trong `_chung/docs/CHUYEN-SDK-2.2.md` §2 và `THAY-DOI-2.2.0.md`. MASK-P3 không sửa hai tài liệu nguồn; lead cập nhật thông báo chung sau. Các yêu cầu cũ “không mã hóa cột”, “tra ngược ra tên gốc”, “khứ hồi nguyên bytes gốc qua engine” trong quyết định 06/11 và phiếu B8 không được dùng để đi vòng CĐ-36.

Căn cứ đã đối chiếu: `AGENTS.md`; API-ENGINE-v1; hướng dẫn/phiếu SDK 2.2.0 và ghi chú thay đổi; các quyết định sáng/chiều 15/11; GIAO-CODEX-DOT-2, GIAO-CODEX-THU-TU, DE-NGHI-SDK-2.1; LOAI-DU-LIEU-RIENG §3; GIAO-CODEX-e_mask §2, MASK-5/6, §7 MASK-B5…B10; CLAUDE, YEU-CAU-VA-HIEN-TRANG, QUYET-DINH-CUOI và VIEC của Mask. Trạng thái hiện tại lấy từ gói và bàn giao mới, không lấy bảng hiện trạng 08/11 làm bằng chứng chạy hiện nay.

**Ranh giới kỹ thuật đã có:** Core mã hóa trường `bi_mat` khi ghi, tìm bằng giá trị qua băm; `doc`/`tim` trả `None` và cờ `<ma>_da_ma_hoa`. Cờ này chỉ chứng minh trường được che khỏi engine, không phải quyền xem hoặc dữ liệu để gỡ che. Không coi `None` là chuỗi rỗng, không ghi `None` đè trường bí mật khi sửa metadata. `bi_mat` của cột ngăn khác danh sách tên bí mật `engine.json.bi_mat`.

**Chưa có bằng chứng cổng:** quyền mở Xem dữ liệu bằng tham chiếu, biên nhận duyệt từ cửa đó, băm chuẩn hóa/duy nhất và tìm nhiều ứng viên cần Core xác nhận ở §8. Không mô tả các đề nghị này như API SDK 2.2.0 đã có. Phạm vi P3 chỉ hai tệp tài liệu, không sửa mã/schema/manifest/SQL, không nối Core hoặc bật Cloud.

## 2. Hiện trạng: mọi điểm cần bản rõ sau lưu

| Điểm | Bằng chứng trong gói/phiếu | Phụ thuộc bản rõ và tác động SDK 2.2.0 |
|---|---|---|
| `mask.mo_che_van_ban@1` (MASK-5) | `chay.py::_mo_ai`, handler `mo`; `che_van_ban.py::_mo_che`; `kho_qua_core.py` và `kho_ngan.py::PortNgan` | Tra alias → `gia_tri` để thay trong văn bản, mọi giá trị chuỗi `du_lieu`, câu trích. Không thể thay bằng `None`; kết quả bộ M mang tên “đã mở che” sẽ gây hiểu sai nếu vẫn giữ hành vi thành công cũ. |
| Mở tệp MASK-B8, chưa có writer/handler hoàn chỉnh | GIAO-CODEX-e_mask §7, B8 | Không AI sửa: dự kiến engine đọc bytes gốc từ Core để trả lại; AI sửa: cần bản rõ từng alias để patch Word run/Excel rich text. Cả hai không còn là đường khôi phục hợp lệ của A; không lấy tệp gốc/snapshot làm cửa giải mã thay thế. |
| Admin duyệt MASK-6 | `duyet_dinh_danh.py::danh_sach/duyet/nhap_demo`; `ui/duyet_dinh_danh.js` | Đang hiển thị/lọc `gia_tri`, so giá trị, chép cả dòng sang bảng chính thức và xóa dòng chờ. Khi đọc null, Admin không thấy tên, engine không thể chép bí mật sang bảng mới; lệnh xóa cũng không có trong SDK 2.2.0. |
| Đối chiếu chính thức/tạm | `PortNgan` tạo `danh_muc`, `bo_sung`, `tam_theo_cum`; `kiem_bi_danh` | Đang chuẩn hóa giá trị gốc để gom cụm, chọn lại alias theo yêu cầu, kiểm mã Junsky/alias không gắn hai tên khác nhau. So null với null làm mất phân biệt thực thể, có thể gộp nhầm. |
| Chống trùng theo giá trị, gặp lại, nhập DEMO | `kho_ngan.py` dùng `chuan_hoa(gia_tri)` làm khóa; `duyet_dinh_danh.py::nhap_demo`; `che_van_ban.py::_che` | Khóa `khoa`, trường `cum`, dấu `gap` hiện có thể chứa tên đã chuẩn hóa. Chỉ đổi `gia_tri` sang bí mật vẫn để lộ qua khóa/dấu. Cần ID opaque và tìm bằng giá trị hiện có trong RAM, không dùng SHA tên không khóa làm khóa công khai. |
| Dò/hậu kiểm danh mục đã biết | `che_van_ban.py::_che` gọi `liet_ke_dinh_danh`, tạo matcher từ mọi `gia_tri`; `_kiem_con_sot` kiểm tên đã biết | **Ảnh hưởng cả CHE.** Không thể nạp từ điển từ ngăn nữa. Tìm chính xác theo băm chỉ có ích sau khi đã có ứng viên; không tự phát hiện mọi tên, không thay matcher mềm bằng phép so băm rồi tuyên bố giữ chất lượng. |
| Giao lại, mất ACK, bản chụp lựa chọn | `kho_ngan.py::PortNgan` ghi `dau_gap.dinh_danh` có `gia_tri`, đọc lại để tái tạo; `KhoDinhDanh` xử lý chốt | JSON lồng và bản sao lựa chọn là đường lưu bản rõ khác; mã hóa riêng cột `gia_tri` không bảo vệ chúng. Phải giữ ID/alias/phiên bản/băm kết quả; giao lại dựa trên đầu vào/kết quả Core đúng quyền, không tra bản rõ đã cất. |
| Hồ sơ Local, map gốc/che | `ho_so_ai.py` và các bước MASK-2c; B7 dự kiến snapshot tệp | Có nguyên văn và map trong hồ sơ do Core cất, cổng hiện tại mới được tiêm/kiểm giả. Cần tách quyền phục vụ che/Local khỏi bước trả lời/hiển thị; không cho bước “mở che” tải hồ sơ gốc để lách CĐ-36. |

Hiện có handler văn bản và màn duyệt đã kiểm giả; B1…B3 mới là gate/reader nội bộ. B8 là yêu cầu trong phiếu, không phải chức năng đã triển khai. Bí danh chung tập đoàn là nghiệp vụ đã chốt; alias tạm riêng yêu cầu theo sửa an toàn 15/11. Không tự thu hẹp bảng chính thức sang từng pháp nhân, cũng không dùng phạm vi chung để bỏ kiểm module/người/tài liệu/DEMO–thật.

## 3. Ba phương án để Anh so sánh

Giờ dưới đây là **ƯỚC TÍNH công sức engine/tài liệu/test sau khi chốt**, chưa đo; không gồm chờ, code Core/module, đo Local/Office thật hoặc phần B còn lại. Các khoảng là hướng thay thế, không cộng với nhau. Ước tính C chỉ để so sánh, không là đề nghị mở đường trái CĐ-36.

| Phương án | Dữ liệu và nơi giữ | Ưu / nhược | Rủi ro và công sức ƯỚC TÍNH |
|---|---|---|---|
| **A — Alias + tham chiếu, xem bản rõ ở Core** | Ngăn Core: bản rõ gốc/chìa đối chiếu chuẩn hóa đều `bi_mat`; băm tìm do Core quản; metadata ID/nhóm/trạng thái/alias không bí mật. Engine chỉ có đầu vào và ứng viên hiện tại trong RAM; sau lưu chỉ đọc metadata. UI Mask không nhận bản rõ. | Phù hợp CĐ-36 trực tiếp; dùng lại qua nhiều việc mà engine không có kho tra ngược. Đổi trải nghiệm: người dùng xem alias và mở từng tham chiếu, không tải câu trả lời/tệp đã khôi phục tên. Dò danh mục phải thiết kế lại. | Tham chiếu/alias vẫn liên kết được nhiều tài liệu; truy vấn băm có thể bị dò đoán. Cần ACL, audit và giới hạn tìm. **32–46 giờ**, khó; phụ thuộc cửa chung Core. |
| **B — Chỉ cùng một yêu cầu, RAM hoặc hồ sơ Core theo việc** | Bản rõ/ánh xạ chỉ từ đầu vào mới của yêu cầu; RAM của việc hoặc hồ sơ tại kho tệp Core có ACL theo chuỗi; không lưu bền bản rõ trong ngăn. Ngăn chỉ ID/alias/trạng thái, bí mật phục vụ danh mục vẫn đọc null. | Có thể khôi phục trong một chuỗi liên tục nếu cho phép; mất RAM thì mất khả năng khôi phục. Hồ sơ giúp retry nhưng tạo khả năng đọc lại bản rõ. Không mở được ở yêu cầu sau. | **Chỉ biến thể trả alias như A phù hợp CĐ-36 hiện tại.** Engine đọc hồ sơ để thay alias thành tên và trả bản rõ là đường khác, không được triển khai; “tệp tạm” không làm nó hợp lệ. RAM-only trả tên cũng ngoài đề xuất “bản rõ chỉ xem ở Core”. **40–60 giờ** nếu được đổi quyết định; không giao code theo CĐ-36. |
| **C — Module giữ ánh xạ và tự gỡ che** | Ánh xạ lấy từ dữ liệu module vốn có, lưu trong ngăn/kho Core của module, không máy engine; nếu cột `bi_mat`, module cũng không được giả định có API đọc bản rõ. Engine chỉ alias/tham chiếu. Không chuyển bản rõ từ Mask sang module qua kết quả/chuyển tiếp. | Module có thể dựng trải nghiệm theo nghiệp vụ, engine đơn giản hơn; mỗi module phải tự quản ánh xạ/quyền và writer Word/Excel. Không có ánh xạ sẵn thì không khôi phục được từ alias. | **Không đạt CĐ-36 nếu tự gỡ che/hiển thị bản rõ ngoài Xem dữ liệu**, kể cả module gọi Core “hộ”. Không dùng module làm proxy giải mã. Chỉ biến thể module mở cửa Xem dữ liệu (không nhận bản rõ) là A. **28–40 giờ phía engine**, chưa gồm module và writer trùng lặp; không có dự toán module đáng tin. |

### 3.1 Luồng và Admin theo từng phương án

**A:** nguồn mới đúng quyền → che trong RAM, ghi bí mật vào ngăn Core → hậu kiểm hai lớp/tiền-ngày và chốt → `van_ban_da_che` → Core điều phối Hỏi AI → chỉ chuỗi đã che ra Cloud khi cửa Cloud được phép → `tra_loi_ai` còn alias → engine xác minh metadata và trả alias + tham chiếu → module hiển thị alias, người có quyền mở Xem dữ liệu của Core. Bản rõ chỉ tồn tại trên màn Core đúng quyền, không trả qua callback/DOM của màn engine, không được đưa trở lại prompt. Đợt hiện tại giả lập AI, **Cloud giữ tắt**.

Admin của A xem danh sách metadata (alias tạm, nhóm, số gặp, trạng thái), mở từng dòng tại Xem dữ liệu để xem tên. Quyền Admin duyệt và quyền xem bản rõ là hai quyền cần kiểm riêng. Quyết định duyệt dựa trên biên nhận đã xem gắn ID/phiên bản, không kèm tên; engine cập nhật trạng thái/alias trên cùng bản ghi. Không có quyền xem thì không duyệt nội dung một cách mù; có thể để chờ hoặc từ chối theo quy trình được chọn. Lọc tên một phần kiểu Excel không còn ở màn Mask; nếu Core cho tìm đúng giá trị thì thực hiện trong cửa Core, không tạo gợi ý tên từ băm.

**B (luồng giả định, không giao):** nhận mới → tạo map RAM/hồ sơ Core của một yêu cầu → che và gửi chuỗi che qua Hỏi AI → trả lời alias → tải lại map cùng chuỗi để thay tên → hiển thị bản rõ. Chính bước tải map/thay tên/hiển thị là xung đột CĐ-36; không đề nghị API cho bước này. Nếu chỉ RAM mà Cloud trả chậm, lease mất, process restart hoặc retry ở worker khác thì phải từ chối khôi phục; không tạo cache hoặc ghi ngăn làm cứu hộ. Admin duyệt sau chuỗi vẫn cần Xem dữ liệu như A; RAM không phải kho để duyệt bất đồng bộ. Hồ sơ phải do Core thu hồi theo vòng đời việc, không TTL tự đoán, không coi “không ngăn” là “không lưu bền”.

**C (luồng giả định, không giao):** module có map nguồn của mình → engine che → Cloud chỉ nội dung che → trả alias → module tự thay bằng map → hiển thị. Hai bước cuối không được CĐ-36 hiện tại cho phép. Module không được lấy map từ ngăn bí mật, Xem dữ liệu, snapshot hoặc đầu ra Mask. Admin vẫn duyệt tại Core như A; danh mục riêng mỗi module không tự trở thành danh mục chính thức toàn tập đoàn, cần đối chiếu ID/trạng thái và xử lý xung đột tập trung. Cho module nhận bản rõ rồi gọi lại engine là cùng một đường vòng, không phải C hợp lệ.

### 3.2 MASK-B5…B10 và Cần Core của mỗi hướng

| Lát | A đề xuất | B giả định | C giả định |
|---|---|---|---|
| B5 Word | Che story/run/metadata từ đầu vào mới; map RAM phục vụ che, không làm kho gỡ. Chưa có cơ chế dò danh mục kín đạt thì chặn phát hành. | Cùng writer che; map giữ theo yêu cầu, không lan sang việc khác. | Cùng writer che; module không gửi bảng tên trong cấu hình/chuyển tiếp. |
| B6 Excel | Che chuỗi, giữ số/style/tiền-ngày; tên sheet/vùng không được sửa vẫn theo blocker hiện có. | Cần map cùng ô/run; không dùng values-only để khôi phục. | Module phải tự viết phần phục hồi nếu được phép; thiếu map thì không đoán. |
| B7 hồ sơ/hai lớp | Giữ hồ sơ nguồn đúng quyền phục vụ che/Local; bước trả kết quả không được mở nguồn. Snapshot không thành kho tra ngược. | Core phải cách ly hồ sơ theo chuỗi và đóng quyền khi hết việc; đây không phải sự cho phép dùng để gỡ che. | Không chuyển hồ sơ gốc/map sang module qua output; cần quyền nguồn tách biệt. |
| **B8** | **Thay mục tiêu bằng kiểm/định vị alias và tham chiếu trong tệp AI trả.** Tệp giữ alias, không trả bytes gốc, không inverse ra tên. | Chỉ khôi phục nếu đổi CĐ-36; chưa đổi thì B8 trả alias như A. | Chuyển phục hồi sang module chỉ nếu đổi CĐ-36; không được giữ tiêu chí cũ rồi nhận đã đạt. |
| B9 SDK | Năng lực/phiếu mới theo nghĩa “đối chiếu tham chiếu”; trả tệp alias và báo cáo tĩnh. @1 cũ không được thành công với tên trường gây hiểu nhầm. | Cần mô tả một yêu cầu xuyên bước/khởi động lại/quyền hồ sơ; SDK hiện không bảo đảm khả năng RAM qua nhiều việc. | Cần contract module nhận alias/tham chiếu; không API map bản rõ. |
| B10 nghiệm thu | Gold mới cho giữ alias/đủ tham chiếu/đúng quyền/không rò; đo định dạng tệp AI sửa, Office mở/lưu thật. Bỏ SHA khứ hồi gốc qua engine khỏi tiêu chí A. | Đo thêm restart/lease/đóng việc/mất map; không gọi các ca thiếu map là thành công. | Đo riêng mỗi module/writer; không suy nghiệm thu engine thành nghiệm thu module. |
| **Cần Core** | C-P3-01…05 ở §8: Xem dữ liệu, quyền/tham chiếu, tìm bí mật/chống trùng, vòng đời và chuyển đổi. Không giải mã cho engine. | Kế thừa A về danh mục/Admin; thêm hồ sơ cùng chuỗi/quyền thu hồi nếu chỉ dùng cho che. Không yêu cầu cửa gỡ từ hồ sơ. | Kế thừa A; module giữ dữ liệu theo cổng module được duyệt. Không API giải mã hoặc chuyển bản rõ sang module. |

**Đánh giá:** A là hướng duy nhất đề nghị thực hiện trong CĐ-36. B/C được phân tích để làm rõ lợi ích và phần bất khả dụng, không là ba lựa chọn đều hợp lệ. Giữ định dạng theo MASK-P2 “phương án B ZIP/XML” vẫn áp dụng cho A; chữ B của P2 là lựa chọn công nghệ writer, khác phương án B về vòng đời bản rõ trong tài liệu này.

## 4. Kho bí danh đề xuất cho A

### 4.1 Một bản ghi bí mật, metadata tách khỏi giá trị

Thiết kế dưới đây là mô hình logic để lập phiếu chuyển sau duyệt, chưa là schema/migration đã có.

| Dữ liệu | Nơi và cách giữ | Quy tắc |
|---|---|---|
| Định danh gốc `gia_tri` | Ngăn Core, cột `bi_mat: true`; ID opaque làm khóa | Chỉ ghi khi đầu vào mới hợp lệ đang có trong RAM. Đọc lại null + `gia_tri_da_ma_hoa`; không có cột rõ dự phòng. |
| Giá trị đối chiếu `gia_tri_chuan` | Cột riêng cũng `bi_mat: true`; Core băm để tìm chính xác | Chuẩn hóa từ nguồn đang có trong RAM, ghim phiên bản quy tắc; không thay gốc bằng bản chuẩn. Không trả băm bí mật ra UI/Cloud. Core cần xác nhận hỗ trợ duy nhất theo giá trị bí mật, không tự suy từ ví dụ SDK. |
| Metadata thực thể | Cùng dòng: `id_dinh_danh`, vùng DEMO/thật, nhóm, trạng thái `CHO_DUYET/CHINH_THUC/TU_CHOI`, số gặp/phiên bản | Đề xuất dùng một bảng thực thể để duyệt chỉ sửa metadata, không cần đọc rồi chép `gia_tri`. Phạm vi chính thức engine/toàn tập đoàn; quyền xem không suy từ phạm vi lưu. |
| Bí danh chính thức và lịch sử | Bảng alias: alias chuẩn hóa không chứa tên → ID thực thể; trạng thái/phiên bản | Mã MASK… hoặc Junsky hợp lệ, duy nhất giữa các alias đang dùng và lịch sử. Không tái cấp alias cũ cho thực thể khác. Chỉ alias mới nhất là chính thức; alias cũ vẫn tham chiếu được theo quyền. |
| Bí danh tạm | Bảng alias: mã tạm opaque, ID thực thể, mã yêu cầu nội bộ | Riêng yêu cầu; cùng tên ở hai yêu cầu không tái dùng alias tạm. Người dùng không thấy việc tìm được tên ở yêu cầu người khác. |
| Yêu cầu/tham chiếu/gặp lại | ID yêu cầu Core, ID thực thể/alias, ID tài liệu, module/người từ nguồn tin cậy; khóa chống lặp theo việc/lượt | Không tên chuẩn hóa trong `khoa/cum`, không JSON `dinh_danh` có bản rõ; không token tự cấp quyền. Gặp lại tăng đúng một lần sau retry/CAS. |
| Băm | Băm đối chiếu bí mật do Core quản; băm nội dung để toàn vẹn/chống lặp chỉ nội bộ | Không tạo SHA-256 không khóa của tên/MST làm khóa công khai: tập giá trị có thể bị dò. Băm toàn văn cũng không gửi Cloud. Thuật toán/key rotation của chỉ mục bí mật do Core xác nhận, engine không giữ khóa. |
| Hồ sơ gốc/map/tệp | Kho tệp Core có ACL cho che/Local; RAM trong việc; engine không lưu bền trên máy | Không dùng hồ sơ làm bảng ánh xạ ở bước đối chiếu trả lời; không nhét map vào ngăn JSON, log, `chuyen_tiep`, báo cáo. Tạm một việc dọn `finally`; không tuyên bố xóa an toàn tuyệt đối RAM Python. |

Chỉ sửa metadata bằng patch bỏ hẳn khóa bí mật, không gửi null/cờ mã hóa lại cho Core. Đề xuất không chuyển dòng chờ sang bảng khác: duyệt đổi trạng thái trên ID cũ, thêm alias chính thức, giữ alias tạm đang được tham chiếu. Từ chối đổi trạng thái, không xóa vật lý. Dọn là kết thúc hiệu lực alias khi không còn yêu cầu đang xử lý, không xóa dữ liệu bằng lệnh ngoài SDK. Hết hạn SDK chỉ ẩn; `gom_het_han=True` đọc lại metadata không được khôi phục quyền đã đóng.

### 4.2 Chống trùng và giới hạn dò danh mục

1. Khi đầu vào mới chứa cụm cần che, chuẩn hóa trong RAM theo phiên bản đã ghim rồi `tim` đúng giá trị bí mật. Kết quả chỉ cho ID/metadata; không đọc bản rõ từ kết quả. Khác nhóm hoặc khác thực thể cùng alias phải báo xung đột để soát, không gộp theo null.
2. Cần duy nhất phía Core theo vùng + giá trị đối chiếu và duy nhất alias chuẩn hóa. `lay_hoac_tao`/CAS/lô nguyên tử phải chống hai việc tạo hai ID cho cùng cụm. Nếu SDK không bảo đảm tổ hợp khóa/duy nhất bí mật, để C-P3-03; không thay bằng khóa tên rõ hoặc chia nhiều lô rồi coi nguyên tử. Tối đa 100 lệnh/lô, vượt từ chối, không cắt ngầm.
3. Alias chính thức dùng lại theo ID; alias tạm cấp theo yêu cầu và lưu quan hệ tới ID. Admin duyệt không cần tên trong engine; mã Junsky mới được so duy nhất theo alias/ID, không so `gia_tri` null. Retry đọc ID/phiên bản/kết quả đã chốt đúng quyền; mất xác nhận sau nhận chốt → `ChuaRo`, không đếm/tạo lại.
4. **Kho kín không còn là từ điển để liệt kê.** Ứng viên từ detector/Local/danh sách đã biết trong đầu vào mới có thể tìm theo băm, nhưng có thể bỏ sót tên đặc biệt vốn chỉ matcher danh mục cũ nhận ra. A chưa có bằng chứng bảo toàn recall. Không dùng cờ “đã nạp danh mục” khi chỉ nạp metadata.
5. Lát A4 phải khảo sát tìm ứng viên có giới hạn và đối chiếu ngữ nghĩa chuẩn hóa/matcher cũ. Có thể đề nghị Core tìm nhiều ứng viên chính xác trong một lời gọi chung; **không yêu cầu Core quét/giải mã danh mục hoặc trả tên**. Liệt kê mọi chuỗi con dài ≤300 của 500.000 ký tự có thể tới khoảng 150 triệu ứng viên: không chọn làm thuật toán mặc định. Có trần ứng viên/thời gian, vượt hoặc chưa chứng minh đủ thì từ chối; không chỉ chạy detector rồi nhận là tương đương danh mục.
6. Nếu không đạt tiêu chí dò kín, A4 kết thúc bằng báo cáo giới hạn để Anh chọn giảm phạm vi hoặc dừng nối; không phát hành `van_ban_da_che` với bảo đảm cũ. Cloud vẫn tắt, nợ chất lượng MASK-2b/2c giữ nguyên. Không giải quyết phần che bằng việc cấp lại quyền đọc danh mục bí mật.

## 5. Kết quả đối chiếu, quyền và tương thích

**Không đổi nghĩa thành công của `mask.mo_che_van_ban@1` tại chỗ.** Sau duyệt, đề nghị năng lực mới `mask.doi_chieu_bi_danh@1`, trả `truong` tĩnh theo API v1: `van_ban_co_bi_danh` (văn bản), `tham_chieu_json` (chuỗi JSON đã kiểm), `so_cho_doi_chieu` (số), `bi_danh_khong_ro_json` (văn bản), `doi_chieu_day_du` (boolean), `trang_thai_ma_yeu_cau` (văn bản), `tra_loi_ai_co_bi_danh_json` (văn bản hoặc null). Tên còn chờ lead đối chiếu sổ năng lực; không đăng ký tại P3. Tệp tương tự: năng lực mới `mask.doi_chieu_bi_danh_tep@1`, trường `tep_co_bi_danh` và báo cáo tham chiếu tĩnh. Không thêm kiểu cột ngoài SDK.

Một mục tham chiếu nội bộ gồm alias, mã tham chiếu opaque, vị trí trong kết quả và trạng thái đối chiếu. Vị trí văn bản là đường trường/chỉ số Unicode `[bat_dau, ket_thuc)`; tệp là mã vùng/đoạn/ô an toàn, không tên sheet/path có định danh. ID lưu trữ trực tiếp không trở thành URL tùy ý; UI chỉ mở cửa Core từ tham chiếu được Core xác minh. Kiểm trần JSON UTF-8 (tệp theo mức thử nghiệm ≤256 KiB), số mục và thời gian; vượt thì lỗi, không cắt danh sách. `doi_chieu_day_du=true` chỉ có nghĩa đủ alias nhận diện được có tham chiếu hợp lệ, **không có nghĩa đã mở bản rõ**.

`@1` mở che cũ được giữ nhận diện để quy trình cũ báo lỗi nghiệp vụ rõ “Chức năng mở che đã thay đổi. Cần cập nhật quy trình để xem dữ liệu qua Core.”, không tạo kết quả giả/ghi tên trường cũ bằng alias rồi báo `mo_day_du=true`. Lead thống kê quy trình đang dùng và chuyển sang năng lực mới; không cần API giải mã trong giai đoạn chuyển. Năng lực tệp cũ chưa phát hành thì không đăng ký theo nghĩa cũ. Không đổi API-ENGINE-v1 hoặc schema chung trong P3.

Đối chiếu trong `tra_loi`, các giá trị chuỗi lồng `du_lieu`, câu trích; giữ khóa/số/ngày/boolean/null và nội dung AI mới. Nhận diện mềm case/khoảng trắng/tách run chỉ chuẩn hóa để tra alias; giữ nguyên chữ trả lời khi chỉ tạo tham chiếu. Nếu có sửa chữ/alias, hạ kiểm nguyên văn của trích dẫn và ghi cần kiểm lại; offset phải thuộc đúng phiên bản văn bản, không lấy offset trước che áp sang câu trả lời. Alias hỏng/lạ giữ nguyên và báo vị trí, không suy đoán thực thể.

Giữ `van_ban_da_che` phiên bản 1 đúng LOAI-DU-LIEU-RIENG §3: không map/bản rõ trong `bi_danh` hoặc `chuyen_tiep`; `con_sot=[]`, `kiem_tien_ngay=true` phải từ hậu kiểm thực tế. Không thêm trường bắt buộc/mã loại mới tại đây. Hỏi AI không gửi `ma_yeu_cau`, băm, ID kho, tham chiếu hoặc báo cáo ra Cloud; prompt nhạy cảm cũng phải qua che. Tệp giữ định dạng vẫn trả `truong` có trường `tep`, không giả thành loại văn bản để gửi Cloud.

Mã yêu cầu nội bộ đi từ Core qua `tra_loi_ai.chuyen_tiep.ma_yeu_cau`, không do AI/caller cấp lại. Trước đọc metadata, mở tham chiếu, tải tệp hay đóng việc, Core kiểm đúng module/người/tài liệu/vùng và trạng thái; biết alias/ID không thay quyền. Đề xuất A chỉ cấp tham chiếu cho thực thể được nguồn Core xác nhận thuộc phạm vi yêu cầu. Đây là thu hẹp so với “tra chính thức toàn bảng” cũ, cần Anh chọn Q3; thiếu bằng chứng quan hệ thì báo chưa xác minh, không cấp liên kết để dò danh mục toàn tập đoàn.

`dong_viec=false` mặc định. Đối chiếu đủ chưa đồng nghĩa người dùng xem xong. Đề xuất module/người gửi đóng rõ qua Core sau khi hoàn tất; alias chưa rõ giữ yêu cầu mở. Đóng phải thu quyền tham chiếu theo chính sách Core; không tự đóng ngay sau kiểm alias vì sẽ làm người dùng mất quyền Xem dữ liệu. Thời hạn giữ/ẩn/xử lý sau đóng để Anh/Core chốt, không tự TTL hoặc dùng hết hạn ngăn như thao tác xóa.

## 6. Các lát sửa sau khi Anh chọn A

Mỗi lát **≤5 tệp mã/khai báo**, test/tài liệu không tính; đường dẫn tương đối dưới `e_mask/goi/e_mask/` trừ khi ghi khác. Tên tệp mới là đề xuất. Không phải lệnh giao triển khai trong P3. Nếu khám phá vượt 5 tệp phải tách phiếu trước; không gộp cả chuyển SDK và đổi nghiệp vụ vào một lát lớn.

| Lát đề xuất | Nội dung, tệp tối đa | Phụ thuộc / điều kiện đạt | Giờ ƯỚC TÍNH | Độ khó |
|---|---|---|---:|---|
| MASK-A1 | Cấu trúc ngăn 2.2 và cấu hình: 5 tệp `engine.json`, `sql/001_tao_kho_bi_danh.sql`, `sql/kiem_ke.json`, `cau_hinh.schema.json`, `e_mask/khoi_tao_ngan.py` | C-P3-03/05 và Q2; SQL chỉ schema riêng, kiểm kê đúng mẫu. Bí mật/ID/duy nhất, không fallback RAM vận hành. Bản khai cũ giữ lịch sử, chưa xóa. | 4–6 | kho |
| MASK-A2 | Adapter kho: 4 tệp `e_mask/kho_ngan.py`, `e_mask/kho_dinh_danh.py`, `e_mask/kho_qua_core.py`, `e_mask/khoi_tao_ngan.py` | A1; SDK doc/tim null+cờ, patch metadata, no xoa; chống trùng/CAS/lô/ACK; bỏ mọi bản rõ trong khóa/dấu/JSON. Không nhận hết nghiệm thu khi handler cũ chưa chuyển. | 5–7 | kho |
| MASK-A3 | Admin/vòng đời: 3 tệp `e_mask/duyet_dinh_danh.py`, `ui/duyet_dinh_danh.js`, `e_mask/quyen_yeu_cau.py` | A2, C-P3-01/02, Q3/Q4; chỉ metadata, Xem dữ liệu ở Core; duyệt cùng ID/phiên bản, không sao bí mật, từ chối/dọn bằng trạng thái. | 4–6 | kho |
| MASK-A4 | Dò kín và che: 3 tệp `e_mask/che_van_ban.py`, `e_mask/tra_cuu_dinh_danh.py`, `e_mask/hau_kiem_ai.py` | A2, C-P3-03; đo chất lượng/chi phí trên DEMO độc lập, không mất tên danh mục cũ; không đạt thì báo giới hạn và chặn phát hành, không hạ chuẩn ngầm. | 6–8 | kho |
| MASK-A5 | Văn bản/thay @1: 4 tệp `e_mask/chay.py`, `e_mask/phong_bi.py`, `e_mask/doi_chieu_bi_danh.py`, `engine.json` | A2/A3/A4, Q1/Q3; output mới tĩnh, alias-only, đủ trường AI/trích dẫn; @1 cũ lỗi rõ; metadata không cấp quyền. | 4–6 | kho |
| MASK-A6 | Sửa mục tiêu B8: 4 tệp `e_mask/doi_chieu_tep_word.py`, `e_mask/doi_chieu_tep_excel.py`, `e_mask/ho_so_tep.py`, `e_mask/doi_chieu_bi_danh.py` | B5/B6/B7 đã điều chỉnh quyền theo A; A5, Q1; giữ tệp AI sửa/alias, không tải gốc/khôi phục; nhận diện run/rich text và báo vị trí an toàn. | 5–7 | kho |
| MASK-A7 | Nối B9 và đo B10: 5 tệp `e_mask/chay.py`, `e_mask/phong_bi.py`, `engine.json`, `e_mask/cong-cu/thu_mask_tep_that.py`, `e_mask/cong-cu/THU-MASK-TEP-THAT.cmd` (2 tệp cuối tính từ repo) | A6; held-out/test bên ngoài, trần/ACL/no plaintext/no inverse, công cụ khô; Anh chạy Office/Local thật sau. Không tự nhận Core/Office thật đã kiểm. | 4–6 | kho |
| **Tổng phần thiết kế lại theo A** | **7 lát** | Chưa gồm Core/module/chuyển dữ liệu thật và phần xây B4…B7 chưa có | **32–46** | |

Không cộng thẳng 32–46 vào toàn bộ 54–80 giờ P2: A6/A7 **thay** mục tiêu và một phần công việc B8/B9/B10, A1…A5 bổ sung chuyển SDK/kho/nghiệp vụ. Lead lập lại tổng dự toán còn lại sau Q1 và xác nhận Core; chưa có tổng dự án mới đáng tin. A4 là lát khảo sát có cửa dừng, số giờ không cam kết sẽ tìm được thuật toán giữ nguyên mọi khả năng của matcher cũ.

Chuyển dữ liệu: không cho engine đọc kho cũ rồi xuất bản rõ sang kho mới. Core/lead dùng quy trình migration được duyệt để bảo vệ cả `khoa`, `cum`, bản sao JSON/nhật ký lịch sử; kiểm số dòng, ID, alias/quan hệ, retry và quyền bằng DEMO trước. Không xóa hiện vật trong P3. Danh mục thật cần phiếu vận hành riêng, không đưa vào test/git. Trước chuyển gói chỉ cổng Core thật mới lưu bền; SDK mới không làm ngăn RAM cũ tự biến thành kho mã hóa.

## 7. Bảng cần Anh chọn

Không hỏi lại CĐ-36; các câu dưới đây chỉ chốt hệ quả nghiệp vụ để lead giao lát sau.

| Câu | Lựa chọn đề xuất | Lựa chọn còn lại và hệ quả |
|---|---|---|
| Q1 — Trải nghiệm mở che văn bản/tệp | **A:** trả alias + tham chiếu, xem tên tại Core; B8 không trả tệp tên gốc | Tạm dừng các năng lực mở che chờ mô hình khác vẫn tuân CĐ-36. B/C tự khôi phục không là lựa chọn được phép theo quyết định hiện hành. |
| Q2 — Dò danh mục kín | Cho khảo sát A4, **chưa chứng minh thì chặn phát hành**, không bật Cloud | Tạm hoãn chuyển luồng che có danh mục đến khi có phương án đủ bằng chứng; không cấp quyền đọc lại danh mục. |
| Q3 — Phạm vi tham chiếu/Xem dữ liệu | Chỉ ID gắn yêu cầu, đúng người/module/tài liệu; bảng chính thức vẫn chung tập đoàn | Cho tham chiếu chính thức ngoài yêu cầu nhưng Core phải xác minh quyền riêng từng dòng; tăng rủi ro dò danh mục và công sức quyền. |
| Q4 — Admin và kết thúc yêu cầu | Admin xem tại Core rồi duyệt bằng ID/phiên bản; đóng rõ sau hoàn tất, không tự đóng vì đối chiếu đủ | Tạm chỉ liệt kê metadata và để chờ khi chưa có cửa Xem dữ liệu/biên nhận; không duyệt mù. Thời hạn giữ sau đóng do Anh/Core chốt riêng. |

## 8. Cần Core — không có giải mã cho engine

| Mã | Cần xác nhận/cửa chung | Khi thiếu |
|---|---|---|
| C-P3-01 | Xem dữ liệu: tham chiếu opaque đến đúng dòng/phiên bản, Core tự kiểm quyền xem từng lần, audit truy cập; bản rõ chỉ trong màn Core. Không trả bản rõ/callback/export sang màn engine/module, không API giải mã. | Chỉ metadata, không tự dựng màn xem tên hoặc đọc snapshot để bù. |
| C-P3-02 | Nguồn tin cậy gắn module/người/tài liệu/vùng, quan hệ yêu cầu–alias, quyền Admin riêng với quyền xem; biên nhận xem/duyệt ID+phiên bản không tên, chống replay/TOCTOU; kiểm lại khi đóng/thu hồi. Không coi trường tự khai `da_xem=true` là biên nhận. | Từ chối cấp tham chiếu/duyệt; giữ C-MB-01/C-M2C-01 về ACL xuyên bước. |
| C-P3-03 | Ngữ nghĩa tìm chính xác `bi_mat`, chuẩn hóa/phiên bản, duy nhất và `lay_hoac_tao` theo giá trị bí mật + vùng, CAS/lô ≤100; không lộ băm/giá trị trong lỗi/log. Đánh giá dò đoán và hạn mức tìm; cân nhắc truy vấn nhiều ứng viên chung, chỉ trả ID/metadata, không trả tên. | Chặn chống trùng/phát hành thay vì khóa tên rõ/SHA công khai; A4 có thể không đạt. Không yêu cầu Core giải mã để matcher quét tên. |
| C-P3-04 | Quyền tệp/nguồn/map tách theo giai đoạn: che/Local cần nguồn, đối chiếu trả lời không tải nguồn/map; vòng đời hồ sơ/kết quả/alias sau đóng, giữ tham chiếu đang xử lý, hết hạn ẩn không thay thu hồi quyền. Kế thừa stream/trần/413/budget và cách ly upload C-MB-02/03. | Không trả bytes gốc, không lấy hồ sơ làm kho gỡ; hủy/mất lease dừng; ACK chưa rõ → `ChuaRo`. |
| C-P3-05 | Quy trình migration Core chung cho dữ liệu cũ có tên trong khóa/JSON/bản sao, lập ánh xạ ID mà engine không đọc rõ; chuyển quy trình @1 sang capability mới, xác nhận hành vi từ chối @1. | Giữ chưa chuyển/chưa nghiệm thu; không đổi hợp đồng nguồn/SDK hoặc sửa Core trong worktree này. |

Các mục này bổ sung, không tự đóng C-M2C-01…05/C-MB-01…03. P3 không đề nghị route/màn riêng trong Core cho Mask. Cửa Xem dữ liệu cần dùng cơ chế chung; nếu Core chưa hỗ trợ thì ghi thiếu, không tự coi tài liệu này là sự phê duyệt API mới.

## 9. Cách nghiệm thu và trạng thái bàn giao

Sau duyệt/triển khai phải kiểm bằng SDK 2.2.0 thật: ghi rồi đọc/tìm đều null+cờ; không tên trong khóa, metadata, JSON lựa chọn, kết quả, log; gặp lại/duyệt/CAS/lô/mất ACK/hết hạn và quyền chéo. Kiểm ngăn bí mật không dựa vào RAM mock trả lại tên như trước. Kiểm dò danh mục riêng với detector/Local, báo đúng chặn/lọt/báo nhầm; không lấy mọi ca bị chặn làm “0 lọt đạt”.

Kiểm A với câu trả lời alias trong mọi trường/trích dẫn, alias lạ/hỏng, ID bị đoán, yêu cầu đóng/quyền thu hồi, Admin thiếu quyền xem, phiên bản đổi sau xem, retry không trùng. Tệp kiểm giữ nội dung AI/format/tiền-ngày, không inverse ra tên, không đường đọc lại gốc từ đối chiếu. Word/Excel/Local/Core thật chưa chạy thì ghi chưa kiểm. Tại P3 chỉ chạy lại gói hiện có để ghi nền, không lấy kết quả đó chứng minh thiết kế A đã được triển khai.

Kết quả lệnh thật, thời gian và giới hạn kiểm của P3 ghi tại mục MASK-P3 trong [VIEC.md](VIEC.md). Không sửa CHANGELOG gói vì không đổi gói chạy. Ba lệnh chung AGENTS.md §5 được chạy theo ghi chú lead dù đây là lát tài liệu; lỗi nền CLI thiếu quyền được báo nguyên trạng, không sửa mã để làm xanh.
