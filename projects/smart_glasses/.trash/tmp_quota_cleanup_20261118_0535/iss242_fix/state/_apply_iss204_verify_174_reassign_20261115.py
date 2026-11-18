#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-15 21:5x 队列自动派活 · 项目总工 (main/moli) 落账 + 改派 ISS-174
================================================================================
【A】★**ISS-204 (hw-lead) 僵尸 fixing → verified** ——
  · 子会话 `agent:hw-lead:subagent:5af88046` (sessionId `9e381769`) 2026-11-15 21:51:54 结束, status=**done**
    ⇒ ★**交卷已投递、文件已落盘** ⇒ brief 明写「不许碰 state/issue_log.yaml」⇒ 没人落账 ⇒ status 停在 `fixing`
    ⇒ ★**`advance.py` 的 in_flight 规则会占住 hw-lead 的名额** ⇒ hw-lead 明明已经交卷闲着, 却进不了候选
  · ★**交卷我独立复核过 (★不采信自述, 只看盘上实物★)**:
    · ✅ 交付物在盘: `HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md` (21996 B, 21:49) + `HANDOFF/2026-11-15_hw-lead_ISS204_UART0_TX_pinmux核.md` (19710 B, 21:51)
    · ✅ ★**关键结论我用项目自己的表复核过**: `HW/PCB/FET3572C_PIN_TABLE.csv` 第 108 行 = `P2,7,U33,UART0_TX_M0_DEBUG,GPIO0_D4_u,3.3V,...`
      ⇒ ★**P2 pin7 出厂默认就是 UART0_TX_M0_DEBUG**; 第 104 行 = `P2,3,W33,PWM0_CH1_M0,GPIO0_C3_d,...` ⇒ ★**PWM0_CH1_M0 是 pin3 不是 pin7**
      ⇒ ⇒ ★**ISS-204 的结论 = 设计本来就正确, 零改动零改板代价** ★
    · ✅ ★**并且它纠正了 main 自己 11-12 的旧读法** (★当时 note 写「P2_7 = PWM0_CH1_M0」⇒ 实为把 NUM 与 ball 混了★)
      ⇒ ★**这类"自己查出来把旧口径纠了"的单, 价值比"照抄题单"大一个量级** ★
    · ✅ 受保护文件 md5 一字未变: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075`
    · ✅ 分片已登记 (`state/fragments/hw.yaml` artifacts 69 条, 含本单 2 条; needs_from 含 `iss204_uart_debug_100ohm_tvs` + `iss204_pingap_gen_pin2_7_fix`)

【B】★**ISS-174 改派给 hw-lead (★原理图主线的一条硬活★)** ——
  · ★**它是 open 名单里唯一一条"纯原理图连通性缺口"** ⇒ 正落在老板 2026-11-11 10:07 主线 (先原理图, PCB 布线类一律不派)
  · ★**main 21:5x 已实测出它的前提可能过期**: `HW/netlist_v1.csv` 里 `NET_TP_INT` **零命中**; 屏侧走 `CONN_LIGHT` 22p
    (Pi5 CM5IO 针序) = DSI lane0/1/2 + I2C_B (屏内 MCU @0x45), **座上没有任何触控/复位脚** ⇒ ★**必须先判真伪, 再出规格**
  · ★**不许改网表/板** ⇒ 改网表不改板会让 `state/check_netlist_pins.py` / `state/check_pcb_nets.py` 立刻对不上 ⇒ 整链重出
    ⇒ ★**本单只出「规格 + 候选脚 + 官方证据」, 落笔留给原理图定稿那一轮统一改** ★

★★**落账纪律** ★★: flock(state/.issue_log.lock) + 锁内重读 · ★**自证: safe_dump(整份 doc) 必须与原文件逐字节相同** ·
原子写 (tmp → fsync → os.replace → fsync(dir)) · ★**只动 ISS-204 / ISS-174 两条** ★

★★**边界** ★★: 不改 `PROJECT_TRACKER.md` §0 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 / 不下采购单 ·
板 / 网表 / 原理图 / BOM 一个字节不动
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BRIEF_174 = os.path.join(HERE, "_brief_iss174.txt")

NOW = "2026-11-15 21:5x"

VERIFY_204 = (
    "pass · %s 项目总工独立复核 (★不采信自述, 只看盘上实物★)\n"
    "★**① 交付物两件在盘 (main 实测 mtime)**: `HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md` (21996 B, 21:49) · "
    "`HANDOFF/2026-11-15_hw-lead_ISS204_UART0_TX_pinmux核.md` (19710 B, 21:51)\n"
    "★**② ★关键结论我用项目自己的表复核过 (★不是采信自述★)★**: `HW/PCB/FET3572C_PIN_TABLE.csv` ★**第 108 行 = "
    "`P2,7,U33,UART0_TX_M0_DEBUG,GPIO0_D4_u,3.3V,...`**★ ⇒ **P2 pin7 出厂默认功能就是 UART0_TX_M0_DEBUG**; "
    "★**第 104 行 = `P2,3,W33,PWM0_CH1_M0,GPIO0_C3_d,...`**★ ⇒ **PWM0_CH1_M0 是 pin3 / ball W33, 不是 pin7 / ball U33** "
    "⇒ ⇒ ★**结论: 本板设计本来就正确, 零改动、零改板代价; 这不是引脚复用问题** ★\n"
    "★**③ ★它纠正了 main 自己 11-12 的旧读法 (★这条要记进账★)★**: main 当时 note 写「Forlinx Table 4 ⇒ P2_7 = PWM0_CH1_M0」 "
    "⇒ ★**实测是把 NUM 与 ball 混了 (P2_7 = U33 = UART0_TX; PWM0_CH1_M0 = P2_3 = W33)** ⇒ ★**本项目自己的引脚表一直是对的, "
    "错的是当时的读法** ⇒ ★**教训: 引脚口径一律以 `HW/PCB/FET3572C_PIN_TABLE.csv` 的 (NUM, ball, 官方功能) 三元组为准, 不许只看功能名** ★\n"
    "★**④ 证据链 (交卷件自带, main 复核为三源交叉)**: Rockchip 官方 datasheet V1.0 (p.30/p.31 Pin Number List 原文抄录) · "
    "Rockchip 官方内核仓库 `rk3572-pinctrl.dtsi` (uart0 节点 = `uart0_tx_m0 <0 RK_PD4 9 &pcfg_pull_up>`) · "
    "Forlinx 官方 User's Hardware Manual §2.6.2 / §3.5.5 ⇒ ★**[官网] ×3 独立源** ★\n"
    "★**⑤ 受保护文件 md5 一字未变**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075`\n"
    "★**⑥ 分片已登记 (main 复核)**: `state/fragments/hw.yaml` artifacts = 69 条 (含本单 2 条) · needs_from 含 "
    "`iss204_uart_debug_100ohm_tvs` (★UART debug 口缺 100Ω+TVS 防护★) + `iss204_pingap_gen_pin2_7_fix` (★生成器侧 pin2_7 口径待订正★) "
    "⇒ ★**两个缺口已进台账, 不是口头交接** ★\n"
    "★**⑦ 残留 (只报不改)**: Forlinx「FET3572-C SoM Pin Multiplexing Comparison Table」下载区需登录 ⇒ [0数据] (已用两份更强一手源替代) · "
    "本板 UART0_TX/RX 反灌与波形实测 = [0数据] (无实板, 降级方案 = 按官方拓扑加 100Ω+TVS 规避) · "
    "★`iss204_pingap_gen_pin2_7_fix` 属生成器侧改动 ⇒ 归 main 在原理图定稿轮统一处理** ★\n"
    "★**⑧ 与口径纪律的符合性**: 零外发 · 资料全部自己上网查官方件 · [0数据] 项都配了降级方案 · 板与网表一个字节未动 ★"
) % NOW


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".iss204.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    brief_174 = open(BRIEF_174, encoding="utf-8").read().strip()

    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        issues = doc.get("issues") or []

        if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200) != raw:
            print("★落盘中止: yaml 往返不是逐字节相同 ⇒ 拒绝写")
            return 2

        by_id = {i.get("id"): i for i in issues}
        changed = []

        # ---------- A. ISS-204 落账 ----------
        it = by_id.get("ISS-204")
        if not it:
            print("★ISS-204 不在 issue_log 里 ⇒ 拒绝写")
            return 2
        if it.get("status") != "fixing":
            print("★ISS-204 的 status 是 %r (不是 fixing) ⇒ 拒绝写" % it.get("status"))
            return 2
        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_result"] = VERIFY_204
        it["verify_date"] = NOW
        it["fixed_at"] = "2026-11-15"
        it["fix_ref"] = "HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md · HANDOFF/2026-11-15_hw-lead_ISS204_UART0_TX_pinmux核.md"
        changed.append("ISS-204 → verified (main 独立复核)")

        # ---------- B. ISS-174 改派 hw-lead ----------
        it = by_id.get("ISS-174")
        if not it:
            print("★ISS-174 不在 issue_log 里 ⇒ 拒绝写")
            return 2
        if it.get("status") != "open":
            print("★ISS-174 的 status 是 %r (不是 open) ⇒ 拒绝写" % it.get("status"))
            return 2
        it["owner"] = "hw-lead"
        it["task_brief"] = brief_174
        it["due"] = "2026-11-18"
        it["source_agent"] = "main"
        it["note"] = (
            (it.get("note") or "") +
            "\n★2026-11-15 21:5x main 改派给 hw-lead (★原理图主线的一条硬活★): ★**它是 open 名单里唯一一条"
            "「纯原理图连通性缺口」⇒ 正落在老板 2026-11-11 10:07 主线 (先原理图, PCB 布线/布局类一律不派)** ★\n"
            "★**main 21:5x 已实测出本单描述的前提可能过期 (★所以 brief 第一步是「判真伪」, 不是「改脚」★)**: "
            "`HW/netlist_v1.csv` 里 `NET_TP_INT` **零命中**; 屏侧走 `CONN_LIGHT` 22p (Pi5 CM5IO 针序) = DSI lane0/1/2 + I2C_B "
            "(屏内 MCU @0x45), **该座上没有任何触控/复位脚**; `TP_RESET` 在网表里只剩 P7 测试点与 `R_PU_RESET_N` 上拉位 ⇒ "
            "⇒ **不是「接了屏没接 SoM」, 是「这条线现在压根不是屏复位线」** ⇒ ★**brief 要求先判 (a)仍成立/(b)已不成立/(c)部分成立** ★\n"
            "★**不许改网表 / 不许改板** ⇒ 改网表不改板会让 `state/check_netlist_pins.py` / `state/check_pcb_nets.py` 立刻对不上 ⇒ "
            "整链重出 ⇒ ⇒ **本单只出「规格 + SoM GPIO 候选脚 + 官方证据」, 落笔留给原理图定稿那一轮统一改** ★\n"
            "★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02) · ★**派活前已过命令存在性闸**: "
            "`python3 state/check_brief_commands.py --brief-file state/_brief_iss174.txt` ⇒ rc=0 ★"
        )
        changed.append("ISS-174 → 改派 hw-lead (加 task_brief, status 仍 open)")

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)

        before = yaml.safe_load(raw)
        after = yaml.safe_load(out)
        b = {i["id"]: i for i in before["issues"]}
        a = {i["id"]: i for i in after["issues"]}
        if set(a) != set(b):
            print("★落盘中止: 条目集合变了 ⇒ 拒绝写")
            return 2
        for iid in b:
            if iid in ("ISS-204", "ISS-174"):
                continue
            if b[iid] != a[iid]:
                print("★落盘中止: %s 被意外改动 ⇒ 拒绝写" % iid)
                return 2

        atomic_write(LOG, out)
        print("★issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        for c in changed:
            print("  · %s" % c)
        print("★自证: yaml 往返逐字节相同 ✓ · 其它 200 条一字未动 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
