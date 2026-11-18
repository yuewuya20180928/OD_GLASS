# 待推送清单 (GitHub 网络受阻时的保险记录)

> **生成**: 2026-10-29 00:59 · **状态**: GitHub git-pack 传输被掐 (SSH 认证通 / api.github.com 200 / pack 传输断)
> ⇒ 本次**未推送任何内容** (发布脚本的保险生效: fetch 失败即中止, 不推陈旧数据、不毁远端历史)
> ⇒ **恢复方式**: 网络恢复后跑 `bash state/publish_github.sh "主控选型改令 + 15候选扩展报告"` 即可; 或等 cron 自动重试 (`13,43 * * * *`, 每 30 分钟一次)

## ★ 本轮未推送的关键内容 (按重要性)

| # | 文件 | 内容 |
|---|---|---|
| 1 | `HW/SOC_BACKUP_TOP5X3.md` (19.5KB) | ★**TOP5 厂家 × TOP3 = 15 候选扩展选型报告** (老板 10-29 00:49 改令) |
| 2 | `PROJECT_TRACKER.md` | §(1.38) 主控选型改令 + §0 变量 4 与主控选型策略行改写 |
| 3 | `state/issue_log.yaml` | ISS-108 扩展交付记录 (15 候选 + 3 家新检索事实) |
| 4 | `state/fragments/hw.yaml` | `soc_backup_candidates` → 15 候选清单 |
| 5 | `state/outbox/README.md` | ★**4 封酷芯微草稿暂停** (代理信 + 第二/三轮) + 发信顺序表改写 |
| 6 | `HW/SOC_BACKUP_TOP5.md` | 上一版 (2 厂家 5 芯片) 标注"已被取代" |
| 7 | `state/_soc_top5x3_report.py` | 扩展报告生成器 (可复现) |
| 8 | `state/publish_via_api.py` | API 通道发布器 (备用; ★缺 token, 当前走不通) |
| 9 | `state/daily_check.py` + `state/publish_github.sh` | ★**退出码分级修复** (巡检异常=3 不再中止发布) + fetch 超时 + 浅克隆降级 |

## ★ 未推送的更早内容 (同一批被卡的)
- `HW/POWER_SHUTDOWN_V3.md` §0/§2/§3 —— ★**P0 拓扑修复** (Q_PG: N-MOS 低边 → **P-MOS 高边 + 漏极接 BAT_SW**)
- `state/gen_netlist.py` V1.9 + `HW/netlist_v1.csv` + `HW/BOM_v1.csv` —— 网表/BOM 重生成 (390Ω 统一)
- `state/check_netlist.py` + `state/test_netlist_drc.py` —— 门禁判据加固 (9/9)
- `state/test_frag_write.py` (16/16) + `state/test_stage_gate_decisions.py` (12/12) —— 两个工具自测
- `state/frag_write.py` —— `--set` 静默吞数据修复
- `state/stage_gate.py` —— ★**G0 假卡死修复** (判据认 `decision` 字段)
- `SW/POWER_STATE_SEMANTICS.md` + `SW/SW_REQUIREMENTS.md` —— ISS-104 交付 + U2 口径回写
- `state/issue_log.yaml` —— ISS-087/088/091/097/101/104/109 关单记录

## ★ 网络诊断结论 (2026-10-29 00:4x-00:59 实测)
| 通道 | 状态 |
|---|---|
| SSH 认证握手 | ✅ 通 (`Hi yuewuya20180928!`) |
| `api.github.com` | ✅ 200 / 0.35s |
| `git fetch` / `git clone` (git-pack 传输) | ❌ "unexpected disconnect while reading sideband packet" |
| 浅克隆 `--depth=1 --filter=blob:none` | ⚠️ 偶尔能过 (00:3x 成功过一次), 多数超时 |
| 浅克隆不带 filter (blob 全下) | ❌ 超时 |
| **结论** | **断的是 git 协议的数据传输层, 不是网络本身** ⇒ 等网络恢复即可, 无需改方案 |

★**发布脚本的两道保险已生效**: ① fetch/克隆失败 = 中止发布 (不推陈旧文档, 不毁远端历史) ② `git log` 查 HEAD 而非 main 分支。
