#!/usr/bin/env bash
# ISS-334 分片写入 (★只走 state/frag_write.py --agent hw-lead★)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

python3 state/frag_write.py --agent hw-lead \
 --add-need 'key=iss334_need1_generator_drift to=main item="ISS-334 need-1: 生成器已漂移 (现生成器只出 2,492 段 vs 官方 stage-1 17,022 段; 链自校准闸 L120~L122 已明写) => env 级臂与官方板不同工艺 => 不可比. 问: 恢复官方产出口径, 还是用现生成器另立新基线? 不答后果: 桶B 16 条零铜网没有可比臂, 板那一趟再踩一次 ISS-328 的不可比坑. 建议默认值: 先立新基线并在新基线上重读 24 个零铜网. 建议排期: 板那一趟 A 步之前"' \
 --add-need 'key=iss334_need2_production_point_auth to=main item="ISS-334 need-2: 是否授权改产生点 state/gen_pcb_routing.py 的 A*, 让它对整网无铜的网 (segment=0 且 pad>=2) 做整网重布, 四条护栏=只加铜不删铜 + 孤岛数不得变多 + 差分腿不得打死 + 改完先跑 compare_arm_official.py --self-test. 不答后果: 桶C 只能擦在产物上, 而本单实测已被证伪 (A* 在官方 stage-1 补 0 条 / 未成 54 条). 建议默认值: 授权. 建议排期: 板那一趟 D 步"' \
 --add-need 'key=iss334_need3_pair_corridor_false_positive to=main item="ISS-334 need-3: state/pair_corridor.py 在官方板上跑完打印 落铜成功 P 1段/N 1段, 但段数 18,092->18,092 且两板几何等价 rc=0 且 CSI_D0_D0_N 仍 0.000mm => 1格退化路径的假阳性. 问: 授权不授权修这个工具 (至少把 1 格路径判成失败, 再谈续段)? 不答后果: 桶A 7 条零铜差分腿空转. 建议默认值: 授权先修假阳性判定; 修完在 tmp 复跑单对, 段数必须 >= 17,024 才算好. 建议排期: A1 臂开跑前"' \
 --add-need 'key=iss334_need4a_single_end_net_usage to=sw-lead item="ISS-334 need-4a: 官方板 24 个零铜网里有 9 条单端低速脚 (CAM_RESET_N, FSIN_OUT, JTAG_TDI, LED_G_D, SPI_MISO_BOOT, SPI_MOSI_BOOT, SPI_SCLK_BOOT, UART_RX, USB_CC2). 问: 固件里这 9 条到底用不用? 特别是 JTAG_TDI / SPI_*_BOOT / LED_G_D / FSIN_OUT / CAM_RESET_N 这 5 条. 不答后果: 为救一条调试脚去动高速差分走廊, 风险不对称. 建议默认值: sw-lead 按固件引用逐条给 用 或 不用. 建议排期: 板那一趟之前"' \
 --add-need 'key=iss334_need4b_zero_copper_net_triage to=main item="ISS-334 need-4b: 请汇总并拍 24 个零铜网按必需性分级 (必须救回 / 可悬空). 输入: sw-lead 的固件引用 (need-4a) + 本单清单 (HW/PCB/ONETRIP_S8_MECHANISM_PATH.md 第一节第3小节). 不答后果: 板那一趟会为 9 条单端脚去改差分走廊. 建议默认值: 必需=15条差分腿+USB_CC2+UART_RX, 其余以固件引用为准. 建议排期: 板那一趟之前"' \
 --add-need 'key=iss334_need5_gate_reference_board to=main item="ISS-334 need-5: 名单制闸 compare_arm_official.py 只能配官方板 (18,092 段) 才有意义, 而现生成器链终板是 3,304 段. 问: 板那一趟的臂一律要求先满足段数 16,283~19,901 再进闸, 还是允许与同工艺基线 3,304 段比? 不答后果: 拿不可比的板去过闸, 闸的结论无效 (ISS-328 就这么死的). 建议默认值: 采纳本单建议 = 一律与官方板比但必须先过区间自检. 建议排期: 板那一趟 A 步"' \
 --add-need 'key=iss334_need6_boss_letter_scope to=main item="ISS-334 need-6: 老板口径那 8 个字母 (W-2 / W-1c / A4 / W-3 / U-1 / P7 等) 要不要并进机制级路线? 问法: 机制级三桶 (A成对走廊 / B出脚几何 / C路由器本体) 全是布线层机制, 不动器件选型与拓扑 => 与口径并行不冲突, 是否按此推进? 不答后果: 机制级做出来的板可能与老板口径打架. 建议默认值: 并行推进, 口径落定后再合并出最终板. 建议排期: 板那一趟之前"' \
 --add-claim 'key=iss334_zero_copper_net_count value=24 note="实测: 官方板 pad>=2 且 segment=0 的网数, 定义与 compare_arm_official.py 的 zero_copper 指标逐字一致; 24/24 全部落在 DRC 未连接网里"' \
 --add-claim 'key=iss334_bucket_split value="A=7/B=16/C=1" note="实测+推算: A=差分腿且伙伴腿官方有铜; B=最紧端点最优出脚余量<=+0.30mm; C=余量>=+0.30mm 而 A* 仍找不到路. 判据见 HW/PCB/ONETRIP_S8_MECHANISM_PATH.md 第二节"' \
 --add-claim 'key=iss334_official_stage1_segments value=17022 note="实测: /tmp/chain_offverify/s1_straight.kicad_pcb = 官方链的 stage-1; 官方板可由它完整复现 (cmp_pcb_geom rc=0, 走线 17980 + 过孔 433 + 铜皮 5 区全同)"' \
 --add-claim 'key=iss334_current_router_segments value=2492 note="实测: /tmp/chain_v76mg1/s1_straight.kicad_pcb; 生成器已漂移 => env 级臂不可比 (链自校准闸 L120~L122)"' \
 --add-claim 'key=iss334_comparable_segment_band value="16283-19901" note="推算: 官方 18092 段 正负10%; 过孔区间 390-476; 越界即判不可比"' \
 --add-claim 'key=iss334_astar_on_official_s1 value="补上0条/未成54条" note="实测: grid 0.125 + margin 0.0625 跑在官方 stage-1 上, 产物 md5 与输入逐字节相同 => 病根在路由器本体, 不在后处理顺序"' \
 --add-claim 'key=iss334_pair_corridor_zero_copper value=零新增铜 note="实测: 官方板上跑 pair_corridor.py 打印 落铜成功 P1段/N1段, 但段数 18,092->18,092 且几何等价 rc=0 => 1格退化路径假阳性"' \
 --add-artifact 'path=HW/PCB/ONETRIP_S8_MECHANISM_PATH.md kind=note summary="ISS-334 主交付页: 零铜网0号清单(24条 fresh) + 三桶死因归类 + 候选臂设计(含对照有效性自检与可比性自检) + 沙盒预演读数 + 6条need + 复现命令"' \
 --add-artifact 'path=HW/PCB/BOARD_ONEPASS_S8_MECHANISM_ACTIONS.md kind=note summary="ISS-334 板那一趟逐字作业包: S8-1复现官方 / S8-2桶A臂 / S8-3桶B臂 / S8-4桶C臂 / S8-5收口(板md5只变一次); 每步=命令+验收读数+不过怎么办"' \
 --add-artifact 'path=HANDOFF/2026-11-18_hw-lead_ISS334_机制级换机制路线.md kind=note summary="ISS-334 交卷单: B0~B7 齐全, 6条need交main/boss, 零写板零落表零改闸零外发"' \
 --status 'phase=delivering progress_pct=80 health=green summary="ISS-334 机制级换机制路线: (1) 官方板零铜网=24个 (pad>=2且segment=0, 与闸定义逐字一致), 24/24落在45条未连接里; 其中15条高速差分腿+9条单端低速脚 => 布局级处方最多碰6个 => 18个原理上覆盖不到; (2) 死因三桶: A成对走廊7 / B出脚几何16 / C路由器本体1 => 几何卡死这个前提是假的 (88/88端点物理可行 + 出脚方向CSP可行); (3) 决定性读数: A* 在官方stage-1(17,022段)上补0条/未成54条且产物md5与输入逐字节相同 => 病根在路由器本体不在后处理顺序 => 只有修在产生点才有戏; (4) 官方板可完整复现 (chain_offverify终板 与 官方板 几何等价 rc=0) => 臂有同工艺起跑线; 但生成器已漂移 (2,492 vs 17,022段) => env级臂不可比 => ISS-328右上臂3,986段的死因同机制; (5) 桶A机制实测撞墙: pair_corridor.py 打印落铜成功但零新增铜(几何等价rc=0) => 1格退化路径假阳性; (6) 候选臂3条+同配方对照臂3条已设计(含对照有效性自检与可比性自检), 沙盒预演4条已跑, 官方补丁链未跑(任务书禁止); (7) 6条need交main/boss, 一条都没自己拍; (8) 判据=名单制闸rc=0+DRC0, 禁拿unc变少当成功, 板md5只变一次"'
RC=$?
echo "FRAG_RC=$RC"
exit $RC
