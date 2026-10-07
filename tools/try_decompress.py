import sys
import lzma
import zlib
sys.path.insert(0, 'tools')
import pack_read

path = sys.argv[1]
target = sys.argv[2]
h, entries = pack_read.parse(path)
data = h['data']
for e in entries:
    if e['path'].endswith(target):
        raw = data[e['offset']:e['offset'] + e['size']]
        print('file:', e['path'], 'size:', e['size'], 'compressed:', e['compressed'])
        print('first bytes:', raw[:16].hex())
        attempts = []

        def try_(name, fn):
            try:
                out = fn()
                attempts.append((name, 'OK len=%d' % len(out), out[:80]))
            except Exception as ex:
                attempts.append((name, 'FAIL %s' % ex, b''))

        try_('lzma_alone', lambda: lzma.decompress(raw, format=lzma.FORMAT_ALONE))
        try_('lzma_xz', lambda: lzma.decompress(raw, format=lzma.FORMAT_XZ))
        try_('zlib', lambda: zlib.decompress(raw))
        try_('raw_deflate', lambda: zlib.decompress(raw, -15))
        try_('raw_lzma1', lambda: lzma.decompress(raw, format=lzma.FORMAT_RAW, filters=[{'id': lzma.FILTER_LZMA1}]))

        for name, status, preview in attempts:
            print('  %-12s %-20s %r' % (name, status, preview))
        break
