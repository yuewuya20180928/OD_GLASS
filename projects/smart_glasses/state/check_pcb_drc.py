#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_pcb_drc.py —— PCB 图纸门禁 (★"硬件自己画图" ⇒ 图纸必须进项目门禁链)

为什么要有这条门禁:
  ★EN 那个 P0 (9 路电源 IC 的 EN 悬空=关断 ⇒ 投板后整板不上电 = 2~4 周返工) 说明
  ★**图纸的致命缺陷必须在"下单前"被机器抓住**, 不能靠人眼 ⇒ ★**DRC 进门禁 = 我们自己的图纸有我们自己的验收标准**。

判据:
  C1 工具链可用 (KiCad 10 AppImage, 免 root ⇒ state/kicad.sh)
  C2 图纸存在 (HW/PCB/demo_mainboard.kicad_pcb) 且能被 KiCad 解析
  C3 ★**DRC violations = 0** (error + warning 都算)
  C4 unconnected items = 0 (--strict; 骨架阶段允许未布线)
  C5 生成器自检 (state/gen_kicad_project.py 的 C1~C6) 仍全过 (图纸与参数没脱节)
  C6 ★**生产文件齐**: Gerber (铜/阻焊/字符/外形) + 钻孔文件都在

退出码: 0 = 全过; 1 = 有不通过项
"""
import json
import os
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(PROJ, "state")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
# ★★2026-11-06 01:1x **支持传入待测板路径** (★positional)
#   ★**为什么**: 之前这个脚本**硬编码官方板** ⇒ ★**传候选板路径也会去量官方板**
#     ⇒ ★**误把官方板的结果当成候选板的证据** (★v35 那次真踩过: 官方 DRC 0 被当成 v35 的)
#   ★**用法**: `python3 state/check_pcb_drc.py /tmp/vXX_R.kicad_pcb [--strict]`
#     ⇒ 打印 `(查板: <路径>)` ⇒ ★**一眼能看出量的是哪块板**
_pos = [a for a in sys.argv[1:] if not a.startswith("--")]
if _pos:
    PCB = os.path.abspath(_pos[0])
GERBER_DIR = os.path.join(PROJ, "HW", "PCB", "gerbers")
KC = os.path.join(HERE, "kicad.sh")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.pop("timeout", 300), **kw)



def _dup_vias(path):
    """★**同点重复过孔** (★net + 坐标完全一样 ⇒ KiCad DRC 报 holes_co_located)
    返回 [(net, x, y, 次数), ...]"""
    import re as _re
    import collections as _c
    try:
        txt = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return []
    cnt = _c.Counter()
    # 逐个 (via ... ) 块扫 (★不用正则跨块 ⇒ 免得嵌套括号搞乱)
    pos = 0
    end_marker = "\n" + "\t)"
    while True:
        i = txt.find("(via", pos)
        if i < 0:
            break
        j = txt.find(end_marker, i)
        if j < 0:
            break
        blk = txt[i:j]
        pos = j + 1
        ma = _re.search(r'\(at ([-\d.]+) ([-\d.]+)\)', blk)
        mn = _re.search(r'\(net (?:"([^"]+)"|(\d+))\)', blk)
        if not ma or not mn:
            continue
        net = mn.group(1) if mn.group(1) else ("#" + mn.group(2))
        cnt[(net, round(float(ma.group(1)), 3), round(float(ma.group(2)), 3))] += 1
    return [(k[0], k[1], k[2], v) for k, v in cnt.items() if v > 1]


def main():
    fails = []
    lines = []
    lines.append(f"  (查板: {PCB})")

    # C1 工具链
    rc = run([KC, "--version"])
    kc_ver = (rc.stdout or "").strip().splitlines()[-1] if rc.returncode == 0 else ""
    ok1 = rc.returncode == 0 and kc_ver.startswith("10.")
    lines.append(f"  {'✅' if ok1 else '❌'} C1 KiCad 工具链可用 — {kc_ver or (rc.stderr or '')[:120]}")
    if not ok1:
        fails.append("C1 工具链不可用")
        print("\n".join(lines))
        return 1

    # C2 图纸可解析
    if not os.path.exists(PCB):
        lines.append(f"  ❌ C2 图纸不存在 — {PCB}")
        fails.append("C2 图纸缺失")
        print("\n".join(lines))
        return 1
    rc = run([KC, "pcb", "export", "drill", "--output", "/tmp/_pcbchk", "--format", "excellon", PCB])
    ok2 = rc.returncode == 0
    lines.append(f"  {'✅' if ok2 else '❌'} C2 图纸可被 KiCad 解析 (drill 导出 rc={rc.returncode})")
    if not ok2:
        fails.append("C2 图纸解析失败")

    # C3/C4 DRC
    out_json = "/tmp/_pcb_drc.json"
    rc = run([KC, "pcb", "drc", "--output", out_json, "--severity-error", "--severity-warning",
              "--format", "json", PCB])
    n_viol = n_unc = -1
    if os.path.exists(out_json):
        d = json.load(open(out_json))
        n_viol = len(d.get("violations") or [])
        n_unc = len(d.get("unconnected_items") or [])
    ok3 = (n_viol == 0)
    # ★C4 分阶段: 骨架阶段 (器件+网络就位, 未布线) 允许未连接; ★布线完成后 (--strict) 必须归零
    strict = "--strict" in sys.argv
    ok4 = (n_unc == 0) if strict else True
    lines.append(f"  {'✅' if ok3 else '❌'} C3 DRC violations = {n_viol} (要求 0)")
    lines.append(f"  {'✅' if ok4 else '❌'} C4 unconnected items = {n_unc}"
                 + (" (--strict: 布线完成后必须为 0)" if strict else "  ← 骨架阶段允许未布线 (布线完成后用 --strict 归零)"))
    if not ok3:
        fails.append(f"C3 DRC {n_viol} 项违规")
    if not ok4:
        fails.append(f"C4 {n_unc} 项未连接")
    if n_viol > 0 and os.path.exists(out_json):
        for x in (d.get("violations") or [])[:6]:
            lines.append(f"       - [{x.get('type')}] {str(x.get('description'))[:110]}")

    # ★★C7 ★**同点重复过孔** (2026-11-05 09:57 新增)
    #   ★**为什么要单独查**: KiCad DRC 只报 `holes_co_located` ("Drilled holes co-located")
    #     ⇒ ★**不说是哪两个、哪条网** ⇒ 排查还得再写脚本
    #   ★**实测**: v26 臂 A/B 的 DRC 2 条全是它 (GND 下拉两遍落在同一坐标)
    #     ⇒ 根因已修 (路由器加 `_via_exists` 查重) ⇒ ★**再加一道显式闸门防复发**
    dup = _dup_vias(PCB)
    ok7 = (len(dup) == 0)
    lines.append(f"  {'✅' if ok7 else '❌'} C7 同点重复过孔 = {len(dup)} (要求 0)")
    if not ok7:
        fails.append(f"C7 {len(dup)} 处重复过孔")
        for (net, x, y, n) in dup[:6]:
            lines.append(f"       - {net} @ ({x:.3f}, {y:.3f}) × {n}")

    # C5 生成器自检
    rc = run([sys.executable, os.path.join(HERE, "gen_kicad_project.py")])
    ok5 = rc.returncode == 0
    lines.append(f"  {'✅' if ok5 else '❌'} C5 生成器自检 (gen_kicad_project.py rc={rc.returncode})")
    if not ok5:
        fails.append("C5 生成器自检不过")

    # C6 生产文件
    need_suffix = [".gtl", ".gbl", ".gts", ".gbs", ".gto", ".gbo", ".gm1"]
    have = os.listdir(GERBER_DIR) if os.path.isdir(GERBER_DIR) else []
    missing = [sf for sf in need_suffix if not any(f.endswith(sf) for f in have)]
    drill = any(f.endswith((".drl", ".xln")) or "drill" in f for f in have)
    ok6 = (not missing) and drill
    lines.append(f"  {'✅' if ok6 else '❌'} C6 生产文件齐 — Gerber {len(have)} 个"
                 + (f", 缺 {missing}" if missing else "") + ("" if drill else ", 缺钻孔文件"))
    if not ok6:
        fails.append("C6 生产文件不齐")

    print("=" * 70)
    print("  PCB 图纸门禁 · check_pcb_drc (★自己画的图, 自己验)")
    print("=" * 70)
    print("\n".join(lines))
    print("-" * 70)
    if fails:
        print(f"❌ 不通过 {len(fails)} 项: {'; '.join(fails)}")
        return 1
    print("✅ 全过 —— 图纸可下单 (★前提: ISS-158 的三件规格回来后重跑生成器再验一遍)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
