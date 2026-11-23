#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 板面 186 个封装【本机 KiCad pcbnew API】逐件实测 (只读)
用法: bash state/pcbnew_py.sh tmp/iss369/tools/board_probe.py <board.kicad_pcb> <out.json>
"""
import json
import sys

import pcbnew

src = sys.argv[1]
dst = sys.argv[2]

bd = pcbnew.LoadBoard(src)
fps = list(bd.GetFootprints())
out = []
for fp in fps:
    fpid = fp.GetFPIDAsString()
    lib = fpid.split(":")[0] if ":" in fpid else ""
    nm = fpid.split(":")[-1] if fpid else ""
    pads = list(fp.Pads())
    pads.sort(key=lambda p: p.GetNumber())
    out.append({
        "ref": fp.GetReference(),
        "value": fp.GetValue(),
        "fpid_as_string": fpid,
        "lib": lib,
        "name": nm,
        "lib_id_str": fp.GetFPID().GetUniStringLibId(),
        "pad_count": len(pads),
        "pads": [[p.GetNumber(), p.GetNetname(), p.GetNetCode(),
                   round(pcbnew.ToMM(p.GetSize().x), 4),
                   round(pcbnew.ToMM(p.GetSize().y), 4),
                   round(pcbnew.ToMM(p.GetPosition().x), 4),
                   round(pcbnew.ToMM(p.GetPosition().y), 4),
                   p.GetShape() if not hasattr(p, "GetShape") else str(p.GetShape())]
                  for p in pads],
        "layers": [bd.GetLayerName(l) for l in fp.GetLayerSet().Seq()],
        "bbox_mm": [round(pcbnew.ToMM(fp.GetBoundingBox().GetWidth()), 4),
                    round(pcbnew.ToMM(fp.GetBoundingBox().GetHeight()), 4)],
        "courtyard": bool(fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount()
                          or fp.GetCourtyard(pcbnew.B_CrtYd).OutlineCount()),
    })
json.dump({"count": len(out), "footprints": out}, open(dst, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("pcbnew footprints=%d -> %s" % (len(out), dst))
print("fpid unique =", sorted(set(f["fpid_as_string"] for f in out)))
print("lib unique =", sorted(set(f["lib"] for f in out)))
print("name unique =", sorted(set(f["name"] for f in out))[:10])
