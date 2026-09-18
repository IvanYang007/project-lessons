import subprocess
from collections import Counter

repo = r"D:\Github\countUp"
raw = subprocess.run(
    ["git", "-C", repo, "log", "--no-merges", "--pretty=format:C%H", "--name-only"],
    capture_output=True, text=True, encoding="utf-8").stdout

pairs, commits, cur = Counter(), Counter(), []


def flush():
    if len(cur) < 2:
        return
    commits.update(cur)
    s = sorted(set(cur))
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            pairs[(s[i], s[j])] += 1


def short(p):
    for pre in ("app/src/main/java/com/countup/app/", "app/src/main/java/com/ivanyang/countup/",
                "app/src/main/res/", "app/src/test/java/com/countup/app/"):
        if p.startswith(pre):
            return p[len(pre):]
    return p


for line in raw.splitlines():
    if line.startswith("C") and len(line) >= 40:
        flush()
        cur = []
    elif line.strip():
        cur.append(line.strip())
flush()

print("=== couplings >= 8 (short names) ===")
for (a, b), n in sorted(pairs.items(), key=lambda kv: -kv[1]):
    if n >= 8:
        print(f"{n:3d}  {short(a)}  +  {short(b)}")
print("=== churn base, top 12 ===")
for p, n in commits.most_common(12):
    print(f"{n:3d}  {short(p)}")
