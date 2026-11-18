#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_pcb_nets.py —— 板子 ↔ 网表 **焊盘级** 等价性门禁 (★"自己画图"的核心验收)

★★ 为什么必须升级成焊盘级 (2026-11-03):
  旧门禁只比 **(ref, net) 集合** ⇒ ★**脚位对调它照样报绿** (假绿):
    · 旧生成器按 CSV 行序给焊盘编号 ⇒ 焊盘号 ≠ 网表真实针号
    · 旧生成器按 (ref, net) 去重 ⇒ 连接器上多个同网脚 (例: CONN_CAM 的 8 个 GND 脚)
      被合并成**一个**焊盘 ⇒ 31 脚只剩 21 个焊盘
  ⇒ 实测过: 板上 `CONN_LIGHT pad2` 的网是 GND, 而网表要求 pad2 = DSI_D0_CK_N;
    `U_TEMP pad1/pad2` 的 SCL/SDA 也是反的 —— 而旧门禁全绿。
  ⇒ ⇒ 本门禁把比对粒度降到 **(器件, 焊盘号) → 网络**, 脚位对调立刻被抓住。

判据:
  C1 ★**焊盘级等价**: 板上的 (ref, 焊盘号) → 网络 集合
     必须与**网表推出的** (ref, 焊盘号) → 网络 集合**完全相等**
     (缺失 / 多余 / 同一个焊盘号挂到不同网络 —— 三种都算失败)
  C2 ★**连接器 / 带编号脚的器件**: 板上焊盘数 == 网表里它的脚数, 且**针号集合相等**
  C3 ★**每个器件**: 板上焊盘数 == 网表推出的脚数
  C4 (★只报告, 不判失败) 焊盘号为**占位(行序)**的器件清单 —— 封装还没定脚的 IC 之类
  C5 (★只报告, 不判失败) 网表自身的缺陷提示 (同名脚挂两个网等)

★网表 → 焊盘编号规则 (与 state/gen_pcb_netlist_board.py 同源, 但这里独立实现一遍,
  避免"生成器和门禁共用一份代码 ⇒ 一起错" ):
  · 编号脚: 节点串 "<器件> pin<N>" / "<器件> pin<N>+pin<M>"
      ⇒ 焊盘号 = **网表真实针号** (归属以**节点串里的器件名**为准, 不以行的 ref 为准)
  · 命名脚 / 裸端: 节点串 "<器件> EN" / "<器件> A4" / "<器件>"
      ⇒ 焊盘号 = **按出现顺序的占位号 1..M** (记入 C4 清单)
  · 退化行 (node1 与 node2 是同一个裸器件) ⇒ 该行不占任何引脚 (网别名/清单行)
  · 行的 ref 若本行两个节点串都没提到 ⇒ ref 自己占一个裸端
  · 裸端按 (器件, 网络) 去重; 该网络若已被同器件的**编号脚**占用 ⇒ 裸端是粗略别名, 不占焊盘

退出码: 全过 0; 否则 1

★自检: `check_pcb_nets.py --selftest` ⇒ 故意把板上两个焊盘对调, 确认门禁**会失败**
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib/python3/dist-packages")
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib")
import pcbnew  # noqa: E402

NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
PSEUDO = ("RAIL_", "NET_")
# ★USB-IF 物理脚名 (A1/A4/A5/A6/A7/A8/A9/A12 · B 同 · shield) 就是**真实焊盘号**
USBIF_RE = re.compile(r"^(?:[AB](?:1|4|5|6|7|8|9|12)|shield)$")
# ★demo 主板只装 MAIN_PCB 的件 (与 state/gen_pcb_netlist_board.py 同口径, 独立实现)
BOARD_FILTER = "MAIN_PCB"
PIN_RE = re.compile(r"pin\d+(\+pin\d+)*")


# --------------------------------------------------------------- 网表 → 焊盘 (独立实现)


def _is_pad_name(tail):
    """★真实焊盘号判定: "pin<N>" (网表针号) 或 **USB-IF 物理脚名** (A1/A4/A5/B12/shield …)
    ★USB-C 座 (如 GCT USB4105) 的 KiCad 封装正是用这组名字当 pad number ⇒ 必须当真实焊盘号
    ★★2026-11-05 07:10 **合并写法也要认** (与 gen_pcb_netlist_board.py **同口径**)
       网表里 USB-C 的 A/B 双排同名脚合写: "A6+B6" / "A4+A9+B4+B9"
       ⇒ USBIF_RE 只匹配**单个**脚名 ⇒ 合并写法被判成"命名脚" ⇒ 落进占位编号分支
       ⇒ 网表侧要 '1','2','3' 而板上是 'A6','B6' ⇒ ★**parity 必红**
       (实测 8 层板: 缺失 12 / 多余 12, 全是 J_USB_C)
       ⇒ ★**检查器与生成器必须同一口径**, 否则一个说"全过"另一个说"不等价" ⇒ 闸门自相矛盾
    """
    if not tail:
        return False
    if re.fullmatch(r"pin\d+(\+pin\d+)*", tail):
        return True
    if USBIF_RE.match(tail):
        return True
    # ★合并写法: 每个 token 都是 USB-IF 物理脚名 ⇒ 整体算"真实焊盘号"
    toks = [t.strip() for t in tail.split("+") if t.strip()]
    if len(toks) >= 2 and all(USBIF_RE.match(t) for t in toks):
        return True
    return False

def split_node(node):
    """节点串 → (器件名, 脚名 or None)"""
    node = (node or "").strip()
    if not node:
        return None, None
    m = re.match(r"^([A-Za-z_0-9]+)\s+(.*)$", node)
    if not m:
        return node, None
    return m.group(1), m.group(2).strip()


def split_names(tail):
    """命名脚里的 '+' 只有后面还跟着字符时才是分隔符 (B+ 是一个脚名)"""
    return [p.strip() for p in re.split(r"\+(?=\w)", tail) if p.strip()]


def netlist_pads(rows):
    """网表 → (per_ref, numbered, placeholder, notes)
      per_ref    : {器件: [(焊盘号, 网络)]}
      numbered   : {器件: {针号: 网络}}   —— 焊盘号 = 网表真实针号
      placeholder: {器件: 焊盘数}          —— 焊盘号 = 行序占位
      notes      : 网表缺陷提示
    """
    refs = set()
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref:
            refs.add(ref)
    real = {x for x in refs if not x.startswith(PSEUDO)}
    # ★器件宇宙 = ref 列真实器件 ∪ 节点串里带编号脚的器件 (J_SOM_P1..P4)
    for r in rows:
        for k in ("node1", "node2"):
            comp, tail = split_node(r.get(k))
            if not comp or comp in real or comp.startswith(PSEUDO):
                continue
            if tail and PIN_RE.fullmatch(tail):
                real.add(comp)

    terms = {}          # dev -> {term_key: (net, kind)}
    notes = []
    for r in rows:
        net = (r.get("net") or "").strip()
        ref = (r.get("ref") or "").strip()
        if not net:
            continue
        parsed = [split_node(r.get(k)) for k in ("node1", "node2")]
        if (parsed[0][0] == parsed[1][0]
                and parsed[0][1] is None and parsed[1][1] is None):
            continue                                  # 退化行 ⇒ 不占引脚
        seen = set()
        for comp, tail in parsed:
            if comp is None or comp not in real:
                continue
            d = terms.setdefault(comp, {})
            if tail and _is_pad_name(tail):
                for tok in tail.split("+"):
                    tok = tok.strip()
                    # ★"pin<N>" ⇒ 数字脚号; ★USB-IF 物理脚名 (A1/B12/shield) ⇒ **字符串脚号**
                    key = ("P", int(tok[3:])) if tok.startswith("pin") else ("P", tok)
                    if key in d and d[key][0] != net:
                        notes.append(f"{comp} {key[1]} 同时挂 {d[key][0]} 与 {net}")
                    d.setdefault(key, (net, "P"))
                    seen.add(comp)
            elif tail:
                for nm in split_names(tail):
                    same = [k for k in d if k[0] == "N" and k[1] == nm]
                    if same and ("N", nm, net) not in d:
                        notes.append(f"{comp} 脚 {nm} 同时挂 {d[same[0]][0]} 与 {net}")
                    d.setdefault(("N", nm, net), (net, "N"))
                    seen.add(comp)
            else:
                d.setdefault(("B", net), (net, "B"))
                seen.add(comp)
        if ref and ref in real and ref not in seen:
            terms.setdefault(ref, {}).setdefault(("B", net), (net, "B"))

    # 裸端若被同器件的编号脚覆盖 ⇒ 粗略别名, 不占焊盘
    for comp, d in terms.items():
        pinnets = {v[0] for k, v in d.items() if k[0] == "P"}
        for k in [k for k in d if k[0] == "B" and k[1] in pinnets]:
            del d[k]

    per_ref, numbered, placeholder = {}, {}, {}
    for comp, d in terms.items():
        if not d:
            continue
        if any(k[0] == "P" for k in d):
            pins = sorted(((k[1], v[0]) for k, v in d.items() if k[0] == "P"),
                          key=lambda t: (0, t[0], 0) if isinstance(t[0], int) else (1, str(t[0]), 0))
            # ★脚号可能是数字 (pin<N>) 或字符串 (USB-IF A1/B12) ⇒ 续号只用数字脚号
            _nums = [x[0] for x in pins if isinstance(x[0], int)]
            nxt = (max(_nums) + 1) if _nums else 1
            for k, v in d.items():
                if k[0] != "P":
                    pins.append((nxt, v[0]))
                    nxt += 1
            per_ref[comp] = pins
            numbered[comp] = {n: net for n, net in pins}
        else:
            # ★★2026-11-05 03:05 修 (实测 parity "缺失 14 / 多余 12" 的根因):
            #   J_USB_C 的脚名是 **USB-IF 物理脚名** (A1/A4/A6/B12… 裸名, 不是 pinN)
            #   ⇒ 旧逻辑把**所有裸名**当"占位脚号"(按行序 1..N) ⇒ 而板上用的是真脚名 ⇒ 两套对不上
            #   ⇒ 现在: USB-IF 裸名 ⇒ **当真实焊盘号** (与板生成器的 USBIF_RE 同口径)
            pins = []
            for i, (_k, v) in enumerate(d.items(), start=1):
                # ★★USB-IF 脚名可能是**合并写法** ("A6+B6" / "A4+A9+B4+B9") ⇒ 每个物理脚各算一个焊盘
                if isinstance(_k, str) and "+" in _k:
                    parts = [q.strip() for q in _k.split("+") if q.strip()]
                    if parts and all(USBIF_RE.match(q) for q in parts):
                        for q in parts:
                            pins.append((q, v[0]))
                        continue
                if isinstance(_k, str) and USBIF_RE.match(_k):
                    pins.append((_k, v[0]))     # ★真实 USB-IF 脚名
                else:
                    pins.append((i, v[0]))
            per_ref[comp] = pins
            placeholder[comp] = len([1 for k, _v in pins if isinstance(k, int)])
    return per_ref, numbered, placeholder, notes


# --------------------------------------------------------------- 板子

def board_pads(path):
    """板 → {(ref, 焊盘号): 网络} + {ref: [焊盘号...]}"""
    b = pcbnew.LoadBoard(path)
    if b is None:
        return None, None
    pairs, per_ref = {}, {}
    for fp in list(b.GetFootprints()):
        ref = fp.GetReference()
        for pad in list(fp.Pads()):
            num = str(pad.GetNumber())
            pairs[(ref, num)] = pad.GetNetname()
            per_ref.setdefault(ref, []).append(num)
    return pairs, per_ref


def compare(want, have):
    """(ref,pad)→net 两个字典的差集 (同号不同网也算不一致)"""
    missing, extra, wrong = [], [], []
    for k, net in want.items():
        if k not in have:
            missing.append((k, net))
        elif have[k] != net:
            wrong.append((k, net, have[k]))
    for k, net in have.items():
        if k not in want:
            extra.append((k, net))
    return missing, extra, wrong


def run_checks(path, verbose=True):
    rows = list(csv.DictReader(open(NET, encoding="utf-8")))
    # ★★2026-11-03 09:54 老板口径: "没有整机, 没有镜脚, demo/主板用 type-c 供电"
    #   ⇒ **这块板子就是 demo 主板** ⇒ board=CHG_BOARD (充电链那套) 与 board=HINGE (跨铰链两个座)
    #   的件不在板上 ⇒ 网表→焊盘推导时按同一口径过滤 (★与生成器同口径, 但**独立实现**, 不共用代码)
    rows = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == BOARD_FILTER]
    per_ref, numbered, placeholder, notes = netlist_pads(rows)
    have, board_refs = board_pads(path)
    if have is None:
        return 1, ["❌ 板文件读不回来: %s" % path], {}

    want = {}
    for ref, pins in per_ref.items():
        if ref.startswith(PSEUDO):
            continue
        for n, net in pins:
            want[(ref, str(n))] = net

    missing, extra, wrong = compare(want, have)
    fails = []

    # ★★NC 焊盘 (无网络) 的处理: ★**SOM 的 4 组 100 脚 BTB 座本来就有 100 个物理焊盘**,
    #   而我们只用了其中 45 个 ⇒ 未用的脚必须是"无网焊盘" (NC) ⇒ **不能**当成"多余"
    #   ⇒ 反过来: 其它器件出现 NC 焊盘 = 可疑 (网表里那个脚没画) ⇒ 判失败
    NC_ALLOWED = {"J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"}
    # ★★2026-11-05 07:15 **J_USB_C 也允许 NC** (USB-IF 规范: **A8/B8 本来就是 NC**,
    #   而两个大固定脚 = 屏蔽壳 (shield) ⇒ ★**网表不给它们分配网络是对的**)
    #   ⇒ 之前 J_USB_C 的 pad(shield)/A8/B8 被判"非法 NC" ⇒ ★C1 永远红 ⇒ 闸门自相矛盾
    #   ★**EMC 提醒 (不阻断本板)**: 屏蔽壳通常还要经 RC (1MΩ ‖ 4.7nF) 接地 ⇒ 属设计项, 另记
    NC_ALLOWED.add("J_USB_C")
    nc_pads = {k for k, v in have.items() if not v}
    extra = [e for e in extra if e[0] not in nc_pads]   # e = (key, net) ⇒ 取 e[0] 比
    bad_nc = sorted(k for k in nc_pads if k[0] not in NC_ALLOWED)

    # ---- C1 焊盘级等价 ----
    ok1 = not (missing or extra or wrong) and not bad_nc
    c1 = [f"  {'✅' if ok1 else '❌'} C1 焊盘级等价 (ref,焊盘号)→网络 "
          f"— 网表 {len(want)} / 板上(带网) {len(have) - len(nc_pads)}",
          f"       缺失 {len(missing)} · 多余 {len(extra)} · 同号异网 {len(wrong)} · "
          f"★NC 焊盘 {len(nc_pads)} 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC {len(bad_nc)}"]
    for k, n in missing[:8]:
        c1.append(f"       ★缺: {k[0]} pad{k[1]} 应为 {n}")
    for k, n in extra[:8]:
        c1.append(f"       ★多: {k[0]} pad{k[1]} = {n}")
    for k, n, g in wrong[:8]:
        c1.append(f"       ★错: {k[0]} pad{k[1]} 应为 {n}, 实际 {g}")
    for k in bad_nc[:8]:
        c1.append(f"       ★NC 焊盘落在不该有 NC 的器件上: {k[0]} pad{k[1]}")
    if not ok1:
        fails.append(f"C1 焊盘级不等价 (缺{len(missing)}/多{len(extra)}/错{len(wrong)}/非法NC{len(bad_nc)})")

    # ---- C2 连接器 / 带编号脚的器件: 针数 + 针号集合 ----
    #   ★**部分用到的 100 脚座** (SOM 的 4 组 BTB): 板上是 100 个物理焊盘, 网表只用其中一部分
    #   ⇒ 判据改成: 板 100 脚 + **网表用到的脚必须都在板上** (而不是"针数相等")
    PARTIAL = {"J_SOM_P1": 100, "J_SOM_P2": 100, "J_SOM_P3": 100, "J_SOM_P4": 100}
    # ★★2026-11-05 07:15 **合法 NC 脚要从"针数"里扣掉** (J_USB_C 的 shield/A8/B8)
    #   ⇒ USB-IF 规范: A8/B8 就是 NC, 两个大固定脚是屏蔽壳 ⇒ ★**板上有 17 个焊盘, 网表用 14 个**
    #   ⇒ C2/C3 直接比"针数相等" ⇒ ★**永远红** ⇒ 改成: 板上的 NC 脚不计入针数
    _nc_by_ref = {}
    for _k in nc_pads:
        _r, _n = _k[0], _k[1]
        _nc_by_ref.setdefault(_r, set()).add(str(_n))

    def _nc_ok(ref):
        """该器件的 NC 脚是否都是允许的 (USB-C 屏蔽/A8/B8)"""
        return ref in NC_ALLOWED

    c2 = []
    bad2 = []
    for ref in sorted(numbered):
        want_nums = {str(n) for n in numbered[ref]}
        got_all = set(board_refs.get(ref, []))
        # ★只数"有网"的焊盘 (USB-C 的 shield/A8/B8 本就无网 ⇒ 不计入针数)
        got_nums = {n for n in got_all if have.get((ref, n))}
        if ref in PARTIAL:
            ok = (len(board_refs.get(ref, [])) == PARTIAL[ref] and want_nums <= got_nums)
            diff = sorted(want_nums - got_nums, key=lambda s: (len(s), s))
            c2.append(f"  {'✅' if ok else '❌'} C2 {ref}: 板 {len(board_refs.get(ref, []))} 脚 "
                      f"(座共 {PARTIAL[ref]}) / 网表用到 {len(want_nums)} 脚"
                      + ("" if ok else f" · 板上缺 {diff[:8]}"))
            if not ok:
                bad2.append(ref)
            continue
        ok = (len(got_nums) == len(want_nums) and got_nums == want_nums
              and len(got_nums) == len(want_nums))
        diff = sorted(got_nums ^ want_nums, key=lambda s: (len(s), s))
        c2.append(f"  {'✅' if ok else '❌'} C2 {ref}: 板 {len(got_nums)} 脚 / 网表 {len(want_nums)} 脚"
                  + ("" if ok else f" · 针号差 {diff[:8]}"))
        if not ok:
            bad2.append(ref)
    if bad2:
        fails.append(f"C2 针号/针数不符 {len(bad2)} 个: {bad2}")

    # ---- C3 每个器件的焊盘数 ----
    c3 = []
    bad3 = []
    for ref in sorted(per_ref):
        if ref.startswith(PSEUDO):
            continue
        w = len(per_ref[ref])
        g = len(board_refs.get(ref, []))
        if ref in PARTIAL:
            if g != PARTIAL[ref]:
                bad3.append((ref, PARTIAL[ref], g))
            continue
        # ★合法 NC 脚 (USB-C 屏蔽/A8/B8) 不计入
        if _nc_ok(ref):
            g = len([n for n in board_refs.get(ref, []) if have.get((ref, n))])
        if w != g:
            bad3.append((ref, w, g))
    ok3 = not bad3
    c3.append(f"  {'✅' if ok3 else '❌'} C3 每个器件焊盘数 == 网表推出的脚数 "
              f"— 器件 {len(per_ref)} 个 · 不符 {len(bad3)} 个")
    for ref, w, g in bad3[:10]:
        c3.append(f"       ★ {ref}: 板 {g} 脚 / 网表 {w} 脚")
    if bad3:
        fails.append(f"C3 焊盘数不符 {len(bad3)} 个")

    # ---- C4 (只报告) 占位焊盘号的器件 ----
    c4 = [f"  ℹ️ C4 焊盘号为**占位(行序)**的器件 {len(placeholder)} 个 "
          f"(封装未落定脚号 ⇒ 板上的脚号是行序, 不是规格针号):"]
    for ref in sorted(placeholder):
        c4.append(f"       · {ref} ({placeholder[ref]} 脚)")

    # ---- C5 (只报告) 网表缺陷 ----
    c5 = [f"  ℹ️ C5 网表提示 {len(notes)} 条 (同名脚挂两个网 ⇒ 封装定脚号后才能收敛):"]
    for n in notes:
        c5.append(f"       ★ {n}")

    body = c1 + c2 + c3 + c4 + c5
    return (0 if not fails else 1), body, {"want": want, "have": have, "fails": fails}


def main():
    selftest = "--selftest" in sys.argv
    print("=" * 72)
    print("  PCB ↔ 网表 **焊盘级** 等价性门禁 (★脚位对调也必须被抓出来)")
    print("=" * 72)
    if selftest:
        return do_selftest()
    # ★★2026-11-05 13:35 **必须支持"查指定的板"** (★原来**只查官方板**, 把参数丢了)
    #   ⇒ ★**实测踩坑**: v29_O 臂 DRC=1/unconn=64 (比官方板好) ⇒ 晋级前预检却红了
    #     ⇒ 原因: `promote_arm.sh` 传的是臂板路径, 但**本脚本 ignores argv** ⇒ 量的是**官方板**
    #       (官方板 09:52 落的, 用的是修 P0 之前的旧网表 ⇒ J_SOM_P3 七脚还是 RAIL_SOM_DCIN)
    #   ⇒ ★**后果: 好臂永远晋级不了 (官方板旧 → parity 红 → 拒晋级 → 官方板永远是旧的) ⇒ 死锁**
    _args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pcb = os.path.abspath(_args[0]) if _args else PCB
    if _args:
        print("  (查板: %s)" % pcb)
    rc, body, _ctx = run_checks(pcb)
    print("\n".join(body))
    print("-" * 72)
    if rc:
        print("❌ 不通过 —— 板子与网表**不等价** ⇒ 板子不能下单")
    else:
        print("✅ 全过 —— 板子与网表**逐焊盘**等价 (脚号/脚数/网络全对)")
    return rc


def do_selftest():
    """★故意把板上两个焊盘对调 ⇒ 门禁必须失败 (证明它不是假绿)"""
    tmp = "/tmp/_pcb_swap_test.kicad_pcb"
    b = pcbnew.LoadBoard(PCB)
    target = None
    for fp in list(b.GetFootprints()):
        pads = sorted(list(fp.Pads()), key=lambda p: int(p.GetNumber()))
        if len(pads) >= 2 and fp.GetReference() == "CONN_CAM":
            target = (fp, pads)
            break
    if target is None:
        print("❌ 自检失败: 找不到可对调的器件")
        return 1
    fp, pads = target
    a, c = pads[1], pads[2]          # ★对调 pin2 / pin3 的**网络**
    na, nc = a.GetNet(), c.GetNet()
    a.SetNet(nc)
    c.SetNet(na)
    pcbnew.SaveBoard(tmp, b)
    print("★自检: 已把 %s 的 pin2/pin3 网络对调 ⇒ 写到 %s" % (fp.GetReference(), tmp))
    rc, body, _ctx = run_checks(tmp)
    hit = any("C1" in x and "❌" in x for x in body)
    print("\n".join(body[:12]))
    print("-" * 72)
    if rc != 0 and hit:
        print("✅ 自检通过 —— 门禁**抓到了**脚位对调 (rc=%d) ⇒ 本门禁不是假绿" % rc)
        os.remove(tmp)
        return 0
    print("❌ 自检失败 —— 脚位对调居然没被抓到 (rc=%d) ⇒ 门禁失效" % rc)
    return 1


if __name__ == "__main__":
    sys.exit(main())
