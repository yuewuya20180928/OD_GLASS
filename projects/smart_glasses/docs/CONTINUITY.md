# docs/CONTINUITY.md —— 换终端续传手册 (把本项目搬到另一台机器)

> **回答那个问题**: "复制到另一个终端, 是不是让另一个终端从 GitHub 拉最新资料然后继续执行就行?"
> **答案: 方向对, 但只覆盖一半。** GitHub 里是**任务与进展** (可复现、可审计), 但**配置 / 记忆 / 环境**有 4 类东西不在仓库里 —— 这份手册把缺什么、怎么补写清楚。

---

## 0. 一句话总览: 什么能自动迁移, 什么不能

| 层 | 内容 | 在 GitHub? | 迁移方式 |
|---|---|---|---|
| **任务与进展** | `TASK_BOARD.md`(总表) · `PROGRESS_SNAPSHOT.md` · `PROJECT_TRACKER.md`(决策与理由) · `state/issue_log.yaml`(119+ 条问题台账) · `STATE.yaml` · 三个总工的交付文档 · 101 个自证脚本 | ✅ 全在 | **git clone/pull 即可** |
| **岗位与机制** | `config/agents/{main,hw-lead,sw-lead,mech-lead}/AGENTS.md` (4 份岗位说明书 + 全部铁律) · `config/openclaw.agents.json` (agent 定义) | ✅ 在仓库 | clone 后拷进 `~/.openclaw/agents/<id>/` |
| **长期记忆与教训** | `MEMORY.md` (135KB) · `memory/*.md` (46 天) | ❌ **不在仓库** | ★**不能推** (含内网 IP 与设备密码) ⇒ 改用 `docs/DECISIONS_DIGEST.md`(脱敏摘要) + 本手册 |
| **网关/渠道配置** | `~/.openclaw/openclaw.json` (插件·渠道·模型·API key) · `~/.openclaw/openclaw-weixin/` (微信账号 token) | ❌ 不能推 (含密钥) | 用 `config/openclaw.json.template` 骨架重建 + 微信重新登录 |
| **cron 任务** | 6 个定时任务 (队列派活 / GitHub 同步 / 每日巡检 / 继续执行后继计划 / **token 守护** / 周交付窗口) | ❌ 不在仓库 | 用 `config/cron_jobs.template.json` 重建 (占位符替换) |
| **运行环境** | conda env `rknn` (rknn-toolkit2 2.3.2) · COCO val2017 + 标注 · 校准集 `~/Public/radxa_yolo/calib_yolov5_100` · 模型 `yolov5s-sim.onnx` | ❌ (数据集太大) | 脚本 `state/bootstrap_new_terminal.sh` 会逐项体检并给补法 |

**覆盖率**: 任务与进展 **100%** · 配置 **需手工重建 3 件** · 记忆 **有脱敏摘要代替** · 环境 **需重装**。

---

## 1. 第 1 步: 拉仓库 + 认路径

```bash
git clone git@github.com:yuewuya20180928/OD_GLASS.git ~/od_glass
cd ~/od_glass/projects/smart_glasses        # ★项目根目录 = 这层
```
★**注意绝对路径**: 本机的 workspace 是 `/home/yuewuya/.openclaw/workspace/projects/smart_glasses`; 换机后所有 `state/*.py` 与 cron payload 里的路径都要改 ⇒ 见第 3 步。

## 2. 第 2 步: 环境体检 (一条命令)

```bash
bash state/bootstrap_new_terminal.sh          # ★只读体检, 不改任何东西
```
它会逐项检查并给出结论:
| 检查项 | 需要的 | 缺了怎么办 |
|---|---|---|
| python3 / yaml / requests | ≥3.10 | `pip install pyyaml requests` |
| conda env `rknn` + rknn-toolkit2 | 2.3.2 | `conda create -n rknn python=3.10 && pip install rknn-toolkit2==2.3.2` |
| onnx / onnxruntime / numpy | 1.14 / 1.26 | `pip install onnx onnxruntime numpy` |
| COCO val2017 + `instances_val2017.json` | 有标注 | 下载 COCO 2017 (val 约 1GB) |
| 校准集 100 张 + `dataset.txt` | `~/Public/radxa_yolo/calib_yolov5_100` | `python3 SW/tools/rknn_bench.py calib` 可自动生成 |
| 模型 `yolov5s-sim.onnx` | sha256 前 16 位 = `20368be665f6f59a` | 从模型资产库取 (见 `SW/MODEL_ASSETS.md`) |
| 4 道门能跑 | merge/gate_check/issue_check/daily_check rc=0 | 直接 `python3 state/daily_check.py` |

## 3. 第 3 步: 重建配置 (3 件)

### 3.1 网关配置
```bash
cp config/openclaw.json.template ~/.openclaw/openclaw.json
# 把 <...> 占位符换成真值: tavily apiKey / 微信账号 / gateway token
```
★**密钥绝不入库** —— 发布脚本的"真值反查"闸门会扫描整棵发布树, 命中即中止推送 (现在还额外扫内网 IP / 设备密码 / 微信 openid)。

### 3.2 四个 agent
```bash
mkdir -p ~/.openclaw/agents/{main,hw-lead,sw-lead,mech-lead}
for a in main hw-lead sw-lead mech-lead; do
  cp config/agents/$a/AGENTS.md ~/.openclaw/agents/$a/AGENTS.md
done
cp config/openclaw.agents.json ~/.openclaw/agents/          # ★改里面的 workspace 绝对路径
```
★**4 个 agent 的岗位说明书/铁律就在 `config/agents/*/AGENTS.md` 里** —— 这是"换机后最容易丢、但最影响质量"的东西。

### 3.3 cron 任务 (6 个)
```bash
cp config/cron_jobs.template.json ~/.openclaw/cron/jobs.template.json
# 用 openclaw 的 cron 管理把 6 条任务建出来 (把 <WEIXIN_TO_ID> 换成老板的微信 ID)
```
★**最关键的是「token 守护」那一条** (每 15 分钟): 它是老板 09:59 定的"限额用完前推进度"机制的执行者 —— 没有它, 换机后照样会断电丢信息。

## 4. 第 4 步: 续传协议 (断电/换机后照这 4 步走)

1. `git pull` ⇒ 读 `TASK_BOARD.md`: **§1 = 老板最新任务** · **§2 = 谁在干什么** · **§3 = 等老板的**
2. 读 `PROGRESS_SNAPSHOT.md` (自动生成的实时快照, 数字不写死) ⇒ 确认最新状态
3. 读 `PROJECT_TRACKER.md` §(1.3x~1.4x) ⇒ 拿到**决策与理由** (为什么是现在这个方案)
4. 读 `docs/DECISIONS_DIGEST.md` ⇒ 拿到**铁律与教训** (换机后最容易重犯的坑)
5. ★**先落盘, 再干活**: 老板的任务先登记到 `TASK_BOARD.md` + `state/issue_log.yaml`, 再动手

## 5. 换机后最容易重犯的 4 个坑 (都在 AGENTS.md 里, 这里再列一遍)

| # | 坑 | 后果 | 现在的防线 |
|---|---|---|---|
| 1 | **收到老板的任务不先落盘, 直接开干** | 10-29 09:59 的任务在 10:02 断电 ⇒ **8.7 小时零产出** | `TASK_BOARD.md` 总表 + `PROGRESS_SNAPSHOT.md` + token 守护 cron |
| 2 | **一个 agent 开两个写会话** (手动派活与队列 cron 撞车) | 两条单一起 0 产出 (10-29 撞了 3 次) | 铁律: **先落 `fixing` 再 spawn**; spawn 后 `subagents list` 核对 |
| 3 | **子 agent 交卷自推 `fixed` 覆盖项目总工的 `verified`** | 验收结论被回退 | 派活模板加"若已 verified 不得回退" + 每次跑 `state/alignment_check.py` |
| 4 | **写死的数字必然过期** (总表/快照/文档里的数) | 看板误导老板 | 所有数字**实时读**; `alignment_check.py` 每次汇报前跑 |

## 6. 一键自检 (每次汇报前)

```bash
cd <项目根>
python3 state/alignment_check.py     # ★rc=0 = 总表/台账/门禁/GitHub 全对齐
python3 state/daily_check.py         # 巡检 + 漂移检测
./status.sh                          # 一屏: 进展/待办/卡点/风险
```

## 7. 一句话总结

> **GitHub = 任务与进展 (100% 可迁移)**; **AGENTS.md = 岗位与铁律 (随仓库走)**; **决策与教训 = 脱敏摘要 `docs/DECISIONS_DIGEST.md`**; **配置与 cron = 用模板重建**; **环境与数据集 = 脚本体检后按提示补**。
> ⇒ **换终端不是"拉下来就能跑", 是"拉下来 + 补 3 件配置 + 装 2 样环境"; 但也不用重做任何一个决策。**
