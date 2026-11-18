#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-216 分片原子写脚本 (走 state/frag_write.py 的 update_fragment / atomic_write_yaml)
======================================================================
★**纪律**: 禁 open(p,"w") 直接写分片; 只动 mech-lead 自己的分片 (state/fragments/mech.yaml);
  不碰别人的分片。
★本单做的事:
  ① 对齐 ISS-213 已落的两条 claim 的 **note** (value 不变 —— 实测已是 buck 口径):
     - `mech_endpoint_surface_temp_caliber` (value = "buck: 83K/108C@0.50W; 60C判据⇒P_max=0.21W")
     - `mech_mech_budget_linear_0p8w_dead`   (value = "0.8W线性口径已作废(P10是buck)")
     + 同域第三条 `chg_board_dissipation` (value = "0.45-0.57W") 的 note
  ② 新增 claim `mech_charge_dissipation_caliber` (跨域只引这一条的对外取值)
  ③ 新增 answer (回 ISS-213 的 need `iss213_mech_mech_budget_charge_caliber_text`)
  ④ 新增 need (端件金属热路质量代价待 u8 定形) + artifact ×3 + status

用法:
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    python3 MECH/_frag_update_iss216.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

AGENT = "mech-lead"
TODAY = "2026-11-16"

# ---------------------------------------------------------------- claim notes
NOTE_ENDPOINT = (
    "★ISS-213 端件外表面温升**现行口径 = buck** (P10 网表有 SW/L_CHG/C_BST/PMID ⇒ 开关型 buck, "
    "耗散 = Pin−Pout+DCR = 0.45–0.57W), **不是** MECH_BUDGET §2.1 的 0.8W (那是线性稳压器公式 "
    "(5−4.2)×I ⇒ 对 buck 不适用, 本单判死该口径)。端件外表面 R_conv = 1/(10 W/m²K × 0.030×0.020 m²) "
    "= 166.67 K/W ⇒ P=0.50W ⇒ ΔT **83K ⇒ 表面 108°C** (0.8W 口径 ⇒ 133K ⇒ 158°C); "
    "★**60°C 判据 ⇒ P_max = (60−25)/166.67 = 0.21W** ⇒ 现耗散超 **2.4–2.7×** ⇒ **必须金属热路** "
    "(打印件沿臂 70mm R = 1944 K/W ⇒ 0.5W 打进去 +972K 不可能; 铝6063 同几何 R = 1.64 K/W ⇒ +0.82K)。"
    "验收: B1 批端件表面 (充电板正上方) 充电 1A 稳态 30min 实测 ≤60°C; 老板已拍'边戴边充不允许' ⇒ "
    "43°C 皮肤红线不适用, 但端件表面仍要过 60°C (烫手)。"
    "★**ISS-216 (2026-11-16) 已把文档侧口径改掉** (本句原文『本单未改 MECH_BUDGET 那一行 ⇒ 文字改动交 main 排期』"
    "已失效): `MECH/MECH_BUDGET.md` §2.1 + §2.3.1 现在写 **0.45–0.57 W (代表值 0.50 W)** + 公式 "
    "Pin−Pout+P_DCR + 器件 **BQ25896** ⇒ **文档 / 脚本 (`MECH/verify_budget.py` P_CHARGE=0.50) / 本门禁 "
    "三处同一个数**; ★本单独立复算三档 IIN = **0.460 / 0.516 / 0.574 W** (ISS-213 §5.3 表里的『0.91A 档 0.51W』"
    "与本单复算 0.5164 W 差 0.01 W = 取整差, 不是口径差)。[推算]"
)

NOTE_LINEAR_DEAD = (
    "★ISS-213 判定: `MECH/MECH_BUDGET.md` §2.1 的『**0.8 W @ 1A** (IC 自身耗散 = (5−4.2)V × 1A)』是"
    "**线性充电 IC** 的公式, 而 P10 充电板是**开关型 buck** ⇒ 该口径对现行方案**不适用 (判死)**; "
    "现行耗散口径 = 0.45–0.57W (Pin−Pout+DCR), 端件温升口径见 claim `mech_endpoint_surface_temp_caliber`。"
    "★**ISS-216 (2026-11-16) 已把这行文字改掉了** —— 本句原文『本单未改 MECH_BUDGET 那一行 ⇒ 文字改动交 main 排期』"
    "**已失效**: `MECH/MECH_BUDGET.md` §2.1 现在 = **0.45–0.57 W (代表值 0.50 W) · 耗散 = Pin − Pout + P_DCR · "
    "器件 BQ25896 (开关型 buck, 网表实读 SW/L_CHG/C_BST/PMID)**; §2.1 结构硬结论 / §2.3.1 充电峰值场景 / "
    "§2.4-E / §2.6-4 / §6 u7+u12 全部同步改完; `MECH/verify_budget.py` 的 `P_CHARGE` 常量 0.8 → **0.50** 并新增 "
    "§8 口径自检 10 组 + `--selftest` 10/10 反向用例 ⇒ **文档 / 脚本 / 机器门禁三处一致**。"
    "旧口径**只作为历史沿革留在文档里并标注『已判死』** (机器门禁 C7 专门盯这个: 旧标记只允许出现在写了"
    "『判死/作废』的行里, 不许当活口径)。[推算]"
)

NOTE_CHG_DISS = (
    "P10拓扑是开关型buck(网表有SW/L_CHG/C_BST/PMID)故耗散=Pin-Pout+DCR; MECH_BUDGET §2.1的0.8W是线性稳压器公式"
    "(5-4.2)xI; 端件表面温升口径随之改为83-108C; 打印件k=0.2 W/mK沿臂70mm导热阻约1944 K/W => 必须有金属导热路径。"
    "★**ISS-216 (2026-11-16) 已把 `MECH/MECH_BUDGET.md` §2.1 的 0.8W 线性口径改成本值 (0.45-0.57W, 代表值 0.50W)** "
    "⇒ 同域 claim `mech_mech_budget_linear_0p8w_dead` 的『文字待改』尾巴已收掉。"
    "★**本单独立复算三档 IIN** (公式 Pin−Pout+P_DCR; VBUS 5.0V · eta 0.90 · R_ILIM 390Ω · K_ILIM 320/355/390 A·Ω "
    "⇒ IIN 0.821/0.910/1.000 A · R_DCR 50mΩ · VBAT 3.70V) = **0.460 / 0.516 / 0.574 W** ⇒ 与已定区间 0.45-0.57W 吻合; "
    "**代表值 0.50 W = `MECH/check_demo_struct_truth.py` 门禁锚点 p_buck_w** ⇒ 文档/脚本/门禁三处同一个数。"
    "★**降级/待核 (查不到就写降级)**: 电感 DCR 取 `HW/CHARGE_BOARD_SPEC.md` 的上限 50mΩ (型号未选 ⇒ 实测只会更小 ⇒ "
    "耗散只会更小); 1A/3.7V 工况效率官网只给 2A/3A 档 (92.5%/90.5%) ⇒ 保守取 0.90。"
    "[实测 网表] + [官方 TI BQ25896 KILIM/效率] + [推算]"
)

NEW_CLAIM = {
    "key": "mech_charge_dissipation_caliber",
    "value": "buck 0.45-0.57W (代表值0.50W) · Pin−Pout+DCR · BQ25896",
    "note": (
        "★ISS-216 (2026-11-16) 结构侧**充电耗散口径统一**的对外取值 (跨域只引这一条): "
        "① 器件/拓扑 = **BQ25896 开关型 buck** ([实测] 网表 P10: SW/L_CHG/C_BST/PMID) ⇒ **耗散 = Pin − Pout + P_DCR**, "
        "**不是**线性稳压器的 (5−4.2)V×I ⇒ 旧口径 0.8 W **已判死** "
        "② **耗散 0.45-0.57 W, 代表值 0.50 W** (复算三档 IIN = 0.460/0.516/0.574 W) "
        "③ **皮肤侧 (镜腿, 主模型 k_eff 50.13 K/W, 基准 35°C)**: 充电 0.50 W ⇒ **60.0 °C** "
        "(区间 0.45/0.57 W ⇒ 57.5/63.6 °C); 充电+满载 1.72/2.02 W ⇒ **121.2/136.2 °C** ⇒ 仍超 43°C 红线 ⇒ "
        "**充电板必须挪出贴皮肤处 + 充电时摘下/禁 OD** "
        "④ **端件外表面 (ISS-213 §5.3, 只引用)**: R_conv 166.67 K/W ⇒ **ΔT 83 K ⇒ 108 °C**; 60°C 判据 ⇒ "
        "**P_max 0.21 W** ⇒ 超 2.4-2.7× ⇒ **必须金属热路** (打印件 1944 K/W ❌ / 铝 6063 1.641 K/W ✅ ⇒ "
        "**R_热路 ≤ 70 K/W**) "
        "⑤ **文档侧已改**: `MECH/MECH_BUDGET.md` §2.1/§2.3.1 = 0.45-0.57 W; `MECH/verify_budget.py` P_CHARGE=0.50 + "
        "§8 口径自检 10 组 + --selftest 10/10 ⇒ **文档/脚本/门禁三处一致**。"
        "★**§3 重量表 0 改动** (口径 ≠ 质量; 端件金属热路的质量代价待 u8 定形, 已登记 need 给 main, 不预扣不猜数)。"
        "[实测 网表] + [官方 TI K_ILIM/效率] + [推算]"
    ),
    "ref": "MECH/MECH_BUDGET.md §2.1/§2.3.1 + MECH/verify_budget.py §8 + "
           "MECH/HW_CROSS_REVIEW_TRIAGE.md §5.3/§5.4",
}

ANSWER_ISS213 = {
    "key": "iss213_mech_mech_budget_charge_caliber_text",
    "to": "main",
    "value": (
        "已改 (ISS-216, 2026-11-16 结构侧闭环): `MECH/MECH_BUDGET.md` §2.1 峰值充电行 = "
        "**0.45-0.57 W (代表值 0.50 W) · 耗散 = Pin − Pout + P_DCR · 器件 BQ25896 (开关型 buck)**; "
        "§2.1 结构硬结论 + §2.3.1 充电峰值场景 (皮肤侧 60.0 / 121.2 / 136.2 °C) + §2.3 结温行 + §2.4-E + §2.6-4 + "
        "§6 u7/u12 全部同步; `MECH/verify_budget.py` 的 `P_CHARGE` 0.8 → **0.50** + **新增 §8 口径自检 10 组 + "
        "`--selftest` 10/10 反向用例** ⇒ **文档 / 脚本 / 机器门禁三处一致**。"
        "★**判据阈值一个没松** (43°C 皮肤红线 / 60°C 端件判据 / cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / "
        "duct_v 6.00 / 板框四数) ⇒ 这是**口径统一 (公式换成板上真实拓扑的公式)**, 不是放宽判据。"
        "★**§3 重量表 0 改动** (口径≠质量), 端件金属热路的质量代价待 u8 (已另登记 need)。"
        "★**结构硬结论方向一条没变**: 充电板挪出贴皮肤处 / 充电时摘下禁 OD / 端件必须金属热路 —— "
        "端件 158 °C → **108.3 °C** (仍超 60 °C 判据 ⇒ 金属热路仍然必须)。"
    ),
    "ref": "HANDOFF/2026-11-16_mech-lead_ISS216_充电耗散口径统一.md + MECH/MECH_BUDGET.md §2.1/§2.3.1 + "
           "MECH/verify_budget.py (rc=0 / --selftest rc=0)",
}

NEED_METAL_MASS = {
    "key": "iss216_mech_endpoint_metal_path_mass_after_u8",
    "to": "main",
    "item": (
        "★ISS-216: 端件**金属热路** (ISS-213 的 THM-PATH 结论) 的**质量代价无法量化** —— 端件截面 u8 未定 ⇒ "
        "§3 的 W6 (充电板+Type-C+屏蔽罩 2-3 g) / W9 (镜框打印 9-14 g) 是否要加金属热桥重量, **待 u8 落定后回算**。"
        "★结构侧先落硬指标: **R_热路 ≤ 70 K/W** (60°C 端件判据下 0.50 W ⇒ ΔT ≤ 35 K); 铝 6063 同几何 "
        "1.641 K/W ✅ / 打印件 1944 K/W ❌ ⇒ **热路必须是铝/铜件**。"
        "★**本单 §3 逐件 0 改动, 不预扣、不猜数** ⇒ 请 main 排期 u8 (端件截面) 与打印包第三档试样。"
    ),
    "since": TODAY,
}

ARTIFACTS = [
    {
        "path": "MECH/MECH_BUDGET.md",
        "kind": "budget",
        "version": "v1.2",
        "updated_at": TODAY,
        "summary": (
            "空间预算 (镜脚侧+镜框侧累加) + 电池三档位 + 散热稳态热模型 (含充电峰值场景) + 重量核算 + 摄像头窗口/FOV + "
            "一拖二分光 + 彩虹纹专章 + P2S 工艺参数/打印vs量产; 第二轮新增 §1.4.5 / §2.3.1 / §4(d) / §5.4 / §5.5, "
            "并更正 3 处数值 (0.23W 皮肤侧 42→46.5°C, 重量合计 49-66→50.1-74.0g, 凸出俯角 1.8→0.7-0.8°/mm)。"
            "★**ISS-216 (2026-11-16) 改**: §2.1 峰值充电行 (**0.45-0.57 W, 代表 0.50 W, 公式 Pin−Pout+P_DCR, 器件 "
            "BQ25896**) + §2.1 结构硬结论 (皮肤侧 60.0 °C, 仍超 43°C 红线 17.0 °C) + §2.3 结温行 (0.50 W ⇒ Tj ≈ 62 °C) + "
            "§2.3.1 充电峰值场景表 (60.0 / 121.2 / 136.2 °C + 端件 108.3 °C / P_max 0.21 W) + §2.4-E + §2.6-4 + "
            "§3 (重量 **0 改动** + 金属热路质量待 u8) + §6 u7 (BQ25896 已定) / u12 (耗散口径已定) ⇒ "
            "**文档 / 脚本 / 机器门禁三处一致**; 判据阈值与板框四数一个没动。"
        ),
    },
    {
        "path": "MECH/verify_budget.py",
        "kind": "script",
        "version": "v1.1",
        "updated_at": TODAY,
        "summary": (
            "自证脚本: 一条命令复算 热模型/充电峰值/电池三档位/重量求和/摄像头几何/截面叠层/分光公差, 并自动与文档对表 "
            "(39/39 一致); 输入参数全部显式列在文件头部。"
            "★**ISS-216 (2026-11-16) 改**: `P_CHARGE` 0.8 → **0.50** (buck 口径 Pin−Pout+P_DCR) + §2 充电峰值场景按 buck "
            "重算 + **新增 §8 口径自检 10 组** (C1 口径标识=buck+BQ25896 · C2 常量在 0.45-0.57 区间 · C3 ≠线性 0.8 · "
            "C4 复算三档落在已定区间(含电感铜损) · C5 =门禁锚点 0.50W · C6/C7/C8 文档口径与旧标记清理 · "
            "C9 功率守恒 1.216/1.071 · C10 区间边界不许被放松) + **--selftest 10/10 反向用例** "
            "(写法照 check_demo_struct_truth.py); 数值对拍 39 → **53 项全绿**; rc: 绿=0 / 红=2。"
        ),
    },
    {
        "path": "HANDOFF/2026-11-16_mech-lead_ISS216_充电耗散口径统一.md",
        "kind": "note",
        "version": "v1.0",
        "updated_at": TODAY,
        "summary": (
            "ISS-216 交接单 (B1~B6 六块齐全): B1 结论 7 条 (含『这不是判据放宽』+『§3 重量 0 改动是结论不是漏改』+ "
            "『顺手抓到并修掉一个让门禁形同虚设的默认参数冻结 bug』) + **受影响结论逐条重列表 (方向不变 / 变 / "
            "需 main 重新裁决)** + B3 证据分级 ([实测]网表/[官方]TI/[推算]/[0数据]) + B4 接口取值 + B5 卡点 6 条 + "
            "B6 自证命令 + §5 边界 (0 次外发 · 实物 [实测]=0 条 · 降级方案 3 条)。"
        ),
    },
]

STATUS = {
    "phase": "P3",
    "progress_pct": 99,
    "health": "yellow",
    "summary": (
        "2026-11-16 ISS-216 (结构侧『充电耗散』热学口径统一): ★**同一个物理量, 文档 / 计算脚本 / 机器门禁三处现在是"
        "同一个数** —— `MECH/MECH_BUDGET.md` §2.1 的『线性充电 IC 0.8 W @ 1A (=(5−4.2)V×1A)』**判死**, 换成板上"
        "真实拓扑的算法: 器件 **BQ25896** (开关型 buck, [实测] 网表 P10: SW/L_CHG/C_BST/PMID) ⇒ 耗散 = "
        "**Pin − Pout + P_DCR = 0.45-0.57 W (代表值 0.50 W)**。★**本单独立复算三档 IIN = 0.460 / 0.516 / 0.574 W** "
        "(公式 Pin−Pout+DCR; VBUS 5.0V · η 0.90 [官方 TI: 充电效率 92.5%@2A/90.5%@3A] · R_ILIM 390Ω [实测网表] · "
        "K_ILIM 320/355/390 A·Ω [官方] ⇒ IIN 0.821/0.910/1.000 A · R_DCR 50mΩ · VBAT 3.70V) ⇒ 与 ISS-213/ISS-089 "
        "已定区间 0.45-0.57W 吻合; ★ISS-213 §5.3 表里的『0.91A 档 0.51W』与本单复算 0.5164W 差 **0.01 W = 取整差**, "
        "只报不改。★**受影响结论逐条重列**: 皮肤侧 75.1→**60.0 °C** (仍超 43°C 红线 17.0 °C) · 充电+满载 "
        "136.2/151.2→**121.2/136.2 °C** · 端件外表面 158→**108.3 °C** (60°C 判据 ⇒ P_max 0.21W ⇒ 超 2.38× ⇒ "
        "**必须金属热路** 方向不变) · §3 重量表 **0 改动** (口径≠质量; 端件金属热路质量代价待 u8, 已登记 need, "
        "不预扣不猜数; 结构侧先落 R_热路 ≤ 70 K/W 硬指标)。★**这不是判据放宽**: 43°C 皮肤红线 / 60°C 端件判据 / "
        "cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00 / 板框四数 全部逐字节未动 (门禁 G4/G4b/G5/G5b 实跑确认) "
        "—— 改的是**公式**不是阈值。★**新增机器门禁**: `MECH/verify_budget.py` 新增 §8 口径自检 10 组 + `--selftest` "
        "**10/10 反向用例** (写法照 check_demo_struct_truth.py), 数值对拍 39→**53 项全绿**, rc 绿=0/红=2; "
        "★顺手抓到并修掉一个**会让门禁形同虚设的真 bug** (`charge_dissipation(..., eta=CHG_ETA)` 在 def 时冻结全局值 ⇒ "
        "反向用例改不动 ⇒ 反向 5/8 抓不到) ⇒ 改成调用时解析后 10/10 全抓。★**边界**: 未改 HW/ 任何文件 · "
        "hw_cross_review_check.py · hinge_usb_check.py · service_port_check.py · display_biosafety_v2_check.py · "
        "check_demo_struct_truth.py (ISS-213 门禁, 只引用) · HW_CROSS_REVIEW_TRIAGE.md · state/issue_log.yaml · "
        "PROJECT_TRACKER.md §0 · state/outbox/ · 别人的分片 · MECH/print/ 打印包基线 (第三档试样仍未做) · "
        "板框四数 · 判据阈值; ★没碰 PCB 布线/布局/板框; ★零外发; ★本单 [实测] 实物 = 0 条。"
    ),
}


def main() -> int:
    def mutate(d: dict) -> None:
        claims = d.setdefault("interface_claims", [])
        by_key = {c.get("key"): c for c in claims}
        touched = []
        for key, note in (("mech_endpoint_surface_temp_caliber", NOTE_ENDPOINT),
                          ("mech_mech_budget_linear_0p8w_dead", NOTE_LINEAR_DEAD),
                          ("chg_board_dissipation", NOTE_CHG_DISS)):
            c = by_key.get(key)
            if c is None:
                raise SystemExit(f"[iss216] 分片里找不到 claim: {key}")
            c["note"] = note
            touched.append(key)
        # 新增 claim (幂等: 已存在就只刷新)
        if not any(c.get("key") == NEW_CLAIM["key"] for c in claims):
            claims.append(dict(NEW_CLAIM))
        # answer 回 ISS-213 的 need (幂等)
        answers = d.setdefault("answers", [])
        if not any(a.get("key") == ANSWER_ISS213["key"] for a in answers):
            answers.append(dict(ANSWER_ISS213))
        # need (幂等)
        needs = d.setdefault("needs_from", [])
        if not any(n.get("key") == NEED_METAL_MASS["key"] for n in needs):
            needs.append(dict(NEED_METAL_MASS))
        # artifacts (幂等: 按 path 覆盖)
        arts = d.setdefault("artifacts", [])
        for a in ARTIFACTS:
            for i, old in enumerate(arts):
                if old.get("path") == a["path"]:
                    arts[i] = dict(a)
                    break
            else:
                arts.append(dict(a))
        st = d.setdefault("status", {})
        st.update(STATUS)

    d = update_fragment(AGENT, mutate)
    print("[iss216] ✅ mech.yaml 已原子更新")
    for k in ("mech_endpoint_surface_temp_caliber", "mech_mech_budget_linear_0p8w_dead",
              "chg_board_dissipation", "mech_charge_dissipation_caliber"):
        print(f"   claim: {k}  (共 {len(d['interface_claims'])} 条)")
    print(f"   answers={len(d['answers'])} needs={len(d['needs_from'])} artifacts={len(d['artifacts'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
