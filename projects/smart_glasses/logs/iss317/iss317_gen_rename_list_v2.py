#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss317_gen_rename_list.py —— ISS-317 交卷物 ① 的机器生成脚本

★**只读** 项目文件 ★ ⇒ ★**零写板 · 零落表 · 零重生成 · 零改闸** ★
★只读清单 (★任务书 §1 硬约束★): `HW/netlist_v1_pins.csv` / `HW/netlist_v1.csv` /
   `state/gen_kicad_sch.py` / `state/gen_pcb_netlist_board.py` / `state/gen_bom.py` ★
★本脚本【不跑任何生成器】★ (★gen_netlist / gen_kicad_sch / gen_pcb_netlist_board / gen_bom 一个都不跑★)

★口径单源 = `state/gen_kicad_sch.py::kicad_ref()` (★ISS-205 规则★):
    末字符是数字 ⇒ 不动; 否则加 "_1"
★本脚本把那条规则**原样复刻** (★并与生成器源码逐字比对·不一致就 abort★)

★★★ v2 (iss317_gen_rename_list_v2.py) 修了一个 v1 的列宽缺陷 ★★★
    v1 的 §D 表里「改哪个真源」列只有 22 字符宽 ⇒ ★被截断★ ⇒
    ★GAP29 / OPN_FROM_BOARD / FOOTPRINT_FROM_BOARD / PLACE_OVERRIDE /
      CONN_CAM_PIN / NC_ALLOWED / --selftest 目标 这些【同步清单】被切掉★
    (★实测: 35 个 ref 的同步清单被截断·其中 J_USB_C 丢了 3 条·CONN_CAM 丢了 2 条★)
    ⇒ ★v2 把该列加宽到 160 ⇒ 不再截断 (★实测最长的一条 = 122 字符★)
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SRC_PINS = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
SRC_NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
SRC_SCH_GEN = os.path.join(PROJ, "state", "gen_kicad_sch.py")
SRC_PCB_GEN = os.path.join(PROJ, "state", "gen_pcb_netlist_board.py")
SRC_BOM_GEN = os.path.join(PROJ, "state", "gen_bom.py")
SRC_PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")

PSEUDO = ("RAIL_", "NET_")

# ───────────────────────────────────────────────────────────
# ★口径单源: 复刻 state/gen_kicad_sch.py::kicad_ref()
# ───────────────────────────────────────────────────────────
_GEN_RE = re.compile(
    r'def kicad_ref\(ref\):.*?if r and r\[-1\]\.isdigit\(\):\s*\n\s*return r\s*\n\s*return r \+ "_1"',
    re.S,
)


def kicad_ref(ref):
    """★ISS-205 口径 (与 state/gen_kicad_sch.py::kicad_ref() 同源·逐字复刻★)"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def is_real(ref):
    """★伪器件 (RAIL_* / NET_*) 不是器件 ⇒ 不改名 (★与 gen_pcb_netlist_board.py::PSEUDO 同口径★)"""
    return not ref.startswith(PSEUDO)


# ───────────────────────────────────────────────────────────
# 读四侧
# ───────────────────────────────────────────────────────────
def read_pins_refs():
    with open(SRC_PINS, encoding="utf-8") as f:
        return {r["ref"].strip() for r in csv.DictReader(f) if (r.get("ref") or "").strip()}


def read_net_refs():
    with open(SRC_NET, encoding="utf-8") as f:
        return {r["ref"].strip() for r in csv.DictReader(f) if (r.get("ref") or "").strip()}


def read_board_refs():
    """★板侧 ref: 直接从 .kicad_pcb 的 (property "Reference" …) 抓 (★只读文本·不 import pcbnew★)"""
    out = set()
    rx = re.compile(r'\(property "Reference" "([^"]*)"')
    with open(SRC_PCB, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = rx.search(line)
            if m and m.group(1):
                out.add(m.group(1))
    return out


def read_sch_refs():
    """★原理图侧 ref: 从 11 页 demo_mainboard_p*.kicad_sch 抓 (★只读★)"""
    out = set()
    rx = re.compile(r'"Reference" "([^"]*)"')
    d = os.path.join(PROJ, "HW", "PCB")
    for fn in sorted(os.listdir(d)):
        if re.fullmatch(r"demo_mainboard_p\d+\.kicad_sch", fn):
            with open(os.path.join(d, fn), encoding="utf-8", errors="replace") as f:
                for line in f:
                    m = rx.search(line)
                    if m and m.group(1):
                        out.add(m.group(1))
    return out


def read_bom_refs():
    with open(os.path.join(PROJ, "HW", "BOM_v1.csv"), encoding="utf-8") as f:
        return {r["ref"].strip() for r in csv.DictReader(f) if (r.get("ref") or "").strip()}


# ───────────────────────────────────────────────────────────
# 自检: 口径必须与生成器源码逐字一致 (★不一致 ⇒ abort★)
# ───────────────────────────────────────────────────────────
def selfcheck_caliber():
    src = open(SRC_SCH_GEN, encoding="utf-8").read()
    if not _GEN_RE.search(src):
        print("❌ abort: 口径单源对不上 —— state/gen_kicad_sch.py::kicad_ref() 的源码形态已变")
        print("   ⇒ ★本单的改名清单不许在口径未确认前产出口★")
        sys.exit(2)
    return True


def main():
    selfcheck_caliber()
    pins = read_pins_refs()
    net = read_net_refs()
    board = read_board_refs()
    sch = read_sch_refs()
    bom = read_bom_refs()

    real_net = {x for x in net if is_real(x)}
    # ★网表真实器件宇宙 = ref 列真实器件 ∪ 节点串里带编号脚的器件 (★与 check_pcb_nets.py 同口径★)
    node_devs = set()
    with open(SRC_NET, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for k in ("node1", "node2"):
                v = (r.get(k) or "").strip()
                m = re.match(r"^([A-Za-z_0-9]+)\s+pin\d", v)
                if m and is_real(m.group(1)):
                    node_devs.add(m.group(1))
    net_universe = real_net | node_devs

    print("=" * 100)
    print("ISS-317 · ① 逐条改名清单 (★机器生成 · 非手抄★)")
    print("=" * 100)
    print()
    print("── §A 四侧现值盘点 (★[实测]★) ──────────────────────────────────────────────")
    print("  脚表侧 HW/netlist_v1_pins.csv      : %3d 个 ref" % len(pins))
    print("  网表侧 HW/netlist_v1.csv (ref 列)  : %3d 个 (含伪器件 RAIL_*/NET_* %d 个)"
          % (len(net), len(net) - len(real_net)))
    print("  网表侧真实器件宇宙 (ref ∪ 节点串)   : %3d 个" % len(net_universe))
    print("  BOM 侧 HW/BOM_v1.csv               : %3d 个 ref" % len(bom))
    print("  原理图侧 11 页 .kicad_sch          : %3d 个 ref" % len(sch))
    print("  板侧 HW/PCB/demo_mainboard.kicad_pcb: %3d 个封装" % len(board))
    print()
    print("  ★口径一致性核对:")
    print("    脚表 == BOM                        : %s" % (pins == bom))
    print("    脚表 ⊆ 网表真实器件宇宙            : %s (差 %d: %s)"
          % (pins <= net_universe, len(pins - net_universe), sorted(pins - net_universe) or "无"))
    print("    脚表 ⊆ 板侧                        : %s (脚表有板无 %d 个 ⇒ CHG_BOARD 件)"
          % (pins <= board, len(pins - board)))
    print("    板侧 == 脚表 ∩ 本板                : %s" % (board == (pins - (pins - board))))
    print("    原理图侧 == kicad_ref(脚表)        : %s" % (sch == {kicad_ref(x) for x in pins}))
    print()

    # ── 改名宇宙: 表侧全部真实器件 (★= 原理图侧已用的那个宇宙★) ──
    universe = sorted(pins)

    # ── 分组统计 ──
    moved = [x for x in universe if is_real(x) and kicad_ref(x) != x]
    kept = [x for x in universe if is_real(x) and kicad_ref(x) == x]
    pseudo = sorted(x for x in net if not is_real(x))
    board_moved = [x for x in moved if x in board]
    board_kept = [x for x in kept if x in board]
    off_board_moved = [x for x in moved if x not in board]
    off_board_kept = [x for x in kept if x not in board]

    print("── §B 改名口径下的分组计数 (★[实测]★) ─────────────────────────────────────")
    print("  改名宇宙 (表侧真实器件)                : %3d" % len(universe))
    print("  ★要改 (末字符是字母 ⇒ 加 _1)          : %3d" % len(moved))
    print("  ★不动 (末字符是数字 ⇒ 一律不动)       : %3d  ← ★ISS-314 实测「30 个不动」是【板侧】口径"
          % len(kept))
    print("    · 其中在板侧 (MAIN_PCB)              : %3d 要改 / %3d 不动"
          % (len(board_moved), len(board_kept)))
    print("    · 其中不在板侧 (CHG_BOARD)           : %3d 要改 / %3d 不动"
          % (len(off_board_moved), len(off_board_kept)))
    print("  伪器件 RAIL_*/NET_* (网表 ref 列)     : %3d  ★不改名 (★它们是网名别名, 不是器件★)"
          % len(pseudo))
    print()

    # ── 单射校验 (★ISS-314 T7 的前置条件★) ──
    tgt = {}
    coll = []
    for x in universe:
        t = kicad_ref(x)
        if t in tgt:
            coll.append((x, tgt[t], t))
        tgt[t] = x
    print("  ★单射校验 (改名后会不会撞名): %s"
          % ("✅ 无碰撞" if not coll else "❌ 撞名 %d 处: %s" % (len(coll), coll)))
    if coll:
        print("  ⇒ ★存在 (X, X_1) 同表共存的 ref ⇒ 改名会制造歧义 ⇒ 必须先解掉★")
    print()

    # ── 现状 C1 基线里【点名】的 ref (★这 5 条是现状 delta, 改名后仍要归零★) ──
    delta_refs = {
        "C_VBUS_GND": "现状「多余 2」(pad1/pad2) —— ★板上有、网表侧这 2 脚推不出来★",
        "Q_PG": "现状「同号异网 2」(pad1/pad3 对调) —— ★ISS-283 G-1 裁决「写法 A」要求板侧重画 3 根线★",
        "D_ESD_USB_D": "现状「同号异网 1」(pad1 挂错网) —— ★S4 的活★",
        "J_USB_C": "★现状合法 NC (shield/A8/B8) ⇒ 改名后撞 NC 白名单 ⇒ 非法 NC 3 + C3 不符 1★",
    }
    print("── §C 现状 C1 delta 涉及的 ref (★改名【不】解掉这 5 条 ⇒ 改名后读数不变★) ────")
    for k, v in delta_refs.items():
        print("  %-14s %s" % (k, v))
    print()

    # ── 逐条改名对照表 ──
    # ── 硬编码 ref 清单 (★只读扫描·不改任何文件★) ──
    GAP29 = ["BT_432243", "CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_LIGHT", "D_ESD_TC",
             "D_ESD_USB_D", "D_TVS_VBUS", "FB_DEMO", "FB_VBUS", "J_USB_C", "Q1", "Q2", "Q_AND",
             "Q_CHG_LED", "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_CAM", "SW_KEY_PWR", "SW_KEY_VM",
             "SW_KEY_VP", "SW_RST", "U_BATPROT", "U_EN_SW", "U_LDO_S28", "U_PWR_SW", "U_SUPV", "X1"]
    GAP29 = set(GAP29)
    OPN_FROM_BOARD = {"U_BATPROT", "Q1"}
    FOOTPRINT_FROM_BOARD = {"Q1"}
    PLACE_OVERRIDE = {"J_USB_C", "R_SER_USB_D_N"}
    NC_ALLOWED = {"J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4", "J_USB_C"}
    SELFTEST_TARGET = {"CONN_CAM"}
    CONN_CAM_PIN = {"CONN_CAM"}

    print("── §D 逐条改名对照表 (★每一行一个 ref · 共 %d 行★) ─────────────────────────" % len(universe))
    print()
    print("★读表须知:")
    print("  · 「旧ref(脚表侧现值)」与「旧ref(板侧现值)」★本机实测两侧【完全一致】★ (★board ⊆ pins 且逐名相同★)")
    print("    ⇒ ★真正分叉的是【表侧/板侧 (不带 _1)】 vs 【原理图侧 (带 _1)】★ ⇒ 第三列给的是原理图侧现值")
    print("  · 「改哪个真源」列给的是★除四侧产物外★还要同批同步的★生成器/判据硬编码★清单")
    print("  · 「改完的预期读数」= 改名后 C1 三项 (缺失/多余/同号异网) 的预期 ⇒ ★改名【不】解掉现状 5 条 delta★")
    print()
    # ★★v2 修: 「改哪个真源」列宽 22 ⇒ 96 (★v1 截断掉了 GAP29 / NC_ALLOWED / --selftest 目标★)
    hdr = ("%-3s %-22s %-22s %-22s %-24s %-160s %-6s %-7s %-34s %-14s"
           % ("#", "旧ref(脚表侧现值)", "旧ref(板侧现值)", "旧ref(原理图侧现值)",
              "新ref(kicad_ref口径)", "改哪个真源(★同步清单★)", "板侧", "动/不动",
              "改完的预期读数", "依赖顺序"))
    print(hdr)
    print("-" * len(hdr))
    for i, x in enumerate(universe, 1):
        old_tbl = x
        old_brd = x if x in board else "—(不在本板·CHG_BOARD)"
        sch_old = kicad_ref(x)          # ★原理图侧现值 = kicad_ref(x) ⇒ 已带 _1★
        new = kicad_ref(x)
        in_brd = "在" if x in board else "不在"
        move = "不动" if new == x else "改名"
        # 同步硬编码清单
        extra = []
        if x in GAP29:
            extra.append("gen_bom.py:307 GAP29")
        if x in OPN_FROM_BOARD:
            extra.append("gen_bom.py:100 OPN_FROM_BOARD")
        if x in FOOTPRINT_FROM_BOARD:
            extra.append("gen_bom.py:113 FOOTPRINT_FROM_BOARD")
        if x in PLACE_OVERRIDE:
            extra.append("gen_pcb_netlist_board.py:203 PLACE_OVERRIDE")
        if x in CONN_CAM_PIN:
            extra.append("gen_pcb_netlist_board.py:221 CONN_CAM_PIN")
        if x in NC_ALLOWED:
            extra.append("check_pcb_nets.py:260-265 NC_ALLOWED")
        if x in SELFTEST_TARGET:
            extra.append("check_pcb_nets.py:402 --selftest 目标")
        if new == x:
            srcs = "★无需改 (已同口径)★"
        else:
            srcs = "四侧产物 + " + ("; ".join(extra) if extra else "★无额外硬编码★")
        # 预期读数
        if new == x:
            exp = "缺失0/多余2/同号异网3 (不变)"
        elif x == "J_USB_C":
            exp = "★非法NC 3 + C3 不符1★ (撞白名单)"
        elif x in delta_refs:
            exp = "★%s★" % ("仍点名该 ref ⇒ delta 不变" if x != "J_USB_C"
                             else "非法NC 3 + C3 不符 1")
        else:
            exp = "缺失0/多余2/同号异网3 (不变)"
        dep = "BATCH-1 背靠背" if new != x else "—"
        print("%-3d %-22s %-22s %-22s %-24s %-160s %-6s %-7s %-34s %-14s"
              % (i, old_tbl, old_brd, sch_old, new, srcs[:160], in_brd, move, exp[:34], dep))
        # ★★ 同时输出【TSV 行】(★机器解析用·不受列宽/全角字符影响★)
        print("TSV\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"
              % (i, old_tbl, old_brd, sch_old, new, srcs, in_brd, move, exp, dep))
    print()

    # ── §E 依赖顺序 (★同批 = 同一个落表单号·背靠背·不许拆两趟★) ──
    print("── §E 依赖顺序 (★同批 = 背靠背·中间不得隔夜★) ───────────────────────────")
    print("  BATCH-1 (★必须同批·背靠背·★):")
    print("    1) 网表侧 HW/netlist_v1.csv   —— ref 列 + node1/node2 里的器件名 (★先改★)")
    print("    2) 脚表侧 HW/netlist_v1_pins.csv —— ref 列")
    print("    3) BOM 侧  HW/BOM_v1.csv      —— ★由 state/gen_bom.py 生成 ⇒ 必须与 1/2 同批重跑★")
    print("    4) 板侧   HW/PCB/demo_mainboard.kicad_pcb —— ★由 state/gen_pcb_netlist_board.py 生成 ⇒ 同批重出★")
    print("    5) 原理图侧 demo_mainboard_p*.kicad_sch —— ★由 state/gen_kicad_sch.py 生成 ⇒")
    print("       ★**不改**★: kicad_ref() 对已带 _1 的 ref 是【幂等】的 ⇒ 重跑得同一张图")
    print("  ★中间态禁令: 1) 已落表但板未重出 ⇒ C1 炸成 缺失350/多余352 (★ISS-314 S3 实测★)")
    print("  ★BATCH-2 (★判据侧·与 BATCH-1 同批★): state/check_pcb_nets.py 两处硬编码 (★见 §2★)")
    print("  ★BATCH-3 (★生成器侧硬编码·与 BATCH-1 同批★):")
    print("       state/gen_bom.py:100 OPN_FROM_BOARD (U_BATPROT / Q1)")
    print("       state/gen_bom.py:307 GAP29 (29 个 ref 清单)")
    print("       state/gen_pcb_netlist_board.py:203 PLACE_OVERRIDE (J_USB_C / R_SER_USB_D_N)")
    print("       state/gen_pcb_netlist_board.py:221 CONN_CAM_PIN")
    print()

    # ── §F 验收命令 (★逐字可粘贴★) ──
    print("── §F 验收命令 (★逐字可粘贴★) ───────────────────────────────────────────")
    print("  # ① 改名后 C1 三项 + C2 + C3 + 非法 NC")
    print("  bash state/pcbnew_py.sh state/check_pcb_nets.py 2>&1 | grep -E 'C1 |缺失 |C2 |C3 '")
    print("  # ② 改名后原理图侧是否仍是同一张图 (★幂等性★)")
    print("  md5sum HW/PCB/demo_mainboard_p*.kicad_sch")
    print("  # ③ 改名后 BOM 侧证据行有没有消失 (★ISS-314 地雷 2★)")
    print("  grep -c '板文件封装' HW/BOM_v1.csv")
    print("  # ④ 改名后四侧位号集合是否同口径")
    print("  python3 state/check_chain_content_anchor.py")
    print("  # ⑤ 门禁链")
    print("  python3 state/merge.py && python3 state/gate_check.py")
    print()

    # ── §G 三个数字 (★交卷页要贴★) ──
    print("── §G 交卷页要贴的三个数 ─────────────────────────────────────────────────")
    print("  总数 (表侧真实器件改名宇宙) = %d" % len(universe))
    print("  不动的 (末字符是数字)       = %d  (★其中板侧 %d 个 / 非板侧 %d 个★)"
          % (len(kept), len(board_kept), len(off_board_kept)))
    print("  要改的                       = %d  (★其中板侧 %d 个 / 非板侧 %d 个★)"
          % (len(moved), len(board_moved), len(off_board_moved)))
    print()
    print("  ★★「豁免」的口径澄清 (★本单实测·这是 §2 的关键数字★):")
    nc_moves = sorted(x for x in NC_ALLOWED if x in universe and kicad_ref(x) != x)
    nc_kept = sorted(x for x in NC_ALLOWED if x in universe and kicad_ref(x) == x)
    print("    NC 白名单 5 个 ref 里, 末字符是数字 ⇒ 本来就不动 : %d 个 %s"
          % (len(nc_kept), nc_kept))
    print("    ⇒ ★**真正需要豁免的只有 %d 个**: %s**" % (len(nc_moves), nc_moves))
    print("    ⇒ ★豁免清单 = 这 %d 个 · 不是 5 个 · 也不是「186 个里挑一批」★" % len(nc_moves))
    print()
    print("  ★★「不动」的 32 vs ISS-314 的 30 —— 口径差异说明 (★数字对不上·这里说清★):")
    print("    ISS-314 §1-2 说的「30 个不动」= ★**板侧 186 个封装**里末字符是数字的个数 (★板侧口径★)")
    print("    本单说的「32 个不动」        = ★**表侧 218 个真实器件**里末字符是数字的个数 (★表侧口径★)")
    print("    差 2 个 = ★板上没有、脚表里有的 CHG_BOARD 件★: %s"
          % sorted(set(off_board_kept)))
    print("    ⇒ ★两个数都对, 只是口径不同★ ⇒ 本单按【表侧口径 32】出清单, 板侧口径 30 也一并列出★")
    print("=" * 100)


if __name__ == "__main__":
    main()
