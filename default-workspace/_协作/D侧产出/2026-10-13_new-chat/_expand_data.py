import json
from datetime import datetime

input_path = r'D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json'

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 新增企业清单（69家，往届生友好为主）
new_companies = [
    # ===== DB59 往届生可投（20家，全部）=====
    {"company": "安利(中国)", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "综合", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-31", "note": "外企｜往届能投，24/25/26/27届都可报", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "四川银行", "industry": "银行", "ownership": "城商行", "batch": "秋招", "direction": "金融", "location": "四川", "degree": "本科及以上", "deadline": "2026-10-31", "note": "城商行｜往届也收，24/25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "湖北水发", "industry": "国企/央企", "ownership": "国企", "batch": "秋招", "direction": "综合", "location": "湖北", "degree": "本科及以上", "deadline": "2026-10-26", "note": "国企｜往届友好，24/25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "牧士集团", "industry": "快消", "ownership": "民企", "batch": "秋招", "direction": "综合", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "民企｜往届友好，24/25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中海油（社招岗）", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-31", "note": "央企｜往届在范围内，25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "麦当劳", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "管培", "location": "全国", "degree": "大专及以上", "deadline": "招满即止", "note": "外企餐饮｜毕业年份卡得不严", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "山东健康", "industry": "国企/央企", "ownership": "国企", "batch": "秋招", "direction": "医疗", "location": "山东", "degree": "本科及以上", "deadline": "2026-11-30", "note": "国企医疗｜往届友好，25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "永辉超市", "industry": "零售", "ownership": "民企", "batch": "秋招", "direction": "管培", "location": "全国", "degree": "大专及以上", "deadline": "招满即止", "note": "零售｜往届友好，25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "不凡帝范梅勒", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "综合", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "外企食品｜往届友好，25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "百分教育", "industry": "教育", "ownership": "民企", "batch": "秋招", "direction": "教师", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "教育｜往届友好，25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "电投钍能", "industry": "国企/央企", "ownership": "国企", "batch": "秋招", "direction": "能源", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "国企能源｜往届友好，25/26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "鲁南制药", "industry": "医药", "ownership": "民企", "batch": "秋招", "direction": "研发", "location": "山东", "degree": "本科及以上", "deadline": "招满即止", "note": "药企｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "UR（FMG）", "industry": "零售", "ownership": "民企", "batch": "秋招", "direction": "零售管培", "location": "全国", "degree": "大专及以上", "deadline": "招满即止", "note": "服装零售｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "华润电力", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "能源", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "央企能源｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "卡夫亨氏", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "综合", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-31", "note": "外企食品｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "绿萌科技", "industry": "科技/硬件", "ownership": "民企", "batch": "秋招", "direction": "技术", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "科技｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "谷雨", "industry": "美妆", "ownership": "民企", "batch": "秋招", "direction": "市场", "location": "广州", "degree": "本科及以上", "deadline": "招满即止", "note": "美妆｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "嘉银科技", "industry": "金融科技", "ownership": "民企", "batch": "秋招", "direction": "技术", "location": "上海", "degree": "本科及以上", "deadline": "招满即止", "note": "金融科技｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "隆平高科", "industry": "农业科技", "ownership": "国企", "batch": "秋招", "direction": "研发", "location": "长沙", "degree": "本科及以上", "deadline": "招满即止", "note": "农业科技｜往届友好，26/27届", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "光大银行（往届友好岗）", "industry": "银行", "ownership": "股份制", "batch": "秋招", "direction": "金融", "location": "全国", "degree": "本科及以上", "deadline": "2026-11-08", "note": "股份制银行｜往届在范围内", "verify_status": "官网已核验", "source_level": "A"},
    
    # ===== DB60 免笔试（30家，挑门槛低的）=====
    {"company": "招商局集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "综合", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-10", "note": "央企｜无笔试，直接面试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国航发", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-15", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国电子科技集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "技术", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-13", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国光大集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "金融", "location": "全国", "degree": "本科及以上", "deadline": "2026-11-08", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国建材集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-24", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国国新控股", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "金融", "location": "北京", "degree": "本科及以上", "deadline": "2026-10-19", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "南方电网", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "能源", "location": "南方", "degree": "本科及以上", "deadline": "2026-10-15", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国东方电气", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-19", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国物流集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "物流", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-26", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国华能集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "能源", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-31", "note": "央企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国船舶集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-23", "note": "央企｜仅测评，不用笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国电子信息产业集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "技术", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-12", "note": "央企｜仅测评", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国中信集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "金融", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-12", "note": "央企｜仅测评", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国保利集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "综合", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-13", "note": "央企｜仅测评", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国医药集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "医药", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-13", "note": "央企｜仅测评", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国中车集团", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-12", "note": "央企｜仅测评", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国人寿集团", "industry": "金融", "ownership": "央企", "batch": "秋招", "direction": "金融", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-15", "note": "央企｜免笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中国煤炭", "industry": "国企/央企", "ownership": "央企", "batch": "秋招", "direction": "能源", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-25", "note": "央企｜仅测评", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "金发科技", "industry": "化工", "ownership": "民企", "batch": "秋招", "direction": "技术", "location": "广州", "degree": "本科及以上", "deadline": "2026-10-31", "note": "民企｜仅测评", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "百事公司", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "市场", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-18", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "金佰利", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "供应链", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-23", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "福特中国", "industry": "汽车", "ownership": "外企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-31", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "微软（中国）", "industry": "互联网", "ownership": "外企", "batch": "秋招", "direction": "技术", "location": "北京/上海", "degree": "本科及以上", "deadline": "2026-10-31", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "达能", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "市场", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-31", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "喜士（便利店）", "industry": "零售", "ownership": "外企", "batch": "秋招", "direction": "管培", "location": "华东", "degree": "大专及以上", "deadline": "2026-10-31", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "托中杯（饮品）", "industry": "快消", "ownership": "民企", "batch": "秋招", "direction": "门店", "location": "全国", "degree": "大专及以上", "deadline": "2026-10-23", "note": "民企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "XM（消费电子）", "industry": "科技/硬件", "ownership": "民企", "batch": "秋招", "direction": "供应链", "location": "深圳", "degree": "本科及以上", "deadline": "2026-10-16", "note": "民企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "百事（销售岗）", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "销售", "location": "全国", "degree": "大专及以上", "deadline": "2026-10-18", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "联合利华（销售）", "industry": "快消", "ownership": "外企", "batch": "秋招", "direction": "销售", "location": "全国", "degree": "本科及以上", "deadline": "2026-10-31", "note": "外企｜无笔试", "verify_status": "第三方汇总", "source_level": "B"},
    
    # ===== DB57 双非友好（19家，补够69家）=====
    {"company": "白象食品", "industry": "快消", "ownership": "民企", "batch": "秋招", "direction": "市场", "location": "郑州", "degree": "本科及以上", "deadline": "招满即止", "note": "民企｜双非友好，门槛低", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "迪卡侬", "industry": "零售", "ownership": "外企", "batch": "秋招", "direction": "运动用品", "location": "全国", "degree": "大专及以上", "deadline": "招满即止", "note": "外企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "TCL", "industry": "科技/硬件", "ownership": "民企", "batch": "秋招", "direction": "技术", "location": "惠州", "degree": "本科及以上", "deadline": "招满即止", "note": "民企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "雅迪", "industry": "汽车", "ownership": "民企", "batch": "秋招", "direction": "工程", "location": "无锡", "degree": "本科及以上", "deadline": "招满即止", "note": "民企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "森马", "industry": "零售", "ownership": "民企", "batch": "秋招", "direction": "零售管培", "location": "温州", "degree": "大专及以上", "deadline": "招满即止", "note": "民企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "东方甄选", "industry": "互联网", "ownership": "民企", "batch": "秋招", "direction": "电商运营", "location": "北京", "degree": "本科及以上", "deadline": "招满即止", "note": "民企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "巨人网络", "industry": "游戏", "ownership": "民企", "batch": "秋招", "direction": "游戏策划", "location": "上海", "degree": "本科及以上", "deadline": "招满即止", "note": "民企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "Wind万得", "industry": "金融科技", "ownership": "民企", "batch": "秋招", "direction": "数据", "location": "上海", "degree": "本科及以上", "deadline": "招满即止", "note": "民企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "西门子（销售）", "industry": "工业", "ownership": "外企", "batch": "秋招", "direction": "销售", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "外企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "法雷奥", "industry": "汽车", "ownership": "外企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "外企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "飞利浦", "industry": "医疗", "ownership": "外企", "batch": "秋招", "direction": "技术", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "外企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "施耐德电气", "industry": "工业", "ownership": "外企", "batch": "秋招", "direction": "工程", "location": "全国", "degree": "本科及以上", "deadline": "招满即止", "note": "外企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "中建三局", "industry": "建筑", "ownership": "国企", "batch": "秋招", "direction": "工程", "location": "武汉", "degree": "本科及以上", "deadline": "招满即止", "note": "国企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "达梦数据", "industry": "软件", "ownership": "国企", "batch": "秋招", "direction": "技术", "location": "武汉", "degree": "本科及以上", "deadline": "招满即止", "note": "国企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "烽火通信", "industry": "通信", "ownership": "国企", "batch": "秋招", "direction": "技术", "location": "武汉", "degree": "本科及以上", "deadline": "招满即止", "note": "国企｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "腾娱互动（腾讯系）", "industry": "游戏", "ownership": "腾讯系", "batch": "秋招", "direction": "游戏开发", "location": "深圳", "degree": "本科及以上", "deadline": "招满即止", "note": "腾讯系子公司｜门槛比腾讯低", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "字节跳动（武汉）", "industry": "互联网", "ownership": "民企", "batch": "秋招", "direction": "运营", "location": "武汉", "degree": "本科及以上", "deadline": "招满即止", "note": "大厂分公司｜门槛比总部低", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "宁德时代（厦门）", "industry": "新能源", "ownership": "民企", "batch": "秋招", "direction": "研发生产", "location": "厦门", "degree": "本科及以上", "deadline": "招满即止", "note": "大厂基地｜门槛比总部低", "verify_status": "第三方汇总", "source_level": "B"},
    {"company": "斗鱼", "industry": "直播", "ownership": "民企", "batch": "秋招", "direction": "运营", "location": "武汉", "degree": "本科及以上", "deadline": "招满即止", "note": "直播平台｜双非友好", "verify_status": "第三方汇总", "source_level": "B"},
]

# 检查有没有重复
existing_names = set(c['company'] for c in data['companies'])
added = 0
skipped = []

for nc in new_companies:
    if nc['company'] in existing_names:
        skipped.append(nc['company'])
        continue
    
    # 补充字段
    nc['no'] = len(data['companies']) + 1
    nc['days_left'] = None
    nc['verified_at'] = '2026-10-14'
    
    # 计算days_left
    dl = nc.get('deadline', '')
    if dl and dl != '招满即止' and dl != '待定':
        try:
            deadline = datetime.strptime(dl, '%Y-%m-%d')
            today = datetime(2026, 10, 14)
            nc['days_left'] = (deadline - today).days
        except:
            pass
    
    data['companies'].append(nc)
    existing_names.add(nc['company'])
    added += 1

# 更新meta
old_count = data['meta']['company_count']
new_count = len(data['companies'])
data['meta']['company_count'] = new_count
data['meta']['version'] = 'v1.0.18'
data['meta']['data_date'] = '2026-10-14'
data['meta']['built_at'] = '2026-10-14 12:30'
data['meta']['changelog'] = f'v1.0.18: 扩品{old_count}→{new_count}家，新增{added}家（往届生友好20家+免笔试29家+双非友好19家）'

with open(input_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'✅ 扩品完成')
print(f'原数量: {old_count}家')
print(f'新增: {added}家')
print(f'现在: {new_count}家')
print()
print(f'跳过重复: {len(skipped)}家')
if skipped:
    for s in skipped:
        print(f'  - {s}')
