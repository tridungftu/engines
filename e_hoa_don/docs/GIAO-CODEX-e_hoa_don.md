# Giao Codex — `e_hoa_don` (Đọc XML hóa đơn) theo SDK 2.0

*Lập 14/11/2026, lát HD-P. Căn cứ: `AGENTS.md`, `CLAUDE.md`, toàn bộ ba tệp trong `e_hoa_don/docs/` trước HD-P, mã `ma-nguon/`, `API-ENGINE-v1.md`, SDK 2.0.0, `_chung/docs/GIAO-CODEX-THU-TU.md`, `_chung/docs/LOAI-DU-LIEU-RIENG.md`; cấu trúc theo phiếu giao `e_hoi_ai` và `e_ocr`.*

**Anh chưa có quyết định cuối cho engine này.** Phiếu này chỉ giao phần đọc XML đã được xác định trong đầu bài HD-P; không duyệt thay phiếu nghiệp vụ cũ. Các số giờ dưới đây là **ƯỚC TÍNH, chưa đo**, không phải thời gian đã thực hiện HD-P. Đầu bài chưa cấp giờ ước tính riêng cho HD-P.

## 1. Kết luận

- **5 lát XML, tổng 15 giờ công ƯỚC TÍNH:** HD-0 → HD-1 → HD-2 → HD-3 → HD-4. Không cộng phần ZIP, bảng kê, tải cổng thuế hoặc thời gian chờ Anh/Core. Không dùng lại con số 9 lát/29 giờ của phiếu cũ làm cam kết cho đợt SDK 2.0.
- Đích triển khai sau HD-P: gói `e_hoa_don/goi/e_hoa_don/`, SDK 2.0, đọc **một tệp XML** thuộc profile hiện có `DEMO_M2_XML_QD1271_FIELDS_V1`; đầu ra là bộ trường tĩnh và tham chiếu tệp JSON chi tiết. Không suy thành bộ đọc mọi chuẩn XML, kiểm chữ ký số hay xác nhận hợp lệ thuế.
- Tái dùng lõi `ma-nguon/lib/hoa_don_xml.py`: DTO bất biến, strict path/namespace, occurrence, Decimal, `raw_ref`, locator, hash, tiền/thuế và quan hệ nguồn; tận dụng phép chiếu trong `ma-nguon/doc.py` và quy tắc trạng thái trong `ma-nguon/lib/trang_thai.py`. Không viết parser thay thế.
- Viết lại vỏ bằng `Engine.tu_khai_bao`, `@app.nang_luc`, `viec.mo_tep`, `viec.tai_tep_ra`. **Bỏ khỏi gói mới** vỏ `ma-nguon/chay.py` dùng socket/Bootstrap/SDKEngine, shim và bridge Core; không sửa, di chuyển hoặc xóa các bản tham chiếu. Ghi phần không dùng vào `VIEC.md` để lead xử lý lưu trữ sau.
- `tai.py`, `phien.py`, `portal.cjs`, `bang_ke.cjs`, `vendor/`, Node lock và các schema `.v1` cũ chỉ làm tham chiếu trong đợt XML. Nguồn Node và lock đã có trong `ma-nguon/` theo `NGUON.md`/CHANGELOG ngày 06/11, dù bảng hiện trạng cũ còn ghi một phần; điều này không chứng minh đã kiểm Chromium, tải thật hoặc đã chốt phạm vi công bố.
- **Đọc XML, tải về và nhận vào nghiệp vụ kế toán là ba kết quả riêng.** Đầu ra bộ đọc luôn giữ trạng thái thuế `UNKNOWN`, ghi nhận nghiệp vụ `NOT_PERFORMED`. SDK báo `XONG` chỉ xác nhận bước đọc kỹ thuật đã trả kết quả, không xác nhận đủ điều kiện hạch toán.
- HD-P **chỉ sửa tài liệu**, không tạo `goi/`, không chạy ba lệnh kiểm engine. Kiểm riêng cấu trúc và khả năng trích nguyên khối §4 bằng regex theo đầu bài. Những lệnh và đường dẫn gói bên dưới là việc của các lát tương lai.

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
- `cau_hinh_may.py` theo `GIAO-CODEX-THU-TU.md` §2: JSON ngoài gói, đường dẫn từ `KTT_ENGINE_CAU_HINH`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\e_hoa_don\cau_hinh.json`. Schema riêng trong gói; khung hiện tại chỉ cần `phien_ban: 1`, không khóa lạ/bí mật. XML thuần **không cần cấu hình máy**: thiếu tệp vẫn khởi động và đọc XML được, không tự tạo thư mục hay tệp mặc định. Chỉ đọc cấu hình khi tính năng cần; Linux dùng đường dẫn DEMO do test cấp, không bịa đường Windows.
- Thiếu cấu hình của tính năng tương lai → `LoiNghiepVu("CHUA_CAU_HINH", "Chưa cấu hình chức năng này.")` tại việc cần nó; JSON cấu hình lỗi → `CAU_HINH_MAY_KHONG_HOP_LE`, câu cố định không lộ đường dẫn. Không nhét context/pháp nhân/tài khoản vào cấu hình máy để vượt qua hạn chế SDK.
- XML đọc/xử lý trong RAM; tệp ra gửi kho tệp Core bằng SDK. **Không cần `kho_tam.py`, dấu chống trùng nghiệp vụ hay dữ liệu bền riêng cho đợt XML.** Nếu phải dùng tệp trung gian thì chỉ thư mục tạm riêng của việc, dọn trong `finally`; không ghi nội dung vào thư mục dữ liệu engine.
- Khi phần tải được duyệt sau: dữ liệu bền tạm chỉ băm/mã/số đếm ở `KTT_ENGINE_DU_LIEU`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\e_hoa_don\du-lieu\`; JSON ghi nguyên tử + khóa tệp như §2 tài liệu chung. Cookie, profile, XML, credential không được cất trong sổ này. Chưa tạo sổ ở các lát XML; nguồn ngoài đã nhận mà chưa trả phải `raise ChuaRo(ma_tuong_quan)`, chờ Core có lượt bền để thay lớp tạm.
- Nhật ký kỹ thuật ra stderr: mã việc, nguồn đọc, mã lỗi cố định, thời gian, số đếm; không nội dung XML, số tiền, MST, số hóa đơn, credential hay đường dẫn. Nguồn gốc/băm/phiên bản nằm trong kết quả, không dùng nhật ký thay kết quả.

## 3. Các lát

| Lát | Nội dung | Yêu cầu đối chiếu phiếu cũ | Phụ thuộc | Giờ ƯỚC TÍNH | Tệp mã tối đa, không tính test/tài liệu |
|---|---|---|---|---:|---|
| HD-0 | Khung SDK 2.0 + `cau_hinh_may` + `kiem_doc_lap`; tái dùng lõi XML để có DEMO thật ngay từ khung | HD-1 (XML), HD-9 (khung độc lập) | API/SDK đã khóa; phạm vi XML được giao trong HD-P | 4 | 5: `__init__.py`, `chay.py`, `cau_hinh_may.py`, `hoa_don_xml.py`, `doc.py` |
| HD-1 | Kiểm chặt phép chiếu, Decimal, vấn đề nguồn và giới hạn | HD-1 (XML), HD-8 (số/tiền) | HD-0 | 3 | 2: `doc.py`, `hoa_don_xml.py`; chỉ sửa lõi khi có lỗi chứng minh được |
| HD-2 | Bàn giao tệp, hủy, mất lease, gửi lại và nhật ký qua SDK | HD-6 (phần cổng), HD-9 | HD-1 | 3 | 2: `chay.py`, `doc.py` |
| HD-3 | Bộ XML DEMO có đáp án, regression và Chạy thử DEMO | HD-8; HD-10 chỉ phần XML/CoreGia | HD-2 | 3 | Tối đa 2 tệp runtime nếu phải sửa lỗi; phần còn lại là test/dữ liệu DEMO |
| HD-4 | Ghim nguồn/phụ thuộc, cài sạch Windows/Linux, bàn giao | HD-9 | HD-3 | 2 | Không thêm mã nghiệp vụ; tối đa 2 kịch bản kiểm trong `tests/` |
| | **Tổng phần XML được lập phiếu** | | | **15** | |

HD-0 có thêm việc chép lõi/chiếu XML tối thiểu vì SDK 2.0.0 trả mã 1 nếu `chay_thu_demo` rỗng. Không dùng stub trả thành công hoặc sửa bộ thử để làm xanh khung gói. Mỗi lát chạy đủ ba lệnh AGENTS.md §5, mỗi PR không quá khoảng 5 tệp mã; vượt thì tách lát và ghi lý do trước khi mở rộng.

| Phần việc phụ thuộc chưa chốt | Trạng thái | Điều kiện mới được lập lát triển khai |
|---|---|---|
| Lát XML/ZIP nhiều hóa đơn và báo cáo coverage | **chờ Anh chốt** | Q2 ở §5; chưa cấp mã HD-n, chưa có lệnh code ZIP |
| Lát bảng kê XLSX/PDF và nguồn Node | **chờ Anh chốt** | Q3, Q4; tách lát nếu vượt 5 tệp mã |
| Lát tải giả, nối nguồn portal/phiên/Windows | **chờ Anh chốt** | Q5–Q8 và cửa chung Core cho bí mật, context, trạng thái, lượt bền |
| Lát công cụ thử trên máy Windows/cổng thuế | **chờ Anh chốt** | Chỉ lập sau các lát trên; công cụ chạy khô mặc định + `.cmd` ASCII, **Anh tự chạy**; cổng thuế thật cần lệnh riêng |

Đợt XML không phụ thuộc Node, Chromium, tài khoản Windows hay dịch vụ ngoài nên **không cần lát thử máy thật riêng**; HD-4 là lát cuối đợt này. Bài trình duyệt/Core thật 120 phút của phiếu cũ, quyền pháp nhân, nhận trùng nghiệp vụ và màn module không được tính là đã nghiệm thu bằng CoreGia.

## 4. Lệnh giao Codex từng lát (dán nguyên khối)

### HD-0 — Khung gói SDK 2.0 và XML DEMO
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, docs/goi-gui-engine/sdk-2.0.0/HUONG-DAN-VIET-ENGINE.md và MAU-PHIEU-ENGINE.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md, e_hoa_don/CLAUDE.md, YEU-CAU-VA-HIEN-TRANG.md, PHIEU-ENGINE-e_hoa_don.md và VIEC.md trong docs/ của engine.
Làm lát HD-0 cho e_hoa_don, chỉ phần XML đã được giao; chưa có quyết định cuối cho ZIP/bảng kê/tải. Tạo e_hoa_don/goi/e_hoa_don/ theo AGENTS.md §3; tham khảo engine-demo/e_demo_doc_tep và e_demo_dem_tu. Không sửa ma-nguon/, mã Core, SDK hoặc tài liệu API đã khóa; không commit/push khi chưa có lệnh.
1. engine.json 2.0: một năng lực hoa_don.doc_xml@2, nhan [tep], tra truong, đủ mọi truong_ra ở phiếu §2.2, tham_so [], loai_du_lieu_rieng [], giới hạn 16 MiB/XML/600 giây, huy_duoc=true; điểm vào {python} -m e_hoa_don.chay. Không đăng ký @1 hoặc ZIP/bảng kê/tải. Thêm schema cấu hình máy và schema báo cáo JSON kỹ thuật, README, CHANGELOG, dữ liệu DEMO nhỏ.
2. Tối đa 5 tệp mã runtime: e_hoa_don/{__init__,chay,cau_hinh_may,hoa_don_xml,doc}.py trong gói. Chép lib/hoa_don_xml.py từ ma-nguon vào hoa_don_xml.py; đổi cả import thường và lazy import sang kho_tri_thuc_sdk.primitives / kho_tri_thuc_sdk.engine_legacy.Issue. Không lấy SDKEngine/Bootstrap. Giữ các thuật toán strict/Decimal và chuỗi __module__ legacy chỉ để giữ dấu vết; không tạo shim/sys.modules tên Core, không dùng pickle. Nhánh ZIP đi cùng tệp nguồn chỉ là mã nội bộ chưa kích hoạt, không thêm handler hay DEMO ZIP.
3. doc.py chỉ chiếu DTO sang bộ trường §2.2 và dựng JSON chi tiết từ ra_json; tận dụng quy tắc _text/kiểm đầu hóa đơn/tiền của doc.py cũ và quy tắc lỗi của lib/trang_thai.py, không chép vòng UUID/cap_tham_chieu hoặc contract hoa_don.v1. Handler dùng viec.mo_tep, context=None, giữ nguyên tham chiếu XML, upload JSON bằng viec.tai_tep_ra rồi mới return truong. Không stub XONG, không bỏ các trường đã khai.
4. cau_hinh_may.py đọc JSON ngoài gói theo KTT_ENGINE_CAU_HINH và mặc định §2.3, có schema; thiếu tệp vẫn khởi động và đọc XML. Không đọc cấu hình máy thật khi test, không chứa bí mật; hàm đọc kiểm trên thư mục DEMO tạm. Tính năng cần cấu hình nhưng thiếu thì LoiNghiepVu CHUA_CAU_HINH; cấu hình sai trả câu tiếng Việt cố định. Không tạo kho_tam vì XML thuần không cần dữ liệu bền.
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

## 5. Cần Core / Chờ Anh của engine này

### 5.1 Cần Core / SDK

| Việc | Cách làm đợt XML | Điều kiện cho phần tiếp theo |
|---|---|---|
| Kênh cấu hình máy chung chưa có (`GIAO-CODEX-THU-TU` §2, §3.1) | Có `cau_hinh_may` + schema ngoài gói; XML không cần cấu hình | Core đưa `cau_hinh`/schema qua cửa chung, không route riêng hóa đơn |
| Context nguồn/profile/company/raw binding chưa có chỗ truyền được kiểm quyền trong hợp đồng engine đợt 1 | `context=None`, trả nguồn + cảnh báo; không tự mở khóa `ngu_canh` | Lead đề xuất cửa context tin cậy dùng chung; Core resolve theo pháp nhân và kiểm quyền trước khi giao. Không lấy tham_so người dùng làm authority |
| Tham chiếu tệp và chuyển năng lực cũ sang SDK 2.0 | Dùng `tep_id` SDK như chuỗi, upload qua SDK; mới là `@2` | Core/module dùng khai báo và giữ pin bản cũ cho quy trình `@1`; xác minh quyền tệp vào/ra, lưu kết quả đúng pháp nhân trên Core thật |
| Ngăn engine/CAS, lượt bền #10, bí mật theo tên, trạng thái tương tác | Chưa cần cho parser XML thuần, không làm kho nội dung tạm | Chặn phần tải thật tới khi có cửa chung và Anh chốt; không nối pipe bí mật tự chế hoặc SQL để vượt SDK |
| Fixture/golden cũ được test tham chiếu nhưng không có trong bộ `ma-nguon` hiện tại | Dựng DEMO có đáp án độc lập; không khẳng định đã đối chiếu toàn bộ golden cũ | Lead bàn giao bộ fixture DEMO có nguồn và hash nếu cần chứng minh tương thích toàn bộ corpus |

Các mục này được ghi vào `e_hoa_don/docs/VIEC.md` để chuyển lead Core qua Anh. Không sửa tài liệu API/SDK, `_chung/tham-chieu-cong-hien-tai/`, mã Core hoặc tự thêm màn/bảng riêng.

### 5.2 Chờ Anh — câu hỏi và đề xuất (chưa phải quyết định)

| Mã | Câu hỏi cần Anh chốt | Đề xuất | Phương án khác / tác động | Phần phụ thuộc |
|---|---|---|---|---|
| Q1 | Quyết định cuối cho toàn engine có giới hạn mốc đầu ở XML kỹ thuật không? | Hoàn tất 5 lát XML/15 giờ ước tính theo phiếu này, giữ rõ cảnh báo/giới hạn profile; duyệt mở rộng riêng sau | Duyệt cả XML/ZIP/bảng kê/tải sau khi có đủ mẫu và cửa Core; phải lập lại giờ/phụ thuộc | Các lát XML nằm trong yêu cầu HD-P hiện tại; mở rộng **chờ Anh chốt** |
| Q2 | ZIP trả báo cáo theo tệp và định nghĩa “đầy đủ” thế nào? | Trình mẫu DEMO giữ ordinal/tên/hash từng entry, phân biệt lỗi/không hỗ trợ/trùng; coverage của gói khác độ đủ của kỳ tải | Chỉ nhận từng XML trước; không gộp XML trùng hoặc coi một tệp lỗi là gói đầy đủ | Lát ZIP/báo cáo **chờ Anh chốt**, chưa công bố `hoa_don.doc_zip_bang_ke@1` |
| Q3 | Bảng kê cần XLSX, PDF hay cả hai, mẫu cột và độ chính xác nào? | XLSX giữ chuỗi tiền exact + currency và số 0 đầu; PDF là bản xem, chỉ xuất khi đối chiếu strict không mất số, lỗi thì từ chối | Hoãn PDF vì parser hiển thị dùng Number/Intl và có miền không bảo toàn Decimal | Lát bảng kê/PDF **chờ Anh chốt**, không ghép vào năng lực XML |
| Q4 | Quyền dùng/đóng gói tập nguồn Node đã ghi CD-096 A1 có áp dụng bản giao SDK 2.0 mới không? | Lead đối chiếu lại đúng tập nguồn/bản/hash và xác nhận phạm vi dùng nội bộ đã ghi; không xin duyệt lại một quyền đã có đủ bằng chứng | Khi còn thiếu căn cứ cho phần nguồn mới thì giữ chờ, chỉ tiếp tục XML; không nạp job/portal/server chưa kiểm | Lát Node/portal **chờ Anh chốt**; metadata cũ không chứng minh nguồn tải thật đã đủ |
| Q5 | Phạm vi tải: pháp nhân, mua vào/bán ra, kỳ tháng, nhóm truy vấn và xử lý thiếu nhóm? | DEMO trước; kỳ trọn tháng, giữ lỗi/coverage từng nhóm, không suy COMPLETE từ sự kiện done; giữ riêng tải/đọc/nhận nghiệp vụ | Chưa đủ seam coverage/profile thì chỉ thử seam giả, không mở năng lực tải | Lát tải/phiên **chờ Anh chốt** và chờ Core, chưa công bố `hoa_don.tai_cong_thue@1` |
| Q6 | Tài khoản Windows, phiên có màn hình, CAPTCHA và vòng đời profile đặt ở đâu? | Tài khoản riêng khác Core/module/engine khác; CAPTCHA gõ tại máy chủ, profile riêng mỗi pháp nhân/phiên; dọn lỗi chặn phiên mới; bí mật qua cơ chế Core được duyệt, không env/args/tệp | Hoãn phần Windows, chỉ ghi bằng chứng giả; không yêu cầu Anh gửi mật khẩu qua chat | Lát Windows/Chromium và công cụ thử thật **chờ Anh chốt** |
| Q7 | Màn nghiệp vụ và cách kiểm kê/quyền tạm đặt ở đâu? | Dùng Chạy thử DEMO chung cho XML; quyền/hàng việc/kho tệp do Core, màn nghiệp vụ thuộc module. Lead trình cơ chế kiểm kê tạm để Anh chốt | Màn thử riêng Core DEMO nếu module chưa nối phải ghi chưa nghiệm thu nghiệp vụ; không làm UI riêng trong engine | Lát nối nghiệp vụ/màn/kiểm kê **chờ Anh chốt**, ngoài 15 giờ |
| Q8 | Khi nào được thử cổng thuế thật, phạm vi tài khoản và kỳ tải nào? | Chỉ sau DEMO và bằng chứng Windows/Core; Anh ra lệnh riêng có phạm vi. Công cụ mặc định chạy khô + `.cmd` ASCII để Anh tự chạy | Tiếp tục chỉ DEMO, chưa ước tính giờ tải thật khi thiếu điều kiện | Lát cuối thử thật **chờ Anh chốt**; HD-P và 5 lát XML không dùng tài khoản/cổng thật |

Không yêu cầu Anh trả lời các câu trên để hoàn tất HD-P. Các câu mở rộng giữ trạng thái chờ, không được hiểu phiếu giao này là quyết định cuối hay bằng chứng đã nối Core thật.
