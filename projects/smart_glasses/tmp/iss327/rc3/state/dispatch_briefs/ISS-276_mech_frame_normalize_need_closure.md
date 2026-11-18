# ISS-276 · mech-lead 任务书 —— ★★「板只改一次」那一趟的 MECH 侧【坐标系归一 + 两条待答 need】★ (★纯分析 + 规格页订正类 · 零写板★)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 06:1x · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
>
> ★**本单性质**: ★**内部活 · MECH 侧 · 纯分析 + 规格页订正类** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零改既有 MECH 判据脚本** ★ ⇒ ★**不是老板级拍板** ★
>
> ★**为什么这一单现在必须做 (★main 本机实读, 不抄任何交卷报告★)**: ★**2026-11-17 05:2x~05:4x, 你自己交的两件活 (ISS-271 / ISS-267) 把 MECH 侧的三个口径算出来了, 但它们用的坐标系是【60×30 套A 坐标】★ ⇒ ★**而现役板是 160×100 台架板 ⇒ 两者的 X/Y 数值含义完全不同 ⇒ 「逐字抄进 §3-S6」会把开口坐标写到 SoM 座上** ★ ⇒ ★**本单 = 把 MECH 侧那两个窗口/矩形【归一到现役板坐标系】, 并把 ISS-273 留给 main 的两条待答 need 收掉** ★

---

## ① 病灶 (★main 本机实读, 行号可复核★)

### ★1.1 你交的两个窗口, 坐标系是 60×30 套A (★本机实测把它们搬到现役板上会撞谁★)

★**现役板实测**: Edge.Cuts = **160.10 × 100.10 mm** · 铜层 **8** · 封装 **186** · `HW/PCB/demo_mainboard_params.json` 板段 = `160.0 / 100.0 / 8 层 / 1.6mm`

| ISS-271 给的 (60×30 套A 口径) | 搬到现役 160×100 板 ⇒ 压住谁 (★main 06:1x 读板实测★) |
|---|---|
| `D_LED_G` 首选窗口 **X 33.00..47.71 × Y 1.60..28.40** | ★**`J_SOM_P3` 的 10 个 DSI 焊盘** (x 34.4/34.8, y 7.96/11.04) ★ |
| 检修口/调试口开口 **X 47.00..60.00 × Y 1.665..11.730** | ★**`J_SOM_P1` 的 56 个焊盘** (x 47.65..70.35, y 7.61..11.39) ★ |

⇒ ★**⇒ 这两个数在 60×30 板上是对的, 在现役 160×100 板上是错的** ★ ⇒ ★**⇒ ISS-271 交卷单 §B5 第 ① 条「§5.1 那一句逐字抄进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6 就行」★ ⇒ ★**照字面执行 = 那一趟开工即撞 SoM 座** ★

★**现役板 SoM 承载区实测** (★4 个 `J_SOM_P1..P4` 焊盘包络并集★): **X 13.65..70.35 (56.70mm) × Y 7.61..54.39 (46.78mm)**
⇒ ★**46.78 > 30 且 > 15 ⇒ 现役 SoM 承载区【物理上装不进】60×30 / 60×15** ★ ⇒ ★**⇒ 「60×30 套A」与「现役 demo 板」是两种物理产品 (SoC 直上板 vs SoM 承载区), 坐标不可互相代入** ★

### ★1.2 现役板上的实际位置 (★你归一化时的输入★)

★**main 06:1x 读板实测**:
| 位号 | 现役板坐标 | 焊盘/网 |
|---|---|---|
| `J_DEBUG` | **(144.30, 58.00)** | 4 焊盘 · `JTAG_TCK/TMS/TDI/TDO` |
| `J_UART` | **(20.74, 70.00)** | 2 焊盘 · `UART_RX/UART_TX` |
| `D_LED_G` | **(101.25, 56.80)** | 2 焊盘 · `GND` / `LED_G_D` |
| `R_LED_G` | **(5.90, 62.50)** | 2 焊盘 · `LED_G` / `LED_G_D` |
| `R_LED_R` | **(84.90, 21.50)** | 2 焊盘 · `LED_R` / `LED_R_D` |

★**⇒ 两个直接冲突 (本机实读)**: ★**① `J_DEBUG` 与 `J_UART` 相距 123.6mm, 而 MECH 模型让它们紧邻 ⇒ 你 §4 说的「开口 X 49.21..59.41 在盘上板不成立」实测成立** ★ ⇒ ★**② `LED_G_D` 走线 93.49mm 的根因: `D_LED_G`(101.25,56.80) 与 `R_LED_G`(5.90,62.50) 分居板子两端** ★ (★你 05:1x 实算 93.492727 对得上★)

### ★1.3 两条你留给 main 的待答 need (★本机实读 `state/fragments/mech.yaml`★)

| key | to | 本机实读状态 |
|---|---|---|
| `iss273_mech_ledger_format_contract` | main | **pending** (★问: 落表台账的格式契约写在哪★) |
| `iss273_mech_ledger_itself_anchor` | main | **pending** (★问: 台账自己要不要再加一层 md5 锚★) |

★**另**: `state/fragments/pm.yaml` 的 `iss273_h1_anchor_single_source` (★**main 自己开的 need, to=mech-lead**★) 实测 **pending / answers=0 / foreign_answers=0** ⇒ ★**⇒ 你的 ISS-273 交卷答案写在了 `iss273_mech_judge_source_change` 这个 key 上, 与 main 开的 key 不配对 ⇒ 需求没闭合** ★ ⇒ ★**⇒ 本单要【用 main 开的那个 key】补一条 answer, 把它闭合** ★

### ★1.4 落表台账格式契约的现值 (★main 本机实读★)

★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.5 / §18.4**: 格式 = **「单号 | 文件 | 旧 md5 | 新 md5 | 变了?」** 四项同行 ⇒ ★**这就是 MECH 侧 `ledger_records()` 靠它抽链的格式 (★实读 `MECH/check_demo_struct_truth.py:325`★)** ⇒ ★**⇒ 契约的现值 = 【这四项同行】; 你的 need 问的是「写进 HW 侧落表作业包模板, 还是写进 MECH 台账说明」** ★

---

## ② 你要交的东西 (★一句话★)

★**把 MECH 侧那两个窗口/矩形【归一到现役 160×100 台架板坐标系】并给出可放行空间, 同时把 ISS-273 留给 main 的两条 need + 那条没配上的 answer 一次收掉** ★

★**交卷物 (6 件)** ★

1. ★**新建** `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` —— ★**「检修口/调试口开口 + `D_LED_G` 位置」的坐标系归一页** ★:
   - §1 ★**坐标系声明 (置顶)**: ★**本文一切坐标 = 现役台架板 160×100 坐标 (Edge.Cuts 实读 160.10 × 100.10) ⇒ 与 `MECH/BOARD_GEOM_30MM.md` 的 60×30 套A 坐标【不是同一套】⇒ 两套数不可互相代入** ★
   - §2 ★**现役板 SoM 承载区实测占位** (★X 13.65..70.35 × Y 7.61..54.39★) + ★**「60×30 套A 与现役板是两种物理产品」的结论** ★
   - §3 ★**检修口/调试口开口**: ★**在现役 160×100 坐标系下的可放行空间** (★**由 `MECH/board_port_opening_s6_check.py` 实算, 不许抄 60×30 的数★**) + ★**与 SoM 座 (J_SOM_P1..P4) 的避让关系** + ★**`J_DEBUG`@144.30,58.00 / `J_UART`@20.74,70.00 相距 123.6mm 这一事实对开口位置的影响**
   - §4 ★**`D_LED_G` 位置**: ★**现役板坐标系下的可放行空间** + ★**实测 `LED_G_D` 走线 93.49mm 的两端坐标 (`D_LED_G`@101.25,56.80 ↔ `R_LED_G`@5.90,62.50) + 根因 (排版器把电阻分到板子另一端)** + ★**只给空间与约束条件, 不定坐标** (★**最终坐标是 PCB 布局的活 = hw-lead★)
   - §5 ★**给 hw-lead 的 S6 认领句 (★现役板坐标版★)** ⇒ ★**明确写: 开口与 LED 窗口的坐标必须与 `HW/PCB/BOARD_FRAME_CALIBER.md` (ISS-274 同批产出) 的帧声明一致, 两边不得各用一套** ★
2. ★**订正** `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` (★**追加式, 老字一字不删★**): ★**加一行帧声明 (★本文坐标 = 60×30 套A 口径; 现役板归一后的数见 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`★) + ★**点名「§B5 第 ① 条『逐字抄进 §3-S6』这句, 对现役板不成立 ⇒ 已改为引用归一页」★**
3. ★**新建** `MECH/check_board_frame_coords.py` —— ★**机器闸** ★:
   - **C1** ★**帧标签**: 本单/工作包里出现的坐标组必须带帧标签 ⇒ **漏标一条即红** ★
   - **C2** ★**归一后窗口不压 SoM 座**: 读板 ⇒ §3/§4 给的开口矩形与 LED 窗口 ⇒ **压住 `J_SOM_P1..P4` 焊盘数必须 = 0** ★ (★**这条就是 ISS-271 那两个矩形在现役板上会撞 SoM 座的机器化留存** ★)
   - **C3** ★**两套坐标不可代入 (负向断言)**: ★**把 60×30 套A 口径的旧矩形喂进现役板坐标 ⇒ 必须报出「压住了 N 个 SoM 焊盘」而不是静默通过** ★
   - **C4** ★**受保护 5 件 md5 前后逐字节不变** (板 / `.kicad_pro` / 网表 / 脚表 / BOM)
   - `--selftest` ★**反向用例 ≥ 5 条** (★每条自证真改到目标★): ★**① 改窗口一个角 ⇒ C2 红 ② 抽帧标签 ⇒ C1 红 ③ 把窗口挪进 SoM 区 ⇒ C2 红 ④ 把旧 60×30 矩形当新坐标喂 ⇒ C3 必须报出压住焊盘数 ⑤ 改受保护件 ⇒ C4 红** ★
4. ★**闭合 ISS-273 留下的三条 (★分片操作★)**: 走 ★**`python3 state/frag_write.py --agent mech-lead`** ★ (★**禁止 `open(p,"w")`** ★):
   - ★**用 main 开的 key `iss273_h1_anchor_single_source` 补一条 answer (★to=main★)** ⇒ ★**把 `state/fragments/pm.yaml` 那条 pending need 闭合** ★ (★**注意: 你写在 mech.yaml, 但 answer 的 key 必须与 main 开的 key 完全一致 ★**)
   - ★**回答 `iss273_mech_ledger_format_contract`** (★to=main★): ★**你从 MECH 侧看到的格式契约现值 = 「单号 + 文件名 + 改前 md5 + 改后 md5」四项同行 (★`HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.5/§18.4 实读★) ⇒ 建议写进【HW 侧落表作业包模板】(★因为台账住在 HW/ 且由 hw-lead 写★), MECH 侧只读** ★
   - ★**回答 `iss273_mech_ledger_itself_anchor`** (★to=main★): ★**你的建议 + 代价** (★**从 MECH 侧判据角度: 台账被改 = 判决源被改 ⇒ 加锚能不能堵住「悄悄换台账」, 加了会不会绕回老循环** ★) ★ ⇒ ★**只给建议与代价, 不代 main 拍** ★
5. ★**交卷单** ★**新建** `HANDOFF/2026-11-17_mech-lead_ISS276_MECH侧坐标系归一与三条need收口.md` —— **B1~B6 六块齐全** (★B1 结论摘要 · B2 验收标准逐条自评 · B3 反向自证贴实跑原始输出 · B4 接口取值声明 · B5 未决项与卡点 · B6 自证复现命令★)
6. ★**分片** ★**新建** —— 走 ★**`python3 state/frag_write.py --agent mech-lead`** ★: 登记 ★**2 条 claim** (★现役板坐标系归一页已立 + 两条 need 已答 + 一条 answer 已配对闭合★) + ★**artifact** ×3 + ★**1 条 need 给 hw-lead** (★「S6 认领句已改成现役板坐标版 ⇒ 请与 `HW/PCB/BOARD_FRAME_CALIBER.md` 对齐后再收进 §3-S6」★) + ★**status** (phase=delivered · progress_pct=100)

---

## ③ 验收命令 (★本机实跑, rc 原样贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/board_port_opening_s6_check.py --json        # rc=0 (★现值, 别改★)
python3 MECH/jd_y0_feasibility.py --selftest              # rc=0 (★别改★)
python3 MECH/check_demo_struct_truth.py                   # rc=0 (23/23 · ★ISS-273 成果, 只许只读★)
python3 MECH/check_demo_struct_truth.py --selftest        # rc=0 (21/21 · ★只许只读★)
python3 MECH/check_board_frame_coords.py                  # rc=0 (★新建★)
python3 MECH/check_board_frame_coords.py --selftest       # rc=0 (★新建★)
python3 state/merge.py                                    # rc=0
python3 state/gate_check.py                               # rc=0 (Q1 18/18)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
python3 -c "…读 state/fragments/pm.yaml 里 iss273_h1_anchor_single_source 的 state ⇒ 必须已 answered…"
```

★**基线 md5 (★2026-11-17 06:1x main 实测★)**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` ⇒ ★**这 5 件必须逐字节不变** ★

★**已知现状 (不必修, 但交卷单要写清)**: ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` 现在 rc=1 (板多 2 个带网焊盘 = F1 落表引起) ⇒ ★**与本单无关, 本单只需保证没让它更糟** ★

---

## ④ 边界 (★逐条自证★)

| 边界 | 怎么自证 |
|---|---|
| ★**零写板 / 零落表** ★ | 板 / `.kicad_pro` / 网表 / 脚表 / BOM 五件 md5 跑前跑后逐字节相同 |
| ★**零改既有 MECH 判据脚本** ★ | ★**`MECH/check_demo_struct_truth.py` (6972b867…) / `MECH/service_port_check.py` / `MECH/board_port_opening_s6_check.py` / `MECH/jd_y0_feasibility.py` 一字不许动** ★ ⇒ ★**你的新闸是【新建】文件, 不许改老脚本** ★ |
| ★**零改 HW 文件** ★ | `HW/` 零字节写入 (★**作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 是 hw-lead 的文件, 本单一个字不许改★**) |
| ★**零改 `MECH/BOARD_GEOM_30MM.md` 的 RK3576 老基线** ★ | ★**它是「另一套基线」的事实登记, 归 main 裁决 ⇒ 本单只在归一页里【引用】它, 不许改它** ★ |
| ★**零外发** ★ | 不发邮件 / 不询价 / 不问询 / 不采购 ⇒ ★**查不到就写 `[0数据]` + 降级方案** ★ |
| ★**证据分级** ★ | 每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` |
| ★**零实物** ★ | ★**实物 `[实测]` = 0 条** ★ (★本机无板; 「实测」= 文件实读 + 脚本实跑★) |
| ★**不替老板拍板** ★ | 台账格式契约的最终落点 / 台账自身要不要加锚 = ★**给建议与代价, 归 main 拍** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | 只走 `state/frag_write.py --agent mech-lead` |
| ★**不写别人的分片** ★ | 只写 `state/fragments/mech.yaml` (★**main 的 `state/fragments/pm.yaml` 你一个字不许改** ★ ⇒ ★**配对闭合靠【answer 的 key 与 main 开的 key 一致】, 不是靠改 main 的分片★**) |

---

## ⑤ 三条不许搞混的 (★本轮踩出来的★)

1. ★**「60×30 套A 坐标」≠「现役板坐标」** ★ ⇒ ★**两个物理产品 (SoC 直上板 vs SoM 承载区) ⇒ 坐标不可互相代入** ★ ⇒ ★**你现在做的归一, 就是为了让别人不必再踩这一脚** ★
2. ★**「ISS-267/271 判红」≠「现役板开不了工」** ★ ⇒ ★**它们判红的是【60×30/60×15 装不下检修口】, 不是【160×100 台架板不能用】** ★ ⇒ ★**你归一后的开口, 是在现役板上的另一个几何问题, 别把两个结论混成一句** ★
3. ★**「answer 的 key 写对」才是闭合** ★ ⇒ ★**你在 mech.yaml 写 answer ⇒ merge.py 按 key 配对 ⇒ key 与 main 开的差一个字就【不闭合】⇒ ★**本单必须用 `iss273_h1_anchor_single_source` 这个原 key** ★ ⇒ ★**写完自己 `grep` 一次确认** ★
