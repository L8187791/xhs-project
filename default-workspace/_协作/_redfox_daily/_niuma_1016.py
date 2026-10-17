# -*- coding: utf-8 -*-
import json, glob, os
d = os.path.dirname(os.path.abspath(__file__))
seen = {}
for f in glob.glob(os.path.join(d, "redfox_*_1016.json")):
    j = json.load(open(f, encoding="utf-8"))
    for it in j.get("items", []):
        n = it.get("authorNickname") or ""
        if "牛马" in n:
            seen[it.get("noteId")] = it
for k, it in seen.items():
    print("=" * 70)
    print("标题:", it.get("title"))
    print("作者:", it.get("authorNickname"), "| 粉:", it.get("authorFans"), "| 发布:", it.get("createTime"))
    print("赞", it.get("likedCount"), "藏", it.get("collectedCount"), "评", it.get("commentsCount"), "转", it.get("sharedCount"))
    print("链接:", it.get("noteLink"))
    print("正文:", repr(it.get("desc")))
