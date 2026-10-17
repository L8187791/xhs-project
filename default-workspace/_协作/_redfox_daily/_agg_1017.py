# -*- coding: utf-8 -*-
"""汇总 10-17 红狐抓取 · 按账号聚合 · 排除已拆对象"""
import json, glob, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
EXCLUDE = ["牛马"]  # 7 天内已拆（10-16 笔记层）

acct = defaultdict(list)
for f in glob.glob(os.path.join(D, "redfox_*_1017.json")):
    try:
        j = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("FAIL", f, e); continue
    for it in j.get("items", []):
        acct[it.get("authorNickname") or "?"].append(it)

def n(v):
    s = str(v).replace("+", "").replace(",", "").strip()
    if s.endswith("w") or s.endswith("W"):
        try: return int(float(s[:-1]) * 10000)
        except: return 0
    try: return int(float(s))
    except: return 0

rows = []
for name, its in acct.items():
    if any(x in name for x in EXCLUDE):
        continue
    likes = [n(i.get("likedCount")) for i in its]
    colls = [n(i.get("collectedCount")) for i in its]
    cmts  = [n(i.get("commentsCount")) for i in its]
    fans  = max(n(i.get("authorFans")) for i in its)
    rows.append((name, len(its), max(likes), max(colls), max(cmts), fans))

rows.sort(key=lambda r: -(r[2] + 2 * r[3] + 3 * r[4]))
print("n_accounts=", len(rows))
for r in rows:
    print("| %s | 篇%d | 赞max%d | 藏max%d | 评max%d | 粉%s" % r)

print("\n=== 明细（赞>=300 的篇）===")
for name, its in acct.items():
    if any(x in name for x in EXCLUDE):
        continue
    for it in its:
        if n(it.get("likedCount")) >= 300:
            print("%-14s | %s | 赞%s 藏%s 评%s | %s | %s" % (
                name, it.get("createTime"), it.get("likedCount"),
                it.get("collectedCount"), it.get("commentsCount"),
                (it.get("title") or "")[:34], it.get("noteLink")))
