# -*- coding: utf-8 -*-
# 严谨台账 §三十六 补 W-A54 ＋ 回执卡 §三 同步更正（R9 同批改）
import hashlib

# ---------- ① 严谨台账 ----------
P1 = r'D:\小红书项目\default-workspace\_协作\严谨记录台账-2026-10.md'
b = open(P1, 'rb').read()
old_md5 = hashlib.md5(b).hexdigest()
ls = b.split(b'\n')
assert sum(1 for l in ls if l.endswith(b'\r')) == 0, 'NOT PURE LF'
s = b.decode('utf-8')

anchor = '*本节由 W 于 2026-10-17 14:4x 新增 · 只增不删*'
add = """### L6·补 · 🔴 自身错误 W-A54（本轮唯一返工 · 自检抓出）

**现象**：页脚首次补丁写成「L 的工作台 · 离线单文件版 · 生成于 2026-10-17 **14:4x** by W（内容线 + 数据线）· 本次刷新：B 层已发落账（WB215）」→ `驾驶舱时效自检.py` 报 **1/34 不符**（页脚 生成日期＝**未找到**）。

**根因**：自检判据为 `生成于 (\\d{4}-\\d{2}-\\d{2}) by W`——日期须**紧跟** `by W`；我在中间插入「14:4x」，判据失配。**R2**（改页面前未核自检判据的匹配串，凭「这句话加个时点更清楚」直接改）。

**处置（改页面不改检查器）**：
1. 页脚**还原为原格式**「生成于 2026-10-17 by W（内容线 + 数据线）<br>」；
2. 刷新时点**移到第四行独立追加**：`<br>🕐 最近刷新 <b>2026-10-17 14:4x</b>：B 层 12:30 场已发落账（WB215）`；
3. 重跑自检 → **34/34 ✅**。

**为何不改判据**：页脚日期格式是**稳定沿用多轮的约定串**，放宽判据＝给自己开口子，会重演 **W-A51**（检查器自己坏了、误报/漏报）。**检查器的价值在拦截力，不在通过率。**

**连带更正**：本卡 §三 与回执卡 §三 原写「本轮无新增自身错误编号」，**已同批改为 W-A54**（R9：一处改、多处同步）。

"""
c = s.count(anchor)
print('① 台账锚点命中 =', c)
assert c == 1
s = s.replace(anchor, add + anchor)
b2 = s.encode('utf-8')
open(P1, 'wb').write(b2)
b3 = open(P1, 'rb').read()
ls3 = b3.split(b'\n')
cr3 = sum(1 for l in ls3 if l.endswith(b'\r'))
print('台账 %d → %d B (+%d) / %s / CRLF %d / 裸LF %d'
      % (len(b), len(b3), len(b3) - len(b), hashlib.md5(b3).hexdigest(), cr3, len(ls3) - 1 - cr3))
print('W-A54 =', b3.decode('utf-8').count('W-A54'))

# ---------- ② 回执卡 §三 ----------
P2 = r'D:\小红书项目\default-workspace\_协作\outbox\回执卡-XHS-20261017-WB215-B层已发落账.md'
c2 = open(P2, 'rb').read()
c2s = c2.decode('utf-8')
old3 = '**本轮无新增自身错误编号。** 三点说明（不虚增、不虚减）：'
new3 = ('**本轮 1 条：W-A54**（页脚改动破坏自检判据 → 改页面不改检查器，重跑 34/34 ✅ · 详见 §2.4 与严谨台账 §三十六·L6·补）。'
        '另三点说明（不虚增、不虚减）：')
n = c2s.count(old3)
print('\n② 回执卡 §三 命中 =', n)
assert n == 1
c2s = c2s.replace(old3, new3)
open(P2, 'wb').write(c2s.encode('utf-8'))
c3 = open(P2, 'rb').read()
print('回执卡 %d → %d B / W-A54 = %d' % (len(c2), len(c3), c3.decode('utf-8').count('W-A54')))
