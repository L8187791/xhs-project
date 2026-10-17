# -*- coding: utf-8 -*-
import os, re, sys

BASE = r"_协作\_浏览器取证\20261014"

def totext(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()

for key in sys.argv[1:]:
    p = os.path.join(BASE, key + ".html")
    if not os.path.exists(p):
        print(f"--- {key}: 无文件"); continue
    html = open(p, encoding="utf-8", errors="ignore").read()
    t = totext(html)
    print(f"\n########## {key} ##########")
    print("文本长度:", len(t))
    # 1. 关键词上下文
    for kw in ["截止", "报名", "网申", "投递", "2027届", "2026届", "校园招聘", "秋招", "10月", "11月", "笔试"]:
        for m in list(re.finditer(re.escape(kw), t))[:2]:
            print(f"  [{kw}] ...{t[max(0,m.start()-80):m.start()+100]}...")
    # 2. 链接
    hrefs = sorted(set(re.findall(r'href=["\']([^"\']+)["\']', html)))
    hit = [h for h in hrefs if any(k in h.lower() for k in
           ["recruit","job","campus","zhaopin","hr","career","join","notice","detail","news","xwzx","tzgg"])]
    print("  --- 招聘相关链接(前15) ---")
    for h in hit[:15]:
        print("     ", h[:130])
