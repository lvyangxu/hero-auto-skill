"""Search a (possibly single-line) html/text file for a regex and print a
context window around every match, with tags stripped.

usage: python tools/_sgrep.py <file> <regex> [window]
"""
import re
import sys

path = sys.argv[1]
pattern = sys.argv[2]
window = int(sys.argv[3]) if len(sys.argv) > 3 else 700

data = open(path, encoding='utf-8', errors='replace').read()
matches = list(re.finditer(pattern, data))

print('matches:', len(matches))
print()

for m in matches[:20]:
    chunk = data[max(0, m.start() - window):m.start() + window]
    chunk = re.sub(r'<script.*?</script>', ' ', chunk, flags=re.S)
    chunk = re.sub(r'<[^>]+>', ' ', chunk)
    chunk = re.sub(r'\s+', ' ', chunk)
    print('--- @%d ---' % m.start())
    print(chunk.strip())
    print()
