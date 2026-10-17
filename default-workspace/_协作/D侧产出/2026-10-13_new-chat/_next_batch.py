import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']

# 找出表外采集的69家（no >= 132），排除已核验的5家
verified = ['安利', '四川银行', '中海油', '麦当劳', '光大银行']
new_companies = [c for c in companies if c['no'] >= 132 and c['company'] not in verified]

# 按优先级排序：招往届的 > 有具体日期的 > 滚动招的
priority = []
for c in new_companies:
    score = 0
    if c.get('past_friendly') == '招往届':
        score += 100
    if c.get('deadline') and c['deadline'] != '招满即止':
        score += 50
    if c.get('status') == '进行中':
        score += 30
    priority.append((score, c))

priority.sort(key=lambda x: -x[0])

print('=== 下一批待核验企业（前10家）===')
print()
for i, (score, c) in enumerate(priority[:10]):
    print(f'{i+1}. #{c["no"]} {c["company"]}')
    print(f'   截止: {c.get("deadline", "无")}')
    print(f'   往届友好: {c.get("past_friendly", "未明确")}')
    print(f'   来源等级: {c.get("source_level", "无")}')
    print()
