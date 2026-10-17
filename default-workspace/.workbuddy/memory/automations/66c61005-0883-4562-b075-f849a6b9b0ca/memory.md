# 22:00 复盘 automation · 求职 A 店（XHS）执行记忆

## 关键运行要点（下次必读）
- 云端资料库脚本在 PowerShell 下**必须先设 `$env:PYTHONIOENCODING="utf-8"`**，否则回包含 emoji/中文会触发
  `UnicodeEncodeError`，而 `safe_print` 静默吞异常 → **表现为 exit 0 但输出全空**（曾误判为脚本不可用）。
- 脚本目录：`C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\skill-library\5.8.2-wb.41111488.gb8f6c953.haebd5991e0e2\database\`
  依赖 `workbuddy_ipc`（在同版本目录根，脚本自动加 sys.path）；解释器用
  `C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe`。
- 写回传参用 `--stdin`，并设 `$OutputEncoding`/`[Console]::OutputEncoding` 为 UTF8；校验用 python 落 ASCII JSON 再读（避免 GBK 乱码）。
- 发布排期表 `UcSbMf8BXQQjx06jvOM7To`：字段＝层级(select)/选题(text)/备注(text)/状态(select)/计划日期/挂载商品。
  10/14 C 记录 id＝`gflbvFMi1ISw4nln1QdZq8`。
- 只改 §一·补，禁整份覆盖；§九–§十四 非每日更新区。

## 执行历史
- 2026-10-14 22:0x（首次留痕）：10/14 三篇（A/B/C）**均已发**；C 层为例外放行 EX-20261014-01（未过二创+五查）。
  10/15 A/B/C 三篇均已定稿（B 层卡 P9 待遇口径待 L 拍板；C 层已升 v4）。
  北极星 1/30 与磁盘 0 成交记录冲突 → 标待 L 回传核实，未改 §一。
  已同步排期表 10/14 C 状态→已发并补备注。简报含待回传 7 项 + 待拍板 6 项。
