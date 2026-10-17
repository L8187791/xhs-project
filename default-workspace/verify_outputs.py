import re, io, os

base = r"D:\Documents\deepseek-harness\default-workspace"

# ---- 验证题库成品 ----
p = os.path.join(base, "产品_面试题库_全本v1.md")
t = io.open(p, encoding="utf-8").read()
qs = re.findall(r"^\*\*([A-E]\d+)\b", t, flags=re.M)
from collections import Counter
groups = Counter(q[0] for q in qs)
dups = [q for q, n in Counter(qs).items() if n > 1]
print("=== 产品_面试题库_全本v1.md ===")
print("总题数:", len(qs), "| 去重后:", len(set(qs)))
print("分组:", dict(sorted(groups.items())))
print("重复编号:", dups or "无")
missing = []
for g, n in (("A", 8), ("B", 14), ("C", 10), ("D", 14), ("E", 4)):
    for i in range(1, n + 1):
        if f"{g}{i}" not in qs:
            missing.append(f"{g}{i}")
print("缺失编号:", missing or "无")
print("含'第 1 章':", "第 1 章" in t, "| 含'第 2 章':", "第 2 章" in t)
print("含待补/见另一文件:", ("待补" in t) or ("见另一文件" in t))
print("含'标准答案':", "标准答案" in t, "| 含'保证通过':", "保证通过" in t)
print("字符数:", len(t))

# ---- 验证纯文本稿 ----
p2 = os.path.join(base, "发布用_第1至3篇纯文本.md")
t2 = io.open(p2, encoding="utf-8").read()
print("\n=== 发布用_第1至3篇纯文本.md ===")
print("篇数标记:", len(re.findall(r"={5,}\s*第\s*\d+\s*篇", t2)))
for k in ("【标题】", "【正文】", "【标签】", "【置顶首评】"):
    print(f"  {k}: {t2.count(k)} 处")
print("残留 Markdown 加粗 **:", t2.count("**"))
print("残留 ### :", t2.count("###"))
print("含占位提示:", "发布前必须" in t2)
print("字符数:", len(t2))
