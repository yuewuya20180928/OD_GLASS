#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 20:5x · job 775d9893「ARS45 继续执行后继计划」
★把本轮实测到的「9 道闸只有 1 道在门禁链上」登记成 main 自己的 need (原子写)★
=========================================================================================
★**为什么用脚本不用命令行**: ★frag_write.py 的 --add-need 用 shlex 拆参数 ⇒
  ★本条 item 含空格/引号/★ ⇒ 命令行拆散 ⇒ argparse 报 unrecognized ⇒ 改用它的
  ★**文档化 Python API** `update_fragment("main", fn)` (★同一套原子写实现·tmp+fsync+os.replace★) ★

★**边界**: ★**只写 main 自己的分片 `state/fragments/pm.yaml`** (★走 frag_write 原子写·禁 open(w)★)
  ⇒ ★不碰 hw.yaml / mech.yaml / sw.yaml (★别人分片·纪律★) ★
  ⇒ ★不碰 issue_log.yaml (★不自签 issue·纪律★) ★
  ⇒ ★不碰板 / 网表 / 脚表 / BOM / 任何闸脚本 ★
★**只追加 1 条 need** ⇒ ★老条目零删改 (★读-改-写前逐条比对老条目数量与内容★) ★
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402
from frag_write import frag_path, atomic_write_yaml  # noqa: E402

KEY = "main_9gates_not_in_gate_chain_20261117"
PATH = frag_path("main")

ITEM = (
    "★★【本 job 2026-11-17 20:5x 实测 · ★不是抄任何 agent 报告★】★★ "
    "★**「板只改一次」那一趟的 9 道钉板 md5 闸: 【代码级通道】9/9 已建齐 "
    "(★ISS-296 MECH 2 道 / ISS-297 HW 6 道 / ISS-298 SW 1 道 · 本 job 实跑 9 道主模式: 8 道 rc=0 · 第 5 道 rc=1★) "
    "⇒ 但【门禁链挂载】只有 1/9★** ★ "
    "⇒ ★**`state/gate_check.py` 的 `EXTRA_GATES` 实跑只有 2 条 "
    "(★`MECH/check_mech_verdict_freshness.py` + `SW/tools/check_onepass_sw_sync.py`★) "
    "⇒ 9 道板 md5 闸里【只有 SW 那 1 道】在链上 · 其余 8 道 (★HW 6 + MECH 2★) 谁都不跑★** ★ "
    "⇒ ★**`state/daily_check.py` 直接跑的 15 个脚本里【一道都不是】这 9 道 "
    "(★实测清单: chain_gate / check_pcb_drc / check_pcb_nets / check_sch_erc / check_sch_pinfull / "
    "check_stage_g1a / compare_arm_official / decision_truth / gate_check / issue_check / "
    "margin_sweep_gate / merge / readiness / stage_gate / daily_check★) "
    "⇒ ★**⇒ 这 8 道闸哪天漂了/坏了, 每日巡检【一个字都不会报】★** ★ "
    "⇒ ★**这正是 MEMORY 铁律④「新闸交卷后第一件事不是『验收通过』, 是【挂进门禁链 + 让它真跑一次】」"
    "的第 N+1 次复现 (★20:0x 已挂过 2 条 · 这 8 条漏挂★)** ★ "
    "⇒ ★**同型第二条洞: `state/land_v_values.py` 的 `ALL_GATES` (落表后全闸扫描) 里【只有 3 道】是这 9 道 "
    "(★`HW/check_onepass_commit_order` / `HW/check_onepass_preflight_coverage` / `MECH/check_board_frame_coords`★) "
    "⇒ 其余 6 道也不在落表扫描里** ★ "
    "⇒ ★**★main 裁决 (★本 job 只登记·不代做★): ① 把 8 道补进 `state/gate_check.py` 的 `EXTRA_GATES` "
    "(★fail-closed 同款: 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算闸红·绝不「没跑就当过」★) "
    "② 或另建一道「9 道闸统一跑」聚合闸挂进链上 (★一次跑完 9 道 + `--selftest`·任一红 ⇒ 聚合闸红★) "
    "③ ★**必须同时解决「已知红基线」: 第 5 道 `HW/check_pin_function_labels.py` 现在主模式 rc=1 "
    "(★18 条既有缺陷基线 = 15 条脚表功能缺陷 + 3 条 md5 台账对账 · `--expect-known` 也 rc=1 · "
    "成因 = `PROTECTED_MD5` 里网表/脚表/BOM 三个基线还停在 ISS-257 时的旧值, 而 ISS-283 落表后真盘已是新值★) "
    "⇒ ★**它挂上去会让门禁链【当场红】⇒ 这不是本 job 能单方面做的改动 ⇒ "
    "要么带「已知红基线豁免」机制一起上 (★判据不许松: 只豁免【已登记的既有缺陷条数】·其余仍红★) "
    "要么先修那 3 条 md5 基线 (★ISS-297 交卷单 B5 已把这条列为未决并明写「留给 main 拍板」★)** ★ "
    "⇒ ★**⇒ 派活时必须把这一点一起说清, 否则执行方会以为「挂上去就行」而把整条链挂红★** ★ "
    "⇒ ★**另 (本 job 实测踩到的环境坑): `state/check_pcb_nets.py` 【必须走 `bash state/pcbnew_py.sh`】 "
    "—— 直跑 `python3 state/check_pcb_nets.py` 报 `ModuleNotFoundError: No module named 'pcbnew'` "
    "⇒ 走 pcbnew_py.sh 才拿到真读数: ★C1 焊盘级等价红 (★网表 480 / 板上 482 · 缺失 0 · 多余 2 · 同号异网 3★)· C2 全绿★** ★"
)


def main() -> int:
    with open(PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    needs = data.get("needs_from") or []
    if any(n.get("key") == KEY for n in needs):
        print("· need %s 已存在 ⇒ 幂等跳过" % KEY)
        return 0
    before_keys = [n.get("key") for n in needs]
    before_dump = yaml.safe_dump(needs, allow_unicode=True, sort_keys=False)

    needs.append({
        "key": KEY,
        "to": "main",
        "item": ITEM,
        "since": "2026-11-17T20:55:00+08:00",
    })
    data["needs_from"] = needs
    atomic_write_yaml(PATH, data)

    # ── 自证: 老条目逐条原样保留 (只追加 1 条) ──
    with open(PATH, encoding="utf-8") as f:
        after = yaml.safe_load(f) or {}
    after_needs = after.get("needs_from") or []
    after_dump = yaml.safe_dump(after_needs[:len(before_keys)], allow_unicode=True, sort_keys=False)
    ok = after_dump == before_dump
    print("· pm.yaml 追加 need %s" % KEY)
    print("· needs_from 条数: %d → %d" % (len(before_keys), len(after_needs)))
    print("· 老条目逐条原样保留:", ok)
    print("· 新 key 在位:", any(n.get("key") == KEY for n in after_needs))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
