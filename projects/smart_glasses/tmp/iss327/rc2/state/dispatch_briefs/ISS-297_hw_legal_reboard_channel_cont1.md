# ★★⑭ · ISS-297 cont1 续做说明 (★2026-11-17 19:0x 由 main (moli) 追加★)

> ★**为什么有这一段**: 上一趟子会话 `agent:hw-lead:subagent:51b84574` (sessionId 64aaa9ad) 18:30:18 → 18:47:28 · runtime 1026s · **status=timeout / abortedLastRun=true** ⇒ ★**transcript 最后两行 = assistant「Confirmed: those 2 legacy cases were already failing before my change (stale fixture vs ISS-283's newer md5). Let me fix the stale fixtures to be dynamic:」→ toolResult「Aborted」** ⇒ ★**死在「修 selftest 里 2 条过期 fixture」那一刻** ★
> ★**⇒ 上一趟的活【大半在盘上】, 本趟是【续做 + 补 5 道闸】, 不是从零重做★**

## ★★⑭-1 · 盘面实况 (★main 2026-11-17 18:4x~19:1x 本机实跑 + 实读, 不抄任何 agent 报告★)

### ★已经做好的 3 件 (★★不许重做★★) ★

| 产物 | main 实测 | 说明 |
|---|---|---|
| ★**新建** `HW/board_reboard.py` | ★**35661 B** ★ | ★**HW 域 6 道闸共用的判决库** ★ ⇒ 里面有 `check_pair()` (★板 + `.kicad_pro` 两件的判决★) · `check_file()` · `load_anchor()` / `chain_state()` / `row_has_four()` (★fail-closed 三条: 链头不唯一 / 链断 / 链头无单号★) · `row_has_four()` (★四项原子映射逐字对账★) · `CASES` (★10 条反向用例★) · `run_cases()` (★沙盒逐条跑 + 跑完立刻删沙盒★) · `build_sandbox()` (★只拷 4 件进沙盒, 真盘零写★) · `make_legal()` (★在沙盒里做一次「合法改板」: 板改一字节 + 锚点写原子 reboard 记录 + 台账追加行★) ★ |
| ★**新建** `HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md` | ★**9216 B** ★ | ★**HW 侧板 md5 台账 (锚点住这儿)** ★ ⇒ §0 纪律 · §1 基线区 · §2 变更区 · §3 留证绑定区 · §4 边界 · ★**§5 「合法改板」通道锚点块 (★`# BEGIN HW_BOARD_REBOARD_ANCHORS` / `# END HW_BOARD_REBOARD_ANCHORS`★) 已写好, 含 2 件 (板 / `.kicad_pro`) 的 `md5:` + `reboard: null`★** ★ |
| ★**改完 1 道闸** `HW/check_fsin_rootcause.py` | ★**rc=0** ★ | ★**D5 已改两层口径** (★D5a = 板 + `.kicad_pro` 两件走台账链头 + 合法改板通道★ · D5b = 网表/脚表/BOM 三件走基线 ∪ 最新落表记录★) ⇒ ★**已 import `board_reboard` (★L60★) + 调 `board_reboard.check_pair()` (★L686★) + 跑 `board_reboard.run_cases()` (★L964★)★** ⇒ ★**`--selftest` 已含 ⑯a~⑯c/⑯d/④/⑤a~⑤c 共 10 条 ISS-297 反向用例** ★ |

### ★还没做的 (★本趟的活★) ★

| # | 活 | main 实测现状 (19:1x) |
|---|---|---|
| ★**1** ★ | ★**5 道闸还没接通道** ★ | ★**它们仍硬钉板 md5 `611b869e…`** ★ ⇒ `HW/check_g1a7_selection_landed.py` L89 `BOARD_MD5` + L90 `PRO_MD5` · `HW/check_onepass_commit_order.py` L101「板」 + L102「.kicad_pro」 · `HW/check_onepass_preflight_coverage.py` L60「板」 · `HW/check_pin_function_labels.py` L145「板」 + L146「.kicad_pro」 · `HW/check_workpack_state_values.py` L62「板」 ★⇒ ★**全部改成读台账链头 + 走 `board_reboard.check_pair()` 口径 (★照 `HW/check_fsin_rootcause.py` 已跑通的那个形状★)★** ★ |
| ★**2** ★ | ★**上一趟说的「修 2 条过期 fixture」没做完** ★ | ★**`HW/check_fsin_rootcause.py --selftest` 现在是 23/25 ⇒ 2 条红** ★ ⇒ ★**失败的就是 ⑭ + ⑮ 两条 (★它们在改之前就红, 与本单无关★)**: ⑭「落表台账最新一条的后值被改 ⇒ D5 红」· ⑮「台账末尾追加更新的落表记录 ⇒ D5 仍绿」 ⇒ ★**根因 = fixture 里写死的旧 md5 (`e06c1dd6…`) 已过期 (★ISS-283 合法落表后网表 md5 已是 `37f62ac3…`★) ⇒ ★**要么把 fixture 改成动态 (★从台账读当前链头★), 要么把这两条判据改成台账口径 ⇒ ★**不许删这两条用例**★** ★ |
| ★**3** ★ | ★**交卷单一个字都没写** ★ | ★**`HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md` 不存在** ★ ⇒ ★**新建 (★B0~B6 齐全★)★** ★ |
| ★**4** ★ | ★**分片一条都没写** ★ | ★**`grep -c iss297 state/fragments/hw.yaml` = 0** ★ ⇒ ★**走 `state/frag_write.py --agent hw-lead` 原子写★** ★ |

★**受保护 5 件基线 (★main 19:1x 实测★)**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★★**必须逐字节不变**★★

★**★注意 `HW/check_pin_function_labels.py` 现在 rc=1 是【既有缺陷基线】(★它自己打印「当前是已知缺陷基线, 落表批次里修」★) ⇒ ★**你只许碰它的板 md5 那两行 (★L145/L146★), 不许顺手修它那 18 条别的缺陷**★ ★**

## ★★⑭-2 · 本趟只做 4 件 (★顺序不许换★)

1. ★**修那 2 条过期 fixture** ⇒ `python3 HW/check_fsin_rootcause.py --selftest` ⇒ **25/25 rc=0** ⇒ ★**★不许删用例来凑绿★** ★
2. ★**把 5 道闸接到通道上** ⇒ ★**每道闸都改成「判决源 = 台账链头 + 合法改板四项原子映射」⇒ ★**判据方向不许变** (★盘上 ≠ 链头且无合法记录 ⇒ 仍红★) · ★**fail-closed 三条一条不许动** (★链头不唯一 / 链断 / 链头无单号 ⇒ 仍红★) · ★**`reboard: null` (★还没发生过合法改板★) ⇒ 仍按纯 md5 硬保护判** ⇒ ★**不许把基线放松来「让它绿」★** ★
3. ★**每道闸补 ≥4 条反向用例 (★沙盒跑, 真盘零写★)** ⇒ ★**照 `HW/board_reboard.py` 里 `CASES` 那 10 条的形状 (★① 合法改板 ⇒ 绿 ② 只改基线没台账记录 ⇒ 红 ③ 四项缺一 ⇒ 红 ④ 盘上 ≠ 记录里的新 md5 ⇒ 红 ⑤ 链头不唯一/链断 ⇒ 红★)★** ⇒ ★**每条贴原样 rc★** ★
4. ★**交卷单 (★新建★) + 分片** ⇒ `grep -c iss297 state/fragments/hw.yaml` ≥ 4

## ★★⑭-3 · 验收 (★原样 rc 贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_fsin_rootcause.py;                    echo "rc=$?"   # 期望 0
python3 HW/check_fsin_rootcause.py --selftest;         echo "rc=$?"   # 期望 0 (25/25)
python3 HW/check_g1a7_selection_landed.py;             echo "rc=$?"   # 期望 0
python3 HW/check_onepass_commit_order.py;              echo "rc=$?"   # 期望 0
python3 HW/check_onepass_preflight_coverage.py;        echo "rc=$?"   # 期望 0
python3 HW/check_pin_function_labels.py;               echo "rc=$?"   # ★期望仍是 1 (既有缺陷基线·你只许碰 L145/L146)★
python3 HW/check_workpack_state_values.py;             echo "rc=$?"   # 期望 0
python3 state/merge.py;                                echo "rc=$?"   # 期望 0
python3 state/gate_check.py;                           echo "rc=$?"   # 期望 0 (Q1 18/18)
grep -c iss297 state/fragments/hw.yaml
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

## ★★⑭-4 · 边界 (★违反就是不合格★)

★**零写板** · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 台账本体 (★只读★)** ★ · ★**不许动 `SW/` 与 `MECH/` 的任何文件和分片** (★SW 侧那道闸归 ISS-298·MECH 侧归 ISS-296★) ★ · ★**不许放宽 fail-closed 三条** · ★**不许为了让闸变绿去改台账里那两个 `md5:` 基线** (★那是「挖坑」, 正是 ISS-284/273 堵死的洞★) ★ · ★**不许把 `HW/check_pin_function_labels.py` 那 18 条既有缺陷顺手修掉** ★ · ★零外发 · ★**不替老板拍板** · ★**不自签 issue_log** · ★**只写自己的分片** · ★**实物 `[实测]` = 0 条**

## ★纪律 (★上一趟就是这么栽的★)

★**长任务一律 `nohup ... > logs/iss297/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**单条 exec ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**交卷单第一件事就是 `write` 建骨架** ★ · ★**分片写完 `grep` 校验** ★ · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)
