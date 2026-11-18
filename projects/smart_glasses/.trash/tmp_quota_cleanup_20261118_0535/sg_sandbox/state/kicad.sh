#!/usr/bin/env bash
# kicad.sh —— 免 root 的 KiCad 10.0.8 调用封装 (AppImage 解包版)
# ★为什么不用系统包: 本机 sudo 要密码 ⇒ 走官方 AppImage (kicad-downloads.s3.cern.ch / 阿里云镜像)
# ★AppImage 解包目录 (1.7G): /home/yuewuya/kicad/squashfs-root
KC_ROOT=/home/yuewuya/kicad/squashfs-root
export LD_LIBRARY_PATH="$KC_ROOT/usr/lib:${LD_LIBRARY_PATH:-}"
exec "$KC_ROOT/usr/bin/kicad-cli" "$@"
