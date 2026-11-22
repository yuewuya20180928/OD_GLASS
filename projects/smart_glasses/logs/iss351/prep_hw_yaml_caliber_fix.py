#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-351 · hw-lead · 存储轴旧口径清账 · ★分片改写中间件生成器★

★**纪律**:
  - ★**零 open(p,"w") 手写 hw.yaml** ★ ⇒ 本脚本只【读】hw.yaml + 【写】3 份 JSON 中间件
    ⇒ 真正落盘一律走 `python3 state/frag_write.py --agent hw-lead --set-json <file> --set-field <field>`
  - ★**零写板** · ★**零落表** (不碰网表/脚表/BOM/原理图/闸脚本/闸判定逻辑) ★
  - ★**零新增拍板项** ⇒ 只改口径措辞, 不改任何 to/due/since/severity 等裁定性字段 ★

本单改 4 个条目 (任务书 §1 定点 1 条 + §2 同型残留 3 条):
  A1 answers[2]  vendor_q19_boot_storage   ← §1 定点改
  A2 answers[13] fw_boot_storage_bom       ← §2 命中 (SPI-NOR + 容量数字 + 板宽 12→15mm)
  N1 needs_from[5] q3_storage_and_audio    ← §2 命中 (SPI-NOR + 容量数字 + 板宽12->15mm)
  R1 risks[2]     R-hw-boot-storage        ← §2 命中 (SPI-NOR + 板宽 12→15mm)

其余条目逐字不动 (脚本自检: 逐条 sha256 比对)。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import shutil
import sys

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FRAG = os.path.join(PROJ, "state", "fragments", "hw.yaml")
LOGD = os.path.join(PROJ, "logs", "iss351")


# ---------------------------------------------------------------- 新措辞
# A1 —— §1 定点条目
A1_OLD_HEAD = "已并入原厂邮件问题清单第7问(内置boot storage? 容量?); 当前按无内置boot storage设计: 外挂 SPI-NOR 16-64MB, 吃镜脚空间, 板宽可能 12->15mm; 请并入第一轮跟进邮件"
A1_NEW = (
    "★【ISS-351 存储轴旧口径清账 · 2026-11-23 · hw-lead】★ ★**本条已按 ISS-346 / ISS-350 机器判决改成【分档】口径; "
    "原措辞整条作废 (三处: 容量区间旧值 / 板宽归属错位 / 外发类指令)**★ "
    "① 容量: ★**外挂 SPI-NOR ≥128 MiB (1 Gbit) 起**★ —— 依据: "
    "[实测] 网表 `HW/netlist_v1.csv` L209 (J_BOOT1 pin5) note 逐字「★V1.1: 容量下限已由 SW 总工锁死 (ISS-080): "
    "rootfs ≤30MB · flash ≥128MB (64MB SPI-NOR 装不下)」; "
    "[官网] ★**Winbond 料号里的数字是 Mbit 不是 MB**★ —— `W25Q128JV` = 128 Mbit = **16 MB** (V=2.7~3.6V) "
    "⇒ ★**`W25Q64` = 64 Mbit = 8 MB, 不可当成 64 MB**★; "
    "[官网] Winbond 官方 QSPI NOR **3V** 产品线 `W25Q-JV` 16Mb~2Gb / `W25Q-RV` 4Mb~2Gb ⇒ ★**1 Gbit 与 2 Gbit 两档都在官方产品线内**★, "
    "且 2.7~3.6V 与板上 `VDD_3V3_IO` 电源域匹配 ⇒ 128 MiB 档买得到。 "
    "② 板宽: ★**板宽 12→15 mm 只在【eMMC 档】成立**★ —— [官网] eMMC 153-ball TFBGA **11.5 × 13.0 × 1.2 mm** "
    "(Micron `MTFC8GACAENS` 8GB) ⇒ 11.5 mm 宽的 BGA 放不进 12 mm 宽的板 ⇒ "
    "★**外挂 SPI-NOR 档 = 板侧零动作 · 不改板宽 · 不重出板**★ —— 依据 [实测]: "
    "板面 `J_BOOT1` 焊盘位已在板 (6 pad @126.3 58 · `HW/PCB/demo_mainboard.kicad_pcb` L3144) + "
    "网表 L202/L204/L206/L208 4 条 0Ω 串阻位 `R_SER_SPI_SCLK/CSn/MOSI/MISO` → `J_BOOT1 pin1..pin4` 标「必装」+ "
    "`HW/BOM_v1.csv` L140~L143 同为「必装」+ 网表 note 逐字「只留焊盘位 + 串阻位, **不画存储芯片**」 ⇒ "
    "★**主板上焊存储芯片这条路已被网表否掉**★ ⇒ 只有 eMMC 档才要改板框 / 改网表 / 板 md5 变。 "
    "③ rootfs 真值仍 [0数据] ⇒ ★**降级方案 = 可判区间**: `rootfs ∈ [7.969 MiB, 199.969 MiB]` 内每档结论都成立 "
    "(ISS-346 每列 rootfs 上限机器自证: 64MB NOR 7.969 / 128MB NOR 71.969 / 256MB NOR 199.969 MiB; "
    "model 槽缩到实测下限 11 MiB 再各 +8 MiB) ⇒ ★**真值落在哪一格就按那一格办, 不存在「等数据出来再判」的状态**★。 "
    "④ ★**外发类指令一律作废**★ (老板 2026-11-11 19:31 + 2026-11-12 02:02 起不再发信) ⇒ "
    "★**本仓一律: 缺口自己网上查 + 标证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据]) + 查不到就写降级方案 "
    "⇒ `state/outbox` 里的草稿一律不发**★。 "
    "★**本条不新增任何拍板项**★ (Q3 怎么拍仍由老板拍, 本条只清口径)。"
)
A1_NEW_REF = (
    "ISS-351 交卷页 HANDOFF/2026-11-23_hw-lead_ISS351_存储轴旧口径清账.md · "
    "SW/STORAGE_CAPACITY_MATRIX.md · HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md · "
    "HANDOFF/2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md · "
    "state/fragments/pm.yaml#iss346_q3_storage_tier_verdict_20261123 · "
    "HW/netlist_v1.csv L202/L204/L206/L208/L209/L210 · HW/BOM_v1.csv L69/L140~L143 · "
    "HW/PCB/demo_mainboard.kicad_pcb L3144"
)

# A2 —— §2 命中: answers[13] fw_boot_storage_bom
A2_NEW = (
    "64MB SPI-NOR 装不下 (分区表 90MB) ⇒ 必须 ≥128MB。 "
    "★**【ISS-351 口径清账 · 2026-11-23 · hw-lead】本条原结论「路线选 eMMC 5.1 / ePoP (不是 NOR)」"
    "已由 ISS-346 / ISS-350 分档口径取代 · 本条保留作历史留档 · 结论不再引用**★ ⇒ 现行口径 = ★**按存储档分档**: "
    "① 只 ADB push 档 (demo) ⇒ 板侧零动作 ⇒ 不占板那一趟; "
    "② 外挂 SPI-NOR 档 (≥128 MiB / 1 Gbit 起 · ISS-080 已锁死) ⇒ 走 `J_BOOT1` 焊盘位 (6 pad 已在板 @126.3,58) + "
    "4 条 0Ω 串阻位必装 ⇒ ★**板侧零动作 · 不改板宽 · 不重出板**★ ⇒ 台架板档与产品板档都不卡; "
    "③ eMMC 档 ⇒ 板宽 12→15 mm ⇒ 台架板档 `B160x100` (160 mm 宽) 板面代价 ≈ 0 ⇒ 不卡 (时限型降为建议型) ⇒ "
    "★**只有产品板档 (F30A 60×30 / P60x15) 才卡 (时限型)**★。 "
    "★量产眼镜印证 (历史留档): 小米 AI 眼镜用 Kingston **ePoP** 存储 (52audio 拆解) ⇒ 方向一致 "
    "(★**eMMC / ePoP 档的可行性印证, 不等于「只能走 eMMC」**★)。 "
    "ARS45 侧仍按『无内置 boot storage』设计 (外挂), 脚号 TBD-06/11。 "
    "★板宽已放宽到 30mm ⇒ 挂 eMMC 的面积压力解除 (旧账: 12→15mm 要 +25% —— ★**该 12→15mm 只属 eMMC 档**★)。 "
    "★rootfs 真值仍 [0数据] ⇒ 降级方案 = 可判区间 `rootfs ∈ [7.969 MiB, 199.969 MiB]` 内结论都成立 "
    "(ISS-346 每列上限机器自证) ⇒ 不存在「等数据出来再判」的状态。"
)

# N1 —— §2 命中: needs_from[5] q3_storage_and_audio 的 item
N1_OLD = "外挂 SPI-NOR ≥128 MiB (1 Gbit) 起, 板宽12->15mm"
N1_NEW = (
    "外挂 SPI-NOR ≥128 MiB (1 Gbit) 起 —— ★**该档板侧零动作 · 不改板宽 · 不重出板**★; "
    "★**板宽 12→15 mm 只在【eMMC 档】成立**★"
)

# R1 —— §2 命中: risks[2] R-hw-boot-storage 的 text
R1_OLD = "若无内置 boot storage → 需外挂 SPI-NOR/eMMC (吃 PCB 面积, 板宽 12→15mm), 投板前必须 close"
R1_NEW = (
    "若无内置 boot storage ⇒ ★**按存储档分档 (ISS-346 / ISS-350 机器判决 · 2026-11-23 订正)**★: "
    "① 只 ADB push 档 (demo) ⇒ 板侧零动作 ⇒ 不占板那一趟; "
    "② 外挂 SPI-NOR 档 (≥128 MiB / 1 Gbit 起) ⇒ 走 `J_BOOT1` 焊盘位 (6 pad 已在板 @126.3,58) + 4 条 0Ω 串阻位必装 ⇒ "
    "★**板侧零动作 · 不改板宽 · 不重出板**★ ⇒ 台架板档与产品板档都不卡; "
    "③ eMMC 档 ⇒ 板宽 12→15 mm ⇒ 台架板档 `B160x100` (160 mm 宽) 板面代价 ≈ 0 ⇒ 不卡 (时限型降为建议型) ⇒ "
    "★**只有产品板档 (F30A 60×30 / P60x15) 才卡 (时限型)**★ ⇒ "
    "★**原措辞「(吃 PCB 面积, 板宽 12→15mm), 投板前必须 close」已由 ISS-346 / ISS-350 分档口径取代 · "
    "本条保留作历史留档 · 结论不再引用**★"
)


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def find_one(lst, key, field="key"):
    hits = [i for i, it in enumerate(lst) if isinstance(it, dict) and it.get(field) == key]
    if len(hits) != 1:
        raise SystemExit("[X] %s 命中 %d 条 (期望 1) ⇒ 不动盘" % (key, len(hits)))
    return hits[0]


def date_objs(o, path=""):
    bad = []
    if isinstance(o, dict):
        for k, v in o.items():
            bad += date_objs(v, "%s.%s" % (path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            bad += date_objs(v, "%s[%d]" % (path, i))
    elif isinstance(o, (datetime.date, datetime.datetime)):
        bad.append((path, repr(o)))
    return bad


def main() -> int:
    os.makedirs(LOGD, exist_ok=True)
    raw = open(FRAG, encoding="utf-8").read()
    SNAP = os.path.join(LOGD, "hw.yaml.before_setjson")
    if os.path.exists(SNAP):
        # ★已存在开工前快照 ⇒ 以快照为基准重算 (★本脚本幂等·可复现★)
        raw = open(SNAP, encoding="utf-8").read()
        print("[OK] 复用开工前快照 = %s (不覆盖)" % os.path.relpath(SNAP, PROJ))
    else:
        shutil.copyfile(FRAG, SNAP)
        print("[OK] 开工前快照已存 = %s" % os.path.relpath(SNAP, PROJ))
    d = yaml.safe_load(raw)

    answers = d["answers"]
    needs = d["needs_from"]
    risks = d["risks"]

    before_answers = {i: sha(it) for i, it in enumerate(answers)}
    before_needs = {i: sha(it) for i, it in enumerate(needs)}
    before_risks = {i: sha(it) for i, it in enumerate(risks)}

    # ---------------- A1 ----------------
    i_a1 = find_one(answers, "vendor_q19_boot_storage")
    a1 = answers[i_a1]
    if a1["value"] != A1_OLD_HEAD:
        raise SystemExit("[X] A1 原文与预期不符 ⇒ 不动盘\n  实际: %r" % a1["value"])
    answers[i_a1] = dict(a1)
    answers[i_a1]["value"] = A1_NEW
    answers[i_a1]["ref"] = A1_NEW_REF

    # ---------------- A2 ----------------
    i_a2 = find_one(answers, "fw_boot_storage_bom")
    a2 = answers[i_a2]
    if "路线选 **eMMC 5.1 / ePoP** (不是 NOR)" not in a2["value"]:
        raise SystemExit("[X] A2 原文不含目标串 ⇒ 不动盘")
    answers[i_a2] = dict(a2)
    answers[i_a2]["value"] = A2_NEW

    # ---------------- N1 ----------------
    i_n1 = find_one(needs, "q3_storage_and_audio")
    n1 = needs[i_n1]
    if N1_OLD not in n1["item"]:
        raise SystemExit("[X] N1 目标串不在 item 里 ⇒ 不动盘\n  实际: %s" % n1["item"])
    needs[i_n1] = dict(n1)
    needs[i_n1]["item"] = n1["item"].replace(N1_OLD, N1_NEW)

    # ---------------- R1 ----------------
    i_r1 = find_one(risks, "R-hw-boot-storage", field="id")
    r1 = risks[i_r1]
    if r1["text"] != R1_OLD:
        raise SystemExit("[X] R1 原文与预期不符 ⇒ 不动盘\n  实际: %r" % r1["text"])
    risks[i_r1] = dict(r1)
    risks[i_r1]["text"] = R1_NEW
    # ★severity 刻意不动★ (风险等级调整属 main 裁量, 本单只改口径)

    # ---------------- 自检 ----------------
    for lst, before, idxs, name in (
        (answers, before_answers, {i_a1, i_a2}, "answers"),
        (needs, before_needs, {i_n1}, "needs_from"),
        (risks, before_risks, {i_r1}, "risks"),
    ):
        for i, it in enumerate(lst):
            if i in idxs:
                continue
            if sha(it) != before[i]:
                raise SystemExit("[X] %s[%d] 被意外改动 ⇒ 不动盘" % (name, i))
        # 目标条目: 只允许指定字段变 (逐字段断言见下)
        for i in idxs:
            print("[OK] %s[%d] 目标条目已改 (其余 %d 条逐字未动)" % (name, i, len(lst) - len(idxs)))

    # 逐字段 diff 断言 (★基准 = 开工前快照★)
    for i in (i_a1, i_a2):
        b = yaml.safe_load(open(SNAP, encoding="utf-8"))["answers"][i]
        a = answers[i]
        changed = sorted(k for k in set(b) | set(a) if b.get(k) != a.get(k))
        exp = ["ref", "value"] if i == i_a1 else ["value"]
        if changed != exp:
            raise SystemExit("[X] answers[%d] 改动字段 = %s (期望 %s)" % (i, changed, exp))
        for k in b:
            if k not in ("value", "ref"):
                assert b[k] == a[k], "answers[%d].%s 被改" % (i, k)
        print("[OK] answers[%d] 改动字段 = %s (to/key 逐字未动)" % (i, changed))

    bneed = yaml.safe_load(open(SNAP, encoding="utf-8"))["needs_from"][i_n1]
    aneed = needs[i_n1]
    ch = sorted(k for k in set(bneed) | set(aneed) if bneed.get(k) != aneed.get(k))
    if ch != ["item"]:
        raise SystemExit("[X] needs_from 改动字段 = %s (期望只有 item)" % ch)
    for k in bneed:
        if k != "item":
            assert bneed[k] == aneed[k], "needs_from.%s 被改" % k
    print("[OK] needs_from[%d] 改动字段 = ['item'] (to/due/since/waiting_on 逐字未动)" % i_n1)

    brisk = yaml.safe_load(open(SNAP, encoding="utf-8"))["risks"][i_r1]
    arisk = risks[i_r1]
    ch = sorted(k for k in set(brisk) | set(arisk) if brisk.get(k) != arisk.get(k))
    if ch != ["text"]:
        raise SystemExit("[X] risks 改动字段 = %s (期望只有 text)" % ch)
    assert brisk["severity"] == arisk["severity"], "severity 被改"
    print("[OK] risks[%d] 改动字段 = ['text'] (id/severity 逐字未动 · severity=%r 刻意不动)" % (i_r1, arisk["severity"]))

    for name, lst in (("answers", answers), ("needs_from", needs), ("risks", risks)):
        bad = date_objs(lst, name)
        if bad:
            raise SystemExit("[X] %s 含非字符串日期字段 ⇒ 不动盘: %s" % (name, bad[:5]))

    # ---------------- 落中间件 ----------------
    out_a = os.path.join(LOGD, "answers_after.json")
    out_n = os.path.join(LOGD, "needs_from_after.json")
    out_r = os.path.join(LOGD, "risks_after.json")
    for path, obj in ((out_a, answers), (out_n, needs), (out_r, risks)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)

    print("[OK] answers 条目数 = %d (改前 %d · 不增不减)" % (len(answers), len(before_answers)))
    print("[OK] needs_from 条目数 = %d (改前 %d · 不增不减)" % (len(needs), len(before_needs)))
    print("[OK] risks 条目数 = %d (改前 %d · 不增不减)" % (len(risks), len(before_risks)))
    for p in (out_a, out_n, out_r):
        print("[OK] 中间件 = %s" % os.path.relpath(p, PROJ))
    print("")
    print("★下一步 (必须逐条跑, 顺序固定):")
    for f, p in (("answers", out_a), ("needs_from", out_n), ("risks", out_r)):
        print("  python3 state/frag_write.py --agent hw-lead --set-json %s --set-field %s" % (p, f))
    return 0


if __name__ == "__main__":
    sys.exit(main())
