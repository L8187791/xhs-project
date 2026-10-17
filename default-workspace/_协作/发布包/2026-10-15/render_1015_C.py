# -*- coding: utf-8 -*-
"""10/15 C 层配图渲染（方案 A 规格 v2：big→list→big，米白底/黑页脚/红左竖条/Noto Sans SC）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import ganhuo_lib as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "图")
ACCT = "小L整理求职资料"

note = {
    "no": "1015-3-C",
    "account": ACCT,
    "images": [
        {   # 图1 big
            "kind": "big",
            "badge": "往届友好",
            "title": "我投了一遍",
            "sub": "我把招往届生的那批投了一遍，说下情况",
            "footer": "各家截止时间不一样，我按企业整理在表里了",
        },
        {   # 图2 list —— 只列 2 家（不说全），第 3 行留白
            "kind": "list",
            "title": "我看到的",
            "items": [
                {"t": "四川银行", "d": "城商行｜10月31日截止｜部分岗放宽到24届"},
                {"t": "光大银行", "d": "报名开到11月8日，表里查得到出处"},
                {"t": "还有一批我在核", "d": "核到能确认的再发，不敢乱写"},
            ],
            "footer": "各家时间不一样，月底前和下月初的都有",
        },
        {   # 图3 big
            "kind": "big",
   "title": "投到第几家",
   "sub": "往届的宝子，评论区说下，我看看你还能投哪些",
            "footer": "投之前自己对一下官网，以企业公告为准",
        },
    ],
}

if __name__ == "__main__":
    ps = G.render(note, OUT, strict=True)
    print("OK", len(ps), "张 ->", OUT)
