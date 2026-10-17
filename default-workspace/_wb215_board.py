# -*- coding: utf-8 -*-
# 推进看板：追加 #50（WB215 · B 层已发落账）· 纯 LF · 只增不删
import hashlib

P = r'D:\小红书项目\default-workspace\_协作\推进看板-2026-10.md'

b = open(P, 'rb').read()
old_size = len(b)
old_md5 = hashlib.md5(b).hexdigest()
lines = b.split(b'\n')
cr = sum(1 for l in lines if l.endswith(b'\r'))
assert cr == 0, 'NOT PURE LF: %d' % cr
if not b.endswith(b'\n'):
    b = b + b'\n'

ROW = ('| 50 | 📌 **10/17 B 层已发落账（WB215）** | W | 🟢 已落账 | '
       'L 14:3x 上报「B层在12点多已发」→ 实读取证后再落账。**四项逐字程序化比对全一致**：'
       '标题 md5 `b727e116`／标签 `3c576349`／首评 `b412e669` 双方同，正文去空白后逐字同（**325 汉字**）'
       '→ **发布版本＝定稿版本，无返工**。桌面件 **1,606 B ／ `ac668299…` ／ CRLF** ↔ '
       '正本 **1,585 B ／ `8179295e…` ／ 纯 LF**（21 B 差＝包根格式，非内容差）。'
       '落点 8 处：发布台账 §六 B 行（稿就绪→**已发**）／§六·补 标题改「A／B 层」＋表加 B 行／'
       '新增「B 层取证说明」块／严谨台账 **§三十六**／卡索引 WB215／本行／回执卡 WB215／驾驶舱 6 区 | '
       '🔴 **未取到四项不推断**：精确发布时刻（只给「12 点多」）／过审状态／「AI辅助」角标／首日数据。'
       '🟢 取号即登记生效：WB214 已被 B2 14:00 场占用，改取 215 并先写占位再落正文，**本轮无撞号**。'
       '⏳ 24h 回传＝**10/18 12:30 后** |\n')

b2 = b + ROW.encode('utf-8')
open(P, 'wb').write(b2)

b3 = open(P, 'rb').read()
lines3 = b3.split(b'\n')
cr3 = sum(1 for l in lines3 if l.endswith(b'\r'))
print('SIZE %d -> %d (+%d)' % (old_size, len(b3), len(b3) - old_size))
print('MD5  %s -> %s' % (old_md5, hashlib.md5(b3).hexdigest()))
print('CRLF_LINES', cr3, 'BARE_LF', len(lines3) - 1 - cr3, '=>', 'PURE LF OK' if cr3 == 0 else 'MIXED!')
print('#50 =', b3.decode('utf-8').count('| 50 |'))
