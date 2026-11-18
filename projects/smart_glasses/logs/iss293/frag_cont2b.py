#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-293 cont2b · 分片原子写 (追加一条 claim: 占位符自检口径订正 + 真零读数)"""
import subprocess, sys, os, shlex
os.chdir("/home/yuewuya/.openclaw/workspace/projects/smart_glasses")

VALUE = (
    "★ISS-293 cont2b (2026-11-18 05:5x · sw-lead) 交卷单占位符自检口径订正: 本单交卷单 "
    "HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md 的 §B6.5 上一版 (2026-11-17 17:5x) 记录"
    "「占位符残留 = 0」是【不准确的】⇒ 原判据把 13 个占位符形态的字面量直接写进 grep -nE 的参数里 ⇒ "
    "该命令行自己命中自己 (自匹配) ⇒ 按项目口径 (旋转箭头图案 | 待+填两字 两型) 实跑上一版是 2 处, 不是 0 ⇒ "
    "★本版按 ISS-306 / ISS-300 同款做法改成 UTF-8 字节转义写 PAT ⇒ 本趟实跑 = 0 (真零, 不是假零) ⇒ "
    "交叉验 python3 state/check_report_placeholders.py <本交卷单> ⇒ 「✔ 无占位符 (★可发)」 rc=0 ⇒ "
    "两个独立口径都判 0 ⇒ ★任务书 §⑮ F1 要的「B0~B6 七块的占位符残留 grep = 0」= 0★ ⇒ "
    "★教训 (留给本项目所有交卷单): 自检命令里不许出现被检形态的字面量 ⇒ 一律用字节转义★"
)
NOTE = (
    "★[实测] 本趟自己实跑 (2026-11-18 05:5x) ⇒ 项目口径 PAT 用 printf 字节转义 (\\360\\237\\224\\204 = 旋转箭头图案, "
    "\\345\\276\\205\\345\\241\\253 = 待+填两字) ⇒ grep -cE \"$PAT\" 交卷单 ⇒ 原样输出 0; "
    "共享闸 state/check_report_placeholders.py 同一文件 ⇒ 原样输出「✔ 无占位符 (★可发)」 rc=0; "
    "★交卷单已按追加式订正 (§B6.5 内加【ISS-293 cont2 订正】行 + 新增 §C4-6 / §C4-7), 老字一个字节没删★ ⇒ "
    "★交卷后本单又重跑了一遍 8 条闸 (logs/iss293/cont2_final_gates2.log) ⇒ 8/8 全 rc=0 ⇒ 改交卷单没把别的闸带红★"
)
REF = (
    "HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md §B6.5 (订正行) + §C4-6 + §C4-7 · "
    "logs/iss293/cont2_final_gates2.log"
)
argv = [
    sys.executable, "state/frag_write.py", "--agent", "sw-lead",
    "--add-claim", "key=iss293_cont2_placeholder_selfcheck_correction_20261118_0555 value=%s note=%s ref=%s" % (
        shlex.quote(VALUE), shlex.quote(NOTE), shlex.quote(REF)),
]
p = subprocess.run(argv, capture_output=True, text=True)
print("frag_write rc=%d" % p.returncode)
if p.stdout.strip(): print("STDOUT:", p.stdout.strip()[-800:])
if p.stderr.strip(): print("STDERR:", p.stderr.strip()[-800:])
sys.exit(p.returncode)
