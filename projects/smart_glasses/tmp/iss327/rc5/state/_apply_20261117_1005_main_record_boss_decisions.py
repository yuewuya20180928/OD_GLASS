#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 10:0x · job 775d9893「ARS45 继续执行后继计划」
★把老板 2026-11-17 09:49「按照你的建议执行」拍板的 8 条写进【唯一真源 state/fragments/pm.yaml 的 needs_from】★
★(★merge.py 的口径: 需求条目带 `decision` 字段 ⇒ 直接判 answered ⇒ 老板清单里这 8 条自动消失★)★
★**只动 state/fragments/pm.yaml 一个文件 (只追加 needs_from 条目, 老的条目一个字没动)★**
★**落表镜像 frag_write.py 的写法 (yaml.safe_dump allow_unicode=True sort_keys=False width=100 + 原子替换)★**
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.join(HERE, "fragments", "pm.yaml")
BAK = PM + ".bak_20261117_1005_main_boss_decisions"

DECIDED_AT = "2026-11-17 09:49"
DECIDED_BY = "boss (2026-11-17 09:49 原话「按照你的建议执行」· 项目总工代录)"

NEW = [
    {
        "key": "boss_a1_v3_batdet_divider_20261117",
        "to": "boss",
        "item": "A1 = V-3 BAT_DET 分压链取值 (白名单 {E, A, D, DEG4}) —— ★**「板只改一次」那一趟的网表侧前置之一 (落表器已就位, 一句凭据 = 一条命令)**★",
        "since": "2026-11-17",
        "decision": "★**A1 = V-3 = E** (★上臂 100k ±1% + 下臂 60k ±1% + 滤波 100nF ±10%★) ⇒ ★**依据 = 唯一同时过漏电与比容差的选项; 一条拍板解锁 13 条**★ "
                    "⇒ ★**已落表 (2026-11-17 09:58:16 · `state/land_v_values.py --decision V-3=E --apply --boss-decision \"2026-11-17 A1 = E\"` · rc=0)**★ "
                    "⇒ 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (含老板凭据机器化留痕 + 新旧 md5 对照)★ "
                    "⇒ ★**main 代拍 F-1 语义 (★ISS-223 F-1 归 main★)**: demo 板 = Type-C 供电不装电池 ⇒ ★**BAT_DET 三颗 = 【板上预留必装】(焊盘在板 / BOM 必装 / 电池不接)**, 不是「宣称 demo 板要装电池」★",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
    {
        "key": "boss_a2_v4_rilim_20261117",
        "to": "boss",
        "item": "A2 = V-4 R_ILIM 档位 (白名单 {680, 470, 390}) —— ★**「板只改一次」那一趟的网表侧前置之一**★",
        "since": "2026-11-17",
        "decision": "★**A2 = V-4 = 680Ω ±1%** (★单 pin 0.349A ⇒ 余量 1.43×; 390Ω 档实测 0.608A > 0.50A 触点额定, 已判死★) ⇒ "
                    "★**已落表 (2026-11-17 09:58:16 · `--decision V-4=680 --boss-decision \"2026-11-17 A2 = 680\"` · rc=0)**★ ⇒ "
                    "网表 L47/L48 已落 `680Ω ±1% (IINMAX ≈0.57A · ICHG ≈0.70A · 单 pin 0.349A ⇒ 余量 1.43×)` + BOM 同步★",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
    {
        "key": "boss_a3_v2_esd_arch_20261117",
        "to": "boss",
        "item": "A3 = V-2 USB ESD 落表方式 + W-1 架构轴 (2脚单通道 / 3脚双通道 / 2脚双向)",
        "since": "2026-11-17",
        "decision": "★**A3 = V-2 = 1 (2脚单通道; 架构轴按真源现状走, 型号轴不动)**★ ⇒ ★**与 ISS-257 已落真源一致 (零返工); 注意 ① 只护 D+, D− 侧归 W-1b/W-1c**★ ⇒ "
                    "★**⚠ 落表被闸拦下 (★2026-11-17 09:55 实测★)**: V-2 的落表动作 = 把 `D_ESD_USB_D` pad1 的网名由 `USB_D_P_SRC` 改成 `NET_USB_D_P_TYPEC` ⇒ "
                    "★**这改的是【行号锚点守卫的实体身份 (ref + net)】⇒ 守卫判 RED (「台账里那颗器件在本表里找不到了」) ⇒ 落表器自动回滚 ⇒ V-2 现在落不下去**★ ⇒ "
                    "★**根因 = 两个工具的接口没接上 (落表器没同步 registry 身份), 不是落表内容错**★ ⇒ 已开 ISS-282 给 hw-lead (★它写的那两个工具★)★ "
                    "⇒ ★**板那一趟必须同趟改 `D_ESD_USB_D` pad1 的网名 (漏改 ⇒ 网表与板对不上)★**",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
    {
        "key": "boss_p7_p8_which_board_20261117",
        "to": "boss",
        "item": "P7 / P8 「画哪一块板」= 现役 160×100 台架板 还是 产品板 60×30 套A (★决定作业包 §3 S1~S13 的坐标帧写哪一套★)",
        "since": "2026-11-17",
        "decision": "★**选项 A = 改现役 160×100 台架板** (★`HW/PCB/demo_mainboard.kicad_pcb` · Edge.Cuts 160.10×100.10 · 8 层 · 186 封装 · md5 `611b869e…`★) ⇒ "
                    "★**理由 = 这是唯一一块【已有 186 封装 + 已布线 + 32 个 Gerber 齐 + 有 DRC 闸】的板; 产品板等于从零画第二块, 且 SoM 承载区 (56.70×46.78mm) 物理装不进 60×30**★ ⇒ "
                    "★**P7 与 P8 同一件事的两个切面 ⇒ 一并确认: 这一趟的坐标帧 = `B160x100` (= 作业包 §3-S6 已声明的 ISS-274 口径)**★ ⇒ "
                    "★**连带后果 (如实记)**: ① 「产品板 (60×30/60×15) 能不能布通 23 条跨 SoM 主体腿」这条 (作业包 §2 第 ③ 条) 在这一趟【不解决】⇒ 归整机阶段 ② "
                    "MECH 侧那套 60×30 窗口与现役板【不可互相代入】(ISS-274/276 已各自声明)★",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
    {
        "key": "boss_p9_port_opening_split_20261117",
        "to": "boss",
        "item": "P9 「检修口 / 调试口开口: 拆成两条, 还是维持合并?」 (★几何上合并不可行★)",
        "since": "2026-11-17",
        "decision": "★**选项 A = 拆成两条, 各自按现役帧 `B160x100` 给坐标** (★调试口开口 = X 137.850..148.050 × Y 54.300..58.900 · UART 检修口 = X 13.790..23.990 × Y 66.300..70.900 ⇒ 两条都不压 SoM 座★) ⇒ "
                    "★**理由 = ISS-276 实测 `J_DEBUG`@(144.30, 58.00) 与 `J_UART`@(20.74, 70.00) 相距 123.56mm ⇒ 合并开口必须清空宽 126.218mm vs 开口本身 10.20mm ⇒ 差 116.017mm ⇒ 几何上不可能**★ ⇒ "
                    "★**未解前置不因这一条消失**: 座体真实高度 h = [0数据] ⇒ 开口 Y 的一切数仍建在「座体高 2.54mm」假设上 ⇒ ★**这一条只拍「拆不拆」, h 由 ISS-278 出参数化规格 (f(h) + 三档) 后再回来拍**★",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
    {
        "key": "boss_w4_q_pg_topology_20261117",
        "to": "boss",
        "item": "P4 (= W-4 / G-1) `Q_PG` 的网表 note 与 P 沟道高边开关常规拓扑【相反】⇒ 写法 A (S=BAT_SW / D=ON / G=PG) 还是写法 B (note 首句直译)",
        "since": "2026-11-17",
        "decision": "★**写法 A = S=BAT_SW / D=ON / G=PG** (★ISS-244 实跑推演: PG 低时 VGS = −4.2V ⇒ 导通 / PG 高时 VGS = −0.9V ⇒ 关断 ⇒ 逻辑自洽; 写法 B ⇒ 上电 ON 被 10k 下拉到 0V ⇒ VGS = 0V 不导通, PG 高时 VGS = +3.3V 反向偏置 ⇒ 【PG 高低都关 ⇒ 开机路径彻底不通】★) ⇒ "
                    "★**⚠ 实测出的连带事实 (★main 2026-11-17 10:0x 读盘★)**: 落地件 `DMP3098L` 引脚序 = **1=G / 2=S / 3=D** ⇒ ★**现网表是 pad1=PWR_ON(G 位!) / pad2=BAT_SW(S) / pad3=PWR_GOOD(D 位!) ⇒ 栅极接负载、漏极接 PG ⇒ 与写法 A 完全对不上**★ ⇒ "
                    "★**⇒ 落表要改的不只是 note, 还有 pad1↔pad3 的网互换 (pad1=PWR_GOOD / pad2=BAT_SW / pad3=PWR_ON) ⇒ 板那一趟必须重画 Q_PG 的 land (SOT-23 库标准序 G/S/D ⇒ 要么选 D-S-G 序器件, 要么重画)**★ ⇒ 已开 ISS-282 (hw-lead) 执行",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
    {
        "key": "boss_g5_led_brightness_20261117",
        "to": "boss",
        "item": "P6 (= W-6 / G-5) LED 亮度档: 1kΩ 串阻 ⇒ 实测只有 1.1~1.3mA (★ISS-244: 1mA 工作点只有 20mA 标称值的 4.8%~7.2% = 暗 14~21 倍★)",
        "since": "2026-11-17",
        "decision": "★**选项 ② = 改 R 到 20 mA 档** ⇒ ★**R_LED_R = 68Ω ±1% (红) · R_LED_G = 55Ω ±1% (绿)**★ ⇒ ★**理由 = ①「接受暗」⇒ 指示灯白天看不见 (它是充电状态的唯一可视反馈) / ③ PWM 调光 = 拿软件帧预算换一颗指示灯的亮度 (比例失衡)**★ ⇒ "
                    "★**连带代价 (如实记)**: 每颗功耗 2.2mW → 66mW (两颗 ≈ 0.13W 进电池账) + 亮度 ×14 ⇒ ★**眼旁光源的 IEC 62471 分级要重算**★ ⇒ "
                    "★**⚠ 口径订正 (★main 主动纠正自己上一条消息★)**: 我 09:4x 给你的消息里写的是「建议改 ≈150Ω」, 那是 §A-补4 W-6 行的旧数 (★该行只写「≈150Ω ⇒ 20mA」, 未给红/绿分档★) ⇒ "
                    "★**按 ISS-244 [官网] 级实测折算, 20mA 档的真值是 红 68Ω / 绿 55Ω (150Ω 只有 ~5mA, 达不到老板批准的「20mA 档」目标)**★ ⇒ ★**本条按 68/55Ω 执行**★ ⇒ 已开 ISS-282 (hw-lead) 落表",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
    {
        "key": "boss_p10_hard_protected_follow_20261117",
        "to": "boss",
        "item": "P10 「板合法改过一次以后, SW 侧的 hard_protected (板 md5 + .kicad_pro md5) 怎么合法跟上?」= ① 给板也建链头 / ② 保留纯 md5 + 显式单号背书 / ③ 拆两层",
        "since": "2026-11-17",
        "decision": "★**方案 ② = 保留纯 md5, 但把「合法改板」做成一个显式的、由单号背书的动作** (★改板那一趟的单号 + 新旧 md5 都留痕, 闸认这个单号★) ⇒ "
                    "★**理由 = 改动面最小 (不动网表/脚表那条已跑通的链头逻辑) + 「悄悄换真源」照样抓得住 (半自动: 改 md5 必须同时改单号字段)**★ ⇒ "
                    "★**三条红线 (任何方案都不许动)**: ① 不许把「改 md5」变成「随手改一下就绿」⇒ 必须留下「谁在哪个单号下改的」证据 (★机器可查: 台账里查得到那个单号 + 文件名 + 改前 md5 + 改后 md5★) ② "
                    "不许为了不红而放宽「盘上 ≠ 链头 ⇒ 红」③ 不许把「取不准」放宽成「取最近一条」⇒ fail-closed 那条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红) 一条都不许动★ ⇒ "
                    "★**⚠ 方案②自带一条缝 (ISS-279 交卷单原文点名)**: 「单号与 md5 若可各自独立编辑 ⇒ 有缝 ⇒ 必须做成【一个字段两个值】且台账里查得到」★ ⇒ 已开 ISS-283 (sw-lead) 落地 + 必须带反向用例",
        "decided_at": DECIDED_AT,
        "decided_by": DECIDED_BY,
    },
]


def main() -> int:
    shutil.copy2(PM, BAK)
    d = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    nf = d.setdefault("needs_from", [])
    before = len(nf)
    keys_before = {n.get("key") for n in nf}
    added = []
    for e in NEW:
        if e["key"] in keys_before:
            print("⚠ 已有同 key ⇒ 跳过 (不重复登记): %s" % e["key"])
            continue
        nf.append(e)
        added.append(e["key"])
    d["updated_at"] = "2026-11-17 10:05"
    d["updated_by"] = "main"
    text = yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(PM), prefix=".pm_tmp_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, PM)
    print("needs_from: %d → %d (新增 %d)" % (before, len(nf), len(added)))
    for k in added:
        print("  + %s" % k)
    # 自检: 能被读回 + 每条都有 decision/decided_at
    d2 = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    ok = all(n.get("decision") and n.get("decided_at")
             for n in d2.get("needs_from", []) if n.get("key") in added)
    print("全部新条目带 decision/decided_at =", ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
