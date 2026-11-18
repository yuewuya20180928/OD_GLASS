#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/check_g1a7_selection_landed.py —— ★★**G1a-7 选型落表门禁** ★★ (ISS-257 · hw-lead · 2026-11-16)
================================================================================
★★**它是干什么的**: ★**守住「G1a-7 = 选型已落表 (必装件无「[待选型]」)」这条绿** ★★
⇒ ★**不是查网表对不对, 是查【那 14 件有没有被改回去 / 改漏 / 改空 / 改坏】** ★

★★**为什么必须有这把尺子 (★本轮 P0 的教训, 血买来的★)** ★★
★**上一轮 (ISS-257 第 1 轮, 20:53 超时) 把 14 件落表时, 把落表链的【证据等级词表】写错了** ★
★**⇒ 网表 CSV 的 `evidence` 列里落了 29 行 `[官网]`** ★
★**⇒ 而落表链自己的白名单 (`state/check_netlist.py` L30 `LEGAL_EVIDENCE`) 里有 `[官方]`, 没有 `[官网]`** ★
★**⇒ `state/check_netlist.py` 由绿转红 ⇒ G1a-5 (原理图定稿的尺子) 跟着红 ⇒ 原理图定稿门跟着红** ★
★**⇒ 所以本闸把「evidence 列必须落在白名单里」单独立成一条判据 (C5)** ★
★**⇒ 并且把这条写进 `--selftest` 的反向用例 (M4: 把某个 evidence 改成 `[官网]` ⇒ 必须红)** ★
★★**⇒ 一句话: ★*同一个坑不许踩第二次* ★★

★★**★两套证据等级词表各归各 (★本闸只认落表链那一套★)** ★★
  · ★**落表链八档** (网表/脚表/BOM 的 `evidence` 列): `[官方]` `[推算]` `[实测]` `[待原厂]`
    `[待JBD]` `[待视涯]` `[同Die参考-待官方确认]` `[0数据]`
    ⇒ ★**判据源 = `state/check_netlist.py` L30** ★
  · ★**选型五档** (选型矩阵 / 缺口清单 / 交卷单散文): `[官网]` `[实测]` `[媒体]` `[推算]` `[0数据]`
    ⇒ ★**判据源 = `HW/check_part_selection_matrix.py` L46 / `HW/check_part_selection_gaps.py` L56** ★
  ⇒ ★**本闸只管落表链那一套; 选型五档一个字不碰 (★那是老板政策, 不是本闸的事★)** ★

★★**六条判据 (★逐条都有反向用例★)** ★★
  **C1** 必装件 ∩ value 含 `[待选型]` = **0 件** (★与 `state/check_stage_g1a.py` 的 G1a-7 同口径★)
  **C2** ★**14 个位号逐个点名** ★: value 非空 / value 不含占位词 / opn 非空 / BOM·网表·脚表 三方都在
  **C3** ★**脚数 584 / 器件 218 / K=0** ★ (★K=0 = 图上逐器件脚数 == 表里逐器件脚数, ★自己解析 .kicad_sch, 不调 KiCad★)
  **C4** ★**板 + `.kicad_pro` md5 逐字节不变** ★ (`611b869e…` / `3e504d2b…`)
  **C5** ★**`evidence` 列必须落在落表链白名单里 (★本轮 P0 的教训进闸★)** ★ (网表 + 脚表 + BOM 三处)
  **C6** 14 个位号的落表闭环: dnp=必装 / evidence 合法 / 不含 `[待选型]` / opn 与网表侧一致

★★**rc 语义** ★★
  `rc=0` ⇒ ★**六条全过 (落表还在)** ★ · `rc=1` ⇒ 有判据不通过, ★**逐条点名** ★ · `rc=2` ⇒ 用法/环境错误
★★**纪律** ★★
  · ★**只读**: 本闸不写任何项目文件 (自检只在临时目录里改副本) ★
  · ★**不改网表 / 不改 BOM / 不改板 / 不改生成器 / 不改判据阈值** ★
  · ★**不跑 KiCad** (★自己解析 .kicad_sch ⇒ 快 + 不产生 UUID 抖动★) ★
  · ★**位号口径的单一真源 = `state/gen_kicad_sch.py` 的 `kicad_ref()`** (★导入失败 ⇒ 响亮失败★) ★

用法:
    python3 HW/check_g1a7_selection_landed.py                  # 跑闸 (rc=0 过)
    python3 HW/check_g1a7_selection_landed.py --verbose        # 逐条明细
    python3 HW/check_g1a7_selection_landed.py --selftest       # 反向用例 (全部必须红)
    python3 HW/check_g1a7_selection_landed.py --root DIR       # 指定工程根 (自检/复现用)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
STATE = os.path.join(PROJ, "state")
# ★★ISS-297 · 2026-11-17 19:3x (hw-lead): 「合法改板」通道 (★判决源 = 落表台账链头 + 四项原子映射★) ★★
#   ★机制照 ISS-284 已跑通的口径; ★本域【自己写】(★不 import 别人地界★) ★
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import board_reboard                                          # noqa: E402

REL = {
    "netlist": os.path.join("HW", "netlist_v1.csv"),
    "pins": os.path.join("HW", "netlist_v1_pins.csv"),
    "bom": os.path.join("HW", "BOM_v1.csv"),
    "board": os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    "pro": os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"),
    "schdir": os.path.join("HW", "PCB"),
    # ★★ISS-297 · ⑭ · 通道要读的两件 (★判决源 = 落表台账链头 + 锚点里的四项原子映射★) ★★
    "anchor": os.path.join("HW", "PCB", "BOARD_ONEPASS_MD5_LEDGER.md"),
    "landing": os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md"),
}

# ★★落表链八档 (★判据源 = `state/check_netlist.py` L30 `LEGAL_EVIDENCE` · ★不许扩词★) ★★
LEGAL_EVIDENCE = {"[官方]", "[推算]", "[实测]", "[待原厂]", "[待JBD]", "[待视涯]",
                  "[同Die参考-待官方确认]", "[0数据]"}

# ★★占位词 (★value / opn 里出现任意一个 = 没落表★) ★★
PLACEHOLDER = ("[待选型]", "[待原厂]", "[待JBD]", "[待视涯]", "TBD", "待定")

# ★★本批落表的 14 个位号 (★ISS-257 §18.2 的 14 件·顺序与台账一致★) ★★
TARGET_REFS = [
    "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_TC", "D_ESD_USB_D", "D_TVS_VBUS",
    "FB_DEMO", "FB_VBUS", "Q_AND", "Q_CHG_LED", "Q_ENVC", "Q_PG",
    "R_SUPV_DIV1", "R_SUPV_DIV2", "U_PWR_SW",
]

EXPECT_PINS = 584
EXPECT_DEVS = 218
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
PRO_MD5 = "3e504d2be83152e337949723e909be1b"

# ★★位号口径的单一真源 (★导入失败 ⇒ 响亮失败, ★不许复制粘贴副本★) ★★
if STATE not in sys.path:
    sys.path.insert(0, STATE)
try:
    import gen_kicad_sch as _gen
except Exception as _e:  # noqa: BLE001
    sys.exit("★生成器导入失败 ⇒ 拒绝跑 (★防位号口径漂移 ⇒ 宁可直接挂★): %s" % _e)
kicad_ref = _gen.kicad_ref


# ─────────────────────────────────────────────────────────────────────────────
# 小工具
# ─────────────────────────────────────────────────────────────────────────────
def md5_file(p: str) -> str:
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(p: str) -> list[dict]:
    with io.open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _path(root: str, key: str) -> str:
    return os.path.join(root, REL[key])


# ─────────────────────────────────────────────────────────────────────────────
# 图侧脚数 (★自己解析 .kicad_sch, ★不调 KiCad ⇒ 不产生 UUID 抖动★)
# ─────────────────────────────────────────────────────────────────────────────
_INST_RE = re.compile(r'\(property "Reference" "([^"]*)"')
_PIN_RE = re.compile(r'\(\s*pin "([^"]*)"\s*\(\s*uuid')


def sch_pin_counts(schdir: str) -> tuple[dict[str, int], int]:
    """返回 ({图上位号: 该实例的脚数}, 实例总数)"""
    out: dict[str, int] = {}
    total = 0
    if not os.path.isdir(schdir):
        return out, 0
    for fn in sorted(os.listdir(schdir)):
        if not fn.endswith(".kicad_sch"):
            continue
        with io.open(os.path.join(schdir, fn), encoding="utf-8") as fh:
            text = fh.read()
        # ★每个实例块 = (symbol ... (property "Reference" "X" ...) (pin "N" ...) ...)★
        # ⇒ 用 "上一个 symbol 块起点 → 本次 Reference 属性" 的区间数 pin★
        starts = [m.start() for m in re.finditer(r"\n\s*\(symbol\s*\n", text)]
        for m in _INST_RE.finditer(text):
            ref = m.group(1)
            lo = max([s for s in starts if s < m.start()] or [0])
            hi = min([s for s in starts if s > m.start()] or [len(text)])
            n = len(_PIN_RE.findall(text[lo:hi]))
            out[ref] = out.get(ref, 0) + n
            total += 1
    return out, total


# ─────────────────────────────────────────────────────────────────────────────
# 主检查
# ─────────────────────────────────────────────────────────────────────────────
def check(root: str, verbose: bool = False) -> tuple[int, list[str]]:
    errors: list[str] = []
    report: list[str] = []

    # ---- 文件在不在 ----
    for key in ("netlist", "pins", "bom", "board", "pro"):
        if not os.path.exists(_path(root, key)):
            errors.append("★缺文件: %s" % REL[key])
    if errors:
        return 2, errors

    net_rows = read_rows(_path(root, "netlist"))
    pin_rows = read_rows(_path(root, "pins"))
    bom_rows = read_rows(_path(root, "bom"))

    bom = {r["ref"]: r for r in bom_rows}
    net_by_ref: dict[str, list[dict]] = {}
    for r in net_rows:
        net_by_ref.setdefault(r["ref"], []).append(r)
    pin_by_ref: dict[str, list[dict]] = {}
    for r in pin_rows:
        pin_by_ref.setdefault(r["ref"], []).append(r)

    # ══════════ C1 · 必装 ∩ `[待选型]` = 0 ══════════
    c1_bad = [r["ref"] for r in bom_rows
              if r.get("dnp") == "必装" and "[待选型]" in (r.get("value") or "")]
    if c1_bad:
        errors.append("★C1 必装件里还有 %d 件写着「[待选型]」: %s"
                      % (len(c1_bad), ", ".join(c1_bad)))
    report.append("   %s C1  必装 ∩ 「[待选型]」 = %d 件 (期望 0)"
                  % ("OK  " if not c1_bad else "FAIL", len(c1_bad)))

    # ══════════ C2 · 14 个位号逐个点名 ══════════
    c2_bad: list[str] = []
    for ref in TARGET_REFS:
        b = bom.get(ref)
        if not b:
            c2_bad.append("%s 不在 BOM 里" % ref)
            continue
        val = (b.get("value") or "").strip()
        opn = (b.get("opn") or "").strip()
        if not val:
            c2_bad.append("%s 的 value 是空的" % ref)
        for ph in PLACEHOLDER:
            if ph in val:
                c2_bad.append("%s 的 value 还含占位词 %s (value=%r)" % (ref, ph, val))
                break
        if not opn:
            c2_bad.append("%s 的 opn 是空的" % ref)
        for ph in ("[待选型]", "[待原厂]", "[待JBD]", "[待视涯]"):
            if ph in opn:
                c2_bad.append("%s 的 opn 还含占位词 %s" % (ref, ph))
                break
        if ref not in net_by_ref:
            c2_bad.append("%s 不在网表 HW/netlist_v1.csv 里" % ref)
        if ref not in pin_by_ref:
            c2_bad.append("%s 不在脚表 HW/netlist_v1_pins.csv 里" % ref)
    if c2_bad:
        errors.append("★C2 14 个落表位号里有 %d 条不合格: %s" % (len(c2_bad), "; ".join(c2_bad)))
    report.append("   %s C2  14 个落表位号逐个点名 (value/opn/占位词/三方在表) — %d 条不合格"
                  % ("OK  " if not c2_bad else "FAIL", len(c2_bad)))

    # ══════════ C3 · 脚数 584 / 器件 218 / K=0 ══════════
    c3_bad: list[str] = []
    n_pins = len(pin_rows)
    n_devs = len(pin_by_ref)
    if n_pins != EXPECT_PINS:
        c3_bad.append("表里脚数 = %d (期望 %d)" % (n_pins, EXPECT_PINS))
    if n_devs != EXPECT_DEVS:
        c3_bad.append("表里器件数 = %d (期望 %d)" % (n_devs, EXPECT_DEVS))

    sch_counts, n_inst = sch_pin_counts(_path(root, "schdir"))
    k_mismatch: list[str] = []
    for ref, rs in pin_by_ref.items():
        want = len(rs)
        flat = kicad_ref(ref)
        got = sch_counts.get(flat)
        if got is None:
            k_mismatch.append("%s (表 %d 脚) 图上【没有这个符号】" % (ref, want))
        elif got != want:
            k_mismatch.append("%s (表 %d 脚 / 图 %d 脚)" % (ref, want, got))
    if k_mismatch:
        c3_bad.append("K != 0 (图上脚数 ≠ 表里脚数) 的器件 %d 个: %s"
                      % (len(k_mismatch), "; ".join(k_mismatch[:8])))
    total_sch_pins = sum(sch_counts.values())
    if not k_mismatch and total_sch_pins != EXPECT_PINS:
        c3_bad.append("图上脚数合计 = %d (期望 %d)" % (total_sch_pins, EXPECT_PINS))
    if c3_bad:
        errors.append("★C3 脚数/器件数/K: %s" % "; ".join(c3_bad))
    report.append("   %s C3  表 %d 脚 / %d 器件 · 图 %d 脚 / %d 符号 · K=%d (期望 %d/%d/K=0)"
                  % ("OK  " if not c3_bad else "FAIL", n_pins, n_devs, total_sch_pins, n_inst,
                     len(k_mismatch), EXPECT_PINS, EXPECT_DEVS))

    # ══════════ C4 · 板 + .kicad_pro md5 逐字节不变 ══════════
    # ★★ISS-297 · 2026-11-17 19:3x (hw-lead): ★**判决源 = 落表台账链头 + 合法改板四项原子映射** ★
    #   ★判据方向一字未变 (★盘上 ≠ 判决源 ⇒ 红★); ★变的只是【判决源】: 写死常量 → 台账链头 ★
    #   ★fail-closed 三条一条不许动 (★链头不唯一 / 链断 / 链头无单号 ⇒ 仍红★) ★
    #   ★`reboard: null` (还没发生过合法改板) ⇒ 仍按纯 md5 硬保护判 ★
    c4_bad: list[str] = []
    b_md5 = md5_file(_path(root, "board"))
    p_md5 = md5_file(_path(root, "pro"))
    ch = board_reboard.check_pair(root, _path(root, "board"), BOARD_MD5,
                                  _path(root, "pro"), PRO_MD5, md5fn=md5_file)
    if not ch["ok"]:
        for e in ch["errs"]:
            c4_bad.append(e)
    if c4_bad:
        errors.append("★C4 受保护文件: %s" % "; ".join(c4_bad))
    report.append("   %s C4  板 %s / .kicad_pro %s (★判决源 = 落表台账链头 + 合法改板通道; 保护基线 %s / %s★)"
                  % ("OK  " if not c4_bad else "FAIL", b_md5[:8], p_md5[:8], BOARD_MD5[:8], PRO_MD5[:8]))

    # ══════════ C5 · evidence 列必须落在落表链白名单里 (★本轮 P0 的教训进闸★) ══════════
    c5_bad: list[str] = []
    for kind, rows in (("netlist", net_rows), ("pins", pin_rows), ("bom", bom_rows)):
        seen: set[str] = set()
        for r in rows:
            ev = (r.get("evidence") or "").strip()
            if ev and ev not in LEGAL_EVIDENCE and ev not in seen:
                seen.add(ev)
                c5_bad.append("%s 的 evidence 列出现非法值 %r (落表链八档里没有它 ⇒ ★**本轮 P0 就是这么红的**★)"
                              % (REL[kind], ev))
    if c5_bad:
        errors.append("★C5 证据等级词表: %s" % "; ".join(c5_bad))
    report.append("   %s C5  evidence 列全在落表链八档白名单里 (★`[官网]` ⇒ 红★) — %d 条非法"
                  % ("OK  " if not c5_bad else "FAIL", len(c5_bad)))

    # ══════════ C6 · 14 个位号的落表闭环 ══════════
    c6_bad: list[str] = []
    for ref in TARGET_REFS:
        b = bom.get(ref)
        if not b:
            continue
        if (b.get("dnp") or "") != "必装":
            c6_bad.append("%s 的 dnp = %r (落表要求必装)" % (ref, b.get("dnp")))
        ev = (b.get("evidence") or "").strip()
        if ev not in LEGAL_EVIDENCE:
            c6_bad.append("%s 的 evidence = %r 不在落表链八档里" % (ref, ev))
        if "[待选型]" in (b.get("value") or ""):
            c6_bad.append("%s 的 value 还写着 [待选型]" % ref)
        # ★网表侧同位号的 evidence 也得是合法的 (★本轮 29 行就死在这儿★)★
        for r in net_by_ref.get(ref, []):
            nev = (r.get("evidence") or "").strip()
            if nev and nev not in LEGAL_EVIDENCE:
                c6_bad.append("%s 在网表里的 evidence = %r 不在落表链八档里" % (ref, nev))
                break
        # ★opn 三方一致 (★网表侧 opn 列 vs BOM 侧 opn 列★)★
        net_opns = {(r.get("opn") or "").strip() for r in net_by_ref.get(ref, [])}
        net_opns = {o for o in net_opns if o}
        bom_opn = (b.get("opn") or "").strip()
        if net_opns and bom_opn and bom_opn not in net_opns:
            c6_bad.append("%s 的 opn 网表侧(%s) 与 BOM 侧(%s) 对不上" % (ref, "/".join(sorted(net_opns)), bom_opn))
    if c6_bad:
        errors.append("★C6 14 个位号的落表闭环: %s" % "; ".join(c6_bad))
    report.append("   %s C6  14 个位号: dnp=必装 / evidence 合法 / 无 [待选型] / opn 三方一致 — %d 条不合格"
                  % ("OK  " if not c6_bad else "FAIL", len(c6_bad)))

    if verbose:
        report.extend(errors)
    return (1 if errors else 0), report


# ─────────────────────────────────────────────────────────────────────────────
# 反向自检 (★把判据读的东西改坏 ⇒ 必须变红★)
# ─────────────────────────────────────────────────────────────────────────────
FIXTURE_FILES = [
    REL["netlist"], REL["pins"], REL["bom"], REL["board"], REL["pro"],
    # ★★ISS-297 · ⑭ · 通道两件 (★不进沙盒 ⇒ C4 会 fail-closed 恒红 ⇒ 自检就没意义了★) ★★
    REL["anchor"], REL["landing"],
]


def _copy_fixture(root: str, dst: str) -> str:
    for rel in FIXTURE_FILES:
        src = os.path.join(root, rel)
        if os.path.exists(src):
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
    # ★图 (★11 个 .kicad_sch · ★只读, ★自检不改它★) ★
    sdir = os.path.join(root, REL["schdir"])
    ddir = os.path.join(dst, REL["schdir"])
    if os.path.isdir(sdir):
        os.makedirs(ddir, exist_ok=True)
        for fn in os.listdir(sdir):
            if fn.endswith(".kicad_sch"):
                shutil.copy2(os.path.join(sdir, fn), os.path.join(ddir, fn))
    return dst


def _fixture_fingerprint(root: str) -> str:
    """★自检护栏: ★突变必须真的改了盘上的副本 ⇒ 否则「反向用例没抓到」是假的★"""
    h = hashlib.md5()
    for rel in FIXTURE_FILES:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            h.update(md5_file(p).encode())
    return h.hexdigest()


def _run_case(name: str, root: str, mutate, expect_rc: int = 1) -> tuple[str, bool, str]:
    tmp = tempfile.mkdtemp(prefix="g1a7_selftest_")
    try:
        _copy_fixture(root, tmp)
        before = _fixture_fingerprint(tmp)
        mutate(tmp)
        after = _fixture_fingerprint(tmp)
        if before == after:
            return name, False, "★突变没生效 (副本逐字节没变) ⇒ 用例本身写错了, 不算抓到★"
        rc, _ = check(tmp, False)
        if rc != expect_rc:
            return name, False, "rc=%d (期望 %d)" % (rc, expect_rc)
        return name, True, "rc=%d (期望 %d) ✔" % (rc, expect_rc)
    except Exception as exc:  # noqa: BLE001
        return name, False, "异常: %s" % exc
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _edit_csv(path: str, fn) -> None:
    with io.open(path, encoding="utf-8", newline="") as fh:
        r = csv.DictReader(fh)
        cols = r.fieldnames
        rows = list(r)
    rows = fn(cols, rows)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def selftest(root: str) -> int:
    cases = []

    # M1 · 把某个 value 改回 `[待选型]` ⇒ 必须红 (C1 + C2)
    def m1(tmp):
        p = os.path.join(tmp, REL["bom"])
        def fn(cols, rows):
            for r in rows:
                if r["ref"] == "Q_AND":
                    r["value"] = "[待选型] N-MOS (硬件 AND)"
                    r["procurement"] = "待选型"
            return rows
        _edit_csv(p, fn)
    cases.append(("M1 把 Q_AND 的 value 改回「[待选型]」", m1, 1))

    # M2 · 删一个位号 ⇒ 必须红 (C2)
    def m2(tmp):
        p = os.path.join(tmp, REL["bom"])
        def fn(cols, rows):
            return [r for r in rows if r["ref"] != "Q_PG"]
        _edit_csv(p, fn)
    cases.append(("M2 从 BOM 删掉一个落表位号 (Q_PG)", m2, 1))

    # M3 · 改脚数 (脚表少一行) ⇒ 必须红 (C3)
    def m3(tmp):
        p = os.path.join(tmp, REL["pins"])
        def fn(cols, rows):
            for i, r in enumerate(rows):
                if r["ref"] == "Q_AND":
                    return rows[:i] + rows[i + 1:]
            return rows
        _edit_csv(p, fn)
    cases.append(("M3 脚表里删掉一个脚 (改脚数)", m3, 1))

    # ★★M4 · 把某个 evidence 改成 `[官网]` ⇒ 必须红 (★本轮 P0 的教训必须进闸★) ★★
    def m4(tmp):
        p = os.path.join(tmp, REL["netlist"])
        def fn(cols, rows):
            for r in rows:
                if r["ref"] == "Q_AND":
                    r["evidence"] = "[官网]"
                    break
            return rows
        _edit_csv(p, fn)
    cases.append(("★M4 把网表某行的 evidence 改成「[官网]」(本轮 P0 的坑)", m4, 1))

    # M5 · 改板 (板 md5 变了) ⇒ 必须红 (C4)
    def m5(tmp):
        p = os.path.join(tmp, REL["board"])
        with io.open(p, "a", encoding="utf-8") as fh:
            fh.write("\n; (test tamper)\n")
    cases.append(("M5 板文件被改动 (md5 变)", m5, 1))

    # M6 · 改 .kicad_pro ⇒ 必须红 (C4)
    def m6(tmp):
        p = os.path.join(tmp, REL["pro"])
        with io.open(p, "a", encoding="utf-8") as fh:
            fh.write("\n{}\n")
    cases.append(("M6 .kicad_pro 被改动 (md5 变)", m6, 1))

    # M7 · 把某个 opn 清空 ⇒ 必须红 (C2)
    def m7(tmp):
        p = os.path.join(tmp, REL["bom"])
        def fn(cols, rows):
            for r in rows:
                if r["ref"] == "U_PWR_SW":
                    r["opn"] = ""
            return rows
        _edit_csv(p, fn)
    cases.append(("M7 把 U_PWR_SW 的 opn 清空", m7, 1))

    # M8 · 把某个 value 换成另一个占位词 ⇒ 必须红 (C2)
    def m8(tmp):
        p = os.path.join(tmp, REL["bom"])
        def fn(cols, rows):
            for r in rows:
                if r["ref"] == "R_SUPV_DIV1":
                    r["value"] = "[待原厂] 分压上臂"
            return rows
        _edit_csv(p, fn)
    cases.append(("M8 把 R_SUPV_DIV1 的 value 换成「[待原厂]」", m8, 1))

    # M9 · 脚表里删掉一个位号 (器件数 218→217) ⇒ 必须红 (C3)
    def m9(tmp):
        p = os.path.join(tmp, REL["pins"])
        def fn(cols, rows):
            return [r for r in rows if r["ref"] != "CHG_GND_STAR"]
        _edit_csv(p, fn)
    cases.append(("M9 脚表里删掉一个位号 (器件数 218→217)", m9, 1))

    # M10 · 把 BOM 里某个落表位号的 dnp 改成 DNP ⇒ 必须红 (C6)
    def m10(tmp):
        p = os.path.join(tmp, REL["bom"])
        def fn(cols, rows):
            for r in rows:
                if r["ref"] == "FB_VBUS":
                    r["dnp"] = "DNP"
            return rows
        _edit_csv(p, fn)
    cases.append(("M10 把 FB_VBUS 的 dnp 改成 DNP", m10, 1))

    # M11 · 把 BOM 的 evidence 改成 `[官网]` ⇒ 必须红 (C5)
    def m11(tmp):
        p = os.path.join(tmp, REL["bom"])
        def fn(cols, rows):
            for r in rows:
                if r["ref"] == "D_TVS_VBUS":
                    r["evidence"] = "[官网]"
            return rows
        _edit_csv(p, fn)
    cases.append(("M11 把 BOM 的 evidence 改成「[官网]」", m11, 1))

    print("=" * 76)
    print("  G1a-7 选型落表门禁 · 反向自检 (★每条都必须变红, 变绿就是判据没被读到★)")
    print("=" * 76)
    ok = 0
    for name, fn, want in cases:
        nm, passed, info = _run_case(name, root, fn, want)
        print("  %s %-52s %s" % ("✅" if passed else "❌", nm, info))
        ok += 1 if passed else 0
    print("-" * 76)
    print("  自检结果: %d/%d 通过" % (ok, len(cases)))

    # ★★ISS-297 · ⑭ · 「合法改板」通道的反向用例 (★沙盒跑·真盘零写·判决源 = 台账链头★) ★★
    #   ★机制: `HW/board_reboard.py` 的 CASES (★照 ISS-284 已跑通的口径·不许自创★) ★
    #   ★每条都【真跑本闸】(★root 指向沙盒★) ⇒ 判据变红/变绿都必须是本闸自己的结论 ★
    #   ★① 合法改板 ⇒ 绿 ② 只改基线没台账记录 ⇒ 红 ③ 四项缺一 ⇒ 红 ④ 盘上 ≠ 记录里的新 md5 ⇒ 红
    #     ⑤ 链头不唯一 / 链断 / 链头无单号 ⇒ 红 (★fail-closed 三条一条不许动★) ★
    ch_cases = []
    tmp_iss297 = tempfile.mkdtemp(prefix="g1a7_iss297_")
    try:
        def iss297_prepare(sb):
            """★把本闸要读的东西铺进沙盒 (★board_reboard 只拷通道那 4 件★) ★"""
            for rel in FIXTURE_FILES:
                src = os.path.join(root, rel)
                d = os.path.join(sb, rel)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(src, d)
            sdir = os.path.join(root, REL["schdir"])
            ddir = os.path.join(sb, REL["schdir"])
            os.makedirs(ddir, exist_ok=True)
            for fn in os.listdir(sdir):
                if fn.endswith(".kicad_sch"):
                    shutil.copy2(os.path.join(sdir, fn), os.path.join(ddir, fn))

        def iss297_judge(sb):
            rc, rep = check(sb, True)
            note = "★本闸 rc=%d★" % rc
            for ln in rep:
                if "C4" in ln:
                    note += " · " + ln.strip()
            return rc == 0, note

        for _name, _exp, _got, _note in board_reboard.run_cases(
                root, os.path.join(tmp_iss297, "iss297_channel"),
                iss297_judge, prepare=iss297_prepare):
            ch_cases.append(("ISS297 " + _name, _exp == _got, _note))
    finally:
        shutil.rmtree(tmp_iss297, ignore_errors=True)

    print("-" * 76)
    print("  ★★ISS-297 · ⑭ 「合法改板」通道反向用例 (%d 条·判决源 = 落表台账链头 + 四项原子映射★)" % len(ch_cases))
    ok_ch = 0
    for name, passed, info in ch_cases:
        print("  %s %s" % ("✅" if passed else "❌", name))
        print("       %s" % info)
        ok_ch += 1 if passed else 0
    print("-" * 76)
    print("  ⇒ 通道用例: %d/%d 通过 · 合计 %d/%d"
          % (ok_ch, len(ch_cases), ok + ok_ch, len(cases) + len(ch_cases)))
    if ok != len(cases) or ok_ch != len(ch_cases):
        print("  ❌ 有反向用例没抓到 ⇒ 判据是摆设 ⇒ 闸不算数")
        return 1
    print("  ✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没★)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=PROJ, help="工程根 (默认 = 本脚本上一级)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="只跑反向用例")
    args = ap.parse_args()

    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    print("=" * 76)
    print("  G1a-7 选型落表门禁 (★ISS-257 · 守住「必装件无「[待选型]」」这条绿★)")
    print("=" * 76)
    rc, report = check(root, True)
    for line in report:
        print(line)
    print("-" * 76)
    if rc == 0:
        print("✅ rc=0: ★★G1a-7 落表还在 (★14 件全落 + 脚数 584/218/K=0 + 板逐字节不变 + evidence 合白名单★)")
    elif rc == 2:
        print("❌ rc=2: 环境/用法错误")
    else:
        print("❌ rc=1: ★**落表被改坏了** ★ (★见上面逐条★)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
