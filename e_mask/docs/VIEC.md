# VIỆC — danh sách việc duy nhất của project `e_mask`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc yêu cầu chung/SDK 2.0, yêu cầu Mask và lập kế hoạch lát có giờ ước tính; trình Anh qua lead | MASK-P | Xong — 14/11/2026 (lập phiếu) | [GIAO-CODEX-e_mask.md](GIAO-CODEX-e_mask.md): 14 lát MASK-0…13, 52–62 giờ ước tính chưa đo; phần tệp có điều kiện, chưa triển khai; PR: **chờ lead mở** |
| 1 | Chuyển kho bí danh sang **ngăn của engine** theo cổng chung (thay `mask.py`/`kho_mask.py`/SQL 113, 117–120 trong Core) | MK-10, 19 | Chờ Core | Bàn cùng lead Core qua Anh |
| 2 | J8b: đối soát mất xác nhận | — | Chờ làm |  |
| 3 | Lát 4: màn duyệt danh sách chờ (Admin) — giao diện của engine | MK-15, 16 | Chờ làm |  |
| 4 | Lát 5: màn thử che/mở che DEMO | — | Chờ Anh | Duyệt `PHIEU-MASK-CHAY-THU-DEMO.md` |
| 5 | Lát 8: che/mở che Word/Excel (mẫu 5–8) | §1.3 | Chờ làm |  |
| 6 | Lát 6: 8 contract (Anh duyệt tên) → lát 7: bài 11 bước | — | Chờ làm |  |
| MASK-P | Lập phiếu giao Codex theo SDK 2.0; chỉ tài liệu, không tạo gói/không sửa nguồn | MK-1…6, 10…22 | Xong — 14/11/2026 | [Phiếu giao](GIAO-CODEX-e_mask.md): 14 lát, 52–62 giờ ước tính có điều kiện. Regex 14/14 khối đạt; 5 mục/bảng lát/tổng giờ khớp; UTF-8/NFC và kiểm khoảng trắng đạt, `git diff --check` mã 0. Ba lệnh kiểm gói AGENTS.md §5 không áp dụng theo ngoại lệ lát chỉ tài liệu; không chạy hoặc nhận là đã kiểm bằng CoreGia. Đề xuất `van_ban_da_che` ở cuối sổ chung mang nhãn **ĐỀ XUẤT MASK-P, chờ Anh**. Không commit/push; PR: **chờ lead mở** |
| MASK-3 | Port kho/quyền, kho tạm và chống trùng sau MASK-2 | MK-10…13, 16…19 | Xong phạm vi port/CoreGia — 14/11/2026 | Chỉ DEMO; đúng bốn tệp mã. Pytest 225 passed, 190 subtests passed; kiểm độc lập ĐẠT. CLI SDK 0/2 ĐẠT do handler MASK-5 còn stub; chưa đạt nghiệm thu chung. PR: **chờ lead mở** |

Các số “lát 1…8/J8b” ở các dòng lịch sử là mã kế hoạch cũ; kế hoạch giao SDK 2.0 dùng `MASK-0…MASK-13` trong phiếu mới. Hoàn tất MASK-P không có nghĩa đã code, kiểm bằng CoreGia hoặc nối Core thật. MASK-P ước tính 1 giờ; tổng giờ 52–62 là dự toán triển khai sau, cập nhật lại sau khảo sát tệp MASK-7.

## MASK-0 — 14/11/2026

- Xong khung MASK-0; PR: **chờ lead mở**. Hai năng lực văn bản trả `CHUA_LAM`, chưa kích hoạt vận hành. Cấu hình chỉ chấp nhận đối tượng rỗng, chờ whitelist tài nguyên detector; Linux dùng đường DEMO tường minh.
- Đã kiểm bằng Core giả (CoreGia): hai handler trả lỗi, không báo `XONG`; cổng DEMO nghiệp vụ **chưa đạt** do stub. `kho_tri_thuc_sdk.thu`: 0/2 ĐẠT, mã thoát 1; pytest: 9 passed, 0 skipped; kiểm độc lập: mã thoát 0.
- Mã cũ giữ nguyên; hiện vật không mang sang gói theo mục MASK-P để lead xem xét lưu trữ sau. Nhu cầu Core đã ghi bên dưới; MASK-0 không phát sinh yêu cầu mới.

## MASK-1 — 14/11/2026

- **Xong phạm vi lõi thuần**, chỉ DEMO; PR: **chờ lead mở**. Bắt đầu 23:53 ngày 14/11/2026, kết thúc 00:03:55 15/11/2026 (UTC+07), khoảng **0.18 giờ thực tế**, so với **3 giờ ước tính** trong phiếu. Lát qua nửa đêm; giữ ngày giao 14/11 theo handoff.
- Chép đúng năm tệp `nguon/privacy/{__init__,types,core,company_names,person_names}.py` vào gói. Giữ KnownText, chuẩn hóa/vị trí, tên dài ưu tiên, bảo vệ số, numeric_review; hỗ trợ NFC/NFD bằng bản dò có ánh xạ vị trí gốc. Đổi sang `[[...]]`, giữ mã Junsky, không cắt số thứ tự lớn. [NGUON.md](../goi/e_mask/NGUON.md) có đường nguồn, SHA byte trước/sau và SHA LF cho checkout Linux/Windows.
- Bản chép đã tách encrypt/decrypt bảng, xuất Word/TXT/ZIP và import cryptography/python-docx. Không thêm thư viện chạy ngoài SDK. Detector import khi gọi; thiếu thì từ chối, không trả kiểm giả. `suggest` chỉ gợi ý thủ công có trần 500 dòng, không dùng che tự động. Phần nguồn cũ giữ nguyên, để lead xét chuyển lưu trữ sau, không xóa/di chuyển.
- **Đã kiểm bằng Core giả (CoreGia)**: pytest **54 passed, 0 skipped**, mã 0; gồm 9 ca MASK-0 và 45 ca MASK-1. Kiểm độc lập **ĐẠT**, mã 0. Ca thuần kiểm NFC/NFD/khoảng trắng/vị trí, tên dài, giữ Junsky, số tự sinh lớn, mã số DEMO không nhầm tiền/ngày, giữ `1.000.000 VND` và `30/10/2026`, phát hiện mất/thêm/đổi số; import sạch chỉ với thư viện chuẩn không đọc tài nguyên/ghi tệp/chạy nguồn ngoài.
- Cổng vẫn giữ nguyên hai handler MASK-0, trả `LoiNghiepVu("CHUA_LAM", "Chức năng này chưa được hoàn tất.")`, không xuất văn bản hoặc cụm gốc. CLI SDK **0/2 ĐẠT, mã 1** do hai stub theo phiếu; **chưa đạt DEMO nghiệp vụ, chưa hoàn tất che/mở che, chưa kích hoạt vận hành**. numeric_review chưa thay hậu kiểm tiền/ngày độc lập ở MASK-2.
- Lệch nền checkout: lúc bắt đầu nhánh chưa chứa MASK-0. Đã khôi phục đúng 10 tệp `e_mask/` từ commit `c3e68148b5db837912a40ea39aa4539f53c3fca0` (đọc Git object vào worktree; giữ nguyên năm tệp mã/phiếu của MASK-0). Lệnh Git restore không ghi được index của worktree ngoài vùng cho phép nên dùng đọc object; không đổi index, không commit/push. Lead đồng bộ dependency trước khi mở PR để diff MASK-1 chỉ còn năm tệp lõi, test và tài liệu.
- Quyết định tạm: dùng họ tiền tố MASK đã có trong fixture cũ, chỉ cho helper DEMO; còn chờ lead xác nhận không trùng mã Junsky thật. Kho cấp mã chung/kiểm quyền thuộc MASK-3. Không có yêu cầu Core mới phát sinh; các mục Cần Core phía dưới giữ nguyên.

Ba lệnh bắt buộc đã chạy bằng `.venv/Scripts/python`, với `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chức năng này chưa được hoàn tất."
[LỖI] Mở che DEMO: "Chức năng này chưa được hoàn tất."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1 (0/2 ĐẠT, đúng giới hạn stub của MASK-1).

python -m pytest e_mask/tests -q
54 passed in 0.59s
Mã thoát: 0; 0 skipped.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát: 0.
```

## MASK-2 — 14/11/2026

- **Xong phạm vi lõi detector/hậu kiểm**, chỉ DEMO; PR: **chờ lead mở**. Bắt đầu **00:06 ngày 15/11/2026**, kết thúc **00:19:10 ngày 15/11/2026** (UTC+07), **0.22 giờ thực tế**, so với **3 giờ ước tính** trong phiếu. Giữ ngày giao 14/11 theo handoff.
- Đúng năm tệp mã chạy: chép `nguon/privacy/detectors.py`, `leftovers.py`, `che_van_ban.py`; sửa `core.py`; thêm `tai_nguyen.py`. Tận dụng toàn bộ test_che_van_ban và kho RAM DEMO chuyển vào `tests/ho_tro_kho_demo.py`, bỏ import tests/tools/Core cũ. Chỉ sửa `e_mask/`, giữ nguyên `ma-nguon/` và các bản tham chiếu; không commit/push.
- Giữ trần 500.000/500/300/20, KnownText/NFD/vị trí, nhãn nhiều dòng, hậu kiểm regex độc lập detector, Counter tiền/ngày của bản gốc đầy đủ, số bắt đầu 0/MST/tài khoản theo ngữ cảnh. Ca 501 email DEMO che đủ 501. Chuỗi bệnh lý chưa kiểm hết chặn văn bản; bí danh hỏng không che khuất dấu vết tên/tiền/ngày. numeric_review dùng NUL giữ ranh giới số, mở che giữ mã chữ thường/dấu chấm/gạch nối, không bắt mã nằm dính trong chữ khác.
- Bốn nguồn sạch chưa có: mặc định `MASK_THIEU_TAI_NGUYEN`. `nap_cau_hinh` chỉ nạp whitelist tin cậy (đường tuyệt đối ngoài gói + SHA-256), đủ bốn tệp, snapshot nguyên bộ; lỗi/thu hồi cấu hình xóa cache cũ. Không có nguồn tải, từ điển thay thế hoặc fallback vận hành. Từ vựng DEMO được mock tường minh ngoài gói, xóa cache mỗi ca. Hàm nạp là cấu hình nội bộ dành cho adapter sau; chưa mở schema cấu hình máy MASK-0 hoặc cho payload tự cấp whitelist/quyền.
- Còn sót/lỗi detector/chưa kiểm đủ/tiền-ngày thay đổi → không công bố văn bản. Mở che thêm kết quả kiểm nội bộ, không đóng yêu cầu nếu kiểm tiền/ngày thất bại; không thay mẫu 1–4 hoặc manifest. Adapter MASK-5 phải đổi kết quả chặn sang `LoiNghiepVu` mã `MASK_DINH_DANH_CHUA_DAT` hoặc `MASK_TIEN_NGAY_THAY_DOI`, câu cố định, không dùng nội dung gốc/str(lỗi). Kho/quyền chỉ là port được bên tin cậy tiêm, không tự cấp mã yêu cầu hoặc xác thực.
- **Đã kiểm bằng Core giả (CoreGia)** ở đường stub; lõi kiểm bằng fixture kho/từ vựng DEMO ngoài gói. Pytest **149 passed, 190 subtests passed, 0 skipped**, mã 0, **15,69 giây**. Bao gồm đúng/vượt trần, 501 cụm, NFD/vị trí, nhãn nhiều dòng, mất/thêm/đổi tiền-ngày, thiếu từng tài nguyên, whitelist/SHA/cache, lỗi detector, bí danh hỏng. Ba chuỗi 500.000 ký tự `1; `, `1, `, `1 ` đo **1,685 / 1,737 / 2,433 giây**; giữ ngưỡng cũ **≤5 giây xử lý, timeout tiến trình con 12 giây**. Đo trên Windows/Python 3.13.14; chưa chạy Linux thực tế, test dùng API đa nền tảng.
- CLI SDK vẫn **0/2 ĐẠT, mã 1** do hai stub `CHUA_LAM` theo phiếu. Kiểm độc lập **ĐẠT, mã 0**, không tệp biên dịch/tham chiếu bị cấm. `git diff --check` mã 0. SDK **2.0.0**, cài offline wheel `--no-index --no-deps`, SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Dùng venv riêng với công cụ pytest sẵn có qua system-site-packages, không thêm dependency chạy.
- **Giới hạn:** heuristic có thể bỏ lọt tên người viết thường không nhãn; có test ghi nhận giới hạn, không coi kết quả “không tìm thấy” là bằng chứng đủ điều kiện Cloud. Nguồn sạch/quyền/kho Core thật chưa có, cổng DEMO nghiệp vụ chưa đạt; 0 lượt Cloud và không gọi engine khác.
- Lệch phiếu: không mở rộng phạm vi; thêm kiểm tiền/ngày nội bộ khi mở để chặn dữ liệu kho bất thường. Chờ lead whitelist bốn tài nguyên. Không phát sinh yêu cầu Core mới; kênh cấu hình/ngăn/quyền đã nằm trong mục **Cần Core**.

Ba lệnh kiểm bắt buộc đã chạy bằng `.venv/Scripts/python`, với `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` (pytest thêm `-s` để ghi số đo hiệu năng):

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chức năng này chưa được hoàn tất."
[LỖI] Mở che DEMO: "Chức năng này chưa được hoàn tất."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1; 0/2 ĐẠT, đường stub theo phiếu MASK-2.

python -m pytest e_mask/tests -q -s
Hiệu năng '1; ': 1.685 giây
Hiệu năng '1, ': 1.737 giây
Hiệu năng '1 ': 2.433 giây
149 passed, 190 subtests passed in 15.69s
Mã thoát: 0; 0 skipped.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát: 0.
```

## MASK-3 — 14/11/2026

- **Xong phạm vi port/kho tạm/chống trùng**, chỉ DEMO; PR: **chờ lead mở**. Giữ ngày giao 14/11 theo handoff. Bắt đầu **00:22 ngày 15/11/2026** (UTC+07); mốc kết thúc và giờ thực tế ghi tại đoạn cuối mục này. Phiếu ước tính **5 giờ**, chưa phải số đo. **Chưa đạt điều kiện nghiệm thu chung** vì hai DEMO ở CLI SDK vẫn là stub thuộc MASK-5.
- Đúng bốn tệp mã chạy: `kho_tam.py`, `kho_dinh_danh.py`, `kho_qua_core.py`, `quyen_yeu_cau.py`. Tái dùng protocol `Kho` của MASK-2 và snapshot/nhật ký/chốt của `ma-nguon/kho_qua_core.py`; không phục hồi cổng cũ hoặc tự đặt API ngăn. `ma-nguon/`, các bản tham chiếu, SDK và Core giữ nguyên; không commit/push.
- `KhoTam` dùng `KTT_ENGINE_DU_LIEU`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\e_mask\du-lieu\` trên Windows; Linux cần đường DEMO tuyệt đối tường minh. Khóa tệp riêng bằng khóa đa tiến trình của hệ điều hành, JSON đọc/đổi/ghi trong cùng khóa; ghi tạm, flush/fsync, `os.replace` cùng thư mục. Từ chối tệp hỏng, đường trong gói/liên kết và lỗi đọc/ghi/khóa bằng `MASK_KHO_TAM_LOI`, không tự tạo kho RAM thay thế. Mã opaque cũng băm trước khi lưu; schema đóng chỉ có băm và mã trạng thái số. Không lưu tên gốc, danh mục, bảng ánh xạ, toàn văn, nội dung che hay kết quả mở che.
- Kho lâu dài và quyền là port nội bộ **chưa có transport SDK 2.0**. Mặc định thiếu kho → `MASK_KHO_CHUA_NOI`; thiếu danh tính tin cậy → `MASK_NGU_CANH_CHUA_XAC_MINH`. Không nhận danh tính từ đầu vào/tham số/pháp nhân. `NguCanhTinCay` do bên cấp quyền tiêm, gắn phiên/module/người/tài liệu/vùng; Core giả cấp mã yêu cầu/lượt ổn định theo việc/bước. Không ép mã opaque thành UUID/64 ký tự, không đưa `lan_thu` vào khóa. Mã yêu cầu mở thiếu/sai/đã đóng hoặc sai chủ bị từ chối.
- Giữ hai thao tác port cũ `snapshot_luot`, `chot_luot`; `chot_luot` với nhật ký rỗng là cửa đọc lại lượt đã chốt, vẫn kiểm quyền. Bên cấp quyền được gọi lại tại snapshot/chốt/đọc lại; port kho phải tự kiểm quyền/lease trong giao dịch. Bảng chung toàn tập đoàn, tách vùng DEMO/thật; không chia theo pháp nhân hoặc giới hạn bảng tra vào bí danh đã tham chiếu của một yêu cầu.
- Nhật ký trong RAM chỉ gửi về kho được phép. Bên kho giả chốt nguyên tử alias/hàng chờ/đếm gặp/tham chiếu/yêu cầu/kết quả, CAS xung đột → `MASK_XUNG_DOT`, `thu_lai_duoc=True`. Lượt đã chốt chỉ đọc từ port, không chạy lại callback/cấp alias/đếm mới. Kết quả đọc lại vẫn qua chặn an toàn. Tiền tố cấp bí danh MASK-3 nằm một chỗ tại `TIEN_TO_TU_SINH = 'MASK'`; chỉ DEMO, còn chờ Anh xác nhận không trùng Junsky thật. Không đổi matcher/tiền tố của lõi MASK-1…2 ngoài phạm vi lát.
- Trước chốt ghi dấu mã/băm. Bên lưu trữ đã nhận chốt mà chưa trả → lưu mã trạng thái chưa rõ, băm chốt và mã tương quan suy từ mã lượt đã băm, rồi `raise ChuaRo`. Khởi động lại/giao lại luôn hỏi snapshot port trước; nếu kho còn đang chờ thì tiếp tục `ChuaRo`, không chạy nghiệp vụ lại. Không phục hồi kết quả từ JSON. Dấu cục bộ nói đã chốt nhưng port mất trạng thái → từ chối xung đột. Mất ACK kết quả SDK do chính SDK gửi lại; không có vòng gửi cũ.
- `KhoBoNho` chuyển từ helper MASK-2 vào `tests/ho_tro_core_gia.py`, ngoài gói chạy; helper cũ chỉ chuyển tiếp import để giữ test. Fixture kho/quyền gắn phiên/module/người/tài liệu và cấp mã, không nhận cờ tự khai từ payload. Hai vùng trong test đều là dữ liệu giả; nhãn `THAT` chỉ để kiểm tách vùng, không có hồ sơ thật. Không thêm dependency chạy ngoài SDK/thư viện chuẩn.
- **Đã kiểm bằng Core giả (CoreGia)** và port kho/quyền giả: **225 passed, 190 subtests passed, 0 skipped**, mã 0, **19,91 giây**. Đủ **11/11 vector_kho_luot.json nguyên bản**; snapshot/nhật ký/bản sao; hai tiến trình tranh ghi JSON và hai tiến trình engine chốt cùng bên kho giả (một chốt, một xung đột, sau retry dùng cùng alias); rollback tại sáu mốc; gặp lại/chống đếm lặp; sai module/người/tài liệu/vùng/mã và thu hồi quyền ở từng cửa; bảng chung; `ChuaRo` sau commit hoặc nguồn còn chờ; mất 1 và cả 4 ACK kết quả SDK, giao lại cùng việc/bước và khởi tạo lại engine. Kiểm byte mọi tệp kho tạm không chứa tên/toàn văn DEMO, kể cả sau mở che.
- Chạy trên **Windows/Python 3.13.14**, chưa chạy Linux thực tế; mã/test có nhánh Windows/Linux và multiprocessing `spawn`. Các kiểm này **không phải bằng chứng bền PostgreSQL, RLS, CAS hoặc quyền Core thật**. Bốn tài nguyên sạch và kho/quyền thật vẫn chờ; 0 lượt Cloud, không gọi engine khác. Duyệt/từ chối/dọn thuộc MASK-6, handler nghiệp vụ thuộc MASK-5; chưa tự nối vào manifest.

Ba lệnh kiểm bắt buộc chạy bằng `.venv/Scripts/python`, với `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; venv cài SDK offline từ wheel đã so SHA256SUMS, phiên bản 2.0.0. Công cụ pytest dùng bản có sẵn qua system-site-packages:

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chức năng này chưa được hoàn tất."
[LỖI] Mở che DEMO: "Chức năng này chưa được hoàn tất."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1; 0/2 ĐẠT, hai stub chưa nối thuộc MASK-5.

python -m pytest e_mask/tests -q
225 passed, 190 subtests passed in 19.91s
Mã thoát: 0; 0 skipped.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát: 0.
```

Lệch phiếu / quyết định tạm: không mở rộng tập bốn tệp mã; giữ adapter tạm chỉ trong tests để kiểm port qua CoreGia, hai handler sản phẩm vẫn stub. Không tự đặt API ngăn khi SDK thiếu transport; Cần Core được cụ thể hóa bên dưới. **Thời gian thực tế:** bắt đầu 00:22, kết thúc **00:50:53 ngày 15/11/2026** (UTC+07), **0.48 giờ**, so với **5 giờ ước tính** trong phiếu.

## Nợ từ kiểm MASK-2 — ghi nhận 14/11/2026, không vá trong MASK-3

- **CAO cho Cloud:** tên người viết thường không nhãn có thể lọt hậu kiểm; test heuristic đạt không chứng minh văn bản đã hết định danh. Cần bổ sung ở lát riêng trước xét bật Cloud.
- Tên viết tắt dạng **N.V. An**: còn nợ kiểm nhận diện/hậu kiểm; không coi MASK-3 là đã xử lý.
- Khác biệt **numeric_review với NUL**: cần đối chiếu riêng với nguồn, giữ ranh giới số và chứng minh tiền/ngày; không sửa trong lát kho/quyền.

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

### Bổ sung MASK-P — 14/11/2026

- Hợp đồng API v1/SDK 2.0 đã khóa; các yêu cầu cổng lịch sử phía trên phải đối chiếu lại theo [phiếu SDK 2.0](GIAO-CODEX-e_mask.md#5-cần-core--chờ-anh-của-engine-này), không khôi phục socket/route/SQL riêng Mask.
- **Ngăn engine + CAS/ghi lô nguyên tử/duy nhất:** bảng tên gốc–bí danh, cụm chờ, yêu cầu và tham chiếu tạm là dữ liệu lâu dài. `kho_tam.py` theo quyết định tạm chỉ lưu mã/băm/số đếm, không được lưu tên gốc/toàn văn/kết quả mở che. Băm không khôi phục tên gốc; khi chưa có port ngăn thì xử lý thật phải `MASK_KHO_CHUA_NOI`, kho DEMO chỉ ở fixture ngoài gói. Cần Core chốt chuyển dữ liệu/cửa 113, 117–120 sang ngăn chung.
- **Danh tính/mã yêu cầu:** SDK hiện chỉ có `viec_id`, `buoc`, `phap_nhan_id`, thiếu module/người gửi/tài liệu đã xác minh. Core phải cấp mã ổn định và kiểm quyền khi snapshot/chốt/mở che/đọc lại/tải tệp; không nhận danh tính tự khai trong tham số/config, không lấy pháp nhân làm quyền mở che. Cần xác nhận tham chiếu tệp con trong JSON cùng việc đi qua `mo_tep`.
- **Chốt và mất ACK (J8b):** đối soát ghi kho/kết quả, giao lại không cấp/đếm/đóng trùng; lượt bền #10 khi bên lưu trữ đã nhận chốt mà chưa trả. Chưa có API ngăn/giữ-chốt-đọc thì chỉ kiểm bằng port giả; không tự khai API mới.
- Kênh cấu hình tới `Engine`, nhật ký/thẻ trạng thái, UI ngăn/màn thử chung chỉ Admin; màn duyệt/lọc kiểu Excel còn thiếu, không tự nối màn riêng cũ. Core kiểm nguồn sinh `van_ban_da_che` và chuỗi Mask → Cloud, kiểm quyền cả đọc kết quả/tệp, không chỉ tin mã loại/cờ caller. Hỏi AI bản 1 vẫn tắt Cloud.
- Tên tám contract lịch sử/`noi_dung_da_che.v1` cần lead đối chiếu cổng mới; không đổi nghĩa lượt/hạn/danh mục của bản đã công bố. Bộ kết quả mở che `truong` không tự nối vào Trích xuất đang nhận `tra_loi_ai`; cần thiết kế riêng nếu có chuỗi đó.

### Cụ thể hóa MASK-3 — 14/11/2026

- **Ngăn/transport chung:** triển khai cổng SDK đọc snapshot, CAS/duy nhất và ghi lô nguyên tử bao trùm định danh/alias mới, hàng chờ, dấu gặp theo yêu cầu, tham chiếu tạm, trạng thái yêu cầu và kết quả. Bốn tệp MASK-3 chỉ định nghĩa port nội bộ, không thêm route/thao tác ngăn công bố. Chuyển bảng lâu dài vào ngăn hạn chế quyền, không lưu tên gốc vào kho tạm.
- **Danh tính và mã ổn định:** Core cấp từ phiên đã xác minh module/người gửi/tài liệu/vùng, gắn việc/bước/lease và mã yêu cầu/lượt; cùng việc/bước giữ nguyên mã qua `lan_thu` và khởi động lại. Kiểm quyền trong cùng giao dịch tại snapshot/chốt/đọc lại, kể cả kết quả/tệp của lượt mở che đã đóng. Mã đã đóng chỉ đọc lại đúng lượt đã chốt, không mở lượt mới. `phap_nhan_id` không làm phạm vi bảng hoặc quyền mở che.
- **Chốt chưa rõ:** port phải phân biệt đã chốt, xác nhận chưa chốt/không còn chốt đang chờ, và đang chờ/chưa biết; trạng thái cuối phải `ChuaRo`. Đối soát theo mã ổn định trước khi xử lý lại, giữ dấu/băm và kết quả ở kho được phép. Bổ sung lượt bền chung #10 khi SDK có; không đổi cơ chế nộp kết quả/ACK vốn do SDK quản.
- **Chứng minh trên hệ lưu trữ thật:** cần kiểm nguyên tử/CAS/rollback/khởi động lại, độ bền và kiểm quyền trong ngăn thật trước nối vận hành. Hai tiến trình với port RAM giả và JSON khóa tệp không thay cho nghiệm thu PostgreSQL/Core thật.

## Chờ Anh / lead — MASK-P

- Chốt đề xuất bổ sung `van_ban_da_che` ở [cuối sổ loại riêng](../../_chung/docs/LOAI-DU-LIEU-RIENG.md#3-đề-xuất-mask-p-chờ-anh--chi-tiết-van_ban_da_che), Q1/Q3/Q4 theo phiếu thứ tự; không coi Q2 dành cho OCR là quyền lưu tên gốc của Mask xuống JSON.
- Cấp whitelist bốn tài nguyên detector sạch, chốt tiền tố tự sinh/tạm không trùng Junsky và đặc tả bản xuất danh mục sạch/quan hệ tên khác. Không dùng danh mục thật làm fixture; chuyển thật cần Anh xác nhận số dòng trước/sau.
- MASK-7 trình số đo DEMO, trần tệp/đầu ra, nguồn hoặc phương án cho Word giữ bố cục, sheet/chart Excel và mở che tệp còn thiếu; chỉ triển khai phần thiếu sau khi được chốt, ước lại giờ trước làm.
- Giữ việc chờ duyệt màn thử DEMO/tên contract theo cổng chung; Anh/lead chạy công cụ Windows và bài 11 bước sau khi Core đủ cửa, ca OCR chưa nối ghi “chưa kiểm”.

## Hiện vật không mang sang gói — ghi nhận MASK-P

Vỏ `ma-nguon/chay.py`, `vong_doi.py`, shim, contract bốn mẫu cũ, helper mã hóa bảng và các bản tham chiếu SQL/route/UI không dùng cho gói SDK 2.0. Giữ nguyên, không xóa/di chuyển trong MASK-P; lead xem xét chuyển `LUU-TRU/` sau khi có gói thay thế và kiểm đủ.
