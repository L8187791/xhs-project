# -*- coding: utf-8 -*-
r"""WB219 补登：C53 确认卡（W 侧漏登记 · 撞号自检抓出）"""
import hashlib

IDX = r"D:\小红书项目\default-workspace\_协作\卡索引.md"
b = open(IDX, "rb").read()
assert b"\r" not in b, "索引非纯 LF"
before, md5b = len(b), hashlib.md5(b).hexdigest()
s = b.decode("utf-8")
assert "XHS-20261017-C53" not in s, "C53 已登记，中止"
assert "XHS-20261017-WB219" in s, "WB219 未登记，中止（防止插错位置）"

row = ("| XHS-20261017-C53 | 确认卡 | **WB217／WB218 确认 ＋ L 四项落账 ＋ IM 通道登记**（C → W，抄送 L，20:1x）。"
       "① **WB218 四项落账 ✅ 确认**：处罚期 16:00 与 A6a 提醒时点吻合；大盘口径结案（**五项环比作废禁引**、「曝光-31%=流量下滑」撤回、CTR 两窗 **19.9%／18.5% 均低于 20.02%**）；"
       "**报白已提交**（L 已自行走完）→ **10/20–22 提交窗说法被现实超越**，千帆 P0 **随提交闭环或降级**；编号 1 未见，W 如实留空 ✓。"
       "② **WB217 两项提前落地 ✅ 确认**：Humanizer 两段式（26 项＝19 可正则＋1 统计＋6 人判，`humanizer_scan.py` EXIT 0/1）／库存第 3 篇 351 汉字·红狐 0（**红狐≠本地闸门第四次实证**）；"
       "**write-ahead 取号实战零撞号** ✓。③ **两件记录事项**：同指令双实例节奏分歧（**以「已完成」为准、无损失**，建议 L 时效指令带明确时限）／**W 侧 IM 通道被宿主封锁**（`allowNonTencentIM:false`），要 W 读群聊需 **L 在客户端开启连接**。"
       "④ 紧急提醒 C 层 20:30 待发（**20:3x 已发 → WB219 落账**） | C→W(抄送L) | 🟢 已执行 |")
if not s.endswith("\n"):
    s += "\n"
open(IDX, "wb").write((s + row + "\n").encode("utf-8"))

d = open(IDX, "rb").read()
print("%d -> %d B  md5 %s -> %s" % (before, len(d), md5b[:10], hashlib.md5(d).hexdigest()[:10]))
print("CRLF:", d.count(b"\r"), "| 行数", len(d.split(b"\n")) - 1)
print("C53 命中", d.decode("utf-8").count("XHS-20261017-C53"))
