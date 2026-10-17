# -*- coding: utf-8 -*-
"""补充抓取（10-17 第二轮）· 目标：给头部账号凑够 >=3 篇可核笔记"""
import os, re, json, subprocess
PY = r"C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
FETCH = (r"C:/Users/Administrator/.workbuddy/plugins/marketplaces/experts/plugins/redfox-xhs-creator/"
         r"skills/xiaohongshu-write/scripts/fetch_xhs_hot_articles.py")
ENV = dict(os.environ); ENV["PYTHONUTF8"] = "1"; ENV["PYTHONIOENCODING"] = "utf-8"
ENV["REDFOX_API_KEY"] = re.search(r"REDFOX_API_KEY=(\S+)",
    open(os.path.expanduser("~/.workbuddy/redfox.env"), encoding="utf-8").read()).group(1).strip().strip('"')
D = os.path.dirname(os.path.abspath(__file__))
KWS = ["今天刚开的秋招", "秋招截止汇总", "秋招汇总表", "秋招 最后一天", "应届生秋招截止", "秋招投递"]
for kw in KWS:
    p = subprocess.run([PY, FETCH, "--keyword", kw, "--max-items", "30", "--page-size", "50",
                        "--output-format", "json", "--start-date", "2026-09-17"],
                       capture_output=True, env=ENV, timeout=200, cwd=D)
    s = (p.stdout or b"").decode("utf-8", errors="replace")
    i = s.find("{")
    if i < 0:
        print("KW %-14s FAIL rc=%s" % (kw, p.returncode)); continue
    obj, _ = json.JSONDecoder().raw_decode(s[i:])
    items = obj.get("items") or []
    fn = os.path.join(D, "redfox2_%s_1017.json" % kw.replace(" ", "_"))
    json.dump(obj, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("KW %-14s total=%s items=%d" % (kw, obj.get("total"), len(items)))
print("DONE2")
