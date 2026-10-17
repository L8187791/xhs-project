import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']
new_companies = [c for c in companies if c['no'] >= 132]

print('新增数量:', len(new_companies), '家')
print()

verify_levels = {}
for c in new_companies:
    vs = c.get('verify_status', '未知')
    verify_levels[vs] = verify_levels.get(vs, 0) + 1

print('核实状态分布:')
for vs, cnt in sorted(verify_levels.items(), key=lambda x: -x[1]):
    print(f'  {vs}: {cnt}家')

print()
has_date = 0
rolling = 0
for c in new_companies:
    dl = c.get('deadline', '')
    if dl and dl != '招满即止' and dl != '待定':
        has_date += 1
    else:
        rolling += 1

print(f'有具体截止日期: {has_date}家')
print(f'滚动招/待定: {rolling}家')

print()
print('近期截止的新增企业:')
recent = []
for c in new_companies:
    dl = c.get('deadline', '')
    if dl and dl != '招满即止' and dl != '待定':
        recent.append((c['no'], c['company'], dl))

recent.sort(key=lambda x: x[2])
for no, name, dl in recent[:15]:
    print(f'  #{no} {name}: {dl}')
