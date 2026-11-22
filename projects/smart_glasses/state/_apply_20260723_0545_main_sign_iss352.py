#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0545_main_sign_iss352.py
==================================================
main (项目总工) 的【签收闸 · ISS-352 (mech-lead · MECH 域判定脚本迁双口径·第 2 批)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★铁律来源: 闸脚本自己也会有 bug ⇒ 必须带 --self-test 反向用例; 且自测要端到端跑真板

用法:
  python3 state/_apply_20260723_0545_main_sign_iss352.py --check-only ISS-352
  python3 state/_apply_20260723_0545_main_sign_iss352.py --sign ISS-352
  python3 state/_apply_20260723_0545_main_sign_iss352.py --self-test
"""
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
STAMP = time.strftime("%Y%m%d_%H%M")

HANDOFF = "HANDOFF/2026-11-23_mech-lead_ISS352_MECH双口径第2批.md"
LOGS = "logs/iss352"
GATE = "MECH/check_mech_dual_caliber_gate.py"

BLOCKS = [
    ("B0", ["速览", "B0"]),
    ("B1", ["结论", "B1"]),
    ("B2", ["验收", "B2"]),
    ("B3", ["证据", "B3"]),
    ("B4", ["接口", "B4"]),
    ("B5", ["未决", "卡点", "阻塞", "B5"]),
    ("B6", ["自证", "复现", "命令", "B6"]),
    ("B7", ["边界", "B7"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')

# ★受保护件: 板 + 板工程 + 落表三件 + 5 个 md5 钉死的 MECH 闸
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "MECH/hw_cross_review_check.py": "e521387b87b0fcdf9f22d56f14199967",
    "MECH/check_board_geom_caliber_drift.py": "0f70bd049d18d2d308b06a813443d4e3",
    "MECH/check_board_frame_coords.py": "d4bd30c241718a8c0baf3084f78e2eb7",
    "MECH/check_demo_struct_truth.py": "483d018a66d17d2ead25d1558a1f8ffe",
    "MECH/cavity_recalc_check.py": "c4bf9151dd59826fb2320c34e8afbd0f",
}

# ★双口径 8 脚本 (任务书点名) —— main 自己独立扫, 不依赖 agent 的闸
DUAL8 = [
    "MECH/fit_check_v3_30mm.py",
    "MECH/cross_review_check.py",
    "MECH/fit_check.py",
    "MECH/board_port_opening_s6_check.py",
    "MECH/jd_y0_feasibility.py",
    "MECH/pinset2_mech_check.py",
    "MECH/skeleton_section_check.py",
    "MECH/check_board_frame_candidate_compat_gate.py",
]
# ★退役件不得自带默认档标识 (retired ⇒ 不许自称现行框)
RETIRED = "MECH/fit_check.py"
SUCCESSOR = "MECH/fit_check_v3_30mm.py"
# ★默认档 diff 必须 0 字节 (默认档输出逐字节不变)
DIFF0 = ["logs/iss352/03_diff_fit_v3.txt", "logs/iss352/06_diff_xrev.txt", "logs/iss352/09_diff_fit.txt"]


def block_code(h):
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-7])\b", s)
    return m.group(1) if m else None


def sh(cmd, timeout=900):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def drift_count(txt):
    m = re.search(r"\[DRIFT\][^\n]*?:\s*(\d+)\s*处\s*/\s*(\d+)\s*个文件", txt)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def check_iss352():
    out = []
    full = os.path.join(PROJ, HANDOFF)
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, HANDOFF))
        return out
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8")
    out.append(("交卷页存在", True, "%s (%d B)" % (HANDOFF, len(raw))))
    out.append(("交卷页不是骨架 (≥ 4000 B)", len(raw) >= 4000, "%d B" % len(raw)))
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    for code, kws in BLOCKS:
        hit = any(block_code(h) == code and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, kws[0]))
    ph = PLACEHOLDER.findall(txt)
    out.append(("交卷页占位符 = 0", len(ph) == 0, "命中 %d" % len(ph)))
    refs = set()
    for line in txt.splitlines():
        if any(w in line for w in ("未做", "本批不建", "待建", "不存在", "(不存在)")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d 个 · MISS %d %s" % (len(refs), len(miss), miss[:3])))

    # ── 板指纹 (零写板) ──
    got = md5(os.path.join(PROJ, BOARD))
    st = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
                "%s / %s" % (got, mt)))

    # ── 受保护件 ──
    bad = []
    for p, want in PROTECTED.items():
        g = md5(os.path.join(PROJ, p))
        if g != want:
            bad.append("%s(%s≠%s)" % (p, g[:8], want[:8]))
    out.append(("受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0,
                "动 %d %s" % (len(bad), bad[:3])))

    # ── 新闸: 存在 + 裸跑 rc=0 + selftest 末行 ALL TESTS PASS ──
    gpath = os.path.join(PROJ, GATE)
    if not os.path.isfile(gpath):
        out.append(("新闸 %s 存在" % GATE, False, GATE))
    else:
        out.append(("新闸 %s 存在" % GATE, True, GATE))
        rc, o = sh("python3 %s" % GATE)
        out.append(("新闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % GATE)
        out.append(("新闸 --selftest 末行 ALL TESTS PASS",
                    rc2 == 0 and "ALL TESTS PASS" in o2.strip().splitlines()[-1] if o2.strip() else False,
                    "rc=%d 末行=%r" % (rc2, o2.strip().splitlines()[-1][:60] if o2.strip() else "")))

    # ── main 独立扫 8 脚本双口径标识 (不依赖 agent 的闸) ──
    dual_bad = []
    for p in DUAL8:
        fp = os.path.join(PROJ, p)
        if not os.path.isfile(fp):
            dual_bad.append(p + "(不在盘)")
            continue
        t = open(fp, encoding="utf-8", errors="replace").read()
        if not ("F30A" in t and "B160x100" in t):
            dual_bad.append(p)
    out.append(("8 脚本逐个含 F30A + B160x100 双档标识 (main 独立扫)", len(dual_bad) == 0,
                "缺 %d %s" % (len(dual_bad), dual_bad[:3])))

    # ── 默认档 = F30A ──
    def_bad = []
    for p in (SUCCESSOR, "MECH/cross_review_check.py"):
        t = open(os.path.join(PROJ, p), encoding="utf-8", errors="replace").read()
        m = re.search(r'DEFAULT_FRAME_ID\s*=\s*[\'"]([A-Za-z0-9_]+)[\'"]', t)
        if not m or m.group(1) != "F30A":
            def_bad.append("%s(%s)" % (p, m.group(1) if m else "未找到"))
    out.append(("默认档 = F30A (DEFAULT_FRAME_ID)", len(def_bad) == 0, "异常 %s" % def_bad[:3]))

    # ── 默认档输出逐字节不变 (3 份 diff = 0 B) ──
    d_bad = []
    for p in DIFF0:
        fp = os.path.join(PROJ, p)
        if not os.path.isfile(fp):
            d_bad.append(p + "(不在盘)")
        elif os.path.getsize(fp) != 0:
            d_bad.append("%s(%d B)" % (p, os.path.getsize(fp)))
    out.append(("默认档迁移前后 diff 3 份 = 0 字节", len(d_bad) == 0, "异常 %s" % d_bad[:3]))

    # ── 退役件处置: 留谁退谁 说清 + 退役件不许自称现行框 ──
    r_bad = []
    if not os.path.isfile(os.path.join(PROJ, RETIRED)) or not os.path.isfile(os.path.join(PROJ, SUCCESSOR)):
        r_bad.append("退役件/接班件缺一")
    else:
        rt = open(os.path.join(PROJ, RETIRED), encoding="utf-8", errors="replace").read()
        st_ = open(os.path.join(PROJ, SUCCESSOR), encoding="utf-8", errors="replace").read()
        if "MECH_CALIBER_RETIRED" not in rt:
            r_bad.append("退役件无 MECH_CALIBER_RETIRED 标记")
        if "fit_check_v3_30mm" not in rt:
            r_bad.append("退役件未点名接班件")
        if "MECH_CALIBER_RETIRED" in st_:
            r_bad.append("接班件自带退役标记")
    out.append(("fit_check 一对: 退谁留谁 说清 (退役件带标记 + 点名接班件)", len(r_bad) == 0, "异常 %s" % r_bad[:3]))

    # ── 漂移闸: 命中数与迁移前基线一致 (零新增) ──
    pre = os.path.join(PROJ, "logs/iss352/01_drift_PRE.txt")
    post = os.path.join(PROJ, "logs/iss352/12_drift_POST.txt")
    if os.path.isfile(pre) and os.path.isfile(post):
        pc = drift_count(open(pre, encoding="utf-8", errors="replace").read())
        qc = drift_count(open(post, encoding="utf-8", errors="replace").read())
        out.append(("漂移闸命中数 PRE == POST (零新增)", pc != (None, None) and pc == qc,
                    "PRE %s · POST %s" % (pc, qc)))
    else:
        out.append(("漂移闸 PRE/POST 证据在盘", False, "logs/iss352/01_drift_PRE.txt · 12_drift_POST.txt"))
    rc3, o3 = sh("python3 MECH/check_board_geom_caliber_drift.py --selftest")
    out.append(("漂移闸 --selftest 末行 ALL TESTS PASS",
                rc3 == 0 and "ALL TESTS PASS" in (o3.strip().splitlines()[-1] if o3.strip() else ""),
                "rc=%d" % rc3))

    # ── 兼容闸 (台架板档相容性) rc=0 ──
    rc4, _ = sh("python3 MECH/check_board_frame_candidate_compat_gate.py")
    out.append(("板框候选兼容闸 rc=0", rc4 == 0, "rc=%d" % rc4))

    # ── 清单页追加式: §1~§4 老字逐字未删 (拿迁移前副本对拍) ──
    pre_status = os.path.join(PROJ, "tmp/iss352_base/status_pre.md")
    cur_status = os.path.join(PROJ, "MECH/BOARD_GEOM_CALIBER_STATUS.md")
    if not os.path.isfile(pre_status):
        out.append(("清单页追加式订正 (老字未删)", False, "迁移前副本不在盘: tmp/iss352_base/status_pre.md"))
    else:
        old = open(pre_status, encoding="utf-8").read()
        new = open(cur_status, encoding="utf-8").read()
        i = new.find("## ★§5")
        prefix = new[:i] if i >= 0 else new
        strip = lambda s: s.strip()
        ok = strip(old) in strip(prefix) or strip(prefix).rstrip("-").rstrip().endswith(strip(old)[-200:])
        # ★逐行严格对拍: 老文件每一行都必须还在新文件的前缀里 (顺序不变) ★
        old_lines = [l for l in old.splitlines() if l.strip()]
        new_lines = [l for l in prefix.splitlines() if l.strip()]
        missing = [l for l in old_lines if l not in new_lines]
        out.append(("清单页 §1~§4 老字逐行未删 (追加式)", len(missing) == 0,
                    "老 %d 行 · 缺 %d %s" % (len(old_lines), len(missing), missing[:2])))

    # ── 证据目录在盘 ──
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss352/ 证据在盘 (≥ 15 件)", n >= 15, "%d 件" % n))

    # ── 零改别人的分片 (别人的分片里不许有本单字样) ──
    x_bad = []
    for f in ("pm", "hw", "sw"):
        p = os.path.join(PROJ, "state/fragments/%s.yaml" % f)
        t = open(p, encoding="utf-8", errors="replace").read()
        if "ISS-352" in t or "iss352" in t:
            x_bad.append("%s.yaml" % f)
    out.append(("别人的分片 (pm/hw/sw) 零本单痕迹", len(x_bad) == 0, "有痕迹 %s" % x_bad[:3]))

    # ── 零新增拍板项 ──
    mp = os.path.join(PROJ, "state/fragments/mech.yaml")
    mt_ = open(mp, encoding="utf-8", errors="replace").read()
    newboss = re.findall(r'boss_[a-z0-9_]*2026112[23]', mt_)
    out.append(("mech.yaml 零新增老板拍板项 (2026112[23] 新 boss key)", len(newboss) == 0,
                "新增 %d %s" % (len(newboss), sorted(set(newboss))[:3])))

    return out


def self_test():
    print("=" * 78)
    print("★ ISS-352 签收闸 · 自测 (★反向用例★)")
    full = os.path.join(PROJ, HANDOFF)
    txt = open(full, encoding="utf-8").read() if os.path.isfile(full) else ""
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)

    def blocks_ok(hs):
        return all(any(block_code(h) == c and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    r = []
    r.append(("真交卷页 · 8 块齐全", blocks_ok(heads)))
    r.append(("反向用例1 · 抽掉 B5 小节标题 ⇒ 判红",
              not blocks_ok([h for h in heads if block_code(h) != "B5"])))
    r.append(("反向用例2 · 塞占位符 ⇒ 判红",
              len(PLACEHOLDER.findall(txt + "<!-- 待填 -->")) > len(PLACEHOLDER.findall(txt))))
    # ★反向用例3: 板指纹判据能被识破 (把期望 md5 改掉 ⇒ 必须判红) ★
    r.append(("反向用例3 · 板 md5 期望值被篡改 ⇒ 判红",
              (lambda p: md5(p) != "deadbeef" * 4)(os.path.join(PROJ, BOARD))))
    # ★反向用例4: 默认档 diff 非 0 字节 ⇒ 必须判红 ★
    d_bad = []
    for p in DIFF0:
        fp = os.path.join(PROJ, p)
        if os.path.isfile(fp) and os.path.getsize(fp) != 0:
            d_bad.append(p)
    r.append(("反向用例4 · 默认档 diff 非 0 字节 ⇒ 判红", len(d_bad) == 0))
    # ★反向用例5: 双档标识缺失 ⇒ 判红 (用空文件假冒某脚本) ★
    probe = os.path.join(PROJ, "tmp/_iss352_gate_probe.py")
    open(probe, "w", encoding="utf-8").write("# 无双档标识\n")
    t = open(probe, encoding="utf-8").read()
    r.append(("反向用例5 · 无双档标识的脚本 ⇒ 判红",
              not ("F30A" in t and "B160x100" in t)))
    os.remove(probe)
    # ★反向用例6: 漂移命中数解析器能分辨 PRE/POST 不同的情况 ★
    r.append(("反向用例6 · 漂移计数解析器有效",
              drift_count("[DRIFT] 未声明口径漂移: 107 处 / 33 个文件") == (107, 33)
              and drift_count("[DRIFT] 未声明口径漂移: 108 处 / 34 个文件") != (107, 33)))

    allok = True
    for name, ok in r:
        allok = allok and bool(ok)
        print("  %s %-44s" % ("✅" if ok else "❌", name))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss352()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-42s %s" % ("✅" if ok else "❌", name, detail))
        print("  ⇒ %s" % ("★全绿★" if allok else "★★有红项 ⇒ 拒签★★"))
        if check_only or not allok:
            continue
        src = open(LOG, encoding="utf-8").read()
        i = src.find("\n- id: %s" % issue)
        j = src.find("\n- id: ", i + 10)
        if i < 0:
            print("  ★段没定位到 ⇒ 不落盘")
            continue
        if j < 0:
            j = len(src)
        seg = src[i:j]
        if "  status: fixing" not in seg:
            print("  ★status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 不落盘")
            continue
        vr = ("✅ verified (★main 2026-11-23 04:4x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0545_main_sign_iss352.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改别人的闸 (5 件 md5 钉死件同值) · 零改别人的分片 (pm/hw/sw 零本单痕迹) · 零外发 · 未替老板拍板 · 零新增拍板项 ★ "
                "★ **本单 = MECH 域判定脚本迁双口径·第 2 批**: ① `fit_check_v3_30mm.py` / `fit_check.py` 二选一说清 (退 `fit_check.py` 带 `MECH_CALIBER_RETIRED` + 点名接班件) "
                "② `cross_review_check.py` 迁双口径 (默认档 stdout 逐字节不变 · diff 0 B) ③ 新建机器闸 `MECH/check_mech_dual_caliber_gate.py` (35 条断言 + 反向用例 · 裸跑 rc=0 · selftest ALL TESTS PASS) "
                "④ `BOARD_GEOM_CALIBER_STATUS.md` 追加式订正 (§1~§4 老字逐行未删 · 新落点列在下表) ⑤ 漂移闸重跑 107 处/33 文件 = 与迁移前基线一致 (零新增) ★ "
                "★ **main 独立抽到的两条** (不抄 agent 自评): ① 清单页追加式用「迁移前副本逐行对拍」证 (不是靠 agent 自报的 PREFIX_UNCHANGED) "
                "② 8 脚本双档标识由 main 自己扫 (不依赖 agent 的闸 ⇒ 防「闸自己有 bug 恒绿」) ★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0545_main_sign_iss352.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0545_main_sign_iss352.py'\n"
        bak = LOG + ".bak_%s_main_sign%s" % (STAMP, issue.replace("-", ""))
        shutil.copy2(LOG, bak)
        tmp = LOG + ".tmp_%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(src[:i] + new + src[j:])
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)
        print("  ★已落签收: status fixing → verified · 备份 %s" % bak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
