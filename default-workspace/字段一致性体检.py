# -*- coding: utf-8 -*-
"""字段值一致性体检 —— 找出「同一含义多种写法」的字段
   买家靠这些字段筛选，写法乱了筛选就废
"""
import io, os, re, sys, json
from collections import Counter, defaultdict
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
D = os.path.join(WS, "技能包_时间表查询官", "data", "timetable.json")
d = json.load(io.open(D, encoding="utf-8"))
cos = d["companies"]
N = len(cos)

# 卖家筛选用得到的字段
SCREEN = ["industry", "ownership", "batch", "direction", "location", "degree"]
print("=" * 90)
print("字段值一致性体检 · %d 家 · %s" % (N, d["meta"]["version"]))
print("=" * 90)

for f in SCREEN:
    vals = [(c.get(f) or "").strip() for c in cos]
    nonempty = [v for v in vals if v]
    empty = N - len(nonempty)
    c = Counter(nonempty)
    print()
    print("【%s】非空 %d ｜ 空 %d ｜ 去重后取值 %d 种" % (f, len(nonempty), empty, len(c)))
    if empty == N:
        print("   🔴 全空")
        continue
    # 可疑：单一取值占比过高（同一含义多种写法会分散）+ 取值种类过多
    kinds = len(c)
    if kinds > 25:
        print("   🔴 取值 %d 种 → 写法高度分散（筛选会碎）" % kinds)
    elif kinds > 10:
        print("   🟡 取值 %d 种 → 偏分散" % kinds)
    else:
        print("   ✅ 取值 %d 种，可控" % kinds)
    print("   分布（前 14）:")
    for k, v in c.most_common(14):
        print("      %-34s %3d" % (k[:34], v))
    if kinds > 14:
        print("      …还有 %d 种" % (kinds - 14))

# ---------- 重点：可标准化的合并建议 ----------
print()
print("=" * 90)
print("可标准化的合并（同义写法）")
print("=" * 90)

def merge_probe(field, rules):
    """rules: [(正则, 标准值)]"""
    vals = [(c.get(field) or "").strip() for c in cos]
    cnt = Counter()
    for v in vals:
        if not v:
            continue
        hit = None
        for rx, std in rules:
            if re.search(rx, v):
                hit = std; break
        cnt[hit or ("其他：" + v[:20])] += 1
    print()
    print("【%s】若按规则归一：" % field)
    for k, v in cnt.most_common():
        print("   %-28s %3d" % (k[:28], v))

merge_probe("ownership", [
    (r"央企|中央企业", "央企"),
    (r"国企|国有企业", "国企"),
    (r"国有", "国企/央企（未细分）"),
    (r"民企|民营", "民企"),
    (r"外企|外资", "外企"),
])
merge_probe("degree", [
    (r"不限|无要求", "不限"),
    (r"博士", "博士"),
    (r"硕士|研究生", "硕士"),
    (r"本科|学士", "本科"),
    (r"大专|专科", "大专"),
])
merge_probe("batch", [
    (r"提前批", "提前批"),
    (r"正式批|秋招|秋", "正式批"),
    (r"补录", "补录"),
    (r"实习", "实习"),
])

# ---------- location 写法 ----------
print()
print("=" * 90)
print("【location】写法检查")
print("=" * 90)
loc = [(c.get("location") or "").strip() for c in cos]
multi = [v for v in loc if re.search(r"[/、,，;；]", v)]
withshi = [v for v in loc if v.endswith("市")]
print("  非空 %d ｜ 含多个地点（需拆） %d ｜ 带「市」字尾 %d" % (
    len([v for v in loc if v]), len(multi), len(withshi)))
print("  多地点样例: %s" % "、".join(multi[:6]))
print("  带「市」样例: %s" % "、".join(withshi[:6]))
