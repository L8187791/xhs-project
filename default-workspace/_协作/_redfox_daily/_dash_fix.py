# -*- coding: utf-8 -*-
"""修正驾驶舱 CARDS：我方条目 WB211→WB212；补入他实例 WB211 条目。单次读改写＋校验。"""
import hashlib

P = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
b0 = open(P, "rb").read()
s = b0.decode("utf-8")
print("BEFORE bytes", len(b0), "CRLF", b0.count(b"\r\n"), "pureLF", b0.count(b"\n") - b0.count(b"\r\n"), "md5", hashlib.md5(b0).hexdigest())

A = " ['WB211','回执 · **B1 09:00 场**"
print("anchor", s.count(A))
assert s.count(A) == 1, "anchor not unique"

NEW = (" ['WB211','回执 · **驾驶舱「今日三层发布」全页刷新**（L 09:07 指出页面仍为 10/16 → 前提复核成立：08:5x 漏改详情页）。"
       "改 27 处 ＋ ROWS 140 行重算（依 v1.0.27 实跑）；其声明终态 153,785 B／md5 `880892a0…`／CRLF 1167／纯 LF 0／桌面同源 "
       "（🔴 该 md5 已被本场 WB212 的纯追加**顺延取代**，见下条）','g','已交付'],\r\n"
       " ['WB212','回执 · **B1 09:00 场**")

s2 = s.replace(A, NEW, 1)
b1 = s2.encode("utf-8")
open(P, "wb").write(b1)
print("AFTER  bytes", len(b1), "CRLF", b1.count(b"\r\n"), "pureLF", b1.count(b"\n") - b1.count(b"\r\n"), "md5", hashlib.md5(b1).hexdigest())
for k in ["案例五", "'WB211'", "'WB212'", "WB202", "C47"]:
    print("  ", k, s2.count(k))
