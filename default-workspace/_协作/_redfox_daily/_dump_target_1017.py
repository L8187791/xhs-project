# -*- coding: utf-8 -*-
import json, glob, os
D = os.path.dirname(os.path.abspath(__file__))
TARGET = "刚刚（秋招版）"
seen = {}
for f in glob.glob(os.path.join(D, "redfox*_1017.json")):
    try:
        j = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    for it in j.get("items", []):
        if (it.get("authorNickname") or "") == TARGET:
            seen[it.get("noteId")] = it
lines = ["### %s · 命中 %d 篇" % (TARGET, len(seen))]
for it in sorted(seen.values(), key=lambda i: i.get("createTime")):
    lines.append("\n---- note ----")
    lines.append("标题: %s" % it.get("title"))
    lines.append("发布: %s | 粉: %s | 赞%s 藏%s 评%s 转%s | 互动%s" % (
        it.get("createTime"), it.get("authorFans"), it.get("likedCount"),
        it.get("collectedCount"), it.get("commentsCount"), it.get("sharedCount"),
        it.get("interactiveCount")))
    lines.append("链接: %s" % it.get("noteLink"))
    lines.append("正文: %s" % (it.get("desc") or ""))
txt = "\n".join(lines)
open(os.path.join(D, "_target_1017.txt"), "w", encoding="utf-8").write(txt)
print("WROTE", len(txt))
