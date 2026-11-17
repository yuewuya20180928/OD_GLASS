#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-288 · sw-lead · 沙盒反向用例自测器 (★情形二: 真盘套补丁后的验收门★)
=====================================================================
★**为什么另起一个脚本 (而不是直接用 ISS-285 那份)★**

  ISS-285 的 `sbx_iss285_reverse_cases.py` 用例 ④ 把「合法落表补行」的
  【改前 md5】**硬编码**成 `2f17650cfbef48d5efd71821505c3343` (★那是 2026-11-17
  09:58:16 那一跳的链头★)。⇒ ISS-283 在 **12:30:23** 又落了一表, 链头前移到
  `37f62ac3f0b81d92ca7d48fdea717f07` ⇒ 那行补记挂到了**分叉**上 ⇒ 链头不唯一
  ⇒ 网表锚点两条判据【一起红】⇒ 用例 ④ 的期望红组 (只该红 F4' + REV-11) 配不上。

  ⇒ ★**那是 ISS-285 那份脚本的【测试夹具过期】, 不是补丁的缺陷**★
  ⇒ ★**本脚本把链头改成【从台账动态取】** ⇒ 台账再落几跳都不用改夹具★

跑法 (★全部在沙盒里跑★ · ★真盘网表/脚表/BOM/板/.kicad_pro 一个字节不许动★):

    # 0) 造一个「已套补丁」的干净基线沙盒
    python3 SW/patches/ISS-288_timing_check_land/verify_iss288_land.py --make-base \
            logs/iss288/sbx_base

    # 1) 跑全部用例
    python3 SW/patches/ISS-288_timing_check_land/verify_iss288_land.py \
            --base logs/iss288/sbx_base --work logs/iss288/sbx_work

退出码: 0 = 全部符合「期望红组 vs 实际红组」 · 1 = 有条不符

★**用例设计 (★覆盖 fail-closed 三条 + F4' 咬得住★)**:
  ① 盘上网表 md5 落在台账登记的状态之外 (伪造 md5)   ⇒ 锚点 ×2 红
  ② 落表台账那一行四项不齐 (缺改后 md5)              ⇒ 锚点 ×2 红 (链头取不准 ⇒ 允许集降级为 ∅)
  ③ 链头不唯一 (台账里从链中段分叉出第二条链)        ⇒ 锚点 ×2 红 (fail-closed)
  ④ 链断 (链头上多出一条前驱不唯一的记录)            ⇒ ★只红「三方对账」★
  ⑤ 链头无单号 (台账里所有小节标题的单号被抹掉)      ⇒ ★只红「三方对账」★
  ⑥ BAT_DET 三颗改回 DNP + 【合法补记把链头前移】     ⇒ ★只红 F4' + REV-11★
                                                          (★证明 F4' 自己在看网表★)
  ⑦ 正向对照: 一切如常                               ⇒ 全绿 (证明闸不是恒红)

★★**为什么 ④⑤ 只红一条、①②③ 红两条 (★不是夹具放水, 是判据设计★)**★★

  补丁的【允许状态集合】按【失败在哪一步】降级:
    · 链头**取不准** (不唯一 / 台账里一条记录都没有 / 判决源读不到) ⇒ 允许集 = **∅**
      ⇒ 连「盘上 md5 ∈ 台账登记状态」也一起红 (★比 R6 更保守★)
    · 链头取到了, 但【链断 / 链头无单号 / 盘上 ≠ 链头】 ⇒ 允许集 = 台账**已知集**
      ⇒ 「盘上 md5 ∈ 台账登记状态」仍绿 (★盘上那个 md5 确实是台账登记过的历史态★)
      ⇒ 但「三方对账成立」必红 (★真源对不上链头 ⇒ 闸不许放行★)

  ⇒ ★**结论: fail-closed 三条一条都没被放宽 —— 每条都至少红「三方对账」★**
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))      # projects/smart_glasses
# ★★【ISS-288 cont1 · 2026-11-17 · sw-lead】★★ 路径修正:
#   改前 = os.path.dirname(os.path.dirname(HERE)) ⇒ "SW/ISS-285_sw_judgment_alignment/…" (★少一层★)
#          ⇒ `--make-base` 必然 rc=2 (can't open file …/SW/ISS-285_sw_judgment_alignment/…)
#   改后 = os.path.dirname(HERE)               ⇒ "SW/patches/ISS-285_sw_judgment_alignment/…" ✅
#   ★**只改这一个路径常量, 判据逻辑 / 用例 / 期望红组 一行没动** ★
APPLIER = os.path.join(os.path.dirname(HERE),
                        "ISS-285_sw_judgment_alignment",
                        "apply_iss285_sw_judgment_alignment.py")

NETLIST_REL = os.path.join("HW", "netlist_v1.csv")
LEDGER_REL = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")
TIMING_REL = os.path.join("SW", "tools", "timing_check.py")
DPS_REL = os.path.join("SW", "tools", "check_demo_panel_spec.py")

K_ALLOWED = "网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)"
K_THREEWAY = "网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)"
K_F4 = "F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)"
K_REV11 = ("REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ "
           "F4'『BAT_DET 三颗必装』必须变红")

# ★沙盒最小镜像 (★只拷这两个门禁真正读到的文件 ⇒ 沙盒 ~6 MB, 不占盘★)
MIN_FILES = [
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
    "HW/SCHEMATIC_LANDING_V1_LANDED.md",
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
    "SW/tools/timing_check.py",
    "SW/tools/check_demo_panel_spec.py",
    "SW/SW_MD5_BASELINE_LEDGER.md",
    "SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md",
    "SW/DEMO_PANEL_SPEC_TRIAGE.md",
    "SW/DEMO_OD_PIPELINE_SPEC.md",
]


def md5_of(path: str) -> str:
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def load_timing(sbx: str):
    p = os.path.join(sbx, TIMING_REL)
    spec = importlib.util.spec_from_file_location("_iss288_timing", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def red_group(out: str):
    return [ln.split("] ", 1)[1].strip() for ln in out.splitlines() if "  [FAIL] " in ln]


def ledger_chain(sbx: str) -> list:
    """★从沙盒台账动态取链 (★链头 → 链尾★)★。"""
    mod = load_timing(sbx)
    dps, err = mod._dps()
    if dps is None:
        raise SystemExit("★读不到 R6 判决源实现: %s" % err)
    anchors, aerr = mod._sw_anchor_entries()
    if anchors is None:
        raise SystemExit("★读不到 SW 台账锚点: %s" % aerr)
    text, spec = dps.sw_ledger_canonical_text(sbx, anchors)
    st = dps.sw_ledger_state(NETLIST_REL, text)
    chain = list(st.get("chain") or [])
    if not chain:
        raise SystemExit("★台账链取不到: %s" % st.get("why"))
    return chain


def ledger_head(sbx: str) -> str:
    """★从沙盒里的落表台账【动态取链头】(★夹具不许硬编码 md5★)★。

    ★口径与 `SW/tools/check_demo_panel_spec.py` 的 `sw_ledger_state()` 同源★
      (★同一个判决源 ⇒ 补记行的「改前 md5」一定挂在真链头上, 不会造成分叉★)
    """
    mod = load_timing(sbx)
    dps, err = mod._dps()
    if dps is None:
        raise SystemExit("★读不到 R6 判决源实现: %s" % err)
    anchors, aerr = mod._sw_anchor_entries()
    if anchors is None:
        raise SystemExit("★读不到 SW 台账锚点: %s" % aerr)
    text, spec = dps.sw_ledger_canonical_text(sbx, anchors)
    st = dps.sw_ledger_state(NETLIST_REL, text)
    head = st.get("head")
    if not head:
        raise SystemExit("★台账链头取不准: %s" % st.get("why"))
    return head


# ===================================================================== 构造器
def mut_case1_fake_md5(sbx: str) -> str:
    """① 盘上网表 md5 落在台账登记的任何状态之外 (伪造 md5)。

    ★手法: 原地改【最后一行】的 `conn_id` 一个字段 (★conn_id 这列没有任何闸读★
      ⇒ 行数不变 (仍 513 数据行) · 结构不变 ⇒ 【只有 md5 变了】★)
    """
    mod = load_timing(sbx)
    p = os.path.join(sbx, NETLIST_REL)
    with open(p, "r", encoding="utf-8-sig", newline="") as fh:
        lines = fh.read().split("\n")
    idx = len(lines) - 1
    while idx > 0 and not lines[idx].strip():
        idx -= 1
    body, term = (lines[idx].rstrip("\r"), "\r") if lines[idx].endswith("\r") else (lines[idx], "")
    fields, quoted = mod._split_csv_line(body)
    fields[11] = "C-99"
    lines[idx] = mod._join_csv_line(fields, quoted) + term
    open(p, "w", encoding="utf-8-sig", newline="").write("\n".join(lines))
    return ("最后一行 L%d 的 conn_id → C-99 (★行数不变 · 结构不变 · 只有 md5 变★); "
            "盘上网表 md5 = %s" % (idx + 1, md5_of(p)))


def mut_case2_ledger_row_incomplete(sbx: str) -> str:
    """② 落表台账的落表行四项不齐 (缺『改后 md5』⇒ 该行不算落表记录 ⇒ 链头取不准)。"""
    p = os.path.join(sbx, LEDGER_REL)
    head = ledger_head(sbx)
    text = open(p, encoding="utf-8").read()
    lines = text.split("\n")
    hit = 0
    for i, ln in enumerate(lines):
        if NETLIST_REL in ln and head in ln:
            lines[i] = ln.replace(head, "★缺改后md5★")
            hit += 1
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return "台账里 %s 的链头落表行被改成『缺改后 md5』(四项不齐) ⇒ 命中 %d 行 (head=%s)" % (
        NETLIST_REL, hit, head)


def mut_case3_head_not_unique(sbx: str) -> str:
    """③ 链头不唯一 (台账里从【链中段】分叉出第二条链 ⇒ 两个链头 ⇒ 取不准 ⇒ 判红)。

    ★**手法**: 追加一条落表行, 它的【改前 md5 = 链中段那一跳】(★不是链头★)
      而【改后 md5 = 另一个】⇒ 台账里从同一前驱分出两条分支
      ⇒ 链头 = {真链头, fake} 两个 ⇒ 不唯一 ⇒ `sw_ledger_state` 取 head=None
      ⇒ 补丁的允许集降级为 ∅ ⇒ 两条网表锚点判据**一起红** (★fail-closed★)
    ★**注意**: 追加行的改前 md5 **不能取链头** —— 取链头只是【把链拉长】,
      链头仍然唯一 (那不是本用例★)。
    """
    p = os.path.join(sbx, LEDGER_REL)
    head = ledger_head(sbx)
    # ★链中段那一跳 = 链头上那行的【改前 md5】★
    mid = ""
    text = open(p, encoding="utf-8").read()
    for ln in text.split("\n"):
        if NETLIST_REL in ln and head in ln:
            toks = re.findall(r"\b[0-9a-f]{32}\b", ln)
            if len(toks) >= 2:
                mid = toks[0]
                break
    if not mid:
        raise SystemExit("★取不到链中段那一跳的 md5 (用例造不出来)")
    fake = "deadbeefdeadbeefdeadbeefdeadbeef"
    row = ("| ★**ISS-288** ★ | ★**`%s`** ★ | ★**`%s`** ★ | ★**`%s`** ★ | ★**是**★ |"
           % (NETLIST_REL, mid, fake))
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n" + row + "\n")
    return ("台账尾部追加第二条指向 %s 的落表行 (★改前 = 链中段 %s …, 改后 = %s…★ "
            "⇒ 链头分叉 = {真链头 %s, fake} 两个 ⇒ 取不准 ⇒ 允许集降级为 ∅ ⇒ 两条都红)"
            % (NETLIST_REL, mid[:12], fake[:12], head[:12]))


def mut_case4_chain_broken(sbx: str) -> str:
    """④ 链断 (链头上多出一条【前驱不唯一】的记录 ⇒ 链走不下去 ⇒ 判红)。

    ★**手法**: 追加一条落表行, 它的【改后 md5 = 真链头】但【改前 md5 = 链上**再往前一跳**】
      (★必须与真链头那一行的改前 md5 **不同** ★ ⇒ 否则前驱集合还是只有一个 ⇒ 链照样走得下去★)
      ⇒ 链头上挂了**两个不同的前驱** ⇒ `sw_ledger_state` 判「前驱不唯一」⇒ chain=[]
      ⇒ 补丁判「链断了 / 不唯一」⇒ 允许集降级为台账已知集
      ⇒ 「盘上 md5 ∈ 登记状态」仍绿 (★盘上那个 md5 确实是台账登记过的态★)
      ⇒ 但「三方对账成立」必红 (★真源对不上链头 ⇒ 闸不许放行★)
    """
    p = os.path.join(sbx, LEDGER_REL)
    head = ledger_head(sbx)
    chain = ledger_chain(sbx)
    # ★chain[0]=链头 · chain[1]=链头的真前驱 · chain[2]=再往前一跳 (★用作伪造的第二前驱★)
    if len(chain) < 3:
        raise SystemExit("★链太短, 造不出「前驱不唯一」(chain=%s)" % chain)
    other = chain[2]
    row = ("| ★**ISS-288** ★ | ★**`%s`** ★ | ★**`%s`** ★ | ★**`%s`** ★ | ★**是**★ |"
           % (NETLIST_REL, other, head))
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n" + row + "\n")
    return ("台账尾部追加第二条【改后 md5 = 真链头 %s】但【改前 md5 = %s (★与真前驱 %s 不同★)】的落表行 "
            "⇒ 链头前驱不唯一 ⇒ chain=[] ⇒ 判「链断了」⇒ 允许集 = 台账已知集 "
            "⇒ 「三方对账」必红" % (head[:12], other[:12], chain[1][:12]))


def mut_case5_head_no_iss(sbx: str) -> str:
    """⑤ 链头无单号 (台账里所有【小节标题】上的单号被抹掉 ⇒ 链头记录继承不到单号 ⇒ 判红)。

    ★**手法**: `sw_ledger_records()` 的单号口径 = 【行内 ISS-xxx】, 行内没写就
      【继承最近的带单号小节标题】⇒ 落表记录行本身**不带** ISS-xxx (它靠标题继承)
      ⇒ ★所以只抹行内的 ISS 抹不掉 ⇒ 必须把【所有 `#` 标题行】上的 ISS-xxx 全抹掉★
      ⇒ 链头记录的单号变成空 ⇒ 补丁判「链头缺落表单号 (字段缺失)」⇒ 判红
    """
    p = os.path.join(sbx, LEDGER_REL)
    text = open(p, encoding="utf-8").read()
    lines = text.split("\n")
    hit = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("#") and re.findall(r"ISS-\d+", s):
            lines[i] = re.sub(r"ISS-\d+", "★无单号★", ln)
            hit += 1
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return ("台账里【所有小节标题】的 ISS-xxx 被抹掉 (★命中 %d 行★ ⇒ 落表记录行继承不到单号★) "
            "⇒ 链头无单号 ⇒ 判红" % hit)


def mut_case6_bat_det_back_to_dnp(sbx: str) -> str:
    """⑥ 把 BAT_DET 三颗改回 DNP + 【合法补记把链头前移】⇒ 期望【只红 F4' + REV-11】。

    ★补记行的【改前 md5】取【当前真链头】(★动态取, 不硬编码★)
      ⇒ 补记挂在链尾上 ⇒ 链头**自动前移**到新 md5 ⇒ 网表锚点两条判据保持绿
      ⇒ 【红组里只剩 F4' + REV-11】⇒ 证明 F4' 真的在读网表, 不是被别的红盖住了★
    """
    mod = load_timing(sbx)
    nl = mod.Netlist(os.path.join(sbx, NETLIST_REL))
    want = {("BAT", "R_BAT_DET_1"), ("BAT_DET", "R_BAT_DET_2"),
            ("BAT_DET", "C_DET_BAT"), ("GND", "C_DET_BAT")}
    line_nos = [x["_line_no"] for x in nl.rows
                if ((x.get("net") or ""), (x.get("ref") or "")) in want]
    tmp = tempfile.mkdtemp(prefix="iss288_case6_")
    try:
        dst = os.path.join(tmp, "netlist_v1.csv")
        mod.set_dnp_at_lines_copy(nl, dst, line_nos, "DNP")
        shutil.copy2(dst, os.path.join(sbx, NETLIST_REL))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    new_md5 = md5_of(os.path.join(sbx, NETLIST_REL))
    prev = ledger_head(sbx)
    lp = os.path.join(sbx, LEDGER_REL)
    row = ("| ★**ISS-288** ★ | ★**`%s`** ★ | ★**`%s`** ★ | ★**`%s`** ★ | ★**是**★ |"
           % (NETLIST_REL, prev, new_md5))
    with open(lp, "a", encoding="utf-8") as f:
        f.write("\n" + row + "\n")
    return ("BAT_DET 三颗的器件本体行 L%s 改回 DNP ⇒ 盘上 md5 = %s ; "
            "台账补一行【合法落表记录】(改前 = 真链头 %s) ⇒ 链头前移 ⇒ 锚点两条判据保持绿"
            % (sorted(line_nos), new_md5, prev))


def mut_none(sbx: str) -> str:
    """⑦ 正向对照: 一切如常。"""
    return "什么都不改 (正向对照 ⇒ 证明闸不是恒红)"


CASES = [
    ("①", "盘上网表 md5 落在台账登记的任何状态之外 (伪造 md5)",
     mut_case1_fake_md5, {K_ALLOWED, K_THREEWAY}),
    ("②", "落表台账那一行四项不齐 (单号 / 文件名 / 前后 md5) ⇒ 链头取不准 ⇒ 允许集 ∅",
     mut_case2_ledger_row_incomplete, {K_ALLOWED, K_THREEWAY}),
    ("③", "链头不唯一 (台账里从链中段分叉出第二条链) ⇒ fail-closed 不许动",
     mut_case3_head_not_unique, {K_ALLOWED, K_THREEWAY}),
    ("④", "链断 (链头前驱不唯一) ⇒ fail-closed 不许动 ⇒ 允许集 = 台账已知集",
     mut_case4_chain_broken, {K_THREEWAY}),
    ("⑤", "链头无单号 (小节标题的单号被抹掉 ⇒ 继承不到单号) ⇒ fail-closed 不许动",
     mut_case5_head_no_iss, {K_THREEWAY}),
    ("⑥", "把 BAT_DET 三颗改回 DNP (+ 合法补记把链头前移) ⇒ ★只该红 F4' + REV-11★",
     mut_case6_bat_det_back_to_dnp, {K_F4, K_REV11}),
    ("⑦", "正向对照: 一切如常 (证明闸不是恒红)",
     mut_none, set()),
]


def copy_min(src: str, dst: str) -> None:
    os.makedirs(os.path.join(dst, "state"), exist_ok=True)
    for rel in MIN_FILES:
        s = os.path.join(src, rel)
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)


def make_base(base: str) -> int:
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(base)
    copy_min(PROJ, base)
    rc, out = run([sys.executable, APPLIER, "--root", base, "--apply"], cwd=base)
    print(out)
    if rc != 0:
        return rc
    rc, out = run([sys.executable, os.path.join(base, TIMING_REL)], cwd=base)
    print(out.splitlines()[-1] if out else "")
    return 0 if rc == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.join(PROJ, "logs", "iss288", "sbx_base"))
    ap.add_argument("--work", default=os.path.join(PROJ, "logs", "iss288", "sbx_work"))
    ap.add_argument("--make-base", action="store_true")
    args = ap.parse_args()

    if args.make_base:
        return make_base(args.base)

    if not os.path.isdir(args.base):
        print("★基线沙盒不存在: %s (先跑 --make-base)" % args.base)
        return 1

    allok = True
    for tag, desc, mut, expect in CASES:
        if os.path.isdir(args.work):
            shutil.rmtree(args.work)
        os.makedirs(args.work)
        copy_min(args.base, args.work)
        note = mut(args.work)
        rc, out = run([sys.executable, os.path.join(args.work, TIMING_REL)], cwd=args.work)
        got = set(red_group(out))
        rc2, out2 = run([sys.executable, os.path.join(args.work, DPS_REL)], cwd=args.work)
        print("=" * 78)
        print("【%s】%s" % (tag, desc))
        print("  构造: %s" % note)
        print("  ---- timing_check.py (沙盒) ---- rc=%d" % rc)
        for ln in out.splitlines():
            if "  [FAIL] " in ln or "SELFTEST" in ln:
                print("  " + ln)
        print("  ---- check_demo_panel_spec.py (沙盒) ---- rc=%d" % rc2)
        for ln in out2.splitlines():
            if ln.startswith("❌") or ln.startswith("   - "):
                print("  " + ln)
        print("  ★期望红组 (%d 条): %s" % (len(expect), sorted(expect) or "(空 ⇒ 期望全绿)"))
        print("  ★实际红组 (%d 条): %s" % (len(got), sorted(got) or "(空 ⇒ 实际全绿)"))
        ok = (got == expect)
        print("  ★判定: %s" % ("✅ 一致" if ok else "❌ 不一致 (期望 %s / 实际 %s)"
                               % (sorted(expect), sorted(got))))
        allok = allok and ok

    print("=" * 78)
    print("★%d 条用例总判定: %s" % (len(CASES), "✅ 全符合" if allok else "❌ 有条不符"))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
