#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M-PRINT / M-FIT 诚实登记 (ISS-017 闭环单, 2026-11-01) —— mech-lead。

★ 铁律: **kind 绝不许写 "实测"** —— 0 件打印, 实物实测 = 0 数据。
  本脚本只把 **已交付的模型层证据** 写进去, 并保持 kind=推算 / value=未测。

写文件铁律: 原子写 (tmp + fsync + os.replace), 禁 open(p,"w") 覆盖。
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(PROJ, "state", "measurements.yaml")

M_PRINT_VALUE = "未测 (0件已打; Rev B 打印包已就绪待打印)"
M_PRINT_NOTE = (
    "★ **未实测, 诚实登记为 [推算]**: 实物 0 件已打 —— 本机物理上无法打印/量测 "
    "(打印机 192.168.1.68 与本机 192.168.2.4/24 跨网段不可达: ping 无响应 + TCP 990/8883/6000/4000 全 closed; "
    "无切片器 (Bambu Studio/OrcaSlicer/Cura 均无; /usr/bin/orca 是 GNOME 屏幕阅读器不是切片器); "
    "无卡尺/千分尺/塞尺; 无 USB 串口 (电子卡尺也接不上); gateway 主机=本机无第二台可借道) "
    "—— 证据 MECH/print/ENV_PROBE_20261101.md (2026-11-01 本人实测, 并更正了 10-25 旧记录里 '无外网' 的错误结论: pip 实测可通)。"
    "【本轮已交付 (模型层, 非实物)】① **Rev B 打印包可直接下片** (MECH/print/fit_coupon_revb.stl + "
    "temple_cage_revb.stl + frame_typec_coupon_revb.stl) —— Rev A 已过期 (板宽 12mm 口径, 不可再打); "
    "Rev B 按板宽 30mm/板长 60mm/RK3576/PIN-SET-2/ISS-092 检修口重做; "
    "② **自检 93/93 尺寸判据 + 38/38 STL↔规格逐点互验 (rc=0)** —— MECH/print/verify_pack_revb.py "
    "(改用 '解析模型精确求尺寸 + STL 逐点互验' 两段式, 绕开 Rev A 在 STL 上量尺寸的 4 个坑); "
    "③ **逐项测量清单 89 项有效待测** (MECH/print/MEASURE_CHECKLIST.md) —— 新增板宽 30 的 PCB 样板/PIN-SET-2/板厚三档/V余量梳、"
    "ISS-092 检修口壁 7 项 + 盖板 9 项、ISS-065 5 项对应实物项; "
    "④ 探测记录 (ENV_PROBE_20261101.md)。"
    "**升级为 [实测] 的唯一路径**: 打印 + 按 89 项清单量 + 回填 (needs_from boss: 打印与量测执行方, due 2026-11-08)。"
    "按纪律, 绝不拿推算/模型值冒充实测。"
)

M_FIT_VALUE = "镜脚侧: 通过但 V 链临界 (板宽30 ⇒ V余量 2.00/最坏1.40); 板厚1.22 档检修口净空 4.48 破 4.50 硬要求; 镜框侧: 未验"
M_FIT_EVIDENCE = (
    "MECH/fit_check_v3_30mm.py (板宽 30mm / RK3576 基线下的设计态干涉检查, rc=0; "
    "板层数 [0数据] ⇒ 板厚按 0.41/0.80/1.00/1.22 四档全算) + "
    "MECH/print/verify_pack_revb.py (打印包模型自检 93/93 + 38/38) + "
    "MECH/print/MEASURE_CHECKLIST.md (89 项实测清单) + MECH/print/ENV_PROBE_20261101.md"
)
M_FIT_NOTE = (
    "★ 这是 **设计态几何 + 公差栈计算**, 不是物理装配实测 ⇒ kind 诚实写 [推算], 阶段门 G2 不认 (符合预期)。"
    "【板宽 30 后的新账 (2026-11-01 翻案)】① **V 链是唯一被板宽打穿的链**: 板宽 30 + 走线槽 6 = 36.00 vs 净高 38.00 "
    "⇒ 余量 2.00 (最坏 1.40) ✅ 过判据 0.60, 但比板宽 15 时少 15.00; 板宽硬顶 = 38.00-6.00-0.60 = **31.40mm**。"
    "② **H/L 链一字不动**: H 控制段仍是电芯段 6.35 (余 0.95/最坏 0.65); L 需求 115.50 vs 130.00 (余 14.50)。"
    "③ ★**检修口净空随板厚变 (新发现)**: 净空 = 7.30-(0.80 皮肤壁+0.50 隔热垫+0.30 空气隙+板厚) ⇒ "
    "板厚 0.41/0.80/1.00 → 5.29/4.90/4.70 ✅, **1.22 (ISS-122 模型A 9层) → 4.48 ❌ 差 0.02 破 ISS-085 的 4.50 硬要求** "
    "⇒ ISS-092 C-5/P-1 口径要随板厚档位重算 (已登记 needs)。"
    "④ **电池空间/续航完全不变** (串行排布, 板宽只吃 PCB 段的 V) ⇒ 板宽 30 换到的是 PCB 面积, 不是电池。"
    "⑤ **重量代价**: PCB +1.332g (4层) / +1.665g (6层) + 金属骨架 +1.215g/侧 (V 覆盖 12→30 满宽) ⇒ 整机 +3.76~4.10g "
    "⇒ 48.9-74.0g → **52.7-78.1g**, 目标 30-40g 更远 [推算]。"
    "⑥ **镜框侧仍全未验** (走鹃Ⅱ 三维尺寸 u1 / 波导 2D 外形图 u4 / 端件截面 u8b / 摄像头 u5) ⇒ "
    "光机·波导干涉 **无法判定**; **波导彩虹纹指标 = [0数据]** (JBD 未选型 ⇒ 无 2D 图/无厂家指标, 已登记 needs)。"
    "★ **口径更正**: PROJECT_TRACKER §(1.43) 那句 '镜腿截面 15×7.3 → 30×7.3' 是自由文本表述, 与本域三条锁死尺寸链 "
    "(7.30×38.00×130.00) 不对应; 本单按 **板宽 = V 向** 算 (与 HW/pcb60x30_check.py 独立复算一致), 口径待 PM 确认。"
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
    hits = []
    for m in d.get("measurements") or []:
        if m.get("id") == "M-PRINT":
            m["value"] = M_PRINT_VALUE
            m["kind"] = "推算"          # ★ 绝不许写 "实测"
            m["when"] = "2026-11-01"
            m["evidence"] = (
                "MECH/print/fit_coupon_revb.stl + temple_cage_revb.stl + frame_typec_coupon_revb.stl (Rev B 打印包, 可直接下片) "
                "+ MECH/print/verify_pack_revb.py (自检 93/93 尺寸判据 + 38/38 STL↔规格逐点互验, rc=0) "
                "+ MECH/print/MEASURE_CHECKLIST.md (89 项有效待测) "
                "+ MECH/print/ENV_PROBE_20261101.md (本机无法打印/量测的实测探测记录) "
                "+ MECH/print/gen_print_pack_revb.py + print_model_revb.py (生成器 + 解析模型)"
            )
            m["note"] = M_PRINT_NOTE
            hits.append("M-PRINT")
        elif m.get("id") == "M-FIT":
            m["value"] = M_FIT_VALUE
            m["kind"] = "推算"          # ★ 绝不许写 "实测"
            m["when"] = "2026-11-01"
            m["evidence"] = M_FIT_EVIDENCE
            m["note"] = M_FIT_NOTE
            hits.append("M-FIT")
    assert set(hits) == {"M-PRINT", "M-FIT"}, f"没找到要更新的条目: {hits}"
    atomic_write(LOG, d)
    print(f"✅ measurements.yaml 已更新: {hits} (kind 保持 推算, 未冒充实测)")
    print("   M-PRINT value:", M_PRINT_VALUE)
    print("   M-FIT  value:", M_FIT_VALUE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
