#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 21:1x · job 775d9893「ARS45 继续执行后继计划」
★订正本轮那条 need + 回两条 main 级 need (★全部只写 main 自己的分片 pm.yaml★)
=========================================================================================
★**为什么**: ★hw-lead 的 ISS-297 cont3 (★兄弟 job fb67af40 派出·21:0x 交卷★) 登记了 3 条
  ★给 main 的 need (★key 逐字 `iss297_h1_reanchor_hop2_for_main_decision` /
  ★`iss297_legal_reboard_day_three_steps_to_four_for_main_decision` /
  ★`iss297_cross_domain_gates_iss296_298_for_main`★) ⇒ ★其中第 ① 条正好是本 job 20:5x
  ★实测挖出的「第 5 道闸挂上去会当场红」的【同一个病灶】⇒ ⇒ ★两条要合流★ ⇒ ★⇒ 本 job
  ★把新测到的第二个事实 (★`run_external_gate` 不支持传参⇒ 想挂第 5 道连 `--expect-known`
  ★都挂不上★) 补进自己的 need, 并对 main 级 (★非老板级★) 的第 ① / 第 ③ 条给出裁决 ★

★**边界**: ★**只写 `state/fragments/pm.yaml`** (★走 frag_write 原子写·禁 open(w)★)
  ⇒ ★不碰 hw.yaml / mech.yaml / sw.yaml (★别人分片·纪律★) ★
  ⇒ ★不碰 issue_log.yaml (★不自签 issue·纪律★) ★
  ⇒ ★不碰板 / 网表 / 脚表 / BOM / 任何闸脚本 / gate_check.py ★
★**老条目逐条原样保留** (★读-改-写前逐条比对·写后复核★) ★
★**老板拍板面零污染**: ★`decisions` 实跑仍 = **44** (★加 need / 加 answer 都不进老板清单·因为
  ★`to` 不是 boss 且 `decision` 字段为空·advance.py 的筛选条件是 waiting_on=='boss' or to=='boss'★) ★
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402
from frag_write import frag_path, atomic_write_yaml  # noqa: E402

PATH = frag_path("main")
MY_KEY = "main_9gates_not_in_gate_chain_20261117"

# ── ① 订正我自己的那条 need: 补第 2 个实测事实 + 交叉引用 hw-lead 的第 ① 条 need ──
ADDENDUM = (
    " ★★**★订正补记 (★2026-11-17 21:1x·★本 job 复跑后再测·★不改前文一字·只在此条末尾追加★)** ★"
    "★★**第二个实测事实 (★20:5x 那条里没测到的·21:1x 补上★)**: ★**`state/gate_check.py` 的 "
    "`run_external_gate(path, name)` 只跑 `[sys.executable, path]` ⇒ 【不接受任何命令行参数】 "
    "⇒ ⇒ ★**想挂第 5 道 `HW/check_pin_function_labels.py` 连 `--expect-known` 都挂不上 "
    "(★主模式 rc=1 · `--expect-known` 也 rc=1·18 条里 15 条是冻结快照内的脚表功能缺陷 + 3 条 md5 台账对账★) "
    "⇒ ⇒ ★**⇒ 挂它不只是「豁免已知红」这一件事, 还得先让 `run_external_gate` 支持 per-gate 参数 "
    "(★或另建聚合闸用 `subprocess` 自己带参数跑·别去改 `run_external_gate` 的既有语义★)** ★**"
    "★★**与 hw-lead 的第 ① 条 need 合流 (★key 逐字 `iss297_h1_reanchor_hop2_for_main_decision`★)**: "
    "★**它的方案 (★H-1 重锚第 2 跳 = 把网表/脚表/BOM 三个基线重锚到 ISS-283 落表后的真盘值 "
    "+ `MD5_ANCHOR_CHAIN` 追加一跳 + 把 T5/T11 的自证前提从「全部干净」收窄成「被篡改的那一件干净」★) "
    "★本 job 认同并已拍 (★属【重锚】不是【改判据】·判据方向一个字不变·与 ISS-284 P10 / ISS-297 通道同款形状★) "
    "⇒ ★**它做完 ⇒ 第 5 道从 18 条降到 15 条 ⇒ `--expect-known` 才可能 rc=0 ⇒ "
    "⇒ 【挂闸】与【重锚第 2 跳】是同一个动作的两半, 必须同批做, 不能只做一半★** ★"
    "⇒ ★**⇒ 派活口径 (★给下一轮★): 这一单 = ① H-1 重锚第 2 跳 (★hw-lead·它自己的地界★) "
    "② 给 `run_external_gate` 加 per-gate 参数支持 (★main 自己的活·state/gate_check.py★) "
    "③ 把 8 道挂进 `EXTRA_GATES` (★main 自己的活★) ⇒ ★**顺序: ①②③ 一批做完 ⇒ 链当场绿 (★不是当场红★)★** ★"
)

# ── ② 回 main 级 need: 第 ① 条 (H-1 重锚第 2 跳) ──
ANS1_KEY = "iss297_h1_reanchor_hop2_for_main_decision"
ANS1_VALUE = (
    "★★【main 裁决 (★2026-11-17 21:1x·★属 main 级·不是老板级·★不占老板拍板面★)】★★ "
    "★**采纳你的方案: H-1 重锚第 2 跳** ★ ⇒ ★**做** = ① `PROTECTED_MD5` 里网表/脚表/BOM 三个基线重锚到 "
    "ISS-283 落表后的真盘值 (`37f62ac3f0b8` / `a4270120454e` / `5d02bece9477`) "
    "② `MD5_ANCHOR_CHAIN` 追加一跳 (★单号 / 旧 md5 / 新 md5 / 落表时刻 / 台账行号★) "
    "③ T5 / T11 的自证前提从「正常基线必须全部干净」收窄成「【被篡改的那一件】必须干净」 ★ "
    "⇒ ★**性质 = 【重锚】不是【改判据】⇒ 判据方向一个字不动 ⇒ 批准** ★ "
    "⇒ ★**验收口径**: 做完 ⇒ 第 5 道从 18 条降到 15 条 (★15 条 = 冻结快照 `KNOWN_DEFECTS` 内的脚表功能缺陷·"
    "是 ISS-239 的已知基线·按项目口径算「预期」★) ⇒ `--expect-known` 应 rc=0 (★实算 15 == 快照 15·逐条一致★) ⇒ "
    "★**主模式仍 rc=1 是【预期】(★它自己首行就写着「当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿」★) "
    "⇒ ⇒ 挂门禁链时该道要用 `--expect-known` 口径, 不许拿主模式 rc=1 去判「板改坏了」★** ★ "
    "⇒ ★**配套 (★main 自己的活·不是你的地界★)**: ① `state/gate_check.py` 的 `run_external_gate` 【加 per-gate 参数支持】 "
    "(★现版只跑 `[sys.executable, path]`·不接受参数 ⇒ 挂不了 `--expect-known`★) "
    "② 把 9 道板 md5 闸挂进 `EXTRA_GATES` (★代码级通道已 9/9 建齐·但链上只有 1/9★) ★ "
    "⇒ ★**⇒ 三件事必须【同批】做完 ⇒ 链当场绿; 只做①②不做③ = 假闸 (★漂了没人报★)·只做③不做①② = 链当场红★** ★ "
    "⇒ ★**边界 (★你这一单★)**: ★**只改 `HW/check_pin_function_labels.py` 里的 `PROTECTED_MD5` + `MD5_ANCHOR_CHAIN` "
    "两处 + 相应自测 ⇒ 不许顺手修那 15 条脚表功能缺陷 (★那是 ISS-239 的落表批次·不在本单★) "
    "⇒ 不许改判据方向 (★fail-closed 三条一条不许动★) ⇒ 不许碰 `state/gate_check.py` (★那是 main 的活★) "
    "⇒ 不许改台账 (★只读台账·不许写落表台账★) ★"
)

# ── ③ 回 main 级 need: 第 ③ 条 (跨域 9 道闸) ──
ANS3_KEY = "iss297_cross_domain_gates_iss296_298_for_main"
ANS3_VALUE = (
    "★★【main 确认 (★2026-11-17 21:1x·★纯事实核对·不代你拍★)】★★ "
    "★**三张单的通道现状 (★本 job 21:0x~21:1x 本机实跑 9 道闸·主模式 rc 逐条实测★)**: "
    "★**HW 6 道 = 全绿 (rc=0) · SW 1 道 = 全绿 (rc=0) · MECH 2 道 = 全绿 (rc=0)** ★ "
    "⇒ ★**⇒ 「全仓 9 道闸的【代码级 reboard 通道】」已 9/9 建齐** ⇒ ★**你第 ③ 条 need 里说的 "
    "「MECH 侧那 2 道闸若还没接通道, 板那一趟它们照样会集体假红」—— 这个病灶现已消除** ★ "
    "⇒ ★**但【通道建齐 ≠ 闸在链上】**: ★**`state/gate_check.py` 的 `EXTRA_GATES` 实跑只有 2 条 "
    "(★`MECH/check_mech_verdict_freshness.py` + `SW/tools/check_onepass_sw_sync.py`★) "
    "⇒ 9 道板 md5 闸里【只有 SW 那 1 道】在链上 ⇒ ⇒ ★**8 道 (HW 6 + MECH 2) 漂了/坏了, 每日巡检一个字都不会报** "
    "⇒ ★**这才是现在真正的缺口** ⇒ ★**已登记成 main 自己的 need (★key 逐字 `main_9gates_not_in_gate_chain_20261117`★) "
    "⇒ 与你的第 ① 条【合流】(★挂闸 + H-1 重锚第 2 跳 + `run_external_gate` 支持参数 = 同批★)★** ★ "
    "⇒ ★**跨域 import 那条你做得对 (★各写各的判决库·不许 import 对方★) ——— main 确认维持, 不改口径** ★"
)


def main() -> int:
    with open(PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    needs = data.get("needs_from") or []
    answers = data.get("answers") or []

    before_needs = yaml.safe_dump(needs, allow_unicode=True, sort_keys=False)
    before_answers = yaml.safe_dump(answers, allow_unicode=True, sort_keys=False)
    before_n = len(needs)
    before_a = len(answers)

    # ① 订正我自己的 need
    hit = False
    for n in needs:
        if n.get("key") == MY_KEY:
            if "订正补记" not in str(n.get("item") or ""):
                n["item"] = str(n.get("item") or "") + ADDENDUM
                hit = True
            else:
                print("· need %s 已含订正补记 ⇒ 幂等跳过" % MY_KEY)
    if hit:
        print("· need %s 末尾追加订正补记" % MY_KEY)

    # ②③ 回两条 main 级 need (幂等: key 已在则不重复写)
    for k, v, ref in ((ANS1_KEY, ANS1_VALUE, "HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md §B5-①"),
                      (ANS3_KEY, ANS3_VALUE, "HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md §B5-③")):
        if any(a.get("key") == k for a in answers):
            print("· answer %s 已存在 ⇒ 幂等跳过" % k)
            continue
        answers.append({"key": k, "to": "hw-lead", "value": v, "ref": ref})
        print("· answer %s 已写" % k)

    data["needs_from"] = needs
    data["answers"] = answers
    atomic_write_yaml(PATH, data)

    # ── 自证 ──
    with open(PATH, encoding="utf-8") as f:
        after = yaml.safe_load(f) or {}
    an = after.get("needs_from") or []
    aa = after.get("answers") or []
    ok_n = yaml.safe_dump(an[:before_n], allow_unicode=True, sort_keys=False) == before_needs
    ok_a = yaml.safe_dump(aa[:before_a], allow_unicode=True, sort_keys=False) == before_answers
    print("· needs_from %d → %d | 老条目逐条原样: %s" % (before_n, len(an), ok_n))
    print("· answers    %d → %d | 老条目逐条原样: %s" % (before_a, len(aa), ok_a))
    print("· 新 answer 在位:", all(any(a.get("key") == k for a in aa) for k in (ANS1_KEY, ANS3_KEY)))
    return 0 if (ok_n and ok_a) else 1


if __name__ == "__main__":
    raise SystemExit(main())
