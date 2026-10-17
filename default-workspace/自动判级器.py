# -*- coding: utf-8 -*-
"""自动判级器 v1.0 —— 「裁定经验」的蒸馏产物
   输入：WorkBuddy 采集的 CSV（列名容错）
   输出：两轴分级（source_level / date_form）+ 可疑项清单（需人工复核）

   蒸馏来源：2026-10-10 手动判 131 家的经验 + 当天所有踩坑规则
   规则出处（守则）：
     第 19 条 区间日期取结束日
     第 23 条 二级单位写「集团·单位」
     第 24 条 三源冲突先查官方有没有
     第 25 条 核实状态七级
     第 27 条 三档等级 + 「确认滚动」单开 ⚪
     第 32 条 否定句防护（官网佐证未找到 ≠ 有佐证）
     第 39 条 to_verify 的判据（要有「疑似截止日」才可去核）
"""
import io, os, re, sys, csv, json, datetime
from collections import Counter
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"

# ============================================================
# 规则表（蒸馏的核心：今天判过的每一类都在这）
# ============================================================

# ---- 守则 32：否定语境（出现即【不得】判强源）----
NEGATION = re.compile(r"(未找到|未见|未核到|无官方|佐证未找到|找不到|未查到|未披露|未注明|没有设置|未写明)")

# ---- A 档信号：企业自己发布的 ----
A_SIGNALS = [
    re.compile(r"公告原文"), re.compile(r"官网原文"), re.compile(r"官网公告"),
    re.compile(r"官方公告"), re.compile(r"官网.{0,6}发布"), re.compile(r"官网 FAQ", re.I),
    re.compile(r"企业官网"),
]
# ---- A 档入口域名（企业自有域名词根）----
A_DOMAIN_HINT = re.compile(r"(\.com\.cn|\.cn/|zhiye\.com|hotjob\.cn|zhaopin\.[a-z0-9\-]+\.com|mokahr|career\.|campus\.)",
                           re.I)
# ---- B 档信号：官方转载 ----
B_SIGNALS = [
    re.compile(r"就业网"), re.compile(r"就业信息网"), re.compile(r"大学就业"),
    re.compile(r"高校就业"), re.compile(r"就业平台"), re.compile(r"24365"),
    re.compile(r"官方简章转发"), re.compile(r"转载官方"),
]
# ---- C 档信号：第三方 ----
C_SIGNALS = [
    re.compile(r"中公"), re.compile(r"牛企"), re.compile(r"超级简历"), re.compile(r"今日头条"),
    re.compile(r"粉笔"), re.compile(r"校招星球"), re.compile(r"猎聘"), re.compile(r"北极星"),
    re.compile(r"汇总表"), re.compile(r"汇总页"), re.compile(r"公考"), re.compile(r"华图"),
    re.compile(r"高顿"), re.compile(r"秒入职"), re.compile(r"应届生求职网"), re.compile(r"offcn", re.I),
]
# ---- 确认滚动（守则 27：单开 ⚪，不进可信度轴）----
ROLLING = re.compile(r"(招满即止|招满为止|招满截止|无固定截止|没有设置统一|滚动招聘)")

# ---- 守则 39：这些日期不是「截止日」，不能作 to_verify 依据 ----
NOT_DEADLINE = re.compile(r"(发布|宣讲|上线|开放|开始|启动|开班|招聘会)")

ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
ANY_DATE = re.compile(r"(20\d{2})\s*[年\-/]\s*(\d{1,2})\s*[月\-/]\s*(\d{1,2})|(\d{1,2})\s*月\s*(\d{1,2})\s*日")
RANGE = re.compile(r"[~\-–—至到]")

def parse_deadline(raw):
    """返回 (iso_date_or_None, 说明)"""
    if not raw:
        return None, "空"
    s = raw.strip()
    if ROLLING.search(s):
        return None, "滚动"
    # ★ 守则 39：原文自述「待核实 / 未写 / 未注明」→ 那个日期不可采信，转 to_verify
    if NEGATION.search(s) or re.search(r"待核实|各岗位.{0,6}不一致", s):
        return None, "日期存疑（原文自述待核实/未写）"
    # ★ 守则 39：出现在「发布/宣讲/上线/开放」旁边的日期**不是截止日**
    if re.match(r"^\s*20\d{2}[-/年]\d{1,2}[-/月]\d{1,2}.*?(发布|宣讲|上线|开放)", s) or \
       re.search(r"(发布|宣讲|上线|开放)日?期?[:：]?\s*20\d{2}", s):
        return None, "日期是发布/宣讲日，非截止日（守则39）"
    # 区间 → 取结束日（守则 19）
    dates = list(ANY_DATE.finditer(s))
    if not dates:
        return None, "无日期"
    if RANGE.search(s) and len(dates) >= 2:
        g = dates[-1].groups()
        y = int(g[0]) if g[0] else 2026
        mo, d = (int(g[1]), int(g[2])) if g[0] else (int(g[3]), int(g[4]))
        try:
            return datetime.date(y, mo, d).isoformat(), "区间取结束日"
        except Exception:
            return None, "区间解析失败"
    g = dates[0].groups()
    y = int(g[0]) if g[0] else 2026
    mo, d = (int(g[1]), int(g[2])) if g[0] else (int(g[3]), int(g[4]))
    try:
        return datetime.date(y, mo, d).isoformat(), "单日期"
    except Exception:
        return None, "日期非法"

ENTRY_COLS = ("投递入口", "官方入口依据", "官方入口", "依据原文", "入口")
URLC_COLS = ("来源URL", "来源", "来源链接")   # ★ 这是「我们从哪采集的」，不是投递入口

def judge_source_level(row):
    """返回 (level, 中文, 理由, 是否需要人工复核)
       ★ 关键：只看【投递入口 / 官方入口依据】，**不看来源URL** ——
         来源URL 指向中公/牛企是「采集渠道」，不代表企业入口是第三方的。"""
    ent = " ".join(str(row.get(k, "")) for k in ENTRY_COLS if k in row)
    text = ent if ent.strip() else " ".join(str(v) for v in row.values() if v)
    if ROLLING.search(text) and not NEGATION.search(text):
        pass  # 滚动不决定 source_level（它是 date_form 的事）
    hits = {"A": 0, "B": 0, "C": 0}
    why = []
    for p in A_SIGNALS:
        if p.search(text):
            hits["A"] += 1; why.append("A:" + p.pattern[:12])
    if A_DOMAIN_HINT.search(text):
        hits["A"] += 1; why.append("A:自有域名")
    for p in B_SIGNALS:
        if p.search(text):
            hits["B"] += 1; why.append("B:" + p.pattern[:12])
    for p in C_SIGNALS:
        if p.search(text):
            hits["C"] += 1; why.append("C:" + p.pattern[:12])

    review = False
    # ★ 守则 32：否定语境 → 不得判 A/B
    if NEGATION.search(text) and (hits["A"] or hits["B"]):
        neg = NEGATION.search(text).group(1)
        why.append("⚠️ 否定语境「%s」→ 强源降级" % neg)
        if hits["A"]:
            hits["A"] = 0; review = True
        if hits["B"] and not hits["A"]:
            hits["B"] = 0
    # C 与 A 同时出现 → 存疑
    # ★ 关键修正：若文本是「转发/转载 + 官方公告」，A 信号来自 B 的**转述对象** → 判 B
    if hits["B"] and re.search(r"(转发|转载|转自|同载|转录)", text):
        why.append("⚠️ A 信号来自转发文本的转述对象 → 降为 B")
        hits["A"] = 0
    if hits["A"] and hits["C"]:
        review = True
        why.append("⚠️ A 与 C 信号并存 → 需人工确认")
    if hits["A"]:
        return "A", "企业自己写的", "；".join(why), review
    if hits["B"]:
        return "B", "二手或我们核过", "；".join(why), review
    if hits["C"]:
        return "C", "第三方未核", "；".join(why), review
    return "C", "第三方未核", "⚠️ 无任何来源信号 → 默认 C（最保守）", True

def judge_date_form(row, dl, dl_note):
    """返回 (form, 中文, 理由, 需要复核)"""
    text = " ".join(str(v) for v in row.values() if v)
    if dl:
        return "hard", "硬日期", dl_note, False
    if ROLLING.search(text):
        return "rolling", "滚动·无固定截止", "原文含招满即止/无固定截止", False
    # 守则 39：要有「疑似截止日」才能进 to_verify
    dates = list(ANY_DATE.finditer(text))
    if dates:
        # 逐个看那个日期附近是不是「发布/宣讲」这类非截止语义
        ok = False
        for m in dates:
            ctx = text[max(0, m.start() - 12):m.end() + 12]
            if not NOT_DEADLINE.search(ctx):
                ok = True; break
        if ok:
            return "to_verify", "有日期待核实", "有疑似截止日 + 存在核验缺口", True
        return "none", "未列明日期", "⚠️ 出现的日期是「发布/宣讲」类，非截止日（守则39）", False
    return "none", "未列明日期", "全文无日期线索", False

def load_rows(path):
    txt = io.open(path, encoding="utf-8-sig").read()
    return list(csv.DictReader(io.StringIO(txt)))

def run(path, out_csv=None):
    rows = load_rows(path)
    print("=" * 92)
    print("判级: %s（%d 行）" % (os.path.basename(path), len(rows)))
    print("=" * 92)
    out, review = [], []
    for i, r in enumerate(rows, 1):
        name = (r.get("企业名称") or r.get("合并写法") or r.get("二级单位名") or r.get("集团名") or "?")
        raw = (r.get("网申截止日期") or r.get("截止日期") or r.get("截止日期原文") or "")
        dl, dl_note = parse_deadline(raw)
        lv, lv_cn, lv_why, rev1 = judge_source_level(r)
        df, df_cn, df_why, rev2 = judge_date_form(r, dl, dl_note)
        rec = {"企业名称": name, "截止日期": dl or "", "source_level": lv, "source_level_cn": lv_cn,
               "date_form": df, "date_form_cn": df_cn,
               "判级理由": (lv_why + " ｜ " + df_why)[:150], "需人工复核": "是" if (rev1 or rev2) else ""}
        out.append(rec)
        if rec["需人工复核"]:
            review.append(rec)
    print("  source_level:", dict(Counter(x["source_level"] for x in out)))
    print("  date_form  :", dict(Counter(x["date_form"] for x in out)))
    print("  ⚠️ 需人工复核: %d 条" % len(review))
    for x in review[:12]:
        print("     %-26s %s/%s  %s" % (x["企业名称"][:26], x["source_level"], x["date_form"], x["判级理由"][:70]))
    if out_csv:
        io.open(out_csv, "w", encoding="utf-8").write(
            "\ufeff" if False else "")
        with open(out_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader(); w.writerows(out)
        print("  → %s" % out_csv)
    return out, review

if __name__ == "__main__":
    EXT = os.path.join(WS, "_扩充")
    targets = [f for f in os.listdir(EXT) if f.endswith(".csv") and "新增企业" in f
               and not f.startswith("判级结果")] if os.path.isdir(EXT) else []
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    for t in targets:
        p = t if os.path.isabs(t) else os.path.join(EXT, t)
        if os.path.exists(p):
            run(p, os.path.join(EXT, "判级结果_%s" % os.path.basename(p)))
            print()
