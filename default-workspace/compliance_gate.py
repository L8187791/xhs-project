# -*- coding: utf-8 -*-
"""合规闸门 v3.8 —— 对齐 2026-10-09 平台违规判定原文 + 2026-10-13 DB46/DB54 分级。
   ★ v3.8（DB54 · 用户 2026-10-13 拍板）：**只查 P0**——P0 阻断发布；P1/P2 降为**提示不阻断**。
     （原 v3.7「有 P1 需人工确认」告警语已改；判定行改为「P0=N(阻断) P1=N(提示) P2=N(提示)」。）

相比旧 gate_check_v2.py 的关键差异：
  1. P0 词库加入「诱饵引流」与「站内商品引导」两类（10/09 判定依据①）
  2. 新增「篇间结构雷同检测」（10/09 判定依据②：多篇同一写作套路）
  3. 商品引导/煽动紧迫的严重度**随 PAUSE_SALES 开关动态变化**：
     PAUSE_SALES=True（停售期）→ P0 硬违规阻断；
     PAUSE_SALES=False（正常期）→ P1 提醒（带链占比 ≤30%、正文不写引导句）
     [2026-10-13 用户拍板：改为动态描述，避免描述与实况脱节]
  4. ★ v3.7 三级分级体系（DB46 §调整3 · 用户 2026-10-13 拍板）：
     P0（碰了就处罚）= 站外导流 / 引导互动 / 焦虑贬损 → 零容忍，直接退回
     P1（碰了可能限流）= 商品引导 / 绝对化用语 / 煽动紧迫 / 效果承诺 → 尽量避免
     P2（建议避免）= 2027届 / 电子版 / 自动发货 / 同构标题 / 封面内页不符 → 仅提示，不阻断
     ⚠️ 绝对化用语（最/第一/独家/包过）用户拍板**维持 P1**，不升 P0。

用法：
  python compliance_gate.py [路径...]      # 默认扫描 干货批次*/*.md
"""
import sys, os, re, json, glob, itertools, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PAUSE_SALES = False  # 2026-10-11 用户拍板「10/12 起进 P1、恢复带链」→ 停售期结束；商品引导降为 P1（带链占比 ≤30%、正文不写引导句）

# [C35 §六·2 授权 · 2026-10-16] 路径常量由旧 Junction 路径改为「本脚本所在目录」（脚本恒在项目根）。
# 边界：**只改这一行常量，扫描逻辑一字不动**（承 C30 §三「闸门不改」）。
# 取证：旧路径 D:\Documents\deepseek-harness\default-workspace 实为 Junction，
#       Target = D:\小红书项目\default-workspace（C35 §二·1 实测 LinkType=Junction）
#       → 新旧路径解析到同一棵树，`_extract` 是同一物理目录 → 属**路径规范化**，非行为变更。
# 改前备份：_协作\_备份\compliance_gate-20261016-改前备份.py
WS = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(WS, "_extract", "gate_v3_report.json")

# ---------------- 规则 ----------------
# P0-A 诱饵引流（10/09 判定依据①）
P0_BAIT = [
    "自取", "私信", "扣1", "扣一", "扣 1", "关注后发", "关注我领", "关注就发",
    "回复我发你", "回复「", "回复\"", "评论区回复", "加微信", "微信", "QQ",
    "扫码", "二维码", "加群", "站外", "小号", "无偿分享请",
    # 2026-10-16 新增（平台 10 月新规 · B 级 → 我方按 P0 守）：
    #   「领取」系全措辞（原仅写「留言领取」）—— 「领取」已覆盖原
    #   「关注领取 / 留言领取 / 领取方式」三个子串，故三词合并为一个「领取」
    "领取", "领资料", "领攻略",
]
# P0-D 诱导互动（判「操纵数据」→ 降分发权重）—— 2026-10-16 新增（平台 10 月新规）
P0_INTERACT = ["求赞", "求收藏", "求点赞", "点赞收藏", "三连", "求个赞", "求关注", "求互动",
               "666", "888"]
# 「公众号」属站外导流，但作为公开信息渠道的陈述（官方公众号/招聘公众号）不算——白名单处理
BAIT_WHITELIST = ["官方公众号", "招聘公众号", "官方招聘公众号", "企业公众号", "就业网"]
# P0-B 商品/成交引导（停售期=P0；恢复售卖后降为 P1）
P0_SALES = [
    "左下角", "主页有", "主页商品", "拍下", "下单", "橱窗", "小黄车", "商品卡", "商品区",
    "完整版在", "链接在", "购买", "售价", "元包邮", "已上架", "库存",
]
# P0-C 焦虑/贬损（10/09 判定提及「诱饵话术」语境）
P0_ANXIETY = ["傻等", "太亏", "就完了", "傻子", "坑死", "后悔一辈子", "血亏", "白投"]
# P1-D 煽动/紧迫措辞 —— 来自 10/09 平台「违规内容」第 2 条原文（正文首句）
P1_URGENCY = ["秋招人注意", "不是明天", "就是今天", "赶紧", "再不投", "千万别", "速看",
              "马上截止", "最后一天", "错过就", "抓紧", "注意！"]
# P1 绝对化用语
P1_ABSOLUTE = ["最", "第一", "唯一", "独家", "永久", "100%", "包过", "保过", "保证",
               "必过", "全网", "顶级", "史上", "绝对"]
# 序数词白名单（正则）：第X批/件/步/轮…属于客观序数，不是绝对化用语
# （平台规则原文：「第一（序数除外）」；此前硬编码列表漏了"第一批"等，导致误报）
ABS_ORDINAL_RE = re.compile(
    r"第[一二三四五六七八九十百千0-9]+"
    r"(?:批|件|步|轮|次|阶段|类|种|条|点|项|篇|节|周|天|年|季度|季度|方面|部分|层|档|期|场|名|位|章|梯队)")
ABS_WHITELIST = ["最后", "最近", "最初", "最终", "最多", "最少", "最新", "最好用",
                 "第一次", "第一步", "第一份", "第一版", "第一阶段", "第一周",
                 "第一时间", "第一节", "第一篇",
                 "第一，", "第一、", "第一：", "第一是", "第一种", "第一点",
                 "第一条", "第一类", "第一方面", "第一项", "第一轮"]
# 结构规则：时间压迫词 + 具体数字/截止动作 → 平台判定过的违规结构
# （依据 10-08 判违规标题《银行秋招：今天就有4家要截止了》——该标题无任何词表禁词，
#   纯词表闸门抓不到，必须靠结构补足）
URGENCY_STRUCT_RE = re.compile(
    r"(今天|今日|明天|明日|当日|马上|即将|抓紧|倒计时)"
    r"[^。；\n]{0,14}"
    r"(截止|关闭|结束|到期|最后一天|就要|仅剩|不足)")
DIGIT_URGENCY_RE = re.compile(
    r"\d+\s*(家|个|所|条|项)?[^。；\n]{0,10}(今天|明天|今日|明日)[^。；\n]{0,10}(截止|关闭|结束|到期)")

P1_FACT = ["190", "16 家", "17 家", "40 家", "四档标色", "30 分钟", "永久更新"]

# ★ v3.7 P2 级词库（2026-10-13 DB46 分级体系 · 用户拍板）
# P2 = 「建议避免」：知道就行，不阻断、不计入不通过判定。
# 依据：DB46 §调整3 —— 封面内页不符/同构标题批量/「2027届」表述/电子版自动发货字眼
# 处置：仅提示（print 警告），不参与 P0/P1 判定，不影响 exit code。
P2_ADVISORY = [
    "2027届", "电子版", "自动发货", "网盘发货", "虚拟商品",
    "封面内页不符", "同构标题", "人教版", "北师大版", "押题", "名师出品",
]

# P1 过时价格口径（✅ 10/15 更新：现行有效价＝19.9 应届 / 49.9 跨人群订阅 / 99.9 长期锚点 / 0 元免费 Skill）
# 来源：WB14 裁定 9.9 已否；DB5 披露豆包侧 skill 内嵌 9.9/25.9/29.9 旧价，本机无该文件、改不动 → 靠闸门兜底
# 🔴 10/15 L 改口径：29.9 档已取消并入 49.9 → 下方 29.9 拦截项**保留有效**（防旧口径残留）
# 🔴 边界断言不可省：「19.9」里含「9.9」，无边界会误伤现行价
P1_PRICE_RE = [
    (re.compile(r"(?<![\d.])9\.9(?!\d)"), "9.9（WB14 已否）"),
    (re.compile(r"(?<![\d.])25\.9(?!\d)"), "25.9（已删组合价）"),
    (re.compile(r"(?<![\d.])29\.9(?!\d)"), "29.9（10/15 已取消档位）"),
    (re.compile(r"(?<![\d.])39\.9(?!\d)"), "39.9（已删口径）"),
]

# 子串误报防护：这些词出现在特定词内部时不算违规
# 例：「快速看一眼」含「速看」、「历史上」含「史上」——都不是违规表述
SUBSTRING_GUARD = {
    "速看": ["快速看", "加速看", "迅速看"],
    "史上": ["历史上", "史上最"],   # 史上最 仍需拦
    "绝对": ["绝对化用语", "绝对化"],  # 规则术语本身
    "保证": ["保证金", "保证书", "不保证"],  # 保证金/不保证 非承诺
    "包过": ["不包过", "不得写", "不写"],
    "独家": ["不独家", "不声称"],
}

# 元引用豁免（v3.3 · 2026-10-10）
# 问题：成稿文件里常附「自查清单」，清单本身会列举禁用词（如「正文无：自取／私信／扣1」）
#       → 闸门把这些**清单行**也判成违规，造成大量假阳性。
# 处置：**只跳过"清单/自查"语境**，不放开普通正文。
# 安全性：若正文真想违规，写成非清单句仍会被抓（见回归 D6）。
META_MARKERS = ["无：", "禁写", "禁词", "不写", "勿写", "自查", "不含", "序数除外",
                "- [ ]", "- [x]", "[ ]", "[x]"]

# ★ v3.6 售后文档豁免（2026-10-10 主运营裁定）
# 问题：「00 交付说明」这类**售后交付文档**必然出现「购买」，而
#       「请勿通过任何站外方式联系，以免受骗」是**反诱饵提示**（保护买家），
#       却被判成 P0 诱饵引流 —— 会让以后所有合规提示都不敢写。
# 处置：**只豁免两类明确的短语，不做整文档豁免**（防止变成漏洞）。
ANTI_BAIT_RE = re.compile(r"(请勿|不要|切勿|避免|谨防).{0,14}(站外|私下|非平台|其他渠道)")
PURCHASE_CTX_RE = re.compile(r"(感谢购买|购买后|购买时|已购买|购买过|拍下后|收到资料|交付说明)")


def _is_meta_line(text, pos, width=0):
    """判断命中是否落在「自查清单 / 元引用」整行里
    —— 按整行判断，而非 12 字窗口（窗口会漏掉长清单行）
    """
    s = text.rfind("\n", 0, pos) + 1
    e = text.find("\n", pos)
    if e == -1:
        e = len(text)
    line = text[s:e]
    return any(mk in line for mk in META_MARKERS)

SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2, "OK": 3}

# ============================================================
# 5.5 A 类合规表达公式 · 豁免规则（v3.2 · 任务卡 09 第 7 项）
# 依据作战计划 5.5 节：
#   「今天 / 截止 / 24:00」这类词不进 P0 禁词库；
#   但必须与「核验时间 + 具体日期」同时出现，单独出现才判 P0。
# 理由：把「情绪紧迫」换成「事实可核验」——同样是钩子，但信息密度更高、
#       平台判「商业营销」概率低得多，收藏率还更高。
# ⚠️ 豁免范围【仅限紧迫类】：诱饵引流 / 商品引导 / 焦虑贬损 / 绝对化用语
#    / 数字待复核 一律【不豁免】。
# ============================================================
EXEMPT_VERIFY_RE = re.compile(r"(核验|核到|核对|已核|我核|核了|核过|查过)")
EXEMPT_DATE_RE = re.compile(
    r"(\d{4}\s*[-/年]\s*\d{1,2}\s*[-/月]\s*\d{1,2})"      # 2026-10-10 / 2026年10月10日
    r"|(\d{1,2}\s*月\s*\d{1,2}\s*日)"                      # 10月10日
    r"|(\d{1,2}\s*[-/]\s*\d{1,2}(?!\d))"                   # 10-10 / 10/10
)


def has_verifiable_evidence(text):
    """是否同时具备「核验动作」+「具体日期」= 5.5 的可核验证据链"""
    return bool(EXEMPT_VERIFY_RE.search(text)) and bool(EXEMPT_DATE_RE.search(text))


def norm(s):
    return s.replace("　", " ").strip()


def scan_text(text, where, doc_kind="note"):
    """返回违规列表 [(severity, kind, hit, context)]"""
    hits = []
    t = text
    # 5.5 豁免判定（只作用于紧迫类，见上方说明）
    exempt_urgency = has_verifiable_evidence(t)

    def find(words, severity, kind):
        for w in words:
            for m in re.finditer(re.escape(w), t):
                s = max(0, m.start() - 12)
                ctx = t[s:m.end() + 12].replace("\n", " ")
                hits.append((severity, kind, w, ctx, m.start()))

    find(P0_BAIT, "P0", "诱饵引流")
    find(P0_INTERACT, "P0", "诱导互动")
    find(P0_SALES, "P0" if PAUSE_SALES else "P1", "商品引导")
    find(P0_ANXIETY, "P0", "焦虑贬损")
    # ⬇️ 5.5 豁免：有「核验动作+具体日期」证据链时不判紧迫（其他类别照旧）
    if not exempt_urgency:
        find(P1_URGENCY, "P0" if PAUSE_SALES else "P1", "煽动紧迫措辞")

    # 统一过滤：① 诱饵白名单 ② 子串误报防护 ③ 元引用（自查清单）豁免
    filtered = []
    for hit in hits:
        sev, kind, w, ctx, pos = hit
        if kind == "诱饵引流" and any(x in ctx for x in BAIT_WHITELIST):
            continue
        guards = SUBSTRING_GUARD.get(w)
        if guards and any(gd in ctx for gd in guards):
            continue
        # ③ 元引用：命中所在的**整行**是自查清单 → 跳过（正文违规仍会被抓）
        if _is_meta_line(t, pos):
            continue
        # ④ v3.6 售后文档豁免（**仅在 doc_kind == "aftersale" 时生效**）
        #    售后交付文档必然出现「购买/拍下」，且「请勿通过站外方式联系」是反诱饵提示。
        #    ⚠️ 笔记（默认 note）**不豁免** —— 「拍下后自动发送」在笔记里仍是商品引导。
        if doc_kind == "aftersale":
            if w in ("站外", "私下", "非平台") and ANTI_BAIT_RE.search(t[max(0, pos - 24):pos + 24]):
                continue
            if w in ("购买", "拍下", "下单", "链接"):
                continue
        filtered.append(hit)
    hits = filtered

    # 绝对化用语（带白名单）
    masked = t
    for w in ABS_WHITELIST:
        masked = masked.replace(w, "○" * len(w))
    masked = ABS_ORDINAL_RE.sub(lambda m: "○" * len(m.group(0)), masked)
    for w in P1_ABSOLUTE:
        for m in re.finditer(re.escape(w), masked):
            s0 = max(0, m.start() - 12)
            ctx = masked[s0:m.end() + 12].replace("\n", " ")
            # 子串误报防护
            guards = SUBSTRING_GUARD.get(w)
            if guards:
                full = masked[max(0, m.start() - 6):m.end() + 6]
                if any(gd in full for gd in guards) and not any(
                        gd in full for gd in ["史上最"] if w == "史上"):
                    continue
            # 元引用（自查清单）豁免
            if _is_meta_line(masked, m.start()):
                continue
            hits.append(("P1", "绝对化用语", w, ctx, m.start()))

    # 结构规则检测（在屏蔽后的文本上，避免与白名单冲突）
    # ⬇️ 5.5 豁免：同上门槛——有证据链时不判「时间压迫」结构
    if not exempt_urgency:
        for pat, tag in [(URGENCY_STRUCT_RE, "时间压迫+截止动作"), (DIGIT_URGENCY_RE, "数字+今天/明天+截止")]:
            for m in pat.finditer(masked):
                if _is_meta_line(masked, m.start()):
                    continue
                hits.append(("P1", "结构风险", tag, m.group(0).replace("\n", " ")[:40], m.start()))

    for w in P1_FACT:
        if w in t:
            for m in re.finditer(re.escape(w), t):
                # ★ 数字边界保护（v3.5）：防止「17 家」匹配到「117 家」里的子串
                if re.match(r"^\s*\d", w) and m.start() > 0 and t[m.start() - 1].isdigit():
                    continue
                s = max(0, m.start() - 12)
                ctx = t[s:m.end() + 12].replace("\n", " ")
                if _is_meta_line(t, m.start()):
                    continue
                hits.append(("P1", "数字/口径待复核", w, ctx, m.start()))

    # 过时价格口径（2026-10-11 WB14 裁定 + DB5 披露：豆包侧 xhs-job-note 内嵌旧价格表，本机改不到）
    # ⚠️ 必须带边界断言：否则「9.9」会命中「19.9」的子串（19.9 是现行有效价）
    for pat, tag in P1_PRICE_RE:
        for m in pat.finditer(t):
            if _is_meta_line(t, m.start()):
                continue
            s = max(0, m.start() - 12)
            ctx = t[s:m.end() + 12].replace("\n", " ")
            hits.append(("P1", "过时价格口径", tag, ctx, m.start()))

    # ★ v3.7 P2 级「建议避免」（DB46 分级体系）—— 只提示，不阻断
    for w in P2_ADVISORY:
        for m in re.finditer(re.escape(w), t):
            if _is_meta_line(t, m.start()):
                continue
            s = max(0, m.start() - 12)
            ctx = t[s:m.end() + 12].replace("\n", " ")
            hits.append(("P2", "建议避免（不阻断）", w, ctx, m.start()))
    return hits


# ---------------- 成稿解析 ----------------
def parse_notes(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    blocks = re.split(r"\n(?=## 第\s*\S+\s*篇)", raw)
    notes = []
    for b in blocks:
        m = re.match(r"## 第\s*(\S+)\s*篇\s*[·:：]?\s*(.*)", b)
        if not m:
            continue
        no, heading = m.group(1), m.group(2).strip()

        def seg(start_kw, end_kws):
            i = b.find(start_kw)
            if i < 0:
                return ""
            i += len(start_kw)
            j = len(b)
            for ek in end_kws:
                k = b.find(ek, i)
                if k >= 0:
                    j = min(j, k)
            return b[i:j].strip()

        title = seg("**标题（≤20 字）**", ["**正文**"])
        body = seg("**正文**", ["**标签**"])
        tags = seg("**标签**", ["**置顶首评"])
        comment = seg("**置顶首评", ["**配图**"])
        # 清理 markdown 粗体残留
        clean = lambda x: re.sub(r"\*\*|^#+\s*", "", x).strip()
        notes.append({
            "file": os.path.basename(path), "no": no, "heading": heading,
            "title": clean(title), "body": clean(body), "tags": clean(tags),
            "comment": clean(comment),
        })
    return notes


# ---------------- 篇间雷同检测 ----------------
def shingles(s, n=3):
    s = re.sub(r"\s+", "", s)
    return set(s[i:i + n] for i in range(max(0, len(s) - n + 1)))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def structure_of(note):
    body = note["body"]
    paras = [p for p in re.split(r"\n\s*\n|\n", body) if p.strip()]
    has_num = bool(re.search(r"[①②③④⑤]|^\s*\d[）)、.]", body, re.M))
    has_bullet = bool(re.search(r"^[·•\-]", body, re.M))
    ends_q = body.strip().endswith(("？", "?"))
    return (len(paras) // 3, has_num, has_bullet, ends_q)


def similarity_report(notes, jac_thr=0.28):
    issues = []
    for a, b in itertools.combinations(notes, 2):
        ja = jaccard(shingles(a["body"]), shingles(b["body"]))
        jt = jaccard(shingles(a["title"]), shingles(b["title"]))
        same_open = a["body"][:12] == b["body"][:12] and len(a["body"][:12]) >= 8
        same_struct = structure_of(a) == structure_of(b)
        flags = []
        if ja >= jac_thr:
            flags.append("正文相似度 %.2f" % ja)
        if jt >= 0.5 and len(a["title"]) >= 6:
            flags.append("标题相似度 %.2f" % jt)
        if same_open:
            flags.append("开头 12 字相同")
        if same_struct:
            flags.append("段落结构相同")
        if len(flags) >= 2:
            issues.append({
                "pair": "%s ↔ %s" % (a["no"], b["no"]),
                "detail": " + ".join(flags),
                "severity": "P0" if ja >= 0.4 or (same_open and same_struct) else "P1",
            })
    # 结构签名聚集（≥3 篇同一签名 = 批量模板特征）
    sigs = {}
    for n in notes:
        sigs.setdefault(structure_of(n), []).append(n["no"])
    for sig, nos in sigs.items():
        if len(nos) >= 3:
            issues.append({
                "pair": "结构聚集 %s" % (",".join(nos)),
                "detail": "%d 篇段落结构完全相同（批量模板特征）" % len(nos),
                "severity": "P1",
            })
    return issues


# ---------------- 主流程 ----------------
def main():
    paths = sys.argv[1:]
    if not paths:
        paths = sorted(glob.glob(os.path.join(WS, "干货批次*", "*.md")))
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "*.md")))
        else:
            files.append(p)
    files = [f for f in files if os.path.isfile(f) and "read" not in os.path.basename(f).lower()]

    all_hits, all_notes = [], []
    for f in files:
        notes = parse_notes(f)
        all_notes += notes
        # ★ v3.6 文档类型判定：售后交付文档（交付说明/售后/使用说明）走 aftersale 豁免
        _bn = os.path.basename(f)
        _kind = "aftersale" if re.search(r"(交付说明|售后|使用说明|常见问题|FAQ)", _bn, re.I) else "note"
        if not notes:
            # ★ v3.5 修复 P1：非成稿格式文件此前被**静默放行**（0 篇 → 打印"通过"）
            #   现在退化为「整文件当作一篇」扫描，避免拿到假通行证
            with open(f, encoding="utf-8") as fh:
                whole = fh.read()
            for sev, kind, w, ctx, _pos in scan_text(whole, "(整文件)", _kind):
                all_hits.append({"file": os.path.basename(f), "no": "(整文件)", "sev": sev,
                                 "kind": kind, "word": w, "ctx": ctx})
            continue
        for n in notes:
            blob = "\n".join([n["title"], n["body"], n["tags"], n["comment"]])
            # ★ v3.5 修复 P0-3：scan_text 返回 5 元组（含 pos），此前按 4 元组解包会**崩溃**
            for sev, kind, w, ctx, _pos in scan_text(blob, n["no"], _kind):
                all_hits.append({"file": n["file"], "no": n["no"], "sev": sev,
                                 "kind": kind, "word": w, "ctx": ctx})

    sims = similarity_report(all_notes) if len(all_notes) >= 2 else []

    print("=" * 68)
    print("合规闸门 v3  |  PAUSE_SALES=%s  |  %s" % (PAUSE_SALES, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("扫描文件 %d 个 · 成稿 %d 篇" % (len(files), len(all_notes)))
    for f in files:
        tag = ""
        if not parse_notes(f):
            tag = "  ⚠️ 非成稿格式 → 已按【整文件】扫描"
        print("   -", os.path.relpath(f, WS) + tag)
    print("=" * 68)

    counts = {"P0": 0, "P1": 0, "P2": 0}
    for h in all_hits:
        counts[h["sev"]] = counts.get(h["sev"], 0) + 1
    for s in sims:
        counts[s["severity"]] = counts.get(s["severity"], 0) + 1

    if all_hits:
        print("\n【词级问题】")
        for h in sorted(all_hits, key=lambda x: (SEV_ORDER.get(x["sev"], 9), x["no"])):
            print("  [%s] %-10s 第%s篇 `%s`  … %s" % (h["sev"], h["kind"], h["no"], h["word"], h["ctx"]))
    else:
        print("\n【词级问题】无 ✅")

    if sims:
        print("\n【篇间雷同】")
        for s in sims:
            print("  [%s] %s : %s" % (s["severity"], s["pair"], s["detail"]))
    else:
        print("\n【篇间雷同】无 ✅")

    print("\n" + "-" * 68)
    # ★ v3.8（DB54 · 用户 2026-10-13 拍板）：只查 P0，P1/P2 降为提示不阻断
    print("判定：P0=%d(阻断)  P1=%d(提示)  P2=%d(提示)  →  %s" % (
        counts["P0"], counts["P1"], counts["P2"],
        "❌ 不通过（P0 必须清零）" if counts["P0"] else "✅ 通过（P1/P2 仅提示，DB54 不阻断）"))
    if counts["P1"] or counts["P2"]:
        print("   提示：P1/P2 命中 %d 条，DB54 口径下**不阻断发布**，请自行判断" % (counts["P1"] + counts["P2"]))

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"time": datetime.datetime.now().isoformat(), "pause_sales": PAUSE_SALES,
                   "files": [os.path.relpath(f, WS) for f in files],
                   "notes": len(all_notes), "hits": all_hits, "similarity": sims,
                   "counts": counts}, f, ensure_ascii=False, indent=2)
    print("报告：%s" % OUT_JSON)


if __name__ == "__main__":
    main()
