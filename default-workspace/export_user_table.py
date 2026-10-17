"""把用户的 xlsx 导出为 CSV，并把「更新时间」写入核验日期列（G 列）。"""
import openpyxl, csv, io

SRC = r"C:\Users\Administrator\Desktop\2027届秋招信息汇总表-终版.xlsx"
OUT = r"D:\Documents\deepseek-harness\default-workspace\秋招总表_数据快照.csv"

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["秋招总表"]

with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["序号", "企业名称", "行业分类", "企业性质", "批次", "招聘方向",
                "工作地点", "学历要求", "网申截止日期", "投递入口", "备注",
                "核验日期", "核实状态", "数据来源"])
    n = 0
    for r in range(2, ws.max_row + 1):
        name = ws.cell(row=r, column=2).value
        if not name:
            continue
        n += 1
        def g(c):
            v = ws.cell(row=r, column=c).value
            if v is None:
                return ""
            if hasattr(v, "date"):
                return v.date().isoformat()
            return str(v)
        w.writerow([
            g(1), g(2), g(3), g(4), g(5), g(6), g(7), g(8), g(9), g(11), g(12),
            g(14),   # 更新时间 → 核验日期
            g(15),   # 核实状态
            g(13),   # 数据来源
        ])
print(f"导出 {n} 行 → {OUT}")

# 统计核实口径
strong = weak = rolling = 0
for r in range(2, ws.max_row + 1):
    if not ws.cell(row=r, column=2).value:
        continue
    st = str(ws.cell(row=r, column=15).value or "")
    if "滚动" in st:
        rolling += 1
    elif "第三方" in st or "待核实" in st:
        weak += 1
    else:
        strong += 1
print(f"\n核实口径统计：强来源 {strong} 家 ｜ 来源较弱 {weak} 家 ｜ 官方确认滚动 {rolling} 家")
print(f"可对外宣称「已核实」的安全家数 = {strong + rolling} 家（排除来源较弱的 {weak} 家）")
