#!/bin/bash
# ★ISS-326 cont5 · 分片增量写入 (必须走 state/frag_write.py --agent mech-lead) ★
set -e
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

python3 state/frag_write.py --agent mech-lead \
 --add-artifact 'path=logs/iss326/verify_final.log kind=evidence version=1.0 updated_at=2026-11-18 summary="★ISS-326 cont5 交卷前自证全量日志 (741行/65451B · 2026-11-18 17:09:08 实跑)★: merge.py rc=0 (产出676 | 阻塞43 | 未闭合需求338 | 冲突0) · gate_check.py rc=0 (Q1 18/18 · Q2 3/3 · Q3 979条claim · Q4 95/488 · Q7 钉板md5闸链 9/9 全绿 · 缺口清单3条) · issue_check.py rc=0 (登记325条 | 逾期0 | 未闭合blocker10 | 问题闭环门全过) · 板md5 611b869e13518c3c023fb178f91a0075 · 板mtime 2026-11-06 07:07:17.362193413 +0800 · 两份交付页占位符 0/0 · tmp/iss326 软链 0 ⇒ 7/7 期望值全对得上 ⇒ 零写板/零落表/零改闸/零改既有文档正文/沙盒无软链 五条边界自证通过★"' \
 --add-claim 'key=iss326_hard_metric_provenance value="12类硬指标逐条带判据脚本+行号+复算命令" note="★ISS-326 cont5 补: 交卷页 B1-1 硬指标表新增第4列「产出它的判据脚本 + 行号 + 复算命令」· 12 行逐条给出 (a) 判据脚本路径+行号 (b) 落盘产物 (c) 一条可复算的命令 ★ · 逐条出处: 1,934行 → iss326_scan_mech_refs.py L263+L277 · 218(186+32) → 同脚本 L242-L244 + L84-L94 自证断言 · 三口径 → iss326_reconcile_counts.py L47-L51 (产物 reconcile_counts_raw.txt L2-L5 顶层 + L34-L37 递归) · 口径D 571 → ★无单一出处★ (main 自己grep未落盘; 见 reconcile6_raw.txt L37-L101 穷举结论: 任何 子集x正则x计数方式 都复现不出571) · py-only 578 → iss326_reconcile6.py L36+L43 · 假阳性 5,619 → ★无单一出处★ (口径C 减口径A 的派生量; 复算式已给) · 三清单 383/164/1356/31 → iss326_disposition.py L273+L276-L279 (tsv 列 $8) · 三形态 1588/87/259 → 同脚本 L280-L281 (tsv 列 $9) · 沙盒8条 → iss326_sandbox.py L126/L197/L222/L258/L293-L301/L334-L335 (results.json 8条) · fresh基线 60/56/16 → mech_gate_proto.py L157-L162 · 暴露面 68+7 → 同脚本 L170-L174 · 扫描面 113份/230token → 同脚本 L143+L147+L183 ★ · ★不许编行号: 无出处的两条明写「无单一出处」并指向穷举日志★" ref="HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md#B1-1"' \
 --add-claim 'key=iss326_gate_check_current_reading value="rc=0" note="★ISS-326 cont5 实跑更正上一版的一句话: state/gate_check.py 本轮 rc=0 (Q1 18/18 齐全 · Q7 9/9 钉板md5闸全绿) ⇒ ★上一版交卷页 B5-8「红在 SW 侧 (反向测试夹具假位号) · rc=1」的口径本轮不成立, 该红已消失★ ⇒ 本单零改闸边界没破 (state/gate_check.py 未改) · 证据 logs/iss326/verify_final.log L5-L68 ★ · ★本条只报读数, 不替 main 改判据★" ref="logs/iss326/verify_final.log"'

echo "FRAG_WRITE_RC=$?"
