# -*- coding: utf-8 -*-
import io
p = r"D:\小红书项目\default-workspace\_协作\推进看板-2026-10.md"
s = io.open(p, encoding="utf-8").read()
print("LF", s.count("\n"), "CRLF", s.count("\r\n"))
# 找 §四 提案表末行
import re
for m in re.finditer(r"^\| 2026-10-16 \| .*$", s, re.M):
    pass
lines = s.split("\n")
# 打印 §四 提案区附近
for i, L in enumerate(lines):
    if "互相读卡产出，每周至少一条" in L:
        print("HEADER at", i + 1)
        for j in range(i, min(i + 30, len(lines))):
            print(j + 1, "|", lines[j][:150])
        break
print("---- tail 6 ----")
for j in range(len(lines) - 6, len(lines)):
    print(j + 1, "|", lines[j][:170])
