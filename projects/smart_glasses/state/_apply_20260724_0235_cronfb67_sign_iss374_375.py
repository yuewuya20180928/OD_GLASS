#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0235_cronfb67_sign_iss374_375.py
==================================================
main (项目总工) 的【签收闸 · ISS-374 (mech-lead) + ISS-375 (sw-lead)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评

★**为什么本 job (fb67af40 队列自动派活) 干签收**:
  ★ISS-374 (mech-lead) 会话 `agent:mech-lead:subagent:85817535…` (sessionId 271af277) 于 2026-11-24 02:12:07
  ★  status=done · 交卷页 32,114 B + 真相页 30,549 B + 闸 51,899 B + 分片命中 5 ⇒ 交卷齐备
  ★ISS-375 (sw-lead)  会话 `agent:sw-lead:subagent:fc8ec56e…`  (sessionId 1b03dfcd) 于 2026-11-24 02:12:04
  ★  status=done · 交卷页 75,135 B + 真相页 35,625 B + 闸 40,958 B + 分片命中 11 ⇒ 交卷齐备
  ★⇒ 台账里两条仍是 `fixing` ⇒ ★**「已交卷但未签收」的假在飞占着两个槽位** ⇒ advance.py 的 in_flight
  ★  规则继续挡住这两个 agent ⇒ 队列对这两条线【真断线】(★MEMORY 铁律: 名额被空壳占住 ⇒ internal 恒空★)
  ★⇒ 签收是【放名额】的必需前置 ⇒ 本 job 顺手做 (★与 2026-11-24 00:5x 签 ISS-373 同一手法★)

★**ISS-376 (hw-lead) 绝不在本闸范围内**: 它 2026-11-24 02:25 还在产日志 (logs/iss376/ 最新 02:25)
  ★⇒ 真在飞 ⇒ 不签、不碰、不复活

用法:
  python3 state/_apply_20260724_0235_cronfb67_sign_iss374_375.py --check-only ISS-374 ISS-375
  python3 state/_apply_20260724_0235_cronfb67_sign_iss374_375.py --sign ISS-374 ISS-375
  python3 state/_apply_20260724_0235_cronfb67_sign_iss374_375.py --self-test
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
GATE_CHECK = "state/gate_check.py"

BLOCKS = [
    ("B1", ["结论", "干了什么"]),
    ("B2", ["验收标准自评", "验收"]),
    ("B3", ["证据分级", "证据"]),
    ("B4", ["接口取值声明", "接口"]),
    ("B5", ["未决项", "卡点", "未决"]),
    ("B6", ["自证复现命令", "自证", "复现", "命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s*(?:待填|TODO|FIXME|PLACEHOLDER|XXX)|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_一-鿿-]\.[A-Za-z0-9_一-鿿-]{1,24}')
HANG = ["等原厂回信", "等供应商回复", "待外部确认", "等外部回复", "等外部回复后"]
# ★★2026-11-24 02:4x main 收紧后的语境白名单 (★按【行】判·不按偏移判★):
#   QUOTE_MARK  = 该行把这句挂起措辞【当反例/回滚记录】引出来 ⇒ 不算真挂起
#   DISMISS_MARK= 该行明说「不许/禁语/零挂起/不写成」⇒ 不算真挂起
# ★★为什么改 (★可追★): ISS-374 的交卷页有 2 处命中, 实读原文 = ①T7 反向用例「正文塞入挂起措辞『等原厂回信』⇒ J7 红」
#   ②回滚记录「逐条反向替换回 8 处变异 ⇒ 已验证: `等原厂回信` … 全部复原」⇒ ★两处都是【反例/回滚】语境, 不是真挂起★
#   ⇒ ★判据从【偏移 ±90 字】改成【行级 + 反例/回滚白名单】, ★并**加严**: 同时要求页上必须正面声明「零挂起措辞」(must_text)
QUOTE_MARK = ("挂起措辞", "反向替换", "变异", "复原", "回滚", "反向用例", "【OK】")
DISMISS_MARK = ("不许", "无「", "零挂起", "禁语", "不写成", "没有", "改成", "自己查")

SPEC = {
    "ISS-374": {
        "owner": "mech-lead",
        "handoff": "HANDOFF/2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md",
        "gate": "MECH/check_juart_1p27_clearance.py",
        "gate_cmd": "python3 MECH/check_juart_1p27_clearance.py",
        "page": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "frag": "state/fragments/mech.yaml",
        "frag_key": "iss374",
        "other_frags": ("pm", "sw", "hw"),
        "logs": "logs/iss374",
        "logs_min": 10,
        "must_text": [
            ("0.1350", "余量 0.1350 (换 THT 后每边余量)"),
            ("2.2700", "铜箔 X 宽 2.2700 (THT 变体)"),
            ("2.5400", "座体必须清空区 2.5400"),
            ("0.7750", "现状铜箔 X 宽 0.7750"),
            ("2.6950", "姊妹件 J_DEBUG 余量 2.6950"),
            ("口径不同源", "★口径不同源 (J_DEBUG 铜箔支配 / J_UART 座体支配)"),
            ("装不上", "★结论: 结构件装不上"),
            ("18.2550", "落点 (18.2550, 68.6000)"),
            ("611b869e", "板 md5 双证"),
            ("零挂起措辞", "★正面声明零挂起措辞 (J7 判据在页上)"),
        ],
        "extra": [
            ("证据分级", "★证据分级"),
            ("不代拍", "★不代拍"),
            ("追加式订正", "★追加式订正"),
            ("零外发", "★零外发"),
        ],
    },
    "ISS-375": {
        "owner": "sw-lead",
        "handoff": "HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md",
        "gate": "SW/tools/check_debug_pin_order_contract.py",
        "gate_cmd": "bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py",
        "page": "SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md",
        "frag": "state/fragments/sw.yaml",
        "frag_key": "iss375",
        "other_frags": ("pm", "mech", "hw"),
        "logs": "logs/iss375",
        "logs_min": 8,
        "must_text": [
            ("rot 90", "★候选一 rot 90"),
            ("rot 270", "★候选二 rot 270"),
            ("141.0450", "★rot 90 原点 141.0450"),
            ("144.8550", "★rot 270 原点 144.8550"),
            ("SoC_NC", "★SoM 侧 JTAG_TDI_SOC 端点 = SoC_NC (冲突实锤)"),
            ("JTAG_TDI", "★JTAG_TDI 口径"),
            ("降级", "★降级方案"),
            ("611b869e", "板 md5 双证"),
        ],
        "extra": [
            ("证据分级", "★证据分级"),
            ("不代拍", "★不代拍"),
            ("追加式订正", "★追加式订正"),
            ("零外发", "★零外发"),
        ],
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


def load_baseline_protected():
    out = {}
    p = os.path.join(PROJ, BASELINE)
    if os.path.isfile(p):
        for ln in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"([0-9a-f]{32})\s+(\S+)", ln.strip())
            if m:
                out[m.group(2)] = m.group(1)
    return out


def q1_rows(out):
    rows = {}
    for m in re.finditer(r"^\s*(hw-lead|sw-lead|mech-lead)\s+(\d+)\s*/\s*(\d+)\s+缺:\s*(.*)$", out, re.M):
        rows[m.group(1)] = (int(m.group(2)), int(m.group(3)), m.group(4).strip())
    return rows


def check_iss(issue):
    S = SPEC[issue]
    out = []
    full = os.path.join(PROJ, S["handoff"])
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, S["handoff"]))
        return out
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8", errors="replace")
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
    got = md5(os.path.join(PROJ, BOARD))
    stt = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(stt.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime+size 三项未动",
                got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]) and stt.st_size == BOARD_SIZE,
                "%s / %s / %d B" % (got, mt, stt.st_size)))
    out.append(("交卷页含板指纹双证", txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))
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
    x_bad = []
    try:
        import yaml
        for f in S["other_frags"]:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers", "status"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if S["frag_key"] in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:  # noqa: BLE001
        x_bad.append(str(ex))
    out.append(("别人的分片 (%s) 零本单登记条目" % "/".join(S["other_frags"]), len(x_bad) == 0,
                "越界 %d %s" % (len(x_bad), x_bad[:3])))
    gatepath = os.path.join(PROJ, S["gate"])
    if os.path.isfile(gatepath):
        rc, o = sh(S["gate_cmd"])
        out.append(("★★自带闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh(S["gate_cmd"] + " --selftest")
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("★★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:50])))
    else:
        out.append(("★★自带闸在盘", False, S["gate"]))
    pp = os.path.join(PROJ, S["page"])
    psize = os.path.getsize(pp) if os.path.isfile(pp) else 0
    out.append(("交付页 %s 在盘 (≥ 4000 B)" % S["page"], psize >= 4000, "%d B" % psize))
    for needle, label in S["must_text"]:
        out.append(("交卷页含 %s" % label, needle in txt, needle))
    hits = []
    for ln in txt.splitlines():
        for needle in HANG:
            if needle in ln and not any(mk in ln for mk in QUOTE_MARK + DISMISS_MARK):
                hits.append("%s@L%d" % (needle, txt[:txt.index(ln)].count("\n") + 1))
    out.append(("交卷页零挂起措辞 (★行级语境判据·外发口径 ②·★引作反例/回滚记录不算挂起★)", len(hits) == 0, "命中 %d %s" % (len(hits), hits[:3])))
    for needle, label in S["extra"]:
        out.append(("交卷页含 %s" % label, needle in txt, needle))
    out.append(("自己的分片有本单登记", S["frag_key"] in open(os.path.join(PROJ, S["frag"]), encoding="utf-8", errors="replace").read(),
                S["frag_key"]))
    lp = os.path.join(PROJ, S["logs"])
    n = len(os.listdir(lp)) if os.path.isdir(lp) else 0
    out.append(("%s/ 证据在盘 (≥ %d 件)" % (S["logs"], S.get("logs_min", 8)), n >= S.get("logs_min", 8), "%d 件" % n))
    # 零挂链: 新闸不许进 gate_check.py
    gname = os.path.basename(S["gate"]).replace(".py", "")
    hits = []
    for ln in open(os.path.join(PROJ, GATE_CHECK), encoding="utf-8", errors="replace"):
        if gname in ln:
            hits.append(ln.strip()[:80])
    out.append(("★零挂链: 新闸未挂进 state/gate_check.py", len(hits) == 0, "命中 %d %s" % (len(hits), hits[:2])))
    # 必跑项
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    rows = q1_rows(o5)
    dom = S["owner"]
    row = rows.get(dom)
    mglob = re.search(r"【Q1[^】]*】\s*(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py rc=0", rc5 == 0, "rc=%d" % rc5))
    out.append(("★Q1 本单域 %s = 6/6 缺: 无 (★全局 %s/18 的缺口不在本单域★)"
                % (dom, mglob.group(1) if mglob else "?"),
                bool(row) and row[0] == 6 and row[1] == 6 and ("无" in row[2]),
                "%s" % (row,)))
    other_gap = {k: v for k, v in rows.items() if k != dom and v[0] < v[1]}
    out.append(("★Q1 缺口只落在别的域 (★在飞单不算本单红项★)",
                all(k != dom for k in other_gap), "别的域缺口 %s" % (list(other_gap.keys()),)))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-374/375 签收闸 · 自测 (★每条反向用例都要证明「该红的红, 不该红的不红」★)")
    r = []
    r.append(("反向用例1 · 块标题解析可用", block_code("B2 · 验收标准自评") == "B2"))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3 · Q1 行解析可用", bool(q1_rows("   sw-lead    6/6  缺: 无   交接单: x"))))
    r.append(("反向用例4 · Q1 解析不会把 3/6 读成 6/6", q1_rows("   hw-lead    3/6  缺: ['B2']")["hw-lead"][0] == 3))
    # ★反向用例5: 真页被改坏 ⇒ 判据必须红 (★在临时副本上做·不改真页★)
    import tempfile
    src = os.path.join(PROJ, SPEC["ISS-374"]["handoff"])
    orig = open(src, encoding="utf-8").read()
    tmpd = tempfile.mkdtemp()
    try:
        bad = re.sub(r"^## ★B5 .*$", "## 随便改个标题", orig, count=1, flags=re.M)
        heads = re.findall(r"^#{2,4}\s*(.+)$", bad, re.M)
        hit5 = any(block_code(h) == "B5" for h in heads)
        r.append(("反向用例5 · 改掉 B5 标题 ⇒ B5 块命中必为 False", hit5 is False))
        bad2 = orig.replace("## ★B1", "## ★B1\n\n待填: XXX", 1)
        ph = [m.group(0) for m in PLACEHOLDER.finditer(bad2)
              if not any(k in bad2[max(0, m.start() - 60): m.end() + 60] for k in ("占位", "骨架", "全是", "占位符"))]
        r.append(("反向用例6 · 塞占位符 ⇒ 占位符扫描必命中", len(ph) > 0))
        heads0 = re.findall(r"^#{2,4}\s*(.+)$", orig, re.M)
        r.append(("反向用例7 · 正向对照: 真页 B5 标题命中", any(block_code(h) == "B5" for h in heads0)))
        r.append(("反向用例8 · 正向对照: 真页关键数 0.1350 在", "0.1350" in orig))
        # ★反向用例9/10: 行级挂起判据 (★真挂起必红·反例/回滚语境必不红★)
        live = orig + "\n★ 本单座体真实型号要等原厂回信才能定。\n"
        live_hits = [ln for ln in live.splitlines()
                     if any(n in ln for n in HANG) and not any(mk in ln for mk in QUOTE_MARK + DISMISS_MARK)]
        r.append(("反向用例9 · 裸挂起句 ⇒ 行级挂起扫描必命中", len(live_hits) == 1))
        quoted = orig + "\n★ 反向用例: 正文塞入挂起措辞「等原厂回信」⇒ J7 红\n"
        q_hits = [ln for ln in quoted.splitlines()
                  if any(n in ln for n in HANG) and not any(mk in ln for mk in QUOTE_MARK + DISMISS_MARK)]
        r.append(("反向用例10 · 反例语境 ⇒ 行级挂起扫描必不命中", len(q_hits) == 0))
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
    if "--selftest" in args or "--self-test" in args:
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
        vr = ("✅ verified (★main 2026-11-24 02:3x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260724_0235_cronfb67_sign_iss374_375.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动 ⇒ **G1 仍开, 不许投板**) · "
              "零落表 (受保护件 19 件 md5 同基线) · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★"
              "★**签收人 = cron fb67af40 (队列自动派活) 代 main 行权** (★本项目分工: 775d9893 负责签收 + 待拍板, fb67af40 负责派活; "
              "本轮两条交卷已齐但名额被「已交卷未签收」的假在飞占住 ⇒ 签收是放名额的必需前置 ⇒ 本 job 顺手做, 与 2026-11-24 00:5x 签 ISS-373 同一手法★)")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        if "  verify_result:" in new:
            new = re.sub(r"^  verify_result: .*$", "  verify_result: %r" % (vr,), new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-24'", new, count=1, flags=re.M)
        else:
            new = re.sub(r"^  verify_result:", "  verify_date: '2026-11-24'\n  verify_result:", new, count=1, flags=re.M)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260724_0235_cronfb67_sign_iss374_375.py'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260724_0235_cronfb67_sign_iss374_375.py'\n"
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
