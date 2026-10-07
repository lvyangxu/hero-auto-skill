import re
import sys

path = sys.argv[1]
patterns = [p.encode() for p in sys.argv[2:]]

with open(path, 'rb') as f:
    data = f.read()

found = {}
for pat in patterns:
    start = 0
    hits = 0
    while True:
        idx = data.find(pat, start)
        if idx < 0:
            break
        hits += 1
        start = idx + 1
        if hits > 200:
            break
    found[pat.decode()] = hits

print('file', path, 'size', len(data))
for k, v in found.items():
    print('  pattern %-20s hits=%d' % (k, v))

# For interesting patterns, dump surrounding printable strings.
for pat in [p for p in patterns if b'manag' in p.lower() or b'allocat' in p.lower()]:
    b = pat
    start = 0
    n = 0
    while n < 40:
        idx = data.find(b, start)
        if idx < 0:
            break
        start = idx + 1
        n += 1
        chunk = data[max(0, idx - 60):idx + 60]
        # extract run of printable
        s = chunk.decode('latin-1')
        runs = re.findall(r'[\x20-\x7e]{4,}', s)
        print('--- hit for %r @%d: %r' % (b, idx, runs))
