#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-22 21:0x · 项目总工 moli

★**本轮: 把三个总工交回的 5 条 need 全部裁掉 (★机制地界·不占老板拍板面★)** ⇒ ★**老板手上只剩 7 个字母★**

★**为什么这一轮才裁**: 2026-11-19 三个总工交卷 (ISS-335 / ISS-336 / ISS-338) ⇒ ★**但签收 + 裁 need 那一步被 Token Plan 用量上限掐掉** ⇒ ★**整条流水线停摆 3 天 18 小时** ⇒ ★**本轮补裁** ★

★**纪律**: 只写 main 自己的分片 (state/fragments/pm.yaml) · 零写板 · 零落表 · 零改闸 · 零改别人分片 · 不替老板拍板 · 零外发
"""
from __future__ import annotations

import os
import shutil
import tempfile
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.join(HERE, "fragments", "pm.yaml")
STAMP = "20261122_2100"

A_335 = (
    "★★【main 裁 (2026-11-22 20:5x · 机制地界 · 不占老板拍板面)】★★ ★**采纳你的建议默认值 = 选项 A (判决清单用 v1 + v2 走影子道)** ★ ⇒ "
    "★**判决清单**: `check_sw_ref_reachability.py` (v1 · ISS-318 · 已挂链) 进判决 · ★**v2 (ISS-332) 走影子道** (只跑只打印·默认不参与判决) ★ "
    "★**切换命令留着 (哪天真要切)**: `--ref-gate v2` (判决换 v2 + v1 退影子) / `--ref-gate both` (两个都进判决) / `--shadow-strict` (影子道也参与判决) ★ "
    "★**三条理由 (都在你的 item 里·我采信)**: ① 清单完备性基准必须含 ISS-321 实测表那 10 道 ⇒ 该表第 2 道就是 v1 ⇒ 只列 v2 会与当天必跑闸脱钩 "
    "② v2 已 verified 但**还没挂链** ⇒ 盘上无日常链背书 ③ v2 比 v1 严 ⇒ 当天 v1 绿 v2 红时★**现场第一反应会去改板凑绿 ⇒ 反而放大「板 md5 变第二次」的风险** ★ ⇒ "
    "★**且影子口径下 v2 的读数每趟照样打印** ⇒ main 想切版时手里已有 v1/v2 当天结论是否一致的实测对照·不必当天临时重跑 ★ ⇒ "
    "★**⇒ 这条 need 从此闭合** ★"
)

A_USBIF = (
    "★★【main 裁 (2026-11-22 20:5x · ★机制地界 + 老板 2026-11-12 02:02「不再发信·全靠自己查资料」·★main 自己查了·不外发★)】★★ "
    "★**裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的「板侧默认 NC + 保留 R_CC2_D」建议【不采纳】** ★ "
    "★**[官网] 证据 (★USB Type-C 规范原文·★主板端是 Sink·Sink 侧必须有 Rd★)**: 「★The USB Type-C receptacle presents Rd on both of its CC pins because a CC pull-down must be present for the receptacle to indicate that it wants to consume VBUS current.★」 "
    "(★USB Type-C Cable and Connector Specification·usb.org 公开 PDF·R1.0/R2.0 章节文本★) ⇒ ★**USB 2.0-only 插座 = 双路 Rd ⇒ CC1/CC2 都要有 Rd ⇒ CC2 不可悬空** ★ "
    "★**[媒体] 同向旁证**: TI《A Primer on USB Type-C and Power Delivery Applications》「Note that one of the CC lines may become VCONN」⇒ 另一条仍须 Rd 做方向检测 ★ "
    "★**[媒体] 补充**: 网上常见的「单 Rd 省一颗电阻」做法只适用于 Source/DRP 侧 (规范原文: 「Only one of the CC1 or CC2 pins shall be in the SRC.Rd state」·★那是【源端】条款·不是插座端条款·★公开来源之所以「互相矛盾」就是这两条被混着引用了★)★ "
    "★**⇒ 结论**: ★**你原来的「待定」在规范层面不成立 ⇒ 它不是待定项, 是必需项** ★ ⇒ ★**这一条与 need-4b 早先口径 (必需 = 15 差分腿 + `USB_CC2` + `UART_RX`) 一致 ⇒ 不冲突** ★ "
    "★**降级方案 (不阻塞板那一趟)**: 若那一趟最终选了带 PD 的 Type-C 控制器芯片、且其 datasheet 明写单 Rd ⇒ 按该芯片 datasheet 复核这一条 ⇒ ★**但 `R_CC2_D` 已在板上 ⇒ 板子不用重出** ★ ⇒ "
    "★**这条 need 从此闭合** ★"
)

A_BOOT = (
    "★★【main 裁 (2026-11-22 20:5x · 机制地界)】★★ ★**裁决 = 3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect ⇒ 你的「J_BOOT1 DNP ⇒ 3 条可悬空」建议【不采纳】** ★ "
    "★**[实测] 盘面依据**: ① 网表 `HW/netlist_v1.csv` P3 区 `J_BOOT1` **整件 DNP** (★原文「SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR 启动存储 (焊盘位可留作扩展)」·pin5/pin6 只预留 3V3/GND★) "
    "② ★**但 `J_BOOT1` 的焊盘位【已经在板上】**(★板上位号清单实读: `J_BOOT1` 在盘★) ⇒ ★**「焊盘位预留」这条已经落地了** ★ "
    "★**⇒ 关键推理 (★这就是「板只改一次」的正确用法★)**: ★**布线保留的成本 ≈ 0 (3 条单端网), 事后收益 = 不用重出板** ⇒ "
    "★**若现在标 NC**: 将来老板拍「外挂 SPI-NOR」⇒ 必须重出板 ⇒ ★**违反「板只改一次」** ★ ⇒ "
    "★**若现在就布线**: 将来无论拍「外挂 SPI-NOR」(只需改 BOM 装件·**焊盘位已在**)还是拍「不挂」(**不装即可·多几段无用铜**) ⇒ ★**板都不用重出** ⇒ ★**⇒ 必须布线** ★ "
    "★**★这与 main 刚给 JTAG_TDI / UART_RX 定的边界是同一条**: ★**「布线保留的成本 ≈ 0, 事后不重出板」⇒ 调试口/预留位一律布线, 一律不许裁** ★ "
    "★**★但有一件【必须在板那一趟开工前】拍掉的事 (★老板级·我代拍不了★)**: 网表里 Q19「内置 boot storage 还是外挂 SPI-NOR/eMMC」仍是 `[待原厂]` 口径 ⇒ ★**若最后拍「外挂 eMMC」⇒ 板上要多一个 eMMC footprint (网表原文: 外挂 eMMC 方案 PCB 面积 +25% 且板宽 12→15mm) ⇒ 那要改网表 + 改板 ⇒ 必须赶在板那一趟开工前落进网表, 否则板 md5 变第二次** ⇒ "
    "★**这条已挂在老板拍板面 `q3_storage_and_audio` 上 (★逾期 26 天★)** ⇒ ★**它不是「等外部回信」, 是「等老板一个字」** ★ "
    "★**降级方案 (查不到/没拍时的默认)**: ★**默认按「SoM 板载 eMMC/SD」走 (⇒ 主板不挂启动存储芯片·J_BOOT1 不装) ⇒ 3 条 `SPI_*_BOOT` 布了但没人用·代价 = 3 段无用铜·换来板永不重出** ★ "
    "★**⇒ 这条 need 从此闭合 (板那一趟开工前的老板前置已单独挂面)** ★"
)

A_JTAG = (
    "★★【main 裁 (2026-11-22 20:5x · 机制地界)】★★ ★**裁决 = JTAG 整组【保留】⇒ `JTAG_TDI` 判【必需】(进 S8 布线目标) ⇒ 不是可悬空候选 ⇒ 你的「裁 TDI 就等于接受 JTAG 实不可用」这个两难, main 选「不裁」** ★ "
    "★**[实测] 盘面依据**: 网表 P8 区 `R_JTAG_TCK` / `R_JTAG_TMS` / `R_JTAG_TDO` / `R_JTAG_TDI` 四颗串阻**都在** + `J_DEBUG` (★1×4 1.27mm 调试排针·原文「调试用, 不装贴片」★) + `TP_JTAG` ⇒ ★**板上位号实读: `R_JTAG_TDI` 在盘** ⇒ ★**TDI 是「该布没布」(0 段), 不是「没人要」** ★ "
    "★**⇒ 关键推理 (同一条边界)**: ★**「布线保留的成本 ≈ 0 (一条单端网), 事后收益 = 不用重出板」⇒ 调试口一律布线** ⇒ ★**裁 TDI = 装上去却只能收不能发的调试口 = 做一个摆设** ⇒ 否决 ★ "
    "★**★★main 给 SW 侧补一条口径边界 (★这条是给你的判据补漏洞·★不是挑错★)★★**: ★**「固件零引用 ⇒ 可悬空」这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】** ★ ⇒ "
    "★**理由**: JTAG 与 UART 是【硬件接口】, 由调试器 / 探针驱动, 不由应用固件引用 ⇒ ★**SW/** 零引用对它不构成「可悬空」的证据** ★ ⇒ ★**所以你那 9 条里 `JTAG_TDI` / `UART_RX` 的「可悬空」结论, main 不采信 (★其余 7 条不涉及调试口·不受影响★)** ★ "
    "★**⇒ 这条 need 从此闭合** ★"
)

A_336 = (
    "★★【main 裁 (2026-11-22 20:5x · 机制地界 · 挂链是 main 的地界)】★★ ★**裁决 = 采纳你的建议: 【不挂日常链】+ 配替代机制** ★ ⇒ "
    "★**① 为什么挂日常链是错的 (三条·采信你的理由)**: C7 现在必红 ⇒ 挂日常链 = 门禁链天天红 ⇒ ★**真红被淹没**; 这道闸判的是**一次性事件**「U-1 拍没拍」·与 EXTRA_GATES 那几道判**常态漂移**的闸生命周期不同; "
    "★**⇒ 「不许挂进 state/gate_check.py 的日常链」这条, 现在写进 main 的口径了** ★ "
    "★**② 替代机制 (★不许用「反正闸红着」当开工的理由★)**: ★**板那一趟 S1 开工前, 必须单次跑 `python3 MECH/check_board_frame_freeze_gate.py` ⇒ rc 必须 0 ⇒ rc=2 (今天必红) = 【不许开工】** ★ ⇒ "
    "★**这条由 main 单独落成「板那一趟开工前置」, 不改你的闸、不改 gate_check.py** ★ "
    "★**③ U-1 落表格式 (三处缺一处闸还红·★已转写进 pm.yaml 的 answer·★board frame 三选一 (B160x100 / F30A / P60x15) 仍是老板级·main 不代拍★)**: "
    "① `state/fragments/mech.yaml` 的 `needs_closed[]` 一条 `key=proto_pcb_freeze_gate` · ② `answers[]` 同 key 一条·value 正文逐字含 **帧 id + 板厚 + 层数** "
    "(★推荐逐字照抄: `U-1 板框冻结: 帧 id = F30A; 板厚 = 1.00 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。`★) · ③ `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES.current_frame` 改成认领的帧 id "
    "★**落完 ⇒ 七条全绿 rc=0** ★ ⇒ ★**⇒ 这条 need 从此闭合** ★"
)

# need-4b 的【定稿】(★原地改 value·零重复 key★)
A_4B_FINAL = (
    "★★【main 裁 (2026-11-22 20:5x · ★need-4b 一次性分级【定稿】·★机制地界·不占老板拍板面★)】★★ ★"
    "★**依赖链已闭合**: need-4a → ISS-338 (verified 2026-11-22 20:5x·★main 独立复扫: 9 条网在 `SW/**` 整词命中全 0·对照组 `BAT_DET`=10 / `RESET_N`=7 / `UART_TX`=1 ⇒ 扫法已被控制网自证★) ⇒ ★**下面这条 = 24 条零铜网的分级定稿** ★ "
    "★**★★分级定稿 (★「必需 / 可悬空 / 待定」三档判据已定·名单待新基线重读·见第 3 条★)★★** ★ "
    "★**A 必需 (23 条)**: ① ★**15 条高速差分腿** (★`CSI_D0_*` / `DSI_D0_*` 族·★无商量空间·必须救回★) ② ★**8 条单端脚**: `CAM_RESET_N` (★dts `reset-gpios gpio1 RK_PB3` ⇒ 相机不出图则 MIPI-CSI 链死★) · "
    "`LED_G_D` (★同族 `LED_B_D`=105 段 / `LED_R_D`=169 段都有铜·只它 0 段 ⇒ 该布没布·且 `D_LED_G` 被 2 个闸脚本硬编码 = 真代码路径★) · `USB_CC2` (★[官网] USB Type-C 插座端双路 Rd 条款★) · "
    "`JTAG_TDI` (★调试口 ⇒ 「布线保留成本≈0·事后不重出板」★) · `UART_RX` (★同上·调试口★) · `SPI_SCLK_BOOT` / `SPI_MOSI_BOOT` / `SPI_MISO_BOOT` (★`J_BOOT1` 焊盘位已在板 ⇒ 布线保留·**不许标 NC**·否则老板拍外挂 SPI-NOR 就得重出板★) ★ "
    "★**B 可悬空 (1 条)**: `FSIN_OUT` (★条件: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作★) ★ "
    "★**C 待定 (0 条)**: ★**原先的两个待定项都被消解了** ⇒ ① USB-IF 条款 → [官网] 规范自证 ⇒ 归 A ② 启动存储 → 「布线保留」策略消解 ⇒ 归 A ⇒ ★**⇒ 待定档已空** ★ "
    "★**★★★【★★★必须一起读的第 3 条 (★main 2026-11-22 本机实读的独立发现·★这条比前两条都重要★★★)★★★】**: "
    "★**官方板那 24 条零铜网【不能直接当靶】** ★ ⇒ ★**[实测]** 官方板 (md5 `611b869e…`) 136 焊盘网 / 90 有铜 / **24 零铜**; ★**现役链终板 `v76mg1` = 7 条零铜** · `v76mz` = 12 · `best_unc23_clrfix` = 7 ⇒ "
    "★**官方板那 24 条里, 21 条在现役链终板 v76mg1 上【已经有铜】·两边都零铜只剩 3 条** (`CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N`) ★ ⇒ "
    "★**⇒ 「布线 45→0」的分母必须在【板那一趟的新基线】上重读** (★S1 位号改名必然重跑生成器 ⇒ 那一趟的板本来就是现役生成器出的 ⇒ **分母可能整个是错的**★) ⇒ "
    "★**⇒ need-4b = 【判据已定稿 · 名单待新基线重读】· 不是「24 条名单已定」** ★ ⇒ "
    "★**⇒ 并派一条硬要求给板那一趟**: ★**S1 改名后、动板之前, 必须先 fresh 读出【新基线的零铜网名单】, 再用上面 A/B/C 判据逐条分级, 再决定哪些进 S8 布线目标·哪些允许标 NC** ★ "
    "★**★不许拿官方板那 24 条直接当 S8 的布线目标清单 (★那 21 条在新基线上本来就通·照着做会白布 21 条或误判 21 条·★这正是「判据用错基线」的老坑★)★** ★ "
    "★**★另加一条判据替换 (★main 2026-11-22 独立复算★)**: ★**「归一化段数对齐」≠「同一块铜」** ⇒ ★**[实测]** 官方板 vs `best_unc23_clrfix`: 两板都有铜 86 条 ⇒ ★**铜长相符只有 21/86** ★ ⇒ "
    "★**⇒ 判据必须改成【逐网铜量名单 + 零铜网名单】双向, 不许拿归一化段数当唯一尺子** (★这条正是 ISS-337 cont2 要写进交卷页的 W3★) ★ ⇒ ★**⇒ 这条 need 从此闭合** ★"
)


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


def main() -> int:
    shutil.copy2(PM, PM + ".bak_" + STAMP)
    d = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    answers = d.setdefault("answers", [])
    have = {a.get("key") for a in answers}

    NEW = [
        ("iss335_ref_gate_v1_or_v2", "sw-lead", A_335,
         "HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md B5-1 · SW/tools/check_onepass_sw_release.py (--ref-gate / --shadow-strict)"),
        ("iss338_need_usbif_cc1_cc2_rule", "sw-lead", A_USBIF,
         "★[官网] USB Type-C Cable and Connector Specification (usb.org 公开 PDF) · ★[媒体] TI《A Primer on USB Type-C and Power Delivery Applications》 · SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md"),
        ("iss338_need_boot_storage_answer", "sw-lead", A_BOOT,
         "HW/netlist_v1.csv P3 区 J_BOOT1 (DNP 口径) · 板上位号清单实读 (J_BOOT1 在盘) · ★老板拍板面 q3_storage_and_audio"),
        ("iss338_need_jtag_group_decision", "sw-lead", A_JTAG,
         "HW/netlist_v1.csv P8 区 R_JTAG_TCK/TMS/TDO/TDI + J_DEBUG + TP_JTAG · 板上位号清单实读 (R_JTAG_TDI 在盘)"),
        ("iss336_mech_board_frame_freeze_gate_chain_decision", "mech-lead", A_336,
         "MECH/check_board_frame_freeze_gate.py (C1~C7 + RC-1~RC-6) · HANDOFF/2026-11-19_mech-lead_ISS336_板框冻结闸实现.md B5-1"),
    ]

    for key, to, val, ref in NEW:
        if key in have:
            for a in answers:
                if a.get("key") == key:
                    a["value"] = val
                    a["to"] = to
                    a["ref"] = ref
            print("· %s 原地改 value (零重复 key)" % key)
        else:
            answers.append({"key": key, "to": to, "value": val, "ref": ref})
            print("· %s 新增 answer (→ %s)" % (key, to))

    # need-4b 原地改 value (定稿版)
    hit = False
    for a in answers:
        if a.get("key") == "iss334_need4b_zero_copper_net_triage":
            a["value"] = A_4B_FINAL
            a["ref"] = "HW/PCB/ONETRIP_S8_MECHANISM_PATH.md · SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md (ISS-338) · logs/iss337/17_main_findings_recheck.txt (零铜网 24→7 · 逐网铜长 21/86)"
            hit = True
            print("· iss334_need4b_zero_copper_net_triage 原地改 value (定稿版)")
    if not hit:
        answers.append({"key": "iss334_need4b_zero_copper_net_triage", "to": "main",
                        "value": A_4B_FINAL,
                        "ref": "HW/PCB/ONETRIP_S8_MECHANISM_PATH.md · SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md (ISS-338) · logs/iss337/17_main_findings_recheck.txt"})
        print("· iss334_need4b_zero_copper_net_triage 新增 answer (定稿版)")

    d["updated_at"] = "2026-11-22 21:00"
    d["updated_by"] = "main"
    atomic_write(PM, yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100000))
    print("· pm.yaml answers 总数 = %d" % len(answers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
