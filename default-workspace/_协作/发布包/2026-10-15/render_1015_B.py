# -*- coding: utf-8 -*-
"""10/15 B 层配图渲染（方案 A 规格 v2：big→list→big，米白底/黑页脚/红左竖条/Noto Sans SC）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import ganhuo_lib as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "图")
ACCT = "小L整理求职资料"

note = {
    "no": "1015-2-B",
    "account": ACCT,
    "images": [
        {   # 图1 big
            "kind": "big",
            "badge": "双非友好",
            "title": "换个名字投",
            "sub": "同一批本事，换个名字投，简历上认得出来",
            "footer": "武汉和厦门那批我没全列，整理在表里了",
        },
        {   # 图2 list —— 只列 3 家（不说全），末尾留白行
            "kind": "list",
            "title": "我看到的三个",
            "items": [
                {"t": "腾讯系·腾娱互动", "d": "游戏子公司｜研发、美术、测试"},
                {"t": "字节跳动武汉分公司", "d": "内容、用户运营｜福利按大厂那套"},
                {"t": "还有厦门基地和一批武汉的", "d": "我没列全，整理在表里了"},
            ],
            "footer": "待遇没跟着名字一起降，具体以公告写的为准",
        },
        {   # 图3 big
            "kind": "big",
            "title": "投哪家大厂",
            "sub": "双非的宝子，评论区说一下，我帮你看看它下面挂着哪几家",
            "footer": "门槛低不等于随便进，笔试面试一样跑不掉",
        },
    ],
}

if __name__ == "__main__":
    ps = G.render(note, OUT, strict=True)
    print("OK", len(ps), "张 ->", OUT)
