"""生成《第1个月执行台账》：每日只填 4 个数，自动算进度与达标判定。"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter
import datetime

OUT = r"D:\Documents\deepseek-harness\default-workspace\第1个月执行台账.xlsx"

H1 = Font(bold=True, size=14)
H2 = Font(bold=True, size=11)
HDR = Font(bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="2F5597")
SUB = PatternFill("solid", fgColor="D9E2F3")
WARN = PatternFill("solid", fgColor="FCE4D6")
OK = PatternFill("solid", fgColor="E2EFDA")
BAD = PatternFill("solid", fgColor="FFC7CE")
BOLD = Font(bold=True)
NOTE = Font(size=9, color="808080")
CEN = Alignment(horizontal="center", vertical="center")
WRAP = Alignment(wrap_text=True, vertical="center")
THIN = Side(style="thin", color="D0D0D0")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ============================================================
# 表 1 · 目标
# ============================================================
ws = wb.active
ws.title = "目标"
ws["A1"] = "第 1 个月目标与判定线"
ws["A1"].font = H1
ws["A2"] = "口径来源：《第1个月作战方案.md》《项目总纲_求职资料.md》第 9.3 节"
ws["A2"].font = NOTE

rows = [
    ("项目", "数值", "单位", "说明"),
    ("月净利（保底/达标）", 1500, "元", "达标线"),
    ("月净利（目标）", 2500, "元", ""),
    ("月净利（挑战）", 5000, "元", "仅作挑战档，不作达标线"),
    ("累计单量（达标）", 43, "单", "由 1500 元 ÷ 客单 25–35 元反推"),
    ("客单下限", 25, "元", "低于此值 = 只有 9.9/19.9 在动"),
    ("客单上限", 35, "元", ""),
    ("可投入天数", 30, "天", "Day 1–Day 30"),
    ("日均单量（推算）", "=ROUND(B5/B8,2)", "单/天", ""),
]
for r in rows:
    ws.append(r)
for r in range(3, 11):
    for c in range(1, 5):
        ws.cell(row=r, column=c).border = BOX
ws["B3"].number_format = "#,##0"
ws["B4"].number_format = "#,##0"
ws["B5"].number_format = "#,##0"
ws["B6"].number_format = "#,##0"
ws["B7"].number_format = "#,##0"
ws["B8"].number_format = "0"
ws["B9"].number_format = "0.00"
for r in (3, 5, 6):
    ws.cell(row=r, column=2).fill = SUB
    ws.cell(row=r, column=2).font = BOLD
for c in range(1, 5):
    cell = ws.cell(row=2, column=c)
    cell.font, cell.fill = HDR, HDR_FILL

ws.append([])
ws.append(["先行指标", "达标线", "", "含义"])
r0 = ws.max_row
for c in range(1, 5):
    cell = ws.cell(row=r0, column=c)
    cell.font, cell.fill = HDR, HDR_FILL
ind = [
    ("搜索词带来的曝光", "单篇 ≥ 500", "关键词有没有铺进标题"),
    ("商品卡点击率", "≥ 3%", "商品卡点击 ÷ 观看；封面标题够不够吸引"),
    ("评论数", "单篇 5–15", "互动钩子有没有生效"),
]
for k, v, m in ind:
    ws.append([k, v, "", m])
    r = ws.max_row
    for c in range(1, 5):
        ws.cell(row=r, column=c).border = BOX

ws.column_dimensions["A"].width = 24
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 8
ws.column_dimensions["D"].width = 46

# ============================================================
# 表 2 · 每日台账
# ============================================================
ws2 = wb.create_sheet("每日台账")
ws2["A1"] = "每日台账（只填浅色 4 列：单量 / 销售额 / 评论 / 单篇最高观看）"
ws2["A1"].font = H1
ws2["A2"] = "填完把这张表发我，我按先行指标算断点在哪、下周改什么。"
ws2["A2"].font = NOTE

HEAD = ["Day", "日期", "发布篇目", "单量", "销售额", "客单", "评论数",
        "单篇最高观看", "累计单量", "累计销售额", "累计客单", "进度判定"]
for i, h in enumerate(HEAD, start=1):
    c = ws2.cell(row=4, column=i, value=h)
    c.font, c.fill, c.alignment, c.border = HDR, HDR_FILL, CEN, BOX
    ws2.column_dimensions[get_column_letter(i)].width = 14 if i > 2 else (6 if i == 1 else 11)

FIRST = 5
for i in range(30):
    r = FIRST + i
    ws2.cell(row=r, column=1, value=i + 1)
    ws2.cell(row=r, column=6, value=f'=IF(D{r}=0,"",ROUND(E{r}/D{r},2))').number_format = "0.00"
    ws2.cell(row=r, column=9, value=f"=SUM($D${FIRST}:D{r})")
    ws2.cell(row=r, column=10, value=f"=SUM($E${FIRST}:E{r})")
    ws2.cell(row=r, column=11, value=f'=IF(I{r}=0,"",ROUND(J{r}/I{r},2))').number_format = "0.00"
    ws2.cell(row=r, column=12, value=(
        f'=IF(I{r}=0,"—",'
        f'IF(I{r}*30/{i+1}>=43,"✅ 按节奏",'
        f'IF(I{r}*30/{i+1}>=30,"🟡 偏慢","⚠️ 需干预")))'
    ))
    for c in range(1, 13):
        cell = ws2.cell(row=r, column=c)
        cell.border = BOX
        cell.alignment = CEN
    for c in (4, 5, 7, 8):        # 人工填写区
        ws2.cell(row=r, column=c).fill = WARN
    ws2.cell(row=r, column=2).number_format = "mm-dd"

LAST = FIRST + 29
rng = f"A{FIRST}:L{LAST}"
ws2.conditional_formatting.add(rng, FormulaRule(
    formula=[f'$A{FIRST}<=7'], fill=PatternFill("solid", fgColor="F2F2F2"), stopIfTrue=False))
ws2.conditional_formatting.add(f"L{FIRST}:L{LAST}", CellIsRule(
    operator="equal", formula=['"✅ 按节奏"'], fill=OK))
ws2.conditional_formatting.add(f"L{FIRST}:L{LAST}", CellIsRule(
    operator="equal", formula=['"⚠️ 需干预"'], fill=BAD))
ws2.conditional_formatting.add(f"H{FIRST}:H{LAST}", CellIsRule(
    operator="greaterThanOrEqual", formula=["500"], fill=OK))

ws2.freeze_panes = f"C{FIRST}"

# 备注
r = LAST + 2
ws2.cell(row=r, column=1, value="填表规则").font = H2
for i, t in enumerate([
    "只填 4 列：单量 / 销售额 / 评论数 / 单篇最高观看。其余列是公式，不要改。",
    "客单 = 销售额 ÷ 单量（自动算）。**自测单/自己拍的单不计入**。",
    "「进度判定」按当前累计单量线性外推到 30 天，达标线 43 单。",
    "单篇最高观看 ≥ 500（绿色）是先行指标达标线；整列会按条件自动标色。",
    "**「客单」这一列比单量更值得盯**：低于 25 元说明只有 9.9/19.9 在动，组合包没接住——这是本月最有价值的警报。",
], start=1):
    ws2.cell(row=r + i, column=1, value=f"{i}. {t}")

# ============================================================
# 表 3 · 数据回传
# ============================================================
ws3 = wb.create_sheet("周回传")
ws3["A1"] = "每周回传（周日晚填，我据此出下周动作）"
ws3["A1"].font = H1
ws3["A2"] = "只填「数值」列。判定列自动算。"
ws3["A2"].font = NOTE

HEAD3 = ["周次", "指标", "数值", "判定线", "达标?"]
for i, h in enumerate(HEAD3, start=1):
    c = ws3.cell(row=4, column=i, value=h)
    c.font, c.fill, c.alignment, c.border = HDR, HDR_FILL, CEN, BOX

items = [
    ("Week1", "总曝光", "—"),
    ("Week1", "总观看", "—"),
    ("Week1", "总评论数", "从 0 变正数"),
    ("Week1", "总单量（不含自测单）", "≥ 1（首单）"),
    ("Week1", "客单", "25–35 元"),
    ("Week1", "退款数", "0"),
    ("Week1", "店铺分", "> 4.6"),
    ("Week2", "累计单量", "≥ 8"),
    ("Week2", "单篇最高观看", "≥ 1000"),
    ("Week2", "商品卡点击率", "≥ 3%"),
    ("Week2", "客单", "25–35 元"),
    ("Week2", "退款数", "0"),
    ("Week3", "累计单量", "≥ 30"),
    ("Week3", "客单", "≥ 25 元"),
    ("Week3", "组合包成交", "≥ 1"),
    ("Week3", "退款数", "0"),
]
r = 5
for wk, k, line in items:
    ws3.cell(row=r, column=1, value=wk)
    ws3.cell(row=r, column=2, value=k)
    ws3.cell(row=r, column=3).fill = WARN
    ws3.cell(row=r, column=4, value=line)
    ws3.cell(row=r, column=5, value="")
    for c in range(1, 6):
        ws3.cell(row=r, column=c).border = BOX
        ws3.cell(row=r, column=c).alignment = CEN
    r += 1

ws3.column_dimensions["A"].width = 10
ws3.column_dimensions["B"].width = 26
ws3.column_dimensions["C"].width = 12
ws3.column_dimensions["D"].width = 18
ws3.column_dimensions["E"].width = 10

r += 1
ws3.cell(row=r, column=1, value="还需要你抄 3 条原话（比数字更有用）").font = H2
for i, t in enumerate([
    "评论区里出现最多的问题（抄 3 条原话）",
    "私信里问得最多的是什么",
    "有没有人主动问「能不能帮我看简历」——**这一条决定 T6 怎么选**",
], start=1):
    ws3.cell(row=r + i, column=1, value=f"{i}. {t}")

wb.save(OUT)
print("saved", OUT)
print("sheets:", wb.sheetnames)
