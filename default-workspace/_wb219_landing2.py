# -*- coding: utf-8 -*-
r"""WB219 续：#53 已被 B3 场占用 → 本场看板用 #54；索引／日志／MEMORY"""
import hashlib, os

WS = r"D:\小红书项目\default-workspace"
BOARD = WS + r"\_协作\推进看板-2026-10.md"
IDX   = WS + r"\_协作\卡索引.md"
LOG   = WS + r"\.workbuddy\memory\2026-10-17.md"
MEM   = r"D:\Documents\2026-10-13-05-08-45\.workbuddy\memory\MEMORY.md"
STRICT = WS + r"\_协作\严谨记录台账-2026-10.md"

def stat(p):
    b = open(p, "rb").read()
    ls = b.split(b"\n")
    cr = sum(1 for l in ls if l.endswith(b"\r"))
    return len(b), hashlib.md5(b).hexdigest(), cr, len(ls) - 1 - cr

s_sz, s_md5, s_cr, _ = stat(STRICT)
print("严谨台账实际 %d B md5 %s" % (s_sz, s_md5[:10]))

# ---------- ② 看板 #54 ----------
sz, md5, cr, bare = stat(BOARD)
print("看板 %d B md5 %s" % (sz, md5[:10]))
b = open(BOARD, "rb").read()
assert cr == 0
s = b.decode("utf-8")
assert "| 54 |" not in s, "看板已有 #54"
row = ("| 54 | 📌 **10/17 C 层（20:30 场）已发落账（WB219）· 当日三层齐** | W | 🟢 已落账 | "
       "L 20:3x 上报「C层已发」→ **先取证后落账**。桌面 `3-C层-文案-2030发.txt` **1,659 B／md5 `7a8a913c…`／CRLF 20** ↔ 正本 **1,931 B／md5 `24bdd51e…`／纯 LF 30**，"
       "**四项逐字程序化比对全一致**（标题 `45dbe5e7`／正文 `b222b561`／标签 `dabf4172`／首评 `700e3ca3`）→ **发布版本＝定稿版本，无返工**。"
       "标题 **17 字符（去空格）／16 汉字**、正文 **332 汉字**（7 段）、标签 8 个、首评 24 汉字。"
       "**首评与正文 CTA 已错开、不撞**；敏感元素机检零命中（家数／企业名／待遇／学历门槛断言）；`截止` 仅 2 次泛称无具体日期。"
       "落点：发布台账 31,217→**34,321 B**／严谨台账 §三十九 → **%d B**／驾驶舱 166,385→**167,005 B**（md5 `3ac5fc6f29…`·CRLF 1221·裸LF 0·桌面同源）／出首评「复制即发」件。 | "
       "✅ 驾驶舱 **34/34**。🟡 首评 ≈21:0x **待 L 手动发**（W 不代发·红线第 4 条 v2）。"
       "🟡 未取到：C 层精确发布时刻／是否过审／首日数据，不推断。🔴 **W-A60**（比对脚本 regex 误报→行级重写后全绿）｜**W-A61**（页脚 md `**` 搬进 HTML→已改 `<b>`）。"
       "🟢 **当日三层 A 08:54／B 12:xx／C 20:3x 全部完成** → 回传 10/18 08:54／12:30／20:30 后。🔴 看板 #53 已被 `B3` 20:00 场（WB217）占用 → 本场顺延 #54。 |") % s_sz
if not s.endswith("\n"):
    s += "\n"
open(BOARD, "wb").write((s + row).encode("utf-8"))
sz2, md52, cr2, _ = stat(BOARD)
print("看板 → %d B (+%d) md5 %s" % (sz2, sz2 - sz, md52[:10]))

# ---------- ③ 索引定稿 ----------
sz, md5, cr, bare = stat(IDX)
assert cr == 0
s = open(IDX, "rb").read().decode("utf-8")
ph = "| XHS-20261017-WB219 | 回执卡 | 进行中（占位 · 取号即登记 · C 层已发落账） | W→C(抄送L) | 🟡 进行中 |"
assert s.count(ph) == 1, "占位行异常"
final = ("| XHS-20261017-WB219 | 回执卡 | **10/17 C 层（20:30 场）已发落账**（W → C，抄送 L，20:4x）。L 20:3x 上报「C层已发」，未给精确时刻 → 不代填。"
         "**发布版本＝定稿版本（四项逐字程序化比对全一致）**：桌面件 1,659 B／`7a8a913ce8785683bc8b16365ce5542c`／CRLF 20 ↔ 正本 1,931 B／`24bdd51e16606652db0bf2f7f187c543`／纯 LF 30；"
         "标题 `45dbe5e7`（17 字符（去空格）／16 汉字）／正文 `b222b561`（332 汉字·7 段）／标签 `dabf4172`（8 个）／首评 `700e3ca3`（24 汉字）——**四项全同**。"
         "首评与正文 CTA 已错开不撞；敏感元素机检零命中。实测：发布台账 31,217→**34,321 B**（`a84e056e38…`）／严谨台账 §三十九 132,597→**%d B**／"
         "驾驶舱 166,385→**167,005 B**（`3ac5fc6f29…`·CRLF 1221·裸LF 0·桌面同源）；驾驶舱自检 **34/34**。"
         "出首评「复制即发」件（≈21:0x，W 不代发）。🟢 **当日三层全部完成**。🔴 **W-A60**（比对脚本 regex 误报→行级重写）｜**W-A61**（页脚 md 星号搬进 HTML→已改 `<b>`）"
         "｜🟡 C53 载明「报白已提交」→ 提交窗说法被现实超越、千帆 P0 转等待态｜🔴 看板 #53 被 `B3` 场占用 → 本场 #54 | W→C(抄送L) | 🟢 已交付 |") % s_sz
s = s.replace(ph, final, 1)
open(IDX, "wb").write(s.encode("utf-8"))
sz2, md52, cr2, _ = stat(IDX)
print("索引 → %d B md5 %s 行 %d 残留占位 %d" % (sz2, md52[:10], len(open(IDX,'rb').read().split(b'\n')) - 1, open(IDX,'rb').read().decode('utf-8').count(ph)))

# ---------- ④ 日志 ----------
lb = open(LOG, "rb").read()
add = """
## 20:4x · 10/17 C 层（20:30 场）已发落账（WB219）

- L 20:3x 上报「C层已发」，未给精确时刻 → 不代填
- **四项逐字程序化比对全一致**（行级解析＋去空白 md5）：桌面件 1,659 B/`7a8a913c…`/CRLF 20 ↔ 正本 1,931 B/`24bdd51e…`/纯 LF 30；标题 `45dbe5e7`（17 字符（去空格）／16 汉字）／正文 `b222b561`（332 汉字）／标签 `dabf4172`（8 个）／首评 `700e3ca3`（24 汉字）→ **发布版本＝定稿版本，无返工**
- 首评与正文 CTA 已错开不撞；敏感元素机检零命中（`截止` 仅 2 次泛称）
- 落点：发布台账 31,217→34,321 B｜严谨台账 §三十九 132,597→%d B｜看板 #54（**#53 已被 B3 场 WB217 占用**）｜索引 WB219｜驾驶舱 166,385→167,005 B（md5 `3ac5fc6f29…`·CRLF 1221·裸LF 0·桌面同源）｜出 `C层-首评-复制即发.txt`
- 自检：驾驶舱 **34/34** ✅
- 自身错误：**W-A60** 比对脚本 regex 抓不到含空格段标题 → 误报 3 项不一致，改行级解析后全绿；**W-A61** 页脚 md `**` 搬进 HTML → 已改 `<b>`（顺手清正文区一处历史同类误用）
- 🟢 **当日三层 A 08:54／B 12:xx／C 20:3x 全部完成**；回传 10/18 08:54／12:30／20:30 后
- C53 载明「**报白已提交**、下周出结果」→ 10/20–22 提交窗说法被现实超越；千帆 P0 三项转等待态（不催、不推断）
""" % s_sz
if not lb.endswith(b"\n"):
    lb += b"\n"
open(LOG, "wb").write(lb + add.encode("utf-8"))
print("日志 →", len(open(LOG, "rb").read()), "B")

# ---------- ⑤ MEMORY ----------
b = open(MEM, "rb").read()
assert b"\r" not in b
s = b.decode("utf-8")
before = len(b)
pairs = [
    ("- 🔴 **C 层 20:30 待发**（稿已就绪 · 332 汉字 · 红狐 0 · 闸门全清）；发后 W 落账。",
     "- 🟢 **C 层 20:30 已发（L 20:3x）、已落账**（WB219 · 332 汉字 · 四项逐字比对全一致）；"
     "**当日三层 A 08:54／B 12:xx／C 20:3x 全部完成** → 回传 10/18 08:54／12:30／20:30 后。"),
    ("- 🟢 **报白：下周才有结果 → 等 L 通知，W 不催不推断**（L 10/17 20:0x）；10/20–22 提交窗是否顺延由 L 定。",
     "- 🟢 **报白已提交、下周出结果 → 等 L 通知，W 不催不推断**（L 10/17 20:0x ＋ C53 载明「已提交」，C 级）；"
     "🟡 **10/20–22 提交窗说法已被现实超越**；千帆 P0 三项目标转**等待态**（随提交闭环或降级）。"),
    ("**164,781 B ／ md5 `e9b0ee90f0bd3806729ee746542de0e4` ／ CRLF 1216 ／ 纯 LF 0**（WB218 后）",
     "**167,005 B ／ md5 `3ac5fc6f29…` ／ CRLF 1221 ／ 纯 LF 0**（WB219 后）"),
]
for old, new in pairs:
    c = s.count(old)
    print("MEMORY 锚点 %d：%s" % (c, old[:30]))
    if c == 1:
        s = s.replace(old, new, 1)
open(MEM, "wb").write(s.encode("utf-8"))
d = open(MEM, "rb").read()
print("MEMORY %d → %d B md5 %s CRLF %d" % (before, len(d), hashlib.md5(d).hexdigest()[:10], d.count(b"\r")))

# ---------- ⑥ 终检 ----------
print("\n=== 终检 ===")
for p, kws in [
    (BOARD, ["| 54 |", "WB219"]),
    (IDX, ["WB219", "四项全同"]),
    (STRICT, ["## 三十九", "W-A60"]),
    (MEM, ["C 层 20:30 已发", "报白已提交"]),
]:
    t = open(p, "rb").read().decode("utf-8")
    print("%-30s %s" % (p.split("\\")[-1], "✅" if all(k in t for k in kws) else "❌ 缺：" + str([k for k in kws if k not in t])))
