#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_20260723_0535_main_u1_layered_recommendation.py
======================================================
main (项目总工) 的【一次性订正 · pm.yaml · ISS-310 (U-1 板框) 建议默认值分层化】
★为什么做这件事 (★修在产生点·不许在产物上擦★):
  ISS-341 (★已由 main 签收·机器判决★) 的相容性矩阵证明:
    · `B160x100` 与现役板同框同层同厚 ⇒ 这一趟 = 改现役板一次 (S1~S13 的 20 个 PCB_PART_POS 继续有效)
    · `F30A` / `P60x15` ⇒ 这一趟 = 重画一块新板 (186 封装 / 45 条未连接 / 作业包 S1~S13 全部作废)
  ⇒ pm.yaml 里 ISS-310 的「建议默认值 = 60×30 (F30A) 且板厚 ≤ 1.00」站不住 (★推理跳了一格:
    「台架板装不进眼镜」≠「这一趟画不了」⇒ 拿结构外形判据去否掉台架板档★)
  ⇒ 而【上位问题】(这一趟画哪块物理产品) 已在 `needs_from[boss_u1_upper_axis_board_trip_physical_product]`
    里登记 ⇒ ★**U-1 的建议默认值必须分层 (先上位、后下位)** ★
  ⇒ DECISION_ONE_PAGER_2026-11-22.md §⑥-3 已授权: 「若矩阵证明站不住 ⇒ 由 main 自己改 pm.yaml 里
    ISS-310 的落表 value —— 这一改只由 main 做」

纪律:
  · 只写 main 自己的分片 `state/fragments/pm.yaml` (★用 state/frag_write.py 原子写★)
  · 改前备份; 改后逐条对拍 (其余 82 条 answers 一条不动) + 受保护件 md5 未动 + merge/gate_check 复跑
  · ★**一条没替老板拍板**: 改的只是【建议默认值】的措辞与层级, 不新增拍板项, 不落任何决定★
用法:
  python3 state/_fix_20260723_0535_main_u1_layered_recommendation.py --check-only
  python3 state/_fix_20260723_0535_main_u1_layered_recommendation.py --apply
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PM = os.path.join(PROJ, "state/fragments/pm.yaml")
KEY = "iss310_main_board_frame_u1_decision"
STALE = "60×30 (F30A) 且板厚 ≤ 1.00"
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/fragments/hw.yaml": None,
    "state/fragments/sw.yaml": None,
    "state/fragments/mech.yaml": None,
}

NEW_VALUE = (
    "★★【main 2026-11-23 05:3x 本机独立复核 · 依 ISS-341 机器判决把本条【分层化】·★建议·不是已决定★】★★ "
    "★**上位问题 (need key `boss_u1_upper_axis_board_trip_physical_product`)**: 这一趟画的是【甲 = demo 台架板 "
    "(160×100 / RK3572-SOM 承载区 / 盘上唯一)】还是【乙 = 产品内板 (60×30 或 60×15 / RK3576 直上板 / 盘上没有)】?★ "
    "★**下位 (U-1 本题) = 条件式 ⇒ 只有第一问答「乙」时才需要答**: "
    "① 若甲 ⇒ U-1 随之落 `B160×100` / 8 层 / 板厚 1.60 / 沿用现役 20 个 `PCB_PART_POS` 与现役孔位 "
    "(★结构外形判据 [腔体/开口/板重] 对台架板本趟不适用★) ② 若乙 ⇒ `F30A` (60×30 / 6 层 / 1.00 / 套 A) 或 `P60×15` "
    "(60×15 / 6 层 / 1.00 / 套 A) ⇒ ★**但那一趟 = 新板第一版** (现役板 186 封装 / 45 条未连接 / 作业包 S1~S13 全部作废) "
    "⇒ 须先拍 ISS-206 (SoM 载板形态) 与主控口径 (RK3572-SOM 直插 vs RK3576-SoC 直上)★ "
    "★**main 的建议默认值 (建议·非已决定·老板可驳回)**: 先拍上位 = 甲 (demo 台架板) ⇒ U-1 = `B160×100` / 8 层 / 1.60 / 沿用现役孔位★ "
    "★**机器判决依据 [实测] (ISS-341 · main 已独立复跑 `MECH/check_board_frame_candidate_compat_gate.py` rc=0 + `--selftest` 11/11)**: "
    "`B160x100` 相容 (占位余量 X8.00 / Y22.25 · 无外溢) ⇒ **改现役板一次**; "
    "`F30A` 占位并集外溢 X+97.60 / Y+50.05 · 承载区包络高差 **−16.78** ⇒ **重画一块新板**; "
    "`P60x15` 外溢 X+97.60 / Y+65.05 · 高差 **−31.78** ⇒ **重画一块新板** "
    "(★另: SoM 承载区 53.60×46.08 mm 物理上进不去 60×30 / 60×15★)★ "
    "★**★旧建议 (60×30 / F30A + 板厚 ≤ 1.00, 理由 = 36 档里唯一在【结构外形判据】上全绿) 已作废 (保留作历史留档·结论不再引用)★**: "
    "★那一步推理【跳了一格】—— 36 档判的是「台架板装不进眼镜」, 而台架板本来就是台架板 (ISS-169: 不装电池 · Type-C 供电 · 板上只有这一块) "
    "⇒ 「装不进眼镜」≠「这一趟画不了」⇒ 该建议不能当这一趟的建议默认值★ "
    "★**一条没替老板拍板** · 老板要答的件数不变 (仍是 9 件: §① 8 项 + 上位问题 1 项) · 拍板顺序建议 = 上位 → 框 → 板厚 → 层数 → 其余★★ "
    "★**权威页**: `DECISION_ONE_PAGER_2026-11-22.md` §⑥/§⑦/§⑩ · `MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md` · "
    "`DECISION_INDEX_2026-11-18.md` §E-1/§E-3 (★2026-11-23 05:3x 追加式订正见索引末尾 §E-1a★)★"
)
NEW_REF = (
    "DECISION_ONE_PAGER_2026-11-22.md §⑥-1/§§⑥-2/§⑦-1/§⑦-2/§⑦-3 (★追加式·老字一字未改★) + "
    "MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md (ISS-341 机器判决) + "
    "DECISION_INDEX_2026-11-18.md §E-1/§E-3 + §E-1a (2026-11-23 05:3x 追加式订正)"
)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def load_answers():
    import yaml
    d = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    return d, (d.get("answers") or [])


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    d, answers = load_answers()
    hits = [e for e in answers if isinstance(e, dict) and e.get("key") == KEY]
    print("=" * 78)
    print("★ ISS-310 (U-1) 建议默认值分层化 · main 地界的一次性订正")
    ok = True
    if len(hits) != 1:
        print("  ❌ pm.yaml 里 key=%s 的条目数 = %d (应为 1) ⇒ 拒改" % (KEY, len(hits)))
        return 1
    old_val = str(hits[0].get("value") or "")
    stale_present = STALE in old_val
    print("  %s 旧建议默认值仍写着 (将被替换): %r" % ("✅" if stale_present else "⚠️", STALE))
    if not stale_present:
        print("  ★旧建议已不在 (已被别的 job 改过) ⇒ 不重复改 (幂等)")
        return 0
    new_answers = []
    changed = 0
    for e in answers:
        if isinstance(e, dict) and e.get("key") == KEY:
            e2 = dict(e)
            e2["value"] = NEW_VALUE
            e2["ref"] = NEW_REF
            new_answers.append(e2)
            changed += 1
        else:
            new_answers.append(e)
    # ★改前对拍基线: 其余条目的 (key,value,to,ref) 指纹 ★
    def fingerprint(lst):
        h = hashlib.md5()
        for e in lst:
            if isinstance(e, dict) and e.get("key") != KEY:
                h.update(repr((e.get("key"), e.get("to"), e.get("value"), e.get("ref"))).encode())
        return h.hexdigest()
    fp_before = fingerprint(answers)
    if not apply:
        print("  ⇒ --check-only: 不落盘 (将改 %d 条, 其余 %d 条指纹 %s)"
              % (changed, len(answers) - changed, fp_before[:12]))
        return 0
    # ★先落 JSON, 再用 frag_write 原子写 (★只用 sanctioned writer★) ★
    tmpj = os.path.join(PROJ, "tmp/_pm_answers_u1_%s.json" % time.strftime("%Y%m%d_%H%M"))
    with open(tmpj, "w", encoding="utf-8") as f:
        json.dump(new_answers, f, ensure_ascii=False, indent=1)
    bak = PM + ".bak_%s_main_u1_layered" % time.strftime("%Y%m%d_%H%M")
    shutil.copy2(PM, bak)
    r = subprocess.run([sys.executable, "state/frag_write.py", "--agent", "main",
                        "--set-json", tmpj, "--set-field", "answers"],
                       cwd=PROJ, capture_output=True, text=True)
    print("  frag_write rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    if r.returncode != 0:
        print("  ❌ frag_write 失败 ⇒ 已回滚 (备份 %s)" % bak)
        shutil.copy2(bak, PM)
        return 1
    # ★改后对拍 ★
    d2, answers2 = load_answers()
    hits2 = [e for e in answers2 if isinstance(e, dict) and e.get("key") == KEY]
    fp_after = fingerprint(answers2)
    v2 = str(hits2[0].get("value") or "") if hits2 else ""
    checks = [
        ("条目数仍为 1", len(hits2) == 1),
        ("旧建议默认值已不在", STALE not in v2),
        ("新值含上位问题 key", "boss_u1_upper_axis_board_trip_physical_product" in v2),
        ("新值含分层建议 (甲 → B160×100)", "甲 (demo 台架板)" in v2 and "B160×100" in v2),
        ("新值标明非已决定", "建议" in v2 and "不是已决定" in v2),
        ("其余条目逐条未动", fp_after == fp_before),
        ("条目总数不变", len(answers2) == len(answers)),
    ]
    for p, want in PROTECTED.items():
        if want is None:
            continue
        checks.append(("受保护件 %s md5 未动" % p, md5(os.path.join(PROJ, p)) == want))
    for name, c in checks:
        ok = ok and c
        print("  %s %s" % ("✅" if c else "❌", name))
    # ★受保护: 别人的分片不能被我这次改动碰 ★
    for f in ("hw", "sw", "mech"):
        p = os.path.join(PROJ, "state/fragments/%s.yaml" % f)
        checks.append(("别人的分片 %s.yaml 未被本次改动写 (只读校验)" % f, os.path.isfile(p)))
    # ★复跑 merge + gate_check ★
    for cmd, name in (("python3 state/merge.py", "merge.py rc=0"),
                      ("python3 state/gate_check.py", "gate_check.py rc=0")):
        rr = subprocess.run(cmd, cwd=PROJ, shell=True, capture_output=True, text=True,
                            env=dict(os.environ, TMPDIR=os.path.join(PROJ, "tmp")))
        c = rr.returncode == 0
        ok = ok and c
        print("  %s %s (rc=%d)" % ("✅" if c else "❌", name, rr.returncode))
    print("  ⇒ %s (备份 %s)" % ("★订正完成·全绿★" if ok else "★★有红项★★", bak))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
