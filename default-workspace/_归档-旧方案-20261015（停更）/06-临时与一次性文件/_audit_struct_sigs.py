# -*- coding: utf-8 -*-
"""只读审计：列出历史库每篇的『结构签名』，定位 P1 结构聚集的具体篇目。
不修改任何文件。用法：python _audit_struct_sigs.py
"""
import sys, glob, os, re, importlib.util

WS = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cg", os.path.join(WS, "compliance_gate.py"))
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)

_args = sys.argv[1:]
_skel_ids = []
if "--skeleton" in _args:
    _i = _args.index("--skeleton")
    _skel_ids = _args[_i + 1:]
    _args = _args[:_i]
_args = [a for a in _args if not a.startswith("--")]
paths = _args or sorted(glob.glob(os.path.join(WS, "干货批次*", "*.md")))

rows = []
whole = []
for p in paths:
    txt = open(p, encoding="utf-8").read()
    notes = cg.parse_notes(p) if hasattr(cg, "parse_notes") else []
    if not notes:
        whole.append(p)
        notes = [{"no": "整文件:" + os.path.basename(p), "title": "(非成稿格式)", "body": txt}]
    for n in notes:
        b = n["body"]
        paras = [x for x in re.split(r"\n\s*\n|\n", b) if x.strip()]
        sig = cg.structure_of(n)
        rows.append({
            "no": str(n["no"]),
            "file": os.path.relpath(p, WS),
            "title": (n.get("title") or "")[:26],
            "chars": len(re.findall(r"[\u4e00-\u9fff]", b)),
            "paras": len(paras),
            "sig": sig,
            "open12": b.replace("\n", "")[:12],
        })

print("=" * 96)
print("历史库结构签名审计（只读）  文件 %d 个 · 篇目 %d 篇" % (len(paths), len(rows)))
if whole:
    print("⚠️ 非成稿格式按整文件扫描：%s" % ", ".join(os.path.basename(x) for x in whole))
print("=" * 96)
print("%-6s %-8s %-9s %-6s %-22s %-12s %s" % ("编号", "段数", "签名", "汉字", "标题", "开头12字", "文件"))
print("-" * 96)
for r in rows:
    print("%-6s %-8s %-9s %-6s %-22s %-12s %s" % (
        r["no"], r["paras"], str(r["sig"]), r["chars"], r["title"], r["open12"], r["file"]))

print("\n【签名聚集分组】")
print("（口径同闸门：非成稿格式的『整文件』只扫敏感词、不计入结构聚集，故此处已剔除）")
groups = {}
for r in rows:
    if str(r["no"]).startswith("整文件"):
        continue
    groups.setdefault(r["sig"], []).append(r)
for sig, g in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    flag = "🔴 ≥3篇 P1" if len(g) >= 3 else ("🟡 2篇" if len(g) == 2 else "")
    print("  签名 %-18s 共 %d 篇：%s  %s" % (str(sig), len(g), ",".join(x["no"] for x in g), flag))
    if len(g) >= 3:
        for x in g:
            print("      - %s 《%s》 段%d 汉字%d  开头「%s」" % (x["no"], x["title"], x["paras"], x["chars"], x["open12"]))

# ---- 可选：两两正文/标题 Jaccard（阈值同闸门 0.28）----
if "--jaccard" in sys.argv:
    print("\n【两两 Jaccard（正文阈值 0.28 / 标题 0.50）】")
    real = [r for r in rows if not str(r["no"]).startswith("整文件")]
    cache = {}
    for r in real:
        for p in paths:
            for n in (cg.parse_notes(p) or []):
                if str(n["no"]) == r["no"]:
                    cache[r["no"]] = (n["title"], n["body"])
    import itertools as _it
    for a, b in _it.combinations(real, 2):
        ta, ba = cache[a["no"]]
        tb, bb = cache[b["no"]]
        jb = cg.jaccard(cg.shingles(ba), cg.shingles(bb))
        jt = cg.jaccard(cg.shingles(ta), cg.shingles(tb))
        mark = "🔴" if jb >= 0.28 or (jt >= 0.5 and len(ta) >= 6) else "🟢"
        print("  %s %s ↔ %s  正文 %.3f ｜ 标题 %.3f ｜ 结构 %s" % (
            mark, a["no"], b["no"], jb, jt, "相同" if a["sig"] == b["sig"] else "不同"))

# ---- 可选：打印指定篇目的段落骨架（每段前 18 字），用于人工判断是真聚集还是假阳性 ----
if "--skeleton" in sys.argv:
    want = sys.argv[sys.argv.index("--skeleton") + 1:]
    print("\n【段落骨架】")
    txt_cache = {}
    for p in paths:
        txt_cache[p] = open(p, encoding="utf-8").read()
    for p in paths:
        for n in (cg.parse_notes(p) or []):
            if want and str(n["no"]) not in want:
                continue
            paras = [x.strip() for x in re.split(r"\n\s*\n|\n", n["body"]) if x.strip()]
            print("\n  ▸ %s 《%s》  段 %d" % (n["no"], n["title"], len(paras)))
            for i, pa in enumerate(paras, 1):
                print("      %2d. %s" % (i, pa[:18].replace("\n", " ")))
