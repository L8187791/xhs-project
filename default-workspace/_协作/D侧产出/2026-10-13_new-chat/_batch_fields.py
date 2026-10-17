import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']

# ===== 补字段③：招满即止标注 =====
rolling_count = 0
for c in companies:
    dl = c.get('deadline', '')
    note = c.get('note', '')
    # 判断是否是招满即止/滚动招
    if dl == '招满即止' or not dl or dl == '待定' or '招满即止' in note:
        c['is_rolling'] = True
        rolling_count += 1
    else:
        c['is_rolling'] = False

print(f'③ 招满即止标注: {rolling_count}家')

# ===== 补字段②：是否招往届 =====
past_friendly_count = 0
past_unknown_count = 0
past_no_count = 0

for c in companies:
    note = c.get('note', '')
    company = c.get('company', '')
    
    # 根据备注判断
    if any(k in note for k in ['往届', '毕业一两年', '24/25', '25/26', '26/27', '往届友好', '往届也收']):
        c['past_friendly'] = '招往届'
        past_friendly_count += 1
    elif any(k in note for k in ['仅限应届', '只要27届', '必须应届']):
        c['past_friendly'] = '不招'
        past_no_count += 1
    else:
        c['past_friendly'] = '未明确'
        past_unknown_count += 1

print(f'② 是否招往届:')
print(f'  招往届: {past_friendly_count}家')
print(f'  不招: {past_no_count}家')
print(f'  未明确: {past_unknown_count}家')

# ===== 补字段④：行业整理（统一分类）=====
# 把零散的行业归到大类
industry_map = {
    '银行': '金融',
    '券商': '金融',
    '金融科技': '金融',
    '国企/央企': '综合央企',
    '互联网': '互联网',
    '快消': '消费',
    '零售': '消费',
    '汽车': '制造',
    '新能源/汽车': '制造',
    '新能源': '制造',
    '科技/硬件': '科技',
    '专业服务': '专业服务',
    '游戏': '文化娱乐',
    '直播': '文化娱乐',
    '物流': '物流运输',
    '教育': '教育',
    '医药': '医疗健康',
    '医疗': '医疗健康',
    '美妆': '消费',
    '农业科技': '农业',
    '化工': '制造',
    '建筑': '建筑',
    '软件': '科技',
    '通信': '科技',
    '工业': '制造',
}

for c in companies:
    old_ind = c.get('industry', '未知')
    c['industry_main'] = industry_map.get(old_ind, old_ind)

print()
print('④ 行业大类整理完成')

# ===== 保存 =====
data['meta']['version'] = 'v1.0.19'
data['meta']['data_date'] = '2026-10-14'
data['meta']['built_at'] = '2026-10-14 17:00'
data['meta']['changelog'] = 'v1.0.19: 批量补字段（招满即止标注/是否招往届/行业大类整理）'

with open(input_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print()
print('✅ 批量补字段完成')
print()
print('=== 字段补全进度 ===')
print('✅ ③ 招满即止标注: 全部完成')
print('✅ ② 是否招往届: 全部完成')
print('✅ ④ 行业大类整理: 全部完成')
print('⏳ ① 招聘方向缺值: 53家待补')
