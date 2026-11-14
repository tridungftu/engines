"""Bounded Vietnamese company-name spans, without altering source text.

This is deliberately a rule-based candidate detector, not general-purpose NER.
Each candidate retains its exact source offsets; only the displayed rule folds
whitespace. Punctuation, labels and sentence predicates stay outside the span.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# Tabs are structural column boundaries, not a safe way to join a company name.
SPACE = r"[^\S\t]+"
COMPANY = re.compile(rf"(?<!\w)(?:(?:tổng{SPACE})?công{SPACE}ty|(?:tong{SPACE})?cong{SPACE}ty|cty\.?|chi{SPACE}nhánh)(?!\w)", re.I)
# 2.3.0: other organisation types. These need a capitalised first name word, so ordinary
# sentences such as "Ngân hàng thông báo..." are not taken as names.
ORGANISATION = re.compile(
    rf"(?<!\w)(?:tập{SPACE}đoàn|ngân{SPACE}hàng(?:{SPACE}TMCP)?|hợp{SPACE}tác{SPACE}xã|HTX|"
    rf"doanh{SPACE}nghiệp{SPACE}tư{SPACE}nhân|DNTN|văn{SPACE}phòng{SPACE}luật{SPACE}sư|công{SPACE}ty{SPACE}luật|"
    rf"bệnh{SPACE}viện|trường{SPACE}(?:đại{SPACE}học|cao{SPACE}đẳng)|quỹ|tap{SPACE}doan|ngan{SPACE}hang)(?!\w)", re.I)
# Public bodies after "và": "Công ty X và Ban Quản lý dự án ..." are two parties.
PUBLIC_BODY = re.compile(rf"(?:ban|sở|bộ|cục|tổng{SPACE}cục|ủy{SPACE}ban|uỷ{SPACE}ban|UBND|chi{SPACE}cục)(?!\w)", re.I)
# Table cells: a long number (tax ID, amount) after a name is another column.
NUMBER_CELL = re.compile(r"\d[\d.,]{4,}(?!\w)|\d{1,2}/\d{1,2}(?:/\d{2,4})?(?![\w/])")
# Public institutions are not confidential counterparties.
PUBLIC_ORG = re.compile(rf"ngân{SPACE}hàng{SPACE}nhà{SPACE}nước|ngân{SPACE}hàng{SPACE}chính{SPACE}sách{SPACE}xã{SPACE}hội|"
                        rf"kho{SPACE}bạc{SPACE}nhà{SPACE}nước", re.I)
# A new line that starts with a label, a list marker or an article number ends a name.
NEXT_LINE_BREAK = re.compile(r"\n[^\S\n]*(?:[^\n:：]{1,40}[:：]|[-•*+]|\d+[.)]|điều\s+\d|article\s+\d)", re.I)
LEGAL_FORM = re.compile(
    rf"(?:cổ{SPACE}phần|CP|TNHH(?:{SPACE}(?:MTV|một{SPACE}thành{SPACE}viên|"
    rf"hai{SPACE}thành{SPACE}viên(?:{SPACE}trở{SPACE}lên)?))?|"
    rf"trách{SPACE}nhiệm{SPACE}hữu{SPACE}hạn(?:{SPACE}(?:một|hai){SPACE}thành{SPACE}viên)?)"
    r"(?!\w)", re.I,
)
# Preserve punctuation inside brand words (ABC.JSC, A&B, 3/2); sentence-final
# punctuation and parentheses are not included in the company-name span.
WORD = re.compile(r"\w+(?:[.&/'’\-]\w+)*", re.UNICODE)


def phrase(expression: str) -> re.Pattern:
    return re.compile(r"(?:" + expression.replace(" ", SPACE) + r")(?!\w)", re.I)


# Strong field labels and predicates. Avoid cutting on an isolated business
# activity such as 'thanh toán', 'đầu tư', 'xây dựng' or 'thương mại'.
FIELD = phrase(
    r"mã số thuế|mã số doanh nghiệp|mã doanh nghiệp|số đăng ký|MST|địa chỉ|trụ sở|số tài khoản|tài khoản|điện thoại|email|fax|"
    r"đại diện(?: bởi)?|người đại diện|chức vụ|doanh thu|lợi nhuận|giá trị|"
    r"vốn điều lệ|ngày ký|số hợp đồng|bên [AB]|chủ đầu tư|bên giao thầu|bên nhận thầu|"
    r"thông tin chi tiết|nội dung hợp đồng|tổng giá trị|diện tích|quyết định|căn cứ|"
    r"người liên hệ|người ký|người lập|liên hệ|mobile|tel|số định danh|số tiền|số lượng"
)
PREDICATE = phrase(
    r"có|đã|sẽ|đang|được|phải|là|đề nghị|yêu cầu|cam kết|xác nhận|"
    r"thông báo|đồng ý|chịu trách nhiệm|chịu thuế|ký kết|ký hợp đồng|"
    r"gọi tắt|sau đây|theo|với|do|ngày|vừa|cần|kính gửi|trân trọng|tại|về|trong|bằng|trước|kể từ|đến hết"
)
ACTION = phrase(
    r"thanh toán (?:cho|số|tiền|giá trị|theo|trong|đợt|bằng|\d[\w.,/]*)|"
    r"(?:cho thuê|thuê) (?:\d[\w.,/]*|diện tích|đất|mặt bằng|nhà|văn phòng|tại)|"
    r"chuyển (?:tiền|khoản)|thực hiện (?:hợp đồng|công việc|nghĩa vụ)|"
    r"cung cấp (?:cho|dịch vụ theo)|nhận được|xuất hóa đơn"
)
CONNECTOR = phrase(r"và|cùng|cho|của")
# Lower-case verb phrases end a name ("Công ty Sao Mai giao hàng cho ..."). Case-sensitive, so a
# capitalised brand such as "Giao Hàng Nhanh" can still be part of a name.
LOWER_ACTION = re.compile(r"(?:giao hàng|giao cho|bán cho|mua của|gửi cho|trả cho|ký với|ký kết|chuyển cho|"
                          r"báo cáo|đề xuất|phối hợp|hợp tác với|làm việc với|ký|cũng|đồng thời)(?!\w)".replace(" ", SPACE))
# An incomplete legal prefix or a chain of generic business activities does not
# establish a particular company's name. A user can still add it explicitly.
GENERIC_WORDS = set("tập đoàn kiến trúc và đầu tư xây dựng thương mại dịch vụ sản xuất xuất nhập khẩu tổng hợp "
                    "tmcp cổ phần".split())


@dataclass(frozen=True)
class CompanySpan:
    start: int
    end: int
    source: str


def _skip_space(text: str, pos: int) -> int:
    while pos < len(text) and text[pos].isspace() and text[pos] != "\t":
        pos += 1
    return pos


def _prefixes(text: str):
    """Company prefixes plus other organisation types, earliest first."""
    found = [(m, False) for m in COMPANY.finditer(text)] + [(m, True) for m in ORGANISATION.finditer(text)]
    return sorted(found, key=lambda item: item[0].start())


def _continues_on_next_line(text: str, name_start: int, end: int, next_pos: int) -> bool:
    """2.6: an ALL-CAPS heading («CÔNG TY TNHH AN BÌNH PHÁT») does not run into the ordinary sentence
    below it («Hợp đồng giữa …»). Mixed-case names still wrap onto lower-case words («Tập\nđoàn»)."""
    word = WORD.match(text, next_pos)
    if not word:
        return False
    letters = [c for c in text[name_start:end] if c.isalpha()]
    heading = len(letters) >= 4 and all(c.isupper() for c in letters)
    return not heading or word.group().isupper()


def company_spans(text: str) -> list[CompanySpan]:
    result = []
    covered = 0
    for prefix, needs_capital in _prefixes(text):
        if prefix.start() < covered:
            continue  # "Tập đoàn" inside "Công ty cổ phần Tập đoàn ..." belongs to that name
        pos = _skip_space(text, prefix.end())
        if pos == prefix.end():
            continue
        form = LEGAL_FORM.match(text, pos)
        if form:
            pos = _skip_space(text, form.end())
        name_start = pos
        first = WORD.match(text, pos)
        if needs_capital and (not first or not first.group()[0].isupper()):
            continue
        if PUBLIC_ORG.match(text, prefix.start()):
            continue
        end = pos
        words = 0
        while pos < len(text) and pos - prefix.start() <= 300 and words < 40:
            if words and text[pos] in "&–-":
                next_pos = _skip_space(text, pos + 1)
                if next_pos == pos + 1 or not WORD.match(text, next_pos):
                    break
                pos = next_pos
            if FIELD.match(text, pos) or COMPANY.match(text, pos):
                break
            # A proper name is needed before sentence predicates can end it.
            if words and (PREDICATE.match(text, pos) or ACTION.match(text, pos) or LOWER_ACTION.match(text, pos)):
                break
            connector = CONNECTOR.match(text, pos)
            if words and connector:
                next_pos = _skip_space(text, connector.end())
                if COMPANY.match(text, next_pos) or ORGANISATION.match(text, next_pos) or PUBLIC_BODY.match(text, next_pos):
                    break
            if words and NUMBER_CELL.match(text, pos):
                break
            word = WORD.match(text, pos)
            if not word:
                break
            end = word.end()
            words += 1
            next_pos = _skip_space(text, end)
            if next_pos == end:
                break
            # Extraction may use even double newlines between consecutive PDF
            # text lines. Neither a single nor double newline proves a name ended,
            # but a following label line, list item or article number does.
            if "\n" in text[end:next_pos] and NEXT_LINE_BREAK.match(text, text.rindex("\n", end, next_pos)):
                break
            if "\n" in text[end:next_pos] and not _continues_on_next_line(text, name_start, end, next_pos):
                break
            pos = next_pos
        if words and end > name_start:
            raw = text[prefix.start():end]
            body = text[name_start:end]
            body_words = set(re.findall(r"\w+", body.casefold()))
            # A particular organisation's name has a capitalised word or a number ("3/2").
            has_capital = any(w[0].isupper() for w in re.findall(r"[^\W\d_]+", body)) or any(c.isdigit() for c in body)
            if (len(raw) <= 300 and pos - prefix.start() <= 300 and words < 40 and has_capital
                    and not body_words.issubset(GENERIC_WORDS)):
                result.append(CompanySpan(prefix.start(), end, " ".join(raw.split())))
                covered = end
    return result
