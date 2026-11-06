# ★★★**pair-aware 长距布线改造方案 (2026-11-06 12:3x)**

> ★**这不是"想法", 是从实测数据倒推出来的方案** ⇒ ★**每个依据都有出处**
> ★**目标**: 把官方板剩下的 45 条未连接 (23 条 >40mm · 25 条是差分腿) 清零

---

## 1. ★**问题陈述 (实测)**

- ★**官方板**: 18092 段 / 433 孔 · **unconnected 45** · DRC 0 · parity rc=0 · md5 `611b869e`
  ⇒ ★**G1 要求 unconnected = 0** (★`state/stage_gate.py` 的 `routing_required` 判据)
- ★**剩余 45 条的构成 (机器统计, `state/probe_unconnected_worklist.py`)**:
  - 端点配对: CONN↔其他 12 · CAP↔CONN 6 · RES↔SOM_BTB 6 · 其他↔SOM_BTB 5 · JST↔RES 4 · CAP↔SOM_BTB 3 · 其他 5
  - 器件参与条数: **CONN 21 · SOM_BTB 17** · RES 12 · CAP 10 · JST 5 · DIODE 2 · TP 2
  - ★**其中 23 条是差分腿 (DSI/CSI), 距离 3.7~98.5mm**

---

## 2. ★**已排除的路径 (每条都有实测数据 ⇒ 不要重走)**

| 路径 | 实测结果 | 出处 |
|---|---|---|
| ★**调 halo margin** | 0.20→0.0625 (0.125mm 网格半格) 救回 3 条 ⇒ **48→45**; 再降到 0 ⇒ **11 条 clearance 违规** ⇒ **0.0625 是下限** | `/tmp/_nostub_loose.log` |
| ★**直连补段** | 45 条上 **补上 0 条** (全被挡) | `/tmp/_loose_straight.log` |
| ★**纯 A\* 补段** | 最多 **3 条** | `/tmp/_nostub_loose.log` |
| ★**拆挡路 + 补一段** | **补上 0 条** ⇒ ★**13 条"挡路全是承重"** (I2C_B_SDA 2→3 / KEY_VOL_P 1→2 / DSI_D0_CK_P 2→3 / V_SOC_IO 1→2 ...) | `/tmp/_ripguard.log` |
| ★**freerouting 2.1.0 (工业级)** | 成品板 37 轮 score **恒定 996.44** 零改善; 空板上 191→89 unrouted 但仍卡在 BTB 出脚 | `/tmp/fr_progress.log` |
| ★**挪 R_SEL 串阻阵** | v56 unc **58** 更差 (配套 TP 被自动排版挤到 y=8.80 堵住出脚走廊); v58 差分对净 **-2** | `/tmp/v56_R.log` `/tmp/v58_R.log` |
| ★**只缩线宽 (0.15mm)** | v57 差分对净 **0** (救回 2 对, 丢 2 对) | `/tmp/v57_R.log` |
| ★**远端优先布焊盘** | v66 无效 (`CSI_D0_CK_P/N` 仍 True/False) | `/tmp/v66_R.log` |

⇒ ★**⇒ 结论: ★**"只改算法"这条路已被穷尽** ⇒ ★**⇒ 剩下的必须是物理/结构层面的改动**

---

## 3. ★**根因 (纯几何, 已复核)**

### 3.1 ★**SoM BTB 出脚的余量精确为 0**

```
SoM BTB (Hirose DF40C-100DS-0.4V(51)): 0.4mm pitch · 焊盘 0.2mm 宽 × 0.7mm 长 · 双排
沿排方向出线的铜边净距 = pitch − 线半宽 − 焊盘半宽 = 0.4 − w/2 − 0.1

  w = 0.20mm ⇒ 净距 0.2000mm ⇒ ★★余量 0.0000mm (卡在临界, 一个纳米都不剩) ⇒ 实际布不出
  w = 0.15mm ⇒ 净距 0.2250mm ⇒ 余量 0.0250mm ⇒ 可行   ← 6mil, 行业标准
  w = 0.10mm ⇒ 净距 0.2500mm ⇒ 余量 0.0500mm ⇒ 可行   (比 6mil 更挑板厂)
```

### 3.2 ★**"P 通 N 不通"是顺序依赖, 不是不对称**

- ★**P 侧靠 "pair-partner 豁免"** (`gen_pcb_routing._free` 里 `others == {self.pair_partner}`) **先走出去了**
- ⇒ ★**N 侧再想走时 P 的铜已经在那里 ⇒ 真堵死**
- ★**实测 `CSI_D0_CK_N`**: 3 个焊盘 (C_AC 45.90,58.60 / TP 44.50,55.20 / CONN_CAM.17 86.90,51.40)
  ⇒ ★**铜有 50 段 / 0 个过孔, 局限在 x 41.95..47.70** ⇒ ★**连了 2 个点, 第 3 个差 39.47mm**
  ⇒ ★**而 P 侧同目标布到了 x=86.2** ⇒ ★**差别只在"谁先走"**

### 3.3 ★**那 39mm 沿线是堵死的**

```
实测沿线 2mm 内异网铜 **662 条**: F.Cu 241 · In2.Cu 244 · In4.Cu 172 · In6.Cu 5
最近的几条: CSI_MCLK(In4.Cu) 0.002mm · VDD_3V3_IO(F.Cu) 0.005mm · UART_TX(In2.Cu) 0.007mm
⇒ ★**8 层里有 4 层都堵** ⇒ ★**单根线走不过去 ⇒ 必须"先占走廊, 再并行铺两根"**
```

---

## 4. ★**方案: pair-aware 长距规划 (★真正的下一步)**

### 4.1 ★**核心思想**

★**不再"P 布完再布 N"** ⇒ ★**改成"先为整对规划一条走廊, 再在走廊内并行铺 P 和 N"**

★**具体做法 (按工程量从小到大)**:

#### ① ★**"走廊优先"的成对 A\*** (★**推荐先做这个, 改动最小**)
- ★**在 `route_diff_pair` 里, 改成**先做一次**"走廊 A\*"**: ★**状态是 (格, 是P还是N)** ⇒ ★**两条线同时长大**
- ★**走廊 A\* 的启发式**: ★**让 P 和 N 的代价函数都拉向彼此** (★**已有的 `build_pair_guide` / `pair_block` 机制可以复用**)
- ★**关键**: ★**P 侧不是"先布完再布 N", 而是"每一步都在考虑另一侧还没走的部分"**
- ★**⇒ 期望效果**: ★**N 侧不会再被 P 侧的铜堵死** ⇒ ★**"CSI_D0_CK_P/N" 这类从 True/False 变 True/True**

#### ② ★**长距主干优先 (trunk)**
- ★**差分对的长距段 (主干) 应该先规划**, ★**再布支线**
- ★**现有 `trunk_p` / `trunk_n` 参数就是干这个的** ⇒ ★**⇒ 只需把"主干焊盘对"的挑选规则改好**
- ★**怎么挑主干**: ★**取"两端距离最远"的那对焊盘** (★**不是 MST 的近端**)

#### ③ ★**N 侧的"预留走廊"**
- ★**P 侧走过的路径, 给 N 侧留一条平行走廊** (★**宽度 = 0.5mm**)
- ★**实现**: ★**P 侧 `_emit_path` 时, 同时在 `pair_block` 里给 N 留位置** ⇒ ★**N 侧走时那条走廊是"自己的"**

### 4.2 ★**配套: 必须同时做的三件事 (★本轮实测的教训)**

| # | 改动 | 依据 |
|---|---|---|
| 1 | ★**`PCB_W_MIN=0.15`** (env 门控, 已交付) | §3.1 ⇒ ★**余量 0 ⇒ 必须降线宽** |
| 2 | ★**`PCB_VIA_CHECK_ALL_CLS=1`** (env 门控, 已交付) | ★**`_via_ok` 查 halo[2] ⇒ 看不见 0.25mm 走线 ⇒ 12 条 clearance 违规** |
| 3 | ★**`_stub_clear` 的 need 跟着 W_MIN 走** (已交付) | ★**need 硬编码 0.299 ⇒ W_MIN=0.15 时偏严 0.024mm ⇒ 把能过的直道判死** |

### 4.3 ★**边界条件 (★必须提前认清)**

- ★**0.15mm 要板厂确认** ⇒ ★**这是唯一的外部依赖** ⇒ ★**6mil 是行业标准, 但本板厂能力文件写的是 0.20mm**
- ★**impedance 要复核**: ★**出脚段只占 lane 的 <2% ⇒ 对 100Ω 差分基本无影响** (★`HW/PCB/STACKUP_IMPEDANCE.md`)
- ★**改 `gen_pcb_routing.py` 会破坏臂间 A/B 可复现性** ⇒ ★**★所有改动必须 env 门控, 默认行为逐位不变**

---

## 5. ★**验收判据 (★沿用现成的, 不要新造)**

- ★**晋级闸**: `python3 state/compare_arm_official.py <候选> <官方板>` ⇒ ★**必须 ACCEPT**
  (硬指标: DRC=0 + 退铜名单空 + 差分死腿空 + 逐网孤岛不变多 + 至少一项变好)
- ★**闸自测**: `python3 state/compare_arm_official.py --self-test` ⇒ ★**必须 ALL TESTS PASS** (★v44/v46/v47 实测坏板当回归夹具)
- ★**晋级**: `bash state/promote_board_file.sh <候选板>` ⇒ ★**自动跑闸复检/parity/备份/叠层/铜皮/终点线自检+自动回滚/投产包/全门禁**
- ★**放行**: ★**只有 unconnected=0 + DRC=0 + 全门禁 rc=0 才盖章** ⇒ ★**当前 stage_gate rc=1 ⇒ G1 仍开**

---

## 6. ★**已经交付的工具 (本轮)**

| 工具 | 作用 |
|---|---|
| `state/promote_board_file.sh` | ★**把任意路径候选板按 finish_line 纪律晋级** (含闸复检 + 自动回滚) |
| `state/patch_astar_gated.py` | 无 stub A\* + **换层点真实几何闸** + 两遍 A\* 预避让 |
| `state/rip_escape_guard.py` | 拆挡路 + **承重守卫** (全层查挡路) |
| `state/fix_via_halo_levels.py` | 过孔真实几何复核 + 挪开 |
| `state/import_ses_direct.py` | Specctra SES 直读导入器 (KiCad 的 ImportSpecctraSES 对 freerouting 2.x 返回 False) |
| `state/run_grid_ladder.sh` | 网格阶梯实验 (margin = 网格半格) |
| `state/v57..v66_arms.sh` | 各实验臂 (env 门控组合) |

★**env 门控一览 (★全部默认关 ⇒ 既有臂逐位可复现)**: `PCB_W_MIN` · `PCB_VIA_CHECK_ALL_CLS` · `PCB_PAIR_ESC_AVOID` · `PCB_PAIR_P_FALLBACK` · `PCB_PAD_ORDER_FAR_FIRST`
