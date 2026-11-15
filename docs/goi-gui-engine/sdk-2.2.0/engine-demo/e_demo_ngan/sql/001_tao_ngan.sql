-- Ngăn đếm theo pháp nhân và ngày. Core cấp id, tăng phiên bản và đặt hạn giữ.
CREATE TABLE eng_e_demo_ngan.dem_goi (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ngay date NOT NULL,
    so_lan numeric NOT NULL,
    UNIQUE (phap_nhan_id, ngay)
);
COMMENT ON TABLE eng_e_demo_ngan.dem_goi IS 'Đếm lượt gọi theo pháp nhân và ngày';
COMMENT ON COLUMN eng_e_demo_ngan.dem_goi.ngay IS 'Ngày đếm theo giờ Việt Nam';
COMMENT ON COLUMN eng_e_demo_ngan.dem_goi.so_lan IS 'Số lần gọi trong ngày
kieu: so';

-- Ngăn dùng chung trong engine. Core giữ phap_nhan_id rỗng và mã hóa giá trị.
CREATE TABLE eng_e_demo_ngan.dinh_danh (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    gia_tri bytea NOT NULL,
    gia_tri_bam bytea NOT NULL,
    bi_danh text
);
COMMENT ON TABLE eng_e_demo_ngan.dinh_danh IS 'Định danh DEMO được mã hóa bởi Core';
COMMENT ON COLUMN eng_e_demo_ngan.dinh_danh.gia_tri IS 'Giá trị định danh đã mã hóa';
COMMENT ON COLUMN eng_e_demo_ngan.dinh_danh.gia_tri_bam IS 'Dấu tra cứu có khóa do Core tính';
COMMENT ON COLUMN eng_e_demo_ngan.dinh_danh.bi_danh IS 'Bí danh DEMO để đối chiếu';
