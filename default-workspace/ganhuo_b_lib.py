# -*- coding: utf-8 -*-
"""B 店（小Z整理考公选岗资料）专属配图库 —— 与 A 店 ganhuo_lib **整套区隔**。

区隔点（B 店同质化判定 §3：封面版式整套不同 → 页眉名必换 + 配色/字体/布局换一套）：
  · 配色：藏青 + 朱红 + 浅蓝灰      （A 店 = 米白 + 正红）
  · 字体：等线 Dengb / Deng          （A 店 = 微软雅黑 msyhbd / msyh）
  · 版式：顶部**通栏色带**页眉 + 圆角卡片 + 圆点序号（A 店 = 左上角灰字页眉 + 直角 + "01" 编号 + 左侧竖条）

隔离纪律：本库**不写任何全局 ACCOUNT**（不碰 ganhuo_lib.ACCOUNT、不读 _account_name.txt）；
         页眉一律由调用方经 note["account"] / spec["account"] 传入。
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1440

# ---------------- B 店配色 ----------------
NAVY    = (26, 42, 74)      # 藏青（主色 / 深底）
NAVY_H  = (20, 33, 60)      # 顶部带（略深）
CRIMSON = (198, 48, 48)     # 朱红（强调）
BG      = (240, 243, 248)   # 浅蓝灰底
CARD    = (255, 255, 255)   # 卡片白
INK     = (26, 42, 74)      # 主文字 = 藏青
GREY    = (122, 130, 146)   # 次级灰
WHITE   = (255, 255, 255)
MUTED   = (200, 208, 222)   # 深底上的浅字
LINE    = (222, 228, 238)   # 浅底描边

# ---------------- B 店字体（等线，与 A 店雅黑区隔）----------------
F_BOLD  = r"C:\Windows\Fonts\Dengb.ttf"
F_REG   = r"C:\Windows\Fonts\Deng.ttf"
F_LIGHT = r"C:\Windows\Fonts\Dengl.ttf"

HEADER_H = 100


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for ch in text or "":
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if d.textlength(cur + ch, font=fnt) <= max_w:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


def header(d, account):
    """B 店页眉：顶部通栏藏青带 + 朱红细线 + 反白账号名 + 右侧朱红方块（A 店无带）"""
    d.rectangle([0, 0, W, HEADER_H], fill=NAVY_H)
    d.rectangle([0, HEADER_H, W, HEADER_H + 7], fill=CRIMSON)
    d.text((88, 26), account or "", font=F(F_BOLD, 34), fill=(224, 231, 242))
    d.rounded_rectangle([W - 128, 30, W - 88, 70], radius=10, fill=CRIMSON)


def footer(d, text, bg=NAVY, fg=WHITE):
    if not text:
        return
    d.rectangle([0, H - 128, W, H], fill=bg)
    d.rectangle([0, H - 128, W, H - 124], fill=CRIMSON)
    d.text((88, H - 96), text, font=F(F_BOLD, 36), fill=fg)


# ============================================================
# 1 · big（封面）：浅蓝灰底 + 顶部带 + 藏青大标题 + 朱红圆角短块
# ============================================================
def lay_big(spec, path):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    header(d, spec.get("account"))
    if spec.get("badge"):
        f = F(F_BOLD, 42); bw = d.textlength(spec["badge"], font=f)
        d.rounded_rectangle([W - 88 - bw - 46, 136, W - 88, 136 + 78], radius=18, fill=CRIMSON)
        d.text((W - 88 - bw - 23, 152), spec["badge"], font=f, fill=WHITE)
    size = spec.get("size", 104)
    f_main = F(F_BOLD, size); y = spec.get("top", 360)
    max_w = W - 196
    for i, ln in enumerate(spec["title"]):
        # 防呆：整行超出安全宽度时自动折行，避免右侧出血/截断
        for j, seg in enumerate(wrap(d, ln, f_main, max_w)):
            d.text((88, y), seg, font=f_main, fill=(CRIMSON if i == 0 and spec.get("first_red") else INK))
            y += int(size * 1.36)
            if j >= 2:  # 最多折 3 段，超出则截断保护
                break
    d.rounded_rectangle([88, y + 34, 268, y + 52], radius=9, fill=CRIMSON)
    f_sub = F(F_REG, 44); y2 = y + 108
    for ln in wrap(d, spec.get("sub", ""), f_sub, W - 196)[:3]:
        d.text((88, y2), ln, font=f_sub, fill=GREY); y2 += 62
    footer(d, spec.get("footer", ""))
    im.save(path, quality=95)


# ============================================================
# 2 · list（清单）：藏青底 + 圆点序号（A 店为 01 编号）
# ============================================================
def lay_list(spec, path):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    header(d, spec.get("account"))
    hs = spec.get("hsize", 80)
    f_h = F(F_BOLD, hs); y = spec.get("top", 250)
    for ln in spec["title"]:
        d.text((88, y), ln, font=f_h, fill=WHITE); y += int(hs * 1.3)
    d.rounded_rectangle([88, y + 30, 228, y + 46], radius=8, fill=CRIMSON)
    y += 116
    f_i = F(F_REG, 44); f_t = F(F_BOLD, 44); f_n = F(F_BOLD, 40)
    for i, item in enumerate(spec["items"], 1):
        # 圆点序号（朱红圆角方块，与 A 店 "01" 数字不同）
        d.rounded_rectangle([88, y, 152, y + 64], radius=18, fill=CRIMSON)
        n = str(i); tw = d.textlength(n, font=f_n)
        d.text((88 + 32 - tw / 2, y + 12), n, font=f_n, fill=WHITE)
        d.text((196, y + 6), item.get("t", ""), font=f_t, fill=WHITE)
        yy = y + 68
        for ln in wrap(d, item.get("d", ""), f_i, W - 320)[:3]:
            d.text((196, yy), ln, font=f_i, fill=MUTED); yy += 54
        y = yy + 34
    footer(d, spec.get("footer", ""), bg=NAVY_H)
    im.save(path, quality=95)


# ============================================================
# 3 · compare（对比）：浅底 + 双栏圆角卡片
# ============================================================
def lay_compare(spec, path):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    header(d, spec.get("account"))
    hs = spec.get("hsize", 76)
    f_h = F(F_BOLD, hs); y = 236
    for ln in spec["title"]:
        d.text((88, y), ln, font=f_h, fill=INK); y += int(hs * 1.3)
    d.rounded_rectangle([88, y + 18, 228, y + 34], radius=8, fill=CRIMSON)
    y += 84
    col_w = (W - 176 - 32) // 2
    for idx, col in enumerate(spec["cols"]):
        x = 88 + idx * (col_w + 32)
        bad = col["kind"] == "bad"
        d.rounded_rectangle([x, y, x + col_w, y + 620], radius=26,
                            fill=CARD, outline=LINE, width=3)
        d.rounded_rectangle([x, y, x + col_w, y + 96], radius=26,
                            fill=(CRIMSON if bad else NAVY))
        d.rectangle([x, y + 62, x + col_w, y + 96], fill=(CRIMSON if bad else NAVY))
        d.text((x + 30, y + 24), col["head"], font=F(F_BOLD, 46), fill=WHITE)
        yy = y + 132
        f_b = F(F_REG, 38)
        for it in col["items"]:
            for ln in wrap(d, it, f_b, col_w - 44)[:3]:
                d.text((x + 24, yy), ln, font=f_b, fill=(64, 74, 96)); yy += 52
            yy += 22
    footer(d, spec.get("footer", ""))
    im.save(path, quality=95)


# ============================================================
# 4 · steps（步骤）：浅底 + 圆角卡片步骤块（A 店为 圆形黑底序号）
# ============================================================
def lay_steps(spec, path):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    header(d, spec.get("account"))
    hsize = spec.get("hsize", 80)
    f_h = F(F_BOLD, hsize); y = 250
    for ln in spec["title"]:
        d.text((88, y), ln, font=f_h, fill=INK); y += int(hsize * 1.3)
    d.rounded_rectangle([88, y + 16, 228, y + 32], radius=8, fill=CRIMSON)
    y += 100
    f_n = F(F_BOLD, 44); f_t = F(F_BOLD, 42); f_d = F(F_REG, 38)
    for i, st in enumerate(spec["steps"], 1):
        d.rounded_rectangle([88, y, W - 88, y + 200], radius=24, fill=CARD, outline=LINE, width=3)
        d.rounded_rectangle([110, y + 28, 190, y + 108], radius=18, fill=NAVY)
        n = str(i); tw = d.textlength(n, font=f_n)
        d.text((110 + 40 - tw / 2, y + 42), n, font=f_n, fill=WHITE)
        d.text((216, y + 34), st["t"], font=f_t, fill=INK)
        yy = y + 100
        for ln in wrap(d, st.get("d", ""), f_d, W - 360)[:3]:
            d.text((216, yy), ln, font=f_d, fill=GREY); yy += 48
        y += 228
    footer(d, spec.get("footer", ""))
    im.save(path, quality=95)


LAYOUTS = {"big": lay_big, "list": lay_list, "compare": lay_compare, "steps": lay_steps}


def render(note, outdir):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    acct = note.get("account") or None
    for i, spec in enumerate(note["images"], 1):
        spec = dict(spec)
        if acct and not spec.get("account"):
            spec["account"] = acct
        p = os.path.join(outdir, "%s_图%d_%s.png" % (note["no"], i, spec["kind"]))
        LAYOUTS[spec["kind"]](spec, p)
        paths.append(p)
        print("SAVED", os.path.basename(p))
    return paths
