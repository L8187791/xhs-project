# -*- coding: utf-8 -*-
r"""WB219：清除正文区历史 ** 误用（纯显示层，不改任何数字/结论）"""
import hashlib, shutil

SRC = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
DESK = r"C:\Users\Administrator\Desktop\L 的工作台.html"

b = open(SRC, "rb").read()
md5b = hashlib.md5(b).hexdigest()
s = b.decode("utf-8")
old = "**🟢 已裁定（C31 · 10-16）**"
n = s.count(old)
print("命中", n)
assert n == 1, "命中数异常"
s = s.replace(old, "<b>🟢 已裁定（C31 · 10-16）</b>")

open(SRC, "wb").write(s.encode("utf-8"))
d = open(SRC, "rb").read()
lsd = d.split(b"\n")
crd = sum(1 for l in lsd if l.endswith(b"\r"))
print("%d -> %d B  md5 %s -> %s  CRLF %d 裸LF %d" % (len(b), len(d), md5b[:10], hashlib.md5(d).hexdigest()[:10], crd, len(lsd) - 1 - crd))
shutil.copyfile(SRC, DESK)
print("桌面同源=%s" % (hashlib.md5(open(DESK, "rb").read()).hexdigest() == hashlib.md5(d).hexdigest()))
print("正文区 ** 残留:", d.decode("utf-8").split("<script")[0].count("**"))
