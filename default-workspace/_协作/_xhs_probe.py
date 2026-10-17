# -*- coding: utf-8 -*-
"""小红书可访问性探测：搜索页 / 发现页 / 笔记详情页（评论区）"""
import os, re, subprocess

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = r"_协作\_浏览器取证\xhs"
os.makedirs(BASE, exist_ok=True)

TARGETS = [
    ("xhs_home",    "小红书首页",       "https://www.xiaohongshu.com"),
    ("xhs_explore", "发现页",           "https://www.xiaohongshu.com/explore"),
    ("xhs_search",  "搜索·秋招",        "https://www.xiaohongshu.com/search_result?keyword=%E7%A7%8B%E6%8B%9B"),
    ("xhs_search2", "搜索·秋招(带type)", "https://www.xiaohongshu.com/search_result?keyword=%E7%A7%8B%E6%8B%9B&type=51"),
]

def dump(url, out, extra=None):
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--disable-dev-shm-usage", "--virtual-time-budget=20000",
           "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
           "--dump-dom", url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=110)
        html = r.stdout.decode("utf-8", errors="ignore")
        open(out, "w", encoding="utf-8").write(html)
        return len(html)
    except Exception as e:
        print("   ERR:", str(e)[:80])
        return -1

def totext(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()

for key, name, url in TARGETS:
    out = os.path.join(BASE, key + ".html")
    n = dump(url, out)
    print(f"\n=== {name} ({key}) ===")
    print(f"    {url}")
    print(f"    html字节={n}")
    if n > 200:
        html = open(out, encoding="utf-8", errors="ignore").read()
        t = totext(html)
        print(f"    纯文本长度={len(t)}")
        # 判断是否登录墙
        for kw in ["登录", "验证", "扫码", "安全验证", "滑块", "请稍后再试", "noteDetail", "search-result"]:
            if kw in t:
                print(f"    ⚠️ 含「{kw}」")
        print("    前400字:", t[:400])
        # 找笔记 ID / 链接
        ids = sorted(set(re.findall(r'/explore/([0-9a-f]{24})', html)) |
                     set(re.findall(r'/discovery/item/([0-9a-f]{24})', html)) |
                     set(re.findall(r'note/([\w]{20,})', html)))
        print(f"    提取到笔记ID {len(ids)} 个:", ids[:8])
    elif n >= 0:
        print("    ⚠️ 空/近空页面（可能被拦截）")
        print("    原始内容:", open(out, encoding="utf-8", errors="ignore").read()[:200])
