#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-017 状态推进: fixing -> fixed (并落 fix_ref) —— mech-lead 交卷后自推。

★为什么要自己推 (不能只交卷): `state/advance.py` 的 in_flight 规则 = "同一 agent 名下只要有
  status==fixing 的 issue, 该 agent 本轮就不再派新活" ⇒ ISS-017 一直卡在 fixing, mech-lead 名下
  11 条 open 待办全被挡住。**交卷 ≠ 状态推进**, 必须一起做。

★写文件铁律: 原子写 (tmp + fsync + os.replace), 禁 open(p,"w") 覆盖 issue_log.yaml。

★verify_by 纪律: **不能填自己** (mech-lead) ⇒ 填 main (项目总工), 符合 issue_check.py 的 C3 验证分离。

★诚实边界 (写在 note 里, 不掩盖): 实物 0 件打印, M-PRINT/M-FIT 的 kind 仍为 推算,
  阶段门 G2 仍不通过 —— 本单走的是任务书明文允许的 "本环境无法实际打印/量测" 分支。
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

FIX_REF = (
    "MECH/print/fit_coupon_revb.stl + MECH/print/temple_cage_revb.stl + MECH/print/frame_typec_coupon_revb.stl "
    "(★Rev B 打印包, 可直接下片; Rev A 板宽12口径已过期不可再打) + "
    "MECH/print/gen_print_pack_revb.py (生成器, 纯numpy无外部依赖) + "
    "MECH/print/print_model_revb.py (★新增: 生成器同步记录的解析图元表 ⇒ 自检脚本精确求尺寸, 不从STL反推) + "
    "MECH/print/verify_pack_revb.py (★自检 rc=0: 尺寸判据 93/93 + STL↔规格逐点互验 38/38; "
    "方法论: 放弃'在STL上量尺寸'(绕向不一致/共面内部面/射线内起点/坐标混用 4个坑), 改'解析模型算尺寸+STL逐点互验'两段式) + "
    "MECH/print/MEASURE_CHECKLIST.md (逐项测量清单 89 项有效待测; Rev A 48 + Rev B 41: "
    "板宽30的PCB样板/PIN-SET-2/板厚三档/V余量梳 + ISS-092检修口壁7+盖板9 + ISS-065 5项) + "
    "MECH/print/ENV_PROBE_20261101.md (★新增: 环境探测记录, 本人实测, 并更正10-25旧记录'无外网'的错误——pip实测可通) + "
    "MECH/print/README.md (打印包说明 + Rev A作废声明) + "
    "MECH/fit_check_v3_30mm.py (★板宽30/RK3576基线下的装配干涉重算, rc=0) + "
    "HANDOFF/2026-11-01_mech-lead_ISS017_打印件实测与装配干涉.md (B1-B6 六块齐) + "
    "MECH/_apply_iss017_measurements.py (measurements.yaml 原子写) + "
    "MECH/_apply_iss017_frag.py (分片原子写, 走 state/frag_write.py) + "
    "state/fragments/mech.yaml (needs_from 新增4条 + interface_claims 更新7条) + "
    "state/measurements.yaml (M-PRINT/M-FIT 诚实登记, kind 保持 推算) + "
    "state/issue_log.yaml (本脚本, 原子写 tmp+fsync+os.replace)"
)

CLOSE_NOTE = (
    "★2026-11-01 21:4x mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main)。"
    "【本单走的是任务书明文允许的 '★如果本环境无法实际打印/量测' 分支】(上一轮 10-30 00:25 派活被 token 配额掐断, 交卷 0 产出; "
    "本轮探测只做一次、结果立刻落盘, 后面全部工作都在该记录之上做)。"
    "【交付 4 项 (分支要求)】① **可直接打印的模型文件**: **Rev B 打印包** (3 个 STL) —— "
    "★Rev A 已作废 (其 P 表锁在板宽 12mm/板长 50mm, 而基线是板宽 30/板长 60/RK3576/PIN-SET-2/ISS-092 检修口 ⇒ 旧的打出来是白打); "
    "自检 **尺寸判据 93/93 + STL↔规格逐点互验 38/38 (rc=0)**; "
    "② **逐项测量清单 89 项有效待测** (量哪里/用什么量/合格判据/记录格式/回填规则/阻塞表全有); "
    "③ **环境探测记录** (ENV_PROBE_20261101.md: 打印机 192.168.1.68 与本机 192.168.2.4/24 跨网段不可达 (ping 100% loss + TCP 990/8883/6000/4000 全 closed) / 无切片器 "
    "(/usr/bin/orca 是 GNOME 屏幕阅读器不是 OrcaSlicer) / 无卡尺千分尺塞尺 / 无 USB 串口 / gateway 主机=本机; "
    "★并更正 10-25 旧记录 '无外网' 的错误: pip 实测可通 ⇒ 10-25 那条结论作废); "
    "④ **needs_from 已登记** (waiting_on=boss, due 2026-11-08): 打印执行方 + 量具清单 (卡尺/塞尺/弹簧秤/电子秤), 写清要什么才能解。"
    "【★本单按新基线(板宽30/RK3576)重算的干涉结论 —— 2 条新发现】"
    "① **V 链是唯一被板宽打穿的链**: 板宽 30 (V向) + 走线槽 6 = 36.00 vs 净高 38.00 ⇒ **V 余量 17.00 → 2.00mm (最坏 1.40)** ✅ 仍过判据 0.60, "
    "但 **板宽硬顶 = 38.00-6.00-0.60 = 31.40mm**; 而 **H 链 (控制段仍电芯段 6.35, 余 0.95/最坏 0.65) 与 L 链 (115.50 vs 130.00, 余 14.50) 一字不动**; "
    "② ★**新发现: 板厚 1.22mm 会破 ISS-092 检修口的 4.50mm 硬要求** —— 净空 = 7.30-(0.80皮肤壁+0.50隔热垫+0.30空气隙+板厚) ⇒ "
    "板厚 0.41/0.80/1.00/1.22 → 净空 **5.29/4.90/4.70/4.48** ⇒ **1.22 (ISS-122 模型A 9层) 差 0.02 不通过** (ISS-092 C-5/P-1 口径要随板厚重算); "
    "③ 电池空间/续航 **完全不变** (串行排布, 板宽只吃 PCB 段的 V) ⇒ 板宽 30 换到的是 PCB 面积不是电池; "
    "④ 重量 PCB +1.332g(4层)/+1.665g(6层) + 骨架 +1.215g/侧 ⇒ 整机 **+3.76~4.10g** ⇒ 48.9-74.0g → **52.7-78.1g** (目标 30-40g 更远); "
    "⑤ **镜框侧全未验** (走鹃Ⅱ u1 / 波导 2D u4 / 端件截面 u8b / 摄像头 u5) ⇒ 光机·波导干涉无法判定; "
    "⑥ **波导彩虹纹指标 [0数据]** (JBD 未选型) ⇒ 已登记 needs iss017_waveguide_rainbow_metric (含结构侧能做/不能做的边界: "
    "应力型彩虹纹可控、膜层色差与亮度均匀性结构改不了)。"
    "【诚实边界 (不掩盖)】**实物 [实测] = 0 条**: 0 件打印、0 项实物量测 ⇒ measurements.yaml 的 M-PRINT/M-FIT "
    "**kind 保持 '推算'** (绝不拿模型值冒充实测), **阶段门 G2 仍不通过** —— 这是设计意图不是本单缺陷; "
    "板厚档位本身是 [0数据] (ISS-122 待 PCB 厂 DFM); PIN-SET-2 的 Y 坐标 [0数据] (板宽 15→30 后作废, 检具暂用 15mm 口径摆放, 只验孔径不验位置); "
    "板宽 30 = V 向这一口径按 BOARD_WIDTH_15MM.md §1.2 + HW/pcb60x30_check.py 独立复算一致 (已登记 needs 请 PM 确认)。"
    "【状态口径】本单 'fixed' = **可执行解已交付 + 解锁条件已登记**, 不等于实物已实测; "
    "阶段门 G2 的唯一卡点是 needs iss017_local_print_measure_unblock (打印+量测执行方, due 2026-11-08)。"
    "未联系任何供应商/原厂/JBD (JBD 相关全走 needs 经项目总工); 未改 HW/ SW/ PROJECT_TRACKER.md DECISIONS.md。"
)


def atomic_write(path, data):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=100)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main():
    with open(LOG, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    hit = 0
    for it in d.get("issues") or []:
        if it.get("id") != "ISS-017":
            continue
        assert it.get("owner") == "mech-lead", f"owner 不是我, 不该改: {it.get('owner')}"
        assert it.get("status") == "fixing", f"状态不是 fixing, 不该推: {it.get('status')}"
        it["status"] = "fixing"          # 先确保合法起点
        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF
        it["verify_by"] = "main"         # ★ 不能填自己 (mech-lead)
        it["verify_result"] = None
        it["verify_date"] = None
        it["note"] = CLOSE_NOTE
        it["need_keys"] = ["iss017_local_print_measure_unblock",
                           "iss017_waveguide_rainbow_metric",
                           "iss017_pcb_thickness_vs_service_port_clearance",
                           "iss017_board_width_direction_clarify"]
        hit += 1
    assert hit == 1, f"没找到 ISS-017 (命中 {hit} 条)"
    atomic_write(LOG, d)
    print("✅ ISS-017: fixing → fixed, fix_ref 已落, verify_by=main")
    print(f"   fix_ref 长度 {len(FIX_REF)} 字符")
    return 0


if __name__ == "__main__":
    sys.exit(main())
