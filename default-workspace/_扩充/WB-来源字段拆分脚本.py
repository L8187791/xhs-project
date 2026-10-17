# -*- coding: utf-8 -*-
"""T2 两轴字段拆分 · 预览脚本（落地卡 25 · 任务 C）

把 timetable.json 的 `source` 一个字符串拆成：
  - source_url   : 从 source 里抽出的 http(s) 链接（抽不到留空）
  - source_level : A 企业自己写的 / B 二手或我们核过 / C 第三方未核
  - date_form    : 硬日期 / 滚动无固定截止 / 待公布

⚠️ 本脚本只输出预览 CSV，**不修改 timetable.json**（等主运营拍板）。

用法：
  python split_source_fields.py [--data 路径] [--out CSV路径]
"""
import argparse
import csv
import datetime
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

# verify_status → 来源等级（机械映射，不带主观判断）
LEVEL_BY_STATUS = {
    "官网原文": "A",
    "企业招聘系统": "A",
    "官网已核验-今日截止": "A",
    "就业网转发": "B",
    "确认滚动": "B",
    "第三方汇总": "C",
    "待核实": "C",
}
# source 字段里出现这些字样 → 判为第三方汇总（用于交叉校验）
THIRD_PARTY_MARK = ["公开汇总", "中公", "超级简历", "牛企", "牛客"]

COLUMNS = [
    "序号", "企业名称", "网申截止日期", "剩余天数",
    "核实状态", "原source", "source_url", "source_level", "date_form", "拆分说明",
]


def pick_url(src):
    m = URL_RE.search(src or "")
    return m.group(0).rstrip("。，,；;") if m else ""


def pick_level(c):
    st = c.get("verify_status", "")
    lv = LEVEL_BY_STATUS.get(st)
    if lv:
        note = "按 verify_status 判"
    else:
        lv, note = "C", "verify_status 未收录，按最弱档处理"
    return lv, note


def pick_date_form(c):
    dl = (c.get("deadline") or "").strip()
    left = c.get("days_left")
    if isinstance(left, int) and not isinstance(left, bool):
        return "硬日期"
    if dl == "招满即止":
        return "滚动无固定截止"
    return "待公布"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--out", default=os.path.join(WS, "_扩充", "WB-timetable-来源字段拆分预览-2026-10-10.csv"))
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    rows = data["companies"]

    out_rows = []
    unsplittable = []
    for c in rows:
        src = str(c.get("source", "") or "")
        url = pick_url(src)
        lv, lv_note = pick_level(c)
        df = pick_date_form(c)

        notes = []
        if not url:
            notes.append("source 内无 http 链接 → source_url 留空（未见来源链接）")
        if not lv_note.startswith("按"):
            notes.append(lv_note)
        # 交叉校验：状态与来源字样打架的，单独标出
        st = c.get("verify_status", "")
        if st == "确认滚动" and any(m in src for m in THIRD_PARTY_MARK):
            notes.append("⚠️ 状态写「确认滚动」但 source 为第三方汇总字样，两字段矛盾，等级待裁定")
            unsplittable.append((c["no"], c["company"], "确认滚动 vs 公开汇总 矛盾"))
        if st in ("待核实", "第三方汇总") and any(m in src for m in ["官方", "就业网"]):
            notes.append("⚠️ 状态为弱档但 source 字样含「官方/就业网」，等级待裁定")
            unsplittable.append((c["no"], c["company"], "状态弱档 vs source 强字样"))
        if df == "待公布" and c.get("note"):
            notes.append("note 里有日期线索但未采信为硬日期，未折算")

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

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out_rows)
    with open(args.out, "rb") as f:
        raw = f.read(3)
    assert raw[:3] != b"\xef\xbb\xbf", "❌ CSV 出现 BOM"

    lv_cnt = Counter(r["source_level"] for r in out_rows)
    df_cnt = Counter(r["date_form"] for r in out_rows)
    url_cnt = sum(1 for r in out_rows if r["source_url"])

    print("总数：%d" % len(out_rows))
    print("source_level：A=%d  B=%d  C=%d" % (lv_cnt["A"], lv_cnt["B"], lv_cnt["C"]))
    print("date_form：硬日期=%d  滚动无固定截止=%d  待公布=%d" % (
        df_cnt["硬日期"], df_cnt["滚动无固定截止"], df_cnt["待公布"]))
    print("含 source_url：%d 条；留空：%d 条" % (url_cnt, len(out_rows) - url_cnt))
    print("等级存疑（需裁定）：%d 条" % len(unsplittable))
    for no, name, why in unsplittable:
        print("   - #%s %s ：%s" % (no, name, why))
    print("输出：%s" % args.out)


if __name__ == "__main__":
    main()
