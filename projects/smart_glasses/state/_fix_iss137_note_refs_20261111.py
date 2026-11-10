#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""订正 ISS-137 note 里的单号引用 + 把 ISS-187 的交付物清单改成实测真值 (2026-11-11 05:0x)

★**为什么改**: ①ISS-137 的 note 里我写了「这三条已另开 ISS-186 承接」⇒ ★**错的**:
   ★**ISS-186 只承接第 ② 条 (DSI payload 6 处)**, ★**第 ① (护栏两洞) + 第 ③ (4 处下游残留) 是 ISS-187**
   ⇒ ⇒ ★**单号指错 = 下一个读的人会去错单找东西** ⇒ 必须订正。
   ②ISS-187 的 fix_ref 里我漏了 `SW/DEMO_OD_PIPELINE_SPEC.md:447` (★**我第一遍真去改了它,
   但 fix_ref 写漏了 ⇒ 又是"做了但没记全"**) ⇒ ★**改成实测 md5 真值**。

★**纪律**: 原子写 + 逐条 count 断言 (旧串必须 count==1, 否则拒绝写)。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

items = doc.get("issues")
items = list(items.values()) if isinstance(items, dict) else list(items or [])

by_id = {it.get("id"): it for it in items}

changed = []

# ---- ① 订正 ISS-137 note 的单号引用 ----
i137 = by_id.get("ISS-137")
if i137 is None:
    print("❌ 找不到 ISS-137")
    sys.exit(1)

old_ref = ("③ 4 处下游旧口径残留 (PROJECT_TRACKER.md:2098 / SW/DEMO_OD_PIPELINE_SPEC.md:447 / "
           "SW/DEMO_OD_TIMING_SPEC.md:194 / SW/tools/rknn_bench.py:257·261)。⇒ ★**这三条已另开 ISS-186 承接** "
           "(owner=main / verify_by=sw-lead), ★**不在本单偷偷带过**。")
new_ref = ("③ 4 处下游旧口径残留 (PROJECT_TRACKER.md:2098 / SW/DEMO_OD_PIPELINE_SPEC.md:447 / "
           "SW/DEMO_OD_TIMING_SPEC.md:194 / SW/tools/rknn_bench.py:257·261)。⇒ ★**这三条已另开 ISS-187 承接** "
           "(owner=main / verify_by=sw-lead, status=fixed, ★**待 sw-lead 复验**), ★**不在本单偷偷带过**。\n"
           "★**单号更正 (2026-11-11 05:0x)**: ★**我第一遍把 ①③ 都写成「ISS-186 承接」⇒ 错了 ⇒ 已订正** ⇒\n"
           "  ★**ISS-186 只承接第 ② 条 (DSI payload 8× 口径差 6 处, owner=hw-lead)** ⇒\n"
           "  ★**第 ① (护栏两洞) + 第 ③ (4 处下游残留) 在 ISS-187** ⇒ ★**单号指错 = 下一个读的人会去错单找东西 ⇒ 必须订正**。")

note = i137.get("note") or ""
if old_ref in note:
    i137["note"] = note.replace(old_ref, new_ref)
    changed.append("ISS-137: note 单号引用 ISS-186 → ISS-187 (第 ①③ 条)")
elif new_ref in note:
    print("ℹ️ ISS-137 note 单号引用已是订正版 (幂等)")
else:
    print("❌ ISS-137 note 里没找到预期的旧串 ⇒ 拒绝盲改")
    sys.exit(2)

# ---- ② ISS-187 的 fix_ref 改成实测真值 ----
i187 = by_id.get("ISS-187")
if i187 is None:
    print("❌ 找不到 ISS-187")
    sys.exit(1)

old_fr = ("HW/e2e_budget_rk3572.py (★selftest() 新增护栏 ⑧⑨⑩ 三条, ★**只加护栏, 一行已发布数字都没动** — "
          "stdout 逐字节比对 diff 空★) · md5 0e622d56… → **d7d1b110e4ed73d244ff02719c1704d6** · "
          "PROJECT_TRACKER.md:2098 (加「已被 ISS-137 rev1 取代」标记, ★**原文一字不删**) · "
          "SW/DEMO_OD_TIMING_SPEC.md:194 (★「显示 TX 与光机 S10 仍是 [0数据]」→ 写清「显示输出侧实测值仍 [0数据] + "
          "TX 只有物理下限 7.776ms ⇒ 合成段只剩 2.32ms」★; md5 71f0c913… → **88f441ecf6e62918e5182acdd2364ef8**) · "
          "SW/tools/rknn_bench.py:257/261 (S9 标签「显示 TX」→「显示输出侧」, ★**数字不动**; md5 → **38e256d2fa1c1fd220077b14bc73e91d**)")

new_fr = (
    "★**4 个文件, 4 处残留 + 3 条护栏, 全部只改口径措辞 / 只加护栏, 一个已发布数字都没动** (★stdout 逐字节比对 diff 空★):\n"
    "  ① `HW/e2e_budget_rk3572.py` — ★selftest() 新增护栏 ⑧⑨⑩ 三条 ⇒ md5 0e622d56… → **d7d1b110e4ed73d244ff02719c1704d6**\n"
    "  ② `PROJECT_TRACKER.md:2098` — 加「已被 ISS-137 rev1 取代」标记 (★**原文一字不删**, ★历史不能被抹掉但不能被当现行结论用★)\n"
    "  ③ `SW/DEMO_OD_TIMING_SPEC.md:194` — 「显示 TX 与光机 S10 仍是 [0数据]」→ 写清「显示输出侧实测值仍 [0数据] + "
    "TX 只有物理下限 7.776ms ⇒ 合成段只剩 2.32ms」 ⇒ md5 71f0c913… → **88f441ecf6e62918e5182acdd2364ef8**\n"
    "  ④ `SW/tools/rknn_bench.py:257/261` — S9 标签「显示 TX」→「显示输出侧」 (★**与 `SW/RKNN_BENCH.md` §4.1 现口径对齐**★, "
    "★**数字不动**★) ⇒ md5 → **38e256d2fa1c1fd220077b14bc73e91d**\n"
    "  ⑤ `SW/DEMO_OD_PIPELINE_SPEC.md:447` — 悬空引用「§⑤ 已指出 显示合成段占 T_FIXED 多少是 [0数据]」→ 改指向 §⑤ 的"
    "**可测判据** (输出侧上限 10.09ms − TX 物理下限 7.776ms ⇒ 合成段只剩 2.32ms ⇒ 一行命令出结论) ⇒ "
    "md5 058c8bde… → **2fe3be4c55bda369a56a13ef6d00565d**"
)

fr = i187.get("fix_ref") or ""
if old_fr in fr:
    i187["fix_ref"] = new_fr
    changed.append("ISS-187: fix_ref 改成 5 条实测真值 (补上了漏记的 DEMO_OD_PIPELINE_SPEC.md:447)")
elif new_fr in fr:
    print("ℹ️ ISS-187 fix_ref 已是实测真值版 (幂等)")
else:
    print("❌ ISS-187 fix_ref 里没找到预期的旧串 ⇒ 拒绝盲改")
    sys.exit(3)

# ---- ③ ISS-187 note 里的"4 处已清"表述核对 (实测: 4 处确实都改了) ----
n187 = i187.get("note") or ""
old_n = "★**4 处下游旧口径残留已清** (建议 6/7/8): `SW/DEMO_OD_TIMING_SPEC.md:194` 措辞 · `SW/tools/rknn_bench.py:257/261` 的 S9 标签 (★**与 `SW/RKNN_BENCH.md` §4.1 现在的 S9 标签同口径**★) · `SW/DEMO_OD_PIPELINE_SPEC.md:447` 的悬空引用 (指向 §⑤ 判据表) ⇒ ★**四处都只改口径措辞, 一个数字没动**。"
new_n = "★**4 处下游旧口径残留已清** (建议 5/6/7/8): `PROJECT_TRACKER.md:2098` 加取代标记 · `SW/DEMO_OD_TIMING_SPEC.md:194` 措辞 · `SW/tools/rknn_bench.py:257/261` 的 S9 标签 (★**与 `SW/RKNN_BENCH.md` §4.1 现在的 S9 标签同口径**★) · `SW/DEMO_OD_PIPELINE_SPEC.md:447` 的悬空引用 (指向 §⑤ 的**可测判据**) ⇒ ★**四处都只改口径措辞, 一个已发布数字没动** ⇒ ★**实测 4 个文件 md5 见 fix_ref**。"
if old_n in n187:
    i187["note"] = n187.replace(old_n, new_n)
    changed.append("ISS-187: note 里残留项补上 :2098 (原来只列了 3 处, 实际 4 处)")
elif new_n in n187:
    print("ℹ️ ISS-187 note 已是订正版 (幂等)")
else:
    print("⚠️ ISS-187 note 里没找到预期的旧串 ⇒ note 那段先不动 (fix_ref 已订正)")

if not changed:
    print("⚠️ 没有任何改动")
    sys.exit(0)

fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
    os.replace(tmp, LOG)
except Exception:
    if os.path.exists(tmp):
        os.unlink(tmp)
    raise

print("✅ 已原子写 issue_log.yaml:")
for c in changed:
    print("   -", c)
