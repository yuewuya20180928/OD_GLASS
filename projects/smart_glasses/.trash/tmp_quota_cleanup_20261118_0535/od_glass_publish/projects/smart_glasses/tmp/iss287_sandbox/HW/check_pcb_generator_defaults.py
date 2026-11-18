#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-269 · 板生成器默认值闸 —— 守住「板只改一次」那三个会让那一趟白做的生成器坑
=================================================================================
派活: state/dispatch_briefs/ISS-269_hw_gen_three_landmines.md (项目总工 2026-11-17 04:2x)

★**本闸守的是「生成器」不是「板」** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM**

三个判据 (★每条都机器可判, 不许"看着像" ★):

  C1 层数默认   : 生成器 `PCB_LAYERS` 的**默认值** == **盘上板铜层数** == **8** (★三者必须同时成立 ★)
                   ★**为什么要绑在一起**: 生成器默认 6 而盘上板是 8 ⇒ 裸跑一次 ⇒ 板掉到 6 层
                   ⇒ 「板只改一次」那一趟当场白做 (★HW/PCB/STACKUP.md 记着 11-06 同型事故 ★)
  C2 DNP 支持   : 生成器必须 (a) **静态**含 DNP 三件套 + 读网表 `dnp` 列
                   (b) **行为**: 把生成器源码里的 `dnp_refs_from_rows` 抽出来 exec, 喂自造样例
                   ⇒ 必须按 `dnp` 列判 DNP (★不是另立一套白名单 ★)
  C3 Value 取值 : 生成器的 `value_of` 必须**本体行优先** (★`type` ∉ {"NET",""} 的行 ★)
                   ⇒ **行为**: 抽 `pick_board_values` exec ⇒ 合成样例 (NET 行在前 / IC 行在后)
                   ⇒ 必须取到 IC 行的器件身份; ★且**真盘网表**上 `U_EN_SW` 取到的 value
                   ⇒ 必须含 `TPS22991RAA` 且**不含**脚功能串 'EN 输入'
  C4 防手滑闸   : 生成器覆盖正式板必须显式 `PCB_ALLOW_OFFICIAL=1` (★建议项 · 本单实现 ★)

★**为什么用「抽源码 exec」而不是「静态字符串匹配」**:
  静态匹配 = 改个注释就能骗过闸 ⇒ 那是假绿 ⇒ ★本闸的行为判定把**生成器自己的函数**
  拿出来跑真实样例 ⇒ 改逻辑就必红 ★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 HW/check_pcb_generator_defaults.py              # 主模式
  python3 HW/check_pcb_generator_defaults.py --selftest    # 反向用例 (≥4 条, 每条自证改到了目标)
  python3 HW/check_pcb_generator_defaults.py --gen PATH --board PATH --netlist PATH   # ★自检用 ★
"""
from __future__ import annotations

import argparse
import ast
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

GEN_DEFAULT = os.path.join(PROJ, "state", "gen_pcb_netlist_board.py")
BOARD_DEFAULT = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
NETLIST_DEFAULT = os.path.join(PROJ, "HW", "netlist_v1.csv")

# ★**盘上板实测铜层数 (2026-11-17 pcbnew 实读 = 8)** ⇒ 这是「板只改一次」那一趟的层数基线
EXPECTED_LAYERS = 8

# ★**板封装的 Value 判据 (作业包 §S3 B-2 的量化判据)**: U_EN_SW 必须拿到器件身份, 不是脚功能串
BOARD_VALUE_REF = "U_EN_SW"
BOARD_VALUE_MUST_CONTAIN = "TPS22991RAA"
BOARD_VALUE_MUST_NOT_CONTAIN = "EN 输入"


# ==============================================================================
# 基础工具
# ==============================================================================
def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_layer_default(src: str):
    """★生成器里 `PCB_LAYERS` 的默认值 (★静态判定 ★)
    匹配 os.environ.get("PCB_LAYERS", N) ⇒ N; 匹配不到 ⇒ None (⇒ 闸红, fail-closed)"""
    m = re.search(r"os\.environ\.get\(\s*[\"']PCB_LAYERS[\"']\s*,\s*(\d+)\s*\)", src)
    if not m:
        return None
    return int(m.group(1))


def board_copper_layers(path: str):
    """★盘上板文件里的铜层数 (★文本层解析 (layers 段) ★)
    ★不依赖 pcbnew ⇒ 系统 python 就能跑; pcbnew 实读另做一条交叉校验 (C1b)"""
    txt = read_text(path)
    i = txt.find("(layers")
    if i < 0:
        return None
    j = txt.find("\n\t)", i)
    block = txt[i:(j if j > 0 else i + 20000)]
    return len(re.findall(r'\(\d+\s+"[^"]+\.Cu"\s+signal\)', block))


def pcbnew_copper_layers(path: str):
    """★用 pcbnew 实读盘上板铜层数 (★交叉校验 ★)
    KiCad 不在本机 ⇒ 返回 (None, 原因) ⇒ 调用方降级成 WARN (不判红)"""
    sh = os.path.join(PROJ, "state", "pcbnew_py.sh")
    if not os.path.exists(sh):
        return None, "state/pcbnew_py.sh 不存在"
    code = ("import pcbnew;b=pcbnew.LoadBoard(%r);print('LAYERS=%%d'%%b.GetCopperLayerCount())"
            % path)
    try:
        r = subprocess.run(["bash", sh, "-c", code], cwd=PROJ, timeout=180,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:                      # pragma: no cover
        return None, "pcbnew 调用异常: %s" % e
    if r.returncode != 0:
        return None, "pcbnew rc=%d: %s" % (r.returncode, (r.stderr or b"")[:160].decode("utf-8", "replace"))
    out = (r.stdout or b"").decode("utf-8", "replace")
    m = re.search(r"LAYERS=(\d+)", out)
    if not m:
        return None, "pcbnew 输出里没有层数: %r" % out[:160]
    return int(m.group(1)), None


def extract_func(src: str, name: str):
    """★把生成器源码里的某个函数抽出来, 编译成可执行对象 (★行为判定的地基 ★)
    ⇒ ★**执行的是生成器自己的代码**, 不是闸里抄一份 ⇒ 改逻辑必红 ★"""
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec(compile(seg, "<gen-extract:%s>" % name, "exec"), ns)
            return ns[name]
    return None


def load_netlist_rows(path: str):
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        return list(csv.DictReader(f))


# ==============================================================================
# 三条判据
# ==============================================================================
def check_C1(gen_path: str, board_path: str):
    """★C1 层数默认 == 盘上板 == 8"""
    res = {"ok": True, "lines": []}
    src = read_text(gen_path)
    default = parse_layer_default(src)
    board_n = board_copper_layers(board_path)
    res["lines"].append("     生成器 PCB_LAYERS 默认 = %s (源码实测)" % default)
    res["lines"].append("     盘上板铜层数 (kicad_pcb 文本 (layers 段) 实测) = %s" % board_n)
    if default is None:
        res["ok"] = False
        res["lines"].append("     ❌ 生成器里解析不到 `os.environ.get(\"PCB_LAYERS\", N)` ⇒ 判据读不到 ⇒ 红")
        return res
    if board_n is None:
        res["ok"] = False
        res["lines"].append("     ❌ 盘上板 (layers 段) 解析不到 ⇒ 红")
        return res
    if default != EXPECTED_LAYERS:
        res["ok"] = False
        res["lines"].append("     ❌ 生成器默认 %d ≠ 期望 %d (★裸跑生成器 ⇒ 板层数会掉 ★)" % (default, EXPECTED_LAYERS))
    if board_n != EXPECTED_LAYERS:
        res["ok"] = False
        res["lines"].append("     ❌ 盘上板 %d 层 ≠ 期望 %d (★基线变了 ⇒ 人工裁决 ★)" % (board_n, EXPECTED_LAYERS))
    if default != board_n:
        res["ok"] = False
        res["lines"].append("     ❌ 生成器默认 %d ≠ 盘上板 %d (★两者必须绑死 ★)" % (default, board_n))
    # C1b: pcbnew 实读交叉校验 (★有 KiCad 就必须对得上 ★)
    live, why = pcbnew_copper_layers(board_path)
    if live is None:
        res["lines"].append("     ⚠ pcbnew 实读跳过 (%s)" % why)
    else:
        res["lines"].append("     pcbnew 实读盘上板铜层数 = %d" % live)
        if live != board_n or live != default:
            res["ok"] = False
            res["lines"].append("     ❌ pcbnew 实读 %d ≠ 文本解析 %d / 生成器默认 %d"
                                % (live, board_n, default))
    return res


def check_C2(gen_path: str, netlist_path: str):
    """★C2 DNP 支持: 静态 (三件套 + 读 dnp 列) + 行为 (抽函数跑样例)"""
    res = {"ok": True, "lines": []}
    src = read_text(gen_path)
    static_miss = []
    for token, why in (
        ("dnp_refs_from_rows", "★没有引用 dnp 位号取值函数 ★"),
        ('"dnp"', "★没有读网表的 dnp 列 ★"),
        ("FP_EXCLUDE_FROM_BOM", "★没有 exclude_from_bom ★"),
        ("FP_EXCLUDE_FROM_POS_FILES", "★没有 exclude_from_pos_files ★"),
        ("FP_DNP", "★没有 dnp 属性 ★"),
    ):
        if token not in src:
            static_miss.append(why)
    if static_miss:
        res["ok"] = False
        for m in static_miss:
            res["lines"].append("     ❌ 静态: %s" % m)
    else:
        res["lines"].append("     静态: dnp 列 + exclude_from_bom/exclude_from_pos_files/dnp 三件套 都在")

    fn = extract_func(src, "dnp_refs_from_rows")
    if fn is None:
        res["ok"] = False
        res["lines"].append("     ❌ 行为: 抽不出 `dnp_refs_from_rows` 函数 ⇒ 红")
        return res
    fixture = [
        {"ref": "AAA", "dnp": "DNP", "value": "x", "type": "R"},
        {"ref": "BBB", "dnp": "必装", "value": "x", "type": "R"},
        {"ref": "CCC", "dnp": "可选", "value": "x", "type": "R"},
        {"ref": "", "dnp": "DNP", "value": "x", "type": "R"},
    ]
    got = fn(fixture)
    if got != {"AAA"}:
        res["ok"] = False
        res["lines"].append("     ❌ 行为: 合成样例应得 {'AAA'} ⇒ 实得 %r" % (sorted(got),))
    else:
        res["lines"].append("     行为: 合成样例 dnp='DNP' ⇒ {'AAA'} (必装/可选/空 ref 都不误判) ✔")

    rows = load_netlist_rows(netlist_path)
    real = fn(rows)
    known = {"U_BATPROT", "BT_432243", "U_LDO_S28"}
    miss = sorted(known - set(real))
    if miss:
        res["ok"] = False
        res["lines"].append("     ❌ 行为: 真盘网表里 %s 明明是 DNP 却没被读出来" % miss)
    else:
        res["lines"].append("     行为: 真盘网表读出 %d 个 DNP 位号 (含 %s) ✔"
                            % (len(real), "/".join(sorted(known))))
    return res


def check_C3(gen_path: str, netlist_path: str):
    """★C3 Value 取值: 静态 (用了本体行优先的函数) + 行为 (合成样例 + 真盘 U_EN_SW)"""
    res = {"ok": True, "lines": []}
    src = read_text(gen_path)
    if "pick_board_values(rows)" not in src:
        res["ok"] = False
        res["lines"].append("     ❌ 静态: main() 没走 `pick_board_values(rows)` ⇒ 仍是首见取值 ⇒ 红")
    else:
        res["lines"].append("     静态: main() 走 pick_board_values(rows) (本体行优先)")

    fn = extract_func(src, "pick_board_values")
    if fn is None:
        res["ok"] = False
        res["lines"].append("     ❌ 行为: 抽不出 `pick_board_values` 函数 ⇒ 红")
        return res
    # ★合成样例: NET 行在前 (脚功能串), IC 行在后 (器件身份) ⇒ 必须取 IC 行
    fixture = [
        {"ref": "ZZZ", "value": "脚功能串 (pin2)", "type": "NET", "net": "N1"},
        {"ref": "ZZZ", "value": "PART-NAME-123", "type": "IC", "net": "N2"},
    ]
    got = fn(fixture)
    if got.get("ZZZ") != "PART-NAME-123":
        res["ok"] = False
        res["lines"].append("     ❌ 行为: 合成样例应取到 'PART-NAME-123' ⇒ 实得 %r"
                            % got.get("ZZZ"))
    else:
        res["lines"].append("     行为: 合成样例 (NET 行在前 / IC 行在后) ⇒ 取到器件身份 ✔")

    rows = load_netlist_rows(netlist_path)
    real = fn(rows)
    v = (real.get(BOARD_VALUE_REF) or "")
    if BOARD_VALUE_MUST_CONTAIN not in v:
        res["ok"] = False
        res["lines"].append("     ❌ 行为: 真盘 %s 取到 %r ⇒ 不含 '%s'"
                            % (BOARD_VALUE_REF, v[:60], BOARD_VALUE_MUST_CONTAIN))
    elif BOARD_VALUE_MUST_NOT_CONTAIN in v:
        res["ok"] = False
        res["lines"].append("     ❌ 行为: 真盘 %s 取到的是脚功能串 (%r)" % (BOARD_VALUE_REF, v[:60]))
    else:
        res["lines"].append("     行为: 真盘 %s ⇒ %r ✔ (含型号串, 不是脚功能串)"
                            % (BOARD_VALUE_REF, v[:60]))
    return res


def check_C4(gen_path: str):
    """★C4 防手滑闸: 覆盖正式板必须显式 PCB_ALLOW_OFFICIAL=1"""
    res = {"ok": True, "lines": []}
    src = read_text(gen_path)
    need = ("PCB_ALLOW_OFFICIAL", "demo_mainboard.kicad_pcb")
    miss = [t for t in need if t not in src]
    if miss:
        res["ok"] = False
        res["lines"].append("     ❌ 生成器里找不到 %s ⇒ 裸跑生成器可覆盖正式板 ⇒ 红" % miss)
    else:
        res["lines"].append("     静态: 正式板路径 + PCB_ALLOW_OFFICIAL 闸都在")
    return res


def evaluate(gen_path: str, board_path: str, netlist_path: str):
    """★主判据 (★返回一个 (ok, 明细行) ★)"""
    lines = []
    ok = True
    for cid, fn in (
        ("C1", lambda: check_C1(gen_path, board_path)),
        ("C2", lambda: check_C2(gen_path, netlist_path)),
        ("C3", lambda: check_C3(gen_path, netlist_path)),
        ("C4", lambda: check_C4(gen_path)),
    ):
        r = fn()
        lines.append("  %s  %s" % ("OK " if r["ok"] else "FAIL", cid))
        lines.extend(r["lines"])
        ok = ok and r["ok"]
    return ok, lines


# ==============================================================================
# --selftest: 反向用例 (★每条都自证「真的改到了目标」 ★)
# ==============================================================================
def _mutate(src: str, old: str, new: str, tag: str) -> str:
    if old not in src:
        raise SystemExit("[selftest] 变异点找不到: %s (★闸自己改了源码 ⇒ 修用例 ★)" % tag)
    return src.replace(old, new, 1)


def run_selftest(gen_path: str, board_path: str, netlist_path: str) -> int:
    cases = []

    tmpd = tempfile.mkdtemp(prefix="iss269_selftest_")
    try:
        gen_src = read_text(gen_path)

        # ---- ① 默认层数改回 6 ⇒ 必须红 ----
        g1 = os.path.join(tmpd, "gen_layers6.py")
        src1 = _mutate(gen_src, 'os.environ.get("PCB_LAYERS", 8)', 'os.environ.get("PCB_LAYERS", 6)', "layer")
        open(g1, "w", encoding="utf-8").write(src1)
        ok, _ = evaluate(g1, board_path, netlist_path)
        cases.append(("① 默认层数 8 → 6", src1 != gen_src, ok is False))

        # ---- ② 删掉 DNP 三件套 ⇒ 必须红 ----
        g2 = os.path.join(tmpd, "gen_nodnp.py")
        src2 = _mutate(gen_src, "pcbnew.FP_DNP", "pcbnew.FP_NOTHING", "dnp")
        open(g2, "w", encoding="utf-8").write(src2)
        ok, _ = evaluate(g2, board_path, netlist_path)
        cases.append(("② DNP 三件套被删", src2 != gen_src, ok is False))

        # ---- ③ 取值规则退回「首见第一行」⇒ 必须红 ----
        g3 = os.path.join(tmpd, "gen_firstrow.py")
        src3 = _mutate(gen_src,
                       'if typ not in ("NET", "") and ref not in value_body:',
                       'if False and ref not in value_body:',
                       "valuerule")
        open(g3, "w", encoding="utf-8").write(src3)
        ok, _ = evaluate(g3, board_path, netlist_path)
        cases.append(("③ Value 退回首见第一行", src3 != gen_src, ok is False))

        # ---- ④ 盘上板被改成 7 层 ⇒ 必须红 (★证明 C1 真的在读盘上板 ★) ----
        b1 = os.path.join(tmpd, "board7.kicad_pcb")
        btxt = read_text(board_path)
        mt = re.search(r'\(\d+\s+"In6\.Cu"\s+signal\)', btxt)
        if not mt:
            print("  ❌ 板文件里找不到 In6.Cu 行 ⇒ 用例④写错了")
            cases.append(("④ 盘上板改 7 层", False, False))
        else:
            bt2 = btxt[:mt.start()] + "" + btxt[mt.end():]
            open(b1, "w", encoding="utf-8").write(bt2)
            ok, _ = evaluate(gen_path, b1, netlist_path)
            cases.append(("④ 盘上板 8 → 7 层", bt2 != btxt, ok is False))

        # ---- ⑤ 闸自身判据被削弱 (EXPECTED_LAYERS 8 → 6) ⇒ 必须红 ----
        #   ★这一条证明 C1 不是「自己跟自己比」⇒ 它真的绑在盘上板的真实层数上 ★
        self_src = read_text(os.path.abspath(__file__))
        gate2 = os.path.join(tmpd, "gate_weakened.py")
        gsrc2 = _mutate(self_src, "EXPECTED_LAYERS = 8", "EXPECTED_LAYERS = 6", "gate")
        open(gate2, "w", encoding="utf-8").write(gsrc2)
        r = subprocess.run([sys.executable, gate2, "--gen", gen_path,
                            "--board", board_path, "--netlist", netlist_path],
                           cwd=PROJ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ok2 = (r.returncode != 0)
        cases.append(("⑤ 闸自身 EXPECTED_LAYERS 8 → 6", gsrc2 != self_src, ok2))

        # ---- ⑥ 网表里 DNP 列被抽掉 ⇒ 必须红 (★证明 C2 真的在读网表 ★) ----
        n1 = os.path.join(tmpd, "netlist_nodnp.csv")
        rows = load_netlist_rows(netlist_path)
        for r_ in rows:
            r_["dnp"] = "必装"
        with open(n1, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        ok, _ = evaluate(gen_path, board_path, n1)
        cases.append(("⑥ 网表 DNP 列全改成必装", True, ok is False))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("=" * 76)
    print("  ISS-269 · 反向用例 (★每条都自证「真的改到了目标」 ★)")
    print("=" * 76)
    bad = 0
    for name, mutated, caught in cases:
        mark = "✔" if (mutated and caught) else "✘"
        if not (mutated and caught):
            bad += 1
        print("  %s  %-34s  变异生效=%s · 闸抓到=%s" % (mark, name, mutated, caught))
    print("-" * 76)
    print("  反向用例 %d/%d 通过" % (len(cases) - bad, len(cases)))
    if bad:
        print("  ❌ 有反向用例没抓到 ⇒ 闸不是判据 (或用例本身写错了)")
        return 1
    print("  ✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没 ★)")
    return 0


# ==============================================================================
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--gen", default=GEN_DEFAULT)
    ap.add_argument("--board", default=BOARD_DEFAULT)
    ap.add_argument("--netlist", default=NETLIST_DEFAULT)
    args = ap.parse_args()

    for p in (args.gen, args.board, args.netlist):
        if not os.path.exists(p):
            print("❌ 用法错: 找不到 %s" % p)
            return 2

    if args.selftest:
        return run_selftest(args.gen, args.board, args.netlist)

    print("=" * 76)
    print("  ISS-269 · 板生成器默认值闸 (★X-3 层数 / X-4 DNP / B-2 Value / 防手滑 ★)")
    print("=" * 76)
    ok, lines = evaluate(args.gen, args.board, args.netlist)
    for l in lines:
        print(l)
    print("-" * 76)
    if ok:
        print("  ✅ rc=0: ★★生成器三条默认值都钉死了 (★板只改一次那一趟的前置齐了 ★)★★")
        return 0
    print("  ❌ rc=1: ★★有生成器默认值没钉死 ⇒ 板那一趟会白做 ★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
