# -*- coding: utf-8 -*-
import json, datetime

P = r"D:/小红书项目/default-workspace/技能包_时间表查询官/data/timetable.json"
d = json.load(open(P, encoding="utf-8"))
meta = d.get("meta", {})
comps = d.get("companies", [])

today = datetime.date(2026, 10, 17)
lo = today - datetime.timedelta(days=3)   # 含近 3 天已过
hi = today + datetime.timedelta(days=21)  # 未来 21 天

print("=== META ===")
print(json.dumps(meta, ensure_ascii=False))

rows = []
for c in comps:
    dl = c.get("deadline") or c.get("网申截止") or c.get("截止日")
    if not dl:
        continue
    s = str(dl).strip()
    dt = None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y年%m月%d日"):
        try:
            dt = datetime.datetime.strptime(s, fmt).date()
            break
        except ValueError:
            pass
    if dt is None:
        continue
    if lo <= dt <= hi:
        delta = (dt - today).days
        rows.append((delta, dt.isoformat(), c.get("name") or c.get("企业名") or c.get("company"), c.get("source_level"), c.get("industry") or c.get("industry_tag")))

rows.sort(key=lambda x: (x[0], x[2] or ""))
print("=== HIT COUNT ===", len(rows))
print("=== FIELDS OF SAMPLE ===", list(comps[0].keys()) if comps else "none")
for r in rows:
    print(f"{r[0]:>4} | {r[1]} | {r[2]} | level={r[3]} | {r[4]}")
