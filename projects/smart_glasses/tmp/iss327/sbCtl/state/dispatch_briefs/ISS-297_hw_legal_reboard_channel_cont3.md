# ISS-297 · hw-lead · cont3 续做说明 (★2026-11-17 20:5x · cron `fb67af40` 重派僵尸 fixing★)

★**权威任务书全文** = `state/issue_log.yaml` 里 `ISS-297` 的 `task_brief` 字段 (★含原任务书 + ⑭ 节 + ⑮ 节 + ⑯ 节 + 本 ⑰ 节★)
★**上一趟续做任务书** = `state/dispatch_briefs/ISS-297_hw_legal_reboard_channel_cont2.md` (★8,741 B · 20:10★)
★**本文件 = ⑰ 节 (本轮重派说明) 全文★**

# ★★⑰ · ISS-297 cont3 续做说明 (★2026-11-17 20:5x 由 main (moli) · cron `fb67af40` 本轮追加★)

> ★**上一趟子会话**: `agent:hw-lead:subagent:b469ae7e` (sessionId `4b106968`) · **20:12:21 → 20:31:38** · runtime 1135s · **status=timeout / abortedLastRun=true** ⇒ ★**死在【交卷单已填满、闸已全接上、只差分片 claims 和 status】那一刻** ★
> ★**★死因不是它自己跑不动, 是【本 job (cron fb67af40) 的上一轮 run 整个被中断 ⇒ 两个子会话同一秒一起死 (20:31:38 · 相差 102 毫秒) ⇒ 父被杀 ⇒ 子被连带】★** ⇒ ★**所以你这一趟: ① 干活顺序 = 【先把活干完落盘】(★每件交付物落盘就追加 rc★) ② 写盘要勤 (★每 10 分钟至少一次★) ⇒ ★**这样再被打断, 活也不会丢** ★
> ★**⇒ 本 job (cron `fb67af40`) = 僵尸 fixing 的唯一重派方 ⇒ 本轮已重派 = cont3 续做 (★不是从零重做★)★**

## ★★⑰-1 · 盘面实况 (★main 20:4x~20:5x 本机实跑, 不抄任何交卷报告★)

★**★好消息: 主体【全做完了】⇒ 你这趟【只剩收尾 2 件】★**

| 件 | 现状 (★main 20:5x 本机实读 + 实跑★) |
|---|---|
| ★**交卷单** ★ | ★**`HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md` = 22,542 B (mtime 20:27) ⇒ ★**B0~B6 六块齐全 + 进度日志 + 无占位符 (★main 20:4x 跑 `python3 state/check_report_placeholders.py` ⇒ 全部无占位符★)⇒ ★**不要重建, 只在末尾追加一小节** ★ |
| ★**6 道闸** ★ | ★**全部已接上通道** ★ ⇒ ★**main 20:4x~20:5x 实跑** ★: `HW/check_fsin_rootcause.py` rc=0 (· `--selftest` rc=0) · `HW/check_g1a7_selection_landed.py` rc=0 (· `--selftest` rc=0) · `HW/check_onepass_commit_order.py` rc=0 (· `--selftest` rc=0) · `HW/check_onepass_preflight_coverage.py` rc=0 (· `--selftest` rc=0) · `HW/check_workpack_state_values.py` rc=0 (· `--selftest` rc=0) · ★**`HW/check_pin_function_labels.py` rc=1 (· `--selftest` rc=1) ⇒ ★这是【既有缺陷基线】(★18 条既有缺陷·改前 18 改后 18·0 条新失效★) ⇒ ★**不是你的活, 不许去修它**★** ★ |
| ★**共用判决库** ★ | ★**`HW/board_reboard.py` (35,661 B · mtime 18:42) ⇒ `--selftest` = **rc=0 · 10/10 条符合预期** ★ ⇒ ★**6 道闸都 import 它, 你不许再写一份 reboard 逻辑★** ★ |
| ★**分片** ★ | ★**★`grep -c iss297 state/fragments/hw.yaml` = 6 ⇒ 但【全是 `artifacts`】(★6 条 tool/handoff 条目, mtime 20:27·20:27:29★)⇒ ★**`interface_claims` 一条没有 + `needs_from` 一条没有 + `status` 块还停在 ISS-292 的摘要** ⇒ ★**这才是你这趟真正的活★** ★ |
| ★**受保护 5 件** ★ | ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b8` · 脚表 `a4270120454a` · BOM `5d02bece9477`** ★ ⇒ ★**必须逐字节不变 (★本单零写板 · 零落表★)★** ★ |

## ★★⑰-2 · 本趟只做 2 件 (★闸本体一个字都不许再动★)

### ★① 分片补齐 `interface_claims` + `needs_from` + `status` (★走 `state/frag_write.py` 原子写, ★★禁止 `open(p,"w")`★★)

★**★house 标准 (★照 `state/fragments/sw.yaml` 里 ISS-298 的形状★ —— ★★ISS-298 已于 20:0x 由 main 独立复验落 `verified`★, `grep -c iss298` = 4★★)** ★

★**必写的 `interface_claims` ≥ 3 条 (★key 自拟但必须带 `iss297` 前缀, 便于 grep★)**:
1. ★**HW 侧 6 道闸已全部接上「合法改板」通道** (★判决源 = 写死常量 → 落表台账链头 + 锚点 reboard 四项原子映射 {by, file, prev_md5, md5} · 照 ISS-284 已跑通的口径 · 判据方向没变 · fail-closed 三条没动 · `reboard: null` 仍按纯 md5 硬保护判★)
2. ★**反向用例全抓到** (★6 闸 × 10 条 ISS-297 通道用例 = 60 条, 沙盒跑, 真盘零写 ⇒ 全抓到★)
3. ★**零写板 · 零落表** (★受保护 5 件 md5 逐字节不变 + 板 mtime 仍 2026-11-06 07:07:17 + 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` mtime 仍 12:30:23 一个字节没写★)

★**必写的 `needs_from` ≥ 1 条 (★给 main 的, ★只列事实与代价, 不替 main / 老板拍板★)**:
- ★**交卷单 B5 的三条待决事项** ⇒ ★**其中第 ① 条建议 main 单开一单做「H-1 重锚第 2 跳」** (★把 `HW/check_pin_function_labels.py` 的 `PROTECTED_MD5` 里网表/脚表/BOM 三个旧基线重锚到 ISS-283 落表后的真盘值 + 在 `MD5_ANCHOR_CHAIN` 追加一跳 + 把 T5/T11 的自证前提从「全部干净」收窄成「被篡改的那一件干净」⇒ ★**做完那 18 条会降到 15 条, 闸就干净了★)★ ⇒ ★**这是建议, 不是决定, 让 main 拍★** ★
- ★**第 ② 条**: ★**合法改板那天, 操作者除了「写板 + 落表台账追加一行 + 锚点填四项」, 还得同步在第 3 道闸自己的板 md5 台账变更区登记那一跳 ⇒ ★**建议 main 在「板只改一次」那一趟的作业包里把【三步】明确写成【四步】★** ★
- ★**第 ③ 条**: ★**MECH 侧 2 道闸 + SW 侧 1 道由 ISS-296 / ISS-298 同口径接通道 (★SW 侧已完成 ✓ / MECH 侧进行中 ✓)⇒ ★**跨域不许 import 对方的判决库, 各自写自己的★** ★

★**★也要把 `status` 块更新成你这一单的 (★用 `--status` 参数★)★**: ★`phase=delivered progress_pct=100 health=绿 summary="★ISS-297 cont3 交卷 …"`★ (★现在还停在 ISS-292 的摘要, ★必须改过来★)

### ★② 交卷单末尾追加一小节 (★★不许重写 B0~B6, 只许在末尾追加★)

★**追加一节 `## ⑰ 交卷后追记 (★2026-11-17 20:5x cont3★)`**, 写清:
- ★**main 20:4x~20:5x 独立复跑的 6 道闸 rc (★含第 5 闸 rc=1 是既有基线这条, 原样写★)** ★
- ★**分片补齐后 `grep -c iss297 state/fragments/hw.yaml` 的新数字** ★
- ★**受保护 5 件 md5 + 板 mtime 的终检读数** ★

## ★★⑰-3 · 交卷前必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/board_reboard.py --selftest ;              echo "rc=$?"
python3 HW/check_fsin_rootcause.py ;                   echo "rc=$?"
python3 HW/check_g1a7_selection_landed.py ;             echo "rc=$?"
python3 HW/check_onepass_commit_order.py ;              echo "rc=$?"
python3 HW/check_onepass_preflight_coverage.py ;        echo "rc=$?"
python3 HW/check_pin_function_labels.py ;               echo "rc=$?"   # ★既有缺陷基线·期望 1★
python3 HW/check_workpack_state_values.py ;             echo "rc=$?"
python3 state/merge.py ;                                echo "rc=$?"
python3 state/gate_check.py ;                           echo "rc=$?"
python3 state/issue_check.py ;                          echo "rc=$?"
grep -c iss297 state/fragments/hw.yaml ;                echo "count=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb
```

## ★★⑰-4 · 边界 (★一条不许松★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** · ★**不许写落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 本体 (★只读★)** ★ · ★**不许动 `SW/` 与 `MECH/` 的任何文件和分片** (★SW 侧那道闸归 ISS-298·MECH 侧两道闸归 ISS-296★) ★ · ★**不许放宽 fail-closed 三条** · ★**不许为了让闸变绿去改台账里那两个 `md5:` 基线** (★那是「挖坑」, 正是 ISS-284/273 堵死的洞★) ★ · ★**不许把 `HW/check_pin_function_labels.py` 那 18 条既有缺陷顺手修掉** (★改前 18 改后 18★) ★ · ★**不许改 `HW/board_reboard.py`** (★共用判决库·6 道闸都 import 它·本单只读★) ★ · ★**不许改 `state/gate_check.py` / `state/issue_log.yaml`** (★签字是 main 的活★) ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ 缺口一律【自己网上查】+ 标证据等级 [官网]/[实测]/[媒体]/[推算]/[0数据] + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★) ★ · ★**不替老板拍板** ★ · ★**不自签 issue_log** (★verify_by=main★) ★ · ★**只写自己的分片 `state/fragments/hw.yaml`** (★`mech.yaml` / `sw.yaml` / `pm.yaml` 一个字节都不许碰★) ★ · ★**实物 `[实测]` = 0 条** ★

## ★★⑰-5 · 死因纪律 (★这一趟的命门就是【别再被连带打死而不落盘】★)

★**① 干活的顺序必须是【先落盘】**: ★**这一趟只有两件, 都是十几分钟的事 ⇒ ★**先把 `interface_claims` 写进分片 (★`frag_write.py` 原子写★) ⇒ 再补 `needs_from` ⇒ 再改 `status` ⇒ 最后追加交卷单那一小节** ★ ⇒ ★**这样再被打断, 至少交卷单是完整的 (★它已经完整了★)★ ★
★**② 每 10 分钟至少一次写盘** · ★**每落一件交付物就把 rc 追加进交卷单** ★
★**③ 单条 `exec` ≤ 60 秒** · ★**长任务一律 `nohup ... > logs/iss297/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) ★
★**④ 分片写完 `grep -c iss297 state/fragments/hw.yaml` 校验** ★
★**⑤ 不许把整份大文件读进来** (★只 grep 你要改的那几行★) ★
★**⑥ 写分片必须用 `state/frag_write.py` 原子写 (★禁止 `open(p,"w")`★)** ★
★**⑦ 文档订正必须追加式 (★老字不许删★)** ★
★**⑧ 不许为了让闸变绿而改闸 / 放宽判据** ★
★**⑨ 沙盒副本上做反向用例, 真件一个字节不许碰** ★
