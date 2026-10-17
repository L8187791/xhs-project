# -*- coding: utf-8 -*-
"""
49.9 三份清单 · 备注列清洗（用户 2026-10-13 授权）
原则：删除内部工序表述，保留对买家有用的信息
删除项：入口回写(第N批...) / 豆包核到 / 单源(WorkBuddy 一处) / K3 采纳 / 待复核 /
        与现值吻合 → 升级为「官网原文」 / 复核记录 / 探针批号 / 内部代号
保留项：官网原文引文 / 区间表述取结束日 / 多分行·多省份差异 / 邮箱而非网申 / 特殊要求
"""
import json, re, os

SRC = r"D:\Documents\deepseek-harness\default-workspace\技能包_时间表查询官\data\timetable.json"

# ---- 删除规则（按优先级）----
DROP_PATTERNS = [
    r"\s*｜?\s*入口回写\(第\d+批(?:修正)?,\s*[\d\-]+\)",   # 入口回写(第6批, 2026-10-11)
    r"\s*｜?\s*入口回写\([^)]*\)",
    r"\(豆包核到官方公告原文\)", r"豆包核到官方公告原文",
    r"豆包未抽到",
    r"⚠️?\s*单源（WorkBuddy 一处）", r"单源\(WorkBuddy 一处\)",
    r"（K3 采纳）", r"\(K3 采纳\) K3",
    r"→\s*升级为「官网原文」",
    r"→\s*待复核", r"待复核",
    r"⚠️\s*已修正：", r"已修正：", r"原解析取到开始日，",
    r"🆕\s*[\d\-]+\s*WorkBuddy\s*核到公告原文",
    r"（?第三方口径，待核）?", r"（第三方口径，待核）",
    r"\|?\s*复核\s*\|?",
    r"（3 源*", 
]

def clean(note: str) -> str:
    if not note:
        return ""
    s = note
    # 1) 删「入口回写」段
    s = re.sub(r"\s*｜\s*入口回写\([^)]*\)", "", s)
    s = re.sub(r"\s*入口回写\([^)]*\)", "", s)
    s = re.sub(r"\s*｜\s*入口回写[^｜]*$", "", s)
    # 2) 删来源标注（对外交付件不必写「来源为中公汇总表」，可信度列已有）
    s = re.sub(r"^来源为中公汇总表[；;]?\s*", "", s)
    s = re.sub(r"^来源为[^；;｜]*汇总表[；;]?\s*", "", s)
    # 3) 删豆包/WorkBuddy 等内部主体
    s = s.replace("（豆包核到官方公告原文）", "").replace("豆包核到官方公告原文", "")
    s = s.replace("，豆包未抽到，建议再核", "").replace("豆包未抽到", "")
    s = re.sub(r"注：?豆包复核核不到官网佐证（[^）]*）[，,]?\s*", "注：未核到官网佐证，", s)
    s = re.sub(r"豆包复核核不到官网佐证（[^）]*）[，,]?\s*", "未核到官网佐证，", s)
    s = re.sub(r"豆包[^，。｜]*[，。]", "", s)
    s = re.sub(r"^注：\s*来源仅中公汇总", "来源仅汇总表", s)
    s = re.sub(r"⚠️?🆕?\s*\d{2}-\d{2}\s*WorkBuddy\s*核到公告原文「[^」]*」[^｜]*", "", s)
    s = re.sub(r"🆕\s*[\d\-]+\s*WorkBuddy\s*核到公告原文「[^」]*」[^｜]*", "", s)
    # 4) 单源表述（去内部主体，保留「仅单一来源」这个买家关心的信息）
    s = s.replace("⚠️ 单源（WorkBuddy 一处），豆包未抽到，建议再核", "仅单一来源，建议以官网为准")
    s = s.replace("单源（WorkBuddy 一处）", "仅单一来源").replace("单源(WorkBuddy 一处)", "仅单一来源")
    s = s.replace("⚠️ 单源（超级简历）+ 未核到官方入口 → 双重弱", "仅单一来源、未核到官方入口")
    s = s.replace("⚠️ 单源（超级简历）→ 待复核", "仅单一来源，待核")
    s = s.replace("（超级简历）", "").replace("（中公汇总表）", "").replace("（汇总表）", "")
    # 5) 删内部代号 / 流程标记
    s = s.replace("（K3 采纳）", "").replace("K3 采纳", "")
    s = s.replace("→ 升级为「官网原文」", "").replace("升级为「官网原文」", "")
    s = s.replace("→ 待复核", "").replace("，待复核", "").replace("｜待复核", "")
    s = s.replace("⚠️ 单源（粉笔）", "仅单一来源").replace("单源（粉笔）", "仅单一来源")
    s = re.sub(r"⚠️?\s*单源（[^）]*）", "仅单一来源", s)
    s = re.sub(r"^单源（[^）]*）", "仅单一来源", s)
    s = re.sub(r"（第三方口径，待核）", "（第三方口径，建议以官网为准）", s)
    s = re.sub(r"⚠️?\s*已修正：原解析取到开始日，按区间结束日更正为\s*", "", s)
    s = re.sub(r"已修正：", "", s)
    s = re.sub(r"原解析取到开始日[，,]?", "", s)
    s = re.sub(r"按区间结束日更正为\s*", "取结束日：", s)
    # 6) emoji 统一化（⚠️ 在 PDF 字体中显示为方框 → 换成文字）
    s = s.replace("⚠️", "注：").replace("🆕", "").replace("✅", "")
    s = re.sub(r"注：\s+", "注：", s)
    # 收尾
    s = re.sub(r"（\s*）", "", s)
    s = re.sub(r"\s*｜\s*(?=｜|$)", "", s)
    s = s.strip(" ｜，,;；")
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"^注：\s*", "注：", s)
    s = re.sub(r"注：\s*$", "", s)
    return s.strip()

if __name__ == "__main__":
    d = json.load(open(SRC, encoding="utf-8"))
    comps = d["companies"]
    n = 0
    samples = []
    for x in comps:
        old = (x.get("note") or "").strip()
        new = clean(old)
        if new != old:
            n += 1
            if len(samples) < 12:
                samples.append((x["company"], old, new))
    print(f"需清洗条目（全 131 条中）：{n}")
    print()
    for name, old, new in samples:
        print(f"【{name}】")
        print("  旧:", old[:130])
        print("  新:", new[:130])
        print()
