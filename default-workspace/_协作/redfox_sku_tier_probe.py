# -*- coding: utf-8 -*-
"""
SKU 三档（19.9 / 49.9 / 99.9）产品方向 · 红狐数据探针（2026-10-15）
用途：为每一档的候选产品方向拉红狐真实爆款数据，验证「需求是否存在 / 多大」。
纪律：① 只用真实拉到的数字；n<5 标「样本不足」
      ② 沿用 WB132 三大清洗陷阱 + 求职意图白名单
运行：python redfox_sku_tier_probe.py
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

# 三档候选方向 -> 关键词
GROUPS = OrderedDict([
    ("19.9 · 应届基础数据(现状)", ["秋招 网申 截止", "校招 时间表", "银行 秋招 截止日"]),
    ("49.9 · 双Skill订阅(现状)", ["冷门国企 秋招", "招满即止 秋招", "秋招 机会 汇总"]),
    ("99.9-A · 全套长期(跨周期)", ["秋招 春招 一起", "校招 全年 规划", "秋招 补录 春招"]),
    ("99.9-B · 跨人群(往届+社招)", ["往届生 求职", "毕业一年 找工作", "社招 应届生 投"]),
    ("99.9-C · 执行工具(排程/管理)", ["投递 管理 表", "秋招 日程 安排", "投递记录 模板"]),
    ("高价认可度(付费意愿)", ["求职资料 值得买吗", "校招表 推荐", "秋招 资料 有用吗"]),
])

WANT = ["秋招", "校招", "网申", "offer", "简历", "面试", "投", "招聘", "岗位",
        "截止", "笔试", "央国企", "国企", "外企", "银行", "大厂", "双非", "应届", "往届",
        "春招", "补录", "社招", "求职", "资料", "表格", "时间表"]

# 🔴 第四轮清洗（本轮人眼抽验发现的新污染）
#   T-E 综艺/娱乐：「音乐银行」（韩综）「浪姐节目组」「在线求职」综艺梗
#   T-F 文学散文：「我是你无法投递的过去」「月亮投递了几则碎片」
#   T-G 游戏：「冈易送来的投递名单」（网易游戏）
#   T-H 职场段子：「应届生刚找到工作，上班上到一半被开了」
TRAP = ["四大菩萨", "四大皆空", "祝你幸福", "留学", "考研报名", "中考", "高考", "金榜题名",
        "景区", "恋综", "相亲", "盒饭", "变脸", "万粉", "福利", "DJI", "礼物",
        # T-E 综艺娱乐
        "音乐银行", "浪姐", "节目组", "综艺", "选秀", "明星", "演员", "爱豆", "偶像",
        "音乐", "歌曲", "演唱会", "追星", "电视剧", "电影",
        # T-G 游戏
        "冈易", "原神", "蛋仔", "王者", "游戏", "抽卡", "氪金",
        # T-F 文学散文
        "无法投递", "碎片", "中秋快乐", "诗句", "散文", "文案", "朋友圈",
        # T-H 职场段子
        "被开", "上班上到一半", "摸鱼", "辞职", "老板", "同事", "打工人日常"]
TRAP2 = ["王多叶", "投了票", "的票", "投都投了", "投票", "吃吧", "妹妹", "爆改", "三无简历",
         "翻盘简历", "写简历", "简历模板", "改造简历", "进厂选秀", "你大坝", "水硕", "呼吸",
         "鬼灭", "地狱", "找实习", "实习攻略", "daily", "穿搭", "妆容",
         "我就这样", "当我", "吹了牛", "撒谎", "在简历上", "乱投", "韩国同事",
         "真的会谢", "破防", "笑死", "家人们", "谁懂", "离大谱", "表情包", "壁纸", "头像",
         "美甲", "脱单", "恋爱", "情感"]

# 🔴 强求职意图词（标题须命中其一，才算真·求职工具需求）
STRONG = ["秋招", "校招", "网申", "应届", "往届", "央国企", "国企", "补录", "春招",
          "内推", "投递", "offer", "笔试", "面经", "求职"]


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


def clean(title):
    if any(x in title for x in TRAP) or any(x in title for x in TRAP2):
        return False
    return any(x in title for x in STRONG)


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


def main():
    out = OrderedDict()
    for name, kws in GROUPS.items():
        seen, rows = set(), []
        for kw in kws:
            got = 0
            for it in pull(kw):
                nid = it.get("noteId")
                if not nid or nid in seen:
                    continue
                seen.add(nid)
                like = num(it.get("likedCount"))
                title = (it.get("title") or "").strip()
                if not title or like <= 0 or not clean(title):
                    continue
                rows.append({"t": title, "l": like,
                             "c": num(it.get("collectedCount")),
                             "m": num(it.get("commentsCount")), "_kw": kw})
                got += 1
            print("  %-22s %-20s -> +%d (累计 %d)" % (name, kw, got, len(rows)), file=sys.stderr)
        if not rows:
            out[name] = {"n": 0}
            continue
        likes = sorted(r["l"] for r in rows)
        out[name] = {
            "n": len(rows),
            "like_med": int(statistics.median(likes)),
            "like_avg": int(sum(likes) / len(likes)),
            "coll_med": int(statistics.median(sorted(r["c"] for r in rows))),
            "cmt_med": int(statistics.median(sorted(r["m"] for r in rows))),
            "hot_top": max(likes),
            "hi3000": sum(1 for r in rows if r["l"] >= 3000),
            "top": sorted(rows, key=lambda r: -r["l"])[:5],
        }
    json.dump(out, open("_redfox_sku_tier_probe.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\nWROTE _redfox_sku_tier_probe.json")
    print("=" * 100)
    for k, v in out.items():
        if not v.get("n"):
            print("%-26s 样本不足" % k)
            continue
        print("%-26s n=%-3d 赞中位%-6d 赞均值%-7d 藏中位%-6d 评中位%-5d 头部%-6d 高赞(≥3k)%-3d"
              % (k, v["n"], v["like_med"], v["like_avg"], v["coll_med"], v["cmt_med"],
                 v["hot_top"], v["hi3000"]))
        for t in v["top"][:3]:
            print("      · %-46s 赞%-6d [%s]" % (t["t"][:46], t["l"], t["_kw"]))


if __name__ == "__main__":
    main()
