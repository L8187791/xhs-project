"""三层闸门自动校验 v2：区分「硬违规」与「软提示」，避免误报淹没真问题。

分级：
  P0 硬违规 —— 必须改，否则有法律/平台风险（百分比、通过率、保证类、站外引流、永久/100%）
  P1 需判断 —— 绝对化用语出现在商品/标题/封面时须改；出现在个人口语（如"最怕"）可留
  INFO      —— 数字一致性交叉核对，供人工确认

用法：python gate_check_v2.py
"""
import io
import os
import re

BASE = r"D:\Documents\deepseek-harness\default-workspace"

# 对外文案（必须零违规才能发布）
CONTENT_FILES = [
    "首批内容包_首发3篇与15篇排期.md",
    "内容包_周批次01_第4至7篇.md",
    "内容包_周批次02_第8至11篇.md",
    "内容包_周批次03_第12至15篇.md",
    "内容包_主力层入口_第16至17篇.md",
    "发布用_第1至3篇纯文本.md",
]
# 内部文档（含费率/漏斗比例等测算数字，属正常，单独扫描）
INTERNAL_FILES = ["产品事实卡.md", "产品阶梯与客单提升方案.md",
                  "主力层应急与替代方案.md", "30天作战日历.md",
                  "商品上架文案包.md", "产品_简历模板包内容母版.md",
                  "产品_面试题库_全本v1.md", "出图规格总表.md",
                  "银行核验工作单.md", "选题库_第2至3个月.md"]
ALL_FILES = CONTENT_FILES + INTERNAL_FILES

# ---- P0：硬违规（无豁免，出现即报） ----
P0 = [
    (re.compile(r"\d+\s*%"), "百分比数字（须有来源，通常应删）"),
    (re.compile(r"通过率"), "通过率"),
    (re.compile(r"包过|保offer|保录取|保证通过"), "违规承诺"),
    (re.compile(r"标准答案|独家真题|HR\s*精选"), "违禁话术"),
    (re.compile(r"永久|100%|全网|顶级|官方指定"), "绝对化用语（硬）"),
    # 站外引流：只匹配真实的联系方式，不匹配"手机号"这个词本身
    (re.compile(r"(?:微信|vx|VX|QQ)\s*[:：]?\s*[A-Za-z0-9_\-]{4,}"), "疑似真实联系方式"),
    (re.compile(r"1[3-9]\d{9}"), "疑似真实手机号"),
    (re.compile(r"加(?:个)?微信|加\s*QQ|私信发你微信"), "引导加联系方式"),
    # 虚构原价：允许"单买合计约 190"，只拦"原价 190"
    (re.compile(r"原价\s*\d+\s*元?(?!.{0,6}(?:不能|不得|禁止|别))"), "虚构原价（须为真实成交价）"),
]
# ---- P1：绝对化用语（口径依位置判断） ----
P1_WORDS = ["最好", "最强", "最快", "第一", "唯一", "最全", "最优", "最便宜", "最专业"]
# 明确属于"个人口语判断"的模式，命中则不计入 P1
COLLOQUIAL = re.compile(r"最(怕|后|近|早|想|难|容易|坑|堵|快|多|缺|终|新)|最后一个|最后一步|最后一天")

# 流程/元信息行豁免：这些行本身就在"讲规则"，不是在"写广告"
EXEMPT_MARKERS = ["- [x]", "- [ ]", "| 序号", "改前", "改后", "禁止", "不得",
                  "无绝对化", "无未核实", "自查", "拦截", "合规禁区", "无条件",
                  "不发出去", "合规要点", "硬红线", "不能写", "不要写", "不写",
                  "别用", "别写", "改成", "建议", "注意", "清单", "说明",
                  "不发", "不出现", "不得写", "原价意味着", "只写", "只能写"]

# 被引号包裹的违规词属于"引用/举例"，不算实际使用
QUOTED = re.compile(r"[「“\"']([^」”\"']{1,12})[」”\"']")


def strip_quoted(line: str) -> str:
    """去掉引号内的内容，避免把'举例说明的违规词'当成真实使用。"""
    return QUOTED.sub("", line)

def scan(files, want_p0=True):
    hard, soft = [], []
    for fn in files:
        path = os.path.join(BASE, fn)
        if not os.path.exists(path):
            hard.append((fn, "-", "文件不存在", ""))
            continue
        text = io.open(path, encoding="utf-8").read()
        for lineno, line in enumerate(text.splitlines(), start=1):
            s = line.strip()
            if not s or any(m in line for m in EXEMPT_MARKERS):
                continue
            probe = strip_quoted(line)   # 去掉引号内举例
            if want_p0:
                for pat, desc in P0:
                    m = pat.search(probe)
                    if m:
                        hard.append((fn, lineno, f"P0 {desc}：{m.group(0)}", s[:70]))
            for w in P1_WORDS:
                if w in probe and not COLLOQUIAL.search(probe):
                    soft.append((fn, lineno, f"P1 绝对化用语「{w}」", s[:70]))
    return hard, soft

print("=" * 68)
print("【闸门 A · 对外文案 P0 硬违规】→ 必须为零才能发布")
print("=" * 68)
hard, _ = scan(CONTENT_FILES, want_p0=True)
if hard:
    cur = None
    for fn, ln, kind, snip in hard:
        if fn != cur:
            print(f"\n── {fn}")
            cur = fn
        print(f"   L{ln}  {kind}\n        {snip}")
    print(f"\n❌ 共 {len(hard)} 处，不可发布")
else:
    print("✅ 对外文案 P0 零违规 —— 全部成稿可发布")

print()
print("=" * 68)
print("【闸门 B · 对外文案 P1 绝对化用语】个人口语已豁免")
print("=" * 68)
_, soft = scan(CONTENT_FILES, want_p0=False)
if soft:
    cur = None
    for fn, ln, kind, snip in soft:
        if fn != cur:
            print(f"\n── {fn}")
            cur = fn
        print(f"   L{ln}  {kind}\n        {snip}")
    print(f"\n⚠️ 共 {len(soft)} 处，需逐条判断是否出现在商品/标题/封面")
else:
    print("✅ 对外文案 P1 零违规")

print()
print("=" * 68)
print("【闸门 C · 内部文档】含费率/漏斗比例，属正常；仅看绝对化用语")
print("=" * 68)
_, soft_i = scan(INTERNAL_FILES, want_p0=False)
for fn, ln, kind, snip in soft_i:
    print(f"   {fn} L{ln}  {kind}")
if not soft_i:
    print("✅ 无")
print("   注：内部文档的百分比是测算参数，不是对外宣称，无需删除。")

print()
print("=" * 68)
print("【INFO 数字一致性交叉核对】")
print("=" * 68)
checks = [
    (re.compile(r"已核验\s*(\d+)\s*家"), "已核验家数", {"67"}),
    (re.compile(r"已核实\s*(\d+)\s*家"), "已核实家数", {"67"}),
    (re.compile(r"(\d+)\s*套"), "简历模板套数", {"12"}),
    (re.compile(r"(\d+)\s*题"), "面试题库题数", {"50"}),
]
got = False
for fn in CONTENT_FILES:
    path = os.path.join(BASE, fn)
    if not os.path.exists(path):
        print(f"  {fn}: 文件不存在（跳过）")
        continue
    text = io.open(path, encoding="utf-8").read()
    for pat, desc, expect in checks:
        found = set(pat.findall(text))
        if found:
            got = True
            flag = "✅" if found <= expect else f"⚠️ 期望 {expect}"
            print(f"  {flag} {fn} | {desc}: {sorted(found)}")
if not got:
    print("  （未检出可核对数字）")

print()
print("说明：P0 必须清零才可发布；P1 若出现在商品详情/标题/封面文字中必须改写，")
print("      个人口语（如「最怕」「最后一天」）可保留。")
