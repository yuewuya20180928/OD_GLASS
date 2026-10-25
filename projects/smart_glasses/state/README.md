# STATE 协议 — 共享状态源 (老板 2026-10-25 指示)

> 老板原话: "总工和3个子模块总工之间可以通过共享 **STATE.yaml** 文件作为唯一状态源, 避免跨专业 Agent 的无效沟通冲突"

## 为什么有这套东西

星型拓扑 (三个总工之间不直接沟通) 有个天然副作用: **A 想知道 B 的进度, 只能靠问**。
问了就是一次跨 agent 往返, 而且经常变成"我催你 → 你回我 → 我再转达 → 信息失真"。

**STATE.yaml 的作用就是把"问"变成"读"**:
- 状态写在共享库里 → B 的最新进度 A 一眼就能看到, **不用发消息**
- B 需要 A 配合 → B 在自己的分片里写 `needs_from` → A 刷新 STATE 就知道自己被点了名 → **A 主动去办, 不用 B 催**
- 两个 agent 对同一个接口给了矛盾的值 → 合并器自动检出 `conflicts` → **不用等到评审会才发现**

## 目录结构

```
projects/smart_glasses/
├── STATE.yaml              ← ★ 合并产物 (机器可读状态快照), 全员只读
├── PROJECT_TRACKER.md      ← 决策理由 / 证据链 / 锁死变量 的真源 (人读)
└── state/
    ├── merge.py            ← 合并器 (v1.1, 并发安全)
    ├── frag_write.py       ← ★ 分片原子写工具 (写分片必须用它)
    ├── stress_test.py      ← ★ 并发/压力/异常输入 压测台 (沙盒副本, 不碰真数据)
    ├── test_merge.py       ← 合并器自测
    ├── test_whitebox.py    ← 多 agent 隔离/路由/并发 白盒测试
    ├── .lastgood/          ← 各分片上次成功解析的副本 (读失败自动回退)
    ├── fragments/
    │   ├── pm.yaml         ← 项目总工 (main) 独占写
    │   ├── hw.yaml         ← 硬件总工 独占写
    │   ├── sw.yaml         ← 软件总工 独占写
    │   └── mech.yaml       ← 结构总工 独占写
    └── README.md           ← 本文件
```

## ⚠️ 单一真源怎么解释 (别混淆)

| | 职责 | 谁写 | 读者 |
|---|---|---|---|
| **`STATE.yaml`** | **当前状态快照** (机器可读): 谁做到哪、卡在哪、在等谁、接口值、冲突 | 合并器自动生成, **人不直接编辑** | 4 个 agent 全文读 |
| **`PROJECT_TRACKER.md`** | **决策与理由真源** (人读): 锁死变量、决策记录、证据链、展开分析 | **只有项目总工 (main)** | 4 个 agent 按需查 |

**关系是单向的**: `STATE.yaml` 里每一项都带 `ref` 指向 `PROJECT_TRACKER.md` 的具体章节或产出文件。
**状态变了 → STATE.yaml 和它 ref 的那份文档必须一起改**。STATE.yaml 不重复存长文正文, 只存"状态 + 指针"。

## 写权限 (硬规则)

- **每个总工只写自己那一个分片** `state/fragments/<agentId>.yaml` → 天然无并发写冲突
- **合并器是唯一写 `STATE.yaml` 的** → 原子写 (临时文件 + rename), 读到的一定是完整快照
- **`PROJECT_TRACKER.md` 只有项目总工能改** (老板 10-21 锁死规则不变)
- **锁死变量表 (§0) 只有项目总工能改** — 分片里只引用, 不复制

## ⚠️ 并发安全 (2026-10-25 压测后新增, 违反 = 数据静默消失)

压测实测: 分片用普通 `open(p,"w")` 写 (先 truncate 再写) 时, 合并器有 **99.6% 的概率读到半截**;
截断点落在合法 YAML 边界时**解析成功但数据残缺** → 整个 agent 的域**无声从快照里消失**, 合并器还打 ✅。

**所以: 写分片必须用原子写。**

```bash
# ✅ 正确 (协议强制): 用原子写工具
cd projects/smart_glasses
python3 state/frag_write.py --agent hw-lead \
    --add-need 'key=pcb_outline_confirm to=mech-lead item=PCB外形确认' \
    --add-answer 'key=q1_latency_scope to=main value=口径C' \
    --add-claim 'key=pcb_outline value=50x12mm note=待确认'

# ❌ 错误 (会造成静默丢数据): 直接 open(w) 覆盖
python3 -c "import yaml; d=yaml.safe_load(open('state/fragments/hw.yaml')); ...; yaml.safe_dump(d, open('state/fragments/hw.yaml','w'))"
```

**合并器现在能自证快照是否完整**:

| 信号 | 含义 |
|---|---|
| 退出码 **0** | 快照完整 |
| 退出码 **2** | 刷新了, 但**快照不完整** (有分片读失败) → 看 `meta.incomplete_fragments` |
| 退出码 **1** | 合并器崩了 (不该发生) |
| `meta.fragments` | 各分片的 size/sha1/mtime → 快照新鲜度可判断 |
| `state/.lastgood/` | 各分片上次成功解析的副本 → 读失败时自动回退 (宁可给旧数据, 不给"这个 agent 不存在") |

**读方铁律**: 看到 `rc=2` 或切片顶部有 "⚠️ 本次快照不完整" → **别把它当全量真相**, 重跑一次合并。

## 分片 schema

```yaml
agent: hw-lead                 # 必填, 必须等于文件名
role: 硬件总工
updated_at: "2026-10-25T01:00:00+08:00"
updated_by: hw-lead

status:
  phase: "P0-P1"
  progress_pct: 35
  health: yellow               # green | yellow | red
  summary: "一句话说清我现在到哪了"

artifacts:                     # 本域产出 (路径相对 projects/smart_glasses/)
  - path: HW/HARDWARE_BREAKDOWN.md
    kind: breakdown
    version: v1.0
    updated_at: "2026-10-25T00:22:00+08:00"
    summary: "26 个模块 + 5 项排除项"

blockers:                      # 卡在本域的
  - id: HW-B1
    desc: "ARS45 显示输出接口未确认"
    severity: high             # high | medium | low
    needs_from: [vendor, main]
    waiting_since: "2026-10-21"

needs_from:                    # ★ 我在等谁 (合并器据此生成"谁在等你"视图)
  - key: pcb_outline_confirm  # ★ 用 key, 对方用同一个 key 就能对上
    to: mech-lead
    item: "PCB 外形 50x12mm 确认 + 器件发热分布 + NTC 位置"
    since: "2026-10-25"

answers:                       # ★ 我回答了谁 (合并器据此把 needs_from 标成 answered)
  - key: pcb_outline_confirm
    to: hw-lead
    value: "50x12mm, 板宽跟 FCCSP pitch 走"
    ref: "MECH/MECH_BUDGET.md#1.3"

interface_claims:              # ★ 我对跨模块接口给出的值 (合并器据此查冲突)
  # ⚠️ value 必须是**短规范值** (用于机器比较), 补充说明写进 note (不参与比较)
  - key: pcb_outline
    value: "50x12mm"
    note: "待确认"

open_questions:                # 我提的、还没人答的 (给人看, 合并器只统计)
  - id: HW-Q1
    to: sw-lead
    text: "调试口形态 + OD 负载曲线 (定 DC-DC 瞬态与电容)"

risks:                         # 我域内的风险
  - id: R-heat
    text: "..."
    severity: high
```

## 合并器用法

```bash
cd projects/smart_glasses

# 刷新共享快照 (任何人任何时候都可以跑; 并发跑有 flock 串行化, 安全)
python3 state/merge.py                    # rc=0 完整 / rc=2 不完整 / rc=1 崩了

# 看自己的待办切片: "谁在等我 / 我欠谁 / 当前冲突"
python3 state/merge.py --for mech-lead

# 机器可读摘要 (JSON)
python3 state/merge.py --json

# 压测台 (沙盒副本, 不碰真数据) —— 改完合并器必跑
python3 state/stress_test.py
```

**合并器做的事**:
1. 读全部分片 (失败自动重试 5 次 + 读期间变更检测 + 回退 `.lastgood/`)
2. 合并 `needs_from` × `answers` → 每个需求标 `answered` / `pending` (+ `target_missing` 标记)
3. 合并 `interface_claims` → 同一 `key` 不同值 = **conflict**, 写进 `conflicts`
4. 统计 `summary` (产出数 / 阻塞数 / 未闭合需求数 / 冲突数 / 不完整分片数)
5. **原子写** `STATE.yaml` (唯一 tmp 名 + `fsync` + `os.replace`), 前面还有 `flock` 串行化

## 星型拓扑守卫 (三层, 2026-10-25 压测后加)

| 层 | 位置 | 拦什么 | 强度 |
|---|---|---|---|
| 1 | 工具层 `tools.deny: ["sessions_send"]` | 直接调 sessions_send | 硬 (Gateway 也 deny) |
| 2 | PATH shim `~/.openclaw/guards/<agentId>/openclaw` | 裸命令 `openclaw agent --agent <对方>` | 软 (绝对路径能绕) |
| 3 | **CLI 入口** `~/.npm-global/bin/openclaw` | **绝对路径调用** (原来能绕, 消息真投递) | 软 (同 OS 用户, 蓄意规避仍可绕) |

- 调用方身份: shim 注入 `OPENCLAW_CALLER_AGENT` 标记; 没有标记 = "未标识" → 跨 agent 呼叫**一律拒** (exit 126)
- 项目总工手动跨 agent 调用: `OPENCLAW_STAR_OVERRIDE=1 openclaw agent --agent X` (审计留痕 `~/.openclaw/guards/star-topology.log`)
- **只写交接单, 不私聊** —— 三个总工之间不做直接沟通 (老板 10-25 硬规则)

## 铁律 (写进 MEMORY.md)

- **要问对方的事, 先看 STATE.yaml** — 状态在里面就别发消息
- **要对方配合, 写进自己的 `needs_from` (带 key)**, 不要发消息催 → 对方刷新 STATE 就看见了
- **回答别人, 写进自己的 `answers` (用对方给的 key)**, 不要私聊回 → 所有人看同一个真相
- **接口值必须写进 `interface_claims`** → 冲突自动暴露, 不用等评审
- **不许在 STATE.yaml 里直接手改** → 会被下次合并覆盖
- **写分片必须用 `state/frag_write.py` (原子写)** → 直接 open(w) 覆盖会造成**静默丢数据** (压测实测 99.6% 概率读到半截)
- **合并器 rc=2 = 快照不完整** → 别把它当全量真相, 重跑
- **一个 agent 同时只开一个写会话** → 两个会话会互相覆盖分片 (last-writer-wins, 丢失更新)
