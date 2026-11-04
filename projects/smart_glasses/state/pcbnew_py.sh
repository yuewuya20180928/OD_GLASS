#!/usr/bin/env bash
# pcbnew_py.sh —— 用 KiCad AppImage 自带的 python 跑脚本 (pcbnew 模块只在它里面)
KC_ROOT=/home/yuewuya/kicad/squashfs-root
export LD_LIBRARY_PATH="$KC_ROOT/usr/lib:${LD_LIBRARY_PATH:-}"
export PYTHONPATH="$KC_ROOT/usr/lib/python3/dist-packages:$KC_ROOT/usr/lib:${PYTHONPATH:-}"
# ★★2026-11-05 07:0x **加 -u (无缓冲)** —— ★**日志不流出来 = 监控全瞎**
#   事故事实: A/B 两轮跑了 44 分钟, /tmp/gen_v23_8l.log 与 /tmp/gen_v24_6l.log **都是 0 字节**
#   ⇒ python 重定向到文件时是**块缓冲 (8KB)** ⇒ 进度 print 全卡在用户态缓冲区里
#      ⇒ ① 人看不到进度 (以为卡死了) ② auto_release 盯的 "已原子替换正式板" 标记迟迟不出现 ⇒ 触发器失灵
#   ⇒ -u ⇒ 逐行实时落盘
exec "$KC_ROOT/usr/bin/python3.11" -u "$@"
