# -*- coding: utf-8 -*-
"""干货配图库 v2：4 套版式（大字报 / 清单 / 对比 / 步骤）。账号页眉已按后台实名。

🔴 v2 视觉统一（2026-10-14 L 选 A 方案）：
  ① 全篇统一米白底（lay_list 由深黑 DARK 改 PAPER）
  ② 页脚统一黑底白字（lay_list 原 bg=RED 已改默认 INK）
  ③ 左竖条统一 RED（lay_steps 原 INK 已改 RED）
  ④ 字体换免费商用：Noto Sans SC（SIL OFL），替代微软雅黑
  ⑤ render() 强校验图序 = 1:big → 2:list → 3:big
"""
import os
from PIL import Image, ImageDraw, ImageFont

# 🔴 v2：换用 Noto Sans SC（SIL Open Font License，可商用），替代微软雅黑（方正规）
BOLD = r"C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf"
REG = r"C:\Windows\Fonts\Noto Sans SC Medium (TrueType).otf"
W, H = 1080, 1440
PAPER = (250, 247, 242); INK = (32, 29, 27); RED = (200, 41, 41)
DARK = (28, 26, 24); WHITE = (255, 255, 255); GREY = (138, 130, 122); SOFT = (76, 70, 64)
ACCOUNT = "小L整理求职资料"   # 2026-10-12 批次2：原「求职时间表研究所」已废弃；仍会被 _account_name.txt 覆盖，仅作最终回落（取 txt 实测值保持全链一致）


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if d.textlength(cur + ch, font=fnt) <= max_w:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_account_name.txt")
if os.path.exists(ACCOUNT_FILE):
    _n = io.open(ACCOUNT_FILE, encoding="utf-8").read().strip() if False else open(ACCOUNT_FILE, encoding="utf-8").read().strip()
    if _n:
        ACCOUNT = _n


def draw_title(d, lines, fnt, y, x, fill, max_seg=3, leading=1.3):
    """2026-10-12 修（同根因）：标题行超出安全宽度时自动折行，最多 max_seg 段，超出截断。
       原lay_big/list/compare/steps 四版式均直接d.text 直绘标题，长标题右侧出血被截断。
       2026-10-14 修：调用方传字符串时（如 spec["title"]）按单行标题处理——
       此前字符串被逐字迭代成竖排，每字一行挤掉列表/正文区（10/15 A/B 层图2 实测踩中）。"""
    if isinstance(lines, str):
        lines = [lines]
    step = int(fnt.size * leading)
    max_w = W - 196                      # 安全宽度：与 B 店 ganhuo_b_lib 对齐
    for ln in (lines or []):
        segs = wrap(d, ln, fnt, max_w) or [""]
        for j, seg in enumerate(segs[:max_seg]):
            d.text((x, y), seg, font=fnt, fill=fill)
            y += step
        if len(segs) > max_seg:          # 截断保护：段数超限则不再往下画
            y += step * (max_seg - len(segs[:max_seg]))
    return y


def header(d, account=None):
    d.text((92, 84), account or ACCOUNT, font=F(BOLD, 32), fill=GREY)


def footer(d, text, bg=INK, fg=WHITE):
    # 2026-10-11 修：footer 传空串时不再画一条空色带（此前会留一条无字黑/红色条，像 bug）
    if not text:
        return
    d.rectangle([0, H - 132, W, H], fill=bg)
    # 2026-10-12 修（同根因）：footer 过长时截断，避免超出画布右界
    f = F(BOLD, 38); s = text
    while d.textlength(s, font=f) > W - 200 and len(s) > 1:
        s = s[:-1]
    if s != text:
        s = s[:-1] + "…" if len(s) > 1 else text[:1]
    d.text((92, H - 100), s, font=f, fill=fg)


def lay_big(spec, path):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 24, H], fill=RED)
    header(d, spec.get("account"))   # 2026-10-12 批次2：透传 spec.account，实现 A/B 店页眉隔离
    if spec.get("badge"):
        f = F(BOLD, 46); bw = d.textlength(spec["badge"], font=f)
        d.rounded_rectangle([W - 92 - bw - 48, 72, W - 92, 72 + 82], radius=16, fill=RED)
        d.text((W - 92 - bw - 24, 88), spec["badge"], font=f, fill=WHITE)
    size = spec.get("size", 104)
    f_main = F(BOLD, size); y = spec.get("top", 340)
    y = draw_title(d, spec["title"], f_main, y, 92, RED, max_seg=3, leading=1.36)   # 2026-10-12 加宽度护栏
    d.rectangle([92, y + 34, 292, y + 42], fill=INK)
    f_sub = F(REG, 44); y2 = y + 96
    for ln in wrap(d, spec.get("sub", ""), f_sub, W - 200)[:3]:
        d.text((92, y2), ln, font=f_sub, fill=SOFT); y2 += 62
    footer(d, spec.get("footer", ""))
    im.save(path, quality=95)


def lay_list(spec, path):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)   # 🔴v2：统一米白底（原 DARK 深黑）
    d.rectangle([0, 0, 24, H], fill=RED)                            # 🔴v2：补左竖条，与 lay_big 统一
    header(d, spec.get("account"))   # 2026-10-12 批次2：透传 spec.account
    hs = spec.get("hsize", 84)
    f_h = F(BOLD, hs); y = spec.get("top", 230)
    y = draw_title(d, spec["title"], f_h, y, 92, INK, max_seg=3, leading=1.3)   # 🔴v2：白字→黑字
    d.rectangle([92, y + 30, 250, y + 38], fill=RED)
    y += 104
    f_n = F(BOLD, 54); f_i = F(REG, 46); f_t = F(BOLD, 46)
    for i, item in enumerate(spec["items"], 1):
        d.text((92, y), "%02d" % i, font=f_n, fill=RED)
        d.text((232, y), item.get("t", ""), font=f_t, fill=INK)     # 🔴v2：白字→黑字
        yy = y + (58 if item.get("t") else 0)
        for ln in wrap(d, item.get("d", ""), f_i, W - 340)[:3]:
            d.text((232, yy), ln, font=f_i, fill=SOFT); yy += 56     # 🔴v2：浅灰(214,208,200)→SOFT
        y = yy + 38
    footer(d, spec.get("footer", ""))                                # 🔴v2：页脚统一黑底（原 bg=RED 红底）
    im.save(path, quality=95)


def lay_compare(spec, path):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 24, H], fill=RED)                            # 🔴v2：补左竖条，与其他版式统一
    header(d, spec.get("account"))   # 2026-10-12 批次2：透传 spec.account
    hs = spec.get("hsize", 78)
    f_h = F(BOLD, hs); y = 210
    y = draw_title(d, spec["title"], f_h, y, 92, INK, max_seg=3, leading=1.3)   # 2026-10-12 加宽度护栏
    d.rectangle([92, y + 18, 250, y + 26], fill=RED)
    y += 76
    col_w = (W - 184 - 36) // 2
    for idx, col in enumerate(spec["cols"]):
        x = 92 + idx * (col_w + 36)
        bad = col["kind"] == "bad"
        d.rounded_rectangle([x, y, x + col_w, y + 92], radius=14,
                            fill=(214, 76, 76) if bad else (44, 122, 87))
        d.text((x + 30, y + 22), col["head"], font=F(BOLD, 46), fill=WHITE)
        yy = y + 118
        f_b = F(REG, 38)
        for it in col["items"]:
            for ln in wrap(d, it, f_b, col_w - 40)[:3]:
                d.text((x + 8, yy), ln, font=f_b, fill=SOFT); yy += 52
            yy += 20
    footer(d, spec.get("footer", ""))
    im.save(path, quality=95)


def lay_steps(spec, path):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 24, H], fill=RED)                            # 🔴v2：左竖条 INK→RED，与其他版式统一
    header(d, spec.get("account"))   # 2026-10-12 批次2：透传 spec.account
    f_h = F(BOLD, spec.get("hsize", 84)); y = 220
    y = draw_title(d, spec["title"], f_h, y, 92, INK, max_seg=3, leading=1.3)   # 2026-10-12 加宽度护栏
    d.rectangle([92, y + 16, 250, y + 24], fill=RED)
    y += 88
    f_n = F(BOLD, 50); f_t = F(BOLD, 44); f_d = F(REG, 40)
    for i, st in enumerate(spec["steps"], 1):
        d.ellipse([92, y, 160, y + 68], fill=INK)
        n = str(i); tw = d.textlength(n, font=f_n)
        d.text((92 + 34 - tw / 2, y + 8), n, font=f_n, fill=WHITE)
        d.text((188, y + 6), st["t"], font=f_t, fill=INK)
        yy = y + 66
        for ln in wrap(d, st.get("d", ""), f_d, W - 300)[:3]:
            d.text((188, yy), ln, font=f_d, fill=SOFT); yy += 48
        y = yy + 40
    footer(d, spec.get("footer", ""))
    im.save(path, quality=95)


LAYOUTS = {"big": lay_big, "list": lay_list, "compare": lay_compare, "steps": lay_steps}

# 🔴 v2（2026-10-14 L 选 A 方案）：图序硬性规范 = 1:big → 2:list → 3:big
ORDER_SPEC = [(1, "big"), (2, "list"), (3, "big")]


def check_order(note):
    """校验图序。返回问题列表（空 = 合规）。"""
    problems = []
    imgs = note.get("images") or []
    if not imgs:
        return ["note 无 images"]
    for pos, want in ORDER_SPEC:
        if pos > len(imgs):
            break
        got = imgs[pos - 1].get("kind")
        if got != want:
            problems.append("图%d 应为 %s，实际 %s" % (pos, want, got))
    if len(imgs) > len(ORDER_SPEC):
        problems.append("超出规范：共 %d 张，规范只定义 %d 张" % (len(imgs), len(ORDER_SPEC)))
    return problems


def render(note, outdir, strict=True):
    """strict=True（默认）：强校验图序 1:big→2:list→3:big，不合规直接 raise。
       strict=False：跳过校验（内容确需 steps/compare 时显式关闭，会打 WARN）。"""
    probs = check_order(note)
    if probs and strict:
        raise ValueError("图序不合规（%s）：%s —— 确需其他版式请显式传 strict=False"
                         % (note.get("no"), "；".join(probs)))
    if probs:
        print("WARN 图序偏离规范（strict=False 已放行）：", "；".join(probs))
    os.makedirs(outdir, exist_ok=True)
    paths = []
    acct = note.get("account") or None          # 2026-10-12 批次2：note 级 account（A/B 店隔离）
    for i, spec in enumerate(note["images"], 1):
        spec = dict(spec)                        # 2026-10-12 批次2：浅拷贝，避免污染调用方对象
        if acct and not spec.get("account"):     # 2026-10-12 批次2：note 级回落到每个 spec
            spec["account"] = acct
        p = os.path.join(outdir, "%s_图%d_%s.png" % (note["no"], i, spec["kind"]))
        LAYOUTS[spec["kind"]](spec, p)
        paths.append(p)
        print("SAVED", os.path.basename(p))
    return paths
