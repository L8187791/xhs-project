import json
import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'
output_path = r'D:\Documents\deepseek-harness\default-workspace\_协作\outbox\timetable-200家-20261014.csv'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']

# 定义要导出的字段
fields = [
    'no', 'company', 'industry', 'ownership', 'batch', 'direction',
    'location', 'degree', 'deadline', 'days_left', 'note',
    'verified_at', 'verify_status', 'is_rolling', 'past_friendly', 'industry_main'
]

with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for c in companies:
        writer.writerow(c)

print(f'✅ CSV已导出')
print(f'路径: {output_path}')
print(f'行数: {len(companies)}家')
