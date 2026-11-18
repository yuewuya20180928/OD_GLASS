# ★候选就绪 · 官方板血脉增量升级 `d0f3d75f` (2026-11-11 06:5x)

## ★这是什么
**在官方板上【只加不删】地补铜**，得到的升级板。官方板原有的 18092 段铜 **一寸未动**，
只新增了 326 段 / 15 个过孔。

## ★实测数据 (全部 fresh DRC + 官方对照闸)
| | 官方板 `611b869e` | ★候选 `d0f3d75f` |
|---|---|---|
| DRC 违规 | 0 | **0** |
| unconnected | 45 条 / 43 网 | **41 条 / 39 网** |
| 零铜网(≥2焊盘) | 24 | **22** |
| 差分单边零铜 | 11 | 11 |
| 差分 Δ 超差 | 3 | 3 |
| 走线段 / 过孔 | 18092 / 433 | 18418 / 448 |
| parity | True | True |
| ★退铜名单 | — | **0** |
| ★差分对死腿 | — | **0** |
| ★逐网孤岛变多 | — | **0** |
| **`compare_arm_official.py`** | — | **rc=0 · ACCEPT** |

**救回的 4 个签名**: `JTAG_TDI` / `LIGHT_5V` / `PWR_GOOD` / `SPI_MOSI_BOOT`
**候选独有签名: 0** ⇒ 纯赚，零新断。
★`CSI_D0_D0_P` 没被挤掉 —— 因为不动官方板已有铜。

## ★配方 (两步，可复现)
```bash
# ① 只加铜 (官方板 → /tmp/snapfix/offboard_patched.kicad_pcb)
PCB_HALO_MARGIN=0.015625 bash state/pcbnew_py.sh state/patch_astar_nostub.py \
  <官方板>.kicad_pcb <官方板>.drc.json --out offboard_patched.kicad_pcb --grid 0.125
# ② 收窄线宽清净距 (11 → 0，不动连通性)
bash state/clrfix_iter.sh offboard_patched.kicad_pcb <drc.json> --max 6 --tag offpatch
```

## ★稳健性 (四档 margin 实测完全相同)
`PCB_HALO_MARGIN` ∈ {0.015625, 0.03125, 0.0078125, 0} ⇒ 全部「补上 4 / 未成 41 / unc 41·39 网」
⇒ **41 条是这条增量路线的顶**，不是调参没调到底。
★第二轮增量补丁 = 补上 0 条 ⇒ 收益一次饱和。

## ★档案
- 板: `state/.lastgood/candidate_official_p41.kicad_pcb` (+ `.kicad_pro` / `.kicad_prl`)
- 凭据: `state/.lastgood/candidate_official_p41.cred.json` / `.clrfix.json`
- md5: `d0f3d75fdc6a5daf089779e212a569a6`

## ★为什么官方板本体仍然不动
官方板 md5 `611b869e13518c3c023fb178f91a0075` **一字未动**，`stage_gate rc=1` ⇒ **G1 仍开**。
换板要老板拍板（会改动 32 个文件引用 + 留证链重跑）。
**本候选是【同血脉增量】，换板代价远小于换成生成器产物。**

## ★对照: 生成器产物 `v76mx1L+pour` (unc 22 网) 为什么不能用
直接跑官方对照闸 ⇒ **rc=1 · REJECT**:
- 退铜名单 4 个 (`CARRIER_BOARD_EN` / `DSI_D0_CK_N_SRC` / `SPI_CSn_BOOT` / `USB_CC1`)
- ★差分对死腿 1 对 (`DSI_D0_CK_P_SRC`/`DSI_D0_CK_N_SRC`)
- 逐网孤岛变多 11 个网

⇒ **它 unc 数少 (22 vs 43) 是拿 1 对差分腿死掉 + 4 个网退铜 + 11 个网拆碎换来的。**
⇒ ★⇒ **不能替换官方板。**

## ★已排除的路径 (别再走)
- 端点吸附 `PCB_PATCH_SNAP=1` ⇒ 有害 (救回 3→2, clearance +2)
- 重跑整条链再补 ⇒ 会把官方板已有补丁挤掉 (实测新断 `CSI_D0_D0_P`)
- 第二轮增量补丁 / 更小 margin ⇒ 零额外收益
