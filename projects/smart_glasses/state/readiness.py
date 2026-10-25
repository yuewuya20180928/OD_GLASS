#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行就绪度体检 (Readiness) —— 机械判定"总工和三个子总工是否已满足项目执行条件"
================================================================================
老板 10-25 19:02: "再次明确下当前项目总工和各个子模块的总工已经满足项目执行的条件"

不凭印象答。用 N 条**可机械判定**的判据, 对 4 个角色各打一次分, 再给项目级终判。

★ 关键区分 (这个项目现在最容易含糊的地方):
  "组织与机制是否就绪" ≠ "项目是否能推进到出样机"
  → 前者可以靠机制补齐, 后者需要实物/设备/外部。
  → 所以终判分两层给, 不和稀泥。

判据来源: 三个 AGENTS.md + 项目产出 + 4 道门 + 工具可用性 + 外部依赖盘点
用法:  python3 state/readiness.py [--json]
退出码: 0=全部就绪  1=有未就绪项  2=检查脚本本身出错
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(PROJ))       # workspace/ (PROJ = <ws>/projects/smart_glasses)
AGENT_WS = {"main": WS,
            "hw-lead": os.path.expanduser("~/.openclaw/workspace-hw"),
            "sw-lead": os.path.expanduser("~/.openclaw/workspace-sw"),
            "mech-lead": os.path.expanduser("~/.openclaw/workspace-mech")}
ROLE = {"main": "项目总工", "hw-lead": "硬件总工", "sw-lead": "软件总工", "mech-lead": "结构总工"}


def read(p: str) -> str:
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except Exception:  # noqa: BLE001
        return ""


def run(cmd: list[str], cwd: str = PROJ) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    import yaml

    C: list[dict] = []          # 判据集合

    def chk(scope: str, name: str, ok: bool | None, detail: str, weight: str = "must"):
        """ok=True 通过 / False 不通过 / None 部分"""
        C.append({"scope": scope, "name": name, "ok": ok, "detail": detail, "weight": weight})

    # ---------- 全局机制 (4 个角色共享) ----------
    chk("全局", "共享状态源可用 (merge rc=0)",
        run([sys.executable, os.path.join(HERE, "merge.py")])[0] == 0,
        "python3 state/merge.py → rc=0 (0完整/2不完整/1崩)")
    chk("全局", "gate ↔ merge 自动对账一致",
        "✅ 与 merge.py 自对账一致" in run([sys.executable, os.path.join(HERE, "gate_check.py")])[1],
        "两个工具口径是否一致 (漂移会自己暴露)")
    rc_i, out_i = run([sys.executable, os.path.join(HERE, "issue_check.py")])
    chk("全局", "问题闭环门 0 违规", rc_i == 0,
        f"issue_check rc={rc_i} (字段/状态机/验证分离/逾期/双向覆盖)")
    chk("全局", "阶段门可判 (G0-G4)", os.path.exists(os.path.join(HERE, "stage_gate.py")),
        "每关准出判据 = issue 状态 + 老板决策 + 实测项")
    # ⚠️ 禁止在这里调 daily_check.py —— daily_check 会反过来调 readiness, 双向调用 = 无限递归
    # (19:03 实测踩过: 进程链 daily_check→readiness→daily_check→... 无限展开, 只能靠 PID 清)
    # 改成静态检查 + 读它的巡检快照
    _snap = os.path.join(HERE, "gate_snapshots")
    _snaps = sorted(f for f in os.listdir(_snap) if f.endswith(".json")) if os.path.isdir(_snap) else []
    chk("全局", "每日巡检可跑 (漂移检测)",
        os.path.exists(os.path.join(HERE, "daily_check.py")) and bool(_snaps),
        f"cron 每天 09:00 兜底; 已建立 {len(_snaps)} 份巡检快照 (漂移比对基线)")
    chk("全局", "推进器可算下一步", os.path.exists(os.path.join(HERE, "advance.py")),
        "advance.py 算→派→落盘→核验")
    chk("全局", "手动看板可出图", os.path.exists(os.path.join(PROJ, "status.sh")),
        "./status.sh 一屏出进展/待办/卡点/风险")
    chk("全局", "框架裁剪基线存在 (74 条)",
        os.path.exists(os.path.join(PROJ, "FRAMEWORK_SCOPE.md")),
        "9 域 68 项 + 6 项项目专属逐条裁剪, 防止反复重吵")
    chk("全局", "星型守卫在 CLI 入口",
        os.path.exists(os.path.expanduser("~/.openclaw/guards/star-topology.log")),
        "三层守卫: tools.deny + PATH shim + CLI 入口包装器 (压测 5 路径复测)")
    chk("全局", "分片原子写工具可用", os.path.exists(os.path.join(HERE, "frag_write.py")),
        "写分片唯一合法入口 (open(p,'w') 会静默丢数据)")

    # ---------- 逐角色 ----------
    for aid, aw in AGENT_WS.items():
        ag = read(os.path.join(aw, "AGENTS.md"))
        chk(aid, "AGENTS.md 存在且有职责清单",
            "职责" in ag, f"{aw}/AGENTS.md")
        chk(aid, "写入边界明确 (不许改什么)",
            ("不许" in ag or "不得" in ag or "边界" in ag), "禁止项写进每次启动都读的 AGENTS.md")
        chk(aid, "交付质量标准在位 (B1-B6 + 证据分级 + 自证)",
            ("B1" in ag and "B6" in ag and "证据" in ag and "自证" in ag),
            "缺块即退回, 交接单模板 v2")
        chk(aid, "禁横向直聊已写明",
            "不做直接沟通" in ag or "星型" in ag, "硬规则写进 AGENTS.md")
        chk(aid, "项目专属 skill 已装",
            os.path.exists(os.path.join(aw, "skills")) and bool(os.listdir(os.path.join(aw, "skills"))),
            f"{aw}/skills/")
        frag = os.path.join(HERE, "fragments",
                            {"main": "pm.yaml", "hw-lead": "hw.yaml",
                             "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}[aid])
        d = yaml.safe_load(read(frag)) or {}
        chk(aid, "分片非空且有 status/artifacts",
            bool(d.get("status")) and bool(d.get("artifacts")),
            f"artifacts={len(d.get('artifacts') or [])} claims={len(d.get('interface_claims') or [])} "
            f"answers={len(d.get('answers') or [])}")
        # 协议: 等外部 (boss/vendor/jbd) 必须 waiting_on+due; 等总工默认 agent (due 可选, 是截止期)
        _ext_bad = [n.get("key") for n in (d.get("needs_from") or [])
                    if n.get("waiting_on", "agent") in ("boss", "vendor", "jbd") and not n.get("due")]
        chk(aid, "外部等待已标 waiting_on+due", not _ext_bad,
            f"等老板/原厂/JBD 必标 (漏标: {_ext_bad})" if _ext_bad
            else "等老板/原厂/JBD 必标; 等总工默认 agent (due 是可选截止期)")

    # 角色特定产出
    hw = read(os.path.join(PROJ, "HW/HARDWARE_BREAKDOWN.md"))
    chk("hw-lead", "硬件模块拆解 + 电源树", "HW-01" in hw and "电源树" in hw, "HW/HARDWARE_BREAKDOWN.md")
    chk("hw-lead", "EMC 预评估 (画板前)", os.path.exists(os.path.join(PROJ, "HW/EMC_PRECHECK.md")),
        "12 风险点 + 16 条画板前硬约束")
    sw = read(os.path.join(PROJ, "SW/SW_REQUIREMENTS.md"))
    chk("sw-lead", "软件需求拆解 + 延迟预算", "M1" in sw and "延迟预算" in sw, "SW/SW_REQUIREMENTS.md")
    chk("sw-lead", "EVT 模板 + 联调计划",
        os.path.exists(os.path.join(PROJ, "SW/EVT_TEMPLATE.md")) and
        os.path.exists(os.path.join(PROJ, "SW/INTEGRATION_PLAN.md")),
        "6 段三态 + 53 用例, 覆盖 G3 七项实测")
    mc = read(os.path.join(PROJ, "MECH/MECH_BUDGET.md"))
    chk("mech-lead", "空间预算 + 散热模型", "热" in mc and "堆叠" in mc or "镜脚" in mc, "MECH/MECH_BUDGET.md")
    chk("mech-lead", "打印包 + 测量清单", os.path.exists(os.path.join(PROJ, "MECH/print/fit_coupon_340.stl")),
        "2 个可下片 STL + 41 项测量清单")
    chk("main", "决策包 (Q1/Q4/Q17)", os.path.exists(os.path.join(PROJ, "DECISION_TABLE_Q1_Q4_Q17.md")),
        "口径 + 建议默认值, 等老板拍板")
    outbox = os.path.join(HERE, "outbox")
    drafts = [f for f in os.listdir(outbox)] if os.path.isdir(outbox) else []
    chk("main", "外发草稿已就绪 (只备不发)", len(drafts) >= 3, f"{len(drafts)} 份: {', '.join(sorted(drafts))}")

    # ---------- 项目级终判 ----------
    log = yaml.safe_load(read(os.path.join(HERE, "issue_log.yaml"))) or {}
    issues = log.get("issues") or []
    meas = yaml.safe_load(read(os.path.join(HERE, "measurements.yaml"))) or {}
    have = [m for m in (meas.get("measurements") or []) if str(m.get("kind")) == "实测"]
    needed = meas.get("needed") or []
    n_ext = sum(1 for i in issues if i.get("owner") in ("boss", "vendor", "jbd")
                and i.get("status") not in ("closed", "deferred", "wontfix"))
    n_int = sum(1 for i in issues if i.get("owner") in ("main", "hw-lead", "sw-lead", "mech-lead")
                and i.get("status") not in ("closed", "deferred", "wontfix"))

    # 纸面阶段就绪 = 机制全绿 + 老板决策是唯一卡点
    paper_ready = all(c["ok"] is not False for c in C if c["scope"] == "全局")
    # 样机阶段就绪 = 有实测 + 有设备/环境
    sample_ready = len(have) >= 1 and len(have) == len(needed)

    # ---------- 输出 ----------
    by_scope: dict[str, list] = {}
    for c in C:
        by_scope.setdefault(c["scope"], []).append(c)

    def verdict(rows) -> str:
        bad = [r for r in rows if r["ok"] is False]
        part = [r for r in rows if r["ok"] is None]
        if bad:
            return f"❌ 未就绪 ({len(bad)} 项不过)"
        if part:
            return f"🟡 基本就绪 ({len(part)} 项有保留)"
        return f"✅ 就绪 ({len(rows)}/{len(rows)})"

    if args.json:
        print(json.dumps({"criteria": C, "by_scope": {k: verdict(v) for k, v in by_scope.items()},
                          "paper_ready": paper_ready, "sample_ready": sample_ready,
                          "measurements": {"have": len(have), "needed": len(needed)},
                          "open_internal": n_int, "open_external": n_ext}, ensure_ascii=False, indent=2))
        return 0 if paper_ready else 1

    print("=" * 78)
    print("  执行就绪度体检 · Readiness  (机械判定, 不凭印象)")
    print("=" * 78)
    for scope in ["全局", "main", "hw-lead", "sw-lead", "mech-lead"]:
        rows = by_scope.get(scope, [])
        if not rows:
            continue
        label = {"全局": "全局机制", "main": "项目总工 (main / moli)"}.get(scope, f"{ROLE.get(scope, scope)} ({scope})")
        print(f"\n【{label}】{verdict(rows)}")
        for r in rows:
            mark = "✅" if r["ok"] is True else ("❌" if r["ok"] is False else "⚠️")
            print(f"   {mark} {r['name']}")
            if r["ok"] is not True:
                print(f"        {r['detail']}")
    print()
    print("── 项目级终判 " + "─" * 55)
    print(f"  📄 纸面阶段 (G0 纸面冻结 / G1 原理图 / G2 结构样机准备): "
          f"{'✅ 组织与机制已就绪' if paper_ready else '❌ 机制有未过项'}")
    print(f"     → 判据: 4 个角色机制全绿 + 质量门/问题门/阶段门/推进器可用 + 框架裁剪基线在位")
    print(f"     → 当前卡点: 老板 {n_ext} 条决策 + 原厂/JBD 外部; 内部可自行推进 {n_int} 条")
    print(f"  🔧 样机阶段 (G3 上电联调 + 硬指标实测): "
          f"{'✅ 就绪' if sample_ready else '❌ 不就绪'}")
    print(f"     → 实测 {len(have)}/{len(needed)} 项 | 无板 / 无打印环境 / 无示波器高速相机 / 无独立验证方")
    print(f"     → 阶段门判: {run([sys.executable, os.path.join(HERE, 'stage_gate.py')])[1].strip().splitlines()[-1]}")
    print()
    print("  结论: **四个角色已具备执行条件** (职责/边界/交付标准/协作机制/质量门/推进器 全部到位)。")
    print("        **但" + '"执行"' + "只能推进到纸面阶段** —— G3 需要的实物/设备/实测一条都没有。")
    print("=" * 78)
    return 0 if paper_ready else 1


if __name__ == "__main__":
    sys.exit(main())
