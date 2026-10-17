# -*- coding: utf-8 -*-
"""10/14-10/16 六篇配图渲染（依 DB47 + 选题方向卡-豆包-01）"""
import sys, os
sys.path.insert(0, r"D:\Documents\deepseek-harness\default-workspace")
import ganhuo_lib as G

OUT = r"D:\Documents\deepseek-harness\default-workspace\_协作\outbox\发布包-XHS-20261014_16-WB\图"
ACCT = "小L整理求职资料"

NOTES = [
    # ============ 第1篇 A层 10/14 ============
    dict(no="1014-1-A", account=ACCT, images=[
        dict(kind="big", title=["本周四家", "网申要关", "按顺序投"], badge="10/14–10/16",
             sub="日期我都核过两遍，按顺序投更稳",
             footer="四家的具体几点关，整理在表里"),
        dict(kind="list", title=["本周要关的这几家"], hsize=80, top=250,
             items=[
                 dict(t="浙江省储备粮 · 10/14", d="省属国企，招的人不多，今天就得动"),
                 dict(t="中国石油 · 10/15", d="能源央企，网申表长，先起个头"),
                 dict(t="广发银行总行 · 10/15", d="股份制银行，缺一项就卡初审"),
             ],
             footer="还有 1 家没列出来，在表里"),
        dict(kind="big", title=["具体几点关", "各自什么线", "都在表里"], top=360,
             sub="有一家的日期我核了两遍才确定",
             footer="这几天你打算先投哪家？"),
    ]),
    # ============ 第2篇 A层 10/15 ============
    dict(no="1015-1-A", account=ACCT, images=[
        dict(kind="big", title=["中石油和广发", "都是明天关", "分两次填"], badge="同一天",
             sub="投的两边不冲突，关键是分两次填",
             footer="16 号还有一家，四大里的"),
        dict(kind="list", title=["两家都在明天关"], hsize=80, top=250,
             items=[
                 dict(t="中国石油", d="能源央企，网申表长，要填家庭成员"),
                 dict(t="广发银行总行", d="股份制银行，缺一项就卡初审"),
                 dict(t="共同点", d="都是 10/15 关，投两边不冲突"),
             ],
             footer="分两次填，比一天硬塞两份要稳"),
        dict(kind="steps", title=["我是这么排的"], hsize=80,
             steps=[
                 dict(t="今天：两份表都开出来", d="各填一半，先占住位置"),
                 dict(t="明天：补剩下的", d="不赶时间，不容易填错"),
                 dict(t="后天：16 号那家单独看", d="它的节奏和这两家不一样"),
             ],
             footer="这两天你打算先投哪家？"),
    ]),
    # ============ 第3篇 A层 10/16 ============
    dict(no="1016-1-A", account=ACCT, images=[
        dict(kind="big", title=["10/16 这家", "节奏和银行", "不一样"], badge="安永",
             sub="准备方式不能照搬银行那套",
             footer="18 号还有一批银行，下周单独说"),
        dict(kind="list", title=["两条线，别混着投"], hsize=80, top=250,
             items=[
                 dict(t="银行线", d="网申 → 笔试 → 结构化面试，节奏较缓有缓冲"),
                 dict(t="四大线", d="网申 → 线上测评，中间几乎不留空"),
                 dict(t="差别在哪", d="四大还有开放英文题，抱佛脚没用"),
             ],
             footer="按投银行的心态等两天，容易措手不及"),
        dict(kind="big", title=["18 号还有一批", "银行网申", "一起关"], top=380,
             sub="和 16 号不是一条线，节奏也不一样",
             footer="这四家你已经投了几家了？"),
    ]),
    # ============ 第4篇 B层 10/14 ============
    dict(no="1014-2-B", account=ACCT, images=[
        dict(kind="big", title=["网申被拒", "先查这几个", "不是简历问题"], badge="自查",
             sub="我自己踩过之后才发现",
             footer="还有两个坑，下篇单独说"),
        dict(kind="list", title=["网申表里常翻车的地方"], hsize=80, top=250,
             items=[
                 dict(t="① 毕业时间", d="填了档案上的日期，系统认学位证上的"),
                 dict(t="② 生源地", d="填成户籍地，初筛直接被筛还不给理由"),
                 dict(t="③ 实习那一栏", d="空着比填得不相关更吃亏"),
             ],
             footer="另外两个坑在下一篇"),
        dict(kind="big", title=["还有两个坑", "照片和专业名称", "下篇说"], top=380,
             sub="证件照的底色尺寸、专业名称怎么写",
             footer="你填网申时卡得最多的是哪一步？"),
    ]),
    # ============ 第5篇 B层 10/15 ============
    dict(no="1015-2-B", account=ACCT, images=[
        dict(kind="big", title=["银行秋招", "时间线", "一段一段看"], badge="三段",
             sub="对着看自己在哪一段",
             footer="每段都有坑，下次拆开讲"),
        dict(kind="steps", title=["三段各自该做什么"], hsize=80,
             steps=[
                 dict(t="网申（现在）", d="10–11 月，过了这窗口多数总行就停"),
                 dict(t="笔试（之后一两周）", d="通知先来，这时间用来刷行测"),
                 dict(t="面试签约（11 月–次年 1 月）", d="拖得久，人反而容易松劲"),
             ],
             footer="你现在卡在哪一段？"),
        dict(kind="big", title=["每一段都有坑", "笔试不发短信", "面试要带什么"], top=380,
             sub="这些我下次拆开讲",
             footer="你现在卡在哪一段？"),
    ]),
    # ============ 第6篇 B层 10/16 ============
    dict(no="1016-2-B", account=ACCT, images=[
        dict(kind="big", title=["十几家一起投", "反而", "一家都投不好"], badge="排序",
             sub="我一开始也这么干",
             footer="撞车取舍、备份方案下次说"),
        dict(kind="steps", title=["我按截止日往前倒排"], hsize=80,
             steps=[
                 dict(t="① 三天内要关的", d="先投，先把不错过放第一，糙一点也行"),
                 dict(t="② 一周内要关的", d="你的主力，花时间打磨开放题"),
                 dict(t="③ 还有两周以上的", d="先放放，基础信息能套着填"),
             ],
             footer="你一般一次投几家？"),
        dict(kind="big", title=["还有两个细节", "撞车怎么取舍", "要不要留备份"], top=380,
             sub="这两个我下次说",
             footer="你一般一次投几家？"),
    ]),
]

if __name__ == "__main__":
    total = 0
    for n in NOTES:
        ps = G.render(n, OUT)
        total += len(ps)
    print("TOTAL", total)
