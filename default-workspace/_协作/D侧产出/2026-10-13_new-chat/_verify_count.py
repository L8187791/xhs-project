import json

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

meta_count = data['meta']['company_count']
actual_count = len(data['companies'])

print('=== 131家宣称 vs 实际数据 ===')
print(f'meta里写的company_count: {meta_count}')
print(f'实际companies数组长度: {actual_count}')
print()

if meta_count == actual_count:
    print('✅ 一致')
else:
    print(f'❌ 不一致！差了{abs(meta_count - actual_count)}家')
    if actual_count > meta_count:
        print(f'   实际比宣称多了{actual_count - meta_count}家')
    else:
        print(f'   实际比宣称少了{meta_count - actual_count}家')

print()
print('=== 数据质量抽查 ===')

# 检查有没有重复企业名
company_names = [c['company'] for c in data['companies']]
duplicates = set([x for x in company_names if company_names.count(x) > 1])
if duplicates:
    print(f'⚠️ 重复企业名: {duplicates}')
else:
    print('✅ 无重复企业名')

# 检查关键字段缺失
missing_deadline = sum(1 for c in data['companies'] if not c.get('deadline') or c.get('deadline') == '待定')
missing_company = sum(1 for c in data['companies'] if not c.get('company'))
print(f'缺截止日期: {missing_deadline}家')
print(f'缺企业名: {missing_company}家')

# 按行业分类统计
industry_count = {}
for c in data['companies']:
    ind = c.get('industry', '未知')
    industry_count[ind] = industry_count.get(ind, 0) + 1

print()
print('=== 行业分布 ===')
for ind, cnt in sorted(industry_count.items(), key=lambda x: -x[1]):
    print(f'  {ind}: {cnt}家')
