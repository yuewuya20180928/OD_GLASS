#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1545_redispatch_iss243_zombie.py
★main (moli) 2026-11-16 15:4x (cron 775d9893 ARS45 继续执行后继计划)★
★**只把 ISS-243 的 task_brief 改成【续做重派】版 (上一轮零产出僵尸) ★**

★★★**为什么必须重派 (★main 本轮自己实跑, 不抄任何交卷报告★) ★★★
· ★**会话**: `agent:hw-lead:subagent:337705c2` (session bdf0ab5c) · 15:15:04 起 · 15:24:10 止 · runtime 546s · ★**status=timeout / abortedLastRun=true** ★
· ★**盘上零产出 (main 实测 ls + md5)**: `HW/MOS_PAD_PIN_MAPPING.md` **不存在** · `HANDOFF/2026-11-16_hw-lead_ISS243_*.md` **不存在** ·
  ★**4 个受保护 md5 与 15:1x 基线逐字节相同** (网表 34132f7e… / 脚表 b21b743a… / BOM c195a117… / 板 611b869e…) ⇒ ★**L1 落表也没发生** ★
· ★**上一轮干到哪 (★main 读会话 transcript 实测, 不是猜★)**: 48 次 exec + 8 次 read + 3 次 write (★**写到 /tmp, 没写项目目录★**) + 2 次 web_search + 2 次 web_fetch;
  ★**死在「Murata 官方在售型号 GRM21BR71C475KA73L / GRM188R71H475KA73D 抓不到」(官网 404 + curl 长跑)★ ⇒ 也就是 L1 的第③小项 (OPN 栏) ⇒ ★**9 分钟全花在内存里, 盘上零产出** ★
· ★**hw-lead 现在没有运行中的写会话** ⇒ ★**可安全重派 (铁律「一个 agent 同时只允许一个写会话」不冲突★)** ★

★★**本脚本的边界★★ ★
· ★**只写 `state/issue_log.yaml`** (只改 ISS-243 一条的 task_brief + note) ★
· ★**不改任何交付物文件 / 网表 / 脚表 / BOM / 板 / 分片 / dispatch_log / PROJECT_TRACKER §0** ★
· ★**零外发** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
IL_LOCK = os.path.join(HERE, ".issue_log.lock")

REDISPATCH_243 = (
    "★**续做派活 (★main 2026-11-16 15:4x 实测: 上一轮会话 15:15:04~15:24:10 撞 timeout (runtime 546s · abortedLastRun=true · status=timeout) "
    "⇒ ISS-243 是【零产出僵尸】★) ⇒ ★**本轮重派 · runTimeout 5400s** ★**\n"
    "★★**上一轮到底干到哪 (★main 读会话 transcript 实测, 不是猜★) ★★\n"
    "· ★**会话**: `agent:hw-lead:subagent:337705c2` (session bdf0ab5c) · 48 exec + 8 read + 3 write + 2 web_search + 2 web_fetch ★\n"
    "· ★**盘上零产出 (main 实测)**: `HW/MOS_PAD_PIN_MAPPING.md` 不存在 · `HANDOFF/2026-11-16_hw-lead_ISS243_*.md` 不存在 · "
    "★**网表/脚表/BOM/板 4 个 md5 与 15:1x 基线逐字节相同 (34132f7e / b21b743a / c195a117 / 611b869e) ⇒ L1 落表也没发生** ★\n"
    "· ★**上一轮死在哪**: ★**卡在「Murata 官方在售型号 GRM21BR71C475KA73L / GRM188R71H475KA73D 抓不到」(官网 404 + curl 长跑) ⇒ 也就是 L1 的第③小项 (OPN 栏)** ★ "
    "⇒ ★**结论: 上一轮把 9 分钟全花在「必须联网才能定的那一个型号」上 ⇒ 盘上零产出** ★\n"
    "★★**本轮怎么干 (★main 给的顺序建议, 不是重写任务书★) ★★\n"
    "· ★**① 先落盘再研究** ⇒ ★**第一件事 = 把 4 件交付物的骨架先建起来** (① `HW/MOS_PAD_PIN_MAPPING.md` ② 新建的门禁脚本 ③ 交卷单 ④ 分片) ⇒ ★**再往里填** ⇒ "
    "★**这样就算再撞 timeout, 盘上也有半成品, 下一轮不用从零开始 (★上一轮的教训: 9 分钟全在内存里, 盘上零产出★)** ★\n"
    "· ★**② L1 落表优先做「不依赖联网」的那部分**: ★**`C_REGN` 的 value 三处订正 (网表 L44/L45 + 脚表 `C_REGN` 行 + BOM `C_REGN` 行) → `4.7µF ±10% (10V)` + 备份 + 落表台账登记 + 4 道闸** "
    "⇒ ★**这部分只需读盘, 立刻能落, 价值最高** ⇒ ★**先落它, 再去查 OPN** ★\n"
    "· ★**③ OPN 那一条 (L1③) 的口径**: ★**官网在售页抓不到是常态 ⇒ 不许再卡在这** ⇒ ★**给 ≥2 个官方在售候选 (各自标 [官网] 出处 + 耐压/封装/介质) + 查不到就写 [0数据] + 降级方案 (按官方参数直接满足的替代型号 / 改设计路径绕开) ★** "
    "⇒ ★**OPN 栏不许留空 (留空 = 采购单出不来 = 门禁 C2 红), 但也不许为「查证」把整轮时间耗光** ★\n"
    "· ★**④ L2/L3 离线可做** ⇒ ★**板文件就在盘上 (`HW/PCB/demo_mainboard.kicad_pcb`), 实读 pad 号/net/尺寸即可, 一行都不用联网** ⇒ ★**这两条应当先做完** ★\n"
    "· ★**⑤ L4 (充电板 6 件 footprint 候选) 需要查官方在售** ⇒ ★**每件给 ≥2 候选 + 焊盘数 + 本体尺寸 + 出处 + 证据等级 + 降级方案** ⇒ ★**查不到的写 [0数据], 不许写「等回复」** ★\n"
    "· ★**⑥ 抓取纪律照旧**: `web_search` / `web_fetch` + ★**带 `--max-time` 的 curl** (★本机上一轮 curl 长跑卡死过★) + `pdftotext` 实读 ⇒ ★**单次 curl 最多 30~40s, 抓不到就换源或写降级方案, 不许死磕** ★\n"
    "· ★**⑦ 门禁 + --selftest 先写再补正文** ⇒ ★**先写门禁 (≥5 条断言) 再补收口页**, 这样边补边能跑 rc ★\n"
    "· ★**⑧ 交卷前必须跑 `python3 state/merge.py` (rc=0) && `python3 state/gate_check.py` (【Q1】18/18) 并把输出贴进交卷单** ★\n"
    "★**其余边界一个字没变**: 零外发 · 只许改 `C_REGN` 那几行 (L1) · 不许改板/布线/布局/板框 · 不许改脚表里别的器件 · 不许改 `state/land_v_values.py` · "
    "不替老板拍板 (V-2/V-3/V-4/G-1/W-1~W-6 一条不许代拍) · 不许自己改 `state/issue_log.yaml` · 实物 [实测] = 0 条 ★\n"
)

NOTE_243 = (
    "\n\n★2026-11-16 15:4x (cron 775d9893 继续执行后继计划) ★**上一轮会话 15:15:04~15:24:10 撞 timeout (runtime 546s · abortedLastRun=true) ⇒ "
    "盘上零产出 (MOS_PAD_PIN_MAPPING.md / 交卷单 / 门禁 三件一件没落 · 网表脚表 BOM 板 4 个 md5 逐字节未变) ⇒ 僵尸 fixing ⇒ 本轮改成【续做重派】brief 并重派** ★"
    "\n· ★**上一轮死在哪**: 卡在 Murata 官方在售型号 (C_REGN 的 OPN 栏) 抓不到 ⇒ 9 分钟全在内存里 ★"
    "\n· ★**本轮要求**: 先落盘骨架再填内容 · L1 落表 (不依赖联网) 先做 · OPN/L4 查不到就写 [0数据] + 降级方案, 不许死磕 ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(IL, IL + ".bak_20261116_1545_redispatch_iss243_zombie")

    lf = open(IL_LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        issues = il.get("issues") or []
        by_id = {it.get("id"): it for it in issues}

        it = by_id.get("ISS-243")
        if not it:
            raise SystemExit("★ISS-243 不存在 ⇒ 中止")
        if it.get("status") != "fixing":
            raise SystemExit("★ISS-243 status=%s (不是 fixing) ⇒ 中止" % it.get("status"))
        b = it.get("task_brief") or ""
        if "★**续做派活" in b:
            print("   - ISS-243 brief 已是【续做重派】版 ⇒ 不重复加")
            return 0
        it["task_brief"] = REDISPATCH_243 + b
        it["note"] = (it.get("note") or "") + NOTE_243

        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()

    print("   - ISS-243 brief 改成【续做重派】版 (零产出僵尸 · 先落盘骨架 · L1 落表优先 · 查不到写降级方案)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
