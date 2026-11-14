# Nguồn gói OCR-0 — 14/11/2026

Mã mới cho repo, dùng nội bộ tập đoàn theo quyết định cuối của engine OCR.
Lát này không chép mã `ma-nguon/`, mã ABBYY/mask_ocr hay mô hình nhận dạng.

| Phần | Nguồn / giấy phép |
|---|---|
| `engine.json`, `e_ocr/__init__.py`, `e_ocr/chay.py` | Viết mới từ mẫu `docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_doc_tep`, theo API v1 và phiếu giao OCR-0; chỉ dùng import SDK ngoài Core |
| `e_ocr/cau_hinh_may.py`, schema cấu hình | Viết mới theo `GIAO-CODEX-THU-TU.md` §2 và `GIAO-CODEX-e_ocr.md` §2; thư viện chuẩn Python |
| `e_ocr/kho_tam.py` | Viết mới; khóa tệp thư viện chuẩn `msvcrt` trên Windows, `fcntl` trên Linux; không có thư viện ngoài |
| `contract/van_ban_tai_lieu.schema.json` | Chép nguyên byte từ `_chung/contract/van_ban_tai_lieu.schema.json`, định nghĩa theo `LOAI-DU-LIEU-RIENG.md` §2.1; test so SHA-256 |
| `demo/` | Dữ liệu giả mới tạo, có nhãn DEMO; chỉ minh họa schema, không phải kết quả OCR đã chạy |
| SDK 2.0.0 | Wheel do Core phát hành trong repo; giữ nguyên điều khoản của bộ phát hành. Không đóng wheel vào gói engine |

SDK được ghim trong `requirements.lock`. SHA-256 wheel phát hành, đã so với
`docs/goi-gui-engine/sdk-2.0.0/SHA256SUMS.txt`:

```text
a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892  kho_tri_thuc_sdk-2.0.0-py3-none-any.whl
```

Băm SHA-256 các tệp trong gói (không tự băm `NGUON.md` để tránh tự tham chiếu):

```text
d06500e37d25dbf8e84f27cb14f202de7e48ad06f1e0d42af3ea1b4ad7e1664d  CHANGELOG.md
1b56ef1a5de686b4359857b68ad86bd909d250714fbc7f43c44e0e78887b0f04  contract/cau_hinh_may.schema.json
f3756741eea1e5c9c9451b8a8df8a5416817f04adffe4bf1b44c24b19c3e7f93  contract/van_ban_tai_lieu.schema.json
e6a148a20c0bda845df9beff217e86657f63c6c75bc3fa0a0e292d389f6551cd  demo/cau_hinh.demo.json
76c99fe7d0a0c286f5e210c569233f4195cae188cb71ca56d0b04036b06d872e  demo/van_ban_tai_lieu.demo.json
98bc2d0d013caeea3e919a56aa267e2ba98b36d999f3cbf49c7948dff9af08aa  e_ocr/__init__.py
298732214730d25b21e98b63e6af92f4159c4c2f1a9599de0a86719ec6023046  e_ocr/cau_hinh_may.py
b358cca0db92a3354c018c89271a4bc244cc15ee28ed5660af8c386f3d829a36  e_ocr/chay.py
0c8f28d64791c4da8c88791cb25b1623b4f00be542a7de4045610743b87373ad  e_ocr/kho_tam.py
fb9a548a1e9dd2827f0abca3bba8765b379ceccdd2ce575bc67c090568de0981  engine.json
7854801809808e60c8ad7830c159e8e3fd164fe3fc4c1e382796931f5ca17a9e  README.md
4d3c636ee2d9f7b990a49b5fb5ccc403a744b9a4ecd7422c72f369a5f416fba0  requirements.lock
```
