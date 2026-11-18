import pcbnew, sys, collections
b = pcbnew.LoadBoard(sys.argv[1])
length = collections.defaultdict(float)
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        continue
    length[t.GetNetname()] += t.GetLength()
for n in ["LED_B","LED_B_D","LED_G","LED_G_D","KEY_VOL_M","KEY_VOL_P","CSI_D0_CK_N","CSI_D0_CK_P","DSI_D0_D3_N","DSI_D0_D3_P","I2C_B_SDA","USB_CC1","ID_DETECT_1","I2C_A_SCL","I2C_B_SCL"]:
    print("%-14s %8.3f mm" % (n, length.get(n,0.0)))
