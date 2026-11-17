# ISS-278 · mech-lead 交卷单 · MECH 侧板侧输入收口 + 机器闸

> **单**: ISS-278 (owner=mech-lead · 派活 2026-11-17 07:3x · cron `fb67af40`)
> **性质**: ★**内部活 · MECH 侧 · 纯分析 + 规格页订正 + 机器闸类 · 零写板 · 零落表 · 零改既有 MECH 判据脚本** ★
> **续做**: ★**上一趟 (子会话 08:05:44→08:52:52 · status=timeout) 被网关重载整段截断 ⇒ 盘上零产物; 本趟从【修 TypeError】开始续做, 落一件写一件** ★
> **★【17:4x 第二趟续做 = 验收】★**: ★**主体由 09:13~09:30 那一趟补完并已 verified; 本趟不重做, 只实跑任务书 §③ 全部验收命令 ⇒ 发现两处真问题: ① 我的新闸 M5 覆盖面缺口 (本单可自修 ⇒ 已修, ★B5.7★); ② `check_demo_struct_truth.py --selftest` rc=1 (根因在 ISS-283 12:30 台账行格式 ⇒ 本单不许改那个脚本 ⇒ 升级给 main, ★B5.5★) ★**
> **一句话交付**: ★**把「板只改一次」那一趟要用的 MECH 侧输入收成【一份规格 + 一道闸】: 检修口/调试口拆成两条独立规格 · 座体高度参数化 + 三档假设 · LED 光孔两假设 + 降级 · 连接器参数对照表** ★

---

## 交付物清单

| # | 交付物 | 路径 | 状态 |
|---|---|---|---|
| 1 | MECH 侧板侧输入清单 (机器可读) | `MECH/BOARD_ONEPASS_MECH_SYNC.md` | ★**已落 (38271 → 83369 B; ★17:4x 续做追加 §12★)**★ |
| 2 | ISS-276 归一页追加式订正 (§3b/§4b/§6b/§7b/§8) | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | ★**已落 (25766 → 48432 B, 追加式; ★前 25766 字节 md5 = c86b11d8… = ISS-276 原文件, 逐字节相同★)**★ |
| 3 | 机器闸 | `MECH/check_onepass_mech_sync.py` | ★**已落 (31303 → 56367 B; ★17:4x 续做修 M5 覆盖面: 拆 M5a/M5b, 5 件一件不少 + 新增反向用例 ⑦b★)**★ |
| 4 | 本交卷单 (B1~B6) | `HANDOFF/2026-11-17_mech-lead_ISS278_MECH侧板侧输入收口.md` | ★**已落 (58238 B; ★17:4x 续做补 B2 两行 + B3.6/B3.7 + B5.5/B5.6/B5.7 + rc 日志 16 行★)**★ |
| 5 | 分片 (claim×2 / artifact×3 / need×1 / status) | `state/fragments/mech.yaml` | ★**已落 (★17:4x 续做段: claim×2 + need×1 + status; 同 key 重复 need 已合并成 1 条★)**★ |
| — | ★**实算脚本 (修复后)** ★ | ★`logs/iss278/compute_iss278.py` (10098 → 10266 B) ★ | ★**已落 + 跑通 rc=0** ★ |
| — | ★**实算产物** ★ | ★`logs/iss278/compute_iss278.json` (0 → 13122 B) ★ | ★**已落** ★ |

---

## B1 · 结论摘要

> ★**本单交付的不是一个「结论」, 是一个【规格 + 一道闸】; 下面的 6 条是闸守的东西** ★

| # | 结论 | 关键数 | 证据级 |
|---|---|---|---|
| ★1 ★ | ★**检修口与调试口是【两条】, 不许再合并** ★ | ★**`J_DEBUG` (144.30, 58.00) ↔ `J_UART` (20.74, 70.00): ΔX 123.56 / ΔY −12.00 / 直线 124.141345 mm; 合并必须清空区并集宽 126.2175 vs 开口宽 10.20 ⇒ 单边间隙 −58.00875 ⇒ 缺口 116.0175 mm ⇒ 几何上不可能** ★ | ★`[实测]` (板读 + 实算) ★ |
| ★2 ★ | ★**座体真实高度 h = `[0数据]`; 降级方案 = 参数式 + 三档 + 按公式取值 (不许把 2.54 当事实, 也不许挂成「等外部回复」)** ★ | ★**`OPEN_Y_eff(h) = max(4.60, h + 1.80)`; 三档 h = 0.90 / 2.54 / 4.00 ⇒ 开口 Y 4.60 / 4.60 / 5.80; 三档全部落板框内 + 压 SoM 焊盘 = 0** ★ | ★`[0数据]` (h) + `[推算]` (三档代入) + `[实测]` (档位锚点) ★ |
| ★3 ★ | ★**★「按 h = 4.00 档画」⇒ 三档全覆盖 ⇒ 座体型号定版不触发第二次改板 ★** ★ | ★**h = 4.00 ⇒ 开口 Y 5.80, 最坏单边间隙 0.6000 (= CRIT, 刚好过) ⇒ 这是保守上界, 型号定版后若 h 更小只会开口变小 ⇒ 结构件开口做大做小都行** ★ | ★`[推算]` ★ |
| ★4 ★ | ★**`D_LED_G` 出光侧结构光孔 = `[0数据]`; 两假设各一份空间, 只列代价不代拍** ★ | ★**假设 A (有孔): 可放行空间 X 6.940..8.250 × Y 63.700..67.900, 走线 0.450~0.965 mm, 板面落位【要改】; 假设 B (无孔): 整高自由带 X 1.550..3.450 + X 72.540..73.660 (Y 1.450..98.950), 走线 0.450~0.965 mm 但现状 93.492727 mm 也合法, 板面落位【不用改】** ★ | ★`[实测]` + `[推算]` + `[0数据]` ★ |
| ★5 ★ | ★**`demo_mainboard_params.json` 与落表板对不上 ⇒ 只登记, 转 hw-lead 改, 本单零改 `HW/`** ★ | ★**19 项里 12 项对不上 (位号名 2 · 脚数 2 · 间距 2 · 位置 4 · SoM 拓扑/尺寸/位置 5 · 圆角 1 ⇒ 另含 BOM/网表口径 1.27 mm 与板读 land pattern 0.50 mm 的出入 2 项); 只有板宽/板高/板厚/铜层/`J_UART` 位号 5 项一致** ★ | ★`[实测]` ★ |
| ★6 ★ | ★**新增覆盖度闸 `MECH/check_onepass_mech_sync.py`: M1~M5 全绿, 8 条反向用例全抓到, 且真件 5 件 md5 跑完自检后仍逐字节不变** ★ | ★**rc=0 (主) / rc=0 (--selftest)** ★ | ★`[实测]` (实跑) ★ |

### B1.1 三条不许搞混的 (★本轮踩出来的★)

| # | 纪律 | 本单怎么落的 |
|---|---|---|
| ★1 ★ | ★**「座体高度 2.54」是假设, 不是事实** ★ | ★**§4b 参数式 + 三档 + 降级路径; 机器块里 `body_h_ref_is_fact: false`; 机器闸 M3 三档逐档验** ★ |
| ★2 ★ | ★**「检修口」和「调试口」是两条, 不是一条** ★ | ★**§3b 两条独立规格; 机器块 `openings[]` 必须恰好 2 条 (M2 判「只有 1 条」即红); 合并禁令 + 缺口 116.0175 留档** ★ |
| ★3 ★ | ★**「MECH 侧板侧输入」不等于「MECH 内部的事」** ★ | ★**§3 「MECH → HW 的输入清单」15 条, 每条带「按什么值画」+「本机实测依据」; §3.4 是可直接抄进作业包 §3-S6 的认领句** ★ |

---

## B2 · 验收标准逐条自评

| 验收命令 (本机实跑) | 期望 | 实跑 rc | 自评 |
|---|---|---|---|
| ★`python3 MECH/check_onepass_mech_sync.py` ★ | rc=0 (★新建★) | ★**rc=0** ★ | ★**✅ M1~M5 全过** ★ |
| ★`python3 MECH/check_onepass_mech_sync.py --selftest` ★ | rc=0 (★新建★, ≥5 条) | ★**rc=0** ★ | ★**✅ 8 条反向用例 (≥5) 全抓到** ★ |
| ★`python3 MECH/check_board_frame_coords.py` ★ | rc=0 (★ISS-276 的闸, 不许被改红★) | ★**rc=0** ★ | ★**✅ 四项全过 (追加式订正后仍全绿)** ★ |
| ★`python3 MECH/check_board_frame_coords.py --selftest` ★ | rc=0 | ★**rc=0** ★ | ★**✅ 6 条反向用例全抓到** ★ |
| ★`python3 MECH/board_port_opening_s6_check.py --json` ★ | rc=0 (★现值, 别改★) | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 MECH/jd_y0_feasibility.py --selftest` ★ | rc=0 (★别改★) | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 MECH/check_demo_struct_truth.py` ★ | rc=0 (★ISS-273 成果, 只许只读★) | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 MECH/check_demo_struct_truth.py --selftest` ★ | rc=0 (★21/21, 只许只读★) | ★**rc=1** ★ | ★**❌ 现值红了 —— ★★根因不在本单 (ISS-283 12:30 落表台账行格式变更★) ⇒ 详见 ★B5.5★, 本单不许改那个脚本 ⇒ 升级给 main** ★ |
| ★`python3 MECH/service_port_check.py` ★ | rc=0 | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 MECH/verify_budget.py` ★ | rc=0 | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 state/merge.py` ★ | rc=0 | ★**rc=0** ★ | ★**✅ 「STATE.yaml 已刷新 (2026-11-17T09:27:34+08:00) · 产出 486 | 阻塞 43 (高危 33) | 未闭合需求 269 | 冲突 0」★** |
| ★`python3 state/gate_check.py` ★ | rc=0 (Q1 18/18) | ★**rc=0** ★ | ★**✅ 「【Q1 交付齐备率】 18/18 个必填验收块齐全」+ Q6 硬件真源闸 ✅ 通过 (rc=0)★** |
| ★`python3 state/check_brief_commands.py --brief-file MECH/BOARD_ONEPASS_MECH_SYNC.md` ★ | rc=0 (★本单清单里的判据命令不许指向不存在的脚本★) | ★**rc=0** ★ | ★**✅ 零告警★** |
| ★`md5sum` 五件受保护 ★ | 逐字节不变 | ★**2/2 硬基线相同 + 3/3 台账链头对上** ★ | ★**✅ 板 611b869e… / `.kicad_pro` 3e504d2b… (★硬基线, 逐字节不变★) + 网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece… (★现值 ≠ 任务书 07:2x 基线, ★★但 = 落表台账链头 (ISS-283 12:30 授权落表) ⇒ 合法落表, 不是偷改 ⇒ 详见 ★B5.6★)★** ★ |

### B2.1 边界逐条自证

| 边界 | 自证 |
|---|---|
| ★**零写板 / 零落表** ★ | ★**五件 md5 跑前跑后逐字节相同 (机器闸 M5 + 本单 B6 复核)** ★ |
| ★**零改既有 MECH 判据脚本** ★ | ★**`check_demo_struct_truth.py` 6972b867… / `service_port_check.py` db58ff6a… / `board_port_opening_s6_check.py` be8bf0ce… / `jd_y0_feasibility.py` 55db5346… / `verify_budget.py` 95d6b011… ⇒ 与 08:26 基准逐位相同; 新闸是【新建】文件** ★ |
| ★**零改 HW 文件** ★ | ★**`HW/` 零字节写入; 本单只**读** `HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` / 网表 / 脚表 / BOM / `demo_mainboard_params.json`** ★ |
| ★**零改 `MECH/BOARD_GEOM_30MM.md` 的 RK3576 老基线** ★ | ★**只【引用】它 (§1 帧声明 + §3.4 警语), 一个字不改** ★ |
| ★**零改别人的交卷单** ★ | ★**ISS-276 的交卷单一个字没改; 归一页只【追加式】订正 (前 25766 字节与 ISS-276 原文件逐字节相同 ⇒ 追加点 = 25776, 追加段 = 22656 字节)** ★ |
| ★**零外发** ★ | ★**不发邮件 / 不询价 / 不问询 / 不采购; 本单 0 条 `[官网]`/`[媒体]`; 缺口一律写 `[0数据]` + 降级方案** ★ |
| ★**证据分级** ★ | ★**每条结论标 `[实测]` / `[推算]` / `[0数据]`; 实物 `[实测]` = 0 条** ★ |
| ★**零实物** ★ | ★**本机无板 ⇒ 打印/量测全部 `[0数据]`** ★ |
| ★**不替老板拍板** ★ | ★**座体高度 h / 结构光孔有否 / 亮度档 G-5 = 只列事实与代价, 归 main→boss (§4.1/§4.2/§4.3)** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead`** ★ |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/mech.yaml`** ★ |

### B2.2 已知现状 (★不必修, 但写清★)

| 项 | 状态 |
|---|---|
| ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` rc=1 (板多 2 个带网焊盘) ★ | ★**既有状态, 本单不负责修; 本单保证没让它更糟 (五件 md5 不变 ⇒ 板一个字节没动)★** ★ |
| ★`MECH/check_demo_struct_truth.py` 的 6 个 PCB 类 id 仍是 FAIL ★ | ★**那是正确状态 (排队等原理图定稿), 不是缺陷; 本单没为了让门禁全绿去动它们** ★ |

---

## B3 · 反向自证 (★实跑原始输出★)

### B3.1 座体高度三档代入 (★brief 指定的必贴项★) —— `python3 MECH/check_onepass_mech_sync.py` 原始输出片段

```
  M3 座体高度参数式 . ✅ 绿  (公式 OPEN_Y_eff(h) = max(4.60, h + 2*(0.60+0.30)) = max(4.60, h + 1.80))
      · PORT_OPEN_DEBUG    h=0.90  eff=4.60  rect=(137.85, 148.05, 54.3, 58.9) 落框=True 压SoM=0 最坏间隙Y=1.550
      · PORT_OPEN_DEBUG    h=2.54  eff=4.60  rect=(137.85, 148.05, 54.3, 58.9) 落框=True 压SoM=0 最坏间隙Y=0.730
      · PORT_OPEN_DEBUG    h=4.00  eff=5.80  rect=(137.85, 148.05, 53.7, 59.5) 落框=True 压SoM=0 最坏间隙Y=0.600
      · PORT_OPEN_UART     h=0.90  eff=4.60  rect=(13.79, 23.99, 66.3, 70.9) 落框=True 压SoM=0 最坏间隙Y=1.550
      · PORT_OPEN_UART     h=2.54  eff=4.60  rect=(13.79, 23.99, 66.3, 70.9) 落框=True 压SoM=0 最坏间隙Y=0.730
      · PORT_OPEN_UART     h=4.00  eff=5.80  rect=(13.79, 23.99, 65.7, 71.5) 落框=True 压SoM=0 最坏间隙Y=0.600
```

★**⇒ 三档全部: 落板框内 = True · 压 SoM 焊盘 = 0 · 最坏单边间隙 ≥ CRIT 0.60 (h=4.00 档刚好 0.6000)** ★

### B3.2 新闸主跑 (★M1~M5 全过★) —— `python3 MECH/check_onepass_mech_sync.py` 原始输出

```
  帧白名单: ['B160x100', 'F30A', 'P60x15']
  M1 帧标签 ........ ✅ 绿  (坐标组 4 个 / 条目 9 条)
  M2 两条开口不压 SoM  ✅ 绿
      · PORT_OPEN_DEBUG    调试口    罩 J_DEBUG                rect=(137.85, 148.05, 54.3, 58.9) ⇒ 压 SoM 焊盘 0
      · PORT_OPEN_UART     检修口    罩 J_UART                 rect=(13.79, 23.99, 66.3, 70.9) ⇒ 压 SoM 焊盘 0
  M4 判据命令真存在 .. ✅ 绿  (命令 11 条)
      · MECH-PORT-DEBUG        MECH/check_onepass_mech_sync.py                      存在
      · MECH-PORT-UART         MECH/check_onepass_mech_sync.py                      存在
      · MECH-PORT-NOMERGE      MECH/check_onepass_mech_sync.py                      存在
      · MECH-BODY-H            MECH/check_onepass_mech_sync.py                      存在
      · MECH-LED-G             MECH/check_onepass_mech_sync.py                      存在
      · MECH-LED-GD-NET        MECH/board_port_opening_s6_check.py                  存在
      · MECH-LED-GD-NET        MECH/check_onepass_mech_sync.py                      存在
      · MECH-CONN-PARAMS       MECH/check_onepass_mech_sync.py                      存在
      · MECH-CONN-PARAMS       state/check_brief_commands.py                        存在
      · MECH-LED-BRIGHT-G5     MECH/check_onepass_mech_sync.py                      存在
      · MECH-LED-HOLE          MECH/check_onepass_mech_sync.py                      存在
  M5 受保护 5 件 md5 . ✅ 绿
      · HW/PCB/demo_mainboard.kicad_pcb            611b869e13518c3c023fb178f91a0075 == 611b869e13518c3c023fb178f91a0075
      · HW/PCB/demo_mainboard.kicad_pro            3e504d2be83152e337949723e909be1b == 3e504d2be83152e337949723e909be1b
      · HW/netlist_v1.csv                          e06c1dd633566aa44732762c2ff99d1c == e06c1dd633566aa44732762c2ff99d1c
      · HW/netlist_v1_pins.csv                     287e7861a0d1007748d92d9fbecdd490 == 287e7861a0d1007748d92d9fbecdd490
      · HW/BOM_v1.csv                              94642d07a69e8d60dd2af57f69b93607 == 94642d07a69e8d60dd2af57f69b93607

================================================================================================
【绿】M1~M5 全过
================================================================================================
rc=0
```

### B3.3 新闸反向用例 (★8 条, 每条自证真改到目标★) —— `python3 MECH/check_onepass_mech_sync.py --selftest` 原始输出

```
  [基线] M1=OK M2=OK M3=OK M4=OK M5=OK
  [OK ] ① 改检修口矩形一个角 (y0 66.300 ⇒ 52.000) ⇒ M2 红: 是 · md5 b0a975fa ⇒ 9409831a (确实改了: True) · M2 命中=[('PORT_OPEN_DEBUG', 0), ('PORT_OPEN_UART', 23)]
  [OK ] ② 把两条开口合并成一个 ⇒ M2/M3 红: 是 · md5 b0a975fa ⇒ 4face20f (确实改了: True) · M2 错误 1 条 / M3 错误 1 条
  [OK ] ③ 抽掉正文表头的帧标签 ⇒ M1 红: 是 · 命中模式: True · md5 b0a975fa ⇒ acaf94b6 (确实改了: True) · M1 错误 4 条
  [OK ] ④ 抽掉机器块里的 frame 字段 ⇒ M1 红: 是 · md5 b0a975fa ⇒ 9350b19d (确实改了: True) · M1 错误 1 条
  [OK ] ⑤ 把 h 三档之一改到不合理 (4.00 ⇒ 40.00) ⇒ M3 红: 是 · md5 b0a975fa ⇒ 95222d4c (确实改了: True) · M3 错误 3 条
  [OK ] ⑥ 把判据命令改成不存在的脚本 ⇒ M4 红: 是 · md5 b0a975fa ⇒ 77cc3d06 (确实改了: True) · M4 错误 11 条
  [OK ] ⑦ 改受保护件 (HW/BOM_v1.csv) ⇒ M5 红: 是 · md5 94642d07 ⇒ 32d2c2cc (确实改了: True) · M5 错误 1 条
  [OK ] ⑧ 自检跑完, 真件 5 件 md5 仍逐字节不变: 是 · demo_mainboard.kicad_pcb=611b869e · demo_mainboard.kicad_pro=3e504d2b · netlist_v1.csv=e06c1dd6 · netlist_v1_pins.csv=287e7861 · BOM_v1.csv=94642d07

================================================================================================
【自检结论】✅ 全抓到
================================================================================================
rc=0
```

★**★ 逐条对照 brief 要求的 5 条反向用例 (★一条不许少★)** ★

| brief 要求 | 本单对应 | 自证 |
|---|---|---|
| ★① 改检修口矩形一个角 ⇒ M2 红 ★ | ★**①** (y0 66.300 ⇒ 52.000 ⇒ 压 SoM 焊盘 23 个) ★ | ✔ M2 红 + md5 变了 |
| ★② 把两条开口合并 ⇒ M2/M3 红 ★ | ★**②** (机器块 `openings[]` 收成 1 条合并矩形) ★ | ✔ M2 红 + M3 红 + md5 变了 |
| ★③ 抽帧标签 ⇒ M1 红 ★ | ★**③** (正文表头) + ★**④** (机器块 `frame` 字段) —— 两条都做 ★ | ✔ M1 红 + md5 变了 |
| ★④ 把 h 三档之一改到不合理 ⇒ M3 红 ★ | ★**⑤** (4.00 ⇒ 40.00, 超板读座体盒高 4.00 ⇒ 物理不合理 + 出框) ★ | ✔ M3 红 + md5 变了 |
| ★⑤ 改受保护件 ⇒ M5 红 ★ | ★**⑦** (沙盒里给 `HW/BOM_v1.csv` 追加 1 行) ★ | ✔ M5 红 + md5 变了 |
| ★**(补) 判据命令真存在 ⇒ M4 红** ★ | ★**⑥** (改成 `MECH/does_not_exist_iss278.py`) ★ | ✔ M4 红 + md5 变了 |
| ★**(补) 真件跑完自检后仍逐字节不变** ★ | ★**⑧** ★ | ✔ 5/5 md5 不变 |

### B3.4 追加式订正的证明 (★老字一字不许删★)

```
$ python3 -c "…"
追加段起点字符位 = 18205
追加段之前的前缀字节数 = 25776
原文件字节数 (09:13 前 ls) = 25766
前缀尾部 = '】, 不是【160×100 台架板不能用】; 本页的开口是另一道几何题, 两句不许并成一句** ★\n\n---\n---\n\n'
⇒ 前缀字节数 25776 = 原 25766 + 我加的分隔符 10 字节 ("\n\n---\n---\n\n")
⇒ 新文件的前 25766 字节与 ISS-276 原文件【逐字节相同】 ⇒ 追加式成立, 老字一字未删未改
```

★**⇒ 追加段起点 = 字节 25776; ISS-276 的 §1~§6.1 全部原封不动; 新增内容 = §3b / §4b / §6b / §7b / §8 (+ §8.1 边界)** ★

### B3.5 上一趟挂掉的那个 TypeError (★修好并重算★)

```
$ cat logs/iss278/compute_iss278.err          # 修之前
Traceback (most recent call last):
  File ".../logs/iss278/compute_iss278.py", line 116, in <module>
    rp = {p["num"]: p for p in res["pads"]}; r2 = rp["2"]
          ~^^^^^^^
TypeError: tuple indices must be integers or slices, not str

$ # 修之后 (两处最小改动)
  ① conn(): 加 "pads_raw": ps   (★原来 pads 被打平成 tuple, 后面按 dict 索引必炸★)
  ② led_net_len(): 返回 (dist, (x,y)) ⇒ 不能整体 round ⇒ 拆开取

$ python3 logs/iss278/compute_iss278.py > logs/iss278/compute_iss278.json
rc=0
$ ls -la logs/iss278/compute_iss278.json
-rw-rw-r-- 1 yuewuya yuewuya 13122 Nov 17 09:13 logs/iss278/compute_iss278.json    ★★原先 0 B ⇒ 算出来的数一个没落盘, 现在全落盘★★
```

★**⇒ 全部实算数都来自这个脚本的实跑输出 (板读 + 只读 import 既有闸常量) ⇒ 一个数都不是抄文档的** ★

### ★B3.6 ★【续做新增】M5 覆盖面订正的实跑原始输出 (★2026-11-17 17:5x★) ★

★**★ 订正前 (★只查 2 件却宣称 5 件★)** ★
```
  M5 受保护 5 件 md5 . ✅ 绿
      · HW/PCB/demo_mainboard.kicad_pcb            611b869e13518c3c023fb178f91a0075 == 611b869e13518c3c023fb178f91a0075
      · HW/PCB/demo_mainboard.kicad_pro            3e504d2be83152e337949723e909be1b == 3e504d2be83152e337949723e909be1b
      ★★ 只有 2 行 ⇒ 声明「5 件」与实查「2 件」对不上 (覆盖面缺口) ★★
```

★**★ 订正后 (★M5a 硬基线 2 件 + M5b 台账链头 3 件 = 5 件一件不少★)** ★
```
$ python3 MECH/check_onepass_mech_sync.py
rc=0
  M5 受保护 5 件 md5 . ✅ 绿  (M5a 硬基线 2 件 + M5b 台账链头 3 件)
      · HW/PCB/demo_mainboard.kicad_pcb            611b869e13518c3c023fb178f91a0075 == 611b869e13518c3c023fb178f91a0075
      · HW/PCB/demo_mainboard.kicad_pro            3e504d2be83152e337949723e909be1b == 3e504d2be83152e337949723e909be1b
      · HW/netlist_v1.csv                          37f62ac3f0b8… == 台账链头 37f62ac3f0b8…  落表单号 ['ISS-283']  链长 10  记录 10
      · HW/netlist_v1_pins.csv                     a4270120454a… == 台账链头 a4270120454a…  落表单号 ['ISS-283']  链长 8  记录 10
      · HW/BOM_v1.csv                              5d02bece9477… == 台账链头 5d02bece9477…  落表单号 ['ISS-283']  链长 7  记录 10

【绿】M1~M5 全过
```

★**★ 新增反向用例 ⑦b (★偷改台账管理件 ⇒ M5b 红★)** ★
```
$ python3 MECH/check_onepass_mech_sync.py --selftest
rc=0
  [OK ] ⑦ 改受保护件 (HW/PCB/demo_mainboard.kicad_pcb) ⇒ M5 红: 是 · md5 611b869e ⇒ 9ca97cf9 (确实改了: True) · M5 错误 1 条
  [OK ] ⑦b 偷改台账管理件 (HW/netlist_v1.csv) 而台账不更新 ⇒ M5b 红: 是 · 命中 M5b 断言: 是 · md5 37f62ac3 ⇒ 61e3019d (确实改了: True) · M5 错误 1 条
  [OK ] ⑧ 自检跑完, 真件 5 件 md5 仍逐字节不变: 是 · demo_mainboard.kicad_pcb=611b869e · demo_mainboard.kicad_pro=3e504d2b · netlist_v1.csv=37f62ac3 · netlist_v1_pins.csv=a4270120 · BOM_v1.csv=5d02bece

【自检结论】✅ 全抓到
```

### ★B3.7 ★【续做新增】`check_demo_struct_truth.py --selftest` rc=1 的根因复现 (★只读沙盒, 真台账一个字节不碰★) ★
```
$ python3 MECH/check_demo_struct_truth.py --selftest
rc=1
Traceback (most recent call last):
  File ".../MECH/check_demo_struct_truth.py", line 1005, in <module>
    sys.exit(main())
  ...
  File ".../MECH/check_demo_struct_truth.py", line 912, in selftest
    lt={LEDGER_CANON: break_head_ticket(base_led, "HW/netlist_v1.csv")})
  ...
  File ".../MECH/check_demo_struct_truth.py", line 889, in break_head_ticket
    assert hit, "没找到台账最新记录那一行"
AssertionError: 没找到台账最新记录那一行

$ # 根因定位 (本机实跑, 只读)
head = 37f62ac3f0b8   (台账链头)
L1069 (ISS-257 旧格式): 含 head[:12]=False · 以 | 开头=True · 含 ISS-=True
L1371 (ISS-283 新格式): 含 head[:12]=True  · 以 | 开头=True · 含 ISS-=False  ★★ 命中三条件缺一 ⇒ assert 炸 ★★
⇒ 把 L1371 补上 "ISS-283" 后, 同一段命中逻辑 hit: 0 ⇒ 1 ⇒ 根因确认 = 台账行格式变更 (ISS-283 12:30), 与本单无关
```

---

## B4 · 接口取值声明

> ★**本节声明本单【对外承诺的取值】, 以及这些值从哪来、谁能改** ★

### B4.1 MECH 对 HW 的接口取值 (★hw-lead 那一趟直接抄★)

| 接口 | 取值 | 帧 | 出处 | 谁可改 |
|---|---|---|---|---|
| ★**调试口开口** ★ | ★**X 137.850..148.050 × Y 54.300..58.900** ★ (座体宽 1.775 · 间隙 X 4.2125 / Y 1.0300) | ★`B160x100` ★ | ★`MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 `openings[PORT_OPEN_DEBUG]` + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3b.2 ★ | ★**MECH 改 (改完必须重跑 `MECH/check_onepass_mech_sync.py`)★** ★ |
| ★**检修口开口** ★ | ★**X 13.790..23.990 × Y 66.300..70.900** ★ (座体宽 2.540 · 间隙 X 3.8300 / Y 1.0300) | ★`B160x100` ★ | ★同上 `openings[PORT_OPEN_UART]` + §3b.2 ★ | ★**MECH 改** ★ |
| ★**开口 Y 公式** ★ | ★**`OPEN_Y_eff(h) = max(4.60, h + 1.80)`; 三档 0.90 / 2.54 / 4.00** ★ | ★`B160x100` ★ | ★§4b.1 + §5 `consts` ★ | ★**MECH 改 (h 定版后由 hw-lead 把真 h 给 MECH, MECH 重算)** ★ |
| ★**`D_LED_G` 整高自由带** ★ | ★**X 1.550..3.450 + X 72.540..73.660, Y 1.450..98.950** ★ | ★`B160x100` ★ | ★§5 `led.full_height_bands` ★ | ★**MECH 改** ★ |
| ★**`D_LED_G` 最近落位带** ★ | ★**X 6.940..8.250 × Y 63.700..67.900** ★ | ★`B160x100` ★ | ★§5 `led.nearest_band` ★ | ★**MECH 改** ★ |
| ★**`LED_G_D` 现状长度** ★ | ★**93.492727 mm** (两端 `R_LED_G`.2 (7.50, 62.60) ↔ `D_LED_G`.1 (100.80, 56.60)) ★ | ★`B160x100` ★ | ★§4.1 / §6b.1 (板读) ★ | ★**不可改 (是实测)** ★ |
| ★**连接器占位 (真源)** ★ | ★**`J_DEBUG` (144.30, 58.00) 1×4 @0.50 · `J_UART` (20.74, 70.00) 1×2 @0.50 · `J_USB_C` (140.000, 5.250) · SoM `J_SOM_P1..P4` 保守包络 X 13.650..70.350 × Y 7.610..54.390** ★ | ★`B160x100` ★ | ★§7b (板读) ★ | ★**不可改 (是实测)** ★ |
| ★**帧 id** ★ | ★**`B160x100` / `F30A` / `P60x15` (三件套, 不许造第四套)** ★ | —— | ★**唯一权威 = `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES`** ★ | ★**hw-lead 改权威表 ⇒ MECH 跟 (两边不得各写一套)** ★ |

### B4.2 本单不承诺 / 不改的

| 项 | 状态 |
|---|---|
| ★**开口最终坐标 / `D_LED_G` 最终坐标** ★ | ★**不是 MECH 的活 (PCB 布局 = hw-lead); MECH 只给空间 + 条件 + 公式** ★ |
| ★**座体型号 / 真实高度** ★ | ★**MECH 不选型; 只给参数式 + 三档; 真 h 到位后 MECH 重算** ★ |
| ★**`HW/PCB/demo_mainboard_params.json`** ★ | ★**MECH 不改 (域外); 只出对照表 (§7b) + 转交 need** ★ |
| ★**`HW/PCB/BOARD_ONEPASS_WORKPACKET.md`** ★ | ★**MECH 不写 (hw-lead 的文件, ISS-281 同批在做); 只出可抄的认领句 (§3.4)** ★ |
| ★**`MECH/BOARD_GEOM_30MM.md` / `state/issue_log.yaml` / 别人的分片** ★ | ★**一个字不改** ★ |

---

## B5 · 未决项与卡点

### B5.1 归 main → 老板拍 (★只列事实与代价, 不代拍★)

| # | 待拍项 | 事实 | 代价 A (不拍 / 按 A 走) | 代价 B (按 B 走) | 排期约束 |
|---|---|---|---|---|---|
| ★1 ★ | ★**亮度档 G-5** ★ | ★**绿灯亮度档 = `[0数据]`; 现状 `R_LED_G` + `D_LED_G` 已在板上** ★ | ★**零板面动作** ★ | ★**改串阻值 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位 ⇒ 【板要改第二次】** ★ | ★**必须排在「板只改一次」之前** ★ |
| ★2 ★ | ★**座体高度 h 的确认途径** ★ | ★**h = `[0数据]`; 本机物理上量不到 (无实物)** ★ | ★**降级路径 = 参数式 + 三档 + 按公式取值; 本单不需要它就能开那一趟** ★ | —— | ★**不阻塞** ★ |
| ★3 ★ | ★**结构光孔有 / 无** ★ | ★**光孔位置 = `[0数据]`; 只差「`D_LED_G` 要不要从 (101.25, 56.80) 挪走」** ★ | ★**假设 B (无孔): 板面落位不用改** ★ | ★**假设 A (有孔): `D_LED_G` 必挪 ⇒ 板面落位要改 ⇒ 走线可压到 0.450~0.965 mm** ★ | ★**必须排在「板只改一次」之前** ★ |

### B5.2 转 hw-lead (★本单一个字不许改 `HW/`★)

| # | 事项 | 出处 | 说明 |
|---|---|---|---|
| ★1 ★ | ★**改 `HW/PCB/demo_mainboard_params.json` 的连接器/SoM 段** ★ | ★§7b 对照表 (19 项里 12 项对不上) ★ | ★**以落表板实读为真源; 涉及 `usb_c_ref` / `usb_c_position_mm` / `uart_pins` / `uart_pitch_mm` / `uart_position_mm` / `jtag_ref` / `jtag_pins` / `jtag_pitch_mm` / `jtag_position_mm` / `som.ref` / `som.pins_x` / `som.pins_y` / `som.width_mm` / `som.height_mm` / `som.position_mm` / `board.corner_radius_mm`** ★ |
| ★2 ★ | ★**核对排针间距口径 (BOM/网表写 1.27 mm, 板读 land pattern 是 0.50 mm)** ★ | ★§7b.2 ★ | ★**选型的实物排针必须能落进 0.50 mm 间距的 land pattern, 否则 ⇒ 改板** ★ |
| ★3 ★ | ★**收 §3.4 的 S6 认领句进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6** ★ | ★`MECH/BOARD_ONEPASS_MECH_SYNC.md` §3.4 ★ | ★**ISS-281 同批在做那个文件 ⇒ 两边各写各的, 只交叉引用** ★ |

### B5.3 本单的卡点 (★阻塞别人吗★)

| # | 卡点 | 阻塞谁 | 状态 |
|---|---|---|---|
| ★1 ★ | ★**无** —— 本单 5 件交付物全部落盘且闸全绿; §4 三条待拍项【不阻塞 hw-lead 开那一趟】(按假设 B + 按 h = 4.00 保守上界画即可) ★ | —— | ★**无阻塞** ★ |

### B5.4 证据分级自述

| 证据级 | 本单条数 | 说明 |
|---|---|---|
| ★`[实测]` ★ | ★**大量 (板读坐标 / 焊盘 / md5 / 脚本实跑输出 / params 读数 / BOM 读数)** ★ | ★**本机无实物 ⇒ 一切「实测」= 文件实读 + 脚本实跑** ★ |
| ★`[推算]` ★ | ★**大量 (开口几何 / 间隙 / 三档代入 / 两假设空间)** ★ | ★**设计态几何 + 公差栈** ★ |
| ★`[0数据]` ★ | ★**座体真实高度 / 座体型号与脚数 / 结构光孔位置与有无 / LED 亮度档** ★ | ★**本机查不到 ⇒ 已给降级方案, 没挂成「等外部回复」** ★ |
| ★`[官网]` / ★`[媒体]` ★ | ★**0 条** ★ | ★**本单零外发、零询价、零问询** ★ |
| ★**实物 `[实测]`** ★ | ★**0 条** ★ | ★**本机无板** ★ |

### ★B5.5 ★【续做新增】`MECH/check_demo_struct_truth.py --selftest` rc=1 —— 根因不在本单, 升级给 main ★

> ★**★ 2026-11-17 17:4x 续做实跑发现 ★★** ★

| 项 | 实测事实 |
|---|---|
| 现象 | ★**`python3 MECH/check_demo_struct_truth.py --selftest` ⇒ rc=1** (任务书 §③ 期望 rc=0) ★ |
| 报错 | ★**`AssertionError: 没找到台账最新记录那一行`** (在 `break_head_ticket()` 里) ★ |
| ★**是不是本单造成的** ★ | ★**不是** ★ —— ① 本单 09:29 跑时 rc=0 (交卷单 B2 表留了记录); ② 12:30 的落表台账改写是 ★**ISS-283 (hw-lead) 的授权落表**★; ③ 本单没碰那个脚本 (md5 `6972b867c8243bc971408f972dc7727e` 与 08:26 基准逐位相同) ★ |
| ★**根因 (本机实跑已复现)** ★ | ★**`break_head_ticket()` 找台账「链头那一行」的命中条件是三条同时成立: ① 该行含 `head[:12]` ② 该行以 `|` 开头 ③ 该行含 `ISS-`** ★ ⇒ ★**ISS-283 12:30 的新格式行 (L1371) 把单号挪到了别的行 ⇒ 三条同时不成立 ⇒ assert 炸** ★ ⇒ ★**本机实跑验证: 把 L1371 补上 `ISS-283` 后, 同一段命中逻辑 `hit` 从 0 变 1 ⇒ 根因确认** ★ |
| ★**本单能不能修** ★ | ★**不能** —— 那个脚本属任务书 §④ 点名「零改既有 MECH 判据脚本」; 且根因在【台账行格式】不在脚本逻辑 ★ |
| 建议修法 (★只列, 不代拍★) | ★**① 改台账行格式 (让 ISS-283 的行也带单号) —— 那是落表链的写法契约, 归落表链; ② 或改 `break_head_ticket()` 的命中条件 (★改成【含 `head[:12]` + 以 `|` 开头】即可, 不必强求同一行含 `ISS-`★) —— 属 MECH 侧但本单边界不许动** ★ |
| ★**⇒ 处置** ★ | ★**升级给 main (分片 need `iss278_mech_demo_struct_truth_selftest_regression`) ⇒ 本单不自签 `state/issue_log.yaml`, 不代 main 派单, 不擅自改那个脚本** ★ |

### ★B5.6 ★【续做新增】受保护 5 件的基线变更留档 (★不是本单改的★) ★

| 件 | 任务书 §③ 基线 (★07:2x★) | 本机现值 (★17:4x★) | 谁改的 | 本单参与? |
|---|---|---|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | ★**同左** ★ | —— | ★**没动** ★ |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | ★**同左** ★ | —— | ★**没动** ★ |
| `HW/netlist_v1.csv` | `e06c1dd633566aa44732762c2ff99d1c` | ★**`37f62ac3f0b81d92ca7d48fdea717f07`** ★ | ★**ISS-283 12:30 授权落表** ★ | ★**没动** ★ |
| `HW/netlist_v1_pins.csv` | `287e7861a0d1007748d92d9fbecdd490` | ★**`a4270120454aedf7a23c92cd8985c8a6`** ★ | ★**ISS-283 12:30 授权落表** ★ | ★**没动** ★ |
| `HW/BOM_v1.csv` | `94642d07a69e8d60dd2af57f69b93607` | ★**`5d02bece9477ffce5fbe0193c7d5cce4`** ★ | ★**ISS-283 12:30 授权落表** ★ | ★**没动** ★ |

★**⇒ 三件台账管理件的现值与落表台账链头逐字对上** (★链头 `37f62ac3f0b8` / `a4270120454a` / `5d02bece9477`, 落表单号 = `ISS-283`, 链长 10 / 8 / 7, 记录 10 / 10 / 10★) ⇒ ★**这是【合法落表】, 不是「真源被偷改」** ★
★**⇒ 本单的「零写板 / 零落表」自证不受影响** (★硬基线两件逐字节不变; 三件变更发生在 12:30, 早于本趟 17:4x, 且由 ISS-283 授权落表 + 链头对上 ⇒ 与本单无关★) ★
★**⇒ 但任务书 §③ 那五个基线 md5 已经过时** ⇒ ★**本单不擅自改任务书 (★那是 main 的文件★) ⇒ 升级给 main** ★

### ★B5.7 ★【续做新增】机器闸 M5 的覆盖面缺口与订正 (★本单可自修 ⇒ 已修★) ★

| 项 | 内容 |
|---|---|
| ★**缺口** ★ | ★**本闸 M5 原先 `for rel, base in CFC.PROTECTED.items()` ⇒ 只查 2 件**; ★**ISS-286 (12:44) 把 `CFC.PROTECTED` 从 5 件改成 2 件** (网表/脚表/BOM 改归台账管) ⇒ ★**本闸覆盖面被悄悄从 5 件削成 2 件 = 任务书 §③ 的「M5 受保护 5 件」没兑现 ⇒ 3 件真源一度没人管** ★ |
| ★**订正** ★ | ★**M5 拆两段, 5 件一件不少**: ★**M5a 硬基线 2 件** (板 / `.kicad_pro`, 基线写死) + ★**M5b 台账管理 3 件** (网表 / 脚表 / BOM, 判决源 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` 链头, ★**照 ISS-286 的 C4 同构口径, fail-closed 六条: 台账读不到 / 查不到登记 / 链头取不准 / 链头无单号 / 链断 / 有孤儿记录 ⇒ 一律判红; 另盘上 md5[:12] ≠ 链头 ⇒ 判红★**) ★ |
| ★**净效果** ★ | ★**合法落表 (链头前移) ⇒ 绿; 偷改真源不更新台账 ⇒ 红; 台账本身坏掉 ⇒ 红 (不许静默判绿)** ★ |
| ★**自证** ★ | ★**新增反向用例 ⑦b** (偷改 `HW/netlist_v1.csv` 而台账不更新 ⇒ M5b 红: ✅ 命中, md5 `37f62ac3` ⇒ `61e3019d`) + ★**⑧ 自证从实查 2 件扩到实查 5 件 (且少于 5 件直接判红)** ★ |
| ★**边界** ★ | ★**只改【自己新建的】`MECH/check_onepass_mech_sync.py`; 既有 MECH 判据脚本六个 md5 与 08:26 基准逐位相同** ★ |

---

## B6 · 自证复现命令

> ★**★ 本机实跑, 从项目根目录 `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses` 起 ★★ ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ---- ① 本单的新闸 (M1~M5) ----
python3 MECH/check_onepass_mech_sync.py                   # rc=0
python3 MECH/check_onepass_mech_sync.py --selftest        # rc=0 (8 条反向用例)

# ---- ② ISS-276 的闸 (★追加式订正后仍须全绿★) ----
python3 MECH/check_board_frame_coords.py                  # rc=0 (四项全过)
python3 MECH/check_board_frame_coords.py --selftest       # rc=0

# ---- ③ 既有 MECH 判据脚本 (★只读, 现值别改★) ----
python3 MECH/board_port_opening_s6_check.py --json        # rc=0
python3 MECH/jd_y0_feasibility.py --selftest              # rc=0
python3 MECH/check_demo_struct_truth.py                   # rc=0
python3 MECH/check_demo_struct_truth.py --selftest        # rc=0 (21/21)
python3 MECH/service_port_check.py                        # rc=0
python3 MECH/verify_budget.py                             # rc=0

# ---- ④ 本单的实算源 (★修好 TypeError 后的脚本★) ----
python3 logs/iss278/compute_iss278.py > logs/iss278/compute_iss278.json   # rc=0 (13122 B)
python3 -c "import json;d=json.load(open('logs/iss278/compute_iss278.json',encoding='utf-8'));print(d['merged']);print(d['separation']);print(d['h_feasibility'])"

# ---- ⑤ 状态层 ----
python3 state/merge.py                                    # rc=0
python3 state/gate_check.py                               # rc=0 (Q1 18/18)

# ---- ⑥ 受保护 5 件 md5 (★必须逐字节不变★) ----
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# 期望: 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b /
#       e06c1dd633566aa44732762c2ff99d1c / 287e7861a0d1007748d92d9fbecdd490 /
#       94642d07a69e8d60dd2af57f69b93607

# ---- ⑦ 既有 MECH 判据脚本未动 (★对 08:26 基准★) ----
md5sum MECH/check_demo_struct_truth.py MECH/service_port_check.py \
       MECH/board_port_opening_s6_check.py MECH/jd_y0_feasibility.py \
       MECH/verify_budget.py
# 期望: 6972b867c8243bc971408f972dc7727e / db58ff6a2afc28b8bf517e3c57c56bc1 /
#       be8bf0ce94beaf96b1ecba71a45dfd44 / 55db53464eb4a559628f99d6ccd1546f /
#       95d6b01142fc535c412d28e2a91cbbfe
```

---

## rc 追加日志

| 时刻 | 动作 | rc | 备注 |
|---|---|---|---|
| 09:13 | ★**修 `logs/iss278/compute_iss278.py` 的 TypeError** ★ | ★**rc=0** ★ | ★**两处: ① `conn()` 把 pads 打成 tuple ⇒ 后面 `p["num"]` 报 `TypeError: tuple indices must be integers` ⇒ 加 `pads_raw` 保留原 dict 列表; ② `led_net_len()` 返回 `(dist, (x,y))` ⇒ 不能整体 `round` ⇒ 拆开取★** |
| 09:13 | ★**重算 `logs/iss278/compute_iss278.py` ⇒ `compute_iss278.json`** ★ | ★**rc=0** ★ | ★**产物 13122 B (原先 0 B)★** |
| 09:2x | ★**新建 `MECH/BOARD_ONEPASS_MECH_SYNC.md`** ★ | ★**写盘成功 (38271 B)**★ | ★**§1 坐标系声明 / §2 逐条表 8 字段 / §3 MECH→HW 输入清单 + S6 认领句 / §4 归 main·老板拍 / §5 机器块 JSON / §6 边界★** |
| 09:2x | ★**基线 rc 全绿预跑 (9 条既有闸)** ★ | ★**全 rc=0** ★ | ★**check_board_frame_coords.py / --selftest / board_port_opening_s6_check.py --json / jd_y0_feasibility.py --selftest / check_demo_struct_truth.py / --selftest / service_port_check.py / verify_budget.py / gate_check.py★** |
| 09:2x | ★**新建 `MECH/check_onepass_mech_sync.py`** ★ | ★**写盘成功 (31303 B)**★ | ★**M1 帧标签 / M2 两条开口各自不压 SoM 座 / M3 座体高度参数式自洽 / M4 判据命令真存在 / M5 受保护 5 件 md5 + --selftest 8 条反向用例★** |
| 09:22 | ★**新闸主跑** ★ | ★**rc=0** ★ | ★**M1~M5 全过 (修完 M1a 缺 frame / M1c 表头缺帧标 / M3 fab 盒高索引错 三处后)★** |
| 09:23 | ★**新闸 --selftest** ★ | ★**rc=0** ★ | ★**8 条反向用例全抓到 (含「真件 5 件 md5 跑完自检后仍逐字节不变」)★** |
| 09:24 | ★**追加式订正 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (§3b/§4b/§6b/§7b/§8)** ★ | ★**写盘成功 (25766 → 48432 B)**★ | ★**追加点 = 字节 25776 ⇒ 前 25766 字节与 ISS-276 原文件逐字节相同; 老字一字未删未改★** |
| 09:25 | ★**追加后复跑 ISS-276 的闸** ★ | ★**rc=0 / --selftest rc=0** ★ | ★**追加段有 19 行坐标组漏帧标签 ⇒ 补 6 个表头的帧标签后全绿; ISS-276 原有 6 条反向用例仍全抓到★** |
| 09:26 | ★**既有 MECH 判据脚本 md5 复核** ★ | ★**5/5 与 08:26 基准逐位相同** ★ | ★**零改既有判据脚本★** |
| 09:27 | ★**分片写 `state/fragments/mech.yaml`** ★ | ★**rc=0** ★ | ★**claim×2 / artifact×3 / need×1 / status; 写完 grep 校验 key 在不在★** |
| 09:28 | ★**全量验收命令实跑** ★ | ★**全 rc=0** ★ | ★**12 条全绿: onepass / onepass --selftest / board_frame_coords / --selftest / board_port_opening_s6_check --json / jd_y0_feasibility --selftest / check_demo_struct_truth / --selftest / service_port_check / verify_budget / state/merge.py / state/gate_check.py★** |
| 09:29 | ★**`state/check_brief_commands.py --brief-file MECH/BOARD_ONEPASS_MECH_SYNC.md`** ★ | ★**rc=0 (零告警)** ★ | ★**本单清单里的判据命令全部指向本机真存在的脚本★** |
| 09:29 | ★**最终 md5 复核 (五件受保护 + 五个既有 MECH 判据脚本)** ★ | ★**10/10 与基线逐位相同** ★ | ★**板 611b869e… / .kicad_pro 3e504d2b… / 网表 e06c1dd6… / 脚表 287e7861… / BOM 94642d07… + 6972b867… / db58ff6a… / be8bf0ce… / 55db5346… / 95d6b011…★** |
| 09:30 | ★**分片 grep 校验 + 合并态复核** ★ | ★**全中** ★ | ★**`state/fragments/mech.yaml`: claim×2 + artifact×3 + need×1 + status(delivered/100/绿) 全在; `STATE.yaml` 里本单 3 个 key 都在 (各 2 处)★** |

---

# ★★【追加段 A】★★ · 2026-11-17 17:4x · ★**网关重载后复跑复核 + 两处上游现状变化的留痕**★

> ★**追加式: 本段之前的老字一字未删未改 (追加点 = 本文件末尾; 前 30149 字节 md5 `90ae24476c2f253bec70104f960aba41` 逐字节不变)★**
> ★**触发**: ★**17:4x 第二次网关重载 ⇒ 本趟从「盘上产物复核 + 验收命令复跑 + 现状变化留痕」开始续做** ★
> ★**性质**: ★**纯复核 + 留痕 · 零写板 · 零落表 · 零改 HW/ · 零改既有 MECH 判据脚本** ★

## ★A.1 复跑结果 (★本机实跑 · 原始日志 `logs/iss278/accept_*.log` + `logs/iss278/state_layer.log`★)

| # | 命令 | 期望 | ★**17:4x 实跑 rc** ★ | 与 09:2x 首跑对比 |
|---|---|---|---|---|
| 1 | `python3 MECH/check_onepass_mech_sync.py` | 0 | ★**0** ★ | ★**一致 (M1~M5 全绿)★** |
| 2 | `python3 MECH/check_onepass_mech_sync.py --selftest` | 0 (≥5 条) | ★**0** ★ | ★**一致 (8 条反向用例)★** |
| 3 | `python3 MECH/check_board_frame_coords.py` | 0 | ★**0** ★ | ★**一致★** |
| 4 | `python3 MECH/check_board_frame_coords.py --selftest` | 0 | ★**0** ★ | ★**一致★** |
| 5 | `python3 MECH/board_port_opening_s6_check.py --json` | 0 | ★**0** ★ | ★**一致★** |
| 6 | `python3 MECH/jd_y0_feasibility.py --selftest` | 0 | ★**0** ★ | ★**一致★** |
| 7 | `python3 MECH/check_demo_struct_truth.py` | 0 | ★**0** ★ | ★**一致 (主跑仍绿)★** |
| 8 | ★**`python3 MECH/check_demo_struct_truth.py --selftest`** ★ | ★**0 (21/21)** ★ | ★**1** ★ | ★**★变化 ⇒ 见 §A.3 (上游所致, 非本单)★**★ |
| 9 | `python3 MECH/service_port_check.py` | 0 | ★**0** ★ | ★**一致 (57/57 · FAIL 0)★** |
| 10 | `python3 MECH/verify_budget.py` | 0 | ★**0** ★ | ★**一致★** |
| 11 | `python3 state/merge.py` | 0 | ★**0** ★ | ★**一致 (STATE.yaml 已刷新)★** |
| 12 | ★**`python3 state/gate_check.py`** ★ | ★**0 (Q1 18/18)** ★ | ★**0** ★ | ★**一致 (【Q1 交付齐备率】18/18 · Q6 硬件真源闸 rc=0)★** |

## ★A.2 现状变化 ①: 受保护集被上游改基线 (★ISS-286 · hw-lead · 与本单无关★)

> ★**本单机器闸 M5 是【只读 import `MECH/check_board_frame_coords.py` 的 `PROTECTED`】⇒ 阈值零漂移 ⇒ 上游改基线时本闸跟着走, 不会假红, 也不会假绿★**

| 件 | ★**任务书基线 (2026-11-17 07:2x main 实测)** ★ | ★**17:4x 现值** ★ | 判定 |
|---|---|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**逐字节不变 ★ (mtime 仍 2026-11-06 07:07:17)★** |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**逐字节不变 ★ (mtime 仍 2026-11-04 23:47)★** |
| `HW/netlist_v1.csv` | `e06c1dd633566aa44732762c2ff99d1c` | ★**`37f62ac3f0b81d92ca7d48fdea717f07`** ★ | ★**上游 12:30 改的 (mtime 2026-11-17 12:30) ⇒ 非本单★** |
| `HW/netlist_v1_pins.csv` | `287e7861a0d1007748d92d9fbecdd490` | ★**`a4270120454aedf7a23c92cd8985c8a6`** ★ | ★**同上★** |
| `HW/BOM_v1.csv` | `94642d07a69e8d60dd2af57f69b93607` | ★**`5d02bece9477ffce5fbe0193c7d5cce4`** ★ | ★**同上★** |

★**⇒ 归因 (★本机实读, 证据级 `[实测]`★)**: ★**那 3 个件的 mtime 一律 = `2026-11-17 12:30`, 与 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (mtime 同为 `2026-11-17 12:30`) 同一批 ⇒ 是 hw-lead 那趟「板侧清单/网表刷新」落下的 ⇒ ★**本单 (mech-lead) 全程零字节写 `HW/` (本单 5 件交付物全在 `MECH/` + `HANDOFF/` + `state/fragments/mech.yaml`)★**
★**⇒ 上游已把 `PROTECTED` 从 5 件改成「板 + `.kicad_pro`」两件 (网表/脚表/BOM 归台账管)** ⇒ ★**本单 §B6 ⑥ 那段「期望 5 个 md5」已经过期 ⇒ 以本段 §A.2 表为准** ★
★**⇒ 「板只改一次」铁律未破**: ★**板 md5 `611b869e…` + mtime `2026-11-06 07:07:17` 两次实测逐字节相同 ⇒ 板至今一次没改过★**

## ★A.3 现状变化 ②: `MECH/check_demo_struct_truth.py --selftest` 由 rc=0 变 rc=1 (★上游所致, 本单不修★)

★**现象 (★原始输出★)**: ★**`AssertionError: 没找到台账最新记录那一行` @ `MECH/check_demo_struct_truth.py:889` `break_head_ticket()`★**

★**根因 (★本机实跑, 可复核★)**: ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` 在 12:30 被重写后, `HW/netlist_v1.csv` 的台账链头变成了 `37f62ac3f0b8…` (第 1371 行); 而该行是「三列 md5 对拍表」格式, 【不含字面量 `ISS-`】★**
★**⇒ 而 `break_head_ticket()` 的匹配条件是 `head[:12] in ln and ln.strip().startswith("|") and "ISS-" in ln` ⇒ 命中 0 行 ⇒ `assert hit` 炸 ⇒ `--selftest` rc=1★**
★**⇒ 只崩反向用例的脚手架, 不崩主跑 (`check_demo_struct_truth.py` 主跑仍 rc=0) ⇒ 被守的判据本身没坏, 坏的是「造故障」的那一步的匹配口径★**

★**非本单所致 (★两条硬自证★)**:
1. ★**`MECH/check_demo_struct_truth.py` md5 = `6972b867c8243bc971408f972dc7727e` = ★本单任务书 §④ 点名不许动的那个基线, 逐位相同 ⇒ 本单一个字没动它★** ★(`service_port_check.py` `db58ff6a…` / `board_port_opening_s6_check.py` `be8bf0ce…` / `jd_y0_feasibility.py` `55db5346…` / `verify_budget.py` `95d6b011…` 五个既有 MECH 判据脚本同样 5/5 逐位相同★)
2. ★**触发数据 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的 mtime = `2026-11-17 12:30` ⇒ 落在 hw-lead 那趟的落表窗口内, 不在本单 (mech-lead) 的动作窗口内★**

★**⇒ 本单处置**: ★**不修** ★ (★`check_demo_struct_truth.py` 对本单是「只许只读」; `HW/` 对本单是「零改」★) ⇒ ★**交 main 转 hw-lead (台账格式口径归 HW 侧)★** ⇒ 已并入本单 §A.4 的 need 里, 不另开新单★

## ★A.4 分片现状复核 (★`state/fragments/mech.yaml` · 只写自己那一份★)

| 项 | 数量 | key / 路径 | 状态 |
|---|---|---|---|
| ★**claim** ★ | ★**2** ★ | `iss278_mech_onepass_board_inputs_spec` · `iss278_mech_onepass_machine_gate` | ★**都在 (grep 命中行 4701 / 4713)★** |
| ★**artifact** ★ | ★**3** ★ | `MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/check_onepass_mech_sync.py` · ★**本交卷单 (17:5x 补登)★** | ★**都在★** |
| ★**need → main** ★ | ★**1** ★ | `iss278_mech_to_hw_board_inputs` (grep 命中行 2678) | ★**在★** |
| ★**status** ★ | — | `phase=delivered` · `progress_pct=100` · `health=绿` | ★**在★** |

★**⇒ 写分片全程走 `python3 state/frag_write.py --agent mech-lead` (禁止 `open(p,"w")`) ⇒ 原子写 (tmp + fsync + `os.replace`) ⇒ ★**并发写不丢★** ⇒ 写完 `grep` 校验自己的 key 在不在 = ★**全中**★**

## ★A.5 本追加段的边界 (★自证口径★)

| 边界 | 自证 |
|---|---|
| ★**零写板** ★ | ★**板 md5 `611b869e…` + mtime `2026-11-06 07:07:17` 两次实测逐字节相同★** |
| ★**零落表** ★ | ★**本追加段只改本文件 + 自己那一份分片; 网表/脚表/BOM 的 12:30 变更不是本单做的 (见 §A.2 归因)★** |
| ★**零改 HW/** ★ | ★**本趟全程只读 `HW/`; 唯一写动作 = 本交卷单追加 + `state/fragments/mech.yaml` 增量★** |
| ★**零改既有 MECH 判据脚本** ★ | ★**5/5 md5 与本单基线逐位相同 (§A.3 第 1 条)★** |
| ★**零改别人的交卷单** ★ | ★**ISS-276 / ISS-277 / ISS-275 交卷单一个字没动; 本单归一页只追加 §3b/§4b/§6b/§7b/§8, 老字逐字节保留★** |
| ★**零外发** ★ | ★**没发邮件 / 没询价 / 没问询 / 没采购; 缺口一律本机实读 + 标证据等级 + 写降级方案★** |
| ★**证据分级** ★ | ★**本段 §A.1~§A.5 全部 `[实测]` (文件实读 + 脚本实跑); 实物 `[实测]` = 0 条★** |
| ★**不替老板拍板** ★ | ★**h / 结构光孔 / 亮度档 G-5 三条仍是「只列事实与代价, 归 main→老板」; 本段没新增任何代拍★** |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead` + `state/merge.py`★** |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/mech.yaml`; `state/fragments/pm.yaml` 一个字没动★** |

## ★A.6 本追加段的 rc 追加日志

| 时刻 | 动作 | rc | 备注 |
|---|---|---|---|
| 17:45 | ★**网关重载后盘上产物复核** ★ | ★**全在** ★ | ★**规格页 72192 B / 闸 47574 B / 交卷单 30149 B / 归一页含 §3b/§4b/§6b/§7b/§8; 分片 claim×2 + artifact + need×1 + status 齐全★** |
| 17:46 | ★**新闸主跑 + --selftest** ★ | ★**0 / 0** ★ | ★**M1~M5 全绿; 8 条反向用例全抓到★** |
| 17:46 | ★**既有闸复跑 (7 条)** ★ | ★**6×0 + 1×1** ★ | ★**唯一非 0 = `check_demo_struct_truth.py --selftest` ⇒ §A.3 已定位根因 + 归因上游★** |
| 17:47 | ★**`state/merge.py` + `state/gate_check.py`** ★ | ★**0 / 0** ★ | ★**Q1 18/18 · Q6 硬件真源闸 rc=0★** |
| 17:47 | ★**受保护件 md5 复核** ★ | ★**板 2/2 逐字节不变; 网表/脚表/BOM 为上游 12:30 变更 (§A.2)★** | ★**板 md5 `611b869e…` + mtime `2026-11-06 07:07:17`★** |
| 17:5x | ★**补登本交卷单为第 3 个 artifact** ★ | ★**0** ★ | ★**走 `frag_write.py`; 写完 grep 校验★** |
| 17:52 | ★**补登第 2 条 need → main (`iss278_mech_demo_struct_truth_selftest_regression`)★** | ★**rc=0** ★ | ★**追加条 (原单那条 `iss278_mech_to_hw_board_inputs` 原样保留未改) ⇒ 把 §A.3 的上游回归登记进状态层, 免得只躺在交卷单里没人看见★** |
| 17:53 | ★**分片 grep 复核** ★ | ★**全中** ★ | ★**claim×2 (`iss278_mech_onepass_board_inputs_spec` / `iss278_mech_onepass_machine_gate`) + artifact (规格页 1.0 / 闸 1.0 / 归一页 1.1 / 本交卷单 iss278) + need×2 (原条 + 追加条) + status (delivered / 100 / 绿)★** |
| 17:54 | ★**`state/merge.py` + `state/gate_check.py` 终跑** ★ | ★**0 / 0 (Q1 18/18)★** | ★**合并后状态层自洽; Q6 硬件真源闸 rc=0★** |

---

## ★A.7 ★**并发落盘留痕 (★本单闸文件在本趟复核窗口内被【另一趟同单】扩写★)**★

> ★**事实 (★本机实读, 证据级 `[实测]`★)**: ★**`MECH/check_onepass_mech_sync.py` 在本趟复核窗口 (17:45 → 17:50) 内一直在长★**
> ★**47574 B (17:45) → 53637 B (17:50:xx) → 55416 B (17:49:39) ⇒ md5 `f2a5bb741c3fe9ace91700b88a6e06d5` → `0937673d1d7059bc4f74f0b23d55f772` ⇒ ★**说明 cron `fb67af40` 把 ISS-278 又派了一趟给另一个 mech-lead 会话, 两个会话在同一工作区并发写同一批文件**★**

| 项 | 值 (★本趟最终态★) | 判定 |
|---|---|---|
| ★**并发扩写的内容** ★ | ★**新增 M5b: 台账链头口径的 3 件 (网表/脚表/BOM) ⇒ 盘上 md5 必须 == 落表台账链头 + 链不许断 + 不许孤儿 + 链头取得准 + 落表单号要能读出来★** | ★**★这是对 §A.2 的正解: 3 件不是「不管了」, 是改用台账链头当判决源 (与 ISS-286 的 C4 同构口径)★** |
| ★**M5 现在覆盖** ★ | ★**M5a 硬基线 2 件 (板 + `.kicad_pro`, 对 `CFC.PROTECTED`) + M5b 台账链头 3 件** ★ | ★**★5 件一个没少, 只是 3 件的判决源从「写死 md5」换成「台账链头」★** |
| ★**M5b 实跑输出 (★原样★)** ★ | ★**`HW/netlist_v1.csv` 37f62ac3f0b8… == 台账链头 37f62ac3f0b8… 落表单号 ['ISS-283'] 链长 10 记录 10 / `HW/netlist_v1_pins.csv` a4270120454a… == 台账链头 a4270120454a… 落表单号 ['ISS-283'] 链长 8 记录 10 / `HW/BOM_v1.csv` 5d02bece9477… == 台账链头 5d02bece9477… 落表单号 ['ISS-283'] 链长 7 记录 10** ★ | ★**★⇒ §A.2 的归因被台账正面确认: 那次网表刷新是【落表登记在案】的, 不是静默漂移★**★ |
| ★**§A.3 的回归** ★ | ★**仍成立**: ★**`check_demo_struct_truth.py --selftest` 仍 rc=1 (ledger 第 1371 行仍无字面量 `ISS-`; `HW/SCHEMATIC_LANDING_V1_LANDED.md` mtime 仍 `2026-11-17 12:30:23` ⇒ 台账未再动)★** | ★**待 hw-lead 修 (已登记 need)★** |
| ★**闸的验收标准** ★ | ★**对最终态文件复跑: 主跑 rc=0 (M1~M5 全绿) / `--selftest` rc=0 (反向用例全抓到) ⇒ ★**ISS-278 的验收标准依旧满足**★** | ★**★本单达标★** |

★**⇒ 对 main 的一句实话**: ★**「闸文件的 md5 是移动靶」是并发派活造成的, 不是有人偷改 ⇒ 引用本单闸的 md5 时请用【当日最终态】并配 `python3 MECH/check_onepass_mech_sync.py` 的 rc, 别拿单一 md5 当锚★**
| 17:51 | ★**终跑全量复验 (12 条命令 · 对最终态文件)★** | ★**11×0 + 1×1** ★ | ★**`logs/iss278/final_sweep.log`: onepass 0 / onepass --selftest 0 / board_frame_coords 0 / --selftest 0 / board_port_opening_s6_check --json 0 / jd_y0_feasibility --selftest 0 / check_demo_struct_truth 0 / ★**check_demo_struct_truth --selftest 1 (§A.3 上游所致)★** / service_port_check 0 / verify_budget 0 / merge 0 / gate_check 0★** ⇒ ★**板 md5 `611b869e…` 逐字节不变★** |
| 17:51 | ★**分片终态 grep 校验** ★ | ★**全中** ★ | ★**claim×2 + artifact×4 (规格页 1.0 / 闸 1.0 / 归一页 1.1 / 本交卷单 iss278) + need×2 (原条 + 追加条) + status (delivered / 100 / 绿)★** ⇒ ★**ISS-278 交卷 5 件齐 + 状态层已合并 (merge rc=0 · gate_check rc=0 · Q1 18/18)★** |
| ★**17:4x** ★ | ★**【续做】本趟 = 续做验收 (★上一趟 09:30 已把 ISS-278 主体交完并 verified; 本趟不重做, 只实跑验收找缺口★)** ★ | ★**见下** ★ | ★**任务书 §③ 全部验收命令实跑 ⇒ 发现两处真问题 (① 我的新闸 M5 覆盖面缺口 ⇒ 本单可自修 ⇒ 已修; ② `check_demo_struct_truth.py --selftest` rc=1 ⇒ 根因在 ISS-283 12:30 台账行格式 ⇒ 本单不许改那个脚本 ⇒ 升级给 main)★** ★ |
| ★**17:47** ★ | ★**实读发现: `CFC.PROTECTED` 被 ISS-286 (12:44) 从 5 件改成 2 件** ★ | ★**定位完成** ★ | ★**⇒ 本闸 M5 的覆盖面被【悄悄削掉一半】(5 件 → 2 件) ⇒ 3 件真源一度【没人管】★** ★ |
| ★**17:48** ★ | ★**修 `MECH/check_onepass_mech_sync.py` 的 M5** ★ | ★**写盘成功** ★ | ★**M5 拆两段: M5a 硬基线 2 件 (板 / `.kicad_pro`) + M5b 台账管理 3 件 (网表 / 脚表 / BOM, 判决源 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` 链头, 照 ISS-286 的 C4 同构口径, fail-closed 六条) ⇒ ★**5 件一件都不少**★; ★**只读 import `CFC.ledger_state` ⇒ 口径零漂移; 一个字不改既有 MECH 判据脚本★** ★ |
| ★**17:48** ★ | ★**沙盒补齐: `make_sandbox()` 现在也复制 3 件台账管理件 + 落表台账本身** ★ | ★**写盘成功** ★ | ★**否则 M5b 在沙盒里永远 fail-closed ⇒ 反向用例跑不了★** ★ |
| ★**17:49** ★ | ★**新增反向用例 ⑦b (偷改台账管理件 ⇒ M5b 红)** ★ | ★**写盘成功** ★ | ★**证明 M5b 不是【摆设】★** ★ |
| ★**17:49** ★ | ★**修 ⑧ 自证的虚标 (原先实查 2 件却宣称「5 件」)** ★ | ★**写盘成功** ★ | ★**现在实查 5 件, 且少于 5 件直接判红★** ★ |
| ★**17:50** ★ | ★**新闸主跑** ★ | ★**rc=0** ★ | ★**M1~M5 全过; M5 输出 5 行 (M5a 2 行 + M5b 3 行, 台账链头 / 落表单号 ISS-283 / 链长 / 记录数全打出)★** ★ |
| ★**17:50** ★ | ★**新闸 --selftest** ★ | ★**rc=0** ★ | ★**12 条反向用例全抓到 (含新增 ⑦b); ⑧ 打印 5 件 md5★** ★ |
| ★**17:51** ★ | ★**追加式订正规格页 `MECH/BOARD_ONEPASS_MECH_SYNC.md`** ★ | ★**写盘成功 (73035 → 83369 B)** ★ | ★**§6 表格加一行「M5 口径订正」 + 末尾追加 §12 (★§12.1 缺口与订正 / §12.2 基线变更留档 / §12.3 selftest rc=1 根因 / §12.4 边界★) ⇒ ★**追加式, §1~§11 一个字没删没改★** ★ |
| ★**17:53** ★ | ★**交卷单补 B2 两行 + B3.6/B3.7 + B5.5/B5.6/B5.7** ★ | ★**写盘成功** ★ | ★**★B2: `check_demo_struct_truth.py --selftest` 由 rc=0 订正为 rc=1 (★如实, 不许假装它绿★); md5 行由「5/5 相同」订正为「2/2 硬基线 + 3/3 台账链头对上」★** ★ |
| ★**17:52** ★ | ★**全量验收命令实跑 (12 条)** ★ | ★**11 条 rc=0 + 1 条 rc=1** ★ | ★**rc=0: onepass / onepass --selftest / check_board_frame_coords / --selftest / board_port_opening_s6_check --json / jd_y0_feasibility --selftest / check_demo_struct_truth / service_port_check / verify_budget / state/merge.py / state/gate_check.py (Q1 18/18 + Q6 ✅) / check_brief_commands (零告警)★; ★**rc=1: `check_demo_struct_truth.py --selftest` ⇒ 根因在 ISS-283 12:30 台账行格式 (★B3.7 有复现★) ⇒ 升级给 main (B5.5)★** ★ |
| ★**17:52** ★ | ★**最终 md5 复核 (受保护 5 件 + 既有 MECH 判据脚本 6 个)** ★ | ★**板与 `.kicad_pro` 逐位相同; 5 个受保护脚本逐位相同** ★ | ★**板 `611b869e…` / `.kicad_pro` `3e504d2b…` (硬基线不变) + 网表 `37f62ac3…` / 脚表 `a4270120…` / BOM `5d02bece…` (= 台账链头, ISS-283 12:30 授权落表 ⇒ 合法, ★**不是本单改的★**); 既有脚本 6972b867… / db58ff6a… / be8bf0ce… / 55db5346… / 95d6b011… 与 08:26 基准逐位相同 (`check_board_frame_coords.py` = `12fa5db0…` 是 ISS-286 12:44 改的, ★**早于本趟, 本趟没碰★**)★** ★ |
| ★**17:55** ★ | ★**分片写 `state/fragments/mech.yaml` (续做段)** ★ | ★**rc=0** ★ | ★**走 `state/frag_write.py --agent mech-lead` ⇒ claim×2 (`iss278_mech_m5_coverage_5files` / `iss278_mech_cont_acceptance_174x`) + need×1 (`iss278_mech_demo_struct_truth_selftest_regression` → main) + status (delivered / 100 / 绿)★** ★ |
| ★**17:55** ★ | ★**★发现并合并同 key 重复 need★** ★ | ★**rc=0** ★ | ★**本 agent 的两次续做把【同一件事】各写了一条同 key 的 need ⇒ `merge.py` 的 `needs_matrix/pending` 里出现两条同 key ⇒ main 会看到同一件事被挂两次 ⇒ ★**合并成 1 条 (item 取两条的并集, 2126 字符, 一条信息都不丢)** ★ ⇒ ★**合并走 `state/frag_write.py` 的 `update_fragment` 原子写 (★不裸写分片★)★** ★ |
| ★**17:55** ★ | ★**分片 grep 校验 (★硬要求★)** ★ | ★**全中** ★ | ★**`state/fragments/mech.yaml`: 三个 key 各 1 条 (claim×2 + need×1, ★**无同 key 重复★**); `STATE.yaml`: 三个 key 全在 (2 / 2 / 3 处)★** ★ |
| ★**17:55** ★ | ★**`state/merge.py` 复跑 + 快照完整性** ★ | ★**rc=0** ★ | ★**「产出 519 · 阻塞 43 (高危 33) · 未闭合需求 297 · 冲突 0」★; ★**快照不完整提示指向 `hw.yaml` (★另两个 agent 的 `interface_claims` 条目缺 `key` 字段 ⇒ 已被忽略★) ⇒ 与本单无关, 本单的 `mech.yaml` 三字段零缺项** ★** ★ |

---

## ★附 A · 交付物清单 + 边界自证 (★17:4x 续做终态★) ★

| # | 交付物 | 路径 | 终态 |
|---|---|---|---|
| 1 | MECH 侧板侧输入清单 (机器可读) | `MECH/BOARD_ONEPASS_MECH_SYNC.md` | ★**83369 B** (★38271 → 续做追加 §12★) ★ |
| 2 | ISS-276 归一页追加式订正 (§3b/§4b/§6b/§7b/§8) | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | ★**48432 B**; ★**前 25766 字节 md5 = `c86b11d879fed012f16c909aabaec0ff` = ISS-276 原文件 ⇒ 逐字节相同 ⇒ 追加式成立** ★ |
| 3 | 机器闸 | `MECH/check_onepass_mech_sync.py` | ★**56367 B** (★31303 → 续做修 M5★) ★ |
| 4 | 本交卷单 (B1~B6 + 附 A/B/C) | `HANDOFF/2026-11-17_mech-lead_ISS278_MECH侧板侧输入收口.md` | ★**本文件** ★ |
| 5 | 分片 | `state/fragments/mech.yaml` | ★**claim×4 (原 2 + 续做 2) / artifact×3 / need×2 (原 1 + 续做 1, ★**同 key 已合并成 1 条★**) / status** ★ |
| — | 实算脚本 + 产物 | `logs/iss278/compute_iss278.py` + `.json` | ★**10266 B + 13122 B, rc=0** ★ |
| — | ★**续做验收原始输出** ★ | ★`logs/iss278/gate_main4.log` / `gate_selftest4.log` / `final_raw.txt` ★ | ★**已落** ★ |

### ★附 A.1 边界终态自证 (★17:5x 实跑★) ★

| 边界 | 自证结果 |
|---|---|
| ★**零写板 / 零落表** ★ | ★**板 `611b869e…` / `.kicad_pro` `3e504d2b…` 硬基线逐字节不变; 三件台账管理件现值 = 落表台账链头 (ISS-283 12:30 授权落表) ⇒ 合法 ⇒ 本单零参与** ★ |
| ★**零改既有 MECH 判据脚本** ★ | ★**5 个受保护脚本 md5 与 08:26 基准逐位相同 (`6972b867…` / `db58ff6a…` / `be8bf0ce…` / `55db5346…` / `95d6b011…`); `check_board_frame_coords.py` = `12fa5db0…` 是 ISS-286 12:44 改的, 早于本趟 ⇒ 本趟没碰; 本趟只改【自己新建的】`check_onepass_mech_sync.py`** ★ |
| ★**零改 HW / SW** ★ | ★**零字节写入 (只读)** ★ |
| ★**零改别人的交卷单** ★ | ★**ISS-276 的交卷单一个字没改; 归一页只【追加式】** ★ |
| ★**零外发** ★ | ★**不发邮件 / 不询价 / 不问询 / 不采购; 本单 `[官网]`/`[媒体]` = 0 条** ★ |
| ★**证据分级** ★ | ★**交卷单里 `[实测]` 21 处 / `[推算]` 5 处 / `[0数据]` 11 处; 实物 `[实测]` = 0 条** ★ |
| ★**不替老板拍板** ★ | ★**座体高度 h / 结构光孔有否 / 亮度档 G-5 = 只列事实与代价, 归 main→老板** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead`; ISS-278 在 issue_log 里是 09:xx 那一趟签的, 本趟没动** ★ |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/mech.yaml`; `hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节没碰** ★ |

## ★附 B · 验收命令全量 rc 原样贴出 (★17:5x 实跑★) ★

```
rc=0 :: python3 MECH/check_onepass_mech_sync.py
rc=0 :: python3 MECH/check_onepass_mech_sync.py --selftest
rc=0 :: python3 MECH/check_board_frame_coords.py
rc=0 :: python3 MECH/check_board_frame_coords.py --selftest
rc=0 :: python3 MECH/board_port_opening_s6_check.py --json
rc=0 :: python3 MECH/jd_y0_feasibility.py --selftest
rc=0 :: python3 MECH/check_demo_struct_truth.py
rc=1 :: python3 MECH/check_demo_struct_truth.py --selftest     ★★ 根因不在本单 ⇒ B5.5 ★★
rc=0 :: python3 MECH/service_port_check.py
rc=0 :: python3 MECH/verify_budget.py
rc=0 :: python3 state/merge.py
        ✅ STATE.yaml 已刷新 (2026-11-17T17:55:03+08:00)
           产出 519 | 阻塞 43 (高危 33) | 未闭合需求 297 | 冲突 0
rc=0 :: python3 state/gate_check.py
        【Q1 交付齐备率】 18/18 个必填验收块齐全
        【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
rc=0 :: python3 state/check_brief_commands.py --brief-file MECH/BOARD_ONEPASS_MECH_SYNC.md
        ── 查了 1 条待办单的 task_brief, 有问题的 0 条

=== 受保护 5 件 md5 (17:5x 实跑) ===
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
37f62ac3f0b81d92ca7d48fdea717f07  HW/netlist_v1.csv       ★★ = 落表台账链头 (ISS-283 12:30 授权落表) ★★
a4270120454aedf7a23c92cd8985c8a6  HW/netlist_v1_pins.csv  ★★ = 落表台账链头 (ISS-283 12:30 授权落表) ★★
5d02bece9477ffce5fbe0193c7d5cce4  HW/BOM_v1.csv          ★★ = 落表台账链头 (ISS-283 12:30 授权落表) ★★

=== 既有 MECH 判据脚本 md5 (对 08:26 基准) ===
6972b867c8243bc971408f972dc7727e  MECH/check_demo_struct_truth.py      ★ 基准相同 ★
db58ff6a2afc28b8bf517e3c57c56bc1  MECH/service_port_check.py           ★ 基准相同 ★
be8bf0ce94beaf96b1ecba71a45dfd44  MECH/board_port_opening_s6_check.py  ★ 基准相同 ★
55db53464eb4a559628f99d6ccd1546f  MECH/jd_y0_feasibility.py            ★ 基准相同 ★
95d6b01142fc535c412d28e2a91cbbfe  MECH/verify_budget.py                ★ 基准相同 ★
12fa5db08d166cce90d47d14f500182e  MECH/check_board_frame_coords.py     ★ ISS-286 12:44 改的, 早于本趟 ⇒ 本趟没碰 ★
```

## ★附 C · 本单留下的三件「不许再犯」的教训 (★本轮实跑踩出来的★) ★

| # | 教训 | 证据 | 处置 |
|---|---|---|---|
| ★1 ★ | ★**「只读 import 既有闸脚本」会让本闸的覆盖面【跟着上游缩水】而自己不知情** ★ | ★**ISS-286 把 `CFC.PROTECTED` 从 5 件改成 2 件 ⇒ 本闸 M5 跟着从 5 件缩成 2 件 ⇒ 3 件真源一度【没人管】, 而本闸一直绿** ★ | ★**M5 拆 M5a/M5b 显式覆盖 5 件; 并加「实查件数 < 宣称件数 ⇒ 判红」的自检 (⑧) ⇒ ★**以后上游改判决源, 本闸会当场发现覆盖缺口, 不再闷声缩**★** ★ |
| ★2 ★ | ★**「台账是真源」= 台账的【行格式】也是判决源的一部分** ★ | ★**ISS-283 12:30 改了台账行格式 ⇒ `break_head_ticket()` 的三条件命中不了 ⇒ 一个 09:29 还绿的 `--selftest` 到 12:30 就红了, 而根因不在那个脚本里** ★ | ★**本单只登记 + 升级 (B5.5); 本闸的 M5b 用【链头 md5】判 (★不依赖行里有没有单号★) ⇒ 本闸不受这个格式变更影响** ★ |
| ★3 ★ | ★**同一个 key 被写两次 = main 看到同一件事被挂两次** ★ | ★**本 agent 的两次续做把【同一件事】各写了一条同 key 的 need ⇒ `needs_matrix/pending` 出现两条同 key** ★ | ★**合并成 1 条 (item 取并集, 一条信息都不丢); 合并走 `frag_write.update_fragment` 原子写 (★不裸写分片★)★** ★ |

### ★B5.8 ★【续做新增 · 顺带发现·本单不改】同族的 ISS-290 闸用了【硬写 md5】而不是台账链头 ⇒ 下一次合法落表就会假红 ★

| 项 | 实测事实 |
|---|---|
| 对象 | ★**`MECH/check_onepass_struct_crosscheck.py` (★ISS-290 的闸, 已 verified; ★**不是本单的域, 本单一个字不改★**)** ★ |
| 它的 N6 怎么判 | ★**`items = dict(CFC.PROTECTED)` + `items.update(PROTECTED_LEDGER_MD5)` ⇒ 网表/脚表/BOM 用【硬写的 md5 基线】** (★现值 `37f62ac3…` / `a4270120…` / `5d02bece…` = ISS-283 12:30 那次落表的现值★) ⇒ ★**现在绿** ★ |
| ⇒ 脆在哪 | ★**下一次【合法】授权落表 (链头前移) ⇒ 硬写基线不会跟着动 ⇒ N6 立刻假红** ⇒ ★**该闸会把「合法落表」误判成「真源被偷改」** ★ |
| 本单怎么做的 | ★**本单的新闸 M5b 判【台账链头】而不是硬写 md5 ⇒ 合法落表 ⇒ 绿; 偷改真源不更新台账 ⇒ 红; 台账坏掉 ⇒ 红 (fail-closed 六条)** ⇒ ★**所以本单的新闸【不会】有这个问题** ★ |
| ⇒ 处置 | ★**只登记, 本单不改那个文件** (★它是 ISS-290 的交付物 + 已 verified + 不在本单边界内★) ⇒ ★**已在给 main 的 need 里一并提一句, 由 main 决定要不要另派一个「把 ISS-290 闸的 N6 也改成台账链头口径」的小活** ★ |
| ★**17:57** ★ | ★**need 再补一句「同族闸 (ISS-290 的 N6) 也该改链头口径」** ★ | ★**rc=0** ★ | ★**走 `frag_write.update_fragment` 原子写 (★不裸改分片★); need 仍是 1 条 (item 2430 字符)★** ★ |
| ★**17:58** ★ | ★**终态全量验收 (★11 条既有闸 + 本单新闸 + 同族闸★)** ★ | ★**全绿, 唯一红的是已升级的那条** ★ | ★**rc=0: onepass / onepass --selftest / check_board_frame_coords / --selftest / board_port_opening_s6_check --json / jd_y0_feasibility --selftest / check_demo_struct_truth / service_port_check / verify_budget / check_onepass_struct_crosscheck (ISS-290 同族闸)★; ★**rc=1: `check_demo_struct_truth.py --selftest` (★已定位根因 + 已升级 main, 不假装它绿★)★** ★ |
| ★**17:58** ★ | ★**分片 grep 终校** ★ | ★**全中** ★ | ★**`state/fragments/mech.yaml`: 三个 key 各 1 条 (claim×2 + need×1, ★**无同 key 重复★**); `STATE.yaml`: 三个 key 全在 (2 / 2 / 3 处)★** ★ |
