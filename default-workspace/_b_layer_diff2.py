# -*- coding: utf-8 -*-
# B 层细项逐字核（程序化，不靠目测）
import hashlib, re

DESK = r'C:\Users\Administrator\Desktop\待发包-20261017-ABC层\2-B层-文案-1230发.txt'
SRC = r'D:\小红书项目\default-workspace\_协作\发布包\2026-10-17\笔记-XHS-20261017-WB-B层.md'

dt = open(DESK, 'rb').read().decode('utf-8').replace('\r\n', '\n')
st = open(SRC, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def grab(text, start_pat, end_pat):
    i = re.search(start_pat, text).end()
    j = re.search(end_pat, text[i:]).start() + i
    seg = text[i:j]
    seg = re.sub(r'━+', '', seg)
    seg = re.sub(r'\*\*', '', seg)
    return seg.strip()


d_title = grab(dt, r'━━━ 标题 ━━━', r'━━━ 正文 ━━━')
s_title = grab(st, r'\*\*标题（≤20 字）\*\*', r'\*\*正文\*\*')
d_body = grab(dt, r'━━━ 正文 ━━━', r'━━━ 标签 ━━━')
s_body = grab(st, r'\*\*正文\*\*', r'\*\*标签\*\*')
d_tag = grab(dt, r'━━━ 标签 ━━━', r'━━━ 置顶首评')
s_tag = grab(st, r'\*\*标签\*\*', r'\*\*置顶首评\*\*')
d_cm = grab(dt, r'━━━ 置顶首评（发完 30 分钟后手动发）━━━', r'\Z')
s_cm = grab(st, r'\*\*置顶首评\*\*', r'\*\*配图\*\*')


def strip_ws(s):
    return re.sub(r'\s+', '', s)


def han(s):
    return len(re.findall(r'[\u4e00-\u9fa5]', s))


rows = [
    ('标题', d_title, s_title),
    ('正文', d_body, s_body),
    ('标签', d_tag, s_tag),
    ('首评', d_cm, s_cm),
]
allok = True
for name, d, s in rows:
    ok = strip_ws(d) == strip_ws(s)
    allok = allok and ok
    print('%-4s %s | 桌面 %d 汉字 %d B(md5 %s) | 正本 %d 汉字 %d B(md5 %s)'
          % (name, '✅一致' if ok else '❌不一致',
             han(d), len(d.encode()), hashlib.md5(d.encode()).hexdigest()[:8],
             han(s), len(s.encode()), hashlib.md5(s.encode()).hexdigest()[:8]))
    if not ok:
        for k in range(min(len(strip_ws(d)), len(strip_ws(s)))):
            if strip_ws(d)[k] != strip_ws(s)[k]:
                print('   首个差异 @%d: 桌面[%s] vs 正本[%s]'
                      % (k, strip_ws(d)[k:k + 20], strip_ws(s)[k:k + 20]))
                break
        else:
            print('   长度差:', len(strip_ws(d)), len(strip_ws(s)))

print('\n标题字数 =', han(d_title), '（≤20 判据 ' + ('✅' if han(d_title) <= 20 else '❌') + '）')
print('正文汉字 =', han(d_body), '（300–600 判据 ' + ('✅' if 300 <= han(d_body) <= 600 else '❌') + '）')
print('末段问句 =', '✅' if d_body.rstrip().endswith('？') else '❌')
print('标签数  =', len(d_tag.split()), '个')
print('首评字数 =', han(d_cm))
print('\n总判 =', '✅ 桌面件与正本逐字一致' if allok else '❌ 存在差异')
