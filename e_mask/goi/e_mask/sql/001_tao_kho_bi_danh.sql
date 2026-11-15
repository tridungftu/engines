-- Kho nhận diện, không phải ánh xạ mở che của một chuỗi.
-- Core cấp các cột hệ thống, mã hóa và tính dấu tra cứu có khóa.
CREATE TABLE eng_e_mask.dinh_danh (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    id_dinh_danh text NOT NULL,
    vung_du_lieu text NOT NULL,
    gia_tri_goc bytea NOT NULL,
    gia_tri_goc_bam bytea NOT NULL,
    gia_tri_chuan bytea NOT NULL,
    gia_tri_chuan_bam bytea NOT NULL,
    phien_ban_chuan_hoa text NOT NULL,
    nhom text NOT NULL,
    trang_thai text NOT NULL,
    so_gap numeric NOT NULL,
    UNIQUE (id_dinh_danh)
);
COMMENT ON TABLE eng_e_mask.dinh_danh IS 'Tên chính thức và tên chờ duyệt, chỉ Core mã hóa';
COMMENT ON COLUMN eng_e_mask.dinh_danh.id_dinh_danh IS 'Mã opaque, không chứa tên hoặc băm tên công khai';
COMMENT ON COLUMN eng_e_mask.dinh_danh.vung_du_lieu IS 'Vùng DEMO hoặc dữ liệu vận hành, không thay quyền truy cập';
COMMENT ON COLUMN eng_e_mask.dinh_danh.gia_tri_goc IS 'Tên nguyên văn đã được Core mã hóa';
COMMENT ON COLUMN eng_e_mask.dinh_danh.gia_tri_goc_bam IS 'Dấu tra cứu có khóa do Core quản';
COMMENT ON COLUMN eng_e_mask.dinh_danh.gia_tri_chuan IS 'Tên chuẩn hóa đã được Core mã hóa';
COMMENT ON COLUMN eng_e_mask.dinh_danh.gia_tri_chuan_bam IS 'Dấu tra cứu có khóa do Core quản';
COMMENT ON COLUMN eng_e_mask.dinh_danh.phien_ban_chuan_hoa IS 'Phiên bản chuẩn hóa đã ghim khi tạo';
COMMENT ON COLUMN eng_e_mask.dinh_danh.nhom IS 'Mã nhóm định danh';
COMMENT ON COLUMN eng_e_mask.dinh_danh.trang_thai IS 'CHO_DUYET, CHINH_THUC hoặc TU_CHOI';
COMMENT ON COLUMN eng_e_mask.dinh_danh.so_gap IS 'Số lần gặp
kieu: so';

-- Chưa khai duy nhất theo dấu bí mật: C-P4-03 cần Core xác nhận
-- chuẩn hóa, chỉ mục, duy nhất và lấy hoặc tạo theo bí mật cùng vùng.
-- Không dùng tên rõ hoặc tự tạo băm tên làm khóa thay thế.
CREATE TABLE eng_e_mask.bi_danh (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    id_bi_danh text NOT NULL,
    id_dinh_danh text NOT NULL,
    vung_du_lieu text NOT NULL,
    bi_danh text NOT NULL,
    bi_danh_chuan text NOT NULL,
    trang_thai text NOT NULL,
    UNIQUE (id_bi_danh),
    UNIQUE (vung_du_lieu, bi_danh_chuan)
);
COMMENT ON TABLE eng_e_mask.bi_danh IS 'Bí danh chính thức và lịch sử, không lưu bí danh tạm theo yêu cầu';
COMMENT ON COLUMN eng_e_mask.bi_danh.id_bi_danh IS 'Mã opaque của bí danh';
COMMENT ON COLUMN eng_e_mask.bi_danh.id_dinh_danh IS 'Mã opaque tham chiếu cùng dòng định danh khi duyệt';
COMMENT ON COLUMN eng_e_mask.bi_danh.vung_du_lieu IS 'Vùng dữ liệu của bí danh';
COMMENT ON COLUMN eng_e_mask.bi_danh.bi_danh IS 'Mã MASK hoặc Junsky hợp lệ, không chứa tên gốc';
COMMENT ON COLUMN eng_e_mask.bi_danh.bi_danh_chuan IS 'Mã bí danh chuẩn hóa để chống trùng trong cùng vùng';
COMMENT ON COLUMN eng_e_mask.bi_danh.trang_thai IS 'Trạng thái chính thức hoặc lịch sử, không xóa và không tái cấp';
