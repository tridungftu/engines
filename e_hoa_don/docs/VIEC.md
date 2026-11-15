# VIỆC — danh sách việc duy nhất của project `e_hoa_don`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

Các dòng 0–5 giữ dấu vết phiếu cũ, không tự mở các lát mở rộng. Phần SDK 2.0 được giao trong HD-P chỉ gồm XML; điều kiện chờ Anh/Core theo phiếu giao mới.

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | Xin Anh **quyết định cuối** cho phiếu (9 lát, 29 giờ công ước tính) | — | Chờ Anh |  |
| 2 | G3-GOI-25: nguồn Node bảng kê trong gói | HD-2 | Chờ Anh | Quyền chép nguồn |
| 3 | HD-CONG-BO: mẫu ZIP/bảng kê | HD-5 | Chờ Anh |  |
| 4 | HD-NOI-PHIEN, HD-WIN: phiên Windows/Chromium thật | HD-3, 4 | Chờ Anh | Tài khoản Windows |
| 5 | HD-NOI-CORE, HD-GIAO-DIEN, HD-SO-TIEN, G3-GOI-26, HD-TONG | HD-6…10 | Chờ làm |  |
| 6 | HD-P — Lập phiếu giao Codex SDK 2.0 cho phần đọc XML đã rõ | HD-P | Xong — 14/11/2026 | `GIAO-CODEX-e_hoa_don.md`: 5 lát HD-0…HD-4, tổng 15 giờ **ước tính**, chưa triển khai; ZIP/bảng kê/tải và thử máy thật **chờ Anh chốt**. Chỉ tài liệu, không tạo `goi/`, không sửa `ma-nguon/`. PR: **chờ lead mở**. |
| 7 | HD-0 — Khung SDK 2.0 + XML DEMO thật + kiểm độc lập | HD-0 | Xong — 14/11/2026 (mốc giao việc) | Kiểm thực tế 15/11/2026: SDK 1/1 DEMO ĐẠT, pytest 63 passed/0 skipped, kiểm độc lập mã 0; đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật. PR: **chờ lead mở**. |
| 8 | HD-1 — XML strict, tiền và vấn đề nguồn | HD-1 | Xong — 15/11/2026 | SDK 1/1 DEMO ĐẠT; pytest 157 passed, 0 skipped; kiểm độc lập mã 0. Đã kiểm bằng Core giả (CoreGia). Lead Claude duyệt doc.py + chay.py; trần 1.000 HHDVu chặn trước DTO/JSON. PR: **chờ lead mở**; xem mục Bàn giao HD-1. |
| 9 | HD-2 — Bàn giao tệp, hủy, mất lease và gửi lại qua SDK | HD-2 | Xong — 14/11/2026 (mốc giao việc) | Kiểm thực tế 15/11/2026: SDK 1/1 DEMO ĐẠT; pytest 259 passed, 0 skipped; kiểm độc lập mã 0. Đã kiểm bằng Core giả (CoreGia) và MayChuGia loopback. PR: **chờ lead mở**; xem Bàn giao HD-2 và `PR-HD-2.md`. |
| 10 | HD-3 — Bộ XML DEMO có đáp án và regression | HD-3 | Xong — 14/11/2026 (mốc giao việc) | Kiểm thực tế 15/11/2026: SDK 3/3 DEMO ĐẠT; pytest 283 passed, 0 skipped; kiểm độc lập mã 0. Đã kiểm bằng Core giả (CoreGia); 0 tệp runtime sửa. PR: **chờ lead mở**; xem Bàn giao HD-3 và `PR-HD-3.md`. |
| 11 | HD-4 — Ghim nguồn và cài sạch XML | HD-4 | Đang làm — 15/11/2026 (sửa CI Linux) | Mốc đầu: Windows đạt, 284 test. Lượt sửa: SDK 3/3 ĐẠT; pytest 298 passed, 0 skipped; kiểm độc lập và cài sạch Windows đạt. Đã kiểm bằng Core giả (CoreGia); chờ CI Linux/Python 3.11 xác nhận, Core thật chưa kiểm. PR: **chờ lead cập nhật mã**. |

HD-P không thay quyết định cuối của Anh cho phiếu 9 lát/29 giờ cũ. Bản giao mới dùng `hoa_don.doc_xml@2` vì đổi phong bì nhận/trả, không tự chuyển quy trình `@1`. Không cần thêm/đổi loại dữ liệu riêng: dùng `tep` → `truong` + tệp JSON chi tiết. Các câu Q1–Q8 và điều kiện mở lát tiếp theo ở `GIAO-CODEX-e_hoa_don.md` §5.2.

Kiểm HD-P ngày 14/11/2026: regex theo đầu bài trích đủ **5/5 khối lệnh §4**, dòng mở khối là ba backtick trơn; khớp 5 mã lát HD-0…HD-4 và tổng 4 + 3 + 3 + 3 + 2 = **15 giờ ước tính**; `git diff --check` mã 0, phạm vi đúng hai tệp tài liệu. Ba lệnh kiểm engine AGENTS.md §5 **không áp dụng** theo đầu bài chỉ tài liệu. Chưa chạy kiểm chức năng engine hoặc CoreGia trong HD-P; các lệnh kiểm trong phiếu là yêu cầu của lát tương lai.

## Cần Core (chuyển lead Core qua Anh)
- HD-4: SDK cần hook nhật ký công khai, không in traceback ra stderr; fail-closed khi thiếu `_ghi` là giải pháp tạm.
- HD-4 phần cũ không dùng: `ma-nguon/chay.py`, `tai.py`, `phien.py`, `bang_ke.cjs`, `portal.cjs`, `vendor/`, Node lock, contract cũ, shim và test tham chiếu; giữ nguyên, chưa xóa hoặc chuyển `LUU-TRU/`. Cần Core context tin cậy, quyền tệp và lead/Core chuyển `@1` → `@2` giữ bản cũ. ZIP/bảng kê/tải chờ Anh; nếu mở tải cần phiếu riêng.
- HD-4 kiểm Windows/Python 3.13.14: SDK 3/3 DEMO, pytest 284 passed/0 skipped, kiểm độc lập và cài sạch Windows đạt, các mã thoát 0; đã kiểm bằng Core giả (CoreGia). Chưa kiểm Linux/Core thật. Venv chính dùng pytest có sẵn; venv cài sạch chỉ cài wheel SDK offline. Thời gian thực tế khoảng 0,12 giờ (02:22–02:29, 15/11/2026 UTC+07), phiếu 2 giờ ước tính; PR: chờ lead mở.
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

### Sửa HD-4 — CI Linux/Python 3.11, 15/11/2026

Kết luận: **Đạt các kiểm tra tại Windows/Python 3.13.14; chờ CI xác nhận Linux/Python 3.11.18**. Đã kiểm bằng Core giả (CoreGia). Nhánh `codex/e_hoa_don-hd-4`; mã PR chưa được cung cấp, chờ lead cập nhật; không git add/commit/push.

Nguyên nhân: `Lib/copy.py` của CPython 3.11.18 dò tùy chọn `org.python.core.PyStringMap` cho Jython, bắt `ImportError` khi không có. Audit hook của kiểm độc lập lại ném `RuntimeError` cho import ngoài allowlist, làm phép dò này trở thành lỗi chí mạng. CPython 3.13 đã bỏ nhánh dò Jython nên Windows 3.13 không gặp. Đối chiếu nguồn chính thức: <https://github.com/python/cpython/blob/v3.11.18/Lib/copy.py>. Chạy nguyên mã copy.py 3.11.18 trong tiến trình `-I -B -S` trên Python 3.13: hook cũ mã 1/RuntimeError; hook mới mã 0 và đủ DEMO. Đây là tái hiện nhánh stdlib, **không phải bằng chứng đã chạy Linux hoặc interpreter 3.11**. Cú pháp cả năm tệp runtime đã qua AST với `feature_version=(3, 11)`; không cần sửa cú pháp, đường dẫn hoặc shell.

Đã làm: chỉ đổi bộ kiểm ngoài gói để từ chối import bằng `ModuleNotFoundError` (thuộc `ImportError`); giữ nguyên allowlist, audit chặn mạng/tiến trình, nạp SDK theo tệp cụ thể, `-I -B -S`, không thêm site-packages/Core/shim hoặc nạp trước copy để né kiểm. Khi tiến trình lỗi, chỉ in mã thoát và tên ngoại lệ trong danh sách cố định; lỗi lạ/thiếu xác nhận/không khởi chạy/quá hạn có mã cố định, không phản chiếu stdout/stderr hay traceback. Thêm 14 ca hồi quy: dò Jython, từ chối org/Core/thư viện chưa ghim dù tệp hiện hữu, chặn bốn sự kiện mạng/tiến trình, chẩn đoán an toàn và lỗi khởi chạy/quá hạn. **0 tệp runtime thay đổi**, không đổi API/SDK/phụ thuộc/CI/kịch bản shell.

Kết quả thật, `PYTHONDONTWRITEBYTECODE=1` và `-B`, SDK 2.0.0:

| Lệnh | Kết quả | Mã thoát |
|---|---|---:|
| `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` | 3/3 DEMO [ĐẠT] | 0 |
| `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q -p no:cacheprovider` | 298 passed in 39.46s, 0 skipped | 0 |
| `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` | [ĐẠT] AST/import/cây gói/tiến trình sạch | 0 |
| `e_hoa_don\tests\KIEM-MAY-SACH.cmd` | Cài SDK offline trong venv mới, gói sao chép riêng; 3/3 DEMO và kiểm độc lập [ĐẠT] | 0 |

Không tìm thấy interpreter Python 3.11/launcher `py`; WSL chưa cài, không có Docker trên PATH. Chưa chạy `sh e_hoa_don/tests/kiem_may_sach.sh` bằng Linux thật hoặc chạy lại CI từ bản sửa chưa commit. Không thay đổi hệ thống Windows để bổ sung môi trường.

Thời gian thực tế: không ghi nhận mốc bắt đầu nên không báo giờ đo giả; pytest 39.46 giây, cài sạch Windows khoảng 6.60 giây. Phiếu HD-4: **2 giờ ước tính** (không có ước tính riêng lượt sửa).

Lệch khỏi phiếu / quyết định tạm: không mở rộng nghiệp vụ; chỉ sửa công cụ kiểm và bổ sung bằng chứng. Cần Core / Chờ Anh mới phát sinh: **không có**; giữ nợ context/quyền tệp/hook nhật ký cũ. Linux/Python 3.11 còn chờ CI xác nhận.

### Bổ sung HD-P — 14/11/2026

- Các dòng cổng ở trên là yêu cầu lịch sử; API v1/SDK 2.0.0 đã khóa theo bộ gửi engine hiện tại. Việc nối/vận hành Core thật chưa được kiểm trong HD-P. Không lấy mô tả socket/SDK cũ làm hợp đồng triển khai mới.
- Cấu hình máy: SDK đợt 1 chưa đưa `cau_hinh` cho engine; dùng lớp JSON ngoài gói theo `GIAO-CODEX-THU-TU.md` §2. XML thuần không cần cấu hình, không bị chặn vì thiếu tệp.
- Context nguồn/profile/company/raw binding: cần cửa chung do Core kiểm quyền theo pháp nhân; SDK hiện chỉ có `viec_id`, `buoc`, `phap_nhan_id`. Đợt XML truyền `context=None`, giữ lý do ứng viên và `can_kiem_tra=true`, không giả định danh/semantic digest hoặc đọc company từ cấu hình máy.
- Kho tệp và chuyển bản: SDK không cam kết `tep_id` là UUID. Gói XML dùng tham chiếu SDK; lead/Core giữ bản/quy trình `@1`, chuyển sang `@2` bằng khai báo khi được giao. Cần kiểm quyền tệp đầu vào/ra và lưu theo pháp nhân trên Core thật; CoreGia không thay bằng chứng này.
- Bí mật theo tên, ngăn engine/CAS, lượt bền #10 và trạng thái chờ nhập: chỉ chặn phần tải sau khi Anh chốt; không cần cho XML thuần. Không tự dựng pipe bí mật/socket/SQL để bù SDK, không lưu nội dung XML/cookie/profile vào sổ JSON tạm.
- Test cũ tham chiếu corpus/golden XML không nằm trong bộ mã nguồn hiện tại: cần lead bàn giao fixture DEMO có hash nếu yêu cầu chứng minh tương thích toàn bộ corpus. Đợt XML tự dựng DEMO có đáp án độc lập, không tuyên bố đã chạy golden cũ khi thiếu dữ liệu.

### Bổ sung HD-2 — 14/11/2026, kiểm thực tế 15/11/2026

- **SDK cần hook nhật ký an toàn công khai:** test canary chứng minh `Engine._lam` của wheel 2.0.0 ghi traceback, đường dẫn và nội dung exception qua `_ghi`. Lớp bọc tạm `CongHoaDon(Engine)` trong `chay.py` chỉ thay câu ghi thành mã cố định `HD_SDK_THONG_BAO`, không đổi luồng lỗi/hủy/lease hoặc sửa SDK. Lỗi invariant vẫn thành `ENGINE_LOI_XU_LY` do SDK. Đây là phụ thuộc vào phương thức nội bộ `_ghi` của bản SDK đã ghim; thay lớp bọc khi SDK có hook chính thức, không khôi phục in traceback nguyên văn.
- **SDK cần seam test công khai để mất lease/giao lại:** CoreGia 2.0.0 có `huy`/`gay_mat_xac_nhan` nhưng chưa có thao tác công khai giả lập 409/404/410, hết lease hoặc xếp lại cùng việc. Test dùng monkeypatch các phương thức CoreGia, riêng giao lại dùng `_lock`/`_viec`/`_hang`; chờ cờ `_huy` để đồng bộ ca gia hạn thật của SDK, không sửa bản cài SDK hoặc tạo server thay MayChuGia. Đề nghị SDK cung cấp seam lỗi/giao lại công khai; không chặn kiểm HD-2 hiện tại.
- Hủy ở mốc sau upload có một JSON đã lưu nhưng **không nộp kết quả**; vòng đời/dọn tệp không còn được kết quả tham chiếu thuộc Core. Chưa kiểm cơ chế dọn tệp và quyền kho tệp trên Core thật. Kiểm hai pháp nhân chỉ chứng minh handler đọc riêng, không cache/dedupe hay nhận nghiệp vụ, không chứng minh quyền truy cập chéo pháp nhân của kho thật.

### Bàn giao HD-0 — mốc 14/11/2026, kiểm thực tế 15/11/2026

Kết luận: Đạt phạm vi HD-0 XML bằng Core giả (CoreGia), chưa nghiệm thu Core thật. Đúng 5 tệp runtime trong `goi/e_hoa_don/e_hoa_don/`; 18 trường SDK, một DEMO qua bộ đọc strict thật, cấu hình JSON ngoài gói và hai schema, README/CHANGELOG/NGUON/lock. Không sửa `ma-nguon/`, Core, SDK hay tài liệu API; không commit/push. PR: **chờ lead mở**; tiêu đề đề nghị `[e_hoa_don] HD-0 — Khung SDK 2.0 và XML DEMO`.

Kết quả thật trên Windows, Python 3.13.14 + SDK 2.0.0; ba lệnh đều dùng `-B`:

| Lệnh | Kết quả | Mã thoát |
|---|---|---:|
| `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` | 1/1 DEMO [ĐẠT] | 0 |
| `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q` | 63 passed in 0.82s, 0 skipped | 0 |
| `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` | [ĐẠT] AST/lazy/dynamic, cây gói, import/DEMO trong tiến trình sạch | 0 |

QA thêm: schema Draft 2020-12 khớp báo cáo thật; wheel SDK đúng SHA phát hành. Không đọc cấu hình máy thật, mọi test cấu hình ở thư mục DEMO tạm; chặn network trong test. Pytest 9.1.1 dùng bản có sẵn, chép offline vào venv. Chưa chạy Linux, bài máy sạch HD-4, Core thật/quyền tệp theo pháp nhân hay corpus/golden cũ.

Thời gian thực tế: 0.243 giờ (00:55:00–01:09:33, 15/11/2026, UTC+07; ước tính trong phiếu: 4 giờ).

Lệch khỏi phiếu: không mở rộng phạm vi nghiệp vụ. Báo cáo thêm `van_de_phep_chieu` để giữ mã/locator vấn đề khi chiếu đầu hóa đơn/tiền, `chi_tiet_nguon` vẫn đúng `ra_json(InvoiceReadResult)`. Dùng quyết định tạm đã giao: JSON cấu hình ngoài gói; handler `context=None`, `can_kiem_tra=true`, định danh/semantic digest null; trần báo cáo 32 MiB là giới hạn đề xuất chưa đo trên corpus lớn.

Cần Core / Chờ Anh mới phát sinh: không có. Giữ các mục HD-P: context tin cậy, quyền tệp vào/ra và kênh cấu hình máy. Chưa nghiệm thu Core thật. ZIP/bảng kê/tải và chuyển quy trình `@1` không thuộc HD-0; không tự mở các lát đó.

Phần cũ không đưa vào gói để lead xét `LUU-TRU/` sau: vỏ `ma-nguon/chay.py` socket/SDKEngine/Bootstrap, vòng UUID/cấp tham chiếu và contract `.v1` cũ, bridge/shim/Core cũ; `tai.py`, `phien.py`, Node/portal/bảng kê/vendor chỉ tham chiếu cho phạm vi đang chờ. **Giữ nguyên toàn bộ tệp cũ, chưa chuyển hoặc xóa**.

### Bàn giao HD-1 — 15/11/2026

Kết luận: **Đạt phạm vi HD-1 — đã kiểm bằng Core giả (CoreGia)**, chưa nghiệm thu Core thật. PR: **chờ lead mở**; tiêu đề `[e_hoa_don] HD-1 — XML strict, tiền và vấn đề nguồn`. Không git add/commit/push.

Đã làm:

- Giữ phần HD-1 trước: `doc.py` phân biệt XML hỏng với encoding/DOCTYPE/namespace/path ngoài profile bằng câu lỗi cố định; kiểm UTF-8 và trần bytes; không bắt tràn DataError. Nhiều TToan không chiếu scalar tiền mơ hồ. Giữ chuỗi định danh, Decimal exact, ABSENT/EMPTY/TEXT, mọi occurrence, money/relations/thuế và issue ngoài semantic envelope V1.
- `chay.py` trả đúng `HD_XML_QUA_LON` và `HD_KET_QUA_QUA_LON` theo phiếu. Chỉ ánh xạ `LoiDuongTruyen(VUOT_GIOI_HAN_KICH_THUOC)` hoặc `LoiNghiepVu(VUOT_GIOI_HAN)` trong khối mở/đọc tệp; mã khác, hủy, mất lease và lỗi invariant giữ nguyên. Vẫn đọc tối đa 16 MiB + 1, kiểm JSON 32 MiB trước upload.
- Trả nợ HD-0: trần vận hành **1.000 HHDVu/XML**. Mỗi dòng khuếch đại thành nhiều DTO/occurrence/locator; ca 200.000 dòng mất 66 giây do lead báo là căn cứ chọn trần bảo thủ cho DEMO, chưa có corpus thật để hiệu chỉnh. Đây không phải giới hạn pháp lý. XML parser tiền kiểm không dựng cây, đếm mọi phần tử HHDVu không namespace, dừng ngay ở dòng 1.001 **trước parser lõi/DTO/phép chiếu/JSON**, bằng `LoiNghiepVu("HD_QUA_NHIEU_DONG_HANG", "Tệp XML vượt giới hạn 1.000 dòng hàng hóa. Anh hãy gửi tệp ít dòng hơn.")`. Đếm cả dòng rỗng/trùng STT/mã hàng; không đếm comment/CDATA, không cắt ngầm. Trần JSON 32 MiB vẫn cần vì ít dòng nhưng nhiều occurrence/nội dung dài vẫn có thể vượt. README gói ghi giá trị và lý do.
- Thêm 20 test DEMO lượt bổ sung, tổng 157 test: năm ca đỏ cũ đã xanh; kiểm ánh xạ lỗi mở/đọc hẹp, giữ lỗi khác/hủy/mất lease/invariant, biên đúng 16 MiB và trần JSON, đúng 1.000 dòng giữ đủ thứ tự/occurrence, 1.001/200.000 dòng bị chặn trước parser lõi/JSON và không upload, comment/CDATA không bị đếm nhầm. Ca 400.000 occurrence SHDon vẫn kiểm thật JSON >32 MiB, không cắt occurrence. Không skip/xfail hoặc sinh expected từ parser.

Kết quả thật trên Windows, Python 3.13.14, SDK 2.0.0. Cả ba lệnh đặt `PYTHONDONTWRITEBYTECODE=1`:

```text
.venv\Scripts\python -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
→ 1/1 DEMO [ĐẠT], mã thoát 0
.venv\Scripts\python -m pytest e_hoa_don/tests -q -p no:cacheprovider
→ 157 passed in 5.57s; 0 skipped; mã thoát 0
.venv\Scripts\python e_hoa_don/tests/kiem_doc_lap.py
→ [ĐẠT] AST/import, cây gói và tiến trình sạch; mã thoát 0
```

Đo bổ sung một lần: XML DEMO 200.000 HHDVu rỗng, 1.600.597 bytes, `doc_xml` từ chối bằng `HD_QUA_NHIEU_DONG_HANG` sau **0.014118 giây**. Chỉ đo lượt gọi hàm thuần trên máy hiện tại, không gồm tạo fixture/I/O Core; không cam kết hiệu năng hoặc so trực tiếp với ca 66 giây khi chưa xác nhận cùng fixture.

Thời gian thực tế: lượt bổ sung khoảng **0.2 giờ**; cộng mốc trước **0.17 giờ**, tổng HD-1 khoảng **0.37 giờ** (ước tính trong phiếu: **3 giờ**); không tính chờ giữa lượt.

Lệch khỏi phiếu / quyết định đã dùng: **lead Claude**, theo phản hồi chuyển trong đầu bài, cho sửa `chay.py` cùng `doc.py`; đây là quyết định của lead, không phải của Anh. Chỉ hai tệp runtime thay đổi, trong trần ≤5; giữ nguyên parser `hoa_don_xml.py`. Thêm trần dòng theo đầu bài bổ sung. Giữ handler `context=None`, `can_kiem_tra=true`, identity/digest null; không ChuaRo cho thiếu context; không mở ZIP/bảng kê/portal/Cloud hoặc đổi API/SDK/Core/ma-nguon.

Cần Core / Chờ Anh mới phát sinh: **không có**. Giữ nợ SDK phát hiện lượt trước: CoreGia chặn bytes khi mở tệp bằng 413 `VUOT_GIOI_HAN_KICH_THUOC`; SDK 2.0.0 ánh xạ thành `KHONG_TRAO_DOI_DUOC_CORE`. Lớp bọc hẹp đã đáp ứng HD-1; đề nghị SDK có ánh xạ chung lỗi tải tệp vượt trần, không chặn bàn giao HD-1. Giữ các mục context tin cậy/quyền tệp/kênh cấu hình đã có. Chưa chạy Linux, máy sạch HD-4 hoặc Core thật.

Nội dung bản nháp PR lượt trước chuyển nguyên vào lịch sử dưới đây. Giữ tệp `PR-HD-1.md`, cập nhật theo kết quả cuối để lead dùng; không xóa tệp.

<details>
<summary>Bản nháp PR-HD-1 trước phản hồi của lead — lịch sử, đã được bàn giao trên thay thế</summary>

````markdown
# [e_hoa_don] HD-1 — XML strict, tiền và vấn đề nguồn

**Bản nháp bàn giao, chưa đủ điều kiện mở PR đạt; PR: chờ lead mở.** Không commit/push.

Kết luận: **Chưa đạt** — phép chiếu/lỗi nguồn đã sửa, còn hợp đồng lỗi vượt trần tại `chay.py` ngoài phạm vi tệp đã giao. Đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật.

Đã làm: chỉ sửa runtime `doc.py`; giữ nguyên parser `hoa_don_xml.py`. Tách lỗi XML hỏng và ngoài profile, không phản chiếu nguồn, không bắt tràn DataError; nhiều TToan không còn chiếu scalar tiền mơ hồ. Giữ chuỗi định danh, Decimal exact, ABSENT/EMPTY/TEXT, occurrence, issue ngoài envelope V1, chi tiết tiền/thuế/quan hệ và handler context=None. Thêm 74 test DEMO với đáp án literal, cập nhật ca hợp đồng lỗi của HD-0.

Kết quả kiểm thực tế trên Windows, Python 3.13.14, SDK 2.0.0 cài wheel offline đúng SHA; ba lệnh dùng `-B`:

```text
.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
→ 1/1 DEMO [ĐẠT], mã thoát 0
.venv\Scripts\python -B -m pytest e_hoa_don/tests -q
→ 5 failed, 132 passed in 4.01s; 0 skipped; mã thoát 1
.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py
→ [ĐẠT] AST/import, cây gói và tiến trình sạch; mã thoát 0
```

Năm test thất bại:

- `test_bytes_thuc_vuot_tran_core_metadata_nho`: CoreGia phát 413 `VUOT_GIOI_HAN_KICH_THUOC`, SDK trả `KHONG_TRAO_DOI_DUOC_CORE`; cần bọc riêng lỗi kích thước khi mở tệp.
- `test_gioi_han_read_16_mib_cong_1` và `test_vuot_16_mib_kiem_bytes_thuc_metadata_khai_thieu`: handler vẫn phát `HD_XML_VUOT_GIOI_HAN` thay `HD_XML_QUA_LON`.
- `test_bao_cao_thuc_vuot_32_mib_khong_upload` và `test_json_vuot_tran_tu_choi_truoc_upload`: handler vẫn phát `HD_JSON_VUOT_GIOI_HAN` thay `HD_KET_QUA_QUA_LON`.

Ca báo cáo quá trần sinh 400.000 occurrence SHDon trong RAM (XML <10 MiB, JSON >32 MiB); engine từ chối trước upload, nhưng mã/câu lỗi đang là bản HD-0. Ca luồng thực xác nhận `read(16 MiB + 1)`; không cắt occurrence hoặc làm xanh test bằng skip/xfail. Các test thuần kiểm context DEMO đầy đủ và mâu thuẫn không đưa context vào handler/manifest.

## Thay đổi cụ thể đề nghị cho `chay.py` (chưa áp dụng)

Vẫn chỉ hai tệp runtime tổng cộng: `doc.py` và `chay.py`; không sửa `hoa_don_xml.py`.

1. Đổi lỗi sau `read(MAX_XML_BYTES + 1)` thành `LoiNghiepVu("HD_XML_QUA_LON", "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn.")`.
2. Riêng khối `viec.mo_tep`/đọc bytes: bọc `LoiDuongTruyen` có mã chính xác `VUOT_GIOI_HAN_KICH_THUOC` hoặc `LoiNghiepVu` có mã `VUOT_GIOI_HAN` thành lỗi trên; các mã khác `raise` nguyên trạng. Không bắt hủy, mất lease, DataError hoặc exception tổng quát.
3. Đổi lỗi sau kiểm `len(bao_cao) > JSON_TOI_DA_BYTE` thành `LoiNghiepVu("HD_KET_QUA_QUA_LON", "Kết quả đọc hóa đơn vượt giới hạn. Anh hãy chia nhỏ dữ liệu đầu vào.")`. Giữ vị trí trước upload, không đổi trần 32 MiB.
4. Bổ sung test lỗi mở tệp khác không bị đổi mã, kiểm biên trần và chạy lại toàn bộ ba lệnh. Chỉ đổi trạng thái HD-1 khi không còn lỗi.

Lệch khỏi phiếu / quyết định tạm: chưa mở rộng tệp khi chưa có xác nhận. Giữ context=None, không ChuaRo cho thiếu context, không ZIP/bảng kê/portal/Cloud. Giữ phạm vi XML DEMO, không sửa ma-nguon/SDK/Core.

Thời gian thực tế đến mốc chờ xác nhận: khoảng **0.17 giờ** (01:11–01:21, 15/11/2026, UTC+07); ước tính trong phiếu: **3 giờ**. Đây chưa phải báo cáo hoàn tất lát.

Cần Core / Chờ Anh mới phát sinh: cần chốt cặp tệp runtime `doc.py` + `chay.py`; ghi nợ SDK ánh xạ lỗi kích thước tải tệp 413 thành lỗi giới hạn chung. Không cần API/ngữ cảnh mới để hoàn tất HD-1. Chưa chạy Linux, máy sạch HD-4 hoặc Core thật.

````

</details>

### Bàn giao HD-2 — mốc 14/11/2026, kiểm thực tế 15/11/2026

Kết luận: **Đạt phạm vi HD-2 — đã kiểm bằng Core giả (CoreGia)** và MayChuGia loopback. PR: **chờ lead mở**; bản nháp đầy đủ tại `PR-HD-2.md`, tiêu đề `[e_hoa_don] HD-2 — Bàn giao tệp, hủy và gửi lại qua SDK`. Chưa nghiệm thu quyền kho tệp hoặc Core thật; không commit/push.

Đã làm: chỉ sửa runtime `chay.py` (1/2 tệp được phép), giữ nguyên `doc.py`/parser và phép chiếu HD-1. Kiểm hủy/tiến độ ở bốn mốc bằng câu cố định; mở theo `tep_id`, giữ nguyên `tep_xml`, bàn giao JSON qua Core trước khi trả đủ 18 trường. Không thêm kho tạm/cache/dedupe, ID, vòng retry/heartbeat, HTTP server hoặc ghi nhận nghiệp vụ. Lớp bọc nhật ký SDK chỉ in mã `HD_SDK_THONG_BAO`, giữ xử lý hủy/mất lease/lỗi invariant của SDK. Context vẫn `None`, kết quả cần kiểm tra, identity/digest null.

Kiểm thực tế trên Windows, Python 3.13.14, SDK wheel 2.0.0 cài offline đúng SHA; pytest 9.1.1 chép offline vào venv. Cả ba lệnh dùng `-B`:

| Lệnh | Kết quả | Mã thoát |
|---|---|---:|
| `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` | 1/1 DEMO [ĐẠT] | 0 |
| `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q` | **259 passed in 37.53s, 0 skipped** | 0 |
| `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` | [ĐẠT] AST/import, cây gói và tiến trình sạch | 0 |

Thêm 102 ca HD-2: đường bộ nhớ + HTTP loopback kiểm bytes/hash/ID opaque; tên tệp chỉ metadata; upload lỗi/thiếu tham chiếu không XONG; mất 1 hoặc 3 ACK ở `tep`/`ket_qua`/`ket_thuc` giữ cùng Idempotency-Key và đúng một lần ghi mỗi thao tác; hủy bốn mốc; mất lease 409/404/410 tại đọc/tiến độ/upload và luồng gia hạn SDK; giao lại cùng việc không ghi nhận; hai pháp nhân DEMO cùng XML xử lý riêng; canary không vào stderr/lỗi/tiến độ. Hai ca tiến trình kiểm `app.chay` và module entry point nhận một dòng JSON stdin qua MayChuGia, stdin vẫn mở khi việc đã bàn giao. Hủy sau upload không nộp kết quả, tệp đã upload vẫn thuộc kho Core giả.

Thời gian thực tế: **0.195 giờ** (01:55:00–02:06:41, 15/11/2026, UTC+07) (ước tính trong phiếu: **3 giờ**).

Lệch khỏi phiếu / quyết định tạm: chỉ lớp bọc nhật ký `_ghi` và seam test CoreGia nội bộ được mô tả tại mục Cần Core; không sửa SDK/Core/ma-nguon hoặc hợp đồng đã khóa, không thay phiên bản gói. Test double HD-1 thêm `kiem_huy`; fixture test chỉ cho kết nối đúng cổng MayChuGia đã đăng ký. Không có skip/xfail. Chưa chạy Linux, máy sạch HD-4 hoặc bài Core thật 120 phút.

Cần Core / Chờ Anh mới phát sinh: hook nhật ký an toàn công khai và seam lease/giao lại cho SDK; quyền kho tệp/thu hồi tệp đã upload chưa kiểm trên Core thật. Không cần Anh chốt thêm để bàn giao HD-2; phần mở rộng ZIP/bảng kê/tải giữ nguyên trạng thái chờ.


### Bàn giao HD-3 — mốc 14/11/2026, kiểm thực tế 15/11/2026

Kết luận: **Đạt phạm vi HD-3 — đã kiểm bằng Core giả (CoreGia)**. PR: **chờ lead mở**; bản nháp `PR-HD-3.md`, tiêu đề `[e_hoa_don] HD-3 — Bộ XML DEMO có đáp án và regression`. Chưa nghiệm thu Core thật; không commit/push.

Đã làm:

- `engine.json` có đúng ba DEMO dương tính trong `demo/`: số 0000123/ngày 2026-10-30, 1000000 VND + 100000 VND = 1100000 VND; tiền lẻ 1000000.123456 VND + 100000.012345 VND = 1100000.135801 VND; mẫu thiếu KHHDon, MST mua rỗng và thiếu TgTTTBSo để kiểm null/ABSENT/EMPTY/cảnh báo/HOLD. Không thêm Ten ngoài allowlist; Công ty DEMO Ánh Dương là nhãn mô tả fixture. TToan ngoài semantic envelope V1 vẫn giữ issue, không nâng thành đầy đủ.
- Ba bản fixture độc lập ở `tests/demo/`, đáp án literal `dap-an.json` viết từ XML, pin SHA-256/số bytes `bam-fixture.json` tính độc lập với parser. `.gitattributes` giữ bytes XML UTF-8/LF trên Windows/Linux; chuẩn hóa bản checkout Windows về LF đã ghim của fixture tiền nguyên. Không nhận đã kiểm hash golden/overlay cũ khi thiếu bytes gốc. `tests/demo/README.md` đối chiếu ý đồ bốn test tham chiếu; không sửa/chạy nguyên trạng namespace Core hoặc thêm shim.
- Thêm **24 ca HD-3**: kiểm đủ 18 trường, từng header/dòng/occurrence/locator, bytes/hash và JSON qua CoreGia.doc_tep, Decimal trong context precision=2, tiền/thuế, context thiếu và identity/digest null; MIME sai chặn trước parser; lỗi cấu trúc đúng lớp LoiNghiepVu/mã/câu HD-1; DTO bất biến/snapshot bytes và Issue SDK. Hai ca XML 1.000/1.001 dòng sinh trong tmp_path/DEMO: 1.000 giữ đủ thứ tự/nguồn, 1.001 từ chối không upload/nộp kết quả. Ca thiếu TToan không tính tổng từ dòng.
- Chạy tiếp toàn bộ regression HD-0…HD-2: tiền/ngày sai, trùng/rỗng/thiếu/mixed, tiền vượt miền, tổng lệch, currency thiếu, bytes/JSON vượt trần, hủy, upload/retry/mất lease, canary. Không skip/xfail hoặc cắt dữ liệu. **0 tệp runtime thay đổi** (trần 2); không mở ZIP/bảng kê/tải/Cloud/Node. Cập nhật hiện trạng và README để phân biệt lịch sử @1 với gói @2, giữ HD-4 chờ làm.

Kết quả thật trên Windows, Python 3.13.14, SDK 2.0.0; wheel cài offline --no-index --no-deps và SHA-256 khớp SHA256SUMS.txt. Pytest 9.1.1 cùng phụ thuộc kiểm thử có sẵn được chép offline vào venv; không thêm dependency runtime.

| Lệnh | Kết quả | Mã thoát |
|---|---|---:|
| `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` | **3/3 DEMO [ĐẠT]** | 0 |
| `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q` | **283 passed in 38.65s, 0 skipped** | 0 |
| `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` | **[ĐẠT] AST/import, cây gói và tiến trình sạch** | 0 |

Thời gian thực tế: **0.208 giờ** (02:08:00–02:20:27, 15/11/2026, UTC+07); ước tính trong phiếu **3 giờ**. Mốc giờ bắt đầu theo lead.

Lệch khỏi phiếu / quyết định tạm đã dùng: **không mở rộng phạm vi**, giữ context=None, tiền exact, identity/digest null, trạng thái thuế UNKNOWN/ghi nhận NOT_PERFORMED. Oracle lượt đầu được sửa sau đối chiếu định nghĩa lõi: TToan có TOTAL_SECTION_UNSUPPORTED (không thêm UNSUPPORTED_ELEMENT), quan hệ không có là ABSENT; không sửa runtime hoặc thêm cảnh báo để né lỗi cấu trúc. Pin chỉ xác nhận ba fixture mới có bytes hiện hữu, không chứng minh tương thích corpus/golden cũ.

Cần Core / Chờ Anh mới phát sinh: **không có**. Giữ nợ context tin cậy, quyền tệp theo pháp nhân, hook log/seam lease SDK và corpus cũ tại mục Cần Core. XML **đã kiểm bằng Core giả (CoreGia)**; ZIP/bảng kê/tải và quyền/Core thật còn chờ Anh/Core theo phiếu; HD-4 ghim nguồn/cài sạch chưa làm. Chưa chạy Linux, máy sạch HD-4 hoặc bài Core thật 120 phút. Không dùng tài khoản/cổng thuế thật.
