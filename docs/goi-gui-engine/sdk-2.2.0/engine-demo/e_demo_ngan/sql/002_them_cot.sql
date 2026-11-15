-- Migration bổ sung chỉ thêm cột cho phép bỏ trống, không thay dữ liệu đã ghi.
ALTER TABLE eng_e_demo_ngan.dem_goi ADD COLUMN ghi_chu text;
COMMENT ON COLUMN eng_e_demo_ngan.dem_goi.ghi_chu IS 'Ghi chú bổ sung khi nâng gói DEMO';
