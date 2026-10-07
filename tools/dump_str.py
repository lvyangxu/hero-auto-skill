import re
import sys

path = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])
with open(path, 'rb') as f:
    f.seek(start)
    data = f.read(end - start)
s = data.decode('latin-1')
runs = re.findall(r'[\x20-\x7e]{3,}', s)
for r in runs:
    print(r)
