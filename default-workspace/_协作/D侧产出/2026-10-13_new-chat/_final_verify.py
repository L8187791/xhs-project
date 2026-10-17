import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']

print('=== 数据确认报告 ===')
print()
print(f'1. 企业总数: {len(companies)}家')
print(f'2. 版本: {data["meta"]["version"]}')
print(f'3. 数据日期: {data["meta"]["data_date"]}')
print()

print('=== 新增字段统计 ===')
print(f'is_rolling（招满即止标注）:')
rolling_true = sum(1 for c in companies if c.get('is_rolling') == True)
rolling_false = sum(1 for c in companies if c.get('is_rolling') == False)
print(f'  是: {rolling_true}家')
print(f'  否: {rolling_false}家')
print()

print(f'past_friendly（是否招往届）:')
past_counts = {}
for c in companies:
    p = c.get('past_friendly', '无此字段')
    past_counts[p] = past_counts.get(p, 0) + 1
for k, v in past_counts.items():
    print(f'  {k}: {v}家')
print()

print(f'industry_main（行业大类）:')
ind_counts = {}
for c in companies:
    i = c.get('industry_main', '无此字段')
    ind_counts[i] = ind_counts.get(i, 0) + 1
for k, v in sorted(ind_counts.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}家')
print()

print('=== 招聘方向缺值 ===')
missing_direction = sum(1 for c in companies if not c.get('direction'))
print(f'缺direction字段: {missing_direction}家')
print()

print('=== 最后5家企业 ===')
for c in companies[-5:]:
    print(f'  #{c["no"]} {c["company"]}')
