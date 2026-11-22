# ISS-339 · 任务书 (hw-lead) · 【可比性前置闸】+【S8 布线归零目标名单重读器】★零写板★

## 0. 抬头

你是**硬件总工 (hw-lead)**。本单 = ★**主线内 · PCB 线 · 纯分析 + 新建闸类 · 零写板**★。
★**板只改一次** ⇒ 那一趟还没开工 ⇒ ★**你这一单只出【两把尺子】, 一个字节都不许碰板**★

---

## 1. 为什么是这一单 (★依据全是 main 本机实读, 你不用重新论证★)

- ★**队列排空**: `python3 state/advance.py --json` ⇒ `internal: []` · `approvals: []` · `waiting: 0` (★40 条待老板拍板不归你★)
- ★**hw-lead 名额已释放**: ISS-337 已于 2026-11-22 21:16 被 main 签收 `verified`
- ★**板那一趟 (S8 = 布线归零 unc 45 → 0) 开工前缺两把尺子** ★ ⇒ main 已把两条 need **裁完** (机制地界), 缺的只是**实现**:

  ① **【可比性前置闸】** — main 2026-11-22 21:2x 已裁 need `iss337_band_truth_overrides_doc` 逐字:
  > 「名单制闸 `state/compare_arm_official.py` **不用改代码** ⇒ 只需在它前面加一道【可比性前置闸】, 判据 = 归一化段数 ∈ [2300,3200] · 铜长 ∈ [4600,5900] mm · 过孔 ∈ [380,520] ⇒ 越界即拦 ⇒ ★**不许拿不可比的板刷闸的结论**★」

  ② **【S8 目标名单重读器】** — main 同日已裁 need `iss337_rereread_zerocopper_denominator` 逐字:
  > 「重读办法 = ① 用那一趟的真实基线板跑 unconnected 清单 ⇒ 得分母 N' (★**不是 45**★) ② 逐条标 [必需 / 可悬空 / 待定] + 标该网在新基线上有没有铜 ③ 必需性分级沿用 main 2026-11-22 20:5x 已裁口径 (不重开)」

  ★**⇒ 这两条 need main 已裁完 ⇒ 缺的只是【实现】⇒ 就是你的活★**

- ★**为什么这两把尺子必须先做 (★历史教训·MEMORY 铁律★)**: ★**v44 / v46 / v47 / v48 四个臂全部打死同样三条差分对** ⇒ ★**"unconnected 变少"不等于板子更好** ⇒ ★**"把有铜的腿砍成零铜 ⇒ ratsnest 变少, 板子更烂"** ⇒ ⇒ ★**这一趟布线必须拿着【名单制 + 可比性】两把尺子去跑, 不许只看计数**★

---

## 2. ★★**交卷物 (5 件)**★★ (★就这 5 件, 不许加★)

1. ★**新建** `HW/check_board_comparable_gate.py` ⇒ ★**新闸**: 可比性前置闸 (零写板 · 只读两块板)
2. ★**新建** `HW/check_s8_target_list.py` ⇒ ★**新脚本**: S8 布线归零目标名单重读器 (零写板 · 只读一块板 + 可选参照板)
3. ★**新建** `HW/PCB/S8_TARGET_LIST_AND_COMPARABILITY.md` ⇒ ★**权威口径页**: 两把尺子的用法 + 官方基线现值快照 + 板那一趟怎么用
4. ★**新建** `HANDOFF/2026-11-22_hw-lead_ISS339_可比性前置闸与S8目标名单.md` ⇒ ★**交卷页 B0~B6 七块** (★格式照抄上一单 `HANDOFF/2026-11-19_hw-lead_ISS337_段数追平根因定位.md` 的块结构★)
5. ★**新建** `logs/iss339/` 原始输出 + ★**新建** `state/fragments/hw.yaml` 分片 (★必须走 `python3 state/frag_write.py --agent hw-lead`★)

---

## 3. D1 硬判据 【可比性前置闸】

**用法**: `python3 HW/check_board_comparable_gate.py <候选板> [参照板]` ⇒ **rc=0 = 可比 · rc=2 = 不可比 (越界即拦)**
★**判据三项, 全部必须落在带内** (三项缺一不可, 缺项 ⇒ rc=2):

| 指标 | 带 | 备注 |
|---|---|---|
| 归一化段数 | **[2300, 3200]** | ★归一化口径 **V1 (层 + 网 + 宽 + 度数=2)**★ |
| 铜长 (mm) | **[4600.0, 5900.0]** | |
| 过孔数 | **[380, 520]** | |

★**区间唯一真值 = `tmp/iss337/seg_parity_selfcheck.py` L59-61** ⇒
`SEG_NORM_LO, SEG_NORM_HI = 2300, 3200` · `CU_LO, CU_HI = 4600.0, 5900.0` · `VIA_LO, VIA_HI = 380, 520`
⇒ ★**不许自己另立区间**★ ⇒ ★**你的脚本里必须带一道自检: 读那个文件比对三个常量, 不一致 ⇒ rc=2 并打印差异**★

★**不许重写解析器** ⇒ ★**优先 `import`**: `sys.path.insert(0, "tmp/iss337")` ⇒ `from seg_parity_selfcheck import metrics, read_board` (★那个文件里已有 `metrics(path, do_normalize=True)` / `normalize_segments()` / `read_board()`★) ⇒ ★**若 `tmp/` 已被清 ⇒ 自带一份逐字复制的解析器 + 上面那道常量自检**★

★**带内样本 (main 2026-11-22 21:1x 实跑 `python3 tmp/iss337/seg_parity_selfcheck.py --selftest` ⇒ 末行 `ALL TESTS PASS`★)**:

| 板 | 归一化段数 | 过孔 | 铜长 |
|---|---|---|---|
| 官方终板 `HW/PCB/demo_mainboard.kicad_pcb` | 2649 | 433 | 5726.9 |
| 现役同工艺基线 `state/.lastgood/best_v76mg1_clrfix.kicad_pcb` | 2582 | 471 | 5582.8 |
| `v76mz` 臂 | 3099 | 486 | 5426.6 |
| `iss325ctl` 臂 | 3129 | 505 | 5483.9 |

★**`--selftest` 必须含 (★MEMORY 铁律: 自测用『实测的坏案例』当回归用例★)**:
- ① **正向对照**: 官方终板 ⇒ 必须判**可比** (rc=0)
- ② **越界反向用例**: 自己造/挑一块带外的板 ⇒ 必须被**拦** (rc=2) ⇒ ★**拿 `state/.lastgood/board_v44R_arm_13407seg_20261106_0145.kicad_pcb` (v44) 当这条的候选★**
- ③ ★**v44 在【综合判据】(可比性 + 名单) 下必须被拒** ⇒ ★**若 v44 的三项指标恰在带内 ⇒ 说明【可比性层抓不住它】⇒ 那就在交卷页里如实写明「v44 靠名单层抓·不靠可比性层」, 不许粉饰**★
- 末行必须打印 `ALL TESTS PASS` ⇒ ★**不许自己另立 selftest 成功标志**★

★**这闸【不进】`state/gate_check.py`** ⇒ ★**挂不挂、怎么挂 = main 的地界, 你只交脚本 + 挂链建议**★

---

## 4. D2 硬判据 【S8 目标名单重读器】

**用法**: `python3 HW/check_s8_target_list.py <板路径> [--baseline <参照板>]`

**必须输出 (★一份表, 一行一条网★)**:

| 列 | 内容 |
|---|---|
| 网名 | |
| 分级 | ★**[必需] / [可悬空] / [待定]** ⇒ ★**沿用下面 §5 的已裁口径, 不许自改, 不许重开**★ |
| 该网在**本板**有没有铜 | 有 / 无 (★零铜 = pad≥2 焊盘网且段数=0★) + 铜长 mm (有的话) |
| 该网在**参照板**有没有铜 | 同上 (★给了 `--baseline` 才出这列★) |
| 备注 | 差分腿 / 单端脚 / DNP 预留位 等 |

★**另必须打印三行汇总** ★:
1. ★**N' = 本板 unconnected 条数 (★不是照抄 45·是这台板自己跑出来的★)** ⇒ ★**逐条 unconnected 网名怎么取**: 照抄 `state/check_pcb_drc.py` 里的调法 ⇒ `bash state/kicad.sh pcb drc --output <json> --severity-error --severity-warning <板路径>` ⇒ 从 JSON 取 unconnected 项的网名
2. ★**两个分母口径都要给 (★不许混着写·ISS-337 铁律★)**: **全部网口径** (官方板实测 21) 与 **pad≥2 焊盘网口径** (官方板实测 24) ⇒ ★**「24 条零铜网」和「45 条 unconnected」是两个东西, 不许互相替代**★
3. ★**两边都零铜清单** (本板 ∩ 参照板都零铜) ⇒ ★**官方板 vs 现役 `v76mg1` 实测只剩 3 条: `CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N`**

★**参照板建议**: `state/.lastgood/best_v76mg1_clrfix.kicad_pcb` (★现役同工艺基线★) —— ★**参照板只读, 不许改**★

★**逐网铜长怎么取**: ★**照 `state/pair_copper_table.py` / `state/compare_net_copper.py` 的同款解析思路, 但你写自己的, 不许改那两个脚本**★ (★`state/pair_copper_table.py` 只打差分对, 本单要【全部网】★)

★**★铁律 (★必须写进 D3 文档★)★**:
- ★**「靶更小」≠「板子更好」** ★ (★现役链终板自己过不了名单制闸 ⇒ 靶更小只是【工作量口径】变了★)
- ★**判据顺序 = 先可比性 → 再名单 → 最后才看计数有没有变好** ★
- ★**本单只出尺子 + 现值快照, 不许改板 / 不许跑臂 / 不许对板下判决** ★

---

## 5. 已有事实 (★实测·直接用★ 但★**你的脚本必须自己算一遍并对上·对不上就如实写出来交 main**★)

- ★**官方板 (只读)**: `HW/PCB/demo_mainboard.kicad_pcb` ⇒ md5 **`611b869e13518c3c023fb178f91a0075`** + mtime **`2026-11-06 07:07:17.362193413`** ⇒ ★**交卷前后必须逐字节不变**★
- ★**官方板现值**: DRC violations **0** · unconnected **45** (`python3 state/check_pcb_drc.py` ⇒ C4) · 走线 18092 段 · 过孔 433
- ★**零铜网两个口径**: 全部网口径 **21** · pad≥2 焊盘网口径 **24** ⇒ ★**官方那 24 条里 21 条在 v76mg1 上已经有铜**★ ⇒ ★**两边都零铜只剩 3 条**★
- ★**必需性分级 (★main 2026-11-22 20:5x 已裁口径·沿用·不许重开·不许自改★)**:
  - ★**必需 23 条** = ① ★**15 条高速差分腿** (`CSI_D0_*` / `DSI_D0_*` 族) + ② ★**8 条单端脚**: `CAM_RESET_N` · `LED_G_D` · `USB_CC2` · `JTAG_TDI` · `UART_RX` · `SPI_SCLK_BOOT` · `SPI_MOSI_BOOT` · `SPI_MISO_BOOT`
  - ★**可悬空 1 条** = `FSIN_OUT` (★**标 NC 是板那一趟的板侧动作·现在只定口径·不定动作**★)
  - ★**待定 0 条**
  - ⇒ ★**24 条零铜网 = 23 必需 + 1 可悬空**★ ⇒ ★**你的表必须逐条对上这 24 条**★ ⇒ ★**对不上的如实写出来交 main 裁, 不许硬凑**★

---

## 6. 铁律 (★违反即废卷★)

| # | 铁律 |
|---|---|
| 1 | ★**零写板** ⇒ 交卷前自证: `md5sum HW/PCB/demo_mainboard.kicad_pcb` + `stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb` ⇒ 必须仍是 `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` |
| 2 | ★**零落表** ⇒ 不许改 `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/SCHEMATIC_LANDING_V1_LANDED.md` |
| 3 | ★**零改闸** ⇒ 不许改 `state/gate_check.py` · `state/compare_arm_official.py` · `state/chain_gate.py` · `state/check_pcb_drc.py` · `state/compare_net_copper.py` · `state/pair_copper_table.py` · `tmp/iss337/seg_parity_selfcheck.py` (★你的两个脚本是**新增**, 不是改既有★) |
| 4 | ★**零重生成** ⇒ 禁用 `state/gen_pcb_routing.py` · `state/gen_pcb_netlist_board.py` · `state/gen_kicad_project.py` · `state/replay_patch_chain.sh` · `state/clrfix_iter.sh` · `state/launch_arms.sh` · `state/v76mz_arms.sh` · `state/v76mg_arms.sh` · `state/v77_arms.sh` (★跑臂是板那一趟的活, 不是你的活★) |
| 5 | ★**零改既有文档正文** ⇒ 不许改 `HW/PCB/ONETRIP_S8_SEGMENT_PARITY_ROOTCAUSE.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `DECISION_PENDING_2026-11-16.md` · `state/fragments/pm.yaml` (★你的 D3 是**新增文档**★) |
| 6 | ★**只写自己的分片** ⇒ 只许写 `state/fragments/hw.yaml` (★必须走 `python3 state/frag_write.py --agent hw-lead` · 禁止 `open(p,"w")`★) |
| 7 | ★**沙盒只写 `tmp/iss339/` 下本单自己的目录** |
| 8 | ★**不自签 `state/issue_log.yaml`** ⇒ verify_by = **main** |
| 9 | ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·全靠自己查资料 ⇒ 没有「批一句可以发」这个选项★) ⇒ 查规格一律自己上官网查 + 标证据等级 `[官网]/[实测]/[媒体]/[推算]/[0数据]` |
| 10 | ★**不替老板拍板** ⇒ 40 条待拍板项不归你; 你只交「选项 + 代价」 |
| 11 | ★**不碰 `state/issue_log.yaml` / `state/dispatch_log.yaml`** (★那是 main 的地界★) |

---

## 7. ★★顺序铁律 (★2026-11-22 21:16 main 实测教训: cont1 死于 token 限额 2056 · cont2 死于 run timeout 17.8 分钟 ⇒ 两个都零落盘★)★★

★**每个交付物 = 一次 write 调用 · 不许攒成一条大 edit · 不许边想边改·不许重写第二遍**★

1. ★**先写 D1** (一次 write) ⇒ ★**立刻**跑一次 `python3 HW/check_board_comparable_gate.py --selftest`
2. ★**再写 D2** (一次 write) ⇒ ★**立刻**跑一次 `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb`
3. ★**再写 D3** (一次 write)
4. ★**再写 D4 交卷页** (一次 write)
5. ★**最后写分片** (frag_write.py) + 贴必跑项输出

⇒ ★**不许在写第 1 个文件之前跑任何探查 / 长命令**★ ⇒ ★**必跑项只许跑一次·加 timeout·不许 `--json`**★
⇒ ★**若你只剩一次落盘机会 ⇒ 先落 D1 + D2 (机器可判的东西比文档值钱)**★

---

## 8. 交卷自检 (★全部要贴进交卷页 D4★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
python3 HW/check_board_comparable_gate.py --selftest
python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb
python3 state/merge.py            # rc 必须 0
python3 state/gate_check.py        # Q1 必须 18/18
```

★**必跑项只许各跑一次**★ ⇒ ★**别重跑链**★

---

## 9. 交卷页 B0~B6 块结构 (★照抄上一单的块名★)

| 块 | 内容 |
|---|---|
| B0 | 一页摘要 (做了什么 / 结论 / 对板那一趟意味着什么) |
| B1 | 交付物清单 (逐件: 路径 · 字节数 · mtime) |
| B2 | ★**验收标准自评**★ (逐条 ★对/不对★ + 机器读数) |
| B3 | ★**证据分级**★ (`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` · 逐条标注) |
| B4 | ★**接口取值声明**★ (你新脚本的 rc 语义 / 入参 / 输出格式 / 跟既有闸的关系) |
| B5 | ★**未决项与卡点**★ (★要交 main 裁的·★不替老板拍★) |
| B6 | ★**可复现命令**★ (逐条 + 逐条输出) |

---

★**做完在回复里贴**: ① 两个脚本的 selftest / 实跑输出 ② 板 md5 + mtime 双证 ③ `merge.py` rc 与 `gate_check.py` 的 Q1 ④ 交卷页路径 ⑤ 分片写入结果 (★`grep -c iss339 state/fragments/hw.yaml`★)
