-- Chỉ thêm cột nhật ký. Binding C-DC-03 phải cấm UI ghi ngăn trực tiếp.
ALTER TABLE eng_e_doi_chieu.xac_nhan ADD COLUMN ma_luot text;
ALTER TABLE eng_e_doi_chieu.xac_nhan ADD COLUMN ma_diem text;
ALTER TABLE eng_e_doi_chieu.xac_nhan ADD COLUMN noi_dung text;
