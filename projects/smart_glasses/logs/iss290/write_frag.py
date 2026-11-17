#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-290 · 写自己的分片 (★只走 state/frag_write.py --agent mech-lead · 禁止 open(p,"w")★)"""
import shlex
import subprocess
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FW = ["python3", "state/frag_write.py", "--agent", "mech-lead"]


def spec(*pairs):
    """★把 (key, value) 对拼成 frag_write 认的 "key=value" 串 (值用 shlex.quote 包住 ⇒ 带空格不散)★"""
    return " ".join("%s=%s" % (k, shlex.quote(str(v))) for k, v in pairs)


CLAIM1 = (("key", "iss290_struct_crosscheck_established"),
          ("value", "★ISS-290 结构侧交叉核对【已立】: MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md (§1 坐标系声明 B160x100 + "
          "§2 MECH 保留区全集 15 条 (6 字段: id/source_iss/type/geometry/physical_reason/evidence) + "
          "§3 S6 的 20 个目标落位 × 保留区逐个核对表 + §4 座体类器件三方对照表 8 行 + "
          "§5 改板 vs 改选型代价对照 + 「必须在那一趟一起改」清单 E-1~E-6 (可直接进 HW/PCB/BOARD_ONEPASS_PREFLIGHT.md) + "
          "§6 corner_radius 3.0 vs 0.0 口径 + §7 机器块 JSON) ⇒ "
          "① S6 20 个目标落位 vs MECH 保留区: 冲突 0 条 (20/20 通过), 最小净距 4.6500 mm (两个 TP_DSI_* 到 SoM 保守包络), "
          "真实位移只有 R_SEL_D3_P (78.900,9.500)→(122.300,5.500); "
          "② SoM 承载区三口径自算 = 焊盘铜箔并集 X 15.100..68.900 × Y 7.610..54.390 (53.80×46.78) / 座体 F.Fab 并集 X 13.700..70.300 × Y 7.900..54.100 (56.60×46.20) / "
          "保守包络 X 13.650..70.350 × Y 7.610..54.390 (56.70×46.78); "
          "③ 座体三方对照: 装不进 2 个 (J_DEBUG/J_UART: BOM·网表 1.27mm 排针 vs 板读 land 0.50mm, Δ0.77) + 口径需澄清 3 个 (J_CHG 同名不同物 / J_SOM_P1 / J_SOM_P3 只有网络语义) + "
          "三方一致 3 个 (J_USB_C / J_SOM_P2 / J_SOM_P4); "
          "④ 「改 land 到 1.27」结构后果实算: 只动 J_DEBUG (必须清空区 X 142.0625..143.8375 → 140.9075..144.9925, 单边间隙 4.2125 → 3.0575 最坏 2.7575 仍 ≥CRIT 0.60, 开口左下角可放行宽 4.2125 → 3.0575), J_UART 零结构影响 (座体口径 2.5400 支配), 两条开口 X/Y 全不变, h 三档全过; "
          "⑤ corner_radius: 板读 R=0.00 vs params 3.0 ⇒ 单角贴角可用区 7.8400 → 0.2041 mm², 四角 −30.5436 mm², 板框面积 −7.7257 mm², 整板 −38.2693 mm² (偏保守不会撞但白丢面积)★"),
          ("note", "★ISS-290 (main 2026-11-17 14:3x 派单, cron 775d9893); 帧 id = B160x100 (与 HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES 逐字对齐); "
          "全部几何自己从板/BOM/网表重算 (logs/iss290/compute_iss290.py + 自写解析器 logs/iss290/pcbparse.py), 不抄任何交卷单的数; "
          "零写板/零落表/零改 HW//零改既有 MECH 判据脚本/零外发/零实物; 事实登记见交卷单"),
          ("ref", "HANDOFF/2026-11-17_mech-lead_ISS289_结构侧最后一道交叉核对.md"))

CLAIM2 = (("key", "iss290_struct_crosscheck_gate_established"),
          ("value", "★ISS-290 结构侧交叉核对【机器闸已立】: MECH/check_onepass_struct_crosscheck.py (★新建, 不改任何既有 MECH 判据脚本★) ⇒ "
          "N1 帧标签 (S6 20 个目标位逐个带帧标签且帧 = B160x100; 校准页 cal:S6_TARGETS + 规格页 §3 表 + 机器块 s6_rows 三处对账) / "
          "N2 SoM 承载区零冲突 (20 个落位 × 焊盘/座体/保守包络 三口径; 且规格页 SoM 三口径必须与板读一致, 防文档漂移) / "
          "N3 两条开口分别验 (检修口 / 调试口分开, 各按 h 三档 0.90/2.54/4.00 逐档验; 机器块 openings[] 必须恰好 2 条 ⇒ 合并即红) / "
          "N4 必清空区净距 ≥ CRIT (CRIT 取自既有 MECH 判据 MECH/check_board_frame_coords.py = 0.60, 不许新造; 规格页 consts.crit 与既有判据不等即红) / "
          "N5 座体三方对照表完整 (§4 表 8 个 J_* 行 × 4 个字段不许空, verdict 不许「待定」; 机器块 connectors[] 同样校验) / "
          "N6 受保护 5 件 md5 逐字节不变 (板 / .kicad_pro / 网表 / 脚表 / BOM); "
          "★主跑 rc=0 (N1~N6 全过) + --selftest rc=0 (8 条反向用例全抓到: ①挪进 SoM 承载区 ⇒ N2 红 ②挪进调试口开口 ⇒ N3 红 ③抽帧标签 ⇒ N1 红 ④合并两条开口 ⇒ N3 红 "
          "⑤把 CRIT 改小 ⇒ N4 红 ⑤b把 CRIT 改大 ⇒ N4 红 ⑥清空 §4 一个字段 ⇒ N5 红 ⑦篡改受保护板文件 ⇒ N6 红 ⑧真件跑完自检后 5 件 md5 仍逐字节不变)★"),
          ("note", "★只读 import MECH/check_board_frame_coords.py (阈值 CRIT / EDGE_KEEPOUT / OPEN_X / PROTECTED 零漂移); 板解析器自带 (自写 s-expr 解析, 一个字不抄既有交卷单); "
          "反向用例一律在沙盒副本上跑 (tmp/iss290_crosscheck_selftest), 真件一个字节不碰; 机器块改数必须同步改 MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md §2/§3/§4 表"),
          ("ref", "MECH/check_onepass_struct_crosscheck.py"))

ARTIFACTS = [
    (("path", "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md"), ("kind", "spec"),
     ("version", "v1.0"), ("updated_at", "2026-11-17"),
     ("summary", "★ISS-290 结构侧最后一道交叉核对规格页 (机器可读)★: §1 坐标系声明 (B160x100 · Edge.Cuts 中心线 0.000..160.000 × 0.000..100.000 · 8 铜层 · 186 封装 · F30A/P60x15 的数不可代入) + "
      "§2 MECH 保留区全集 15 条 (SoM 三口径 / 两条开口 + 开口 Y 参数式 / 两条必须清空区 / LED 两条可放行带 + 最近落位带 / 板边 0.80 / J_USB_C 座体+铜箔 / J_CHG 铜箔 / corner_radius 口径) + "
      "§3 S6 20 个目标落位 × 保留区逐个核对表 (ref/frame/target_x/target_y/footprint_extent/hit_zones/verdict/min_clearance_mm/evidence) + "
      "§4 座体类器件三方对照表 (J_DEBUG/J_UART/J_USB_C/J_CHG/J_SOM_P1..P4 × BOM·网表规格串 / 板读 land / 结构占位 / verdict / 改板连带影响) + "
      "§5 改板 vs 改选型代价对照 (路径 A 1.27 / B 2.54 / C 取消座体) + 「必须在那一趟一起改」清单 E-1~E-6 (标题/现状[实测]/改法/判据命令/归谁改) + "
      "§6 corner_radius 3.0 vs 0.0 两种口径差值 (单角 −7.6359 mm² · 四角 −30.5436 mm² · 整板 −38.2693 mm²) + §7 机器块 JSON★")),
    (("path", "MECH/check_onepass_struct_crosscheck.py"), ("kind", "script"),
     ("version", "v1.0"), ("updated_at", "2026-11-17"),
     ("summary", "★ISS-290 结构侧交叉核对机器闸 (新建)★: N1 帧标签 / N2 SoM 承载区零冲突 (含文档漂移对账) / N3 两条开口分别验 (h 三档逐档) / "
      "N4 必清空区净距 ≥ CRIT (CRIT 只读 import 既有判据) / N5 座体三方对照表四字段齐全 / N6 受保护 5 件 md5; 主跑 rc=0, --selftest rc=0 (8 条反向用例全抓到, 沙盒副本上跑, 真件一个字节不碰)")),
    (("path", "MECH/BOARD_ONEPASS_MECH_SYNC.md"), ("kind", "sync"),
     ("version", "iss290-append"), ("updated_at", "2026-11-17"),
     ("summary", "★ISS-278 那页的【追加式】订正 (老字一字不删不改: 前 38271 字节 md5 b0a975fa4876458328477851253fdefa 前后逐字节相同)★: "
      "新增 §9「S6 目标落位 × MECH 保留区 交叉核对」 (含给 hw-lead 的 S6 落位约束句 · 现役板坐标版) + "
      "新增 §10「座体类器件三方对照摘要 + 排针 pitch 1.27 vs 0.50 的结构后果」 (含「改 land 到 1.27」后两条开口 / 两条必须清空区 / 净距逐项实算 + E-1~E-6 清单); "
      "★ISS-278 的闸 MECH/check_onepass_mech_sync.py 追加后仍 rc=0 全绿★")),
]

NEED = (("key", "iss290_onpass_must_change_list_to_hw"),
        ("to", "main"),
        ("item", "★ISS-290 §5.6 那份「必须在那一趟一起改」清单 (E-1~E-6) ⇒ 请 main 转 hw-lead 并入 HW/PCB/BOARD_ONEPASS_PREFLIGHT.md; "
         "其中【E-1 排针 pitch 1.27 vs 0.50 (J_DEBUG/J_UART: BOM·网表写 1.27mm 排针, 板上 land 是 0.50mm, Δ0.77 ⇒ 实物排针落不进)】与"
         "【E-2 corner_radius 3.0 vs 0.0 (板读 R=0.00, params 写 3.0, 且 state/gen_pcb_netlist_board.py 的 add_outline() 根本不读这个参数)】"
         "★**两条都会改板 ⇒ 必须排在「板只改一次」之前定**★; 另 E-3 (J_CHG 同名不同物: 主板 2 脚 vs 网表 HINGE 10p) 与 E-4 (J_SOM_P1/P3 的 BOM 规格串只有网络语义) 会触落表, 须 main 批准后与那一趟一起做; "
         "E-5 (SoM 承载区三口径写进作业包) 与 E-6 (J_USB_C 缺一条结构边开口规格, 座体贴板边 Y=0) 零改板, 零改口径, 直接抄★"),
        ("since", "2026-11-17"))

STATUS = (("phase", "delivered"), ("progress_pct", "100"), ("health", "绿"),
          ("summary", "★ISS-290 结构侧最后一道交叉核对交付: 一份交叉核对表 (MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md: 保留区全集 15 条 + S6 20 个目标落位逐个核对 (冲突 0 条 · 最小净距 4.6500 mm) + "
           "座体三方对照 8 行 + 改板 vs 改选型代价 + E-1~E-6 清单 + corner_radius 口径) + 一道机器闸 (MECH/check_onepass_struct_crosscheck.py: N1~N6, 主跑 rc=0, --selftest rc=0 8 条反向用例全抓到) + "
           "ISS-278 那页追加式 §9/§10 (老字逐字节未动, 其闸仍 rc=0) ⇒ 把「板只改一次」那一趟在结构侧最后两个没人交叉验过的接口一次验完; "
           "零写板/零落表/零改 HW//零改既有 MECH 判据脚本/零改生成器/零外发/零实物; 待 main 转 hw-lead 的 E-1~E-6 清单 (E-1/E-2 会改板 ⇒ 必须排在「板只改一次」之前定)★"))


def run(args):
    r = subprocess.run(FW + args, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.stderr.strip():
        print("STDERR:", r.stderr.strip())
    if r.returncode != 0:
        sys.exit("frag_write 失败 rc=%d" % r.returncode)


run(["--add-claim", spec(*CLAIM1)])
run(["--add-claim", spec(*CLAIM2)])
for a in ARTIFACTS:
    run(["--add-artifact", spec(*a)])
run(["--add-need", spec(*NEED)])
run(["--status", spec(*STATUS)])
print("★分片写入完成 (只写 state/fragments/mech.yaml, 走 state/frag_write.py 原子写)★")
