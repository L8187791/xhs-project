# -*- coding: utf-8 -*-
import json, glob, os
from collections import defaultdict
D = os.path.dirname(os.path.abspath(__file__))
acct = defaultdict(list)
for f in glob.glob(os.path.join(D, "redfox_*_1017.json")):
    j = json.load(open(f, encoding="utf-8"))
    for it in j.get("items", []):
        acct[it.get("authorNickname") or "?"].append(it)

def n(v):
    s = str(v).replace("+","").replace(",","").strip()
    if s.lower().endswith("w"):
        try: return int(float(s[:-1])*10000)
        except: return 0
    try: return int(float(s))
    except: return 0

out = []
out.append("账号数=%d" % len(acct))
for name in sorted(acct, key=lambda k: -max(n(i.get("likedCount")) for i in acct[k])):
    its = acct[name]
    if "牛马" in name:
        continue
    fans = max(n(i.get("authorFans")) for i in its)
    out.append("\n### %s | 篇%d | 粉丝%s" % (name, len(its), fans))
    for it in sorted(its, key=lambda i: -n(i.get("likedCount"))):
        out.append("  [%s] 赞%s 藏%s 评%s 转%s | %s | %s" % (
            it.get("createTime"), it.get("likedCount"), it.get("collectedCount"),
            it.get("commentsCount"), it.get("sharedCount"),
            (it.get("title") or "").strip(), it.get("noteLink")))
txt = "\n".join(out)
open(os.path.join(D, "_agg_1017.txt"), "w", encoding="utf-8").write(txt)
print("WROTE", len(txt), "chars")
