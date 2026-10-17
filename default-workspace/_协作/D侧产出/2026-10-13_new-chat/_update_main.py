import json
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']
today = datetime(2026, 10, 14)

# ===== D3: 补69家source =====
for c in companies:
    if c['no'] >= 132 and not c.get('source'):
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
for c in companies:
    if c.get('status'):
        continue
    
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

# 更新meta
data['meta']['version'] = 'v1.0.20'
data['meta']['data_date'] = '2026-10-14'
data['meta']['built_at'] = '2026-10-14 20:1x'
data['meta']['changelog'] = 'v1.0.20: 补69家source/status字段，重导CSV v2'

with open(input_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ 主文件已更新')
print(f'版本: v1.0.20')
print()

# 统计
status_counts = {}
for c in companies:
    s = c.get('status', '无')
    status_counts[s] = status_counts.get(s, 0) + 1
print('status分布:')
for k, v in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}家')
