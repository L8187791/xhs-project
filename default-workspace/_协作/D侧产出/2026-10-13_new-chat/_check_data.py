import json
from datetime import datetime

with open(r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

today = datetime(2026, 10, 14)
companies = data['companies']

status_count = {'已截止': 0, '进行中': 0, '无日期': 0}
expired = []
recent_deadline = []

for c in companies:
    deadline_str = c.get('deadline', '')
    if not deadline_str or deadline_str == '待定':
        status_count['无日期'] += 1
        continue
    
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_left = (deadline - today).days
        
        if days_left < 0:
            status_count['已截止'] += 1
        else:
            status_count['进行中'] += 1
            if days_left <= 7:
                recent_deadline.append((c['company'], deadline_str, days_left))
        
        if c.get('days_left') != days_left:
            expired.append((c['company'], c.get('days_left'), days_left))
    except:
        status_count['无日期'] += 1

print('=== 数据状态统计 ===')
print(f'总企业数: {len(companies)}')
print(f'已截止: {status_count["已截止"]}')
print(f'进行中: {status_count["进行中"]}')
print(f'无日期: {status_count["无日期"]}')
print()

print('=== days_left字段过期数量 ===')
print(f'需要更新days_left: {len(expired)}家')
print()

print('=== 最近7天截止的企业（需重点核查）===')
for name, dl, days in sorted(recent_deadline, key=lambda x: x[2]):
    print(f'  {name}: {dl} (还剩{days}天)')
