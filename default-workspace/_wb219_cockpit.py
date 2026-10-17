# -*- coding: utf-8 -*-
r"""WB219：驾驶舱 C 层已发同步（读最新 → 改 → 写 → 校验 → 桌面同源）"""
import hashlib, re, shutil

SRC = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
DESK = r"C:\Users\Administrator\Desktop\L 的工作台.html"

b0 = open(SRC, "rb").read()
md5_b0 = hashlib.md5(b0).hexdigest()
ls0 = b0.split(b"\n")
cr0 = sum(1 for l in ls0 if l.endswith(b"\r"))
print("改前 %d B  md5 %s  CRLF %d  裸LF %d" % (len(b0), md5_b0, cr0, len(ls0) - 1 - cr0))
assert b"\r\n" in b0

s = b0.decode("utf-8").replace("\r\n", "\n")
pairs = []

# ① 步骤条
pairs.append((
    "· C 层 20:30（稿已就绪）",
    "· C 层 20:30：<b>🟢 已发（L 20:3x 上报 · 332 汉字 · 红狐 0 · 桌面件↔正本四项逐字比对全一致 → 发布版本＝定稿版本，无返工）</b>"
))

# ② C 卡 note
pairs.append((
    '<div class="note">🟢 <b>稿已就绪（待 20:30 发）</b> · 标题《往届生能投的，我按公告口径分了三类》· 正文 332 汉字 · <b>红狐 0 命中</b> · 闸门 P0=P1=P2=0。往届口径一律以<b>公告原文</b>为准（表内标「往届」31 家，含部分招往届）。</div>',
    '<div class="note">🟢 <b>已发（L 20:3x 上报「C层已发」· 精确时刻未给）</b> · 标题《往届生能投的，我按公告口径分了三类》'
    '（<b>17 字符（去空格）／16 汉字</b>）· 正文 <b>332 汉字</b>（7 段）· 标签 8 个 · <b>红狐 0 命中</b> · 闸门 P0=P1=P2=0 · '
    '桌面件↔正本<b>四项逐字比对全一致</b>（md5 标题 45dbe5e7／正文 b222b561／标签 dabf4172／首评 700e3ca3）→ <b>无返工</b>。'
    '首评＝「还没开始翻公告的往届生，你现在盯着哪一类？」（24 汉字·<b>L 发完 30 分钟后 ≈21:0x 手动发</b>，已与正文 CTA 错开不撞）。'
    '往届口径一律以<b>公告原文</b>为准（表内标「往届」31 家，含部分招往届）。</div>'
))

# ③ 排期表 C 行
pairs.append((
    '<td>往届可投口径三分类 · ①清单式</td><td><span class="tag gr">稿已就绪（332 汉字·红狐 0）</span></td>',
    '<td>往届可投口径三分类 · ①清单式</td><td><span class="tag g">🟢 已发（20:30 场）</span></td>'
))

ok = []
for old, new in pairs:
    c = s.count(old)
    assert c == 1, "锚点命中 %d 次（应为 1）: %s" % (c, old[:60])
    s = s.replace(old, new, 1)
    ok.append(old[:40])

# ④ 页脚刷新行（正则，因他方可能已改）
m = re.search(r"🕐 最近刷新 <b>[^<]*</b>：[^\n]*", s)
assert m, "页脚刷新行未找到"
old_footer = m.group(0)
new_footer = ("🕐 最近刷新 <b>2026-10-17 20:4x</b>：**C 层 20:30 已发落账（WB219）**——三项今日发布全部完成（A 08:54／B 12:xx／C 20:3x）→ "
              "四项逐字比对全一致·首评 ≈21:0x 待 L 手动发 ‖ 上轮 20:1x L 四项裁定落账（WB218）")
s = s.replace(old_footer, new_footer, 1)
ok.append("页脚（原：" + old_footer[:28] + "）")

out = s.replace("\n", "\r\n").encode("utf-8")
open(SRC, "wb").write(out)

d = open(SRC, "rb").read()
lsd = d.split(b"\n")
crd = sum(1 for l in lsd if l.endswith(b"\r"))
bare = len(lsd) - 1 - crd
if bare:
    d = re.sub(rb"(?<!\r)\n", b"\r\n", d)
    open(SRC, "wb").write(d)
    d = open(SRC, "rb").read()
    lsd = d.split(b"\n")
    crd = sum(1 for l in lsd if l.endswith(b"\r"))
    bare = len(lsd) - 1 - crd
print("改后 %d B  md5 %s  CRLF %d  裸LF %d" % (len(d), hashlib.md5(d).hexdigest(), crd, bare))
print("替换 %d 处：" % len(ok))
for x in ok:
    print("  ·", x)

shutil.copyfile(SRC, DESK)
dk = open(DESK, "rb").read()
print("桌面 %d B 同源=%s" % (len(dk), hashlib.md5(dk).hexdigest() == hashlib.md5(d).hexdigest()))
t = d.decode("utf-8")
print("残留「稿已就绪（待 20:30 发）」:", t.count("稿已就绪（待 20:30 发）"))
print("残留「C 层 20:30（稿已就绪）」:", t.count("C 层 20:30（稿已就绪）"))
