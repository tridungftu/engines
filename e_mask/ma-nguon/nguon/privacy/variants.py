"""Suggestions only: fuzzy comparison never changes source text or masks."""
import re
import unicodedata
from difflib import SequenceMatcher

from .core import PrivacyError, key, literal_pattern, normalize, validate_rules

NAME_CATEGORIES = {"CONG_TY", "CA_NHAN"}


def folded(text):
    return " ".join("".join(c for c in unicodedata.normalize("NFD", text.casefold())
                            if unicodedata.category(c) != "Mn").replace("đ", "d").split())


def similar(left, right):
    if left["category"] != right["category"] or left["category"] not in NAME_CATEGORIES:
        return False
    if re.search(r"\d", left["source"] + right["source"]):
        return False
    if key(left["source"]) == key(right["source"]):
        return False  # Exact duplicates belong in the duplicate warning.
    a, b = folded(left["source"]), folded(right["source"])
    if min(len(a), len(b)) < 6 or len(a.split()) != len(b.split()):
        return False
    return SequenceMatcher(None, a, b, autojunk=False).ratio() >= .9


def propose(rules, documents):
    groups = []
    used = set()
    for i, rule in enumerate(rules):
        if i in used or rule["category"] not in NAME_CATEGORIES:
            continue
        members = [i]
        for j in range(i + 1, len(rules)):
            if j not in used and all(similar(rules[k], rules[j]) for k in members):
                members.append(j)
        if len(members) < 2:
            continue
        # Already confirmed aliases need no repeated suggestion.
        if len({rules[k]["token"] for k in members}) == 1 and all(rules[k].get("canonical") for k in members):
            used.update(members)
            continue
        used.update(members)
        entries = []
        for index in members:
            contexts = []
            for doc in documents:
                for match in re.finditer(literal_pattern(rules[index]["source"]), doc.original, re.I):
                    contexts.append({"document": doc.name,
                                     "text": doc.original[max(0, match.start()-65):match.end()+85]})
                    if len(contexts) == 3:
                        break
                if len(contexts) == 3:
                    break
            entries.append({"index": index, "contexts": contexts})
        groups.append({"members": entries})
    return groups


def group_rules(rules, indices, canonical, token, saved):
    selected = set(indices)
    if len(selected) < 2 or any(i < 0 or i >= len(rules) for i in selected):
        raise PrivacyError("Chọn ít nhất hai biến thể trong danh sách hiện tại.")
    members = [rules[i] for i in sorted(selected)]
    categories = {r["category"] for r in members}
    if len(categories) != 1 or not categories <= NAME_CATEGORIES:
        raise PrivacyError("Chỉ gom các tên cùng nhóm Doanh nghiệp hoặc Cá nhân.")
    canonical = " ".join(normalize(canonical).split())
    if re.search(r"\d", canonical) or any(re.search(r"\d", r["source"]) for r in members):
        raise PrivacyError("Không dùng gom biến thể văn bản cho tên chứa chữ số hoặc mã định danh.")
    if token not in {r["token"] for r in members}:
        raise PrivacyError("Chọn bí danh của một trong các biến thể đã chọn.")
    selected_names = {key(r["source"]) for r in members}
    if any(r["token"] != token and (key(r["source"]) == key(canonical) or
           key(r.get("canonical", "")) == key(canonical)) for r in saved):
        raise PrivacyError("Tên chuẩn đã thuộc một định danh khác trong danh mục. Hãy kiểm tra lại.")
    saved_selected = [r for r in saved if key(r["source"]) in selected_names]
    if any(r["token"] != token for r in saved_selected):
        raise PrivacyError("Có tên đã lưu với bí danh khác. Không tự gộp hai định danh đã dùng; chọn lại nhóm/bí danh.")
    # A token owned by an unrelated saved name cannot be appropriated by editing a row.
    if any(r["token"] == token for r in saved) and not any(r["token"] == token for r in saved_selected):
        raise PrivacyError("Bí danh này thuộc tên khác trong danh mục. Cần có tên đã lưu trong nhóm được xác nhận.")
    if any(i not in selected and r["token"] == token and not r.get("canonical") for i, r in enumerate(rules)):
        raise PrivacyError("Bí danh còn được dùng ở dòng khác. Hãy chọn đủ các dòng cùng đối tượng trước khi gom.")
    updated = [dict(r) for r in rules]
    for i, rule in enumerate(updated):
        if i in selected:
            rule.update(token=token, canonical=canonical, enabled=True)
        elif rule["token"] == token and rule.get("canonical"):
            rule["canonical"] = canonical
    return validate_rules(updated), {(key(r["source"]), token) for r in members}
