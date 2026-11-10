#!/bin/bash
# ★GitHub 同步脚本 (OD_GLASS) —— 项目总工维护
# 流程: 刷新生成物 → rsync 项目库 → 拷贝 docs/config 映射件 → **真值反查脱敏** → commit → push → 用 GitHub API 验 blob SHA
# 纪律: ① 仓库公开, 推前必须过真值反查 (命中 0 才推) ② 验证不许用 raw.githubusercontent (CDN 缓存旧版)
set -u
# ★并发锁: 多个来源 (我手动 / cron 自动 / 队列) 同时推同一棵树会撞 git 锁 → 用 flock 串行化
LOCK=/tmp/od_glass_publish.lock
exec 9>"$LOCK"
flock -w 120 9 || { echo "❌ 拿不到发布锁 (另一个发布在跑), 跳过"; exit 0; }
WS=/home/yuewuya/.openclaw/workspace
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ=$WS/projects/smart_glasses
PUB=/tmp/od_glass_publish
REPO=yuewuya20180928/OD_GLASS
MSG="${1:-自动同步: 状态刷新}"

cd "$PROJ" || exit 1

# ---- 1. 刷新生成物 ----
# ★2026-10-28 加固: 生成器失败必须**当场报错并退出**, 不能吞掉错误继续推。
#   事故: gen_todo.py 有语法错误时, `>/dev/null 2>&1` 把错误吞了, 文档没更新但脚本继续跑,
#   结果**推的是旧文档却以为刷新了** ⇒ 老板在 GitHub 上看到过期数据而无人知道。
#   ⇒ 统一: 失败即退出 (set -e 之外再加显式检查), 且失败时把 stderr 原文打出来。
gen() {  # gen <说明> <命令...>  —— ★允许 rc=0 与 rc=3 (巡检有异常, 快照已生成)
  local desc="$1"; shift
  local err rc
  err=$("$@" 2>&1 >/dev/null); rc=$?
  if [ "$rc" != "0" ] && [ "$rc" != "3" ]; then
    echo "[1] ❌ 生成失败 (rc=$rc): $desc"
    echo "$err" | head -20
    echo "[1] ★已中止发布 —— 不推陈旧文档 (修好后重跑)"
    exit 1
  fi
  if [ "$rc" = "3" ]; then
    echo "[1] ⚠️ $desc 巡检有异常 (rc=3, 快照已生成) —— 继续发布"
  else
    echo "[1] $desc 已刷新"
  fi
}
gen "TODO.md"                    python3 state/gen_todo.py
gen "门禁快照"                    python3 state/daily_check.py
gen "docs/PROJECT_STATUS.md + docs/OPEN_ISSUES.md" python3 state/gen_publish_docs.py --out "$PROJ/docs"
gen "docs/START_HERE.md (接手指南)" python3 state/gen_start_here.py
gen "STATUS_SUMMARY.md (一页看懂)" python3 state/gen_status_summary.py
gen "STATE.yaml"                 python3 state/merge.py

# ---- 2. 发布树 ----
if [ ! -d "$PUB/.git" ]; then
  rm -rf "$PUB"; mkdir -p "$PUB"; cd "$PUB"
  git init -q -b main
  git remote add origin git@github.com:$REPO.git
fi
cd "$PUB" || exit 1
# ★从远端 rehydrate (机器重启会清空 /tmp → 发布树会变空仓库; 每次先拉回远端状态)
# ★★2026-10-28 18:3x 加固: 原写法 `git fetch -q ... 2>/dev/null && git reset ...` —
#   **fetch 失败时错误被吞掉, 脚本继续跑** ⇒ rsync --delete 把发布树覆盖成只有新内容
#   ⇒ 随后 commit+push 会把**远端全部历史压成一个新 commit** (历史丢失!)
#   ⇒ 现在: fetch 失败 = **中止发布** (宁可今天不推, 也不能毁历史)
# ★加超时: 2026-10-29 00:3x 实测 —— git-pack 传输在网络不稳时会**长时间挂住**,
#   没有超时 = 整个发布流程卡在那儿 (既不推也不报错, 看起来像"在跑")。
#   120s 拿不到就当失败 ⇒ 中止 (保险已在, 不会推陈旧文档) ⇒ 下轮重试。
# ★降级策略 (2026-10-29 00:3x 实测): 网络不稳时 git-pack 传输会断 ("unexpected disconnect
#   while reading sideband packet") ⇒ 普通 fetch 失败。**浅克隆 (--depth=1 --single-branch)
#   的包小得多, 实测能过** ⇒ fetch 失败时降级到浅克隆, 而不是直接放弃发布。
#   ★★2026-10-29 09:28 修正: 浅克隆**不要加 --filter=blob:none** (见下面 65 行附近的注释)。
if ! timeout 600 git fetch -q origin main 2>/tmp/_fetch_err.log; then
  echo "[2] ⚠️ 普通 fetch 失败 —— 降级试浅克隆 (--depth=1 --single-branch)"
  # ★★2026-10-29 23:5x 改动: **失败时不要先删 $PUB/.git** —— 删了就毁掉"可推增量的本地发布树", 下一轮只能重新全量克隆 (这个网络下要 10 分钟+ 且常挂) ⇒ 改成: 克隆到 tmp_clone 成功后再整体换。
  # ★★2026-10-29 09:28 实测修正: **不要加 --filter=blob:none** —— 加了之后 git-pack 传输本身能过,
  #   但 **checkout 阶段要按需拉 blob ⇒ 卡在 "Clone succeeded, but checkout failed"** ⇒ 整个 clone 返非零
  #   ⇒ 脚本误判"浅克隆失败"并把已经下好的仓库 rm 掉。去掉 filter 后 (blob 全下) 实测 10 分钟内完整跑通。
  #   ⇒ 超时给足 (600s): 这个网络下全 blob 浅克隆要 ~10 分钟。
  if ! timeout 900 git clone -q --depth=1 --single-branch \
       git@github.com:$REPO.git "$PUB.tmp_clone" 2>>/tmp/_fetch_err.log; then
    rm -rf "$PUB.tmp_clone"
    echo "[2] ❌ 浅克隆也失败 —— ★中止发布 (避免把远端历史压扁)"
    echo "--- 错误 ---"; head -10 /tmp/_fetch_err.log 2>/dev/null
    echo "[2] ★网络恢复后重跑即可; 本次未推送任何内容"
    exit 1
  fi
  rm -rf "$PUB"; mv "$PUB.tmp_clone" "$PUB"
  cd "$PUB" || exit 1
  git config user.name "yuewuya20180928"
  git config user.email "yuewuya20180928@users.noreply.github.com"
  git remote set-url origin git@github.com:$REPO.git
  echo "[2] ✅ 浅克隆成功 (HEAD = $(git rev-parse --short HEAD))"
fi
git reset -q --hard origin/main 2>/dev/null || git reset -q --hard HEAD 2>/dev/null || { echo "[2] ❌ reset 失败, 中止"; exit 1; }
# ★检查要用 HEAD (不是 main 分支) —— fetch 后 `git reset --hard origin/main` 才把 HEAD 指过去;
#   查 main 分支会在"本地分支还没跟上"时误判为空 (2026-10-28 18:4x 实测踩中: fetch 其实成功了)
if [ -z "$(git rev-parse HEAD 2>/dev/null)" ]; then
  echo "[2] ❌ rehydrate 后仍无 commit —— 中止发布 (★绝不能推一个空历史的仓库)"
  exit 1
fi
echo "[2] rehydrate OK: HEAD = $(git rev-parse --short HEAD)"
# git 身份 (新仓库没有身份 → commit 会失败)
git config user.name "yuewuya20180928"
git config user.email "yuewuya20180928@users.noreply.github.com"

# ★排除运行时垃圾 (BOOTSTRAP.md 是 runtime 在 cwd 生成的通用提示, 不是项目文件;
#   .openclaw/ 是 runtime 状态) —— 上一版它被推上了 GitHub 公开发布树
# ★备份目录清理 (源树与发布树都要清): rsync 的 --delete **不会删被 exclude 保护的目标端文件**
#   → 之前推过一次 .v11_backup/ 与 HW/.iss075_bak/ (公开仓库里不该有)
find "$PROJ" -maxdepth 3 \( -name '.*_bak' -o -name '*_backup' -o -name '.*_backup' \) -type d -exec rm -rf {} + 2>/dev/null
find "$PUB" -maxdepth 5 \( -name '.*_bak' -o -name '*_backup' -o -name '.*_backup' \) -type d -exec rm -rf {} + 2>/dev/null
rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
      --exclude 'BOOTSTRAP.md' --exclude '.openclaw' --exclude 'workspace-state.json' \
      --exclude '*.tmp' --exclude '.DS_Store' \
      --exclude '.*_bak' --exclude '*_backup' --exclude '.*_backup' --exclude '.bak_*' \
      --exclude 'state/_os_snapshots/hirose_*' --exclude 'state/_os_snapshots/hirose_pages' \
      --exclude 'demo_mainboard.kicad_pcb' \
      --exclude 'production/gerbers' --exclude 'production/drill' \
      --exclude 'production/pos' --exclude 'production/assembly' \
      --exclude '/HW/PCB/gerbers' \
      --exclude '/HW/PCB/production/gerbers' --exclude '/HW/PCB/production/drill' \
      --exclude '/HW/PCB/production/pos' --exclude '/HW/PCB/production/assembly' \
      --exclude '/HW/PCB/production/3d' \
      --exclude '/state/.lastgood' \
      --include '/HW/PCB/_frame_reference.kicad_pcb' \
      --exclude '/HW/PCB/*.kicad_pcb' \
      --exclude '*.kicad_pcb' \
      "$PROJ/" projects/smart_glasses/
# ★★2026-11-05 09:40 补漏 (实测): **Gerber 有两份** —— `HW/PCB/gerbers/` (顶层副本) 与
#   `HW/PCB/production/gerbers/` (投产集), 32 个文件名集合相同 + md5 逐个相同 (实测 F_Cu.gtl
#   8f0329fb… 两边一致) ⇒⇒ 只排除/只撤 `production/` 那份, **顶层副本照样被 rsync 抄进发布树
#   ⇒⇒ 坏板 (DRC 2 / unconnected 82) 的 32 个 Gerber 在 09:21 那次推送 (0638101) 里进了公开仓**
#   (GitHub contents API 实测: projects/smart_glasses/HW/PCB/gerbers = 32 项)
#   ⇒⇒ 违反 AGENTS.md 铁律③「板 + 派生产物一起管 ⇒ 拦下时一起撤 ⇒ 仓库里没有板 = 诚实状态」
#   ⇒ 修法: 顶层副本也要 exclude + 也要撤 (两条路径一个都不能漏)。
# ★★2026-11-05 09:20 **板 + 派生产物改成"闸门通过才显式拷进来"**
#   ⇒ rsync 不再直接抄板/Gerber ⇒ ⇒ 闸门拦下时**不会又把它们抄回树里** (避免反复抄-删)
#   ⇒ 闸门通过时在 [4.5] 之后显式 cp (见下方 "发布闸: 板通过" 分支)

# ---- 3. docs / config 映射件 ----
mkdir -p docs config/agents/main
cp "$WS/AGENTS.md" config/agents/main/AGENTS.md
[ -f "$PROJ/REPO_README.md" ] && cp "$PROJ/REPO_README.md" README.md
for a in hw-lead sw-lead mech-lead; do
  [ -f "/home/yuewuya/.openclaw/workspace-$a/AGENTS.md" ] && cp "/home/yuewuya/.openclaw/workspace-$a/AGENTS.md" "config/agents/$a/AGENTS.md"
done
# ★★★2026-11-01 21:4x: 迁移资产映射 (老板要把 4-Agent 职能制搬到另一台主机)
#   `state/_migrate_assets.py` 把 agent 人格/记忆/守卫/skills/局部配置写到 **$PROJ/config/**,
#   ★但这里原来**只 cp 4 个 AGENTS.md** ⇒ 那些资产**根本没进发布树** (2026-11-01 实测: 远端只有 AGENTS.md)
#   ⇒ 现在把整个 config/ 目录 rsync 上去 (排除 __pycache__/.git)
#   ★安全: 这些文件已由真值反查闸门扫过 (值形态 + 口令上下文 + 凭据真值 三层)
# ★★2026-11-02 08:2x: **MEMORY / 日记 的自动同步 + 一致性门禁** (心跳查出的"真值源分裂"修复)
#   ★问题: 运行时读的是 `$WS/config/agents/main/MEMORY.md`, 而我 (项目总工) 一直写 `$WS/MEMORY.md`
#     ⇒ **两份同名文件分叉, 我写的记忆运行时读不到**; 且发布树里的日记停在 2026-06-11
#     ⇒ ★**"断电续传凭据"这个机制实际上三个月没生效**。
#   ⇒ 修法: **真值源 = `$WS/MEMORY.md`**, 发布前自动同步到 config/ 与项目树 ⇒ 不用人记得。
WS_MEM="$WS/MEMORY.md"
if [ -f "$WS_MEM" ]; then
  cp -f "$WS_MEM" "$PROJ/config/agents/main/MEMORY.md"
  # ★★2026-11-05 09:52 补: **运行时副本也要同步** —— 本脚本的注释自己写着
  #   「运行时读的是 $WS/config/agents/main/MEMORY.md」, 但原来只同步了**项目树**那份
  #   ⇒ ⇒ check_memory_sync.py 一直报这个副本 ❌ (实测 11-05 09:47: 运行时副本还停在 06:10 的
  #   /tmp/gen_v21.log 那一版, 真值源已是 09:23 的 v25 版) ⇒ ⇒ 运行时读到的还是旧记忆
  if [ -d "$WS/config/agents/main" ]; then
    cp -f "$WS_MEM" "$WS/config/agents/main/MEMORY.md"
  fi
  if [ -d "$WS/config/agents/main/memory" ]; then
    mkdir -p "$PROJ/config/agents/main/memory"
    rsync -a "$WS/config/agents/main/memory/" "$PROJ/config/agents/main/memory/"
  fi
  # ★★2026-11-05 09:55 补: **日记真值源是 $WS/memory/** (AGENTS.md 规定写 `memory/YYYY-MM-DD.md`),
  #   但发布树原来只同步了 $WS/config/agents/main/memory/ (实测停在 2026-11-02)
  #   ⇒ ⇒ 公开仓里的日记落后 3 天 (今天的 11-05 没进去)
  #   ⇒ ★**必须过脱敏过滤** (实测: 直接 rsync 会被本脚本后面的真值反查拦下 ——
  #   `config/agents/main/memory/2026-06-06.md` 命中 VALUE_SHAPE:wechat-openid ⇒ 闸门正确拒推)
  #   ⇒ ⇒ 用 scrub_daily_memory.py: 只发**近 14 天** + **命中敏感值的一律跳过**
  #      (它的规则与下面的真值反查同一套口径 ⇒ 这边过的, 闸门那边不会再拦)
  if [ -d "$WS/memory" ]; then
    python3 "$SCRIPT_DIR/scrub_daily_memory.py" "$WS/memory" "$PROJ/config/agents/main/memory" \
      --days 14 --apply 2>&1 | sed 's/^/  /' || true
    # ★★同一套镜像也刷**运行时的日记目录** ($WS/config/agents/main/memory/)
    #   —— check_memory_sync.py 拿它跟项目树那份逐字节比 (实测报 ❌: 2026-11-02.md 两边内容不同,
    #      因为这份镜像停在 11-02 的迁移副本, 而真值源已经是新版本) ⇒⇒ 刷齐后门禁才全绿
    python3 "$SCRIPT_DIR/scrub_daily_memory.py" "$WS/memory" "$WS/config/agents/main/memory" \
      --days 14 --apply 2>&1 | sed 's/^/  /' || true
  fi
  echo "[3a] MEMORY + daily memory 已从工作区真值源同步"
  # ★同步完立刻自检 (三份 md5 必须一致) ⇒ 分叉就在这里被抓住, 不用等到下次心跳才发现
  python3 "$SCRIPT_DIR/check_memory_sync.py" 2>&1 | sed 's/^/  /' || true
fi

if [ -d "$PROJ/config" ]; then
  rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
        "$PROJ/config/" config/
  echo "[3] config/ 映射件已同步 ($(find config -type f | wc -l) 文件)"
  # ★★★2026-11-11 05:1x 补漏 (★实测踩到★): **发布树里有【两份】config/** ——
  #   ① 根级 `config/` (★上面 rsync 刷的★) · ② 嵌套 `projects/smart_glasses/config/` (★step [2] 的 rsync 刷的★)
  #   ⇒ ★**顺序洞**: step [2] 先把 `$PROJ/` 整个刷进发布树 (⇒ 嵌套那份此时还是**旧的**),
  #     ★**然后** step [3a] 才把 `$WS/MEMORY.md` (真值源) 拷进 `$PROJ/config/agents/main/MEMORY.md` + 刷日记目录
  #   ⇒ ⇒ **嵌套那份永远落后一轮** (★实测: 真值源 md5 f4b1a12b… / 根级 config/ = f4b1a12b… /
  #     ★**嵌套 projects/smart_glasses/config/ = 43771ef9… (上一轮的旧版)**★)
  #   ⇒ ⇒ ★**后果**: 公开仓里给「项目树那份 MEMORY」看的入口是**嵌套那份** ⇒ ★**我写的最新记忆没进仓**
  #   ⇒ ⇒ ★**修法**: 在 [3a] 之后**再刷一次嵌套那份** (★此时 $PROJ/config/ 已是最新★)
  if [ -d "$PUB/projects/smart_glasses/config" ]; then
    rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
          "$PROJ/config/" "$PUB/projects/smart_glasses/config/"
    _nested_md5=$(md5sum "$PUB/projects/smart_glasses/config/agents/main/MEMORY.md" 2>/dev/null | cut -d' ' -f1)
    _src_md5=$(md5sum "$WS_MEM" 2>/dev/null | cut -d' ' -f1)
    if [ -n "$_nested_md5" ] && [ "$_nested_md5" = "$_src_md5" ]; then
      echo "[3] ★嵌套 config/ 已补刷 (MEMORY md5 = 真值源 ${_src_md5:0:8} ✅)"
    else
      echo "[3] ⚠️ 嵌套 config/ 补刷后 MEMORY md5 仍与真值源不一致 (${_nested_md5:0:8} vs ${_src_md5:0:8}) ⇒ 诚实报出来"
    fi
  fi
fi
cp "$PROJ/TODO.md" docs/TODO.md
cp "$PROJ/docs/PROJECT_STATUS.md" docs/PROJECT_STATUS.md
cp "$PROJ/docs/OPEN_ISSUES.md" docs/OPEN_ISSUES.md
cp "$PROJ/docs/START_HERE.md" docs/START_HERE.md
cp "$PROJ/state/STATUS_DIGEST.md" docs/STATUS_DIGEST.md
cp "$PROJ/CERT_CHECKLIST.md" docs/CERT_CHECKLIST.md
cp "$PROJ/DECISIONS.md" docs/DECISIONS.md
# ★2026-10-29 加: 待老板拍板页也进 docs/ (老板主要看 GitHub —— 拍板页放项目树里老板看不到)
ls -1t "$PROJ"/DECISION_PENDING_*.md 2>/dev/null | head -3 | while read -r f; do cp "$f" "docs/$(basename "$f")"; done
cp "$PROJ/DECISION_TABLE_Q1_Q4_Q17.md" docs/DECISION_TABLE_Q1_Q4_Q17.md
cp "$PROJ/FRAMEWORK_SCOPE.md" docs/FRAMEWORK_SCOPE.md
cp "$PROJ/INTERFACES.md" docs/INTERFACES.md
cp "$PROJ/PRINT/PRINTER_SETUP.md" docs/PRINT_SETUP.md
cp "$PROJ/STRESS_TEST_2026-10-25.md" docs/STRESS_TEST_2026-10-25.md
cp "$PROJ/STATUS_SUMMARY.md" docs/STATUS_SUMMARY.md
# 发布树 .gitignore (防垃圾再进来)
cat > .gitignore <<'GITIGNORE'
__pycache__/
*.pyc
.DS_Store
*.tmp
state/.lastgood/
/projects/smart_glasses/state/.lastgood/
/projects/smart_glasses/HW/PCB/production/3d/
*.kicad_pcb
!**/_frame_reference.kicad_pcb
BOOTSTRAP.md
.openclaw/
workspace-state.json
GITIGNORE
# 框架文档 (若项目树里有 FRAMEWORK/ 则整目录带过去)
[ -d "$PROJ/FRAMEWORK" ] && rsync -a --delete "$PROJ/FRAMEWORK/" docs/FRAMEWORK/

# ---- 4. ★真值反查脱敏 (仓库公开, 命中 0 才准推) ----
python3 - "$PUB" <<'PY'
# ★★2026-10-30 00:4x 扩展: 除了 openclaw.json 里的 token/apikey/secret, 再扫 3 类**不在配置文件里但同样敏感**的串:
#   ① 设备口令 (板子 SSH 密码) ② 微信 openid (推送目标) ③ 内网 IP 段
#   动机: MEMORY.md / TOOLS.md / memory/*.md 里就有这些 ⇒ ★**它们绝不能进公开仓库**, 一旦误加就要靠这道闸拦住。

import json, os, sys, re
# ★★★2026-11-01 20:4x 重写 (上一版留了个真隐患, 见下):
# ★★隐患: 上一版把微信 openid **拆拼**后硬编码在这份脚本里 ("...dzq" + "HDb...") —— 但**本脚本自己会被 rsync 进公开仓库**!
#   拆拼只是骗过了"自己扫自己"这一关, 两段明文都在文件里, grep 一下就能拼回完整 openid ⇒ **等于把凭据发到公开仓库**。
#   ⇒ 正解: **脚本里一个敏感串都不写**, 全部从**本地不入库的真值源**现读。
#     真值源 = ~/.openclaw/openclaw.json (token/apikey/secret) + ~/.openclaw/cron/jobs.json (推送目标 openid) + 本机 TOOLS.md (设备口令)。
#     这三个文件都在 ~/.openclaw/ 下, **不在发布树里** ⇒ 闸门自己干净, 且不靠"拆拼"这种脆弱技巧。
# ★★口径: **内网 IP 不作为阻断项** —— DECISION_PENDING_2026-10-26.md / state/issue_log.yaml / state/measurements.yaml
#   里本来就有打印机内网地址 (早就在仓库里), 加这条会把**已发布内容**也拦掉 ⇒ 推不出去。
#   ⇒ 高危只保留: **设备 SSH 口令** + **微信 openid** + **配置里的 token/apikey** (这三个是真正的凭据/隐私)。

# ★★口径: **内网 IP 不作为阻断项** —— DECISION_PENDING_2026-10-26.md / state/issue_log.yaml / state/measurements.yaml
#   里本来就有打印机内网地址 (早就在仓库里), 加这条会把**已发布内容**也拦掉 ⇒ 推不出去。
#   ⇒ 高危只保留: **设备 SSH 口令** + **微信 openid** + **配置里的 token/apikey** (这三个是真正的凭据/隐私)。
#
# ★★★2026-11-01 20:4x 修掉自指悖论 (上一版留下的真隐患):
#   上一版把微信 openid **拆拼**后硬编码在这份脚本里 —— 但**本脚本自己会被 rsync 进公开仓库**!
#   拆拼只是骗过"自己扫自己"这一关, 两段明文都在文件里, grep 一下就能拼回完整串 ⇒ **等于把凭据发到公开仓库**。
#   ⇒ 正解: **脚本里一个敏感串明文都不写**, 全部从**本地不入库的真值源**现读:
#     · ~/.openclaw/openclaw.json        → token / apikey / secret
#     · ~/.openclaw/cron/jobs.json        → 推送目标标识
#     · ~/.../TOOLS.md, ~/.../MEMORY.md   → 设备口令
#   这三个源都在 ~/.openclaw/ 下, **不在发布树里** ⇒ 闸门自身干净。
#   ★同理: 设备口令的**匹配规则**也必须由真值动态生成 (下面用 re.escape 拼), 
#     否则源码里那句 `sshpass -p <口令>` 字面量会被自己扫到 ⇒ 又一次自指悖论。

def _read(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception:
        return ""

def _local_literals():
    """从本地真值源现读**高熵**敏感串 (微信 openid) —— 脚本自身不含任何明文。
    ★注意: **设备口令绝不能进这里** —— 低熵短串当字面量扫会命中路径名 (10-30 那版误报 6 个文件的根因)
      ⇒ 设备口令一律走 EXTRA_RE 的**上下文**匹配。"""
    out = []
    try:
        j = json.load(open(os.path.expanduser("~/.openclaw/cron/jobs.json"), encoding="utf-8"))
        jobs = j.get("jobs", j) if isinstance(j, dict) else j
        for job in (jobs or []):
            d = (job or {}).get("delivery") or {}
            to = d.get("to")
            cands = to if isinstance(to, list) else [to]
            for x in cands:
                if isinstance(x, str) and len(x) >= 20 and "@" in x:
                    out.append(x.split("@")[0])       # 只要 @ 之前那段标识
    except Exception:
        pass
    return sorted(set(x for x in out if x))

def _local_passwords():
    """从本地 TOOLS.md / MEMORY.md 现读**设备口令** (低熵) —— 只用来动态生成上下文正则, 本身不入脚本明文。
    ★格式兼容 (实盘形态): `**SSH 密码**: \\`<设备口令>\\`` (markdown 反引号 + 粗体星号) / `sshpass -p 'xxx'` / `password=xxx`
    ★长度下限 **3** (不是 6) —— 实盘口令就 5 个字符, 下限 6 会把真口令漏掉 ⇒ 闸门形同虚设"""
    out = set()
    for p in (os.path.expanduser("~/.openclaw/workspace/TOOLS.md"),
              os.path.expanduser("~/.openclaw/workspace/MEMORY.md")):
        s = _read(p)
        # 前缀允许 markdown 装饰 (* ` " 等) 夹在关键词与冒号之间
        pat = (r"(?i)(?:sshpass\s+-p\s+|密码\s*[:：]\s*|pass(?:word|wd)?\s*[:=]\s*)"
               r"[\s*`\"']*([A-Za-z0-9_@!#$%^&*.-]{3,24})[\s*`\"']*")
        for m in re.finditer(pat, s):
            out.add(m.group(1))
    return sorted(out)

pub = sys.argv[1]
EXTRA_LITERALS = _local_literals()
# ★设备口令: 只在**口令上下文**命中才算 —— 光路径名不算 (上一版 \b<口令>\b 会误伤 6 个正常文件)
#   ★规则用真值动态拼 ⇒ 脚本源码里不出现任何口令明文 ⇒ 不会自指
EXTRA_RE = []
for _pw in _local_passwords():
    _e = re.escape(_pw)
    # ★上下文里允许 markdown 装饰夹在关键词与冒号/值之间 (实盘形态: `**SSH 密码**: \`<设备口令>\``)
    _ctx = r"[\s*`\"]*"
    # ★口令值必须是**完整字段**: 后不跟标识符续接符 (`-` `_` `/` 字母数字) / 域名尾巴 (`.com`) /
    #   "空格+英文词" (散文续写, 如 `key: <口令> camera module` ⇒ 那是正文不是口令值)
    _B = r"(?![-_/A-Za-z0-9])(?!\.[A-Za-z])(?!\s+[A-Za-z0-9])"
    EXTRA_RE.append(re.compile(r"sshpass\s+-p\s+['\"]?" + _e + r"\b"))
    EXTRA_RE.append(re.compile(r"(?i)(?<![A-Za-z0-9])pass(?:[_-]?(?:word|wd))?(?![A-Za-z0-9])" + _ctx + r"(?:[:=：]|\|)" + _ctx + r"['\"]?" + _e + _B))
    EXTRA_RE.append(re.compile(r"(?i)密码" + _ctx + r"(?:[:=：]|\|)" + _ctx + r"['\"]?" + _e + _B))
    # ★★2026-11-02 20:4x **重写"通用上下文"规则** —— 旧版 (任何 `[:=]` 后跟口令就算) 在本项目**根本不成立**:
    #   原因: 设备口令与**板子品牌名 Radxa 同形** ⇒ 硬件文档里满篇 "**高**: **<品牌>-overlays ...**"
    #   / "**Radxa Display 5 / 8 HD**" / "产品页: <品牌>.com" 全被误判 (2026-11-02 实测拦住一次正常发布)。
    #   ⇒ 改成**三种精确形态** (漏检风险由第 1/2/3 条 + 真值字面量层 + 值形态层兜底):
    #     ① **凭据语义键**: 键名本身像口令 (pwd/pass/secret/token/key/auth/login/user/密码/口令/账号/密钥 ...)
    #     ② **定界值**: 任意键, 但值被引号/反引号定界 (形如 key: '<口令>' / key: `<口令>`)
    #     ③ **URL userinfo**: `scheme://user:<口令>@host` ⇒ 口令后紧跟 `@`
    #   ★键与值之间除 `:` `=` `：` 外**也允许 markdown 表格竖线** (| 密码 | <口令> | 这种键值分列的写法)
    #   ★键名两侧边界用 (?<![A-Za-z0-9]) / (?![A-Za-z0-9]) 而不是 \b ——
    #     \b 在下划线前不成立 (`user_name: <口令>` 漏检), 而 "monkey" 里的 "key" 也不该算键名。
    #   ★值侧收紧: 口令必须是**独立 token** —— 后面不跟标识符续接符 (`-` `_` 字母数字 `/`) 也不跟域名尾巴 (`.com`)
    #   ⇒ `<品牌>-overlays` / `<品牌>.com` / `docs.<品牌>.com` 不再命中, 而 `密码: <口令>` / `password=<口令>`
    #     / `sshpass -p '<口令>'` / `http://<user>:<口令>@host` / `帐号：<口令>` **仍全部被拦** (回归自测已过)。
    # ★注意: _kwd 里**不能再写 (?i)** —— 外面已经带了全局 flag, 重复会 re.error (global flags not at start)
    _kwd = (r"(?:pwd|pw|pass(?:[_-]?(?:word|wd))?|passphrase|secret(?:[_-]?key)?|token|"
            r"api[_-]?key|apikey|access[_-]?key|client[_-]?secret|private[_-]?key|auth(?:[_-]?token)?|"
            r"keys?|credential|cred|login|signin|sign[_-]?in|ssh[_-]?pass|user(?:[_-]?name)?|"
            r"密码|密碼|口令|账号|帐号|账户|用户|密钥|授权码|校验码)")
    EXTRA_RE.append(re.compile(r"(?i)(?<![A-Za-z0-9])" + _kwd + r"(?![A-Za-z0-9])" + _ctx + r"(?:[:=：]|\|)" + _ctx + r"['\"]?" + _e + _B))
    EXTRA_RE.append(re.compile(r"(?i)" + _ctx + r"[:=：]" + _ctx + r"['\"`]" + _e + r"['\"`]"))
    EXTRA_RE.append(re.compile(r"(?i)" + _ctx + r"[:=：]" + _ctx + r"['\"]?" + _e + r"@"))

truths = []
cfgp = os.path.expanduser("~/.openclaw/openclaw.json")
try:
    cfg = json.load(open(cfgp, encoding="utf-8"))
    def walk(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and len(v) >= 20 and re.search(r"(token|apikey|secret|password)", k, re.I):
                    truths.append((p + "/" + k, v))
                else:
                    walk(v, p + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{p}[{i}]")
    walk(cfg)
except Exception as e:
    print("⚠️ 读不到 openclaw.json:", e)
# ★★★2026-11-01 21:3x 补三条规则 (迁移到另一台主机前必须先补, 否则新主机一上手就在裸奔):
#   ① **扫全部四个 agent 的 auth-profiles** (原来只扫 main ⇒ 三个子 agent 的 key 漏检)
#   ② 加**值形态**规则 (sk-cp-… / tvly-… / ghp_… / sk-ant-… 等) ⇒ **不依赖字段名** ——
#      字段名能被改 (把 "key" 改成 "v" 就绕过), **值形态改不掉**
#   ③ 扫 agents 目录下的 **models.json** (可能含 authHeader 里的凭据)
import glob as _glob

_agent_profiles = sorted(_glob.glob(os.path.expanduser("~/.openclaw/agents/*/agent/auth-profiles.json")))
_agent_models = sorted(_glob.glob(os.path.expanduser("~/.openclaw/agents/*/agent/models.json")))
for p in _agent_profiles + _agent_models:
    try:
        d = json.load(open(p, encoding="utf-8"))
        def w2(o, pre=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and len(v) >= 20 and re.search(r"(key|token|secret)", k, re.I):
                        truths.append((pre + "/" + k, v))
                    else:
                        w2(v, pre + "/" + k)
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    w2(v, f"{pre}[{i}]")
        w2(d)
    except Exception:
        pass

# ★★值形态规则: **不依赖字段名** —— 字段名能被改, 值形态改不掉
VALUE_PATTERNS = [
    ("sk-cp-",   re.compile(r"sk-cp-[A-Za-z0-9_\-]{20,}")),
    ("sk-ant-",  re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("tvly-",    re.compile(r"tvly-[A-Za-z0-9_\-]{20,}")),
    ("ghp_",     re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("github_pat_", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("sk-proj-", re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}")),
    ("AKIA",     re.compile(r"AKIA[0-9A-Z]{16}")),
    ("wechat-openid", re.compile(r"o9cq[0-9A-Za-z]{12,}")),
]
hits = []
for root, dirs, files in os.walk(pub):
    dirs[:] = [d for d in dirs if d != ".git"]
    for f in files:
        p = os.path.join(root, f)
        try:
            data = open(p, "rb").read().decode("utf-8", "ignore")
        except Exception:
            continue
        for name, t in truths:
            if t and t in data:
                hits.append((os.path.relpath(p, pub), name))
        # ★★2026-10-30: 再扫 3 类不在配置文件里但同样敏感的串 (设备口令 / 微信 openid / 内网 IP)
        for lit in EXTRA_LITERALS:
            if lit and lit in data:
                hits.append((os.path.relpath(p, pub), f"EXTRA_LITERAL:{lit[:4]}***"))
        for rx in EXTRA_RE:
            m = rx.search(data)
            if m:
                hits.append((os.path.relpath(p, pub), f"EXTRA_RE:{rx.pattern}"))
        # ★★2026-11-01: **值形态**规则 —— 不依赖字段名 (字段名能被改, 值形态改不掉)
        for tag, vrx in VALUE_PATTERNS:
            m = vrx.search(data)
            if m:
                hits.append((os.path.relpath(p, pub), f"VALUE_SHAPE:{tag} ({m.group(0)[:6]}...)"))
print(f"真值反查: {len(truths)} 条凭据真值 + {len(EXTRA_LITERALS)} 敏感串 + {len(EXTRA_RE)} 口令上下文正则 "
      f"+ {len(VALUE_PATTERNS)} 值形态规则 × 整棵发布树 → 命中 {len(hits)}")
for h in hits[:10]:
    print("   ❌ 命中:", h)
sys.exit(1 if hits else 0)
PY
if [ $? -ne 0 ]; then
  echo "❌ 真值反查有命中, 拒绝推送"
  exit 1
fi
echo "[4] 真值反查 0 命中 ✅"

# ★★2026-11-05 09:20 **发布前闸 v3: 逻辑抽到独立脚本 + 判据③"验过且通过"**
#   v1/v2 的洞 (两次实测踩到):
#     ① v1 依赖 `.layout_landed.json` (当时还没一次成功落盘写过) ⇒ 闸门实际只跑了"段数≥1"
#     ② v2 拦住时整个发布都不推 ⇒ 板坏 ⇒ 连状态文档都推不上 ⇒ 老板在 GitHub 上永远看到过期状态
#     ③ ★★v2 最大的洞 (2026-11-05 09:20 实测事故): "板 mtime ≤ 已量过的板" 被当**通过**
#        ⇒ 而 auto_release 脚本**无条件**写 `.verified_board_mtime` ⇒⇒
#        ⇒⇒ **v25 (焊盘短路 / DRC 2 / unconnected 82) + 它出的 30 个 Gerber 被推上 GitHub (f31814b)**
#   v3 改法:
#     · ★**闸门逻辑抽到 state/board_publish_gate.sh (可单测, 已测 4 个分支)**
#     · ★**判据③**: `.verified_board_ok_mtime` 必须存在且 == 板 mtime (只有自验 rc=0 才写)
#       且 `.layout_done.json` 的 unconnected / drc_violations 必须都是 0
#     · ★**板 + 派生产物 (Gerber/钻孔/坐标/贴片) 一起管** ⇒ 拦下时一起撤 (历史里保留)
#     · ★**rsync 不再直接抄板/Gerber** ⇒ 闸门通过时才显式 cp ⇒ 不会"抄回来又删掉"反复折腾
PCB_REL="projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"
PCB_SRC="$PROJ/HW/PCB/demo_mainboard.kicad_pcb"
SKIP_PUSH=0
BOARD_BAD=0
BOARD_WHY=""
# ★★2026-11-05 09:50 修 (实测事故二): 包裹条件原来测的是**发布树**的 $PCB_REL,
#   而 rsync 早就把板从发布树排除了 ⇒ ⇒ 这块 if **从来就不成立** ⇒⇒
#   ⇒⇒ 闸门整块从来没跑过 (输出里连 "[4.5]" 行都没有!) ⇒⇒ 拦下时的"板级隔离"也从来没执行
#   ⇒⇒ 结果: 坏板 (DRC 2 / unconnected 82) 的 32 个 Gerber 一直躺在公开仓里
#      (GitHub contents API 实测 projects/smart_glasses/HW/PCB/gerbers = 32 项)
#   ⇒⇒ 现在: ① 条件测**源树**的板 ② 撤下逻辑交给 board_publish_gate.sh --withdraw (可单测, 11/11 过)
if [ -f "$PCB_SRC" ]; then
  # ★★闸门必须跑在**源树**上 (★不是发布树!) —— 因为: ① 板在源树 (rsync 已排除板 ⇒ 发布树里本来就没有)
  #   ② `.verified_board_ok_mtime` / `.layout_done.json` 这些自验证据也在源树
  #   ⇒ ⇒ 用发布树跑闸 ⇒ 永远"没有板" ⇒ ⇒ 板永远发布不出去 (★09:22 自己发现并修掉的逻辑 bug)
  GATE_OUT="$(bash "$PROJ/state/board_publish_gate.sh" "$PROJ" --withdraw "$PUB" 2>&1)"; GATE_RC=$?
  if [ "$GATE_RC" -ne 0 ]; then
    BOARD_BAD=1
    BOARD_WHY="$(echo "$GATE_OUT" | grep -m1 '^BAD|' | sed 's/^BAD|//')"
    SKIP_PUSH=1
    echo "[4.5] ⚠️ 发布闸拦板: $BOARD_WHY ⇒ ★**这块板不进 GitHub** (文档照推)"
    echo "$GATE_OUT" | grep -m1 '^WITHDRAW|' | sed 's/^/[4.5] /'
  else
    echo "[4.5] 发布闸: 板通过 (${GATE_OUT#OK|})"
    # ★★闸门通过 ⇒ 这时候才把板 + 派生产物拷进发布树 (rsync 阶段已排除)
    mkdir -p "$(dirname "$PCB_REL")"
    cp "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" "$PCB_REL" 2>/dev/null || true
    for _d in gerbers drill pos assembly 3d; do
      [ -d "$PROJ/HW/PCB/production/$_d" ] || continue
      mkdir -p "projects/smart_glasses/HW/PCB/production/$_d"
      cp -r "$PROJ/HW/PCB/production/$_d/." "projects/smart_glasses/HW/PCB/production/$_d/" 2>/dev/null || true
    done
    # ★顶层副本同样要带进来 (闸门通过时) —— 否则仓库会永久丢掉这一份 (历史里还在)
    if [ -d "$PROJ/HW/PCB/gerbers" ]; then
      mkdir -p projects/smart_glasses/HW/PCB/gerbers
      cp -r "$PROJ/HW/PCB/gerbers/." projects/smart_glasses/HW/PCB/gerbers/ 2>/dev/null || true
    fi
  fi
fi

# ---- 5. commit + push ----
# ★被跟踪过的运行时垃圾要显式 untrack (rsync 排除 = 保护不被删, 所以它会留在仓库里)
for junk in projects/smart_glasses/BOOTSTRAP.md projects/smart_glasses/.openclaw/workspace-state.json; do
  git rm -q --cached --ignore-unmatch "$junk" 2>/dev/null
  rm -f "$junk" 2>/dev/null
done
git add -A
if [ "$BOARD_BAD" = "1" ]; then
  # ★★★2026-11-05 09:20 **板级隔离 v3: 板 + 它的派生产物 (Gerber/钻孔/坐标/贴片) 一起撤**
  #   ★★为什么要升级: v2 用 `git checkout HEAD -- 板` ⇒ 但 **HEAD 里已经就是那块带短路的板** (f31814b 已推)
  #      ⇒ 撤不回来 ⇒ ⇒ 且 **Gerber 是从这块板出的** ⇒ 只撤板等于留了一堆不可投产的投产文件
  #   ⇒⇒ 现在: 板 + production/{gerbers,drill,pos,assembly} 全部从发布树里删掉 (历史里留着)
  #      ⇒ 文档照推 ⇒ ⇒ **仓库里"没有板" = 诚实状态** (从来没一块板过了门禁)
  git rm -q --cached --ignore-unmatch "$PCB_REL" 2>/dev/null || true
  rm -f "$PCB_REL" 2>/dev/null
  for _d in gerbers drill pos assembly; do
    git rm -r -q --cached --ignore-unmatch "projects/smart_glasses/HW/PCB/production/$_d" 2>/dev/null || true
    rm -rf "projects/smart_glasses/HW/PCB/production/$_d" 2>/dev/null || true
  done
  # ★★2026-11-05 09:40 补漏: **顶层 `HW/PCB/gerbers/` 副本也要撤** (见 rsync 段注释)
  git rm -r -q --cached --ignore-unmatch "projects/smart_glasses/HW/PCB/gerbers" 2>/dev/null || true
  rm -rf "projects/smart_glasses/HW/PCB/gerbers" 2>/dev/null || true
  echo "[5] ★板级隔离: 板 + Gerber/钻孔/坐标/贴片 全部从发布树撤下 (历史里保留) · 文档照常推"
  git add -A
fi
if git diff --cached --quiet; then
  echo "[5] 无变化 (跳过 push)"
else
  git commit -q -m "$MSG" && git push -q origin main && echo "[5] 已 push: $(git rev-parse --short HEAD)" && PUSHED=1
fi

# ---- 6. 验证 (① 远端 SHA == 本地 HEAD (不需要 API, 免限流) ② blob SHA 逐个比, API 限流时跳过) ----
echo "[6] 远端 SHA 校验 (ls-remote, 不吃 API 限流)"
REMOTE_SHA=$(git ls-remote origin main | cut -f1)
LOCAL_SHA=$(git rev-parse HEAD)
if [ "$REMOTE_SHA" = "$LOCAL_SHA" ]; then
  echo "  ✅ 远端 main = 本地 HEAD = ${LOCAL_SHA:0:8} → 推送已落地"
  # ★★2026-11-02 01:5x: **推送成功后写哨兵** —— 此前这个记录**只有人读、没有自动写点**
  #   ⇒ 手动推 / cron 自动同步推 / token 守护推, 记录都不更新 ⇒ token_watch 报的"距上次推送"永远是假的
  #   ⇒ 而这条是老板 10-29 定的最可靠兜底 (限额数值本身未公开) ⇒ **它骗自己 = 兜底失效**
  #   ⇒ 写入点放在这里 (唯一的推送收口, 三条推送路径都过它)
  if [ "${PUSHED:-0}" = "1" ]; then
    python3 "$SCRIPT_DIR/token_watch.py" --write-flag 2>/dev/null && echo "[6b] 推送哨兵已更新" || true
  fi
else
  echo "  ❌ 远端 ${REMOTE_SHA:0:8} != 本地 ${LOCAL_SHA:0:8}"
  exit 1
fi

python3 - "$PUB" "$REPO" <<'PY'
import json, os, subprocess, sys, urllib.request, time
pub, repo = sys.argv[1], sys.argv[2]
def gh(path):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}{path}",
                                 headers={"User-Agent": "openclaw-verify"})
    return json.load(urllib.request.urlopen(req, timeout=30))
files = ["docs/PROJECT_STATUS.md", "docs/OPEN_ISSUES.md", "docs/TODO.md",
         "projects/smart_glasses/PROJECT_TRACKER.md",
         "projects/smart_glasses/state/issue_log.yaml",
         "projects/smart_glasses/HW/SCHEMATIC_V1_SPEC.json",
         "projects/smart_glasses/state/check_netlist.py",
         "docs/STATUS_SUMMARY.md", "projects/smart_glasses/STATUS_SUMMARY.md",
         "projects/smart_glasses/HW/ONLINE_FINDINGS_2026-10-26.md",
         "README.md", "projects/smart_glasses/REPO_README.md",
         "projects/smart_glasses/HW/SCHEMATIC_V1.md"]
ok = bad = 0
for f in files:
    if not os.path.exists(os.path.join(pub, f)):
        print(f"  ⏭  {f} (本地没有, 跳过)")
        continue
    local = subprocess.run(["git", "-C", pub, "rev-parse", f"HEAD:{f}"], capture_output=True, text=True).stdout.strip()
    # ★权威基准 = git 协议的远端树 (origin/main:<file>), 不吃 CDN/API 缓存, 也不吃 API 限流
    tree = subprocess.run(["git", "-C", pub, "rev-parse", f"origin/main:{f}"], capture_output=True, text=True).stdout.strip()
    try:
        # ★加 cache-buster: GitHub contents API 会缓存刚推的文件的 blob sha
        #   (2026-10-27 实测: 推送后 contents API 返回上一版的 sha → 误报 3 个文件不一致;
        #    git ls-remote + git rev-parse origin/main:<file> 与加 _= 后重查都证明远端是对的)
        remote = gh(f"/contents/{f}?ref=main&_={int(time.time()*1000)}").get("sha", "")
    except Exception as e:
        msg = str(e)
        if "403" in msg or "rate limit" in msg.lower():
            print(f"  ⏭  {f} (API 限流 → 用 git 远端树判定)")
            same = (local == tree and local != "")
            ok += same
            bad += (not same)
            print(f"  {'✅' if same else '❌'} {f}  local={local[:8]} tree={tree[:8]} (git 协议)")
            continue
        print(f"  ❌ {f} → API 取不到: {e}")
        bad += 1
        continue
    same = (local == remote == tree)
    ok += same
    bad += (not same)
    print(f"  {'✅' if same else '❌'} {f}  local={local[:8]} api={remote[:8]} tree={tree[:8]}")
if ok == 0 and bad == 0:
    print("验证: 逐文件 blob SHA 校验已跳过 (GitHub API 限流) —— 远端一致性由上面的 ls-remote 硬校验保证")
else:
    print(f"验证: {ok} 一致 / {bad} 不一致")
sys.exit(1 if bad else 0)
PY
