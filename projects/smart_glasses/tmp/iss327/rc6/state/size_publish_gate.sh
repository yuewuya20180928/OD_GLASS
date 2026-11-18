#!/usr/bin/env bash
# size_publish_gate.sh —— ★**大文件发布闸 (独立可单测)**
# 用法:
#   bash state/size_publish_gate.sh <发布树> [--max-mb 50]      # 撤下所有超限文件 (rc 0 = 干净)
#   bash state/size_publish_gate.sh --selftest                  # 单测 (6 个分支, 含实测坏案例)
#
# ★★为什么必须有这道闸 (2026-11-17 06:1x 实测事故):
#   sw-lead 的 ISS250 (RKNN toolkit2 量化) 在源树 `logs/iss250_r6/` 留下 3 个 **245MB 的 .pkl**
#   (float.pkl / rknn3.pkl / tk2.pkl) ⇒ 发布脚本的 rsync **无尺寸上限** ⇒ 它们被抄进发布树
#   ⇒ `git add -A` 把它们 commit 进仓 ⇒ GitHub pre-receive 直接拒收:
#       remote: error: File .../rknn3.pkl is 245.14 MB; this exceeds GitHub's file size limit of 100.00 MB
#       remote: error: GH001: Large files detected. ... pre-receive hook declined
#   ⇒⇒ **远端历史没被压扁 (仍停在 6370aff)**, 但**每一轮重跑都会同样失败**
#     (rsync 每轮都把 .pkl 再抄回来 ⇒ git add -A 再 commit ⇒ push 再被拒)
#   ⇒⇒ ⇒ ★**这类 bug 必须修在产生点 (发布管线的 rsync + 提交前的尺寸闸), 不许在产物上擦**
#          (手删发布树里的 .pkl = 下一轮又被抄回来; 删源树的 .pkl = 毁掉 sw-lead 的工作产物)
#
# ★阈值取 50MB (GitHub 硬限是 100MB, 50MB 是它的警告线) ⇒ 宁可"宁可不入仓"也不让推送被拒
#   (仓库的定位是"状态 + 证据", 大二进制产物不入库; 想留的走 .json/.log/图 这些小证据)
# ★撤下动作 = `git rm --cached` (历史里保留) + 删工作区副本 (防 rsync 抄回后被 `git add -A` 加进仓)
#   ⇒ 与 board_publish_gate.sh 的 --withdraw 同构
set -u

MAX_MB=50
PUB=""
SELFTEST=0

# ---- 撤下: 超限文件 (磁盘实扫, 不依赖是否被 git 跟踪) ----
withdraw_big() {
  local pub="$1" max_bytes="$2"
  local out=0 size rel
  # ★用 find -printf '%s|%P' (字节 + 相对路径) 而不是 `find -size +Nc`
  #   ⇒ `-size` 是 512B 块向上取整 ⇒ 边界会算错 (差半个块)
  while IFS='|' read -r size rel; do
    [ -n "${rel:-}" ] || continue
    # ★先 untrack 再删文件: 顺序反了的话, `git rm --cached` 会因为"文件已不存在"而失败
    ( cd "$pub" && git rm -q -f --cached --ignore-unmatch -- "$rel" ) >/dev/null 2>&1 || true
    if rm -f "$pub/$rel" 2>/dev/null; then
      echo "WITHDRAW|$rel|$size"
    else
      echo "WITHDRAW_FAIL|$rel|$size"
      out=1
    fi
  done < <(find "$pub" -type f -not -path "$pub/.git/*" -printf '%s|%P\n' 2>/dev/null \
           | awk -F'|' -v m="$max_bytes" '$1+0 > m+0 {print}')
  return $out
}

# ============================================================================
# --selftest: 6 个分支 (★必须包含"实测坏案例"当回归用例 — AGENTS.md 铁律六★)
# ============================================================================
_selftest() {
  local pass=0 fail=0
  local ROOT; ROOT="$(mktemp -d /tmp/sizegate_selftest.XXXXXX)"
  chk() {  # chk <名> <期望> <实际>
    if [ "$2" = "$3" ]; then echo "  ✅ $1"; pass=$((pass+1));
    else echo "  ❌ $1 (期望 $2, 实得 $3)"; fail=$((fail+1)); fi
  }
  mkpub() {  # mkpub <目录>
    mkdir -p "$1"
    ( cd "$1" && git init -q -b main && git -c user.email=t@t -c user.name=t commit -qm init --allow-empty ) >/dev/null 2>&1
  }

  echo "[selftest] ① 无大文件 ⇒ 不动任何东西"
  PUBT="$ROOT/p1"; mkpub "$PUBT"
  echo "small" > "$PUBT/a.txt"
  OUT="$(bash "$0" "$PUBT" 2>&1)"; RC=$?
  chk "rc=0" 0 $RC
  [ -f "$PUBT/a.txt" ] && { echo "  ✅ 小文件保留"; pass=$((pass+1)); } || { echo "  ❌ 小文件被误删"; fail=$((fail+1)); }

  # ★★所有用例都用**小文件 + 显式小阈值** (逻辑等价, 磁盘压力≈0)
  #   ⇒ 第一版用真 245MB 文件做 git add -A ⇒ **把 tmpfs 撑爆, Bus error (core dumped)** ⇒
  #   ⇒ selftest 本身成了事故源 ⇒ 阈值参数化才是正解
  echo "[selftest] ② ★实测坏案例★ (超限 .pkl) ⇒ 必须撤下 (磁盘 + index)"
  PUBT="$ROOT/p2"; mkpub "$PUBT"
  mkdir -p "$PUBT/projects/smart_glasses/logs/iss250_r6"
  truncate -s 3M "$PUBT/projects/smart_glasses/logs/iss250_r6/rknn3.pkl"
  truncate -s 3M "$PUBT/projects/smart_glasses/logs/iss250_r6/float.pkl"
  truncate -s 3M "$PUBT/projects/smart_glasses/logs/iss250_r6/tk2.pkl"
  ( cd "$PUBT" && git add -A ) >/dev/null 2>&1
  OUT="$(bash "$0" "$PUBT" --max-mb 1 2>&1)"; RC=$?
  chk "rc=0" 0 $RC
  echo "$OUT" | grep -q "^WITHDRAW|" && { echo "  ✅ 输出了 WITHDRAW|"; pass=$((pass+1)); } || { echo "  ❌ 没输出 WITHDRAW|"; fail=$((fail+1)); }
  LEFT="$(find "$PUBT" -name '*.pkl' -not -path "$PUBT/.git/*" | wc -l)"
  chk "磁盘上 .pkl 剩 0" 0 "$LEFT"
  LEFTG="$(cd "$PUBT" && git ls-files | grep -c '\.pkl$' || true)"
  chk "index 里 .pkl 剩 0" 0 "$LEFTG"

  echo "[selftest] ③ 阈值内的文件 ⇒ 必须保留 (不能一刀切)"
  PUBT="$ROOT/p3"; mkpub "$PUBT"
  truncate -s 900K "$PUBT/keep.bin"
  OUT="$(bash "$0" "$PUBT" --max-mb 1 2>&1)"; RC=$?
  chk "rc=0" 0 $RC
  [ -f "$PUBT/keep.bin" ] && { echo "  ✅ 阈值内文件保留"; pass=$((pass+1)); } || { echo "  ❌ 被误删"; fail=$((fail+1)); }

  echo "[selftest] ④ 未跟踪的大文件 ⇒ 也要删 (rsync 抄回工作区后 git add -A 会把它加进仓)"
  PUBT="$ROOT/p4"; mkpub "$PUBT"
  truncate -s 2M "$PUBT/untracked_big.bin"
  OUT="$(bash "$0" "$PUBT" --max-mb 1 2>&1)"; RC=$?
  chk "rc=0" 0 $RC
  [ ! -f "$PUBT/untracked_big.bin" ] && { echo "  ✅ 未跟踪大文件已删"; pass=$((pass+1)); } || { echo "  ❌ 未跟踪大文件还在"; fail=$((fail+1)); }

  echo "[selftest] ⑤ .git 内部的大对象 ⇒ 不能动 (那是 git 自己的 pack, 不是工作区文件)"
  PUBT="$ROOT/p5"; mkpub "$PUBT"
  truncate -s 2M "$PUBT/.git/objects/pack/fake.pack"
  echo ok > "$PUBT/small.txt"
  OUT="$(bash "$0" "$PUBT" --max-mb 1 2>&1)"; RC=$?
  chk "rc=0" 0 $RC
  [ -f "$PUBT/.git/objects/pack/fake.pack" ] && { echo "  ✅ .git 内部文件未被动"; pass=$((pass+1)); } || { echo "  ❌ .git 内部文件被删了"; fail=$((fail+1)); }

  echo "[selftest] ⑥ 边界: 恰好等于阈值 ⇒ 保留 (超差判据是 > 不是 >=)"
  PUBT="$ROOT/p6"; mkpub "$PUBT"
  truncate -s 1048576 "$PUBT/exact.bin"
  OUT="$(bash "$0" "$PUBT" --max-mb 1 2>&1)"; RC=$?
  chk "rc=0" 0 $RC
  [ -f "$PUBT/exact.bin" ] && { echo "  ✅ 恰好等于阈值保留"; pass=$((pass+1)); } || { echo "  ❌ 等于阈值被误删"; fail=$((fail+1)); }

  echo "[selftest] 结果: $pass 通过 / $fail 失败"
  rm -rf "$ROOT"
  [ "$fail" = "0" ] || exit 1
  exit 0
}

# ---- 参数 ----
for a in "$@"; do
  case "$a" in
    --selftest) SELFTEST=1 ;;
    --max-mb) NEXT=1 ;;
    *) if [ "${NEXT:-0}" = "1" ]; then MAX_MB="$a"; NEXT=0; continue; fi
       PUB="$a" ;;
  esac
done
if [ "$SELFTEST" = "1" ]; then _selftest; exit $?; fi
[ -n "$PUB" ] || { echo "用法: size_publish_gate.sh <发布树> [--max-mb 50] | --selftest"; exit 2; }
[ -d "$PUB" ] || { echo "发布树不存在: $PUB"; exit 2; }

MAX_BYTES=$((MAX_MB * 1024 * 1024))
echo "SIZE_GATE|阈值 ${MAX_MB}MB"
withdraw_big "$PUB" "$MAX_BYTES"
RC=$?
if [ "$RC" = "0" ]; then
  echo "SIZE_GATE_OK|发布树里已无 >${MAX_MB}MB 的文件"
  exit 0
fi
echo "SIZE_GATE_FAIL|有超限文件删不掉 ⇒ 中止发布"
exit 1
