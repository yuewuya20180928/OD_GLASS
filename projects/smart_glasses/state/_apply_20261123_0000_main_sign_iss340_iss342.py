#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0000_main_sign_iss340_iss342.py
==================================================
main (项目总工) 的【签收闸】: 自己跑验收线, 全绿才签, 有红项就拒签 (★fail-closed·★与落表器同一套哲学★)

用法:
  python3 state/_apply_20261123_0000_main_sign_iss340_iss342.py --check-only     # 只跑验收线, 不写盘
  python3 state/_apply_20261123_0000_main_sign_iss340_iss342.py --sign ISS-340 [ISS-342]

零写板 · 零落表 · 零改闸 · 零改真生成器 · 零外发 · 只写 state/issue_log.yaml (main 的地界)
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

BLOCKS = [
    ("B1", ["结论摘要", "结论 (给", "一句话"]),
    ("B2", ["验收标准自评", "自评", "验收标准"]),
    ("B3", ["证据分级", "证据等级", "证据"]),
    ("B4", ["接口取值", "接口声明", "interface_claims", "接口请求"]),
    ("B5", ["阻塞", "卡点", "未决", "待办"]),
    ("B6", ["复现", "复现命令", "自证"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config)/[0-9A-Za-z_./-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
# ★★已知「不是文件引用」的写法 (★闸的 --whitelist 用法示例里的占位文件名·★逐条记明理由★)★★
KNOWN_EXAMPLE_PATHS = {
    "MECH/FOO.md": "★闸 `--whitelist` 用法示例里的占位文件名 (★例: --whitelist MECH/FOO.md:10-20★) ⇒ 不是对真实文件的引用★",
}


def sh(cmd, timeout=900):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_board():
    out = []
    st = os.stat(os.path.join(PROJ, BOARD))
    import datetime
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    ok = (md5(os.path.join(PROJ, BOARD)) == BOARD_MD5) and mt.startswith(BOARD_MTIME[:19])
    out.append(("板指纹 md5+mtime 未动", ok, "%s / %s" % (md5(os.path.join(PROJ, BOARD)), mt)))
    return out


def check_handoff(path):
    out = []
    full = os.path.join(PROJ, path)
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, path))
        return out, ""
    txt = open(full, encoding="utf-8").read()
    out.append(("交卷页存在", True, "%s (%d B)" % (path, len(txt.encode()))))
    out.append(("交卷页不是骨架 (≥ 4000 B)", len(txt.encode()) >= 4000, "%d B" % len(txt.encode())))
    for code, kws in BLOCKS:
        hit = any(k in txt for k in kws)
        out.append(("交卷页 %s 块" % code, hit, kws[0]))
    ph = PLACEHOLDER.findall(txt)
    out.append(("交卷页占位符 = 0", len(ph) == 0, "命中 %d" % len(ph)))
    refs = sorted(set(PATH_RE.findall(txt)))
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p)) and p not in KNOWN_EXAMPLE_PATHS]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d 个 · 已知示例 %d 个 · MISS %d %s"
                % (len(refs), len([p for p in refs if p in KNOWN_EXAMPLE_PATHS]), len(miss), miss[:3])))
    return out, txt


def check_frag(agent, key, need):
    p = os.path.join(PROJ, "state/fragments/%s.yaml" % agent)
    n = open(p, encoding="utf-8").read().count(key)
    return [("分片命中 %s ≥ %d" % (key, need), n >= need, "实测 %d" % n)]


def check_iss340():
    out = []
    h, txt = check_handoff("HANDOFF/2026-11-22_hw-lead_ISS340_板网表C1差异归属判定.md")
    out += h
    lp = os.path.join(PROJ, "logs/iss340/07_cont2_required_checks.log")
    out.append(("logs/iss340/07 必跑日志存在", os.path.isfile(lp),
                "%d B" % (os.path.getsize(lp) if os.path.isfile(lp) else 0)))
    out += check_frag("hw", "iss340", 10)
    rc, o = sh("python3 HW/check_board_netlist_divergence_gate.py --selftest")
    last = [l for l in o.strip().splitlines() if l.strip()][-1] if o.strip() else ""
    out.append(("判别闸 selftest 末行 ALL TESTS PASS", rc == 0 and "ALL TESTS PASS" in last, last[:80]))
    rc, o = sh("python3 HW/check_board_netlist_divergence_gate.py")
    ok = rc == 0 and "A=0 / B=3 / C=2" in o and "无未解释差异" in o
    out.append(("判别闸实跑 = A0/B3/C2 且无未解释", ok, "rc=%d" % rc))
    out += check_board()
    return out


def check_iss342():
    out = []
    h, txt = check_handoff("HANDOFF/2026-11-22_mech-lead_ISS342_结构侧权威表口径漂移.md")
    out += h
    out += check_frag("mech", "iss342", 5)
    # 老字一字未删: 与追加前的原文件逐字对照 (只许有插入)
    orig = "/tmp/iss342_geom_orig.md"
    cur = os.path.join(PROJ, "MECH/BOARD_GEOM_30MM.md")
    if os.path.isfile(orig):
        o_raw = open(orig, "rb").read()
        c_raw = open(cur, "rb").read()
        o_lines = o_raw.split(b"\n")
        body = b"\n".join(o_lines[1:])
        bm = hashlib.md5(body).hexdigest()
        out.append(("BOARD_GEOM_30MM.md 老正文 md5 未变", bm == "0cbdbeabbc96290d16fae4920da3a192", bm))
        out.append(("BOARD_GEOM_30MM.md 只有插入零删除", c_raw.startswith(o_lines[0] + b"\n") and body in c_raw,
                    "老 %d B → 现 %d B" % (len(o_raw), len(c_raw))))
    else:
        out.append(("原文件 /tmp/iss342_geom_orig.md 还在 (老字对照)", False, "缺失"))
    out += check_board()
    return out


CHECKS = {"ISS-340": check_iss340, "ISS-342": check_iss342}


def main():
    args = sys.argv[1:]
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = CHECKS[issue]()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑·fail-closed★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-38s %s" % ("✅" if ok else "❌", name, detail))
        print("  ⇒ %s" % ("★全绿★" if allok else "★★有红项 ⇒ 拒签★★"))
        if check_only or not allok:
            continue
        # ── 落签收 (原子写 + 备份) ──
        src = open(LOG, encoding="utf-8").read()
        i = src.find("\n- id: %s" % issue)
        j = src.find("\n- id: ", i + 10)
        if i < 0:
            print("  ★段没定位到 ⇒ 不落盘")
            continue
        if j < 0:
            j = len(src)   # ★该条是列表最后一条 ⇒ 段尾 = 文件末 (★2026-11-23 00:1x 实测踩到过★)
        seg = src[i:j]
        if "  status: fixing" not in seg:
            print("  ★status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 不落盘")
            continue
        vr = "✅ verified (★main 2026-11-22 23:5x~2026-11-23 00:0x 本机独立复核·不抄 agent 报告★) ⇒ " \
             "★**签收闸 `state/_apply_20261123_0000_main_sign_iss340_iss342.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ " \
             + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines) \
             + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改闸 · 零改真生成器 · 零外发 · 未替老板拍板 · 零写别人的分片 ★ " \
             "★ **★本单的前一轮子会话于 23:37:52 被【父 run 结束 ⇒ 子会话连带 abort】掐死 (★零产出·白跑 7 分钟★) ⇒ 本单由 main 在 boss 会话里重派 (★父会话用 sessions_yield 等 ⇒ 没再被 abort·★且 brief 加了「先落盘, 后填内容」★) ★** ★"
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        new = new.replace("  verify_date: null", "  verify_date: '2026-11-23'", 1)
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
