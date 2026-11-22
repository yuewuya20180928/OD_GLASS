#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0405_main_open_iss350.py
==================================================
main (项目总工) 开 ISS-350 (sw-lead · Q3 分档口径写回 SW 侧) 并原子写进 state/issue_log.yaml
★只写 issue_log.yaml (main 的地界) · 零写板 · 零落表 · 零写别人的分片 · 零外发★
用法: python3 state/_apply_20260723_0405_main_open_iss350.py [--dry-run]
"""
import os
import shutil
import sys
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

TITLE = ("★★[★新主线·PCB 线·存储轴 Q3 分档口径写回 SW 侧·纯口径·零写板] ★★【ISS-346 已签收 ⇒ Q3 从「整卡」改成"
         "「分档」⇒ SW 侧自己的分片 `sw.yaml` 的措辞还是旧的 ⇒ 机器读到的还是错的口径 ⇒ 把 3 条措辞订正写回"
         " + 补登记分档结论】★★ ★**只改措辞与登记, 不改网表真源 / 不改脚表 / 不改 BOM / 不改板 / 不代老板拍板**★")

DESC = ("★**main 2026-11-23 04:0x 本机实读 + 实跑 (不抄任何 agent 报告)★** ⇒ ★**① 题面**: ISS-346 (sw-lead · Q3 存储轴"
        "可判矩阵) 已由 main 于 03:4x 签收 (★签收闸 `state/_apply_20260723_0345_main_sign_iss346.py` 21 条验收全绿 + "
        "`--self-test` 3/3 ALL TESTS PASS★) ⇒ **[实测] 机器判决 (5×4 矩阵 20/20 格 · failures=0 · 生成器裸跑 rc=0)** = "
        "① 只 ADB push 档 ⇒ 板侧零动作 ⇒ 不卡 ② 外挂 SPI-NOR 档 ⇒ `J_BOOT1` 焊盘位已在板 (6 pad @126.3,58) + 4 条 0Ω "
        "串阻位必装 ⇒ PCB 层零动作 ⇒ 台架板档与产品板档都不卡 ③ eMMC 档 ⇒ 板宽 12→15 mm ⇒ 台架板档 B160x100 板面代价≈0 ⇒ "
        "不卡 ⇒ ⇒ ★**只有「eMMC + 产品板档 (F30A / P60x15)」才卡 (时限型)**★ ⇒ ★**⇒ Q3 不再以「整卡」形式占着板那一趟的"
        "阻塞位**★ ⇒ ★**② 要改的**: `state/fragments/sw.yaml` 的 `iss338_need_boot_storage_answer` 三条措辞 = "
        "「3 条 SPI_*_BOOT」⇒ ★**4 条**★ (网表 L202/L204/L206/L208) · 「外挂 SPI-NOR ⇒ 板要重出」⇒ ★**不成立**★ (走 "
        "J_BOOT1 焊盘位 ⇒ 板侧零动作) · 问原厂那句 ⇒ ★**改问「SoM 侧是否引出这 4 条 SPI boot pin (我方网表侧记为 SoC_NC)」**★ "
        "⇒ ★**③ 配套**: 补登记 Q3 分档结论 (含音频轴「与存储轴互不依赖」一条·★音频做不做不判/不建议/不代拍★)★ ⇒ "
        "★**④ 为什么现在派**: sw-lead 名额在 ISS-346 签收后已释放 (★本单是 sw-lead 本轮唯一在飞单·一个 agent 同时只跑一个写会话★)★ "
        "⇒ ★**⑤ 边界**: 零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 必须逐字节不变) · "
        "零落表 · 零改闸 · 只写自己的分片 sw.yaml + 交卷页 + logs/iss350/ · 零外发 ★")

BRIEF = ("★**题**: ISS-346 (Q3 存储轴可判矩阵) 已由 main 于 2026-11-23 03:4x 签收 ⇒ Q3 从「整卡」变成「分档」 ⇒ SW 侧 "
         "(你的分片 `sw.yaml`) 的措辞还是旧的 ⇒ 机器读到的还是错的口径 ⇒ ★**本单 = 把 Q3 分档口径写回 SW 侧 (★纯口径·零写板·零落表★)**★ "
         "★**做 4 件**: ① 改 `sw.yaml` 的 `iss338_need_boot_storage_answer` 三条措辞 (3 条 SPI_*_BOOT ⇒ ★**4 条**★ = "
         "SPI_SCLK_BOOT / SPI_CSn_BOOT / SPI_MOSI_BOOT / SPI_MISO_BOOT = 网表 L202/L204/L206/L208 · 「外挂 SPI-NOR ⇒ 板要重出」"
         "⇒ ★**不成立**★ ⇒ 改「走 `J_BOOT1` 焊盘位 ⇒ 板侧零动作, 不重出板」· 问原厂改问「SoM 侧是否引出这 4 条 SPI boot pin」) "
         "★**只走 `state/frag_write.py --agent sw-lead --set-json <file> --set-field answers`·禁止手改 YAML·零重复 key**★ "
         "② 补登记 Q3 分档结论 (--add-claim / --add-answer) ★**只登记·不新增拍板项·不代拍**★ "
         "③ 复核 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 里 4 条 SPI_*_BOOT 仍判【必需】 (★与 ISS-344 口径一致·★不许改那个文件★) "
         "④ 交卷页 `HANDOFF/2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md` (★骨架已由 main 预落·B0~B7 齐全 + 引用 MISS=0 + 板指纹前后双证★) "
         "★**纪律**: 零写板 · 零落表 (不改网表/脚表/BOM/原理图/闸) · 只写 sw.yaml + 交卷页 + logs/iss350/ · ★**零外发**★ · "
         "证据分级必标 · 不替老板拍板 · 写分片只用 frag_write.py ★**必跑**: `python3 state/merge.py` (rc=0) && "
         "`python3 state/gate_check.py` (★Q1 必须 18/18★) && `python3 state/frag_write.py --agent sw-lead --show` && "
         "`md5sum HW/PCB/demo_mainboard.kicad_pcb` (必须 611b869e13518c3c023fb178f91a0075) ★ "
         "★**任务书全文**: `state/dispatch_briefs/ISS-350_sw_q3_storage_tier_writeback.md` (★check_brief_commands.py --brief-file rc=0★) ★")

NOTE = ("★★2026-11-23 · cron 775d9893 (ARS45 继续执行后继计划) 开单并派出 (★项目总工 main★) ★★ "
        "★**开单依据**: ISS-346 签收后 Q3 存储轴从「整卡」变「分档」(★机器判决 20/20 格★) ⇒ SW 侧措辞跟不上 ⇒ 开本单; "
        "★**判定**: 纯口径类 · 零写板 · 零落表 (★符合「板只改一次」纪律: 先派纯分析/作业包类★) · ★**Q3 的卡不卡范围已收窄**★ "
        "(★台架板档 ⇒ 不卡; 产品板档 + eMMC ⇒ 才卡·时限型★) · 老板拍板面 §① 第 6 行已按此订正 "
        "(DECISION_ONE_PAGER_2026-11-22.md §① 第 6 行 + §⑨) · 本单不新增拍板项 · 音频轴只登记「与存储轴互不依赖」一条 "
        "(★不做/不做的判断仍不代拍★) ★ ★**派活时刻**: 2026-11-23 04:0x · ★**status 落 fixing ⇒ 兄弟 job fb67af40 的 "
        "advance.py --json 看不见本单 ⇒ 不会重复派** ★")

ENTRY = {
    "id": "ISS-350",
    "title": TITLE,
    "severity": "medium",
    "source_blocker": "ISS-346",
    "source_agent": "main",
    "desc": DESC,
    "owner": "sw-lead",
    "reporter": "main",
    "raised": "2026-11-23",
    "due": "2026-11-24",
    "status": "open",
    "external": "false",
    "task_brief": BRIEF,
    "dispatched_at": None,
    "verify_by": "main",
    "verify_result": None,
    "note": NOTE,
}


def yaml_dump_entry(e):
    import yaml
    return yaml.safe_dump([e], allow_unicode=True, sort_keys=False, width=200,
                           default_flow_style=False)


def main():
    src = open(LOG, encoding="utf-8").read()
    if "\n- id: ISS-350" in src:
        print("★ISS-350 已在台账 ⇒ 不重复开单")
        return 0
    chunk = yaml_dump_entry(ENTRY)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    if "--dry-run" in sys.argv:
        print(chunk)
        return 0
    bak = LOG + ".bak_%s_main_open_iss350" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src + chunk)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    # 写回自检
    import yaml
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)
    if isinstance(items, dict):
        items = list(items.values())
    ids = [i.get("id") for i in items]
    print("★台账条数 = %d · ISS-350 在盘 = %s · 零重复 id = %s · 备份 %s"
          % (len(ids), "ISS-350" in ids, len(ids) == len(set(ids)), os.path.basename(bak)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
