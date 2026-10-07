import os

roots = [
    r'd:\Lingma',
    r'F:\nvm4w',
    r'F:\Git',
    r'C:\Program Files (x86)\Steam',
    r'C:\Users\anshi\AppData\Local',
]
max_depth = 12
out = []
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
            if 'zstd' in low:
                out.append(os.path.join(dirpath, fn))
with open('tools/zstd2.txt', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(o + '\n')
    f.write('total %d\n' % len(out))
print('done', len(out))
