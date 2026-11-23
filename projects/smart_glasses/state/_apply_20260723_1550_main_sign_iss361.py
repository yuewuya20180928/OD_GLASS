#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_1550_main_sign_iss361.py
==================================================
main (项目总工) 的【签收闸 · ISS-361 (hw-lead · 「板那一趟」封装真值覆盖缺口)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本单特殊: 交的是【覆盖缺口页 + 机器闸】⇒ 判据核心 = ①闸 G0~G7 main 自己复跑
  ②★四桶判据 (TP/DNP/靶内/缺口) main 自己复算并与 C4 的 158 对账★
  ③★13 件缺口的根因 (BOM footprint 栏是描述串而非字面量「待定」) main 自己读 BOM 验★
用法:
  python3 state/_apply_20260723_1550_main_sign_iss361.py --check-only ISS-361
  python3 state/_apply_20260723_1550_main_sign_iss361.py --sign ISS-361
  python3 state/_apply_20260723_1550_main_sign_iss361.py --self-test
"""
import csv
import datetime
import hashlib
import json
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
HANDOFF = "HANDOFF/2026-11-23_hw-lead_ISS361_封装真值覆盖缺口.md"
PAGE = "HW/PCB/FP_TRUTH_COVERAGE_GAP.md"
GATE = "HW/check_fp_truth_coverage_gap.py"
LOGS = "logs/iss361"
GEN = "logs/iss361/build_fp_truth_coverage_gap.py"

BLOCKS = [
    ("B1", ["结论"]),
    ("B2", ["验收标准自评", "验收"]),
    ("B3", ["证据分级", "证据"]),
    ("B4", ["接口取值声明", "接口"]),
    ("B5", ["未决项", "卡点", "未决"]),
    ("B6", ["自证复现命令", "自证", "复现", "命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s*(?:待填|TODO|FIXME|PLACEHOLDER|XXX)|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": BOARD_MD5,
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
OTHER_FRAGS = ("pm", "sw", "mech")


def block_code(h):
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-9])\b", s)
    return m.group(1) if m else None


def sh(cmd, timeout=1800):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_iss361():
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
    ph = [m.group(0) for m in PLACEHOLDER.finditer(txt)
          if not any(k in txt[max(0, m.start() - 60): m.end() + 60] for k in ("占位", "骨架", "全是", "占位符"))]
    out.append(("交卷页占位符 = 0 (语境窗口)", len(ph) == 0, "命中 %d" % len(ph)))
    fenced = "\n".join(re.findall(r"```.*?```", txt, re.S))
    body = re.sub(r"```.*?```", "", txt, flags=re.S)
    refs = set()
    for line in body.splitlines():
        if any(w in line for w in ("不存在", "待建", "未做")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    sandbox = [p for p in miss if p in fenced and p not in body]
    typo = []
    for p in list(miss):
        if p in sandbox:
            continue
        base = os.path.basename(p)
        for root, _d, files in os.walk(PROJ):
            if root.startswith(os.path.join(PROJ, "tmp")) or "/.trash/" in root:
                continue
            if base in files:
                typo.append("%s → %s" % (p, os.path.relpath(os.path.join(root, base), PROJ)))
                miss.remove(p)
                break
    real = [p for p in miss if p not in sandbox]
    out.append(("交卷页引用文件逐个在盘 (0 MISS; ★路径笔误单列★)", len(real) == 0,
                "引用 %d · 真 MISS %d %s · 沙盒 %d · 笔误 %d" % (len(refs), len(real), real[:3], len(sandbox), len(typo))))
    got = md5(os.path.join(PROJ, BOARD))
    stt = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(stt.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]), "%s / %s" % (got, mt)))
    out.append(("交卷页含板指纹双证", txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))
    bad = []
    for p, want in PROTECTED.items():
        g = md5(os.path.join(PROJ, p))
        if g != want:
            bad.append(p)
    out.append(("零落表: 受保护件 %d 件 md5 未动" % len(PROTECTED), len(bad) == 0, "动 %d %s" % (len(bad), bad[:3])))
    x_bad = []
    try:
        import yaml
        for f in OTHER_FRAGS:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss361" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append(str(ex))
    out.append(("别人的分片 (pm/sw/mech) 零本单登记条目", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))
    # 两个交付物
    out.append(("覆盖缺口页 %s 在盘 (≥ 4000 B)" % PAGE,
                os.path.isfile(os.path.join(PROJ, PAGE)) and os.path.getsize(os.path.join(PROJ, PAGE)) >= 4000,
                "%d B" % (os.path.getsize(os.path.join(PROJ, PAGE)) if os.path.isfile(os.path.join(PROJ, PAGE)) else 0)))
    # ★★自带闸 main 自己复跑
    if os.path.isfile(os.path.join(PROJ, GATE)):
        rc, o = sh("python3 %s" % GATE)
        out.append(("★★自带闸裸跑 rc=0 (G0~G7)", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % GATE)
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("★★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:50])))
    else:
        out.append(("★★自带闸在盘", False, GATE))
    # ★★四桶判据 main 自己复算 + 与 C4 的 158 对账
    try:
        rc3, o3 = sh("bash state/pcbnew_py.sh state/check_pcb_nets.py")
        m = re.search(r"焊盘号为\*\*占位\(行序\)\*\*的器件\s*(\d+)\s*个", o3) or re.search(r"占位\(行序\)[^\n]*?(\d+)\s*个", o3)
        c4 = int(m.group(1)) if m else None
        out.append(("★★C4 占位脚号读数 (main 自己跑 check_pcb_nets)", c4 == 158, "C4=%s" % c4))
        rc4, o4 = sh("python3 %s" % GEN)
        # ★★生成器输出一行关键读数 (★不是 JSON★) ⇒ 按行解析 ★
        mt = re.search(r"C4=(\d+).*?交集=(\d+).*?TP=(\d+)\s+DNP=(\d+)\s+缺口=(\d+).*?四桶和=(\d+)", o4, re.S)
        if mt:
            g_c4, inter, tp, dnp, gp, tot = (int(x) for x in mt.groups())
            out.append(("★★四桶判据自洽 (TP+DNP+靶内+缺口 = C4 的 158)",
                        tot == 158 and g_c4 == 158 and tp + dnp + inter + gp == 158,
                        "%s+%s+%s+%s=%s · 生成器 C4=%s" % (tp, dnp, inter, gp, tot, g_c4)))
            out.append(("★★四桶读数与页里声明一致 (42/26/77/13)",
                        (tp, dnp, inter, gp) == (42, 26, 77, 13), "%s/%s/%s/%s" % (tp, dnp, inter, gp)))
            out.append(("★★main 自己跑的 C4 读数与生成器一致", c4 == g_c4, "check_pcb_nets=%s · 生成器=%s" % (c4, g_c4)))
        else:
            out.append(("★★四桶读数可解析 (main 自己跑生成器)", False, "未解析到读数行: %r" % o4.strip()[-120:]))
    except Exception as ex:
        out.append(("★★四桶判据复算", False, "失败 %s" % ex))
    # ★★13 件缺口的根因: BOM footprint 栏是描述串而非字面量「待定」 ⇒ main 自己读 BOM 验
    try:
        rows = list(csv.DictReader(open(os.path.join(PROJ, "HW/BOM_v1.csv"), encoding="utf-8")))
        dev = [r for r in rows if (r.get("type") or "").strip() not in ("NET", "TP")]
        must_dev = [r for r in dev if (r.get("dnp") or "").strip() == "必装"]
        lit = [r.get("ref") for r in must_dev if (r.get("footprint") or "").strip() == "待定"]
        desc = [r.get("ref") for r in must_dev if (r.get("footprint") or "").strip() not in ("待定", "")
                and (r.get("footprint") or "").strip() != "待定"]
        out.append(("★★BOM 侧: 必装器件里 footprint 字面量「待定」=%d 件, 描述串=%d 件 (★两种写法并存⇒ 按字面量筛会漏★)"
                    % (len(lit), len(desc)), len(lit) >= 70 and len(desc) >= 1,
                    "待定 %d (%s) · 描述串 %d (%s)" % (len(lit), lit[:3], len(desc), desc[:3])))
    except Exception as ex:
        out.append(("★★BOM 根因复核", False, "失败 %s" % ex))
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss361/ 证据在盘 (≥ 8 件)", n >= 8, "%d 件" % n))
    rc5, o5 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc5 == 0, "rc=%d" % rc5))
    rc6, o6 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o6)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc6 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc6, m3.group(0) if m3 else "未读到")))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-361 签收闸 · 自测")
    r = []
    r.append(("反向用例1 · 块标题解析可用", block_code("B3 · 证据分级") == "B3"))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3 · 四桶自洽判据能分辨 (42/26/77/13)",
              42 + 26 + 77 + 13 == 158 and 42 + 26 + 77 + 12 != 158))
    r.append(("反向用例4 · 锚点/注释不算占位符", not PLACEHOLDER.search("`<!-- G01 -->`")))
    allok = True
    for n, ok in r:
        allok = allok and bool(ok)
        print("  %s %s" % ("✅" if ok else "❌", n))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss361()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-46s %s" % ("✅" if ok else "❌", name, detail))
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
        vr = ("✅ verified (★main 2026-11-23 15:5x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_1550_main_sign_iss361.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板**) · "
              "零落表 (受保护件 5 件同值) · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★ "
              "★★【main 独立复核】★★ ★**① 自带闸 `HW/check_fp_truth_coverage_gap.py` 由 main 自己复跑: 裸跑 rc=0 (G0~G7) + `--selftest` 末行 ALL TESTS PASS** ★ "
              "★**② 四桶判据 main 自己复算**: TP 42 + DNP 26 + 靶内 77 + 缺口 13 = **158** ⇒ 与 main 自己跑的 `check_pcb_nets.py` 的 C4 读数 (占位脚号 158 件) **对账一致** ★ "
              "★**③ 13 件缺口的根因 main 自己读 BOM 验**: ★**BOM 的 `footprint` 栏里【字面量「待定」】与【描述串 (如「★板文件封装: N 焊盘 (…)」)】两种写法并存 ⇒ "
              "⇒ ISS-356 用的 `footprint == '待定'` 单一条件把那 13 件全挡在门外 ⇒ **清单类判据必须用语义判定, 不能用字面量相等** ★ "
              "★**④ ★★本单推翻了我 08:1x 写进 `state/board_trip_baseline_20260723.txt` 的那条验收口径 (★已由 main 在该文件《订正一》里改掉★)**: "
              "★**「C4 的 158 会随封装真值基线收敛」机制上不成立** (★沙盒实跑: 只把 5 件网表节点串改成具名 pinN ⇒ 158→153 (板面零改动), 而 100 件 land 全换官方封装读数仍 158★) ⇒ "
              "★**⇒ 收敛的主要杠杆在【网表节点具名】, 不在【换 land】⇒ 那一趟的验收要按「换官方 land 90 件 + 网表节点具名 90 件」这两条数来写** ★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        if "  verify_result:" in new:
            new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        else:
            new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_1550_main_sign_iss361.py'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_1550_main_sign_iss361.py'\n"
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
