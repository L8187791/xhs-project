# -*- coding: utf-8 -*-
import hashlib
BT = chr(96)
p = r'D:/Documents/2026-10-13-05-08-45/.workbuddy/memory/MEMORY.md'
old = ('- 🔴 **动工前先扫 inbox（W-A56）**：C51 落卡后 **3.8h 未读**才被 L 触发 → 每次动工前 ' + BT + 'ls -1t inbox' + BT +
       ' 取最新 3 件，收工再查一次未读。')
new = old + '（🟢 **C52 已改判为「节奏认知」非错误**：C/W 场次错位的结构性结果；非紧急卡可等下一场，紧急卡由 L 转达。）'
b = open(p, 'rb').read()
assert b'\r' not in b
s = b.decode('utf-8')
n = s.count(old)
print('命中', n)
assert n == 1
open(p, 'wb').write(s.replace(old, new).encode('utf-8'))
b2 = open(p, 'rb').read()
print('改后 %d B  md5 %s  CR=%s' % (len(b2), hashlib.md5(b2).hexdigest(), b'\r' in b2))
