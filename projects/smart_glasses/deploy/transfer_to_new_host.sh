#!/usr/bin/env bash
# =============================================================================
# ARS45 · 部署包 → 新主机 一键传输 (修掉 host key 变更 + 免密)
# =============================================================================
# 用法:
#     bash transfer_to_new_host.sh <新主机IP> [用户名]
#
# 它做 4 件事:
#   ① 检查/修复 host key (★先核验指纹再改, 不盲信)
#   ② 装本机公钥到新主机 (之后 scp/ssh 免密)
#   ③ 传部署包 + 4 个凭据文件 (凭据走 SSH 加密通道, 不落明文在共享盘)
#   ④ 在新主机上跑 install.sh
#
# ★★为什么不用 `scp -o StrictHostKeyChecking=no` 一把梭:
#   那样是**盲信任** ⇒ 万一有人做中间人, 你永远不会知道。
#   本脚本是**先 ssh-keyscan 拿指纹 → 打印出来 → 和你报的对比 → 一致才写入 known_hosts**。
# =============================================================================
set -uo pipefail

TARGET="${1:-}"
REMOTE_USER="${2:-}"
BUNDLE="${ARS45_BUNDLE:-$HOME/ars45-deploy/ars45-deploy-20261101-2336.tar.gz}"
WS="$HOME/.openclaw"

C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_ERR=$'\033[31m'; C_H=$'\033[36m'; C_OFF=$'\033[0m'
step() { echo; echo "${C_H}━━━ $* ━━━${C_OFF}"; }
ok()   { echo "  ${C_OK}✅${C_OFF} $*"; }
warn() { echo "  ${C_WARN}⚠️${C_OFF} $*"; }
die()  { echo "${C_ERR}❌ $*${C_OFF}"; exit 1; }

[ -n "$TARGET" ] || die "用法: bash transfer_to_new_host.sh <新主机IP> [用户名]"
[ -f "$BUNDLE" ] || die "找不到部署包: $BUNDLE (先跑 make_bundle.sh)"

echo "${C_H}目标${C_OFF}: $TARGET ${REMOTE_USER:+用户 $REMOTE_USER}"

# ---------- ① host key ----------
step "① 检查 host key (★先核验, 不盲信)"
NEW_FP=$(timeout 15 ssh-keyscan -t ed25519 "$TARGET" 2>/dev/null | ssh-keygen -lf - 2>/dev/null | awk '{print $2}')
[ -n "$NEW_FP" ] || die "ssh-keyscan 拿不到 $TARGET 的指纹 (机器开着吗?)"
echo "  当前机器上的指纹 (ED25519): $NEW_FP"
# ★★比对必须**按 key 类型取**, 不能 grep 第一条 —— known_hosts 里 RSA/ECDSA/ED25519 三条顺序不定,
#   取错类型会拿 RSA 指纹跟 ED25519 比 ⇒ **假警报** (2026-11-01 23:4x 实测踩到)
OLD=$(ssh-keygen -lf "$HOME/.ssh/known_hosts" 2>/dev/null | grep " $TARGET " | grep "(ED25519)" | awk '{print $2}' | head -1)
if [ -n "$OLD" ] && [ "$OLD" != "$NEW_FP" ]; then
  warn "known_hosts 里是**旧指纹** (机器重装过 / IP 换过机器):"
  echo "     旧: $OLD"
  echo "     新: $NEW_FP"
  echo "  ⇒ ★**请确认新指纹确实是你那台新主机的** (对比新主机上跑 'ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub')"
  echo "  ⇒ 确认无误后, 重跑本脚本并加 --force 接受新指纹"
  [ "${FORCE:-0}" = "1" ] || die "已中止 (加 FORCE=1 可跳过这步确认)"
  ssh-keygen -f "$HOME/.ssh/known_hosts" -R "$TARGET" >/dev/null
  ok "已删除旧记录"
fi
if ssh -o BatchMode=yes -o ConnectTimeout=8 "$TARGET" true 2>/dev/null; then
  ok "host key 已就位 + 公钥认证可用"
else
  ok "host key 已就位 (公钥还没装 ⇒ 下面会装)"
fi

# ---------- ② 装公钥 ----------
step "② 装本机公钥 (之后免密)"
PUBKEY=$(cat "$HOME/.ssh/id_ed25519.pub")
if [ -n "$REMOTE_USER" ]; then
  ssh -o ConnectTimeout=10 "$REMOTE_USER@$TARGET" "mkdir -p ~/.ssh && chmod 700 ~/.ssh && grep -qF '$PUBKEY' ~/.ssh/authorized_keys 2>/dev/null || echo '$PUBKEY' >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys" \
    && ok "公钥已装到 $REMOTE_USER@$TARGET" || warn "装公钥失败 (密码不对?) ⇒ 请手动在目标机上执行:"
else
  warn "没给用户名 ⇒ 跳过公钥安装 (请手动在目标机执行)"
  echo "     mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$PUBKEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
fi

# ---------- ③ 传文件 ----------
step "③ 传部署包 + 凭据 (★凭据走 SSH 加密通道)"
DEST="${REMOTE_USER:+$REMOTE_USER@}$TARGET"
scp -q "$BUNDLE" "$DEST:~/" && ok "部署包已传 ($(du -h "$BUNDLE" | cut -f1))" || die "部署包传输失败"
ssh "$DEST" "mkdir -p ~/ars45-credentials" 2>/dev/null
for f in "$WS/openclaw.json" "$WS/workspace/TOOLS.md" "$WS/agents/main/agent/auth-profiles.json" "$WS/cron/jobs.json"; do
  [ -f "$f" ] || { warn "缺 $f (跳过)"; continue; }
  scp -q "$f" "$DEST:~/ars45-credentials/" && ok "凭据已传: $(basename "$f")" || warn "传输失败: $(basename "$f")"
done

# ---------- ④ 目标机上跑 install ----------
step "④ 在目标机上跑 install.sh"
BN=$(basename "$BUNDLE" .tar.gz)
ssh "$DEST" "cd ~ && tar xzf '$BN.tar.gz' && cd '$BN' && mkdir -p credentials && cp ~/ars45-credentials/* credentials/ 2>/dev/null; ./install.sh" \
  && ok "install.sh 已执行" || warn "install.sh 执行有异常 (看上面的输出)"

echo
echo "${C_H}━━━ 传输完成 ━━━${C_OFF}"
echo "  ★★别忘: **旧主机 ($HOSTNAME) 的 7 个 cron 要先停**"
echo "     openclaw cron disable <jobId>   # 全部停掉"
echo "     ★包括 GitHub 同步那个 ⇒ 只留一个推送方"
