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

# ★★**2026-11-07 01:5x 兄弟实测复现的洞 (★修在产生点, 方案 B)**: ★**stderr 与 stdout 同流 ⇒
#   board_progress 中途抛异常 ⇒ Traceback 落在【尾部】⇒ 前缀天然干净 ⇒ ★**下游的前缀闸必然放行**
#   ⇒ 崩掉的事实被当成成功写进真值源 (★他沙箱实测: 旧块 1668 → 新块 1036, rc=0, 块里含 RuntimeError)
#   ⇒ 修法: ★**stderr 单独走一路; ★**非空 ⇒ 把 `<stderr>` 前缀 + 内容写进 $OUT (★让下游前缀闸立刻拦住)
#     + ★**本脚本退出码置 1 (★独立问题: 之前 board_progress 崩了, bcast_facts.sh 照样往下跑守卫/指纹/自验 ⇒ 守门人失职)****
# ★★**2026-11-07 02:2x 兄弟实测指出两点, 一并改**:
#   ★**① 固定名会竞态 (★同一脚本第 43 行的 _selftest_tmp 就用了 $$) ⇒ ★**23:4x 那条铁律明写"固定名在并发播报下会竞态" ⇒ ★**我新加的两个文件破了它自己刚立的规矩****
_ERR=/tmp/_bcast_facts_stderr_$$.txt
_RAW=/tmp/_bcast_facts_raw_$$.txt
python3 state/board_progress.py > "$_RAW" 2>"$_ERR"
_bc_failed=0
if [ -s "$_ERR" ]; then
  _bc_failed=1
  # ★★**2026-11-07 01:55 兄弟实测指出: ★**标记写【尾部】而注释说【顶部】⇒ 注释与行为不符 ⇒ 下游前缀闸看不见 ⇒ ★**⇒ 改成前置 (★让注释与行为一致)****
  {
    echo "<stderr>"
    cat "$_ERR"
    echo "--- board_progress.py stdout (★以下内容不可信, 整份作废) ---"
    cat "$_RAW"
  } > "$OUT"
  echo "★**board_progress.py 有 stderr ⇒ 事实不可信 ⇒ 已在 $OUT 【顶部】标 <stderr> ⇒ 下游闸门会拒绝写入**" >&2
  # ★★★**★2026-11-07 02:2x 兄弟实测指出: ★**我原先把 `exit 1` 放在脚本末尾 (★第 83 行) ⇒ 中间的【守卫】与
  #   【46.8s 完整自验 auto_release_if_ready.sh】照样跑 ⇒ ★**⇒ "崩了仍跑自验" 这件事并没有被治 (★只是最后退出了 1)
  #   ⇒ ★**⇒ 后果: ★**自验若刷新了 `.layout_done.json` 的 `at` ⇒ ★**又触发"留证变化 ⇒ 假播报"那一族 (★00:2x 刚治过一次的病, 从另一条路回来)
  #   ⇒ ★**⇒ 修法: ★**检测到 stderr 就【立刻退出】, 一行守卫/自验都不跑****
  rm -f "$_ERR" "$_RAW"
  echo "✗ bcast_facts.sh: board_progress.py 有 stderr ⇒ 事实不可信 ⇒ 立刻退出 (★不跑守卫, 不跑自验) ⇒ 退出码 1" >&2
  exit 1
else
  cp -f "$_RAW" "$OUT"
fi

# ★★2026-11-06 23:3x 【判据退化守卫的"下一节"】(★兄弟 23:3x 收尾建议)
#   ★**现状**: daily_check → daily_check --self-test ⇒ **自证** ⇒ ★**若有人把 --self-test 本身改坏, 没人拦**
#   ⇒ ★**这里给它一个外部消费者 (★播报侧 ⇒ 不动放行侧的 chain_gate, ★按之前定的留给老板/总工)**
#   ⇒ ★**每次播报都验一次 ⇒ 老板看得见这一行**
# ★★用唯一临时名 (★兄弟 23:4x 指出: 固定名在并发播报下会竞态)
_selftest_tmp="/tmp/_dc_selftest_$$.txt"
if python3 -B state/daily_check.py --self-test >"$_selftest_tmp" 2>&1; then
  echo "[守卫] 判据退化守卫 daily_check --self-test ✅" >> "$OUT"
else
  echo "[守卫] ★★判据退化守卫 daily_check --self-test ❌ (★有人改坏了判据或它自己的自测)" >> "$OUT"
  tail -3 "$_selftest_tmp" >> "$OUT" 2>&1
fi

# 板指纹 = [板] 行 "· " 之后的全部 (mtime · 大小 · 段数 · 孔数)
cur_fp=$(grep -m1 '^\[板\]' "$OUT" 2>/dev/null | sed 's/^\[板\][^·]*· *//')
prev_fp=""
if [ -f "$MEM" ]; then
  prev_fp=$(grep '^\[板\]' "$MEM" 2>/dev/null | tail -1 | sed 's/^\[板\][^·]*· *//')
fi
# ★★2026-11-07 00:2x (★兄弟撞出只跨零点触发的真 bug, ★根因在这里):
#   ★**跨零点后当天日记还不存在 ⇒ prev_fp 为空 ⇒ 每轮都走"板指纹有变"⇒ 每轮跑 46.8s 完整自验
#   ⇒ .layout_done.json 的 at 每轮推进 ⇒ [布线] 行逐字都在变 ⇒ ★**每轮都给老板发一条假播报**
#   ⇒ ★**根治: 兜底去翻"最近一个含 [板] 行的日记"** (★跨零点 / 新一天 / 当天没写过 ⇒ 都能正确回退)
if [ -z "$prev_fp" ]; then
  for _d in 1 2 3 4 5 6 7; do
    _md=$(date -d "-${_d} day" +%Y-%m-%d)
    _f="/home/yuewuya/.openclaw/workspace/memory/${_md}.md"
    if [ -f "$_f" ]; then
      prev_fp=$(grep '^\[板\]' "$_f" 2>/dev/null | tail -1 | sed 's/^\[板\][^·]*· *//')
      [ -n "$prev_fp" ] && break
    fi
  done
  [ -n "$prev_fp" ] && echo "★当天日记无 [板] 行 ⇒ 已回退到最近一份含 [板] 行的日记作基线" >> "$OUT"
fi

if [ -n "$cur_fp" ] && [ "$cur_fp" = "$prev_fp" ]; then
  echo "★板指纹未变 ⇒ 跳过重自验 (板 mtime/段数/孔数 与上次播报一致)" >> "$OUT"
else
  echo "── 板指纹有变 ⇒ 跑一次完整自验 (DRC + 门禁 + 投产包 + 盖章) ──" >> "$OUT"
  bash state/auto_release_if_ready.sh >> "$OUT" 2>&1
  echo "── 自验结束 (rc=$?) ──" >> "$OUT"
fi
rm -f "$_selftest_tmp" "$_ERR" "$_RAW"
if [ "$_bc_failed" = "1" ]; then
  echo "✗ bcast_facts.sh: board_progress.py 有 stderr ⇒ 事实不可信 ⇒ 退出码 1 (★崩掉的事实不许进块)" >&2
  exit 1
fi

cat "$OUT"
