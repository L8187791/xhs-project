# -*- coding: utf-8 -*-
# 卡索引：WB215 占位行 → 定稿行（纯 LF · 整行替换）
import hashlib

P = r'D:\小红书项目\default-workspace\_协作\卡索引.md'

b = open(P, 'rb').read()
old_size = len(b)
old_md5 = hashlib.md5(b).hexdigest()
lines = b.split(b'\n')
cr = sum(1 for l in lines if l.endswith(b'\r'))
assert cr == 0, 'NOT PURE LF: %d' % cr
assert b.endswith(b'\n')

s = b.decode('utf-8')
ls = s.split('\n')
hits = [i for i, l in enumerate(ls) if l.startswith('| XHS-20261017-WB215 |')]
print('WB215 行命中 =', len(hits), 'at', hits)
assert len(hits) == 1, '占位行定位异常'

FINAL = ('| XHS-20261017-WB215 | 回执卡 | '
         '**10/17 B 层已发落账**（L 2026-10-17 14:3x 上报「B层在12点多已发」，未提供精确时刻 · W 14:4x 实读取证后落账）。'
         '**① 四项逐字程序化比对全一致**（正则抽取＋去空白后 md5，非目测）：'
         '标题 md5 双方同 **`b727e116`**（「应届生别只盯截止日，有人提前关」**14 汉字＋1 逗号＝15 字符** ≤20 ✅）／'
         '标签 md5 同 **`3c576349`**（**8 个**）／首评 md5 同 **`b412e669`**（**29 汉字** · 人群点名型）／'
         '正文去空白后逐字相同（**325 汉字** 300–600 ✅ · 结尾问句 ✅）'
         '→ **✅ 发布版本＝定稿版本（WB208 专家复核后版 · 红狐 word_count 2→0），本轮无返工**。'
         '**② 双源字节**：桌面 `待发包-20261017-ABC层/2-B层-文案-1230发.txt` **1,606 B ／ md5 `ac6682997d5b13bb5fc06747bafaa6a7` ／ CRLF** ↔ '
         '正本 `发布包\\2026-10-17\\笔记-XHS-20261017-WB-B层.md` **1,585 B ／ md5 `8179295e58d75b265b4623a7be534e6a` ／ 纯 LF**；'
         '**21 B 差＝包根格式差（首行/分隔行/脚注/段落单双空行），非内容差**。'
         '**③ 内容合规**：零家数零企业名断言（处罚期）／无链接无商品／首评与正文 CTA 错开 ／12:30 时段「12 点多」未越界下午场。'
         '**④ 落点 8 处全实写并回验**：发布台账 §六 B 行（稿就绪→**已发** · **26,260→28,789 B** · md5 `a45f877e…`→`e4cb94ec…`）／'
         '§六·补 标题改「**（10/17 A／B 层）**」＋表格加 B 行／§六·补 后新增「**10/17 B 层取证说明**」块（四项比对＋21B 成因＋未取到四项＋时段合规）／'
         '严谨台账 **§三十六**（L1–L6 · **119,396→122,568 B** · md5 `6e3deabf…`→`977e95b1…`）／看板 **#50**（**92,794→93,855 B**）／卡索引本行／回执卡本卡／驾驶舱 6 区。'
         '**⑤ 取号即登记生效**：摘要口径曾拟取 WB214，**双源核对发现已被 B2 14:00 场占用**（其卡面明写「未取到 B 层是否已发」）→ 改取 **215** 并**先写占位行再做正文**，'
         '撞号窗口由分钟级压到秒级，**本轮无撞号**。'
         '🔴 **未取到四项一律留白不推断**：精确发布时刻（只给「12 点多」· 不代填 12:30:00）／平台过审状态／「AI辅助」角标／首日曝光观看。'
         '**本轮无新增自身错误编号；未发请判卡**。⏳ 24h 回传＝**10/18 12:30 后** | W→L，抄送 C | 🟢 已发 |')

ls[hits[0]] = FINAL
s2 = '\n'.join(ls)
b2 = s2.encode('utf-8')
open(P, 'wb').write(b2)

b3 = open(P, 'rb').read()
lines3 = b3.split(b'\n')
cr3 = sum(1 for l in lines3 if l.endswith(b'\r'))
print('\nSIZE %d -> %d (%+d)' % (old_size, len(b3), len(b3) - old_size))
print('MD5  %s -> %s' % (old_md5, hashlib.md5(b3).hexdigest()))
print('CRLF_LINES', cr3, 'BARE_LF', len(lines3) - 1 - cr3, '=>', 'PURE LF OK' if cr3 == 0 else 'MIXED!')
print('行数 =', len(lines3) - 1)
print('🚧 残留 =', b3.decode('utf-8').count('🚧 进行中'))
print('WB215 =', b3.decode('utf-8').count('WB215'))
print('末行 WB215 在尾部 =', 'WB215' in lines3[-2].decode('utf-8'))
