"""Đo DEMO MASK-2b; tập âm tính gán nhãn thủ công, không ước lượng production."""
import argparse
import ast
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
THU_MUC = Path(__file__).resolve().parent
sys.path.insert(0, str(THU_MUC.parent / 'goi/e_mask'))
from e_mask import che_van_ban, tai_nguyen
from ho_tro_kho_demo import KhoBoNho


# Nguyên văn literal DEMO có sẵn, kiểm nguồn bằng AST ở mỗi lượt đo.
MAU_CU = {
    'test_che_van_ban.py': [
        '; thanh toán 1.000.000 VND ngày 30/10/2026.',
        'đơn vị demo xanh',
        'dữ liệu demo 0.00 ngày 30/10/2026',
        '0.00; 0,00; 0.000; 1.000.000 VND; 30/10/2026; 30/10/2026',
        'tổng tiền 1000000000 VND; ngày 30/10/2026',
        'ngày 30 tháng 10 năm 2026',
        'giá trị 0.00; 0,00; 0.000; 30/10/2026',
        '1.000.000 VND ngày 30/10/2026.',
        '; nội dung AI bổ sung.',
    ],
    'test_mask_1.py': [
        ' — nội dung DEMO giữ nguyên; ',
        '1.000.000 VND ngày 30/10/2026',
        '999.000 VND ngày 30/10/2026',
        '1.000.000 VND ngày 31/10/2026',
    ],
    'test_mask_2.py': ['nội dung'],
}

# Dữ liệu giả bổ sung: kế toán/hợp đồng, không tên người/tổ chức nhạy cảm.
CAU_KHONG_TEN = [
    'Bên A thanh toán 1.000.000 VND ngày 30/10/2026.',
    'Bên B bàn giao đủ chứng từ gốc theo hợp đồng.',
    'Kế toán ghi nhận doanh thu khi hoàn tất bàn giao.',
    'Hóa đơn được đối chiếu với biên bản nghiệm thu.',
    'Khoản phải thu đã được xác nhận vào cuối tháng.',
    'Chi phí trả trước được phân bổ trong kỳ kế toán.',
    'Hồ sơ thanh toán gồm hợp đồng và hóa đơn.',
    'Lý do điều chỉnh là sai đơn giá trên chứng từ.',
    'Lương tháng được hạch toán vào chi phí quản lý.',
    'Tăng doanh thu phải có chứng từ chứng minh.',
    'Lãi suất vay được giữ nguyên trong kỳ hợp đồng.',
    'Lệ phí được thanh toán theo quy định.',
    'Quá trình đối chiếu kéo dài lê thê trong kỳ.',
    'Đào tạo nghiệp vụ kế toán được tổ chức định kỳ.',
    'Đáo hạn khoản vay vào ngày 2026-10-30.',
    'Chu kỳ thanh toán được ghi tại phụ lục hợp đồng.',
    'Chủ nợ xác nhận số dư tại cuối kỳ.',
    'Chi phí kỳ này cao hơn kỳ trước.',
    'Hà Nội là địa điểm giao hàng trong phụ lục.',
    'ha noi la dia diem giao hang trong phu luc.',
    'Thuế GTGT được kê khai đúng kỳ.',
    'Công nợ phải trả được theo dõi theo thời hạn.',
    'Ngân sách dự kiến đã được phê duyệt nội bộ.',
    'Kiểm tra lại chứng từ trước khi ghi sổ.',
    'Ngày mai nộp báo cáo quyết toán theo kế hoạch.',
    'Hai bên thống nhất gia hạn thời gian thực hiện.',
    'Phụ lục có hiệu lực kể từ ngày ký.',
    'Tài sản cố định được khấu hao theo thời gian sử dụng.',
    'Giá trị hợp đồng là 1.000.000 VND và đã gồm thuế.',
    'Dữ liệu giả DEMO dùng để kiểm tra quy trình kế toán.',
]

CA_TEN = [
    'giữa nguyễn văn an và bên B',
    'anh tran bao long đã ký',
    'chị lê thị hoa (kế toán)',
    'gửi nguyen van an',
]


def mau_cu():
    for ten, ds in MAU_CU.items():
        chuoi = {n.value.strip() for n in ast.walk(ast.parse((THU_MUC / ten).read_text('utf-8')))
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        for chu in ds:
            assert chu.strip() in chuoi, (ten, chu)
            yield chu


def do_am_tinh(ds):
    chan, che = [], []
    for i, chu in enumerate(ds, 1):
        kq = che_van_ban.che(chu, [], KhoBoNho())
        if not kq['gui_duoc']:
            chan.append(i)
        if kq['so_cho_thay']:
            che.append(i)
    return {'so_mau': len(ds), 'so_chan_nham': len(chan), 'so_che_nham': len(che),
            'ti_le_bao_nham': len(set(chan + che)) / len(ds),
            'vi_tri_chan_nham': chan, 'vi_tri_che_nham': che}


def do():
    tai_nguyen.xoa_cache()
    tai_nguyen.nap_tu_goi()
    ket = {'am_tinh_co_san': do_am_tinh(list(mau_cu())),
           'am_tinh_bo_sung': do_am_tinh(CAU_KHONG_TEN), 'ten_nguoi': []}
    for i, chu in enumerate(CA_TEN, 1):
        kq = che_van_ban.che(chu, [], KhoBoNho())
        ket['ten_nguoi'].append({'ca': i, 'gui_duoc': kq['gui_duoc'],
                                'so_cho_thay': kq['so_cho_thay'],
                                'so_con_sot': len(kq['con_sot'])})
    return ket


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--moc', choices=['truoc', 'sau'], required=True)
    args = p.parse_args()
    tep = THU_MUC.parent / 'docs/SO-DO-MASK-2b.json'
    bao_cao = json.loads(tep.read_text('utf-8')) if tep.exists() else {}
    bao_cao[args.moc] = do()
    tep.write_text(json.dumps(bao_cao, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(bao_cao[args.moc], ensure_ascii=False, indent=2))
