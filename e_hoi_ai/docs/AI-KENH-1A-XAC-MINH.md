# AI-KENH-1a — Xác minh kênh AI bản 1 (CD-098)

Ngày 06/11/2026 · Nhánh `lat/ai-1a` · HEAD `5d8b2bcf` · Chỉ khảo sát và viết báo cáo, không sửa mã, không commit.

**Cập nhật theo CD-111 ngày 07/11/2026:** **1b-01 = DUYỆT (Anh 21:31: “1b-01 đồng ý”)**; **1b-06 = KHÔNG làm đường riêng**. Việc cần AI nối bằng chuỗi engine do Core điều phối theo CD-110; engine không gọi engine. Bỏ 1b-07/08 dạng gọi AI giữa chừng; chuyển các ràng buộc còn cần sang bước Hỏi AI trong chuỗi. Căn cứ CD-111 mục 2/4 và xác nhận 21:31 lấy từ handoff DOC-CD111; bản `CHI-DAO-TU-ANH.md` trong worktree hiện kết thúc ở CD-110, chưa có CD-111. Các bằng chứng mã/test 1a dưới đây giữ mốc khảo sát cũ, không phải xác minh lại mã hiện hành.

~~**Kết luận cũ: cần 1b.** Có cổng AI dùng chung, Local LAN/Tailscale, Python kiểm trích dẫn và khung SDK/quyền. Chưa đủ luồng bản 1: thiếu metadata prompt/function, chưa nối runtime với adapter chuẩn, chưa có câu trả lời “không thấy căn cứ”, chưa khóa Cloud bắt buộc và thiếu operation cho engine trích hỏi AI qua Core. Không cần dựng cổng/client AI thứ hai.~~ **Thay theo CD-111:** giữ phần thiếu metadata, runtime, trả lời thiếu căn cứ, rào Local và nhật ký; phần thiếu operation riêng không còn là việc phải bổ sung.

## Căn cứ và giới hạn xác minh

- Quyết định cuối `QUYET-DINH-CUOI-e_hoi_ai.md` §1–2: bản 1 chỉ Local; module sở hữu prompt theo function; thiếu prompt phải từ chối; nhật ký có module/function/phiên bản prompt. Tệp chưa có trong worktree, đã đọc **chỉ đọc** bản tại thư mục dự án chính: `D:\Claude\Phan mem ho tro ke toan\Phần mềm kho tri thức\docs\47-core\g3\QUYET-DINH-CUOI-e_hoi_ai.md:8–20,35`.
- Phiếu cũ tại mốc `4f180f92`: `PHIEU-ENGINE-e_hoi_ai.md:39–40`; kế hoạch `KE-HOACH-G3-GOI.md:319,349–351`. Mốc `4f180f92` dùng đối chiếu hàng lát cũ; bằng chứng mã dưới đây lấy tại HEAD của worktree. **Không đổi SDK**; wheel 1.4.1 vẫn chỉ candidate theo §6.3.
- TL 48 §1.2: đọc bản tài liệu ở thư mục dự án cha, không đọc cấu hình máy/model hay dữ liệu thật. Chỉ kết luận về mã và test thuần/mock; Local thật, PostgreSQL, launcher Windows, quyền thực tế và lịch sử sau khởi động lại trên Core thật **chưa kiểm**.

Quy ước đường dẫn trong các bảng: **A** = `engines/e_hoi_ai`; **C** = `src/kho_tri_thuc/core`; **S** = `src/kho_tri_thuc/sdk_core`; **T** = `tests`. “Có” là có implementation trong phạm vi kiểm tra, không đồng nghĩa đã vận hành thật.

## Từng khâu của luồng

| Khâu cần có | Có / thiếu / sai | Bằng chứng tệp:dòng và nhận định |
|---|---|---|
| Module gửi việc → Core | **Có khung; thiếu binding AI bản 1** | `S/engine_module.py:22–37,141–146` gửi capability kèm tham chiếu đầu vào, không gửi tùy ý toàn bộ payload AI. `C/dich_vu_engine.py:231–255` chọn loại việc đã ghim và tạo việc kèm tham chiếu; provider `C/kenh_engine.py:396–399` mới phân giải đầu vào. Chưa thấy provider/binding AI bản 1 cụ thể trong `src` và `engines`. |
| Quyền, pháp nhân, contract | **Có khung** | `C/cong_sdk.py:790–813` giới hạn capability theo module đã xác thực; `C/dich_vu_engine.py:153–177` so pins/contract/KT, `:235–255` kiểm phiên/MTQ/công tắc/dedupe. `C/kenh_engine.py:360–367` lấy nguồn từ lease tin cậy, nhưng `ham/phien_ban_ham` hiện là **mã/phiên bản adapter engine** (`C/sql/068_ket_qua_engine.sql:97`), chưa phải function nghiệp vụ của module. Không lấy danh tính do module tự khai làm căn cứ cấp quyền. |
| Prompt của function + mã/phiên bản + tài liệu | **Thiếu** | `C/contract/ky_thuat.json:8–35` đóng khóa, chỉ có `loai_viec/van_ban/chi_dan/truong/dinh_danh_da_biet/chi_cuc_bo`; thêm metadata prompt hiện bị schema bác. `A/lib/cong_ai.py:287–294` DTO cũng thiếu mã/phiên bản prompt và function. Đã có văn bản tài liệu và metadata nguồn ở `A/hoi.py:57–82`, chưa có nối prompt đúng function từ gói module. |
| Thiếu prompt thì từ chối | **Sai so với bản 1** | `C/contract/ky_thuat.json:20` cho `chi_dan` rỗng; `A/lib/cong_ai.py:1204–1205` chỉ kiểm kiểu chuỗi. `T/test_g3_ai_1b.py` còn có test chấp nhận chỉ dẫn rỗng. Không được dùng khung mặc định để thay prompt function bị thiếu. |
| Runtime nhận việc → adapter Hỏi AI | **Thiếu nối** | `A/chay.py:48–70` đọc `yeu_cau_demo`, gọi provider DTO, xuất `ai-demo.json`; `:149` mặc định provider giả; `:202` readiness `contracts=[]`. Trong khi `A/engine.json:11–13` khai báo `ai.hoi@1`. Adapter schema thật ở `A/hoi.py:34–93` chưa được runtime này gọi; `A/hoi.py:44–45` và `A/bi_mat.py:104–110` còn bắt buộc seam Mask kể cả chỉ Local. |
| Cổng AI chung, dùng lại implementation | **Có** | `src/kho_tri_thuc/tri_thuc/cong_ai.py:9–13` alias đúng module `A/lib/cong_ai.py`; bridge Local cũng alias implementation gói. `A/hoi.py:86–93` gọi cùng `CongAI.goi`, không dựng client riêng. Test bridge xác nhận class/module identity. |
| Local AI theo TL 48 §1.2 | **Có trong mã; chưa kiểm máy thật** | `A/lib/ai_cuc_bo.py:35–86` kiểm IP nội bộ/Tailscale, chặn DNS/HTTPS/public IP/model Cloud hoặc remote; `:118–145` socket tới IP và bind nguồn Tailscale; `:171–227` kiểm model trước gửi, tắt proxy/chuyển hướng. Local mặc định tắt (`:26`); không suy ra đã có model sẵn sàng. |
| Ghép khung trích dẫn / không thấy căn cứ | **Có một phần; thiếu hành vi hỏi đáp** | `A/lib/cong_ai.py:61–69,893–899,1208` ghép chỉ dẫn + văn bản + mẫu JSON có trích dẫn. Khi không có thông tin chỉ yêu cầu bỏ trường; `:1242–1243` trả “Chưa có kết quả AI, cần người làm.”; `A/hoi.py:112` luôn `cau_tra_loi=None`. Chưa bảo đảm trả “không thấy căn cứ”; cần phân biệt trường hợp này với Local lỗi. |
| Python kiểm trích dẫn | **Có** | `A/lib/cong_ai.py:783–833` chuẩn hóa khoảng trắng, kiểm đoạn trích thuộc văn bản, giá trị nằm trong trích dẫn, loại trường sai và chạy kiểm Python bổ sung. `A/hoi.py:98–105` chỉ chuyển trường đã giữ sang dẫn chứng có vị trí nguồn. Kiểm này xác nhận chuỗi/căn cứ, không tự chứng minh mọi suy luận của model đúng. |
| Trả kết quả về module | **Có khung; thiếu nối đầu–cuối** | `A/hoi.py:112–130` tạo/kiểm `tra_loi_ai.v1`; `S/viec.py:109–117` có `viec.ket_qua`; `C/kenh_engine.py:694–709` ghi và xác nhận commit. Runtime còn xuất DTO DEMO nên chưa chứng minh module nhận kết quả contract Hỏi AI thật. |
| Nhật ký module/function/prompt/thời gian/kiểm | **Có một phần** | `A/lib/cong_ai.py:355–378,1050–1070` có thời điểm, thời lượng, kết quả, kiểm trích dẫn, pháp nhân/việc; thiếu module/function/mã và phiên bản prompt. `A/nhat_ky.py:75–113` có bàn giao qua SDK, retry cùng bytes và đợi ACK; `C/nhat_ky_ai_legacy.py:68–86` cũng chưa lưu metadata prompt/function. Không coi seam nhật ký giả là bằng chứng lưu bền Core thật. |
| ~~Engine trích → Core → AI~~ **Chuỗi Core → bước Hỏi AI** | ~~**Thiếu transport**~~ **Thay theo CD-111: không bổ sung transport riêng** | Bằng chứng lịch sử: `S/engine.py:70–99`, whitelist `S/kenh_khung.py:65–68` và dispatch `C/kenh_engine.py:653–711` chỉ có nhận/đọc/ghi/heartbeat/kết thúc, chưa có gọi AI. `engines/e_trich_xuat/ai_chung.py:13,103,130–135` vẫn import/nhận `CongAI` rồi gọi trực tiếp trong process. Cổng được tiêm không đồng nghĩa đã đi qua SDK/Core IPC. **Hướng sửa:** tách trích thành chuẩn bị / hậu kiểm; Core xếp bước Hỏi AI ở giữa, không mở operation để trích gọi AI giữa chừng. |
| Bản 1 không có đường Cloud bật được | **Chưa đạt bảo đảm bắt buộc** | `A/lib/cong_ai.py:120` mặc định tắt, nhưng `A/hoi.py:89–90` chỉ ép tắt khi request có `chi_cuc_bo=True`; schema mặc định false (`C/contract/ky_thuat.json:31–34`). `T/test_g3_ai_2.py:128–138,167–179` chứng minh bằng mock: cờ true có 0 Cloud, cờ false có thể gọi Cloud khi cấu hình cho phép. Nhánh trích riêng đã ép Local (`engines/e_trich_xuat/ai_chung.py:130–142`), chưa đủ thay rào chung bản 1. |

## Kiểm đường gọi Cloud trực tiếp

`git grep` toàn bộ tệp được git quản lý trong `src` và `engines` tìm hai domain chỉ thấy implementation provider tại `A/lib/cong_ai.py:657,693` và chú thích cùng tệp. Hai lớp đó thực sự dựng/gửi HTTP qua `_goi_json` (`:667–677,699–706`), không chỉ là tên trong tài liệu. Cổng có kiểm Cloud/Mask trước gọi provider (`:1086–1120`). `src/kho_tri_thuc/m4/review_goc/trich_xuat/cloud.py:11` đã chuyển sang cổng chung.

**Không thấy đường gọi hai domain vượt cổng trong phạm vi mã đã khảo sát. Tuy nhiên không thể xác nhận “không có code gọi API trực tiếp” theo nghĩa tuyệt đối:** provider vẫn tồn tại trong cổng, và đường dùng chúng chưa bị khóa bắt buộc cho bản 1. Chú thích tự nêu “ngoại lệ” ở `A/lib/cong_ai.py:25–29` không thay cho quyết định bản 1 chỉ Local. Không đọc cấu hình thật nên không kết luận trạng thái công tắc triển khai; lát này thực tế không gọi mạng/AI/Mask.

## Việc 1b đề xuất, mỗi việc tối đa 3 tệp

Đây là phạm vi để lead chia/giao sau, **không phải quyền sửa trong 1a hay trong DOC-CD111**. ~~Thứ tự: chốt schema/API → contract → rào Local và adapter/runtime → binding/transport → nhật ký → nghiệm thu.~~ **Thay theo CD-111:** contract 1b-01 đã duyệt → đồng bộ ví dụ/manifest → rào Local và adapter/runtime → binding/nguồn cho bước Hỏi AI → nhật ký → nghiệm thu qua chuỗi Core. Các việc chung tệp phải nối tiếp; việc chuỗi theo CD-110 vẫn chờ duyệt phiếu sửa, không tự mở lát code chuỗi mới.

| Việc | Kết quả và kiểm bắt buộc | Tệp đề xuất, gồm test |
|---|---|---|
| 1b-01 · Contract bản 1 — **DUYỆT (Anh 21:31, 07/11/2026)** | Metadata prompt/function, prompt không trắng; nguồn tin cậy do Core xác minh; đáp ứng đầu ra thiếu căn cứ. Chọn phiên bản tương thích, không đổi âm thầm contract đã ghim. Duyệt phạm vi contract không phải xác nhận đã triển khai xong hoặc duyệt operation gọi AI riêng. | `C/contract/ky_thuat.json`; `A/contract/schemas.json`; `T/test_g3_ai_1b.py` |
| 1b-02 · Ví dụ và manifest | Đồng bộ ví dụ DEMO, manifest theo contract được duyệt; kiểm bản ghim/đầu vào ra. | `A/contract/vi_du.json`; `A/engine.json`; `T/test_g3_goi_ai_mau.py` |
| 1b-03 · Hành vi hỏi đáp Local | Dùng prompt function, giữ khung chung; từ chối thiếu prompt; “không thấy căn cứ” khác lỗi Local; khóa Cloud phía thực thi kể cả payload thiếu/false và cấu hình Cloud bật. | `A/lib/cong_ai.py`; `A/hoi.py`; `T/test_g3_ai_2.py` |
| 1b-04 · Runtime thật | Nối adapter, schema và readiness đúng năng lực; Local hoạt động khi không có Mask/khóa Cloud; giữ ACK/drain. | `A/chay.py`; `A/bi_mat.py`; `T/test_g3_ai_4a.py` |
| 1b-05 · Binding/nguồn Core cho **bước Hỏi AI trong chuỗi** | Dùng hàng việc/lease hiện có; đối chiếu function/prompt với khai báo gói module, không nhầm mã adapter với function; phân giải tài liệu đúng pháp nhân; bác giả danh, sai pin hoặc nguồn ngoài quyền; tạo provider thực thay DEMO. Core giao việc cho bước Hỏi AI, không nhận lượt gọi AI giữa chừng từ engine trích. | `C/dich_vu_engine.py`; `C/kenh_engine.py`; `T/test_g2_32_e1.py` |
| ~~1b-06 · Wire AI hẹp~~ **KHÔNG làm đường riêng — thay theo CD-111** | ~~Chỉ khi API được duyệt: thêm operation có schema đóng, giới hạn theo lease, không RPC tổng quát.~~ Việc cần AI nối bằng chuỗi engine Core điều phối theo CD-110; không mở operation AI riêng cho engine trích. | ~~`S/kenh_khung.py`; `T/test_kenh_0.py`~~ Danh sách cũ chỉ giữ để đối chiếu, không còn là whitelist triển khai. |
| ~~1b-07 · SDK engine~~ **Bỏ dạng gọi AI giữa chừng — thay theo CD-111** | ~~Thêm method gọi operation đã duyệt; kiểm dữ liệu/lease/lỗi; không gọi model trong SDK.~~ Kiểm dữ liệu, lease và lỗi của **bước Hỏi AI trong chuỗi** bằng kênh việc chuẩn; không thêm method để engine trích gọi AI hoặc gọi model trong SDK. | ~~`S/engine.py`; `T/test_g2_20.py`~~ Không giao lát SDK riêng theo thiết kế cũ. |
| ~~1b-08 · Core nhận lượt AI~~ **Bỏ dạng gọi AI giữa chừng — thay theo CD-111** | ~~Dispatch/provider dùng cùng cổng, ép Local; kiểm lease/phạm vi, không giữ transaction trong thời gian đợi AI; mất kết nối/model lỗi không sang Cloud.~~ Giữ các yêu cầu này cho **bước Hỏi AI trong chuỗi**, phân vào 1b-03/04/05 và bài nghiệm thu; không tạo dispatch nhận lời gọi riêng từ trích. | ~~`C/kenh_engine.py`; `T/test_g2_32_e1.py`~~ Lead khóa lại tệp/test theo bước chuỗi, không mở rộng từ danh sách cũ. |
| 1b-09 · Nhật ký đủ provenance | Bổ sung module/function/mã và phiên bản prompt từ nguồn đã xác minh; giữ thời gian/kiểm; ACK, phát lại không trùng, không lưu prompt/tài liệu/khóa vào metadata. Ưu tiên tệp kết quả qua Core hiện có. | `A/lib/cong_ai.py`; `A/nhat_ky.py`; `T/test_g3_ai_5a.py` |

Nếu cách lưu nhật ký được chốt cần đổi CSDL/quyền hoặc bổ sung tệp ngoài các nhóm trên, lead tách việc N và whitelist mới trước giao; không ngầm sửa `pg_migrations.py` hay mở rộng lát. Module quản lý prompt và quyền sửa prompt thuộc module theo quyết định cuối, không thêm trình quản lý prompt vào engine. Việc cấp binding/pins thật và kiểm PostgreSQL do lead thực hiện.

**Yêu cầu bắt buộc của bước Hỏi AI trong chuỗi (chuyển từ 1b-07/08, thay theo CD-111):** Core kiểm quyền/pháp nhân/lease và nguồn prompt/function trước khi giao bước; bản 1 ép Local kể cả cờ thiếu/false hoặc cấu hình Cloud bật; không giữ transaction CSDL khi chờ AI; mất kết nối hoặc model lỗi thì báo rõ/cho thử lại, **không chuyển Cloud**. SDK chỉ trao đổi việc và kết quả theo chuẩn, không gọi model. Các yêu cầu này không bị bỏ cùng ba lát đường riêng.

**Ví dụ chuỗi trích hợp đồng theo CD-111 mục 2 trong handoff:** module gửi tệp + loại + bộ tham số đã cố định → Core chạy OCR nếu cần (Word bỏ qua) → **Trích chuẩn bị** văn bản, trường cần lấy và đầu vào theo prompt function của module → **Hỏi AI Local** qua cổng chung → **Trích hậu kiểm** kết quả, trường thiếu và trích dẫn → Core trả bảng thông tin về module. Core kiểm khớp đầu ra/đầu vào và điều phối đúng thứ tự đã khai; engine trích không gọi Hỏi AI, engine Hỏi AI không gọi engine trích. Đánh giá hỏi lại trường thiếu xem [phiếu trích mục 1](PHIEU-ENGINE-e_trich_xuat.md#1-hợp-đồng-việc-và-trách-nhiệm).

~~**G3-GOI-34 sau 1b:** tháo import lõi AI khỏi trích, port sang operation SDK đã chạy được và kiểm wheel/alias/class identity độc lập. Không lấy việc đóng gói để coi transport đã có.~~ **Thay theo CD-111:** tách engine trích thành các bước chuỗi (chuẩn bị / hậu kiểm), không còn import `CongAI` trong engine trích; kiểm tương thích gói vẫn giữ, không làm operation gọi AI riêng. DOC-CD111 không đổi version, không build/phát hành/ghim wheel; SDK 1.5.0 đã phát hành cho CRM không tự đổi bản ghim engine, wheel 1.4.1 vẫn chỉ candidate (§6.3).

## Điểm cần chốt

| Người chốt | Câu cần quyết định | ☑ Đề xuất |
|---|---|---|
| ~~Anh, sau khi lead trình schema/API cụ thể~~ **Đã chốt theo CD-111** | ~~Duyệt phần mở rộng contract metadata prompt và operation AI dành cho engine trích?~~ **1b-01 DUYỆT (Anh 21:31); 1b-06 KHÔNG làm đường riêng.** | ~~☑ Dùng lại kênh có sẵn, bổ sung operation Local hẹp theo lease; không cho engine tự khai danh tính/phạm vi, không transport thứ hai. Module gửi việc vẫn dùng API hiện có.~~ **Thay theo CD-111:** nối bằng chuỗi Core theo CD-110; không xin duyệt lại 1b-01 hoặc mở operation riêng. |
| Lead | Lưu đủ nhật ký bằng tệp kết quả Core hay cần cấu trúc lưu khác? | ☑ Ưu tiên cơ chế Core hiện có, nguồn lease và đối chiếu function/prompt theo gói module; nếu phải đổi CSDL/quyền, tách N để lead kiểm PG/Opus. |
| ~~Anh, phần đã ghi chờ ở quyết định cuối~~ **Đã kê khai theo CD-106** | ~~Model Local nào trên máy GPU để nghiệm thu thật?~~ gpt-oss-20b, Qwen3 8B và Gemma đã được kê khai; còn kiểm kết nối/model thực tế do lead. | ~~☑ Kê khai model khi làm lát Local thật; không cản việc contract/transport và mock của 1b.~~ Làm phát hiện/chọn model và kiểm Local theo CD-106. Không yêu cầu mở Cloud hoặc cấp khóa cho bản 1. |

Bản 1 chỉ Local và prompt thuộc module **đã chốt**, không xin duyệt lại hai nguyên tắc này.

## Test trước/sau và phần chưa kiểm

Chạy đúng Python `D:\KTT-CD060-DEMO\python313\python.exe`, `-X utf8 -B -m unittest`, cwd worktree, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH` gồm `src;tests` của worktree và thư mục `deps` được handoff chỉ định. Không nạp tệp runtime/cấu hình thật. Hai lượt chạy cùng các lựa chọn dưới đây:

| Nhóm thuần/mock | Trước: ok/fail/error/skip | Sau: ok/fail/error/skip |
|---|---:|---:|
| `tests.test_g3_ai_1a`, `tests.test_g3_ai_1b`, `tests.test_g3_ai_2`, `tests.test_g3_goi_ai_loi` | 42/0/0/0 | 42/0/0/0 |
| `tests.test_ai1_local_ai_lan.AddressTests`; `tests.test_cong_ai.BangLoaiViecVaCaiDatTests`, `.DanhGiaTrichDanTests`; `tests.test_cong_ai_nhat_ky.BoGhiPostgresThuan`, `.MigrationThuan` | 22/0/0/0 | 22/0/0/0 |
| **Tổng** | **64/0/0/0** | **64/0/0/0** |

Chỉ chọn lớp thuần/mock: không chạy lớp tích hợp HTTP tạo server hoặc lớp PostgreSQL; không chạy `tests.test_v3`, `tests.test_v7`. Các test trước xác nhận cờ chỉ Local chặn Cloud khi Local lỗi/không chắc/được chọn kiểm, kiểm dẫn chứng sai, địa chỉ/model, bridge và ghi SQL qua kết nối giả. Chúng kiểm contract cũ; xanh không có nghĩa các yêu cầu bản 1 mới đã đủ.

Thời gian runner ghi nhận: trước 1,795 giây, sau 3,659 giây (tổng hai nhóm mỗi lượt). **Lỗi mới: không trong 64 test đã chạy; skip không tăng.** Đã đọc nền `docs/46-chuyen-doi-dieu-phoi/NEN-TEST.md` §0; các nhóm mới dùng kết quả trước/sau làm đối chứng, không suy rộng thành toàn bộ nền xanh. Không chạy toàn bộ nền hoặc bài UI đầu–cuối trong 1a. Lịch sử sau restart, cách ly pháp nhân, Local LAN/Tailscale/model thật và nghiệm thu bản 1 vẫn cần lead kiểm ở các lát tương ứng. Phạm vi thay đổi cuối: chỉ tệp báo cáo này, UTF-8 có dấu; kiểm `git status` chỉ thấy tệp mới được phép, không có mã sửa.

### Kiểm tài liệu DOC-CD111 — 07/11/2026

Số **64** phía trên là lịch sử lát 1a, giữ nguyên để đối chiếu. DOC-CD111 chạy lại đúng các module/lớp thuần/mock đã liệt kê bằng Python và `PYTHONPATH` trong handoff; bộ test hiện hành có **72 ca**. Không sửa test hoặc mã sản phẩm.

| Phạm vi | Trước: ok/fail/error/skip | Sau: ok/fail/error/skip |
|---|---:|---:|
| Các module/lớp thuần/mock liệt kê ở bảng 1a phía trên | **72/0/0/0** | **72/0/0/0** |

Không có lỗi mới trong phạm vi đã chạy; không tăng skip. Đã kiểm UTF-8 nghiêm ngặt của cả bốn tệp, rà nội dung và `git diff --check`. Chỉ sửa bốn tài liệu được giao, giữ nội dung hết hiệu lực bằng gạch/ghi “thay theo CD-111”; không commit, đổi SDK, thêm thư viện hoặc chạy PG/server/AI thật. Chưa kiểm vận hành chuỗi/Local thật. Lead cần chốt lại giờ thực còn lại, whitelist tách bước trích và trình phương án lặp có giới hạn; nguồn CD-111 hiện lấy từ handoff, cần đối chiếu khi bản chỉ đạo được đồng bộ.
