# MECH/MECH_NEEDS_TRIAGE.md —— MECH 域未答需求四分类处置 (ISS-313)

> **交卷人**: 结构总工 (mech-lead) 🔩 · **日期**: 2026-11-18 · **关联**: ISS-313 (队列自动派活 · cron `fb67af40`)
> **性质**: 内部活 · 需求闭环 / 卫生类 · **零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log**
> **同源**: 本页与 `HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md` 与 `state/fragments/mech.yaml` 的分类结果**同源** (数据源 `logs/iss313/iss313_data.py` ⇒ 改一处三处一起变)。

---

## §0 · 口径 · 取数命令 · 证据分级声明

### §0.1 本单要解决什么

`state/gate_check.py` 的缺口清单里, `mech-lead: 108 条需求确实还没人答 (等另一个总工)` (派活时 05:5x 实测) —— 口径是
`real_open = needs_total − needs_answered_incoming − needs_closable_unregistered − needs_waiting_external`。
本单把 MECH 域 `needs_from` 的 **185 条**逐条归类并处置, 让这条红**真的降下来**。

### §0.2 四类怎么分的 (★与派活书一一对应★)

| 类 | 判据 | 条数 | 本单动作 |
|---|---|---|---|
| ① `waiting_on = agent` | 显式 `waiting_on: agent` (34 条) + `waiting_on: hw-lead` (1 条 · **格式错**: 应为 agent) | 35 | 内部活 ⇒ 自己推: 能答的直接写进 `answers`; 不能答的写清【该谁答 + 为什么 + 一句话问法】 |
| ② `waiting_on = boss` | 显式 `waiting_on: boss` | 20 | **不代拍** ⇒ 整理成 `need key + 决策码` 一页 (选项 / 代价 / 建议默认值 / 不拍的后果) |
| ③ `waiting_on = vendor` / `jbd` | 显式 `waiting_on: vendor` (10) / `jbd` (6) | 16 | ★**老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信, 全靠自己查资料」⇒ 一律自查 + 标证据等级 + 查不到写降级方案 ⇒ 关闭, 不再挂等外部回信**★ |
| ④ `waiting_on` 为空 (缺字段) | `needs_from` 条目**没有** `waiting_on` 字段 ⇒ 合并器/门禁按 `agent` 语义处理 (内部) | 114 | 逐条判三选一: (a) 已作废 / (b) 已被本单答复覆盖 / (c) 真·待答 |

### §0.3 证据分级 (★全页每个结论都带★)

| 标记 | 含义 |
|---|---|
| `[官网]` (≡ **官方**) | 原厂 / 官网 / 标准原文可直接复核 (例: renata.com 产品页、MIL-A-8625F、Hirose 官网规格) —— ★本域习惯叫「官网」, `state/gate_check.py` 的证据标签集里同一档叫「官方」, 同一档不两说 |
| `[实测]` | 本机实跑脚本 / 解析盘上文件得到的数 (可复现, 命令见 §9.2) |
| `[媒体]` | 行业通例 / 公开资料 (无统一规格的那种) |
| `[推算]` | 由上两类按公式复算得到的设计态值 |
| `[0数据]` | 公开渠道查不到 ⇒ 记为已知缺口 ⇒ **必配降级方案** |

> ★**标签对照**: 本页用 `[官网]` 表示 gate_check 标签集里的 **官方** (同一档, 本域习惯叫「官网」); `[实测]` / `[推算]` / `[0数据]` 四档同名。

### §0.4 取数命令 (★逐条取数, 原始输出在 `logs/iss313/`★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss313_tmp          # ★/tmp 是带 usrquota 的 tmpfs, 配额已满 ⇒ 别写 /tmp★
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb MECH/service_port_check.py state/fragments/mech.yaml
```

---

## §1 · 四类总账 (对账表)

| 类 | 总条数 | 本单之前已闭合 (不动) | **本单关闭** | **本单保留** | **本单新答** |
|---|---|---|---|---|---|
| ① waiting_on=agent (内部) | 35 | 1 (格式错那条已被 hw-lead 答) | **12** | 9 | 12 |
| ② waiting_on=boss | 20 | 3 (2 条老板已拍 + 1 条 main 已答) | **5** | 12 | 0 |
| ③ vendor / jbd (外部) | 16 | 0 | **16** | 0 | 16 |
| ④ waiting_on 空 | 114 | 45 | **31** | 51 | 0 |
| **合计** | **185** | **49** | **64** | **72** | **26** |

> ★**「本单之前已闭合 49 条」的口径**: ① 被**被问方**在 `answers` 里用同一 key 答过 (merge.py 的闭合规则: 需求 `(owner,key,to)` 被闭合 ⟺ 存在 key 相同且**作者 = to** 的答复) 45 条; ② 老板 `decision` 全局闭合 2 条 (`q4_battery_scope` / `q16_aspect_ratio`) + main 已答 1 条 (`iss047_margin_criterion_decision`) + 格式错那条 (`iss017_pcb_thickness_vs_service_port_clearance`, 已被 hw-lead 答) 1 条 ⇒ **这些条目本单一个没动**, 留在 `needs_from` 作历史痕迹。
>
> ★**关闭的定义**: 从 `needs_from` 移出 + **依据行** (本页表格 + 分片 `needs_closed` 台账, 两者同源) ⇒ 合并器/门禁的 `needs_total` 与 `needs_waiting_external` 同时下降。
>
> ★**新答的定义**: 写进 `state/fragments/mech.yaml` 的 `answers` (带 key + 出处 ref + 证据等级) ⇒ 合并后进 `STATE.yaml` 的 `domains.mech-lead.answers`, 全员可见。

### §1.1 机检数字的前后对比 (★本机实跑, 原始输出见 `logs/iss313/`★)

| 指标 | 派活时 (2026-11-18 05:5x) | 本单交卷时 (06:4x) | 变化 |
|---|---|---|---|
| `mech-lead` 缺口清单条数 | 108 条 | **62 条** | **↓46** |
| `mech-lead` needs_total | 185 | 121 | ↓64 |
| `mech-lead` 等外部 (boss/原厂/JBD) | 20 条 | 16 条 (全为 boss 类) | ↓4 |
| **全局** 等外部 | 70 条 | **49 条** | **↓21 (★16 条外部依赖清零★)** |
| **全局** 等另一个总工 | 341 条 | **306 条** | ↓35 |
| 自闭合 (自己答自己) | 0 条 | **0 条** | 不变 (★本单不许自闭合⇒ 一条都没造★) |
| Q1 交付齐备率 | 18/18 | **18/18** | 不变 |

---

## §2 · ① 类 · `waiting_on = agent` (35 条) —— 内部活自己推

★**这一类的处置口径**: 逐条判【我能答吗】⇒ **能答的直接写进自己的 `answers` (带 key + 出处 + 证据等级)** ⇒ **不能答的写清【该谁答 + 为什么 + 一句话问法】**。

### §2.1 关闭的 12 条 (依据行逐条)

| # | need key | 原 to | 动作 | 依据 (★每条都带★) | 级别 |
|---|---|---|---|---|---|
| 1 | `iss085_battery_side` | main | **close+answer** | [实测] HW/netlist_v1.csv L17「[BAT_CHG] 充电电流进镜脚侧电池保护 IC (BQ2970) —— 保护 IC 与电池同板 (镜脚)」+ L40「[V1.2 电池搬镜脚后]」+ L2「充电链整条在充电板」⇒ 电池在镜脚 / 充电板在镜框 的分工已落表 | [实测] |
| 2 | `iss085_service_port_form` | main | **close** | MECH/SERVICE_PORT_ISS092.md (2026-10-30, ISS-092 交卷) 已给完整规格 (开口 10.20×4.60 / 盖板 13.20×7.60×1.20 / 内腔 4.70 / SP-A·SP-B·SP-C 三案 / §11 七条接口请求) ⇒ 本条 (2026-10-27) 的全部问项被覆盖 | [实测] |
| 3 | `iss100_jchg_pitch_fix` | main | **close+answer** | [实测] MECH/hinge_usb_check.py:67 "j_chg_pitch_mm": (0.50, "J_CHG 定稿 0.5mm pitch (网表 V1.5 起; ISS-085 已定 0.5mm —— 原来这里写 1.27 是过期口径, 导致 [FAIL] 假警报)") | [实测] |
| 4 | `iss099_hw_mounting_holes` | main | **close+answer** | [实测] 现行套 A (MECH/BOARD_GEOM_30MM.md §3 + HW/pcb60x30_check.py:119-124 + mech.yaml interface_claims.pcb_mounting): P1(8.00,15.00)/P2(52.00,15.00) 定位销 ⌀2.0 (P1 全基准 + P2 只定 Y) + S1(8.00,10.00)/S2(52.00,20.00) 压紧 ⌀1.4 | [实测] |
| 5 | `iss099_hw_jchg_qty` | main | **close+answer** | [实测] HW/BOM_v1.csv:70 note「实物一对 (框侧座 + 脚侧座), 备料按 2 只」+ HW/netlist_v1.csv L38 note「J_CHG 实物是一对 (框侧座 + 脚侧座), 采购/备料别只算一只」 | [实测] |
| 6 | `iss092_service_port_face_decision` | main | **close+answer** | [实测] MECH/SERVICE_PORT_ISS092.md §11 I-2「假设按【外侧面】+ 接受 +0.73 g」+ HW/PCB/BOARD_ONEPASS_WORKPACKET.md §1 C-OPEN-1 (调试口 罩 J_DEBUG) / C-OPEN-2 (检修口 罩 J_UART) 已按外侧面 SP-A 给出坐标 (帧 B160x100) | [实测] |
| 7 | `iss092_probe_before_cover_decision` | main | **close+answer** | [实测] MECH/SERVICE_PORT_ISS092.md §11 I-3「假设按【装前压针】」+ §0 #6 (产线: J_DEBUG 改 2×5@1.27 Cortex-10 焊盘阵列 D-1 + 装前压针) + §0 #7 (零新增工位) + §4.2 C-6「默认无 (实心盖板)」 | [实测] |
| 8 | `iss092_ip_wording_decision` | main | **close+answer** | [实测] MECH/SERVICE_PORT_ISS092.md §0 #5「IP: …【本项目现阶段不宣称 IP 等级】(FRAMEWORK_SCOPE H5-04 已把 IP 推迟到量产)」+ §6 三段措辞 + §11 I-4 | [实测] |
| 9 | `mech_rebase_pcb_width_y_holes` | hw-lead | **close** | [实测] 套 A 已仲裁并落表 (MECH/BOARD_GEOM_30MM.md §3 + HW/pcb60x30_check.py:119-124 + mech.yaml interface_claims.pcb_mounting) ⇒ Y 坐标不再是待确认项 | [实测] |
| 10 | `iss192_pcb60x30_holes_set_b_to_set_a` | hw-lead | **close+answer** | [实测] HW/pcb60x30_check.py:119-124 HOLES = [P1 (8.00,15.00) ⌀2.0 全基准 / P2 (52.00,15.00) ⌀2.0 只定 Y / S1 (8.00,10.00) ⌀1.40 只压紧 / S2 (52.00,20.00) ⌀1.40 只压紧] = 套 A | [实测] |
| 11 | `iss200_mech_doc_residual_old_pinmap` | main | **close+answer** | [实测] MECH/USB_HINGE_STRUCTURE.md: L16 §0 C-3 (40p→16p/20p/26p 已标作废, 现行 25.30 整机 / 5.00 demo) + L18 §0 C-5 (SYS 不跨铰链, 老 0.55A 口径已作废) + L19 §0 C-6 (反插真实后果 = 1 断路 + 2 短接, 不是『BAT_CHG 短接 GND』) + L286 §5.1 J_CHG 行 (老 6 脚口径已作废) + L362 §5.3 C-4 (算式已按 10p 改写, 两格已按裁写齐) | [实测] |
| 12 | `iss200_mech_frag_mech_j_chg_pins_note` | main | **close+answer** | [实测] mech.yaml interface_claims.mech_j_chg_pins.note 现写『本 note 现与同域另一条 claim j_chg_pin_map (ISS-200 已订正) 逐脚完全一致, 分片内不一致已消除』; value 仍是 10p@0.5mm | [实测] |

### §2.2 保留的 9 条 (owner + 一句话问法)

| # | need key | owner | 为什么是他答 | 一句话问法 (★给 main 的一行 need★) | 板那一趟? |
|---|---|---|---|---|---|
| 1 | `iss100_hw_pcb_outline_stale` | hw-lead (经项目总工) | 分片取值属硬件总工地界, 我不许代改; 且这两个数会进板那一趟的 P10 充电链判据 | hw-lead: 请把 interface_claims.chg_input_limit 从 0.82-1.00A (390Ω 档 + 0.822 倒向系数) 改成 680Ω 现行口径 (IIN 0.574A / ICHG 0.698A / 单 pin 0.349A), 出处 MECH/HINGE_POWER_CALC.md §0-A.1 | ★是★ |
| 2 | `iss100_stale_cost_rows` | hw-lead (经项目总工) | 正文行属 HW 地界; 我只在 mech-lead 侧的结构结论是对的 (串行模型下净高 38mm 一毫米不用动) | hw-lead: 请删/改 HW/PCB_FORM_FACTOR_RECHECK.md 的 L342 / L377 / L425 三行 15mm 板宽旧代价 (L185 若仍在也一并清), 结构侧回执: 串行模型下镜腿根部净高 38mm 一毫米不用动, 打印件不改版 | 否 |
| 3 | `iss092_print_pack_rev` | main (批期排程) | 本域出不了『排进哪一批』的答案 —— ISS-027 批次表是项目总工的排期地界; 且批次排序要先看板那一趟 | main: 请把 ISS-092 的打印包改版五件 (通窗 / 螺钉凸台 / 磁铁沉槽 / 定位凸台 / 盖板件) 排进 ISS-027 哪一批 (本域建议 B2 镜脚装配验证批), 并把第三档 Type-C 试样 (frame_typec_coupon_tier3_revb.stl) 同批 | 否 |
| 4 | `mech_dfm_battery_seat` | main → boss | 架构/成本取舍是老板级; 改了会动整条镜腿壳体分型 (与 ISS-127 P1 耦合) | main→boss: 电池座与 PCB 座是否接受从『注塑件本体特征』改为 CNC 金属嵌件 (Al6063-T6, 与 SoC 骨架共基准)? 几何上不做不出来 (电芯段 H 链最坏 -0.577mm, 皮纹面 0.5° 也只救到 0.087mm), 代价 = 零件数 +2 (左右各 1) + 成本 | 否 |
| 5 | `mech_dfm_shell_geometry` | main (排期) + 结构侧出模型 | 本域可做的是【建模】, 排期与开模次序要 main 定; 且与 ISS-127 P1 (H 向分型) 架构裁耦合 | main: 请定量产外形件建模排期 (本域建议在 ISS-027 B3 镜框与光学批之前完成建模并跑 MECH/dfm_check.py 面级检查; 未完成不开模); 建模口径按 ISS-127 P1 (H 向分型 = 皮肤盖 + 内胆) | 否 |
| 6 | `mech_rebase_netlist_hinge_mismatch` | main + hw-lead | 网表是硬件总工的地界, 我只报; 结构侧影响 = 铰链区整套结论 (ISS-085/089/091) 是否转 deferred 到整机阶段 | main+hw-lead: DEMO_BOARD_HW_DECISION §5-N5 (J_CHG 不再跨铰链 / 充电 IC 与电池位改 DNP) 至今未落 —— HW/netlist_v1.csv 仍 CHG_BOARD 94 行未转 DNP 且 J_CHG board=HINGE; 请给一句: demo 阶段是否保留 J_CHG 跨铰链? (结构侧按『保留 ⇒ 铰链区结论继续成立 / 取消 ⇒ 本域 ISS-085/089/091 转 deferred』执行) | 否 |
| 7 | `iss192_demo_board_zero_mounting_holes_keepout` | hw-lead + main (板那一趟同批改) | 板与网表都归硬件总工; 结构侧只能给『骨架要几个定位基准 + 孔心到板边余量』的接口要求 | hw-lead: demo 板 (HW/PCB/demo_mainboard.kicad_pcb, 帧 B160x100) 零 MountingHole, 而 params 里的 4 个坐标是 60×45 时代遗留且两点压在器件区 —— 请在板那一趟同批补 4 个 ⌀2.2 固定孔 (孔心到板边 >=2.50mm, 避开 SoM 承载区) 并同步 params; 结构侧回执: 骨架按 2 定位销 (全基准 + 只定 Y) + 2 压紧孔 造 | ★是★ |
| 8 | `iss192_mech_scripts_dead_constants_disposition` | main (机制裁决) | 『历史可复现 > 文件干净』还是『退役 v2』是项目取舍; 本域倾向并存 + v2 打横幅 | main: 请裁 MECH/fit_check.py (M-FIT v2, 基线板宽12/板长50/4层0.80 已全死) 与 MECH/fit_check_v3_30mm.py 长期并存还是退役 v2? 本域倾向并存 + v2 打作废横幅 (历史可复现 > 文件干净), 只改它一个数会造出 Frankenstein 半迁移口径 | 否 |
| 9 | `iss200_hw_residual_old_pinmap` | hw-lead (经项目总工) | 逐脚 net 行是对的, 只有 note 列带旧口径 ⇒ 机器判定以逐脚 net 为准, 但人会读 note | hw-lead: 请订正 HW/netlist_v1.csv 的 note 列旧 J_CHG 口径 (L38『pin7=VBUS_DET』→pin7=NC; L20/L21『pin10 已改作 TS 专用回流』→pin10=HINGE_RSV), 逐脚 net 行一个不许动 | 否 |

---

## §3 · ② 类 · `waiting_on = boss` (20 条) —— need key + 决策码一页 (★不代拍★)

★**口径**: 这一类**不是**结构侧能答的 (口径/预算/产品语义是老板级) ⇒ 本单**只整理不拍板**: 每条给【决策码 + 选项 + 代价 + 建议默认值 (只作参考) + 不拍的后果】。
★老板只要在决策页上回一个码即可, 不用重读 185 条。

| 决策码 | need key | 状态 | 要拍的一件事 | 选项 | 代价 | 建议默认值 (★只作参考·不代拍★) | 不拍的后果 |
|---|---|---|---|---|---|---|---|
| **M-B0** | `q4_battery_scope` | 已闭合 | 按需触发场景下 ≥1h (老板 10-25 19:16 拍板, 项目总工代录) | ★已闭合 (老板 10-25 19:16 拍板, 项目总工代录) ⇒ 留档备查, 不再重复问 | — | — | — |
| **M-B0** | `q16_aspect_ratio` | 已闭合 | 宽高比无所谓; 选型判据改为『≥1080p60 出图能力』(老板 10-25 19:16 拍板) | ★已闭合 (老板 10-25 19:16 拍板, 项目总工代录) ⇒ 留档备查, 不再重复问 | — | — | — |
| **M-B1** | `boss_local_print_measure` | 待拍 | 指定打印与量测执行方 (三选一) | ① 把打印执行方接入 192.168.1.0/24 或开子网互通 (零采购) ／ ② 委托代打印服务 (¥/件 + 排期) ／ ③ 在能装 Bambu Studio 的桌面环境切片 + 第三方打印 | ① 零采购但依赖对方改网络; ② 一次性服务费 + 沟通成本, 拿到 STl 直接下片; ③ 需一台能装切片器的机器 + 第三方面 | ① (零采购; 本机实测 ping 无响应 + TCP 990/8883/6000/4000 全 closed, 见 MECH/print/ENV_PROBE_20261101.md) | 不拍 ⇒ 实物实测 [实测] 永远 = 0 条 ⇒ G2 阶段门永久红; B1 的 34 项工艺数据 / B2 的 49 项实测全部拿不到; 且 T-05~T-08 材料试样 (UV 老化 2000h ≈ 83 天) 排期无法启动 |
| **M-B2** | `reva_cell_thickness_tol` | 待拍 | 电芯厚度公差写进采购要求 ≤±0.10 (★并须把型号名改对) | ① 收紧到 ≤±0.10 并把型号写对 (见 evidence 的型号错配) ／ ② 维持 ±0.15 (需把压垫工作间隙从 0.15 加到 0.20+, 吃掉 H 链余量) ／ ③ 改用丰江 432243 (4.30mm) 绕开厚度公差 | ① 采购窗口可能变窄 (★但型号改对后才是真约束); ② H 链余量 -0.05~0.10, 判据 0.60 口径下余量归零风险; ③ 整机 +2.28g (MECH/CLEARANCE_FIX.md §解B 实测) | ① + 型号改对 (本域建议) | 不拍 ⇒ 采购单按 340mAh/4.60mm 下单, 而真型号厚 6.40mm ⇒ 到货装不进 7.30mm 镜腿 ⇒ 电芯段 H 链直接报废 (最坏 -1.10mm); 且 ±0.15 下最坏情况电芯顶到顶板 (硬干涉 0.25) |
| **M-B3** | `mech_reltest_kit_site` | 待拍 | 可靠性测试的场地与工装预算 (A 自购小件 / B 借用 / C 外委) | A 自购小件 ¥800-1500 (扭力计/拉力计/人工汗液试剂/酒精/色卡) ／ B 借用 (恒温箱/UVA-340 老化箱/振动台/FPC 动态弯折机) ／ C 外委 (X-ray 抽检 + 切片 ¥3000-8000 + MTF) | A 最便宜但只能覆盖 T-01~T-08 的一部分; B 零采购但依赖外部排期; C 单价最高但一次买齐 12 类用例 | A + C (A 覆盖贴肤/化学类, C 只外委 X-ray/切片/MTF 三项) | 不拍 ⇒ 12 类用例全部停在方案阶段 (UV 单项就占 83 天设备窗口) ⇒ 1 台样机的唯一一次采集机会作废 |
| **M-B4** | `mech_reltest_usb_mon_kit` | 待拍 | ISS-085 T-13 监测设备清单 (与 M-B3 同一笔预算) | ① USB 协议分析器 ／ ② 示波器 + 差分探头 ／ ③ 主机端自动批量传输脚本 ／ ④ 自制扭转保载夹具 ／ ⑤ FPC 动态弯折机 ／ ⑥ 阻抗仪 | ① 单价最高但一键出报告; ② 通用件可复用; ③④⑤⑥ 单价低但要做工装 | ② + ③ (先把 USB 连续性判据立起来, 动态弯折另借) | 不拍 ⇒ T-01/T-02/T-03 照做, 但 T-13 无数据 ⇒ 跨铰链 USB 链路连续性始终没有量产抽检口径 |
| **M-B4b** | `iss047_margin_criterion_decision` | 已闭合 (main 已答) | 俯角余量口径 = B' 有效余量 >=4deg (含边框遮挡 1.91deg => 俯角 <=25.89deg, h_max d=35 = 16.99mm) —— ★本条已被 main 用同一 key 答过 (merge 口径 answered) ⇒ 本单只留档, 不再重复问 | — | — | — | — |
| **M-B5** | `iss091_rilim_decision` | 已闭合 | R_ILIM 档位 = 680Ω (V-4 已裁) | — | — | — | — |
| **M-B6** | `iss091_worn_while_charging` | 已闭合 | 『边戴边充』不允许 (老板 10-28 已拍) | — | — | — | — |
| **M-B7** | `iss100_board_length` | 已闭合 | 板长 = 60.00mm (10-28 项目总工裁) | — | — | — | — |
| **M-B8** | `iss099_poka_yoke_decision` | 已闭合 (按本域默认假设) | 机械防呆 = 结构硬约束 (外侧面防呆 + 定位键) | — | — | — | — |
| **M-B9** | `iss099_rilim_300_dead` | 已闭合 | R_ILIM 300Ω / 260Ω 已判死 (随 V-4 落表) | — | — | — | — |
| **M-B10** | `proto_wear_criteria` | 待拍 | B4 佩戴体验三项可测项定义 (夹持力 / 配重分布 / 鼻梁压感) | ① 老板给三个数 (夹持力 N / 配重分布 % / 鼻梁压感 mm 或 g) ／ ② 老板只给『合格区间』不点具体值 ／ ③ 授权结构侧按 ISO 12845/EN ISO 9241-6 提建议值由老板确认 | ① 最省事但要老板花时间; ③ 本域出数有依据 (ISO 12845 夹持力分布 + 鼻梁区接触压强), 但仍需老板签字 | ③ | 不拍 ⇒ 这三项全标 [0数据] 且无判据, 而 1 台样机只有一次采集机会 (RELIABILITY_TEST_PLAN §B2.3/B3.3 样本量硬边界) ⇒ 漏测后续补不回来 ⇒ B4 佩戴体验这一整项作废 |
| **M-B11** | `proto_b4_reliability_kit` | 待拍 | B4 当天的器具清单 (T-14 无损段 + T-13 挂测位) | ① 沿用 M-B3/M-B4 的总预算, 只确认『本批次要哪几样』 ／ ② 单独批一笔 B4 零星器具 | ① 零重复申请; ② 多一次审批 | ① (同源同账) | 不拍 ⇒ B4 当天 T-14 (弯折区结构审查 + J_CHG 反插 20 次) 与 T-13 挂测位都缺器具 ⇒ 当天只能做目视, 无留证 |
| **M-B12** | `iss017_local_print_measure_unblock` | 待拍 | ISS-017 实物实测 0 件的解锁条件 (与 M-B1 同一笔, 合并拍) | ① / ② / ③ 同 M-B1; 另加量测侧四件套 (数显卡尺 0.01mm + 塞尺 0.02mm 一档 + 弹簧秤 0-25N + 电子秤 0.01g) 或由打印方代测回填 | 量测四件套 ≈ ¥300-600 (一次性, 可长期复用); 代测回填免费但每批一次往返 | ① + 自购量测四件套 | 不拍 ⇒ 同 M-B1: G2 永久红, B1/B2 实测拿不到; ★M-PRINT 是 B1 的唯一硬前置 ⇒ 它不解锁, B1→B2→G2 直接少 2 项 |
| **M-B13** | `mech_mat_skin_coating_decision` | 待拍 | 皮肤侧 PU 封闭涂层是否列为必须工序 + 整机是否做 ISO 10993 评价 | ① 列为必须工序 + 只对涂层件出 ISO 10993 声明 (暂不做整机评价) ／ ② 不列 (皮肤侧直接裸 PA6-CF) ／ ③ 整机做 ISO 10993 生物相容性评价 | ① 增加 1 道工序 + 周期; ③ 排期后移 (1 台样机阶段做整机评价不现实) | ① (与本域默认假设一致) | 不拍 ⇒ 皮肤侧耐汗液/化妆品的责任无归属 ⇒ T-05~T-08 的 R6-1/R6-2 两组试样对比失去判据 ⇒ 贴肤面是否合格无结论 |
| **M-B14** | `mech_mat_sweat_test_spec` | 待拍 | T-05~T-08 材料试样送检执行方 (7 组试样 + 老化箱/恒温槽排期) | ① 送第三方检测机构 (贵, 报告权威) ／ ② 自建 (需老化箱/恒温槽, 本机没有) ／ ③ 混合: 第三方做 T-06/T-08 (UV 老化), 自建做 T-05/T-07 | T-08 UVA-340 2000h ≈ 83 天设备窗口 ⇒ 建议最先启动; 第三方单项 ¥ 数百~数千 | ③ + 立刻启动 T-08 排期 | 不拍 ⇒ 83 天的 UV 老化窗口错过, 全部顺延一个季度; 且 T-06 硬判据 (UV 后剪切 ≥90%) 没有被执行方 |
| **M-B15** | `mech_mat_nose_pad_criteria` | 待拍 | 鼻托压力 / 镜腿压力分布 / 佩戴稳定 / 可佩戴时长 4 项判据 | ① 老板给 4 项可测判据 (压力 N / 分布 % / 稳定时长 h / 可佩戴 h) ／ ② 授权结构侧按 ISO 12845 + 现有 B4 方案提建议值 | ① 老板花时间; ② 本域出数有依据但需老板签字 | ② | 不拍 ⇒ ISS-038 的压力侧四项永远无判据 ⇒ 鼻托与镜腿的设计无从收敛 (材料侧交了 VMQ-A50 但压不出可用性结论) |
| **M-B16** | `mech_dfm_draft_texture` | 待拍 | 镜腿皮肤侧是否接受皮纹面/喷砂面 (而非光面) | ① 接受皮纹面 ⇒ 脱模斜度可放宽到 0.5° (深腔截面差 1.327→0.663mm) ／ ② 不接受 ⇒ 皮肤侧须 1.5° ⇒ 截面差 1.990mm | ① 外观取舍 + 模具成本略高; ② 几何余量被吃掉 0.663mm ⇒ 电芯段 H 链更紧 | ① (本域默认假设: 按皮纹面推进, 鼻梁区仍可光面) | 不拍 ⇒ 脱模斜度只能按 1.5° 取 ⇒ 量产外壳几何做不出来 (与 mech_dfm_battery_seat 同一条链) ⇒ 开模前必须回来 |
| **M-B17** | `iss209_mech_d_value_decision` | 待拍 | 评估距离 d 取 15 / 18 / 20 (眼盒判据 V2 §3 ⑤-b) | d=15 ⇒ T=18.00mm, 可动余量仅 0.20mm (< 判据 0.60 ⇒ 装配不可行) ／ d=18 (同类公开值) ⇒ T=21.00mm, 余量 3.20mm (唯一装得下且有余量的折中) ／ d=20 ⇒ T=23.00mm, 余量 5.20mm 但镜框最厚 ×1.92 于 12mm 目标 | d=15 直接否掉当前腔体布局; d=20 镜框厚 23mm, 重量与外观代价大 | d=18 (本域只给数, 不拍板) | 不拍 ⇒ 镜框正中区腔体重排 (T = d+3.0) 与分光件规格 (C-6) 都定不下来 ⇒ 镜框占位件开不了工 ⇒ ISS-209/219/222 的下游全部挂起 |

★**与项目总工既有清单的对应**: `DECISION_INDEX_2026-11-18.md` 的待老板拍板清单已列本域 18 条 (编号 #9~#26) ⇒ 本页的 `M-B1~M-B17` 与它一一对应 (本页多出的是本单新查出的 `M-B2` 的型号错配与 `M-B8` 的已闭合项)。

---

## §4 · ③ 类 · `vendor` / `jbd` (16 条) —— ★自查 + 证据等级 + 降级方案★

★**老板政策 (硬)**: 2026-11-11 19:31「不再做任何邮件 / 供应商 / 原厂问询, 获取不到结果的自己网上查」+ 2026-11-12 02:02「不再发信, 全靠自己查资料」。
⇒ 本单**零外发** (不发邮件 / 不询价 / 不问询 / 不采购 / 不联系任何厂商), `state/outbox/` 下的草稿**一律不发只留档**;
⇒ **16 条一条都不许再挂「等原厂回信」** ⇒ 逐条自查 ⇒ 查不到就写降级方案 ⇒ **全部关闭**。

| # | need key | 原 waiting_on | 自查结论 (摘要) | 证据等级 | 降级方案 (★查不到怎么办★) |
|---|---|---|---|---|---|
| 1 | `jbd_waveguide_2d` | jbd | 【自查结论 · 不再等外部回信】JBD 官网 (jb-display.com) 只公开 MicroLED 光引擎/投影器与开发套件参数: Hummingbird | [官网]/[0数据] | ① 镜框按【参数化占位 + 可换压框】设计: 卡槽按 3 档假想外形建模, 到货只换压框不改镜框主体 (ISS-134 V2 已定同一路径, 见 MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md); ② 眼盒面积 ≤62 … |
| 2 | `jbd_dual_eye_module` | jbd | 【自查结论 · 前提已作废】走鹃Ⅱ 已于 2026-11-02 换型为视涯 0.49" 1920×1080 SiOLED 面板 (老板『视崖屏幕已经不用了』, | [官方]/[推算] | 结构按 ISS-209 重排口径留位: 正中区轴向厚度 T = d + 3.0 = 18/21/23mm (d=15/18/20, 待 M-B17 拍) + 眼盒 ≤62mm² 约束下的分光件新规格 (45° 平板 11×11×1.5 +  … |
| 3 | `jbd_optical_engine_dims` | jbd | 【自查结论 · 前提已作废 + 尺寸公开查不到】① 走鹃Ⅱ 已作废 (同 ③-2); ② 官网只给体积/重量/功耗/FOV (Hummingbird Ⅱ 全彩投 | [官网]/[0数据] | 镜框光学腔体按 ISS-209/219 的参数化口径出 (T=18/21/23mm 三档 + 眼盒 ≤62mm²), 并给 MECH/print/optical_cage_TEMPLATE.stl 一个【可换压框】的卡槽模板 —— 不再等待 … |
| 4 | `vendor_ars45_thermal_pad` | vendor | 【自查结论 · 前提已作废】① 酷芯微 ARS45 已不在选型内 (老板 2026-10-29 00:49 令跳过酷芯微改选国内 TOP5; 现役主控 = RK | [官方]/[0数据]/[实测] | 散热路径按现役口径定死: SoC 背面散热焊盘 → 0.3mm 导热垫 → 铝/铜骨架 (纵向延伸兼 PCB 支撑) → 石墨面内扩展 → 对流, 路径不得有塑料隔断 (打印件 k=0.2 插进去热阻 +94K/W); boot stora … |
| 5 | `iss017_waveguide_rainbow_metric` | jbd | 【自查结论】彩虹纹四项 (亮度均匀性 / 色差 / 应力敏感度 / AR 镀膜耐久性) 在公开渠道只有【代用量】, 无可直接引用的供应商判据: JBD 官网第三 | [官网]/[0数据] | ① 验收改用代用量三件套 (亮度均匀性 / ΔE / 彩虹抑制效率), 数值门槛随波导选型一起定; ② 结构侧只承诺【应力项可控】(沉槽/压垫/对称压紧, 装配应力不引起应力型彩虹纹), **给不出『彩虹纹合格』的结论** —— 膜层色差与 … |
| 6 | `mech_mat_waveguide_uv_cosmetic` | jbd | 【自查结论】波导/镀膜的 UV 透过率衰减 / 化妆品耐受 / 与硅胶垫相容性, 公开渠道查不到供应商分级数据 [0数据]。【降级方案】① 相容性改由【硅胶侧】 | [0数据]/[官网] | ① 相容性改由【硅胶侧】承担: 波导按玻璃基 + 硅胶垫 VMQ-A50 (硅胶按有 ISO 10993 / FDA 21 CFR 177-2600 认证的牌号选, 证书未到手不得投产) ⇒ 波导本身不用背相容性; ② UV 判据 (透过率 … |
| 7 | `mech_dfm_waveguide_seat` | jbd | 【自查结论】波导 2D 外形 / 外形公差 / 能否承受压铸件收缩与热变形 / 安装面平面度 四项, 公开渠道查不到 [0数据] (未选型 ⇒ 无供应商数据)。 | [0数据]/[推算] | 卡槽按【CNC 卡座 + 3 点金属压条】出图 (DFM_REVIEW 1.1-12): ① 压条角度可调 ⇒ 换波导只换压条, 不动镜框主体; ② 平面度/平行度写成【设计态判据】(安装面 0.05mm / 平行度 ±0.3deg, 与  … |
| 8 | `mech_reltest_cell_samples` | vendor | 【自查结论】① Renata 官网实读: ICP422339PR = 340mAh / 4.6mm / 23.5 / 40.5; ICP582035PR-01 | [官网]/[0数据]/[推算] | ① 备件 2 只按【同批号 + 同生产月】采购 (循环/鼓包的离散靠批内一致性, 不靠规格书); ② 内阻按 0.10Ω (区间 0.08-0.15) [推算] —— 且 ISS-229 已证结论对该区间稳健 (680Ω 档 max 39. … |
| 9 | `iss091_cell_ir` | vendor | 【自查结论】丰江官网只给尺寸/容量/循环/脉冲放电, **内阻未公布** [0数据]。【降级方案】按 0.10Ω (区间 0.08-0.15) [推算] 执行, | [官网]/[0数据]/[推算] | 按 0.10Ω (区间 0.08-0.15) [推算] 执行, 且该区间的敏感性已由 ISS-229 算完: 680Ω 档 max 皮肤侧 39.7°C (0.08Ω) ~ 41.4°C (0.15Ω) ⇒ 均 <43°C 红线, 结论稳健 … |
| 10 | `iss099_jchg_rfq` | vendor | 【自查结论 · 官网规格直接满足, 不需要询价】Hirose FH12-10S-0.5SH(55) 官网规格 [官网]: 单触点额定 **0.5A** / 10 | [官网]/[官方] | 若实测可插厚度不足 ⇒ 固定段改 1oz (压降回基准, 结论方向不变) 或固定段 2oz + 转角段单独加厚过渡 |
| 11 | `iss099_fpc_vendor_capability` | vendor | 【自查结论】① 分段铜厚 (固定段 2oz / 弯折段 1oz + 过渡斜坡 ≥1.0mm) = 公开 FPC 工艺通例, 无统一公开规格 [媒体/行业通例]; | [媒体]/[0数据] | ① 做不到分段铜厚 ⇒ 固定段也用 1oz (压降回基准, 结论方向不变); ② 做不到 keep-out ⇒ 改 6 层 FPC (铰链区径向余量 1.00mm 会被挤掉, 需重算) ⇒ 因此把 keep-out 列为硬要求, 其余两项可 … |
| 12 | `mech_mat_vendor_datasheet` | vendor | 【自查结论 · 三项里两项官网有、一项查不到】① 3M VHB 5962/5962P 官网 [官网]: 1.6mm 厚 (公差 ±10%) / 改良丙烯酸 / | [官网]/[0数据] | 电池固定维持【背胶 + 限位台阶 + 激光压痕】三重冗余 (VHB 不单独承结构力), 耐受性靠 R6-4 送检实测; UV 胶只用于【非贴肤点】(镜片/导光柱), 贴肤点一律机械 + 硅胶; T-06 判据 (UV 后剪切 ≥90%) 走 … |
| 13 | `mech_mat_anodize_process` | vendor | 【自查结论】MIL-A-8625F [官网]: Type III 膜厚公差 **±20%** (≤0.002in) / ±0.0004in (>2 mils); | [官网]/[0数据] | ① 出图写『masked, then machined to ≤5µm』, 夹具基准 = 精加工的 ⌀2.0 H7/h6 销孔 (与 PIN-SET-2 一致); ② 膜厚公差按 ±20% 写进图纸 (标称 25µm ⇒ ±5µm), 最终 … |
| 14 | `mech_dfm_shrink_rate` | vendor | 【自查结论】① PC/ABS 注塑件收缩率: ASTM D955-89 口径下 **0.29%-0.76%**, 且**各向异性** (流动向 vs 垂直流动向 | [媒体]/[0数据] | 所有『两件互相配』的界面按 DFM_REVIEW 2.5.3 移交 CNC 件/镶件 (与 mech_dfm_battery_seat 同向) ⇒ 结论不因具体 S 改变 ⇒ 该外部依赖可退休 |
| 15 | `mech_dfm_anodize_uniformity` | vendor | 【自查结论】MIL-A-8625F [官网]: 膜厚公差 ±20% (≤2 mil) / ±0.4 mil (>2 mil), 精密工艺可做到 ±0.1 mil | [官网]/[推算] | ① 按方案 A (CNC → 阳极 → 定位面/定位孔二次精加工 ≤5µm) 出图, 遮蔽区在图纸上标注; ② 若供应商只能做方案 C (阳极前留量) ⇒ 要求书面承诺膜厚均匀性 ≤±10%, 否则方案 B/C 不可用; ③ ★膜厚均匀性* … |
| 16 | `mech_dfm_mold_tolerance` | vendor | 【自查结论】① 注塑 PC/ABS 一般公差带 通用经验 ±0.20~±0.30 (小件) / ±0.50 (大件); 压铸 ADC12 ±0.20~±0.25 | [媒体]/[推算] | ① 按 DFM_REVIEW 2.4 公差带出图并**全部设单向公差**; ② 最小特征不可达处改 CNC 镶件 (与 mech_dfm_battery_seat 同向); ③ 顶针/浇口/分型面归量产外形件建模阶段 (need mech_ … |

★**逐条完整答复 (含全文 + 出处) 已写进 `state/fragments/mech.yaml` 的 `answers`** (key 与上表一一对应), 本页只给摘要。

---

## §5 · ④ 类 · `waiting_on` 为空 (114 条) —— 三选一逐条

### §5.1 (a) 已作废 / (b) 已被后续交付覆盖 ⇒ 关闭 31 条

| # | need key | 判定 | 依据 (★每条都带★) | 级别 |
|---|---|---|---|---|
| 1 | `iss091_stack_value_conflict` | (a) 已作废 —— 本条要统一的两个数 (27.0 / 26.5) 都已退出活口径 | [实测] 现行铰链区口径 = 25.30 mm (整机: 31p@0.3 + 22p@0.5 + 10p@0.5) / 5.00 mm (demo: 只有 J_CHG) —— MECH/USB_HINGE_STRUCTURE.md §0 C-3 + §9 + MECH/HINGE_FPC_GEOMETRY_TRUTH.md T1/T2; 净高分母 = 38.00 (现行) 不是 37.00 (已作废的叠放模型) | [实测] |
| 2 | `iss091_pin9_10_ntc_return` | (a) 已作废 —— 本条的前提 (把 pin9/pin10 改作 TS 专用回流) 已被网表撤除 | [实测] TS_RTN 在 HW/netlist_v1.csv 里 0 次出现 (2026-11-03 起残留撤除, NTC 与 30.31k 分压下臂改回 PGND) ⇒ 现行 pin9/10 = HINGE_RSV, 没有 TS 专用回流; 本域 need iss202_mech_frag_old_needs_stale (2026-11-12) 已把这条登记为【前提已不存在】 | [实测] |
| 3 | `iss089_typec_opening_and_print_pack` | (b) 已被后续两条覆盖 —— 打印包改版已按第三档试样落地 | [实测] ISS-213 (need iss213_mech_typec_third_candidate) 出第三档 (FDM 直成型 10.50×4.80 / 金属嵌件 CNC ±0.05 10.25×4.55, 最坏单边 0.63/0.62 ✅) + ISS-218 已落成 MECH/print/frame_typec_coupon_tier3_revb.stl (72.0×32.0×5.0mm, 可直接下片) + 门禁 (余量对拍 4/4 + MECH_ANCHORS 7/7 + 反向用例 8/8); ① 镜脚侧 Type-C 特征已随 ISS-014 决策 5 (充电板挪镜框) 作废 | [实测] |
| 4 | `iss017_board_width_direction_clarify` | (a) 已作废 —— 口径已被锁定 | [官方] 板宽 30mm = V 向 (镜脚垂直方向): 老板 10-29 19:16 拍板 + MECH/BOARD_GEOM_30MM.md §0『板宽是 V 向尺寸 ⇒ 镜脚 V 余量 17.00 → 2.00 (最坏 1.40), 板宽硬顶 31.40mm』+ 镜脚三条锁死尺寸链 H 7.30 / V 38.00 / L 130.00 一字不动 | [官方]/[实测] |
| 5 | `optical_cavity_recompute_for_sioled` | (b) 已被 ISS-208/209 的重排交付覆盖 | [实测] MECH/CENTER_CAVITY_RECALC.md + MECH/cavity_recalc_check.py (rc=0, 12 项 + --selftest 9/9) + MECH/MECH_BUDGET.md §1.8 指针段 + §1.7 X-1..X-6 (眼盒/腔体/热学判据) ⇒ 镜框侧四件事 (光学腔体 / 分光器 / 显示仓布局 / 外形重量) 已出数 | [实测] |
| 6 | `mech_numpy_dep_for_print_check` | (a) 已解决 —— 本条的阻塞 (numpy 缺失) 不复存在, 剩余项已由另一条 need 承接 | [实测] 2026-11-11 21:2x 实测: numpy 2.5.4 (python3 3.14.4) ⇒ python3 MECH/dfm_check.py rc=0 + python3 MECH/print/verify_pack_revb.py rc=0 (93/93 + 38/38); ★真正剩余阻塞 (量产外形件模型) 已由 need mech_dfm_shell_geometry 承接 | [实测] |
| 7 | `iss134_mech_close_legacy_zoujuan_refs` | (b) 已被本单自己的收口交付覆盖 (ISS-208) | [实测] 5 份旧文档 33 处『走鹃』逐处定性 = 活动 27 (全部改写成现行口径) + 历史 6 (保留原文 + 加『已作废 (2026-11-15, ISS-134 V2)』); 机器门禁 python3 MECH/display_biosafety_v2_check.py rc=0 (5 项) 带 --selftest 6 用例全过; 逐处定性表见 MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md §1 | [实测] |
| 8 | `iss208_mech_legacy_zoujuan_closeout_done` | (b) 闭环完成上报 —— 交付物已落盘, 无待答项 | [实测] 同上: MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md §1 + display_biosafety_v2_check.py rc=0 + 判据文件 md5 96239070dc7c0ec00edb1b758a698769 / bda4a29464336bc1452c913602ce3f46 未变 | [实测] |
| 9 | `iss208_mech_rebudget_frame_cavity_d15_20` | (b) 已被 ISS-209 的重排交付覆盖 | [实测] MECH/CENTER_CAVITY_RECALC.md: T = d + 3.0 = 18.00/21.00/23.00mm (d=15/18/20), 冲突量 3.20/6.20/8.20mm 与 §1.7.1 C-1 逐字一致; MECH_BUDGET §1.7.1 C-1 + §1.8 指针段; 机器门禁 MECH/cavity_recalc_check.py rc=0 | [实测] |
| 10 | `iss208_mech_recompute_optical_thermal_468mw` | (b) 已被 ISS-209 的重排 + 热学三连交付覆盖 | [实测] ISS-209 已出: 腔体重排 (CENTER_CAVITY_RECALC.md) + 腔体热 C-7 (need iss209_mech_cavity_heat_468mw_vs_50c) + 鼻梁热路径 C-C (need iss209_mech_nose_bridge_heat_path) + X-3 冲突 (need iss209_mech_x3_skin_path_claim); 现行热学判据已落 MECH_BUDGET §1.7 X-3 (腔体 ≤50°C / 面板结温 ≤60°C / ≥0.5W 被动散热面 / 不得密闭腔) | [实测] |
| 11 | `iss209_mech_cavity_rebudget_done` | (b) 闭环完成上报 —— 交付物已落盘 | [实测] MECH/CENTER_CAVITY_RECALC.md + MECH/cavity_recalc_check.py (rc=0, 12 项 + --selftest 9/9) + MECH_BUDGET §1.8 指针段 (既有数字 0 改动) | [实测] |
| 12 | `iss209_mech_splitter_resize_for_eyebox62` | (b) 已被 ISS-219 闭环 (C-6) | [实测] need iss219_mech_m6_splitter_spec_landing (2026-11-16) 原文写明『结构侧给出的新规格 (C-6, 已闭环 need iss209_mech_splitter_resize_for_eyebox62)』: 45° 平板 11×11×1.5 + 转向棱镜 ×2 9×9×5 ⇒ 0.9697cc (工程 0.9915) / W4 3.68-7.36g (工程 3.77-7.53), 整机重量上限 74.0 → 76.13g | [实测] |
| 13 | `iss213_mech_endpoint_thermal_path_metal` | (b) 结论已落结构真源 + 剩余项已拆分到 u8 那条 | [实测] MECH/MECH_BUDGET.md §3/§2.3.1 + mech.yaml interface_claims (mech_endpoint_surface_temp_caliber / mech_mech_budget_linear_0p8w_dead) + MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md: 端件必须金属热路 (打印件 1944 K/W ❌ / 铝 6063-T6 1.935 K/W ✅), R_热路 ≤70 K/W ⇒ 截面积 ≥4.975mm² (2.0×2.0 不合格); ★剩余『端件截面 u8 未定 ⇒ 重量算不出』已转 need iss218_mech_u8_endpoint_section_decide | [实测] |
| 14 | `iss213_mech_mech_budget_charge_caliber_text` | (b) 已被 ISS-216 改完 (文字 + 脚本常量 + 口径自检) | [实测] MECH/MECH_BUDGET.md §2.1 B 行『0.45-0.57 W (代表值 0.50 W) — 耗散 = Pin − Pout + P_DCR (buck 口径)』+ §2.3.1 (皮肤侧 60.0°C / 端件 108.3°C / P_max 0.21W) + MECH/verify_budget.py 的 P_CHARGE = 0.50 + §8 口径自检 C1~C10 (含 C5 = 门禁锚点 0.50W) | [实测] |
| 15 | `iss218_mech_alu_k_201_vs_237` | (b) 已被 ISS-219 改完 (四处文档 + 脚本常量) | [实测] MECH/MECH_BUDGET.md L519『k 口径 (旧口径 237 已订正) → 201 · §2.3.1/§3 ISS-216 注/§5.1/§5.5 四处 + MECH/verify_budget.py 常量 + ENDPOINT_METAL_PATH_MASS_TEMPLATE.md 已统一为 201 W/m·K (Hydro/Aalco/Kaiser 三家互证)』+ verify_budget.py:111 K_AL_6063_T6 = 201.0 (旧 237 只留追溯) | [实测] |
| 16 | `iss229_mech_charge_skin_temp_scope_to_main` | (b) 三个问题都被 V-4 落表回答了 | [实测] HW/netlist_v1.csv L47 已落 680Ω (IIN 0.574A / ICHG 0.698A / 单 pin 0.349A ⇒ 余量 1.43×); ① 充电时皮肤侧 43°C 不再是硬约束 (老板 10-28『边戴边充不允许』⇒ 充电时眼镜不在皮肤上), 但铰链段温升 / TS 停充门限偏差 (390Ω max 36.5mV = 1.13°C) / 单 pin 触点额定三条仍成立; ② V-4 建议默认值已拍 (680Ω) ⇒ DECISION_PENDING_2026-11-16.md §A2 A2 可直接落; ③ 本域 need 里的 47.1°C / 42.1°C 已被 ISS-229 的 §B4.2 订正覆盖 | [实测] |
| 17 | `iss246_mech_handoff_review` | (b) 交卷待复核 —— 交付物已落盘, 无待答项 (复核本身是 main 的动作) | [实测] HANDOFF/2026-11-18_mech-lead_ISS310_板框口径代价对照.md 之前的 ISS-246 交卷单 (6 段: B2 自评 / B3 证据分级 / B4 接口取值 / B5 验收命令原样输出 / B6 边界审计 / 附交卷物清单) + 分片 (frag_write.py 原子写) + merge/gate_check rc=0 Q1 18/18 | [实测] |
| 18 | `iss251_mech_service_port_pad_y_migrate` | (b) 已被 ISS-264 覆盖 —— 三项里两项已迁, 剩下一项已另立 need | [实测] MECH/SERVICE_PORT_ISS092.md 头部 ISS-264 指针: 夹具基准常量已迁 (p2_y=15.00 / s2_y=20.00) + pcb_thk=1.00 已核, 受保护脚本走 H-1 重基线 (md5 9b24bf98… → db58ff6a…); ★【只剩 jd_y0 一项】⇒ 已由 need iss264_mech_jd_y0_and_open_y_caliber / iss264_mech_jd_y0_legal_range_errata_pending / iss267_mech_jd_y0_and_frame_decision 承接 | [实测] |
| 19 | `iss251_mech_demo_truth_gate_red_concurrent` | (b) 并发事件已闭环 —— 该闸现为绿 | [实测] python3 MECH/check_demo_struct_truth.py rc=0 (57 项判据本身没坏) + 板 md5 611b869e13518c3c023fb178f91a0075 / mtime 2026-11-06 07:07:17 逐字节不变 ⇒ 当年『21/23 红』的并发窗口已过 | [实测] |
| 20 | `iss251_mech_owner_decisions_pending` | (b) 5 项已拆到具体 need —— 2 项已定, 3 项另有归属 | [实测] (d) 板长 = 60.00mm 已定 (BOARD_GEOM_30MM §1) ⇒ 归零; (e) 板厚 = 1.00mm (6 层) 已定 ⇒ 归零; (a) d 值 ⇒ need iss209_mech_d_value_decision (决策码 M-B17); (b) u8 ⇒ need iss218_mech_u8_endpoint_section_decide; (c) 集热面材质/面积 ⇒ need iss219_mech_c7_sink_area_confirm + iss222_mech_c7b_sink_is_metal_not_print | [实测] |
| 21 | `iss251_mech_handoff_review` | (b) 交卷待复核 —— 交付物已落盘, 无待答项 | [实测] HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md (B1-B6 六块齐全 + 附 A 三处逐条订正表 + 附 B 并发说明 + 附 C 边界自审) + MECH/check_budget_caliber.py (rc=0 17/17 · --selftest rc=0 13/13) + 分片 (5 artifact + 5 claim + 4 need, frag_write.py 原子写) | [实测] |
| 22 | `iss264_mech_gate_script_md5_rebase` | (b) 三个新 md5 已落进 issue_log 的受保护锚点 | [实测] state/issue_log.yaml 实读: 4ae5827e986f1aebb108c5aa2a475074 / c4bf9151dd59826fb2320c34e8afbd0f / db58ff6a2afc28b8bf517e3c57c56bc1 各命中 6 处 ⇒ 落锚动作已完成 (本单不自签 issue_log, 只是核对结果) | [实测] |
| 23 | `iss271_mech_s6_port_opening_claim` | (b) 认领句已被挂进板那一趟的作业包 | [实测] HW/PCB/BOARD_ONEPASS_WORKPACKET.md §1「三条开口的认领句 (3 条 · 全部可抄进作业包 §3-S6)」+ C-OPEN-1 调试口 (罩 J_DEBUG, 帧 B160x100, 开口 X 137.850..148.050 × Y 54.300..58.900) + C-OPEN-2 检修口 (罩 J_UART, 开口 X 13.790..23.990 × Y 66.300..70.900) + §3-S6 行 B15_SVC_PORT_SPLIT / B16_LED_G_OPTO | [实测] |
| 24 | `iss271_mech_ledg_g5_brightness_gate` | (b) 老板已拍 (2026-11-17 09:49) | [官方] pm.yaml needs_from[boss_g5_led_brightness_20261117].decision: 选项 ② = 改 R 到 20mA 档 ⇒ R_LED_R = 68Ω ±1% (红) / R_LED_G = 55Ω ±1% (绿); 代价: 每颗 2.2mW → 66mW (两颗 ≈0.13W 进电池账) + 亮度 ×14 ⇒ 眼旁光源 IEC 62471 分级要重算; ★另有 boss_dled_g_expose_decision_20261117 一并拍了 U-8 (外露与否) | [官方] |
| 25 | `iss246_mech_continue_verify` | (b) 续做复核已完成 —— 交付物已落盘, 无待答项 | [实测] 交卷单已追加 C-1~C-6 附录 (当期真值 05:07:16) + 门禁 rc=0 23/23 · --selftest rc=0 14/14 · merge rc=0 · gate_check rc=0 (Q1 18/18) + 沙盒反证 绿-红-红-绿 四步留档 4 份; ★本轮复跑 check_demo_struct_truth.py --selftest ⇒ rc=0 (反向用例 28/28 抓到) | [实测] |
| 26 | `iss278_mech_demo_struct_truth_selftest_regression` | (b) 回归已修复 —— 本轮实跑 rc=0 | [实测] 本轮实跑 python3 MECH/check_demo_struct_truth.py --selftest ⇒ rc=0, 反向用例 28/28 抓到 (含 R8/R9/R10/R11a/R11b/R12 六条台账链头用例) + 主跑 rc=0; 板 md5 611b869e13518c3c023fb178f91a0075 与 mtime 2026-11-06 07:07:17 逐字节不变 ⇒ 『板只改一次』铁律未破 | [实测] |
| 27 | `iss278_mech_to_hw_board_inputs` | (b) 已转出 —— 不再由 mech-lead 追 | [官方] 本条正文自述: 『已转出 · 2026-11-17 · main 16:0x 已转 hw-lead 的 ISS-292 任务书「⑬ 追加」节 · pm.yaml 已回写答案 ⇒ 本条不再由 mech-lead 追; 其中 E-1~E-5 归 hw-lead 的 ISS-292, E-6 的 MECH 半边已由 ISS-294 (mech-lead) 接手并交卷』 | [官方] |
| 28 | `iss296_mech_iss294_opening_status_need` | (b) 状态已写清 —— 本单交卷页 §7 已把这条 need 的现状写全 | [实测] J_USB_C 边开口几何已算完 (帧 B160x100): 边开口 X 132.995..147.005 × Y 0.000..7.300 (宽 14.010 深 7.300) + 必须清空区 X 133.895..146.105 × Y 0.000..6.400 + 单边净距 X/Y 0.900 ⇒ 最坏 0.600 = CRIT 刚好过 + 座体真实高 h 仍 [0数据] ⇒ 开口最终尺寸 + Z 向窗口仍是 main→boss 拍板项 (已在 MECH/BOARD_ONEPASS_MECH_SYNC.md §10.1 落笔) | [实测] |
| 29 | `iss203_mech_claim_mainboard_len_carrier_direct` | (b) 已被同批更晚的升级条取代 | [实测] need iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice (2026-11-15) 把同一件事升级给老板 (pm.yaml 已有该 key 的 to=boss 待拍项, DECISION_INDEX #31 剩 0 天) ⇒ 旧条 (2026-11-12) 不再单独追; ★两条 claim 的 value 已在 ISS-206 保持 69/76 不改 + 补注『这是 A/B 互斥方案的板长, 不是现行板板长』 | [实测] |
| 30 | `iss229_hw_landing_must_sync_mech_anchor_iss233` | (b) 该次实例已闭环 —— 规则已另立常驻条 | [实测] 事件已闭环: 2026-11-16 06:48:38 ISS-233 第 3 批改网表 L442 + 脚表 L531 ⇒ 本域已按 H-1 把 MECH 锚点跟到 (网表 34132f7e40a241e1fae1476be0eafbd5 / 脚表 b21b743a7702d30729f0d653c15392df, by=ISS-233) ⇒ 门禁回 rc=0 (23/23); ★常驻规则由 need iss224_hw_landing_must_update_gate_ledger 承接 | [实测] |
| 31 | `iss218_mech_pa_cf_shrinkage_density_feedback` | (b) 自查部分已尽 + 剩余实物回填已挂到打印执行方那条 | [实测] 补偿公式已在册 (Bambu 官网公式 补偿% = (实测/设计) × 100, 随件试样自带 3 个标定方块 5/10/20, 前置 = PA-CF 必须 80~90℃/8~12h 干料否则数据不可比) + 密度按 1.18 g/cc 占位记账 (标签已标 [0数据-占位], 只用于净重差粗算, 不进 §3 合计) + 加工厂表面粗糙度 Ra 已降级为功能性要求 (开口两对边无刀痕阶梯 / 锐边倒钝 R0.2 / 去毛刺); ★剩余『打印方量完回填』已挂在 need boss_local_print_measure (决策码 M-B1) / iss017_local_print_measure_unblock (M-B12) 上 ⇒ 本条不再单独追外部 | [实测]/[推算] |

### §5.2 (c) 真·待答 ⇒ 保留 51 条

| # | need key | owner | 处理方式 | 一句话问法 (★给 main 的一行 need★) | 板那一趟? |
|---|---|---|---|---|---|
| 1 | `soc_carrier_mainboard_site` | main → boss (A/B 方案取舍) | 主板位 + 载板化方案取舍是老板级; 同一问题已由 pm.yaml 的 iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice (DECISION_INDEX #31, 剩 0 天) 升级给老板 ⇒ 本域不重复问, 只跟结果 | main: 主板位 (镜脚 / 镜框) + A/B 载板化取舍的老板裁决已在 DECISION_INDEX #31 挂着 ⇒ 出结果后回本域一句即可 (结构结论全部随它变) | 否 |
| 2 | `u8_frame_section_carrier` | main (端件截面 u8 排期) | u8 是端件热路 / 框侧汇流 / 装配顺序三条链的共同前置; 已有专门条目 (iss218_mech_u8_endpoint_section_decide + iss089_frame_section_u8_block) | main: u8 端件截面请排期拍 (本域已备好重量账模板 MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md, 五档情景 A/B/C) —— 它同时卡端件金属热路重量与框侧汇流 | 否 |
| 3 | `iss089_frame_section_u8_block` | main (与 u8 同一条) | 本条是『把 u8 提到阻塞级』的提级请求; u8 的实际排期条目是 iss218_mech_u8_endpoint_section_decide | main: u8 提为阻塞级的动作 = 把 iss218_mech_u8_endpoint_section_decide 排进板那一趟之前; 本域不再另问 | 否 |
| 4 | `iss089_decision_stack_correction` | main (DECISIONS.md 是项目总工地界) | ★本条建议的替换值 31.00mm 本身也已过期 —— 现行真值是 25.30mm (整机) / 5.00mm (demo) ⇒ 要改就得改到新值, 不能改到 31.00 | main: DECISIONS.md 2026-10-27 那条『铰链区堆叠仍 26.5mm (余 10.5mm)』已过期 —— ★但本条当年建议的替换值 31.00mm 也不是现行值: 现行 = 25.30mm (整机) / 5.00mm (demo), 出处 MECH/HINGE_FPC_GEOMETRY_TRUTH.md T1/T2 + MECH/USB_HINGE_STRUCTURE.md §9 ⇒ 请按新值改, 别按 31.00 改 | 否 |
| 5 | `proto_pcb_freeze_gate` | main (排期) + 板那一趟 | 板框/厚度/层数/孔位冻结闸: 板厚与层数已定 (1.00mm / 6 层), 板框仍在拍 (U-1) ⇒ 闸还没满足; 老板 11-17 00:43『接下来的目标是绘制 PCB 图』⇒ 板只改一次 ⇒ 冻结闸是这一趟的第一前置 | main: 板框冻结闸还差 U-1 (板框三选一: B160x100 / F30A / P60x15) ⇒ 板只改一次那一趟开工前必须先冻结 (板厚 1.00/6 层与 PIN-SET-2 套 A 已定) | ★是★ |
| 6 | `iss121_magnet_cover_y_wall_decision` | main (结构取舍) | 盖板 Y 向壁厚缺 0.40mm 是真冲突, 三个选项各有代价; 三个选项的成本还没算完 | main: 检修口盖板 Y 向壁厚缺 0.40mm 请裁 —— ① 盖板 Y 7.60→8.60 (+0.02g/侧) ② 磁铁改 ⌀3.0 (吸力降) ③ 承认该处壁厚要求可降 (ISS-092 C-8『磁铁不承结构力』⇒ 需拉脱实测); 本域默认假设 = ③ | ★是★ |
| 7 | `iss092_magnet_soc_gap_correct` | main (PM 授权改 ISS-092 正文) | MECH/SERVICE_PORT_ISS092.md 是已 verified 的文件, 本轮边界只许交新文件 ⇒ 正文里那两处 68.30mm 只能由 main 授权后改 | main: 请准许把 MECH/SERVICE_PORT_ISS092.md 里『磁铁↔SoC 间距 ≥68mm』两处订正为 28.00mm (坐标混算作废) 并把『对 SoC 大概率无影响』的依据强度降级 (28mm 够不够取决于 SoC 磁敏感度 = [0数据]); 同一文档 §11 I-2/I-3/I-4 三条默认假设已生效 | 否 |
| 8 | `proto_b1_split_coupon` | main (B1 批次排期) | 拆两段是排期建议 (B1a 纯 coupon 34 项 / B1b 板相关项), 不是结构结论 | main: B1 拆两段请拍 (B1a = 纯 coupon 34 项工艺标定, 完全不依赖 PCB 冻结 ⇒ ISS-040 打印执行方一有着落就能开; B1b = 板相关项, 必须等 PCB 冻结) ⇒ 本域建议按拆两段执行, B1a 先开 | ★是★ |
| 9 | `mech_iss127_temple_split` | main → boss (架构裁) | 镜腿壳体改 H 向分型 (皮肤盖 + 内胆) 是架构级; P1 已被本域算完并推荐, 只差这一刀 | main→boss: 镜腿壳体改 H 向分型 (皮肤盖 + 内胆) 是否接受? P1 收益: 链① 三档 α 全过 0.40 (0.750/0.736/0.722/0.708) + 链② 四档全过 + 重量净减 0.38g/对; 代价: 零件 24→26 件 + 模具 2 套/侧 + 外观多一条分型线 (贴肤面可零斜度) + 皮肤盖加强筋 +0.15~0.25g/对; 备选 P2 (局部 H 向分型) 会让链② 破线 0.190 < 0.40 | ★是★ |
| 10 | `mech_iss127_graphite_cut` | main (预算裁) | 石墨裁剪是重量预算裁剪, 骨架 4.08g/对 的超支另算 (本条不动) | main: 石墨按【只铺 SoC 段 + X 向逃线带 5.00/边】裁剪是否确认? 收益 = 石墨 2.16g/对 → 0.98g/对 (净减 0.38g/对), 依据 = 30mm 板宽下骨架候选 C 的 SoC 段满宽 30.00, 横向扩散已被满宽铝骨架覆盖 | ★是★ |
| 11 | `mech_iss127_graphite_in_hchain` | main + hw-lead | 挤占 vs 叠加 是链② 的口径钉子, 两条文档不一致, 必须有一句裁定 | main+hw-lead: 石墨在链② (PCB/骨架堆叠 H 链) 里是【挤占】那 0.30 空气隙还是【叠加】在 4.40 之外? 本域按叠加 (保守) 算 ⇒ 链② 在 α=1.5° + 含石墨 + 板厚 1.22 时最坏 0.190 < 0.40 破线; 按挤占则 0.490 ✅ —— 请钉一句 (注: P1 H 向分型下链② 脱模项=0 ⇒ 四档全过) | ★是★ |
| 12 | `iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` | main → boss | A/B 互斥方案的取舍是老板级; 老板已把『P7/P8 用哪块板』拍了 (选项 A = 改现役 160×100 台架板), 但这条问的是【claim 算现行板长还是历史方案对照】, 还没答 | main→boss: 这两条 claim (mainboard_len_carrier=69mm / mainboard_len_direct=76mm) 算『现行板长』还是『历史方案对照’? 建议按『历史方案对照』保留并补注 (value 不改) —— 现行板长是 60.00mm; 老板 11-17 已拍 P7/P8 = 改现役 160×100 台架板, 若 A/B 方案随之作废则这两条整体标作废 | 否 |
| 13 | `iss134_mech_boss_decide_waveguide_vendor_and_fov` | main → boss | 波导归属 + FOV 目标是老板级; 公开波导只有 20-30°(D) vs 我们 D3 口径 120° 对角, 差一个量级 ⇒ 必须一起拍 | main→boss: 波导归属 (A 舜宇奥来 / B 瑞声×Dispelix / C JBD 刻蚀) + FOV 目标一起拍 —— 本域建议按 B 的公开几何做镜框参数化占位 (卡槽 + 可换压框), A 或 C 到货只重做压框; ★FOV 必须在占位件之前定 (耦入/耦出角可调), 否则重演 11-02 方案变了全部重算 | ★是★ |
| 14 | `iss134_mech_reassign_iss004_013_016_048` | main (issue_log 地界) | issue 状态与 owner 是项目总工的活, 我一笔没动 state/issue_log.yaml ⇒ 只报不改 | main: 请按 ISS-134 的建议重排 4 条 issue 的 owner/状态 (ISS-016 走鹃Ⅱ 长宽高 → closed 因 11-02 换型作废; ISS-048 光生物安全 → owner 改 mech-lead 按 V2 判据表闭环; ISS-004 波导未选型 → owner 改 pm/mech-lead 并改成『等老板拍归属 + 参数化占位』; ISS-013 → note 改成『缺几何数据 + 用参数化占位与可换压框绕开』), 并连带改 MECH/PROTOTYPE_PLAN.md B3 的开工前置 (JBD 回 u1+u4 之前镜框不开工) | 否 |
| 15 | `iss134_mech_archive_jbd_question_list` | main (根目录文件地界) | JBD_QUESTION_LIST.md 在项目根目录, 属 main 地界; 且按老板 11-11 19:31 + 11-12 02:02 不再发信 ⇒ 那批问项已全部作废 | main: 请把根目录 JBD_QUESTION_LIST.md 归档为历史件 (走鹃Ⅱ 出瞳/波长/光通量/MTF/光生物安全 已随 11-02 换型作废; 波导交 JBD 推荐那条已被公开采购路线取代); 同批 state/outbox/ 下的 jbd_query.md / jbd_query_addendum.md / visionox_display_inquiry.md / visionox_display_dsc_mode_query.md 我一律不发只留档 | 否 |
| 16 | `iss208_mech_waveguide_eyebox_le_62mm2_gate` | main → boss (与波导归属一起拍) | 眼盒面积是选型前置条件, 不是结果; 老板拍波导时必须一起拍, 否则选回来的波导一定超限 | main→boss: 眼盒面积 A_e <= 62mm² (入眼 2000 cd/m², V2 C-4/C-5) 必须作为波导【选型前置条件】一起拍 —— 公开在售波导标称眼盒全部超限 (12×10=120mm² 超 1.94× / 15×10=150mm² 超 2.42×) ⇒ 且『出瞳 4mm』≠ 眼盒面积 (A_e 的厂商定义式公开查不到 ⇒ 要求供方按 V2 §3 ⑥ 定义式给 A_e) | ★是★ |
| 17 | `iss208_main_fix_v2_section_refs` | main (判据文件地界) | 改判据文件 (DISPLAY_BIOSAFETY_CRITERIA_V2.md) 是项目总工的活, 我一字没改 (md5 96239070dc7c0ec00edb1b758a698769) | main: DISPLAY_BIOSAFETY_CRITERIA_V2.md 的节号自指对不上 (C-4 写『出处 3.5 (式 5/6/7)』、① 写『本文 3.7』, 而该文件 3 实际只有 ①~⑥) ⇒ 请统一改成 3 ⑤-b / 3 ⑥ / 3 ③-c; ★不影响任何阈值 (62mm²/1500/4000/50°C/60°C/15-20mm/0.011rad/0.1234 全部照抄无误), 只影响检索 | 否 |
| 18 | `iss209_mech_cavity_heat_468mw_vs_50c` | main (与 u8/集热面一起裁) | 腔体 81.20/77.43/75.24°C vs 50°C 红线是硬冲突, 加厚救不了 (只贡献 6.4%-11.5% 面积) ⇒ 必须走金属热路 | main: 面板 468mW 放正中区 ⇒ 腔体 81.20/77.43/75.24°C (d=15/18/20) vs 50°C 红线, 保 50°C 需被动散热面 ≈4668.9mm² (u8 未定值的 4.67 倍) ⇒ 腔体散热不能靠加厚, 必须金属热路导到铰链侧/端件 (≥0.5W 被动散热面 + 不得密闭腔) —— 请与 u8 + 集热面材质一起裁 | 否 |
| 19 | `iss209_mech_nose_bridge_heat_path` | main (结构论据已给, 待认可) | 量化已给完, 剩下的是『PCB 不进镜框正中』这条论据要不要写进锁死链 | main: 鼻梁区热路径量化: 节点→鼻梁接触面 12.0mm / R_bridge=400K/W, SoC 0.55W + 面板 0.468W = 1.018W 进镜框 ⇒ 鼻梁接触面 54.33/52.75/51.83°C (d=15/18/20) ⇒ 对 43°C 余量 -11.33/-9.75/-8.83°C; 加鼻梁侧热断 (R=1000) 仍 43.74/43.03/42.61°C ⇒ 加厚救不了 ⇒ 结构侧论据 = PCB 不进镜框正中 (与 ISS-065 §2.4 同向), 请认可 | 否 |
| 20 | `iss209_mech_x3_skin_path_claim` | main (判据措辞裁决) | X-3 那句话在现行 468mW 功耗下不成立 ⇒ 要么加限定语, 要么补热断要求; 这是判据措辞, 归 main | main: MECH_BUDGET §1.7 X-3『光学件在镜框, 不进皮肤热路径』在 468mW 面板下不成立 (仅面板就让鼻梁接触面到 43.89/43.16/42.74°C, d=15/18 档已破 43°C 红线 0.89/0.16°C) ⇒ 请裁: 加限定语还是补『鼻梁侧热断 >=454.8 K/W』要求 (本单未改该行一个字) | 否 |
| 21 | `iss213_mech_cross_domain_to_main` | main (派给对应总工) | 跨域条目汇总: ① ② 已被 hw-lead 答复 (iss089_p9_topology_and_stack / iss089_chg_led_board_column 均已被答), ③ ICHG 系数已被 ISS-229 解决 ⇒ 剩下的仍要 main 派 | main: ISS-213 跨域汇总里 ① PIN-MISMATCH/STK-P9/TOPO-3 与 ② NET-LED 已由 hw-lead 答复、③ THM-RATIO 已由 ISS-229 解决 ⇒ 剩下条目请按本条正文继续派给对应总工 (结构侧对 ① 的建议已写明: 拓扑按 H 向径向嵌套, 堆叠按触点区 27.00 / FPC 带宽 35.50 两口径分列) | ★是★ |
| 22 | `iss213_mech_iss126_premise_superseded` | main (issue_log 地界) | ISS-126 的 open 状态与解锁条件是 main 的活; 本域只给『前提已超越』的证据 | main: ISS-126 的前提已被现口径超越 —— 现行板厚 = 1.00mm (6 层) (MECH/BOARD_GEOM_30MM §1 + service_port_check.py BASE pcb_thk=1.00, 注释『6 层现行; 4 层 0.80 已作废』) ⇒ 检修口盖板内腔 = 7.30 − 2.60 = 4.70mm >= cavity_req 4.50 ✅ 余 0.20 (实跑 54/54 OK / FAIL 0) ⇒ 『只有 0.80 及以下才安全』不成立 ⇒ 请裁关闭 (或改写为『板厚若改到 1.22 档才需重开』) | ★是★ |
| 23 | `iss213_mech_typec_third_candidate` | main → boss (开口尺寸) | 第三档几何已出且试样已落, 但『产品件走 FDM 直成型还是金属嵌件』是产品决策 | main→boss: Type-C 开口第三档已出 (FDM 直成型 10.50×4.80 / 金属嵌件 CNC ±0.05 10.25×4.55, 最坏单边 0.63/0.62 ✅, 端件面板最小外形 13.50×7.80 含承力壁 ≥1.50) ⇒ 该特征不得靠打印面成型 ⇒ 请拍: 产品件走 FDM 直成型还是金属嵌件 (两档都合格, 是工艺路线决策) + 开口圆角 R; ★下游两件要排期: HW/CHARGE_BOARD_SPEC.md M-15 的名义+公差 (hw-lead) + 打印包加第三档试样 | ★是★ |
| 24 | `iss213_mech_pcb_class_6_queued` | main (随整链重出) | 6 个 PCB 类 id / 7 行 FAIL 按老板 11-11 10:07『PCB 布线/布局类一律不派, 排队等原理图定稿』⇒ 保持 FAIL 是正确状态; 只差『挂到哪一单』 | main: 6 个 PCB 类 id (STK-FANOUT / PCB-X-GAP / MRG-54P / MRG-X-4 / MRG-X-3 ×2 / FRM-SUM) 的重算挂到哪一单? 恢复条件已逐条写在 MECH/hw_cross_review_check.py 的说明里 (原理图 P9 定稿给 4 条 FPC 实际落点与拓扑 ⇒ 复算 FPC 带宽合计 ≤ 板宽 30.00 − 0.60) ⇒ 建议随整链重出; ★本单一字没碰它, 分布未变 (PASS 14 / FAIL 17 / 条件通过 8 / 说明 15) | ★是★ |
| 25 | `iss216_mech_endpoint_metal_path_mass_after_u8` | main (与 u8 同批) | 金属热路的重量代价必须等 u8; 本域已把硬指标落定 (R_热路 ≤70 K/W ⇒ A ≥4.975mm²) | main: 端件金属热路的重量代价等 u8 落定后回算 —— 本域先落硬指标: R_热路 ≤70 K/W (60°C 端件判据下 0.50W ⇒ ΔT ≤35K); 铝 6063-T6 同几何 1.935 K/W ✅ / 打印件 1944 K/W ❌ ⇒ 热路必须是铝/铜件; ★§3 逐件 0 改动, 不预扣不猜数 ⇒ 请把 u8 排期与打印包第三档试样一起排 | 否 |
| 26 | `iss218_mech_tier3_coupon_print_and_measure` | main (打印/切片/量测执行方) | 试样已落成, 只差实物; 执行方归 boss 侧那条 | main: Type-C 第三档试样已落成 (frame_typec_coupon_tier3_revb.stl, 72.0×32.0×5.0mm, 可直接下片) + 门禁 (余量对拍 4/4 + MECH_ANCHORS 7/7 + 反向用例 8/8) ⇒ 现在只差实物: 打印 + 切片 + 量测三项执行方 (本机跨网段不可达/无切片器/无量具) ⇒ 回填口径 = MECH/print/MEASURE_CHECKLIST.md N1~N27 (总 116 项) 填 state/measurements.yaml 的 M-PRINT (kind 必须写 实测) + MECH_BUDGET §5.4 的 FDM 孔径收缩/公差行; ★放行闸 = N23~N26 (装母座后单边塞尺 ≥0.60) | ★是★ |
| 27 | `iss218_mech_u8_endpoint_section_decide` | main (u8 拍板) | u8 是端件热路/框侧汇流/装配顺序三条链的共同前置; 本域已备好重量账模板 | main: 端件截面 u8 请排期拍 (本域已把重量账模板备好: u8∈{30,33,35,38,40} × 表A 整条端件金属化 11.3~22.7g (比 W9 本身还重 ⇒ 不可接受) / 表B 半高 5.7~11.3g / 表C 局部热桥 0.95~5.67g (推荐 3.0×3.0=1.70g)); ★新算出一条硬下限: R_热路 ≤70K/W ⇒ A ≥4.98mm² ⇒ 2.0×2.0 铝条也不合格 (R=87.1 K/W) | 否 |
| 28 | `iss238_mech_marker_policy_decision` | main (判据口径) | 判据本体的放宽要走 H-1 重基线, 顺序不许倒; 本域推荐 P3 (判据本体零改动) | main: 作废标注的判据口径三选一 —— P1 regex (已作废 + 日期或 ISS 号) / P2 四选一 (漏检风险最高, 不推荐) / P3 维持单串 + 新增形态同步进清单 (★本域推荐★ ⇒ 判据本体零改动, 不用走 H-1); ★底线不许破: 放宽的只是『什么算作废标注』, 裸走鹃命中必须仍然是红; 另: 要不要把 python3 MECH/check_zoujuan_marker_consistency.py 挂进 state/daily_check.py? (实测 grep -n display_biosafety state/daily_check.py ⇒ 0 命中 ⇒ 巡检仍看不见) | 否 |
| 29 | `iss240_mech_hinge_fpc_truth_decisions` | main (三处拍板) | 跨铰链 FPC 几何收口三处要 main 拍; 改判据要 H-1 重基线, 本单不许碰 | main: 跨铰链 FPC 三处请拍 —— (a) 旧 claim mech_hinge_stack_fixed_mm=25.00 与 G7/C9 字面判据怎么处置? 三档 (a) 改成 demo 口径 J_CHG 单链 (高度 5.00/径向 3.35) 丢留痕 / (b) 保留 25.00 但标明=整机阶段旧架构口径 demo 不适用 / (c) 拆 claim key (本域倾向 c); (b) hinge_usb_check.py 的 CROSS_LINKS 4 条 (CONN_USB 网表 0 命中) 与 ffc_pitch_mm 一律 0.5mm 怎么改? 建议按 board 栏取 (board==HINGE 才算跨铰链); (c) claim mech_hinge_links_count=0(demo) 与 mech_hinge_radial_mm=4.40 / mech_hinge_stack_declared_mm=49.62 三个旧 key 是否按 demo 口径清理 | 否 |
| 30 | `iss222_mech_c7b_sink_is_metal_not_print` | main (与 u8/集热面一起裁) | C-7b 改变了 C-7 的解法 (打印件顶面不能当集热面) ⇒ 集热面材质必须一起裁 | main: C-7b 已算出: 打印件 PA-CF 沿上沿方向热阻 3610 K/W ⇒ 顶面有效热导 R=398.9 K/W (比同面积直接对流差 8.4 倍) ⇒ 实算腔体 53.60°C ❌ (超 50°C 红线 3.60°C) ⇒ ★铝制集热背板 120×30×1.0 不是可选降级, 是 P3 成立的必要条件 (装上 47.77°C @0.468W / 48.65 @0.50W ✅, P_max 0.5496W, +9.72g = 2.70 mg/mm²); 端件整条金属化 11.34-22.68g 换 600-800mm² = 14.18-37.80 mg/mm² (贵 5.3-14.0 倍且面积仍差 3-7 倍) ⇒ 不可接受 ⇒ 请裁集热面做成什么材质 | 否 |
| 31 | `iss219_mech_c8_ts_axis_caliber` | main (三选一) | 分光件轴向口径不自洽, 三档全废 ⇒ 要么改口径, 要么给构型, 要么走并排化 | main: §1.4.5 的 t_s=6.0mm 与平板几何在旧口径下就已不自洽 (45° 平板必须覆盖整个光束直径 ⇒ 竖向投影 >= 光束直径) ⇒ 修正后器件区 15.8/16.8 ⇒ 可动余量 -3.8/-0.8/+1.2 (旧) 与 -4.8/-1.8/+0.2 (新) ⇒ 三档全废 (d=20 余 0.2 < 判据 0.60) ⇒ 三条出路请裁: (a) t_s 改按平板竖向投影重算 ⇒ ISS-209 候选 1 器件区并排化 从推荐升级为必须 (b) 给分光件竖向压缩构型 (c) 走并排化 (耦合光学与分光件转向 90° 并排) | 否 |
| 32 | `iss219_mech_c7_sink_area_confirm` | main (镜框上沿可外露面积) | 集热面面积能不能做到 3600mm² 是 C-7 的唯一前置 | main: 镜框上沿可外露集热面能不能做到 120×30 = 3600mm² (波导压框/摄像头/装饰件会遮)? 做不到 ⇒ 降级: (a) 铝制集热背板 120×30×1.0 顶上沿外侧把面积做出来 (+9.72g) (b) 扩到镜框顶面 + 铰链上盖两处并联 (+800-1200mm²) (c) 面板功耗降到 ≤0.415W (P3 的 P_max=0.604W ⇒ 468mW 只余 +29%) (d) 改整机形态 | 否 |
| 33 | `iss219_mech_m6_splitter_spec_landing` | main (§1.3 M6 落地) | §1.3 M6 现行值是按走鹃Ⅱ 2.9mm 光束定的, 与眼盒 ≤62mm² 不自洽 ⇒ 换不换要拍 | main: 请裁 §1.3 M6 的落地 —— 现行 14×10×6 / 0.79cc / W4 3-6g 按走鹃Ⅱ 2.9mm 光束定, 与 X-1 的 62mm² 眼盒不自洽; 结构侧新规格 (C-6, 已闭环 iss209_mech_splitter_resize_for_eyebox62) = 45° 平板 11×11×1.5 + 转向棱镜 ×2 9×9×5 ⇒ 0.9697cc (工程 0.9915) / W4 3.68-7.36g (工程 3.77-7.53), 腔体占位要放大; 连带整机重量上限 74.0 → 76.13g | 否 |
| 34 | `iss224_hw_landing_must_update_gate_ledger` | hw-lead (常驻规则) | 常驻规则: 每次落表要同步 MECH 侧锚点, 否则 MECH 闸假红 | hw-lead: 每次改 HW/netlist_v1.csv 或 HW/netlist_v1_pins.csv 都必须同步 MECH 侧锚点 (MECH/HW_CROSS_REVIEW_TRIAGE.md §1 source_ledger.entries 的 md5/prev_md5/by/landed_at 四个字段), 且落表记录里必须能查到【落表单号 + 文件名 + 新 md5 + 旧 md5】四项 ⇒ 门禁 C21 逐项对账; ★只改锚点不落表 = 悄悄换真源, 只落表不改锚点 = 门禁假红 | ★是★ |
| 35 | `iss229_mech_hw_pcb_outline_old_charge_numbers` | hw-lead (经项目总工) | HW 文档三处仍带 0.822 旧系数; 我不许代改 HW 地界 | hw-lead: 请把 HW/PCB_OUTLINE_60x15.md 的三处旧系数数改掉 —— ①§3.4 表 ICHG/单 pin/余量: 390Ω 0.82A→1.216A / 0.411A→0.608A / ✅→❌超 0.5A 21.6%; 470Ω 0.68A→1.009A / 0.341A→0.505A / ✅→❌超 1.0%; 680Ω 0.47A→0.697A / 0.236A→0.349A / ✅余量 1.43×; 300Ω 0.534A→0.790A ②L149 充电时间 ~29.20min→~19.7min (典型 32.08→21.7min) ③§4.2 O-4 TS 参考地抬高 14-32mV=0.44-0.99°C → 390Ω max 36.5mV=1.13°C (留 1°C 裕量只在 680Ω/1.2kΩ 成立) | ★是★ |
| 36 | `iss229_mech_sw_evt_pwr05_charge_current_criterion` | sw-lead | SW 的 PWR-05 判据量的是哪个电流, 只有 sw-lead 能定 | sw-lead: 请复核 SW/EVT_TEMPLATE.md PWR-05『充电电流 ≥1.5A @5V/2A 适配器』量的是输入电流 IIN 还是电池侧电流 ICHG —— 改正系数 1.216 下 max 档电池侧 = 390Ω 1.216A / 680Ω 0.697A / 1.2kΩ 0.395A (连现行 V-4 候选 680Ω 也只有 0.697A ⇒ 1.5A 达不到); 若量的是 IIN, 390Ω max 1.00A / 680Ω 0.574A ⇒ 同样达不到; ★该不兼容在旧 0.822 系数下就已存在 (390Ω max = 0.822A) ⇒ 属既存判据, 不是 ISS-229 造成的 | ★是★ |
| 37 | `iss222_mech_print_pack_optical_cage_md5` | main (PROJECT_TRACKER 是项目总工地界) | 打印包禁改项因走鹃Ⅱ 作废而解冻, STL 已重生, 但台账登记值还没更新 | main: 请把 PROJECT_TRACKER.md 里 optical_cage_TEMPLATE.stl 的登记 md5 从 6f23c2e2f52e81060e5c0bbecb4cc881 更新成 537dc6afb4246cce30aa6853de7cebd1 (ISS-222 已按新规格重生: 分光件座 14×6×10 → 7.78×8.84×11.0; 其余 6 个 STL 逐字节未变) | ★是★ |
| 38 | `iss264_mech_jd_y0_and_open_y_caliber` | main + hw-lead | jd_y0 (J_DEBUG 焊盘阵列 Y 起点) 是所有检修口 Y 向数的总开关, 未定则开口 Y / P-5 最近距离全部悬着 | main+hw-lead: 请给 30mm 板上 J_DEBUG 阵列真实起点 jd_y0 (合法区间 [1.665, 11.730], 现状 9.50) ⇒ 定了它, 开口 Y (现 7.835..12.435) 与 P-5 最近距离 (P2 3.23mm / S2 8.53mm) 一次算清; ★候选 A 9.50 / C 10.00~11.00 (B 不可用), 且须与落表 1x4 vs 脚本 2x5 的脚数一起定 (差 0.635mm) | ★是★ |
| 39 | `iss264_mech_jd_y0_legal_range_errata_pending` | main | 两件要 main 拍/改: 决策页 A 段的 jd_y0 区间订正 + 检查项 2.5 的 Y 上限是否按 30mm 板口径放宽 | main: 请拍两件 —— ① 决策页 A 段把『jd_y0 合法区间』改成订正后的 [1.665, 11.730] mm, 并把『按相对位置迁 ⇒ 孔与焊盘阵列重叠 12.37mm』改写成『检查项 2.5 判红 (焊盘上沿 25.77 > 13.00, 余量 -12.77mm)』(P-5 3.23/8.53 与开口 Y 7.835..12.435 不变) ② 检查项 2.5 的 Y 上限 13.00 要不要按 30mm 板口径订正为 28.00 (订正 ⇒ 区间上界 11.73→26.73, 候选表整张重算, jd_y0=24.50 几何上变可行但治具/探针对位前提要重谈; 不订正 ⇒ 维持最保守窄带, 候选只有 A 9.50 / C 10.00~11.00) | ★是★ |
| 40 | `iss267_mech_jd_y0_and_frame_decision` | main (板框三选一) → boss | 板框三套并存 + jd_y0 两拍合并; 板框 = 老板拍, main 汇总 | main: 板框口径三选一请汇总后交老板 (① B160x100 台架板 160×100 ② F30A 产品板 60×30 套A ③ P60x15 60×15) —— 结构侧已给 36 档机器可行域表 (MECH/board_frame_feasibility.py) + 两条路线代价 (MECH/BOARD_FRAME_DECISION_INPUT.md §C): ① 36 档全红 (V链-68.00 / L链-85.50, 与板厚无关) 且板本身 47.36g = 整机质量预算 65~97% ⇒ 不得宣称可投产; ② 板厚 0.80/1.00 两档全绿 (开口可一次带完) 但 S6 20 落位 + 三条开口 + 座体 6 组 + 9 道钉板闸 + MECH 6 闸 + 帧表 + 叠层阻抗 + 骨架截面 都要重算重锚且 P7 布通未验证 ⇒ 建议先拍框再拍板厚再拍层数最后 P7 | ★是★ |
| 41 | `iss267_mech_debug_part_model` | hw-lead | J_DEBUG 脚数与座体高度是结构开口尺寸的输入, 落表与结构模型不一致 | hw-lead: 请定 J_DEBUG 的脚数与座体真实高度 —— 落表是 1×4 (HW/BOM_v1.csv:71 + HW/netlist_v1_pins.csv:202-205) 而 MECH/service_port_check.py 按 2×5 (10 脚 Cortex-10) 算 ⇒ 必须清空区 X 宽 7.62 与开口 X 10.20 要重算; 另 J_UART 相对位置: 盘上板 J_DEBUG@(144.30,58.00) 与 J_UART@(20.74,70.00) 相距 123.6mm 而结构模型让它们紧邻 ⇒ 开口 X 49.21..59.41 在盘上板不成立; 座体真实高 2.54 是假设 ⇒ 开口 Y 宽 4.60 / 单边 1.03 全部依赖它 ⇒ [0数据] | ★是★ |
| 42 | `iss271_mech_s6_ledg_window` | hw-lead (板那一趟坐标空间) | 板侧落位坐标已算好, 等 hw-lead 在板那一趟用; 但脚数与 J_UART 相对位置还没定 | hw-lead: 板侧坐标空间可直接用 —— (1) 检修口/调试口: Y 向 jd_y0 ∈ [1.665, 11.730] (现状 9.50), X 向 jd_x0 ∈ [48.290, 51.090] (2×5) 或 [48.925, 51.725] (落表 1×4), 开口 X 可放行区间 [47.00, 60.00], 必须清空区 X 50.50..58.12 × Y jd_y0±1.27, 开口 10.20×4.60, 单边间隙 X 1.29 / Y 1.03; ★脚数与 jd_x0 必须一起定 (差 0.635mm) (2) D_LED_G 落位窗口 (60×30 套A 板坐标): 可放行矩形 18 块, 全高可用 X 带 3 条 (X 3.00..6.40 / X 9.60..14.20 / ★X 33.00..47.71 宽 14.71 = 首选窗口★) × Y 1.60..28.40 | ★是★ |
| 43 | `iss276_mech_s6_claim_frame_align` | hw-lead | 帧 id 与坐标基准必须两边一致, 不一致就停手 | hw-lead: 请与 HW/PCB/BOARD_FRAME_CALIBER.md (ISS-274 同批产出) 的帧声明对齐后再收进 §3-S6 —— 三条具体: ①调试口开口 = X 137.850..148.050 × Y 54.300..58.900 (帧 B160x100), 左下角可放行 X0 ∈ [137.850, 142.063] · Y0 ∈ [54.300, 55.330] ②UART 检修口开口 = X 13.790..23.990 × Y 66.300..70.900, 左下角可放行 X0 ∈ [13.790, 17.620] · Y0 ∈ [66.300, 67.330] ③★S6 必须拆成两条: J_DEBUG (144.30,58.00) 与 J_UART (20.74,70.00) ΔX = 123.56mm ⇒ 一个开口罩不住两个 ⇒『必须清空区 7.62×2.54』是 60×30 套A 的并排模型, 在本帧不成立, 不得抄★ | ★是★ |
| 44 | `iss296_mech_m3_nine_gates_green_need` | main (写进板那一趟作业包) | 9 道钉板 md5 闸要收工当天同一次全绿, 这句话必须写进作业包 | main: 请把『9 道钉板 md5 闸 ①~⑨ 收工当天必须同一次全绿』写进板那一趟的作业包 —— 机器清单 state/board_md5_pinned_gates.json 实测 9/9 全是『已有 reboard 通道』(HW 6 道由 ISS-297 建好, 本单已把 M3 表那 6 个单元格由『待建』订正为『已建 (ISS-297)』并留痕); ★第 5 道 HW/check_pin_function_labels.py 主模式仍 rc=1 (18 条 ISS-257 起的既有缺陷, 属别单范畴) ⇒ 那一道的前置债在 hw-lead 那边 | ★是★ |
| 45 | `iss296_mech_m2_6_frame_id_need` | main → boss (U-274-6) | 帧 id 统一 = 老板级 (U-274-6), 且是后期坐标漂移的根 | main→boss: 帧 id 统一请拍 (U-274-6) —— 盘上并存 B160x100 (MECH 闸现役帧) / 160x100-bench (HW 侧) / 60x30-setA / F30A 四套写法 ⇒ 权威表是 HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES = B160x100 / F30A / P60x15 (现役 = B160x100), MECH/check_onepass_mech_sync.py 的 FRAMES_ALLOWED 亦为同三个 id ⇒ 本单一律按权威表三个 id 书写; 另请裁: 是否在 MECH 两页 (BOARD_PORT_OPENING_S6_FRAME_CALIBER.md / BOARD_ONEPASS_MECH_CLAIMS.md) 加一行 id 对照注记, 免得两处各写一套 | ★是★ |
| 46 | `iss296_mech_m1_ledger_row_need` | main (出板那一趟落表用) | 落表台账那一行的接口格式是出板那一趟的输入, 台账本体不许 MECH 侧写 | main: 出板那一趟落表请按这个格式写 —— 每受管文件一行 = 单号 ／ 文件名 ／ 改前 md5 ／ 改后 md5 四项同行; 板与 .kicad_pro 必须成对两行同一个单号 (只写一行 ⇒ 判红); .kicad_pro 真没变时也要写『否 (逐字节不变)』那一行; 一行不许同时写两件两值 (歧义行 ⇒ MECH 侧当它不算变更行 ⇒ 判红); 单号必须出现在行内或该行所属小节标题里; ★板的前值 = 611b869e13518c3c023fb178f91a0075, .kicad_pro 的前值 = 3e504d2be83152e337949723e909be1b (逐字节不变) | ★是★ |
| 47 | `iss300_release_gate_hook_into_gate_chain` | main (挂闸是项目总工的活) | 挂闸动作在 main 地界 (state/gate_check.py 一个字不许本单改) | main: 请把 MECH/check_onepass_mech_release.py 挂进 state/gate_check.py 的 EXTRA_GATES —— 事实: 该闸 rc=0 实跑通过, fail-closed 语义与现有 run_external_gate 同款, 不写任何文件, 不碰板; 代价: gate_check 每次跑多一道外闸, 该闸内部再跑 6 道 ⇒ 门禁链单次耗时增加约 6 闸的量 (本机实测 6 闸合计 <60s) | ★是★ |
| 48 | `iss300_release_gate_hook_staging_vs_legal_reboard` | main (口径裁决) | 挂链后板那一趟当天必然从绿转红 —— 这个口径必须先裁, 否则会误读成板改坏了 | main: 请裁挂链口径 —— 6 道里有 2 道是钉板 md5 闸 (check_board_frame_coords 的 C4 + check_onepass_mech_sync 的 M5) ⇒ 板只改一次那一趟板 md5 会合法变 ⇒ 那 2 道当天必然从绿转红 ⇒ 只有走合法改板通道 (ISS-296 已建好) 才回绿; 代价: 挂链后当天 gate_check 会红 ⇒ 若不分阶段, 会被误读成板改坏 → 去改板凑绿 → 板 md5 变第二次 → 整趟白跑 ⇒ 本域已把这句话写死在汇总闸的失败输出里 (板 md5 当天变更是合法的, 绝不许改板凑绿) | ★是★ |
| 49 | `iss296_mech_cont3b_reboard_day_selftest_must_run` | main (写进收工验收清单) | 板那一趟落表当天, MECH 两道闸的主跑与 --selftest 必须同一次一起绿 —— ⑱/⑲ 两条反向用例已把 main 的真实落表形状 (两张表) 钉进闸的自检, 只跑主模式抓不到假红 | main: 请把『板那一趟落表后 MECH 两道闸的【主跑 + --selftest】必须同一次一起绿』写进收工验收清单 —— ⑱/⑲ 两条用例已把真实落表形状 (两张表) 钉进闸的自检 ⇒ 落表当天若只跑主模式, 两张表形状的假红不会被抓到 | ★是★ |
| 50 | `iss303_mech_n6_depends_on_cfc_ledger_api` | main (代码级耦合登记 · 常驻约束) | ★这是永久约束不是一次性事项: N6 只读调用板框坐标闸的 5 个名字, 改名 = 本域闸 fail-closed 恒红 | main: 代码级耦合登记 (常驻): MECH/check_onepass_struct_crosscheck.py 的 N6 只读调用 MECH/check_board_frame_coords.py 的 5 个名字 (ledger_state / ledger_cover_rows / m12 / PROTECTED / LEDGER_CANON) ⇒ 这 5 个名字不许改 (改名 = 我的闸 fail-closed 恒红); 若要改口径请走同源改法 (ISS-296 同源探针 logs/iss296/probe_ledger_reading_same_source.py 继续跑); ★代价: 板帧坐标闸与结构交叉核对闸共用一套台账解析器 ⇒ 好处口径零漂移, 边界同域 MECH/ 内 ⇒ 不碰 HW/ 与 SW/ | ★是★ |
| 51 | `iss303_mech_n6_membership_vs_equality_caliber` | main (口径二选一) | 两道闸口径不同源 (一道成员判定, 一道等值判定), 是取舍不是事实 | main: 请裁 N6 与 C4 的口径 —— N6 现在是【成员判定】(盘上 md5 ∈ 硬基线 ∪ 台账登记过的 md5) 而 MECH/check_board_frame_coords.py 的 C4 仍是【等值判定】(盘上 md5 必须 == 台账链头) ⇒ 若台账里出现链上历史值 (或盘上被回滚到硬基线) 则 C4 会红而 N6 会绿; 代价: 两道闸口径不同源 (一道兜底合法落表跳, 一道严格等值) ⇒ 建议保持现状 (严格等值仍由 C4 承担) 或把 N6 也改成等值 (更严但盘上回滚场景会红); 本单按任务书 B1.2 的字面口径实现 (成员判定) | ★是★ |

---

## §6 · 对账表 (关 X / 留 Y / 新答 Z)

| 项 | 条数 | 说明 |
|---|---|---|
| **关 (关闭)** | **64** | ① 12 + ② 5 + ③ 16 + ④ 31 ⇒ 全部带依据行 (本页表格 + 分片 `needs_closed` 台账) |
| **留 (保留待答)** | **72** | ① 9 + ② 12 + ④ 51 ⇒ 每条带 owner + 处理方式 + 一句话问法 (分片 `needs_open_ledger` 台账) |
| **新答 (写进 answers)** | **26** | ① 类自答 12 条 + ③ 类自查 16 条 ⇒ 带 key + 出处 ref + 证据等级 |
| 本单之前已闭合 (不动) | 49 | 被问方已答 45 + 老板 decision 2 + main 已答 1 + 格式错 1 ⇒ 留在 `needs_from` 作历史痕迹 |
| **合计** | **185** | ✓ 逐条无遗漏、无重复、无批量清空 |

### §6.1 ★已知副作用 (如实记, 不藏★)

★**关闭即留证的代价**: 关闭的 need 从 `needs_from` 移出后, 它的 key 在合并器的 `referenced_keys` 里也消失了 ⇒ 对应的 `answers` 条目会被合并器记 1 条 `lint` (`这个 answers.key 没有任何 needs_from 引用它`)。

- 改分片前 lint = **455** 条 (★全部是**既有**的 `interface_claims` 散文值 + 别人的 answers, 与本单无关★); 改分片后 = **489** 条 ⇒ **本单新增 26 条 (正是本单新写的 26 条 answers)**。
- ★**lint 不进任何闸**: `state/merge.py` 的 rc 只看片段完整 (0/2), `state/gate_check.py` 的 rc 只看硬件真源闸 + 新闸 + 9 道钉板 md5 闸 ⇒ **本单前后 merge rc=0 / gate rc=0 均未变**; `state/daily_check.py` 也不看 lint。
- ★**为什么仍然这么写**: 答复正文必须留在 `answers` (合并后进 `STATE.yaml`, 全员可见), 否则 26 条结论只剩文档、状态源看不见 ⇒ 宁可接受 26 条 lint, 也不把答复藏在 .md 里。

---

## §7 · 与「板只改一次」那一趟相关的待答输入清单

★**背景**: 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ **板只改一次** ⇒ 凡与【板框 / 板厚 / 层数 / 镜腿宽度 / 检修口净空 / 重量预算】有关的待答条目, 都要在这一趟之前定, 否则板要改第二次。
★**本单不重做 ISS-310 已交的框口径对照表** (`MECH/BOARD_FRAME_DECISION_INPUT.md` 只读) —— 本页只列**还没答的条目**。

| # | need key | 类别 | 为什么与那一趟有关 (★一句话★) | owner |
|---|---|---|---|---|
| 1 | `iss100_hw_pcb_outline_stale` | 分片取值属硬件总工地界, 我不许代改; 且这两个数会进板那一趟的 P10 充电链判据 | hw-lead: 请把 interface_claims.chg_input_limit 从 0.82-1.00A (390Ω 档 + 0.822 倒向系数) 改成 680Ω 现行口径 (IIN 0.574A / ICHG 0.698A / 单 pin 0.349A), 出处 MECH/HINGE_POWER_CALC.md §0-A.1 | hw-lead (经项目总工) |
| 2 | `iss192_demo_board_zero_mounting_holes_keepout` | 板与网表都归硬件总工; 结构侧只能给『骨架要几个定位基准 + 孔心到板边余量』的接口要求 | hw-lead: demo 板 (HW/PCB/demo_mainboard.kicad_pcb, 帧 B160x100) 零 MountingHole, 而 params 里的 4 个坐标是 60×45 时代遗留且两点压在器件区 —— 请在板那一趟同批补 4 个 ⌀2.2 固定孔 (孔心到板边 >=2.50mm, 避开 SoM 承载区) 并同步 params; 结构侧回执: 骨架按 2 定位销 (全基准 + 只定 Y) + 2 压紧孔 造 | hw-lead + main (板那一趟同批改) |
| 3 | `proto_pcb_freeze_gate` | 板框/厚度/层数/孔位冻结闸: 板厚与层数已定 (1.00mm / 6 层), 板框仍在拍 (U-1) ⇒ 闸还没满足; 老板 11-17 00:43『接下来的目标是绘制 PCB 图』⇒ 板只改一次 ⇒ 冻结闸是这一趟的 | main: 板框冻结闸还差 U-1 (板框三选一: B160x100 / F30A / P60x15) ⇒ 板只改一次那一趟开工前必须先冻结 (板厚 1.00/6 层与 PIN-SET-2 套 A 已定) | main (排期) + 板那一趟 |
| 4 | `iss121_magnet_cover_y_wall_decision` | 盖板 Y 向壁厚缺 0.40mm 是真冲突, 三个选项各有代价; 三个选项的成本还没算完 | main: 检修口盖板 Y 向壁厚缺 0.40mm 请裁 —— ① 盖板 Y 7.60→8.60 (+0.02g/侧) ② 磁铁改 ⌀3.0 (吸力降) ③ 承认该处壁厚要求可降 (ISS-092 C-8『磁铁不承结构力』⇒ 需拉脱实测); 本域默认假设 = ③ | main (结构取舍) |
| 5 | `proto_b1_split_coupon` | 拆两段是排期建议 (B1a 纯 coupon 34 项 / B1b 板相关项), 不是结构结论 | main: B1 拆两段请拍 (B1a = 纯 coupon 34 项工艺标定, 完全不依赖 PCB 冻结 ⇒ ISS-040 打印执行方一有着落就能开; B1b = 板相关项, 必须等 PCB 冻结) ⇒ 本域建议按拆两段执行, B1a 先开 | main (B1 批次排期) |
| 6 | `mech_iss127_temple_split` | 镜腿壳体改 H 向分型 (皮肤盖 + 内胆) 是架构级; P1 已被本域算完并推荐, 只差这一刀 | main→boss: 镜腿壳体改 H 向分型 (皮肤盖 + 内胆) 是否接受? P1 收益: 链① 三档 α 全过 0.40 (0.750/0.736/0.722/0.708) + 链② 四档全过 + 重量净减 0.38g/对; 代价: 零件 24→26 件 + 模具 2 套/侧 + 外观多一条分型线 (贴肤面可零斜度) + 皮肤盖加强筋 +0.15~0.25g/对; 备选 P2 (局部 H 向分型) 会让链② 破线 0.190 < 0.40 | main → boss (架构裁) |
| 7 | `mech_iss127_graphite_cut` | 石墨裁剪是重量预算裁剪, 骨架 4.08g/对 的超支另算 (本条不动) | main: 石墨按【只铺 SoC 段 + X 向逃线带 5.00/边】裁剪是否确认? 收益 = 石墨 2.16g/对 → 0.98g/对 (净减 0.38g/对), 依据 = 30mm 板宽下骨架候选 C 的 SoC 段满宽 30.00, 横向扩散已被满宽铝骨架覆盖 | main (预算裁) |
| 8 | `mech_iss127_graphite_in_hchain` | 挤占 vs 叠加 是链② 的口径钉子, 两条文档不一致, 必须有一句裁定 | main+hw-lead: 石墨在链② (PCB/骨架堆叠 H 链) 里是【挤占】那 0.30 空气隙还是【叠加】在 4.40 之外? 本域按叠加 (保守) 算 ⇒ 链② 在 α=1.5° + 含石墨 + 板厚 1.22 时最坏 0.190 < 0.40 破线; 按挤占则 0.490 ✅ —— 请钉一句 (注: P1 H 向分型下链② 脱模项=0 ⇒ 四档全过) | main + hw-lead |
| 9 | `iss134_mech_boss_decide_waveguide_vendor_and_fov` | 波导归属 + FOV 目标是老板级; 公开波导只有 20-30°(D) vs 我们 D3 口径 120° 对角, 差一个量级 ⇒ 必须一起拍 | main→boss: 波导归属 (A 舜宇奥来 / B 瑞声×Dispelix / C JBD 刻蚀) + FOV 目标一起拍 —— 本域建议按 B 的公开几何做镜框参数化占位 (卡槽 + 可换压框), A 或 C 到货只重做压框; ★FOV 必须在占位件之前定 (耦入/耦出角可调), 否则重演 11-02 方案变了全部重算 | main → boss |
| 10 | `iss208_mech_waveguide_eyebox_le_62mm2_gate` | 眼盒面积是选型前置条件, 不是结果; 老板拍波导时必须一起拍, 否则选回来的波导一定超限 | main→boss: 眼盒面积 A_e <= 62mm² (入眼 2000 cd/m², V2 C-4/C-5) 必须作为波导【选型前置条件】一起拍 —— 公开在售波导标称眼盒全部超限 (12×10=120mm² 超 1.94× / 15×10=150mm² 超 2.42×) ⇒ 且『出瞳 4mm』≠ 眼盒面积 (A_e 的厂商定义式公开查不到 ⇒ 要求供方按 V2 §3 ⑥ 定义式给 A_e) | main → boss (与波导归属一起拍) |
| 11 | `iss213_mech_cross_domain_to_main` | 跨域条目汇总: ① ② 已被 hw-lead 答复 (iss089_p9_topology_and_stack / iss089_chg_led_board_column 均已被答), ③ ICHG 系数已被 ISS-2 | main: ISS-213 跨域汇总里 ① PIN-MISMATCH/STK-P9/TOPO-3 与 ② NET-LED 已由 hw-lead 答复、③ THM-RATIO 已由 ISS-229 解决 ⇒ 剩下条目请按本条正文继续派给对应总工 (结构侧对 ① 的建议已写明: 拓扑按 H 向径向嵌套, 堆叠按触点区 27.00 / FPC 带宽 35.50 两口径分列) | main (派给对应总工) |
| 12 | `iss213_mech_iss126_premise_superseded` | ISS-126 的 open 状态与解锁条件是 main 的活; 本域只给『前提已超越』的证据 | main: ISS-126 的前提已被现口径超越 —— 现行板厚 = 1.00mm (6 层) (MECH/BOARD_GEOM_30MM §1 + service_port_check.py BASE pcb_thk=1.00, 注释『6 层现行; 4 层 0.80 已作废』) ⇒ 检修口盖板内腔 = 7.30 − 2.60 = 4.70mm >= cavity_req 4.50 ✅ 余 0.20 (实跑 54/54 OK / FAIL 0) ⇒ 『只有 0.80 及以下才安全』不成立 ⇒ 请裁关闭 (或改写为『 | main (issue_log 地界) |
| 13 | `iss213_mech_typec_third_candidate` | 第三档几何已出且试样已落, 但『产品件走 FDM 直成型还是金属嵌件』是产品决策 | main→boss: Type-C 开口第三档已出 (FDM 直成型 10.50×4.80 / 金属嵌件 CNC ±0.05 10.25×4.55, 最坏单边 0.63/0.62 ✅, 端件面板最小外形 13.50×7.80 含承力壁 ≥1.50) ⇒ 该特征不得靠打印面成型 ⇒ 请拍: 产品件走 FDM 直成型还是金属嵌件 (两档都合格, 是工艺路线决策) + 开口圆角 R; ★下游两件要排期: HW/CHARGE_BOARD_SPEC.md M-15 的名义+公差 (hw-lead) + 打印包加第三档试样 | main → boss (开口尺寸) |
| 14 | `iss213_mech_pcb_class_6_queued` | 6 个 PCB 类 id / 7 行 FAIL 按老板 11-11 10:07『PCB 布线/布局类一律不派, 排队等原理图定稿』⇒ 保持 FAIL 是正确状态; 只差『挂到哪一单』 | main: 6 个 PCB 类 id (STK-FANOUT / PCB-X-GAP / MRG-54P / MRG-X-4 / MRG-X-3 ×2 / FRM-SUM) 的重算挂到哪一单? 恢复条件已逐条写在 MECH/hw_cross_review_check.py 的说明里 (原理图 P9 定稿给 4 条 FPC 实际落点与拓扑 ⇒ 复算 FPC 带宽合计 ≤ 板宽 30.00 − 0.60) ⇒ 建议随整链重出; ★本单一字没碰它, 分布未变 (PASS 14 / FAIL 17 / 条件通过 8 / 说 | main (随整链重出) |
| 15 | `iss218_mech_tier3_coupon_print_and_measure` | 试样已落成, 只差实物; 执行方归 boss 侧那条 | main: Type-C 第三档试样已落成 (frame_typec_coupon_tier3_revb.stl, 72.0×32.0×5.0mm, 可直接下片) + 门禁 (余量对拍 4/4 + MECH_ANCHORS 7/7 + 反向用例 8/8) ⇒ 现在只差实物: 打印 + 切片 + 量测三项执行方 (本机跨网段不可达/无切片器/无量具) ⇒ 回填口径 = MECH/print/MEASURE_CHECKLIST.md N1~N27 (总 116 项) 填 state/measurements.yaml  | main (打印/切片/量测执行方) |
| 16 | `iss224_hw_landing_must_update_gate_ledger` | 常驻规则: 每次落表要同步 MECH 侧锚点, 否则 MECH 闸假红 | hw-lead: 每次改 HW/netlist_v1.csv 或 HW/netlist_v1_pins.csv 都必须同步 MECH 侧锚点 (MECH/HW_CROSS_REVIEW_TRIAGE.md §1 source_ledger.entries 的 md5/prev_md5/by/landed_at 四个字段), 且落表记录里必须能查到【落表单号 + 文件名 + 新 md5 + 旧 md5】四项 ⇒ 门禁 C21 逐项对账; ★只改锚点不落表 = 悄悄换真源, 只落表不改锚点 = 门禁假红 | hw-lead (常驻规则) |
| 17 | `iss229_mech_hw_pcb_outline_old_charge_numbers` | HW 文档三处仍带 0.822 旧系数; 我不许代改 HW 地界 | hw-lead: 请把 HW/PCB_OUTLINE_60x15.md 的三处旧系数数改掉 —— ①§3.4 表 ICHG/单 pin/余量: 390Ω 0.82A→1.216A / 0.411A→0.608A / ✅→❌超 0.5A 21.6%; 470Ω 0.68A→1.009A / 0.341A→0.505A / ✅→❌超 1.0%; 680Ω 0.47A→0.697A / 0.236A→0.349A / ✅余量 1.43×; 300Ω 0.534A→0.790A ②L149 充电时间 ~29.20min→~ | hw-lead (经项目总工) |
| 18 | `iss229_mech_sw_evt_pwr05_charge_current_criterion` | SW 的 PWR-05 判据量的是哪个电流, 只有 sw-lead 能定 | sw-lead: 请复核 SW/EVT_TEMPLATE.md PWR-05『充电电流 ≥1.5A @5V/2A 适配器』量的是输入电流 IIN 还是电池侧电流 ICHG —— 改正系数 1.216 下 max 档电池侧 = 390Ω 1.216A / 680Ω 0.697A / 1.2kΩ 0.395A (连现行 V-4 候选 680Ω 也只有 0.697A ⇒ 1.5A 达不到); 若量的是 IIN, 390Ω max 1.00A / 680Ω 0.574A ⇒ 同样达不到; ★该不兼容在旧 0.822 系数下 | sw-lead |
| 19 | `iss222_mech_print_pack_optical_cage_md5` | 打印包禁改项因走鹃Ⅱ 作废而解冻, STL 已重生, 但台账登记值还没更新 | main: 请把 PROJECT_TRACKER.md 里 optical_cage_TEMPLATE.stl 的登记 md5 从 6f23c2e2f52e81060e5c0bbecb4cc881 更新成 537dc6afb4246cce30aa6853de7cebd1 (ISS-222 已按新规格重生: 分光件座 14×6×10 → 7.78×8.84×11.0; 其余 6 个 STL 逐字节未变) | main (PROJECT_TRACKER 是项目总工地界) |
| 20 | `iss264_mech_jd_y0_and_open_y_caliber` | jd_y0 (J_DEBUG 焊盘阵列 Y 起点) 是所有检修口 Y 向数的总开关, 未定则开口 Y / P-5 最近距离全部悬着 | main+hw-lead: 请给 30mm 板上 J_DEBUG 阵列真实起点 jd_y0 (合法区间 [1.665, 11.730], 现状 9.50) ⇒ 定了它, 开口 Y (现 7.835..12.435) 与 P-5 最近距离 (P2 3.23mm / S2 8.53mm) 一次算清; ★候选 A 9.50 / C 10.00~11.00 (B 不可用), 且须与落表 1x4 vs 脚本 2x5 的脚数一起定 (差 0.635mm) | main + hw-lead |
| 21 | `iss264_mech_jd_y0_legal_range_errata_pending` | 两件要 main 拍/改: 决策页 A 段的 jd_y0 区间订正 + 检查项 2.5 的 Y 上限是否按 30mm 板口径放宽 | main: 请拍两件 —— ① 决策页 A 段把『jd_y0 合法区间』改成订正后的 [1.665, 11.730] mm, 并把『按相对位置迁 ⇒ 孔与焊盘阵列重叠 12.37mm』改写成『检查项 2.5 判红 (焊盘上沿 25.77 > 13.00, 余量 -12.77mm)』(P-5 3.23/8.53 与开口 Y 7.835..12.435 不变) ② 检查项 2.5 的 Y 上限 13.00 要不要按 30mm 板口径订正为 28.00 (订正 ⇒ 区间上界 11.73→26.73, 候选表整张重算, j | main |
| 22 | `iss267_mech_jd_y0_and_frame_decision` | 板框三套并存 + jd_y0 两拍合并; 板框 = 老板拍, main 汇总 | main: 板框口径三选一请汇总后交老板 (① B160x100 台架板 160×100 ② F30A 产品板 60×30 套A ③ P60x15 60×15) —— 结构侧已给 36 档机器可行域表 (MECH/board_frame_feasibility.py) + 两条路线代价 (MECH/BOARD_FRAME_DECISION_INPUT.md §C): ① 36 档全红 (V链-68.00 / L链-85.50, 与板厚无关) 且板本身 47.36g = 整机质量预算 65~97% ⇒ 不得宣称可投产 | main (板框三选一) → boss |
| 23 | `iss267_mech_debug_part_model` | J_DEBUG 脚数与座体高度是结构开口尺寸的输入, 落表与结构模型不一致 | hw-lead: 请定 J_DEBUG 的脚数与座体真实高度 —— 落表是 1×4 (HW/BOM_v1.csv:71 + HW/netlist_v1_pins.csv:202-205) 而 MECH/service_port_check.py 按 2×5 (10 脚 Cortex-10) 算 ⇒ 必须清空区 X 宽 7.62 与开口 X 10.20 要重算; 另 J_UART 相对位置: 盘上板 J_DEBUG@(144.30,58.00) 与 J_UART@(20.74,70.00) 相距 123.6mm 而结 | hw-lead |
| 24 | `iss271_mech_s6_ledg_window` | 板侧落位坐标已算好, 等 hw-lead 在板那一趟用; 但脚数与 J_UART 相对位置还没定 | hw-lead: 板侧坐标空间可直接用 —— (1) 检修口/调试口: Y 向 jd_y0 ∈ [1.665, 11.730] (现状 9.50), X 向 jd_x0 ∈ [48.290, 51.090] (2×5) 或 [48.925, 51.725] (落表 1×4), 开口 X 可放行区间 [47.00, 60.00], 必须清空区 X 50.50..58.12 × Y jd_y0±1.27, 开口 10.20×4.60, 单边间隙 X 1.29 / Y 1.03; ★脚数与 jd_x0 必须一起定 (差  | hw-lead (板那一趟坐标空间) |
| 25 | `iss276_mech_s6_claim_frame_align` | 帧 id 与坐标基准必须两边一致, 不一致就停手 | hw-lead: 请与 HW/PCB/BOARD_FRAME_CALIBER.md (ISS-274 同批产出) 的帧声明对齐后再收进 §3-S6 —— 三条具体: ①调试口开口 = X 137.850..148.050 × Y 54.300..58.900 (帧 B160x100), 左下角可放行 X0 ∈ [137.850, 142.063] · Y0 ∈ [54.300, 55.330] ②UART 检修口开口 = X 13.790..23.990 × Y 66.300..70.900, 左下角可放行 X0  | hw-lead |
| 26 | `iss296_mech_m3_nine_gates_green_need` | 9 道钉板 md5 闸要收工当天同一次全绿, 这句话必须写进作业包 | main: 请把『9 道钉板 md5 闸 ①~⑨ 收工当天必须同一次全绿』写进板那一趟的作业包 —— 机器清单 state/board_md5_pinned_gates.json 实测 9/9 全是『已有 reboard 通道』(HW 6 道由 ISS-297 建好, 本单已把 M3 表那 6 个单元格由『待建』订正为『已建 (ISS-297)』并留痕); ★第 5 道 HW/check_pin_function_labels.py 主模式仍 rc=1 (18 条 ISS-257 起的既有缺陷, 属别单范畴) ⇒  | main (写进板那一趟作业包) |
| 27 | `iss296_mech_m2_6_frame_id_need` | 帧 id 统一 = 老板级 (U-274-6), 且是后期坐标漂移的根 | main→boss: 帧 id 统一请拍 (U-274-6) —— 盘上并存 B160x100 (MECH 闸现役帧) / 160x100-bench (HW 侧) / 60x30-setA / F30A 四套写法 ⇒ 权威表是 HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES = B160x100 / F30A / P60x15 (现役 = B160x100), MECH/check_onepass_mech_sync.py 的 FRAMES_ALLOWED 亦为同三个 id | main → boss (U-274-6) |
| 28 | `iss296_mech_m1_ledger_row_need` | 落表台账那一行的接口格式是出板那一趟的输入, 台账本体不许 MECH 侧写 | main: 出板那一趟落表请按这个格式写 —— 每受管文件一行 = 单号 ／ 文件名 ／ 改前 md5 ／ 改后 md5 四项同行; 板与 .kicad_pro 必须成对两行同一个单号 (只写一行 ⇒ 判红); .kicad_pro 真没变时也要写『否 (逐字节不变)』那一行; 一行不许同时写两件两值 (歧义行 ⇒ MECH 侧当它不算变更行 ⇒ 判红); 单号必须出现在行内或该行所属小节标题里; ★板的前值 = 611b869e13518c3c023fb178f91a0075, .kicad_pro 的前值 =  | main (出板那一趟落表用) |
| 29 | `iss300_release_gate_hook_into_gate_chain` | 挂闸动作在 main 地界 (state/gate_check.py 一个字不许本单改) | main: 请把 MECH/check_onepass_mech_release.py 挂进 state/gate_check.py 的 EXTRA_GATES —— 事实: 该闸 rc=0 实跑通过, fail-closed 语义与现有 run_external_gate 同款, 不写任何文件, 不碰板; 代价: gate_check 每次跑多一道外闸, 该闸内部再跑 6 道 ⇒ 门禁链单次耗时增加约 6 闸的量 (本机实测 6 闸合计 <60s) | main (挂闸是项目总工的活) |
| 30 | `iss300_release_gate_hook_staging_vs_legal_reboard` | 挂链后板那一趟当天必然从绿转红 —— 这个口径必须先裁, 否则会误读成板改坏了 | main: 请裁挂链口径 —— 6 道里有 2 道是钉板 md5 闸 (check_board_frame_coords 的 C4 + check_onepass_mech_sync 的 M5) ⇒ 板只改一次那一趟板 md5 会合法变 ⇒ 那 2 道当天必然从绿转红 ⇒ 只有走合法改板通道 (ISS-296 已建好) 才回绿; 代价: 挂链后当天 gate_check 会红 ⇒ 若不分阶段, 会被误读成板改坏 → 去改板凑绿 → 板 md5 变第二次 → 整趟白跑 ⇒ 本域已把这句话写死在汇总闸的失败输出里 (板 | main (口径裁决) |
| 31 | `iss296_mech_cont3b_reboard_day_selftest_must_run` | 板那一趟落表当天, MECH 两道闸的主跑与 --selftest 必须同一次一起绿 —— ⑱/⑲ 两条反向用例已把 main 的真实落表形状 (两张表) 钉进闸的自检, 只跑主模式抓不到假红 | main: 请把『板那一趟落表后 MECH 两道闸的【主跑 + --selftest】必须同一次一起绿』写进收工验收清单 —— ⑱/⑲ 两条用例已把真实落表形状 (两张表) 钉进闸的自检 ⇒ 落表当天若只跑主模式, 两张表形状的假红不会被抓到 | main (写进收工验收清单) |
| 32 | `iss303_mech_n6_depends_on_cfc_ledger_api` | ★这是永久约束不是一次性事项: N6 只读调用板框坐标闸的 5 个名字, 改名 = 本域闸 fail-closed 恒红 | main: 代码级耦合登记 (常驻): MECH/check_onepass_struct_crosscheck.py 的 N6 只读调用 MECH/check_board_frame_coords.py 的 5 个名字 (ledger_state / ledger_cover_rows / m12 / PROTECTED / LEDGER_CANON) ⇒ 这 5 个名字不许改 (改名 = 我的闸 fail-closed 恒红); 若要改口径请走同源改法 (ISS-296 同源探针 logs/iss296/pro | main (代码级耦合登记 · 常驻约束) |
| 33 | `iss303_mech_n6_membership_vs_equality_caliber` | 两道闸口径不同源 (一道成员判定, 一道等值判定), 是取舍不是事实 | main: 请裁 N6 与 C4 的口径 —— N6 现在是【成员判定】(盘上 md5 ∈ 硬基线 ∪ 台账登记过的 md5) 而 MECH/check_board_frame_coords.py 的 C4 仍是【等值判定】(盘上 md5 必须 == 台账链头) ⇒ 若台账里出现链上历史值 (或盘上被回滚到硬基线) 则 C4 会红而 N6 会绿; 代价: 两道闸口径不同源 (一道兜底合法落表跳, 一道严格等值) ⇒ 建议保持现状 (严格等值仍由 C4 承担) 或把 N6 也改成等值 (更严但盘上回滚场景会红); 本 | main (口径二选一) |

**合计 33 条与板那一趟直接相关。** 另有 ② 类里 3 条 (M-B2 电芯采购要求 / M-B12 打印执行方 / M-B7 已闭合板长) 与那一趟的实物/采购侧耦合, 一并见 §3。

### §7.1 板那一趟之前结构侧【已经定了、可以直接用】的值 (★免得重复讨论★)

| 项 | 现行值 | 出处 | 级别 |
|---|---|---|---|
| 板长 | 60.00mm (X=0 = 铰链端) | `MECH/BOARD_GEOM_30MM.md` §1 | [官方] |
| 板宽 | 30.00mm (= V 向) | 同上 | [官方] |
| 板厚 / 层数 | 1.00mm (6 层) | 同上 + `MECH/service_port_check.py` BASE `pcb_thk` | [官方] |
| PIN-SET-2 孔位 (套 A) | P1(8.00,15.00) / P2(52.00,15.00) 定位销 ⌀2.0 + S1(8.00,10.00) / S2(52.00,20.00) 压紧 ⌀1.4 | 同上 §3 + `HW/pcb60x30_check.py`:119-124 | [实测] |
| 检修口净空 | 盖板内腔 4.70mm ≥ 判据 4.50 (余 0.20) | `MECH/service_port_check.py` 检查项 4.2 (rc=0, 57/57) | [推算] |
| 检修口开口 (帧 B160x100) | 调试口 X 137.850..148.050 × Y 54.300..58.900 · UART 检修口 X 13.790..23.990 × Y 66.300..70.900 · 开口 Y 按 `OPEN_Y_eff(h)=max(4.60, h+1.80)` (h=[0数据]) | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §1 C-OPEN-1/2 + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | [实测] |
| 镜脚三条锁死链 | H 7.30 / V 38.00 / L 130.00 (Δ0.00) | `MECH/MECH_BUDGET.md` §1.6.2 + `MECH/service_port_check.py` | [官方] |
| 板 md5 (零写板基线) | `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17` | 本轮实跑 `md5sum` + `stat` | [实测] |

---

## §8 · 证据分级汇总

| 结论 / 数 | 级别 | 来源 |
|---|---|---|
| 机检 mech-lead 缺口 108 → **62** | [实测] | `state/gate_check.py` 两次实跑 (原始输出 `logs/iss313/gate_check_BEFORE.txt` / `gate_check_AFTER.txt`) |
| 全局等外部 70 → **49** | [实测] | 同上 |
| 板 md5 `611b869e…` + mtime `2026-11-06 07:07:17` | [实测] | `md5sum` + `stat` (交卷前后逐字节相同) |
| Hirose FH12-10S-0.5SH(55): 单触点 **0.5A** / FPC 厚度 **0.30mm** / 座高 2.00mm / 10 位 / 0.50mm pitch / 50V / ZIF | [官网] | Hirose 官网 + 分销规格页 |
| 3M VHB 5962: 1.6mm ±10% / 长期耐温 **93°C** / 短期 149°C / 剥离 39 N/cm | [官网] | 3M 技术数据表 |
| LOCTITE AA 3311: **ISO-10993 biocompatible** / UV 固化 / 深度 >13mm | [官网] | Henkel 产品页 |
| MIL-A-8625 Type III: 膜厚公差 **±20%** (≤2 mil) / 典型 0.0005-0.002in / 50% 渗透 + 50% 表层生长 | [官网] | MIL-A-8625F §3.7.2.1 / §3.4.3 |
| Renata: ICP422339PR 340mAh 4.6×23.5×40.5 · ICP582035PR-01 340mAh **6.4**×20.5×37 | [官网] | renata.com 锂聚合物电池页 |
| 丰江 432243: 3.7V ≥420mAh 4.3×22.0×43.5 脉冲 1~3A 循环 ≥500 | [官网] | battsysbattery.cn 软包聚合物电池页 |
| JBD: Hummingbird Mini Ⅱ 0.15cc/0.3g/60mW · Hummingbird Ⅱ 0.2cc/0.5g/95mW · Hummingbird Ⅰ 6000nits/30° · 刻蚀波导彩虹抑制 95% / 均匀性 >80% / ΔE 0.02 | [官网] | jb-display.com |
| PC/ABS 注塑收缩率 0.29-0.76% (ASTM D955-89) 各向异性 | [媒体] | 行业通例 |
| 波导 2D 外形 / 耦入区容差角 / 安装基准 / 膜层判据 / ARS45 散热焊盘 / 丰江内阻 / 镁合金点蚀数据 | [0数据] | 公开渠道查不到 ⇒ 已写降级方案 (§4) |
| 铝 6063-T6 k = **201** W/m·K | [官网] | Hydro / Aalco / Kaiser 三家互证 (MECH_BUDGET §3 已统一) |
| 腔体 81.20/77.43/75.24°C (d=15/18/20) · 鼻梁 54.33/52.75/51.83°C · 集热面需求 ≈2628mm² (P3) / ≈4175mm² (P1) | [推算] | ISS-065 §2.3 模型 + MECH_BUDGET §1.7 / §3 |
| 端件金属热路 R ≤70 K/W ⇒ A ≥4.975mm² (2.0×2.0 铝条不合格) | [推算] | MECH_BUDGET §3 |

---

## §9 · 边界自审 (★逐条核对★)

### §9.1 硬边界

| 边界 | 本单怎么守的 |
|---|---|
| **零写板** | 板 `HW/PCB/demo_mainboard.kicad_pcb` 交卷前后 md5 = `611b869e13518c3c023fb178f91a0075`、mtime = `2026-11-06 07:07:17` ⇒ 逐字节相同 (本单只读板) |
| **零落表** | 网表 / 脚表 / BOM / 落表台账 一律未动 |
| **零改闸** | `state/gate_check.py` / `state/merge.py` / `MECH/service_port_check.py` 一个字没改 (`MECH/service_port_check.py` md5 = `db58ff6a2afc28b8bf517e3c57c56bc1` 前后相同) |
| **零改既有文档正文** | `MECH/BOARD_FRAME_DECISION_INPUT.md` / `MECH/BOARD_GEOM_30MM.md` / `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` 只读; 本单只**新建** `MECH/MECH_NEEDS_TRIAGE.md` |
| **零外发** | 不发邮件 / 不询价 / 不问询 / 不采购 / 不联系任何厂商; `state/outbox/` 下的草稿一律不发只留档; §4 的 16 条全部自查结案 |
| **不替老板拍板** | ② 类只给【need key + 决策码 + 选项 + 代价 + 建议默认值 + 不拍的后果】; 建议值都标注「只作参考·不代拍」; 本单**没有**在分片里写任何 `decision` 字段 |
| **不自签 issue_log** | `state/issue_log.yaml` 一个字节没碰 (只读核对 3 个 md5 是否落锚) |
| **只写自己那一份** | `state/fragments/mech.yaml` 一个分片 (走 `state/frag_write.py` 原子写, **禁止** `open(p,"w")`); `hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节没碰 |

### §9.2 交卷前必跑 (★输出原样贴进交接单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss313_tmp
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb MECH/service_port_check.py state/fragments/mech.yaml
```

### §9.3 本单新写的文件 (★只有这 4 类★)

| 路径 | 性质 |
|---|---|
| `MECH/MECH_NEEDS_TRIAGE.md` | 新建 (本单交卷页) |
| `HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md` | 新建 (交卷单 B1~B6) |
| `logs/iss313/` | 新建 (取数命令 + 原始输出 + 改分片前后 md5 + 数据源与脚本) |
| `state/fragments/mech.yaml` | 只改自己那一份 (经 `state/frag_write.py` 原子写) |

