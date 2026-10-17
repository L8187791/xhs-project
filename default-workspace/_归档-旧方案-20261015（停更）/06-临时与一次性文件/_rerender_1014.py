# -*- coding: utf-8 -*-
"""10/14 三篇配图 · 方案A 重渲（统一米白底 / 统一黑底页脚 / 统一左竖条 / Noto Sans SC / 严格图序）"""
import sys, os
WS = r"D:/Documents/deepseek-harness/default-workspace"
sys.path.insert(0, WS)
import ganhuo_lib as G

def load_notes(fname):
    p = os.path.join(WS, fname)
    g = {"__name__": "_notmain_", "__file__": p}
    exec(compile(open(p, encoding="utf-8").read(), fname, "exec"), g)
    return g.get("NOTES", [])

notes = load_notes("_render_db47_1416.py") + load_notes("_render_wj_102.py")
print("载入总篇数 =", len(notes))
targets = [n for n in notes if n["no"].startswith("1014-")]
print("10/14 目标 =", [n["no"] for n in targets])
assert len(targets) == 3, "应恰好 3 篇"

PKG = os.path.join(WS, "_协作", "outbox", "发布包-XHS-20261014_16-WB")
for n in targets:
    outdir = os.path.join(PKG, "图-往届生" if n["no"].endswith("WJ") else "图")
    print("--- %s -> %s" % (n["no"], os.path.basename(outdir)))
    G.render(n, outdir)      # strict=True：图序不合规会直接报错
print("\n全部完成（已过严格图序校验）")
