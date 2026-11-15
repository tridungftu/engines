"""Đo khảo sát R3 ngoài gói; chỉ DEMO, không mạng/Local/Cloud.

Gold mới được đóng băng trước chạy. Đây không phải held-out có người soạn
độc lập của MASK-2c §6.6; không lấy số phát hành bằng 0 làm recall bằng 1.
Chạy: .venv/Scripts/python -B e_mask/tests/do_mask_r3.py
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic, perf_counter
import unicodedata
from uuid import uuid4

sys.dont_write_bytecode = True
GOI = Path(__file__).resolve().parents[1] / 'goi/e_mask'
sys.path.insert(0, str(GOI))

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia
from e_mask import che_van_ban as che, tai_nguyen
from e_mask.kho_dinh_danh import KhoDinhDanh
from e_mask.khoi_tao_ngan import PHIEN_BAN_CHUAN_HOA
from e_mask.tra_cuu_dinh_danh import TraCuuDinhDanh, UngVien
from ho_tro_ngan import QuyenNganDemo


def do():
    tep = Path(__file__).with_name('demo_mask_r3.json')
    bam = sha256(tep.read_bytes()).hexdigest()
    if bam != 'b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181':
        raise ValueError('Gold DEMO đã đổi; cần đóng băng lại trước phép đo.')
    gold = json.loads(tep.read_text(encoding='utf-8'))
    tai_nguyen.nap_tu_goi()
    tac_vu, ket, so_rpc = [], [], Counter()
    quyen = QuyenNganDemo()

    def dau_do(viec):
        quyen.cap(viec.id)
        # Spy chỉ đếm, không giữ đối số hoặc giá trị cột bí mật.
        tim = viec.ngan.tim
        def spy(bang, **kw):
            so_rpc[bang] += 1
            return tim(bang, **kw)
        viec.ngan.tim = spy
        try:
            ket.append(tac_vu.pop(0)(viec))
        finally:
            viec.ngan.tim = tim
        return {'loai': 'van_ban_da_che', 'van_ban_da_che': {
            'phien_ban': 1, 'van_ban': 'DEMO đầu dò ngoài gói', 'ma_yeu_cau': 'DEMO',
            'con_sot': [], 'kiem_tien_ngay': True, 'chuyen_tiep': {}}}

    app = Engine.tu_khai_bao(str(GOI / 'engine.json'))
    for nl in app.phieu['nang_luc']:
        app.nang_luc(nl['ma'])(dau_do)
    core = CoreGia(app)

    def chay(ham):
        tac_vu.append(ham)
        kq = core.chay_thu(app, 'mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': 'DEMO'})
        if kq['trang_thai'] != 'XONG':
            raise ValueError('Đầu dò DEMO gặp lỗi kỹ thuật.')
        return ket.pop()

    def nap(viec):
        with viec.ngan.lo() as lo:
            for i, (nhom, ten, _) in enumerate(gold['duong']):
                ma = uuid4().hex
                alias = '[[MASKDEMO-R3-' + str(i) + ']]'
                lo.them('dinh_danh', dict(id_dinh_danh=ma, vung_du_lieu='DEMO',
                    gia_tri_goc=ten, gia_tri_chuan=che.chuan_hoa(ten),
                    phien_ban_chuan_hoa=PHIEN_BAN_CHUAN_HOA, nhom=nhom,
                    trang_thai='CHINH_THUC', so_gap=1))
                lo.them('bi_danh', dict(id_bi_danh=uuid4().hex, id_dinh_danh=ma,
                    vung_du_lieu='DEMO', bi_danh=alias,
                    bi_danh_chuan=che.chuan_bi_danh(alias), trang_thai='CHINH_THUC'))
    chay(nap)

    def bien_the(ten, dang):
        if dang == 'nfd':
            return unicodedata.normalize('NFD', ten)
        if dang == 'cf_chen':
            return '\u200b'.join(ten)
        if dang == 'cf_thay_cach':
            return ten.replace(' ', '\u200b')
        if dang == 'viet_thuong':
            return ten.lower()
        return ten

    cac = []
    for dang in gold['bien_the']:
        for i, (nhom, ten, chu) in enumerate(gold['duong']):
            doi = bien_the(ten, dang)
            chu = chu.replace(ten, doi)
            a = chu.index(doi)  # Gold do người soạn cung cấp, không lấy từ detector.
            cac.append((('duong' if dang == 'goc' else dang), i, chu, (a, a + len(doi))))
    cac.extend(('am', i, chu, None) for i, chu in enumerate(gold['am']))
    bao_cao = []
    for nhom_do, i, chu, span in cac:
        # Đối chứng matcher cũ CHỈ ở công cụ DEMO ngoài gói. Danh mục lấy
        # từ fixture đã đóng băng, không liệt kê/giải mã ngăn Core để bù R3.
        nfc, toa_do = che._nfc_vi_tri(chu)
        bo_do_cu = che._BoDo(nfc)
        matcher_cu_che_du = span is not None and any(
            toa_do[a][0] <= span[0] and span[1] <= toa_do[b - 1][1]
            for _, ten, _ in gold['duong']
            for a, b in bo_do_cu.spans(ten, loose=True, masking=True))
        def thu(viec):
            kho = KhoDinhDanh(quyen=quyen).mo_kho_nhan_dien(viec)
            truoc = so_rpc.copy()
            dau = perf_counter()
            try:
                k = che.khao_sat_che_chinh_xac(chu, [], kho,
                    han_monotonic=monotonic() + 30, kiem_huy=viec.kiem_huy)
                che_du = span is not None and any(a <= span[0] and span[1] <= b
                                                  for a, b, _ in k.doi_chieu.phep_thay)
                bao_nham = span is None and bool(k.doi_chieu.phep_thay)
                chan = bool(k.con_sot) or not k.kiem_tien_ngay
                trang_thai = ('chan_nghiep_vu' if chan else
                    ('che_du' if che_du else 'lot_ban_khao_sat') if span else
                    ('bao_nham' if bao_nham else 'giu_nguyen'))
                return dict(trang_thai=trang_thai, gold_che_du=che_du, bao_nham=bao_nham,
                    so_ung_vien=k.doi_chieu.so_ung_vien, so_chua_co=k.doi_chieu.so_chua_co,
                    so_phep=len(k.doi_chieu.phep_thay), kiem_tien_ngay=k.kiem_tien_ngay,
                    giay=round(perf_counter() - dau, 6),
                    rpc=dict(so_rpc - truoc))
            except LoiNghiepVu as exc:
                loi_kt = exc.ma in {'MASK_UNG_VIEN_QUA_HAN', 'MASK_NGU_CANH_CHUA_XAC_MINH',
                                    'MASK_NGAN_CHUA_CO', 'MASK_KHO_CAN_CORE'}
                return dict(trang_thai='loi_ky_thuat' if loi_kt else 'chan_nghiep_vu', ma_loi=exc.ma,
                            giay=round(perf_counter() - dau, 6), rpc=dict(so_rpc - truoc))
            except Exception as exc:
                # Chỉ tên lớp, không thông điệp/traceback/đầu vào.
                return dict(trang_thai='loi_ky_thuat', ma_loi=type(exc).__name__,
                            giay=round(perf_counter() - dau, 6), rpc=dict(so_rpc - truoc))
        bao_cao.append(dict(nhom=nhom_do, ca=i, matcher_cu_che_du=matcher_cu_che_du, **chay(thu)))

    def bien_2000(viec):
        chu = ';'.join('demor3x' + str(i) for i in range(2001))
        l = TraCuuDinhDanh(chu, KhoDinhDanh(quyen=quyen).mo_kho_nhan_dien(viec),
                          han_monotonic=monotonic() + 30, kiem_huy=viec.kiem_huy)
        dau, a, truoc = perf_counter(), 0, so_rpc.copy()
        try:
            for i in range(2001):
                ten = 'demor3x' + str(i)
                l.them(UngVien(a, a + len(ten), 'KHAC', 'truong'))
                a += len(ten) + 1
        except LoiNghiepVu as exc:
            return dict(ma_loi=exc.ma, giay=round(perf_counter() - dau, 6), rpc=dict(so_rpc - truoc))
        finally:
            l.dong()

    tong = {}
    for nhom in dict.fromkeys(d['nhom'] for d in bao_cao):
        ds = [d for d in bao_cao if d['nhom'] == nhom]
        tong[nhom] = dict(so_ca=len(ds), trang_thai=dict(Counter(d['trang_thai'] for d in ds)),
            gold_che_du_ke_ca_bi_chan=sum(d.get('gold_che_du', False) for d in ds),
            matcher_cu_che_du=sum(d['matcher_cu_che_du'] for d in ds),
            bao_nham_ke_ca_bi_chan=sum(d.get('bao_nham', False) for d in ds),
            giay=round(sum(d['giay'] for d in ds), 6))
    def bien_500k(viec):
        chu = 'a ' * 250000
        dau, truoc = perf_counter(), so_rpc.copy()
        try:
            k = che.khao_sat_che_chinh_xac(chu, [],
                KhoDinhDanh(quyen=quyen).mo_kho_nhan_dien(viec),
                han_monotonic=monotonic() + 30, kiem_huy=viec.kiem_huy)
            return dict(ky_tu=len(chu), so_ung_vien=k.doi_chieu.so_ung_vien,
                        so_phep=len(k.doi_chieu.phep_thay), giay=round(perf_counter() - dau, 6),
                        rpc=dict(so_rpc - truoc), chan=bool(k.con_sot) or not k.kiem_tien_ngay)
        except LoiNghiepVu as exc:
            return dict(ky_tu=len(chu), ma_loi=exc.ma, giay=round(perf_counter() - dau, 6),
                        rpc=dict(so_rpc - truoc))

    return dict(phien_ban=1, gold_sha256=bam, moi_truong='SDK 2.2.0 / CoreGia / Windows / chỉ DEMO',
        gioi_han='Khảo sát RAM, chưa người soạn độc lập, chưa Local/Core thật; không chứng nhận độ phủ/chi phí.',
        phat_hanh_thuc_te=0, luot_local_thuc_te=0, tong=tong, bien_2000=chay(bien_2000),
        bien_500k=chay(bien_500k), cac_ca=bao_cao)


if __name__ == '__main__':
    chu = json.dumps(do(), ensure_ascii=False, indent=2) + '\n'
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(chu, encoding='utf-8', newline='\n')
    else:
        print(chu, end='')
