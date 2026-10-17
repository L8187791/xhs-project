# -*- coding: utf-8 -*-
import hashlib
BT = chr(96)
p = r'_协作/严谨记录台账-2026-10.md'
old = '✅ 10,049 B／' + BT + 'bc7c5bd0…' + BT + '／纯 LF'
new = '✅ 11,139 B／' + BT + '88533844…' + BT + '／纯 LF 153（补 W-A57 后复测）'
b = open(p, 'rb').read()
assert b'\r' not in b
s = b.decode('utf-8')
assert s.count(old) == 1, s.count(old)
open(p, 'wb').write(s.replace(old, new).encode('utf-8'))
b2 = open(p, 'rb').read()
print('改后 %d B  md5 %s  CR=%s' % (len(b2), hashlib.md5(b2).hexdigest(), b'\r' in b2))
print('残留 10,049 =', b2.decode('utf-8').count('10,049'))
