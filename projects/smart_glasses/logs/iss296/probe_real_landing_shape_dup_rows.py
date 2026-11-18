#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-296 cont3 · 探针: 「合法改板」通道对【main 真实落表形状】是否成立

★**为什么要有这个探针** ★
  ISS-302 (2026-11-18 00:22 合法落表) 在落表台账里写了【两张表】:
    ① §16.2 「新旧 md5 前后对照」链头行  (L1451)
    ② §19.3 「逐条登记」行               (L1466)
  ⇒ ★**同一个 md5 值 (链头 6aee500e…) 在台账里出现了两次** ★
  ⇒ 而 ISS-296 交卷时的正向对照 ⑰ 只覆盖了【单行】形状 ⇒ ★**真实落表形状没被验过** ★
  ⇒ 本探针在【沙盒副本】上补验三件事 (★真件一个字节不许碰★):
    A: 合法改板一次 + 【§16.2 行 + §19.3 行 两张表都写】⇒ C4 必须【绿】(★这才是 ISS-296 的承诺★)
    B: 同样两张表, 但两行的【改前 md5 互相不一致】⇒ C4 必须【红】(★fail-closed 不得被放松★)
    C: 台账里【同一个链头 md5 出现在几行】⇒ 定位 ⑩c 反向用例自检变红的根因

★**判据方向不变**: 本探针只【读】闸的函数, 不改闸本体任何一行 ★
"""
import importlib.util
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GATE = os.path.join(ROOT, "MECH", "check_board_frame_coords.py")

spec = importlib.util.spec_from_file_location("cf", GATE)
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)

BOARD_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
PRO_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pro")
LEDGER = cf.LEDGER_CANON
BASE = "611b869e1351"          # 板基线 (闸里写死的那个)
PRO_BASE = "3e504d2be831"

errs = []


def sb_read(sb):
    with open(os.path.join(sb, LEDGER), encoding="utf-8") as f:
        return f.read()


def sb_write(sb, text):
    with open(os.path.join(sb, LEDGER), "w", encoding="utf-8") as f:
        f.write(text)


def board_append_byte(sb):
    p = os.path.join(sb, BOARD_REL)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
    return cf.md5_of(p)


def c4_reason(res):
    for e in res["C4"]["errs"]:
        if "合法改板" in e:
            return e
    return res["C4"]["errs"][0] if res["C4"]["errs"] else ""


def two_table_rows(ticket, prev, new, path, label):
    """★main 真实落表形状: ① §16.2 链头行 + ② §19.3 逐条登记行 = 两张表各一行★"""
    r1 = (f"| ★**`{path}`** ★ | `{prev}` | `{new}` | ★**是**★ |\n")
    r2 = (f"| L9999 | {path} | `{prev}` | `{new}` | ★**2026-11-18 05:5x** ★ | "
          f"★**{ticket}** ★ |\n")
    return r1, r2


print("=" * 96)
print("【ISS-296 cont3 探针】合法改板通道 × main 真实落表形状 (两张表各一行)")
print("=" * 96)

# =====================================================================================
# A: 合法改板一次 + 两张表都写 ⇒ C4 必须绿
# =====================================================================================
sb = cf.make_sandbox(ROOT, "probeA_dup_rows_legal_reboard")
newmd5 = board_append_byte(sb)
r1, r2 = two_table_rows("ISS-999", BASE, newmd5[:12], BOARD_REL, "板")
pro_r = (f"| ★**`{PRO_REL}`** ★ | `{PRO_BASE}` | `{PRO_BASE}` | ★**否 (逐字节不变)** ★ |\n")
sb_write(sb, sb_read(sb) + "\n" + r1 + r2 + pro_r)
resA = cf.run_checks(sb)
greenA = resA["C4"]["ok"]
othersA = [k for k in ("C1", "C2", "C3") if not resA[k]["ok"]]
print(f"\n[A] 合法改板一次 + §16.2 行 + §19.3 行 (两张表) ⇒ C4 绿: {'是' if greenA else '否'}"
      f" · C1/C2/C3 = {'全绿' if not othersA else othersA} · C4 错误 {len(resA['C4']['errs'])} 条")
if not greenA:
    print(f"    ⇒ 红在哪: {c4_reason(resA)}")
    errs.append("A: 两张表形状下合法改板后 C4 红了 ⇒ 真实落表会假红 (★ISS-296 的承诺被破★)")
if othersA:
    errs.append(f"A: 两张表形状下 C1/C2/C3 红了: {othersA}")

# =====================================================================================
# B: 两张表都写, 但两行的【改前 md5 互相不一致】⇒ C4 必须红 (fail-closed)
# =====================================================================================
sb = cf.make_sandbox(ROOT, "probeB_dup_rows_inconsistent_prev")
newmd5B = board_append_byte(sb)
b1 = (f"| ★**`{BOARD_REL}`** ★ | `{BASE}` | `{newmd5B[:12]}` | ★**是**★ |\n")
b2 = (f"| L9999 | {BOARD_REL} | `deadbeefdead` | `{newmd5B[:12]}` | ★**2026-11-18 05:5x** ★ | "
      f"★**ISS-999** ★ |\n")
sb_write(sb, sb_read(sb) + "\n" + b1 + b2 + pro_r)
resB = cf.run_checks(sb)
redB = not resB["C4"]["ok"]
print(f"\n[B] 两张表都写但【改前 md5 互相不一致】⇒ C4 红: {'是' if redB else '否'} · {c4_reason(resB)}")
if not redB:
    errs.append("B: 两张表改前 md5 不一致后 C4 没红 ⇒ fail-closed 被放松")

# =====================================================================================
# C: 台账里【同一个链头 md5 出现在几行】⇒ ⑩c 自检变红的根因
# =====================================================================================
lt = sb_read(ROOT)
st = cf.ledger_state(os.path.join("HW", "netlist_v1.csv"), lt)
head = st["head"]
rows_with_head = []
for i, ln in enumerate(lt.splitlines(), 1):
    t = ln.strip()
    if not t.startswith("|"):
        continue
    tk = cf.LEDGER_MD_RE.findall(t)
    if len(tk) >= 2 and tk[-1][:12] == head:
        rows_with_head.append(i)
print(f"\n[C] 台账链头 {head} 出现在 {len(rows_with_head)} 行: {rows_with_head}")
print(f"    ⇒ ⑩c 反向用例的沙盒构造按『最后 md5 == 链头』扫全部行 ⇒ 命中 {len(rows_with_head)} 行"
      f" ⇒ 而它的断言写的是 hit == 1 ⇒ 【NG】")
print(f"    ⇒ ★**这不是闸的判据问题** (C4 判红仍然正确) ⇒ 是【自检夹具的计数假设】过期 ★")
if len(rows_with_head) <= 1:
    errs.append("C: 链头只出现在 1 行 ⇒ ⑩c 的 hit==1 假设仍成立 ⇒ 需另找根因")

# =====================================================================================
print("\n" + "=" * 96)
print(f"【探针结论】{'✅ 三条全过' if not errs else '❌ ' + '; '.join(errs)}")
print("=" * 96)
sys.exit(0 if not errs else 2)
