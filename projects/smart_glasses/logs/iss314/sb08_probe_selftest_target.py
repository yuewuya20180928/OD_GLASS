import pcbnew
for tag, p in (("现役板", "HW/PCB/demo_mainboard.kicad_pcb"),
               ("改名板", "tmp/iss314_sandbox/board_ref1.kicad_pcb")):
    b = pcbnew.LoadBoard(p)
    names = [f.GetReference() for f in b.GetFootprints()]
    hit = "CONN_CAM" in names
    print("★ %-8s: --selftest 目标 'CONN_CAM' ⇒ %s | 板上 CONN_CAM* = %s"
          % (tag, "找得到" if hit else "★找不到 ⇒ 自检失败★",
             [n for n in names if n.startswith("CONN_CAM")]))
    # ★封装顺序 (SaveBoard 会不会重排?)
    print("    前 6 个封装顺序: %s" % names[:6])
