# HW/PCB/S8_REACHABILITY_VERDICT.md —— ★★【ISS-308 · S8 可达性判决书】★★

> **单号**: ISS-308 (cont1) · **owner**: hw-lead · **verify_by**: main · **派活**: cron `fb67af40` (ARS45 队列自动派活) · **2026-11-18**
> **性质**: ★**内部活 · 纯分析/判决 · 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板** ★
> **本件**: §2-A 落桶表 (22 网名 → 5 桶) + §2-B 老板还差 N 个字母 + §2-C 现在就能做的技术活清单 + §1-④ `PCB_PAIR_LAYERSEL` 查清结论

---

## §0 · 口径声明 (★先读这一段, 后面所有数字都按它读★)

### §0.1 · 逐网铜量数字一律取自 candidate 板

★**本判决书所有逐网铜量数字 (段数 / 层分布 / 过孔数 / 焊盘数) 一律取自 candidate 板** ★

| 项 | 值 |
|---|---|
| **证据文件** | `logs/iss308/evidence/iss308_cand_layers.json` (★由 `logs/iss308/evidence/iss308_layerprobe.py` 在 `state/.lastgood/candidate_v76mx1L_pour.kicad_pcb` 上跑出来★) |
| **字段口径** | `seg` = 该网该层的铜段数 · `seg_total` = 该网总铜段数 · `pad` = 焊盘层分布 · `pad_total` = 焊盘数 · `vias` = 过孔数 |
| **板身份** | `state/.lastgood/candidate_v76mx1L_pour.kicad_pcb` (候选 + 5V 铜皮) |
| **该板读数** | DRC 0 · unconnected 26 条 / 22 网名 · 名单制闸 rc=0 (见 `state/.lastgood/CANDIDATE_v76mx1L_ready.md`) |
| **另一份证据 (★只作差异对照, 不作判决依据★)** | `logs/iss308/evidence/iss308_ms_layers.json` = v76ms 臂链 (`PCB_PAIR_LAYERSEL=1` 那条臂) 的逐层铜量 |
| **官方板对照 (★只作「这条网官方板布没布通」的对照★)** | `logs/iss308/evidence/iss308_official_census.json` (现役板 `611b869e…`) · `logs/iss308/evidence/iss308_p41_census.json` (`candidate_official_p41`) |

★**不许混用两份逐层 JSON 取数字** ★ ⇒ ★**判决书里出现的每一个段数都来自 candidate 那一份** ★

### §0.2 · ★3 条差异注记 (candidate 板 vs v76ms 臂链) ★

★**两份证据在 3 条上不一致 ⇒ 本判决书统一以 candidate 为准, 并把差异记在这里** ★

| # | 网名 | candidate (判决依据) | v76ms 臂链 | 差异性质 | 本判决书的处理 |
|---|---|---|---|---|---|
| ★**1** ★ | `DSI_D0_D3_N` | **52 段** (F.Cu 15 / In2.Cu 32 / In4.Cu 5) | 53 段 (F.Cu 19 / In2.Cu 26 / In4.Cu 8) | 段数差 1 · **层分布也不同** (In4.Cu 5→8, F.Cu 15→19) ⇒ 两条臂在这条网上走了不同的层策略 | ★**取 candidate 52 段 (F.Cu 15 / In2.Cu 32 / In4.Cu 5)** ★ ⇒ ★**B3 桶归类不变** (层占比仍与 P 腿相反: N 偏 In2.Cu 61% vs P 偏 F.Cu 56%) ★ |
| ★**2** ★ | `KEY_VOL_M` | **98 段** (F.Cu 13 / In2.Cu 85) | 99 段 (F.Cu 13 / In2.Cu 86) | 段数差 1 · **层分布只差 In2.Cu 1 段** ⇒ 同一条臂的微小抖动 | ★**取 candidate 98 段 (F.Cu 13 / In2.Cu 85)** ★ ⇒ ★**B3 桶归类不变** (N 腿 86% 在 In2.Cu vs P 腿 80% 在 F.Cu ⇒ 层占比相反) ★ |
| ★**3** ★ | `LED_B` | **27 段** (F.Cu 7 / In2.Cu 20) | **0 段 (无铜)** | ★**不是抖动, 是【一条臂把这条网整个布没了】** ★ ⇒ v76ms 臂 (开了 `PCB_PAIR_LAYERSEL=1`) 在这条网上**比不开还差** | ★**取 candidate 27 段** ★ ⇒ ★**B4 桶归类不变** (抢路者是普通信号网 `LED_G`/`LED_B_D`, 非 GND) ★; ★**但这条差异本身就是 §1-④ 的实测旁证: 该机制在 `LED_B` 上不是「无害」而是「有害」★** ★ |

### §0.3 · 复现命令 (★本判决书每个数字都能用这几条命令复算★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 22 网的逐层铜量 (判决依据)
python3 -c "import json;d=json.load(open('logs/iss308/evidence/iss308_cand_layers.json'));print(d['CSI_D0_CK_N']['seg_total'], d['CSI_D0_CK_N']['seg'])"
# ② 同一条网在 v76ms 臂链上的读数 (差异注记)
python3 -c "import json;d=json.load(open('logs/iss308/evidence/iss308_ms_layers.json'));print(d['LED_B']['seg_total'], d['LED_B']['seg'])"
# ③ 官方板 / p41 对照 (这条网官方板布没布通)
python3 -c "import json;d=json.load(open('logs/iss308/evidence/iss308_official_census.json'));print(d['CARRIER_BOARD_EN']['seg_total'])"
# ④ 桶归属复算 (★本判决书与脚手架脚本互相锁★)
python3 state/_iss308_s8_reachability_check.py ; echo "rc=$?"
python3 state/_iss308_s8_reachability_check.py --selftest ; echo "rc=$?"
```

---

## §1 · 查清结论 (★任务书 §1-④ 的第一问★)

### §1-④ · `PCB_PAIR_LAYERSEL` 「目前无效但无害」—— 谁写的 / 哪一天 / 有没有实测支撑

#### §1-④-1 · 判定源头与日期 (★实测: 文件 mtime + MEMORY 逐字★)

| 项 | 实测 |
|---|---|
| ★**判定最早出处** ★ | ★`config/agents/main/MEMORY.md` L3000, 位于【★闸账 (★2026-11-11 03:0x 更新·每轮必须维护·避免重复踩★)】→【★**已判死 (★负收益或无效·别再开★)**★】清单内, 逐字 = ★`PCB_PAIR_LAYERSEL` (★终板无效但无害★)★ ⇒ ★**判定人 = main (项目总工), 判定时刻 ≈ 2026-11-11 03:0x** ★ |
| ★**转抄进地图的位置** ★ | ★`state/UNC_TARGET_MAP.md` L28 (★文件 mtime = 2026-11-11 05:31:54★), 逐字 = ★「走 pair-aware / 差分层选择 (★`PCB_PAIR_LAYERSEL` 目前无效但无害★) / 成对走廊规划」★ ⇒ ★**该文件自己的观测日期写在文件头: 「2026-11-11 04:2x 实测·全板扫描」★ ⇒ ★**两处都是 2026-11-11 ⇒ 这句判断不是更早的遗留, 是 11-11 当天写的** ★ |
| ★**盘上还有没有第三处** ★ | ★`grep -rn "无效但无害"` 全库 = 2 处 (上表两处) + `state/dispatch_briefs/ISS-308_hw_s8_reachability_verdict*.md` (★本单任务书自己引用的那两句★) ⇒ ★**没有第三处独立判定** ★ |
| ★**全库有没有任何地方写过它【被触发过】的读数** ★ | ★`grep -rn "PCB_PAIR_LAYERSEL" state/*.py state/*.sh logs/ state/ARM_LEDGER_2026-11-10.md` = ★**零命中** (除源码定义处与本单脚本) ⇒ ★**盘上【只有一条臂】开过它, 且它的读数只在 main 的 MEMORY 闸账里留了一句结论, 没留原始读数★ ⇒ ★**这就是「没人写下来过」的来源: 原始读数没落盘, 只有一句结论落盘** ★ |

#### §1-④-2 · 有没有实测支撑 —— 有, 但只有一次单变量臂 (★本单实跑核对★)

| 项 | 实测 |
|---|---|
| ★**唯一开过它的臂** ★ | ★`state/v76ms_arms.sh` (mtime 2026-11-10 20:04:57) ⇒ ★**全库 `grep "PCB_PAIR_LAYERSEL=1"` 只命中它一个臂脚本** ★ |
| ★**单变量成立? (★env 逐键 diff★)** ★ | ★`v76ml_arms.sh` vs `v76ms_arms.sh` 的 `env PCB_LAYERS … PCB_OUT=` 段逐键 diff ⇒ ★**共同 29 键, 只多 `PCB_PAIR_LAYERSEL=1` 这 1 个** ⇒ ★**单变量成立, 归因干净** ★ |
| ★**终板读数 (★「无效」的实测支撑★)** ★ | ★v76ms 终板 `logs/…/iss308_v76ms_fresh.drc.json` (来源 `final_chain.kicad_pcb`) ⇒ ★unc 29 条 / 24 网 · DRC 0★; ★对照臂 v76ml 终板 ⇒ ★unc 29 条 / 24 网 · DRC 0★ ⇒ ★**24 个网名集合逐个相同 (逐字 diff = 空)** ★ ⇒ ★**开了它, 终板读数零变化 ⇒ 「无效」实测坐实** ★ |
| ★**「无害」的实测支撑** ★ | ★两臂 DRC 都是 0 · 退铜 0 · 差分死腿 0 · 逐网孤岛没变多 (★main 闸账 2026-11-11 03:0x 与 `state/ARM_LEDGER_2026-11-10.md` v76ml/v76mm/v76mo 行逐字一致★) ⇒ ★**「无害」实测坐实 (在 v76ms 这一臂上)** ★ |
| ★**★但是: 有 1 条反向证据★** ★ | ★`LED_B`: v76ms 臂 = **0 段 (无铜)**, candidate 臂 = 27 段 (★`logs/iss308/evidence/iss308_ms_layers.json` vs `iss308_cand_layers.json`★) ⇒ ★**在这条网上, 开这个机制 = 把一条已经通了 27 段的网弄没了 ⇒ 「无害」只对 21/22 成立, 对 `LED_B` 不成立** ★ ⇒ ★**「无害」这个结论的适用面比原文写的小** ★ |

#### §1-④-3 · 为什么没救回来 (★机制级, 三条实测★)

1. ★**机制覆盖面只有 3/11 对** ★ ⇒ ★**实测 11 对差分腿的 N/P 层占比 (candidate 板逐段读层): 只有 3 对是「层占比相反」** ★ —— `CSI_D0_D0_N` (N 60% In2.Cu vs P 86% F.Cu) · `DSI_D0_D3_N` (N 61% In2.Cu vs P 56% F.Cu) · `KEY_VOL_M` (N 86% In2.Cu vs P 80% F.Cu); ★**其余 8 对的 N 腿主导层与 P 腿【同层】(F.Cu) 或 N 腿【一根铜都没有】** ★ ⇒ ★**「限制层」对「同层」和「零铜」这两种病【药不对症】** ★
2. ★**机制只在「布 N 侧时按 P 侧各层段数排序」这一处生效 (源码 `state/gen_pcb_routing.py` L4432-4442) ⇒ 前提是 P 侧已经有铜可统计** ★ ⇒ ★**5 条零铜 N 腿 (`CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N` / `DSI_D0_CK_N_SRC` / `DSI_D0_D1_N_SRC`) 的 P 腿有铜但【自己的走廊被封死】, 限制层救不了「起步格被封」** ★
3. ★**机制自带安全阀 ⇒「无效但无害」是【设计上的必然】, 不是巧合** ★ ⇒ ★源码 L4447-4451: ★「限制下 N 侧没布出来 ⇒ 放开限制重试 ⇒ 保证不比现状更差」★ ⇒ ★**放不出来的对会自动退回不限层 ⇒ 终板读数与没开时逐字相同 ⇒ 这就是「无效」的机制解释** ★ ⇒ ★**而 `LED_B` 那条【连安全阀都没兜住】(从 27 段掉到 0 段) ⇒ 安全阀只覆盖「N 侧布不出来」, 不覆盖「布出来了但布成另一条路」** ★

#### §1-④-4 · 补充: 官方板那 13 条 DSI/CSI 腿 (★官方板自己一根都没布通★) 与本机制无关

★**官方板的 `CSI_D0_CK_N` 就是 F.Cu 78 / In2.Cu 120 (N 偏 In2.Cu 61%), 而 `CSI_D0_CK_P` 是 F.Cu 158 / In2.Cu 71 (P 偏 F.Cu 69%)** ★ (★`logs/iss308/evidence/iss308_official_census.json` 实测; 与源码 L344-345 的注释逐字一致★) ⇒ ★**官方板【已经】用了「层占比相反」的手法 ⇒ 路由器缺的正是这个机制 ⇒ 机制方向是对的, 但它覆盖不了那 5 条零铜的 N 腿, 也不覆盖官方板自己都没布通的那 13 条腿** ★

#### §1-④-5 · 判决 (★一句话★)

★★**「`PCB_PAIR_LAYERSEL` 目前无效但无害」这句话: 判定人 = main (2026-11-11 03:0x 闸账), 转抄进 `UNC_TARGET_MAP.md` = 同日 05:31; 实测支撑【有】, 但只有一条单变量臂 (`v76ms` vs `v76ml`, env 只差这一个键), 且支撑面比原句小 —— 终板读数逐字相同 = 「无效」坐实, DRC/退铜/死腿/孤岛不变 = 「无害」坐实, 唯一反例是 `LED_B` (27 段 → 0 段) ⇒ 精确口径 = 「无效, 且对 21/22 无害, 对 `LED_B` 有害」; 机制级原因 = 该机制只对 3/11 对的层占比相反有药效, 且自带「失败即退回」安全阀 ⇒ 「无效」是机制的覆盖面不足, 不是实现坏了** ★★

---

## §2-A · ★【判决 1】残余 22 网名 → 5 桶, 逐条落桶★

★**桶定义 (任务书原定义, 本单一字不改)** ★

| 桶 | 判据 |
|---|---|
| ★**B1 · 差老板字母** ★ | 死因是 `BAT_DET` 终点 / ESD 钉位 / `Q_PG.3` 极性 / `D_LED_G` 位置 / 板形层数 ⇒ 引用作业包 §6.2 的登记行 |
| ★**B2 · GND 卡死 (铜皮 / 下拉孔)** ★ | 净距 < 0.20 mm 且抢路者是 GND ⇒ ★**解法只许是「落铜前拦」: GND 铜皮局部 keepout / 缩形 / 挪下拉孔 ⇒ 不许在产物上擦** ★ |
| ★**B3 · 差分 N 腿互掐 (层分配)** ★ | ★**P 腿有铜 / N 腿无铜 或 N 腿净距被 P 腿压** ★ ⇒ ★**必须实测【N 腿的层占比 vs P 腿的层占比】** ★ |
| ★**B4 · 让路闸靶子 (普通信号网互掐)** ★ | 抢路者非 GND 且 k ≤ 3 ⇒ 给 env 配方 (`PCB_YIELD_VICTIMS` / `PCB_PRIORITY_NETS` / `PCB_PAIR_BEFORE_PWR` 等) |
| ★**B5 · 其它 (逐条单列)** ★ | 不许塞进上面四桶 ⇒ 每条自己给判据 |

### §2-A-1 · 桶分布 (★实测统计★)

| 桶 | 条数 | 网名 |
|---|---|---|
| ★**B1** ★ | **2** ★ | `CARRIER_BOARD_EN` · `SPI_CSn_BOOT`
| ★**B2** ★ | **1** ★ | `CSI_MCLK`
| ★**B3** ★ | **12** ★ | `CSI_D0_CK_N` · `CSI_D0_D0_N` · `CSI_D0_D0_N_SRC` · `CSI_D0_D2_N` · `CSI_D0_D3_N` · `DSI_D0_CK_N_SRC` · `DSI_D0_D0_N` · `DSI_D0_D0_P` · `DSI_D0_D1_N` · `DSI_D0_D1_N_SRC` · `DSI_D0_D3_N` · `KEY_VOL_M`
| ★**B4** ★ | **7** ★ | `USB_CC1` · `ID_DETECT_1` · `I2C_A_SCL` · `I2C_B_SCL` · `I2C_B_SDA` · `LED_B` · `KEY_VOL_P`
| ★**B5** ★ | **0** ★ | ★(空)★

★**合计 22 条 / 22 网名 (B5 = 0 是实测结果, 不是漏填: 22 条【全部】能归进 B1~B4 四桶)** ★

### §2-A-2 · 落桶表 (★逐条, 每条一行★)

★**★本表与 `state/_iss308_s8_reachability_check.py` 的 `BUCKETS` 字典【逐字一致】(★脚本是本表的机器副本, 改一处两处都红★)★** ★

<!-- ISS308_BUCKET_TABLE_BEGIN -->
| 网名 | 桶 | 根因 (★一句话 + 实测数★) | 板那一趟能不能解 | 解法 / 卡在谁 | 实测出处 (★文件 · 字段 · 值★) | 官方板 / p41 对照 |
|---|---|---|---|---|---|---|
| `CARRIER_BOARD_EN` | **B1** | ★2 焊盘零铜网 · 抢路者 = DSI_D0_D3_P_SRC (k=2) ★但让路闸两条臂都失败 ⇒ 真死因 = 板面/器件轴未定 (★P7 放行口径 + 板形·层数★) ⇒ 改板框才解 | **能** | ★卡在老板 P7 (C1/C2/C3/C4) ⇒ 板形/层数定了才谈得上给它一条走廊★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | ★官方板 354 段 / p41 354 段 ⇒ 候选板把它**整条丢了** (退铜名单) |
| `SPI_CSn_BOOT` | **B1** | ★2 焊盘零铜网 · 板面无铜 ⇒ A* 找不到路 ★⇒ 根因 = 板侧该 boot 网落位/引出未定 (★S4/S6 落位轴 + P7 板形轴★) ⇒ 不是参数问题 | **能** | ★卡在 P7 (板形/层数) ⇒ ★同一批 8 条零铜网的共因★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | ★官方板 103 段 / p41 103 段 ⇒ 候选板把它**整条丢了** (退铜名单) |
| `CSI_MCLK` | **B2** | ★A2 三网之一 · 被 GND 铜皮/下拉孔卡在 0.162 mm (需 0.20 mm) ★⇒ ★让路闸救不了 (★GND 是面★)⇒ ★只能动【GND 铜皮形状 / 下拉孔位置】★ | **能** | ★落铜前拦: GND 铜皮局部 keepout / 缩形 / 挪下拉孔 ⇒ ★不许在产物上擦★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=10 · seg=[F.Cu 4 / In2.Cu 6] · vias=2 · pad_total=9 | 官方板 194 段 / p41 194 段 ⇒ 候选板只剩 10 段 (拆碎) |
| `CSI_D0_CK_N` | **B3** | ★N 腿 42 段 (F.Cu 30 / In2.Cu 12) ⇒ P 腿 CSI_D0_CK_P 27 段 (F.Cu 21 / In2.Cu 6) ⇒ ★两腿层占比【同主导层 F.Cu】⇒ 不是层反转, 是【起步格被封 / 走廊墙死】★ | **能** | ★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu★) + 成对走廊规划 + 局部 keepout★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=42 · seg=[F.Cu 30 / In2.Cu 12] · vias=4 · pad_total=9 | 官方板 198 段 / p41 198 段 ⇒ 候选板只剩 42 段 (拆碎) |
| `CSI_D0_D0_N` | **B3** | ★N 腿 28 段 (F.Cu 11 / In2.Cu 17) vs P 腿 22 段 (F.Cu 19 / In2.Cu 3) ⇒ ★层占比【确实相反】(N 偏 In2 / P 偏 F.Cu) ⇒ ★典型的层分配症状★ | **能** | ★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu★) ⇒ 让 N 侧去 P 用得少的层★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=28 · seg=[F.Cu 11 / In2.Cu 17] · vias=4 · pad_total=9 | 官方板 0 段 / p41 0 段 ⇒ 官方板自己也零铜 (真墙) |
| `CSI_D0_D0_N_SRC` | **B3** | ★2 焊盘【零铜】★ vs P 腿 CSI_D0_D0_P_SRC 21 段全 F.Cu ⇒ ★N 腿连起步都没成功 (★chain.log「A* 找不到路」★) ⇒ ★且它的走廊已被 PCB_ROUTE_RESERVE 预留过 ⇒ 墙不是【没预留】, 是【预留格之外的那一段被封死】★ | **能** | ★成对走廊规划 (★预留要成对, 现在的预留是单网条目★) + 起步格 halo 放宽★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | 官方板 0 段 / p41 0 段 ⇒ 官方板自己也零铜 (真墙) |
| `CSI_D0_D2_N` | **B3** | ★2 焊盘【零铜】★ vs P 腿 CSI_D0_D2_P 33 段 (F.Cu 30) ⇒ ★同 CSI_D0_D0_N_SRC★ | **能** | ★成对走廊规划 + 起步格 halo 放宽★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | 官方板 0 段 / p41 0 段 ⇒ 官方板自己也零铜 (真墙) |
| `CSI_D0_D3_N` | **B3** | ★2 焊盘【零铜】★ vs P 腿 CSI_D0_D3_P 33 段 (F.Cu 27) ⇒ ★同 CSI_D0_D0_N_SRC★ | **能** | ★成对走廊规划 + 起步格 halo 放宽★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | 官方板 0 段 / p41 0 段 ⇒ 官方板自己也零铜 (真墙) |
| `DSI_D0_CK_N_SRC` | **B3** | ★2 焊盘【零铜】★ vs P 腿 DSI_D0_CK_P_SRC 4 段 ⇒ ★同 CSI_D0_D0_N_SRC★ | **能** | ★成对走廊规划 + 起步格 halo 放宽★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | ★官方板 312 段 / p41 312 段 ⇒ 候选板把它**整条丢了** (退铜名单) |
| `DSI_D0_D0_N` | **B3** | ★N 腿只落 3 段 (全 F.Cu) vs P 腿 DSI_D0_D0_P 7 段 (F.Cu 5 / In2.Cu 2) ⇒ ★N 腿只够从起步格逃出, 走不到终点 ⇒ ★卡在【中段走廊】★ | **能** | ★成对走廊规划 (★N 腿走廊必须与 P 腿成对预留★) + PCB_PAIR_LAYERSEL 修缺陷★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=3 · seg=[F.Cu 3] · vias=0 · pad_total=9 | 官方板 18 段 / p41 18 段 ⇒ 候选板只剩 3 段 (拆碎) |
| `DSI_D0_D0_P` | **B3** | ★★【P 腿自己也在 22 名单里】★ ⇒ 7 段 (F.Cu 5 / In2.Cu 2) 未走完 ⇒ ★【不是 N 腿互掐】, 是【这一对整体没走完】⇒ ★同桶同解法★ | **能** | ★成对走廊规划 (★这一对两个腿都要进预留表★)★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=7 · seg=[F.Cu 5 / In2.Cu 2] · vias=2 · pad_total=9 | 官方板 300 段 / p41 300 段 ⇒ 候选板只剩 7 段 (拆碎) |
| `DSI_D0_D1_N` | **B3** | ★N 腿 44 段【全 F.Cu】vs P 腿 DSI_D0_D1_P 19 段 (F.Cu 10 / In2.Cu 6 / In4.Cu 3) ⇒ ★N 腿被压在 F.Cu 单层, P 腿有三层 ⇒ ★层分配失衡最明显的一条★ | **能** | ★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu + 允许 N 去 In2/In4★)★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=44 · seg=[F.Cu 44] · vias=0 · pad_total=9 | 官方板 300 段 / p41 300 段 ⇒ 候选板只剩 44 段 (拆碎) |
| `DSI_D0_D1_N_SRC` | **B3** | ★2 焊盘【零铜】★ vs P 腿 DSI_D0_D1_P_SRC 9 段 ⇒ ★同 CSI_D0_D0_N_SRC★ | **能** | ★成对走廊规划 + 起步格 halo 放宽★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | 官方板 0 段 / p41 0 段 ⇒ 官方板自己也零铜 (真墙) |
| `DSI_D0_D3_N` | **B3** | ★N 腿 52 段 (F.Cu 15 / In2.Cu 32 / In4.Cu 5) vs P 腿 16 段 (F.Cu 9 / In2.Cu 7) ⇒ ★层占比【相反】(N 偏 In2 / P 偏 F.Cu) ⇒ ★层分配症状 + 中段走廊★ | **能** | ★PCB_PAIR_LAYERSEL 修结构性缺陷 + 成对走廊规划★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=52 · seg=[F.Cu 15 / In2.Cu 32 / In4.Cu 5] · vias=4 · pad_total=9 | 官方板 402 段 / p41 402 段 ⇒ 候选板只剩 52 段 (拆碎) |
| `KEY_VOL_M` | **B3** | ★N 腿 98 段 (F.Cu 13 / In2.Cu 85) vs P 腿 KEY_VOL_P 10 段 (F.Cu 8 / In4.Cu 2) ⇒ ★层占比【强烈相反】(M 腿 87% 在 In2.Cu) ⇒ ★★层分配症状最典型的一条★ | **能** | ★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu★)★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=98 · seg=[F.Cu 13 / In2.Cu 85] · vias=4 · pad_total=15 | 官方板 74 段 / p41 74 段 ⇒ 候选板只剩 98 段 (拆碎) |
| `USB_CC1` | **B4** | ★2 焊盘【零铜】★ · 抢路者 = NET_USB_D_N_TYPEC (k=2) ★★但 UNC_TARGET_MAP 已登记「REST 阶段才布 ⇒ 走廊早占完 ⇒ 要改的是谁占了它的走廊」★ ⇒ ★让路闸对它无效 (已在 PCB_YIELD_VICTIMS 名单里, 仍不通)★ | **能** | ★不是让路闸 ⇒ 是【占它走廊的人】⇒ 需 PCB_PRIORITY_NETS 提前布 / 走廊重规划★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=0 · seg=[无铜] · vias=0 · pad_total=6 | ★官方板 151 段 / p41 151 段 ⇒ 候选板把它**整条丢了** (退铜名单) |
| `ID_DETECT_1` | **B4** | ★6 段 (全 F.Cu) · 抢路者 = ID_DETECT_0 (k=1) ★⇒ ★真靶子 (★k≤3 且抢路者非 GND★) ⇒ ★窄版让路闸对 BOOT_N 已验证成功 ⇒ ★同一抢路者可复用同一条约束★ | **能** | ★PCB_YIELD_VICTIMS 加 ID_DETECT_1 (★让 BOOT_N 已成功的同一条约束复用★) | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=6 · seg=[F.Cu 6] · vias=0 · pad_total=9 | 官方板 20 段 / p41 20 段 ⇒ 候选板只剩 6 段 (拆碎) |
| `I2C_A_SCL` | **B4** | ★4 段 (F.Cu 3 / In2.Cu 1) · 4 焊盘 · ★连过 2 次都没成 ⇒ ★属于【让路闸名单里但仍不通】的一类★ | **能** | ★PCB_YIELD_VICTIMS 加 I2C_A_SCL / I2C_B_SCL / I2C_B_SDA (★成组试, 别单条试★) | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=4 · seg=[F.Cu 3 / In2.Cu 1] · vias=2 · pad_total=12 | 官方板 56 段 / p41 56 段 ⇒ 候选板只剩 4 段 (拆碎) |
| `I2C_B_SCL` | **B4** | ★3 段 (全 F.Cu) · 5 焊盘 · ★v76ms chain.log 明列「A* 找不到路 I2C_A_SCL」★ ⇒ ★与 I2C_A_SCL 同因 ⇒ 成组处理★ | **能** | ★PCB_YIELD_VICTIMS 成组加 + PCB_PRIORITY_NETS 提到电源之前 (★I2C_A_SCL 已在优先网名单里, 仍不通★) | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=3 · seg=[F.Cu 3] · vias=0 · pad_total=15 | 官方板 3 段 / p41 3 段 ⇒ 候选板只剩 3 段 (拆碎) |
| `I2C_B_SDA` | **B4** | ★26 段 (F.Cu 18 / In2.Cu 5 / In4.Cu 3) · 5 焊盘 · ★v76ms chain.log「A* 找不到路 I2C_B_SDA」★ | **能** | ★成组让路 (I2C_A_SCL / I2C_B_SCL / I2C_B_SDA 三条一起) ★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=26 · seg=[F.Cu 18 / In2.Cu 5 / In4.Cu 3] · vias=3 · pad_total=15 | 官方板 248 段 / p41 248 段 ⇒ 候选板只剩 26 段 (拆碎) |
| `LED_B` | **B4** | ★27 段 (F.Cu 7 / In2.Cu 20) · 3 焊盘 · ★v76ms chain.log「A* 找不到路 LED_B」★ · ★抢路者 = LED_G / LED_B_D (★普通信号网★) ⇒ 属让路闸那一类★ | **能** | ★PCB_YIELD_VICTIMS 加 LED_B + 走廊重规划 (★LED_B_D 的 93.49 mm 长线是走廊占用方★) | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=27 · seg=[F.Cu 7 / In2.Cu 20] · vias=2 · pad_total=9 | 官方板 167 段 / p41 167 段 ⇒ 候选板只剩 27 段 (拆碎) |
| `KEY_VOL_P` | **B4** | ★10 段 (F.Cu 8 / In4.Cu 2) · 5 焊盘 · ★v76ms chain.log「_emit_path 放弃(净距/板边/过孔) KEY_VOL_P」★ ⇒ ★落铜前就被闸拦下 ⇒ ★属【落铜前拦】类 (★不是产物上擦★)★ | **能** | ★落铜前拦: PCB_ESC_CLR_FIX 已开仍被拦 ⇒ 需【局部位移/缩形】或挪下拉孔★ | `iss308_cand_layers.json` → `seg`/`seg_total`/`vias`: seg_total=10 · seg=[F.Cu 8 / In4.Cu 2] · vias=2 · pad_total=15 | 官方板 95 段 / p41 95 段 ⇒ 候选板只剩 10 段 (拆碎) |
<!-- ISS308_BUCKET_TABLE_END -->

★**★表里那 22 条的桶归属【不是】本单重新推算出来的 —— 是逐字抄上一趟 (`agent:hw-lead:subagent:56d88b87`) 已经算好并写进 `state/_iss308_s8_reachability_check.py` 的 `BUCKETS` 的** ★
★**本单只做 3 件事**: ① **核** (逐条把根因里的段数/层占比与盘上证据文件对拍 —— ★22 条根因里的每一个「N 段数」与 `iss308_cand_layers.json` 的 `seg_total` 逐条比对, **22/22 零不符**★) ② **补** (每条补上「实测出处 = 命令 + 文件 + 字段」与官方板对照) ③ **锁** (给桶归属加一份独立权威源, 见 §2-A-3) ★

### §2-A-3 · ★★桶归属的独立权威源 (★本单对「判据是摆设」这一缺陷的修法★) ★★

★**上一趟的 `check()` 只校验「桶 ∈ {B1..B5}」+「字段非空」+「网名集合 == 靶表」+「板 md5/mtime 未变」⇒ ⇒ 它【从不校验某条网名应该落在哪个桶】⇒ ⇒ 把 `CSI_D0_D2_N` 的桶从 B3 改成 B5 (★B5 也是合法桶★) ⇒ 脚本【判绿】⇒ ⇒ 脚本是摆设** ★

★**本单的修法 (三重锁, 改任一处必红)** ★

| 锁 | 机制 | 谁动了会红 |
|---|---|---|
| ★**锁 1** ★ | 脚本内新增 ★`BUCKET_AUTHORITY`★ 独立副本 (★22 网名 → 桶的第二份字面量, 不是从 `BUCKETS` 派生的★) ⇒ `check()` 逐条比对 | 改 `BUCKETS` 里任一条的桶 ⇒ ★红** ★ |
| ★**锁 2** ★ | `check()` **实读**本判决书 `HW/PCB/S8_REACHABILITY_VERDICT.md` 的 §2-A-2 落桶表 (★`<!-- ISS308_BUCKET_TABLE_BEGIN/END -->` 之间的行★) ⇒ 三方 (脚本 / 判决书 / 权威副本) 必须逐条一致 | 改判决书表格里任一条的桶 ⇒ ★红** ★ |
| ★**锁 3** ★ | `--selftest` 用例① 保持 ★「B3 → B5 这种【另一个合法桶】」★ 的形状 (★不许拿「桶名拼写非法」当反向用例★) ⇒ 必须判红 | — |

★**不许放宽任何现有判据** (`VALID_BUCKETS` / 字段非空 / 网名集合比对 / 板 md5+mtime 四条一个都没动) ★

### §2-A-4 · ★★口径重大注记: 这 22 条是【候选臂口径】, 不是【官方板口径】★★

★**这是本单最重要的一条口径注记, 也是 §2-B 的关键前提** ★

| 实测 | 数字 |
|---|---|
| ★**现役官方板 (`611b869e…`) 的 unconnected** ★ | ★**45 条 / 43 网名** (★`logs/iss308/evidence/iss308_live.drc.json` 实测★) |
| ★**候选板 `candidate_v76mx1L_pour` 的 unconnected** ★ | ★**26 条 / 22 网名** ⇒ ★**这 22 条就是这 22 网名** ★ |
| ★**两个集合的交集** ★ | ★**只有 12 条** (★`CSI_D0_D0_N` · `CSI_D0_D0_N_SRC` · `CSI_D0_D2_N` · `CSI_D0_D3_N` · `DSI_D0_D0_N` · `DSI_D0_D0_P` · `DSI_D0_D1_N` · `DSI_D0_D1_N_SRC` · `I2C_A_SCL` · `I2C_B_SCL` · `I2C_B_SDA` · `ID_DETECT_1`★) |
| ★**22 条里【官方板上是连通的】(★候选臂自己弄丢的★) ★ | ★**10 条** (★`CARRIER_BOARD_EN` · `CSI_D0_CK_N` · `CSI_MCLK` · `DSI_D0_CK_N_SRC` · `DSI_D0_D3_N` · `KEY_VOL_M` · `KEY_VOL_P` · `LED_B` · `SPI_CSn_BOOT` · `USB_CC1`★) ⇒ ★**这 10 条官方板有铜且连通 (官方板 unc 43 网名单里没有它们) ⇒ 它们【不是墙】, 是候选臂的退铜/拆碎** ★ |
| ★**候选臂自己被官方对照闸判死的证据 (★盘上已有, 不是本单新判★)** ★ | ★`state/CURRENT_TASK_ARCHIVE_2026-11-11.md` L4 逐字: ★「`candidate_v76mx1L` 已作废 (★官方对照闸 rc=1 REJECT: 退铜 4 网 (CARRIER_BOARD_EN/DSI_D0_CK_N_SRC/SPI_CSn_BOOT/USB_CC1) + 差分死腿 1 对 (DSI_D0_CK_P_SRC/N_SRC) + 逐网孤岛变多 11 网 ⇒ 它 unc 少 (22 vs 43) 是拿差分腿死掉 + 退铜 + 拆碎换来的」★ ⇒ ★**本单实测的「22 里官方板有铜但候选板零铜」4 条 = `CARRIER_BOARD_EN`/`DSI_D0_CK_N_SRC`/`SPI_CSn_BOOT`/`USB_CC1` ⇒ 与闸的退铜名单【逐字相同】★ |

★★**⇒ 判决: §2-A 的 22 条落桶表【在候选臂口径内成立】(★它是「这条网在这条臂的走法下为什么不通」的解释★), 但它【不等于】S8 (45→0) 的真实靶集 —— S8 的真实靶集是官方板那 43 个网名, 其中只有 12 条落在这张表里; 另外 10 条是候选臂自伤、31 条是官方板自己也没布通的高位腿** ★★

★**这直接决定 §2-B 的 N**: ★**「45 条归零」这个目标本身要先问老板「归零还是分级放行」(★= P7 的 C4★), 因为候选臂那 22 条**【证明不了】**官方板 43 条能不能归零 —— 它自己还欠着 4 条退铜 + 1 对死腿 + 11 网孤岛** ★

---

## §2-B · ★【判决 2】老板还差 N 个字母★

### §2-B-1 · 结论

★★**N = 2** ★★ —— ★**但这个 N 只数【S8 这一步】; 连同 ISS-306 (sw-lead) 已 verified 的 4 个【S4 / G1a 侧】字母, 板那一趟开工前老板一共还差 6 个** ★★

★**口径 (照 ISS-306 已 verified 的那个口径写)** ★

| 项 | 本单 |
|---|---|
| ★**计数范围** ★ | ★**只数卡「板那一趟 S8 (unconnected 45 → 0)」的字母** ★ ⇒ ★**不重复计 ISS-306 已计的 4 个** (★`W-2` / `W-1b`+`W-1c` / `A4 老表` / `A5 老表` — 那些卡 S4 与 G1a-8, 不是 S8★) |
| ★**每条给三样** ★ | ★**① 卡在哪一步 (S4/S5/S8) ② 对应哪条残余网名 ③ 不拍的后果 (一句话, 具体)** ★ |
| ★**不拍板** ★ | ★**只给 N + 卡点 + 后果, 不给决策码; 建议默认值一律不写** ★ |

### §2-B-2 · N = 2 逐条

| # | 字母 (need key) | 卡在哪一步 | 对应哪条残余网名 | 不拍的后果 (一句话) | 盘上状态 (实测) |
|---|---|---|---|---|---|
| ★**1** ★ | ★**P7 · 作业包 §7 的四个选项 (C1 板加宽 / C2 层数 / C3 SoM 下移 / C4 不归零·分级放行)** ★ (★决策页 `DECISION_PENDING_2026-11-16.md` L1206 第 ⑦ 条 · 逐字「★**作业包 §7 的 P7 (板框/层数/放行 C1~C4) ⇒ ★**S8 的正面战场** ⇒ ★**45 条 unconnected 能不能归零**」★) | ★**S8** ★ | ★**全部 22 条 (B1 桶那 2 条 `CARRIER_BOARD_EN` / `SPI_CSn_BOOT` 的根因直接写着「板面/器件轴未定 ⇒ 改板框才解」)** ★ | ★**不拍 ⇒ 45 条 unconnected 归不了零 ⇒ G1 开不了 ⇒ 投不了板** (★作业包 §6.2 逐字★); ★**且 C1/C2/C3 三个选项都要改板 ⇒ 若在 S10 之后才拍 ⇒ 板 md5 第二次变 ⇒ 「板只改一次」当场破功 ⇒ Gerbers/投产包/留证链/盖章/发布全作废重做** (★作业包 §6.2 订正行逐字★) | ★**仍 OPEN, 且 pm.yaml 里【没有】对应的 need key (★决策页第 ⑦ 条 × 5 处快照都在列, 但 `state/fragments/pm.yaml` 的 56 条 `needs_from` 里没有它★) ⇒ ★**这是登记缺口, 本单只登记不代开** ★ |
| ★**2** ★ | ★**D_LED_G 外露 / 物理位置** ★ (★need key `boss_dled_g_expose_decision_20261117` · 决策页 L1206 第 ③ 条逐字「★**S8 (布线归零) ⇒ `LED_G_D` 走线 93.49 mm ⇒ 要么挪 LED·要么改网表**」★) | ★**S8** (兼 S6 落位轴) ★ | ★**`LED_B`** (★B4 桶; 它的走廊占用方是 `LED_G_D` ★实测 candidate 板 `LED_G_D` = ★**98.929 mm / 23 段**★ ⇒ 横跨 x 8..76 的 SoM 主体区★) | ★**不拍 ⇒ 板面落位不能定 ⇒ 要么挪 LED (板面动) 要么改网表 (★越出「板那一趟零改网表」边界★) ⇒ `LED_G_D` 那条近 99 mm 长线继续占着中部走廊 ⇒ `LED_B` / `LED_B_D` 一族布不通** ★ | ★**OPEN** (★`state/fragments/pm.yaml`: `waiting_on: boss` · `due: 2026-11-18` · ★**无 `decision` 字段★ ⇒ 老板还没回) ★ |

### §2-B-3 · ★明确【不计入】N 的项 (★避免与 ISS-306 重复计数 / 避免把已拍的当还欠的★)

| 项 | 盘上实测状态 | 处理 |
|---|---|---|
| ★**A1** (★`BAT_DET` 终点★) | ★**已拍** ★: `state/fragments/pm.yaml` 的 `boss_a1_v3_batdet_divider_20261117` ⇒ ★`decision: A1 = V-3 = E` · `decided_at: 2026-11-17 09:49` · ★已落表 (2026-11-17 09:58:16 · rc=0)★ ⇒ ★**作业包 §6.2 里「S8 卡 A1」那一行【已过期】** ★ | ★**不计入 N** ★ |
| ★**W-4** (★`Q_PG.3` 极性★) | ★**已拍** ★: `boss_w4_q_pg_topology_20261117` ⇒ ★`decision: 写法 A (S=BAT_SW / D=ON / G=PG)` · `decided_at: 2026-11-17 09:49`★ | ★**不计入 N** ★ |
| ★**W-2 / W-1b / W-1c** (★ESD 型号轴 + D− 侧补不补★) | ★**仍 OPEN** (★`boss_esd_model_axis_pending_20261117` 无 `decision`★) ⇒ ★**但它卡的是 S4 (板那一趟的 A 类步), 不是 S8** ★ | ★**不计入本单 N** ★ ⇒ ★**已由 ISS-306 (sw-lead, verified) 计入它自己的 N=4, 本单不重复计** ★ |
| ★**A4 老表 / A5 老表** (★关机语义 + `TPS22991RAA` 追认★) | ★**仍 OPEN** (★`boss_shutdown_semantics_and_loadswitch_20261117` 无 `decision`★) ⇒ ★**卡 G1a-8 (原理图定稿闸), 不是 S8** ★ | ★**不计入本单 N** ★ ⇒ ★**已由 ISS-306 计入** ★ |
| ★**`FSIN_OUT` 3.01 mm** (★作业包 §6.2 登记成「S8 卡 hw + 路由器作者」★) | ★**根因已被 ISS-282 订正 = 【布线排队顺序】⇒ 归 `PCB_PRIORITY_NETS` 把 `FSIN_OUT` 提到电源之前布 (已有实测支撑: L=3.0mm 就是那条直线) ⇒ 【不需要动板】** ★ (★`HW/PCB/FSIN_OUT_ROOTCAUSE.md` §8 逐字★) | ★**不计入 N** ★ ⇒ ★**归 §2-C 技术活 T2** ★ |
| ★**`board_p41_promote`** (★换不换官方板血脉基线★) | ★**仍 OPEN** (★决策页 L1206 第 ⑤ 条, main 建议 (a) 不换★) ⇒ ★**但它卡的是【基线重锚】, 不是 S8 归零本身** ★ | ★**不计入 N** ★ ⇒ ★**登记在 §2-C-5 (★换基线会改 S8 的靶集口径, 必须先定★)** ★ |

### §2-B-4 · ★板那一趟开工前的【总数】 (★与 ISS-306 合并去重★)

| 来源 | 字母 | 卡在哪一步 |
|---|---|---|
| ★**本单 (ISS-308)** ★ | ★**P7 (§7 四选项)** ★ | ★**S8** ★ |
| ★**本单 (ISS-308)** ★ | ★**D_LED_G 外露/位置** ★ | ★**S8** ★ |
| ★**ISS-306 (sw-lead, verified)** ★ | `W-2` (D− 侧补不补 ESD) | ★**S4** ★ |
| ★**ISS-306 (sw-lead, verified)** ★ | `W-1b` + `W-1c` (D+ 那颗真 OPN) | ★**S4** ★ |
| ★**ISS-306 (sw-lead, verified)** ★ | `A4 老表` (关机语义) | ★**G1a-8** ★ |
| ★**ISS-306 (sw-lead, verified)** ★ | `A5 老表` (追认 `TPS22991RAA`) | ★**G1a-8** ★ |
| ★**合计** ★ | ★**6 个字母 (★无重叠★)** ★ | ★**S8 侧 2 个 + S4/G1a 侧 4 个** ★ |

★**★两条必须同批拍的时间铁律 (★否则板 md5 变两次★)**: ★**P7 的 C1/C2/C3 三个选项都改板 ⇒ P7 必须在那一趟【之前】拍; `D_LED_G` 位置也改板面落位 ⇒ 同样必须【之前】拍; 而 ISS-306 那 4 个 (W-2 / W-1b / W-1c / A4 / A5 老表) 也改板或改网表真源 ⇒ 【同批】★ ⇒ ★**这一批 6 个字母是【板只改一次】的单点阀门, 晚一个 ⇒ 板改第二次** ★

---

## §2-C · ★【判决 3】现在就能做的技术活清单 (★零等老板★)

### §2-C-0 · 口径

★**本单口径**: 「现在就能做」= ★**① 零等老板 ② 不产生第二次板改 (★要么纯 env / 路由器源码侧, 要么必须与板那一趟同一次做完★)** ★
★**凡是需要改【网表真源】的 ⇒ 不许写进这里 ⇒ 归 §2-B** (★`boss_esd_model_axis_pending_20261117` / `boss_shutdown_semantics_and_loadswitch_20261117` 都属这一类★)

★**臂的实测机时 (★估代价用★)**: ★**单臂 ≈ 70 min + 链 ≈ 8 min** (★实测: `v76ms` 臂 `state/.lastgood/v76ms_reserve.txt` mtime 20:07:32 → 臂产物 `/tmp/v76ms_R.kicad_pcb` mtime 21:17:33 → 链产物 `/tmp/chain_v76ms/final_chain.kicad_pcb` mtime 21:25:42★) ⇒ ★**一次 DRC 复跑 ≈ 40 s** (★`state/check_pcb_drc.py` 实测★)

| # | 技术活 | env 键 (★逐字★) | 落铜前拦 / 落位增补的具体改法 | 预期能解掉哪几个残余网名 | 预估代价 (臂跑多久 / 改不改路由器源码 / 改不改板) |
|---|---|---|---|---|---|
| ★**T1** ★ | ★**窄版让路闸扩名单** ★ (★已验证机制: `BOOT_N` 靠它救回, 扰动面 97 → 1 处★) | ★`PCB_YIELD_STRAIGHT=1` + ★`PCB_YIELD_VICTIMS=<名单>` (★分号/逗号分隔, 空 ⇒ 全部生效 = 老行为★) | ★**只加受害网, 不动闸几何** ⇒ ★**每次只加 1 个网, 每加一个 = +1 处扰动 ⇒ 必须跑 `bash state/pcbnew_py.sh state/gate_live_check.py --arm-script <臂脚本>` 体检 (★须 rc=0 且【至少 1 处会被约束】★) ⇒ ★**「`BOOT_N` 已被 `ID_DETECT_0` 抢 ⇒ 同一抢路者可复用同一条约束」⇒ `ID_DETECT_1` 复用 `BOOT_N` 那条** ★ | ★**`ID_DETECT_1`** (★k=1, 抢路者 `ID_DETECT_0`★) ★· ★**`I2C_A_SCL` / `I2C_B_SCL` / `I2C_B_SDA` 成组** (★v76ms `chain.log` 明列三条「A* 找不到路」★) ★ | ★**改 env, 不改源码, 不改板** ★ · ★**代价 = 每个网一次臂 (≈78 min) ⇒ 4 个网 ≈ 5.2 h 机时** ★ · ★**注意: `CARRIER_BOARD_EN` / `USB_CC1` 让路闸【救不了】(★`UNC_TARGET_MAP.md` 已登记: 两条臂都失败 / REST 阶段才布⇒走廊早占完★) ⇒ 这两条不列在 T1★ |
| ★**T2** ★ | ★**优先网重排** ★ (★`FSIN_OUT` 根因已被 ISS-282 订正 = 布线排队顺序★) | ★`PCB_PRIORITY_NETS=FSIN_OUT;…` (★分号分隔, 默认空★) | ★**把 `FSIN_OUT` 提到电源之前布** ★ (★已有实测支撑: L=3.0mm 就是 A→B 那条直线, 候选臂 env 里 `FSIN_OUT` 已排第一★) ⇒ ★**同时把 `LED_B` / `USB_CC1` / `I2C_B_SCL` / `I2C_B_SDA` 提到同批** ★ | ★**`FSIN_OUT`** (★候选臂已通, 官方板仍断 ⇒ 官方板血脉增量路线要用它★) ★· ★**`LED_B` / `I2C_B_SCL` / `I2C_B_SDA`** (★优先网只能改变【谁先挑走廊】, 不能凭空多出走廊 ⇒ 配合 T1/T3 才有效★) | ★**改 env, 不改源码, 不改板** ★ · ★**代价 = 一次臂 (≈78 min)** ★ |
| ★**T3** ★ | ★**差分对层选择 (★上 §1-④ 已查清机制面★)** ★ | ★`PCB_PAIR_LAYERSEL=1` (★默认 0 ⇒ 逐位不变★) | ★**开在【候选臂 recipe】上做一次单变量臂** ⇒ ★**只对 3 对有药效** (★`CSI_D0_D0_N` / `DSI_D0_D3_N` / `KEY_VOL_M` — N/P 层占比相反★) ⇒ ★**对 5 条零铜 N 腿无药效** (★起步格被封, 不是层分配病★) ⇒ ★**必须同时盯 `LED_B` (v76ms 臂上 27 段 → 0 段) ⇒ 这条网要单独看** ★ | ★**最多 3 对的层分配症状** (★`CSI_D0_D0_N` · `DSI_D0_D3_N` · `KEY_VOL_M`★) ⇒ ★**修不了零铜那 5 条** ★ | ★**改 env, 不改源码, 不改板** ★ · ★**代价 = 一次臂 (≈78 min) ⇒ 收益预期【小】, 建议只作为【确认 §1-④ 判决】的那一枪, 不作为主力** ★ |
| ★**T4** ★ | ★**成对走廊规划 + 起步格 halo 放宽** ★ (★B3 桶 12 条的主力机制★) | ★`PCB_ROUTE_RESERVE=NET_A+NET_B:li0,x0,y0,x1,y1;…` (★格式: 网名:层号,x0,y0,x1,y1 (mm, 层号 0/2/4…), 多组用 `;`★) + ★`PCB_HALO_MARGIN` (★默认 0.20, 候选臂用 0.0625★) + ★`PCB_PAIR_ESCAPE_EXEMPT=1` + ★`PCB_SKIP_PAD_CELLS=1` + ★`PCB_PAIR_EXEMPT_R` | ★**① 成对预留框必须【成对】**: 候选臂 env 里已有 19 组成对框 (★如 `CSI_D0_D0_N_SRC+CSI_D0_D0_P_SRC` / `DSI_D0_CK_N_SRC+DSI_D0_CK_P_SRC`★) ⇒ ★**要补的是 5 条零铜 N 腿【自己的那一格】, 不是再加框** ★ → ★**用 `state/plan_route_reserve.py` 按实测铜占位重算框 (★全几何, 不猜★)★** → ★**② 起步格 halo 放宽**: ★`PCB_HALO_MARGIN` 只能小步降 (★MEMORY 已实测 `HALO_MARGIN=0` ⇒ 11 条 clearance 违规 ⇒ 不可行★) ⇒ ★**只能改「起步格豁免」的判据 (★`_free()` 里 `PAIR_ESCAPE_EXEMPT` 分支, 源码 L1128-1146★) ⇒ 【own pad cell 起步】的豁免半径** ★ | ★**`CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N` / `DSI_D0_CK_N_SRC` / `DSI_D0_D1_N_SRC`** (★5 条零铜 N 腿★) ★· ★**`CSI_D0_CK_N` / `DSI_D0_D0_N` / `DSI_D0_D1_N` / `DSI_D0_D1_P`** (★N 腿有铜但被压死★) | ★**要改路由器源码** (★`_free()` 的 halo/起步格豁免判据, 源码 L1082-1146★) ★· ★**不改板** ★ · ★**代价 = 源码改 1 处 + 一次臂 (≈78 min) + 一次 DRC (≈40 s) + 一次名单制闸自测** ★ |
| ★**T5** ★ | ★**GND 卡死的落铜前拦 (★B2 桶 `CSI_MCLK`★)** ★ | ★**无 env 键可用** ★ ⇒ ★**`PCB_KEEPOUT` 挡不了走线 (★源码 L731-737 逐字: 「那是【排版期禁放框】⇒ 挡不了走线」★) ⇒ ★**GND 铜皮局部 keepout 必须在 zone fill 之前做** (★`_fill_zones()` 源码 L4617 / L5102-5107★) | ★**三选一 (★风险从低到高★)**: ① ★**GND 铜皮局部 keepout / 缩形** (★只动面, 不动走线 ⇒ 风险最低★) ② ★**挪 GND 下拉孔** (★只动孔 ⇒ 需重跑 GND 下拉 ⇒ 可能引入孤岛★) ③ ★**换层** (★需 pair-aware ⇒ 成本最高★) ⇒ ★**★铁律: 必须在【落铜前】拦/改 ⇒ 不许在产物上擦★** ★ | ★**`CSI_MCLK`** (★B2 桶唯一一条; 候选板 10 段, 官方板 194 段 ⇒ 官方板是通的 ⇒ ★**这条也是候选臂自伤, 不是墙**★) | ★**要改路由器源码 (★zone fill 前插 keepout★) 或改板面铜皮** ★· ★**改铜皮 = 板那一次改 (★板 md5 变一次★), 不额外等老板** ★· ★**代价 = 源码 1 处 + 一次臂 + DRC** ★ |
| ★**T6** ★ | ★**`KEY_VOL_P` 的落铜前拦** ★ | ★**`PCB_ESC_CLR_FIX=1`** (★默认 0★) + ★**`_emit_path` 的净距闸** (★源码内, 非 env★) | ★**实测**: v76ms 臂 `chain.log` L43/L85 逐字「未成: ★**`_emit_path` 放弃(净距/板边/过孔) KEY_VOL_P`★」⇒ ★**落铜前就被闸拦下 (不是产物上擦) ⇒ `PCB_ESC_CLR_FIX=1` 开了仍被拦 ⇒ 要么改 `_emit_path` 的真实几何模型 (★净距/板边/过孔 三项逐项放行, 源码 `_emit_path`★), 要么把 `SW_KEY_VP` / `C_KEY_VP` 落位挪开 (★= 落位增补, 属板那一次★)** ★ | ★**`KEY_VOL_P`** (★候选板 10 段 / 官方板 95 段 ⇒ 候选臂自伤★) | ★**改 env 或改源码** ★· ★**落位挪开 = 板那一次改** ★ · ★**代价 = 一次臂 + DRC** ★ |
| ★**T7** ★ | ★**官方板血脉增量路线 (★p41 配方已在盘上★)** ★ | ★`PCB_HALO_MARGIN=0.015625` (★`state/clrfix_iter.sh` / `state/patch_astar_nostub.py` 内部★) | ★**按 `state/.lastgood/CANDIDATE_official_p41_ready.md` 的两步配方重跑**: ① `PCB_HALO_MARGIN=0.015625 bash state/pcbnew_py.sh state/patch_astar_nostub.py <官方板> <官方板>.drc.json --out … --grid 0.125` ② `bash state/clrfix_iter.sh … --max 6 --tag offpatch` ⇒ ★**官方板 18092 段一寸不动, 只加铜** ★ | ★**4 个签名 (`JTAG_TDI` / `LIGHT_5V` / `PWR_GOOD` / `SPI_MOSI_BOOT`) 已在 p41 上救回** ★· ★**但 p41 的 unc 顶在 41 条 / 39 网 (★四档 margin 实测逐位相同, 第二轮增量补 0 条 ⇒ 收益饱和★) ⇒ ★**【再跑一遍还是 41】, 归零靠它不行** ★ | ★**改 env, 不改源码, 不改板** ★ · ★**代价 = 一次增量 + 一次 DRC (≈40 s) + 一次名单制闸** ★ |

### §2-C-1 · ★技术活与桶的对应 (★哪几条靠哪一枪★)

| 桶 | 网名 | 主枪 | 备枪 | 能不能在板那一趟解 |
|---|---|---|---|---|
| ★**B1** ★ (2 条) | `CARRIER_BOARD_EN` · `SPI_CSn_BOOT` | ★**P7 (老板字母)** ★ | ★T7 (官方板血脉: 官方板这 2 条都有铜 ⇒ 用增量保住) ★ | ★**能 (★但 P7 不拍就定不下来★)** ★ |
| ★**B2** ★ (1 条) | `CSI_MCLK` | ★**T5** ★ | —— | ★**能** ★ |
| ★**B3** ★ (12 条) | `CSI_D0_CK_N` · `CSI_D0_D0_N` · `CSI_D0_D0_N_SRC` · `CSI_D0_D2_N` · `CSI_D0_D3_N` · `DSI_D0_CK_N_SRC` · `DSI_D0_D0_N` · `DSI_D0_D0_P` · `DSI_D0_D1_N` · `DSI_D0_D1_N_SRC` · `DSI_D0_D3_N` · `KEY_VOL_M` | ★**T4** ★ | ★**T3 (★只对 3 对有药效★)** ★ | ★**能 (★代价 = 改路由器源码 1 处 + 一次臂★)** ★ |
| ★**B4** ★ (7 条) | `USB_CC1` · `ID_DETECT_1` · `I2C_A_SCL` · `I2C_B_SCL` · `I2C_B_SDA` · `LED_B` · `KEY_VOL_P` | ★**T1** ★ | ★**T2 (排队顺序)** ★ · ★T6 (`KEY_VOL_P`) | ★**能** ★ |
| ★**B5** ★ (0 条) | —— | —— | —— | —— |

### §2-C-2 · ★★T1~T7 全部【零等老板】, 但 T4/T5/T6 的源码改动会【重跑整条臂链】★★

★**顺序建议 (★零等老板也能先跑★)**: ★**T7 (一次, 官方板血脉增量, 把基线读数刷新到 p41 的 41 条/39 网) → T1 (逐个网扩让路闸名单, 每次一臂) → T2 (排队顺序, 一次臂) → T3 (一次臂, 只为确认 §1-④ 判决) → T4 (★改源码 + 一次臂, 主力★) → T5 / T6 (★改源码 + 一次臂★)** ★
★**T7 必须先跑** ★ ⇒ ★**因为 §2-A-4 实测: 候选臂那 22 条里有 10 条官方板是连通的 ⇒ 换回官方板血脉 ⇒ 靶集口径当场变 (43 网名 → 39 网名) ⇒ 不先刷基线, 后面的臂都在错的靶集上打分** ★

---

## §2-D · ★★【S6 落位增补表草案】★★ (★任务书 §0 点名的第三件交付物★)

### §2-D-1 · 一句话

★**S6 落位增补 = 【把 10 个 `R_SEL_*` + 10 个 `TP_DSI_*` 显式钉回官方锚点 (20 个 distinct ref) + 把 `R_SEL_D3_P` 从 lane 倒挂位 (78.90, 9.50) 换到 (122.30, 5.50)】 ⇒ ★**lane 交叉 8 → 0** ★ ⇒ ★**零新增设计 (全是官方板已实测坐标) · 封装/板框/网表一律不动** ★ ⇒ ★**★它【不是老板字母】: `HW/PCB/LAYOUT_FIX_SPEC.md` §3 方案 A 逐字「谁拍: ★**总工 (main) 就能拍** ★ (纯布局, 不碰网表/板框/封装)」⇒ ⇒ 归【现在就能做】, 不进 §2-B 的 N★** ★

### §2-D-2 · ★权威源 (★机器可读 · 已有的, 不用新造★)

★**权威块 = `HW/PCB/BOARD_FRAME_CALIBER.md` §6 的 `cal:S6_TARGETS` (★L181-L211★) ⇒ ★**这是 S6 目标位的唯一真源, 本单不新造一份★** ★

```json cal:S6_TARGETS   ← ★逐字摘自 HW/PCB/BOARD_FRAME_CALIBER.md (★不抄错★)
{
  "frame": "B160x100",
  "note": "S6 目标位 = 20 个 distinct ref (作业包 §3-S6 / LAYOUT_FIX_SPEC §3 方案 A 的 PCB_PART_POS 串)",
  "allow_board_diff": ["R_SEL_D3_P"],
  "legacy_positions": { "R_SEL_D3_P": [78.9, 9.5] },
  "targets": [ ★…20 行, 见源文件★ ]
}
```

★**机器闸** = `python3 HW/check_board_frame_caliber.py` (★C1 漏标帧即红 / C2 坐标漂移即红★) ⇒ ★**本单建议: 那一趟开工前先跑它, 确认板面现状与 `cal:S6_TARGETS` 的差集 = 只有 `R_SEL_D3_P` 一处** ★

### §2-D-3 · ★落铜前拦 / 落位增补的具体改法 (★`PCB_PART_POS` 串 · 逐字照抄★)

★**★这一串就是那一趟 S6 要写进 env 的全部内容 (★帧 = `B160x100` · mm★)★**

```bash
PCB_PART_POS="R_SEL_D0_N:78.90,5.50;R_SEL_D0_P:83.70,5.50;R_SEL_D1_N:88.50,5.50;R_SEL_D1_P:93.30,5.50;R_SEL_CK_N:98.10,5.50;R_SEL_CK_P:102.90,5.50;R_SEL_D2_P:112.50,5.50;R_SEL_D2_N:107.70,5.50;R_SEL_D3_N:117.30,5.50;R_SEL_D3_P:122.30,5.50;TP_DSI_D0_N:75.70,5.50;TP_DSI_D0_P:87.50,79.70;TP_DSI_D1_N:91.90,79.70;TP_DSI_D1_P:96.30,79.70;TP_DSI_CK_N:78.70,79.70;TP_DSI_CK_P:83.10,79.70;TP_DSI_D2_N:100.70,79.70;TP_DSI_D2_P:105.10,79.70;TP_DSI_D3_N:120.50,5.50;TP_DSI_D3_P:75.70,9.50"
```
★**★注意: 上面本单的抄写顺序把 `R_SEL_D2_P` 排在了 `R_SEL_D2_N` 前面 (★抄串时自己按字母序排了·**网名顺序不影响路由器行为**, 因为 `PCB_PART_POS` 是【键值对】解析★) ⇒ ★**权威顺序以 `HW/PCB/LAYOUT_FIX_SPEC.md` L172 / `cal:S6_TARGETS` 为准, 本单这行只当【坐标值】的抄本★** ★

### §2-D-4 · ★★返工量口径 (★ISS-274 订正: 「21 个」是重复计数, 实测 distinct = 20★)★★

| 项 | 数 | 说明 |
|---|---|---|
| ★**要显式钉的器件** ★ | ★**20** ★ | ★**10×`R_SEL_*` + 10×`TP_DSI_*` ⇒ distinct = 20 (原文「21 个」是重复计数: `R_SEL_D3_P` 本来就在那 10 个里)★** |
| ★**真实位移** ★ | ★**1** ★ | ★**`R_SEL_D3_P`: (78.90, 9.50) → (122.30, 5.50) (★lane 倒挂源★) ⇒ 实测 Δx = +43.40, Δy = −4.00 (★原页写的是到 `J_SOM_P3.83` 的线变长 Δx +60.50 → +103.90, 那是连线长度不是位移★)★** |
| ★**固化钉位 (防再挪)** ★ | ★**19** ★ | ★**其余 19 个现值已等于目标位 ⇒ 实钉是为了【防生成器/布线臂再把它们挪回左上】, 不是位移** ★ |
| ★**那一趟的返工量** ★ | ★**1 个真实位移 + 19 个固化钉位** ★ | ★**按 21 个算就会把返工预估算错 (★LAYOUT_FIX_SPEC §3 订正② 逐字★)★** |

### §2-D-5 · ★校验 (★方案 A 自带的四项, 逐字★)

| 校验项 | 结果 |
|---|---|
| lane 交叉数 | ★**0** ★ (★官方现状 8 → 臂现状 45 → **0**★) ★ |
| `R_SEL_*` 与 SoM 承载区 (x 8..76) | ★**零重叠** (★x 最小 75.70★) ★ |
| `R_SEL_D3_P` 新位 (122.30, 5.50) 占位 | ★**空** (★该区只有 `R_SEL_D2_P`@112.5 / `R_SEL_D3_N`@117.3 / `TP_DSI_D3_N`@120.5 / `SW_BOOT`@116.4,y=10.5★) ★ |
| `TP_DSI_*` 板底排 (y = 79.70) 与 SoM 区 | ★**零重叠** (★y 79.70 > 56★) ★ |

### §2-D-6 · ★它解掉 §2-A 那 22 条里的哪几条 (★诚实的口径★)

★**直接解掉 = 0 条** (★本单实测: 22 条里落在 `R_SEL_*` / `TP_DSI_*` 承载网上的【一条都没有】—— 那 22 条全是 SoM 腿与信号网, 不是 DSI lane 中途串阻★) ⇒ ★**它的作用是【几何前置】, 不是【直接解网名】** ★
- ★**为什么仍要做**: ★**ISS-265 §0 逐字: 臂布局把 10 条 DSI 差分腿的 lane 序【完全反向】(45 处交叉) ⇒ 官方板自己 8 处交叉 ⇒ ★**官方板那 13 条 DSI 腿一根都没布通, 有 8 处是 lane 倒挂造成的** ⇒ ⇒ 不修 lane, S8 归零连【起跑资格】都没有** ★
- ★**所以它在 §2-C 里的位置**: ★**T7 (刷基线, 因为靶集口径会当场变) 之后、所有 DSI/CSI 相关臂 (T1/T2/T3/T4) 之前** ★ ⇒ ★**它【零等老板】(main 就能拍) · 改的是 env 不是板 · 代价 = 一次臂 (≈78 min) + 一次板框坐标闸 (≈10 s)** ★
- ★**★一条必须说清的边界**: ★**它【不】解决 23 条跨 SoM 主体的 DSI/CSI 腿** ⇒ ★**那部分仍卡老板 `P7` 的 C1/C2/C3 (改板形/层数) 或 C4 (分级放行) ⇒ ⇒ ★**§2-D 做完 ≠ S8 能归零★** ★

### §2-D-7 · ★帧标纪律 (★ISS-271 的坑, 必须整段带帧标★)

★**★`D_LED_G` 首选窗口 (X 33.00..47.71 × Y 1.60..28.40) 与检修口/调试口开口 (X 47.00..60.00 × Y 1.665..11.730) 都是【★60×30 套A 帧★】(帧 id `F30A`) ⇒ ★**不可当 S6 坐标用★** ⇒ ★**照字面抄进 S6 = 那一趟开工即撞 SoM 座 (实测 `D_LED_G` 窗口压住 `J_SOM_P3` 的 10 个焊盘, 检修口开口压住 `J_SOM_P1` 的 56 个焊盘)★** ⇒ ⇒ ★**S6 增补表的每一行都必须带帧标 (`B160x100`), 帧标缺失 = 机器闸 `HW/check_board_frame_caliber.py` C1 判红★** ★

---

## §3 · 本判决书未做的事 (★如实交代★)

| 项 | 状态 |
|---|---|
| ★**22 条的桶归属** ★ | ★**逐字抄上一趟的 `BUCKETS`, 本单只核 + 补出处 + 加锁, 未重新推算** ★ |
| ★**§2-B 的 N** ★ | ★**N=2 (S8 侧)** ★ ⇒ ★**板那一趟开工前合计 6 个 (与 ISS-306 合并去重)** ★ |
| ★**§2-C 的 7 条技术活** ★ | ★**全部只列配方 + 代价, 本单【一枪没跑】(★任务书明令: 不许新跑布线臂★)** ★ ⇒ ★**代价里的机时是按 v76ms 臂实测 mtime 推的, 不是本单实测的臂** ★ |
| ★**官方板 43 网名的逐条归桶** ★ | ★**本单没做** ★ ⇒ ★**§2-A 的 22 条表 ≠ S8 的完整靶集 (★见 §2-A-4★) ⇒ 【官方板那 31 条本单没归桶】—— 归【下一单】或归【板那一趟开工前的清单核对】★ |
| ★**§1-④ 的「谁写的」** ★ | ★**查到了判定人与日期 (main / 2026-11-11 03:0x), 但原始读数盘上没留 ⇒ 【原始读数】这半边是 [0数据] (★要拿到它: 重跑 v76ms 臂 ≈78 min + 重跑 v76ml 对照臂 ≈78 min★)** ★ |

---

## §4 · 证据分级

| 等级 | 本单用在哪 |
|---|---|
| ★**`[实测]`** ★ | 22 条逐层铜量 (★`iss308_cand_layers.json`★) · 两臂终板 unc 读数 (★`iss308_v76ms_fresh.drc.json` + live 板 DRC★) · 官方板 / p41 逐网铜量 (★`iss308_official_census.json` / `iss308_p41_census.json`★) · env 逐键 diff (★`v76ml_arms.sh` vs `v76ms_arms.sh`★) · `LED_B` 两臂差异 (27 段 vs 0 段) · pm.yaml 的 need 状态 (★`decided_at` / `waiting_on` / 有无 `decision`★) · 源码行号 (★`gen_pcb_routing.py` L731-737 / L1082-1146 / L4423-4453 / L4617 / L5102-5107★) · 臂机时 (★mtime 实测★) |
| ★**`[推算]`** ★ | 11 对差分腿的 N/P 层占比对比与「只有 3 对相反」的统计 (★由 candidate 板逐段读层算出★) · 「B3 桶 12 条中零铜 5 条」的归类 (★由 `seg_total=0` + P 腿有铜推出★) · 「候选臂那 10 条是自伤」的判定 (★由官方板 unc 名单 + 官方板铜量推出★) |
| ★**`[官网]`** ★ | ★**本单未使用** ★ |
| ★**`[媒体]`** ★ | ★**本单未使用** ★ |
| ★**`[0数据]`** ★ | ① ★`PCB_PAIR_LAYERSEL` 单变量臂的【原始读数】(★盘上只有一句结论, 没留原始读数★) ⇒ 要拿到: 重跑 v76ms + v76ml 两条臂 (≈156 min 机时) ★② ★`LED_B` 在 v76ms 臂上从 27 段掉到 0 段的【机制级根因】(★已知是【开机制的那条臂】, 但【为什么它连安全阀都没兜住】盘上无分析 ⇒ 要拿到: 跑一次 diff_pair_audit / 读 v76ms 臂的 `LED_B` 起步格读数★) ★③ ★官方板那 43 个网名各自的死因归桶 (★本单没做, 不在 22 条范围内★) ★ |

---

## §5 · 边界自证 (★本判决书零副作用★)

| 边界 | 自证 |
|---|---|
| ★**零写板** ★ | ★本单只读盘 (★`state/pcbnew_py.sh` 跑的是只读探针: `iss308_layerprobe.py` / `probe_netlen2.py` / `probe_official_census.py` / `probe_led.py`★) ⇒ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17` 一字未动 (见交卷单 B4) ★ |
| ★**零落表** ★ | ★网表 / 脚表 / BOM / 台账 一个字节没动 (见交卷单 B4 的 4 个 md5) ★ |
| ★**零改闸 / 零改判据脚本** ★ | ★`state/compare_arm_official.py` · `state/check_pcb_drc.py` · `state/gate_check.py` · `HW/check_onepass_commit_order.py` · `HW/check_workpack_state_values.py` 一个字节没动 ⇒ **唯一例外 = `state/_iss308_s8_reachability_check.py`** (★本单第 3 件交付物, 本来就是本单自己建的脚手架★) ★ |
| ★**零改既有文档正文** ★ | ★作业包 / 清单页 / `state/UNC_TARGET_MAP.md` / 臂总账 / 决策页 一律不碰 ⇒ 本单只【新建】`HW/PCB/S8_REACHABILITY_VERDICT.md` + 交卷单, 只【改】自己那个脚手架脚本 ★ |
| ★**零外发** ★ | ★没发任何邮件 / 询价 / 问询 / 采购 ⇒ 本单全部证据来自本机盘上文件 ⇒ **不依赖任何外部回复** ★ |
| ★**不替老板拍板** ★ | ★§2-B 只给 N + 卡点 + 后果, **全文无「已决定 / 已拍 / 就选 X」** ⇒ 不给建议默认值 ★ |
| ★**不自签 issue_log** ★ | ★没写 `state/issue_log.yaml` ★ |
| ★**不新跑布线臂** ★ | ★本单【一枪没跑】 ⇒ 22 条的段数全部来自上一趟已落盘的证据文件 ★ |
| ★**不改别人分片** ★ | ★只写 `state/fragments/hw.yaml` (走 `state/frag_write.py --agent hw-lead`) ★ |

---

## ★附 · 给 main 的一行 ★

★★**S8 归零在技术上【不是不可达】(B2/B3/B4 共 20 条各有 env 配方 + 1 处源码改动的路径, 逐条都有实测出处), 但 §2-A-4 实测出这 22 条靶表是【已被官方对照闸判死的候选臂】的口径 ⇒ 靶集不真实 ⇒ 老板还差 2 个 S8 侧字母 (`P7` 的 §7 四选项 + `D_LED_G` 外露/位置), 连同 ISS-306 已 verified 的 4 个 S4/G1a 侧字母 = 板那一趟开工前共 6 个 ⇒ 而 §1-④ 已查清 `PCB_PAIR_LAYERSEL` 「无效但无害」是【只有一条单变量臂的读数】支撑的, 且实测支撑面比原句小 (对 `LED_B` 有害) ⇒ 建议主力改走【T4 成对走廊 + 起步格豁免】而不是【T3 开层选择】** ★★
