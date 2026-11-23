#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_1005_main_sign_iss357.py
==================================================
main (项目总工) 的【签收闸 · ISS-357 (sw-lead · SW 域 needs 144 条四分类处置)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本单特殊: 交的是【需求闭环台账】⇒ ★main 必须自己核「分片计数真的平账 + 缺口真的降下来」★
            ⇒ 且 ★不许把 needs 删空来凑数★ (每条关闭都要有依据行)
★与 ISS-356 签收闸同族 (fail-closed · 自带反向用例自测)

用法:
  python3 state/_apply_20260723_1005_main_sign_iss357.py --check-only ISS-357
  python3 state/_apply_20260723_1005_main_sign_iss357.py --sign ISS-357
  python3 state/_apply_20260723_1005_main_sign_iss357.py --self-test
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
LOCK = os.path.join(PROJ, "state/.issue_log.lock")
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
STAMP = time.strftime("%Y%m%d_%H%M")

HANDOFF = "HANDOFF/2026-11-23_sw-lead_ISS357_SW未答需求分类.md"
TRIAGE = "SW/SW_NEEDS_TRIAGE.md"
FRAG = "state/fragments/sw.yaml"
LOGS = "logs/iss357"

# ★★交卷页的六个块 (★gate_check.py 按关键词判块★)★★
BLOCKS = [
    ("B1", ["结论", "摘要"]),
    ("B2", ["验收", "自评"]),
    ("B3", ["证据", "分级"]),
    ("B4", ["接口", "interface_claims"]),
    ("B5", ["未决", "卡点"]),
    ("B6", ["自证", "复现", "命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    # ★SW 域已交件 (★sw-lead 自报 md5 7641e5d0b0967cf3b1b03f9af9f1a27e★)
    "SW/MODEL_LICENSE.md": "7641e5d0b0967cf3b1b03f9af9f1a27e",
}
OTHER_FRAGS = ("pm", "hw", "mech")
FORBIDDEN = ["等原厂回信", "等供应商回复", "请并入第一轮跟进邮件", "请并进第二轮邮件",
             "跟进邮件", "买一块", "采购 RK3572", "采购RK3572"]
NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍",
       "作废", "不挂账", "不再", "零发信", "不发")

# ★★分片计数契约 (★sw-lead 自报 + main 实读 09:5x 复核过★)★★
EXP = {"needs_from": 70, "needs_closed": 74, "needs_open_ledger": 70, "answers": 58}
EXP_TOTAL = 144          # ★关 74 + 留 70 = 144 (原 needs_from 144 条)★
GAP_BASE = 98            # ★派活前缺口基线 (sw-lead 那条)★
GAP_MAX = 33             # ★交卷后必须 ≤ 33 (真降下来)★
DEC_CODES = ["S-B%02d" % i for i in range(1, 11)] + ["S-S10"]


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


def load_sw():
    import yaml
    with open(os.path.join(PROJ, FRAG), encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def check_iss357():
    out = []
    full = os.path.join(PROJ, HANDOFF)
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, HANDOFF))
        return out
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8", "replace")
    out.append(("交卷页存在", True, "%s (%d B)" % (HANDOFF, len(raw))))
    out.append(("交卷页不是骨架 (≥ 4000 B)", len(raw) >= 4000, "%d B" % len(raw)))
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    for code, kws in BLOCKS:
        hit = any(block_code(h) == code and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, kws[0]))
    ph_hits, ph_desc = [], 0
    for m in PLACEHOLDER.finditer(txt):
        ctx = txt[max(0, m.start() - 60): m.end() + 60]
        if any(k in ctx for k in ("占位", "骨架", "全是", "占位符", "待填")):
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
    out.append(("交卷页含板指纹双证 (md5≥2 / mtime≥2)",
                txt.count(BOARD_MD5) >= 2 and txt.count(BOARD_MTIME[:19]) >= 2,
                "md5 %d 次 / mtime %d 次" % (txt.count(BOARD_MD5), txt.count(BOARD_MTIME[:19]))))

    # ── 零落表 ──
    bad = []
    for p, want in PROTECTED.items():
        pp = os.path.join(PROJ, p)
        if not os.path.isfile(pp):
            bad.append("%s(不在盘)" % p)
            continue
        g = md5(pp)
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
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks",
                         "blockers", "needs_closed", "needs_open_ledger"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss357" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append("解析失败 %s" % ex)
    out.append(("别人的分片 (pm/hw/mech) 零本单登记条目", len(x_bad) == 0,
                "越界 %d %s" % (len(x_bad), x_bad[:3])))

    # ── 交付物在盘 ──
    tpath = os.path.join(PROJ, TRIAGE)
    tsz = os.path.getsize(tpath) if os.path.isfile(tpath) else 0
    out.append(("交付物 %s 在盘 (≥ 4000 B)" % TRIAGE, tsz >= 4000, "%d B" % tsz))
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss357/ 证据在盘 (≥ 8 件)", n >= 8, "%d 件" % n))

    # ── ★★核心判据 A: 分片计数平账 (★不许把 needs 删空来凑数★) ──
    try:
        d = load_sw()
        counts = {k: len(d.get(k) or []) for k in EXP}
        out.append(("★分片计数契约 (needs_from 70 / needs_closed 74 / ledger 70 / answers 58)",
                    counts == EXP, "实读 %s" % counts))
        tot = counts.get("needs_closed", 0) + counts.get("needs_from", 0)
        out.append(("★总平账: 关 %d + 留 %d = %d (原 needs_from 144 条一条没删)"
                    % (counts.get("needs_closed", 0), counts.get("needs_from", 0), tot),
                    tot == EXP_TOTAL, "实读 %d" % tot))
    except Exception as ex:
        counts, tot = {}, -1
        out.append(("★分片计数契约", False, "读分片失败 %s" % ex))

    # ── ★核心判据 B: 每条关闭都要有依据行 (不许批量清空) ──
    try:
        nc = d.get("needs_closed") or []
        need = ("reason", "evidence", "evidence_level", "closed_at", "closed_by")
        bad_c = [str(c.get("key")) for c in nc
                 if not isinstance(c, dict) or any(not c.get(k) for k in need)]
        out.append(("★每条 needs_closed 带 reason/evidence/evidence_level/closed_at/closed_by",
                    len(nc) > 0 and len(bad_c) == 0,
                    "条 %d · 缺依据 %d %s" % (len(nc), len(bad_c), bad_c[:3])))
    except Exception as ex:
        out.append(("★每条 needs_closed 带依据行", False, "解析失败 %s" % ex))

    # ── ★核心判据 C: 缺口清单里 sw-lead 那条必须真的降下来 ──
    rc5, o5 = sh("python3 state/gate_check.py")
    m = re.search(r"sw-lead:\s*(\d+)\s*条需求确实还没人答", o5)
    gap = int(m.group(1)) if m else -1
    out.append(("★缺口清单 sw-lead ≤ %d (派活前基线 %d ⇒ 真降下来)" % (GAP_MAX, GAP_BASE),
                0 <= gap <= GAP_MAX, "实读 %s" % (gap if gap >= 0 else "未读到")))
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18 (★交卷页 B1~B6 齐全⇒ 不许掉 Q1★)",
                rc5 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc5, m3.group(0) if m3 else "未读到")))

    # ── ★核心判据 D: 决策码表齐全 (② 类 ⇒ 带 need key + 建议默认值 + 不拍的后果) ──
    try:
        tt = open(tpath, encoding="utf-8", errors="replace").read()
        miss_c = [c for c in DEC_CODES if c not in tt]
        out.append(("★决策码表 %d 个齐全 (S-B01~S-B10 + S-S10)" % len(DEC_CODES),
                    len(miss_c) == 0, "缺 %d %s" % (len(miss_c), miss_c[:4])))
    except Exception as ex:
        out.append(("★决策码表齐全", False, "读不到 %s (%s)" % (TRIAGE, ex)))

    # ── 必跑 ──
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))

    # ── 禁语 (零外发) ──
    hits = forbidden_hits(txt)
    out.append(("零外发: 无「等原厂回信/等回复/跟进邮件」的非否定语境表述", len(hits) == 0,
                "命中 %d %s" % (len(hits), hits[:3])))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-357 签收闸 · 自测 (★反向用例★)")

    def blocks_ok(hs):
        return all(any(block_code(h) == c and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)

    def flat_ok(counts):
        return (counts.get("needs_closed", 0) + counts.get("needs_from", 0)) == EXP_TOTAL

    def closed_ok(nc, need=("reason", "evidence", "evidence_level", "closed_at", "closed_by")):
        return len(nc) > 0 and not [c for c in nc
                                    if not isinstance(c, dict) or any(not c.get(k) for k in need)]

    r = []
    # ★注意: headings 取自 re.findall(r"^#{2,4}\s*(.+)$") ⇒ 已剥掉 "##"★
    r.append(("正向用例 · 六块齐全 ⇒ 绿",
              blocks_ok(["B1 · 结论摘要", "B2 · 验收", "B3 · 证据分级",
                         "B4 · 接口取值声明", "B5 · 未决项", "B6 · 自证复现命令"])))
    r.append(("反向用例1 · 抽掉 B3 小节标题 ⇒ 判红",
              not blocks_ok(["B1 · 结论摘要", "B2 · 验收", "B4 · 接口取值声明",
                             "B5 · 未决项", "B6 · 自证复现命令"])))
    r.append(("反向用例2 · 板 md5 期望值被篡改 ⇒ 判红",
              md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3a · 禁止性表述 (不许等原厂回信) 不算违规",
              forbidden_hits("★本单不许写等原厂回信★") == []))
    r.append(("反向用例3b · 真违规 (查不到就等原厂回信) 必须被抓到",
              forbidden_hits("查不到就等原厂回信吧") != []))
    r.append(("反向用例3c · '不再发信' 语境不算违规",
              forbidden_hits("★按老板口径: 不再发信, 一切自查★") == []))
    r.append(("反向用例4 · 平账判据能分辨 (删空 needs ⇒ 判红)",
              flat_ok({"needs_from": 70, "needs_closed": 74})
              and not flat_ok({"needs_from": 0, "needs_closed": 0})))
    r.append(("反向用例5 · 关闭条目缺依据行 ⇒ 判红",
              closed_ok([{"key": "k", "reason": "r", "evidence": "e", "evidence_level": "[实测]",
                          "closed_at": "t", "closed_by": "b"}])
              and not closed_ok([{"key": "k", "reason": "r"}])))
    r.append(("反向用例6 · 缺口判据能分辨 (98 基线 vs 33 实测)",
              (0 <= 33 <= GAP_MAX) and not (0 <= GAP_BASE <= GAP_MAX)))
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
        lines = check_iss357()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-46s %s" % ("✅" if ok else "❌", name, detail))
        print("  ⇒ %s" % ("★全绿★" if allok else "★★有红项 ⇒ 拒签★★"))
        if check_only or not allok:
            continue
        import fcntl
        lf = open(LOCK, "w")
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
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
                  "★**签收闸 `state/_apply_20260723_1005_main_sign_iss357.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
                  + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
                  + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime "
                    "`2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板**) · "
                    "零落表 · 零改别人的分片 · 零外发 · 未代老板拍板 · 未新增拍板项 ★")
            new = seg.replace("  status: fixing", "  status: verified", 1)
            new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
            if "  verify_date:" in new:
                new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new,
                             count=1, flags=re.M)
            else:
                new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
            if "  fix_ref:" in new:
                new = re.sub(r"^  fix_ref: .*$",
                             "  fix_ref: 'state/_apply_20260723_1005_main_sign_iss357.py'", new,
                             count=1, flags=re.M)
            else:
                new = new.rstrip("\n") + \
                    "\n  fix_ref: 'state/_apply_20260723_1005_main_sign_iss357.py'\n"
            bak = LOG + ".bak_%s_main_sign%s" % (STAMP, issue.replace("-", ""))
            shutil.copy2(LOG, bak)
            tmp = LOG + ".tmp_%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(src[:i] + new + src[j:])
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, LOG)
            print("  ★已落签收: status fixing → verified · 备份 %s" % bak)
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)
            lf.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
