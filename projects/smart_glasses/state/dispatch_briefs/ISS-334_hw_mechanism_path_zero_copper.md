【ISS-334 · hw-lead · ★★机制级路线: 零铜网「换机制」 (成对走廊 / 换层绕开 / 路由器本体) · 逐网死因归类 + 候选臂设计 + 沙盒预演方案 + 逐字作业包 (★零写板·零落表·零改闸·零改生成器★)★★】

★**这是 main 2026-11-18 23:5x 新开的单 (job cron fb67af40「ARS45 队列自动派活」)· ★派活前置三条: ① `state/advance.py --json` 实读 `internal: []` ⇒ 三个总工名下零 open 零 fixing (本单是本轮唯一新单) ② 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ PCB 线可派 ③ ★**「板只改一次」铁律 ⇒ 本单只出【纯分析 / 作业包】, 一个字节都不许写板**★**

---

## ★★★【① 现状 (★全部本机实读·不许抄任何文档里的旧数★)】★★★

- 板 `HW/PCB/demo_mainboard.kicad_pcb` · md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` ⇒ **12 天逐字节未动**
- `python3 state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` ⇒ **rc=0 · DRC 0 · unc 45 条** (★43 网名·★从 DRC JSON 端点自己解析, 别抄表★) · 走线 **18092 段** · 过孔 **433**
- ★**成功判据的唯一尺子 = 名单制闸**: `python3 state/compare_arm_official.py --self-test` ⇒ 本机实跑 **ALL TESTS PASS · rc=0** (★它用实测的 v44/v46/v47 坏案例当回归用例★) ⇒ 硬指标五条:
  ① DRC 必须 = 0
  ② **退铜名单空** (官方有铜 ⇒ 候选零铜)
  ③ **差分对死腿空** (官方双边有铜 ⇒ 候选单边零铜)
  ④ 计数类 (unc / 零铜网数 / 差分单边零铜对数) **不变差**
  ⑤ 至少一项严格变好
  ★★**"unc 变少"不算数; "计数持平"更不算数** (★v46 教训: 零铜网 26=26 · 单边零铜对 11=11 全平, 但名单换了 10 个, 其中 3 条本来通的差分腿被打成零铜★) ⇒ **必须比名单, 不能比计数** ★★
- 常用只读命令 (★都已实测存在, 用法照抄★):
  - `python3 state/compare_arm_official.py <候选板> <官方板>` (★exit 0 = 可晋级 / 1 = 不可★)
  - `python3 state/pair_copper_table.py HW/PCB/demo_mainboard.kicad_pcb` ⇒ 逐对铜长 (★0.000 = 零铜腿★)
  - `bash state/pcbnew_py.sh state/probe_unconnected_worklist.py HW/PCB/demo_mainboard.kicad_pcb state/official_18092_unc.drc.json --out tmp/iss334/01_worklist.md` ⇒ ★**这个脚本自己就把未连接分成「整网无铜 / 三脚网只通局部 / 端点缝」三类** ⇒ §1 直接引它, **不许自己另编一套分类**
  - `bash state/pcbnew_py.sh state/gate_live_check.py --arm-script <臂脚本>` ⇒ 「谁掐谁」表 (★返回 0 ⇒ 闸在这个臂上不生效 ⇒ 不许开臂★)
  - `bash state/pcbnew_py.sh state/probe_unc_map.py <板> <drc.json>`

---

## ★★★【② 为什么是这一单 (★两条布局处方已被两个臂证伪★)】★★★

| ★臂★ | ★判决★ | ★出处★ |
|---|---|---|
| ★ISS-325 左上臂★ | ★**REJECT**: 退铜 4 + 差分死腿 1 对 + 逐网孤岛 +9★ | `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` §7 |
| ★ISS-328 右上臂★ | ★**REJECT**: 退铜 2 + 逐网孤岛 +7 + 段数 3,986 vs 官方 18,092 ⇒ **不可比**★ | `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` §3 |

★★⇒ **「挪器件位置」这条路, 两个方向都死了** ⇒ 归零只剩三条路:
- **(a) 机制级** (★本单★): 官方板里「≥2 焊盘但一根铜都没有」的网 (★量级 12~24 个, **具体数字以你 fresh 读数为准, 不许抄 ISS-328 那张表**★) ⇒ 它们连铜都不存在 ⇒ 让路闸 / 挪器件对它一点用都没有 ⇒ **必须换机制**
- (b) 老板口径 (★W-2 / W-1c / A4 / W-3 / U-1 / P7 ⇒ 等老板那 8 个字母★)
- (c) 路由器本体

★**⇒ 本单 = (a) 的前三件: 清单 + 归类 + 臂设计 + 作业包** ★

---

## ★★★【③ 本单要交的四件 (★按顺序做·每件独立·一件没做完也要留痕·不许留空/编数★)】★★★

### ① §1 · 零铜网 0 号清单 (fresh 机器读数)
- 跑上面那两条只读命令, 对**官方板**逐网读出: 网名 / 焊盘数 / 端点 (ref+pad+坐标+层) / 有无铜 / 属于「整网无铜 · 三脚网 · 端点缝」哪一类
- 交付: 一张表 + 一句话结论 **「零铜网 N 个 = 哪几个网名」**
- ★**不许抄 ISS-322/ISS-325/ISS-328 里任何一张历史表** (★ISS-325 已实测: 那张 8 块板 unc 表是历史记录, fresh 重测 2 块对不上★)

### ② §2 · 逐网死因归类 (三桶)
每条零铜网必须归到且只归到一个桶, 每条给三样东西:
- **归桶依据**: 机器读数 + 出处 (★文件+行号 / 日志行·不许写「看起来像」★)
- **最小可试机制**: 一条 env 串或一个脚本调用 (★逐字★)
- **反向用例**: 什么读数能证明这条路不通 (★不许只写「失败」★)

| ★桶★ | ★病因★ | ★机制候选 (★env 名照抄 `state/gen_pcb_routing.py`·都是真存在的★)★ |
|---|---|---|
| ★A 成对走廊★ | 差分 P/N 同排互掐 / 走廊被占 | `PCB_PAIR_LAYERSEL` · `PCB_PAIR_AUTO_TRUNK` · `PCB_PAIR_SWAP_RETRY` · `PCB_PAIR_BEFORE_PWR` · `PCB_ROUTE_RESERVE` (★逐网预留走廊·看 `state/pair_corridor.py`★) |
| ★B 换层绕开★ | 端点几何卡死 (同排邻脚 / GND 铜皮 / 0.162mm 净距) | escape 方向分析 (`state/analyze_escape_dirs.py` · `state/probe_escape_feasibility.py`) + `PCB_ESC_STRAIGHT` · `PCB_ESC_STRAIGHT_NETS` · `PCB_ESC_CLR_FIX` · `PCB_ESC_ROWNORM` · `PCB_ESC_ROWNORM2` · `PCB_LAYERS` · `PCB_W_MIN` (★**只许在沙盒试·不许改真件默认值★★) |
| ★C 路由器本体★ | A* 搜索本身没找到路 (不是几何卡死) | ★**在产生点修**★: `state/patch_astar_gated.py` · `state/fix_unconnected_astar.py` · `state/fix_board_rip_guarded.py` (★注意 MEMORY 铁律: **修在产生点, 不许在产物上擦**★) |

### ③ §3 · 候选臂设计 (★只设计 + 判据, 不许在本单里跑长链★)
- 每桶 1 条「候选臂」+ 1 条「**同配方**对照臂」; 每条臂写死: env 串 (逐字) + 跑哪几个脚本 (逐字命令) + 预期耗时 + 产物落 `tmp/iss334/arms/<臂名>/` + 判据命令 (名单制闸 + DRC + unc) + 失败回退
- ★★**对照有效性自检 (★ISS-325/ISS-328 的血泪·必写·★★)**: 候选臂与对照臂必须在**可测量的量**上真不同 (落位 diff ≠ 0 **或** 读数 diff ≠ 0) ⇒ ★**若两者逐条相同 ⇒ 该臂作废, 不许当对照, 不许拿它的读数当功劳** (★ISS-325 左上臂两臂 185 个封装落位 diff=0 ⇒ 对照天然失效★)
- ★★**可比性自检**: 段数/过孔数必须与基线同量级 (★ISS-328 臂 3,986 段 vs 官方 18,092 ⇒ **不可比** ⇒ unc 45→29 一律不算数★) ⇒ 每条臂必须写「同工艺才可比」的自检方法

### ④ §4 · 逐字可执行作业包 (给「板那一趟」用)
`HW/PCB/BOARD_ONEPASS_S8_MECHANISM_ACTIONS.md` (新建): 按 S8 次序逐步写 **命令 + 验收读数 + 不过怎么办** ⇒ ★**板那一趟只照这份跑, 板 md5 只变一次**★

★**★沙盒预演 (可选·有严格时限·★)★**: 若你判断某条臂**裸板级**跑完 ≤ 20 分钟 ⇒ 可以在 `tmp/iss334/` 沙盒跑一条 (★只写 tmp/·★不许写 `HW/PCB/demo_mainboard.kicad_pcb`★) ⇒ ★**不许跑官方补丁链 (≈2h)·不许跑 `state/replay_patch_chain.sh`·不许跑任何会落盘到 `HW/PCB/` 的命令★ ⇒ 跑不完就写「**未跑 + 原因 + 预计耗时 + 下一轮跑**」★

---

## ★★★【④ 纪律 (★违反任意一条 = 本单不算交卷★)】★★★

1. ★**零写板**: 板 md5 + mtime **交卷前后各读一次, 必须逐字节相同** (`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413`)
2. ★**零落表** · ★**零改闸** (`state/gate_check.py` / `state/compare_arm_official.py` / `state/check_pcb_drc.py` / `state/check_pcb_nets.py` 一律只读) · ★**零改生成器代码** (`state/gen_*.py` / `state/patch_*.py` / `state/fix_*.py` 只许读) · ★**零改既有文档正文** · 不碰 `SW/` 与 `MECH/` 域 · 不碰别人的分片
3. ★**沙盒只写 `tmp/iss334/`**; 机器原始输出落 `logs/iss334/`
4. ★**写分片只能用 `python3 state/frag_write.py --agent hw-lead`** (★禁止 `open(p,"w")`★)
5. ★**零外发**: 不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律**自己网上查** + 标证据等级 (`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`) + 查不到就写**降级方案** ⇒ **没有「批一句可以发」这个选项**
6. ★**不替老板 / main 拍板**: 每条 need 给「问法 + 谁答 + 不答后果 + 建议默认值 + 建议排期」, ★**一条都不许自己定** ★
7. ★**不自签 `state/issue_log.yaml`**
8. ★**顺序死法 (★上一趟 ISS-333 cont2 就是死在这★)**: ★**先把文件写完 (作业包 + 交卷页 + 分片), 最后才跑必跑项** ⇒
   ```
   python3 state/merge.py ; echo "MERGE_RC=$?"
   python3 state/gate_check.py ; echo "GATE_RC=$?"      # ★Q1 必须 18/18★
   python3 state/issue_check.py ; echo "ISSUE_RC=$?"
   ```
   ★**各只许跑一次·加 timeout·`gate_check` 不许 `--json`** ★
9. ★**长生成停顿死法 (★上一趟 ISS-328 cont4 死在这★)**: ★**正文逐字给出 + 每块一次 write (≤ ~25 行) + 不许在写第一块之前跑任何探查** ⇒ 每完成一块立刻落盘 ⇒ ★**永远盘上有东西** ⇒ 回复 ≤ ~800 字

---

## ★★★【⑤ 交付物 (★路径逐字★)】★★★

| # | ★路径★ | ★内容★ |
|---|---|---|
| ① | ★**新建** `HW/PCB/ONETRIP_S8_MECHANISM_PATH.md` | §0 口径与边界自证 / §1 零铜网 0 号清单 (fresh) / §2 逐网死因归类 (三桶 + 反向用例) / §3 候选臂设计 (含对照有效性自检 + 可比性自检) / §4 沙盒预演读数 (或「未跑 + 原因 + 预计耗时」) / §5 need 列表 (交 main 拍·不代拍) / §6 复现命令 (逐字) |
| ② | ★**新建** `HW/PCB/BOARD_ONEPASS_S8_MECHANISM_ACTIONS.md` | ★**「板那一趟」的逐字作业包**: 每步 = 命令 + 验收读数 + 不过怎么办 (★板 md5 只变一次★) |
| ③ | ★**新建 (交卷页)** `HANDOFF/2026-11-18_hw-lead_ISS334_机制级换机制路线.md` | B0 一句话结论 / B1 结论摘要 / B2 验收标准自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令 |
| ④ | `logs/iss334/` + `tmp/iss334/` | 机器原始输出 + 沙盒 |
| ⑤ | `state/fragments/hw.yaml` | 走 `frag_write.py --agent hw-lead` (needs_from + interface_claims + status) |

★**门禁关键词 (★`state/gate_check.py` 按标题关键词认块·缺一块 Q1 就红·照抄这些词进标题★)★:
- B1 → 结论 / 一句话  ·  B2 → 验收标准 / 自评  ·  B3 → 证据分级  ·  B4 → 接口取值 / 接口声明 / interface_claims  ·  B5 → 阻塞 / 卡点 / 未决  ·  B6 → 复现 / 自证
★**占位符必须 0**: `<!-- ` · `🔄|待填|PLACEHOLDER|施工中` · `__[A-Z_]+__` ★(★你在 B6 里写这两条 grep 命令本身会被扫到 ⇒ 用转义写法, 别自匹配★)

---

## ★★★【⑥ 交卷回复格式 (★最后一条消息★)】★★★

```
ZERO_COPPER_NETS=<数>
ARM_DESIGNED=<数>
WORKPACKET_BYTES=<数>
MERGE_RC=0
GATE_RC=0
BOARD_MD5=611b869e13518c3c023fb178f91a0075
```
★**再附 ≤8 行摘要**: 三桶各几条 / 每桶最小可试机制是什么 / need 几条交 main 拍 / 沙盒预演跑了没 ★
