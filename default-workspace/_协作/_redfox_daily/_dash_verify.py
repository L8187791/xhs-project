# -*- coding: utf-8 -*-
import hashlib
p = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
b = open(p, "rb").read()
s = b.decode("utf-8")
print("bytes", len(b), "CRLF", b.count(b"\r\n"), "pureLF", b.count(b"\n") - b.count(b"\r\n"), "md5", hashlib.md5(b).hexdigest())
for k in ["案例五", "WB211", "WB212", "WB202", "WB210", "C46", "C47", "刚刚（秋招版）", "刚刚秋招版"]:
    print("  ", k, s.count(k))
print("div", s.count("<div"), s.count("</div>"))
