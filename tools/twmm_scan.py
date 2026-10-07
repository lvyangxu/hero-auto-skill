import re
import sys

path = sys.argv[1]
with open(path, 'rb') as f:
    data = f.read()

strs = re.findall(rb'[ -~]{4,}', data)
decoded = [s.decode('latin1') for s in strs]

keywords = ['pack', 'basename', 'filename', 'file_name', 'stem',
            'modname', 'mod name', 'display name', 'displayname',
            'plain name', 'title', 'friendly name', 'get_name']

hits = []
for s in decoded:
    low = s.lower()
    if any(k in low for k in keywords):
        hits.append(s)

# de-duplicate, keep order
seen = set()
uniq = []
for h in hits:
    if h not in seen:
        seen.add(h)
        uniq.append(h)

for h in uniq[:400]:
    print(h)
print('---total unique hits:', len(uniq))
