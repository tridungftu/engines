# Cài và nghiệm thu bốn engine — DONG-GOI-1

Ngày 15/11/2026. Tài liệu cho Anh trên máy Windows x64 mới, Python **3.13**.
Chỉ dùng Core tập và dữ liệu DEMO. Đây là **hướng dẫn để thực hiện**; các ô ảnh
đang trống, chưa có bằng chứng bấm trình duyệt hoặc lưu bền trên Core thật.
Các kiểm tự động trong lát này **đã kiểm bằng Core giả (CoreGia)**.

## 1. Chuẩn bị bản cài

Lead giao Core có SDK **2.2.0**, cổng ngăn engine/cấu hình, tài khoản Admin DEMO và cách khởi động lại Core.
Python chạy engine phải là môi trường Core chọn cho `{python}`; cài phụ thuộc
vào đúng môi trường đó, không chỉ vào Python đang mở ở terminal.
Đóng gói không bao gồm Core, PostgreSQL, Tesseract, ABBYY, model Local AI hay
wheel phụ thuộc ngoài SDK. Lead chuẩn bị riêng kho wheel CPython 3.13 Windows
x64 cho phụ thuộc OCR theo `requirements.lock`/`NGUON.md`; không cần mạng khi cài.

| Engine / phiên bản tại mốc giao | Cấu hình riêng | Ngăn nghiệp vụ / SQL cần cài |
|---|---|---|
| Hỏi AI `e_hoi_ai` 0.12.0 | Có | `model_phat_hien` / có |
| Nhận dạng văn bản `e_ocr` 1.0.9 | Có | `han_muc_ngay`, `luot_abbyy`, `trang_thai_engine` / có |
| Đọc XML hóa đơn `e_hoa_don` 1.0.0 | Không | Không / không |
| Trích thông tin hợp đồng `e_trich_xuat` 0.5.0 | Có | Không / không |

Cấu hình cả ba engine do Core lưu; không phải bảng nghiệp vụ ở trên. Không
tạo tệp cấu hình runtime trên máy engine. Không nhập khóa/mật khẩu vào cấu
hình, tài liệu hay ảnh. Địa chỉ, đường dẫn trong các lệnh dưới là **placeholder**,
không chép nguyên; chỉ dùng thông tin DEMO lead bàn giao tại máy cài.

## 2. Tạo bộ giao và kiểm SHA

Lead chạy từ gốc repo (git và Python chuẩn là đủ):

```powershell
python _chung/cong-cu/dong_goi.py --engine e_hoa_don --engine e_hoi_ai --engine e_ocr --engine e_trich_xuat --ra "<thu-muc-phat-hanh-ngoai-repo>" --nhan "<moc-giao>" --ref HEAD
```

`--engine` lặp được; `--ref` chọn commit/tag/nhánh, mặc định `HEAD`;
`--nhan` là nhãn bộ giao, không phải git ref. Công cụ chốt một commit cho
mọi gói và wheel, đọc blob git nguyên bytes, bỏ qua mọi sửa/chưa theo dõi trong
working tree. Lead cần đưa thay đổi engine vào git trước khi chọn mốc giao.
ZIP chứa một thư mục gốc đúng mã engine, không có tiền tố `engine/goi/`.
Thứ tự tên, timestamp 01/01/1980, quyền file 0644 cố định; ZIP_STORED để
không phụ thuộc zlib. Cùng commit và engine cho cùng SHA ZIP, bất kể nhãn.

Đầu ra phải mới/rỗng và ngoài repo. Ngoại lệ duy nhất là **`.dong-goi-thu` tại
gốc repo**, được Anh yêu cầu để chạy thử và đã gitignore; không giao thư mục
này vào git. Không ghi đè/trộn các bộ giao cũ. Công cụ kiểm tất cả gói trước
khi ghi: thiếu/thừa/lặp mục kiểm kê, sai phiên bản/bytes/SHA đều dừng.
Kiểm kê `sql/kiem_ke.json` phủ toàn gói trừ chính nó; không chuẩn hóa CRLF.

Danh sách cho phép: tệp gốc `engine.json`, `README.md`, `CHANGELOG.md`,
`NGUON.md`, `requirements.lock`, `cau_hinh.schema.json`, `.gitattributes`;
mã `.py`/`LICENSE` dưới đúng mã engine; JSON dưới `contract/`; dữ liệu DEMO
txt/json/xml/pdf/png/jpg/jpeg/docx/xlsx/zip/md dưới `demo/`; js/css/html dưới
`ui/`; `sql/NNN_ten_khong_dau.sql`, `sql/kiem_ke.json`. Từ chối liên kết git,
submodule, tên không an toàn/trùng hoa thường trên Windows và mọi tên chứa
`bi-mat`, `secret`, `token`, `password`, `.env*`, `.venv`, `__pycache__`,
`.pytest-tmp*`, `.pytest_cache`, `LUU-TRU`, `.pyc`/`.pyo`, dù trong nhánh được phép.
Không âm thầm lọc tệp rồi tiếp tục phát hành.

Bộ giao có bốn ZIP, wheel SDK, `SHA256SUMS.txt`, `DANH-SACH-GOI.json`.
JSON ghi tên/mã/phiên bản/SDK/năng lực, có ngăn/SQL, tên ZIP, SHA và commit.
Lead gửi SHA/commit qua kênh bàn giao tin cậy để Anh đối chiếu; tệp SHA nằm
cạnh ZIP tự nó chỉ phát hiện thay đổi, không xác thực người phát hành.

Tại thư mục nhận bộ giao, kiểm **mọi ZIP và wheel** trước khi giải nén/cài:

```powershell
Get-Content SHA256SUMS.txt | ForEach-Object {
    $phan = $_ -split '  ', 2
    $bamGiao = $phan[0]
    $tenGiao = $phan[1]
    $bamNhan = (Get-FileHash -LiteralPath $tenGiao -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($bamNhan -ne $bamGiao) { throw 'SHA-256 không khớp; dừng cài.' }
    Write-Host "ĐẠT $tenGiao"
}
```

SHA wheel SDK phải là
`0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`.
Giải nén từng ZIP bằng Explorer → **Extract All / Giải nén tất cả**, vào
thư mục engine ngoài mã Core. Chọn thư mục con có `engine.json` khi cài Core;
giữ nguyên bytes và giữ thư mục này lâu dài vì Core chạy engine từ đây.

## 3. Kiểm SDK và cài phụ thuộc OCR

Dùng đúng Python Core chọn cho `{python}`. Hỏi AI, Trích xuất và Hóa đơn chỉ
cần SDK 2.2.0 và các phụ thuộc của SDK đã có trong môi trường Python của Core.
Kiểm tra phiên bản SDK phải in **2.2.0**:

```powershell
& "<python-core>" -c "import kho_tri_thuc_sdk;print(kho_tri_thuc_sdk.__version__)"
```

OCR có phụ thuộc riêng được ghim hash; cài vào cùng Python Core từ kho wheel
đã chuẩn bị, rồi kiểm tra phụ thuộc. Đặt `PYTHONDONTWRITEBYTECODE=1` trong
môi trường Core trước khi chạy engine để tránh sinh bytecode trong gói.

```powershell
& "<python-core>" -m pip install --require-hashes --no-deps --no-index --find-links "<kho-wheel-da-kiem>" --find-links "<bo-giao>" -r "<goi-e_ocr>\requirements.lock"
& "<python-core>" -m pip check
```

Nếu phiên bản SDK sai hoặc `pip check` chưa đạt thì dừng trước khi Bật engine.

## 4. Cài và Bật engine

Theo CĐ-36, Core main `0ebd632` đã được lead bấm thử. Trước lần đầu cài engine
có ngăn trên Core tổng, **lead** khóa cấu hình tiến trình cài
`tien_trinh_cai.thu_muc_engine` bằng `.cmd` riêng do lead soạn và thực hiện.

Trên trình duyệt, thực hiện tuần tự cho cả bốn gói:

| Bước | Thao tác BẤM | Kết quả mong đợi | Ô chụp ảnh / kết quả thực tế |
|---|---|---|---|
| C1 | Đăng nhập Admin DEMO → Quản trị Core → Quản lý engine | Mở danh sách engine, đúng Core tập | ☐ Ảnh: …; đạt/chờ: … |
| C2 | Bấm Xem trước gói → chọn **thư mục gói đã giải nén** có `engine.json` | Đúng tên, phiên bản và năng lực trong DANH-SACH-GOI.json | ☐ Ảnh: …; đạt/chờ: … |
| C3 | Bấm Duyệt cài | Tiến trình cài C4 tự cài ngăn cho gói có `sql/` (Hỏi AI, OCR); màn hiện “Đang cài ngăn dữ liệu…” | ☐ Ảnh: …; đạt/chờ: … |
| C4 | Tải lại màn sau khi cài, rồi bấm Bật | “Cấu hình: Bật, Vận hành: Sẵn sàng” | ☐ Ảnh: …; đạt/chờ: … |
| C5 | Với AI/OCR/TX, bấm Cấu hình | Màn cấu hình riêng hiển thị; không có mục này thì ghi **Cần Core**, dừng ca phụ thuộc | ☐ Ảnh: …; đạt/chờ: … |

Phải tải lại màn để thấy nút Bật sau khi cài ngăn; đây là nợ Core đã biết.
Các lối Cấu hình, chi tiết kết quả và tải tệp bên dưới là **yêu cầu nghiệm thu**;
chỉ đánh đạt sau khi thấy trên bản Core thật. Không dựng URL riêng hoặc gọi API
để thay thao tác BẤM.

## 5. Nhập cấu hình qua màn engine

Nguồn đúng là `cau_hinh.schema.json` trong từng ZIP. Phân biệt schema
`required` với điều kiện để nguồn ngoài hoạt động:

| Engine | Trường phải nhập / quy tắc | Giá trị DEMO và thao tác lưu |
|---|---|---|
| Hỏi AI | Gốc không có required; để hỏi phải có `local_ai`. Khi có, **`url`, `timeout_giay` bắt buộc**; timeout >0, ≤600. `quy_tac_model` mặc định `[]`; mỗi quy tắc đủ `mau_ma_prompt`, `uu_tien`, `du_phong` (mảng, có thể rỗng) | Cổng Local AI → Địa chỉ máy Local AI: `http://<IP-noi-bo-may-Local-AI>:<cong>`; thời hạn 60 → Lưu. Địa chỉ DEMO loopback minh họa: `http://127.0.0.1:12345`, chỉ có tác dụng nếu server tại đó. Model phát hiện sau lượt hỏi; tải lại màn rồi Thêm quy tắc nếu cần. Cloud hiện “Chưa áp dụng ở bản 1” |
| OCR | Schema không có required, có mặc định. `abbyy.bat=false`; muốn bật cần hai đường tuyệt đối **khác nhau**, đã có và truy cập được: `thu_muc_vao`, `thu_muc_ra`; `thoi_han_giay` nguyên 1–900 (900); `han_muc_trang_30_ngay` nguyên 0–5000 (5000). `tesseract.duong_dan` có thể rỗng để tự tìm; `ngon_ngu` chỉ `vie`, `eng`, `vie+eng`, `eng+vie` | Cấu hình OCR → Tesseract dự phòng: `<tep-tesseract.exe-DEMO>` và Tiếng Việt + Tiếng Anh → Lưu cấu hình. Chỉ bật ABBYY sau khi Anh kiểm Hot Folder DEMO; nhập thư mục nhận/trả và lưu. Không dùng thư mục Hot Folder đang xử lý hồ sơ thật |
| Trích xuất | **`ngan_sach_token_vao_toi_da` bắt buộc**, nguyên 1024–100000, default 16000 | Cấu hình → Trần ngân sách đầu vào AI: 16000 → Lưu. Đây là ước lượng, không phải context đo thật của model |
| Hóa đơn | Không khai schema hoặc màn cấu hình | Không nhập cấu hình, không tạo ngăn |

IP Local phải là IP trực tiếp nội bộ/loopback hoặc Tailscale được engine
chấp nhận, không dùng DNS/public/proxy. Local AI cần có model thực sự khả dụng.
Tesseract cần executable Windows x64 và gói ngôn ngữ `vie`/`eng`; không đóng
chúng trong ZIP. ABBYY cần FineReader Corporate hợp lệ, task Hot Folder nhận
tệp rồi xuất PDF có lớp chữ đúng mã; quyền tạo/dọn tạm ở cha thư mục vào.
Chỉ dùng dữ liệu giả; không chụp ảnh có đường dẫn vận hành, khóa hay mật khẩu.

## 6. Nghiệm thu BẤM từng engine

Ghi ở **mọi hàng**: đạt/chưa đạt/chưa kiểm, thời điểm, tên ảnh. Ô ảnh trống
không là đạt. Lỗi nguồn hoặc “chưa rõ” không được ghi XONG; không gửi lại mù.
Trước khởi động lại, chờ việc kết thúc; lead dùng cách restart Core được bàn
giao, sau đó Anh đăng nhập lại trên trình duyệt. Không có nút restart Core
nào được giả định trong tài liệu này.

### Hỏi AI

| Bước | Thao tác BẤM | Kết quả mong đợi | Ô chụp ảnh / kết quả thực tế |
|---|---|---|---|
| AI1 | Quản lý engine → Hỏi AI → Cấu hình → nhập Local → Lưu | Báo đã lưu; tải lại trang vẫn đúng cấu hình; Cloud chưa áp dụng | ☐ Ảnh: …; kết quả: … |
| AI2 | Hỏi AI → Chạy thử DEMO (màn chung) → “Hỏi số tiền và ngày thanh toán DEMO” → Chạy → mở kết quả | 1.000.000 VND và 30/10/2026 có trích dẫn nguồn; chỉ Local. Kết quả model khác phải soát, không tự đánh đạt | ☐ Ảnh: …; kết quả: … |
| AI3 | Chọn “Hỏi người bảo lãnh không có trong tài liệu DEMO” → Chạy → mở kết quả | Không thấy căn cứ, `co_can_cu=false`; không bịa người bảo lãnh | ☐ Ảnh: …; kết quả: … |
| AI4 | Chọn “Trích tiền và ngày theo khuôn DEMO” → Chạy → mở kết quả | Tiền có VND, ngày dữ liệu `2026-10-30`, dẫn chứng được kiểm; có căn cứ mới đạt | ☐ Ảnh: …; kết quả: … |
| AI5 | Quay Cấu hình → tải lại → ghi nhận danh sách Model đã phát hiện | Có catalog từ `model_phat_hien`; trạng thái là lần kiểm gần nhất | ☐ Ảnh trước restart: … |
| AI6 | Sau lead restart Core: đăng nhập → Quản lý engine → Hỏi AI → Cấu hình, rồi mở lại kết quả AI2 và chạy việc DEMO mới | Cấu hình và model catalog còn, kết quả cũ còn trong Core; việc mới hoạt động. Đây là kiểm ngăn thật qua restart | ☐ Ảnh sau restart: …; kết quả: … |

### OCR

| Bước | Thao tác BẤM | Kết quả mong đợi | Ô chụp ảnh / kết quả thực tế |
|---|---|---|---|
| OCR1 | Nhận dạng văn bản → Cấu hình → chọn Tesseract/ngôn ngữ → Lưu cấu hình → Tải lại cấu hình | Giá trị đã lưu còn; trạng thái/hạn mức hiển thị hoặc ghi rõ phần lỗi | ☐ Ảnh: …; kết quả: … |
| OCR2 | Chạy thử DEMO → lần lượt chọn hai mẫu “Đọc tài liệu có vị trí” (PDF quét 3 trang, PNG 1 trang) → Chạy từng mẫu → mở kết quả | Đủ 3/1 trang, nguồn Tesseract, có vị trí; đối chiếu tiền/ngày với ảnh gốc. Không tự hiệu đính | ☐ Ảnh PDF/PNG: …; kết quả: … |
| OCR3 | Chọn từng mẫu “Đọc văn bản thuần” PDF/PNG → Chạy → mở kết quả | Trả chuỗi đủ trang theo nguồn, không mất trang/âm thầm cắt | ☐ Ảnh PDF/PNG: …; kết quả: … |
| OCR4 | Chọn từng mẫu “Xuất Word giữ bảng” PDF/PNG → Chạy → bấm tải kết quả → mở DOCX | Có DOCX tải được; so chữ và bố cục với nguồn. Bảng chỉ có trong ảnh chưa được tái tạo, cảnh báo phải được giữ | ☐ Ảnh kết quả/Word: …; kết quả: … |
| OCR5 | Sau khi Anh kiểm ABBYY thật: mở Cấu hình → bật ABBYY → Lưu. Trên màn quy trình DEMO Core đã chuẩn bị, chọn nguồn “Chỉ ABBYY”, tải PDF DEMO → Chạy → mở kết quả; quay Cấu hình | Lượt thực qua ABBYY; trang đã dùng/còn lại thay đổi đúng một lần; ngăn `han_muc_ngay`, `luot_abbyy`, `trang_thai_engine` có dữ liệu. Sáu DEMO mặc định chỉ Tesseract **không** chứng minh sổ ABBYY | ☐ Ảnh kết quả/hạn mức trước restart: … |
| OCR6 | Sau lead restart Core: đăng nhập → Nhận dạng văn bản → Cấu hình → đối chiếu hạn mức/lượt chưa rõ và mở lại kết quả OCR5 | Sổ ngăn còn sau restart, không về 0, không gửi lại lượt dở. Cùng ngày/cửa sổ 30 ngày để so số; nếu chưa chạy OCR5 thì ca lưu ngăn **chưa kiểm** | ☐ Ảnh sau restart: …; kết quả: … |

OCR5 cần màn quy trình và chọn pháp nhân DEMO do lead chuẩn bị, không sửa
sáu mẫu manifest Tesseract. Danh sách chưa rõ chỉ hiển thị số đếm; chưa có
lượt thì không bịa mẫu để đánh đạt. Kiểm chống trùng/crash/ACL thực giữ ở
phiếu OCR; tài liệu chung không nhận thay nghiệm thu ABBYY/model thật.

### Hóa đơn

| Bước | Thao tác BẤM | Kết quả mong đợi | Ô chụp ảnh / kết quả thực tế |
|---|---|---|---|
| HD1 | Đọc XML hóa đơn → Chạy thử DEMO → “DEMO 0000123 — tiền nguyên” → Chạy → mở kết quả | Số hóa đơn giữ `0000123`; ngày 30/10/2026; 1.000.000 VND + 100.000 VND = 1.100.000 VND, có cảnh báo cần kiểm tra ngữ cảnh | ☐ Ảnh: …; kết quả: … |
| HD2 | Chọn “DEMO 0000123 — tiền lẻ exact” → Chạy → mở kết quả | Tổng dữ liệu `1100000.135801` VND, không làm tròn/mất số 0 đầu | ☐ Ảnh: …; kết quả: … |
| HD3 | Chọn “DEMO thiếu nguồn — null và cảnh báo” → Chạy → mở kết quả | Trường thiếu là null/cảnh báo, không suy thành 0 | ☐ Ảnh: …; kết quả: … |
| HD4 | Chọn “DEMO ZIP hỗn hợp — giữ tệp lỗi và trùng” → Chạy → mở/tải JSON chi tiết | 5 tệp/1 thư mục, 3 đọc được/1 lỗi/1 chưa hỗ trợ/1 trùng nội dung; `da_doc_het=false`, `can_kiem_tra=true` | ☐ Ảnh: …; kết quả: … |
| HD5 | Nếu lead có quy trình DEMO đọc XML/ZIP → Bảng kê XLSX: chọn tệp → Chạy → bấm tải bảng kê → mở XLSX | Hai sheet “Hoa don”, “Kiem ke tep”; giữ tiền exact/VND, mã 0 đầu, lỗi/trùng. Manifest chưa có DEMO XLSX độc lập; thiếu quy trình thì ghi chưa kiểm | ☐ Ảnh Excel: …; kết quả: … |
| HD6 | Sau lead restart Core: đăng nhập → mở lại kết quả HD1/HD4, tải tệp cũ | Core còn lịch sử/tệp; engine này không có ngăn nghiệp vụ, ghi **không áp dụng kiểm ngăn** | ☐ Ảnh sau restart: …; kết quả: … |

Đọc kỹ thuật thành công không xác nhận tính hợp lệ thuế, đủ hóa đơn kỳ hay
đã ghi nhận kế toán. PDF và tải cổng thuế chưa hỗ trợ trong bản này.

### Trích xuất

| Bước | Thao tác BẤM | Kết quả mong đợi | Ô chụp ảnh / kết quả thực tế |
|---|---|---|---|
| TX1 | Trích thông tin hợp đồng → Cấu hình → nhập 16000 → Lưu → tải lại | Ngân sách còn đúng; không có bảng ngăn nghiệp vụ/SQL cần cài | ☐ Ảnh: …; kết quả: … |
| TX2 | Chạy thử DEMO → “Đọc hợp đồng DOCX DEMO” → Chạy → mở kết quả | Văn bản/cấu trúc từ DOCX; vị trí theo đoạn, không bịa trang | ☐ Ảnh: …; kết quả: … |
| TX3 | Chọn “Chấp nhận Track Changes DOCX DEMO” → Chạy → mở kết quả | Văn bản theo Accept All; tệp gốc không đổi | ☐ Ảnh: …; kết quả: … |
| TX4 | Chọn “Chuẩn bị đủ trường từ snapshot DEMO” → Chạy → mở kết quả | Yêu cầu AI đúng snapshot và hồ sơ đã tải Core; bước này không tự gọi AI | ☐ Ảnh: …; kết quả: … |
| TX5 | Chọn “Hậu kiểm độc lập từng ô DEMO” → Chạy → mở trạng thái | Cần Core cấp tệp tham chiếu C-TX-06. Nếu thiếu tệp/đứng DANG_CHAY: ghi chưa đạt, không sửa ID hay bỏ ca. Khi được cấp thật, hậu kiểm phải có dẫn chứng đúng từng ô | ☐ Ảnh: …; kết quả: … |
| TX6 | Chọn “Xuất đủ JSON và Excel DEMO” → Chạy → bấm tải cả hai tệp | Hai tệp hợp lệ; 2 tham số, 0 cần soát theo fixture; JSON chuẩn có dẫn chứng, không dùng `phan_hoi_ai` làm kết quả đã duyệt | ☐ Ảnh/tệp: …; kết quả: … |
| TX7 | Sau lead restart Core: đăng nhập → Cấu hình → kiểm ngân sách; mở lại kết quả TX6 và tải hai tệp | Cấu hình/lịch sử/tệp Core còn. Không có ngăn nghiệp vụ TX nên phần đó không áp dụng; không nhận thay kiểm toàn chuỗi Local AI | ☐ Ảnh sau restart: …; kết quả: … |

## 7. Phần chưa hỗ trợ và việc Anh tự chạy

| Cần Core/SDK hoặc lead | Ảnh hưởng / cách ghi nghiệm thu |
|---|---|
| Cấu hình cho CLI `chay_thu_demo` | CLI 2.2.0 tự tạo CoreGia rỗng, chưa nạp cấu hình và Local giả; lỗi CLI không chứng minh UI cấu hình thật lỗi, cũng không được đổi thành đạt. Hỏi AI cần cấu hình; OCR cần ngăn/cấu hình/nguồn cục bộ phù hợp |
| Tệp tham chiếu DEMO C-TX-06 | CLI chưa đăng ký tệp hậu kiểm nằm trong phong bì `tra_loi_ai`; giữ đủ 5 mẫu, ghi đúng trạng thái chưa đạt |
| Kiểu `json` trong ngăn | SDK 2.2.0 chưa nhận; AI `api` và OCR `da_nhan`/`dang_giu`/`theo_ngay` dùng JSON text qua `van_ban` ≤64 KiB. Không tự đổi kiểu cột |
| `giao_dien_quan_tri` | Schema manifest 2.2.0 chưa nhận khóa này. Lead Core cần nạp/review ba màn `ui/cau_hinh.js`, thống nhất `KttCore.engine(ma)`, quyền Admin và dạng trả cấu hình; OCR/TX dùng `gia_tri`, AI dùng `cau_hinh`. Không thấy màn thì ghi Cần Core, không tự thêm khóa manifest |
| Phụ thuộc OCR | Lead chuẩn bị kho wheel đã kiểm hash theo lock OCR cho Python Core |
| Tệp DEMO lồng trong `truong` của Hóa đơn | Chưa có DEMO XLSX độc lập trên màn chung, dùng quy trình DEMO Core chuẩn bị để kiểm HD5 |

Các công cụ sau nằm **ngoài ZIP runtime**, lead giao riêng cùng đúng mốc mã
và README/fixture của chúng. Anh tự chạy; lát này không kết nối máy AI,
không chạy ABBYY thật, không thay đổi Windows:

| Công cụ .cmd từ repo | Mục đích / điều kiện |
|---|---|
| `e_hoi_ai\cong-cu\THU-LOCAL-AI-THAT.cmd` | Kiểm Local AI thật, nhận URL qua dòng lệnh; chỉ Local, không Cloud |
| `e_ocr\cong-cu\KIEM-TESSERACT.cmd` | Kiểm executable/ngôn ngữ; không tự tải/cài Tesseract |
| `e_ocr\cong-cu\THU-ABBYY-THAT.cmd` | Mặc định chạy khô; chỉ `--that --cau-hinh <JSON-DEMO-Anh-chi-dinh>` mới thử Hot Folder. Tệp cấu hình này chỉ của công cụ kiểm, không phải cấu hình runtime |
| `e_trich_xuat\cong-cu\DO-SUC-CHUA-MODEL.cmd` | Đo T3 sau khi có model, cấu hình, bộ DEMO/biên bản E6 đúng mốc; chạy khô không chứng minh tải thật |
| `e_trich_xuat\cong-cu\CHAY-N1-MOT-LAN.cmd` | Đo N1 đúng một lần với nền lead đã duyệt; không xóa dấu/đổi nền để chạy lại lựa số |

Biên bản Anh điền: ngày/giờ …; commit …; SHA bộ giao đã đối chiếu …;
Core/Python/SDK …; người chạy …; từng hàng ảnh/kết quả …;
ca chưa đạt/chưa kiểm và lý do …; thời điểm restart …; kết luận … .
