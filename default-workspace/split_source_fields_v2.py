# -*- coding: utf-8 -*-
"""T2 来源字段拆分 · 按主运营裁定落表（任务卡 30 · 任务 B / P1）

裁定（卡 30 第二节）：
  ✅ A/B/C 三档 = 33 / 48 / 50
  ✅ 「确认滚动」单开 ⚪ 第四档，不参与 A/B/C
  ✅ 「官网已核验-今日截止」归 🟢(A)
  ✅ date_form「待公布」改「有日期待核实」
  ⚠️ source_url 先别回写（现状 16%，主运营要想清楚怎么对外说）

产出：
  1. 完整 CSV（131 行 + ⚪ 列）
  2. 「拆不出来」清单 CSV（无法判级 / 无法拆出链接 / 等级存疑）
  ❌ 不回写 timetable.json

用法：
  python split_source_fields_v2.py
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
THIRD_PARTY_MARK = ["公开汇总", "中公", "超级简历", "牛企", "牛客"]
STRONG_MARK = ["官方", "就业网", "官网"]
# ⚠️ 否定语境防护：source 里写「官网佐证未找到」「未见官方入口」是**否定**强源，不是强源
NEG_MARK = ["佐证未找到", "未见官方", "未找到", "官网未", "未核到", "无官方"]

# ── 裁定后的映射 ──
LEVEL = {
    "官网原文": "A",
    "企业招聘系统": "A",
    "官网已核验-今日截止": "A",
    "就业网转发": "B",
    "第三方汇总": "C",
    "待核实": "C",
    "确认滚动": "⚪",          # 第四档，不参与 A/B/C
}
LEVEL_LABEL = {
    "A": "A 企业自己写的",
    "B": "B 二手或我们核过",
    "C": "C 第三方未核",
    "⚪": "⚪ 滚动·无固定截止（不参与 A/B/C）",
}

COLUMNS = ["序号", "企业名称", "网申截止日期", "剩余天数", "核实状态",
           "原source", "source_url", "source_level", "date_form", "拆分说明"]

UNSPLIT_COLUMNS = ["类别", "序号", "企业名称", "核实状态", "原source", "date_form", "拆不出来的原因"]


def pick_url(src):
    m = URL_RE.search(src or "")
    return m.group(0).rstrip("。，,；;") if m else ""


def pick_date_form(c):
    dl = (c.get("deadline") or "").strip()
    left = c.get("days_left")
    if isinstance(left, int) and not isinstance(left, bool):
        return "硬日期"
    if dl == "招满即止":
        return "滚动无固定截止"
    return "有日期待核实"        # 裁定：原名「待公布」→「有日期待核实」


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
        lv = LEVEL.get(st, "C")           # 未收录一律按最弱档
        df = pick_date_form(c)

        notes = []
        if not url:
            notes.append("source 内无 http 链接 → source_url 留空（未见来源链接）")
            unsplit.append(["① 拆不出来源链接", c.get("no", ""), c.get("company", ""), st, src, df,
                            "source 字段里没有 http 链接，无法拆出 source_url"])
        if lv == "⚪":
            notes.append("⚠️ 归入第四档 ⚪；三字段不一致：状态=确认滚动 / source=第三方汇总字样 / note 称官网，需回查采集记录")
            unsplit.append(["③ 等级存疑·需回查", c.get("no", ""), c.get("company", ""), st, src, df,
                            "verify_status 与 source 字样、note 三处说法不一致，本轮无法确认真实来源等级"])
        elif (st in ("第三方汇总", "待核实")
              and any(m in src for m in STRONG_MARK)
              and not any(m in src for m in NEG_MARK)):
            notes.append("⚠️ 状态为弱档但 source 字样含「官方/就业网」，等级存疑")
            unsplit.append(["③ 等级存疑·需回查", c.get("no", ""), c.get("company", ""), st, src, df,
                            "verify_status 判为弱档，但 source 字样指向强源，两者矛盾"])
        if df == "有日期待核实" and c.get("note"):
            notes.append("note 内有日期线索但未采信，未折算为硬日期")

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
            w = csv.DictWriter(f, fieldnames=cols) if isinstance(rs[0], dict) else csv.writer(f)
            if isinstance(rs[0], dict):
                w.writeheader()
                w.writerows(rs)
            else:
                w.writerow(cols)
                w.writerows(rs)
        with open(path, "rb") as f:
            raw = f.read(3)
        assert raw[:3] != b"\xef\xbb\xbf", "❌ CSV 出现 BOM：%s" % path

    lv = Counter(r["source_level"] for r in out_rows)
    df = Counter(r["date_form"] for r in out_rows)
    cat = Counter(u[0] for u in unsplit)
    url_n = sum(1 for r in out_rows if r["source_url"])

    print("=== 完整表 ===")
    print("总行数：%d" % len(out_rows))
    print("source_level：%s" % "　｜　".join(
        "%s %d" % (LEVEL_LABEL[k][:1], v) for k, v in sorted(lv.items())))
    print("  明细：%s" % " / ".join("%s=%d" % (k, lv[k]) for k in ["A", "B", "C", "⚪"] if lv.get(k)))
    print("  A+B+C（不含⚪）= %d" % (lv["A"] + lv["B"] + lv["C"]))
    print("date_form：硬日期=%d　滚动无固定截止=%d　有日期待核实=%d" % (
        df["硬日期"], df["滚动无固定截止"], df["有日期待核实"]))
    print("含 source_url：%d / %d = %.0f%%" % (url_n, len(out_rows), url_n / len(out_rows) * 100))
    print()
    print("=== 拆不出来清单 ===")
    for k, v in sorted(cat.items()):
        print("  %s：%d 条" % (k, v))
    print("  合计：%d 条（含重复计数：同一条可能既无链接又等级存疑）" % len(unsplit))
    print()
    print("输出：%s" % p_main)
    print("输出：%s" % p_un)
    print()
    print("⚠️ timetable.json 未改动")


if __name__ == "__main__":
    main()
