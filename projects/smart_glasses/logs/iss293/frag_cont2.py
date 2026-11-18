#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-293 cont2 · 分片原子写 (走 state/frag_write.py 的 CLI 路径; 值用 shlex.quote 包好, 免空格炸裂)"""
import subprocess, sys, os, shlex

os.chdir("/home/yuewuya/.openclaw/workspace/projects/smart_glasses")

CLAIM_VALUE = (
    "★ISS-293 cont2 (2026-11-18 05:4x · sw-lead) 独立复跑: 新闸 rc=0 (29/29) · --selftest rc=0 (4/4) · "
    "timing_check 全量 rc=0 (SELFTEST 85/85) · --only F4_adc_det rc=0 · --only F4D_usb_vbus_det rc=0 · "
    "check_demo_panel_spec rc=0 · --selftest rc=0 (22/22) · merge rc=0 · gate_check rc=0 (Q1 18/18) · "
    "issue_check rc=0 ⇒ 10/10 全绿; ★F2 八条对账本机逐条 grep 复核全中 (BAT_DET 25 处 / 1.8V 33 处 / "
    "0.439 6 处 / 2.1%FS 21 处 / 37500 21 处 / 33.791 21 处 / 必装 52 处); "
    "活结论里残留 3.3V 口径旧数的行 = 0 (唯一命中 L141 = LDO EN 内部 500kΩ 下拉, 与 ADC 链无关, 闸的 "
    "ADC_CLAIM_RE 前置过滤排除, 非人工豁免)★"
)
CLAIM_NOTE = (
    "★[实测] 本趟自己实跑 (脚本 logs/iss293/cont2_verify.sh, 日志 logs/iss293/cont2_verify.log, "
    "2026-11-18 05:4x), 不抄 main 的读数。★★重要: 受保护 5 件的 md5 与 ISS-293 交卷时刻 (2026-11-17 18:00) "
    "相比, 网表/脚表/BOM 三件已被 ★★hw-lead 的 ISS-302 合法落表 (C_SYS / SYS_CHG 由 DNP 改必装 + "
    "note 追加式订正 + BOM 加 20µF) 于 2026-11-18 00:21:08 改掉★ (网表 37f62ac3→6aee500e / "
    "脚表 a4270120→9174309d / BOM 5d02bece→5b999399) ⇒ 与本单 (sw-lead) 无关, 本单一个字节都没碰这三件 ⇒ "
    "★板两件 md5 + mtime 仍逐字节不变 (611b869e / 3e504d2b / mtime 2026-11-06 07:07:17) ⇒ "
    "零写板双重自证仍成立★ ⇒ ★另: check_demo_panel_spec.py --selftest 在本机 /tmp (tmpfs 7.5G 已 80% 满) "
    "上会撞 [Disk quota exceeded] ⇒ 跑该自检必须带 TMPDIR 指向大盘, 否则 rc=1 是环境问题不是判据红 "
    "(本趟已带 TMPDIR ⇒ rc=0 · SELFTEST 22/22)★"
)
STATUS_SUMMARY = (
    "★ISS-293 (2026-11-17 派 · sw-lead · owner) 已交卷, 2026-11-18 05:4x cont2 独立复跑收口: "
    "① B1 文档 SW/SW_TIMING_REVIEW.md 的 ADC 段已按 ISS-291 现行闸追加式订正 "
    "(判决对象 VBUS_DET_D→BAT_DET pin38/SARADC_VIN5/1.8V 域 · 37500.0Ω · 33.791ms · 2.1%FS · "
    "LSB 0.439mV · 节点 1.575V ≤ 1.98V · 六判据全✔; 老口径那条红 = 假红已作废; BAT_DET 三颗已必装 "
    "⇒ §7-4 P0 解除; 新增 §14 ADC 现值卡 17 键) "
    "② B2 新闸 SW/tools/check_timing_review_adc_sync.py rc=0 (29/29) + --selftest rc=0 (4/4, 沙盒副本上做, 真件零改动) "
    "③ B3 回归 10 条本趟自己实跑全 rc=0 (含 gate_check Q1 18/18) "
    "④ 交卷单 HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md B0~B7 齐全 + 占位符残留 0 "
    "★★附注: 网表/脚表/BOM 三个 md5 已被 hw-lead 的 ISS-302 合法落表 (2026-11-18 00:21:08) 改掉, "
    "板两件 md5 + mtime 逐字节不变 ⇒ 零写板仍成立 (详见交卷单 §C4)★ "
    "★★要 main 拍板的只剩一件: M7-R6 要不要同步改 SW/SW_REQUIREMENTS.md "
    "(需求真源 = PM 域 ⇒ sw-lead 不自改, 已登记 need iss293_sw_m7r6_sync_to_main)★★"
)
STATUS_SUMMARY = STATUS_SUMMARY.replace('"', "'")  # status 正则用双引号包裹, 内部不能有双引号

argv = [
    sys.executable, "state/frag_write.py", "--agent", "sw-lead",
    "--add-claim",
    "key=iss293_cont2_indep_reverify_20261118_0545 value=%s note=%s ref=%s" % (
        shlex.quote(CLAIM_VALUE), shlex.quote(CLAIM_NOTE),
        shlex.quote("logs/iss293/cont2_verify.log + logs/iss293/verify_run.log + logs/iss293/verify_full.log + "
                    "logs/iss293/verify_state_gates.log + HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md §C4")
    ),
    "--status",
    'phase=delivered progress_pct=100 health=green summary="%s"' % STATUS_SUMMARY,
]
p = subprocess.run(argv, capture_output=True, text=True)
print("frag_write rc=%d" % p.returncode)
if p.stdout.strip():
    print("STDOUT:", p.stdout.strip()[-1500:])
if p.stderr.strip():
    print("STDERR:", p.stderr.strip()[-1500:])
sys.exit(p.returncode)
