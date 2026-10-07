import ctypes
import os
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
    # RPFM stores a 4-byte uncompressed size prefix before the zstd frame.
    size = int.from_bytes(raw[:4], 'little')
    frame = raw[4:]
    src = ctypes.create_string_buffer(frame, len(frame))
    dst = ctypes.create_string_buffer(size)
    res = lib.ZSTD_decompress(dst, size, src, len(frame))
    if lib.ZSTD_isError(res):
        raise RuntimeError('zstd error on frame')
    return dst.raw[:res]


def main():
    pack_path = sys.argv[1]
    out_dir = sys.argv[2]
    h, entries = pack_read.parse(pack_path)
    data = h['data']
    os.makedirs(out_dir, exist_ok=True)
    n_ok = 0
    for e in entries:
        rel = e['path'].replace('\\', '/')
        dst_path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        raw = data[e['offset']:e['offset'] + e['size']]
        try:
            content = zstd(raw) if e['compressed'] else raw
        except Exception as ex:
            print('FAIL', rel, ex)
            continue
        with open(dst_path, 'wb') as f:
            f.write(content)
        n_ok += 1
    print('extracted', n_ok, 'files to', out_dir)


if __name__ == '__main__':
    main()
