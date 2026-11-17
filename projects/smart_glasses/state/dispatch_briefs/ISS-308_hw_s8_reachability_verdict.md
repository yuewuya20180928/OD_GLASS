# ISS-308 · hw-lead 任务书 —— ★★【「板那一趟 S8 (unconnected 45 → 0)」的可达性判决书: 残余网逐条归桶 + 老板还差 N 个字母 + 现在就能做的技术活清单】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-308
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 04:3x** ★
> ★**性质**: ★**内部活 · 纯分析 / 作业包类 · 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板** ★

---

## ★0 · 一句话

★**「板只改一次」⇒ S1 / S2 / S3 / S4 / S6 / S7 / S8 必须【同趟】做完 ⇒ ⇒ 如果 S8 (布线归零) 能不能做完【现在】没人说得清, 这一趟就可能白跑 ⇒ 而白跑 = 板 md5 变第二次 = Gerber / 投产包 / 留证链 / 盖章 / 发布全作废** ★
★**⇒ 本单 = 把 S8 的可达性判【死】: 残余的 22 个网名逐条落到 5 个桶 (老板字母 / GND 卡死 / 差分 N 腿互掐 / 让路闸靶子 / 其它) ⇒ 交出【老板还差 N 个字母 (N 必须是具体数字)】+【现在就能做的技术活清单】+【S6 落位增补表草案】** ★
★**★这是本单唯一目标 (★不许顺手改任何东西 / 不许代拍★)** ★

---

## ★1 · 病灶 (★main 2026-11-18 04:2x~04:3x 本机实跑, 原样 rc, 不抄任何 agent 报告★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
bash state/pcbnew_py.sh state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb ; echo "rc=$?"
python3 state/compare_arm_official.py --self-test ; echo "rc=$?"
```

★**① 现役板实测 (★main 04:3x 本机实跑, 原样★)**:

```
✅ C3 DRC violations = 0 (要求 0)
✅ C4 unconnected items = 45  ← 骨架阶段允许未布线 (布线完成后用 --strict 归零)
✅ C7 同点重复过孔 = 0 (要求 0)
✅ C6 生产文件齐 — Gerber 32 个
rc=0
```

★**板身份**: md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17` · 帧 `B160x100` (160.00×100.00mm / 8 铜层 / 186 封装) ⇒ ★**本单全程不许碰它** ★

★**② 作业包 §3-S8 原文口径 (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 实读★)**:

- ★**「45 条里 23 条是高速 DSI/CSI 腿, 全部要跨 SoM 主体 (x 8..76, y 6..56)」** ★
- ★**「官方板 (160×100/8L) 这 13 条 DSI 腿自己一根都没布通」** ★
- ★**其余 22 条的死因登记 = ISS-265 §6 逐条列了 5 条**: A1 (`BAT_DET` 终点未定义) · W-1/W-2 (ESD 未拍 ⇒ 器件钉位定不下来) · W-4 (`Q_PG.3` 极性未定) · `D_LED_G` 物理位置 (★`LED_G_D` 走线 93.49 mm★) · `FSIN_OUT` 3.01 mm 布不通 (★根因已由 ISS-282 订正 = 【布线排队顺序】, 不是逃逸方向 bug★) ★
- ★**「这是本单唯一一个『可能整趟做完仍然投不了板』的步」** ★

★**③ 残余网名清单 (★`state/UNC_TARGET_MAP.md` §「11-11 05:6x 更新」实读★)** —— 最佳候选 `state/.lastgood/candidate_v76mx1L_pour.kicad_pcb` (★DRC 0 · unc 26 条 / 22 网名 · 名单制闸 rc=0★) 的残余 22 网名:

`CARRIER_BOARD_EN` `CSI_D0_CK_N` `CSI_D0_D0_N` `CSI_D0_D0_N_SRC` `CSI_D0_D2_N` `CSI_D0_D3_N` `CSI_MCLK` `DSI_D0_CK_N_SRC` `DSI_D0_D0_N` `DSI_D0_D0_P` `DSI_D0_D1_N` `DSI_D0_D1_N_SRC` `DSI_D0_D3_N` `I2C_A_SCL` `I2C_B_SCL` `I2C_B_SDA` `ID_DETECT_1` `KEY_VOL_M` `KEY_VOL_P` `LED_B` `SPI_CSn_BOOT` `USB_CC1`

★**★④ 一个【没人写下来过】的现象 (★本单第一问★)**: ★**22 条残余里, 差分类的绝大多数是【N 腿】** (`CSI_D0_CK_N` / `CSI_D0_D0_N` / `CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N` / `DSI_D0_CK_N_SRC` / `DSI_D0_D0_N` / `DSI_D0_D1_N` / `DSI_D0_D1_N_SRC` / `DSI_D0_D3_N` · 另 `DSI_D0_D0_P` / `KEY_VOL_P` / `KEY_VOL_M` / `LED_B`) ⇒ ⇒ ★**「P 腿布通了、N 腿布不通」是【层分配】的典型症状, 不是「走廊不够」的典型症状** ★
★**⇒ 而路由器源码里【正好有一个专门治这个的机制】**: `state/gen_pcb_routing.py` 里的 `PCB_PAIR_LAYERSEL` (★env 门控 · 默认关 ⇒ 逐位不变★) ★**它的注释原文写着**: 「★**布 N 侧时, 若 P 侧在【某些层】上占了很多 ⇒ 把 N 侧【优先限制到 P 侧用得少的层】**★」 ★
★**⇒ 而 `state/UNC_TARGET_MAP.md` 的原文写的是**: 「★**走 pair-aware / 差分层选择 (★`PCB_PAIR_LAYERSEL` 目前无效但无害★) / 成对走廊规划**★」 ⇒ ⇒ ★**「无效」这个判断【谁写的 / 哪一天写的 / 有没有实测支撑】= 本单必须查清的第一件事** ★

★**⑤ 臂史 (★`state/ARM_LEDGER_2026-11-10.md` 实读★)**: ★**33+ 个臂全部停在 unc 24~29 条 / DRC 0~1** ⇒ ★**布线参数调优已经【到平台期】了** ⇒ ⇒ ★**按 MEMORY 铁律「多个臂在同一批网/差分对上失败 ⇒ 先查它们共享的东西」⇒ 根因在布局 / 机制, 不在参数** ⇒ ★**⇒ 本单要交的是【机制级判决】, 不是【再来一个臂】** ★

★**⑥ 板那一趟的时序铁律 (★`HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` + 作业包 §6.1/§6.2 实读★)**: ★**板 md5 只允许变一次 ⇒ A 类步 (S1/S2/S3/S4/S6/S7/S8) 必须同趟做完 ⇒ B 类步 (S9~S13) 最后跑一次** ⇒ ★**⇒ 在这之前, 只有「不改板」的准备工作值得先做; 任何 B 类步先跑 = 破功** ★

---

## ★2 · 本单要交的三件东西 (★唯一目标★)

### ★2-A · 【判决 1】残余 22 网名 → 5 个桶, 逐条落桶 (★主交付★)

★**每个网名一行, 必须有**: 网名 · 桶 · 根因 (一句话 + 依据行号/坐标/实测数) · 能不能在「板那一趟」这一趟里解 · 若能: 解法一句话 (env 键 / 落铜前拦 / 落位坐标 / 老板字母) · 若不能: 卡在谁 ★

| 桶 | 判据 (本单自己定死, 逐条给依据) |
|---|---|
| ★**B1 · 差老板字母** ★ | 死因是 `BAT_DET` 终点 / ESD 钉位 / `Q_PG.3` 极性 / `D_LED_G` 位置 / 板形层数 ⇒ 引用作业包 §6.2 的登记行 |
| ★**B2 · GND 卡死 (铜皮 / 下拉孔)** ★ | 净距 < 0.20 mm 且抢路者是 GND ⇒ ★**★解法只许是「落铜前拦」: GND 铜皮局部 keepout / 缩形 / 挪下拉孔 ⇒ 不许在产物上擦 (★MEMORY 铁律★)** ★ |
| ★**B3 · 差分 N 腿互掐 (层分配)** ★ | ★**P 腿有铜 / N 腿无铜 或 N 腿净距被 P 腿压** ⇒ ★**⇒ 必须实测【N 腿的层占比 vs P 腿的层占比】(★从最佳候选板逐段读层★) ⇒ 拿它判「`PCB_PAIR_LAYERSEL` 这套机制到底有没有被触发过 / 为什么没救回来」** ★ |
| ★**B4 · 让路闸靶子 (普通信号网互掐)** ★ | 抢路者非 GND 且 k ≤ 3 ⇒ 给 env 配方 (`PCB_YIELD_VICTIMS` / `PCB_PRIORITY_NETS` / `PCB_PAIR_BEFORE_PWR` 等) |
| ★**B5 · 其它 (逐条单列)** ★ | 不许塞进上面四桶 ⇒ 每条自己给判据 |

### ★2-B · 【判决 2】老板还差 N 个字母 (★N 必须是具体数字★)

★**照 ISS-306 (sw-lead) 已 verified 的那个口径写** (★那个单子问的是 G1a 两条红 ⇒ 本单问的是 S8★):
★**① N = 几** · ★**② 每个字母卡在哪一步 (S4 / S5 / S8) + 对应哪条残余网名** · ★**③ 不拍的后果 (一句话, 要具体: 「该网布不通 / 板必须再改一次 / G1 开不了」)** ★
★**④ 若 N = 0 ⇒ 那就明写 N = 0, 不许为了凑数硬找卡点** (★ISS-306 的口径★)

### ★2-C · 【判决 3】现在就能做的技术活清单 (★零等老板★)

★**逐条给**: 技术活内容 · 需要哪个 env 键 (逐字) · 落铜前拦 / 落位增补的具体改法 (坐标 / 净距) · 预期能解掉哪几个残余网名 · **预估代价 (臂跑多久 / 要不要改路由器源码 / 要不要改板)** ★
★**★凡是要改板 / 要改网表真源的 ⇒ 不许写进「现在就能做」⇒ 归到 2-B 的老板字母桶** ★

---

## ★3 · 交付物 (★三个, 新建 ⇒ 不许改既有文件正文★)

★**★交卷物 (3 件) · 全部为【新建文件】★★ ★:

1. ★**`HW/PCB/S8_REACHABILITY_VERDICT.md`** (★新建 · 判决书正文 ★) ⇒ ★**内容 = §2-A 的落桶表 + §2-B 的 N 个字母 + §2-C 的技术活清单 + 每条数字的实测出处 (★命令 + 行号 / 坐标★)** ★
2. ★**`HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md`** (★新建 · 交卷单 ★) ⇒ ★**必须按【标准验收块 B1~B6】写** (★`state/gate_check.py` 的 `REQUIRED_BLOCKS` 口径★) ⇒ ★**Q1 必须 18/18** ★ ★ ⇒ ★**占位符判据 = `grep -cE "🔄|待填"` 必须 = 0** (★`state/check_report_placeholders.py` 抓不到这种形态, 这是 main 实测坑★)
3. ★**`state/_iss308_s8_reachability_check.py`** (★新建 · 只读复跑脚本 ★) ⇒ ★**rc=0** · 把 §2-A 的【桶归属 + 网名清单】钉住 (★能被别人一条命令复算★) · 附 `--selftest` 反向用例 (★改一条网名的桶 ⇒ 脚本必须红★)

★**★分片纪律★**: ★**只写 `state/fragments/hw.yaml`** (★用 `python3 state/frag_write.py --agent hw-lead ...` 原子写, ★**禁止 open(p,"w")★**) ⇒ ★**claim / answer / artifact 各至少一条** ⇒ ★**`grep -c iss308` 必须 ≥ 5** ★
★**★不许写**: `state/fragments/mech.yaml` / `sw.yaml` / `pm.yaml` / 任何别人的分片 ★

---

## ★4 · 交卷物 (4 件) 的验收命令 (★全部实测存在, 逐条给期望 rc★)

★**★先跑这三条 (★工作目录 = `/home/yuewuya/.openclaw/workspace/projects/smart_glasses`★)** ★

1. ★**现役板底数 (零写板自证)★**: `bash state/pcbnew_py.sh state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` ⇒ ★**rc=0** · ★**C4 unconnected items = 45** (★main 04:3x 实测原样★) ★
2. ★**名单制晋级闸自测 (★判据本体不许改★)★**: `python3 state/compare_arm_official.py --self-test` ⇒ ★**rc=0** ★
3. ★**本单第 3 件 (★新建只读复跑脚本★)★**: `python3 state/_iss308_s8_reachability_check.py` ⇒ ★**rc=0** ★ · `python3 state/_iss308_s8_reachability_check.py --selftest` ⇒ ★**rc=0** (★反向用例自证★) ★
4. ★**交卷前必跑 (★三条的原始输出都要贴进交卷单 B4★)★**: `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ ★**rc=0 · Q1 18/18 · Q7 9/9** ★ · `python3 state/issue_check.py` ⇒ rc=0 ★

★**★板零写板双证 (★交卷单 B4 必须贴这两行★)** ★:
```bash
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
# ★期望: 611b869e13518c3c023fb178f91a0075 · 2026-11-06 07:07:17 (一字未动)★
```

★**★时间预算 (★main 实测坑, 必读★)**: ★**上一批子会话在 570~1360 秒被父 run 掐掉 (status=timeout / abortedLastRun=true) ⇒ ⇒ 【交卷优先, 不许追求完美】: B1~B6 先填满 (缺口写进 B5 未决项) ⇒ 再补 §2-A/2-B/2-C 的深度** ★
★**★不许新跑布线臂 (★本单是【分析 / 判决】单, 不是开臂单·理由见 §1-⑤★)** ⇒ ★**所有数字必须来自【已在盘上的东西】: 现役板读数 / `state/.lastgood/` 的候选板 / `state/ARM_LEDGER_2026-11-10.md` / `state/UNC_TARGET_MAP.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` / `HW/PCB/FSIN_OUT_ROOTCAUSE.md` / `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` / `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `HW/PCB/BOARD_FRAME_CALIBER.md`** ★
★**★若某个数字在盘上找不到 ⇒ 不许估 ⇒ 标 [0数据] + 写清「要拿到它得跑什么 / 代价多少」★**

---

## ★5 · 边界 (★逐条自证, 写进交卷单 B6★)

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | ★板 md5 + mtime 两条都贴 (见 §4)★ |
| ★**零落表** ★ | ★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/SCHEMATIC_LANDING_V1_LANDED.md` 一个字节没动 (★md5 对回台账登记值: 6aee500e… / 9174309d… / 5b999399…★)★ |
| ★**零改闸 / 零改判据脚本** ★ | ★`state/compare_arm_official.py` / `state/check_pcb_drc.py` / `state/gate_check.py` / `HW/check_onepass_commit_order.py` / `HW/check_workpack_state_values.py` 一个字节没动★ |
| ★**零改既有文档正文** ★ | ★本单只【新建】三个文件 ⇒ 作业包 / 清单页 / `state/UNC_TARGET_MAP.md` / 臂总账 一律不碰 (★要追加就追加到你自己的新文件里, 别去改别人维护的页★)★ |
| ★**零外发** ★ | ★没发任何邮件 / 询价 / 问询 / 采购 / 原厂问询 ⇒ 本单不依赖任何外部回复 ⇒ 【查不到就写 [0数据] + 降级方案】★ |
| ★**不替老板拍板** ★ | ★§2-B 只给 N + 卡点 + 后果, 不给决策码★ |
| ★**不自签 issue_log** ★ | ★不写 `state/issue_log.yaml` (★验收由 main 签★)★ |
| ★**不改别人分片** ★ | ★只写 `state/fragments/hw.yaml`★ |

---

## ★6 · 交卷格式 (★照 ISS-307 那份交卷单的形状写★)

★**交卷单 = `HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md`**, 必须含:
★**B0** 结论摘要 (★三行: S8 可行 / 需 N 处布局修正后可 / 需老板 P7 选 C4 —— ★三选一, 必须选一个, 不许骑墙★) ★
★**B1** 验收标准自评 (★逐条对 §4 的期望 rc, 贴原始输出★) ★
★**B2** 证据分级 (★`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 逐条标★) ★
★**B3** 接口取值声明 (★本单声明的网名清单 / 落位坐标 / env 键名 —— 这些是别人要照抄的东西, 必须逐字给★) ★
★**B4** 闸复跑原始输出 (★§4 那几条 + 板 md5/mtime 双证★) ★
★**B5** 未决项与卡点 (★每条写: 卡在谁 / 要什么 / 不做的后果 ★**含本单自己没做完的部分 (★时间预算不够就写这里, 不许装完成★)★) ★
★**B6** 边界自证 (★§5 那张表逐行★) ★

★**★交卷纪律★**: ★**先交卷, 再完美** ★ · ★**占位符 0 (`grep -cE "🔄|待填"` = 0)** ★ · ★**Q1 必须 18/18** ★

---

## ★7 · 为什么这一单值得一个总工的预算 (★给 main 复盘用, 不必写进交卷单★)

★**① 队列已排空**: `state/advance.py --json` ⇒ `internal: []` (三个总工 open=0 · fixing=0) + `subagents list` ⇒ active 0 ⇒ ★**本轮按「开新单」处理 (队列排空时让内部待办不断线 = 本 job 的存在意义)★** ★
★**② 机器前置全清**: `state/gate_check.py` rc=0 (★Q1 18/18 · Q7 钉板 md5 闸链 9/9 全绿★) · `state/issue_check.py` rc=0 ⇒ ★**板那一趟开工前, 机器能挡的都挡住了 ⇒ 剩下的红只有两类: ①老板的字母 ②S8 本体** ★
★**③ 本单攻的是②里的【可判决部分】**: ★**S8 能不能做完, 现在没有任何一份文档给出答案 ⇒ ⇒ 而 S8 是 G1 最后一关 ⇒ ⇒ 答错 = 板改第二次** ★
★**④ 与兄弟单的关系**: ★**ISS-307 (hw-lead · 04:2x verified) 交了 ESD 选型候选集 ⇒ 老板的 W-2 / W-1b / W-1c 现在拍得动了 ⇒ 本单接着把【S8 侧】也拍得动 (⇒ 老板能一次开跑, 而不是开跑一半卡住)★** ★
★**⑤ 不造活**: ★**sw-lead / mech-lead 名下 open=0 · fixing=0 · 各自的闸全绿 ⇒ 本轮不给他们硬造活 (★只派这一条)★** ★
