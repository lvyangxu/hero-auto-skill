import ctypes
import sys

DLL = r'F:\Git\mingw64\bin\libzstd.dll'
lib = ctypes.CDLL(DLL)
lib.ZSTD_decompress.restype = ctypes.c_size_t
lib.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
lib.ZSTD_getFrameContentSize.restype = ctypes.c_ulonglong
lib.ZSTD_getFrameContentSize.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
lib.ZSTD_isError.restype = ctypes.c_uint
lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
lib.ZSTD_getErrorName.restype = ctypes.c_char_p
lib.ZSTD_getErrorName.argtypes = [ctypes.c_size_t]

src_path, dst_path = sys.argv[1], sys.argv[2]
data = open(src_path, 'rb').read()
src = ctypes.create_string_buffer(data, len(data))
content = lib.ZSTD_getFrameContentSize(src, len(data))
print('frame content size =', content)
cap = content if content < (1 << 40) else 256 * 1024 * 1024
dst = ctypes.create_string_buffer(cap)
res = lib.ZSTD_decompress(dst, cap, src, len(data))
if lib.ZSTD_isError(res):
    print('ERROR:', lib.ZSTD_getErrorName(res).decode())
else:
    print('decompressed size =', res)
    with open(dst_path, 'wb') as f:
        f.write(dst.raw[:res])
