# ISS-261 · main (moli) 交卷单 —— 投递口径① 的 `mode=none` 归类修复 (★假故障「没送到 12」归零★)

> ★**派活人**: 项目总工 (main / moli) · ★**落账时刻**: 2026-11-17 04:5x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**本单性质**: ★**内部活 · 门禁/运维工具侧 · 判据口径订正类 (★零写板 · 零落表 · 零外发 · 零采购★)** ⇒ ★**不是老板级拍板** ★
> ★**老板 2026-11-12 02:02 政策**: 不再发信 / 全靠自己查资料 ⇒ ★**零外发** ★
> ★**为什么是 main 自己干**: ★**本单 owner = main (★三个总工名额全被 ISS-269/270/271 占着·★一 agent 一个写会话铁律★) ⇒ 无人可派 ⇒ main 自做自验** ★

---

## ① B1 · 口径句 (★一句话★)

★**`state/delivery_truth.py` 的口径① 在分类单轮 run 时, ★**没有先看这个 job 的 `delivery.mode`** ⇒ 老板 2026-11-04 09:5x 关掉的推送 (mode=none) 照样被算成「没送到」⇒ 输出「★送到 0 · 没送到 12 · 本来就不投 0★」= ★**纯假故障 (狼来了)★** ⇒ ★**本单把 mode=none 的 `delivered=false` 改判成「本来就不投」, 并给它配了反向用例** ★

---

## ② B2 · 病灶 (★main 2026-11-17 04:2x~04:3x 本机实跑, 不是抄任何交卷报告★)

### ★① 修前的真实输出 (★`python3 state/delivery_health.py` 原文★)

```
★投递口径①: ARS45 10 分钟进展播报 + 落盘自检放行 (自研主板) | 最近 12 轮 → ★送到 0 · 没送到 4 · ★这轮没跑成 8 · 本来就不投 0
★投递口径①: ARS45 状态速报 (每小时推微信, 老板手机上看状态) | 最近 12 轮 → ★送到 0 · 没送到 12 · ★这轮没跑成 0 · 本来就不投 0
★投递口径①: ARS45 项目每日巡检 | 最近 12 轮 → ★送到 0 · 没送到 8 · ★这轮没跑成 4 · 本来就不投 0
★投递口径①: ARS45 继续执行后继计划 | 最近 12 轮 → ★送到 0 · 没送到 7 · ★这轮没跑成 5 · 本来就不投 0
```

★**⇒ 「本来就不投」这一列结构上恒为 0 (★4 个 job 全是 0★) ⇒ ★**这不是数据问题, 是判据问题** ★

### ★② 根因 (★`state/delivery_truth.py:94-121` 修前原文★)

```python
if status == "error":
    verdict = "run_error"
elif delivered is True:
    verdict = "delivered"
elif delivered is False:
    verdict = "not_delivered"      # ★★这条先命中★★
else:
    verdict = "no_delivery"        # ★★于是这一支永远走不到★★
```

★**实测事实 (★`~/.openclaw/cron/jobs.json` + `cron/runs/*.jsonl`★)**: ★**这 4 个 job 的 `delivery.mode` 全是 `none`** (★老板 2026-11-04 09:5x 指示关掉微信推送★)
⇒ ★**OpenClaw 在 mode=none 时照样把 `delivery.delivered` 写成 `false`** ⇒ ★**`delivered is False` 这一支先命中 ⇒ 全部落进「没送到」** ★
★**⇒ 那个 `else: no_delivery` 分支 (★注释就写着「mode=none / not-requested ⇒ 本来就不投」★) 是死代码, 永远走不到** ★

### ★③ 自相矛盾的旁证 (★为什么这不是「本来就该这样」★)

★**同一张输出里, A 类 / B 类 / D 类 【都已经有 mode=none 的排除逻辑】** ⇒
- `state/delivery_health.py:181` ★**D 类**: `if (d.get("mode") or "announce") == "none": continue` (★2026-11-10 11:3x 加★)
- `state/delivery_health.py:272` ★**A 类**: `and (b.get("mode") or "announce") != "none"`
- `state/delivery_health.py:279` ★**B 类**: `b_impact = [b for b in clsB if b.get("mode") != "none"]`

★**⇒ 只有口径①漏了 ⇒ 两套口径在同一张输出里互相打脸** ★
★**⇒ 本单修完, 口径① 与 A/B/D 三类的口径第一次一致** ★

---

## ③ B3 · 改法 (★只动分类, 别的一个字没动★)

★**① 把分类抽成纯函数 `classify_run(status, delivered, mode)`** (★可自测, 不依赖盘上真数据★) ★
★**② 分类顺序 (★顺序就是判据★)**:
| # | 条件 | 结论 | 理由 |
|---|---|---|---|
| ① | `status == 'error'` | `run_error` | ★**job 自己失败跟投递模式无关** ⇒ mode=none 也照样算「这轮没跑成」 ★ |
| ② | `delivered is True` | `delivered` | ★**真送到了老板手上 ⇒ 最高优先级, mode 无关** ★ |
| ③ | ★**`mode == 'none'`**★ | `no_delivery` | ★**★ISS-261 的修点★ · 推送本来就没开 ⇒ `delivered=false` 是预期行为 ⇒ 不算故障 ★** ★ |
| ④ | `delivered is False` | `not_delivered` | ★**跑了但没送到 ⇒ 真故障** ★ |
| ⑤ | 其余 (delivered 缺字段) | `no_delivery` | 老行为, 保留 |

★**③ `runs_view(job_id, n, mode=None)` 加 mode 形参 + `collect()` 把 `d.get("mode")` 传进去** ★
★**④ 新增 `--selftest`** (★纯函数用例 + 端到端用例★) ★
★**⑤ 没动的**: ★**`delivery_health.py` 一个字节没改** (★A/B/D 三类判据原封不动★) · ★**任何告警阈值一个字节没改** ★ · ★**真源 (`cron/runs/*.jsonl`) 只读不写** ★

---

## ④ B4 · 验收 (★本机实跑, 原文 rc★)

### ★① 反向用例 (★ISS-261 登记时点名要的那条★) ★

```
$ python3 state/delivery_truth.py --selftest
════════ 投递口径① selftest ════════
  纯函数用例: 7 条
  端到端用例: 4 个 job
✅ 全过 (31 条断言)
SELFTEST_RC=0
```

★**用例清单 (★7 纯函数 + 4 job × 6 端到端 = 31 断言★)**:
| 用例 | 输入 | 期望 | 作用 |
|---|---|---|---|
| C1 | mode=none + delivered=false | `no_delivery` | ★**★反向用例本体★ · 「没送到」必须挪到「本来就不投」★** ★ |
| C2 | mode=announce + delivered=false | `not_delivered` | ★**老行为逐字不变** ★ |
| C3 | mode=announce + delivered=true | `delivered` | 真送到最高优先级 |
| C4 | mode=none + delivered=true | `delivered` | ★**mode 不许压掉「真送到」** ★ |
| C5 | mode=none + status=error | `run_error` | ★**job 自己失败跟投递模式无关** ★ |
| C6 | mode=announce + delivered 缺字段 | `no_delivery` | 老行为保留 |
| C7 | mode 缺省 (None) | 按 announce 判 | ★**老调用方兼容** ★ |
| E2E × 4 | ★**盘上真 run 记录**★ | mode=none ⇒ `not_delivered==0` 且 `no_delivery==非 error 轮数`; mode≠none ⇒ `not_delivered` 与逐轮期望一致; 四个计数与逐轮 verdict 逐项自洽 | ★**端到端, 不是只测纯函数** ★ |

### ★② 修后真实输出 (★同一份 run 记录★) ★

```
★投递口径①: ARS45 10 分钟进展播报 + 落盘自检放行 (自研主板) | 最近 12 轮 → ★送到 0 · 没送到 0 · ★这轮没跑成 8 · 本来就不投 4
★投递口径①: ARS45 状态速报 (每小时推微信, 老板手机上看状态) | 最近 12 轮 → ★送到 0 · 没送到 0 · ★这轮没跑成 0 · 本来就不投 12
★投递口径①: ARS45 项目每日巡检 | 最近 12 轮 → ★送到 0 · 没送到 0 · ★这轮没跑成 4 · 本来就不投 8
★投递口径①: ARS45 继续执行后继计划 | 最近 12 轮 → ★送到 0 · 没送到 0 · ★这轮没跑成 5 · 本来就不投 7
```

★**⇒ 「状态速报」那一行: 没送到 12 → 0, 本来就不投 0 → 12 (★这正是 ISS-261 登记时写的那句「看着像推送挂了的假象」消失★)** ★

### ★③ 隔离性自证 (★同一份数据, 修前修后各跑一次 `delivery_health.py`, 逐行 diff★) ★

```
=== diff (before → after) ===
2,5c2,5
< ...10 分钟进展播报... → ★送到 0 · 没送到 4 · ★这轮没跑成 8 · 本来就不投 0
< ...状态速报...       → ★送到 0 · 没送到 12 · ★这轮没跑成 0 · 本来就不投 0
< ...项目每日巡检...   → ★送到 0 · 没送到 8 · ★这轮没跑成 4 · 本来就不投 0
< ...继续执行后继计划...→ ★送到 0 · 没送到 7 · ★这轮没跑成 5 · 本来就不投 0
---
> ...10 分钟进展播报... → ★送到 0 · 没送到 0 · ★这轮没跑成 8 · 本来就不投 4
> ...状态速报...       → ★送到 0 · 没送到 0 · ★这轮没跑成 0 · 本来就不投 12
> ...项目每日巡检...   → ★送到 0 · 没送到 0 · ★这轮没跑成 4 · 本来就不投 8
> ...继续执行后继计划...→ ★送到 0 · 没送到 0 · ★这轮没跑成 5 · 本来就不投 7
```

★**⇒ 只有 4 行口径① 变了; A 类 / B 类 / D 类 / 口径② / 结论行 逐字节不变 ⇒ ★**判据改动没有外溢** ★**

### ★④ H-1 台账 ★

| 项 | 值 |
|---|---|
| ★**改动前 md5** ★ | `00ff09721fad2b1fa8621d5af5573f7f` |
| ★**改动后 md5** ★ | ★**`8dad8b39d873b3d930acb1c076e240cb`** ★ |
| ★**备份** ★ | `state/.bak_delivery_truth_20261117_0435_iss261.py` (★md5 与改前逐字节相同★) |
| ★**反向用例** ★ | `python3 state/delivery_truth.py --selftest` ⇒ rc=0 · 31 断言 |
| ★**台账位置** ★ | ★**脚本自身 docstring 的「H-1 台账 · ISS-261」段 + 本交卷单 + `state/issue_log.yaml` ISS-261 note (★三处互指★)** ★ |
| ★**是否在受保护脚本台账里** ★ | ★**否 (★`delivery_truth.py` 不在任何受保护 md5 台账中 ⇒ 无外部台账需连带重基线★)** ★ |

### ★⑤ 零副作用复核 (★本机实跑 md5★) ★

★**受保护 5 件逐字节未变**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**零写板 · 零落表成立** ★
★**`state/delivery_health.py` md5 逐字节未变** (★A/B/D 三类判据一个字没动★) ★
★**`python3 -m py_compile state/delivery_truth.py` ⇒ compile OK** ★

---

## ⑤ B5 · 未决 / 给下一个人的 (★不代拍★)

★**① 本单只落 `fixed`, 不落 `verified`** ⇒ ★**按 `state/issue_check.py` 的验证分离规则 (C3): `verify_by` 不得等于 `owner` ⇒ 本单 owner = main ⇒ main 不能自签 verified** ★
★**⇒ 已新开 ISS-272 (sw-lead · 独立复核本单的口径①改判)** ⇒ ★**复核人 = sw-lead (★与 owner 分离★) ⇒ 复核通过后才允许落 verified** ★
★**② sw-lead 名额被 ISS-270 占着** ⇒ ★**ISS-272 在队列里排队, 等名额空出来再派 (★不抢跑★)** ★
★**③ 本单没改任何告警阈值** ⇒ ★**如果老板要「mode=none 的 job 完全不进投递口径①」(★更彻底★), 那是另一个口径决定, 不在本单范围** ★

---

## ⑥ B6 · 自证复现命令 (★逐条可跑★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 反向用例 (★31 断言 rc=0★)
python3 state/delivery_truth.py --selftest; echo "RC=$?"

# ② 修后真实读数 (★口径① 四行★)
python3 state/delivery_health.py | head -6

# ③ 隔离性 (★修前修后 diff 只该有 4 行口径①★)
cp state/delivery_truth.py /tmp/dt_new.py
cp state/.bak_delivery_truth_20261117_0435_iss261.py state/delivery_truth.py
python3 state/delivery_health.py > /tmp/dh_before.txt 2>&1
cp /tmp/dt_new.py state/delivery_truth.py
python3 state/delivery_health.py > /tmp/dh_after.txt 2>&1
diff /tmp/dh_before.txt /tmp/dh_after.txt

# ④ 零副作用 (★板面 5 件 md5★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv

# ⑤ 门禁链 (★本单自己跑过的★)
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py && python3 state/stage_gate.py
```

★**边界自证**: ★**零外发 · 零采购 · 零写板 · 零落表 · 零改网表/脚表/BOM · 零改任何告警阈值 · A/B/D 三类判据零改动 · 不写别人的分片 · 不改 PROJECT_TRACKER.md §0 · 不替老板拍板 · 不自签 verified** ★
