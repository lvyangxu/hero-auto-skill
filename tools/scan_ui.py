import os
import sys
sys.path.insert(0, 'tools')
import pack_index

DATA = r'F:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data'
packs = ['data.pack', 'ui2.pack', 'ui3.pack', 'db.pack', 'boot.pack', 'data_bl.pack']
needles = ['character_details', '.twui', 'campaign_ui', 'skill_tree']
out = []
for pk in packs:
    p = os.path.join(DATA, pk)
    if not os.path.isfile(p):
        continue
    try:
        entries = pack_index.read_index(p)
    except Exception as e:
        out.append('ERR %s %s' % (pk, e))
        continue
    for name, size, comp in entries:
        low = name.lower()
        for nd in needles:
            if nd in low:
                out.append('%s :: %s' % (pk, name))
                break
with open('tools/scan_ui.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
    f.write('\ntotal %d\n' % len(out))
print('done', len(out))
