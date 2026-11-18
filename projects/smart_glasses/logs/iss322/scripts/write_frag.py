#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-322 · tmp 沙盒脚本 · ★分片写入驱动 (★走 state/frag_write.py 的原子写·禁 open(p,"w")★)★
★ frag_write.py 的 CLI 形态: 每个 --add-* 标志收【一个】字符串, 内部用 shlex.split 拆成 key=value
★ ⇒ 值里带空格 ⇒ 必须用双引号包起来 (shlex 语义) ★"""
import subprocess, sys, os

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FW = os.path.join(PROJ, "state", "frag_write.py")
A = []


def q(v):
    """包成 shlex 认的双引号串"""
    return '"' + v.replace('"', "'") + '"'


A += ["--add-artifact",
      "path=HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md kind=doc version=1.0 updated_at=2026-11-18 "
      "summary=" + q("ISS-322 · S8 布线归零作业包: 45 条 unconnected 逐条清单(机器搬·条数=45 与 check_pcb_drc 的 C4 逐字一致) + "
                     "逐条死因登记(桶: 几何不可布(布局级) 22 / 算法可解 18 / 口径未定 5) + 高速腿几何可布性判定"
                     "(结论 (a) 几何可布: 端点 88/88 可出 · SoM 主体区 In1/In3/In5/In6/B.Cu 各占 0.38% ⇒ 板框与层数都不用改 · "
                     "真瓶颈是段内 P/N 顺序翻转 17/47 处) + 逐条修法/BATCH-1-2-3/逐条验收命令 + 7 条待拍死结 + 证据分级")]

A += ["--add-artifact",
      "path=HANDOFF/2026-11-18_hw-lead_ISS322_S8布线归零作业包.md kind=handoff version=1.0 updated_at=2026-11-18 "
      "summary=" + q("ISS-322 交卷页 (B0~B6 齐全) · 零写板双证 · gate_check rc=1 的 SW 域红项逐字归因")]

A += ["--add-artifact",
      "path=logs/iss322/ kind=evidence version=1.0 updated_at=2026-11-18 "
      "summary=" + q("ISS-322 全部原始读数 (01~29 号 raw) + 11 个只读探针与分析脚本 · 交卷页引用的每个读数都有对应 raw 文件")]

CLAIMS = [
    ("iss322_s8_45_unc_itemized",
     "45 条 unconnected 逐条清单 (8 列: #/网名/起点(ref+pad+x,y)/终点/长度mm/类型/死因桶/修法) · 机器搬 · "
     "条数与 check_pcb_drc 的 C4 行逐字一致 = 45",
     "[实测] logs/iss322/01_check_pcb_drc_baseline.txt + tmp/iss322/build_table45.py (带 assert len==45 的 abort 校验)", ""),
    ("iss322_s8_23_vs_13",
     "不打架: 23 = DSI_+CSI_ 未连接条目数 / 22 = 高速网名总数 / 13 = DSI_ 单方向网名数 / 9 = CSI_ 单方向网名数 · "
     "13+9=22 网名 = 23 条 (CSI_D0_D0_N 3 焊盘断成 2 段)",
     "[实测] logs/iss322/02_extract_unc_summary.txt", ""),
    ("iss322_s8_hs_geometric_verdict",
     "(a) 几何可布 —— 但必须带一次布局修正: 端点 88/88 物理可出 (W=0.20 与 W=0.15 均 0 个不可能) · "
     "SoM 主体区 x8..76 y6..56 逐层占布 F.Cu 5.73% / In2.Cu 1.52% / In4.Cu 0.81% / In1·In3·In5·In6·B.Cu 各 0.38% · "
     "J_SOM_P1..P4 各 100 个 SMD 焊盘且通孔 0 ⇒ 板框 160x100 与 8L 都不用改 ⇒ 板 md5 不会因几何而第二次变 · "
     "真瓶颈是段内 P/N 顺序翻转 17/47 处 (DSI 4 族在 R_SEL/TP_DSI 侧 Δx=4.80mm · CSI 5 族在连接器侧 Δx=0.50mm)",
     "[实测] logs/iss322/06_probe_escape_feasibility.txt + 19_probe_som_body.txt + 20_probe_pn_order.txt", ""),
    ("iss322_s8_lane_order_evidence",
     "8 块同代板对照: R_SEL_* 集群 x 序与 SoM 端序一致的 7 块 (v76me0/mg0/mj0/mv0/mw0/mx0 + best_unc23) 的 unc = "
     "35/35/28/29/29/26/23, 唯独 lane 序反向的现役板 = 45 (全盘最差) ⇒ 修法是把 21 个 R_SEL_*/TP_DSI_* 挪到左上 "
     "x 5.50..38.35, 不是挪到右上 (ISS-265 方案 A 的方向需复议)",
     "[实测] logs/iss322/22_lane_order_vs_unc.txt · 因果性部分标 [推算] (7/1 对照未严格控制路由器/seed)", ""),
    ("iss322_s8_zero_copper_mechanism",
     "22 个高速未连通网名里 15 个在板上零铜 (一根线都没长出来) ⇒ 路由器是没布出来不是布歪了 ⇒ 换层/让路闸等增量手段"
     "对它们无效 ⇒ 必须换机制 (成对走廊 + 布局修正 + 布线顺序) · 同时: 走线 18092 段这个指标对 S8 零信息量 (假绿来源)",
     "[实测] logs/iss322/18_hs_copper_amount.txt", ""),
    ("iss322_s8_official_board_not_independent",
     "「官方板 18092」= 现役板本身 (official_18092_unc.drc.json 的 source=demo_mainboard.kicad_pcb; 现役板实测走线 "
     "18092 段/过孔 433) ⇒ 与现役板网名签名 43/43 完全相同、差集 0 ⇒ 「官方板同病」对 45/45 全真、零区分度 ⇒ "
     "本单把它从桶降级成标记列; 几何级的真正旁证是 17/47 段内翻转 + SoM 主体区逐层占布 + 8 块板对照",
     "[实测] logs/iss322/07_cmp_unc_sets_cur_vs_official.txt + 24_unc_diff_vs_unc_target_map_baseline.txt", ""),
    ("iss322_s8_unc_target_map_diff",
     "UNC_TARGET_MAP.md 的基线 (baseline_v76mw0_chain, 本机重跑 unc 29 条/24 签名) 与现役板 (45 条/43 签名) 的差集 = "
     "只有现役板有 31 条 + 只有基线板有 12 条 + 交集 12 条 ⇒ 那份三桶表只覆盖现役板 43 网名中的 12 个 (28%) ⇒ "
     "不许拿它的 22 网名当现役板靶集",
     "[实测] logs/iss322/24_unc_diff_vs_unc_target_map_baseline.txt", ""),
    ("iss322_s8_fail_history_correction",
     "v44/v46/v47/v48 四臂共同失败 = 39 个网名 / 45 个 (net,pad) 对 / 16 条高速腿; 任务书点名的 DSI_D0_CK / "
     "DSI_D0_CK_SRC / DSI_D0_D1 三个网名在四个 fail_detail 文件里一个都不存在, 真实的是 DSI_D0_CK_N / "
     "DSI_D0_CK_N_SRC / DSI_D0_D1_N; 且四臂同代 ⇒ 有算法同源混淆 ⇒ 证明得了「调参数调不出来」, 证明不了「布局是唯一因」",
     "[实测] logs/iss322/08_fail_history_intersection.txt", ""),
    ("iss322_s8_zero_proven_on_disk",
     "归零是否可达 = [0数据] —— 盘上 9 份 DRC JSON 最低 unc = 23 (best_unc23_clrfix, 2026-11-11 04:43), 无一份 = 0 ⇒ "
     "本单只判「几何不构成障碍」, 不判「零可达」⇒ 归零与否仍要 iss322_s8_p7_zero_scope 拍",
     "[0数据] logs/iss322/14_min_unc_scan.txt",
     "ref=HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md"),
]
for k, v, n, extra in CLAIMS:
    A += ["--add-claim", "key=%s value=%s note=%s %s" % (k, q(v), q(n), extra)]

NEEDS = [
    ("iss322_s8_p7_zero_scope",
     "问法: S8 归零到底要不要动板框/层数? 本单实测: 不要 —— SoM 主体区 x8..76 y6..56 内 In1/In3/In5/In6/B.Cu "
     "各只占 0.38%, J_SOM_P1..P4 全是 F.Cu 上的 SMD(通孔 0), 且同框同层数的 best_unc23 板做到 unc 23 ⇒ "
     "是不是把 P7 口径从「C1/C2/C3 改板 / C4 不归零」改成「同框归零」? | 谁答: main (转老板) | "
     "不答的后果: 沿用 ISS-308 判「现役帧上 45→0 不可达」⇒ S8 不以归零收口 ⇒ G1 开不了 ⇒ 投不了板; "
     "或走 C4 分级放行 ⇒ 带着 11 条「两块板都没布通」的硬骨头 (高速 8 + 非高速 3) 投板 ⇒ 投板后才发现 = "
     "2-4 周 + ¥4-8K | 建议默认值: 「同框归零」(依据 §3-4 + §3-7 实测) ⇒ P7 只需选板形, 不必选「改不改板」 | "
     "建议排期: BATCH-1 开工前"),
    ("iss322_s8_rsel_lane_order",
     "问法: R_SEL_* + TP_DSI_* 这 21 个 DSI lane 器件, 挪到【左上 x 5.50..38.35】还是【右上 (ISS-265 方案 A)】? "
     "本单实测: 左上那 7 块同代板 unc = 23/26/28/29/29/35/35, 右上现役板 = 45 (全盘最差) ⇒ 建议【左上】 | "
     "谁答: main + 老板 (要动布局 ⇒ 动板 md5) | 不答的后果: 按 ISS-265 方案 A 布 ⇒ 段内 P/N 顺序翻转 17/47 处 ⇒ "
     "高速 23 条必然要交叉 ⇒ 归不了零 ⇒ 板 md5 变两次 (S6 布局一次 + S8 再布一次) = 2-4 周 + ¥4-8K | "
     "建议默认值: 左上 x 5.50..38.35 (R_SEL_* y=3.00 · TP_DSI_* y=6.20) | 建议排期: BATCH-1 开工前"),
    ("iss322_s8_csi_cap_side",
     "问法: CSI 5 族在 CONN_CAM 连接器侧的 P/N 顺序与 AC 电容侧相反 (Δx=0.50mm) ⇒ "
     "是【把 AC 电容挪到连接器同侧】还是【成对换层绕开】? | 谁答: main | 不答的后果: CSI 10 条走不进「改布局」批 ⇒ "
     "落到「算法可解」⇒ 实测这类在 v44/v46/v47/v48 四条臂上都没布出来 ⇒ 45 归不了零 ⇒ G1 开不了 | "
     "建议默认值: 成对换层绕开 (不动器件、不动板框、风险最低) ⇒ 万一失败再退到「挪 AC 电容」 | 建议排期: BATCH-1 开工前"),
    ("iss322_s8_a1_batdet",
     "问法: BAT_DET 的终点是哪个点? (ISS-265 §6-1 登记的 A1 · 作业包 §3-S8 的 5 条死因之一) | "
     "谁答: 老板 (经 main 转达 · 技术选项由 hw-lead 给) | 不答的后果: BAT_DET (J_SOM_P1.38 ↔ C_DET_BAT.1 · "
     "直线 37.08mm) 布不了 ⇒ 45 归不了零 ⇒ G1 开不了 ⇒ 投不了板 | 建议默认值: 终点 = C_DET_BAT.1 "
     "(现状网表已这么连 · 只需确认不是要改成分压链中点) | 建议排期: BATCH-1 开工前"),
    ("iss322_s8_w1w2_esd",
     "问法: ESD 架构定了没? 定了才能定 D_ESD_USB_D / D_ESD_LIGHT 的封装与钉位 (W-1 / W-2) | 谁答: 老板 "
     "(ISS-307 已给候选集) | 不答的后果: LIGHT_5V (6.56mm) 与 USB_D 侧的钉位定不下来 ⇒ 那一趟开工后还得再改一次板 ⇒ "
     "板 md5 变第 2 次 = 2-4 周 + ¥4-8K | 建议默认值: ISS-307 候选集里封装最小的一个, 并把钉位写进 PCB_PART_POS | "
     "建议排期: BATCH-1 开工前"),
    ("iss322_s8_w4_qpg",
     "问法: PWR_GOOD 从 Q_PG.3 出来还是进去? (极性) | 谁答: 老板 | 不答的后果: Q_PG.3 是不是终点都没定 ⇒ "
     "PWR_GOOD (R_PU_PG.2 ↔ Q_PG.3 · 15.13mm) 布不了 ⇒ 45 归不了零 | 建议默认值: Q_PG.3 = 输出脚 "
     "(PWR_GOOD 从 Q_PG 出来到 R_PU_PG) | 建议排期: BATCH-1 开工前"),
    ("iss322_s8_d_led_g_pos",
     "问法: D_LED_G 落在板上的哪个点? (现状 LED_G_D 直线 93.49mm) | 谁答: mech-lead + 老板 "
     "(依赖 MECH 侧落位 · ISS-320 在飞) | 不答的后果: LED_G_D 93.49mm + LED_G 被 LED_B 掐 0.200mm ⇒ "
     "这 2 条布不了 ⇒ 45 归不了零 | 建议默认值: 把 D_LED_G 挪到 R_LED_G 同侧 (直线 < 20mm) | "
     "建议排期: BATCH-1 开工前 (与 MECH 落位同批)"),
]
for k, item in NEEDS:
    A += ["--add-need", "key=%s to=main since=2026-11-18 item=%s" % (k, q(item))]

A += ["--status",
      "phase=delivered progress_pct=100 health=green summary=" +
      q("ISS-322 已交卷: 45 条 unconnected 逐条清单 + 逐条死因登记 (几何不可布(布局级) 22 / 算法可解 18 / "
        "口径未定 5) + 高速腿几何可布性判定 = (a) 几何可布 (端点 88/88 可出 · 板框与层数不用改 · "
        "真瓶颈 = 段内 P/N 顺序翻转 17/47 处 · 修法 = 21 个 R_SEL_*/TP_DSI_* 挪到左上) + 逐条修法/BATCH-1-2-3/验收命令 "
        "+ 7 条待拍死结 (iss322_s8_*) + 证据分级. 零写板双证通过. gate_check rc=1 的唯一红项是 SW 域的 ISS-318 闸 "
        "(已逐字归因, 不属本单)")]

cmd = [sys.executable, FW, "--agent", "hw-lead"] + A
print("★ 调用: state/frag_write.py --agent hw-lead (★原子写·禁 open(p,w)★)")
print("★ 参数条数: %d" % len(A))
r = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True)
print(r.stdout)
if r.stderr:
    print("STDERR:", r.stderr[:3000])
sys.exit(r.returncode)
