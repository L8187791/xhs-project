# -*- coding: utf-8 -*-
# 修正：页脚保持「生成于 YYYY-MM-DD by W」原格式，时点移至第四行（不改自检判据）
import hashlib, re, shutil

SRC = r'D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html'
DESK = r'C:\Users\Administrator\Desktop\L 的工作台.html'

b = open(SRC, 'rb').read()
old_size = len(b)
old_md5 = hashlib.md5(b).hexdigest()
s = b.decode('utf-8')

# ① 页脚第一行还原（去时点）
o1 = 'L 的工作台 · 离线单文件版 · 生成于 2026-10-17 14:4x by W（内容线 + 数据线）· 本次刷新：B 层已发落账（WB215）<br>'
n1 = 'L 的工作台 · 离线单文件版 · 生成于 2026-10-17 by W（内容线 + 数据线）<br>'
c1 = s.count(o1)
print('① 页脚行还原 命中', c1, '✅' if c1 == 1 else '❌')
assert c1 == 1
s = s.replace(o1, n1)

# ② 第四行末尾追加刷新时点
o2 = '不攒批、只增不删（依据 <span class="mono">_协作\\工作台维护规则-W全责-20261014.md</span>）'
n2 = ('不攒批、只增不删（依据 <span class="mono">_协作\\工作台维护规则-W全责-20261014.md</span>）'
      '<br>🕐 最近刷新 <b>2026-10-17 14:4x</b>：B 层 12:30 场已发落账（WB215）')
c2 = s.count(o2)
print('② 第四行追加 命中', c2, '✅' if c2 == 1 else '❌')
assert c2 == 1
s = s.replace(o2, n2)

b2 = s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')
open(SRC, 'wb').write(b2)

b3 = open(SRC, 'rb').read()
ls3 = b3.split(b'\n')
cr3 = sum(1 for l in ls3 if l.endswith(b'\r'))
bare3 = len(ls3) - 1 - cr3
if bare3:
    b3 = re.sub(rb'(?<!\r)\n', b'\r\n', b3)
    open(SRC, 'wb').write(b3)
    b3 = open(SRC, 'rb').read()
    ls3 = b3.split(b'\n')
    cr3 = sum(1 for l in ls3 if l.endswith(b'\r'))
    bare3 = len(ls3) - 1 - cr3
    print('🔧 兜底归一')

txt = b3.decode('utf-8')
m = re.search(r'生成于 (\d{4}-\d{2}-\d{2}) by W', txt)
print('\nAFTER %d B (%+d) / %s / CRLF %d / 裸LF %d' % (len(b3), len(b3) - old_size,
                                                     hashlib.md5(b3).hexdigest(), cr3, bare3))
print('页脚判据命中 =', m.group(1) if m else '未找到')
print('刷新时点行 =', txt.count('🕐 最近刷新'))

shutil.copy2(SRC, DESK)
db = open(DESK, 'rb').read()
print('桌面同源 =', '✅' if hashlib.md5(db).hexdigest() == hashlib.md5(b3).hexdigest() else '❌', len(db), 'B')
