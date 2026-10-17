import io, os, re

BASE = r"D:\Documents\deepseek-harness\default-workspace"
FILES = ["内容包_周批次01_第4至7篇.md", "内容包_周批次02_第8至11篇.md",
         "内容包_周批次03_第12至15篇.md", "首批内容包_首发3篇与15篇排期.md"]

rows = []
for fn in FILES:
    t = io.open(os.path.join(BASE, fn), encoding="utf-8").read()
    chunks = re.split(r"\n(?=#{1,2}\s*第\s*\d+\s*篇)", t)
    for c in chunks:
        if not re.match(r"#{1,2}\s*第\s*\d+\s*篇", c.strip()):
            continue
        no = re.search(r"第\s*(\d+)\s*篇", c).group(1)
        typ = re.search(r"第\s*\d+\s*篇\s*·\s*([^\n（(]+)", c)
        title = ""
        m = re.search(r"①\s*标题\**\s*\n+\**([^\n*]+)", c)
        if m:
            title = m.group(1).strip()
        prod = ""
        m2 = re.search(r"⑥\s*挂载商品\**\s*\n+([^\n]+)", c)
        if m2:
            prod = m2.group(1).strip()[:40]
        rows.append((int(no), typ.group(1).strip() if typ else "", title, prod))

rows.sort()
print(f"{'#':<4}{'类型':<8}{'标题':<34}挂载商品")
print("-" * 100)
for no, typ, title, prod in rows:
    print(f"{no:<4}{typ:<8}{title:<34}{prod}")
print(f"\n合计 {len(rows)} 篇")
