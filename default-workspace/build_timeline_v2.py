"""按用户表的 15 列结构重建《秋招网申截止时间表》产品骨架，并填入 67 家数据。

列结构（对齐用户表，补 1 列核验日期）：
序号 企业名称 行业分类 企业性质 批次 招聘方向 工作地点 学历要求 网申截止日期
剩余天数 投递入口 备注 核验日期 核实状态 数据来源
配色（沿用用户口径）：红=7天内截止｜橙=8-15天内｜灰=已截止
"""
import csv, io, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

CSV = r"D:\Documents\deepseek-harness\default-workspace\秋招总表_数据快照.csv"
OUT = r"D:\Documents\deepseek-harness\default-workspace\秋招网申截止时间表_v2产品版.xlsx"

rows = list(csv.DictReader(io.open(CSV, encoding="utf-8-sig")))
print("读入", len(rows), "行")

HDR = ["序号", "企业名称", "行业分类", "企业性质", "批次", "招聘方向", "工作地点",
       "学历要求", "网申截止日期", "剩余天数", "投递入口", "备注",
       "核验日期", "核实状态", "数据来源"]
WIDTH = [6, 16, 12, 12, 12, 22, 16, 11, 13, 10, 26, 34, 11, 16, 20]

wb = Workbook()
ws = wb.active
ws.title = "秋招总表"

TITLE = Font(bold=True, size=13)
NOTE = Font(size=9, color="808080")
H = Font(bold=True, color="FFFFFF", size=10)
HFILL = PatternFill("solid", fgColor="2F5597")
THIN = Side(style="thin", color="D0D0D0")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CEN = Alignment(horizontal="center", vertical="center")
WRAP = Alignment(wrap_text=True, vertical="center")

ws["A1"] = "2027 届秋招网申截止时间表"
ws["A1"].font = TITLE
ws["A2"] = ("红=7天内截止 · 橙=8–15天内 · 灰=已截止　｜　"
            "每行标注核验日期、核实状态与数据来源　｜　共 67 家企业（2026-10-08 定版）")
ws["A2"].font = NOTE

HR = 4
for i, (name, w) in enumerate(zip(HDR, WIDTH), start=1):
    c = ws.cell(row=HR, column=i, value=name)
    c.font, c.fill, c.alignment, c.border = H, HFILL, CEN, BOX
    ws.column_dimensions[get_column_letter(i)].width = w

FIRST = HR + 1
for idx, r in enumerate(rows):
    rn = FIRST + idx
    vals = [
        int(r["序号"]) if r["序号"] else "",
        r["企业名称"], r["行业分类"], r["企业性质"], r["批次"], r["招聘方向"],
        r["工作地点"], r["学历要求"], r["网申截止日期"],
        None,                      # J 列公式
        r["投递入口"], r["备注"], r["核验日期"], r["核实状态"], r["数据来源"],
    ]
    for i, v in enumerate(vals, start=1):
        cell = ws.cell(row=rn, column=i, value=v)
        cell.border = BOX
        cell.alignment = WRAP if i in (6, 7, 11, 12, 15) else CEN
    # I 列截止日转为日期格式（便于公式比较）
    cell_i = ws.cell(row=rn, column=9)
    if isinstance(cell_i.value, str) and "-" in cell_i.value:
        try:
            cell_i.value = datetime.date.fromisoformat(cell_i.value)
            cell_i.number_format = "yyyy-mm-dd"
        except ValueError:
            pass                      # "招满即止" 保持文本
    ws.cell(row=rn, column=13).number_format = "yyyy-mm-dd"
    # J 列：剩余天数（活公式）
    ws.cell(row=rn, column=10, value=(
        f'=IF(ISNUMBER($I{rn}),IF($I{rn}<TODAY(),"已截止",$I{rn}-TODAY()),$I{rn}&"")'
    )).alignment = CEN

LAST = FIRST + len(rows) - 1
rng = f"A{FIRST}:O{LAST}"
# 配色：以 I 列（截止日期）为依据
ws.conditional_formatting.add(rng, FormulaRule(
    formula=[f'AND(ISNUMBER($I{FIRST}),$I{FIRST}<TODAY())'],
    fill=PatternFill("solid", fgColor="D9D9D9"), stopIfTrue=False))
ws.conditional_formatting.add(rng, FormulaRule(
    formula=[f'AND(ISNUMBER($I{FIRST}),$I{FIRST}-TODAY()>=0,$I{FIRST}-TODAY()<=7)'],
    fill=PatternFill("solid", fgColor="FFC7CE"), stopIfTrue=False))
ws.conditional_formatting.add(rng, FormulaRule(
    formula=[f'AND(ISNUMBER($I{FIRST}),$I{FIRST}-TODAY()>=8,$I{FIRST}-TODAY()<=15)'],
    fill=PatternFill("solid", fgColor="FFEB9C"), stopIfTrue=False))

ws.freeze_panes = f"C{FIRST}"
ws.auto_filter.ref = f"A{HR}:O{LAST}"

# ---------------- 使用说明 ----------------
ws2 = wb.create_sheet("使用说明")
ws2.column_dimensions["A"].width = 4
ws2.column_dimensions["B"].width = 96
readme = [
    ("T", "这份表怎么用"),
    ("1", "红色 = 7 天内截止，橙色 = 8–15 天内截止，灰色 = 已截止。打开第一眼先看红和橙。"),
    ("2", "「剩余天数」是活公式，随你打开文件的日期自动变；若某行显示“招满即止”，说明官方没有固定截止日。"),
    ("3", "「核实状态」有五种：官网原文 / 就业网转发 / 官网已核验-今日截止（这三类为已核实）；"
          "确认滚动（官方明示无固定截止）；第三方汇总 / 待核实（来源较弱，请自行复核）。"),
    ("4", "「核验日期」= 我打开官网或公告看到的那天。核验日期比截止日期更值得看，它说明这条信息的新鲜度。"),
    ("5", "「数据来源」标明了每条信息来自哪一类渠道，第三方汇总的条目请你点开投递入口自己再过一遍。"),
    ("6", "表里没有“大概”“预计”这种词。核不到固定日期的，我如实写“招满即止”。"),
    ("", ""),
    ("T", "关于家数与来源"),
    ("", "本表共 67 家企业，数据定版于 2026-10-08。其中来源较弱的条目已在“核实状态”列标注——"
         "我没有把它们藏起来，因为你需要知道哪些要自己再核一遍。"),
    ("", ""),
    ("T", "关于更新"),
    ("", "每周我会重新核验一遍官网。更新版直接发给你，已购的不用再买。"),
    ("", ""),
    ("T", "关于错误"),
    ("", "如果你发现哪一行和官网不一致，请告诉我——是我的核验出了问题，我会立刻改，并感谢你。"),
    ("", ""),
    ("T", "重要提醒"),
    ("", "截止日期变化快，投递前务必以企业官方招聘页为准。本表是帮你省掉“挨个找入口”的时间，"
         "不是替代官网。"),
]
r = 2
for tag, text in readme:
    if tag == "T":
        ws2.cell(row=r, column=2, value=text).font = Font(bold=True, size=12)
    elif text:
        ws2.cell(row=r, column=1, value=tag).font = Font(bold=True)
        ws2.cell(row=r, column=2, value=text).alignment = WRAP
    r += 1

wb.save(OUT)
print("saved", OUT)
print(f"数据行 {FIRST}–{LAST}（{len(rows)} 行）")
