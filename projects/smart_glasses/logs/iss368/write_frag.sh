#!/usr/bin/env bash
# ISS-368 · sw-lead · 分片写入 (★只走 state/frag_write.py★ · ★不许 open(p,"w")★)
set -e
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

echo "### 写前 md5 基线"
md5sum state/fragments/sw.yaml | tee logs/iss368/frag_md5_before.txt
stat -c '%y %n' state/fragments/sw.yaml

python3 state/frag_write.py --agent sw-lead \
 --add-artifact 'path=SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md kind=spec version=v1.0 updated_at=2026-11-23 summary="★ISS-368 · sw-lead · 2026-11-23 · SW09 三处同批落地补丁一页 (★本单新建★) ⇒ §0 口径与读数 (9 条读数各写清哪个脚本产出怎么复跑) / §1 三处落点逐字规格 (15 处编辑 A1~A4 + B1~B11 各给定位串+原文+新文+自证·规格由 apply 脚本 EDITS 表自动导出零手抄) / §2 幂等性 (第 2 遍第 3 遍逐字节 diff = 0) / §3 dry-run 证明 (副本上 10 道 SW 闸绿 10 红 0 + 新闸 F1~F7 绿 7 红 0 + 反证只改一处 H4 红 F4 红) / §4 回滚 (逐字节反向补丁 + 回滚命令 + 回滚后 10 道闸绿 10 红 0) / §5 未决项只登记不代拍 / §6 边界自证 / §7 复现全表"' \
 --add-artifact 'path=SW/tools/apply_sw09_three_place_patch.py kind=tool version=v1.0 updated_at=2026-11-23 summary="★ISS-368 · sw-lead · 2026-11-23 · SW09 三处同批落地幂等补丁 (★本单新建★) ⇒ 默认干跑 · --apply 只许写项目盘 tmp/ 下的副本目录 (真件写不进去·rc=2 拒写) · 15 条编辑 (落点① 4 + 落点② 11 + 落点③ 0 只验不改) · 三种原子操作自带幂等分支 (replace / insert_after_line / json_append) · --rollback 走同一套锚点反向执行 · --dry-run 显式旗标已补 (判据方向未动)"' \
 --add-artifact 'path=SW/tools/check_sw09_patch_dryrun.py kind=tool version=v1.0 updated_at=2026-11-23 summary="★ISS-368 · sw-lead · 2026-11-23 · SW09 补丁的副本 dry-run 机器闸 (★本单新建★) ⇒ F1 三处同批到位 / F2 H4-REG 三数字 9-1-5 / F3 幂等 / F4 10 道 SW 闸全绿 / F5 证据等级五级白名单 / F6 正文零挂起措辞 / F7 沙盒在项目盘 tmp/ 且零软链 ⇒ 裸跑 rc=0 (绿 7 红 0) + --selftest 8/8 ALL TESTS PASS · 本闸零挂链 (挂不挂 EXTRA_GATES 归 main)"' \
 --add-artifact 'path=HANDOFF/2026-11-23_sw-lead_ISS368_SW09三处同批落地补丁.md kind=handoff version=v1.0 updated_at=2026-11-23 summary="★ISS-368 · sw-lead · 2026-11-23 · ISS-368 交卷页 (★本单新建★) ⇒ B1~B6 六段齐全 + 20 条验收线逐条判定 + 必跑命令原样 rc + 落盘清单 + 沙盒留证路径 + 要 main 裁的 5 件事"' \
 --add-answer 'key=iss368_sw09_three_place_landing_patch_delivered to=main value="★ISS-368 回覆 (sw-lead 2026-11-23) · 【SW09_FP_TRUTH_READ 的三处同批落地已被做成一次可执行 · 幂等 · 可回滚 · 有沙盒证明的动作】⇒ 交付三件: ① 一页 SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md (§0~§7) ② 幂等补丁 SW/tools/apply_sw09_three_place_patch.py (默认干跑 · --apply 只许写项目盘 tmp/ 下的副本 · 真件写不进去) + 机器闸 SW/tools/check_sw09_patch_dryrun.py (裸跑 rc=0 · --selftest 8/8) ③ 交卷页 HANDOFF/2026-11-23_sw-lead_ISS368_SW09三处同批落地补丁.md · 【真件三处零改】SW/BOARD_ONEPASS_SW_SYNC.md b8f935db… / SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md 17b3c38c… / SW/tools/check_fp_truth_read.py cab7a6f1… 前后逐字节同值 · 【反证成立】只改落点① 或只改落点② ⇒ ISS-362 闸 H4 红 + ISS-363 闸 F4 红 (三变体实跑 rc=0) · 【回滚】--apply --rollback ⇒ 两份页面逐字节回到落地前原文 · 回滚后 10 道 SW 闸绿 10 红 0 · 【本单不代拍】新闸挂不挂 state/gate_check.py 的 EXTRA_GATES = main 的机制地界 (本单零挂链) · 【板与真源零改动】板 md5 611b869e… mtime 2026-11-06 07:07:17.362193413" ref="SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md · logs/iss368/check_sw09_patch_dryrun.out · logs/iss368/prove_partial_landing.out · logs/iss368/rollback_proof.txt"' \
 --add-claim 'key=iss368_sw09_three_place_landing_contract value="SW09_FP_TRUTH_READ 的真件落地是【三处同批的一个动作】不许拆成三批: ① 清单页 SW/BOARD_ONEPASS_SW_SYNC.md 的 §2 小节头 (8 条 ⇒ 9 条) + §2 逐条表第 9 行 (7 列齐全) + §2.1 归属步分布 S10 行 (3 ⇒ 4) + §6 机器可读 JSON 块 items[] 追加第 9 个对象 (9 字段齐全非空) ② 影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md 的 §H4-REG 三个登记数字 (H4-ITEMS 8⇒9 · H4-COVER 0⇒1 · H4-GENERIC 4⇒5) + 块内 H4-FINDING / H4-IMPACT / H4-COUNTERMEASURE / 附注 + 页首边界句 + §1 G01 行 + §5 证据分级行 ③ 新闸 SW/tools/check_fp_truth_read.py (只验不改 · md5 必须仍 cab7a6f1…) · 落地方 = main 在板只改一次那一趟的一键动作 (落表批次地界) · 落地后自证 = python3 SW/tools/check_sw09_patch_dryrun.py ⇒ F1~F7 全绿 · 只改其中任一处 ⇒ H4 红 + F4 红" note="logs/iss368/landings_spec_dump.md (逐字规格自动导出) · logs/iss368/check_sw09_patch_dryrun.out · logs/iss368/prove_partial_landing.out · logs/iss368/rollback_proof.txt" ref="SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md#§1"' \
 --add-need 'key=iss368_sw09_extra_gates_hookup_decision to=main item="【只登记·不代拍】ISS-368 交两件新脚本, 请 main 裁两件事: ① 新闸 SW/tools/check_sw09_patch_dryrun.py (F1~F7) 挂不挂 state/gate_check.py 的 EXTRA_GATES ⇒ 本单零挂链 (state/gate_check.py md5 5f370bb8… 前后同值) ⇒ 挂不挂由 main 定 ② 真件三处 (清单页 SW/BOARD_ONEPASS_SW_SYNC.md + 影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md + 新闸 SW/tools/check_fp_truth_read.py) 的落地执行归 main 在板只改一次那一趟的一键动作 ⇒ 本单只交补丁 + 副本 dry-run 证明 + 回滚说明 · 真件零改" since=2026-11-23' \
 --status 'phase=delivered progress_pct=100 health=green summary="★ISS-368 · sw-lead · 2026-11-23 · SW09_FP_TRUTH_READ 三处同批落地 ⇒ 幂等补丁 + 副本 dry-run 证明 + 回滚说明三件交齐 (真件零改 · 零写板 · 零落表 · 零挂链) · 新闸 F1~F7 绿 7 红 0 · --selftest 8/8 · 副本上 10 道 SW 闸绿 10 红 0 · 反证只改一处 H4 红 F4 红成立 · 回滚逐字节可逆"'

echo "### 写后 md5"
md5sum state/fragments/sw.yaml | tee logs/iss368/frag_md5_after.txt
stat -c '%y %n' state/fragments/sw.yaml
echo "### 校验"
echo "grep -c iss368 = $(grep -c iss368 state/fragments/sw.yaml)"
echo "DONE"
