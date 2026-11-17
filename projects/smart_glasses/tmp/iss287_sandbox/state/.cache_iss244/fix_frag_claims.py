#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-244 · 用 state/frag_write.py 的原子写路径, 就地订正 sw-lead 分片里被并发落表变陈旧的条目。

★为什么需要: 本单生成期间 (2026-11-16 15:45:45) 另一个落表批次改了 BOM,
  `C_REGN` 已落 ⇒ "23 - U_PWR_SW = 22 件待落" 这条口径当场变陈旧 ⇒
  merge.py 的 interface_claims 同 key 不同 value 冲突检测会把它判成 conflict
  ⇒ 必须就地订正, 不许留着冲突条目。

纪律: 只写 sw-lead 自己的分片; 只改自己本轮写的 key; 走 frag_write.update_fragment (原子写)。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from frag_write import update_fragment  # noqa: E402

NEW_CLAIM_VALUE = (
    "OPN 回填清单 = ISS-241 登记范围 22 件 (逐行带 ref+net 稳定锚点 + 网表/脚表/BOM 当刻行号, 行号会随落表漂移)"
    " + 要不要改 land + 谁拍 + 状态; 其中当前仍待落 21 件, 1 件 (C_REGN) 已被并发落表批次落掉 (2026-11-16 15:45:45 实测 BOM 已改)"
)
NEW_CLAIM_NOTE = (
    "★[实测] 2026-11-16 sw-lead · 收口页 HW/PART_SELECTION_GAPS_CLOSEOUT.md §4 · 型号与证据等级逐字取自 ISS-241 矩阵基准块 (不重挑),"
    " 锚点由生成器 state/.cache_iss244/build_closout.py 现算 ⇒ 与盘上真源同源。"
    "★**件数控两个机器派生源**: 登记范围 = ISS-241 矩阵基准块 expected_refs = 22 (登记事实) / 当前待落 = HW/BOM_v1.csv 实跑 待选型∩必装−越界件 = 21 (盘上事实);"
    " 两者差的一件是 C_REGN (已被并发落表落掉) ⇒ 清单保留该行并写 landed_note 落表证据。"
    "★交 main 排落表批次; ★落表注意: value 栏换型号+判据串 / opn 栏要含变体字母 / 主板件多数要重画 land (G-7) /"
    " 充电板 5 件封装占位待定归 ISS-243 L4 / R_SUPV_DIV1 与 DIV2 在 G-10 拍板前不建议填最终阻值"
)

NEW_ANSWER_VALUE = (
    "★ISS-244 已交卷 (零外发, 实物[实测]=0条): ① HW/PART_SELECTION_GAPS_CLOSEOUT.md (新建) = G-1~G-10 逐条自查补全"
    " (每条八栏: 缺口/归谁/本轮自查结果/证据等级/出处/降级方案/还差什么/状态) + 22 件 OPN 回填清单"
    " (登记范围 22 / 当前待落 21 / C_REGN 已被并发落表落掉); ② HW/check_part_selection_gaps.py (新建) = C0~C6 六条断言"
    " + --selftest 八条反向用例 8/8 全抓到 (每条自证: 变异真的落到副本 / 目标那条真的变红 / 其余仍绿);"
    " ③ 证据落盘 state/.cache_iss244/ (五份 Kingbright 原厂 PDF + TI TPS3808 / SLVAF82B / TPD2E2U06 / TPDxE05U06"
    " + AO3407A / DMP3098L + 数字化脚本 extract_ivif.py + 分压算式脚本 supv_divider_solve.py + 生成器 build_closout.py)。"
    "★四条重点缺口的结论: G-5 LED 1mA 档只有标称亮度的 4.8~7.2% (厂商曲线数字化, 四颗料互证);"
    " G-3+G-4 业界依据 = 差分对正负两根都要护 + 紧贴连接器, USB2.0 Cd<4pF 判据下双通道件达标 ⇒ 代价在焊盘与面积不在结电容;"
    " G-1 写法A 逻辑自洽 / 写法B 开机路径不通 ⇒ note 首句必须改 (连带需 D-S-G 引脚序);"
    " G-10 官方公式与三档候选阻值已算出, 但真正阻塞是 U_SUPV 与 U_DCDC_VIO 都 DNP ⇒ 建议两臂随 U_SUPV 一并 DNP。"
    "★留 main 与老板拍六项 (V-2 ESD 二选一 / V-3 / V-4 / G-1 源漏写法 / G-10 要不要恢复监督器 / LED 亮度档) ⇒ 本单一条未代拍;"
    " 请 main 落 verified 并把六项并进 DECISION_PENDING; ★state/issue_log.yaml 本单零写入 (verify 留给 main);"
    " ★HW/ 只新增两个文件 (收口页 + 门禁), 网表 / 脚表 / BOM / 板 / ISS-241 矩阵与门禁 一个字节未改"
)


def mutate(d):
    for c in d.get("interface_claims") or []:
        if c.get("key") == "iss244_opn_backfill_22_rows":
            c["value"] = NEW_CLAIM_VALUE
            c["note"] = NEW_CLAIM_NOTE
            c["ref"] = "HW/PART_SELECTION_GAPS_CLOSEOUT.md §4"
    for a in d.get("answers") or []:
        if a.get("key") == "iss244_gaps_closeout":
            a["value"] = NEW_ANSWER_VALUE
            a["ref"] = "HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md"


update_fragment("sw-lead", mutate)
print("[fix_frag_claims] sw-lead 分片已就地订正 (走 frag_write 原子写)")
