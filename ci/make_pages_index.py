# -*- coding: utf-8 -*-
"""GitHub Pages 站点组装：把工作区根目录的 HTML 看板拷入 _site/ 并生成索引页。

被 deploy job 调用（python ci/make_pages_index.py）。
纪律：只读 default-workspace，只写仓库根 _site/。
"""
import io
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = os.path.join(ROOT, "default-workspace")
SITE = os.path.join(ROOT, "_site")

HTML_FILES = sorted(
    f for f in os.listdir(WS)
    if f.endswith(".html") and not f.startswith("~")
)

CARDS = [
    ("求职项目进展.md", "求职项目进展（总台账）"),
    ("项目交接文件_20261015.md", "项目交接文件"),
]

def main():
    if os.path.exists(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE)

    for f in HTML_FILES:
        shutil.copy2(os.path.join(WS, f), os.path.join(SITE, f))

    rows = "\n".join(
        '<li><a href="%s">%s</a></li>' % (f, f) for f in HTML_FILES
    )
    doc_rows = "\n".join(
        '<li><a href="%s">%s</a>%s</li>' % (src, title,
            "" if os.path.exists(os.path.join(WS, src)) else ' <em>（缺失）</em>')
        for src, title in CARDS
    )
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>小红书项目 · 看板索引</title>
<style>
  body { font-family: "Microsoft YaHei", system-ui, sans-serif; max-width: 720px;
         margin: 2rem auto; padding: 0 1rem; color: #222; }
  h1 { font-size: 1.4rem; border-bottom: 2px solid #e44; padding-bottom: .4rem; }
  h2 { font-size: 1.1rem; margin-top: 1.6rem; }
  li { margin: .3rem 0; }
  .meta { color: #888; font-size: .85rem; }
</style>
</head>
<body>
<h1>小红书项目 · 看板索引</h1>
<p class="meta">由 GitHub Actions 自动构建 · commit %COMMIT%</p>
<h2>数据看板</h2>
<ul>
%ROWS%
</ul>
<h2>台账文档</h2>
<ul>
%DOCROWS%
</ul>
</body>
</html>
"""
    html = (html.replace("%COMMIT%", os.environ.get("GITHUB_SHA", "local"))
                .replace("%ROWS%", rows)
                .replace("%DOCROWS%", doc_rows))
    with io.open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print("已组装 _site/：%d 个 HTML 看板 + index.html" % len(HTML_FILES))
    for f in HTML_FILES:
        print("  -", f)


if __name__ == "__main__":
    main()
