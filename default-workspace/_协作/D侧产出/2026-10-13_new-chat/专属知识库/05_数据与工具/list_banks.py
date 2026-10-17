import json

with open(r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

banks = []
for c in data['companies']:
    name = c.get('company', '')
    if any(k in name for k in ['银行', '工商', '农业', '中国', '建设', '交通', '邮储', '招商', '浦发', '中信', '民生', '光大', '华夏', '平安', '兴业', '广发', '浙商', '恒丰', '渤海', '农商', '齐鲁']):
        banks.append(c)

print(f"共 {len(banks)} 家银行")
print("=" * 80)
for b in banks:
    no = b['no']
    name = b['company']
    deadline = b.get('deadline', '')
    note = b.get('note', '')[:60]
    status = b.get('status', '')
    print(f"{no:3d} | {name:20s} | {deadline:12s} | {status:8s} | {note}")
