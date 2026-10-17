# -*- coding: utf-8 -*-
"""
红狐高评论钩子挖掘
用途：从红狐爆款库里找出「评论数最高 / 评论点赞比最高」的笔记，提炼可复用的评论区钩子结构。
注意：红狐接口只给评论【数】，不给评论【原文】。因此本脚本输出的是「标题结构 -> 高评论」的
      A 级实证相关性（真实赞藏评数），钩子话术本身属 B/C 级推演，需标注。
运行：C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe redfox_hook_mining.py
"""
import os, re, json, subprocess, collections

PY = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
FETCH = (r"C:/Users/Administrator/.workbuddy/plugins/cache/experts/redfox-xhs-creator/"
         r"1.0.0/skills/xiaohongshu-write/scripts/fetch_xhs_hot_articles.py")
KEYWORDS = ["秋招", "双非", "校招", "应届生求职", "往届生"]
ENV = dict(os.environ)
if not ENV.get("REDFOX_API_KEY"):
    m = re.search(r"REDFOX_API_KEY=(\S+)", open(os.path.expanduser("~/.workbuddy/redfox.env"),
                                                encoding="utf-8").read())
    ENV["REDFOX_API_KEY"] = m.group(1) if m else ""


def num(v):
    """'5000+' -> 5000 ; '1w+' -> 10000 ; '7w+' -> 70000 ; None -> 0"""
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().replace(",", "")
    m = re.match(r"^([\d.]+)\s*w", s, re.I)
    if m:
        return int(float(m.group(1)) * 10000)
    m = re.match(r"^([\d.]+)", s)
    return int(float(m.group(1))) if m else 0


def pull(kw):
    p = subprocess.run(
        [PY, FETCH, "--keyword", kw, "--max-items", "50", "--page-size", "50",
         "--output-format", "json"],
        capture_output=True, text=True, encoding="utf-8", env=ENV)
    out = p.stdout or ""
    i = out.find("{")
    if i < 0:
        return []
    try:
        obj, _ = json.JSONDecoder().raw_decode(out[i:])
    except Exception:
        return []
    items = obj.get("items") or []
    for it in items:
        it["_kw"] = kw
    return items


def main():
    seen, rows = set(), []
    for kw in KEYWORDS:
        for it in pull(kw):
            nid = it.get("noteId")
            if not nid or nid in seen:
                continue
            seen.add(nid)
            rows.append({
                "kw": it.get("_kw"),
                "title": (it.get("title") or "").replace("|", " ").strip(),
                "fans": num(it.get("authorFans")),
                "liked": num(it.get("likedCount")),
                "collect": num(it.get("collectedCount")),
                "cmt": num(it.get("commentsCount")),
                "share": num(it.get("sharedCount")),
                "link": it.get("noteLink", ""),
            })
    rows = [r for r in rows if r["liked"] > 0]

    def ratio(r):                       # 评论/点赞：>1 说明"愿意说"多于"愿意赞"
        return r["cmt"] / r["liked"] if r["liked"] else 0

    top_cmt = sorted(rows, key=lambda r: -r["cmt"])[:20]
    top_ratio = sorted([r for r in rows if r["cmt"] >= 10], key=lambda r: -ratio(r))[:15]

    L = []
    L.append("# 红狐高评论钩子挖掘（%s）\n" % KEYWORDS)
    L.append("> 数据源：红狐爆款库，关键词 %s，去重后 %d 篇。"
             "**接口只提供评论数、不提供评论原文**，故下表为「标题结构 → 高评论」的实证相关性。\n"
             % ("、".join(KEYWORDS), len(rows)))

    L.append("\n## 一 · 评论数 TOP20（绝对量）\n")
    L.append("| # | 标题 | 粉丝 | 点赞 | 收藏 | 评论 | 评论/点赞 | 关键词 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(top_cmt, 1):
        L.append("| %d | %s | %d | %d | %d | **%d** | %.2f | %s |"
                 % (i, r["title"][:44], r["fans"], r["liked"], r["collect"],
                    r["cmt"], ratio(r), r["kw"]))

    L.append("\n## 二 · 评论/点赞比 TOP15（评论≥10 · 钩子效率榜）\n")
    L.append("> 比值 >1 = 评论多于点赞，说明该篇**触发了表达欲**而非只是认同，是最值得抄的钩子结构。\n")
    L.append("| # | 标题 | 粉丝 | 点赞 | 评论 | 评论/点赞 | 关键词 |")
    L.append("|---|---|---|---|---|---|---|")
    for i, r in enumerate(top_ratio, 1):
        L.append("| %d | %s | %d | %d | **%d** | **%.2f** | %s |"
                 % (i, r["title"][:44], r["fans"], r["liked"], r["cmt"], ratio(r), r["kw"]))

    # 结构标签统计
    pat = collections.OrderedDict([
        ("疑问句/吗/？",      r"[吗呢?？]"),
        ("召唤评论（说说/聊聊/来）", r"说说|聊聊|来说|来评论|评论区"),
        ("两难选择（还是/或）",  r"还是|或者|A还是B"),
        ("情绪词（恶心/崩/哭/累/烦/焦虑）", r"恶心|崩|哭|累|烦|焦虑|破防|emo|死"),
        ("反直觉（别/其实/没想到/居然）", r"别再|其实|没想到|居然|反而是|不是.*而是"),
        ("人群点名（XX生/XXer/双非）", r"双非|二本|文科生|理科生|保研|留子|往届|应届|研究生|本科生"),
        ("求助式（怎么办/怎么跟）", r"怎么办|怎么跟|怎么跟|如何|求"),
    ])
    L.append("\n## 三 · 高评论篇（评论/点赞 > 0.3）的标题结构命中率\n")
    hi = [r for r in rows if ratio(r) > 0.3]
    L.append("| 结构标签 | 高评论篇命中 | 占比 |")
    L.append("|---|---|---|")
    for name, p in pat.items():
        c = sum(1 for r in hi if re.search(p, r["title"]))
        L.append("| %s | %d / %d | %.0f%% |" % (name, c, len(hi), 100 * c / max(len(hi), 1)))

    L.append("\n## 四 · 反例：同为提问但评论极低（评论 < 20 且点赞 > 300）\n")
    L.append("| 标题 | 粉丝 | 点赞 | 评论 | 评论/点赞 |")
    L.append("|---|---|---|---|---|")
    for r in sorted([r for r in rows if r["cmt"] < 20 and r["liked"] > 300],
                    key=lambda r: -r["liked"])[:10]:
        L.append("| %s | %d | %d | %d | %.3f |"
                 % (r["title"][:44], r["fans"], r["liked"], r["cmt"], ratio(r)))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "红狐高评论钩子结构-挖掘报告.md")
    open(out, "w", encoding="utf-8").write("\n".join(L))
    print("WROTE", out)
    print("total rows:", len(rows))
    print("\n-- TOP10 评论数 --")
    for r in top_cmt[:10]:
        print("  %5d 评 / %6d 赞 / 粉%6d | %s" % (r["cmt"], r["liked"], r["fans"], r["title"][:40]))
    print("\n-- TOP10 评论/点赞比 --")
    for r in top_ratio[:10]:
        print("  %.2f | %5d 评 / %6d 赞 | %s" % (ratio(r), r["cmt"], r["liked"], r["title"][:40]))


if __name__ == "__main__":
    main()
