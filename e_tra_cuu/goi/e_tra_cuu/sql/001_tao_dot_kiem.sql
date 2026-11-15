-- Bài đo DEMO; Core gắn pháp nhân từ việc và cấp các cột hệ thống.
-- Không đặt hạn giữ: TC-Q06 chưa chốt, engine không tự xóa nhật ký/bài đo.
CREATE TABLE eng_e_tra_cuu.dot_kiem (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma_dot text NOT NULL,
    trang_thai text,
    bam_bo text,
    bam_cau_hinh text,
    phien_ban_engine text,
    chi_so text,
    bao_cao text,
    bam_bao_cao text,
    UNIQUE (phap_nhan_id, ma_dot)
);
