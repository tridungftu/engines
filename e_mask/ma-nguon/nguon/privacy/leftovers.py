"""Leftover review list (2.3.0): what still looks like a name or identifier after masking.

This is the last safety net before approval. It never changes text; the user either adds
an item to the rule list or dismisses it for the session.
"""
from __future__ import annotations

import re
from functools import lru_cache

from .core import TOKEN
from .detectors import DATA, DATE, MONEY, NAME_GAP, WORD, acronyms, fold, is_cap, money_context, places, surnames

LIMIT = 200
DIGITS = re.compile(r"(?<![\d.,/:])\d(?:[ .-]?\d){7,}(?![\d/:])")
MONEY_AFTER = re.compile(r"^\s*(?:đ\b|đồng|vnđ|vnd|usd|triệu|tỷ|%)", re.I)
EMAIL_URL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|https?://\S+|www\.\S+", re.I)
SENTENCE_START = re.compile(r"(?:^|[\n\t.!?:;•\-–—(\"“\[]|\d[.)])[^\S\n]*$")
FOREIGN = re.compile(r"[fjwzFJWZ]")


@lru_cache(maxsize=None)
def allowlist() -> tuple[frozenset, frozenset]:
    """(phrases, words) that are ordinary capitalised document vocabulary."""
    phrases, words = set(), set()
    for line in (DATA / "leftover_allowlist.txt").read_text("utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("words:"):
            words.update(w.casefold() for w in line[6:].split())
        else:
            phrases.add(fold(line))
    return frozenset(phrases), frozenset(words)


def _ordinary(phrase: str) -> bool:
    phrases, words = allowlist()
    folded = fold(phrase)
    return (folded in phrases or folded in places()
            or all(w in words for w in folded.split()) or phrase.upper() in acronyms())


def _guess(text: str) -> str:
    if "@" in text:
        return "EMAIL"
    if text[:1].isdigit():
        return "TAI_KHOAN"
    first = text.split()[0]
    return "CA_NHAN" if first in surnames()[0] or first in surnames()[1] else "CONG_TY"


def _candidates(text: str):
    for m in EMAIL_URL.finditer(text):
        yield m.start(), m.end(), m.group().rstrip(".,;)")
    for m in DIGITS.finditer(text):
        value = m.group()
        if value.isdigit():
            # Số viết liền: theo đúng quy tắc của lõi (MASK-2) — «Tổng tiền thanh toán: 1250000000» là tiền, còn
            # «Tài khoản: 1912345678901 VND» hay số bắt đầu bằng 0 thì vẫn hỏi lại dù có đơn vị tiền phía sau.
            if money_context(text, m.start(), m.end()):
                continue
        elif MONEY.fullmatch(value) or DATE.fullmatch(value) or MONEY_AFTER.match(text[m.end():m.end() + 8]):
            continue
        yield m.start(), m.end(), value
    pos = 0
    while True:
        m = WORD.search(text, pos)
        if not m:
            break
        pos = m.end()
        if not is_cap(m.group()) or (m.start() and text[m.start() - 1].isalnum()):
            continue  # lower-case word, or letters glued to digits ("1C26TAA")
        # Collect a run of capitalised words separated by at most two spaces.
        words, end, cursor = [m.group()], m.end(), m.end()
        while len(words) < 6:
            gap = NAME_GAP.match(text, cursor)
            nxt = WORD.match(text, gap.end()) if gap else None
            if not nxt or not is_cap(nxt.group()):
                break
            words.append(nxt.group())
            end = cursor = nxt.end()
        pos = end
        phrase = text[m.start():end]
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", end)
        line = text[line_start:line_end if line_end >= 0 else len(text)].strip()
        if text[end:end + 2].lstrip().startswith((":", "：")):
            continue  # field label such as "Người liên hệ:"
        if phrase.isupper() and len(words) > 1 and line.isupper():
            continue  # heading line in capitals
        at_start = bool(SENTENCE_START.search(text[max(0, m.start() - 6):m.start()]))
        if len(words) == 1:
            word = words[0]
            # A lone Vietnamese syllable is usually the first word of an ordinary phrase
            # ("Ngân hàng", "Kho vận"). Brand-like words are long, CamelCase, capitals or foreign.
            brand_like = (len(word) >= 8 or any(c.isupper() for c in word[1:]) or bool(FOREIGN.search(word)))
            if len(word) < 3 or not brand_like or (at_start and not any(c.isupper() for c in word[1:])):
                continue
        elif at_start:
            words_after_first = phrase.split()[1:]
            if _ordinary(" ".join(words_after_first)):
                continue
        yield m.start(), end, " ".join(phrase.split())


def leftovers(texts: list[str], dismissed=frozenset(), limit: int = LIMIT) -> dict:
    """Group candidates across the masked texts: text, count, up to two contexts, a category guess."""
    items: dict[str, dict] = {}
    ignored = {fold(d) for d in dismissed}
    for original in texts:
        # Same-length placeholder: a token separates words and positions still match the original.
        text = TOKEN.sub(lambda m: "\x00" * len(m.group()), original)
        for start, end, value in _candidates(text):
            folded = fold(value)
            if len(value) < 2 or folded in ignored or _ordinary(value):
                continue
            item = items.setdefault(folded, {"text": value, "count": 0, "contexts": [], "category_guess": _guess(value)})
            item["count"] += 1
            if len(item["contexts"]) < 2:
                context = original_context(original, start, end)
                if context not in item["contexts"]:
                    item["contexts"].append(context)
    ordered = list(items.values())
    # Count every occurrence, including those at a sentence start that were not candidates.
    joined = "\n".join(texts)
    for item in ordered:
        item["count"] = max(item["count"], len(re.findall(r"(?<!\w)" + re.escape(item["text"]) + r"(?!\w)", joined)))
    return {"items": ordered[:limit], "total": len(ordered)}


def original_context(text: str, start: int, end: int, width: int = 60) -> str:
    return " ".join(text[max(0, start - width):min(len(text), end + width)].split())


def add_ai_findings(result: dict, findings: list[dict], texts: list[str], dismissed=frozenset(),
                    limit: int = LIMIT) -> dict:
    """Merge Local AI findings into the leftover list.

    A finding is shown only while its phrase is still present (outside aliases) in the current
    masked texts, so items disappear once the user masks them. AI items come first.
    """
    from .core import literal_pattern

    ignored = {fold(d) for d in dismissed}
    items = {fold(i["text"]): dict(i) for i in result["items"]}
    placeholder = [(original, TOKEN.sub(lambda m: "\x00" * len(m.group()), original)) for original in texts]
    ai_items = []
    for finding in findings:
        key = fold(finding["text"])
        if key in ignored:
            continue
        pattern = re.compile(literal_pattern(finding["text"]), re.I)
        count, contexts = 0, []
        for original, text in placeholder:
            for m in pattern.finditer(text):
                count += 1
                if len(contexts) < 2:
                    context = original_context(original, m.start(), m.end())
                    if context not in contexts:
                        contexts.append(context)
        if not count:
            continue  # already masked (or edited away)
        item = items.pop(key, None) or {"text": finding["text"], "contexts": contexts,
                                         "category_guess": finding.get("category", "KHAC")}
        item.update(count=max(count, item.get("count", 0)), ai=True, reason=finding.get("reason", ""))
        ai_items.append(item)
    ordered = ai_items + list(items.values())
    return {"items": ordered[:limit], "total": len(ordered)}
