# -*- coding: utf-8 -*-
r"""WB219：C 层发布件 ↔ 包内正本 四项逐字程序化比对（行级解析 · 非目测）"""
import re, hashlib

DESK = r"C:\Users\Administrator\Desktop\待发包-20261017-ABC层\3-C层-文案-2030发.txt"
BAG  = r"D:\小红书项目\default-workspace\_协作\发布包\2026-10-17\笔记-XHS-20261017-WB-C层.md"

def rd(p):
    b = open(p, "rb").read()
    ls = b.split(b"\n")
    cr = sum(1 for l in ls if l.endswith(b"\r"))
    return b, b.decode("utf-8").replace("\r\n", "\n"), cr, len(ls) - 1 - cr

db, ds, dcr, dbare = rd(DESK)
bb, bs, bcr, bbare = rd(BAG)
print("桌面件   %d B  CRLF %d  纯LF %d  md5 %s" % (len(db), dcr, dbare, hashlib.md5(db).hexdigest()))
print("包内正本 %d B  CRLF %d  纯LF %d  md5 %s" % (len(bb), bcr, bbare, hashlib.md5(bb).hexdigest()))
print()

# ---------- 桌面件：按 ━━━ 分隔行切段 ----------
dl = ds.split("\n")
idx = [i for i, l in enumerate(dl) if l.startswith("━")]
D = {}
for k, i in enumerate(idx):
    end = idx[k + 1] if k + 1 < len(idx) else len(dl)
    body = [l for l in dl[i + 1:end] if l.strip()]
    D["title" if k == 0 else ("body" if k == 1 else ("tags" if k == 2 else "first"))] = "\n".join(body).strip()

# ---------- 包内正本：行级 ----------
bl = bs.split("\n")
def grab(start_pred, stop_pred):
    out, on = [], False
    for l in bl:
        if not on and start_pred(l):
            on = True
            continue
        if on and stop_pred(l):
            break
        if on:
            out.append(l)
    return [x for x in out if x.strip()]

B = {}
B["title"] = grab(lambda l: l.startswith("**标题"), lambda l: l.startswith("**正文"))
B["body"]  = grab(lambda l: l.startswith("**正文"), lambda l: l.startswith("**标签"))
B["tags"]  = grab(lambda l: l.startswith("**标签"), lambda l: l.startswith("**置顶首评"))
B["first"] = grab(lambda l: l.startswith("**置顶首评"), lambda l: l.startswith("**配图"))
for k in B:
    B[k] = "\n".join(B[k]).strip()

def norm(x):
    return re.sub(r"\s+", "", x)

def han(x):
    return len([c for c in x if "\u4e00" <= c <= "\u9fa5"])

names = [("title", "标题"), ("body", "正文"), ("tags", "标签"), ("first", "首评")]
allok = True
print("%-5s %-10s %-10s %-9s %-9s %s" % ("项", "桌面md5", "正本md5", "桌面汉字", "正本汉字", "结论"))
for k, nm in names:
    a, b2 = D.get(k, ""), B.get(k, "")
    ha, hb = hashlib.md5(norm(a).encode()).hexdigest()[:8], hashlib.md5(norm(b2).encode()).hexdigest()[:8]
    same = norm(a) == norm(b2) and norm(a) != ""
    allok &= same
    print("%-5s %-10s %-10s %-9d %-9d %s" % (nm, ha, hb, han(a), han(b2), "✅ 逐字一致" if same else "❌ 不一致"))
print()
print("总判定:", "✅ 发布版本＝定稿版本，无返工" if allok else "❌ 存在差异，须逐字核")
print()
t = D["title"]
print("标题: %d 字符（去空格）／%d 汉字 ｜ %s" % (len(t.replace(" ", "")), han(t), t))
print("正文: %d 汉字 ｜ 段数 %d" % (han(D["body"]), len([l for l in D["body"].split("\n") if l.strip()])))
print("标签: %d 个 ｜ %s" % (len(D["tags"].split()), D["tags"]))
print("首评: %d 汉字 ｜ %s" % (han(D["first"]), D["first"]))
print()
cta = [l for l in D["body"].split("\n") if l.strip()][-1]
print("正文结尾 CTA :", cta)
print("首评前 10 字  :", D["first"][:10])
print("是否逐字撞（首评前10字 ⊂ CTA）:", D["first"][:10] in cta)
print()
hits = []
for kw in ["200 家", "200家", "123 家", "123家", "截止", "华为", "国家电网", "六险一金", "包吃住", "不限院校", "二本能进"]:
    for seg in (D["title"], D["body"], D["first"], D["tags"]):
        if kw in seg:
            hits.append(kw)
print("敏感元素命中:", sorted(set(hits)) if hits else "零命中 ✅（家数／企业名／待遇／学历门槛断言均无）")

# 首评「复制即发」包
out = r"D:\小红书项目\default-workspace\_协作\发布包\2026-10-17\C层-首评-复制即发.txt"
open(out, "wb").write(D["first"].encode("utf-8"))
print()
print("已生成首评复制即发件:", out)
print(repr(open(out, "rb").read()))
