"""Kiểm độc lập MASK-2b: 32 ca t9 và 41 câu t10, chỉ văn bản giả DEMO.

Chép literal bằng AST; không import/chạy script tham khảo hoặc phụ thuộc h2.
Bộ đo đi hết cổng SDK với CoreGia và quyền DEMO ngoài gói.
"""
import ast
import json
from pathlib import Path
import sys
import unicodedata

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'goi/e_mask'))

from ho_tro_mo_lich_su import mo_che as mo_che_lich_su
import pytest
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask import tai_nguyen, ten_nguoi
from e_mask import che_van_ban as xu_ly
from ho_tro_van_ban_lich_su import tao_app
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho
from ho_tro_kho_demo import KhoBoNho
from ho_tro_ngan import QuyenNganDemo


T9 = [('giữa nguyễn văn an và bên B', ['nguyenvanan']),
 ('Hợp đồng gửi nguyen van an trước ngày mai', ['nguyenvanan']),
 ('anh tran bao long đã ký', ['tranbaolong']),
 ('chị lê thị hoa (kế toán) đã nhận', ['lethihoa']),
 ('NGUYỄN VĂN AN ĐÃ KÝ', ['nguyenvanan']),
 ('NGUYEN VAN AN DA KY', ['nguyenvanan']),
 ('Ký bởi trần thị bích ngọc hôm nay', ['tranthibichngoc']),
 ('Ký bởi huỳnh đức thịnh hôm nay', ['huynhducthinh']),
 ('Ký bởi lâm quốc đạt hôm nay', ['lamquocdat']),
 ('Ký bởi tạ văn bình hôm nay', ['tavanbinh']),
 ('Ký bởi ung nho khoa hôm nay', ['ungnhokhoa']),
 ('Ký bởi hoàng long hôm nay', ['hoanglong']),
 ('Ký bởi phạm văn đồng thanh tùng hôm nay', ['phamvandongthanhtung']),
 ('nguyễn văn an là giám đốc', ['nguyenvanan']),
 ('Người ký là nguyễn văn an', ['nguyenvanan']),
 ('Người ký là nguyễn văn an.', ['nguyenvanan']),
 ('Gửi cho bên B, nguyễn văn an, và bên C', ['nguyenvanan']),
 ('Họ tên\tnguyễn văn an\tChức vụ\tgiám đốc', ['nguyenvanan']),
 ('Ký bởi nguyễn\nvăn\nan hôm nay', ['nguyenvanan']),
 ('Ký bởi ngu\u200byễn văn a\u200bn hôm nay', ['nguyenvanan']),
 ('Ký bởi nguyễn văn an1 hôm nay', ['nguyenvanan']),
 ('a. long đã ký', ['along']),
 ('c. hoa đã nhận hàng', ['choa']),
 ('john smith đã ký hợp đồng', ['johnsmith']),
 ('Ký bởi tên người nước ngoài michael johnson hôm nay', ['michaeljohnson']),
 ('ông nguyễn văn an và bà lê thị hoa', ['nguyenvanan', 'lethihoa']),
 ('hợp đồng với phan thanh hải ngày 1/1/2026', ['phanthanhhai']),
 ('đối tác đặng minh tuấn thanh toán 1.000.000 VND', ['dangminhtuan']),
 ('Vũ Thị Mai Anh', ['vuthimaianh']),
 ('vũ thị mai anh', ['vuthimaianh']),
 ('bùi xuân trường gửi thư', ['buixuantruong']),
 ('trần văn a ký', ['tranvana'])]

T10 = ['Thanh toán tại hà nội theo hợp đồng số 01/2026 ngày 30/10/2026.',
 'Công ty đã giao hàng tại hà nội và lê thị hoa đơn gốc.',
 'Lý do điều chỉnh là chênh lệch tỷ giá cuối kỳ.',
 'Số dư trương mục ngân hàng được đối chiếu hàng tháng.',
 'Phan bổ chi phí trả trước theo từng kỳ kế toán.',
 'Kế toán phân bổ chi phí đào tạo nhân viên trong quý.',
 'Mai sau khi nhận hóa đơn sẽ hạch toán vào tài khoản 331.',
 'Hồ sơ thanh toán gồm hóa đơn và biên bản nghiệm thu.',
 'Chi phí cao hơn dự toán 10.000.000 VND do lâm thời tăng giá.',
 'Doanh thu kim ngạch xuất khẩu sang châu á tăng 5%.',
 'Thái độ phục vụ của nhà thầu được đánh giá tốt.',
 'Đinh kèm theo hợp đồng là phụ lục số 1.',
 'Khoản vay ngắn hạn được trả vào cuối tháng 12.',
 'Chi phí lương tháng 10 là 500.000.000 VND.',
 'Bên A có trách nhiệm thanh toán trong vòng 30 ngày.',
 'Báo cáo tài chính hợp nhất năm 2026 được lập theo chuẩn mực.',
 'Lập dự phòng phải thu khó đòi theo thông tư hiện hành.',
 'Tài sản cố định hữu hình khấu hao theo đường thẳng.',
 'Hàng tồn kho được đánh giá theo giá gốc.',
 'Giá trị hợp lý của khoản đầu tư cao hơn giá gốc.',
 'Hợp đồng có hiệu lực kể từ ngày ký và kéo dài 12 tháng.',
 'Phương thức thanh toán là chuyển khoản trong 15 ngày.',
 'Trần nợ vay được phê duyệt bởi hội đồng quản trị.',
 'Hoàng hôn trên biển là hình ảnh trong báo cáo thường niên.',
 'Thuế giá trị gia tăng đầu vào được khấu trừ đầy đủ.',
 'Bùi nhùi và các vật tư khác được ghi nhận vào chi phí.',
 'Võ đoán trong ước tính kế toán cần tránh.',
 'Dương tính giả trong kiểm toán được xem xét lại.',
 'Vương quốc Anh là thị trường xuất khẩu lớn.',
 'Tạ ơn khách hàng đã tin tưởng sử dụng dịch vụ.',
 'Ngô nghê là cách nói; thực tế chi phí được ghi nhận đúng kỳ.',
 'Lương thực và thực phẩm là nhóm hàng chính.',
 'Hà nội và thành phố hồ chí minh là hai thị trường chính.',
 'Thanh lý tài sản cố định theo quyết định của hội đồng quản trị.',
 'Đoàn kiểm toán làm việc tại văn phòng trong 5 ngày.',
 'Cao su thiên nhiên là nguyên liệu chính của công ty.',
 'Tiền mặt tại quỹ cuối kỳ là 20.000.000 VND.',
 'Lý thuyết kế toán và thực hành được áp dụng.',
 'Phạm vi kiểm toán gồm các khoản mục trọng yếu.',
 'Trịnh trọng cam kết thực hiện đúng hợp đồng.',
 'Mạc định các điều khoản theo mẫu hợp đồng chuẩn.']

@pytest.fixture(autouse=True)
def tu_dien_sach():
    tai_nguyen.xoa_cache()
    tai_nguyen.nap_tu_goi()
    yield
    tai_nguyen.xoa_cache()


def khoa_doc_lap(chu):
    chu = unicodedata.normalize('NFD', chu.casefold().replace('đ', 'd'))
    return ''.join(c for c in chu if c.isalnum() and not unicodedata.combining(c))


def chay_core_gia(chu):
    ngan, quyen, core = NganBoNho(KHAI_NGAN), QuyenNganDemo(), CoreGia()
    viec = core.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': chu})
    quyen.cap(viec)
    core.chay(tao_app(ngan=ngan, quyen=quyen))
    return core.xem(viec)


@pytest.mark.parametrize('chu,ten', T9, ids=[f't9-{i:02d}' for i in range(1, 33)])
def test_t9_khong_phat_hanh_nguyen_ten(chu, ten, capsys):
    kq = chay_core_gia(chu)
    if kq['trang_thai'] == 'XONG':
        ket = kq['ket_qua']['van_ban_da_che']
        assert ket['con_sot'] == [] and ket['kiem_tien_ngay']
        assert all(t not in khoa_doc_lap(ket['van_ban']) for t in ten)
    else:
        assert kq['trang_thai'] == 'LOI'
        assert kq['loi']['ma'] == 'MASK_DINH_DANH_CHUA_DAT'
        assert kq.get('ket_qua') is None
    log = capsys.readouterr()
    assert all(t not in khoa_doc_lap(log.out + log.err) for t in ten)


@pytest.mark.parametrize('so,chu', list(enumerate(T10, 1)), ids=[f't10-{i:02d}' for i in range(1, 42)])
def test_t10_cau_thuong_va_ca_mo_ho(so, chu):
    kq = chay_core_gia(chu)
    if so in {2, 7}:  # Ca 2 mập mờ tên; ca 7 nhãn tài khoản cũ chặn cả số sổ cái 331.
        assert kq['trang_thai'] == 'LOI'
        assert kq['loi']['ma'] == 'MASK_DINH_DANH_CHUA_DAT'
        assert kq.get('ket_qua') is None
    else:
        assert kq['trang_thai'] == 'XONG', kq
        ket = kq['ket_qua']['van_ban_da_che']
        assert ket['van_ban'] == chu
        assert ket['so_cho_thay'] == 0 and ket['con_sot'] == []
        assert ket['kiem_tien_ngay']


def test_nguyen_van_73_ca_bang_ban_tham_khao():
    luu = Path(__file__).resolve().parents[1] / 'LUU-TRU/rv_mask_2b'
    for tep, ten, tap_mau in [('tan_cong_t9.py.txt', 'ATT', T9), ('bao_nham_t10.py.txt', 'S', T10)]:
        cay = ast.parse((luu / tep).read_text('utf-8'))
        goc = next(ast.literal_eval(n.value) for n in cay.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == ten for t in n.targets))
        assert tap_mau == goc
    assert len(T9) == 32 and len(T10) == 41


@pytest.mark.parametrize('ho', 'Ưng Âu Khúc Lục Thân Ninh Quan Ông Vi Mẫn Khổng Bế Nông Lò Hầu'.split())
@pytest.mark.parametrize('khong_dau', [False, True])
def test_ho_hiem_khong_bi_loai_nhu_tu_thuong(ho, khong_dau):
    ten = ho.lower() + ' nho khoa'
    if khong_dau:
        ten = ''.join(c for c in unicodedata.normalize('NFD', ten) if not unicodedata.combining(c))
    kq = xu_ly.che('Ký bởi ' + ten + ' hôm nay', [], KhoBoNho())
    assert not kq['gui_duoc'] or khoa_doc_lap(ten) not in khoa_doc_lap(kq['van_ban_da_che'])


@pytest.mark.parametrize('xung', ['a.', 'c.', 'ô.', 'b.', 'A.', 'C.', 'Ô.', 'B.',
                                 'anh', 'chị', 'ông', 'bà', 'mr', 'ms'])
@pytest.mark.parametrize('ten', ['long', 'zê rô', 'zê rô lạ'])
def test_danh_xung_1_den_3_am_tiet_ca_ngoai_danh_sach(xung, ten):
    chu = xung + ' ' + ten + ' đã ký'
    kho = KhoBoNho()
    kq = xu_ly.che(chu, [], kho)
    assert kq['gui_duoc'] and kq['so_cho_thay'] == 1
    assert khoa_doc_lap(ten) not in khoa_doc_lap(kq['van_ban_da_che'])
    mo = mo_che_lich_su(kq['van_ban_da_che'], kq['ma_yeu_cau'], kho)
    assert mo['mo_day_du'] and mo['van_ban_da_mo_che'] == chu


@pytest.mark.parametrize('dau', ['ký ', 'gửi ', 'với ', 'bởi ', 'giữa ', 'mr ', 'ms. '])
def test_latin_sau_ngu_canh_chan_bang_diem_va_khong_lo_noi_dung(dau):
    chu = dau + 'john smith'
    kq = xu_ly.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None
    muc = next(m for m in kq['con_sot'] if m.get('ly_do') == 'nghi tên người nước ngoài')
    assert 4 <= muc['diem'] < 8 and muc['can_cu']
    assert 'john' not in json.dumps(kq, ensure_ascii=False)
    assert 'smith' not in json.dumps(kq, ensure_ascii=False)


@pytest.mark.parametrize('chu', ['gửi an ly', 'bởi quan kong', 'với phan blake'])
def test_latin_co_ngu_canh_khong_duoc_mien_vi_trung_am_viet(chu):
    # Latin có thể trùng họ/âm tiết Việt; không để đường điểm thấp làm lọt.
    kq = xu_ly.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None
    assert any(m.get('ly_do') == 'nghi tên người nước ngoài' for m in kq['con_sot'])


@pytest.mark.parametrize('chu', ['báo cáo tài chính', 'phương thức thanh toán', 'thuế giá trị gia tăng',
                                'lý do điều chỉnh', 'thanh lý tài sản', 'đoàn kiểm toán',
                                'cao su thiên nhiên', 'báo cáo quản lý', 'gửi công văn', 'ký văn bản'])
def test_cum_thong_dung_o_dau_giua_cuoi_khong_bi_nhan_nham(chu):
    chu = 'Nội dung: ' + chu + '.'
    assert ten_nguoi.tim(chu) == []
    kq = xu_ly.che(chu, [], KhoBoNho())
    assert kq['gui_duoc'] and kq['van_ban_da_che'] == chu


def test_ba_muc_diem_va_canh_bao_co_can_cu_khong_chua_ten():
    assert ten_nguoi.tim('lý do điều chỉnh') == []
    vua = next(t for t in ten_nguoi.tim('gửi phan thanh hải') if t.gia_tri == 'phan thanh hải')
    cao = next(t for t in ten_nguoi.tim('anh phan thanh hải') if t.gia_tri == 'phan thanh hải')
    assert 4 <= vua.diem < 8 and vua.bat_buoc_duyet and not vua.tin_cay
    assert cao.diem >= 8 and cao.tin_cay and not cao.bat_buoc_duyet
    assert vua.can_cu and cao.can_cu


@pytest.mark.parametrize('chu', ['số 01/2026', 'hợp đồng số 01/2026', 'Số 01/2026 ngày 30/10/2026'])
def test_so_van_ban_khong_che_hoac_chan(chu):
    kq = xu_ly.che(chu, [], KhoBoNho())
    assert kq['gui_duoc'] and kq['so_cho_thay'] == 0
    assert kq['van_ban_da_che'] == chu and kq['kiem_tien_ngay']


def test_ngoai_le_so_van_ban_khong_mien_ma_co_hau_to_va_tai_khoan():
    for chu in ['hợp đồng số 01/2026/HD-DEMO', 'Tài khoản: 012345678901']:
        kq = xu_ly.che(chu, [], KhoBoNho())
        assert not kq['gui_duoc'] or kq['so_cho_thay'] > 0


def test_t10_do_day_du_ke_ca_bao_nham_duoi_10_phan_tram():
    # Đếm hợp chặn/che thừa trên TẤT CẢ 41 câu, kể cả câu mập mờ.
    bao_nham = []
    for i, chu in enumerate(T10, 1):
        kq = chay_core_gia(chu)
        vb = (kq.get('ket_qua') or {}).get('van_ban_da_che', {}).get('van_ban')
        if vb != chu:
            bao_nham.append(i)
    assert bao_nham == [2, 7]
    assert len(bao_nham) / len(T10) <= 0.10


def do_rv():
    """Đo cả chặn và che thừa, đếm hợp; không suy số đo từ test passed."""
    from e_mask.che_van_ban import _kiem_con_sot
    tai_nguyen.xoa_cache()
    tai_nguyen.nap_tu_goi()
    ket = {'t9': [], 't10': []}
    for i, (chu, ten) in enumerate(T9, 1):
        kq = chay_core_gia(chu)
        vb = (kq.get('ket_qua') or {}).get('van_ban_da_che', {}).get('van_ban')
        trang_thai = ('chan' if vb is None else
                      'lot' if any(t in khoa_doc_lap(vb) for t in ten) else 'che')
        ket['t9'].append({'ca': i, 'van_ban_demo': chu, 'loai': 'nuoc_ngoai' if i in {24, 25} else 'tieng_viet',
                          'ket_qua': trang_thai, 'ma_loi': (kq.get('loi') or {}).get('ma')})
    for i, chu in enumerate(T10, 1):
        kq = chay_core_gia(chu)
        vb = (kq.get('ket_qua') or {}).get('van_ban_da_che', {}).get('van_ban')
        trang_thai = 'chan' if vb is None else 'che_thua' if vb != chu else 'giu_nguyen'
        ly_do = _kiem_con_sot(chu, [])[0] if vb is None else []
        ket['t10'].append({'ca': i, 'van_ban_demo': chu, 'ket_qua': trang_thai,
                           'ma_loi': (kq.get('loi') or {}).get('ma'), 'ly_do': ly_do})
    ket['tom_tat'] = {'t9_so_ca': 32,
                     't9_lot': sum(c['ket_qua'] == 'lot' for c in ket['t9']),
                     't9_chan': sum(c['ket_qua'] == 'chan' for c in ket['t9']),
                     't9_che': sum(c['ket_qua'] == 'che' for c in ket['t9']),
                     't10_so_ca': 41,
                     't10_chan': sum(c['ket_qua'] == 'chan' for c in ket['t10']),
                     't10_che_thua': sum(c['ket_qua'] == 'che_thua' for c in ket['t10']),
                     't10_bao_nham': sum(c['ket_qua'] != 'giu_nguyen' for c in ket['t10'])}
    return ket


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--moc', required=True, choices=['rv_truoc', 'rv_sau'])
    args = p.parse_args()
    tep = Path(__file__).resolve().parents[1] / 'docs/SO-DO-MASK-2b.json'
    bao_cao = json.loads(tep.read_text('utf-8'))
    bao_cao[args.moc] = do_rv()
    tep.write_text(json.dumps(bao_cao, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(bao_cao[args.moc]['tom_tat'], ensure_ascii=False))
