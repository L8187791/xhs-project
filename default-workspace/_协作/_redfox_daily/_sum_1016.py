# -*- coding: utf-8 -*-
import json, glob, os
d = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in glob.glob(os.path.join(d, "redfox_*_1016.json")):
    try:
        j = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("FAIL", f, e); continue
    for it in j.get("items", []):
        rows.append((it.get("authorNickname"), it.get("title"), it.get("createTime"),
                     it.get("likedCount"), it.get("collectedCount"), it.get("commentsCount"),
                     it.get("sharedCount"), it.get("authorFans"), it.get("noteLink"), os.path.basename(f)))
rows.sort(key=lambda r: -((int(str(r[3]).replace('+','') or 0) if str(r[3]).isdigit() or str(r[3]).replace('+','').isdigit() else 0)
                          + 2*((int(str(r[4]).replace('+','') or 0) if str(r[4]).replace('+','').isdigit() else 0))
                          + 3*((int(str(r[5]).replace('+','') or 0) if str(r[5]).replace('+','').isdigit() else 0))))
print("n=", len(rows))
for r in rows:
    print(" | ".join(str(x) for x in r[:9]))
