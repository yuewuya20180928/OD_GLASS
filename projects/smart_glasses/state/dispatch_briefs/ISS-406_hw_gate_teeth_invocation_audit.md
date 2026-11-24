# ★ISS-406 · hw-lead · 板那一趟【验收链有没有牙齿】—— 门禁链 18 道闸的「实际调用方式」逐道清账 + fail-closed 闸 ★

★**单号**: ISS-406 · ★**派活**: 项目总工 (main / moli) · ★**执笔**: hw-lead (硬件总工) · ★**日期**: 2026-11-25
★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
★**主线关系**: ★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属 ★**「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板)** ★

---

## ★0 · 一句话题面 ★

★★**门禁链 `state/gate_check.py` 上那 18 道闸, 全仓没有任何一道闸在问: 「它被调用时用的是哪一档? 那一档会不会让一个坏掉的板判绿?」—— 最典型的就是 `state/check_pcb_drc.py`: 不带 `--strict` 时它的 unconnected 判据 `ok4 = (n_unc == 0) if strict else True` ⇒ **恒真 ⇒ 假绿** ⇒ 板那一趟若有人拿「DRC 通过」当验收凭据, 而那次调用没带 `--strict`, 则 **unconnected=45 也会判绿** ⇒ 验收是假的 ⇒ 板改第二次 ★★**

---

## ★★一 · 题面 (★main 2026-11-25 01:5x~02:0x 本机实读 + 本机实算, 不抄任何 agent 报告★) ★★

### ★1.1 · 本机实测事实 (★全部可复现★) ★

| # | 事实 | 实测读数 | 出处 (★本机实读★) |
|---|---|---|---|
| ① | ★**门禁链挂 18 道闸** ★ | `EXTRA_GATES` 7 道 + `PINNED_MD5_GATES` 10 道 + HW pinout 闸 1 道 = **18** | `state/gate_check.py` L211 `EXTRA_GATES` / L262 `PINNED_MD5_GATES` / L176 `HW_PINOUT_GATE` |
| ② | ★**链上闸一律用 subprocess 调, 参数是每条目的第三个元素** ★ | `subprocess.run(cmd, cwd=PROJ, capture_output=True, ...)` | `state/gate_check.py` L291 |
| ③ | ★**链上已有一道闸用「非默认档」跑** ★ | `HW/check_pin_function_labels.py` ⇒ 链上 args = `("--expect-known",)` ⇒ ★**裸跑必然 rc=1 (基线常量停在 ISS-257 旧值) ⇒ 链上跑的是「已知缺陷放行」档** ★ | `state/gate_check.py` L267 + L258 注释 |
| ④ | ★★**投板前命门闸 `state/check_pcb_drc.py` 不在链上, 且它带一档「恒真判据」** ★★ | `state/check_pcb_drc.py` L134-L139 逐字: `strict = "--strict" in sys.argv` · `ok4 = (n_unc == 0) if strict else True` · 输出行还自带 `← 骨架阶段允许未布线 (布线完成后用 --strict 归零)` ⇒ ★**不带 `--strict` ⇒ C4 unconnected 恒判绿** ★ | ★**本机实读源码★** (★ISS-404 交卷页也已点名同一件事, 属独立复核一致★) |
| ⑤ | ★**另一道命门闸 `state/check_pcb_nets.py` 也不在链上, 且今天就是红的** ★ | `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ rc=1 (C1 焊盘级等价: 缺失 0 · 多余 2 · 同号异网 3) | 本机实跑 (★daily_check 2026-11-25 01:32 同读数★) |
| ⑥ | ★**板 md5 自 2026-11-06 起未动, 18 天** ★ | `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` | 本机 `md5sum` + `stat` |

### ★1.2 · ★为什么至今零机器闸盯这一格 ★

★**既有闸盯的是「闸在不在链上」, 不是「闸被怎么调」** ★:
- `HW/check_onepass_preflight_coverage.py` (★已挂在钉板闸④★) 的 **P3 判据 = 「清单引用的脚本在本机真实存在」** ⇒ ★**只查存在, 不查调用档位★**
- ★**ISS-404 交卷的 `HW/check_onepass_gate_hook_coverage.py` (G1~G7) 判的是「点名的闸有没有在挂链表 / 人工签核台账」** ⇒ ★**同样只查「在不在」, 不查「在链上时被怎么调」★**
- ★**ISS-388 交卷的 `SW/tools/check_sw_gate_health.py` H1 盯的是「同一道闸在两个 TMPDIR 深度下读数是否相同」(环境无关性)** ⇒ ★**也不是「宽松档」这一轴★**

⇒ ★**结论: 「调用档位 ⇒ 判据强度」这一轴, 全仓至今零机器闸覆盖 ⇒ 本单补这一格** ★

### ★1.3 · ★坏结局 (★为什么值钱★) ★

★**「板只改一次」= 板 md5 全生命周期只许变 1 次** ⇒ ★**投板前的每一道检查, 都是「板改第二次」的最后一道闸** ★
⇒ 坏结局三选一:
① ★**宽松档假绿**: 板那一趟当天有人跑 `check_pcb_drc.py` (不带 `--strict`) 拿到 rc=0 ⇒ ★**unconnected=45 也判绿 ⇒ 拿一张没布完的板去投** ⇒ 板改第二次 (2-4 周 + 一批板的钱) ★
② ★**fail-open 空转**: 某道链上闸在「输入文件缺失 / 目标文件被改名 / 沙盒路径不对」时返回绿 ⇒ ★**红的东西被当成绿** ⇒ 与 ISS-388 的「判据与环境耦合」同族但更毒 (它直接判板) ★
③ ★**链上闸自己坏了没人知道**: 与 ISS-388 同一形状 ⇒ ★**「闸自己坏了」这件事本身零检测手段** ★

---

## ★★二 · 本单交付 (★5 件 · 全部零写板★) ★★

| # | 交付物 | 路径 | 验收口径 |
|---|---|---|---|
| ① | 真相页 | ★**新建** `HW/PCB/BOARD_ONEPASS_GATE_TEETH_AUDIT.md` ★ | §0~§7 + 机器块; ★**三张表**: (a) ★**链上 18 道闸 × 实际 argv × 该闸源码里存在哪些「宽松档开关」× 链上用的是哪一档** ★ (b) ★**fail-open 嫌疑清单**: 每道链上闸在什么条件下会「输入缺失却判绿」(★静态判定优先, 不许靠猜★) (c) ★**投板前必须用严格档跑的闸名单 + 为什么** ★ |
| ② | 新闸 | ★**新建** `HW/check_onepass_gate_teeth.py` ★ | ★**裸跑 rc=1** (★红的是现状, 不是闸故障★) · `--selftest` **rc=0** · 末行逐字 `ALL TESTS PASS` (★正向 ≥1 + 反向 ≥8★) · ★**零挂链** (★`grep -c check_onepass_gate_teeth state/gate_check.py` = 0★) |
| ③ | 交卷页 | ★**新建** `HANDOFF/2026-11-25_hw-lead_ISS406_验收链牙齿清账与闸.md` ★ | B1~B7 全填 (★标题用仓里规范口径, gate_check Q1 六块齐全★) |
| ④ | 自有分片收口 | `state/fragments/hw.yaml` | ★**只走 `state/frag_write.py`** ★ (★禁止 `open(p,"w")`★) · 写后四项自检: 条数 / 丢 key / 多的 key / 内容有变的条 (★老条目逐字比对★) |
| ⑤ | 留证 | `logs/iss406/` + 沙盒 `tmp/iss406/` | ★**不硬链接真件 · 不写系统 `/tmp`** ★ |

### ★2.1 · 新闸的判据骨架 (★main 给的方向, 具体实现你定, 但不许放松★) ★

| 判据 | 要求 |
|---|---|
| ★**T1 链上闸逐道台账自洽** ★ | ★**链上 18 道闸, 每道在台账里有且只有一行; argv 必须从 `state/gate_check.py` 用 AST 解析出来 (★不许手抄★); 解析条数 ≠ 实际条数 ⇒ 判红** ★ |
| ★**T2 宽松档识别** ★ | 对每道链上闸, 从其源码里找出「会让判据放宽的开关参数」(★`--strict` / `--expect-known` / `--allow-*` / 形如 `if "<flag>" in sys.argv` 的分支★) ⇒ ★**链上用宽松档的闸必须被点名 + 写清「宽松档放宽了哪条判据」** ★ |
| ★**T3 fail-open 嫌疑自证** ★ | 每道链上闸必须给出「输入缺失时会不会判绿」的判定 + 依据 (★源码行号级证据★) ⇒ ★**判「可能会」但拿不出行号证据的, 算没查** ★ |
| ★**T4 板三证不动** ★ | 板 / 网表 / 脚表 / BOM md5 与基线逐字相同 (★基线板 md5 = `611b869e13518c3c023fb178f91a0075`★) |
| ★**T5 零挂链 + 零外发自证** ★ | `grep -c` 本闸名在 `state/gate_check.py` = 0; ★`state/outbox/` 未动 ★ |
| ★**T6 证据分级** ★ | 每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` |
| ★**T7 零写板自证** ★ | 板 md5 / mtime / size 三项与基线逐字相同 |

★**★自指悖论 (★必须在交卷页点名, 不许自己解决★)★**: ★**本闸自己也不在链上 ⇒ 它同样需要被登记 (在链上 或 人工签核台账里) ⇒ 那一步在 main 地界 ⇒ 台账里「本闸自身」这一行请写成 `待 main 挂链`, 并把这条悖论作为问句交 main** ★

### ★2.2 · 必跑命令 (★交卷页 B6 要贴原样输出 + rc★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-406_hw_gate_teeth_invocation_audit.md   # 期望 rc=0
python3 HW/check_onepass_gate_teeth.py                     # 期望 rc=1 (★红的是现状★)
python3 HW/check_onepass_gate_teeth.py --selftest          # 期望 rc=0 · 末行逐字 ALL TESTS PASS
bash state/pcbnew_py.sh state/check_pcb_drc.py             # ★不带 --strict 的读数 (★留证: 假绿对照·单跑要几分钟, 只跑一次★)
bash state/pcbnew_py.sh state/check_pcb_drc.py --strict    # ★带 --strict 的读数 (★对照: unconnected 项必须不同★)
python3 HW/check_onepass_preflight_coverage.py             # ★既有钉板闸④不许被本单弄红 (★rc 必须与开工前逐字相同★)
python3 state/merge.py                                     # rc 必须 0
python3 state/gate_check.py                                # rc 必须 0 · Q1 必须 18/18
```

★**时间预算**: ★`check_pcb_drc.py` 单跑要几分钟 ⇒ ★**最多跑 2 次 (一次宽松档 + 一次严格档)**, 其余结论一律走静态分析 + 已有日志 ⇒ **不许跑满链 20 遍** ★

### ★2.3 · 边界 (★违反任一条 = 本单不算交卷★) ★

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` + size `4940213` 三项逐字未动 |
| ★**零落表** ★ | 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` 逐字未动 |
| ★**零改既有闸判据/阈值** ★ | 既有闸文件 md5 与开工前逐字相同 (★至少点名 `state/gate_check.py` · `HW/check_onepass_preflight_coverage.py` · `state/check_pcb_drc.py` · `state/check_pcb_nets.py`★) |
| ★**零改既有页正文** ★ | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` md5 逐字未动 |
| ★**零挂链** ★ | `grep -c check_onepass_gate_teeth state/gate_check.py` = 0 |
| ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ `state/outbox/` 22 件逐字未动 ⇒ **没有「批一句可以发」这个选项** ★ |
| ★**不代拍** ★ | 挂不挂链 / 哪几道用严格档 / 要不要人工签核台账 ⇒ 全部交 main, 机器块写 `not_decided_here` |
| ★**不自签** ★ | ★**不许写 `state/issue_log.yaml`** ★ (★签收由 main 做★) |

---

## ★★三 · 纪律 (★与其它单一样的硬规矩★) ★★

① ★**写分片必须用 `state/frag_write.py`** (★禁止 `open(p,"w")`★)
② ★**只写本任务允许的文件, 不碰别人的** (★尤其是: `HW/PCB/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md` 是 ISS-404 的交卷件, 只读不写★)
③ ★**证据分级** `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 必须标
④ ★**不许外发任何邮件/询价/问询/采购** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案
⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
⑥ ★**不许自己把新闸挂上链** (★挂链是 main 的地界★) ⇒ 只在交卷页里点名建议

## ★★四 · 留给 main 的问句 (★你只摆代价, 一条都不许代拍★) ★★

- ★**Q1**: 链上 18 道闸里, 有几道用「宽松档」跑? ⇒ 要不要把其中某几道改成严格档? (★代价: 改了链上读数会变, 可能当场红★)
- ★**Q2**: `state/check_pcb_drc.py` 要不要挂链? 挂的话必须带 `--strict` ⇒ 挂上去当天链会红 (unconnected=45) ⇒ 挂不挂?
- ★**Q3**: 「投板前必须用严格档跑的闸名单」要不要成为一份人工签核台账页?
- ★**Q4**: 本闸自己挂不挂链 (★自指悖论★)?
- ★**Q5**: fail-open 嫌疑清单里若有真阳性, 谁负责修 (★判据口径变更属 main 地界★)?
