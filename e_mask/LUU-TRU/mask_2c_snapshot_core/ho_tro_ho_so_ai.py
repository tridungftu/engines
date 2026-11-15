"""Adapter kho tệp CoreGia DEMO, ngoài gói; không chứng nhận ACL Core thật."""
from threading import RLock

from kho_tri_thuc_sdk.thu import CoreGia

from e_mask.ho_so_ai import ThamChieuHoSo, bam_bytes


class CongHoSoCoreGiaDemo:
    def __init__(self, core=None):
        self.core = core or CoreGia()
        self._khoa = RLock()
        self._ve, self._chu, self._tham_chieu, self._theo_bam = set(), {}, {}, {}
        self.thu_hoi = False

    @staticmethod
    def chu(viec, ctx):
        return (ctx.ma_yeu_cau, ctx.phien, ctx.module, ctx.nguoi_gui, ctx.tai_lieu,
                ctx.vung, viec.ngu_canh['phap_nhan_id'])

    def cap(self, viec, ctx):
        with self._khoa:
            self._ve.add(self.chu(viec, ctx))

    def kiem_quyen(self, viec, ngu_canh, *, tham_chieu, thao_tac):
        with self._khoa:
            viec.kiem_huy()
            chu = self.chu(viec, ngu_canh)
            return (not self.thu_hoi and chu in self._ve
                    and (tham_chieu is None or (self._chu.get(tham_chieu.tep_id) == chu
                         and self._tham_chieu.get(tham_chieu.tep_id) == tham_chieu)))

    def luu(self, viec, ngu_canh, du_lieu):
        with self._khoa:
            if not self.kiem_quyen(viec, ngu_canh, tham_chieu=None, thao_tac='luu'):
                raise ValueError('DEMO quyền đã thu hồi')
            chu = self.chu(viec, ngu_canh)
            khoa = (chu, bam_bytes(du_lieu))
            if khoa not in self._theo_bam:
                ref = ThamChieuHoSo(**self.core.them_tep('mask-2c-ho-so.json', du_lieu,
                                                       'application/json'))
                self._chu[ref.tep_id] = chu
                self._tham_chieu[ref.tep_id] = ref
                self._theo_bam[khoa] = ref
            return self._theo_bam[khoa]

    def doc(self, viec, ngu_canh, tham_chieu):
        with self._khoa:
            if not self.kiem_quyen(viec, ngu_canh, tham_chieu=tham_chieu, thao_tac='doc'):
                raise ValueError('DEMO tệp không được cấp quyền')
            return self.core.doc_tep(tham_chieu.tep_id)
