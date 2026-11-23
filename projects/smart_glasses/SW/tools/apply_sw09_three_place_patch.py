#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-368 · sw-lead · 「板那一趟」SW 侧清单第 9 条 (SW09_FP_TRUTH_READ) 的【三处同批落地】幂等补丁.

★**本脚本只交补丁, 真件零改** ★
  · ★**默认干跑 (dry-run)**: 不写任何盘 ⇒ 直接跑 `python3 SW/tools/apply_sw09_three_place_patch.py` 只打印计划 ★
  · ★**只有显式 `--apply` 才写盘** ⇒ ★**且只允许写到「项目盘 tmp/ 下的副本目录」⇒ 真件写不进去** ★
  · ★**幂等**: 同一补丁跑第二次 ⇒ 零变更 (逐字节 diff = 0) ⇒ 跑第三次同样零变更 ★
  · ★**可回滚**: `--rollback` 走同一套锚点反向执行 ⇒ 逐字节回到落地前的原文 ★

★**三处落点 (★main 2026-11-23 16:58 已裁「加」⇒ 必须三处同批★)** ★
  ★**落点①** `SW/BOARD_ONEPASS_SW_SYNC.md`
      · §2 逐条表      → 加第 9 行 (`SW09_FP_TRUTH_READ`)
      · §2 逐条表小节头 → 「8 条一条不许漏」⇒「9 条一条不许漏」
      · §2.1 归属步分布 → S10 由 3 条 ⇒ 4 条 (加 `SW09_FP_TRUTH_READ`)
      · §6 机器可读 JSON 块 → `items[]` 加第 9 个对象 (9 字段齐全)
  ★**落点②** `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md`
      · §H4-REG 三个登记数字 → `H4-ITEMS` 8⇒9 · `H4-COVER` 0⇒1 · `H4-GENERIC` 4⇒5
      · §H4-REG 块内正文 + 头部边界句 + §1 G01 行 + §5 证据分级行 ⇒ 同批改成「9 条 / 已收口」的口径
  ★**落点③** `SW/tools/check_fp_truth_read.py` (★ISS-363 已交·本单已跑绿★)
      · ★**本补丁对它【零改动】** ⇒ 只做【存在性 + 字节不变】双证 ★

★**为什么必须三处同批 (★本脚本存在的理由★)** ★
  · 落点② 的 §H4-REG 是【动态登记 vs 实测】判据 (ISS-362 闸 H4 / ISS-363 闸 F4 都读它) ⇒
    ★**只改落点① ⇒ 登记还是 8/0/4 而实测已经是 9/1/5 ⇒ H4 红 + F4 红** ★
  · 反过来 ★**只改落点② ⇒ 登记 9/1/5 而实测还是 8/0/4 ⇒ H4 红 + F4 红** ★
  · ⇒ ★**三处必须同批** ⇒ 本脚本把三处打成【一个动作】, 一次执行、一次可回滚 ★

★**边界 (★本脚本全程不越★)** ★
  · 零写板 (板 md5 / mtime / size 一个字节不许动 ⇒ 本脚本【不碰 HW/】★)
  · 零落表 (网表 / 脚表 / BOM 一个字节不许动 ⇒ 本脚本【不碰 HW/】★)
  · 零改既有闸 (既有闸脚本 / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一个字节不许动★)
  · 零改既有页面 (真件三处【本脚本一个字节都不写】⇒ 写盘只发生在 `--apply --target-root <项目盘 tmp/ 下的副本>★)
  · 零挂链 (本脚本【不】把自己写进任何 EXTRA_GATES★)
  · 零外发 (不发邮件 / 不询价 / 不联系供应商★)

用法:
    python3 SW/tools/apply_sw09_three_place_patch.py                 # 干跑 (★默认★·只打印计划)
    python3 SW/tools/apply_sw09_three_place_patch.py --dry-run       # 干跑 (★显式旗标·与默认同义·零副作用★)
    python3 SW/tools/apply_sw09_three_place_patch.py --json          # 干跑 (机读)
    python3 SW/tools/apply_sw09_three_place_patch.py --apply --target-root <项目盘 tmp/ 下的副本>
    python3 SW/tools/apply_sw09_three_place_patch.py --apply --rollback --target-root <副本>

退出码: 0 = 计划/执行成功 (幂等命中也算成功) · 1 = 有锚点缺失或校验不通过 (fail-closed) · 2 = 用法错 / 拒绝写真件
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))

SYNC_REL = os.path.join("SW", "BOARD_ONEPASS_SW_SYNC.md")
IMPACT_REL = os.path.join("SW", "BOARD_ONEPASS_FP_TRUTH_IMPACT.md")
GATE_REL = os.path.join("SW", "tools", "check_fp_truth_read.py")
PATCH_REL = os.path.join("SW", "BOARD_ONEPASS_SW09_LANDING_PATCH.md")

SPOT_SYNC = "①清单页 SW/BOARD_ONEPASS_SW_SYNC.md"
SPOT_IMPACT = "②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md"
SPOT_GATE = "③新闸 SW/tools/check_fp_truth_read.py"

SW09_ID = "SW09_FP_TRUTH_READ"

# ==================================================================================================
# ★落点③ 的闸: 只验不改 (★ISS-363 已交·本补丁对它零改动★)
# ==================================================================================================
GATE_REL_MD5_EXPECT = "cab7a6f17c1da35f4e54185ad8b62089"   # ★ISS-363 交卷时的 md5 (★本单开工前实测同值★)

# ==================================================================================================
# ★落点① 的新增内容 (★SW09 的 9 个字段·逐字取自 ISS-363 交卷页 §B4 / 登记页 §1 的草案★)
#   ★**字段顺序 = 清单 JSON 的 9 字段顺序** ★ · ★**字符串里不许出现 ASCII 双引号** (★JSON 会转义★)★
# ==================================================================================================
SW09_ITEM = {
    "id": SW09_ID,
    "source_iss": "ISS-241+ISS-244",
    "title": "S10 换封装真值: 三份真源的封装栏 (fp 栏) 必须与板面库封装名逐行一致 (★SW 侧第一跳 = 把那一栏从「没人读」变成「有闸读」★)",
    "current_state": (
        "[实测] 板面 186 个封装的库封装名【全空】(0/186 非空) ⇒ 「库封装名」这个真值在板面上现在不存在 "
        "⇒ 三份真源的 fp 栏自然也换不了 ⇒ ① 网表 513 行里 423 行 fp 空 (170 个 ref 板上有) "
        "② 脚表 584 行里 454 行 fp 空 (172 个 ref 板上有) ③ BOM 218 行 fp 全非空, 但 178 行写「待定」(81.7%) "
        "④ BOM 的 `J_USB_C` 写「16 焊盘」而板面实际 18 个 pad (机械孔算不算焊盘的口径差) "
        "⇒ SW 侧第一跳只能是【让那一栏机器读得到 + 把真值来源钉死】, 换真值那一跳要等板侧先补库封装名"
    ),
    "action": (
        "板侧那一趟 (★板只改一次 ⇒ 这一跳必须落在那一趟里★): 先把板面 186 个封装的库封装名补成真库封装名 "
        "⇒ ★**同批** (★一次落表批次·不许分两批★) 把三份真源的 fp 栏换成【同一个库封装名字符串】"
        "⇒ 三份真源 md5 同批变 ⇒ 落表台账同批留痕 ⇒ SW 侧同批把 F1 的期望值 (哪一行该是什么值) 跟着走 "
        "⇒ ★**不许只改一处 (★三处同批★)**"
    ),
    "criterion": (
        "python3 SW/tools/check_fp_truth_read.py ⇒ rc=0 "
        "(★F1 那一栏按表头名可读 + F2 盘上 md5 == 落表台账链头 + F4 清单登记条数 == 本机实测条数★) ; "
        "python3 SW/tools/check_sw_fp_truth_impact.py ⇒ rc=0 "
        "(★ISS-362 的 H1/H4 登记式绿 ⇒ 加第 9 条那天, §H4-REG 的三个数字要同批同步★)"
    ),
    "step": "S10",
    "blocked_by": "板那一趟 (★板面库封装名补齐 ⇒ 归板侧/hw-lead★) + main→老板 (★加新判据 = 改判据 = 受保护资产★)",
    "evidence": "[实测]",
}

# ★§2 逐条表的那一行 (★7 列: id | source_iss | title | step | blocked_by | current_state | criterion★)
SW09_ROW = (
    "| ★**`{id}`** ★ | ★{src} ★ | ★**{title}** ★ | ★**{step}** ★ | ★**{blk}** ★ | ★**{cur}** ★ | ★**{cri}** ★ |"
).format(
    id=SW09_ID,
    src=SW09_ITEM["source_iss"],
    title=SW09_ITEM["title"],
    step=SW09_ITEM["step"],
    blk=SW09_ITEM["blocked_by"],
    cur=SW09_ITEM["current_state"],
    cri=SW09_ITEM["criterion"],
)

# ==================================================================================================
# ★落点② 的正文改写 (★逐字给出 · 供 §1 规格页与 §4 回滚页引用★)
# ==================================================================================================
IMPACT_HEAD_OLD = (
    "> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** · "
    "★**不许往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条** (★那是「改那一趟的清单」⇒ 归 main 裁★) ★"
)
IMPACT_HEAD_NEW = (
    "> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** · "
    "★**第 9 条 (`SW09_FP_TRUTH_READ`) 已按 main 2026-11-23 16:58 的裁决「加」同批落地** "
    "(★清单页 §2 表 + §2.1 分布表 + §6 JSON 块 三处同批 + 本页 §H4-REG 三个数字同步★) "
    "⇒ ★**本页后续【不许】单改一处** (★只改一处 ⇒ H4 红 + F4 红★) ★"
)

IMPACT_G01_OLD = "(★板侧输入清单 8 条 + W5 现状探针 + W6 受保护 5 件台账对账★)"
IMPACT_G01_NEW = "(★板侧输入清单 9 条 + W5 现状探针 + W6 受保护 5 件台账对账★)"

IMPACT_EV_OLD = "| 8 条板侧输入清单覆盖这一跳的条目 = 0 | ★**实测** ★ | §4 的新闸 H4 实读 JSON 块 |"
IMPACT_EV_NEW = "| 9 条板侧输入清单覆盖这一跳的条目 = 1 | ★**实测** ★ | §4 的新闸 H4 实读 JSON 块 |"

H4_HEAD_OLD = "### H4-REG · 8 条板侧输入清单里没有「S10 换封装真值」这一条"
H4_HEAD_NEW = "### H4-REG · 9 条板侧输入清单里已有「S10 换封装真值」这一条 (★`SW09_FP_TRUTH_READ`★)"

H4_FINDING_OLD = (
    "- H4-FINDING: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` 的 8 条清单 (SW01~SW08) 里, 没有任何一条的 "
    "`current_state` / `action` 讲的是【封装栏落真库封装名】这件事 ⇒ 覆盖条数 = 0** ★ "
    "⇒ ★**⇒ S10 换封装真值这一跳, 在 SW 侧的板侧输入清单上是【完全空白的】** ★"
)
H4_FINDING_NEW = (
    "- H4-FINDING: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` 的 9 条清单 (SW01~SW09) 里, 已有 1 条 "
    "(`SW09_FP_TRUTH_READ`) 的 `current_state` / `action` 讲的是【封装栏落真库封装名】这件事 ⇒ 覆盖条数 = 1** ★ "
    "⇒ ★**⇒ S10 换封装真值这一跳, 在 SW 侧的板侧输入清单上已被【收口】** "
    "(★第 9 条于 2026-11-23 按 main 16:58 裁决「加」同批落地★) ★"
)

H4_IMPACT_OLD = (
    "- H4-IMPACT: ★**清单是那一趟的 SW 侧【收口清单】⇒ 它没有的跳 ⇒ 那一趟当天就没有人认领这一跳 ⇒ "
    "这一跳红/不红都没人解释 ⇒ 而这一跳【必然换 3 个 md5】⇒ 正好撞在 §1.1 那三道条件闸的口径上 ⇒ "
    "风险 = 有人为了让闸绿去改锚点 / 改判据** ★"
)
H4_IMPACT_NEW = (
    "- H4-IMPACT: ★**清单是那一趟的 SW 侧【收口清单】⇒ 它有的跳 ⇒ 那一趟当天有人认领这一跳 ⇒ "
    "这一跳红/不绿都有判据 ⇒ 而这一跳【必然换 3 个 md5】⇒ 正好撞在 §1.1 那三道条件闸的口径上 ⇒ "
    "风险 = 有人为了让闸绿去改锚点 / 改判据** ★"
)

H4_COUNTER_OLD = (
    "- H4-COUNTERMEASURE: ★**本页 §1 逐闸写清了这一跳会不会红 / 红了怎么判; §3 给了当天 SOP ⇒ "
    "空白被【登记】上了 ⇒ 那一趟当班的人照着 §3 念即可** ★ ⇒ ★**★本单【不许】直接往 "
    "`SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条 ⇒ 那是「改那一趟的清单」⇒ 归 main 裁★** ★ ⇒ "
    "★**要加的话, 加的写法建议见本页交卷页 B5-2 (★归 main 转 hw-lead / 板侧作业包那一趟★)** ★"
)
H4_COUNTER_NEW = (
    "- H4-COUNTERMEASURE: ★**本页 §1 逐闸写清了这一跳会不会红 / 红了怎么判; §3 给了当天 SOP ⇒ "
    "这一跳被【收口】上了 ⇒ 那一趟当班的人照着 §3 念即可** ★ ⇒ ★**★第 9 条 (`SW09_FP_TRUTH_READ`) 已按 "
    "main 2026-11-23 16:58 的裁决「加」同批落地** (★清单页 §2 表 + §2.1 分布表 + §6 JSON 块 三处同批 "
    "+ 本页 §H4-REG 三个数字同步★) ⇒ ★**对应的机器闸 `SW/tools/check_fp_truth_read.py` 已交 (★ISS-363★) "
    "⇒ 第 9 条与那一栏的判据都在机器上可查** ★"
)

H4_NOTE_OLD = (
    "- ★**附: `H4-GENERIC=4` 的含义** ★: ★**8 条里有 4 条 (SW02 / SW04 / SW07 / SW08) 的 "
    "`current_state` / `action` 里泛泛提到过「封装」二字, 但没有一条说的是【封装栏落真值】⇒ 也就是说: "
    "「泛提封装」的那 4 条, **一条都不覆盖这一跳** ⇒ 覆盖条数仍然是 0** ★"
)
H4_NOTE_NEW = (
    "- ★**附: `H4-GENERIC=5` 的含义** ★: ★**9 条里有 5 条 (SW02 / SW04 / SW07 / SW08 / SW09) 的 "
    "`current_state` / `action` 里提到过「封装」二字, 其中只有 SW09 这一条说的是【封装栏落真值】⇒ 也就是说: "
    "「泛提封装」的那 4 条 (SW02 / SW04 / SW07 / SW08) **一条都不覆盖这一跳** ⇒ 覆盖条数 = 1 (★只算 SW09★)** ★"
)

# ==================================================================================================
# ★编辑表 (★每条 = 一个唯一锚点 + 逐字原文 + 逐字新文 + 自证口径★)
#   kind = "replace"            ⇒ old 必须【全文唯一】出现一次
#   kind = "insert_after_line"  ⇒ anchor 必须【全文唯一】命中一行, payload 插在该行之后
#   kind = "json_append"        ⇒ 往 §6 JSON 块的 items[] 末尾追加一个对象
# ==================================================================================================
EDITS = [
    # ---------------- 落点① : 清单页 ----------------
    dict(eid="A1", spot=SPOT_SYNC, file=SYNC_REL, kind="replace",
         where="§2 逐条表 · 小节头",
         old="## §2 · 逐条表 (★每条固定 9 个字段 · ★★8 条一条不许漏★★)",
         new="## §2 · 逐条表 (★每条固定 9 个字段 · ★★9 条一条不许漏★★)",
         proof="★grep「★★9 条一条不许漏★★」命中 1 次 · ★且 §6 JSON 块 items 长度 == 9★"),
    dict(eid="A2", spot=SPOT_SYNC, file=SYNC_REL, kind="insert_after_line",
         where="§2 逐条表 · 第 9 行",
         anchor="| ★**`SW08_ESD_USB_D`** ★ | ★ISS-266+ISS-279 ★ |",
         payload=SW09_ROW,
         proof="★§2 表里 grep「`SW09_FP_TRUTH_READ`」命中 1 次 (★且该行 7 列齐全★)★"),
    dict(eid="A3", spot=SPOT_SYNC, file=SYNC_REL, kind="replace",
         where="§2.1 归属步分布 · S10 行",
         old="| ★**S10** ★ | 3 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` ★ |",
         new="| ★**S10** ★ | 4 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` · `SW09_FP_TRUTH_READ` ★ |",
         proof="★§2.1 表里 S10 行条数 == 4 且条目含 `SW09_FP_TRUTH_READ`★"),
    dict(eid="A4", spot=SPOT_SYNC, file=SYNC_REL, kind="json_append",
         where="§6 机器可读 JSON 块 · items[]",
         item=SW09_ITEM,
         proof="★§6 JSON 块 items 长度 == 9 且 items[8].id == SW09_FP_TRUTH_READ 且 9 字段齐全非空★"),

    # ---------------- 落点② : 影响页 ----------------
    dict(eid="B1", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="页首边界句",
         old=IMPACT_HEAD_OLD, new=IMPACT_HEAD_NEW,
         proof="★grep「已按 main 2026-11-23 16:58 的裁决「加」同批落地」命中 1 次★"),
    dict(eid="B2", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§1 逐闸表 G01 行",
         old=IMPACT_G01_OLD, new=IMPACT_G01_NEW,
         proof="★grep「板侧输入清单 9 条」命中 1 次★"),
    dict(eid="B3", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · 小节头",
         old=H4_HEAD_OLD, new=H4_HEAD_NEW,
         proof="★grep「9 条板侧输入清单里已有」命中 1 次★"),
    dict(eid="B4", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · H4-ITEMS",
         old="- H4-ITEMS: 8", new="- H4-ITEMS: 9",
         proof="★H4-REG 块里 `H4-ITEMS` == 9★"),
    dict(eid="B5", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · H4-COVER",
         old="- H4-COVER: 0", new="- H4-COVER: 1",
         proof="★H4-REG 块里 `H4-COVER` == 1★"),
    dict(eid="B6", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · H4-GENERIC",
         old="- H4-GENERIC: 4", new="- H4-GENERIC: 5",
         proof="★H4-REG 块里 `H4-GENERIC` == 5★"),
    dict(eid="B7", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · H4-FINDING",
         old=H4_FINDING_OLD, new=H4_FINDING_NEW,
         proof="★H4-FINDING 非空且含「覆盖条数 = 1」★"),
    dict(eid="B8", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · H4-IMPACT",
         old=H4_IMPACT_OLD, new=H4_IMPACT_NEW,
         proof="★H4-IMPACT 非空★"),
    dict(eid="B9", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · H4-COUNTERMEASURE",
         old=H4_COUNTER_OLD, new=H4_COUNTER_NEW,
         proof="★H4-COUNTERMEASURE 非空且含「已按 main 2026-11-23 16:58 的裁决「加」同批落地」★"),
    dict(eid="B10", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§H4-REG 块 · 附注 (H4-GENERIC 的含义)",
         old=H4_NOTE_OLD, new=H4_NOTE_NEW,
         proof="★grep「附: `H4-GENERIC=5` 的含义」命中 1 次★"),
    dict(eid="B11", spot=SPOT_IMPACT, file=IMPACT_REL, kind="replace",
         where="§5 证据分级 · 覆盖条数那一行",
         old=IMPACT_EV_OLD, new=IMPACT_EV_NEW,
         proof="★grep「9 条板侧输入清单覆盖这一跳的条目 = 1」命中 1 次★"),
]

JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)


# ==================================================================================================
# 小工具
# ==================================================================================================
def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve(root: str, rel: str) -> str:
    return os.path.join(root, rel)


# ==================================================================================================
# ★三种原子操作 (★每种都返回 (新文本, 状态) · 状态 ∈ applied / already / missing★)
# ==================================================================================================
def op_replace(text: str, old: str, new: str):
    n = text.count(old)
    if n == 0:
        if text.count(new) >= 1:
            return text, "already"
        return text, "missing"
    if n > 1:
        return text, "ambiguous"
    return text.replace(old, new, 1), "applied"


def op_insert_after_line(text: str, anchor: str, payload: str):
    if payload in text:
        return text, "already"
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if anchor in l]
    if len(hits) != 1:
        return text, "missing" if not hits else "ambiguous"
    i = hits[0]
    lines.insert(i + 1, payload)
    return "\n".join(lines), "applied"


def _json_block_span(text: str):
    m = JSON_BLOCK_RE.search(text)
    if not m:
        return None
    return m


def op_json_append(text: str, item: dict):
    m = _json_block_span(text)
    if not m:
        return text, "missing"
    try:
        data = json.loads(m.group(1))
    except Exception:                                        # noqa: BLE001
        return text, "missing"
    items = data.get("items")
    if not isinstance(items, list):
        return text, "missing"
    for it in items:
        if isinstance(it, dict) and it.get("id") == item["id"]:
            return text, "already"
    items.append(item)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    return text[:m.start(1)] + new_json + text[m.end(1):], "applied"


def op_json_remove(text: str, item_id: str):
    m = _json_block_span(text)
    if not m:
        return text, "missing"
    try:
        data = json.loads(m.group(1))
    except Exception:                                        # noqa: BLE001
        return text, "missing"
    items = data.get("items")
    if not isinstance(items, list):
        return text, "missing"
    keep = [it for it in items if not (isinstance(it, dict) and it.get("id") == item_id)]
    if len(keep) == len(items):
        return text, "already"
    data["items"] = keep
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    return text[:m.start(1)] + new_json + text[m.end(1):], "applied"


# ==================================================================================================
# ★计划 / 执行
# ==================================================================================================
def plan(root: str):
    """返回 (要读的文件 → 文本, 编辑表) ★"""
    files = {}
    for rel in (SYNC_REL, IMPACT_REL, GATE_REL):
        p = resolve(root, rel)
        files[rel] = read_text(p) if os.path.isfile(p) else None
    return files


def run_edits(files: dict, rollback: bool = False):
    """★在内存里跑一遍编辑表 ⇒ 返回 (新文件表, 报告) ★"""
    out = dict(files)
    report = []
    for ed in EDITS:
        rel = ed["file"]
        text = out.get(rel)
        if text is None:
            report.append(dict(eid=ed["eid"], spot=ed["spot"], where=ed["where"],
                               status="missing_file", file=rel))
            continue
        if rollback:
            if ed["kind"] == "replace":
                new, st = op_replace(text, ed["new"], ed["old"])
            elif ed["kind"] == "insert_after_line":
                new, st = op_remove_line(text, ed["payload"])
            else:                                            # json_append
                new, st = op_json_remove(text, ed["item"]["id"])
        else:
            if ed["kind"] == "replace":
                new, st = op_replace(text, ed["old"], ed["new"])
            elif ed["kind"] == "insert_after_line":
                new, st = op_insert_after_line(text, ed["anchor"], ed["payload"])
            else:                                            # json_append
                new, st = op_json_append(text, ed["item"])
        out[rel] = new
        report.append(dict(eid=ed["eid"], spot=ed["spot"], where=ed["where"],
                           status=st, file=rel, proof=ed["proof"]))
    return out, report


def op_remove_line(text: str, payload: str):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l == payload]
    if not hits:
        return text, "already"
    if len(hits) > 1:
        return text, "ambiguous"
    del lines[hits[0]]
    return "\n".join(lines), "applied"


# ==================================================================================================
# ★写盘闸: 只许写项目盘 tmp/ 下的副本 ⇒ 真件写不进去 ★
# ==================================================================================================
def guard_target(root: str, target: str):
    """★返回 (ok, 原因) ★"""
    root_r = os.path.realpath(root)
    tgt_r = os.path.realpath(target)
    if tgt_r == root_r:
        return False, "★拒绝: 目标就是真件项目根 ⇒ 真件写不进去★"
    tmp_r = os.path.realpath(os.path.join(root_r, "tmp"))
    if not (tgt_r == tmp_r or tgt_r.startswith(tmp_r + os.sep)):
        return False, "★拒绝: 目标不在项目盘 `tmp/` 下 ⇒ 只许写副本目录★"
    if not os.path.isdir(tgt_r):
        return False, "★拒绝: 目标副本目录不存在 ⇒ 先建目录再跑★"
    return True, "ok"


def protected_guard(root: str, target: str):
    """★写盘前的最后一道闸: 目标副本里的真件三处 + 板 + 三份真源 + 既有闸, 逐字节不许变 ★"""
    problems = []
    # 板 + 三份真源 (★本补丁【不碰 HW/】⇒ 副本里它们必须原样 ★)
    for rel in (os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
                os.path.join("HW", "netlist_v1.csv"),
                os.path.join("HW", "netlist_v1_pins.csv"),
                os.path.join("HW", "BOM_v1.csv")):
        p = resolve(root, rel)
        q = resolve(target, rel)
        if os.path.isfile(p) and os.path.isfile(q):
            if md5_of(p) != md5_of(q):
                problems.append("副本里的 %s 与真件不一致 ⇒ 沙盒不干净" % rel)
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="ISS-368 · SW09 三处同批落地 · 幂等补丁 (★默认干跑★)")
    ap.add_argument("--root", default=PROJ, help="★项目根 (默认 = 本脚本所在仓库根★)")
    ap.add_argument("--dry-run", action="store_true",
                    help="★显式声明干跑 (★默认就是干跑·本旗标只为让必跑命令逐字可跑·零副作用★)")
    ap.add_argument("--apply", action="store_true", help="★真写盘 (★默认不写★)")
    ap.add_argument("--rollback", action="store_true", help="★反向补丁 (★与 --apply 一起用★)")
    ap.add_argument("--target-root", default="", help="★写盘目标 (★必须是项目盘 tmp/ 下的副本目录★)")
    ap.add_argument("--json", action="store_true", help="★机读输出★")
    args = ap.parse_args(argv)

    if args.dry_run and args.apply:
        sys.stderr.write("❌ --dry-run 与 --apply 互斥 (★本脚本默认干跑·真写盘只走 --apply★)\n")
        return 2

    root = os.path.abspath(args.root)
    target = os.path.abspath(args.target_root) if args.target_root else ""

    # ★写盘闸先跑 (★拒绝写真件 ⇒ 后面的一切都发生在副本上★)
    if args.apply:
        if not target:
            sys.stderr.write("❌ --apply 必须带 --target-root <项目盘 tmp/ 下的副本目录> "
                             "(★真件写不进去★)\n")
            return 2
        ok, why = guard_target(root, target)
        if not ok:
            sys.stderr.write("❌ %s\n" % why)
            return 2
        probs = protected_guard(root, target)
        if probs:
            sys.stderr.write("❌ 沙盒卫生不通过: %s\n" % "; ".join(probs))
            return 1

    # ★基准文本: 干跑 ⇒ 真件; 写盘 ⇒ 目标副本 (★补丁是相对【被改的那个文件】的★)
    base_root = target if args.apply else root
    files = plan(base_root)
    missing = [r for r, t in files.items() if t is None]
    if missing:
        sys.stderr.write("❌ 读不到: %s\n" % ", ".join(missing))
        return 1

    out, report = run_edits(files, rollback=args.rollback)
    changed = [r for r in report if r["status"] == "applied"]
    bad = [r for r in report if r["status"] in ("missing", "ambiguous", "missing_file")]

    # ★落点③ 的双证 (★只验不改★)
    gate_p = resolve(root, GATE_REL)
    gate_md5_before = md5_of(gate_p)
    gate_md5_after = md5_of(gate_p)

    result = {
        "mode": ("apply" if args.apply else "dry-run") + ("+rollback" if args.rollback else ""),
        "root": root,
        "base_root": base_root,
        "target_root": args.target_root or "",
        "edits": report,
        "n_edits": len(report),
        "n_changed": len(changed),
        "n_bad": len(bad),
        "spot3_gate": {
            "rel": GATE_REL,
            "md5_before": gate_md5_before,
            "md5_after": gate_md5_after,
            "unchanged": gate_md5_before == gate_md5_after,
            "expect_md5": GATE_REL_MD5_EXPECT,
            "matches_expect": gate_md5_before == GATE_REL_MD5_EXPECT,
        },
        "new_bytes": {r: len(out[r].encode("utf-8")) for r in (SYNC_REL, IMPACT_REL)},
        "old_bytes": {r: len(files[r].encode("utf-8")) for r in (SYNC_REL, IMPACT_REL)},
    }

    # ---------------- 写盘 (★只有 --apply 才走这里★) ----------------
    if args.apply:
        for rel in (SYNC_REL, IMPACT_REL):
            src = resolve(target, rel)
            if not os.path.isfile(src):
                sys.stderr.write("❌ 副本里缺 %s ⇒ 先把真件复制进副本★\n" % rel)
                return 1
        if bad:
            sys.stderr.write("❌ 有锚点缺失/歧义 ⇒ 拒绝写盘 (fail-closed): %s\n"
                             % ", ".join("%s(%s)" % (r["eid"], r["status"]) for r in bad))
            return 1
        if changed:
            for rel in (SYNC_REL, IMPACT_REL):
                with open(resolve(target, rel), "w", encoding="utf-8", newline="") as f:
                    f.write(out[rel])
        result["written"] = ([resolve(target, SYNC_REL), resolve(target, IMPACT_REL)]
                              if changed else [])
        result["written_md5_after"] = {rel: md5_of(resolve(target, rel))
                                       for rel in (SYNC_REL, IMPACT_REL)}
        # ★落点③ 再双证一次 (★写盘之后★)
        gp = resolve(target, GATE_REL)
        result["spot3_gate"]["md5_after_write"] = md5_of(gp) if os.path.isfile(gp) else None
        result["spot3_gate"]["unchanged"] = (
            result["spot3_gate"]["md5_after_write"] in (None, gate_md5_before))


    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 96)
        print("ISS-368 · SW09 三处同批落地 · 幂等补丁 · 模式 = %s" % result["mode"])
        print("  项目根 = %s" % root)
        if args.apply:
            print("  写盘目标 = %s" % target)
            print("  ★**真件一个字节都没写 (写盘只发生在上面的副本目录里)** ★")
        else:
            print("  基准 = %s" % base_root)
            print("  ★**干跑 (默认) ⇒ 本次一个字节都没写** ★")
        print("=" * 96)
        for r in report:
            mark = {"applied": "★变★", "already": "幂等命中(零变更)",
                    "missing": "★锚点缺失★", "ambiguous": "★锚点歧义★",
                    "missing_file": "★文件缺★"}.get(r["status"], r["status"])
            print("  [%-12s] %-6s %-38s %s" % (mark, r["eid"], r["where"], r["spot"]))
            print("               自证: %s" % r.get("proof", "-"))
        print("-" * 96)
        print("  编辑 %d 条 · 变更 %d 条 · 幂等命中(零变更) %d 条 · 异常 %d 条"
              % (len(report), len(changed),
                 len([r for r in report if r["status"] == "already"]), len(bad)))
        print("  落点③ 新闸 md5 前后 = %s ⇒ %s"
              % (result["spot3_gate"]["md5_before"],
                 "未变 ★" if result["spot3_gate"]["unchanged"] else "★变了★"))
        if result["spot3_gate"]["matches_expect"]:
            print("  落点③ 新闸 md5 == ISS-363 交卷基线 (%s) ⇒ 一致 ★"
                  % GATE_REL_MD5_EXPECT)
        else:
            print("  ★落点③ 新闸 md5 != ISS-363 交卷基线 ⇒ 本单【零改动该文件】的声明需复核★")
        if args.apply:
            if result["written"]:
                print("  已写: %s" % " · ".join(result["written"]))
            else:
                print("  ★**零写入 (幂等命中 ⇒ 本次没有任何文件被改)** ★")
        print("=" * 96)

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
