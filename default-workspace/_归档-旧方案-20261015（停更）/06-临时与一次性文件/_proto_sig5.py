# -*- coding: utf-8 -*-
"""原型实验（不改 compliance_gate.py）：给结构签名加第五维，看历史库 01/05/07 是否自然分散。

只读取、只打印，不修改任何文件。
用法：python _proto_sig5.py
"""
import os, re, glob, importlib.util, collections

WS = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cg", os.path.join(WS, "compliance_gate.py"))
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)

HIST = sorted(glob.glob(os.path.join(WS, "干货批次*", "*.md")))
NEW = sorted(glob.glob(os.path.join(WS, "_协作", "outbox", "笔记-XHS-2026101[45]-WB-*.md")))


def para_list(body):
    return [p.strip() for p in re.split(r"\n\s*\n|\n", body) if p.strip()]


NUM_RE = re.compile(r"^(\s*[①②③④⑤]|\s*\d[）)、.])")
BULLET_RE = re.compile(r"^[·•\-]")


def sig4(n):
    return cg.structure_of(n)


def sig5_ratio(n):
    """第五维候选 A：清单段占比（编号段+圆点段 占全部段的比例）分 4 档"""
    ps = para_list(n["body"])
    if not ps:
        return 0
    lst = sum(1 for p in ps if NUM_RE.match(p) or BULLET_RE.match(p))
    r = lst / len(ps)
    return min(int(r * 4), 3)          # 0:<25% 1:25-50% 2:50-75% 3:>=75%


def sig5_bucket(n):
    """第五维候选 B：精确段数分档（每 3 段一档，不封顶）"""
    return len(para_list(n["body"])) // 3


def sig5_numratio(n):
    """第五维候选 C：编号段占比（只看编号段）分 3 档"""
    ps = para_list(n["body"])
    if not ps:
        return 0
    num = sum(1 for p in ps if NUM_RE.match(p))
    r = num / len(ps)
    return 0 if r == 0 else (1 if r < 0.30 else (2 if r < 0.50 else 3))


rows = []
for tag, paths in (("历史库", HIST), ("新四篇", NEW)):
    for p in paths:
        for n in (cg.parse_notes(p) or []):
            ps = para_list(n["body"])
            num = sum(1 for x in ps if NUM_RE.match(x))
            bul = sum(1 for x in ps if BULLET_RE.match(x))
            rows.append({
                "tag": tag, "no": str(n["no"]), "title": (n.get("title") or "")[:20],
                "paras": len(ps), "num": num, "bul": bul,
                "s4": sig4(n), "a": sig5_ratio(n), "b": sig5_bucket(n), "c": sig5_numratio(n),
            })

print("=" * 104)
print("结构签名『第五维』原型实验（只读 · 未改 compliance_gate.py）")
print("=" * 104)
print("%-5s %-6s %-22s %-5s %-5s %-5s │ %-14s %-8s %-8s %-8s" % (
    "来源", "编号", "标题", "段数", "编号段", "圆点段", "现有4维", "A清单占比", "B精确段", "C编号占比"))
print("-" * 104)
for r in rows:
    print("%-5s %-6s %-22s %-5d %-5d %-5d │ %-14s %-8s %-8s %-8s" % (
        r["tag"], r["no"], r["title"], r["paras"], r["num"], r["bul"],
        str(r["s4"]), r["a"], r["b"], r["c"]))

print("\n" + "=" * 104)
print("各方案下『≥3 篇同签名』聚集情况（🔴=仍触发 P1　🟢=已分散）")
print("=" * 104)
for label, key, extra in (("现有 4 维（现状）", "s4", None),
                          ("方案 A · 第五维=清单段占比", "s4", "a"),
                          ("方案 B · 第五维=精确段数分档", "s4", "b"),
                          ("方案 C · 第五维=编号段占比", "s4", "c")):
    g = collections.defaultdict(list)
    for r in rows:
        k = (r[key], r[extra]) if extra else r[key]
        g[k].append("%s%s" % (r["tag"][0], r["no"]))
    hits = {k: v for k, v in g.items() if len(v) >= 3}
    flag = "🔴 仍触发 P1 ×%d" % len(hits) if hits else "🟢 无聚集（P1 归零）"
    print("\n【%s】 %s" % (label, flag))
    for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
        if len(v) >= 2:
            tail = "  ← 🔴 ≥3" if len(v) >= 3 else ""
            print("   签名 %-22s 共 %d 篇：%s%s" % (str(k), len(v), ",".join(v), tail))

print("\n" + "=" * 104)
print("对新四篇的连带影响检查（改指标不能把新稿打成新 P1）")
print("=" * 104)
new = [r for r in rows if r["tag"] == "新四篇"]
for label, extra in (("A", "a"), ("B", "b"), ("C", "c")):
    g = collections.defaultdict(list)
    for r in new:
        g[(r["s4"], r[extra])].append(r["no"])
    worst = max(len(v) for v in g.values())
    print("  方案 %s：新四篇最大同签名聚集 = %d 篇 %s" % (
        label, worst, "🟢 安全（<3）" if worst < 3 else "🔴 新 P1 风险"))
