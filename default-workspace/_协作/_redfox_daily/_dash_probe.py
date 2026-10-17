# -*- coding: utf-8 -*-
"""驾驶舱更新：① 追加「案例五 · 刚刚（秋招版）」 ② 卡片流补账 WB202–WB211 / C44–C47
保持 CRLF 行尾；改后打印 CRLF/纯LF/字节数/md5（与 md5 对照口径一致）"""
import io, hashlib, sys

P = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
b0 = open(P, "rb").read()
s = b0.decode("utf-8")
crlf0 = b0.count(b"\r\n"); lf0 = b0.count(b"\n")
print("BEFORE bytes=%d CRLF=%d pureLF=%d md5=%s" % (len(b0), crlf0, lf0 - crlf0, hashlib.md5(b0).hexdigest()))

A1 = '      </div>\n    </div>\n\n    <div class="panel">\n      <h2><span class="dot"></span>日常机制与审核线'
print("anchor1 count =", s.count(A1))
print("anchor2 count =", s.count("const CARDS=[\n"))
