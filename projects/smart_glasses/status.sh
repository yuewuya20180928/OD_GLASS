#!/usr/bin/env bash
# 手动触发: 项目状态总览 (整体进展 / 待办 / 卡点 / 风险)
# 用法: ./status.sh                一屏看板
#       ./status.sh --json         机读
#       ./status.sh hw-lead        只看某个总工 (hw-lead|sw-lead|mech-lead)
cd "$(dirname "$0")" || exit 2
case "${1:-}" in
  hw-lead|sw-lead|mech-lead) exec python3 state/status.py --agent "$1" ;;
  *) exec python3 state/status.py "$@" ;;
esac
