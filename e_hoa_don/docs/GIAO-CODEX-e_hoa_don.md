# Giao Codex — `e_hoa_don` (Đọc XML hóa đơn) theo SDK 2.0

*Lập 14/11/2026, lát HD-P. Căn cứ: `AGENTS.md`, `CLAUDE.md`, toàn bộ ba tệp trong `e_hoa_don/docs/` trước HD-P, mã `ma-nguon/`, `API-ENGINE-v1.md`, SDK 2.0.0, `_chung/docs/GIAO-CODEX-THU-TU.md`, `_chung/docs/LOAI-DU-LIEU-RIENG.md`; cấu trúc theo phiếu giao `e_hoi_ai` và `e_ocr`.*

**Cập nhật HD-P2 — 15/11/2026:** Anh chốt XML là mốc 1; mở ZIP + bảng kê Excel; PDF và tải cổng thuế để sau (`QUYET-DINH-ANH-20261115.md` câu 6). Q1–Q3 tại §5.2 đã chốt. Bổ sung HD-5…HD-8; HD-P2 chỉ lập tài liệu, không kích hoạt năng lực mới. Các số giờ triển khai dưới đây là **ƯỚC TÍNH, chưa đo**; riêng HD-P2 được lead ước tính **1 giờ** trong `GIAO-CODEX-DOT-2.md` §1.

## 1. Kết luận

- **5 lát XML, tổng 15 giờ công ƯỚC TÍNH:** HD-0 → HD-1 → HD-2 → HD-3 → HD-4. Không cộng phần ZIP, bảng kê, tải cổng thuế hoặc thời gian chờ Anh/Core. Không dùng lại con số 9 lát/29 giờ của phiếu cũ làm cam kết cho đợt SDK 2.0.
- **4 lát mở rộng, tổng 14 giờ ƯỚC TÍNH:** HD-5 → HD-6 → HD-7 → HD-8, chi tiết §2.4–2.6 và §4. Tách đọc ZIP và xuất XLSX thành hai năng lực `hoa_don.doc_zip@1`, `hoa_don.bang_ke_xlsx@1`; giữ nguyên hợp đồng `hoa_don.doc_xml@2`. Tổng phiếu triển khai XML + ZIP/XLSX là **29 giờ ước tính**, tình cờ bằng tổng phiếu cũ nhưng khác phạm vi; không gồm HD-P2, PDF, portal hoặc chờ Core.
- Đích triển khai sau HD-P: gói `e_hoa_don/goi/e_hoa_don/`, SDK 2.0, đọc **một tệp XML** thuộc profile hiện có `DEMO_M2_XML_QD1271_FIELDS_V1`; đầu ra là bộ trường tĩnh và tham chiếu tệp JSON chi tiết. Không suy thành bộ đọc mọi chuẩn XML, kiểm chữ ký số hay xác nhận hợp lệ thuế.
- Tái dùng lõi `ma-nguon/lib/hoa_don_xml.py`: DTO bất biến, strict path/namespace, occurrence, Decimal, `raw_ref`, locator, hash, tiền/thuế và quan hệ nguồn; tận dụng phép chiếu trong `ma-nguon/doc.py` và quy tắc trạng thái trong `ma-nguon/lib/trang_thai.py`. Không viết parser thay thế.
- Viết lại vỏ bằng `Engine.tu_khai_bao`, `@app.nang_luc`, `viec.mo_tep`, `viec.tai_tep_ra`. **Bỏ khỏi gói mới** vỏ `ma-nguon/chay.py` dùng socket/Bootstrap/SDKEngine, shim và bridge Core; không sửa, di chuyển hoặc xóa các bản tham chiếu. Ghi phần không dùng vào `VIEC.md` để lead xử lý lưu trữ sau.
- `tai.py`, `phien.py`, `portal.cjs`, `bang_ke.cjs`, `vendor/`, Node lock và các schema `.v1` cũ chỉ làm tham chiếu trong đợt XML. Nguồn Node và lock đã có trong `ma-nguon/` theo `NGUON.md`/CHANGELOG ngày 06/11, dù bảng hiện trạng cũ còn ghi một phần; điều này không chứng minh đã kiểm Chromium, tải thật hoặc đã chốt phạm vi công bố.
- **Đọc XML, tải về và nhận vào nghiệp vụ kế toán là ba kết quả riêng.** Đầu ra bộ đọc luôn giữ trạng thái thuế `UNKNOWN`, ghi nhận nghiệp vụ `NOT_PERFORMED`. SDK báo `XONG` chỉ xác nhận bước đọc kỹ thuật đã trả kết quả, không xác nhận đủ điều kiện hạch toán.
- HD-P là lịch sử lập phiếu XML. HD-P2 **chỉ sửa tài liệu**, giữ nguyên mã/gói đã có; chạy đủ ba lệnh kiểm AGENTS.md §5, pytest thêm `--basetemp=.pytest-tmp` theo đầu bài. Kết quả chỉ chứng minh hồi quy gói XML hiện tại, không chứng minh ZIP/XLSX đã triển khai.

## 2. Thiết kế phiếu `engine.json` 2.0

### 2.1 Năng lực và phong bì

| Năng lực trong gói SDK 2.0 | Nhận | Trả | Phạm vi |
|---|---|---|---|
| `hoa_don.doc_xml@2` | `tep` — `application/xml`, `text/xml` | `truong` — bộ trường cố định ở §2.2 | Đọc XML strict hiện có; ghép trường vào cột ngăn, tệp chi tiết giữ dữ liệu nhiều dòng |

**Lý do `@2`:** manifest 1 cũ công bố `hoa_don.doc_xml@1` nhận `tham_chieu_tep.v1`, trả `hoa_don.v1`. Chuyển sang `tep` → `truong` là đổi cách nhận/trả; theo API b.2 và mẫu phiếu §3.3 phải tăng số năng lực. Giữ bản cũ trong `ma-nguon/`, không đổi nội dung `@1` hoặc tự chuyển quy trình đang dùng nó. Lead/Core quản lý giữ phiên bản cũ và chuyển khai báo quy trình; gói mới không đăng ký một `@1` giả tương thích.

- Core có đúng ba loại gốc `tep`, `van_ban`, `truong`: bước đầu nhận `tep`, bước này kết thúc bằng `truong`. Không nhận XML qua `van_ban` để tránh mất hash bytes/mã hóa nguồn; không nhận đường dẫn máy dưới dạng tham số.
- `loai_du_lieu_rieng: []`. Bốn loại riêng trong `LOAI-DU-LIEU-RIENG.md` phục vụ OCR/AI/Mask, không biểu diễn hóa đơn có dòng hàng và Decimal. Không mượn các mã ấy hoặc dùng `hoa_don.v1` làm một loại gốc. **Chưa cần loại riêng mới**, vì dữ liệu chi tiết được lưu thành tệp qua SDK; không sửa danh mục chung trong HD-P.
- `tham_so: []`: đợt này không có lựa chọn ZIP/portal, kỳ tải, tài khoản hay context JSON do người dùng tự nhập. Chưa mở quy tắc hạch toán, sửa số hoặc tự chọn pháp nhân.

**Khung khai báo** (danh sách `truong_ra` điền đầy đủ theo §2.2):

```json
{
  "phien_ban_manifest": 2,
  "loai": "engine",
  "ma": "e_hoa_don",
  "ten": "Đọc XML hóa đơn",
  "phien_ban": "1.0.0",
  "tuong_thich": {"core": ">=2.0.0 <3.0.0", "api": "v1", "sdk": ">=2.0.0 <3.0.0"},
  "che_do_chay": "cuc_bo",
  "diem_vao": {"lenh": ["{python}", "-m", "e_hoa_don.chay"], "thu_muc": "."},
  "loai_du_lieu_rieng": [],
  "tai_nguyen": {"so_viec_dong_thoi": 1},
  "readiness": {"thoi_han_giay": 30},
  "bi_mat": [],
  "webhook": null
}
```

Đây là khung thiết kế, **chưa phải manifest hoàn chỉnh**: HD-0 phải thêm `nang_luc`, `truong_ra`, `gioi_han`, `huy_duoc`, `tham_so` và ít nhất một `chay_thu_demo` thực sự chạy qua bộ đọc. Không thêm khóa ngoài hợp đồng API/SDK.

### 2.2 Trường trả về và độ chính xác

Mọi kết quả thành công có phong bì `{"loai":"truong","truong":{...}}`, đủ các trường sau; giá trị nguồn thiếu/sai/mơ hồ là `null`, không tự điền số 0 hoặc tiền tệ.

| `ma` trong `truong_ra` | `kieu` | Nguồn/quy tắc |
|---|---|---|
| `mau_so`, `ky_hieu`, `so_hoa_don` | `van_ban` | `KHMSHDon`, `KHHDon`, `SHDon`; số hóa đơn giữ chuỗi và số 0 đầu |
| `ngay_lap` | `ngay` | `NLap` hợp lệ, `YYYY-MM-DD`; ngày sai để `null`, thêm cảnh báo |
| `ma_so_thue_ban`, `ma_so_thue_mua` | `van_ban` | `NBan/MST`, `NMua/MST`; không ép thành số |
| `don_vi_tien` | `van_ban` | `DVTTe` duy nhất, hợp lệ dạng ba chữ hoa; không mặc định VND |
| `tien_truoc_thue`, `tien_thue`, `tong_thanh_toan` | `so_tien` | Số nguồn từ `money.net_amount`, `tax_amount`, `total_amount`, kèm tiền tệ; không tính lại tổng |
| `so_dong` | `so` | Số dòng nguồn đọc được; không suy STT thành khóa dòng |
| `can_kiem_tra` | `co_khong` | `true` khi còn vấn đề nguồn, thiếu context, money/relations HOLD hoặc lý do ứng viên |
| `canh_bao` | `van_ban` | Các mã và câu tiếng Việt cố định, mỗi mục một dòng; không chèn XML, định danh hay đường dẫn vào câu lỗi |
| `tep_xml` | `tep` | Nguyên đối tượng tệp đầu vào của Core; không tạo ID, không tải lên lại bản XML |
| `chi_tiet_nguon` | `tep` | Đối tượng tệp `application/json` do `viec.tai_tep_ra` trả; chưa tải thành công thì không trả `XONG` |
| `nguon_doc` | `van_ban` | `xml_strict` |
| `phien_ban_engine` | `van_ban` | Ví dụ `e_hoa_don 1.0.0`, lấy từ phiên bản gói |
| `bam_dau_vao` | `van_ban` | `sha256:<64 ký tự hex>` của bytes XML thực, không băm lại văn bản đã chuẩn hóa |

- Tiền ở cổng SDK: ví dụ `{"so":"1000000.123456","tien_te":"VND"}`; chuyển Decimal bằng `format(value, "f")`, **không float/round**. SDK wheel 2.0.0 đang có chấp nhận chuỗi thập phân cho `so_tien.so` (`engine.py`, `_kiem_gia_tri_truong`); HD-0 phải có assertion qua CoreGia để kiểm chính đường trả kết quả này. Không dùng dạng cũ `gia_tri`/`don_vi_tien` cho trường `so_tien` của SDK.
- Chỉ chiếu giá trị tiền nguồn rõ ràng và mã tiền tệ hợp lệ. Số sai/mơ hồ để `null`; tổng mâu thuẫn nhưng từng số nguồn rõ thì giữ từng số và bật `can_kiem_tra`, không sửa tổng. Tiền nguồn vượt miền phép chiếu cũ 18 chữ số phần nguyên/6 thập phân: giữ exact text và issue trong tệp chi tiết, trường `so_tien` tương ứng là `null`, không cắt/làm tròn. `net_amount` bao gồm cả phần không chịu thuế; không đổi nhãn thành cơ sở tính thuế chịu thuế.
- Tệp JSON kỹ thuật phiên bản 1 có `phien_ban`, `nguon_doc`, `phien_ban_engine`, `bam_dau_vao`, `tep_xml`, `chi_tiet_nguon` = `ra_json(InvoiceReadResult)`. Giữ nguyên occurrence `ABSENT`/`EMPTY`/`TEXT`, thứ tự dòng, locator, raw ref, money, relations, issue, lý do ứng viên và semantic digest nếu có. `ra_json` loại raw bytes, giữ Decimal thành exact text; số tiền raw luôn đi cùng thông tin currency/trạng thái nguồn của DTO, không biến thành tiền chuẩn khi thiếu currency. Không đặt nhãn `contract: hoa_don.v1` lên báo cáo mới hoặc sửa schema `.v1` cũ để hợp thức hóa nó.
- `tep_id` của SDK là chuỗi tham chiếu, không có cam kết UUID; không dùng `_id()`/vòng cấp trước hai UUID của `doc.py` cũ. Lấy ID JSON **sau** `tai_tep_ra`; báo cáo không tự tham chiếu ID của chính nó. Tên báo cáo cố định `hoa-don-chi-tiet.json`, không ghép từ đường dẫn/tên hóa đơn.
- Không có cổng context nghiệp vụ tin cậy trong SDK đợt 1: handler truyền `context=None`. Vẫn đọc phần nguồn, trả `can_kiem_tra=true`; giữ `CONTEXT_ABSENT`, `IDENTITY_UNRESOLVED`, định danh và semantic digest `null` như lõi. Không lấy `ngu_canh.phap_nhan_id` làm MST, không tự tạo company/profile binding/crosswalk. Các ca context đầy đủ/mâu thuẫn chỉ thử trực tiếp lõi bằng context DEMO trong tests, chưa mở vào năng lực.
- Không ánh xạ enum `CHO` cũ thành `ChuaRo`: thiếu context là dữ liệu cần kiểm tra, không phải nguồn ngoài đã nhận việc. `TToan`/`TTHDLQuan` hiện có phần đọc bổ sung nhưng chưa thuộc semantic envelope V1; giữ nguyên issue/HOLD, không nâng thành bằng chứng nội dung đầy đủ.

### 2.3 Giới hạn, cấu hình máy và dữ liệu tạm

- `gioi_han`: `tep_toi_da_mib: 16`, `mime: ["application/xml","text/xml"]`, `thoi_han_giay: 600`; `huy_duoc: true`. Đây là trần tiếp nhận XML đang có; không chép `trang_toi_da`, `adapter`, `capability` hay hồ sơ socket của manifest 1 vào phiếu 2.0. Kiểm bytes thực bằng đọc tối đa `16 MiB + 1` trước parse, kể cả metadata khai thiếu/sai. Quá hạn bước do Core thu lease; engine không tự đặt lại lease.
- Trần JSON chi tiết **32 MiB, giới hạn kỹ thuật đề xuất, chưa đo**; kiểm trước upload, vượt → từ chối rõ, không cắt occurrence/dòng/cảnh báo. Thử biên bằng dữ liệu sinh trong test, không commit tệp lớn.
- **Quyết định 15/11 thay phương án JSON ngoài gói cũ:** không đọc/ghi tệp cấu hình máy hoặc dùng `KTT_ENGINE_CAU_HINH`/`KTT_ENGINE_DU_LIEU` làm nguồn lưu. XML/ZIP/XLSX hiện **không cần cấu hình hay bảng ngăn**. `chay.py` hiện không import/nạp `cau_hinh_may.py`; HD-5 xác nhận giữ nó ngoài đường chạy, cập nhật hồ sơ và ghi việc lưu trữ sau, không xóa tệp cũ.
- Nếu tính năng sau cần giữ cấu hình/dữ liệu: dùng cổng `Ngan` theo `GIAO-CODEX-DOT-2.md` §2 và `DE-NGHI-SDK-2.1.md` §3 (`doc`, `tim`, `lo`, CAS); `chon_ngan(app)` chọn `app.ngan`, chưa có thì `NganBoNho` RAM, cảnh báo một lần ra stderr như tài liệu chung. Màn cấu hình thuộc engine dùng `KttCore.engine(ma)`. Thiếu cấu hình trả `CHUA_CAU_HINH`; không lấy cấu hình làm authority nghiệp vụ. Chưa thêm cổng/màn/ngăn khi XML/ZIP/XLSX không dùng.
- XML đọc/xử lý trong RAM; tệp ra gửi kho tệp Core bằng SDK. **Không cần `kho_tam.py`, dấu chống trùng nghiệp vụ hay dữ liệu bền riêng cho đợt XML.** Nếu phải dùng tệp trung gian thì chỉ thư mục tạm riêng của việc, dọn trong `finally`; không ghi nội dung vào thư mục dữ liệu engine.
- Không sổ JSON, đệm bền hay dấu chống trùng lưu trên máy, kể cả phần tải tương lai. Tệp vào/ra do Core quản qua SDK; xử lý trong RAM, tệp tạm riêng việc nếu bắt buộc phải dọn trong `finally` cả khi lỗi/hủy. Khi mở tải sau phải lập phiếu riêng về bí mật/phiên/lượt bền qua cửa chung; nguồn ngoài đã nhận mà chưa trả → `raise ChuaRo(ma_tuong_quan)`.
- Nhật ký kỹ thuật ra stderr: mã việc, nguồn đọc, mã lỗi cố định, thời gian, số đếm; không nội dung XML, số tiền, MST, số hóa đơn, credential hay đường dẫn. Nguồn gốc/băm/phiên bản nằm trong kết quả, không dùng nhật ký thay kết quả.

### 2.4 `hoa_don.doc_zip@1` — báo cáo từng tệp, không suy “đầy đủ”

**Thiết kế mới HD-P2, chưa triển khai.** `nhan: ["tep"]`, `tra: "truong"`, `tham_so: []`, `loai_du_lieu_rieng: []`. MIME `application/zip`, `application/x-zip-compressed`; `huy_duoc: true`, thời hạn 600 giây. Tái dùng `doc_goi_hoa_don_zip`/DTO/strict XML hiện có; không gọi năng lực XML qua engine/Core, không viết parser XML thứ hai.

Trường tĩnh phải khai trong `truong_ra`: `tep_zip`, `chi_tiet_nguon` kiểu `tep`; `so_tep`, `so_doc_duoc`, `so_loi`, `so_khong_ho_tro`, `so_trung_noi_dung` kiểu `so`; `da_doc_het`, `can_kiem_tra` kiểu `co_khong`; `canh_bao`, `bam_dau_vao`, `nguon_doc`, `phien_ban_engine` kiểu `van_ban`. `nguon_doc="zip_xml_strict"`; giữ nguyên `tep_zip` do Core cấp. JSON `hoa-don-goi-chi-tiet.json` tải qua `viec.tai_tep_ra`; chưa có tham chiếu Core thì không trả `XONG`.

JSON kỹ thuật mới `phien_ban: 1`, `nguon_doc`, `phien_ban_engine`, `bam_dau_vao` của bytes ZIP, `tep_zip`, `da_doc_het`, các số đếm trên, `do_du_ky_tai: "UNKNOWN"`, `danh_sach_tep`, `danh_sach_thu_muc`, `canh_bao`. Mỗi phần tử `danh_sach_tep` có:

| Trường | Nghĩa / điều kiện |
|---|---|
| `thu_tu`, `ten` | Ordinal 1-based theo central directory, giữ đúng tên entry; không sắp xếp theo tên, không gộp tên trùng. Ordinal có thể cách quãng vì thư mục nằm trong `danh_sach_thu_muc` với ordinal gốc |
| `bam`, `kich_thuoc` | SHA-256 bytes **đã giải nén đầy đủ và kiểm CRC**, độ dài thực; không băm tên, CRC hay bytes ZIP thay bytes tệp. Không đọc hết được thì `bam=null`, `kich_thuoc=null`, kèm lý do cố định |
| `trang_thai_doc` | `doc_duoc`: XML thuộc subset đang hỗ trợ; `loi`: XML hỏng/CRC sai/không mở được; `khong_ho_tro`: PDF, tệp khác, ZIP lồng hoặc XML ngoài profile/encoding/namespace/path. Không diễn giải PDF hoặc giải nén đệ quy |
| `trung_ten`, `trung_noi_dung_voi` | Cờ tên trùng và ordinal tệp **đứng trước đầu tiên có cùng băm bytes**, hoặc `null`. “Trùng” là dấu riêng, không thay trạng thái đọc; cùng tên khác bytes không là trùng nội dung. Chỉ so trong việc hiện tại, không chống trùng hạch toán |
| `ma_loi`, `canh_bao`, `can_kiem_tra` | Mã/câu cố định, không phản chiếu exception/đường máy/XML; tên entry chỉ ở trường metadata kết quả. `can_kiem_tra` giữ vấn đề nguồn, tiền/thuế/quan hệ và thiếu context |
| `truong_hoa_don`, `chi_tiet_nguon` | Với tệp đọc được: phép chiếu XML §2.2 (không tự tạo `tep_id` cho entry), cùng `ra_json(InvoiceReadResult)`, occurrence/locator/raw_ref. Dùng tham chiếu nguồn `(tep_zip, bam_goi, thu_tu, ten, bam)` thay trường `tep_xml` không tồn tại; không tạo tham chiếu kho Core giả. Với lỗi/không hỗ trợ: `truong_hoa_don=null`, giữ chi tiết chẩn đoán an toàn nếu có |

- **Kiểm kê mọi tệp:** `so_tep = so_doc_duoc + so_loi + so_khong_ho_tro`; `so_trung_noi_dung` là số entry có `trung_noi_dung_voi`, có thể giao với các nhóm đọc. Giữ cả bản trùng trong báo cáo và bảng kê; không tự xóa/gộp. Thư mục chỉ là metadata, không tính hóa đơn. Tệp không XML cũng phải đọc có chặn trần để lấy băm, khác nhánh cũ bỏ qua không băm.
- **Không sao chép nguyên `artifact_coverage=COMPLETE` của lõi:** lõi hiện bỏ non-XML/thư mục và không đánh dấu trùng nội dung. `da_doc_het=true` chỉ khi có ít nhất một tệp, kiểm kê hết, mọi tệp đọc được XML trong profile, có băm; có bất kỳ `loi`/`khong_ho_tro` thì `false`. ZIP rỗng/chỉ thư mục trả `false`, cảnh báo “Gói không có tệp hóa đơn đọc được.” Một XML tốt + một XML lỗi vẫn trả báo cáo từng tệp nhưng `da_doc_het=false`, `can_kiem_tra=true`. Không dùng chữ “đầy đủ” trong kết luận; dùng “Đã đọc X/Y tệp; có tệp lỗi/chưa hỗ trợ” theo số đếm. Đọc hết không xác nhận đủ kỳ, hợp lệ thuế hoặc đủ căn cứ hạch toán.
- XML lỗi sau khi giải nén đủ vẫn có băm; entry không đọc hết không băm phần đầu hoặc đoán băm. Tệp trùng bytes có thể giữ kết quả đọc riêng; không dùng tên làm khóa. `context=None`, trạng thái thuế `UNKNOWN`, ghi nhận `NOT_PERFORMED` như XML.
- **Trần đề xuất để kiểm ở HD-5/HD-8, chưa đo corpus:** ZIP 64 MiB; tối đa 1.000 entry gồm thư mục; mỗi tệp giải nén 16 MiB; tổng bytes giải nén 128 MiB; mỗi XML tối đa 1.000 HHDVu (gate HD-1 trước DTO); JSON ra 32 MiB. Kiểm metadata và bytes thực, đọc giới hạn + 1, cộng cả tệp không hỗ trợ/trùng. Vượt bất kỳ trần nào → từ chối **toàn việc** bằng `LoiNghiepVu`, không trả tập con `XONG`; không gọi quá trần là một lỗi cục bộ rồi bỏ phần dư. ZIP không mở được/central directory hỏng → lỗi toàn việc, không bịa danh sách rỗng đã kiểm hết. CRC/entry mã hóa/phương thức chưa hỗ trợ được báo riêng khi vẫn kiểm kê được gói trong trần.
- Không `extract`/`extractall`, không mở tên entry thành đường dẫn; tên `../`, đường tuyệt đối, tên trùng, Unicode chỉ là metadata. Kiểm hủy giữa các entry; mất lease/hủy/upload lỗi không đổi thành báo cáo thành công một phần. Bytes đầu vào/kết quả trong RAM; không sổ, đệm bền, tệp cấu hình hay nội dung lưu trên máy (§2.3).

### 2.5 `hoa_don.bang_ke_xlsx@1` — bảng kê có nguồn, số tiền là text

**Thiết kế mới HD-P2, chưa triển khai.** `nhan: ["truong"]`, `tra: "truong"`, `tham_so: []`, không loại riêng mới. Là bước sau `hoa_don.doc_xml@2` hoặc `hoa_don.doc_zip@1`; không là bước đầu nhận tệp XML/ZIP. Không sửa đầu ra XML cũ hoặc thêm mảng vào kiểu trường SDK. Core điều phối chuỗi; bộ xuất đọc **tệp JSON được tham chiếu ở `truong.chi_tiet_nguon`** qua `viec.mo_tep`, nhận diện schema XML hiện có hoặc ZIP §2.4, kiểm phiên bản/nguồn/băm/đếm và tham chiếu `tep_xml`/`tep_zip` khớp đầu vào. Thiếu/sai cấu trúc → `LoiNghiepVu("HD_BANG_KE_DAU_VAO", "Cần kết quả đọc XML hoặc ZIP hóa đơn hợp lệ để lập bảng kê.")`. Không nhận đường dẫn máy, không gọi engine khác, không parse lại XML bằng parser hiển thị Node.

Đầu ra `truong_ra` cố định: `bang_ke` (`tep`, MIME XLSX), `chi_tiet_nguon` (`tep`, giữ tham chiếu JSON nguồn), `so_hoa_don`, `so_loi`, `so_khong_ho_tro`, `so_trung_noi_dung` (`so`), `da_doc_het`, `can_kiem_tra` (`co_khong`), `canh_bao`, `bam_dau_vao`, `phien_ban_engine` (`van_ban`). Băm đầu vào là SHA-256 bytes JSON thực đọc; XLSX ghi cả băm JSON và băm XML/ZIP nguồn. `da_doc_het` kế thừa ZIP; với XML chỉ nói một tệp đã đọc kỹ thuật, giữ mọi cảnh báo/HOLD. Không có tổng tiền gộp nhiều currency.

Hai sheet tên cố định, không cắt tên do caller nhập:

- **`Hoa don`:** một dòng mỗi XML đọc được theo ordinal nguồn, gồm cả trùng. Cột: STT; thứ tự entry; tên entry; băm tệp; mẫu số; ký hiệu; số hóa đơn; ngày lập; MST bán; MST mua; tiền trước thuế; tiền thuế; tổng thanh toán; mã tiền tệ; cần kiểm tra; cảnh báo; trùng với thứ tự. XML đơn dùng thứ tự 1 và metadata tệp Core. Ngày hiển thị dd/mm/yyyy; JSON nguồn vẫn ISO. Không sinh dữ liệu không có như tên bên bán/mua ngoài allowlist.
- **`Kiem ke tep`:** mọi tệp, kể cả lỗi/không hỗ trợ/trùng; thứ tự, tên, băm hoặc ô trống + lý do, trạng thái đọc, trùng tên/trùng nội dung, mã lỗi/cảnh báo. Khối thông tin đầu sheet ghi số đếm, `da_doc_het`, băm/phiên bản/nguồn, “Không xác nhận đủ hóa đơn trong kỳ; chưa thực hiện ghi nhận nghiệp vụ”. ZIP đọc thiếu vẫn xuất được báo cáo XLSX với cảnh báo rõ; không biến nó thành bảng kê “đầy đủ”. ZIP không có XML đọc được có sheet hóa đơn chỉ tiêu đề và sheet kiểm kê đầy đủ các mục thực có.

**Quy tắc bắt buộc:**

1. Các cột tiền ghi **cell string**, định dạng text `@`, chuỗi thập phân exact từ DTO/JSON; ví dụ `1000000.123456` đi kèm `VND`. Không qua JavaScript `Number`/`parseFloat`, Python `float`, làm tròn hoặc công thức SUM. Giữ cả số 0 thập phân trong exact text; giá trị rõ vượt miền chiếu 18/6 lấy từ `exact_text`/occurrence nguồn có kiểm tra, kèm cảnh báo, không lấy scalar SDK `null` thay thành 0. Mơ hồ/sai thì ô tiền trống và cảnh báo, giữ toàn bộ occurrence trong JSON.
2. Mỗi số tiền luôn đi với cột mã tiền tệ nguồn. Thiếu/sai/mơ hồ currency: **không xuất thành số tiền hợp lệ**, cột tiền để trống và cảnh báo; raw exact text + trạng thái currency vẫn ở JSON. Không mặc định VND, không đổi tỷ giá. VND/USD khác nhau không cộng chung.
3. Số hóa đơn `0000123`, MST, mẫu số/ký hiệu, băm là cell string; không ép số, không thêm dấu nháy vào giá trị thực làm đổi chuỗi. Mọi text nguồn bắt đầu `=`, `+`, `-`, `@` cũng là string literal, không cell formula/hyperlink/macro; không thay đổi lexeme để chống formula.
4. Trần đề xuất: JSON vào 32 MiB (metadata + bytes thực); tối đa 1.000 dòng hóa đơn/1.000 entry kiểm kê, mỗi cell text tối đa **16.000 ký tự** (trần bảo thủ của engine, chưa đo), XLSX ra 32 MiB, thời hạn 600 giây; `huy_duoc=true`. Trường `gioi_han` manifest chỉ dùng khóa API cho phép (JSON nằm trong tệp tham chiếu nên handler vẫn phải kiểm); vượt → `HD_BANG_KE_VUOT_GIOI_HAN`, không cắt dòng/text hoặc làm tròn.
5. Xuất XLSX vào buffer RAM, gửi `hoa-don-bang-ke.xlsx` bằng `viec.tai_tep_ra`; có tham chiếu Core mới trả `XONG`. Không ghi `.xlsx`/JSON trung gian/cache trên máy. Nếu công cụ buộc dùng tạm: thư mục riêng việc, dọn `finally` trên cả thành công/lỗi/hủy; không dùng tạm để thay sổ bền. Chưa có nhu cầu ngăn/cấu hình; không tạo màn riêng.

### 2.6 So sánh nguồn XLSX và quyết định sử dụng

| Phương án | Ưu điểm có căn cứ | Phần phải làm / trade-off |
|---|---|---|
| Node + ExcelJS | Nguồn cũ có phép chiếu tiền thành text | Tham chiếu cách chiếu cột/định dạng từ `ma-nguon/bang_ke.cjs`, không chạy. |
| Python + thư viện XLSX | Cùng runtime engine, hỗ trợ XLSX | Cần bổ sung dependency, nguồn, giấy phép và kiểm cài sạch. |
| **Python stdlib (`zipfile` + XML OOXML tối thiểu tự viết) — chọn** | Cùng runtime engine, không thêm dependency | Tự viết và kiểm OOXML, quan hệ, style và tính tương thích. |

**Quyết định của lead 15/11/2026:** engine chạy Python theo SDK 2.0; Core chưa có cơ chế cấp runtime Node, bổ sung runtime sẽ thêm Cần Core và rủi ro cài máy sạch. Bảng kê chỉ cần cell chữ (inline string, định dạng text `@`), vài style, độ rộng cột và dòng tiêu đề cố định, đủ nhỏ để tự viết bằng thư viện chuẩn; không thêm dependency.

**Quyền nguồn:** `ma-nguon/NGUON.md` ghi CD-096 A1 cho phần mềm nội bộ, chỉ dùng nội bộ. HD-7 tham chiếu tĩnh `bang_ke.cjs` để đối chiếu phép chiếu và định dạng phù hợp §2.5; ghi nguồn tương đối, quyền và SHA bytes thực của nguồn tham chiếu cùng mô tả vào `NGUON.md`, không tự đặt LICENSE mới. Không coi quyền nội bộ là quyền phân phối bên ngoài.

## 3. Các lát

| Lát | Nội dung | Yêu cầu đối chiếu phiếu cũ | Phụ thuộc | Giờ ƯỚC TÍNH | Tệp mã tối đa, không tính test/tài liệu |
|---|---|---|---|---:|---|
| HD-0 | Khung SDK 2.0 + kiểm độc lập; `cau_hinh_may` là phương án lịch sử, được HD-5 đưa ra khỏi đường chạy theo quyết định 15/11 | HD-1 (XML), HD-9 (khung độc lập) | API/SDK đã khóa; phạm vi XML được giao trong HD-P | 4 | 5: `__init__.py`, `chay.py`, `cau_hinh_may.py`, `hoa_don_xml.py`, `doc.py` |
| HD-1 | Kiểm chặt phép chiếu, Decimal, vấn đề nguồn và giới hạn | HD-1 (XML), HD-8 (số/tiền) | HD-0 | 3 | 2: `doc.py`, `hoa_don_xml.py`; chỉ sửa lõi khi có lỗi chứng minh được |
| HD-2 | Bàn giao tệp, hủy, mất lease, gửi lại và nhật ký qua SDK | HD-6 (phần cổng), HD-9 | HD-1 | 3 | 2: `chay.py`, `doc.py` |
| HD-3 | Bộ XML DEMO có đáp án, regression và Chạy thử DEMO | HD-8; HD-10 chỉ phần XML/CoreGia | HD-2 | 3 | Tối đa 2 tệp runtime nếu phải sửa lỗi; phần còn lại là test/dữ liệu DEMO |
| HD-4 | Ghim nguồn/phụ thuộc, cài sạch Windows/Linux, bàn giao | HD-9 | HD-3 | 2 | Không thêm mã nghiệp vụ; tối đa 2 kịch bản kiểm trong `tests/` |
| | **Tổng phần XML được lập phiếu** | | | **15** | |
| HD-5 | Lõi ZIP + báo cáo từng entry; xác nhận cấu hình tệp ngoài đường chạy | HD-1, HD-5 (yêu cầu cũ) | HD-4; quyết định Anh 15/11 | 4 | Tối đa 4: `zip.py`, `hoa_don_xml.py`, `doc.py`, `chay.py` |
| HD-6 | Công bố `hoa_don.doc_zip@1`, bàn giao JSON qua CoreGia | HD-5, HD-6 (yêu cầu cũ) | HD-5 | 3 | Tối đa 2: `chay.py`, `zip.py` |
| HD-7 | `hoa_don.bang_ke_xlsx@1`, Python stdlib, tiền text exact | HD-2, HD-8 (yêu cầu cũ) | HD-6; nguồn/quyền CD-096 A1 ở §2.6 | 5 | Tối đa 3: `chay.py`, `bang_ke.py`, `xlsx_toi_thieu.py`; test ngoài gói |
| HD-8 | Oracle ZIP/XLSX, kiểm độc lập/cài sạch | HD-8, HD-9; chưa phải bài Core thật HD-10 | HD-7 | 2 | Tối đa 2 runtime nếu sửa lỗi có chứng cứ; vượt thì tách lát |
| | **Tổng ZIP + XLSX, không PDF/portal** | | | **14** | |

HD-0 có thêm việc chép lõi/chiếu XML tối thiểu vì SDK 2.0.0 trả mã 1 nếu `chay_thu_demo` rỗng. Không dùng stub trả thành công hoặc sửa bộ thử để làm xanh khung gói. Mỗi lát chạy đủ ba lệnh AGENTS.md §5, mỗi PR không quá khoảng 5 tệp mã; vượt thì tách lát và ghi lý do trước khi mở rộng.

| Phần việc phụ thuộc chưa chốt | Trạng thái | Điều kiện mới được lập lát triển khai |
|---|---|---|
| ZIP nhiều hóa đơn và báo cáo từng entry | **Đã mở phạm vi 15/11; chờ triển khai HD-5/HD-6** | §2.4; không cần Anh chốt lại Q2 |
| Bảng kê XLSX | **Đã mở phạm vi 15/11; chờ triển khai HD-7/HD-8** | §2.5–2.6; Python stdlib theo quyết định lead, không thêm dependency |
| PDF | **Để sau theo quyết định 15/11** | Phiếu riêng sau này; không kéo Chromium/renderer vào XLSX |
| Lát tải giả, nối nguồn portal/phiên/Windows | **chờ Anh chốt** | Q5–Q8 và cửa chung Core cho bí mật, context, trạng thái, lượt bền |
| Lát công cụ thử trên máy Windows/cổng thuế | **chờ Anh chốt** | Chỉ lập sau các lát trên; công cụ chạy khô mặc định + `.cmd` ASCII, **Anh tự chạy**; cổng thuế thật cần lệnh riêng |

Đợt XML không phụ thuộc Node, Chromium, tài khoản Windows hay dịch vụ ngoài nên **không cần lát thử máy thật riêng**; HD-4 là lát cuối đợt này. Bài trình duyệt/Core thật 120 phút của phiếu cũ, quyền pháp nhân, nhận trùng nghiệp vụ và màn module không được tính là đã nghiệm thu bằng CoreGia.

## 4. Lệnh giao Codex từng lát (dán nguyên khối)

HD-0…HD-4 dưới đây giữ cấu trúc lệnh XML để đối chiếu lịch sử. Các chỉ dẫn cấu hình tệp/ZIP-XLSX “chờ Anh” trong bản cũ được cập nhật theo §2.3 và quyết định 15/11; không tái triển khai phương án lưu trên đĩa. Lệnh HD-5…HD-8 là phần giao mới của HD-P2.

### HD-0 — Khung gói SDK 2.0 và XML DEMO
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, docs/goi-gui-engine/sdk-2.0.0/HUONG-DAN-VIET-ENGINE.md và MAU-PHIEU-ENGINE.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md, e_hoa_don/CLAUDE.md, YEU-CAU-VA-HIEN-TRANG.md, PHIEU-ENGINE-e_hoa_don.md và VIEC.md trong docs/ của engine.
Làm lát HD-0 cho e_hoa_don, chỉ phần XML; ZIP/bảng kê có phiếu riêng HD-5…HD-8, tải để sau. Tạo e_hoa_don/goi/e_hoa_don/ theo AGENTS.md §3; tham khảo engine-demo/e_demo_doc_tep và e_demo_dem_tu. Không sửa ma-nguon/, mã Core, SDK hoặc tài liệu API đã khóa; không commit/push khi chưa có lệnh.
1. engine.json 2.0: một năng lực hoa_don.doc_xml@2, nhan [tep], tra truong, đủ mọi truong_ra ở phiếu §2.2, tham_so [], loai_du_lieu_rieng [], giới hạn 16 MiB/XML/600 giây, huy_duoc=true; điểm vào {python} -m e_hoa_don.chay. Không đăng ký @1 hoặc ZIP/bảng kê/tải. Thêm schema cấu hình máy và schema báo cáo JSON kỹ thuật, README, CHANGELOG, dữ liệu DEMO nhỏ.
2. Tối đa 5 tệp mã runtime: e_hoa_don/{__init__,chay,cau_hinh_may,hoa_don_xml,doc}.py trong gói. Chép lib/hoa_don_xml.py từ ma-nguon vào hoa_don_xml.py; đổi cả import thường và lazy import sang kho_tri_thuc_sdk.primitives / kho_tri_thuc_sdk.engine_legacy.Issue. Không lấy SDKEngine/Bootstrap. Giữ các thuật toán strict/Decimal và chuỗi __module__ legacy chỉ để giữ dấu vết; không tạo shim/sys.modules tên Core, không dùng pickle. Nhánh ZIP đi cùng tệp nguồn chỉ là mã nội bộ chưa kích hoạt, không thêm handler hay DEMO ZIP.
3. doc.py chỉ chiếu DTO sang bộ trường §2.2 và dựng JSON chi tiết từ ra_json; tận dụng quy tắc _text/kiểm đầu hóa đơn/tiền của doc.py cũ và quy tắc lỗi của lib/trang_thai.py, không chép vòng UUID/cap_tham_chieu hoặc contract hoa_don.v1. Handler dùng viec.mo_tep, context=None, giữ nguyên tham chiếu XML, upload JSON bằng viec.tai_tep_ra rồi mới return truong. Không stub XONG, không bỏ các trường đã khai.
4. Cập nhật quyết định 15/11: XML không cần cấu hình; không đọc/ghi JSON cấu hình ngoài gói, không kho_tam. cau_hinh_may.py đã có thì giữ tệp nhưng đưa ra khỏi đường chạy ở HD-5; dữ liệu cần giữ sau này chỉ qua Ngan theo §2.3.
5. e_hoa_don/tests/kiem_doc_lap.py: kiểm AST/import cả lazy/dynamic, không kho_tri_thuc.*, không SDKEngine/Bootstrap/kenh_engine, không phụ thuộc đường Core/shim; quét gói không __pycache__/.pyc/symlink hoặc tệp vượt trần đóng gói. Không nhầm chuỗi __module__ legacy thành import được phép. Kiểm trong tiến trình sạch chỉ có gói + SDK/stdlib; mã thoát 0/1. Chạy Python với -B/PYTHONDONTWRITEBYTECODE để không sinh bytecode trong gói.
Test Linux/Windows bằng CoreGia SDK: XML DEMO 0000123, ngày 2026-10-30, tiền hàng 1000000 VND, thuế 100000 VND, tổng 1100000 VND; tiền lẻ kiểm so_tien.so là chuỗi exact; JSON chi tiết không raw bytes, giữ locator/hash/Decimal. Thiếu context vẫn XONG bước đọc nhưng can_kiem_tra=true, không tạo semantic digest/định danh. XML hỏng → LoiNghiepVu HD_XML_KHONG_DOC_DUOC, câu tiếng Việt không lộ nguồn; không gọi mạng ngoài CoreGia, không Node/Cloud/cổng thuế.
Đạt: có ít nhất 1 DEMO qua bộ đọc thật, không chay_thu_demo rỗng; chạy .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don; .venv\Scripts\python -B -m pytest e_hoa_don/tests -q; .venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py (Linux dùng .venv/bin/python). SDK mọi DEMO [ĐẠT], pytest 0 lỗi, kiem_doc_lap mã 0. Ghi kết quả thật vào PR và VIEC.md/CHANGELOG: đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật.
```

### HD-1 — XML strict, tiền và vấn đề nguồn
```
Đọc AGENTS.md, API-ENGINE-v1.md và hướng dẫn SDK 2.0.0 trong docs/goi-gui-engine/, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md và e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md. Làm HD-1 sau HD-0; chỉ XML DEMO, không ZIP/bảng kê/portal, không sửa ma-nguon/, SDK/Core, không commit/push khi chưa có lệnh.
Giữ hoa_don.doc_xml@2: tep XML → truong đủ §2.2 + tệp JSON chi tiết. Tối đa 2 tệp runtime doc.py/hoa_don_xml.py; ưu tiên bọc lỗi/phép chiếu, không sửa lõi nếu chưa có lỗi chứng minh được.
- Giữ nguyên SHDon/MST/mã hàng ở dạng chuỗi, ABSENT/EMPTY/TEXT và mọi occurrence trùng; không strip namespace, tìm descendant, chọn scalar đầu/cuối, hoặc lấy STT/MaHang làm định danh logic. Ngày chỉ YYYY-MM-DD; ngày sai/null có cảnh báo và lexeme gốc trong JSON.
- Decimal exact, giữ số 0 thập phân; không float/round/default 0. Tiền SDK là {so: chuỗi exact, tien_te: mã tiền}; tiền thiếu/sai/mơ hồ/không có currency là null. Áp miền phép chiếu cũ 18/6: vượt miền chỉ giữ raw exact text + issue, không cắt. Tổng nguồn lệch thì giữ các số rõ ràng, can_kiem_tra=true; không tính lại để thay số nguồn, không gọi net_amount là net chịu thuế. Giữ money/relations và chi tiết thuế trong báo cáo.
- Đọc bytes thực tối đa 16 MiB + 1; vượt → LoiNghiepVu HD_XML_QUA_LON, "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn." Metadata vượt trần có thể bị SDK từ chối trước với VUOT_GIOI_HAN. XML hỏng → HD_XML_KHONG_DOC_DUOC, "Không đọc được cấu trúc tệp XML hóa đơn." Encoding/DOCTYPE/namespace/path ngoài profile → HD_XML_NGOAI_PROFILE, "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ." Không phản chiếu exception, lexeme hoặc đường dẫn. Không bắt tràn mọi DataError: lỗi invariant nội bộ để SDK báo lỗi chung.
- Kiểm JSON chi tiết <=32 MiB trước upload; vượt → LoiNghiepVu HD_KET_QUA_QUA_LON, "Kết quả đọc hóa đơn vượt giới hạn. Anh hãy chia nhỏ dữ liệu đầu vào." Không cắt dòng/occurrence/cảnh báo. Giữ TOTAL_SECTION_UNSUPPORTED và lý do ngoài semantic envelope V1; không xóa issue để tạo digest.
- Handler vẫn context=None: can_kiem_tra=true, không giả company/profile binding; CHO nội bộ không đổi thành ChuaRo. Context DEMO đầy đủ/mâu thuẫn chỉ kiểm trực tiếp hàm thuần, không thêm tham_so hoặc khóa ngu_canh.
Test CoreGia + unit test lõi (không Core thật): số 0000123; số lẻ 1000000.123456 VND; ABSENT khác EMPTY và số 0; tiền sai dấu phẩy/exponent; quá 18/6, số lượng/đơn giá quá 21/6; thiếu currency; field trùng/mixed; ngày không tồn tại; namespace/DOCTYPE/XML hỏng; tổng lệch; TTHDLQuan; context thiếu/mâu thuẫn không tạo identity/digest giả; bytes thực vượt trần dù metadata nhỏ; báo cáo vượt trần. Đáp án literal độc lập với parser, không sinh expected từ output.
Chạy đủ .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don; .venv\Scripts\python -B -m pytest e_hoa_don/tests -q; .venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py (Linux dùng .venv/bin/python). Mọi DEMO [ĐẠT], 0 lỗi, skip có lý do. Cập nhật VIEC.md/CHANGELOG và PR với kết quả thật, ghi đã kiểm bằng Core giả (CoreGia).
```

### HD-2 — Bàn giao tệp, hủy và gửi lại qua SDK
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, hướng dẫn SDK 2.0.0, _chung/docs/GIAO-CODEX-THU-TU.md và e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md. Làm HD-2 sau HD-1; giữ nguyên tep XML → truong của hoa_don.doc_xml@2, chỉ DEMO, không sửa ma-nguon/, SDK/Core và không commit/push khi chưa có lệnh. Tối đa 2 tệp runtime chay.py/doc.py.
- viec.kiem_huy()/tien_do trước đọc, sau parse, trước upload và trước return; không bắt mất tín hiệu hủy/mất lease. Báo tiến độ bằng câu cố định, không số hóa đơn/MST/tiền/XML. Không tự viết heartbeat, vòng retry hoặc HTTP server/socket riêng; SDK quản lý lease/Idempotency-Key/gửi lại.
- Mở tệp chỉ bằng tep_id qua viec.mo_tep; tên tệp là metadata, không mở đường dẫn theo ten, không truy cập tệp ngoài kho Core. Giữ đối tượng tep_xml đầu vào; tạo báo cáo không chứa raw bytes hoặc ID tự cấp. Upload hoa-don-chi-tiet.json bằng viec.tai_tep_ra; chỉ return đủ trường sau khi có tham chiếu Core trả. Không gọi _id UUID hoặc tự tạo ID thay khi upload lỗi.
- Chỉ giữ bytes/kết quả trong RAM tới bàn giao. Nếu dùng tạm thì tạm riêng việc, dọn finally; không nhật ký nội dung hay cache tài liệu ở thư mục dữ liệu engine. Không thêm kho_tam/dedupe nghiệp vụ: cùng XML khác pháp nhân là các việc riêng, chống nhận trùng vào kế toán thuộc Core/module.
- stderr chỉ mã việc/nguồn/số đếm/thời gian/mã lỗi cố định; không prompt, dữ liệu tài liệu, định danh nghiệp vụ, đường dẫn hay secret. Lỗi XML theo HD-1; không bọc ViecDaHuy/mất lease thành LoiNghiepVu hoặc XONG. XML cục bộ không có nguồn ngoài nhận việc nên không phát ChuaRo để che lỗi upload/thiếu context.
Test bằng CoreGia SDK + MayChuGia loopback (không cổng thuế): đọc/upload thành công; tep_id không phải UUID; giữ nguyên bytes XML gốc và hash; gay_mat_xac_nhan("tep"), gay_mat_xac_nhan("ket_qua"), gay_mat_xac_nhan("ket_thuc") không tạo kết quả hoặc tệp trùng khi gửi lại; upload thất bại không XONG; hủy ở các điểm kiểm không nộp kết quả; mất lease 409/404/410 dừng, không nộp/không kết thúc; giao lại việc thuần không ghi nhận nghiệp vụ; hai pháp nhân DEMO không chia sẻ cache. Kiểm stderr/loi bằng canary DEMO. Thêm test app.chay nhận một dòng JSON khởi động stdin qua MayChuGia; không sửa SDK nếu thiếu seam test, ghi Cần Core/SDK vào VIEC.md.
Chạy .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don; .venv\Scripts\python -B -m pytest e_hoa_don/tests -q; .venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py (Linux dùng .venv/bin/python). Ghi số thật vào PR/VIEC.md/CHANGELOG; kết luận chỉ đã kiểm bằng Core giả (CoreGia), không suy quyền kho tệp/Core thật đã đạt.
```

### HD-3 — Bộ XML DEMO và regression
```
Đọc AGENTS.md, hướng dẫn SDK 2.0.0, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md và e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md. Làm HD-3 sau HD-2, chỉ bộ XML DEMO có đáp án; không ZIP/bảng kê/tải/Cloud/Node, không sửa ma-nguon/, tests-tu-core/, tu-core-cu/, Core/SDK; không commit/push khi chưa có lệnh.
- Tận dụng ý đồ test trong tests-tu-core/test_hoa_don_xml.py, test_g3_goi_hd_reader.py, test_g3_goi_hd_anh_xa.py và tu-core-cu/tests/test_g3_hd_1.py. Các test cũ trỏ namespace Core/fixtures không kèm trong gói không chạy nguyên trạng. Tự dựng fixture XML giả + đáp án literal độc lập trong e_hoa_don/tests/demo; không tự nhận hash golden cũ đã được kiểm khi thiếu bytes fixture gốc, không skip âm thầm ca cần thiết.
- engine.json có ít nhất 3 chay_thu_demo dương tính, tep_demo nằm trong demo/ của gói: số 0000123/ngày 2026-10-30/tiền 1000000 VND + thuế 100000 VND = tổng 1100000 VND; mẫu tiền lẻ 1000000.123456 VND + 100000.012345 VND = 1100000.135801 VND; mẫu thiếu một số nguồn để kiểm null/cảnh báo. XML phải đúng subset của parser; tên Công ty DEMO Ánh Dương là nhãn mô tả fixture, không thêm Ten ngoài allowlist rồi gọi đó là ca hoàn toàn hỗ trợ. Không mẫu nào cần cấu hình máy hay mạng ngoài Core giả.
- Lệnh SDK trực tiếp phải chạy được offline trên gói, không thay bằng bộ thử riêng che lỗi. Pytest kiểm giá trị từng trường và tệp chi tiết qua CoreGia.doc_tep; SDK chỉ thấy XONG chưa chứng minh tiền/hash đúng. Mẫu không context có can_kiem_tra=true; thiếu TToan/tổng hoặc ngoài envelope V1 không được tự báo đầy đủ.
- Ca âm trong pytest, không đặt vào chay_thu_demo mong XONG: XML hỏng, sai profile/namespace/DOCTYPE, MIME sai, field trùng/rỗng/thiếu, tiền/ngày sai, tiền vượt miền, tổng lệch, thiếu currency, giới hạn, hủy, upload/retry/mất lease, log không lộ canary. Khẳng định LoiNghiepVu đúng mã/câu cố định theo HD-1; không cắt ngầm, không thêm cảnh báo giả để né lỗi cấu trúc.
- Tệp lớn chỉ sinh lúc test trong thư mục DEMO tạm, không commit. Tối đa 2 tệp runtime nếu cần sửa lỗi; còn lại test/tài liệu/dữ liệu. Cập nhật VIEC.md và YEU-CAU-VA-HIEN-TRANG.md, phân biệt XML đã kiểm bằng Core giả (CoreGia) với ZIP/bảng kê/tải còn chờ Anh.
Chạy .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don; .venv\Scripts\python -B -m pytest e_hoa_don/tests -q; .venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py (Linux dùng .venv/bin/python). Đạt ít nhất 3/3 DEMO, pytest 0 lỗi, kiem_doc_lap mã 0; ghi kết quả thật và skip có lý do vào PR/CHANGELOG. Không ghi đã chạy bài Core thật 120 phút.
```

### HD-4 — Ghim nguồn và cài máy sạch
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, hướng dẫn SDK 2.0.0, _chung/docs/GIAO-CODEX-THU-TU.md và e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md. Làm HD-4 sau HD-3, chỉ gói XML; không sửa ma-nguon/, Core/SDK, không commit/push khi chưa có lệnh, không chạy tài khoản/cổng thuế hay thay đổi hệ thống Windows.
- goi/e_hoa_don/requirements.lock ghi đúng SDK 2.0.0 và SHA wheel trong repo; thư viện ngoài SDK hiện không cần (chỉ stdlib), không chép lock CHUA_KIEM của ma-nguon hoặc metadata candidate 1.4.1. Cài SDK wheel offline --no-index --no-deps; không kéo cryptography/jsonschema/Node/browser nếu engine không dùng. Nếu phát sinh thư viện thì không tự thêm ngoài phạm vi phiếu; báo lead, ghi nguồn và pin trước khi dùng.
- NGUON.md: nguồn tương đối ma-nguon → từng tệp gói, thay đổi import/phép chiếu, phiên bản/giấy phép đã có căn cứ, SHA-256 bytes thực, xử lý khác biệt LF/CRLF. Không tự đặt giấy phép mới, không ghi đường dẫn máy phát triển. Không đưa bang_ke/portal/vendor/Node lock/shim/tests tham chiếu vào gói XML; runtime chỉ SDK + stdlib + mã nội bộ. Không sửa metadata hash để bỏ qua nguồn đổi.
- Hai kịch bản e_hoa_don/tests/kiem_may_sach.sh và KIEM-MAY-SACH.cmd (ASCII): tạo venv mới ở thư mục tạm kiểm DEMO, cài SDK wheel đã đối chiếu SHA, chép đúng gói sang vị trí khác ngoài cây source, chạy DEMO + kiểm nhập độc lập. Không dùng PYTHONPATH trỏ Core/ma-nguon/shim. Trên Windows chỉ thao tác venv/tệp DEMO trong workspace, không cài máy hệ thống; việc vận hành khác chỉ soạn .cmd cho Anh tự chạy. Test cấu hình thiếu vẫn đọc được XML và LoiNghiepVu khi gọi chức năng cần cấu hình chưa có.
- Chạy bản phù hợp môi trường hiện có; ghi rõ Windows/Linux nào đã chạy và môi trường nào chưa kiểm, không ghi đã chạy Linux nếu chỉ có Windows. Không phát sinh tệp __pycache__/.pyc bằng -B/PYTHONDONTWRITEBYTECODE. Không thêm mã nghiệp vụ, tối đa 2 kịch bản kiểm ngoài runtime. Ghi phần cũ không dùng vào VIEC.md, không xóa hoặc chuyển LUU-TRU trong lát này.
- README/CHANGELOG hướng dẫn nhận tep XML, trả truong §2.2 + tệp JSON, tiền exact kèm tiền tệ, null/HOLD/canh_bao; chưa có context tin cậy thì chỉ đọc kỹ thuật; chuyển quy trình @1 → @2 do lead/Core và giữ bản cũ, không tự động đổi. Chưa công bố ZIP/bảng kê/tải; bằng chứng chỉ đã kiểm bằng Core giả (CoreGia).
Chạy .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don; .venv\Scripts\python -B -m pytest e_hoa_don/tests -q; .venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py (Linux dùng .venv/bin/python), thêm kiểm cài sạch. Mọi DEMO [ĐẠT], 0 lỗi, skip có lý do; VIEC.md/CHANGELOG/PR ghi số thật, ngày, giờ thực tế và Cần Core/Chờ Anh. Đợt XML không cần công cụ thử cổng thật; nếu mở phần tải sau thì phải lập phiếu riêng chờ Anh chốt.
```

### HD-5 — ZIP: lõi và kiểm kê từng tệp (4 giờ ước tính)
```
Đọc AGENTS.md; API-ENGINE-v1.md + hướng dẫn/mẫu phiếu SDK 2.0.0; _chung/docs/QUYET-DINH-ANH-20261115.md; GIAO-CODEX-DOT-2.md §2; DE-NGHI-SDK-2.1.md; LOAI-DU-LIEU-RIENG.md; e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md §2.3–2.4 và hồ sơ engine. Làm HD-5 sau HD-4, chỉ DEMO. Không sửa Core/SDK/ma-nguon, không xóa tệp, không commit/push khi chưa có lệnh.
Tối đa 4 runtime: zip.py, hoa_don_xml.py, doc.py, chay.py. Tái dùng lõi doc_goi_hoa_don_zip/strict XML/DTO; chỉnh có test khi cần để chặn tổng giải nén/gate 1.000 HHDVu trước DTO, lấy băm non-XML và giữ entry lỗi. Không viết parser XML thứ hai; không đổi hoa_don.doc_xml@2. Kiểm cau_hinh_may.py vẫn ngoài đường chạy chay.py như hiện tại, giữ tệp/test lịch sử và ghi việc lưu trữ sau; không thêm ngăn khi không có dữ liệu cần giữ.
Tạo zip.py + schema JSON kỹ thuật gói theo §2.4. Duyệt central directory theo ordinal 1-based, mở ZipInfo thay tên; giữ tên trùng/khác bytes và mọi bản trùng nội dung. Băm bytes giải nén đầy đủ có CRC, không đọc đủ thì bam=null kèm lý do, không dùng CRC thay SHA. Tách trạng thái đọc và dấu trùng; non-XML đọc có trần để băm nhưng không parse. Thư mục báo riêng. Không kế thừa COMPLETE của lõi để tuyên bố đủ; đếm đối chiếu, da_doc_het=false khi rỗng/lỗi/không hỗ trợ; do_du_ky_tai UNKNOWN, thuế UNKNOWN, ghi nhận NOT_PERFORMED, context=None.
Giới hạn §2.4: ZIP 64 MiB, 1.000 entry, 16 MiB/tệp, tổng giải nén 128 MiB, 1.000 HHDVu/XML, JSON 32 MiB. Vượt trần từ chối toàn việc bằng LoiNghiepVu HD_ZIP_VUOT_GIOI_HAN, câu tiếng Việt cố định; ZIP không kiểm kê được → HD_ZIP_KHONG_DOC_DUOC. CRC/entry không mở được trong gói còn kiểm kê được báo cục bộ. Không cắt ngầm/giải nén đĩa/đệ quy; không cấu hình tệp, sổ hoặc cache bền, mọi dữ liệu trong RAM; tạm bắt buộc phải dọn finally.
Điều kiện đạt: unit tests đáp án độc lập cho tốt+hỏng+PDF+trùng bytes+trùng tên khác bytes, thứ tự khác thứ tự từ điển, ZIP rỗng/chỉ thư mục, XML ngoài profile, CRC/mã hóa, tên ../ và tuyệt đối, băm null khi không đọc đủ; biên/trần metadata giả, tổng giải nén, 1.001 HHDVu chặn trước DTO. Khẳng định không mở tên thành đường máy, không ghi nội dung/cấu hình, không báo đầy đủ hoặc gộp trùng. HD-5 chưa đăng ký năng lực ZIP; XML hiện có và hồi quy phải đạt.
Chạy .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don; .venv\Scripts\python -B -m pytest e_hoa_don/tests -q --basetemp=.pytest-tmp; .venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py (Linux dùng .venv/bin/python). Mọi DEMO ĐẠT, pytest 0 lỗi, kiểm độc lập mã 0; ghi số thật/skip có lý do, ngày, PR, giờ vào VIEC.md/CHANGELOG. Ghi rõ đã kiểm bằng Core giả (CoreGia), không suy Core thật.
```

### HD-6 — `hoa_don.doc_zip@1`: cổng SDK và báo cáo gói (3 giờ ước tính)
```
Đọc AGENTS.md, hợp đồng/hướng dẫn SDK 2.0.0, quyết định 15/11 và GIAO-CODEX-DOT-2.md §2, e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md §2.3–2.4. Làm HD-6 sau HD-5. Tối đa 2 runtime chay.py/zip.py; chỉ DEMO, không sửa Core/SDK/ma-nguon, không xóa/commit/push khi chưa có lệnh.
Đăng ký hoa_don.doc_zip@1: nhan [tep], tra truong đủ trường tĩnh §2.4, tham_so [], không loại riêng, MIME ZIP, 64 MiB/600 giây, hủy được. Giữ nguyên doc_xml@2. Handler đọc qua viec.mo_tep và giới hạn bytes thực; kiểm hủy giữa entry, trước upload/trả. Giữ tep_zip, băm bytes ZIP thực; tải hoa-don-goi-chi-tiet.json qua viec.tai_tep_ra rồi mới trả. Không tạo tep_id cho entry, gọi engine khác hay nhận nghiệp vụ. Lỗi/hủy/mất lease/upload thất bại không đổi XONG; nguồn cục bộ không dùng ChuaRo che lỗi.
Thêm chay_thu_demo dương cho ZIP hỗn hợp có ít nhất XML tốt, XML lỗi, PDF, trùng nội dung/tên; SDK XONG chỉ là đã trả báo cáo, phải da_doc_het=false và can_kiem_tra=true. Test CoreGia đối chiếu toàn JSON/từng băm/ordinal/đếm với đáp án literal, cảnh báo không gọi đầy đủ. ZIP rỗng giữ cảnh báo, ZIP hỏng/vượt trần từ chối không upload. Test hủy/mất lease/gửi lại Idempotency-Key/upload lỗi, canary không ra stderr/tiến độ/câu lỗi. Chỉ giữ tên entry trong metadata báo cáo.
Không lưu gì trên máy: không cấu hình tệp/sổ/cache, RAM; tạm riêng việc nếu bắt buộc dọn finally. Chưa cần Ngan; về sau dùng đúng cổng Ngan/RAM, không sổ JSON. Điều kiện đạt: DEMO XML+ZIP đều ĐẠT, các ca trên không mất entry và không giả thành công/đủ kỳ; giữ UNKNOWN/NOT_PERFORMED/context=None.
Chạy đủ ba lệnh AGENTS.md §5 bằng .venv\Scripts\python -B (Linux .venv/bin/python); pytest e_hoa_don/tests -q --basetemp=.pytest-tmp. Ghi kết quả thật, skip có lý do, ngày/PR/giờ vào VIEC.md/CHANGELOG: đã kiểm bằng Core giả (CoreGia); chưa nghiệm thu Core thật/quyền kho tệp.
```

### HD-7 — `hoa_don.bang_ke_xlsx@1`: XLSX chính xác (5 giờ ước tính)
```
Đọc AGENTS.md, API/hướng dẫn SDK 2.0.0, quyết định 15/11, GIAO-CODEX-DOT-2.md §2 và phiếu §2.3–2.6; đọc tĩnh ma-nguon/bang_ke.cjs và NGUON.md trong worktree. Làm sau HD-6; tối đa 3 tệp runtime dự kiến chay.py, bang_ke.py, xlsx_toi_thieu.py; test ngoài gói. Không sửa nguồn tham chiếu/Core/SDK, không xóa/commit/push.
Dùng Python stdlib: zipfile và XML OOXML tối thiểu tự viết, buffer RAM; hai sheet Hoa don/Kiem ke tep, inline string với định dạng text @, style, độ rộng cột và dòng tiêu đề cố định. Nhận truong từ doc_xml@2/doc_zip@1, trả truong §2.5; đọc JSON bằng viec.mo_tep, kiểm schema/phiên bản/băm/tham chiếu/đếm; không parse XML lại. Đối chiếu cột và thứ tự theo §2.5 với bang_ke.cjs bằng đọc tĩnh, ghi rõ cột mới/khác theo thiết kế; không chạy mã tham chiếu. Giữ mọi entry, lỗi và trùng. Tiền là chuỗi exact kèm mã tiền tệ, số hóa đơn 0000123 và MST giữ string; không float/round/SUM. Sai/mơ hồ/thiếu currency để trống và cảnh báo; text bắt đầu =,+,-,@ là literal, không formula/hyperlink; không cắt dữ liệu.
Giới hạn JSON 32 MiB, 1.000 dòng/1.000 entry, text 16.000 ký tự/cell, XLSX 32 MiB, 600 giây; vượt → LoiNghiepVu HD_BANG_KE_VUOT_GIOI_HAN, không upload phần cắt. Kiểm hủy trong xử lý, trước upload/trả; lỗi/hủy/mất lease/upload lỗi không XONG. Upload buffer bằng viec.tai_tep_ra, chỉ trả khi có tham chiếu. Không lưu cấu hình/sổ/cache/XLSX/JSON trên máy; nếu bắt buộc có tạm riêng việc, dọn finally cả lỗi/hủy. Chưa cần ngăn/cấu hình/màn riêng.
Test đọc lại XLSX bằng zipfile, kiểm XML hợp lệ và quan hệ, sheet, thứ tự cột, style text @, freeze header, độ rộng và giá trị cell bằng oracle độc lập; không lấy output writer làm expected. Test đối chiếu tĩnh cột/thứ tự với bang_ke.cjs và giải thích khác biệt §2.5. Kiểm tiền 1000000.123456, 1000000.120000, âm/0, trên 2^53, ngoài 18/6, currency thiếu/USD; số 0000123, null/EMPTY, text giống formula, tổng nguồn lệch, lỗi/trùng ZIP. Kiểm sai schema/trộn nguồn/vượt trần/upload lỗi/hủy/mất lease không XONG. Ghi nguồn tham chiếu, quyền A1, SHA bytes thực và cách dùng vào NGUON.md; không thêm dependency.
SDK 2.0.0 chay_thu_demo chưa cấp fixture tệp lồng trong truong: kiểm XLSX bằng pytest với CoreGia.them_tep/kết quả bước đọc thật, ghi mức phủ riêng và Cần Core; không tạo ID giả hoặc sửa SDK. Chạy ba lệnh AGENTS.md §5 bằng .venv\Scripts\python -B (Linux .venv/bin/python), pytest --basetemp=.pytest-tmp; ghi số thật, skip có lý do, giờ/ngày/PR vào VIEC.md/CHANGELOG; đã kiểm bằng Core giả (CoreGia), chưa kiểm Core thật/Excel app thì ghi rõ.
```

### HD-8 — Oracle, nguồn và cài sạch ZIP/XLSX (2 giờ ước tính)
```
Đọc AGENTS.md, API/SDK 2.0.0, quyết định 15/11, GIAO-CODEX-DOT-2.md §2 và phiếu §2.3–2.6. Làm sau HD-7, chỉ DEMO ZIP/XLSX; tối đa 2 tệp runtime nếu sửa lỗi có chứng cứ, vượt thì tách lát; không sửa Core/SDK/ma-nguon, không xóa/commit/push.
Bộ DEMO có đáp án literal và pin bytes/SHA độc lập: ZIP đúng thứ tự, lỗi từng tệp, PDF/ZIP lồng, trùng bytes/tên khác bytes, rỗng/thư mục, CRC/mã hóa, namespace, trần metadata/bytes/tổng giải nén/JSON/XLSX/cell, 1.000/1.001 HHDVu. Mẫu lớn chỉ sinh trong RAM/tạm test. So từng entry/đếm/băm, tiền exact/currency/số 0 đầu, raw/null/cảnh báo/HOLD; đọc lại hai sheet bằng zipfile, kiểm mọi XML hợp lệ, quan hệ OOXML và cell/style/thứ tự bằng oracle độc lập; test so cột/thứ tự với bang_ke.cjs bằng đọc tĩnh. Kiểm không sinh công thức hay tổng đa tiền tệ; lỗi không đổi thành đủ kỳ hoặc đã ghi nhận.
Mở rộng kiểm độc lập/cài sạch cho SDK + Python stdlib, giữ chặn Core/shim/import chưa ghim/mạng và tiến trình ngoài. Gói sao chép ngoài source vẫn đọc XML/ZIP/xuất XLSX, không PYTHONPATH Core/ma-nguon. Chạy Windows/Linux khi có, ghi môi trường chưa chạy; không tự cài hệ thống Windows. Đối chiếu quyền A1 và SHA bytes thực của nguồn tham chiếu, kể cả LF/CRLF nếu khác; không giả mã băm phát hành.
Chứng minh engine không ghi bền; tạm nếu có dọn finally cả lỗi/hủy; bytes/tệp bàn giao do Core quản. Kiểm hủy/upload/ACK/mất lease/canary cho cả hai năng lực. Ca cần Core thật/Excel app/quyền tệp chưa kiểm ghi rõ, không tính đạt bằng fixture.
Điều kiện đạt: đủ oracle ZIP/XLSX và hồi quy XML, mọi DEMO đang khai ĐẠT, không lỗi/skip không giải thích; kiểm độc lập và cài sạch trên môi trường thực chạy đạt; giữ nợ môi trường/Core. Chạy .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don; .venv\Scripts\python -B -m pytest e_hoa_don/tests -q --basetemp=.pytest-tmp; .venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py (Linux .venv/bin/python), thêm kịch bản cài sạch phù hợp.
Cập nhật VIEC.md/CHANGELOG/NGUON/README và báo cáo AGENTS.md §6, số thật + giờ thực so 2 giờ ước tính; đã kiểm bằng Core giả (CoreGia), không kết luận Core thật hoặc bài nghiệp vụ 120 phút đã đạt. Cần Core thiếu fixture ghi vào VIEC.md, không đổi API đã khóa.
```

## 5. Cần Core / Chờ Anh của engine này

### 5.1 Cần Core / SDK

| Việc | Cách làm đợt XML | Điều kiện cho phần tiếp theo |
|---|---|---|
| Ngăn/cấu hình SDK 2.1 chưa có | XML/ZIP/XLSX không cần; HD-5 đưa cấu hình tệp cũ ra khỏi đường chạy | Khi cần dùng `Ngan`/RAM, không lưu đĩa; Core cấp `app.ngan`/cấu hình qua cửa chung, không route riêng hóa đơn |
| DEMO `truong` tham chiếu JSON nguồn | SDK 2.0.0 chỉ cấp `tep_demo` khi đầu vào là `tep`; pytest CoreGia cấp tệp/kết quả bước đọc để kiểm XLSX | Cần fixture/chuỗi Chạy thử chung, không route riêng hóa đơn hoặc ID giả; không công bố đã có DEMO XLSX trực tiếp khi chưa có seam |
| Context nguồn/profile/company/raw binding chưa có chỗ truyền được kiểm quyền trong hợp đồng engine đợt 1 | `context=None`, trả nguồn + cảnh báo; không tự mở khóa `ngu_canh` | Lead đề xuất cửa context tin cậy dùng chung; Core resolve theo pháp nhân và kiểm quyền trước khi giao. Không lấy tham_so người dùng làm authority |
| Tham chiếu tệp và chuyển năng lực cũ sang SDK 2.0 | Dùng `tep_id` SDK như chuỗi, upload qua SDK; mới là `@2` | Core/module dùng khai báo và giữ pin bản cũ cho quy trình `@1`; xác minh quyền tệp vào/ra, lưu kết quả đúng pháp nhân trên Core thật |
| Ngăn engine/CAS, lượt bền #10, bí mật theo tên, trạng thái tương tác | Chưa cần cho parser XML thuần, không làm kho nội dung tạm | Chặn phần tải thật tới khi có cửa chung và Anh chốt; không nối pipe bí mật tự chế hoặc SQL để vượt SDK |
| Fixture/golden cũ được test tham chiếu nhưng không có trong bộ `ma-nguon` hiện tại | Dựng DEMO có đáp án độc lập; không khẳng định đã đối chiếu toàn bộ golden cũ | Lead bàn giao bộ fixture DEMO có nguồn và hash nếu cần chứng minh tương thích toàn bộ corpus |

Các mục này được ghi vào `e_hoa_don/docs/VIEC.md` để chuyển lead Core qua Anh. Không sửa tài liệu API/SDK, `_chung/tham-chieu-cong-hien-tai/`, mã Core hoặc tự thêm màn/bảng riêng.

### 5.2 Quyết định Q1–Q3 và phần còn chờ

| Mã | Câu hỏi cần Anh chốt | Đề xuất | Phương án khác / tác động | Phần phụ thuộc |
|---|---|---|---|---|
| Q1 | **Đã chốt 15/11:** XML là mốc 1; mở tiếp ZIP + bảng kê Excel | Giữ HD-0…HD-4 và thêm HD-5…HD-8 | Không suy thành duyệt PDF/portal hoặc nhận nghiệp vụ | HD-P2 lập phiếu; chưa triển khai ZIP/XLSX |
| Q2 | **Đã chốt 15/11:** ZIP báo cáo từng tệp, thứ tự/tên/băm/đọc được/lỗi/không hỗ trợ/trùng | §2.4: giữ từng entry, không gọi “đầy đủ” khi lỗi | Coverage gói khác độ đủ kỳ tải; không tự gộp trùng | `hoa_don.doc_zip@1`, HD-5/HD-6 |
| Q3 | **Đã chốt 15/11:** XLSX giữ chuỗi tiền exact + mã tiền tệ, số hóa đơn giữ số 0 đầu | §2.5; PDF để sau | Lead chốt Python stdlib ở §2.6; không thêm dependency | `hoa_don.bang_ke_xlsx@1`, HD-7/HD-8 |
| Q4 | Quyền tham chiếu nguồn cũ: **đã có căn cứ CD-096 A1** tại `ma-nguon/NGUON.md` | Chỉ dùng nội bộ, đối chiếu nguồn/hash tham chiếu tĩnh và ghi vào NGUON ở HD-7 | Không bao phủ phân phối bên ngoài hoặc nguồn mới chưa rõ quyền; không nạp portal/server | Không hỏi lại quyền đã có; PDF/portal vẫn để sau |
| Q5 | Phạm vi tải: pháp nhân, mua vào/bán ra, kỳ tháng, nhóm truy vấn và xử lý thiếu nhóm? | DEMO trước; kỳ trọn tháng, giữ lỗi/coverage từng nhóm, không suy COMPLETE từ sự kiện done; giữ riêng tải/đọc/nhận nghiệp vụ | Chưa đủ seam coverage/profile thì chỉ thử seam giả, không mở năng lực tải | Lát tải/phiên **chờ Anh chốt** và chờ Core, chưa công bố `hoa_don.tai_cong_thue@1` |
| Q6 | Tài khoản Windows, phiên có màn hình, CAPTCHA và vòng đời profile đặt ở đâu? | Tài khoản riêng khác Core/module/engine khác; CAPTCHA gõ tại máy chủ, profile riêng mỗi pháp nhân/phiên; dọn lỗi chặn phiên mới; bí mật qua cơ chế Core được duyệt, không env/args/tệp | Hoãn phần Windows, chỉ ghi bằng chứng giả; không yêu cầu Anh gửi mật khẩu qua chat | Lát Windows/Chromium và công cụ thử thật **chờ Anh chốt** |
| Q7 | Màn nghiệp vụ và cách kiểm kê/quyền tạm đặt ở đâu? | Dùng Chạy thử DEMO chung cho XML; quyền/hàng việc/kho tệp do Core, màn nghiệp vụ thuộc module. Lead trình cơ chế kiểm kê tạm để Anh chốt | Màn thử riêng Core DEMO nếu module chưa nối phải ghi chưa nghiệm thu nghiệp vụ; không làm UI riêng trong engine | Lát nối nghiệp vụ/màn/kiểm kê **chờ Anh chốt**, ngoài 15 giờ |
| Q8 | Khi nào được thử cổng thuế thật, phạm vi tài khoản và kỳ tải nào? | Chỉ sau DEMO và bằng chứng Windows/Core; Anh ra lệnh riêng có phạm vi. Công cụ mặc định chạy khô + `.cmd` ASCII để Anh tự chạy | Tiếp tục chỉ DEMO, chưa ước tính giờ tải thật khi thiếu điều kiện | Lát cuối thử thật **chờ Anh chốt**; HD-P và 5 lát XML không dùng tài khoản/cổng thật |

Q1–Q3 không còn chờ Anh. Q5–Q8 thuộc phần tải/Windows/màn nghiệp vụ để sau, không chặn ZIP/XLSX. Phiếu HD-P2 là thiết kế triển khai theo phạm vi đã mở, không là bằng chứng đã nối Core thật.
