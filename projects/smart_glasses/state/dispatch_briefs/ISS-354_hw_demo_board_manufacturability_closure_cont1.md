# ISS-354 · hw-lead · ★demo 主板可制造性收口 (SoM 座 pin1 排向 + 封装/脚号不自洽 + BOM 待选型) · ★**cont1 续做**★ · 纯查证 · 零写板

★**这是 cont1 续做派活 (★不是从零重开★)** ★

## ★★为什么是 cont1 (★上一趟怎么死的·本趟从哪儿续★) ★★

★**上一趟 (2026-11-23 04:2x 派) 的会话被掐死了, 但产物部分在盘** ⇒ ★**本单 = 从已完成位置续做, 不是从零★**

★**死因 (★main 本机实读, 不抄任何 agent 报告★)**: ★**兄弟 job `fb67af40` (ARS45 队列自动派活) 那一趟 cron 自己超时了** ⇒ 错误原文 `cron: job execution timed out (last phase: model-call-started)` (★`~/.openclaw/cron/runs/fb67af40-a9eb-4cdd-a842-8cbb8fdd7865.jsonl` 逐字★) ⇒ ★**父 run 一死, 它派出的两个子会话在同一瞬间被连带 abort** (★hw-lead 子会话 `4a01dc6e` 的 `endedAt` 与 sw-lead 子会话 `b0220170` 相差 114 ms = 同一瞬间死的·`abortedLastRun: true`★) ⇒ ★**不是 hw-lead 自己的问题, 是父 job 超时连带** ★

★**上一趟最后一条消息 (★实读自会话 `4a01dc6e` 的 transcript·不是抄交卷报告★)**:
> "Board footprints measured. Now let me compare against KiCad official footprints and pull TI datasheets locally (PDF → text)."

★**已在盘的产物 (★别重做·直接用★)** ⇒ 全在 `logs/iss354/datasheets/` (★4 份官方 datasheet PDF·★已经下好了·直接读, 不用再上网找★):

| 文件 | 器件 | 对应本单第 (2) 件事的哪个 ref |
|---|---|---|
| `tps7a20.pdf` (8,987,703 B) | TPS7A20 (5 脚: 1=OUT, 2=GND, 3=EN, 4=IN, 5=Pad) | ★**`U_LDO_S28`** (★板封装只落 4 焊盘 (1,2,4,5) ⇒ **缺 EN(3)**★) |
| `tps3808g01.pdf` (986,585 B) | TPS3808G01 (SOT-23-6, 6 脚) | ★**`U_SUPV`** (★板封装只落 4 焊盘 (1,4,5,6) ⇒ **缺 GND(2) 与 MR(3)**★) |
| `bq2970.pdf` (1,502,110 B) | BQ2970 (SOT-23-6) | ★**`U_BATPROT`** (★板封装 6 焊盘但编号 **2..7** ⇒ 与符号 1..6 不对齐★) |
| `csd16406q3.pdf` (452,762 B) | CSD16406Q3 (SON-8 3.3×3.3) | ★**`Q1` / `Q2`** (★板封装 5 焊盘 (2,3,4,5,6) + 外形 4.94×5.0 ≠ SON-8 3×3★) |

★**没做的 (★本趟要补的就是这些★)**:
1. ★**交卷页** `HANDOFF/2026-11-23_hw-lead_ISS354_*.md` — ★**完全没写** (★HANDOFF 目录下 `ISS-35[34]` 两个交卷页都不存在★)
2. ★**分片登记** — ★**`state/fragments/hw.yaml` 里 `iss354` 命中 = 0** (★实测 grep 四个分片文件全是 0★) ⇒ ★**上一趟的结论一个字都没进台账★**
3. ★**PDF → 文本没做** — ★**上一趟正要做这一步就被掐死了** ⇒ ★**datasheet 已在盘, 直接转文本读引脚表★**
4. ★**改项清单没写** — `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的追加段 (★零行加进去★)
5. ★**下料前一票否决项没写** — `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的追加段 (★零行加进去★)
6. ★**BOM 里 OPN 待选型的候选没查**
7. ★**本单自带的闸** — ★**没有新建** (★必须交付一个能跑的、带 `--selftest` 反向用例的独立脚本★)

★**纪律**: ★**「不信上一趟」** ⇒ ★**datasheet 的引脚表你要自己从 PDF 转文本后读出来核对, 不许直接抄 brief 里的症状描述当作结论★ ★

---

## ★★本单只做 3 件 (★纯查证/作业包类 · 零写板★) ★★

★**任务书全文 = `state/dispatch_briefs/ISS-354_hw_demo_board_manufacturability_closure.md`** ⇒ ★**先把它读完, 它的 3 件交付物定义、边界、必跑项一律照办, 本页只说「从哪儿续」★**

### (1) ★**SoM 座 pin1 「哪一排」= 无定论 ⇒ 出降级方案 + 下料前检查项★**

★**已知 (★`HW/PCB/SOM_CONNECTOR_GEOMETRY_PROBE.md` 已查清的部分, ★**别重查, 直接用**★)**:
- P1 = (51.0, 3.5) / P2 = (51.0, 46.5) / P3 = (17.0, 3.5) / P4 = (17.0, 46.5) (mm, SoM 顶视, 原点=左下角)
- ★**pin1 在哪一「端」已定**: 四个座的 pin1 全在各自连接器的 **+x 端** (P1/P2 在 x=60.8 朝 x=68 板边; P3/P4 在 x=26.8 朝板中心 x=34), 脚号从该端往 −x 递增
- ★**pin1 在哪一「排」(y 大的一排 / y 小的一排) = ★无定论★** ⇒ ★**载板焊盘若把两排做反 ⇒ 该座 100 个网络全部对调 ⇒ 板子白打** ★
- ★**DF40C-100DS-0.4V(51) 原厂推荐 PCB 焊盘图的全部标注数值** 已在 §4 (pad 宽/长/两排中心距) + 可点开的 URL ⇒ ★**直接用, 不要自己再找一遍★**

★**本单要交的是**:
- ① ★**降级方案 (三条并列, 写清代价)**: (a) ★**按官方推荐焊盘图落盘** (b) ★**板侧加防呆/标注 (丝印 pin1 三角 + 缺口) ⇒ 不改电气, 只降低装反概率** (c) ★**两排镜像兼容的可能性评估** (★若器件是对称封装/信号可交换, 能不能设计成「装反也能通」⇒ 若不能, 就明说不能★) ⇒ ★**结论不许含「等原厂确认」** ⇒ ★**没有原厂确认就按「最坏假设 = 两排可能反」来写方案** ★
- ② ★**下料前必须核对的一票否决项** ⇒ ★**追加**到 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★追加式, 老字别删★): 写清「★什么状态下不许下料★」+「★用什么手段核对★」(★手册底面图 / 原厂 3D / 实物照片 / 样件通电对称性★) + 「★核对不到怎么办 (降级: 改设计路径绕开它)」★

### (2) ★**5 个 ref / 4 类 封装与脚号不自洽 ⇒ 查官方 ⇒ 出板那一趟改项清单★**

★**病灶 (★`HW/PCB/PIN_REALITY_GAP.md` §2 已定位, ★**别重跑一遍去发现, 直接用, 但**每条都要自己从 PDF 核对确认**★)**:

| ref | 症状 (板文件实测) | datasheet (★已在盘★) |
|---|---|---|
| `Q1` | BOM footprint=SON-8 Q3 3.3×3.3mm; 板封装只画 **5 焊盘 (2,3,4,5,6)** 且外形 **4.94×5.0mm ≠ SON-8 3×3** | `csd16406q3.pdf` |
| `Q2` | 同 `Q1` | `csd16406q3.pdf` |
| `U_BATPROT` | BOM opn=BQ2970 (SOT-23-6); 板封装 6 焊盘但编号 **2..7**, 与符号 **1..6** 不对齐 | `bq2970.pdf` |
| `U_LDO_S28` | TPS7A20-28 (5 脚: 1=OUT,2=GND,3=EN,4=IN,5=Pad); 板封装只落 **4 焊盘 (1,2,4,5) ⇒ 缺 EN(3)** | `tps7a20.pdf` |
| `U_SUPV` | TPS3808G01 类 (SOT-23-6, 6 脚); 板封装只落 **4 焊盘 (1,4,5,6) ⇒ 缺 GND(2) 与 MR(3)** | `tps3808g01.pdf` |

★**本单要交的**: 逐个从 PDF 读引脚表判定 ★**正确封装 + 正确脚号** ⇒ 出**改项清单**: ★**每条 = ref / 现封装 / 应为封装 / 差异 / 证据等级 / 下料前必须核对与否 / 连带影响 (是否影响别的网)★** ⇒ ★**追加**到 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的**新段** (★追加式, 老字别删★) ⇒ ★**这是「板那一趟」的输入, 本单不改板** ★

★**★不许手写进 `HW/PCB/PIN_REALITY_GAP.md`★**: ★**它是 `python3 state/gen_kicad_sch.py --pin-gap` 的产物 ⇒ 重跑即冲掉 ⇒ 要么把结论写进生成器, 要么落到独立文档 / 作业包, 不许直接改那个页** ★

### (3) ★**BOM 里 OPN 仍「待选型」的器件 ⇒ 自己查官网 ⇒ 给候选 + 代价 (不代拍)★**

★**做法**: ★**读 `HW/BOM_v1.csv` 找出 OPN/封装仍标 `[0数据]` / 「待选型」的器件** ⇒ ★**自己网上查厂商官网 (在售型号 + 关键参数 + 是否在售 + 封装是否与现有板封装兼容) ⇒ 给 **2~3 个候选 + 各自代价 (封装是否要改 / 是否有交期风险 / 是否要多加外围元件)**** ⇒ ★**只给候选与代价, 不落表、不代老板拍** ★ ⇒ ★**查不到的写 [0数据] + 降级方案** ★

★**★外发禁令 (★本单最容易踩的一条★)★**: ★**不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 没有「批一句可以发」这个选项★) ⇒ ★**`state/outbox/` 里的草稿一律不发, 只作资料留档** ★

---

## ★★边界 (★一条都不许越★) ★★

- ★**零写板**: `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 必须是 `611b869e13518c3c023fb178f91a0075` / mtime 必须是 `2026-11-06 07:07:17.362193413` ⇒ ★**开工前 + 交卷后各打一次, 双证贴 §B6** ★
- ★**零落表**: 不改网表 / 脚表 / BOM / 原理图 / 任何闸 / `state/fragments/pm.yaml` / `state/fragments/sw.yaml` / `state/fragments/mech.yaml` / `state/issue_log.yaml` (★自签 issue_log 是 main 的地界★)
- ★**只写**: `state/fragments/hw.yaml` (★只走 frag_write.py★) + `HANDOFF/2026-11-23_hw-lead_ISS354_*.md` + `logs/iss354/` + `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的追加段 + `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的追加段 (★**只追加, 零删除既有行**★) + `tmp/iss354/` (★沙盒★)
- ★**零外发 / 零采购 / 零联系供应商**
- ★**不替老板拍板** · ★**不新增拍板项** (★C_VBUS_GND 留位 / ESD 架构轴 / U-1 画哪块物理产品 这些是老板的项, 本单只登记事实与影响, 不代拍★)
- ★**证据分级必标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`
- ★**不许改既有闸的判据方向** · ★**不许动 `state/gate_check.py`** · ★**不许动 `state/merge.py`**
- ★**本单与 U-1 (画哪块物理产品) 无关** ⇒ ★**交的是器件级/几何级事实与改项清单, 不碰板坐标/层数/尺寸 ⇒ 不因 U-1 未拍而卡住** ★

## ★★必跑项 (★交卷前跑, 把原样输出贴进交卷页 §B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp          # ★/tmp 配额已打满·必写盘的动作一律落项目盘★
python3 state/merge.py            # rc 必须 0
python3 state/gate_check.py        # rc 必须 0 · Q1 必须 18/18
python3 state/frag_write.py --agent hw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```

★**本单自带的闸** (★**新写**一个只读判定脚本, ★**文件名与路径你自己定** (★放 `HW/` 下, ★**交卷页里写清你定的那个路径★)★)): ★**判据 = ① 5 个 ref 逐条: 现封装 vs 查得的应封装 ⇒ 逐条点名, 状态只认「已定位」/「仍未定位」; ② BOM 里 OPN 仍 `[0数据]` 的器件名单 (★**列名单, 不许只报数**★); ③ preflight 追加段是否含「下料前一票否决项」; ④ 作业包追加段是否含改项清单 ⇒ 输出带名单, 只报数量 ⇒ rc=1** ★ ⇒ ★**须带 `--selftest` 反向用例 (★故意在临时副本里去掉其中一条 ⇒ 必须被抓出来★)** ★

★**任务书全文**: `state/dispatch_briefs/ISS-354_hw_demo_board_manufacturability_closure.md` (★`python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-354_hw_demo_board_manufacturability_closure.md` ⇒ rc=0★)
