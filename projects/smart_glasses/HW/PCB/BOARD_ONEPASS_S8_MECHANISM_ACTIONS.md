# BOARD ONEPASS · S8 机制级「换机制」作业包 (ISS-334)

> 单号: **ISS-334** · 角色: **硬件总工 (hw-lead)** · 日期: **2026-11-18**
> ★**这份是「板那一趟」的逐字作业包** ★ — ★**照这份跑, 板 md5 只变一次** ★
> ★**铁律**: ★**在 S8-5 收口之前, 一律不许碰 `HW/PCB/demo_mainboard.kicad_pcb`** ★ (★起跑线/中间产物全在 `tmp/iss334/` 与 `/tmp/chain_*`★)

---

## §0 板那一趟的铁律 (★先读这一段, 再往下★)

| # | 铁律 | 怎么守 |
|---|---|---|
| 1 | ★**板只改一次** ★ | S8-1~S8-4 全在 `tmp/iss334/arms/<臂名>/` 与 `/tmp/chain_<臂名>/` 里跑; ★**只有 S8-5 收口那一步才允许动 `HW/PCB/demo_mainboard.kicad_pcb`** ★ |
| 2 | ★**起跑线必须是官方 stage-1** ★ | `/tmp/chain_offverify/s1_straight.kicad_pcb` (17,022 段) ⇒ ★**不许用现生成器的产物起跑** (★现生成器只出 2,492 段 ⇒ 与官方板不同工艺 ⇒ 不可比★) |
| 3 | ★**对照臂先跑, 且必须复现官方** ★ | `cmp_pcb_geom.py <对照臂终板> HW/PCB/demo_mainboard.kicad_pcb` ★**必须 rc=0** ★ ⇒ 不过就先修链, 不许开候选臂 |
| 4 | ★**判据是名单制闸, 不是 unc 条数** ★ | `compare_arm_official.py` rc=0 才算可晋级; ★**"unc 变少"不算成功, "计数持平"更不算成功** ★ |
| 5 | ★**闸没生效不许开臂** ★ | `gate_live_check.py --arm-script <臂脚本>` 返回 0 ⇒ 停 |
| 6 | ★**可比性自检先过** ★ | 终板段数 ∈ 16,283~19,901 且过孔 ∈ 390~476 ⇒ 不过 ⇒ 读数一律不算数 |

---

## S8-1 ★前置: 复现官方 (★对照臂 C0/A0/B0 干的就是这一步·**必做**★)★

★**为什么这是第一步**: ★**官方板能被完整复现才有"同工艺对比"这回事** ★ (`cmp_pcb_geom.py` 实测: 官方板 ≡ `/tmp/chain_offverify/final_chain.kicad_pcb`, 走线 17,980 条 + 过孔 433 + 铜皮 5 区全同)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
ARM=C0_control
mkdir -p tmp/iss334/arms/$ARM
cp /tmp/chain_offverify/s1_straight.kicad_pcb tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb
PCB_CHAIN_LOOSE_MARGIN=0.0625 bash state/replay_patch_chain.sh \
    tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb $ARM
FINAL=/tmp/chain_$ARM/final_chain.kicad_pcb
```

★**验收读数 (三条都要)** ★

| # | 命令 | 合格 | 不过怎么办 |
|---|---|---|---|
| 1 | `python3 state/cmp_pcb_geom.py $FINAL HW/PCB/demo_mainboard.kicad_pcb` | ★**rc=0 (几何等价)** ★ | ★**链没复现官方 ⇒ 停 ⇒ 查链的 env (`PCB_CHAIN_LOOSE_MARGIN` / margin 档) ⇒ 不许往下走** ★ |
| 2 | `grep -c "(segment" $FINAL` | ★**18,092 (或 ±10%: 16,283~19,901)** ★ | 同上 |
| 3 | `python3 state/check_pcb_drc.py $FINAL` | ★**rc=0 · DRC viol = 0** ★ | ★**停; 不许带着 DRC 违规往下走** ★ |

★**S8-1 不过 = 整趟不许开臂** ★

---

## S8-2 ★候选臂 A: `A1_pair_corridor` (★桶 A · 7 条零铜差分腿★)★

★**前置 (★硬前置·§4-3 实测撞过墙★)**: ★**`state/pair_corridor.py` 必须先被修到能产出 ≥2 格的路径** ★
(★现状: 跑完打印"落铜成功: P 1 段 / N 1 段", 但★**段数 18,092→18,092 且两板几何等价 = 零新增铜**★)
⇒ ★**没修 ⇒ 不许开 A1** ⇒ ★**修工具的授权见 ISS-334 §5 need-3** ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
ARM=A1_pair_corridor
mkdir -p tmp/iss334/arms/$ARM
cp /tmp/chain_offverify/s1_straight.kicad_pcb tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb
bash state/kicad.sh pcb drc --output tmp/iss334/arms/$ARM/s0_official_s1.drc.json \
     --severity-error --severity-warning --format json tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb
for PN in "CSI_D0_D0_P CSI_D0_D0_N" "CSI_D0_D0_P_SRC CSI_D0_D0_N_SRC" \
          "CSI_D0_D1_P_SRC CSI_D0_D1_N_SRC" "CSI_D0_D3_P CSI_D0_D3_N" \
          "CSI_D0_D3_P_SRC CSI_D0_D3_N_SRC" "DSI_D0_D2_P_SRC DSI_D0_D2_N_SRC" \
          "DSI_D0_D3_P_SRC DSI_D0_D3_N_SRC"; do
  set -- $PN
  bash state/pcbnew_py.sh state/pair_corridor.py \
      tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb tmp/iss334/arms/$ARM/s0_official_s1.drc.json \
      --out tmp/iss334/arms/$ARM/pc_$1.kicad_pcb --pair $1 $2
  grep -c "(segment" tmp/iss334/arms/$ARM/pc_$1.kicad_pcb
done
```

★**验收读数 (★每对都要看"段数真的变了"★)** ★

| # | 命令 | 合格 | 不过怎么办 |
|---|---|---|---|
| 1 | `grep -c "(segment" tmp/iss334/arms/$ARM/pc_*.kicad_pcb` | ★**每个都比 17,022 大 (至少 +2)** ★ | ★**还是 17,022 ⇒ 又是 1 格退化路径的假阳性 ⇒ 停 ⇒ 工具还没修好** ★ |
| 2 | `python3 state/pair_copper_table.py tmp/iss334/arms/$ARM/pc_<P>.kicad_pcb \| grep <N>` | ★**该 N 腿铜长 > 0.000** ★ | ★**= 0.000 ⇒ 该对没救回 ⇒ 记 REJECT, 走 S8-4** ★ |
| 3 | `bash state/pcbnew_py.sh state/gate_live_check.py --arm-script tmp/iss334/arms/$ARM/arm.sh` | ★**返回 ≠ 0** ★ | ★**返回 0 ⇒ 闸不生效 ⇒ 不许开臂** ★ |

★**A1 全对通过后才允许套链** ★

```bash
PCB_CHAIN_LOOSE_MARGIN=0.0625 bash state/replay_patch_chain.sh \
    tmp/iss334/arms/$ARM/pc_<最后一个>.kicad_pcb $ARM
FINAL=/tmp/chain_$ARM/final_chain.kicad_pcb
python3 state/compare_arm_official.py $FINAL HW/PCB/demo_mainboard.kicad_pcb ; echo "GATE_RC=$?"
python3 state/check_pcb_drc.py $FINAL ; echo "DRC_RC=$?"
```

★**不过怎么办**: ★**GATE_RC=1 ⇒ 看闸打印的【退铜名单】/【差分死腿】⇒ 只要名单非空 ⇒ 这条臂 REJECT ⇒ 不许晋板** ★

---

## S8-3 ★候选臂 B: `B1_fine_grid` (★桶 B · 16 条出脚几何钉死的网★)★

★**前置 (★硬前置★)**: ★**need-1 必须先有答复** (★现生成器只出 2,492 段 ⇒ 生成器级 env 臂不可比★)
★**本臂是【成品板级】的细网格臂**: ★**把链的 A★ 步网格 0.125 → 0.0625** ★ ⇒ ★**不是改 env, 是改链脚本里的一个字面量** ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
ARM=B1_fine_grid
mkdir -p tmp/iss334/arms/$ARM
cp /tmp/chain_offverify/s1_straight.kicad_pcb tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb
cp state/replay_patch_chain.sh tmp/iss334/arms/$ARM/chain.sh
# ★唯一改动: 链里 A★ 步的网格 0.125 → 0.0625 ★
sed -i 's|"$WORK/s2_combo.kicad_pcb" "$WORK/final_chain.kicad_pcb" 0.125|"$WORK/s2_combo.kicad_pcb" "$WORK/final_chain.kicad_pcb" 0.0625|' \
    tmp/iss334/arms/$ARM/chain.sh
grep -n 'final_chain.kicad_pcb" 0\.' tmp/iss334/arms/$ARM/chain.sh    # ★只此一行变了★
bash tmp/iss334/arms/$ARM/chain.sh tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb $ARM
FINAL=/tmp/chain_$ARM/final_chain.kicad_pcb
```

★**验收读数** ★

| # | 命令 | 合格 | 不过怎么办 |
|---|---|---|---|
| 1 | `grep -c "(segment" $FINAL` | ★**∈ 16,283 ~ 19,901** ★ | ★**低于 16,283 ⇒ 与官方不同工艺 ⇒ 读数不算数 ⇒ 停** ★ |
| 2 | `python3 state/pair_copper_table.py $FINAL > tmp/iss334/arms/$ARM/pair_copper.txt` ★**再与官方板的同名表逐行比** ★ | ★**16 条 B 桶网里至少 1 条铜长 > 0.000** ★ | ★**全是 0.000 ⇒ 细网格救不了 ⇒ B 桶药方证伪 ⇒ 走 S8-4** ★ |
| 3 | `python3 state/compare_arm_official.py $FINAL HW/PCB/demo_mainboard.kicad_pcb ; echo "GATE_RC=$?"` | ★**GATE_RC=0** ★ | ★**GATE_RC=1 ⇒ 看退铜名单 ⇒ 非空 ⇒ REJECT** ★ |
| 4 | `python3 state/check_pcb_drc.py $FINAL ; echo "DRC_RC=$?"` | ★**DRC_RC=0** ★ | ★**非 0 ⇒ 停** ★ |

★**耗时预估**: ★**网格减半 ⇒ 格数 ×4 ⇒ 内存/时间 ×4 ⇒ 整条链 ≈ 4~8 h** ★ ⇒ ★**必须排在夜里跑** ★

---

## S8-4 ★候选臂 C: `C2_production_fix` (★桶 C · ★**修在产生点**★ · 唯一有望救 24 条的一类机制)★

★**前置 (★硬前置★)**: ★**need-2 授权 + need-1 有答复** ★
★**为什么 C1 (`fix_board_rip_guarded.py`) 不再单独排**: ★**实测 A★ 在官方 stage-1 (17,022 段) 上补 0 条 / 未成 54 条 (产物 md5 与输入逐字节相同)** ★
⇒ ★**"擦在产物上"这条路已被证伪 ⇒ 只有改产生点才有戏** ★

★**C2 的改法规格 (★给改的人·本单零改生成器代码★)** ★

| 项 | 规格 (★逐条·可直接照着改★) |
|---|---|
| ★改哪个文件 ★ | ★**`state/gen_pcb_routing.py`** ★ (★产生点·不是产物★) |
| ★触发条件 ★ | ★**该网在板上 segment 数 = 0 且焊盘数 ≥ 2** ★ (★与 `state/compare_arm_official.py` 的 `zero_copper` 定义逐字一致★) |
| ★改哪一段 ★ | ★**A★ 的起跑点: 从"已有铜的端点"改成"从焊盘格起步"** ★ (★`state/patch_astar_nostub.py` 的 `pad_cells` 已有先例·见该脚本第 90 行★) |
| ★护栏 1 ★ | ★**只加铜不删铜** ★ ⇒ ★**不可能把任何网打成零铜** ★ |
| ★护栏 2 ★ | ★**落铜后逐网孤岛数不得变多** ★ (★沿用 `state/rip_guard.island_count_model`★) |
| ★护栏 3 ★ | ★**不许打死差分腿** ★ (★差分腿打死 = 一条高速通道不存在 = 一票否决★) |
| ★护栏 4 ★ | ★**改完必须先跑 `python3 state/compare_arm_official.py --self-test` (★必须 ALL TESTS PASS·rc=0★)** ★ |

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/compare_arm_official.py --self-test ; echo "SELFTEST_RC=$?"
# ★然后: 用改好的生成器 + 官方同配方重出 stage-1, 再走 S8-1 的链 ★
ARM=C2_production_fix
mkdir -p tmp/iss334/arms/$ARM
bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py    # ★env 与官方配方逐字一致★
```

★**验收读数** ★

| # | 命令 | 合格 | 不过怎么办 |
|---|---|---|---|
| 1 | `python3 state/compare_arm_official.py --self-test` | ★**rc=0** ★ | ★**非 0 ⇒ 闸被改坏了 ⇒ 立即回滚 (★MEMORY: 改在产生点也要有回归★)** ★ |
| 2 | `python3 state/pair_copper_table.py <新stage-1> \| grep <24 个零铜网>` | ★**24 条里至少 1 条铜长 > 0.000** ★ | ★**全是 0.000 ⇒ C2 也没救回 ⇒ 剩下的只有 need-4 (按必需性砍掉)** ★ |
| 3 | ★**套 S8-1 的链, 然后跑 §3-2 的 ①②③④⑤** ★ | ★**GATE_RC=0 · DRC_RC=0 · 段数在区间内** ★ | 不过 ⇒ REJECT |

---

## S8-5 ★收口: 板 md5 只变这一次 ★

★**只有这一节允许写 `HW/PCB/demo_mainboard.kicad_pcb`** ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
WINNER=<S8-2 / S8-3 / S8-4 里 rc=0 的那条臂>
FINAL=/tmp/chain_$WINNER/final_chain.kicad_pcb
# ★① 收口前最后一次三计数 (★退铜名单必须空·差分死腿必须空★)
python3 state/compare_arm_official.py $FINAL HW/PCB/demo_mainboard.kicad_pcb ; echo "GATE_RC=$?"
# ★② 备份旧板 (★不许覆盖没备份★)
cp HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb.bak_$(date +%Y%m%d_%H%M)
# ★③ 只在这一步覆盖 ★
cp $FINAL HW/PCB/demo_mainboard.kicad_pcb
# ★④ 覆盖后立刻复验 (★md5 变了才是"板只改一次"的证据★)
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
python3 state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb ; echo "DRC_RC=$?"
```

★**验收读数** ★

| # | 项 | 合格 | 不过怎么办 |
|---|---|---|---|
| 1 | ★**退铜名单** ★ | ★**空** ★ | ★**非空 ⇒ 回滚 (`cp` 回 .bak) ⇒ REJECT** ★ |
| 2 | ★**差分死腿** ★ | ★**空** ★ | ★**非空 ⇒ 回滚 ⇒ REJECT** ★ |
| 3 | DRC | ★**viol = 0** ★ | ★**非 0 ⇒ 回滚** ★ |
| 4 | ★**板 md5** ★ | ★**与交卷前的 `611b869e13518c3c023fb178f91a0075` 不同** ★ | ★**相同 ⇒ 说明没真的换板 (★或换成了几何等价的板·那也不算数★)** ★ |
| 5 | ★**段数 / 过孔** ★ | ★**16,283~19,901 / 390~476** ★ | ★**越界 ⇒ 回滚** ★ |
| 6 | ★**零铜网数** ★ | ★**≤ 24 (只许少不许多)** ★ | ★**变多 ⇒ 回滚 (★说明打死了别的网★)** ★ |

★**收口后**: ★**把新板的 md5 写进 `HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md` (★若该文件由他人维护 ⇒ 只在分片里报, 别直接改正文★)** ★

---

## §附 · 板那一趟的【不许做】清单

1. ★**不许**用现生成器的产物当起跑线 (★2,492 段 ⇒ 不可比★)
2. ★**不许**拿"unc 变少"当成功 (★★老教训: unc 最少的板自己就 REJECT★★)
3. ★**不许**在对照臂没复现官方的情况下开候选臂
4. ★**不许**跳过 §3-6-2 的段数/过孔区间自检
5. ★**不许**跑 `state/gen_production_pack.sh` (★投产包重出不在本趟★)
6. ★**不许**把 S8-2/3/4 的中间产物直接写进 `HW/PCB/` (★只允许 S8-5 那一次★)
