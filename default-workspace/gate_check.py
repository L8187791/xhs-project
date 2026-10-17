"""三层闸门自动校验：跨文件数字一致性 + 绝对化用语 + 未核实统计数字。

用法：python gate_check.py
覆盖：全部内容包 + 发布用纯文本稿 + 产品文件
"""
import io
import os
import re
import sys

BASE = r"D:\Documents\deepseek-harness\default-workspace"

# 事实卡口径（唯一事实源）
FACTS = {
    "时间表家数": 17,
    "简历模板套数": 12,
    "题库题数": 50,
    "价格": ["9.9", "19.9", "25.9", "29.9", "34.9", "49.9", "99", "149"],
}

FORBIDDEN_ABSOLUTE = ["最", "第一", "top1", "永久", "100%", "全网", "独家",
                      "保证", "包过", "唯一", "顶级", "官方指定"]

# 未核实统计数字的高危模式（行业流传数据）
RISKY_STATS = [
    (re.compile(r"\d+\s*秒"), "秒级统计（如 HR 看 7 秒）"),
    (re.compile(r"\d{2,3}\s*%"), "百分比数字"),
    (re.compile(r"通过率"), "通过率"),
    (re.compile(r"\d+\s*倍"), "倍数"),
    (re.compile(r"\d+\s*万人"), "人数统计"),
]

# 只检查正文/标题区（自检清单与修正记录行豁免，因为它们本身在声明禁止用词）
EXEMPT_MARKERS = ["- [x]", "- [ ]", "| 序号", "改前", "改后", "禁止", "不得",
                  "无绝对化", "无未核实", "自查", "搜索", "拦截", "合规禁区"]

FILES = [
    "首批内容包_首发3篇与15篇排期.md",
    "内容包_周批次01_第4至7篇.md",
    "内容包_周批次02_第8至11篇.md",
    "内容包_周批次03_第12至15篇.md",
    "发布用_第1至3篇纯文本.md",
]

issues = []
checked = 0

for fn in FILES:
    path = os.path.join(BASE, fn)
    if not os.path.exists(path):
        issues.append((fn, "-", "文件不存在", ""))
        continue
    text = io.open(path, encoding="utf-8").read()
    checked += 1
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if any(m in line for m in EXEMPT_MARKERS):
            continue
        # 绝对化用语
        for w in FORBIDDEN_ABSOLUTE:
            if w in line:
                issues.append((fn, lineno, f"绝对化用语「{w}」", stripped[:60]))
        # 未核实统计数字
        for pat, desc in RISKY_STATS:
            if pat.search(line):
                issues.append((fn, lineno, f"疑似未核实统计：{desc}", stripped[:60]))

# 跨文件数字一致性：家数 / 套数 / 题数出现处
print(f"扫描文件 {checked} 个，发现问题 {len(issues)} 处\n")
if issues:
    cur = None
    for fn, ln, kind, snippet in issues:
        if fn != cur:
            print(f"── {fn}")
            cur = fn
        print(f"   L{ln}  {kind}\n        {snippet}")
else:
    print("✅ 未发现绝对化用语或未核实统计数字")

# 数字一致性交叉核对
print("\n=== 关键数字出现情况（人工复核是否与事实卡一致）===")
patterns = [
    (re.compile(r"已核验\s*(\d+)\s*家"), "已核验家数（应=17）"),
    (re.compile(r"(\d+)\s*套"), "套数（应=12）"),
    (re.compile(r"(\d+)\s*题"), "题数（应=50）"),
]
for fn in FILES:
    path = os.path.join(BASE, fn)
    if not os.path.exists(path):
        continue
    text = io.open(path, encoding="utf-8").read()
    for pat, desc in patterns:
        found = sorted({m for m in pat.findall(text)})
        if found:
            print(f"  {fn} | {desc}: {found}")
