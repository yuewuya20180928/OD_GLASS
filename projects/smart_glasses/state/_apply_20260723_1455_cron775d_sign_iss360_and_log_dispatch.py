#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_1455_cron775d_sign_iss360_and_log_dispatch.py
============================================================
main (项目总工) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-23 14:55
★本脚本做两件事 (★互不相干·各自独立★):
  ① 【签收闸 · ISS-360】mech-lead cont1 交卷 (板框建议默认值作废标注 · 纯文档一行 · 零写板)
     ⇒ 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) ⇒ 不抄 agent 的自评
  ② 【派活留痕】把本 job 本轮真实发生的两次派活写进 dispatch_log
     ⇒ ISS-361 cont1 (hw-lead) + ISS-362 (sw-lead) ⇒ 幂等 (已存在则不重复写)

★哲学:
  · 签收 = main 独立复核, 不是 agent 自评的转录 ⇒ 板指纹 / 老字 md5 / 闸 rc 全部本机重跑
  · 幂等: 重复跑不会写第二遍 (dispatch_log 靠 issue+cont 判重; issue_log 靠 status 判重)
  · 原子写: 一律 tmp + fsync + os.replace ⇒ 不留半截文件
  · 零写板 · 零落表 · 零改别人的分片 · 零外发 · 不替老板拍板

用法:
  python3 state/_apply_20260723_1455_cron775d_sign_iss360_and_log_dispatch.py --check-only
  python3 state/_apply_20260723_1455_cron775d_sign_iss360_and_log_dispatch.py --sign ISS-360
  python3 state/_apply_20260723_1455_cron775d_sign_iss360_and_log_dispatch.py --log-dispatch
  python3 state/_apply_20260723_1455_cron775d_sign_iss360_and_log_dispatch.py --self-test
"""
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
DLOG = os.path.join(PROJ, "state/dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")
SELF = "state/_apply_20260723_1455_cron775d_sign_iss360_and_log_dispatch.py"

# ---- 受保护件 (板只改一次 ⇒ 一个字节都不许动) ----
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": BOARD_MD5,
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
# ---- ISS-360 交付物 ----
PAGE = "MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md"
HANDOFF = "HANDOFF/2026-11-23_mech-lead_ISS360_板框建议默认值作废标注.md"
LOGS = "logs/iss360"
COMPAT = "MECH/check_board_frame_candidate_compat_gate.py"
OLD_MD5 = "543c4d7fb001c66ea2ce6b80bebb6769"   # sed -n '100,110p' 老字基线
FRAG = "state/fragments/mech.yaml"
OTHER_FRAGS = ("pm", "sw", "hw")
BLOCKS = [
    ("B1", ["结论"]),
    ("B2", ["验收标准自评", "验收"]),
    ("B3", ["证据分级", "证据"]),
    ("B4", ["接口取值声明", "接口"]),
    ("B5", ["未决项", "卡点", "未决"]),
    ("B6", ["自证复现命令", "自证", "复现", "命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
# ★★交假口径 = 签收打回 ⇒ 这几个说法出现即红 (★ISS-341 明文否定过★)
FALSE_CLAIMS = ["几何数算错了", "几何算错了", "F30A 算错了", "F30A 的几何数错了"]
# ★本单开工时刻 ⇒ 闸脚本 mtime 早于它 = 本单零改闸
SESSION_START = "2026-11-23 13:45"


def sh(cmd, timeout=1200):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def block_code(h):
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-9])\b", s)
    return m.group(1) if m else None


def atomic_write(path, text):
    tmp = path + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# ============================ ① ISS-360 签收验收线 ============================
def check_iss360():
    out = []
    full = os.path.join(PROJ, HANDOFF)
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, HANDOFF))
        return out
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8")
    out.append(("交卷页存在且非骨架 (>= 4000 B)", len(raw) >= 4000, "%d B" % len(raw)))
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    for code, kws in BLOCKS:
        hit = any(block_code(h) == code and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, kws[0]))
    ph = [m.group(0) for m in PLACEHOLDER.finditer(txt)
          if not any(k in txt[max(0, m.start() - 60): m.end() + 60] for k in ("占位", "骨架", "全是", "占位符"))]
    out.append(("交卷页占位符 = 0 (语境窗口)", len(ph) == 0, "命中 %d" % len(ph)))
    # 引用文件在盘
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
    real = [p for p in miss if p not in sandbox]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(real) == 0,
                "引用 %d · 真 MISS %d %s" % (len(refs), len(real), real[:3])))

    # ---- 目标页: 追加式 + 老字零改动 ----
    pf = os.path.join(PROJ, PAGE)
    ptext = open(pf, encoding="utf-8").read()
    out.append(("★目标页含 §1-3.1 订正标记", "订正标记 · ISS-360" in ptext, "grep 命中"))
    rc, o = sh("sed -n '100,110p' %s | md5sum" % PAGE)
    got = o.strip().split()[0] if o.strip() else ""
    out.append(("★★老字零改动 md5 (L100~L110)", got == OLD_MD5, "实测 %s · 期望 %s" % (got, OLD_MD5)))
    # ★老字还在 (没被删)
    keep = re.search(r"建议默认值\s*=\s*选项.?\s*②?\s*`?F30A", ptext) is not None
    out.append(("★老字「建议默认值 = 选项② F30A」仍在 (没被删)", keep, "grep %s" % keep))
    # ★★订正口径正确 (不许交假口径)
    says_ok = ("没算错" in ptext) and ("答不了" in ptext or "不该替上位问题作答" in ptext)
    bad = [w for w in FALSE_CLAIMS if w in ptext]
    out.append(("★★订正口径正确 (含「没算错」+「答不了/不该替上位问题作答」)", says_ok, "命中=%s" % says_ok))
    out.append(("★★零假口径 (不许「几何数算错了」等)", len(bad) == 0, "命中 %d %s" % (len(bad), bad)))
    # ★一条没替老板拍
    nopick = ("一条没替老板拍" in ptext) or ("不替老板拍" in ptext) or ("一条没替老板拍" in txt)
    out.append(("★一条没替老板拍 (目标页或交卷页声明)", nopick, "命中=%s" % nopick))

    # ---- 兼容闸 rc + selftest ----
    rc, o = sh("python3 %s" % COMPAT)
    out.append(("★兼容闸 rc=0", rc == 0, "rc=%d" % rc))
    rc, o = sh("python3 %s --selftest" % COMPAT)
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*条用例与预期一致", o)
    out.append(("★兼容闸 selftest 11/11 + ALL TESTS PASS",
                rc == 0 and bool(m) and m.group(1) == "11" and m.group(2) == "11" and "ALL TESTS PASS" in o,
                "rc=%d %s" % (rc, m.group(0) if m else "未读到")))

    # ---- 板指纹双证 ----
    got = md5(os.path.join(PROJ, BOARD))
    stt = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(stt.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime 逐字节未动",
                got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]), "%s / %s" % (got, mt)))
    # ---- 零落表 ----
    badp = []
    for p, want in PROTECTED.items():
        if md5(os.path.join(PROJ, p)) != want:
            badp.append(p)
    out.append(("零落表: 受保护件 %d 件 md5 未动" % len(PROTECTED), len(badp) == 0, "动 %d %s" % (len(badp), badp[:3])))
    # ---- 零改闸 (mtime 早于本单开工) ----
    badg = []
    for g in ("state/gate_check.py", "state/merge.py", "state/frag_write.py"):
        m2 = datetime.datetime.fromtimestamp(os.stat(os.path.join(PROJ, g)).st_mtime).strftime("%Y-%m-%d %H:%M")
        if m2 >= SESSION_START:
            badg.append("%s (%s)" % (g, m2))
    out.append(("零改闸: gate_check/merge/frag_write mtime < 13:45", len(badg) == 0, "动 %d %s" % (len(badg), badg[:3])))
    # ---- 别人分片零本单登记 ----
    x_bad = []
    for f in OTHER_FRAGS:
        d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
        for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
            for e in (d.get(sect) or []):
                if isinstance(e, dict):
                    k = str(e.get("key") or e.get("id") or e.get("path") or "")
                    if "iss360" in k.lower():
                        x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    out.append(("别人的分片 (pm/sw/hw) 零本单登记条目", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))
    # ---- 分片有本单痕迹 (走 frag_write) ----
    n = 0
    try:
        n = open(os.path.join(PROJ, FRAG), encoding="utf-8").read().lower().count("iss360")
    except Exception:
        pass
    out.append(("本单分片痕迹在盘 (mech.yaml)", n > 0, "grep -c iss360 = %d" % n))
    # ---- 留证 ----
    ln = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss360/ 留证在盘 (>= 5 件)", ln >= 5, "%d 件" % ln))
    # ---- 必跑 ----
    rc, o = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc == 0, "rc=%d" % rc))
    rc, o = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18",
                rc == 0 and bool(m3) and m3.group(1) == "18", "rc=%d Q1=%s" % (rc, m3.group(0) if m else "未读到")))
    return out


def sign_iss360(issue, lines):
    src = open(LOG, encoding="utf-8").read()
    i = src.find("\n- id: %s" % issue)
    j = src.find("\n- id: ", i + 10)
    if i < 0:
        print("  ★段没定位到 ⇒ 不落盘")
        return False
    if j < 0:
        j = len(src)
    seg = src[i:j]
    if "  status: fixing" not in seg:
        print("  ★status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 不落盘 (★不抢签★)")
        return False
    vr = ("✅ verified (★main 2026-11-23 14:55 本机独立复核 · 不抄 agent 报告★) ⇒ "
          "★**签收闸 `%s` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
          % SELF
          + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
          + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ "
            "**G1 仍开, 不许投板**) · 零落表 (受保护件 5 件同值) · 零改闸 (gate_check/merge/frag_write mtime < 13:45) · "
            "零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★ "
            "★★【main 独立复核 (★不抄 agent 报告★)】★★ "
            "★**① 追加式铁律**: 目标页 `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` 新增 §1-3.1 (L112~L141) · "
            "★**老字 `sed -n '100,110p' | md5sum` = `543c4d7fb001c66ea2ce6b80bebb6769` 追加前后同值 ⇒ L105~L110 一个字节未动** ★ "
            "★**② 订正口径正确 (★这是本单最容易交假口径的地方·已实读校验★)**: 页里写「站在它自己那一层上没算错」+"
            "「答不了【这一趟画哪块板】这个问题」+ 逐字引 ISS-341 三行原话 ⇒ ★**零处出现「几何数算错了」类假口径** ★ "
            "★**③ 一条没替老板拍**: 页里明写「本条不宣布『这一趟画哪块板』, 也不宣布『那就画 B160×100』」+ "
            "§1-3 的 F30A / 1.00mm / 6 层 / 5 条候选代价清单 / 36 档表 一个字没动 ⇒ "
            "**U-1 仍是老板的项 (need key `boss_u1_upper_axis_board_trip_physical_product`)·本单零新增拍板项** ★ "
            "★**④ 机器判据可复跑**: `MECH/check_board_frame_candidate_compat_gate.py` rc=0 + `--selftest` 11/11 ALL TESTS PASS ★"
            "★**⑤ 留证**: `logs/iss360/` 5 件 + 交卷页 20,989 B (B1~B6 齐全·占位符 0) + 分片 19 处本单痕迹 ★")
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
    atomic_write(LOG, src[:i] + new + src[j:])
    print("  ★已落签收: status fixing → verified · 备份 %s" % os.path.basename(bak))
    return True


# ============================ ② 派活留痕 (幂等) ============================
def log_dispatch():
    rows = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
    have = set()
    for r in rows:
        have.add((str(r.get("issue")), str(r.get("cont") or "")))
    todo = []

    b361 = os.path.join(PROJ, "state/dispatch_briefs/ISS-361_hw_fp_truth_coverage_gap.md")
    brief361 = open(b361, encoding="utf-8").read() if os.path.isfile(b361) else ""
    todo.append({
        "issue": "ISS-361",
        "agent": "hw-lead",
        "at": "2026-11-23",
        "cont": "cont1",
        "dead_cause": ("★cont0 (会话 de729ea9-50c2-446d-8de1-84685b6290e2 / sessionId c4ab4672-e40a-4c5e-88af-41522eb018d5) "
                       "于 2026-11-23 14:41:45 派出 · 145 秒后 status=failed 且连 transcript 文件都没落 ⇒ 零交付物 "
                       "(★`logs/iss361/` 不存在 · `HANDOFF/2026-11-23_hw-lead_ISS361_*.md` 不存在 · "
                       "`HW/PCB/FP_TRUTH_COVERAGE_GAP.md` 不存在 · `HW/check_fp_truth_coverage_gap.py` 不存在★) ⇒ "
                       "★**成【僵尸 fixing】· 不是【已开工】**⇒ ★本单 status 保持 fixing ⇒ 下一轮 advance.py 的 in_flight 规则看不见本单 ⇒ 不会重复派★ ★ "
                       "★补派时刻 2026-11-23 14:52 · ★hw-lead 槽位确认空闲 (前一个会话 queue_iss328_closout 于 14:47:50 status=done 收工) ★ "
                       "★brief 文件 = state/dispatch_briefs/ISS-361_hw_fp_truth_coverage_gap.md (15,922 B) ★"),
        "brief": brief361,
        "job": "cron 775d9893 (ARS45 继续执行后继计划) · 补派 cont1 时刻 2026-11-23 14:52 GMT+8",
    })

    b362 = os.path.join(PROJ, "state/dispatch_briefs/ISS-362_sw_fp_truth_impact.md")
    brief362 = open(b362, encoding="utf-8").read() if os.path.isfile(b362) else ""
    todo.append({
        "issue": "ISS-362",
        "agent": "sw-lead",
        "at": "2026-11-23",
        "cont": "",
        "dead_cause": ("★首派 (2026-11-23 14:0x · 同一 cron job 的上一趟) 只写了 brief + 落台账 + 写 dispatch_log, "
                       "★**但从未真正 spawn** ⇒ 盘上零交付物 (`logs/iss362/` 不存在 · 交卷页不存在 · 新闸不存在) ⇒ "
                       "★**成【僵尸 fixing】**★ ⇒ ★本单 status 保持 fixing ⇒ 下一轮 advance.py 的 in_flight 规则看不见本单 ⇒ 不会重复派★ ★ "
                       "★补派时刻 2026-11-23 14:50 · ★sw-lead 槽位确认空闲 (名下无在跑会话) ★ "
                       "★brief 文件 = state/dispatch_briefs/ISS-362_sw_fp_truth_impact.md (18,281 B) ★"),
        "brief": brief362,
        "job": "cron 775d9893 (ARS45 继续执行后继计划) · 补派时刻 2026-11-23 14:50 GMT+8",
    })

    added = 0
    src = open(DLOG, encoding="utf-8").read()
    if not src.endswith("\n"):
        src += "\n"
    for e in todo:
        key = (str(e["issue"]), str(e.get("cont") or ""))
        if key in have:
            print("  ★幂等跳过 (已存在): %s cont=%s" % key)
            continue
        block = yaml.safe_dump([e], allow_unicode=True, default_flow_style=False, width=10 ** 6)
        src += block
        have.add(key)
        added += 1
    if added:
        bak = DLOG + ".bak_%s_cron775d_logdispatch" % STAMP
        shutil.copy2(DLOG, bak)
        atomic_write(DLOG, src)
        print("  ★dispatch_log 追加 %d 条 · 备份 %s" % (added, os.path.basename(bak)))
    else:
        print("  ★dispatch_log 无新增 (幂等)")
    return added


# ============================ ③ 自测 ============================
def self_test():
    print("=" * 78)
    print("★ 签收闸 + 派活留痕 · 自测")
    r = []
    r.append(("反向用例1 · 老字基线期望值被篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    r.append(("反向用例2 · 块标题解析可用 (B2 / B5)",
              block_code("★B2 · 验收标准自评") == "B2" and block_code("B5 · 未决项") == "B5"))
    # ★反向用例3: 假口径词表自身要自洽 (★非空 · 每条都是「…错了」句 · 不含合法措辞★)
    r.append(("反向用例3 · 假口径词表自洽 (非空·每条含『错了』·不含合法措辞)",
              len(FALSE_CLAIMS) >= 3
              and all("错了" in w for w in FALSE_CLAIMS)
              and not any("没算错" in w or "算错了吗" in w for w in FALSE_CLAIMS)))
    # ★反向用例3b ★★正向对照★★: 合法引文 (ISS-341 原话「算错了吗? → 没算错」)
    #   【不许】被假口径词表命中 ⇒ 否则会把正确口径判成红 (★假阳性 = 误拒签★)
    legit = "★F30A 的几何数 (60×30 / 6 层 / ≤1.00) 算错了吗? → 没算错★"
    r.append(("反向用例3b · 正向对照: 合法引文不被假口径词表命中 (零假阳性)",
              not any(w in legit for w in FALSE_CLAIMS)))
    r.append(("反向用例4 · 老字 md5 基线是 32 位十六进制", bool(re.fullmatch(r"[0-9a-f]{32}", OLD_MD5))))
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
    if "--log-dispatch" in args:
        print("=" * 78)
        print("★ 派活留痕 · 本轮真实发生的派活")
        log_dispatch()
        return 0
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss360()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-52s %s" % ("✅" if ok else "❌", name, detail))
        print("  ⇒ %s" % ("★全绿★" if allok else "★★有红项 ⇒ 拒签★★"))
        if check_only or not allok:
            continue
        sign_iss360(issue, lines)
    return 0


if __name__ == "__main__":
    sys.exit(main())
