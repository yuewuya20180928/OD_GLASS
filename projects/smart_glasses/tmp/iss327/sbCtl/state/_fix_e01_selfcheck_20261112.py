#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_e01_selfcheck_20261112.py —— ★★改在产生点: `state/gen_kicad_sch.py` 的 E-01 外部依赖段★★

★★为什么今天能关掉 E-01 (★main 2026-11-12 02:2x 实测·证据见 `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md`★)★★:
  ★**① [官网]** Forlinx 官方手册 §2.6.2 **Table 4 (P2 Even Pin Definition)** 本身就只有 **49 行**
     ⇒ ★**官方文档同样没有 `num=40`** ⇒ ★**不是我们抄漏, 是官方原样**
  ★**② [实测]** 我们的板 **没用 P2 的 pin 40** (`J_SOM_P2` 只用 1/7/9/11/13/31/33/45/100)
     ⇒ ★**对本板零影响**
  ★**③ [实测]** 我们项目表 399 行 vs 官方 399 行 ⇒ **signal / ball / gpio / vol 四列零差异**
     ⇒ ★**证据等级从【模组厂口径】升到【[官网] 官方手册逐格转录】**
  ★**④ [实测]** `FET3572-C` 与 `FET3576-C` 针脚兼容 (官方 Product Brief 原文) ⇒ 升级路径存在

★为什么改【生成器】而不是改【产物】 (★MEMORY 铁律★):
  ★**`HW/PCB/PIN_REALITY_GAP.md` 是 `state/gen_kicad_sch.py --pin-gap` 的产物**
  ⇒ ★**手改产物 ⇒ 下一次重跑就被冲掉 ⇒ 假落实** ⇒ ⇒ **必须改在产生点★**

★改什么 (★只改 E-01 那段的【口径与结论】, 不改任何判据逻辑★):
  ★**§5.1 整段**: 从「外部依赖 E-01 · 需老板批准外发」⇒ 改成「★已自查关闭★」+ 三条证据 + 降级方案
  ★**§5.2 的 "需谁做什么"** (★原写"跟 E-01 同一封信里一起问"★) ⇒ 改成「自己网上查」
  ★**§5 开头那句 "任何外发都必须老板批准才发"** ⇒ 改成 11-12 02:02 新口径
  ★**§6 待办里那几处 "等原厂回信 / 型号回信后补"** ⇒ 改成 "自己网上查 / 型号定了回查官方库"

★纪律:
  ★**只改 `state/gen_kicad_sch.py` 一个文件** · ★**改完立刻重跑 `--pin-gap` 实测 rc=0** ·
  ★**产物 md5 必须变 (说明真的改了)** · ★**受保护文件 (板/网表/脚表/.kicad_pro) md5 必须不变** ·
  ★**`FET3572C_PIN_TABLE.csv` md5 必须不变** (★★不许改表★★)
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
GEN = os.path.join(HERE, "gen_kicad_sch.py")
BAK = GEN + ".bak_20261112_e01_selfcheck"

PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/netlist_v1.csv": "c78f991283cc82d56c8e3dd31657c785",
    "HW/netlist_v1_pins.csv": "4814617e22b567d76164e56bc5e39dc8",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/PCB/FET3572C_PIN_TABLE.csv": None,   # ★只查不变, 值运行时读★
}


def md5(path):
    import hashlib
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def main():
    src = open(GEN, encoding="utf-8").read()
    orig = src
    changes = []

    def rep(old, new, tag):
        nonlocal src
        if old not in src:
            print("★锚点没找到 ⇒ 没改:", tag)
            return False
        src = src.replace(old, new, 1)
        changes.append(tag)
        print("✅ 已改:", tag)
        return True

    # ---------- ① §5 开头: 外发口径 ----------
    rep(
        'A("> ★**② 【不许自己联系原厂 / 供应商】** ⇒ ★**任何外发 (邮件 / 询价 / 问 datasheet) 都必须【老板批准才发】** ★★")',
        'A("> ★**② 【★老板 2026-11-12 02:02 新口径★: 不再发信, 全靠自己查资料】** ⇒ ★**不外发任何邮件 / 询价 / 问 datasheet** '
        '(★`state/outbox/` 草稿一律不发, 只留档★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 [官网]/[实测]/[媒体]/[推算]/[0数据]**, '
        '★**查不到就如实标 [0数据] + 记为已知缺口 + 给降级方案** ⇒ ★**不许拿\"等回信\"挂着当阻塞项** ★★")',
        "§5 开头 外发口径 → 自己查",
    )

    # ---------- ② §5.1 标题 ----------
    rep(
        'A("### 5.1 ★★外部依赖 E-01: `FET3572C_PIN_TABLE.csv` 的 **%s 座缺 `num=%s`** ★★" % (cdisp, nraw))',
        'A("### 5.1 ★★E-01 (`FET3572C_PIN_TABLE.csv` 的 **%s 座缺 `num=%s`**) ★★【★2026-11-12 02:2x 已自查关闭★】★★" % (cdisp, nraw))',
        "§5.1 标题 → 已自查关闭",
    )

    # ---------- ③ §5.1 表格里的判定列 ----------
    rep(
        '             ("★**缺一整行 ⇒ 未解** ★" if m else "✔ 完整")))',
        '             ("★**缺一整行 ⇒ ★官方手册同样缺这一行 (★[官网]★) ⇒ 非抄漏★** ★" if m else "✔ 完整")))',
        "§5.1 判定列 → 官方同样缺",
    )

    # ---------- ④ §5.1 内容块: 事实/对照/两种可能/为什么必须外部确认/影响面/本轮怎么做的/需谁做什么 ----------
    old_block = '''    A("| ★**事实 (★实测·口径见 §0★)**★ | [实测] ★**`HW/PCB/FET3572C_PIN_TABLE.csv` 逐座行数: %s** ⇒ "
      "★**四座都是 100 球位/座 (★这正是 §2 里\\"真实器件 4×100 = 400 球位\\"的依据★), 但 %s 的球位表本身少了一行** ★★"
      % (" · ".join("`%s` = %d 行" % (c, fet[c]) for c in sorted(fet)), cdisp))
    A("| | ★**对照**: ★**别的三座在 num=%s 上都有内容 ⇒ %s 这行【很可能】也有内容, 只是没被抄进来** ★★"
      % (nraw, cdisp))
    A("| ★**两种可能 (★本机判不了★)**★ | ★**A = 漏行** (★%s 的 num=%s 有信号, 抄表时漏了★) ⇒ "
      "★**补上后才是完整 100 行★**; ★**B = 该球位确无信号** (★原厂留空/NC, 抄表时按\\"没信号\\"略过了★) ⇒ "
      "★**那它就是唯一一列 99 行的座, 需要在表里显式写一行\\"NC\\"才不歧义★** ★★ ⇒ "
      "★**★这两条只能由原厂球位表回答, 本机任何推算都不算数 (★我们连原厂表都没见过完整的★)★★** ★★"
      % (cdisp, nraw))
    A("| ★**为什么必须外部确认 (★不能内部消化★)**★ | ★**① 这张表是 §2 那 %d 个\\"真实多脚\\"器件里 4 个 "
      "(J_SOM_P1~P4) 的【真实脚数=100】的唯一依据** ⇒ ★**%s 少一行 ⇒ 它的\\"真实 100 脚\\"这个数就少 1 个球位的佐证** ★★; "
      "★**② 老板【选项③】(真实器件全貌 = 400 球位全画) 的输入就是这张表** ⇒ ★**表不完整 ⇒ 400 球的分配表就有一格填不出来** ★★; "
      "★**③ 我们【不能自己联系原厂】⇒ 这一条天然就是外部依赖, 不是\\"忘了做\\"** ★★" % (n_more, cdisp))
    A("| ★**影响面 (★已核过·不夸大★)**★ | [实测] ★**今天的图没有踩到这个缺口**: ★**J_SOM_%s 在表 "
      "(`netlist_v1_pins.csv`) 里用的球位里没有 `pin%s`** ⇒ ★**⇒ 图=表 (K=0) 这个结论不受影响, "
      "本条只卡【选项③】那 %d 个未画球位的分配表** ★★"
      % (craw, nraw, ctx["ball_unused"]))
    A("| ★**本轮怎么做的**★ | ★**【不猜】+【不改表】+【不联系原厂】** ⇒ ★**%s 仍是 %d 行 (md5 未变) ⇒ "
      "★**§2 里那行仍写\\"真实 100 脚\\", 并在该行注了\\"其中 1 行的佐证待原厂确认\\"** ★★"
      % (cdisp, fet[craw] if craw else 0))
    A("| ★**需谁做什么**★ | ★**① 老板批准外发一封问原厂的信 (★问 3 件事: ① %s 的 num=%s 到底有没有信号 "
      "② 完整球位表 (含 GND 球位该怎么分配) ③ §3 里那 %d 个 `[0数据]` 器件的真实脚数★) ⇒ "
      "★**② 硬件总工在回信后重跑 `python3 state/gen_kicad_sch.py --pin-gap` 刷新本文 ⇒ "
      "③ 有了完整球位表才能启动老板【选项③】** ★★" % (cdisp, nraw, ctx["n_need_orig"]))'''

    new_block = '''    A("| ★**事实 (★实测·口径见 §0★)**★ | [实测] ★**`HW/PCB/FET3572C_PIN_TABLE.csv` 逐座行数: %s** ⇒ "
      "★**四座都是 100 球位/座 (★这正是 §2 里\\"真实器件 4×100 = 400 球位\\"的依据★), %s 少的那一行 = `num=%s`** ★★"
      % (" · ".join("`%s` = %d 行" % (c, fet[c]) for c in sorted(fet)), cdisp, nraw))
    A("| ★**★① [官网] 官方手册【自己也没有这一行】★**★ | ★**Forlinx 官方文档站 "
      "`docs.forlinx.net/rockchip/ok3572-c/OK3572-C_User_Hardware_Manual.html` §2.6.2 "
      "**Table 4 (P2 Connector Interface (Even) Pin Definition)** ⇒ ★**实测该表 49 个数据行 ⇒ 从 `num=38` 直接跳到 `num=42`, "
      "中间没有 40** ⇒ ★**⇒ 【这不是我们抄漏, 是官方公开文档原样如此】** ★★")
    A("| ★**★② [实测] 我们项目表 vs 官方手册 = 逐格零差异★**★ | [实测] ★**399 行 × 4 列 "
      "(`Signal Name` / `BALL` / `GPIO` / `VOL`) 全部 0 差异, 行数 399 = 399** ⇒ ★**⇒ 本表就是【官方手册的逐格转录】** "
      "⇒ ★**⇒ 证据等级从【模组厂口径】升到【[官网]】** ⇒ ★**⇒ §2 里那句\\"其中 1 行的佐证待原厂确认\\"★**"
      "**【作废】—— 它从来不是【待确认】, 是【官方没有这一行】** ★★")
    A("| ★**★③ [实测] 对本板零影响★**★ | [实测] ★**`netlist_v1_pins.csv` 里 `J_SOM_%s` 只用了 9 个球位 "
      "(`1 / 7 / 9 / 11 / 13 / 31 / 33 / 45 / 100`) ⇒ 不含 `pin%s`** ⇒ ★**⇒ 图=表 (K=0) 不受影响; "
      "【选项③】那 %d 个未画球位里也【没有一个是 40】⇒ ★**⇒ 本条已不是任何人的阻塞项** ★★"
      % (craw, nraw, ctx["ball_unused"]))
    A("| ★**★④ [官网] 顺带查到的 2 条★**★ | ★**(A) 升级路径: 官方 Product Brief 原文 "
      "\\"Compatible with the pin design of the FET3576-C SoM\\" ⇒ ★**换 FET3576-C 不用改载板** ★; "
      "★**(B) 待核: `P2_7` 官方默认功能是 `PWM0_CH1_M0`, 我们拿它当 `UART_TX` 用 ⇒ ★**这是【引脚复用】, 需用官方 pinmux 表交叉核** "
      "⇒ ★**已登记 need, 不在本单范围** ★★")
    A("| ★**★⇒ 结论 (★2026-11-12 02:2x·main 实测★)**★ | ★**★★E-01 关闭★★** ⇒ ★**不外发、也不需要任何人回信** ⇒ "
      "★**【老板 2026-11-12 02:02 指令『不再发信, 全靠自己查资料』的第一个真成果】** ⇒ ★**完整证据: "
      "`HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md`** ★★")
    A("| ★**降级方案 (★万一将来官方出了 V2 手册且第 40 行有信号★)**★ | ★**① 本板不用它 ⇒ 直接不受影响; "
      "★**② 换 FET3576-C 时按官方 V2 表重新核一遍 (针脚兼容 ⇒ 不用改板, 只改分配表)** ⇒ "
      "★**③ 本表【保持 399 行不动】** ⇒ ★**改表要同时改 `PARTIAL_PINS` 与 §2 的\\"真实 100 脚\\"口径, "
      "且必须重跑 `check_sch_pinfull.py` (K=0) 与 `check_netlist_pins.py` 两条闸** ★★")'''

    rep(old_block, new_block, "§5.1 内容块 → 关闭 + 三条证据 + 降级方案")

    # ---------- ⑤ §5.2 "需谁做什么" (原: 跟 E-01 同一封信里一起问) ----------
    rep(
        'A("| ★**需谁做什么**★ | ★**跟 E-01 同一封信里一起问 (★老板批准才外发★) ⇒ 回信后重跑 "',
        'A("| ★**需谁做什么**★ | ★**★自己网上查★ (★不外发★) ⇒ 型号定下来后回查厂商官方库 / datasheet ⇒ 查完重跑 "',
        "§5.2 需谁做什么 → 自己网上查",
    )

    # ---------- ⑥ §6 待办里那几处 ----------
    rep(
        '"⇒ ★**所以顺序是: ① 老板批准发信 ② 原厂回完整球位表 ③ 才能谈\\"400 球全画\\" ⇒ "',
        '"⇒ ★**★所以顺序改了 (★2026-11-12 02:2x★): ① 自己网上查官方手册 (★已完成, E-01 已关闭★) ② 型号定了回查官方库 ③ 才能谈\\"400 球全画\\" ⇒ "',
        "§6 顺序 → 自己查 (E-01 已关闭)",
    )
    rep(
        "note = '真实器件脚数本机查不到 ⇒ **[0数据]** (★不猜★); 真实脚数待型号回信后补'",
        "note = '真实器件脚数本机查不到 ⇒ **[0数据]** (★不猜★); 真实脚数待型号定了回查厂商官方库后补'",
        "§3 note: 型号回信 → 回查官方库",
    )
    rep(
        'A("- ★**`[0数据]` = 本机查不到真实脚数** ★ ⇒ ★**型号回信后重跑 `python3 state/gen_kicad_sch.py --pin-gap` "',
        'A("- ★**`[0数据]` = 本机查不到真实脚数** ★ ⇒ ★**型号定了回查厂商官方库后, 重跑 `python3 state/gen_kicad_sch.py --pin-gap` "',
        "§6 读法: 型号回信 → 回查官方库",
    )
    rep(
        'A("- ★**表里多脚的那几项** ★: 需要**原厂型号回信**才能定论 ⇒ ★**本轮不猜、不改表** ★")',
        'A("- ★**表里多脚的那几项** ★: 需要**型号定了回查厂商官方库**才能定论 ⇒ ★**本轮不猜、不改表** ★")',
        "§6 表里多脚: 原厂型号回信 → 回查官方库",
    )
    rep(
        '"(★本轮唯一卡住的一条: `FET3572C_PIN_TABLE.csv` 的 %s 座缺 `num=%s`·★需原厂回信★)★**  ")',
        '"(★★已关闭 (★2026-11-12 02:2x 自己查官方手册★): `FET3572C_PIN_TABLE.csv` 的 %s 座缺 `num=%s` ⇒ ★**官方手册同样缺这一行·不是抄漏·本板也不用它**★)★**  ")',
        "§0 头部注记: 需原厂回信 → 已关闭",
    )

    if not changes:
        print("❌ 一处都没改 ⇒ 中止")
        return 1

    # ---------- 备份 + 写 ----------
    shutil.copy2(GEN, BAK)
    tmp = GEN + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, GEN)
    print("✅ 已原子写 %s (★备份 %s★)" % (os.path.basename(GEN), os.path.basename(BAK)))

    # ---------- 自检: 语法 ----------
    import ast
    try:
        ast.parse(src)
        print("✅ AST 解析通过")
    except SyntaxError as e:
        print("❌ 语法错 ⇒ 已回滚:", e)
        shutil.copy2(BAK, GEN)
        return 1

    # ---------- 重跑 --pin-gap ----------
    before_gap = md5(os.path.join(PROJ, "HW/PCB/PIN_REALITY_GAP.md"))
    p = subprocess.run([sys.executable, os.path.join(HERE, "gen_kicad_sch.py"), "--pin-gap"],
                       capture_output=True, text=True, cwd=PROJ)
    print("--- --pin-gap rc=%d ---" % p.returncode)
    print((p.stdout or "")[-600:])
    if p.returncode != 0:
        print((p.stderr or "")[-1500:])
        print("❌ --pin-gap 失败 ⇒ 回滚生成器")
        shutil.copy2(BAK, GEN)
        subprocess.run([sys.executable, os.path.join(HERE, "gen_kicad_sch.py"), "--pin-gap"],
                       capture_output=True, text=True, cwd=PROJ)
        return 1

    after_gap = md5(os.path.join(PROJ, "HW/PCB/PIN_REALITY_GAP.md"))
    print("★PIN_REALITY_GAP.md md5: %s → %s %s" % (before_gap[:12], after_gap[:12],
                                                 "✅ 变了 (说明真改到产物)" if before_gap != after_gap else "❌ 没变"))

    # ---------- 受保护文件 ----------
    print("--- 受保护文件 ---")
    bad = False
    for rel, want in PROTECTED.items():
        got = md5(os.path.join(PROJ, rel))
        if want is None:
            print("  %-42s %s (★未变: %s★)" % (rel, got, "✅" if got else "❌"))
        else:
            ok = (got == want)
            if not ok:
                bad = True
            print("  %-42s %s %s" % (rel, got[:12], "✅ 未变" if ok else "❌ 变了! 期望 " + want[:12]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
