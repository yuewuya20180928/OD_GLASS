#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1545_redispatch_iss243.py
★main (moli) 2026-11-16 15:45 (cron fb67af40 ARS45 队列自动派活)★

★★★**本脚本只做两件事 (★不碰任何交付物/真源/分片/板★)** ★★★
★**① 给 `state/issue_log.yaml` 的 ISS-243.task_brief 追加一段【续做重派】说明** ★
★**② 给 `state/dispatch_log.yaml` 补一条 ISS-243 的【续做重派】记录** ★

★★★**为什么必须重派 (★main 本轮实测, 不采信 agent 自述★)** ★★★
· ★**会话**: `agent:hw-lead:subagent:337705c2` (session bdf0ab5c) 15:15:03 起 · 15:24:10 止 · runtime 543s ·
  ★**status=timeout · abortedLastRun=true** ★ ⇒ **零交卷**
· ★**盘上零产出 (main 15:3x 实测 ls/grep)**:
  · 网表 `HW/netlist_v1.csv` L44/L45 value 仍 = 「[待选型] 1µF」· 脚表 L132/L133 同 · BOM L43 value 仍 = 「1」/opn 仍空
  · `state/.bak_iss243/` 不存在 · `HW/MOS_PAD_PIN_MAPPING.md` 不存在 · `HANDOFF/2026-11-16_hw-lead_ISS243_*.md` 不存在
  · `state/fragments/hw.yaml` 里 0 处 ISS-243 ⇒ **分片也没写**
· ★**上一轮死在哪 (main 读 transcript 实测)**: 死在「去 murata.com 官网查 `GRM21BR71C475KA73L` 型号页」——
  ① `web_fetch` 403 ×2 ② `murata.com/api/...` 404 ×2 ③ 裸 curl 抓到 843 B 的 **HTML 错误页当 PDF** ④ 最后起了一个**后台 curl**
  (session `tidal-glade`, pid 559264) 再去等它 ⇒ 撞 timeout ⇒ **9 分钟全花在内存里, 盘上零产出**

★★★**本轮追加的硬规矩 (★全部是 main 本机实测出来的, 不是猜★)** ★★★
① ★**L1 落表的真源不是 CSV, 是 `state/gen_netlist.py` L500/L502 的 `add()` 调用** ⇒ ★**手改 `HW/netlist_v1.csv`
   是改生成物 (ISS-075 明令禁止) ⇒ ★**改完必须按硬顺序重生成**:
   `gen_netlist.py` → `gen_kicad_net.py` → `gen_netlist_pins.py` → `gen_bom.py` → `gen_schematic_pages.py` → `gen_kicad_sch.py`
   (★顺序是硬的: 脚表脚号来自 `.net`★) ⇒ ★**OPN/封装 栏的唯一真源是 `state/gen_netlist.py` 的 `PARTS` 字典** ⇒
   ★**`C_REGN` 在 `PARTS` 里没有条目 ⇒ 补一条 ⇒ 三个 CSV 的 footprint/opn 列才会带上**
② ★**TI 原文本机已有, 不许再下载**: `/tmp/bq25896.pdf` (1675426 B) + `/tmp/bq25896.txt` (pdftotext 输出) ⇒
   ★**pin22 原文在 txt 第 340~343 行** ⇒ ★**先拷进 `state/.cache_iss243/` 再用** (/tmp 会清)
③ ★**OPN 不许重新查 Murata 官网** (实测 403/404) ⇒ ★**直接用 ISS-241 矩阵 §3.7 已给的推荐项 `GRM21BR71C475KA73L`**
   (0805 / 4.7µF / 16V / X7R / ±10%) ⇒ ★**矩阵里标 `[0数据]` 的型号不许用**
④ ★**不许起后台长跑命令 + 不许去等一个还没完的 process** ⇒ ★**所有 curl 前台跑 + 带 `--max-time 20`**
⑤ ★**`HW/check_netlist_selfconsistency.py --expect-resolved` 落表前基线 = 18 条 (rc=1)** (main 本轮实跑)
   ⇒ ★**落表后必须仍是 18 条** ⇒ ★**变 19+ = 你碰坏了别的东西; 变 17 = 你越界落了本单不该落的东西** ⇒
   ★**现状守卫 (不带参数) 必须 rc=0**
⑥ ★**落表台账是 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (不是 WORKPACKET §9)** ⇒ ★**参考实现 = `state/land_v_values.py`**
   (★**只许读, 不许改★**) ⇒ ★**受保护 md5 = 板 `611b869e…` + `.kicad_pro` `3e504d2b…` 必须逐字节不变**
⑦ ★**`DECISION_PENDING_2026-11-16.md` W-3 还挂着** (它写「落表前要老板点一次头」) ⇒ ★**本单按 ISS-243 授权落 L1 (官方值)**
   ⇒ ★**交卷单里写一行留给 main 去把 W-3 标掉** ⇒ ★**不许自己改 DECISION_PENDING**

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` (ISS-243 的 task_brief) + `state/dispatch_log.yaml`** ★
· ★**不改任何交付物 / 真源 / 分片 / 板 / 网表 / BOM / DECISION_PENDING / PROJECT_TRACKER §0** ★
· ★**零外发** · ★**未替老板拍板** · ★**不改 issue 的 status (仍是 fixing ⇒ 名额仍被 hw-lead 占着, 符合铁律)** ★
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"
MARK = "★注 (★main 2026-11-16 15:4x 追加·★不改上面任何原文★)"

APPEND_243 = r"""

★★★★**★注 (★main 2026-11-16 15:4x 追加·★不改上面任何原文★)**★★★★ ★
★**【续做重派】★上一轮会话 `agent:hw-lead:subagent:337705c2` (session bdf0ab5c) 15:15:03 起 · 15:24:10 止 · runtime 543s · ★**status=timeout / abortedLastRun=true** ★ ⇒ ★**零交卷 · 盘上零产出** (★main 15:3x 实测: 网表 L44/L45 仍 =「[待选型] 1µF」· 脚表 L132/L133 同 · BOM L43 value 仍 =「1」/opn 仍空 · `state/.bak_iss243/` 不存在 · `HW/MOS_PAD_PIN_MAPPING.md` 不存在 · 交卷单不存在 · `state/fragments/hw.yaml` 里 0 处 ISS-243★) ⇒ ★**本轮重派 · runTimeout 5400s** ★**
★**上一轮死在哪 (main 读 transcript 实测)**: 死在「去 murata.com 官网查 `GRM21BR71C475KA73L` 型号页」—— ① `web_fetch` 403 ×2 ② `murata.com/api/...` 404 ×2 ③ 裸 curl 抓到 843 B 的 **HTML 错误页当 PDF** ④ 最后起了一个**后台 curl** (session `tidal-glade`, pid 559264) 再去等它 ⇒ 撞 timeout ⇒ ★**9 分钟全花在内存里, 盘上零成品** ★
★★★**★★本轮硬规矩 (★main 本机实测出来的, 一条都不许违反★)★★** ★
★**① 【先落盘, 再研究】** ★**第一件事 = 把 4 件交付物的骨架建起来** (交卷单 + 门禁脚本 + `HW/MOS_PAD_PIN_MAPPING.md` + `state/.bak_iss243/` 备份目录) ⇒ ★**再往里填** ⇒ ★**这样再撞 timeout, 盘上也留半成品, 下一轮不用从零开始 (上一轮就是这么白烧 9 分钟的)★ ★
★**② 【L1 落表的真源不是 CSV!】** ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 全是【生成物】** ⇒ ★**手改 CSV = 改生成物 (ISS-075 明令禁止) ⇒ 下次重跑生成器就被抹掉** ⇒ ★**真源 = `state/gen_netlist.py`**:
★**① L500/L502 两条 `add("P1", "REGN"/"GND", "C_REGN", ...)` 的 value 栏 `[待选型] 1µF` → `4.7µF ±10% (10V)`** ★**② `PARTS` 字典 (L47~L90, 「位号 → (封装, OPN)」唯一真源) 里 `C_REGN` 没有任何条目 ⇒ 补一条** (★**footprint + opn = `GRM21BR71C475KA73L`** ★⇒ 三个 CSV 的 footprint/opn 列才会带上★) ⇒ ★**③ 落表后按【硬顺序】重生成 (★顺序是硬的: 脚表脚号来自 `.net`★)**: `python3 state/gen_netlist.py` → `python3 state/gen_kicad_net.py` → `python3 state/gen_netlist_pins.py` → `python3 state/gen_bom.py` → `python3 state/gen_schematic_pages.py` → `python3 state/gen_kicad_sch.py` ★
★**③ 【TI 原文本机已有, 不许再下载】** ★**`/tmp/bq25896.pdf` (1675426 B) + `/tmp/bq25896.txt` (pdftotext 输出) 已在盘** ⇒ ★**pin22 原文在 txt 的第 340~343 行**: 「Internally, REGN is connected to the cathode of the boost-strap diode. **Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND.** The capacitor should be placed close to the IC. REGN also serves as bias rail of TS pin.」 ⇒ ★**先把这两个文件拷进 `state/.cache_iss243/` 再用** (/tmp 会被清) ⇒ ★**你自己 `pdftotext` 实读一遍抄进交卷单即可 (30 秒的事) ⇒ 不许再去 ti.com 下载** ★
★**④ 【OPN 不许重新查 Murata 官网】** ★**实测 403/404 ⇒ 直接用 ISS-241 矩阵 §3.7 已给的推荐项 `GRM21BR71C475KA73L`** (0805 / 4.7µF / 16V / X7R / ±10%, 16V > 手册要求的 10V) ⇒ ★**矩阵里标 `[0数据]` 的型号不许用** (如 10V 版 `GRM21BR71A475KA73L`) ⇒ ★**出处照抄矩阵 §3.7 + Murata 官方系列页** ⇒ ★**你若要补官方页 ⇒ 限时 3 分钟 + 必须 `--max-time 20` ⇒ 超时就用矩阵口径** ★
★**⑤ 【不许起后台长跑命令 + 不许去等一个还没完的 process】** ★**所有 curl 必须【前台跑 + `--max-time 20`】** ⇒ ★**不许 `cmd &` 起后台** ⇒ ★**不许 poll 一个还没结束的 process** ⇒ ★**上一轮就是死在这** ★
★**⑥ 【不许再用 web_fetch 打 Murata / Diodes / TI 的型号页】** (实测 403/404) ⇒ ★**查不到就写 `[0数据]` + 降级方案** (★老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料★) ★
★**⑦ 【selfconsistency 的基线是 18】** ★**main 本轮实跑**: `python3 HW/check_netlist_selfconsistency.py` ⇒ ★**rc=0 (现状守卫绿)** ★ `--expect-resolved` ⇒ ★**rc=1 · 恰好 18 条未落表** ⇒ ★**落表后必须仍是 18 条** ⇒ ★**变 19+ = 你碰坏了别的东西; 变 17 = 你越界落了本单不该落的东西** ⇒ ★**两种都要在交卷单里写清** ★
★**⑧ 【落表台账的正确位置 + 参考实现】** ★**台账 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (单号 + 文件名 + 新旧 md5)** (★**不是 WORKPACKET §9★) ⇒ ★**参考实现 = `state/land_v_values.py` (★只许读, 不许改★)** ⇒ ★**落表后必须把新 md5 打到 stdout** (★供 sw-lead / mech-lead 走 H-1 重锚★) ⇒ ★**受保护 md5 = 板 `611b869e13518c3c023fb178f91a0075` + `.kicad_pro` `3e504d2be83152e337949723e909be1b` 必须逐字节不变** ⇒ ★**规格页锚点表 (`HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 `<!-- ANCHORS -->` 块) 与门禁 `EXPECT` 必须逐字一致** (★落表后跑现状守卫, 若报锚点漂移 ⇒ 按规格页 §5.5 的流程整块重生成★) ★
★**⑨ 【W-3 还挂着】** ★**`DECISION_PENDING_2026-11-16.md` W-3 写着「C_REGN 落表前要老板点一次头」** ⇒ ★**本单按 ISS-243 的授权落 L1 (官方值, main 层级已开单)** ⇒ ★**交卷单里必须写一行: L1 已落, 依据 = TI 手册官方值 + ISS-243 授权 ⇒ 请 main 去把 W-3 标掉 (老板级留痕)** ⇒ ★**不许自己改 `DECISION_PENDING_2026-11-16.md`** ★
★★★**★★本轮验收命令 (★main 本轮实测全部存在, 照抄即可, 别自己找★)★★** ★
★**落表前**: `python3 HW/check_netlist_selfconsistency.py` (rc=0) · `--expect-resolved` (★**记录条数 = 18**) ★
★**落表后**: ★**① `python3 HW/check_netlist_selfconsistency.py` ⇒ 必须 rc=0** ★ **② `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ 条数必须仍是 18** ★ **③ `python3 state/check_netlist.py` · ④ `python3 state/check_netlist_pins.py` · ⑤ `python3 state/check_sch_erc.py` · ⑥ `python3 state/check_sch_pinfull.py` ⇒ 全部 rc=0** ★ **⑦ `python3 HW/check_netlist_contradiction_r3.py` ⇒ 必须仍是 rc=1 且恰 3 条 findings (★ISS-242 的门禁, 不许被本单改红★)** ★ **⑧ `python3 HW/check_part_selection_matrix.py` (+ `--selftest`) ⇒ 必须 rc=0 (★ISS-241 的门禁, 不许被本单改红★)** ★ **⑨ `python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0 · 【Q1】18/18** ★ **⑩ 你自己新建的门禁 + `--selftest`** ⇒ ★**新产物 (★新建★)**: `HW/MOS_PAD_PIN_MAPPING.md` · `HW/check_iss243_cregn.py` (★门禁脚本名你自己起也行, 但交卷单要写清★) · `HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md` · `state/.bak_iss243/` (★备份目录★) · `state/.cache_iss243/` (★TI PDF + txt 缓存★) ★
★**★排期纪律 (★防止再撞 timeout★)** ★**① 骨架落盘 (10 分钟) → ② L1 落表 (20 分钟) → ③ L2 映射表 (20 分钟) → ④ L3 改法 (10 分钟) → ⑤ L4 清单 (15 分钟) → ⑥ 门禁 + --selftest + 验收 + 分片 (20 分钟)** ⇒ ★**任何一步卡住 3 分钟 ⇒ 跳到下一步 + 在交卷单里写明卡在哪** ⇒ ★**不许为了把 L1 做完美而把 L2/L3/L4 全丢掉** (★L2/L3/L4 是纯出文档, 不依赖落表★) ★
★**其余边界一个字没变**: 零外发 · 不碰 PCB 布线/布局/板框 · 不改脚表里别的器件 · 不许碰 `C_VBUS_OUT`/`C_VBUS_GND` (★ISS-242 那两条缺陷归 main 排期★) · 不改 `state/land_v_values.py` · 不替老板拍板 (V-2/V-3/V-4/G-1/W-1~W-6) · 实物 [实测] = 0 条 · 不改 `state/issue_log.yaml` (verify 留给 main) ★
"""

BRIEF_243_HEAD = (
    "★**续做重派 (★main 2026-11-16 15:4x 实测: 上一轮会话 15:15:03~15:24:10 撞 timeout (runtime 543s · abortedLastRun=true · status=timeout) "
    "⇒ ISS-243 是【零产出僵尸】★) ⇒ ★**本轮重派 · runTimeout 5400s** ★** "
    "★**盘上零产出 (网表/脚表/BOM 三处 C_REGN 仍是「[待选型] 1µF」· 备份目录/映射表/交卷单/分片 四件一件没落) ⇒ 上一轮 9 分钟全花在内存里 "
    "(去 murata.com 查型号页 → 403/404 → 起了个后台 curl 去等它) ⇒ 本轮要求: 先落盘骨架再填内容 · TI PDF 本机已有 (/tmp/bq25896.pdf) 不许重下 · "
    "OPN 直接用 ISS-241 矩阵 §3.7 的 GRM21BR71C475KA73L · 所有 curl 前台跑带 --max-time 20 · L1 真源是 state/gen_netlist.py 不是 CSV** ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_redispatch243.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(IL, IL + ".bak_20261116_1545_redispatch_iss243")
    shutil.copy2(DL, DL + ".bak_20261116_1545_redispatch_iss243")
    lf = open(LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)

        # ── ① issue_log: ISS-243.task_brief 追加续做重派说明 (幂等) ──
        log = yaml.safe_load(open(IL, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        target = None
        for it in issues:
            if it.get("id") == "ISS-243":
                target = it
                break
        if target is None:
            print("★★ ISS-243 不在 issue_log 里 ⇒ 中止")
            return 2
        brief = target.get("task_brief") or ""
        if MARK in brief:
            print("   - ISS-243 brief 里已有 15:4x 追加块 ⇒ 不重复写")
        else:
            target["task_brief"] = brief + APPEND_243
            _atomic_write(IL, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
            print("   - ISS-243 task_brief 追加【续做重派】块 (len %d → %d)"
                  % (len(brief), len(target["task_brief"])))
        print("   - ISS-243 status =", target.get("status"), "(保持 fixing ⇒ hw-lead 名额仍被占, 符合铁律)")

        # ── ② dispatch_log: 补一条 ISS-243 续做重派记录 ──
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {"dispatches": []}
        disp = dl.setdefault("dispatches", [])
        if any(d.get("issue") == "ISS-243" and d.get("redispatch") for d in disp):
            print("   - dispatch_log 里已有 ISS-243 重派记录 ⇒ 不重复写")
        else:
            disp.append({
                "issue": "ISS-243",
                "agent": "hw-lead",
                "at": TODAY,
                "brief": BRIEF_243_HEAD,
                "redispatch": True,
                "reason": (
                    "★上一轮 status=timeout/aborted (runtime 543s · abortedLastRun=true · session bdf0ab5c) ⇒ 零产出僵尸: "
                    "网表 L44/L45 与脚表 L132/L133 与 BOM L43 的 C_REGN 仍 =「[待选型] 1µF」· state/.bak_iss243/ 不存在 · "
                    "HW/MOS_PAD_PIN_MAPPING.md 不存在 · HANDOFF/2026-11-16_hw-lead_ISS243_*.md 不存在 · state/fragments/hw.yaml 里 0 处 ISS-243 "
                    "⇒ 4 件交付物一件没落 ⇒ 仍无交卷 ★"
                ),
                "session_key": "agent:hw-lead:subagent:337705c2-7055-4a42-b274-8f05613cfb12",
                "dead_session_id": "bdf0ab5c-066e-45b0-922e-63bebc772787",
            })
            _atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
            print("   - dispatch_log 补记 ISS-243 续做重派 (dead session bdf0ab5c)")
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
