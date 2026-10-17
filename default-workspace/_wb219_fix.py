# -*- coding: utf-8 -*-
r"""WB219 修正：页脚 ** 误用（HTML 里会显示星号）→ 改 <b>"""
import hashlib, shutil

SRC = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
DESK = r"C:\Users\Administrator\Desktop\L 的工作台.html"

b = open(SRC, "rb").read()
md5b = hashlib.md5(b).hexdigest()
s = b.decode("utf-8")
old = "🕐 最近刷新 <b>2026-10-17 20:4x</b>：**C 层 20:30 已发落账（WB219）**——"
new = "🕐 最近刷新 <b>2026-10-17 20:4x</b>：<b>C 层 20:30 已发落账（WB219）</b>——"
assert s.count(old) == 1, "锚点命中 %d 次" % s.count(old)
s = s.replace(old, new, 1)
assert "：" + "**" not in s.split("🕐 最近刷新")[1][:200], "仍有 ** 残留"

out = s.encode("utf-8")
open(SRC, "wb").write(out)
d = open(SRC, "rb").read()
lsd = d.split(b"\n")
crd = sum(1 for l in lsd if l.endswith(b"\r"))
print("%d B -> %d B  md5 %s -> %s  CRLF %d 裸LF %d" % (len(b), len(d), md5b[:10], hashlib.md5(d).hexdigest()[:10], crd, len(lsd) - 1 - crd))
shutil.copyfile(SRC, DESK)
print("桌面同源=%s" % (hashlib.md5(open(DESK, "rb").read()).hexdigest() == hashlib.md5(d).hexdigest()))
# 全页 ** 误用体检（正文文本区，非 JS）
t = d.decode("utf-8")
body = t.split("<script")[0]
print("正文区 ** 出现次数:", body.count("**"))
