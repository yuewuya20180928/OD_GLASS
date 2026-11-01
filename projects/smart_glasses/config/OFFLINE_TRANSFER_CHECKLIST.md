# 带外传输清单 —— ★这 4 个文件含凭据, **绝对不能进 GitHub**

> 生成: 2026-11-01 21:2x (项目总工) · 配套 `HW/AGENT_MIGRATION_PLAN.md`
> ★**仓库是公开的** (yuewuya20180928/OD_GLASS, 免登录可读) ⇒ 推上去 = 泄给所有人

| 文件 | 含什么 | 怎么带 |
|---|---|---|
| `~/.openclaw/openclaw.json` | gateway auth token (48 字符) + tavily apiKey | ★scp 直传 / 密码管理器 / 加密包 (三选一) |
| `~/.openclaw/workspace/TOOLS.md` | 板子 SSH 明文口令 | ★scp 直传 / 密码管理器 / 加密包 (三选一) |
| `~/.openclaw/agents/main/agent/auth-profiles.json` | minimax API key (sk-cp-...) | ★scp 直传 / 密码管理器 / 加密包 (三选一) |
| `~/.openclaw/cron/jobs.json` | 微信 openid (推送目标) + 全部 cron payload | ★scp 直传 / 密码管理器 / 加密包 (三选一) |

## ★为什么它们不在仓库里 (11-01 20:5x 的教训)

- 上一版发布脚本把微信 openid **拆拼**后硬编码在自己里 (`"前半" + "后半"`) ⇒ 拆拼骗过了'自己扫自己'，但**两段明文都在会被公开的脚本里** ⇒ grep 一下就拼得回来 ⇒ **等于把凭据发到公开仓库**。
- ⇒ 现在的规则: **脚本里一个敏感串明文都不写**，全部从**本地不入库的真值源**现读 (`~/.openclaw/openclaw.json` / `cron/jobs.json` / `TOOLS.md`)。

## ★★落地后必做 (在新主机上)

```bash
# 1. 铺好凭据文件
cp <带外传来的>/openclaw.json            ~/.openclaw/
cp <带外传来的>/TOOLS.md                ~/.openclaw/workspace/
cp <带外传来的>/auth-profiles.json      ~/.openclaw/agents/main/agent/
cp <带外传来的>/jobs.json               ~/.openclaw/cron/
# 2. ★把 agents 段合进 openclaw.json (别直接覆盖!) —— 见 AGENT_MIGRATION_PLAN.md §6
# 3. ★验证闸门抓得住 (反向自测)
cd ~/.openclaw/workspace/projects/smart_glasses && python3 state/publish_github.sh --selftest
```

## ★★旧主机的处置 (★顺序不能反)

1. **先停旧主机的 cron** (否则两边同时派活 ⇒ 互相覆盖分片)
2. 再在新主机开 cron (每个 job 带 `model=minimax/MiniMax-M3.1-Flash`)
3. ★旧主机的 `TOOLS.md` / `auth-profiles.json` **带完之后从旧机删掉或降权** (它们是全机凭据)
