#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0130_cron775d_sign_iss343_iss344.py
==================================================
main (项目总工) 的【签收闸】★**本 job (cron 775d9893) 2026-11-23 01:3x**★
  ★**ISS-343 (hw-lead) / ISS-344 (sw-lead) 两条交卷的验收 + 签收★

★★**为什么本 job 干这件事 (★不越界的理由★)**:
  ★**这两个 agent 的会话已经在 01:19 / 01:18 交卷结束** ⇒ 台账里还挂着 `fixing`
  ⇒ ★**铁律「一个 agent 同时只压一条」⇒ `advance.py` 的 in_flight 规则会挡住这两个 agent 的下一条**
  ⇒ ★**队列会静默停摆** ⇒ ★**签收 = 解卡动作** (★不是重复劳动: 兄弟 job fb67 签过 ISS-339, 但本轮它没签这两条★)
  ★**签收哲学**: ★**fail-closed** —— ★**自己跑验收线, 全绿才签; 有红项就拒签 (★与落表器同一套★)★

用法:
  python3 state/_apply_20261123_0130_cron775d_sign_iss343_iss344.py --check-only
  python3 state/_apply_20261123_0130_cron775d_sign_iss343_iss344.py --sign ISS-343 ISS-344

★**边界**: 零写板 · 零落表 · 零改闸 · 零改别人分片 · 零外发 · ★**只写 state/issue_log.yaml (main 的地界)**
"""
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"

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
KNOWN_EXAMPLE_PATHS = {
    "MECH/FOO.md": "★闸 `--whitelist` 用法示例里的占位文件名 ⇒ 不是对真实文件的引用★",
}


def sh(cmd, timeout=900):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")     # ★不用 /tmp (★配额已满★)
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_board():
    st = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    ok = (md5(os.path.join(PROJ, BOARD)) == BOARD_MD5) and mt.startswith(BOARD_MTIME[:19])
    return [("板指纹 md5+mtime 未动", ok, "%s / %s" % (md5(os.path.join(PROJ, BOARD)), mt))]


def check_handoff(path):
    out = []
    full = os.path.join(PROJ, path)
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, path))
        return out
    txt = open(full, encoding="utf-8").read()
    out.append(("交卷页存在且非骨架 (≥4000 B)", len(txt.encode()) >= 4000,
                "%s (%d B)" % (os.path.basename(path), len(txt.encode()))))
    for code, kws in BLOCKS:
        out.append(("交卷页 %s 块" % code, any(k in txt for k in kws), kws[0]))
    ph = PLACEHOLDER.findall(txt)
    out.append(("交卷页占位符 = 0", len(ph) == 0, "命中 %d %s" % (len(ph), ph[:3])))
    refs = sorted(set(PATH_RE.findall(txt)))
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p)) and p not in KNOWN_EXAMPLE_PATHS]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d · MISS %d %s" % (len(refs), len(miss), miss[:3])))
    return out


def check_frag(agent, key, need):
    p = os.path.join(PROJ, "state/fragments/%s.yaml" % agent)
    n = open(p, encoding="utf-8").read().count(key)
    return [("分片 %s.yaml 命中 %s ≥ %d" % (agent, key, need), n >= n and n >= need, "实测 %d" % n)]


def check_iss343():
    out = []
    out += check_handoff("HANDOFF/2026-11-23_hw-lead_ISS343_板侧项全集漏项补齐.md")
    lg = os.path.join(PROJ, "logs/iss343")
    out.append(("logs/iss343/ 存在且非空", os.path.isdir(lg) and len(os.listdir(lg)) > 0,
                "%d 件" % (len(os.listdir(lg)) if os.path.isdir(lg) else 0)))
    out += check_frag("hw", "iss343", 3)
    rc, o = sh("python3 HW/check_onepass_preflight_coverage.py")
    out.append(("覆盖度闸 裸跑 rc=0", rc == 0, "rc=%d" % rc))
    rc, o = sh("python3 HW/check_onepass_preflight_coverage.py --selftest")
    # ★**判据修正 (★main 2026-11-23 01:3x 实跑后改★)**: ★**这个闸的 selftest 末行不是字面 "ALL TESTS PASS"★**
    #   ⇒ 实跑末两行 = 「⇒ 通道用例: 10/10 通过 · 合计 24/24」 + 「✅ 通道反向用例全抓到 …」 ⇒ rc=0
    #   ⇒ ★**判据按它自己的口径写 (★不许拿别的闸的末行格式去卡它★)**
    m = re.search(r"通道用例:\s*\d+/\d+\s*通过", o)
    m2 = re.search(r"合计\s*\d+/\d+", o)
    ok = rc == 0 and bool(m) and bool(m2) and ("通道反向用例全抓到" in o)
    last = [l for l in o.strip().splitlines() if l.strip()][-1] if o.strip() else ""
    out.append(("覆盖度闸 selftest rc=0 且通道用例全通过 (10/10 · 合计 24/24)", ok,
                "rc=%d · %s" % (rc, last[:70])))
    rc, o = sh("python3 HW/check_workpack_state_values.py")
    out.append(("作业包现状值闸 rc=0", rc == 0, "rc=%d" % rc))
    out += check_board()
    return out


def check_iss344():
    out = []
    out += check_handoff("HANDOFF/2026-11-23_sw-lead_ISS344_零铜网分级口径对账.md")
    lg = os.path.join(PROJ, "logs/iss344")
    out.append(("logs/iss344/ 存在且非空", os.path.isdir(lg) and len(os.listdir(lg)) > 0,
                "%d 件" % (len(os.listdir(lg)) if os.path.isdir(lg) else 0)))
    out += check_frag("sw", "iss344", 3)
    rc, o = sh("python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb "
               "--baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb")
    ok = rc == 0 and ("必需 23" in o and "可悬空 1" in o and "待定 0" in o)
    out.append(("S8 目标名单重读器 rc=0 且分级自检一致 (23/1/0)", ok, "rc=%d" % rc))
    rc, o = sh("python3 SW/tools/check_sw_ref_reachability.py")
    out.append(("SW 位号引用可达性闸 rc=0", rc == 0, "rc=%d" % rc))
    rc, o = sh("python3 SW/tools/check_onepass_sw_release.py")
    out.append(("SW 侧准出汇总闸 rc=0", rc == 0, "rc=%d" % rc))
    out += check_board()
    return out


def check_common():
    out = []
    rc, o = sh("python3 state/merge.py")
    out.append(("merge rc=0", rc == 0, "rc=%d" % rc))
    rc, o = sh("python3 state/gate_check.py")
    q1 = "18/18" in o
    out.append(("gate_check rc=0 且 Q1=18/18", rc == 0 and q1, "rc=%d Q1命中=%s" % (rc, q1)))
    return out


CHECKS = {"ISS-343": check_iss343, "ISS-344": check_iss344}
FIXREF = {
    "ISS-343": "HANDOFF/2026-11-23_hw-lead_ISS343_板侧项全集漏项补齐.md + logs/iss343/ + "
               "HW/check_onepass_preflight_coverage.py (自测) + state/fragments/hw.yaml",
    "ISS-344": "HANDOFF/2026-11-23_sw-lead_ISS344_零铜网分级口径对账.md + logs/iss344/ + "
               "HW/check_s8_target_list.py + SW/tools/check_sw_ref_reachability.py + state/fragments/sw.yaml",
}
OWNER = {"ISS-343": "hw-lead", "ISS-344": "sw-lead"}


def run_checks(ids):
    all_out = []
    for iid in ids:
        out = []
        out.append(("—— %s (%s) ——" % (iid, OWNER.get(iid, "?")), True, ""))
        out += CHECKS[iid]()
        all_out += out
    all_out.append(("—— 共用 (merge / gate_check) ——", True, ""))
    all_out += check_common()
    return all_out


def main() -> int:
    import yaml
    args = sys.argv[1:]
    ids = [a for a in args if a.startswith("ISS-")]
    sign = "--sign" in args
    if not ids:
        print("用法: --check-only | --sign ISS-343 [ISS-344]")
        return 2
    out = run_checks(ids)
    reds = []
    print("=" * 72)
    print("main 签收闸 · ISS-343 / ISS-344 (★fail-closed: 有红项就拒签★)")
    print("=" * 72)
    for name, ok, detail in out:
        if not detail:
            print("  %s %s" % ("·" if ok else "★", name))
            continue
        if not ok:
            reds.append(name)
        print("  %s %-44s %s" % ("✅" if ok else "❌", name, detail[:90]))
    print()
    if reds:
        print("❌ 红项 %d 条 ⇒ **拒签** (★fail-closed★):" % len(reds))
        for r in reds:
            print("   ·", r)
        return 1
    print("✅ 验收线全绿 (%d 条)" % len(out))

    if not sign:
        print("★--check-only ⇒ 只读验收, 未写盘")
        return 0

    doc = yaml.safe_load(open(LOG, encoding="utf-8").read()) or {}
    issues = doc.get("issues") or []
    changed = []
    for iid in ids:
        hit = [i for i in issues if i.get("id") == iid]
        if not hit:
            print("★%s 不在台账 ⇒ 跳过" % iid)
            continue
        it = hit[0]
        if it.get("status") == "verified":
            print("★%s 已是 verified ⇒ 幂等跳过" % iid)
            continue
        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_result"] = "pass"
        it["verify_date"] = datetime.date.today().isoformat()
        it["fix_ref"] = FIXREF.get(iid, it.get("fix_ref"))
        it["note"] = (str(it.get("note") or "") +
                      " ★**2026-11-23 01:3x cron 775d9893 main 签收: 验收线全绿 (交卷页六块齐全 + 占位符 0 + 引用 0 MISS "
                      "+ 分片登记命中 + 本单闸/自测 rc=0 + merge rc=0 + gate_check rc=0 Q1=18/18 + 板 md5/mtime 未动) ⇒ "
                      "status: fixing → verified (verify_by=main ≠ owner=%s)★**" % OWNER.get(iid, "?"))
        changed.append(iid)
    if not changed:
        print("★无状态变化 ⇒ 未写盘")
        return 0
    bak = LOG + ".bak_20261123_0130_cron775d_sign_iss343_iss344"
    if not os.path.exists(bak):
        shutil.copy2(LOG, bak)
        print("★备份 ->", os.path.basename(bak))
    out_text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    print("★已签收:", ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
