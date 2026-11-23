#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★ISS-369 独立复核脚本 (v2)★ —— ★不依赖上一趟的任何脚本/JSON·自己读盘自己算★
目的: 用 KiCad 10.0.8 的 pcbnew 直接读板, 独立复核:
  ① 板面封装总数
  ② 每个封装的 GetFPIDAsString() / GetLibItemName() / GetUniStringLibId() 是否非空
  ③ 每个封装的焊盘数 (含焊盘名为空的 NPTH)
  ④ 板面总焊盘数
用法: bash state/pcbnew_py.sh logs/iss369/scripts/v2_indep_board_probe.py <板文件>
"""
import json
import os
import sys

import pcbnew

PCB_DEFAULT = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")


def main():
    pcb_path = sys.argv[1] if len(sys.argv) > 1 else PCB_DEFAULT
    pcb_path = os.path.abspath(pcb_path)
    board = pcbnew.LoadBoard(pcb_path)
    if board is None:
        print("FATAL: LoadBoard returned None for %s" % pcb_path)
        return 2

    rows = []
    total_pads = 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        try:
            fpid = fp.GetFPIDAsString()
        except Exception:
            fpid = "<ERR>"
        try:
            libitem = fp.GetFPID().GetLibItemName()
        except Exception:
            libitem = "<ERR>"
        try:
            unilib = fp.GetFPID().GetUniStringLibId()
        except Exception:
            unilib = "<ERR>"
        pads = list(fp.Pads())
        npad = len(pads)
        # 焊盘名为空 (NPTH 固定孔) 的计数
        n_empty_pad_name = sum(1 for p in pads if (p.GetNumber() or "").strip() == "")
        total_pads += npad
        rows.append({
            "ref": str(ref),
            "value": str(fp.GetValue()),
            "fpid": str(fpid),
            "libitem": str(libitem),
            "unilib": str(unilib),
            "n_pads": npad,
            "n_pads_empty_name": n_empty_pad_name,
            "x": fp.GetPosition().x,
            "y": fp.GetPosition().y,
            "orient": fp.GetOrientationDegrees(),
        })
    rows.sort(key=lambda r: r["ref"])
    named = [r for r in rows if (r["fpid"] or "").strip() != ""]
    libid_variants = sorted(set(r["fpid"] for r in rows))
    out = {
        "pcb": pcb_path,
        "footprint_count": len(rows),
        "named_libid_count": len(named),
        "fpid_unique_values": libid_variants,
        "total_pads": total_pads,
        "rows": rows,
    }
    dest = os.path.join("logs", "iss369", "62_indep_board_probe.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("footprints      = %d" % len(rows))
    print("named lib_id    = %d" % len(named))
    print("fpid unique     = %r" % libid_variants)
    print("total pads      = %d" % total_pads)
    print("written -> %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
