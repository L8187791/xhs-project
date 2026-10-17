# -*- coding: utf-8 -*-
"""10/15 A 层配图渲染（方案 A 规格 v2：big→list→big，米白底/黑页脚/红左竖条/Noto Sans SC）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import ganhuo_lib as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "图")
ACCT = "小L整理求职资料"

note = {
    "no": "1015-1-A",
    "account": ACCT,
    "images": [
        {   # 图1 big
            "kind": "big",
            "badge": "今天",
            "title": "今天关的两家",
            "sub": "一家央企，一家股份制银行，都是今天到期",
            "footer": "具体几点关、走哪条线更稳，我整理在表里了",
        },
        {   # 图2 list —— 只列 2 家（不说全），末尾留白行
            "kind": "list",
            "title": "今天到期的两家",
            "items": [
                {"t": "中石油", "d": "央企｜9月初开到今天｜石油工程、机械、化工、地质"},
                {"t": "广发银行（总行）", "d": "股份制｜分支机构是另一条线，到下个月中"},
                {"t": "还有一批在后面几天", "d": "具体是哪些、各自几点关，表里都有"},
            ],
            "footer": "完整表在主页，按截止日排好了",
        },
        {   # 图3 big
            "kind": "big",
            "title": "今天打算先投哪家",
            "sub": "两边都想试的话，先把表头填掉，再回头补细节",
            "footer": "评论区说说你今天投了哪家",
        },
    ],
}

if __name__ == "__main__":
    ps = G.render(note, OUT, strict=True)
    print("OK", len(ps), "张 ->", OUT)
