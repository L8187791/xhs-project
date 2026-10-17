# -*- coding: utf-8 -*-
"""49.9 三份清单 PDF 预览导出（reportlab）"""
import os, json
from datetime import date
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                Spacer, PageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from _clean_note import clean as clean_note

ROOT = r"D:\Documents\deepseek-harness\default-workspace"
SRC = os.path.join(ROOT, "技能包_时间表查询官", "data", "timetable.json")
OUTDIR = os.path.join(ROOT, "49.9产品包-上架用", "03 交付文件")
OUTPDF = os.path.join(OUTDIR, "49.9产品包_预览.pdf")
BASE = date(2026, 10, 19)

# 字体（微软雅黑；回退 STSong-Light）
FONT = "MSYH"
try:
    pdfmetrics.registerFont(TTFont(FONT, r"C:\Windows\Fonts\msyh.ttc"))
    pdfmetrics.registerFont(TTFont(FONT + "-B", r"C:\Windows\Fonts\msyhbd.ttc"))
    FB = FONT + "-B"
except Exception:
    FONT = "STSong-Light"; FB = FONT

NAVY = colors.HexColor("#1F3864")
ZEBRA = colors.HexColor("#F2F5FA")
REDBG = colors.HexColor("#FCE4E4")
REDTX = colors.HexColor("#C00000")
LINEC = colors.HexColor("#D0D7E5")
GRAYTX = colors.HexColor("#7A8391")

COLS = ["企业名称", "截止日期", "剩余天数", "企业性质", "投递入口", "来源可信度", "备注"]
WEIGHTS = [0.20, 0.09, 0.07, 0.07, 0.21, 0.07, 0.29]

def parse(s):
    try:
        y, m, d = map(int, s.split("-")); return date(y, m, d)
    except Exception:
        return None

def classify(x):
    df = x.get("date_form"); dl = (x.get("deadline") or "").strip()
    if df == "hard":
        p = parse(dl)
        return "ongoing" if (p and p >= BASE) else "closed"
    if df in ("rolling", "none"):
        return "rolling"
    return "to_verify"

def days_left(x):
    c = classify(x)
    if c == "rolling": return "招满即止"
    if c == "to_verify": return "待核实"
    p = parse(x.get("deadline") or "")
    if not p: return "待核实"
    return (p - BASE).days

def dtext(x):
    c = classify(x)
    return "招满即止" if c == "rolling" else ("待核实" if c == "to_verify" else x.get("deadline", ""))

def row_of(x):
    return [x["company"], dtext(x), str(days_left(x)), x.get("ownership", ""),
            (x.get("apply_url") or "").replace("https://", "").replace("http://", ""),
            (x.get("source_level") or "—"), clean_note((x.get("note") or "").strip())]

def build(ind, name, extra_verify=False):
    d = json.load(open(SRC, encoding="utf-8"))
    comps = d["companies"]
    main = [x for x in comps if x.get("industry") == ind and classify(x) in ("ongoing", "rolling")]
    main.sort(key=lambda x: (classify(x) != "ongoing", x.get("deadline") or "9999"))
    rows = [row_of(x) for x in main]
    if extra_verify:
        vf = [x for x in comps if x.get("industry") == ind and classify(x) == "to_verify"]
        rows += [row_of(x) for x in vf]
    return name, rows

def make_pdf():
    doc = SimpleDocTemplate(OUTPDF, pagesize=landscape(A4),
                            leftMargin=12*mm, rightMargin=12*mm,
                            topMargin=12*mm, bottomMargin=12*mm,
                            title="2026秋招分行业网申截止清单 预览")
    W = landscape(A4)[0] - 24*mm

    st_title = ParagraphStyle("t", fontName=FB, fontSize=16, textColor=NAVY, leading=20)
    st_sub = ParagraphStyle("s", fontName=FONT, fontSize=9, textColor=GRAYTX, leading=13)
    st_cell = ParagraphStyle("c", fontName=FONT, fontSize=8.5, leading=11)
    st_cell_c = ParagraphStyle("cc", fontName=FONT, fontSize=8.5, leading=11, alignment=1)

    colw = [W * w for w in WEIGHTS]

    flow = []
    groups = [build("银行", "银行篇"), build("互联网", "互联网篇"),
              build("国企/央企", "央国企篇", True)]
    for gi, (name, rows) in enumerate(groups):
        n_on = sum(1 for r in rows if r[2].lstrip("-").isdigit() and int(r[2]) >= 0)
        n_roll = sum(1 for r in rows if r[1] == "招满即止")
        n_vf = sum(1 for r in rows if r[1] == "待核实")
        flow.append(Paragraph(f"2026 秋招 {name} · 网申截止清单", st_title))
        sub = (f"数据基准日 2026-10-19 ｜ 共 {len(rows)} 家 ｜ 进行中 {n_on} 家 · "
               f"滚动招聘 {n_roll} 家" + (f" · 待核实 {n_vf} 家" if n_vf else "")
               + " ｜ 截止时间以企业官网为准")
        flow.append(Paragraph(sub, st_sub))
        flow.append(Spacer(1, 4*mm))

        data = [COLS] + [[Paragraph(str(c), st_cell_c if i in (1,2,3,5) else st_cell)
                          for i, c in enumerate(r)] for r in rows]
        t = Table(data, colWidths=colw, repeatRows=1)
        style = [
            ("BACKGROUND", (0,0), (-1,0), NAVY),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), FB),
            ("FONTSIZE", (0,0), (-1,0), 9),
            ("FONTNAME", (0,1), (-1,-1), FONT),
            ("GRID", (0,0), (-1,-1), 0.4, LINEC),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]
        for i in range(1, len(rows)+1):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0,i), (-1,i), ZEBRA))
            r = rows[i-1]
            if r[2].lstrip("-").isdigit() and 0 <= int(r[2]) <= 7:
                style.append(("BACKGROUND", (1,i), (2,i), REDBG))
                style.append(("TEXTCOLOR", (1,i), (2,i), REDTX))
        t.setStyle(TableStyle(style))
        flow.append(t)
        if gi < len(groups) - 1:
            flow.append(PageBreak())

    doc.build(flow)
    print("saved", OUTPDF)

if __name__ == "__main__":
    make_pdf()
