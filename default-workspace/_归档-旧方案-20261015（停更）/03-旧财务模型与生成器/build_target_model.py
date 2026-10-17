"""生成《月入2W目标财务模型》：把 3 个月目标拆成可执行的单量/客单/流量/投流账。"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule

OUT = r"D:\Documents\deepseek-harness\default-workspace\月入2W目标财务模型.xlsx"

H1 = Font(bold=True, size=14)
H2 = Font(bold=True, size=11)
HDR = Font(bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="2F5597")
SUB_FILL = PatternFill("solid", fgColor="D9E2F3")
WARN = PatternFill("solid", fgColor="FCE4D6")
OK = PatternFill("solid", fgColor="E2EFDA")
BAD = PatternFill("solid", fgColor="FFC7CE")
BOLD = Font(bold=True)
NOTE = Font(size=9, color="808080")
CENTER = Alignment(horizontal="center", vertical="center")
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ============================================================
# 1. 假设
# ============================================================
ws = wb.active
ws.title = "假设"
ws["A1"] = "假设与口径（唯一参数源）"
ws["A1"].font = H1
ws["A2"] = "淡橙色为可调参数。修改后全表自动重算。"
ws["A2"].font = NOTE

ws.append([])
ws.append(["参数", "值", "单位", "说明"])
HDR_ROW = ws.max_row          # = 4
data = [
    ("月净利目标", 20000, "元", "目标已更新：3 个月内成型为月入 2W"),
    ("到账率", None, "比例", "= 1 − 平台服务费 − 退款损耗"),
    ("每月天数", 30, "天", ""),
    ("平台服务费", 0.02, "比例", "虚拟商品常规服务费；免佣期可低至 0.6%"),
    ("退款损耗", 0.12, "比例", "虚拟商品退款普遍；退款还会压制店铺分→流量"),
    ("投流保守 CAC", 20, "元/单", "CPC 0.8 元 ÷ 点击→下单 4%"),
    ("投流乐观 CAC", 50, "元/单", "CPC 2 元 ÷ 点击→下单 4%"),
    ("付费单量占比", 0.4, "比例", "40% 单量来自付费流量；其余靠内容自然流"),
]
for row in data:
    ws.append(row)

# 动态记录各参数所在行，避免硬编码偏移
R = {name: HDR_ROW + 1 + i for i, (name, *_rest) in enumerate(data)}
ROW_TARGET = R["月净利目标"]
ROW_RATE = R["到账率"]
ROW_DAYS = R["每月天数"]
ROW_CAC_LO = R["投流保守 CAC"]
ROW_CAC_HI = R["投流乐观 CAC"]
ROW_PAID = R["付费单量占比"]
# 到账率公式（此时行号已知）
ws.cell(row=ROW_RATE, column=2,
        value=f"=1-B{R['平台服务费']}-B{R['退款损耗']}")

ws.cell(row=ROW_TARGET, column=2).number_format = "#,##0"
ws.cell(row=ROW_RATE, column=2).number_format = "0.0%"
ws.cell(row=R["平台服务费"], column=2).number_format = "0.0%"
ws.cell(row=R["退款损耗"], column=2).number_format = "0.0%"
ws.cell(row=ROW_CAC_LO, column=2).number_format = "0"
ws.cell(row=ROW_CAC_HI, column=2).number_format = "0"
ws.cell(row=ROW_PAID, column=2).number_format = "0%"
for r in (ROW_TARGET, R["平台服务费"], R["退款损耗"], ROW_CAC_LO, ROW_CAC_HI, ROW_PAID):
    ws.cell(row=r, column=2).fill = WARN
    ws.cell(row=r, column=2).font = BOLD

ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 12
ws.column_dimensions["C"].width = 10
ws.column_dimensions["D"].width = 50

WS = "'假设'"
RR = f"$B${ROW_RATE}"
TARGET = f"$B${ROW_TARGET}"
DAYS = f"$B${ROW_DAYS}"
CAC_LO = f"$B${ROW_CAC_LO}"
CAC_HI = f"$B${ROW_CAC_HI}"
PAID_SHARE = f"$B${ROW_PAID}"

# ---- 自动结论：2W 净利能不能成立 ----
CB = ROW_PAID + 2
ws.cell(row=CB, column=1, value="自动结论（随参数变化）").font = H2
ws.cell(row=CB, column=1).fill = SUB_FILL
rows_c = [
    ("达到 2W 需要的毛销售额",
     f"=ROUND({TARGET}/B{ROW_RATE},0)", "#,##0 元",
     "因为净额 = 销售额 × 到账率，所以销售额必须放大"),
    ("在 99 元客单下需要的单数",
     f"=ROUND({TARGET}/(99*B{ROW_RATE}),0)", "#,##0 单", ""),
    ("若 40% 单量靠投流（CAC 35 元）",
     f"=ROUND({TARGET}/(99*B{ROW_RATE})*B{ROW_PAID}*AVERAGE(B{ROW_CAC_LO},B{ROW_CAC_HI}),0)",
     "#,##0 元", "这笔钱必须从净利里出"),
    ("扣掉投流后实际净利",
     f"={TARGET}-B{CB+2}", "#,##0 元", "低于 2W 的差额"),
    ("结论",
     f'=IF(B{CB+3}>=TARGET,'
     f'"纯自然流 + 99 元客单即可达标",'
     f'"投流会吃掉 "&TEXT(B{CB+2},"#,##0")&" 元：2W 净利只能靠自然流 + 提客单实现，'
     f'不能靠买量")',
     "文本", "这是本模型最重要的一条判断"),
]
for i, (name, f, fmt, note) in enumerate(rows_c):
    r = CB + 1 + i
    ws.cell(row=r, column=1, value=name).font = BOLD
    c = ws.cell(row=r, column=2, value=f)
    if fmt != "文本":
        c.number_format = fmt
    ws.cell(row=r, column=4, value=note)
    c.fill = SUB_FILL if i < len(rows_c) - 1 else OK

# ============================================================
# 2. 目标换算（核心表）
# ============================================================
ws2 = wb.create_sheet("目标换算")
ws2["A1"] = "月入 2W：不同客单需要多少单？"
ws2["A1"].font = H1
ws2["A2"] = "这一张表解释了为什么必须提客单 —— 在 29.9 元价格带上目标不成立。"
ws2["A2"].font = NOTE

ws2.append([])
ws2.append(["客单档位", "客单价", "净额/单", "需成交单数/月", "日均单量",
            "付费单量", "投流支出(取CAC中值)", "净利(扣投流)", "是否达标"])
h = ws2.max_row
for c in range(1, 10):
    cell = ws2.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, Alignment(wrap_text=True, horizontal="center", vertical="center")

tiers = [
    ("1 单件资料", 29.9),
    ("小组合", 49.9),
    ("全流程包（首批）", 99.0),
    ("全流程包（稳定）", 149.0),
    ("含 1v1 服务", 199.0),
    ("陪跑服务", 399.0),
]
first = ws2.max_row + 1
for i, (name, price) in enumerate(tiers):
    r = ws2.max_row + 1
    ws2.cell(row=r, column=1, value=name)
    ws2.cell(row=r, column=2, value=price).number_format = "0.0"
    ws2.cell(row=r, column=3, value=f"=B{r}*{WS}!{RR}").number_format = "0.00"
    ws2.cell(row=r, column=4, value=f"=ROUNDUP({WS}!{TARGET}/C{r},0)")
    ws2.cell(row=r, column=5, value=f"=ROUND(D{r}/{WS}!{DAYS},1)")
    ws2.cell(row=r, column=6, value=f"=ROUND(D{r}*{WS}!{PAID_SHARE},0)")
    ws2.cell(row=r, column=7, value=f"=F{r}*AVERAGE({WS}!{CAC_LO},{WS}!{CAC_HI})").number_format = "#,##0"
    ws2.cell(row=r, column=8, value=f"=ROUND(D{r}*C{r}-G{r},0)").number_format = "#,##0"
    ws2.cell(row=r, column=9, value=f'=IF(H{r}>={WS}!{TARGET},"达标（自然流口径）","差 "&TEXT({WS}!{TARGET}-H{r},"#,##0")&" 元")')
    for c in range(1, 10):
        ws2.cell(row=r, column=c).border = BOX
        ws2.cell(row=r, column=c).alignment = CENTER
last = ws2.max_row

ws2.conditional_formatting.add(f"E{first}:E{last}",
    CellIsRule(operator="lessThanOrEqual", formula=["8"], fill=OK))
ws2.conditional_formatting.add(f"E{first}:E{last}",
    CellIsRule(operator="greaterThan", formula=["15"], fill=BAD))
ws2.conditional_formatting.add(f"I{first}:I{last}",
    CellIsRule(operator="equal", formula=['"达标"'], fill=OK))

rr = last + 2
ws2.cell(row=rr, column=1, value="怎么读这张表").font = H2
for i, t in enumerate([
    "「净利(扣投流)」= 成交单数 × 净额/单 − 40% 单量的投流支出（CAC 取 20/50 的中值 35 元）",
    "重要：所有档位这一列都低于 2W —— 说明「一边买量一边做到 2W 净利」在任何价格带都不成立",
    "29.9 元客单需要日均 26 单，且扣投流后只剩 9120 元 —— 既做不到，也不赚钱",
    "99 元客单日均 7.8 单、扣投流后 16718 元 —— 单量达标了，但投流吃掉了 3282 元",
    "结论：2W 净利必须靠「自然流 + 客单 99 以上」。投流只能在客单站上 150+ 之后小比例使用",
], start=1):
    ws2.cell(row=rr + i, column=1, value=f"{i}. {t}")

for col, w in zip("ABCDEFGHI", (20, 11, 11, 15, 11, 10, 19, 14, 14)):
    ws2.column_dimensions[col].width = w

# ============================================================
# 3. 混合客单模型
# ============================================================
ws3 = wb.create_sheet("混合客单")
ws3["A1"] = "混合客单：现实中不会所有人都买 99 元"
ws3["A1"].font = H1
ws3["A2"] = "调「成交占比」这一列，看混合客单和所需单量怎么变。"
ws3["A2"].font = NOTE

ws3.append([])
ws3.append(["层级", "成交占比", "客单价", "加权贡献", "", "指标", "值"])
h = ws3.max_row
for c in (1, 2, 3, 4, 6, 7):
    cell = ws3.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, CENTER

mix = [
    ("入门层（9.9–29.9）", 0.55, 25.0),
    ("主力层（99–149）", 0.35, 99.0),
    ("高客单层（399+）", 0.10, 399.0),
]
mfirst = ws3.max_row + 1
for name, share, price in mix:
    r = ws3.max_row + 1
    ws3.cell(row=r, column=1, value=name)
    ws3.cell(row=r, column=2, value=share).number_format = "0%"
    ws3.cell(row=r, column=2).fill = WARN
    ws3.cell(row=r, column=3, value=price).number_format = "0.0"
    ws3.cell(row=r, column=4, value=f"=B{r}*C{r}").number_format = "0.0"
    for c in range(1, 5):
        ws3.cell(row=r, column=c).border = BOX
mlast = ws3.max_row
TOTAL_ROW = mlast + 1
ws3.cell(row=TOTAL_ROW, column=1, value="合计 / 混合客单").font = BOLD
ws3.cell(row=TOTAL_ROW, column=2, value=f"=SUM(B{mfirst}:B{mlast})").number_format = "0%"
ws3.cell(row=TOTAL_ROW, column=2).font = BOLD
ws3.cell(row=TOTAL_ROW, column=4, value=f"=SUM(D{mfirst}:D{mlast})").number_format = "0.00"
ws3.cell(row=TOTAL_ROW, column=4).font = BOLD
MIXROW = TOTAL_ROW
MIXREF = f"D{MIXROW}"      # 混合客单所在单元格

metrics = [
    ("混合客单", f"={MIXREF}", "0.0"),
    ("净额/单", f"={MIXREF}*{WS}!{RR}", "0.00"),
    ("需成交单数/月", f"=ROUNDUP({WS}!{TARGET}/({MIXREF}*{WS}!{RR}),0)", "#,##0"),
    ("日均单量", f"=ROUND({WS}!{TARGET}/({MIXREF}*{WS}!{RR})/{WS}!{DAYS},1)", "0.0"),
    ("其中付费单量", f"=ROUND({WS}!{TARGET}/({MIXREF}*{WS}!{RR})*{WS}!{PAID_SHARE},0)", "#,##0"),
    ("投流支出", f"=ROUND({WS}!{TARGET}/({MIXREF}*{WS}!{RR})*{WS}!{PAID_SHARE}*AVERAGE({WS}!{CAC_LO},{WS}!{CAC_HI}),0)", "#,##0"),
]
mstart = mfirst
for i, (name, f, fmt) in enumerate(metrics):
    r = mstart + i
    ws3.cell(row=r, column=6, value=name).font = BOLD
    cell = ws3.cell(row=r, column=7, value=f)
    cell.number_format = fmt
    cell.fill = SUB_FILL
AD_FLOW_ROW = mstart + 5          # 投流支出所在行
NET_ROW = mstart + 6
ws3.cell(row=NET_ROW, column=6, value="净利(扣投流)").font = BOLD
cell = ws3.cell(row=NET_ROW, column=7,
                value=f"=ROUND({WS}!{TARGET}-G{AD_FLOW_ROW},0)")
cell.number_format = "#,##0"
ws3.cell(row=NET_ROW, column=8,
         value=f'=IF(G{NET_ROW}>={WS}!{TARGET},"达标","缺口 "&TEXT({WS}!{TARGET}-G{NET_ROW},"#,##0")&" 元")')
r = NET_ROW

rr = r + 2
ws3.cell(row=rr, column=1, value="关键动作：把主力层占比往上推").font = H2
for i, t in enumerate([
    "主力层占比 35% → 混合客单约 88 元，日均约 9 单",
    "主力层占比 50% → 混合客单超过 110 元，日均降到 7 单以内",
    "所以第 2–3 个月的核心指标不是总单量，而是「主力层成交占比」",
    "把 55% 的低价买家往上推，靠三件事：详情页升级引导 / 自动回复 / 已购用户补差价升级",
    "注意：混合客单 88 元时，扣掉 40% 投流（3687 元）后净利约 16313 元 —— 仍不到 2W",
    "要真正到 2W，必须把付费占比压到 10% 以下（即基本不买量），或把混合客单做到 150 元以上",
], start=1):
    ws3.cell(row=rr + i, column=1, value=f"{i}. {t}")

for col, w in zip("ABCDEFGH", (22, 11, 11, 12, 3, 18, 13, 18)):
    ws3.column_dimensions[col].width = w

# ============================================================
# 4. 投流可行性
# ============================================================
ws4 = wb.create_sheet("投流可行性")
ws4["A1"] = "投流可行性：什么客单价才配得起付费流量"
ws4["A1"].font = H1
ws4["A2"] = "净额必须大于获客成本，否则投一单亏一单。"
ws4["A2"].font = NOTE

ws4.append([])
ws4.append(["客单价", "净额/单", "CAC(保守 20 元)", "净利", "CAC(乐观 50 元)", "净利", "可承受 CAC 上限", "结论"])
h = ws4.max_row
for c in range(1, 9):
    cell = ws4.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, Alignment(wrap_text=True, horizontal="center", vertical="center")

for name, price in tiers:
    r = ws4.max_row + 1
    ws4.cell(row=r, column=1, value=price).number_format = "0.0"
    ws4.cell(row=r, column=2, value=f"=A{r}*{WS}!{RR}").number_format = "0.00"
    ws4.cell(row=r, column=3, value=f"={WS}!{CAC_LO}")
    ws4.cell(row=r, column=4, value=f"=B{r}-C{r}").number_format = "0.00"
    ws4.cell(row=r, column=5, value=f"={WS}!{CAC_HI}")
    ws4.cell(row=r, column=6, value=f"=B{r}-E{r}").number_format = "0.00"
    ws4.cell(row=r, column=7, value=f"=B{r}").number_format = "0.00"
    ws4.cell(row=r, column=8, value=f'=IF(D{r}>0,"可投","每投一单亏 "&TEXT(-D{r},"0")&" 元")')
    for c in range(1, 9):
        ws4.cell(row=r, column=c).border = BOX
        ws4.cell(row=r, column=c).alignment = CENTER

ws4.conditional_formatting.add(f"D{ws4.max_row-len(tiers)+1}:F{ws4.max_row}",
    CellIsRule(operator="lessThan", formula=["0"], fill=BAD))
ws4.conditional_formatting.add(f"D{ws4.max_row-len(tiers)+1}:F{ws4.max_row}",
    CellIsRule(operator="greaterThanOrEqual", formula=["0"], fill=OK))

rr = ws4.max_row + 2
ws4.cell(row=rr, column=1, value="结论").font = H2
for i, t in enumerate([
    "29.9 元客单：净额约 25.7 元，CAC 乐观值 50 元 → 每投一单亏约 24 元。不能投。",
    "99 元客单：净额约 85 元 → 两种 CAC 假设下都为正，可以投。",
    "149 元以上：投流空间充足，可以做「付费放量」。",
    "所以顺序必须是：先靠内容和搜索把客单做上去，再开投流。反过来做一定亏。",
], start=1):
    ws4.cell(row=rr + i, column=1, value=f"{i}. {t}")

for col, w in zip("ABCDEFGH", (10, 11, 18, 10, 18, 10, 16, 22)):
    ws4.column_dimensions[col].width = w

# ============================================================
# 5. 三个月路线图
# ============================================================
ws5 = wb.create_sheet("三个月路线图")
ws5["A1"] = "3 个月路线图：每月只解决一个瓶颈"
ws5["A1"].font = H1
ws5["A2"] = "不追求每月等速增长，而是每月换一个卡点去打。"
ws5["A2"].font = NOTE

ws5.append([])
ws5.append(["月份", "本月瓶颈", "核心动作", "客单目标", "日均单量", "月净利目标", "判定线"])
h = ws5.max_row
for c in range(1, 8):
    cell = ws5.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, Alignment(wrap_text=True, horizontal="center", vertical="center")

plan = [
    ("第 1 个月", "信任与出单（0 → 首批成交）",
     "完成银行核验填表；上架 3 个入门款；发布 15 篇；每篇带互动钩子；跑通自动发货",
     "25–35 元", "1–2 单", "1500–2500 元", "评论数从 0 变正数；出现单篇 1000+ 观看"),
    ("第 2 个月", "客单（把人往上推）",
     "上架全流程包 99 元；详情页加升级引导；已购用户补差价升级；主力层占比 ≥ 35%",
     "60–90 元", "3–5 单", "6000–9000 元", "主力层成交占比 ≥ 35%；混合客单 ≥ 70 元"),
    ("第 3 个月", "放量（才允许花钱）",
     "客单站稳后开投流；主力层占比推到 50%；上 1v1 服务；复用爆款选题批量复制",
     "100–150 元", "6–8 单", "20000 元", "混合客单 ≥ 100 元；投流 ROI ≥ 1.5"),
]
for row in plan:
    ws5.append(list(row))
    r = ws5.max_row
    for c in range(1, 8):
        ws5.cell(row=r, column=c).border = BOX
        ws5.cell(row=r, column=c).alignment = WRAP

rr = ws5.max_row + 2
ws5.cell(row=rr, column=1, value="这个路线图最重要的三条纪律").font = H2
for i, t in enumerate([
    "第 1 个月不要碰投流。客单没上去之前，投流是纯亏损，且会把「亏损」误读成「起量」。",
    "第 2 个月不要加产品数量。瓶颈在客单，不在品类——上新只会分散账号标签。",
    "第 3 个月才允许小额投流，且只用于「放大已验证的爆款笔记」，不用于「买新客户」。",
    "关键修正：模型显示「一边大量买量、一边做到 2W 净利」在任何价格带都不成立。2W 的主路径是自然流 + 客单 99 元以上。",
], start=1):
    ws5.cell(row=rr + i, column=1, value=f"{i}. {t}")

rr2 = rr + 5
ws5.cell(row=rr2, column=1, value="不迎合的风险声明").font = Font(bold=True, size=11, color="C00000")
for i, t in enumerate([
    "月入 2W 是挑战目标，不是保底。第 1 个月从 0 单起步，现实区间是 1500–2500 元（与项目诊断报告的中位预期一致）。",
    "第 3 个月达成 2W 需要同时满足三件事：主力层占比 ≥ 50%、混合客单 ≥ 100 元、至少 2 篇 5000+ 观看的爆款。缺一项，落点大概率在 8000–12000 元。",
    "任何「先违规起量再整改」的想法都要排除：平台清退者永久禁止重新入驻，退出成本不可逆。",
    "主力层能否成立，取决于你能否交付「一次简历诊断」这类人工服务。做不到就改用「定制改写建议」，但仍需你本人处理。",
], start=1):
    ws5.cell(row=rr2 + i, column=1, value=f"{i}. {t}")

for col, w in zip("ABCDEFG", (11, 24, 46, 12, 10, 14, 30)):
    ws5.column_dimensions[col].width = w

wb.save(OUT)
print("saved", OUT)
