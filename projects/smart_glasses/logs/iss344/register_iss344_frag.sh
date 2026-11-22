#!/usr/bin/env bash
# =============================================================================
# register_iss344_frag.sh —— ISS-344 分片登记 (★只走 state/frag_write.py·零 open(p,"w")★)
# =============================================================================
set -eu
cd "$(dirname "$0")/../.." || exit 2
FW="python3 state/frag_write.py --agent sw-lead"

$FW --add-artifact 'path=SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md kind=doc version=1.1 updated_at=2026-11-23 summary="★ISS-344 追加式分级订正 (老字一字未删): 6 条 (JTAG_TDI / SPI_MISO_BOOT / SPI_MOSI_BOOT / SPI_SCLK_BOOT / UART_RX / USB_CC2) 由 NC 改判【必需 · 进 S8 布线目标 · 板侧不许标 NC】; FSIN_OUT 保留可悬空但补条件 (现在不许落 NC); §0 / §2 / §3 / §3-1 / §4 / §5 / §6 逐处追加订正 + 文末 §7 分级订正小节; 只增不删由字符级子序列自证 (logs/iss344/03_only_additions_proof.txt)★"'

$FW --add-artifact 'path=SW/tools/check_sw_zero_copper_grade_consistency.py kind=tool version=1.0 updated_at=2026-11-23 summary="★ISS-344 新闸: 只读 HW/check_s8_target_list.py 的 REQUIRED_SINGLE / FLOAT_OK (AST 静态解析·不执行其代码·一字不改) ⇒ 扫 SW 页 §3 / §3-1 的建议板侧标记 ⇒ C0~C9 九条判据 (凡判 NC 必须在 FLOAT_OK / 凡在 REQUIRED_SINGLE 判 NC 就判红并点名 / 必需网固件侧清单必须标作废 / 待定必须为 0); 反向用例: tmp 副本把 JTAG_TDI 改回 NC ⇒ 判红并点名 JTAG_TDI ⇒ 恢复判绿 ⇒ 真件零被动★"'

$FW --add-artifact 'path=logs/iss344/ kind=log version=1.0 updated_at=2026-11-23 summary="★ISS-344 机器原始输出: 01_gate_green / 02_reverse_case_red / 03_only_additions_proof / 04_diff_only_additions / 05_mandatory_commands / 06_boundary_md5 / 07_refs_exist / 08_grade_lines + 一条命令复现 run_iss344.sh + 订正执行器 apply_iss344_corrections.py + 自证器 check_only_additions.py + 反向用例 reverse_case.py★"'

$FW --add-artifact 'path=HANDOFF/2026-11-23_sw-lead_ISS344_零铜网分级口径对账.md kind=handoff version=1.0 updated_at=2026-11-23 summary="★ISS-344 交卷页 (B1~B6 齐全): 结论摘要 / 验收标准逐条自评 / 证据分级 / 接口取值声明 / 未决项与卡点 / 自证复现命令; 回答 main §4 的 3 个问题 (6 条冲突逐条对 pm.yaml key / SW 页旧分级陈述行号 / 反向用例点名)★"'

$FW --add-claim 'key=iss344_sw_zero_copper_grade value="必需 23 (15 条高速差分腿 + 8 条单端脚: CAM_RESET_N / LED_G_D / USB_CC2 / JTAG_TDI / UART_RX / SPI_SCLK_BOOT / SPI_MOSI_BOOT / SPI_MISO_BOOT) · 可悬空 1 (FSIN_OUT, 条件式: 板那一趟新基线上仍是零铜才允许标 no-connect; 标 NC 是板那一趟的板侧动作, 现在只定口径不动手) · 待定 0" note="★ISS-344: SW 侧口径已对齐 main 2026-11-22 20:5x 终裁 (iss334_need4b_zero_copper_net_triage / iss338_need_jtag_group_decision / iss338_need_boot_storage_answer / iss338_need_usbif_cc1_cc2_rule); 板侧真值源 = HW/check_s8_target_list.py (只读·一字不许动); 本单只对齐不重判, 零外发零新增老板拍板项★" ref="SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md §7 · HW/check_s8_target_list.py"'

$FW --add-answer 'key=iss344_sw_grade_alignment to=main value="★**ISS-344 交回 main (2026-11-23)**: ① SW 页 6 条冲突 (JTAG_TDI / SPI_MISO_BOOT / SPI_MOSI_BOOT / SPI_SCLK_BOOT / UART_RX / USB_CC2) 已按你 2026-11-22 20:5x 终裁【追加式】改判为【必需 · 进 S8 布线目标 · 板侧不许标 NC】(依据逐条引 pm.yaml 的 4 个 key 原文); ② FSIN_OUT 保留可悬空但补上条件 (板那一趟新基线仍零铜才允许标 NC, 现在只定口径不动手 ⇒ SW 侧现在没有落任何 NC); ③ 这 6 条对应的固件侧降级声明条目一律标【作废】, 不是改写成新的固件侧改动 (那是板那一趟同批改的活); ④ 新建闸 SW/tools/check_sw_zero_copper_grade_consistency.py (只读 HW/check_s8_target_list.py 的 REQUIRED_SINGLE / FLOAT_OK ⇒ 判 NC 的网必须在 FLOAT_OK, 在 REQUIRED_SINGLE 的网判 NC 就判红并点名), 反向用例已在 tmp 副本上跑通 (判红并点名 JTAG_TDI, 恢复判绿, 真件 md5 零变动); ⑤ 固件本体 / 板 / 落表 / 板侧判据 一个字节都没动; 零外发; 本单未新增任何老板拍板项★" ref="HANDOFF/2026-11-23_sw-lead_ISS344_零铜网分级口径对账.md · SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md §7 · logs/iss344/"'

$FW --status 'phase=delivered progress_pct=100 health=green summary="★ISS-344 交卷: 零铜单端网分级口径对账 —— SW 页 6 条 (JTAG_TDI / SPI_*_BOOT x3 / UART_RX / USB_CC2) 由 NC 改判【必需】(追加式·老字一字未删), FSIN_OUT 补条件式可悬空 (现在不落 NC), 新建 SW 侧分级一致性闸 (只读板侧判据) + 反向用例判红点名, 零写板 / 零落表 / 零改固件本体 / 零改板侧判据 / 零外发; 板 md5 611b869e13518c3c023fb178f91a0075 未动★"'

echo "── 分片登记完成 · iss344 命中数 ──"
grep -c iss344 state/fragments/sw.yaml
