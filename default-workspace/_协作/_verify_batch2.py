# -*- coding: utf-8 -*-
import os, re, subprocess, json

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = r"_协作\_浏览器取证\20261014"
os.makedirs(BASE, exist_ok=True)

TARGETS = [
    ("ey_campus",  "安永校招官网",        "https://careers.ey.com.cn"),
    ("post_zl",    "邮政2027网申(智联)",  "https://chinapost2027.zhaopin.com"),
    ("post_jl",    "邮政吉林分公司公告",  "https://jilin.chinapost.com.cn/jl/report/2609/1875-1.html"),
    ("cnpc2",      "中石油招聘(备用)",    "https://zhaopin.cnpc.com.cn/recruit"),
    ("cgb_hr",     "广发银行招聘",        "https://www.cgbchina.com.cn/Channel/11581868"),
    ("sinomach2",  "国机集团招聘",        "http://job.sinomach.com.cn"),
    ("catl2",      "宁德时代招聘",        "https://hr.catl.com"),
]

def dump(url, out):
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--disable-dev-shm-usage", "--virtual-time-budget=18000",
           "--dump-dom", url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=100)
        html = r.stdout.decode("utf-8", errors="ignore")
        open(out, "w", encoding="utf-8").write(html)
        return len(html)
    except Exception as e:
        print("ERR", e); return -1

def totext(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()

KW = ["截止", "报名", "网申", "投递", "10月16日", "10月31日", "2026-10-31",
      "2026-10-16", "校园招聘", "秋招", "笔试", "面试", "2027届", "2026届", "择业期"]

for key, name, url in TARGETS:
    out = os.path.join(BASE, key + ".html")
    n = dump(url, out)
    print(f"\n=== {name} ({key}) ===")
    print(f"    {url}  html={n}")
    if n > 200:
        t = totext(open(out, encoding="utf-8", errors="ignore").read())
        print(f"    纯文本={len(t)}")
        found = False
        for kw in KW:
            for m in list(re.finditer(re.escape(kw), t))[:2]:
                print(f"    [{kw}] ...{t[max(0,m.start()-70):m.start()+90]}...")
                found = True
        if not found:
            print("    前300字:", t[:300])
