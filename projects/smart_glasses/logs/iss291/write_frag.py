#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-291 分片写入 (★走 state/frag_write.py 的原子写, 绝不普通 open(w)★)"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "state"))
from frag_write import update_fragment  # noqa: E402

NEED1 = (
    "★【ISS-291 · 2026-11-17 · sw-lead · USB 插入检测链 (数字脚) 的三条未决 + 三个改法, 请 main 拍板★】★ "
    "判决对象收口后暴露的硬件侧后果 (★本单零落表, 只登记★): ★本板唯一那条【真正的 ADC 链】是 BAT_DET "
    "(网表 L186 ⇒ J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域), 而 VBUS_DET_D 链 (网表 L434/435/439 ⇒ J_SOM_P1 pin100 = "
    "USB_DRD1_VBUSDET) 是【USB OTG 插入检测数字脚】(脚表 L101 vol 栏 = —— ⇒ 域未知)⇒ ★老闸把它当 12bit SAR-ADC 判 "
    "(假红), 现在已按【数字检测输入】口径单判★ ⇒ 三件事查不到 ⇒ **[0数据]** ⇒ 登记给硬件侧: "
    "① 【内部 40kΩ 下拉】Forlinx FET3572 手册 (state/_os_snapshots/fx3572_manual.html §USB Design Note) 只对 "
    "**USB_DRD0_VBUSDET** 明写 'the chip contains an internal 40 kΩ pull-down' + 'A high level indicates DEVICE mode "
    "(2.7-3.3 V, typical: 3.0 V)' + 'In device mode, VBUSDET must be high (> 2.3 V)' ⇒ ★本板是 DRD1 ⇒ 手册未记载★ "
    "⇒ ★若 DRD1 同样带 40kΩ 内部下拉: 节点 = 5V×(1M‖40k)/(1M+1M‖40k) = **0.185V** ≪ 2.3V ⇒ **USB 插入检测永不触发**★ "
    "⇒ 【IO 域 / abs-max】脚表 L101 vol 栏 = —— ⇒ 域未知 ⇒ 闸按降级上界 3.3V (手册高电平带上沿) 判 ⇒ ★若域实为 1.8V ⇒ "
    "abs-max = 2.1V ⇒ 节点 2.625V **越限** ⇒ 必须改分压比★ ⇒ 【识别裕量】VBUS 取 USB 规范下限 4.75V 时节点 2.375V, "
    "距识别阈值 2.3V 只剩 **75mV (3.3%)** ⇒ ★很薄★ ⇒ "
    "★★三个改法 (★我不拍, 由 main/老板定★): (A 换料不换板, 推荐) 上臂 1M→22k + 下臂 1M 不动 ⇒ 节点 = 3.18V (落在手册 "
    "2.7-3.3V 高电平带内) ⇒ 静态电流 5V/(22k+38.5k) = 82.6µA / 413µW (代价: 常开功耗 2.5µA→~83µA); "
    "(B 按手册推荐) 该脚 3.3V 上拉 4.7k ⇒ 静态电流 702µA (代价最大, 只在功能优先于功耗时选); "
    "(C 不动硬件) 接受 75mV 裕量 + 把『插拔 USB 时读 USB_DRD1_VBUSDET 状态位』列为 EVT 必测项 (功能风险留在板上)★ ⇒ "
    "★★降级方案 (★这一趟来不及改板时★): 保留 1M/1M, EVT 必测项加『插/不插 USB 时能区分状态位』; 若实测读不到高电平 ⇒ "
    "说明内部 40kΩ 下拉存在 ⇒ 立刻按 (A) 改料 (换料不换板)★ ⇒ ★决定点: 「板只改一次」那一趟之前★ ⇒ "
    "★SW 侧闸已把两种情形都算出来报出 (理想 2.5V / 含下拉 0.185V), 判据见 SW/ADC_CALIBER_TABLE.md §1 行 15~18 与 §3★"
)

NEED2 = (
    "★【ISS-291 · 2026-11-17 · sw-lead · ★「板只改一次」那一趟不许套 VBUS_DET 100k/47k 那条★】★ "
    "★**这条建议基于错误前提, 照做 = 把一个假红换成真死功能**★: HW/CHARGE_STATUS_READBACK.md:101 逐字建议『是否同意把 "
    "`VBUS_DET` 的分压从 1M+1M 改为 **100k/47k** (换料不换板, 修 P1-8 的 451ms 建立 + 15.2%FS 漏电); 改动会让 5V→1.60V』 "
    "⇒ ★那条建议是按「VBUS_DET 是 SAR-ADC 输入」提的★ ⇒ ★而它其实是 USB 插入检测【数字】脚 (网表 L439 ⇒ J_SOM_P1 pin100 "
    "= USB_DRD1_VBUSDET)⇒ ★100k/47k ⇒ 节点 = 5V×47/147 = **1.60V < 2.3V 识别阈值** ⇒ **USB 插入检测直接死**★ ⇒ "
    "★另注: 真 ADC 链是 BAT_DET (pin38), 它的 451ms/15.2%FS 同样是假红 (判决对象错 + FS 口径错), 现已按 1.8V 域收口 "
    "(R_th=37.5kΩ ⇒ τ=3.75ms ⇒ 12bit 建立 33.8ms ⇒ 漏电 37.5mV = 2.1% FS, 与网表 L182 note 逐字对上)★ ⇒ "
    "★★正确动作: 先按 iss291_sw_vbus_det_d_digital_caliber 把域/abs-max/内部下拉确认掉, 再决定 VBUS_DET_D 怎么改; "
    "若那一趟已经把 100k/47k 写进网表 ⇒ 立刻回退成 1M/1M 或按方案 A 改值★ ⇒ "
    "★本单零落表: 网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece… / 板 611b869e… 四个 md5 逐字节不变★"
)

ART_SW_TABLE = (
    "★ISS-291 (2026-11-17 · sw-lead) 口径对照页 ★ ⇒ 一页表 (18 行): 量 / 现值 / 改后 / 依据出处 / 证据等级 ⇒ "
    "含『FS 3.3→1.8 (官方 datasheet 三处出处)』与『判决对象 VBUS_DET_D→BAT_DET (网表 L186 + 脚表 L39)』两行 ★ "
    "⇒ 另含 §2 三处口径为什么以前会打架 / §3 三条『查不到』的 fail-closed 处理 / §4 旧文档结论被推翻的清单 "
    "(SW_TIMING_REVIEW 的 ADC 500kΩ·451ms·15.2%FS / CHARGE_STATUS_READBACK:101 的 100k/47k 建议 / SCHEMATIC_REFDIE:375 的 3.3V 占位值) ★"
)

ART_TOOL = (
    "★ISS-291 (2026-11-17 · sw-lead) SW 侧判据口径收口补丁 (SW 侧单文件) ★ ⇒ ① 判决对象: 取链规则由『元组顺序第一条 "
    "populated 链』改为『落点是不是 SAR-ADC 脚』(判决源 = HW/PCB/FET3572C_PIN_TABLE.csv 的 signal+vol 两列; 落点 = 网表实读) "
    "⇒ active_chain 由 VBUS_DET_D 改为 **BAT_DET** (J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域); 脚表读不到/落点不唯一 ⇒ fail-closed 判红 ★ "
    "⇒ ② 满量程: DEVICE['V_DET_FS'] 由 3.3 改为 **1.8** (脚表 L39 + datasheet L2454 + L2864 三处出处逐字引; ADC_BITS 12 的证据等级 [0数据]→[官网]) ★ "
    "⇒ ③ 新增 F4D 数字检测输入口径段 (静态电流 4.81µA≤26.25µA / 节点 2.5V>2.3V / abs-max 3.3V 降级 + 三条 unresolved 未决项) ★ "
    "⇒ ④ 新增机器对账: 从网表 L182 note 正则抽出 37.5kΩ/37.5mV/2.1%FS 三个数与算出来的数对账 (fs_caliber_ok) ★ "
    "⇒ ⑤ 判据阈值一条不许调松 (建立 300ms / 漏电 0.4V 原值保留) ★ ⇒ ⑥ 反向用例 +6 条 (REV-12 FS→3.3 / REV-13 元组第一条 / "
    "REV-14 BAT_DET 三颗 DNP / REV-15 下臂 60k→100k 过压 / REV-16 VBUS_DET_D 10k/10k 静态电流 / REV-17 上臂 1M→10M 节点电平) ★ "
    "⇒ ★本机实跑: python3 SW/tools/timing_check.py ⇒ rc=0 · SELFTEST **85/85** (ISS-288 落地态是 72/72 ⇒ 条数只增不减) ★ "
    "⇒ 脚本 md5 cf09c921002937920bfa40701d523b33 · 2632 行 (改前 68c4becffe6bcd708e388dba9d18a505 · 1981 行) ★"
)

ART_HANDOFF = (
    "★ISS-291 (2026-11-17 · sw-lead) 交卷单 ★ ⇒ B1 判决对象改对 (判决源 = SoM 脚表 signal/vol 两列 + 落点网表实读; "
    "数字链另立 F4D 口径) + B2 满量程 3.3→1.8 (官方三处出处逐字 + 三个数与网表 note 逐字对上 ⇒ 2.1% FS) + B3 反向用例 6 条 "
    "(每条贴原样 rc + 期望红组 vs 实际红组, 日志 logs/iss291/rev_cases.log) + B4 回归 7 条全 rc=0 + 受保护 5 件 md5 逐字节不变 + "
    "B5 硬件后果只登记 (两条 need 给 main, 不改网表/脚表/BOM 一个字节) + 边界自查表 + 留给 main 的三件事 ★"
)

STATUS_SUMMARY = (
    "★ISS-291 (main 15:5x 派单 · cron 775d9893) = 【SW 侧 ADC 判据: 判决对象 + 满量程口径双错】收口★ ⇒ "
    "① 判决对象改对: 取链规则由『元组顺序第一条 populated 链』改为『落点是不是 SAR-ADC 脚』(判决源 = SoM 脚表 signal+vol; "
    "落点 = 网表实读) ⇒ active_chain 由 VBUS_DET_D (落点 pin100 = USB 数字脚) 改为 **BAT_DET** (落点 pin38 = SARADC_VIN5, 1.8V 域) ⇒ "
    "老闸那条红 = 假红, 真 ADC 链此前无判据 ⇒ 现已补齐 ★ "
    "② 满量程口径改对: V_DET_FS 3.3 → **1.8V** (脚表 L39 + datasheet L2454/L2864 三处官方出处) ⇒ 漏电 0.50V/15.2%FS → "
    "**37.5mV/2.1%FS** ⇒ 与网表 L182 note 写死的数**逐字对上** (并加了一道机器对账) ★ "
    "③ 数字链另立口径 (F4D): 静态电流 4.81µA≤26.25µA / 节点 2.5V>2.3V 识别阈值 / abs-max 降级 3.3V + 三条 [0数据] 未决项 "
    "(USB_DRD1_VBUSDET 的域·abs-max·内部 40kΩ 下拉) ⇒ 全部登记 need 给 main, 本单不碰真源 ★ "
    "④ 反向用例 +6 条 (REV-12~REV-17) ⇒ 每条贴原样 rc + 期望/实际红组 ★ "
    "⇒ ★本机实跑: timing_check.py rc=0 · 85/85 (原 72/72) · check_demo_panel_spec rc=0 · --selftest rc=0 (22/22) · "
    "HW/check_step1_parts_spec rc=0 (8/8) · state/merge rc=0 · state/gate_check rc=0 · state/issue_check rc=0 ★ "
    "★受保护 5 件 md5 逐字节不变 (板 611b869e… / .kicad_pro 3e504d2b… / 网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece…)★ ⇒ "
    "★零写板 · 零落表 · 零改 HW/ · 零外发 · 不自签 issue_log · 板端实物 [实测] = 0 条★ ⇒ "
    "交卷单 = HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md · 口径对照页 = SW/ADC_CALIBER_TABLE.md"
)


def mutate(d):
    d.setdefault("updated_at", "2026-11-17")
    d["updated_at"] = "2026-11-17"
    d["updated_by"] = "sw-lead"
    # ---- needs_from: 追加两条 ----
    needs = d.setdefault("needs_from", [])
    for key, item in (("iss291_sw_vbus_det_d_digital_caliber", NEED1),
                      ("iss291_sw_do_not_apply_vbus_100k47k", NEED2)):
        if not any(n.get("key") == key for n in needs):
            needs.append({"key": key, "to": "main", "item": item, "since": "2026-11-17"})
    # ---- ★把 iss285 那条 need 标成已解决 (resolved_by: ISS-288)★ ----
    for n in needs:
        if n.get("key") == "iss285_sw_apply_after_iss283_verified":
            n["resolved_by"] = "ISS-288"
            n["resolved_note"] = (
                "★【ISS-291 · 2026-11-17 · sw-lead】已解决: 前提已满足 (ISS-283 已 verified + ISS-285 补丁已落盘, "
                "落盘后 timing_check.py md5 = 68c4becffe6bcd708e388dba9d18a505 = ISS-285 交卷单写死的期望值, 且 "
                "python3 SW/tools/timing_check.py ⇒ rc=0 · 72/72) ⇒ 本条 need 的「等 ISS-283 落 verified 后一次性套用」"
                "已被 ISS-288 履行完毕 ⇒ 标 closed (★签字/关闭动作归 main★)★")
    # ---- artifacts: 追加三件 ----
    arts = d.setdefault("artifacts", [])
    for path, kind, summary in (
            ("SW/ADC_CALIBER_TABLE.md", "doc", ART_SW_TABLE),
            ("SW/tools/timing_check.py", "tool", ART_TOOL),
            ("HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md", "handoff", ART_HANDOFF)):
        if not any(a.get("path") == path for a in arts):
            arts.append({"path": path, "kind": kind, "version": "v1.0",
                          "updated_at": "2026-11-17", "summary": summary})
    # ---- status ----
    st = d.setdefault("status", {})
    st["phase"] = "delivered"
    st["progress_pct"] = 100
    st["health"] = "green"
    st["summary"] = STATUS_SUMMARY
    st["updated_at"] = "2026-11-17"


if __name__ == "__main__":
    d = update_fragment("sw-lead", mutate)
    print("✅ sw-lead 分片已原子写: needs_from=%d artifacts=%d"
          % (len(d.get("needs_from") or []), len(d.get("artifacts") or [])))
