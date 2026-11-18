#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 10:4x · job 775d9893「ARS45 继续执行后继计划」
★(1) 把「落表后的两处收口」追加进 ISS-283 (hw-lead) 的 task_brief + note★
★    ① `HW/check_onepass_preflight_coverage.py` rc=1 (P5 现状值过期 + P6 基线 md5 过期)★
★    ② `state/land_v_values.py --selftest` rc=1 (★V-3/V-4 已落 ⇒ 用例12 硬套补丁 ⇒ RuntimeError 崩★)★
★(2) 决策页 §A-补15 追加一段「落表后的两道闸现红 + 已派收口」(★如实报, 不许只报好消息★)★
★**纪律: 多行标量走「yaml 取旧值 → 拼新值 → 单行 json 写回 → 全量复核」★**
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
BAK_LOG = LOG + ".bak_20261117_1040_main_relay_283"
BAK_PAGE = PAGE + ".bak_20261117_1040_main_r53_gates"

RELAY = """

---

## ★★⑩ 追加 (★2026-11-17 10:4x main 实跑·落表的直接后果·这两件归你一起收口★★)

★**A1+A2 落表后, 有两道闸当场变红 —— 都是【落表的正常后果】, 但必须收, 不许留红★**

### ★① `HW/check_onepass_preflight_coverage.py` ⇒ **rc=1** (★落表前是 rc=0★)

```
  FAIL  P5
     5 个现状探针: 清单里的现状值 == 盘面实测: ❌
     ❌ B17_DNP_43: 盘面实测 = '零标记 40 颗', 但清单 current_state 里没有这个值 ⇒ 清单过期
     ❌ B03_ULDO_S28_PAD3: 盘面实测 = '18 条缺陷', 但清单 current_state 里没有这个值 ⇒ 清单过期
  FAIL  P6
     受保护 5 件 md5 逐字节不变: ❌
     ❌ 网表 md5 2f17650cfbef48d5efd71821505c3343 ≠ 基线 e06c1dd633566aa44732762c2ff99d1c
     ❌ 脚表 md5 6ea65fecdf95902e47330083d140d455 ≠ 基线 287e7861a0d1007748d92d9fbecdd490
     ❌ BOM  md5 ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd ≠ 基线 94642d07a69e8d60dd2af57f69b93607
```

★**⇒ 收口动作 (★两条, 不许用「改判据让它绿」的办法★)**:
- ★**P5 = 清单现状值跟着盘面改**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 里 `B17_DNP_43` 的 current_state → `零标记 40 颗` (★落表后 DEMO_DNP 少 3 颗★) · `B03_ULDO_S28_PAD3` 的 current_state → `18 条缺陷` (★落表后 `--expect-resolved` 只剩 4 条, 全是板侧★) ⇒ ★**闸自己写的正确姿势: 「盘面变了 ⇒ 现状值跟着改 ⇒ 再跑闸」** ★
- ★**P6 = 受保护基线重锚**: 网表 / 脚表 / BOM 三件的基线 md5 ⇒ 改成刚落表的真值 (`2f17650c…` / `6ea65fec…` / `ea5f4f58…`) ⇒ ★**必须留痕 (★走 H-1 四项: 落表单号 + 文件名 + 新旧 md5★) ⇒ 出处 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16** ★ ⇒ ★**板 `611b869e…` 与 `.kicad_pro 3e504d2b…` 两个基线不许动 (★它们本来就没变★)** ★
- ★**⇒ 改完必须 `python3 HW/check_onepass_preflight_coverage.py` rc=0 + `--selftest` rc=0 (★反向一条不许少★)** ★

### ★② `state/land_v_values.py --selftest` ⇒ **rc=1 (★是崩, 不是红★)**

```
  File "state/land_v_values.py", line 1896, in run_selftest
    plan12.apply_patches()
  File "state/land_v_values.py", line 1390, in apply_patches
    txt = replace_after(txt, p.ctx, p.old, p.new, p.count)
RuntimeError: ★旧值出现 0 次 (期望 1 次)
```

★**⇒ 根因**: 落表器自测的用例 12 假设 V-3/V-4 **还没落** ⇒ 落表后旧值不存在 ⇒ 硬套补丁 ⇒ 崩 ⇒ ★**落表器的「已落过」检测只覆盖了 V-2 (D_ESD_USB_D), 没覆盖 V-3 / V-4** ★
★**⇒ 收口动作**: ★**给 V-3 / V-4 也加「已落过」判定** (★像 V-2 那样: 已落 ⇒ 拒绝重落 + 文案写【已落过】★) ⇒ ★**用例 12 改成对【已落过】状态判红, 不许再硬套补丁** ⇒ ★**`--selftest` 必须回到 rc=0** ★
★**★顺带**: 你 B1 做的「合法落表改 net 名」通道, ★**也要顺手把 V-3/V-4 的「已落过」语义理清** (★「合法落表」与「重复落表」是两件事, 不许混★) ★
"""


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


def main() -> int:
    raw = open(LOG, encoding="utf-8").read()
    before = yaml.safe_load(raw) or {}
    bmap = {it["id"]: it for it in before.get("issues", [])}
    lines = raw.split("\n")

    def block_range(iid):
        start = end = None
        for i, ln in enumerate(lines):
            if ln.startswith("- id: "):
                if start is not None:
                    end = i
                    break
                if ln[len("- id: "):].strip() == iid:
                    start = i
        if start is None:
            return None, None
        if end is None:
            end = len(lines)
        return start, end

    def replace_scalar(iid, key, newval):
        s, e = block_range(iid)
        if s is None:
            print("❌ 找不到 %s" % iid)
            return False
        blk = lines[s:e]
        ki = None
        for j, ln in enumerate(blk):
            if ln.strip().startswith(key + ":"):
                ki = j
                break
        if ki is None:
            print("❌ %s 块内找不到 %s" % (iid, key))
            return False
        k = ki + 1
        while k < len(blk):
            ln = blk[k]
            if ln.startswith("- id: "):
                break
            ind = len(ln) - len(ln.lstrip(" "))
            if ind == 2 and ":" in ln:
                break
            k += 1
        blk[ki:k] = ["  %s: %s" % (key, q(newval))]
        lines[s:e] = blk
        return True

    old = bmap["ISS-283"]
    tb = old.get("task_brief") or ""
    if "⑩ 追加" not in tb:
        replace_scalar("ISS-283", "task_brief", tb + RELAY)
    nt = old.get("note") or ""
    if "落表的直接后果" not in nt:
        replace_scalar("ISS-283", "note", nt + (
            " ★**2026-11-17 10:4x 追加 (main)**: A1+A2 落表后有【两道闸当场变红】(★都是落表的正常后果, 但必须收★): "
            "① `HW/check_onepass_preflight_coverage.py` **rc=1** ⇒ P5 两个现状探针过期 (B17_DNP_43 → 「零标记 40 颗」/ B03_ULDO_S28_PAD3 → 「18 条缺陷」) + "
            "P6 三个受保护基线 md5 过期 (网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…`) ⇒ ★**收口 = 清单现状值跟着盘面改 + 基线走 H-1 四项重锚 (★出处 = 落表台账 §16★)** ★ "
            "② `state/land_v_values.py --selftest` **rc=1 (崩)** ⇒ 用例 12 硬套 V-3/V-4 的补丁而旧值已不存在 ⇒ ★**落表器的「已落过」检测要覆盖 V-3/V-4** ★ ⇒ "
            "★**任务书已追加「⑩ 追加」节 (含原样 rc 与收口动作)★** ★"))

    out = "\n".join(lines)
    shutil.copy2(LOG, BAK_LOG)
    open(LOG, "w", encoding="utf-8").write(out)

    # 决策页追加
    page_add = """
### ★★⑤ 追加 (★2026-11-17 10:4x main 实跑·★落表后有两道闸当场变红★)

★**如实报 (★不许只报好消息★)**: ★**A1+A2 落表后, 两道闸变红 —— 都是落表的正常后果, 已在 ISS-283 (hw-lead) 的任务书里追加了收口动作, 责任已落到单上★**

| 闸 | 现象 | 收口 (★已在 ISS-283 任务书「⑩ 追加」节★) |
|---|---|---|
| ★**`HW/check_onepass_preflight_coverage.py`** ★ | ★**rc=1** ⇒ P5 两个现状探针过期 (★DNP 零标记 40 颗 / 缺陷 18 条★) + P6 三个受保护基线 md5 过期 (★网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…`★) | ★**清单现状值跟着盘面改 + 基线走 H-1 四项重锚 (★出处 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16★)** ⇒ ★**板 `611b869e…` 与 `.kicad_pro 3e504d2b…` 两个基线本来就没变, 不许动** ★ |
| ★**`state/land_v_values.py --selftest`** ★ | ★**rc=1 (是崩不是红)** ⇒ 用例 12 硬套 V-3/V-4 的补丁, 而旧值已落表不存在 ⇒ `RuntimeError: 旧值出现 0 次` | ★**落表器的「已落过」检测要覆盖 V-3 / V-4** (★V-2 早有, 这两个没有★) ⇒ 用例 12 改成对【已落过】判红 ⇒ `--selftest` 回 rc=0 |

"""
    ptxt = open(PAGE, encoding="utf-8").read()
    if "⑤ 追加 (★2026-11-17 10:4x main 实跑·★落表后有两道闸当场变红★)" not in ptxt:
        shutil.copy2(PAGE, BAK_PAGE)
        marker = "\n> ★**本节数字的出处 (★可复核★)**: 落表 rc 与台账"
        if marker in ptxt:
            ptxt = ptxt.replace(marker, page_add + marker, 1)
        else:
            ptxt = ptxt.rstrip("\n") + "\n" + page_add
        open(PAGE, "w", encoding="utf-8").write(ptxt)
        print("✔ 决策页已追加 ⑤")
    else:
        print("⚠ 决策页 ⑤ 已存在 ⇒ 不重复追加")

    # 复核
    after = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    amap = {it["id"]: it for it in after.get("issues", [])}
    ok = True
    for iid, it in bmap.items():
        a = amap.get(iid, {})
        for k, v in it.items():
            if iid == "ISS-283" and k in ("note", "task_brief"):
                continue
            if a.get(k) != v:
                print("❌ %s 的 %s 变了" % (iid, k))
                ok = False
    print("  ISS-283 task_brief 含⑩ =", "⑩ 追加" in (amap["ISS-283"].get("task_brief") or ""))
    print("  其余 issue 全部字段逐字相同 =", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
