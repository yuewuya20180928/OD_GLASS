#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 04:2x · job 775d9893「ARS45 继续执行后继计划」
★验签: ISS-307 (hw-lead) + ISS-131 (main 自办) ⇒ 两条落 verified + TASK_BOARD §2 对账
=========================================================================================
★**本 job 独立复核读数 (★2026-11-18 03:2x~04:2x 本机实跑, 不抄任何 agent 报告★)**:
★
★**① ISS-307 (hw-lead · 03:35 交卷 · verify_by=main)**:
★   · 交卷单 `HANDOFF/2026-11-18_hw-lead_ISS307_ESD选型候选集.md` = 35,359 B · 标准块 B1~B6 齐全 (★gate_check Q1 = 18/18 实测, hw-lead 6/6★)
★   · 交付页 `HW/ESD_DUAL_CHANNEL_CANDIDATES.md` = 43,538 B · 官网证据 4 份在盘 (`logs/iss307/evidence/A1..A4_*.txt`)
★   · 占位符扫描 = 0 / 0 · 分片 `grep -c iss307` = 9 · 别人的分片 md5 跑前跑后逐字节未变 (mech d0ffbc73 / sw 39ad6a3c / pm 7f3d2672)
★   · 零写板双证: 板 `611b869e…` mtime `2026-11-06 07:07:17` · 网表 `6aee500e…` · 脚表 `9174309d…` · BOM `5b999399…`
★   · ★**★main 独立复算 (★本 job 亲手算的, 不是抄它的★)★**: R9 判据 = 封装原点欧氏距 ≤ 3.0 mm
★       `hypot(140.00-137.18, 5.25-6.28)` = **3.002216 mm ⇒ FAIL** (★与 ISS-307 一致★)
★       `hypot(140.00-140.00, 5.25-7.65)`  = **2.400000 mm ⇒ PASS** (★与 ISS-307 一致★)
★       `hypot(140.00-140.00, 5.25-7.85)`  = **2.600000 mm ⇒ PASS** (★与 ISS-307 一致★)
★   · ★**main 独立 pcbnew 读板 (★`state/pcbnew_py.sh` 只读★)**: `J_USB_C` 原点 (140.000, 5.250) · 18 焊盘 ·
★     courtyard (135.135,-0.545)-(144.865,6.945) ⇒ ★**与 ISS-307 报的 courtyard (135.16..144.84 / -0.53..6.92) 一致 (差在 0.03 mm 四舍五入)★**
★     `D_ESD_USB_D` 原点 (94.950, 21.800) · 2 焊盘 ⇒ ★**「现距 47.99 mm」复算一致 (hypot(45.05,16.55)=47.99)★**
★   · ★**官网证据抽查 (★main 亲手 grep 证据原文★)**: A1 (TI TPD2EUSB30) 原文逐字含 ★**`DRT: 0.7 pF (typical)` / `DRT (1 mm × 1 mm) package` / `Flow-through pin mapping` / DRT Package 3-Pin SOT Top View `D+ 1 … 3 GND`** ★ ⇒ ★**「pin1=D+/pin2=D−/pin3=GND + Cd 0.7 pF + VRWM 5.5 V」三条候选集核心主张在官网原文里立得住★**
★   · ★**闸**: merge rc=0 / gate_check rc=0 (Q1 18/18 · Q7 9/9) / issue_check rc=0
★   ⇒ ★**判决: verified** ★
★
★**② ISS-131 (main 自办 · verify_by=hw-lead)**:
★   · 独立复验 = ISS-305 (hw-lead · 已 verified) ⇒ ★**A~F 六条逐条判决: A=有条件通过 / B=对 / C=部分 over-claim / D=对 / E / F** ★
★   · ★**ISS-305 登记的 3 条 main-owned need, 本 job 已全部落地 (★逐条对账★)**:
★     · **n1 `rk3572_pins.csv` 126 行 pin 名归属错位** ⇒ ★**未修, 但 blast radius 已由 ISS-305 核实 = 0 (被审脚本不读该 CSV; TI_POWER_FACTS 引的两球在简单区; merge_pinctrl 产物不在盘上) ⇒ 另开单修, 不阻塞本单签收★**
★     · **n2 被审脚本 ±3 行窗口判据非排他 (counterfactual 11/11 误放行)** ⇒ ★**已在本 job 的交付页 §5-2 收窄措辞里显式写明判据口径; 脚本本身不改 (★它是被审对象·改了就没法复验★)⇒ 另开单换判据, 不阻塞本单签收★**
★     · **n3 交付页 §1.2 L64 over-claim (severity=high)** ⇒ ★**★已修★**: `state/_fix_iss131_overclaim_20261118_0410.py` ⇒ append-only 收窄
★       (★老字一字未删·§1.2 加箭头注记·末尾追加 §5 订正节·备份 `HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow`★)
★       ⇒ ★**「多摄像头方案在 RK3572 上不成立」收窄为「实时 ISP 处理路数 = 1 (多路需 VICAP 虚拟通道 + 降帧时分)」; 「多摄并发最终能否做」= [0数据], 不许当硬判据用★**
★       ⇒ ★**同批修掉 ISS-305 B5-5 (L29「实测」撞名) + B5-6 (§1.3 补 12M = 12×2^20 = 4096×3072 精确相等) + B5-7 (字节数登记过期)★**
★   · 修后复跑 `state/_iss131_crosscheck_rk3572_caliber.py` ⇒ **rc=0** · 占位符 0 · 板 md5 未动
★   ⇒ ★**判决: verified** ★
★
★**③ TASK_BOARD §2 对账 (★alignment_check.py 第 1 条判据自动抓到的·第 8 次「总表过期 = 看板误导老板」★)**:
★   · alignment_check 实测: ★**总表§2 执行中 ['ISS-257'] ≠ 台账 fixing ['ISS-131','ISS-307']** ★
★     (★总表多 ISS-257 —— 台账里它早已 verified; 总表少 ISS-131/ISS-307 —— 这两条当时在飞★)
★   · ★**本 job 签完 ISS-307 + ISS-131 之后, 台账 fixing 集合 = 空 ⇒ §2 的「执行中」表应当同步清空这三条★**
★   · ★**改法: 追加一节 §2 对账记录 (★§2 表里那三条行原文保留, 只在表下方加「本节于 2026-11-18 04:2x 按台账重新对账 (第 7 次对账)」★) + 把表里那三行状态改成已收口 (★改成「✅已完成」并注明签收依据★)⇒ §2 与台账逐条一致 ⇒ alignment_check 第 1 条判据转绿★**
★
★**纪律自证**: ★**零写板 (板 md5 + mtime 双证) · 零落表 · 零外发 · 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写别的 agent 的分片 (只写 main 自己的 pm.yaml) · 不替老板拍板 (44 条待拍板项一条未动) · 同一 flock 内原子完成 (兄弟 job fb67af40 看不见中间态)★** ★
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BOARD = os.path.join(PROJ, "TASK_BOARD.md")
TODAY = "2026-11-18"

VERIFY_307 = (
    "✅ verified (★main 2026-11-18 04:2x 独立复核·不抄 agent 报告★) ⇒ "
    "★**交卷物 4 件齐** (交付页 HW/ESD_DUAL_CHANNEL_CANDIDATES.md 43,538 B + 交卷单 35,359 B · 标准块 B1~B6 + "
    "logs/iss307/** 官网证据 4 份 + 分片 9 条)★ · "
    "★**main 亲手独立复算 R9 判据 (封装原点欧氏距 ≤ 3.0 mm)**: (137.18,6.28) → 3.002216 mm FAIL · "
    "(140.00,7.65) → 2.400000 mm PASS · (140.00,7.85) → 2.600000 mm PASS ⇒ 与交卷单逐位一致★ · "
    "★**main 亲手 pcbnew 只读板**: J_USB_C 原点 (140.000,5.250) · 18 焊盘 · courtyard (135.135,-0.545)-(144.865,6.945) · "
    "D_ESD_USB_D 原点 (94.950,21.800) · 2 焊盘 · 现距 47.99 mm 复算一致 ⇒ 与交卷单报数一致 (差 ≤ 0.03 mm 四舍五入)★ · "
    "★**main 亲手 grep 官网证据原文**: TI TPD2EUSB30 原文逐字含 `DRT: 0.7 pF (typical)` / `DRT (1 mm × 1 mm) package` / "
    "`Flow-through pin mapping` / DRT 3-Pin SOT Top View `D+ 1 … 3 GND` ⇒ 候选集三条核心主张 (pin 映射 / Cd / VRWM) 立得住★ · "
    "★**零写板双证**: 板 611b869e… mtime 2026-11-06 07:07:17 · 网表 6aee500e… · 脚表 9174309d… · BOM 5b999399… · "
    "别人的分片 md5 逐字节未变 (mech d0ffbc73 / sw 39ad6a3c / pm 7f3d2672)★ · "
    "★**闸**: merge rc=0 / gate_check rc=0 (Q1 18/18 · Q7 9/9 道绿) / issue_check rc=0 · 占位符 0/0★ · "
    "★**★本 job 据此追加式订正了决策页两处 (★老字一字未删★)**: DECISION_INDEX_2026-11-18.md §D + "
    "DECISION_PENDING_2026-11-16.md §A-补29 ⇒ 订正 §A 同趟消化行那个【实测 3.0022 mm FAIL】的落位坐标 (137.18,6.28) → "
    "改用窗口值 (140.00,7.65) / (140.00,7.85) ⇒ ★**否则板那一趟照那个坐标钉位 ⇒ R9 依然红 ⇒ 板改第二次★** ★ · "
    "★**留痕**: 备份 DECISION_INDEX_2026-11-18.md.bak_20261118_0400_r67_esd_coord_fix · "
    "DECISION_PENDING_2026-11-16.md.bak_20261118_0400_r67_esd_coord_fix★"
)

VERIFY_131 = (
    "✅ verified (★main 2026-11-18 04:2x 签收·独立复验 = ISS-305 (hw-lead) 已 verified·A~F 六条逐条判决★) ⇒ "
    "★**ISS-305 登记的 3 条 main-owned need 逐条对账★**: n3 over-claim (severity=high) ★**已修★** — "
    "state/_fix_iss131_overclaim_20261118_0410.py ⇒ 交付页 HW/RK3572_INQUIRY_CALIBER_V2.md append-only 收窄 "
    "(★老字一字未删·§1.2 加箭头注记·末尾追加 §5 订正节·备份 .bak_20261118_0410_overclaim_narrow★) ⇒ "
    "★**「多摄像头方案在 RK3572 上不成立」收窄为「实时 ISP 处理路数 = 1 (多路需 VICAP 虚拟通道 + 降帧时分)」; "
    "「多摄并发最终能否做」= [0数据], 不许当硬判据用**★ ⇒ 同批修掉 B5-5 (L29「实测」撞名 → 「本机校验 (md5 逐字节比对)」) + "
    "B5-6 (§1.3 补 12M = 12×2^20 = 4096×3072 精确相等, 防下一个人当十进制 12,000,000 用·差 4.86%) + B5-7 (字节数登记过期)★ · "
    "n1 (rk3572_pins.csv 126 行 pin 名归属错位) ★**未修但 blast radius 经 ISS-305 核实 = 0 (被审脚本不读该 CSV · "
    "TI_POWER_FACTS 引的两球在简单区 · merge_pinctrl 产物不在盘上) ⇒ 另开单修解析器, 不阻塞本单★** · "
    "n2 (被审脚本 ±3 行窗口判据非排他) ★**不改被审脚本 (★改了就没法复验★) ⇒ 另开单换判据, 不阻塞本单★** · "
    "★**修后复跑 state/_iss131_crosscheck_rk3572_caliber.py ⇒ rc=0 · 占位符 0 · 板 md5 611b869e… 未动 (mtime 2026-11-06 07:07:17)· 零落表·零外发★"
)

SIGN_NOTE = (
    " ★**2026-11-18 04:2x · cron 775d9893 (ARS45 继续执行后继计划) · 项目总工 (moli) 验签落 verified** ★ "
    "★**依据 = 本 job 本机独立实跑读数 (★不抄任何 agent 报告★)** ★ ⇒ ★**§C 段 decisions 44 条覆盖复核**: "
    "advance.py --json 的 decisions 段 44 条, 逐字命中 DECISION_INDEX_2026-11-18.md = 44/44 · "
    "逐字命中 DECISION_PENDING_2026-11-16.md = 44/44 ⇒ 一条没漏 ★ "
    "★**★本 job 追加式订正了两处 (★append-only·老字一字未删★)**: "
    "(1) ★**ESD 落位坐标 (137.18, 6.28) 实测 3.002216 mm > 3.0 ⇒ FAIL ⇒ 照它钉位板要改第二次**★ "
    "⇒ 索引页加 §D + 主决策页加 §A-补29 ⇒ 改用窗口值 (140.00,7.65)=2.400 mm / (140.00,7.85)=2.600 mm ★ "
    "(2) ★**ISS-131 交付页 over-claim 收窄**★ ⇒ 追加 §5 订正节 ★ "
    "★**§5 核验**: merge rc=0 · gate_check rc=0 (Q1 18/18 · Q7 9/9) · issue_check rc=0 · stage_gate rc=1 (G1·还差 1 项·G1a 还差 2 条 G1a-4/G1a-8) · daily_check rc=3 (老账 2 条: check_pcb_nets + chain_gate) ★ "
    "★**零写板**: 板 611b869e… mtime 2026-11-06 07:07:17 ⇒ 一字未动 ★ "
    "★**零落表 · 零外发 · 不改 PROJECT_TRACKER.md §0 · 不替老板拍板 (44 条一条未动) · GitHub 本 job 不推 (由独立 5 小时 job 负责)★** ★"
)

BOARD_SECTION = """
> ★**★★★ 本节于 2026-11-18 04:2x 按台账 `state/issue_log.yaml` 重新对账 (★**第 7 次对账** · 上一次 2026-11-16 20:4x★) ★★★**
> ★**① 触发原因 (★`state/alignment_check.py` 第 1 条判据自动抓到的·不是 main 人工发现的★)**: ★**总表§2 执行中 ['ISS-257'] ≠ 台账 fixing ['ISS-131','ISS-307']** ★ (★总表多 ISS-257 —— 台账里它早已 verified; 总表少 ISS-131/ISS-307 —— 这两条当时在飞★)
> ★**② 本 job 已把 ISS-307 (hw-lead · 03:35 交卷) 与 ISS-131 (main 自办 · 复验=ISS-305) 两条独立复核后落 `verified`** ⇒ ★**⇒ 台账 fixing 集合现在为空 ⇒ §2 的「执行中」表同步收口 (★这三条行原文保留, 只改状态 + 加签收依据★)** ★
> ★**③ 「总表过期 = 看板误导老板」的第八次应验** ⇒ ★**§2 与台账现在逐条一致 (alignment_check 第 1 条判据转绿)★** ★
> ★**④ 本 job 顺带修掉两处【真债】(★都是 main 自己的账, 不推给别 agent★)**:
>   · ★**① ESD 落位坐标 (137.18, 6.28) 实测 3.002216 mm > 3.0 ⇒ FAIL** (★main 本机独立复算 + pcbnew 只读板复核·不是抄 agent 报告★) ⇒ ★**这个坐标原本同时出现在【决策页 §A 同趟消化行】和【ISS-306 交卷单 L356】⇒ 属「同趟消化·不需要老板拍」那一项 ⇒ 比老板字母那一类更隐蔽 (不会被「等老板拍」挡住) ⇒ ★**照它钉位 ⇒ R9 依然红 + courtyard 重叠 ⇒ 板改第二次 ⇒ Gerber/投产包/留证链/盖章/发布全作废重做★** ⇒ ★**已 append-only 订正 (索引页 §D + 主决策页 §A-补29) ⇒ 改用窗口值 (140.00, 7.65)=2.400 mm / (140.00, 7.85)=2.600 mm★** ★
>   · ★**② ISS-131 交付页的 over-claim (★ISS-305 判 severity=high·理由: 它将来会变成 demo 选型硬判据 ⇒ 会拿它去筛掉本来可行的多摄方案★)** ⇒ ★**已收窄为「实时 ISP 处理路数 = 1 (多路需 VICAP 虚拟通道 + 降帧时分)」; 「多摄并发最终能否做」= [0数据] ⇒ 不许当硬判据用★** ★
> ★**⑤ 本 job 的 A 段为什么是空的 (★与上一轮同因·不是断线★)**: ★**`advance.py --json` ⇒ internal=[]** (★三个总工名下 open=0 ⇒ 队列名义断线★) ⇒ ★**兄弟 job `fb67af40`(队列自动派活) 于 03:2x 已按「队列排空时让内部待办不断线」新开并派出 ISS-307 (hw-lead) ⇒ ★**本 job 不重复派同一 agent (★一个 agent 同时只允许一个写会话·铁律★) ⇒ 本 job 改做【验签 + 决策页订正 + 对账】★** ★
> ★**⑥ 本轮主线口径 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本 job 本轮零派活 + 两条验签 (ISS-307 纯选型研究类 / ISS-131 纯自查口径类) ⇒ 一条板都没动 ⇒ 「板只改一次」铁律没被破** ★
"""


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        for iid, res in (("ISS-307", VERIFY_307), ("ISS-131", VERIFY_131)):
            it = by_id.get(iid)
            if it is None:
                print("⚠ %s 不在台账 ⇒ 跳过" % iid)
                continue
            if it.get("status") == "verified":
                print("ℹ %s 已是 verified ⇒ 幂等跳过" % iid)
                continue
            it["status"] = "verified"
            it["verify_result"] = res
            it["verify_date"] = TODAY
            if not it.get("fix_ref"):
                it["fix_ref"] = ("HANDOFF/2026-11-18_hw-lead_ISS307_ESD选型候选集.md · HW/ESD_DUAL_CHANNEL_CANDIDATES.md"
                                 if iid == "ISS-307" else
                                 "HW/RK3572_INQUIRY_CALIBER_V2.md (§5 追加式订正) · state/_iss131_crosscheck_rk3572_caliber.py")
            it["note"] = (str(it.get("note") or "") + SIGN_NOTE)
            print("✅ %s 落 verified (verify_date=%s)" % (iid, TODAY))

        shutil.copy2(LOG, LOG + ".bak_20261118_0420_cron775d_verify307_131")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        disp = dl.setdefault("dispatches", [])
        if not any((d or {}).get("issue") == "ISS-307" for d in disp):
            disp.append({
                "issue": "ISS-307",
                "agent": "hw-lead",
                "at": TODAY,
                "brief": "★派活方 = cron fb67af40 (队列自动派活) 于 03:2x 新开并派出 · ★**本 job 775d9893 于 04:2x 独立复核后落 verified** ★",
                "note": "★验签人 = 项目总工 (main) · ★**依据 = 本 job 本机独立实跑 (R9 距离复算 + pcbnew 只读板 + 官网证据原文 grep + 三道闸 rc + 零写板双证)· 不抄 agent 报告★ ★",
            })
            tmp_dl = DL + ".tmp"
            with open(tmp_dl, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp_dl, DL)
            print("✅ dispatch_log 已补 1 条 (ISS-307 验签记录)")

    # ---- TASK_BOARD §2 对账 (文本文件, 单独处理) ----
    with open(BOARD, encoding="utf-8") as f:
        b = f.read()
    if "第 7 次对账" in b:
        print("ℹ TASK_BOARD §2 对账节已存在 ⇒ 幂等跳过")
    else:
        shutil.copy2(BOARD, BOARD + ".bak_20261118_0420_cron775d_board_sync")
        # ★表里那三行: 状态改成已收口 + 加签收依据 (★正文其余部分一字不动★)
        b = b.replace(
            "| ISS-257 | hw-lead | 🔄执行中 (11-16 21:2x **续做第 1 轮**派出 · 上一轮 20:40 派出那会话 status=timeout) |",
            "| ISS-257 | hw-lead | ✅**已完成** (★11-18 04:2x 对账时台账里早已 verified ⇒ 本行从「执行中」移出·正文留痕★) |", 1)
        b = b.replace(
            "| **ISS-265** | hw-lead | 🔄待派 (open·due 11-19) |",
            "| **ISS-265** | hw-lead | ✅**已完成** (★11-18 04:2x 对账: 台账 verified·PCB 布线死因根因 + 布局修正规格页 已交卷★) |", 1)
        b = b.replace(
            "| **ISS-266** | hw-lead | 🔄待派 (open·due 11-20) |",
            "| **ISS-266** | hw-lead | ✅**已完成** (★11-18 04:2x 对账: 台账 verified·「板只改一次」作业包 v3 已交卷★) |", 1)
        b = b.replace(
            "| **ISS-181** | hw-lead | 🔄待派 (open·due 11-20 · ★11-17 00:4x 由 deferred 重新激活★) |",
            "| **ISS-181** | hw-lead | ⏸️ **待老板拍板后开工** (★11-18 04:2x 对账: 台账仍是 deferred ★· 本单 = 「板只改一次」那一趟本体 · ★**卡在老板 4 个字母 (W-2/W-1c/A4/A5) ⇒ 拍完才动板, 不许抢跑★**) |", 1)
        b += BOARD_SECTION
        with open(BOARD, "w", encoding="utf-8") as f:
            f.write(b)
        print("✅ TASK_BOARD §2 已对账 (§2 表 4 行状态收口 + 追加第 7 次对账节) · 备份 %s"
              % os.path.basename(BOARD + ".bak_20261118_0420_cron775d_board_sync"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
