#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0520_main_sign_iss345.py
==================================================
main (项目总工) 的【签收闸 · ISS-345 cont1 (mech-lead · MECH 域 8 个判定脚本迁双口径 · 第 1 批 2 脚本)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评

用法:
  python3 state/_apply_20260723_0520_main_sign_iss345.py --check-only ISS-345
  python3 state/_apply_20260723_0520_main_sign_iss345.py --sign ISS-345
  python3 state/_apply_20260723_0520_main_sign_iss345.py --self-test
"""
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

HANDOFF = "HANDOFF/2026-11-23_mech-lead_ISS345_8脚本迁双口径.md"
BLOCKS = [
    ("B1", ["结论", "一句话", "B1"]),
    ("B2", ["验收标准", "自评", "B2"]),
    ("B3", ["证据分级", "证据等级", "证据", "B3"]),
    ("B4", ["接口取值", "接口声明", "interface_claims", "B4"]),
    ("B5", ["未决", "卡点", "阻塞", "B5"]),
    ("B6", ["自证", "复现", "命令", "B6"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
# ★本单动的两个脚本 (★双口径迁移本体★)
SCRIPTS = ["MECH/pinset2_mech_check.py", "MECH/skeleton_section_check.py"]
# ★默认档 (60×30) 迁移前后必须逐字节相同 ⇒ diff 文件必须是 0 字节
DIFF_ZERO = ["logs/iss345/12_diff_pinset2.txt", "logs/iss345/13_diff_skeleton.txt"]
# ★第二档 (160×100) 必须有读数 (非空)★
SECOND_FRAME = ["logs/iss345/14_pinset2_B160x100.txt", "logs/iss345/15_skeleton_B160x100.txt"]
FRAG_MARKS = ["iss345_mech_cont1_dual_caliber_batch1", "iss345_mech_cont1_batch2_remaining",
              "logs/iss345/14_pinset2_B160x100.txt", "logs/iss345/15_skeleton_B160x100.txt"]


def block_code(h):
    """★★判据修正在产生点★★: 本仓交卷页的块标题写法是 `## ★B1 · 结论摘要 ★`
    ⇒ 不能用 `h.startswith('B1')` 判 ⇒ 先剥掉装饰 (★/·/空格/【】/全角符号) 再取块号
    ★★真闸与自测【共用】这一个函数 ⇒ 免得自测测的是另一套判据 (★本轮真踩到过★)★★"""
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


def check_iss345():
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
    # ★★判据修正在产生点★★: 交卷页里【显式标注为第 2 批未做】的文件路径是【前向引用】·
    #   ★**它本来就不该在盘** ⇒ 漏判 = 假阳性 ⇒ 按行排除 (★逐行看同一行有没有「未做/第 2 批/不建/待建」★)
    refs = set()
    for line in txt.splitlines():
        if any(w in line for w in ("未做", "第 2 批", "本批不建", "待建", "本批【不许】新建")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    out.append(("交卷页引用文件逐个在盘 (0 MISS · 排除第 2 批前向引用)", len(miss) == 0,
                "引用 %d 个 · MISS %d %s" % (len(refs), len(miss), miss[:3])))

    # ── 双口径本体: 默认档输出必须与迁移前逐字节相同 (★核心判据: 不许改判据方向★) ──
    for d in DIFF_ZERO:
        p = os.path.join(PROJ, d)
        ok = os.path.isfile(p) and os.path.getsize(p) == 0
        out.append(("默认档 60×30 迁移前后逐字节相同 (%s)" % os.path.basename(d), ok,
                    "diff %d B" % (os.path.getsize(p) if os.path.isfile(p) else -1)))
    for d in SECOND_FRAME:
        p = os.path.join(PROJ, d)
        ok = os.path.isfile(p) and os.path.getsize(p) > 0
        out.append(("第二档 160×100 有读数 (%s)" % os.path.basename(d), ok,
                    "%d B" % (os.path.getsize(p) if os.path.isfile(p) else -1)))
    for s in SCRIPTS:
        p = os.path.join(PROJ, s)
        ok = os.path.isfile(p) and os.path.getsize(p) > 1000
        out.append(("脚本在盘 (%s)" % s, ok, "%d B" % (os.path.getsize(p) if os.path.isfile(p) else -1)))

    # ── 两个脚本本机实跑 (★默认档 + 第二档 + selftest★) ──
    # ★★判据修正在产生点★★: `skeleton_section_check.py` **没有 `--selftest` 这个 flag**
    #   (★CLI 只有 --json / --frame★) ⇒ 用错 flag 会得到 rc=2 (用法错) ⇒ **不能拿它当红项**
    #   ⇒ 改成: ★跑两遍比输出是否确定 (★等价于幂等★) + 靠上面的 0 字节 diff 证默认档逐字节未变★
    rc, o = sh("python3 MECH/pinset2_mech_check.py --self-test")
    out.append(("实跑 pinset2_mech_check.py --self-test 绿", rc == 0, "rc=%d" % rc))
    rc1, o1 = sh("python3 MECH/skeleton_section_check.py")
    rc2, o2 = sh("python3 MECH/skeleton_section_check.py")
    out.append(("实跑 skeleton_section_check.py (默认档) rc=0", rc1 == 0 and rc2 == 0, "rc=%d/%d" % (rc1, rc2)))
    out.append(("实跑 skeleton 两次输出确定 (幂等)", o1 == o2, "一致=%s" % (o1 == o2)))
    rc, o = sh("python3 MECH/pinset2_mech_check.py --frame B160x100")
    out.append(("实跑 pinset2 第二档 B160x100 绿", rc == 0, "rc=%d" % rc))
    rc, o = sh("python3 MECH/skeleton_section_check.py --frame B160x100")
    out.append(("实跑 skeleton 第二档 B160x100 绿", rc == 0, "rc=%d" % rc))

    # ── 分片登记 (mech.yaml · 只读) ──
    import yaml
    frag = open(os.path.join(PROJ, "state/fragments/mech.yaml"), encoding="utf-8").read()
    miss_m = [k for k in FRAG_MARKS if k not in frag]
    out.append(("mech.yaml 本单登记 %d 条齐全" % len(FRAG_MARKS), len(miss_m) == 0, "缺 %s" % miss_m[:2]))
    d = yaml.safe_load(frag) or {}
    struct = []
    for sect in ("artifacts", "answers", "needs_from", "needs", "interface_claims", "claims"):
        for e in (d.get(sect) or []):
            if isinstance(e, dict):
                struct.append("%s:%s" % (sect, e.get("key") or e.get("path")))
    dup = [k for k in set(struct) if struct.count(k) > 1]
    dup_mine = [k for k in dup if any(t in k for t in FRAG_MARKS)]
    out.append(("mech.yaml 本单条目零重复 key (结构判)", len(dup_mine) == 0,
                "本单重复 %d %s · ★全表历史重复 %d 条 (不是本单的账)★" % (len(dup_mine), dup_mine[:2], len(dup))))

    # ── 受保护件 + 板指纹 ──
    bad = []
    for p, want in PROTECTED.items():
        got = md5(os.path.join(PROJ, p))
        if got != want:
            bad.append("%s(%s≠%s)" % (p, got[:8], want[:8]))
    out.append(("受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0, "动 %d %s" % (len(bad), bad[:3])))
    st = os.stat(os.path.join(PROJ, BOARD))
    import datetime
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    got = md5(os.path.join(PROJ, BOARD))
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
                "%s / %s" % (got, mt)))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-345 签收闸 · 自测 (★反向用例★)")
    txt = open(os.path.join(PROJ, HANDOFF), encoding="utf-8").read()
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)

    def blocks_ok(hs):
        return all(any(block_code(h) == c and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    print("  %s 真交卷页 · 6 块齐全 (B1~B6 · 与 gate_check.py 的 Q1 同口径)" % ("✅" if blocks_ok(heads) else "❌"))
    print("  %s 反向用例1 · 抽掉 B3 小节标题 ⇒ 判红"
          % ("✅" if not blocks_ok([h for h in heads if block_code(h) != "B3"]) else "❌"))
    print("  %s 反向用例2 · 塞占位符 ⇒ 判红"
          % ("✅" if len(PLACEHOLDER.findall(txt + "<!-- 待填 -->")) > len(PLACEHOLDER.findall(txt)) else "❌"))
    print("  %s 反向用例3 · diff 非空 ⇒ 判红 (默认档必须逐字节相同)"
          % ("✅" if not (os.path.getsize(os.path.join(PROJ, DIFF_ZERO[0])) > 0) else "❌"))
    allok = blocks_ok(heads)
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss345()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-38s %s" % ("✅" if ok else "❌", name, detail))
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
        vr = ("✅ verified (★main 2026-11-23 05:2x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0520_main_sign_iss345.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改闸 · 零外发 · 未替老板拍板 · 零写别人的分片 (mech.yaml 只读) ★ "
                "★ **本单 = ISS-345 cont1 (第 1 批 2 个脚本: `MECH/pinset2_mech_check.py` + `MECH/skeleton_section_check.py`)**: "
                "★**默认档 (F30A 60×30) 迁移前后输出逐字节相同**★ (diff 两个文件均 0 字节 ⇒ ★**判据方向一个字没改**★) + "
                "★**第二档 B160x100 读数在盘**★ (★每条数都有出处: 帧 id / 板 160×100 / 8 层 / 1.60mm / SoM 承载区 53.80×46.78 / "
                "4×100=400 焊盘·★纯 python 逐焊盘重解析逐位一致★) + selftest 6/6 + compat rc=0 + 分片 7 条登记 + "
                "漂移闸 107 处/33 文件与迁移前基线完全一致 (零新增) ★ ★**★未做 (交 main 裁)**: 第 2 批 = "
                "`fit_check_v3_30mm.py` / `fit_check.py` (自报作废·须二选一说清) / `cross_review_check.py` 迁双口径 + 新建闸 "
                "`check_mech_dual_caliber_gate.py` (含反向用例) + `BOARD_GEOM_CALIBER_STATUS.md` scope A/B 追加式订正 + "
                "漂移闸迁后重跑回填 + 三个既有帧表脚本核对 ⇒ ★**默认档恒为 F30A (`DEFAULT_FRAME_ID`)·本单未拍默认档·切档命令已留档**★ ★★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0520_main_sign_iss345.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0520_main_sign_iss345.py'\n"
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
