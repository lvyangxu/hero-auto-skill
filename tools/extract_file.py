import ctypes
import sys
sys.path.insert(0, 'tools')
import pack_read

DLL = r'F:\Git\mingw64\bin\libzstd.dll'
lib = ctypes.CDLL(DLL)
lib.ZSTD_decompress.restype = ctypes.c_size_t
lib.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
lib.ZSTD_isError.restype = ctypes.c_uint
lib.ZSTD_isError.argtypes = [ctypes.c_size_t]


def zstd(raw):
    size = int.from_bytes(raw[:4], 'little')
    frame = raw[4:]
    src = ctypes.create_string_buffer(frame, len(frame))
    dst = ctypes.create_string_buffer(size)
    res = lib.ZSTD_decompress(dst, size, src, len(frame))
    if lib.ZSTD_isError(res):
        raise RuntimeError('zstd error')
    return dst.raw[:res]


path = sys.argv[1]
name = sys.argv[2]
outpath = sys.argv[3]
h, entries = pack_read.parse(path)
data = h['data']
for e in entries:
    if e['path'].replace('\\', '/').endswith(name):
        raw = data[e['offset']:e['offset'] + e['size']]
        content = zstd(raw) if e['compressed'] else raw
        with open(outpath, 'wb') as f:
            f.write(content)
        print('wrote', outpath, len(content), 'bytes from', e['path'])
        break
else:
    print('NOT FOUND', name)
