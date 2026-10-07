import re
import sys

path = sys.argv[1]
patterns = [p for p in sys.argv[2:]]
with open(path, 'rb') as f:
    data = f.read()
print('file', path, 'size', len(data))
for p in patterns:
    b = p.encode()
    idxs = []
    start = 0
    while len(idxs) < 30:
        i = data.find(b, start)
        if i < 0:
            break
        idxs.append(i)
        start = i + 1
    print('=== %s : %d hits ===' % (p, len(idxs)))
    for i in idxs:
        chunk = data[max(0, i - 70):i + 70].decode('latin-1')
        runs = re.findall(r'[\x20-\x7e]{3,}', chunk)
        print('  @%d %r' % (i, runs))
