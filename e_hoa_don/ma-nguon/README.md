# e_hoa_don — Đọc hóa đơn XML

**G3-GOI-26, 06/11/2026: hồ sơ nguồn và phụ thuộc đã cập nhật sau G3-GOI-25;
ghim phát hành còn CHUA_KIEM.** SDK 1.4.1 chỉ là candidate theo
[kế hoạch §6.3](../../docs/47-core/g3/KE-HOACH-G3-GOI.md#63-điều-kiện-từ-lát-04-opus-review-05112026).
`requirements.lock` hiện chỉ ghi các điều kiện chờ, chưa phải lock cài đặt.
Chưa có bằng chứng gói Python chạy độc lập chỉ với wheel SDK.

## Năng lực và bố trí gói

Manifest giữ phiên bản `0.1.0-demo.1`, adapter cùng phiên bản; Python distribution
trong `pyproject.toml` giữ `0.1.0.dev1`. Hai cách ghi thuộc hai loại metadata,
không phải phiên bản SDK; lát này không thay phiên bản.

| Thành phần | Phạm vi hiện có |
|---|---|
| `hoa_don.doc_xml@1` | Capability duy nhất được công bố: vào `tham_chieu_tep.v1`, ra `hoa_don.v1`. Giữ XML strict, số hóa đơn, Decimal và dấu vết nguồn. |
| `lib/hoa_don_xml.py`, `lib/trang_thai.py` | Bộ đọc XML/ZIP và ánh xạ trạng thái nội bộ. Bridge legacy giữ cùng module/class/object và hash bằng chứng. ZIP nội bộ chưa có nghĩa đã công bố capability ZIP. |
| `bang_ke.cjs`, `vendor/build.js`, `vendor/config.js` | Nguồn xuất bảng kê/PDF đã nằm trong gói theo CD-096 A1. Wrapper nạp tương đối và kiểm SHA hai tệp vendor trước require. Test Excel dùng XLSX trong RAM; PDF dùng Chromium giả. |
| `portal.cjs`, `phien.py` | Seam tải/phiên DEMO. Nguồn job/portal thật, tài khoản Windows, ACL, profile và Chromium thật còn CHUA_KIEM. |
| `contract/` | Phân phối schema đã có: `chung.v1`, `tham_chieu_tep.v1`, `hoa_don.v1`; ví dụ là dữ liệu giả. Chưa công bố capability bảng kê/PDF/tải mới. |

Mã nằm ở `engines/e_hoa_don/`; shim tại
`src/kho_tri_thuc/engines/e_hoa_don/__init__.py` chỉ đặt `__path__`, giữ tên
`kho_tri_thuc.engines.e_hoa_don`. Core dùng điểm vào
`kho_tri_thuc.engines.e_hoa_don.chay` từ manifest. Discovery đọc manifest/contract,
không import implementation. Bí mật chỉ qua stdin/handle theo hồ sơ Core cấp.

## Phụ thuộc và điều kiện ghim cuối

Môi trường đo regression: **Python 3.13.14**, **Node v24.18.0**; yêu cầu khai báo
hiện tại là Python ≥3.11 và Node ≥20. Đây là bản đã dùng kiểm, không phải chứng
nhận mọi bản trong khoảng đều tương thích.

Node đã có `package-lock.json` v3, ghim **exceljs 4.4.0**, **fast-xml-parser 4.5.7**,
**playwright 1.62.1** cùng 102 entry thư viện; giữ resolved/integrity của nguồn.
Metadata Chromium: revision **1234**, bản **151.0.7922.34**, chưa kiểm cài/chạy.
Quyền dùng nội bộ, nguồn gốc, SHA LF/CRLF và khác biệt duy nhất ở require config
được ghi tại [NGUON.md](NGUON.md). Không có bước cài npm hoặc tải browser trong
bộ kiểm thuần bên dưới.

Python reader dùng stdlib XML/ZIP/Decimal và SDK. `chay.py`/`phien.py` đã chuyển
các helper có tương đương sang SDK ở lát 24, nhưng còn hai ngoại lệ:

| Tệp | Import ngoài SDK còn tồn tại | Điều kiện còn thiếu |
|---|---|---|
| `chay.py` | `kho_tri_thuc.nguon.trich6_host.env_con` | Helper chèn đường dự án chưa có tương đương SDK được duyệt. |
| `phien.py` | `kho_tri_thuc.core.kiem_tra_tien_trinh.kiem_tra_tien_trinh` | Kiểm tiến trình thật thuộc Core; chưa có port SDK tương đương. |

Các lớp giữ `__module__` legacy để hash bằng chứng không đổi; cần kiểm lại
pickle/type hints với wheel cuối theo §6.3. Test identity trong repo không thay
thế kiểm độc lập. `pyproject.toml` hiện chưa cấu hình packages/package-data,
`dependencies` còn rỗng; không dùng nó để kết luận đã build/cài được engine.

Lead cần chốt SDK sau G3-GOI-34, exact version và SHA wheel cùng closure phụ
thuộc thực dùng rồi hoàn thiện `requirements.lock`. Builder SDK hiện khai
`cryptography==49.0.0`, `jsonschema>=4.18,<5`; đây là metadata của candidate,
chưa phải lock cuối. Không kéo extra PostgreSQL vào engine. Hai ngoại lệ import
và cấu hình build cần handoff đúng tệp trước khi kiểm wheel độc lập ở G3-GOI-38.
Windows/Chromium thật, gate nạp gói §6.1/6.5 và registry/pins do lead kiểm riêng;
tải từ cổng thuế thật vẫn cần lệnh riêng.

## Kiểm thuần trước và sau

Chạy từ gốc worktree, dùng đúng runtime được cấp. Với HD-3a, chỉ chọn
`HDThuanTest`; không chạy `HDTienTrinhTest` vì nhóm đó mở socket/Node/Job thật.

```powershell
$goc = (Get-Location).Path
$env:PYTHONPATH = $goc + '\src;' + $goc + '\tests;D:\Claude\Phan mem ho tro ke toan\Phần mềm kho tri thức\var\app-runtime\app-runtime-20261019-092310-807\deps'
$env:PYTHONDONTWRITEBYTECODE = '1'
& 'D:\KTT-CD060-DEMO\python313\python.exe' -X utf8 -B -m unittest `
  engines.e_hoa_don.tests.test_doc_lap `
  tests.test_g3_goi_hd_move tests.test_g3_goi_hd_reader tests.test_g3_goi_hd_anh_xa `
  tests.test_g3_hd_1 tests.test_g3_hd_2a tests.test_g3_hd_3a.HDThuanTest `
  tests.test_g3_hd_3b tests.test_hoa_don_xml tests.test_xs3_hoa_don `
  tests.test_g3_goi_import_sach tests.test_g3_goi_ham_thuan
node engines\e_hoa_don\tests\nguon.cjs
$env:NODE_PATH = 'D:\Claude\Phan mem download hoa don\node_modules'
$env:KTT_PYTHON = 'D:\KTT-CD060-DEMO\python313\python.exe'
node tests\g3_hd_2b.cjs
```

Bộ kiểm trên bao gồm manifest/contract offline, identity/import sạch, XML/ZIP,
Decimal/raw bytes/hash, ACK/lease/phiên giả, Node closure/integrity và XLSX/PDF
DEMO. Ghi riêng ok/FAIL/ERROR/skip trước và sau, không suy thành nghiệm thu vận
hành Windows hoặc bằng chứng package độc lập.

## Ghim và quay về bản đã kiểm

Sau khi đủ các điều kiện trên, lead dùng cơ chế Core hiện có tính `ma_bam_goi`
trên đúng thư mục gói hoàn chỉnh, gồm tài liệu, lock, tests và CJS; đối chiếu root
với `__path__` shim và chặn `__pycache__`. Các SHA nguồn trong `NGUON.md` không
thay mã băm toàn gói. Chưa ghi pin phát hành cho snapshot hiện tại.

Khi đổi bản, lead giữ bản đã ghim tương thích để quay lại; drain bản đang chạy,
chờ Core ACK các kết quả/việc đang giữ rồi mới chuyển pin và hồ sơ chạy. Không
ghi đè thư mục gói đang chạy; giữ phiên bản công việc cũ và kiểm lại hash,
capability, readiness của bản được chọn. Nếu SHA nguồn lệch hoặc còn việc chưa
ACK thì giữ chặn chuyển bản, báo lead; không sửa SHA để chấp nhận nguồn lạ.
