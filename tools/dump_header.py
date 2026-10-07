import sys

def dump(path):
    with open(path, 'rb') as f:
        data = f.read()
    print('file:', path)
    print('size:', len(data))
    n = min(256, len(data))
    for i in range(0, n, 16):
        chunk = data[i:i+16]
        hexs = ' '.join('%02x' % b for b in chunk)
        asci = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print('%08x  %-47s  %s' % (i, hexs, asci))

if __name__ == '__main__':
    dump(sys.argv[1])
