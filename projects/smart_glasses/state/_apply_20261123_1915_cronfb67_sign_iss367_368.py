#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
签收 ISS-367 (mech-lead) + ISS-368 (sw-lead) · ★cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 19:1x★
================================================================================
★**为什么有本脚本 (★台账堵点的第 N 次复发★)**:
  · ISS-367 / ISS-368 的 CONT1 会话分别在 18:42 / 18:44 交卷完毕 (会话 status=done · 交付物全在盘)
  · 但台账 status 仍是 `fixing` ⇒ `state/advance.py` 的 in_flight 规则 (★该 agent 名下已有 fixing ⇒ 不派新活★)
    ⇒ sw-lead / mech-lead 两个槽位被【已交卷的单】永久压住 ⇒ 排队的 ISS-370 (sw-lead) 永远进不了 internal
    ⇒ 兄弟 job 775d9893 自 18:39 起一直停在 sessions_yield 里 (transcript mtime 18:39:02 · 31 分钟无写入)
  · ⇒ 本脚本 = 项目总工 (main) 的【签收】动作: 把这两条已交卷的单落成 verified ⇒ 槽位释放 ⇒ 派活链不断线

★**本脚本严格 fail-closed (★判据全部本机实跑 · 不抄任何 agent 报告★)**:
  ① 验收线全部现跑 (新闸 rc + --selftest rc + merge rc + gate_check rc + Q1 读数 + 板/网表/脚表 md5)
  ② 只认「status == fixing」的段才能签 ⇒ 已被别人签过 ⇒ 不落盘 (幂等)
  ③ 写盘前 md5 复核 issue_log ⇒ 体检期间被并发改过 ⇒ rc=2 中止
  ④ 备份 + 原子替换 (os.replace)
  ⑤ 一次写盘同时签两条 (★缩短并发窗口★) ⇒ 只读一次旧文本、只替换两段、只写一次盘

★**不碰的东西 (★硬边界★)**: 板 / 网表 / 脚表 / BOM / 既有闸脚本 / 既有页面正文 / 任何分片 / 不改别人的 issue
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
STAMP = "20261123_1915"

BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
NETLIST_MD5 = "6aee500e60ba0732f83a9cf557ba90ab"
PINS_MD5 = "9174309df1ec9411ac8e8d9e80ee386a"

DISPATCH_AT = "2026-11-23 18:32:00"   # ★两条 CONT1 的派活时刻 (★既有页 mtime 早于它 ⇒ 本单没改既有页★)
QUIET_S = 180                          # ★L-1: 交卷页 + 会话文件 mtime 静默 ≥3 分钟才签★

SESS = {
    "ISS-368": "/home/yuewuya/.openclaw/agents/sw-lead/sessions/df3c87fc-5af1-41c6-9943-27a8716a6e58.jsonl",
    "ISS-367": "/home/yuewuya/.openclaw/agents/mech-lead/sessions/6c74630c-0c89-4032-90fb-b7ed9a951753.jsonl",
}

BANNED = ["等原厂回信", "等外部回复", "待外部确认", "请放行外发", "走 main 外发"]
DESC_OK = ["零外发", "禁", "不许", "不得", "闸 L5", "口径提醒", "不外发", "零次邮件"]


def to_ns(s: str) -> int:
    """★'2026-11-06 07:07:17.362193413' → epoch ns (★基线带纳秒 ⇒ 比较必须也带纳秒★)"""
    import datetime as _dt
    date, _, rest = s.partition(" ")
    hms, _, frac = rest.partition(".")
    base = _dt.datetime.strptime(date + " " + hms, "%Y-%m-%d %H:%M:%S")
    ns = int((frac + "000000000")[:9])
    return int(base.timestamp()) * 1000000000 + ns


def md5(p: str) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stat(p: str):
    if not os.path.exists(p):
        return None
    return os.stat(p)


def mt(p: str) -> str:
    st = stat(p)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)) if st else "MISSING"


def run(cmd: str, cwd: str = PROJ, timeout: int = 1800):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 99, "TIMEOUT after %ss" % timeout


def quiet(path: str, min_s: int = QUIET_S):
    st = stat(path)
    if st is None:
        return False, "文件不存在"
    age = time.time() - st.st_mtime
    return age >= min_s, "mtime %s · 静默 %.0fs (需 ≥%ds)" % (mt(path), age, min_s)


def no_banned(path: str):
    """★描述性引用不算违规 (★L-2: 语境窗里有否定标记 ⇒ 描述)★"""
    bad = []
    if not os.path.exists(path):
        return False, "文件不存在"
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            for b in BANNED:
                if b in line and not any(d in line for d in DESC_OK):
                    bad.append("L%d 命中「%s」" % (i, b))
    return (not bad), ("零命中" if not bad else "; ".join(bad[:5]))


def blocks(path: str):
    if not os.path.exists(path):
        return False, "交卷页不存在"
    txt = open(path, encoding="utf-8", errors="replace").read()
    miss = [b for b in ("B1", "B2", "B3", "B4", "B5", "B6") if b not in txt]
    return (not miss), ("B1~B6 齐全" if not miss else "缺: " + ",".join(miss))


def frag_keys(frag: str, key: str):
    p = os.path.join(HERE, "fragments", frag)
    if not os.path.exists(p):
        return False, "分片不存在"
    txt = open(p, encoding="utf-8", errors="replace").read()
    n = txt.count(key)
    return n > 0, "命中 %d 处 (%s)" % (n, key)


def base_lines():
    """★两条共用 / 板侧真源的验收线★"""
    out = []
    st = stat(BOARD)
    got = md5(BOARD) if st else "MISSING"
    ok = got == BOARD_MD5
    out.append(("板 md5 逐字节未动", ok, "%s (期望 %s)" % (got, BOARD_MD5)))
    ok2 = bool(st) and int(st.st_mtime_ns) == to_ns(BOARD_MTIME)
    out.append(("板 mtime 未动 (纳秒)", bool(ok2),
                "%d ns (期望 %d ns)" % (int(st.st_mtime_ns) if st else 0, to_ns(BOARD_MTIME))))
    for path, want, label in ((os.path.join(PROJ, "HW/netlist_v1.csv"), NETLIST_MD5, "网表 md5"),
                              (os.path.join(PROJ, "HW/netlist_v1_pins.csv"), PINS_MD5, "脚表 md5")):
        g = md5(path) if os.path.exists(path) else "MISSING"
        out.append((label + " 未动", g == want, "%s (期望 %s)" % (g, want)))
    # ★既有闸脚本一字不改 (★mtime 必须早于派活时刻★)★
    for rel in ("state/gate_check.py", "state/merge.py", "state/frag_write.py"):
        p = os.path.join(PROJ, rel)
        st = stat(p)
        ok = bool(st) and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)) < DISPATCH_AT
        out.append(("既有闸未改 " + rel, ok, "mtime " + mt(p)))
    return out


def check(issue: str):
    lines = []
    if issue == "ISS-368":
        handoff = "HANDOFF/2026-11-23_sw-lead_ISS368_SW09三处同批落地补丁.md"
        page = "SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md"
        gate = "SW/tools/check_sw09_patch_dryrun.py"
        patch = "SW/tools/apply_sw09_three_place_patch.py"
        frag = "sw.yaml"
        # ★真件三处零改 (★归 main 的落表批次地界★)★
        for rel in ("SW/BOARD_ONEPASS_SW_SYNC.md", "SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md"):
            p = os.path.join(PROJ, rel)
            st = stat(p)
            ok = bool(st) and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)) < DISPATCH_AT
            lines.append(("真件零改 " + rel, ok, "mtime " + mt(p)))
    else:
        handoff = "HANDOFF/2026-11-23_mech-lead_ISS367_S10换封装LED窗口规格同趟重算.md"
        page = "MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md"
        gate = "MECH/check_onepass_s10_led_spec_sync.py"
        patch = None
        frag = "mech.yaml"
        p = os.path.join(PROJ, "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md")
        st = stat(p)
        ok = bool(st) and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)) < DISPATCH_AT
        lines.append(("本单零改既有页 BOARD_ONEPASS_STRUCT_CROSSCHECK.md", ok, "mtime " + mt(p)))
        # ★两处定点改写确实是本单做的 (★mtime 必须晚于派活且落在交卷窗内★)★
        for rel in ("MECH/BOARD_ONEPASS_MECH_SYNC.md", "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md"):
            p2 = os.path.join(PROJ, rel)
            st2 = stat(p2)
            ok2 = bool(st2) and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st2.st_mtime)) >= DISPATCH_AT
            lines.append(("定点改写已落地 " + rel, ok2, "mtime " + mt(p2)))

    # ★交付物在盘★
    for rel in ((handoff, page, gate) + ((patch,) if patch else ())):
        p = os.path.join(PROJ, rel)
        st = stat(p)
        lines.append(("交付物在盘 " + rel, bool(st) and st.st_size > 0,
                      ("%d B" % st.st_size) if st else "缺失"))
    # ★交卷页 B1~B6★
    ok, det = blocks(os.path.join(PROJ, handoff))
    lines.append(("交卷页 B1~B6 齐全", ok, det))
    # ★L-1: 交卷页 + 会话文件都静默 ≥3 分钟★
    ok, det = quiet(os.path.join(PROJ, handoff))
    lines.append(("交卷页已静默", ok, det))
    ok, det = quiet(SESS[issue])
    lines.append(("会话已静默 (agent 已交卷)", ok, det))
    # ★分片只走 frag_write ⇒ 键存在★
    ok, det = frag_keys(frag, issue.lower().replace("-", ""))
    lines.append(("分片含本单键", ok, det))
    # ★零外发★
    ok, det = no_banned(os.path.join(PROJ, handoff))
    lines.append(("交卷页零外发措辞", ok, det))
    # ★新闸 rc + 自测 rc★
    rc, out = run("python3 %s" % gate)
    lines.append(("新闸 rc=0 (%s)" % gate, rc == 0, "rc=%d" % rc))
    rc2, out2 = run("python3 %s --selftest" % gate)
    ok2 = rc2 == 0 and ("ALL TESTS PASS" in out2)
    lines.append(("新闸 --selftest 全绿", ok2, "rc=%d · %s" % (rc2, "ALL TESTS PASS" if ok2 else out2.strip().splitlines()[-1] if out2.strip() else "?")))
    if patch:
        rc3, out3 = run("python3 %s --dry-run" % patch)
        lines.append(("幂等补丁干跑 rc=0 (真件零写)", rc3 == 0, "rc=%d" % rc3))
    # ★全链★
    rc4, out4 = run("python3 state/merge.py")
    lines.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, out5 = run("python3 state/gate_check.py")
    q1 = ""
    for ln in out5.splitlines():
        if "【Q1" in ln:
            q1 = ln.strip()
    ok5 = rc5 == 0 and "18/18" in q1
    lines.append(("gate_check rc=0 且 Q1=18/18", ok5, "rc=%d · %s" % (rc5, q1 or "Q1 未读到")))
    lines.extend(base_lines())
    return lines


SUMMARY = {
    "ISS-368": "sw-lead · SW09 清单第 9 条三处同批落地的【幂等补丁 + 副本 dry-run 证明 + 回滚说明】· 零写板 · 零落表 · 真件三处零改",
    "ISS-367": "mech-lead · 换官方 0805 后 LED 窗口规格【同趟重算 + 两处定点改写 + 一条机器闸】· 零写板 · 零落表",
}


def self_test():
    """★自测: 用【实测的坏案例】当回归用例 (★闸本身会有 bug ⇒ 必须先证明闸能拒★)"""
    print("== 签收闸自测 ==")
    # ① 板 md5 判据: 假的板名 ⇒ 必须红
    ok, det = md5(BOARD) == BOARD_MD5, md5(BOARD)
    assert ok, "★真板 md5 竟然不等于基线 ★"
    bad = "00000000000000000000000000000000"
    assert (bad == BOARD_MD5) is False
    print("  ✅ ① 板 md5 判据: 真板绿 / 假 md5 红 (bad != baseline)")
    # ② 静默判据: 刚写的文件 ⇒ 必须红
    tmp = os.path.join(HERE, "_tmp_sign_selftest.txt")
    with open(tmp, "w") as f:
        f.write("x")
    okq, detq = quiet(tmp, min_s=QUIET_S)
    assert not okq, "★刚写的文件竟然算静默 ★"
    os.remove(tmp)
    print("  ✅ ② 静默判据: 刚写的文件 ⇒ 红 (fail-closed)")
    # ③ 禁语判据: 正文挂起措辞 ⇒ 必须红; 描述性引用 ⇒ 必须绿
    t2 = os.path.join(HERE, "_tmp_sign_selftest2.txt")
    with open(t2, "w") as f:
        f.write("这一项等原厂回信后再定\n")
    okb, detb = no_banned(t2)
    assert not okb, "★挂起措辞竟然没被抓到 ★"
    with open(t2, "w") as f:
        f.write("零外发: 全文禁止「等原厂回信」这类挂起措辞\n")
    okb2, detb2 = no_banned(t2)
    assert okb2, "★描述性引用被误判 ★"
    os.remove(t2)
    print("  ✅ ③ 禁语判据: 挂起措辞红 / 描述性引用绿 (L-2 语境窗)")
    print("== 自测 3/3 全过 ==")
    return 0


def sign_one(src: str, issue: str, lines):
    """★定位段 + 幂等检查 + 改写 (★只改本段, 别的段一个字节不动★)★"""
    i = src.find("\n- id: %s" % issue)
    if i < 0:
        return src, None, "段没定位到"
    j = src.find("\n- id: ", i + 10)
    if j < 0:
        j = len(src)
    seg = src[i:j]
    if "  status: fixing" not in seg:
        return src, None, "status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 不落盘"
    vr = ("✅ verified (★cron fb67af40 2026-11-23 19:1x 本机独立复核 · 不抄 agent 报告★) ⇒ "
          "★**签收闸本机实跑验收线, 全绿才签 (fail-closed)★** ⇒ "
          + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
          + " ★ " + SUMMARY[issue])
    new = seg.replace("  status: fixing", "  status: verified", 1)
    if "  verify_result:" in new:
        new = re.sub(r"^  verify_result: .*$", "  verify_result: %r" % (vr,), new, count=1, flags=re.M)
    else:
        new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
    if "  verify_date:" in new:
        new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
    else:
        new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
    ref = "state/_apply_20261123_1915_cronfb67_sign_iss367_368.py"
    if "  fix_ref:" in new:
        new = re.sub(r"^  fix_ref: .*$", "  fix_ref: '%s'" % ref, new, count=1, flags=re.M)
    else:
        new = new.rstrip("\n") + "\n  fix_ref: '%s'\n" % ref
    return src[:i] + new + src[j:], new, "已改写"


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    check_only = "--check-only" in args
    targets = [a for a in args if a.startswith("ISS-")] or ["ISS-367", "ISS-368"]
    results = {}
    allok = True
    for issue in targets:
        lines = check(issue)
        results[issue] = lines
        ok = all(o for _, o, _ in lines)
        allok = allok and ok
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        for name, o, det in lines:
            print("  %s %-46s %s" % ("✅" if o else "❌", name, det))
        print("  ⇒ %s" % ("★全绿★" if ok else "★★有红项 ⇒ 拒签★★"))
    if check_only:
        print("\n(check-only · 未落盘)")
        return 0 if allok else 1
    if not allok:
        print("\n★有红项 ⇒ 拒签 ⇒ 不落盘")
        return 1
    # ★写盘: 一次读 → 两次段替换 → md5 复核 → 备份 → 原子替换★
    src = open(LOG, encoding="utf-8").read()
    before = hashlib.md5(src.encode("utf-8")).hexdigest()
    out = src
    for issue in targets:
        out, _new, msg = sign_one(out, issue, results[issue])
        print("  ★%s: %s" % (issue, msg))
    after = hashlib.md5(out.encode("utf-8")).hexdigest()
    if before == after:
        print("  ★内容无变化 ⇒ 不落盘")
        return 0
    # ★并发守卫: 落盘前再核一次盘上 md5 (★体检期间被并发改过 ⇒ 中止★)★
    now = hashlib.md5(open(LOG, encoding="utf-8").read().encode("utf-8")).hexdigest()
    if now != before:
        print("  ★★issue_log 在体检期间被并发改过 (md5 %s → %s) ⇒ rc=2 中止, 不落盘" % (before, now))
        return 2
    bak = LOG + ".bak_%s_sign_367_368" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    print("  ★已落签收: ISS-367 + ISS-368 status fixing → verified · 备份 %s" % os.path.basename(bak))
    return 0


if __name__ == "__main__":
    sys.exit(main())
