import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']
total = len(companies)

print(f'=== 现状统计（{total}家）===')
print()

# ① 招聘方向缺值
missing_direction = sum(1 for c in companies if not c.get('direction'))
print(f'① 招聘方向缺值: {missing_direction}家')

# ② 是否招往届（现在没有这个字段）
has_past_field = sum(1 for c in companies if 'past_friendly' in c)
print(f'② 是否招往届: 无此字段，需新增')

# ③ 招满即止标注
rolling = sum(1 for c in companies if c.get('deadline') == '招满即止' or not c.get('deadline'))
print(f'③ 招满即止/无日期: {rolling}家')

# ④ 行业/城市
print(f'④ 行业分布:')
industry_count = {}
for c in companies:
    ind = c.get('industry', '未知')
    industry_count[ind] = industry_count.get(ind, 0) + 1
for ind, cnt in sorted(industry_count.items(), key=lambda x: -x[1]):
    print(f'  {ind}: {cnt}家')

print()
print(f'工作地点写"全国"的: {sum(1 for c in companies if c.get("location") == "全国")}家')
