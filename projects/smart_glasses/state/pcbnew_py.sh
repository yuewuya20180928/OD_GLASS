#!/usr/bin/env bash
# pcbnew_py.sh —— 用 KiCad AppImage 自带的 python 跑脚本 (pcbnew 模块只在它里面)
KC_ROOT=/home/yuewuya/kicad/squashfs-root
export LD_LIBRARY_PATH="$KC_ROOT/usr/lib:${LD_LIBRARY_PATH:-}"
export PYTHONPATH="$KC_ROOT/usr/lib/python3/dist-packages:$KC_ROOT/usr/lib:${PYTHONPATH:-}"
exec "$KC_ROOT/usr/bin/python3.11" "$@"
