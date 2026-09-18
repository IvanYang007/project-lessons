import subprocess, sys
from collections import Counter, defaultdict

repo = r"D:\Github\papervault"
raw = subprocess.run(
    ["git", "-C", repo, "log", "--no-merges", "--pretty=format:C%H", "--name-only", "--", "src"],
    capture_output=True, text=True, encoding="utf-8").stdout

pairs = Counter()
commits = Counter()
cur = []
def flush():
    if len(cur) < 2:
        return
    commits.update(cur)
    s = sorted(set(cur))
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            pairs[(s[i], s[j])] += 1

for line in raw.splitlines():
    if line.startswith("C") and len(line) >= 40:
        flush(); cur = []
    elif line.strip():
        cur.append(line.strip())
flush()

print("=== couplings (count >= 5) ===")
rows = [(n, a, b) for (a, b), n in pairs.items() if n >= 5]
for n, a, b in sorted(rows, reverse=True)[:20]:
    print(f"{n:3d}  {a}  +  {b}")
print("=== support base ===")
for p, n in commits.most_common(8):
    print(f"{n:3d}  {p}")
