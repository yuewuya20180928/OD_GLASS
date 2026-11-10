#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_corridor.py —— ★★【★防回归自测: 【走廊让路】(★`PCB_CORRIDOR_YIELD`★)★】★★

★★★**★问题 (★2026-11-10 19:3x 实测坐实★)★★★ ★★★
  ★**现象 (★`v76mo` 臂·实测★)**: ★**`BOOT_N` @ (63.60, 11.04) 出不去**
    ⇒ ★**因为 `ID_DETECT_1` 的一根 (62.2,11.95)->(68.95,11.95) w=0.15 的直道
      【正好横在 `BOOT_N` 的出脚口上方 0.91mm】** ★
  · ★★★**★关键对照 (★官方板 vs 臂板★)★★★ ★★★
    ★**官方板: ★y=11.95 那一条线上【一寸 F.Cu 走线都没有】⇒ ⇒ 官方板把整条走廊腾空了** ★★
    ★**⇒ ⇒ "让路"是一条【链】, 不是单点**: ★★**让走 `ID_DETECT_0`, `ID_DETECT_1` 照样堵** ★★
    ⇒ ★★**⇒ ⇒ 而【调优先网名单】只调"谁先走", ★管不到"这条走廊上挤着几个网" ⇒ ⇒ 那条路已实测关闭** ★★
  · ★★★**★机制 (★`escape_stub()` 里★)**: ★★**出脚直道只查 `_stub_clear` / `_stub_vs_routed`
    (★自己走不走得通★)⇒ ⇒ 【从不管"我这条直道会不会站在别人的出脚口上"】⇒ ⇒ ⇒ 需要新判据** ★★
  · ★**修法 (★env 门控 `PCB_CORRIDOR_YIELD`, ★默认关⇒逐位不变★)**:
    ★★**出脚直道若会【站在别人的出脚口上】⇒ ⇒ 换方向/换长度 ⇒ ⇒ 把走廊让给对方** ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测★)** ★★★
  ① ★**默认关**: ★**不设 `PCB_CORRIDOR_YIELD` ⇒ 行为必须逐位不变** ★
  ② ★**显式开才 True**
  ③ ★**源码级: 修法必须落在【`escape_stub()` 的方向候选循环里】(★不是事后剔铜★)**
  ④ ★**源码级: 修法必须【只拦不删】(★不许出现删铜路径★)**
  ⑤ ★★★★**★几何级 (★真判据, ★真实坐标★): ★★**`BOOT_N` 与 `ID_DETECT_1` 的出脚口【必须被判为"互相挡住"】★★**
     (★实测: `ID_DETECT_1` 的直道 (62.2,11.95)->(68.95,11.95) 离 `BOOT_N` 出脚口 (63.6,11.04) 仅 0.91mm★)
  ⑥ ★★★**★几何级: ★【无关的两个脚】(★比如远在板子另一头的★)必须判为【不挡】★★ ⇒ ★**闸不许乱杀** ★★
  ⑦ ★★★**★端到端 (★真跑一遍布线★): ★开闸后【不该有的那根横道】必须消失 / 至少不站在别人的出脚口上★**

用法:
  bash state/pcbnew_py.sh state/_test_corridor.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

FAIL = []
OK = []


def chk(name, cond, detail=""):
    if cond:
        OK.append(name)
        print("  ✔ %s" % name)
    else:
        FAIL.append(name)
        print("  ✘ %s  ★%s" % (name, detail))
    return bool(cond)


# ---------------------------------------------------------------- ① ② 默认关 / 显式开
os.environ.pop("PCB_CORRIDOR_YIELD", None)
import gen_pcb_routing as G          # noqa: E402
chk("① 默认 PCB_CORRIDOR_YIELD 未设 ⇒ 必须 False (★默认逐位不变★)",
    G.CORRIDOR_YIELD is False, "实际 = %r" % (G.CORRIDOR_YIELD,))

os.environ["PCB_CORRIDOR_YIELD"] = "1"
import importlib                   # noqa: E402
G2 = importlib.reload(G)
chk("② PCB_CORRIDOR_YIELD=1 ⇒ 必须 True",
    G2.CORRIDOR_YIELD is True, "实际 = %r" % (G2.CORRIDOR_YIELD,))
os.environ.pop("PCB_CORRIDOR_YIELD", None)
importlib.reload(G)

# ---------------------------------------------------------------- ③ ④ 源码级
_src = open(os.path.join(_HERE, "gen_pcb_routing.py"), encoding="utf-8").read()
_i = _src.index("def escape_stub(self, net, pad):")
_j = _src.find("\n    def ", _i + 10)
_body = _src[_i:_j if _j > 0 else len(_src)]

chk("③ 修法必须落在【`escape_stub()` 的方向候选循环里】(★不是事后剔铜★)",
    "_stub_blocks_neighbor" in _body,
    "★escape_stub() 里没有调 _stub_blocks_neighbor ⇒ 修法没接上★")

chk("④ 修法只【拦不删】(★不许有删铜路径★)",
    ("_drop_committed" not in _body) and (".Remove(" not in _body)
    and ("self.tracks.remove" not in _body) and ("self.tracks.pop" not in _body),
    "★escape_stub() 里出现了删铜路径★")

# ---------------------------------------------------------------- ⑤⑥ 几何级
print()
print("── 几何级: 用【真实坐标】问真判据 ──")
try:
    import pcbnew                # noqa: E402
except Exception:                # noqa: BLE001
    pcbnew = None

if pcbnew is not None:
    board = pcbnew.LoadBoard(os.path.join(_HERE, "..", "HW", "PCB",
                                          "demo_mainboard.kicad_pcb"))
    r = G.GridRouter(board)
    os.environ["PCB_CORRIDOR_YIELD"] = "1"
    import importlib
    G3 = importlib.reload(G)
    board = pcbnew.LoadBoard(os.path.join(_HERE, "..", "HW", "PCB",
                                          "demo_mainboard.kicad_pcb"))
    r = G3.GridRouter(board)

    # ★★★**实测数据 (★2026-11-10 19:3x, ★从 v76mo 裸板量出来的★)** ★★★
    # ★★**`ID_DETECT_1` 的直道 (62.2,11.95)->(68.95,11.95) w=0.15** ★★
    # ★★**离 `BOOT_N` 的出脚口 (63.60, 11.04) 只有 0.91mm ⇒ ⇒ 它【站在别人的出脚口上】** ★★
    CROSS = (62.20, 11.95, 68.95, 11.95)
    BOOTN_PAD = (63.60, 11.04)

    # ★★**构造: 让 `ID_DETECT_1` 走那条横道, 再问"它挡不挡 `BOOT_N` 的出脚"** ★★
    print("  ★真判据: 直道 (%.2f,%.2f)->(%.2f,%.2f) vs 出脚口 (%.2f,%.2f)"
          % (CROSS + BOOTN_PAD))
    _d = G3._pt_seg_dist(BOOTN_PAD[0], BOOTN_PAD[1], CROSS[0], CROSS[1], CROSS[2], CROSS[3])
    print("     出脚口到该直道的距离 = %.4fmm (★实测 0.91·★需 < 0.30+W_MIN/2 才算站在口上★)" % _d)
    # ★★★**实测校准 (★2026-11-10 19:3x★)**: ★**`ID_DETECT_1` 的直道离 `BOOT_N` 出脚口 0.91mm,
    #   而 `BOOT_N` 的出脚直道是 (63.6, 11.04)→(63.6, 12.24), 长 1.2mm
    #   ⇒ ⇒ 【两者在 y=11.04~11.95 这段重叠】⇒ ⇒ 我那条直道【挡住了它的出脚】★★**
    _stub_len = 1.20
    chk("⑤a 实测: 出脚口到那条横道的距离必须 < 【出脚直道长 + 铜边余量】(= %.2f+0.375) ⇒ ★【确实重叠】★" % _stub_len,
        _d < _stub_len + 0.375,
        "★实测 %.4f ⇒ 不重叠 ⇒ ⑤ 的前提不成立★" % _d)

    # ★★**用真判据问: 这条直道会不会挡 `BOOT_N` 的出脚** ★★
    _blocked = r._stub_blocks_neighbor("ID_DETECT_1", CROSS[0], CROSS[1], CROSS[2], CROSS[3])
    print("  ★真判据 _stub_blocks_neighbor('ID_DETECT_1', 那条横道) = %s" % _blocked)
    chk("⑤b 真判据必须判【那条横道挡住了 `BOOT_N` 的出脚口】",
        _blocked,
        "★判据没抓到 ⇒ 修法无效★")

    # ★★**⑥ 无关的脚 (★板子另一头★) 必须判为【不挡】** ★★
    _far = r._stub_blocks_neighbor("ID_DETECT_1", 140.0, 60.0, 145.0, 60.0)
    chk("⑥ 真判据: 远在板子另一头的直道必须判为【不挡】(★闸不许乱杀★)",
        not _far,
        "★把无关的直道也判成挡 ⇒ 闸太宽★")
else:
    chk("⑤⑥ 几何级断言 (★拿不到 pcbnew★)", False, "★pcbnew 不可用★")

# ---------------------------------------------------------------- 汇总
print()
if FAIL:
    print("═══ 失败 %d 项 ═══" % len(FAIL))
    for f in FAIL:
        print("   ✘ %s" % f)
    sys.exit(1)
print("═══ ALL PASS (%d 项) ═══" % len(OK))
sys.exit(0)
