# -*- coding: utf-8 -*-
"""C52 裁定同步：W-A56 改判「节奏认知」，三处加注（只增不删）。"""
import hashlib
BT = chr(96)
NOTE = ('\n> 📌 **C52 裁定同步（2026-10-17 20:0x · 只增不删）**：C52 §三 已把本条**改判为「节奏结构」而非错误**——'
        'C51 15:11 落卡 → W 下一场 20:00，3.8–4.8h 滞后＝C/W 场次错位的结构性结果。'
        '**不计入错误台账，改登记为「节奏认知」**；规则：非紧急卡接受等到 W 下一场，紧急卡由 L 一句话转达；C 发卡尽量赶在 W 场次（08:5x／13:5x／19:5x／22:5x）之前。'
        '**「动工前先扫 inbox」的机制保留**（它是预防手段，与定性无关）。')

targets = [
    (r'_协作/严谨记录台账-2026-10.md',
     '- **W-A56**｜C51 落卡 **15:11**，我至 **18:5x** 才动（L 说「看下群聊」才盘 inbox），**滞后 3.8 小时**。根因：手工线无兜底扫卡动作，全依赖定时任务与 L 口头指令。已加：**每次动工前先 ' + BT + 'ls -1t inbox' + BT + ' 取最新 3 件**；收工自检加「inbox 是否仍有未读」。'),
    (r'_协作/outbox/回执卡-XHS-20261017-WB216-C51前三项更正.md',
     '| **复查** | 下一轮动工（10/18 首场）验证是否执行到位 |'),
]
for p, anchor in targets:
    b = open(p, 'rb').read()
    assert b'\r' not in b, '非纯 LF：' + p
    s = b.decode('utf-8')
    n = s.count(anchor)
    print('%-46s 锚点命中 %d' % (p.split('/')[-1], n))
    assert n == 1, '中止（未写盘）'
    s = s.replace(anchor, anchor + NOTE)
    open(p, 'wb').write(s.encode('utf-8'))
    b2 = open(p, 'rb').read()
    print('   改后 %d B  md5 %s  CR=%s' % (len(b2), hashlib.md5(b2).hexdigest()[:8], b'\r' in b2))

# MEMORY：改定性（只增不删，追加括注）
p = r'D:/Documents/2026-10-13-05-08-45/.workbuddy/memory/MEMORY.md'
old = '- 🔴 **动工前先扫 inbox（W-A56）**：C51 落卡后 **3.8h 未读**才被 L 触发 → 每次动工前 ' + BT + 'ls -1t inbox' + BT + ' 取最新 3 件，收工再查一次。'
new = old + '（🟢 **C52 已改判为「节奏认知」非错误**：C/W 场次错位的结构性结果；非紧急卡可等下一场，紧急卡由 L 转达。）'
b = open(p, 'rb').read()
assert b'\r' not in b
s = b.decode('utf-8')
n = s.count(old)
print('%-46s 锚点命中 %d' % ('MEMORY.md', n))
assert n == 1
open(p, 'wb').write(s.replace(old, new).encode('utf-8'))
b2 = open(p, 'rb').read()
print('   改后 %d B  md5 %s  CR=%s' % (len(b2), hashlib.md5(b2).hexdigest()[:8], b'\r' in b2))
