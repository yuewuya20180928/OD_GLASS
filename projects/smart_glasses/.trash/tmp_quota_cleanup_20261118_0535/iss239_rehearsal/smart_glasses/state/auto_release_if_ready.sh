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
BOARD_SEG="$(grep -c '(segment' "$PCB_FILE" 2>/dev/null | head -1)"; BOARD_SEG="${BOARD_SEG:-0}"
# ★★2026-11-05 04:32 **板侧判据 (不依赖"当前在跑那一轮"的日志)**
#   问题: 一落盘就起下一轮 ⇒ detect_live_log() 只能看到**下一轮**的日志 ⇒ ★**上一轮那块板永远不会被量一遍**
#   ⇒ 修法: 官方板 mtime 比留证文件新 + 板有走线 + ★这块板还没被量过 (marker) ⇒ 也触发自验
BM="$(stat -c %Y "$PCB_FILE" 2>/dev/null | head -1)"; BM="${BM:-0}"
EM="$(stat -c %Y "HW/PCB/.layout_done.json" 2>/dev/null | head -1)"; EM="${EM:-0}"
M0="$(cat state/.verified_board_mtime 2>/dev/null | head -1)"; M0="${M0:-0}"
# ★★2026-11-05 06:30 **"落盘时刻闸"** (同事提的待办②) —— ★**防止量到被中途存盘覆盖的坏板**
#   事故事实: 05:57 官方板被**中途落盘**覆盖成骨架 (mtime=05:50) ⇒ 板侧判据照样触发自验
#   ⇒ 留证 .layout_done.json 被写成 tracks=0 ⇒ ★**自己污染了自己的证据** (06:08 才自愈)
#   ⇒ 判据: 落盘时刻印 .layout_landed.json 的 {at, tracks} 必须与盘上的板对得上
#     ① |板 mtime - at| <= 10s   (盘上的板就是刚落的那块, 不是后来被改的)
#     ② 板当前走线段数 == 印里的 tracks (段数对不上 ⇒ 板被改过)
LAND_JSON="HW/PCB/.layout_landed.json"
LAND_OK=0
if [ -f "$LAND_JSON" ]; then
  L_AT="$(python3 -c 'import json,sys;print(int(json.load(open(sys.argv[1])).get("at",0)))' "$LAND_JSON" 2>/dev/null || echo 0)"
  L_TR="$(python3 -c 'import json,sys;print(int(json.load(open(sys.argv[1])).get("tracks",0)))' "$LAND_JSON" 2>/dev/null || echo 0)"
  if [ "${L_AT:-0}" -gt 0 ] && [ "$BM" -gt 0 ]; then
    D=$(( BM > L_AT ? BM - L_AT : L_AT - BM ))
    if [ "$D" -le 10 ] && [ "${BOARD_SEG:-0}" -eq "${L_TR:-0}" ]; then
      LAND_OK=1
    else
      echo "  ⚠️ 落盘时刻闸: 板 mtime=$BM vs 落盘 at=$L_AT (差 ${D}s) · 板段数=${BOARD_SEG} vs 落盘段数=${L_TR} ⇒ ★**板被中途存盘改过 ⇒ 不许量**"
    fi
  fi
else
  echo "  (注: 无 .layout_landed.json ⇒ 落盘时刻闸不可用 (该印 06:30 才加))"
fi
if [ "$LANDED" -eq 1 ] && [ ! -f "$LAND_JSON" ] && [ "${BM:-0}" -le "${M0:-0}" ]; then LAND_OK=1; fi   # ★老板无印 ⇒ 只放行"已经量过的那块板"一次 (★新板不许走无印通道)
if [ "$BM" -gt "$EM" ] && [ "$BM" -gt "$M0" ] && [ "${BOARD_SEG:-0}" -ge 1 ] && [ "$LAND_OK" -eq 1 ]; then
  LANDED=1
  echo "  (板侧判据: 官方板 mtime=$BM > 留证=$EM ⇒ 有一轮落盘但没量过 ⇒ 触发自验)"
fi
# ★★2026-11-05 07:0x **补洞: 日志触发的自验也必须过"落盘时刻闸"** (★只对"新板"要求)
#   事故事实: 上一轮日志里永远留着 "已原子替换正式板" ⇒ 没有在跑的轮次时, 指针 fallback 会拿到**旧日志**
#   ⇒ LANDED=1 ⇒ ★**对一块被中途落盘覆盖过的板自验** ⇒ .layout_done.json 被写成垃圾 ⇒ 自己污染自己的证据
#   ⇒ 现在: 板比"上次量过的板"新 (BM > M0) 时, 落盘时刻闸对不上 ⇒ **一律不许量**
if [ "$LANDED" -eq 1 ] && [ "${BM:-0}" -gt "${M0:-0}" ] && [ "$LAND_OK" -eq 0 ]; then
  echo "  ⚠ 日志说落盘了, 但板 mtime=$BM 比上次量过的板 ($M0) 新 且**落盘时刻闸对不上** ⇒ ★**不许量** (等真正落盘的一轮)"
  LANDED=0
fi
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
# ★★★2026-11-05 10:05 **互斥锁: 同一时刻只允许一个自验在跑**
#   ★**为什么**: 10 分钟播报 cron 每轮都调本脚本 ⇒ 一旦板落盘, 自验要 10~15 分钟 (DRC+门禁+投产包)
#     ⇒ ★**下一轮 cron 触发的自验会重叠** ⇒ CPU 被抢 + 多个自验同时写 .layout_done.json (证据被冲)
#     ⇒ 实测症状: cron 播报在 10:00 送来 **09:05 / 09:10 的旧快照** ⇒ 就是排队堆积
#   ⇒ ★**锁**: state/.auto_release.lock (目录) ⇒ 拿不到锁就直接退出 (不排队, 不重复烧 CPU)
LOCK=state/.auto_release.lock
if ! mkdir "$LOCK" 2>/dev/null; then
  # ★锁可能是上次被杀留下的 ⇒ 检查里面的 PID 是否还活着
  LPID=$(cat "$LOCK/pid" 2>/dev/null | head -1 | tr -d ' ')
  if [ -n "${LPID:-}" ] && kill -0 "$LPID" 2>/dev/null; then
    echo "⏳ 已有自验在跑 (PID $LPID) ⇒ ★**本轮跳过自验** (不排队, 不重复烧 CPU)"
    exit 0
  fi
  rm -rf "$LOCK" 2>/dev/null || true
  mkdir -p "$LOCK" 2>/dev/null || true
fi
echo $$ > "$LOCK/pid"
# ★退出时释放锁 (无论成败)
trap 'rm -rf "$LOCK" 2>/dev/null || true' EXIT
bash state/verify_and_release.sh > /tmp/auto_release.log 2>&1
rc=$?
# ★记住"这块板已经量过" ⇒ 防止下一轮 cron 又拿同一块板重跑一遍自验 (白烧 CPU)
echo "${BM}" > state/.verified_board_mtime
# ★★★2026-11-05 09:20 **关键修正: "量过" ≠ "验过且通过"**
#   实测事故: v25 (焊盘短路 + DRC 2 + unconnected 82) 的自验 rc=1 ⇒ 但上面那句**无条件**写了
#   `.verified_board_mtime` ⇒ 而发布闸把"板 mtime ≤ 已量过的板"当**通过** ⇒⇒
#   ⇒⇒ **带短路的板 + 它出的 30 个 Gerber 被推进了 GitHub** (commit f31814b) ⇒⇒ 门禁形同虚设
#   ⇒⇒ **修法: 两个标记分工**
#     · `.verified_board_mtime`     = **量过** (不管过没过) ⇒ 只用于"别重复烧 CPU"
#     · `.verified_board_ok_mtime`  = **验过且通过 (rc=0)** ⇒ ★**只有这个能授权发布**
if [ "$rc" -eq 0 ]; then
  echo "${BM}" > state/.verified_board_ok_mtime
  echo "  ✓ 板通过自验 ⇒ 写 .verified_board_ok_mtime=$BM (★此标记才授权发布)"
else
  rm -f state/.verified_board_ok_mtime
  echo "  ✗ 自验 rc=$rc ⇒ ★**不写** .verified_board_ok_mtime (⇒ 发布闸会拦这块板)"
fi
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
