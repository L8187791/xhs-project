# -*- coding: utf-8 -*-
"""发文检查器 —— 蒸馏产物 #3
   把用户 2026-10-10 的三条建议做成可执行检查：
     ① 人设一致性（简介蒸馏：踩过坑的过来人，不是专家/学姐/HR）
     ② 时间节点建议（含样本不足的诚实标注）
     ③ 标题打分（复用标题打分器）
   用法：
     python 发文检查器.py                       # 跑内置的明日候选
     python 发文检查器.py "标题1" "标题2" ...
"""
import io, os, re, sys, datetime, importlib.util
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
spec = importlib.util.spec_from_file_location("sc", os.path.join(WS, "标题打分器.py"))
SC = importlib.util.module_from_spec(spec); spec.loader.exec_module(SC)

# ============================================================
# ① 人设规则（从简介蒸馏）
#    「普通打工人，自己找工作时被信息差坑过。整理…」= 过来人，不是专家
# ============================================================
PERSONA_FORBID = [
    # ★ 只在「自称」模式里判（「面试官问你…」里的面试官是叙述对象，不是自称）
    (r"(?:我是|我作为|作为|当个|我叫)[^，。！？]{0,4}(学姐|学长|前辈|老师|专家|内行|HR|面试官)",
     "❌ 自称不符人设（简介是「普通打工人」）"),
    (r"(教你|带你|保证|保姆级|手把手|包会)", "❌ 教学/承诺口吻（人设是「整理分享」，不是「教学」）"),
    (r"(必须|一定要|千万要|务必要)", "⚠️ 命令口吻（人设是过来人，不是权威）"),
    (r"(上岸|逆袭|翻身)", "⚠️ 结果导向词（不符合「整理资料」的克制）"),
]
PERSONA_PREFER = [
    (r"(我核过|我整理|我发现的|我自己|我踩过|我碰到过)", "✅ 过来人第一人称"),
    (r"(我整理的|我核对的|我逐条核)", "✅ 整理者视角"),
]
# 时效内容可以没有第一人称（信息本身就是身份证明）
INFO_LIKE = re.compile(r"(截止|汇总|一览|清单|时间表|网申)")

def check_persona(title, body=""):
    t = title + " " + body
    bad, good = [], []
    for p, why in PERSONA_FORBID:
        m = re.search(p, t)
        if m:
            bad.append("%s「%s」" % (why, m.group(1)))
    for p, why in PERSONA_PREFER:
        if re.search(p, t):
            good.append(why)
    if not good and INFO_LIKE.search(title):
        good.append("✅ 信息型内容（无需第一人称，信息本身即身份证明）")
    score = 100 - 30 * len(bad) + (10 if good else 0)
    return max(0, min(100, score)), good, bad

# ============================================================
# ② 时间节点
# ============================================================
SLOTS = {
    "上午 11:00-12:30": ("午休刷一轮", "中", "发短平快的信息型"),
    "下午 14:00-16:00": ("课间/自习", "中高", "⭐ 爆款时段（10-08 爆款发在 15:42）"),
    "傍晚 17:30-18:30": ("一天信息回补", "高", "发汇总型（收藏率高）"),
    "晚间 20:00-21:00": ("休闲", "高", "⚠️ 只发收藏型，不发时效型（今日 20:30 仅 26 观看）"),
    "深夜 22:00+":     ("睡前", "中", "⚠️ 最差（今日 22:30 仅 17 观看）"),
}
def time_advice(level):
    """level: 'A' 信息型 / 'B' 方法论"""
    if level == "A":
        return ["下午 14:00-16:00（爆款时段）", "傍晚 17:30-18:30", "上午 11:30-12:30（次选）"]
    return ["傍晚 17:30-18:30", "下午 14:00-16:00", "晚间 20:00-21:00（收藏型可）"]

# ============================================================
# ③ 综合检查
# ============================================================
def check(title, body="", level="A"):
    ts, tgood, tnotes = SC.score(title)
    ps, pgood, pbad = check_persona(title, body)
    return {"标题": title, "标题分": ts, "标题要点": tgood, "标题缺项": tnotes,
            "人设分": ps, "人设符合": pgood, "人设问题": pbad,
            "建议时段": time_advice(level), "层": level,
            "综合": int(ts * 0.6 + ps * 0.4)}

def show(r, idx=None):
    print()
    print("  %s【%d 分】%s" % ("%d. " % idx if idx else "", r["综合"], r["标题"]))
    print("      标题分 %d ｜ 人设分 %d ｜ 层 %s" % (r["标题分"], r["人设分"], r["层"]))
    for g in r["人设符合"]:
        print("      %s" % g)
    for b in r["人设问题"]:
        print("      %s" % b)
    for n in r["标题缺项"][:2]:
        print("      ⚠️ %s" % n)
    print("      🕐 建议时段：%s" % " / ".join(r["建议时段"]))

if __name__ == "__main__":
    print("=" * 90)
    print("发文检查器 · 人设 + 时间 + 标题打分")
    print("=" * 90)
    print()
    print("【人设基准】踩过坑的过来人，把自己整理的资料分享出来")
    print("            ✅ 我核过 / 我整理时发现 / 我自己踩过")
    print("            ❌ 学姐/老师/专家 · 教你/带你 · 必须/一定")
    print()
    print("【时间基准】主发 14:00–16:00（爆款时段）+ 17:30–18:30")
    print("            ⚠️ 样本仅 7 篇且集中同一天 —— 时段差异被内容差异盖住，别过度解读")

    args = sys.argv[1:]
    CANDS = []
    if args:
        CANDS = [(a, "", "A") for a in args]
    else:
        # 明日及后续候选（从内容燃料盘点来）
        CANDS = [
            ("未来7天｜9家网申截止汇总", "", "A"),
            ("未来30天｜12家银行网申截止汇总", "", "A"),
            ("央国企｜未来30天22家截止汇总", "", "A"),
            ("本周五关闸｜9家要截止", "", "A"),
            ("10月下旬截止：46家的日期在这", "", "A"),
            ("面试官问你还有什么想问的，我踩过的坑", "", "B"),
            ("简历上一段实习都没有，我是怎么写的", "", "B"),
        ]

    print()
    print("=" * 90)
    print("检查结果（按综合分排序）")
    print("=" * 90)
    rs = [check(t, b, l) for t, b, l in CANDS]
    for i, r in enumerate(sorted(rs, key=lambda x: -x["综合"]), 1):
        show(r, i)
    print()
    print("=" * 90)
    print("「几选几」建议")
    print("=" * 90)
    top = sorted(rs, key=lambda x: -x["综合"])
    a = [r for r in top if r["层"] == "A"]
    b = [r for r in top if r["层"] == "B"]
    print("  A 层（信息型，60%）：前 3 选 1–2 条")
    for r in a[:3]:
        print("     %d 分  %s  → %s" % (r["综合"], r["标题"], r["建议时段"][0]))
    print("  B 层（方法论，40%）：前 3 选 1 条")
    for r in b[:3]:
        print("     %d 分  %s" % (r["综合"], r["标题"]))
    print()
    print("  ⚠️ 同日同层只发 1 条（防同构）；A/B 混发，别连发同层")
