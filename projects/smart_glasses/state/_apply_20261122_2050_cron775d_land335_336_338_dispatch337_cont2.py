#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-22 20:5x · 项目总工 moli

★**本轮三件事 (★一件都不能少★)**:
  ① ★**ISS-335 / ISS-336 / ISS-338 落地 (fixing → verified)** — 三单 2026-11-19 就交卷了, 但★**签收那一步被 token 限额掐掉** (★整个流水线 3 天 18 小时零产出·全仓零文件改动 2026-11-19 02:42 → 2026-11-22 20:47★) ⇒ ★**本 job 2026-11-22 20:5x 本机逐件独立复核后签字** (★不抄 agent 报告★)
  ② ★**ISS-337 cont2 续做派活** — cont1 (2026-11-19 02:3x) 被 token 限额掐死在半路 ⇒ ★**成果 3 件已在盘·还差 4 件** ⇒ ★**续做不是从零**
  ③ ★**机制侧 5 条 need 落裁 (main 的地界·不占老板拍板面)** — 三个总工交回的 need 全部是机制地界 ⇒ ★**裁完老板手上只剩 7 个字母**

★**纪律**: 零写板 · 零落表 · 零改闸 · 零改生成器 · 零外发 · 只写 main 自己的分片(另脚本) · 不替老板拍板
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-22"
STAMP = "20261122_2050"

BRIEF_337_CONT2 = open(os.path.join(
    HERE, "dispatch_briefs", "ISS-337_hw_segment_parity_cont2.md"), encoding="utf-8").read()


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


VERIFY_335 = (
    "✅ verified (★main 2026-11-22 20:5x 本机独立复核·不抄 agent 报告★) ⇒ 交卷物在盘: "
    "· 闸本体 `SW/tools/check_onepass_sw_release.py` (31,029 B @2026-11-19 00:43) "
    "· 交卷页 `HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md` (B0~B6 六块齐全·gate_check 实测 sw-lead 6/6 缺: 无) "
    "· 分片 `state/fragments/sw.yaml` (★`grep -c iss335` = **13** 条·零重复 key★) "
    "★**main 本机实跑复核 (2026-11-22 20:4x)**: `TMPDIR=$PWD/tmp python3 SW/tools/check_onepass_sw_release.py` ⇒ **rc=0** · "
    "**10 道闸: 绿 10 / 红 0** ⇒ 判决「★SW 侧软件可以出 Gerber★」(★只代表 SW 侧这 10 道闸全绿·不等于整条板链全绿·HW/MECH 侧的闸另算★) · "
    "★**影子道 (默认不参与判决)**: `SW/tools/check_sw_ref_reachability_v2.py` ⇒ rc=0 ✔ 绿 ⇒ ★**v2 当天读数照样打印·main 想切版时手里已有 v1/v2 对照** ★ "
    "★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 (★17 天★) ⇒ **G1 仍开, 不许投板** "
    "★**main 就它交回的 1 条 need 已裁 (★机制地界·不占老板拍板面★)**: `iss335_ref_gate_v1_or_v2` ⇒ **采纳选项 A (判决清单用 v1 + v2 走影子道)** "
    "★**理由 (三条·★都在 sw-lead 自己的 item 里★)**: ① 清单完备性基准必须含 ISS-321 实测表那 10 道 (★该表第 2 道就是 v1·只列 v2 会与当天必跑闸脱钩★) "
    "② v2 已 verified 但**还没挂链** ⇒ 盘上无日常链背书 · ③ v2 比 v1 严 ⇒ 当天 v1 绿 v2 红时, ★**现场第一反应会去改板凑绿 ⇒ 反而放大「板 md5 变第二次」的风险** ★ ⇒ ★**切换命令留着**: `--ref-gate v2` / `--ref-gate both` / `--shadow-strict` ★"
)

VERIFY_336 = (
    "✅ verified (★main 2026-11-22 20:5x 本机独立复核·不抄 agent 报告★) ⇒ 交卷物在盘: "
    "· 闸本体 `MECH/check_board_frame_freeze_gate.py` (40,105 B @2026-11-19 01:15) + 自测 `MECH/check_board_frame_freeze_gate_selftest.py` (21,199 B @01:16) "
    "· 交卷页 `HANDOFF/2026-11-19_mech-lead_ISS336_板框冻结闸实现.md` (B0~B6 六块齐全·gate_check 实测 mech-lead 6/6 缺: 无) "
    "· 分片 `state/fragments/mech.yaml` (★`grep -c iss336` = **8** 条·零重复 key★) "
    "★**main 本机实跑复核 (2026-11-22 20:4x)**: `TMPDIR=$PWD/tmp python3 MECH/check_board_frame_freeze_gate.py` ⇒ **rc=2 · 判红 1 条 = C7** "
    "(★C7 = need `proto_pcb_freeze_gate` 未闭合 ⇒ ★**「今天红 = U-1 还没拍」= 正确红·不是闸坏了**★) ⇒ ★**C1~C6 全绿** (板厚档位 / 帧 / 层数 / 孔位 / 36 档 can_open 全部自洽) "
    "· `python3 MECH/check_board_frame_freeze_gate_selftest.py` ⇒ **rc=0 · 11/11 条用例与预期一致** (RC-1~RC-6 六条反向用例全抓到 + 正向对照全绿 + 真源/阈值自证过) "
    "· ★**12 件受保护文件 md5 逐件「同」(板 / 网表 / 脚表 / BOM / MECH 真源 / 分片 / BOARD_FRAME_CALIBER.md) ⇒ 真件零改动** ★ "
    "★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板** "
    "★**main 就它交回的 1 条 need 已裁 (★机制地界·不占老板拍板面★)**: `iss336_mech_board_frame_freeze_gate_chain_decision` ⇒ "
    "**采纳 mech-lead 的建议: 【不挂日常链】+ 配替代机制** ⇒ ★**理由**: ① C7 现在必红 ⇒ 挂日常链 = 门禁链天天红 ⇒ **真红被淹没**; "
    "② 这道闸判的是**一次性事件**「U-1 拍没拍」·与 EXTRA_GATES 那几道判**常态漂移**的闸生命周期不同; "
    "③ ★**替代机制 = 板那一趟 S1 开工前单次跑 `python3 MECH/check_board_frame_freeze_gate.py` ⇒ rc 必须 0** ⇒ ★**不许用「反正闸红着」当开工的理由** ★ "
    "★**U-1 落表格式 (三处缺一处闸还红·★已转写进 pm.yaml 的 answer·★board frame 三选一 (B160x100 / F30A / P60x15) 仍是老板级·main 不代拍★)**: "
    "① `state/fragments/mech.yaml` 的 `needs_closed[]` 一条 `key=proto_pcb_freeze_gate` · ② `answers[]` 同 key 一条·value 正文逐字含 **帧 id + 板厚 + 层数** "
    "(★推荐逐字照抄: `U-1 板框冻结: 帧 id = F30A; 板厚 = 1.00 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。`★) · ③ `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES.current_frame` 改成认领的帧 id "
    "★**落完 ⇒ 七条全绿 rc=0** ★"
)

VERIFY_338 = (
    "✅ verified (★main 2026-11-22 20:5x 本机独立复核·不抄 agent 报告★) ⇒ 交卷物在盘: "
    "· 主交付物 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` (39,713 B @2026-11-19 01:47) "
    "· 交卷页 `HANDOFF/2026-11-19_sw-lead_ISS338_9条单端脚固件引用.md` (21,409 B @01:47 · B0~B6 六块齐全·gate_check 实测 sw-lead 6/6 缺: 无) "
    "· 证据 `logs/iss338/` 28 件 · 分片 `state/fragments/sw.yaml` (★`grep -c iss338` = **19** 条·零重复 key★) "
    "★**main 本机独立复扫 (★2026-11-22 20:4x·★不算抄它的报告·★直接 grep `SW/**` 排除本单交付物★)**: "
    "★**9 条网逐条 `-w` 整词命中文件数 = 全 0** ⇒ `CAM_RESET_N` 0 · `FSIN_OUT` 0 · `JTAG_TDI` 0 · `LED_G_D` 0 · `SPI_MISO_BOOT` 0 · `SPI_MOSI_BOOT` 0 · `SPI_SCLK_BOOT` 0 · `UART_RX` 0 · `USB_CC2` 0 ★ "
    "★**对照组 (证明扫法本身有效·不是扫不出来)**: `BAT_DET` 命中 **10** 个文件 · `RESET_N` **7** · `UART_TX` **1** ⇒ ★**扫法已被控制网自证** ★ "
    "★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板** "
    "★**main 采信它的分级结论 (sw-lead 推翻 main 先前 4 条口径·★经复扫确认它对★)**: 必需 2 (`CAM_RESET_N` / `LED_G_D` ★同族 `LED_B_D`=105 段 `LED_R_D`=169 段都有铜·只它 0 段 ⇒ 该布没布·且 `D_LED_G` 被 2 个闸脚本硬编码 = 真代码路径★) "
    "· 可悬空候选 6 (`UART_RX` ★SW 侧串口实测只读·写方向 0 行★ / `USB_CC2` ★见下面 main 的独立裁决·★已从「候选」升为【必需】★ / 其余 4 条) · 待定 1 (`USB_CC2` 的 USB-IF 条款) "
    "★**★main 就它交回的 3 条 need 已裁 (★机制地界·不占老板拍板面·★全部落进 pm.yaml 的 answers★)**: "
    "① `iss338_need_usbif_cc1_cc2_rule` ⇒ **main 自己查 (★老板 2026-11-12 02:02「不再发信·全靠自己查资料」★)·[官网]**: USB Type-C 规范原文 "
    "「★The USB Type-C receptacle presents Rd on both of its CC pins because a CC pull-down must be present for the receptacle to indicate that it wants to consume VBUS current.★」"
    "(★usb.org《USB Type-C Cable and Connector Specification》R1.0/R2.0 章节文本★) ⇒ ★**USB 2.0-only 插座 = 双路 Rd ⇒ USB_CC2 不可悬空** ⇒ "
    "★**推翻 sw-lead 的「板侧默认 NC + 保留 R_CC2_D」建议 ⇒ USB_CC2 判【必需】(与 need-4b 早先口径一致) ⇒ 板侧不许标 NC** ★ "
    "(★[媒体] TI《A Primer on USB Type-C》同向: 「Note that one of the CC lines may become VCONN」⇒ 另一条仍须 Rd 做方向检测★) · "
    "★**降级方案 (不阻塞板那一趟)**: 若那一趟最终选了带 PD 的 Type-C 控制器芯片且其 datasheet 明写单 Rd ⇒ 按该 datasheet 复核这一条 · **但 `R_CC2_D` 已在板上 ⇒ 板子不用重出** ★ "
    "② `iss338_need_boot_storage_answer` ⇒ **[实测] 网表口径已定**: `HW/netlist_v1.csv` P3 区 `J_BOOT1` 整件 **DNP** (★原文「SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR 启动存储 (焊盘位可留作扩展)」·pin5/pin6 只预留 3V3/GND★) "
    "⇒ ★**3 条 `SPI_*_BOOT` 是「焊盘位预留」而不是 SoC 上拉脚 ⇒ 板那一趟按 DNP + 板侧标 no-connect 处理, 不进 S8 布线目标** ★ "
    "⇒ ★**但 Q19「内置 boot storage 还是外挂 SPI-NOR/eMMC」在网表里仍是 `[待原厂]` 口径 ⇒ 板那一趟开工前必须再确认一次 (★若拍成外挂 SPI-NOR ⇒ J_BOOT1 改必装 + 3 条网要布线 ⇒ 那要重新算「板只改一次」⇒ 必须赶在板那一趟之前拍·不许板画完再改★)★ · "
    "★**降级方案**: 查不到就按 DNP 走 (★主板侧不挂启动存储芯片是【独立于 Q19】的保守选择·★rootfs 走 SoM 板载 eMMC/SD★) ★ "
    "③ `iss338_need_jtag_group_decision` ⇒ **[实测] 裁 JTAG 整组保留, 不裁 TDI**: 网表 P8 区 `R_JTAG_TCK/TMS/TDO/TDI` 四颗串阻 + `J_DEBUG` (1×4 1.27mm 调试排针·★原文「调试用, 不装贴片」★) + `TP_JTAG` ⇒ "
    "★**4 线里只裁 TDI = 装上去却不能用的调试口** ⇒ ★**JTAG_TDI 判【必需】(进 S8 布线目标·一条单端网·成本极低) ⇒ 不是悬空候选** ★ "
    "(★注意: JTAG 是**硬件调试口**不是应用固件信号 ⇒ ★**「SW/** 零引用」对它不构成「可悬空」的证据★ ⇒ ★**ISS-338 的 SW 引用判据只适用于固件信号, 不适用于调试口★ —— 这是 main 给 sw-lead 口径补的一条边界★) ★"
)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []

        # ① ISS-335 / ISS-336 / ISS-338 落地
        for iid, vres in (("ISS-335", VERIFY_335), ("ISS-336", VERIFY_336), ("ISS-338", VERIFY_338)):
            it = idx.get(iid)
            if not it:
                print("· %s 不存在 (异常)" % iid)
                return 1
            if it.get("status") != "verified":
                it["status"] = "verified"
                it["verify_result"] = vres
                it["verify_date"] = NOW
                it["verify_by"] = "main"
                applied.append("%s fixing → verified (★main 2026-11-22 20:4x~20:5x 本机独立复核★)" % iid)
            else:
                applied.append("%s 已是 verified (跳过)" % iid)

        # ② ISS-337 cont2 续做 (status 保持 fixing)
        i337 = idx.get("ISS-337")
        if not i337:
            print("· ISS-337 不存在 (异常)")
            return 1
        tb = i337.get("task_brief") or ""
        if "ISS-337 · hw-lead · ★★cont2" not in tb:
            i337["task_brief"] = tb + "\n\n---\n\n" + BRIEF_337_CONT2
            applied.append("ISS-337 task_brief += cont2 (★cont0+cont1 原文逐字保留★) · status 保持 fixing")
        else:
            applied.append("ISS-337 cont2 已在 brief 里 (跳过)")
        i337["dispatched_at"] = NOW
        i337["note"] = (str(i337.get("note") or "") + " ★★2026-11-22 20:5x · cron 775d9893 派 cont2 (★**续做不是从零**★)★★ "
                        "★**cont1 (2026-11-19 02:3x) 的子会话被【Token Plan 用量上限】掐死在 02:42 (★错误码 2056·不是技术失败★) ⇒ 整条流水线停摆 **3 天 18 小时** (★2026-11-19 02:42 → 2026-11-22 20:47·全仓零文件改动★)★ ★"
                        "★**派活方 2026-11-22 20:5x 本机实读盘面 ⇒ cont1 的 6 处缺口: 【已做完 3 件】(selftest 用例 5 已修 ⇒ 末行 ALL TESTS PASS·归一化定义已钉死成 V1 ⇒ 官方 2649 vs 现役 2582·main 两条独立发现已复算落 logs/iss337/17) / 【还差 4 件】(G1 B4 追加·G2 写分片·G3 band 口径统一到脚本真值·G4 件数 13 + 空指针清理)★ ★"
                        "★**任务书全文**: `state/dispatch_briefs/ISS-337_hw_segment_parity_cont2.md` (★`check_brief_commands.py --brief-file` rc=0★) ★").strip()

        out = dict(log)
        out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cron775d_%s_land335_336_338_dispatch337cont2" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        # ③ dispatch_log
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == "ISS-337" and "cont2" in str(d.get("brief")) for d in disp):
            disp.append({
                "issue": "ISS-337", "agent": "hw-lead", "at": NOW,
                "brief": "★**cont2 续做派活 (★2026-11-22 20:5x·cron 775d9893★)** ★**为什么**: cont1 (2026-11-19 02:3x) 被 Token Plan 用量上限 (2056) 掐死 ⇒ 流水线停摆 3 天 18 小时 ⇒ ★**成果 3 件已在盘·还差 4 件 ⇒ 续做不是从零** ★ "
                          "★**cont1 已做完**: selftest 用例 5 已修 (末行 ALL TESTS PASS·`tmp/iss337/seg_parity_selfcheck.py` @02:36 + `logs/iss337/19_*` @02:40) · 归一化定义钉死成 V1 (`logs/iss337/18_*` @02:42 · 官方 2649 vs 现役 2582) · main 两条独立发现已复算 (`logs/iss337/17_*` @02:35) ★ "
                          "★**还差 4 件**: G1 交卷页追加 `## B4 · 接口取值声明 (interface_claims)` (⇒ gate_check Q1 里 hw-lead 6/6 缺: 无) · G2 写 `state/fragments/hw.yaml` (⇒ `grep -c iss337` ≥ 5) · "
                          "G3 band 口径统一到脚本真值 (归一化 [2300,3200] · 铜长 [4600,5900]mm · 过孔 [380,520]·★老口径 [380,450] 会把现役臂 471/486/505 全误拦·官方板自己反而过★) · G4 §B3 件数改 13 + §5 两行臂读数写 [0数据] + 原因取本机 `tmp/iss337/sbx/run_sbx.out` 原文 (EXIT=124 / EXIT=143) ★ "
                          "★**任务书全文**: `state/dispatch_briefs/ISS-337_hw_segment_parity_cont2.md` (6,618 B · `check_brief_commands.py --brief-file` rc=0) ★ "
                          "★**边界**: 零写板 (板 md5 611b869e… + mtime 2026-11-06 07:07:17.362193413) · 零落表 · 零改闸 · 零改生成器 · 零改别人文档 · 只写 state/fragments/hw.yaml · 不自签 issue_log · 零外发 · 不替老板拍板 · 沙盒只写 tmp/iss337 + logs/iss337 · 不许重跑两条沙盒臂 ★",
                "job": "cron 775d9893 (ARS45 继续执行后继计划) · ★派活时刻 2026-11-22 20:5x · ★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job fb67af40 不会重复派** ★",
            })
        for iid, agent in (("ISS-335", "sw-lead"), ("ISS-336", "mech-lead"), ("ISS-338", "sw-lead")):
            if not any(isinstance(d, dict) and d.get("issue") == iid and "2026-11-22" in str(d.get("at")) for d in disp):
                disp.append({
                    "issue": iid, "agent": agent, "at": NOW,
                    "brief": "★**签收落地 (fixing → verified)** ★**为什么这一轮才签**: 该单 2026-11-19 交卷, 但★**签收那一步被 token 限额掐掉** ⇒ 整条流水线停摆 3 天 18 小时 (★全仓零文件改动 2026-11-19 02:42 → 2026-11-22 20:47★) ⇒ ★**2026-11-22 20:4x~20:5x main 本机逐件独立复核后签字 (不抄 agent 报告)** ★",
                    "job": "cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-22 20:5x",
                })
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cron775d_%s_land335_336_338" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))

    for a in applied:
        print("· " + a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
