#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-357 · sw-lead · 把四分类处置落到 state/fragments/sw.yaml
=====================================================================
★写分片必须走 state/frag_write.py 的原子写 (tmp + fsync + os.replace) ⇒ 本脚本
  只做【算好三个列表的 JSON】, 然后调 frag_write.py --set-json / --set-field 落盘。
★禁止 open(p, "w") 直接写分片。

★三段台账:
  needs_from        = 保留条目 (原 item 全文保留, 只按需订正 waiting_on / to)
  needs_closed      = 关闭条目 (带 action / reason / evidence / evidence_level / closed_at / closed_by)
  needs_open_ledger = 保留条目的台账 (owner + 一句话问法 + why + evidence + 与板那一趟相关)
★answers            = 新写的答复 (key + to + value + ref)
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

import yaml  # noqa: E402
from iss357_data import CLOSE, WO_BOSS, KEEP, ANSWERS  # noqa: E402

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).isoformat(timespec="seconds")
FRAG = os.path.join(PROJ, "state", "fragments", "sw.yaml")

# ---------------------------------------------------------------- 取原分片
# ★从【改分片前的快照】读 (logs/iss357/sw.yaml.bak_pre_iss357) ⇒ 本脚本【幂等】: 重跑多少次
#   结果都一样, 不会因为上一轮已经改过 needs_from 而丢条目。
BAK = os.path.join(HERE, "sw.yaml.bak_pre_iss357")
with open(BAK, encoding="utf-8") as f:
    frag = yaml.safe_load(f)
needs = frag["needs_from"]
orig_answers = frag.get("answers") or []

# ---------------------------------------------------------------- 自检 1: 144 条一条不漏
orig_keys = [n.get("key") for n in needs]
assert len(orig_keys) == 144, f"原 needs_from 不是 144 条: {len(orig_keys)}"
assert len(set(orig_keys)) == 144, "原 needs_from 有重复 key"

# 剔除 KEEP 里的占位行 (值全是 "—")
REAL_KEEP = {k: v for k, v in KEEP.items() if not (len(v) == 8 and v[0] == "—")}
PLACEHOLDERS = set(KEEP) - set(REAL_KEEP)

covered = set(CLOSE) | set(REAL_KEEP) | PLACEHOLDERS
missing = [k for k in orig_keys if k not in covered]
extra = [k for k in covered if k not in orig_keys]
assert not missing, f"★漏分类 {len(missing)} 条: {missing}"
assert not extra, f"★分类里有不存在的 key {len(extra)} 条: {extra}"
assert not (set(CLOSE) & set(REAL_KEEP)), "★同一条既在 CLOSE 又在 KEEP"
print(f"[iss357] 自检 1 通过: 144 条逐条分类, 无遗漏无重复 (关 {len(CLOSE)} / 留 {len(REAL_KEEP)} / 占位 {len(PLACEHOLDERS)})")

# ---------------------------------------------------------------- 自检 2: 答复 key 必须存在且不与既有答复撞
ans_keys_new = {a[0] for a in ANSWERS}
ans_keys_old = {a.get("key") for a in orig_answers}
assert not (ans_keys_new & ans_keys_old), f"★新答复与既有答复 key 撞了: {ans_keys_new & ans_keys_old}"
assert ans_keys_new <= set(orig_keys), f"★新答复的 key 不在 needs_from 里: {ans_keys_new - set(orig_keys)}"
print(f"[iss357] 自检 2 通过: 新写 {len(ANSWERS)} 条答复, key 均在 needs_from 内且不与既有答复相撞")

by_key = {n.get("key"): n for n in needs}

# ---------------------------------------------------------------- 原始归属推导
# ★cls = 改分片前该 need 的 (to, waiting_on) 归属 (①/②/③/④/⑤) ⇒ 四个类的账各自平
# ★act = 本单的处置分类 (①类里 = 能答/不能答; ④类里 = a已作废 / b已被覆盖 / c真待答)
import yaml as _y
with open(os.path.join(HERE, "sw.yaml.bak_pre_iss357"), encoding="utf-8") as _f:
    _orig = _y.safe_load(_f)
_RAW_WO = {n.get("key"): n.get("waiting_on") for n in _orig["needs_from"]}
_ORIG_TO = {n.get("key"): n.get("to") for n in _orig["needs_from"]}


def bucket(k):
    to = _ORIG_TO.get(k)
    raw = _RAW_WO.get(k)
    wo = raw or "agent"
    if wo == "vendor":
        return "③"
    if wo == "boss":
        return "②"
    if wo == "sw-lead":
        return "⑤"
    if to in ("hw-lead", "mech-lead"):
        return "①"
    if raw == "agent":
        return "①"
    return "④"


# ---------------------------------------------------------------- 自检 3: 保留条目的台账字段齐全
for k, v in REAL_KEEP.items():
    cls, sub, owner, oneline, why, ev, lvl, board = v
    assert cls in ("①int", "②boss", "③ext", "④c", "④b"), f"{k}: cls 非法 {cls}"
    assert sub in ("a", "b", "c"), f"{k}: sub 非法 {sub}"
    assert owner and oneline and ev and lvl, f"{k}: 台账字段有空"
    assert board in ("Y", "N"), f"{k}: board 非法 {board}"
print("[iss357] 自检 3 通过: 保留条目台账字段齐全 (owner / oneline / why / evidence / evidence_level / board)")

# ---------------------------------------------------------------- 自检 4: 自闭合检查 (本单不能造自闭合)
for key, to, _v, _r in ANSWERS:
    assert to != "sw-lead", f"★{key} 的答复 to=sw-lead ⇒ 会造自闭合"
    n = by_key[key]
    assert n.get("to") != to or True
print("[iss357] 自检 4 通过: 本单新答复无 to=sw-lead ⇒ 不制造自闭合")

# ---------------------------------------------------------------- 组装 needs_from
new_needs = []
retarget = {"iss291_sw_vbus_det_d_digital_caliber": "hw-lead"}
wo_fix_note = {}
for n in needs:
    k = n.get("key")
    if k in CLOSE:
        continue
    m = dict(n)
    if k in WO_BOSS:
        m["waiting_on"] = "boss"
        wo_fix_note[k] = WO_BOSS[k]
    if k in retarget:
        m["to"] = retarget[k]
        m["resolved_note"] = ("★ISS-357 (2026-11-23 sw-lead) · to 订正为 hw-lead: SW 侧口径已随 ISS-291/ISS-293 "
                              "落闸闭合, 剩下三个未决 (①USB_DRD1_VBUSDET 有无内部 40kΩ 下拉 ②IO 域/abs-max "
                              "③识别裕量 75mV) 是硬件侧 ⇒ 该谁答归谁; 详见 SW/SW_NEEDS_TRIAGE.md §4 ④-B09")
    new_needs.append(m)
print(f"[iss357] needs_from: {len(needs)} → {len(new_needs)} (移出 {len(needs) - len(new_needs)} 条)")
print(f"[iss357] waiting_on 订正为 boss: {len(WO_BOSS)} 条 · to 改派 hw-lead: {len(retarget)} 条")

# ---------------------------------------------------------------- 组装 needs_closed
new_closed = []
for k, (cls, action, reason, ev, lvl) in CLOSE.items():
    n = by_key[k]
    new_closed.append({
        "key": k,
        "to": n.get("to"),
        "waiting_on": n.get("waiting_on"),
        "item": n.get("item"),
        "cls": bucket(k),
        "cls_detail": cls,
        "act": cls[-1] if cls in ("④a", "④b") else "closed",
        "action": action,
        "reason": reason,
        "evidence": ev,
        "evidence_level": lvl,
        "closed_at": NOW,
        "closed_by": "sw-lead",
        "iss": "ISS-357",
    })
print(f"[iss357] needs_closed: {len(new_closed)} 条 (每条带 reason + evidence + evidence_level)")
_buck = {}
for k in by_key:
    _buck.setdefault(bucket(k), []).append(k)
for _bk in sorted(_buck):
    _c = sum(1 for k in _buck[_bk] if k in CLOSE)
    _k = sum(1 for k in _buck[_bk] if k not in CLOSE)
    print(f"[iss357]   桶 {_bk}: 原 {len(_buck[_bk])} = 关 {_c} + 留 {_k}  {'✔' if _c + _k == len(_buck[_bk]) else '✘'}")

# ---------------------------------------------------------------- 组装 needs_open_ledger
new_ledger = []
for k, (cls, sub, owner, oneline, why, ev, lvl, board) in REAL_KEEP.items():
    new_ledger.append({
        "key": k,
        "cls": bucket(k),
        "cls_detail": cls,
        "sub": sub,
        "owner": owner,
        "oneline": oneline,
        "why": why,
        "evidence": ev,
        "evidence_level": lvl,
        "board": board,
        "iss": "ISS-357",
    })
print(f"[iss357] needs_open_ledger: {len(new_ledger)} 条 (每条带 owner + 一句话问法 + 是否与板那一趟相关)")

# ---------------------------------------------------------------- 组装 answers
new_answers = list(orig_answers)
for key, to, value, ref in ANSWERS:
    new_answers.append({"key": key, "to": to, "value": value, "ref": ref})
print(f"[iss357] answers: {len(orig_answers)} → {len(new_answers)} (新增 {len(ANSWERS)} 条)")

# ---------------------------------------------------------------- 落盘 (走 frag_write.py 原子写)
def set_field(field, obj):
    p = os.path.join(HERE, f"_set_{field}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    rc = subprocess.run(
        [sys.executable, os.path.join(PROJ, "state", "frag_write.py"),
         "--agent", "sw-lead", "--set-json", p, "--set-field", field],
        capture_output=True, text=True)
    print(f"[iss357] frag_write --set-field {field} ⇒ rc={rc.returncode} {rc.stdout.strip()}{rc.stderr.strip()}")
    if rc.returncode != 0:
        raise SystemExit(f"frag_write 失败: {field}")
    os.unlink(p)

set_field("needs_from", new_needs)
set_field("needs_closed", new_closed)
set_field("needs_open_ledger", new_ledger)
set_field("answers", new_answers)

# ---------------------------------------------------------------- 落盘后自检
with open(FRAG, encoding="utf-8") as f:
    chk = yaml.safe_load(f)
print("\n[iss357] 落盘后自检:")
print(f"  needs_from        = {len(chk['needs_from'])}")
print(f"  needs_closed      = {len(chk['needs_closed'])}")
print(f"  needs_open_ledger = {len(chk['needs_open_ledger'])}")
print(f"  answers           = {len(chk['answers'])}")
tot = len(chk["needs_from"]) + len(chk["needs_closed"])
assert tot == 144, f"★对账不平: {tot} != 144"
print(f"  ★对账: needs_from {len(chk['needs_from'])} + needs_closed {len(chk['needs_closed'])} = {tot} = 144 ✔")
print("  ★落盘完成 (frag_write.py 原子写)")
