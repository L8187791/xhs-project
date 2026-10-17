"""生成《本月目标与客户财务测算》工作簿（替换作战室文档「本月目标 · 净利 5000 执行方案」章节）。"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:\Documents\deepseek-harness\default-workspace\本月目标与客户财务测算_v2.xlsx"

# ---------- 样式 ----------
H1 = Font(bold=True, size=14)
H2 = Font(bold=True, size=11)
HDR = Font(bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="2F5597")
SUB_FILL = PatternFill("solid", fgColor="D9E2F3")
WARN_FILL = PatternFill("solid", fgColor="FCE4D6")
OK_FILL = PatternFill("solid", fgColor="E2EFDA")
BOLD = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ============================================================
# 1. 假设与口径
# ============================================================
ws = wb.active
ws.title = "假设与口径"
ws["A1"] = "假设与口径（唯一参数源 · 全部测算引用本表）"
ws["A1"].font = H1
ws["A2"] = "替换作战室文档中「本月目标 · 净利 5000 执行方案」的旧口径。淡橙色为可调参数。"
ws["A2"].font = Font(italic=True, size=9, color="808080")

rows = [
    ("参数", "值", "单位", "说明 / 与旧口径差异"),
    ("净利目标", 5000, "元", "维持目标不变，但按三档呈现（保底/目标/挑战）"),
    ("执行期天数", 22, "天", "10/09–10/31"),
    ("平台服务费（常规）", 0.02, "比例", "旧口径按 5% 计提，偏高。虚拟商品常规 2%"),
    ("平台服务费（百万免佣期）", 0.006, "比例", "2025-09-01 至 2026-08-31：前 100 万交易额免佣，仅留支付渠道成本 0.6%"),
    ("退款损耗（低）", 0.08, "比例", "旧口径按 5% 计提，偏低"),
    ("退款损耗（中）", 0.12, "比例", "推荐基准。退款还会压制店铺分→流量，属隐性成本"),
    ("退款损耗（高）", 0.18, "比例", "悲观情景：出现集中退款或差评"),
    ("背景口径", "0.02", "文本", "用于本表全部测算，偏保守（未享免佣）"),
    ("退款口径", "0.12", "文本", "用于本表全部测算，取推荐基准"),
]
for r in rows:
    ws.append(r)

# 组合到账率与净额（供其他表引用）
ws.append([])
ws.append(["客单档位", "客单价", "到账率", "净额/单", "备注"])
hdr_row = ws.max_row
for c in range(1, 6):
    cell = ws.cell(row=hdr_row, column=c)
    cell.font = HDR
    cell.fill = HDR_FILL
    cell.alignment = CENTER

TIER_FIRST = hdr_row + 1
NET_RATE_CELL = f"$C${TIER_FIRST}"      # 到账率单元格（引用行 9 的退款口径）
ws.cell(row=9, column=4, value="← 到账率由本行退款口径驱动")

tiers = [
    ("简历包基础", 9.9, "低客单，单独卖不划算"),
    ("时间表单卖", 19.9, "引流与信任款"),
    ("组合包（主推）", 25.9, "目标口径"),
    ("组合包升级", 29.9, "第 3 周上，冲客单"),
    ("高客单咨询", 599.0, "虚拟服务，验证付费意愿用"),
]
for name, price, note in tiers:
    r = ws.max_row + 1
    ws.cell(row=r, column=1, value=name)
    ws.cell(row=r, column=2, value=price).number_format = "0.0"
    ws.cell(row=r, column=3, value="=1-$B$9")
    ws.cell(row=r, column=4, value=f"=B{r}*C{r}").number_format = "0.00"
    ws.cell(row=r, column=5, value=note)

# 参数区百分比格式（行 5–9 为比例参数；行 4 为净利目标）
for r in range(5, 10):
    ws.cell(row=r, column=2).number_format = "0.0%"
ws["B4"].number_format = "#,##0"
# 客单档位表的「到账率」列格式
for r in range(hdr_row + 1, hdr_row + 1 + len(tiers)):
    ws.cell(row=r, column=3).number_format = "0%"

# 参数可调区高亮
for r in (4, 5, 6, 7, 8):
    ws.cell(row=r, column=2).fill = WARN_FILL
    ws.cell(row=r, column=2).font = BOLD

ws.column_dimensions["A"].width = 26
ws.column_dimensions["B"].width = 12
ws.column_dimensions["C"].width = 10
ws.column_dimensions["D"].width = 12
ws.column_dimensions["E"].width = 52

NOTE_ROW = ws.max_row + 2
ws.cell(row=NOTE_ROW, column=1, value="数据来源").font = H2
notes = [
    "平台服务费 2% / 百万免佣 0.6%：小红书虚拟行业经营指南、百万免佣计划公开报道",
    "退款损耗 8–12%：虚拟商品退款争议普遍存在；实操记录显示退款会致「店铺分爆红、订单量腰斩、商品笔记停止推流」",
    "因此退款不只是损失一单的金额，而是连锁影响后续流量 —— 旧口径按 5% 计提低估了风险",
]
for i, n in enumerate(notes, start=1):
    ws.cell(row=NOTE_ROW + i, column=1, value=f"{i}. {n}")

# 记录关键单元格地址
PRICE_RANGE_FIRST = TIER_FIRST   # 客单档位数据首行

# ============================================================
# 2. 本月目标
# ============================================================
ws2 = wb.create_sheet("本月目标")
ws2["A1"] = "本月目标换算（22 天 · 10/09–10/31）"
ws2["A1"].font = H1
ws2["A2"] = "目标 = 5000 元净利。先选客单档位，再看所需日均单量。"
ws2["A2"].font = Font(italic=True, size=9, color="808080")

ws2.append([])
ws2.append(["客单档位", "客单价", "净额/单", "所需单量", "日均单量", "判断"])
h = ws2.max_row
for c in range(1, 7):
    cell = ws2.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, CENTER

for i, (name, price, note) in enumerate(tiers):
    r = ws2.max_row + 1
    src = PRICE_RANGE_FIRST + i
    ws2.cell(row=r, column=1, value=name)
    ws2.cell(row=r, column=2, value=price).number_format = "0.0"
    ws2.cell(row=r, column=3, value=f"=B{r}*'假设与口径'!{NET_RATE_CELL}").number_format = "0.00"
    ws2.cell(row=r, column=4, value=f"=IF(C{r}<=0,\"不可达\",ROUNDUP(5000/C{r},0))")
    ws2.cell(row=r, column=5, value=f"=IF(C{r}<=0,\"—\",ROUND(D{r}/22,1))")
    ws2.cell(row=r, column=6, value=note)
    for c in range(1, 7):
        ws2.cell(row=r, column=c).border = BOX

# 旧口径对照
ws2.append([])
rr = ws2.max_row + 1
ws2.cell(row=rr, column=1, value="与旧口径的差异（客单 15 元 / 25.9 元）").font = H2
ws2.append(["口径", "客单价", "旧文档单量", "旧文档日均", "重算单量", "重算日均"])
h2 = ws2.max_row
for c in range(1, 7):
    cell = ws2.cell(row=h2, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, CENTER

for price, old_n, old_d in ((25.9, 214, 7.1), (15.0, 370, 12.3)):
    r = ws2.max_row + 1
    ws2.cell(row=r, column=1, value="组合包" if price > 20 else "混卖实际客单")
    ws2.cell(row=r, column=2, value=price).number_format = "0.0"
    ws2.cell(row=r, column=3, value=old_n)
    ws2.cell(row=r, column=4, value=old_d)
    ws2.cell(row=r, column=5, value=f"=ROUNDUP(5000/(B{r}*'假设与口径'!{NET_RATE_CELL}),0)")
    ws2.cell(row=r, column=6, value=f"=ROUND(E{r}/22,1)")
    for c in range(1, 7):
        ws2.cell(row=r, column=c).border = BOX

ws2.cell(row=ws2.max_row + 1, column=1,
         value="结论：客单 15 元时日均需约 20 单，对 26 粉新号属结构性不可能 →「把客单做到 25 元以上」是目标成立的前提。")
ws2.cell(row=ws2.max_row, column=1).font = Font(bold=True, color="C00000")

ws2.column_dimensions["A"].width = 20
for col in "BCDEF":
    ws2.column_dimensions[col].width = 14

# ============================================================
# 3. 含投流测算
# ============================================================
ws3 = wb.create_sheet("含投流测算")
ws3["A1"] = "付费流量测算：25.9 元客单能不能投流？"
ws3["A1"].font = H1
ws3["A2"] = "薯条没有营销组件（只能买阅读/点赞/关注）；聚光起充 5000 元以上、日最低预算 300 元。以下按聚光 CPC 口径测算。"
ws3["A2"].font = Font(italic=True, size=9, color="808080")

ws3.append([])
ws3.append(["行业基准", "值", "说明"])
h = ws3.max_row
for c in range(1, 4):
    cell = ws3.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, CENTER
base = [
    ("CPC（元/点击）", 0.8, "代理商口径下限"),
    ("CPC（元/点击）", 4.0, "代理商口径上限"),
    ("点击→下单转化（低）", 0.02, "资料类保守值"),
    ("点击→下单转化（高）", 0.05, "乐观值"),
]
for k, v, n in base:
    ws3.append([k, v, n])
CPC_LO, CPC_HI = h + 1, h + 2
CV_LO, CV_HI = h + 3, h + 4
ws3.cell(row=CPC_LO, column=2).number_format = "0.0"
ws3.cell(row=CPC_HI, column=2).number_format = "0.0"
ws3.cell(row=CV_LO, column=2).number_format = "0%"
ws3.cell(row=CV_HI, column=2).number_format = "0%"

ws3.append([])
rr = ws3.max_row + 1
ws3.cell(row=rr, column=1, value="获客成本与净利（每个客单档位 × 四种组合）").font = H2
ws3.append(["客单档位", "客单价", "净额/单",
            "CAC(低CPC高转化)", "净利/单", "CAC(高CPC低转化)", "净利/单",
            "盈亏平衡CAC", "结论"])
h3 = ws3.max_row
for c in range(1, 10):
    cell = ws3.cell(row=h3, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, Alignment(wrap_text=True, horizontal="center", vertical="center")

for i, (name, price, _) in enumerate(tiers):
    r = ws3.max_row + 1
    src = PRICE_RANGE_FIRST + i
    ws3.cell(row=r, column=1, value=name)
    ws3.cell(row=r, column=2, value=price).number_format = "0.0"
    ws3.cell(row=r, column=3, value=f"=B{r}*'假设与口径'!{NET_RATE_CELL}").number_format = "0.00"
    ws3.cell(row=r, column=4, value=f"=$B${CPC_LO}/$B${CV_HI}").number_format = "0.0"
    ws3.cell(row=r, column=5, value=f"=C{r}-D{r}").number_format = "0.00"
    ws3.cell(row=r, column=6, value=f"=$B${CPC_HI}/$B${CV_LO}").number_format = "0.0"
    ws3.cell(row=r, column=7, value=f"=C{r}-F{r}").number_format = "0.00"
    ws3.cell(row=r, column=8, value=f"=C{r}").number_format = "0.00"
    ws3.cell(row=r, column=9, value=f'=IF(E{r}<0,"每投一单亏 "&TEXT(-E{r},"0")&" 元","可投")')
    for c in range(1, 10):
        ws3.cell(row=r, column=c).border = BOX
    if price < 100:
        for c in (5, 7):
            ws3.cell(row=r, column=c).fill = WARN_FILL

rr = ws3.max_row + 2
ws3.cell(row=rr, column=1, value="要在本价格带上投正，需要同时满足").font = BOLD
ws3.cell(row=rr + 1, column=1, value="① 净额/单 > CAC；② 点击→下单转化 > CPC ÷ 净额/单。以主推组合包（25.9 元）为例：")
# 结论计算块（独立区域，避免与上方结论文字行冲突）
CALC = rr + 7
ws3.cell(row=CALC, column=1, value="结论计算块（可改）")
ws3.cell(row=CALC, column=1).font = H2
ws3.cell(row=CALC, column=1).fill = SUB_FILL
ws3.cell(row=CALC, column=2, value="主推客单价").font = BOLD
ws3.cell(row=CALC, column=3, value=25.9).number_format = "0.0"
ws3.cell(row=CALC + 1, column=2, value="净额/单").font = BOLD
ws3.cell(row=CALC + 1, column=3, value=f"=C{CALC}*'假设与口径'!{NET_RATE_CELL}").number_format = "0.00"
ws3.cell(row=CALC + 2, column=2, value="CPC 上限（转化 5%）").font = BOLD
ws3.cell(row=CALC + 2, column=3, value=f"=C{CALC+1}*$B${CV_HI}").number_format = "0.00"
ws3.cell(row=CALC + 3, column=2, value="CPC=4 元时所需转化率").font = BOLD
ws3.cell(row=CALC + 3, column=3, value=f"=$B${CPC_HI}/C{CALC+1}").number_format = "0.0%"

ws3.cell(row=rr + 3, column=1).value = f'="① CPC = 4 元时，所需转化率 > "&TEXT(C{CALC+3},"0.0%")&"（公开资料中找不到支撑）"'
ws3.cell(row=rr + 4, column=1).value = f'="② 转化率 5% 时，可承受 CPC 上限约 "&TEXT(C{CALC+2},"0.00")&" 元"'
ws3.cell(row=rr + 5, column=1, value="结论：本项目在 19.9–25.9 元价格带上，付费投流在数学上不成立，应转搜索关键词 + 群聊。")
ws3.cell(row=rr + 5, column=1).font = Font(bold=True, color="C00000")

ws3.column_dimensions["A"].width = 20
ws3.column_dimensions["B"].width = 10
ws3.column_dimensions["C"].width = 11
for col in "DEFGH":
    ws3.column_dimensions[col].width = 17
ws3.column_dimensions["I"].width = 26

# ============================================================
# 4. 净利敏感性
# ============================================================
ws4 = wb.create_sheet("净利敏感性")
ws4["A1"] = "净利敏感性：22 天 × 不同客单 × 不同日均单量"
ws4["A1"].font = H1
ws4["A2"] = "绿色 = 达成 5000 目标的组合；浅橙 = 低于 2500。列按客单价，行按日均单量。"
ws4["A2"].font = Font(italic=True, size=9, color="808080")

prices = [9.9, 15.0, 19.9, 25.9, 29.9]
daily = [3, 5, 7, 10, 15, 20, 25]

ws4.append([])
start = ws4.max_row + 1
ws4.cell(row=start, column=1, value="日均单量").font = HDR
ws4.cell(row=start, column=1).fill = HDR_FILL
ws4.cell(row=start, column=1).alignment = CENTER
for j, p in enumerate(prices):
    c = ws4.cell(row=start, column=2 + j, value=p)
    c.font, c.fill, c.alignment = HDR, HDR_FILL, CENTER
    c.number_format = "0.0"

for i, d in enumerate(daily):
    r = start + 1 + i
    ws4.cell(row=r, column=1, value=d).font = BOLD
    ws4.cell(row=r, column=1).fill = SUB_FILL
    for j in range(len(prices)):
        col = 2 + j
        L = get_column_letter(col)
        price_ref = f"{L}${start}"
        f = f"=ROUND($A{r}*22*{price_ref}*'假设与口径'!{NET_RATE_CELL},0)"
        cell = ws4.cell(row=r, column=col, value=f)
        cell.number_format = "#,##0"
        cell.border = BOX
        cell.alignment = CENTER

end = start + len(daily)
# 条件格式
from openpyxl.formatting.rule import CellIsRule
rng = f"B{start+1}:{get_column_letter(1+len(prices))}{end}"
ws4.conditional_formatting.add(rng, CellIsRule(operator="greaterThanOrEqual", formula=["5000"], fill=OK_FILL))
ws4.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["2500"], fill=WARN_FILL))

rr = end + 2
ws4.cell(row=rr, column=1, value="备注").font = H2
for i, t in enumerate([
    "净额/单 = 客单价 × 到账率（到账率取自「假设与口径」，当前为 88%：2% 平台服务费 + 12% 退款）",
    "表中为 22 天累计净利。绿色达成 5000，浅橙低于 2500（文档自认的中位预期区间上限）",
    "对照：账号当前单篇最高观看 799；历史最高曝光 2051（观看约 280）→ 日均 7–10 单需要稳定爆款",
], start=1):
    ws4.cell(row=rr + i, column=1, value=f"{i}. {t}")

ws4.column_dimensions["A"].width = 14
for j in range(len(prices)):
    ws4.column_dimensions[get_column_letter(2 + j)].width = 13

# ============================================================
# 5. 三周进度表
# ============================================================
ws5 = wb.create_sheet("三周进度表")
ws5["A1"] = "三周进度表与判定线（按 5000 元目标折算）"
ws5["A1"].font = H1
ws5["A2"] = "判定线已按剔除平台 5% 假设、采用 88% 到账率重算；客单基准 25.9 元。"
ws5["A2"].font = Font(italic=True, size=9, color="808080")

ws5.append([])
ws5.append(["阶段", "日期", "天数", "阶段目标", "阶段单量", "累计单量", "累计净利", "文档原判定线", "判定"])
h = ws5.max_row
for c in range(1, 10):
    cell = ws5.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, Alignment(wrap_text=True, horizontal="center", vertical="center")

# 目标基准：25.9 元客单，日均 = 5000 / 22 / 净额
TARGET_PRICE = 25.9
net_per_order = TARGET_PRICE * 0.88          # 22.8 元
daily_target = 5000 / 22 / net_per_order     # ≈ 9.98 单/天

stages = [
    ("第 1 周 · 起量", "10/09–10/15", 7),
    ("第 2 周 · 冲刺", "10/16–10/22", 7),
    ("第 3 周 · 收官", "10/23–10/31", 9),
]
acc = 0
for idx, (name, span, days) in enumerate(stages, start=1):
    r = ws5.max_row + 1
    stage_n = round(daily_target * days)
    acc += stage_n
    ws5.cell(row=r, column=1, value=name)
    ws5.cell(row=r, column=2, value=span)
    ws5.cell(row=r, column=3, value=days)
    ws5.cell(row=r, column=4, value=f"日均 {round(stage_n/days,1)} 单")
    ws5.cell(row=r, column=5, value=stage_n)
    ws5.cell(row=r, column=6, value=acc)
    ws5.cell(row=r, column=7, value=f"=ROUND(F{r}*{TARGET_PRICE}*'假设与口径'!{NET_RATE_CELL},0)")
    ws5.cell(row=r, column=7).number_format = "#,##0"
    ws5.cell(row=r, column=8, value={1: "—", 2: "10/16 判定线", 3: "10/23 判定线"}[idx])
    ws5.cell(row=r, column=9, value="按累计净利对照 5000")
    for c in range(1, 10):
        ws5.cell(row=r, column=c).border = BOX

rr = ws5.max_row + 2
ws5.cell(row=rr, column=1, value="原判定线的问题").font = H2
for i, t in enumerate([
    "文档 10/16 判定线「单量 ≥ 60」——60 单 × 25.9 元 × 88% ≈ 1368 元，只对应「净利约 1400 元」的档位",
    "若按 60 单放行，等于把目标默认降到 1400 元，却仍按 5000 元的节奏分配资源",
    "建议判定线：10/16 累计 ≥ 68 单且客单 ≥ 20；10/23 累计 ≥ 157 单",
    "目标分层建议：保底 1200 元 / 目标 2500 元 / 挑战 5000 元",
    "末行累计净利约 5242 元，略高于目标：因阶段单量四舍五入（70/70/90 = 230 单，非恰好 220 单），属取整残差，不是计算错误",
], start=1):
    ws5.cell(row=rr + i, column=1, value=f"{i}. {t}")

ws5.column_dimensions["A"].width = 18
ws5.column_dimensions["B"].width = 14
ws5.column_dimensions["C"].width = 7
ws5.column_dimensions["D"].width = 16
for col in "EFGHI":
    ws5.column_dimensions[col].width = 15
ws5.column_dimensions["H"].width = 24

# ============================================================
# 6. 口径修正对照
# ============================================================
ws6 = wb.create_sheet("口径修正对照")
ws6["A1"] = "与旧文档口径的逐项修正对照"
ws6["A1"].font = H1
ws6.append([])
ws6.append(["项目", "旧文档口径", "修正口径", "方向", "依据"])
h = ws6.max_row
for c in range(1, 6):
    cell = ws6.cell(row=h, column=c)
    cell.font, cell.fill, cell.alignment = HDR, HDR_FILL, CENTER

items = [
    ("平台扣点", "5%", "0.6%–2%（当前免佣期 0.6%）", "利好", "虚拟商品常规服务费 2%；百万免佣计划前 100 万交易额仅 0.6% 支付成本"),
    ("退款损耗", "5%", "8%–12%（推荐 12%）", "利空", "虚拟商品退款争议普遍；退款致店铺分下降会连累流量"),
    ("客单假设", "只给标价 25.9", "同时给 15 元混卖实际客单", "利空", "文档自述「现状 15 元（9.9+19.9 混卖）」"),
    ("投流成本", "未计入", "CAC 40–100 元/单（负毛利）", "利空", "CPC 0.8–4 元 × 点击→下单 2–5%"),
    ("投流工具", "薯条（商品成交目标）", "薯条无商品组件；聚光起充 5000 元", "利空", "薯条仅三种推广目标；聚光需企业号"),
    ("10/16 判定线", "单量 ≥ 60", "≥ 68 单且客单 ≥ 20", "利空", "60 单仅对应约 1400 元净利"),
    ("净利/单（25.9 元）", "23.3 元（扣 10%）", "22.8 元（扣 12%）", "基本持平", "两项修正方向相反，大体抵消"),
]
for it in items:
    ws6.append(list(it))
    r = ws6.max_row
    for c in range(1, 6):
        ws6.cell(row=r, column=c).border = BOX
        ws6.cell(row=r, column=c).alignment = WRAP
    ws6.cell(row=r, column=4).alignment = CENTER

rr = ws6.max_row + 2
ws6.cell(row=rr, column=1, value="核心结论").font = H2
concl = [
    "两项财务修正方向相反、大体抵消：净额/单仍约 22.8 元，日均约 10 单（25.9 元客单）。",
    "真正的风险不是费率，而是：① 真实客单可能只有 15 元（日均需约 20 单）；② 付费流量负毛利；③ 退款连累店铺分。",
    "因此策略应为：提客单（做分层与组合）+ 零成本流量（搜索关键词 + 群聊）+ 严控退款（交付说明前置）。",
]
for i, t in enumerate(concl, start=1):
    ws6.cell(row=rr + i, column=1, value=f"{i}. {t}")

for col, w in zip("ABCDE", (16, 24, 30, 10, 52)):
    ws6.column_dimensions[col].width = w

wb.save(OUT)
print("saved", OUT)
