# -*- coding: utf-8 -*-
"""同步技能：工作区 .codebuddy/skills → WorkBuddy 项目资源（实体副本）

为什么需要：WorkBuddy 不认 junction（实测 reparse point 但技能注册表不收），
只认「项目资源目录下的实体目录」。所以源与副本必须手动/脚本同步。

🔴 规则（部署清单）：
   改了工作区 .codebuddy/skills/ 里的任何文件 → 必须跑一次本脚本。
   本脚本会把「源」覆盖到「副本」，并打印差异。
"""
import io, os, sys, filecmp, shutil, datetime
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
SRC = os.path.join(WS, ".codebuddy", "skills")
DST = r"C:\Users\Administrator\.workbuddy\project-resources\p_76fa99a297f34c0e8eb4ee3df2408fb4"

def diff(a, b):
    out = []
    for root, dirs, fs in os.walk(a):
        for f in fs:
            p1 = os.path.join(root, f)
            rel = os.path.relpath(p1, a)
            p2 = os.path.join(b, rel)
            if not os.path.exists(p2):
                out.append(("新增", rel))
            elif not filecmp.cmp(p1, p2, shallow=False):
                out.append(("更新", rel))
    return out

print("=" * 66)
print("技能同步 · %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 66)
total = 0
for n in sorted(os.listdir(SRC)):
    s, d = os.path.join(SRC, n), os.path.join(DST, n)
    if not os.path.isdir(s):
        continue
    if os.path.islink(d) or (os.path.exists(d) and not os.path.isdir(d)):
        subprocess = __import__("subprocess")
        subprocess.run(["cmd", "/c", "rmdir", d], capture_output=True)
    if os.path.exists(d):
        ch = diff(s, d)
        if ch:
            shutil.rmtree(d, ignore_errors=True); shutil.copytree(s, d)
            for k, rel in ch:
                print("   %s %s/%s" % (k, n, rel)); total += 1
        else:
            print("   ⏭ %-18s 无变化" % n)
    else:
        shutil.copytree(s, d)
        print("   ✅ %-18s 首次复制" % n); total += 1
print()
print("   共 %d 处变更" % total)
print("   ⚠️ 源改了必须重跑本脚本 —— 否则 WorkBuddy 用的是旧副本")
