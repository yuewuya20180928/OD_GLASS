#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0605_brief_newmarker_229_230.py
★main (moli) · 2026-11-16 06:05 · cron fb67af40 (队列自动派活)★

★★**为什么做这件事 (★派活前命令存在性闸点名的两条 brief·纯文本卫生·不是改活★)** ★★
· `python3 state/check_brief_commands.py` 实测点出:
  ❌ ISS-229: `HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md` 不存在
  ❌ ISS-230: `HANDOFF/2026-11-16_hw-lead_ISS230_第3批作业包v2与加强断言.md` 不存在
· ★**这两条【不是命令, 是本单的产出文件 (交接单)】** ⇒ 闸按「同句 30 字内出现 新建/产出/交付物… ⇒ 视为产出物, 豁免」★
  ⇒ ★**缺的是闸约定的显式声明** ⇒ ★**补一句「★新建★ 本单产出」** ⇒ 闸下次不再误报 ★
· ★**做法 = 原文级定点替换 (不用 yaml round-trip) ⇒ 除那两处字符串外, 文件其余部分逐字节不变** ★
★**不做的事**: ★**不改 status / 不改 owner / 不改任何活内容 / 不碰别人的分片 / 不碰板与网表 / 零外发** ★
"""
import os
import shutil
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
STAMP = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

# ★★**两处定点替换 (左 => 右)★★**
PATCHES = [
    ("★**交接单** `HANDOFF/2026-11-16_mech-lead_ISS229_",
     "★**交接单 (★新建★ 本单产出)** `HANDOFF/2026-11-16_mech-lead_ISS229_"),
    ("★**交接单** `HANDOFF/2026-11-16_hw-lead_ISS230_",
     "★**交接单 (★新建★ 本单产出)** `HANDOFF/2026-11-16_hw-lead_ISS230_"),
]


def main() -> int:
    if not os.path.exists(LOG):
        print("❌ issue_log.yaml 不存在")
        return 1
    bak = os.path.join(HERE, "issue_log.yaml.bak_briefmarker_%s" % STAMP)
    shutil.copy2(LOG, bak)
    raw = open(LOG, "r", encoding="utf-8").read()
    before_len = len(raw)

    new = raw
    hits = []
    for old, rep in PATCHES:
        n = new.count(old)
        hits.append((old, n))
        if n != 1:
            print("❌ 定位失败 (期望恰好 1 处, 实得 %d): %s" % (n, old))
            return 2
        new = new.replace(old, rep)

    tmp = LOG + ".tmp_briefmarker"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)

    # ★回读验证: yaml 仍可解析 + 两处新标记在位 + status 没被碰★
    import yaml
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    ok = True
    for it in d["issues"]:
        if it.get("id") in ("ISS-229", "ISS-230"):
            b = it.get("task_brief") or ""
            has = ("★新建★ 本单产出" in b)
            print("  %s | owner=%s | status=%s | 新建标记在位=%s"
                  % (it.get("id"), it.get("owner"), it.get("status"), has))
            ok = ok and has
    print("备份: %s" % bak)
    print("字节: %d -> %d (Δ%+d)" % (before_len, len(new), len(new) - before_len))
    print("✅ 定点替换完成" if ok else "❌ 回读验证失败")
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
