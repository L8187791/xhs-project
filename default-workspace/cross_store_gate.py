# -*- coding: utf-8 -*-
"""跨店同质化红线闸门（v1）
规则源：_协作/_扩充/跨店同质化红线-v1.md
用法：python cross_store_gate.py [日期]        日期默认 2026-10-12
判定 R1 正文 Jaccard / R2 标题 Jaccard / R3 首评前10字 / R4 开头12字 / R5 结构签名
返回码：0=全绿  2=有 🔴 阻断（不得发布）
"""
import os, re, sys, glob, itertools
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.path.dirname(os.path.abspath(__file__))
PA = os.path.join(WS, "_协作", "发布包")          # A 店：<日期>/
PB_SUFFIX = "-B店"                                 # B 店：<日期>-B店/

# ---- 阈值（与红线文档 v1 一致）----
TH = {
    "body_cross": (0.15, 0.28),   # (🟡下限, 🔴下限)
    "body_own":   (0.20, 0.35),
    "title":      (0.15, 0.30),
    "c10":        10,             # 首评前 N 字逐字相同 => 🔴
    "open12":     12,             # 正文开头 N 字逐字相同 => 🔴
    "struct_hit": 3,              # 同签名篇数 >=3 => 🔴 ；==2 => 🟡
}


def seg(raw, kw, stops=("## ",)):
    i = raw.find(kw)
    if i < 0:
        return ""
    i += len(kw)
    j = len(raw)
    for s in stops:
        k = raw.find("\n" + s, i)
        if k >= 0:
            j = min(j, k)
    return raw[i:j].strip()


def first_line(x):
    for l in (x or "").splitlines():
        if l.strip():
            return l.strip()
    return ""


def clean(x):
    return re.sub(r"\*\*", "", x or "").strip()


def load(path, comment_file=None):
    raw = open(path, encoding="utf-8").read()
    title = first_line(seg(raw, "## 标题"))
    body = seg(raw, "## 正文")
    m = re.search(r"## [^\n]*置顶[^\n]*\n(.*?)(?=\n## |\Z)", raw, re.S)
    comment = clean(m.group(1)) if m else ""
    if comment_file and os.path.exists(comment_file):
        comment = open(comment_file, encoding="utf-8").read().strip()
    return {"title": clean(title), "body": clean(body), "comment": comment}


def shingles(s, n=3):
    s = re.sub(r"\s+", "", s)
    return set(s[i:i + n] for i in range(max(0, len(s) - n + 1)))


def jac(a, b):
    A, B = shingles(a), shingles(b)
    return len(A & B) / len(A | B) if (A and B) else 0.0


def struct(body):
    paras = [p for p in re.split(r"\n\s*\n|\n", body) if p.strip()]
    has_num = bool(re.search(r"[①②③④⑤]|^\s*\d[）)、.]", body, re.M))
    has_bullet = bool(re.search(r"^[·•\-]", body, re.M))
    ends_q = body.strip().endswith(("？", "?"))
    return (min(len(paras) // 3, 4), has_num, has_bullet, ends_q)


def collect(date):
    docs = []
    adir = os.path.join(PA, date)
    for fn, cf in (("A层稿.md", "首评话术-A层.md"), ("B层稿.md", "首评话术-B层.md")):
        p = os.path.join(adir, fn)
        if os.path.exists(p):
            docs.append(("A店", fn[:-3], load(p, os.path.join(adir, cf))))
    bdir = os.path.join(PA, date + PB_SUFFIX)
    skip = ("骨架", "待填", "待定", "草稿", "模板", "说明", "校验", "README", "总览")
    for p in sorted(glob.glob(os.path.join(bdir, "B店稿-*.md"))):
        name = os.path.basename(p)
        if any(s in name for s in skip):
            continue
        docs.append(("B店", name[:-3], load(p)))
    return docs


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else "2026-10-12"
    docs = collect(date)
    if not docs:
        print("[!] 未找到稿件：", date)
        return 1
    print("=" * 96)
    print("跨店同质化红线闸门 v1  |  日期 %s  |  稿件 %d 篇" % (date, len(docs)))
    print("=" * 96)
    viol, warn = [], []

    # R5 结构签名统计（按店统计；跨店同骨架仅 🟡 观察）
    sig_store, sig_global = {}, {}
    for st, nm, d in docs:
        sg = struct(d["body"])
        sig_store.setdefault((st, sg), []).append(nm)
        sig_global.setdefault(sg, []).append(st + nm)

    print("\n%-30s %7s %7s %7s %6s %-20s %s" % ("对比对", "正文", "标题", "首评", "开头", "结构签名", "判定"))
    print("-" * 96)
    for (sa, na, da), (sb, nb, db) in itertools.combinations(docs, 2):
        jb, jt, jc = jac(da["body"], db["body"]), jac(da["title"], db["title"]), jac(da["comment"], db["comment"])
        same10 = da["comment"][:TH["c10"]] == db["comment"][:TH["c10"]] and len(da["comment"][:TH["c10"]]) >= 6
        same12 = da["body"][:TH["open12"]] == db["body"][:TH["open12"]] and len(da["body"][:TH["open12"]]) >= 8
        cross = (sa != sb)
        lo, hi = TH["body_cross"] if cross else TH["body_own"]
        tlo, thi = TH["title"]
        flags = []
        if jb >= hi:
            flags.append("🔴正文≥%.2f" % hi)
        elif jb >= lo:
            flags.append("🟡正文")
        if jt >= thi:
            flags.append("🔴标题")
        elif jt >= tlo:
            flags.append("🟡标题")
        if same10:
            flags.append("🔴首评撞头10字")
        if same12:
            flags.append("🔴开头撞段12字")
        if struct(da["body"]) == struct(db["body"]) and not (same10 or same12 or jb >= hi):
            flags.append("🟡同骨架")
        tag = "🔴" if any(f.startswith("🔴") for f in flags) else ("🟡" if flags else "✅")
        line = "%s%s↔%s%s" % (sa, na, sb, nb)
        print("%-30s %7.3f %7.3f %7.3f %6s %-20s %s %s" % (
            line, jb, jt, jc, "撞" if same12 else ("撞" if same10 else "否"),
            ("相同" if struct(da["body"]) == struct(db["body"]) else "不同"), tag, " ".join(flags)))
        if tag == "🔴":
            viol.append((line, flags))
        elif tag == "🟡":
            warn.append(line)

    print("\n=== R5 结构签名聚类（店内 ≥3=🔴 / 店内 =2=🟡 / 跨店=🟡观察）===")
    for (st, sg), lst in sorted(sig_store.items(), key=lambda x: -len(x[1])):
        lvl = "🔴" if len(lst) >= TH["struct_hit"] else ("🟡" if len(lst) == 2 else "✅")
        print("  %s %s %-24s ×%d  %s" % (lvl, st, str(sg), len(lst), " / ".join(lst)))
        if len(lst) >= TH["struct_hit"]:
            viol.append(("%s 店内结构签名 %s" % (st, sg), ["🔴店内同骨架×%d" % len(lst)]))
    for sg, lst in sorted(sig_global.items(), key=lambda x: -len(x[1])):
        stores = set(x[:2] for x in lst)
        if len(lst) >= 2 and len(stores) >= 2:
            print("  🟡 跨店同骨架 %-24s ×%d  %s" % (str(sg), len(lst), " / ".join(lst)))

    print("\n" + "-" * 96)
    if viol:
        print("判定：🔴 不通过（%d 项阻断）——不得发布" % len(viol))
        for v, f in viol:
            print("   ✗", v, "→", " ".join(f))
        return 2
    print("判定：✅ 通过（🟡 观察 %d 对，不阻断）" % len(warn))
    return 0


if __name__ == "__main__":
    sys.exit(main())
