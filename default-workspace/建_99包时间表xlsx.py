# -*- coding: utf-8 -*-
r"""99 包 ① 时间表 xlsx 重出 v1.0.9（任务卡 41 · 任务 B）

数据来源：`技能包_时间表查询官\data\timetable.json`（v1.0.9，已含两轴字段）

卡面硬要求（逐条对应下面的 assert）：
  - 主表 131 家 / 补充池 11 家
  - 已截止 18 家必须标「已截止 N 天」（灰档）
  - 两轴列不可为空（131/131）
  - 过 compliance_gate.py P0=0（由 gate 单独跑，不在本脚本内）

列序按卡面：序号｜企业名｜截止日期｜状态｜来源可信度(A/B/C/⚪)｜等级中文｜日期形态｜投递入口
其余（招聘方向/工作地点/学历/核实状态/核验日期/备注）沿用旧表。

用法：python 建_99包时间表xlsx.py
"""
import datetime
import json
import os
import re
import shutil
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = r"D:\Documents\deepseek-harness\default-workspace"
DATA = os.path.join(WS, "技能包_时间表查询官", "data", "timetable.json")
ARCHIVE_DIR = os.path.join(WS, "_扩充", "旧版归档")
PKG = os.path.join(WS, "交付_99元全流程资料包")
XLSX = os.path.join(PKG, "① 2027届秋招网申截止时间表.xlsx")
VER = "v1.0.10"   # 卡 44：加回「剩余天数」数值列 + 更新日志措辞改客观

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FILL_TITLE = PatternFill("solid", fgColor="FFF2E8")
FILL_HDR = PatternFill("solid", fgColor="E8EEF7")
FILL_RED = PatternFill("solid", fgColor="FCE4E4")
FILL_ORANGE = PatternFill("solid", fgColor="FDEFD8")
FILL_GRAY = PatternFill("solid", fgColor="EDEDED")
FONT_GRAY = Font(color="9C9C9C")
FONT_RED = Font(color="C0392B", bold=True)
FONT_ORANGE = Font(color="B9770E")

# 列序 = 卡面要求 + 主运营裁定 J1 加回的「剩余天数」数值列 + 旧表既有字段
HEADERS = ["序号", "企业名称", "截止日期", "状态", "剩余天数",
           "来源可信度", "等级中文", "日期形态", "投递入口",
           "招聘方向", "工作地点", "学历", "核实状态", "核验日期", "备注"]
WIDTHS = [6, 24, 13, 15, 10, 12, 20, 15, 30, 22, 18, 12, 14, 12, 46]
BASE_DATE = datetime.date(2026, 10, 10)   # 数据核验日期，剩余天数以它为准


def state_of(c):
    """状态列：已截止 N 天 / 剩 N 天（紧急）/ 剩 N 天 / 招满即止 / 有日期待核实 / 未列明日期

    判据只认 JSON 里的 days_left 与 date_form，不猜、不折算。
    """
    left = c.get("days_left")
    if isinstance(left, int) and not isinstance(left, bool):
        if left < 0:
            return "已截止 %d 天" % (-left)
        if left <= 7:
            return "剩 %d 天（紧急）" % left
        return "剩 %d 天" % left
    df = c.get("date_form")
    if df == "rolling":
        return "招满即止"
    if df == "to_verify":
        return "有日期待核实"
    if df == "none":
        return "未列明日期"
    return ""


def style_status(cell, left):
    if isinstance(left, int) and not isinstance(left, bool):
        if left < 0:
            cell.fill, cell.font = FILL_GRAY, FONT_GRAY
        elif left <= 7:
            cell.fill, cell.font = FILL_RED, FONT_RED
        elif left <= 15:
            cell.fill, cell.font = FILL_ORANGE, FONT_ORANGE


def main():
    # ── 0. 旧表先归档（不做不可逆操作）──
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    old_backup = os.path.join(ARCHIVE_DIR, "99包_时间表_v1.0.9_20261010.xlsx")
    if not os.path.exists(old_backup):
        shutil.copy2(XLSX, old_backup)
    print("① 上一版(v1.0.9)已归档 → %s" % old_backup)

    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    rows = data["companies"]
    assert len(rows) == 131, "❌ 主表应为 131 家，实得 %d" % len(rows)
    assert data["meta"]["version"] == "v1.0.9", "❌ 数据版本不是 v1.0.9"

    # ── 1. 两轴列不可为空（131/131）──
    for c in rows:
        assert c.get("source_level"), "❌ source_level 为空：%s" % c["company"]
        assert c.get("source_level_cn"), "❌ 等级中文为空：%s" % c["company"]
        assert c.get("date_form"), "❌ date_form 为空：%s" % c["company"]

    old = load_workbook(XLSX)          # 读旧表的补充池 / 更新日志
    wb = Workbook()
    ws = wb.active
    ws.title = "秋招总表"

    # ── 2. 表头区 ──
    ws.cell(row=1, column=1,
            value="2027 届秋招网申截止时间  %s ｜ 主表 131 家 + 补充池 11 家" % VER)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(HEADERS))
    ws.cell(row=1, column=1).fill = FILL_TITLE
    ws.cell(row=1, column=1).font = Font(bold=True, size=12)
    ws.row_dimensions[1].height = 24

    ws.cell(row=2, column=1,
            value="红=7 天内截止 · 橙=8–15 天 · 灰=已截止 ｜ 「来源可信度」与「日期形态」是两条独立的轴，"
                  "说明见「使用说明」表 ｜ 截止日期以企业官网为准")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(HEADERS))
    ws.cell(row=2, column=1).font = Font(color="7F7F7F", italic=True)

    for i, h in enumerate(HEADERS, start=1):
        cell = ws.cell(row=4, column=i, value=h)
        cell.fill = FILL_HDR
        cell.font = Font(bold=True)
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[4].height = 22

    # ── 3. 主表 131 行 ──
    expired = 0
    for j, c in enumerate(rows):
        r = 5 + j
        left = c.get("days_left")
        vals = [c.get("no", ""), c.get("company", ""), c.get("deadline", ""),
                state_of(c),
                left if isinstance(left, int) and not isinstance(left, bool) else "",
                c.get("source_level", ""), c.get("source_level_cn", ""),
                c.get("date_form_cn") or c.get("date_form", ""),
                c.get("apply_url", ""),
                c.get("direction", ""), c.get("location", ""), c.get("degree", ""),
                c.get("verify_status", ""), c.get("verified_at", ""), c.get("note", "")]
        assert all(str(v) != "" for v in (vals[5], vals[6], vals[7])), \
            "❌ 两轴列出现空值：%s" % c["company"]
        for i, v in enumerate(vals, start=1):
            cell = ws.cell(row=r, column=i, value=v)
            cell.border = BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center",
                                       wrap_text=(i == len(HEADERS)))
        style_status(ws.cell(row=r, column=4), left)
        if isinstance(left, int) and not isinstance(left, bool) and left < 0:
            expired += 1
            assert state_of(c).startswith("已截止"), "❌ 已截止项未标「已截止 N 天」：%s" % c["company"]

    assert expired == 18, "❌ 已截止应为 18 家，实得 %d" % expired
    assert ws.max_row == 135, "❌ 主表行数应为 135（表头 4 + 数据 131），实得 %d" % ws.max_row

    # ── 3b. 「剩余天数」数值列自校验（卡 44 验收：数值 = deadline − 2026-10-10）──
    i_days = HEADERS.index("剩余天数") + 1
    n_num = n_neg = 0
    for j, c in enumerate(rows):
        cell = ws.cell(row=5 + j, column=i_days)
        dl = c.get("deadline") or ""
        if re.match(r"^\d{4}-\d{2}-\d{2}$", dl):
            exp = (datetime.date.fromisoformat(dl) - BASE_DATE).days
            assert isinstance(cell.value, int) and not isinstance(cell.value, bool), \
                "❌ 剩余天数不是数值：%s → %r" % (c["company"], cell.value)
            assert cell.value == exp, \
                "❌ 剩余天数算错：%s 表内 %r，应为 %d（%s − 2026-10-10）" % (
                    c["company"], cell.value, exp, dl)
            n_num += 1
            if cell.value < 0:
                n_neg += 1
        else:
            assert cell.value in ("", None), \
                "❌ 无日期行不应填剩余天数：%s → %r" % (c["company"], cell.value)
    assert n_num == 107, "❌ 应有 107 个数值，实得 %d" % n_num
    assert n_neg == 18, "❌ 负数（已截止）应为 18，实得 %d" % n_neg
    print("   剩余天数列：%d 个数值、负数 %d 个，逐行与 deadline−2026-10-10 复核一致"
          % (n_num, n_neg))

    for i, w in enumerate(WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A5"

    # ── 4. 补充池（原样搬旧表 11 家）──
    os_ = old["补充池"]
    ws2 = wb.create_sheet("补充池")
    for r in range(1, os_.max_row + 1):
        for col in range(1, os_.max_column + 1):
            v = os_.cell(row=r, column=col).value
            if v is not None:
                ws2.cell(row=r, column=col, value=v)
    pool_n = sum(1 for r in range(5, os_.max_row + 1) if os_.cell(row=r, column=2).value)
    assert pool_n == 11, "❌ 补充池应为 11 家，实得 %d" % pool_n
    for k, w in zip("ABCD", [5, 30, 42, 70]):
        ws2.column_dimensions[k].width = w

    # ── 5. 使用说明 ──
    ws3 = wb.create_sheet("使用说明")
    lines = [
        ("这份表怎么用", True),
        ("", False),
        ("1. 颜色：红=7 天内截止，橙=8–15 天，灰=已截止（「剩余天数」按核验日期 2026-10-10 算，"
         "不会自己变；要每天自动算请用「⑦ 网申进度台账模板」）", False),
        ("", False),
        ("2. 两条独立的轴，请分开看：", True),
        ("   【来源可信度】这条信息是谁写的 —— A 企业自己写的 ／ B 二手或我们核过 ／ "
         "C 第三方未核 ／ ⚪ 滚动·无固定截止（不参与可信度分级）", False),
        ("   【日期形态】这家到底有没有写死截止日 —— 硬日期 ／ 滚动·无固定截止 ／ "
         "有日期待核实（去官网能查到）／ 未列明日期（公告本身没写，官网也查不到）", False),
        ("", False),
        ("3. 为什么分两列？因为「信息可不可信」和「有没有固定截止日」是两回事。", False),
        ("   例：通用技术集团来源是官网原文（A），但日期形态是滚动·无固定截止。两列各看各的。", False),
        ("", False),
        ("4. 「状态」列写「已截止 N 天」的就是已经过了的，不必再投。", False),
        ("", False),
        ("5. 另有 11 家只有官方入口、无集团级截止日，见「补充池」表，不与主表混。", False),
        ("", False),
        ("6. 层级说明：「中国核工业集团·中核华辰」= 集团二级单位，有独立截止日。", False),
        ("", False),
        ("7. 想按紧急程度排？对「剩余天数」列做升序排序即可 —— 它是数值列，负数就是已截止的。", False),
        ("", False),
        ("8. 每周五发布新版，已购用户免费获取；承诺期限至 2027 年 7 月。", False),
        ("", False),
        ("本表为信息整理，不评价企业、不推荐投递；截止日期以官网为准。", False),
    ]
    for i, (t, b) in enumerate(lines, start=1):
        ws3.cell(row=i, column=1, value=t).font = Font(bold=True) if b else Font()
    ws3.column_dimensions["A"].width = 110

    # ── 6. 更新日志（旧记录保留 + 追加三条）──
    ws4 = wb.create_sheet("更新日志")
    ws4.cell(row=1, column=1, value="时间表更新日志")
    ws4.cell(row=2, column=1,
             value="⚠️ 这是活表 —— 每周五更新新版，已购用户免费获取（承诺至 2027 年 7 月）")
    for i, h in enumerate(["版本", "日期", "内容"], start=1):
        cell = ws4.cell(row=4, column=i, value=h)
        cell.fill = FILL_HDR
        cell.font = Font(bold=True)
        cell.border = BORDER
    new_log = [
        ("v1.0.7", "10-10", "主表扩充至 131 家"),
        ("v1.0.8", "10-10", "新增 source_level（来源可信度）与 date_form（日期形态）两列"),
        ("v1.0.9", "10-10", "新增「来源可信度 / 等级中文 / 日期形态」三列；新增「状态」列"
                            "（已截止 N 天 / 剩 N 天）"),
        ("v1.0.10", "10-10", "在「状态」后加回「剩余天数」数值列（可排序；已截止为负数）"),
    ]
    old_log = old["更新日志"]
    # ★ 去重：本轮要写的版本若旧表里已有（上一轮刚写过），以本轮措辞为准，跳过旧行
    new_vers = {row[0].lower() for row in new_log}
    r = 5
    for rr in range(5, old_log.max_row + 1):
        v1 = old_log.cell(row=rr, column=1).value
        if not v1 or str(v1).strip() == "下次":
            continue
        if str(v1).strip().lower() in new_vers:
            continue
        for i, v in enumerate([v1, old_log.cell(row=rr, column=2).value,
                               old_log.cell(row=rr, column=3).value], start=1):
            cell = ws4.cell(row=r, column=i, value=v)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=(i == 3))
        r += 1
    for row in new_log:
        for i, v in enumerate(row, start=1):
            cell = ws4.cell(row=r, column=i, value=v)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=(i == 3))
        r += 1
    for i, v in enumerate(["下次", "10-16", "每周五更新（周五发布）"], start=1):
        ws4.cell(row=r, column=i, value=v).border = BORDER
    vers = [str(ws4.cell(row=rr, column=1).value).strip().lower()
            for rr in range(5, r) if ws4.cell(row=rr, column=1).value]
    assert len(vers) == len(set(vers)), "❌ 更新日志版本号重复：%s" % vers
    for k, w in zip("ABC", [10, 12, 80]):
        ws4.column_dimensions[k].width = w

    # 表顺序与旧表一致：更新日志 / 秋招总表 / 补充池 / 使用说明
    wb.move_sheet("更新日志", offset=-3)
    assert wb.sheetnames == ["更新日志", "秋招总表", "补充池", "使用说明"], wb.sheetnames

    wb.save(XLSX)
    print("② 已写出：%s" % XLSX)
    print("   工作表：%s" % " / ".join(wb.sheetnames))
    print("   主表 131 家（其中已截止 %d 家，均标「已截止 N 天」）" % expired)
    print("   补充池 %d 家 ｜ 两轴列 131/131 非空" % pool_n)
    print("   列数 %d：%s" % (len(HEADERS), " / ".join(HEADERS)))
    print("   版本：%s" % VER)


if __name__ == "__main__":
    main()
