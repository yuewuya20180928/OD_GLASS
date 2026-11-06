#!/usr/bin/env bash
# bcast_facts.sh —— ★**播报取事实 (轻量) + 只有"板变了"才跑重自验** (2026-11-05 12:40)
# ★**为什么拆开**: 10 分钟播报 job 的 payload 里原来直接跑 `state/auto_release_if_ready.sh`
#   ⇒ ★**那一跑要 8 分钟** (自验里含一次 KiCad DRC) ⇒ ★**加上模型回合 ⇒ 撞 600s 超时**
#   ⇒ 实测 11-05 12:11 那轮: status=error, error="cron: job execution timed out (last phase: tool-execution-started)"
#   ⇒ 后果: ★**老板的 10 分钟进展窗口连续挂 5 轮** (run 状态 error ⇒ 看板上没进展)
# ★**新做法**: 事实用 `state/board_progress.py` 取 (★实测 **0.111 秒**)
#   ⇒ 板指纹 (mtime/段数/孔数) 与上次播报相同 ⇒ ★**跳过重自验** (板没变, 自验结果也不会变)
#   ⇒ 板指纹变了 ⇒ ★**才跑一次** `auto_release_if_ready.sh` (自验 + 放行盖章), 输出并进事实文件
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
OUT=/tmp/_bcast_facts.txt
MEM=/home/yuewuya/.openclaw/workspace/memory/$(date +%Y-%m-%d).md

python3 state/board_progress.py > "$OUT" 2>&1

# ★★2026-11-06 23:3x 【判据退化守卫的"下一节"】(★兄弟 23:3x 收尾建议)
#   ★**现状**: daily_check → daily_check --self-test ⇒ **自证** ⇒ ★**若有人把 --self-test 本身改坏, 没人拦**
#   ⇒ ★**这里给它一个外部消费者 (★播报侧 ⇒ 不动放行侧的 chain_gate, ★按之前定的留给老板/总工)**
#   ⇒ ★**每次播报都验一次 ⇒ 老板看得见这一行**
if python3 -B state/daily_check.py --self-test >/tmp/_dc_selftest.txt 2>&1; then
  echo "[守卫] 判据退化守卫 daily_check --self-test ✅" >> "$OUT"
else
  echo "[守卫] ★★判据退化守卫 daily_check --self-test ❌ (★有人改坏了判据或它自己的自测)" >> "$OUT"
  tail -3 /tmp/_dc_selftest.txt >> "$OUT" 2>&1
fi

# 板指纹 = [板] 行 "· " 之后的全部 (mtime · 大小 · 段数 · 孔数)
cur_fp=$(grep -m1 '^\[板\]' "$OUT" 2>/dev/null | sed 's/^\[板\][^·]*· *//')
prev_fp=""
if [ -f "$MEM" ]; then
  prev_fp=$(grep '^\[板\]' "$MEM" 2>/dev/null | tail -1 | sed 's/^\[板\][^·]*· *//')
fi

if [ -n "$cur_fp" ] && [ "$cur_fp" = "$prev_fp" ]; then
  echo "★板指纹未变 ⇒ 跳过重自验 (板 mtime/段数/孔数 与上次播报一致)" >> "$OUT"
else
  echo "── 板指纹有变 ⇒ 跑一次完整自验 (DRC + 门禁 + 投产包 + 盖章) ──" >> "$OUT"
  bash state/auto_release_if_ready.sh >> "$OUT" 2>&1
  echo "── 自验结束 (rc=$?) ──" >> "$OUT"
fi

cat "$OUT"
