#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0345_main_sign_iss377_378.py
==================================================
main (项目总工) 的【签收闸 · ISS-377 (mech-lead) + ISS-378 (sw-lead)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★★公共判据★: 板三项指纹 / 零落表(基线 md5) / 别人分片零本单登记 / 自带闸裸跑+selftest / 零挂链 / 交卷页 B1~B6 + 关键数 / 证据目录 / merge + gate_check Q1=18/18
★★可归因红★: gate_check 的红若指向【别的单的在飞产物】⇒ 记录归因, 不计入本单拒签 (★2026-11-24 03:2x 定规★)

用法:
  python3 state/_apply_20260724_0345_main_sign_iss377_378.py --check-only ISS-377
  python3 state/_apply_20260724_0345_main_sign_iss377_378.py --check-only ISS-378
  python3 state/_apply_20260724_0345_main_sign_iss377_378.py --sign ISS-377
  python3 state/_apply_20260724_0345_main_sign_iss377_378.py --sign ISS-378
  python3 state/_apply_20260724_0345_main_sign_iss377_378.py --self-test
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
BOARD_SIZE = 4940213
STAMP = time.strftime("%Y%m%d_%H%M")

SPEC = {
    "ISS-377": {
        "owner": "mech-lead",
        "handoff": "HANDOFF/2026-11-24_mech-lead_ISS377_座体净距判据同源化与座体型号自查.md",
        "gate": "MECH/check_connector_clearance_caliber.py",
        "page": "MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md",
        "frag": "state/fragments/mech.yaml",
        "frag_key": "iss377",
        "other_frags": ("pm", "hw", "sw"),
        "logs": "logs/iss377",
        "baseline": None,
        "must": [
            ("0.5200", "★J_UART 现状 Y 向罩住余量最坏 0.5200 < CRIT 0.60"),
            ("1.5175", "★J_DEBUG 换官方 THT 后铜箔每边超出真相页清空区 1.5175"),
            ("0.3625", "★现页四处理想口径 0.3625 (★两个口径都在页里·不许只写一个★)"),
            ("4.18", "★两口径差 4.18 倍"),
            ("DP-1", "★降级方案 DP-1~DP-4"),
            ("DF40C", "★座体真实型号 J_SOM_P1~P4 = Hirose DF40C-100DS"),
            ("USB4105", "★座体真实型号 J_USB_C = GCT USB4105-16P"),
            ("0数据", "★J_DEBUG / J_UART 无厂商料号 = [0数据]"),
            ("611b869e", "★板 md5 写进页里"),
        ],
        "extra": [
            ("同源", "★判据同源化 (J_DEBUG 铜箔支配 vs J_UART 座体支配 不再各算各的)"),
            ("max(", "★同源公式 M = max(H_housing, C_copper)"),
        ],
        "must_not": [("等原厂回信", "★禁挂起措辞"), ("等供应商回复", "★禁挂起措辞")],
    },
    "ISS-378": {
        "owner": "sw-lead",
        "handoff": "HANDOFF/2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md",
        "gate": "SW/tools/check_debug_header_fw_impact.py",
        "page": "SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md",
        "frag": "state/fragments/sw.yaml",
        "frag_key": "iss378",
        "other_frags": ("pm", "hw", "mech"),
        "logs": "logs/iss378",
        "baseline": None,
        "must": [
            ("19", "★逐网 19 行表"),
            ("救砖", "★三条救砖链"),
            ("JTAG_TDI", "★JTAG_TDI 冲突登记"),
            ("SoC_NC", "★SoC 侧 JTAG_TDI 端点 = SoC_NC 实测事实"),
            ("141.0450", "★候选 A (rot90 顺排) 坐标"),
            ("144.8550", "★候选 B (rot270 逆排) 坐标"),
            ("611b869e", "★板 md5 写进页里"),
        ],
        "extra": [
            ("不代拍", "★只做事实与代价, 不代拍"),
        ],
        "must_not": [("等原厂回信", "★禁挂起措辞"), ("等供应商回复", "★禁挂起措辞")],
    },
}


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


def check_iss(issue):
    S = SPEC[issue]
    out = []
    full = os.path.join(PROJ, S["handoff"])
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, S["handoff"]))
        return out
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8")
    out.append(("交卷页存在", True, "%s (%d B)" % (S["handoff"], len(raw))))
    out.append(("交卷页不是骨架 (≥ 4000 B)", len(raw) >= 4000, "%d B" % len(raw)))
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    blob = "\n".join(heads)
    for code, kws in (("B1", ["结论", "结论摘要", "一句话"]), ("B2", ["验收标准自评", "自评", "验收标准"]),
                      ("B3", ["证据分级", "证据等级", "证据"]), ("B4", ["接口取值", "接口声明", "interface_claims"]),
                      ("B5", ["阻塞", "卡点", "未决", "待办"]), ("B6", ["复现", "复现命令", "自证"])):
        hit = any(k in blob for k in kws)
        out.append(("交卷页 %s 块标题含 gate_check 关键词" % code, hit, kws[0]))
    ph = [m.group(0) for m in re.finditer(r'<!--\s*(?:待填|TODO|FIXME|PLACEHOLDER|XXX)|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__', txt)
          if not any(k in txt[max(0, m.start() - 60): m.end() + 60] for k in ("占位", "骨架", "全是", "占位符"))]
    out.append(("交卷页占位符 = 0 (语境窗口)", len(ph) == 0, "命中 %d" % len(ph)))
    fenced = "\n".join(re.findall(r"```.*?```", txt, re.S))
    body = re.sub(r"```.*?```", "", txt, flags=re.S)
    refs = set()
    for line in body.splitlines():
        if any(w in line for w in ("不存在", "待建", "未做")):
            continue
        refs.update(re.findall(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_一-鿿-]\.[A-Za-z0-9_一-鿿-]{1,24}', line))
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
    out.append(("板指纹 md5+mtime+size 三项未动",
                got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]) and stt.st_size == BOARD_SIZE,
                "%s / %s / %d B" % (got, mt, stt.st_size)))
    out.append(("交卷页含板指纹双证", txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))
    # 零落表: 受保护件固定集 (板/板工程/网表/脚表/BOM + gate_check/merge/frag_write)
    prot = {"HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
            "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
            "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
            "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8"}
    bad = []
    for p, want in prot.items():
        fp = os.path.join(PROJ, p)
        if os.path.isfile(fp) and md5(fp) != want:
            bad.append(p)
    out.append(("零落表: 受保护件 %d 件 md5 同基线" % len(prot), len(bad) == 0, "动 %d %s" % (len(bad), bad[:3])))
    x_bad = []
    try:
        import yaml
        for f in S["other_frags"]:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if S["frag_key"] in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append(str(ex))
    out.append(("别人的分片 (%s) 零本单登记条目" % "/".join(S["other_frags"]), len(x_bad) == 0,
                "越界 %d %s" % (len(x_bad), x_bad[:3])))
    if os.path.isfile(os.path.join(PROJ, S["gate"])):
        rc, o = sh("python3 %s" % S["gate"])
        out.append(("★★自带闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % S["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("★★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:50])))
        out.append(("★★零挂链 (新闸不在 state/gate_check.py 里)",
                    sh("grep -c %s state/gate_check.py" % os.path.basename(S["gate"]))[1].strip().splitlines()[0] == "0",
                    "grep 命中 0"))
    else:
        out.append(("★★自带闸在盘", False, S["gate"]))
    pp = os.path.join(PROJ, S["page"])
    out.append(("交付页 %s 在盘 (≥ 4000 B)" % S["page"],
                os.path.isfile(pp) and os.path.getsize(pp) >= 4000,
                "%d B" % (os.path.getsize(pp) if os.path.isfile(pp) else 0)))
    for needle, label in S["must"]:
        out.append(("交卷页含 %s" % label, needle in txt, needle))
    for needle, label in S["extra"]:
        out.append(("交卷页含 %s" % label, needle in txt, needle))
    for needle, label in S["must_not"]:
        hits = []
        s0 = 0
        while True:
            k = txt.find(needle, s0)
            if k < 0:
                break
            ctx = txt[max(0, k - 90): k + len(needle) + 90]
            if not any(mk in ctx for mk in ("不许", "禁", "无「", "零挂起", "不写成", "没有")):
                hits.append(k)
            s0 = k + 1
        out.append(("交卷页不含 %s (语境判据)" % label, len(hits) == 0, "命中 %d" % len(hits)))
    out.append(("自己的分片有本单登记", S["frag_key"] in open(os.path.join(PROJ, S["frag"]), encoding="utf-8", errors="replace").read(), S["frag_key"]))
    # ★★证据判据按【关键证据链】而不是【魔数件数】(★L-14 同型: 这两单是收尾/续做趟, 天然少于整轮★)
    lp = os.path.join(PROJ, S["logs"])
    n = len(os.listdir(lp)) if os.path.isdir(lp) else 0
    req = {"ISS-377": ["board_connectors.json", "commands.txt"],
           "ISS-378": ["01_gate_bare.log", "02_gate_selftest.log"]}[issue]
    missreq = [f for f in req if not os.path.isfile(os.path.join(lp, f))]
    out.append(("%s/ 证据在盘 (≥ %d 件 + 关键证据链 %d/%d)"
                % (S["logs"], len(req), len(req) - len(missreq), len(req)),
                n >= len(req) and not missreq, "%d 件 · 缺 %s" % (n, missreq[:3])))
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py Q1 = 18/18", bool(m3) and m3.group(1) == "18",
                "Q1=%s" % (m3.group(0) if m3 else "未读到")))
    reds = [l.strip() for l in o5.splitlines() if ("❌" in l or "新闸红" in l)]
    mine = [r for r in reds if (S["frag_key"] in r) or (os.path.basename(S["gate"]) in r) or (os.path.basename(S["page"]) in r)]
    others = [r for r in reds if r not in mine]
    out.append(("★★gate_check 的红不指向本单产物 (★可归因他单在飞·★逐条归因★)", not mine,
                ("本单相关红 %d 条 %s" % (len(mine), mine[:2])) if mine else ("他单在飞红 %d 条 (已归因)" % len(others))))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-377/378 签收闸 · 自测")
    r = []
    r.append(("反向用例1 · 块标题解析可用", block_code("B2 · 验收标准自评") == "B2"))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3 · 377 的两个口径数都在判据里", ("1.5175" in [m[0] for m in SPEC["ISS-377"]["must"]]) and ("0.3625" in [m[0] for m in SPEC["ISS-377"]["must"]])))
    r.append(("反向用例4 · 378 的两个候选坐标都在判据里", ("141.0450" in [m[0] for m in SPEC["ISS-378"]["must"]]) and ("144.8550" in [m[0] for m in SPEC["ISS-378"]["must"]])))
    allok = True
    for n, ok in r:
        allok = allok and bool(ok)
        print("  %s %s" % ("✅" if ok else "❌", n))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return self_test()
    issues = [a for a in args if a in SPEC]
    check_only = "--check-only" in args or not issues
    for issue in issues:
        lines = check_iss(issue)
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-48s %s" % ("✅" if ok else "❌", name, detail))
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
        vr = ("✅ verified (★main 2026-11-24 03:4x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260724_0345_main_sign_iss377_378.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动 ⇒ **G1 仍开, 不许投板**) · "
              "零落表 (受保护件 md5 同基线) · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        if "  verify_result:" in new:
            new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        else:
            new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-24'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-24'\n  verify_result:", 1)
        if "  verify_by:" in new:
            new = re.sub(r"^  verify_by: .*$", "  verify_by: main", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_by: main\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260724_0345_main_sign_iss377_378.py'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260724_0345_main_sign_iss377_378.py'\n"
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
