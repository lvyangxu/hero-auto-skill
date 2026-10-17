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


args = sys.argv[1:]
ctx_filter = None
if args and args[0] == '--ctx':
    ctx_filter = args[1].lower()
    args = args[2:]
needle = (args[0] if args else '').lower()

count = 0
for m in re.finditer(r'<tr>(.*?)</tr>', doc, re.S):
    ctx = ctx_at(m.start())
    if ctx_filter is not None and ctx_filter not in ctx.lower():
        continue
    cells = re.findall(r'<td>(.*?)</td>', m.group(1), re.S)
    cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in cells]
    if not cells or (len(cells) >= 4 and cells[0] == 'Name'):
        continue
    line = ' | '.join(cells)
    if needle and needle not in line.lower():
        continue
    print('%-40s %s' % (ctx, line))
    count += 1
print('rows:', count)
