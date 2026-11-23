#!/bin/bash
# ★★【ISS-367 · mech-lead · 分片写入】★★ ★只走 state/frag_write.py ★
# ★写前/写后 md5 各记一次 (★并发守卫★) ★
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
F=state/fragments/mech.yaml

echo "=== 写前 md5 基线 ==="
md5sum "$F"
stat -c '%y %s' "$F"
md5sum "$F" > logs/iss367/16_frag_md5_before.txt
stat -c '%y %s' "$F" >> logs/iss367/16_frag_md5_before.txt

python3 state/frag_write.py --agent mech-lead \
  --add-artifact 'path=MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md kind=spec version=v1 summary="ISS-367 新建规格页: S10 把 D_LED_G 换官方 0805 后 LED 窗口规格同趟重算 (§0 口径 §1 漂移本体 §2 MECH_SYNC 定点改写逐字 §3 S6_CALIBER LED 窗口规格 §4 同趟重算清单 §5 未决项 §2.4 本趟自审更正)"' \
  --add-artifact 'path=MECH/check_onepass_s10_led_spec_sync.py kind=gate version=v1 summary="ISS-367 新建机器闸: L0 基准块 L1 四组数==实算 L2 sweep 非单调须显式承认 L3 两处定点改写不许与实算打架 L4 证据等级五级白名单 L5 零挂起措辞 L6 沙盒在项目盘 tmp/ + --selftest 7 条反向用例全抓到" ' \
  --add-artifact 'path=HANDOFF/2026-11-23_mech-lead_ISS367_S10换封装LED窗口规格同趟重算.md kind=handoff version=v1 summary="ISS-367 交卷页: B1~B6 六段齐全 + 20 条验收线逐条判定 + 落盘清单 + 沙盒留证路径 + 一键回滚说明" ' \
  --add-claim 'key=iss367_mech_s10_led_space_recompute value="2183 / 2.225..3.250 + 73.215..74.385 / 2183·2241·2253·2197 (不再单调)" note="ISS-367 实算 (25 件 S10 MECH 侧子集口径 · 双路径交叉对账一致 · logs/iss367/07_compute_after.json + 04_crosscheck_two_paths.txt): 可落位块数 1992→2183 (+191) · 两条整高自由带 X 1.550..3.450 / 72.540..73.660 → 2.225..3.250 (宽 -0.875) / 73.215..74.385 (宽 +0.050) · 净距敏感度 sweep 1992/2016/2031/2075 → 2183/2241/2253/2197 ⇒ clr=0.5 的 2197 < clr=0.2 的 2253 ⇒ 不再单调 ⇒ 页与两处机器块三份同源 [实测]" ' \
  --add-claim 'key=iss367_mech_two_spot_rewrites_done value="MECH_SYNC + S6_CALIBER 两处机器块已按实算逐字改写 (diff 留证在盘)" note="ISS-367 定点改写 (main 授权只这两处): ① MECH/BOARD_ONEPASS_MECH_SYNC.md 机器块 led.full_height_bands / nearest_band / hypothesis_*.space / hypothesis_*.net_len_range_mm / clearance_sweep + 新增 s10_basis + 正文 8 行 (md5 c7945f59… → ddd931ea…) ② MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 机器块 led_window_g_bench_hard.rect + led_window_g_bench_recommended.rect + §4.2/§5/§6b/§9.3 共 18 行 (md5 d7b33ed7… → b254fa98…) ⇒ 两页其余任何一行逐字节未变 (diff -u 全文留证 logs/iss367/11_diff_*.txt) ⇒ 改前原文备份 logs/iss367/10_pre_*.md + 一键回滚说明 logs/iss367/12_ROLLBACK.sh [实测]" ' \
  --add-claim 'key=iss367_mech_l4_false_red_fixed value="L4 判据方向 (五级白名单) 一字未改 · 9 条假红已消" note="ISS-367 CONT1 自审: 本单机器闸 L4 原有【自身假红】9 条 —— 病灶 = 把方括号包裹的数值区间 ([-0.750, +2.150]) 与数组字面量 ([\"placeable\"]) 也当证据等级来判 ⇒ 修法只落在产生点 (只把内容全为中文表意文字+ASCII 数字且至少含一个中文的方括号 token 当等级候选) ⇒ 白名单方向未动 ⇒ 非白名单等级标签照样红 ⇒ 另反向用例由 6 条增到 7 条 (新增 把 §2 全部证据等级清空 ⇒ L4 红) ⇒ --selftest rc=0 7/7 全抓到 (logs/iss367/15_selftest.txt) [实测]" ' \
  --add-claim 'key=iss367_mech_s10_spec_corrections value="上一趟清单漏 2 处同源行 + 1 处落位原点坐标写错 ⇒ 本趟按实算改正" note="ISS-367 CONT1 实跑复核: ① 上一趟 §2.1/§3.1 改写清单漏了 MECH_SYNC 机器块 items[].spec (两假设空间) 与 S6_CALIBER §9.3 S6 落位约束第 ④ 条 ⇒ 本趟补进清单并已改写 ② §3.1 item 8 的最近落位封装原点后三档上一趟按 x1±clr 硬推写错 ⇒ 实算 = (7.715, 63.775) / (7.815, 63.875) / (8.115, 64.175) (logs/iss367/08_nearest_origin.json · 同函数同口径复跑 BEFORE 与改前页逐字相同) ③ §1.3/§5.1 四处差值算错已按实算改正 (封装原点窗口 Y 内缩 0.050/0.450 · 最近落位带 带宽 1.310→0.935 与 带高 4.200→3.650 · 窄 0.375) [实测]" ' \
  --add-need 'key=iss367_mech_s10_swap_set_count_to_main to=main item="★ISS-367 登记 (要 main 拍 · 本单不代拍): 「板只改一次」那一趟 S10 到底换几件? ★本页与两处机器块全部用【MECH 侧 25 件子集】口径 (= 与 ISS-365 沙盒、与 main 复核过的三个数同源); ★若那一趟把 91 件靶子全换 ⇒ 可落位块数 2183→2200 · sweep 2200/2237/2250/2167 ⇒ 本页与两处机器块当场失效 ⇒ 那一趟开工当天必须先跑 python3 MECH/check_onepass_s10_led_spec_sync.py (rc≠0 就按 --compute 的读数更新)。★另 D_LED_G 结构光孔有/无 (老板项 U-365-3) 与 按键 3N vs 1.5N 仍只登记不代拍 —— 见 MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md §5。★[实测]" since=2026-11-23' \
  --status 'phase=delivered progress_pct=100 health=绿 summary="ISS-367 交卷: 「板只改一次」S10 把 D_LED_G 换成官方 0805 后的结构侧两处未收口项已同趟重算并定点改写 ⇒ 可落位块数 1992→2183 · 两条整高自由带 1.550..3.450 / 72.540..73.660 → 2.225..3.250 / 73.215..74.385 (带 A 宽 -0.875) · sweep 1992/2016/2031/2075 → 2183/2241/2253/2197 (clr=0.5 的 2197 < clr=0.2 的 2253 ⇒ 不再单调) ⇒ MECH/BOARD_ONEPASS_MECH_SYNC.md 机器块 + MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 的 LED 窗口规格两处已按实算逐字改写 (diff 与改前原文留证在 logs/iss367/) ⇒ 新建规格页 MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md + 新建机器闸 MECH/check_onepass_s10_led_spec_sync.py (L0~L6 全绿 · --selftest 7/7) ⇒ 本单机器闸 L4 的 9 条自身假红已修 (只改什么算证据等级 · 白名单方向未动) ⇒ 上一趟 3 处错值已按实算改正 ⇒ 零写板 (611b869e… / mtime 2026-11-06 07:07:17) 零落表 零改既有闸 零改 BOARD_ONEPASS_STRUCT_CROSSCHECK.md 零挂链 零外发 未替老板拍板 (光孔有无 / 换件集合口径 只登记) ⇒ 写 5 处 = 规格页 + 新闸 + 交卷页 + logs/iss367/ + 本分片 (只走 state/frag_write.py)"'

echo "rc=$?"
echo "=== 写后 md5 ==="
md5sum "$F"
stat -c '%y %s' "$F"
md5sum "$F" > logs/iss367/17_frag_md5_after.txt
stat -c '%y %s' "$F" >> logs/iss367/17_frag_md5_after.txt
