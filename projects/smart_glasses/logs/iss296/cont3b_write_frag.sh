#!/usr/bin/env bash
# ★ISS-296 cont3-b · 分片原子写 (★只写 mech-lead 自己那一份 · 走 state/frag_write.py 的原子写通道★)
set -euo pipefail
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

python3 state/frag_write.py --agent mech-lead \
  --add-claim 'key=iss296_mech_real_landing_shape_case18_19 value="闸1 自检新增 ⑱ (main 真实落表形状: §16.2 链头行 + §19.3 登记行 两张表都写 ⇒ C4 必须绿 · C1/C2/C3 全绿) + ⑲ (同样两张表但改前 md5 互相不一致 ⇒ C4 必须红) ⇒ 自检条数 20→22 (只增不减) · 判据方向/fail-closed 三条/阈值 一个都没动"' \
  --add-claim 'key=iss296_mech_real_landing_shape_probe value="独立探针 logs/iss296/probe_real_landing_shape_dup_rows.py ⇒ rc=0 (A 两张表形状合法改板 ⇒ C4 绿 · B 两张表改前不一致 ⇒ C4 红 · C 链头 md5 落在台账 L1451+L1466 两行 ⇒ ⑩c 计数假设过期的根因)"' \
  --add-artifact 'path=logs/iss296/probe_real_landing_shape_dup_rows.py kind=probe version=iss296-cont3b summary="ISS-296 cont3-b 探针: 合法改板通道 × main 真实落表形状 (两张表) 的 A/B/C 三条, 全部在沙盒副本上跑, rc=0"' \
  --add-artifact 'path=logs/iss296/cont3b_real_landing_shape_probe.log kind=log version=iss296-cont3b summary="上述探针的原样输出留证 (rc=0 · 三条全过)"' \
  --add-need 'key=iss296_mech_cont3b_reboard_day_selftest_must_run to=main item="板那一趟落表之后, MECH 两道闸的【主跑 + --selftest】必须【同一次】一起绿: ⑱/⑲ 两条用例已经把 main 的真实落表形状 (两张表) 钉进闸的自检 ⇒ 落表当天若只跑主模式, 两张表形状的假红不会被抓到 ⇒ 收工验收清单要写明 --selftest 也要跑"' \
  --status 'phase=delivered progress_pct=100 health=green summary="★ISS-296 cont3-b 交卷 (2026-11-18 05:5x · mech-lead): 在 cont3 修好 ⑩c 计数断言 (hit==1 ⇒ hit>=1) 之后, 补上【main 真实落表形状】的正向对照 —— 闸1 自检新增 ⑱ (两张表 = §16.2 链头行 + §19.3 登记行 ⇒ C4 绿) + ⑲ (两张表改前 md5 不一致 ⇒ C4 红), 自检条数 20→22 只增不减, 判据方向/fail-closed 三条/阈值 一个都没动; 独立探针 logs/iss296/probe_real_landing_shape_dup_rows.py rc=0 三条全过 (A 绿 / B 红 / C 定位 ⑩c 根因); 零写板零落表零改网表真源 (板 md5 611b869e… + mtime 2026-11-06 07:07:17 双证不变)"'

echo "--- 写完校验 ---"
grep -c iss296 state/fragments/mech.yaml
grep -n "iss296_mech_real_landing_shape\|iss296_mech_cont3b_reboard_day" state/fragments/mech.yaml | head
