# -*- coding: utf-8 -*-
"""
定题评分（W 新职责专用 · 2026-10-14 建）
用途：候选方向 → 拉红狐真实爆款数据 → 按《选题定题SOP·红狐评分法》六维打分 → 排序输出。
纪律：只输出真实拉到的数字；样本 n<5 的方向标「样本不足」，不得据此定题。
运行：C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe redfox_topic_scoring.py
"""
import os, re, json, sys, subprocess, statistics
from collections import OrderedDict

PY = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
FETCH = (r"C:/Users/Administrator/.workbuddy/plugins/cache/experts/redfox-xhs-creator/"
         r"1.0.0/skills/xiaohongshu-write/scripts/fetch_xhs_hot_articles.py")

ENV = dict(os.environ)
try:
    txt = open(os.path.expanduser("~/.workbuddy/redfox.env"), encoding="utf-8").read()
    m = re.search(r"REDFOX_API_KEY=(\S+)", txt)
    if m:
        ENV["REDFOX_API_KEY"] = m.group(1).strip().strip('"')
except Exception:
    pass

# 候选方向：层 -> 方向名 -> 关键词
CANDIDATES = OrderedDict([
    ("A层·时效", OrderedDict([
        ("截止提醒（通用）", ["秋招截止", "网申截止"]),
        ("最后一天/明天截止", ["网申最后一天", "秋招明天截止"]),
        ("单家深挖（安永类）", ["安永 秋招", "四大 秋招"]),
        ("秋招时间线", ["秋招时间表", "网申时间表"]),
    ])),
    ("C层·机会型", OrderedDict([
        ("免笔试（对照·已定稿）", ["免笔试", "秋招 免笔试"]),
        ("秋招捡漏", ["秋招捡漏", "秋招 捡漏岗位"]),
        ("补录/二次放岗", ["秋招补录", "秋招 二次招聘"]),
        ("信息差", ["秋招信息差", "校招信息差"]),
        ("冷门央国企", ["冷门国企", "小众央国企 秋招"]),
        ("踩坑/后悔（经历型）", ["秋招踩坑", "秋招后悔"]),
        ("二战/延期毕业", ["二战秋招", "秋招 延毕"]),
    ])),
])


def num(v):
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


# ---- 清洗：求职意图白名单 + 已知陷阱黑名单（WB132 三大陷阱 + 本轮新增） ----
WANT = ["秋招", "校招", "网申", "offer", "简历", "面试", "投", "招聘", "岗位",
        "截止", "笔试", "央国企", "国企", "外企", "银行", "大厂", "双非", "应届", "往届"]
TRAP = ["四大菩萨", "四大皆空", "四大忧郁", "祝你幸福", "留学", "考研报名", "中考", "高考",
        "金榜题名", "景区", "恋综", "相亲", "盒饭", "变脸", "万粉", "福利", "DJI", "礼物"]


def clean(title):
    if any(x in title for x in TRAP):
        return False
    return any(x in title for x in WANT)


def pull(kw, max_items=30):
    p = subprocess.run(
        [PY, FETCH, "--keyword", kw, "--max-items", str(max_items), "--page-size", "50",
         "--output-format", "json"],
        capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=180)
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


def band(v, table):
    """table: [(下限, 分值), ...] 从高到低"""
    for lo, sc in table:
        if v >= lo:
            return sc
    return 0


def score(it_stats):
    """六维打分（数据四维 + 可核验/母版间隔由人工填，此处先算数据四维 85 分制）"""
    cr = it_stats["cr_med"]          # 评/赞中位
    like = it_stats["like_med"]      # 赞中位
    hi = it_stats["hi_ratio"]        # 评/赞>=0.3 占比
    n = it_stats["n"]
    s_cr = band(cr, [(0.30, 35), (0.20, 28), (0.15, 21), (0.10, 14), (0.0, 7)])
    s_like = band(like, [(5000, 20), (3000, 16), (1000, 12), (500, 8), (0, 4)])
    s_hi = band(hi, [(0.30, 15), (0.20, 11), (0.10, 7), (0.0, 3)])
    s_hot = band(it_stats["hot_top"], [(20000, 15), (10000, 11), (5000, 7), (0, 3)])
    return {
        "评论率代理35": s_cr, "爆款天花板20": s_like,
        "高互动占比15": s_hi, "头部爆款15": s_hot,
        "数据小计85": s_cr + s_like + s_hi + s_hot,
        "样本": n,
    }


def main():
    out = OrderedDict()
    for layer, dirs in CANDIDATES.items():
        out[layer] = OrderedDict()
        for name, kws in dirs.items():
            seen, rows = set(), []
            for kw in kws:
                for it in pull(kw):
                    nid = it.get("noteId")
                    if not nid or nid in seen:
                        continue
                    seen.add(nid)
                    like = num(it.get("likedCount"))
                    coll = num(it.get("collectedCount"))
                    cmt = num(it.get("commentsCount"))
                    title = (it.get("title") or "").strip()
                    if not title or like <= 0:      # 清洗：无标题 / 量级缺失不入样
                        continue
                    if not clean(title):            # 清洗：非求职意图 / 已知陷阱
                        continue
                    rows.append({"t": title, "l": like, "c": coll, "m": cmt,
                                 "cr": (cmt / like) if like > 100 else 0})
                print("  拉取 %-16s -> 累计 %d 条" % (kw, len(rows)), file=sys.stderr)
            if not rows:
                out[layer][name] = {"n": 0}
                continue
            crs = [r["cr"] for r in rows if r["l"] > 100]   # 评/赞只在赞>100 时有效
            if not crs:
                crs = [0]
            likes = sorted(r["l"] for r in rows)
            colls = sorted(r["c"] for r in rows)
            st = {
                "n": len(rows),
                "n_ratio": len(crs),
                "cr_med": round(statistics.median(crs), 3),
                "like_med": int(statistics.median(likes)),
                "coll_med": int(statistics.median(colls)),
                "cmt_med": int(statistics.median([r["m"] for r in rows])),
                "hi_ratio": round(sum(1 for x in crs if x >= 0.30) / len(crs), 3),
                "hot_top": max(r["l"] for r in rows),
                "top": sorted(rows, key=lambda r: (-r["cr"], -r["l"]))[:6],
            }
            st["score"] = score(st)
            out[layer][name] = st
            print("  %-16s n=%-3d 评/赞中位%.3f 赞中位%d 高互动占比%.0f%% 分%d"
                  % (name, st["n"], st["cr_med"], st["like_med"],
                     st["hi_ratio"] * 100, st["score"]["数据小计85"]), file=sys.stderr)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_redfox_topic_score.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("WROTE " + path)
    print(json.dumps(out, ensure_ascii=False, indent=2)[:6000])


if __name__ == "__main__":
    main()
