#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss314_frag_write.py —— ISS-314 分片写入驱动 (★只负责组装 argv, 落盘仍由 state/frag_write.py 原子做★)

★为什么用驱动而不是直接敲 CLI: ★本单的中文摘要里有引号 / 空格 / 星号 ⇒ 手敲 argv 极易被 shell 吃掉
  ⇒ 驱动用 subprocess 调 CLI (★与 state/frag_write.py 同一口径, 仍是它的原子写★) ★
★注意 (★CLI 内部用 shlex.split(spec)★): 每条 spec 的 summary 必须【自带双引号】,
  否则含空格的摘要会被 shlex 拆成多个 token ⇒ frag_write 直接报错退出 (★fail-loud, 好过静默丢★)
"""
import os
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLI = os.path.join(PROJ, "state", "frag_write.py")

A1_SUMMARY = (
    "ISS-314 交卷正文: S1 位号改名口径收口。"
    "§1 病灶 (作业包 §3-S1 板侧加 _1 与 §5 网表逐字节不变 自相矛盾 · 三侧 ref 口径现状实测) · "
    "§2 三选项代价矩阵 (①三侧同口径 / ②板侧不加_1 / ③加反查层 · 每格给: 额外要动的件 / 落表批次怎么排 / BOM 证据回填 / 失败长什么样) · "
    "§3 反查层补丁设计 (加在 board_pads() 而非 compare() · 口径单源 = gen_kicad_sch.py::kicad_ref() · 映射表不落盘 · 判红文案三行结构 · "
    "fail-closed F1~F5 · 7 条反向用例) · "
    "§4 沙盒 8 场景原始读数 · "
    "§5 BOM 兜底三选项 (甲映射 / 乙报警 / 丙改标注口径) + 同号异网 3 条改法 · "
    "§6 证据分级 + 建议默认值 (建议选① + 解封 check_pcb_nets.py 两行 · 不代拍)"
)

A2_SUMMARY = (
    "ISS-314 交卷单: B0~B6 标准验收块 + 附-A~附-D。"
    "必含沙盒 8 场景 C1 读数对照 (原始输出位置逐条给) + 给 main 的 1 条建议 (选①三侧同口径落表 · 理由三条) + 零写板双证。占位符 0"
)

A3_SUMMARY = (
    "ISS-314 沙盒 8 场景矩阵 (★脚本从原始输出自算 · 非手抄★): "
    "S0 现状 0/2/3/0 · "
    "S1 只改板侧 350/352/0/非法NC3 + C2红14 + C3红155 · "
    "S2 只改板侧+反查层 0/2/3/0 + C2红0 + C3红0 (反查命中155 · 未同步1) · "
    "S3 只改网表 与 S1 同型 · "
    "S4 三侧同口径 0/2/3/非法NC3 + C3红1 · "
    "S5 同 S4 · "
    "S6/S7 映射表被改坏 0/13/1/3 + 未同步4 ⇒ "
    "三条硬结论: 只改一侧必炸 / 改名与受保护判据禁改不可兼得 / 反查层是诊断层不掩盖真错"
)

A4_SUMMARY = (
    "ISS-314 取数日志目录 (19 个文件): 现状 C1/C2/C3 读数 + chain_gate 两条红 + 8 场景原始输出 + "
    "反查层补丁 diff + 两版沙盒判据副本 + 8 个沙盒脚本 + 场景矩阵生成器 + 交卷前核验 + 分片写回执。"
    "★沙盒只写 tmp/iss314_sandbox/ 与 tmp/iss314_tmp/ · 跑完即删 · 项目文件零改动★"
)

N1_ITEM = (
    "★S1 位号改名口径必须开工前拍★: "
    "作业包 §3-S1 (板侧 156 个封装位号加 _1) 与 §5 (网表/脚表/BOM 逐字节不变) 自相矛盾 ⇒ "
    "沙盒 8 场景实测: 只改一侧 ⇒ C1 缺失350/多余352/同号异网0/非法NC3 + C2红14 + C3红155; "
    "三侧同口径 ⇒ 0/2/3 但仍 非法NC3 + C3红1 (J_USB_C→J_USB_C_1 撞死 check_pcb_nets.py:265 的 NC 白名单) ⇒ "
    "★「位号改名」与「受保护判据脚本一个字不许改」不可兼得★。 "
    "请拍两件: ① 选 ①三侧同口径落表 (本单建议) 还是 ③板侧改名+判据反查层? "
    "② 能不能解封 state/check_pcb_nets.py 两行 (L265 NC 白名单 + L402 --selftest 目标 CONN_CAM · 改名后自检会抛 ValueError 崩掉)? "
    "不拍的后果: 那一趟跑完 C1 炸成 702 条 ⇒ 板 md5 第二次变 (2-4 周 + ¥4-8K) + "
    "BOM 9 行证据消失并换成假话「不在本 PCB」(看着还是绿的 · 没人拦) + "
    "CPL 与 BOM 位号分叉 (贴片那天才炸) + 判据自检自崩 (假绿风险回来)。 "
    "依据: HW/PCB/ONETRIP_S1_REF_RENAME_CALIBER.md §2/§3/§4/§6 + logs/iss314/12_scenario_matrix.txt"
)

ARTIFACTS = [
    'path=HW/PCB/ONETRIP_S1_REF_RENAME_CALIBER.md kind=analysis version=iss314-v1 summary="%s"' % A1_SUMMARY,
    'path=HANDOFF/2026-11-18_hw-lead_ISS314_S1位号改名口径收口.md kind=handoff version=iss314-v1 summary="%s"' % A2_SUMMARY,
    'path=logs/iss314/12_scenario_matrix.txt kind=data version=iss314-v1 summary="%s"' % A3_SUMMARY,
    'path=logs/iss314/ kind=data version=iss314-v1 summary="%s"' % A4_SUMMARY,
]

NEEDS = [
    'key=s1_ref_rename_caliber_20261118 to=main since=2026-11-18 item="%s"' % N1_ITEM,
]


def main():
    argv = [sys.executable, CLI, "--agent", "hw-lead"]
    for a in ARTIFACTS:
        argv += ["--add-artifact", a]
    for n in NEEDS:
        argv += ["--add-need", n]
    print("★ 调 frag_write.py (★原子写★), argv 长度 %d" % len(argv))
    r = subprocess.run(argv, cwd=PROJ)
    if r.returncode != 0:
        print("❌ frag_write rc=%d" % r.returncode)
        return r.returncode
    print("✅ frag_write rc=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
