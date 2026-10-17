# -*- coding: utf-8 -*-
"""
DB28 · 任务 A：19.9 现有产品 xlsx 排版美化
- 不改数据内容（只改视觉）
- 表头加底色 / 冻结首行与表头 / 截止日列 7 天内高亮 / 列宽适配 / 边框 / 斑马纹
- 备份原文件后另存美化版
"""
import shutil, os, datetime
from openpyxl import load_workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                             NamedStyle)
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule
from openpyxl.comments import Comment

SRC = "19.9产品包-上架用/03 交付文件/2026秋招网申截止时间表.xlsx"
OUT = "19.9产品包-上架用/03 交付文件/2026秋招网申截止时间表_美化版.xlsx"

# --- 1) 备份原文件（不覆盖）---
bak_dir = "19.9产品包-上架用/03 交付文件/_备份_美化前"
os.makedirs(bak_dir, exist_ok=True)
bak = os.path.join(bak_dir, os.path.basename(SRC))
if not os.path.exists(bak):
    shutil.copy2(SRC, bak)
    print("[备份] ->", bak)
else:
    print("[备份] 已存在，跳过:", bak)

wb = load_workbook(SRC)
ws = wb.active

# --- 配色（清爽 / 求职向 / 不花哨）---
C_HEAD   = "1F3864"   # 深藏蓝 表头底
C_HEADTX = "FFFFFF"   # 表头白字
C_TITLE  = "1F3864"
C_ZEBRA  = "F2F5FA"   # 极浅蓝斑马
C_WARN   = "FCE4E4"   # 7天内 -> 浅红底
C_WARNTX = "C00000"   # 7天内 -> 深红字
C_NOTE   = "FDECEC"
C_BORDER = "D0D7E5"

thin = Side(style="thin", color=C_BORDER)
BORD = Border(left=thin, right=thin, top=thin, bottom=thin)

NCOL = ws.max_column
NROW = ws.max_row

# --- 2) 标题行（第 1 行）---
# 合并 A1:O1 让标题居中撑满
if not ws.merged_cells.ranges:
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=NCOL)
t = ws.cell(1, 1)
t.value = "2026 秋招网申截止时间表｜主表 131 家｜每周五更新"
t.font = Font(name="微软雅黑", size=14, bold=True, color=C_TITLE)
t.alignment = Alignment(horizontal="left", vertical="center")
ws.row_dimensions[1].height = 30

# 第 2 行：说明行（若空则补一行说明；有内容则不动）
r2 = ws.cell(2, 1).value
if r2 is None:
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=NCOL)
    n = ws.cell(2, 1)
    n.value = ("使用说明：按截止日期升序排列 ｜ 剩余天数≤7 的行以浅红底+深红字高亮 ｜ "
               "「进行中」= 还可投递，「已截止」= 仅作历史参考 ｜ 截止时间以企业官网为准")
    n.font = Font(name="微软雅黑", size=9, color="595959")
    n.alignment = Alignment(horizontal="left", vertical="center")
    n.fill = PatternFill("solid", fgColor=C_NOTE)
ws.row_dimensions[2].height = 20

# --- 3) 表头行（第 3 行）---
HDR = 3
for c in range(1, NCOL + 1):
    cell = ws.cell(HDR, c)
    cell.fill = PatternFill("solid", fgColor=C_HEAD)
    cell.font = Font(name="微软雅黑", size=10, bold=True, color=C_HEADTX)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORD
ws.row_dimensions[HDR].height = 24

# --- 4) 数据区样式 ---
# 需要识别关键列
allhdr = [ws.cell(HDR, c).value for c in range(1, NCOL + 1)]
def idx(name):
    return allhdr.index(name) + 1 if name in allhdr else None
i_deadline = idx("截止日期")
i_days     = idx("剩余天数")
i_status   = idx("状态")
i_no       = idx("序号")
i_url      = idx("投递入口")

for r in range(HDR + 1, NROW + 1):
    if ws.cell(r, 1).value is None:
        continue
    zebra = (r % 2 == 0)
    for c in range(1, NCOL + 1):
        cell = ws.cell(r, c)
        cell.border = BORD
        cell.font = Font(name="微软雅黑", size=10, color="262626")
        if zebra:
            cell.fill = PatternFill("solid", fgColor=C_ZEBRA)
        # 对齐
        if c in (i_no,):
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c in (i_deadline, i_days, i_status):
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c == i_url:
            cell.alignment = Alignment(horizontal="left", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)

# --- 5) 7 天内高亮（截止日期列 + 剩余天数列 + 状态列）---
# 口径：剩余天数 0~7（含今天）→ 浅红底 + 深红粗体；已截止（<0）→ 灰色弱化
warn_cols = [c for c in (i_deadline, i_days, i_status) if c]
cnt_warn = 0
cnt_past = 0
for r in range(HDR + 1, NROW + 1):
    if ws.cell(r, 1).value is None:
        continue
    v = ws.cell(r, i_days).value if i_days else None
    if isinstance(v, (int, float)):
        if 0 <= v <= 7:
            cnt_warn += 1
            for c in warn_cols:
                ws.cell(r, c).fill = PatternFill("solid", fgColor=C_WARN)
                ws.cell(r, c).font = Font(name="微软雅黑", size=10, bold=True, color=C_WARNTX)
        elif v < 0:
            cnt_past += 1
            for c in range(1, NCOL + 1):
                f = ws.cell(r, c).font
                ws.cell(r, c).font = Font(name="微软雅黑", size=10, color="A6A6A6")
print(f"[高亮] 7天内 {cnt_warn} 行 / 已截止 {cnt_past} 行")

# --- 6) 列宽适配（覆盖现有）---
widths = {
    "序号": 6, "企业名称": 30, "截止日期": 13, "状态": 12, "剩余天数": 10,
    "来源可信度": 12, "等级": 8, "日期形态": 12, "企业性质": 11,
    "银行类型": 12, "招聘方向": 22, "工作地点": 20, "学历": 12,
    "投递入口": 34, "备注": 30,
}
for c in range(1, NCOL + 1):
    name = allhdr[c - 1]
    if name in widths:
        ws.column_dimensions[get_column_letter(c)].width = widths[name]
    else:
        ws.column_dimensions[get_column_letter(c)].width = 14

# --- 7) 冻结（首行+说明+表头，即数据从第 4 行起）---
ws.freeze_panes = "A4"

# --- 8) 自动筛选 ---
ws.auto_filter.ref = f"A{HDR}:{get_column_letter(NCOL)}{NROW}"

# --- 9) 打印设置（A4 横向 / 重复表头）---
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_title_rows = f"{HDR}:{HDR}"

wb.save(OUT)
print("[保存] ->", OUT)
print("[校验] 数据行数 =", sum(1 for r in range(4, NROW + 1) if ws.cell(r, 1).value is not None))
