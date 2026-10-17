# -*- coding: utf-8 -*-
"""10/16 B 层配图渲染·免笔试方向（方案 A 规格 v2：big→list→big，米白底/黑页脚/红左竖条/Noto Sans SC）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import ganhuo_lib as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "图")
ACCT = "小L整理求职资料"

note = {
    "no": "1016-2-B",
    "account": ACCT,
    "images": [
        {   # 图1 big
            "kind": "big",
            "badge": "免笔试",
            "title": "先别照抄",
            "sub": "有一批岗位不设笔试这一步，但要自己核过",
            "footer": "具体考不考，投之前还是看一眼公告",
        },
        {   # 图2 list —— 只列 2 家（不说全），第 3 行留白
            "kind": "list",
            "title": "我看到的",
            "items": [
                {"t": "传得广的免笔试清单", "d": "我核了一家，官网写着要统一线上笔试"},
                {"t": "怎么看有没有笔试", "d": "点进公告看流程那栏就清楚了"},
                {"t": "还有一批我没核完", "d": "我没列全，整理在表里了"},
            ],
            "footer": "免笔试不等于容易进，简历那关更看内容",
        },
        {   # 图3 big
            "kind": "big",
            "title": "看流程那栏",
            "sub": "双非的宝子，你卡在笔试还是简历？评论区聊聊",
            "footer": "笔试那道筛子没了，经历得自己理顺",
        },
    ],
}

if __name__ == "__main__":
    ps = G.render(note, OUT, strict=True)
    print("OK", len(ps), "张 ->", OUT)
