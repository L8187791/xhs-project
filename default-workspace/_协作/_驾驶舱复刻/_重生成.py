# -*- coding: utf-8 -*-
"""
求职协作工作台 · 数据重生成脚本
用途：主表(timetable.json)更新后，重新把 200 家明细注入 HTML，保持看板与权威源同步。
用法：C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe _重生成.py
注意：本脚本只刷新数据，不改页面结构。跑完后请核对页脚的版本号与 data_date 是否同步更新。
"""
import json, os, re, datetime

HERE   = os.path.dirname(os.path.abspath(__file__))
SRC    = os.path.abspath(os.path.join(HERE, '..', '..', '技能包_时间表查询官', 'data', 'timetable.json'))
HTML   = os.path.join(HERE, '求职协作工作台.html')
TODAY  = datetime.date.today()

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def build_rows(data):
    """列定义：[序, 企业, 行业, 性质, 截止日, 剩余天数, 分级, 日期形态, 往届, 备注, 入口url, 来源摘要]"""
    rows = []
    for c in data['companies']:
        dl = c.get('deadline') or ''
        days = None
        try:
            days = (datetime.date.fromisoformat(str(dl)[:10]) - TODAY).days
        except Exception:
            days = None
        rows.append([
            c.get('no'), c.get('company', ''), c.get('industry', ''),
            c.get('ownership', ''), str(dl)[:10] if dl else '', days,
            (c.get('source_level') or '').strip(), c.get('date_form_cn', ''),
            (c.get('past_friendly') or '').strip(),
            (c.get('note') or '')[:40],
            c.get('apply_url', '') if c.get('apply_url_status') == 'link' else '',
            (c.get('source') or '')[:34],
        ])
    return rows

def main():
    data = load(SRC)
    meta = data.get('meta', {})
    rows = build_rows(data)
    html = open(HTML, encoding='utf-8').read()

    payload = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))
    new, n = re.subn(r'const ROWS = \[.*?\];\n', 'const ROWS = %s;\n' % payload, html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('FAIL: 未找到 const ROWS 占位，页面结构可能被改动，请人工检查')

    # 同步页脚版本信息
    ver = meta.get('version', '?'); dd = meta.get('data_date', '?')
    new = re.sub(r'主表权威源 timetable\.json v[\d.]+（data_date [\d-]+）',
                 '主表权威源 timetable.json v%s（data_date %s）' % (ver, dd), new)

    open(HTML, 'w', encoding='utf-8').write(new)
    print('OK  rows=%d  ver=%s  data_date=%s  size=%d' % (len(rows), ver, dd, len(new)))

if __name__ == '__main__':
    main()
