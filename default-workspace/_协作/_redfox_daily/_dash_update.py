# -*- coding: utf-8 -*-
"""驾驶舱更新（只增不删）：
① 追加「案例五 · 2026-10-17 · 刚刚（秋招版）」
② 卡片流补账（WB202–WB211 / C44–C47）
保持 CRLF；改前改后打印字节数/CRLF/纯LF/md5"""
import hashlib

P = r"D:\小红书项目\default-workspace\_协作\_驾驶舱复刻\L 的工作台.html"
b0 = open(P, "rb").read()
s = b0.decode("utf-8")
print("BEFORE bytes=%d CRLF=%d pureLF=%d md5=%s" % (
    len(b0), b0.count(b"\r\n"), b0.count(b"\n") - b0.count(b"\r\n"), hashlib.md5(b0).hexdigest()))

A1 = '    </div>\r\n\r\n    <div class="panel">\r\n      <h2><span class="dot"></span>日常机制与审核线'
A2 = 'const CARDS=[\r\n'
print("anchor1 =", s.count(A1), " anchor2 =", s.count(A2))
assert s.count(A1) == 1 and s.count(A2) == 1, "anchor not unique"

CASE5 = '''    <div class="panel">
      <h2><span class="dot g"></span>案例五 · 2026-10-17 · 刚刚（秋招版）<span class="sub">2026-10-17 · 红狐实跑（非降级）· 待 C 审核</span></h2>
      <div class="grid g4">
        <div class="kpi" style="padding:11px 13px"><div class="lb">选中理由</div><div class="vl" style="font-size:16px">命中最多</div><div class="ft">优先级 #1 今日无可用对象 → 落 #2 高互动账号</div></div>
        <div class="kpi" style="padding:11px 13px"><div class="lb">近 30 天样本</div><div class="vl" style="font-size:18px">4<small> 篇</small></div><div class="ft">09-20～10-10 · 两轮 13 词命中 · 赞/藏/评原始值</div></div>
        <div class="kpi" style="padding:11px 13px"><div class="lb">单篇峰值</div><div class="vl" style="font-size:18px">1209<small> 赞</small></div><div class="ft">09-24「国庆节前即将截止的秋招汇总」藏 1142 / 评 313</div></div>
        <div class="kpi" style="padding:11px 13px"><div class="lb">篇幅</div><div class="vl" style="font-size:18px">740<small> 汉字</small></div><div class="ft">≤800 上限 · 未取到处一律标「未取到」</div></div>
      </div>
      <div class="note" style="margin-top:0">产出：<span class="mono">_协作\\竞品日报\\2026-10-17-拆解-刚刚秋招版.md</span>。去重声明：与 10-16 拆的牛马学姐<b>不同账号</b>；本号近 30 天活跃（09-20～10-10）。🔴 B / C 维<b>未取到</b>（红狐仅笔记层，无商品页）。</div>
      <div class="grid g2">
        <div class="panel">
          <h2><span class="dot g"></span>✅ 可复用点（3 条，均带落点）</h2>
          <ul class="tight">
            <li><b>【动作】</b>岗位表固定三列＝<b>企业类型／base地／有无笔试</b>。<br><b>【落点】</b>我方时间表字段模板 ＋ A 层笔记表格三列描述。<br><b>【依据】</b>09-20／10-06 正文均写「细分了企业类型、base地、有无笔试」，与我方主表字段重合。</li>
            <li><b>【动作】</b>标题走「<b>日期＋今天刚开的秋招</b>」系列化容器（只学系列感，不搬文案）。<br><b>【落点】</b>时效层稿件标题模板（守则62 ≤20 字）。<br><b>【依据】</b>09-20／10-10 同名不同日期（赞 604／540）。</li>
            <li><b>【动作】</b>正文以<b>可核量级开场</b>（开了多少家／热度升降）再落到投递优先级。<br><b>【落点】</b>A 层时效稿开篇（与 10/17 政策平台篇澄清式开场并列备选）。<br><b>【依据】</b>10-06「9月累计开了3100多家」；10-10「每天只有四五十家…」。</li>
          </ul>
        </div>
        <div class="panel">
          <h2><span class="dot r"></span>❌ 不可复用 / 风险</h2>
          <ul class="tight">
            <li>🔴 <b>数字不可照搬</b>：「近4000家／3100多家／每天100多家」为对方<b>自述未核验</b>（B 级），与守则1＋守则78 冲突。</li>
            <li>🔴 标签跨届堆（25fall/26fall/27届）与<b>守则55</b>（不写「2027届」）冲突，不照抄。</li>
            <li>🟡 09-24 篇（赞1209）<b>正文为空</b> → 可能是纯图/长图，文字层不足以佐证其做法，<b>不作 A／F 维依据</b>。</li>
            <li>🔴 4 篇正文实查<b>无「领取／私信」字样（0 命中）</b>；其「岗位表」引导属站内暗示，<b>只学字段结构、不学引导话术</b>——配「领取」即 P0。</li>
            <li>🔴 红狐数据<b>仅供内部</b>，不得出现在任何对外交付物；依 SOP §七·4 不得对外披露来源。</li>
          </ul>
        </div>
      </div>
    </div>
'''

CARDS_NEW = """const CARDS=[
 ['WB211','回执 · **B1 09:00 场**：① 第 0 步竞品拆解＝**刚刚（秋招版）**（红狐实跑·非降级·两轮 13 词命中 4 篇·**740 汉字** ≤800·A–F 六维）② inbox **无未处理卡**（最新 C47 已由 WB209 承接）③ 看板回写 ④ 驾驶舱同步；自纠 W-A43／W-A44','g','已发 C'],
 ['WB210','数据卡 · **账号后台三屏实读**（L 08:55 手机截图 3 张 · S 级）：「近7日」曝光 **1.7 万（-31%）**／观看 **2,938（-28%）**／CTR **18.5%**／首页推荐 **80%**；**10-17 A 层＝🔵 笔记审核中（0/0/0）**；主页 粉丝 **1,098**／关注 50','g','已采登'],
 ['WB209','回执 · **10/17 A 层已发落账 ＋ C47 确认**：桌面 `1-A层-文案-0900发.txt` 实读 1,582 B／md5 `16481dfa…`；标题 15 字／正文 308 汉字；发布版本＝WB208 专家复核定稿（红狐 6 处已清零）','g','已发 C'],
 ['C47','裁定卡 · WB207／WB208／A1 简报**三项通过**；a1（07:30）**可观测首跑成功**；探针真结果仍等 B1（09:00）／a2（10:00）','g','已执行'],
 ['WB208','回执 · **专家模式复核今日三稿**：红狐 API A 2→0／B 0→0／C 4→0，**改一处同步三处**＋重渲 6 图；三关复跑全清；🔴 固化「**红狐命中一律算命中**，不得以本地 P0=0 放过」','g','已发 C'],
 ['WB207','回执 · C46 执行：主表 no.75 note 回写（**v1.0.26→v1.0.27**，逐条 diff 仅 1 条）＋ SOP 幂等＋自检第5问＋库存命名规则（**三处同批改**）＋ C45 索引补登记 ＋ `-W版.md` 恢复（4,990 B）','g','已发 C'],
 ['WB206','请判卡 · WB205 复核差异两项＋07:00 幂等缺口：① 主表 no.75（光大 A 级 11-08）与卡上「光大兰州分行 11-08」**同法人重复** ② 10-16 同日双卡（幂等未生效 W-A41）③ C45 未登记索引','r','已发 C'],
 ['C46','裁定卡 · WB204–WB206 裁定＋**报白门槛升 P0**：① 光大同法人＝甲案＋A 级授权（改 note 不加条目）② 07:00 幂等＝甲案 ③ 库存命名「库存-」前缀；🔴 L 需 10/19 前千帆后台三项实测','r','已执行'],
 ['WB205','数据卡 · **每日 07:00 新发事件采集**（首期）：四路全跑无缺路——平台侧 6 条（C/B）／政策侧 4 条（A）／企业侧 3 条（B）／权威源 69 家（A）','g','已采登'],
 ['WB204','回执 · **10/17 B/C 两层成稿＋三层待发包出齐**：B「截止日≠关门日」325 汉字／C「往届可投口径三分类」322 汉字；三关实跑全清；桌面 `待发包-20261017-ABC层` 9 图 3 文案齐','g','已发 C'],
 ['WB203','回执 · **W 日终收口（B4 23:00）**：卡片闭环检查／自身错误补登 13 条（W-A19～A32）／索引核对／看板回写（§一·补＋指标快照）／驾驶舱同步 md5 `57bf16b9…`','g','已发 C'],
 ['WB202','回执 · **C44 裁定执行**：三条硬规则落笔（一物一路径一命名／双做须分名／写入前查现场）＋ **驾驶舱一次性改名四件**（源→`L 的工作台.html`，md5 `2defd3da…`，B1–B4 提示词同批改）','g','已发 C'],
 ['C45','裁定卡 · WB201–WB203 裁定＋同路径双写处置（**甲**）＋ **C-A17 认错**（C 静默覆盖 W 采集成果，根因 R2）；SOP 提案即日生效','y','已执行'],
 ['C44','裁定卡 · WB201 三项裁定＋医美交付物**同路径双写**冲突（甲）＋WB196 复核通过＋晚场抽检 7 项（`a3-21-00` 自动触发）','g','已执行'],
"""

def crlf(x):
    return x.replace("\r\n", "\n").replace("\n", "\r\n")

s2 = s.replace(A1, '    </div>\r\n\r\n' + crlf(CASE5) + '    <div class="panel">\r\n      <h2><span class="dot"></span>日常机制与审核线', 1)
s2 = s2.replace(A2, crlf(CARDS_NEW), 1)
b1 = s2.encode("utf-8")
open(P, "wb").write(b1)
print("AFTER  bytes=%d CRLF=%d pureLF=%d md5=%s" % (
    len(b1), b1.count(b"\r\n"), b1.count(b"\n") - b1.count(b"\r\n"), hashlib.md5(b1).hexdigest()))
print("检查：案例五=%d  WB211=%d  WB202=%d  WB210=%d" % (
    s2.count("案例五"), s2.count("WB211"), s2.count("WB202"), s2.count("WB210")))
