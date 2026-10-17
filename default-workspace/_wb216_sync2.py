# -*- coding: utf-8 -*-
"""同步回执卡最终字节到索引与台账（避免 inline 反引号被 shell 吞）。"""
import hashlib
BT = chr(96)  # 反引号，规避任何 shell 预处理
old = '✅ 10,049 B／' + BT + 'bc7c5bd0…' + BT + '／纯 LF'
new = '✅ 11,139 B／' + BT + '88533844…' + BT + '／纯 LF 153（补 W-A57 后复测）'
for p in (r'_协作/卡索引.md', r'_协作/严谨记录台账-2026-10.md'):
    b = open(p, 'rb').read()
    assert b'\r' not in b, '非纯 LF'
    s = b.decode('utf-8')
    c = s.count(old)
    print('%-22s 命中 %d' % (p.split('/')[-1], c))
    assert c == 1, '命中数不为 1，中止（未写盘）'
    open(p, 'wb').write(s.replace(old, new).encode('utf-8'))
    b2 = open(p, 'rb').read()
    print('   改后 %d B  md5 %s  CR存在=%s' % (len(b2), hashlib.md5(b2).hexdigest(), b'\r' in b2))
