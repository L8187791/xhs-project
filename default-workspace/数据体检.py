# -*- coding: utf-8 -*-
"""数据体检 —— 全面检查 timetable.json 的质量问题
   不看单一字段，逐项列出所有可修的质量缺口
"""
import io, os, re, sys, json, datetime
from collections import Counter, defaultdict
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
D = os.path.join(WS, "技能包_时间表查询官", "data", "timetable.json")
d = json.load(io.open(D, encoding="utf-8"))
cos = d["companies"]
T = datetime.date(2026, 10, 10)
N = len(cos)

print("=" * 88)
print("数据体检 · timetable.json %s ｜ %d 家" % (d["meta"]["version"], N))
print("=" * 88)

# ---------- ① 字段完整率 ----------
print()
print("① 字段完整率（空值 = 空串 / None / 缺字段）")
fields = Counter()
for c in cos:
    for k in c:
        fields[k] += 1
allkeys = sorted(set(k for c in cos for k in c))
bad = []
for k in allkeys:
    if k in ("no", "company"):
        continue
    empty = sum(1 for c in cos if not c.get(k) and c.get(k) != 0)
    pct = 100.0 * (N - empty) / N
    mark = "🔴" if pct < 60 else ("🟡" if pct < 95 else "✅")
    if pct < 95:
        bad.append((k, empty, pct))
        print("  %s %-22s 完整 %5.1f%%（空 %d）" % (mark, k, pct, empty))
print("  → 需关注字段 %d 个" % len(bad))

# ---------- ② 行业待分类 ----------
print()
print("② 行业分类")
ind = Counter(c.get("industry") or "(空)" for c in cos)
for k, v in ind.most_common():
    print("  %-16s %3d %s" % (k, v, "🔴 待分类" if "待分类" in k or k == "(空)" else ""))
todo = [c for c in cos if "待分类" in (c.get("industry") or "") or not c.get("industry")]
print("  → 待分类 %d 家: %s" % (len(todo), "、".join(c["company"][:12] for c in todo[:8])))

# ---------- ③ 投递入口缺失 ----------
print()
print("③ 投递入口（apply_url）")
no_url = [c for c in cos if not c.get("apply_url")]
print("  有链接 %d ｜ 无链接 %d（%.1f%% 缺失）" % (N - len(no_url), len(no_url), 100.0 * len(no_url) / N))
src_url = sum(1 for c in cos if isinstance(c.get("source_url"), str) and c["source_url"].startswith("http"))
print("  source_url 有 http 链接: %d（%.1f%%）" % (src_url, 100.0 * src_url / N))

# ---------- ④ 日期自洽 ----------
print()
print("④ 日期与剩余天数自洽")
mis = []
for c in cos:
    dl = c.get("deadline") or ""
    if re.match(r"^\d{4}-\d{2}-\d{2}$", dl):
        try:
            n = (datetime.date.fromisoformat(dl) - T).days
        except Exception:
            mis.append((c["company"], dl, "日期非法")); continue
        if c.get("days_left") != n:
            mis.append((c["company"], dl, "days_left=%s 应为 %d" % (c.get("days_left"), n)))
print("  mismatch: %d %s" % (len(mis), "✅" if not mis else ""))
for x in mis[:6]:
    print("     %-16s %s  %s" % x)

# ---------- ⑤ 两轴自洽 ----------
print()
print("⑤ 两轴自洽")
prob = []
for c in cos:
    sl, df = c.get("source_level"), c.get("date_form")
    if sl == "⚪" and df != "rolling":
        prob.append((c["company"], "⚪ 但 date_form=%s" % df))
    if df == "hard" and not re.match(r"^\d{4}-\d{2}-\d{2}$", c.get("deadline") or ""):
        prob.append((c["company"], "hard 但 deadline=%r" % c.get("deadline")))
    if df == "to_verify" and not (c.get("note") or ""):
        prob.append((c["company"], "to_verify 但无 note 说明"))
print("  问题 %d %s" % (len(prob), "✅" if not prob else ""))
for x in prob[:6]:
    print("     %-16s %s" % x)

# ---------- ⑥ 重复 / 命名 ----------
print()
print("⑥ 重复与命名规范（守则第 23 条：二级单位写「集团·单位」）")
names = Counter(c["company"] for c in cos)
dup = {k: v for k, v in names.items() if v > 1}
print("  重名: %d %s" % (len(dup), dup if dup else "✅"))
sec = [c["company"] for c in cos if re.search(r"[（(]", c["company"]) and "·" not in c["company"]]
print("  疑似二级单位未按「集团·单位」: %d" % len(sec))
for s in sec[:8]:
    print("     %s" % s)

# ---------- ⑦ 已截止标注 ----------
print()
print("⑦ 已截止项")
exp = [c for c in cos if isinstance(c.get("days_left"), int) and c["days_left"] < 0]
print("  已截止 %d 家" % len(exp))
noverify = [c["company"] for c in exp if "已截止" not in (c.get("note") or "")]
print("  note 未标「已截止」: %d %s" % (noverify.count("") if False else len(noverify), "✅" if not noverify else noverify[:6]))

# ---------- ⑧ 补充池去重 ----------
print()
print("⑧ 补充池 / 主表是否有重叠")
pool = os.path.join(WS, "_扩充", "补充池_有入口无日期.md")
if os.path.exists(pool):
    t = io.open(pool, encoding="utf-8").read()
    main = set(c["company"] for c in cos)
    hit = []
    for line in t.split("\n"):
        m = re.match(r"^\|\s*\d+\s*\|\s*([^|]+?)\s*\|", line)
        if m:
            nm = m.group(1).strip()
            # 模糊匹配
            for mc in main:
                if nm and (nm in mc or mc in nm) and nm != mc:
                    hit.append((nm, mc))
    print("  疑似重叠: %d" % len(hit))
    for a, b in hit[:6]:
        print("     池「%s」 ↔ 主表「%s」" % (a, b))
else:
    print("  补充池文件不存在")

print()
print("=" * 88)
print("体检结论")
print("=" * 88)
print("  🔴 最该修: %s" % (
    "、".join([x[0] for x in bad[:4]]) if bad else "无"))
print("  待分类 %d 家 ｜ 无入口链接 %d 家 ｜ 日期不一致 %d ｜ 两轴问题 %d" % (
    len(todo), len(no_url), len(mis), len(prob)))
