# -*- coding: utf-8 -*-
"""往届生 3 篇配图渲染（依 DB51 新方向 · 不列企业名）"""
import sys, os
sys.path.insert(0, r"D:\Documents\deepseek-harness\default-workspace")
import ganhuo_lib as G

OUT = r"D:\Documents\deepseek-harness\default-workspace\_协作\outbox\发布包-XHS-20261014_16-WB\图-往届生"
ACCT = "小L整理求职资料"

NOTES = [
    # ============ 往届生第1篇 10/14 18:00 ============
    dict(no="1014-3-WJ", account=ACCT, images=[
        dict(kind="big", title=["往届生投秋招", "先看这 3 件", "不是看毕业几年"], badge="10/14",
             sub="这三件没捋清，投出去也大概率无效",
             footer="各家窗口开多久，整理在表里"),
        dict(kind="list", title=["先捋清这两件"], hsize=80, top=250,
             items=[
                 dict(t="择业期", d="毕业后多数按两年算，这期间未就业仍算应届"),
                 dict(t="档案在哪", d="留校还是回原籍，两种填法不一样"),
             ],
             footer="第 3 件：报到证怎么处理，写在表里"),
        dict(kind="big", title=["同样是银行", "为什么有人能投", "有人不能"], top=360,
             sub="差别来自各家对「应届」的认定口径",
             footer="你毕业几年了，还在投秋招吗？"),
    ]),
    # ============ 往届生第2篇 10/15 18:00 ============
    dict(no="1015-3-WJ", account=ACCT, images=[
        dict(kind="big", title=["往届生填网申", "这 2 栏", "和应届不一样"], badge="10/15",
             sub="填错不一定当场报错，但可能过不了初筛",
             footer="第 3 栏和专业名称有关，下篇说"),
        dict(kind="list", title=["这两栏要对着填"], hsize=80, top=250,
             items=[
                 dict(t="毕业时间", d="按毕业证填，不是学位证，两个日期常差几个月"),
                 dict(t="生源地", d="不是户籍地，按入学前户籍所在地算"),
             ],
             footer="迁过户口的尤其容易搞混"),
        dict(kind="big", title=["还有一个坑", "和专业名称", "有关"], top=360,
             sub="填的时候看不出来，审核时才冒出来",
             footer="这两个坑你踩过哪个？"),
    ]),
    # ============ 往届生第3篇 10/16 18:00 ============
    dict(no="1016-3-WJ", account=ACCT, images=[
        dict(kind="big", title=["同样是银行", "往届生门槛", "差在层级"], badge="10/16",
             sub="不是资格不够，是不知道该看哪份公告",
             footer="具体哪些、窗口开多久，都在表里"),
        dict(kind="list", title=["三层，松紧不同"], hsize=80, top=250,
             items=[
                 dict(t="国有大行", d="总行统一发公告，全国一套标准"),
                 dict(t="股份制银行", d="总行和分行各发各的，各省可能不一样"),
             ],
             footer="第 3 层：城商行，渠道分散，容易被漏"),
        dict(kind="big", title=["一个信息问题", "不是资格问题", "是看哪份公告"], top=360,
             sub="往届生投银行，难点在信息不在条件",
             footer="你是哪一年毕业的，投过银行吗？"),
    ]),
]

if __name__ == "__main__":
    total = 0
    for n in NOTES:
        ps = G.render(n, OUT)
        total += len(ps)
    print("TOTAL", total)
