#!/bin/bash
# ISS-335 · sw-lead 分片 status 补写 (★必须走 state/frag_write.py 原子写★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

python3 state/frag_write.py --agent sw-lead \
  --status 'phase="delivered"' \
  --status 'progress_pct="100"' \
  --status 'health="green"' \
  --status 'summary="ISS-335 (2026-11-19 00:4x~00:5x) 交卷: SW 侧「板只改一次」准出汇总闸已落地 —— 一条命令 python3 SW/tools/check_onepass_sw_release.py 给出 SW 侧能不能出 Gerber 的结论 (主跑 rc=0, 绿 10 红 0, 逐条 rc 见 logs/iss335/01_main_run.log)。对标 MECH 侧 ISS-300 的 check_onepass_mech_release.py, 判定对象换成 SW 侧。清单基准 = ISS-321 实测表那 10 道 (含 4 道链外闸: check_demo_panel_spec / check_shutdown_semantics / check_timing_review_adc_sync / timing_check —— 板那一趟当天它们会红而今天不在链上 ⇒ 没人会注意到), 少一道 ⇒ 汇总直接红。fail-closed 四条全部实测: 脚本不存在 / 跑不起来 / 超时 300s / rc 非 0 一律算闸红, 绝不没跑就当过。TMPDIR 一律指项目内 tmp/iss335_tmp (本机系统临时目录配额到顶, 不指会 6 道一起假红)。三道 R6 闸必须裸跑 —— 传 --selftest 会 rc=2 usage 错误 ⇒ 汇总自己红, 自检 6b 现场实测三道都 rc=2 证明这条坑是真的。--selftest rc=0, 8 组反向用例全过, 真件真闸真篡改跑在沙盒副本 (SW/ 与 state/ 真拷贝), 真盘一个字节没碰。位号可达性闸列 v1 还是 v2: 建议默认 v1 判决 + v2 影子, 已登记 needs_from (iss335_ref_gate_v1_or_v2, to=main, waiting_on 留空) 等 main 拍, 本单不代拍也不改 state/gate_check.py 一个字节。交付: SW/tools/check_onepass_sw_release.py (新建) + SW/ONETRIP_SW_RELEASE_GATE_SPEC.md (清单页 + 当天 SOP + 回滚三档) + HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md (B0~B6) + logs/iss335/ (机器原始输出)。零写板 (板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17.362193413 前后逐字节相同) 零落表 (网表 / 脚表 / BOM 三件 md5+mtime 不变) 零改既有 16 道 SW 闸 零改 gate_check.py 零改 issue_log.yaml 零改别人分片 零外发。"'
echo "FRAG_STATUS_RC=$?"
