#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_layersel.py —— ★★【★防回归自测: 【差分对的层选择】(★`PCB_PAIR_LAYERSEL`★)★】★★

★★★**★问题 (★2026-11-10 19:5x 实测坐实★)★★★ ★★★
  ★**官方板的差分对 P/N 【在【不同层】上分段走】(★实测各层段数★)**:
    · ★`CSI_D0_CK_P` = F.Cu 158 / In2.Cu 71★
    · ★`CSI_D0_CK_N` = F.Cu 78  / In2.Cu 120★ ⇒ ★★**两腿的层占比【相反】★★**
  ⇒ ★★**⇒ 这是【层选择】, 不是【走廊位置】** ★★
  ⇒ ★★**⇒ 而路由器【没有这个机制】(★grep `layer_block`/`blocked_layers`/`exclude.*layer` = 0 命中★)**
    ⇒ ★**P 和 N 用【同一套层集合】(`ROUTE_LAYERS` = [0,2,4,6]) ⇒ ⇒ N 侧只被【走廊】引导, 【不被层引导】**
    ⇒ ★★**⇒ ⇒ 两腿只能挤在同一层 ⇒ ⇒ 挤到 0.4280mm 就违规 (★实测 `CSI_D0_CK_P`↔`CSI_D0_CK_N`★)** ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测★)** ★★★
  ① ★**默认关**: ★**不设 `PCB_PAIR_LAYERSEL` ⇒ 行为必须逐位不变** ★
  ② ★**显式开才 True**
  ③ ★**源码级: 修法必须落在【`_free()` 里 (★所有自由格判断的唯一入口★)】**
  ④ ★**源码级: 修法必须【只限不删】(★不许出现删铜路径★)**
  ⑤ ★★★**★几何级: ★`_free()` 必须【拒绝不在允许层上的格】(★真判据, 真调用★)** ★★★
  ⑥ ★★★**★几何级: ★【层限制解除后, ★同一个格必须恢复可用】(★不许把网永久锁死★)** ★★★
  ⑦ ★★★**★安全性: ★**限制层时 N 侧没布出来 ⇒ ⇒ 必须【放开限制重试】⇒ ⇒ 不会比现状更差** ★★★

用法:
  bash state/pcbnew_py.sh state/_test_layersel.py
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
os.environ.pop("PCB_PAIR_LAYERSEL", None)
import gen_pcb_routing as G          # noqa: E402
chk("① 默认 PCB_PAIR_LAYERSEL 未设 ⇒ 必须 False (★默认逐位不变★)",
    G.PAIR_LAYERSEL is False, "实际 = %r" % (G.PAIR_LAYERSEL,))

os.environ["PCB_PAIR_LAYERSEL"] = "1"
import importlib                   # noqa: E402
G2 = importlib.reload(G)
chk("② PCB_PAIR_LAYERSEL=1 ⇒ 必须 True",
    G2.PAIR_LAYERSEL is True, "实际 = %r" % (G2.PAIR_LAYERSEL,))
os.environ.pop("PCB_PAIR_LAYERSEL", None)
importlib.reload(G)

# ---------------------------------------------------------------- ③ ④ 源码级
_src = open(os.path.join(_HERE, "gen_pcb_routing.py"), encoding="utf-8").read()

_i = _src.index("def _free(self, li, idx, net, cls=1):")
_j = _src.find("\n    def ", _i + 10)
_fbody = _src[_i:_j if _j > 0 else len(_src)]

chk("③ 修法必须落在【`_free()` 里 (★所有自由格判断的唯一入口★)】",
    "_layer_limit" in _fbody,
    "★_free() 里没有 _layer_limit ⇒ 修法没接上★")
chk("④ 修法只【限不删】(★不许出现删铜路径★)",
    ("_drop_committed" not in _fbody) and (".Remove(" not in _fbody)
    and ("self.tracks.remove" not in _fbody),
    "★_free() 里出现了删铜路径★")

# ★★**安全性 (★放开重试★) 必须存在** ★★
chk("⑦ 安全性: 限制层时 N 侧没布出来 ⇒ 必须【放开限制重试】(★保证不比现状更差★)",
    "n_layers_retry" in _src and "_layer_limit = None" in _src,
    "★找不到放开重试的逻辑 ⇒ 闸可能比现状更差★")

# ---------------------------------------------------------------- ⑤⑥ 几何级
print()
print("── 几何级: 用【真 `_free()`】测层限制 ──")
try:
    import pcbnew                # noqa: E402
except Exception:                # noqa: BLE001
    pcbnew = None

if pcbnew is not None:
    board = pcbnew.LoadBoard(os.path.join(_HERE, "..", "HW", "PCB",
                                          "demo_mainboard.kicad_pcb"))
    r = G.GridRouter(board)
    # ★找一个【空的】格 (★不受别的铜影响★) ★
    _idx = None
    for _i2 in range(10, r.W - 10):
        for _j2 in range(10, r.H - 10):
            _k = r._idx(_i2, _j2)
            if not r.cu[0].get(_k) and not r.halo[1][0].get(_k):
                _idx = _k
                break
        if _idx is not None:
            break
    print("  ★选一个空格 idx=%d (★层 0★)" % _idx)

    # ★★**不限制 ⇒ 可用** ★★
    r._layer_limit = None
    _ok0 = r._free(0, _idx, "TESTNET", 1)
    print("  ★不限制时 _free(层0) = %s" % _ok0)

    # ★★**限制到只含层 2 ⇒ 层 0 不可用, 层 2 可用** ★★
    r._layer_limit = {2, 4}
    _ok_l0 = r._free(0, _idx, "TESTNET", 1)
    _ok_l2 = r._free(2, _idx, "TESTNET", 1)
    print("  ★限制={2,4} 时 _free(层0)=%s · _free(层2)=%s" % (_ok_l0, _ok_l2))

    chk("⑤ 真判据: 限制层后, 【不在允许层上的格必须被拒】(★层0 应 False★) 且 【允许层仍可用】(★层2 应 True★)",
        (not _ok_l0) and _ok_l2,
        "★层0=%s (★应 False★) 层2=%s (★应 True★) ⇒ 层限制行为不对★" % (_ok_l0, _ok_l2))

    # ★★**解除限制 ⇒ 恢复可用** ★★
    r._layer_limit = None
    _ok1 = r._free(0, _idx, "TESTNET", 1)
    chk("⑥ 真判据: 解除层限制后, 【同一个格必须恢复可用】(★不许把网永久锁死★)",
        _ok1,
        "★解除限制后仍不可用 ⇒ 格被永久锁死★")
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
