#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-10-30 00:2x —— 项目总工 (moli) 本轮台账动作 (v2, 加锁版)
================================================================================
★并发注意 (2026-10-30 00:2x 实测): 老板的 webchat 会话 (= 同一个 main agent 的另一个会话)
  在 00:06 也写了 state/issue_log.yaml (顺延 due + 关 ISS-049) ⇒ **issue_log.yaml 有并发写者**。
  ⇒ 本脚本: ①flock 串行 ②锁内重新读盘 ③锁内改 + 原子写 (tmp + os.replace)
  ⇒ 已经被人做掉的 (ISS-049) 不重复做, 只补一条独立复核 note。

① verify_date 回填 × 8   —— 依据 = 各单 verify_result 首段的复核日期 (抄的, 不是编的)
② 亲核关单 × 1         —— ISS-080 (verify_by=main, owner=sw-lead ⇒ 验证分离成立)
③ 新登记 × 1           —— ISS-120 (S2 板端实测, 从 ISS-080 拆出, EVT BR-01 门禁)
   (ISS-121 骨架重量超差 **不另开单**: 已在 state/fragments/hw.yaml needs_from
    "骨架截面形状 + 重量口径 (ISS-049)" 里跟踪 ⇒ 重复登记 = 噪声)

纪律: 不改 §0 锁死表 · 不动其他 agent 的分片
"""
from __future__ import annotations

import fcntl
import os
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-10-30"
STAMP = "2026-10-30 00:2x"


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)          # ★锁内重读 (不锁外读的那份)
        issues = log["issues"]
        by = {i["id"]: i for i in issues}
        done = []

        # ---------- ① verify_date 回填 ----------
        backfill = {
            "ISS-037": ("2026-10-27", 'verify_result 首段 "2026-10-27 09:0x 项目总工独立复核"'),
            "ISS-085": ("2026-10-27", 'verify_result 首段 "2026-10-27 09:0x 项目总工独立复核"'),
            "ISS-090": ("2026-10-27", 'verify_result 首段 "2026-10-27 20:1x 项目总工逐条复核"'),
            "ISS-091": ("2026-10-28", 'verify_result 首段 "2026-10-28 00:5x 项目总工验收"'),
            "ISS-093": ("2026-10-27", 'verify_result 首段 "2026-10-27 19:4x 项目总工验收"'),
            "ISS-099": ("2026-10-28", 'verify_result 首段 "2026-10-28 01:0x 项目总工验收"'),
            "ISS-100": ("2026-10-28", 'verify_result 首段 "2026-10-28 01:0x 项目总工验收"'),
        }
        for iid, (vd, src) in backfill.items():
            it = by[iid]
            if it.get("verify_date"):
                done.append(f"{iid} 跳过 (已有 verify_date={it.get('verify_date')})")
                continue
            assert it["status"] == "verified", (iid, it["status"])
            it["verify_date"] = vd
            it["note"] = (it.get("note") or "") + \
                f"\n★{STAMP} 项目总工回填 verify_date={vd} —— 依据: {src} (★回填, 非当场记录)"
            done.append(f"{iid} 回填 verify_date={vd}")

        # ISS-074: verified 但 verify_result/verify_date 全空 —— 补登记 (口径写清楚: hw-lead 当时判**不通过**)
        it = by["ISS-074"]
        if it.get("verify_date"):
            done.append("ISS-074 跳过 (已有 verify_date)")
        else:
            it["verify_date"] = "2026-10-28"
            it["verify_result"] = (
                f"{STAMP} 项目总工补登记 (★事后回填, 口径必须写清楚): "
                "① hw-lead V1.2 复审 (HANDOFF/2026-10-27_hw-lead_V1.2复审.md) 结论 = **不通过** "
                "(8 问: 2 通过 / 1 部分通过 / 4 不通过 / 1 部分不通过) ⇒ 本单交付**当时没过** "
                "② 缺陷在 V1.3~V1.8 修掉, 复审链 = ISS-075 (10-27 pass) + ISS-088 (10-28 pass, main 判) "
                "③ 现版自证: `python3 state/check_netlist.py` rc=0 (全过) + `python3 state/check_kicad_net.py` rc=0 "
                "+ `python3 HW/pinset2_check.py` rc=0 (35/36, FAIL 0) "
                "④ 故 verify_date 取 **2026-10-28** (ISS-088 闭环日) —— ★不等于 10-27 就通过"
            )
            it["note"] = (it.get("note") or "") + \
                f"\n★{STAMP} 项目总工回填 verify_date=2026-10-28 + verify_result (依据链见 verify_result; ★事后回填)"
            done.append("ISS-074 回填 verify_date=2026-10-28 + verify_result")

        # ---------- ② ISS-049: 已被 webchat 会话关单, 只补独立复核 note ----------
        it = by["ISS-049"]
        if it.get("status") == "verified":
            it["note"] = (it.get("note") or "") + \
                (f"\n★{STAMP} cron 会话 (main) 独立复核补记: `python3 HW/pinset2_check.py` → rc=0, 35/36, **FAIL 0**, "
                 "WARN 1 = 骨架重量超 MECH_BUDGET §2.4 B 的 '+1-3g' 口径 0.62g —— ★该 WARN 不另开单, "
                 "已在 `state/fragments/hw.yaml` needs_from『骨架截面形状 + 重量口径 (ISS-049)』里跟踪 "
                 "(满宽 4.86g/对 判死 / 台阶形 3.62g/对 仍超 0.62g) ⇒ 请 mech-lead 定截面形状 (台阶/U形/槽形) 并回口径")
            done.append("ISS-049 补独立复核 note (未重复关单)")

        # ---------- ③ ISS-080 亲核关单 (方案层) ----------
        it = by["ISS-080"]
        if it.get("status") == "verified":
            done.append("ISS-080 跳过 (已被关单)")
        else:
            assert it["status"] == "fixed" and it.get("owner") == "sw-lead" and it.get("verify_by") == "main"
            it["status"] = "verified"
            it["verify_date"] = TODAY
            it["verify_result"] = (
                f"{STAMP} 项目总工独立复核 (★口径: 本单交付的是**方案**, 不是板端实测通过): "
                "① 交卷内容齐: SW/FLASH_AND_VERSION.md §4.5 (S2 可执行实测方案: P1~P4 参数位 + t1~t4 时序骨架 + "
                "3 条识别分支 + CB-01~09 机械判据 + L0/L1/L2 三层先验 + BR-01~12 用例表 + 失败决策树) "
                "+ SW/EVT_TEMPLATE.md §11 (EVT-8/BR-01) + SW/tools/ 4 件套 "
                "(boot_rescue_probe.py / flash_writer.py / flash_layout_check.py / s2_selftest.sh) "
                "② 自证实跑 `bash SW/tools/s2_selftest.sh` → **rc=0, 通过 10 / 失败 0**; "
                "P1~P4 全 [0数据] (严禁用通用示例冒充真值) "
                "③ ★**板端 S2 实测 0 次** (无板 + P1~P4 待原厂) —— 这部分**不随本单闭环** → 已拆出 **ISS-120** "
                "(owner=sw-lead, EVT 阶段 BR-01 门禁) 单独跟踪, 不许被本单的 verified 掩盖 "
                "④ 方案里抓出的 4 个版本块真 bug (A/B 槽 CRC 串台 / payloadCRC 误含 bootable / "
                "擦除态 0xFF 误判 / 长度 0xFFFF 误判非空) 已由交卷方当场修掉 ⇒ 判定 pass (方案层)"
            )
            it["note"] = (it.get("note") or "") + \
                f"\n★{STAMP} 项目总工亲核关单 (方案层): status fixed→verified; ★板端实测拆出 ISS-120 单独跟踪 (不掩盖 0 实测)"
            done.append("ISS-080 关单 fixed→verified (方案层) + 拆出 ISS-120")

        # ---------- ④ 新登记 ISS-120 ----------
        if "ISS-120" in by:
            done.append("ISS-120 跳过 (已存在)")
        else:
            issues.append({
                "id": "ISS-120",
                "title": "★S2 救砖链路板端实测 (量产一票否决项) —— 方案+自检已闭环 (ISS-080), 待 EVT 有板后真跑 (EVT-8/BR-01)",
                "severity": "high",
                "source_blocker": "ISS-080",
                "source_agent": "main",
                "desc": "ISS-080 交卷的是**方案** (P1~P4 参数位 + t1~t4 时序 + 3 条识别分支 + CB-01~09 + "
                        "BR-01~12 + 失败决策树), 板端实测 0 次。P1_BOOT_ENTER_SPEC / P2_DL_TOOL / "
                        "P3_USB_PHY / P4_BOOT_STORE 四个参数项全 [0数据] (需原厂回 boot 入口条件 / 下载工具链 / "
                        "USB boot PHY / boot storage BOM) ⇒ **没板没参数跑不了**。⇒ EVT 阶段有板 + 原厂参数到位后, "
                        "按 EVT-8/BR-01 实跑 CB-01~09 机械判据 + BR-01~12 用例, S2 连挂 2 次 → 升级 S3。量产放行前必须 close。",
                "owner": "sw-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-30",
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "verify_by": "main",
                "verify_result": None,
                "verify_date": None,
                "note": "2026-10-30 00:2x 项目总工从 ISS-080 关单时拆出 —— ★不许因为 ISS-080 verified 就当 S2 实测已过",
                "dispatched_at": None,
            })
            done.append("ISS-120 新登记 (S2 板端实测 / EVT BR-01 门禁)")

        # ---------- 原子写回 ----------
        before = os.path.getsize(LOG)
        text = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, text)
        after = os.path.getsize(LOG)
        print(f"✅ issue_log.yaml 已更新: {before} → {after} 字节 | 登记问题 {len(issues)} 条")
        for d in done:
            print("   -", d)
        fcntl.flock(lk, fcntl.LOCK_UN)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
