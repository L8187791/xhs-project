# -*- coding: utf-8 -*-
"""看板回写（只增不删）：① 在办尾部追加 #47 行 ② §四 提案区追加 1 条。单次读改写＋校验。"""
import io, hashlib

P = r"D:\小红书项目\default-workspace\_协作\推进看板-2026-10.md"
s = io.open(P, encoding="utf-8").read()
b0 = len(s.encode("utf-8"))
print("BEFORE bytes", b0, "LF", s.count("\n"), "CRLF", s.count("\r\n"))

A_TAIL = "| 46 | 🖥 **驾驶舱「今日三层发布」全页刷新**"
A_PROP = "\n\n**指标**（用于判断「越转越好」）："
print("anchor_tail", s.count(A_TAIL), "anchor_prop", s.count(A_PROP))
assert s.count(A_TAIL) == 1 and s.count(A_PROP) == 1

ROW47 = ("| 47 | 🧭 **W B1 09:00 场（2026-10-17）· 第 0 步竞品拆解 ＋ 读卡** | W | 🟢 已完成 | "
         "① **竞品拆解＝刚刚（秋招版）**（红狐实跑·非降级·两轮 13 词命中 4 篇·09-20～10-10）→ "
         "`_协作\\竞品日报\\2026-10-17-拆解-刚刚秋招版.md`（**740 汉字** ≤800）"
         "② **读卡：inbox 无未处理卡**（最新 C47 已由 WB209 承接）"
         "③ 回写看板＋驾驶舱（新增「案例五」＋卡片流补账 WB202–WB211／C44–C47）＋桌面同步 "
         "| 🔴 **并发发现**：驾驶舱 9:12:29 被另一 W 实例（L 触发）全页刷新（153,785 B／md5 `880892a0…`）；"
         "本场在**未触碰区纯追加**（无覆盖），改后 **161,043 B／md5 `1947d5df…`／CRLF 1211／纯 LF 0**、源↔桌面同 md5；"
         "🔴 **WB211 已被该实例占用 → 本场回执改取 WB212** |")

PROP = ("| 2026-10-17 | W（WB212 发现） | 🔴 **同一时段两个 W 实例并发写同一批共享文件 → 撞号＋同路径双写风险**："
        "现象＝本场 B1（09:00 自动触发）运行期间，另一 W 实例（L 09:07 触发）于 **9:12:29** 全页刷新 "
        "`_协作\\_驾驶舱复刻\\L 的工作台.html`、**9:13:33** 写本看板与 `卡索引.md`、**9:13:50** 出回执 **WB211**；"
        "本场若非先 `Test-Path`＋读现场再追加，就会以旧快照**覆盖**对方刷新成果，且 **211 号会被两方各占一次**。"
        "成本＝共享单文件（驾驶舱／看板／卡索引）在**多实例并发**下无互斥，撞号与覆盖只会越来越频繁。"
        "改法（**建议**）：① W 侧同号段取号改为**落盘前 `Test-Path` 双源复核**（本轮已按此把回执改取 WB212）"
        "② 驾驶舱／看板的**写入按场次串行**，或写前先比 md5、变了即改「追加差异」而非整文件重写 ③ 长任务开工前写**占用标记**。"
        "预期收益＝消除「同路径双写」这类静默丢失 | 🟡 待 C 评估 |")

s2 = s.replace(A_TAIL, A_TAIL, 1)  # no-op keep
# 追加 #47：插到最后一个表格行（A_TAIL 所在行）之后
lines = s.split("\n")
out = []
inserted47 = False
for L in lines:
    out.append(L)
    if (not inserted47) and L.startswith(A_TAIL):
        out.append(ROW47)
        inserted47 = True
assert inserted47
s2 = "\n".join(out)

# §四 提案追加
s2 = s2.replace(A_PROP, "\n" + PROP + A_PROP, 1)

io.open(P, "w", encoding="utf-8", newline="").write(s2)
b1 = len(s2.encode("utf-8"))
print("AFTER  bytes", b1, "LF", s2.count("\n"), "CRLF", s2.count("\r\n"))
# 校验对方内容未丢
for k in ["| 46 | 🖥", "| 45 | ⚠️", "| 42 | 📊", "| 47 | 🧭", "WB212 发现", "2026-10-17-拆解-刚刚秋招版.md"]:
    print("keep", k, s2.count(k))
