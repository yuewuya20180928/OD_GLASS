# ★★【跨会话协作通知】2026-11-11 04:5x ★★

## ★1. 链目录撞名 (★已发生·已规避★)
★`state/v76my_arms.sh` 的链步骤在写 **`/tmp/chain_v76mx1/`** ⇒ ★**会覆写 `v76mx1` 的终板** ★
⇒ ★**权威副本已归档到稳定路径** (★请改用这些路径, 别再用 `/tmp/chain_v76mx1/`★):
- ★**候选臂B**: `state/.lastgood/candidate_v76mx1_chain.kicad_pcb` (+ `.kicad_pro` + `.kicad_prl` + `.chain.json`) ★
- ★**对照臂A**: `state/.lastgood/baseline_v76mx0_chain.kicad_pcb` (+ 同套三件套 + 凭据) ★
- ★**同链基线(闸关)**: `state/.lastgood/baseline_v76mw0_chain.kicad_pcb` ★

## ★2. ★★`v76my` 的 env 已实测【零额外收益】⇒ 建议别再花一小时★★
★`PCB_YIELD_VICTIMS=BOOT_N,USB_CC1,CARRIER_BOARD_EN` ⇒ ★**与只保护 `BOOT_N` 的臂, 未连接网名集合【完全相同】** ★★
(★交集 23 · 仅A 0 · 仅B 0 ⇒ `state/cmp_unc_sets.py` 实测★)
⇒ ⇒ **多改 129/137 段铜 + 扰动面 1→3 处, 净收益 0 个网** ⇒ ⇒ ★**名单保持最小: 只 `BOOT_N`** ★★
★原因: ★`USB_CC1` 在 **REST 阶段(最后布)** ⇒ 走廊早被占完 ⇒ ★**让路闸对"最后才布的网"无效** ★★

## ★3. 窄版让路闸的实测判决 (★已过名单闸★)
| | 臂A(闸关) | 臂B(窄版闸开) |
|---|---|---|
| DRC | 0 | **0** |
| unc | 29 条 / 24 网名 | **28 条 / 23 网名** |
| 网名集合 | — | ★**仅基线 1 · 仅候选 0 ⇒ 纯赚 `BOOT_N`, 零新断** ★★ |
| 退铜/死腿/孤岛 | 0/0/0 | **0/0/0** |
| 名单闸 | rc=1 | ★**rc=0 ACCEPT** ★★

## ★4. 官方板未动
★md5 `611b869e13518c3c023fb178f91a0075` · mtime 2026-11-06 07:07:17 ⇒ ★**G1 仍开, 不许投板** ★
