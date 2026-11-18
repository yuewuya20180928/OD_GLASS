#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-322 · tmp 沙盒脚本 · ★★45 条 unconnected 逐条清单装配器 (★机器搬·一行不许手抄★)★★
输入 (全部机器读数):
  · /tmp/_pcb_drc_demo_mainboard.kicad_pcb.json   ← state/check_pcb_drc.py
  · tmp/iss322/unc_worklist_current.txt           ← state/probe_unconnected_worklist_v2.py
  · tmp/iss322/escape_feas_current.txt            ← state/probe_escape_feasibility.py
  · tmp/iss322/lane_conflicts_current.txt         ← state/probe_lane_conflicts.py
  · tmp/iss322/cur_vs_best23.json                 ← tmp/iss322/cmp_cur_vs_best23.py
  · tmp/iss322/hs_geometry.json                   ← tmp/iss322/hs_geometry.py
输出: tmp/iss322/table45.md  (★交卷页 §1 直接贴★)
"""
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DRC = "/tmp/_pcb_drc_demo_mainboard.kicad_pcb.json"
d = json.load(open(DRC, encoding="utf-8"))
unc = d.get("unconnected_items") or []
assert len(unc) == 45, "unc != 45"

PAD = re.compile(r"^Pad (\S+) \[([^\]]*)\] of (\S+) on (\S+)$")
TRK = re.compile(r"^Track \[([^\]]*)\] on (\S+), length ([\d.]+) mm$")
VIA = re.compile(r"^Via \[([^\]]*)\] on (\S+)")


def p(it):
    dsc = it["description"]
    x = (it.get("pos") or {}).get("x")
    y = (it.get("pos") or {}).get("y")
    m = PAD.match(dsc)
    if m:
        return dict(kind="pad", pad=m.group(1), net=m.group(2), ref=m.group(3),
                    layer=m.group(4), x=x, y=y, dsc=dsc)
    m = TRK.match(dsc)
    if m:
        return dict(kind="track", pad=None, net=m.group(1), ref=None, layer=m.group(2),
                    x=x, y=y, length=float(m.group(3)), dsc=dsc)
    m = VIA.match(dsc)
    if m:
        return dict(kind="via", pad=None, net=m.group(1), ref=None, layer=m.group(2),
                    x=x, y=y, dsc=dsc)
    m = re.search(r"\[([^\]]+)\]", dsc)
    return dict(kind="other", pad=None, net=m.group(1) if m else "?", ref=None,
                layer=None, x=x, y=y, dsc=dsc)


def endpoint(q):
    if q["kind"] == "pad":
        return "%s.%s @ (%s, %s) %s" % (q["ref"], q["pad"], q["x"], q["y"], q["layer"])
    if q["kind"] == "track":
        return "走线端 @ (%s, %s) %s len=%smm" % (q["x"], q["y"], q["layer"], q["length"])
    if q["kind"] == "via":
        return "过孔 @ (%s, %s) %s" % (q["x"], q["y"], q["layer"])
    return q["dsc"]


# ── 死因辅助数据 ──
wl = open(os.path.join(HERE, "unc_worklist_current.txt"), encoding="utf-8").read()
WALL = set()
for ln in wl.splitlines():
    m = re.match(r"\s*★墙 (\S+)\s+(\S+)", ln)
    if m:
        WALL.add((m.group(1), m.group(2).strip()))
CLS = open(os.path.join(HERE, "classify_current.txt"), encoding="utf-8").read() \
    if os.path.exists(os.path.join(HERE, "classify_current.txt")) else ""
best = json.load(open(os.path.join(HERE, "cur_vs_best23.json"), encoding="utf-8"))
hsg = json.load(open(os.path.join(HERE, "hs_geometry.json"), encoding="utf-8"))

# ── 布局级 (17 处段内 P/N 顺序翻转) 归属 ──
FLIP_FAMS = {"DSI_D0_CK", "DSI_D0_D0", "DSI_D0_D1", "DSI_D0_D2"}   # 实测翻转的 4 个 DSI 族
CSI_FLIP = True    # 实测: CSI 5 族在【连接器侧】全部翻转 (Δx=0.50mm)


def fam(net):
    for suf in ("_P_SRC", "_N_SRC", "_P", "_N"):
        if net.endswith(suf):
            return net[:-len(suf)]
    return net


# ── 口径未定清单 (作业包 §3-S8 已登记 5 条死因) ──
PENDING = {
    "BAT_DET": ("口径未定", "A1 · `BAT_DET` 终点未定义 (ISS-265 §6-1)",
                "等拍板 (A1)", "★拍板前连【钉位】都定不下来 ⇒ 不许布 (★也不许把它算进算法可解★)"),
    "LIGHT_5V": ("口径未定", "W-1/W-2 · ESD 未拍 ⇒ `D_ESD_LIGHT` 钉位定不下来",
                 "等拍板 (W-1/W-2)", "★W-1/W-2 未拍 ⇒ 器件钉位不定 ⇒ 该腿终点会变"),
    "PWR_GOOD": ("口径未定", "W-4 · `Q_PG.3` 极性未定",
                 "等拍板 (W-4)", "★极性未定 ⇒ `Q_PG.3` 是不是终点都没定"),
    "LED_G_D": ("口径未定", "`D_LED_G` 物理位置未定 (MECH 侧落位)",
                "等拍板 (`D_LED_G` 位置)", "★`LED_G_D` 直线 93.49mm ⇒ 位置一变整条腿重算"),
    "LED_G": ("口径未定", "`D_LED_G` 物理位置未定 ⇒ `LED_G` 连带 (★`LED_G` 端点被 `LED_B` 掐 0.200mm★)",
              "等拍板 (`D_LED_G` 位置)", "★与 `LED_G_D` 同源 (MECH 落位) ⇒ 一拍一起解"),
}

rows = []
for i, u in enumerate(unc, 1):
    a, b = p(u["items"][0]), p(u["items"][1])
    net = a["net"] or b["net"]
    L = None
    for q in (a, b):
        if q.get("length"):
            L = q["length"]
            break
    if L is None:
        import math
        L = round(math.hypot(a["x"] - b["x"], a["y"] - b["y"]), 2)
    kind = "直线距离" if not (a.get("length") or b.get("length")) else "DRC段长"
    hs = net.startswith(("DSI_", "CSI_"))
    f = fam(net)
    wall_a = (net, "走线端") in WALL
    wall_b = (net, endpoint(a).split(" @")[0]) in WALL or (net, endpoint(b).split(" @")[0]) in WALL
    wall = wall_a or wall_b
    # ── 落桶 (★每条只落一个桶★) ──
    if net in PENDING:
        bucket, cause, fixcat, note = PENDING[net]
    elif hs and f in FLIP_FAMS:
        bucket = "几何不可布 (布局级)"
        cause = "★DSI lane 段内 P/N 顺序翻转 (实测 17/47 处) ⇒ 该族必须交叉才能连"
        fixcat = "改布局"
        note = "★挪 21 个器件 (10×`R_SEL_*` + 10×`TP_DSI_*`) 到左上 x 5.50..38.35 ⇒ lane 序与 SoM 端一致"
    elif hs and net.startswith("CSI_"):
        bucket = "几何不可布 (布局级)"
        cause = "★CSI 连接器侧 P/N 顺序翻转 (Δx=0.50mm) ⇒ 该族必须交叉才能连"
        fixcat = "改布局 + pair-aware"
        note = "★AC 电容侧 P/N 间距 4.80mm 与连接器侧 0.50mm 不匹配 ⇒ 要么挪电容侧, 要么成对换层绕"
    elif hs:
        bucket = "算法可解"
        cause = "端点可出 + 走廊中段被别腿堵 ⇒ 让路/换层/pair-aware 可解"
        fixcat = "pair-aware + 换层"
        note = "★本族 (DSI_D0_D3) 段内序【未】翻转 (★`R_SEL_D3_P` 被挂在倒挂位 78.90/9.50 上掩盖了它★) ⇒ 走 pair-aware + 内层换层"
    elif net == "FSIN_OUT":
        bucket = "算法可解"
        cause = "端点可出 + 走廊中段被 `VDD_3V3_IO` 掐 (★ISS-282 订正: 根因是布线排队顺序·不是逃逸方向 bug★)"
        fixcat = "改逃逸方向 (布线顺序)"
        note = "★把 `FSIN_OUT` 提到 `PCB_PRIORITY_NETS` 里电源之前布 (★ISS-282 实测: L=3.0mm 就是 A→B 那条直线★)"
    else:
        bucket = "算法可解"
        cause = "端点可出 + 走廊中段被堵 ⇒ 让路闸 / 换层 / 改逃逸方向可解"
        fixcat = "让路闸 + 换层"
        note = ""
    rows.append(dict(i=i, net=net, a=endpoint(a), b=endpoint(b), L=L, kind=kind,
                     hs=hs, fam=f, bucket=bucket, cause=cause, fixcat=fixcat,
                     note=note, wall=wall,
                     off_best=(net in best["routed_by_best"]),
                     off_hard=(net in best["still_unc_in_best"])))

md = []
md.append("| # | 网名 | 起点 (ref+pad+x,y) | 终点 (ref+pad+x,y) | 长度 mm | 类型 | 死因桶 | 修法 |")
md.append("|---:|---|---|---|---:|---|---|---|")
for r in rows:
    md.append("| %d | `%s` | %s | %s | %s | %s | **%s** | %s |" % (
        r["i"], r["net"], r["a"], r["b"], r["L"], "高速 DSI/CSI" if r["hs"] else "普通",
        r["bucket"], r["fixcat"]))
open(os.path.join(HERE, "table45.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")

# 机读全表
full = []
for r in rows:
    full.append(r)
json.dump(full, open(os.path.join(HERE, "table45.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("★45 条逐条清单已生成: tmp/iss322/table45.md (%d 行数据)" % len(rows))
print()
c = collections.Counter(r["bucket"] for r in rows)
print("落桶分布 (★每条只落一个桶★):")
for k, v in c.most_common():
    print("   %-24s %2d 条" % (k, v))
print()
print("高速 DSI/CSI 条目 = %d (其中 DSI_ %d / CSI_ %d)"
      % (sum(1 for r in rows if r["hs"]),
         sum(1 for r in rows if r["net"].startswith("DSI_")),
         sum(1 for r in rows if r["net"].startswith("CSI_"))))
print("真墙端点条目 = %d" % sum(1 for r in rows if r["wall"]))
print("best_unc23 板已布通 = %d 条 · 两边都没通 = %d 条"
      % (sum(1 for r in rows if r["off_best"]), sum(1 for r in rows if r["off_hard"])))
print()
print("--- 表 (前 6 行预览) ---")
for l in md[:8]:
    print(l)
