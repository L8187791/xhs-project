import openpyxl

p = r"D:\Documents\deepseek-harness\default-workspace\时间表_已算值.xlsx"
wbf = openpyxl.load_workbook(p, data_only=False)
ws = wbf["网申时间表"]
for r in (4, 5, 6):
    for c in (5, 9):
        cell = ws.cell(row=r, column=c)
        print(f"{cell.coordinate}: type={cell.data_type!r} value={cell.value!r}")
print()
# 条件格式规则
for rng, rules in ws.conditional_formatting._cf_rules.items():
    print("range:", rng.sqref)
    for rule in rules:
        print("   type:", rule.type, "| formula:", getattr(rule, "formula", None), "| dxf fill:", rule.dxf.fill.bgColor.rgb if rule.dxf and rule.dxf.fill else None)
