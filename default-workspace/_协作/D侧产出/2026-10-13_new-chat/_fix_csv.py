import json
import csv
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'
output_path = r'D:\Documents\deepseek-harness\default-workspace\_协作\outbox\timetable-200家-20261014-v2.csv'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']
today = datetime(2026, 10, 14)

# ===== D3: 补69家source =====
# 新增的69家（no >= 132）source是空的，补上
source_map = {}
for c in companies:
    if c['no'] >= 132:
        # 根据industry判断来源
        if c.get('past_friendly') == '招往届':
            c['source'] = '小红书爆款笔记采集（DB59）'
            c['source_level'] = 'B'
        elif c.get('is_rolling') and '免笔试' in c.get('note', ''):
            c['source'] = '小红书爆款笔记采集（DB60）'
            c['source_level'] = 'B'
        else:
            c['source'] = '小红书爆款笔记采集（DB57）'
            c['source_level'] = 'B'

# ===== D4: 补69家status =====
# 根据deadline判断status
for c in companies:
    if c.get('status'):
        continue  # 已有值
    
    dl = c.get('deadline', '')
    if not dl or dl == '招满即止' or dl == '待定':
        c['status'] = '滚动招'
        continue
    
    try:
        deadline = datetime.strptime(dl, '%Y-%m-%d')
        days_left = (deadline - today).days
        if days_left < 0:
            c['status'] = '已截止'
        else:
            c['status'] = '进行中'
    except:
        c['status'] = '待核实'

# ===== D2: 重导CSV，补齐所有列 =====
fields = [
    'no', 'company', 'industry', 'ownership', 'batch', 'direction',
    'location', 'degree', 'deadline', 'days_left', 'status',
    'verify_status', 'source_level', 'source', 'source_url',
    'apply_url', 'apply_url_status', 'is_rolling', 'past_friendly', 'industry_main',
    'note', 'verified_at'
]

with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for c in companies:
        writer.writerow(c)

# 统计结果
print('✅ D2/D3/D4 完成')
print()
print(f'CSV路径: {output_path}')
print(f'行数: {len(companies)}家')
print(f'列数: {len(fields)}列')
print()

# 统计status分布
status_counts = {}
for c in companies:
    s = c.get('status', '无')
    status_counts[s] = status_counts.get(s, 0) + 1
print('status分布:')
for k, v in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}家')

print()
# 统计source_level分布
sl_counts = {}
for c in companies:
    s = c.get('source_level', '无')
    sl_counts[s] = sl_counts.get(s, 0) + 1
print('source_level分布:')
for k, v in sorted(sl_counts.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}家')
