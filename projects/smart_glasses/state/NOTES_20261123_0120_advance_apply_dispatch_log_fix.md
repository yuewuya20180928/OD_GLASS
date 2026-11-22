# ★main 自修笔记 · `state/advance.py --apply` 落盘路径 (2026-11-23 01:2x · cron 775d9893)

> ★**性质**: ★**项目总工 (moli) 修自己的派活工具 · 零写板 · 零外发 · 零代拍**★

---

## ① 病灶 (★本机实读 + 实跑, 非推测★)

★**本 job (cron 775d9893「继续执行后继计划」) 步骤 2 的落盘手段是**:
```bash
python3 state/advance.py --apply --only <ISS-ID>     # 派完把该 issue 标 fixing + 写派活日志
```
★**这条路一直是坏的**:

| 证据 | 读数 |
|---|---|
| `state/dispatch_log.yaml` 顶层类型 | **list** (不是 dict) · 334 条 · 291 KB |
| `state/advance.py` 旧代码 | `dl.setdefault("dispatches", []).append(...)` ⇒ **AttributeError: 'list' object has no attribute 'setdefault'** |
| 后果 | ★**「派完标 fixing + 写派活日志」这一步从来没自动跑通过** ⇒ 兄弟 job (fb67 队列派活) 只能绕开它、自己用原子写落 `fixing` ⇒ 两个 job 各写各的 |
| 反向用例 | ★**用修复前的备份跑同一沙盒 ⇒ 确实复现 AttributeError** (⇒ 这条回归用例抓的是真事故, 不是自造的假 bug) |

---

## ② 修法 (★修在产生点, 不在产物上擦★)

★**只改 `state/advance.py` 一处, 判据/阈值/排序一个字没动**:

1. ★**两种形状都认** ⇒ `list` ⇒ 直接追加; `dict` ⇒ 走 `dispatches` 键 ⇒ 写回时保持原形状。
2. ★**追加式写回** ⇒ 新条目用 `yaml.safe_dump([entry])` **追加到文件尾** ⇒ ★**历史 291 KB 字节零改动** (零 churn)。
3. ★**空跑零写** ⇒ 只有【真有新派活】或【日志文件不存在】才写盘 ⇒ 空跑连 md5 都不变。
4. ★**写回后自检** ⇒ 重新加载核对「条目数 = 旧数 + 新增数」+「末条 = 刚写的那条」⇒ 不一致 ⇒ `sys.exit(2)` ⇒ ★**不许静默写坏日志**。

★**备份**: `state/.bak_advance_20260723_0120_pre_dispatchlog_fix.py` · `state/.bak_dispatch_log_20260723_0120_pre_fix.yaml`

---

## ③ 单测 (★本项目铁律: 晋级判据必须写成独立脚本 + 单测★)

★**新文件**: `state/test_advance_apply_dispatch_log.py` (★端到端跑真 `advance.py`, 不只测纯函数★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 -B state/test_advance_apply_dispatch_log.py
```

| 用例 | 验什么 | 结果 |
|---|---|---|
| T1 | **list 形状** dispatch_log ⇒ `--apply --only` 正常落盘 (★旧代码在这条上崩★) | ✅ |
| T2 | **dict 形状** dispatch_log ⇒ 同样正常落盘 (两种形状都认) | ✅ |
| T3 | `--only` 过滤 ⇒ 只有指定单标 fixing, 另一条仍 open, 只追加 1 条日志 | ✅ |
| T4 | internal 为空 ⇒ 空跑 ⇒ **dispatch_log 字节零变化** (零 churn) + 不崩 | ✅ |
| T5 | ★**反向用例** ⇒ 用【修复前】备份跑同一沙盒 ⇒ 必须复现 AttributeError | ✅ |

★**实跑结果**: `✅ ALL TESTS PASS (5/5)` · rc=0

---

## ④ 真盘实跑 (★修完必须在真盘上验一遍★)

```bash
python3 state/advance.py --apply          # ★本轮 internal 为空 ⇒ 应为空跑★
```

| 项 | 跑前 md5 | 跑后 md5 | 判定 |
|---|---|---|---|
| `state/dispatch_log.yaml` | `4e4e3b87b713e436ad1685481682b8d7` | `4e4e3b87b713e436ad1685481682b8d7` | ★**字节零变化** (空跑零 churn)★ |
| `state/issue_log.yaml` | `4a75ac43ad05e39dcda3ed73af8e74c9` | `4a75ac43ad05e39dcda3ed73af8e74c9` | ★**未动**★ |
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**板未动** (mtime 仍是 2026-11-06 07:07:17.362193413)★ |

★**旧代码在这一步会直接抛 AttributeError** ⇒ 现在 rc=1 (★「无可执行动作」的正常退出码★) + 三项 md5 全不变 ⇒ 修好了。

---

## ⑤ ★★【跨 job 基础设施红】/tmp 的 userquota 被打满 (2026-11-23 01:1x 实测)★★

★**这不是板的问题, 是整台机器的作业面问题**:

| 证据 | 读数 |
|---|---|
| `/tmp` 挂载 | `tmpfs on /tmp type tmpfs (rw,nosuid,nodev,nr_inodes=1048576,inode64,**userquota**)` · 7.5 G · 系统层 df 显示 1.5 G 可用 |
| ★**用户配额**★ | ★**已打满** ⇒ 实测 `cp` 一个 14 KB 文件就报 `Disk quota exceeded`; `dd` 写 20 M 报 `IO error: Disk quota exceeded`; `mkdir` 能建但**写不进文件**★ |
| ★**假读数后果**★ | ★**本 job 跑 `issue_check.py` 时把 stdout 重定向到 /tmp ⇒ 拿到 `rc=120` + 输出 0 字节** ⇒ ★**差点被当成「闸崩了」读** (直接跑同一条命令 rc=1 + 341 条清单正常出) ⇒ ★**任何把门禁输出落到 /tmp 的写法都会出假读数**★ |
| 占用大头 | ★**`/tmp/od_glass_publish` 4.1 G** (★5 小时 GitHub 同步 job 的发布暂存目录 · `.git/FETCH_HEAD` 01:15 还在被写 ⇒ **那个 job 此刻正在跑** ⇒ **不许此刻动它**★) + ★**`/tmp/adv_sandbox` 680 M** (00:56 起 · 子 agent 正在用)★ |
| 本 job 已自救 | ★**新写的单测沙盒从 /tmp 改落项目盘** (`state/.tmp_advselftest/` · 用完即删) ⇒ 不再吃 /tmp 配额★ |

★**建议 (交老板 / 交 GitHub 同步 job 的 owner)**:
1. ★**发布暂存目录不要长期占着 /tmp** ⇒ 推完即清, 或把暂存目录改到项目盘 (`/home/yuewuya/.openclaw/workspace/...`) ⇒ ★**否则 5 小时 job 的 rsync 会继续在 EDQUOT 上失败, GitHub 推不出去**★
2. ★**子 agent 沙盒一律落项目盘, 不落 /tmp** ⇒ 本 job 的单测已按这条改
3. ★**门禁命令的输出不许重定向到 /tmp** ⇒ 直接跑或落项目盘 ⇒ ★**假读数 (rc=120 / 0 字节) 会把「闸红」和「闸崩」混成一团**★

---

## ⑥ 边界自证

- ★**零写板** ⇒ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 前后一致
- ★**零改他 agent 的分片** ⇒ 只动 `state/advance.py` + 新增 `state/test_advance_apply_dispatch_log.py` + `state/issue_log.yaml` (加 2 条 main 自有条目)
- ★**零改判据** ⇒ `advance.py` 的 internal/approvals/decisions/waiting 四段判据与阈值一个字没动
- ★**零外发 / 零代拍** ⇒ 本单不发邮件、不联系供应商、不替老板拍板
- ★**不改 `PROJECT_TRACKER.md` §0 锁死表** ⇒ 没碰
