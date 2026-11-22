#!/usr/bin/env bash
# =============================================================================
# ARS45 智能眼镜 —— 部署包生成器
# =============================================================================
# 生成一个**可直接拷到另一台主机**的 tar.gz:
#     ars45-deploy-<日期>.tar.gz
#
# 包内结构:
#     install.sh          ← 入口 (自包含, 不依赖先 clone 仓库)
#     README.md           ← 三步走
#     CREDENTIALS.md      ← 4 个凭据文件怎么填
#     config/             ← agent 配置资产 (人格/记忆/guards/skills/agents.json)
#     project/            ← 项目库快照 (含 projects/smart_glasses)
#     credentials/        ← ★放这 4 个带凭据的文件 (不随包分发, 由你 scp 进去)
#
# 用法:
#     bash deploy/make_bundle.sh              # 生成到项目树外 (默认 ../)
#     bash deploy/make_bundle.sh --out /tmp   # 指定输出目录
#     bash deploy/make_bundle.sh --no-project # 只带配置, 不带项目库快照 (45MB)
#
# ★★为什么要有这个 (老板 2026-11-01 23:0x):
#   一键脚本原本放在仓库里 ⇒ 新主机得**先 clone 才能拿到脚本** ⇒ 鸡生蛋
#   ⇒ 打成独立包 ⇒ **拷过去 → 解压 → 跑 install.sh** 就完事, 连 GitHub 都不用
# =============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(cd "$HERE/.." && pwd)"
WS="$(cd "$PROJ/.." && pwd)"

OUT_DIR="$(cd "$PROJ/.." && pwd)/.."
INCLUDE_PROJECT=1
while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT_DIR="${2:-$OUT_DIR}"; shift ;;
    --no-project) INCLUDE_PROJECT=0 ;;
    -h|--help) sed -n '2,26p' "$0"; exit 0 ;;
  esac
  shift
done

STAMP="$(date +%Y%m%d-%H%M)"
BUNDLE_NAME="ars45-deploy-$STAMP"
WORK="$(mktemp -d)/$BUNDLE_NAME"
mkdir -p "$WORK/credentials"

echo "═══ 生成部署包 $BUNDLE_NAME ═══"

# 1) 安装器 + 文档
cp "$HERE/install.sh" "$WORK/install.sh"
chmod +x "$WORK/install.sh"
[ -f "$HERE/README.md" ] && cp "$HERE/README.md" "$WORK/README.md"
[ -f "$HERE/CREDENTIALS.md" ] && cp "$HERE/CREDENTIALS.md" "$WORK/CREDENTIALS.md"
echo "  ✅ install.sh + 文档"

# 2) agent 配置资产 (从发布树副本拿 —— 那里是最新的)
CFGSRC="$WS/projects/smart_glasses/config"
if [ ! -d "$CFGSRC" ]; then
  CFGSRC="/tmp/od_glass_publish/config"
  echo "  (项目树里没有 config/ ⇒ 从发布树副本取)"
fi
if [ -d "$CFGSRC" ]; then
  cp -r "$CFGSRC" "$WORK/config"
  echo "  ✅ config/ ($(find "$WORK/config" -type f | wc -l) 文件, $(du -sh "$WORK/config" | cut -f1))"
else
  echo "  ⚠️ 找不到 config/ ⇒ 包里将没有 agent 配置资产 (install.sh 会报错)"
fi

# 3) 项目库快照
if [ $INCLUDE_PROJECT -eq 1 ]; then
  mkdir -p "$WORK/project/projects"
  rsync -a --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
        --exclude '.*_bak' --exclude '*_backup' --exclude '.bak_*' \
        "$PROJ/" "$WORK/project/projects/smart_glasses/"
  echo "  ✅ project/ 项目库快照 ($(du -sh "$WORK/project" | cut -f1))"
else
  echo "  ⏭ 跳过 project/ (--no-project) ⇒ install.sh 会去 GitHub clone"
fi

# 4) 凭据占位说明
cat > "$WORK/credentials/PLACE_HERE.txt" <<'EOF'
把下面 4 个文件放进本目录 (credentials/), 然后跑 ../install.sh:

  openclaw.json         ← 旧主机 ~/.openclaw/openclaw.json        (网关 token + tavily key)
  TOOLS.md              ← 旧主机 ~/.openclaw/workspace/TOOLS.md  (板子 SSH 口令 + 内网 IP)
  auth-profiles.json    ← 旧主机 ~/.openclaw/agents/main/agent/auth-profiles.json (minimax API key)
  jobs.json             ← 旧主机 ~/.openclaw/cron/jobs.json     (微信 openid + cron payload)

★这 4 个文件含凭据, 绝不进 GitHub ⇒ 用 scp / 密码管理器带过去。
★拷完本目录可以清空 (不要留明文凭据在机器上)。
EOF
echo "  ✅ credentials/ 占位说明"

# 5) 打包
mkdir -p "$OUT_DIR"
TARBALL="$OUT_DIR/$BUNDLE_NAME.tar.gz"
tar czf "$TARBALL" -C "$(dirname "$WORK")" "$BUNDLE_NAME"
echo
echo "═══ 完成 ═══"
echo "  包: $TARBALL"
echo "  体积: $(du -h "$TARBALL" | cut -f1)"
echo
echo "  ★拷到新主机后:"
echo "    tar xzf $(basename "$TARBALL") && cd $BUNDLE_NAME"
echo "    scp <旧主机那 4 个凭据文件> credentials/"
echo "    ./install.sh"
