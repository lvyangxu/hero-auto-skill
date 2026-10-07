import sys
sys.path.insert(0, 'tools')
import pack_read

path = sys.argv[1]
target = sys.argv[2]
h, entries = pack_read.parse(path)
data = h['data']
for e in entries:
    if e['path'].endswith(target):
        raw = data[e['offset']:e['offset'] + e['size']]
        with open('tools/raw.bin', 'wb') as f:
            f.write(raw)
        with open('tools/stripped.zst', 'wb') as f:
            f.write(raw[4:])
        print('wrote tools/raw.bin (%d) and tools/stripped.zst (%d)' % (len(raw), len(raw) - 4))
        print('prefix u32 le =', int.from_bytes(raw[:4], 'little'))
        break
