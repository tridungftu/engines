# NGUON — gói XML e_hoa_don HD-0

Nguồn nội bộ trong repo; không truy cập nguồn ngoài hoặc tự đặt giấy phép mới. Quyền/nguồn Node của bản cũ không được dùng làm căn cứ công bố ZIP/bảng kê/tải trong gói này. Runtime chỉ stdlib và SDK 2.0.0; không thêm dependency ngoài SDK.

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
