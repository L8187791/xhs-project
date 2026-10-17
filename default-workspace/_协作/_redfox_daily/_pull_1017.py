# -*- coding: utf-8 -*-
"""今日红狐抓取（2026-10-17）· 求职线关键词 · 字节捕获 + 解析 JSON 落盘"""
import os, re, json, subprocess

PY = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
FETCH = (r"C:/Users/Administrator/.workbuddy/plugins/marketplaces/experts/plugins/redfox-xhs-creator/"
         r"skills/xiaohongshu-write/scripts/fetch_xhs_hot_articles.py")

ENV = dict(os.environ)
ENV["PYTHONUTF8"] = "1"
ENV["PYTHONIOENCODING"] = "utf-8"
txt = open(os.path.expanduser("~/.workbuddy/redfox.env"), encoding="utf-8").read()
m = re.search(r"REDFOX_API_KEY=(\S+)", txt)
ENV["REDFOX_API_KEY"] = m.group(1).strip().strip('"') if m else ""

D = os.path.dirname(os.path.abspath(__file__))
KWS = ["秋招截止", "网申截止", "秋招时间表", "往届生秋招", "免笔试外企", "秋招中小厂", "校招汇总表"]

total = 0
for kw in KWS:
    p = subprocess.run([PY, FETCH, "--keyword", kw, "--max-items", "30",
                        "--page-size", "50", "--output-format", "json",
                        "--start-date", "2026-09-17"],
                       capture_output=True, env=ENV, timeout=200, cwd=D)
    raw = (p.stdout or b"")
    s = raw.decode("utf-8", errors="replace")
    i = s.find("{")
    if i < 0:
        print("KW %-10s FAIL rc=%s stderr=%s" % (kw, p.returncode, (p.stderr or b"")[:200]))
        continue
    try:
        obj, _ = json.JSONDecoder().raw_decode(s[i:])
    except Exception as e:
        print("KW %-10s PARSE FAIL %s" % (kw, e)); continue
    items = obj.get("items") or []
    fn = os.path.join(D, "redfox_%s_1017.json" % kw)
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    total += len(items)
    print("KW %-10s total=%s items=%d -> %s" % (kw, obj.get("total"), len(items), os.path.basename(fn)))
print("ALL DONE total_items=%d" % total)
