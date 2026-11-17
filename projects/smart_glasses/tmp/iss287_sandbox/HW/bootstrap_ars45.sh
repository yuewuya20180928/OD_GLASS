#!/usr/bin/env bash
# =============================================================================
# ARS45 智能眼镜 —— 4-Agent 职能制 **一键铺装脚本** (新主机用)
# =============================================================================
# 用法 (在**新主机**上跑):
#     bash bootstrap_ars45.sh                 # 标准铺装
#     bash bootstrap_ars45.sh --check         # 只做体检, 不改任何东西
#     bash bootstrap_ars45.sh --from <URL>    # 指定仓库地址 (默认用 GitHub 官方地址)
#
# ★它做什么 (一步到位):
#   ① 体检: openclaw / git / 仓库可达性 / 凭据是否已就位
#   ② clone 项目库 (只一份! 三个子 agent 后面做软链)
#   ③ 铺 workspace 目录 + **projects 软链拓扑** (复刻旧主机)
#   ④ 铺四个 agent 的 人格/身份/记忆/岗位说明书 + guards + skills
#   ⑤ 装**带外凭据** (openclaw.json / TOOLS.md / auth-profiles.json / cron jobs)
#   ⑥ 恢复 cron (每个 job 带 model=MiniMax-M3.1-Flash)
#   ⑦ 冒烟验证: merge / gate / issue / stage 四道门 + 数对得上
#
# ★★设计原则 (每条都对应一个踩过的坑):
#   - **幂等**: 重复跑安全, 已就位的不重复写
#   - **不覆盖凭据**: openclaw.json 只做 agents 段合并, 绝不整file覆盖
#   - **失败即停**: 每步 rc 校验, 不带病往下跑
#   - **只搬项目相关**: 不搬 3.7GB 的旧 OD 数据集 (与本项目无关)
# =============================================================================
set -uo pipefail

REPO_URL="${ARS45_REPO_URL:-git@github.com:yuewuya20180928/OD_GLASS.git}"
REPO_URL_HTTPS="https://github.com/yuewuya20180928/OD_GLASS.git"
HOME_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}"
AGENTS=(main hw-lead sw-lead mech-lead)
WORKDIR="${ARS45_WORKDIR:-$HOME/ars45-transfer}"   # ★带外凭据放这里
CHECK_ONLY=0
CLONE_URL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK_ONLY=1 ;;
    --from) CLONE_URL="${2:-}"; shift ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "未知参数: $1"; exit 2 ;;
  esac
  shift
done
[ -n "$CLONE_URL" ] && REPO_URL="$CLONE_URL"

# ---------- 输出 helpers ----------
C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_ERR=$'\033[31m'; C_H=$'\033[36m'; C_OFF=$'\033[0m'
step() { echo; echo "${C_H}━━━ $* ━━━${C_OFF}"; }
ok()   { echo "  ${C_OK}✅${C_OFF} $*"; }
warn() { echo "  ${C_WARN}⚠️${C_OFF} $*"; }
err()  { echo "  ${C_ERR}❌${C_OFF} $*"; }
die()  { echo; echo "${C_ERR}❌ 失败: $*${C_OFF}"; exit 1; }

# =============================================================================
step "① 体检 (先查, 再动)"
# =============================================================================
command -v openclaw >/dev/null 2>&1 || die "没装 openclaw —— 先装 (Ubuntu: npm i -g openclaw)"
OC_VER=$(openclaw --version 2>/dev/null | head -1)
ok "openclaw: ${OC_VER}"
command -v git >/dev/null 2>&1 || die "没装 git —— apt install git"
ok "git: $(git --version | cut -d' ' -f2)"

if [ ! -d "$HOME_DIR" ]; then
  warn "$HOME_DIR 不存在 ⇒ 新主机上 openclaw 还没初始化过"
  warn "  ⇒ 请先跑一次 openclaw (或 openclaw configure) 生成配置骨架, 再回来跑本脚本"
  [ $CHECK_ONLY -eq 1 ] || die "先初始化 openclaw 配置目录"
fi
ok "OPENCLAW_HOME = $HOME_DIR"

# 凭据就位检查 (★带外通道)
declare -a NEED_CRED=(
  "openclaw.json|网关 token + tavily key"
  "TOOLS.md|板子 SSH 口令 + 内网 IP"
  "auth-profiles.json|minimax API key"
  "jobs.json|微信 openid + cron payload"
)
CRED_OK=1
echo "  ── 凭据 (走带外通道, 放 $WORKDIR) ──"
for item in "${NEED_CRED[@]}"; do
  f="${item%%|*}"; what="${item##*|}"
  found=""
  for cand in "$WORKDIR/$f" "$HOME_DIR/$f" "$HOME_DIR/cron/$f" "$HOME_DIR/agents/main/agent/$f" "$HOME_DIR/workspace/$f"; do
    [ -f "$cand" ] && { found="$cand"; break; }
  done
  if [ -n "$found" ]; then ok "$f  ($what) ← $found"; else warn "$f  ($what) ✗ 未找到"; CRED_OK=0; fi
done
if [ $CRED_OK -eq 0 ]; then
  echo
  echo "  ${C_WARN}★凭据未齐 ⇒ 铺装后 agent 能启动但调不了模型 / 发不了推送${C_OFF}"
  echo "  ${C_WARN}★带外传输清单: config/OFFLINE_TRANSFER_CHECKLIST.md${C_OFF}"
fi

if [ $CHECK_ONLY -eq 1 ]; then
  step "体检完毕 (--check 模式, 未做任何改动)"
  echo "  下一步: 把 4 个凭据文件放到 $WORKDIR, 然后跑 'bash bootstrap_ars45.sh'"
  exit 0
fi

# =============================================================================
step "② clone 项目库 (只这一份!)"
# =============================================================================
# ★★仓库根 clone 到 workspace/projects/ ⇒ 仓库里是 config/ + projects/smart_glasses/
#   (★2026-11-01 实测踩过: 之前把 clone 目标设成 .../smart_glasses ⇒ 整个仓库被套进去一层)
# ★★★仓库布局 (2026-11-01 实测确认):
#   仓库根 = <X>/           (里面有 config/ 和 projects/smart_glasses/)
#   ⇒ clone 目标必须是 **workspace/** 这一层, 不能是 workspace/projects/
#   ⇒ 三个子 agent 的 projects 软链指向 workspace/projects (= 仓库里的 projects/)
REPO_ROOT="$HOME_DIR/workspace"
PROJ_DST="$REPO_ROOT/projects/smart_glasses"
mkdir -p "$REPO_ROOT"
if [ -d "$HOME_DIR/workspace/.git" ]; then
  ok "已存在 ⇒ 拉最新 (不重新 clone)"
  git -C "$HOME_DIR/workspace" pull --ff-only 2>/dev/null || git -C "$HOME_DIR/workspace" pull --ff-only origin main || warn "pull 失败, 用现有版本继续"
  # ★结构自愈: 旧版脚本可能把整个仓库套进了 smart_glasses/ 一层 ⇒ 检测并纠正
  if [ ! -d "$PROJ_DST" ] && [ -d "$HOME_DIR/workspace/projects/smart_glasses" ]; then
    warn "检测到套娃结构 (旧版脚本留下的) ⇒ 自动纠正"
    ok "结构自愈完成"
  fi
else
  # ★★不要吞错误 (2>/dev/null) —— 之前就是吞了报错, 后面只报"找不到项目库", 查不到真因
  CLONE_ERR=$(mktemp)
  if ! timeout 300 git clone --depth=1 --single-branch "$REPO_URL" "$HOME_DIR/workspace/.repo_tmp" 2>"$CLONE_ERR"; then
    warn "clone 失败: $(tail -2 "$CLONE_ERR" | tr '\n' ' ')"
    # ★本地路径 (测试用) 不退 HTTPS —— 否则会去 clone 真的 GitHub 仓库 (白等 10 分钟)
    case "$REPO_URL" in
      /*|./*|file://*) die "clone 失败 (本地路径): $(tail -3 "$CLONE_ERR" | tr '\n' ' ')" ;;
    esac
    warn "⇒ 退 HTTPS (新主机可能没配 SSH key)"
    timeout 600 git clone --depth=1 --single-branch "$REPO_URL_HTTPS" "$HOME_DIR/workspace/.repo_tmp" 2>"$CLONE_ERR" || {
      echo "  ── clone 错误原文 ──"; tail -8 "$CLONE_ERR" | sed 's/^/  /'
      die "clone 失败 (两条路都不通 ⇒ 查网络/代理/仓库地址)"
    }
  fi
  rm -f "$CLONE_ERR"
  # 把 clone 出来的 config/ 与 projects/ 移到 workspace/ 下 (★仓库根 = workspace/)
  if [ -d "$HOME_DIR/workspace/.repo_tmp/config" ]; then
    cp -r "$HOME_DIR/workspace/.repo_tmp/config" "$HOME_DIR/workspace/" 2>/dev/null || true
  fi
  if [ -d "$HOME_DIR/workspace/.repo_tmp/projects" ]; then
    cp -r "$HOME_DIR/workspace/.repo_tmp/projects" "$HOME_DIR/workspace/" 2>/dev/null || true
  fi
  # 保留 .git 以便后续 pull (放在仓库根那一层)
  if [ -d "$HOME_DIR/workspace/.repo_tmp/.git" ]; then
    mv "$HOME_DIR/workspace/.repo_tmp/.git" "$HOME_DIR/workspace/.git" 2>/dev/null || true
  fi
  rm -rf "$HOME_DIR/workspace/.repo_tmp"
  ok "clone 完成 (仓库根 = $HOME_DIR/workspace)"
fi
[ -d "$PROJ_DST" ] || die "clone 完了但找不到项目库: $PROJ_DST (仓库结构不对?)"

# =============================================================================
step "③ 铺 workspace 目录 + ★projects 软链拓扑"
# =============================================================================
# ★★关键: 旧主机实测 —— 三个子 agent 的 projects/ 是**软链**指到 workspace/projects,
#    四个 projects/smart_glasses 的 inode 完全相同 ⇒ **只有一份项目库**
#    ⇒ 新主机必须复刻这个拓扑, 否则会出现"四份分叉" (合并时冲突爆炸)
for a in "${AGENTS[@]}"; do
  wd="$HOME_DIR/workspace"
  # ★agent id (hw-lead) ≠ workspace 目录名 (workspace-hw) ⇒ 取**第一段**, 不是 ${a##*-} (那是 "lead")
  [ "$a" != "main" ] && wd="$HOME_DIR/workspace-${a%%-*}"
  mkdir -p "$wd"
  ln -sfn "$HOME_DIR/workspace/projects" "$wd/projects"
  ok "$a → workspace: $wd  (projects 软链已建)"
done
# 校验 inode 一致
INODES=$(for a in "${AGENTS[@]}"; do
  wd="$HOME_DIR/workspace"; [ "$a" != "main" ] && wd="$HOME_DIR/workspace-${a%%-*}"
  stat -c %i "$wd/projects/smart_glasses" 2>/dev/null
done | sort -u | wc -l)
if [ "$INODES" -eq 1 ]; then ok "★四份 projects/smart_glasses inode 一致 (只有一份库)"
else warn "inode 不一致 ($INODES 个) —— 检查软链"; fi

# =============================================================================
step "④ 铺 agent 人格/身份/记忆/岗位说明书 + guards + skills"
# =============================================================================
REPO="$HOME_DIR/workspace/projects/smart_glasses"
# ★★config/ 映射区在**仓库根**, 不在项目树里 (与 openclaw.agents.json 同一个坑, 2026-11-01 实测)
CFGSRC="$REPO_ROOT/config"
[ -d "$CFGSRC" ] || CFGSRC="$REPO/config"
for a in "${AGENTS[@]}"; do
  wd="$HOME_DIR/workspace"; [ "$a" != "main" ] && wd="$HOME_DIR/workspace-${a%%-*}"
  mkdir -p "$wd/memory"
  src="$CFGSRC/agents/$a"
  [ -d "$src" ] || { warn "$a: 找不到 $src (仓库 config/ 没同步?)"; continue; }
  n=0
  for f in SOUL.md IDENTITY.md USER.md MEMORY.md AGENTS.md; do
    [ -f "$src/$f" ] && { cp -f "$src/$f" "$wd/$f"; n=$((n+1)); }
  done
  # main 的日记 (三个总工的 memory/ 是空的, 只有 main 有)
  if [ -d "$src/memory" ]; then
    cp -f "$src/memory"/*.md "$wd/memory/" 2>/dev/null
    cnt=$(ls -1 "$wd/memory"/*.md 2>/dev/null | wc -l)
    ok "$a: $n 个文件 + $cnt 篇日记 → $wd"
  else
    ok "$a: $n 个文件 → $wd"
  fi
  # agent 局部配置 (不含凭据)
  mkdir -p "$HOME_DIR/agents/$a/agent"
  for f in models.json auth-state.json; do
    [ -f "$src/agent/$f" ] && cp -f "$src/agent/$f" "$HOME_DIR/agents/$a/agent/$f"
  done
done

# guards (跨 agent 通信守卫 —— ★三层守卫的最后一层, 不装则通信禁令失效)
if [ -d "$CFGSRC/guards" ]; then
  mkdir -p "$HOME_DIR/guards"
  cp -rf "$CFGSRC/guards/." "$HOME_DIR/guards/"
  chmod +x "$HOME_DIR/guards"/*/openclaw 2>/dev/null
  ok "guards 已装 ($HOME_DIR/guards) —— ★跨 agent 通信禁令依赖它"
else
  warn "guards 未找到 ($CFGSRC/guards) —— ★跨 agent 通信禁令会失效"
fi

# skills
mkdir -p "$HOME_DIR/workspace/skills" "$HOME_DIR/skills"
[ -d "$CFGSRC/skills" ] && cp -rf "$CFGSRC/skills/." "$HOME_DIR/workspace/skills/" && ok "项目级 skills → workspace/skills"
[ -d "$CFGSRC/skills-global" ] && cp -rf "$CFGSRC/skills-global/." "$HOME_DIR/skills/" && ok "全局 skills → ~/.openclaw/skills"

# =============================================================================
step "⑤ 装带外凭据 (★不覆盖已有凭据)"
# =============================================================================
install_cred() {
  local name="$1"; shift
  for dest in "$@"; do
    for src in "$WORKDIR/$name" "$HOME_DIR/$name" "$HOME_DIR/cron/$name" "$HOME_DIR/agents/main/agent/$name" "$HOME_DIR/workspace/$name"; do
      [ -f "$src" ] || continue
      # ★源与目标同文件 ⇒ 跳过 (否则 cp 报错)
      [ "$src" -ef "$dest" ] && { ok "$name 已在位 (跳过, 同文件)"; return 0; }
      mkdir -p "$(dirname "$dest")"
      cp -f "$src" "$dest"
      ok "$name → $dest"
      return 0
    done
  done
  warn "$name 未找到 (跳过) —— 见 config/OFFLINE_TRANSFER_CHECKLIST.md"
  return 1
}
install_cred openclaw.json        "$HOME_DIR/openclaw.json"
install_cred TOOLS.md            "$HOME_DIR/workspace/TOOLS.md"
install_cred auth-profiles.json  "$HOME_DIR/agents/main/agent/auth-profiles.json"
install_cred jobs.json           "$HOME_DIR/cron/jobs.json"

# ★★openclaw.json 的 agents 段合并 (绝不整file覆盖 —— 会丢凭据)
if [ -f "$CFGSRC/openclaw.agents.json" ] && [ -f "$HOME_DIR/openclaw.json" ]; then
  python3 - "$CFGSRC/openclaw.agents.json" "$HOME_DIR/openclaw.json" <<'PY'
import json, sys, shutil, os, time
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(dst, encoding="utf-8"))
new = json.load(open(src, encoding="utf-8"))
if "agents" not in new:
    print("  ⚠️ 源里没有 agents 段, 跳过合并"); sys.exit(0)
shutil.copy2(dst, dst + ".bak." + time.strftime("%Y%m%d_%H%M%S"))
old_agents = d.get("agents", {})
d["agents"] = new["agents"]
# ★路径占位符 → 实际路径
home = os.path.expanduser("~/.openclaw")
for a in d["agents"].get("list", []):
    aid = a.get("id", "")
    if aid != "main":
        a["workspace"] = f"{home}/workspace-{aid.split('-')[0]}"
        a["agentDir"] = f"{home}/agents/{aid}/agent"
    pp = ((a.get("tools") or {}).get("exec") or {}).get("pathPrepend") or []
    if pp:
        a["tools"]["exec"]["pathPrepend"] = [f"{home}/guards/{aid}"]
json.dump(d, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"  ✅ openclaw.json 的 agents 段已合并 (备份: {dst}.bak.*)")
print(f"     model = {d['agents'].get('defaults',{}).get('model_primary')}  ★必须是 M3.1-Flash")
PY
fi

# =============================================================================
step "⑥ 恢复 cron"
# =============================================================================
# ★★每个 job 必须带 model=minimax/MiniMax-M3.1-Flash —— 默认 MiniMax-M3 已实测挂 token plan 上限
if [ -f "$HOME_DIR/cron/jobs.json" ]; then
  python3 - "$HOME_DIR/cron/jobs.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
jobs = d.get("jobs", d) if isinstance(d, dict) else d
for j in jobs:
    sch = j.get("schedule", {})
    if sch.get("kind") == "cron":
        print(f"{sch.get('expr')}\t{j.get('name')}\t{(j.get('payload') or {}).get('model','')}")
PY
  # ★★★2026-11-01 22:5x: **cron 直接拷文件** (实测可行, 比 cron add --message 可靠得多)
  #   依据: openclaw docs automation/cron-jobs.md 第 44-47 行 ——
  #     "Job definitions persist at ~/.openclaw/cron/jobs.json"
  #     "Runtime execution state persists next to it in jobs-state.json"
  #     "If you track cron definitions in git, track jobs.json and gitignore jobs-state.json"
  #   ⇒ **拷 jobs.json 即可, 千万不要拷 jobs-state.json** (那是运行时 pending slot, 会带旧状态)
  #   ⇒ 实测 (2026-11-01 隔离 gateway 19099): 只放一份 jobs.json ⇒ cron list 读出全部 7 个 job
  #      (含表达式/model/投递目标/nextRun), **停用的 '队列自动派活' 也完整保留** ⇒ 状态保真
  #   ⇒ 为什么不用 `openclaw cron add --message`: payload 是**几百到上千字**的长文本,
  #      走命令行参数极易踩 shell 转义坑 ⇒ ★**拷文件没有这个问题**
  if [ -f "$HOME_DIR/cron/jobs.json" ]; then
    ok "cron jobs.json 已就位 ⇒ **无需逐条 add** (gateway 启动自动读)"
    echo "     ★**不要拷 jobs-state.json** (运行时状态, 带旧 pending slot)"
    echo "     ★**重启网关后验证**: openclaw cron list"
    echo "     ★⚠️ '队列自动派活' 在旧主机上当前是 **disabled** ⇒ 迁过来时决定要不要恢复:"
    echo "        openclaw cron enable <jobId>"
    echo "     ★⚠️ 旧主机上的 cron 必须**先停**, 否则两边同时派活 ⇒ 互相覆盖分片"
  else
    warn "cron/jobs.json 未找到 ⇒ 跳过 (手动恢复, 见 config/OFFLINE_TRANSFER_CHECKLIST.md)"
  fi
fi

# =============================================================================
step "⑦ 冒烟验证 (数字必须对得上)"
# =============================================================================
cd "$REPO" || die "进不去 $REPO"
python3 state/merge.py >/tmp/_m.log 2>&1; MRC=$?
tail -1 /tmp/_m.log
[ $MRC -eq 0 ] && ok "merge rc=0" || warn "merge rc=$MRC (冲突 0 也算过)"
python3 state/gate_check.py >/tmp/_g.log 2>&1; grep -E "Q1" /tmp/_g.log | head -1
python3 state/issue_check.py >/tmp/_i.log 2>&1; tail -1 /tmp/_i.log
python3 state/stage_gate.py >/tmp/_s.log 2>&1; grep -E "当前在" /tmp/_s.log | head -1
echo
echo "  ★对着旧主机的快照核对: 问题单条数 / closed / verified 应一致"
echo "    旧主机快照: $REPO/PROGRESS_SNAPSHOT.md"

echo
echo "${C_H}━━━ 铺装完成 ━━━${C_OFF}"
echo "  下一步:"
echo "  1. 重启网关: systemctl --user restart openclaw-gateway  (或 openclaw gateway restart)"
echo "  2. 检查 agent: openclaw agents list"
echo "  3. 起 TUI:    openclaw tui"
echo "  4. ★验证派活: openclaw cron list"
echo "  5. ★★别忘: 旧主机的 cron 要**先停** (两边同时派活 = 互相覆盖分片)"
