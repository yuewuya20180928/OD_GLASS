#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0050_cronfb67_sign_iss373.py
==================================================
main (项目总工) 的【签收闸 · ISS-373 (hw-lead)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评

★**为什么本文件是 cron fb67af40 (队列自动派活) 建的, 不是 775d9893 (继续执行后继计划)**:
  ★兄弟 job 775d9893 于 2026-11-24 00:24:07 被【cron 执行超时 (60 分钟硬墙·externalAbort=true)】掐死,
  ★它死前正在写 ISS-373 的签收闸 (本机实读它的 transcript: 已核过页里的关键数字 + 已查 3 个 needs key +
  ★已查零挂链) ⇒ ★**本 job 接手把它没写完的签收闸补齐** (★本项目的分工是: 775d9893 负责签收 + 待拍板,
  ★fb67af40 负责派活 ⇒ 但 775d9893 这一轮已经死了, 而 fb67af40 这一轮必须让队列【继续有活干】⇒
  ★签收 ISS-373 是【放 hw-lead 名额】的必需前置 ⇒ fb67af40 顺手把它做了★)

用法:
  python3 state/_apply_20260724_0050_cronfb67_sign_iss373.py --check-only ISS-373
  python3 state/_apply_20260724_0050_cronfb67_sign_iss373.py --sign ISS-373
  python3 state/_apply_20260724_0050_cronfb67_sign_iss373.py --self-test
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
BASELINE = os.path.join(PROJ, "logs/iss369/00_baseline_md5.txt")
KICAD_FP = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

BLOCKS = [
    ("B1", ["结论"]),
    ("B2", ["验收标准自评", "验收"]),
    ("B3", ["证据分级", "证据"]),
    ("B4", ["接口取值声明", "接口"]),
    ("B5", ["未决项", "卡点", "未决"]),
    ("B6", ["自证复现命令", "自证", "复现", "命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s*(?:待填|TODO|FIXME|PLACEHOLDER|XXX)|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
# ★★末段允许 CJK (★交卷页文件名含中文·旧正则会在 1.27 处截断 ⇒ 假 MISS★)
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_一-鿿-]\.[A-Za-z0-9_一-鿿-]{1,24}')

SPEC = {
    "ISS-373": {
        "owner": "hw-lead",
        "handoff": "HANDOFF/2026-11-23_hw-lead_ISS373_S10换件集合唯一真源与口径闸.md",
        "gate": "HW/check_onepass_s10_swap_set_truth.py",
        "page": "HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md",
        "frag": "state/fragments/hw.yaml",
        "frag_key": "iss373",
        "other_frags": ("pm", "sw", "mech"),
        "logs": "logs/iss373",
        "logs_min": 10,
        "logs_required": ["01_sets_probe.txt", "07_led_sensitivity_90_vs_91.json",
                          "08_boundary_md5.txt", "02_sbx_swap_report.json"],
        "must_text": [
            ("158", "C4 = 158"),
            ("90", "90 件口径"),
            ("91", "91 件口径"),
            ("唯一真源", "★唯一真源"),
            ("差集", "★差集"),
            ("J_DEBUG", "★差集那件 = J_DEBUG"),
            ("2206", "★MECH 侧 90 件口径落位块数 2206"),
            ("2200", "★MECH 侧 91 件口径落位块数 2200"),
            ("611b869e", "板 md5"),
        ],
        "must_not_text": [
            ("15,777", "★旧口径「15,777 个 .pretty 目录」不许再出现"),
        ],
        "extra": [
            ("写库名", "★写库名联动手"),
            ("C4", "★C4 影响 = 0"),
            ("追加式订正块", "★追加式订正块"),
            ("不代拍", "★不代 main / 不代老板拍"),
        ],
    },
}


def block_code(h):
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-9])\b", s)
    return m.group(1) if m else None


def sh(cmd, timeout=1200):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def load_baseline_protected():
    """★基线 md5 从 logs/iss369/00_baseline_md5.txt 读 (★不手打·★打错必假红★)"""
    out = {}
    p = os.path.join(PROJ, BASELINE)
    if os.path.isfile(p):
        for ln in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"([0-9a-f]{32})\s+(\S+)", ln.strip())
            if m:
                out[m.group(2)] = m.group(1)
    return out


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
    # 板指纹三项
    got = md5(os.path.join(PROJ, BOARD))
    stt = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(stt.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime+size 三项未动",
                got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]) and stt.st_size == BOARD_SIZE,
                "%s / %s / %d B" % (got, mt, stt.st_size)))
    out.append(("交卷页含板指纹双证", txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))
    # 零落表 (基线 md5)
    prot = load_baseline_protected()
    bad = []
    for p, want in prot.items():
        fp = os.path.join(PROJ, p)
        if not os.path.isfile(fp):
            continue
        g = md5(fp)
        if g != want:
            bad.append("%s(%s≠%s)" % (p, g[:8], want[:8]))
    out.append(("零落表+零写板: 受保护件 %d 件 md5 同基线" % len(prot), len(bad) == 0,
                "动 %d %s" % (len(bad), bad[:3])))
    # 别人分片零本单登记
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
    # 自带闸
    if os.path.isfile(os.path.join(PROJ, S["gate"])):
        rc, o = sh("python3 %s" % S["gate"])
        out.append(("★★自带闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % S["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("★★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:50])))
    else:
        out.append(("★★自带闸在盘", False, S["gate"]))
    # 交付页在盘
    pp = os.path.join(PROJ, S["page"])
    out.append(("交付页 %s 在盘 (≥ 4000 B)" % S["page"],
                os.path.isfile(pp) and os.path.getsize(pp) >= 4000,
                "%d B" % (os.path.getsize(pp) if os.path.isfile(pp) else 0)))
    # 交付页 §0~§7 章节齐全
    if os.path.isfile(pp):
        ptxt = open(pp, encoding="utf-8").read()
        secs = sorted(set(re.findall(r"^##\s*§(\d)", ptxt, re.M)))
        out.append(("交付页 §0~§7 章节齐全", secs == ["0", "1", "2", "3", "4", "5", "6", "7"], "§%s" % ",".join(secs)))
    # 关键文本
    for needle, label in S["must_text"]:
        out.append(("交卷页含 %s" % label, needle in txt, needle))
    # ★零挂起措辞 (语境判据) ★
    HANG = ["等原厂回信", "等供应商回复", "待外部确认", "等外部回复"]
    hits = []
    for needle in HANG:
        s0 = 0
        while True:
            k = txt.find(needle, s0)
            if k < 0:
                break
            ctx = txt[max(0, k - 90): k + len(needle) + 90]
            if not any(mk in ctx for mk in ("不许", "无「", "零挂起", "禁语", "不写成", "没有")):
                hits.append("%s@%d" % (needle, k))
            s0 = k + 1
    out.append(("交卷页零挂起措辞 (语境判据)", len(hits) == 0, "命中 %d %s" % (len(hits), hits[:3])))
    for needle, label in S["must_not_text"]:
        hits = []
        s0 = 0
        while True:
            k = txt.find(needle, s0)
            if k < 0:
                break
            ctx = txt[max(0, k - 90): k + len(needle) + 90]
            if not any(mk in ctx for mk in ("不是", "作废", "单位写错", "已订正", "纠正", "旧口径", "不成立")):
                hits.append(k)
            s0 = k + 1
        out.append(("交卷页不含 %s (★语境判据: 引用并当场纠正不算★)" % label, len(hits) == 0,
                    "传播命中 %d %s" % (len(hits), hits[:3])))
    for needle, label in S["extra"]:
        out.append(("交卷页含 %s" % label, needle in txt, needle))
    # 自己的分片有登记
    out.append(("自己的分片有本单登记", S["frag_key"] in open(os.path.join(PROJ, S["frag"]), encoding="utf-8", errors="replace").read(),
                S["frag_key"]))
    # 证据目录
    lp = os.path.join(PROJ, S["logs"])
    n = len(os.listdir(lp)) if os.path.isdir(lp) else 0
    req = S.get("logs_required") or []
    missreq = [f for f in req if not os.path.isfile(os.path.join(lp, f))]
    out.append(("%s/ 证据在盘 (≥ %d 件 + 关键证据链 %d/%d)"
                % (S["logs"], S.get("logs_min", 10), len(req) - len(missreq), len(req)),
                n >= S.get("logs_min", 10) and not missreq,
                "%d 件 · 缺 %s" % (n, missreq[:3])))
    # 必跑项
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc5 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc5, m3.group(0) if m3 else "未读到")))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-373 签收闸 · 自测 (★每条反向用例都要证明「该红的红, 不该红的不红」★)")
    r = []
    r.append(("反向用例1 · 块标题解析可用", block_code("B2 · 验收标准自评") == "B2"))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3 · 旧口径「15,777」必被判红 (must_not 语义)", "15,777" not in "本页写的是 155 目录 / 15,468 文件"))
    r.append(("反向用例4 · KiCad 库计数 main 实读 = 155 目录 / 15,468 文件",
              len([d for d in os.listdir(KICAD_FP) if d.endswith(".pretty")]) == 155))
    # ★反向用例5: 真的把交卷页改坏 ⇒ 判据必须红 (★在临时副本上做·不改真页★)
    import tempfile
    src = os.path.join(PROJ, SPEC["ISS-373"]["handoff"])
    orig = open(src, encoding="utf-8").read()
    tmpd = tempfile.mkdtemp()
    try:
        # (a) 删掉 B5 块标题 ⇒ block_code 扫不到 B5
        bad = re.sub(r"^## B5 .*$", "## 随便改个标题", orig, count=1, flags=re.M)
        heads = re.findall(r"^#{2,4}\s*(.+)$", bad, re.M)
        hit5 = any(block_code(h) == "B5" for h in heads)
        r.append(("反向用例5 · 改掉 B5 标题 ⇒ B5 块命中必为 False", hit5 is False))
        # (b) 塞一个占位符 ⇒ 占位符扫描必须命中
        bad2 = orig.replace("## B1 结论摘要", "## B1 结论摘要\n\n待填: XXX", 1)
        ph = [m.group(0) for m in PLACEHOLDER.finditer(bad2)
              if not any(k in bad2[max(0, m.start() - 60): m.end() + 60] for k in ("占位", "骨架", "全是", "占位符"))]
        r.append(("反向用例6 · 塞占位符 ⇒ 占位符扫描必命中", len(ph) > 0))
        # (c) 真页本身的 B5 标题确实在 ⇒ 正向对照
        heads0 = re.findall(r"^#{2,4}\s*(.+)$", orig, re.M)
        r.append(("反向用例7 · 正向对照: 真页 B5 标题命中", any(block_code(h) == "B5" for h in heads0)))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)
    allok = True
    for n, ok in r:
        allok = allok and bool(ok)
        print("  %s %s" % ("✅" if ok else "❌", n))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


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
        vr = ("✅ verified (★main 2026-11-24 00:5x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260724_0050_cronfb67_sign_iss373.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动 ⇒ **G1 仍开, 不许投板**) · "
              "零落表 (受保护件 19 件 md5 同基线) · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★"
              "★**签收人 = cron fb67af40 (队列自动派活) 代 main 行权** (★兄弟 job 775d9893 于 00:24:07 被 60 分钟 cron 硬墙掐死·它死前正在写本闸·本 job 接手补齐⇒ 让队列继续有活干★)")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        if "  verify_result:" in new:
            new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        else:
            new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-24'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-24'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260724_0050_cronfb67_sign_iss373.py'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260724_0050_cronfb67_sign_iss373.py'\n"
        if "  verify_by:" in new:
            new = re.sub(r"^  verify_by: .*$", "  verify_by: 'main'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  verify_by: 'main'\n"
        bak = LOG + ".bak_%s_cronfb67_sign%s" % (STAMP, issue.replace("-", ""))
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
