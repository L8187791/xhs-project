# -*- coding: utf-8 -*-
# 驾驶舱 6 区同步：B 层「稿已就绪/未取到」→「已发」（读-改-写同脚本 + 写后回读校验）
import hashlib, re, shutil, os

SRC = r'D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html'
DESK = r'C:\Users\Administrator\Desktop\L 的工作台.html'
BAK = r'D:\小红书项目\default-workspace\_协作\_备份\L 的工作台-WB215前-20261017.html'

# ---- 读 ----
b = open(SRC, 'rb').read()
old_size = len(b)
old_md5 = hashlib.md5(b).hexdigest()
ls = b.split(b'\n')
cr = sum(1 for l in ls if l.endswith(b'\r'))
assert cr > 0 and (len(ls) - 1 - cr) == 0, 'HTML 非纯 CRLF: CRLF=%d BARE=%d' % (cr, len(ls) - 1 - cr)
print('BEFORE %d B / %s / CRLF %d / 裸LF 0' % (old_size, old_md5, cr))

# 备份
os.makedirs(os.path.dirname(BAK), exist_ok=True)
shutil.copy2(SRC, BAK)
print('备份 →', BAK, os.path.getsize(BAK), 'B')

s = b.decode('utf-8').replace('\r\n', '\n')  # 内部统一 LF 处理，最后再整体转 CRLF

PATCHES = []

# ---------- ① 步骤条 ----------
o1 = ('B 层 12:30：<b>14:00 实查盘上无任何发布回传证据 → 「未取到」，W 不推断</b>')
n1 = ('B 层 12:30：<b>🟢 已发（L 14:3x 上报「12 点多已发」· 325 汉字 · 红狐 0 · 桌面件↔正本四项逐字比对全一致 → 发布版本＝定稿版本，无返工）</b>')
PATCHES.append(('① 步骤条 B 层', o1, n1))

# ---------- ② B 卡片 note ----------
o2 = ('🟡 <b>12:30 应发 —— 14:00 实查：盘上无任何发布回传证据（11:00 后全库零改动）→ 「未取到」，不推断已发/未发</b>。稿本体已就绪 · 标题《应届生别只盯截止日，有人提前关》· 正文 325 汉字 · <b>红狐 0 命中</b> · 闸门 P0=P1=P2=0。二手标注必回官网核；官网无表述 → 判 C，不落表不入文案。L 回传后 W 落账。')
n2 = ('🟢 <b>已发（12:30 场 · L 14:3x 上报「B层在12点多已发」· W 14:4x 实读取证后落账）</b>。标题《应届生别只盯截止日，有人提前关》· 正文 325 汉字 · <b>红狐 0 命中</b> · 闸门 P0=P1=P2=0。🔴 <b>发布版本＝定稿版本</b>：桌面件（1,606 B／<span class="mono">ac668299</span>／CRLF）↔ 正本（1,585 B／<span class="mono">8179295e</span>／纯 LF）—— 标题 md5 <span class="mono">b727e116</span>／标签 <span class="mono">3c576349</span>／首评 <span class="mono">b412e669</span> 双方相同，正文去空白后逐字同（21 B 差＝包根格式，非内容差）→ <b>无返工</b>。🟡 <b>未取到四项一律留白不推断</b>：精确发布时刻（只给「12 点多」）／平台过审状态／「AI辅助」角标／首日曝光观看。⏳ 24h 回传 <b>10/18 12:30 后</b>。')
PATCHES.append(('② B 卡片 note', o2, n2))

# ---------- ③ 排期表 B 行 ----------
o3 = ('<tr><td>T+0 · 10/17</td><td><span class="tag v">B</span></td><td>12:30</td><td>招满即止口径 · 截止日≠关门日</td><td><span class="tag gr">稿已就绪（325 汉字·红狐 0）</span></td></tr>')
n3 = ('<tr><td>T+0 · 10/17</td><td><span class="tag v">B</span></td><td>12:30</td><td>招满即止口径 · 截止日≠关门日</td><td><span class="tag g">🟢 已发（12:30 场）</span></td></tr>')
PATCHES.append(('③ 排期表 B 行', o3, n3))

# ---------- ④ 页脚时点 ----------
o4 = 'L 的工作台 · 离线单文件版 · 生成于 2026-10-17 by W（内容线 + 数据线）<br>'
n4 = 'L 的工作台 · 离线单文件版 · 生成于 2026-10-17 14:4x by W（内容线 + 数据线）· 本次刷新：B 层已发落账（WB215）<br>'
PATCHES.append(('④ 页脚', o4, n4))

print('\n--- 命中核对 ---')
ok_all = True
for name, o, n in PATCHES:
    c = s.count(o)
    print('%-12s 命中 %d %s' % (name, c, '✅' if c == 1 else '❌'))
    if c != 1:
        ok_all = False
if not ok_all:
    raise SystemExit('存在命中异常，未写盘')

for name, o, n in PATCHES:
    s = s.replace(o, n)

# ---------- 写：整体转 CRLF ----------
s_out = s.replace('\r\n', '\n').replace('\n', '\r\n')
b2 = s_out.encode('utf-8')
open(SRC, 'wb').write(b2)

# ---------- 回验 ----------
b3 = open(SRC, 'rb').read()
ls3 = b3.split(b'\n')
cr3 = sum(1 for l in ls3 if l.endswith(b'\r'))
bare3 = len(ls3) - 1 - cr3
# 兜底归一
if bare3:
    b3 = re.sub(rb'(?<!\r)\n', b'\r\n', b3)
    open(SRC, 'wb').write(b3)
    b3 = open(SRC, 'rb').read()
    ls3 = b3.split(b'\n')
    cr3 = sum(1 for l in ls3 if l.endswith(b'\r'))
    bare3 = len(ls3) - 1 - cr3
    print('🔧 已兜底归一裸 LF')

print('\nAFTER  %d B (+%d) / %s / CRLF %d / 裸LF %d %s'
      % (len(b3), len(b3) - old_size, hashlib.md5(b3).hexdigest(), cr3, bare3,
         '✅' if bare3 == 0 else '❌混合'))
txt = b3.decode('utf-8')
print('「稿已就绪」残留 =', txt.count('稿已就绪'), '（应为 3：C 卡片1 + 排期C行1 + 步骤条C层1）')
print('「未取到」，W 不推断 残留 =', txt.count('「未取到」，W 不推断'))
print('B 卡片已发 =', txt.count('W 14:4x 实读取证后落账'))
print('排期B行已发 =', txt.count('🟢 已发（12:30 场）'))
print('页脚时点 =', txt.count('生成于 2026-10-17 14:4x'))

# ---------- 桌面同源 ----------
shutil.copy2(SRC, DESK)
db = open(DESK, 'rb').read()
print('\n桌面 %d B / %s / 与源同 md5 = %s'
      % (len(db), hashlib.md5(db).hexdigest(),
         '✅' if hashlib.md5(db).hexdigest() == hashlib.md5(b3).hexdigest() else '❌'))
