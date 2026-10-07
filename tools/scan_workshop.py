import os
import sys
sys.path.insert(0, 'tools')
import pack_index

root = r'F:\SteamLibrary\steamapps\workshop\content\1142710'
needle = sys.argv[1].lower() if len(sys.argv) > 1 else 'auto'
out = []
for d in sorted(os.listdir(root)):
    dd = os.path.join(root, d)
    if not os.path.isdir(dd):
        continue
    for fn in os.listdir(dd):
        if not fn.lower().endswith('.pack'):
            continue
        p = os.path.join(dd, fn)
        try:
            entries = pack_index.read_index(p)
        except Exception as e:
            out.append('ERR %s %s' % (fn, e))
            continue
        for name, size, comp in entries:
            if needle in name.lower():
                out.append('%s :: %s' % (fn, name))
with open('tools/scan_workshop_%s.txt' % needle, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
    f.write('\ntotal %d\n' % len(out))
print('done', len(out))
