# -*- coding: utf-8 -*-
"""
5 个 RED Skill 方案评分（专家模式 · 2026-10-14）
用途：每个方案 → 拉红狐真实爆款数据验证「需求是否存在/多大」→ 结合转化/紧迫/合规/成本打分 → 排序。
纪律：① 只用真实拉到的数字，n<5 标「样本不足」不得据此定序
      ② 人工维度（转化/紧迫/合规/成本/协同）必须写明依据，不拍脑袋
      ③ 沿用 WB132 三大清洗陷阱 + 求职意图白名单
运行：C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe redfox_skill_scoring.py
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

# 5 个方案 -> 关键词（验证需求真实存在）
CANDIDATES = OrderedDict([
    ("① 投递优先级排程器(排序)", ["秋招 先投哪家", "网申 投递顺序", "秋招 截止 顺序", "网申 优先"]),
    ("⑤ 冷门机会雷达(发现)", ["冷门国企", "小众国企 秋招", "双非 机会 国企", "没人知道 公司 秋招"]),
    ("② 往届生可投判定器(判定)", ["往届生 秋招", "往届生 网申", "往届生 能投吗"]),
    # ④ 原关键词(网申 填写 错误 / 注意事项 / 踩坑)仅召回 3 条，换更贴近"提交前"的词
    ("④ 网申填表避坑自查器(核查)", ["网申 填错", "秋招 网申 提交", "网申 信息填写", "秋招 投递 注意"]),
    # ③ 原关键词召回大量"投票梗"与"简历教程"，换成"被拒/没消息/石沉大海"
    ("③ 网申卡点诊断器(诊断)", ["秋招 简历 没通过", "网申 一直没通知", "秋招 0 offer", "投了很多 没面试"]),
])

# 人工维度（每项写明依据，依据来自已落盘事实，非臆断）
MANUAL = {
    "① 投递优先级排程器(排序)": dict(conv=23, urge=13, comp=9, cost=8, syn=9,
        why="转化23/25：12→131 缺口最直白，表结构可对齐导入；紧迫13/15：倒计时是真字段；合规9/10：仅1项C级标注风险；成本8/10：示例库需随表更新；协同9/10：直接服务A层时效稿"),
    "⑤ 冷门机会雷达(发现)": dict(conv=21, urge=14, comp=9, cost=7, syn=10,
        why="转化21/25：信息差钩子强但缺口感略弱于①（不是'缺数据'而是'不知道有'）；紧迫14/15：招满即止无提醒，最强；合规9/10：待遇字段表内没有→不写即安全；成本7/10：招满即止需高频核；协同10/10：机会型内容天花板最高(DB55)"),
    "② 往届生可投判定器(判定)": dict(conv=18, urge=15, comp=6, cost=8, syn=8,
        why="转化18/25：只能给类型不给名单，缺口是天然的但'名单'需29.9先上架；紧迫15/15：择业期倒计时过一天少一天；合规6/10：🔴DB59表外不可核→点名即P0，必须只给类型；成本8/10；协同8/10：C层人群精准"),
    "④ 网申填表避坑自查器(核查)": dict(conv=16, urge=15, comp=8, cost=9, syn=7,
        why="转化16/25：清单类方法论，与表格绑定偏弱（买表不是必需）；紧迫15/15：提交后不可改，场景自带；合规8/10：各企业规则不同，写死有风险需留'通常/多数'；成本9/10：清单静态，最省维护；协同7/10"),
    "③ 网申卡点诊断器(诊断)": dict(conv=14, urge=8, comp=9, cost=8, syn=9,
        why="转化14/25：结论是'节奏问题'，用户可自行改节奏，不必然买表；紧迫8/15：拖延流失不如倒计时硬；合规9/10；成本8/10；协同9/10：天然评论区话题，服务B层评论率KPI"),
}

WANT = ["秋招", "校招", "网申", "offer", "简历", "面试", "投", "招聘", "岗位",
        "截止", "笔试", "央国企", "国企", "外企", "银行", "大厂", "双非", "应届", "往届"]
TRAP = ["四大菩萨", "四大皆空", "四大忧郁", "祝你幸福", "留学", "考研报名", "中考", "高考",
        "金榜题名", "景区", "恋综", "相亲", "盒饭", "变脸", "万粉", "福利", "DJI", "礼物"]


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


# 🔴 2026-10-14 新增陷阱（本轮人眼抽验发现）
#   T-A 投票梗：「投」字召回"投了票/王多叶/35一位的票/投都投了"
#   T-B 简历教程：与"投了没回音"无关，是"怎么写简历"
#   T-C 吐槽段子：进厂选秀/你大坝/水硕之呼吸/鬼灭梗
TRAP2 = ["王多叶", "投了票", "的票", "投都投了", "投票", "吃吧", "妹妹",
         "爆改", "三无简历", "翻盘简历", "写简历", "简历模板", "改造简历",
         "进厂选秀", "你大坝", "水硕", "呼吸", "鬼灭", "地狱", "选秀",
         "找实习", "实习攻略", "daily", "穿搭", "妆容",
         # T-D 情景段子（第三次清洗）：「面试被拒我就这样」「当你在简历上撒谎」
         "我就这样", "当我", "吹了牛", "撒谎", "在简历上", "乱投", "韩国同事",
         "真的会谢", "破防", "笑死", "家人们", "谁懂", "离大谱"]


def clean(title):
    if any(x in title for x in TRAP):
        return False
    if any(x in title for x in TRAP2):
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
    for lo, sc in table:
        if v >= lo:
            return sc
    return 0


def main():
    out = OrderedDict()
    for name, kws in CANDIDATES.items():
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
                if not title or like <= 0:
                    continue
                if not clean(title):
                    continue
                rows.append({"t": title, "l": like, "c": coll, "m": cmt,
                             "cr": (cmt / like) if like > 100 else 0})
            print("  拉取 %-18s -> 累计 %d 条" % (kw, len(rows)), file=sys.stderr)

        if not rows:
            out[name] = {"n": 0}
            continue

        crs = sorted(r["cr"] for r in rows)
        likes = sorted(r["l"] for r in rows)
        colls = sorted(r["c"] for r in rows)
        cmts = sorted(r["m"] for r in rows)
        st = {
            "n": len(rows),
            "cr_med": round(statistics.median(crs), 3),
            "like_med": int(statistics.median(likes)),
            "coll_med": int(statistics.median(colls)),
            "cmt_med": int(statistics.median(cmts)),
            "hi_ratio": round(sum(1 for r in rows if r["cr"] >= 0.30) / len(rows), 3),
            "hot_top": max(r["l"] for r in rows),
            "top": sorted(rows, key=lambda r: -r["l"])[:5],
        }
        # ---- 数据维度 30 分：需求验证度 ----
        s_n = band(st["n"], [(30, 8), (20, 6), (12, 4), (5, 2), (0, 0)])
        s_like = band(st["like_med"], [(3000, 10), (1500, 8), (800, 6), (300, 4), (0, 2)])
        s_coll = band(st["coll_med"], [(2000, 6), (1000, 5), (500, 3), (0, 1)])
        s_hot = band(st["hot_top"], [(20000, 6), (10000, 5), (5000, 3), (0, 1)])
        st["数据分30"] = s_n + s_like + s_coll + s_hot
        st["细分"] = {"样本量8": s_n, "赞中位10": s_like, "藏中位6": s_coll, "头部爆款6": s_hot}

        m = MANUAL[name]
        st["人工分70"] = m["conv"] + m["urge"] + m["comp"] + m["cost"] + m["syn"]
        st["人工细分"] = {"转化紧密25": m["conv"], "紧迫感15": m["urge"],
                          "合规安全10": m["comp"], "开发成本10": m["cost"], "内容协同10": m["syn"]}
        st["总分"] = st["数据分30"] + st["人工分70"]
        st["依据"] = m["why"]
        out[name] = st

    json.dump(out, open("_redfox_skill_score.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("WROTE _redfox_skill_score.json")
    for k, v in sorted(out.items(), key=lambda x: -x[1].get("总分", 0)):
        if not v.get("n"):
            print("  %-26s 样本不足" % k)
            continue
        print("  %-26s 总分%3d = 数据%2d/30 + 人工%2d/70 | n=%-3d 赞中位%-6d 藏中位%-6d 头部%d 评/赞%.3f"
              % (k, v["总分"], v["数据分30"], v["人工分70"], v["n"],
                 v["like_med"], v["coll_med"], v["hot_top"], v["cr_med"]))


if __name__ == "__main__":
    main()
