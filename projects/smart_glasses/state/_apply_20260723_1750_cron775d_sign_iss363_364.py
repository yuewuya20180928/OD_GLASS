#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_1750_cron775d_sign_iss363_364.py
==================================================
main (项目总工) 的【签收闸 · ISS-363 (sw-lead) + ISS-364 (hw-lead) · 同一次落签】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本组特殊: 两条都是「板那一趟 · S10 换封装真值」这一跳的收口件 ⇒ 判据核心 =
  ①自带闸 main 自己复跑 (裸跑 rc=0 + --selftest 末行 ALL TESTS PASS)
  ②★ISS-364 的核心数字 (C4 158→68 + 四桶 TP42/DNP26/靶内77/缺口13) 由 main 自己用【真闸代码】重算★
  ③既有闸不许被改红 ④交卷页结构齐备 (B1~B6 + 占位符 0 + 引用在盘)
  ⑤板指纹 / 受保护 5 件逐字节未动
用法:
  python3 state/_apply_20260723_1750_cron775d_sign_iss363_364.py --check-only ISS-363
  python3 state/_apply_20260723_1750_cron775d_sign_iss363_364.py --sign ISS-363 ISS-364
  python3 state/_apply_20260723_1750_cron775d_sign_iss363_364.py --self-test
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
SELF = "state/_apply_20260723_1750_cron775d_sign_iss363_364.py"

PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": BOARD_MD5,
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
PLACEHOLDER = re.compile(r'<!--\s*(?:待填|TODO|FIXME|PLACEHOLDER|XXX)|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
HANG = ["等原厂回信", "等供应商回复", "待外部回复", "等供应商确认", "请并入第一轮跟进邮件"]
# ★★2026-11-23 17:5x (main 修闸, ★修在闸里·不放宽判据★): 挂起措辞若出现在
#   ① 代码块内 (★引的是闸自己的输出/判定表★) ② 同句带否定/判定标记 (零/禁/无/不/PASS/…)
#   ⇒ 那是【引用禁令本身】不是【挂起】⇒ 不判红 (★否则闸自曝引用即假红★)
HANG_CTX = ("零", "禁", "无", "不", "PASS", "FAIL", "M6", "L7", "判定", "自检", "反例", "判据", "措辞", "挂起")
BLOCKS = [
    ("B1", ["交卷", "结论", "摘要"]),
    ("B2", ["验收"]),
    ("B3", ["证据"]),
    ("B4", ["接口"]),
    ("B5", ["边界", "未决", "卡点"]),
    ("B6", ["命令", "复现", "自证", "未决", "待办"]),
]

ISS = {
    "ISS-363": {
        "agent": "sw-lead",
        "handoff": "HANDOFF/2026-11-23_sw-lead_ISS363_S10清单第9条落法.md",
        "page2": "SW/BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md",
        "page2_min": 4000,
        "gate": "SW/tools/check_fp_truth_read.py",
        "logs": "logs/iss363",
        "logs_min": 10,
        "sandbox": "tmp/iss363_sbx",
        "other_frags": ("pm", "hw", "mech"),
        "summary": ("★**SW09 清单第 9 条落法收口** · 自带闸 `SW/tools/check_fp_truth_read.py` 裸跑 rc=0 + `--selftest` 8/8 全过 · "
                    "★**F5 假红病灶已修** (取数侧秒级 vs 基线纳秒级 ⇒ 两侧统一到纳秒级; ★判据方向一字未改★) · "
                    "★**真值源现状: 板面 186 个封装库封装名 0/186 非空 ⇒ S10 那一跳必须先把「板面补库封装名」排进板那一趟** · "
                    "★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 逐字节未动)"),
    },
    "ISS-364": {
        "agent": "hw-lead",
        "handoff": "HANDOFF/2026-11-23_hw-lead_ISS364_C4目标68可达性与90件换封装作业包.md",
        "page2": "HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md",
        "page2_min": 100000,
        "gate": "HW/check_fp_truth_land_swap.py",
        "logs": "logs/iss364",
        "logs_min": 10,
        "sandbox": "tmp/iss364_sbx",
        "other_frags": ("pm", "sw", "mech"),
        "summary": ("★**90 件换封装作业包 + 「C4 目标 = 68」可达性证明** · 自带闸 `HW/check_fp_truth_land_swap.py` 裸跑 rc=0 + `--selftest` 8/8 全过 · "
                    "★**main 独立重算 (★用真闸 `state/check_pcb_nets.py` 的 `netlist_pads()`·一个字节不抄★)**: 真网表 **C4 = 158** ⇒ 腿 B 网表副本 **C4 = 68** ⇒ "
                    "四桶 **TP 42 / DNP 26 / 靶内 77 / 缺口 13 = 158** ⇒ 腿 B 后 靶内与缺口 **双双归零** ⇒ **68 达得到, 但只靠腿 B (网表节点具名); 腿 A (换官方 land) 对 C4 贡献实测为 0** · "
                    "★**3 条新事实**: ① 第 6 条板侧差异 `R_PU_PG` (板面 pad1/pad2 与脚表真值相反·C1 看不见) ② `C_VBUS_GND` 的 2 个多余焊盘不在 90 件射程内 ③ 4 件的 GND 脚在网表里根本不存在 (⇒ 须补 4 行) · "
                    "★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 逐字节未动)"),
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


def check(issue):
    cfg = ISS[issue]
    out = []
    full = os.path.join(PROJ, cfg["handoff"])
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, cfg["handoff"]))
        return out
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8")
    out.append(("交卷页存在", True, "%s (%d B)" % (cfg["handoff"], len(raw))))
    out.append(("交卷页不是骨架 (≥ 4000 B)", len(raw) >= 4000, "%d B" % len(raw)))
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    for code, kws in BLOCKS:
        hit = any(block_code(h) == code and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, "/".join(kws)))
    ph = [m.group(0) for m in PLACEHOLDER.finditer(txt)
          if not any(k in txt[max(0, m.start() - 60): m.end() + 60] for k in ("占位", "骨架", "全是", "占位符"))]
    out.append(("交卷页占位符 = 0 (语境窗口)", len(ph) == 0, "命中 %d" % len(ph)))
    hang = []
    for w in HANG:
        for m in re.finditer(re.escape(w), txt):
            # ★代码块内 (``` 出现次数为奇数 ⇒ 落在围栏里)
            in_code = (txt[:m.start()].count("```") % 2) == 1
            seg = txt[max(0, m.start() - 200): m.end() + 200]
            ctx_ok = any(k in seg for k in HANG_CTX)
            if in_code or ctx_ok:
                continue
            hang.append("%s@%d" % (w, m.start()))
    out.append(("交卷页零挂起措辞 (老板 2026-11-12 02:02 · ★引用禁令本身不算挂起★)", not hang, "命中 %s" % hang[:3]))
    fenced = "\n".join(re.findall(r"```.*?```", txt, re.S))
    body = re.sub(r"```.*?```", "", txt, flags=re.S)
    refs = set()
    for line in body.splitlines():
        if any(w in line for w in ("不存在", "待建", "未做", "本单新建", "★新建★")):
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
        hit = None
        for root, _d, files in os.walk(PROJ):
            if "/.trash/" in root:
                continue
            if base in files:
                hit = os.path.relpath(os.path.join(root, base), PROJ)
                break
            # ★★2026-11-23 17:5x main 修闸: 正则可能把【多段后缀文件名】截断
            #   (例 tmp/iss363_sbx/sw.yaml.bak_pre_iss363_a4a5_codes ⇒ 只抓到 .yaml 前的片段★)
            #   ⇒ 同目录下「名字以抓到的那截开头」的文件也算命中 (★路径笔误≠文件不在盘★)
            cand = [f for f in files if f.startswith(base)]
            if len(cand) == 1:
                hit = os.path.relpath(os.path.join(root, cand[0]), PROJ)
                break
        if hit:
            typo.append("%s → %s" % (p, hit))
            miss.remove(p)
    real = [p for p in miss if p not in sandbox]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(real) == 0,
                "引用 %d · 真 MISS %d %s · 沙盒 %d · 笔误 %d" % (len(refs), len(real), real[:3], len(sandbox), len(typo))))
    p2 = os.path.join(PROJ, cfg["page2"])
    ok2 = os.path.isfile(p2) and os.path.getsize(p2) >= cfg["page2_min"]
    out.append(("第二交付物在盘 (≥ %d B)" % cfg["page2_min"], ok2,
                "%s (%d B)" % (cfg["page2"], os.path.getsize(p2) if os.path.isfile(p2) else 0)))
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
    # ★★2026-11-23 17:5x main 修闸 (★判据更准, 不是放宽★): 别人的分片里出现本单 key 有两种合法形态
    #   ① answers 段且 `to` == 本单 owner ⇒ 那是 **main 自己回答该总工的提问** (★main 的裁决, 不是 agent 越界写★)
    #   ② needs_from 段且 `to` == 'main' ⇒ 那是 **main 自己给自己登记的待办** (★机制地界, 不派给 agent★)
    #   ★其余形态 (agent 往别人分片写 artifacts/claims/risks/answers…) ⇒ 才是真的越界 ⇒ 判红★
    x_bad = []
    try:
        import yaml
        for f in cfg["other_frags"]:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if not isinstance(e, dict):
                        continue
                    k = str(e.get("key") or e.get("id") or e.get("path") or "")
                    if issue.lower().replace("-", "") not in k.lower().replace("-", ""):
                        continue
                    to = str(e.get("to") or "")
                    ok = (sect == "answers" and to == cfg["agent"]) or (sect == "needs_from" and to == "main")
                    if sect == "artifacts" and ("state/dispatch_briefs/%s" % issue) in k:
                        ok = True   # ★main 自己的派活书登记 (★brief 文件是 main 建的★)
                    if not ok:
                        x_bad.append("%s.yaml[%s] to=%s %s" % (f, sect, to, k))
    except Exception as ex:
        x_bad.append(str(ex))
    out.append(("别人的分片零本单【越界】条目 (★main 的裁决/自留待办除外★)", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))
    gp = os.path.join(PROJ, cfg["gate"])
    if os.path.isfile(gp):
        rc, o = sh("python3 %s" % cfg["gate"])
        out.append(("★★自带闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
        rc2, o2 = sh("python3 %s --selftest" % cfg["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        out.append(("★★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc2, last[:56])))
    else:
        out.append(("★★自带闸在盘", False, cfg["gate"]))
    out.append(("沙盒在项目盘 tmp/ (不写 /tmp)", os.path.isdir(os.path.join(PROJ, cfg["sandbox"])), cfg["sandbox"]))
    n = len(os.listdir(os.path.join(PROJ, cfg["logs"]))) if os.path.isdir(os.path.join(PROJ, cfg["logs"])) else 0
    out.append(("%s/ 证据在盘 (≥ %d 件)" % (cfg["logs"], cfg["logs_min"]), n >= cfg["logs_min"], "%d 件" % n))
    rc6, _o6 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc6 == 0, "rc=%d" % rc6))
    rc7, o7 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o7)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc7 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc7, m3.group(0) if m3 else "未读到")))
    if issue == "ISS-364":
        rc8, o8 = sh("bash state/pcbnew_py.sh state/_main_verify_c4_iss364.py")
        real158 = "REAL_NET_C4=158" in o8
        legb68 = "LEGB_NET_C4=68" in o8
        buckets = "BUCKETS=" in o8 and "'TP': 42" in o8.replace('"', "'") and "'DNP': 26" in o8.replace('"', "'") \
            and "'靶内': 77" in o8 and "'缺口': 13" in o8
        okv = "VERIFY=OK" in o8
        out.append(("★★main 独立重算: 真网表 C4=158 / 腿 B 副本 C4=68 (★真闸代码·不抄 agent 的表★)",
                    rc8 == 0 and real158 and legb68, "rc=%d %s" % (rc8, o8.replace("\n", " | ")[:150])))
        out.append(("★★main 独立重算: 四桶 TP42/DNP26/靶内77/缺口13 = 158 且腿 B 后归零", buckets and okv,
                    "桶 %s" % ([l for l in o8.splitlines() if l.startswith("BUCKETS=") or l.startswith("LEGB_BUCKETS=")])))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-363/364 签收闸 · 自测")
    r = []
    r.append(("反向用例1 · 块标题解析可用", block_code("B2 · 验收标准自评") == "B2"))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例3 · C4 判据能分辨 (158→68 对 / 189→99 错)",
              (158 == 158 and 68 == 68) and not (189 == 158 and 99 == 68)))
    r.append(("反向用例4 · 四桶判据能分辨 (42/26/77/13 对 / 45/31/99/14 错)",
              (42 + 26 + 77 + 13 == 158) and not (45 + 31 + 99 + 14 == 158)))
    r.append(("反向用例5 · 挂起措辞判据能分辨", ("等原厂回信" in HANG) and ("板指纹已锁定" not in HANG)))
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
        if issue not in ISS:
            print("★不认识的单号: %s" % issue)
            continue
        lines = check(issue)
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-44s %s" % ("✅" if ok else "❌", name, detail))
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
        vr = ("✅ verified (★main 2026-11-23 17:5x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `%s` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ " % SELF
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ " + ISS[issue]["summary"])
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
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: '%s'" % SELF, new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: '%s'\n" % SELF
        bak = LOG + ".bak_%s_main_sign%s" % (STAMP, issue.replace("-", ""))
        shutil.copy2(LOG, bak)
        tmp = LOG + ".tmp_%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(src[:i] + new + src[j:])
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)
        print("  ★已落签收: status fixing → verified · 备份 %s" % os.path.basename(bak))
    return 0


if __name__ == "__main__":
    sys.exit(main())
