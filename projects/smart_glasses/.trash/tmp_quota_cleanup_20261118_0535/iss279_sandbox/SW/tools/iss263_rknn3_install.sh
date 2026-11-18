#!/usr/bin/env bash
# ISS-263 · rknn3-toolkit 1.2.0 安装脚本 (独立 conda env: ~/miniconda3/envs/rknn3, python 3.10)
# ★纪律: 每装完一个包就追加 "OK <pkg> <ver>" 到 marker 目录, 被掐也不丢进度 ★
set -u
PY=~/miniconda3/envs/rknn3/bin/python
PIP=~/miniconda3/envs/rknn3/bin/pip
MARK=/var/tmp/iss263_rknn3/marks
mkdir -p "$MARK"

echo "=== ISS263 install start $(date -Is) ==="
echo "### $PIP --version"; $PIP --version 2>&1
echo "### $PY -V"; $PY -V 2>&1

echo "=== STEP1: torch==2.4.0+cpu (pytorch cpu index, 避免 CUDA 巨物) $(date -Is) ==="
$PIP install --timeout 60 --retries 5 "torch==2.4.0+cpu" \
  --index-url https://download.pytorch.org/whl/cpu 2>&1
RC1=$?
echo "STEP1_RC=$RC1"
if [ $RC1 -eq 0 ]; then
  echo "OK torch $($PIP show torch 2>/dev/null | awk '/^Version:/{print $2}')" >> "$MARK/ok.txt"
fi

echo "=== STEP2: rknn3-toolkit wheel (local file, md5 已校验) $(date -Is) ==="
$PIP install --timeout 60 --retries 5 /var/tmp/iss263_rknn3/wheel.whl 2>&1
RC2=$?
echo "STEP2_RC=$RC2"
if [ $RC2 -eq 0 ]; then
  echo "OK rknn3-toolkit $($PIP show rknn3-toolkit 2>/dev/null | awk '/^Version:/{print $2}')" >> "$MARK/ok.txt"
fi

echo "=== STEP3: 最终 pip list $(date -Is) ==="
$PIP list 2>&1
echo "=== STEP4: import 冒烟 $(date -Is) ==="
$PY -c "import rknn3; print('IMPORT_OK', getattr(rknn3,'__version__','n/a'), rknn3.__file__)" 2>&1
echo "IMPORT_RC=$?"
echo "=== ISS263 install end $(date -Is) ==="
