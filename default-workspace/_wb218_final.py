# -*- coding: utf-8 -*-
r"""WB218 收尾：MEMORY 驾驶舱基线更新 ＋ 日志补自检结论 ＋ 回执卡行尾实测"""
import hashlib, os

# ---- MEMORY 驾驶舱基线 ----
M = r"D:\Documents\2026-10-13-05-08-45\.workbuddy\memory\MEMORY.md"
b = open(M, "rb").read()
assert b"\r" not in b
s = b.decode("utf-8")
old = "**164,415 B ／ md5 `7c3ffdf1e7ee1f4a2615ce4746db6b10` ／ CRLF 1216 ／ 纯 LF 0**（WB215 后）"
new = "**164,781 B ／ md5 `e9b0ee90f0bd3806729ee746542de0e4` ／ CRLF 1216 ／ 纯 LF 0**（WB218 后）"
c = s.count(old)
print("MEMORY 基线锚点命中", c)
if c == 1:
    s = s.replace(old, new, 1)
    open(M, "wb").write(s.encode("utf-8"))
    d = open(M, "rb").read()
    print("  MEMORY →", len(d), "B  md5", hashlib.md5(d).hexdigest()[:10], "CRLF", d.count(b"\r"))
else:
    print("  ⚠️ 基线未更新（锚点不唯一），留待人工核")

# ---- 日志补自检 ----
L = r"D:\小红书项目\default-workspace\.workbuddy\memory\2026-10-17.md"
lb = open(L, "rb").read()
cr = sum(1 for l in lb.split(b"\n") if l.endswith(b"\r"))
print("日志 CRLF", cr)
add = ("- 撞号自检：无撞号、无漏登；报 **WB217 空头登记（近期·硬）** —— 非本场造成（B3 20:00 场 20:02:45 取号、红狐查词在途），"
       "W 不删他方占位、不接管号，登记观察至 21:00\n")
if not lb.endswith(b"\n"):
    lb += b"\n"
if "WB217 空头登记" not in lb.decode("utf-8"):
    open(L, "wb").write(lb + add.encode("utf-8"))
    print("  日志已补，", len(open(L, "rb").read()), "B")
else:
    print("  日志已有该行，跳过")

# ---- 回执卡行尾实测 ----
for p in [r"D:\小红书项目\default-workspace\_协作\outbox\回执卡-XHS-20261017-WB218-L四项裁定落账.md"]:
    pb = open(p, "rb").read()
    ls = pb.split(b"\n")
    cr2 = sum(1 for l in ls if l.endswith(b"\r"))
    print("回执卡 %d B  md5 %s  CRLF %d  裸LF %d" % (len(pb), hashlib.md5(pb).hexdigest()[:10], cr2, len(ls) - 1 - cr2))
