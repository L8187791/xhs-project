# -*- coding: utf-8 -*-
import io
p = r"D:\小红书项目\default-workspace\_协作\推进看板-2026-10.md"
s = io.open(p, encoding="utf-8").read()
b = len(open(p, "rb").read())
lines = s.splitlines()
print("bytes", b, "lines", len(lines), "CRLF", s.count("\r\n"), "pureLF", s.count("\n") - s.count("\r\n"))
for i, L in enumerate(lines[-24:], start=len(lines) - 23):
    print(i, "|", L[:190])
