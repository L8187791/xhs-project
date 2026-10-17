# -*- coding: utf-8 -*-
# 取号即登记（write-ahead）：WB215 占位行入卡索引，纯 LF 追加
import hashlib

P = r'D:\小红书项目\default-workspace\_协作\卡索引.md'

b = open(P, 'rb').read()
before_size = len(b)
before_md5 = hashlib.md5(b).hexdigest()
lines = b.split(b'\n')
cr = sum(1 for l in lines if l.endswith(b'\r'))
assert cr == 0, 'NOT PURE LF: %d' % cr
assert b.endswith(b'\n')

row = ('| XHS-20261017-WB215 | 回执卡 | 🚧 **进行中（取号即登记占位 · 2026-10-17 14:4x）**'
       '：10/17 **B 层 12:30 场已发落账**（L 14:3x 上报「B层在12点多已发」）。'
       '取证与落点补写中，完成后本行整行替换为定稿回执摘要 | W→L，抄送 C | 🚧 进行中 |\n')

b2 = b + row.encode('utf-8')
open(P, 'wb').write(b2)

b3 = open(P, 'rb').read()
lines3 = b3.split(b'\n')
cr3 = sum(1 for l in lines3 if l.endswith(b'\r'))
print('BEFORE', before_size, before_md5)
print('AFTER ', len(b3), hashlib.md5(b3).hexdigest())
print('CRLF_LINES', cr3, 'BARE_LF', len(lines3) - 1 - cr3)
print('WB215_IN', b3.count(b'WB215'))
print('TAIL_OK', b3.endswith(b'\n'))
