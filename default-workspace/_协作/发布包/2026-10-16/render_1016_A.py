# -*- coding: utf-8 -*-
"""10/16 A 层配图渲染（big→list→big，安永单家深挖）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import ganhuo_lib as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "图")
ACCT = "小L整理求职资料"

note = {
    "no": "1016-1-A",
    "account": ACCT,
    "images": [
        {   # 图1 big
            "kind": "big",
            "badge": "今天截止",
            "title": "安永今天关",
            "sub": "网申从七月底开到今天，别停在开放性问题那一页",
            "footer": "具体几点关，我整理在表里了",
        },
        {   # 图2 list —— 三段，末条留白
            "kind": "list",
            "title": "我卡住的地方",
            "items": [
                {"t": "基本信息", "d": "照着简历过一遍就行"},
                {"t": "后面几道大题", "d": "先在文档里写完再粘进去"},
                {"t": "分所那条线", "d": "我没一家家核，不敢写死"},
            ],
            "footer": "这次开的是审计、税务、咨询几条线",
        },
        {   # 图3 big
            "kind": "big",
            "title": "今天先投哪家",
            "sub": "今天赶截止的宝子，你打算投哪条线？评论区聊聊",
            "footer": "很多城市都有点，本科以上都能投",
        },
    ],
}

if __name__ == "__main__":
    ps = G.render(note, OUT, strict=True)
    print("OK", len(ps), "张 ->", OUT)
