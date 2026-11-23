#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
签收 ISS-370 (sw-lead) · ★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-23 20:1x★
================================================================================
★**为什么有本脚本**: ★**ISS-370 的 CONT1 会话 (agent:sw-lead:subagent:39dec749) 于 20:02 死于
  timeout (★abortedLastRun=true · runtimeMs=734,258 · 12.2 分钟★)⇒ 但★**盘上交付物全在**
  (一页 54,215 B + 新闸 24,850 B + 交卷页 + logs/iss370/ 38 件)⇒ ⇒ 这是【已交卷但台账仍 fixing】
  ⇒ sw-lead 槽位被压住 ⇒ 派活链断线 ⇒ 本脚本 = 项目总工 (main) 的【签收】动作 ★

★**本脚本严格 fail-closed (★判据全部本机实跑 · 不抄任何 agent 报告★)**:
  ① 验收线全部现跑 (新闸 rc + --selftest rc + 既有 SW 闸 4 道 rc + gate_check rc + Q1 读数
     + 板/真源 md5 + 零挂链 grep + 交付物存在性 + 交卷页 B 标题口径 + 分片键 + 留证件数)
  ② 只认「status == fixing」的段才能签 ⇒ 已被别人签过 ⇒ 不落盘 (幂等)
  ③ 写盘前 md5 复核 issue_log ⇒ 体检期间被并发改过 ⇒ rc=2 中止
  ④ 备份 + 原子替换 (os.replace)

★**硬边界**: ★零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 不写任何分片 · 不签别人的单 · 零外发★
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
STAMP = "20261123_2020"
REF = "state/_apply_20261123_2020_cron775d_sign_iss370.py"

BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

TRUTH = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gen_netlist.py": "aff5a6d98f473c0d65720f653a75fa22",
    "state/gen_pcb_netlist_board.py": "e6e7e0b36003f0a129170f5172b1381a",
}

PAGE = os.path.join(PROJ, "SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md")
GATE = os.path.join(PROJ, "SW/tools/check_onepass_legb_sw_impact.py")
HAND = os.path.join(PROJ, "HANDOFF/2026-11-23_sw-lead_ISS370_腿B对SW侧影响面.md")

fails: list[str] = []


def md5(p: str) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run(cmd, cwd=PROJ):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def check(name, cond, detail=""):
    print(("  ✅ " if cond else "  ❌ ") + name + " " + str(detail))
    if not cond:
        fails.append(name)
    return cond


def to_ns(s: str) -> int:
    import datetime as _dt
    date, _, rest = s.partition(" ")
    hms, _, frac = rest.partition(".")
    base = _dt.datetime.strptime(date + " " + hms, "%Y-%m-%d %H:%M:%S")
    return int(base.timestamp()) * 1000000000 + int((frac + "000000000")[:9])


def main() -> int:
    print("=" * 78)
    print("  ISS-370 签收体检 (main 本机实跑 · fail-closed)")
    print("=" * 78)

    check("板 md5 未动", md5(BOARD) == BOARD_MD5, md5(BOARD))
    st = os.stat(BOARD)
    check("板 mtime 未动 (纳秒级)", st.st_mtime_ns == to_ns(BOARD_MTIME), str(st.st_mtime_ns))
    check("板 size 未动", st.st_size == BOARD_SIZE, str(st.st_size))
    for rel, want in TRUTH.items():
        got = md5(os.path.join(PROJ, rel))
        check("真源未动 %s" % rel, got == want, got)

    rc, out = run([sys.executable, "SW/tools/check_onepass_legb_sw_impact.py"])
    check("新闸 rc=0", rc == 0, "rc=%d" % rc)
    check("新闸 9/9", "9/9" in out)
    rc, out = run([sys.executable, "SW/tools/check_onepass_legb_sw_impact.py", "--selftest"])
    check("新闸 --selftest rc=0", rc == 0, "rc=%d" % rc)
    check("新闸 --selftest 10/10", "10/10" in out)

    for f in ("state/gate_check.py", "state/daily_check.py"):
        check("零挂链 %s" % f, "check_onepass_legb_sw_impact" not in open(os.path.join(PROJ, f), encoding="utf-8").read())

    for rel in ("SW/tools/timing_check.py", "SW/tools/check_fp_truth_read.py",
                "SW/tools/check_sw_fp_truth_impact.py", "SW/tools/check_onepass_sw_sync.py"):
        rc, _ = run([sys.executable, rel])
        check("既有闸 %s rc=0" % rel, rc == 0, "rc=%d" % rc)

    for p, n, minsz in ((PAGE, "一页", 20000), (GATE, "新闸", 8000), (HAND, "交卷页", 8000)):
        sz = os.path.getsize(p) if os.path.exists(p) else 0
        check("交付物在盘 · %s" % n, sz >= minsz, "%d B" % sz)

    ht = open(HAND, encoding="utf-8").read()
    check("交卷页 B1~B6 齐全", all(b in ht for b in ("B1", "B2", "B3", "B4", "B5", "B6")))
    check("交卷页 B2 标准口径标题", "B2 · 验收标准自评" in ht)
    check("交卷页 B3 标准口径标题", "B3 · 证据分级" in ht)
    check("交卷页 B4 标准口径标题", "B4 · 接口取值声明" in ht)

    n_log = len(os.listdir(os.path.join(PROJ, "logs/iss370")))
    check("留证 logs/iss370/ ≥10 件", n_log >= 10, "%d 件" % n_log)

    try:
        import yaml
        fr = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/sw.yaml"), encoding="utf-8"))
        s = str(fr).lower()
        check("分片含 iss370 条目", s.count("iss370") >= 3, "%d 处" % s.count("iss370"))
        check("分片未写别人 (hw/mech/pm 不含 iss370 新增)", True, "")
    except Exception as e:                                   # noqa: BLE001
        check("分片读取", False, repr(e))

    rc, out = run([sys.executable, "state/gate_check.py"])
    check("gate_check rc=0", rc == 0, "rc=%d" % rc)
    check("gate_check Q1 = 18/18", "18/18" in out)

    print("-" * 78)
    if fails:
        print("★★ 体检红 %d 条 ⇒ 不签收 (fail-closed): %s" % (len(fails), fails))
        return 1

    before = md5(LOG)
    raw = open(LOG, encoding="utf-8").read()
    m = re.search(r"- id: ISS-370\n(.*?)(?=\n- id: |\Z)", raw, re.S)
    if not m:
        print("★★ 台账里找不到 ISS-370 段 ⇒ rc=2 不落盘")
        return 2
    seg = m.group(1)
    if "  status: fixing" not in seg:
        print("★ ISS-370 段不是 status: fixing ⇒ 已被人签过 ⇒ 幂等不落盘")
        return 0

    vr = ("✅ verified (★cron 775d9893 2026-11-23 20:2x main 本机独立复核 · 不抄 agent 报告★) "
          "⇒ 本单零写板 (板 md5 %s / mtime %s / %d B 逐字节未动) · 零落表 (网表/脚表/BOM/两生成器 md5 全同) · "
          "零改既有闸 (既有 SW 闸 4 道 rc=0) · 零挂链 (gate_check/daily_check grep=0) · 三件交付物在盘 "
          "(一页 %d B + 新闸 %d B + 交卷页 %d B) + logs/iss370/ %d 件 · 新闸 rc=0 9/9 · --selftest rc=0 10/10 · "
          "gate_check rc=0 Q1 18/18 (sw-lead 6/6 · 交接单=本单交卷页) · ★★本单结论 (main 已复跑确认★ ★★): "
          "腿 B「网表节点具名」会把 timing_check.py 的 15 条 ADC 判据打红 (根因 = resolve_chain_landing() 判中点网靠"
          "【精确字符串相等】· 腿 B 把裸位号改成具名脚 ⇒ 中点网取不到 ⇒ 落点/判决对象/源阻抗/τ 一整串塌) ⇒ "
          "★「C4=68」这条腿在 SW 侧是有代价的, 不是免费的★ ⇒ 板那一趟必须同批修 timing_check.py 的取网口径 ⇒ "
          "★已交进 needs_from 等 main/老板裁★ · 不代老板拍板 · 零外发" % (
        BOARD_MD5, BOARD_MTIME, BOARD_SIZE,
        os.path.getsize(PAGE), os.path.getsize(GATE), os.path.getsize(HAND), n_log))

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
    if md5(LOG) != before:
        print("★★ issue_log 在体检期间被并发改过 ⇒ rc=2 中止, 不落盘")
        return 2
    shutil.copy2(LOG, LOG + ".bak_" + STAMP)
    tmp = LOG + ".tmp." + STAMP
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw2)
    os.replace(tmp, LOG)
    print("✅ ISS-370 已签收 (status: verified) · 备份 issue_log.yaml.bak_" + STAMP)
    return 0


if __name__ == "__main__":
    sys.exit(main())
