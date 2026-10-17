import json
from datetime import datetime

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']

# 分类统计
has_date = 0      # 有具体截止日期
pending = 0       # 待定/待核实
rolling = 0       # 滚动招（无固定截止）
none_date = 0     # 完全没写

# 按核实状态分
verify_levels = {}

for c in companies:
    dl = c.get('deadline', '')
    vs = c.get('verify_status', '未知')
    
    verify_levels[vs] = verify_levels.get(vs, 0) + 1
    
    if not dl or dl == '待定':
        pending += 1
    elif dl == '滚动' or dl == '招满即止':
        rolling += 1
    else:
        # 检查能不能解析成日期
        try:
            datetime.strptime(dl, '%Y-%m-%d')
            has_date += 1
        except:
            none_date += 1

print('=== 131家数据质量明细 ===')
print(f'总企业数: {len(companies)}')
print()
print(f'✅ 有具体截止日期: {has_date}家 ({has_date*100//len(companies)}%)')
print(f'⚠️ 待定/待核实: {pending}家 ({pending*100//len(companies)}%)')
print(f'🟡 滚动招（招满即止）: {rolling}家 ({rolling*100//len(companies)}%)')
print(f'❓ 其他格式: {none_date}家')
print()

print('=== 核实状态分布（可信度）===')
for vs, cnt in sorted(verify_levels.items(), key=lambda x: -x[1]):
    pct = cnt*100//len(companies)
    print(f'  {vs}: {cnt}家 ({pct}%)')

print()
print('=== 产品宣称风险点 ===')
print(f'如果用户以为"131家都有具体截止日期"，')
print(f'实际只有{has_date}家有硬日期，占{has_date*100//len(companies)}%')
print()
print(f'其余{pending + rolling}家是待定/滚动招，')
print(f'用户打开可能会觉得"怎么这么多没写日期"')
