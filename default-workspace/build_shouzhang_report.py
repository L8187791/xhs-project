# -*- coding: utf-8 -*-
"""生成小红书虚拟电商「手帐」赛道评估交付文件"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:\Documents\deepseek-harness\default-workspace\小红书虚拟电商手帐赛道评估.xlsx"

wb = Workbook()

# ---------- 样式 ----------
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="微软雅黑", size=14, bold=True, color="1F4E79")
SUB_FONT = Font(name="微软雅黑", size=10, bold=True, color="1F4E79")
BODY_FONT = Font(name="微软雅黑", size=9.5)
NOTE_FONT = Font(name="微软雅黑", size=9, italic=True, color="808080")
WRAP = Alignment(wrap_text=True, vertical="top", horizontal="left")
CENTER = Alignment(wrap_text=True, vertical="center", horizontal="center")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
BAND_FILL = PatternFill("solid", fgColor="F2F6FC")
PRIORITY_FILL = {
    "高": PatternFill("solid", fgColor="C6EFCE"),
    "中": PatternFill("solid", fgColor="FFF2CC"),
    "低": PatternFill("solid", fgColor="F2F2F2"),
}

def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = BORDER

def set_widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

def write_rows(ws, rows, start_row, ncols, band=True):
    r = start_row
    for idx, row in enumerate(rows):
        for c, val in enumerate(row, start=1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.font = BODY_FONT
            cell.alignment = WRAP
            cell.border = BORDER
            if band and idx % 2 == 1:
                cell.fill = BAND_FILL
        # 优先级列着色
        if row and str(row[0]) in PRIORITY_FILL and ws.title.startswith("01"):
            ws.cell(row=r, column=1).fill = PRIORITY_FILL[str(row[0])]
            ws.cell(row=r, column=1).alignment = CENTER
            ws.cell(row=r, column=1).font = Font(name="微软雅黑", size=10, bold=True)
        r += 1
    return r

# ============================================================
# Sheet 0: 总览
# ============================================================
ws0 = wb.active
ws0.title = "00_总览"
ws0.column_dimensions["A"].width = 3
ws0.column_dimensions["B"].width = 24
ws0.column_dimensions["C"].width = 90

ws0["B2"] = "小红书虚拟电商「手帐」垂直赛道评估"
ws0["B2"].font = TITLE_FONT

overview = [
    ("核心结论", "高毛利、低门槛、已红海化、正遭遇平台合规收紧的成熟赛道。能赚钱，但赚的是「细分差异化 + 执行力 + 复购运营」的钱，不是信息差搬运的钱。"),
    ("一句话判断", "泛化「电子手帐模板」已卷死；真正机会在细分人群款（考研/教师/ADHD/孕妈/婚礼/财务）＋会员订阅＋私域复购。"),
    ("综合推荐度", "★★★☆（有条件推荐：原创能力 + 深耕一个细分人群可入局；纯搬运赚快钱已被 2025 新规堵死）。"),
    ("市场热度", "真实成交被验证：全年计划日程本 30 元/份售 4700+ 单≈12 万+营收；海外 Etsy 头部店月营收 9800 美元。"),
    ("最大风险", "① 2025 下半年小红书虚拟类目调整＋新规收紧（296 个爆品下架）；② 版权/侵权投诉；③ 泛款价格战。"),
    ("最大机会", "① AI 重塑成本结构；② 细分人群蓝海（ADHD/教师/婚礼等）；③ 订阅制打开利润天花板；④ 官方类目升级利好合规原创者。"),
    ("本文件包含", "① Sheet1 细分人群选品清单；② Sheet2 竞品账号拆解表；③ Sheet3 站内竞品挖掘与拆解方法论。"),
]
r = 4
for k, v in overview:
    ws0.cell(row=r, column=2, value=k).font = SUB_FONT
    ws0.cell(row=r, column=2).alignment = Alignment(vertical="top", horizontal="left")
    c = ws0.cell(row=r, column=3, value=v)
    c.font = BODY_FONT
    c.alignment = WRAP
    r += 1

ws0.cell(row=r + 1, column=2, value="数据说明").font = SUB_FONT
ws0.cell(row=r + 1, column=3, value="所有数据来自公开网络来源（派代网、小红书种草学官方指南、极目新闻、Etsy 卖家社区、领淘电商教育等），时间为 2025-2026 年。具体竞品账号名、销量、客单价请以小红书站内实时搜索为准二次核实。").font = NOTE_FONT
ws0.cell(row=r + 1, column=3).alignment = WRAP

# ============================================================
# Sheet 1: 细分人群选品清单
# ============================================================
ws1 = wb.create_sheet("01_细分人群选品清单")
headers1 = ["优先级", "细分人群", "核心痛点 / 爽点", "具体选品（产品形态）", "参考客单价(元)",
            "竞争度", "需求验证方法", "引流内容角度"]
ws1.append([])
ws1.cell(row=1, column=1, value="交付物①：小红书虚拟电商手帐赛道 · 细分人群选品清单").font = TITLE_FONT
for i, h in enumerate(headers1, start=1):
    ws1.cell(row=2, column=i, value=h)
style_header(ws1, 2, len(headers1))

rows1 = [
    ["高", "考研 / 备考人群\n(考研二战/雅思/考公)",
     "计划乱、无法坚持、焦虑；要上岸的强目标驱动",
     "考研全年规划本、倒计时表、周计划+复盘、错题本、背诵打卡表、康奈尔笔记(英语/政治分科)、1000题打卡表",
     "19.9~39.9", "中(刚需但已有供给)", "站内搜「考研计划本」「考研倒计时」，按销量排序，读评论区挖具体痛点",
     "「考研二战上岸计划本」「政治1000题打卡表」「被室友偷瞄三次的学习计划本」"],
    ["高", "教师人群\n(班主任/科任老师)",
     "备课、排课、批改、家长会、班级管理繁琐",
     "课程表、周计划、批改记录表、家长会记录、学生成绩追踪表、班级管理SOP",
     "19.9~49.9", "低(蓝海)", "搜「教师手帐」「班主任计划」「班级管理」，看是否有成熟供给",
     "「班主任开学第一周计划本」「老师专属课表+批改记录」"],
    ["高", "ADHD / 注意力不足人群\n(成人ADHD/执行力弱)",
     "专注难、任务多易崩、需要极简与正反馈",
     "简化版面+多巴胺配色手帐、「大脑垃圾桶」页、每日≤3任务框、习惯微打卡、番茄钟页",
     "29.9~59.9(溢价高)", "极低(国内蓝海,海外已爆发)", "参照 Etsy「ADHD planner」近两年爆发式增长；国内搜索「ADHD手帐」验证空白",
     "「ADHD人的极简手帐」「注意力救星」「我的大脑终于能撑过一整天」"],
    ["高", "婚礼筹备人群",
     "筹备复杂、怕漏项、预算失控、倒计时焦虑",
     "婚礼倒计时、预算表、宾客名单+座位表、筹备清单、婚纱照规划、伴手礼清单",
     "29.9~59.9", "低(蓝海)", "搜「备婚手帐」「婚礼倒计时」，看供给量与销量",
     "「备婚倒计时手帐」「婚礼预算+宾客清单一本搞定」"],
    ["中", "宝妈 / 育儿人群",
     "记录宝宝成长、辅食、疫苗、作息易漏",
     "宝宝成长记录、辅食表、疫苗提醒、亲子阅读打卡、育儿日程本",
     "19.9~39.9", "中低", "搜「宝宝记录本」「辅食表」，宝妈群体复购强",
     "「新手妈妈必备记录本」「辅食+疫苗+作息一页全记」"],
    ["中", "财务 / 还债 / 攒钱人群",
     "记账难坚持、还债焦虑、想存钱",
     "债务清偿进度可视化、52周存钱表、预算计划、记账复盘本",
     "19.9~39.9", "低(蓝海)", "搜「还债进度」「52周存钱」，情绪+工具双驱动",
     "「还债进度条手帐」「52周存钱法，年底多存1万」"],
    ["中", "健身 / 减脂人群",
     "坚持难、饮食与训练记录繁琐",
     "健身打卡、餐谱记录、围度/体重记录、训练计划本",
     "19.9~39.9", "中低", "搜「减脂记录本」「健身打卡表」",
     "「减脂餐谱记录本」「健身打卡，坚持100天」"],
    ["中", "职场效率党",
     "周报、开会、任务管理占时间",
     "周报模板、会议记录、OKR/计划本、工作SOP模板",
     "19.9~49.9", "中高(偏红海)", "搜「周报模板」「会议记录」，通用型已多，需细分行业",
     "「周报写到崩溃？送你自动生成器」"],
    ["低", "学生党通用\n(中学生/大学生)",
     "单词、错题、复习、计划",
     "康奈尔笔记、120天单词本、错题本、复习计划表",
     "9.9~29.9", "高(红海)", "搜「单词本」「错题本」，已售量巨大，价格战激烈",
     "「120天单词本」「康奈尔笔记模板」"],
    ["低", "3分钟热度 / 自律焦虑人群\n(情绪价值款)",
     "焦虑、『买了=努力了』的自我安慰",
     "全年计划日程本、21天习惯打卡、自律打卡(安慰剂型)",
     "19.9~39.9", "高(已被验证爆款,同质化重)", "已被验证：全年计划日程本30元售4700+单；需差异化包装",
     "「2026全年计划本」「今年必逆袭」「买完即自律」"],
]
r = write_rows(ws1, rows1, 3, len(headers1))
ws1.cell(row=r + 1, column=1, value="选品三原则").font = SUB_FONT
principles = [
    "① 先选「你自己就是该人群」的细分，写下市面产品 10 个不爽点 = 你的产品需求文档。",
    "② 泛款卷死，细分款溢价高：『ADHD planner』比『planner』好卖十倍；客单价可上探到 59.9 元。",
    "③ 一个爆款带一串矩阵：全年计划本 → 120天单词本 → 康奈尔 → GoodNotes 模板，分层覆盖场景。",
]
for i, p in enumerate(principles):
    c = ws1.cell(row=r + 2 + i, column=1, value=p)
    c.font = BODY_FONT
    c.alignment = WRAP
    ws1.merge_cells(start_row=r + 2 + i, start_column=1, end_row=r + 2 + i, end_column=len(headers1))

set_widths(ws1, [8, 16, 26, 40, 14, 20, 32, 32])
ws1.freeze_panes = "A3"

# ============================================================
# Sheet 2: 竞品账号拆解表
# ============================================================
ws2 = wb.create_sheet("02_竞品账号拆解表")
headers2 = ["竞品类型 / 定位", "代表账号 / 来源", "主打产品", "客单价",
            "已确认销售数据", "内容打法", "变现路径", "可借鉴点", "差异化机会"]
ws2.cell(row=1, column=1, value="交付物②：小红书虚拟电商手帐赛道 · 竞品账号拆解表").font = TITLE_FONT
for i, h in enumerate(headers2, start=1):
    ws2.cell(row=2, column=i, value=h)
style_header(ws2, 2, len(headers2))

rows2 = [
    ["日程/计划模板标杆\n(情绪价值款)",
     "「全年计划日程本」卖家(站内搜索「全年计划日程本」即见,账号名请站内核实)",
     "2025全年计划日程本 + 120天单词本 + 康奈尔 + GoodNotes模板(共7款)",
     "10.8~30.8",
     "TOP款30元/份售4700+单,单项营收≈12万+;评价1600+条",
     "原创简笔头像+清晰定位简介;人性化标题、评论区引导、玄学发布时间",
     "原创设计人设→商卡/笔记成交→产品矩阵分层(引流款+主力款)",
     "原创人设、7款产品矩阵分层定价、把「自律焦虑」包装成情绪价值",
     "拆到细分人群(考研/教师/ADHD),从通用日程本切到垂直款"],
    ["实体手帐文创\n(参照,非纯虚拟)",
     "段宇佳:「又见一面文创」「绘梦文化」(湖北日报报道)",
     "手帐本、榉木印章、创意小卡片",
     "成本占售价50%~60%",
     "单月营业额峰值3.6万,稳定1万/月;最大单100+套2000余元",
     "图文种草+直播带货;约稿插画师,固定签约画师按需定制原创画稿",
     "小红书图文+直播间购物车(20品类)→按需投产→上架成交",
     "供应链成本优势、签约画师保证原创、直播+种草双引擎",
     "实体可作手帐整体赛道参照;虚拟卖家可学其「原创画稿+矩阵账号」"],
    ["海外数字手帐标杆\n(打法对标)",
     "PastelPaperPlans(Etsy,海外卖家社区跟踪)",
     "马卡龙色系+习惯打卡手帐(8份手帐+会员站)",
     "单本8~25美元;会员月费4~10美元",
     "月营收9800美元(Etsy 5000+订阅4800)",
     "Pinterest日更5-10pin;细分单品+季节款+捆绑包",
     "Etsy listing→Pinterest流量(60-80%)→会员订阅把复购变月费",
     "订阅制(利润占半)、捆绑包拉客单(5本25刀)、季节款(开学/新年双高峰)",
     "国内对应:马卡龙色系+习惯打卡细分;用「免费领→私域→豪华包」落地订阅"],
    ["学习/考研电子手帐",
     "「学习大师」等教育电子手帐卖家(GoodNotes/Notability模板,见于站内外)",
     "学习专用电子手帐、考研模板、计划本",
     "9.9~39.9",
     "闲鱼/淘宝 9.9-39.9 电子手帐包销量成千",
     "配合GoodNotes使用教程视频;发「平板笔记前后对比」类内容",
     "低价走量+教程引流→私域→升级豪华包",
     "用教程视频降低使用门槛、前后对比制造向往感",
     "聚焦单一考试人群(考研二战/雅思)做垂直款+教程IP"],
    ["小学教辅/资料类\n(虚拟电商通用参照)",
     "小学资料类虚拟店铺(站内搜索「小学资料」,爆款笔记已售过万)",
     "幼儿启蒙、控笔、古诗词、专注力等数十类电子资料",
     "几元~30元",
     "单价不超一杯奶茶钱,笔记已售过万",
     "「带娃」人设+日更1-2条+痛点刺激/场景代入",
     "低价走量+评论区服务拉复购+产品矩阵覆盖数十场景",
     "精准人设、日更频率、认真回复评论区提升复购",
     "其「细分学段/场景」思路可直接迁移到手帐(如分科/分人群)"],
]
r = write_rows(ws2, rows2, 3, len(headers2))

ws2.cell(row=r + 1, column=1, value="重要提示").font = SUB_FONT
tips = [
    "① 本表「代表账号」中,有公开数据的是可确认案例;账号名称、实时销量请务必在站内搜索二次核实(平台实时变动,无法离线抓取)。",
    "② 拆解竞品时重点看四个维度:产品矩阵(几款/怎么分层)、定价(引流款vs主力款)、内容(笔记选题+封面)、转化(商卡/私域/订阅)。",
    "③ 差异化机会总结:通用日程本/学生单词本已红海 → 往「窄人群(教师/ADHD/婚礼/财务) + 订阅复购」方向切。",
]
for i, p in enumerate(tips):
    c = ws2.cell(row=r + 2 + i, column=1, value=p)
    c.font = BODY_FONT
    c.alignment = WRAP
    ws2.merge_cells(start_row=r + 2 + i, start_column=1, end_row=r + 2 + i, end_column=len(headers2))

set_widths(ws2, [16, 24, 26, 14, 22, 26, 24, 26, 26])
ws2.freeze_panes = "A3"

# ============================================================
# Sheet 3: 竞品挖掘与拆解方法论
# ============================================================
ws3 = wb.create_sheet("03_竞品挖掘方法论")
ws3.column_dimensions["A"].width = 4
ws3.column_dimensions["B"].width = 18
ws3.column_dimensions["C"].width = 92
ws3["B2"] = "交付物②附录：站内竞品挖掘与拆解方法论"
ws3["B2"].font = TITLE_FONT

methods = [
    ("第1步 找竞品", "在小红书搜核心词+细分词各搜一遍,按「销量」排序:\n核心词:电子手帐 / 手帐模板 / 手帐素材 / 电子贴纸 / 计划本 / GoodNotes模板\n细分词:考研计划本 / 教师手帐 / 婚礼倒计时 / ADHD手帐 / 减脂记录本 / 还债计划表"),
    ("第2步 锁定标杆", "取每个词销量前3的账号(看商品卡「已售」),再进主页看:定位简介、头像、产品数量、笔记风格、有无直播。"),
    ("第3步 拆产品矩阵", "记录:共几款产品?价格区间?哪款是引流款(9.9-19.9)、主力款(29.9-49.9)、利润款(捆绑包/会员)?"),
    ("第4步 拆内容", "记录其笔记:标题钩子(痛点/数字/悬念)、封面风格、更新频率、评论区互动话术。对照官方指南:手工行业店播占56%+商卡21%,虚拟行业笔记占39%+商卡32%。"),
    ("第5步 拆转化", "记录其转化路径:商卡直购?评论/私信引流?免费领→私域→豪华包?有无会员订阅?"),
    ("第6步 找差异化", "把竞品的「空白点」列出来:未覆盖的人群、未做的场景、未用的订阅制、可做更细的垂直款。"),
    ("落地建议", "建一个自己的竞品跟踪表,每周更新一次销量变化,重点盯 2-3 个与你目标人群一致的竞品,持续 4 周即可看清打法。"),
]
r = 4
for k, v in methods:
    ws3.cell(row=r, column=2, value=k).font = SUB_FONT
    ws3.cell(row=r, column=2).alignment = Alignment(vertical="top", horizontal="left")
    c = ws3.cell(row=r, column=3, value=v)
    c.font = BODY_FONT
    c.alignment = WRAP
    r += 1

wb.save(OUT)
print("SAVED:", OUT)
print("Sheets:", wb.sheetnames)
