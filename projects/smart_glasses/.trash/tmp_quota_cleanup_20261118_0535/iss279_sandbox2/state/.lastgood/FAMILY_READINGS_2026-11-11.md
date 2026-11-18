# ★mw/mg 族链终板读数 (收口表) ★

> 出品: `state/close_family_readings.sh` (2026-11-11 07:5x, main 会话)
> ★**每块板都 fresh 跑了一次 `kicad.sh pcb drc` (规则随同目录 .kicad_pro 同源)** ★
> ★**官方板那一行 = 官方板本体 (md5 611b869e) 的对照基准** ★

| 板 | 段 | 孔 | DRC违规 | unc 条 | unc 网名 |
|---|---:|---:|---:|---:|---:|
| baseline_v76mg0_chain | 3297 | 470 | 29 | 25 | 23 |
| baseline_v76mw0_chain | 3383 | 442 | 0 | 29 | 24 |
| baseline_v76mx0_chain | 3383 | 442 | 0 | 29 | 24 |
| baseline_v76mv0_chain | 3376 | 441 | 0 | 29 | 24 |
| baseline_v76mj0_chain | 3394 | 446 | 16 | 28 | 23 |
| best_v76mg1_clrfix | 3304 | 471 | 0 | 25 | 23 |
| best_unc23_clrfix | 3364 | 475 | 0 | 23 | 21 |
| candidate_v76mx1L_chain | 3650 | 457 | 0 | 26 | 22 |
| candidate_official_p41 | 18418 | 448 | 0 | 41 | 39 |
| board_nostub_loose_unc45_20261106_0705 | 18092 | 433 | 0 | 45 | 43 |

## ★判读 (★本轮实跑出来的★)

- ★**生成器族板 (mg0/mw0/mx0/mv0/mj0 + mg1 + mx1L)** ⇒ 段数只有 3300~3650 (★官方板 18092★) ⇒ ★**不同工艺, 不能直接比 unc**
- ★**同臂单变量 (★本轮真测★)**: `best_unc23_clrfix` (★loose 步 margin **0.031**★) vs `best_v76mg1_clrfix` (★loose 步 margin 0.0625★)
  ⇒ ★**交集 21 · 仅 0.031 侧 0 · 仅 0.0625 侧 2** ⇒ ★**0.031 纯赚 2 个网, 零新断** ⇒ 但【同一块板 vs 官方板 = REJECT】⇒ ★**不能替换官方板** ★
- ★**官方对照闸 (名单制) 实测判决**: `best_unc23_clrfix` ⇒ ★**REJECT** (★退铜 4 个网: `CARRIER_BOARD_EN`/`CSI_MCLK_SRC`/`SPI_CSn_BOOT`/`USB_CC1` + 逐网孤岛变多 11 个网★)
- ★⇒ ⇒ **唯一可晋级候选仍是 `candidate_official_p41`** (★官方板血脉增量: unc 41·39 网 / DRC 0 / 退铜0·死腿0·孤岛0 / compare_arm_official rc=0 ACCEPT★)
