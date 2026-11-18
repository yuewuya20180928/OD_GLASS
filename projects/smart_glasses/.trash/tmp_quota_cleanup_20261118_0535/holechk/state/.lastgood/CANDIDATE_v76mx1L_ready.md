# ★【候选板 v76mx1L · 已过全部闸门 · 等老板拍板】★ (2026-11-11 05:1x)

## ★配方 (★三个机制叠加★)
1. ★**窄版让路闸** (★`PCB_YIELD_STRAIGHT=1` + `PCB_YIELD_VICTIMS=BOOT_N`★) ⇒ ★救回 **`BOOT_N`** ★
2. ★**松边距补丁链** (★`PCB_CHAIN_LOOSE_MARGIN=0.03125`★) ⇒ ★救回 **`TS_BAT`** · `LED_B` · `I2C_A_SCL` ★
3. ★**收窄线宽** (★`state/fix_clearance_width.py` / `clrfix_iter.sh`★) ⇒ ★清掉 0.1937mm 边际违规 ⇒ ★**DRC 0** ★

## ★三把尺 (★全部独立复算一致★)
| 判据 | 候选 | 同链基线 | |
|---|---:|---:|---|
| fresh DRC | **0** | 0 | ✅ |
| unconnected | **26 条 / 22 网名** | 29 条 / 24 网名 | ✅ |
| 网名集合 | ★**仅候选 0 · 仅基线 2** | | ✅ **纯赚 2 个网, 零新断** |
| 零铜网(≥2焊盘) | **8** | 10 | ✅ 改善 |
| 差分单边零铜 / Δ超差 | 5 / 1 | 5 / 1 | ✅ 持平 |
| 退铜 / 差分死腿 / 逐网孤岛变多 | **0 / 0 / 0** | — | ✅ |
| parity | True | True | ✅ |
| **名单制闸 rc** | | | **0 = ACCEPT** ✔ |

## ★加 5V 铜皮后 (★官方板级完整度★)
★`state/.lastgood/candidate_v76mx1L_pour.kicad_pcb` ⇒ ★**铜皮 5 块 (与官方板同) · DRC 0 · unc 26条/22网名** ⇒ ★**名单闸仍 rc=0 ACCEPT** ★

## ★与官方板对比
| | 官方板 | ★候选(+铜皮)★ |
|---|---:|---:|
| unconnected | 45 条 / 43 网名 | ★**26 条 / 22 网名** ★ |
| 走线段 | 18092 (★粒度差, 总长只差 ~4%★) | 3650 |
| 过孔 | 433 | 457 |
| 铜皮 | 5 | 5 |
| DRC | 0 | 0 |

## ★文件
- 候选(无铜皮): `state/.lastgood/candidate_v76mx1L_chain.kicad_pcb` (+`.kicad_pro`/`.kicad_prl`/`.chain.json`/`.clrfix.json`)
- 候选(+5V铜皮): `state/.lastgood/candidate_v76mx1L_pour.kicad_pcb` (+`.kicad_pro`/`.kicad_prl`)
- 同链基线: `state/.lastgood/baseline_v76mw0_chain.kicad_pcb`
- 路由器产物: `/tmp/v76mx1_R.kicad_pcb` · 链: `/tmp/chain_v76mx1L/`

## ★状态
★官方板 md5 `611b869e13518c3c023fb178f91a0075` **未动** ⇒ ★**G1 仍开, 不许投板** ⇒ ★**未晋级, 未发布任何 Gerber** ★
