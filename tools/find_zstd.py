import os
import sys

roots = [
    r'C:\Program Files',
    r'C:\Program Files (x86)',
    r'C:\Users\anshi\AppData',
    r'F:\SteamLibrary',
]
max_depth = 8
hits = []
for root in roots:
    if not os.path.isdir(root):
        continue
    base_depth = root.rstrip('\\').count('\\')
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath.count('\\') - base_depth
        if depth > max_depth:
            dirnames[:] = []
            continue
        for fn in filenames:
            low = fn.lower()
            if 'zstd' in low and (low.endswith('.dll') or low.endswith('.exe')):
                hits.append(os.path.join(dirpath, fn))
for h in hits:
    print(h)
print('total', len(hits))
