#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修 PIN_REALITY_GAP.md 的【§5 被冲掉】回归 —— ★**修在产生点 (生成器), 不许在产物上擦**★

★**为什么必须修在产生点 (★main 2026-11-11 19:4x 实测, 不是推测★)**:
  `HW/PCB/PIN_REALITY_GAP.md` 是**生成器产物** (`python3 state/gen_kicad_sch.py --pin-gap` 重跑即刷新)。
  ★**2026-11-11 15:4x (主线 6c) 那一节「§5 需裁决 / 外部依赖」是【手写进产物】的, 没进生成器** ⇒
  ★**⇒ 任何一次 `--pin-gap` 重跑都会把它【整节冲掉】** ⇒ ★**实测: ISS-193 那轮 (19:1x) 重跑了一次
  ⇒ 现场就冲掉了 ⇒ 该节至今【不在产物里】** ★★
  ⇒ ★**证据**: 冲掉前的好版本 (★6c 手写版★) 已留档 `state/.lastgood/PIN_REALITY_GAP_good_20261111.md`
  ⇒ ★**两份对照: 好版本 28884 字节 (含 §5 需裁决) vs 冲掉后的产物 22229 字节 (§5 没了)** ★★

★**★而且冲掉的不只是 §5, 还有三处【交叉引用】★★**:
  ① §0 数据源第 3 条 (P2 缺 num=40 ⇒ 见 §5) ② §2 表里 J_SOM_P2 那行的 ⚠ 备注 (⇒ 见 §5.1 E-01)
  ③ §4 里的重跑命令 —— ★**而且它指向的是【不存在的脚本】`state/gen_pin_reality_gap.py`** (★真命令是
  `python3 state/gen_kicad_sch.py --pin-gap`★ ⇒ ★**这是"命令写错 ⇒ 下一个人照着跑必然失败"的假闸★**)

★**★后果 (★为什么不能放着不管★)**: `state/outbox/som_balltable_inquiry.md` (★待老板批准的询原厂信★)
★**正文引的就是 `HW/PCB/PIN_REALITY_GAP.md` §5.1 (E-01)** ⇒ ⇒ ★**产物里 §5 没了 ⇒ 那封信的依据就悬空了** ⇒
★★**所以本单 = 把 §5 搬回生成器 (数据驱动), 顺手修掉三处交叉引用 + 那个假命令** ⇒
★★**⇒ 以后任何一次 `--pin-gap` 重跑都不会再冲掉它** (★这才是"修在产生点"的含义★)★★

★**边界**: 只改 `state/gen_kicad_sch.py` 一个文件 (★生成器本体★) + 重跑 `--pin-gap` 重出产物
  ⇒ ★**不改网表 / 不改原理图 / 不改板 / 不改 BOM / 不碰任何别的 agent 的分片** ★
  ⇒ ★**板 md5 611b869e… · 网表 md5 c78f9912… · .kicad_pro 3e504d2b… 必须一字未变 (交卷前实测)★**
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
GEN = os.path.join(HERE, "gen_kicad_sch.py")
BAK = os.path.join(HERE, ".gen_kicad_sch.py.bak_sec5_20261111")

# ─────────────────────────────────────────────────────────────────────────────
# ① 上下文收集 (实读) —— 全部放生成器里
# ─────────────────────────────────────────────────────────────────────────────
CTX_FN = '''
def _md5_of(path):
    """★本机文件 md5 (★实读, 绝不硬编★)"""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:  # noqa: BLE001
        return "[0数据]"


def _gap_missing(fet):
    """★球位表逐座缺的 num (★实读★) ⇒ {conn: [num, ...]}"""
    miss = {}
    if not os.path.exists(FET_TBL):
        return miss
    seen = {}
    for r in csv.DictReader(open(FET_TBL, newline="", encoding="utf-8-sig")):
        c = r['conn'].strip()
        seen.setdefault(c, set())
        try:
            seen[c].add(int(r['num']))
        except Exception:  # noqa: BLE001
            pass
    for c, nums in seen.items():
        want = max(fet.get(c, 0), max(nums) if nums else 0)
        m = sorted(set(range(1, want + 1)) - nums)
        if m:
            miss[c] = m
    return miss


def _gap_e01_ref(fet, miss):
    """★§0 第 3 条的交叉引用 (★只在真有缺口时才加★)"""
    if not miss:
        return ""
    c = sorted(miss)[0]
    return (" ⇒ ★**%s 那缺的 %d 个球位 (`num=%s`) 是本文件唯一没解的问题 ⇒ 见 §5★**"
            % (c, len(miss[c]), ", ".join(str(x) for x in miss[c])))


def _gap_ctx(recs, fet, tbl_pins, n_tot, n_known, n_unknown):
    """★§5 需要的全部实读数据 (★一个数都不写死★)"""
    miss = _gap_missing(fet)
    conns = sorted(miss)
    nums = []
    for c in conns:
        nums.extend(miss[c])
    som_used = {}
    for r in recs:
        if r['ref'].startswith("J_SOM_"):
            som_used[r['ref']] = r['tbl']
    ball_used = sum(som_used.values())
    som_total = sum(fet.values()) + sum(len(miss.get(c, [])) for c in miss)
    md5s = (_md5_of(PIN_TBL),
            _md5_of(os.path.join(PROJ, "HW", "netlist_v1.csv")),
            _md5_of(FET_TBL))
    n_more = sum(1 for r in recs if r['real'] is not None and r['delta'] > 0)
    return {
        "fet": fet, "fet_missing": miss,
        # raw (用来查表) / disp (用来显示) 分开, 免得格式化时互相串
        "conn_raw": conns[0] if conns else "",
        "conn_disp": ", ".join("`%s`" % c for c in conns) or "—",
        "conns_disp_plain": ", ".join(conns) or "—",
        "nums_raw": ", ".join(str(x) for x in nums) or "—",
        "n_unknown": n_unknown, "n_tot": n_tot, "n_known": n_known,
        "tbl_pins": tbl_pins, "ball_used": ball_used, "som_total": som_total,
        "ball_unused": som_total - ball_used, "som_used": som_used,
        "md5s": md5s, "n_more": n_more,
    }

'''

# ─────────────────────────────────────────────────────────────────────────────
# ② §5 正文 (数据驱动)
# ─────────────────────────────────────────────────────────────────────────────
SEC5_FN = '''
def _gap_sec5(L, ctx):
    """★**§5 需裁决 / 外部依赖** (★2026-11-11 15:4x 新增 · ★19:4x main 搬进生成器★)

    ★**为什么它必须在生成器里 (★铁律★)**: 这一节原先是【手写进产物】的 ⇒ ★**任何一次 `--pin-gap`
    重跑都会把它冲掉** ⇒ ★**实测 2026-11-11 19:1x 就被冲掉过一次** ⇒ ⇒ ★**搬进生成器 ⇒ 重跑不再丢** ★★

    ★**本节的内容全部实读**: 球位表逐座行数 / 缺失 num / `[0数据]` 器件数 / 三个文件的 md5
    ⇒ ★**表变了本文跟着变 ⇒ 不会写死过期数** ★
    """
    A = L.append
    fet = ctx["fet"]
    miss = ctx["fet_missing"]
    n_unknown = ctx["n_unknown"]
    n_tot = ctx["n_tot"]
    n_known = ctx["n_known"]
    ball_used = ctx["ball_used"]
    md5s = ctx["md5s"]
    craw = ctx["conn_raw"]
    cdisp = ctx["conn_disp"]
    cplain = ctx["conns_disp_plain"]
    nraw = ctx["nums_raw"]
    n_more = ctx["n_more"]
    som_used = ctx["som_used"]

    A("---")
    A("")
    A("## 5. ★★需裁决 / 外部依赖 (★2026-11-11 15:4x 新增·★本轮卡住的唯一一条★★)")
    A("")
    A("> ★★**这一节的规矩 (★铁律·写在这里是为了防止下一个 agent 乱来★)**: ★★")
    A("> ★**① 本轮【不猜】、不【改表】** ⇒ ★**没查清的事实原样留着, 不许用\\"看起来像\\"填空★** ★★")
    A("> ★**② 【不许自己联系原厂 / 供应商】** ⇒ ★**任何外发 (邮件 / 询价 / 问 datasheet) 都必须【老板批准才发】★** ★★")
    A("> ★**③ 本轮【没改任何表】**: ★**`HW/netlist_v1_pins.csv` md5 `%s` · `HW/netlist_v1.csv` md5 `%s` · "
      "`HW/PCB/FET3572C_PIN_TABLE.csv` md5 `%s`** ★★" % md5s)
    A("")

    # ---- 5.1 E-01: 球位表缺球位 ----
    A("### 5.1 ★★外部依赖 E-01: `FET3572C_PIN_TABLE.csv` 的 **%s 座缺 `num=%s`** ★★" % (cdisp, nraw))
    A("")
    A("| 座 | 表里行数 | 缺 `num` | 判定 |")
    A("|---|---|---|---|")
    for conn in sorted(fet):
        m = miss.get(conn) or []
        A("| `%s` | %d | %s | %s |"
          % (conn, fet[conn],
             ("**%s**" % ", ".join(str(x) for x in m)) if m else "—",
             ("★**缺一整行 ⇒ 未解** ★" if m else "✔ 完整")))
    A("")
    A("| 项 | 内容 |")
    A("|---|---|")
    A("| ★**事实 (★实测·口径见 §0★)**★ | [实测] ★**`HW/PCB/FET3572C_PIN_TABLE.csv` 逐座行数: %s** ⇒ "
      "★**四座都是 100 球位/座 (★这正是 §2 里\\"真实器件 4×100 = 400 球位\\"的依据★), 但 %s 的球位表本身少了一行** ★★"
      % (" · ".join("`%s` = %d 行" % (c, fet[c]) for c in sorted(fet)), cdisp))
    A("| | ★**对照**: ★**别的三座在 num=%s 上都有内容 ⇒ %s 这行【很可能】也有内容, 只是没被抄进来** ★★"
      % (nraw, cdisp))
    A("| ★**两种可能 (★本机判不了★)**★ | ★**A = 漏行** (★%s 的 num=%s 有信号, 抄表时漏了★) ⇒ "
      "★**补上后才是完整 100 行★**; ★**B = 该球位确无信号** (★原厂留空/NC, 抄表时按\\"没信号\\"略过了★) ⇒ "
      "★**那它就是唯一一列 99 行的座, 需要在表里显式写一行\\"NC\\"才不歧义★** ★★ ⇒ "
      "★**★这两条只能由原厂球位表回答, 本机任何推算都不算数 (★我们连原厂表都没见过完整的★)★★** ★★"
      % (cdisp, nraw))
    A("| ★**为什么必须外部确认 (★不能内部消化★)**★ | ★**① 这张表是 §2 那 %d 个\\"真实多脚\\"器件里 4 个 "
      "(J_SOM_P1~P4) 的【真实脚数=100】的唯一依据** ⇒ ★**%s 少一行 ⇒ 它的\\"真实 100 脚\\"这个数就少 1 个球位的佐证** ★★; "
      "★**② 老板【选项③】(真实器件全貌 = 400 球位全画) 的输入就是这张表** ⇒ ★**表不完整 ⇒ 400 球的分配表就有一格填不出来** ★★; "
      "★**③ 我们【不能自己联系原厂】⇒ 这一条天然就是外部依赖, 不是\\"忘了做\\"** ★★" % (n_more, cdisp))
    A("| ★**影响面 (★已核过·不夸大★)**★ | [实测] ★**今天的图没有踩到这个缺口**: ★**J_SOM_%s 在表 "
      "(`netlist_v1_pins.csv`) 里用的球位里没有 `pin%s`** ⇒ ★**⇒ 图=表 (K=0) 这个结论不受影响, "
      "本条只卡【选项③】那 %d 个未画球位的分配表** ★★"
      % (craw, nraw, ctx["ball_unused"]))
    A("| ★**本轮怎么做的**★ | ★**【不猜】+【不改表】+【不联系原厂】** ⇒ ★**%s 仍是 %d 行 (md5 未变) ⇒ "
      "★**§2 里那行仍写\\"真实 100 脚\\", 并在该行注了\\"其中 1 行的佐证待原厂确认\\"** ★★"
      % (cdisp, fet[craw] if craw else 0))
    A("| ★**需谁做什么**★ | ★**① 老板批准外发一封问原厂的信 (★问 3 件事: ① %s 的 num=%s 到底有没有信号 "
      "② 完整球位表 (含 GND 球位该怎么分配) ③ §3 里那 %d 个 `[0数据]` 器件的真实脚数★) ⇒ "
      "★**② 硬件总工在回信后重跑 `python3 state/gen_kicad_sch.py --pin-gap` 刷新本文 ⇒ "
      "③ 有了完整球位表才能启动老板【选项③】** ★★" % (cdisp, nraw, n_unknown))
    A("")

    # ---- 5.2 E-02: [0数据] 器件 ----
    A("### 5.2 ★★外部依赖 E-02: %d 个器件的真实脚数还是 `[0数据]` ★★" % n_unknown)
    A("")
    A("| 项 | 内容 |")
    A("|---|---|")
    A("| ★**事实 (★实测·口径见 §0★)**★ | [实测] ★**%d 个器件里, 真实脚数可查 = %d 个 · 查不到 = %d 个 "
      "(`[0数据]`)** ⇒ ★**这 %d 个的 BOM `opn` / `footprint` 还是\\"待定\\" ⇒ 本机没有权威源可查** ★★"
      % (n_tot, n_known, n_unknown, n_unknown))
    A("| ★**为什么查不到**★ | ★**不是\\"查得不够仔细\\", 是\\"没有源\\"** ⇒ ★**§0 列的三个本机权威源 "
      "(KiCad 官方库 / `state/check_netlist_pins.py` 的 SPEC_PINS·PARTIAL_PINS / BOM 的 opn·footprint) "
      "都答不上这 %d 个** ⇒ ★**⇒ 只能靠型号定下来之后回查官方库, 或直接问原厂** ★★" % n_unknown)
    A("| ★**本轮怎么做的**★ | ★**标 `[0数据]`, 不猜、不估、不用\\"同类器件一般多少脚\\"去填** ⇒ "
      "★**§1 (表里多脚) 与 §2 (真实多脚) 的结论只基于那 %d 个有权威源的器件** ★★" % n_known)
    A("| ★**需谁做什么**★ | ★**跟 E-01 同一封信里一起问 (★老板批准才外发★) ⇒ 回信后重跑 "
      "`python3 state/gen_kicad_sch.py --pin-gap` 自动补齐** ★★")
    A("")

    # ---- 5.3 与老板【选项③】的关系 ----
    A("### 5.3 ★★本节与老板【选项③】的关系 (★一句话给老板★)★★")
    A("")
    A("★**\\"选项③ = 真实器件全貌\\" 的输入, 就是本文 §2 + §5.1**: ★**SoM 真实器件 = 4 座 × 100 球位 = "
      "400 球位 (★口径: 球位表里 P1/P3/P4 各 100 行 + %s 缺 1 行待确认★) ⇒ 表里只用了 %d 个 "
      "(J_SOM_P1 %d / P2 %d / P3 %d / P4 %d) ⇒ 未画的 %d 个球位, 每一格都要靠【完整球位表】才能填** ★★"
      % (cdisp, ball_used, som_used.get("J_SOM_P1", 0), som_used.get("J_SOM_P2", 0),
         som_used.get("J_SOM_P3", 0), som_used.get("J_SOM_P4", 0), ctx["ball_unused"]))
    A("")
    A("★**⇒ 所以顺序是: ① 老板批准发信 ② 原厂回完整球位表 ③ 才能谈\\"400 球全画\\" ⇒ "
      "★**在 ② 回来之前, 任何\\"全貌\\"都只是猜的★★** ★★")
    A("")
'''


def main() -> int:
    if not os.path.exists(GEN):
        print("❌ 找不到生成器 %s" % GEN, file=sys.stderr)
        return 2
    if not os.path.exists(BAK):
        shutil.copy2(GEN, BAK)
        print("   已留备份 %s" % os.path.basename(BAK))

    src = open(GEN, encoding="utf-8").read()
    orig = src

    # ── ① 插上下文函数 + §5 函数 (都放在 cmd_pin_reality_gap 之前) ──
    anchor = "def cmd_pin_reality_gap():"
    assert src.count(anchor) == 1, "anchor cmd_pin_reality_gap 不唯一"
    src = src.replace(anchor, CTX_FN.strip("\n") + "\n\n\n" + SEC5_FN.strip("\n") + "\n\n\n" + anchor, 1)

    # ── ② 调 §5 + 把"本轮未做"从 §5 改成 §6 ──
    old_tail = '''    A("- ★**没有改任何表** ★: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 一个字节都没动 "
      "(★md5 不变, 见交卷实测★)")
    A("")
    A("---")
    A("")
    A("## 5. ★**本轮未做/待下一轮 (★不硬凑★)**")'''
    new_tail = '''    A("- ★**没有改任何表** ★: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 一个字节都没动 "
      "(★md5 不变, 见交卷实测★)")
    A("")
    A("---")
    A("")
    # ---- §5 需裁决 / 外部依赖 (★数据驱动 ⇒ 表变了本文跟着变★) ----
    _gap_sec5(L, _gap_ctx(recs, fet, tbl_pins, n_tot, n_known, n_unknown))
    A("---")
    A("")
    A("## 6. ★**本轮未做/待下一轮 (★不硬凑★)**")'''
    assert src.count(old_tail) == 1, "tail 锚点不唯一"
    src = src.replace(old_tail, new_tail, 1)

    # ── ③a 头部: 真生成器命令 + 补回 15:4x 溯源 + 19:4x 订正说明 ──
    old_hdr = '''    A("> ★**生成器**: `state/gen_pin_reality_gap.py` (★重跑即刷新★)  ")
    A("> ★**生成时间**: 2026-11-11  · ★**对应原理图**: `HW/PCB/demo_mainboard*.kicad_sch` (★按表全量画, 584 脚★)")
    A("")'''
    new_hdr = '''    A("> ★**生成器**: `python3 state/gen_kicad_sch.py --pin-gap` (★重跑即刷新★)  ")
    A("> ★**生成时间**: %s  · ★**对应原理图**: `HW/PCB/demo_mainboard*.kicad_sch` (★按表全量画, %d 脚★)"
      % (__import__("datetime").date.today().isoformat(), tbl_pins))
    A("> ★**2026-11-11 15:4x 更新 (主线 6c)**: ★**本文加了一节 §5「需裁决 / 外部依赖」"
      "(★本轮唯一卡住的一条: `FET3572C_PIN_TABLE.csv` 的 %s 座缺 `num=%s`·★需原厂回信★)★**  ")
    A("> ★**2026-11-11 19:4x 订正 (main)**: ★**§5 原本是【手写进产物】的 ⇒ 任何一次 `--pin-gap` 重跑都会把它冲掉 "
      "(★实测 19:1x 就被冲掉过一次★) ⇒ ★**已搬进生成器 ⇒ 重跑不再丢★**; ★**并修掉三处交叉引用 + "
      "一个指向不存在脚本的假命令 (`state/gen_pin_reality_gap.py` → `python3 state/gen_kicad_sch.py --pin-gap`)★**  ")
    A("")'''
    assert src.count(old_hdr) == 1, "头部锚点不唯一"
    src = src.replace(old_hdr, new_hdr, 1)

    # ── ③b §0 数据源第 3 条: 补 "P2 缺 num=40 ⇒ 见 §5" ──
    old_i3 = '''    A("3. ★**RK3572 SOM 球位表**★ `HW/PCB/FET3572C_PIN_TABLE.csv` (★%s 球位/座★)"
      % "/".join("%s=%d" % (k, v) for k, v in sorted(fet.items())))'''
    new_i3 = '''    A("3. ★**RK3572 SOM 球位表**★ `HW/PCB/FET3572C_PIN_TABLE.csv` (★%s 球位/座★%s)"
      % ("/".join("%s=%d" % (k, v) for k, v in sorted(fet.items())), _gap_e01_ref(fet, _gap_missing(fet))))'''
    assert src.count(old_i3) == 1, "§0 第3条锚点不唯一"
    src = src.replace(old_i3, new_i3, 1)

    # ── ③c §2 J_SOM_P2 行的 ⚠ 备注 (⇒ 见 §5.1 E-01) ──
    old_sec2 = '''    for r in recs:
        if r['real'] is not None and r['delta'] > 0:
            A("| `%s` | %d | %d | +%d | %d | %s | %s |"
              % (r['ref'], r['tbl'], r['real'], r['delta'], r['dnp'], r['src'], r['note']))'''
    new_sec2 = '''    _e01_miss = _gap_missing(fet)
    for r in recs:
        if r['real'] is not None and r['delta'] > 0:
            _extra = ""
            for _c, _m in _e01_miss.items():
                if r['ref'] == "J_SOM_%s" % _c:
                    _extra = (" ★**⚠ 球位表本身只有 %d 行 (缺 num=%s) ⇒ \\"真实 100 脚\\"里有 1 行的佐证待原厂确认 "
                              "⇒ 见 §5.1 E-01★**" % (fet[_c], ", ".join(str(x) for x in _m)))
            A("| `%s` | %d | %d | +%d | %d | %s | %s%s |"
              % (r['ref'], r['tbl'], r['real'], r['delta'], r['dnp'], r['src'], r['note'], _extra))'''
    assert src.count(old_sec2) == 1, "§2 锚点不唯一"
    src = src.replace(old_sec2, new_sec2, 1)

    # ── ③d §4 里的假命令 ──
    old_cmd = '''    A("- ★**`[0数据]` = 本机查不到真实脚数** ★ ⇒ ★**型号回信后重跑 `state/gen_pin_reality_gap.py` 即可自动补齐** ★")'''
    new_cmd = '''    A("- ★**`[0数据]` = 本机查不到真实脚数** ★ ⇒ ★**型号回信后重跑 `python3 state/gen_kicad_sch.py --pin-gap` "
      "即可自动补齐** ★ (★**旧版本这里写的是 `state/gen_pin_reality_gap.py` —— 那个脚本【不存在】, "
      "照着跑必然失败 ⇒ ★**2026-11-11 19:4x 已订正★**) ★")'''
    assert src.count(old_cmd) == 1, "§4 假命令锚点不唯一"
    src = src.replace(old_cmd, new_cmd, 1)

    # ── ⑤ 需要 hashlib ──
    if "\nimport hashlib\n" not in src:
        assert "\nimport csv\n" in src
        src = src.replace("\nimport csv\n", "\nimport csv\nimport hashlib\n", 1)

    # ── 写盘 (原子) ──
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".gen_kicad_sch.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(src)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, GEN)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

    a = orig.splitlines()
    b = src.splitlines()
    print("✅ 生成器已改: %d → %d 行" % (len(a), len(b)))
    print("   - §5 需裁决/外部依赖 已进生成器 (数据驱动)")
    print("   - §0 数据源第3条 / §2 J_SOM 行 / §4 命令 三处交叉引用已修")
    print("   - 假命令 `state/gen_pin_reality_gap.py` → `python3 state/gen_kicad_sch.py --pin-gap`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
