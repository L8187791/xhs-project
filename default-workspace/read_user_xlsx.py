"""精确统计用户表：行数、字段、核实状态、已截止数量、日期分布。"""
import openpyxl
from collections import Counter
import datetime

SRC = r"C:\Users\Administrator\Desktop\2027届秋招信息汇总表-终版.xlsx"
wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["秋招总表"]

# 表头
hdr = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
print("列数:", len(hdr))
print("表头:", [h for h in hdr if h])

# 数据行
rows = []
for r in range(2, ws.max_row + 1):
    name = ws.cell(row=r, column=2).value
    if not name:
        continue
    rows.append({
        "序号": ws.cell(row=r, column=1).value,
        "企业": name,
        "行业": ws.cell(row=r, column=3).value,
        "性质": ws.cell(row=r, column=4).value,
        "批次": ws.cell(row=r, column=5).value,
        "截止": ws.cell(row=r, column=9).value,
        "备注": ws.cell(row=r, column=12).value,
    })
print(f"\n有效数据行: {len(rows)} 家")
print("序号范围:", rows[0]["序号"], "→", rows[-1]["序号"])

print("\n按行业分类:")
for k, v in Counter(r["行业"] for r in rows).most_common():
    print(f"  {k}: {v}")

print("\n按企业性质:")
for k, v in Counter(r["性质"] for r in rows).most_common():
    print(f"  {k}: {v}")

print("\n按批次:")
for k, v in Counter(r["批次"] for r in rows).most_common():
    print(f"  {k}: {v}")

# 截止日期类型
today = datetime.date(2026, 10, 9)
d_dates, d_rolling, d_none = [], [], []
for r in rows:
    v = r["截止"]
    if v is None:
        d_none.append(r)
    elif isinstance(v, datetime.datetime):
        d_dates.append((r, v.date()))
    else:
        d_rolling.append(r)
print(f"\n有明确截止日期: {len(d_dates)} 家")
print(f"招满即止/滚动: {len(d_rolling)} 家")
print(f"空白: {len(d_none)} 家")
print("滚动/空白的家:", [r["企业"] for r in d_rolling] + [r["企业"] for r in d_none])

past = [(r, d) for r, d in d_dates if d < today]
fut = sorted([(d, r["企业"]) for r, d in d_dates if d >= today])
print(f"\n已截止（< 2026-10-09）: {len(past)} 家 → {[r['企业'] for r, _ in past]}")
print(f"未截止: {len(fut)} 家")
print("\n未截止按日期:")
for d, n in fut:
    print(f"  {d}  {n}")
