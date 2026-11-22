# ISS-353 · sw-lead · ★rk3572 目标口径清账 + 板端依赖降级 · ★**cont1 续做**★ · 纯口径 · 零写板

★**这是 cont1 续做派活 (★不是从零重开★)** ★

## ★★为什么是 cont1 (★上一趟怎么死的·本趟从哪儿续★) ★★

★**上一趟 (2026-11-23 04:2x 派) 的会话被掐死了, 但产物部分在盘** ⇒ ★**本单 = 从已完成位置续做, 不是从零★**

★**死因 (★main 本机实读, 不抄任何 agent 报告★)**: ★**兄弟 job `fb67af40` (ARS45 队列自动派活) 那一趟 cron 自己超时了** ⇒ 错误原文 `cron: job execution timed out (last phase: model-call-started)` (★`~/.openclaw/cron/runs/fb67af40-a9eb-4cdd-a842-8cbb8fdd7865.jsonl` 逐字★) ⇒ ★**父 run 一死, 它派出的两个子会话在同一瞬间被连带 abort** (★sw-lead 子会话 `b0220170` 与 hw-lead 子会话 `4a01dc6e` 的 `endedAt` 相差 114 ms = 同一瞬间死的·`abortedLastRun: true`★) ⇒ ★**不是 sw-lead 自己的问题, 是父 job 超时连带** ★

★**已在盘的产物 (★别重做·直接用★)** ⇒ 全在 `logs/iss353/` (★7 件★):

| 文件 | 内容 | 状态 |
|---|---|---|
| `config_probe_rknn3.log` | ★**rknn3-toolkit 1.2.0 正/反向实测**: `config(target_platform='rk3572')` **rc=0** · `config(target_platform='rk3576')` **抛异常** · RKNN 方法清单 (★证明 config 真读 target_platform★) | ★**已完成, 直接引用**★ |
| `config_probe_toolkit2.log` | toolkit2 侧合法 target 清单 | ★已完成★ |
| `convert_rk3572_1run.log` | rk3572 target 转换跑通 | ★已完成★ |
| `roundtrip_probe.log` | 产物往返探针 | ★已完成★ |
| `official_lookup_changelog.log` / `official_lookup_tree.log` | 官方检索记录 | ★已完成★ |
| `caliber_scan_before_cleanup.txt` | ★**全仓扫描结果 (★这是本单最贵的一份产物★)**: 扫面 `SW/ HW/ state/fragments/ HANDOFF/ logs/ REQ/` · 文本文件 **1984** 个 · 命中 **355** 行 (★结论矛盾 **86** · 历史叙述 **269**★) · ★**逐条点名 (文件 + 行号 + 原文片段 + 判定 + 处置建议) 的名单表已经在盘**★ | ★**已完成, 直接用★** |

★**没做的 (★本趟要补的就是这些★)**:
1. ★**交卷页** `HANDOFF/2026-11-23_sw-lead_ISS353_*.md` — ★**完全没写** (★HANDOFF 目录下 `ISS-35[34]` 两个交卷页都不存在★)
2. ★**分片登记** — ★**`state/fragments/sw.yaml` 里 `iss353` 命中 = 0** (★实测 grep 四个分片文件全是 0★) ⇒ ★**上一趟的结论一个字都没进台账★**
3. ★**本单自带的闸** — ★**没有新建** (★扫描脚本可以复用 `logs/iss353/caliber_scan_before_cleanup.txt` 的逻辑, 但★**交付物必须是一个能跑的、带 `--selftest` 反向用例的独立脚本★**★)
4. ★**清理/订正那 86 条结论矛盾** — ★**`caliber_scan_before_cleanup.txt` 的文件名就写着 "before_cleanup" ⇒ 说明上一趟正要做这一步就被掐死了★**
5. ★**板端不可达复证 + 降级 A/B/C 三档写死**
6. ★**结案建议 (ISS-155 的 blocker 能不能降)**

★**纪律**: ★**「不信上一趟」** ⇒ ★**引用上一趟的读数时必须注明「引用上一趟本机实测 (04:2x)」并给出你自己的复跑读数, 两者不一致就写出来** ★

---

## ★★本单只做 4 件 (★纯口径 · 零写板 · 零落表 · 零采购 · 零外发★) ★★

★**任务书全文 = `state/dispatch_briefs/ISS-353_sw_rk3572_target_caliber_cleanup.md`** ⇒ ★**先把它读完, 它的 4 件交付物定义、边界、必跑项一律照办, 本页只说「从哪儿续」★**

★**但 ★**本单的边界收紧一条**: ★**上一趟已把「结论矛盾 86 条」的名单扫出来了 ⇒ 本趟★**不许只交名单**★, 必须★**逐条处置** (★要么改写成当前真值, 要么写明「★已由 ISS-263 (rknn3-toolkit 1.2.0 支持 rk3572) 取代·本条保留作历史留档·结论不再引用★」★) ⇒ ★**只报「扫到 86 条」不算交卷** ★

★**新口径必须写清三句** (机器读分片时不会去看上下文):
- ① ★**toolkit2 (2.3.2 / 2.5.0) 不支持 rk3572 target** ⇒ [官网]+[实测] ⇒ ★**所以转换链要用 rknn3-toolkit 1.2.0** ★
- ② ★**rknn3-toolkit 1.2.0 支持 `target_platform='rk3572'`** ⇒ [实测] ⇒ ★**转换链这一环已通** ★
- ③ ★**板端接受性仍 [0数据]** ⇒ ★**降级方案 = 板到手一条命令出 PASS/FAIL** (★`SW/tools/rk3572_rknn3_board_smoke.sh` 已存在★) ⇒ ★**板不来 ⇒ demo 路线【不被这条卡住】, 卡的是「验收何时做」, 不是「能不能做」** ★

★**板端降级三档必须写死 (★不许只写「等板子」★)**:
- ★**降级 A (主)**: 板到手 ⇒ `SW/tools/rk3572_rknn3_board_smoke.sh` 一条命令 ⇒ PASS/FAIL + 判据 (能 init / 能跑完 / 精度不塌 / NPU 耗时对得上 `HW/e2e_budget_rk3572.py`) ★
- ★**降级 B**: 板不来 ⇒ demo 阶段不停, 用 rknn3-toolkit 产物推进 PC 侧链路; ★**板端验收登记为「待板」而不是「待外部回复」** ★
- ★**降级 C**: 若板端拒收 ⇒ 三档 (查 rkaiq/板端 runtime 有无 rk3572 专用编译 / 换 SoC / CPU 推理) ⇒ ★**写清代价排序, 供老板拍, sw-lead 不代拍** ★

★**结案建议交 main (★给选项 + 代价, 不代老板拍★)**: ★**ISS-155 的 blocker 状态能不能降** (★从「demo 头号卡点」改成「转换链已通 / 板端待板」是否成立? 降级后它还阻塞 demo 路线选择吗?★) ⇒ ★**给结论 + 依据 + 残留代价 + 需要老板拍的那一条 (若有)** ★

---

## ★★交付物 (★4 件, 一件不许少★) ★★

1. ★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS353_rk3572目标口径清账.md` (★B0~B7 七块齐全★ + ★页内引用路径逐个在盘 (MISS = 0)★ + ★**板指纹前后双证**★)
2. ★**追加式订正**: `SW/RK3572_TARGET_COMPAT_V2.md` ★**加一节 v2.1 (零删除老行; 只追加/改写被点名的那几行, 老字别删)★** ⇒ 把 ISS-263 的 rknn3 事实与本单的新口径并进去
3. ★**证据**: `logs/iss353/` (★在上一趟 7 件基础上补齐: 清理/订正后的复扫名单 + 必跑项原样输出★)
4. ★**分片**: 只走 `python3 state/frag_write.py --agent sw-lead` (★禁止 `open(p,"w")` 手改 YAML★) ⇒ ★**交卷时 `grep -c iss353 state/fragments/sw.yaml` 必须 ≥ 5** (★上一趟 = 0 = 没登记★)

★**本单自带的闸** (★**新写**一个只读判定脚本, ★**文件名与路径你自己定** (★放 `SW/tools/` 下, ★**交卷页里写清你定的那个路径★)★)): ★**扫全仓, 凡仍写着「rk3572 不是合法 target」/「必须用 rk3576 target」这类【结论】的 ⇒ 逐条点名列出 (含文件 + 行号 + 原文片段 + 判定「历史叙述(可留) / 结论矛盾(要处置)」) ⇒ 输出必须带名单, 只报数量 ⇒ rc=1** ★ ⇒ ★**须带 `--selftest` 反向用例 (★故意留一条旧结论在临时副本里 ⇒ 必须被抓出来★)** ★

★**★沙盒纪律 (★本轮新增, 因为 /tmp 配额刚被打爆过★)★★**: ★**所有临时文件/沙盒一律落项目盘 `$PWD/tmp/` (★如 `tmp/iss353/`★), ★**不许写 `/tmp`★** (★`/tmp` 是带 userquota 的 tmpfs (7.5G), 2026-11-23 04:4x 实测配额已打满 ⇒ 连 1 MB 写都失败 ⇒ ★**写 /tmp 会让闸门拿到假读数 (rc=120 / 0 字节)★**) ⇒ ★**要跑 KiCad 导出这类必写盘的动作, 先 `export TMPDIR=$PWD/tmp`★ ★

---

## ★★边界 (★一条都不许越★) ★★

- ★**零写板**: `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 必须是 `611b869e13518c3c023fb178f91a0075` / mtime 必须是 `2026-11-06 07:07:17.362193413` ⇒ ★**开工前 + 交卷后各打一次, 双证贴 §B6** ★
- ★**零落表**: 不改网表 / 脚表 / BOM / 原理图 / 任何闸 / `state/fragments/pm.yaml` / `state/fragments/hw.yaml` / `state/fragments/mech.yaml` / `state/issue_log.yaml` (★自签 issue_log 是 main 的地界★)
- ★**只写**: `state/fragments/sw.yaml` (★只走 frag_write.py★) + `HANDOFF/2026-11-23_sw-lead_ISS353_*.md` + `logs/iss353/` + `SW/RK3572_TARGET_COMPAT_V2.md` 的追加段 + `tmp/iss353/` (★沙盒★)
- ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★) ⇒ ★**`state/outbox/` 里的草稿一律不发, 只作资料留档** ★
- ★**零采购**: ★**不许再提「买一块 RK3572 板/开发板」** (★老板 2026-11-04 19:10 指示★)
- ★**不替老板拍板** · ★**不新增拍板项**
- ★**证据分级必标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ ★**不许把 [推算] 写成 [实测]** ★
- ★**不许改既有闸的判据方向** · ★**不许动 `state/gate_check.py`** · ★**不许动 `state/merge.py`**

## ★★必跑项 (★交卷前跑, 把原样输出贴进交卷页 §B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp          # ★/tmp 配额已打满·必写盘的动作一律落项目盘★
python3 state/merge.py            # rc 必须 0
python3 state/gate_check.py        # rc 必须 0 · Q1 必须 18/18
python3 state/frag_write.py --agent sw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```

★**任务书全文**: `state/dispatch_briefs/ISS-353_sw_rk3572_target_caliber_cleanup.md` (★`python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-353_sw_rk3572_target_caliber_cleanup.md` ⇒ rc=0★)
