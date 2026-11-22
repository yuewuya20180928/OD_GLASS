#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1150_open_iss240_241.py
★main (moli) 2026-11-16 11:5x (cron 775d9893 继续执行后继计划)★
★新开 ISS-240 (mech-lead · 跨铰链 FPC 几何三口径收口) + ISS-241 (sw-lead · BOM 剩余 [待选型] 必装件 OPN 选型证据矩阵·排队)★

★★**为什么是这两条 (★main 本轮 11:3x~11:5x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**advance.py --json ⇒ internal=[] / approvals=[] / decisions=40 / waiting=[]** ⇒ 根因 = ★**hw-lead (ISS-239) 与 sw-lead (ISS-172) 名额都被在飞单占着, 且两条会话本轮实测都活着** ★
  (★sw-lead 会话 `3bd4d3a6` 最后一条 = 11:38:54「Data collection complete. Writing the full evidence matrix to disk now.」★·
   ★hw-lead 会话 `ed081370` 最后一条 = 11:38:40「The `type` column is per-row, so device classification needs fixing.」⇒ **两个都是真在飞, 不是僵尸** ★)
  ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 本轮不重复派这两条** ★
· ★**mech-lead 名额空着** (ISS-238 已于 11:2x 由 main 独立验收落 `verified`, 它的会话 11:22 已结束) ⇒ ★**本轮自己找活, 派给 mech-lead** ★

★★**ISS-240 的病灶 (★main 本轮逐个实跑 + 逐行实读出来的, 每条都有出处★)** ★★
★**A. 跨铰链 FPC 的几何账有【三套口径】, 现行门禁钉的那套既不是网表真源、构成也和真源完全不同** ★
· ★**口径① = 网表真源 (现行件, 权威)**: `HW/STEP1_PARTS_SPEC.md` §0 裁定块 (ISS-237, 2026-11-16) ★
  ⇒ ★**camera = 31p / 0.3mm** (Radxa Camera 4K · IMX415 · 板文件封装 FH35C-31S-0.3SHW(50))★ · ★**display = 22p / 0.5mm** (Waveshare 2.8inch DSI LCD SKU 22028 · 座 FH12-22S-0.5SH(55))★
  ⇒ ★**脚表实测: count(CONN_CAM) = 31 · count(CONN_LIGHT) = 22** (main 本轮实跑 `csv.DictReader` 计数) ★
  ⇒ ★**真值垂直占位 = 31×0.3 + 22×0.5 + 10×0.5(J_CHG) = 9.3 + 11.0 + 5.0 = 25.3 mm** (★[推算]·算式逐行写清★) ★
· ★**口径② = 脚本的「收敛版」**: `MECH/hinge_usb_check.py` 的 `RECOMMENDED_PINS` 硬编码 ★**J_CHG 10 / CONN_CAM 16 / CONN_LIGHT 20 / CONN_USB 4**★, 全部按 `ffc_pitch_mm = 0.5` 算 ⇒ ★**16×0.5 + 20×0.5 + 4×0.5 + 10×0.5 = 8.0 + 10.0 + 2.0 + 5.0 = 25.0 mm** ★
  ⇒ ★★★**main 本轮实跑 `python3 MECH/hinge_usb_check.py` ⇒ 打印「垂直(高度)占位 收敛版 = 25.0 mm (16p/20p/4p/10p 全 0.5mm) vs 镜脚净高 38.0 mm」★★★ ★
· ★**口径③ = 脚本的「声明版」**: 同一次实跑打印 ★**「垂直(高度)占位 声明版 = 31.5 mm (网表声明 31p/22p/0p/10p 全 0.5mm)」** ★
  ⇒ ★★**这两个数里的 31.5mm 是【把 camera 当 0.5mm pitch 算出来的】(31×0.5 = 15.5, 而真值是 31×0.3 = 9.3) ⇒ 高估 6.2mm**★★ ★
· ★★★**⇒ 结论 (main 本轮自己算的)**: ★**现行门禁钉的 25.00 mm = 口径②, 它与真值 25.3 mm 只差 0.3 mm, 但【构成完全不同】(16p@0.5+20p@0.5 vs 31p@0.3+22p@0.5) ⇒ 是【两个不同的错凑出的巧合】** ★★★
  ⇒ ★**⇒ 一旦 camera 座换料/换 pitch, 或 display 座按 ISS-237 从 40p 收到 22p 之外再变, 这个 25.00 不会跟着变 ⇒ 它【不是从真源推出来的数】** ★
· ★★★**B. `MECH/check_demo_struct_truth.py` 的 G7 把 25.00 当现行值钉死 (main 本轮实读代码 L585~L593)★★★ ★
  ⇒ ★**G7 断言 = `fixed == "25.00"`, 描述文字 = 「分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)」** ★
  ⇒ ★★**⇒ 这条门禁把【口径②的推导过程】写进了判据里 ⇒ 谁改数字谁红 ⇒ 它【锁住的是错的构成】, 不是锁住真值**★★ ★
· ★★★**C. `CROSS_LINKS` 里的 `CONN_USB` 在网表里一行都没有 (main 本轮实跑 grep)★★★ ★
  ⇒ ★**`grep -n "CONN_USB" HW/netlist_v1.csv` ⇒ 0 命中 · `HW/netlist_v1_pins.csv` ⇒ 0 命中** ★
  ⇒ ★**demo 板的 USB-C 入口 = `J_USB_C` (网表 L419, board=MAIN_PCB) ⇒ 在主板上, 不跨铰链**; 充电板另有自己的 `J_TYPE_C` (网表 L3, board=CHG_BOARD) ★
  ⇒ ★★**⇒ 铰链区径向占位按 N=4 条链算 (R_min 3.0 + 4×(0.2+0.15) = 4.4 mm ⇒ 余量 1.0 mm), 真实 N=3 ⇒ 3.75 mm ⇒ 余量 1.65 mm** ★★
  ⇒ ★**(方向: 脚本高估占位 ⇒ 偏保守, 不致命; 但它是【错的链路清单】, 而正文 §5.2 F-2 还在拿它讲「跨铰链 USB 链路未展开完整」)** ★
· ★★★**D. 正文 `MECH/USB_HINGE_STRUCTURE.md` 还写着 3 处过期口径 (main 本轮实跑 grep, 行号在盘上)**★★★ ★
  ⇒ ★**L90 `| L-3 | **MIPI-CSI** | `CONN_CAM` (40p) | 40 | …` / L91 `| L-4 | **MIPI-DSI** | `CONN_LIGHT` (40p*) | 21 用到 / **9 必装** | …` / L96 「* `CONN_LIGHT` 的 pin 数在网表值列**没有写**」** ★
  ⇒ ★★**⇒ 网表早就写了 (L237 `CONN_LIGHT` = `★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), …)`) ⇒ 这 3 处现在全是【假陈述】**★★ ★
  ⇒ ★**⇒ 而且脚本 §4 的正文对表【只查关键词 + 4.4 / 25.0 两个数】⇒ 这 3 处旧口径【隐形通过】= 一盏隐形红 (ISS-213 / ISS-238 同型)** ★
· ★**⇒ 本单 = 收口这三套口径 (不是改板, 不是改网表) + 出改法映射 + 新建独立机器门禁 (带反向用例)** ★

★★**ISS-241 的病灶 (★main 本轮实跑 `HW/BOM_v1.csv` 统计出来的★)** ★★
· ★**BOM 里 value 仍写「待选型」且【必装】的行 = 23 条** (★DNP 的 40 条不占本单·R/C 通用品也不占★) ★
· ★**其中 `U_PWR_SW` / `U_EN_SW` 已被 ISS-172 占住 (sw-lead 在办) ⇒ 本单排除** ★
· ★★**⇒ 本单 = 剩下的 21 件 (其中 `R_SUPV_DIV1/2` 是 0Ω 跳线位 = 规格件, 一句话带过)**: ★
  ESD 阵列 ×4 (`D_ESD_CAM` / `D_ESD_DEMO` / `D_ESD_TC` / `D_ESD_USB_D`) · π 滤波磁珠 ×2 (`FB_DEMO` / `FB_VBUS`) · TVS ×1 (`D_TVS_VBUS`) ·
  MOS ×4 (`Q_AND` 硬件AND / `Q_ENVC` 反相 / `Q_PG` P-MOS 高边 / `Q_CHG_LED`) · LED ×3 (`D_LED_G` / `D_LED_R` / `D_CHG_LED`) · 按键 ×5 (`SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST`) · 电容 ×1 (`C_REGN` 1µF) ★
· ★**硬约束 (本单最要紧的一条)**: ★**这 21 件的封装在板文件里是【占位焊盘】(BOM 里写着「板文件封装: 2 焊盘」/「3 焊盘」/「待定」) ⇒ 选型必须【落在现有焊盘占位上】⇒ 不许靠换封装解选型** ★
· ★**⇒ 本单 = 出 OPN 选型证据矩阵 (≥2 候选 × 官方参数 + 在售型号 + 封装兼容 + 降级方案) ⇒ 【只出证据, 不许落表】(落表交 main 排期)★ ★

★★**边界 (两条单共同的)★★ ★★
★零外发 (老板 2026-11-12 02:02: 不再发信, 全靠自己查资料) · ★不改 PROJECT_TRACKER.md §0 · ★不写别人的分片 · ★**不碰 PCB 布线 / 布局 / 板框** ·
★**不许改网表 / 脚表 / BOM** (⇒ 不会打断 MECH C21 三方对账与 SW R6 锚点) · ★不替老板拍板 · ★**不代拍 V-2/V-3/V-4** ★
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

TITLE_240 = (
    "★★[主线内·结构/判据侧·内部活] ★★跨铰链 FPC 几何账【三套口径】互相打架 "
    "(★脚本「收敛版」= 硬编码 16p/20p ⇒ 而网表真源已是 camera 31p/**0.3mm** + display 22p/0.5mm · "
    "★脚本把 camera 按 0.5mm 算 ⇒ 声明版 31.5mm 高估 6.2mm · "
    "★`CROSS_LINKS` 里的 `CONN_USB` 在网表里【一行都没有】(demo 板 USB-C = `J_USB_C` 在主板·不跨铰链) ⇒ 径向占位按 4 条链算 4.4mm·真实 3 条 = 3.75mm · "
    "★`MECH/check_demo_struct_truth.py` G7 把分片 claim `mech_hinge_stack_fixed_mm` = **25.00** 当现行值钉死 "
    "(★而 25.00 = 16p@0.5+20p@0.5+4p@0.5+10p@0.5, 与真值 25.3mm 构成完全不同 = 两个不同的错凑出的巧合★) · "
    "★正文 `MECH/USB_HINGE_STRUCTURE.md` L90/L91/L96 还写着 `CONN_CAM (40p)` / `CONN_LIGHT (40p*)` / 「网表值列根本没写 pin 数」⇒ 而网表 L237 早写明 22p@0.5mm ⇒ 脚本 §4 只查关键词 + 4.4/25.0 两个数 ⇒ 这 3 处旧口径【隐形通过】★) "
    "⇒ 三口径收口 + 逐条改法映射 (只报不改网表/板) + 新建独立机器门禁 (带反向用例)"
)

DESC_240 = (
    "★main 2026-11-16 11:4x~11:5x 自己实跑 + 逐行实读出来的 (★不是抄任何交卷报告★) ★\n"
    "★**① 网表真源 (权威)**: `HW/STEP1_PARTS_SPEC.md` §0 裁定块 (ISS-237 · 2026-11-16) ⇒ camera **31p/0.3mm** "
    "(Radxa Camera 4K · IMX415) · display **22p/0.5mm** (Waveshare 2.8inch DSI LCD SKU 22028 · FH12-22S-0.5SH(55)); "
    "脚表实测 count(CONN_CAM)=31 · count(CONN_LIGHT)=22 ⇒ ★**真值垂直占位 = 31×0.3 + 22×0.5 + 10×0.5 = 25.3 mm**★\n"
    "★**② 脚本口径 (main 实跑 `python3 MECH/hinge_usb_check.py` 原样)**: 「垂直(高度)占位 声明版 = 31.5 mm (网表声明 31p/22p/0p/10p 全 0.5mm)」· "
    "「垂直(高度)占位 收敛版 = 25.0 mm (16p/20p/4p/10p 全 0.5mm) vs 镜脚净高 38.0 mm」⇒ ★**31.5 = 把 camera 当 0.5mm 算 ⇒ 高估 6.2mm**★\n"
    "★**③ 门禁钉死**: `MECH/check_demo_struct_truth.py` G7 (L585~L593) 断言 `mech_hinge_stack_fixed_mm == \"25.00\"`, "
    "判据描述里写死「ISS-206 裁 2 的 16p/20p/4p/10p」⇒ ★**判据把口径②的推导过程也锁住了**★\n"
    "★**④ 链路清单错**: `CROSS_LINKS = [J_CHG, CONN_USB, CONN_CAM, CONN_LIGHT]`; ★**`grep CONN_USB HW/netlist_v1.csv` ⇒ 0 命中, "
    "脚表也 0 命中**★ ⇒ demo 板 USB-C 入口 = `J_USB_C` (网表 L419 · MAIN_PCB) ⇒ 不跨铰链 ⇒ ★**真实 N=3 ⇒ 径向 3.75mm · 余量 1.65mm (脚本按 N=4 说 4.4mm · 余量 1.0mm)**★\n"
    "★**⑤ 正文旧口径**: `MECH/USB_HINGE_STRUCTURE.md` L90 「`CONN_CAM` (40p)」· L91 「`CONN_LIGHT` (40p*) · 21 用到 / 9 必装」· "
    "L96 「`CONN_LIGHT` 的 pin 数在网表值列**没有写**」⇒ ★**网表 L237 早写明 22p@0.5mm ⇒ 这 3 处现在是假陈述; 脚本 §4 只查关键词 + 4.4/25.0 ⇒ 隐形通过**★\n"
    "★**⑥ 本单要做的三件事**: ★**① 三口径收口页 (新文件, 含算式逐行 + 数字自证) ② 文档侧补标 (旧口径加作废标记 + 加现行口径行, ★旧字一个不删★) ③ 新建不依赖受保护脚本的机器门禁 + 反向用例**★"
)

BRIEF_240 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**跨铰链 FPC 的三套几何口径收成一套**★ ⇒ ★**收口页 + 文档侧补标 (只加不删) + 逐条改法映射 (只报不改) + 一个不依赖受保护脚本的新机器门禁 (带反向用例)**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 11:4x~11:5x 自己实跑, 不是推测★)** ★★
· ★**main 实跑 `python3 MECH/hinge_usb_check.py` (rc=0) ⇒ 打印两行**: 「垂直(高度)占位 声明版 = **31.5 mm** (网表声明 31p/22p/0p/10p **全 0.5mm**)」· 「垂直(高度)占位 收敛版 = **25.0 mm** (**16p/20p/4p/10p** 全 0.5mm) vs 镜脚净高 38.0 mm」★
· ★**main 实跑网表/脚表计数**: `count(CONN_CAM) = 31` · `count(CONN_LIGHT) = 22` · `grep CONN_USB HW/netlist_v1.csv` ⇒ **0 命中** ★
· ★**main 实读 `HW/STEP1_PARTS_SPEC.md` §0 裁定块 (ISS-237 · 2026-11-16)**: camera = **31p / 0.3mm** · display = **22p / 0.5mm** ★
· ★**main 实读 `MECH/check_demo_struct_truth.py` L585~L593**: G7 把 `mech_hinge_stack_fixed_mm` = **25.00** 钉死, 判据文字写着「ISS-206 裁 2 的 16p/20p/4p/10p」★
· ★★★**⇒ main 本轮自己算的结论 (你必须自己重算一遍, 不许照抄★)**: ★**真值 = 31×0.3 + 22×0.5 + 10×0.5 = 25.3 mm; 而被门禁钉死的 25.00 = 16×0.5 + 20×0.5 + 4×0.5 + 10×0.5 ⇒ 两者【构成完全不同】(16p@0.5+20p@0.5 vs 31p@0.3+22p@0.5) ⇒ 25.00 是【两个不同的错凑出的巧合】, 不是从真源推出来的数** ★★★
  ⇒ ★**⇒ 一旦 camera 换 pitch / 换料, 或 display 座按 ISS-237 之外再变, 25.00 不会跟着变** ★

★★**① 三口径收口页 (★新建文件★)** ★★
· ★**新建** `MECH/HINGE_FPC_GEOMETRY_TRUTH.md` ⇒ ★**必须含 4 张表**:
  ★**T1 三口径对照**: 行 = {脚本收敛版 (RECOMMENDED_PINS 硬编码 16/20/4/10 @0.5) / 脚本声明版 (网表声明 31/22/0/10 全按 0.5) / 网表真源 (每颗座按【自己的】pitch: camera 0.3 · display 0.5 · J_CHG 0.5)}; 列 = 每颗座触点区宽 + 合计 + 与镜脚净高 38.0 的余量 + ★**每个数字的算式逐行写出来 (不许只给结果)★**
  ★**T2 径向账**: CROSS_LINKS 里 ★**`CONN_USB` 在网表里 0 命中 ⇒ 真实跨铰链链路 = 3 条**★ ⇒ 径向 = R_min 3.0 + N×(t 0.2 + gap 0.15) ⇒ N=4 4.4mm vs N=3 3.75mm ⇒ 余量 1.0 vs 1.65mm
  ★**T3 逐条改法映射**: 每条 = ★**「文件:行号 · 现在写的 · 应改成什么 · 为什么能改 (依据哪个文件哪一行) · 还差什么 · 归谁改 (本单 / main 排期 / 不许动)」★**
  ★**T4 真值单一事实源声明**: 写死「★**跨铰链 FPC 几何真源 = `HW/STEP1_PARTS_SPEC.md` §0 裁定块 (ISS-237) + 网表/脚表实测计数**★ ⇒ ★**结构侧任何占位数都必须能从它推出来**★」
· ★**旧口径一律留痕**: 收口页里 16p/20p/26p/40p/12mm 这些数★**一律标「已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)」, 一个不许删**★

★★**② 文档侧补标 (★主修复·只许加不许删★)** ★★
· ★**只许动 `MECH/USB_HINGE_STRUCTURE.md`** ⇒ ★**逐处加 canonical 作废标注 + 现行口径行 (至少这三处)**: ★
  ★**L90** 「`CONN_CAM` (40p)」⇒ ★**加标 + 补现行行 = 31p/0.3mm (Radxa Camera 4K)★**
  ★**L91** 「`CONN_LIGHT` (40p*) · 21 用到 / 9 必装」⇒ ★**加标 + 补现行行 = 22p/0.5mm (Waveshare 2.8inch · ISS-237 裁定)· 脚表实测 22/22 全必装**★
  ★**L96** 「`CONN_LIGHT` 的 pin 数在网表值列**没有写**」⇒ ★**加标 + 订正为「网表 L237 已写明 22p@0.5mm (HIROSE FH12-22S-0.5SH(55))」**★
  ★**L310/L316/L320/L321/L333/L342/L343/L414/L430/L440** 等 ★**仍写 16p/20p/26p/40p/12mm 板宽 / `mech_conn_light_pins` = 20p@0.5mm** 的行 ⇒ ★**逐行核一遍: 该加作废标记的加, 该补现行口径的补** ★
· ★**绝对不许**: ★**删行 / 删数值 / 改任何实测原文**★ ⇒ ★**删掉 = 失去「当初为什么这么算」的留痕** ★
· ★**不许改**: `MECH/hinge_usb_check.py` (md5 3425bc14… · ★**在 `MECH/cavity_recalc_check.py` 的 MD5_EXPECTED 受保护清单里★**) · `MECH/check_demo_struct_truth.py` (md5 fa9b59e5…) · `MECH/cavity_recalc_check.py` · `MECH/service_port_check.py` (9b24bf98…) · `MECH/hw_cross_review_check.py` (e521387b…) · `MECH/display_biosafety_v2_check.py` (29c77fc3…) · `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (96239070…) · ★**判据阈值一个不许松** ★
· ★★**⇒ 脚本与门禁的改法【只出映射, 不许自己改】★★** (★改受保护脚本要 H-1 重基线: 改脚本 + md5 台账 + 反向用例 + 留痕 ⇒ 那是 main 的活★) ⇒ ★**你只交映射表 + 新门禁** ★

★★**③ 新机器门禁 (★新建·不靠任何受保护脚本★)** ★★
· ★**新建** `MECH/check_hinge_fpc_truth.py` ⇒ ★**至少 6 条断言**:
  ① ★**跨铰链链路清单里每个 ref 必须在网表里存在** (★`CONN_USB` 现在不通过 ⇒ 改法映射里说清这是【要 main 改脚本】还是【要 main 改架构结论】★)
  ② ★**每颗跨铰链座的 pitch 必须用它自己的 pitch** (camera 0.3 / display 0.5 / J_CHG 0.5) ⇒ 禁止「全 0.5mm」这种一刀切
  ③ ★**分片 claim `mech_hinge_stack_fixed_mm` 的值必须能从网表真源重算出来** (★即门禁要能自己算出 25.3 并与 claim 比对, 而不是只比字面 "25.00"★) ⇒ ★**注意: G7 现在比字面 "25.00" ⇒ 新门禁要比【算出来的数】★**
  ④ ★**正文里出现的 40p / 16p / 20p / 26p / 12mm 板宽 必须带 canonical 作废标注** ⇒ 裸命中 = 红
  ⑤ ★**正文里必须存在「现行口径行」(31p/0.3mm + 22p/0.5mm)** ⇒ 缺 = 红 (★防止下次又只留旧数★)
  ⑥ ★**canonical 标注串本身必须能在正文里找到** (★否则门禁自己失效都没人知道★)
· ★**`--selftest` 反向用例 ≥ 6 条, 每条必须自证「真的改到了目标」** (★例: 把 camera 的 pitch 从 0.3 改成 0.5 ⇒ 期望红哪一条; 把正文作废标记删掉 ⇒ 期望红哪一条; 把 claim 值改成 26.0 ⇒ 期望红哪一条★) ⇒ ★**不许出现「改了没生效」的假用例** ★

★★**④ 交卷单 + ⑤ 分片** ★★
· ★**交卷单** `HANDOFF/2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md` ⇒ ★**B1~B6 六块齐全** (B1 目标与范围 / B2 事实与数据 (每条带出处) / B3 三口径对照表 / B4 逐条改法映射 / B5 验收命令实跑输出 / B6 边界自证)
· ★**分片** `state/fragments/mech.yaml` ⇒ ★**走 `python3 state/frag_write.py` 原子写** ⇒ ★**只许加自己的 claim/need/artifact, 不许改别人的 key, 不许手改 yaml** ★

★★**验收命令 (★交卷前必跑, 原样贴输出★)** ★★
```
python3 MECH/check_hinge_fpc_truth.py            → rc=0 (全部断言 PASS)
python3 MECH/check_hinge_fpc_truth.py --selftest  → rc=0 (反向用例 N/N 全抓到, 每条自证)
python3 MECH/hinge_usb_check.py                  → rc=0 (★不许改它·只是证明你没碰坏它★)
python3 MECH/check_demo_struct_truth.py          → rc=0 (23/23 · ★不许放松任何阈值★)
python3 MECH/cavity_recalc_check.py              → rc=0 (23/23)
python3 state/merge.py && python3 state/gate_check.py → rc=0 (【Q1】18/18)
```
★**受保护 md5 必须逐字节未变 (交卷时实测贴出)**: ★
`MECH/hinge_usb_check.py` 3425bc141508de8a35f34c7cf7b803e8 · `MECH/service_port_check.py` 9b24bf985764880f0105aee677fba6a8 · `MECH/hw_cross_review_check.py` e521387b87b0fcdf9f22d56f14199967 · `MECH/display_biosafety_v2_check.py` 29c77fc3fc823048b1d96c9500d28dd7 · `MECH/check_demo_struct_truth.py` fa9b59e593a13408ad9505d986276f63 · `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` 96239070dc7c0ec00edb1b778a698769 · `HW/netlist_v1.csv` 34132f7e40a241e1fae1476be0eafbd5 · `HW/netlist_v1_pins.csv` b21b743a7702d30729f0d653c15392df · `HW/BOM_v1.csv` c195a117ff17490d4d1e1a5b8f1995a7 · `HW/PCB/demo_mainboard.kicad_pcb` 611b869e13518c3c023fb178f91a0075 · `HW/PCB/demo_mainboard.kicad_pro` 3e504d2be83152e337949723e909be1b ★

★★**边界 (★逐项自证★)** ★★
· ★**零外发** (不发邮件 / 不联系供应商 / 不下采购单) · ★**实物 [实测] = 0 条** (本单所有数 = [推算], 依据是网表/脚表/裁定块的实测值) ★
· ★**不碰 PCB 布线 / 布局 / 板框** · ★**不许改网表 / 脚表 / BOM / 板** (★改了就打断 MECH C21 三方对账与 SW R6 锚点★) ★
· ★**不改 PROJECT_TRACKER.md §0** · ★**不写别人的分片** (只写 `state/fragments/mech.yaml`) · ★**不自签 issue_log** (status 留给 main 落 verified) ★
· ★**不替老板拍板** · ★**不代拍 V-2 / V-3 / V-4** ★
· ★**抗过载纪律 (★今天血泪换来的★)**: ★**① 每拿到一个结论立刻写盘** (别攒到最后一起写 ⇒ 上轮白死的正是这个) ★**② 撞 `overloaded_error (2064) (529)` 或 `unknown error, 715 (1000)` 就原地重试, 别放弃** ★**③ 别整文件读大文件** (按行/按节读) ★

★**一句话交卷标准 (★main 会照这个验收, 不抄你的自述★)**: ★**「三口径收口页里每个数都能自己重算出来 · 正文旧口径全部带作废标记且旧字一个没删 · 新门禁 rc=0 且反向用例每条都自证 · 受保护 11 个 md5 逐字节未变」** ★"""

TITLE_241 = (
    "★★[主线内·硬件选型/官方口径侧·内部活·排队] ★★BOM 里 value 仍写「待选型」的必装器件 = **21 件** "
    "(★ESD 阵列 ×4 · π 滤波磁珠 ×2 · TVS ×1 · MOS ×4 · LED ×3 · 按键 ×5 · 电容 ×1★) ⇒ 主板 BOM 出不来 OPN "
    "(★**排除 `U_PWR_SW`/`U_EN_SW` = ISS-172 在办 · 排除 40 条 DNP · 排除 R/C 通用品★) ⇒ "
    "≥2 候选 × 官方参数 + 在售型号 + **封装必须落在板文件现有 2/3 焊盘占位上** + 降级方案 + 机器门禁"
)

DESC_241 = (
    "★main 2026-11-16 11:5x 自己实跑 `HW/BOM_v1.csv` 统计出来的 (★不是抄任何交卷报告★) ★\n"
    "★**① 统计口径**: value 含「待选型」且 dnp 不含 DNP ⇒ **23 行**; 排除 `U_PWR_SW` (ISS-172 在办) ⇒ **21 件** ★\n"
    "★**② 清单 (owner/板位)**: ESD 阵列 ×4 (`D_ESD_CAM`/`D_ESD_DEMO`/`D_ESD_TC`/`D_ESD_USB_D`) · π 滤波磁珠 ×2 (`FB_DEMO`/`FB_VBUS`) · "
    "TVS ×1 (`D_TVS_VBUS`) · MOS ×4 (`Q_AND` 硬件AND / `Q_ENVC` 反相 / `Q_PG` P-MOS 高边开关 / `Q_CHG_LED`) · "
    "LED ×3 (`D_LED_G`/`D_LED_R`/`D_CHG_LED`) · 按键 ×5 (`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST`) · "
    "电容 ×1 (`C_REGN` 1µF) · ★**另 `R_SUPV_DIV1/2` 是 0Ω 跳线位 = 规格件, 一句话带过不算选型研究**★\n"
    "★**③ 最要紧的硬约束**: ★**这批件的封装在板文件里是【占位焊盘】(BOM 里写着「板文件封装: 2 焊盘」/「3 焊盘」/「待定」) ⇒ 选型必须【落在现有焊盘占位上】⇒ 不许靠换封装解选型** ★\n"
    "★**④ 为什么卡主线**: ★**主板 BOM 出不来 OPN ⇒ 采购单出不来 ⇒ 投板做不了** ★ (★这是 demo 板关键路径上【原理图侧】的最后一块拼图★) ★\n"
    "★**⑤ 本单只出证据矩阵, 不许落表** (★落表要 main 排期 + H-1 重锚, 否则打断 MECH C21 / SW R6★) ★"
)

BRIEF_241 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 BOM 里 ★**value 仍写「待选型」的 21 件必装器件**★ 变成 ★**可采购的 OPN 选型证据矩阵**★ ⇒ ★**每件 ≥2 候选 × 官方参数 + 在售型号 + 封装兼容性 + 降级方案**★ ⇒ ★**只出证据, 不许落表**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 11:5x 自己实跑统计★)** ★★
· ★**`HW/BOM_v1.csv` 实测**: value 含「待选型」且必装 ⇒ **23 行** ⇒ 排除 `U_PWR_SW`/`U_EN_SW` (★ISS-172 正在办, 别抢★) ⇒ **21 件** ★
· ★**这 21 件的封装全是板文件里的【占位焊盘】** (★BOM 原文: 「板文件封装: 2 焊盘 (ESD 阵列 [待选型])」/「3 焊盘 ([待选型] N-MOS …)」/「待定」★) ⇒ ★**选型必须落在现有焊盘上** ★
· ★**主板 BOM 出不来 OPN ⇒ 采购单出不来 ⇒ 投板做不了** ⇒ ★**这是 demo 板关键路径上原理图侧的最后一块拼图** ★
· ★**政策 (老板 2026-11-12 02:02)**: ★**不再发信, 全靠自己查资料** ⇒ ★**不许找供应商问, 只查公开官网/数据手册** ★

★★**① 清单 (21 件·逐件都要有结论, 不许跳过任何一件★)** ★★
· ★**ESD 阵列 ×4**: `D_ESD_CAM` (camera FPC 侧) · `D_ESD_DEMO` (demo 板 USB 2.0) · `D_ESD_TC` (充电板 Type-C 侧) · `D_ESD_USB_D` (USB 2.0 双通道) ⇒ ★**注意 Forlinx 载板指引要求 ESD 紧贴接口** ★
· ★**π 滤波磁珠 ×2**: `FB_DEMO` (demo 板 VBUS) · `FB_VBUS` (充电板 VBUS) ⇒ 给出 阻抗曲线 @100MHz / 额定电流 / DCR
· ★**TVS ×1**: `D_TVS_VBUS` (5V 级单向) ⇒ 给出 VRWM / 钳位电压 @Ipp / 峰值脉冲功率 / 结电容
· ★**MOS ×4**: `Q_AND` (N-MOS 硬件 AND · 3 焊盘) · `Q_ENVC` (N-MOS 反相 · 3 焊盘) · `Q_PG` (★**P-MOS 高边开关 · 低漏 · Vgs(th) 要明确★**) · `Q_CHG_LED` (N-MOS)
· ★**LED ×3**: `D_LED_G` / `D_LED_R` / `D_CHG_LED` ⇒ 给 Vf/If/波长/封装
· ★**按键 ×5**: `SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST` ⇒ 给行程力/高度/封装
· ★**电容 ×1**: `C_REGN` (1µF, 充电板) ⇒ 给 耐压/介质/封装

★★**② 每件的输出格式 (★统一模板, 便于机器门禁逐条查★)** ★★
每件一行, 必含: ★**位号 · 板位 (MAIN_PCB / CHG_BOARD) · 判据 (从网表 note + 官方参数里提炼, 如「低漏 Vgs(th) ≤ 某值」) · 候选1 (型号 + 官方链接 + 关键参数 + 封装) · 候选2 (…) · ★**推荐项 + 为什么 (★但【不代拍】: 只给依据与代价, 老板/PM 要的一票由 main 排期走★)· 封装兼容性结论 (与板文件现有 2/3 焊盘占位是否匹配) · 证据等级 · 降级方案 (查不到就写降级方案, 不许留空)** ★
· ★**证据等级五级固定**: ★`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`★ (★官方数据手册 = [官网]; 板上实测 = [实测]; 查不到 = [0数据] + 必须写降级方案★) ★
· ★**降级方案是必须项**: 例 ★**查不到带 RCB 的负载开关 ⇒ 降级 = 选无 RCB 型号 + 主板本地加反灌保护 (TVS/二极管) + 登记缺口**★ (★ISS-172 交卷里已有同型写法, 照那个口径★) ★
· ★**不许猜**: 查不到的型号/参数/封装 ⇒ 标 [0数据] 并写降级方案 ⇒ ★**不许把「没查到」写成具体型号** ★

★★**③ 机器门禁 (★新建·别改别人的脚本★)** ★★
· ★**新建** `HW/check_part_selection_matrix.py` ⇒ ★**至少 5 条断言**: ① 矩阵覆盖 21 个位号, 一个不缺 (★少一个就红★) ② 每件都有 ≥2 个候选 + 封装兼容性结论 + 证据等级 + 降级方案 ③ 每件的封装必须标出与板文件占位的关系 (兼容/不兼容 + 理由) ④ ★**不许出现「已定型」式空话: 候选型号栏不许为空** ⑤ **矩阵里的位号不许超出本单 21 件的范围** (防止越界改别人的单)
· ★**`--selftest` 反向用例 ≥ 5 条, 每条自证「真的改到了目标」** (★例: 删掉 1 个位号 ⇒ 期望红哪条; 把某件候选清空 ⇒ 期望红哪条; 把降级方案删掉 ⇒ 期望红哪条★) ★

★★**④ 交付物** ★★
· ★**新建** `HW/PART_SELECTION_MATRIX_2026-11-16.md` (★矩阵正文★) · ★**新建** `HW/check_part_selection_matrix.py` (★门禁★) · ★**交卷单** `HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md` (B1~B6) · ★**分片** `state/fragments/sw.yaml` (走 `state/frag_write.py` 原子写, ★只加自己的 key★)
· ★**文件冲突自检**: ★**在飞 hw-lead (ISS-239) 正在写 `HW/check_pin_function_labels.py` / `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` ⇒ 本单新建的文件名与它【零交集】, 不许改任何已有 HW 文件** ★

★★**验收命令 (★交卷前必跑★)** ★★
```
python3 HW/check_part_selection_matrix.py            → rc=0
python3 HW/check_part_selection_matrix.py --selftest  → rc=0 (反向 N/N 全抓到)
python3 HW/check_step1_parts_spec.py                 → rc=0 (★不许把 ISS-237 的屏口径门禁改红★)
python3 state/merge.py && python3 state/gate_check.py → rc=0 (【Q1】18/18)
```
★**受保护 md5 必须逐字节未变**: `HW/netlist_v1.csv` 34132f7e40a241e1fae1476be0eafbd5 · `HW/netlist_v1_pins.csv` b21b743a7702d30729f0d653c15392df · `HW/BOM_v1.csv` c195a117ff17490d4d1e1a5b8f1995a7 · `HW/PCB/demo_mainboard.kicad_pcb` 611b869e13518c3c023fb178f91a0075 · `HW/PCB/demo_mainboard.kicad_pro` 3e504d2be83152e337949723e909be1b ★

★★**边界 (★逐项自证★)** ★★
· ★**零外发** (不发邮件 / 不联系供应商 / 不下采购单 · ★老板 11-12 02:02 政策: 只查公开资料★) · ★**实物 [实测] = 0 条** (本单所有型号参数 = [官网]/[媒体], 板端没有实物) ★
· ★**不许落表**: ★**不许改网表 / 脚表 / BOM 的 value/opn 栏** ⇒ ★**落表由 main 排期 (H-1 重锚)★** ★
· ★**不碰 PCB 布线 / 布局 / 板框** · ★**不改 PROJECT_TRACKER.md §0** · ★**不写别人的分片** (只写 `state/fragments/sw.yaml`) · ★**不自签 issue_log** ★
· ★**不替老板拍板** (★选型只给依据与代价, 一票交 main 排期★) · ★**不代拍 V-2 / V-3 / V-4** ★
· ★**抗过载纪律**: ★**① 每拿到一个结论立刻写盘 ② 撞 529 / 715 原地重试 ③ 别整文件读大文件** ★

★**一句话交卷标准 (★main 会照这个验收★)**: ★**「21 个位号一个不缺 · 每件 ≥2 候选 + 官方参数 + 封装兼容结论 + 证据等级 + 降级方案 · 门禁 rc=0 且反向用例自证 · 5 个受保护 md5 逐字节未变 · 零外发」** ★"""


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f) or {}
    issues = log.get("issues") or []
    ids = {i.get("id") for i in issues}

    backup = LOG + ".bak_20261116_1150_open_240_241"
    shutil.copy2(LOG, backup)

    new = []
    if "ISS-240" not in ids:
        new.append({
            "id": "ISS-240",
            "title": TITLE_240,
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": DESC_240,
            "owner": "mech-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-19",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": (
                "★2026-11-16 11:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮 11:4x~11:5x 自己实跑** "
                "(★`python3 MECH/hinge_usb_check.py` 打印 声明版 31.5mm / 收敛版 25.0mm · 脚表 count(CONN_CAM)=31 · "
                "count(CONN_LIGHT)=22 · `grep CONN_USB HW/netlist_v1.csv` ⇒ 0 命中 · G7 (L585~L593) 钉 25.00 · "
                "`MECH/USB_HINGE_STRUCTURE.md` L90/L91/L96 旧口径★) ⇒ ★**真值 25.3mm 与被钉死的 25.00 构成完全不同 "
                "(16p@0.5+20p@0.5 vs 31p@0.3+22p@0.5) ⇒ 两个不同的错凑出的巧合** ★ "
                "★**mech-lead 名额本轮空着 (ISS-238 已 verified)** ⇒ 派它; ★**hw-lead/sw-lead 本轮不派 (ISS-239 / ISS-172 会话真在跑)** ★ "
                "★**不许改受保护脚本 / 不许改网表·脚表·BOM·板 ⇒ 不会打断 MECH C21 三方对账与 SW R6 锚点** ★"
            ),
            "dispatched_at": None,
            "task_brief": BRIEF_240,
        })
    if "ISS-241" not in ids:
        new.append({
            "id": "ISS-241",
            "title": TITLE_241,
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": DESC_241,
            "owner": "sw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": (
                "★2026-11-16 11:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮实跑 `HW/BOM_v1.csv` 统计** "
                "(★value 含「待选型」且必装 ⇒ 23 行 ⇒ 排除 U_PWR_SW/U_EN_SW (ISS-172 在办) ⇒ 21 件★) ⇒ "
                "★**主板 BOM 出不来 OPN ⇒ 采购单出不来 ⇒ 投板做不了** ⇒ 本单只出证据矩阵, 不许落表 ★ "
                "★**排队不派 (sw-lead 名额被 ISS-172 占着, 会话真在跑)** ⇒ 等 ISS-172 交卷后由 advance.py 自动可派 ★"
            ),
            "dispatched_at": None,
            "task_brief": BRIEF_241,
        })

    if not new:
        print("nothing to do (both already exist)")
        return 0

    issues.extend(new)
    log["issues"] = issues
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100000))
    print(f"opened: {[n['id'] for n in new]}  backup={os.path.basename(backup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
