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
  C4 unconnected items = 0
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
GERBER_DIR = os.path.join(PROJ, "HW", "PCB", "gerbers")
KC = os.path.join(HERE, "kicad.sh")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.pop("timeout", 300), **kw)


def main():
    fails = []
    lines = []

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
    ok4 = (n_unc == 0)
    lines.append(f"  {'✅' if ok3 else '❌'} C3 DRC violations = {n_viol} (要求 0)")
    lines.append(f"  {'✅' if ok4 else '❌'} C4 unconnected items = {n_unc} (要求 0)")
    if not ok3:
        fails.append(f"C3 DRC {n_viol} 项违规")
    if not ok4:
        fails.append(f"C4 {n_unc} 项未连接")
    if n_viol > 0 and os.path.exists(out_json):
        for x in (d.get("violations") or [])[:6]:
            lines.append(f"       - [{x.get('type')}] {str(x.get('description'))[:110]}")

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
