#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chain_gate.py —— ★生产链"环节之间"的**准入 / 准出**门禁 (2026-11-04 19:35 老板指示)

★**为什么必须有它 (当天实测踩了 3 次, 全是"环节之间没人把关")**:
  ① 11-04 19:2x **BOM 比网表旧 10 小时** (BOM 11-03 00:50 / 网表 11-04 10:04) ⇒ 备料口径对不上
     ⇒ **网表 → BOM 之间没有准出校验**
  ② 11-04 19:3x **板子比网表旧** (PCB 03:02 / 网表 10:04) ⇒ 投板用的板不是最新网表生成的板
     ⇒ **网表 → PCB 之间没有准入校验**
  ③ 原理图从 10-27 起 KiCad 就打不开 (少一个右括号 ⇒ 888 层不闭合) ⇒ 投产资料全导不出
     ⇒ **原理图 → 投产包 之间没有准出校验** (而且我们的"自检"只查语义, 不查工具能不能用)
⇒ ★**一句话**: ★**每个环节做完, 下一个环节开工前, 必须有机器判据证明"上一个环节的产物是新的、是对的、能用的"**

★**链条 (生产链)**: 网表 → 原理图 → PCB → BOM → 投产资料包
★**每环两道判据**:
  · **准入 (entry)**: 本环开工前 —— 上游产物存在 · **比上游源新** (mtime 新鲜度) · 上游准出已通过
  · **准出 (exit)**: 本环交付前 —— 本环的**机器门禁 rc=0** (只读脚本, 不许改文件)

用法:
  python3 state/chain_gate.py            # 快检 (秒级): 只查新鲜度 + 齐全性 ⇒ 可挂 daily_check
  python3 state/chain_gate.py --full     # 全检 (约 1~2 分钟): 额外真跑 KiCad/网表门禁
退出码: 0 = 全过; 1 = 有环节没过 (打印哪一环的准入/准出、为什么、怎么修)
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
FULL = "--full" in sys.argv

CSV = os.path.join(PROJ, "HW", "netlist_v1.csv")
# ★★ BOM 的**真源** = 脚级真值表 (★2026-11-11 20:2x: BOM 改成从脚级表按器件聚合★)
# ★★ (旧版 BOM 读的是导线级表 ⇒ 带着 75 个 RAIL_*/NET_* 伪器件 ⇒ 位号集合永不对★)
PINS_CSV = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
SCH = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_sch")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
BOM = os.path.join(PROJ, "HW", "BOM_v1.csv")
PROD = os.path.join(PROJ, "HW", "PCB", "production")

GEN_NETLIST = os.path.join(HERE, "gen_netlist.py")
GEN_SCH = os.path.join(HERE, "gen_kicad_sch.py")
GEN_PCB = os.path.join(HERE, "gen_pcb_netlist_board.py")
GEN_BOM = os.path.join(HERE, "gen_bom.py")

# ★投产包必备产物 (缺一不可)
PROD_REQUIRED = [
    ("Gerber (F/B/4 内层/阻焊/丝印/外形/粘贴)", "gerbers/demo_mainboard-F_Cu.gtl"),
    ("Gerber 内层 In1", "gerbers/demo_mainboard-In1_Cu.g1"),
    ("Gerber job 文件", "gerbers/demo_mainboard-job.gbrjob"),
    ("钻孔 PTH", "drill/demo_mainboard-PTH.drl"),
    ("钻孔 NPTH", "drill/demo_mainboard-NPTH.drl"),
    ("钻孔图 PDF", "drill/demo_mainboard-PTH-drl_map.pdf"),
    ("坐标文件 CPL", "pos/demo_mainboard-pos.csv"),
    ("装配 IPC-2581", "assembly/demo_mainboard-ipc2581.xml"),
    ("装配图 PDF (顶)", "assembly/demo_mainboard-assembly-top.pdf"),
    ("PCB 图 PDF (全层)", "doc/demo_mainboard-pcb-all.pdf"),
    ("3D 模型 STEP", "3d/demo_mainboard.step"),
    ("外形 DXF", "doc/demo_mainboard-Edge_Cuts.dxf"),
    ("裸板测试网表 D356", "doc/demo_mainboard.d356"),
    ("板统计", "doc/board-stats.txt"),
    ("★原理图 PDF", "doc/demo_mainboard-sch.pdf"),
    ("★原理图 SVG", "doc/sch_svg/demo_mainboard.svg"),
    ("★KiCad 原理图网表", "doc/demo_mainboard-kicad.net"),
    ("★KiCad BOM", "doc/demo_mainboard-kicad-bom.xml"),
    # ★★2026-11-11 11:0x (hw-lead): 投产包必须带**原理图源文件**, 不能只有 PDF/SVG
    #   ★为什么: PDF/SVG 是**渲染件** —— 板厂"能看不能改"; 真要改个脚位/阻值只能回我们这改 ⇒ 又一轮 2-4 周 + ¥4-8K
    #   ★而且 10 个子页 (demo_mainboard_p1..p10.kicad_sch) 只活在 HW/PCB/ 里 ⇒ 投产包里没人知道它们是原理图的一部分
    #   ★.kicad_pro **必带**: 封装库引用 / 设计规则(DRC+ERC) / 图纸设置 / 文本框参数 **全部只存在这一个文件里**
    #     ⇒ 丢了 .kicad_pro 就算 .kicad_sch 全在, 工程文件也是残废的 (开出来是默认规则)
    ("★原理图源文件 根页", "doc/sch_src/demo_mainboard.kicad_sch"),
    ("★原理图源文件 子页 P1", "doc/sch_src/demo_mainboard_p1.kicad_sch"),
    ("★原理图源文件 子页 P2", "doc/sch_src/demo_mainboard_p2.kicad_sch"),
    ("★原理图源文件 子页 P3", "doc/sch_src/demo_mainboard_p3.kicad_sch"),
    ("★原理图源文件 子页 P4", "doc/sch_src/demo_mainboard_p4.kicad_sch"),
    ("★原理图源文件 子页 P5", "doc/sch_src/demo_mainboard_p5.kicad_sch"),
    ("★原理图源文件 子页 P6", "doc/sch_src/demo_mainboard_p6.kicad_sch"),
    ("★原理图源文件 子页 P7", "doc/sch_src/demo_mainboard_p7.kicad_sch"),
    ("原理图源文件 子页 P8", "doc/sch_src/demo_mainboard_p8.kicad_sch"),
    ("原理图源文件 子页 P9", "doc/sch_src/demo_mainboard_p9.kicad_sch"),
    ("原理图源文件 子页 P10", "doc/sch_src/demo_mainboard_p10.kicad_sch"),
    ("★KiCad 工程文件 (.kicad_pro)", "doc/sch_src/demo_mainboard.kicad_pro"),
]

# ★★投产包里的原理图源文件目录 (2026-11-11 hw-lead)
SCH_SRC_DIR = os.path.join(PROD, "doc", "sch_src")
SCH_SRC_PRO = "demo_mainboard.kicad_pro"


def mt(p):
    try:
        return os.path.getmtime(p)
    except Exception:
        return 0.0


def run(cmd, timeout=900):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=PROJ)
        return r.returncode, (r.stdout + r.stderr)[-300:]
    except Exception as e:
        return 99, str(e)


def ts(p):
    t = mt(p)
    return time.strftime("%m-%d %H:%M", time.localtime(t)) if t else "(缺)"


def _md5(p):
    import hashlib
    try:
        with open(p, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def expected_sch_src_files():
    """★期望投产包 doc/sch_src/ 里的文件集合 = HW/PCB/ 下**全部** .kicad_sch + 主工程 .kicad_pro
    ★为什么动态算 (不写死 12 个): 新加了 p11 子页却没进投产包时, 门禁必须自己发现 (防"漏了新的")"""
    import glob
    sch_dir = os.path.join(PROJ, "HW", "PCB")
    names = set(os.path.basename(p) for p in glob.glob(os.path.join(sch_dir, "*.kicad_sch")))
    names.add(SCH_SRC_PRO)
    return names


def check_sch_src_pack():
    """★投产包里的原理图源文件 (2026-11-11) —— 只读校验
    ★判据: ① 目录在  ② 文件名集合与 HW/PCB/ **一一对应** (多一个少一个都红)
            ③ 每个文件内容 (md5) 与源文件**完全一致** (防"加了旧的")"""
    if not os.path.isdir(SCH_SRC_DIR):
        return False, ("doc/sch_src/ 不存在 ⇒ 投产包只有 PDF/SVG 渲染件, **没有可改的原理图源文件** "
                       "(板厂能看不能改) ⇒ 修法: cp -p HW/PCB/demo_mainboard*.kicad_sch "
                       "HW/PCB/demo_mainboard.kicad_pro HW/PCB/production/doc/sch_src/")
    have_all = set(os.listdir(SCH_SRC_DIR))
    have = set(f for f in have_all if os.path.isfile(os.path.join(SCH_SRC_DIR, f)))
    subdirs = sorted(have_all - have)
    exp = expected_sch_src_files()
    miss = sorted(exp - have)
    extra = sorted(have - exp)
    # 内容一致性 (防"加了旧的")
    bad = []
    for n in sorted(exp & have):
        src = os.path.join(PROJ, "HW", "PCB", n)
        dst = os.path.join(SCH_SRC_DIR, n)
        if not os.path.exists(src):
            continue
        if _md5(src) != _md5(dst):
            bad.append(n)
    prob = []
    if miss:
        prob.append(f"缺 {len(miss)} 个 (例 {miss[:3]})")
    if extra:
        prob.append(f"多 {len(extra)} 个 (例 {extra[:3]})")
    if bad:
        prob.append(f"内容与源不一致 {len(bad)} 个 (例 {bad[:3]})")
    if subdirs:
        prob.append(f"目录里还有子目录 {subdirs[:2]}")
    if prob:
        return False, ("原理图源文件与 HW/PCB/ **没有一一对应**: " + "; ".join(prob)
                       + " ⇒ 修法: 把 doc/sch_src/ 同步成 HW/PCB/ 下全部 .kicad_sch + " + SCH_SRC_PRO)
    return True, (f"{len(exp)} 个源文件齐全 · 与 HW/PCB/ 一一对应 · 内容 md5 全一致 "
                   f"({len([n for n in exp if n.endswith('.kicad_sch')])} 个 .kicad_sch + 1 个 .kicad_pro)")


def check_bom_against_netlist():
    """★只读校验 BOM 与**其真源**一致 (不许重生成 —— 门禁只读)

    ★★**口径 (2026-11-11 20:2x, ISS-193)**: BOM 现在由 `state/gen_bom.py` 从**脚级真值表**
    `HW/netlist_v1_pins.csv` **按器件聚合**生成 (★584 脚 ⇒ 218 器件 / 0 伪器件 / 含 J_SOM_P2+P4★)
    ⇒ 本校验的**对照源必须是同一张表**; 拿导线级表 `netlist_v1.csv` 比 ⇒ 必然报
    「网表有 BOM 没有 75 个 (伪位号)」+「BOM 有网表没有 2 个 (J_SOM_P2/P4)」= **假失败** ★
    ★★**DNP 口径 (ref 级)**: 该器件**所有脚**都标 DNP ⇒ 整器 DNP; 有任一必装 ⇒ 必装
    (★与 `state/gen_bom.py` 的聚合口径逐字一致★) ★
    """
    import csv as _csv
    try:
        rows = list(_csv.DictReader(open(PINS_CSV, encoding="utf-8")))
        brows = list(_csv.DictReader(open(BOM, encoding="utf-8")))
    except Exception as e:
        return False, f"读不了 PINS_CSV/BOM: {e}"
    by_ref = {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref:
            by_ref.setdefault(ref, set()).add((r.get("dnp") or "").strip().upper())
    net_all_dnp = {k for k, v in by_ref.items() if v == {"DNP"}}
    bom_refs = {(r.get("ref") or "").strip() for r in brows}
    net_refs = set(by_ref)
    missing = sorted(net_refs - bom_refs)
    extra = sorted(bom_refs - net_refs)
    bom_dnp = {r.get("ref") for r in brows if (r.get("dnp") or "") == "DNP"}
    dnp_mismatch = sorted(bom_dnp ^ net_all_dnp)
    # ★伪器件不得进物料表 (★评审 R12★)
    pseudo_in_bom = sorted(r for r in bom_refs if r.startswith("RAIL_") or r.startswith("NET_"))
    if missing or extra or dnp_mismatch or pseudo_in_bom:
        msg = []
        if missing:
            msg.append(f"真源有 BOM 没有 {len(missing)} 个 (例 {missing[:5]})")
        if extra:
            msg.append(f"BOM 有真源没有 {len(extra)} 个 (例 {extra[:5]})")
        if dnp_mismatch:
            msg.append(f"DNP 口径不一致 {len(dnp_mismatch)} 个 (例 {dnp_mismatch[:5]})")
        if pseudo_in_bom:
            msg.append(f"★伪器件混进物料表 {len(pseudo_in_bom)} 个 (★评审 R12★ 例 {pseudo_in_bom[:5]})")
        return False, "; ".join(msg)
    return True, (f"位号 {len(net_refs)} 个全对 (★脚级真源口径★) · DNP {len(net_all_dnp)} 个一致"
                  f" · 伪器件 0 个")


def main():
    print("=" * 78)
    print("生产链准入/准出门禁 · chain_gate "
          + ("(全检: 真跑 KiCad + 网表门禁)" if FULL else "(快检: 新鲜度 + 齐全性)"))
    print("=" * 78)
    fails = 0
    rows = []

    def stage(name, entry_ok, entry_msg, exit_ok, exit_msg):
        nonlocal fails
        if not entry_ok or not exit_ok:
            fails += 1
        rows.append((name, "✅" if entry_ok else "❌", entry_msg,
                     "✅" if exit_ok else "❌", exit_msg))

    # ---------- 环 1: 网表 ----------
    e1 = os.path.exists(CSV) and mt(CSV) >= mt(GEN_NETLIST) - 1
    e1m = f"产物 {ts(CSV)} vs 生成器 {ts(GEN_NETLIST)}"
    if not os.path.exists(CSV):
        e1, e1m = False, f"网表不存在 ({CSV})"
    x1, x1m = True, "快检跳过 (全检才跑)"
    if FULL:
        rc, msg = run([sys.executable, "state/check_netlist.py"])
        x1 = rc == 0
        x1m = f"check_netlist rc={rc}"
        if not x1:
            x1m += " | " + msg.strip().splitlines()[-1][:120] if msg.strip() else ""
    stage("① 网表 (HW/netlist_v1.csv)", e1, e1m, x1, x1m)

    # ---------- 环 2: 原理图 ----------
    e2 = (os.path.exists(SCH) and os.path.exists(CSV)
          and mt(SCH) >= mt(CSV) - 1 and e1 and x1)
    e2m = f"原理图 {ts(SCH)} ≥ 网表 {ts(CSV)}"
    if not os.path.exists(SCH):
        e2, e2m = False, "原理图不存在"
    x2, x2m = True, "快检跳过"
    if FULL:
        rc, msg = run([sys.executable, "state/check_sch_loadable.py"])
        x2 = rc == 0
        x2m = f"check_sch_loadable rc={rc}"
        if not x2:
            x2m += " | " + (msg.strip().splitlines()[-1][:120] if msg.strip() else "")
    stage("② 原理图 (.kicad_sch)", e2, e2m, x2, x2m)

    # ---------- 环 3: PCB ----------
    e3 = (os.path.exists(PCB) and os.path.exists(CSV)
          and mt(PCB) >= mt(CSV) - 1 and e1 and x1)
    e3m = f"PCB {ts(PCB)} ≥ 网表 {ts(CSV)}"
    if not os.path.exists(PCB):
        e3, e3m = False, "PCB 不存在"
    x3, x3m = True, "快检跳过"
    if FULL:
        rc, msg = run(["bash", os.path.join(HERE, "pcbnew_py.sh"), "state/check_pcb_nets.py"])
        x3 = rc == 0
        x3m = f"check_pcb_nets rc={rc}"
        if not x3:
            x3m += " | " + (msg.strip().splitlines()[-1][:120] if msg.strip() else "")
        rc2, _ = run([sys.executable, "state/check_pcb_drc.py"])
        x3m += f" · check_pcb_drc rc={rc2}"
        x3 = x3 and rc2 == 0
    # ★布线是否完成 (不阻塞"准出", 但要报出来 —— 现在 Gerber 不能下单)
    lay = None
    lp = os.path.join(PROJ, "HW", "PCB", ".layout_done.json")
    if os.path.exists(lp):
        try:
            lay = json.load(open(lp, encoding="utf-8"))
        except Exception:
            lay = None
    lay_txt = ("布线已完成 (unconnected=%s · DRC=%s)" % (lay.get("unconnected"), lay.get("drc_violations"))
                if lay else "★未布线 ⇒ 这份 Gerber 不能下单 (ISS-181)")
    stage("③ PCB (.kicad_pcb)", e3, e3m, x3, x3m + " | " + lay_txt)

    # ---------- 环 4: BOM ----------
    e4 = (os.path.exists(BOM) and os.path.exists(CSV) and mt(BOM) >= mt(CSV) - 1)
    e4m = f"BOM {ts(BOM)} ≥ 网表 {ts(CSV)}"
    if not os.path.exists(BOM):
        e4, e4m = False, "BOM 不存在"
    x4, x4m = check_bom_against_netlist()
    stage("④ BOM (HW/BOM_v1.csv)", e4, e4m, x4, x4m)

    # ---------- 环 5: 投产资料包 ----------
    missing = []
    for label, rel in PROD_REQUIRED:
        p = os.path.join(PROD, rel)
        if not (os.path.exists(p) and os.path.getsize(p) > 0):
            missing.append(label)
    # ★2026-11-04 19:55 补: 投产包必须**比板/原理图新** ⇒ 否则投板用的还是旧板生成的 Gerber
    stale = []
    pack_t = mt(os.path.join(PROD, "gerbers", "demo_mainboard-F_Cu.gtl"))
    for label, src in (("PCB", PCB), ("原理图", SCH)):
        if pack_t and mt(src) > pack_t + 1:
            stale.append(label)
    # ★★2026-11-11 (hw-lead) 新增检查项: 投产包必须带**原理图源文件** (doc/sch_src/)
    #   判据: 文件名集合与 HW/PCB/ 一一对应 + 内容 md5 全一致 (多一个少一个都红)
    ss_ok, ss_msg = check_sch_src_pack()
    e5 = (not missing) and (not stale) and e1 and e2 and e3 and e4 and ss_ok
    e5m = (f"{len(PROD_REQUIRED) - len(missing)}/{len(PROD_REQUIRED)} 必备产物齐全"
           + ("" if not missing else " · 缺: " + ", ".join(missing[:4]))
           + ("" if not stale else f" · ★**投产包比 {', '.join(stale)} 旧 ⇒ 投板用的是旧板的 Gerber**")
           + " · ★原理图源文件: " + ss_msg)
    if not os.path.isdir(PROD):
        e5, e5m = False, "production/ 目录不存在 ⇒ 跑 state/gen_production_pack.sh"
    x5 = True
    x5m = "快检跳过"
    if FULL:
        n = sum(len(fs) for _, _, fs in os.walk(PROD))
        x5m = f"投产包 {n} 个文件 · {ts(PROD)}"
        x5 = n >= len(PROD_REQUIRED)
    stage("⑤ 投产资料包 (HW/PCB/production/)", e5, e5m, x5, x5m)

    # ---------- 打印 ----------
    print(f"\n{'环节':<28}{'准入':<6}{'准出':<6}")
    print("-" * 78)
    for name, ei, em, xi, xm in rows:
        print(f"{name:<28}{ei:<6}{xi:<6}")
        print(f"    准入: {em}")
        print(f"    准出: {xm}")
    print("-" * 78)
    if fails:
        print(f"❌ 生产链有 {fails} 个环节没过 ⇒ ★**下游产物不许用** (先修上游, 再重生成下游)")
        print("   修法: ① 网表/原理图/PCB/BOM 任一比它的源旧 ⇒ 重跑对应生成器 "
              "(`python3 state/gen_netlist.py` / `gen_kicad_sch.py` / `gen_bom.py` / "
              "`bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py`) "
              "② 投产包缺件 ⇒ `bash state/gen_production_pack.sh` "
              "③ 投产包缺/多/旧**原理图源文件** ⇒ `cp -p HW/PCB/demo_mainboard*.kicad_sch "
              "HW/PCB/demo_mainboard.kicad_pro HW/PCB/production/doc/sch_src/`")
        return 1
    print("✅ 生产链准入/准出全过 —— 下游产物都是新的、且与上游一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
