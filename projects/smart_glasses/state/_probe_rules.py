import os, pcbnew
MM=1e6
PROJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b=pcbnew.LoadBoard(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"))
ds=b.GetDesignSettings()
for k in ("m_MinClearance","m_TrackMinWidth","m_ViasMinSize","m_ViasMinAnnularRing","m_CopperEdgeClearance","m_HoleToHoleMin","m_HoleClearance"):
    print("  %-24s = %s"%(k, getattr(ds,k,"n/a")))
