---
name: state-protocol
description: "ARS45 智能眼镜项目的共享状态源 (STATE.yaml) 协议。当需要读写项目状态、登记需求与回答、声明跨模块接口值、或刷新/查看他人状态时使用。也用于在动笔写任何项目产出之前先确认当前状态。"
tags: [domain-specific, project-protocol, multi-agent, state]
version: 1.0.0
---

# STATE 协议 — 共享状态源

> 老板 2026-10-25 指示: "总工和3个子模块总工之间可以通过共享 STATE.yaml 文件作为唯一状态源, 避免跨专业 Agent 的无效沟通冲突"

## 核心用法 (3 条, 记住就够)

```bash
cd projects/smart_glasses

# 1. 刷新共享快照 (纯函数, 无锁, 任何时候都能跑)
python3 state/merge.py

# 2. 看自己的切片: 谁在等我 / 我欠谁 / 当前冲突
python3 state/merge.py --for <你的agentId>

# 3. 机器可读
python3 state/merge.py --json
```

**动笔前先跑第 2 步**。你要的答案多半已经在 STATE.yaml 里, **不用发消息问**。

## 写规则

| 你要做的 | 写到哪 | 怎么写 |
|---|---|---|
| 更新自己的进度/状态/产出 | `state/fragments/<你的id>.yaml` 的 `status` / `artifacts` | **用 `state/frag_write.py` 原子写** (见下) |
| 你需要别人配合 | 自己的分片 → `needs_from` | **必须带 `key`** (唯一标识) + `to` + `item` |
| 你回答了别人 | 自己的分片 → `answers` | **用对方给的 `key`** + `value` + `ref` |
| 你对跨模块接口给的值 | 自己的分片 → `interface_claims` | `value` 写**短规范值**, 说明写 `note` |
| 你卡住了 | 自己的分片 → `blockers` | `severity`: high/medium/low + `needs_from` |

**绝不直接编辑 `STATE.yaml`** —— 它是合并产物, 会被下次合并覆盖。

## ⚠️ 写分片必须原子写 (2026-10-25 压测实测, 不是理论)

**普通 `open(path,"w")` 覆盖 = 会静默丢数据。** 实测: 分片写到一半被合并器读到 →
- 99.6% 的概率读到 0 字节 / 半截 → 整个 agent 的域**无声从快照里消失**, 合并器还打 ✅
- 截断点落在合法 YAML 边界时**解析成功但数据残缺** → 同样无声丢

**正确写法 (协议强制)**:

```bash
cd projects/smart_glasses
python3 state/frag_write.py --agent <你的id> \
    --add-need 'key=xxx to=yyy item=zzz since=2026-10-25' \
    --add-answer 'key=xxx to=www value=答案 ref=文件.md#节' \
    --add-claim 'key=接口名 value=50x12mm note=待确认' \
    --add-artifact 'path=HW/xxx.md kind=breakdown summary=一句话' \
    --status 'phase=P1 progress_pct=30 health=yellow summary=一句话'
python3 state/merge.py
```

或用 Python API:

```python
import sys; sys.path.insert(0, "state")
from frag_write import update_fragment
update_fragment("hw-lead", lambda d: d.setdefault("needs_from", []).append({
    "key": "pcb_outline_confirm", "to": "mech-lead", "item": "PCB 外形确认", "since": "2026-10-25"}))
```

**合并器退出码**: `0` = 快照完整 / `2` = 刷新了但**不完整** (有分片读失败, 已回退旧快照) / `1` = 崩了。
看到 `2` → **重跑一次** `merge.py`, 别拿这份快照当全量真相。

## 三个必须懂的机制

### 1. needs_from × answers 按 key 配对
- 你写 `needs_from: [{key: "pcb_outline_confirm", to: "mech-lead", ...}]`
- mech-lead 写 `answers: [{key: "pcb_outline_confirm", to: "hw-lead", value: "..."}]`
- 合并后你的需求自动变 `answered`
- **只有被问的那个 agent 的回答才能闭合你的需求** (别人代答不算, 只会被记成 `foreign_answers`)

### 2. interface_claims 自动查冲突
- 两个 agent 对同一个 `key` 给了**不同规范值** → 合并器自动报 `conflicts`
- 这就是"避免无效沟通冲突"的落点: 不用等到评审会才发现两个人理解不一样
- `value` 必须是**短规范值** (如 `50x12mm` / `4-6层` / `38-40C(红线43C)`)
  - 写成散文 (如 "皮肤侧 ≤38-40°C, 红线 43°C (ISO 13732-1)") → 会被标 `lint` 警告, **不参与比较** (因为没法可靠比较)
  - 正确写法: `value: "38-40C(红线43C)"` + `note: "ISO 13732-1; 贴皮肤镜腿可持续上限 0.15-0.2W"`

### 3. answers.key 会被校验
- 你的 `answers.key` 如果**没有任何 `needs_from` 引用** → 合并器报 `lint` (多半是 key 写错了)
- **为什么重要**: key 写错 → 需求**静默不闭合**, 对方永远等不到答复, 且没有任何报错

### 4. ⚠️ 同一个 key 会被多人复用 (10-25 质量门实测)
- 现象: `q1_latency_scope` 这类**同一个问题**, main 和 sw-lead **各自**登记了一条 needs (同 key, 不同发起方) → 这是合法用法
- **配对靠 `to` 字段区分方向**: 需求 (owner, key, to) 只能被**`to` 指定的那个 agent** 的答复闭合
- **风险**: 答复的 `to` 写错 → 变成"自己答自己" → 需求被假闭合
- **检测**: `python3 state/gate_check.py` 会报「自闭合 (自己答自己)」和「key 双向重用」两项, 看到就改 `to`

### 5. needs_from 的 waiting_on / due (10-25 新增)
- `waiting_on`: `agent` (默认, 等另一个总工) | `boss` | `vendor` | `jbd` (等外部)
- `due: "YYYY-MM-DD"` → 合并器自动算逾期
- **为什么**: 不标的话, "等老板"和"对方没答"混在一起 → 项目总会重复催办已经在等外部的事

### 6. STATE.yaml vs PROJECT_TRACKER.md 的分工
| | 放什么 | 谁写 |
|---|---|---|
| `STATE.yaml` | **当前状态快照** (机器可读): 做到哪、卡在哪、在等谁、接口值、冲突 | 合并器生成, 不手改 |
| `PROJECT_TRACKER.md` | **决策与理由真源** (人读): 锁死变量、决策记录、证据链、展开分析 | **只有项目总工 (main)** |

`STATE.yaml` 每项都带 `ref` 指向 tracker 或产出文件。**状态变了 → 两边一起改**。

## 铁律

1. **要问的事, 先看 STATE.yaml** —— 状态在里面就别发消息
2. **要别人配合, 写 `needs_from` (带 key)**, 不要发消息催 → 对方刷新 STATE 就看见了
3. **回答别人, 写 `answers` (用对方的 key)**, 不要私聊回 → 所有人看同一个真相
4. **接口值必须写进 `interface_claims`** → 冲突自动暴露
5. **不许手改 `STATE.yaml`**
6. **锁死变量表只有项目总工能改** —— 分片里只引用, 不复制

## 排错

```bash
python3 state/test_merge.py      # 合并器自测
python3 state/gate_check.py      # ★ 质量门看板 (交付齐备率/证据分级/接口声明/需求闭环/硬指标覆盖)
python3 state/test_whitebox.py   # 多 agent 隔离/路由/并发 白盒测试
python3 state/stress_test.py     # ★ 并发/压力/异常输入 压测台 (沙盒副本, 不碰真数据)
```
- 冲突检测失效 → 看 `state/test_merge.py` 的 `[1] [2]`
- 需求闭合了但你不希望 → 检查是不是**别人**用同一个 key 回答了 (会被记到 `foreign_answers`)
- lint 报警 → 把 `value` 改成短规范值, 说明挪到 `note`
- 快照少了某个 agent → 合并器 stderr 会说 "跳过 xxx.yaml"; 分片多半正被并发写 → **重跑 merge.py**; 修法是改用 `frag_write.py` 原子写
- 合并器 rc=1 崩了 → 看 traceback; 现在合并器已能兜住畸形输入, 崩了说明有新 bug, 立刻报项目总工

## ★ 星型拓扑: 不要直接联系别的总工 (老板 10-25 硬规则)

三个总工之间**不做直接沟通**, 走 STATE.yaml + 交接单。实测证据: 绝对路径调用 CLI
**真的能把消息投进对方会话** (已实证 3 次), 现在守卫已下沉到 CLI 入口拦掉, 但别去试。

- 要别的总工配合 → 写 `needs_from` (带 key), 对方刷新 STATE 就看见了
- 要转达给项目总工 → 写交接单到 `projects/smart_glasses/HANDOFF/`
- **`sessions_send` 没有这个工具; `openclaw agent --agent <别人>` 会被守卫拦 (exit 126)** —— 两者都不该用
