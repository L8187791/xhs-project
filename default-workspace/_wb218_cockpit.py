# -*- coding: utf-8 -*-
r"""WB218：驾驶舱补丁（L 四项裁定）· 读改写同脚本 · CRLF 保持 · 桌面同源"""
import hashlib, re, shutil, os

SRC = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
DESK = r"C:\Users\Administrator\Desktop\L 的工作台.html"

b0 = open(SRC, "rb").read()
md5_b0 = hashlib.md5(b0).hexdigest()
ls0 = b0.split(b"\n")
cr0 = sum(1 for l in ls0 if l.endswith(b"\r"))
print("改前 %d B  md5 %s  CRLF %d  裸LF %d" % (len(b0), md5_b0, cr0, len(ls0) - 1 - cr0))
assert b"\r\n" in b0, "源非 CRLF，中止"

# 用 LF 归一后的文本做替换（W-A50：多行匹配前必须归一）
s = b0.decode("utf-8").replace("\r\n", "\n")

pairs = []

# ① 倒计时目标 15:58 → 16:00
pairs.append(('var target=new Date("2026-10-19T15:58:00")',
              'var target=new Date("2026-10-19T16:00:00")'))

# ② 发布纪律标题
pairs.append(("发布纪律（处罚期，至 10/19 15:58）",
              "发布纪律（处罚期，至 10/19 16:00 解禁）"))

# ③ 步骤条：大盘口径冲突 → 结案
old3 = ("｜⚠️ <b>近7日大盘口径冲突待 L 澄清</b>：曝光 <b>2.5万 vs 1.7万</b>／观看 <b>4,775 vs 2,938</b>／"
        "CTR <b>19.9% vs 18.5%</b>（旧数压基线 20.02%、新数低于基线）→ <b>两套数并列留痕、不擅自改</b>")
new3 = ("｜🟢 <b>近7日大盘口径已结案</b>（L 20:0x）：曝光按<b>滚动 7 天</b>统计，"
        "2.5万（10-09~10-15）vs 1.7万（10-10~10-16）＝<b>窗口起点不同、非数据错误</b> → "
        "<b>禁跨窗口比较、禁算环比</b>（原 -31%／-28% 等<b>全部作废</b>）；"
        "CTR 两窗口 19.9%／18.5% <b>均未站上 20.02%</b>；🆕 <b>报 7 日数必写窗口起止日</b>")
pairs.append((old3, new3))

# ④ 风险清单：报白 → 下周出结果
pairs.append(("· 报白审核结果未出 → 驳回则 10/19 上架不成立<br>",
              "· 报白<b>下周才出结果</b>（L 20:0x）→ 等通知；10/20–22 提交窗是否顺延<b>由 L 定</b><br>"))

# ⑤ 风险清单：处罚期解禁加时点
pairs.append(("· 处罚期违规内容删除未收口（6/10）→ 直接影响解禁<br>",
              "· 处罚期违规内容删除未收口（6/10）→ 直接影响解禁（<b>10/19 16:00</b>）<br>"))

# ⑥ 页脚刷新行（状态用「→」记录轨迹）
old6 = "🕐 最近刷新 <b>2026-10-17 14:4x</b>：B 层 12:30 场已发落账（WB215）"
new6 = ("🕐 最近刷新 <b>2026-10-17 20:1x</b>：L 四项裁定落账（WB218）——处罚期至 <b>10/19 16:00</b>／"
        "大盘口径结案（窗口位移·禁环比）／报白下周出结果 → 上轮 14:4x B 层落账（WB215）")
pairs.append((old6, new6))

ok = []
for old, new in pairs:
    c = s.count(old)
    assert c == 1, "锚点命中 %d 次（应为 1）: %s" % (c, old[:50])
    s = s.replace(old, new, 1)
    ok.append(old[:34])

# 还原 CRLF
s_crlf = s.replace("\n", "\r\n")
out = s_crlf.encode("utf-8")
open(SRC, "wb").write(out)

# 回读校验
d = open(SRC, "rb").read()
md5_d = hashlib.md5(d).hexdigest()
lsd = d.split(b"\n")
crd = sum(1 for l in lsd if l.endswith(b"\r"))
bare = len(lsd) - 1 - crd
if bare:  # 兜底：把裸 LF 精确补 \r
    d = re.sub(rb"(?<!\r)\n", b"\r\n", d)
    open(SRC, "wb").write(d)
    d = open(SRC, "rb").read()
    lsd = d.split(b"\n")
    crd = sum(1 for l in lsd if l.endswith(b"\r"))
    bare = len(lsd) - 1 - crd
    md5_d = hashlib.md5(d).hexdigest()
print("改后 %d B  md5 %s  CRLF %d  裸LF %d" % (len(d), md5_d, crd, bare))
print("已替换 %d 处:" % len(ok))
for x in ok:
    print("  ·", x)

# 同步桌面
shutil.copyfile(SRC, DESK)
dk = open(DESK, "rb").read()
print("桌面 %d B  md5 %s  同源=%s" % (len(dk), hashlib.md5(dk).hexdigest()[:12], hashlib.md5(dk).hexdigest() == hashlib.md5(d).hexdigest()))
