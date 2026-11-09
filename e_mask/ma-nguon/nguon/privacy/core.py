from __future__ import annotations

import bisect
import io
import json
import re
import secrets
import unicodedata
import zipfile
from collections import defaultdict
from functools import lru_cache

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from docx import Document
from docx.shared import Pt

from .company_names import company_spans
from .person_names import person_names
from .detectors import DATE, MONEY, MONEY_NEAR, detect, traces


from .types import Extracted as Extracted, PrivacyError as PrivacyError
from .types import normalize as normalize


CATEGORIES = {
    "CONG_TY": "Doanh nghiệp", "CA_NHAN": "Cá nhân", "EMAIL": "Email",
    "DIEN_THOAI": "Điện thoại", "MA_SO_THUE": "Mã số thuế", "TAI_KHOAN": "Tài khoản",
    "GIAY_TO": "Giấy tờ", "HOP_DONG": "Mã hợp đồng", "DIA_CHI": "Địa chỉ",
    "DU_AN": "Dự án", "KHAC": "Khác",
}
TOKEN = re.compile(r"\[[A-Z][A-Z0-9_]{2,49}\]")


def key(text: str) -> str:
    return " ".join(normalize(text).split()).casefold()


def literal_pattern(source: str) -> str:
    words = re.split(r"\s+", source.strip())
    body = r"\s+".join(re.escape(w) for w in words)
    left = r"(?<!\w)" if source[0].isalnum() or source[0] == "_" else ""
    right = r"(?!\w)" if source[-1].isalnum() or source[-1] == "_" else ""
    return left + body + right


def validate_rules(rules: list[dict], max_rules: int = 500) -> list[dict]:
    if len(rules) > max_rules:
        raise PrivacyError(f"Danh sách vượt giới hạn {max_rules} mục.")
    occurrences = {}
    result = []
    for index, rule in enumerate(rules, 1):
        source = normalize(str(rule.get("source", ""))).strip()
        category = rule.get("category", "KHAC")
        token = str(rule.get("token", "")).strip()
        if not 2 <= len(source) <= 300 or category not in CATEGORIES or not TOKEN.fullmatch(token):
            raise PrivacyError("Cụm gốc cần 2–300 ký tự; bí danh có dạng [CONG_TY_001].")
        if TOKEN.search(source):
            raise PrivacyError("Không dùng bí danh làm cụm gốc cần thay.")
        occurrences.setdefault(key(source), []).append(index)
        result.append({"source": source, "token": token, "category": category,
                       "enabled": bool(rule.get("enabled", True))})
        if rule.get("canonical") is not None:
            canonical = " ".join(normalize(str(rule["canonical"])).split())
            if category not in {"CONG_TY", "CA_NHAN"} or not 2 <= len(canonical) <= 300 or TOKEN.search(canonical):
                raise PrivacyError("Tên chuẩn cần 2–300 ký tự, thuộc nhóm Doanh nghiệp hoặc Cá nhân.")
            result[-1]["canonical"] = canonical
    duplicates = [rows for rows in occurrences.values() if len(rows) > 1]
    if duplicates:
        details = "\n".join(
            f"• { ' '.join(result[rows[0] - 1]['source'].split()) } — dòng {', '.join(map(str, rows))}"
            for rows in duplicates
        )
        raise PrivacyError("Cụm gốc bị trùng. Mỗi cụm chỉ cần một dòng:\n" + details)
    return result


def suggest(texts: list[str], existing: list[dict] | None = None, reserved_tokens: set[str] | None = None,
            blocked: set[str] | None = None, origins: dict | None = None) -> list[dict]:
    """Suggestions, accepted one by one: longest phrase first, and every occurrence of an accepted
    phrase is consumed before the next one is considered (2.6). A phrase that only occurs inside or
    across an accepted one ("Công ty TNHH A" within "Công ty TNHH A B C", a name cut by a line break)
    is therefore not suggested again. `blocked` = keys Anh marked as wrong detections."""
    rules = list(existing or [])
    seen = {key(r["source"]) for r in rules}
    blocked = blocked or set()
    used = {r["token"] for r in rules} | {t for text in texts for t in TOKEN.findall(text)} | (reserved_tokens or set())
    # These are deterministic suggestions, NOT a general Vietnamese NER model.
    patterns = [
        ("EMAIL", r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
        ("DIEN_THOAI", r"(?<![\w\d])(?:\+84[ .-]?[1-9]|0[35789])(?:[ .-]?\d){8}(?!\d)"),
        ("MA_SO_THUE", r"(?:mã\s*số\s*thuế|MST)\s*[:：]?\s*(?P<value>\d{10}(?:[- ]?\d{3})?)(?!\d)"),
        ("TAI_KHOAN", r"(?:số\s*tài\s*khoản|STK|tài\s*khoản\s*số)\s*[:：]?\s*(?P<value>\d[\d .-]{4,30}\d)"),
        ("GIAY_TO", r"(?:CCCD|CMND|hộ\s*chiếu|căn\s*cước(?:\s*công\s*dân)?)\s*(?:số)?\s*[:：]?\s*(?P<value>(?-i:[A-Z]\d{7,8}|\d{9}|\d{12}))(?!\w)"),
        ("HOP_DONG", r"(?:số\s*hợp\s*đồng|hợp\s*đồng\s*số|mã\s*hợp\s*đồng)\s*[:：]?\s*(?P<value>[\w][\w./-]{2,60})"),
        ("DIA_CHI", r"(?:địa\s*chỉ|trụ\s*sở)\s*[:：]\s*(?P<value>[^\n\t;]{4,180})"),
        ("DU_AN", r"(?:tên\s*dự\s*án|dự\s*án)\s*[:：]\s*(?P<value>[^\n\t;]{3,140})"),
    ]

    def find(source):
        wanted = key(source)
        return next((r for r in rules if key(r["source"]) == wanted), None)

    # 1) Collect candidates from every layer on the ORIGINAL texts, so a longer, different name that
    #    contains a catalogue entry («Công ty TNHH Sao Mai Xanh» vs «Công ty TNHH Sao Mai») is still found.
    working = list(texts)
    candidates = []
    for text in working:
        for category, pattern in patterns:
            for match in re.finditer(r"(?<!\w)" + pattern, text, re.IGNORECASE):
                source = match.groupdict().get("value", match.group()).strip(" .,-\r\n")
                # Labels delimit typical contract fields on the same line.
                source = re.split(r"\s+(?:MST|mã số thuế|chức vụ|địa chỉ)\s*[:：]", source, flags=re.I)[0].strip()
                candidates.append((category, source, None, f"Nhãn trường ({CATEGORIES[category]})"))
        candidates += [("CA_NHAN", name, None, "Tên người sau nhãn/danh xưng") for name in person_names(text)]
        candidates += [("CONG_TY", span.source, None, "Tên doanh nghiệp (Công ty/Ngân hàng/…)")
                       for span in company_spans(text)]
        # 2.3.0 high-recall layers: identifiers, organisations, addresses, people, projects.
        candidates += [(f.category, f.source, f.parent,
                        f"Tên rút gọn/viết tắt của «{f.parent}»" if f.parent else f"Lớp nhận diện 2.3 ({CATEGORIES[f.category]})")
                       for f in detect(text)]

    # 2) Accept identifiers first (they must never lose a slot to long phrases), then longest first;
    #    earlier layers win ties. Within one group (names: companies + people; otherwise one category)
    #    a candidate needs an occurrence that does not touch an accepted one, else it is a fragment or a
    #    cut of a phrase already in the list. Other groups never consume each other: a person or a phone
    #    number inside a long address stays its own row.
    order = sorted(range(len(candidates)), key=lambda i: (candidates[i][0] not in IDENTIFIERS,
                                                          -len(" ".join(candidates[i][1].split())), i))
    joined = "\x00".join(working)  # NUL: a phrase never spans two cells/texts
    lowered = joined.lower()
    # Case-folded copy with the same positions lets the regex use a fast literal scan (no re.I).
    exact = len(lowered) == len(joined)

    def spans_of(source):
        return occurrences(source.lower(), lowered) if exact else [
            m.span() for m in re.finditer(literal_pattern(source), joined, re.I)]
    taken = defaultdict(Occupied)
    reviewed = defaultdict(Containers)  # occurrences of rules already in the list (catalogue, earlier edits)
    for rule in existing or []:
        if rule.get("enabled", True):
            reviewed[group(rule["category"])].extend(spans_of(rule["source"]))
    def adds_a_name(span, inner):
        """A phrase around a reviewed one must add a capitalised word or a number («… Sao Mai Xanh»),
        not just a verb («… Sao Mai cũng ký»)."""
        if not inner:
            return True
        start, end = span
        rest, cursor = [], start
        for a, b in sorted(inner):
            rest.append(joined[cursor:max(cursor, a)])
            cursor = max(cursor, b)
        rest.append(joined[cursor:end])
        return any(c.isupper() or c.isdigit() for c in "".join(rest))
    first = {}  # key -> first free occurrence, to list suggestions in reading order
    rejected = set()  # fragments stay fragments: spans taken only ever grow
    reviewed_keys = {key(r["source"]) for r in existing or []}

    def add(category, source, parent=None, layer=""):
        # Single-line inputs in the browser strip literal line breaks. Fold them
        # explicitly to spaces; literal_pattern still matches the original wraps.
        source = " ".join(source.split())
        name = key(source)
        if (name in seen or name in blocked or name in rejected or len(source) < 2 or TOKEN.search(source)
                or len(rules) >= 500):
            return
        spans = spans_of(source)
        kind = group(category)
        free = [span for span in spans if not taken[kind].touches(*span) and not reviewed[kind].contains(*span)
                and adds_a_name(span, reviewed[kind].within(*span))]
        if spans and not free:
            rejected.add(name)
            return  # only inside / across phrases accepted earlier
        taken[kind].update(free)
        if origins is not None:
            origins[name] = layer
        first[name] = min(span[0] for span in free) if free else len(joined)
        owner = find(parent) if parent else None
        if owner is not None and key(owner["source"]) in reviewed_keys:
            owner = None  # joining a short form to a saved name stays Anh's explicit decision (2.2 rule)
        if owner is not None and owner["category"] in {"CONG_TY", "CA_NHAN"}:
            # A short form of a name in this list shares its alias; the full name is the canonical name.
            canonical = owner.get("canonical") or owner["source"]
            if not owner.get("canonical"):
                rules[rules.index(owner)] = owner = {**owner, "canonical": canonical}
            rules.append({"source": source, "token": owner["token"], "category": owner["category"],
                          "enabled": True, "canonical": canonical})
        else:
            rules.append({"source": source, "token": None, "category": category, "enabled": True})
        seen.add(name)

    for index in order:
        add(*candidates[index])
    known = len(existing or [])
    fresh = sorted(rules[known:], key=lambda r: first.get(key(r["source"]), 0))
    # Aliases are numbered in reading order; short forms take their full name's alias.
    names = {}
    def alias(rule):
        return rule.get("canonical") and key(rule["canonical"]) != key(rule["source"])
    for rule in fresh:
        if rule["token"] is None and not alias(rule):
            index = 1
            while f"[{rule['category']}_{index:03d}]" in used:
                index += 1
            rule["token"] = f"[{rule['category']}_{index:03d}]"
            used.add(rule["token"])
            names[key(rule["source"])] = rule["token"]
    for rule in fresh:
        if alias(rule) and key(rule["canonical"]) in names:
            rule["token"] = names[key(rule["canonical"])]
    return rules[:known] + fresh


def occurrences(source: str, text: str) -> list[tuple[int, int]]:
    """Same matches as literal_pattern(source) on already lower-cased text, but scanned without the
    leading look-behind so the regex engine can jump between literal prefixes (≈10× faster)."""
    words = re.split(r"\s+", source.strip())
    body = re.compile(r"\s+".join(re.escape(w) for w in words))
    check_left = source[0].isalnum() or source[0] == "_"
    check_right = source[-1].isalnum() or source[-1] == "_"
    found = []
    for match in body.finditer(text):
        start, end = match.span()
        if check_left and start and (text[start - 1].isalnum() or text[start - 1] == "_"):
            continue
        if check_right and end < len(text) and (text[end].isalnum() or text[end] == "_"):
            continue
        found.append((start, end))
    return found


IDENTIFIERS = {"EMAIL", "DIEN_THOAI", "MA_SO_THUE", "TAI_KHOAN", "GIAY_TO", "HOP_DONG"}


def group(category: str) -> str:
    """Companies and people compete for the same words; every other category only with itself."""
    return "NAME" if category in {"CONG_TY", "CA_NHAN"} else category


class Containers:
    """Possibly overlapping spans; answers «is (start, end) inside one of them?»."""

    def __init__(self):
        self.spans, self.ready = [], True

    def extend(self, spans) -> None:
        self.spans.extend(spans)
        self.ready = False

    def contains(self, start: int, end: int) -> bool:
        if not self.spans:
            return False
        if not self.ready:
            self.spans.sort()
            self.starts = [s for s, _ in self.spans]
            self.reach, best = [], -1
            for _, e in self.spans:
                best = max(best, e)
                self.reach.append(best)
            self.ready = True
        i = bisect.bisect_right(self.starts, start) - 1
        return i >= 0 and self.reach[i] >= end

    def within(self, start: int, end: int) -> list[tuple[int, int]]:
        if not self.spans:
            return []
        self.contains(start, end)  # sorts on first use
        i = bisect.bisect_left(self.starts, start)
        found = []
        while i < len(self.spans) and self.spans[i][0] < end:
            if self.spans[i][1] <= end and self.spans[i] != (start, end):
                found.append(self.spans[i])
            i += 1
        return found


class Occupied:
    """Disjoint character spans already consumed by accepted phrases."""

    def __init__(self):
        self.starts, self.ends = [], []

    def touches(self, start: int, end: int) -> bool:
        i = bisect.bisect_right(self.starts, start) - 1
        if i >= 0 and self.ends[i] > start:
            return True
        return i + 1 < len(self.starts) and self.starts[i + 1] < end

    def update(self, spans) -> None:
        for start, end in spans:
            i = bisect.bisect_left(self.starts, start)
            self.starts.insert(i, start)
            self.ends.insert(i, end)


def derived_aliases(rules: list[dict], existing: list[dict] | None = None) -> set[tuple[str, str]]:
    """(name, alias) pairs suggest() linked to a full name in the same list (for catalogue merge)."""
    old = {key(r["source"]) for r in existing or []}
    sources = {key(r["source"]): r["token"] for r in rules}
    # Only when the full name is new too. Joining a short form to a name already in the catalogue
    # keeps the 2.2 rule: the user confirms explicitly ("tên khác của cùng một đối tượng").
    return {(key(r["source"]), r["token"]) for r in rules
            if key(r["source"]) not in old and r.get("canonical") and key(r["canonical"]) != key(r["source"])
            and key(r["canonical"]) not in old and sources.get(key(r["canonical"])) == r["token"]}


def replace(text: str, rules: list[dict]) -> tuple[str, int]:
    active = sorted((r for r in rules if r["enabled"]), key=lambda r: len(r["source"]), reverse=True)
    if not active:
        return text, 0
    expression = "|".join(f"(?P<R{i}>{literal_pattern(r['source'])})" for i, r in enumerate(active))
    # One pass prevents replacements from modifying tokens created earlier in the same pass.
    return re.subn(expression, lambda m: active[int(m.lastgroup[1:])]["token"], text, flags=re.I)


class LeftoverError(PrivacyError):
    """`verify(..., known=…)`: bản đã che còn dấu vết định danh. `items` = [{"cum", "so_lan", "nhom_goi_y"}]."""

    def __init__(self, items: list[dict]):
        super().__init__(f"Bản đã che còn {len(items)} dấu vết định danh. Hãy che thêm rồi kiểm lại.")
        self.items = items


def verify(text: str, rules: list[dict], known=None, dismissed=frozenset()) -> None:
    """Bản xuất không còn cụm nào trong danh sách. Chế độ tự động (`known` khác None, MASK-2) kiểm thêm dấu vết:
    định danh bên gọi đã biết (kể cả viết khác cách) và mẫu định danh của AnDanh — xem `dau_vet()`. Màn hình
    che file thủ công gọi không có `known` nên giữ nguyên như trước (Anh tự duyệt «Còn lại cần rà soát»)."""
    without_tokens = TOKEN.sub("", text)
    for rule in rules:
        if rule["enabled"] and re.search(literal_pattern(rule["source"]), without_tokens, re.I):
            raise PrivacyError("Bản xuất còn cụm đã chọn cần thay. Hãy cập nhật và duyệt lại.")
    if known is not None:
        found = dau_vet(text, known, dismissed)
        if found:
            raise LeftoverError(found)


# ---- Định danh đã biết (MASK-2): che và kiểm cả khi văn bản viết khác cách ------------------------------
# Mỗi định danh là (giá trị, nhóm, so_long): so_long = bên gọi khai nhóm (khác KHAC). Khi so_long và «bộ khung» ≥ 6
# ký tự, giá trị khớp cả cách viết khác: bộ khung = bỏ dấu tiếng Việt (Đ → D), chữ thường, chỉ giữ chữ/số; giữa hai
# ký tự liền nhau được chen tối đa 3 ký tự phân cách (khoảng trắng — kể cả xuống dòng, trừ Tab là ranh giới ô —
# và . , - /). Ví dụ «001.234.567.890» ~ «001,234,567,890» ~ «001  234 567\n890» ~ «001234567890»;
# «HĐ-2026/015» ~ «HD 2026/015». Dấu chỉ được MẤT (gõ không dấu), không được ĐỔI: «An Phát» không khớp
# «án phát» (trừ khi chính giá trị khai viết không dấu). Ranh giới: không dính chữ/số phía trước/sau, không nằm giữa
# một số chia nhóm bằng . hoặc , («1.001.234.567.890» không bị che một phần). Cách viết khác có dạng số tiền/ngày
# mà khác cách chia nhóm chữ số («1250000» ~ «1.250.000 đồng», «12052026» ~ «12/05/2026») không bị che — bước kiểm
# còn sót chặn lượt (422). Kiểm còn sót: mã toàn chữ số ≥ 8 số thì bỏ ranh giới (dính liền chữ/số khác vẫn là còn
# sót, như `dau_vet` của AnDanh so chuỗi con); tên/mã có chữ giữ ranh giới từ.
KNOWN_MIN = 6
KNOWN_SUBSTRING = 8
KNOWN_GAP = 3
GAP_CHARS = frozenset(".,-/–—‐‑")
NUMERIC_ID = re.compile(r"[\d\s.,\-/]+")
DIGIT_RUN = re.compile(r"\d(?:(?:(?!\t)[\s.,\-/]){1,3}\d)*")


@lru_cache(maxsize=8192)
def fold_char(char: str) -> str:
    """Một ký tự của bộ khung: chữ/số không dấu, chữ thường; "" với ký tự khác."""
    if char in "đĐ":
        return "d"
    if not char.isalnum():
        return ""
    base = unicodedata.normalize("NFD", char)[0].lower()
    return base if len(base) == 1 and base.isalnum() else char.lower()[:1]


def skeleton(text: str) -> str:
    return "".join(fold_char(c) for c in text)


def _plain(char: str) -> bool:
    """Ký tự không mang dấu (đã bị bỏ dấu nếu là chữ tiếng Việt)."""
    return char not in "đĐ" and unicodedata.normalize("NFD", char) == char


def _gap(char: str) -> bool:
    return char in GAP_CHARS or (char.isspace() and char != "\t")


def _word(char: str) -> bool:
    return char.isalnum() or char == "_"


class KnownText:
    """Văn bản đã gấp về bộ khung (kèm vị trí gốc), dựng một lần cho mọi định danh của lượt."""

    def __init__(self, text: str):
        self.text = text
        chars, positions = [], []
        for index, char in enumerate(text):
            if char.isascii():
                folded = char.lower() if char.isalnum() else ""
            else:
                folded = fold_char(char)
            if folded:
                chars.append(folded)
                positions.append(index)
        self.folded, self.positions = "".join(chars), positions

    def _edges(self, start: int, end: int) -> bool:
        """Không dính chữ/số trước-sau, và không nằm giữa một số chia nhóm bằng . hoặc , («1.001.234…»)."""
        text = self.text
        before = text[max(0, start - 2):start]
        after = text[end:end + 2]
        if before[-1:] and (_word(before[-1]) or (before[-1] in ".," and before[:1].isdigit()
                                                  and text[start].isdigit())):
            return False
        return not (after[:1] and (_word(after[0]) or (after[0] in ".," and after[1:].isdigit()
                                                       and text[end - 1].isdigit())))

    def _money_or_date(self, start: int, end: int, value: str) -> bool:
        """Cách viết khác có dạng số tiền / ngày («1.250.000 đồng», «12/05/2026») mà khác cách chia nhóm chữ số của
        giá trị khai («1250000», «12052026»): không che (không đụng số tiền, ngày) — bước kiểm sẽ chặn lượt.
        Cùng cách chia nhóm («001.234.567.890» ~ «001,234,567,890») vẫn là cùng mã; số bắt đầu bằng 0 không là tiền."""
        surface = self.text[start:end]
        money = surface[:1] != "0" and (MONEY.fullmatch(surface) or (
            re.fullmatch(r"[\d\s.,]+", surface) and MONEY_NEAR.match(self.text[end:end + 8])))
        if not (DATE.fullmatch(surface) or money):
            return False
        return [len(g) for g in re.findall(r"\d+", surface)] != [len(g) for g in re.findall(r"\d+", value)]

    def spans(self, value: str, loose: bool = True, boundary: bool = True,
              masking: bool = False) -> list[tuple[int, int]]:
        """Chỗ xuất hiện của `value`: đúng chữ (như `replace()`), và nếu `loose` thì cả cách viết khác (bộ khung).
        `masking`: bỏ cách viết khác có dạng số tiền/ngày (xem `_money_or_date`); bước kiểm còn sót không bỏ."""
        found = {m.span() for m in re.finditer(literal_pattern(value), self.text, re.I)}
        letters = [c for c in value if fold_char(c)]
        wanted = "".join(fold_char(c) for c in letters)
        if loose and len(wanted) >= KNOWN_MIN:
            plain_value = all(_plain(c) for c in letters)
            index = self.folded.find(wanted)
            while index >= 0:
                where = self.positions[index:index + len(wanted)]
                start, end = where[0], where[-1] + 1
                ok = all(b - a - 1 <= KNOWN_GAP and all(_gap(c) for c in self.text[a + 1:b])
                         for a, b in zip(where, where[1:]))
                ok = ok and all(t.lower() == v.lower() or plain_value or _plain(t)
                                for t, v in zip((self.text[i] for i in where), letters))
                ok = ok and (not boundary or self._edges(start, end))
                if ok and not (masking and (start, end) not in found and self._money_or_date(start, end, value)):
                    found.add((start, end))
                index = self.folded.find(wanted, index + 1)
        merged = []
        for start, end in sorted(found):
            if merged and start < merged[-1][1]:
                merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
            else:
                merged.append((start, end))
        return merged


def next_token(category: str, used: set[str]) -> str:
    index = 1
    while f"[{category}_{index:03d}]" in used:
        index += 1
    return f"[{category}_{index:03d}]"


def alias_like(value: str) -> bool:
    """Giá trị có dạng bí danh («[ABC] …», «[CONG_TY_001]»): không nhận làm định danh cần che."""
    return TOKEN.search(value) is not None


def known_rules(text: str, known, existing: list[dict], used: set[str]) -> list[dict]:
    """Định danh đã biết → dòng bí danh: một dòng cho mỗi cách viết có trong `text`, cùng một bí danh (bí danh của
    danh mục nếu giá trị đã có ở đó). `known` = [(giá trị, nhóm, so_long)]; giá trị không có trong văn bản thì bỏ
    qua (bước kiểm sau khi che vẫn bắt nếu nó lọt). Giá trị có dạng bí danh → PrivacyError."""
    owners = {key(r["source"]): (r["token"], r["category"]) for r in existing}
    used = set(used)
    finder = KnownText(text)
    rules = []
    for value, category, loose in known:
        if alias_like(value):
            raise PrivacyError("Định danh đã biết không được có dạng bí danh ([ABC]…).")
        surfaces = {}
        for start, end in finder.spans(value, loose, masking=True):
            surface = " ".join(text[start:end].split())
            if len(surface) <= 300:  # dài hơn giới hạn một dòng: không thay được → bước kiểm báo còn sót
                surfaces.setdefault(key(surface), surface)
        if not surfaces:
            continue
        owner = next((owners[name] for name in [key(value), *surfaces] if name in owners), None)
        if owner is None:
            owner = (next_token(category, used), category)
            used.add(owner[0])
        for name, surface in surfaces.items():
            if name in owners:
                continue  # đã có dòng (danh mục, hoặc định danh trước trong lượt)
            owners[name] = owner
            rules.append({"source": surface, "token": owner[0], "category": owner[1], "enabled": True})
    return rules


def leaked_known(masked: str, known) -> list[dict]:
    """Định danh đã biết còn trong bản đã che — đúng chữ, cách viết khác (nhóm đã khai), hoặc (mã chỉ gồm số,
    ≥ 8 chữ số) cùng dãy số trong một dãy số dài hơn / viết khác dấu phân cách."""
    plain = TOKEN.sub(lambda m: "\x00" * len(m.group()), masked)  # bí danh tách chữ, không nối hai dãy số
    finder = KnownText(plain)
    runs = None
    found, listed = [], set()
    for value, category, loose in known:
        if key(value) in listed:
            continue
        # Chuỗi con (bỏ ranh giới) chỉ với mã toàn chữ số ≥ 8 số; tên/mã có chữ dùng ranh giới từ, để «Sao Mai» không
        # chặn nhầm khi nó chỉ là đầu của một tên khác đã che («Sao Maiko»).
        frame = skeleton(value)
        count = len(finder.spans(value, loose, boundary=not (frame.isdigit() and len(frame) >= KNOWN_SUBSTRING)))
        digits = re.sub(r"\D", "", value)
        if not count and len(digits) >= 8 and NUMERIC_ID.fullmatch(value):
            if runs is None:
                runs = [re.sub(r"\D", "", m.group()) for m in DIGIT_RUN.finditer(plain)]
            count = sum(1 for run in runs if digits in run)
        if count:
            listed.add(key(value))
            found.append({"cum": value, "so_lan": count, "nhom_goi_y": category})
    return found


def dau_vet(masked: str, known=(), dismissed=frozenset()) -> list[dict]:
    """Phép kiểm `dau_vet` của AnDanh (engine #6) trong lõi Mask v2: [{"cum", "so_lan", "nhom_goi_y"}] còn sót sau
    khi che — định danh đã biết (`leaked_known`) rồi các mẫu định danh (`detectors.traces`). `dismissed` = cụm Anh
    đã cho giữ / đánh dấu «Sai» (chỉ bỏ dấu vết theo mẫu, không bao giờ bỏ định danh bên gọi đã khai)."""
    plain = TOKEN.sub(lambda m: "\x00" * len(m.group()), masked)
    found = leaked_known(plain, known)
    listed = {key(item["cum"]) for item in found}
    ignored = {key(d) for d in dismissed}
    grouped = {}
    for category, value in traces(plain):
        name = key(value)
        if name in listed or name in ignored:
            continue
        item = grouped.setdefault(name, {"cum": value, "so_lan": 0, "nhom_goi_y": category})
        item["so_lan"] += 1
    return found + list(grouped.values())


def numeric_review(before: str, after: str, rules: list[dict]) -> dict:
    # Compare the unchanged numbers after approved identifiers have been removed.
    expected, _ = replace(before, rules)
    def numbers(t):
        return re.findall(r"[-+]?\d+(?:[.,:/%-]\d+)*%?", TOKEN.sub("", t))
    left, right = numbers(expected), numbers(after)
    return {"changed": left != right, "before_count": len(left), "after_count": len(right)}


def make_docx(text: str) -> bytes:
    doc = Document()
    for name in ("author", "last_modified_by", "title", "subject", "comments", "keywords", "category"):
        setattr(doc.core_properties, name, "")
    doc.styles["Normal"].font.name = "Arial"
    doc.styles["Normal"].font.size = Pt(11)
    rows: list[list[str]] = []

    def flush():
        if not rows:
            return
        width = max(len(r) for r in rows)
        if width > 40:
            raise PrivacyError("Bảng vượt 40 cột. Hãy chia nhỏ bảng trong bản nháp rồi duyệt lại.")
        table = doc.add_table(rows=0, cols=width)
        table.style = "Table Grid"
        for row in rows:
            cells = table.add_row().cells
            for cell, value in zip(cells, row):
                cell.text = value
        rows.clear()

    for line in text.splitlines():
        if "\t" in line:
            rows.append(line.split("\t"))
        else:
            flush()
            doc.add_paragraph(line)
    flush()
    stream = io.BytesIO()
    doc.save(stream)
    return stream.getvalue()


def export_document(text: str, rules: list[dict], file_format: str) -> bytes:
    """Build one reviewed document and check the actual content being returned."""
    if file_format not in {"txt", "docx"}:
        raise PrivacyError("Định dạng xuất tài liệu không được hỗ trợ.")
    verify(text, rules)
    if file_format == "txt":
        return text.encode("utf-8-sig")
    docx = make_docx(text)
    # Check text in the generated Word package, including all table cells.
    doc = Document(io.BytesIO(docx))
    roundtrip = "\n".join([p.text for p in doc.paragraphs] +
                          [c.text for t in doc.tables for row in t.rows for c in row.cells])
    verify(roundtrip, rules)
    return docx


def export_bundle(texts: list[str], rules: list[dict]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, text in enumerate(texts, 1):
            name = f"tai-lieu-{index:03d}"
            archive.writestr(name + ".txt", export_document(text, rules, "txt"))
            archive.writestr(name + ".docx", export_document(text, rules, "docx"))
    return stream.getvalue()


def encrypt_mapping(rules: list[dict], password: str) -> bytes:
    if len(password) < 12:
        raise PrivacyError("Mật khẩu bảng ánh xạ cần ít nhất 12 ký tự.")
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
    derived = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(password.encode("utf-8"))
    data = json.dumps({"version": 1, "rules": rules}, ensure_ascii=False).encode("utf-8")
    return b"LOCALMASK1" + salt + nonce + AESGCM(derived).encrypt(nonce, data, b"LOCALMASK1")


def decrypt_mapping(data: bytes, password: str, max_rules: int = 500) -> list[dict]:
    if not data.startswith(b"LOCALMASK1") or not 53 <= len(data) <= 8 * 1024 * 1024:
        raise PrivacyError("Bảng ánh xạ không đúng định dạng.")
    try:
        salt, nonce = data[10:26], data[26:38]
        derived = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(password.encode("utf-8"))
        decoded = json.loads(AESGCM(derived).decrypt(nonce, data[38:], b"LOCALMASK1"))
        return validate_rules(decoded["rules"], max_rules=max_rules)
    except Exception:
        raise PrivacyError("Không mở được bảng ánh xạ: sai mật khẩu hoặc file bị thay đổi.") from None
