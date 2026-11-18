#!/usr/bin/env python3
import json, collections
d = json.load(open("/tmp/iss308_cand_layers.json", encoding="utf-8"))
RES22 = """CARRIER_BOARD_EN CSI_D0_CK_N CSI_D0_D0_N CSI_D0_D0_N_SRC CSI_D0_D2_N CSI_D0_D3_N CSI_MCLK
DSI_D0_CK_N_SRC DSI_D0_D0_N DSI_D0_D0_P DSI_D0_D1_N DSI_D0_D1_N_SRC DSI_D0_D3_N
I2C_A_SCL I2C_B_SCL I2C_B_SDA ID_DETECT_1 KEY_VOL_M KEY_VOL_P LED_B SPI_CSn_BOOT USB_CC1""".split()
print("residual count:", len(RES22), "unique:", len(set(RES22)))

def show(n):
    v = d.get(n)
    if v is None:
        return "  %-16s ABSENT" % n
    return "  %-16s seg=%-3d %-52s pad=%-2d %-28s via=%d" % (
        n, v["seg_total"], str(v["seg"]), v["pad_total"], str(v["pad"]), v["vias"])

print("\n########## A. 22 残余网 逐条 ##########")
for n in RES22:
    print(show(n))

print("\n########## B. 配对腿对照 (P 腿 / 伙伴腿) ##########")
PAIRS = [
 ("CSI_D0_CK_N","CSI_D0_CK_P"),("CSI_D0_D0_N","CSI_D0_D0_P"),
 ("CSI_D0_D0_N_SRC","CSI_D0_D0_P_SRC"),("CSI_D0_D2_N","CSI_D0_D2_P"),
 ("CSI_D0_D3_N","CSI_D0_D3_P"),("CSI_MCLK","CSI_MCLK"),
 ("DSI_D0_CK_N_SRC","DSI_D0_CK_P_SRC"),("DSI_D0_D0_N","DSI_D0_D0_P"),
 ("DSI_D0_D0_P","DSI_D0_D0_P"),("DSI_D0_D1_N","DSI_D0_D1_P"),
 ("DSI_D0_D1_N_SRC","DSI_D0_D1_P_SRC"),("DSI_D0_D3_N","DSI_D0_D3_P"),
 ("KEY_VOL_M","KEY_VOL_P"),
]
for n,p in PAIRS:
    print(show(n)); print(show(p)); print("  ---")

print("\n########## C. 所有含 DSI/CSI/KEY 的网 (含 P 腿全表) ##########")
for n in sorted(d):
    if any(k in n for k in ("DSI","CSI","KEY_VOL","USB_D")):
        print(show(n))
