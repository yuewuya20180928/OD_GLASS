#!/usr/bin/env bash
# =============================================================================
# ARS45 智能眼镜 · 4-Agent 职能制 —— ★自包含部署安装器★
# =============================================================================
# ★设计目标 (老板 2026-11-01 23:0x 的要求): **"直接放到另一个主机上部署"**
#   ⇒ 本脚本**不依赖"先 clone 仓库"** (鸡生蛋问题) ⇒ 拷过来就能跑
#
# 用法:
#   ./install.sh                 # 自动判断: 有同目录 project/ 就用它, 否则去 GitHub 拉
#   ./install.sh --check         # 只体检, 不改任何东西
#   ./install.sh --offline       # ★强制只用同目录的 project/ (完全不联网)
#   ./install.sh --repo <URL>    # 指定项目库地址
#   ./install.sh --home <dir>    # 指定 OPENCLAW_HOME (默认 ~/.openclaw)
#
# 它做什么 (7 步):
#   ① 体检 (openclaw / git / python3 / 凭据就位情况)
#   ② 取得项目库 (同目录快照 或 GitHub clone)
#   ③ 铺 workspace 目录 + ★projects 软链拓扑 (四个 inode 必须一致)
#   ④ 铺四个 agent 的 人格/身份/记忆/岗位说明书 + guards + skills
#   ⑤ 装带外凭据 + 合并 openclaw.json 的 agents 段 (★只合并 agents 段, 绝不整file覆盖)
#   ⑥ 装 cron jobs.json (★gateway 启动自动读, 不用逐条 cron add)
#   ⑦ 冒烟验证: merge / gate / issue / stage 四道门 + 与旧主机对数
#
# ★★三条铁律 (每条都对应一个踩过的坑):
#   - **只有一份项目库**: 三个子 agent 的 projects/ 是软链指向同一处 ⇒ 绝不能出现四份分叉
#   - **只合并 agents 段**: openclaw.json 整file覆盖会把 gateway token / tavily key 弄丢
#   - **绝不拷 jobs-state.json**: 那是运行时 pending slot, 带旧状态会串
# =============================================================================
set -uo pipefail

# ---------- 定位包内资源 ----------
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="${ARS45_REPO_URL:-git@github.com:yuewuya20180928/OD_GLASS.git}"
REPO_URL_HTTPS="https://github.com/yuewuya20180928/OD_GLASS.git"
HOME_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}"
AGENTS=(main hw-lead sw-lead mech-lead)
CHECK_ONLY=0
OFFLINE=0
FORCE_REPO=""

while [ $# -gt 0 ]; do
  case "$1" in
    --check)   CHECK_ONLY=1 ;;
    --offline) OFFLINE=1 ;;
    --repo)    FORCE_REPO="${2:-}"; shift ;;
    --home)    HOME_DIR="${2:-$HOME/.openclaw}"; shift ;;
    -h|--help) sed -n '2,32p' "$0"; exit 0 ;;
    *) echo "未知参数: $1 (--help 看用法)"; exit 2 ;;
  esac
  shift
done
[ -n "$FORCE_REPO" ] && REPO_URL="$FORCE_REPO"

C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_ERR=$'\033[31m'; C_H=$'\033[36m'; C_B=$'\033[1m'; C_OFF=$'\033[0m'
step() { echo; echo "${C_H}━━━ $* ━━━${C_OFF}"; }
ok()   { echo "  ${C_OK}✅${C_OFF} $*"; }
warn() { echo "  ${C_WARN}⚠️${C_OFF} $*"; }
err()  { echo "  ${C_ERR}❌${C_OFF} $*"; }
die()  { echo; echo "${C_ERR}❌ 失败: $*${C_OFF}"; exit 1; }

echo "${C_B}ARS45 智能眼镜 · 4-Agent 职能制部署安装器${C_OFF}"
echo "  包目录: $SELF_DIR   目标: $HOME_DIR"

# =============================================================================
step "① 体检"
# =============================================================================
command -v openclaw >/dev/null 2>&1 || die "没装 openclaw —— Ubuntu: npm i -g openclaw"
ok "openclaw: $(openclaw --version 2>/dev/null | head -1)"
command -v git >/dev/null 2>&1 || die "没装 git —— apt install git"
ok "git: $(git --version | cut -d' ' -f2)"
command -v python3 >/dev/null 2>&1 || die "没装 python3 —— apt install python3"
ok "python3: $(python3 --version)"

if [ ! -d "$HOME_DIR" ]; then
  warn "$HOME_DIR 不存在 ⇒ openclaw 还没初始化过"
  warn "  ⇒ 请先跑一次 'openclaw configure' 或 'openclaw' 生成配置骨架, 再回来跑本脚本"
  [ $CHECK_ONLY -eq 1 ] || die "先初始化 openclaw"
fi
ok "OPENCLAW_HOME = $HOME_DIR"

# 凭据就位检查
CRED_DIR="$SELF_DIR/credentials"
[ -d "$CRED_DIR" ] || CRED_DIR="$HOME_DIR"
declare -a NEED_CRED=(
  "openclaw.json|网关 token + tavily apiKey"
  "TOOLS.md|板子 SSH 口令 + 内网 IP"
  "auth-profiles.json|minimax API key"
  "jobs.json|微信 openid + cron payload"
)
CRED_OK=1
echo "  ── 凭据 (★含机密, 走带外通道, 放 $CRED_DIR) ──"
for item in "${NEED_CRED[@]}"; do
  f="${item%%|*}"; what="${item##*|}"
  found=""
  for cand in "$CRED_DIR/$f" "$HOME_DIR/$f" "$HOME_DIR/cron/$f" "$HOME_DIR/agents/main/agent/$f" "$HOME_DIR/workspace/$f"; do
    [ -f "$cand" ] && { found="$cand"; break; }
  done
  if [ -n "$found" ]; then ok "$f  ($what)"; else warn "$f  ($what) ✗ 未找到"; CRED_OK=0; fi
done
if [ $CRED_OK -eq 0 ]; then
  echo "  ${C_WARN}★凭据未齐 ⇒ agent 能启动但调不了模型 / 发不了推送${C_OFF}"
  echo "  ${C_WARN}★见 CREDENTIALS.md (本包内) —— 4 个文件, scp 过来即可${C_OFF}"
fi
if [ $CHECK_ONLY -eq 1 ]; then
  step "体检完毕 (--check 未做任何改动)"
  echo "  下一步: 把 4 个凭据文件放进 $CRED_DIR, 然后跑 './install.sh'"
  exit 0
fi

# =============================================================================
step "② 取得项目库 (只一份!)"
# =============================================================================
REPO_ROOT="$HOME_DIR/workspace"
PROJ_DST="$REPO_ROOT/projects/smart_glasses"
CFGSRC=""
mkdir -p "$REPO_ROOT"

# 优先: 同目录的快照 (打包模式)
if [ -d "$SELF_DIR/project/projects/smart_glasses" ]; then
  ok "用包内项目库快照 (离线, 不联网)"
  mkdir -p "$REPO_ROOT/projects"
  [ -d "$PROJ_DST" ] || cp -r "$SELF_DIR/project/projects/smart_glasses" "$PROJ_DST"
  [ -d "$SELF_DIR/project/config" ] && cp -rf "$SELF_DIR/project/config" "$REPO_ROOT/" 2>/dev/null
  CFGSRC="$REPO_ROOT/config"
  [ -d "$SELF_DIR/config" ] && [ ! -d "$CFGSRC" ] && { cp -rf "$SELF_DIR/config" "$REPO_ROOT/"; CFGSRC="$REPO_ROOT/config"; }
elif [ $OFFLINE -eq 1 ]; then
  die "--offline 模式但包内没有 project/ 快照"
else
  # GitHub
  if [ -d "$REPO_ROOT/.git" ]; then
    ok "已存在 ⇒ 拉最新"
    git -C "$REPO_ROOT" pull --ff-only 2>/dev/null || warn "pull 失败, 用现有版本继续"
  else
    CLONE_ERR=$(mktemp)
    if ! timeout 300 git clone --depth=1 --single-branch "$REPO_URL" "$HOME_DIR/workspace/.repo_tmp" 2>"$CLONE_ERR"; then
      warn "SSH clone 失败: $(tail -1 "$CLONE_ERR")"
      case "$REPO_URL" in /*|./*|file://*) die "clone 失败 (本地路径)" ;; esac
      warn "⇒ 退 HTTPS (新主机可能没配 SSH key)"
      timeout 600 git clone --depth=1 --single-branch "$REPO_URL_HTTPS" "$HOME_DIR/workspace/.repo_tmp" 2>"$CLONE_ERR" || {
        tail -6 "$CLONE_ERR" | sed 's/^/  /'; die "clone 失败 (查网络/代理)"; }
    fi
    rm -f "$CLONE_ERR"
    [ -d "$HOME_DIR/workspace/.repo_tmp/config" ] && cp -r "$HOME_DIR/workspace/.repo_tmp/config" "$REPO_ROOT/" 2>/dev/null
    [ -d "$HOME_DIR/workspace/.repo_tmp/projects" ] && cp -r "$HOME_DIR/workspace/.repo_tmp/projects" "$REPO_ROOT/" 2>/dev/null
    [ -d "$HOME_DIR/workspace/.repo_tmp/.git" ] && mv "$HOME_DIR/workspace/.repo_tmp/.git" "$REPO_ROOT/.git" 2>/dev/null
    rm -rf "$HOME_DIR/workspace/.repo_tmp"
    ok "clone 完成"
  fi
  CFGSRC="$REPO_ROOT/config"
fi
[ -d "$PROJ_DST" ] || die "找不到项目库: $PROJ_DST"
ok "项目库: $PROJ_DST"
[ -d "$CFGSRC" ] || die "找不到 agent 配置: 期望 $CFGSRC (agent 人格/记忆/守卫)"

# =============================================================================
step "③ 铺 workspace + ★projects 软链拓扑 (只一份库)"
# =============================================================================
# ★★agent id (hw-lead) ≠ workspace 目录名 (workspace-hw) ⇒ 取第一段, 不是 ${a##*-} (那是 "lead")
for a in "${AGENTS[@]}"; do
  wd="$HOME_DIR/workspace"; [ "$a" != "main" ] && wd="$HOME_DIR/workspace-${a%%-*}"
  mkdir -p "$wd"
  ln -sfn "$HOME_DIR/workspace/projects" "$wd/projects"
done
INODES=$(for a in "${AGENTS[@]}"; do
  wd="$HOME_DIR/workspace"; [ "$a" != "main" ] && wd="$HOME_DIR/workspace-${a%%-*}"
  stat -c %i "$wd/projects/smart_glasses" 2>/dev/null
done | sort -u | wc -l)
if [ "$INODES" -eq 1 ]; then ok "★四份 projects/smart_glasses inode 一致 (=1, 只有一份库)"
else die "inode 不一致 ($INODES 个) ⇒ 软链没建对, 停下别继续"; fi

# =============================================================================
step "④ 铺 agent 人格 / 记忆 / 岗位说明书 / guards / skills"
# =============================================================================
for a in "${AGENTS[@]}"; do
  wd="$HOME_DIR/workspace"; [ "$a" != "main" ] && wd="$HOME_DIR/workspace-${a%%-*}"
  mkdir -p "$wd/memory"
  src="$CFGSRC/agents/$a"
  [ -d "$src" ] || { warn "$a: 找不到 $src"; continue; }
  n=0
  for f in SOUL.md IDENTITY.md USER.md MEMORY.md AGENTS.md; do
    [ -f "$src/$f" ] && { cp -f "$src/$f" "$wd/$f"; n=$((n+1)); }
  done
  if [ -d "$src/memory" ]; then
    cp -f "$src/memory"/*.md "$wd/memory/" 2>/dev/null
    cnt=$(ls -1 "$wd/memory"/*.md 2>/dev/null | wc -l)
    ok "$a: $n 文件 + $cnt 篇日记 → $wd"
  else
    ok "$a: $n 文件 → $wd"
  fi
  mkdir -p "$HOME_DIR/agents/$a/agent"
  for f in models.json auth-state.json; do
    [ -f "$src/agent/$f" ] && cp -f "$src/agent/$f" "$HOME_DIR/agents/$a/agent/$f"
  done
done
if [ -d "$CFGSRC/guards" ]; then
  mkdir -p "$HOME_DIR/guards"; cp -rf "$CFGSRC/guards/." "$HOME_DIR/guards/"
  chmod +x "$HOME_DIR/guards"/*/openclaw 2>/dev/null
  ok "guards 已装 —— ★跨 agent 通信禁令依赖它"
else
  warn "guards 缺失 ⇒ ★跨 agent 通信禁令会失效"
fi
mkdir -p "$HOME_DIR/workspace/skills" "$HOME_DIR/skills"
[ -d "$CFGSRC/skills" ] && cp -rf "$CFGSRC/skills/." "$HOME_DIR/workspace/skills/" && ok "项目级 skills → workspace/skills"
[ -d "$CFGSRC/skills-global" ] && cp -rf "$CFGSRC/skills-global/." "$HOME_DIR/skills/" && ok "全局 skills → ~/.openclaw/skills"

# =============================================================================
step "⑤ 装带外凭据 (★只合并 agents 段, 绝不整file覆盖)"
# =============================================================================
install_cred() {
  local name="$1"; shift
  for dest in "$@"; do
    for src in "$CRED_DIR/$name" "$HOME_DIR/$name" "$HOME_DIR/cron/$name" "$HOME_DIR/agents/main/agent/$name" "$HOME_DIR/workspace/$name"; do
      [ -f "$src" ] || continue
      [ "$src" -ef "$dest" ] && { ok "$name 已在位"; return 0; }
      mkdir -p "$(dirname "$dest")"; cp -f "$src" "$dest"
      ok "$name → $dest"; return 0
    done
  done
  warn "$name 未找到 (跳过) —— 见 CREDENTIALS.md"; return 1
}
install_cred openclaw.json       "$HOME_DIR/openclaw.json"
install_cred TOOLS.md           "$HOME_DIR/workspace/TOOLS.md"
install_cred auth-profiles.json "$HOME_DIR/agents/main/agent/auth-profiles.json"
install_cred jobs.json          "$HOME_DIR/cron/jobs.json"

if [ -f "$CFGSRC/openclaw.agents.json" ] && [ -f "$HOME_DIR/openclaw.json" ]; then
  python3 - "$CFGSRC/openclaw.agents.json" "$HOME_DIR/openclaw.json" <<'PY'
import json, sys, shutil, os, time
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(dst, encoding="utf-8"))
new = json.load(open(src, encoding="utf-8"))
if "agents" not in new:
    print("  ⚠️ 源里没有 agents 段, 跳过合并"); sys.exit(0)
shutil.copy2(dst, dst + ".bak." + time.strftime("%Y%m%d_%H%M%S"))
d["agents"] = new["agents"]
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
print(f"  ✅ openclaw.json 的 agents 段已合并 (★原文件已备份 .bak.*)")
print(f"     model = {d['agents'].get('defaults',{}).get('model_primary')}  ★必须是 M3.1-Flash")
PY
fi

# =============================================================================
step "⑥ cron (★拷 jobs.json 即可, gateway 启动自动读)"
# =============================================================================
if [ -f "$HOME_DIR/cron/jobs.json" ]; then
  ok "jobs.json 已就位 ⇒ **无需逐条 cron add**"
  echo "     ★**不要拷 jobs-state.json** (运行时 pending slot, 带旧状态会串)"
  echo "     ★验证: openclaw cron list"
  echo "     ★⚠️ '队列自动派活' 在旧主机是 disabled ⇒ 要恢复: openclaw cron enable fb67af40-a9eb-4cdd-a842-8cbb8fdd7865"
  echo "     ★⚠️ ★★旧主机的 cron 必须**先停** ⇒ 否则两边同时派活 = 同 agent 两个写会话 = 互相覆盖分片"
else
  warn "jobs.json 未找到 ⇒ cron 需手动恢复"
fi

# =============================================================================
step "⑦ 冒烟验证 (数字必须与旧主机一致)"
# =============================================================================
cd "$PROJ_DST" || die "进不去 $PROJ_DST"
python3 state/merge.py >/tmp/_m.log 2>&1; MRC=$?; tail -1 /tmp/_m.log
[ $MRC -eq 0 ] && ok "merge rc=0" || warn "merge rc=$MRC"
python3 state/gate_check.py >/tmp/_g.log 2>&1; grep -E "Q1" /tmp/_g.log | head -1
python3 state/issue_check.py >/tmp/_i.log 2>&1; tail -1 /tmp/_i.log
python3 state/stage_gate.py >/tmp/_s.log 2>&1; grep -E "当前在" /tmp/_s.log | head -1
echo
echo "  ★对着旧主机快照核对: $PROJ_DST/PROGRESS_SNAPSHOT.md"

echo
echo "${C_H}━━━ 部署完成 ━━━${C_OFF}"
cat <<'DONE'
  1. 重启网关: systemctl --user restart openclaw-gateway   (或 openclaw gateway restart)
  2. 检查 agent: openclaw agents list
  3. 起 TUI:     openclaw tui
  4. 验证派活:  openclaw cron list
  5. ★★别忘: 旧主机的 cron 要**先停** (两边同时派活 = 互相覆盖分片)
     ★★而且旧主机的 **GitHub 同步 cron 也要停** ⇒ 只留一个推送方, 否则两边 state/ 会漂移
DONE
