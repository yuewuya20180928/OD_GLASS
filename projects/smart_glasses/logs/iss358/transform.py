#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-358 cont1 · mech.yaml 分片改造器 (生成新段 JSON, ★不直接写分片★ —— 写只走 state/frag_write.py)

改造项:
  (1) answers   : 8 条改 key (value/to/ref 一字不动)
  (2) artifacts : 31 组同 path 登记 → 每 path 1 条 (被并入的 summary 逐字保留在 base 的 summary 里)
  (3) interface_claims : 1 组逐字相同重名 → 留 1 条
输出:
  logs/iss358/new_answers.json / new_artifacts.json / new_interface_claims.json
  logs/iss358/dedup_list.md (可追回清单)
"""
import os, sys, json, yaml, collections

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(PROJ, "logs", "iss358")
SRC = os.path.join(PROJ, "state", "fragments", "mech.yaml")

with open(SRC, "r", encoding="utf-8") as f:
    d = yaml.safe_load(f)

# ---------- (1) answers 改 key ----------
# idx(0 基) -> 新 key;  None = 不改
RENAME_ANS = {
    1:  "pcb_outline_confirm_2_cavity",                 # 镜脚内腔需求(下限)
    2:  "pcb_outline_confirm_3_camera_mount",            # 摄像头安装
    3:  "pcb_outline_confirm_4_thermal_path",            # 散热接触路径
    6:  "pcb_outline_confirm_5_mfit_result",             # M-FIT 结果
    5:  "ntc_placement_2_power_budget",                  # 持续功耗上限/结温档位
    7:  "ntc_placement_3_struct_constraint",             # 结构侧硬约束(余量 0.30mm)
    37: "iss219_mech_c7_sink_area_confirm_2_live_caliber_threshold",  # 活口径 W_rim 门槛重算
    40: "iss264_mech_jd_y0_and_open_y_caliber",          # → 既有 need (ISS-264 状态), 逐字对应
}
answers = []
ans_log = []
for i, a in enumerate(d["answers"]):
    b = dict(a)
    if i in RENAME_ANS:
        old = b.get("key")
        b["key"] = RENAME_ANS[i]
        ans_log.append({"idx": i, "old_key": old, "new_key": RENAME_ANS[i],
                        "to": a.get("to"), "vlen": len(str(a.get("value") or "")),
                        "ref": a.get("ref"), "value": a.get("value")})
    answers.append(b)
assert len(answers) == len(d["answers"]), "answers 条数必须不变"
# 自检: 改 key 后不得出现重名
kc = collections.Counter(a.get("key") for a in answers)
dups = {k: n for k, n in kc.items() if n > 1}
assert not dups, "改 key 后 answers 仍有重名: %s" % dups
# 自检: 除 key 外其余字段逐字不变
for i, (a, b) in enumerate(zip(d["answers"], answers)):
    if i in RENAME_ANS:
        assert {k: v for k, v in a.items() if k != "key"} == {k: v for k, v in b.items() if k != "key"}, \
            "idx %d 非 key 字段被改动" % i

# ---------- (2) artifacts 同 path 合并 ----------
arts = d["artifacts"]
bypath = collections.OrderedDict()
for i, a in enumerate(arts):
    bypath.setdefault(a.get("path"), []).append((i, a))
merge_log = []
new_arts = []
for path, members in bypath.items():
    if len(members) == 1:
        new_arts.append(dict(members[0][1]))
        continue
    # base = 信息最全 (summary 最长); 同长取 updated_at 最新; 再同取 idx 最小
    members_sorted = sorted(members, key=lambda t: (-len(str(t[1].get("summary") or "")),
                                                     str(t[1].get("updated_at") or ""), t[0]),
                            reverse=False)
    # updated_at 最新优先 ⇒ 先按 -len, 再按 -updated_at, 再 idx 升序
    members_sorted = sorted(members, key=lambda t: (-len(str(t[1].get("summary") or "")),
                                                     [-ord(ch) for ch in str(t[1].get("updated_at") or "")],
                                                     t[0]))
    base_idx, base = members_sorted[0]
    others = [(i, a) for i, a in members if i != base_idx]
    b = dict(base)
    base_sum = str(base.get("summary") or "")
    blocks = []
    for i, a in others:
        blocks.append("〔原登记 #%d · kind=%s · version=%s · updated_at=%s〕%s"
                      % (i, a.get("kind"), a.get("version"), a.get("updated_at"),
                         str(a.get("summary") or "")))
    b["summary"] = (base_sum + "\n‖ ISS-358 cont1 同 path 合并: 本条为该 path 的主登记, 以下 %d 条独立登记"
                    "按原文逐字并入 (未删字, 可按 #序号追回):\n" % len(others)) + "\n".join(blocks)
    new_arts.append(b)
    merge_log.append({"path": path, "base_idx": base_idx,
                      "base_kind": base.get("kind"), "base_version": base.get("version"),
                      "base_updated_at": base.get("updated_at"), "base_summary": base_sum,
                      "absorbed": [{"idx": i, "kind": a.get("kind"), "version": a.get("version"),
                                    "updated_at": a.get("updated_at"),
                                    "summary": str(a.get("summary") or "")} for i, a in others]})
assert len(new_arts) == len({a.get("path") for a in new_arts}), "artifacts 仍有同 path 重复"
# 自检: 并入后所有原文 summary 仍在
for m in merge_log:
    for ab in m["absorbed"]:
        assert ab["summary"] in [x for x in new_arts if x.get("path") == m["path"]][0]["summary"], \
            "artifacts %s 的原 summary 丢了" % m["path"]

# ---------- (3) interface_claims 逐字重名 ----------
claims = d["interface_claims"]
seen = {}
new_claims = []
claim_log = []
for i, c in enumerate(claims):
    key = c.get("key")
    sig = json.dumps(c, ensure_ascii=False, sort_keys=True)
    if key in seen and seen[key][0] == sig:
        claim_log.append({"dropped_idx": i, "kept_idx": seen[key][1], "key": key,
                          "entry": c})
        continue
    seen.setdefault(key, (sig, i))
    new_claims.append(dict(c))

for name, val in (("answers", answers), ("artifacts", new_arts),
                  ("interface_claims", new_claims)):
    with open(os.path.join(OUT, "new_%s.json" % name), "w", encoding="utf-8") as f:
        json.dump(val, f, ensure_ascii=False, indent=1)
    print("写出 new_%s.json : %d 条 (原 %d)" % (name, len(val),
          len(d[{"answers": "answers", "artifacts": "artifacts", "interface_claims": "interface_claims"}[name]])))

with open(os.path.join(OUT, "renames.json"), "w", encoding="utf-8") as f:
    json.dump(ans_log, f, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "merge_log.json"), "w", encoding="utf-8") as f:
    json.dump(merge_log, f, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "claim_log.json"), "w", encoding="utf-8") as f:
    json.dump(claim_log, f, ensure_ascii=False, indent=1)
print("answers 改 key %d 条 | artifacts 合并 %d 组 | interface_claims 去重 %d 条"
      % (len(ans_log), len(merge_log), len(claim_log)))
