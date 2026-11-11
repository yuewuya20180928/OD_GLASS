#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日巡检 (Daily Check) —— 一次跑完 4 个门, 并自动检测"状态漂移"
================================================================================
老板 10-25 12:01: "后继出现问题的时候如何确认?"

确认问题不能靠"我每天想起来看一眼"。本脚本把巡检变成一个**可复现的固定动作**:
  1. 跑 merge.py       → 刷新 STATE.yaml (rc: 0完整 / 2不完整 / 1崩)
  2. 跑 gate_check.py  → 交付质量 5 道门 (Q1..Q5)
  3. 跑 issue_check.py → 问题闭环门 (字段/状态机/验证分离/逾期/双向覆盖)
  4. 跑 stage_gate.py  → 阶段门 (当前在第几关, 缺什么)
  5. ★漂移检测★        与上一次快照逐项比 —— 指标掉了 / 新增高危 / 问题被"忘记" → 报警

漂移是"问题出现"最可靠的信号: 没人会主动说自己变差了, 但数字会。

用法:  python3 state/daily_check.py [--no-snapshot]
退出码: 0=一切正常  1=有违规或漂移  2=脚本/文件错
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SNAP = os.path.join(HERE, "gate_snapshots")
PY = sys.executable


def _clean_env() -> dict:
    """★**干净的子进程环境** (★2026-11-06 22:2x, ★兄弟实测挖到的根因)

    ★★**根因不是"解释器路径", 是"继承污染的环境变量"**:
      `state/pcbnew_py.sh` 导出了 `PYTHONPATH=/home/yuewuya/kicad/squashfs-root/usr/lib/python3/dist-packages:...`
      ⇒ ★**这个 PYTHONPATH 会被子进程继承**
      ⇒ ★**即使用对了 `/usr/bin/python3`, 它启动时仍去 KiCad 的 dist-packages 找 `encodings`**
      ⇒ ★**⇒ `Fatal Python error: Failed to import encodings module` ⇒ `<no Python frame>`**
    ⇒ ★**所以: 只修"用哪个解释器"不够, ★**必须把这两个变量从子进程环境里剥掉****
    """
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    return env


def run(script: str, *args: str) -> tuple[int, str, str]:
    # ★**显式系统 python3 + 剥掉 PYTHONPATH/PYTHONHOME** (★见 _clean_env 的根因说明)
    #   ★**"只用 which 修解释器"是不够的 ⇒ 继承污染的环境变量才是真凶**
    import shutil as _sh
    _py = _sh.which("python3") or "/usr/bin/python3"
    p = subprocess.run([_py, os.path.join(HERE, script), *args],
                       capture_output=True, text=True, cwd=PROJ, env=_clean_env())
    return p.returncode, p.stdout, p.stderr


def run_sh(script: str, *args: str) -> tuple[int, str, str]:
    """★pcbnew 脚本必须走 state/pcbnew_py.sh (AppImage 自带 python3.11) ——
    系统 python3.14 没有 pcbnew ⇒ 直接跑会 ModuleNotFoundError ⇒ ★**门禁会静默失效**"""
    p = subprocess.run(["bash", os.path.join(HERE, "pcbnew_py.sh"),
                        os.path.join(HERE, script), *args],
                       capture_output=True, text=True, cwd=PROJ)
    return p.returncode, p.stdout, p.stderr


def run_sys(script: str, *args: str) -> tuple[int, str, str]:
    """★**用系统 python3 跑** (★`pcbnew_py.sh` 的 KiCad python3.11 **没装 yaml**
       ⇒ ★*decision_truth* / *compare_arm_official* 的自测必须走这个 ⇒ 走错必 ModuleNotFoundError)"""
    # ★★2026-11-06 21:4x (★兄弟 21:2x 的低危尾巴): ★**别用 sys.executable** (★它继承启动者的 python
    #   ⇒ ★**若有人用 pcbnew_py.sh 跑 daily_check ⇒ KiCad python 没 yaml ⇒ 两个自测全 ModuleNotFoundError
    #   ⇒ ★**且"需求闭环"整行变 None/None ⇒ 满屏假警**)
    #   ⇒ ★**这里显式找系统 python3** ⇒ 无论谁跑都对
    import shutil as _sh
    _py = _sh.which("python3") or "/usr/bin/python3"
    p = subprocess.run([_py, "-B", os.path.join(HERE, script), *args],
                       capture_output=True, text=True, cwd=PROJ, env=_clean_env())
    return p.returncode, p.stdout, p.stderr


def jrun(script: str) -> tuple[int, dict | None]:
    rc, out, err = run(script, "--json")
    try:
        return rc, json.loads(out)
    except Exception:  # noqa: BLE001
        return rc, None


def _selftest_ok(rc: int, out: str) -> bool:
    """★**自测判据 (★抽成纯函数 ⇒ 可被断言 ⇒ 判据退化时会被抓住)**

    ★★**为什么必须带"输出行数 > 0"** (★2026-11-07 00:2x, ★兄弟用回退实验实测):
      ★**若只看 rc**: ★**自测脚本被改成"什么都不打印 + exit 0" ⇒ rc=0 ⇒ 判据说 PASS**
      ⇒ ★★**⇒ 整条决策口径护栏静默失效, 而老板看到的还是 "✅ 全过"**
      ⇒ ★**⇒ 这条判据的"反向验证用例"就固化在 `--self-test` 里 (★见 selftest())**
    """
    return (rc == 0) and len((out or "").strip().splitlines()) > 0


GUARD_TESTS = (
    ("_test_edge_strict.py", "板边 fail-closed 守卫 (★自造违规铜 + 实测坏案例交叉验证★)"),
    ("_test_meander_edge.py", "蛇形出板闸守卫 (★PCB_MEANDER_EDGE★)"),
    ("_test_merge_fix.py", "共线合并瞬移守卫 (★PCB_MERGE_FIX★)"),
    ("_test_gnd_orphan.py", "GND 孤儿铜守卫 (★PCB_GND_ORPHAN_FIX★)"),
    ("_test_esc_clr.py", "出脚离网格段净距守卫 (★PCB_ESC_CLR_FIX★)"),
    ("_test_rownorm2.py", "排法线约束生效守卫 (★PCB_ESC_ROWNORM2★)"),
    ("_test_corridor.py", "走廊让路守卫 (★PCB_CORRIDOR_YIELD★)"),
    ("_test_layersel.py", "差分层选择守卫 (★PCB_PAIR_LAYERSEL★)"),
    ("_test_yield.py", "预测性让路守卫 (★PCB_YIELD_STRAIGHT★)"),
    ("_test_yield2.py", "窄版预测性让路守卫 (★PCB_YIELD_VICTIMS + 真实2D净距★)"),
    ("_test_clrfix.py", "边际净距修复守卫 (★收窄走线 + 差分腿/过孔护栏★)"),
    ("_lint_arm_env.py", "臂脚本 env 变量名守卫 (★★防【注释写进 env 块⇒变量根本没生效】★★)"),
)


def _run_guard_tests() -> list[str]:
    """★★**把三个守卫脚本接进自测段** (★2026-11-10 11:2x 新增★)

    ★★**判据**: ★**rc == 0 ★且★ stdout 非空** (★复用 `_selftest_ok`★)
      ⇒ ★★**守卫脚本被改成"什么都不打印 + exit 0" ⇒ 照样被判不合格** ★★
    """
    fails: list[str] = []
    for script, desc in GUARD_TESTS:
        path = os.path.join(HERE, script)
        if not os.path.exists(path):
            fails.append("★守卫脚本不存在: %s" % script)
            print("❌ 守卫 %s (%s) —— ★文件不存在★" % (script, desc))
            continue
        rc, out, err = run_sh(script)
        ok = _selftest_ok(rc, out)
        n = len((out or "").strip().splitlines())
        print("%s 守卫 %s (%s) rc=%s (输出 %d 行)"
              % ("✅" if ok else "❌", script, desc, rc, n))
        if not ok:
            tail = [x for x in ((err or "") + "\n" + (out or "")).strip().splitlines() if x.strip()]
            fails.append("★守卫 %s (%s) 未过 (rc=%s, 输出 %d 行): %s"
                         % (script, desc, rc, n, " | ".join(tail[-3:])[:300]))
    return fails


def selftest(full: bool = True) -> int:
    """★**daily_check 自己的自测 (★★它是巡检链的一节 ⇒ 必须有下一节来验它)**

    ★★**`full=True` (★`--self-test`★)**: ★**轻量判据自测 + ★三个守卫脚本 (★重的★)** ★★
    ★★**`full=False` (★`--self-test-fast`★)**: ★**只跑轻量判据自测** ★★
       ⇒ ★★**给"正常巡检段"用 (★别把重自测塞进每次巡检★)** ★★
    """
    fails = []
    # ① ★**核心反向用例: 空壳自测 (rc=0 · 输出 0 行) 必须判不合格**
    if _selftest_ok(0, ""):
        fails.append("★★**空壳自测 (rc=0 · 输出 0 行) 被判 PASS ⇒ 判据退化了!**")
    # ② 正常自测 (rc=0 · 有输出) 必须判合格
    if not _selftest_ok(0, "✔ 一行输出\n"):
        fails.append("★**正常自测被判不合格 ⇒ 判据过严**")
    # ③ ★**对照: 旧判据 (只看 rc) 在空壳场景下会假 PASS ⇒ 这就是本用例要防的东西**
    old_verdict = (0 == 0)
    if not old_verdict:
        fails.append("★**对照失效: 旧判据居然没放行空壳 ⇒ 对照口径不对**")
    # ④ rc 非 0 一律不合格 (无论有没有输出)
    if _selftest_ok(1, "有输出\n"):
        fails.append("★**rc≠0 却被判合格 ⇒ 判据有洞**")
    # ⑤ ★★**2026-11-10 11:2x 【★把三个守卫脚本接进自测 (★原来零个真实调用点 ⇒ "回归钉住"只是手工跑★)】★★ ★★
    #   ★★**为什么必须接**: ★**"守卫写好了但没人调用" = "裸奔"** ⇒ ★**跟项目铁律"闸脚本自己要有人拦"同一个病** ★★
    #   ★★**接了之后**: ★**任一守卫失败 ⇒ `daily_check.py --self-test` 必须 rc≠0** ★★
    if full:
        fails.extend(_run_guard_tests())
    for f in fails:
        print("   ★ %s" % f)
    if fails:
        print("★daily_check --self-test 未过 (%d 项)" % len(fails))
        return 1
    print("✔ daily_check --self-test 全过 (★含'空壳自测必须被判不合格'这条反向用例)")
    if full:
        print("✔ 三个守卫脚本全过 (★板边 fail-closed / 蛇形出板闸 / 共线合并瞬移★)")
    print("★★**判断标准只有一条 (★兄弟给的)**: ★**把判据改回去, 有没有东西会红? 不会 ⇒ 这条判据裸奔**")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-snapshot", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="★全量自测 (★轻量判据 + ★三个守卫脚本★) ⇒ 任一失败 rc≠0★")
    ap.add_argument("--self-test-fast", action="store_true",
                    help="★只跑轻量判据自测 (★不跑三个守卫 ⇒ 正常巡检段不受重自测拖累★)")
    args = ap.parse_args()
    if args.self_test:
        return selftest(full=True)
    if args.self_test_fast:
        return selftest(full=False)

    problems: list[str] = []

    # ★★★2026-11-07 00:3x 【自测接进"它自己的调用链"】(★兄弟 00:2x 建议:
    #   ★**"再把 daily_check 的 --self-test 接进 chain_gate 或它自己的调用链"**)
    #   ★**为什么必须接自己的链**: ★**daily_check 是巡检链的一节 ⇒ 必须有下一节来验它**
    #   ⇒ ★**否则"判据退化 ⇒ 静默 PASS"这条路没人拦**
    #   ⇒ ★**注意别重蹈"自测接进巡检、但巡检自己没自测"的循环** ⇒ ★**现在这一环也接上了**
    _rc_self, _out_self, _err_self = run_sys("daily_check.py", "--self-test-fast")
    if _rc_self != 0:
        problems.append("★daily_check --self-test-fast 未过 (★判据退化? ★详见 stdout): "
                        + ((_out_self or _err_self).strip().splitlines()[-1][:160]
                           if (_out_self or _err_self).strip() else ""))
    print(f"{'✅' if _rc_self == 0 else '❌'} daily_check --self-test-fast rc={_rc_self} "
          f"(★判据退化守卫★ · ★★三个守卫脚本只在 `--self-test` 跑 ⇒ 巡检段不受重自测拖累★★)")

    # ★★★★**★2026-11-11 01:5x 【★分析工具的【可用性自检】接进巡检 (★不是判据守卫·是"工具别悄悄坏掉"★)】★★★★ ★
    #   ★**为什么必须有**: ★**"守卫写好了但没人调用" = "裸奔"** ⇒ ★**同一条铁律·换个对象** ★★
    #     ★★**⇒ 分析工具坏掉时【不会自己报错】(★它只是给出错数字★) ⇒ ⇒ 必须有地方检查它还能用** ★★
    #   ★**为什么只查【--check-env】不查【全流程】**: ★★**全流程要跑 DRC (★分钟级★) ⇒ ⇒ 不能塞进每次巡检** ★★
    #   ★**⇒ 只做"能启动 + 能列出板 + 工程文件齐"这种【秒级】体检★★
    _tools = ("arm_reading_guard.py", "arm_ranking.py", "probe_start_cell.py", "probe_escape_block.py",
              "gate_live_check.py")
    for _t in _tools:
        _p = os.path.join(HERE, _t)
        if not os.path.exists(_p):
            problems.append("★分析工具缺失: %s" % _t)
            continue
        try:
            with open(_p, "r", encoding="utf-8") as _f:
                compile(_f.read(), _p, "exec")
        except Exception as _e:
            problems.append("★分析工具语法错: %s (%s)" % (_t, str(_e)[:120]))
    # ★★**工程文件同源体检 (★缺 .kicad_pro ⇒ DRC 读数作废★·实测假违规 87 条★)** ★★
    _b = HERE + "/.lastgood/baseline_v76mv0_chain.kicad_pcb"
    if os.path.exists(_b):
        _pro = _b[:-len(".kicad_pcb")] + ".kicad_pro"
        if not os.path.exists(_pro):
            problems.append("★基线板旁缺 .kicad_pro ⇒ fresh DRC 读数作废 (★实测假 track_width 87 条★)")
    print(f"{'✅' if not problems else '⚠️'} 分析工具体检 ({len(_tools)} 个·秒级·语法+工程文件同源)")

    # 1) merge
    rc_m, out_m, err_m = run("merge.py")
    if rc_m not in (0, 2):
        problems.append(f"merge.py 崩溃 rc={rc_m}: {err_m.strip()[:200]}")
    elif rc_m == 2:
        problems.append("merge.py 返回 2 → 快照不完整 (有分片读失败, 已回退 .lastgood)")

    # ★★2026-11-06 21:1x 【自测接进巡检】(★兄弟指出: 两个 --self-test 都没人调用
    #   ⇒ "只在人记得手跑时才生效" ⇒ ★**跟 MEMORY 铁律"闸脚本自己要有人拦"同一个病**)
    #   ⇒ ★**decision_truth** = 老板决策口径的唯一真源 + 三处消费者的护栏
    #   ⇒ ★**compare_arm_official** = 晋级闸 (逐网孤岛名单) 的护栏
    rc_dt, out_dt, err_dt = run_sys("decision_truth.py", "--self-test")
    # ★★★2026-11-06 23:4x (★兄弟 23:1x 用我自己的 #135 查出来的真缺口):
    #   ★**① 只判 rc 不判 stdout 非空** ⇒ ★**若自测被改成"什么都不打印 + exit 0" ⇒ daily_check 静默 PASS**
    #     ⇒ ★**⇒ 判据: rc == 0 ★且★ stdout 非空** (★这正是 #135 的"它真的吐出了要检查的东西")
    dt_out_n = len((out_dt or "").strip().splitlines())
    dt_ok = _selftest_ok(rc_dt, out_dt)
    rc_ao, out_ao, err_ao = run_sys("compare_arm_official.py", "--self-test")
    ao_out_n = len((out_ao or "").strip().splitlines())
    ao_ok = _selftest_ok(rc_ao, out_ao)
    # ★★2026-11-11 08:5x 【新闸也要被守卫 (★承"守卫者也要被守卫"那条★)】★★
    #   ★**margin_sweep_gate** = ★**"unc 变少 ≠ 板子更好" 的机器闸** (★判据仍是名单制·唯一实现★)
    #   ⇒ ★**它的自测也必须挂在巡检上 ⇒ 不许只靠人记得手跑★**
    #   ★★**只跑 --self-test-fast (★纯函数那三条·不跑 fresh DRC·不拖慢巡检★)★★
    rc_mg, out_mg, err_mg = run_sys("margin_sweep_gate.py", "--self-test-fast")
    mg_out_n = len((out_mg or "").strip().splitlines())
    mg_ok = _selftest_ok(rc_mg, out_mg)
    # ★★2026-11-11 10:2x 【★原理图 ERC 闸也要被守卫 + 进巡检 (★老板 10:07 把主线切到原理图后的第一道闸★)】★★
    #   ★**check_sch_erc.py** = ★**原理图 ERC=0 的机器闸 (★此前从未跑过 ERC ⇒ 46 条 label_dangling 全盲★)**
    #   ⇒ ★**守卫者也要被守卫** ⇒ 它的自测也挂到巡检上 (★只跑 --self-test·不带 e2e ⇒ 不拖慢巡检★)**
    rc_erc, out_erc, err_erc = run_sys("check_sch_erc.py", "--self-test")
    erc_out_n = len((out_erc or "").strip().splitlines())
    erc_ok = _selftest_ok(rc_erc, out_erc)

    # 2) gate
    rc_g, gate = jrun("gate_check.py")
    # 3) issue
    rc_i, issue = jrun("issue_check.py")
    # 4) stage
    rc_s, stage = jrun("stage_gate.py")
    rc_r, ready = jrun("readiness.py")
    # ★2026-11-02 22:5x: PCB 图纸门禁进门禁链 (自己画的图自己验; EN 那个 P0 的教训)
    rc_pcb_rc, out_p, err_p = run("check_pcb_drc.py")
    pcb_ok = (rc_pcb_rc == 0)
    # ★PCB ↔ 网表 等价性 (板子由网表生成 ⇒ 必须逐点相等)
    # ★2026-11-04 19:4x 修: 原来用系统 python 跑 (pcbnew 不存在 ⇒ rc 必失败),
    #   而且算出来的 pcb_ok / pcb_net_ok **是死变量, 从没进过 problems** ⇒ 门禁形同虚设
    rc_pn, out_pn, err_pn = run_sh("check_pcb_nets.py")
    pcb_net_ok = (rc_pn == 0)
    # ★生产链准入/准出 (网表→原理图→PCB→BOM→投产包, 环节之间)
    rc_cg, out_cg, err_cg = run("chain_gate.py")
    chain_ok = (rc_cg == 0)

    # ★★2026-11-06 23:4x: ★**两个自测通过时也要打印可见行** (★原先"静默通过" ⇒ 掉线了报告看不出来)
    print(f"{'✅' if dt_ok else '❌'} decision_truth --self-test rc={rc_dt} (输出 {dt_out_n} 行)")
    print(f"{'✅' if ao_ok else '❌'} compare_arm_official --self-test rc={rc_ao} (输出 {ao_out_n} 行)")
    print(f"{'✅' if mg_ok else '❌'} margin_sweep_gate --self-test-fast rc={rc_mg} (输出 {mg_out_n} 行)")
    print(f"{'✅' if erc_ok else '❌'} check_sch_erc --self-test rc={rc_erc} (输出 {erc_out_n} 行)")
    if not erc_ok:
        problems.append(f"★check_sch_erc --self-test 没过 (rc={rc_erc}, 输出 {erc_out_n} 行): "
                        f"{(err_erc or out_erc).strip().splitlines()[-1][:160] if (err_erc or out_erc).strip() else ''}")
    if not mg_ok:
        problems.append(f"★margin_sweep_gate --self-test-fast 没过 (rc={rc_mg}, 输出 {mg_out_n} 行): "
                        f"{(err_mg or out_mg).strip().splitlines()[-1][:160] if (err_mg or out_mg).strip() else ''}")
    if not dt_ok:
        problems.append(f"★decision_truth --self-test 没过 (rc={rc_dt}, 输出 {dt_out_n} 行): "
                        f"{(err_dt or out_dt).strip().splitlines()[-1][:160] if (err_dt or out_dt).strip() else ''}")
    if not ao_ok:
        problems.append(f"★compare_arm_official --self-test 没过 (rc={rc_ao}, 输出 {ao_out_n} 行): "
                        f"{(err_ao or out_ao).strip().splitlines()[-1][:160] if (err_ao or out_ao).strip() else ''}")
    if gate is None:
        problems.append("gate_check.py 输出无法解析")
    if issue is None:
        problems.append("issue_check.py 输出无法解析")
    if stage is None:
        problems.append("stage_gate.py 输出无法解析")
    if rc_i == 1:
        problems.append(f"问题闭环门有违规 {len((issue or {}).get('errors') or [])} 条")
    if not pcb_ok:
        problems.append(f"★PCB 图纸门禁没过 (check_pcb_drc rc={rc_pcb_rc})")
    if not pcb_net_ok:
        problems.append(f"★PCB↔网表逐焊盘等价没过 (check_pcb_nets rc={rc_pn}) —— 板子与网表不一致, 不许投板")
    if not chain_ok:
        problems.append("★生产链准入/准出没过 (chain_gate) —— 有环节的产物比源旧或缺件, 下游产物不许用")
    if gate and gate.get("summary", {}).get("reconciliation", {}).get("ok") is False:
        problems.append("gate 与 merge 口径不一致 (先重跑 merge.py)")

    # 5) 漂移检测
    os.makedirs(SNAP, exist_ok=True)
    snaps = sorted(f for f in os.listdir(SNAP) if f.endswith(".json"))
    # ★★2026-11-11 00:3x 实测修: ★**基线不能取【今天自己的快照】★★
    #   ★**实测缺陷 (★反向验证: 人为把今天的 blocks_ok 改成 5 再跑 ⇒ 漂移检测仍报"无漂移"★)**:
    #     原来 `snaps[-1]` ⇒ ★**同一天第二次跑时, snaps[-1] 就是今天自己刚写的那个文件**
    #     ⇒ ⇒ 拿【自己】当基线 ⇒ ★**指标掉多少都测不出来** ⇒ ★**这道闸在一天里跑第二次以上就瞎了** ★★
    #     ⇒ ★★**与 MEMORY 铁律「恒为 0 的指标比没有指标更危险」同一个病 (这里是"恒不报的漂移检测")**★★
    #   ★**修法**: 基线取**今天之前**最新的一份 ⇒ ★**同一天跑几次都拿同一个真基线** ⇒ ★**漂移每次都能测出来**
    #     (★今天第一次跑时本来就没有今天的文件 ⇒ 行为不变; 今天是第 N 次跑 ⇒ 基线仍是昨天/上一次的那份★)
    import datetime as _dt
    _today = _dt.date.today().isoformat()
    _prior = [s for s in snaps if not s.startswith(_today)]
    _baseline_name = _prior[-1] if _prior else None
    prev = None
    if _baseline_name:
        try:
            with open(os.path.join(SNAP, _baseline_name), encoding="utf-8") as f:
                prev = json.load(f)
        except Exception:  # noqa: BLE001
            prev = None

    ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    cur = {
        "readiness": {k: v for k, v in (ready or {}).items() if k != "criteria"},
        "gate": (gate or {}).get("summary", {}),
        "issues": {k: v for k, v in (issue or {}).items() if k != "issues"},
        "stage": {k: v for k, v in (stage or {}).items() if k != "results"},
    }
    drift: list[str] = []
    if prev:
        pg, pi = prev.get("gate", {}), prev.get("issues", {})
        cg, ci = cur["gate"], cur["issues"]
        # 齐备率掉了
        if cg.get("blocks_ok") is not None and pg.get("blocks_ok") is not None and cg["blocks_ok"] < pg["blocks_ok"]:
            drift.append(f"★Q1 齐备率下降: {pg['blocks_ok']}/{pg.get('blocks_total')} → {cg['blocks_ok']}/{cg.get('blocks_total')}")
        # 内部未闭合变多
        if (cg.get("global_pending") or 0) > (pg.get("global_pending") or 0):
            drift.append(f"★内部未闭合增加: {pg.get('global_pending')} → {cg.get('global_pending')}")
        # 问题单数量增加
        if (ci.get("total") or 0) > (pi.get("total") or 0):
            drift.append(f"★问题单增加: {pi.get('total')} → {ci.get('total')}")
        # 逾期
        if (ci.get("overdue") or 0) > (pi.get("overdue") or 0):
            drift.append(f"★逾期问题增加: {pi.get('overdue')} → {ci.get('overdue')}")
        # 未闭环 blocker
        cb = sum(1 for x in (issue or {}).get("issues", [])
                 if x.get("severity") == "blocker" and x.get("status") not in ("closed", "deferred", "wontfix"))
        drift.append(f"  (未闭环 blocker: {cb} 条)")

    # ★ 人读摘要 (投递通知不可靠时的兜底: 结论落盘, 随时可查, 也会随 GitHub 同步)
    if not args.no_snapshot:
        dig = [
            f"# 每日状态摘要 ({ts})", "",
            "> 自动生成 (源: `state/daily_check.py`) | 微信推送不可靠时的兜底 —— 结论永远落在这里",
            "", "```",
        ]
        _st = cur.get("stage") or {}
        _gt = cur.get("gate") or {}
        _is = cur.get("issues") or {}
        _rd = cur.get("readiness") or {}
        dig.append(f"阶段门      {_st.get('current_gate')}  (已过 {_st.get('passed_gates') or '无'})")
        dig.append(f"齐备率      {_gt.get('blocks_ok')}/{_gt.get('blocks_total')}")
        dig.append(f"需求闭环    问方 {_gt.get('needs_answered_incoming')}/{_gt.get('needs_total')} | 内部未闭合 {_gt.get('global_pending')} | 等外部 {_gt.get('global_waiting_external')}")
        dig.append(f"接口声明    {_gt.get('interface_claims_total') or _gt.get('interface_claims') or '?'} 条")
        dig.append(f"实测        {_rd.get('measurements',{}).get('have')}/{_rd.get('measurements',{}).get('needed')} 项")
        dig.append(f"问题单      {_is.get('total')} 条 (逾期 {_is.get('overdue')} | 违规 {len(_is.get('errors') or [])})")
        dig.append(f"就绪度      纸面 {'✅' if _rd.get('paper_ready') else '❌'} | 样机 {'✅' if _rd.get('sample_ready') else '❌'}")
        dig.append(f"生产链      准入/准出 {'✅ 全过' if chain_ok else '❌ 有环节没过'} | PCB图纸 {'✅' if pcb_ok else '❌'} | PCB↔网表 {'✅' if pcb_net_ok else '❌'}")
        dig.append(f"漂移        {'无 ✅' if not [d for d in drift if d.startswith('★')] else '有 ⚠️'}")
        dig.append("```")
        if problems:
            dig += ["", "## 异常", ""] + [f"- {x}" for x in problems]
        try:
            with open(os.path.join(HERE, "STATUS_DIGEST.md"), "w", encoding="utf-8") as f:
                f.write("\n".join(dig))
        except Exception:  # noqa: BLE001
            pass

    if not args.no_snapshot:
        import datetime as dt
        name = f"{dt.date.today().isoformat()}_daily.json"
        with open(os.path.join(SNAP, name), "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    # ---- 一屏报告 ----
    print("=" * 74)
    print("每日巡检 · Daily Check")
    print("=" * 74)
    g = cur["gate"]
    i = cur["issues"]
    s = cur["stage"]
    print(f"  merge          rc={rc_m} {'✅ 完整' if rc_m == 0 else '⚠️ 不完整'}")
    print(f"  交付齐备率     {g.get('blocks_ok')}/{g.get('blocks_total')}"
          f" | 证据分级 {g.get('evidence_ok_agents')}/{g.get('evidence_total_agents')}"
          f" | 接口声明 {g.get('interface_claims_total', g.get('interface_claims', '?'))} 条")
    print(f"  需求闭环       问方 {g.get('needs_answered_incoming')}/{g.get('needs_total')}"
          f" | 内部未闭合 {g.get('global_pending')} | 等外部 {g.get('global_waiting_external')}"
          f" | 对账 {'✅' if (g.get('reconciliation') or {}).get('ok') else '❌'}")
    print(f"  问题闭环门     {i.get('total')} 条 | 逾期 {i.get('overdue')}"
          f" | 内部 {i.get('internal')} / 外部 {i.get('external')} | 违规 {len(i.get('errors') or [])}")
    print(f"  阶段门         当前 **{s.get('current_gate')}** | 已过 {s.get('passed_gates')}")
    # ★★2026-11-11 10:2x 【★原理图 ERC 实况进巡检 (★主线切原理图后的第一道闸★)】★★
    #   ★**读 check_sch_erc.py 落的缓存 (★不每次重跑 ERC ⇒ 不拖慢巡检★); 缓存过期 ⇒ 标"数据过期"不许当现状★
    _erc_line = "  原理图 ERC      (无缓存 ⇒ 跑一次 `python3 state/check_sch_erc.py` 生成)"
    try:
        _cp = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".erc_last.json")
        _c = json.load(open(_cp, encoding="utf-8"))
        _sch = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "HW", "PCB", "demo_mainboard.kicad_sch")
        _stale = (os.path.exists(_sch) and _c.get("sch_mtime") and
                  abs(os.path.getmtime(_sch) - float(_c["sch_mtime"])) > 1)
        _n = int(_c.get("count", 0))
        if _stale:
            _erc_line = (f"  原理图 ERC      ⚠️ 数据过期 (原理图已改, 缓存测于 {_c.get('at')}) ⇒ 需重跑 check_sch_erc.py")
        else:
            _erc_line = (f"  原理图 ERC      {'✅ 0 条' if _n == 0 else f'❌ {_n} 条'} "
                         f"(实测 {_c.get('at')} · {(_c.get('by_type') or {})})")
            if _n > 0:
                problems.append(f"★原理图 ERC = {_n} 条 ({(_c.get('by_type') or {})}) ⇒ ★**原理图不许进投产包** (★新闸: state/check_sch_erc.py★)")
    except Exception as _e:
        _erc_line = f"  原理图 ERC      (读缓存失败: {_e})"
    print(_erc_line)
    r = cur.get("readiness") or {}
    print(f"  执行就绪度     纸面阶段 {'✅就绪' if r.get('paper_ready') else '❌未就绪'} | "
          f"样机阶段 {'✅就绪' if r.get('sample_ready') else '❌不就绪'} | "
          f"实测 {r.get('measurements',{}).get('have')}/{r.get('measurements',{}).get('needed')} 项")
    if prev:
        print(f"  漂移检测       {'无漂移 ✅' if not [d for d in drift if d.startswith('★')] else '有漂移 ⚠️'}")
        for d in drift:
            print(f"      {d}")
    else:
        print("  漂移检测       首次巡检 (无历史快照, 已建立基线)")
    if problems:
        print()
        print("❌ 异常:")
        for p in problems:
            print(f"   - {p}")
        # ★2026-10-29 00:2x 修: 退出码分级 —— 巡检**发现异常** (已记录) 与 **脚本崩溃** 必须分开。
        #   旧行为: 两种都 return 1 ⇒ publish_github.sh 的 gen() 把"巡检有异常"当成"生成器崩溃"
        #   ⇒ 中止整条发布 ⇒ **GitHub 同步静默卡了 5 小时** (远端停在 19:13 的 commit)。
        #   新行为: 异常 → **rc=3** (快照已生成, 文档照常可推); 崩溃 → rc=1/2 (真正该中止)。
        #   ⇒ 发布脚本的 gen() 对 rc ∈ {0,3} 视为成功。
        print()
        print(f"ℹ️ 巡检异常已记录 (快照已生成) —— 退出码 3 (不是崩溃, 发布不因此中止)")
        return 3
    print()
    print("✅ 巡检通过 (无违规 / 无漂移)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
