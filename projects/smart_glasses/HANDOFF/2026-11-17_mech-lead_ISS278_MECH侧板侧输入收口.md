# ISS-278 · mech-lead 交卷单 · MECH 侧板侧输入收口 + 机器闸

> **单**: ISS-278 (owner=mech-lead · 派活 2026-11-17 07:3x · cron `fb67af40`)
> **性质**: ★**内部活 · MECH 侧 · 纯分析 + 规格页订正 + 机器闸类 · 零写板 · 零落表 · 零改既有 MECH 判据脚本** ★
> **续做**: ★**上一趟 (子会话 08:05:44→08:52:52 · status=timeout) 被网关重载整段截断 ⇒ 盘上零产物; 本趟从【修 TypeError】开始续做, 落一件写一件** ★
> **一句话交付**: ★**把「板只改一次」那一趟要用的 MECH 侧输入收成【一份规格 + 一道闸】: 检修口/调试口拆成两条独立规格 · 座体高度参数化 + 三档假设 · LED 光孔两假设 + 降级 · 连接器参数对照表** ★

---

## 交付物清单

| # | 交付物 | 路径 | 状态 |
|---|---|---|---|
| 1 | MECH 侧板侧输入清单 (机器可读) | `MECH/BOARD_ONEPASS_MECH_SYNC.md` | ★**已落 (38271 B)**★ |
| 2 | ISS-276 归一页追加式订正 (§3b/§4b/§6b/§7b/§8) | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | ★**已落 (25766 → 48432 B, 追加式)**★ |
| 3 | 机器闸 | `MECH/check_onepass_mech_sync.py` | ★**已落 (31303 B)**★ |
| 4 | 本交卷单 (B1~B6) | `HANDOFF/2026-11-17_mech-lead_ISS278_MECH侧板侧输入收口.md` | ★**已落**★ |
| 5 | 分片 (claim×2 / artifact×3 / need×1 / status) | `state/fragments/mech.yaml` | ★**已落**★ |
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
| ★`python3 MECH/check_demo_struct_truth.py --selftest` ★ | rc=0 (★21/21, 只许只读★) | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 MECH/service_port_check.py` ★ | rc=0 | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 MECH/verify_budget.py` ★ | rc=0 | ★**rc=0** ★ | ★**✅ 现值未动** ★ |
| ★`python3 state/merge.py` ★ | rc=0 | ★**rc=0** ★ | ★**✅ 「STATE.yaml 已刷新 (2026-11-17T09:27:34+08:00) · 产出 486 | 阻塞 43 (高危 33) | 未闭合需求 269 | 冲突 0」★** |
| ★`python3 state/gate_check.py` ★ | rc=0 (Q1 18/18) | ★**rc=0** ★ | ★**✅ 「【Q1 交付齐备率】 18/18 个必填验收块齐全」+ Q6 硬件真源闸 ✅ 通过 (rc=0)★** |
| ★`python3 state/check_brief_commands.py --brief-file MECH/BOARD_ONEPASS_MECH_SYNC.md` ★ | rc=0 (★本单清单里的判据命令不许指向不存在的脚本★) | ★**rc=0** ★ | ★**✅ 零告警★** |
| ★`md5sum` 五件受保护 ★ | 逐字节不变 | ★**5/5 相同** ★ | ★**✅ 板 611b869e… / `.kicad_pro` 3e504d2b… / 网表 e06c1dd6… / 脚表 287e7861… / BOM 94642d07…** ★ |

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
