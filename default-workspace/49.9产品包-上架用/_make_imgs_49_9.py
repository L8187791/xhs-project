# -*- coding: utf-8 -*-
"""
49.9 产品图（3 张，3:4）
风格：清爽 / 求职向 / 不花哨（与 19.9 同色系，形成产品家族感）
配色：浅底米白 + 深蓝 #1F3864 主色 + 红 #C00000 仅作强调
铁律：汉字 -> Source Han Serif SC Heavy；英数/标点 -> Noto Sans SC
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1242, 1656
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04 产品图")
os.makedirs(OUT, exist_ok=True)

NAVY = (31, 56, 100)
NAVY_L = (74, 111, 165)
RED = (192, 0, 0)
GOLD = (176, 141, 74)      # 49.9 用一点暖金作档位区分（克制，只用于价格牌描边）
INK = (34, 38, 45)
GRAY = (122, 131, 145)
LGRAY = (176, 184, 196)
BG = (250, 251, 253)
BG2 = (241, 244, 249)
BG3 = (232, 238, 247)
LINE = (208, 215, 229)
WHITE = (255, 255, 255)

HAN = r"C:\Windows\Fonts\Source Han Serif SC Heavy (TrueType).ttf"
LAT_B = r"C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf"
LAT_M = r"C:\Windows\Fonts\Noto Sans SC Medium (TrueType).otf"
LAT_R = r"C:\Windows\Fonts\Noto Sans SC (TrueType).otf"

_cache = {}
def F(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]

def han(s): return F(HAN, s)
def latb(s): return F(LAT_B, s)
def latm(s): return F(LAT_M, s)
def latr(s): return F(LAT_R, s)

def is_han(ch):
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF) or (0x3400 <= o <= 0x4DBF)

def draw_mixed(d, xy, text, hsize, lsize=None, hcolor=INK, lcolor=None,
               han_fn=han, lat_fn=latb):
    if lsize is None: lsize = hsize
    lcolor = lcolor or hcolor
    x, y = xy
    for ch in text:
        if is_han(ch):
            f = han_fn(hsize); c = hcolor
        else:
            f = lat_fn(lsize); c = lcolor
        d.text((x, y), ch, font=f, fill=c)
        x += d.textlength(ch, font=f)
    return x

def measure(d, text, hsize, lsize=None, han_fn=han, lat_fn=latb):
    if lsize is None: lsize = hsize
    w = 0.0
    for ch in text:
        f = han_fn(hsize) if is_han(ch) else lat_fn(lsize)
        w += d.textlength(ch, font=f)
    return w

def wrap_mixed(d, text, maxw, hsize, lsize=None, han_fn=han, lat_fn=latb):
    lines, cur = [], ""
    for ch in text:
        if measure(d, cur + ch, hsize, lsize, han_fn, lat_fn) > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def canvas():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)

def top_brand(d, price="49.9"):
    x, y = 92, 96
    d.text((x, y), "小 L 整理求职资料", font=latb(38), fill=GRAY)
    f = latb(52)
    tw = d.textlength(price, font=f)
    pw, ph = tw + 72, 88
    box = (W - 92 - pw, y - 14, W - 92, y - 14 + ph)
    rrect(d, box, 20, fill=RED)
    d.text((W - 92 - pw + 36, y - 14 + 16), price, font=f, fill=WHITE)

def bottom_bar(d, text, size=40):
    bh = 116
    d.rectangle((0, H - bh, W, H), fill=NAVY)
    fs = size
    while fs > 26 and measure(d, text, fs, fs, han, latb) > W - 144:
        fs -= 2
    tw = measure(d, text, fs, fs, han, latb)
    draw_mixed(d, ((W - tw) / 2, H - bh + (bh - fs) / 2 - 6), text, fs, fs, WHITE, WHITE)

def sidebar(d):
    d.rectangle((0, 0, 14, H), fill=NAVY)


# ============================================================
# 图 1 · 主图：突出「分行业清单 + 每周更新」
# ============================================================
def fig1():
    img, d = canvas()
    sidebar(d); top_brand(d)
    L = 160

    y = 300
    draw_mixed(d, (L, y), "分行业截止清单包", 128, 128, NAVY, NAVY)
    y += 186
    draw_mixed(d, (L, y), "银行 · 互联网 · 央国企", 88, 88, NAVY_L, NAVY_L)

    y += 150
    d.rectangle((L, y, L + 132, y + 10), fill=RED)

    y += 86
    for line, col in [
        ("三个行业，各一份独立清单", INK),
        ("每周刷新一次「还能投几家」", INK),
    ]:
        draw_mixed(d, (L, y), line, 52, 52, col, col)
        y += 84

    # 三行业卡片
    y += 90
    cards = [("银行", "17 家", "大行已截止\n中小行还在招"),
             ("互联网", "15 家", "大厂滚动招\n招满即止"),
             ("央国企", "53 家", "战线最长\n持续到年底")]
    cw = (W - 2 * L - 2 * 30) // 3
    chh = 300
    for i, (name, cnt, desc) in enumerate(cards):
        x = L + i * (cw + 30)
        rrect(d, (x, y, x + cw, y + chh), 20, fill=BG2, outline=LINE, width=2)
        # 顶条
        rrect(d, (x, y, x + cw, y + 12), 20, fill=NAVY)
        d.rectangle((x, y + 8, x + cw, y + 12), fill=NAVY)
        draw_mixed(d, (x + 30, y + 46), name, 52, 52, NAVY, NAVY)
        draw_mixed(d, (x + 30, y + 122), cnt, 68, 68, RED, RED)
        ty = y + 214
        for ln in desc.split("\n"):
            draw_mixed(d, (x + 30, ty), ln, 30, 30, GRAY, GRAY, han, latr)
            ty += 42

    bottom_bar(d, "每周更新一次 · 到 2027 年 4 月春招结束")
    p = os.path.join(OUT, "49.9产品_图1_主图.png")
    img.save(p, "PNG"); print("saved", p, img.size)


# ============================================================
# 图 2 · 内容预览（三份清单缩略展示）
# ============================================================
def fig2():
    img, d = canvas()
    sidebar(d); top_brand(d)
    L = 160

    y = 320
    draw_mixed(d, (L, y), "你会拿到什么", 96, 96, NAVY, NAVY)
    y += 150
    d.rectangle((L, y, L + 132, y + 10), fill=RED)

    y += 100
    # 三份清单缩略（模拟表格）
    panels = [
        ("银行篇.xlsx", "17 家", ["江西裕民银行  10/24",
                                 "兴业银行  10/25",
                                 "浙商银行  10/25",
                                 "宁波银行  10/31",
                                 "＋ 大行历史参考组"]),
        ("互联网篇.xlsx", "15 家", ["网易  10/20",
                                   "蚂蚁集团  10/30",
                                   "美团  10/31",
                                   "小红书  11/08",
                                   "＋ 6 家滚动招聘"]),
        ("央国企篇.xlsx", "53 家", ["中国五矿  10/19",
                                   "国家管网  10/20",
                                   "中国电信  10/20",
                                   "中国石化  10/15",
                                   "＋ 14 家滚动招聘"]),
    ]
    ph = 278
    gap = 24
    for i, (title, cnt, rows) in enumerate(panels):
        py = y + i * (ph + gap)
        # 卡片
        rrect(d, (L, py, W - L, py + ph), 18, fill=WHITE, outline=LINE, width=2)
        # 左侧色条
        d.rectangle((L, py + 12, L + 10, py + ph - 12), fill=NAVY)
        # 标题
        draw_mixed(d, (L + 40, py + 22), title, 42, 42, INK, INK)
        # 家数徽章
        bw = measure(d, cnt, 34, 34, han, latb) + 44
        rrect(d, (W - L - 30 - bw, py + 24, W - L - 30, py + 24 + 56), 14, fill=BG3)
        draw_mixed(d, (W - L - 30 - bw + 22, py + 36), cnt, 34, 34, NAVY, NAVY)
        # 行
        ty = py + 88
        for r_ in rows:
            draw_mixed(d, (L + 40, ty), r_, 30, 30, GRAY, GRAY, han, latr)
            ty += 36

    bottom_bar(d, "三份 Excel · 可编辑 · 每条附投递入口")
    p = os.path.join(OUT, "49.9产品_图2_内容预览.png")
    img.save(p, "PNG"); print("saved", p, img.size)


# ============================================================
# 图 3 · 对比图（19.9 vs 49.9）
# ============================================================
def fig3():
    img, d = canvas()
    sidebar(d); top_brand(d)
    L = 160

    y = 300
    draw_mixed(d, (L, y), "19.9 和 49.9", 96, 96, NAVY, NAVY)
    y += 132
    draw_mixed(d, (L, y), "差在哪", 96, 96, NAVY, NAVY)
    y += 148
    d.rectangle((L, y, L + 132, y + 10), fill=RED)

    y += 76
    colw = (W - 2 * L - 40) // 2
    x1, x2 = L, L + colw + 40
    headh = 124

    # 表头
    rrect(d, (x1, y, x1 + colw, y + headh), 16, fill=BG2, outline=LINE, width=2)
    draw_mixed(d, (x1 + 34, y + 22), "19.9 时间表", 42, 42, INK, INK)
    draw_mixed(d, (x1 + 34, y + 74), "一张总表", 30, 30, GRAY, GRAY, han, latr)

    rrect(d, (x2, y, x2 + colw, y + headh), 16, fill=NAVY)
    draw_mixed(d, (x2 + 34, y + 22), "49.9 清单包", 42, 42, WHITE, WHITE)
    draw_mixed(d, (x2 + 34, y + 74), "分行业 + 每周更新", 30, 30, (206, 218, 240), (206, 218, 240), han, latr)

    rows = [
        ("内容形式", "131 家在一张大表", "三个行业各一份"),
        ("筛选", "自己按行业筛", "打开就是你的行业"),
        ("更新", "一次性交付", "每周刷新截止状态"),
        ("历史参考", "无", "已截止大行参考组"),
        ("适合", "随便看看", "要持续跟进的人"),
    ]
    yy = y + headh + 22
    rowh = 134
    for i, (label, a, b) in enumerate(rows):
        r = yy + i * rowh
        # 左卡片
        rrect(d, (x1, r, x1 + colw, r + rowh - 24), 14, fill=WHITE, outline=LINE, width=2)
        draw_mixed(d, (x1 + 24, r + 16), label, 27, 27, LGRAY, LGRAY, han, latr)
        la = wrap_mixed(d, a, colw - 48, 31, 31, han, latm)
        ty = r + 54
        for ln in la:
            draw_mixed(d, (x1 + 24, ty), ln, 31, 31, GRAY, GRAY, han, latm)
            ty += 38
        # 右卡片
        rrect(d, (x2, r, x2 + colw, r + rowh - 24), 14, fill=BG2, outline=LINE, width=2)
        draw_mixed(d, (x2 + 24, r + 16), label, 27, 27, LGRAY, LGRAY, han, latr)
        lb = wrap_mixed(d, b, colw - 68, 31, 31, han, latb)
        ty = r + 54
        for ln in lb:
            d.ellipse((x2 + 24, ty + 13, x2 + 36, ty + 25), fill=NAVY)
            draw_mixed(d, (x2 + 46, ty), ln, 31, 31, INK, INK)
            ty += 38

    bottom_bar(d, "多花 30 块，换分行业 + 每周更新")
    p = os.path.join(OUT, "49.9产品_图3_对比.png")
    img.save(p, "PNG"); print("saved", p, img.size)


if __name__ == "__main__":
    fig1(); fig2(); fig3()
