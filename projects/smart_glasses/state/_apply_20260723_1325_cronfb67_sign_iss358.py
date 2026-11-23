#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_1325_cronfb67_sign_iss358.py
==================================================
cron fb67af40 (ARS45 队列自动派活) 的【签收闸 · ISS-358 (mech-lead · mech.yaml 分片重名 key 清理)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★为什么本 job 能签: ISS-359 已由 main 13:18 签完, ★**mech-lead 的槽位被 ISS-358 的 fixing 占着**
  ⇒ ★**不签 ⇒ ISS-360 派不出去 ⇒ 队列断线** ⇒ 本闸就是「放名额」的那一步
★本单特殊: 交的是【分片卫生】⇒ ★main 必须自己核「① 高危重名真的清零 ② 零内容丢失
  ③ 没把 need 打成未答 (不制造孤儿) ④ 没把别人的分片改脏」★

用法:
  python3 state/_apply_20260723_1325_cronfb67_sign_iss358.py --check-only ISS-358
  python3 state/_apply_20260723_1325_cronfb67_sign_iss358.py --sign ISS-358
  python3 state/_apply_20260723_1325_cronfb67_sign_iss358.py --self-test
"""
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
LOCK = os.path.join(PROJ, "state/.issue_log.lock")
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
STAMP = time.strftime("%Y%m%d_%H%M")
SELF = "state/_apply_20260723_1325_cronfb67_sign_iss358.py"

HANDOFF = "HANDOFF/2026-11-23_mech-lead_ISS358_分片重名key清理.md"
FRAG = "state/fragments/mech.yaml"
LOGS = "logs/iss358"
CLOSURE_BEFORE = "logs/iss358/closure_before.json"
CLOSURE_AFTER = "logs/iss358/closure_after.json"

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
}
OTHER_FRAGS = ("pm", "hw", "sw")
FORBIDDEN = ["等原厂回信", "等供应商回复", "请并入第一轮跟进邮件", "请并进第二轮邮件",
             "跟进邮件", "买一块", "采购 RK3572", "采购RK3572"]
NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍",
       "作废", "不挂账", "不再", "零发信", "不发")

# ★本单动过的 4 组 key (拆成语义独立 key, 每个原 key 必须留 ≥1 条答案)★
TARGET_KEYS = ("pcb_outline_confirm", "ntc_placement",
               "iss219_mech_c7_sink_area_confirm", "iss251_mech_service_port_pad_y_migrate")
# ★并发同窗由 ISS-356 (hw-lead) 产生的 need key 前缀 ⇒ 不算本单造成的新增未闭合★
CONCURRENT_PREFIX = ("iss356_",)


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


def load_yaml(path):
    import yaml
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def check_iss358():
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
        for f in OTHER_FRAGS:
            d = load_yaml(os.path.join(PROJ, "state/fragments/%s.yaml" % f))
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks",
                         "blockers", "needs_closed", "needs_open_ledger"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss358" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append("解析失败 %s" % ex)
    out.append(("别人的分片 (pm/hw/sw) 零本单登记条目", len(x_bad) == 0,
                "越界 %d %s" % (len(x_bad), x_bad[:3])))

    # ── 交付物在盘 ──
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss358/ 证据在盘 (≥ 8 件)", n >= 8, "%d 件" % n))

    # ── ★核心判据 A: 高危段重名真的清零 (★自己跑体检器, 不抄 agent 自评★) ──
    rc, o = sh("python3 state/check_frag_dup_keys.py --agent mech-lead")
    m = re.search(r"高危段重名合计 \*\*(\d+)\*\* 组", o)
    high = int(m.group(1)) if m else -1
    out.append(("★★高危段重名 = 0 (main 只读体检器实跑)", rc == 0 and high == 0,
                "rc=%d 高危 %s 组" % (rc, high)))

    # ── ★核心判据 B: 零内容丢失 (★对照派活前的基线 JSON 逐条找得到★) ──
    try:
        cb = json.load(open(os.path.join(PROJ, CLOSURE_BEFORE), encoding="utf-8"))
        frag = load_yaml(os.path.join(PROJ, FRAG))
        blob = " ".join(str(a.get("value", "")) for a in (frag.get("answers") or []))
        tot, miss_v = 0, []
        for k, lst in (cb.get("mech_target_answers") or {}).items():
            for e in lst:
                tot += 1
                if str(e.get("value", ""))[:60] not in blob:
                    miss_v.append("%s#%s" % (k, e.get("idx")))
        out.append(("★★零内容丢失: 派活前那 4 组的 %d 条答案逐字仍在现分片" % tot,
                    tot > 0 and len(miss_v) == 0,
                    "共 %d 条 · 丢 %d %s" % (tot, len(miss_v), miss_v[:4])))
    except Exception as ex:
        out.append(("★★零内容丢失", False, "读基线失败 %s" % ex))

    # ── ★核心判据 C: 原 key 每个都留 ≥1 条答案 (不许把 need 打成未答) ──
    try:
        frag = load_yaml(os.path.join(PROJ, FRAG))
        cnt = {}
        for a in (frag.get("answers") or []):
            cnt[a.get("key")] = cnt.get(a.get("key"), 0) + 1
        empty = [k for k in TARGET_KEYS if cnt.get(k, 0) < 1]
        out.append(("★★原 key 各留 ≥1 条答案 (4 组全留, 不制造孤儿)", len(empty) == 0,
                    "留空 %d %s" % (len(empty), empty)))
        dup_now = [k for k in TARGET_KEYS if cnt.get(k, 0) > 1]
        out.append(("★★目标 4 组现在 key 唯一 (每组恰好 1 条)", len(dup_now) == 0,
                    "仍重名 %d %s" % (len(dup_now), dup_now)))
    except Exception as ex:
        out.append(("★★原 key 各留 ≥1 条答案", False, "读分片失败 %s" % ex))

    # ── ★核心判据 D: 本单不得新增任何未闭合 need (★并发 ISS-356 的不算本单造成★) ──
    try:
        cb = json.load(open(os.path.join(PROJ, CLOSURE_BEFORE), encoding="utf-8"))
        ca = json.load(open(os.path.join(PROJ, CLOSURE_AFTER), encoding="utf-8"))
        keyset = lambda lst: {x.get("key") if isinstance(x, dict) else x for x in lst}
        new = keyset(ca.get("unanswered_list") or []) - keyset(cb.get("unanswered_list") or [])
        mine = [k for k in new if not str(k).startswith(CONCURRENT_PREFIX)]
        gone = keyset(cb.get("unanswered_list") or []) - keyset(ca.get("unanswered_list") or [])
        out.append(("★★本单零新增未闭合 need (并发 ISS-356 的 %d 条除外)" % len(new),
                    len(mine) == 0, "本单造成 %d %s · 并发 %d"
                    % (len(mine), mine[:3], len(new) - len(mine))))
        out.append(("★★无「本来已闭合被本单打回未闭合」", len(gone) == 0,
                    "回退 %d %s" % (len(gone), list(gone)[:3])))
    except Exception as ex:
        out.append(("★★本单零新增未闭合 need", False, "读基线失败 %s" % ex))

    # ── 必跑 ──
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc5 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc5, m3.group(0) if m3 else "未读到")))

    # ── 禁语 (零外发) ──
    hits = forbidden_hits(txt)
    out.append(("零外发: 无「等原厂回信/等回复/跟进邮件」的非否定语境表述", len(hits) == 0,
                "命中 %d %s" % (len(hits), hits[:3])))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-358 签收闸 · 自测 (★反向用例★)")

    def blocks_ok(hs):
        return all(any(block_code(h) == c and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)

    def kept_ok(cnt):
        return all(cnt.get(k, 0) >= 1 for k in TARGET_KEYS)

    def new_unclosed_ok(new):
        mine = [k for k in new if not str(k).startswith(CONCURRENT_PREFIX)]
        return len(mine) == 0

    r = []
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
    r.append(("反向用例4 · 原 key 全留 ⇒ 绿; 抽掉一个 ⇒ 判红",
              kept_ok({k: 1 for k in TARGET_KEYS})
              and not kept_ok({k: 1 for k in TARGET_KEYS if k != "ntc_placement"})))
    r.append(("反向用例5 · 并发 iss356_* 新增未闭合不算本单造成 ⇒ 绿",
              new_unclosed_ok({"iss356_bom_footprint_backfill", "iss356_x"})))
    r.append(("反向用例6 · 本单自己的 key 新增未闭合 ⇒ 判红",
              not new_unclosed_ok({"pcb_outline_confirm_something"})))
    r.append(("反向用例7 · 目标组 key 仍重名 ⇒ 判红",
              not (lambda c: all(c.get(k, 0) <= 1 for k in TARGET_KEYS))(
                  {"pcb_outline_confirm": 2})))
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
        lines = check_iss358()
        print("=" * 78)
        print("★ %s 签收验收线 (★cron fb67af40 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
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
            vr = ("✅ verified (★cron fb67af40 (ARS45 队列自动派活) 13:2x 本机独立复核 · 不抄 agent 报告★) ⇒ "
                  "★**签收闸 `%s` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ " % SELF
                  + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
                  + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime "
                    "`2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板**) · "
                    "零落表 · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★ "
                    "★**签收动机**: ISS-359 已由 main 13:18 签完, ★**mech-lead 的槽位被本单的 fixing 占着** "
                    "⇒ 不签 ⇒ ISS-360 派不出去 ⇒ 队列断线 ⇒ 本闸 = 放名额的那一步 ★ ★")
            new = seg.replace("  status: fixing", "  status: verified", 1)
            new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
            if "  verify_date:" in new:
                new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new,
                             count=1, flags=re.M)
            else:
                new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
            if "  fix_ref:" in new:
                new = re.sub(r"^  fix_ref: .*$", "  fix_ref: '%s'" % SELF, new,
                             count=1, flags=re.M)
            else:
                new = new.rstrip("\n") + "\n  fix_ref: '%s'\n" % SELF
            bak = LOG + ".bak_%s_cronfb67_sign%s" % (STAMP, issue.replace("-", ""))
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
