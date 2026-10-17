import json
from datetime import datetime, timedelta

with open(r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

data = raw['companies']
meta = raw['meta']

today = datetime(2026, 10, 14)
tomorrow = datetime(2026, 10, 15)
day_after = datetime(2026, 10, 16)

print('=== 今日（10-14）截止 ===')
for item in data:
    deadline_str = item.get('deadline', '')
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str[:10], '%Y-%m-%d')
            if deadline.date() == today.date():
                print(f"  {item['company']} | {deadline_str} | {item.get('industry', '')} | {item.get('ownership', '')}")
        except:
            pass

print()
print('=== 明日（10-15）截止 ===')
for item in data:
    deadline_str = item.get('deadline', '')
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str[:10], '%Y-%m-%d')
            if deadline.date() == tomorrow.date():
                print(f"  {item['company']} | {deadline_str} | {item.get('industry', '')} | {item.get('ownership', '')}")
        except:
            pass

print()
print('=== 后日（10-16）截止 ===')
for item in data:
    deadline_str = item.get('deadline', '')
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str[:10], '%Y-%m-%d')
            if deadline.date() == day_after.date():
                print(f"  {item['company']} | {deadline_str} | {item.get('industry', '')} | {item.get('ownership', '')}")
        except:
            pass

print()
print('=== 未来7天（10-14 至 10-20）截止汇总 ===')
for i in range(7):
    day = today + timedelta(days=i)
    count = 0
    names = []
    for item in data:
        deadline_str = item.get('deadline', '')
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str[:10], '%Y-%m-%d')
                if deadline.date() == day.date():
                    count += 1
                    names.append(item['company'])
            except:
                pass
    print(f"  {day.strftime('%m-%d')}：{count}家")
    if count > 0 and count <= 10:
        print(f"    {', '.join(names)}")

print()
print('=== 数据巡检 ===')
print(f"  总企业数：{meta['company_count']}")
print(f"  数据日期：{meta['data_date']}")
print(f"  版本：{meta['version']}")
has_deadline = sum(1 for item in data if item.get('deadline'))
print(f"  有截止日期：{has_deadline}")
verified = sum(1 for item in data if item.get('verified_at'))
print(f"  已核验：{verified}")
print(f"  待核验：{has_deadline - verified}")
status_count = {}
for item in data:
    s = item.get('status', 'unknown')
    status_count[s] = status_count.get(s, 0) + 1
print(f"  状态分布：{status_count}")

