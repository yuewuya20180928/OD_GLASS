#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_iss105_rfq_retire_20261112.py —— ★★C 段最后一条「请你放行外发」退休★★

★问题 (★main 2026-11-12 02:1x 实测★):
  `iss105_jchg_rfq_release` 这条 need 只在 `state/fragments/hw.yaml` 里 (★owner=hw-lead 的分片★)
  ⇒ ★**我 (main) 不能写别人的分片** (★hw-lead 此刻还在跑 ISS-195 单 ⇒ 撞车风险★)
  ⇒ ★**但老板 2026-11-12 02:02 的指令是全局事实, 不该因为"条目住在谁的���片里"就退休不掉★**

★解法 (★用项目自己设计的机制, 不绕过铁律★):
  ★**`state/decision_truth.py` 的 `decision_keys()` = 【所有分片里带 decision 的 key 的并集】**
  ⇒ ★**只要【任何一个】分片里记了同 key + decision, 那条 need 在【所有】分片里就算已闭合**
  (★这正是 decision_truth 存在的理由: 「老板拍过板的 need, decision 只被记在被问的那个 agent 的分片里 ⇒ 同 key 在别的分片里没有回写 ⇒ 假挂着」★)
  ⇒ ★**所以在 pm.yaml (★main 自己的分片★) 记一条同 key + decision 的 need ⇒ 老板清单上那条自动消失**
  ⇒ ★**不动 hw.yaml 一根手指 ⇒ 不撞 hw-lead 的在飞单★**

★落账纪律:
  ① 原子写 (走 frag_write.atomic_write_yaml) · 先备份
  ② 写完立刻实测: ★**`advance.py --json` 里 `iss105_jchg_rfq_release` 必须消失 + C 段条数 36 → 35**★
  ③ ★**`merge.py` 冲突必须仍是 0** (★不许因为加了一条 needs_from 就造出冲突★)
  ④ 只碰 pm.yaml 一个文件
"""
import fcntl
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402
import frag_write  # noqa: E402

FRAG = os.path.join(HERE, "fragments", "pm.yaml")
LOCK = os.path.join(HERE, ".frag.lock")
KEY = "iss105_jchg_rfq_release"

DEC = (
    "★老板 2026-11-12 02:02 决定 (★覆盖 11-11 19:31 那条, 并补上【替代方案】★): "
    "★**「不再发信, 全靠自己查资料」** ⇒ ★**J_CHG 询价函 `state/outbox/j_chg_rfq.md` 不发, "
    "也不申请「采购动作豁免」** ⇒ ★**该外部依赖改为【自己网上查】**: "
    "① Hirose FH12-22S-0.5SH(55) 等候选的**官网规格书** (单触点额定电流 / 可插厚度 / 防呆 / 座高) "
    "② **公开分销渠道页面**的单价与交期 (★只作参考区间, 不询价不下单★) "
    "③ 查不到 ⇒ ★**标 `[0数据]` + 记为已知缺口 + 给降级方案 (★如按实测样件验证, 或选官网参数直接满足的替代型号★) "
    "⇒ ★**从待拍板清单退休**★\n"
    "★**本条 decision 记在 pm.yaml (main 自己的分片) 而不是 hw.yaml** ⇒ ★**依据 = `state/decision_truth.py` 的"
    "「老板决策是全局事实」机制 (同 key 在任何分片记了 decision ⇒ 所有分片的同 key need 都算已闭合)★** "
    "⇒ ★**故意不写 hw.yaml (★hw-lead 此刻在跑 ISS-195 ⇒ 不碰别人的分片, 不撞在飞单★)**★"
)


def load(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def advance_keys():
    p = subprocess.run([sys.executable, os.path.join(HERE, "advance.py"), "--json"],
                       capture_output=True, text=True, cwd=os.path.dirname(HERE))
    d = json.loads(p.stdout)
    plan = d.get("plan", d)
    return (plan.get("decisions") or []), plan


def main():
    # ---- 基线 ----
    dec_before, plan_before = advance_keys()
    print("★基线: C 段 %d 条 | iss105 在里面 = %s"
          % (len(dec_before), KEY in [x.get("key") for x in dec_before]))

    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            d = load(FRAG)
            needs = d.setdefault("needs_from", [])
            if any(n.get("key") == KEY for n in needs):
                print("ℹ️ pm.yaml 里已有 %s ⇒ 不动" % KEY)
            else:
                needs.append({
                    "key": KEY,
                    "to": "boss",
                    "item": "★【老板 2026-11-12 02:02 已决 · 本条退休】J_CHG 询价函放行外发 —— "
                            "★**不再发信, 全靠自己查资料** ⇒ 本条不再上老板清单 (★原需求: J_CHG 询价草稿 "
                            "`state/outbox/j_chg_rfq.md` 已就绪但未发, 请求放行外发给 Hirose + 国产对标★)。",
                    "since": "2026-11-12",
                    "due": "2026-11-12",
                    "decided_at": "2026-11-12",
                    "decided_by": "boss (2026-11-12 02:02)",
                    "decision": DEC,
                })
                frag_write.atomic_write_yaml(FRAG, d)
                print("✅ pm.yaml 已原子写: 新增同 key + decision 的 needs_from 条目")
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)

    # ---- 实测 ----
    dec_after, plan_after = advance_keys()
    keys_after = [x.get("key") for x in dec_after]
    ok = True
    print()
    print("=== 验收实测 ===")
    print("  C 段条数: %d → %d" % (len(dec_before), len(dec_after)))
    if KEY in keys_after:
        print("  ❌ %s 还在老板清单上" % KEY)
        ok = False
    else:
        print("  ✅ %s 已从老板清单消失" % KEY)
    if len(dec_after) != len(dec_before) - 1:
        print("  ⚠️ C 段条数不是 -1 (★可能同时有别的变化★)")
    # merge 冲突
    p = subprocess.run([sys.executable, os.path.join(HERE, "merge.py")],
                       capture_output=True, text=True, cwd=os.path.dirname(HERE))
    out = p.stdout + p.stderr
    conf = "?"
    for tok in out.split():
        if tok.isdigit():
            pass
    import re
    m = re.search(r"冲突 (\d+)", out)
    if m:
        conf = m.group(1)
    print("  merge 冲突 = %s %s" % (conf, "✅" if conf == "0" else "❌"))
    if conf != "0":
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
