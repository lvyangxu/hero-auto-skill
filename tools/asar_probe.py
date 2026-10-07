import re
import sys

path = sys.argv[1]
kws = [k.lower() for k in sys.argv[2].split(',')]

with open(path, 'rb') as f:
    data = f.read().decode('latin1')

for kw in kws:
    print('======== ' + kw + ' ========')
    seen = set()
    count = 0
    for m in re.finditer(re.escape(kw), data, re.IGNORECASE):
        s = max(0, m.start() - 120)
        e = min(len(data), m.end() + 120)
        ctx = data[s:e].replace('\r', ' ').replace('\n', ' ')
        ctx = ''.join(ch if 32 <= ord(ch) < 127 else '.' for ch in ctx)
        if ctx in seen:
            continue
        seen.add(ctx)
        print(ctx)
        count += 1
        if count >= 20:
            break
    print('---- shown:', count)
