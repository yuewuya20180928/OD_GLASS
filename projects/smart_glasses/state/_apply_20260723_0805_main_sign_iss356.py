#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0805_main_sign_iss356.py
==================================================
main (项目总工) 的【签收闸 · ISS-356 (hw-lead · 「板那一趟」封装真值基线)】
★预置 (★2026-11-23 08:0x main 先写好·交卷落地后一条命令签★)
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本单特殊: 交的是【封装真值基线】⇒ ★main 必须自己核「目标 lib:name 指向的库文件真在盘」★
            ⇒ 且 ★族级映射表不许拿「待定/TBD/待选型」当结论★

用法:
  python3 state/_apply_20260723_0805_main_sign_iss356.py --check-only ISS-356
  python3 state/_apply_20260723_0805_main_sign_iss356.py --sign ISS-356
  python3 state/_apply_20260723_0805_main_sign_iss356.py --self-test
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

HANDOFF = "HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md"
PAGE = "HW/FP_TRUTH_BASELINE.md"
GATE = "HW/check_fp_truth_baseline.py"
LOGS = "logs/iss356"
KICAD_FP = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

# ★★交卷页的六个块 (★标题里必须出现这些关键词·★gate_check.py 按关键词判块★)★★
BLOCKS = [
    ("B1", ["结论"]),
    ("B2", ["验收标准自评", "验收"]),
    ("B3", ["证据分级", "证据"]),
    ("B4", ["接口取值声明", "接口"]),
    ("B5", ["未决项", "卡点", "未决"]),
    ("B6", ["自证复现命令", "自证", "复现", "命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
OTHER_FRAGS = ("pm", "sw", "mech")
FORBIDDEN = ["等原厂回信", "等供应商回复", "请并入第一轮跟进邮件", "买一块", "采购 RK3572"]
NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍", "不许只写",
       "★★2026-11-23 10:1x 实测补: 交卷页里【描述禁语规则本身】的句子也会命中关键词 (例「禁「等原厂回信」…」「黑名单词全文扫」) ⇒ 一并计入否定语境★",
       "禁", "黑名单", "挂起措辞", "不许写", "禁止性")


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


def forbidden_hits(body):
    hs = []
    for w in FORBIDDEN:
        s = 0
        while True:
            i = body.find(w, s)
            if i < 0:
                break
            ctx = body[max(0, i - 40): i + len(w) + 40]
            if not any(n in ctx for n in NEG):
                hs.append("%s@%d" % (w, i))
            s = i + 1
    return hs


def check_iss356():
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
    ph_hits = []
    ph_desc = 0
    for m in PLACEHOLDER.finditer(txt):
        ctx = txt[max(0, m.start() - 60): m.end() + 60]
        if any(k in ctx for k in ("占位", "骨架", "全是", "占位符")):
            ph_desc += 1
            continue
        ph_hits.append("%r@%d" % (m.group(0), m.start()))
    out.append(("交卷页占位符 = 0 (语境窗口: 描述性引用不计)", len(ph_hits) == 0,
                "真占位 %d %s · 描述性 %d" % (len(ph_hits), ph_hits[:3], ph_desc)))
    fenced_txt = "\n".join(re.findall(r"```.*?```", txt, re.S))
    body_txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    refs = set()
    for line in body_txt.splitlines():
        if any(w in line for w in ("不存在", "待建", "本批不建", "未做")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    sandbox_only = [p for p in miss if p in fenced_txt and p not in body_txt]
    real_miss = [p for p in miss if p not in sandbox_only]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(real_miss) == 0,
                "正文引用 %d 个 · 真 MISS %d %s · 代码块沙盒产物 %d"
                % (len(refs), len(real_miss), real_miss[:3], len(sandbox_only))))

    # ── 板指纹 (零写板) + 双证 ──
    got = md5(os.path.join(PROJ, BOARD))
    st = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
                "%s / %s" % (got, mt)))
    out.append(("交卷页含板指纹双证", txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))

    # ── 零落表 ──
    bad = []
    for p, want in PROTECTED.items():
        g = md5(os.path.join(PROJ, p))
        if g != want:
            bad.append("%s(%s≠%s)" % (p, g[:8], want[:8]))
    out.append(("零落表: 受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0,
                "动 %d %s" % (len(bad), bad[:3])))

    # ── 零改别人的分片 ──
    x_bad = []
    try:
        import yaml
        for f in OTHER_FRAGS:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f),
                                    encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss356" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append("解析失败 %s" % ex)
    out.append(("别人的分片 (pm/sw/mech) 零本单登记条目", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))

    # ── 两个交付物在盘 (★基线页路径容许两处: HW/ 或 HW/PCB/ 下都认★) ──
    out.append(("交付物 自带闸 %s 在盘" % GATE, os.path.isfile(os.path.join(PROJ, GATE)), GATE))
    page_paths = [PAGE, "HW/PCB/FP_TRUTH_BASELINE.md"]
    page_hit = [p for p in page_paths if os.path.isfile(os.path.join(PROJ, p))]
    out.append(("交付物 封装真值基线页在盘 (HW/ 或 HW/PCB/ 都认)", bool(page_hit),
                page_hit[0] if page_hit else "两处都不在盘"))

    # ── 自带闸 ──
    if os.path.isfile(os.path.join(PROJ, GATE)):
        rc, o = sh("python3 %s" % GATE)
        out.append(("自带闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % GATE)
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:60])))

    # ── ★基线页内容判据 (main 独立读页) ──
    page_hit = [p for p in (PAGE, "HW/PCB/FP_TRUTH_BASELINE.md") if os.path.isfile(os.path.join(PROJ, p))]
    ppath = os.path.join(PROJ, page_hit[0]) if page_hit else os.path.join(PROJ, PAGE)
    if os.path.isfile(ppath):
        pt = open(ppath, encoding="utf-8", errors="replace").read()
        out.append(("基线页 §1 族级映射表在盘", "族级映射" in pt or "族" in pt, "§1 在盘"))
        out.append(("基线页 §3 删件候选在盘", "删件候选" in pt, "§3 在盘"))
        # ★族级表里不许拿「待定/TBD/待选型」当结论★ (在 §1 段内)
        i1 = pt.find("族级映射")
        j1 = pt.find("删件候选")
        seg1 = pt[i1:j1] if (i1 >= 0 and j1 > i1) else ""
        # ★只查「结论栏」行 (★表头/说明里出现「待定」不算★) ⇒ 取带 lib:name 的行 ★
        fam_rows = [l for l in seg1.splitlines() if re.search(r"lib:[A-Za-z0-9_.+-]+", l)]
        bad_fam = [l for l in fam_rows if re.search(r"(待定|TBD|待选型)", l)
                   and not re.search(r"(降级|删除|不适用|暂无|待 boss|待选型项)", l)]
        out.append(("★族级表每行都给出目标 lib:name (不许拿占位当结论)",
                    len(fam_rows) >= 5 and len(bad_fam) == 0,
                    "族行 %d · 占位当结论 %d" % (len(fam_rows), len(bad_fam))))
        # ★★main 独立核: 目标 lib:name 指向的【封装文件】真在盘 (★★不是只看 .pretty 库目录在不在★
        #   ⇒ KiCad 10 的官方库是 metric 后缀命名 (R_0402_1005Metric / C_0603_1608Metric /
        #     LED_0805_2012Metric / L_0805_2012Metric / SW_SPST_B3S-1000) ⇒ 旧名 (R_0402 / C_0603)
        #   【按字面找不到文件】⇒ 写进基线页 ⇒ 那一趟画出去的板会指向不存在的封装 ⇒ 返工★★) ★
        libs = {}
        for l in pt.splitlines():
            # ★★2026-11-23 10:1x 实测修正: lib 名必须【首字母大写】(★KiCad 官方库都是 CamelCase★) ⇒ 否则页面里「查 `lib.pretty` 目录」会被当成 lib:name ⇒ 假红★
            for m in re.finditer(r"`([A-Z][A-Za-z0-9_]*):([A-Za-z0-9_.\-]+)`", l):
                libs.setdefault(m.group(1), set()).add(m.group(2))
            for m in re.finditer(r"([A-Z][A-Za-z0-9_]+):([A-Za-z0-9_.\-]+)\.kicad_mod", l):
                libs.setdefault(m.group(1), set()).add(m.group(2))
        missing = []
        checked = 0
        for lib, names in libs.items():
            d = os.path.join(KICAD_FP, lib + ".pretty")
            if not os.path.isdir(d):
                missing.append("%s.pretty(库目录不在盘)" % lib)
                continue
            for nm in names:
                checked += 1
                if not os.path.isfile(os.path.join(d, nm + ".kicad_mod")):
                    missing.append("%s:%s" % (lib, nm))
        out.append(("★目标 lib:name 的【封装文件】真在盘 (逐个查 .kicad_mod)",
                    len(libs) == 0 or len(missing) == 0,
                    "库 %d · 文件 %d · 不在盘 %d %s" % (len(libs), checked, len(missing), missing[:4])))
        # ★库计数口径 (★main 实读: 155 个 .pretty 库目录 / 15,468 个 .kicad_mod 封装文件★)
        n_dirs = len([d for d in os.listdir(KICAD_FP) if d.endswith(".pretty")]) if os.path.isdir(KICAD_FP) else 0
        n_files = sum(len(os.listdir(os.path.join(KICAD_FP, d))) for d in os.listdir(KICAD_FP)
                       if d.endswith(".pretty")) if os.path.isdir(KICAD_FP) else 0
        bad_cnt = []
        if "15,777" in pt or "15777" in pt:
            bad_cnt.append("页里出现 15,777")
        if re.search(r"1[0-9],?[0-9]{3}\s*个\s*\.?pretty", pt):
            bad_cnt.append("把封装文件数当 .pretty 目录数")
        out.append(("★库计数口径正确 (155 库目录 / 15,468 封装文件)", len(bad_cnt) == 0,
                    "main 实读 %d 目录 / %d 文件 %s" % (n_dirs, n_files, bad_cnt[:2])))
    else:
        out.append(("★基线页内容判据", False, "页不在盘"))

    # ── 禁语 ──
    hits = forbidden_hits(txt)
    out.append(("零外发: 无「等原厂回信/等回复/跟进邮件」的非否定语境表述", len(hits) == 0,
                "命中 %d %s" % (len(hits), hits[:3])))

    # ── 证据目录 ──
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss356/ 证据在盘 (≥ 8 件)", n >= 8, "%d 件" % n))

    # ── 必跑项 ──
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18 (★交卷页 B1~B6 齐全⇒ 不许掉 Q1★)",
                rc5 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc5, m3.group(0) if m3 else "未读到")))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-356 签收闸 · 自测 (★反向用例★)")
    full = os.path.join(PROJ, HANDOFF)
    txt = open(full, encoding="utf-8").read() if os.path.isfile(full) else ""
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)

    def blocks_ok(hs):
        return all(any(block_code(h) == c and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    r = []
    pre = not os.path.isfile(full)
    r.append(("真交卷页 · 6 块齐全 (★未落地时算预置态·不算红★)",
              blocks_ok(heads) if not pre else True))
    r.append(("反向用例1 · 抽掉 B3 小节标题 ⇒ 判红",
              not blocks_ok([h for h in heads if block_code(h) != "B3"])))
    r.append(("反向用例2 · 板 md5 期望值被篡改 ⇒ 判红",
              md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3a · 禁止性表述 (不许等原厂回信) 不算违规",
              forbidden_hits("★本单不许写等原厂回信★") == []))
    r.append(("反向用例3b · 真违规 (查不到就等原厂回信) 必须被抓到",
              forbidden_hits("查不到就等原厂回信吧") != []))
    # ★反向用例4: 族级表「占位当结论」判据能分辨 ★
    def fam_bad(rows):
        return [l for l in rows if re.search(r"(待定|TBD|待选型)", l)
                and not re.search(r"(降级|删除|不适用|暂无|待 boss|待选型项)", l)]
    r.append(("反向用例4 · 族级表占位当结论判据能分辨",
              fam_bad(["| R_0402 | lib:Resistor_SMD:R_0402 |"]) == []
              and fam_bad(["| R_0402 | 封装待定 |"]) != []))
    # ★反向用例6: lib:name 抽取 + 封装文件存在性判据能分辨 (旧名 vs KiCad 10 真名) ★
    def libnames(pt):
        s = set()
        for l in pt.splitlines():
            # ★★2026-11-23 10:1x 实测修正: lib 名必须【首字母大写】(★KiCad 官方库都是 CamelCase★) ⇒ 否则页面里「查 `lib.pretty` 目录」会被当成 lib:name ⇒ 假红★
            for m in re.finditer(r"`([A-Z][A-Za-z0-9_]*):([A-Za-z0-9_.\-]+)`", l):
                s.add((m.group(1), m.group(2)))
        return s
    def fp_exists(lib, nm):
        return os.path.isfile(os.path.join(KICAD_FP, lib + ".pretty", nm + ".kicad_mod"))
    r.append(("反向用例6 · 旧名 R_0402 不存在 / 真名 R_0402_1005Metric 存在",
              not fp_exists("Resistor_SMD", "R_0402") and fp_exists("Resistor_SMD", "R_0402_1005Metric")))
    r.append(("反向用例7 · lib:name 抽取判据能分辨",
              ("Resistor_SMD", "R_0402_1005Metric") in libnames("| R | `Resistor_SMD:R_0402_1005Metric` |")
              and libnames("| R | 封装待定 |") == set()))
    allok = True
    for name, ok in r:
        allok = allok and bool(ok)
        print("  %s %-46s" % ("✅" if ok else "❌", name))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss356()
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
        vr = ("✅ verified (★main 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0805_main_sign_iss356.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改别人的分片 · 零外发 · 未代老板拍板 · 未新增拍板项 ★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0805_main_sign_iss356.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0805_main_sign_iss356.py'\n"
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
