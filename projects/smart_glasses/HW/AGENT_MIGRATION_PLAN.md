# ARS45 项目 —— 4-Agent 职能制迁移到另一台主机

> **文档**: `HW/AGENT_MIGRATION_PLAN.md` · **起草**: 项目总工 (moli) · **日期**: 2026-11-01 21:2x
> **场景**: 老板要把本项目全部 agent 配置拷到另一台主机, 由那边的 **openclaw TUI** 接管后继处理
> **配套**: `config/openclaw.agents.json` (脱敏后的 agent 配置摘录, 已随仓库推送) · `config/agents/` (四份 AGENTS.md, 已推送)

---

## B1 结论摘要 (三句话)

1. **项目库本体已经在 GitHub 上**(415 个文件, HEAD `3f0d256a`)⇒ **另一台主机 clone 下来就有了 90% 的工作面**。
2. **缺的是 agent 的"人格 + 记忆 + 守卫"三件套**(共 **85 个文件**): 四份 SOUL/IDENTITY/USER/TOOLS/MEMORY + main 的 48 篇日记 + 4 个 guards shim ⇒ **这些要补推**。
3. ★**两个文件绝对不能进公开仓库**: `TOOLS.md`(含板子 SSH 明文口令)与 `auth-profiles.json`(含 minimax API key)⇒ **必须走带外传输**(见 §4), **且闸门要补规则** —— 现在的闸门**抓不到 auth-profiles 里的 key**(实测漏检)。

---

## B2 ★先看清事实: 四个 agent 的 workspace 到底是不是四份

**实测结论(纠正 AGENTS.md 里"软链"的措辞)**:

| 路径 | 实测 | 说明 |
|---|---|---|
| `workspace-hw/projects` → `workspace/projects` | ✅ **是软链** (readlink 确认) | 三个子 agent 的 `projects/` 都指向同一个目录 |
| `workspace{,-hw,-sw,-mech}/projects/smart_glasses` | ★**inode 完全相同 (6839086)** | ⇒ **只有一份项目库**, 不是四份拷贝 |

⇒ ★**迁移含义**: **只需要搬一份 `projects/smart_glasses`**, 另一台主机把三个子 agent 的 `projects` 也做成软链即可 ⇒ **不存在"四份分叉要合并"的问题** (这点很重要, 否则迁移会做重复劳动)。

---

## B3 ★差集: 哪些已经在 GitHub, 哪些还要推

> 复现: `python3 HW/agent_migration_diff.py` (机械差集, 数字实时读)

### ✅ 已在 GitHub (415 文件)
| 类别 | 位置 |
|---|---|
| 项目库本体 | `projects/smart_glasses/**` (392 文件) |
| 四份岗位说明书 | `config/agents/{main,hw-lead,sw-lead,mech-lead}/AGENTS.md` |
| 三个总工的 MEMORY.md | `config/agents/*/MEMORY.md` |
| agent 配置摘录 (脱敏) | `config/openclaw.agents.json` |
| 文档/生成物 | `docs/**`, `README.md` |

### ★★ 还要推 (85 个文件, 全部**无凭据**)
| # | 类别 | 数量 | 目标路径 |
|---|---|---|---|
| 1 | **main 的长期记忆 + 日记** | **48** | `config/agents/main/memory/*.md` + `config/agents/main/MEMORY.md` |
| 2 | **四份人格文件** (SOUL/IDENTITY/USER) | **12** | `config/agents/<id>/{SOUL,IDENTITY,USER}.md` |
| 3 | **guards PATH shim + 星型拓扑日志** | **4** | `config/guards/<id>/openclaw`, `config/guards/star-topology.log` |
| 4 | **agent 局部配置** (models.json / auth-state.json) | **6** | `config/agents/<id>/agent/{models,auth-state}.json` |
| 5 | **项目级 skills** | **3** | `config/skills/{qa-requirement-review,smart-glasses-pm,smart-hardware-reference}/` |
| 6 | **全局 skills** | **2** | `config/skills-global/{nimo-glasses,state-protocol}/` |
| 7 | **迁移操作手册** (本文) | **1** | `HW/AGENT_MIGRATION_PLAN.md` |
| 8 | **补推脚本** (一键重跑, 可复现) | **1** | `state/_migrate_assets.py` |
| 9 | **带外传输清单** | **1** | `config/OFFLINE_TRANSFER_CHECKLIST.md` |

**★已实测推送 (2026-11-01 21:5x)**: 远端 commit `4d62791` ⇒ `config/` 共 **102 个文件**:
`main 日记 48 + 其它 agent 人格/配置 21 + guards 4 + 项目 skills 14 + 全局 skills 11 + 其它 4` ⇒
**另一台主机 clone 完就有了全部 agent 配置** (凭据除外, 走带外)。

### ★★ 绝对不能推 (带凭据, 走带外通道)
| 文件 | 含什么 | 出处 |
|---|---|---|
| `workspace/TOOLS.md` | 板子 SSH **明文口令** (`sshpass -p '<BOARD_SSH_PASSWORD>'`) | 本机 `~/.openclaw/workspace/TOOLS.md` |
| `agents/main/agent/auth-profiles.json` | **minimax API key** (`sk-cp-...`) | 本机 `~/.openclaw/agents/main/agent/auth-profiles.json` |
| `openclaw.json` | gateway auth token (48 字符) + tavily apiKey | 本机 `~/.openclaw/openclaw.json` |
| `cron/jobs.json` | 微信 openid (推送目标) | 本机 `~/.openclaw/cron/jobs.json` |

⇒ ★**这 4 个文件是"后继处理真正需要的"** ⇒ **必须带过去, 但不能进 GitHub** ⇒ 见 §4。

---

## B4 ★★另一台主机怎么接管 (分 5 步, 按顺序做)

### 步骤 0 — 先确认前提 (别跳过)
- [ ] 另一台主机已装 **openclaw** 且版本 ≥ 本机 (本机 `app 2026.5.19`)
- [ ] 另一台主机能访问 GitHub (本机网络很慢, `git clone` 要 10 分钟; **建议 `--depth=1 --single-branch`**)
- [ ] **模型 API key 有效** (minimax / anthropic —— 走 §4 带外)
- [ ] 决定: **旧主机是否继续跑?** ⇒ ★**强烈建议旧主机关掉 cron** (见步骤 4), 否则**两边同时派活会互相覆盖分片** (AGENTS.md 铁律: 一个 agent 同时只开一个写会话)

### 步骤 1 — 装 openclaw 配置骨架
```bash
# ① clone 项目库 (只这一份! 三个子 agent 的 projects 后面做软链)
git clone --depth=1 --single-branch git@github.com:yuewuya20180928/OD_GLASS.git
cd OD_GLASS
# ② 把脱敏的 agent 配置套进 openclaw.json
#    ★ 不是直接覆盖 —— 要手工合并 (见本文末尾 §6 的合并步骤)
```

### 步骤 2 — 铺 workspace 目录结构
```bash
OPENCLAW_HOME=~/.openclaw
mkdir -p $OPENCLAW_HOME/{workspace,workspace-hw,workspace-sw,workspace-mech}
mkdir -p $OPENCLAW_HOME/workspace/projects
# ★ 项目库只有一份 ⇒ 三个子 agent 的 projects 指向它 (复刻本机的软链拓扑)
ln -s $OPENCLAW_HOME/workspace/projects $OPENCLAW_HOME/workspace-hw/projects
ln -s $OPENCLAW_HOME/workspace/projects $OPENCLAW_HOME/workspace-sw/projects
ln -s $OPENCLAW_HOME/workspace/projects $OPENCLAW_HOME/workspace-mech/projects
# ★ main 的 workspace 里也要能进项目库
ln -s $PWD/OD_GLASS/projects/smart_glasses $OPENCLAW_HOME/workspace/projects/smart_glasses
```

### 步骤 3 — 铺 agent 人格 + 记忆 + 守卫
```bash
cd OD_GLASS
for a in main hw-lead sw-lead mech-lead; do
  wd=$OPENCLAW_HOME/workspace; [ "$a" != main ] && wd=$OPENCLAW_HOME/workspace-$a
  mkdir -p $wd/memory
  # 人格 + 身份 + 记忆
  cp config/agents/$a/{SOUL,IDENTITY,USER,MEMORY}.md $wd/ 2>/dev/null
  cp config/agents/$a/memory/*.md $wd/memory/ 2>/dev/null
  # 岗位说明书
  cp config/agents/$a/AGENTS.md $wd/
  # agent 局部配置
  mkdir -p $OPENCLAW_HOME/agents/$a/agent
  cp config/agents/$a/agent/{models,auth-state}.json $OPENCLAW_HOME/agents/$a/agent/ 2>/dev/null
done
# ★ TOOLS.md 不在仓库 (含口令) ⇒ 走 §4 带外
# guards
mkdir -p $OPENCLAW_HOME/guards
cp -r config/guards/* $OPENCLAW_HOME/guards/
chmod +x $OPENCLAW_HOME/guards/*/openclaw
# skills
cp -r config/skills/* $OPENCLAW_HOME/workspace/skills/ 2>/dev/null
cp -r config/skills-global/* $OPENCLAW_HOME/skills/ 2>/dev/null
```

### 步骤 4 — 装凭据 (带外, 唯一不能进 GitHub 的部分)
```bash
# ★★ 以下 4 个文件从旧主机带过来 (scp / 密码管理器 / 加密包), 不要走 GitHub
scp old-host:~/.openclaw/openclaw.json                      $OPENCLAW_HOME/
scp old-host:~/.openclaw/workspace/TOOLS.md                $OPENCLAW_HOME/workspace/
scp old-host:~/.openclaw/agents/main/agent/auth-profiles.json $OPENCLAW_HOME/agents/main/agent/
scp old-host:~/.openclaw/cron/jobs.json                     $OPENCLAW_HOME/cron/
# ★ 然后把 openclaw.json 里的 agents 段替换成 config/openclaw.agents.json 的内容 (路径占位符换成实际路径)
# ★ 微信 openid 在 cron/jobs.json 里 ⇒ 推送目标不用改
```

### 步骤 5 — 恢复 cron (★ 注意: 旧主机要先停)
```bash
# ★★★ 顺序不能反: 先停旧主机的 cron, 再开新主机的
# 旧主机 (如果继续留着):
openclaw cron disable <jobId>   # 或直接停 systemd 服务
# 新主机:
openclaw cron add --name "ARS45 队列自动派活" --cron "7,37 * * * *" --session isolated \
  --message "<从 config/cron/ 拿 payload>" --model minimax/MiniMax-M3.1-Flash
# ★ 每个 job 都要带 model=minimax/MiniMax-M3.1-Flash (默认 MiniMax-M3 会挂 token plan 上限)
```

### 步骤 6 — 冒烟验证 (照着跑, 数字必须对)
```bash
cd $OPENCLAW_HOME/workspace/projects/smart_glasses
python3 state/merge.py        # rc=0, 冲突 0
python3 state/gate_check.py   # Q1 18/18
python3 state/issue_check.py  # 违规 0
python3 state/stage_gate.py   # G2, 差 7 项
./status.sh                   # 一屏看板
# ★ 与旧主机最后一次快照对比: 问题单条数 / closed / verified 数应完全一致
```

---

## B4 ★★★ 一键铺装 (老板要的"一键搞定" —— 已实测跑通)

> **脚本**: `HW/bootstrap_ars45.sh` · **在新主机上跑**:
> ```bash
> bash bootstrap_ars45.sh --check        # 先体检, 不改任何东西
> bash bootstrap_ars45.sh               # 标准铺装
> ```

### 它做什么 (7 步, 全自动)
| 步 | 动作 |
|---|---|
| ① | **体检**: openclaw / git / 凭据是否就位 (4 个带外文件逐个报) |
| ② | **clone 仓库** (SSH 失败自动退 HTTPS) —— 只 clone **一份** |
| ③ | 铺 workspace 目录 + **★projects 软链拓扑** (复刻旧主机: 四个 inode 相同) |
| ④ | 铺四个 agent 的 **人格/身份/记忆/岗位说明书** + main 的 48 篇日记 + **guards** + skills |
| ⑤ | 装**带外凭据** (4 个文件) + 合并 `openclaw.json` 的 agents 段 (★只合并 agents 段, 绝不整file覆盖) |
| ⑥ | 打印 cron 恢复模板 (★每个 job 带 `model=MiniMax-M3.1-Flash`) |
| ⑦ | **冒烟验证**: merge / gate / issue / stage 四道门 + 与旧主机对数 |

### ★实测结果 (隔离假 HOME 跑通, 2026-11-01 21:5x)
```
① 体检        ✅ 4 个凭据全部识别
② clone      ✅ (SSH 失败自动退 HTTPS)
③ 软链拓扑   ✅ 四份 projects/smart_glasses inode 一致 (= 1)
④ 铺文件     ✅ main 4 文件 + 48 篇日记; 三个总工各 4 文件; guards + skills 全装
⑤ 凭据       ✅ agents 段合并, model = minimax/MiniMax-M3.1-Flash ✅
⑦ 四道门     ✅ merge rc=0 (冲突 0) · Q1 18/18 · 违规 0 · G2 差 7 项  ← **与旧主机数字完全一致**
幂等性       ✅ 重跑 0 错
```

### ★★但有一件事脚本**故意不做** —— cron 不自动恢复
**为什么**: `openclaw cron add` 的 `--message` 参数是**整个 payload 全文**(每个 job 几百到上千字, 还含引号/换行)⇒ **命令行传参极易踩 shell 转义坑** ⇒ ★**脚本只把 7 个 job 的表达式/名字/model 打出来 + 给模板**, 让执行者逐条粘贴 ⇒ **宁可让人看一眼, 不要自动化踩坑**。
⇒ 如果你要全自动, 我可以改成写 `jobs.json` 再 `openclaw cron` 导入(需先验证该 CLI 有导入命令 —— **目前没查, 不能瞎编**)。

## B4.5 ★★实测踩到的 3 个坑 (我做这一步时真踩的, 别在新主机上重踩)

| # | 坑 | 现象 | 根因 |
|---|---|---|---|
| 1 | ★**发布脚本只 cp 4 个 AGENTS.md** | 我把 85 个迁移资产放进项目树的 `config/`, 推上去**远端只有 AGENTS.md** | 发布脚本第 3 步是 `cp` 单个文件, **不是 rsync 整个目录** ⇒ 已改成 `rsync -a --delete "$PROJ/config/" config/` |
| 2 | ★**agent id ≠ workspace 目录名** | `hw-lead` 的 workspace 是 `workspace-hw` (不是 `workspace-hw-lead`) ⇒ 拷贝脚本报"源不存在" | agent id 带角色后缀, workspace 用短名 ⇒ 脚本里用 `aid.split("-")[0]` |
| 3 | ★**占位符路径写错** | `config/openclaw.agents.json` 里写成了 `<OPENCLAW_HOME>/workspace-hw-lead` | 同上 ⇒ 已改成 `workspace-hw` / `workspace-sw` / `workspace-mech` |
| 4 | ★**`${a##*-}` 取到 "lead"** | 三个子 agent 全指向 `workspace-lead` | agent id 拆**第一段** (`${a%%-*}`) |
| 5 | ★**clone 目标套了一层** | 仓库被 clone 进 `smart_glasses/` 里一层 ⇒ 后面全找不到 | 仓库根 = `workspace/` (里面才有 `config/` + `projects/`) |
| 6 | ★**clone 错误被 `2>/dev/null` 吞了** | 只报"找不到项目库", 查不到真因 | 错误存临时文件并打印原文 |
| 7 | ★**编辑时把 `else` 分支删掉了** | clone 逻辑只在 `if` 里, 不成立时啥也不干 | ⇒ ★**这就是"写完不实测"的典型后果** |

## B5 ★★另一台主机会踩的 5 个坑 (按踩到概率排序)

| # | 坑 | 后果 | 预防 |
|---|---|---|---|
| 1 | ★**两边 cron 同时开** | 同一个 agent 两个写会话 ⇒ **互相覆盖分片** (10-29 第三例撞车, 两条都 0 产出) | **先停旧主机, 再开新主机**; 旧主机的 5 个 cron 里"队列自动派活"**当前是 disabled**(实测)⇒ 迁过去前**确认要不要恢复它** |
| 2 | ★**push 到了错误的远端** | 新主机 clone 的是**旧主机推的**那个远端 ⇒ 但如果新主机自己开 cron 推, 会用**新主机的 SSH key** 推同一个仓库 ⇒ 要么配置**只读**账号, 要么明确"新主机是唯一推送方" | 迁移后**明确单一推送方** |
| 3 | ★**忘记建 projects 软链** | 子 agent 写到自己 workspace 下的独立副本 ⇒ **四份分叉**, 合并时冲突爆炸 | 照步骤 2 做, 跑 `stat -c %i` 确认**四个 inode 相同** |
| 4 | ★**闸门没补规则 → 凭据泄漏** | 另一台主机若把 `auth-profiles.json` / `TOOLS.md` 放进发布树 ⇒ **公开仓库泄 API key** | ★**本轮就要给闸门补规则**(见 §7) |
| 5 | **skills 没装** | `smart-glasses-pm` / `state-protocol` / `smart-hardware-reference` 缺失 ⇒ agent 少了方法论与状态协议 | 照步骤 3 装 |

---

## B6 ★`openclaw.json` 的合并步骤 (别直接覆盖)

`config/openclaw.agents.json` 是**脱敏摘录**, 只有 `agents` + `tools` 两段。合并步骤:

1. 备份旧机的 `openclaw.json` → `openclaw.json.bak.$(date +%s)`
2. 用 `config/openclaw.agents.json` 的 `agents` 段**替换**新机 `openclaw.json` 的 `agents` 段
3. 把占位符 `<OPENCLAW_HOME>` 换成实际路径 (`~/.openclaw`), `workspace` 段按 §4 步骤 2 改
4. ★**`model` 必须改成 `minimax/MiniMax-M3.1-Flash`** ⇒ ★**本文件里的 `minimax/MiniMax-M3` 是过期的** —— M3 已被实测**挂 token plan 上限** (10-28 17:19 起所有失败都是它) ⇒ **照抄会让新主机一开局就撞同一个坑**
5. ★**`tools.sessions.visibility`** 保留 `all` (三个总工要看彼此的 needs_from)
6. ★**`tools.agentToAgent.allow`** 保留四个 id —— 但**注意**: 三个总工的 `deny: ["sessions_send"]` + `guards/` shim 是**三层守卫**的最后一层 ⇒ ★**guards 一定要装**(步骤 3), 否则**跨 agent 通信禁令失效** (10-25 压测实证: 绝对路径调用**真的**能把消息投进对方会话)

---

## B7 ★★给闸门补规则 (★2026-11-01 21:3x **已实装并实测通过**)

**原状实测**: `state/publish_github.sh` 的真值反查只扫 `openclaw.json` + **main 一个** agent 的 `auth-profiles.json`, 且**只认字段名** (`key|token|secret|password`) ⇒ ①三个子 agent 的 key **漏检** ②字段名一改就绕过。

**★已补的三条规则 (已落盘, 已在发布树实测)**:

| # | 规则 | 实现 |
|---|---|---|
| 1 | **扫全部四个 agent 的 auth-profiles + models.json** | `glob(~/.openclaw/agents/*/agent/{auth-profiles,models}.json)` (原来只扫 main 一个) |
| 2 | ★**值形态规则** (不依赖字段名) | `sk-cp-` / `sk-ant-` / `tvly-` / `ghp_` / `github_pat_` / `sk-proj-` / `AKIA` / `o9cq`(微信 openid) —— ★**字段名能被改, 值形态改不掉** |
| 3 | 设备口令**上下文**匹配 | `sshpass -p X` / `密码: X` (规则由本地真值动态生成, 脚本里无明文) |

**★补规则的当场战果 (证明这规则不是摆设)**: 一加上就抓出 **7 处真实泄漏** ——
| 位置 | 泄漏内容 | 处置 |
|---|---|---|
| `config/agents/main/memory/2026-11-01.md` | 我写闸门缺陷说明时**抄了 openid 原文** | 已脱敏成 `<WECHAT_OPENID_REDACTED>` (源 + 副本) |
| `config/agents/main/memory/2026-10-30.md` | 同上 (上一轮的原文) | 同上 |
| `config/agents/main/memory/2026-06-11.md` | 老日记里的 openid | 同上 |
| `config/skills-global/.trash_热点检索输出报文_20260618/**` (4 文件) | 技能文档里的 RECIPIENT 常量 | ★**整个 `.trash_` 垃圾目录已删** |
| `config/agents/main/memory/2026-08-13.md` / `2026-07-26.md` | `sshpass -p '<口令>'` | 已脱敏成 `<BOARD_SSH_PASSWORD>` |
| `HW/AGENT_MIGRATION_PLAN.md` (本文) | ★**我自己写迁移方案时抄了口令举例** | 已脱敏 —— ★**同一个错犯了第三次, 见下** |

**★自测结果**: 真实发布树 **0 命中** (485 文件) + 故意造 5 类泄漏 (sk-cp / tvly / ghp_ / 微信 openid / AKIA) **全部被抓到**。

**★★★ 同一个错我犯了第三次 —— 必须写进铁律**:
> 描述"某处有凭据"的时候, **不要把凭据原文抄进文档**。前两次是 `TASK_BOARD.md` §7, 这次是本文 —— ★**都是"举例子"举出来的** ⇒ **一律用 `<占位符>` 代替**, 并在括号里说明"这里本来是什么"。

## B8 未决项

| # | 未决 | 卡在谁 | 说明 |
|---|---|---|---|
| 1 | **旧主机是否继续跑?** | 老板 | ★**两边同时跑会互相覆盖分片** ⇒ 建议旧主机只留 GitHub 推送或干脆停 |
| 2 | **"队列自动派活" cron 当前是 disabled** | 老板 | 实测 `enabled=false` (非自动失败, 是被手动关的) ⇒ **迁过去时要不要恢复?** 建议恢复 (它是对话断线时的兜底) |
| 3 | **凭据带外通道** (scp / 密码管理器 / 加密包) | 老板 | 4 个文件, 我倾向 **scp 直传 + 落地后删源** 或 **1Password/Bitwarden** |
| 4 | **新主机的 GitHub 推送身份** | 老板 | 新主机需要 SSH key; 若旧机保留 ⇒ 明确单一推送方 |
| 5 | **session 历史要不要搬** | 老板 | `agents/*/sessions/*.jsonl` 共 120 个会话文件 (含历史上下文) ⇒ 搬过去可保留对话连续性, 但**体积大且含凭据痕迹** ⇒ 我建议**只搬 main 的最近几条**, 其余不搬 |

---

## 附: 一句话给老板

**"项目库本体早就在 GitHub 上了, 那台主机 clone 一下就有了 90%; 缺的是 agent 的'人格 + 记忆 + 守卫'85 个文件, 我可以补推。★但有 4 个文件带凭据(设备口令 / minimax API key / gateway token / 微信 openid)绝对不能进公开仓库, 要走带外; 而且现在的闸门**抓不到 auth-profiles 里的 API key**(实测漏检), 得先补规则再迁 —— 否则新主机一上手就在裸奔。"**
