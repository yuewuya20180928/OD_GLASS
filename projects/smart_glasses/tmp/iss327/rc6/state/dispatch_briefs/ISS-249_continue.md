★★**目标 (★内部活·原理图/网表侧·★【续做】·★不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★★**上一轮 (19:19~19:29) 被 runTimeout 掐死 ⇒ 本轮只补缺口, 不许重做已落的部分** ★★

★★**① 上一轮怎么死的 (★main 19:4x 实测, 不是猜★)** ★★
· 会话 `agent:hw-lead:subagent:8f4758a2-…` 19:19:21 起 · **19:29:40 被 timeout 掐断** (runtime 617s) ⇒ transcript 末条 = 「Now writing the landing ledger §17:」
· ⇒ ★**核心落表已完成, 交卷层没来得及做** ★

★★**② 盘上实况 (★main 19:3x~19:4x 自己实跑, 不抄你的会话★)** ★★
| 项 | 实测 | 你要不要重做 |
|---|---|---|
| `state/gen_netlist.py` L381 / L391 两行 node2 | ★**已落** (grep 实读: L381 = `VBUS_5V_F1` · L391 = `VBUS_5V_CHG`) ★ | ★**不许重做** ★ |
| `python3 HW/check_iss247_f1_landed.py` | ★**rc=0 · 「✅ F1 已落表」** ★ | 不许重做 |
| `HW/netlist_v1.csv` md5 | **`16ac89f7…`** (★已变 = F1 已落的证据★) | 不许重做 |
| 板 `611b869e…` / `.kicad_pro` `3e504d2b…` | ★**逐字节未变** ★ | ★**不许碰** ★ |
| `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17 | ★**已写** (L704 起 · 含落表条目 / 复现命令 / 受保护 md5 / 反向自证配方) ★ | ★**只许补缺, 不许重写** ★ |
| `HANDOFF/2026-11-16_hw-lead_ISS249_*.md` | ★**缺** ★ | ★**本轮必须写** ★ |
| `state/fragments/hw.yaml` 里 ISS-249 的 claim/artifact | ★**缺** (hw.yaml mtime 18:46 = 开单前) ★ | ★**本轮必须写** ★ |
| 反向自证 (改回 F1 ⇒ 必须红 ⇒ 装回 ⇒ 又绿) | ★**配方已写进 §17, 但没有已跑的输出** ★ | ★**本轮必须跑并贴输出** ★ |

★★**③ 本轮只做这 4 件 (★少一件即无效★)** ★★
① ★**交卷单** `HANDOFF/2026-11-16_hw-lead_ISS249_F1真落表.md` (★B1~B6 六块齐全★; ★`gate_check` 按【标题行】认块 ⇒ 标题里要带它要的语义关键词, 否则不计分★) ⇒ 内容: 结论摘要 / 验收标准自评 / 证据分级 / 接口取值声明 / 未决项与卡点 / 自证复现命令
② ★**反向自证实跑并贴输出**: ★**沙盒里把 L381/L391 改回旧值 ⇒ `check_iss247_f1_landed.py` 必须 rc=1 ⇒ 装回 ⇒ 必须 rc=0** ★ ⇒ ★**素材都在盘: `state/.bak_iss249/gen_netlist.py` + `/tmp/gen_netlist_iss249_FIXED.py` ⇒ 用沙盒, 真盘一个字节不许动** ★
③ ★**分片** `state/fragments/hw.yaml` (★**必须**走 `python3 state/frag_write.py --agent hw-lead …` 原子写, ★不许 `open(p,"w")`★) ⇒ +artifact ×N / +claim ×N / +need (给 main 的 H-1 重锚提示)
④ ★**H-1 重锚提示交回 main (★关键★)**: ★**网表 md5 已从 `611c3ba3…` 变成 `16ac89f7…` ⇒ `MECH/check_demo_struct_truth.py` 的 G5b/C21 与 SW 侧 R6 的 md5 锚点【按设计变红】** ⇒ ★**你只报告, 不许去修别人的域 (MECH/SW 的重锚是别的单)** ★

★★**④ 验收命令 (★逐条要 rc, 原样贴进交卷单 B5★)** ★★
```
python3 HW/check_iss247_f1_landed.py                # rc=0 (★S1~S6 全绿★)
python3 HW/check_iss247_f1_landed.py --selftest     # rc=0 (★11/11★)
python3 HW/check_netlist_selfconsistency.py          # rc=0
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★仍 18 条·不许上升★)
python3 HW/check_netlist_contradiction_r3.py        # rc=1 (★恰 2 条 = F2+F3 · F1 已消失★)
python3 state/check_netlist.py && python3 state/check_netlist_pins.py   # rc=0
python3 state/check_sch_erc.py && python3 state/check_sch_pinfull.py   # rc=0 (★584=584 · K=0★)
python3 state/merge.py && python3 state/gate_check.py   # rc=0 (★Q1 18/18★)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# 期望: 16ac89f7… / ef436a37… / 2a730574… / 611b869e… / 3e504d2b…  (★后三个逐字节不变★)
```

★★**⑤ 边界 (★越界即无效★)** ★★
· ★**不许碰板 / PCB 布线 / 布局 / 板框** ★ · ★**不许落 V-2 / V-3 / V-4 (★那是老板的拍板, 机器门禁 `state/land_v_values.py` 必须带 `--boss-decision` 才准落★)** ★
· ★**不许改 `MECH/` 与 `SW/` 任何文件** (★G5b/C21 红是并发落表导致, 不是你的失败, 不许你去修★) ★
· ★**不许改 `PROJECT_TRACKER.md` §0** · ★**不许自签 `state/issue_log.yaml`** (★verify 留给 main★) ★
· ★**零外发** (★不发信 / 不询价 / 不问询 / 不采购★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`, 查不到就写降级方案
· ★**不替老板拍板** ⇒ 只列选项 + 量化代价

★★**⑥ 硬规矩 (★上一轮就是死在这★)** ★★
· ★**先落盘骨架再填内容** (★先建交卷单文件 + 先建骨架章节, 再一条条填★) ⇒ ★**宁可交一份半空的交卷单, 也不要在内存里攒到最后一秒★**
· ★**每做完一个可验证的小块, 立刻写盘** (★10 分钟窗口一到就被掐, 内存里的东西全丢★)
· ★**本轮 runTimeout 5400s (90 分钟) ⇒ 慢慢做, 但别攒** ★
