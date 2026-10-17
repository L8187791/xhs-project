# -*- coding: utf-8 -*-
"""
卡号撞号与空头自检 · 求职线
用法：python 卡号撞号自检.py
职责（只看「近期」＝索引已覆盖的号段，历史卡不误判）：
  ① 卡索引「卡号列」真重复（只认第一列）
  ② 空头登记：索引登记了卡号，但 inbox/outbox 无对应文件
  ③ 漏登记：近期卡文件存在，但索引无该卡号
  ④ 号段连续性
依据：2026-10-17 双实例并发撞号实跑（B1 与我同取 WB212）。
纪律：只读不写；❌ 须回盘修正后重跑。
"""
import collections
import datetime
import os
import re
import sys

COL = r"D:\小红书项目\default-workspace\_协作"
INDEX = os.path.join(COL, "卡索引.md")
DIRS = [os.path.join(COL, "inbox"), os.path.join(COL, "outbox")]
RECENT = 205          # WB 号 ≥ RECENT 视为「近期」（约最近 10 张），纳入硬校验
RECENT_C = 44         # C 号 ≥ RECENT_C 视为「近期」

# 已知例外（已报 C/L 待裁定，不阻断自检）
KNOWN_DUP = {
    "XHS-20261016-C44": "C 侧同日两卡同号（裁定卡＋预案卡）→ 已报 C（WB213 §六·1），W 不擅改 C 卡号",
}

hard_fail = []


def say(good, tag, msg, hard=True):
    if not good and hard:
        hard_fail.append(tag)
    print("  %s %-28s %s" % ("✅" if good else "❌", tag, msg))


def card_of(name):
    """从文件名严格取卡号：WB/C + 数字 + 紧跟 - 或 .md 或行尾"""
    m = re.search(r"(?:^|[-_（(])((?:WB|C)\d+)(?=[-_.。．\s]|$)", name)
    return m.group(1) if m else None


s = open(INDEX, encoding="utf-8").read()
def num_of(k):
    return int(k[2:]) if k.startswith("WB") else int(k[1:])


def is_recent(k):
    return num_of(k) >= (RECENT if k.startswith("WB") else RECENT_C)


print("=" * 78)
print("卡号撞号与空头自检 · 硬校验：WB≥%d / C≥%d" % (RECENT, RECENT_C))
print("=" * 78)

# ---------- ① 卡号列真重复 ----------
first_col = []
for line in s.split("\n"):
    line = line.strip()
    if not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if cells and re.match(r"^XHS-\d{8}-(WB|C|DB|ZL)", cells[0]):
        first_col.append(cells[0])

cnt = collections.Counter(first_col)
dup = {k: v for k, v in cnt.items() if v > 1}
print("\n【① 卡号列重复】")
dup_new = {k: v for k, v in dup.items()
           if is_recent(re.search(r"(WB|C)(\d+)$", k).group(0)) and k not in KNOWN_DUP}
dup_old = {k: v for k, v in dup.items() if k not in dup_new or k in KNOWN_DUP}
say(not dup_new, "重复卡号(近期·硬)",
    "、".join("%s×%d" % (k, v) for k, v in dup_new.items()) if dup_new else "无")
if dup_old:
    for k, v in sorted(dup_old.items()):
        why = KNOWN_DUP.get(k)
        print("     🟡 %s×%d  %s" % (k, v, ("【已报待判】" + why) if why else "历史重复·提示不改"))
print("     索引登记 %d 行（唯一 %d）" % (len(first_col), len(cnt)))

# ---------- 实盘 ----------
disk = collections.defaultdict(list)
for d in DIRS:
    if not os.path.isdir(d):
        continue
    for f in os.listdir(d):
        if not f.lower().endswith(".md"):
            continue
        k = card_of(f)
        if k:
            p = os.path.join(d, f)
            disk[k].append((os.path.getmtime(p), f))

# 同号多文件：区分「不同类型配对（数据卡+回执卡，正常）」与「同类型撞号（真撞）」
print("\n【①b 同号多文件】")
clash, pair = {}, {}
for k, v in disk.items():
    if len(v) < 2:
        continue
    types = collections.Counter()
    for _, f in v:
        m = re.match(r"([\u4e00-\u9fff]{2,4}卡|通知卡|派工卡)", f)
        types[m.group(1) if m else "其他"] += 1
    bad = {t: n for t, n in types.items() if n > 1}
    (clash if bad else pair)[k] = ", ".join("%s×%d" % (t, n) for t, n in types.items())
say(not clash, "同号同类型撞号(硬)",
    "；".join("%s[%s]" % (k, v) for k, v in sorted(clash.items())) if clash else "无")
if pair:
    print("     🟡 同号不同类（正常配对）: %s" % "；".join(
        "%s[%s]" % (k, v) for k, v in sorted(pair.items())))

# ---------- ② 空头登记（近期） ----------
idx_keys = set()
for k in first_col:
    m = re.search(r"(WB|C)(\d+)$", k)
    if m:
        idx_keys.add(m.group(1) + m.group(2))

recent_idx = set(k for k in idx_keys if is_recent(k))
hollow = sorted(k for k in recent_idx if k not in disk)
hollow_old = sorted(k for k in idx_keys if k not in recent_idx and k not in disk)
print("\n【② 空头登记（索引有、盘上无）】")
say(not hollow, "空头登记(近期·硬)", "、".join(hollow) if hollow else "无")
if hollow_old:
    print("     🟡 历史空头（提示·多为归档或 C 侧卡）: %s" % "、".join(hollow_old))

# ---------- ③ 漏登记（近期文件） ----------
CUT = datetime.datetime(2026, 10, 15).timestamp()
miss = []
for k, v in disk.items():
    if any(t >= CUT for t, _ in v) and k not in idx_keys:
        miss.append(k)
miss = sorted(set(miss))
print("\n【③ 漏登记（盘有、索引无 · 仅 10/15 后）】")
say(not miss, "漏登记", "、".join(miss) if miss else "无")

# ---------- ④ 连续性 ----------
print("\n【④ 号段连续性】")
wbn = sorted(int(k[2:]) for k in idx_keys if k.startswith("WB"))
cn = sorted(int(k[1:]) for k in idx_keys if k.startswith("C"))
if wbn:
    gaps = [x for x in range(wbn[0], wbn[-1] + 1) if x not in set(wbn)]
    recent_gap = [x for x in gaps if x >= max(RECENT, wbn[-1] - 40)]
    print("     WB：%d–%d 共 %d 个｜近期空档 %s" % (
        wbn[0], wbn[-1], len(wbn), recent_gap if recent_gap else "无"))
    print("     ⚠️ 空档若为 C 侧卡或未用号，属正常，人工判")
if cn:
    print("     C ：%d–%d 共 %d 个" % (cn[0], cn[-1], len(cn)))

# ---------- ⑤ 并发提示 ----------
print("\n【⑤ 最近落盘 5 张（并发观察）】")
allf = []
for d in DIRS:
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.lower().endswith(".md"):
                p = os.path.join(d, f)
                allf.append((os.path.getmtime(p), os.path.basename(d), f))
allf.sort(reverse=True)
for t, d, f in allf[:5]:
    print("     %s  %-7s %s" % (datetime.datetime.fromtimestamp(t).strftime("%m-%d %H:%M:%S"), d, f[:88]))

print("\n" + "=" * 78)
if not hard_fail:
    print("✅ 卡号体系一致 —— 无撞号、无空头、无漏登（近期号段）")
else:
    print("❌ 不一致项：%s —— 须回盘修正后重跑" % "、".join(hard_fail))
print("=" * 78)
sys.exit(0 if not hard_fail else 1)