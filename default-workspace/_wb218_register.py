# -*- coding: utf-8 -*-
r"""WB218 取号即登记（write-ahead）：向 卡索引.md 追加占位行"""
import hashlib

IDX = r"D:\小红书项目\default-workspace\_协作\卡索引.md"
b = open(IDX, "rb").read()
ls = b.split(b"\n")
cr = sum(1 for l in ls if l.endswith(b"\r"))
assert cr == 0, "索引不是纯 LF，中止"
assert b"WB218" not in b, "WB218 已存在，中止（避免撞号）"

before = len(b)
ph = "| XHS-20261017-WB218 | 回执卡 | 进行中（占位 · 取号即登记 · L 四项裁定的落账） | W→C(抄送L) | 🟡 进行中 |"
if not b.endswith(b"\n"):
    b += b"\n"
b = (b.decode("utf-8") + ph + "\n").encode("utf-8")
open(IDX, "wb").write(b)

d = open(IDX, "rb").read()
ls2 = d.split(b"\n")
cr2 = sum(1 for l in ls2 if l.endswith(b"\r"))
print("bytes %d -> %d" % (before, len(d)))
print("md5", hashlib.md5(d).hexdigest()[:10], "CRLF", cr2, "行", len(ls2) - 1)
print("末行:", d.decode("utf-8").split("\n")[-2][:110])
