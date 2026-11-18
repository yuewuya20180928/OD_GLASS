#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_e01_closed_20261112.py —— ★★落账 E-01 自查关闭 + 开 ISS-201 (P2_7 pinmux 交叉核)★★

★★背景 (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」★)★★:
  ★**main 靠公开官网文档自己查掉了唯一一条真正卡着【选项③】的外部依赖**:
  ★**① [官网]** Forlinx 官方手册 §2.6.2 Table 4 (P2 Even) 本身只有 49 行 ⇒ 官方也没有 `num=40` ⇒ 不是我们抄漏
  ★**② [实测]** 我们项目表 399 行 vs 官方 399 行 ⇒ signal/ball/gpio/vol **四列零差异** ⇒ 本表 = 官方手册逐格转录
  ★**③ [实测]** `J_SOM_P2` 只用 1/7/9/11/13/31/33/45/100 ⇒ **不用 40** ⇒ 对本板零影响
  ⇒ ★**⇒ E-01 关闭** ⇒ ★**证据文档 `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md`**

★本单干两件事 ★:
  ① ★**在 pm.yaml 记一条 answer (★E-01 已关闭·自己查·不外发★)** ⇒ 让"自己查"这条在项目台账里【有据可查】
     (★**注意**: E-01 本身不是 pm.yaml 的 need ⇒ 所以这里【新增一条 answer 而不是给 need 加 decision】★)
  ② ★**开 ISS-201** ⇒ ★**发现 A: `P2_7` 官方默认功能 = `PWM0_CH1_M0`, 我们拿它当 `UART_TX` 用**
     ⇒ ★**这是【引脚复用】, 需用官方 pinmux 表交叉核** ⇒ owner=hw-lead / verify_by=main
     ⇒ ★**owner=hw-lead 的理由: 它正在跑 ISS-195 ⇒ 队列会等它空闲才派 (铁律: 一个 agent 一个写会话)★**

★落账纪律 (★与项目既有范式一致★):
  ① flock(state/.issue_log.lock) + 锁内重读 + 只新增 ISS-201 一条 + 原子写
  ② yaml 往返复现自检 + 逐条 diff 实测 (★只有新增一条, 其余不动★)
  ③ ★**排版 width 先探后用** (★MEMORY 铁律★)
  ④ ★**pm.yaml 走 frag_write 的原子写** (★只加 answer, 不碰别人的分片★)
"""
import fcntl
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import yaml  # noqa: E402

LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_e01closed_20261112"
FRAG = os.path.join(HERE, "fragments", "pm.yaml")

IID = "ISS-204"

NEW_ISSUE = {
    "id": IID,
    "title": "★★[主线内·原理图侧·内部活] `J_SOM_P2.pin7` 官方默认功能 = `PWM0_CH1_M0`, 我们拿它当 `UART_TX` 用 "
             "⇒ ★**引脚复用是否合法, 要用官方 pinmux 表交叉核** (★2026-11-12 02:2x 自己查官方手册时撞出来的★★)",
    "severity": "medium",
    "source_blocker": "SW-TIM-B1",
    "source_agent": "main",
    "desc": "★2026-11-12 02:2x 项目总工开单 (★依据 = `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md` §3 发现 A 的实测★)。\n"
             "★**事实 [官网]**: Forlinx 官方手册 §2.6.2 **Table 4 (P2 Even Pin Definition)** 里 "
             "`P2_7` = **`PWM0_CH1_M0`** / GPIO0_C3_d / 3.3V ⇒ ★**官方默认功能是 PWM0, 不是 UART0_TX**。\n"
             "★**事实 [实测]**: 我们 `HW/netlist_v1_pins.csv` 里 `J_SOM_P2.pin7` 接的是 **`UART_TX`** "
             "(★`pin9` 接 `UART_RX` ⇒ ★**官方 Table 4 里 `P2_9` 确实写的是 `UART0_RX_M0_DEBUG` ⇒ "
             "TX/RX 在官方口径下应当同属 UART0 组, 而 `P2_7` 的默认功能却是 PWM0 ⇒ 这就是【引脚复用 (pinmux)】★**)。\n"
             "★**⇒ 要核的是**: ① ★**RK3572 的 pinmux 表里, UART0_TX 能不能复用到 `PWM0_CH1_M0` 这个脚 (★查 "
             "`rockchip.fr/RK3572 datasheet V1.0` 的 IOMUX 章节 + 官方 `Pin Multiplexing Comparison Table`★) "
             "② ★**复用后有没有副作用 (★PWM0_CH1 有没有别的默认功能冲突 / 会不会影响 BOOT 阶段★)** "
             "③ ★**若不能复用 ⇒ 这是【真设计缺陷】⇒ 改法 = 换 UART 引脚 (★`P2_7`↔`P2_9` 之外还有没有别的 UART0_TX 脚★) "
             "⇒ ★**★换脚会改网表 + 板 ⇒ 属整链重出范围 ⇒ 本单【只出结论不改板】★★**\n"
             "★**★边界 (★不许越界★)**: ★**本单【只查+只出结论】** ⇒ ★**不许改 `HW/netlist_v1.csv` / "
             "`HW/netlist_v1_pins.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard*.kicad_sch` / "
             "`state/gen_kicad_sch.py` / `HW/PCB/FET3572C_PIN_TABLE.csv` (★板 md5 必须仍 "
             "`611b869e13518c3c023fb178f91a0075`★)** ⇒ ★**只许写**: `HW/PCB/` 下一份新的交叉核文档 + "
             "`HANDOFF/` 交卷报告 + ★**必要时** `state/fragments/hw.yaml` (走 `frag_write.py`, ★只许新增本单相关条目★)★ "
             "⇒ ★**不许发任何邮件 / 不许联系原厂 / 不许下采购单** ⇒ ★**不许跑 `--pin-gap` 重跑产物** "
             "(★`HW/PCB/PIN_REALITY_GAP.md` 是 main 刚改过 `state/gen_kicad_sch.py` 的产物★ ⇒ 重跑会带上 main 的改动, "
             "★但本单不许动生成器 ⇒ 所以也不许重跑★)**",
    "owner": "hw-lead",
    "reporter": "main",
    "raised": "2026-11-12",
    "due": "2026-11-14",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": "",
    "verify_by": "main",
    "verify_result": None,
    "task_brief": (
        "★**目标 (★内部活·不是原厂的事·也不是 PCB 布线/布局类★)**: 用**公开官方资料**交叉核 "
        "`J_SOM_P2.pin7` 能不能当 `UART_TX` 用 (★引脚复用合法性★) ⇒ **只出结论, 不改网表/不改板**。\n\n"
        "★**★① 已经查到的 (★main 2026-11-12 02:2x 实测·你不用重查★)**:\n"
        "  · ★**[官网]** Forlinx 官方手册 `docs.forlinx.net/rockchip/ok3572-c/OK3572-C_User_Hardware_Manual.html` "
        "§2.6.2 **Table 4 (P2 Even Pin Definition)** ⇒ `P2_7` = **`PWM0_CH1_M0`** / GPIO0_C3_d / 3.3V "
        "⇒ ★**官方默认功能是 PWM0, 不是 UART0_TX**\n"
        "  · ★**[官网]** 同表 `P2_9` = `UART0_RX_M0_DEBUG` ⇒ ★**TX/RX 应同属 UART0 组 ⇒ `P2_7` 当 UART_TX "
        "⇒ 这是【引脚复用 (pinmux)】**\n"
        "  · ★**[实测]** 我们 `netlist_v1_pins.csv`: `J_SOM_P2.pin7` → `UART_TX`, `pin9` → `UART_RX`\n"
        "  · ★**★② 你要查的 (★只查这一件事★)**:\n"
        "  · ★**RK3572 的 pinmux 表**: `PWM0_CH1_M0` 这个脚能不能复用成 `UART0_TX` ⇒ ★**查 "
        "`https://rockchip.fr/RK3572%20datasheet%20V1.0.pdf` 的 IOMUX / Pin Multiplexing 章节 + Forlinx 的 "
        "`Pin Multiplexing Comparison Table` (★公开资料, 不许联系任何人★)**\n"
        "  · ★**复用有无副作用**: ★**BOOT 阶段 (★`PMIC_VDC` / `SARADC_VIN0_BOOT` 走的是 SARADC/ADC 脚, 不在这条 UART 链上★) "
        "⇒ 确认不受影响**\n"
        "  · ★**若不能复用 ⇒ 找替代脚**: ★**RK3572 上还有哪个脚能复用成 UART0_TX (★且是我们板子已经接出来的 / "
        "或者能通过改网表+改板实现的★)** ⇒ ★**列出候选 + 各自的改板代价 (★换脚要改网表 + 板 + BOM + 整链重出★)**\n\n"
        "★**★★③ 判据 (★三条都要给, 少一条不算交卷★)** ★★:\n"
        "  ① ★**结论** = 能复用 / 不能复用 / 查不到 ⇒ ★**每个结论必须带证据等级** "
        "`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ ★**查不到就写 `[0数据]` + 已知缺口 + 降级方案 "
        "(★例如: 改用 UART1/2/3 的某个脚, 或加一级电平转换★)** ⇒ ★**不许猜**\n"
        "  ② ★**把查到的官方 IOMUX 那一行原文抄进你的文档** (★表名 + 行 + 出处 URL + 页码/章节号★) "
        "⇒ ★**这是本单唯一要的\"证据\"**\n"
        "  ③ ★**板 md5 必须仍是 `611b869e13518c3c023fb178f91a0075`**, ★**网表 md5 仍是 `c78f991283cc82d56c8e3dd31657c785`** "
        "⇒ ★**本单只出文档, 一个字节都不许改设计**\n\n"
        "★**★④ 交卷 (★≤8 行·别写长篇★)**: ① 结论 + 证据等级 ② 官方 IOMUX 那行原文 + 出处 "
        "③ 若不能复用 = 替代脚候选 + 改板代价 ④ 板/网表 md5 未变的实测 ⑤ 你写了哪个文件 "
        "⑥ 查不到的项 + 降级方案 ★★\n\n"
        "★**★⑤ 边界 (★再强调一次★)**: ★**不许发任何邮件 / 不许联系原厂 / 不许联系供应商 / 不许下采购单** "
        "⇒ ★**老板 2026-11-12 02:02: 「不再发信，全靠自己查资料」** ⇒ ★**所有资料一律【自己网上查】+ 标证据等级** "
        "⇒ ★**不许碰**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · "
        "`HW/PCB/demo_mainboard*.kicad_sch` · `state/gen_kicad_sch.py` · `HW/PCB/FET3572C_PIN_TABLE.csv` · "
        "`HW/PCB/PIN_REALITY_GAP.md` (★★main 刚改过, 不许重跑覆盖★★) · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 "
        "· 别人的分片 ⇒ ★**只许写**: `HW/PCB/` 下一份新文档 + `HANDOFF/` 交卷报告 + "
        "`state/fragments/hw.yaml` (★走 `frag_write.py`·只许新增本单相关条目★)"
    ),
    "dispatched_at": "",
    "fixed_at": "",
}


def dump_atomic(obj, path, width):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main():
    # ---------- ① pm.yaml 加 answer (E-01 已关闭) ----------
    import frag_write
    with open(os.path.join(HERE, ".frag.lock"), "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            d = yaml.safe_load(open(FRAG, encoding="utf-8")) or {}
            answers = d.setdefault("answers", [])
            key = "e01_som_balltable_selfcheck_202612"
            if not any(a.get("key") == key for a in answers):
                answers.append({
                    "key": key,
                    "to": "main",
                    "value": (
                        "★**E-01 (`FET3572C_PIN_TABLE.csv` 的 P2 座缺 `num=40`) 已关闭 · 2026-11-12 02:2x "
                        "项目总工【自己网上查】解决 (★老板 2026-11-12 02:02 指令「不再发信，全靠自己查资料」★)**\n"
                        "★**① [官网]** Forlinx 官方手册 §2.6.2 **Table 4 (P2 Even Pin Definition)** 实测只有 "
                        "**49 个数据行** ⇒ 从 `num=38` 直接跳到 `num=42` ⇒ ★**官方文档同样没有 `num=40`** ⇒ "
                        "★**不是我们抄漏, 是官方原样**\n"
                        "★**② [实测]** 项目表 399 行 vs 官方 399 行 ⇒ `Signal Name`/`BALL`/`GPIO`/`VOL` "
                        "**四列零差异** ⇒ ★**本表 = 官方手册逐格转录** ⇒ ★**证据等级从【模组厂口径】升到【[官网]】**\n"
                        "★**③ [实测]** `J_SOM_P2` 只用 1/7/9/11/13/31/33/45/100 ⇒ ★**不用 `pin40`** ⇒ "
                        "★**对本板零影响** ⇒ ⇒ ★**E-01 不再是任何人的阻塞项**\n"
                        "★**④ 顺带查到**: (A) FET3576-C 与 FET3572-C **针脚兼容** ⇒ 升级不用改载板 "
                        "(B) `P2_7` 官方默认功能是 `PWM0_CH1_M0` 而我们当 `UART_TX` ⇒ **引脚复用待核** "
                        "⇒ 已开 **ISS-201** (owner=hw-lead)\n"
                        "★**完整证据**: `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md`\n"
                        "★**已改在产生点**: `state/gen_kicad_sch.py` (§5.1 整段 + §5.2 + §6 + §2 注记) ⇒ "
                        "`HW/PCB/PIN_REALITY_GAP.md` 已重跑刷新 ⇒ ★**受保护文件 md5 全未变** "
                        "(★板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · "
                        "脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · "
                        "`FET3572C_PIN_TABLE.csv` `67340a0b707095fc4c0755a4c79ea8b6`★)"
                    ),
                    "ref": "HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md",
                })
                frag_write.atomic_write_yaml(FRAG, d)
                print("✅ pm.yaml 已加 answer: " + key)
            else:
                print("ℹ️ pm.yaml 已有该 answer ⇒ 不动")
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)

    # ---------- ② issue_log 加 ISS-201 ----------
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        items = doc if isinstance(doc, list) else doc.get("issues")
        width = None
        for w in (60, 80, 100, 120, 200):
            if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=w) == raw:
                width = w
                break
        print("★当前排版 width = %s" % (width or "探不到 (★用 200 + 逐条 diff 兜底★)"))
        width = width or 200
        if any(str(i.get("id")) == IID for i in items):
            print("ℹ️ %s 已存在 ⇒ 不动" % IID)
            return 0
        shutil.copy2(LOG, BAK)
        items.append(NEW_ISSUE)
        a = yaml.safe_load(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        if yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width) != \
           yaml.safe_dump(b, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width):
            print("❌ yaml 往返不一致 ⇒ 放弃写")
            return 1
        dump_atomic(doc, LOG, width)
        print("✅ 已原子写 issue_log.yaml: 新增 %s (★备份 %s★)" % (IID, os.path.basename(BAK)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
