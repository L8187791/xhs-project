# -*- coding: utf-8 -*-
"""10/16 C 层配图渲染·冷门央国企晚截止方向（方案 A 规格 v2：big→list→big，米白底/黑页脚/红左竖条/Noto Sans SC）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import ganhuo_lib as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "图")
ACCT = "小L整理求职资料"

note = {
    "no": "1016-3-C",
    "account": ACCT,
    "images": [
        {   # 图1 big
            "kind": "big",
            "badge": "还没关",
            "title": "开到十月底",
            "sub": "以为秋招收尾了，这批网申还开着",
            "footer": "有一家公告里写的是开到十一月底",
        },
        {   # 图2 list —— 只列 3 家（不说全），第 4 行留白
            "kind": "list",
            "title": "我拉到的",
            "items": [
                {"t": "中国邮政", "d": "简历收到十月三十一号"},
                {"t": "国机集团", "d": "十月三十一号，两个来源对得上"},
                {"t": "中国长城科技集团", "d": "公告原文写的是网申开到十一月底"},
                {"t": "还有一批开得更晚的", "d": "我没列全，整理在表里了"},
            ],
            "footer": "各省各分公司收口的日子不一定同步",
        },
        {   # 图3 big
            "kind": "big",
            "title": "别等想起来",
            "sub": "十月还在投的宝子，你漏掉过月底才关的企业吗？评论区聊聊",
            "footer": "日期越近越扎眼，开得晚的最容易被漏",
        },
    ],
}

if __name__ == "__main__":
    ps = G.render(note, OUT, strict=True)
    print("OK", len(ps), "张 ->", OUT)
    for p in ps:
        print("  ", os.path.basename(p))
