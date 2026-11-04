#!/usr/bin/env bash
# auto_release_if_ready.sh —— ★布线落盘后自动"自验 + 放行" (2026-11-05 06:00)
# 用法: bash state/auto_release_if_ready.sh
# 行为: 若 v15 日志出现 EXIT= 且尚未放行 ⇒ 跑 verify_and_release.sh ⇒ 写留证 ⇒ 推 GitHub ⇒ 打出摘要
#       若还没落盘 ⇒ 只打印一行"还在跑"
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
# ★★2026-11-05 03:25 修: **原来写死 /tmp/gen_v15.log** ⇒ v15 早就有 EXIT= ⇒ 脚本每轮都拿
#   **旧日志**去对**当前板文件**做自验 ⇒ 一直测的是被 8 层实验覆盖的坏板 (343/13) ⇒ 白费 CPU + 误导老板
#   ⇒ 现在: **指针文件** state/.current_gen_log 指向"当前这一轮"的日志 (启动时写)
# ★★2026-11-05 04:15 修 (第 2 次同款病): 指针文件 **失真** ⇒ 触发器盯的是**上一轮被 kill 的日志**
#   现场: .current_gen_log 还指着 /tmp/gen_v17.log (v17 是 04:04 手动杀的 ⇒ 日志里是 EXIT=143)
#   ⇒ 脚本看到 "EXIT=" 就认定"已落盘" ⇒ 每轮 cron 都在 **0 走线骨架板** 上白跑一遍 verify
#   ⇒ 还会把留证 .layout_done.json 覆写成骨架板的数 (本轮实测 343/13/tracks=0)
#   ⇒ 修法A: 优先**探测当前真正在跑的那一轮**的日志 (扫 /proc/*/cmdline 里的 `> /tmp/gen_*.log`)
#   ⇒         —— 指针只是 fallback, 因为手动启动 (不经过 run_board_gen.sh) 不会更新指针
#   ⇒ 修法B: 触发条件从"出现 EXIT=" 收紧为 "**EXIT=0**"
#   ⇒         —— 143=SIGTERM(被杀) / 124=timeout ⇒ 这轮**没落盘**, 不能拿来触发自验
detect_live_log() {
  local f cmd lg
  for f in /proc/[0-9]*/cmdline; do
    cmd="$(tr '\0' ' ' < "$f" 2>/dev/null || true)" || continue
    case "$cmd" in
      *gen_pcb_netlist_board.py*)
        lg="$(printf '%s' "$cmd" \
          | grep -oE '>[[:space:]]*/tmp/gen_[A-Za-z0-9_.-]+\.log' \
          | head -1 | sed 's/^>[[:space:]]*//')"
        if [ -n "$lg" ] && [ -f "$lg" ]; then printf '%s\n' "$lg"; return 0; fi
        ;;
    esac
  done
  return 1
}
LOG="$(detect_live_log || true)"
if [ -z "$LOG" ] || [ ! -f "$LOG" ]; then
  LOG="$(cat state/.current_gen_log 2>/dev/null || true)"
fi
if [ -z "$LOG" ] || [ ! -f "$LOG" ]; then
  LOG="$(ls -t /tmp/gen_*.log 2>/dev/null | head -1)"
fi
# 指针对齐到"当前在跑的那一轮", 供下一轮 fallback 使用
if [ -n "$LOG" ] && [ -f "$LOG" ]; then echo "$LOG" > state/.current_gen_log; fi
STAMP=state/.auto_release_done
echo "★盯的日志: ${LOG:-<无>}"
echo "=== 机器读数 (board_progress.py) ==="
python3 state/board_progress.py 2>/dev/null
# ★★触发条件: **"这一轮真的落盘了"** (不只看退出码!)
#   EXIT=143 ⇒ 被 SIGTERM 杀掉 (手动 kill / 超时) ⇒ 这轮没落盘 ⇒ **不许**触发自验
#   EXIT=124 ⇒ timeout 到点            ⇒ 同上
#   ★★2026-11-05 04:20 **不能只认 EXIT=0**: 脚本退出码把"布线成功"和"网表 parity 全过"混在一起
#     (实测 v15: 布线成功 92/17, 但 parity 缺失14/多余12 ⇒ 退出码 1 ⇒ ★**永远不会触发自验**)
#   ⇒ 改用**落盘标记** "✓ 已原子替换正式板" (原子替换成功后立刻打印) ⇒ **这才是"板真的换了"的证据**
#   ⇒ 再加一道硬闸: 官方板必须**真的有走线** (>0 segment) ⇒ 骨架板/空板一律不许自验
PCB_FILE="HW/PCB/demo_mainboard.kicad_pcb"
LANDED=0
if grep -q "已原子替换正式板" "$LOG" 2>/dev/null; then LANDED=1; fi
if grep -q "EXIT=0" "$LOG" 2>/dev/null; then LANDED=1; fi
BOARD_SEG="$(grep -c '(segment' "$PCB_FILE" 2>/dev/null || echo 0)"
if [ "$LANDED" -ne 1 ]; then
  RC_SEEN="$(grep -oE 'EXIT=[0-9]+' "$LOG" 2>/dev/null | tail -1 || true)"
  echo "还在跑: $(ps -o etime= -C python3.11 2>/dev/null | tail -1 | tr -d ' ') (日志无落盘标记${RC_SEEN:+ · 上次退出码 $RC_SEEN ⇒ 未落盘, 不触发自验})"
  exit 0
fi
if [ "${BOARD_SEG:-0}" -lt 1 ]; then
  echo "⚠️ 日志说落盘了, 但官方板 $PCB_FILE 只有 $BOARD_SEG 段走线 ⇒ 判定为**空板** ⇒ 不触发自验 (等下一轮)"
  exit 0
fi
if [ -f "$STAMP" ]; then
  echo "已放行过 (stamp $STAMP): $(cat $STAMP)"
  exit 0
fi
echo "★落盘了 ⇒ 开始自验+放行"
bash state/verify_and_release.sh > /tmp/auto_release.log 2>&1
rc=$?
grep -E "DRC violations|unconnected items|C3 DRC|C4 unconnected|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|缺失|多余" /tmp/auto_release.log | head -24
echo "--- 差分对审计 (前 12 行) ---"
grep -E "缺:|净距=|Δ" /tmp/auto_release.log | head -14
# ★★2026-11-05 03:15 **修 stamp bug**: 之前**无条件盖章 + 无条件打印"已放行"** ⇒
#   一轮 rc=1 的失败自验会盖上"已放行"章 ⇒ 之后永远不会再自验 ⇒ ★**失败就不许盖章**
if [ "$rc" -eq 0 ]; then
  date "+%Y-%m-%dT%H:%M:%S" > "$STAMP"
  echo "✓ 已放行 (verify rc=0)"
else
  rm -f "$STAMP"
  echo "❌ 未通过 (verify rc=$rc) ⇒ ★**不盖章** ⇒ 下一轮会重跑自验 (可重复)"
fi
