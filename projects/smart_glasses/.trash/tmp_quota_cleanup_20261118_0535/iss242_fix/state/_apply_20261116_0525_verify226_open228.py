#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0525_verify226_open228.py
★main (moli) 手动清账 + 开新单 · 2026-11-16 05:25 (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★队列止血, 不是例行公事★)** ★★
· sw-lead 的 ISS-226 子会话 (`agent:sw-lead:subagent:dcd4e764`) ★**2026-11-16 05:16:32 被平台中止**
  (status=timeout · abortedLastRun=true · 最后两次 `edit` 的 toolResult = "Aborted")★
· ★**但成果已经全部落盘并全绿** ⇒ 不是"半成品僵尸", 是"**已交卷但交卷正文被中止**"★
  - 4/4 交付物在盘 (05:04 / 05:07 / 05:10 / 05:14)
  - `SW/tools/check_brightness_biosafety.py` rc=0 (C1..C6 全过) + `--selftest` rc=0 (13/13)
  - 分片 sw.yaml 真落盘 (05:12:52): artifact×3 / answer×1 (回 ISS-134 need) / claim×2 / need×1
  - 交接单 402 行, B1~B6 六块齐全, ★**零悬空引用** (A-28 那次编辑被中止 ⇒ 该行压根没写进去 ⇒ 无悬空)★
· ⇒ ★**落 ISS-226 = verified** (★main 2026-11-16 05:2x 自己实跑验收, 不是抄交卷报告★)
  ⇒ ★同时清掉僵尸 fixing (会话死但状态卡在 fixing ⇒ ★**占着 sw-lead 名额 ⇒ advance.py 永远派不出 sw-lead 的活**★)★

★★**ISS-228 新开 (sw-lead 名额空出来后唯一不与任何人抢的活)** ★★
· 来源 = ★**hw.yaml 里本来就挂着、至今没人接的跨域 need**★ `iss148_rk3572_gpio0_vccio_domain_check`
  (to=sw-lead, since 2026-11-02, due 11-03, ★**已逾期 13 天**★)
· ★**它卡的是原理图主线**: RK3572 GPIO0 (I2C0_SCL=GPIO0_B0 球 1K21 / I2C0_SDA=GPIO0_B1 球 U32) 到底挂哪个
  VCCIO 供电组 ⇒ 决定 ★**I2C_A 上拉最终电压域 (1.8V / 2.8V / 3.3V)**★ ⇒ 决定 ISS-211 缺陷① + d1 组怎么落表
  ⇒ ★**这不是 PCB 布线/布局类, 不是老板级拍板 ⇒ 可派** ★
· ★**零外发**: 官方口径一律【自己网上查】+ 标证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据]) + 查不到写降级方案 ★
"""
import os
import shutil
import datetime as dt
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

BRIEF_228 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: ★**把 RK3572 GPIO0 bank → VCCIO 供电组的官方映射核出来, 让「I2C_A 上拉最终电压域」从「拍不了」变成「可拍」**★ ⇒ 出 ★**(1) 官方口径自查结论 (含证据等级) · (2) 给 hw-lead 的可落表判据串 · (3) 机器门禁 + 反向用例 · (4) 交接单 + 分片**★ ⇒ ★**本单不许改 `HW/` 下任何文件**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 05:2x 实查, 不是推测★)** ★★
· ★**hw.yaml 里本来就挂着一条没人接的跨域 need**: `iss148_rk3572_gpio0_vccio_domain_check` (to=sw-lead, since 2026-11-02, due 2026-11-03 ⇒ ★**已逾期 13 天**★) ⇒ ★**它不是 main 编的活, 是项目里本来就挂着、没人接的单** ★
· ★**它卡的是原理图主线**: I2C0_SCL = ★**GPIO0_B0 (球 1K21)**★ / I2C0_SDA = ★**GPIO0_B1 (球 U32)**★ ⇒ 这两根脚挂哪个 VCCIO 组 ⇒ ★**I2C_A 上拉最终是 1.8V / 2.8V / 3.3V**★ ⇒ 决定 ★**ISS-211 缺陷① (I2C_A 上拉 4.7k/3.3V vs 网表 2.2k→1.8V 的矛盾) + d1 组怎么落表**★ ⇒ ★**落表定稿前不核, d1 只能悬着** ★
· ★**它不依赖任何在飞单** ⇒ 落在本轮 (sw-lead 名额刚被清出来) ⇒ ★**不占主线的时间窗** ★

★★**已有依据 (★全部来自项目内已有材料 + 你自己去查官方资料★, 不许编数★)** ★★
· ★**官方已定的部分** (`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §VCCIO, ★**[官网]+[实测]**★): RK3572 datasheet p.39 渲染图 (★`HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png`★) ⇒ `1.8V/3.3V GPIO supply voltage` 那行的 net 名 = ★**PMUIO1_VCC + VCCIO1_VCC + VCCIO2_VCC + VCCIO3_VCC + VCCIO4_VCC + VCCIO5_VCC + VCCIO6_VCC**★ (max ★**3.63 V**★); `1.8V only` 那行只有 ★**PMUIO0_VCC1V8 + VCCIO0_VCC1V8**★ (max 1.98 V); `1.2V/1.8V` 那行只有 ★**VCCIO7_VCC**★ ⇒ ★**⇒ 「VCCIO1_VCC 属 1.8V only」是 pdftotext 扁平文本的排版假象, 不是官方口径 (那份 txt 多行单元格错位)**★ ⇒ ★**「VCCIO1_VCC 能上 3.3V」是官方事实** ★
· ★**仍未定的部分 (★就是本单要干的★)**: ★**datasheet 没有 GPIO bank → VCCIO 组 的对应表**★ ⇒ ★**GPIO0_B0 / GPIO0_B1 具体挂哪个 VCCIO 供电组 = [0数据]**★ ⇒ ★**所以「I2C0 这两根脚能不能上 3.3V」目前仍无官方依据** ★
· ★**★本地 txt 只能当线索, 不能当结论★**: `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` 是 pdftotext 转出的扁平引脚表, ★**没有 bank↔GPIO 对照表, 只能靠引脚表顺序推断**★ ⇒ ★**推出来的结论一律标 [推算], 推不出就写 [0数据]** ★
· ★**SoM 侧**: SoM 模组 = ★**FET3572-C (瑞芯微 RK3572 核心板)**★ ⇒ 它自己的 IO 域电压可能由载板供电决定 ⇒ ★**BSP `rk3572.dtsi` 的 `io-domains` / pinctrl `rockchip,pins` 里带 VCCIO 网名**★ 是第二权威源 ⇒ ★**这是本单最该去查的那一条** ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**官方口径自查结论 (新建一份 md, 放 `SW/` 或 `HW/` 之外的 `SW/` 侧均可, ★但★不许写 `HW/` 下任何文件★)** ★ ⇒ 必须含: ★**(a) 检索面清单 (查了哪些官方源: Rockchip datasheet Rev 1.0/1.1 §2.6 引脚表 + §4 abs-max 表 / Rockchip 官方内核 `develop-6.12/rk3572-pinctrl.dtsi` / `arch/arm64/boot/dts/rockchip/rk3572.dtsi` 的 `io-domains` / Forlinx 载板手册的 VCCIO 供电网名 / 官方 WiFi&BT 模块的 VCCIO 划分)** ★ **(b) 逐源结论 + 证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据])** ★ **(c) 结论一句话: I2C0 (GPIO0_B0/B1) 的 IO 域电压能不能上 3.3V / 2.8V / 1.8V, 依据是什么** ★ **(d) ★查不到就明写 [0数据] + 三条降级方案 (各写清落到网表哪一行/哪个字段)** ★
② ★**给 hw-lead 的可落表判据串 (★这是本单对主线的实际贡献★)** ★ ⇒ 写成一段 ★**能直接粘进 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` 的作业条目**★: ★**(1) B-01/B-02 的 `imp` 与 `level` 最终取值 (多少 Ω / 拉到什么轨) · (2) 该取值引用的官方出处 (文件+章节/图) · (3) 若结论是 [0数据] ⇒ 给一条【保守默认 + 后续解锁条件】**★ ⇒ ★**不许替 hw-lead 改网表, 只给判据串** ★
③ ★**机器门禁 (新建脚本 + `--selftest` 反向用例)** ★ ⇒ 门禁要能抓住: ★**(a) 结论被换成无出处的数 · (b) 证据等级被抹 · (c) 降级方案被删 · (d) 「[0数据] 被悄悄改成一个具体电压」** ★ ⇒ ★**`--selftest` 必须每条反例都真的变红** ★
④ ★**交接单 + 分片** ★ ⇒ `HANDOFF/2026-11-16_sw-lead_ISS228_RK3572_GPIO0_VCCIO官方映射自查.md` (★B1~B6 六块齐全★) + ★**分片 `state/fragments/sw.yaml` (必须走 `python3 state/frag_write.py` 原子写★)** ★ ⇒ ★**并明确回掉 hw.yaml 那条 need `iss148_rk3572_gpio0_vccio_domain_check` (交答案, 让它变 answered)** ★

★★**边界 (★违反一条即本单无效★)** ★★
· ★**不许改** `HW/` 下任何文件 (★网表 / 脚表 / 板 / `.kicad_pro` / 原理图 / BOM / `SCHEMATIC_V1_SPEC.json` / `FET3572C_PIN_TABLE.csv` 一个字节不许动★) ⇒ ★**判据串只出文字, 落表由 hw-lead 做** ★
· ★**不许改** `MECH/` 下任何文件 ★
· ★**不许改** `state/issue_log.yaml` (★status 留给 main 落 verified★) / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/` / 别人的分片 ★
· ★**不许碰** PCB 布线 / 布局 / 板框 ★
· ★**不许把 [推算] 写成 [官网]/[实测]** ★ ⇒ ★**本地 txt 顺序推断出来的结论一律 [推算]; 查不到一律 [0数据]** ★
· ★**板端 [实测] = 0 条** (★板与屏不在本机 ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」★) ★
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到必须写降级方案** ★ ⇒ ★**不许写「等原厂回信」** ★
· ★**不许自签 issue_log** ★

★★**交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★)** ★★
```
python3 SW/tools/check_demo_panel_spec.py             # rc=0 (★R1~R5 一条不许被本单改红★; ★R6 若红 = ISS-223 落表后锚点过期, 写明原因, 不许自己去改锚点★)
python3 SW/tools/check_demo_panel_spec.py --selftest   # rc=0
python3 SW/tools/check_brightness_biosafety.py         # rc=0 (★ISS-226 的闸不许被本单改红★)
python3 SW/tools/check_brightness_biosafety.py --selftest  # rc=0
python3 state/merge.py && python3 state/gate_check.py # rc=0 且 【Q1 交付齐备率】 18/18
```
★**交卷前最后一件事**: ★**再实跑一次你新建的门禁 + `--selftest`** ⇒ ★**贴原样输出 + 贴「改坏必红」的对照 (把某条证据等级抹掉后变红)** ★

★★**已知会红、且不归你管的那两盏 (★提前说清, 免得你误修★)** ★★
· ★**`MECH/check_demo_struct_truth.py` 现在 G5b + C21 两组红** ⇒ ★**根因 = ISS-223 (hw-lead) 于 2026-11-16 05:18 重生成网表/脚表 (网表 md5 `3215020b…` / 脚表 `a600afae…`) ⇒ MECH 台账锚点过期** ★ ⇒ ★**不是你的锅, 不许为了让 MECH 闸变绿去改 `MECH/`** ★
· ★**`SW/tools/check_demo_panel_spec.py` 的 R6 现在红** ⇒ ★**同一个根因 (SW 台账锚点过期, 锚点写的是 `13f59a43…`, 盘上已是 `3215020b…`)** ★ ⇒ ★**不许自己去改锚点** ⇒ ★**那是 ISS-223 交卷后走 `SW/SW_MD5_BASELINE_LEDGER.md` §4 H-1 重锚流程的活 (等 hw-lead 交卷后再派)** ★
"""


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {i.get("id"): i for i in issues}

    # ---------- 1. ISS-226 → verified (main 自测验收, 清僵尸占位) ----------
    i226 = by_id["ISS-226"]
    assert i226.get("status") == "fixing", i226.get("status")
    i226["status"] = "verified"
    i226["verify_by"] = "main"
    i226["verify_date"] = TODAY
    i226["verify_result"] = (
        "★main 2026-11-16 05:2x 自测验收 (非抄交卷报告)★\n"
        "· 交付物 4/4 在盘: ①SW/SW_BRIGHTNESS_CONTROL_POLICY.md (17302 B, 05:04:32) "
        "②SW/BRIGHTNESS_API_BLUE_RATIO.md (14098 B, 05:07:37) "
        "③SW/tools/check_brightness_biosafety.py (26811 B, 05:10:34) "
        "④HANDOFF/2026-11-16_sw-lead_ISS226_蓝光通道占比上限与亮度API.md (39863 B, 05:14:09, 402 行, B1~B6 六块齐全) ★\n"
        "· 门禁实跑 (main 自己跑的): `python3 SW/tools/check_brightness_biosafety.py` → rc=0 (C1 判据数值锁定 / "
        "C2 越限后果链 / C3 API 蓝通道占比量 / C4 跨域只读对账 / C5 不许编造实测值 / C6 降级方案 ⇒ 全过) ; "
        "★`--selftest` → rc=0 (13/13 反向用例全抓到) ★\n"
        "· 分片真落盘: state/fragments/sw.yaml (mtime 05:12:52) ⇒ artifact×3 (policy / api / gate) + "
        "answer×1 (回 mech-lead 的 `iss134_sw_blue_drive_ratio_cap`) + interface_claim×2 (`sw_brightness_api_blue_ratio_field` "
        "/ `sw_brightness_api_blue_ratio_board_state`) + need×1 (`iss226_land_verified_and_reanchor` to=main) ★\n"
        "· ★**交卷正文被平台中止, 但成果全绿** ⇒ 子会话 `agent:sw-lead:subagent:dcd4e764` 于 2026-11-16 05:16:32 "
        "status=timeout (最后两次 `edit` 的 toolResult = \"Aborted\") ⇒ ★**不是半成品, 是【已交卷但交卷正文被砍】** ★\n"
        "· ★**中止留下的缺口已自查**: 交接单里 ★**零悬空引用** (A-28 那次编辑被中止 ⇒ 该行压根没写进去 ⇒ 没有任何地方引用 A-28)★ ⇒ "
        "文件 402 行、尾部「阻塞: 无阻塞」段完整 ⇒ ★**不构成交付缺口, 不需要续做** ★\n"
        "· ★**同时清掉僵尸 fixing**: 会话死但状态卡在 fixing ⇒ ★**占着 sw-lead 名额 ⇒ `state/advance.py` 的 in_flight 规则会让 "
        "sw-lead 本轮拿不到任何新活 (advance.py --json 的 internal 段本轮为空就是被它挡的)** ★\n"
        "· ★**不在本单账上的红 (★按设计, 是「锚点过期」不是「红灯被调没」★)**: `SW/tools/check_demo_panel_spec.py` 的 R6 "
        "(盘上网表 md5 `3215020b…` ≠ 锚点 `13f59a43…`) + `MECH/check_demo_struct_truth.py` 的 G5b + C21 ⇒ ★**根因 = "
        "ISS-223 (hw-lead) 2026-11-16 05:18 重生成网表/脚表** ⇒ ★**等 ISS-223 交卷后走各自台账的 H-1 重锚流程** ★"
    )
    i226["note"] = (i226.get("note") or "") + (
        "\n2026-11-16 05:25 (cron 775d9893 继续执行后继计划) ★main 自测验收 ⇒ 落 verified★ "
        "⇒ ★同时清掉僵尸 fixing (会话 05:16:32 被平台中止但成果 4/4 全绿)⇒ 放掉 sw-lead 名额★"
    )

    # ---------- 2. 新开 ISS-228 (sw-lead 名额) ----------
    assert "ISS-228" not in by_id, "ISS-228 已存在"
    issues.append({
        "id": "ISS-228",
        "title": "★★[主线内·硬件选型/官方口径侧·内部活] RK3572 GPIO0 (I2C0_SCL=GPIO0_B0 球 1K21 / I2C0_SDA=GPIO0_B1 球 U32) → VCCIO 供电组官方映射自查 ⇒ 让「I2C_A 上拉最终电压域」可拍 (★回掉 hw.yaml 逾期 13 天的 need `iss148_rk3572_gpio0_vccio_domain_check`★)",
        "severity": "high",
        "source_blocker": "ISS-211",
        "desc": "★**main 2026-11-16 05:2x 实查分片**: `state/fragments/hw.yaml` 里挂着一条 ★**至今没人接的跨域 need**★ "
                "`iss148_rk3572_gpio0_vccio_domain_check` (to=sw-lead, since 2026-11-02, due 2026-11-03 ⇒ ★**逾期 13 天**★) ★\n"
                "· ★**它卡的是原理图主线**: I2C0_SCL/SDA = GPIO0_B0 (球 1K21) / GPIO0_B1 (球 U32) ⇒ 这两根脚挂哪个 VCCIO 组 "
                "⇒ ★**I2C_A 上拉最终电压域 (1.8V / 2.8V / 3.3V)**★ ⇒ 决定 ★**ISS-211 缺陷① + d1 组落表**★ ★\n"
                "· ★**已定的部分** (`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md`): datasheet p.39 渲染图 ⇒ VCCIO1~6 可上 3.3V (max 3.63V); "
                "`1.8V only` 只有 VCCIO0 ⇒ ★**「VCCIO1_VCC 属 1.8V only」是扁平 txt 的排版假象** ★\n"
                "· ★**没定的部分 = 本单要干的**: datasheet ★**没有 GPIO bank → VCCIO 组对应表**★ ⇒ GPIO0_B0/B1 归属 = [0数据] ★\n"
                "· ★**本单 = 内部活 · 零外发 · 不许改 `HW/`** ★",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": ["iss148_rk3572_gpio0_vccio_domain_check"],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 05:25 (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮实查分片, 发现 hw.yaml 里一条 "
                "逾期 13 天的跨域 need 没人接 (to=sw-lead)** ★\n"
                "★**sw-lead 名额的上一条 ISS-226 本轮 05:25 落 verified (main 自测: 门禁 rc=0 + selftest 13/13 + 分片真落盘) "
                "⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改 `HW/` 任何文件 · 不改 `MECH/` 任何文件 · 不碰 PCB 布线布局 · 不写别人分片 · 不发信 · 不自签 issue_log ★",
        "task_brief": BRIEF_228,
        "dispatched_at": None,
    })

    # ---------- 写回 ----------
    shutil.copy2(LOG, LOG + ".bak_20261116_0525_verify226_open228")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-226 → verified / ISS-228 新开 (owner=sw-lead, status=open)")
    print("issues total:", len(log["issues"]))


if __name__ == "__main__":
    main()
