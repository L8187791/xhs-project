# -*- coding: utf-8 -*-
"""来源字段拆分 · 按主运营最终裁定落表（任务卡 36 · 任务 B + C）

════════════════════════════════════════════════════════════
裁定依据：`主运营裁定-交付卡32-33-来源口径+期号+并发-2026-10-10.md`

【D1 最终口径 · 两轴拆分】
  source_level（来源可信度）：A 33 / B 37 / C 50，小计 **120**
  「确认滚动」11 家【不进 source_level 轴】，归 date_form 轴的「滚动·无固定截止」
  —— 因为「官网已核验」是可信度维度、「确认滚动」是日期形态维度，
     压在同一条轴上才是原来 7 级显得多的根因。

【D2 最终口径 · date_form 拆两档】
  硬日期 107 / 滚动·无固定截止 17 / **有日期待核实 3** / **未列明日期 4** = 131
  区分标准：note 里【有没有日期线索】
      有 → 去官网能查到（有目标）     无 → 公告本身就没写（查不到）

【任务 C · 否定语境防护 NEGATION_GUARD】
  案例：青岛银行 source = 「中公汇总(2026-09-04)，官网佐证**未找到**」
        关键词命中「官网」→ 一度被判成"含强源字样"。但它是否定句。
  危害：这是「自动化判级」的通病 —— 否定语境被当成肯定。
        将来任何自动回写 timetable.json 的脚本都会踩同一个坑。
  处置：见 NEGATION_GUARD 词表 + 模块加载时的**硬断言**（守则第 32 条）。
════════════════════════════════════════════════════════════
产出：
  1. 完整 CSV（131 行）
  2. 「拆不出来」清单 CSV
❌ 不回写 timetable.json（等主运营想清楚怎么对外说）

用法：python WB-来源拆分落表脚本.py
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
DEFAULT_DATA = os.path.join(WS, "技能包_时间表查询官", "data", "timetable.json")

URL_RE = re.compile(r"https?://[^\s，,；;）)】\]]+")
DATE_RE = re.compile(
    r"(20\d{2}\s*[-/年]\s*\d{1,2}\s*[-/月]\s*\d{1,2})"   # 2026-09-28 / 2026年9月1日
    r"|(\d{1,2}\s*月\s*\d{1,2}\s*日)"                     # 9月1日
)

STRONG_MARK = ["官方", "就业网", "官网"]

# ─────────────────────────────────────────────────────────
# ★ 否定语境防护 NEGATION_GUARD（任务 C · 守则第 32 条）
#   source 里写「官网佐证未找到」「未见官方入口」—— 命中了「官网」两个字，
#   但语义是【否定】强源，绝不能当成强源。
# ⚠️ 维护要求：新增任何"强源字样"时，必须同步检查这里是否有对应的否定说法。
# ─────────────────────────────────────────────────────────
NEGATION_GUARD = ["佐证未找到", "未见官方", "未找到", "官网未", "未核到", "无官方"]


def has_strong_mark(src):
    """source 文本是否指向强源。

    两条否决线：
      ① 命中任何否定语境 → 一律不算强源（哪怕写了「官网」两个字）
      ② 否则命中 STRONG_MARK 才算
    """
    s = src or ""
    if any(neg in s for neg in NEGATION_GUARD):
        return False
    return any(m in s for m in STRONG_MARK)


# ── 模块加载即自检：用真实事故样本做硬断言（不埋这条断言，下次还会踩同一个坑）──
_SAMPLE_NEG = "中公汇总(2026-09-04)，官网佐证未找到"      # 青岛银行事故原文
_SAMPLE_POS = "北京大学就业网转发(2026-09-20)"              # 正对照
assert has_strong_mark(_SAMPLE_NEG) is False, (
    "❌ 否定语境被误判为强源：%r（青岛银行案例 · 守则第 32 条）" % _SAMPLE_NEG)
assert has_strong_mark(_SAMPLE_POS) is True, (
    "❌ 正对照失效，防护词表收得过宽：%r" % _SAMPLE_POS)

# ── 裁定后的映射：source_level（确认滚动不在此轴上）──
LEVEL = {
    "官网原文": "A",
    "企业招聘系统": "A",
    "官网已核验-今日截止": "A",
    "就业网转发": "B",
    "第三方汇总": "C",
    "待核实": "C",
}
LEVEL_LABEL = {"A": "A 企业自己写的", "B": "B 二手或我们核过", "C": "C 第三方未核"}
ROLLING_STATUS = "确认滚动"          # 11 家 → 不进 source_level 轴
ROLLING_DEADLINE = "招满即止"

COLUMNS = ["序号", "企业名称", "网申截止日期", "剩余天数", "核实状态",
           "原source", "source_url", "source_level", "date_form", "拆分说明"]
UNSPLIT_COLUMNS = ["类别", "序号", "企业名称", "核实状态", "原source", "date_form", "拆不出来的原因"]


def pick_url(src):
    m = URL_RE.search(src or "")
    return m.group(0).rstrip("。，,；;") if m else ""


def pick_date_form(c):
    """D2 最终口径：date_form 四档"""
    dl = (c.get("deadline") or "").strip()
    note = str(c.get("note") or "")
    left = c.get("days_left")
    if isinstance(left, int) and not isinstance(left, bool):
        return "硬日期"
    if dl == ROLLING_DEADLINE:
        return "滚动·无固定截止"
    # 走到这里 = deadline 为空
    return "有日期待核实" if DATE_RE.search(note) else "未列明日期"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--outdir", default=os.path.join(WS, "_扩充"))
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    rows = data["companies"]

    out_rows, unsplit = [], []
    for c in rows:
        src = str(c.get("source", "") or "")
        st = c.get("verify_status", "")
        url = pick_url(src)
        df = pick_date_form(c)
        is_rolling = (st == ROLLING_STATUS)

        # source_level：确认滚动不进此轴 → 留空
        lv = "" if is_rolling else LEVEL.get(st, "C")

        notes = []
        if is_rolling:
            notes.append("确认滚动 → 不进 source_level 轴（归 date_form·滚动·无固定截止）")
        if not url:
            notes.append("source 内无 http 链接 → source_url 留空（未见来源链接）")
            unsplit.append(["① 拆不出来源链接", c.get("no", ""), c.get("company", ""), st, src, df,
                            "source 字段里没有 http 链接，无法拆出 source_url"])
        # 等级存疑：只看非滚动条目（滚动条目已不在 source_level 轴上）
        if not is_rolling and st in ("第三方汇总", "待核实") and has_strong_mark(src):
            notes.append("⚠️ 状态为弱档但 source 字样含「官方/就业网」，若对外标注来源可信度需回查")
            unsplit.append(["③ 来源字样与状态不一致·需回查", c.get("no", ""), c.get("company", ""),
                            st, src, df,
                            "verify_status 判为弱档，但 source 字样指向强源，两者矛盾；"
                            "新口径下不影响等级，但若对外标注来源可信度需回查采集记录"])
        if df == "有日期待核实":
            notes.append("note 内有日期线索但未采信，未折算为硬日期")
        elif df == "未列明日期":
            notes.append("note 内亦无日期 → 官网同样查不到")

        out_rows.append({
            "序号": c.get("no", ""),
            "企业名称": c.get("company", ""),
            "网申截止日期": c.get("deadline", ""),
            "剩余天数": c.get("days_left", ""),
            "核实状态": st,
            "原source": src,
            "source_url": url,
            "source_level": lv,
            "date_form": df,
            "拆分说明": "；".join(notes),
        })

    os.makedirs(args.outdir, exist_ok=True)
    p_main = os.path.join(args.outdir, "WB-timetable-来源拆分落表-2026-10-10.csv")
    p_un = os.path.join(args.outdir, "WB-来源拆分-拆不出来清单-2026-10-10.csv")

    for path, cols, rs in [(p_main, COLUMNS, out_rows), (p_un, UNSPLIT_COLUMNS, unsplit)]:
        with open(path, "w", encoding="utf-8", newline="") as f:
            if rs and isinstance(rs[0], dict):
                w = csv.DictWriter(f, fieldnames=cols)
                w.writeheader()
                w.writerows(rs)
            else:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerows(rs)
        with open(path, "rb") as f:
            raw = f.read(3)
        assert raw[:3] != b"\xef\xbb\xbf", "❌ CSV 出现 BOM：%s" % path

    lv = Counter(r["source_level"] for r in out_rows)
    df = Counter(r["date_form"] for r in out_rows)
    url_n = sum(1 for r in out_rows if r["source_url"])

    print("=== 任务 C 自检（否定语境防护）===")
    print("  否定样本 %r" % _SAMPLE_NEG)
    print("          → 强源判定 = %s  ✅（必须 False）" % has_strong_mark(_SAMPLE_NEG))
    print("  正对照   %r" % _SAMPLE_POS)
    print("          → 强源判定 = %s  ✅（必须 True）" % has_strong_mark(_SAMPLE_POS))
    print()
    print("=== 任务 B 落表结果 ===")
    print("总行数：%d" % len(out_rows))
    print("source_level：A=%d B=%d C=%d　小计=%d；确认滚动 %d 家不在此轴（合计仍 131）" % (
        lv["A"], lv["B"], lv["C"], lv["A"] + lv["B"] + lv["C"], lv[""]))
    print("date_form：硬日期=%d　滚动·无固定截止=%d　有日期待核实=%d　未列明日期=%d　小计=%d" % (
        df["硬日期"], df["滚动·无固定截止"], df["有日期待核实"], df["未列明日期"],
        sum(df.values())))
    print("含 source_url：%d / %d = %.0f%%" % (url_n, len(out_rows), url_n / len(out_rows) * 100))
    print()
    print("=== 交叉验收（我自己重算 vs 主运营裁定）===")
    exp_lv = {"A": 33, "B": 37, "C": 50, "": 11}
    exp_df = {"硬日期": 107, "滚动·无固定截止": 17, "有日期待核实": 3, "未列明日期": 4}
    ok = True
    for k, v in exp_lv.items():
        got = lv.get(k, 0)
        if got != v:
            ok = False
        print("  %s source_level %s：期望 %d，实得 %d" % (
            "✅" if got == v else "❌", k or "（确认滚动·不进轴）", v, got))
    for k, v in exp_df.items():
        got = df.get(k, 0)
        if got != v:
            ok = False
        print("  %s date_form %s：期望 %d，实得 %d" % (
            "✅" if got == v else "❌", k, v, got))
    assert ok, "❌ 与裁定不符，落表中止"
    print()
    print("=== 有日期待核实 / 未列明日期 明细 ===")
    for r in out_rows:
        if r["date_form"] in ("有日期待核实", "未列明日期"):
            print("  [%-8s] %s" % (r["date_form"], r["企业名称"]))
    print()
    print("=== 拆不出来清单 ===")
    cat = Counter(u[0] for u in unsplit)
    for k, v in sorted(cat.items()):
        print("  %s：%d 条" % (k, v))
    print("  合计：%d 条" % len(unsplit))
    print()
    print("输出：%s" % p_main)
    print("输出：%s" % p_un)
    print("⚠️ timetable.json 未改动")


if __name__ == "__main__":
    main()
