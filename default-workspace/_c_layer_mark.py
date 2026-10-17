# -*- coding: utf-8 -*-
"""把 C 层稿内过期的「待渲染」标记改为已渲染事实（内容零变更）。"""
import hashlib
BT = chr(96)
p = r'_协作/发布包/2026-10-17/笔记-XHS-20261017-WB-C层.md'
old = '⏳ 待渲染（big / list / big），出图前先过 ' + BT + 'ganhuo_lib.py' + BT + ' strict 校验'
new = ('✅ 已渲染并同步桌面（图1_big ／图2_list ／图3_big，2026-10-17 07:29:46；'
       '与桌面 `图-C层-往届口径/图1.png·图2.png·图3.png` 字节一致：84,788／130,910／79,510 B）；'
       '出图前已过 ' + BT + 'ganhuo_lib.py' + BT + ' strict 校验。'
       '**内容零变更**（标题／正文／首评／标签／图内文字均未动）→ 三关结论继续有效。')
b = open(p, 'rb').read()
print('改前 %d B  md5 %s' % (len(b), hashlib.md5(b).hexdigest()))
assert b'\r' not in b
s = b.decode('utf-8')
n = s.count(old)
print('命中', n)
assert n == 1
open(p, 'wb').write(s.replace(old, new).encode('utf-8'))
b2 = open(p, 'rb').read()
print('改后 %d B  md5 %s  CR=%s' % (len(b2), hashlib.md5(b2).hexdigest(), b'\r' in b2))
s2 = b2.decode('utf-8')
L = s2.split('\n')
print('正文汉字复算 =', len([c for c in '\n'.join(L[8:21]) if '\u4e00' <= c <= '\u9fa5']))
print('标题 =', L[5], '| 汉字', len([c for c in L[5] if '\u4e00' <= c <= '\u9fa5']), '| 字符(去空格)', len(L[5].replace(' ', '')))
