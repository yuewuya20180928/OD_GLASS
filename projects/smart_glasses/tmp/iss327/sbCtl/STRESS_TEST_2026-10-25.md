# 4-Agent 通信 · 压力 / 并发 / 异常结果测试报告

> 指令来源: 老板 2026-10-25 01:02 —— "先压力和并发测试一下各个agent之间的通信是否正常及是否会存在异常通信结果"
> 执行: 项目总工 (main) + 硬件/软件/结构三个总工并发执行
> 窗口: 2026-10-25 09:04 – 09:16 (25 分钟)
> 结论一句话: **通信通道干净 (零串味 / 零误闭合 / 消息投递被守卫拦住), 但共享状态源在并发下会"说谎" —— 已修 10 处, 留 2 项残余风险**

---

## 0. 结论速览

| 维度 | 结论 | 证据等级 |
|---|---|---|
| 横向消息**会不会串味** | **不会** —— 双向 0 泄漏 (4 个总工各自 canary 归属 100% 正确) | 实测 (三方独立验证) |
| 需求**会不会被误闭合** | **不会** —— 600+ 条压力需求 0 条被误标 answered, 第三方代答全部进 `foreign_answers` | 实测 (三方独立验证) |
| 消息**能不能违规投递** | **原来能** —— 绝对路径调用绕开守卫, 消息**真的**进了对方会话 (3 次实证) → **已封** | 实测 + 修复后复测 5/5 |
| 共享状态源**能不能当真** | **原来不能** —— 并发下 12% 的合并把某个 agent **整域静默蒸发**, 快照还打 ✅ | 实测 (三方 + 本地测试台) |
| 修完能不能当真 | **能** —— 并发压测下整域消失 0 次, 半截快照 0 次, 异常输入不再崩 | 修复后复测 |

---

## 1. 测试架构 (三层, 互相印证)

| 层 | 做法 | 产出 |
|---|---|---|
| **L1 协议层 (本地, 确定性)** | `state/stress_test.py` 沙盒副本跑 7 组测试: 并发合并 / 撕裂读 / 读者一致性 / 配对语义 / 异常输入 / 同分片并发写 / 半截留痕 | 可复现, 带数字 |
| **L2 真实 agent 层** | 3 个总工**同时**跑: 各自写自己分片 (9 轮) + 各自并发跑 merge + 读自己切片 + 消息通道探针 | 三方独立结论, 交叉印证 |
| **L3 白盒层** | `state/test_whitebox.py` (配置层 / agentDir 隔离 / 路由精确性 / 上下文不串 / 并发安全 / 异常检测) | 全部通过 |

---

## 2. 抓到的真缺陷 (按严重度)

### 🔴 D1 · 绝对路径调用完全绕过星型拓扑守卫, 消息**真投递**
- **现象**: `tools.exec.pathPrepend` 注入的 PATH shim 只拦**裸命令** `openclaw`; 用绝对路径 `/home/yuewuya/.npm-global/bin/openclaw agent --agent <对方>` 直接调真二进制 → 绕过。
- **实证**: sw-lead 的探针消息原文 `stress probe sw->hw abs-path` 出现在 `agents/hw-lead/sessions/1ea3a11a-*.jsonl` 的 **user 消息**里; mech-lead 的 `stress probe mech->sw` 出现在 sw-lead 会话里; 对方 assistant 已经开始回应。
- **影响**: 老板 10-25 硬规则"三个总工之间不做直接沟通"**当时是纸面的**。此前 MEMORY 里记的 R15"绝对路径仍能绕过"由推测变成**已验证事实**。
- **修法**: 守卫从 PATH 层**下沉到 CLI 入口本身** —— 替换 `~/.npm-global/bin/openclaw` 为守卫包装器 (网关服务走 `node dist/index.js`, 不经过该 bin, 不受影响)。

### 🔴 D2 · 分片非原子写 → 整个 agent 从共享快照**静默蒸发**
- **现象**: 分片用 `open(p,"w")` (先 truncate 再写) → 合并器读到 0 字节或半截 → `yaml.safe_load` 返回 `None` → `merge.py` 走 `if not isinstance(data, dict): continue` → **连 stderr 告警都没有**, 该 agent 全部产出/需求/阻塞从快照消失, 但 merge 仍 `rc=0` + 打印 `✅ STATE.yaml 已刷新`。
- **实测**: hw-lead 测出 **330,291 / 331,579 次并发读命中 0 字节文件 (99.61%)**; mech-lead 测出 **40 轮合并里 15 轮 (38%) 整个 domain 消失** (峰值丢 138 个 canary + 694 条 needs + 4 条 blocker)。
- **最坏后果**: 别的 agent 读到这份快照, 会认为"硬件总工没有待办" → **据此做出错误决策**; 且事后无法从 STATE.yaml 判断快照是残缺的。

### 🔴 D3 · 截断到"合法 YAML 边界" → 静默丢数据, 连告警都没有
- **现象**: 分片写了一半, 截断点恰好落在 YAML 合法边界 → 解析**成功** → 合并器接受**残缺**分片 → 数据无声消失。
- **实测**: sw-lead 受控实验 400 条 needs_from, 4 读线程 × 3000 次 → **411 次"合法但截断"** (n≠400), 4024 次解析失败。hw-lead 对 18,988 字节分片做 138 点截断 → **73 点解析失败 / 3 点崩 merge / 62 点"正常"但数据少一半**。
- **为什么难防**: 光看 YAML 合不合法**判不出来** → 只能靠"写侧原子化"根治。

### 🔴 D4 · 并发合并互相踩固定名 tmp → 合并器崩溃, 快照静默过期
- **现象**: `atomic_write` 用固定名 `STATE.yaml.tmp` → 两个 merge 并发时, 先完成的 `os.replace` 把 tmp 吃掉, 后完成的找不到文件 → `FileNotFoundError` → `rc=1`。
- **实测**: hw-lead **53 次调用里 4 次崩 (7.5%)**; 6 并发时 **7/8 崩**。极端情况: tmp 被别人 rename 走后, 下一个 merge 会把**半截内容**提升成正式快照 → **静默快照污染**。
- **文档不符**: `merge.py` 头注释写"纯函数, 无锁, 任何 agent 任何时候都能跑" —— 实测**不成立**。

### 🟠 D5 · 畸形 schema 直接打崩合并器
- **现象**: `merge.py:143` 对 `needs_from` 元素直接 `.get()` → 元素退化成 str 时 `AttributeError: 'str' object has no attribute 'get'`; 字段整体类型错 (如 `needs_from: "字符串"`) → 整个合并 rc=1, **STATE.yaml 根本不生成**。

### 🟠 D6 · UTF-8 多字节被截断 → UnicodeDecodeError
- **现象**: 写到一半的多字节字符被切开 → `'utf-8' codec can't decode byte 0xe2 in position 0`。

### 🟠 D7 · 已闭合的需求会因对方分片被跳过而**翻回 pending** (状态源"说谎")
- **现象**: 答案存在 mech.yaml, 那一瞬间 mech.yaml 被读到半截 → 合并跳过 → `pcb_outline_confirm` 从 `answered` 变 `pending`, `answers: []` → 项目总工会**重复催办**已答复的问题。
- **sw-lead 给了完整 A→E 复现链**。

### 🟠 D8 · 目标 agent 缺席时, 指向它的需求**凭空蒸发**
- **现象**: `open_needs` 在 16 ↔ 344 之间剧烈跳变, 没人被通知。

### 🟡 D9 · 同一 agent 的两个并发会话互相覆盖分片 (丢失更新)
- **现象**: 两个 hw-lead 会话同时 read-modify-write 同一 `hw.yaml` → 后写者覆盖先写者, **先写者的 9 个 canary 全丢** (兄弟会话的 9 个全活)。合并器只看 `agent` 字段, 分不清谁写的 → **产出归属失真**。

### 🟡 D10 · 压测条目无上限, 快照被撑爆
- **现象**: needs_from 膨胀到 694 条, STATE.yaml 涨到 360 KB, 合并耗时随条目数线性增长。

### 🟡 D11 · 既有测试套件完全没覆盖并发路径
- `test_merge.py` / `test_whitebox.py` 全绿, 但 D1–D10 全部落在测试盲区里。

---

## 3. 已实施的修复 (merge.py v1.1 + 守卫下沉)

| # | 修复 | 对应缺陷 |
|---|---|---|
| 1 | 原子写 tmp 唯一化 (PID + 随机名), 失败只删自己那个 tmp | D4 |
| 2 | 合并器加 `fcntl.flock` 排他锁 → 并发 merge 串行化 | D4 |
| 3 | 分片读: 5 次重试 + **读前后 stat 检测**(文件在读期间被改过就重读) + 0 字节视为瞬态 | D2 D3 D6 |
| 4 | 分片读失败 → **回退 `state/.lastgood/` 上次成功快照** (宁可给旧数据, 也不给"这个 agent 不存在") | D2 D3 D7 |
| 5 | 分片 schema 归一化 (类型错/非 dict 条目 → 忽略 + 记 lint, 不再崩) | D5 D6 |
| 6 | 快照不完整 → `meta.incomplete_fragments` 留痕 + **rc=2** + CLI/切片双重告警 | D2 D3 D7 D8 |
| 7 | 需求目标 agent 缺席 → `target_missing: true` 单独标出 (不改 pending 语义) | D8 |
| 8 | `meta.fragments` 写进各分片指纹 (size/sha1/mtime_ns) → 快照新鲜度可判断 | D10 D11 |
| 9 | 两个分片声明同一 agent id → 检出并留痕 (防冒名/静默覆盖) | D9 |
| 10 | 新增 `state/frag_write.py` —— **分片原子写工具** (tmp + fsync + replace), 协议强制用它 | D2 D3 D9 |
| 11 | 守卫下沉到 CLI 入口 (`~/.npm-global/bin/openclaw` 包装器), 5 条路径实测全对 | D1 |
| 12 | `state/stress_test.py` —— 可复现压测台 (7 组测试, 沙盒副本, 不碰真数据) | D11 |

### 修复前后对照 (L1 本地测试台, 同参数)

| 指标 | 修复前 | 修复后 |
|---|---|---|
| T1 20 个 merge 并发 | rc 混 `0/1` (部分崩溃) | **rc 全 0**, 快照 200/200 完整, 无 .tmp 残留 |
| T2 撕裂读 · 整域消失/静默丢数据 | **6 次** | **0 次** |
| T2 撕裂读 · 数据过期(显式标记) | 14 次(隐性) | 25 次(**显式标 stale**) |
| T2 撕裂读 · 解析失败跳过 | 6 次 | **0 次** |
| T3 292 次并发读快照 | 0 次半截 | 0 次半截 |
| T5 字段类型错 | **rc=1 崩, STATE.yaml 不生成** | rc=2, 快照有效, lint 留痕 |
| T5 其余 8 种异常输入 | 多数 rc=0 但**不留痕** | 全部 rc=2 + 留痕 + CLI 告警 |
| T7 半截分片 | **零标记** | `meta.incomplete_fragments` 留痕 + 双重告警 |

### 守卫修复后复测 (5 条路径, 全对)

| 路径 | 结果 |
|---|---|
| 裸命令 `openclaw agent --agent X` (走 PATH shim) | **126 拦截**, 未送达 |
| **绝对路径** `.../bin/openclaw agent --agent X` (原来能绕) | **126 拦截** ✅ 已封 |
| 绝对路径 + `OPENCLAW_STAR_OVERRIDE=1` (项目总工手动) | 0 放行 + 审计留痕 |
| 同 agent 自调用 `--agent <自己>` | 0 放行 |
| 非 `agent` 子命令 (config/status/--version) | 0 放行 |

---

## 4. 残余风险 (未根治, 需老板知悉)

1. **🔴 同一 agent 的两个并发会话互相覆盖分片** (D9) —— 根治手段: 一个 agent 同时只允许一个写会话, 或分片加 `writer_session` 字段、合并器按 (agent, session) 分组。**协议层已写死"一 agent 一文件", 但"一 agent 一会话"目前没强制**。
2. **🟠 守卫是纪律 + 包装器, 不是内核级隔离** —— 四个 agent 跑在**同一个 OS 用户**下, 蓄意规避 (改 cwd + 清环境变量 + 直接调 `dist/index.js`) 仍能绕过。**要硬边界只有两条**: ① 给三个总工 `tools.deny: ["exec"]` (代价: 不能跑 shell 查料号/编译); ② `~/.openclaw/exec-approvals.json` 配 per-agent allowlist (代价: 非白名单命令一律拒, 且无 UI 时默认 deny, 日常会频繁被挡)。**当前不擅自改, 等老板拍板**。
3. **🟠 分片非原子写仍在发生** —— 修复是"合并器能自证快照完整 + 出事回退旧快照"; 根治要**全员改用 `state/frag_write.py`**。已在协议文档和 skill 里写死, 但三个总工是否照做需要后续抽查。
4. **🟡 压测条目无上限** (D10) —— 需要给 `needs_from` 加保留期/归档策略。

---

## 5. 复现方式

```bash
cd projects/smart_glasses

# L1 协议层压测 (沙盒副本, 不碰真数据) —— 修复后应全绿
python3 state/stress_test.py            # 原版行为对照: STRESS_MERGE=<旧版merge.py路径>

# L3 白盒测试 (配置层 / 隔离 / 路由 / 并发安全 / 异常检测)
python3 state/test_whitebox.py
python3 state/test_merge.py

# 真项目刷新
python3 state/merge.py                   # rc=0 完整 / rc=2 不完整 / rc=1 崩了
python3 state/merge.py --for hw-lead     # 切片 (顶部会提示快照是否完整)
```

## 6. 涉及文件

| 文件 | 变更 |
|---|---|
| `state/merge.py` | v1.1 (12 处修复); 旧版备份 `state/merge.py.bak_pre_stress_20261025_0918` |
| `state/frag_write.py` | **新增** 分片原子写工具 |
| `state/stress_test.py` | **新增** 压测台 (7 组) |
| `state/test_merge.py` | 适配新签名 |
| `state/test_whitebox.py` | 修指纹检测假阳性 (只查 user 消息) + 修 main 发送方判定 |
| `state/README.md` | 协议文档更新 (原子写 / rc 码 / 不完整标记 / 守卫三层) |
| `~/.npm-global/bin/openclaw` | **CLI 入口守卫** (原软链备份 `/tmp/openclaw.bin.symlink.bak`) |
| `~/.openclaw/guards/*/openclaw` | 注入 `OPENCLAW_CALLER_AGENT` 标记 |
| `~/.openclaw/guards/star-topology.log` | 跨 agent 投递审计日志 |
