"""Dump selected Cco contexts / members from the extracted UI documentation.

usage: python tools/_cco.py <ctx-substring> [<member-substring>]
"""
import html
import re
import sys

doc = open('tools/_uidoc.html', encoding='utf-8', errors='replace').read()
heads = [(m.start(), m.group(1)) for m in re.finditer(r'<h3>([^<]+)</h3>', doc)]


def ctx_at(pos):
    name = '?'
    for p, n in heads:
        if p > pos:
            break
        name = n
    return name


ctx_filter = sys.argv[1].lower()
member_filter = sys.argv[2].lower() if len(sys.argv) > 2 else None

count = 0
for m in re.finditer(r'<tr>(.*?)</tr>', doc, re.S):
    ctx = ctx_at(m.start())
    if ctx_filter not in ctx.lower():
        continue
    cells = re.findall(r'<td>(.*?)</td>', m.group(1), re.S)
    cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in cells]
    if not cells or (len(cells) >= 4 and cells[0] == 'Name'):
        continue
    line = ' | '.join(cells)
    if member_filter and member_filter not in line.lower():
        continue
    print(line)
    count += 1

print('---')
print('rows:', count)
