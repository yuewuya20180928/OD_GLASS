#!/bin/bash
# ISS-306 sw-lead · /tmp 配额回收 (可恢复: 移入 .trash, 非 rm)
D=/home/yuewuya/.openclaw/workspace/projects/smart_glasses/.trash/tmp_quota_cleanup_20261118_0535
for d in od_glass_publish sbxtest iss239_rehearsal iss279_sandbox iss279_sandbox2 holechk iss242_fix sg_sandbox; do
  [ -d "/tmp/$d" ] || { echo "SKIP (gone): $d"; continue; }
  echo "--- moving /tmp/$d ($(du -sh /tmp/$d | cut -f1)) ---"
  mv "/tmp/$d" "$D/" && echo "OK  $d" || echo "FAIL $d"
done
echo "=== after ==="
df -h /tmp | tail -1
du -sh "$D" | tail -1
