★★**目标 (★内部活·结构侧·★【续做】·★不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★★**上一轮 (19:19~19:29) 被 runTimeout 掐死 ⇒ 盘上【三处老账已改了 2 处半】, 但【交卷层 + 新门禁】一件没落 ⇒ 本轮只补缺口** ★★

★★**① 上一轮怎么死的 (★main 19:4x 实测, 不是猜★)** ★★
· 会话 `agent:mech-lead:subagent:6348eece-…` 19:19:42 起 · **19:29:40 被 timeout 掐断** (runtime 596s, abortedLastRun=true) ⇒ transcript 末条 = exec 返回 「Aborted」
· ⇒ ★**它在改文档的半路上被掐** ★

★★**② 盘上实况 (★main 19:4x 自己实跑, 不抄你的会话★)** ★★
| 老账 | 盘上实况 | 本轮要不要做 |
|---|---|---|
| ★**【A】充电耗散口径** | ★**`MECH/verify_budget.py` 已是 buck 口径** (L86-89: `P_CHARGE_LO/HI = 0.45/0.57` · `P_CHARGE = 0.50` · L15-17 头注写明旧口径 0.8 线性公式已判死) · ★**`python3 MECH/verify_budget.py` 实跑 rc=0 · 「✅ 门禁绿: 充电耗散口径 = buck」** ★ · ★**`MECH/MECH_BUDGET.md` L604-605 已把旧口径标为「已判死 (历史沿革)」并写了新值 0.45-0.57 W** ★ | ★**基本已落 ⇒ 只许【核对 + 补出处/行号到订正表】, 不许重复改** ★ |
| ★**【B】铝 k 201 保守侧** | ★**早已落 (ISS-219 落的, 不是本单)**: ★**`MECH/MECH_BUDGET.md` L519 「k 口径 (旧口径 237 已订正) → 201」+ L707/L875/L1017/L1092 全是 201** · ★**`MECH/verify_budget.py` L111 `K_AL_6063_T6 = 201.0` + L112 留 237 只作追溯 + L118 `R_AL_201`** ★ | ★**已落 ⇒ 本单只登记「已落 + 出处」, 不许再改数值** ★ |
| ★**【C】检修口文档 15mm→60×30** | ★**`MECH/SERVICE_PORT_ISS092.md` 已改 (mtime 19:25:58)**: ★**L5 有 ISS-251 口径订正范围声明 · L19/L200/L201 已用 需求 36.00 / 余 +2.00 (最坏 +1.40) · L22/L281/L322 已换 30mm 板套 A 基准 (P2 Y=15.00 / S2 Y=20.00) · L89/L192 已标旧 15mm 口径作废** ★ | ★**基本已落 ⇒ 只许【逐处核对有没有漏的 15mm 残留 + 补出处】** ★ |
| ★**新门禁 `MECH/check_budget_caliber.py`** | ★**不存在** ★ | ★**本轮必须建** ★ |
| ★**交卷单 `HANDOFF/2026-11-16_mech-lead_ISS251_*.md`** | ★**不存在** ★ | ★**本轮必须写** ★ |
| ★**分片 `state/fragments/mech.yaml`** | ★**ISS-251 的 claim/artifact 未写** (mech.yaml mtime 18:47 = 开单前) ★ | ★**本轮必须写** ★ |
| ★**三处逐条订正表 (旧值→新值 + 文件 + 行号 + 证据等级)** | ★**缺** ★ | ★**本轮必须出** ★ |

★★**③ 本轮只做这 5 件 (★少一件即无效★)** ★★
① ★**三处逐条订正表** (★每条: 旧值 → 新值 + 文件 + 行号 + 证据等级 + 依据出处★) ⇒ ★**A/B/C 三处逐处列, 已在盘的标「★已落 (出处: 行号)★」, 本轮补的标「★本轮补 (行号)★」** ★
② ★**新机器门禁** `MECH/check_budget_caliber.py` (★rc=0★) + ★**`--selftest` (★反向用例 ≥4 条: 改回旧口径 / 改数字 / 删依据出处 / 改文档数字 ⇒ 必须红★)★ ⇒ ★**只判口径, 不许碰别的域的判据** ★
③ ★**交卷单** `HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md` (★B1~B6 六块齐全; ★`gate_check` 按【标题行】认块 ⇒ 标题要带它要的语义关键词★)
④ ★**分片** `state/fragments/mech.yaml` (★**必须**走 `python3 state/frag_write.py --agent mech-lead …` 原子写★) ⇒ +artifact ×N / +claim ×N / +need (给 main 的, 逐条写清)
⑤ ★**并发说明一行 (★必写★)**: ★**`MECH/check_demo_struct_truth.py` 的 G5b / C21 现在是红的 (main 19:4x 实测: 「21/23 组通过 · FAIL 2 组」· 原因是 `HW/netlist_v1.csv` 盘上 md5 `16ac89f7…` ≠ 锚点 `611c3ba3…`)** ⇒ ★**那是 hw-lead 的 ISS-249 落表造成的 md5 变化, 不是你的失败, 你不许去修它** ★ ⇒ ★**你在交卷单里写明这一行★**

★★**④ 验收命令 (★逐条要 rc, 原样贴进交卷单 B5★)** ★★
```
python3 MECH/verify_budget.py                       # rc=0 (★buck 口径已对拍★)
python3 MECH/check_budget_caliber.py                # rc=0 (★本轮新建★)
python3 MECH/check_budget_caliber.py --selftest     # rc=0 (★反向用例全抓到★)
python3 MECH/service_port_check.py                  # rc=0 (★当前绿★)
python3 MECH/check_demo_struct_truth.py              # ★**21/23 · FAIL 2 = G5b/C21 (并发落表, 非本单)** ★
python3 state/merge.py && python3 state/gate_check.py   # rc=0 (★Q1 18/18★)
md5sum MECH/check_demo_struct_truth.py MECH/service_port_check.py MECH/hinge_usb_check.py
# ★**前三个受保护脚本必须逐字节不变** (★`fa9b59e5…` 是 check_demo_struct_truth.py 的基线★) ★
```

★★**⑤ 边界 (★越界即无效★)** ★★
· ★**不许碰 `HW/` (★网表 / 脚表 / BOM / 板 / `.kicad_pro` 一个字节不许动★)** · ★**不许碰板 / PCB 布线 / 布局** ★
· ★**不许改 `MECH/check_demo_struct_truth.py` / `MECH/service_port_check.py` / `MECH/hinge_usb_check.py`** (★含常量: 夹具基准 Y / 焊盘阵列 Y / `pcb_thk` 都不许动★ ⇒ 等 main + hw-lead 定 30mm 板上的最终值 ⇒ 登记 need 给 main)
· ★**不许改 `PROJECT_TRACKER.md` §0** · ★**不许自签 `state/issue_log.yaml`** (★verify 留给 main★) ★
· ★**零外发** · ★**不替老板拍板**: ★**d 值 (15/18/20) · u8 端件截面 · 集热面材质/面积 · 板长 · 板厚档位 ⇒ 一律只列选项 + 量化代价, 不代拍** ★

★★**⑥ 硬规矩 (★上一轮就是死在这★)** ★★
· ★**先落盘骨架再填内容** (★第 1 分钟就把交卷单文件 + 订正表的空表写到盘上, 再一条条填★) ⇒ ★**上一轮 10 分钟改了 2 处半文档, 但交卷层一件没落 ⇒ 等于白干** ★
· ★**每改完一处立刻写盘 + 在订正表里记一行 (旧值→新值+行号)★** ⇒ ★**被掐时不丢活★**
· ★**本轮 runTimeout 5400s (90 分钟) ⇒ 慢慢做, 但别攒** ★
