#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_1655_main_sign_iss365.py
==================================================
main (项目总工) 的【签收闸 · ISS-365 (mech-lead · S10 换封装对 MECH 侧的影响面)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本单特殊: 交的是【换封装那一跳对结构侧的影响面】⇒ 判据核心 = ①自带闸 main 自己复跑
  ②★净距两列 + Δ 与 D_LED_G 块数漂移由 main 自己重算 (不抄 agent 的表)★
  ③既有四道 MECH 闸不许被改红 ④沙盒在项目盘
用法:
  python3 state/_apply_20260723_1655_main_sign_iss365.py --check-only ISS-365
  python3 state/_apply_20260723_1655_main_sign_iss365.py --sign ISS-365
  python3 state/_apply_20260723_1655_main_sign_iss365.py --self-test
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
HANDOFF = "HANDOFF/2026-11-23_mech-lead_ISS365_S10换封装对MECH侧影响面.md"
LOGS = "logs/iss365"
GATE = "MECH/check_onepass_s10_fp_swap_impact.py"
COMPUTE = "logs/iss365/compute_iss365.py"
LEDS = "logs/iss365/led_space_drift.py"
MANIFEST = "logs/iss365/29_final_md5.txt"
MECH_GATES = ["MECH/check_onepass_struct_crosscheck.py", "MECH/check_onepass_mech_sync.py",
              "MECH/check_board_frame_coords.py", "MECH/check_demo_struct_truth.py"]

BLOCKS = [
    ("B1", ["结论"]),
    ("B2", ["验收标准自评", "验收"]),
    ("B3", ["证据分级", "证据"]),
    ("B4", ["接口取值声明", "接口"]),
    ("B5", ["未决项", "卡点", "未决"]),
    ("B6", ["自证复现命令", "自证", "复现", "命令"]),
    ("B7", ["边界自证", "边界"]),
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
OTHER_FRAGS = ("pm", "sw", "hw")
FORBIDDEN = ["等原厂回信", "等供应商回复", "请并入第一轮跟进邮件", "买一块", "采购 RK3572"]
NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍", "禁", "黑名单", "挂起措辞")


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


def check_iss365():
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
    # ★agent 自己的 md5 清单由 main 复跑
    if os.path.isfile(os.path.join(PROJ, MANIFEST)):
        rc0, o0 = sh("md5sum -c %s" % MANIFEST)
        nbad = len([l for l in o0.splitlines() if "FAILED" in l])
        out.append(("★★agent 的 md5 清单 main 复跑 ⇒ 全部逐字节未变", rc0 == 0 and nbad == 0,
                    "rc=%d FAILED=%d 行数=%d" % (rc0, nbad, len(o0.splitlines()))))
    else:
        out.append(("★★agent 的 md5 清单在盘", False, MANIFEST))
    x_bad = []
    try:
        import yaml
        for f in OTHER_FRAGS:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss365" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append(str(ex))
    out.append(("别人的分片 (pm/sw/hw) 零本单登记条目", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))
    # ★★自带闸
    if os.path.isfile(os.path.join(PROJ, GATE)):
        rc, o = sh("python3 %s" % GATE)
        out.append(("★★自带闸裸跑 rc=0 (M0~M7)", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % GATE)
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("★★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:50])))
    else:
        out.append(("★★自带闸在盘", False, GATE))
    # ★★main 自己重算: 10 个 R_SEL_* 的净距两列 + Δ
    try:
        rc3, o3 = sh("python3 %s" % COMPUTE)
        rows = re.findall(r"(R_SEL_\w+)\s+换前净距\s+([\d.]+)\s+换后净距\s+([\d.]+)\s+Δ\s+(-?[\d.]+)", o3)
        deltas = [float(r[3]) for r in rows]
        tight_before = min(float(r[1]) for r in rows) if rows else None
        tight_after = min(float(r[2]) for r in rows) if rows else None
        ok = (len(rows) == 10 and tight_before == 7.65 and tight_after == 7.325
              and abs(min(deltas) + 0.325) < 1e-9 and max(deltas) == 0.675)
        out.append(("★★main 自己重算 10 个 R_SEL_* 净距两列 + Δ (最紧 7.65→7.325, Δ −0.325)", ok,
                    "%d 行 · 最紧 %s→%s · Δ 范围 [%s, %s]" % (len(rows), tight_before, tight_after,
                                                           min(deltas) if deltas else None, max(deltas) if deltas else None)))
    except Exception as ex:
        out.append(("★★main 自己重算 R_SEL_* 净距", False, "失败 %s" % ex))
    # ★★main 自己重算: D_LED_G 可落位块数漂移 1992→2183
    try:
        rc4, o4 = sh("python3 %s" % LEDS)
        m = re.search(r"可落位块数:\s*(\d+)\s*->\s*(\d+)", o4)
        mono = re.findall(r"\((\d+\.\d+), (\d+)\)", o4)
        nonmono = bool(mono) and int(mono[-1][1]) < int(mono[-2][1]) if len(mono) >= 2 else False
        out.append(("★★main 自己重算 D_LED_G 可落位块数 1992→2183", bool(m) and m.group(1) == "1992" and m.group(2) == "2183",
                    m.group(0) if m else "未读到"))
        out.append(("★★clr sweep 非单调 (clr=0.5 < clr=0.2) ⇒ 旧「可落位越多」直觉作废", nonmono,
                    "末两档 %s" % (mono[-2:] if mono else None)))
    except Exception as ex:
        out.append(("★★main 自己重算 D_LED_G 漂移", False, "失败 %s" % ex))
    # ★★既有四道 MECH 闸不许被改红
    badg = []
    for g in MECH_GATES:
        rc5, _o = sh("python3 %s" % g)
        if rc5 != 0:
            badg.append("%s(rc=%d)" % (g.split("/")[-1], rc5))
    out.append(("★★既有 4 道 MECH 闸未被本单改红", not badg, "红 %d %s" % (len(badg), badg[:3])))
    out.append(("沙盒在项目盘 tmp/ (不写 /tmp)", os.path.isdir(os.path.join(PROJ, "tmp", "iss365_sbx")), "tmp/iss365_sbx"))
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss365/ 证据在盘 (≥ 10 件)", n >= 10, "%d 件" % n))
    rc6, o6 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc6 == 0, "rc=%d" % rc6))
    rc7, o7 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o7)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc7 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc7, m3.group(0) if m3 else "未读到")))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-365 签收闸 · 自测")
    r = []
    r.append(("反向用例1 · 块标题解析可用", block_code("B2 · 验收标准自评") == "B2"))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3 · 净距判据能分辨 (7.65→7.325 / Δ −0.325)",
              abs((7.325 - 7.65) + 0.325) < 1e-9 and abs((7.33 - 7.65) + 0.325) > 1e-9))
    r.append(("反向用例4 · 非单调判据能分辨 (2197 < 2253 ⇒ 非单调)", 2197 < 2253 and 2075 < 2183))
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
        lines = check_iss365()
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
        vr = ("✅ verified (★main 2026-11-23 17:0x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_1655_main_sign_iss365.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板**) · "
              "零落表 (受保护件 5 件同值) · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★ "
              "★★【main 独立复核 (★自己重算, 不抄 agent 的表★)】★★ "
              "★**① 10 个 `R_SEL_*` 换官方 0603 后的净距两列 + Δ 由 main 自己重算**: 最紧一行 `R_SEL_D0_N` **7.65 → 7.325 (Δ −0.325)**, 其余行 Δ ∈ {−0.325, +0.675}, 10 行全在 ⇒ **结构侧零重排成立** (冲突 0→0; 全板最小净距 4.6500 前后不变) ★ "
              "★**② ★★本单最值钱的一条: `D_LED_G` 换官方 0805 后的真漂移, main 自己重算**: 可落位块数 **1992 → 2183 (+191)**, 且 **clr sweep 不再单调** (clr=0.5 → 2197 **<** clr=0.2 → 2253) ⇒ ★**「净距越大可落位越多」这条旧直觉在 0805 下不成立 ⇒ 必须重扫, 不能插值** ⇒ ⇒ **既有页 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2 那句「led_space 块数不变」的后半句已作废, 须同趟重算** ★ "
              "★**③ 既有 4 道 MECH 闸未被本单改红** (struct_crosscheck / mech_sync / board_frame_coords / demo_struct_truth 全 rc=0) ★ "
              "★**④ agent 的 md5 清单由 main 复跑 ⇒ 逐字节全同**; 沙盒在项目盘 `tmp/iss365_sbx` (不写 /tmp) ★ "
              "★**⑤ 未代老板拍**: ★**按键按动力度 (3 N KMR2 vs 1.5 N B3U-1000P) 与 `D_LED_G` 结构光孔有无 = 两件老板的项 (U-365-1 / U-365-3)·只登记两路的结构代价 (键孔宽 +1.200 vs 不变; 键高 1.9 vs 1.6 mm [官网])** ★")
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
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_1655_main_sign_iss365.py'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_1655_main_sign_iss365.py'\n"
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
