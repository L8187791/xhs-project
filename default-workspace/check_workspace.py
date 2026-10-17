"""批量检查工作区文件状态与关键口径是否齐全。"""
import io
import os
import re

BASE = r"D:\Documents\deepseek-harness\default-workspace"

EXPECT = [
    "项目总纲_求职资料.md", "AI团队编制与运营手册.md", "产品事实卡.md",
    "首批内容包_首发3篇与15篇排期.md", "内容包_周批次01_第4至7篇.md",
    "内容包_周批次02_第8至11篇.md", "内容包_周批次03_第12至15篇.md",
    "发布用_第1至3篇纯文本.md", "出图规格总表.md",
    "产品_面试题库_全本v1.md", "产品1_时间表规格与核验SOP.md",
    "秋招网申截止时间表_v1骨架.xlsx",
    "月入2W目标财务模型.xlsx", "产品阶梯与客单提升方案.md",
    "主力层应急与替代方案.md", "商品上架文案包.md",
    "30天作战日历.md", "产品_简历模板包内容母版.md",
    "每周数据回传模板.md", "索引与进度看板.md",
]

print(f"{'文件':<44}{'状态':<8}大小")
print("-" * 68)
missing = []
for fn in EXPECT:
    p = os.path.join(BASE, fn)
    if os.path.exists(p):
        size = os.path.getsize(p)
        print(f"{fn:<44}{'✅':<8}{size/1024:.1f} KB")
    else:
        print(f"{fn:<44}{'⏳ 缺':<8}-")
        missing.append(fn)

print(f"\n共 {len(EXPECT)} 项，缺失 {len(missing)} 项")
if missing:
    print("缺失清单：")
    for m in missing:
        print("  -", m)

# 关键口径一致性：价格
print("\n=== 价格口径出现情况 ===")
prices = ["19.9", "9.9", "29.9", "25.9", "34.9", "49.9", "99", "69"]
for fn in EXPECT:
    p = os.path.join(BASE, fn)
    if not os.path.exists(p) or not fn.endswith(".md"):
        continue
    t = io.open(p, encoding="utf-8").read()
    hit = sorted({x for x in prices if x in t})
    if hit:
        print(f"  {fn}: {hit}")
