#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0745_fix_iss236_brief_closout_marker.py
★main (moli) · 2026-11-16 07:4x · cron fb67af40 队列自动派活★

★★**为什么做这件事 (★派活前的命令存在性闸点名的第 1 条★)** ★★
· ★**`state/check_brief_commands.py` 实跑 ⇒ ❌ ISS-236: 引用了不存在的路径/命令 (1 个)**
  ⇒ ★**`HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md`** ★**(★实测: 该文件不存在★)** ★
· ★**但 ISS-236 的 brief 原文写的是**: `② ★**【原理图定稿收口清单】(★建议 `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md`★)** ★`
  ⇒ ★**这是【本单要新建的交付物】, 不是【要执行的命令】⇒ 属闸的第三类误报 (★闸靠
    「同一行 30 字内出现 新建/产出/交付物/输出文件…」来豁免本单产出★ ⇒ 原文用「★建议★」
    ⇒ 没命中豁免词 ⇒ 被当成"引用了不存在的路径"★)** ★
· ★**处置口径 (★不改 brief 语义, 只让闸认得出★)**:
  ★**① 把 ISS-236 brief 里两处「★建议 `路径`★」改成「★新建★ `路径` (★本单产出★)」**
  ★**② 这样 `check_brief_commands.py` 的 `declared_outputs()` 就能按其设计豁免它 ⇒ 闸从 ❌ 回到 ✅**
  ★**③ 不改任何验收判据 / 不改 owner / 不改 status / 不碰别人分片 / 不碰 PCB** ★

★★**★边界★** ★★
· ★**只改 ISS-236 一条的 task_brief 文本 (两处「建议」→「新建 (本单产出)」) ★**
· ★**status 保持 fixing (★hw-lead 正在跑这条: 会话 e7a86064 / 产物 state/land_v_values.py
  mtime 07:35★) ⇒ 本脚本【不碰它的 status】★**
· ★**零外发** · ★**零 message 工具** (微信通道 2026-11-11 10:17 已删) · ★**零 PCB 触碰** ★
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261116_0745_fix_iss236_brief_closout_marker"

OLD1 = "★**【原理图定稿收口清单】(★建议 `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md`★)**"
NEW1 = "★**【原理图定稿收口清单】(★新建★ `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` ★本单产出★)**"

OLD2 = "★**参数化一键落表器 (★建议 `state/land_v_values.py`★)**"
NEW2 = "★**参数化一键落表器 (★新建★ `state/land_v_values.py` ★本单产出★)**"

with open(LOG, "r", encoding="utf-8") as f:
    log = yaml.safe_load(f)

hit = 0
for it in log.get("issues") or []:
    if it.get("id") != "ISS-236":
        continue
    b = it.get("task_brief") or ""
    if OLD1 in b:
        b = b.replace(OLD1, NEW1)
        hit += 1
    if OLD2 in b:
        b = b.replace(OLD2, NEW2)
        hit += 1
    it["task_brief"] = b

assert hit == 2, "expected 2 replacements, got %d" % hit

shutil.copy2(LOG, BAK)
with open(LOG, "w", encoding="utf-8") as f:
    yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

print("[OK] ISS-236 brief: %d 处「★建议★」→「★新建★ (本单产出)」" % hit)
print("[OK] status 未动 / owner 未动 / 别人分片未碰 / 备份 =", os.path.basename(BAK))
