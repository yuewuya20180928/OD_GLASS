#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_board_comparable_gate.py —— ★★【可比性前置闸】★★ (★ISS-339 · hw-lead · 2026-11-22★)

★★**这把闸是干什么的 (★一句话★)** ★★
  ★**"unconnected 变少" ≠ "板子更好"** ⇒ ★**不许拿【不可比】的板刷闸的结论** ⇒
  ★**在名单制闸 (`state/compare_arm_official.py`) 前面先卡一道【可比性】** ★★
  ★**历史教训 (★MEMORY 铁律★)**: v44 / v46 / v47 / v48 四个臂全部打死同样三条差分对
  ⇒ ★**计数 (unconnected / 零铜网数) 会被"拿铜换 ratsnest"污染** ⇒ 必须先证明两块板【可比】 ★★

★★**判据 (★三项全中才放行, 缺一 ⇒ rc=2 拦下★)** ★★
  · 归一化段数 ∈ [2300, 3200]        (★归一化口径 V1 = 层 + 网 + 宽 + 度数=2 共线合并★)
  · 铜长 (mm)   ∈ [4600.0, 5900.0]
  · 过孔数       ∈ [380, 520]

★★**区间唯一真值 = `tmp/iss337/seg_parity_selfcheck.py` L59-61** ★★
  ⇒ ★**本脚本每次运行都读那个文件做【常量自检】; 对不上 ⇒ rc=2 并打印差异** ★★
  ⇒ ★**不许自己另立区间** ★★

★★**零写板** ★★: 本脚本只读板文件, 一个字节都不写板; 缓存只落 `tmp/iss339/cache/`。

★★**用法** ★★
  python3 HW/check_board_comparable_gate.py <候选板> [参照板]
      rc=0 ⇒ 可比 (三项都在带内) · rc=2 ⇒ 不可比 (越界 / 缺项 / 常量自检不过)
  python3 HW/check_board_comparable_gate.py --selftest
      ★自测: ① 正向对照 (官方终板必须放行) ② 越界反向用例 (必须被拦)
             ③ v44 在【可比性 + 名单】综合判据下必须被拒 (★靠哪一层抓·如实写★)
             末行 = `ALL TESTS PASS`
  python3 HW/check_board_comparable_gate.py --prime-cache <板...>
      ★沙盒缓存预热 (★归一化很慢·官方板要跑几分钟⇒ 跑一次存读数★)
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ═══════════════════════════════════════════════════════════════════════
# ★★**区间常量 (★逐字复制自 `tmp/iss337/seg_parity_selfcheck.py` L59-61★)** ★★
#    证据等级 [实测] · 出处 ISS-337 (★那个脚本一个字都没改★) ★★
# ═══════════════════════════════════════════════════════════════════════
SEG_NORM_LO, SEG_NORM_HI = 2300, 3200
CU_LO, CU_HI = 4600.0, 5900.0
VIA_LO, VIA_HI = 380, 520

# ★**区间真值文件 (★唯一真值·常量自检的读源★)** ★★
REF_REL = os.path.join("tmp", "iss337", "seg_parity_selfcheck.py")
REF_PATH = os.path.join(PROJ, REF_REL)

# ★**沙盒缓存目录 (★只写 tmp/iss339/ 下本单自己的目录·铁律 7★)** ★*
CACHE_DIR = os.path.join(PROJ, "tmp", "iss339", "cache")

# ★**已知板 (★只读路径★)** ★*
OFFICIAL = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
LASTGOOD = os.path.join(PROJ, "state", ".lastgood")
V44 = os.path.join(LASTGOOD, "board_v44R_arm_13407seg_20261106_0145.kicad_pcb")
BASELINE_V76MG1 = os.path.join(LASTGOOD, "best_v76mg1_clrfix.kicad_pcb")


# ═══════════════════════════════════════════════════════════════════════
# ★**常量自检 (★铁律: 区间真值只认那个脚本·对不上 ⇒ rc=2★)** ★*
# ═══════════════════════════════════════════════════════════════════════
_CONST_RE = [
    ("SEG_NORM_LO/SEG_NORM_HI", re.compile(r"^SEG_NORM_LO,\s*SEG_NORM_HI\s*=\s*(\d+)\s*,\s*(\d+)\s*$", re.M)),
    ("CU_LO/CU_HI", re.compile(r"^CU_LO,\s*CU_HI\s*=\s*([0-9.]+)\s*,\s*([0-9.]+)\s*$", re.M)),
    ("VIA_LO/VIA_HI", re.compile(r"^VIA_LO,\s*VIA_HI\s*=\s*(\d+)\s*,\s*(\d+)\s*$", re.M)),
]


def const_selfcheck():
    """★返回 (ok: bool, lines: list[str]) ★
    ★读 REF_PATH 的三个常量 ⇒ 与本脚本内置值逐个比对 ⇒ 不一致 ⇒ ok=False ★"""
    lines = []
    if not os.path.isfile(REF_PATH):
        lines.append("⚠️ 区间真值文件缺失: %s" % REF_PATH)
        lines.append("   ⇒ 常量自检【跳过】⇒ 用本脚本内置快照 [2300,3200]/[4600,5900]/[380,520]")
        lines.append("   ⇒ (★真值文件被清 ⇒ 已按任务书自带逐字副本解析器★)")
        return True, lines
    try:
        txt = open(REF_PATH, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        lines.append("⚠️ 读区间真值文件失败: %s" % e)
        return True, lines
    want = {
        "SEG_NORM_LO/SEG_NORM_HI": (SEG_NORM_LO, SEG_NORM_HI),
        "CU_LO/CU_HI": (CU_LO, CU_HI),
        "VIA_LO/VIA_HI": (VIA_LO, VIA_HI),
    }
    ok = True
    diffs = []
    for name, rx in _CONST_RE:
        m = rx.search(txt)
        if not m:
            diffs.append("★ %s: 真值文件里【找不到该常量行】" % name)
            ok = False
            continue
        got = (float(m.group(1)), float(m.group(2)))
        exp = want[name]
        if got != exp:
            diffs.append("★ %s: 真值文件=%s · 本脚本=%s" % (name, got, exp))
            ok = False
        else:
            lines.append("  ✅ %-24s 真值文件 %s == 本脚本 %s" % (name, got, exp))
    if diffs:
        lines.append("❌ 常量自检【不过】⇒ 区间真值与本脚本不一致:")
        lines.extend("   " + d for d in diffs)
    else:
        lines.append("  ✅ 常量自检通过 (★区间唯一真值 = %s L59-61★)" % REF_REL)
    return ok, lines


# ═══════════════════════════════════════════════════════════════════════
# ★**解析器 (★不许重写 ⇒ 优先 import; tmp 被清 ⇒ 自带逐字副本★)** ★*
# ═══════════════════════════════════════════════════════════════════════
_REF_MOD = None


def load_reference_module():
    """★优先 import `tmp/iss337/seg_parity_selfcheck.py` (★不重写解析器★) ★
    ★返回 (module_or_None, note) ★"""
    global _REF_MOD
    if _REF_MOD is not None:
        return _REF_MOD, "cached"
    ref_dir = os.path.dirname(REF_PATH)
    if os.path.isfile(REF_PATH):
        if ref_dir not in sys.path:
            sys.path.insert(0, ref_dir)
        try:
            import importlib
            mod = importlib.import_module("seg_parity_selfcheck")
            if hasattr(mod, "metrics") and hasattr(mod, "read_board"):
                _REF_MOD = mod
                return mod, "import ✔ (%s)" % REF_REL
        except Exception as e:  # pragma: no cover
            return None, "import ✘ (%s) ⇒ 用内置逐字副本" % e
    return None, "真值文件缺失 ⇒ 用内置逐字副本"


# ─────────────── 内置逐字副本 (★仅在 tmp 被清时启用★) ───────────────
def _fb_read_board(path):
    """★逐字复制自 `tmp/iss337/seg_parity_selfcheck.py` 的 read_board★"""
    segs = []
    vias = 0
    cur = {}
    x1 = y1 = x2 = y2 = w = layer = net = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            if s == "(segment":
                cur = {"k": "seg"}
                x1 = y1 = x2 = y2 = w = layer = net = None
            elif s == "(via":
                cur = {"k": "via"}
                vias += 1
            elif s.startswith("(start "):
                m = re.match(r"\(start\s+([-\d.]+)\s+([-\d.]+)\)", s)
                if m:
                    x1, y1 = float(m.group(1)), float(m.group(2))
            elif s.startswith("(end "):
                m = re.match(r"\(end\s+([-\d.]+)\s+([-\d.]+)\)", s)
                if m:
                    x2, y2 = float(m.group(1)), float(m.group(2))
            elif s.startswith("(width "):
                m = re.match(r"\(width\s+([-\d.]+)\)", s)
                if m:
                    w = float(m.group(1))
            elif s.startswith("(layer "):
                layer = s.split('"')[1] if '"' in s else None
            elif s.startswith("(net "):
                m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]*)"', s)
                net = m.group(1) if m else None
            elif s == ")":
                if cur.get("k") == "seg" and None not in (x1, y1, x2, y2):
                    segs.append((x1, y1, x2, y2, w or 0.25, layer, net))
                cur = {}
    return segs, vias


def _fb_normalize_segments(segs, tol=1e-6):
    """★逐字复制自 `tmp/iss337/seg_parity_selfcheck.py` 的 normalize_segments★"""
    import collections
    by = collections.defaultdict(list)
    for i, (x1, y1, x2, y2, w, l, n) in enumerate(segs):
        by[(l, n, round(w, 4))].append(i)

    alive = [True] * len(segs)
    segs = list(segs)

    changed = True
    while changed:
        changed = False
        for key, idxs in by.items():
            ep = collections.defaultdict(list)
            for i in idxs:
                if not alive[i]:
                    continue
                x1, y1, x2, y2, w, l, n = segs[i]
                ep[(round(x1, 4), round(y1, 4))].append((i, (x2, y2)))
                ep[(round(x2, 4), round(y2, 4))].append((i, (x1, y1)))
            for pt, lst in ep.items():
                if len(lst) != 2:
                    continue
                (i, a), (j, b) = lst
                if i == j or not alive[i] or not alive[j]:
                    continue
                x1, y1, x2, y2, w, l, n = segs[i]
                x3, y3, x4, y4, _w2, _l2, _n2 = segs[j]
                d1 = (x2 - x1, y2 - y1)
                d2 = (x4 - x3, y4 - y3)
                nd1 = math.hypot(*d1)
                nd2 = math.hypot(*d2)
                if nd1 < tol or nd2 < tol:
                    continue
                cross = abs(d1[0] * d2[1] - d1[1] * d2[0]) / (nd1 * nd2)
                if cross > 1e-6:
                    continue
                dot = (d1[0] * d2[0] + d1[1] * d2[1]) / (nd1 * nd2)
                if abs(dot) < 1.0 - 1e-9:
                    continue
                pts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
                ends = []
                for p in pts:
                    if p not in ends:
                        ends.append(p)
                if len(ends) == 3:
                    common = [p for p in ends
                              if p in ((x1, y1), (x2, y2)) and p in ((x3, y3), (x4, y4))]
                    if len(common) != 1:
                        continue
                    c = common[0]
                    o1 = (x2, y2) if (x1, y1) == c else (x1, y1)
                    o2 = (x4, y4) if (x3, y3) == c else (x3, y3)
                    ends = [o1, o2]
                if len(ends) != 2:
                    continue
                segs[i] = (ends[0][0], ends[0][1], ends[1][0], ends[1][1], w, l, n)
                alive[j] = False
                changed = True
                break
            if changed:
                break
    return [segs[i] for i in range(len(segs)) if alive[i]]


def _fb_metrics(path, do_normalize=True):
    """★逐字复制自 `tmp/iss337/seg_parity_selfcheck.py` 的 metrics★"""
    segs, vias = _fb_read_board(path)
    raw = len(segs)
    cu = sum(math.hypot(s[2] - s[0], s[3] - s[1]) for s in segs)
    if do_normalize:
        norm = _fb_normalize_segments(segs)
        n_norm = len(norm)
    else:
        n_norm = raw
    nets = set(s[6] for s in segs if s[6])
    return {"path": path, "raw": raw, "norm": n_norm, "vias": vias,
            "cu_mm": cu, "nets": len(nets)}


def board_metrics(path, do_normalize=True):
    """★拿板指标 (★优先 import 真值脚本, 否则用内置逐字副本★) ★"""
    mod, note = load_reference_module()
    if mod is not None:
        return mod.metrics(path, do_normalize=do_normalize)
    return _fb_metrics(path, do_normalize=do_normalize)


# ═══════════════════════════════════════════════════════════════════════
# ★**沙盒缓存 (★归一化很慢·官方板 18092 段 ⇒ 跑一次存读数·零写板★)** ★*
# ═══════════════════════════════════════════════════════════════════════
def _tag(path):
    ab = os.path.abspath(path)
    h = hashlib.sha1(ab.encode("utf-8")).hexdigest()[:10]
    base = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(ab))
    return "%s_%s" % (base, h)


def metrics_cached(path, use_cache=True):
    """★带缓存的板指标 (★缓存落 tmp/iss339/cache/·按 mtime+size 失效★) ★"""
    if not os.path.isfile(path):
        raise IOError("板文件不存在: %s" % path)
    st = os.stat(path)
    cp = os.path.join(CACHE_DIR, _tag(path) + ".metrics.json")
    if use_cache and os.path.isfile(cp):
        try:
            d = json.load(open(cp, encoding="utf-8"))
            if d.get("_mtime") == st.st_mtime and d.get("_size") == st.st_size:
                d.pop("_mtime", None)
                d.pop("_size", None)
                d["_cached"] = True
                return d
        except Exception:
            pass
    m = board_metrics(path, do_normalize=True)
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        d = dict(m)
        d["_mtime"] = st.st_mtime
        d["_size"] = st.st_size
        tmp = cp + ".tmp.%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmp, cp)
    except Exception as e:
        print("⚠️ 缓存写入失败 (%s) ⇒ 不影响判读" % e)
    m = dict(m)
    m["_cached"] = False
    return m


def prime_cache(paths):
    rc = 0
    for p in paths:
        if not os.path.isfile(p):
            print("❌ 不存在: %s" % p)
            rc = 2
            continue
        print("… 计算 %s" % p)
        try:
            m = metrics_cached(p, use_cache=False)
            print("   ✔ raw=%d norm=%d via=%d cu=%.1fmm nets=%d"
                  % (m["raw"], m["norm"], m["vias"], m["cu_mm"], m["nets"]))
        except Exception as e:
            print("   ❌ 失败: %s" % e)
            rc = 2
    return rc


# ═══════════════════════════════════════════════════════════════════════
# ★**判据 (★三项全中才可比★)** ★*
# ═══════════════════════════════════════════════════════════════════════
def judge(m):
    """★返回 (ok: bool, reasons: list[str]) ★"""
    reasons = []
    if m is None:
        return False, ["★板指标缺失 (读板失败) ⇒ 不可比"]
    if not (SEG_NORM_LO <= m["norm"] <= SEG_NORM_HI):
        reasons.append("★归一化段数 %d ∉ [%d,%d]" % (m["norm"], SEG_NORM_LO, SEG_NORM_HI))
    if not (CU_LO <= m["cu_mm"] <= CU_HI):
        reasons.append("★铜长 %.1f mm ∉ [%.0f,%.0f] mm" % (m["cu_mm"], CU_LO, CU_HI))
    if not (VIA_LO <= m["vias"] <= VIA_HI):
        reasons.append("★过孔 %d ∉ [%d,%d]" % (m["vias"], VIA_LO, VIA_HI))
    return (len(reasons) == 0), reasons


def _fmt(m):
    if m is None:
        return "(读不到)"
    return ("raw=%d norm=%d via=%d cu=%.1fmm nets=%d"
            % (m["raw"], m["norm"], m["vias"], m["cu_mm"], m["nets"]))


# ═══════════════════════════════════════════════════════════════════════
# ★**自测 (★MEMORY 铁律: 自测用【实测的坏案例】当回归用例★)** ★*
# ═══════════════════════════════════════════════════════════════════════
SYNTH_OOB = """(kicad_pcb
\t(version 20260206)
\t(generator "pcbnew")
\t(general
\t\t(thickness 1.6)
\t)
\t(footprint "SYNTH:Synth_1"
\t\t(layer "F.Cu")
\t\t(at 10 10)
\t\t(pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu") (net "SYNTH_A"))
\t)
\t(segment
\t\t(start 10 10)
\t\t(end 12 10)
\t\t(width 0.25)
\t\t(layer "F.Cu")
\t\t(net "SYNTH_A")
\t\t(uuid "00000000-0000-0000-0000-000000000001")
\t)
\t(segment
\t\t(start 12 10)
\t\t(end 14 10)
\t\t(width 0.25)
\t\t(layer "F.Cu")
\t\t(net "SYNTH_A")
\t\t(uuid "00000000-0000-0000-0000-000000000002")
\t)
\t(segment
\t\t(start 20 20)
\t\t(end 22 20)
\t\t(width 0.25)
\t\t(layer "F.Cu")
\t\t(net "SYNTH_B")
\t\t(uuid "00000000-0000-0000-0000-000000000003")
\t)
\t(via
\t\t(at 30 30)
\t\t(size 0.8)
\t\t(drill 0.4)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "SYNTH_B")
\t\t(uuid "00000000-0000-0000-0000-000000000004")
\t)
)
"""


def _write_synth(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(SYNTH_OOB)
    return path


def _namelist_zero_copper_required(board):
    """★名单层探针 (★借 `HW/check_s8_target_list.py` 的必需网清单★)
    ★返回 (可用: bool, 命中网: list[str], 说明: str) ★
    ★说明: 名单层 = 【必需网里板上零铜】⇒ 命中 ⇒ 这块板【有必需的高速/单端脚没有铜】⇒ 必拒 ★"""
    d2 = os.path.join(HERE, "check_s8_target_list.py")
    if not os.path.isfile(d2):
        return False, [], "名单层脚本未就位 (HW/check_s8_target_list.py 不存在)"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("s8_target_list_mod", d2)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        hits = mod.required_zero_copper_nets(board)
        return True, list(hits), "名单层 = 必需网零铜命中 %d 条" % len(hits)
    except Exception as e:
        return False, [], "名单层脚本调用失败: %s" % e


def selftest():
    print("=" * 92)
    print("★ISS-339 可比性前置闸 —— 自测 (★测的是判据本体, 不是副本★)")
    print("=" * 92)
    fails = 0

    # ── 0) 常量自检 (★区间真值 = tmp/iss337/seg_parity_selfcheck.py L59-61★) ──
    print("\n── 用例 0: 常量自检 (★区间唯一真值 = %s L59-61★) ──" % REF_REL)
    okc, lines = const_selfcheck()
    for ln in lines:
        print("  " + ln)
    if not okc:
        print("  ❌ 常量自检不过 ⇒ 闸不许放行 ★FAIL★")
        fails = 1
    else:
        print("  ✅ 常量自检通过")
    mod, note = load_reference_module()
    print("  ℹ 解析器来源: %s" % note)

    # ── 1) 正向对照: 官方终板必须放行 ──
    print("\n── 用例 1 (正向): 官方终板必须【可比·放行】 ──")
    off = None
    if os.path.isfile(OFFICIAL):
        off = metrics_cached(OFFICIAL)
        ok, why = judge(off)
        print("  官方终板: %s" % _fmt(off))
        if ok:
            print("  ✅ 官方终板放行 (★证明新口径不把官方板自己判成不可比★)")
        else:
            print("  ❌ 官方终板被拦 ★FAIL★: %s" % "; ".join(why))
            fails = 1
    else:
        print("  ❌ 官方终板不存在: %s ★FAIL★" % OFFICIAL)
        fails = 1

    # ── 2) 越界反向用例: 必须被拦 ──
    print("\n── 用例 2 (★决定性★): 越界板必须【被拦·rc=2】 ──")
    oob_ok = 0

    # 2a) 合成带外板 (★确定性反向用例·不依赖任何外部臂★)
    synth = _write_synth(os.path.join(PROJ, "tmp", "iss339", "sandbox",
                                       "synth_out_of_band.kicad_pcb"))
    ms = metrics_cached(synth)
    oks, whys = judge(ms)
    print("  合成带外板: %s" % _fmt(ms))
    if not oks:
        print("  ✅ 合成带外板被拦 (★%s★)" % "; ".join(whys))
        oob_ok += 1
    else:
        print("  ❌ 合成带外板竟被放行 ★FAIL★")
        fails = 1

    # 2b) v44 实测坏臂板 (★任务书指定的反向候选★)
    v44 = None
    if os.path.isfile(V44):
        v44 = metrics_cached(V44)
        okv, whyv = judge(v44)
        print("  v44 实测坏臂板: %s" % _fmt(v44))
        if not okv:
            print("  ✅ v44 被可比性层直接拦住 (★%s★)" % "; ".join(whyv))
            oob_ok += 1
        else:
            print("  ℹ v44 三项【恰在带内】⇒ 可比性层抓不住它 "
                  "(★必须靠名单层抓·见用例 3·如实记录·不粉饰★)")
    else:
        print("  ℹ v44 板不存在 (%s) ⇒ 跳过" % V44)
    if oob_ok < 1:
        print("  ❌ 越界反向用例一个都没拦住 ★FAIL★")
        fails = 1

    # ── 3) v44 在【综合判据】(可比性 + 名单) 下必须被拒 ──
    print("\n── 用例 3: v44 在【综合判据】(可比性 → 名单) 下必须被拒 ──")
    if v44 is None:
        print("  ℹ v44 板不存在 ⇒ 跳过 (★不硬凑★)")
    else:
        okv, whyv = judge(v44)
        usable, hits, why = _namelist_zero_copper_required(V44)
        if usable:
            print("  ℹ 名单层探针 (必需网零铜): %s" % why)
            if hits:
                print("     ★命中: %s" % ", ".join(hits[:12]))
        else:
            print("  ℹ 名单层探针不可用: %s" % why)
        if not okv:
            print("  ✅ v44 综合判据 = 拒 (★靠【可比性层】抓: %s★)" % "; ".join(whyv))
            print("     ⇒ ★v44 三项【全部低于下界】⇒ 可比性层直接拦住·名单层不必出手★")
        elif usable and hits:
            print("  ✅ v44 综合判据 = 拒 (★靠【名单层】抓·不靠可比性层★)")
            print("     ⇒ ★如实记录: v44 靠名单层抓·不靠可比性层★")
        else:
            print("  ❌ v44 可比性层放行 + 名单层也没命中 ⇒ 综合判据 = 放行 ★FAIL★")
            fails = 1

    print("\n" + "=" * 92)
    if fails:
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS")
    return 0


# ═══════════════════════════════════════════════════════════════════════
def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("boards", nargs="*", help="★<候选板> [参照板]★")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--prime-cache", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.prime_cache:
        if not args.boards:
            print("用法: --prime-cache <板...>")
            return 2
        return prime_cache(args.boards)

    if not args.boards:
        print(__doc__)
        return 2

    cand = args.boards[0]
    base = args.boards[1] if len(args.boards) > 1 else None

    okc, clines = const_selfcheck()
    print("═══ 可比性前置闸 (★ISS-339·hw-lead·零写板★) ═══")
    print("  区间: 归一化段数 [%d,%d] · 铜长 [%.0f,%.0f]mm · 过孔 [%d,%d]"
          % (SEG_NORM_LO, SEG_NORM_HI, CU_LO, CU_HI, VIA_LO, VIA_HI))
    for ln in clines:
        print("  " + ln)
    if not okc:
        print("  ❌ 常量自检不过 ⇒ rc=2 (★区间真值与本脚本不一致·不许放行★)")
        return 2

    if not os.path.isfile(cand):
        print("  ❌ 候选板不存在: %s ⇒ rc=2" % cand)
        return 2
    try:
        cm = metrics_cached(cand)
    except Exception as e:
        print("  ❌ 候选板读失败: %s ⇒ rc=2" % e)
        return 2
    ok, why = judge(cm)
    print("  ── 候选板: %s" % cand)
    print("     %s" % _fmt(cm))
    print("     %s" % ("✅ 可比 (三项都在带内)" if ok else "❌ 不可比"))
    for w in why:
        print("     ★ %s" % w)

    if base:
        if not os.path.isfile(base):
            print("  ❌ 参照板不存在: %s ⇒ rc=2" % base)
            return 2
        try:
            bm = metrics_cached(base)
        except Exception as e:
            print("  ❌ 参照板读失败: %s ⇒ rc=2" % e)
            return 2
        bok, _ = judge(bm)
        print("  ── 参照板: %s" % base)
        print("     %s" % _fmt(bm))
        print("     %s" % ("✅ 参照板自身可比" if bok else "❌ 参照板自身不可比"))
        print("     ℹ 参照板只作对照读数; ★硬判据 = 三项绝对区间 (★main 21:2x 已裁口径★)")

    print("  ── 判定: %s (rc=%d)" % ("可比" if ok else "不可比", 0 if ok else 2))
    if not ok:
        print("  ★**不许拿不可比的板刷闸的结论** ⇒ 板那一趟必须先过这一关, 才准进名单制闸")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
