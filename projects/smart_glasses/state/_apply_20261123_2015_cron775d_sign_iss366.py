#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
签收 ISS-366 (hw-lead) · ★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-23 20:1x★
================================================================================
★**为什么有本脚本**: ★**ISS-366 的 CONT2 会话 (agent:hw-lead:subagent:d92e7cd7) 于 20:03 交卷完毕
  (会话 status=done)⇒ 但台账 status 仍是 `fixing` ⇒ `state/advance.py` 的 in_flight 规则
  (该 agent 名下已有 fixing ⇒ 不派新活) ⇒ **hw-lead 槽位被【已交卷的单】永久压住** ⇒
  排队的 ISS-369 (hw-lead) 永远进不了 internal ⇒ ⇒ 本脚本 = 项目总工 (main) 的【签收】动作:
  把这条已交卷的单落成 verified ⇒ 槽位释放 ⇒ 派活链不断线 ★

★**本脚本严格 fail-closed (★判据全部本机实跑 · 不抄任何 agent 报告★)**:
  ① 验收线全部现跑 (新闸 rc + --selftest rc + 既有闸 3 道 rc + merge rc + gate_check rc + Q1 读数
     + 板/真源/生成器 md5 + 零挂链 grep + 交付物存在性 + 分片键 + **生成器级复跑的三条硬证据**)
  ② 只认「status == fixing」的段才能签 ⇒ 已被别人签过 ⇒ 不落盘 (幂等)
  ③ 写盘前 md5 复核 issue_log ⇒ 体检期间被并发改过 ⇒ rc=2 中止
  ④ 备份 + 原子替换 (os.replace)
  ⑤ **零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 不写任何分片 · 零外发**

★**签字依据的三个"不是自述" (★main 本机实跑★)**:
  · ★**生成器级 == 手改级 逐字节相同**: md5 `b2bdf8438ea29386e41474aec21a55c9` (三路同值:
    沙盒 S3 产物 / REPRO 手改版 / **main 自己用带补丁的生成器重跑一遍**)
  · ★**零行号位移**: S3 网表 vs S0 基线网表 ⇒ **只增 5 行, 删改 0 行** ⇒ 既有行号锚点零失配
  · ★**板面真的多了接地 land**: S0 板 5 件各 **1** 个 land ⇒ S3 板各 **2** 个 (main 自己解析 .kicad_pcb)
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
STAMP = "20261123_2015"
REF = "state/_apply_20261123_2015_cron775d_sign_iss366.py"

BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

# ★真源 + 生成器 (★零落表自证★)
TRUTH = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gen_netlist.py": "aff5a6d98f473c0d65720f653a75fa22",
    "state/gen_pcb_netlist_board.py": "e6e7e0b36003f0a129170f5172b1381a",
    "state/land_v_values.py": "4032aaf308d545179a6f8d8b7129c49d",
    "state/decision_truth.py": "28254f1d48fd48c17628693aaa3fe0b4",
}

SBX = os.path.join(PROJ, "tmp/iss366_sbx")
S3_NET = "b2bdf8438ea29386e41474aec21a55c9"
FIVE = ["C_KEY_PWR", "C_KEY_VM", "C_KEY_VP", "C_KEY_CAM", "R_BAT_DET_2"]

fails: list[str] = []
notes: list[str] = []


def md5(p: str) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run(cmd, cwd=PROJ):
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=900)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def check(name, cond, detail=""):
    if cond:
        print("  ✅ %s %s" % (name, detail))
        notes.append("✅ " + name)
    else:
        print("  ❌ %s %s" % (name, detail))
        fails.append(name)
    return cond


def board_land_counts(path):
    txt = open(path, encoding="utf-8").read()
    idxs = [m.start() for m in re.finditer(r'\n\t\(footprint ', txt)] + [len(txt)]
    out = {}
    for a, b in zip(idxs, idxs[1:]):
        blk = txt[a:b]
        m = re.search(r'\(property "Reference" "([^"]+)"', blk) or re.search(r'fp_text reference "([^"]+)"', blk)
        if not m:
            continue
        if m.group(1) in FIVE:
            out[m.group(1)] = len(re.findall(r'\(pad "([^"]*)"', blk))
    return out


def main() -> int:
    print("=" * 78)
    print("  ISS-366 签收体检 (main 本机实跑 · fail-closed)")
    print("=" * 78)

    # ① 板双证
    check("板 md5 未动", md5(BOARD) == BOARD_MD5, md5(BOARD))
    st = os.stat(BOARD)
    # ★mtime 必须带纳秒比对 (★秒级会把「同一秒内被改」漏掉★)
    def to_ns(s: str) -> int:
        import datetime as _dt
        date, _, rest = s.partition(" ")
        hms, _, frac = rest.partition(".")
        base = _dt.datetime.strptime(date + " " + hms, "%Y-%m-%d %H:%M:%S")
        return int(base.timestamp()) * 1000000000 + int((frac + "000000000")[:9])
    check("板 mtime 未动 (纳秒级)", st.st_mtime_ns == to_ns(BOARD_MTIME),
          "%d ns (期望 %d)" % (st.st_mtime_ns, to_ns(BOARD_MTIME)))
    mt = __import__("datetime").datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    check("板 size 未动", st.st_size == BOARD_SIZE, str(st.st_size))

    # ② 真源 + 生成器
    for rel, want in TRUTH.items():
        got = md5(os.path.join(PROJ, rel))
        check("真源未动 %s" % rel, got == want, got)

    # ③ 新闸
    rc, out = run([sys.executable, "HW/check_netlist_gnd_rows.py", "--selftest"])
    check("新闸 --selftest rc=0", rc == 0, "rc=%d" % rc)
    check("新闸 --selftest 7/7", "7/7" in out and "ALL TESTS PASS" in out)
    rc, out = run([sys.executable, "HW/check_netlist_gnd_rows.py"])
    check("新闸跑现行网表 rc=1 (预期红)", rc == 1, "rc=%d" % rc)
    missing = [r for r in FIVE if r not in out]
    check("新闸点名 5 件", not missing, "缺=%s" % (missing or "无"))

    # ④ 既有闸 3 道
    rc, _ = run([sys.executable, "HW/check_fp_truth_baseline.py"])
    check("既有闸 check_fp_truth_baseline rc=0", rc == 0, "rc=%d" % rc)
    rc, _ = run([sys.executable, "HW/check_fp_truth_land_swap.py", "--selftest"])
    check("既有闸 land_swap --selftest rc=0", rc == 0, "rc=%d" % rc)
    rc, _ = run([sys.executable, "HW/check_netlist_selfconsistency.py"])
    check("既有闸 check_netlist_selfconsistency rc=0", rc == 0, "rc=%d" % rc)

    # ⑤ 零挂链
    for f in ("state/gate_check.py", "state/daily_check.py"):
        p = os.path.join(PROJ, f)
        txt = open(p, encoding="utf-8").read()
        check("零挂链 %s" % f, "check_netlist_gnd_rows" not in txt)

    # ⑥ 交付物
    one = os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_NETLIST_ROW_FIX.md")
    gate = os.path.join(PROJ, "HW/check_netlist_gnd_rows.py")
    hand = os.path.join(PROJ, "HANDOFF/2026-11-23_hw-lead_ISS366_网表4行补行作业包.md")
    for p, n in ((one, "一页"), (gate, "新闸"), (hand, "交卷页")):
        check("交付物在盘 · %s" % n, os.path.exists(p) and os.path.getsize(p) > 4000,
              "%d B" % (os.path.getsize(p) if os.path.exists(p) else 0))
    lg = os.path.join(PROJ, "logs/iss366")
    n_log = len([f for f in os.listdir(lg)]) if os.path.isdir(lg) else 0
    check("留证 logs/iss366/ ≥8 件", n_log >= 8, "%d 件" % n_log)

    # ⑦ 交卷页 B 块 + 标准口径标题
    if os.path.exists(hand):
        ht = open(hand, encoding="utf-8").read()
        check("交卷页 B1~B6 齐全", all(("%s" % b) in ht for b in ("B1", "B2", "B3", "B4", "B5", "B6")))
        check("交卷页 B2 标准口径标题", "B2 · 验收标准自评" in ht)
        check("交卷页 B3 标准口径标题", "B3 · 证据分级" in ht)
        check("交卷页 B4 标准口径标题", "B4 · 接口取值声明" in ht)

    # ⑧ 分片键 (iss366 前缀)
    try:
        import yaml
        fr = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/hw.yaml"), encoding="utf-8"))
        art = [a for a in fr.get("artifacts", []) if "iss366" in str(a).lower()]
        ans = [a for a in fr.get("answers", []) if "iss366" in str(a).lower()]
        clm = [a for a in fr.get("interface_claims", []) if "iss366" in str(a).lower()]
        check("分片 artifacts 含 iss366 ≥1", len(art) >= 1, "%d 条" % len(art))
        check("分片 answers 含 iss366 ≥1", len(ans) >= 1, "%d 条" % len(ans))
        check("分片 interface_claims 含 iss366 ≥1", len(clm) >= 1, "%d 条" % len(clm))
    except Exception as e:                                    # noqa: BLE001
        check("分片读取", False, repr(e))

    # ⑨ ★生成器级复跑的三条硬证据 (★main 本机实跑, 不是抄 agent 报告★) ★
    gen3 = os.path.join(SBX, "S3/gen/gen_netlist.py")
    gt = open(gen3, encoding="utf-8").read() if os.path.exists(gen3) else ""
    check("沙盒 S3 生成器带 ISS-366 补丁", "独立 net=GND 接地行 (ISS-366)" in gt)
    s3n = os.path.join(SBX, "S3/HW/netlist_v1.csv")
    hd = os.path.join(SBX, "REPRO/S3_handedit_netlist_v1.csv")
    check("S3 网表 md5 == 手改级 md5 == %s" % S3_NET,
          os.path.exists(s3n) and os.path.exists(hd) and md5(s3n) == md5(hd) == S3_NET,
          "%s / %s" % (md5(s3n) if os.path.exists(s3n) else "-",
                       md5(hd) if os.path.exists(hd) else "-"))
    s0n = os.path.join(SBX, "S0/HW/netlist_v1.csv")
    if os.path.exists(s0n) and os.path.exists(s3n):
        a = open(s0n, encoding="utf-8").read().splitlines()
        b = open(s3n, encoding="utf-8").read().splitlines()
        added = len(b) - len(a)
        prefix_same = b[:len(a)] == a
        check("S3 vs S0 零行号位移 (只追加 5 行, 前段逐字节相同)", prefix_same and added == 5,
              "added=%d prefix_same=%s" % (added, prefix_same))
    b0 = board_land_counts(os.path.join(SBX, "S0/HW/sbx_board.kicad_pcb"))
    b3 = board_land_counts(os.path.join(SBX, "S3/HW/sbx_board.kicad_pcb"))
    check("板面 land 数 1⇒2 (5 件)",
          all(b0.get(r) == 1 and b3.get(r) == 2 for r in FIVE),
          "S0=%s S3=%s" % (b0, b3))

    # ⑩ gate_check (★最后跑, 因为它最慢★)
    rc, out = run([sys.executable, "state/gate_check.py"])
    check("gate_check rc=0", rc == 0, "rc=%d" % rc)
    check("gate_check Q1 = 18/18", "18/18" in out)

    print("-" * 78)
    if fails:
        print("★★ 体检红 %d 条 ⇒ 不签收 (fail-closed): %s" % (len(fails), fails))
        return 1

    # ⑪ 落台账 (★只认 status: fixing 才签⇒ 幂等★)
    before = md5(LOG)
    raw = open(LOG, encoding="utf-8").read()
    m = re.search(r"- id: ISS-366\n(.*?)(?=\n- id: |\Z)", raw, re.S)
    if not m:
        print("★★ 台账里找不到 ISS-366 段 ⇒ rc=2 不落盘")
        return 2
    seg = m.group(1)
    if "  status: fixing" not in seg:
        print("★ ISS-366 段不是 status: fixing ⇒ 已被人签过 ⇒ 幂等不落盘")
        return 0
    vr = ("✅ verified (★cron 775d9893 2026-11-23 20:1x main 本机独立复核 · 不抄 agent 报告★) "
          "⇒ 本单零写板 (板 md5 %s / mtime %s / %d B 逐字节未动) · 零落表 (网表/脚表/BOM/两生成器/"
          "land_v_values/decision_truth md5 全同) · 零改既有闸 (既有 3 道 rc=0) · 零挂链 "
          "(gate_check/daily_check grep=0) · 四件交付物在盘 (一页 %d B + 新闸 %d B + 交卷页 %d B + "
          "logs/iss366/ %d 件) · ★新闸 --selftest rc=0 7/7 · 跑现行网表 rc=1 精确点名 5 件 · "
          "gate_check rc=0 Q1 18/18 (hw-lead 6/6 · 交接单=本单交卷页) · ★★生成器级复跑三条硬证据 (main 本机实跑)★★: "
          "① 沙盒 S3 生成器级网表 == 手改级 == %s 逐字节相同 (三路同值) ② S3 vs S0 零行号位移 (只追加 5 行·删改 0 行) "
          "③ 板面 land 数 5 件各 1⇒2 ⇒ ★「不许手改生成物·要改改生成器并重跑」这条纪律被证明★ · "
          "★口径订正已登记: 「82 条」= 台账指纹口径 / 「25 条」= 规格页谓词口径 (双口径 S3 均 0 失配) · "
          "★任务书路径笔误已登记: state/check_netlist_selfconsistency.py 不存在 ⇒ 真身在 HW/ 下 · "
          "★6 件要 main 裁的事已登记成 needs_from (S1/S3 变体 / 同批或拆批 / DNP 补不补 / 新闸挂不挂 / "
          "路径笔误 / FP_TRUTH_BASELINE M6 断言同批更新) ⇒ 本单不代老板拍板 · 零外发" % (
        BOARD_MD5, BOARD_MTIME, BOARD_SIZE,
        os.path.getsize(one), os.path.getsize(gate), os.path.getsize(hand), n_log, S3_NET))

    new = seg.replace("  status: fixing", "  status: verified", 1)
    if "  verify_result:" in new:
        new = re.sub(r"^  verify_result: .*$", "  verify_result: %r" % (vr,), new, count=1, flags=re.M)
    else:
        new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
    if "  verify_date:" in new:
        new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
    else:
        new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
    if "  fix_ref:" in new:
        new = re.sub(r"^  fix_ref: .*$", "  fix_ref: '%s'" % REF, new, count=1, flags=re.M)
    else:
        new = new.rstrip("\n") + "\n  fix_ref: '%s'\n" % REF

    raw2 = raw[:m.start(1)] + new + raw[m.end(1):]

    now = md5(LOG)
    if now != before:
        print("★★ issue_log 在体检期间被并发改过 (md5 %s → %s) ⇒ rc=2 中止, 不落盘" % (before, now))
        return 2
    bak = LOG + ".bak_" + STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp." + STAMP
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw2)
    os.replace(tmp, LOG)
    print("✅ ISS-366 已签收 (status: verified) · 备份 %s" % os.path.basename(bak))
    return 0


if __name__ == "__main__":
    sys.exit(main())
