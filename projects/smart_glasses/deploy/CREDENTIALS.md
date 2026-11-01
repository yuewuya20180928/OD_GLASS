# 凭据文件说明 —— ★这 4 个文件绝不能进 GitHub

> 仓库是**公开的** (`yuewuya20180928/OD_GLASS`, 免登录可读) ⇒ 推上去 = 泄给所有人。
> ⇒ **带外通道**传: scp / 密码管理器 / 加密包,三选一。

---

## 4 个文件

| 文件 | 旧主机路径 | 含什么 | 缺了会怎样 |
|---|---|---|---|
| **openclaw.json** | `~/.openclaw/openclaw.json` | gateway auth token (48 字符) + tavily webSearch apiKey | 网关拒绝连接 / 搜不了网 |
| **TOOLS.md** | `~/.openclaw/workspace/TOOLS.md` | 板子 SSH **明文口令** + 内网 IP + 板端路径 | 板子连不上 (算不了实测) |
| **auth-profiles.json** | `~/.openclaw/agents/main/agent/auth-profiles.json` | **minimax API key** (`sk-cp-...`) | ★**agent 起来了但调不了模型** |
| **jobs.json** | `~/.openclaw/cron/jobs.json` | 微信 openid (推送目标) + 全部 cron payload | 收不到微信推送 / cron 要手工重建 |

---

## 怎么传

```bash
# 旧主机上打包 (临时)
cd ~/.openclaw
tar czf /tmp/ars45-credentials.tar.gz \
    openclaw.json \
    workspace/TOOLS.md \
    agents/main/agent/auth-profiles.json \
    cron/jobs.json

# 传到新主机
scp /tmp/ars45-credentials.tar.gz new-host:~/ars45-transfer/

# 新主机上解开到 credentials/
cd ars45-deploy-YYYYMMDD-HHMM
tar xzf ~/ars45-transfer/ars45-credentials.tar.gz -C /tmp/cred_tmp
cp /tmp/cred_tmp/openclaw.json \
   /tmp/cred_tmp/workspace/TOOLS.md \
   /tmp/cred_tmp/agents/main/agent/auth-profiles.json \
   /tmp/cred_tmp/cron/jobs.json \
   credentials/
rm -rf /tmp/cred_tmp
```

---

## ★传完之后

1. **旧主机上删掉临时包** (`rm /tmp/ars45-credentials.tar.gz`) —— 它是明文凭据
2. **新主机上清空 `credentials/`** (装完就没用了) —— 别把明文凭据留在盘上
3. **旧主机的 cron 停掉** (详见 README.md) —— 这条最要紧

---

## ⚠️ 一个已经踩过的坑 (别重踩)

**描述"某处有凭据"的时候,不要把凭据原文抄进文档。**

这个错我犯了三次:发布脚本里拆拼硬编码 → `TASK_BOARD.md` 举例 → 迁移方案书举例。
⇒ **一律用 `<占位符>` 代替**, 在括号里说明"这里本来是什么"。

⇒ ★**说明性文档不是豁免区** —— 仓库一公开, 文档里的举例就是泄漏。
