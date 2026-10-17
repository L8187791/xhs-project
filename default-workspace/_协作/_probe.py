import json, collections, os

p = r"技能包_时间表查询官/data/timetable.json"
print("path:", os.path.abspath(p))
print("size:", os.path.getsize(p))
d = json.load(open(p, encoding="utf-8"))
print("top type:", type(d).__name__)
if isinstance(d, dict):
    print("top keys:", list(d.keys())[:20])
    ents = d.get("entries") or d.get("companies") or []
else:
    ents = d
print("ents len:", len(ents))
if ents:
    print("sample0 keys:", sorted(ents[0].keys()))
    print("sample company:", ents[0].get("company"))
    print("source_level dist:", collections.Counter(str(e.get("source_level")) for e in ents))
    print("status dist:", collections.Counter(str(e.get("status")) for e in ents))
    lv = collections.Counter(str(e.get("source_level")) for e in ents)
    print()
    print("=== A 级 ===")
    for e in ents:
        if str(e.get("source_level")) == "A":
            print(f"  {e.get('company')} | deadline={e.get('deadline')} | status={e.get('status')} | src={str(e.get('source'))[:45]} | url={str(e.get('source_url'))[:55]}")
