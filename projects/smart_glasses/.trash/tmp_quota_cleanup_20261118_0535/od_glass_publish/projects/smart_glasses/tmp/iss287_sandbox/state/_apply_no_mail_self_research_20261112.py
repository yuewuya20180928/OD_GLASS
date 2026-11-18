#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_no_mail_self_research_20261112.py —— ★★老板 2026-11-12 02:02 指令落源头★★

★★老板原话 (★2026-11-12 02:02★): 「不再发信，全靠自己查资料」★★
  ★**比 19:31 那条更彻底**: 19:31 是「不再做任何邮件咨询」(★只说【不发】★)
  ⇒ 今天这条补上了【替代方案是【自己查】, 不是【干等】】★ ⇒ ★**所有"等回信"的外部依赖必须当场换成"自己查"的任务★**

★为什么必须落源头 (★MEMORY 铁律★):
  ★**决策必须登记在源头** ⇒ 只在文档里写一遍 = 下次刷新就被冲掉 = 假落实
  ⇒ ★**`state/fragments/pm.yaml` 的 `needs_from` 是 C 段决策项的唯一真源** ⇒ 落这里

★本单干三件事 (★只碰 pm.yaml 一个文件★):
  ① ★**退休 C 段最后 1 条还在挂"请你放行外发"的条目**: `iss105_jchg_rfq_release`
     (★它在 hw.yaml 分片里 · 但【决策是全局事实】⇒ 按 decision_truth 机制,
       记在 pm.yaml 里的 decision 会让【所有分片】的同 key 条目一起被闭合★)
     ⇒ ★**它还要求"要不要给采购动作单独开一次豁免" ⇒ 老板今天这句直接把它回答了: 不发 ⇒ 豁免不成立 ★**
  ② ★**新增 1 条"自己查"的顶层口径条目** ⇒ 把"全靠自己查资料"变成 C 段里一条**可查、可追的活**
     (★不是一句口号 ⇒ 落成 needs_from 条目 ⇒ 老板清单上看得见★)
  ③ ★**`bridge_chip_quote`** (★pm.yaml 里唯一一条还在问"要不要启动询价"★)
     ⇒ 询价 = 外发 ⇒ 退休 ⇒ 改为【自己网上查规格 + 公开渠道比价】

★落账纪律:
  ① ★**用 `state/frag_write.py` 的原子写** (★tmp + fsync + os.replace★)
  ② ★**先备份** `pm.yaml` ⇒ 逐条 diff 实测 ⇒ 只应有 3 处变化
  ③ ★**写完立刻复跑 `advance.py --json` ⇒ C 段条数应变 36 → 35** (★iss105 那条被闭合★)
     ⇒ ★**并实测 `iss105_jchg_rfq_release` 不再出现在老板清单上★**
  ④ ★**不许碰 hw.yaml / sw.yaml / mech.yaml** (★那是三个总工的分片 ★ 而且 hw-lead 正在跑单★)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import yaml  # noqa: E402

FRAG = os.path.join(HERE, "fragments", "pm.yaml")
BAK = FRAG + ".bak_20261112_0202_selfresearch"


def load(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    # ---- 锁内重读 + 备份 ----
    import fcntl
    lock = open(os.path.join(HERE, ".frag.lock"), "a+")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        d = load(FRAG)
        before = yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100)
        needs = d.setdefault("needs_from", [])
        keys = {n.get("key") for n in needs}

        NEW = []

        # ---- ① 退休 C 段最后一条"放行外发" ----
        KEY1 = "iss105_jchg_rfq_release"
        DEC1 = (
            "★老板 2026-11-12 02:02 决定: ★**「不再发信, 全靠自己查资料」** ⇒ ★**J_CHG 询价函"
            "`state/outbox/j_chg_rfq.md` 不发, 也不申请采购动作豁免** ⇒ ★**该条外部依赖改为【自己网上查】**: "
            "① Hirose FH12-22S-0.5SH(55) 等候选的**官网规格书** (单触点额定电流 / 可插厚度 / 防呆结构 / 座高) "
            "② **公开分销渠道页面**的单价与交期 (★只作参考区间, 不下单★) "
            "③ 查不到的项 (★如「可插厚度 ≥0.25mm」这种只有实测能定的★) ⇒ ★**如实标 `[0数据]` + 记为已知缺口 + 给降级方案** "
            "(★降级 = 按实测样件验证, 或选一个官网参数能直接满足的替代型号★) ⇒ ★**从待拍板清单退休**★"
        )
        if KEY1 in keys:
            for n in needs:
                if n.get("key") == KEY1 and not n.get("decision"):
                    n["decision"] = DEC1
                    n["decided_at"] = "2026-11-12"
                    n["decided_by"] = "boss (2026-11-12 02:02)"
                    NEW.append("① 退休 " + KEY1)
        else:
            NEW.append("① pm.yaml 里没有 " + KEY1 + " (★它只在 hw.yaml ⇒ 靠 decision_truth 的全局决策闭合★)")

        # ---- ② 退休 bridge_chip_quote (询价 = 外发) ----
        KEY2 = "bridge_chip_quote"
        DEC2 = (
            "★老板 2026-11-12 02:02 决定: ★**「不再发信, 全靠自己查资料」** ⇒ ★**DP→MIPI-DSI 桥接芯片询价不再启动** "
            "(★询价 = 外发 = 一律不发★) ⇒ ★**改为【自己网上查】**: ① 芯片规格书 (★桥接能力 / MIPI DSI 输入输出 lane 数与速率 / "
            "工作电压 / 封装★) ② **公开渠道单价与交期** (★只作选型参考, 不询价不下单★) "
            "③ 查不到 ⇒ ★**标 `[0数据]` + 记为已知缺口 + 给降级方案 (★例如: 改走 SoM 自带 MIPI DSI 输出, 不加桥接芯片★)** "
            "⇒ ★**从待拍板清单退休**★"
        )
        if KEY2 in keys:
            for n in needs:
                if n.get("key") == KEY2 and not n.get("decision"):
                    n["decision"] = DEC2
                    n["decided_at"] = "2026-11-12"
                    n["decided_by"] = "boss (2026-11-12 02:02)"
                    NEW.append("② 退休 " + KEY2)
        else:
            NEW.append("② pm.yaml 里没有 " + KEY2)

        # ---- ③ 新增"自己查资料"顶层口径条目 ----
        KEY3 = "self_research_policy_202612"
        ITEM3 = (
            "★★【老板 2026-11-12 02:02 新口径】**不再发信, 全靠自己查资料** ★★\n"
            "★**替代 19:31 那条「不再做任何邮件咨询」** ⇒ ★**19:31 只说了【不发】, 今天补上了【发不发都不重要, "
            "因为我们自己能查】** ★\n"
            "★★**具体口径 (★全部由项目总工/各总工自己执行, 不用老板批★)** ★★:\n"
            "★**① 查什么**: 芯片/器件/模组的**规格与球位/引脚定义**、**pinout / 封装尺寸 / 电气参数**、"
            "**公开渠道单价与交期** (★只作参考区间, 不询价不下单★)、**公开 dts / BSP / 社区实测**\n"
            "★**② 证据等级 (★每个数必须带等级★)**: `[官网]` (★厂商官网/官方 datasheet★) · `[实测]` (★本机可复现★) · "
            "`[媒体]` (★媒体/社区/论坛★) · `[推算]` (★由已知量推★) · `[0数据]` (★查不到★)\n"
            "★**③ 查不到怎么办**: ★**如实标 `[0数据]` + 记为【已知缺口】+ 给【降级方案】** ⇒ ★**不许拿\"等回信\"挂着, "
            "也不许拿\"同类器件一般多少\"去填** ⇒ ★**降级方案例子**: 实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开它\n"
            "★**④ 边界**: ★**`state/outbox/` 全部草稿一律不发, 只留档** ⇒ ★**不许再拿「老板批一句可以发」当流程**\n"
            "★★**这一条是【可追的活】, 不是口号**: ★**它要求把项目里所有还写着「等原厂回信 / 等外部回复」的地方, "
            "逐条换成【自己查的结果 + 证据等级】** ⇒ ★**谁改的、查了什么、结论是什么, 都要落到具体文档里★★"
        )
        if KEY3 not in keys:
            needs.append({
                "key": KEY3,
                "to": "boss",
                "item": ITEM3,
                "since": "2026-11-12",
                "due": "2026-11-14",
            })
            NEW.append("③ 新增 " + KEY3)
        else:
            NEW.append("③ " + KEY3 + " 已存在")

        if not NEW:
            print("ℹ️ 无变化 ⇒ 不写")
            return 0

        # ---- 原子写 (走 frag_write 的同一个原子写函数) ----
        import frag_write
        frag_write.atomic_write_yaml(FRAG, d)
        print("✅ 已原子写 pm.yaml:")
        for x in NEW:
            print("   ", x)
        return 0
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    sys.exit(main())
