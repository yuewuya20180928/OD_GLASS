#!/usr/bin/env python3
"""STATE 合并器自测 — 证明三件事真的работает (不是摆设)

    python3 state/test_merge.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge as M  # noqa: E402

FAILS = []


def check(name: str, cond: bool, extra: str = "") -> None:
    if cond:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}  {extra}")
        FAILS.append(name)


def frag(agent: str, **kw) -> dict:
    d = {"agent": agent, "role": agent}
    d.update(kw)
    return d


def test_conflict_detected():
    print("\n[1] 冲突检测: 同一 key 不同值 → 必须报冲突")
    frags = {
        "hw": frag("hw", interface_claims=[{"key": "pcb_outline", "value": "50x12mm"}]),
        "mech": frag("mech", interface_claims=[{"key": "pcb_outline", "value": "60x15mm"}]),
    }
    st = M.build_state(frags)
    check("检出 1 个冲突", len(st["conflicts"]) == 1, str(st["conflicts"]))
    check("冲突 key 正确", st["conflicts"] and st["conflicts"][0]["key"] == "pcb_outline")
    check("冲突双方值都记录", st["conflicts"] and
          st["conflicts"][0]["values"] == {"hw": "50x12mm", "mech": "60x15mm"})


def test_no_false_conflict():
    print("\n[2] 假阳性防护: 同值不同措辞/带注释 → 不能报冲突")
    cases = [
        ("50x12mm", "50x12mm"),
        ("50x12mm", "50x12mm (待确认)"),
        ("50x12mm", "50 x 12 mm"),
        ("38-40C", "38-40C"),
        ("4-6层", "4-6 层 (锁死)"),
    ]
    for a, b in cases:
        frags = {
            "hw": frag("hw", interface_claims=[{"key": "k", "value": a}]),
            "mech": frag("mech", interface_claims=[{"key": "k", "value": b}]),
        }
        st = M.build_state(frags)
        check(f"'{a}' vs '{b}' → 不冲突", len(st["conflicts"]) == 0, str(st["conflicts"]))


def test_needs_answers_pairing():
    print("\n[3] needs_from × answers 按 key 配对")
    frags = {
        "hw": frag("hw", needs_from=[{"key": "k1", "to": "mech", "item": "PCB 外形"}]),
        "mech": frag("mech", answers=[{"key": "k1", "to": "hw", "value": "50x12mm"}]),
    }
    st = M.build_state(frags)
    need = st["domains"]["hw"]["needs_from"][0]
    check("已配对 → answered", need["state"] == "answered", str(need))
    check("答案带上了回答方", need["answers"] and need["answers"][0]["by"] == "mech")
    check("pending 计数为 0", st["needs_matrix"]["pending"] == [])

    frags2 = {
        "hw": frag("hw", needs_from=[{"key": "k1", "to": "mech", "item": "PCB 外形"}]),
        "mech": frag("mech", answers=[{"key": "other", "to": "hw", "value": "x"}]),
    }
    st2 = M.build_state(frags2)
    check("key 对不上 → 仍 pending", st2["domains"]["hw"]["needs_from"][0]["state"] == "pending")

    # ⚠️ 别人不能替被问的人闭合需求
    frags3 = {
        "hw": frag("hw", needs_from=[{"key": "k1", "to": "main", "item": "Q16 显示接口"}]),
        "mech": frag("mech", answers=[{"key": "k1", "to": "hw", "value": "v"}]),
    }
    st3 = M.build_state(frags3)
    n3 = st3["domains"]["hw"]["needs_from"][0]
    check("非被问方回答 → 不得闭合需求", n3["state"] == "pending", str(n3))
    check("外来回答被单独记下", len(n3.get("foreign_answers") or []) == 1, str(n3))


def test_digest():
    print("\n[4] 切片摘要: 别人在等我 / 我欠谁")
    frags = {
        "main": frag("main", status={"summary": "s", "health": "green"}),
        "hw": frag("hw", needs_from=[{"key": "k1", "to": "main", "item": "Q16 显示接口"}]),
        "mech": frag("mech", answers=[{"key": "k1", "to": "mech", "value": "v"}]),
    }
    st = M.build_state(frags)
    d = M.digest_for(st, "main")
    check("main 看到 hw 在等他 (未被回答)", "Q16 显示接口" in d, d)
    check("main 的切片列出欠账", "我欠别人的" in d)
    d2 = M.digest_for(st, "hw")
    check("hw 的切片里自己那条仍欠着 (main 未答)", "→ main" in d2, d2)


def test_canonical_values_not_flagged():
    print("\n[8] 规范值不能被误判成散文 (10-25 真实误报回归测试)")
    canon_vals = [
        "无桥接340-575mAh/有桥接575-675mAh",
        "口径A:55.7/67.0/83.7ms,口径C:42.3/50.3ms",
        "俯角20-32度/FOV>=100度/边框凹进<=1.5mm",
        "38-40C(红线43C)",
        "4-6层",
        "50x12mm",
        "9.5x3.6mm",
    ]
    for v in canon_vals:
        check(f"'{v}' → 不算散文", not M.is_prose(v))
    # 这些必须被认成散文
    for v in ["皮肤侧 ≤38-40°C, 红线 43°C (ISO 13732-1) 超过就该降功耗",
              "建议先做原型再量产",
              "这个值还没定下来"]:
        check(f"'{v[:20]}...' → 算散文", M.is_prose(v))


def test_answers_unknown_key_lint():
    print("\n[9] answers.key 无人引用 → lint (防 key 写错静默失败)")
    frags = {
        "hw": frag("hw", needs_from=[{"key": "k1", "to": "mech", "item": "x"}]),
        "mech": frag("mech", answers=[{"key": "typo_key", "to": "hw", "value": "v"}]),
    }
    st = M.build_state(frags)
    check("错 key 被标 lint", any(l["key"] == "typo_key" for l in st["lint"]), str(st["lint"]))
    check("错 key 不闭合需求", st["domains"]["hw"]["needs_from"][0]["state"] == "pending")


def test_needs_normalization_bucket():
    print("\n[10] 一边是散文 → 进 needs_normalization, 不判冲突")
    frags = {
        "hw": frag("hw", interface_claims=[{"key": "k", "value": "50x12mm"}]),
        "mech": frag("mech", interface_claims=[{"key": "k", "value": "PCB 板子外形 50 乘 12 毫米 这边还带点别的说明"}]),
    }
    st = M.build_state(frags)
    check("不判冲突", len(st["conflicts"]) == 0, str(st["conflicts"]))
    check("进待规范化", len(st["needs_normalization"]) == 1, str(st.get("needs_normalization")))


def test_prose_value_lint():
    print("\n[7] 散文 value → 标 lint 且不参与冲突比较")
    frags = {
        "hw": frag("hw", interface_claims=[{"key": "k", "value": "50x12mm"}]),
        "mech": frag("mech", interface_claims=[{"key": "k", "value": "皮肤侧 38-40 度红线 43 度 ISO 标准要求 必须按这个来"}]),
    }
    st = M.build_state(frags)
    check("散文值不报冲突", len(st["conflicts"]) == 0, str(st["conflicts"]))
    check("散文值进 lint", len(st["lint"]) == 1, str(st["lint"]))
    check("lint 指出是哪个 agent", st["lint"] and st["lint"][0]["agent"] == "mech")


def test_atomic_write():
    print("\n[5] 原子写: 写出来的 STATE.yaml 能被 yaml 解析, 且不留 tmp")
    tmpdir = tempfile.mkdtemp()
    try:
        p = os.path.join(tmpdir, "STATE.yaml")
        M.atomic_write(p, "a: 1\nb:\n  - x\n")
        import yaml
        d = yaml.safe_load(open(p, encoding="utf-8"))
        check("yaml 可解析", d == {"a": 1, "b": ["x"]}, str(d))
        check("没留 .tmp", not os.path.exists(p + ".tmp"))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_real_repo_state():
    print("\n[6] 真实项目: 合并当前分片不炸, 且字段齐全")
    frags, _issues = M.load_fragments()
    check("读到 4 个分片", len(frags) == 4, str(list(frags.keys())))
    st = M.build_state(frags)
    for k in ("meta", "project", "domains", "interface_claims", "needs_matrix",
              "blockers", "conflicts", "risks", "summary"):
        check(f"STATE 有 {k}", k in st)
    check("4 个域都在", set(st["domains"]) == {"main", "hw-lead", "sw-lead", "mech-lead"})
    check("当前无冲突", len(st["conflicts"]) == 0, str(st["conflicts"]))


if __name__ == "__main__":
    for t in (test_conflict_detected, test_no_false_conflict, test_needs_answers_pairing,
              test_digest, test_atomic_write, test_real_repo_state, test_prose_value_lint,
              test_canonical_values_not_flagged, test_answers_unknown_key_lint,
              test_needs_normalization_bucket):
        t()
    print("\n" + "=" * 60)
    if FAILS:
        print(f"❌ {len(FAILS)} 项失败: {FAILS}")
        sys.exit(1)
    print("✅ 全部通过")
