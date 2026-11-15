"""Conservative suggestions for explicitly labelled Vietnamese personal names."""
import re


LABEL = re.compile(r"(?<!\w)(?:ông|bà|họ\s+(?:và\s+)?tên|đại\s+diện)(?!\w)[^\S\t]*[:：]?[^\S\t]*", re.I)
WORD = re.compile(r"[^\W\d_]+(?:[-’'][^\W\d_]+)*", re.UNICODE)
NOT_PERSON = re.compile(r"(?:thành\s+phố|tỉnh|quận|huyện|phường|xã|công\s+ty|tập\s+đoàn|sở|bộ|ban|ủy\s+ban|uỷ\s+ban|UBND|hội\s+đồng)(?!\w)", re.I)
ROLE = re.compile(r"(?:chức\s+vụ|tổng\s+giám\s+đốc|giám\s+đốc|chủ\s+tịch|trưởng\s+phòng|đại\s+diện)(?!\w)", re.I)


def person_names(text: str) -> list[str]:
    result = []
    for label in LABEL.finditer(text):
        pos = label.end()
        # In 'Đại diện: Ông ...', the inner explicit honorific owns the name.
        if LABEL.match(text, pos) or NOT_PERSON.match(text, pos):
            continue
        words = []
        while len(words) < 7:
            if ROLE.match(text, pos):
                break
            word = WORD.match(text, pos)
            if not word or not word.group()[0].isupper():
                break
            words.append(word.group())
            end = word.end()
            gap = re.match(r"[^\S\t]+", text[end:])
            if not gap:
                break
            pos = end + gap.end()
        if 2 <= len(words) < 7:
            result.append(" ".join(words))
    return result
