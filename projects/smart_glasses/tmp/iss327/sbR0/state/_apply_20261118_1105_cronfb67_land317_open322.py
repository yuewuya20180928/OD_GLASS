#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-317 落地 (fixing → verified) + 新开 ISS-322 (hw-lead · S8 布线归零作业包)
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 11:0x ★

★**为什么有本脚本** (★main 11:0x 本机实读★):
  · 子会话 `agent:hw-lead:subagent:b1b07ded-...` 10:38:00 起 · 11:00:2x 跑完 (status=done)
    ⇒ ★**这一轮 3 条在飞里唯一交卷完整的** ★ (mech-lead ISS-320 / sw-lead ISS-321 仍在跑)
  · main 11:0x **独立复核** (不抄 agent 报告):
      - 交付物 `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` = 90,132 B / **959 行** · §0~§6 七节全填实
      - 交卷页 `HANDOFF/2026-11-18_hw-lead_ISS317_S1位号改名可执行清单.md` = 25,535 B / **281 行** · B0~B6 齐全
      - 占位符扫描 = 0 (两份文档都是 0)
      - `logs/iss317/` = **32 件** (19 个场景原始输出 + 脚本 + v2 清单)
      - 分片 `state/fragments/hw.yaml` 里 `ISS-317` 命中 **3** 次 (已写)
      - ★零写板双证: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未变
    ⇒ ★**交卷判据 (交卷页 B0~B6 + 分片已写 + 闸读数归因清楚) 三件齐 ⇒ 可落 verified** ★

★**为什么 hw-lead 现在能接新单**: ISS-317 落 verified ⇒ hw-lead 名下无 fixing ⇒
  ★**新开 ISS-322 直接落 fixing ⇒ 下一轮 in_flight 规则仍会跳过 hw-lead ⇒ 无 open 窗口 ⇒ 不与兄弟 job 775d9893 撞车** ★
"""
from __future__ import annotations

import fcntl
import os
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"

BRIEF_322 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-322_hw_s8_routing_to_zero_workpack.md"),
    encoding="utf-8").read()

TITLE_322 = (
    "★★[主线内·HW 侧·布线归零作业包 + 死因逐条登记类·内部活] "
    "★★【「板只改一次」那一趟的 S8 (布线归零 unconnected 45 → 0): 45 条逐条死因登记 + "
    "23 条高速 DSI/CSI 腿的几何可布性判定 + 逐条修法/落表批次/验收命令作业包】★★ "
    "⇒ ★**纯分析 / 作业包 / 判据设计类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM/原理图真源** ★"
)

NOTE_322 = (
    "★**2026-11-18 11:0x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 "
    "(status 直接落 fixing ⇒ 下一轮 in_flight 规则会跳过 hw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
    "★**开单依据 (★main 11:0x 本机实读·不抄任何 agent 报告★)**: "
    "★**① 老板 2026-11-17 00:43: 「接下来的目标是绘制 PCB 图」⇒ 布线/布局类 ISS 现在【可派】** ★ "
    "★**② 「板只改一次」⇒ 真动板那一趟必须一次做完 (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + "
    "布线 45→0 + Gerber/投产包重出·同一趟·背靠背) ⇒ 必须先把「布线那一段」做成可执行的作业包** ★ "
    "★**③ main 11:0x 实跑 `python3 state/check_pcb_drc.py` ⇒ DRC violations = 0 · unconnected items = **45** "
    "(骨架阶段所以 C4 不是红)** ★ "
    "★**④ `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S8 自称是作业包里唯一一个「可能整趟做完仍然投不了板」的步** ★ "
    "★**⑤ §3-S8 里两个数打架: 「45 条里 **23** 条是高速 DSI/CSI 腿」 vs 「官方板 (160×100/8L) 这 **13** 条 DSI 腿"
    "自己一根都没布通」 ⇒ 23 与 13 必查清** ★ "
    "★**⑥ `state/UNC_TARGET_MAP.md` 的基线是 2026-11-11 的 (unc 29 条 / 22 个网名) ⇒ 与现役板 45 对不上 ⇒ 基线过期** ★ "
    "★**⑦ MEMORY 铁律: v44 / v46 / v47 / v48 四个臂全部打死同样三条差分腿 (`DSI_D0_CK` · `DSI_D0_CK_SRC` · "
    "`DSI_D0_D1`) ⇒ 根因在布局不在路由算法 ⇒ S8 大概率不是「调路由参数」能解决的** ★ "
    "★**⑧ §3-S8 已登记的 5 条死因 (A1 BAT_DET 终点未定义 / W-1 W-2 ESD 未拍 ⇒ 器件钉位定不下来 / "
    "W-4 `Q_PG.3` 极性未定 / `D_LED_G` 物理位置 (LED_G_D 走线 93.49 mm) / `FSIN_OUT` 3.01 mm 布不通) "
    "⇒ 只覆盖 22 条里的 5 条 ⇒ 剩 40 条至今无人登记** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-322_hw_s8_routing_to_zero_workpack.md` "
    "(9,035 B · `check_brief_commands.py --brief-file` rc=0) ★ "
    "★**边界**: 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM/原理图真源 · 零改既有文档正文 · "
    "沙盒只写 `tmp/iss322/` · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料·"
    "需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案★) · 不替老板拍板 · 不自签 issue_log ★"
)

VERIFY_317 = (
    "✅ verified (★main 2026-11-18 11:0x 独立复核·不抄 agent 报告★) ⇒ "
    "★**交卷物在盘**: `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` (90,132 B · **959 行** · §0~§6 七节全填实 · "
    "占位符扫描 0) + `HANDOFF/2026-11-18_hw-lead_ISS317_S1位号改名可执行清单.md` (25,535 B · **281 行** · B0~B6 齐全 · "
    "占位符扫描 0) + `logs/iss317/` (**32 件**: 19 个场景原始输出 + 生成器/沙盒脚本 + v2 清单) + "
    "`state/fragments/hw.yaml` (★`ISS-317` 命中 **3** 次·已写·3 artifacts + 1 need + 3 claims★) ★ "
    "⇒ ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` "
    "交卷前后逐字节不变 ★ "
    "⇒ ★**子会话本轮 10:38:00 起 · 11:00:2x 跑完 (status=done) ⇒ 有 label 的子会话活过父 run 结束 (本轮 3 条里 1/1) ★ "
    "★**交卷页自己声明的未完项如实留账 (不装完成)**: ① 三件待拍 (★改名走【五侧同口径】还是【板侧单改】· "
    "NC 白名单走 甲/乙/丙-② · 落表排期日期★· need key `s1_ref_rename_caliber_20261118` ⇒ **归 main + 老板**, "
    "本单不代拍) ② 「五侧同口径」实为**五侧**不是三侧 (218 行表里 186 个要改 · 板侧只动 156 个) ⇒ "
    "★**本单自己纠正了 ISS-314/ISS-317 的「三侧」措辞** ★ "
    "★**闸读数归因已做实**: 交卷前 `gate_check.py` rc=1, ★**唯一红项 = 「ISS-318 SW 侧位号引用可达性闸」· "
    "18 条真隐患全部来自 `SW/ONETRIP_SW_RENAME_SAFETY.md` (★sw-lead 10:47 写的·SW 域·与本单无关★) · "
    "决定性试验: 挪走那个 SW 文件 ⇒ 该闸 rc=0 绿 ⇒ 该闸输入面不含本单任何文件 ⇒ ★**不是本单的红** ★ "
    "⇒ ★**主线的 `gate_check.py` 此刻仍是 rc=1, 红项属 SW 域 (sw-lead 的 ISS-321 在飞中) ⇒ 下一轮要盯它落** ★"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        # ★锁内重读 (★不许用锁外读到的旧内容写回★)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []

        # ---------- ① ISS-317 → verified ----------
        i317 = idx.get("ISS-317")
        if i317 and i317.get("status") != "verified":
            i317["status"] = "verified"
            i317["verify_date"] = NOW
            i317["verify_result"] = VERIFY_317
            i317["note"] = (i317.get("note") or "") + (
                f"\n★**{NOW} 11:0x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
                "★**独立复核**: 交付物 959 行 §0~§6 实填 + 交卷页 281 行 B0~B6 + 占位符 0 + logs/iss317 32 件 + "
                "分片命中 3 + 板 md5/mtime 逐字节不变 ★ "
                "★**未完项如实留账**: 三件待拍 (need `s1_ref_rename_caliber_20261118`) 归 main + 老板, 不代拍 ★")
            applied.append("ISS-317 verified")
        elif i317:
            applied.append("ISS-317 已是 verified (跳过)")

        # ---------- ② 新开 ISS-322 (status 直接落 fixing) ----------
        if "ISS-322" not in idx:
            new = {
                "id": "ISS-322",
                "title": TITLE_322,
                "owner": "hw-lead",
                "status": "fixing",
                "severity": "high",
                "reporter": "main",
                "raised": NOW,
                "due": "2026-11-19",
                "created_at": NOW,
                "dispatched_at": NOW,
                "verify_by": "main",
                "source_blocker": "ISS-265",
                "task_brief": BRIEF_322,
                "note": NOTE_322,
                "need_keys": [
                    "iss322_s8_unc45_deadcause_registry",
                    "iss322_s8_dsi_csi_geometric_routability_verdict",
                    "iss322_s8_pending_decisions",
                ],
            }
            issues.append(new)
            applied.append("ISS-322 开单 (status=fixing ⇒ 已派)")
        else:
            applied.append("ISS-322 已存在 (跳过)")

        # ---------- ③ 落盘 issue_log ----------
        hdr = log.get("meta")
        out = dict(log)
        out["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        # ---------- ④ dispatch_log ----------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == "ISS-322" for d in disp):
            disp.append({
                "issue": "ISS-322",
                "agent": "hw-lead",
                "at": NOW,
                "brief": NOTE_322,
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 11:0x · "
                        "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
            })
            dl["dispatches"] = disp
            atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
            applied.append("dispatch_log 追加 ISS-322")

        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
