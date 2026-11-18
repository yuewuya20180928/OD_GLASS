#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-291 反向用例证据跑器 (★只读盘面真源, 副本一律落在 /tmp★)

用途: 给交卷单产出「每条反向用例的【原样 rc】+【期望红组】vs【实际红组】」表。

★纪律:
  · 只读 `HW/netlist_v1.csv` 与 `SW/tools/timing_check.py`; 改坏的都是**副本** (/tmp)
  · 锚点类红 (网表 md5 / 三方对账) 在副本上**必然**红 ⇒ 单独归到「锚点噪声」, 不算目标红组
  · 本脚本不改盘面任何文件
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, "SW", "tools", "timing_check.py")
sys.path.insert(0, os.path.join(ROOT, "SW", "tools"))
import timing_check as T  # noqa: E402

NL = T.Netlist(T.DEFAULT_NETLIST)
TMP = tempfile.mkdtemp(prefix="iss291_rev_")

# ★锚点类红 (改副本必然变) ⇒ 不算目标红组 ★
ANCHOR_RE = re.compile(r"网表锚点")


def run_tool(script=TOOL, netlist=None):
    cmd = [sys.executable, script]
    if netlist:
        cmd += ["--netlist", netlist]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=300)
    fails = []
    for line in p.stdout.split("\n"):
        if line.startswith("  [FAIL]"):
            fails.append(line.replace("  [FAIL] ", "").strip())
    return p.returncode, fails, p.stdout, p.stderr


def report(tag, expect_desc, rc, fails):
    anchor = [f for f in fails if ANCHOR_RE.search(f)]
    real = [f for f in fails if not ANCHOR_RE.search(f)]
    print("=" * 100, flush=True)
    print("### %s" % tag, flush=True)
    print("  原样 rc        : %d" % rc, flush=True)
    print("  期望红组       : %s" % expect_desc, flush=True)
    print("  实际红组(目标) : %s" % (" || ".join(real) if real else "(无)"), flush=True)
    print("  锚点噪声(必然) : %d 条 (改副本 ⇒ md5 变了 ⇒ 锚点类必红)" % len(anchor), flush=True)
    for f in anchor:
        print("      - %s" % f[:110])
    return real


def mut_netlist(edits=None, dnp_targets=None, name="mut.csv"):
    dest = os.path.join(TMP, name)
    if dnp_targets:
        tset = set(dnp_targets)
        line_nos = [x["_line_no"] for x in NL.rows
                    if ((x.get("net") or ""), x.get("ref") or "") in tset]
        T.set_dnp_at_lines_copy(NL, dest, line_nos)
    else:
        T.mutated_copy(NL, dest, edits or [])
    return dest


def copy_tool_with(src_repl, dst_name):
    """★把脚本【副本】改坏 (只改常量/开关) ⇒ 跑副本 ⇒ 看它变不变红。

    ★**为什么副本必须落在 SW/tools/ 里**: 脚本用 `__file__` 推 `_PROJECT_ROOT`
      ⇒ 副本落在 /tmp 会找不到 HW/netlist_v1.csv ⇒ rc=2 (假失败) ⇒ ★必须同目录落★。
    ★跑完立刻删 (⇒ 盘面不残留临时文件)。
    """
    src = open(TOOL, encoding="utf-8").read()
    for old, new in src_repl:
        assert old in src, "替换目标没找到: %s" % old
        src = src.replace(old, new, 1)
    dst = os.path.join(ROOT, "SW", "tools", dst_name)
    open(dst, "w", encoding="utf-8").write(src)
    return dst


BASE_RC, BASE_FAILS, _, _ = run_tool()
print("### 基线 (一切如常)", flush=True)
print("  原样 rc        : %d" % BASE_RC, flush=True)
print("  红组           : %s" % (" || ".join(BASE_FAILS) if BASE_FAILS else "(无)"), flush=True)
print()

# ① 满量程改回 3.3
sc1 = copy_tool_with([('"V_DET_FS": 1.8,', '"V_DET_FS": 3.3,')],
                     "_iss291_tmp_fs33.py")
rc, fails, _, _ = run_tool(script=sc1)
os.remove(sc1)
report("① 把 V_DET_FS 改回 3.3 (老口径) ⇒ 满量程/口径同源判据变红",
       "满量程口径判据变红 (fs_caliber_ok: True→False)", rc, fails)

# ② 取链规则改回「元组第一条」
sc2 = copy_tool_with([('CHAIN_SELECT_MODE = "by_landing_pin"', 'CHAIN_SELECT_MODE = "tuple_order"')],
                     "_iss291_tmp_tuple.py")
rc, fails, _, _ = run_tool(script=sc2)
os.remove(sc2)
report("② 把取链规则改回「元组第一条」⇒ 判决对象判据变红",
       "判决对象判据变红 (object_ok: True→False, active_chain: BAT_DET→VBUS_DET_D)", rc, fails)

# ③ BAT_DET 三颗改回 DNP
net3 = mut_netlist(dnp_targets=[("BAT", "R_BAT_DET_1"), ("BAT_DET", "R_BAT_DET_2"),
                                ("BAT_DET", "C_DET_BAT"), ("GND", "C_DET_BAT")], name="dnp.csv")
rc, fails, _, _ = run_tool(netlist=net3)
report("③ 把 BAT_DET 三颗改回 DNP ⇒ 「ADC 输入悬空」判据变红",
       "「ADC 输入悬空」判据变红 (populated_ok: True→False, active_chain → fail-closed)", rc, fails)

# ④ BAT_DET 下臂 60k→100k
net4 = mut_netlist(edits=[("R_BAT_DET_2", "100k ±1%")], name="bot100k.csv")
rc, fails, _, _ = run_tool(netlist=net4)
report("④ 把 BAT_DET 下臂 60k→100k ⇒ @4.2V 节点 2.1V > 1.98V ⇒ 过压判据变红",
       "过压判据变红 (node_ok: True→False)", rc, fails)

# ⑥ VBUS_DET_D 10k/10k
net6 = mut_netlist(edits=[("R_VBUS_DET_D1", "10k ±1%"), ("R_VBUS_DET_D2", "10k ±1%")],
                   name="vbus10k.csv")
rc, fails, _, _ = run_tool(netlist=net6)
report("⑥ 把 VBUS_DET_D 两颗电阻改成 10k/10k ⇒ 数字链静态电流判据变红",
       "数字链静态电流判据变红 (static_current_ok: True→False)", rc, fails)

# ⑥b (加分) VBUS_DET_D 上臂 1M→10M
net6b = mut_netlist(edits=[("R_VBUS_DET_D1", "10M ±1%")], name="vbus10M.csv")
rc, fails, _, _ = run_tool(netlist=net6b)
report("⑥b 把 VBUS_DET_D 上臂 1M→10M ⇒ 数字链节点电平判据变红",
       "数字链节点电平判据变红 (level_ok: True→False)", rc, fails)

shutil.rmtree(TMP, ignore_errors=True)
print("=" * 100)
