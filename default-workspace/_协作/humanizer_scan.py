# -*- coding: utf-8 -*-
r"""humanizer_scan.py · Humanizer 最小可跑判据（v1.0 · 2026-10-17）

用途：
    把 `_协作\humanizer_check.md`（26 项 tell 清单）里**能正则化**的条目做成可跑检查，
    让「人工逐条核」变成「清单 + 可复算输出」，不再靠记忆。

边界（重要）：
    1) 只扫「标题／正文／标签／置顶首评」四处，**不扫稿头元信息**（否则「领取」「下单」等
       出现在纪律说明里会自命中）。
    2) 本脚本只做**提示**，不替代人判：第 6/12/22/26 项仍需人工判（脚本对这些项只给统计量）。
    3) 退出码：0＝无命中（可定稿）；1＝有命中（须改后再跑或记「已核·保留」）。

用法：
    python _协作\humanizer_scan.py "路径\笔记-xxx.md"
    python _协作\humanizer_scan.py "路径\笔记-xxx.md" --json
"""
import json
import os
import re
import sys

# ---- 可正则化条目（编号对应 humanizer_check.md） ----
RULES = [
    ("01", "套话连接词", r"首先|其次|再者|最后一点|另需说明|此外还需"),
    ("02", "总结套话", r"综上所述|总而言之|总的来说|综上所叙|总之"),
    ("03", "提示套话", r"值得注意的是|需要指出的是|不难发现|显而易见|众所周知"),
    ("04", "时代空话", r"在当今|在.{0,6}的今天|随着.{0,8}的发展|在如今"),
    ("05", "递进堆砌", r"不仅.{0,30}而且"),
    ("07", "空泛副词", r"极大地|有效地|显著地|在一定程度上|某种程度上"),
    ("08", "程度副词堆叠", r"非常|十分|极其|相当|特别"),
    ("09", "符号化段首", r"^[▎｜|❶❷❸❹❺]"),  # 另按「段首符号占比 ≥60%」判，见下方特例
    ("11", "无第一人称", r"我"),  # 计数=0 才算命中
    ("13", "结尾口号", r"愿你|让我们一起|希望对你(有所)?帮助|加油鸭|冲鸭"),
    ("14", "求赞藏诱导", r"求赞|求收藏|求点赞|求关注|求互动|点赞收藏|三连|码住|先收藏"),
    ("15", "领取系诱饵", r"领取|领资料|领攻略|自取|私信|扣1|扣一|关注后发"),
    ("16", "商品引导", r"左下角|主页有|主页商品|拍下|下单|橱窗|小黄车|商品卡|链接在|购买|售价|已上架|库存"),
    ("17", "绝对化用语", r"最(?!近|后|初|终|多|少|新|好|第)|第一(?!次|步|份|版|阶段|周|时间|节|篇|种|点|条|类|方面|项|轮)|唯一|独家|永久|100%|包过|必过|保证过|全网|顶级|史上|绝对"),
    ("18", "煽动紧迫", r"赶紧|千万别|再不投|最后一天|马上截止|就是今天|错过就|抓紧|速看"),
    ("19", "焦虑贬损", r"傻等|太亏|就完了|傻子|坑死|后悔一辈子|血亏|白投"),
    ("20", "无场景锚点", r"那天|上周|前几天|昨天晚上|我翻|我打开|我记|凌晨|当时我"),  # 计数=0 才算命中
    ("24", "总结收束语", r"以上就是|以上$|以上。"),
    ("25", "命令式说教", r"切记|一定要注意|千万要|务必"),
]

# 人工判项（脚本只标注，不判定）
MANUAL = ["06 三连排比", "12 人称漂移", "21 数字过整", "22 要点等长", "23 缺「我踩过的坑」", "26 模板化要点"]


def grab(s, start, end):
    i = s.index(start) + len(start)
    j = s.index(end, i)
    return s[i:j].strip()


def load_parts(path):
    s = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    parts = {}
    parts["标题"] = grab(s, "**标题（≤20 字）**", "**正文**")
    parts["正文"] = grab(s, "**正文**", "**标签**")
    parts["标签"] = grab(s, "**标签**", "**置顶首评**")
    parts["首评"] = grab(s, "**置顶首评**", "**配图**")
    return s, parts


def main():
    if len(sys.argv) < 2:
        print("用法: python _协作\\humanizer_scan.py <稿.md> [--json]")
        return 2
    path = sys.argv[1]
    as_json = "--json" in sys.argv
    if not os.path.exists(path):
        print("文件不存在: %s" % path)
        return 2

    _, parts = load_parts(path)
    text = "\n".join(parts.values())
    body = parts["正文"]
    hits = []

    for no, name, pat in RULES:
        found = re.findall(pat, text, flags=re.M)
        if no == "11":  # 无第一人称：计数 0 才命中
            if len(found) == 0:
                hits.append({"no": no, "name": name, "count": 0, "samples": ["（全文无「我」）"]})
            continue
        if no == "20":  # 无场景锚点：计数 0 才命中
            if len(found) == 0:
                hits.append({"no": no, "name": name, "count": 0, "samples": ["（全文无时间/动作锚点）"]})
            continue
        if no == "08":  # 程度副词按密度 ≥3 才算
            if len(found) >= 3:
                hits.append({"no": no, "name": name, "count": len(found), "samples": found[:5]})
            continue
        if no == "09":  # 段首符号小标题：只有「占比 ≥60%」才算（① 编号清单本身允许）
            paras0 = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
            sym = [p for p in paras0 if re.match(r"^[▎｜|❶❷❸❹❺]", p.strip())]
            ratio = len(sym) / len(paras0) if paras0 else 0
            if ratio >= 0.60:
                hits.append({"no": no, "name": name, "count": len(sym),
                             "samples": ["段首符号占比 %.0f%%" % (ratio * 100)]})
            continue
        if found:
            hits.append({"no": no, "name": name, "count": len(found), "samples": found[:5]})

    # 统计量（供人工判 10/22/26）
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    lens = [len(re.findall(r"[\u4e00-\u9fff]", p)) for p in paras]
    mean = sum(lens) / len(lens) if lens else 0
    sd = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5 if lens else 0
    stats = {
        "正文汉字": len(re.findall(r"[\u4e00-\u9fff]", body)),
        "段数": len(paras),
        "段长均值": round(mean, 1),
        "段长标准差": round(sd, 1),
        "段长变异系数": round(sd / mean, 3) if mean else 0,
        "编号项数": len(re.findall(r"^[①②③④⑤⑥⑦⑧⑨⑩]", body, flags=re.M)),
        "我_出现次数": len(re.findall(r"我", body)),
    }

    out = {"file": os.path.basename(path), "hits": hits, "hit_count": len(hits),
           "stats": stats, "manual_items": MANUAL}

    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("=== Humanizer 可跑判据 v1.0 ===")
        print("文件：%s" % out["file"])
        print("正文汉字 %d ｜ 段数 %d ｜ 段长均值 %.1f ｜ 标准差 %.1f ｜ 变异系数 %.3f ｜ 编号项 %d ｜ 「我」%d 次"
              % (stats["正文汉字"], stats["段数"], stats["段长均值"], stats["段长标准差"],
                 stats["段长变异系数"], stats["编号项数"], stats["我_出现次数"]))
        if hits:
            print("命中 %d 项：" % len(hits))
            for h in hits:
                print("  [%s] %s ×%d 例：%s" % (h["no"], h["name"], h["count"], "／".join(h["samples"])))
        else:
            print("命中 0 项 ✅（可正则条目）")
        print("须人工判：%s" % " ｜ ".join(MANUAL))
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
