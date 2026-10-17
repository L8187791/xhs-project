"""批量核验 15 篇成稿的结构完整性：7 项齐全 + 互动钩子 + 配图规格。"""
import io, os, re

BASE = r"D:\Documents\deepseek-harness\default-workspace"
FILES = [
    ("1–3 篇", "首批内容包_首发3篇与15篇排期.md"),
    ("4–7 篇", "内容包_周批次01_第4至7篇.md"),
    ("8–11 篇", "内容包_周批次02_第8至11篇.md"),
    ("12–15 篇", "内容包_周批次03_第12至15篇.md"),
    ("16–17 篇（主力层入口）", "内容包_主力层入口_第16至17篇.md"),
]
ITEMS = ["### ① 标题", "### ② 正文", "### ③ 标签", "### ④ 置顶首评",
         "### ⑤ 配图规格", "### ⑥ 挂载商品", "### ⑦ 合规自检"]
# 兼容另一种写法：**① 标题** / ## ① 标题
ITEM_RE = {
    "标题": re.compile(r"(?:###|##|\*\*)\s*①\s*标题"),
    "正文": re.compile(r"(?:###|##|\*\*)\s*②\s*正文"),
    "标签": re.compile(r"(?:###|##|\*\*)\s*③\s*标签"),
    "置顶首评": re.compile(r"(?:###|##|\*\*)\s*④\s*置顶首评"),
    "配图规格": re.compile(r"(?:###|##|\*\*)\s*⑤\s*配图规格"),
    "挂载商品": re.compile(r"(?:###|##|\*\*)\s*⑥\s*挂载商品"),
    "合规自检": re.compile(r"(?:###|##|\*\*)\s*⑦\s*合规自检"),
}
SEC4 = re.compile(r"(?:###|##|\*\*)\s*④\s*置顶首评")
SEC3 = re.compile(r"(?:###|##|\*\*)\s*③\s*标签")
SEC5 = re.compile(r"(?:###|##|\*\*)\s*⑤\s*配图规格")

total_posts = 0
problems = []

for label, fn in FILES:
    path = os.path.join(BASE, fn)
    if not os.path.exists(path):
        problems.append(f"{fn} 不存在")
        continue
    text = io.open(path, encoding="utf-8").read()
    # 按 "## 第 N 篇" 或 "# 第 N 篇" 切分
    chunks = re.split(r"\n(?=#{1,2}\s*第\s*\d+\s*篇)", text)
    posts = [c for c in chunks if re.match(r"#{1,2}\s*第\s*\d+\s*篇", c.strip())]
    print(f"\n=== {label}（{fn}）===")
    print(f"   检出 {len(posts)} 篇")
    for p in posts:
        total_posts += 1
        head = p.splitlines()[0].strip()
        missing = [k for k, rx in ITEM_RE.items() if not rx.search(p)]
        # 互动钩子：正文区是否有问句
        m3 = SEC3.search(p)
        body = p[:m3.start()] if m3 else p
        has_q = ("？" in body) or ("?" in body)
        # 置顶首评也应有提问
        m4, m5 = SEC4.search(p), SEC5.search(p)
        first = p[m4.end():m5.start()] if (m4 and m5) else ""
        first_q = ("？" in first) or ("?" in first)
        # 配图数量
        m = re.search(r"配图规格（(\d+)\s*图", p)
        nimg = m.group(1) if m else "?"
        status = []
        if missing:
            status.append("缺 " + "/".join(missing))
        if not has_q:
            status.append("正文无提问")
        if not first_q:
            status.append("首评无提问")
        mark = "✅" if not status else "⚠️ " + "；".join(status)
        print(f"   {head[:30]:<32} 配图 {nimg} 图  {mark}")
        if status:
            problems.append(f"{head}: {'；'.join(status)}")

print(f"\n{'='*60}")
print(f"合计成稿：{total_posts} 篇")
if problems:
    print(f"⚠️ 待修问题 {len(problems)} 处：")
    for x in problems:
        print("   -", x)
else:
    print("✅ 全部成稿 7 项齐全，正文与置顶首评均含互动提问")
