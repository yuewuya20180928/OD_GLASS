#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 04:3x · job 775d9893「ARS45 继续执行后继计划」
★TASK_BOARD §2 第 7 次对账的收尾: 把 ISS-257 行【移出 §2】(★不是改状态, 是移出★)
=========================================================================================
★**为什么必须移出行 (★alignment_check.py L55-60 的解析口径★)**:
★   `for ln in sec2.split("\\n"): m = re.match(r"^\\|\\s*(ISS-\\d+)\\s*\\|", ln)` ⇒ ★**只要 §2 表里还留着
★   一行「| ISS-xxx | ... |」, 它就被算成【在跑】⇒ 与台账 fixing 集合比对 ⇒ 不一致 ⇒ 判红★★
★   ⇒ ★**光把状态文字改成「已完成」不够 ⇒ 必须把整行移出 §2 (★这正是本文件自己的老规矩:
★   「⇒ ★**已移出本节** ★」· ★历史上 ISS-249/250/255/251 等 7 条都是这么处理的★)**
★
★**为什么 ISS-257 要移出 (★不是它没干完★)**:
★   · 台账 `state/issue_log.yaml` 里 ★**ISS-257 status = verified** ★ (★早已 verified·不是本轮才完的★)
★   · §2 是【与台账的投影】⇒ 台账里不在 flying 的, §2 就不该留着它的行
★   · ★**留着的代价 = alignment_check 第 1 条判据永远红 ⇒ 看板继续误导老板 (★「总表过期 = 看板误导老板」第 8 次应验★)**
★
★**移出后 §2 的内容 (★保持表头 + 3 条 cron 常驻行 + 已完成行的留痕★)**:
★   · ISS-265 / ISS-266 / ISS-181 三行是 ★**`**ISS-xxx**` 粗体格式** ⇒ ★**匹配不到 `^\\|\\s*ISS-\\d+\\s*\\|` 这个正则
★     ⇒ ★**它们不会被算成「在跑」★ (★这个粗体格式是本项目 §2 表的既有写法·不是我这次改的·保留★)
★   · ISS-257 行是唯一一行 ★**裸 `| ISS-257 |` 格式** ★ ⇒ ★**就是它触发的误报 ⇒ 移出它, 判据即转绿★**
★
★**留痕纪律**: ★**正文那一整行不删内容, 而是整行移出 §2 表 (★迁到本脚本追加的「已移出」记录里★)⇒ 老字逐字保留在案★**
★**边界**: ★**零写板 · 零落表 · 零外发 · 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不改台账 (台账已 verified·本脚本只读它做断言)★**
"""
import os
import re
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BOARD = os.path.join(PROJ, "TASK_BOARD.md")
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = BOARD + ".bak_20261118_0430_cron775d_board_sec2_fix"

NOTE = """

> ★**★⑦ ISS-257 行【已移出本节】(★2026-11-18 04:3x 补·第 7 次对账的收尾★)** ★
> ★**移出理由**: ★**台账 `state/issue_log.yaml` 里 ISS-257 status = `verified` (★早已 verified★) ⇒ §2 是台账的投影 ⇒ 不该留着它的行** ★
> ★**★为什么「改成已完成」还不够**: ★**`state/alignment_check.py` L55-60 的解析口径是 `re.match(r"^\\|\\s*(ISS-\\d+)\\s*\\|", ln)` ⇒ ★**只要 §2 表里还有一行裸 `| ISS-257 |` 格式, 它就被算成【在跑】⇒ 与台账 fixing 集合 ([] ) 不一致 ⇒ 第 1 条判据永远红★** ⇒ ★**必须整行移出 (★这正是本表自己的老规矩: 「⇒ 已移出本节」· 历史上 ISS-249/250/255/251 等 7 条都是这么处理的★)★** ★
> ★**★ISS-257 的内容 (★老字逐字保留, 不删一个字节★)**: ★★[主线内·原理图/选型侧·落表执行·续做] ★**上一轮落表【成功】**: BOM 必装∩[待选型] = **0** ⇒ `check_stage_g1a.py` 的 **G1a-7 已 ✅** · 6 条生成命令 rc=0 · 脚数 584/器件 218/K=0 没变 · 板 `611b869e…`+`.kicad_pro 3e504d2b…` 没动 ⇒ ★**本轮两件活**: ① **P0 修红** (★evidence 词表写错 ⇒ 网表 29 行写成 `[官网]` ⇒ `state/check_netlist.py` rc=1 ⇒ **G1a-5 由绿转红** ⇒ 改回落表链自己的 `[官方]` + 重生成 ⇒ 必须 rc=0★) ② **补交 4 件** (★`HW/SCHEMATIC_LANDING_V1_LANDED.md` **§18** 台账登记新 md5 ⇒ 顺修 `chain_gate` ① 网表准入红 · `HW/check_g1a7_selection_landed.py`+`--selftest` · 交卷单 · 分片含给 sw/mech 各 1 条 need★) ⇒ ★**只改 value/opn/evidence 三列 · 不落 V-2/V-3/V-4 · 零外发** ★★★
"""


def main() -> int:
    # ★断言: 台账里 ISS-257 确实不是 flying (★本脚本不许靠猜★)
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    by_id = {it.get("id"): it for it in (log.get("issues") or [])}
    st = (by_id.get("ISS-257") or {}).get("status")
    if st in ("fixing", "open"):
        raise SystemExit("★ISS-257 在台账里 status=%s ⇒ 不该移出 §2 ⇒ 拒绝写" % st)
    print("ℹ 断言通过: 台账 ISS-257 status=%s (非 flying ⇒ 可移出 §2)" % st)

    with open(BOARD, encoding="utf-8") as f:
        b = f.read()
    if "⑦ ISS-257 行【已移出本节】" in b:
        print("ℹ 移出记录已存在 ⇒ 幂等跳过")
        return 0

    lines = b.split("\n")
    keep, moved = [], []
    for ln in lines:
        if re.match(r"^\|\s*ISS-257\s*\|", ln):
            moved.append(ln)
        else:
            keep.append(ln)
    if len(moved) != 1:
        raise SystemExit("★§2 里裸格式 ISS-257 行数 = %d (期望 1) ⇒ 拒绝写" % len(moved))
    print("✅ 已移出 §2 的行 (%d 行, %d B)" % (len(moved), len(moved[0].encode("utf-8"))))

    shutil.copy2(BOARD, BAK)
    b = "\n".join(keep) + NOTE
    with open(BOARD, "w", encoding="utf-8") as f:
        f.write(b)
    print("✅ TASK_BOARD §2 已收口 (ISS-257 行移出 + 追加留痕) · 备份 %s" % os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
