# -*- coding: utf-8 -*-
"""关闸清单生成脚本 v1.0（落地卡 25 · 任务 A）

从「求职时间表 AI 助手」技能包的 timetable.json 生成未来 7–15 天内截止的清单。

铁律（卡面硬性）：
  1. days_left < 0 的必须剔除（"不漏投"的底线）
  2. 不猜日期；days_left 为空的（无固定截止）单列一节
  3. 无绝对化用语
  4. 不给建议
  5. 过 compliance_gate.py，P0=0

用法：
  python gen_closing_list.py [--data 路径] [--window 15] [--outdir 关闸清单]
"""
import argparse
import datetime
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
DEFAULT_DATA = os.path.join(WS, "技能包_时间表查询官", "data", "timetable.json")
DEFAULT_OUTDIR = os.path.join(WS, "关闸清单")

# 核实状态 → 三档（强 → 弱）
# 🟢 企业自己写的：企业官网原文 / 企业自有招聘系统 / 我们核到官网且确认当日口径
# 🟡 二手或我们核过：高校就业网等转发官方公告
# 🔴 第三方未核：公开汇总、待核实
TIER = {
    "官网原文": ("🟢", "企业自己写的"),
    "企业招聘系统": ("🟢", "企业自己写的"),
    "官网已核验-今日截止": ("🟢", "企业自己写的"),
    "就业网转发": ("🟡", "二手或我们核过"),
    "确认滚动": ("🟡", "二手或我们核过"),
    "第三方汇总": ("🔴", "第三方未核"),
    "待核实": ("🔴", "第三方未核"),
}
UNKNOWN_TIER = ("🔴", "第三方未核")  # 未知一律按最弱处理，不抬高档位

# date_form 四档（v1.0.9 两轴口径）—— 下册按此字段分档，不硬编码企业名
DF_LABEL = {"hard": "硬日期", "rolling": "招满即止",
            "to_verify": "有日期待核实", "none": "未列明日期"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tier_of(status):
    return TIER.get(status, UNKNOWN_TIER)


def next_issue_no(outdir):
    """期号 = 现有 *_关闸清单.md 数量 + 1，保证连续不重复"""
    if not os.path.isdir(outdir):
        return 1
    n = len([f for f in os.listdir(outdir) if f.endswith("_关闸清单.md")])
    return n + 1


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def build(data, window, data_date, issue_no, today, urgent=7):
    """J1 裁定：分两档 —— 「7 天内紧急」+「8–15 天」。
    硬规则不变：days_left < 0 一律剔除。"""
    rows = data["companies"]
    meta = data.get("meta", {})

    in_window = [c for c in rows if is_int(c.get("days_left")) and 0 <= c["days_left"] <= window]
    in_window.sort(key=lambda c: (c["days_left"], c.get("no", 0)))
    # 两档切分（urgent 默认 7）
    band_urgent = [c for c in in_window if c["days_left"] <= urgent]
    band_soon = [c for c in in_window if c["days_left"] > urgent]

    expired = [c for c in rows if is_int(c.get("days_left")) and c["days_left"] < 0]
    beyond = [c for c in rows if is_int(c.get("days_left")) and c["days_left"] > window]
    no_deadline = [c for c in rows if not is_int(c.get("days_left"))]

    # —— 自检：已截止的必须为 0 条进清单 ——
    assert all(c["days_left"] >= 0 for c in in_window), "❌ 已截止项混入清单"
    # —— 自检：两档相加 = 上册总数，不重不漏 ——
    assert len(band_urgent) + len(band_soon) == len(in_window), "❌ 两档切分丢条"

    tier_cnt = {"🟢": 0, "🟡": 0, "🔴": 0}
    for c in in_window:
        tier_cnt[tier_of(c.get("verify_status", ""))[0]] += 1

    return in_window, (band_urgent, band_soon), expired, beyond, no_deadline, tier_cnt, meta


def render_md(bands, no_deadline, tier_cnt, meta, window, issue_no, data_date, today, total, expired, beyond, urgent=7):
    items = bands[0] + bands[1]
    L = []
    A = L.append
    A("# 关闸清单 · 第 %d 期" % issue_no)
    A("")
    A("数据核验日期：%s　｜　更新节奏：每周五更新　｜　已截止的已剔除" % data_date)
    A("")
    A("- 数据来源：`技能包_时间表查询官/data/timetable.json`（%d 家，版本 %s）" % (total, meta.get("version", "")))
    A("- 生成时间：%s" % today)
    A("- 筛选口径：剩余天数 ∈ [0, %d]，按剩余天数由少到多排列" % window)
    A("")
    A("> 本清单只做排期，不替你决定投哪家。截止时间请以企业官网为准。")
    A("")
    A("核实状态三档：🟢 企业自己写的　｜　🟡 二手或我们核过　｜　🔴 第三方未核")
    A("")
    A("## 一、未来 %d 天内截止（共 %d 家）" % (window, len(items)))
    A("")
    A("### 一-A · %d 天内截止（紧急，共 %d 家）" % (urgent, len(bands[0])))
    A("")
    A("| 企业 | 截止日 | 剩余天数 | 核实状态 |")
    A("|---|---|---|---|")
    for c in bands[0]:
        icon, label = tier_of(c.get("verify_status", ""))
        A("| %s | %s | %d | %s %s |" % (c["company"], c.get("deadline", ""), c["days_left"], icon, label))
    A("")
    A("### 一-B · %d–%d 天截止（共 %d 家）" % (urgent + 1, window, len(bands[1])))
    A("")
    A("| 企业 | 截止日 | 剩余天数 | 核实状态 |")
    A("|---|---|---|---|")
    for c in bands[1]:
        icon, label = tier_of(c.get("verify_status", ""))
        A("| %s | %s | %d | %s %s |" % (c["company"], c.get("deadline", ""), c["days_left"], icon, label))
    A("")
    nd_rolling = [c for c in no_deadline if c.get("date_form") == "rolling"]
    nd_verify = [c for c in no_deadline if c.get("date_form") == "to_verify"]
    nd_none = [c for c in no_deadline if c.get("date_form") == "none"]
    nd_other = [c for c in no_deadline if c.get("date_form") not in ("rolling", "to_verify", "none")]

    A("## 二、招满即止 · 无固定截止（共 %d 家）" % len(no_deadline))
    A("")
    A("这些条在官方口径里没有写死截止日，或有日期但无法解析为确定日期，因此不入上册。")
    A("")
    # ★ K4 裁定：下册按 date_form 字段分档（读字段，不硬编码企业名）
    A("### 二-A · 招满即止（共 %d 家）" % len(nd_rolling))
    A("")
    A("| 企业 | 截止口径 | 核实状态 |")
    A("|---|---|---|")
    for c in nd_rolling:
        icon, label = tier_of(c.get("verify_status", ""))
        A("| %s | %s | %s %s |" % (c["company"], DF_LABEL.get("rolling"), icon, label))
    A("")
    A("### 二-B · 有日期待核实（共 %d 家）" % len(nd_verify))
    A("")
    A("note 里有日期线索，但来源是转载页/汇总表，未采信为硬日期 —— 去官网核对能查到。")
    A("")
    A("| 企业 | 截止口径 | 核实状态 |")
    A("|---|---|---|")
    for c in nd_verify:
        icon, label = tier_of(c.get("verify_status", ""))
        A("| %s | %s | %s %s |" % (c["company"], DF_LABEL.get("to_verify"), icon, label))
    A("")
    A("### 二-C · 未列明日期（共 %d 家）" % len(nd_none))
    A("")
    A("公告本身就没写截止日 —— 去官网也查不到。")
    A("")
    A("| 企业 | 截止口径 | 核实状态 |")
    A("|---|---|---|")
    for c in nd_none:
        icon, label = tier_of(c.get("verify_status", ""))
        A("| %s | %s | %s %s |" % (c["company"], DF_LABEL.get("none"), icon, label))
    A("")
    A("## 三、本期统计")
    A("")
    A("- 上册入册：%d 家" % len(items))
    A("- 下册（无固定截止）：%d 家" % len(no_deadline))
    A("  - 招满即止：%d 家" % len(nd_rolling))
    A("  - 有日期待核实：%d 家（去官网能查到）" % len(nd_verify))
    A("  - 未列明日期：%d 家（公告本身没写）" % len(nd_none))
    A("- 未入册·已截止（剩余天数为负）：%d 家" % len(expired))
    A("- 未入册·超出窗口（剩余天数 > %d）：%d 家" % (window, len(beyond)))
    A("- 三档分布：🟢 %d　｜　🟡 %d　｜　🔴 %d" % (tier_cnt["🟢"], tier_cnt["🟡"], tier_cnt["🔴"]))
    A("")
    A("---")
    A("")
    A("数据以核验日期为准，投递前请以官网为准。")
    return "\n".join(L)


def render_txt(bands, no_deadline, tier_cnt, meta, window, issue_no, data_date, today, total, expired, beyond, urgent=7):
    items = bands[0] + bands[1]
    L = []
    A = L.append
    A("关闸清单 · 第 %d 期" % issue_no)
    A("数据核验日期：%s｜更新节奏：每周五更新｜已截止的已剔除" % data_date)
    A("数据来源：技能包_时间表查询官/data/timetable.json（%d 家，版本 %s）" % (total, meta.get("version", "")))
    A("生成时间：%s" % today)
    A("核实状态三档：🟢 企业自己写的｜🟡 二手或我们核过｜🔴 第三方未核")
    A("本清单只做排期，不替你决定投哪家。截止时间请以企业官网为准。")
    A("")
    A("【一-A、%d 天内截止 · 紧急】共 %d 家" % (urgent, len(bands[0])))
    for i, c in enumerate(bands[0], 1):
        icon, label = tier_of(c.get("verify_status", ""))
        A("%2d. %s　截止 %s　剩 %d 天　%s%s" % (i, c["company"], c.get("deadline", ""), c["days_left"], icon, label))
    A("")
    A("【一-B、%d–%d 天截止】共 %d 家" % (urgent + 1, window, len(bands[1])))
    for i, c in enumerate(bands[1], 1):
        icon, label = tier_of(c.get("verify_status", ""))
        A("%2d. %s　截止 %s　剩 %d 天　%s%s" % (i, c["company"], c.get("deadline", ""), c["days_left"], icon, label))
    A("")
    nd_rolling = [c for c in no_deadline if c.get("date_form") == "rolling"]
    nd_verify = [c for c in no_deadline if c.get("date_form") == "to_verify"]
    nd_none = [c for c in no_deadline if c.get("date_form") == "none"]

    A("【二-A、招满即止】共 %d 家" % len(nd_rolling))
    for i, c in enumerate(nd_rolling, 1):
        icon, label = tier_of(c.get("verify_status", ""))
        A("%2d. %s　截止口径：%s　%s%s" % (i, c["company"], DF_LABEL["rolling"], icon, label))
    A("")
    A("【二-B、有日期待核实】共 %d 家（去官网能查到）" % len(nd_verify))
    for i, c in enumerate(nd_verify, 1):
        icon, label = tier_of(c.get("verify_status", ""))
        A("%2d. %s　截止口径：%s　%s%s" % (i, c["company"], DF_LABEL["to_verify"], icon, label))
    A("")
    A("【二-C、未列明日期】共 %d 家（公告本身没写，官网也查不到）" % len(nd_none))
    for i, c in enumerate(nd_none, 1):
        icon, label = tier_of(c.get("verify_status", ""))
        A("%2d. %s　截止口径：%s　%s%s" % (i, c["company"], DF_LABEL["none"], icon, label))
    A("")
    A("【三、本期统计】")
    A("上册入册：%d 家" % len(items))
    A("下册（无固定截止）：%d 家" % len(no_deadline))
    A("未入册·已截止（剩余天数为负）：%d 家" % len(expired))
    A("未入册·超出窗口（剩余天数 > %d）：%d 家" % (window, len(beyond)))
    A("三档分布：🟢 %d｜🟡 %d｜🔴 %d" % (tier_cnt["🟢"], tier_cnt["🟡"], tier_cnt["🔴"]))
    A("")
    A("数据以核验日期为准，投递前请以官网为准。")
    return "\n".join(L)


def write_nobom(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(path, "rb") as f:
        raw = f.read(3)
    assert raw[:3] != b"\xef\xbb\xbf", "❌ 出现 BOM：%s" % path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--window", type=int, default=15)
    ap.add_argument("--urgent", type=int, default=7, help="紧急档分界（默认 7 天）")
    ap.add_argument("--outdir", default=DEFAULT_OUTDIR)
    # 期号可显式指定（卡 36 任务 A 要求保留的修复）。
    # 原因：next_issue_no() 按 outdir 内 *_关闸清单.md 的**文件个数**推算期号，
    # 换一个输出目录重跑就会算错（_扩充 里 0 个 → 误标「第 1 期」），
    # 曾导致同一份内容被标成两个不同期号（见交付卡 33 的 D10）。
    ap.add_argument("--issue", type=int, default=None, help="指定期号；不给则沿用自动推算")
    ap.add_argument("--expect-nodl", type=int, default=7,
                    help="下册两档（有日期待核实+未列明日期）应有条数，默认 7（本数据日口径）")
    args = ap.parse_args()

    data = load(args.data)
    rows = data["companies"]
    meta = data.get("meta", {})
    data_date = meta.get("data_date") or datetime.date.today().isoformat()
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    os.makedirs(args.outdir, exist_ok=True)
    issue_no = args.issue if args.issue is not None else next_issue_no(args.outdir)

    items, bands, expired, beyond, no_deadline, tier_cnt, meta = build(
        data, args.window, data_date, issue_no, today, urgent=args.urgent)
    total = len(rows)
    assert len(items) + len(expired) + len(beyond) + len(no_deadline) == total, "❌ 四类相加不等于总数"

    # ★ 卡 41 任务 A：下册按 date_form 分两档，两档相加必须等于「无日期条目」总数
    n_verify = sum(1 for c in no_deadline if c.get("date_form") == "to_verify")
    n_none = sum(1 for c in no_deadline if c.get("date_form") == "none")
    n_empty_dl = sum(1 for c in rows if not str(c.get("deadline") or "").strip())
    # 结构性断言（永远应成立，不受数据变化影响）
    assert n_verify + n_none == n_empty_dl, (
        "❌ 下册两档相加(%d) ≠ 无deadline条目数(%d)" % (n_verify + n_none, n_empty_dl))
    # 卡面指定的当期数值断言（下期数据变了用 --expect-nodl 改）
    assert n_verify + n_none == args.expect_nodl, (
        "❌ 下册两档相加 = %d，期望 %d（有日期待核实 %d + 未列明日期 %d）"
        % (n_verify + n_none, args.expect_nodl, n_verify, n_none))

    md = render_md(bands, no_deadline, tier_cnt, meta, args.window, issue_no, data_date, today, total, expired, beyond, args.urgent)
    txt = render_txt(bands, no_deadline, tier_cnt, meta, args.window, issue_no, data_date, today, total, expired, beyond, args.urgent)

    base = "%s_关闸清单" % datetime.date.today().isoformat()
    p_md = os.path.join(args.outdir, base + ".md")
    p_txt = os.path.join(args.outdir, base + ".txt")
    write_nobom(p_md, md)
    write_nobom(p_txt, txt)

    print("期号：第 %d 期" % issue_no)
    print("上册（0–%d 天）：%d 家　＝ 紧急档（≤%d 天）%d 家 + 次急档（%d–%d 天）%d 家" % (
        args.window, len(items), args.urgent, len(bands[0]),
        args.urgent + 1, args.window, len(bands[1])))
    print("下册（无固定截止）：%d 家" % len(no_deadline))
    print("已剔除（days_left<0）：%d 家" % len(expired))
    print("三档：🟢%d 🟡%d 🔴%d" % (tier_cnt["🟢"], tier_cnt["🟡"], tier_cnt["🔴"]))
    print("清单内含已截止项条数（必须为 0）：%d" % len([c for c in items if c["days_left"] < 0]))
    print("输出：%s" % p_md)
    print("输出：%s" % p_txt)


if __name__ == "__main__":
    main()
