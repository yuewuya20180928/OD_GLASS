#!/usr/bin/env bash
# replay_patch_chain.sh -- ★★★**复现"官方板补丁链" (★2026-11-09 02:5x)** ★★★
#
# ★★★**为什么要有这个脚本 (★今晚最贵的教训)****
#   ★**官方板 = 路由阶段(13407 段) + 一串补丁(→18092 段, unc 45, DRC 0)** ⇒ ★**不是一次路由出来的**
#   ★⇒ ★**任何臂的候选板若只跑【最后一步补丁】, 就跟官方终板【不是同工艺】⇒ 四把尺子会刷出一堆假失败**
#   ★**今晚实测**: ★**对照臂 v76 (★根本没做任何改动) 也被闸门 REJECT (★2 对死腿 + 11 个碎裂网)** ⇒ ★**⇒ 那批失败全是基线不可比**
#
# ★★★**2026-11-09 04:5x 实测订正 (★md5 血缘 + 逐段复现 ⇒ 本注释是【实测结论】不是推测)** ★★★
#
# ★**官方链真实血缘 (★用 md5 + 各步日志首行的"输入路径/图元数"双向锁死)**:
#   ┌ 官方 _straight7 (md5 8b33af51 · 17022 段 / 17430 图元)
#   │   → combo     : patch_astar_nostub grid 0.125 ★**margin 0.20**  (★补上 6 条 ⇒ 17585 段 / 18008 图元, md5 3267a6df)
#   │   → loose     : patch_astar_nostub grid 0.125 ★**margin 0.0625** (★补上 3 条 ⇒ ★★18092 段 = 现在的官方板, md5 611b869e)
#   └─ ★**这两步已实测逐字节复现官方终板** (★几何+层+网集合 17980 条全同 / DRC 0 / unc 45 / 字节数 4940213 一致)
#
# ★★★**★★上一版(02:5x)写错了两处 ⇒ 链走岔 ⇒ 17731 段 ≠ 18092 (★实测)** ★★★:
#   ① ★**顺序错**: ★**把 `_nostub125`(17619 段) 当链的第①步** ⇒ ★★**那是【死支】** ★★
#     ★**证据**: ★**md5 对照** ⇒ `_nostub125` = `board_nostub125_unc50`(17430→18042 图元) 与官方终板**无祖先关系**;
#     ★**且它自己的日志首行写的是 "输入 = HW/PCB/demo_mainboard.kicad_pcb"** ⇒ ★**它是【拿终板当输入跑的实验】不是链的一环**
#   ② ★**参数错**: ★**combo 步的 margin 是 0.20, 不是 0.125** ⇒ ★**用 0.125 会多补 CSI_D0_D0_P/VDD_3V3_IO/PWR_GOOD(15.127)**
#     ★**证据**: ★**官方 `_combo.log` 的 6 条补上清单与 margin=0.20 跑出来的【逐条一致】** (★0.125 多出 3 条 ⇒ 不一致)
#
# ★★★**自校准 (★本脚本的正确性判据 —— 不靠"我觉得对不对")****:
#   ★**用法**: `bash state/replay_patch_chain.sh <路由产物板> <标签> [--validate]`
#   ★**--validate 模式**: ★**拿【已知的官方链中段板】(`/tmp/_straight7.kicad_pcb`) 重放 combo+loose 两步**
#     ⇒ ★**结果必须与官方终板逐段数一致 (⇒ 18092 段 / unc 45 / DRC 0) ⇒ 参数对了**
#     ⇒ ★**★没复现出来之前, 这个脚本产出的板不许拿去跟官方比** (★否则又是拿苹果比橘子)
#   ★★★**2026-11-09 04:5x 新增: `--self-test` 闸 (★链跑完自动比对官方终板 ⇒ 不一致就 rc≠0 ⇒ 不许拿去比)** ★★★
#
# ★**每步都要【该板自己的 fresh DRC】当输入** (★补丁器靠 DRC.json 里的 unconnected_items 找活)
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

# ★★★★**★2026-11-11 09:0x 新增: 官方链 stage-1 板的 md5 (★自校准闸分档要用【输入的性质】, 不能用【过程量】★)** ★★★★
# ★★★★**★为什么 (★实测: offverify 那轮被判错档 ⇒ "闸门形同虚设"又一起实例★)**: ★★★
#   ★**原分档只看 `SKIP_STRAIGHT` (★"这轮有没有跑 straight 步"这个【过程量】★)**
#   ⇒ ★**offverify 明明拿的就是官方 stage-1 (md5 8b33af51 · 17022 段), 却因"没带 --validate"被判成【档②】★★**
#   ⇒ ★★**⇒ 档① 的严格比对 (几何 + unc 网名集合) 根本没跑 ⇒ 闸只报了段数/unc/DRC 就放行 ⇒ 闸门形同虚设 ★★**
#   ⇒ ★★**⇒ 而且档② 那句理由自相矛盾**: "输入是【路由产物】(17022 段) ⇒ 当前路由器只出 17022 段 ⇒ 路由器代码已漂移" ★★
OFFICIAL_S1_MD5="8b33af5181e8d80ef471c6d1f59298e6"

# ★★★★**★2026-11-11 09:0x: 自校准闸分档判据 (★唯一实现★) ⇒ $1=输入md5 $2=输入段数 $3=VALIDATE标记 ⇒ echo 1|2 ★★★★
# ★**档① = 输入就是【官方链 stage-1 板】(md5 命中) ⇒ 它的链产物【必须逐条复现官方终板】**
# ★**档② = 输入是【路由产物】⇒ 只能判 DRC/unc, ★不许宣称"与官方同工艺"**
pick_grade() {
  local md5="$1" segi="$2" val="${3:-}"
  if [ "$md5" = "$OFFICIAL_S1_MD5" ]; then echo 1; return 0; fi
  if [ "$val" = "--validate" ] && [ "$segi" -ge 17000 ]; then echo 1; return 0; fi
  echo 2
}

# ★★★★**★2026-11-11 09:0x 新增: `--self-test` (★分档判据必须能证伪★) ★★★★
# ★**为什么 (★"闸要能证伪"铁律★)**: ★**分档判据刚被改过 (★从"过程量"改成"输入性质"★) ⇒ 必须有独立用例证明改对了★★**
#   ★★**⇒ 而且必须带【反向用例】(★把判据改弱 ⇒ 自测必须红★)****
if [ "${1:-}" = "--self-test" ]; then
  fail=0
  chk() { # $1=名字 $2=期望档 $3=实际档
    if [ "$2" = "$3" ]; then echo "  ✅ $1 ⇒ 档$3"; else echo "  ❌ $1 ⇒ 期望档$2 实得档$3"; fail=1; fi
  }
  echo "★自校准闸分档判据自测 (★测的就是 pick_grade 本体, 不是副本★)"
  chk "官方 stage-1 板 (★offverify 那轮的真实情况★)" 1 "$(pick_grade "$OFFICIAL_S1_MD5" 17022 "")"
  chk "同段数但不是官方 stage-1 (★证明不靠段数★)" 2 "$(pick_grade "deadbeef00000000000000000000000000" 17022 "")"
  chk "--validate + 17022 段" 1 "$(pick_grade "deadbeef00000000000000000000000000" 17022 "--validate")"
  chk "路由产物臂 14023 段 (★必须仍走档②★)" 2 "$(pick_grade "deadbeef00000000000000000000000000" 14023 "")"
  chk "官方 stage-1 就算段数不对也走档① (★证明靠 md5★)" 1 "$(pick_grade "$OFFICIAL_S1_MD5" 12345 "")"
  # ★**★反向用例 (★铁律: 自测必须能证伪★)**: ★**把判据改弱成"永远档②" ⇒ 上面的档① 用例必须抓得住 ★★
  # ★**常量体检: 本机若留着官方 stage-1 板 ⇒ 核一下常量没写错****
  for f in /tmp/_straight7.kicad_pcb /tmp/offverify/in_official_s1.kicad_pcb; do
    [ -f "$f" ] || continue
    m="$(md5sum "$f" | awk '{print $1}')"
    if [ "$m" = "$OFFICIAL_S1_MD5" ]; then echo "  ✅ 常量体检: $f md5 命中"; else echo "  ⚠️ 常量体检: $f md5=$m 与常量不同 (★该文件不是官方 stage-1★)"; fi
  done
  if [ "$fail" = "0" ]; then echo "ALL TESTS PASS"; exit 0; else echo "SELFTEST FAILED"; exit 1; fi
fi

ROUTE="${1:?用法: replay_patch_chain.sh <路由产物板> <标签> [--validate]}"
TAG="${2:?用法: replay_patch_chain.sh <路由产物板> <标签> [--validate]}"
VALIDATE="${3:-}"

WORK=/tmp/chain_${TAG}
mkdir -p "$WORK"
LOG=$WORK/chain.log
: > "$LOG"

say() { echo "[$TAG] $*" | tee -a "$LOG"; }

# ★**fresh DRC (★给下一步当输入)**
fresh_drc() {   # $1=板 → $2=json
  bash state/kicad.sh pcb drc --output "$2" --severity-error --severity-warning \
       --format json "$1" >/dev/null 2>&1
}

# ★★★★★★2026-11-11 06:2x 【★【补丁链的"假阳性"自检闸】(★默认开, ★只报不改产物★)】★★★★★★
#   ★★★**★为什么必须有 (★实测坐实★)**: ★★★
#     ★**链日志说"补上 6 条" ⇒ 终板里只有 3 个网名真的少了 ⇒ ⇒ "补上" 是【假阳性】** ★★
#     ★**⇒ "补上" = 【A* 找到了路径】≠ 【真的连上了】⇒ ⇒ 链日志在骗人** ★★
#     ★★★**★口径差在哪★**: ★**A* 的终点只落在【格心】⇒ 离焊盘中心差 0.15~0.19mm ⇒ 铜没搭上焊盘**
#       ⇒ ★**⇒ KiCad 仍判未连接 ⇒ ⇒ 铜落了, 但网没连** ★★
#   ★★★**★本闸做什么★**: ★★**每步落铜后, 拿【输入板的未连接清单】与【输出板的未连接清单】逐项核**
#     ⇒ ★★**打印"真救回 N 条 / 假阳性 M 条"⇒ ⇒ 以后不会再被"补上 N 条"骗** ★★
#   ★★★**★纪律 (★为什么不改产物层★)**: ★★**只【报】, 不改任何铜 ⇒ ⇒ 官方链的逐位复现不受影响** ★★
verify_patch() {  # $1=输入板 $2=输入drc.json $3=输出板
  local in="$1" indrc="$2" out="$3"
  local outdrc="$WORK/$(basename "$out").verify.json"
  fresh_drc "$out" "$outdrc" || { say "   ⚠️ 自检闸: 输出板 fresh DRC 失败 ⇒ 跳过"; return 0; }
  python3 - "$indrc" "$outdrc" <<'PY' 2>/dev/null | sed 's/^/   /'
import json, sys
def sigs(p):
    j = json.load(open(p, encoding="utf-8"))
    out = set()
    for it in (j.get("unconnected_items") or []):
        names = []
        for a in (it.get("items") or []):
            d = a.get("description") or ""
            i, k = d.find("["), d.find("]")
            names.append(d[i+1:k] if i >= 0 and k > i else "?")
        out.add("|".join(names))
    return out
try:
    a, b = sigs(sys.argv[1]), sigs(sys.argv[2])
except Exception:
    print("⚠️ 自检闸: 清单读取失败"); raise SystemExit(0)
saved, broken = a - b, b - a
print("★自检闸: 未连接 %d → %d 条 · ★真救回 %d 个签名 · 新断 %d 个签名"
      % (len(a), len(b), len(saved), len(broken)))
if saved:
    print("  ★救回: %s" % ", ".join(sorted(saved)))
if broken:
    print("  ⚠️ 新断: %s" % ", ".join(sorted(broken)))
PY
}

step_nostub() {  # $1=输入板 $2=输出板 $3=网格 $4=margin $5=额外参数
  # ★★2026-11-09 03:3x **修: extra 收【第 5 个起的全部参数】** ★★
  #   ★**原 bug**: `extra="${5:-}"` 只取第 5 个 ⇒ ★**"--max-dist 15" 的 "15" 被丢 ⇒ 脚本拿到 "--max-dist" 没有值 ⇒ IndexError**
  local in="$1" out="$2" grid="$3" margin="$4" extra="${*:5}"
  # ★★★**★2026-11-10 04:4x 修 (★产生点★): DRC 文件按【输入板】命名 ★★★**
  #   ★**原 bug**: ★按【输出板】命名 ⇒ ★`final_chain.kicad_pcb.drc.json` 里装的是【上一步 s2_combo 的 DRC】★
  #   ★**⇒ 于是"同名 json 是不是终板的"变成猜 ⇒ ★★★已实测害我算错一次(v76ru: 打碎 9 ⇒ 实际 5)★★★**
  #   ★**⇒ 正解: 名字必须说明【这份 DRC 是谁的】⇒ 按输入板命名 ★**
  local drc="$WORK/$(basename "$in").drc.json"
  say "── nostub: $(basename "$in") → $(basename "$out") (grid=$grid margin=$margin $extra)"
  # ★★2026-11-09 03:1x **护栏: 输入板不存在 ⇒ 立刻停 (★不许"级联失败"一路假跑完)**
  #   ★**实测教训**: 03:1x 那轮 replay 里, combo3 步 IndexError 崩了 ⇒ 后面几步拿着【不存在的输入】继续跑
  #   ⇒ 最后一步报 'NoneType has no attribute Zones' ⇒ ★**日志看着像"跑完了", 实际早就断了**
  if [ ! -f "$in" ]; then
    say "❌ 输入板不存在 ($in) ⇒ 链断在这里 ⇒ 收工 (★不许继续假跑)"
    exit 9
  fi
  fresh_drc "$in" "$drc"
  env PCB_HALO_MARGIN="$margin" bash state/pcbnew_py.sh state/patch_astar_nostub.py \
      "$in" "$drc" --out "$out" --grid "$grid" $extra >> "$LOG" 2>&1
  if [ ! -f "$out" ]; then
    say "❌ 本步没出板 ⇒ 链断在这里 ⇒ 收工 (★看 $LOG 尾部的 Traceback)"
    exit 8
  fi
  say "   ⇒ $(grep -ac '(segment' "$out" 2>/dev/null) 段"
  # ★★★**2026-11-11 06:2x: ★【假阳性自检闸】⇒ "补上 N 条"【不等于】真的连上了** ★★★
  verify_patch "$in" "$drc" "$out"
}

step_straight() {  # $1=输入板 $2=输出板
  local in="$1" out="$2"
  # ★★2026-11-10 04:4x 修 (★产生点★): ★同上 ⇒ DRC 按【输入板】命名 ★★
  local drc="$WORK/$(basename "$in").drc.json"
  say "── straight: $(basename "$in") → $(basename "$out")"
  if [ ! -f "$in" ]; then
    say "❌ 输入板不存在 ($in) ⇒ 链断在这里 ⇒ 收工"
    exit 9
  fi
  fresh_drc "$in" "$drc"
  bash state/pcbnew_py.sh state/fix_straight_links.py "$in" "$drc" --out "$out" >> "$LOG" 2>&1
  say "   ⇒ $(grep -ac '(segment' "$out" 2>/dev/null) 段"
}

if [ "$VALIDATE" = "--validate" ]; then
  say "★自校准模式: 用官方【链中段板】重放 ⇒ 结果必须复现官方终板 (18092 段 / unc 45 / DRC 0)"
  # ★★2026-11-09 04:5x 订正: 输入必须是【_straight7】(★官方链 combo 步的真实输入, md5 8b33af51, 17022 段)
  #   ★**旧注释说"输入 = 路由产物(13407 段)" ⇒ ★**那是错的** ⇒ ★**用 13407 段板当输入, 后面几段根本对不上**
  IN="${ROUTE:-/tmp/_straight7.kicad_pcb}"
  say "   输入 = $IN ($(grep -ac '(segment' "$IN" 2>/dev/null) 段)"
  # ★**★关键: 输入已是【straight 步之后】⇒ ★**不许再跑 straight** (★否则会重跑一遍 straight ⇒ 走岔)
  # ★**判据: 输入段数 ≥ 17000 ⇒ 已是链中段板 ⇒ 跳过 straight 步**
  SEGI=$(grep -ac '(segment' "$IN" 2>/dev/null || echo 0)
  if [ "$SEGI" -ge 17000 ]; then
    SKIP_STRAIGHT=1
    say "   ★输入段数 $SEGI ≥ 17000 ⇒ 已是【straight 之后】⇒ ★**跳过 straight 步** (★不然会重跑)"
  else
    SKIP_STRAIGHT=0
    say "   ★输入段数 $SEGI < 17000 ⇒ 是【路由产物】⇒ ★**会跑 straight 步**"
  fi
else
  IN="$ROUTE"
  SKIP_STRAIGHT=0
  # ★★★**★2026-11-09 05:4x 修: SEGI 在非 --validate 分支没赋值 ⇒ `set -u` 直接崩 (★"闸脚本自己也会有 bug ⇒ 闸门形同虚设"的第三次实例)** ★★★
  SEGI=$(grep -ac '(segment' "$IN" 2>/dev/null || echo 0)
fi

# ★★★★**★2026-11-11 09:0x: 自校准闸分档 (★按【输入的性质】判 ★ 不是按 SKIP_STRAIGHT 那个过程量★)****
# ★★**★为什么 (★实测: offverify 拿的是官方 stage-1 却被判成档② ⇒ 档① 严格比对根本没跑★)****
IN_MD5="$(md5sum "$IN" 2>/dev/null | awk '{print $1}')"
GRADE="$(pick_grade "$IN_MD5" "$SEGI" "$VALIDATE")"
if [ "$GRADE" = "1" ]; then
  say "★自校准分档 = 档① (输入 md5=$IN_MD5 · $SEGI 段 ⇒ 是【官方链 stage-1】⇒ 链产物必须逐条复现官方终板)"
else
  say "★自校准分档 = 档② (输入 md5=$IN_MD5 · $SEGI 段 ⇒ 不是官方 stage-1 ⇒ 只判 DRC/unc, 不许宣称与官方同工艺)"
fi

# ★★★**★2026-11-09 04:5x 改: 链的【真实顺序】 = straight 步 → combo(margin 0.20) → loose(margin 0.0625)** ★★★
# ★**旧版把 _nostub125(死支) 放① + combo 用 0.125 ⇒ 两处都错 ⇒ 走岔 ⇒ 17731 段**
# ★**证据见文件头注释 (md5 血缘 + 逐段复现)**
#
# ★**① straight 步 (★官方那次: _straight1/2/3/6/7 各自【独立】跑, 不是层层串联 —— ★因为 _straight3 与 _straight7 只差 3 段)** ★
# ★**★实测 (★11-09 04:5x): _straight3 集合 16907 条 vs _straight7 集合 16910 条 ⇒ 只差 3 条 (LIGHT_3V3×1 + ID_DETECT_0×2)**
# ★**⇒ 说明 straight 步是【同一输入上跑多次不同参数】, 每次都从【原始输入】出发, 取最好的那次**
if [ "$SKIP_STRAIGHT" = "1" ]; then
  say "── straight: ★跳过 (★输入已是 straight 之后的链中段板)"
  cp "$IN" "$WORK/s1_straight.kicad_pcb"
else
  step_straight "$IN" "$WORK/s1_straight.kicad_pcb"
fi
# ★**② combo (★margin 0.20 = PCB_HALO_MARGIN 默认值 ⇒ ★官方那次没设 env ⇒ 就是默认)** ★
step_nostub "$WORK/s1_straight.kicad_pcb" "$WORK/s2_combo.kicad_pcb" 0.125 0.20
# ★**③ loose (★margin 0.0625 = 网格半格 ⇒ 这才是"loose"的关键)** ★
# ★★2026-11-11 04:3x 【loose 步 margin 可参数化·默认 0.0625 ⇒ 逐位不变】★★
#   ★依据: margin 0.03125 ⇒ unc 29→27 ⇒ 代价是 0.1937mm 边际违规 ⇒ 由 clrfix_iter 清理 ⇒ DRC 0
_LOOSE_MARGIN="${PCB_CHAIN_LOOSE_MARGIN:-0.0625}"
step_nostub "$WORK/s2_combo.kicad_pcb" "$WORK/final_chain.kicad_pcb" 0.125 "$_LOOSE_MARGIN"

if [ -f "$WORK/final_chain.kicad_pcb" ]; then
  say "★链跑完 ⇒ 终板 $WORK/final_chain.kicad_pcb"
  say "   段数 = $(grep -ac '(segment' "$WORK/final_chain.kicad_pcb") (★官方终板 = 18092 ⇒ 不等于就不算数)"
else
  # ★★2026-11-09 03:3x **修: 不许无条件说"链跑完"** ★★ (★上一轮就是在这儿骗了人: 实际终板根本没生成)
  say "❌ 链没跑完 (终板没生成) ⇒ ★**本轮结果不算数** (★看 $LOG 尾部的 Traceback)"
  exit 7
fi
bash state/pcbnew_py.sh state/check_pcb_drc.py "$WORK/final_chain.kicad_pcb" 2>&1 | grep -E "C3 |C4 " | tee -a "$LOG"

# ★★★**★2026-11-10 04:4x 新增 (★兄弟 session 提的待办★): 链尾写【终板自己的 fresh DRC】 ★★★
#   ★**为什么**: ★**同名 json 曾经是"上一步的输入 DRC" ⇒ 读数极易读错 ⇒ ★★**必须有一份"名字就说明是终板"的 DRC** ★★
#   ★**文件名**: ★`final_board.drc.json` (★不叫 `final_chain.kicad_pcb.drc.json` ⇒ 避免与旧习惯混淆★)
FINALDRC="$WORK/final_board.drc.json"
fresh_drc "$WORK/final_chain.kicad_pcb" "$FINALDRC"
if [ -f "$FINALDRC" ]; then
  say "★终板 fresh DRC = $FINALDRC"
  say "   ★unc 条目 = $(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));u=d.get('unconnected_items') or [];print(len(u))" "$FINALDRC" 2>/dev/null || echo '?')"
  say "   ★违规数   = $(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(len(d.get('violations',[])))" "$FINALDRC" 2>/dev/null || echo '?')"
  say "   ★unc 网名 = $(python3 -c "import json,sys,re;d=json.load(open(sys.argv[1]));u=d.get('unconnected_items') or [];s=set();[s.update(re.findall(r'\[([A-Za-z0-9_]+)\]',json.dumps(x,ensure_ascii=False))) for x in u];print(len(s))" "$FINALDRC" 2>/dev/null || echo '?')"
  # ★★**★同时把【终板 DRC】按老名字也写一份 (★兼容旧脚本/旧习惯★) ★★ ★★**⇒ 覆盖掉那份"上一步输入 DRC", 杜绝再踩坑 ★★
  cp "$FINALDRC" "$WORK/final_chain.kicad_pcb.drc.json"
  say "   ★已覆盖同名旧文件 ⇒ final_chain.kicad_pcb.drc.json 现在【就是终板的 DRC】(★不再有【上一步输入】歧义★)"
else
  say "❌ 终板 fresh DRC 没生成 ⇒ ★**读数不可信**"
  exit 6
fi

# ★★★**2026-11-09 04:5x 新增: 自校准闸 (★复现不了官方终板 ⇒ rc≠0 ⇒ 这块板不许拿去跟官方比)** ★★★
# ★★★★**★05:2x 订正 (★v76 对照臂实测暴露的闸自身 bug)****
# ★**原闸把"段数必须 == 18092"写死** ⇒ ★**对【输入 = 路由产物】的臂永远红** (★v76b 实测: 14023 段 ⇒ rc=11)
# ★**⇒ 闸门形同虚设 (★正是【闸脚本自己有 bug ⇒ 闸门形同虚设】那条铁律)** ⇒ ★★**必须分两种输入分别判** ★★
# ★**判据分两档 (★按【输入段数】分档, ★不按结果分档)**:
#   ★**档① 输入 ≥17000 段 (★已是【官方链 stage-1 板】) ⇒ 必须【逐条复现官方终板】** ⇒ 不一致 ⇒ rc=11/12
#   ★**档② 输入 <17000 段 (★是【路由产物】) ⇒ 只能判 DRC/unc, ★不许宣称"与官方同工艺"**
#     ⇒ ★**因为官方链的 stage-1 (路由阶段) 产物是 17022 段, 而【当前路由器的产物只有 13407 段】**
#     ⇒ ★**⇒ 路由产物臂与官方板【天然不可比】(★路由器代码已漂移) ⇒ ★这里只能出数, 不许说"可比"**
SEGF=$(grep -ac '(segment' "$WORK/final_chain.kicad_pcb")
# ★★**★2026-11-11 09:0x 修: 分档判据从【过程量 SKIP_STRAIGHT】改成【输入性质 GRADE】(★否则 offverify 这种"输入就是官方 stage-1 但没带 --validate"的轮次会被误判成档② ⇒ 严格比对不跑★)****
if [ "$GRADE" = "1" ]; then
  # ★**档①: 必须逐条复现官方终板**
  if [ "$SEGF" != "18092" ]; then
    say "❌ 自校准闸(档①): 段数 = $SEGF ≠ 18092 (★官方终板) ⇒ ★**参数/顺序没对上 ⇒ 这块板不许拿去跟官方比**"
    say "   ⇒ 排查: ① combo 步 margin 是不是 0.20 (★不是 0.125) ② 输入是不是【链中段板】(★不是路由产物)"
    exit 11
  fi
  # ★**几何集合比对 (★忽略 UUID 随机 ⇒ 只比 起点/终点/线宽/层/网)**
  # ★★★★**★2026-11-09 06:3x: 改用【统一工具】`state/cmp_pcb_geom.py` (★★**别再各处各写一遍解析 ⇒ 改一处必漏**) ★★★★
  # ★**这个工具的存在理由 (★实测)**: ★**md5 不能判复现** ⇒ ★**KiCad 每次存盘重生成 uuid** ⇒ ★★**本项目因此判错 3 次** ★★
  if [ -f "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" ]; then
    python3 "$PROJ/state/cmp_pcb_geom.py" "$WORK/final_chain.kicad_pcb" "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" --zones 2>&1 | tee -a "$LOG"
    python3 "$PROJ/state/cmp_pcb_geom.py" "$WORK/final_chain.kicad_pcb" "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" --zones >/dev/null 2>&1 || exit 12
  fi
  # ★**unc 网名集合比对 (★比"unc 数量"强得多 ⇒ ★★**同工艺的板必须连【哪几个网没连上】都一样** ★★)**
  # ★**★实测 (★05:5x)**: ★**官方板 vs 本链复现板 ⇒ 网名集合 43/43 完全相同 (★仅官方 0 · 仅复现 0)**
  # ★**★对照: 走岔的旧链板 (17731段) ⇒ 网名集合差 1 个 (★46条unc) ⇒ ★★**本闸抓得住** ★★
  # ★★★★**★2026-11-09 06:0x 修 (★自测时抓到的真 bug)**: ★**`$WORK/final_chain.kicad_pcb.drc.json` 是【loose 步的输入 DRC】(★48 条), 不是终板的 (★45 条)** ★★
  #   ⇒ ★**拿它比 unc ⇒ 判据失效 (★比的是上一级板的状态)** ⇒ ★★**必须 fresh DRC 终板自己** ★★
  FRESHDRC="$WORK/_final_fresh.drc.json"
  fresh_drc "$WORK/final_chain.kicad_pcb" "$FRESHDRC"
  # ★★★★**★2026-11-11 09:0x 修: 官方 unc 参照不许再靠 `/tmp/_drc45.json` 这种临时文件 (★缺了就静默跳过比对 ⇒ 又一次"闸门形同虚设"★)****
  OFFDRC="/tmp/_drc45.json"
  if [ ! -f "$OFFDRC" ]; then
    OFFDRC="$WORK/_official_fresh.drc.json"
    say "   ★官方 unc 参照 (/tmp/_drc45.json) 不在 ⇒ 现算官方板 fresh DRC ⇒ $OFFDRC"
    fresh_drc "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" "$OFFDRC"
  fi
  if [ ! -f "$FRESHDRC" ] || [ ! -f "$OFFDRC" ]; then
    say "❌ unc 网名集合比对做不了 (终板 DRC 或 官方参照 DRC 缺失) ⇒ ★**不许静默跳过** ⇒ rc=14"
    exit 14
  fi
  python3 "$PROJ/state/cmp_unc_sets.py" "$OFFDRC" "$FRESHDRC" 2>&1 | tail -8 | tee -a "$LOG"
  python3 "$PROJ/state/cmp_unc_sets.py" "$OFFDRC" "$FRESHDRC" --strict >/dev/null 2>&1 || exit 13
  say "★自校准闸(档①)通过 ⇒ 这块板与官方终板同工艺 ⇒ ★可以拿去跟官方比"
else
  # ★**档②: 路由产物臂 ⇒ 只报数, 不许宣称"可比"**
  say "⚠️ 自校准闸(档②): 输入是【路由产物】($SEGI 段) ⇒ ★**链已跑完但产物不能与官方板直接比**"
  say "   ★原因: ★官方链的 stage-1 产物是 17022 段, 当前路由器只出 $SEGI 段 ⇒ ★路由器代码已漂移 ⇒ ★两臂不同工艺"
  say "   ⇒ ★段数 $SEGF (★官方终板 18092) · ★unc/DRC 见上 ⇒ ★**只能用【四把尺子】对已晋级臂比, 不能拿这块直接对比官方**"
fi

CHAINJSON="$WORK/final_chain.kicad_pcb.chain.json"
# ★★2026-11-09 16:3x 修: ★**凭据必须【无条件】写 (★之前挂在档①闸之后 ⇒ 档②臂(★输入<17000段)拿不到凭据 ⇒ 比较脚本拒比)** ★★
python3 - "$CHAINJSON" "$IN" "$WORK/final_chain.kicad_pcb" "$TAG" "$PROJ" <<'PY'
import hashlib, json, os, sys
out, inp, dst, tag = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
HERE = os.path.join(os.path.abspath(sys.argv[5]), "state")
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()
def _router_src_sha(inp=""):
    """★**路由器源码指纹 (★配方的一部分 ⇒ 源码漂了 ⇒ 老臂读数不可混比★)**

    ★★★★★★2026-11-11 05:5x 【★优先读【臂溯源侧车】⇒ 源码漂了也不慌★】★★★★★★
      ★**为什么**: 臂脚本只在日志里打印一次源码 sha ⇒ 源码一漂 ⇒ 凭据就在撒谎 ⇒ 照凭据复现会得到另一块板
      ★★**⇒ 正解**: 臂跑完写 `<板>.routersrc.json` (★state/arm_provenance.py★) ⇒ ⇒ 凭据钉【真正跑出这块板的源码】★★
    """
    import hashlib
    if inp:
        side = inp + ".routersrc.json"
        if os.path.exists(side):
            try:
                d = json.load(open(side, encoding="utf-8"))
                sha = d.get("router_src_sha256")
                if sha:
                    return "%s:%s" % (d.get("router_src_file", "?"), sha[:16])
            except Exception:
                pass
    cand = [os.path.join(HERE, "gen_pcb_routing.py"),
            os.path.join(HERE, ".router_src_v76mw2.py")]
    for p in cand:
        if os.path.exists(p):
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for c in iter(lambda: f.read(1 << 20), b""):
                    h.update(c)
            return "%s:%s" % (os.path.basename(p), h.hexdigest()[:16])
    return "unknown"
def _router_sidecar(inp=""):
    """★**读【臂溯源侧车】⇒ 把【路由器的 env + 源码】并进链凭据 ⇒ ★配方一个文件自洽**"""
    if not inp:
        return {}
    side = inp + ".routersrc.json"
    if not os.path.exists(side):
        return {}
    try:
        return json.load(open(side, encoding="utf-8"))
    except Exception:
        return {}


def segs(p):
    n = 0
    with open(p, encoding="utf-8", errors="ignore") as f:
        for l in f:
            if l.lstrip().startswith("(segment"):
                n += 1
    return n
info = {
    "tag": tag,
    "input": os.path.abspath(inp),
    "input_md5": md5(inp),
    "output": os.path.abspath(dst),
    "output_md5": md5(dst),
    "output_segments": segs(dst),
    # ★★★★★★2026-11-11 05:4x 【★凭据不许写死 margin ⇒ 照凭据复现会得到另一块板★】★★★★★★
    #   ★**实测踩到**: `PCB_CHAIN_LOOSE_MARGIN=0.03125` 跑出来的板, 凭据却写 `margin=0.0625`
    #     ⇒ ★**照凭据复现 ⇒ 得到 unc 24 而不是 22 的另一块板 ⇒ 配方不可复现 ⇒ 凭据形同虚设** ★★
    #   ★**正解**: 凭据必须记【实际跑的 margin】⇒ 并顺带记【路由器源码 sha】+【关键 env】⇒ ★配方才可复现** ★
    "chain": ["straight(skip-if-mid)", "nostub margin=0.20 grid=0.125",
              "nostub margin=%s grid=0.125" % os.environ.get("PCB_CHAIN_LOOSE_MARGIN", "0.0625")],
    "loose_margin": os.environ.get("PCB_CHAIN_LOOSE_MARGIN", "0.0625"),
    "router_src_sha256": _router_src_sha(inp),
    "router_env": _router_sidecar(inp).get("key_env", {}),
    "router_arm": _router_sidecar(inp).get("arm", ""),
    "key_env": {k: v for k, v in os.environ.items() if k.startswith("PCB_")},
    "note": "★**这块板是【官方补丁链的产物】⇒ ★★**不是独立候选臂**; ★★**要当候选臂比, 必须与【同链基线】比 (★state/compare_arm_baseline.sh) ★★",
}
json.dump(info, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("  ✅ 链凭据: %s" % out)
PY
