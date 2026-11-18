# ISS-272 · sw-lead 交卷单 —— 独立复核 ISS-261「投递口径① mode=none 归类」改判

> ★**派活人**: 项目总工 (main / moli) · ★**复核人**: sw-lead (★与 owner=main 分离 ⇒ 满足 `state/issue_check.py` C3「验证分离」★)
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**单性质**: ★**内部活 · 运维工具侧 · 独立复核类 (零写板 · 零落表 · 零外发 · 零采购)★** ⇒ ★**不是老板级拍板** ★
> ★**老板 2026-11-17 00:43 主线口径**: 「接下来的目标是绘制 PCB 图」 ⇒ ★**本单不在 PCB 主线上** ★
> ★**老板 2026-11-12 02:02 政策**: 不再发信 / 全靠自己查资料 ⇒ ★**零外发** ★
> ★**状态**: ★**本单落 `fixing` 保持不动** (★本来就是 fixing, 不重复标★) ⇒ ★**交卷后由 main 独立复验落 `verified`** ★

---

## B1 · 结论摘要 (★一句话★)

> ### ★**main 的改判 = 对 (判据正确) + 有 3 个缺口 (缺口是什么见 B5)★**
>
> ★**① 改判对不对**: ★**对** ★ — ★**判据 `mode=none ⇒ delivered=false ⇒ no_delivery` 语义正确** (★推送本来就没开 ⇒ `delivered=false` 是预期行为★) · ★**我独立复现了隔离性: 自己 swap 修前/修后各跑一次 `delivery_health.py`, diff 只有 4 行口径① 变了, A 类 / B 类 / D 类 / 口径② / 结论行 逐字节不变** ★
> ★**② 反向用例够不够硬**: ★**判据本身够硬 (变异测试 5/5 全抓得住), 但【端到端 announce 分支在当前盘上一次都没执行过】(★变异 M6 实测证实★) ⇒ 我用【合成 run 记录】把这条分支钉死 (★本单已落地, 断言 31 → 44★)** ★
> ★**③ 有没有把真故障藏起来**: ★**三个口径各答各的, 不含糊** ——
> · ★**job 自己挂了 (status=error)**: ★**藏不住** ★ (★实测 7/4/6/6 轮「这轮没跑成」照样计数 + B 类告警照样响★)
> · ★**推送类故障 (A 类 / D 类)**: ★**看不见, 但语义上不算故障** (★推送本来就关着★) ⇒ ★**唯一真缺口在这里: A 类排除 mode=none 时, 连【认不出来的错误】也一起排除了 ⇒ 与 `classify()` 自己的「宁可吵, 不可漏」原则直接矛盾 (★沙盒实测 E3: 0 条告警★)★** ★
> · ★**三个缺口今天都不影响输出** (★实测: 当前 12 轮窗口全部落在 mode=none 时代, 追溯洗白今天打不着★) ★

★**⇒ main 可以拿这句话把 ISS-261 从 `fixed` 落 `verified` (★建议同时把 B5 的缺口 2/3 开成 needs_from 给 main 拍板★)★**

---

## B2 · 验收标准自评 (★逐条 通过/不通过/未验★)

| # | 任务书要求 | 自评 | ★**实测证据**★ |
|---|---|---|---|
| ① | ★**自己跑一遍 `--selftest` (rc 必须 = 0)** ★ | ✅ **通过** | ★**[实测]** `python3 state/delivery_truth.py --selftest` ⇒ ★**rc=0 · 31 条断言** (★main 的版本★) ⇒ ★**我加压后 rc=0 · 44 条断言** ★ |
| ② | ★**自己 swap 修前/修后做 diff (不许只信 main 的结论)** ★ | ✅ **通过** | ★**[实测]** 用 `state/.bak_delivery_truth_20261117_0435_iss261.py` 自己 swap ⇒ ★**diff 只有第 2~5 行 (4 行口径①) 变了; 第 1 行 (健康结论) + 第 6 行 (口径②) 逐字节不变** ★ · ★**run 记录 md5 前后对照 = NO_DRIFT (数据无漂移, diff 可归因)** ★ |
| ③ | ★**确认 diff 只涉及口径①** ★ | ✅ **通过** | ★**[实测]** 两份输出各 6 行; `diff` 结果 `2,5c2,5` ⇒ ★**只有 4 行口径① 变** ★ |
| ④ | ★**反向用例加压 (自己造输入, 不许只跑现成 selftest)** ★ | ✅ **通过** | ★**[实测]** ★**14 条加压** (★任务书点名 4 条 + 我自己加 10 条★) ⇒ ★**12 条符合预期, 2 条不符 ⇒ 构成缺口 3** ★ |
| ⑤ | ★**假故障会不会被藏起来的判断 (能/不能 + 为什么 + 缺口在哪)** ★ | ✅ **通过** | ★**[实测]** ★**沙盒 A/B/D 三类逐条实测 (E1/E2/E3/F) + 口径① 四个 job 实际计数** ⇒ ★**结论见 B5 的「可见性矩阵」** ★ |
| ⑥ | ★**交卷单 B1~B6 六块齐全** ★ | ✅ **通过** | ★**[实测]** `gate_check.py` ⇒ ★**Q1 18/18, sw-lead 6/6 缺: 无, 计分单 = 本单** ★ |
| ⑦ | ★**分片走 `frag_write.py --agent sw-lead`** ★ | ✅ **通过** | ★**[实测]** ★**只走 `state/frag_write.py --agent sw-lead` (★没碰 `open(p,"w")★); 未写任何别人的分片** ★ |
| ⑧ | ★**第 ③ 步做完必须把 `state/delivery_truth.py` 恢复到新版本 (自己 md5sum 确认)** ★ | ✅ **通过** | ★**[实测]** ★**swap 完立刻 `md5sum` ⇒ `a4cb793c41f33ee1681d46023c2ac2a7` (★不是假设 copy 成功★) ★ |
| ⑨ | ★**不许改 `state/delivery_health.py`** ★ | ✅ **通过** | ★**[实测]** ★**本单全程没写 `delivery_health.py`** ★ |
| ⑩ | ★**不许自签 `state/issue_log.yaml`** ★ | ✅ **通过** | ★**[实测]** ★**没碰 `issue_log.yaml`; ISS-272 状态仍是 `fixing` (★由 main 落 `verified`★)** ★ |
| ⑪ | ★**零写板 / 零落表 / 零外发 / 零采购** ★ | ✅ **通过** | ★**[实测]** ★**只动了 `state/delivery_truth.py` (加 selftest 用例) + `state/fragments/sw.yaml` (走 frag_write) + 本交卷单; 沙盒全在 `workspace/tmp/`** ★ |

★**★新增 (★不在原任务书, 但我判定必须做★): ★**变异测试 (mutation testing) ★** —— 只跑现成 selftest 证明不了「反向用例够不够硬」, ★**我把判据逐条改坏, 看 selftest 抓不抓得住** ★**

| 变异 | 改坏的地方 | selftest rc | ★**结论**★ |
|---|---|---|---|
| M1 | ★删掉 `mode=='none'` 那一支 (⇒ mode=none 也算「没送到」) ★ | **1** | ★**抓到了✔** ★ |
| M2 | ★announce 的 `delivered is False` 也吞掉 (⇒ 真投递故障被隐藏) ★ | **1** | ★**抓到了✔** (★main 的版本靠纯函数 C7 抓到; ★**我加合成用例后由 SYN 用例抓到 ⇒ 不再是一根独苗★**) ★ |
| M3 | ★`status=='error'` 优先级降到最后 (⇒ job 自己挂了被 mode=none 吞掉) ★ | **1** | ★**抓到了✔** ★ |
| M4 | ★`delivered is True` 也吞掉 (⇒ 真送到被隐藏) ★ | **1** | ★**抓到了✔** ★ |
| M5 | ★`mode=None` 缺省时直接 no_delivery (⇒ 老调用方兼容性被破坏) ★ | **1** | ★**抓到了✔** ★ |
| M6 | ★**把【端到端 announce 分支】的期望值故意改错 (⇒ 探这条分支有没有被执行)** ★ | **0** | ★★**没抓到 ⇒ 【端到端 announce 分支在当前盘上零执行】★★** (★盘上 9 个 job 的 mode 全是 none ⇒ 该分支是死代码★) ★★**⇒ 本单用合成用例替代覆盖 (M2 现由 SYN 抓到)★** ★ |

---

## B3 · 证据分级 (★实测/官方/推算/0数据★)

★**本单全部结论来自本机实跑, 无一条抄报告。证据等级逐条标注如下。★**

### ★① 独立复现 (★全部 [实测]★) ★
- ★**[实测]** `state/delivery_truth.py` 起始 md5 = `8dad8b39d873b3d930acb1c076e240cb`; 备份 `state/.bak_delivery_truth_20261117_0435_iss261.py` md5 = `00ff09721fad2b1fa8621d5af5573f7f` ⇒ ★**与 main 交卷单写的两个 md5 逐字一致** ★
- ★**[实测]** `--selftest` ⇒ ★**rc=0 · 31 条断言 (7 纯函数 + 4 job × 6 端到端)★** ⇒ ★**与 main 交卷单一致** ★
- ★**[实测]** 自己 swap 修前/修后 ⇒ `diff` = ★**`2,5c2,5` (只 4 行口径①)★**; 两份输出各 6 行, ★**第 1 行 (健康结论) 与第 6 行 (口径②) 逐字节不变** ★
- ★**[实测]** run 记录 md5 前后对照 ⇒ ★**NO_DRIFT** (★diff 可归因到判据, 不是数据在动★)

### ★② 反向用例加压 (★全部 [实测]★) ★
★**任务书点名的 4 条 (★全过★)** ★

| # | 输入 (status, delivered, mode) | 实测 | 期望 | 判定 | ★**「真故障会不会被藏起来?」自问自答**★ |
|---|---|---|---|---|---|
| ① | `("error", False, "none")` | `run_error` | `run_error` | ✅ | ★**不会藏** —— job 自己挂了, 跟推送开没开无关, 照样报「这轮没跑成」★ |
| ② | `("ok", True, "none")` | `delivered` | `delivered` | ✅ | ★**不会藏** —— 真送到了最高优先级, mode 压不掉★ |
| ③ | `("ok", False, None)` | `not_delivered` | `not_delivered` | ✅ | ★**不会藏** —— mode 缺字段按 announce 判, 与改前逐字一致★ |
| ④ | `("ok", False, "announce")` | `not_delivered` | `not_delivered` | ✅ | ★**不会藏** —— announce 下的真投递故障仍算「没送到」★ |

★**我加的 10 条 (★8 条全过, 2 条不符 ⇒ 缺口 3★)** ★

| # | 输入 | 实测 | 我期望 | 判定 | 说明 |
|---|---|---|---|---|---|
| 5 | `("error", True, "none")` | `run_error` | `run_error` | ✅ | 矛盾输入, error 优先 ⇒ 保守报「没跑成」✔ |
| 6 | `("error", None, "announce")` | `run_error` | `run_error` | ✅ | ✔ |
| 7 | `("ok", None, "none")` | `no_delivery` | `no_delivery` | ✅ | ✔ |
| 8 | `("ok", None, "announce")` | `no_delivery` | `no_delivery` | ✅ | ✔ |
| 9 | ★**("timeout", False, "none")** ★ | ★**no_delivery** ★ | `run_error` | ★**❌** ★ | ★**★真故障被吞 (缺口 3)★** ★ |
| 10 | `("timeout", False, "announce")` | `not_delivered` | `not_delivered` | ✅ | ✔ |
| 11 | ★**("cancelled", False, "none")** ★ | ★**no_delivery** ★ | `run_error` | ★**❌** ★ | ★**★真故障被吞 (缺口 3)★** ★ |
| 12 | `("ok", False, "NONE")` | `not_delivered` | `not_delivered` | ✅ | 大小写敏感 ⇒ 按 announce 判 (保守方向, 可接受) |
| 13 | `("ok", False, "none ")` | `not_delivered` | `not_delivered` | ✅ | 未 strip ⇒ 按 announce 判 (保守方向, 可接受) |
| 14 | `("ok", False, "")` | `not_delivered` | `not_delivered` | ✅ | 空串 ⇒ `(mode or "announce")` ⇒ announce ✔ |

### ★③ 「假故障会不会被藏起来」· 可见性矩阵 (★全部 [实测], 沙盒★) ★

★**沙盒设计**: 在 `workspace/tmp/` 造一个 `mode=none` 的 job + 假的 `jobs-state.json` / `jobs.json` / `runs/*.jsonl`, ★**用 `delivery_health` 自己的 `collect()` / `collect_silent_fail()` 跑 (★真函数, 只换输入路径★) ⇒ ★**零污染真盘** ★

| 故障形态 | mode=none 下老板看得见吗 | ★**为什么 (实测依据)** ★ |
|---|---|---|
| ★**job 自己跑挂 (`status=error`)** ★ | ★**✅ 能看见** ★ | ★**口径①「这轮没跑成」计数实测 = 7 / 4 / 6 / 6 (四个 job) ⇒ 一直有数** ★ |
| ★**B 类故障** (session takeover / gateway draining / timeout / fallbacksummary) ★ | ★**✅ 能看见** ★ | ★**沙盒 E2: 连挂 5 次 ⇒ B 类 1 条告警 (★mode=none 只放宽到 24h 窗口, 不排除★)** ★ |
| ★**A 类故障** (OutboundDeliveryError / sendMessage prepare failed) ★ | ★**❌ 看不见** ★ | ★**沙盒 E1: 连挂 5 次 ⇒ A 类 0 条** ★ (★`clsA` 过滤 `(mode or "announce") != "none"`) ★ |
| ★**★认不出来的错误** (★`classify()` 的兜底分支★) ★ | ★★**❌ 完全看不见** ★★ ★ | ★★**沙盒 E3: 连挂 5 次 ⇒ A 类 0 条 / B 类 0 条 ⇒ 【一条告警都不出】★★ ★★**⇒ 与 `classify()` 自己写的「认不出来 ⇒ 按真故障处理 (宁可吵, 不可漏)」直接矛盾** ★★ ★ |
| ★**D 类** (run=ok 但 delivered=false) ★ | ★**❌ 看不见 (但语义上不算故障)** ★ | ★**沙盒 F: mode=none ⇒ D 类 0 条; 同一 job 改成 mode=announce ⇒ D 类 1 条 ⇒ 对照组证明判据本身是通的** ★ |

★**⇒ 结论 (★不许含糊★): 「mode=none 的 job 真的坏了, 老板能不能看见?」** ★
★**——「job 自己坏了」能看见 (口径①「这轮没跑成」+ B 类连挂告警, 两条独立路);「投递坏了」看不见, 但推送本来就关着, 投递坏 ≠ 老板少了东西, 语义上不算故障。** ★
★**⇒ 唯一真缺口: 「job 自己坏了但错误长得不认识」这一类 (★沙盒 E3 实测零告警★) ⇒ 这正是 `classify()` 兜底原则想抓的东西, 被 mode=none 的整条排除吃掉了。** ★
★**⇒ 该排除是 2026-11-11 10:3x 引入的既有行为, ★**不是 ISS-261 引入的** ★ ⇒ ★**ISS-261 无责, 但 ISS-272 的复核结论里必须写明它存在** ★

### ★④ 追溯套用「当前」mode (★[实测] 现象 + [推算] 后果★) ★
- ★**[实测]** run 记录里 ★**`delivery.mode` 字段 3796/3796 全缺** ⇒ ★**按轮还原「当时那个 job 是不是开着推送」在数据上做不到** ★
- ★**[实测]** `collect()` 把 ★**jobs.json 里的【当前】mode 套到【全部 12 轮历史】上** ★ ⇒ ★**同一份 run 记录, 只改 mode 参数, 计数就整片翻转 (实验 A)★** ★
- ★**[实测]** 「ARS45 状态速报」: mode=announce ⇒ ★**没送到 12 / 本来就不投 0** ★; mode=none ⇒ ★**没送到 0 / 本来就不投 12** ★ ⇒ ★**同一批 run, 两个数** ★
- ★**[实测]** 「ARS45 10 分钟进展播报」在 ★**announce 时代 (11-05 12:36 ~ 11-11 10:21, 该时段有 216 轮真送到作证)** 有 ★**10 轮 `status=ok` + `delivered=false` = 真投递失败** ★ ⇒ ★**新判据把这 10 轮追溯洗成「本来就不投」** ★
- ★**[实测]** ★**但这 10 轮不在当前 12 轮窗口内** (★窗口 = 11-17 00:30 ~ 04:36, 全在 mode=none 时代★) ⇒ ★**今天不影响输出** ★
- ★**[推算]** ★**老板一旦把推送改回 announce ⇒ 同一批 run 记录立刻变成「没送到 12」⇒ 假故障立刻复现** ★

### ★⑤ 口径① 现在的鉴别力 (★[实测]★) ★
- ★**[实测]** 盘上 ★**9 个 cron job 的 `delivery.mode` 全是 `none`** ★ ⇒ ★**口径① 的「没送到」这一列结构上恒为 0** ⇒ ★**口径① 现在只能区分「这轮没跑成」和「本来就不投」两列; 投递真故障它已经报不出来了 (★因为盘上确实一个推送都没开★)** ★
- ★**[实测]** 口径② 今日失败队列 = ★**0 条** ★ ⇒ ★**没有任何投递侧真故障被漏掉的证据** ★

### ★⑥ 数据漂移提示 (★[实测]★, 免得 main 对不上数★) ★
- ★**[实测]** main 交卷单写「10 分钟进展播报 → 没送到 4 · 这轮没跑成 8」; ★**我同一时刻实测 = 没送到 5 · 这轮没跑成 7** ★
- ★**[实测]** main 写「继续执行后继计划 → 没送到 7 · 这轮没跑成 5」; ★**我实测 = 没送到 6 · 这轮没跑成 6** ★
- ★**[推算]** ★**run 记录是活的, 每隔十几分钟就多一轮 ⇒ 两边的数必然对不上, ★**这不是判据不一致, 是数据在动** ★ ⇒ ★**main 复核时不必追这个数** ★

---

## B4 · 接口取值声明 (interface_claims)

★**本单不声明任何接口取值 (★内部活, 不涉及芯片脚表 / 网表 / BOM / 时序 / 供电时序 ★) ⇒ ★**B4 无接口取值** ★
★**⇒ 本单对项目的唯一「取值贡献」是【投递口径判据的台账值】, 已登记为 interface_claim 一条 (★`iss272_delivery_truth_md5_20261117`★) ⇒ ★**给 main 一个可被自动检出的锚点** ★**

★**★口径声明 (★口径类, 不是脚表类★)** ★
| 项 | 值 | ★**依据**★ |
|---|---|---|
| ★**ISS-261 改判后 `state/delivery_truth.py` md5** ★ | ★**`8dad8b39d873b3d930acb1c076e240cb`** ★ | ★**[实测]** 本单起始实测 ★ |
| ★**本单加压后 `state/delivery_truth.py` md5** ★ | ★**`a4cb793c41f33ee1681d46023c2ac2a7`** ★ | ★**[实测]** 本单收尾实测 ★ |
| ★**修前 (ISS-261 备份) md5** ★ | ★**`00ff09721fad2b1fa8621d5af5573f7f`** ★ | ★**[实测]** `state/.bak_delivery_truth_20261117_0435_iss261.py` ★ |
| ★**判据 `classify_run` 函数体** ★ | ★**本单与 main 的 ISS-261 版逐字节相同 (1253 B)** ★ | ★**[实测]** 函数体抽取后 `==` 比较 = True ★ |

★**⇒ ★★**main 落 `verified` 时请把 ISS-261 的 md5 台账更新为「判据版 `8dad8b39…` + selftest 加压版 `a4cb793c…`」, 否则 issue_log 里那个 md5 会过期★** ★

---

## B5 · 未决项与卡点 (★需要谁回答什么★)

★**★以下 3 条我【不代拍】, 请 main 裁决★。★**每条都给了「我建议改成什么 + 为什么」, 但 ★**判据我一个字没改** ★ (★任务书明令: 判据除非发现真错 ⇒ 写进交卷单由 main 拍★) ★

### ★缺口 1 · 端到端 announce 分支零覆盖 (★★已由本单补上, 只需 main 知情★) ★
- ★**现象 [实测]**: 变异 M6 ⇒ 把端到端 announce 分支的期望改错, `--selftest` 仍 rc=0 ⇒ ★**该分支在当前盘上一次都没执行过 (盘上 9 个 job 的 mode 全是 none)** ★
- ★**★本单已处理**: 加了【合成 run 记录】用例组 (★只加用例, `classify_run` 判据逐字节未动★) ⇒ ★**断言 31 → 44, rc=0; M2 (announce 真投递故障被吞) 现在由 SYN 用例抓到** ★
- ★**要 main 做的**: ★**无 (仅知情)** ★ —— 但 ★**若 main 认为「合成用例不如真数据」, 另一条路是等盘上真出现 announce job 时再补真数据端到端用例★** ★

### ★★缺口 2 · 追溯套用「当前」mode (★★建议 main 拍: 补 mode 水位线★) ★★ ★
- ★**现象 [实测]**: `collect()` 用 jobs.json 的【当前】mode 套到全部 12 轮历史; run 记录里 `delivery.mode` 3796/3796 全缺 ⇒ ★**无法按轮还原当时的 mode** ★
- ★**后果 ① [实测]**: 「10 分钟进展播报」announce 时代的 ★**10 轮真投递失败被追溯洗成「本来就不投」** ★ (★今天不在窗口内, 不影响输出★)
- ★**后果 ② [推算]**: ★**老板一旦改回 announce, 同一批 run 记录立刻变「没送到 12」⇒ 假故障复现 (实验 A 实测同一批数据两个数)** ★
- ★**★我建议改成什么★**: ★**在 `delivery_truth.py` 里记一条【mode 变更水位线】—— 即每个 job 的 mode 从「announce 变 none」的时刻 —— 然后只对水位线【之后】的 run 套用 mode=none; 水位线【之前】的 run 一律按 announce 判 (★宁可多报, 不可漏报★)** ★
- ★**为什么**: ★**① 它同时修掉两个方向 (追溯洗白 + 改回 announce 立刻假报); ② 它不需要改 OpenClaw cron 侧 (run 记录补字段要动上游, 周期长得多); ③ 水位线可以由 `delivery_health.py` 已经在维护的 `state/.delivery_health_alerted.json` 旁挂一个 `mode_changed_at` 台账** ★
- ★**代价 [推算]**: ★**水位线拿不到历史真值时 (★第一次改 mode 时没人记★) ⇒ 只能对「有 delivered=True 佐证」的那段判 announce, 其余保守按 announce 判 (★宁可吵不可漏★)** ★
- ★**要 main 回答**: ★**「补 mode 水位线」这条要不要开新单做? (★还是并进别的单?★) ★**

### ★缺口 3 · `status` 判据只认精确 `"error"` (★★建议 main 拍: 改判据★) ★
- ★**现象 [实测]**: `("timeout", False, "none")` ⇒ ★**`no_delivery`** ★; `("cancelled", False, "none")` ⇒ ★**`no_delivery`** ★ ⇒ ★**真故障被吞成「本来就不投」** ★
- ★**当前风险等级 [实测]**: ★**盘上 run 记录 `status` 取值全集 = {ok: 1669, error: 2127}, 非 ok/error 的 finished run = 0** ⇒ ★**今天不触发** ★
- ★**★我建议改成什么★**: ★**把 `status == "error"` 改成「status 不在成功集合里 ⇒ 算 run_error」—— 即 `if status not in ("ok", "success", "completed", None): return "run_error"`; ★**并且把判据顺序里的 mode=none 那一支放在 run_error 之后 (★已经是了★)** ★
- ★**为什么**: ★**① 现在的判据是「白名单一个字符串」, 而 OpenClaw 将来加任何失败态名都会漏; ② 改成「黑名单成功态」是 fail-closed 方向 (★宁可吵, 不可漏★), 与本项目铁律一致; ③ 改完之后 `status=timeout + mode=none` ⇒ run_error ⇒ **真故障露出来** ★
- ★**代价 [推算]**: ★**若 OpenClaw 存在别的「非失败但非 ok」的状态名 (★比如 `skipped` / `cancelled-by-user`★), 改完会把它们误报成 run_error ⇒ ★**改之前必须先确认上游的状态取值全集 (★目前只有 ok / error 两个, [实测]★)** ★
- ★**要 main 回答**: ★**「改白名单为黑名单」这条要不要做 (★在 ISS-261 落 verified 之后另开单, 还是直接并进本单★)? ★**

### ★缺口 4 · A 类排除 mode=none 时把「认不出来的错误」也排除了 (★★建议 main 拍★) ★
- ★**现象 [实测]**: 沙盒 E3 ⇒ ★**mode=none 的 job 撞上一个未知错误 (★`classify()` 归 A 类★) ⇒ A 类 0 条 / B 类 0 条 ⇒ 一条告警都不出** ★
- ★**矛盾点 [实测]**: ★**`classify()` 的兜底注释写着「认不出来 ⇒ 按真故障处理 (宁可吵, 不可漏)」, 而 `clsA` 的 mode=none 排除把这句兜底整个吃掉了** ★
- ★**★我建议改成什么★**: ★**A 类排除 mode=none 时, 只排除「【投递通道类】错误」, 不排除「认不出来的错误」—— 即把 `classify()` 的返回值从 "A"/"B" 两分改成三分 ("A"/"B"/"U"=unknown), 让 unknown 不受 mode 过滤** ★
- ★**为什么**: ★**① 它是唯一一条「真故障零告警」的路; ② 语义上说得通: 推送关着 ⇒ 投递通道坏了跟我无关, 但「job 自己出了个没人认识的新错误」跟推送开没开无关; ③ 改动只在 `delivery_health.py` 里 ⇒ ★**★那不是本单的地界 ⇒ 本单只报不改, 交 main 拍** ★ ★
- ★**要 main 回答**: ★**「A 类三分 (A/B/U)」这条要不要开单做? ★**

---

## B6 · 自证复现命令

★**★全部本机实跑, 输出 rc 见本单 B2 / B3★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 反向用例 (★main 版 31 条 ⇒ 本单加压后 44 条, rc 都必须 = 0★)
python3 state/delivery_truth.py --selftest; echo "RC=$?"

# ② 修后读数 (★口径① 四行★)
python3 state/delivery_health.py | head -6

# ③ ★自己 swap 修前/修后做 diff (★用盘上备份, 不用任何人的 /tmp★)★
#    ★★沙盒建议用 workspace/tmp (394G 可用), 别用 /tmp (配额紧张)★★
S=/home/yuewuya/.openclaw/workspace/tmp/iss272_review; mkdir -p $S
cp state/delivery_truth.py $S/dt_new.py
cp state/.bak_delivery_truth_20261117_0435_iss261.py state/delivery_truth.py
python3 state/delivery_health.py > $S/dh_before.txt 2>&1
cp $S/dt_new.py state/delivery_truth.py
python3 state/delivery_health.py > $S/dh_after.txt 2>&1
diff $S/dh_before.txt $S/dh_after.txt
md5sum state/delivery_truth.py   # ★★必须回到 a4cb793c41f33ee1681d46023c2ac2a7★★

# ④ 加压用例 (★自己造输入, 不许只跑现成的 selftest★)
python3 - <<'EOF'
import sys; sys.path.insert(0, 'state')
from delivery_truth import classify_run
for args in [("error", False, "none"), ("ok", True, "none"), ("ok", False, None), ("ok", False, "announce")]:
    print(args, "->", classify_run(*args))
EOF

# ⑤ 判据未被改动 (★本单只许加 selftest 用例★)
python3 - <<'EOF'
import re
def grab(p):
    t=open(p,encoding="utf-8").read()
    return re.search(r"def classify_run\(.*?\n(?=\ndef )", t, re.S).group(0)
print("判据逐字节相同 =", grab("/home/yuewuya/.openclaw/workspace/tmp/iss272_review/delivery_truth.pre_iss272_selftest.py") == grab("state/delivery_truth.py"))
EOF

# ⑥ 门禁链
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py && python3 state/stage_gate.py
```

★**★门禁链实测 rc (★2026-11-17 05:3x~05:5x 本机实跑, ★分片落完后重跑★)★**: ★**`merge.py` rc=0** (★产出 457 | 阻塞 43 (高危 33) | 未闭合需求 262 | 冲突 0 | 健康度 red★) ★
· ★**`gate_check.py` rc=0** ⇒ ★**【Q1 交付齐备率】18/18 个必填验收块齐全** (★sw-lead 6/6 缺: 无, ★**计分单 = 本单**★) · ★**Q2 证据分级率 3/3** ★ · ★**Q3 接口声明率 786 条** ★ · ★**Q6 硬件真源闸 ✅ 通过 (rc=0)** ★
· ★**`issue_check.py` rc=0** ⇒ ★**「✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)」** ★
· ★**`stage_gate.py` rc=1** ⇒ ★**★既有的 G1 缺口 (PCB unconnected=45, ISS-181), 与本单无关, 本单未新增任何缺口★★** ★

★**★零副作用实测 (★本机 md5 现场跑★)★** ★
| 件 | 实测 md5 | 判定 |
|---|---|---|
| ★**板 `HW/PCB/demo_mainboard.kicad_pcb`** ★ | `611b869e13518c3c023fb178f91a0075` | ★**与 main 交卷单记的值逐字相同 ⇒ 零写板** ★ |
| ★**网表 `HW/netlist_v1.csv`** ★ | `e06c1dd633566aa44732762c2ff99d1c` | ★**逐字相同 ⇒ 零落表** ★ |
| ★**脚表 `HW/netlist_v1_pins.csv`** ★ | `287e7861a0d1007748d92d9fbecdd490` | ★**逐字相同** ★ |
| ★**BOM `HW/BOM_v1.csv`** ★ | `94642d07a69e8d60dd2af57f69b93607` | ★**逐字相同** ★ |
| ★**`.kicad_pro`** ★ | `3e504d2be83152e337949723e909be1b` | ★**逐字相同** ★ |
| ★**`state/delivery_health.py`** ★ | mtime `11-11 10:36:24` | ★**本单全程未写 ⇒ A/B/D 三类判据一字未动** ★ |
| ★**`state/issue_log.yaml`** ★ | mtime `11-17 05:28:35` | ★**早于本单开工 ⇒ 本单未碰 ⇒ 不自签 verified** ★ |
| ★**`state/delivery_truth.py`** ★ | `a4cb793c41f33ee1681d46023c2ac2a7` | ★**本单加压版 (★判据逐字节未改★)** ★ |

★**边界自证**: ★**零外发 · 零采购 · 零写板 · 零落表 · 零改网表/脚表/BOM · 零改 PROJECT_TRACKER.md §0 · 未改 `state/delivery_health.py` (★A/B/D 三类判据一字未动★) · 未改 `state/issue_log.yaml` (★不自签 verified★) · 判据 `classify_run` 逐字节未改 · 只写 `state/fragments/sw.yaml` (走 `frag_write.py --agent sw-lead`) · 未写任何别人的分片 · 未替老板拍板** ★
