#!/usr/bin/env python3
"""Generate lookup data for Kanji Linear Algebra web app.

Parses ids.txt to build a pair index mapping (charA, charB) -> list of characters
composed of A and B. Handles radical variant mapping and recursive decomposition
so that e.g. 水×火 -> 淡 (where 淡 = ⿰氵炎, 氵≈水, 炎≈火+火).
"""

import json
import re
from collections import defaultdict

# IDS operator characters
IDS_BINARY = set('⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻')
IDS_TERNARY = set('⿲⿳')

# Placeholder characters used for unnamed components in IDS
PLACEHOLDERS = set('①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑲△αℓ')

# Radical/variant -> base character mapping
RADICAL_TO_BASE = {
    '氵': '水', '⺡': '水',
    '釒': '金', '钅': '金',
    '亻': '人',
    '灬': '火', '⺣': '火',
    '忄': '心',
    '扌': '手',
    '犭': '犬',
    '饣': '食', '飠': '食',
    '礻': '示',
    '衤': '衣',
    '讠': '言',
    '刂': '刀',
    '纟': '糸', '糹': '糸',
    '艹': '艸',
    '⺮': '竹',
    '⻊': '足',
    '耂': '老',
    '罒': '网',
    '⺼': '肉',
    '⺌': '小', '⺍': '小',
    '⺊': '卜',
    '⺩': '玉',
    '冫': '冰',
    '丷': '八',
    '⺆': '冂',
    '⺄': '乙',
}


def parse_ids(s):
    """Parse an IDS string into a tree.
    Returns a string (leaf) or tuple (operator, child1, child2, ...) or None on error.
    """
    pos = [0]

    def _parse():
        if pos[0] >= len(s):
            return None
        ch = s[pos[0]]
        pos[0] += 1
        if ch in IDS_BINARY:
            left = _parse()
            right = _parse()
            if left is None or right is None:
                return None
            return (ch, left, right)
        elif ch in IDS_TERNARY:
            a, b, c = _parse(), _parse(), _parse()
            if any(x is None for x in [a, b, c]):
                return None
            return (ch, a, b, c)
        else:
            return ch

    return _parse()


def get_all_leaves(tree):
    """Get all leaf characters from a parsed IDS tree."""
    if tree is None:
        return []
    if isinstance(tree, str):
        return [tree]
    result = []
    for child in tree[1:]:
        result.extend(get_all_leaves(child))
    return result


def effective_base(char, decompositions, memo, depth=0):
    """Compute the effective base character for a component.
    If the character (possibly after radical mapping) decomposes entirely into
    copies of a single base character, return that base. Otherwise return itself
    (after radical mapping).
    """
    if char in memo:
        return memo[char]
    if depth > 8:
        result = RADICAL_TO_BASE.get(char, char)
        memo[char] = result
        return result

    # Apply radical mapping
    mapped = RADICAL_TO_BASE.get(char, char)

    # If mapped char has a decomposition, check if all leaves reduce to one base
    target = mapped
    if target in decompositions:
        ids_str = decompositions[target]
        tree = parse_ids(ids_str)
        if tree and not isinstance(tree, str):
            leaves = get_all_leaves(tree)
            if leaves and not any(l in PLACEHOLDERS for l in leaves):
                bases = set()
                for leaf in leaves:
                    bases.add(RADICAL_TO_BASE.get(leaf, leaf))
                if len(bases) == 1:
                    single = bases.pop()
                    # Recurse to find the deepest base
                    memo[char] = None  # Sentinel to detect cycles
                    result = effective_base(
                        single, decompositions, memo, depth + 1)
                    memo[char] = result
                    return result

    memo[char] = mapped
    return mapped


def subtree_base(tree, decompositions, memo):
    """Compute effective base for an IDS subtree (inline decomposition).
    Returns the base character if all leaves reduce to one, else None.
    """
    if tree is None:
        return None
    if isinstance(tree, str):
        return effective_base(tree, decompositions, memo)

    leaves = get_all_leaves(tree)
    if not leaves or any(l in PLACEHOLDERS for l in leaves):
        return None

    bases = set()
    for leaf in leaves:
        base = effective_base(leaf, decompositions, memo)
        if base is None:
            return None
        bases.add(base)

    return bases.pop() if len(bases) == 1 else None


def main():
    # Step 1: Parse ids.txt
    decompositions = {}
    char_list = []

    with open('ids.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 3:
                continue

            char = parts[1]
            # Take the first decomposition, strip regional annotations like [GTKV]
            ids_raw = parts[2]
            ids_clean = re.sub(r'\[.*?\]$', '', ids_raw).strip()

            if ids_clean and ids_clean != char:
                decompositions[char] = ids_clean
                char_list.append(char)

    print(f"Parsed {len(decompositions)} decompositions from ids.txt")

    # Step 2: Build pair index
    memo = {}
    pair_index = defaultdict(lambda: defaultdict(list))

    for char in char_list:
        ids_str = decompositions[char]
        tree = parse_ids(ids_str)

        if tree is None or isinstance(tree, str):
            continue

        op = tree[0]
        if op in IDS_BINARY:
            comp1, comp2 = tree[1], tree[2]
            base1 = subtree_base(comp1, decompositions, memo)
            base2 = subtree_base(comp2, decompositions, memo)

            if base1 and base2:
                if char not in pair_index[base1][base2]:
                    pair_index[base1][base2].append(char)

        elif op in IDS_TERNARY:
            # For ternary, record all pairwise combinations
            comps = [tree[1], tree[2], tree[3]]
            bases = [subtree_base(c, decompositions, memo) for c in comps]
            for i in range(3):
                for j in range(3):
                    if i != j and bases[i] and bases[j]:
                        if char not in pair_index[bases[i]][bases[j]]:
                            pair_index[bases[i]][bases[j]].append(char)

    # Step 3: Load definitions
    with open('zh-defs.json', 'r', encoding='utf-8') as f:
        zh_defs_full = json.load(f)
    with open('jp-defs.json', 'r', encoding='utf-8') as f:
        jp_defs_full = json.load(f)

    # Collect single-character definitions
    def extract_single_char_defs(defs_dict, max_meanings=3):
        result = {}
        for key, entries in defs_dict.items():
            if len(key) != 1:
                continue
            meanings = []
            for entry in entries[:max_meanings]:
                m = entry.get('en', '')
                if m:
                    meanings.append(m)
            if meanings:
                result[key] = '; '.join(meanings)
        return result

    zh_defs = extract_single_char_defs(zh_defs_full)
    jp_defs = extract_single_char_defs(jp_defs_full)

    # Step 4: Sort pair results - prefer characters with definitions, then by code point
    has_def = set(zh_defs.keys()) | set(jp_defs.keys())

    def sort_key(ch):
        return (0 if ch in has_def else 1, ord(ch))

    pair_dict = {}
    total_entries = 0
    for b1, inner in pair_index.items():
        pair_dict[b1] = {}
        for b2, chars in inner.items():
            sorted_chars = sorted(chars, key=sort_key)
            pair_dict[b1][b2] = sorted_chars
            total_entries += len(sorted_chars)

    print(f"Pair index: {sum(len(v) for v in pair_dict.values())} unique pairs, "
          f"{total_entries} total characters")
    print(f"Definitions: {len(zh_defs)} Chinese, {len(jp_defs)} Japanese")

    # Step 5: Write data.js
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write('// Auto-generated data for Kanji Linear Algebra\n')
        f.write('// Do not edit manually - regenerate with preprocess.py\n\n')
        f.write('const PAIR_INDEX = ')
        json.dump(pair_dict, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n\n')
        f.write('const ZH_DEFS = ')
        json.dump(zh_defs, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n\n')
        f.write('const JP_DEFS = ')
        json.dump(jp_defs, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')

    import os
    size_kb = os.path.getsize('data.js') / 1024
    print(f"Generated data.js: {size_kb:.1f} KB")


if __name__ == '__main__':
    main()
