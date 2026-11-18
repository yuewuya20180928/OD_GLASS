#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 17:5x · job 775d9893「ARS45 继续执行后继计划」
★新开 ISS-295 (mech-lead) · MECH 侧「合法改板」机制 + 收工重锚清单★
=========================================================================================
★**为什么有这一趟 (★main 17:4x~17:5x 本机实查盘面 + 读会话, 不抄任何交卷报告★)**:
  · `python3 state/advance.py --json` ⇒ ★**`internal: [ISS-293 → sw-lead]`** (★ISS-293 的上一趟会话 17:18 failed ⇒
    17:4x 被重开为 open ⇒ 本趟已重新派出并标 fixing★)
  · ★**两个名额被占 (hw-lead: ISS-292 在飞 · 会话 `4a4fade6` status=running★; sw-lead: ISS-293 本趟已派出★)**
  · ★**mech-lead 名额空着 (ISS-294 已由 main 17:4x 独立复验落 verified★) ⇒ 而 issue_log 里 mech-lead 名下【没有 open 单】**
    ⇒ ★**本 job 照 advance.py 的名单只能派 ISS-293 一条 ⇒ 但主线 (板那一趟) 的 MECH 侧还差一件 ⇒ ⇒ 本趟新开 ISS-295 补上★**
★**★ISS-295 的病灶 (★main 17:4x~17:5x 本机实读, 逐条带行号★)**:
  · `MECH/check_board_frame_coords.py` L79 · `MECH/check_demo_struct_truth.py` L81 ⇒ ★**板 md5 `611b869e…` 写死成「硬保护基线」★**
  · `grep -rn "reboard" MECH/*.py | wc -l` ⇒ ★**实测 = 0 ⇒ MECH 侧【没有】SW 侧 ISS-284 那套「合法改板」机制★**
  · ★**⇒ 板那一趟合法改板一次后, MECH 两道闸必假红 ⇒ 收工验收时的假红会被误读成「板改坏了」⇒ 板白改第二遍★**
★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** ⇒ ★**不碰任何 agent 的分片
  (★`state/fragments/*.yaml` 是三个总工的, main 不写★) · 不碰板 / 网表 / 脚表 / BOM / 落表台账 / 决策页 / outbox / 任何闸脚本★
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ★
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-295_mech_legal_reboard_mechanism.md")
TODAY = "2026-11-17"

TITLE_295 = """★★[主线内·MECH 侧·闸机制类·内部活] ★★【MECH 两道闸把【板 md5】写死成「硬保护基线」⇒ 板那一趟合法改板一次后 ⇒ 这两道闸必假红 ⇒ 而收工验收时的假红会被误读成「板改坏了」⇒ 板白改第二遍】★★ ⇒ ★**本单 = 把 SW 侧 ISS-284 已验证的「合法改板」机制 (reboard 四项原子记录 + 落表台账链头 + fail-closed 四条) 接到 MECH 侧两道闸 + 把 MECH 侧「收工后同一次重锚」写成收工清单强制项 + ≥4 条反向用例 (★纯 MECH 侧·零写板·零落表·零改网表★)** ★"""

DESC_295 = """★main 2026-11-17 17:4x~17:5x 本机实读盘面 (★不抄任何 agent 报告★)★
★**① 病灶 (逐条带行号)**: ★**`MECH/check_board_frame_coords.py` L79** `PROTECTED` 字典里 ★`"demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075"` ★(共 2 件: 板 + `.kicad_pro`★) ⇒ ★**基线写死 ⇒ 板一改 ⇒ C4 必红** ★ · ★**`MECH/check_demo_struct_truth.py` L81** `MD5_EXPECTED` 里同一个板 md5 ★(共 6 件: 板 + `.kicad_pro` + 4 个 MECH 脚本★) ⇒ ★**基线写死 ⇒ 板一改 ⇒ 必红** ★
★**② 同一个文件里已经治过同一种病, 但只治了一半**: `MECH/check_board_frame_coords.py` L76~L80 自己写着 ★「★★**ISS-286 · 2026-11-17** ★★ 原先这里是 5 件 (板 / `.kicad_pro` + 网表 / 脚表 / BOM 三件写死 md5) ★★⇒ 网表 / 脚表 / BOM 三件【移出】写死基线, 改走【落表台账链头】★★」 ★ ⇒ ★**★★★同一个病, 同一个文件, 只治了三件, 板那两件没治 ⇒ 现在板要合法变了, 缺口暴露★★★ ★**
★**③ MECH 侧完全没有「合法改板」机制 (main 本机实跑)**: `grep -rn "reboard" MECH/*.py | wc -l` ⇒ ★**实测 = 0** ★ ⇒ ★**而 SW 侧早就有了 (ISS-284 · 已 verified·main 已独立复验过)★**: `SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` (★四条判据: ① 保护基线自证 ② 台账无变更行 ⇒ 纯 md5 硬保护 ③ 有变更行 ⇒ 链头唯一/链不断/链头有单号 + 四项逐字对上 + 基线留链尾 + 盘上==链头 ④ 同组成对覆盖★) + 锚点 `SW/SW_MD5_BASELINE_LEDGER.md` §1 的 `hard_protected[].reboard` 原子映射 (★单号 by + 文件名 file + 改前 prev_md5 + 改后 md5★) + 判决源 = 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 链头 (★现链头 §16.2 板那两行「变了? = 否」⇒ 板还没合法改过★) ★
★**④ 那一趟板会变什么 (⇒ MECH 侧要重锚的不止 md5)**: 作业包 §3-S1~S13 的 A 类步 ⇒ 位号 `_1` 后缀 **156 → 157** · `C_VBUS_GND` 下板 (★封装 **186 → 185**★) · `Q_PG` 三根线重画 (★pad1→PWR_GOOD / pad2→BAT_SW / pad3→PWR_ON★) · D− 侧 ESD 三件 (★`R4`/`R9` 落表★) · S6 布局修正 (★真实位移只有 `R_SEL_D3_P` 一处★) · S8 布线归零 (★unconnected **45 → 0**★) ⇒ ★**⇒ 板 md5 变一次 + 封装数变一次 + 位号后缀变一次 + 落位变一次 ⇒ MECH 侧凡【读板】的判据都要同一次重锚** ★
★**⑤ 为什么不能「改基线数字」了事**: 那是「悄悄换真源」(★本项目 ISS-273/275 花大力气堵掉的洞★) ⇒ ★**必须照 SW 侧 ISS-284 的形状做成【一个由单号背书、有台账可查、fail-closed】的显式动作 ⇒ 判据只许变严, 不许放松** ★
★**⑥ 收工清单 (MECH 侧没人写)**: HW 侧那条在 ISS-292 的 B4 里补 (★作业包「重锚」现在 grep = 0 处★) ⇒ ★**MECH 侧要重锚的至少五条: ① 两道闸的板/`.kicad_pro` 基线 ② ISS-286 已台账化的网表/脚表/BOM 链头 ③ 三条开口 (DEBUG/UART/USBC) + 固定孔清空区 + `J_USB_C` 座体 `F.Fab` 几何 ④ S6 那 20 个落位坐标与禁入区/承区 ⑤ 帧标 id 统一 (`B160x100` vs `160x100-bench` vs `F30A`/`60x30-setA` ⇒ 指同一批帧 ⇒ 这条 main 还没裁 (U-274-6) ⇒ 只登记 need, 不许自己裁★)** ★"""

NOTE_295 = """★★2026-11-17 17:5x 继续执行后继计划 job (775d9893) 新开 ★★: ★**依据 = main 17:4x~17:5x 本机实读 (`MECH/check_board_frame_coords.py` L79 · `MECH/check_demo_struct_truth.py` L81 · `grep -rn reboard MECH/*.py` = 0 · SW 侧 `check_demo_panel_spec.py` 的 `check_r6_hard_protected()` 与 `SW/SW_MD5_BASELINE_LEDGER.md` §1 · 落表台账 §16.2 现链头) ★** ★ ⇒ ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律 (★本单只动 MECH 侧两道闸 + 一页 MECH 收工清单, 不动板·不动网表·不动落表台账★) ★** ⇒ ★**零写板 · 零落表** ★ ⇒ ★**任务书全文 = `state/dispatch_briefs/ISS-295_mech_legal_reboard_mechanism.md` (★11595 B · 已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ⇒ ★**第一条 (必做)**: 先 cat 那份任务书全文 ★ ⇒ ★**本单是「板只改一次」那一趟开工前 MECH 侧的最后一件前置**: 那趟一开工板 md5 就变 ⇒ MECH 两道闸当场假红 ⇒ ⇒ 假红会被读成「板改坏了」⇒ ⇒ 有人去改板凑绿 ⇒ ⇒ 最坏 = 把 `C_VBUS_GND` 装回板上 (ISS-289 交卷单点名的 2-4 周 + ¥4-8K) ★ ⇒ ★**本单零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律自己网上查 + 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★"""


def main() -> int:
    if not os.path.exists(BRIEF):
        print("⚠ 缺 brief 文件: %s ⇒ 中止" % BRIEF)
        return 1
    with open(BRIEF, encoding="utf-8") as f:
        brief = f.read()

    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if os.path.exists(LOG):
            shutil.copy2(LOG, LOG + ".bak_20261117_1750_cron775d_open_iss295")
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        if any(it.get("id") == "ISS-295" for it in issues):
            print("· ISS-295 已存在 ⇒ 幂等跳过")
        else:
            issues.append({
                "id": "ISS-295",
                "title": TITLE_295,
                "severity": "high",
                "source_blocker": None,
                "source_agent": "main",
                "desc": DESC_295,
                "owner": "mech-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-20",
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": NOTE_295,
                "dispatched_at": "",
                "task_brief": brief,
            })
            with open(LOG, "w", encoding="utf-8") as f:
                yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
            print("· ISS-295 已开 (owner=mech-lead · status=open)")

        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-295", "agent": "mech-lead", "at": TODAY,
            "brief": brief[:300]})
        with open(DL, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        print("· dispatch_log 已写 (ISS-295 → mech-lead)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
