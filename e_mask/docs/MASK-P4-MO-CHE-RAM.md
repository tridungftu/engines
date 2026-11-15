# MASK-P4 — Mở che cùng chu kỳ, ánh xạ chỉ trong RAM

*15/11/2026 · CHỈ TÀI LIỆU · PR: chờ lead mở. Chưa triển khai các lát dưới đây.*

## 1. Quyết định và phạm vi

Áp dụng câu 10 mới của [quyết định chiều/tối 15/11](../../_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md): **Mask che → Core điều phối Hỏi AI → Mask mở che ngay khi có kết quả, trong cùng một chu kỳ**. Ánh xạ bí danh → bản gốc chỉ trong RAM tiến trình Mask khi chuỗi chạy. Không ngăn, không tệp, không hồ sơ Core, không cơ chế phục hồi ánh xạ sau restart. Người dùng phải chạy lại toàn chuỗi nếu mất RAM.

CĐ-36 vẫn giữ nguyên: không giải mã `bi_mat` cho engine, không đọc lại bản rõ từ Core/module để thay cho RAM. Phương án A của [MASK-P3](MASK-P3-MO-CHE-SDK-2.2.md) **không dùng theo quyết định Anh 15/11 tối**. Phương án B của P3 nay chỉ dùng biến thể RAM; biến thể hồ sơ Core không dùng. Phương án B ZIP/XML của MASK-P2 là lựa chọn công nghệ Word/Excel, vẫn giữ; hai chữ B không cùng nghĩa.

Phiếu này thay các yêu cầu tra ngược toàn kho, giữ map/snapshot tại Core và mở thiếu vẫn trả thành công trong MASK-5/6, MASK-2c, MASK-B5…B10. API v1, SDK 2.2.0 và loại dữ liệu chung không đổi trong P4. Không sửa mã, schema, manifest, SQL hoặc CHANGELOG gói chạy. Cloud tiếp tục tắt; Local/Office/Core thật chưa được chứng nhận.

## 2. Vòng đời RAM và điều phối

| Nội dung | Thiết kế bắt buộc khi triển khai |
|---|---|
| Khóa và quyền | Kho RAM khóa theo `ma_yeu_cau` opaque **do Core cấp**, ổn định xuyên các bước, ràng buộc module/người/tài liệu/pháp nhân/DEMO từ nguồn Core tin cậy. Không lấy mã caller tự đặt, không lấy `viec_id` riêng từng bước làm mã chuỗi. Mã trong `chuyen_tiep` chỉ để đối chiếu với ngữ cảnh Core, không tự cấp quyền. |
| Dữ liệu | Bảng alias → chuỗi nguyên văn xuất hiện trong đầu vào hiện tại; gồm alias chính thức và tạm đã dùng ở yêu cầu này. Giữ map span/Unicode, phiên bản/băm, kế hoạch Local và bytes tệp cần dùng cũng trong RAM cùng bản ghi. Không có alias ở yêu cầu này thì không được tra kho để mở, kể cả alias chính thức. |
| Đúng bản gốc | Giữ nguyên NFD/Cf/khoảng trắng của vùng gốc theo chính sách đã kiểm. Cùng một alias ứng với nhiều nguyên văn khác nhau mà câu trả lời không phân biệt được → chặn do mơ hồ; không chọn tên đầu tiên hoặc dùng bản chuẩn hóa thay nguyên văn. |
| Thời hạn đề xuất | `thoi_han_anh_xa_giay`: mặc định **600 giây (10 phút)**, cấu hình nguyên **60–900 giây (1–15 phút)** qua `viec.cau_hinh` SDK 2.2.0; chụp lúc bắt đầu. Hạn tuyệt đối = thời điểm tạo + TTL, hoặc deadline chuỗi Core nếu sớm hơn; dùng đồng hồ monotonic tại Mask. Không trượt hạn theo truy cập/retry/đổi cấu hình. Đây là **đề xuất**, cần đo Local/tệp ở biên; chuỗi dài không kịp phải từ chối, không tự nới hạn. |
| Trạng thái | `DANG_CHE → CHO_AI → DANG_MO → KET_THUC`; hủy, lỗi kết thúc, mất quyền/lease hoặc quá hạn đều chuyển kết thúc và hủy dữ liệu RAM. Chỉ một bước được sở hữu bản ghi; mở che lấy quyền dùng một lần dưới khóa, không có hai lần mở đồng thời. |
| Dọn chủ động | Bỏ tham chiếu map/gốc/bytes/đối tượng phụ ngay sau mở che xong, hủy, lỗi, kết thúc chuỗi, hoặc TTL. `finally` cho mỗi nhánh kết thúc; bộ hẹn giờ dọn cả lúc đang chờ AI, không chờ việc tiếp theo mới dọn. Nếu quá hạn/hủy khi đang mở, ngừng xử lý và không phát hành kết quả. Python không bảo đảm ghi đè an toàn mọi bản sao trong RAM; không tuyên bố xóa vật lý tuyệt đối. |
| Lỗi/mất RAM | Restart, process chết, chuyển instance, hết hạn, đã tiêu thụ hoặc không có bản ghi → `LoiNghiepVu("MASK_ANH_XA_KHONG_CON", "Không còn dữ liệu mở che của chuỗi này. Anh hãy chạy lại toàn bộ chuỗi che và hỏi AI.")`. Sai quyền → lỗi quyền cố định. Không trả bản mở thiếu, không giả `mo_day_du=true`, không nạp lại từ ngăn/tệp/nguồn Core. |
| Retry/ACK | Retry trong cùng chuỗi chỉ dùng trạng thái/băm RAM còn hiệu lực và đúng quyền; đầu vào khác với cùng mã thì từ chối. Sau tiêu thụ không tái tạo map và không cache bản rõ. Core có thể giao lại kết quả cuối đã tiếp nhận theo quyền, không gọi mở che lại để tái dựng. Mất ACK sau nguồn đã nhận → `ChuaRo(ma_tuong_quan)`; chỉ giữ RAM nếu chuỗi còn đang chờ, trong hạn tuyệt đối, không coi là lỗi kết thúc. Nếu RAM đã dọn thì chạy lại toàn chuỗi với mã Core mới. |

**Chế độ triển khai đề xuất:** `che_do_chay="cuc_bo"`, một tiến trình Mask sống suốt chuỗi, `tai_nguyen.so_viec_dong_thoi=1`, tối đa **một chuỗi có map đang sống** trong giai đoạn đầu. Sau bước che, trả lượt xử lý cho Core nhưng giữ bản ghi RAM; không giữ handler chờ làm nghẽn bước mở. Chuỗi thứ hai khi còn map sống phải chờ ở Core hoặc bị từ chối rõ, không đẩy map cũ ra để lấy chỗ. RAM còn bị chặn theo trần văn bản/tệp §7.3 và budget Core; vượt từ chối trước phát hành.

**`so_viec_dong_thoi=1` không bảo đảm cùng instance.** Core phải ghim tất cả bước Mask (chuẩn bị, hậu kiểm Local, che bổ sung, mở che) của mã yêu cầu về đúng tiến trình/instance ban đầu, không spawn mỗi việc, không chuyển worker/failover để tiếp tục chuỗi. Core gửi tín hiệu kết thúc/hủy/lỗi ở bước AI cho Mask ngay cả khi không còn việc Mask đang chạy; TTL là chốt dự phòng. `tu_xa`/nhiều instance chưa mở trước khi có bằng chứng ghim đúng worker. Thiếu các cửa chung này → **Cần Core**, runtime từ chối luồng cần RAM, chỉ kiểm bằng adapter CoreGia ngoài gói; không tự thêm API hoặc kênh gọi giữa engine.

### 2.1 Ranh giới dữ liệu, kể cả MASK-2c

- Không ghi bản rõ hay ánh xạ vào log, traceback, stderr, trường ngăn thường, tệp tạm, hồ sơ Core, kết quả che hoặc `chuyen_tiep`. Không dùng JSON lồng/map span + gốc/bytes gốc làm bản sao phục hồi trá hình. Không truyền map sang Local AI hoặc module. Nhật ký chỉ mã lỗi cố định, số đếm, thời gian và phiên bản; không dump request/response/local variables.
- Ngoại lệ nghiệp vụ được yêu cầu riêng là **kho tên chính thức/chờ duyệt có cột `bi_mat`** ở §3: chỉ ghi ứng viên đầu vào vào cột đã khai bí mật qua Core để Core mã hóa. Không lưu bản rõ ở khóa, metadata, JSON, dấu gặp hay cấu hình. Đây là kho nhận diện, không phải ánh xạ mở che của chuỗi và không được dùng để phục hồi RAM.
- MASK-2c vẫn do Core điều phối Mask → Hỏi AI Local → Mask. Gốc/bản quy tắc/map/kế hoạch của Mask nằm trong RAM; bỏ đường ghi/đọc snapshot Core có chúng trong `ho_so_ai.py`. Core chỉ giao đoạn Local cần thiết theo cổng tin cậy hiện hành và trả đủ phản hồi; không giữ hồ sơ map/gốc riêng để Mask mở che. Mã/băm/chỉ số đoạn/profile có thể chuyển tiếp nội bộ, không mang gốc/map; nguồn gốc/ACL của đoạn Local vẫn bắt buộc. Nếu cổng hiện tại phụ thuộc snapshot thì ghi C-P4-01/04, chưa coi runtime đã hỗ trợ.
- Cả phản hồi Local chứa nguyên văn và map Unicode nội bộ đều theo TTL/vòng đời RAM; không chuyển chúng ra Cloud. Giữ nguyên yêu cầu đủ đoạn, span chính xác, Cf/NFD, hậu kiểm tiền/ngày và bằng chứng nguồn Local. Thiếu RAM/nguồn/đoạn → chặn; không phát hành bản quy tắc chưa qua Local.

### 2.2 Mở che văn bản và tệp

Văn bản/`tra_loi_ai`: thay trên `tra_loi`, các giá trị chuỗi lồng trong `du_lieu`, câu trích; giữ khóa/số/ngày/boolean/null và nội dung mới. Mở mềm hoa/thường/khoảng trắng/tách run chỉ khi alias xác định duy nhất trong map đúng yêu cầu. Câu trích bị đổi phải hạ trạng thái kiểm nguyên văn và tính lại vị trí trên phiên bản phù hợp; không giữ offset trước che làm chứng cứ cho câu trả lời mới.

Alias lạ/hỏng/thiếu/mơ hồ → `LoiNghiepVu("MASK_MO_CHE_KHONG_DAY_DU", "Không thể mở che đầy đủ kết quả này. Anh hãy chạy lại toàn bộ chuỗi.")`, hủy map và không trả văn bản/tệp đã mở một phần. Báo cáo hỗ trợ chỉ vị trí/mã vùng an toàn, không bản rõ hoặc tên sheet chưa che. Thay thế và kiểm hoàn chỉnh trong RAM trước bàn giao; không streaming bản rõ dở cho caller. Kết quả cuối đã mở chỉ về đúng người/module, không quay lại Cloud.

DOCX/XLSX: dùng map RAM của đúng mã yêu cầu và reader/gate/writer ZIP/XML P2. Tệp che chưa sửa: chỉ có thể trả nguyên bytes gốc **đang ở RAM**, sau kiểm băm và quyền; nếu không giữ bytes thì patch inverse và không hứa SHA toàn tệp bằng gốc. Không tải gốc/snapshot Core để khứ hồi. Tệp AI sửa: kiểm whitelist/trần lại trên chính tệp gửi về, patch alias trên tệp đó, giữ phần AI thêm/format/tiền-ngày; không thay bằng bản gốc. Alias hỏng hoặc vùng chưa hỗ trợ → từ chối cả tệp. Áp cùng TTL và dọn cả bytes gốc/map sau mở. Không có mở lại tệp vào ngày sau hoặc gửi tệp qua chuỗi độc lập. Cloud sửa tệp vẫn chỉ giả lập trong loạt này.

## 3. Kho bí danh chính thức và Admin tối thiểu

Tên đã duyệt dùng chung toàn tập đoàn qua nhiều lần che, nhưng **kho chỉ lưu bí danh + trường `bi_mat`**, cùng ID opaque/nhóm/trạng thái/phiên bản/số gặp cần thiết. `gia_tri_goc` và `gia_tri_chuan` (nếu cần chuẩn hóa) đều `bi_mat:true`; Core mã hóa, quản chỉ mục băm. Không lưu tên chuẩn hóa ở khóa/cột rõ, không SHA-256 tên không khóa làm khóa công khai, không sao bí mật vào JSON. `doc`/`tim` trả null+cờ mã hóa đúng SDK 2.2.0; không có giải mã cho Mask.

1. Detector/quy tắc/Local hoặc danh sách từ đầu vào hiện tại tạo ứng viên có giới hạn trong RAM. Chuẩn hóa theo phiên bản ghim; gọi `viec.ngan.tim` với lọc **bằng chính xác** trên giá trị cột bí mật để Core so băm. Không tự tính/bóc băm Core, không tìm một phần/fuzzy/prefix trong kho, không liệt kê danh mục rồi dựng matcher bằng bản rõ. Biến thể được detector đề xuất là ứng viên riêng; từng ứng viên vẫn tìm chính xác, không coi băm tương đương matcher mềm.
2. Kết quả chỉ ID/alias/metadata/null+cờ; dùng nguyên văn từ đầu vào đang ở RAM để thêm alias vào map yêu cầu. Tên đã duyệt được dùng lại alias; tên mới tạo hàng chờ với giá trị vào cột bí mật. Alias tạm chỉ nằm trong RAM yêu cầu, không lưu quan hệ yêu cầu → alias → tên ra ngăn. Kho chờ chỉ cần ID, bí mật và metadata, không giữ map theo chuỗi.
3. `lay_hoac_tao`, duy nhất theo giá trị bí mật/vùng, CAS và lô ≤100 phải được Core xác nhận; không gộp các giá trị null thành cùng thực thể. Sửa metadata bỏ hẳn khóa bí mật, không ghi null/cờ trở lại. Duyệt đổi trạng thái và alias trên cùng ID, không chép trường bí mật sang bảng khác; từ chối bằng trạng thái, không dùng lệnh `xoa` vốn không có trong SDK. Map của chuỗi đang chạy giữ alias/nguyên văn đã ghim, không tự đổi vì Admin duyệt giữa chừng.
4. UI engine chỉ hiện ID tham chiếu an toàn, alias/nhóm/trạng thái/số gặp; không hiển thị bản rõ, không lọc tên một phần. Admin cần xem tên thì xem tại cửa **Xem dữ liệu của Core**, bản rõ không callback/export sang UI engine. Core xác thực quyền xem/duyệt, gắn biên nhận ID+phiên bản không chứa tên; UI gửi ID/phiên bản/alias/quyết định qua `KttCore.engine("e_mask")`. Thiếu cửa xem/xác minh thì để chờ, không duyệt mù hay tự khai `da_xem=true`.

Tìm theo băm chỉ trả lời “ứng viên này đã được duyệt chưa”, không tự phát hiện tên. Phải đo lại recall/báo nhầm trên DEMO độc lập có tên đặc biệt mà matcher danh mục cũ từng bắt được, gồm MASK-2c. Trần khảo sát đề xuất **2.000 ứng viên phân biệt/chuỗi**, không quét mọi chuỗi con của 500.000 ký tự; vượt trần/thời gian hoặc chưa chứng minh chất lượng thì từ chối. Hạn mức chống dò đoán, chuẩn hóa/chỉ mục/duy nhất và tính khả thi chi phí là C-P4-03; không đề nghị giải mã danh mục để bù.

## 4. Các lát MASK-R mới

Mỗi lát ≤5 tệp mã/khai báo; test/tài liệu không tính. Đường dưới `e_mask/goi/e_mask/`, trừ ghi khác. Chỉ DEMO, không thêm dependency; vượt closure phải tách trước. Đây là **giờ ƯỚC TÍNH chưa đo**, không gồm Core, migration dữ liệu thật, Local/Office thật hoặc thời gian chờ. Các lát R thay MASK-A1…A7 của P3; không cộng dự toán A vào đây.

| Lát | Nội dung và tệp tối đa | Phụ thuộc | Giờ ƯỚC TÍNH | Độ khó |
|---|---|---|---:|---|
| MASK-R1 | Ngăn bí mật SDK 2.2/config: 5 — `engine.json`, `cau_hinh.schema.json`, `sql/001_tao_kho_bi_danh.sql`, `sql/kiem_ke.json`, `e_mask/khoi_tao_ngan.py` | C-P4-03; mẫu SDK và inventory | 4–6 | kho |
| MASK-R2 | Adapter kho chỉ bí mật/metadata: 4 — `e_mask/kho_ngan.py`, `e_mask/kho_dinh_danh.py`, `e_mask/kho_qua_core.py`, `e_mask/khoi_tao_ngan.py` | R1; duy nhất/CAS/tìm chính xác | 5–7 | kho |
| MASK-R3 | Dò ứng viên và che không matcher danh mục: 3 — `e_mask/che_van_ban.py`, `e_mask/tra_cuu_dinh_danh.py`, `e_mask/hau_kiem_ai.py` | R2; cửa dừng chất lượng | 6–8 | kho |
| MASK-R4 | Kho RAM/vòng đời/ghim: 3 — `e_mask/kho_anh_xa_ram.py`, `e_mask/quyen_yeu_cau.py`, `e_mask/chay.py` | R1; C-P4-01/02; adapter CoreGia | 4–6 | kho |
| MASK-R5 | Bỏ snapshot/map Core khỏi MASK-2c: 5 — `e_mask/anh_xa_ai.py`, `e_mask/ho_so_ai.py`, `e_mask/chuan_bi_ai.py`, `e_mask/hau_kiem_ai.py`, `e_mask/phong_bi.py` | R2/R3/R4; C-P4-04, AI-9 | 6–8 | kho |
| MASK-R6 | Mở che văn bản/AI từ RAM: 4 — `e_mask/mo_che_ram.py`, `e_mask/che_van_ban.py`, `e_mask/chay.py`, `e_mask/phong_bi.py` | R3/R4/R5; C-P4-02/05 | 4–6 | kho |
| MASK-R7 | Admin chỉ metadata, duyệt tại cùng ID: 2 — `e_mask/duyet_dinh_danh.py`, `ui/duyet_dinh_danh.js` | R2; C-P4-06 | 3–5 | vua |
| **Tổng R** | **7 lát, mỗi lát ≤5 tệp** | Không bao gồm B5…B10 | **32–46** | |

Thứ tự: R1→R2→R3; R4 sau R1; R5 sau R3/R4; R6 sau R5; R7 sau R2. B5/B6 chỉ nối API RAM đã chốt sau R5/R6; B7 tích hợp tệp, B8 mở tệp, B9 phát hành, B10 đo. Phân công R4 tạo kho RAM, R5 chuyển MASK-2c văn bản, B7 chuyển hồ sơ tệp; không tính hai lần cùng phần chuyển. Dự toán B5…B10 mới là **36–56 giờ** (bảng §7.4 phiếu giao); tổng R + B5…B10 **68–102 giờ**, chưa gồm B4 chưa triển khai và các phần ngoài phạm vi nói trên. Đây không phải tổng giờ thực tế hay cam kết toàn dự án.

### MASK-R1 — Ngăn bí mật và cấu hình SDK 2.2
```
Đọc AGENTS.md, API-ENGINE-v1.md, hướng dẫn/phiếu/thay đổi SDK 2.2.0 trong docs/goi-gui-engine/sdk-2.2.0, _chung/docs/CHUYEN-SDK-2.2.md, quyết định Anh chiều 15/11 câu 10, CĐ-36 ở MASK-P3, e_mask/docs/MASK-P4-MO-CHE-RAM.md §1–5 và VIEC.md. Làm MASK-R1, 4–6 giờ ƯỚC TÍNH, kho. Chỉ DEMO; không giải mã bi_mat/Cloud.
Tối đa 5 tệp đúng bảng §4: khai kho alias + cột bi_mat/metadata, cấu hình TTL 600 giây trong 60–900, SDK >=2.2.0 <3.0.0, cuc_bo/so_viec_dong_thoi=1. SQL chỉ schema eng_e_mask theo mẫu SDK, kiểm kê bytes/SHA mọi tệp theo mẫu. Không bảng map RAM, không bản rõ trong khóa/JSON; không xóa bản khai cũ. Thiếu duy nhất bí mật ghi C-P4-03, chưa nhận đủ nghiệm thu. Test CoreGia ghi/đọc/tìm null+cờ và schema/config/SQL inventory; không fallback ngăn RAM vận hành.
Chạy đủ ba lệnh AGENTS.md §5 bằng .venv/Scripts/python -B (SDK CLI, pytest, kiem_doc_lap.py), git diff --check; báo kết quả thật kể cả lỗi nền. Cập nhật VIEC/CHANGELOG nếu đổi gói, ghi đã kiểm bằng Core giả (CoreGia), báo §6 thực tế/ước tính/Cần Core; không commit/push/sửa Core/SDK/nguồn cũ.
```

### MASK-R2 — Kho nhận diện không đọc bản rõ
```
Đọc AGENTS.md, SDK 2.2.0, quyết định chiều 15/11 câu 10, CĐ-36 ở MASK-P3 và MASK-P4-MO-CHE-RAM.md §2–5, VIEC.md. Làm MASK-R2 sau R1, 5–7 giờ ƯỚC TÍNH, kho; tối đa 4 tệp đúng bảng §4. Dùng viec.ngan/doc/tim/lo thật; tìm ứng viên bằng chính xác cột bi_mat, kết quả chỉ ID/alias/metadata/null+cờ. Không map/gốc trong khóa/cum/dau_gap/JSON/snapshot, không hash tên công khai, không import Core/engine khác.
Alias chính thức dùng lại qua lần che, alias tạm/map chỉ trong RAM yêu cầu. Sửa metadata không chép khóa bí mật, duyệt tại cùng ID; no xoa. Kiểm duy nhất/lay_hoac_tao/CAS/lô <=100, retry/mất ACK ChuaRo không đếm hoặc cấp trùng; thiếu bảo đảm Core thì chặn và ghi C-P4-03. Test CoreGia null+cờ/tên không lộ ở khóa hay metadata/hai việc xung đột/DEMO-thật; không dùng mock trả tên để thay ngữ nghĩa SDK.
Chạy ba lệnh AGENTS.md §5 bằng .venv/Scripts/python -B và git diff --check; VIEC/CHANGELOG, báo thật §6, đã kiểm bằng Core giả (CoreGia), PR chờ lead mở; không commit/push/Core/SDK/dependency.
```

### MASK-R3 — Dò ứng viên bằng tìm chính xác
```
Đọc AGENTS.md, SDK 2.2.0, quyết định chiều câu 10, MASK-P4-MO-CHE-RAM.md §3–5, phiếu GIAO-CODEX-e_mask.md §6 (bổ sung P4), VIEC.md. Làm MASK-R3 sau R2, 6–8 giờ ƯỚC TÍNH, kho; tối đa 3 tệp đúng bảng §4. Bỏ dựng matcher/liệt kê danh mục bản rõ; detector/quy tắc/Local/đầu vào tạo ứng viên RAM, từng ứng viên tìm đúng giá trị qua chỉ mục băm Core. Không fuzzy/prefix kho, không quét mọi chuỗi con; trần đề xuất 2000 ứng viên, quá hạn/trần thì từ chối.
Ghép alias từ metadata với nguyên văn đầu vào hiện tại trong RAM; cùng alias nhiều nguyên văn không phân biệt được thì chặn. Đo DEMO độc lập tên danh mục đặc biệt, Cf/NFD/viết thường/âm tiết thường; báo lọt/báo nhầm/chặn/lỗi riêng, không lấy tất cả bị chặn làm đạt. Chưa chứng minh độ phủ/chi phí thì kết thúc khảo sát bằng giới hạn, không phát hành/cloud/đọc lại tên để bù. Giữ kiểm tiền/ngày và Local bắt buộc.
Chạy ba lệnh AGENTS.md §5 bằng .venv/Scripts/python -B và git diff --check; VIEC/CHANGELOG/C-P4-03, báo §6 số thật, đã kiểm bằng Core giả (CoreGia); không commit/push/sửa Core/SDK/dependency.
```

### MASK-R4 — Kho ánh xạ RAM và vòng đời chuỗi
```
Đọc AGENTS.md, SDK 2.2.0, quyết định chiều câu 10, MASK-P4-MO-CHE-RAM.md §2/4/5 và VIEC.md. Làm MASK-R4 sau R1, 4–6 giờ ƯỚC TÍNH, kho; tối đa 3 tệp đúng bảng §4. Kho chỉ RAM Mask khóa ma_yeu_cau do Core cấp, kiểm module/người/tài liệu/pháp nhân/DEMO; nguồn tin cậy thiếu thì từ chối. TTL 600 giây cấu hình 60–900 chụp đầu chuỗi, monotonic, hạn Core nếu sớm hơn, không trượt retry. Một chuỗi sống, một bước sở hữu; nhường handler lúc chờ AI, không chặn bước mở.
Khóa luồng/tiêu thụ một lần, dọn chủ động timer và finally sau mở/hủy/lỗi/kết thúc/hết hạn, kể cả hủy ở bước AI. Không map/gốc/log/stderr/ngăn/tệp/tạm/hồ sơ/chuyen_tiep; không cứu từ instance khác. Cần Core ghim instance và thông báo vòng đời, so_viec_dong_thoi=1 không đủ; thiếu thì runtime từ chối, adapter giả chỉ ngoài gói. Test đồng hồ giả, timer khi rảnh, timeout đua mở/hủy, retry đầu vào đổi, restart/instance khác, sai quyền, hai chuỗi/two-open không ảnh hưởng map khác; lỗi MASK_ANH_XA_KHONG_CON yêu cầu chạy lại, không output thiếu.
Chạy ba lệnh AGENTS.md §5 bằng .venv/Scripts/python -B, git diff --check; VIEC/CHANGELOG/C-P4-01/02, báo §6 thật, đã kiểm bằng Core giả (CoreGia); không commit/push/Core/SDK/dependency.
```

### MASK-R5 — MASK-2c dùng RAM xuyên các bước Local
```
Đọc AGENTS.md, SDK 2.2.0, quyết định chiều câu 10, MASK-P4-MO-CHE-RAM.md §2–5, GIAO-CODEX-e_mask.md §6 bổ sung P4, bàn giao MASK-2c/AI-9 và VIEC.md. Làm MASK-R5 sau R2/R3/R4, 6–8 giờ ƯỚC TÍNH, kho; tối đa 5 tệp đúng bảng §4. Chuyển ho_so_ai/map/gốc/bản quy tắc/kế hoạch/phiên bản sang kho RAM R4; bỏ đọc/ghi snapshot Core chứa chúng, không sửa schema/contract chung để lách. Core vẫn điều phối từng Local/lặp/ghép; không gọi Hỏi AI/model từ Mask.
Chuyen_tiep chỉ mã/băm/chỉ số/profile an toàn, không gốc/map. Giữ đủ đoạn, Unicode/overlap/span, nguồn Local tin cậy, chống replay/tệp đổi, kiểm tiền-ngày và hậu kiểm; mất RAM/lỗi/hủy/TTL không phát hành. Cần Core thay phụ thuộc hồ sơ và xác minh nguồn/quyền xuyên bước, thiếu thì ghi C-P4-04 và kiểm adapter CoreGia, không nhận runtime thật. Local ChuaRo chỉ chờ trong hạn tuyệt đối; terminal lỗi dọn map. Test spy mọi cửa Core/ngăn/log/stderr/tệp bảo đảm không xuất map/hồ sơ; sai nguồn/thiếu đoạn/restart/khác instance phải chặn, không Cloud.
Chạy ba lệnh AGENTS.md §5 bằng .venv/Scripts/python -B, git diff --check; VIEC/CHANGELOG/C-P4-01/02/04, báo §6 thật, đã kiểm bằng Core giả (CoreGia); không commit/push/Core/SDK/dependency.
```

### MASK-R6 — Mở che văn bản và trả lời AI từ RAM
```
Đọc AGENTS.md, SDK 2.2.0, quyết định chiều câu 10, CĐ-36 ở MASK-P3, MASK-P4-MO-CHE-RAM.md §2/4/5, VIEC.md. Làm MASK-R6 sau R3/R4/R5, 4–6 giờ ƯỚC TÍNH, kho; tối đa 4 tệp đúng bảng §4. Nối mask.mo_che_van_ban@1 với map RAM đúng yêu cầu đã kiểm quyền, chỉ alias từng dùng ở chuỗi. Không đổi nghĩa thành công thành alias+tham chiếu A, không tra ngược ngăn bi_mat hoặc đọc nguồn/snapshot để gỡ. Giữ nhan/tra hiện hành; cờ dong_viec=false cũ không cho giữ map sau mở, cần thông báo chuyển quy trình.
Mở tra_loi/chuỗi lồng du_lieu/câu trích, giữ nội dung AI mới và kiểu tiền/ngày/số; case/space mềm chỉ khi duy nhất. Hạ kiểm nguyên văn/trích dẫn tính lại khi thay chữ. Alias lạ/hỏng/thiếu/mơ hồ hoặc hết RAM -> LoiNghiepVu tiếng Việt, không kết quả một phần. Sau thành công/lỗi/hủy dọn map một lần; mất ACK ChuaRo không tạo cache bản rõ. Core bàn giao cuối đúng quyền, không gửi Cloud.
Test CoreGia đủ trường AI, NFD/Cf/nhiều nguyên văn cùng alias/alias ngoài yêu cầu/replay/sai quyền/restart/TTL/khác instance/hủy/mất ACK và không rò. Chạy ba lệnh AGENTS.md §5 bằng .venv/Scripts/python -B và git diff --check; VIEC/CHANGELOG/C-P4-02/05, báo §6 thật, đã kiểm bằng Core giả (CoreGia); không commit/push/Core/SDK/dependency.
```

### MASK-R7 — Duyệt metadata và xem tên tại Core
```
Đọc AGENTS.md, SDK 2.2.0, CĐ-36 ở MASK-P3, quyết định chiều câu 10, MASK-P4-MO-CHE-RAM.md §3–5, VIEC.md. Làm MASK-R7 sau R2, 3–5 giờ ƯỚC TÍNH, vua; tối đa 2 tệp đúng bảng §4. UI KttCore.engine("e_mask") chỉ ID/alias/nhóm/trạng thái/số gặp, không bản rõ/lọc tên một phần. Admin xem tại cửa Core đúng quyền, nhận biên nhận ID/phiên bản không tên; thiếu cửa/phiên bản đổi thì để chờ, không duyệt mù/cờ tự khai. Không API giải mã/callback tên vào UI.
Duyệt sửa metadata cùng ID, alias duy nhất Junsky/MASK; không đọc-sao bí mật sang bảng khác, không null đè bí mật/no xoa. RAM chuỗi đang chạy không đổi theo quyết định Admin. Test KttCore giả và CoreGia null+cờ, XSS/CAS/replay/thiếu quyền xem/duyệt/tên không xuất DOM/log; không mạng ngoài/eval/innerHTML chưa lọc. Chạy ba lệnh AGENTS.md §5 bằng .venv/Scripts/python -B và git diff --check; VIEC/CHANGELOG/C-P4-06, báo §6 thật, đã kiểm bằng Core giả (CoreGia), chưa UI Core thật; không commit/push/Core/SDK/dependency.
```

## 5. Cần Core và nghiệm thu

| Mã | Cửa chung cần xác nhận, không phải API đã có |
|---|---|
| C-P4-01 | Mã yêu cầu Core cấp, nguồn ngữ cảnh/ACL xuyên bước; **ghim cùng tiến trình/instance**, không spawn mỗi bước hoặc failover tiếp tục; chặn chuỗi thứ hai khi map sống. Thiếu thì không chạy luồng cần RAM. |
| C-P4-02 | Báo kết thúc/hủy/lỗi/lease/deadline toàn chuỗi tới Mask khi nó đang rảnh; đồng bộ với mở/tiêu thụ và bàn giao cuối, không chạy lại mở che sau đã tiêu thụ. Kết quả chưa xác nhận dùng ChuaRo; mất RAM chạy mới. |
| C-P4-03 | Ngữ nghĩa băm/chuẩn hóa/duy nhất/tìm chính xác bi_mat/CAS/lô ≤100 và hạn mức dò đoán; không log ứng viên/băm. Không giải mã cho engine. Kế thừa phần phù hợp C-P3-03. |
| C-P4-04 | Điều phối Local đủ đoạn + nguồn tin cậy và quyền tệp, thay thiết kế snapshot có map của C-M2C-01/05, C-MB-01/02. Core không lưu hoặc trả hồ sơ ánh xạ/gốc để khôi phục; chỉ điều phối dữ liệu Local cần thiết theo contract. Lead điều chỉnh profile/sổ chung nếu cần, P4 không sửa nguồn chung. |
| C-P4-05 | Tải/trả tệp theo quyền, streaming/trần bytes/413, budget RAM/thời gian cả chuỗi; không dump payload/traceback ra log/stderr, không ghi tệp tạm rõ/ánh xạ; cách ly upload chưa phát hành và xử lý mất ACK. Không lưu map trong upload/log/crash dump. Kế thừa C-MB-03. |
| C-P4-06 | Admin xem tại cửa Core, quyền xem/duyệt và biên nhận ID+phiên bản không bản rõ; migration dữ liệu cũ do Core/lead bảo vệ khóa/JSON/bản sao. Không route giải mã/đặc thù Mask, không để engine đọc tên cũ để chuyển. |

Các yêu cầu P3 về A/đối chiếu tham chiếu và P2/2c về map/hồ sơ phục hồi không còn hiệu lực; những mục quyền, nguồn Local, CAS, trần và Admin không mâu thuẫn vẫn giữ. Không chờ Anh chọn lại A/B/C. TTL/trần ứng viên là đề xuất đo kỹ thuật; lead/Core chốt sau bằng chứng, không tự coi là quyết định nghiệp vụ mới.

Nghiệm thu triển khai phải kiểm spy không lưu ánh xạ ở mọi cửa, lifecycle có timer khi chờ, restart/đổi instance/hủy/lỗi/TTL/double-open, quyền chéo, tên đã duyệt dùng lại qua hai chuỗi nhưng map không sống qua chuỗi, null+cờ và tìm chính xác, alias thiếu không phát hành. Word/Excel thêm bytes bất biến, nguyên bytes khi nguồn RAM còn, giữ sửa AI, tiền/ngày và trần biên. Chạy đủ ba lệnh §5 AGENTS; trước nối thật ghi **đã kiểm bằng Core giả (CoreGia)**. Kết quả kiểm nền riêng P4 và thời gian nằm tại [VIEC.md](VIEC.md); không lấy gói cũ kiểm qua làm bằng chứng các lát R/B đã triển khai.
