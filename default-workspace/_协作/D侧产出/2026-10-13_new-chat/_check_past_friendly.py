import json

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = data['companies']

# 粗筛：哪些企业备注里可能提到往届生/毕业年份宽松
past_friendly = []
for c in companies:
    note = c.get('note', '')
    direction = c.get('direction', '')
    # 关键词匹配
    keywords = ['往届', '毕业', '届', '25届', '26届', '不限', '宽松']
    if any(k in note for k in keywords):
        past_friendly.append((c['company'], c.get('note', '')[:50]))

print('=== 现有131家里疑似往届生友好的 ===')
print(f'粗筛出: {len(past_friendly)}家')
print()
for name, note in past_friendly[:20]:
    print(f'  {name}')
    print(f'    备注: {note}')
    print()
