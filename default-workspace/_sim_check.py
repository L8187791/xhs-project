# -*- coding: utf-8 -*-
"""同质化五查（通用版 · v3 · 2026-10-16）—— 对应跨店同质化红线 R1–R5（店内口径）

用法：
  python _sim_check.py --new <稿.md> [<稿2.md> <稿3.md>]      # 只查新批内部互比
  python _sim_check.py --new <稿.md> --ref-dir <参照目录>       # 新批 vs 参照系
  python _sim_check.py --new <稿.md> --recent 3                 # 参照=最近3天发布包(默认)
  python _sim_check.py --new <稿.md> --dump-parse               # 只打印解析结果（回归取证用）
  python _sim_check.py --new <稿.md> --list-refs                # 只打印参照文件清单

判定阈值（店内 · 依主文档 §跨店同质化红线 v1）：
  R1 正文 Jaccard   ≥0.35🔴 / 0.20–0.35🟡
  R2 标题 Jaccard   ≥0.30🔴 / 0.15–0.30🟡
  R3 首评前 10 字    逐字相同🔴 / 前 6 字相同🟡
  R4 正文开头 12 字  逐字相同🔴 / 前 8 字相同🟡
  R5 结构签名        与参照系 ≥3 篇相同🔴 / =2 篇相同🟡

--- v2 变更（2026-10-16 · 依 C32 §四／§六·3 授权，改动方案见 outbox 回执）---
[v2-1] WS 由硬编码旧路径改为「**本脚本所在目录**」（脚本恒在项目根）。
       🔴 取证更正：旧路径 `D:\\Documents\\deepseek-harness\\default-workspace`
       **在本机存在**，它是一个 **Junction**，Target = `D:\\小红书项目\\default-workspace`
       （实测 `(Get-Item ...).LinkType = Junction`）→ 旧路径**能解析到同一棵树**，
       不是死路径；本次改动属**健壮性提升**，不属「修 bug」，历史五查结论**不因此作废**。
[v2-2] 解析器与 `compliance_gate.py` 对齐：支持成稿格式
       `## 第 N 篇` ＋ `**标题（≤20 字）**` / `**正文**` / `**标签**` / `**置顶首评` / `**配图**`
       （旧格式 `## 标题` / `## 正文` 保留，向后兼容）。
[v2-3] 一个文件含多篇时**逐篇**参与比对（标签形如 `文件名#篇号`），不再整文件当一篇。
[v2-4] 打印**参照文件清单**（`--list-refs` 或默认输出末尾），参照系可审计。
[v2-5] 新增 `--dump-parse`：打印每篇解析出的 title / body 前 40 字 / comment，用于回归取证。
[v2-6] 旧格式**首评段名**由「只认 `## …置顶…`」扩为 `## 置顶首评` / `## 首评` / `## 置顶评论`
       / 行内 `**置顶首评**：…` 四种写法。
       🔴 取证：现行 3 天参照篇（10-15／10-16 六篇）**没有一篇**用 `## …置顶…` 段名
       （10-16 B层 用 `## 首评`、10-15 A层 用 `**置顶首评**：`）→
       v1 下 **R3（首评前 10 字）对整个现行参照系恒为空 → 该红线从未真正生效**。
       本项属**新增检出能力**，非"修错"；历史卡上写的「首评10=-」在 v1 口径下**是空值不是通过值**。

--- v3 变更（2026-10-16 · 依 C35 §四·1／§四·4 ＋ §八 授权；改前备份：_协作/_备份/_sim_check-v2-20261016-改前备份.py）---
[v3-4] 🆕（依 C36 §二·1 裁定）`首评10`／`开头12` 两列改**三态**：`✅未命中`／`★命中`／`⚠️解析空`，
       并在结果末尾打印「参与比对篇数 ＋ 首评非空篇数」。
       理由：`-` 在 v1 与 v2/v3 有**两种含义** —— v1＝两边首评都解析成空 → 输出 `-`（**假通过**）；
       v2/v3＝取到真值但前 10 字不同 → 输出 `-`（**真通过**）。同一符号两种含义 →
       **「R3 是否已恢复」在产出物层面无法自证**。
       🔴 **边界：只改输出表达，阈值与判定逻辑一字不动**（承 C36 §二·1）。
[v3-1] `--recent` 的参照文件筛选：只取**文件名以 `笔记-` 开头**的件。
       原取 `发布包/<日期>/*.md` 全部 → 实测该 glob 共 24 个，**只有 7 个是笔记件**，
       另 17 个（二创检查记录｜_备份_二创记录｜_闸门校验｜专家判定报告｜自测报告｜选题与素材包｜
       首评话术｜稿.md｜发布包-第2篇.md 等）**没有 `## 标题`／`## 正文`** → 走 `load()` 退化分支
       （title 落首行、body 落整文件）→ 拿整份记录文件去算 Jaccard。
       🔴 取证影响面：09:41 那组「8 篇」里 `2026-10-14_15/` 的 2 个文件**都不是笔记件** → **该组数字不可用**；
       15:11 实跑的 7 个参照文件**全部是笔记件** → 现行结论（库存候选稿 0.041／0.000）**不受影响**。
       被排除项一律**打印清单**（可审计）；窗口内若某日全为非笔记件 → **该日视为不在参照系**，
       不做「旧命名稿兜底」（保持规则单一；见 C35 §四·4 取舍）。
[v3-2] `--list-refs` 末尾追加 `REFSET_SHA256=`（对「绝对路径＋整数 mtime」排序串取 SHA-256）→
       参照集**可对账**。解决「同一稿同日两次跑数不可比」：`--recent N` 是**滑动窗口**
       （实测同一脚本 09:41 参照 8 篇／14:03 参照 6 篇／15:11 参照 6 篇，因 10-14_15 两件掉出窗口）。
       卡上引用本值即可证明「两次跑的是不是同一批参照」。
[v3-3] `--new` 改为「**非 `--list-refs` 时必填**」。原恒 `required=True` → 单独跑 `--list-refs` 直接
       报 `error: the following arguments are required: --new`（与 docstring 自相矛盾）。
"""
import os, re, sys, itertools, glob, time, argparse, hashlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# [v2-1] 以脚本自身位置为工作区根；可用环境变量 SIM_WS 覆盖（做对照实验用）
WS = os.environ.get("SIM_WS") or os.path.dirname(os.path.abspath(__file__))

T_BODY_RED, T_BODY_YEL = 0.35, 0.20
T_TITLE_RED, T_TITLE_YEL = 0.30, 0.15

NOTE_SPLIT = re.compile(r"\n(?=##\s*第\s*\S+\s*篇)")

# [v3-1] 参照系只取笔记件（原取目录下全部 *.md，混入二创记录/闸门校验/自测报告等非笔记件）
NOTE_PREFIX = "笔记-"


def seg(raw, kw, stops=("## ", "# ")):
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


def seg2(raw, start_kw, end_kws):
    """成稿格式用：与 compliance_gate.parse_notes 同口径（找 start_kw，截到任何一个 end_kw）"""
    i = raw.find(start_kw)
    if i < 0:
        return ""
    i += len(start_kw)
    j = len(raw)
    for ek in end_kws:
        k = raw.find(ek, i)
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


def clean_h(x):
    return re.sub(r"\*\*|^#+\s*", "", x or "").strip()


def parse_comment_legacy(raw):
    """[v2-6] 旧格式首评段名有多种写法，逐一尝试，避免 R3 静默失效。

    实测（2026-10-16）现行参照系的段名写法：
      `## 置顶首评`（10-12 B层稿）｜`## 置顶评论`（10-11 稿）｜`## 首评`（10-16 B层）
      ｜`**置顶首评**：…`（10-15 A层 · 行内粗体，前置无 `##`）
    v1 只认 `##[^\n]*置顶[^\n]*\n` → **10-15／10-16 参照篇全部取不到首评 → R3 从未真正生效**。
    """
    for pat in (r"^##+\s*置顶?首评[^\n]*\n(.*?)(?=\n## |\Z)",
                r"^##+\s*首评[^\n]*\n(.*?)(?=\n## |\Z)",
                r"^##+[^\n]*置顶[^\n]*\n(.*?)(?=\n## |\Z)",
                r"^\*\*\s*置顶?首评\s*\*\*\s*[：:]\s*([^\n]+)"):
        m = re.search(pat, raw, re.S | re.M)
        if m:
            return clean(m.group(1))
    return ""


def load(path):
    """返回 list[dict]：一个文件可能含多篇（成稿格式）"""
    raw = open(path, encoding="utf-8").read()
    base = os.path.basename(path)
    out = []

    # ---- 成稿格式（优先）：## 第 N 篇 + **标题（≤20 字）** / **正文** ----
    if re.search(r"\n##\s*第\s*\S+\s*篇", raw):
        for b in NOTE_SPLIT.split(raw):
            m = re.match(r"##\s*第\s*(\S+)\s*篇\s*[·:：]?\s*(.*)", b)
            if not m:
                continue
            no = m.group(1)
            title = clean_h(seg2(b, "**标题（≤20 字）**", ["**正文**"]))
            if not title:
                title = clean_h(seg2(b, "**标题**", ["**正文**"]))
            body = clean_h(seg2(b, "**正文**", ["**标签**", "\n## "]))
            comment = clean_h(seg2(b, "**置顶首评", ["**配图**", "\n## "]))
            out.append({"name": "%s#%s" % (base, no), "title": title,
                        "body": body, "comment": comment})
        if out:
            return out

    # ---- 旧格式（向后兼容）：## 标题 / ## 正文 ----
    title = clean(first_line(seg(raw, "## 标题")))
    if not title:
        m = re.search(r"^#+\s*(.+)", raw, re.M)
        title = m.group(1) if m else ""
    body = clean(seg(raw, "## 正文"))
    if not body:
        body = raw
    comment = parse_comment_legacy(raw)
    out.append({"name": base, "title": clean(title), "body": clean(body),
                "comment": comment})
    return out


def refset_sha256(files):
    """[v3-2] 参照集内容指纹：对「绝对路径|整数mtime」排序串取 SHA-256（卡上引用即可对账）"""
    items = []
    for p in files:
        try:
            items.append("%s|%d" % (os.path.abspath(p), int(os.path.getmtime(p))))
        except Exception:
            items.append("%s|?" % os.path.abspath(p))
    items.sort()
    return hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()


def shingles(s, n=3):
    s = re.sub(r"\s+", "", s or "")
    return set(s[i:i + n] for i in range(max(0, len(s) - n + 1)))


def jac(a, b):
    A, B = shingles(a), shingles(b)
    return len(A & B) / len(A | B) if (A and B) else 0.0


def struct(body):
    paras = [p for p in re.split(r"\n\s*\n|\n", body) if p.strip()]
    has_num = bool(re.search(r"[①②③④⑤]|^\s*\d[）)、.]", body, re.M))
    has_bullet = bool(re.search(r"^[·•\-]", body, re.M))
    ends_q = (body or "").strip().endswith(("？", "?"))
    return (min(len(paras) // 3, 4), has_num, has_bullet, ends_q)


def grade(v, red, yel):
    return "🔴" if v >= red else ("🟡" if v >= yel else "✅")


def tri_state(hit, txts):
    """[v3-4] 三态表达：★命中 / ⚠️解析空 / ✅未命中。

    原两态（`★`／`-`）下，`-` 同时代表「真未命中」与「解析为空导致的未命中」，
    使 v1 的假通过无法与 v2/v3 的真通过区分（C36 §二·1）。
    🔴 只改表达：参与判定的 `hit` 仍由调用方按原阈值算好传入。
    """
    if hit:
        return "★命中"
    for t in txts:
        if len((t or "").strip()) < 8:
            return "⚠️解析空"
    return "✅未命中"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", nargs="+", default=None,
                    help="待查稿件（可多个）；[v3-3] 仅 --list-refs 时可省略")
    ap.add_argument("--ref-dir", default=None)
    ap.add_argument("--recent", type=int, default=3, help="参照系=最近N天发布包（默认3）")
    ap.add_argument("--dump-parse", action="store_true", help="[v2-5] 只打印解析结果")
    ap.add_argument("--list-refs", action="store_true", help="[v2-4] 只打印参照文件清单")
    a = ap.parse_args()

    # [v3-3] --new 改为「非 --list-refs 时必填」
    if not a.list_refs and not a.new:
        ap.error("the following arguments are required: --new")

    news = []
    for p in (a.new or []):
        if os.path.exists(p):
            news.extend(load(p))
        else:
            print("⚠️ 文件不存在，已跳过：%s" % p)

    if a.dump_parse:
        print("=== 解析取证（--dump-parse）===")
        print("WS = %s" % WS)
        for n in news:
            print("-" * 60)
            print("篇名   ：%s" % n["name"])
            print("标题   ：%s  （%d 字）" % (n["title"], len(n["title"])))
            print("正文头 ：%s" % n["body"][:40])
            print("正文长 ：%d 字符" % len(n["body"]))
            print("首评   ：%s" % (n["comment"][:30] or "(空)"))
        return 0

    refs, ref_files, excluded = [], [], []
    if a.ref_dir:
        ref_files = sorted(glob.glob(os.path.join(a.ref_dir, "*.md")))
    else:
        cut = time.time() - a.recent * 86400
        for p in sorted(glob.glob(os.path.join(WS, "_协作", "发布包", "*", "*.md"))):
            try:
                if os.path.getmtime(p) < cut:
                    continue
            except Exception:
                continue
            # [v3-1] 非笔记件不入参照系（其解析退化：title 落首行、body 落整文件 → 数字不可用）
            if not os.path.basename(p).startswith(NOTE_PREFIX):
                excluded.append(p)
                continue
            ref_files.append(p)
    refs = []
    for p in ref_files:
        refs.extend(load(p))

    new_names = {n["name"] for n in news}
    n_parsed_all = len(refs)
    refs = [r for r in refs if r["name"] not in new_names]

    if a.list_refs:
        print("=== 参照文件清单（--list-refs）===")
        print("WS = %s" % WS)
        print("截断时点 = now - %d 天 = %s" % (
            a.recent, time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() - a.recent * 86400))))
        for p in ref_files:
            print("  %s  (%s)" % (p, time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(p)))))
        print("文件 %d 个 → 解析出 %d 篇 → 去自比后 %d 篇" % (len(ref_files), n_parsed_all, len(refs)))
        if excluded:
            print("[v3-1] 已排除非笔记件 %d 个（文件名不以 \"%s\" 开头）：" % (len(excluded), NOTE_PREFIX))
            for p in excluded:
                print("  × %s" % p)
        print("REFSET_SHA256=%s" % refset_sha256(ref_files))
        return 0

    print("新批：%s" % ", ".join(n["name"] for n in news))
    print("参照系：%d 篇（最近 %d 天）｜文件 %d 个" % (len(refs), a.recent, len(ref_files)))
    print()
    print("%-34s %7s %7s %8s %9s %-8s %s" % ("对比对", "正文", "标题", "首评10", "开头12", "签名", "判定"))
    print("-" * 92)

    worst = {}
    pairs = list(itertools.combinations(news, 2)) + [(x, y) for x in news for y in refs]
    for da, db in pairs:
        jb, jt = jac(da["body"], db["body"]), jac(da["title"], db["title"])
        o12 = da["body"][:12] == db["body"][:12] and len(da["body"][:12]) >= 8
        c10 = da["comment"][:10] == db["comment"][:10] and len(da["comment"][:10]) >= 8
        sa, sb = struct(da["body"]), struct(db["body"])
        g = "🔴" if (jb >= T_BODY_RED or jt >= T_TITLE_RED or o12 or c10) else \
            ("🟡" if (jb >= T_BODY_YEL or jt >= T_TITLE_YEL or sa == sb) else "✅")
        print("%-34s %7.3f %7.3f %8s %9s %-8s %s" % (
            (da["name"][:16] + "↔" + db["name"][:16]), jb, jt,
            tri_state(c10, [da["comment"], db["comment"]]),
            tri_state(o12, [da["body"], db["body"]]),
            ("同" if sa == sb else "异"), g))
        worst[g] = worst.get(g, 0) + 1

    print()
    print("=== 结构签名（新批）===")
    for n in news:
        print("  %-28s %-22s 开头12字：%s" % (n["name"][:28], str(struct(n["body"])), n["body"][:12]))

    print()
    print("=== 参照文件清单 ===")
    for p in ref_files:
        print("  %s" % p)
    if excluded:
        print("[v3-1] 已排除非笔记件 %d 个：%s" % (
            len(excluded), "；".join(os.path.basename(x) for x in excluded)))
    print("REFSET_SHA256=%s" % refset_sha256(ref_files))

    verdict = "🔴" if worst.get("🔴") else ("🟡" if worst.get("🟡") else "✅")
    print()
    print("=== 交付卡一行 ===")
    # [v3-4] 三态：命中 / 解析空 / 未命中
    c10_hit = any(x["comment"][:10] == y["comment"][:10] and len(x["comment"][:10]) >= 8 for x, y in pairs)
    o12_hit = any(x["body"][:12] == y["body"][:12] and len(x["body"][:12]) >= 8 for x, y in pairs)
    c_empty = any(len((x["comment"] or "").strip()) < 8 or len((y["comment"] or "").strip()) < 8 for x, y in pairs)
    o_empty = any(len((x["body"] or "").strip()) < 12 or len((y["body"] or "").strip()) < 12 for x, y in pairs)
    c10_s = "★命中" if c10_hit else ("⚠️解析空" if c_empty else "✅未命中")
    o12_s = "★命中" if o12_hit else ("⚠️解析空" if o_empty else "✅未命中")
    print("同质化五查：正文%.3f/标题%.3f/首评10=%s/开头12=%s/签名=%s → %s" % (
        max([jac(x["body"], y["body"]) for x, y in pairs] or [0]),
        max([jac(x["title"], y["title"]) for x, y in pairs] or [0]),
        c10_s, o12_s,
        "有同" if any(struct(x["body"]) == struct(y["body"]) for x, y in pairs) else "全异",
        verdict))
    # [v3-4] 参与比对篇数 ＋ 首评非空篇数 → 让「R3 是否真的跑了」可自证
    n_c_new = sum(1 for n in news if len((n["comment"] or "").strip()) >= 8)
    n_c_ref = sum(1 for r in refs if len((r["comment"] or "").strip()) >= 8)
    print("[v3-4] 参与比对：篇对 %d 个（新批 %d 篇 × 参照 %d 篇）｜首评非空：新批 %d/%d、参照 %d/%d" % (
        len(pairs), len(news), len(refs), n_c_new, len(news), n_c_ref, len(refs)))
    return 0 if verdict != "🔴" else 2


if __name__ == "__main__":
    sys.exit(main())
