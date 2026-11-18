# ARS45 智能眼镜 · 4-Agent 职能制 —— 部署包

> 把这个包拷到新主机,解压,跑 `./install.sh` 就完事。**连 GitHub 都不用**(项目库快照已在包里)。

---

## 三步走

```bash
# ① 解压
tar xzf ars45-deploy-YYYYMMDD-HHMM.tar.gz
cd ars45-deploy-YYYYMMDD-HHMM

# ② 把 4 个凭据文件放进 credentials/ (★含机密, 走带外通道)
scp <旧主机>:~/.openclaw/openclaw.json                     credentials/
scp <旧主机>:~/.openclaw/workspace/TOOLS.md               credentials/
scp <旧主机>:~/.openclaw/agents/main/agent/auth-profiles.json credentials/
scp <旧主机>:~/.openclaw/cron/jobs.json                    credentials/

# ③ 部署
./install.sh
```

装完重启网关,起 TUI:

```bash
systemctl --user restart openclaw-gateway
openclaw agents list      # 应看到 4 个 agent
openclaw cron list        # 应看到 7 个 job
openclaw tui              # 接管
```

---

## 装了什么

| 项 | 内容 |
|---|---|
| **项目库** | `projects/smart_glasses/**` (含 issue 台账 125 条 / 4 个 agent 分片 / 41 份交卷单) |
| **agent 人格** | 四个 agent 各自的 `SOUL.md` / `IDENTITY.md` / `USER.md` / `MEMORY.md` + 岗位说明书 `AGENTS.md` |
| **agent 记忆** | main 的 **48 篇日记** (2026-06 ~ 2026-11) |
| **guards** | 三个总工的 PATH shim —— ★**跨 agent 通信禁令依赖它**, 不装禁令会失效 |
| **skills** | 项目级 3 个 (`smart-glasses-pm` / `smart-hardware-reference` / `qa-requirement-review`) + 全局 2 个 (`state-protocol` / `nimo-glasses`) |
| **agent 配置** | `openclaw.json` 的 `agents` 段 (★只合并这一段, 不覆盖凭据) |
| **cron** | `jobs.json` (★**拷文件即可, gateway 启动自动读**, 不用逐条 `cron add`) |

---

## ⚠️ 三件必须注意的事

### 1. ★旧主机的 cron 要**先停**
```bash
# 在旧主机上 (★必须是第一步!)
openclaw cron disable <jobId>   # 7 个全停
```
**理由**: 两边同时派活 ⇒ 同一个 agent 两个写会话 ⇒ **互相覆盖分片**
(2026-10-29 第三例撞车: 两条都 0 产出)。

**旧主机的 GitHub 同步 cron 也要停** ⇒ 只留一个推送方, 否则两边 `state/` 是两份会漂移。

### 2. ★只有**一份**项目库
三个子 agent 的 `projects/` 是**软链**指到同一处。安装器会校验四个 inode 一致 —— 不一致就停下报错。
**绝不能出现四份分叉**, 否则合并时冲突爆炸。

### 3. ★绝不拷 `jobs-state.json`
那是运行时 pending slot(带旧状态), 会串。只拷 `jobs.json`。

---

## 参数

```bash
./install.sh --check          # 只体检, 不改任何东西
./install.sh --offline        # 强制只用包内快照, 完全不联网
./install.sh --repo <URL>     # 指定项目库地址 (默认 GitHub)
./install.sh --home <dir>     # 指定 OPENCLAW_HOME (默认 ~/.openclaw)
```

---

## 装完怎么验证

安装器最后会跑四道门, **数字必须与旧主机一致**:

```
merge rc=0 (冲突 0) · Q1 18/18 · 违规 0 · G2 结构样机装配 (还差 7 项)
```

对不上 ⇒ 回来找项目总工。

---

## 出问题先看

| 现象 | 多半是 |
|---|---|
| `没装 openclaw` | `npm i -g openclaw` |
| `openclaw 还没初始化过` | 先跑一次 `openclaw configure` |
| `clone 失败` | 没配 SSH key ⇒ 会自动退 HTTPS; 都不行就查网络/代理 |
| `找不到项目库` | 包不完整 ⇒ 用 `--repo` 从 GitHub 拉 |
| `inode 不一致` | 软链没建对 ⇒ 停下别继续, 找我 |
| agent 起来了但调不了模型 | `auth-profiles.json` 没到位 (minimax API key) |
| 收不到微信推送 | 微信 context token 过期 ⇒ 在微信给机器人发一句话即恢复 |
