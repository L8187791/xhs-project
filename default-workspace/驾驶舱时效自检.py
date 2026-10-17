# -*- coding: utf-8 -*-
"""
驾驶舱时效自检 · L 的工作台.html
用法：python 驾驶舱时效自检.py  [--path <html路径>]
职责：把驾驶舱里所有「当前状态」字段与权威源 / 当日日期逐项对账，任一项不符即 ❌ 并给出应改值。
依据：L 2026-10-17 指令「每天实时更新这个工作台，不要出现漏的事情」（医美侧除外）。
纪律：本脚本只读不写；❌ 项须回盘修正后重跑，全 ✅ 才算驾驶舱已刷新。
"""
import argparse
import datetime
import json
import os
import re
import sys

WS = os.path.dirname(os.path.abspath(__file__))
TB_DEFAULT = os.path.join(WS, "技能包_时间表查询官", "data", "timetable.json")
HTML_DEFAULT = os.path.join(WS, "_协作", "_驾驶舱复刻", "L 的工作台.html")

OK, BAD = "✅", "❌"
results = []


def chk(name, got, want, note=""):
    good = str(got) == str(want)
    results.append((good, name, got, want, note))
    print("  %s %-26s 现值=%-22s 应为=%-22s %s" % (
        OK if good else BAD, name, got, want, note))
    return good


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=HTML_DEFAULT)
    ap.add_argument("--tb", default=TB_DEFAULT)
    ap.add_argument("--date", default=None, help="对账基准日 YYYY-MM-DD，默认今天")
    a = ap.parse_args()

    T = (datetime.date.fromisoformat(a.date) if a.date else datetime.date.today())
    print("=" * 78)
    print("驾驶舱时效自检 · 基准日 %s · %s" % (T.isoformat(), a.path))
    print("=" * 78)

    if not os.path.exists(a.path):
        print("%s 找不到驾驶舱：%s" % (BAD, a.path))
        return 1
    b = open(a.path, "rb").read()
    s = b.decode("utf-8")
    crlf = sum(1 for l in b.split(b"\n")[:-1] if l.endswith(b"\r"))
    pure = b.count(b"\n") - crlf

    tb = json.load(open(a.tb, encoding="utf-8"))
    ver = tb["meta"]["version"]
    cs = tb["companies"]

    def dl(c):
        try:
            return datetime.date.fromisoformat(c["deadline"])
        except Exception:
            return None

    def cnt(days):
        return len([c for c in cs if dl(c) and 0 <= (dl(c) - T).days <= days])

    n_today = len([c for c in cs if dl(c) == T])
    n_tmr = len([c for c in cs if dl(c) == T + datetime.timedelta(days=1)])
    n_d3 = cnt(3)
    n_d7 = cnt(7)
    n_d21 = cnt(21)
    n_d30 = cnt(30)
    hard = [c for c in cs if dl(c)]
    n_exp = len([c for c in hard if dl(c) < T])
    n_noday = len(cs) - len(hard)

    print("\n【A · 行尾与结构】")
    chk("行尾 纯LF", pure, 0, "须为 0（CRLF 统一）")
    chk("html 闭合", "%d/%d" % (s.count("<html"), s.count("</html>")), "1/1")
    chk("body 闭合", "%d/%d" % (s.count("<body"), s.count("</body>")), "1/1")
    chk("script 闭合", "%d/%d" % (s.count("<script"), s.count("</script>")), "1/1")
    chk("table 配对", "%d/%d" % (s.count("<table"), s.count("</table>")),
        "%d/%d" % (s.count("<table"), s.count("<table")))

    print("\n【B · 日期与权威源版本】")
    m = re.search(r"数据快照 <b>(\d{4}-\d{2}-\d{2})</b>", s)
    chk("侧栏 数据快照", m.group(1) if m else "未找到", T.isoformat())
    m = re.search(r'<span class="pill">数据快照 (\d{4}-\d{2}-\d{2})</span>', s)
    chk("顶栏 pill 快照", m.group(1) if m else "未找到", T.isoformat())
    m = re.search(r"权威源 (v[\d.]+)（updated", s)
    chk("侧栏 权威源版本", m.group(1) if m else "未找到", ver)
    # 版本号：只在「现行口径」HTML 行里查（排除卡片索引的 JS 数组行，那些是历史留痕）
    live = "\n".join(l for l in s.split("\n") if not l.lstrip().startswith("["))
    n_ver = live.count(ver)
    results.append((n_ver >= 3, "%s 出现处数(≥3)" % ver, n_ver, "≥3", "侧栏/数据池/主表KPI/明细标题"))
    print("  %s %-26s 现值=%-22s 应为=%-22s %s" % (
        OK if n_ver >= 3 else BAD, "%s 出现处数(≥3)" % ver, n_ver, "≥3", "侧栏/数据池/主表KPI/明细标题"))
    old = sorted(set(v for v in re.findall(r"v1\.0\.\d+", live) if v != ver))
    chk("残留旧版本号(现行区)", (",".join(old) if old else "无"), "无", "历史卡片行不计")

    print("\n【C · 主表 KPI】")
    m = re.search(r"今日截止 (\d+) 家 · 明日 (\d+) 家 · 7 天内 (\d+) 家", s)
    if m:
        chk("总览 今日截止", m.group(1), n_today)
        chk("总览 明日截止", m.group(2), n_tmr)
        chk("总览 7 天内", m.group(3), n_d7)
    else:
        chk("总览 KPI 行", "未找到", "已匹配")
    m = re.search(r"今天 / 明天截止</div><div class=\"vl\">(\d+)<small>/ (\d+)</small>", s)
    if m:
        chk("主表 今天/明天", "%s/%s" % (m.group(1), m.group(2)), "%d/%d" % (n_today, n_tmr))
    else:
        chk("主表 今天/明天", "未找到", "已匹配")

    print("\n【D · 截止日水位】")
    for label, want in (("今天 / 明天", n_today + n_tmr), ("3 天内", n_d3),
                        ("7 天内", n_d7), ("21 天内", n_d21), ("30 天内", n_d30)):
        m = re.search(re.escape('<span class="n">%s</span>' % label) + r'.*?<span class="v">(\d+) 家</span>', s)
        chk("水位 %s" % label, m.group(1) if m else "未找到", want)
    m = re.search(r"已过期（可比较 \d+ 行内）</span>.*?<span class=\"v\">(\d+) 家</span>", s)
    chk("水位 已过期", m.group(1) if m else "未找到", n_exp)

    print("\n【E · 200 家明细 · chips 与 ROWS】")
    for f, want in (("soon", n_d3), ("week", n_d7), ("expired", n_exp), ("noday", n_noday)):
        m = re.search(r'data-f="%s">[^<]*?(\d+)</span>' % f, s)
        chk("chip %s" % f, m.group(1) if m else "未找到", want)
    m = re.search(r"全部 (\d+)</span>", s)
    chk("chip all", m.group(1) if m else "未找到", len(cs))

    lm = re.search(r"^const ROWS = (\[\[.*\]\]);?\s*$", s, re.M)
    if lm:
        rows = json.loads(lm.group(1))
        chk("ROWS 行数", len(rows), len(cs))
        mis = []
        for r in rows:
            try:
                d = datetime.date.fromisoformat(str(r[4]))
            except Exception:
                if r[5] is not None:
                    mis.append((r[0], r[4], r[5], "null"))
                continue
            want = (d - T).days
            if r[5] != want:
                mis.append((r[0], r[4], r[5], want))
        chk("ROWS 剩余天数 错行数", len(mis), 0, ("例：" + str(mis[:3])) if mis else "")
    else:
        chk("ROWS 数组", "未找到", "已匹配")

    print("\n【F · 今日三层发布 详情三卡片】")
    for tag in ("A 层 · 09:00", "B 层 · 12:30", "C 层 · 20:30"):
        chk("卡片存在 %s" % tag, tag in s, True)
    md = "%d/%d" % (T.month, T.day)
    chk("卡片含当日 %s" % md, md in s, True, "已发/稿就绪标记")

    print("\n【G · 排期表 / 事件页 / 页脚】")
    chk("排期表含 T+0 · %s" % md, ("T+0 · %s" % md) in s, True)
    m = re.search(r"今日新发事件采集（(WB\d+) · (\d{2}-\d{2}) 已跑完）", s)
    if m:
        chk("事件页 采集日", m.group(2), "%02d-%02d" % (T.month, T.day))
        print("     ℹ️ 事件页 WB 号＝%s（信息项，须与当日 07:00 采集卡号一致）" % m.group(1))
    else:
        chk("事件页 标题", "未找到", "已匹配")
    m = re.search(r"生成于 (\d{4}-\d{2}-\d{2}) by W", s)
    chk("页脚 生成日期", m.group(1) if m else "未找到", T.isoformat())

    print("\n" + "=" * 78)
    bad_n = sum(1 for r in results if not r[0])
    if bad_n == 0:
        print("%s 全部 %d 项通过 —— 驾驶舱已按 %s 刷新，无漏项" % (OK, len(results), T.isoformat()))
    else:
        print("%s %d/%d 项不符 —— 驾驶舱未刷新到位，须回盘修正后重跑：" % (BAD, bad_n, len(results)))
        for good, name, got, want, note in results:
            if not good:
                print("    · %s：现值 %s → 应为 %s" % (name, got, want))
    print("（医美侧不在本自检范围 · L 通知后才动）")
    print("=" * 78)
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())