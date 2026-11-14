"""High-recall suggestion layers added in 2.3.0 (suggestions only; the user still reviews).

Each detector returns ``Finding`` objects. ``core.suggest`` turns them into rules. Nothing
here edits text. Capitalisation is tested with ``str.isupper()`` because character ranges
such as ``[A-ZÀ-Ỹ]`` miss many Vietnamese letters.
"""
from __future__ import annotations

import re
from bisect import bisect_left
from dataclasses import dataclass
from ... import tai_nguyen

from .company_names import GENERIC_WORDS, LEGAL_FORM, company_spans

SPACE = r"[^\S\n\t]+"  # spaces inside one line; tabs are column boundaries
WORD = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*")
NAME_GAP = re.compile(r"[^\S\n\t]{1,2}(?![^\S\n\t])")  # wider gaps are table columns


@dataclass(frozen=True)
class Finding:
    category: str
    source: str
    start: int = -1
    end: int = -1
    parent: str | None = None  # full name this alias/short form belongs to


def _lines(name: str) -> list[str]:
    return tai_nguyen.doc_dong(name)


@tai_nguyen.bo_nho
def surnames() -> tuple[frozenset, frozenset]:
    title, upper = set(), set()
    for line in _lines("vn_surnames.txt"):
        name, _, flag = line.partition(" ")
        title.add(name)
        if flag.strip() == "*":
            upper.add(name.upper())
    return frozenset(title), frozenset(upper)


@tai_nguyen.bo_nho
def places() -> frozenset:
    return frozenset(" ".join(line.split()).casefold() for line in _lines("vn_places.txt"))


@tai_nguyen.bo_nho
def acronyms() -> frozenset:
    return frozenset(word for line in _lines("common_acronyms.txt") for word in line.split())


def kiem_tai_nguyen():
    """Không coi văn bản không khớp mẫu là đã kiểm khi thiếu từ vựng."""
    from .leftovers import allowlist
    try:
        for doc in (surnames, places, acronyms, allowlist):
            doc()
    except Exception:
        raise tai_nguyen.ThieuTaiNguyen() from None


def fold(text: str) -> str:
    return " ".join(text.split()).casefold()


def is_cap(word: str) -> bool:
    return word[:1].isupper()


def cap_run(text: str, pos: int, max_words: int, case: str | None = None, stop=None) -> tuple[list[str], int]:
    """Consecutive capitalised words on one line. case='upper'|'title' keeps one style.

    ``stop`` (a regex) ends the run before a word where it matches, e.g. a job title.
    """
    words, end = [], pos
    while len(words) < max_words:
        if stop is not None and words and stop.match(text, pos):
            break
        match = WORD.match(text, pos)
        if not match or not is_cap(match.group()):
            break
        word = match.group()
        upper = word.isupper() and len(word) > 1
        if (case == "upper" and not word.isupper()) or (case == "title" and upper):
            break
        words.append(word)
        end = match.end()
        gap = NAME_GAP.match(text, end)
        if not gap:
            break
        pos = gap.end()
    return words, end


class Spans:
    """Merged, sorted spans with O(log n) overlap checks."""

    def __init__(self, spans=()):
        merged = []
        for a, b in sorted((a, b) for a, b in spans if a >= 0 and b > a):
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        self.starts = [a for a, _ in merged]
        self.ends = [b for _, b in merged]

    def hit(self, start: int, end: int) -> bool:
        index = bisect_left(self.starts, end) - 1
        return index >= 0 and self.ends[index] > start


def overlaps(start: int, end: int, spans) -> bool:
    if isinstance(spans, Spans):
        return spans.hit(start, end)
    return any(start < b and a < end for a, b in spans)


# ---- Identifiers ----------------------------------------------------------------------------

PHONE = re.compile(r"(?<![\w+])(?:\+84[ .-]?|0)\(?2\d{1,2}\)?(?:[ .-]?\d){7,8}(?![\d])")
PHONE_INTL = re.compile(r"(?<![\w+])\+(?!84)[1-9]\d{0,2}(?:[ .-]?\d){6,12}(?!\d)")
PHONE_PAREN = re.compile(r"(?<![\w])\(0?2\d{1,2}\)[ .-]?\d{3,4}[ .-]?\d{3,4}(?!\d)")
BARE_NUMBER = re.compile(r"(?<![\w.,/+-])\d{10,19}(?![\w.,/-])")
DOC_NUMBER = re.compile(r"(?<![\w/])\d{1,6}(?:/\d{2,4})?/[^\W\d_][\w.]*(?:-[\w.]+)*(?![\w/])")
PUBLIC_ISSUER = re.compile(r"/(?:[A-ZĐ]{1,3}-(?:UBND|HĐND|TTg|CP|NHNN|BTC|BCT|BYT|BXD|BGDĐT|BTNMT|BLĐTBXH|BTP|BNV|BCA|BQP|BKHĐT|BGTVT|BNNPTNT|BTTTT|BVHTTDL|BKHCN)|QH\d*|UBTVQH\d*|NĐ-CP|NQ-CP|QĐ-TTg|CT-TTg|TT-[A-ZĐ]+|TTLT-[A-ZĐ-]+|L-CTN|PL-UBTVQH\d*)$")
PUBLIC_DOC_BEFORE = re.compile(r"(?:bộ\s+luật|luật|nghị\s+định|thông\s+tư|nghị\s+quyết|pháp\s+lệnh|chỉ\s+thị)"
                               r"(?:\s+[^\W\d_]+){0,6}\s+(?:số\s+)?$", re.I)
DOC_LABEL_BEFORE = re.compile(r"(?:(?:^|\n)[^\S\n]*số[^\S\n]*[:：]|(?:hợp\s+đồng|phụ\s+lục|đơn\s+hàng|biên\s+bản|[uủ]y\s+quyền|"
                              r"quyết\s+định|thỏa\s+thuận|contract|agreement)[^\n]{0,30}(?:số|no\.?)[^\S\n]*[:：]?)"
                              r"[^\S\n]*$", re.I)
CERT_NUMBER = re.compile(r"(?<![\w-])\d{3,}(?:-\d+){2,}(?![\w-])")
ACCOUNT = re.compile(r"(?<!\w)(?:tài\s+khoản|STK|TK|A/C|account(?:\s+no\.?)?)(?:[^\S\n\t]+[^\W\d_]+){0,5}?"
                     r"[^\S\n\t]*[:：]?[^\S\n\t]*"
                     r"(?P<value>\d(?:[ .-]?\d){5,22})(?![\d])", re.I)
MONEY_NEAR = re.compile(r"^\s*(?:đ\b|đồng|vnđ|vnd|usd|triệu|tỷ|₫)", re.I)
MONEY = re.compile(r"\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?")  # 1.250.000.000 / 1,250,000.50
DATE = re.compile(r"\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}")

# ---- Số tiền viết liền, không dấu phân cách (MASK-2, Anh chốt: không che số tiền) ------------------
# Kiểm theo thứ tự (ca mơ hồ thì CHE):
# 1. Số bắt đầu bằng 0 (tài khoản, điện thoại, CCCD, MST…) → không bao giờ là số tiền.
# 2. Trường chứa số có nhãn định danh (tài khoản, TK, STK, A/C, CCCD, MST, mã…, điện thoại, số hợp đồng/hóa đơn…)
#    hoặc động từ chuyển tiền (chuyển, nộp, gửi, rút, nhận…) → là định danh, KỂ CẢ khi sau số có đơn vị tiền
#    («Tài khoản: 1903… VND»: VND/USD sau số tài khoản là loại tiền của tài khoản). Ngoại lệ duy nhất: «tài khoản»/
#    «TK» đứng NGAY sau «Số dư»/«Số tiền» và là nhãn định danh duy nhất của trường (không có động từ chuyển tiền),
#    từ đó tới số không có chữ số, sau số là đơn vị bằng chữ (đồng, đ, triệu, tỷ, ₫): «Số dư tài khoản 5000000000
#    đồng». «Số tiền chuyển vào tài khoản 1903… đồng», «Giá trị tài khoản 1903… đồng» → vẫn che.
# 3. Không có nhãn định danh: là số tiền khi có đơn vị tiền ngay sau («… đồng», «… VND»), hoặc trường chứa nó là
#    trường tiền — nhãn tiền («Tổng tiền thanh toán:», «Giá trị hợp đồng:», «Số dư:», thẻ hóa đơn điện tử
#    <ThTien>, <TgTTTBSo>…) rồi tới thẳng con số, giữa chỉ có từ của nhãn tiền, ngoặc đơn, «:»/«là»/«bằng số».
#    Nhãn tiền xa con số hoặc giữa có từ khác («Tiền điện kỳ trước của khách 1903…») → vẫn che (thà che thừa).
# Số ngay sau nhãn tài khoản/MST/điện thoại (lớp ACCOUNT, dấu vết) chỉ được coi là tiền khi có phần chia nhóm nghìn
# («TK 331 1.250.000.000 VND») hoặc đúng ngoại lệ ở bước 2 — xem `labelled_money`.
_MONEY_WORDS = (r"tiền|giá(?:\s+trị)?|tổng\s+cộng|cộng\s+tiền|doanh\s+thu|doanh\s+số|số\s+dư|dư\s+nợ|dư\s+có|"
                r"phải\s+trả|phải\s+thu|tạm\s+ứng|chi\s+phí|kinh\s+phí|ngân\s+sách|lương|thưởng|phí|lãi|vốn|thuế|"
                r"amount|total|subtotal|sum|price|balance|value|cost|fee|salary|"
                r"ThTien|DGia|TgTCThue|TgTThue|TgTTTBSo|TTCKTMai|TgTKCThue|TgTKhac|STCKhau|TgTien|SoTien|TienThue")
_MONEY_FILLER = (r"thanh\s+toán|hàng(?:\s+hóa)?|dịch\s+vụ|GTGT|VAT|trước|sau|chưa|đã|gồm|bao\s+gồm|còn\s+lại|còn|"
                 r"tổng|hợp\s+đồng|tháng|năm|quý|kỳ|cuối\s+kỳ|đầu\s+kỳ|đợt|gốc|bằng\s+số|số|phát\s+sinh|nợ|"
                 r"có|quyết\s+toán|nghiệm\s+thu|đề\s+nghị|được\s+duyệt|thực\s+tế|dự\s+toán|bán|mua|phụ\s+cấp|"
                 r"thực\s+lĩnh|thực\s+nhận|net|gross|due|paid|" + _MONEY_WORDS)
MONEY_FIELD = re.compile(
    rf"(?<!\w)(?:{_MONEY_WORDS})(?!\w)(?:[^\S\n\t]+(?:{_MONEY_FILLER})(?!\w)){{0,5}}"
    r"[^\S\n\t]*(?:\([^()\n\t]{0,40}\)[^\S\n\t]*)?(?:[:：=>]|\"[^\S\n\t]*:|là|bằng\s+số)?[^\S\n\t]*$", re.I)
CURRENCY_BEFORE = re.compile(r"(?<!\w)(?:vnđ|vnd|usd|eur)[^\S\n\t]*[:：]?[^\S\n\t]*$|₫[^\S\n\t]*$", re.I)
ID_LABEL = re.compile(
    r"(?<!\w)(?:tài\s+khoản|STK|TK|A/C|account|acc|số\s+thẻ|thẻ\s+số|CCCD|CMND|căn\s+cước|hộ\s+chiếu|passport|"
    r"định\s+danh|MST|MSDN|mã|điện\s+thoại|ĐT|SĐT|phone|tel|fax|hotline|hợp\s+đồng\s+số|số\s+hợp\s+đồng|"
    r"hóa\s+đơn\s+số|số\s+hóa\s+đơn|chứng\s+từ|tham\s+chiếu|ref|seri|serial|ID|"
    # động từ chuyển tiền: «chuyển tiền 1903…», «nộp tiền 1903…» có thể là số tài khoản → vẫn che
    r"chuyển|nộp|gửi|rút|nhận|CK|thụ\s+hưởng|beneficiary)(?!\w)", re.I)


# Vòng 3: ngoại lệ chỉ khi danh từ tài khoản đứng NGAY sau «Số dư»/«Số tiền» («Số dư tài khoản 5000000000 đồng») và
# là nhãn định danh duy nhất của trường — «Số tiền chuyển vào tài khoản 1903…», «Giá trị tài khoản 1903…» vẫn che.
MONEY_OWNER = re.compile(r"(?<!\w)(?:tổng\s+)?số\s+(?:dư|tiền)[^\S\n\t]+(?P<label>tài\s+khoản|TK)(?!\w)", re.I)
AMOUNT_WORD_AFTER = re.compile(r"^[^\S\n\t]*(?:đồng|đ\b|triệu|tỷ|₫)", re.I)


def money_context(text: str, start: int, end: int) -> bool:
    """`text[start:end]` (dãy chữ số viết liền) là số tiền theo ngữ cảnh — quy tắc ở khối chú thích phía trên."""
    if text[start:start + 1] == "0":
        return False
    line = text[text.rfind("\n", 0, start) + 1:start]
    field = re.split(r"[\t;|]", line)[-1][-90:]
    labels = list(ID_LABEL.finditer(field))
    if labels:
        owner = MONEY_OWNER.search(field)
        return bool(owner and len(labels) == 1 and labels[0].start() == owner.start("label")
                    and not re.search(r"\d", field[owner.start():]) and AMOUNT_WORD_AFTER.match(text[end:end + 10]))
    if MONEY_NEAR.match(text[end:end + 8]):
        return True
    return bool(MONEY_FIELD.search(field) or CURRENCY_BEFORE.search(field))


def labelled_money(text: str, start: int, end: int) -> bool:
    """Số ngay sau nhãn định danh (tài khoản, MST, điện thoại) chỉ là số tiền/ngày khi có phần chia nhóm nghìn hoặc
    là ngày («1.250.000.000», «15.03.2026»), hoặc đúng ngoại lệ «Số dư tài khoản 5000000000 đồng» (`money_context`).
    Đơn vị tiền phía sau một mình không đủ («Tài khoản: 1912345678901 VND» vẫn là số tài khoản); số bắt đầu bằng 0
    không bao giờ là tiền, kể cả có chia nhóm («Tài khoản: 001.234.567.890 VND»)."""
    value = text[start:end]
    if value[:1] == "0":
        return False
    if any(MONEY.fullmatch(part) or DATE.fullmatch(part) for part in value.split()):
        return True
    return value.isdigit() and money_context(text, start, end)


def _digits(text: str) -> str:
    return re.sub(r"\D", "", text)


def identifiers(text: str) -> list[Finding]:
    found = []
    for pattern in (PHONE, PHONE_PAREN):
        for m in pattern.finditer(text):
            digits = _digits(m.group())
            national = digits[2:] if m.group().startswith("+84") else digits.lstrip("0")
            if len(national) == 10 and national.startswith("2"):
                found.append(Finding("DIEN_THOAI", m.group(), m.start(), m.end()))
    for m in PHONE_INTL.finditer(text):
        found.append(Finding("DIEN_THOAI", m.group(), m.start(), m.end()))
    for m in ACCOUNT.finditer(text):
        # Đơn vị tiền sau số có nhãn tài khoản không đủ để coi là số tiền («Tài khoản: 1903… VND»): cần thêm phần
        # chia nhóm nghìn hoặc ngoại lệ «Số dư tài khoản … đồng» (MASK-2 vòng 2).
        if MONEY_NEAR.match(text[m.end():m.end() + 8]) and labelled_money(text, m.start("value"), m.end("value")):
            continue
        found.append(Finding("TAI_KHOAN", m["value"], m.start("value"), m.end("value")))
    for m in DOC_NUMBER.finditer(text):
        if not DOC_LABEL_BEFORE.search(text[max(0, m.start() - 45):m.start()]):
            continue  # e.g. "Văn bản số 133/2026/CV-HCN" is a reference the reader may need
        if PUBLIC_ISSUER.search(m.group()) or PUBLIC_DOC_BEFORE.search(text[max(0, m.start() - 40):m.start()]):
            continue  # laws, decrees, circulars are public references, not identifiers
        if any(c.isupper() for c in m.group().split("/", 1)[1]):
            found.append(Finding("HOP_DONG", m.group(), m.start(), m.end()))
    for m in CERT_NUMBER.finditer(text):
        if len(_digits(m.group())) >= 8:
            found.append(Finding("GIAY_TO", m.group(), m.start(), m.end()))
    for m in BARE_NUMBER.finditer(text):
        value = m.group()
        if money_context(text, m.start(), m.end()):
            continue  # số tiền viết liền («Tổng tiền thanh toán: 1250000000», «… đồng»): không che (MASK-2)
        if len(value) == 12 and value[0] == "0" and 1 <= int(value[:3]) <= 96:
            category = "GIAY_TO"  # 12-digit citizen ID: province code 001–096
        elif len(value) in {10, 11} and value.startswith(("03", "05", "07", "08", "09", "02")):
            continue  # phone numbers are handled by the phone patterns
        else:
            category = "TAI_KHOAN"
        found.append(Finding(category, value, m.start(), m.end()))
    return found


# ---- Organisations --------------------------------------------------------------------------

EN_SUFFIX = re.compile(
    r"(?<=[\s,])(?:Co\.,?\s*Ltd\.?|Company\s+Limited|Joint\s+Stock\s+Company|JSC|Corp(?:oration)?\.?|Inc\.?|LLC|"
    r"Pte\.?\s*Ltd\.?|Ltd\.?|LLP|PLC|GmbH|Holdings(?:\s+Pte\.?\s*Ltd\.?)?|Group)(?![\w])")
EN_WORD = re.compile(r"[^\W\d_][\w&.'’-]*")
PAREN_ABBR = re.compile(r"\s*\(\s*([^\W\d_][\w&.-]{1,24})\s*\)")
QUOTED_ALIAS = re.compile(
    r"(?:(?:sau\s+đây\s+)?(?:được\s+)?(?:gọi\s+tắt\s+là|gọi\s+là|viết\s+tắt\s+là)|hereinafter(?:\s+referred\s+to\s+as)?)"
    r"\s*[\"“'‘]([^\"”'’\n]{2,60})[\"”'’]", re.I)
PAREN_QUOTED = re.compile(r"\(\s*[\"“]([^\"”\n]{2,40})[\"”]\s*\)")
CUE = re.compile(r"(?<!\w)(?:bên|khách\s+hàng|đối\s+tác|nhà\s+cung\s+cấp|nhà\s+thầu|thương\s+hiệu|hãng)"
                 + SPACE, re.I)
ACRONYM_CUE = re.compile(r"(?<!\w)(?:của|do|với|cho|và|tại)" + SPACE, re.I)
GENERIC_ALIAS = re.compile(r"(?:bên\s+\w{1,4}|bên\s+(?:bán|mua|thuê|cho\s+thuê|giao|nhận)|chủ\s+đầu\s+tư|nhà\s+thầu|"
                           r"hợp\s+đồng|công\s+ty|ngân\s+hàng|khách\s+hàng|dự\s+án|the\s+\w+|party\s+\w)$", re.I)


def english_orgs(text: str) -> list[Finding]:
    found = []
    for suffix in EN_SUFFIX.finditer(text):
        words, pos = [], suffix.start()
        # Walk back over capitalised words on the same line.
        head = text[:pos]
        tokens = list(re.finditer(r"[^\W\d_][\w&.'’-]*|\S", head[max(0, pos - 120):]))
        offset = max(0, pos - 120)
        for token in reversed(tokens):
            value = token.group()
            between = head[offset + token.end():pos]
            if "\n" in between or "\t" in between or len(words) >= 6:
                break
            if value == "&" and words:
                words.insert(0, value)  # "Baker & Holt LLP"
                pos = offset + token.start()
                continue
            if not EN_WORD.fullmatch(value) or not is_cap(value):
                break
            words.insert(0, value)
            pos = offset + token.start()
        while words and words[0] == "&":
            words.pop(0)
            pos = text.index(words[0], pos) if words else pos
        if words and not all(w.upper() in acronyms() for w in words):
            source = text[pos:suffix.end()]
            found.append(Finding("CONG_TY", " ".join(source.split()), pos, suffix.end()))
    return found


def organisations(text: str) -> list[Finding]:
    spans = company_spans(text)
    found = [Finding("CONG_TY", s.source, s.start, s.end) for s in spans]
    taken = [(s.start, s.end) for s in spans]
    found += [f for f in english_orgs(text) if not overlaps(f.start, f.end, taken)]
    orgs = sorted(found, key=lambda f: f.start)
    # Abbreviation in parentheses directly after an organisation: "(Techcombank)".
    for org in orgs:
        m = PAREN_ABBR.match(text, org.end)
        if m and any(c.isupper() for c in m[1]) and m[1].upper() not in acronyms():
            found.append(Finding("CONG_TY", m[1], m.start(1), m.end(1), parent=org.source))
    # Quoted short names: (sau đây gọi là "Minh Long"), ("Sunrise").
    for pattern in (QUOTED_ALIAS, PAREN_QUOTED):
        for m in pattern.finditer(text):
            alias = " ".join(m[1].split()).strip(" .,")
            if len(alias) < 2 or GENERIC_ALIAS.fullmatch(alias) or not is_cap(alias):
                continue
            parent = next((o.source for o in reversed(orgs) if o.end <= m.start() and m.start() - o.end <= 80), None)
            found.append(Finding("CONG_TY", alias, m.start(1), m.end(1), parent=parent))
    # Brand names after a business cue: "bên Hưng Thịnh", "khách hàng Hưng Thịnh".
    for m in CUE.finditer(text):
        words, end = cap_run(text, m.end(), 4)
        if not words or (len(words) == 1 and (len(words[0]) <= 2 or words[0].isupper())):
            continue  # "Bên A", "BÊN BÁN:" are party labels
        if words[0].upper() in acronyms() or text[end:end + 2].lstrip().startswith((":", "：")):
            continue
        name = " ".join(words)
        if fold(name) not in places() and words[0] not in surnames()[0]:
            found.append(Finding("CONG_TY", name, m.end(), end))
    # Acronym-led names after a preposition: "của VNPT Technology".
    for m in ACRONYM_CUE.finditer(text):
        if not m.group().strip().islower():
            continue  # "LÝ DO ĐIỀU CHỈNH" is a heading, not "do <organisation>"
        words, end = cap_run(text, m.end(), 4)
        if (words and words[0].isupper() and words[0].isascii() and 3 <= len(words[0]) <= 8
                and words[0] not in acronyms()):
            found.append(Finding("CONG_TY", " ".join(words), m.end(), end))
    return found


STRIP_PREFIX = re.compile(r"^(?:(?:tổng\s+)?công\s+ty|tập\s+đoàn|ngân\s+hàng(?:\s+TMCP)?|cong\s+ty)\s+", re.I)
EN_TAIL = re.compile(r"\s+(?:group|jsc|corp(?:oration)?|holdings|co\.?,?\s*ltd\.?|ltd\.?|inc\.?|pte\.?\s*ltd\.?)$", re.I)


def short_names(text: str, parents: list[str], spans=()) -> list[Finding]:
    """Core name of a detected company when it also appears on its own: 'Minh Long'.

    At least one occurrence must lie outside every detected organisation span, so
    Text variants of the same full name do not produce a separate short form.
    """
    from .core import literal_pattern

    found, done = [], set()
    spans = spans if isinstance(spans, Spans) else Spans(spans)
    for parent in parents:
        if fold(parent) in done:
            continue
        done.add(fold(parent))
        core = STRIP_PREFIX.sub("", parent)
        form = LEGAL_FORM.match(core)
        if form:
            core = core[form.end():].strip()
        core = EN_TAIL.sub("", core).strip()
        words = core.split()
        while words and words[0].casefold() in GENERIC_WORDS:
            words.pop(0)
        candidates = [" ".join(words[i:]) for i in range(0, max(1, len(words) - 1))]
        for candidate in candidates:
            parts = candidate.split()
            if (len(parts) < 2 or all(p.casefold() in GENERIC_WORDS for p in parts) or not is_cap(parts[0])
                    or fold(candidate) in places()):
                continue
            hit = next((m for m in re.finditer(literal_pattern(candidate), text, re.I)
                        if is_cap(m.group()) and not spans.hit(m.start(), m.end())), None)
            if hit:
                found.append(Finding("CONG_TY", candidate, hit.start(), hit.end(), parent=parent))
                break
    return found


# ---- People ---------------------------------------------------------------------------------

HONORIFIC = re.compile(r"(?<!\w)(?:anh|chị|ông|bà|cô|chú|bác|em|mr|ms|mrs|dr|luật\s+sư|ls|ts|ths|pgs|gs|kỹ\s+sư|ks)"
                       r"\.?" + SPACE, re.I)
PERSON_LABEL = re.compile(
    r"(?<!\w)(?:người\s+liên\s+hệ|người\s+ký|người\s+lập|người\s+nhận|người\s+đề\s+nghị|người\s+đại\s+diện|"
    r"kiểm\s+toán\s+viên|chủ\s+(?:tài\s+khoản|TK)|người\s+thụ\s+hưởng|account\s+name|beneficiary|tôi\s+là|tôi\s+tên\s+là|[uủ]y\s+quyền\s+cho|họ\s+(?:và\s+)?tên|from|to|cc|attn)"
    r"(?!\w)[^\S\n\t]*[:：]?[^\S\n\t]*", re.I)
ADDRESS_BEFORE = re.compile(
    r"(?:đường|phố|quận|huyện|phường|xã|tỉnh|thành\s+phố|tp\.?|thị\s+xã|thị\s+trấn|số|ngõ|ngách|hẻm|kiệt|"
    r"khu|ấp|thôn|xóm|tòa\s+nhà|chung\s+cư|\d+[A-Za-z]?(?:/\d+)*)[^\S\n\t]*[,.]?[^\S\n\t]*$", re.I)
NOT_GIVEN = set("sơ do lịch luận tạo thuyết tưởng trí nghiệp khoản động toán giá phí hợp sản ban phòng nội phán cấm "
                "túc quốc".split())
ROLE_PHRASE = re.compile(r"(?<!\w)(?:giám\s+đốc|tổng\s+giám|phó\s+tổng|trưởng\s+phòng|kế\s+toán|chủ\s+tịch|thư\s+ký|"
                        r"công\s+ty|tập\s+đoàn|ngân\s+hàng)(?!\w)", re.I)


def _person_ok(words: list[str], start: int, text: str, case: str) -> bool:
    name = " ".join(words)
    if fold(name) in places() or ADDRESS_BEFORE.search(text[max(0, start - 30):start]):
        return False
    rest = [w.casefold() for w in words[1:]]
    if ROLE_PHRASE.search(name):
        return False
    if case == "upper" and (len(words) < 3 or rest[0] in NOT_GIVEN):
        return False
    ascii_only = all(w.isascii() for w in words)
    if ascii_only and len(words) < 3:
        return False
    return 2 <= len(words) <= 4


def _ascii(text: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn").replace("Đ", "D")


@tai_nguyen.bo_nho
def _ascii_surnames() -> frozenset:
    return frozenset(_ascii(s) for s in surnames()[0] if len(_ascii(s)) > 2)


def people(text: str, blocked=()) -> list[Finding]:
    blocked = blocked if isinstance(blocked, Spans) else Spans(blocked)
    title, upper = surnames()
    ascii_title = _ascii_surnames()  # computed once, not for every text/cell
    found = []
    for match in WORD.finditer(text):
        word = match.group()
        if word in title or word in ascii_title:
            case = "title"
        elif word in upper:
            case = "upper"
        else:
            continue
        if overlaps(match.start(), match.end(), blocked):
            continue
        words, end = cap_run(text, match.start(), 4, case, stop=ROLE_PHRASE)
        if word in ascii_title and not all(w.isascii() for w in words):
            continue
        if _person_ok(words, match.start(), text, case):
            found.append(Finding("CA_NHAN", " ".join(words), match.start(), end))
    for pattern in (HONORIFIC, PERSON_LABEL):
        for m in pattern.finditer(text):
            words, end = cap_run(text, m.end(), 4, stop=ROLE_PHRASE)
            if not words or overlaps(m.end(), end, blocked):
                continue
            if words[0].casefold() in {"công", "tập", "ngân", "tổng", "bệnh", "các", "quý"}:
                continue
            name = " ".join(words)
            if fold(name) in places() or ROLE_PHRASE.search(name):
                continue
            if len(words) == 1:
                phrase = " ".join(text[m.start():end].split())
                # A lone surname ("Ông Nguyễn" + line break) is a wrapped full name, not a given name.
                if (pattern is HONORIFIC and len(words[0]) >= 2 and not words[0].isupper()
                        and fold(phrase) not in places() and words[0] not in surnames()[0]):
                    found.append(Finding("CA_NHAN", phrase, m.start(), end))
                continue
            found.append(Finding("CA_NHAN", name, m.end(), end))
    return found


def linked_people(findings: list[Finding]) -> list[Finding]:
    """'Mai Anh' / 'anh Thắng' → the one full name that ends with it."""
    full = {f.source for f in findings if f.category == "CA_NHAN" and len(f.source.split()) >= 3}
    result = []
    for f in findings:
        if f.category != "CA_NHAN" or f.parent:
            result.append(f)
            continue
        tail = f.source.split()
        if HONORIFIC.match(f.source + " "):
            tail = tail[1:]
        owners = [n for n in full if n != f.source and len(n.split()) > len(tail)
                  and [w.casefold() for w in n.split()[-len(tail):]] == [w.casefold() for w in tail]]
        result.append(Finding(f.category, f.source, f.start, f.end, parent=owners[0]) if len(owners) == 1 else f)
    return result


# ---- Addresses and projects -----------------------------------------------------------------

ADDRESS_LABEL = re.compile(r"(?<!\w)(?:nơi\s+thường\s+trú|thường\s+trú|nơi\s+ở(?:\s+hiện\s+(?:nay|tại))?|chỗ\s+ở|"
                           r"địa\s+chỉ\s+liên\s+hệ|dia\s+chi|tru\s+so|address)\s*[:：]\s*(?P<value>[^\n\t;]{4,180})", re.I)
ADMIN = re.compile(r"(?<!\w)(?:phường|quận|huyện|xã|tp\.?|thành\s+phố|tỉnh|thị\s+xã|thị\s+trấn|p\.|q\.)(?!\w)", re.I)
STARTER = re.compile(r"(?<![\w/.,])(?:(?:tầng|lầu|phòng|tòa\s+nhà|số|ngõ|ngách|hẻm|kiệt|lô|căn\s+hộ|thôn|ấp|xóm)"
                     + SPACE + r"[\w/-]+|\d+[A-Za-z]?(?:/\d+[A-Za-z]?)*(?=" + SPACE + r"[^\W\d_]))", re.I)
PART_WORD = re.compile(r"[^\W\d_]+\.?|\d+[A-Za-z]?(?:/\d+)*")
LOWER_OK = re.compile(r"(?:tầng|lầu|phòng|tòa|nhà|số|ngõ|ngách|hẻm|kiệt|lô|căn|hộ|thôn|ấp|xóm|đường|phố|phường|"
                      r"quận|huyện|xã|tỉnh|thành|thị|trấn|tp\.?|p\.|q\.)$", re.I)


def _address_part(text: str, pos: int) -> int:
    """End of one comma-separated address part: capitalised words, numbers, address nouns."""
    end, count = pos, 0
    while True:
        m = PART_WORD.match(text, pos)
        if not m:
            break
        token = m.group()
        if not (token[0].isdigit() or is_cap(token) or LOWER_OK.fullmatch(token)):
            break
        end, count = m.end(), count + 1
        gap = re.compile(SPACE).match(text, end)
        if not gap or count > 8:
            break
        pos = gap.end()
    return end if count else pos


def addresses(text: str) -> list[Finding]:
    found = []
    for m in ADDRESS_LABEL.finditer(text):
        value = re.split(r"\s+(?:điện\s+thoại|đt|email|mst)\s*[:：]", m["value"], flags=re.I)[0].strip(" .,-")
        found.append(Finding("DIA_CHI", value, m.start("value"), m.start("value") + len(value)))
    covered = [(f.start, f.end) for f in found]
    for m in STARTER.finditer(text):
        if overlaps(m.start(), m.end(), covered):
            continue
        end = _address_part(text, m.start())
        parts = 1
        while True:
            comma = re.compile(r"[^\S\n\t]*,[^\S\n\t]*").match(text, end)
            if not comma:
                break
            nxt = _address_part(text, comma.end())
            if nxt == comma.end():
                break
            end, parts = nxt, parts + 1
        value = text[m.start():end].strip(" ,.")
        tail = fold(value.rsplit(",", 1)[-1])
        if parts >= 3 and (ADMIN.search(value) or tail in places()):
            found.append(Finding("DIA_CHI", value, m.start(), m.start() + len(value)))
            covered.append((m.start(), end))
    return found


PROJECT = re.compile(r"(?<!\w)(?:dự\s+án|khu\s+đô\s+thị|khu\s+dân\s+cư)"
                     + SPACE, re.I)


def projects(text: str) -> list[Finding]:
    found = []
    for m in PROJECT.finditer(text):
        pos = m.end()
        again = PROJECT.match(text, pos)  # "Dự án Khu đô thị Ecopark Grand"
        if again:
            pos = again.end()
        words, end = cap_run(text, pos, 5)
        if len(words) == 1 and re.match(r"[^\S\n\t]+[^\W\d_]", text[end:end + 3]) and text[end:].split()[0].islower():
            continue  # "dự án Đầu tư xây dựng" is a description, not a project name
        if words and not (len(words) == 1 and words[0].isupper() and words[0] in acronyms()):
            name = " ".join(words)
            if fold(name) not in places():
                found.append(Finding("DU_AN", name, pos, end))
    return found


def detect(text: str) -> list[Finding]:
    """All 2.3.0 layers for one text, in priority order (earlier wins on duplicates)."""
    kiem_tai_nguyen()
    ids = identifiers(text)
    orgs = organisations(text)
    addr = addresses(text)
    blocked = Spans((f.start, f.end) for f in orgs + addr)
    persons = linked_people(people(text, blocked))
    org_spans = [(f.start, f.end) for f in orgs if not f.parent and f.start >= 0]
    shorts = short_names(text, [f.source for f in orgs if not f.parent], org_spans)
    return ids + addr + orgs + shorts + persons + projects(text)


# ---- Dấu vết định danh sau khi che (MASK-2) ---------------------------------------------------------
# Viết lại phép kiểm `AnDanh.dau_vet()` của engine #6 (review hồ sơ xây dựng, `trich_xuat/cloud.py`, chỉ đọc):
# quét BẢN ĐÃ CHE theo các mẫu định danh của AnDanh; còn khớp = còn sót mảnh định danh, lượt API không gửi.
# Khác AnDanh: bỏ đúng những thứ Mask v2 cố ý giữ (số tiền, ngày, văn bản pháp luật công khai, tổng đài 1800/1900,
# địa danh, cụm chỉ gồm loại hình doanh nghiệp như «Công ty TNHH») để không chặn nhầm. Bí danh phải được thay bằng
# ký tự không phải chữ/số/khoảng trắng (\x00) trước khi gọi, như `leftovers()`.
_LABEL_TAIL = r"[^\S\t]*(?:là|[:：])?[^\S\t]*"


def _number(least: int, extra: str = "") -> str:
    return rf"\d(?:[\d.\-{extra}]|[^\S\t]){{{least},}}\d"


TRACE_LABELLED = (
    ("MA_SO_THUE", re.compile(r"(?<!\w)(?:mã\s+số\s+thuế|mã\s+số\s+doanh\s+nghiệp|MST|MSDN)(?!\w)" + _LABEL_TAIL
                              + rf"(?P<value>{_number(7)})", re.I)),
    ("TAI_KHOAN", re.compile(r"(?<!\w)(?:số\s+tài\s+khoản|tài\s+khoản\s+số|tài\s+khoản|STK|TK\s+số|TK)(?!\w)"
                             + _LABEL_TAIL + rf"(?P<value>{_number(5)})", re.I)),
    ("DIEN_THOAI", re.compile(r"(?<!\w)(?:điện\s+thoại|ĐTDĐ|SĐT|ĐT|di\s+động|tel|fax|hotline)(?!\w)" + _LABEL_TAIL
                              + rf"(?P<value>\+?{_number(7, '()')})", re.I)),
    ("DIEN_THOAI", re.compile(r"(?<![\d.,])(?P<value>0\d{2,3}(?:[.]|[^\S\t])?\d{3}(?:[.]|[^\S\t])?\d{3,4})(?![\d.,])")),
    ("EMAIL", re.compile(r"(?<![\w.+-])(?P<value>[\w.+-]+@[\w-]+(?:\.[\w-]+)+)")),
    ("HOP_DONG", re.compile(r"(?<![\w/])(?P<value>\d{1,6}/\d{2,4}/[\w\-/.]*[^\W\d_][\w\-/.]*)")),
    ("HOP_DONG", re.compile(r"(?<!\w)(?:hợp\s+đồng|HĐ)[^\S\n\t]*(?:số|so)(?!\w)" + _LABEL_TAIL
                            + r"(?P<value>[\w\-/.]*\d[\w\-/.]*)", re.I)),
    ("CONG_TY", re.compile(r"(?<![\w&.'-])(?P<value>(?:[A-Z][A-Z0-9&.'\-]*[^\S\n\t]+){1,8}(?:CO\.?,?[^\S\n\t]*LTD\.?|"
                           r"COMPANY[^\S\n\t]+LIMITED|CORPORATION|CORP\.|JOINT[^\S\n\t]+STOCK[^\S\n\t]+COMPANY|JSC|"
                           r"INC\.|LIMITED|LLC|GMBH|PTE\.?[^\S\n\t]*LTD\.?))(?![\w])")),
)
TRACE_PERSON = re.compile(r"(?<!\w)(?:Ông/Bà|Ông\s*\(Bà\)|Ông|Bà|Mr\.?|Ms\.?|Mrs\.?)[^\S\n\t]+")
TRACE_COMPANY = re.compile(r"(?<!\w)(?:tổng\s+công\s+ty|công\s+ty|tập\s+đoàn|chi\s+nhánh|liên\s+danh)(?!\w)", re.I)
# Từ nối trong tên doanh nghiệp (theo AnDanh) và từ chỉ loại hình/chung chung: đi tiếp nhưng không phải phần tên riêng.
TRACE_CONNECT = frozenset(
    "cổ phần trách nhiệm hữu hạn một hai thành viên trở lên và xây dựng đầu tư thương mại dịch vụ phát triển kỹ "
    "thuật công nghệ sản xuất vấn thiết kế môi trường cơ khí điện nước hạ tầng giao thông kinh doanh - & tnhh mtv cp "
    "jsc tmcp ngân hàng nhà ban quản lý dự án chi nhánh văn phòng đại diện miền bắc nam trung khu vực số".split())
SERVICE_NUMBER = re.compile(r"1[89]00\d{4,6}")


def _company_trace(text: str, match) -> str | None:
    """«Công ty …» + các từ viết hoa / từ nối (cách nhau một dấu cách) — như `tim_cong_ty` của AnDanh; cần ít nhất
    một từ là tên riêng (không phải loại hình, từ chung, viết tắt thông dụng hay địa danh)."""
    if not match.group()[0].isupper():
        return None
    end, names = match.end(), []
    for token in re.finditer(r"\S+", text[match.end():match.end() + 200]):
        if match.end() + token.start() - end > 1:
            break  # chỉ đi tiếp qua đúng một dấu cách
        word = token.group()
        core = word.rstrip(",.;:)")
        if not core or not (core[0].isupper() or core[0].isdigit() or core.casefold() in TRACE_CONNECT):
            break
        if core[0].isupper() and core.casefold() not in TRACE_CONNECT and core.casefold() not in GENERIC_WORDS \
                and core.upper() not in acronyms() and core != "Bên":
            names.append(core)
        end = match.end() + token.start() + len(core)
        if core != word or len(names) >= 15:
            break
    if not names or fold(" ".join(names)) in places():
        return None
    return " ".join(text[match.start():end].split())


def traces(text: str) -> list[tuple[str, str]]:
    """(nhóm, cụm) còn trông như định danh trong bản đã che (bí danh đã thay bằng \x00)."""
    found = []
    kiem_tai_nguyen()
    for category, pattern in TRACE_LABELLED:
        for m in pattern.finditer(text):
            value = m["value"].strip().rstrip(".-/")
            start = m.start("value")
            labelled = category in {"MA_SO_THUE", "TAI_KHOAN", "DIEN_THOAI"}
            if labelled and labelled_money(text, start, start + len(value)):
                continue  # chỉ số chia nhóm nghìn, ngày, «Số dư tài khoản … đồng»; đơn vị tiền phía sau không đủ
            if category == "DIEN_THOAI" and SERVICE_NUMBER.fullmatch(_digits(value)):
                continue  # tổng đài 1800/1900: số công khai
            if category == "HOP_DONG" and (len(value) < 3 or DATE.fullmatch(value) or PUBLIC_ISSUER.search(value)
                                           or PUBLIC_DOC_BEFORE.search(text[max(0, m.start() - 40):m.start()])):
                continue  # văn bản pháp luật công khai, ngày, số quá ngắn
            if category == "CONG_TY" and all(w.upper() in acronyms() for w in value.split()[:-1]):
                continue
            found.append((category, " ".join(value.split())))
    for m in TRACE_PERSON.finditer(text):
        words, _ = cap_run(text, m.end(), 5, stop=ROLE_PHRASE)
        if len(words) < 2 or words[0].casefold() in {"công", "tập", "ngân", "tổng", "bệnh", "các", "quý"}:
            continue
        name = " ".join(words)
        if fold(name) in places() or fold(f"{m.group().strip()} {words[0]}") in places():
            continue  # «Bà Rịa», «Bà Đen»: địa danh
        found.append(("CA_NHAN", name))
    for m in TRACE_COMPANY.finditer(text):
        value = _company_trace(text, m)
        if value:
            found.append(("CONG_TY", value))
    return found
