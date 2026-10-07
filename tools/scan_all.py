import sys
sys.path.insert(0, 'tools')
import pack_index

needle = sys.argv[1].lower()
packs = sys.argv[2:]
out = []
for p in packs:
    try:
        entries = pack_index.read_index(p)
    except Exception as e:
        out.append('ERR %s %s' % (p, e))
        continue
    for name, size, comp in entries:
        if needle in name.lower():
            out.append('%s :: %s' % (p.split('\\')[-1], name))
with open('tools/scan_all_%s.txt' % needle.replace('/','_').replace('.','_'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
    f.write('\ntotal %d\n' % len(out))
print('done', len(out))
