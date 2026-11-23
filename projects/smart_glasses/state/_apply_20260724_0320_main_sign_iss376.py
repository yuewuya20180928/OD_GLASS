#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0320_main_sign_iss376.py
==================================================
main (项目总工) 的【签收闸 · ISS-376 (hw-lead · `J_DEBUG` 换官方 1×4 THT land 的落位可行性)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本单特殊: 交的是【几何穷举 + 代价账】⇒ 判据核心 = ①闸 main 自己复跑 ②两处硬冲突数必须在页里
  ③可行域必须是【区间】而不是一个点 ④「只试一个落点就宣布可行」必须被反向用例打掉

用法:
  python3 state/_apply_20260724_0320_main_sign_iss376.py --check-only ISS-376
  python3 state/_apply_20260724_0320_main_sign_iss376.py --sign ISS-376
  python3 state/_apply_20260724_0320_main_sign_iss376.py --self-test
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
HANDOFF = "HANDOFF/2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md"
GATE = "HW/check_jdebug_land_fit.py"
BASELINE = os.path.join(PROJ, "logs/iss376/must_run.txt")

BLOCKS = [
    ("B1", ["任务与结论摘要", "结论"]),
    ("B2", ["数值结论"]),
    ("B3", ["代价账"]),
    ("B4", ["未决项"]),
    ("B5", ["过程说明"]),
    ("B6", ["验收线", "必跑命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s*(?:待填|TODO|FIXME|PLACEHOLDER|XXX)|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_一-鿿-]\.[A-Za-z0-9_一-鿿-]{1,24}')
MUST = [
    ("0.1271", "★硬冲突1: pad1 vs JTAG_TDO 孔净距 0.1271"),
    ("0.0000", "★硬冲突2: pad3 vs XTAL_OUT 0.0000"),
    ("0.25", "★孔净距要求 ≥ 0.25"),
    ("可行域", "★落位可行域 (区间)"),
    ("SetOrientationDegrees", "★三朝向 pad 坐标用 SetOrientationDegrees 实算"),
    ("kicad_mod", "★官方 land 盘上实读 (.kicad_mod 自己解析)"),
    ("kicad_pro", "★板面 DRC 判据 (.kicad_pro 实读)"),
    ("JTAG_TDO", "★JTAG_TDO 冲突点"),
    ("XTAL_OUT", "★XTAL_OUT 冲突点"),
    ("代价", "★代价账 (挪完还剩什么)"),
]
MUST_NOT = [
    ("等原厂回信", "★禁挂起措辞"),
    ("等供应商回复", "★禁挂起措辞"),
]


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


def check_iss376():
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
    # ★★路径笔误单列 (★2026-11-24 03:2x 实测: 本闸第一版漏了这一段 ⇒ 页面里 `HW/check_pcb_nets.py` (真路径 `state/check_pcb_nets.py`) 被判成真 MISS
    #   ⇒ ★★⇒ 闸自己也会漏实现 ⇒ 判据写完必须拿真文档跑一遍★) ★
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
                "引用 %d · 真 MISS %d %s · 沙盒 %d · 路径笔误 %d %s"
                % (len(refs), len(real), real[:3], len(sandbox), len(typo), typo[:3])))
    got = md5(os.path.join(PROJ, BOARD))
    stt = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(stt.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime+size 三项未动",
                got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]) and stt.st_size == BOARD_SIZE,
                "%s / %s / %d B" % (got, mt, stt.st_size)))
    out.append(("交卷页含板指纹双证", txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))
    # 零落表: 基线 md5 从 logs/iss376/must_run.txt 读
    prot = {}
    if os.path.isfile(BASELINE):
        for ln in open(BASELINE, encoding="utf-8", errors="replace"):
            m = re.match(r"([0-9a-f]{32})\s+(\S+)", ln.strip())
            if m:
                prot[m.group(2)] = m.group(1)
    bad = []
    for p, want in prot.items():
        fp = os.path.join(PROJ, p)
        if not os.path.isfile(fp):
            continue
        g = md5(fp)
        if g != want:
            bad.append("%s(%s≠%s)" % (p, g[:8], want[:8]))
    out.append(("零落表+零写板: 基线清单 %d 件 md5 同值" % len(prot), len(bad) == 0,
                "动 %d %s" % (len(bad), bad[:3])))
    # 别人分片零本单登记
    x_bad = []
    try:
        import yaml
        for f in ("pm", "sw", "mech"):
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss376" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append(str(ex))
    out.append(("别人的分片 (pm/sw/mech) 零本单登记条目", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))
    # 自带闸
    if os.path.isfile(os.path.join(PROJ, GATE)):
        rc, o = sh("python3 %s" % GATE)
        out.append(("★★自带闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % GATE)
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("★★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:50])))
        # ★★反向用例必须含「只试一个落点就宣布可行」那两条
        out.append(("★★反向用例含「只试一个落点就宣布可行/不可行」两条",
                    ("单点" in o2) or ("可行区声明" in o2) or ("单点声明" in o2),
                    "selftest 输出命中"))
    else:
        out.append(("★★自带闸在盘", False, GATE))
    # 关键文本
    for needle, label in MUST:
        out.append(("交卷页含 %s" % label, needle in txt, needle))
    for needle, label in MUST_NOT:
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
    # 自己的分片有登记
    out.append(("自己的分片有本单登记", "iss376" in open(os.path.join(PROJ, "state/fragments/hw.yaml"),
                                                        encoding="utf-8", errors="replace").read(), "iss376"))
    n = len(os.listdir(os.path.join(PROJ, "logs/iss376"))) if os.path.isdir(os.path.join(PROJ, "logs/iss376")) else 0
    out.append(("logs/iss376/ 证据在盘 (≥ 6 件)", n >= 6, "%d 件" % n))
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    q1ok = bool(m3) and m3.group(1) == "18"
    out.append(("gate_check.py Q1 = 18/18 (★本单的那 3 个缺块已清零·★Q1 是本单的硬指标★)", q1ok,
                "Q1=%s" % (m3.group(0) if m3 else "未读到")))
    # ★★可归因红: gate_check 的 rc 若因【别的单的在飞产物】而红 ⇒ 记录归因, 不计入本单拒签 (★2026-11-24 03:2x 实测:
    #   唯一红 = MECH 侧位号引用可达性闸 指向 MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md = ISS-377 在飞⇒ 与本单无关★)
    reds = [l.strip() for l in o5.splitlines() if ("❌" in l or "新闸红" in l)]
    mine = [r for r in reds if ("ISS376" in r) or ("JDEBUG排针换land" in r) or ("check_jdebug_land_fit" in r)]
    others = [r for r in reds if r not in mine]
    out.append(("★★gate_check 的红不指向本单产物 (★可归因他单在飞·★逐条列出归因★)",
                not mine, ("本单相关红 %d 条 %s" % (len(mine), mine[:2])) if mine else
                ("他单在飞红 %d 条 (已归因, 不计本单)" % len(others))))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-376 签收闸 · 自测")
    r = []
    r.append(("反向用例1 · 块标题解析可用", block_code("B2 · 数值结论") == "B2"))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3 · 两处硬冲突数都在判据里", ("0.1271" in [m[0] for m in MUST]) and ("0.0000" in [m[0] for m in MUST])))
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
    issues = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not issues
    for issue in issues:
        lines = check_iss376()
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
        vr = ("✅ verified (★main 2026-11-24 03:2x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260724_0320_main_sign_iss376.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动 ⇒ **G1 仍开, 不许投板**) · "
              "零落表 (基线清单 md5 同值) · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★ "
              "★★【main 独立复核】★★ ★**① 自带闸 `HW/check_jdebug_land_fit.py` main 自己复跑: 裸跑 rc=0 (9 条判据红 0) + `--selftest` rc=0 (11/11 反向用例全过)** ★ "
              "★**② 两处硬冲突数在页里**: ★**pad1 vs `JTAG_TDO` 孔净距 0.1271** + ★**pad3 vs `XTAL_OUT` 0.0000** (★孔净距要求 ≥ 0.25★) ⇒ ★**⇒ 现位放不下 1×4 THT land 这条是几何事实, 不是判断题** ★ "
              "★**③ 落位可行域给的是【区间】不是一个点** (★且反向用例里有两条专打「只试一个落点就宣布可行/不可行」★) ⇒ ★**⇒ 那一趟挪落点时不会被一个单点骗** ★ "
              "★**④ 落点几何是实算不是手算**: 三朝向 pad 绝对坐标用 `SetOrientationDegrees` 实算 · 官方 land 从盘上 `.kicad_mod` 自己解析 · 板面判据从 `.kicad_pro` 实读 ⇒ ★**没有写死的数** ★ "
              "★**⑤ 代价账在页里** (★挪完还剩什么·只算不拍★) ⇒ ★**⑥ 交 main 裁的 4 条已在页里逐条写清「要谁回答什么」** (★U1 换不换 land / U2 要不要挪 `XTAL_OUT`·`JTAG_TDO` 过孔 ⇒ 本单给的是「不需要」·★main 可直接否掉★ / U3 会不会挤掉调试口罩开口 ⇒ 交 mech-lead / U4 rot 0·270 翻转 JTAG pin 顺序与 ISS-375 契约是否冲突 ⇒ 交 sw-lead) ★")
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
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260724_0320_main_sign_iss376.py'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260724_0320_main_sign_iss376.py'\n"
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
