# -*- coding: utf-8 -*-
"""卡索引补登记 WB212（只增不删）"""
import io
P = r"D:\小红书项目\default-workspace\_协作\卡索引.md"
s = io.open(P, encoding="utf-8").read()
print("BEFORE bytes", len(s.encode("utf-8")), "LF", s.count("\n"), "CRLF", s.count("\r\n"))
print("tail5:")
for L in s.split("\n")[-5:]:
    print("  |", L[:150])

ROW = ("| XHS-20261017-WB212 | 回执卡 | **B1 09:00 场：竞品拆解 ＋ 并发双实例留痕 ＋ 驾驶舱补账**。W→C，抄送 L，09:2x。"
       "① **第 0 步竞品拆解＝刚刚（秋招版）**（红狐实跑·非降级·两轮 13 词命中 4 篇·09-20～10-10）→ "
       "`_协作\\竞品日报\\2026-10-17-拆解-刚刚秋招版.md`（**740 汉字** ≤800）；② **inbox 无未处理卡**（最新 C47 已由 WB209 承接）→ 无执行项；"
       "③ 看板尾部 ＋#47 行 ＋ §四 提案 1 条（80,951→82,841 B）；④ 驾驶舱新增「案例五」＋卡片流**补账 WB202–WB211／C44–C47**（161,043 B／"
       "md5 `1947d5df…`／CRLF 1211／纯 LF 0／源↔桌面一致）；🔴 **并发实证**：另一 W 实例（L 09:07 触发）9:12:29 刷新驾驶舱（153,785 B／"
       "`880892a0…`）→ **本场未覆盖、纯追加**，并因 **WB211 已被其占用**改取 WB212；🟡 自纠 **W-A43**（红狐包装脚本编码崩溃）／**W-A44**"
       "（根目录 2 个 `*_热门数据.html` 残留）／**W-A45**（首估 866 汉字超限，压缩至 740） | C | 🟢 已发 C |")

if not s.endswith("\n"):
    s += "\n"
s = s + ROW + "\n"
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("AFTER bytes", len(s.encode("utf-8")), "LF", s.count("\n"))
print("keep WB211:", s.count("WB211"), " WB210:", s.count("WB210"), " WB212:", s.count("WB212"))
