"""校验重算后的财务工作簿：公式 + 缓存值 + 关键逻辑核对。"""
import openpyxl

PATH = r"D:\Documents\deepseek-harness\default-workspace\本月目标与客户财务测算_已算值.xlsx"

wbv = openpyxl.load_workbook(PATH, data_only=True)
print("sheets:", wbv.sheetnames)

def show(name, maxr=None, maxc=None):
    ws = wbv[name]
    print(f"\n===== {name} ({ws.max_row}x{ws.max_column}) =====")
    r_lim = maxr or ws.max_row
    c_lim = maxc or ws.max_column
    for r in range(1, r_lim + 1):
        vals = []
        for c in range(1, c_lim + 1):
            v = ws.cell(row=r, column=c).value
            if v is None:
                v = ""
            if isinstance(v, float):
                v = round(v, 3)
            vals.append(str(v)[:34])
        if any(x.strip() for x in vals):
            print(f"  r{r}: " + " | ".join(vals))

for s in wbv.sheetnames:
    show(s)
