# -*- coding: utf-8 -*-
"""标题打分器 —— 「爆款公式」蒸馏的第一个产物
   输入：标题候选列表
   输出：0-100 分 + 缺什么 + 红线检查
   依据：① 7 篇实测拆解 ② 长尾词矩阵（217 条按赞加权） ③ compliance_gate 红线
"""
import io, os, re, sys, importlib.util
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
spec = importlib.util.spec_from_file_location("g", os.path.join(WS, "compliance_gate.py"))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)

# ---- 从长尾词矩阵实测来的句式权重（篇均赞）----
PATTERNS = [
    ("时间锚点+截止", r"(今天|今晚|明天|本周|这周|下旬|月中|月底|\d+月\d+日).{0,8}(截止|截)", 273.5),
    ("主题+汇总",     r"(汇总|一览|清单|大全|合集)", 265.1),
    ("具体日期+截止", r"\d{1,2}\s*月\s*\d{1,2}\s*日.{0,6}截止", 165.6),
    ("主题+版本化",   r"(更新|第\s*\d+\s*版|修订)", 39.7),
]
# ---- 爆款公式三要素（依据 7 篇实测：爆款 11,639 曝光 / 26.1% 点击率）----
def score(title):
    t = title.strip()
    s, notes, good = 0, [], []

    # ① 具体数字（爆款有「4 家」）
    if re.search(r"\d+\s*(家|个|条|所|批|种|类)", t):
        s += 25; good.append("具体数字")
    else:
        notes.append("缺「具体数字」（爆款：4 家）")

    # ② 时间锚点 + 截止（爆款有「今天截止」）
    m = re.search(r"(今天|今晚|明天|本周|这周|未来\s*\d+\s*天|\d+月\d+日|下旬|月底)", t)
    has_due = bool(re.search(r"(截止|截|关闸|要投|就到)", t))
    if m and has_due:
        s += 30; good.append("时间锚点+截止")
    elif m:
        s += 12; notes.append("有时间锚点但缺「截止/关闸」")
    elif has_due:
        s += 12; notes.append("有「截止」但缺时间锚点")
    else:
        notes.append("缺「时间锚点 + 截止」——这是爆款最强的那个组合")

    # ③ 可核验 / 汇总感（爆款有「附官网核验时间」）
    if re.search(r"(汇总|一览|清单|核验|核实|官网|附)", t):
        s += 20; good.append("可核验/汇总感")
    else:
        notes.append("缺「汇总 / 可核验」字样")

    # ④ 句式加权（长尾词矩阵）
    best = None
    for name, pat, w in PATTERNS:
        if re.search(pat, t):
            if best is None or w > best[2]:
                best = (name, pat, w)
    if best:
        s += 15; good.append("句式「%s」（篇均 %.1f 赞）" % (best[0], best[2]))
    else:
        notes.append("句式不落任何高加权档")

    # ⑤ 自宣传扣分（《时间表更新了》= 39 观看）
    if re.search(r"(更新了|我们|本文|本店|上新)", t):
        s -= 25; notes.append("🔴 含自我宣传语气（《时间表更新了》实测仅 39 观看）")

    # ⑥ 字数
    n = len(re.sub(r"\s+", "", t))
    if n > 20:
        s -= 10; notes.append("超 20 字（%d）" % n)
    elif n <= 14:
        s += 5; good.append("字数 %d 合适" % n)

    # ⑦ 红线（★ 只查词级：绝对化/诱饵/焦虑/商品；**不查结构风险**）
    #    理由：结构风险（时间压迫+截止）需配合正文的「核验日期」才判 5.5 豁免，
    #    标题单独扫必然误报 —— 今天爆款标题就被误判过一次。
    hits = [h for h in G.scan_text(t + "（核验日期 2026-10-10）", "title")
            if h[1] in ("绝对化用语", "诱饵引流", "商品引导", "焦虑贬损")]
    if hits:
        s -= 40
        notes.append("🔴 红线：" + "、".join("%s「%s」" % (h[1], h[2]) for h in hits))

    return max(0, min(100, s)), good, notes

if __name__ == "__main__":
    # ============ 自测：拿今天真实的 7 篇回测 ============
    REAL = [
        ("4 家银行网申今天截止（附官网核验时间）", 3102),
        ("时间表更新了，就在今天24点！", 39),
        ("网申截止别信二手消息｜3 个官方渠道，自己查", 14),
        ("简历上一段实习都没有，怎么写", 28),
        ("群面里容易出局的三种表现", 44),
        ("投了没回音，问题出在哪（按环节排查）", 26),
        ("央国企和互联网的简历，差别在哪", 17),
        ("未来7天｜9家网申截止汇总", None),          # 明天要发的
    ]
    print("=" * 88)
    print("标题打分器 · 用今天真实 7 篇回测")
    print("=" * 88)
    rows = []
    for t, v in REAL:
        s, good, notes = score(t)
        rows.append((s, t, v, good, notes))
    for s, t, v, good, notes in sorted(rows, reverse=True):
        mark = "🏆" if (v or 0) >= 1000 else ("⭐" if v is None else "")
        print()
        print("  %s %3d 分 ｜ %s" % (mark, s, t))
        print("      实测观看: %s" % ("（未发）" if v is None else v))
        if good:
            print("      ✅ %s" % "、".join(good))
        for n in notes:
            print("      ⚠️ %s" % n)

    print()
    print("=" * 88)
    print("校验：分数能否预测实测观看？")
    print("=" * 88)
    import statistics
    hit = [r for r in rows if r[2]]
    hi = [r for r in hit if r[0] >= 60]
    lo = [r for r in hit if r[0] < 60]
    if hi and lo:
        print("  高分（≥60）平均观看: %.0f ｜ 低分（<60）平均观看: %.0f" % (
            statistics.mean([r[2] for r in hi]), statistics.mean([r[2] for r in lo])))
        print("  倍数: %.1f 倍" % (statistics.mean([r[2] for r in hi]) / statistics.mean([r[2] for r in lo])))
    print()
    print("  各篇分数 vs 观看：")
    for s, t, v, _, _ in sorted(rows, key=lambda x: -(x[2] or 0)):
        print("     %3d 分 ｜ %6s ｜ %s" % (s, v if v else "未发", t[:40]))
