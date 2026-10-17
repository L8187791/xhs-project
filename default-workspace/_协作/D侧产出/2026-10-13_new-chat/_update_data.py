import json
from datetime import datetime

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'
output_path = input_path

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

today = datetime(2026, 10, 14)
companies = data['companies']

updated_count = 0
for c in companies:
    deadline_str = c.get('deadline', '')
    if not deadline_str or deadline_str == '待定':
        c['days_left'] = None
        continue
    
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_left = (deadline - today).days
        c['days_left'] = days_left
        updated_count += 1
    except:
        c['days_left'] = None

# 更新meta
data['meta']['data_date'] = '2026-10-14'
data['meta']['built_at'] = '2026-10-14 12:00'
old_version = data['meta']['version']
new_version = old_version + '.18'
data['meta']['version'] = new_version
data['meta']['changelog'] = f'{new_version}: 自动重算days_left（数据日期10-11→10-14），{updated_count}家企业剩余天数更新'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'✅ 更新完成')
print(f'版本: {old_version} → {new_version}')
print(f'更新days_left: {updated_count}家')
print(f'数据日期: 2026-10-14')
print()
print('=== 今日截止（10/14）===')
for c in companies:
    if c.get('days_left') == 0:
        print(f'  🔴 {c["company"]}: 今天截止')
