import json

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']

# 找出新增的69家（no >= 132的）
new_companies = [c for c in companies if c['no'] >= 132]
old_companies = [c for c in companies if c['no'] < 132]

print('=== 新增企业可信度统计 ===')
print(f'新增数量: {len(new_companies)}家')
print()

# 按核实状态分
verify_levels = {}
for c in new_companies:
    vs = c.get('verify_status', '未知')
    verify_levels[vs] = verify_levels.get(vs, 0) + 1

print('核实状态分布:')
for vs, cnt in sorted(verify_levels.items(), key=lambda x: -x[1]):
    pct = cnt * 100 // len(new_companies)
    print(f'  {vs}: {cnt}家 ({pct}%)')

print()
print('=== 硬日期 vs 滚动招 ===')
has_date = 0
rolling = 0
for c in new_companies:
    dl = c.get('deadline', '')
    if dl and dl != '招满即止' and dl != '待定':
        has_date += 1
    else:
        rolling += 1

print(f'有具体截止日期: {has_date}家 ({has_date*100//len(new_companies)}%)')
print(f'滚动招/待定: {rolling}家 ({rolling*100//len(new_companies)}%)')

print()
print('=== 重点抽查：近期截止的新增企业 ===')
# 找出有具体日期且最近的
recent = []
for c in new_companies:
    dl = c.get('deadline', '')
    if dl and dl != '招满即止' and dl != '待定':
        recent.append((c['no'], c['company'], dl, c.get('note', '')[:30]))

recent.sort(key=lambda x: x[2])
for no, name, dl, note in recent[:10]:
    print(f'  #{no} {name}: {dl}')
    print(f'      备注: {note}')
