#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_close_issues_week_20261101.py —— 2026-11-01 周更新: issue_log.yaml 原子写

--------------------------------------------------------------------------------
本单把 4 条 owner==hw-lead 的 issue 从 open 推到 fixed (并落 fix_ref), 并给 ISS-121
补一条登记 note (前情已 verified, 本周只登记, 不改状态)。

★写文件铁律: 原子写 (tmp + fsync + os.replace), 禁止 open(p,"w") 覆盖 issue_log.yaml。
  照抄 state/_close_iss092.py 的写法 (MECH 那条 precedent)。

★只改 owner==hw-lead 的行; 别人的 issue 一行不动。

用法: python3 HW/_close_issues_week_20261101.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(PROJ, "state", "issue_log.yaml")

COMMON = ("★2026-11-01 hw-lead 周更新窗口 (项目总工派) 交卷并自推状态。")

# ---------------------------------------------------------------- fix_ref
FIX_REF = {
    "ISS-043": (
        "HW/CHARGE_STATUS_READBACK.md (ISS-043 主文档: 充电状态读取 = ①CHG_STAT (BQ25896 STAT 开漏 + R_PU_CHG_STAT 10k 上拉到 "
        "VDD_3V3_IO → J_CHG pin5 → SoC GPIO, 低=充电中/高=未充/1Hz闪=故障) + ②VBUS_DET (R_VBUS_DET_1/2 1M+1M 分压 + C_DET_VBUS 100nF → "
        "J_CHG pin7 → SoC USB_VBUS_DET ADC) 两条独立通路, 均有测试点 TP_CHG_STAT / TP_VBUS; 门禁判据必须 OR(...) 才 fail-safe + "
        "未知态 fail-closed; RC 复算 τ=50ms (建议改 100k/47k ⇒ 3.2ms); I2C 跨铰链 DNP ⇒ 不依赖寄存器) "
        "+ HW/netlist_v1.csv P2 行 159-173 / P7 行 355,382 / P9 行 437 (网表证据) "
        "+ HANDOFF/2026-11-01_hw-lead_周更新.md (B1-B6) "
        "+ state/fragments/hw.yaml (claims chg_status_readback / chg_status_gate_logic / chg_vbus_det_rc; answers emc_hw_interface_ask→main)"
    ),
    "ISS-079": (
        "HW/ONLINE_INTEL_2026-10-26.md (ISS-079 主文档: (a) 『采用 ARS45 的 AI 翻译眼镜』= 科大讯飞『讯飞AI眼镜』—— 2026-05-28 澳门 "
        "BEYOND Expo 2026 发布, 6-15 预售, 40g, 122 种语言实时翻译, 字幕投射镜片 + 扬声器播放, 唇动识别降噪, GlassClaw AI 助理; "
        "★其公开拆解 [0数据] (4 条检索路径), 同门可借鉴拆解 = 小米 AI 眼镜 (高通 AR1 + BES2700H + PMAR2130 + Kingston ePoP + 5 颗麦) / "
        "夸克 S1 (刚柔结合 + 石墨三层热路 + 0.7mm 刚性板 + 0.157Wh) / Rokid 乐奇 (IMX681 + 4 麦 + 210mAh); "
        "(b) 酷芯微港交所招股书 (媒体转述级): 2026-01-28 递表主板/华泰国际保荐, fabless, 智能可穿戴仅占 2024 营收 9.8%, "
        "前五大供应商 36.9/65.5/61.2%, 前五大客户 72.3/76.1/58.8% (最大客户 33.1%→34.1% = 深圳瑞可创新), 分销收入 1.71亿→4350万 (-1.09亿), "
        "2025 前 9 月扭亏净利 5082.5万; ★PHIP 直链 [0数据] + 5 条试过路径 + 人工拿法) "
        "+ HANDOFF/2026-11-01_hw-lead_周更新.md (B1-B6)"
    ),
    "ISS-105": (
        "HW/CHARGE_CURRENT_RECHECK_2026-11-01.md (ISS-105 收口主文档: ①分片过期值订正 pcb_outline 60x15→60x30mm / pcb_width_recommend "
        "15→30mm / pcb_mount_holes_xy Y 按 30mm 板宽重算 P1(8,15)P2(52,15)S1(8,10)S2(52,20) / battery_capacity_tier 重复旧值条目已删; "
        "②J_CHG『实物一对』备料口径写进 HW/BOM_v1.csv 第 12 行 memo + 网表 P1 注记 + claim j_chg_qty=2; "
        "③机械防呆已是 RFQ 硬判据 C-4 (反插=BAT_CHG 短接 GND); "
        "★④新增交叉评审命中: CHARGE_BOARD_SPEC §3.4 的 ICHG=IIN×(VBAT/VBUS)/η **方向反了** (buck 应为 ICHG=η·Vbus/Vbat·IIN=1.2162×IIN, "
        "旧式 0.8222× 是其倒数, 乘积 1.000000000 自校) ⇒ 390Ω 档实际 ICHG 1.00-1.22A / 单 pin 0.608A > 0.5A 触点天花板 ⇒ 判 FAIL, "
        "建议 R_ILIM 退 680Ω (单 pin 0.349A / 余量 1.43× / 铰链余量 2.15×)) "
        "+ HW/calc_chg_ichg.py (自证脚本, rc=0) + HW/calc_chg_ichg.json "
        "+ HW/hw_week_20261101_check.py (45/45 PASS) + HANDOFF/2026-11-01_hw-lead_周更新.md (B1-B6)"
    ),
    "ISS-111": (
        "HW/EVT_RELIABILITY_TEST_ITEMS.md (ISS-111 主文档: EVT 可靠性实测项清单 6 类 37 项 —— 跌落 9 (含 1 项前置『支架装法确认』R-D-00) / "
        "振动 5 / 弯折 6 / 热 5 / 焊点 6 / 连接器寿命 6; 每项含 测什么 / 怎么测(设备+工装+样品数+次数) / 量化判据 / 测不过回退哪一版 / 状态 "
        "五字段; 工况直接引用 RELIABILITY_DESIGN §2.2 不重写 (跌落 1.0m × 10 次/台 × 3 台 = 30 次 / 振动 5-200Hz PSD 0.005g²/Hz + 2g rms / "
        "弯折 100 次/天 → 5 年 182,500 次, R≥3.0mm / 500g 冲击); ★X-ray 抽样按**位置**计 (1 台样机只有 1 块主板 ⇒ 同板 3 位置 + 1 切片, "
        "空洞率≤25% 不变) ⇒ 闭合 mech-lead 的 mech_reltest_xray_sampling) "
        "+ HANDOFF/2026-11-01_hw-lead_ISS111_EVT可靠性实测项清单.md (B1-B6) "
        "+ HANDOFF/2026-11-01_hw-lead_周更新.md (B1-B6)"
    ),
}

CLOSE_NOTE = {
    "ISS-043": COMMON + "\n【本单做了什么】① 出 HW/CHARGE_STATUS_READBACK.md —— 回答 sw-lead IR-02『充电时必须禁 OD』所需的硬件前提:"
                         "**充电状态读取不是『未确认』, 硬件上本来就是双通路** (CHG_STAT + VBUS_DET, 都在网表里, 有位号/阻值/测试点); "
                         "② 给出 fail-safe 门禁判据 (OR + 未知态 fail-closed) 与时序预算 (CHG_STAT ≤100ms / VBUS_DET τ=50ms); "
                         "③ 复算并确认 sw-lead 9 项请求 P1-8 (1M+1M 源阻抗 500kΩ) 成立 ⇒ 给出 100k/47k 换料不换板的建议; "
                         "④ 分片原子写 (3 条新 claims + 1 条 answer 给 main 的 emc_hw_interface_ask + 2 条 needs); "
                         "⑤ 本脚本把 ISS-043 推到 fixed 并落 fix_ref。\n"
                         "★【结论】M-CHRG 门禁**硬件上可实现**, sw-lead 只需按 §3.1 的 OR 判据 + §3.3 的未知态 fail-closed 实现; "
                         "剩余风险是 SoC 脚号 (TBD-10, 随 11-01 换芯 RK3576 一次性重做) 与 STAT 极性的 datasheet 复核 (EVT 项 R-H-03)。",
    "ISS-079": COMMON + "\n【本单做了什么】① 出 HW/ONLINE_INTEL_2026-10-26.md —— (a) 锁定『采用 ARS45 的 AI 翻译眼镜』= **科大讯飞『讯飞AI眼镜』**"
                         "(2026-05-28 BEYOND Expo 2026 发布 / 40g / 122 语言 / 唇动识别降噪), 并如实标注其**公开拆解 [0数据]**; "
                         "(b) 检索酷芯微港交所招股书 (媒体转述级) 并逐条标来源 URL + 证据等级 + 原文引用; "
                         "(c) 试 5 条路径拿 PHIP 直链, 全部失败 ⇒ 如实标 [0数据] + 写人工拿法 + 登记 needs; "
                         "(d) 分片原子写 (artifact + 2 条 answer + 1 条 needs)。\n"
                         "★【最有价值的产出】招股书数据把『跳过酷芯微』从定性判断变成**有公开数据的判断**: fabless + 智能可穿戴仅占营收 9.8% "
                         "+ 供应商集中 61.2-65.5% + 客户集中 58.8-76.1% (最大客户是无人机厂) + 分销收入一年塌 1.09 亿 ⇒ ARS45 的产能与交期"
                         "在酷芯微内部不是第一优先级 ⇒ **支持 10-29 19:20 的拍板**。★另: 量产眼镜普遍用 eMMC/ePoP 而非 SPI-NOR ⇒ 与 sw-lead 的 "
                         "fw_boot_storage_bom 方向一致; 刚柔结合 + 石墨 + 0.7mm 板 ⇒ 印证我方骨架/石墨路线。",
    "ISS-105": COMMON + "\n【本单做了什么】① 出 HW/CHARGE_CURRENT_RECHECK_2026-11-01.md —— 把 ISS-105 的 4 个子项逐条闭环, 并**顺手命中一条"
                         "ISS-089 交叉评审 (mech-lead 判对, 我方独立确认)**: CHARGE_BOARD_SPEC §3.4 的 ICHG/IIN 换算方向反了 ⇒ "
                         "390Ω 档单 pin 实际 0.608A > 0.5A 触点天花板 ⇒ 390Ω 档判 FAIL, 建议 R_ILIM 退 680Ω (换料不换板); "
                         "② 出 HW/calc_chg_ichg.py (rc=0, 系数自校 + 5 档扫描 + 三条硬判据); "
                         "③ 分片原子写: claims 订正 6 条 (全部写清 旧值→新值) + 新增 8 条 + 删掉 battery_capacity_tier 的重复旧值条目; "
                         "④ HW/BOM_v1.csv 的 J_CHG 行补『实物一对, 备料按 2 只』+ R_ILIM 订正提示; "
                         "⑤ 本脚本把 ISS-105 推到 fixed 并落 fix_ref。\n"
                         "★【诚实边界】**网表与 BOM 生成器 (state/gen_netlist.py / gen_bom.py) 不在本单边界** ⇒ R_ILIM 退档、充电灯 board 列、"
                         "J_DEBUG Cortex-10 改造三条都走 needs 给项目总工排期; BOM 的备料口径写在 memo 列 (生成器强制 qty==1), "
                         "已登记 needs `iss105_bom_generator_qty_override` 要求加覆盖表, 否则下次重生成会覆盖掉这一行。",
    "ISS-111": COMMON + "\n【本单做了什么】① 出 HW/EVT_RELIABILITY_TEST_ITEMS.md —— 补上被三处悬空引用的文件 (RELIABILITY_ABSMAX_DERATING_V2.md "
                         "§5/§433/§481), 6 类 37 项, 每项五字段 (测什么/怎么测/量化判据/不过回退/状态), 工况**不重写**只引用 §2.2; "
                         "② 出 HANDOFF/2026-11-01_hw-lead_ISS111_EVT可靠性实测项清单.md (B1-B6); "
                         "③ 分片原子写 (artifact + answer 给 mech-lead 的 mech_reltest_xray_sampling + 新 claim evt_reliability_test_items / "
                         "evt_xray_sampling); ④ 本脚本把 ISS-111 推到 fixed 并落 fix_ref。\n"
                         "★【要点】① **X-ray 抽样口径按 1 台样机修正** (旧『抽检 3 块板』不成立 ⇒ 同板 3 位置 + 1 切片, 抽样按位置计); "
                         "② **跌落的总闸是支架装法不是板厚** (点接触 4 层 0.8mm ⇒ σ=115MPa 超许用 / 面接触 ⇒ 17MPa) ⇒ 测前必须先确认装法 (R-D-00); "
                         "③ 37 项全部标 [未验] (无样机), 5 项判据依赖 [0数据] (电芯规格书/绝对最大额定/跌落等级/FPC 应变/膨胀曲线) 并已登记依赖方; "
                         "④ 热项与 SW/EVT_TEMPLATE.md §8.2 的 THM-01~06 **合并执行**, 不另起第二套热测试。",
}

ISS121_NOTE = (COMMON + "\n【本周只做登记, 不改状态】ISS-121 前情已由 hw-lead 推到 verified (verify_by=main, "
               "fix_ref=HW/ISS121_MIC_MAGNET_POSITION.md, 项目总工 21:2x 亲核通过)。本周周更新里把它的产出与 6 条新 claims "
               "(mic_acoustic_hole_pos / mic_acoustic_hole_dia / mic_count / mic_magnetic_margin / mag_field_immunity_req / "
               "service_port_feature_clearance) 一并登记进分片, 便于老板在一屏内看到本周全部交付面。")


def atomic_write_yaml(path: str, data: dict) -> None:
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {i.get("id"): i for i in issues}

    changed = []
    for iid in ("ISS-043", "ISS-079", "ISS-105", "ISS-111"):
        it = by_id.get(iid)
        if it is None:
            print(f"⚠️ 找不到 {iid}", file=sys.stderr)
            continue
        if it.get("owner") != "hw-lead":
            print(f"⚠️ {iid} owner 不是 hw-lead, 跳过", file=sys.stderr)
            continue
        if it.get("status") in ("closed", "verified"):
            print(f"⚠️ {iid} 已是 {it.get('status')}, 不动", file=sys.stderr)
            continue
        changed.append(iid)
        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF[iid]
        it["verify_by"] = "main"          # ★自己修的必须别人验; 不能填 owner
        it["verify_result"] = None
        it["verify_date"] = None
        it["note"] = (it.get("note") or "") + "\n\n" + CLOSE_NOTE[iid]

    it121 = by_id.get("ISS-121")
    if it121 is not None and it121.get("owner") == "hw-lead":
        it121["note"] = (it121.get("note") or "") + "\n\n" + ISS121_NOTE
        changed.append("ISS-121(仅登记 note)")

    print(f"[issue_log] 改动 {len(changed)} 条: {changed}")
    for iid in ("ISS-043", "ISS-079", "ISS-105", "ISS-111"):
        it = by_id.get(iid)
        if it:
            print(f"  {iid}: status={it.get('status')} verify_by={it.get('verify_by')} "
                  f"fix_ref_len={len(it.get('fix_ref') or '')}")
    if dry:
        print("[dry-run] 未落盘")
        return 0
    atomic_write_yaml(LOG, log)
    print("[issue_log] ✅ 已原子写 (tmp + fsync + os.replace)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
