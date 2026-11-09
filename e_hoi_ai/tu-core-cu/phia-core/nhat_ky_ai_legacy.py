"""Bộ ghi nhật ký cổng AI vào PostgreSQL, phía Core (G3-GOI-06).

Tách khỏi lõi cổng AI (``engines/e_hoi_ai/lib/cong_ai.py``) để gói AI không giữ
mã chạm CSDL. Bridge ``kho_tri_thuc.tri_thuc.cong_ai`` gắn lại ``BoGhiPostgres``
vào cùng module lõi để consumer cũ dùng ``cong_ai.BoGhiPostgres`` như trước.
Không import driver CSDL: nhận factory kết nối từ bên gọi.
"""
from __future__ import annotations

import logging
from typing import Callable

from ..engines.e_hoi_ai.lib import cong_ai as _loi
from ..engines.e_hoi_ai.lib.cong_ai import BanGhiCongAI, DUONG_CLOUD, LOCAL_DUNG, LOCAL_SAI

# Cùng logger với lõi để thông báo lỗi ghi nhật ký giữ nguyên nơi phát.
_LOG = logging.getLogger(_loi.__name__)


class BoGhiPostgres:
    """Ghi metadata vào ``nhat_ky.cong_ai_goi`` (M0034), không giữ DSN/khóa.

    ``ket_noi`` là factory context manager cấp kết nối RIÊNG cho nhật ký, ví dụ
    ``lambda: psycopg.connect(dsn)`` hoặc ``pool.connection``. Không truyền kết nối
    đang dùng cho giao dịch nghiệp vụ. Mỗi dòng có giao dịch riêng, kể cả kết nối
    autocommit; lỗi INSERT/commit/kết nối chỉ log tên loại lỗi, không làm mất kết quả AI.
    """

    def __init__(self, ket_noi: Callable):
        self._ket_noi = ket_noi

    def thong_ke(self, cua_so: int) -> dict[str, dict]:
        """Một SELECT, cùng snapshot; chỉ metadata M0034, không cập nhật nhật ký.

        Lỗi đọc được chuyển lên cổng: không có số đo thì không tự giảm tỷ lệ kiểm.
        """
        with self._ket_noi() as conn:
            with conn.cursor() as cur:
                cur.execute("""WITH luot AS (
                    SELECT loai_viec, count(*) AS so_luot
                    FROM nhat_ky.cong_ai_goi WHERE duong = 'LOCAL' GROUP BY loai_viec
                ), kiem AS (
                    SELECT loai_viec, %s = ANY(ly_do) AS dung,
                           row_number() OVER (PARTITION BY loai_viec ORDER BY luc DESC, id DESC) AS stt
                    FROM nhat_ky.cong_ai_goi
                    WHERE duong = 'CLOUD' AND da_gui AND ket_qua = 'DAT'
                      AND 'KIEM_XAC_SUAT' = ANY(ly_do_chuyen_cloud)
                      AND ((%s = ANY(ly_do)) <> (%s = ANY(ly_do)))
                ), tong AS (
                    SELECT loai_viec, count(*) AS so_kiem,
                           count(*) FILTER (WHERE stt <= %s) AS so_kiem_cua_so,
                           count(*) FILTER (WHERE stt <= %s AND dung) AS so_dung_cua_so
                    FROM kiem GROUP BY loai_viec
                ) SELECT loai_viec, coalesce(so_luot, 0), coalesce(so_kiem, 0),
                         coalesce(so_kiem_cua_so, 0), coalesce(so_dung_cua_so, 0)
                  FROM luot FULL JOIN tong USING (loai_viec)""",
                            (LOCAL_DUNG, LOCAL_DUNG, LOCAL_SAI, cua_so, cua_so))
                rows = cur.fetchall()
        return {ma: dict(so_luot=luot, so_kiem=kiem, so_kiem_cua_so=n, so_dung_cua_so=dung)
                for ma, luot, kiem, n, dung in rows}

    def ghi(self, ban_ghi: BanGhiCongAI) -> None:
        try:
            with self._ket_noi() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO nhat_ky.cong_ai_goi (
                                ma_yeu_cau, luc, loai_viec, duong, cloud, nha_cung_cap, model,
                                da_gui, so_ky_tu_gui, so_ky_tu_nhan, token_vao, token_ra,
                                thoi_gian_ms, chi_phi_uoc, ma_luot_mask, ly_do_chuyen_cloud,
                                ly_do_khong_gui, ket_qua, ly_do, trich_dan_hop_le,
                                so_truong_bi_loai, loi, phap_nhan_id, viec_id, de_xuat_id,
                                dau_vao_mask_hash, ket_qua_tom_tat
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, NULL
                            )""",
                            (ban_ghi.ma_yeu_cau, ban_ghi.luc, ban_ghi.loai_viec, ban_ghi.duong,
                             ban_ghi.duong == DUONG_CLOUD, ban_ghi.nha_cung_cap, ban_ghi.model,
                             ban_ghi.da_gui, ban_ghi.so_ky_tu_gui, ban_ghi.so_ky_tu_nhan,
                             ban_ghi.token_vao, ban_ghi.token_ra, ban_ghi.thoi_gian_ms,
                             ban_ghi.chi_phi_uoc_usd, ban_ghi.ma_luot_mask, list(ban_ghi.ly_do_chuyen_cloud),
                             ban_ghi.ly_do_khong_gui, ban_ghi.ket_qua, list(ban_ghi.ly_do),
                             ban_ghi.trich_dan_hop_le, ban_ghi.so_truong_bi_loai, ban_ghi.loi,
                             ban_ghi.phap_nhan_id, ban_ghi.viec_id, ban_ghi.de_xuat_id),
                        )
        except Exception as exc:  # noqa: BLE001 — không log thông báo/traceback có thể chứa dữ liệu hoặc DSN
            _LOG.error("Không ghi được nhật ký cổng AI (%s).", type(exc).__name__)
