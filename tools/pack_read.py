import struct
import sys
import os

# PFHFlags
HAS_EXTENDED_HEADER = 0b0000_0001_0000_0000
HAS_ENCRYPTED_INDEX = 0b0000_0000_1000_0000
HAS_INDEX_WITH_TIMESTAMPS = 0b0000_0000_0100_0000
HAS_ENCRYPTED_DATA = 0b0000_0000_0001_0000


def read_u32(data, pos):
    return struct.unpack_from('<I', data, pos)[0], pos + 4


def read_cstr(data, pos):
    end = data.index(b'\x00', pos)
    return data[pos:end].decode('utf-8', 'replace'), end + 1


def parse(path):
    with open(path, 'rb') as f:
        data = f.read()
    magic = data[0:4].decode('ascii', 'replace')
    bitmask, pos = read_u32(data, 4)
    packs_count, pos = read_u32(data, pos)
    packs_index_size, pos = read_u32(data, pos)
    files_count, pos = read_u32(data, pos)
    files_index_size, pos = read_u32(data, pos)
    timestamp, pos = read_u32(data, pos)
    assert magic == 'PFH5', 'unexpected magic %r' % magic
    header = dict(magic=magic, bitmask=bitmask, packs_count=packs_count,
                  packs_index_size=packs_index_size, files_count=files_count,
                  files_index_size=files_index_size, timestamp=timestamp, header_end=pos)

    if bitmask & HAS_EXTENDED_HEADER:
        pos += 20

    pack_deps = []
    for _ in range(packs_count):
        name, pos = read_cstr(data, pos)
        pack_deps.append(name)
    header['dependencies'] = pack_deps

    entries = []
    for _ in range(files_count):
        size, pos = read_u32(data, pos)
        if bitmask & HAS_INDEX_WITH_TIMESTAMPS:
            _, pos = read_u32(data, pos)
        is_compressed = data[pos]
        pos += 1
        name, pos = read_cstr(data, pos)
        entries.append(dict(path=name, size=size, compressed=bool(is_compressed)))

    data_start = pos
    off = data_start
    for e in entries:
        e['offset'] = off
        off += e['size']
    header['data_start'] = data_start
    header['data_end'] = off
    header['file_size'] = len(data)
    header['data'] = data
    return header, entries


if __name__ == '__main__':
    h, entries = parse(sys.argv[1])
    print('header:', {k: v for k, v in h.items() if k != 'data'})
    print('files:', len(entries))
    for e in entries[:20]:
        print('  %10d  comp=%s  %s' % (e['size'], e['compressed'], e['path']))
