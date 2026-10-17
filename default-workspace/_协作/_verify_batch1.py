# -*- coding: utf-8 -*-
"""批量浏览器取证 v1 —— 系统 Edge headless
用法: python _verify_batch1.py
输出: _协作/_浏览器取证/20261014/<key>.html  + 控制台文本摘要
"""
import os, re, subprocess, sys, json, time

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = r"_协作\_浏览器取证\20261014"
os.makedirs(BASE, exist_ok=True)

# (key, 企业名, URL)
TARGETS = [
    ("cnpc",       "中国石油",   "https://zhaopin.cnpc.com.cn"),
    ("cgb",        "广发银行",   "https://www.cgbchina.com.cn"),
    ("bytedance",  "字节跳动",   "https://jobs.bytedance.com/campus"),
    ("catl",       "宁德时代",   "https://www.catl.com/about/join.html"),
    ("ey",         "安永",       "https://www.ey.com/zh_cn/careers/students"),
    ("chng",       "中国华能",   "https://www.chng.com.cn"),
    ("danone",     "达能",       "https://www.danone.com/en/careers.html"),
    ("chinapost",  "中国邮政",   "http://www.chinapost.com.cn"),
    ("sinomach",   "国机集团",   "https://www.sinomach.com.cn"),
]

KEYWORDS = ["截止", "报名", "网申", "10月", "11月", "12月", "2026", "2027",
            "校园招聘", "秋招", "投递", "简历", "笔试", "面试", "届"]

def dump(url, out):
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--disable-dev-shm-usage", "--virtual-time-budget=15000",
           "--dump-dom", url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=90)
        html = r.stdout.decode("utf-8", errors="ignore")
        open(out, "w", encoding="utf-8").write(html)
        return len(html)
    except Exception as e:
        return -1

def totext(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

results = []
for key, name, url in TARGETS:
    out = os.path.join(BASE, key + ".html")
    n = dump(url, out)
    row = {"key": key, "name": name, "url": url, "bytes": n, "textlen": 0, "hits": []}
    if n > 0:
        t = totext(open(out, encoding="utf-8", errors="ignore").read())
        row["textlen"] = len(t)
        row["hits"] = [k for k in KEYWORDS if k in t]
        # 抓含关键词的上下文
        ctxs = []
        for kw in ["截止", "报名", "网申", "校园招聘", "2027届", "2026届"]:
            for m in list(re.finditer(re.escape(kw), t))[:2]:
                ctxs.append(f"[{kw}] ...{t[max(0,m.start()-50):m.start()+70]}...")
        row["ctx"] = ctxs[:6]
    results.append(row)
    print(f"=== {name} ({key}) ===")
    print(f"    url={url}")
    print(f"    html字节={n} 纯文本={row['textlen']} 命中={row['hits']}")
    for c in row.get("ctx", []):
        print("    " + c)
    print()

json.dump(results, open(os.path.join(BASE, "_batch1_result.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("存档目录:", os.path.abspath(BASE))
