# ISS-322 · hw-lead · ★★「板只改一次」那一趟的 S8: 布线归零 (unconnected 45 → 0) 死因逐条登记 + 高速腿几何可布性判定 + 布线作业包★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-322
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 11:0x** ★
> ★**性质**: 内部活 · ★**纯分析 / 作业包 / 判据设计类 (HW 侧)** ★ · 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM/原理图真源 · 沙盒只写 `tmp/` · 零外发 · 不替老板拍板 · 不自签 issue_log
> ★**上游**: `ISS-311` (板那一趟重出清单 · verified) · `ISS-314` (S1 改名口径 · verified) · `ISS-317` (S1 逐条改名清单 · verified) · `ISS-265` (S8 死因 5 条)

---

## ★0 · 主线口径 (★老板 2026-11-17 00:43: 「接下来的目标是绘制 PCB 图」★)

★**当前主线 = 绘制 PCB 图** ⇒ ★**布线 / 布局类 ISS 现在【可派】** ★
★**但「板只改一次」⇒ 派 PCB 单的纪律 (★老板口径★)**:
1. ★**先派【纯分析 / 作业包】类 (★不动板★)** ★ ⇒ ★**本单就是这一类** ★
2. ★**真动板那一趟必须一次做完** (★位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出·同一趟·背靠背·不许拆两趟★) ⇒ ★**本单就是给那一趟造「布线那一段」的作业包** ★
3. ★**原理图/网表侧只派【不改网表真源】的活** (★板要对着一个不再变的网表画★) ⇒ ★**本单零碰网表真源** ★

---

## ★1 · main 11:0x 本机实读的事实 (★你的活从这些数开始, 不许自己重测当基线★)

| # | 事实 (★main 本机实跑★) | 怎么复现 |
|---|---|---|
| ① | ★**现役板 `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413`** ⇒ **零写板双证的基线值** | `md5sum HW/PCB/demo_mainboard.kicad_pcb` · `stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb` |
| ② | ★**DRC violations = 0 · unconnected items = 45** (★骨架阶段所以 C4 不是红★) | `python3 state/check_pcb_drc.py` (★输出里 C3/C4 两行★) |
| ③ | ★**`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S8 = 「布线归零 (unconnected 45 → 0)」· ★**它是作业包里唯一写着「可能整趟做完仍然投不了板」的步** ★ | 读该文件 §3-S8 段 |
| ④ | ★**§3-S8 里两个数打架**: 「45 条里 **23** 条是高速 DSI/CSI 腿」 vs 「官方板 (160×100/8L) 这 **13** 条 DSI 腿自己一根都没布通」 ⇒ ★**23 与 13 必查清 (是子集? 是写错了? 是两批? ★)★ | 同上 |
| ⑤ | ★**§3-S8 已登记 5 条死因 (非 DSI/CSI 那 22 条里)**: A1 (`BAT_DET` 终点未定义) · W-1/W-2 (ESD 未拍 ⇒ 器件钉位定不下来) · W-4 (`Q_PG.3` 极性未定) · `D_LED_G` 物理位置 (★`LED_G_D` 走线 **93.49 mm**★) · `FSIN_OUT` **3.01 mm** 布不通 (★疑似逃逸方向 bug★) | 同上 |
| ⑥ | ★**`state/UNC_TARGET_MAP.md` 的基线是 2026-11-11 的 (unc **29** 条 / **22** 个网名 · 基线板 `state/.lastgood/baseline_v76mw0_chain.kicad_pcb`) ⇒ 与现役板 (45) 对不上 ⇒ ★**基线过期, 必须先对齐** ★ | 读 `state/UNC_TARGET_MAP.md` |
| ⑦ | ★**官方板 18092 的 unc 列表在盘上**: `state/official_18092_unc.drc.json` (含 `unconnected_items` 数组) ⇒ ★**官方板自己也没布通的那些 ⇒ 归「几何/框级」桶, 不归「算法」桶** ★ | `python3 -c "import json;d=json.load(open('state/official_18092_unc.drc.json'));print(len(d['unconnected_items']))"` |
| ⑧ | ★★**同型事故史 (★项目铁律·写在 MEMORY 里·本单必须并进去★)★**: **v44 / v46 / v47 / v48 四个臂全部打死同样三条差分腿** (`DSI_D0_CK` · `DSI_D0_CK_SRC` · `DSI_D0_D1`) ⇒ ★**根因在布局, 不在路由算法** ⇒ ★**⇒ 你要判的第三条: 这 3 条在现役板上是不是同一个死法? 若同 ⇒ S8 就不是「调路由参数」能解决的** ★ | `state/_fail_detail_v4[4-8]_R.json` (★8 个文件·逐字读 fail_detail 的 start/goal★) |
| ⑨ | ★**`state/compare_arm_official.py` 的【名单制】判据** (★退铜名单空 + 差分死腿空 + 逐网孤岛空 + rc=0 ACCEPT★) 是那一趟布线的验收口径 ⇒ ★**本单每条修法都要挂得住它** | `python3 state/compare_arm_official.py --self-test` (★必跑一次·看它自己的反向用例★) |
| ⑩ | ★**闸链现状**: `python3 state/gate_check.py` ⇒ ★**rc=1** · ★**唯一红项 = 「ISS-318 SW 侧位号引用可达性闸」· 18 条真隐患全部来自 `SW/ONETRIP_SW_RENAME_SAFETY.md` (★sw-lead 10:47 写的·★属 SW 域·与本单无关★)★ ⇒ ★**你交卷时 rc 仍是 1 是正常的, 但必须把这条红单独归因 (逐字贴出来 + 说明它的输入面不含本单任何文件) ★** ★ | `python3 state/gate_check.py` |

---

## ★2 · 本单要交的东西 (★6 件·缺一不算交卷★)

### ★① 45 条 unconnected 逐条清单 (★机器搬·一行不许手抄·一条不许少★)

- ★**数据源**: 现役板 (★md5 见 §1-①★) ⇒ `python3 state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` ⇒ 它会把 DRC JSON 写到 `/tmp/_pcb_drc_<板名标签>.json` (★看 `state/check_pcb_drc.py` L109~L119★) ⇒ 取 `unconnected_items` 数组 ★
- ★**每条至少这 8 列**: `#` · `网名` · `起点(ref+pad+x,y)` · `终点(ref+pad+x,y)` · `长度mm` · `类型(高速 DSI/CSI ⇄ 普通)` · `死因桶` · `修法`
- ★**自证**: 条数必须 = **45** (★与 `check_pcb_drc.py` 的 C4 行逐字一致★) ⇒ 不一致就是抄错了

### ★② 逐条死因登记 (★机器判据·不许推算·不许「疑似」糊过去★)

- ★**必须用现役探针出读数** (★先确认文件存在再用·不存在就写 `[0数据]` + 降级方案★):
  `state/probe_unc_map.py` · `state/classify_unc.py` · `state/probe_net_rootcause.py` ·
  `state/gate_live_check.py` (★读法: `bash state/pcbnew_py.sh state/gate_live_check.py --arm-script state/v76mw_arms.sh` · ★它给「谁掐谁」全表 + k 值★) ·
  `state/cmp_unc_sets.py` (★现役板 unc 集合 ⇄ 官方板 unc 集合 差集★)
- ★**并进来的三份既有结论 (★不许重做·不许改口径·只许对齐/补差★)**:
  1. §1-⑤ 的 5 条死因 (作业包 §3-S8 登记的)
  2. `state/UNC_TARGET_MAP.md` 的三桶 (★被 GND 掐 9 · k≤3 非 GND 3 · k=12 差分配对 14★) + ★**它的基线是 unc 29 / 22 网名 ⇒ 与现役板 45 对不上 ⇒ 你要出「差集表」: 多了哪些 / 少了哪些 / 为什么** ★
  3. §1-⑧ 的同型事故史 (v44/v46/v47/v48 打死同 3 条差分腿 ⇒ 布局级)
- ★**桶定义 (★本单自定·但每条必须落进且只落一个桶★)**: `几何不可布` (★框/布局级·必须改布局或板框★) · `算法可解` (★让路闸 / 换层 / pair-aware / 逃逸方向★) · `口径未定` (★A1 / W-1 / W-2 / W-4 这类「拍板前连钉位都定不下来」的★) · `官方板同病` (★官方板自己也没布通⇒ 佐证「几何级」★)

### ★③ ★★最关键的一条: 23 条高速 DSI/CSI 腿的【几何可布性判定】★★

★**这是本单存在的理由 —— 板那一趟能不能一次做完, 取决于这个结论** ★

- ★**先解决 §1-④ 的数打架**: 23 还是 13? ⇒ ★**用机器数出来 (不许抄作业包那句)★** ⇒ 交卷页写清「两个数各指什么」
- ★**判定口径 (★机器可判·两个结论二选一★)**:
  - **(a) 几何可布** ⇒ 缺的是走线 / 层选 / 让路 ⇒ 属**可解** ⇒ 那 23 条走 §2-④ 的修法
  - **(b) 几何不可布** ⇒ ★**必须先改布局或板框 ⇒ ⇒ 板 md5 第二次变 (2-4 周 + ¥4-8K) ⇒ ⇒ 这是本单最贵的结论, 必须量化到「差多少 mm / 哪条走廊 / 挪哪个器件」★ ★
- ★**必须用现役探针出读数**: `state/probe_dsi_corridor.py` · `state/probe_pair_lane.py` · `state/probe_corridor_block.py` · `state/probe_escape_feasibility.py` · `state/pair_corridor.py` · `state/probe_lane_conflicts.py` · `state/probe_crossover.py` · `state/probe_csi_order.py` (★存在性自己先核·缺的写 `[0数据]`★)
- ★**官方板对照 (只读)**: `state/official_18092_unc.drc.json` ⇒ ★**官方板也没布通的那几条 ⇒ 归「官方板同病」桶 ⇒ 这是「几何级」的旁证** ★

### ★④ 逐条修法 + 落表批次 + 逐条验收命令 (★那一趟照着就能干★)

- ★**每条**: 修法类别 (让路闸 / 换层 / pair-aware / 改逃逸方向 / 改布局 / 改板框 / 改判据 / 等拍板) · 代价 (人日 + 板 md5 是否会变) · ★**落表批次 (BATCH-1/2/3, ★与 `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` §1-3 的批次口径对齐·不许另起一套编号★)★** · 逐条验收命令 (★逐字可粘贴★)
- ★**批次纪律**: ★**同一批次 = 同一个落表单号 · 背靠背 · 不许拆成两趟** ★ (★与 ISS-317 §1-3 逐字一致★)
- ★**每条修法都要挂得住 §1-⑨ 的名单制判据** (★不许写「调一下路由参数就好了」这种挂不住的句子★)

### ★⑤ 需要老板 / main 拍的死结清单 (★本单不代拍★)

- 逐条列: ★**need key** ★ · 一句话问法 · 谁答 · ★**不答的后果 (★量化: 板 md5 第几次变 / 投不了板 / 假绿风险★)★** · 建议默认值 · 建议排期 (★批次顺序·日期老板定★)
- ★**已知至少 4 条**: A1 (`BAT_DET` 终点) · W-1/W-2 (ESD 架构 ⇒ `D_ESD_USB_D` 器件钉位) · W-4 (`Q_PG.3` 极性) · `D_LED_G` 物理位置 (★依赖 MECH 侧落位★)
- ★**不许把「等外部 / 等老板」当成阻塞项挂着** ⇒ 每条都要给降级方案 (★自己网上查 + 证据等级 + 查不到就写降级路径★)

### ★⑥ 交卷物 4 件 + 分片 + 证据分级 + 零写板双证

| # | 交付物 | 要求 |
|---|---|---|
| ① | ★**本单新建**: `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` | §0 口径与边界自证 · §1 45 条逐条清单 (★机器搬★) · §2 逐条死因登记 + 三桶 · §3 ★高速腿几何可布性判定 (★结论 + 量化缺口★)· §4 逐条修法 + 批次 + 验收命令 · §5 待拍死结 · §6 证据分级 · §7 文件清单 · ★**占位符 0** ★ |
| ② | ★**本单新建**: `HANDOFF/2026-11-18_hw-lead_ISS322_S8布线归零作业包.md` | B0~B6 齐全 (★照 `HANDOFF/2026-11-18_hw-lead_ISS317_S1位号改名可执行清单.md` 的 B0~B6 写法★) · ★**占位符 0** ★ |
| ③ | ★**`logs/iss322/`** (★新建·只写自己这一份★) | 原始输出 (★每个读数都有对应 raw 文件·★交卷页引用的日志必须真的存在, 不许留悬空引用★) + 探针脚本 |
| ④ | ★**`state/fragments/hw.yaml`** (★只写自己这一份·★**必须用 `python3 state/frag_write.py --agent hw-lead` 原子写, 禁止 `open(p,"w")`★★) | artifacts + needs + claims ≥ 各 1 · status 换 ISS-322 |

★**证据分级 (★四档标齐★)**: `[官网]` (厂商官网 / 官方 datasheet) · `[实测]` (本机可复现) · `[媒体]` · `[推算]` · `[0数据]` (查不到) ★
★**零写板双证**: 板 md5 仍 = `611b869e13518c3c023fb178f91a0075` 且 mtime 仍 = `2026-11-06 07:07:17.362193413` (★交卷前后各测一次·两次都要贴出来★)

---

## ★3 · 交卷前必跑 (★输出原样贴进回复★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/compare_arm_official.py --self-test          # ★必须 rc=0 (看它自己的反向用例)★
python3 state/merge.py                                        # rc 必须 0
python3 state/gate_check.py                                   # Q1 必须 18/18 · ★rc 当前是 1 (见 §1-⑩) ⇒ 必须逐字归因★
python3 state/issue_check.py                                  # rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb                        # = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb                  # = 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中" HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md   # = 0
grep -c "ISS-322" state/fragments/hw.yaml                      # >= 1
```

★**★如果 `gate_check.py` 的 rc=1 且红项只有「ISS-318 SW 侧位号引用可达性闸」⇒ 那是 SW 域的既有红, 不是你的红** ★
★★**但不许为了凑 rc=0 去动 SW 域文件 / 不许改闸 / 不许改基线** ★★ ⇒ **正确做法: 逐字把那条红贴出来 + 说明「该闸输入面不含本单任何文件」+ 证明办法 (★挪走那个 SW 文件后该闸 rc=0 ⇒ 证明红不在你这边·★同类证明 ISS-317 已经做过一次, 见 `logs/iss317/09_merge_gate_output.txt` 开头★)★**

---

## ★4 · 边界 (★违反即交卷不算★)

| # | 边界 | 说明 |
|---|---|---|
| ① | ★**零写板** ★ | 板 md5 / mtime 交卷前后逐字节相同 (★沙盒只许写 `tmp/iss322/`★) |
| ② | ★**零落表** ★ | 不许写任何落表物 / 落表台账 |
| ③ | ★**零改闸** ★ | `state/gate_check.py` · `state/compare_arm_official.py` · `state/check_pcb_nets.py` · `state/check_pcb_drc.py` 一个字节不许改 |
| ④ | ★**零改网表/脚表/BOM/原理图真源** ★ | 只读 |
| ⑤ | ★**零改既有文档正文** ★ | 新建文件为主; 要改既有文档的, 只在交卷页给「逐字改法 + 行号」给 main |
| ⑥ | ★**不替老板/main 拍板** ★ | 只给选项 + 代价 + 建议默认值 + 不拍的后果 |
| ⑦ | ★**不自签 issue_log** ★ | `state/issue_log.yaml` 里 ISS-322 的 status / verify_result 留给 main |
| ⑧ | ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 需要外部资料一律**自己网上查** + 标证据等级 + 查不到写降级方案 ⇒ ★**没有「等原厂回信」这个选项** ★ |
| ⑨ | ★**只写自己那一份分片** ★ | `state/fragments/hw.yaml`; `hw.yaml`/`sw.yaml`/`mech.yaml`/`pm.yaml` 一个字节不许碰 |
| ⑩ | ★**沙盒跑完删干净** ★ | `tmp/iss322/` 交卷前清空 |

---

## ★5 · 给 main 的 need (★本单不代拍·逐条登记到分片的 needs 里★)

★**need key 建议前缀**: `iss322_s8_*` · ★**每条必须带: 一句话问法 + 谁答 + 不答的后果 (量化) + 建议默认值 + 建议排期** ★
