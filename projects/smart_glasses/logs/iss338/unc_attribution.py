#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-338 · unc 45 条归因 (只读 logs/iss334/00_official_drc_fresh.json)"""
import json, collections, re, sys
NINE = ["CAM_RESET_N","FSIN_OUT","JTAG_TDI","LED_G_D","SPI_MISO_BOOT",
        "SPI_MOSI_BOOT","SPI_SCLK_BOOT","UART_RX","USB_CC2"]
d = json.load(open(sys.argv[1] if len(sys.argv)>1 else "logs/iss334/00_official_drc_fresh.json"))
ui = d["unconnected_items"]
def netof(it):
    for x in it.get("items", []):
        m = re.search(r"\[([^\]]+)\]", x.get("description",""))
        if m: return m.group(1)
    return "?"
per = collections.Counter(netof(it) for it in ui)
tot = sum(per.get(n,0) for n in NINE)
diff = sum(c for n,c in per.items() if n.startswith(("CSI_","DSI_")))
print("unconnected_items = %d | 涉及网名 = %d" % (len(ui), len(per)))
for n in NINE:
    print("  %-16s %d 条 (%.1f%%)" % (n, per.get(n,0), per.get(n,0)/len(ui)*100))
print("  本单 9 条 = %d/%d = %.1f%% | 差分腿 = %d 条 (无交集) | 其余 = %d 条"
      % (tot, len(ui), tot/len(ui)*100, diff, len(ui)-tot-diff))
print("  ⇒ 悬空 9 条后 unc 预估 = %d - %d = %d" % (len(ui), tot, len(ui)-tot))
