# 4-Agent 协同开发体系 —— 职责 / 边界 / 配置

> 老板 2026-10-25 决定: 项目改为 **4-Agent 职能制** —— 1 个项目总工 + 3 个子模块总工。
> 本文件是这套体系的完整说明。**岗位说明书原文**在 `config/agents/*/AGENTS.md` (每个 agent 每次启动都会读它)。

---

## 1. 为什么是 4 个 Agent, 不是 1 个人 + 3 个助手

| 设计点 | 理由 |
|---|---|
| **main 就是项目总工, 不另建总工 agent** | 总工的核心职责是"需求对接 + 跨模块串联", 而 main 已经持有全部项目上下文 (决策历史/锁死变量/老板偏好); 另建一个等于把上下文切一半出去, 还多一跳中转 |
| **三个子总工是平级的职能专家** | 硬件/软件/结构的判断依据完全不同 (降额规则 vs 帧龄模型 vs 公差栈), 一个 agent 兼三样会互相污染结论 |
| **★ 星型拓扑: 三个子总工之间【不做直接沟通】** | 老板原话: "2.硬件总工、3.软件总工、4.结构总工之间**不做直接沟通**, 由总工对接我的需求和命令拆分给各个模块" |
| **★ 但横向【信息】必须流通** | 堵死的是**对话**不是**信息**。结构总工要能读到硬件的 PCB 尺寸, 硬件要能读到结构给的镜脚内腔 —— 所以走**共享产出区 + 共享状态源**, 不走会话 |
| **一个 agent 同时只开一个写会话** | 压测实测: 同一 agent 两个并发写会话会**互相覆盖分片** (9 个 canary 全丢) |

---

## 2. 星型拓扑 + 三层守卫

```
        ┌──────────────┐
        │    main      │
        └──────┬───────┘
               │ sessions_spawn(agentId=...)
     ┌─────────┼─────────┐
   hw-lead  sw-lead  mech-lead
     └─────────┼─────────┘
               ↕ ✗ 禁止横向直聊
```

**三层守卫** (压测实测 5 条路径全对, 报告见 `docs/STRESS_TEST_2026-10-25.md`)

| 层 | 位置 | 作用 |
|---|---|---|
| 1 | per-agent `tools.deny: ["sessions_send"]` | 工具层: 三个子总工的会话工具列表里根本没有 `sessions_send` |
| 2 | per-agent `tools.exec.pathPrepend: [guards/<id>/]` | PATH shim: 命中 `--agent <非自己>` 直接 `exit 126` |
| 3 | **CLI 入口包装器** (`~/.npm-global/bin/openclaw`) | ★ 压测抓到: 只做前两层时, **绝对路径调用真二进制能绕过, 消息真的投进了对方会话** → 守卫下沉到 CLI 入口封死 |

**残余风险 (已知悉)**: 守卫是"纪律 + 包装器"级, 同一个 OS 用户蓄意规避 (改 cwd + 清环境变量 + 直接调 `dist/index.js`) 仍能绕过。**要内核级硬边界只有两条路** (给子总工 `deny exec` / `exec-approvals` 配 per-agent allowlist), 代价与取舍待定。

**防绕过之外, 真正的隔离靠机制**: 共享状态源的**合并器**只认"被问的那个 agent 的答复"才能闭合需求 → 就算消息串了, 也闭不了别人的需求。

---

## 3. 四个角色的职责与边界

### 3.1 main — 项目总工 (moli)

| 职责 | 产出落在哪 |
|---|---|
| 整体解决方案 (数据流架构/选型组合/备选路径) | `PROJECT_TRACKER.md` §1/§2 |
| 物料选型 (sensor/光机/波导/主控/桥接芯片) | §2 |
| 需求对接与拆解 (老板的话 → 可验证需求 → 同时下发三方) | `REQ/REQUIREMENTS.md` |
| 计划制定 (阶段门 G0-G4 + 里程碑) | §4 + `state/stage_gate.py` |
| 跨模块沟通串联 (收口产出/裁决冲突/组织评审) | `INTERFACES.md` + `HANDOFF/` |
| 质量与进度把控 (质量门/问题闭环/阶段门/就绪度) | `state/` |

**main 独有的 4 条铁律**
1. **自己修的必须别人验** (`verify_by ≠ owner`) —— 我自己写的 issue, 验证人也不能是我
2. **给用户的数必须引子总工的核算原文**, 不自己心算 (10-25 被 mech-lead 当场纠正过)
3. **外发一律经 main** —— 邮件/询价/采购只出草稿放 `state/outbox/`, 老板说"可以发"才发
4. **锁死变量表只有 main 能改** (`PROJECT_TRACKER.md` §0)

### 3.2 hw-lead — 硬件总工
- 硬件方案评估与**拆解** (26 个模块 + 明确排除项, 防以后被加回来)
- **原理图绘制与审核** (含 11 项审图 checklist) / PCB 图绘制与审核
- 电源树 / EMC 预评估 / 可靠性设计评审 / sensor 与镜头选型
- 边界: 不改锁死表; 不外联供应商; 高阶级不自行决定 (会升级给 main)

### 3.3 sw-lead — 软件总工
- 软件需求拆解 → 方案设计 → 方案评审 → 功能开发与验证
- **延迟预算必须建"框龄 (age)"模型**, 不能把环节相加 (age = ceil(T_od / 16.67ms), 差 1ms 可能差 17ms)
- 内存规划 / 低功耗策略 (与散热强耦合) / 固件烧录与回滚 / EVT 模板与联调计划
- 边界: 纯 NPU 耗时与 SDK 总耗时**必须分开报**

### 3.4 mech-lead — 结构总工 (带散热)
- 整体结构需求拆解 → 结构方案设计 → 方案评审 → **P2S 打印实现**
- 空间预算 (镜脚侧 + 镜框侧累加) / 散热稳态热模型 / 重量核算 / 材料选型 / DFM / 可靠性测试方案
- 边界: **报功耗必须同时报皮肤侧温度**; "临界" ≠ "通过" (余量要跟公差一起比)

### 3.5 三个总工的共同交付标准 (缺块即退回)

| 块 | 内容 |
|---|---|
| **B1** | 结论摘要 (一句话 + 关键数字) |
| **B2** | 验收标准自评 (逐条 通过/不通过/**未验**) |
| **B3** | 证据分级 `[实测]/[官方]/[推算]/[0数据]` |
| **B4** | 接口取值声明 (`interface_claims`, 短规范值, 散文走 note) |
| **B5** | 未决项 + 卡点 (等老板/原厂/JBD 必标 `waiting_on` + `due`) |
| **B6** | 自证复现命令 (别人能一条命令复算出结论) |

**"做不到"要交证据, 不交空口** —— 例: 结构总工交出 `ENV_PROBE.log` (打印机跨网段 ping 无响应 + 端口全 closed + 无切片器/量具) + 可下片 STL + 41 项测量清单, 而不是一句"环境不支持"。

---

## 4. 配置 (脱敏摘录)

> 完整: `config/openclaw.agents.json` (凭据 gateway token / tavily apiKey / 模型 authHeader **已在源头剔除, 原件不入库**)
> 岗位说明书原文: `config/agents/*/AGENTS.md`

```jsonc
{
  "tools": {
    "profile": "coding",
    "agentToAgent": { "enabled": true, "allow": ["main","hw-lead","sw-lead","mech-lead"] },
    "sessions":     { "visibility": "all" }        // 跨 agent 可见
  },
  "agents": {
    "defaults": {
      "workspace": "<OPENCLAW_HOME>/workspace",    // main 走这个继承
      "model": { "primary": "minimax/MiniMax-M3" },
      "subagents": { "allowAgents": ["main","hw-lead","sw-lead","mech-lead"] }
    },
    "list": [
      { "id": "main",      "name": "项目总工" },
      { "id": "hw-lead",   "name": "硬件总工",
        "workspace": "<OPENCLAW_HOME>/workspace-hw",
        "agentDir":  "<OPENCLAW_HOME>/agents/hw-lead/agent",
        "model": "minimax/MiniMax-M3",
        "subagents": { "allowAgents": ["hw-lead"] },          // 只能 spawn 自己
        "tools": { "deny": ["sessions_send"],                 // 守卫第 1 层
                   "exec": { "pathPrepend": ["<OPENCLAW_HOME>/guards/hw-lead"] } } },  // 第 2 层
      { "id": "sw-lead",   "name": "软件总工",   …同构… },
      { "id": "mech-lead", "name": "结构总工(带散热)", …同构… }
    ]
  }
}
```

**各 agent 的运行时基建** (每个 workspace 必备)

| 文件 | 作用 |
|---|---|
| `AGENTS.md` | ★ 岗位说明书 (职责/边界/交付标准/通信规则) —— **每次启动都会读** |
| `SOUL.md` / `IDENTITY.md` / `USER.md` | 人格 / 身份 / 用户画像 (不随仓库公开) |
| `HEARTBEAT.md` | 轮转检查项 |
| `MEMORY.md` | 自己的长期结论 |
| `skills/` | 项目专属 skill (见下) |
| `projects/` | → 指向共享项目库的**软链**, 相对路径可用 |

**skill 分工**: `smart-glasses-pm` (总工工作法) / `-hw` / `-sw` / `-mech` (三总工) / `state-protocol` (状态源协议) / `smart-hardware-reference` (9 域 68 项硬件生命周期基准) / `qa-requirement-review` (需求五维评审)
> ⚠️ 装 ClawHub skill 必须扫 U+FFFD / BOM / CRLF —— 装完**根本不加载且零报错** (发布方编码坏), 每次装完立刻 `skills list` 确认在列表里且 ready。

---

## 5. 共享状态源协议 (跨 agent 协作的底座)

```
各总工独占写自己那份分片  →  合并器纯函数合并  →  原子写  →  STATE.yaml (全员只读)
state/fragments/{pm,hw,sw,mech}.yaml     state/merge.py              STATE.yaml
```

**三个机制**
1. **`needs_from` × `answers` 按 key 配对** —— 需求自动标 answered。★ **只有被问的那个 agent 的回答才能闭合它**, 别人代答记进 `foreign_answers`
2. **`interface_claims` 同 key 不同值 → 自动 conflict** —— 跨模块接口取值冲突被机械检出
3. **`waiting_on` + `due`** —— 等老板/原厂/JBD 的需求标等待, 合并器自动算逾期; 等另一个总工**不标** `waiting_on` (默认 agent)

**铁律**
- **写分片必须原子写** (`state/frag_write.py`) —— 普通 `open(p,"w")` 实测 99.6% 概率读到半截, **整个 agent 域从快照静默蒸发** (12%~38% 的合并受影响, 而快照还打 ✅)
- **绝不直接编辑 `STATE.yaml`** (合并器唯一写)
- **老板的决策**用 `decision` 字段记在需求上 (老板是人不是 agent, 走 agent 间配对规则永远闭合不了)

---

## 6. 质量门体系 (把控不靠"我看过了")

| 门 | 脚本 | 判据 |
|---|---|---|
| **交付质量门** | `state/gate_check.py` | Q1 齐备率(18) / Q2 证据分级 / Q3 接口声明 / Q4 需求闭环 / Q5 硬指标覆盖 —— **gate ↔ merge 自动对账** |
| **问题闭环门** | `state/issue_check.py` | 字段 / 状态机 / **验证分离** / 逾期 / **双向覆盖** (STATE 的高危阻塞必须有 issue; issue 引用的阻塞必须真实存在) |
| **阶段门** | `state/stage_gate.py` | G0-G4 五关, 准出 = issue 状态 + 老板决策已答 + **实测项齐全** (推算值不算) |
| **执行就绪度** | `state/readiness.py` | 38 条判据给 4 个角色打分; **分两层**: 纸面阶段 ✅ / 样机阶段 ❌ |
| **配置审计** | `state/agent_config_check.py` | 81 条判据: 配置/定义/workspace/**skill 加载(含 U+FFFD 扫描)**/通信拓扑/三层守卫/运行时 |
| **巡检 + 漂移** | `state/daily_check.py` | 每天自动跑, 与上次快照逐项比 → **齐备率掉了/未闭合多了/逾期多了 → 报警** |

**问题闭环状态机** (不许跳级)
```
open → fixing → fixed → verified → closed
                          ▲          │
                          └── 验证分离: verify_by ≠ owner ──┘
```
`fixed ≠ closed`: closed 必须有 `fix_ref` + `verify_result=pass` + `verify_by ≠ owner` + `verify_date`。

**外部等待单列**: 等老板/原厂/JBD 的问题**不算总工失职**, 但必须有 `verify_by` 盯着, 否则就是"没人追"。

---

## 7. 已验证的坑 (压测抓出来的)

`docs/STRESS_TEST_2026-10-25.md` 完整报告。**11 个缺陷, 5 个严重**, 全部已修:

| 缺陷 | 后果 |
|---|---|
| 绝对路径调 CLI 绕过守卫 | **消息真的投进了对方会话** (实证 3 次) |
| 分片非原子写 | **整个 agent 域从快照静默蒸发**, 快照还打 ✅ |
| 截断落在合法 YAML 边界 | 解析成功但数据残缺 (411/4551 次) |
| 固定名 `STATE.yaml.tmp` | 并发 merge 互踩, 7.5% 概率崩 |
| 非 dict 元素 / UTF-8 多字节截断 | merge 直接抛异常 |

**教训**: 顺序跑测不出并发缺陷 (规范步骤 10 次顺序 merge 全绿, 加并发才炸); **失败要降级到"旧但完整"而不是"新但残缺"**。

---

## 8. 复现命令

```bash
cd projects/smart_glasses
python3 state/test_merge.py       # 合并器自测
python3 state/test_whitebox.py    # 白盒 (配置层/隔离/路由/并发/异常)
python3 state/stress_test.py      # 并发压测台 (沙盒副本, 不碰真数据)
python3 state/merge.py            # rc 0=完整 2=不完整 1=崩
python3 state/gate_check.py       # + 与 merge 自动对账
python3 state/issue_check.py
python3 state/stage_gate.py
python3 state/readiness.py
python3 state/agent_config_check.py
python3 state/daily_check.py
./status.sh
```
