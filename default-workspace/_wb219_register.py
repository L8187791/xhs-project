# -*- coding: utf-8 -*-
r"""WB219 取号即登记（write-ahead）"""
import hashlib

IDX = r"D:\小红书项目\default-workspace\_协作\卡索引.md"
b = open(IDX, "rb").read()
ls = b.split(b"\n")
cr = sum(1 for l in ls if l.endswith(b"\r"))
assert cr == 0, "索引非纯 LF，中止"
assert b"WB219" not in b, "WB219 已存在，中止（避免撞号）"

before = len(b)
ph = "| XHS-20261017-WB219 | 回执卡 | 进行中（占位 · 取号即登记 · C 层已发落账） | W→C(抄送L) | 🟡 进行中 |"
if not b.endswith(b"\n"):
    b += b"\n"
b = (b.decode("utf-8") + ph + "\n").encode("utf-8")
open(IDX, "wb").write(b)

d = open(IDX, "rb").read()
print("bytes %d -> %d  md5 %s  行 %d" % (before, len(d), hashlib.md5(d).hexdigest()[:10], len(d.split(b"\n")) - 1))
