# -*- coding: utf-8 -*-
"""C51 §五·3 单独重跑（项1/项2 已完成，不重跑）。"""
import hashlib

p3 = r'_协作/发布包/库存候选/库存-20261017-网申必填项自查.md'
b = open(p3, 'rb').read()
ls = b.split(b'\n')
cr = sum(1 for l in ls if l.endswith(b'\r'))
print('改前 %d B  md5 %s  CRLF %d  BARE_LF %d' % (len(b), hashlib.md5(b).hexdigest(), cr, len(ls) - 1 - cr))

s = b.decode('utf-8')

old = 'T3=**14 字** ≤20 ✅'
assert s.count(old) == 1, '替换串命中 %d 次' % s.count(old)
s = s.replace(old, 'T3=**14 字符（去空格）／12 汉字** ≤20 ✅')

anchor = '**未落桌面包、未发布**（库存稿按看板 #5 只求「已定稿 ≥6 篇滚动」）'
assert s.count(anchor) == 1, '锚点命中 %d 次' % s.count(anchor)
add = ('\n\n> 📌 **C51 §五·3 字数口径统一（2026-10-17 18:5x）**：T3 原写「14 字」，**未写明是汉字数还是去空格字符数**'
       '（同族：同名指标两种算法）。C51 实算＝标题「应届生网申，先核这 3 个必填项」**汉字 12 ＋ 数字「3」＋ 逗号 ＝ 14 字符（去空格）**；'
       '**含 2 个空格为 16 字符**。\n> 已改为「**14 字符（去空格）／12 汉字**」；「≤20」结论不变。'
       '**此后所有新稿一律写「N 字符（去空格）／M 汉字」，不再单写「N 字」。**')
s = s.replace(anchor, anchor + add)

data = s.encode('utf-8')
assert b'\r' not in data, '出现 CR'
open(p3, 'wb').write(data)

b = open(p3, 'rb').read()
ls = b.split(b'\n')
cr = sum(1 for l in ls if l.endswith(b'\r'))
print('改后 %d B  md5 %s  CRLF %d  BARE_LF %d' % (len(b), hashlib.md5(b).hexdigest(), cr, len(ls) - 1 - cr))
t = b.decode('utf-8')
print('残留 "14 字" =', t.count('T3=**14 字**'), '(目标 0)')
print('新 T3 行 →', [l for l in t.split('\n') if 'T3=' in l][0][:120])
