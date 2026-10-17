# -*- coding: utf-8 -*-
"""CI 总闸门 runner：串联工作区既有自检脚本，统一判定、统一退出码。

定位：CI 的 test 阶段唯一入口（GitHub Actions 里跑 `python ci/run_checks.py`）。
职责：
  1. 全量语法体检：py_compile 扫 default-workspace 根目录全部 *.py；
  2. 合规闸门：compliance_gate.py（v3.8，只查 P0），读 _extract/gate_v3_report.json 判定；
  3. 卡号撞号自检：卡号撞号自检.py（内置已知例外白名单，退出码即判定）；
  4. 驾驶舱时效自检：驾驶舱时效自检.py（对账「今天」，驾驶舱漏更新即 ❌）。

纪律：本脚本只读不写（compliance_gate 自写的报告 JSON 除外，且该文件已 gitignore）。
"""
import io
import json
import os
import py_compile
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = os.path.join(ROOT, "default-workspace")

# 子脚本（卡号撞号自检 / 驾驶舱时效自检等）会打印 ✅/❌，
# Windows GBK 控制台下会 UnicodeEncodeError，统一注入 UTF-8 环境。
CHILD_ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")

results = []  # (name, ok, detail)


def record(name, ok, detail):
    results.append((name, ok, detail))
    print("  %s %-24s %s" % ("✅" if ok else "❌", name, detail))


def run_py(name, script, *args):
    """跑一个工作区自检脚本，退出码即判定；输出尾部随报告打印。"""
    cmd = [sys.executable, script, *args]
    print("\n--- $ python %s %s" % (script, " ".join(args)))
    p = subprocess.run(cmd, cwd=WS, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=CHILD_ENV)
    out = (p.stdout or "") + (p.stderr or "")
    tail = out.strip().splitlines()[-12:]
    for line in tail:
        print("    " + line)
    record(name, p.returncode == 0,
           "exit=%d" % p.returncode if p.returncode else "通过")
    return p.returncode


def step_syntax():
    print("\n=== ① 全量语法体检（py_compile） ===")
    bad = []
    names = sorted(f for f in os.listdir(WS) if f.endswith(".py"))
    for f in names:
        try:
            py_compile.compile(os.path.join(WS, f), doraise=True)
        except py_compile.PyCompileError as e:
            bad.append("%s: %s" % (f, str(e).splitlines()[0]))
    record("语法体检(%d 个脚本)" % len(names), not bad,
           "; ".join(bad[:5]) or "全部可编译")


def step_compliance():
    print("\n=== ② 合规闸门 compliance_gate.py（只查 P0） ===")
    run_py("合规闸门执行", "compliance_gate.py")
    report = os.path.join(WS, "_extract", "gate_v3_report.json")
    if not os.path.exists(report):
        record("合规闸门判定", False, "报告缺失 _extract/gate_v3_report.json")
        return
    r = json.load(io.open(report, encoding="utf-8"))
    c = r.get("counts", {})
    record("合规闸门判定", c.get("P0", 0) == 0,
           "P0=%d P1=%d P2=%d（P0 必须清零）" % (c.get("P0", 0), c.get("P1", 0), c.get("P2", 0)))


def main():
    print("CI 总闸门 · 仓库根 %s" % ROOT)

    step_syntax()
    step_compliance()

    print("\n=== ③ 卡号撞号自检 ===")
    run_py("卡号撞号", "卡号撞号自检.py")

    print("\n=== ④ 驾驶舱时效自检 ===")
    run_py("驾驶舱时效", "驾驶舱时效自检.py")

    print("\n" + "=" * 68)
    fails = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print("  %s %-24s %s" % ("✅" if ok else "❌", name, detail))
    print("=" * 68)
    print("判定：%d 项检查，通过 %d，失败 %d" % (len(results), len(results) - len(fails), len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
