#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-284 · 写 sw.yaml 分片 (★必须走 state/frag_write.py 的原子写★)。

★每个 --add-* 的规格 = 【一个 argv 元素】, 里面 key="value" 用双引号包住 (★frag_write 内部走 shlex.split★)
★用 subprocess 传 argv (不走 shell) ⇒ 免掉 ★/引号/空格 的转义坑★
"""
import subprocess
import sys

PY = sys.executable
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

SPECS = []


def spec(flag, **kv):
    parts = []
    for k, v in kv.items():
        v = str(v).replace('"', "'")
        parts.append('%s="%s"' % (k, v))
    SPECS.append([flag, " ".join(parts)])


# ---- 1 交付物 (artifact) ----
spec("--add-artifact",
     path="HANDOFF/2026-11-17_sw-lead_ISS284_hard_protected合法改板机制.md",
     kind="handoff", version="v1.0", updated_at="2026-11-17",
     summary="★ISS-284 (2026-11-17, sw-lead) 交卷单 (B1~B6 六块齐全) ★P10 = 方案 ② (老板 2026-11-17 09:49 拍板「按照你的建议执行」) ⇒ "
             "SW 侧 hard_protected (板 / .kicad_pro) 的【合法改板】机制落地: 一条合法改板 = 【单号 + 文件名 + 改前 md5 + 改后 md5】四件捆在锚点【一个原子映射】里 "
             "+ 同一份四项必须在落表台账 HW/SCHEMATIC_LANDING_V1_LANDED.md 的同一行里查到; 判据方向一个字没变 (盘上 ≠ 链头 ⇒ 红); fail-closed 三条一条没动 "
             "(链头不唯一 / 链断 / 链头无单号 ⇒ 红); 另加两条 (保护基线必须留在链尾 / 同组两件必须成对覆盖) ★反向用例 REV-16~REV-21 六条 (含 1 条正向) 全抓到 "
             "⇒ check_demo_panel_spec.py --selftest 22/22 (原 16 条一条没删) ★零写板 · 零落表 · 落表台账零写入 · 不替老板拍板★")

spec("--add-artifact",
     path="SW/SW_MD5_BASELINE_LEDGER.md",
     kind="ledger", version="v1.4", updated_at="2026-11-17",
     summary="★ISS-284 (2026-11-17, sw-lead) 纯追加: §1 锚点块 hard_protected[] 两条各加一个【reboard】原子字段 (★null = 还没发生过合法改板★ · "
             "★md5 字段语义改为【保护基线】且永远不许改★) + §1 新增《硬保护两件的合法改板机制 (P10 = 方案 ②)》十条 (含落表台账那一行的接口格式) + "
             "§3 追加 R-12 留痕行 (下一个空号, R-01~R-11 一个字没删) ⇒ ★网表/脚表那条已跑通的链头逻辑 (ISS-275) 一个字没动 (读数前后逐字相同, IDENTICAL: True)★")

spec("--add-artifact",
     path="SW/tools/check_demo_panel_spec.py",
     kind="gate", version="v1.1", updated_at="2026-11-17",
     summary="★ISS-284: R6 硬保护段升级成【合法改板机制】★ —— 新增 check_r6_hard_protected() + sw_ledger_cover_rows() / sw_ledger_change_rows() / "
             "sw_ledger_change_state() / m12() 四个 helper (★自己写, 不 import MECH★); 硬保护件现在走【落表台账链头】判决 (与网表/脚表同源) ⇒ "
             "盘上 ≠ 链头 ⇒ 红 (判据方向没变) ★网表/脚表分支的读数一字未动 (IDENTICAL: True)★; --selftest 由 16 条增到 22 条 (REV-16~REV-21 六条新增) ⇒ 22/22 rc=0")

spec("--add-artifact",
     path="logs/iss284/",
     kind="log", version="v1.0", updated_at="2026-11-17",
     summary="★ISS-284 本机实跑原始日志: gates_demo_panel.log (rc=0 + selftest 22/22) · gates_timing_check.log (★rc=1 · 68/71 —— 三条红全是 09:58 上游落表造成的 "
             "★与本单无关, A/B 实测证明★) · gates_step1.log (rc=0 · 8/8) · gates_onepass_preflight.log (★rc=1 · 上游落表造成★) · gates_onepass_sw_sync.log (★rc=1 · 上游落表造成★) · "
             "netlist_reading_before_after.log (IDENTICAL: True) · ab_timing_check_pre_ledger.log (★A/B: 换回改动前的台账仍 68/71 ⇒ 证明不是本单弄坏的★) · probe_netlist_reading.py (对比工具)★")

# ---- 2 机制声明 (claim) ----
spec("--add-claim",
     key="sw_hard_protected_legal_reboard_mechanism",
     value="★P10 = 方案 ② (★老板 2026-11-17 09:49 拍板「按照你的建议执行」★): 一条合法改板 = 【单号 by + 文件名 file + 改前 md5 prev_md5 + 改后 md5 md5】"
           "四件捆在锚点 hard_protected[].reboard【一个原子映射】里 + 同一份四项必须在落表台账 HW/SCHEMATIC_LANDING_V1_LANDED.md 的同一行里查到★",
     note="★ISS-284·2026-11-17·sw-lead·零写板零落表★ ① 【一个字段两个值】: 四项捆一个原子映射 (★不许拆成两个可各自独立编辑的字段 —— 那是 ISS-279 点名的缝★) "
          "② 【判据方向没变】: 盘上 ≠ 台账链头 ⇒ 红 (★合法改板只让链头前移, 不是把判据放松★) ③ 【fail-closed 三条一条没动】: 链头不唯一 / 链断 / 链头无单号 ⇒ 红 "
          "④ 【基线不许前移】: 锚点 md5 = 保护基线, 必须留在台账链尾且在台账里查得到 ⇒ 只改 md5 凑绿 = 红 ⑤ 【同组成对】: 板 + .kicad_pro 必须被同一单号覆盖 "
          "⇒ 只来一条记录 = 红 ⑥ 【落表台账那一行的格式】: 「单号 | 文件名 | 改前 md5 | 改后 md5」四项同行 (★一行两件两值 = 歧义行 = 不算变更行★) "
          "⑦ 【信任边界】: 落表台账 = append-only; 本闸保证的是「锚点自己不能说了算」 (★「悄悄换台账」不在本闸能力范围内★) "
          "⑧ 闸 = SW/tools/check_demo_panel_spec.py 的 check_r6_hard_protected(); 反向用例 REV-16~REV-21 六条 (含 1 条正向) ⇒ selftest 22/22 "
          "⑨ 【真落那一行留给「出板那一趟」的 main】 (★本单落表台账零写入★)★")

# ---- 3 回答旧 need (老板已拍板) ----
spec("--add-answer",
     key="sw_hard_protected_reanchor_options", to="main",
     value="★已闭合 (ISS-284, sw-lead, 2026-11-17)★ 老板 2026-11-17 09:49 拍板「按照你的建议执行」⇒ P10 = 方案 ② ⇒ SW 侧机制已落地: "
           "① 锚点 SW/SW_MD5_BASELINE_LEDGER.md §1 hard_protected[] 每条加一个 reboard 原子映射 (★单号 + 文件名 + 改前 md5 + 改后 md5 四件捆一起★; "
           "md5 字段语义改为【保护基线】且永远不许改★) ② 闸 SW/tools/check_demo_panel_spec.py 的 R6 硬保护段改成走【落表台账链头】判决 (与网表/脚表同源) "
           "⇒ 盘上 ≠ 链头 ⇒ 红 (★判据方向一个字没变★) ③ fail-closed 三条 (链头不唯一 / 链断 / 链头无单号) 一条没动 ④ 另加两条: 基线必须留在链尾 / "
           "同组两件必须成对覆盖 ⇒ 只改板不动 .kicad_pro = 红 ⑤ 落表台账那一行的接口格式 = 「单号 | 文件名 | 改前 md5 | 改后 md5」四项同行 "
           "⇒ ★真落那一行留给「出板那一趟」的 main (★本单落表台账零写入★)★ ⇒ 反向用例 REV-16~REV-21 六条 (含 1 条正向) 全抓到 ⇒ selftest 22/22 "
           "(★原 16 条一条没删★) ⇒ 板 / .kicad_pro / 网表 / 脚表 / BOM 五件逐字节不变 ⇒ 零写板 · 零落表 · 不替老板拍板★",
     ref="HANDOFF/2026-11-17_sw-lead_ISS284_hard_protected合法改板机制.md ; SW/SW_MD5_BASELINE_LEDGER.md §1 + §3 R-12 ; SW/tools/check_demo_panel_spec.py check_r6_hard_protected()")

# ---- 4 给 main 的 need: 出板那一趟要落的那一行 ----
spec("--add-need",
     key="sw_legal_reboard_landing_row_on_board_trip", to="main", since="2026-11-17",
     item="★【出板那一趟】合法改板那一行必须落在落表台账里★ —— SW 侧 R6 硬保护段现在按【落表台账链头】判决 ⇒ 出板那一趟请在 "
          "HW/SCHEMATIC_LANDING_V1_LANDED.md 里写两行 (★格式: 单号 | 文件名 | 改前 md5 | 改后 md5 四项同行★): "
          "① 板那一行 = 「出板单号 | HW/PCB/demo_mainboard.kicad_pcb | 611b869e13518c3c023fb178f91a0075 | <新板 md5>」 "
          "② .kicad_pro 那一行 = 「出板单号 | HW/PCB/demo_mainboard.kicad_pro | 3e504d2be83152e337949723e909be1b | <新 .kicad_pro md5>」 "
          "(★若 .kicad_pro 真的逐字节没变, 改前=改后也要写一行「否 (逐字节不变)」★ ⇒ ★两件必须成对, 只来一条 = 红★) "
          "★同时 SW 侧锚点 SW/SW_MD5_BASELINE_LEDGER.md §1 的 hard_protected[].reboard 要填上同一单号的四项 (★四件捆一个原子映射, 不许只填 md5★) "
          "⇒ 填完 SW 侧 R6 即绿 (★判据方向没变: 盘上 ≠ 链头照样红★)★ ⇒ ★本单 (ISS-284) 只出机制与闸, 落表台账一个字节没碰 (★真落那一行归出板那一趟★)★")

# ---- 跑 ----
cmd = [PY, "state/frag_write.py", "--agent", "sw-lead"]
for flag, s in SPECS:
    cmd += [flag, s]
print(">>> frag_write.py --agent sw-lead (%d 条增量)" % len(SPECS))
rc = subprocess.call(cmd, cwd=ROOT)
print("frag_write rc=%d" % rc)
sys.exit(rc)
