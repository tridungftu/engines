# MASK-2c-4 — Sửa theo kiểm độc lập của lead, 15/11/2026

**Kết luận: Đạt phần sửa công cụ/dữ liệu theo lead; đã kiểm bằng Core giả (CoreGia). CHƯA ĐO Local thật, chưa nghiệm thu Core thật.** Bộ vẫn là **ỨNG VIÊN, chờ lead đóng băng**; `held_out_doc_lap=false`. PR: **chờ lead mở**. Không commit/push, không sửa runtime gói.

**Đã làm:** bổ sung 28 ca, tách mẫu số chặn trước AI/AI thực sự đo/tổng, thêm timeout theo số đoạn với dừng tiến trình con và báo cáo từng phần, đo che thừa ở ca có định danh, `.cmd` ASCII/CRLF và giới hạn thư mục báo cáo. Vẫn đúng ba tệp mã/dữ liệu ngoài gói; test/tài liệu cập nhật riêng.

**Kết quả kiểm:** riêng công cụ **50 passed, 0 skipped, 41,13 giây, mã 0**; toàn Mask **1159 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 160,89 giây, mã 0**. SDK CLI **0/2, mã 1**, cả hai thiếu nguồn phiên/quyền; adapter DEMO **2/2 ĐẠT, mã 0**; kiểm độc lập **ĐẠT, mã 0**. Chạy khô: **190 ca, 63 ca người, 124 gold span**, `ket_qua=null`, 0 lượt Local/Cloud. [Đầu ra lệnh](KET-QUA-KIEM-MASK-2c-4.txt).

**Thời gian thực tế:** **15:01–15:23:45 ngày 15/11/2026 (UTC+07), 0,38 giờ**; phiếu MASK-2c-4 **5 giờ ƯỚC TÍNH**, không có dự toán riêng cho lượt sửa. Mốc bắt đầu theo lead.

**Lệch khỏi phiếu / quyết định tạm:** CLI thật tách từng ca sang tiến trình con để áp timeout cứng trên Windows/Linux; không thêm dependency. Các tiến trình dùng CoreGia và ngăn/snapshot RAM. Biên nhận budget/tokenizer/nguồn vẫn là fixture, không chứng nhận Core/model thật. Không chạy model thật, không dùng oracle trên bộ ứng viên mới hoặc đổi detector/prompt theo ứng viên.

**Cần Core / Chờ Anh mới phát sinh:** không thêm yêu cầu Core/SDK; giữ C-M2C-01…05 và nợ CAO. Lead đóng băng/gold độc lập, xác minh backend Local/egress trước đo thật; Anh chạy `.cmd`. Local đạt cũng chưa bật Cloud.

## Bộ ứng viên sau sửa

| Nhóm | Cũ giữ nguyên | Mới | Tổng |
|---|---:|---:|---:|
| Người | 45 | 18 | 63 |
| Câu thường | 75 | 0 | 75 |
| Tổ chức | 15 | 5 | 20 |
| Địa chỉ | 15 | 5 | 20 |
| Biến thể cũ | 12 | 0 | 12 |
| Tổng | 162 | **28** | **190** |

Có **124 gold span**. 18 ca người mới đều không dấu: Hoa đầu chữ/IN HOA, 2 hoặc 4 âm tiết; đủ họ hà/hồ/lương/văn/phan/mai và danh xưng ông/bà/anh/chị/TS./ThS./Mr. Năm tổ chức và năm địa chỉ mới có span không chứa chữ DEMO; mỗi nhóm phủ đủ hợp đồng, email, biên bản, bảng kê, chữ ký. Nhãn DEMO và nguồn hư cấu nằm ngoài span. Sáu ca dài kiểm theo `lap_ke_hoach` thực: đầu/cuối toàn văn, đầu/cuối đoạn nội bộ, tên nằm trọn trong overlap và tên vắt biên đoạn chính; không ước lượng mép bằng hằng số. Gold có loại, nguyên văn và offset code point nửa mở chính xác.

Giữ nguyên 162 ca cũ, development và bốn ca hồi quy lead. Đã kiểm 28/28 định danh mới không trùng trên **803 tệp UTF-8 Git quản lý**, trừ chính bộ mới và đường cấm; chuẩn hóa dấu/hoa/khoảng trắng trước đối chiếu. Không dùng hồ sơ thật hoặc tên nhân vật nhận ra được; đây là dữ liệu hư cấu tự soạn, chưa phải gold độc lập.

SHA-256 `noi_dung` JSON UTF-8 chuẩn (`ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False`):

```text
b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad
```

## Mẫu số và che thừa

`ket_qua.hai_lop` là tổng toàn bộ ca; `phan_tach` có ba nhóm loại trừ nhau:

- `chan_truoc_ai`: lớp quy tắc từ chối nghiệp vụ trước AI; số đoạn AI hoàn tất bằng 0.
- `ai_thuc_su_do`: ít nhất một đoạn AI-9 trả XONG; kèm số đủ đoạn, số hợp lệ và số chưa đo đủ. Có một đoạn xong không chứng minh đã đo xong ca.
- `chua_co_doan_ai_xong`: chưa có đoạn AI-9 XONG, gồm lỗi trước gửi/model/context, lỗi trả lời, timeout hoặc chưa chạy. Số gọi provider báo riêng, không tự coi là số POST thành công.

**0 lọt trên ca bị chặn trước AI là hiển nhiên.** Không lấy các ca này làm bằng chứng AI có recall tốt. Từng nhóm và tổng đều có số lọt theo ca/span, mẫu số ca/span thực sự phát hành, tỷ lệ lọt tương ứng; báo nhầm câu thường = hợp che thừa hoặc chặn nghiệp vụ / số câu thường của chính nhóm, kèm mẫu hợp lệ. Mẫu phát hành rỗng cho tỷ lệ `null`. Ca chưa đo đủ giữ số span lọt và che thừa `null`; không đổi lỗi/timeout thành đạt 0 lọt.

Che thừa được tính cho mọi phép che đã đối chiếu độc lập: phần khoảng che nằm ngoài **hợp các gold span**. Báo từng ca số span che thừa/số ký tự che thừa, và tổng `che_thua_dinh_danh` trên các ca có gold (người/tổ chức/địa chỉ và biến thể). Giữ riêng tử số/mẫu số báo nhầm câu thường. Nếu nhãn DEMO ngoài gold bị lớp quy tắc che, phần đó cũng bị tính che thừa; không bỏ để làm đẹp số đo.

## Timeout và báo cáo từng phần

- `--timeout` là số giây mỗi ca; mặc định **120 × số đoạn thực**, chặn bởi `--timeout-toi-da` (mặc định **3600 giây**). Giá trị phải dương, hữu hạn. Timeout socket mỗi lượt vẫn tuân thủ trần AI-9 **600 giây** và thời gian còn lại; không sửa runtime.
- CLI `--that` chạy từng ca trong tiến trình con, timeout cứng tính cả khởi tạo/đo quy tắc/hai lớp của ca. Parent kill và wait child khi hết hạn; giữ checkpoint hoàn chỉnh gần nhất trong RAM, số đoạn đã hoàn tất và mọi ca trước đó. Ca/đoạn chưa đủ được ghi `tinh_trang_do="chưa đo đủ"`, `HET_HAN_CHUOI`; tiếp tục ca kế tiếp. Số timeout cứng xác định báo riêng với ChuaRo mơ hồ của transport.
- Ngoại lệ giữa chừng: giữ kết quả trước đó, đánh dấu ca còn lại chưa đo đủ, ghi JSON từng phần rồi thoát mã 1. Message/traceback/provider output không được phản chiếu vào báo cáo. Dừng child không xác nhận backend đã hủy request; không tự gửi lại ca timeout.
- Không chỉ định `--bao-cao` thì chỉ in JSON. Có đích thì phải là `.json` mới, thư mục đã tồn tại, không ghi đè. Mặc định đích phải ngoài repo; trong repo cần `--thu-muc-bao-cao` trỏ đúng thư mục cha riêng, không phải repo root/mã engine/docs/_chung/.git.

Ví dụ sau khi lead đóng băng (placeholder, không chứa địa chỉ máy thật):

```cmd
"e_mask\cong-cu\THU-MASK-LOCAL-AI-THAT.cmd" --that --url "<URL-IP-LOCAL>" --model "<MODEL-LOCAL>" --bao-cao "<THU-MUC-NGOAI-REPO>\mask-demo.json"
```

Có thể thêm `--timeout 300 --timeout-toi-da 1800`. Nếu chủ động lưu trong một thư mục báo cáo riêng của repo, cần thêm `--thu-muc-bao-cao "<THU-MUC-BAO-CAO-RIENG>"` và chọn tệp ngay trong thư mục đó. `.cmd` được ghi **CRLF** đúng `.gitattributes`, giữ ASCII/quote/`-B`; có test Windows đường dẫn chứa khoảng trắng. Chạy khô mặc định không mạng, không đo detector/Local giả; mã 0 khi khô không phải nghiệm thu.

## Kiểm lại và giới hạn

Toàn bộ tích hợp mới **đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả. 50 test công cụ gồm dữ liệu/gold/SHA/mép/overlap, mẫu số tách, ba loại che thừa, che thừa toàn chuỗi, timeout tham số/socket/cứng, giữ đoạn đã xong, ngoại lệ giữa chừng, ghi báo cáo từng phần không lộ gốc/URL/path, đích chỉ định và CRLF. Không kiểm Linux thực tế; test Python/subprocess dùng thư viện chuẩn, test cmd chỉ Windows có skip có lý do trên Linux. Bốn xfail held-out lớp 1 giữ nguyên. Không chạy lại riêng toàn bộ Hỏi AI vì không sửa runtime/adapter của engine đó; chuỗi AI-9 được chạy qua bộ test công cụ.

Các lượt thử trung gian: 4 failed/43 passed (test cũ chưa chỉ định thư mục báo cáo, budget timeout quá ngắn để đến POST và dữ liệu mới chưa ghi xong); sau đó 47 passed. Thêm ba bài kiểm sâu có lượt 2 failed/48 passed: kỳ vọng che thừa chưa tính nhãn DEMO bị che ngoài gold, và deadline test dài chưa đủ tới đoạn đầu. Đã sửa kỳ vọng để tính đầy đủ che thừa, tăng thời hạn fixture rồi đạt 50 passed; không sửa runtime/gold để làm xanh. Một lượt full test đang chạy được dừng để sửa fixture, không tính là lượt kiểm hoàn tất.

---

## Lịch sử bàn giao trước kiểm độc lập (14:22–14:53)

Phần dưới lưu số liệu/băm/hướng dẫn **của bản trước**, không thay thông số hiện hành ở trên.

# MASK-2c-4 — Công cụ đo DEMO Local ngoài gói

**Kết luận: Chưa đạt nghiệm thu Local/Core thật; phần công cụ và mock đã kiểm bằng Core giả (CoreGia). CHƯA ĐO Local thật.** Bộ mới là ứng viên, **chưa lead đóng băng/gold độc lập**, không tự nhận là held-out độc lập. PR: **chờ lead mở**; không commit/push.

**Đã làm:** đúng ba tệp mã/dữ liệu ngoài gói: `cong-cu/thu_mask_local_ai_that.py`, `cong-cu/THU-MASK-LOCAL-AI-THAT.cmd` (ASCII), `cong-cu/mask_2c_4_ung_vien_demo.json`. Thêm test ngoài gói; cập nhật VIEC/CHANGELOG/tài liệu. Không sửa runtime Mask/Hỏi AI, Core/SDK/nguồn cũ/schema/dependency, không bật Cloud.

**Kết quả kiểm:** Mask **1143 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped**; riêng 34 test tool sau các chỉnh metadata/đích báo cáo cuối **34 passed**. Hỏi AI hồi quy **560 passed, 0 skipped**. DEMO có quyền Mask **2/2**, Hỏi AI **3/3 + 1 ca AI-9**; kiểm độc lập hai gói đạt. CLI SDK chuẩn Mask **0/2, mã 1** vì thiếu quyền; Hỏi AI **0/3, mã 1** vì thiếu cấu hình. `git diff --check` đạt. [Kết quả lệnh](KET-QUA-KIEM-MASK-2c-4.txt). Không nới cửa để làm xanh.

**Thời gian thực tế:** **14:22–14:53 ngày 15/11/2026 (UTC+07), 0,52 giờ**; mốc bắt đầu theo lead, mốc kết thúc bàn giao làm tròn phút. Phiếu **5 giờ ƯỚC TÍNH**, độ khó **vua**.

**Lệch khỏi phiếu / quyết định tạm:** không có bộ nghiệm thu độc lập mới do lead cung cấp nên soạn ứng viên đúng nhánh dự phòng Anh giao. Không chạy model thật. CoreGia dùng lại fixture quyền/snapshot/chứng thực/budget hiện có ngoài gói; token trong biên nhận là fixture, **chưa đo tokenizer thật**, không được lấy làm chứng nhận sức chứa. AI-9 giữ nguyên kiểm context đang tải và budget byte bảo thủ; thiếu metadata/model/context vẫn lỗi. Không chỉnh detector/prompt từ kết quả ứng viên, không chạy oracle gold trên bộ ứng viên mới.

**Cần Core / Chờ Anh mới phát sinh:** chưa thêm API; giữ C-M2C-01…05 và nợ CAO. Chờ lead giữ khâu gold/đóng băng độc lập và xác minh backend Local/egress; Anh chạy `.cmd`. Local đạt cũng không bật Cloud. Nợ transport AI-9 sau POST lead nêu giữ nguyên vì không chạm `e_hoi_ai`; lỗi/chưa rõ không tính là detector thành công.

## Bộ ứng viên và gold

| Nhóm | Ca | Ghi chú |
|---|---:|---|
| Tên người viết thường mới | 45 | 45 tên cơ sở/45 ngữ cảnh khác nhau; có họ hiếm, viết tắt, tên nước ngoài, gạch/nháy, lặp |
| Câu thường mới | 75 | Không bỏ ca mập mờ/viết sai; gold/quy tắc xử lý giữ từ trước chạy |
| Tổ chức DEMO | 15 | Gold span cụ thể |
| Địa chỉ DEMO | 15 | Gold span cụ thể |
| Biến thể riêng | 12 | NFD/Cf/selector/tab/NBSP/lặp/overlap/mép đoạn/chuỗi dài tới khoảng 100.000 code point; không tăng 45 tên cơ sở |
| Tổng ứng viên | **162** | **96 gold span** tính từng lần xuất hiện |

`development` có 2 ca riêng; `hoi_quy_lead_cu` có bốn ca đã biết, không tính vào 162 ca mới. Mọi tên/tổ chức/địa chỉ là tổ hợp giả tự soạn, không lấy từ hồ sơ thật. Test chỉ kiểm nhãn/băm/offset/số lượng và tính mới; không dùng ứng viên để điều chỉnh runtime/prompt. Sau khi xem held-out để chỉnh, phải soạn held-out khác.

SHA-256 của `noi_dung` JSON UTF-8 chuẩn (`ensure_ascii=False`, `sort_keys=True`, `separators=(",",":")`, `allow_nan=False`):

```text
a32a84a90f5f3391761f07a24ccdad4a5349f52626c7564fddef0c0cbb1ea076
```

Đây là băm có thể tái tính, **không phải chữ ký/xác nhận độc lập của lead**. Lead cần giữ gold và mốc đóng băng trước đo nghiệm thu; nếu thay bộ, tính lại SHA trước chạy và giữ bộ đo/gold bất biến. Công cụ luôn báo `held_out_doc_lap=false` cho bản ứng viên này.

## Cách đo và giới hạn kết luận

Tool ngoài gói đóng vai Core, cấp quyền/ngăn/snapshot DEMO trong RAM. Lớp quy tắc gọi năng lực che hiện tại qua CoreGia; hai lớp gọi chuẩn bị → AI-9 nguyên bản cho từng đoạn → ghép tất cả phản hồi vào kho CoreGia → hậu kiểm. Không thêm lời gọi engine khác vào gói Mask. Không bỏ trần/kiểm IP, DNS/proxy/redirect, remote model, model đang tải, context, JSON/schema/span/hoàn tất của Hỏi AI; model Anh chọn mất thì từ chối, không dùng model khác. Cờ nguồn/biên nhận Core là giả trong adapter, không chứng nhận ACL/lease/tokenizer/cửa Cloud thật.

Bộ chấm độc lập detector đi tuần tự hai chuỗi, tra alias đã chốt trong ngăn và xác minh nguyên văn giữ lại; ánh xạ không khớp/không duy nhất là lỗi đo. Gold phải được che đủ khoảng, không chỉ prefix; phép dò độc lập bỏ dấu/Cf/khoảng trắng/dấu câu kiểm phần nhận diện còn lại. Báo từng ca và tổng riêng: phát hành che đủ, phát hành còn lọt, chặn nghiệp vụ, lỗi kỹ thuật, chưa rõ. Số lọt có mẫu số gold span/tên cơ sở/tổng ca và số thực sự phát hành; không suy recall từ số không phát hành.

Báo nhầm = hợp câu thường che thừa hoặc chặn nghiệp vụ / **75**; kèm số ca hợp lệ/tổng, tỷ lệ trên mẫu hợp lệ và số câu phát hành nguyên vẹn. Lỗi kỹ thuật/chưa rõ không thành “không báo nhầm”. Không có số Local thật trong báo cáo này. Kết quả từ mock chỉ kiểm công cụ, không thay phép đo chất lượng model.

Báo cáo JSON có mã ca, số đếm, phiên bản/băm tool/engine/model/prompt/khuôn/profile/cấu hình không URL, thời điểm và p50/p95. Model có tên đơn giản thì ghi tên; tên khác chỉ ghi băm để tránh mang đường dẫn. `so_luot_local` là số gọi **provider**, kể cả lỗi trước POST; số đoạn AI xong/đủ kế hoạch báo riêng. Không tự nhận các lượt gọi provider đều đã POST thành công. AI-9 gom timeout/mất phản hồi/202 vào `ChuaRo`, nên số timeout xác định để `null`, báo số `chua_ro` thật; không tự điền timeout bằng 0. Không lưu gốc/trích dẫn/URL/path/mã mở che; không ghi báo cáo runtime vào thư mục engine. Không ghi đè tệp đã có.

**AI chỉ cứu được khi AI báo đủ — AI báo thiếu một phần tên thì phần còn lại lọt.** Bốn test tham số hóa với AI giả báo đúng đều che hết bốn ca lead cũ; test AI chỉ báo prefix xác nhận vẫn phát hành còn lọt. Nếu đã thấy một ca lọt thì kết luận không đạt ngay, kể cả ca khác lỗi kỹ thuật; không biến lỗi/timeout/thiếu model/đoạn thành “0 lọt đạt”. Kết quả 0 quan sát trên ứng viên cũng không cấp quyền bật Cloud.

## Anh chạy sau khâu lead giữ gold

Mặc định, từ bất kỳ thư mục làm việc nào:

```cmd
"e_mask\cong-cu\THU-MASK-LOCAL-AI-THAT.cmd"
```

Anh thay placeholder bằng IP Local có cổng và model đã xác minh; chỉ DEMO. Tệp báo cáo tùy chọn phải ở ngoài thư mục engine, tên mới có đuôi `.json`:

```cmd
"e_mask\cong-cu\THU-MASK-LOCAL-AI-THAT.cmd" --that --url "<URL-IP-LOCAL>" --model "<MODEL-LOCAL>" --bao-cao "bao-cao-mask-local-demo.json"
```

Mẫu trên không chứa địa chỉ máy thật. `--tap development` hoặc `--tap hoi_quy_lead_cu` chọn hai nhóm riêng; mặc định `ung_vien`. Không gộp số liệu các nhóm để thay mẫu số nghiệm thu. Mã thoát: 0 khi chạy khô hợp lệ hoặc đo ứng viên đủ và quan sát 0 lọt; 1 khi chưa đo đủ/có lọt/Cloud khác 0; 2 khi tham số/bộ/ghi báo cáo không hợp lệ. **Mã 0 của công cụ không phải nghiệm thu held-out/Core thật hoặc quyền bật Cloud.**

## Lệnh kiểm thực tế

Mọi lượt tích hợp ở đây **đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả trên loopback. Không chạy Local thật, không chạy Linux/Core thật. SDK 2.0.0 cài offline từ wheel; SHA khớp `SHA256SUMS.txt`: `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Python 3.13.14, pytest 9.1.1 có sẵn; `.venv` dùng system-site-packages cho test, không thêm dependency engine.

| Lệnh (`.venv/Scripts/python -B`) | Kết quả thật | Mã |
|---|---|---:|
| `-m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | 0/2; cả hai thiếu quyền/phiên | 1 |
| `-m pytest e_mask/tests -q` | 1143 passed, 4 xfailed, 190 subtests passed; 189,07 giây; 0 skipped | 0 |
| `-m pytest e_mask/tests/test_mask_2c_4.py -q` | 34 passed; 26,53 giây, sau chỉnh metadata/đích báo cáo cuối | 0 |
| `e_mask/tests/kiem_doc_lap.py` | Gói độc lập đạt | 0 |
| `e_mask/tests/chay_demo.py` | 2/2; CoreGia có quyền/ngăn DEMO | 0 |
| `-m pytest e_hoi_ai/tests -q` | 560 passed; 181,10 giây; 0 skipped | 0 |
| `-m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai` | 0/3; `CHUA_CAU_HINH`, chưa cấp cấu hình/model | 1 |
| `e_hoi_ai/tests/kiem_doc_lap.py` | Gói độc lập đạt | 0 |
| `e_hoi_ai/tests/chay_demo_voi_local_gia.py` | 3/3 DEMO, thêm 1 ca AI-9; tất cả Local HTTP giả | 0 |
| `e_mask/cong-cu/thu_mask_local_ai_that.py` | Khô: 162 ca/96 gold span; `CHƯA ĐO Local thật`, kết quả đo `null`, 0 lượt Local/Cloud | 0 |
| `git diff --check` | Không lỗi khoảng trắng | 0 |

Bốn `xfail strict` là bốn ca held-out lớp quy tắc đã biết, giữ nguyên; bốn test hai lớp với AI giả báo đủ là test riêng, không biến xfail thành thành công Local thật. Không có skip trên Windows; test chạy `.cmd` có điều kiện skip trên Linux với lý do Windows-only, phần kiểm ASCII/quote vẫn chạy ở Linux.

Lượt đầu tool test: **12 failed, 20 passed**, do adapter chưa khai bảng RAM `chuan_bi_ai`; đã bổ sung khai bảng ngoài gói. Các lượt sau đạt; có kiểm riêng timeout phải thực sự ra `CHUA_RO` thay vì lỗi fixture. Không sửa runtime/gold để làm xanh. Lượt toàn Mask trước đó 1141 passed; lượt sau có đủ 34 test mới là 1143 passed. Sau cùng chỉ chỉnh nhãn “đã thử Local”, kiểm đích báo cáo mọi engine và metadata timeout chưa xác định; chạy lại toàn bộ 34 test tool đạt. Bài báo nhầm/mock chỉ dùng development/hồi quy; không lấy tỷ lệ mock làm số đo Local thật.
