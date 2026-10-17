# -*- coding: utf-8 -*-
"""
三层定题（A时效 / B机会型 / C往届生）红狐实证挖掘
输出：每个方向的 赞/藏/评 中位数、评论率代理（评/赞）、TOP 标题
"""
import json
import os
import subprocess
import sys
import statistics
from collections import OrderedDict

PY = sys.executable
SCRIPT_DIR = r"C:/Users/Administrator/.workbuddy/plugins/cache/experts/redfox-xhs-creator/1.0.0/skills/xiaohongshu-write/scripts"
SCRIPT = os.path.join(SCRIPT_DIR, "fetch_xhs_hot_articles.py")

# 三层 × 关键词
LAYERS = OrderedDict([
    ("A层·时效截止", ["秋招截止", "网申截止", "秋招时间表", "截止提醒"]),
    ("B层·机会型",   ["双非", "中小厂", "免笔试", "大厂"]),
    ("C层·往届生",   ["往届生", "往届生求职", "26届", "毕业后还能校招吗"]),
])


def num(x):
    """红狐的量级字段可能是 '5000+' / '1.2万' / 纯数字"""
    if x is None:
        return 0
    s = str(x).strip().replace(",", "")
    try:
        if s.endswith("万"):
            return int(float(s[:-1]) * 10000)
        if s.endswith("+"):
            return int(float(s[:-1]))
        if s.endswith("k") or s.endswith("K"):
            return int(float(s[:-1]) * 1000)
        return int(float(s))
    except Exception:
        return 0


def fetch(keyword, max_items=20):
    env = dict(os.environ)
    try:
        key = open(r"C:/Users/Administrator/.workbuddy/redfox.env", encoding="utf-8").read()
        for line in key.splitlines():
            if line.startswith("export REDFOX_API_KEY="):
                env["REDFOX_API_KEY"] = line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    cmd = [PY, SCRIPT, "--keyword", keyword, "--max-items", str(max_items),
           "--page-size", "50", "--output-format", "json"]
    try:
        p = subprocess.run(cmd, capture_output=True, cwd=SCRIPT_DIR, env=env, timeout=120)
        out = (p.stdout or b"").decode("utf-8", "ignore")
        i = out.find("{")
        if i < 0:
            return []
        o, _ = json.JSONDecoder().raw_decode(out[i:])
        return o.get("items") or []
    except Exception as e:
        print("  ERR %s: %s" % (keyword, e), file=sys.stderr)
        return []


def main():
    result = OrderedDict()
    for layer, kws in LAYERS.items():
        all_items = []
        per_kw = OrderedDict()
        for kw in kws:
            items = fetch(kw)
            per_kw[kw] = items
            all_items.extend(items)
            print("  拉取 %-14s -> %d 条" % (kw, len(items)), file=sys.stderr)

        # 去重（按标题）
        seen = set()
        uniq = []
        for it in all_items:
            t = (it.get("title") or "").strip()
            if not t or t in seen:
                continue
            seen.add(t)
            uniq.append(it)

        rows = []
        for it in uniq:
            l = num(it.get("likedCount"))
            c = num(it.get("collectedCount"))
            cm = num(it.get("commentsCount"))
            rows.append({
                "title": (it.get("title") or "")[:46],
                "liked": l, "collected": c, "comments": cm,
                "fans": it.get("authorFans"),
                "ratio": round(cm / l, 3) if l > 100 else None,
            })

        rows.sort(key=lambda r: -r["comments"])
        result[layer] = {"kw_count": {k: len(v) for k, v in per_kw.items()},
                         "total": len(rows), "rows": rows}

    # ---- 输出统计 ----
    print("\n" + "=" * 78)
    print("三层定题 · 红狐实证挖掘（%s）" % "2026-10-14")
    print("=" * 78)
    for layer, d in result.items():
        rows = d["rows"]
        if not rows:
            print("\n【%s】无数据" % layer)
            continue
        lik = [r["liked"] for r in rows if r["liked"] > 0]
        col = [r["collected"] for r in rows if r["collected"] > 0]
        cmt = [r["comments"] for r in rows if r["comments"] > 0]
        ratios = [r["ratio"] for r in rows if r["ratio"] is not None]
        print("\n【%s】样本 %d 篇（关键词：%s）" % (
            layer, d["total"], "、".join("%s(%d)" % (k, v) for k, v in d["kw_count"].items())))
        print("  点赞  中位数 %-8d 均值 %-8d 最高 %d" % (
            statistics.median(lik), sum(lik) // len(lik), max(lik)))
        print("  收藏  中位数 %-8d 均值 %-8d 最高 %d" % (
            statistics.median(col), sum(col) // len(col), max(col)))
        print("  评论  中位数 %-8d 均值 %-8d 最高 %d" % (
            statistics.median(cmt), sum(cmt) // len(cmt), max(cmt)))
        if ratios:
            print("  🔴 评/赞 中位数 %.3f  （我方基线 0.056；≥0.3 视为高互动型）" % statistics.median(ratios))
            hi = [r for r in ratios if r >= 0.3]
            print("     评/赞 ≥0.3 的篇数：%d / %d（%.0f%%）" % (
                len(hi), len(ratios), 100.0 * len(hi) / len(ratios)))
        print("  --- 评论数 TOP8 ---")
        for r in rows[:8]:
            print("   %-46s 赞%-7d 藏%-7d 评%-6d 评/赞%s" % (
                r["title"], r["liked"], r["collected"], r["comments"],
                r["ratio"] if r["ratio"] is not None else "-"))

    json.dump(result, open("_redfox_layer_result.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n已存 _redfox_layer_result.json")


if __name__ == "__main__":
    main()
