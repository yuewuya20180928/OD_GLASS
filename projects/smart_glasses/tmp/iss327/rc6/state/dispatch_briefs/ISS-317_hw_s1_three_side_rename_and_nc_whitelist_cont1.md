# ISS-317 · hw-lead · ★★cont1 续做说明★★ (★僵尸 fixing 重派 · 不是从零重做★)

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-317
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 09:1x** ★
> ★**原任务书全文 (★一个字不许删★)**: `state/dispatch_briefs/ISS-317_hw_s1_three_side_rename_and_nc_whitelist.md` (14,711 B)
> ★**性质不变**: ★**内部活 · 纯分析 / 作业包 / 判据设计类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★0 · ★为什么有这张 cont1 (★main 09:1x 本机实读, 不抄任何 agent 报告★) ★

★**上一趟子会话**: `agent:hw-lead:subagent:6d3d6815-5d3c-47a9-9de9-a9b6637d9806` (taskName `queue_iss317`)
⇒ ★**08:39:03 起 · 08:49:57 死** ★ · ★**runtimeMs=651204 · status=timeout · abortedLastRun=true** ★
⇒ ★**死因 = 父 cron run 结束时子会话被连带 abort (★与 ISS-308 / ISS-309 同一个死法★) ⇒ 不是 hw-lead 的错, 是派活机制的错** ★
⇒ 最后一话停在: 「Now let me fix T5 to use the correct construction. Let me check the chain anchor's CLI and how it consumes the pins table.」★

★**⇒ 上一趟 = 僵尸 fixing**: ★**交卷页不存在** (`HANDOFF/` 下 `ISS317` 命中 0) · ★**hw 分片没更新** (`state/fragments/hw.yaml` mtime `08:05:34` · status 段仍写 ISS-305 ⇒ `grep -c iss317` = 0) ★
⇒ ⇒ **hw-lead 整个被挡 (★advance.py 的 in_flight 规则: 同 agent 名下有 fixing 单 ⇒ 本轮不再派新活★)** ★

★**★但上一趟的分析成果【已经在盘上】(★main 09:1x 本机实读核对★) ⇒ ★**本单按【续做, 不是从零重做】处理** ★ ★

| 在盘成果 | 路径 (★实读 size + mtime★) | 内容 |
|---|---|---|
| ★**① 逐条改名清单 (★机器生成·非手抄★)** ★ | `logs/iss317/rename_list_raw.txt` (58,695 B · 08:45) | ★§A 四侧现值盘点 + §B 改名口径下的分组计数 + (后续 §C~ 未跑完)★ |
| ★**① 的生成脚本** ★ | `logs/iss317/iss317_gen_rename_list.py` (18,666 B · 08:45) | ★**只读**项目文件 ⇒ 零写板 / 零落表 / 零重生成 / 零改闸; ★口径单源 = `state/gen_kicad_sch.py::kicad_ref()` (★ISS-205 规则·逐字比对不一致就 abort★)★ |
| ★**T5/T6 沙盒造法脚本 (★写到一半★)** ★ | `logs/iss317/iss317_sb_make_t5t6.py` (15,242 B · 08:46) | ★**只写 `tmp/iss317_sandbox/`**; ★T5 = 映射歧义 (X 与 X_1 共存) · T6 = 板侧 ref 改成表侧没有的名字 ⇒ 期望 ③ 红★ |
| ★**C1 现状基线** ★ | `logs/iss317/01_c1_baseline_full.txt` (7,130 B · 08:40) | ★`check_pcb_nets.py` 现状读数全量★ |
| ★**BOM 导出原始输出** ★ | `logs/iss317/02_bom_export_raw.txt` (121 B · 08:44) | ★★**只有 121 B ⇒ 几乎肯定没跑完** ⇒ 补跑★ |

★**⇒ 本单第一步 = 读 `logs/iss317/rename_list_raw.txt` + `iss317_sb_make_t5t6.py` (★别重跑一遍基线, 别重新推一遍口径★)** ★

---

## ★1 · ★★main 09:1x 从 `rename_list_raw.txt` 里读出来的实测数字 (★你必须独立复核, 但别再从零推一遍★) ★★

★**§A 四侧现值盘点 (★[实测]★)** ★
```
脚表侧   HW/netlist_v1_pins.csv        : 218 个 ref
网表侧   HW/netlist_v1.csv (ref 列)    : 291 个 (含伪器件 RAIL_*/NET_* 75 个)
网表侧   真实器件宇宙 (ref ∪ 节点串)    : 218 个
BOM 侧   HW/BOM_v1.csv                 : 218 个 ref
原理图侧 11 页 .kicad_sch              : 218 个 ref
板侧     HW/PCB/demo_mainboard.kicad_pcb: 186 个封装
```
★**§A 口径一致性核对 (★这 5 条是判据的地基★)** ★
```
脚表 == BOM                      : True
脚表 ⊆ 网表真实器件宇宙           : True (差 0)
脚表 ⊆ 板侧                      : False (脚表有板无 32 个 ⇒ CHG_BOARD 件)
板侧 == 脚表 ∩ 本板               : True
原理图侧 == kicad_ref(脚表)        : True
```
★**§B 改名口径下的分组计数 (★[实测]★)** ★
```
改名宇宙 (表侧真实器件)              : 218
★要改 (末字符是字母 ⇒ 加 _1)        : 186
★不动 (末字符是数字 ⇒ 一律不动)      :  32   ← ★ISS-314 说的「30 个不动」是【板侧】口径, 表侧是 32★
  · 其中在板侧 (MAIN_PCB)            : 156 要改 /  30 不动
  · 其中不在板侧 (CHG_BOARD)         :  30 要改 /   2 不动
```
★**★⇒ 由此得到一条必须写进交卷页的结论 (★main 09:1x 的读法, 你要复核★)**: ★**「S1 位号改名」不是「板侧 186 个封装改名」, 而是【表侧 218 个 ref 里 186 个改名】(★其中 156 个在板上·30 个是 CHG_BOARD 件★) ⇒ ⇒ 板侧只动 156 个, 而网表/脚表/BOM/原理图四侧要动 186 个 ⇒ ⇒ ★**「三侧同口径」其实要动【五侧】(板 + 网表 + 脚表 + BOM + 原理图)★** ⇒ ⇒ ★**ISS-314 说的「三侧」在计数上是不完整的 ⇒ 这条要写进交卷页 §结论, 并给出五侧的逐条对照表★** ★

★**★另一条 (★必须处理, 不许绕开★)**: ★**`J_USB_C` 末字符是字母 ⇒ 在改名宇宙里 ⇒ 它会被改成 `J_USB_C_1`** ⇒ ★**而 `J_USB_C` 是 `state/check_pcb_nets.py` 的 NC 白名单成员** ⇒ ⇒ ★**即便五侧同口径, NC 白名单那几行照样被撞死 (★ISS-314 实测: 非法 NC 3 + C3 红 1★) ⇒ ★**本单必须给出这三选项的沙盒实跑读数 (★不许手抄上一趟的结论★)** ★

---

## ★2 · ★续做清单 (★按这个顺序做, 先交卷再完美★) ★

★**★① 先把交卷页骨架落盘 (★上一趟死在这个坑上: 一页纸都没落 ⇒ 成果全在盘上但没人认领★)★**
- 新建 `HANDOFF/2026-11-18_hw-lead_ISS317_S1位号改名可执行清单.md` (★文件名自己定也行·但要在交卷页里写清★)
- ★**先落 B0/B1 骨架 + 已确认的 §A/§B 数字 + 下面的 §2 ②③④ 结论占位** ⇒ ★**哪怕只完成一半, 也要有一页能读的纸★**

★**② T5 / T6 实跑 (★U-1 未验项★)**
- ★**先把 `logs/iss317/iss317_sb_make_t5t6.py` 补完** (★上一趟停在 "fix T5 to use the correct construction"★ ⇒ ★**它是「造法不对」还是「跑法不对」, 你自己读源码判断★)
- ★**判据脚本 = ISS-314 留档的沙盒副本 `logs/iss314/check_pcb_nets_reflookup.py` (★只读取·拷进沙盒跑·不许改那份副本★)★**
- ★**期望**: T5 ⇒ ③ 红 (★文案「口径歧义」或「单射校验失败」★) · T6 ⇒ ③ 红 (★文案「口径未同步: 1 个板上位号在网表里找不到」★)
- ★**沙盒只许写 `tmp/iss317_sandbox/`** ⇒ 交卷前删干净 (★ISS-314 是这么做的★)

★**③ 三侧同口径 (★现应叫【五侧同口径】· 见 §1★) 的逐条改名对照表**
- ★**每一个 ref 一行** (★照 `HW/PCB/ONETRIP_REISSUE_MANIFEST.md` §3-1 同款口径★) ⇒ 表侧现值 / 表侧改名后 / 板侧现值 / 板侧改名后 / 网表 / 脚表 / BOM / 原理图 八列
- ★**机器生成 (★照 `iss317_gen_rename_list.py` 的路子·不许手抄 186 行★)** ★

★**④ NC 白名单撞死的三选项 + 各自 C1/C2/C3 预期读数**
- 甲 = 豁免那几条 / 乙 = 解封 `state/check_pcb_nets.py` 两行 / 丙 = 白名单按形状推导
- ★**每一项的 C1/C2/C3 读数必须是沙盒实跑出来的, 不许推算** ★
- ★**本单只给选项 + 代价, 不替老板拍板** ★

★**⑤ BOM 证据回填兜底的机器可判判据写法 (★ISS-311 地雷 2★)**
- ★**问题**: BOM 证据会【静默消失且无报警】⇒ 判据要能【在证据消失那一刻判红】★
- ★**写法**: 判据位置 + 触发条件 + 期望读数 + 反向用例 (★破坏前绿·破坏后红·不是巧合自证★) ★

★**⑥ 补齐 ISS-314 的 5 条未验 (★它自己说「下一轮补」的那几条★)**
| 未验项 | cont1 的要求 |
|---|---|
| T5 / T6 实跑 | ★见 §2 ②★ |
| DMP3098L 官网规格 | ★**自己上官网查** (★不许写「等原厂回信」·不许外发询价★) ⇒ 标证据等级 `[官网]` ⇒ ★查不到就写降级方案 (★选官网参数直接满足的替代型号 / 改设计路径绕开★)★ |
| ESD 器件官网规格 | ★同上★ |
| BOM 问号行数现值 | ★**实跑 `bash state/kicad.sh sch export bom` 现值** (★ISS-314 跑出来是 问号行数 0 / 总行 219★ ⇒ 你要独立复核一遍·抄不算数★) ★ |
| 落表排期口径 | ★给出「哪几批、每批什么时候、谁批」的三列表 (★不替老板拍日期·只给批次顺序与前置★) ★ |

★**⑦ 交卷前必跑 (★输出原样贴进回复★)**
```
python3 state/merge.py && python3 state/gate_check.py     # rc 必须 0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb                     # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb               # 必须 = 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER" <你的交卷页>                 # 必须 = 0
```
★**并用 `state/frag_write.py --agent hw-lead` 原子写 `state/fragments/hw.yaml`** (★禁止 `open(p,"w")`★) ★
★**自证**: 板 md5 + mtime 交卷前后逐字节相同 ⇒ **零写板** ★

★**⑧ 时间预算纪律 (★这一趟的教训★)**
★**上一趟 10 分钟被父 run 连带 abort ⇒ ⇒ 本单请【先落纸再干活】**: 每完成 §2 的一条, 就把结论回填进交卷页 (★哪怕是「未验, 原因 X」也要写上★) ⇒ ★**宁可交半成品页, 不许一页纸都不落** ★

---

## ★3 · ★边界 (★硬★) ★
- ★**零写板** (板 `HW/PCB/demo_mainboard.kicad_pcb` 一个字节不许动) ★
- ★**零落表** (不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 任何 `.kicad_sch`) ★
- ★**零重生成** (★`state/gen_netlist.py` / `gen_kicad_sch.py` / `gen_pcb_netlist_board.py` / `gen_bom.py` 一个都不许跑★) ★
- ★**零改闸** (★`state/check_pcb_nets.py` / `state/gate_check.py` / 任何 `check_*.py` 一律不许改★) ★
- ★**零改既有文档正文** (★沙盒只写 `tmp/iss317_sandbox/`★) ★
- ★**零外发** (★不许发邮件/询价/问询/采购; 型号规格一律自己上官网查并标证据等级★) ★
- ★**不替老板拍板** · ★**不自签 issue_log** (★status/verify_result 留给 main★) ★
- ★**不许改 `state/issue_log.yaml`** ★

---

## ★4 · ★交卷格式 (★照上一趟 ISS-314 的交卷页格式·B0~B6齐全★) ★
- 交卷页 `HANDOFF/2026-11-18_hw-lead_ISS317_*.md` (★B0 一句话+清单 / B1 结论摘要 / B2 验收标准自评(逐条 通过|不通过|未验) / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点(需要谁回答什么) / B6 自证复现命令★)
- `logs/iss317/` 原始输出 (★每个读数都要有对应原始输出文件·不许只贴结论★)
- `state/fragments/hw.yaml` (★只改自己那一份★)
