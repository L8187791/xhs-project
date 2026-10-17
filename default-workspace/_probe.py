# -*- coding: utf-8 -*-
BT = chr(96)
old = '✅ 10,049 B／' + BT + 'bc7c5bd0…' + BT + '／纯 LF'
import glob
for p in (r'_协作/台账' ,):
    pass
for p in (r'_协作/卡索引.md', r'_协作/严谨记录台账-2026-10.md', r'_协作/推进看板-2026-10.md'):
    s = open(p, 'rb').read().decode('utf-8')
    print('%-20s 10,049 命中 %d | bc7c5bd0 命中 %d' % (p.split('/')[-1], s.count('10,049'), s.count('bc7c5bd0')))
    for l in s.split('\n'):
        if '10,049' in l or 'bc7c5bd0' in l:
            print('   →', l[:200])
