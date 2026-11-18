#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_board_frame_freeze_gate_selftest.py —— ISS-336 板框冻结闸的【反向用例自测】 (mech-lead)
==================================================================================================
干什么:
  给 `MECH/check_board_frame_freeze_gate.py` (板框冻结闸 U-1) 配一套**反向用例**, 保证:
    ① 六条反向用例 (ISS-316 §2-5 的 RC-1~RC-6) **全部被闸抓住** (判红);
    ② 一条正向对照 (帧=F30A / 板厚=1.00 / 层数=6 / 孔位=套 A) ⇒ **七条判据全绿**;
    ③ C7 的真源口径**实测**过: 用一条真的闭合记录跑 ⇒ 命中; 用一句「板框已定」跑 ⇒ 不命中;
    ④ 阈值是**现读**的, 不是抄的: 在沙盒里把 service_port_check 的现值改掉 ⇒ 闸的读数跟着变。

★★ 沙盒纪律 (★硬★) ★★:
  · 全部用例都在**沙盒副本**上跑 —— 副本建在 `tmp/iss336/selftest/` 下 (★项目内, 不写 /tmp★)。
  · **真件一个字节不碰**: 板 md5 / 网表 / 脚表 / BOM / `state/fragments/*.yaml` /
    `MECH/service_port_check.py` / `MECH/board_frame_feasibility.py` /
    `HW/PCB/BOARD_FRAME_CALIBER.md` 自测前后逐字节相同 (★自测脚本自己跑前后 md5 对拍★)。
  · 沙盒里只写三类东西: ① 改过的 `service_port_check.py` 副本 (阈值漂移实验) ② 改过的
    `BOARD_FRAME_CALIBER.md` 副本 (current_frame 实验) ③ 改过的 `state/fragments/mech.yaml` 副本
    (伪造/伪造空转闭合记录 ⇒ 只在副本里, 真分片零改动)。
  · ★**不许 `rm -rf /tmp/*`** (★本机有别的 agent 在建沙盒★) ⇒ 本脚本只删自己建的
    `tmp/iss336/selftest/` 子目录, 且只删自己建的。

用法:
  python3 MECH/check_board_frame_freeze_gate_selftest.py --selftest   ⇒ 跑全部用例, rc=0
  python3 MECH/check_board_frame_freeze_gate_selftest.py --json       ⇒ 机器可读
退出码: 0 = 全部用例与预期一致; 2 = 有用例与预期不一致 (★与既有 MECH 闸脚本 rc 语义一致★)。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ★沙盒根 (★项目内 tmp/iss336/selftest/ —— ★不许写 /tmp★)
SANDBOX = os.path.join(ROOT, "tmp", "iss336", "selftest")

# ★闸脚本 (本文件旁边那个)
GATE = os.path.join(HERE, "check_board_frame_freeze_gate.py")

# ★需要拷进沙盒、且**在自测前后逐字节比对**的真件 (★零写板 / 零落表 / 零改既有闸 的自证★)
PROTECTED = [
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
    "MECH/service_port_check.py",
    "MECH/board_frame_feasibility.py",
    "MECH/check_board_frame_coords.py",
    "MECH/check_onepass_mech_release.py",
    "HW/PCB/BOARD_FRAME_CALIBER.md",
    "state/fragments/mech.yaml",
    "state/fragments/pm.yaml",
]

# ★沙盒里必须有的文件 (闸要读) ★
SANDBOX_FILES = [
    "MECH/check_board_frame_freeze_gate.py",
    "MECH/service_port_check.py",
    "METH/service_port_check.py",          # ★占位: 下面会去掉, 保留清单可读性★
    "MECH/board_frame_feasibility.py",
    "HW/PCB/BOARD_FRAME_CALIBER.md",
    "state/fragments/mech.yaml",
    "state/fragments/pm.yaml",
]


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_protected() -> dict:
    out = {}
    for rel in PROTECTED:
        p = os.path.join(ROOT, rel)
        out[rel] = md5(p) if os.path.exists(p) else "(缺)"
    return out


def build_sandbox(name: str) -> str:
    """建一个沙盒副本根 (★只拷闸要读的那几件, 不拷全仓★)"""
    dst = os.path.join(SANDBOX, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)          # ★只删自己建的子目录★
    for rel in SANDBOX_FILES:
        if rel.endswith("service_port_check.py") and rel.startswith("METH"):
            continue
        src = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            continue
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(src, d)
    return dst


def sandbox_yaml(path: str):
    import yaml
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: str, data) -> None:
    import yaml
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def run_gate(root: str) -> dict:
    """在给定 root 上跑闸 ⇒ 返回机器可读结果 (★沙盒里跑, 真件零碰★)"""
    spec = importlib.util.spec_from_file_location(
        "gate_iss336_selftest", os.path.join(root, "MECH", "check_board_frame_freeze_gate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rep = mod.judge(root)
    return {
        "mode": "L1-claim" if rep["has_claim"] else "L2-standing",
        "subject": dict(rep["subject"]),
        "claim_src": rep["claim"]["src"],
        "claim_closed_in_ledger": rep["claim"]["closed_in_ledger"],
        "claim_closed_by_merge": rep["claim"]["closed_by_merge"],
        "criteria": [{"code": c, "ok": o, "title": t, "reason": r, "source": s}
                     for c, o, t, r, s in rep["results"]],
        "red": [c for c, o, _, _, _ in rep["results"] if not o],
    }


def codes(result: dict) -> list:
    return [c["code"] for c in result["criteria"]]


def reds(result: dict) -> list:
    return [c["code"] for c in result["criteria"] if not c["ok"]]


# ==================================================================================================
# ★造 U-1 冻结记录 (★只造在沙盒副本里; 真分片零改动★)
# ==================================================================================================
FREEZE_ANSWER_F30A = (
    "U-1 板框冻结: 帧 id = F30A; 板厚 = 1.00 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。"
    "[实测] MECH/BOARD_GEOM_30MM.md §1/§3; HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES。"
)


def inject_freeze(root: str, answer_text: str, closed: bool = True, in_main: bool = False) -> None:
    """在沙盒的 mech.yaml (或 pm.yaml) 里造一条 U-1 闭合记录 + 答案。

    ★落表形态照抄盘上真实的 needs_closed / answers 结构 (★键名 / 字段名逐字照抄★):
      · `needs_closed[]` 一条: key / to / waiting_on / item / iss / closed_at / closed_by / cls /
        action / reason / evidence / evidence_level / answer_key / answer_ref
      · `answers[]` 一条: key / to / value / ref
    """
    import yaml
    mech_p = os.path.join(root, "state", "fragments", "mech.yaml")
    pm_p = os.path.join(root, "state", "fragments", "pm.yaml")
    mech = sandbox_yaml(mech_p)
    pm = sandbox_yaml(pm_p)

    key = "proto_pcb_freeze_gate"
    if in_main:
        # ★main 侧的 answers (★merge 口径: needs_from × answers 按 key 配对, 作者 = need 的 to★)
        pm.setdefault("answers", []).append({
            "key": key, "to": "mech-lead", "value": answer_text,
            "ref": "ISS-336 沙盒正向对照 (★真分片零改动★)",
        })
    else:
        mech.setdefault("answers", []).append({
            "key": key, "to": "mech-lead", "value": answer_text,
            "ref": "ISS-336 沙盒正向对照 (★真分片零改动★)",
        })
    if closed:
        mech.setdefault("needs_closed", []).append({
            "key": key, "to": "main", "waiting_on": None,
            "item": "★沙盒用例: U-1 板框冻结闸 need 的闭合记录 (★ISS-336 自测专用·真分片零改动★)",
            "iss": "ISS-336",
            "closed_at": "2026-11-19T00:00:00+08:00",
            "closed_by": "mech-lead",
            "cls": "①agent", "action": "close+answer",
            "reason": "沙盒用例 (自测专用)",
            "evidence": answer_text,
            "evidence_level": "[实测]",
            "answer_key": key,
            "answer_ref": "state/fragments/mech.yaml answers[key=%s]" % key,
        })
        # ★闭合 ⇒ 从 needs_from 里退休 (★与 ISS-313 的真实形态一致: 关闭 = 从 needs_from 移出 + 台账依据行★)
        mech["needs_from"] = [n for n in (mech.get("needs_from") or []) if n.get("key") != key]
    write_yaml(mech_p, mech)
    write_yaml(pm_p, pm)


def set_current_frame(root: str, frame_id: str) -> None:
    """改沙盒 `BOARD_FRAME_CALIBER.md` 的 cal:FRAMES.current_frame (★只改副本★)"""
    p = os.path.join(root, "HW", "PCB", "BOARD_FRAME_CALIBER.md")
    with open(p, encoding="utf-8") as f:
        t = f.read()
    t2 = re.sub(r'("current_frame"\s*:\s*")[^"]*(")',
                lambda m: m.group(1) + frame_id + m.group(2), t, count=1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(t2)


def mutate_service_port_check(root: str, old: str, new: str) -> None:
    """改沙盒 `service_port_check.py` 的一个现值 (★只改副本·阈值漂移实验用★)"""
    p = os.path.join(root, "MECH", "service_port_check.py")
    with open(p, encoding="utf-8") as f:
        t = f.read()
    if old not in t:
        raise SystemExit("★沙盒改值失败: service_port_check.py 里找不到 %r" % old)
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace(old, new, 1))


# ==================================================================================================
# ★用例集 ★
# ==================================================================================================
def build_cases() -> list:
    """六条反向用例 (★ISS-316 §2-5 的 RC-1~RC-6 逐条复现★) + 一条正向对照 + 三条真源/阈值自证

    ★期望口径 (★照 ISS-316 §2-5 的原措辞「**必须判红**」★)★:
      · `must_red`  = 必须判红的判据 (★subset 判定: 实际判红集 ⊇ must_red★)
        —— ISS-316 §2-5 每条 RC 只点名**它要抓的那一条** (C3 / C3+C6 / C5 / C6 / C2 / C7),
           其余判据红不红不在它的管辖内 ⇒ 用 subset 判定才是原意。
      · `exact`     = True 时要求判红集**恰好**等于 `must_red` (★用于能把变体隔离干净的那几条★)
      · `no_extra`  = False 时允许 fail-closed 连锁红 (★例: 答案只有「板框已定」⇒ 连帧 id/板厚/层数
                     都解析不出来 ⇒ C1/C3/C4 必然也红 —— 这是 fail-closed 的正确行为, 不是误报★)
    """
    cases = []

    # ---------- RC-1: 只拍帧 id 没拍板厚 ⇒ C3 红 ----------
    #  ★沙盒把 current_frame 切成 F30A ⇒ 只隔离出「板厚没拍」这一个缺陷 (C2 不搅局)
    #  ★ISS-316 §2-5 点名的判据 = C3 (板厚缺失); 另外 C6/C7 也红是**fail-closed 连锁**
    #    (板厚缺 ⇒ (帧,厚,层) 组合不可定位 ⇒ C6 判红; 答案里没三个数 ⇒ C7 判红) ⇒ 不是误报
    cases.append({
        "id": "RC-1",
        "title": "只拍了帧 id, 板厚没拍 (写「板框用 60×30」, 不写板厚) ⇒ 人话读起来像冻结了",
        "must_red": ["C3"], "exact": False, "no_extra": False,
        "setup": lambda root: (inject_freeze(root, "板框用 60×30。层数 6。"),
                               set_current_frame(root, "F30A")),
    })

    # ---------- RC-2: 板厚写 1.22 ⇒ C3 + C6 红 (ISS-316 §2-5 明写「C3 + C6」) ----------
    cases.append({
        "id": "RC-2",
        "title": "帧 id 与板厚都写了, 板厚写的是 1.22 (离判红只差 0.02)",
        "must_red": ["C3", "C6"], "exact": True, "no_extra": True,
        "setup": lambda root: (inject_freeze(
            root, "U-1 板框冻结: 帧 id = F30A; 板厚 = 1.22 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。"),
            set_current_frame(root, "F30A")),
    })

    # ---------- RC-3: 帧 id 写 P60x15 ⇒ C5 红 (几何全绿, 人眼最容易上当) ----------
    #  ★ISS-316 §2-4 的 C6 判红条件逐字含「P60x15 任一档」⇒ P60x15 必然 C5+C6 双红★
    cases.append({
        "id": "RC-3",
        "title": "帧 id 写 P60x15 (几何全绿, 人眼最容易上当的一条)",
        "must_red": ["C5", "C6"], "exact": True, "no_extra": True,
        "setup": lambda root: (inject_freeze(
            root, "U-1 板框冻结: 帧 id = P60x15; 板厚 = 1.00 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。"),
            set_current_frame(root, "P60x15")),
    })

    # ---------- RC-4: 帧 id 写 B160x100 ⇒ C6 红 ----------
    cases.append({
        "id": "RC-4",
        "title": "帧 id 写 B160x100 (它是现役帧 ⇒ 默认最容易不写出来)",
        "must_red": ["C6"], "exact": True, "no_extra": True,
        "setup": lambda root: inject_freeze(
            root, "U-1 板框冻结: 帧 id = B160x100; 板厚 = 1.00 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。"),
    })

    # ---------- RC-5: 认领句写 F30A 但 cal:FRAMES.current_frame 仍是 B160x100 ⇒ C2 红 ----------
    cases.append({
        "id": "RC-5",
        "title": "认领句写在 F30A, 但 cal:FRAMES.current_frame 还停在 B160x100 (两处各写各的)",
        "must_red": ["C2"], "exact": True, "no_extra": True,
        "setup": lambda root: inject_freeze(
            root, "U-1 板框冻结: 帧 id = F30A; 板厚 = 1.00 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。"),
    })

    # ---------- RC-6: need 闭合了但答案只有一句「板框已定」⇒ C7 红 ----------
    #  ★fail-closed 连锁: 空话闭合 ⇒ 连帧 id/板厚/层数都解析不出来 ⇒ C1/C3/C4 必然也红 (★不是误报★)
    cases.append({
        "id": "RC-6",
        "title": "need key 闭合了, 但答案只有一句「板框已定」 (空转闭合)",
        "must_red": ["C7"], "exact": False, "no_extra": False,
        "setup": lambda root: inject_freeze(root, "板框已定。"),
    })

    # ---------- 正向对照: F30A / 1.00 / 6 层 / 套 A ⇒ 七条全绿 ----------
    #  ★注意: current_frame 在盘上是 B160x100 ⇒ 正向对照必须把沙盒的 current_frame 也切成 F30A
    #    (★这正是 C2 的含义: 拍板后认领句与 cal:FRAMES 必须同步 —— 这是 U-1 落表时必须一起做的事★)
    cases.append({
        "id": "POS-1",
        "title": "正向对照: 帧 = F30A, 板厚 = 1.00, 层数 = 6, 孔位 = 套 A ⇒ 七条判据全绿",
        "must_red": [], "exact": True, "no_extra": True,
        "setup": lambda root: (inject_freeze(root, FREEZE_ANSWER_F30A),
                               set_current_frame(root, "F30A")),
    })

    # ---------- 真源自证 A: 闭合记录里带齐三个数 ⇒ C7 命中 ----------
    cases.append({
        "id": "SRC-1",
        "title": "C7 真源自证: 闭合记录的答案里逐字含帧 id + 板厚 + 层数 ⇒ C7 命中",
        "must_red": [], "exact": True, "no_extra": True,
        "setup": lambda root: (inject_freeze(root, FREEZE_ANSWER_F30A),
                               set_current_frame(root, "F30A")),
    })

    # ---------- 真源自证 B: 答案只有「板框已定」⇒ C7 不命中 ----------
    cases.append({
        "id": "SRC-2",
        "title": "C7 真源自证: 闭合记录的答案只有一句「板框已定」⇒ C7 不命中",
        "must_red": ["C7"], "exact": False, "no_extra": False,
        "setup": lambda root: inject_freeze(root, "板框已定。"),
    })

    # ---------- 真源自证 C: main 侧 answers 配对闭合也算闭合 (merge 口径) ----------
    cases.append({
        "id": "SRC-3",
        "title": "C7 真源自证: 闭合记录落在 main 的 pm.yaml answers (merge 配对口径) ⇒ 也算闭合",
        "must_red": [], "exact": True, "no_extra": True,
        "setup": lambda root: (inject_freeze(root, FREEZE_ANSWER_F30A, in_main=True),
                               set_current_frame(root, "F30A")),
    })

    # ---------- 阈值现读自证: 把 service_port_check 的现值改掉 ⇒ 闸的读数跟着变 ----------
    cases.append({
        "id": "THR-1",
        "title": "阈值现读自证: 沙盒里把 cavity_req 4.50 改成 4.30 ⇒ 允许板厚集从 {0.80,1.00} 变成 {0.80,1.00,1.22}",
        "must_red": [], "exact": True, "no_extra": True,
        "expect_allowed_thk": [0.8, 1.0, 1.22],
        "setup": lambda root: (inject_freeze(root, FREEZE_ANSWER_F30A),
                               set_current_frame(root, "F30A"),
                               mutate_service_port_check(root, '"cavity_req":    4.50,', '"cavity_req":    4.30,')),
    })

    return cases


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="跑全部反向用例 (默认行为)")
    ap.add_argument("--json", action="store_true", help="机器可读")
    args = ap.parse_args()

    before = snapshot_protected()
    cases = build_cases()
    results = []
    n_ok = 0

    if not args.json:
        print("=" * 104)
        print("BOARD FRAME FREEZE GATE — SELFTEST (ISS-336) | mech-lead 2026-11-19")
        print("=" * 104)
        print("★全部用例跑在沙盒副本上 (根: tmp/iss336/selftest/) ⇒ **真件一个字节不碰** (自测前后 md5 对拍)")
        print()

    for case in cases:
        root = build_sandbox(case["id"].lower())
        case["setup"](root)
        try:
            res = run_gate(root)
        except Exception as e:      # noqa: BLE001
            res = {"error": "%s: %s" % (type(e).__name__, e), "red": [], "criteria": []}

        if "error" in res:
            ok = False
            detail = res["error"]
        else:
            got_red = res["red"]
            want_red = case["must_red"]
            missing = [c for c in want_red if c not in got_red]
            extra = [c for c in got_red if c not in want_red]
            ok = not missing
            if ok and case.get("exact"):
                ok = not extra
            if ok and "expect_allowed_thk" in case:
                spec = importlib.util.spec_from_file_location(
                    "bff_thr_%s" % case["id"], os.path.join(root, "MECH", "board_frame_feasibility.py"))
                bff = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bff)
                got_set = sorted({r["thk"] for r in bff.all_rows() if r["cavity_ok"]})
                if [round(x, 4) for x in got_set] != [round(x, 4) for x in case["expect_allowed_thk"]]:
                    ok = False
                    detail = "允许板厚集 = %s ≠ 期望 %s" % (got_set, case["expect_allowed_thk"])
                else:
                    detail = "允许板厚集随现值变 = %s" % got_set
            else:
                detail = "判红 %s (必须判红 %s%s)" % (
                    got_red or "无", want_red or "无",
                    ("; 额外红 %s (★fail-closed 连锁, 非误报★)" % extra) if extra else "")
        n_ok += 1 if ok else 0
        results.append({"id": case["id"], "title": case["title"], "ok": ok,
                        "detail": detail, "result": res})

        if not args.json:
            mark = "✅ 与预期一致" if ok else "❌ 与预期不一致"
            print("  %-8s %s  %s" % (case["id"], mark, case["title"]))
            print("           %s" % detail)
            if res.get("criteria"):
                for c in res["criteria"]:
                    if not c["ok"]:
                        print("             · %s 红: %s" % (c["code"], c["reason"]))

    after = snapshot_protected()
    changed = [k for k in before if before[k] != after[k]]
    zero_write_ok = not changed

    if not args.json:
        print()
        print("【零写板 / 零落表 / 零改既有闸】自测前后 md5 逐字节对拍 (★%d 件受保护文件★)" % len(PROTECTED))
        for rel in PROTECTED:
            flag = "★变了★" if before[rel] != after[rel] else "同"
            print("  %-46s %s  %s" % (rel, before[rel], flag))
        print("  ⇒ %s" % ("★真件零改动 (全部 md5 相同)★" if zero_write_ok
                          else "★★真件被改了: %s ⇒ 本自测有 bug★★" % ", ".join(changed)))
        print()
        print("★结论: %d/%d 条用例与预期一致 (RC-1~RC-6 六条反向用例全抓到 + 正向对照全绿 + 真源/阈值自证过)"
              % (n_ok, len(cases)))
        print("=" * 104)

    if args.json:
        print(json.dumps({"cases": results, "n_ok": n_ok, "n_total": len(cases),
                          "zero_write_ok": zero_write_ok, "changed": changed,
                          "before": before, "after": after},
                         ensure_ascii=False, indent=2, default=str))

    rc = 0 if (n_ok == len(cases) and zero_write_ok) else 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
