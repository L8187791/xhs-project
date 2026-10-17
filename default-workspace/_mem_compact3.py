# -*- coding: utf-8 -*-
# 第三轮：结构性迁移（表 ID 明细 → REFERENCE §C）＋ MEMORY 再压
import hashlib

MEM = r'D:\Documents\2026-10-13-05-08-45\.workbuddy\memory\MEMORY.md'
REF = r'D:\Documents\2026-10-13-05-08-45\.workbuddy\memory\REFERENCE-求职项目.md'


def stat(p, tag):
    b = open(p, 'rb').read()
    ls = b.split(b'\n')
    cr = sum(1 for l in ls if l.endswith(b'\r'))
    print('%s %d B / CRLF %d / 裸LF %d' % (tag, len(b), cr, len(ls) - 1 - cr))
    return b, cr


# ---------- ① REFERENCE：表 ID 补全（4 → 6 表 + 快照页） ----------
rb, rcr = stat(REF, 'REF.before')
rs = rb.decode('utf-8')

old_r1 = '- 空间 `iLE1Cu3WbF0SM1XGCZTSaT`；权威页 `X5wIHjW7h05MMVlL2i34ba`；旧页'
new_r1 = '- 空间 `iLE1Cu3WbF0SM1XGCZTSaT`；权威页 `X5wIHjW7h05MMVlL2i34ba`；**数据快照页 `OuIVbXUEGn1oG72I74wT3q`**；旧页'
assert rs.count(old_r1) == 1, 'REF 权威页行命中 %d' % rs.count(old_r1)
rs = rs.replace(old_r1, new_r1)

old_r2 = '- 4 表：待办 `jXSNAphTmjKYhdWjMJV6oM` / 排期 `UcSbMf8BXQQjx06jvOM7To` / 店铺 `Vdd0Fs70cCWYWUNaWDOpfY` / 岗位台账 `AobUABfhPgihosDP4kJcHf`。'
new_r2 = ('- **6 表**：待办 `jXSNAphTmjKYhdWjMJV6oM` / 排期 `UcSbMf8BXQQjx06jvOM7To` / 店铺 `Vdd0Fs70cCWYWUNaWDOpfY` / '
          '**笔记明细 `rC5M6ZpFotkzyCLJ3SVPr2`** / **每日复盘 `QQG7aeUbL9a1ytGAtHwFKs`** / 岗位台账 `AobUABfhPgihosDP4kJcHf`。')
assert rs.count(old_r2) == 1, 'REF 4表行命中 %d' % rs.count(old_r2)
rs = rs.replace(old_r2, new_r2)

open(REF, 'wb').write(rs.encode('utf-8'))
rb2 = open(REF, 'rb').read()
ls2 = rb2.split(b'\n')
print('REF.after %d B (%+d) / %s / CRLF %d / 裸LF %d'
      % (len(rb2), len(rb2) - len(rb), hashlib.md5(rb2).hexdigest(),
         sum(1 for l in ls2 if l.endswith(b'\r')), len(ls2) - 1 - sum(1 for l in ls2 if l.endswith(b'\r'))))

# ---------- ② MEMORY：再压 ----------
mb, mcr = stat(MEM, 'MEM.before')
ms = mb.decode('utf-8')
pairs = []

# (a) §7 表 ID 两行 → 一行索引
pairs.append((
    '- 🔴🔴 **权威数据=工作台**（页 `X5wIHjW7h05MMVlL2i34ba` + 5 表 + 快照 `OuIVbXUEGn1oG72I74wT3q`）。\n'
    '- 表 ID：待办 `jXSNAphTmjKYhdWjMJV6oM`／排期 `UcSbMf8BXQQjx06jvOM7To`／店铺 `Vdd0Fs70cCWYWUNaWDOpfY`／笔记明细 `rC5M6ZpFotkzyCLJ3SVPr2`／每日复盘 `QQG7aeUbL9a1ytGAtHwFKs`／岗位台账 `AobUABfhPgihosDP4kJcHf`。\n'
    '- 🔴 带类型键写（`{"状态":{"select":"已发"}}`）；回读用 `query_database_record`。（细节见 REFERENCE §C）',
    '- 🔴🔴 **权威数据=工作台**：权威页／快照页／**6 表 ID**／带类型键写＋`query_database_record` 回读 → **全见 `REFERENCE §C`**。'
))

# (b) §10 A3 面板
pairs.append((
    '- 🟢 **A3 面板实读**（存档 `_协作\\_automation_原文\\A3-读卡抽检出卡-2100-20261016.md`）：创建 10/16、**已运行 0 次**、每天 21:00 → 🔴 **A3 是正牌那条、禁止删除**；要停用的是另一条「C21:00 读卡抽检出卡」。',
    '- 🟢 **A3 面板实读**（存档 `_automation_原文\\A3-读卡抽检出卡-2100-20261016.md`）：创建 10/16、已运行 0 次、每天 21:00 → 🔴 **A3 是正牌、禁删**；要停用的是「C21:00 读卡抽检出卡」。'
))

# (c) §10 automation 跨实例边界
pairs.append((
    '- 🔴 **automation 跨实例边界（WB199 实测）**：C 侧 `a1`／`a2`／`a2-2`／`a3-21-00` 在 W 实例全部 `view` not found → **C 侧任务不在 W 实例管辖**；须由 C 侧自查完成，**在此之前回执＋台账即有效载体**。',
    '- 🔴 **automation 跨实例边界（WB199 实测）**：C 侧 `a1`／`a2`／`a2-2`／`a3-21-00` 在 W 实例全部 `view` not found → **C 侧任务不归 W 管**，须 C 侧自查；在此之前**回执＋台账即有效载体**。'
))

# (d) §4 写法数据压缩
pairs.append((
    '- **写法 > 方向**（B 级）：评论率中位 B 0.171 > A 0.113 > C 0.064；写法 ①清单 0.250／④第一人称 0.191／②单家 0.108／③反直觉 0.075（最差）→ **C 用④**。🔴 拉数必清洗（「26届」=中高考生／赞0=接口截断）。',
    '- **写法 > 方向**（B 级）：评论率中位 B 0.171 > A 0.113 > C 0.064；写法 **①清单 0.250 最优／④第一人称第二／③反直觉 0.075 最差** → **C 用④**。🔴 拉数必清洗（「26届」=中高考生／赞0=接口截断）。'
))

# (e) §8 定价依据压缩
pairs.append((
    '- 🔴 **定价依据（红狐 A-）**：高价档天花板由「人群宽度」定（跨人群中位 10000 vs 执行工具 1428）；工具是窄需求、资料是宽需求；付费对象＝内容非工具。',
    '- 🔴 **定价依据（红狐 A-）**：高价档天花板由「人群宽度」定（跨人群中位 10000 vs 工具 1428）；付费对象＝内容非工具。'
))

# (f) §6 后台三屏压缩
pairs.append((
    '- 🆕 **后台三屏（L 10/17 08:55 · S 级 · 逐篇明细见发布台账 §七）**：粉丝 **1,098**／关注 50／获赞收藏 **638**｜🔴 **未见「账号异常」橙标**（10/16 有，待 L 确认）｜来源＝首页推荐 80%／搜索 8%／主页 3%／其他 9%（与 10/16「新增**粉丝**来源·搜索 91.8%」是**不同指标**，不冲突）｜10-16 A＝57 最高，10-17 A＝审核中；**评＝1 均系自发首评，用户评＝0**。',
    '- 🆕 **后台三屏（L 10/17 08:55 · S 级 · 逐篇见发布台账 §七）**：粉丝 **1,098**／关注 50／赞藏 **638**｜🔴 **未见「账号异常」橙标**（10/16 有，待 L 确认）｜来源＝首页推荐 80%／搜索 8%／主页 3%／其他 9%（与 10/16「**新增粉丝**来源·搜索 91.8%」是不同指标）｜10-16 A＝57 最高，10-17 A＝审核中；**评＝1 均系自发首评，用户评＝0**。'
))

# (g) §10 三级口径 ⑤ 压缩
pairs.append((
    '⑤ 🔴 **红线第 4 条 v2**：**不得以账号身份让 AI 操控运营号小 L** 发笔记/评论/点赞/关注/私信/采集，**只能 L 本人手动**；红狐等其他账号采公开数据不在禁区；C／W 的 automation 不碰账号**继续不受限**；🟡 采集需小 L 登录态 → 停、报 L。',
    '⑤ 🔴 **红线第 4 条 v2**：**不得以账号身份让 AI 操控运营号小 L** 发/评/赞/关注/私信/采集，**只能 L 本人手动**；红狐等账号采公开数据不在禁区；C／W 的 automation 不碰账号**不受限**；🟡 需小 L 登录态 → 停、报 L。'
))

# (h) §7 驾驶舱 6 区 微压
pairs.append((
    '**每次刷新必覆盖 6 区**：**①步骤条 ②排期表 ③「今日三层发布」三卡片（W-A50 漏此区）④数据快照日期＋权威源版本号（≥3 处）⑤主表 KPI／水位／ROWS 剩余天数＋chips ⑥事件页＋页脚**。',
    '**每次必覆盖 6 区**：**①步骤条 ②排期表 ③「今日三层发布」三卡片（W-A50 漏此区）④快照日期＋权威源版本号（≥3 处）⑤KPI／水位／ROWS 剩余天数＋chips ⑥事件页＋页脚**。'
))

ok = True
for i, (o, n) in enumerate(pairs, 1):
    c = ms.count(o)
    print('  (%s) 命中 %d %s' % ('abcdefgh'[i - 1], c, '✅' if c == 1 else '❌'))
    if c != 1:
        ok = False
if not ok:
    raise SystemExit('命中异常，MEMORY 未写盘')

for o, n in pairs:
    ms = ms.replace(o, n)

open(MEM, 'wb').write(ms.encode('utf-8'))
mb2 = open(MEM, 'rb').read()
ls3 = mb2.split(b'\n')
cr3 = sum(1 for l in ls3 if l.endswith(b'\r'))
han = len([c for c in mb2.decode('utf-8') if '\u4e00' <= c <= '\u9fa5'])
print('\nMEM.after %d B (%+d, from 20815: %.0f%%) / %s / CRLF %d / 裸LF %d / 汉字 %d'
      % (len(mb2), len(mb2) - len(mb), (20815 - len(mb2)) / 20815 * 100,
         hashlib.md5(mb2).hexdigest(), cr3, len(ls3) - 1 - cr3, han))
