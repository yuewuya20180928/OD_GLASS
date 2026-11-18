# ISS-311 · hw-lead 任务书 —— ★★【「板那一趟」重出清单 + 产出链同步缺口定位 (C1 差 2 个焊盘 + 投产包原理图源文件 11 个不一致) ⇒ 交一份【板只改一次】不许漏件的作业包】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-311
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 纯分析 / 作业包类** ★
> ★**边界 (硬)**: ★**零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★1 · 病灶 (★main 2026-11-18 05:5x 本机实跑 `python3 state/chain_gate.py` 原始输出, 不抄任何 agent 报告★) ★

```
环节                          准入    准出
③ PCB (.kicad_pcb)          ❌     ✅
    准入: ★★板与网表不等价 (C1/C2 红 ⇒ 板是旧网表的板)★★ · ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482 · 11-06 07:07
⑤ 投产资料包 (HW/PCB/production/) ❌  ✅
    准入: 30/30 必备产物齐全 · ★★投产包比 原理图 旧 ⇒ 投板用的是旧板的 Gerber★★
          · ★★原理图源文件: 原理图源文件与 HW/PCB/ 没有一一对应: 内容与源不一致 11 个★★
            (例 ['demo_mainboard.kicad_sch', 'demo_mainboard_p1.kicad_sch', 'demo_mainboard_p10.kicad_sch'])
          ⇒ 修法: 把 doc/sch_src/ 同步成 HW/PCB/ 下全部 .kicad_sch + demo_mainboard.kicad_pro
❌ 生产链有 2 个环节没过 ⇒ ★下游产物不许用★
```

★**★这两条红正是「板只改一次」那一趟的【产物清单】出了问题 (★老板 11-17 00:43: 板只改一次 ⇒ 那一趟必须一次做完: 位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出★)** ★
★**⇒ 本单就是把那一句「Gerber/投产包重出」变成一张【逐件的作业包表】: 每件产物 = 生成器入口 · 上游依赖 · 现值 · 验收判据 · 顺序 · 归属** ★

---

## ★2 · 本单要交的四件事 ★

### ★2-1 · 【C1 焊盘差异定位】(★把「板是旧网表的板」这句结论变成逐条证据★) ★
★**现状**: 网表 **480** 个 (ref, 焊盘号)→网络 vs 板上带网焊盘 **482** ⇒ **差 2 个** ★
★**本单要交**:
- ★**板上有、网表里没有** 的 (ref, pad) 逐条列出 (★带板上网络名 + 板文件行号/坐标★)
- ★**网表有、板上没有** 的 (ref, pad) 逐条列出 (★带网表行号 + 网络名★)
- ★**判定**: 这 2 个差是【板侧多出来的旧件】还是【网表新加的脚】⇒ ★**结论必须指向板那一趟要做的具体动作 (改板 / 改网表 / 两者同规格)**, 不许只交差集了事 ★
- ★**自证**: 交页里附上自己跑的取数命令 + 原始输出 (★不许抄 chain_gate 的结论★)

### ★2-2 · 【原理图源文件 11 个不一致定位】★
★**现状**: `HW/PCB/production/doc/sch_src/` 下有 11 个 `.kicad_sch` + 1 个 `.kicad_pro`, ★**与 `HW/PCB/` 下同名文件内容不一致** ★
★**本单要交 (★逐个文件, 11 个一个不许少★)**:
| 列 | 内容 |
|---|---|
| ★**文件名** ★ | ★例 `demo_mainboard_p1.kicad_sch`★ |
| ★**差异类型** ★ | ★**内容旧** / ★**uuid 抖动 (⇒ 归一化后一致·不是真缺件)** / ★**缺页** / ★**改名** ★ |
| ★**差异证据** ★ | ★md5 + 归一化指纹 (★照 chain_gate ② 原理图准入那一栏的口径: 归一化后 11 个一致 ⇒ uuid 抖动不影响判据★) + 差异行数 ★ |
| ★**修法** ★ | ★**重生成 / 直接同步 / 判据无关★ ★ |

★**★关键一问 (★本单要回答★)**: ★**这 11 个差异里, 有几个是【投产包里的原理图比 `HW/PCB/` 旧】(★⇒ 投板时用投产包 = 用旧原理图★)· 有几个只是 uuid 抖动 (⇒ 不是真缺件·不必重出) ⇒ 两个数都要给** ★

### ★2-3 · 【「板那一趟」重出清单 (★本单的核心交付物·一张表★★) ★
★**每一件产物一行**, ★列: ★**产物名 · 生成器入口命令 (逐字可跑) · 上游依赖 · 现值 (md5 + 时间戳) · 板那一趟做完后的验收判据 (能跑的那条命令 + 期望值) · 顺序位 · 归属人** ★
★**至少覆盖这些件 (★照 chain_gate 的五个环节 + 板那一趟点名的 Gerber/投产包★)**:
网表 · 11 个原理图页 + `.kicad_pro` · 板 · Gerber · 钻孔 · 坐标 · 贴片 · 装配图 · 3D 模型 · BOM · 投产包 (`HW/PCB/production/` 全部子目录: `gerbers/` `drill/` `pos/` `assembly/` `3d/` `doc/`) · 投产包清单文件 (★`MANIFEST.md5`★)
★**生成器入口 (★chain_gate 自己给的修法, 本单照抄核一遍再用★)**:
`python3 state/gen_netlist.py` · `python3 state/gen_kicad_sch.py` · `python3 state/gen_bom.py` · `bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py` · `bash state/gen_production_pack.sh` · `cp -p HW/PCB/demo_mainboard*.kicad_sch HW/PCB/demo_mainboard.kicad_pro HW/PCB/production/doc/sch_src/`
★**每条命令都要自己实测存在 (★不许写不存在的命令★) ⇒ 不存在的写「缺, 需新建」并给出建议入口** ★

### ★2-4 · 【顺序 + 一致性判据 + 归属】
- ★**硬顺序** (★照 chain_gate 口径★): ★**网表 → 原理图 → 板 → Gerber → 投产包** ★ ⇒ 交一张依赖图 (★谁是谁的上游★)
- ★**「同趟出」清单**: ★**哪些产物在板那一趟里必须一起重出 (★不许留旧件混进去·★因为旧件正是今天 ⑤ 红的原因★)** ★
- ★**归属**: 每件归给谁 (hw / sw / mech / main) ★
- ★**★只交清单, 不执行任何重出命令 (★本单零重生成·零写板·零落表★)** ★

---

## ★3 · 交卷物 (4 件) ★

1. ★**新建 `HW/PCB/ONETRIP_REISSUE_MANIFEST.md`** (★重出清单正文: §1 C1 差 2 条逐条证据 · §2 原理图 11 个差异逐条表 · §3 重出清单主表 · §4 顺序与依赖 + 同趟出清单 + 归属 · §5 证据分级 + 自证命令★)
2. ★**新建 `HANDOFF/2026-11-18_hw-lead_ISS311_板那一趟重出清单.md`** (★B1~B6 齐全 · 占位符 0 · 与上面那份同源不重写★)
3. ★**`logs/iss311/`** (★逐条取数命令 + 原始输出 + 被测文件 md5 前后值★)
4. ★**`state/fragments/hw.yaml`** (★★**必须用 `python3 state/frag_write.py --agent hw-lead` 原子写 (★禁止 open(p,"w")★)★** · artifacts + needs_from · 只写自己那一份★)

---

## ★4 · 硬边界 (★违反即不算交卷★) ★

- ★**零写板**: 板 `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 (`611b869e13518c3c023fb178f91a0075`) + mtime (`2026-11-06 07:07:17`) 交卷前后逐字节相同 ⇒ **交卷页要贴这两个值** ★
- ★**零落表 / 零改网表真源** (★网表 / 脚表 / BOM / 落表台账 一律不动★) ★
- ★**★零重生成 (★本单只交清单, 不跑任何生成器 / 打包脚本 / cp 同步★)** ⇒ ★**不许动 `HW/PCB/production/` 下任何文件** ★
- ★**零改闸**: `state/chain_gate.py` / `state/gate_check.py` / `state/merge.py` 一个字不许改 ★
- ★**零改既有文档正文**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 只读不写 ⇒ ★**本单交的是【另一份清单】, 不是【改好的那两个文件】** ★
- ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 外部依赖一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★** ★
- ★**不替老板拍板 · 不自签 issue_log** (★`state/issue_log.yaml` 只由 main 改★) ★
- ★**只写**: `HW/PCB/ONETRIP_REISSUE_MANIFEST.md` (★本单新建★) · `HANDOFF/` 本单交卷单 · `logs/iss311/` · `state/fragments/hw.yaml` (★经 frag_write.py★) ★

---

## ★5 · 交卷前必跑 (★把输出原样贴进回复★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/chain_gate.py            # ★现状基线 (★两条红如实在·不许自己去改绿★)
python3 state/merge.py && python3 state/gate_check.py    # rc 必须 0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/production/MANIFEST.*
```

★**★额外纪律 (★与所有派活单同款★)★**: ① ★**写分片必须用 `state/frag_write.py` (禁止 open(p,"w"))** ★ ② ★**只写本任务允许的文件, 不碰别人的** ★ ③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ ④ ★**不许外发任何邮件/询价/问询/采购** ★ ⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
