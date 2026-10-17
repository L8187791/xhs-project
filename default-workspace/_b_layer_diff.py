# -*- coding: utf-8 -*-
# B 层：桌面发布件 vs 发布包正本 逐字比对
import hashlib, re, os

DESK = r'C:\Users\Administrator\Desktop\待发包-20261017-ABC层\2-B层-文案-1230发.txt'
SRC = r'D:\小红书项目\default-workspace\_协作\发布包\2026-10-17\笔记-XHS-20261017-WB-B层.md'


def stat(p):
    b = open(p, 'rb').read()
    lines = b.split(b'\n')
    cr = sum(1 for l in lines if l.endswith(b'\r'))
    bare = len(lines) - 1 - cr
    eol = 'CRLF' if cr and bare == 0 else ('LF' if cr == 0 else '混合 CRLF=%d LF=%d' % (cr, bare))
    return b, hashlib.md5(b).hexdigest(), len(b), eol, cr, bare


db, dmd5, dsz, deol, dcr, dbare = stat(DESK)
sb, smd5, ssz, seol, scr, sbare = stat(SRC)
print('DESK %d B md5=%s eol=%s' % (dsz, dmd5, deol))
print('SRC  %d B md5=%s eol=%s' % (ssz, smd5, seol))

dt = db.decode('utf-8').replace('\r\n', '\n')
st = sb.decode('utf-8').replace('\r\n', '\n')

# 正文抽取：桌面件为「标题: / 正文: / 标签: / 首评:」结构；正本为 md
def norm(s):
    s = re.sub(r'\s+', '', s)
    return s


han = lambda s: len(re.findall(r'[\u4e00-\u9fa5]', s))

print('\n--- 桌面件全文 ---')
print(dt)
print('--- 正本全文 ---')
print(st)

# 逐字：取桌面正文核心段与正本正文核心段
print('\n--- 关键行 ---')
for ln in dt.split('\n'):
    if ln.startswith(('标题', '标签', '首评', '字数', '—', '===')):
        print('[D]', ln)
