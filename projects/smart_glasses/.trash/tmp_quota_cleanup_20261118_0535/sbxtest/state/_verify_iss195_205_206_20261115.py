#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main 独立验收签字 (2026-11-15 21:2x) —— ISS-195 / ISS-205 / ISS-206
=============================================================
★铁律: 干活的人不许自签 ⇒ verify_by=main, 本脚本只写 issue_log.yaml 的
  status / verify_result / verify_date / fixed_at / note 追加段
★不碰: PROJECT_TRACKER.md §0 / 任何分片 / 任何真源文件 (板/网表/脚表/原理图)
"""
import io
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

# ★每个 verify_result 都必须是本轮 main 自己跑出来的数字 (不是子 agent 自述)
VERIFY = {
    "ISS-195": (
        "pass · 2026-11-15 21:2x 项目总工独立复核 (★不采信自述★)\n"
        "★**达成**: `python3 HW/iss121_mic_magnet_check.py` **rc=0** ⇒ ★**当前落位 Y=12.00 => 孔壁净空 1.26mm (控制孔 S1)**★ "
        "⇒ 与 hw-lead 交卷单的数字**逐字一致** ⇒ 逐孔 P1 1.69 / S1 1.26 / P2 44.60 / S2 45.42mm · 三条判据 (不重叠>0 / 板规则 0.25 / ISS-092先例 1.00) 全 PASS ★**余量 +0.26mm**★\n"
        "★**Y 落位敏感度 (脚本 [F] 段)**: 全区间 [0.80..29.20] 最差 Y=14.19 => 0.55mm (P1) · 最优 Y=29.20 => 12.49mm · "
        "★**满足 ISS-092 先例 1.00mm 的可用 Y 区间 = [0.80..8.50] / [11.50..12.93] / [17.07..29.20]**★ ⇒ 板中线 Y=15.00 **不许取** (0.55 < 1.00)\n"
        "★**口径漂移闸 [E]**: PASS (pinset vs pcb60x30_check.py HOLES 逐坐标一致 4 孔)\n"
        "★**修前→修后**: 控制孔 3.01mm (作废 15mm 老口径) → **1.26mm** ⇒ Δ-1.75mm ★**这是真收窄, 不是美化**★\n"
        "★**FAIL 清单**: 仅 1 条 [已归属->ISS-105] M1 铰链端落板区边界 [0数据] ⇒ **本单零未归属 FAIL**\n"
        "★**脚本自己发现的老账 (★main 记下, 值得单独立项★)**: `HW/iss121_mic_magnet_check.json` 的 mtime (03:43:07) **早于** `.py` (03:43:43) ⇒ "
        "上一轮死会话改完脚本就挂了、没重跑 ⇒ **盘上是过期件** ★⇒ 本轮重跑后 json 65529B → 17450B, 差异全在采样密度导出 (worst/best 逐字未变) ⇒ **脚本无 bug, 是落盘不同源**★"
    ),
    "ISS-205": (
        "pass · 2026-11-15 21:2x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 问号行数 = 0** [实测]: `bash state/kicad.sh sch export bom -o /tmp/v_bom_verify.csv --fields Reference HW/PCB/demo_mainboard.kicad_sch` rc=0 ⇒ "
        "★**带 `?` 行数 = 0** (基线 186) ★ 数据行 **218** / 唯一位号 **218** / **重复位号 0**★\n"
        "★**② ERC**: `python3 state/check_sch_erc.py` rc=0 ⇒ **ERC 违规数 = 0**\n"
        "★**③ 脚数完整性**: `python3 state/check_sch_pinfull.py` rc=0 ⇒ 图上 584 脚 = 表里 584 脚 · **K=0** (universe=218) ⇒ ★**图=表 仍成立 (加 `_1` 后缀没破坏映射)**★\n"
        "★**④ 可加载**: `python3 state/check_sch_loadable.py` rc=0 ⇒ C1 括号平衡=0 / C2 KiCad 导出网表 rc=0 (378221 B) / C3 导出 PDF rc=0 (681533 B) ⇒ 全过\n"
        "★**⑤ 生产链**: `python3 state/chain_gate.py` rc=0 ⇒ **30/30 必备产物齐全** · ★**原理图源文件 12 个与 HW/PCB/ 逐字节 md5 一致**★ (★main 逐个 md5 对拍 11/11 OK★) · BOM 准出 位号 218 个全对 · DNP 46 个一致 · 伪器件 0 个\n"
        "★**⑥ 受保护文件 md5 全部未变**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**本单没碰板/没碰网表/没碰脚表**★\n"
        "★**⑦ 原理图本体 mtime 仍 2026-11-12 03:36** ⇒ ★**本单没重铸原理图**★ ⇒ 问号归零的真正来源 = ★**投产包被重新生成 (11-12 的 `_1` 后缀图导出 BOM 本来就干净, 投产包里躺着 11-11 17:25 的旧 BOM)**★ ⇒ ★**换句话说: 这是【清旧件】, 不是【改图】**★ ⇒ ★**下次任何人说\"原理图改了\"都先看 mtime, 别看交卷措辞**★\n"
        "★**残留 (不在本单范围, 已另开)**: G1 板位号仍旧名 (板上 156 个末字符是字母) / G2 板缺 R_CC1+R_CC2 封装 / G3 板比图少 32 器件 ⇒ **板侧属整链重出第 1 步** ⇒ 本单没碰板"
    ),
    "ISS-206": (
        "pass · 2026-11-15 21:2x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 结构侧 J_CHG pin map 收口**: `python3 MECH/hinge_usb_check.py` rc=0 ⇒ ★**收敛版 25.0mm (16p/20p/4p/10p) · [FAIL] 0 项**★ ⇒ ★**第 3 套 `8p@0.5` 口径已消灭**★ ⇒ 正文关键词/关键数字一致性检查全过\n"
        "★**② 检修口**: `python3 MECH/service_port_check.py` rc=0 ⇒ ★**54/54 项一致 · FAIL 0**★ ⇒ V PCB 36.00 / 余 +2.00 / 最坏 +1.40 · H PCB 4.40 / 余 +2.90\n"
        "★**③ 判据阈值一条没松** (★main 自己 grep 过脚本参数★): CRIT 0.60 · cav_v 38.00 · duct_v 6.00\n"
        "★**④ 残留 (★本单如实报出来, 不藏账★)**: 脚本仍报 1 条 [FIND] ⇒ ★**`CONN_USB` 声明 4p 但网表上是 `[]` (跨铰链 USB 链路在网表上没展开完整: D+/D−/GND/SHIELD)**★ ⇒ ★**这是真缺口, 归 hw-lead 侧网表 (ISS-086)**★ ⇒ 本单只报不改 (★mech-lead 没越界改网表, 纪律正确★)\n"
        "★**⑤ mech-lead 登记给 main 的 4 条 need (U-1~U-4) 仍未裁** ⇒ ★**这 4 条进 C 段决策页** ⇒ main 下一轮裁 (★U-3 = 分片 `mech_hinge_stack_fixed_mm` 仍 24.00 vs 文档 25.00, ★不许子 agent 改别人分片, 只能 main 改★)\n"
        "★**⑥ 受保护文件未动**: 板 `611b869e` / 网表 `c78f9912` 一字未动"
    ),
}

NOTE = (
    "\n★**【2026-11-15 21:2x 项目总工 (main) 独立验收签字】** ★\n"
    "★**本轮 = 同病第 14 次复发的收口 (★僵尸 fixing★)**: 兄弟 job 20:5x 清过一次僵尸 (三个会话 11-12 08:1x 全 status=failed ⇒ 交卷事件投给了已死会话 ⇒ 没人落账) ⇒ "
    "20:5x 重派 ⇒ ★**本轮三个会话 (hw-lead `3792d6c1` / sw-lead `22d71c7d` / mech-lead `686f2afe`) 21:05~21:08 全部 status=**done** 且交卷完整** ⇒ "
    "★**main 独立复核全部通过 (★不采信自述★) ⇒ 本单转 verified ⇒ 三个总工名额全部释放**★\n"
    "★**下一轮 A 段将恢复可派**: hw-lead 名额释放 ⇒ ISS-199 / ISS-204 自动可派 (★都是原理图/规格侧, 不是 PCB 布线类 ⇒ 不违反老板 10:07 口径★)\n"
)


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    changed = []
    for it in issues:
        iid = it.get("id")
        if iid not in VERIFY:
            continue
        assert it.get("status") == "fixing", "%s status=%s 非 fixing" % (iid, it.get("status"))
        assert it.get("verify_by") == "main", "%s verify_by 非 main" % iid
        it["status"] = "verified"
        it["verify_result"] = VERIFY[iid]
        it["verify_date"] = "2026-11-15 21:2x"
        it["fixed_at"] = "2026-11-15"
        it["note"] = (it.get("note") or "") + NOTE
        changed.append("%s → verified" % iid)
    assert len(changed) == 3, "只应改 3 条, 实改 %d" % len(changed)
    shutil.copy2(LOG, LOG + ".bak_20261115_2120_verify")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("\n".join(changed))


if __name__ == "__main__":
    main()
