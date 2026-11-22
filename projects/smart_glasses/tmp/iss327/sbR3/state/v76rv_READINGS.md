# v76rv 权威读数 (★fresh DRC 同口径 ★生成于 2026-11-10 02:26:07★)

```
# v76rv 权威读数 (★fresh DRC 同口径 ★生成于 2026-11-10 02:25:56★)

  ★体检: 旧同名 json = unc 46 条 / 38 网 / DRC 4   |   fresh = unc 43 条 / 37 网 / DRC 4
  ⚠️ ★★【旧同名 json 与终板不一致 ⇒ 它是【上一步的输入 DRC】⇒ 别拿它读数】★★
  ✓ 已把 fresh DRC 写回 /tmp/chain_v76rv/final_chain.kicad_pcb.drc.json (旧的存成 *.stale_input)
── 权威读数 (fresh DRC) ──
  板    : /tmp/chain_v76rv/final_chain.kicad_pcb
  段数  : 15034
  DRC违规: 4
  unc   : 43 条 / 37 个网名
     - [clearance] Clearance violation ( clearance 0.2000 mm; actual 0.1275 mm)
     - [clearance] Clearance violation ( clearance 0.2000 mm; actual 0.1813 mm)
     - [copper_edge_clearance] Board edge clearance violation (board setup constraints edge clearance 0.5000 mm; actual 0.3424 mm)
     - [copper_edge_clearance] Board edge clearance violation (board setup constraints edge clearance 0.5000 mm; actual 0.3424 mm)
── vs 同链基线 (★fresh DRC 双边) ──
══════ 候选臂 vs 同工艺基线 ══════
  候选臂: /tmp/chain_v76rv/final_chain.kicad_pcb  (15034 段)
  基线  : state/.lastgood/baseline_v76_chain.kicad_pcb  (14023 段)
  ✅ 链凭据: 输入=/tmp/v76rv_R.kicad_pcb 步数=?
  候选: DRC违规=4 · unconnected=43
  基线: DRC违规=0 · unconnected=46
── ① 未连接网名集合 (★强判据) ──
板A: 46 条 unc · 42 个网名签名 · 46 个端点归属
板B: 43 条 unc · 37 个网名签名 · 43 个端点归属

── ① 网名集合 (★强判据) ──
  交集 32 · 仅A 10 · 仅B 5
── ①b 名单差集 (★谁被救回 / 谁被打断) ──
基线: unc 条目 46 · 网名签名 42
候选: unc 条目 43 · 网名签名 37

★仅基线有 (★候选救回) 10:
    ✔ BAT_DET
    ✔ CSI_D0_D2_P
    ✔ DSI_D0_D1_P
    ✔ DSI_D0_D2_N
    ✔ FSIN_OUT
    ✔ ID_DETECT_0
    ✔ JTAG_TDI
    ✔ LIGHT_3V3
    ✔ SPI_SCLK_BOOT
    ✔ VBUS_DET_D

★仅候选有 (★候选打断) 5:
    ✘ CSI_D0_CK_N
    ✘ I2C_A_SDA
    ✘ JTAG_TCK
    ✘ UART_TX
    ✘ VDD_1V8_IO

★交集 32 · 净账: 救回 10 / 新断 5 ⇒ ★净 -5
★★**判据① (网名集合必须变小 ★按【大小】★) ⇒ 通过 ✔ (★42 → 37★)**
   ★(附: ★**是不是基线的严格子集** = 否 ✘ (★候选有 5 个网名基线里没有★) ★★⇒ ★【子集】是【更严】的口径, ★【变小】是文档口径 ★★)
── ② 名单制闸 (★臂 vs 基线) ──
  ★注: ★**该脚本内部把第二个参数叫"官方板" ⇒ ★★**这里的"官方"实际指本基线** ★★ (★读数时注意) ★
  走线段                           15034        14023
  过孔                              401          392
  parity通过                       True         True
  ── ★退铜名单 (官方板有铜⇒候选零铜): 1
       ★ KEY_VOL_P
  ── ★差分对死腿: 0
  ── ★逐网孤岛变多: 6
       ★ CSI_D0_CK_N  (官方 0 项 ⇒ 候选 1 项)
       ★ I2C_A_SDA  (官方 0 项 ⇒ 候选 2 项)
       ★ JTAG_TCK  (官方 0 项 ⇒ 候选 1 项)
       ★ KEY_VOL_P  (官方 1 项 ⇒ 候选 4 项)
       ★ UART_TX  (官方 0 项 ⇒ 候选 1 项)
       ★ VDD_1V8_IO  (官方 0 项 ⇒ 候选 1 项)
  ── (参考) 救回零铜的网: 6
  ── 判定: REJECT
     · ★**DRC=4 (必须 0)**
     · DRC 变差 0→4
     · ★**逐网孤岛变多 6 个网 (官方项数⇒候选更多 ⇒ 网被拆碎): CSI_D0_CK_N, I2C_A_SDA, JTAG_TCK, KEY_VOL_P, UART_TX, VDD_1V8_IO**
  闸 rc=1
```
