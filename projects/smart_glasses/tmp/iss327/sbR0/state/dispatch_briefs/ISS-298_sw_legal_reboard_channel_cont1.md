# ★★⑭ · ISS-298 cont1 续做说明 (★2026-11-17 19:0x 由 main (moli) 追加★)

> ★**为什么有这一段**: 上一趟子会话 `agent:sw-lead:subagent:eefd6258` (sessionId 68654eaf) 18:30:17 → 18:47:28 · runtime 1026s · **status=timeout / abortedLastRun=true** ⇒ ★**transcript 最后两行 = assistant「Now let me gather key facts before implementing: the ledger's change rows for the board, and the state gate scripts' behavior.」→ toolResult「Aborted」** ⇒ ★**死在「读完事实、还没动手改闸」那一刻** ★
> ★**⇒ 本单是 SW 侧【只有 1 道闸】的单, 上一趟【只写了个交卷单骨架 + 读了台账】⇒ 本趟是从闸本体开始做★**

## ★★⑭-1 · 盘面实况 (★main 2026-11-17 18:4x~19:1x 本机实跑 + 实读, 不抄任何 agent 报告★)

| # | 项 | main 实测 (19:1x) |
|---|---|---|
| ★**1** ★ | ★**交卷单骨架已建** ★ | ★**`HANDOFF/2026-11-17_sw-lead_ISS298_合法改板通道.md` = 2306 B** ★ ⇒ ★**B0 一句话结论 + 交付物清单已写, 但 B1~B8 八节全是「★待填★」** ★ ⇒ ★**本趟要填满★** ★ |
| ★**2** ★ | ★**闸本体【一个字都没改】** ★ | ★**`SW/tools/check_onepass_sw_sync.py` mtime = 17:51 (★上一趟没动它★)** ★ ⇒ ★**它仍硬钉板 md5** ★ ⇒ L84-85 `ANCHOR_MD5 = {"HW/PCB/demo_mainboard.kicad_pcb": "611b869e…", "HW/PCB/demo_mainboard.kicad_pro": "3e504d2b…"}` + L105-107 `protected_map()` 里「板」/「.kicad_pro」两行仍写死基线 ★ ⇒ ★**这就是本单要改的那一处** ★ |
| ★**3** ★ | ★**分片一条都没写** ★ | ★**`grep -c iss298 state/fragments/sw.yaml` = 0** ★ ⇒ ★**走 `state/frag_write.py --agent sw-lead` 原子写★** ★ |
| ★**4** ★ | ★**参考实现已经跑通 (★照抄它的形状, 不许自创★)** ★ | ★**权威闸 `SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` (★L522 起★)** ★ + ★**锚点块 `SW/SW_MD5_BASELINE_LEDGER.md` §1 的 `hard_protected:` 段 (★L54~L65★) 已经写好 2 件的 `md5:` + `reboard: null`★** ★ ⇒ ★**★SW 侧那道闸要把判决源从「字面基线」换成【台账链头 + 合法改板四项原子映射】, 口径照 ISS-284 已跑通的那个★** ★ |

★**★关键: SW 侧的参考实现比 HW 侧更成熟 (★`SW/tools/check_demo_panel_spec.py` 的 R6 已含 `check_r6_hard_protected()` 四条判据 + `LEDGER_REQUIRED_ITEMS = ("by","file","md5","prev_md5")` + `reboard: null` 的语义★) ⇒ ★**照它改 `SW/tools/check_onepass_sw_sync.py`, 不要从零写一套★** ★

★**受保护 5 件基线 (★main 19:1x 实测★)**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★★**必须逐字节不变**★★

## ★★⑭-2 · 本趟只做 3 件 (★顺序不许换★)

1. ★**把 `SW/tools/check_onepass_sw_sync.py` 的「板 / `.kicad_pro` 两件」接到合法改板通道上** ⇒ ★**照 `SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` 四条判据逐字照搬口径★**:
   | # | 判据 | 必须保持的方向 |
   |---|---|---|
   | ① | ★**保护基线自证** ★: 锚点里的基线 md5 必须能在落表台账里与该文件【同行】查到 | ★**只改锚点里的 md5 而台账没记 ⇒ 红** (★「挖坑」必须堵死★) ★ |
   | ② | ★**台账里该文件没有变更行** ★ ⇒ 不许有 reboard 记录; 且盘上 md5 必须 == 基线 | ★**纯 md5 硬保护, 一条不许松** ★ |
   | ③ | ★**台账里有变更行** ★ ⇒ 链头必须唯一 / 链不断 / 链头有单号 (★fail-closed 三条★) ⇒ 锚点必须带 `reboard` 四项原子记录 (★缺一 ⇒ 红★) ⇒ 四项必须与台账链头逐字对上 ⇒ 保护基线必须留在链尾 ⇒ 盘上 md5 必须 == 台账链头 | ★**判据方向不许变: 盘上 ≠ 链头 ⇒ 红 (合法改板只让链头前移)★** ★ |
   | ④ | ★**同组受保护件覆盖** ★: 一次合法改板必须覆盖同组全部件 | ★**只来一条记录 ⇒ 红** ★ |
   ⇒ ★**★`reboard: null` (★还没发生过合法改板★) ⇒ 仍按纯 md5 硬保护判 ⇒ ★**不许为了「将来会改」就把基线放松**★** ★
2. ★**补 ≥4 条反向用例 (★沙盒跑, 真盘零写★)** ⇒ ★**照 `SW/tools/check_demo_panel_spec.py --selftest` 里 REV-16~REV-21 那六条的形状★** ⇒ ★**每条贴原样 rc★** ⇒ ★**★不许把闸里的判据删一条来凑绿★** ★
3. ★**填满交卷单 B1~B8 + 分片** ⇒ `grep -c iss298 state/fragments/sw.yaml` ≥ 4

## ★★⑭-3 · 验收 (★原样 rc 贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_onepass_sw_sync.py;                 echo "rc=$?"   # 期望 0
python3 SW/tools/check_onepass_sw_sync.py --selftest;      echo "rc=$?"   # 期望 0 (★原有 10 条一条不许删 + 新增 ≥4 条★)
python3 SW/tools/check_demo_panel_spec.py;                  echo "rc=$?"   # 期望 0
python3 SW/tools/check_demo_panel_spec.py --selftest;       echo "rc=$?"   # 期望 0 (22/22)
python3 SW/tools/timing_check.py;                          echo "rc=$?"   # 期望 0
python3 state/merge.py;                                    echo "rc=$?"   # 期望 0
python3 state/gate_check.py;                               echo "rc=$?"   # 期望 0 (Q1 18/18)
grep -c iss298 state/fragments/sw.yaml
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

## ★★⑭-4 · 边界 (★违反就是不合格★)

★**零写板** · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 台账本体 (★只读★)** ★ · ★**不许改 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块里那两个 `md5:` 基线** (★那是「挖坑」, 正是 ISS-284/273 堵死的洞★) ★ · ★**不许动 `HW/` 与 `MECH/` 的任何文件和分片** (★HW 侧那道闸归 ISS-297·MECH 侧归 ISS-296★) ★ · ★**不许放宽 fail-closed 三条** · ★**不许改 `SW/tools/check_demo_panel_spec.py` 一个字节** (★那是权威闸, 只许读★) ★ · ★零外发 · ★**不替老板拍板** · ★**不自签 issue_log** · ★**只写自己的分片** · ★**实物 `[实测]` = 0 条**

## ★纪律 (★上一趟就是这么栽的★)

★**长任务一律 `nohup ... > logs/iss298/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**单条 exec ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**交卷单第一件事就是 `write` 补骨架 (★已有骨架, 直接填 B1~B8★)** ★ · ★**分片写完 `grep` 校验** ★ · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)
