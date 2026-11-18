#!/usr/bin/env bash
# ISS-263 · sw-lead · rknn3-toolkit 1.2.0 (cp310 linux x86_64) 官方 wheel 分片并发下载器
# ★byte-accurate 断点续传: 每片的本地字节数即已确认的连续前缀, 续传时按偏移继续 Range★
# ★进度可查: $WORKDIR/progress.txt + $LOGDIR/rknn3_download.log★
# ★fail-closed: 本脚本【只取字节】, 【不做 md5 判定】(md5 由调用方校验, 不过就不许装)★
set -u

URL="${RKNN3_WHEEL_URL:-https://raw.githubusercontent.com/airockchip/rknn3-toolkit/main/rknn3-toolkit/packages/rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl}"
TOTAL=102657410
NCHUNK=7
WORKDIR="${RKNN3_WORKDIR:-/var/tmp/iss263_rknn3}"
PARTS="$WORKDIR/parts"
LOGDIR="${RKNN3_LOGDIR:-/home/yuewuya/.openclaw/workspace/projects/smart_glasses/logs/iss263}"
mkdir -p "$PARTS" "$LOGDIR"
LOG="$LOGDIR/rknn3_download.log"
PROG="$WORKDIR/progress.txt"
CHUNK=$(( (TOTAL + NCHUNK - 1) / NCHUNK ))

log() { printf '%s [ISS263-DL] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

part_range() { local i=$1 s e; s=$(( i * CHUNK )); e=$(( s + CHUNK - 1 )); [ "$e" -ge "$TOTAL" ] && e=$(( TOTAL - 1 )); echo "$s $e"; }
part_expected() { local i=$1 s e; read -r s e <<< "$(part_range "$i")"; echo $(( e - s + 1 )); }

fetch_part() {
  local i=$1 s e exp have start tmp code got
  read -r s e <<< "$(part_range "$i")"
  exp=$(part_expected "$i")
  local f="$PARTS/p$i"
  tmp="$PARTS/p$i.tmp"
  have=$( [ -f "$f" ] && stat -c %s "$f" || echo 0 )
  while [ "$have" -lt "$exp" ]; do
    start=$(( s + have ))
    rm -f "$tmp"; : > "$tmp"
    code=$(curl -sS --fail --connect-timeout 30 --max-time 1200 \
                 -H "Range: bytes=$start-$e" "$URL" -o "$tmp" -w '%{http_code}' 2>> "$LOG" )
    crc=$?
    got=$( [ -f "$tmp" ] && stat -c %s "$tmp" || echo 0 )
    if [ "$code" = "206" ]; then
      cat "$tmp" >> "$f"
      have=$(( have + got ))
      log "part $i +$got now=$have/$exp (206)"
    elif [ "$code" = "200" ]; then
      # 服务器忽略 Range => 返回整文件; 本地切片补齐 (退化路径)
      log "part $i HTTP 200 (server ignored Range) => local split, got=$got"
      python3 - "$tmp" "$f" "$have" "$(( exp - have ))" <<'PY'
import sys
tmp,f,have,need = sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
with open(tmp,'rb') as s, open(f,'ab') as d:
    s.seek(have)
    left=need
    while left>0:
        b=s.read(min(1<<20,left))
        if not b: break
        d.write(b); left-=len(b)
PY
      have=$(stat -c %s "$f")
      log "part $i local-split done now=$have/$exp"
    else
      log "part $i curl rc=$crc http=$code got=$got => retry (保留已得 $have/$exp)"
      sleep 4
      continue
    fi
    rm -f "$tmp"
  done
  log "part $i COMPLETE bytes=$(stat -c %s "$f") expected=$exp"
}

write_progress() {
  {
    echo "# ISS-263 rknn3-toolkit wheel 下载进度  (updated $(date '+%Y-%m-%d %H:%M:%S'))"
    echo "# url=$URL"
    echo "# total_bytes=$TOTAL  nchunk=$NCHUNK  chunk=$CHUNK  workdir=$WORKDIR"
    echo "# official_md5=a972e03af94fd18e21f026558735b28d"
    local i s e exp cur tot=0 dn=0
    for i in $(seq 0 $((NCHUNK-1))); do
      read -r s e <<< "$(part_range "$i")"
      exp=$(part_expected "$i")
      cur=$( [ -f "$PARTS/p$i" ] && stat -c %s "$PARTS/p$i" || echo 0 )
      tot=$(( tot + cur ))
      [ "$cur" -ge "$exp" ] && dn=$(( dn + 1 ))
      echo "part $i: $cur / $exp bytes  (range $s-$e)"
    done
    echo "TOTAL: $tot / $TOTAL bytes  ($(( tot * 100 / TOTAL ))%)  parts_complete=$dn/$NCHUNK"
    echo "# 拼装命令: cat $PARTS/p0 $PARTS/p1 $PARTS/p2 $PARTS/p3 $PARTS/p4 $PARTS/p5 $PARTS/p6 > $WORKDIR/wheel.whl"
    echo "# 校验命令: md5sum $WORKDIR/wheel.whl  # 期望 a972e03af94fd18e21f026558735b28d"
  } > "$PROG"
}

log "START url=$URL total=$TOTAL nchunk=$NCHUNK chunk=$CHUNK workdir=$WORKDIR"
write_progress
pids=()
for i in $(seq 0 $((NCHUNK-1))); do
  fetch_part "$i" &
  pids+=($!)
  sleep 0.3
done
( while :; do write_progress; sleep 20; done ) &
PROG_PID=$!
for p in "${pids[@]}"; do wait "$p"; done
kill "$PROG_PID" 2>/dev/null
write_progress
log "ALL PARTS DONE"
exit 0
