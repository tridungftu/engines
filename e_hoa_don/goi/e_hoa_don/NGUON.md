# NGUON — gói XML/ZIP/XLSX e_hoa_don

Nguồn nội bộ trong repo; không truy cập nguồn ngoài hoặc tự đặt giấy phép mới. HD-7 tham chiếu tĩnh nguồn Node theo quyền CD-096 A1 chỉ nội bộ, xem mục HD-7; không nạp Node/portal hoặc suy thành quyền phân phối bên ngoài. Runtime hiện hành chỉ stdlib và SDK 2.2.0; không thêm dependency ngoài SDK. Các bảng HD-0…HD-6 giữ mốc lịch sử.

| Nguồn tương đối từ gốc repo | Đích tương đối trong gói | Cách chuyển |
|---|---|---|
| `e_hoa_don/ma-nguon/lib/hoa_don_xml.py` | `e_hoa_don/hoa_don_xml.py` | Chép nguyên thuật toán, chỉ đổi hai import `kho_tri_thuc.sdk_core.primitives` và lazy `kho_tri_thuc.sdk_core.engine_legacy.Issue` sang `kho_tri_thuc_sdk`; chuẩn hóa LF. Giữ `__module__` legacy làm dấu vết, không shim/sys.modules/pickle. |
| `e_hoa_don/ma-nguon/doc.py` | `e_hoa_don/doc.py` | Tận dụng `_text`, kiểm đầu hóa đơn và miền tiền 18/6; viết phép chiếu trường SDK và báo cáo `ra_json`. Không chép vòng UUID/cap_tham_chieu hoặc contract hoa_don.v1. |
| `e_hoa_don/ma-nguon/lib/trang_thai.py` | `e_hoa_don/doc.py` | Tận dụng gate `shape != SUPPORTED_SUBSET` cho lỗi đọc; thiếu context chuyển thành cảnh báo dữ liệu theo phiếu HD-0, không chép enum/CHO hoặc ánh xạ ZIP. |
| `docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_doc_tep` và `e_demo_dem_tu` | `e_hoa_don/chay.py`, `engine.json` | Tham khảo mẫu SDK 2.0; không lấy fallback import Core. |
| `e_ocr/goi/e_ocr/e_ocr/cau_hinh_may.py`, `e_ocr/tests/kiem_doc_lap.py` | `e_hoa_don/cau_hinh_may.py` và kiểm ngoài gói | Tham khảo mẫu cấu hình ngoài gói, AST/cây tệp; thu gọn cấu hình HD-0 và thêm tiến trình sạch, kiểm dynamic/lazy. |
| `e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md` §2 và đầu bài HD-0 | Các tệp mới còn lại | Viết mới theo phạm vi đã giao, không đổi API/SDK. DEMO hoàn toàn giả. |

SDK: wheel `docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl`, phiên bản 2.0.0, SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`, khớp `SHA256SUMS.txt`, cài offline `--no-index --no-deps`. Không chép wheel hoặc test tools vào gói. Không phân phối nguồn Node/Chromium/vendor/shim hoặc các schema `.v1` cũ.

Các SHA dưới đây tính trên bytes thực; cột LF chỉ đổi CRLF thành LF, không chuẩn hóa Unicode. Tệp mới trong worktree đang dùng UTF-8 không BOM/LF; Git checkout khác kiểu xuống dòng sẽ đổi SHA bytes, so cột LF để đối chiếu nội dung. Không dùng hash này để bỏ qua kiểm thay đổi mã. Danh mục gói không tự băm `NGUON.md`.

## Nguồn tham chiếu

| Tệp nguồn | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `e_hoa_don/ma-nguon/lib/hoa_don_xml.py` | `00f7ca777b65f3434bd89efc8a618709531bcf3d143bf45dc5cb35245c2ca3af` | `2a757150d69ef24d7369621b22f6c25895867005ca167655813c91700e600f2b` |
| `e_hoa_don/ma-nguon/doc.py` | `a66dea667d2690f790c42e7684548d4015299a4dcb86f318bd36854df59dd5a9` | `4ce7dcb5ec02a62c4bc762c2ffa8a52359cbb9bd65f9ad2bb8e7313a74bd0d8b` |
| `e_hoa_don/ma-nguon/lib/trang_thai.py` | `d1cacb693a5b74c987605f08f9c8f2f89978cb4b8e4a1a6cb4ed73807f59ae82` | `66a24f1afe6a8771713c1ed1344e2f5b86f33aa4ce88f0952b037f068209b3f8` |

## Gói HD-0 tại mốc bàn giao (lịch sử)

| Tệp trong gói | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `CHANGELOG.md` | `97981e3e905784ca7be7ba85bf35e36a6c0a30d5f96936f5ea7be2c3383fdf95` | `97981e3e905784ca7be7ba85bf35e36a6c0a30d5f96936f5ea7be2c3383fdf95` |
| `contract/bao_cao_xml.schema.json` | `480c43d9ad9226922e28da3d94c56056df70d7318146fd812dbd0dede8368d12` | `480c43d9ad9226922e28da3d94c56056df70d7318146fd812dbd0dede8368d12` |
| `contract/cau_hinh_may.schema.json` | `195eb425011f09b51bd0890689156f0fa4b07660ebd6dc01f54769176abea2b4` | `195eb425011f09b51bd0890689156f0fa4b07660ebd6dc01f54769176abea2b4` |
| `demo/hoa-don-DEMO.xml` | `06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe` | `06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe` |
| `e_hoa_don/__init__.py` | `168c1ace3c34e2faed85d57f601633d46d492896f56b4f2acd8fcb727f03f78c` | `168c1ace3c34e2faed85d57f601633d46d492896f56b4f2acd8fcb727f03f78c` |
| `e_hoa_don/cau_hinh_may.py` | `94528ad3f5d7feb06cb912eddd5e8a2a47b53443d0538bf65d7b93dbdfa2a17b` | `94528ad3f5d7feb06cb912eddd5e8a2a47b53443d0538bf65d7b93dbdfa2a17b` |
| `e_hoa_don/chay.py` | `b4fb1fe6ecd63b20b7b293bdcf640c8d8ad920b30fbe11cb35e3c4f5c34b2523` | `b4fb1fe6ecd63b20b7b293bdcf640c8d8ad920b30fbe11cb35e3c4f5c34b2523` |
| `e_hoa_don/doc.py` | `4ad4a0065a22aca2e58c0bb6de7053cd7dcefa003c21f1d464d7ecabcae10b7a` | `4ad4a0065a22aca2e58c0bb6de7053cd7dcefa003c21f1d464d7ecabcae10b7a` |
| `e_hoa_don/hoa_don_xml.py` | `86f1dce600818e4f27cf26e7d4f2fa590f0722334fa766ef2e3ed43af2a7ebba` | `86f1dce600818e4f27cf26e7d4f2fa590f0722334fa766ef2e3ed43af2a7ebba` |
| `engine.json` | `bb1d48c0c641ff54aa8809eccf60074d1a7b47f3087358cc67521618d3d71629` | `bb1d48c0c641ff54aa8809eccf60074d1a7b47f3087358cc67521618d3d71629` |
| `README.md` | `659f894abf2d7c35a2f643d3369b1e268a5f336b0eac68a7b719144ede97c636` | `659f894abf2d7c35a2f643d3369b1e268a5f336b0eac68a7b719144ede97c636` |
| `requirements.lock` | `9d44717d3f5fdb8196eeb57b46a80436370a220289b88fc1e0f9deda7be90ab4` | `9d44717d3f5fdb8196eeb57b46a80436370a220289b88fc1e0f9deda7be90ab4` |

## HD-1 — 15/11/2026

Hai tệp runtime thay đổi: `e_hoa_don/doc.py` (lỗi nguồn/phép chiếu và tiền kiểm trần 1.000 HHDVu bằng XMLParser stdlib không dựng cây), `e_hoa_don/chay.py` (hợp đồng lỗi vượt trần và ánh xạ hẹp lỗi kích thước mở/đọc tệp). Cặp tệp do lead Claude duyệt; parser `hoa_don_xml.py` giữ nguyên HD-0, test đối chiếu nguồn cộng hai thay đổi import vẫn đạt. Không đổi nguồn, giấy phép hoặc dependency.

| Tệp runtime HD-1 | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `e_hoa_don/doc.py` | `4114d0d293438572f5293a69395d6a53a5300aacf4a2c94f3530e999b5fbcd89` | `bee080710b417a81f5b0d88a9d41474dcf2fe44635f55b8dd028b7c58714da93` |
| `e_hoa_don/chay.py` | `71dc63fe70d6260b5ead8578f20a2a4d467ade1fe7430bc1e44e6446fe409e92` | `49e70e7af6f14637ebcb174c6f7326136d2be6bca76ded9dd5bcda6d766ffde6` |

Bảng HD-0 giữ lịch sử; không dùng làm hash tệp HD-1 đã thay đổi. Danh mục cuối toàn gói thuộc HD-4.

## HD-4 — danh mục thực tế 15/11/2026

Ba tệp nguồn `ma-nguon` ở trên đã được đối chiếu SHA bytes và LF, khớp bảng lịch sử; không sửa metadata nguồn. Parser giữ thuật toán nguồn, chỉ đổi hai import như đã nêu; `doc.py` là phép chiếu viết lại từ các quy tắc nguồn, `chay.py` là vỏ SDK mới có chốt fail-closed; `cau_hinh_may.py` và `__init__.py` viết mới theo phiếu/mẫu. Manifest, hai schema, ba XML DEMO, README, CHANGELOG và lock viết mới theo phiếu; không lấy Node hay portal. Phiên bản gói 1.0.0 theo engine.json; SDK 2.0.0 theo wheel. Nguồn nội bộ Python không có căn cứ giấy phép riêng trong hồ sơ đã xét: không tự gán license. Quyền nội bộ CD-096 A1 ghi cho nguồn Node cũ không suy rộng sang gói XML.

Bảng dưới ghi SHA bytes thực tại mốc HD-4 và SHA sau thay CRLF bằng LF; không chuẩn hóa Unicode. Khác biệt checkout phải đối chiếu cả LF và thay đổi nội dung; không sửa hash lịch sử để bỏ qua thay đổi. Không tự băm NGUON.md để tránh tự tham chiếu.

| Tệp trong gói | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `CHANGELOG.md` | `cada241a82a76898b96a0ed062dd6106ee137de7ca3ac40e2df6e14a1c12a8d3` | `cada241a82a76898b96a0ed062dd6106ee137de7ca3ac40e2df6e14a1c12a8d3` |
| `contract/bao_cao_xml.schema.json` | `66c615f95550dad54fd84a89aa153b91fa1a39a5ae89091173ed281ebc817d4b` | `480c43d9ad9226922e28da3d94c56056df70d7318146fd812dbd0dede8368d12` |
| `contract/cau_hinh_may.schema.json` | `6556c8f200d7a082af390590b95ba2a1b1ec536cf971e1a654b618f5bf9461af` | `195eb425011f09b51bd0890689156f0fa4b07660ebd6dc01f54769176abea2b4` |
| `demo/hoa-don-DEMO.xml` | `06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe` | `06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe` |
| `demo/hoa-don-le-DEMO.xml` | `6ef712c06b870cfa7cd478a463ba1349689ca283bcf79f2a1fd8f64bfba6225b` | `6ef712c06b870cfa7cd478a463ba1349689ca283bcf79f2a1fd8f64bfba6225b` |
| `demo/hoa-don-thieu-DEMO.xml` | `fb45b967fcc1fe6fb7f0896a3235889a3a9623a997694460443e8ee3bafe516a` | `fb45b967fcc1fe6fb7f0896a3235889a3a9623a997694460443e8ee3bafe516a` |
| `e_hoa_don/__init__.py` | `ed1b55a64dbdd460297394371d44be45872cb34a1f854bffda9ff8564b00e2f7` | `168c1ace3c34e2faed85d57f601633d46d492896f56b4f2acd8fcb727f03f78c` |
| `e_hoa_don/cau_hinh_may.py` | `703bca0f04ade53a9b723d25e9cfbd6b7d1659ccb87dcb6462603a5fdb58e719` | `94528ad3f5d7feb06cb912eddd5e8a2a47b53443d0538bf65d7b93dbdfa2a17b` |
| `e_hoa_don/chay.py` | `9739bcc5fd3cbfd07b3cc9609686331ab0ecadaf9fbba44646e1a4eb37e04e06` | `9739bcc5fd3cbfd07b3cc9609686331ab0ecadaf9fbba44646e1a4eb37e04e06` |
| `e_hoa_don/doc.py` | `4114d0d293438572f5293a69395d6a53a5300aacf4a2c94f3530e999b5fbcd89` | `bee080710b417a81f5b0d88a9d41474dcf2fe44635f55b8dd028b7c58714da93` |
| `e_hoa_don/hoa_don_xml.py` | `4153585d413117c97563e215c9da1cfd1548e17119c2651ffea4763aaba53d88` | `86f1dce600818e4f27cf26e7d4f2fa590f0722334fa766ef2e3ed43af2a7ebba` |
| `engine.json` | `0f26a4de8318a97a569089bf870a1b1a47da3e209592a6f2fd7f0acd251fdbb6` | `e356a102f2a9bfbafa072964548b661ef611bf17376e1885237fdb0a4b17229a` |
| `README.md` | `884bab27c527849bd358dc31cf91e2341f39d7c64b83047402e66aef0ace6213` | `884bab27c527849bd358dc31cf91e2341f39d7c64b83047402e66aef0ace6213` |
| `requirements.lock` | `b8352099070d06ed79794796878efcf4f245f6bae8732ad61b0552e8e6dd8f50` | `9d44717d3f5fdb8196eeb57b46a80436370a220289b88fc1e0f9deda7be90ab4` |

## Sửa HD-4 — CI Linux/Python 3.11, 15/11/2026

Chỉ CHANGELOG trong gói được bổ sung bằng chứng sửa công cụ kiểm ngoài gói; năm tệp runtime, manifest, schema, DEMO, README và lock không đổi. Không thay hash nguồn hoặc bảng lịch sử HD-4 ở trên để bỏ qua thay đổi. Bản sửa `tests/kiem_doc_lap.py` và test hồi quy nằm ngoài gói; không có nguồn/phụ thuộc runtime mới.

| Tệp đổi trong gói | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `CHANGELOG.md` | `a4e08324b4f21865b36351f3dee137ae7ccc3523f84734c3f60904e552f6d00e` | `a4e08324b4f21865b36351f3dee137ae7ccc3523f84734c3f60904e552f6d00e` |

## HD-P2 — cập nhật tài liệu 15/11/2026

Chỉ bổ sung CHANGELOG trong gói để ghi phiếu ZIP/XLSX HD-5…HD-8 tại `e_hoa_don/docs/`; không đổi runtime/manifest/schema/DEMO/lock, không đưa nguồn Node hoặc dependency mới vào gói. Quyền CD-096 A1 chỉ dùng nội bộ của nguồn Node được dẫn trong phiếu thiết kế, chưa là bằng chứng gói SDK 2.0 đã đóng XLSX. Giữ nguyên mọi bảng SHA lịch sử ở trên; đây là băm CHANGELOG sau bổ sung HD-P2, không là băm toàn gói phát hành.

| Tệp đổi trong gói | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `CHANGELOG.md` | `d8adc3e10866662a32d9b890add47bf95d37c2ca2c5b597107fad6d5d46ff420` | `d8adc3e10866662a32d9b890add47bf95d37c2ca2c5b597107fad6d5d46ff420` |

Quyết định lead 15/11: XLSX dự kiến dùng Python stdlib; `bang_ke.cjs` chỉ tham chiếu tĩnh cách chiếu cột/định dạng. Chưa thêm mã hay dependency XLSX.

## HD-5 — lõi kiểm kê ZIP, 15/11/2026

`e_hoa_don/zip.py` viết mới theo phiếu §2.4, tái dùng trực tiếp `doc_goi_hoa_don_zip`, `ra_json`, phép chiếu XML và gate HHDVu HD-1; không chép parser thứ hai. `e_hoa_don/hoa_don_xml.py` chỉ đổi cổng ZIP và thêm stat/unicodedata cùng hai hằng số bảo vệ ZIP; parser XML/DTO/thuật toán tiền còn lại nguyên AST so với nguồn đã ghi ở bảng trên (sau hai đổi import SDK lịch sử). Nguồn ma-nguon/Core/SDK không sửa. Không nguồn bên ngoài hoặc dependency mới; runtime chỉ SDK 2.0.0 + stdlib. Không tự đặt giấy phép mới. Manifest và phiên bản 1.0.0 giữ nguyên vì chưa công bố năng lực ZIP.

Các bảng lịch sử giữ nguyên. SHA bytes thực/LF của các tệp thay đổi hoặc thêm trong gói HD-5 ở dưới; không tự băm NGUON.md. Các tệp khác trong gói không đổi.

| Tệp HD-5 trong gói | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `e_hoa_don/zip.py` | `e10b854b14c990c756c318ed3f9b8ed21f59f97ff154570957d1a6587ce1add9` | `e10b854b14c990c756c318ed3f9b8ed21f59f97ff154570957d1a6587ce1add9` |
| `e_hoa_don/hoa_don_xml.py` | `fb201bbb723c4c739596dbbbe0270584a8ab2dbc368886428cde7ef0e3fbcab1` | `8b7cb17848a5861b7384aefa31b22d6cc39f28b2e3486a0c4bc938929d397f32` |
| `contract/bao_cao_zip.schema.json` | `3585b86eb1f8d9210d54d42042fc73b4cfa36c39ccbf4e8bfaf21a391d78f27b` | `fb320d2310fb3651e8fe8c487c4e83a4f464df53d7736cc3de943bb3f8aa8443` |
| `README.md` | `d1c4959a102df6de300193f1905f857de1aa099107dd26bb6c0cc1d027593b35` | `70302865c2f4357df4fdb8af51d596faf4cf27346329da1d6b36bea327114c98` |
| `CHANGELOG.md` | `12d96bfd0d55201516790a24c2320af2997ed8b1d207f2e4685e5a7b2950d08a` | `12d96bfd0d55201516790a24c2320af2997ed8b1d207f2e4685e5a7b2950d08a` |


## HD-6 — cổng SDK ZIP và phụ thuộc stdlib, 15/11/2026

Chỉ hai tệp runtime đổi: `e_hoa_don/chay.py` (handler SDK ZIP) và `e_hoa_don/zip.py` (bọc cảnh báo stdlib). Tái dùng trực tiếp lõi HD-5; `hoa_don_xml.py`, `doc.py`, Core/SDK/ma-nguon không đổi trong lát này. Không nguồn bên ngoài hoặc dependency mới; chỉ SDK 2.0.0 + Python stdlib, giữ quyền nội bộ đã ghi ở trên. Giữ phiên bản gói hiện có 1.0.0 và hợp đồng XML; việc ghim phát hành cuối ZIP/XLSX thuộc HD-8/lead.

Phụ thuộc riêng của CPython cần kiểm khi nâng Python: `ZipExtFile._left`, `_update_crc`, `_eof`, `_compress_left`, `_decompressor` (và `eof` của DEFLATE); `zipfile._EndRecData`, `_ECD_DISK_NUMBER`, `_ECD_DISK_START`, `_ECD_ENTRIES_TOTAL`, `_ECD_ENTRIES_THIS_DISK`. Đây không phải API công khai ổn định. `tests/test_hd_6.py::test_chot_api_rieng_zipfile_va_crc` chốt sự tồn tại và hành vi: số đếm EOCD, ghi được `_left`/hook CRC, bytes giải nén đủ, EOF/compressed-left, DEFLATE EOF và CRC sai phải từ chối. Hồi quy HD-5 kiểm metadata giả/bytes thật/tổng/trần/CRC trên cả STORED và DEFLATE. Cần chạy lại các ca này khi nâng Python; không bỏ test để hợp thức hóa thay đổi stdlib.

Một số bản Python phát UserWarning có tên entry cho central directory overlap. `zip.py` dùng `warnings.catch_warnings`, bộ lọc UserWarning và hook `showwarning` ném `BadZipFile` với câu cố định. Hook chỉ có hiệu lực trong lời gọi lõi; lõi bắt ngay tại mở/đọc entry, giữ bản ghi lỗi với băm/kích thước null, tiếp tục kiểm kê. Không đổi `zipfile.ZipFile.open` toàn cục; khôi phục hook/filter cả khi lỗi/hủy. Phiếu chỉ cho 1 việc đồng thời; khi đổi mô hình đồng thời phải kiểm lại phạm vi bộ lọc warnings của bản Python đang dùng. Test overlap bytes thật và test cảnh báo cưỡng bức (chạy cả trên Python từ chối overlap trực tiếp) kiểm canary, không có stderr và không mất entry.

DEMO ZIP được dựng từ bytes `demo/hoa-don-DEMO.xml` đã pin ở HD-3, XML hỏng literal `<HDon`, PDF giả `%PDF-DEMO`, bản trùng bytes và bản đổi số `0000123` thành `0000124`; timestamp ZIP cố định 30/10/2026, STORED. Chỉ dữ liệu DEMO, không tệp thật. Oracle trong `tests/test_hd_6.py` dựng toàn JSON từ literal trường/DTO/cảnh báo, không gọi bộ đọc để tạo expected; chỉ ghép tham chiếu Core/băm bytes bằng hashlib. So toàn JSON, từng ordinal/băm/đếm qua CoreGia và HTTP giả; không dùng output writer/reader làm đáp án.

Các bảng hash lịch sử giữ nguyên; bảng HD-6 bên dưới là bytes thực và chuẩn LF sau thay đổi, không tự băm NGUON.md.

| Tệp HD-6 trong gói | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `e_hoa_don/chay.py` | `f99ce16f45c731fe6e4d333f625da2206d866acaf6518103425f1ba1d6a46882` | `703668d9be7eb296d69bd294b708366e4820814143cf612fad1660595ef5c69e` |
| `e_hoa_don/zip.py` | `6212ab75f8f1e0cb8cc2103d11ce4a5d4ea08ab213d5191745c3721ecc215149` | `3be2a2156de2ba8f63c5a9679b8c4d344a6d7e5a8d12f838d5d440b2d4b3e733` |
| `engine.json` | `00f42154f2350dc071c4ad8b96356d41daf381ffa867d45983c72752107ef400` | `b84b1cf197a8131aed30c2f54ec6cad90cae1030e38b710a241546b0a568864c` |
| `demo/goi-hon-hop-DEMO.zip` | `91106609ac23affecdb2be9592f7a708a0b816700c5370eb234bbc913a5cedc8` | `91106609ac23affecdb2be9592f7a708a0b816700c5370eb234bbc913a5cedc8` |
| `README.md` | `e672c541977e41c20e6c90b782f6a72deb124ec6f7ad85af16699a66b2df7665` | `e672c541977e41c20e6c90b782f6a72deb124ec6f7ad85af16699a66b2df7665` |
| `CHANGELOG.md` | `45a2079d3a84af74fdbf1ae0cbf71203082a43d750b9cb303df879780ef633c1` | `91f695b387181154f9d4d8138e039119537975d01039566366bf1cbeab1da845` |


## HD-7 — nguồn bảng kê, 15/11/2026

Quyền **CD-096 A1**, theo `e_hoa_don/ma-nguon/NGUON.md`: phần mềm nội bộ, Anh xác nhận 06/11/2026, chỉ dùng nội bộ. Không tự đặt LICENSE mới; không suy thành quyền phân phối bên ngoài. Các nguồn dưới đây chỉ đọc tĩnh trong worktree, không chạy/require Node, không sửa nguồn tham chiếu và không chép vendor/dependency vào runtime.

| Nguồn tương đối gốc repo | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `e_hoa_don/ma-nguon/bang_ke.cjs` | `9e88fa02e0d18ba816bb54a31eac6e79d1c3cc9f6c95d1d08b8ce232c4ea807f` | `99dea0ecf2b991bca7107d2b179078585359a936ac187856bb89563d3cbb9445` |
| `e_hoa_don/ma-nguon/vendor/config.js` | `35c86b295812793e98dd0ed65b3b34f247b1b67cb318e0e2d7fded0f1a57c3df` | `48cb8cb1b0253cd4a5110f1628150053a0372a00b3503f359a01849281f90b02` |
| `e_hoa_don/ma-nguon/vendor/build.js` | `6e7b23e937b40740817b94e629647f8080e089cf66f57cca9561ea9a0d9ab614` | `5664548e0f08936e6b15536dc4ec23bd55a04417d6c66ef439362415a16ab3d5` |
| `e_hoa_don/ma-nguon/NGUON.md` | `f7f4d146d266de773c49d7ef5e47491df9b67a85ccd3a1a9cff2fae13e705007` | `7ea8d95ce00411cad015bd74afa0fae4d34ed7fc33a8aca5265b2ab6879f1c09` |

`bang_ke.cjs`: đối chiếu thứ tự DAU/TONG và quy tắc giữ text/null; `vendor/config.js`: EXCEL_COLUMNS chính là thứ tự buildExcel dùng; `vendor/build.js`: đọc tĩnh để xác nhận cách chọn cột, width và header. `ma-nguon/NGUON.md`: bằng chứng quyền A1 và nguồn lịch sử. SHA thực ở trên đo trên bytes checkout (CRLF); cột LF chỉ đổi CRLF → LF, không chuẩn hóa Unicode. Không dùng hash lịch sử thay bytes hiện tại.

Đối chiếu với phiếu §2.5: sheet `Hoa don` có đúng 17 cột theo thứ tự STT; Thứ tự entry; Tên entry; Băm tệp; Mẫu số; Ký hiệu; Số hóa đơn; Ngày lập; MST bán; MST mua; Tiền trước thuế; Tiền thuế; Tổng thanh toán; Mã tiền tệ; Cần kiểm tra; Cảnh báo; Trùng với thứ tự.

- Cột chung giữ thứ tự tương đối nguồn: `_stt`, `khmshdon`, `khhdon`, `shdon`, `tdlap`, `nbmst`, `nmmst`, `tgtcthue`, `tgtthue`, `tgtttbso`, `dvtte`. DAU/TONG trong bang_ke.cjs xác định phép chiếu; nguồn buildExcel lấy thứ tự từ EXCEL_COLUMNS trong config.js.
- Bỏ cột `nbten`, `nmten`, `nmcccd`, `tthai`: không có dữ liệu tương ứng trong strict allowlist; không tự bịa tên/CCCD/trạng thái thuế. Đổi nhãn tiền trước thuế để phản ánh TgTCThue gồm cả phần không chịu thuế.
- Cột mới theo thiết kế: Thứ tự entry, Tên entry, Băm tệp trước mẫu số; Cần kiểm tra, Cảnh báo, Trùng với thứ tự sau currency. Không thay trạng thái đọc bằng dấu trùng.
- Sheet mới `Kiem ke tep` gồm mọi entry, cả thư mục, lỗi, chưa hỗ trợ và trùng, theo ordinal nguồn; khối thông tin đầu giữ đếm/băm JSON và XML/ZIP/phiên bản/nguồn/da_doc_het và giới hạn ý nghĩa nghiệp vụ. Hai tên sheet cố định.
- Khác nguồn cũ theo quyết định lead: Python stdlib OOXML, RAM; inline string và text `@` cho mọi ô, header có style/freeze, width cố định. Không Number/float/round/SUM, hyperlink hay macro. Tiền ngoài miền 18/6 lấy exact_text đã kiểm trong JSON kèm cảnh báo; currency thiếu/sai/mơ hồ thì tiền trống. Không parse XML lại, không đổi tổng nguồn.

Ba runtime HD-7: `e_hoa_don/chay.py` đăng ký handler; `e_hoa_don/bang_ke.py` kiểm schema JSON nội bộ + binding/đếm/phiên bản/băm, tái dựng phần DTO để dùng lại chieu_truong, tạo bảng; `e_hoa_don/xlsx_toi_thieu.py` tự viết OOXML bằng zipfile, XML escape và ST_Xstring bảo toàn control/literal _xHHHH_. Không có dependency mới; SDK 2.0.0 + Python stdlib.

Pytest có oracle cột/giá trị literal độc lập, đọc lại mọi XML và quan hệ OOXML bằng zipfile; test đối chiếu tĩnh nguồn ở trên. Đây là đã kiểm bằng Core giả (CoreGia); chưa kiểm Excel app/Core thật. Chạy thử SDK vẫn chỉ phủ 3 XML + 1 ZIP: SDK 2.0.0 chưa tạo fixture tệp JSON lồng trong truong, XLSX được kiểm bằng CoreGia.them_tep và kết quả bước đọc thật trong pytest, không ID giả và không sửa SDK. Cần Core bổ sung fixture/chuỗi Chạy thử chung.


SHA triển khai HD-7 đo trên bytes thực tại bàn giao, không phải băm phát hành toàn gói:

| Tệp trong gói | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---|---|
| `e_hoa_don/chay.py` | `f12dc1afbb78b24888590080788fc9ea23d5bf6f3b781d9b1f098650c9896610` | `15b95ec911ea65dd63ce053a1aed6a495fe4b7edd11ded2602d412532abb815e` |
| `e_hoa_don/bang_ke.py` | `93407052b3ff30d089903889548291ef0109e20184381c8d45df494b71a8c5dd` | `93407052b3ff30d089903889548291ef0109e20184381c8d45df494b71a8c5dd` |
| `e_hoa_don/xlsx_toi_thieu.py` | `ad6a6c8e89d73e5e994c4f21066c7ee76640b261eaf253dc82a69cf1337fa46d` | `ad6a6c8e89d73e5e994c4f21066c7ee76640b261eaf253dc82a69cf1337fa46d` |
| `engine.json` | `f269a40b342df76456e5a5cab8e726afefaec9bdf490594fb56c3e62499d9b44` | `726356b63682629eac6361afbd600461f6c1079d6d46bb38ccac3827c8ef6858` |

## HD-8 ? ??i chi?u ngu?n 15/11/2026

??i chi?u l?i quy?n CD-096 A1 trong `ma-nguon/NGUON.md`: ch? d?ng n?i b?; ngu?n Node ch? ??c t?nh, kh?ng ch?y v? kh?ng c?p quy?n ph?n ph?i. Test ??i chi?u SHA bytes th?c v? d?ng LF c?a `bang_ke.cjs`, `vendor/config.js`, `vendor/build.js`, `NGUON.md` v?i b?ng HD-7; c?c SHA theo t?p kh?ng ph?i m? b?m g?i ph?t h?nh. Kh?ng th?m runtime hay dependency.
## HD-9 — SDK 2.2.0, 15/11/2026

Wheel nội bộ `kho_tri_thuc_sdk-2.2.0-py3-none-any.whl`, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` (đối chiếu SHA256SUMS.txt; không thêm phụ thuộc runtime). Theo quyết định lead, hạ trần đầu vào ZIP và JSON bảng kê qua `mo_tep` xuống 20 MiB; giữ trần đầu ra. Các bảng lịch sử giữ nguyên. SHA dưới đây đo bytes thực và chuẩn LF, hai giá trị giống nhau tại thời điểm kiểm; không tự băm NGUON.md.

| Tệp | SHA-256 bytes thực / chuẩn LF |
|---|---|
| `engine.json` | `912414e9926bbe24e978d4e165722e93d66761c19b4a2d4089ec5019c421433f` |
| `requirements.lock` | `ab043bbb337b669c302791d26eb214ca9e5812e304c169e356bc3e3d5eb5e13a` |
| `README.md` | `27275f0a84d31262179ef5f1ac22d28cece8e94121e21430fd5a70a74e450e9d` |
| `CHANGELOG.md` | `5e8c5d56a1d9677e817544f7c192f759d87d0b14caa9c9ef05ea4c0a20758ded` |
| `e_hoa_don/bang_ke.py` | `9893619ff051f77a7235073ce8ffc165958c3b0dfaf3626fa087ba602632d342` |
| `e_hoa_don/zip.py` | `5b60d342be6f9e109c75df7b266e779a0aa389c0937288f7e7ed77e992685e52` |


## 1.0.1 — LX-HD, 28/11/2026

Sửa `_tep_mac_dinh()` theo mẫu `e_ocr/goi/e_ocr/e_ocr/cau_hinh_may.py` và phiếu Linux §4: thiếu PROGRAMDATA thì Windows dùng C:/ProgramData, không phải Windows dùng /var/lib. Không đổi xử lý KTT_ENGINE_CAU_HINH hoặc các kiểm an toàn. Helper vẫn ngoài đường chạy XML/ZIP/XLSX. Nâng engine.json, __init__ và các oracle/test phiên bản hiện hành lên 1.0.1; các bảng 1.0.0 bên trên là lịch sử. Runtime chỉ SDK 2.2.0 đã ghim + stdlib; không đổi requirements.lock, không nguồn ngoài hoặc thư viện mới.

Bảng dưới là kiểm kê toàn gói tại bàn giao LX-HD, tính sau mọi thay đổi gói bằng hashlib stdlib; không tự băm NGUON.md. Engine không có công cụ sinh kiểm kê riêng, không có SQL/ngăn hoặc sql/kiem_ke.json. SHA bytes thực dùng bytes checkout; SHA chuẩn LF chỉ thay CRLF → LF ở tệp văn bản, ZIP giữ bytes gốc. Các bảng lịch sử giữ nguyên. Đã kiểm bằng Core giả (CoreGia): SDK 4/4 ĐẠT, pytest 662 passed/0 skipped, kiểm độc lập ĐẠT; Linux mới giả lập đường, chưa chạy Ubuntu/WSL.

| Tệp trong gói | Byte | SHA-256 bytes thực | SHA-256 chuẩn LF |
|---|---:|---|---|
| `CHANGELOG.md` | 22641 | `11303e3b21fdfa49ddbef7f9cb8b90eaacfadcd2b6ab9bcbe7594aed8bee1477` | `237d62c0f6a4e4cdf68a71368b076706ea06bfdda8b8989739e13b0b43ac287c` |
| `contract/bao_cao_xml.schema.json` | 14127 | `66c615f95550dad54fd84a89aa153b91fa1a39a5ae89091173ed281ebc817d4b` | `480c43d9ad9226922e28da3d94c56056df70d7318146fd812dbd0dede8368d12` |
| `contract/bao_cao_zip.schema.json` | 25950 | `3585b86eb1f8d9210d54d42042fc73b4cfa36c39ccbf4e8bfaf21a391d78f27b` | `fb320d2310fb3651e8fe8c487c4e83a4f464df53d7736cc3de943bb3f8aa8443` |
| `contract/cau_hinh_may.schema.json` | 330 | `6556c8f200d7a082af390590b95ba2a1b1ec536cf971e1a654b618f5bf9461af` | `195eb425011f09b51bd0890689156f0fa4b07660ebd6dc01f54769176abea2b4` |
| `demo/goi-hon-hop-DEMO.zip` | 3028 | `91106609ac23affecdb2be9592f7a708a0b816700c5370eb234bbc913a5cedc8` | `91106609ac23affecdb2be9592f7a708a0b816700c5370eb234bbc913a5cedc8` |
| `demo/hoa-don-DEMO.xml` | 798 | `06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe` | `06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe` |
| `demo/hoa-don-le-DEMO.xml` | 847 | `6ef712c06b870cfa7cd478a463ba1349689ca283bcf79f2a1fd8f64bfba6225b` | `6ef712c06b870cfa7cd478a463ba1349689ca283bcf79f2a1fd8f64bfba6225b` |
| `demo/hoa-don-thieu-DEMO.xml` | 732 | `fb45b967fcc1fe6fb7f0896a3235889a3a9623a997694460443e8ee3bafe516a` | `fb45b967fcc1fe6fb7f0896a3235889a3a9623a997694460443e8ee3bafe516a` |
| `e_hoa_don/__init__.py` | 114 | `c7a9cbf31d3b4c4dddb139f6397a3bc5e246920c933242ef0b66a1aecf4fdd1f` | `2e7f601d60eea7d20fc7ead51a59d7f8bbc130eb850419ccc4d774b75fe324cf` |
| `e_hoa_don/bang_ke.py` | 16628 | `22644020e02dc97153ba60bbbf21da4908628ab71d7e1cc6d8ce264894b0d827` | `9893619ff051f77a7235073ce8ffc165958c3b0dfaf3626fa087ba602632d342` |
| `e_hoa_don/cau_hinh_may.py` | 2803 | `b775322033ac37ce72034000ad6b641c166ab03c66aa46513491f47c9ce7b9b6` | `f069cb040bad8c04ebc7e45d85146d9cd04c149d78c19cef47470729aed78cc3` |
| `e_hoa_don/chay.py` | 4424 | `f12dc1afbb78b24888590080788fc9ea23d5bf6f3b781d9b1f098650c9896610` | `15b95ec911ea65dd63ce053a1aed6a495fe4b7edd11ded2602d412532abb815e` |
| `e_hoa_don/doc.py` | 8400 | `4114d0d293438572f5293a69395d6a53a5300aacf4a2c94f3530e999b5fbcd89` | `bee080710b417a81f5b0d88a9d41474dcf2fe44635f55b8dd028b7c58714da93` |
| `e_hoa_don/hoa_don_xml.py` | 73550 | `fb201bbb723c4c739596dbbbe0270584a8ab2dbc368886428cde7ef0e3fbcab1` | `8b7cb17848a5861b7384aefa31b22d6cc39f28b2e3486a0c4bc938929d397f32` |
| `e_hoa_don/xlsx_toi_thieu.py` | 5982 | `06e185c00dc5762a4393a7223d47e234d6af39a3424dcf43263ae60933fbc304` | `ad6a6c8e89d73e5e994c4f21066c7ee76640b261eaf253dc82a69cf1337fa46d` |
| `e_hoa_don/zip.py` | 9114 | `0d9abdf12d0a5767ab2f46b445f4baeda8e7e6e0ca264f971eec11ca6aa99567` | `5b60d342be6f9e109c75df7b266e779a0aa389c0937288f7e7ed77e992685e52` |
| `engine.json` | 7874 | `3aee2faecbc5d49e5cd3097f8cf8ddcc1faf847de9076f936859267eb0c19d75` | `8396ccc872375f58fb8e224012cee00fea268543f73072e7a509e6340eb39454` |
| `README.md` | 16270 | `13f3c18994fdd9d15c952d52399c8fd7a0b1de6dcf7f7c5bf8f0b7f60fa098f8` | `2d2d3356760ac3efa6d5c47716d1d4ee0222af8fc6ddba6cfef4db3bac9fd455` |
| `requirements.lock` | 195 | `ec4b721a01e650ad2fd7392b999078279c50788b71803a8d4ba672af0594b137` | `ab043bbb337b669c302791d26eb214ca9e5812e304c169e356bc3e3d5eb5e13a` |
