#!/usr/bin/env bash
# ISS-263 · STEP2: 装 rknn3-toolkit 1.2.0 wheel (md5 已校验) + 依赖
set -u
PY=~/miniconda3/envs/rknn3/bin/python
PIP=~/miniconda3/envs/rknn3/bin/pip
MARK=/var/tmp/iss263_rknn3/marks
mkdir -p "$MARK"
WHL=/var/tmp/iss263_rknn3/rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl

# ★ISS-263 坑 1: /tmp 是 7.5G tmpfs (只剩 1.8G) 且塞满别的 agent 的残留 ⇒ pip 解包 wheel 报 Errno 122 Disk quota exceeded
# ⇒ 把 TMPDIR 指向根分区 (/dev/sda2, 396G avail), 不删别人的 /tmp
export TMPDIR=/var/tmp/iss263_rknn3/tmp
mkdir -p "$TMPDIR"
export XDG_CACHE_HOME=/var/tmp/iss263_rknn3/cache
echo "=== ISS263 STEP2 start $(date -Is) ==="
echo "TMPDIR=$TMPDIR  (根分区, 绕开 /tmp tmpfs 配额)"
df -h /var/tmp | tail -1
md5sum "$WHL"
echo "--- pip install ---"
$PIP install --timeout 60 --retries 5 "$WHL" 2>&1
RC=$?
echo "STEP2_RC=$RC"
if [ $RC -eq 0 ]; then
  echo "OK rknn3-toolkit $($PIP show rknn3-toolkit 2>/dev/null | awk '/^Version:/{print $2}')" >> "$MARK/ok.txt"
fi
echo "=== final pip list $(date -Is) ==="
$PIP list 2>&1
echo "=== import 冒烟 $(date -Is) ==="
$PY -c "import rknn3; print('IMPORT_OK', getattr(rknn3,'__version__','n/a')); print(rknn3.__file__); print([n for n in dir(rknn3) if not n.startswith('_')])" 2>&1
echo "IMPORT_RC=$?"
echo "=== ISS263 STEP2 end $(date -Is) ==="
