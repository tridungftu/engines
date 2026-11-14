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

HD-P không thay quyết định cuối của Anh cho phiếu 9 lát/29 giờ cũ. Bản giao mới dùng `hoa_don.doc_xml@2` vì đổi phong bì nhận/trả, không tự chuyển quy trình `@1`. Không cần thêm/đổi loại dữ liệu riêng: dùng `tep` → `truong` + tệp JSON chi tiết. Các câu Q1–Q8 và điều kiện mở lát tiếp theo ở `GIAO-CODEX-e_hoa_don.md` §5.2.

Kiểm HD-P ngày 14/11/2026: regex theo đầu bài trích đủ **5/5 khối lệnh §4**, dòng mở khối là ba backtick trơn; khớp 5 mã lát HD-0…HD-4 và tổng 4 + 3 + 3 + 3 + 2 = **15 giờ ước tính**; `git diff --check` mã 0, phạm vi đúng hai tệp tài liệu. Ba lệnh kiểm engine AGENTS.md §5 **không áp dụng** theo đầu bài chỉ tài liệu. Chưa chạy kiểm chức năng engine hoặc CoreGia trong HD-P; các lệnh kiểm trong phiếu là yêu cầu của lát tương lai.

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

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
