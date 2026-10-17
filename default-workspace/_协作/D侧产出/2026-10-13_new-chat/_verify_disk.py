import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== 磁盘实际情况 ===')
print(f'企业总数: {len(data["companies"])}家')
print(f'版本: {data["meta"]["version"]}')
print(f'数据日期: {data["meta"]["data_date"]}')
print()

# 检查有没有新字段
sample = data['companies'][0]
print('第一条企业的字段:')
for k in sample.keys():
    print(f'  {k}')

print()
print('最后5家企业编号:')
for c in data['companies'][-5:]:
    print(f'  #{c["no"]} {c["company"]}')
