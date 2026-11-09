# Engine OCR — dựng môi trường sạch

G3-GOI-20 · 07/11/2026. Phạm vi: ghim thư viện đang cài và nguồn vendor,
không cài/nâng gói hoặc xác nhận ABBYY/Tesseract nhận dạng thật.

## Môi trường Python

Mốc đã đo: **CPython 3.13.14, Windows x64**. Dùng cùng bản Python và các
wheel tương ứng khi tái lập. `requirements.lock` chứa **9 gói Python**
đã đo qua metadata, gồm cả dependency bắc cầu của pdfplumber. Giấy phép,
lý do dùng và trạng thái thiếu ở `NGUON.md`.

Các lệnh dưới là hướng dẫn cho người dựng trên môi trường sạch, thực hiện
từ thư mục gốc gói bàn giao/repo; chưa được chạy cài đặt trong lát này.
`python` là CPython đúng bản đã chọn; các đường dẫn đều là ví dụ tương đối.
Kho wheel sạch `wheelhouse` phải do lead chuẩn bị/kiểm nguồn trước.

```powershell
python -X utf8 -B -m venv .venv-ocr
& '.\.venv-ocr\Scripts\python.exe' -X utf8 -B -m pip install --no-index --find-links .\wheelhouse -r .\engines\e_ocr\requirements.lock
& '.\.venv-ocr\Scripts\python.exe' -X utf8 -B -m pip check
```

Không thêm `--require-hashes`: SHA-256 trong lock là hash **mã nguồn
vendor**, không phải hash wheel pip. Không sao chép toàn bộ site-packages
của máy phát triển hoặc dùng `pip freeze` toàn ứng dụng làm lock OCR.

SDK là phụ thuộc nền do lead cấp theo bản đã duyệt, được kiểm riêng với
gói OCR và namespace `kho_tri_thuc.sdk_core`. **Không ghim/cài/phát hành
wheel SDK 1.4.1 candidate** từ hướng dẫn này; không thay version SDK.
Việc chốt wheel phát hành thuộc lát 34, `KE-HOACH-G3-GOI.md` §6.3.

## Phần còn thiếu của nhánh nhận dạng

Lock tái lập được các gói của **PDF có lớp chữ và cắt ảnh**. Còn hai gói
**khai nhưng chưa cài/chưa dùng thật ở bản 1** trong môi trường đo:

- `pymupdf`: nguồn local-mask-ocr 2.1.0 khai `>=1.28.2,<2`; vendor
  import ngay và dùng cho OCR ảnh/render PDF dự phòng.
- `defusedxml`: nguồn khai `>=0.7.1,<1`; vendor/bộ đọc DOCX cần XML an toàn.

Các khoảng trên **không phải pin đã đo**. Lead cần chốt phiên bản/giấy
phép, cung cấp môi trường có hai gói và đo metadata trước khi cập nhật
lock ở lát được giao riêng. Không suy ra phiên bản đang cài từ cận dưới.
Chỉ cài 9 gói hiện ghim chưa làm parser DOCX hoặc nhánh mask_ocr sẵn sàng;
test dependency thật phải ghi `CHUA_KIEM/skip`, không đổi sang mock để
tuyên bố đã kiểm nhận dạng.

## Tesseract và tiếng Việt

`mask_ocr.extraction.image_text` dùng OCR Tesseract **tích hợp của MuPDF**
(`Pixmap.pdfocr_tobytes`), không import `pytesseract` và không chạy
`tesseract.exe` từ nhánh này. Không thêm pytesseract, VietOCR/Paddle/dual
hoặc chép worker/model legacy chỉ để dựng môi trường.

Để chuẩn bị triển khai, dùng bộ Tesseract native và bộ ngôn ngữ đã được
lead kiểm nguồn/giấy phép. Máy khảo sát báo CLI **5.5.3.20260724**, các
ngôn ngữ **vie, eng, osd**. Cần cả `vie.traineddata` và `eng.traineddata`
cho cấu hình `vie+eng`; bộ cài/model sạch chưa được ghim hash trong lát
này. Có thể kiểm thông tin bằng:

```powershell
tesseract --version
tesseract --list-langs
```

Đặt thư mục bộ cài được duyệt trên `PATH` chỉ khi cần dùng CLI kiểm tra.
`TESSDATA_PREFIX` là biến của Tesseract, nhưng **không được dùng làm
fallback bởi `runtime.tesseract_info` hiện tại**: vendor tìm model theo
quy tắc riêng và truyền `tessdata` tường minh vào MuPDF. Vì vậy, cài CLI
hoặc đặt biến này chưa đủ để bật nhánh nhận dạng của engine.

Vendor đọc cấu hình triển khai sạch do lead cấp qua
`LOCAL_OCR_DUAL_CONFIG` (JSON UTF-8, không chứa bí mật). Đường nhận dạng
chỉ cần `tesseract_language` và `models`; ví dụ nội dung:

```json
{
  "tesseract_language": "vie+eng",
  "models": "models"
}
```

Đường `models` tương đối với thư mục chứa JSON, phải có
`models/tessdata_best/vie.traineddata` và `eng.traineddata` trong cùng
thư mục `tessdata_best`. Một lựa chọn legacy khác là model đặt trong
`vendor/mask_ocr/mask_ocr/models` theo đúng phép ghép `ROOT` của runtime;
gói hiện không kèm model và không tự tải/chuyển model tới đó. Ưu tiên
cấu hình sạch tường minh để tránh phụ thuộc bố cục nguồn cũ.

Ví dụ đặt biến cho tiến trình triển khai (tệp mẫu phải được tạo riêng
trong khu vực sạch, không trỏ tới cấu hình thật):

```powershell
$env:LOCAL_OCR_DUAL_CONFIG = (Join-Path (Get-Location) 'ocr-demo/runtime.json')
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

Không cần `KTT_NGUON_OCR` hoặc thêm thư mục công cụ cũ vào `sys.path`.
Không gọi `runtime.settings`, `ready` hay OCR thật trong bài kiểm thuần:
chúng có thể đọc cấu hình/model. Sau khi đủ dependency/model, lead phải
thử nhận dạng DEMO để xác nhận Tesseract mà MuPDF thực dùng; phiên bản
CLI vừa đo không chứng minh engine đã chạy OCR đúng.

## ABBYY tùy chọn và kiểm tra

ABBYY là **cầu nối ngoài tùy chọn**, không cài bằng pip và không được
bundle cùng engine. Khi được cấu hình, lớp chọn nguồn ưu tiên ABBYY,
đọc PDF lớp chữ bằng pdfplumber; khi lỗi/hết hạn mức thì gọi mask_ocr.
Core cấp backend, quyền đọc tệp và sổ hạn mức; không đặt khóa, địa chỉ
thật hoặc đường dẫn bí mật vào tài liệu này. Kết nối ABBYY thật và thử
Windows thuộc lead/lát OCR-WIN-NT, chưa được kiểm ở lát 20.

Trong checkout phát triển đã có SDK nguồn, đặt môi trường thuần rồi chạy
đúng thư mục test OCR (không cần PostgreSQL/server):

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
$env:PYTHONDONTWRITEBYTECODE = '1'
& '.\.venv-ocr\Scripts\python.exe' -X utf8 -B -m unittest discover -s engines\e_ocr\tests -v
```

Kiểm closure import/lock và SHA vendor là kiểm tĩnh bằng stdlib. Các ca
PDF/ảnh dùng dữ liệu DEMO trong RAM; các ca OCR/ABBYY dùng mock. Test DOCX
dependency thật skip khi thiếu pymupdf/defusedxml. Kết quả xanh không thay
cho dựng môi trường sạch hoặc nghiệm thu nhận dạng thật.
