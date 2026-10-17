# -*- coding: utf-8 -*-
import json, glob, os
from collections import defaultdict
D = os.path.dirname(os.path.abspath(__file__))
acct = defaultdict(dict)
for f in glob.glob(os.path.join(D, "redfox*_1017.json")):
    try:
        j = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    for it in j.get("items", []):
        acct[it.get("authorNickname") or "?"][it.get("noteId")] = it

def n(v):
    s = str(v).replace("+","").replace(",","").strip()
    if s.lower().endswith("w"):
        try: return int(float(s[:-1])*10000)
        except: return 0
    try: return int(float(s))
    except: return 0

out = []
for name in sorted(acct, key=lambda k: -len(acct[k])):
    its = list(acct[name].values())
    mx = max(n(i.get("likedCount")) for i in its)
    out.append("\n### %s | 篇%d | 赞max%d | 粉%s" % (name, len(its), mx, max(n(i.get("authorFans")) for i in its)))
    for it in sorted(its, key=lambda i: -n(i.get("likedCount"))):
        out.append("  [%s] 赞%s 藏%s 评%s 转%s | %s" % (
            it.get("createTime"), it.get("likedCount"), it.get("collectedCount"),
            it.get("commentsCount"), it.get("sharedCount"), (it.get("title") or "").strip()[:44]))
txt = "\n".join(out)
open(os.path.join(D, "_agg_1017_v2.txt"), "w", encoding="utf-8").write(txt)
print("accounts=", len(acct), "chars=", len(txt))
