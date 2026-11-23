#!/usr/bin/env bash
# ★ISS-368 · 沙盒构建 (★项目盘 tmp/ 下的真副本·禁止软链★)
#   用法: build_sbx.sh <项目根> <沙盒目录>
#   ★**只复制判据要读的那几件 + 它们依赖的目录** ★ · ★**不复制 tmp/ logs/ .trash/ 大件★ ★
set -eu
ROOT="${1:?root}"
SBX="${2:?sbx}"
mkdir -p "$SBX"

copy_dir() {   # copy_dir <相对路径>
  local rel="$1"
  [ -e "$ROOT/$rel" ] || return 0
  mkdir -p "$SBX/$rel"
  ( cd "$ROOT/$rel" && find . -type f ! -name '*.pyc' ! -path '*/__pycache__/*' -print0 ) \
    | while IFS= read -r -d '' f; do
        mkdir -p "$SBX/$rel/$(dirname "$f")"
        cp -p "$ROOT/$rel/$f" "$SBX/$rel/$f"
      done
}

copy_file() {  # copy_file <相对路径>
  local rel="$1"
  [ -f "$ROOT/$rel" ] || return 0
  mkdir -p "$SBX/$(dirname "$rel")"
  cp -p "$ROOT/$rel" "$SBX/$rel"
}

# ---- 目录 ----
for d in SW HW MECH config deploy docs REF REQ FRAMEWORK PRINT; do
  copy_dir "$d"
done
mkdir -p "$SBX/state"
for d in state/fragments state/tasks state/fixtures state/gate_snapshots state/outbox state/measurements.yaml; do
  [ -e "$ROOT/$d" ] && copy_dir "$d"
done

# ---- state 根下的散文件 (★排除 .bak_* 大件·排除 _os_snapshots★) ----
( cd "$ROOT/state" && find . -maxdepth 1 -type f ! -name '*.bak*' ! -name '*.pyc' -print0 ) \
  | while IFS= read -r -d '' f; do cp -p "$ROOT/state/$f" "$SBX/state/$f"; done

# ---- 根下的散文件 (★排除 *.onnx 大件·排除 .bak_*★) ----
( cd "$ROOT" && find . -maxdepth 1 -type f ! -name '*.onnx' ! -name '*.bak*' ! -name '*.pyc' -print0 ) \
  | while IFS= read -r -d '' f; do cp -p "$ROOT/$f" "$SBX/$f"; done

# ---- 沙盒自己的 tmp (★子进程 TMPDIR 指这儿·避系统临时目录配额★) ----
mkdir -p "$SBX/tmp"

echo "沙盒 = $SBX"
du -sh "$SBX"
