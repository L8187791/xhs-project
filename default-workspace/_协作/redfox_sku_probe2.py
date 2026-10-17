# -*- coding: utf-8 -*-
"""SKU 探针二期：①工具型 vs 内容型占比分析 ②补跑付费意愿/工具需求词"""
import os, re, json, subprocess, statistics
from collections import OrderedDict

PY = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
FETCH = (r"C:/Users/Administrator/.workbuddy/plugins/cache/experts/redfox-xhs-creator/"
         r"1.0.0/skills/xiaohongshu-write/scripts/fetch_xhs_hot_articles.py")
ENV = dict(os.environ)
txt = open(os.path.expanduser("~/.workbuddy/redfox.env"), encoding="utf-8").read()
m = re.search(r"REDFOX_API_KEY=(\S+)", txt)
if m:
    ENV["REDFOX_API_KEY"] = m.group(1).strip().strip('"')

TOOL = ["表", "汇总", "清单", "整理", "模板", "工具", "攻略", "教程", "合集", "大全", "雷达", "排程"]
STORY = ["经历", "现状", "扎心", "故事", "求职女孩", "被开", "崩溃", "焦虑", "迷茫", "吐槽"]

SUPP = OrderedDict([
    ("付费意愿验证", ["秋招 表格 分享", "校招 汇总表", "求职 资料 整理", "秋招 时间表 2027"]),
])

TRAP = ["音乐银行", "浪姐", "节目组", "综艺", "选秀", "明星", "演员", "爱豆", "偶像", "音乐",
        "歌曲", "演唱会", "追星", "电视剧", "电影", "冈易", "原神", "蛋仔", "王者", "游戏",
        "无法投递", "碎片", "中秋快乐", "诗句", "散文", "文案", "朋友圈", "被开", "摸鱼",
        "辞职", "老板", "同事", "打工人日常", "四大菩萨", "留学", "考研报名", "中考", "高考",
        "金榜题名", "景区", "恋综", "相亲", "盒饭", "变脸", "投票", "简历模板", "写简历",
        "找实习", "穿搭", "妆容", "表情包", "壁纸", "头像", "美甲", "脱单", "恋爱", "情感",
        "魔仙堡", "礐嶨", "入山"]
STRONG = ["秋招", "校招", "网申", "应届", "往届", "央国企", "国企", "补录", "春招",
          "内推", "投递", "offer", "笔试", "面经", "求职"]


def num(v):
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().replace(",", "")
    mm = re.match(r"^([\d.]+)\s*w", s, re.I)
    if mm:
        return int(float(mm.group(1)) * 10000)
    mm = re.match(r"^([\d.]+)", s)
    return int(float(mm.group(1))) if mm else 0


def clean(t):
    if any(x in t for x in TRAP):
        return False
    return any(x in t for x in STRONG)


def pull(kw, mx=30):
    p = subprocess.run([PY, FETCH, "--keyword", kw, "--max-items", str(mx),
                        "--page-size", "50", "--output-format", "json"],
                       capture_output=True, text=True, encoding="utf-8", env=ENV, timeout=180)
    o = p.stdout or ""
    i = o.find("{")
    if i < 0:
        return []
    try:
        obj, _ = json.JSONDecoder().raw_decode(o[i:])
        return obj.get("items") or []
    except Exception:
        return []


# ---- 一期 JSON 的二次分析 ----
d = json.load(open("_redfox_sku_tier_probe.json", encoding="utf-8"))
print("=" * 90)
print("【一期二次分析】工具型 vs 内容型（基于 top5 标题）")
for k, v in d.items():
    if not v.get("n"):
        print("%-26s 样本不足" % k); continue
    tops = v.get("top", [])
    n_tool = sum(1 for t in tops if any(x in t["t"] for x in TOOL))
    n_story = sum(1 for t in tops if any(x in t["t"] for x in STORY))
    print("%-26s n=%-3d 中位%-6d | top5中 工具型%d 内容型%d" %
          (k, v["n"], v["like_med"], n_tool, n_story))

# ---- 补充跑 ----
print("\n" + "=" * 90)
print("【二期补跑】付费意愿 / 工具需求验证")
out = OrderedDict()
for name, kws in SUPP.items():
    seen, rows = set(), []
    for kw in kws:
        got = 0
        for it in pull(kw):
            nid = it.get("noteId")
            if not nid or nid in seen:
                continue
            seen.add(nid)
            like = num(it.get("likedCount"))
            t = (it.get("title") or "").strip()
            if not t or like <= 0 or not clean(t):
                continue
            rows.append({"t": t, "l": like, "c": num(it.get("collectedCount")),
                         "m": num(it.get("commentsCount")), "_kw": kw})
            got += 1
        print("  %-20s -> +%d (累计 %d)" % (kw, got, len(rows)))
    if rows:
        out[name] = {"n": len(rows),
                     "like_med": int(statistics.median(sorted(r["l"] for r in rows))),
                     "coll_med": int(statistics.median(sorted(r["c"] for r in rows))),
                     "hi3000": sum(1 for r in rows if r["l"] >= 3000),
                     "top": sorted(rows, key=lambda r: -r["l"])[:6]}
json.dump(out, open("_redfox_paywill_probe.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
for k, v in out.items():
    print("\n%s n=%d 赞中位%d 藏中位%d 高赞%d" % (k, v["n"], v["like_med"], v["coll_med"], v["hi3000"]))
    for t in v["top"]:
        print("   · %-44s 赞%-6d [%s]" % (t["t"][:44], t["l"], t["_kw"]))
