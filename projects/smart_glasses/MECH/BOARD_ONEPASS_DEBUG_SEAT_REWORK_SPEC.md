# `J_DEBUG` + `J_UART` 座体 / 开口 / 必须清空区 —— 结构件改件要求单 【两件合到一件】 (ISS-389 · mech-lead)

> ★**一句话结论** ★**`J_DEBUG` 的座体必须清空区在那一趟【无论如何都要动】(三个竞争值 `1.7750`/`4.0850`/`4.8100` 算下来全红 ⇒ `OI-5` 只改返工幅度不改方向); `J_UART` 的座体必须清空区【不动就装不上】(现状 `2.5400` 对官方 THT 铜箔 `2.2700` 只剩 `0.1350` ⇒ 最坏 `-0.1650` 判红) ⇒ 两件同批换官方 P1.27 THT land 时, 结构件【必须同批返工】, 不存在「先只改一件」的省事方案; 本单给出两件的【统一口径表 + 逐轴改件要求单 + 三档返工幅度代价账 + 四条结构侧自答 + 闸链影响】, 但【三档选哪个 / 落点选哪个 / 座体高定哪档 / 判据该不该改 / Y 向零余量接受与否】全部是 main / boss 的裁决权 ⇒ 本单【不代拍】** ★
>
> ★**派活**: 项目总工 (main) · ISS-389 · 2026-11-24 派 / 做 · 交卷人 = 结构总工 (mech-lead) ★
> ★**本页闸**: ★`MECH/check_debug_seat_rework_spec.py` (★本单新建 · ★**零挂链** (`grep -c check_debug_seat_rework_spec state/gate_check.py` = `0`)★) ★
> ★**交卷页**: ★`HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md` ★
> ★**上游真相页 (★只读·一个字没改★)**: ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` (ISS-386 合一件答) · `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` (ISS-377 判据链) · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (ISS-371) · `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (ISS-374) · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (开口/清空区真身) · `MECH/service_port_check.py` (`CRIT`/`TOL` 真身 L126-L127) · `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` (ISS-379 三候选落点) · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (E-1 板侧项) ★
> ★**本单边界**: ★**零写板 · 零落表 · 零改已签收件 / 既有页面正文 · 零改既有闸 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★ ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★
> ★**证据分级**: ★`[官网]` / ★`[实测]` / ★`[媒体]` / ★`[推算]` / ★`[0数据]` (★五级白名单·★本单实际用到 `[实测]` `[推算]` `[0数据]` 三级★) ★

★**判据常量取法 (★本页与闸都不写死★)**: ★`CRIT` / `TOL` **现场从 `MECH/service_port_check.py` L126-L127 源码读** ⇒ ★`TOL["fdm_part"] = 0.30` · `CRIT = 2 × TOL["fdm_part"] = 0.60` ⇒ ★**达标所需每边名义余量 `req = CRIT + TOL["fdm_part"] = 0.9000`** ★

★**判据链 (★ISS-377 §0.1·两件同一公式★)**:
```
① 座体必须清空区 H (X/Y 宽)      ② 铜箔包络 C (X/Y 宽)
③ 同源化必须清空区 M = max(H, C)  ④ 开口余量 (每边) = (O − M) / 2      O = 罩开口宽
⑤ 罩住余量 (每边) = (H − C) / 2    ⑥ 最坏余量 = 余量 − TOL["fdm_part"]  ⑦ 判据: 最坏余量 ≥ CRIT
```

---

## ★§0 一句话结论 (★三句·每件一句 + 结构件动不动一句★)★

★**`J_DEBUG` 一句**: ★**座体必须清空区从 `1.7750` 改到 `6.6100` (X) / `2.5400` 改到 `2.8000` (Y) —— 铜箔每边超出清空区 `1.5175`, 装不进; 罩开口 X `10.2000` 一字不动, 罩开口 Y `4.6000` 也不动 (但余量恰好卡在 `CRIT`, 零容差)** ★

★**`J_UART` 一句**: ★**座体必须清空区从 `2.5400` 改到 `4.0700` (X) / `2.5400` 改到 `2.8000` (Y) —— 中心随落点走 (`17.9650`/`19.0350`/`18.9350`); 罩开口 X `10.2000` 不动; ★**罩开口 Y `4.6000` 只有在落点 `C1`/`C3` 下才成立, 落点 `C2` 差 `0.2000` 放不下, 必须把开口 Y 改到含 `66.1000..70.7000`** ★

★**「结构件在那一趟动不动」一句**: ★**要动 —— 而且是【两件同批都动】**: `J_DEBUG` 三个清空区竞争值算下来全红 ⇒ 无论如何都要动; `J_UART` 换官方 THT 后罩住余量 `0.1350` (最坏 `-0.1650`) 判红 ⇒ 也要动; ⇒ ★**若 `B33_PIN_LAND_1P27` 两件都含 (OI-2), 结构件必须同批返工两次机会都不给 ⇒ 板只改一次的纪律要求: 改件要求单必须在那一趟开工前定死 (本单 §0/§1/§2/§3/§4 就是那份定死用的单子)** ★

---

## ★§1 两件合到一件的【统一口径表】 (★不许分两票★)★

★**★口径说明 (★读这张表前必读★)★**:
- ★**「余量 / 最坏余量 / 红绿」三列 = 【现状结构件】对【那一趟板侧换官方 P1.27 THT land 之后的铜箔】算出来的值** ⇒ 这是「那一趟不改结构件会怎样」的判决 ★
- ★**「目标余量 / 目标最坏余量 / 目标红绿」三列 = 改件要求单落地之后 (结构件按 §2/§3 改完) 的值** ⇒ 这是「改完能不能过」 ★
- ★**轴口径**: `X` / `Y` = 罩住轴 (判据链只含 X/Y 两轴) · `Z` = 座体高 `h`, **无罩住余量判据** ⇒ 三列一律 `N/A` (★不是漏填★)
- ★**`J_DEBUG` 的 X 走【同心宽口径】** (`(H − C)/2`, ★ISS-386 §1 口径来源 X = `copper_driven`★) ⇒ 与 ISS-386 同一口径 ⇒ 两页数字逐字可比 ★

| 件 | 轴 | 现状值 | 那一趟后目标值 | 余量 | 最坏余量 | CRIT | 红/绿 | 目标余量 | 目标最坏余量 | 目标红/绿 | 谁改哪一处 | 改件项 | 判据来源 (页:行) | 证据等级 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `J_DEBUG` | X | `1.7750` | `6.6100` | `-1.5175` | `-1.8175` | `0.6000` | ★**红** ★ | `0.9000` | `0.6000` | ★**绿** ★ | 座体必须清空区 (结构件内腔) | `D-1` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§1` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `J_DEBUG` | Y | `2.5400` | `2.8000` | `0.7700` | `0.4700` | `0.6000` | ★**红** ★ | `0.9000` | `0.6000` | ★**绿** ★ | 座体必须清空区 (结构件内腔) | `D-2` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L183` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§1` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `J_DEBUG` | Z | `[0数据]` (MECH 现行模型 `2.5400`) | `2.5400` (沿用现行模型档) | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | 本单不改 (座体高定档归 boss, `OI-11`) | `D-5` | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1` · `MECH/service_port_check.py L126-L127` | `[0数据]` |
| `J_UART` | X | `2.5400` | `4.0700` | `0.1350` | `-0.1650` | `0.6000` | ★**红** ★ | `0.9000` | `0.6000` | ★**绿** ★ | 座体必须清空区 (结构件内腔) | `U-1` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§1` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `J_UART` | Y | `2.5400` | `2.8000` | `0.7700` | `0.4700` | `0.6000` | ★**红** ★ | `0.9000` | `0.6000` | ★**绿** ★ | 座体必须清空区 (结构件内腔) | `U-2` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L196` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§1` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `J_UART` | Z | `[0数据]` (MECH 现行模型 `2.5400`) | `2.5400` (沿用现行模型档) | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | 本单不改 (座体高定档归 boss, `OI-11`) | `U-6` | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1` · `MECH/service_port_check.py L126-L127` | `[0数据]` |

★**★读这张表的四条纪律★**:
1. ★**两件的「红/绿」方向【完全相同】(X 轴都红 / Y 轴都红 / Z 轴都不判)** ⇒ ★**「两个连接器分两票」这个病根在口径层已经堵死** ★
2. ★**「红」不是「一件红一件绿」的混账** —— 两件同红 ⇒ ★**那一趟两件结构件必须同批返工**, 不能只动一件 ★
3. ★**目标列三件全绿** ⇒ ★**改完是能装的**, 不是「改完还是红」 ★
4. ★**目标列的余量全部【恰好等于 `CRIT`】** (`最坏余量 0.6000` = `CRIT` `0.6000`) ⇒ ★**「改完刚好压线」, 不是「改完有余量」⇒ §5 `OI-13` 就是问这个余量要不要** ★

---

## ★§2 `J_DEBUG` 改件要求单 (★逐条: 现状 / 改后 / 谁改哪一处★)★

★**★每条三件事缺一不可: ① 现状是什么 (页:行 + 实测) ② 那一趟后要变成什么 (具体 mm 数) ③ 谁改哪一处 (板侧铜箔 / 开口 / 清空区 / 座体选型)★ ★★本页不出现任何没有数的说法★ ★**

| 改件项 | 改件项名 | ① 现状 (页:行 + 实测) | ② 那一趟后 (具体 mm) | ③ 谁改哪一处 | 判据来源 (页:行) | 证据等级 |
|---|---|---|---|---|---|---|
| `D-1` | ★**座体必须清空区 X 宽** ★ | `1.7750` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351`: X `142.063..143.838` (宽 `1.7750`, 中心 `142.9500`) | ★**`6.6100` — X `139.6450..146.2550` (中心 `142.9500` 不动)** ★ | ★**清空区 (结构件内腔)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§3` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `D-2` | ★**座体必须清空区 Y 宽** ★ | `2.5400` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L183`: Y `55.330..57.870` (中心 `56.6000`) | ★**`2.8000` — Y `55.2000..58.0000` (中心 `56.6000` 不动)** ★ | ★**清空区 (结构件内腔)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L183` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§1` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `D-3` | ★**罩开口 X 宽与位置** ★ | `10.2000` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352`: X `137.850..148.050` (中心 `142.9500`) | ★**`10.2000` — X `137.850..148.050` (一字不动)** ★ | ★**开口 (不改)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §1` · `§3` | `[实测]`+`[推算]` |
| `D-4` | ★**罩开口 Y 宽与位置** ★ | `4.6000` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352`: Y `54.300..58.900` (中心 `56.6000`) | ★**`4.6000` — Y `54.300..58.900` (不改) ★ ⇒ 但开口 Y 每边余量只有 `0.9000` ⇒ 最坏 `0.6000` = `CRIT` ⇒ 零容差 ⇒ `OI-13` 的两��路见 §5** ★ | ★**开口 (口径待 main+boss 裁, `OI-13`)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§1` | `[实测]`+`[推算]` |
| `D-5` | ★**座体真实高 `h`** ★ | `[0数据]` (MECH 现行模型假设 `2.5400`) — `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1` | ★**本趟不动 (沿用 `2.5400` 档) ★ ⇒ 若 boss 定 `4.0000` 档 ⇒ `D-2` 改 `4.0000` 且 `D-4` 开口 Y 改 `5.8000`** ★ | ★**boss (`OI-11`)** ★ | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1` · `MECH/service_port_check.py L126-L127` | `[0数据]` |
| `D-6` | ★**座体选型 / keepout** ★ | `[0数据]` (本机无厂商 keepout 图纸) ; 官方 1×4 THT 座体本体 (`F.Fab`) X `5.0800` × `2.1000` — `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L139` | ★**座体本体 ≤ `5.0800` × `2.1000` ; 占位清空区按 `D-1`/`D-2` 开 (`6.6100` × `2.8000`) ⇒ 每边比座体本体多让 `0.7650`** ★ | ★**座体选型 + 开模 (结构件侧)** ★ | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L139` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §5` | `[实测]`+`[0数据]` |
| `D-7` | ★**板侧铜箔落点 (居中解)** ★ | 铜箔 X 宽 `1.7750`, X `142.0625..143.8375` × Y `56.1500..57.0500`, 中心 `(142.9500, 56.6000)` — `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L61` | ★**换官方 1×4 THT 后铜箔 X `140.5450..145.3550` × Y `56.1000..57.1000`, 中心锁 `(142.9500, 56.6000)` ⇒ ★**X 向允许中心偏心 `±0.4475`, Y 向允许中心偏心 `0.0000`** ★ (★官方 land 的 `pad1` 在局部 `(0,0)`, 而现状封装的 `pad1` 在局部 `(-2.10, -1.40)` ⇒ 换 land 必须重定封装原点, 否则铜箔整体平移 `(+2.1000, +1.4000)` 直接顶死开口★)** ★ | ★**板侧封装原点 (main; `E-1` 已拍 pitch, 朝向归 sw-lead 的 ISS-378)** ★ | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L61` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L98` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §2.1` | `[实测]`+`[推算]` |
| `D-8` | ★**板侧铜箔 (换不换)** ★ | 现状自绘 SMD 占位 pitch `0.50`, 4 脚, 铜箔 `1.7750` × `0.9000` — `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63` | ★**换官方 P1.27 THT land (铜箔 `4.8100` × `1.0000`)** ★ | ★**板侧铜箔 (main; `B33_PIN_LAND_1P27`)** ★ | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105` | `[实测]` |

★**★`J_DEBUG` 出件口径 (★照这三条就能开模·★不改板面任何一行★)★**:
1. ★**罩开口 X `137.8500..148.0500` (宽 `10.2000`) 一字不动** —— 铜箔中心 `142.9500` 不动 ⇒ 开口不动 (ISS-371 L190 同源) ★
2. ★**座体占位清空区 X `139.6450..146.2550` (宽 `6.6100`) × Y `55.2000..58.0000` (宽 `2.8000`)**, 中心 `(142.9500, 56.6000)` ★
3. ★**罩开口 Y `54.3000..58.9000` (宽 `4.6000`) 不动** ⇒ 开口 Y 每边余量 `0.9000` ⇒ 最坏 `0.6000` = `CRIT` ⇒ **压线零容差** (★`OI-13` 的代价就在这行★) ★

---

## ★§3 `J_UART` 改件要求单 (★逐条: 现状 / 改后 / 谁改哪一处★)★

| 改件项 | 改件项名 | ① 现状 (页:行 + 实测) | ② 那一趟后 (具体 mm) | ③ 谁改哪一处 | 判据来源 (页:行) | 证据等级 |
|---|---|---|---|---|---|---|
| `U-1` | ★**座体必须清空区 X 宽** ★ | `2.5400` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346`: X `17.620..20.160` (宽 `2.5400`, 中心 `18.8900`) | ★**`4.0700` — 中心随落点: `C1` 中心 `17.9650` ⇒ X `15.9300..20.0000` ; `C2` 中心 `19.0350` ⇒ X `17.0000..21.0700` ; `C3` 中心 `18.9350` ⇒ X `16.9000..20.9700`** ★ | ★**清空区 (结构件内腔)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§2.1` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `U-2` | ★**座体必须清空区 Y 宽** ★ | `2.5400` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L196`: Y `67.330..69.870` (中心 `68.6000`) | ★**`2.8000` — Y `67.2000..70.0000` (落点 `C1`/`C3` 中心 `68.6000` 不动; 落点 `C2` 中心 `68.4000` ⇒ Y `67.0000..69.8000`, 但那样开口就装不下 ⇒ 见 `U-4`)** ★ | ★**清空区 (结构件内腔)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L196` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§1` · `MECH/service_port_check.py L126-L127` | `[实测]`+`[推算]` |
| `U-3` | ★**罩开口 X 宽与位置** ★ | `10.2000` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347`: X `13.790..23.990` (中心 `18.8900`) | ★**`10.2000` — X `13.790..23.990` (一字不动)** ★ ⇒ 三候选的开口 X 每边余量 `2.1400`/`3.9900` (`C1`) · `3.2100`/`2.9200` (`C2`) · `3.1100`/`3.0200` (`C3`) ⇒ 最坏 `1.8400` ≥ `CRIT` ⇒ **开口 X 不是卡点** ★ | ★**开口 (不改)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §1` · `§2` | `[实测]`+`[推算]` |
| `U-4` | ★**罩开口 Y 宽与位置 (★分落点·本单新算★)** ★ | `4.6000` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347`: Y `66.300..70.900` (中心 `68.6000`) | ★**落点 `C1`/`C3` ⇒ `4.6000` — Y `66.300..70.900` 不动 (但每边余量恰 `0.9000` ⇒ 最坏 `0.6000` = `CRIT` ⇒ 零容差) ; 落点 `C2` ⇒ ★**开口 Y 必须含 `66.1000..70.7000`** ★ ⇒ 二选一: ★**(a) 下移 `0.2000` (宽仍 `4.6000`, 中心改 `68.4000`) ; (b) 中心不动、宽放大到 `5.0000` (Y `66.1000..71.1000`)** ★ | ★**开口 (结构件侧; ★但选 `C2` 还是 `C1`/`C3` 归 main 的 `OI-3`★)** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347` · `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` · `§2` | `[实测]`+`[推算]` |
| `U-5` | ★**座体在罩内的平移量** ★ | 现状清空区中心 X `18.8900` — `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346` | ★**`C1` 中心 `17.9650` (移 `-0.9250`) ; `C2` 中心 `19.0350` (移 `+0.1450`) ; `C3` 中心 `18.9350` (移 `+0.0450`) ⇒ 三个值都写在改件单上, 结构件照着开三套定位孔** ★ | ★**结构件侧 (落点归 main, `OI-3`)** ★ | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §2.1` · `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3` | `[推算]` |
| `U-6` | ★**座体真实高 `h`** ★ | `[0数据]` (MECH 现行模型假设 `2.5400`) | ★**本趟不动 (沿用 `2.5400` 档) ⇒ 与 `D-5` 同档同口径** ★ | ★**boss (`OI-11`)** ★ | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1` · `MECH/service_port_check.py L126-L127` | `[0数据]` |
| `U-7` | ★**座体选型 / keepout** ★ | `[0数据]` (本机无厂商 keepout 图纸) ; 官方 1×2 THT 座体本体 (`F.Fab`) `2.6400` × `2.2000` — `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L118` | ★**座体本体 ≤ `2.6400` × `2.2000` ; 占位清空区按 `U-1`/`U-2` 开 (`4.0700` × `2.8000`) ⇒ 每边比座体本体多让 `0.7150`** ★ | ★**座体选型 + 开模 (结构件侧)** ★ | `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L118` · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §5` | `[实测]`+`[0数据]` |
| `U-8` | ★**板侧铜箔 (换不换)** ★ | 现状自绘 SMD 占位 pitch `0.50`, 2 脚, 铜箔 `0.7750` × `0.9000` — `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63` | ★**换官方 P1×2 THT land (铜箔 `2.2700` × `1.0000`)** ★ ⇒ ★**若 `OI-2` 判「不含」⇒ 本行不执行, `U-1`~`U-5` 全部不执行, `J_UART` 结构件零返工** ★ | ★**板侧铜箔 (main; `OI-2`)** ★ | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63` · `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L32` | `[实测]` |
| `U-9` | ★**落点的 Y 向可行域 (★本单新算·★ISS-386 未覆盖★)** ★ | ISS-386 §2.1 只给了【X 向】需求 `4.0700`, ★**没有校 Y 向「清空区放不放得进开口」** ★ ; 本单实算: 铜箔相对罩开口每边内缩必须 ≥ `1.8000` | ★**精确判据: 铜箔相对罩开口每边内缩量必须 ≥ `2 × 0.9000 = 1.8000` ⇒ ★**`C1` 铜箔 Y 中心必须 = `68.6000` (允许偏心 `0.0000`) ; `C3` 同 (允许偏心 `0.0000`) ; `C2` 铜箔 Y 中心 `68.4000` ⇒ 内缩只有 `1.6000` ⇒ 差 `0.2000` ⇒ 【不可行】, 除非按 `U-4` 改开口 Y** ★ ⇒ ★**X 向三候选全部可行 (允许偏心 `+0.6200`/`+1.0100`/`+1.0600`)** ★ | ★**板侧落点 (main, `OI-3`)** ★ | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1` · `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3` · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347` | `[实测]`+`[推算]` |

★**★`J_UART` 出件口径 (★照这三条就能开模·★但落点要 main 先定★)★**:
1. ★**罩开口 X `13.7900..23.9900` (宽 `10.2000`) 一字不动** ★
2. ★**座体占位清空区 X 宽 `4.0700` (中心三选一: `17.9650` / `19.0350` / `18.9350`) × Y 宽 `2.8000`** ★
3. ★**罩开口 Y `66.3000..70.9000` (宽 `4.6000`) 只在落点 `C1`/`C3` 下成立** ; ★**落点 `C2` ⇒ 开口 Y 改 `66.1000..70.7000` (宽 `4.6000`, 下移 `0.2000`) 或 `66.1000..71.1000` (宽 `5.0000`)** ★

---

## ★§4 三档返工幅度代价账 (`OI-5` · ★只给代价, 不给裁决★)★

★**★三个竞争值的出处 (★互不相干的三条推导链★)★**: ★`1.7750` = 真相页「座体宽 = 板读铜箔宽」(`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351`) · ★`4.0850` = 现页四处「把现状 `0.275` 宽 pad 搬到 1.27 pitch 上」(`3.81 + 0.275`, `MECH/BOARD_ONEPASS_MECH_SYNC.md L561`) · ★`4.8100` = 官方 THT 真 land (`3.81 + 1.00`, `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105`) ★

| # | 清空区 X 宽档 | 罩住余量 X | 最坏余量 | 单边超出量 | 要过判据需的清空区 X 宽 | ★**结构件总宽增量 (到 `6.6100`)** ★ | 几何不干涉所需 (`4.8100`) 的增量 | 红绿 | 出处 (页:行) | 证据等级 |
|---|---|---|---|---|---|---|---|---|---|---|
| ① | `1.7750` | `-1.5175` | `-1.8175` | `1.5175` | `6.6100` | ★**`+4.8350`** ★ | `+3.0350` | ★**红** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351` | `[实测]`+`[推算]` |
| ② | `4.0850` | `-0.3625` | `-0.6625` | `0.3625` | `6.6100` | ★**`+2.5250`** ★ | `+0.7250` | ★**红** ★ | `MECH/BOARD_ONEPASS_MECH_SYNC.md L561` | `[实测]`+`[推算]` |
| ③ | `4.8100` | `0.0000` | `-0.3000` | `0.0000` (齐平) | `6.6100` | ★**`+1.8000`** ★ | `+0.0000` | ★**红** (最坏 `-0.3000` < `CRIT`) ★ | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105` | `[实测]`+`[推算]` |

★**★四条读法 (★这是本页给 main 的核心信息★)★**:
1. ★**三档的【红绿方向完全相同】(全部红) ⇒ `OI-5` 选哪个【只改返工幅度】, 不改这一趟「结构件要不要动」** ⇒ ★**`J_DEBUG` 的结构件在那一趟无论如何都要动 ⇒ 不存在「先只改 `J_UART`」的省事方案** ★
2. ★**★目标值三档【完全相同】= `6.6100` ⇒ `OI-5` 不改改件要求单, 只改【结构件总宽增量】(`+4.8350` / `+2.5250` / `+1.8000`) ⇒ 三档差 `3.0350`** ★ ⇒ ★**改件要求单可以在 `OI-5` 没定之前就照 `6.6100` 写 (本单 §2 `D-1` 就是), 但【返工工时/工装/镜脚内腔尺寸】要在 `OI-5` 定了之后才敢冻结** ★
3. ★**要过罩住判据的清空区 X 宽需求 = 铜箔 `4.8100` + 2 × `0.9000` = `6.6100`** ⇒ ★**比官方 land 自己的 `F.CrtYd` `6.0900` 还大 `0.5200`** ⇒ `OI-12` (归 main + boss, 本单 §5 答) ★
4. ★**开口侧不受 `OI-5` 影响**: `M = max(H, C)` 在三档下都取 `4.8100` ⇒ 开口余量 X 恒为 `2.6950` (最坏 `2.3950`) ⇒ ★**开口 X `10.2000` 够用 (要容 `H = 6.6100` 也只需每边 `1.7950`, 最坏 `1.4950` ≥ `CRIT`) ⇒ 只改清空区 X, 开口 X 不动** ★

★**★本页不写「应采用 X」★** ⇒ 裁决权留给 main (机器块 `decisions.clearance_x_tier_decision = not_decided_here`) ★

---

## ★§5 四条【结构侧能自答的】逐条答 (★只答技术面, 不代 main / boss 拍★)★

### ★§5.1 `OI-2` — `B33_PIN_LAND_1P27` 的范围含不含 `J_UART` (归 main) ★

★**结构侧的技术面已答完 (两条腿的代价都算死), 只等 main 一句话** ★

| 分支 | 结构件后果 | 代价 (具体数) | 遗留耦合 |
|---|---|---|---|
| ★**含 `J_UART`** ★ | `J_UART` 结构件**同批返工**: 清空区 `2.5400`×`2.5400` → `4.0700`×`2.8000` (X `+1.5300`, Y `+0.2600`), 中心随落点移 (`-0.9250`/`+0.1450`/`+0.0450`) | 罩开口 X 不动; ★**罩开口 Y 只有落点 `C1`/`C3` 才不动, 落点 `C2` 要改到含 `66.1000..70.7000` (见 `U-4`)** | ★**落点裁决 (`OI-3`) 与本条耦合**: `C2` 的 Y 向不可行 ⇒ 若 main 定了 `C2`, 结构件还得再改一次开口 Y ⇒ ★**这两条必须一起拍, 分开拍会返工第二次** ★ |
| ★**不含 `J_UART`** ★ | `J_UART` 结构件**零返工**: 清空区保持 `2.5400` × `2.5400` (现状值) | 结构件省一次返工; ★**但 `J_UART` 就换不成官方 1×2 THT land ⇒ 板上 BOM (`HW/BOM_v1.csv:77`) 与网表 (`HW/netlist_v1.csv:399`) 写的 1.27mm 实物排针仍落不进 0.50mm pitch 的自绘占位 land (Δ pitch `0.77`)** ⇒ ★**结构件零返工 ≠ 实物装配问题解决** | `J_UART` 结构件与 `J_DEBUG` 结构件**不在同一趟改** ⇒ 两件座体占位尺寸不同 (`6.6100` vs `2.5400`) ⇒ 同一套镜脚内腔里两个不同的座体孔位 ⇒ 装配工装要两套 |

★**结构侧的结论**: ★**这不是结构侧能裁的范围题 (范围裁决权在 main), 但两条腿的代价与后果结构侧已全部量化** ⇒ ★**答复窗口 = 板框上位问题 (`boss_u1_upper_axis_board_trip_physical_product`) 的同一个窗口** —— 因为结构件一旦开模/下单就没法回头 ★

★**证据等级**: 分支代价 `[推算]` ; Δ pitch `0.77` 与 BOM/网表 1.27mm `[实测]` (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63`) ★

### ★§5.2 `OI-12` — ⑤ 罩住判据对 THT 排针是不是过严 (归 main + boss) ★

★**★先把硬差额摆出来 (★这不是空谈·是有数的★)★**:

| 项 | `J_DEBUG` | `J_UART` | 出处 (页:行) |
|---|---|---|---|
| 官方 THT 铜箔 X 宽 | `4.8100` | `2.2700` | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105` · `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L32` |
| 官方 land 的 `F.CrtYd` (板向 X) | `6.0900` (★**真 `F.CrtYd` 图元**★) | `3.5500` (★**本封装无 `F.CrtYd` 图元, 是 `GetBoundingBox` 退包络**★) | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L140` · `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md L63` |
| courtyard 给的每边余量 | `0.6400` | `0.6400` | 同上 (÷2) |
| ★**判据要求的每边余量** ★ | ★`0.9000` (`CRIT` `0.6000` + `TOL` `0.3000`) ★ | ★`0.9000` ★ | `MECH/service_port_check.py L126-L127` |
| ★**差额** ★ | ★**每边 `0.2600`, 总宽 `0.5200`** (`6.6100` − `6.0900`) ★ | ★**每边 `0.2600`, 总宽 `0.5200`** (`4.0700` − `3.5500`) ★ | 推算 |
| 判据要求的清空区 X 宽 | `6.6100` | `4.0700` | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0` |

★**⇒ 结构侧的答复 (★只摆事实与两条路, 不代裁★)★**: ★**这条判据要的不是「座体放得下」, 而是「座体 + 每边 `0.9000` 的空气带」; IPC 的 courtyard 给的是器件本体加倒角, 本来就不含装配空气带 ⇒ 对 THT 排针说它「过严」在口径上站得住 ⇒ 但它在数字上是【硬差额 `0.5200`】, 不是感觉** ★

| 路 | 判据改成什么 | 清空区 X 需求 | 结构件每边多让 (对座体本体) | 代价 |
|---|---|---|---|---|
| ★**路 A — 判据不动** ★ | 「最坏余量 = 余量 − `TOL` ≥ `CRIT`」保持 | `J_DEBUG` `6.6100` · `J_UART` `4.0700` | `J_DEBUG` `(6.6100 − 5.0800)/2 = 0.7650` · `J_UART` `(4.0700 − 2.6400)/2 = 0.7150` | ★**不改任何既有判据页** ; 镜脚内腔按「座体本体 + 每边 `0.9000` 空气」开 ⇒ 内腔变大 + 罩外观缝变大 + 装配工装按内腔走 ; Y 向不受影响 (`h = 2.54` 档) ★ |
| ★**路 B — 判据改口径 (名义余量)** ★ | 「名义余量 ≥ `CRIT`」(不扣 `TOL`) | `J_DEBUG` `6.0100` · `J_UART` `3.4700` | `J_DEBUG` `(6.0100 − 5.0800)/2 = 0.4650` · `J_UART` `(3.4700 − 2.6400)/2 = 0.4150` | ★**`J_DEBUG` 的 `6.0100` 比 courtyard `6.0900` 还小 `0.0800` ⇒ 「比 courtyard 还大」的反常消失** ; 但 FDM 件 `±0.3000`/边的制造公差不再被扣除 ⇒ 装配后实际余量只剩 `0.3000` (不干涉, 但过阈无裕度) ; ★**口径一改, 本页 §1~§4 全部余量与三档代价要重算** ; ★**且 `J_UART` 的 `3.4700` 正好等于 ISS-377 §3.2 `DP-1` 那个数 ⇒ 路 B 一改, `OI-14` 同时消掉** ★ |

★**★一条必须一起拍的耦合 (★结构侧提醒, 不代裁★)★**: ★**`OI-12` 和 `OI-14` 是同一个决定的两面** —— 走「路 A」则 `3.4700` 差 `0.6000` 仍要订正为 `4.0700` ; 走「路 B」则 `3.4700` 反而是对的 ⇒ ★**这两条分开拍, 一定会得到互相矛盾的两个数** ★

★**证据等级**: 差额与两条路的数字 `[推算]` ; courtyard / `F.Fab` 值 `[实测]` (ISS-371 §0.1 / ISS-374 §2 实读官方 `.kicad_mod`) ★

### ★§5.3 `OI-13` — Y 向零制造余量接受吗 (归 main + boss) ★

★**★硬事实 (★两条, 都带数★)★**:
1. ★**罩开口 Y `4.6000` 只容清空区 Y `2.8000`** ⇒ 每边 `0.9000` ⇒ 最坏 `0.6000` = `CRIT` ⇒ ★**余量恰好等于判据, 一点不多** (来源: `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347` + `MECH/service_port_check.py L126-L127`) ★
2. ★**★本单新算的一条更硬的: Y 向【铜箔中心允许偏心 = `0.0000`】** ★ ⇒ 铜箔相对罩开口每边内缩量必须 ≥ `2 × 0.9000 = 1.8000`, 而 `J_DEBUG` 与落点 `C1`/`C3` 的内缩量【恰好就是 `1.8000`】 ⇒ ★**铜箔中心偏 `1 µm` 就装不下** ; 落点 `C2` 内缩只有 `1.6000` ⇒ 差 `0.2000` ⇒ **不可行** (来源: `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352` + `L347` + `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3`) ★

★**结构侧的答复 (★给两条路与各自代价, 不代裁★)★**:
- ★**「接受零余量」在物理上【不产生干涉】** (最坏余量 `0.6000` > `0` ⇒ FDM 公差已被扣过一轮) ⇒ ★**它省的是结构件一次开模, 付的是装配零容错 + 落点零容差** —— 风险落在「手工对位」上, 不落在尺寸上 ★
- ★**「放大开口 Y」⇒ 罩开口 Y 重做, 两件同批** ★

| 路 | 罩开口 Y | 每边余量 / 最坏 | 裕出 `CRIT` | 结构件代价 |
|---|---|---|---|---|
| ★**路 A — 接受零余量** ★ | `4.6000` (不动) | `0.9000` / `0.6000` | `0.0000` | 开口零改动 ; ★**代价: `J_DEBUG` 与落点 `C1`/`C3` 的 Y 向偏心容差 `0.0000` ; 装配全靠人工对位** ★ |
| ★**路 B — 开口 Y 放大 `Δ`** ★ | `4.6000 + 2Δ` ⇒ 例: `Δ = 0.5000` ⇒ `5.6000` ; `Δ = 0.6000` ⇒ `5.8000` | `Δ = 0.5000` ⇒ `1.4000` / `1.1000` ; `Δ = 0.6000` ⇒ `1.5000` / `1.2000` | `0.5000` / `0.6000` | ★**罩开口 Y 从 `4.6000` 放大 ⇒ 罩外观缝 + 防水防尘 + 镜脚壁厚同批重做; 两件同批** ★ |

★**★一条自带自洽的组合 (★结构侧给账, 不代裁★)★**: ★**若 boss 把座体高 `h` 定在 `4.0000` 档 ⇒ 清空区 Y 变 `4.0000` ⇒ 罩开口 Y 必需 `4.0000 + 2 × 0.9000 = 5.8000` ⇒ 开口 Y 一放大就把落点 `C2` 的 `0.2000` 缺口一并补上 (`5.8000` 宽下 `C2` 可行) ⇒ 一次改动同时解掉 `OI-13` 与落点 `C2` 的死结** ★ ⇒ ★**但 `h` 定档是 boss 的裁决权 (`OI-11`), 本单只给这条账** ★

★**证据等级**: 硬事实 `[实测]` + `[推算]` ; 开口放大后的数字 `[推算]` ★

### ★§5.4 `OI-14` — ISS-377 §3.2 `DP-1` 的 `3.4700` 要不要订正为 `4.0700` (归 main) ★

★**★结构侧的技术面可以自答: 在现行判据链下, `3.4700` 不够, 差 `0.6000`★**

| 口径 | 公式 | `J_UART` 清空区 X | 罩住余量 | 最坏余量 | 判据 |
|---|---|---|---|---|---|
| 现行判据链 (全链) | 铜箔 + 2 × (`CRIT` + `TOL`) = `2.2700` + 2 × `0.9000` | `4.0700` | `0.9000` | `0.6000` | ★**恰好过阈** ★ |
| 名义余量口径 (ISS-377 `DP-1` 用的) | 铜箔 + 2 × `CRIT` = `2.2700` + 2 × `0.6000` | `3.4700` | `0.6000` | `0.3000` | ★**`0.3000` < `CRIT` `0.6000` ⇒ 不过阈** ★ |

⇒ ★**结构侧的结论: 按 `3.4700` 出件, 那一趟会再判一次红 ⇒ 【本单的改件要求单必须按 `4.0700` 写】(本单 §3 `U-1` 就是 `4.0700`) ⇒ 结构侧不再有技术问题** ★

★**留给 main 的只剩一件**: ★**「要不要把这个订正块往 ISS-377 老页落」** —— 老页是已签收件, ★**本单零改老页** ⇒ 订正块只写在本页与机器块里, 由 main 决定落不落 ★

★**★但本条与 `OI-12` 必须一起拍 (★见 §5.2 末段★)★**: ★**若 main 同时选 `OI-12` 的「路 B」(名义余量口径), 则 `3.4700` 反而是对的 ⇒ 订正动作要撤销** ⇒ ★**两条是同一个决定的两面, 分开拍会得到互相矛盾的两个数** ★

★**证据等级**: 两个数的推导 `[推算]` ; `CRIT`/`TOL` `[实测]` (`MECH/service_port_check.py L126-L127`) ★

---

## ★§6 「那一趟」的闸链影响 (★沙盒预演实测·★不是推的★)★

★**★做法 (★可复现★)★**: ★把 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的两处「座体必须清空区」改成 §2/§3 的目标值 (★`J_DEBUG` → X `139.6450..146.2550` × Y `55.2000..58.0000` ; `J_UART` → X `15.9300..20.0000` × Y `67.2000..70.0000`★), 其余一字不动, 在沙盒 `tmp/iss389_sbx/probe/` 里跑既有闸 ⇒ ★**只读本机 · 零写板 · 零落表 · 真件一个字节未动** ★

| 既有闸 | 沙盒预演 rc | 触发原因 (★实测输出★) | 要不要同批落 |
|---|---|---|---|
| `MECH/check_debug_seat_3d_fit.py` | ★**1 (红)** ★ | `K3.3` ×4: ISS-386 页里的 `housing`/`opening` 与真相页不一致 ; `K3.4`/`K3.5`: 三个候选的 `cover_signed`/`cover_worst`/`open_signed`/`open_worst` 与实算不符 (★`C2` 实算 `cover_worst = -0.4700` ⇒ 因为清空区中心锁在 `C1` 的铜箔中心★) | ★**要**: ISS-386 页的机器块要按新真相页重出 (`--emit`) ★ |
| `MECH/check_juart_1p27_clearance.py` | ★**1 (红)** ★ | `J1`/`J2`: 页内每边余量与按真相页实读的座体宽重算不符 ; `J5`: 「实算两件同向」校验挂 | ★**要**: ISS-374 页的余量列要按新真相页重算 ★ |
| `MECH/check_connector_clearance_caliber.py` | ★**1 (红·★基线就红·非本单引入★)** ★ | ★**新增** `K0`: 页内座体清空区与真相页不一致 (页 `1.775`/`2.54` vs 真身 `6.61`/`2.80` · `2.54`/`2.54` vs `4.07`/`2.80`) ; `K7` 的不通过文件从 2 个变成 3 个 (★新增真相页 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 md5 与已签收基线对不上★) | ★**要**: ISS-377 页 §1 表要同步 + 基线由 main 重签 ★ |
| `MECH/check_jdebug_1p27_clearance.py` | `0` (绿) | 开口 X 取自 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md`, 不吃真相页的清空区 | 不动 |
| `MECH/check_jdebug_arrangement_truth.py` | `0` (绿) | 不依赖真相页的清空区 | 不动 |
| `MECH/check_onepass_mech_sync.py` | `0` (绿) | 不读真相页 | 不动 |
| `MECH/check_onepass_struct_crosscheck.py` | `0` (绿) | 不吃真相页的清空区 | 不动 |
| `MECH/check_onepass_mech_release.py` | `0` (绿) | | 不动 |
| `MECH/check_onepass_s10_led_spec_sync.py` | `0` (绿) | | 不动 |
| `MECH/check_board_frame_coords.py` | `0` (绿) | | 不动 |

★**★三条必须一起动的结构件模型 (★改件落地时漏掉任何一处, 结构件就对不上★)★**:
1. ★**`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`** (开口/清空区真身) L183/L196/L346/L351 四行 + L352/L347 两行 —— ★**这是唯一的几何真身源, 其余页都是从它派生** ★
2. ★**`MECH/service_port_check.py`** L222 (`OPEN_X, OPEN_Y = 10.20, 4.60`) —— ★**罩开口尺寸写死在这儿** ⇒ 若走 `OI-13` 的路 B (开口 Y 放大) 这里必须跟着改 ; ★**但 L126-L127 的 `TOL`/`CRIT` 一个字不许动 (它是全部闸的判据源头)** ★ ; ★**另注: 该文件 L70-L75 的 `jd_cols: 5` / `jd_rows: 2` 建模的是【2×5 Cortex-10 阵列】, 与板面 1×4 的 `J_DEBUG` 不是同一颗件 (板读 `J_DEBUG` = 4 脚 pitch 0.50) ⇒ 那一族镜脚末端盖板结构件不在本单范围** ★
3. ★**`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md`** (ISS-386 页) 的机器块 —— ★**必须用 `python3 MECH/check_debug_seat_3d_fit.py --emit` 重出, 不许手改** ★

★**★闸链纪律 (★本单给 main 的执行顺序建议·★不代拍★)★**: ★**结构件出件必须等「真相页 → ISS-386 页机器块 → ISS-374 页余量列 → ISS-377 页 §1 表 → 基线重签」这一串在同一批落**, 否则中途任何一道闸红着出件, 等于把「板只改一次」变成「板改两次」 ★

★**证据等级**: 本表全部 `[实测]` (沙盒实跑 rc + 实测输出) ★

---

## ★§7 降级方案 + 待裁项 (★只登记·要谁回答什么·★本单不代拍★)★

★**★降级方案 (★查不到处的必须项·零外发·不挂外部依赖★)★**:

| # | 方案 | 依据 | 代价 | 影响 |
|---|---|---|---|---|
| `DP-1` | ★**按最坏值设计**: `J_DEBUG` 清空区 X 取 `6.6100` (铜箔 `4.8100` + 2 × `0.9000`) ★ | §4 + §0 | 结构件总宽增量按 `OI-5` 三档分别是 `+4.8350`/`+2.5250`/`+1.8000` ⇒ 返工幅度要等 `OI-5` | `J_DEBUG` |
| `DP-2` | ★**按最坏值设计**: `J_UART` 清空区 X 取 `4.0700`, 中心随落点 (`17.9650`/`19.0350`/`18.9350`) ★ | §3 `U-1` + `U-5` | 中心随落点移动 ⇒ 必须与板那一趟同批; ★**`C2` 需同时按 `U-4` 改开口 Y** | `J_UART` |
| `DP-3` | ★**落点避开 `C2`**: 若 main 选 `C1` 或 `C3` ⇒ 罩开口 Y `4.6000` 一字不动, 结构件只改清空区 ★ | §3 `U-9` | `C1` 板侧余量 `0.2750` / `C3` 板侧余量 `0.0447` ⇒ `C3` 的板侧余量最薄 (`0.0447`) | `J_UART` |
| `DP-4` | ★**改设计路径绕开 (Y 向)**: 罩开口 Y 一并放大 (≥ `5.6000`, `Δ = 0.5000`; 或 `5.8000`, `Δ = 0.6000`) ★ | §5.3 `OI-13` | 罩开口 Y 规格重做 ⇒ 结构件开口与清空区同批改; 一次改动顺带解掉落点 `C2` 的死结 | `J_DEBUG` + `J_UART` |
| `DP-5` | ★**实测样件兜底**: 座体真实高 `h` 与真实型号 `[0数据]` ⇒ 按 Z 向保守上界出件, 装配前用 1 台样件实测座体占位与净距 ★ | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1` | 样件只做 1 台 (boss: 成本不是问题但别乱花) ⇒ 实测后清空区/开口按实测收口, 结构件不返工第二遍 | `J_DEBUG` + `J_UART` |
| `DP-6` | ★**判据兜底**: 若 `OI-12` 迟迟不裁 ⇒ 结构件按【两档都过得去】的 `6.0100` 起改 (口径 A/B 的交集下界 `6.0100` 与 `6.6100` 的差别是空气带, 不是干涉) ⇒ 但这样不能同时保证 `OI-13` 的零余量问题被解 ★ | §5.2 两条路 | 结构件先按 `6.6100` 开 (空气带多给的 `0.6000` 可后加工修掉, 清空区是「多挖一点」而不是「少挖一点」) ⇒ **本单只给这条兜底的可行性判断, 选不选归 main** | `J_DEBUG` |

★**★待裁项 (★本单只登记·要谁回答什么·答复窗口 = 板框上位问题的同一个窗口★)★**:

| # | 待裁项 | 要谁回答什么 | 为什么本单不能答 | 答复窗口 |
|---|---|---|---|---|
| `OI-5` | ★**`J_DEBUG` 的「必须清空区 X 宽」以哪个数为准 (`1.7750`/`4.0850`/`4.8100`)** ★ | ★**main**: 「取哪一个?」 ★ | 三个数在仓里并存, 裁决权在 main ; ★**本单只摆三行代价 (§4) 且已证明目标值三档同 = `6.6100`** ★ | ★**与板框上位问题同窗口** ★ |
| `OI-3` | ★**`J_UART` 落点三选一 (`C1` rot 270 / `C2` rot 90 / `C3` rot 90)** ★ | ★**main**: 「定哪个?」 ★ | 落点裁决权在 main ; ★**本单已给出三候选的 X/Y 向可行域 (§3 `U-9`): `C2` 的 Y 向差 `0.2000` 不可行** ★ | ★**与板框上位问题同窗口** ★ |
| `OI-2` | ★**`B33_PIN_LAND_1P27` 含不含 `J_UART`** ★ | ★**main**: 「含还是不含?」 ★ | 板那一趟的范围裁决权在 main ; ★**结构侧两条腿的代价已算死 (§5.1)** ★ | ★**与板框上位问题同窗口** ★ |
| `OI-11` | ★**座体真实高 `h` (`[0数据]`)** ★ | ★**boss**: 「走三档参数化还是定版一个值锁死?」 ★ | 无实物依据 ; ★**X 向判决与 `h` 无关 ⇒ 不阻塞 `OI-5`** ★ | ★**与板框上位问题同窗口** ★ |
| `OI-12` | ★**⑤ 罩住判据对 THT 排针是否过严 (差 `0.5200`)** ★ | ★**main + boss**: 「判据改不改?」 ★ | 口径裁决权不在结构侧 ; ★**本单给两条路与各自代价 (§5.2)** ★ | ★**与板框上位问题同窗口** ★ |
| `OI-13` | ★**Y 向零制造余量接受吗 (偏心容差 `0.0000`)** ★ | ★**main + boss**: 「接受还是开口 Y 一起放大?」 ★ | 口径 + 成本取舍 ; ★**本单给两条路与各自代价 (§5.3)** ★ | ★**与板框上位问题同窗口** ★ |
| `OI-14` | ★**ISS-377 §3.2 `DP-1` 的 `3.4700` 订正为 `4.0700`?** ★ | ★**main**: 「订正块往老页落不落?」 ★ | 老页是已签收件, 本单零改 ; ★**结构侧已自答: 现行判据链下 `3.4700` 差 `0.6000` 不过阈** ★ | ★**与板框上位问题同窗口** ★ |

★**★本单不挂任何外部依赖 (★零外发·页内不写任何把外部依赖挂起来的措辞★)★**: ★**所有 `[0数据]` 处都给了降级方案 (`DP-1`~`DP-6`) ⇒ 没有需要外部回复才能推进的项** ★

---

## ★§8 复跑命令 + 机器块 ★

### ★§8.1 复跑命令 (★每个数都能自己跑出来★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★★本单新建闸 (★只读·零挂链·★判据逐条列★)★★
python3 MECH/check_debug_seat_rework_spec.py             # rc=0 · 末行 PASS
python3 MECH/check_debug_seat_rework_spec.py --selftest  # rc=0 · 末行 ALL TESTS PASS
python3 MECH/check_debug_seat_rework_spec.py --emit      # 打印机器块 JSON (页内 §8.2 就是它)

# ★★判据常量真身 (★现场读·不写死★)★★
grep -n 'TOL = {"fdm_part"\|CRIT = 2 \* TOL' MECH/service_port_check.py

# ★★开口 / 必须清空区真身 (★只读)★★
sed -n '183p;196p;346,347p;351,352p' MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md

# ★★上游合一件答页 (★只读·零改)★★
python3 MECH/check_debug_seat_3d_fit.py ; echo rc=$?

# ★★Y 向可行域实算 (★本单新算·★沙盒脚本★)★
python3 tmp/iss389_sbx/feas2.py

# ★★闸链影响沙盒预演 (★只改沙盒·真件零写)★
python3 tmp/iss389_sbx/probe_apply.py
for g in check_debug_seat_3d_fit check_jdebug_1p27_clearance check_juart_1p27_clearance \
         check_jdebug_arrangement_truth check_onepass_mech_sync check_onepass_mech_release \
         check_connector_clearance_caliber check_onepass_s10_led_spec_sync check_board_frame_coords; do
  printf "%-38s " "$g"; python3 tmp/iss389_sbx/probe/MECH/$g.py --root tmp/iss389_sbx/probe >/dev/null 2>&1; echo "rc=$?";
done

# ★★零写板 / 零落表 / 零挂链 自证★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%n %y %s' HW/PCB/demo_mainboard.kicad_pcb
grep -c check_debug_seat_rework_spec state/gate_check.py     # 必须 0

# ★★台账侧 (★签收归 main·本单不自签★)★★
python3 state/merge.py                                   # rc=0
python3 state/gate_check.py                              # rc=0 · Q1 18/18
python3 state/check_brief_commands.py                    # rc=0
```

### ★§8.2 机器可读 JSON 块 (★`MECH/check_debug_seat_rework_spec.py` 只认这块★)★

<!-- MECH-DEBUG-SEAT-REWORK-SPEC-JSON-BEGIN -->

```json
{
 "schema": "mech.debug.seat.rework.spec.v1",
 "issue": "ISS-389",
 "agent": "mech-lead",
 "updated": "2026-11-24",
 "criterion": {
  "crit_source": "MECH/service_port_check.py L126-L127 (CRIT = 2 * TOL['fdm_part'])",
  "crit_value": 0.6,
  "tol_fdm_part": 0.3,
  "required_margin_per_side": 0.9,
  "axes": ["x", "y"],
  "formula": "M = max(H_housing, C_copper) per axis; margin_open = (O_opening - M)/2; margin_cover = (H_housing - C_copper)/2; worst = margin - TOL['fdm_part']; pass iff worst >= CRIT",
  "placement_rule": "存在宽 W 的清空区 H 使 H 包含 C 且 H 含于 O 且两边各留 req <=> 铜箔相对开口每边内缩量 >= 2*req = 1.8000; 允许的铜箔中心偏心 = (内缩量 - 1.8000)/2"
 },
 "unified_rows": [
  {
   "ref": "J_DEBUG",
   "axis": "X",
   "current_value": 1.775,
   "target_value": 6.61,
   "current_margin": -1.5175,
   "current_worst": -1.8175,
   "target_margin": 0.9,
   "target_worst": 0.6,
   "crit": 0.6,
   "current_verdict": "红",
   "target_verdict": "绿",
   "owner": "座体必须清空区 (结构件内腔)",
   "item": "D-1",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §1; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "ref": "J_DEBUG",
   "axis": "Y",
   "current_value": 2.54,
   "target_value": 2.8,
   "current_margin": 0.77,
   "current_worst": 0.47,
   "target_margin": 0.9,
   "target_worst": 0.6,
   "crit": 0.6,
   "current_verdict": "红",
   "target_verdict": "绿",
   "owner": "座体必须清空区 (结构件内腔)",
   "item": "D-2",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L183; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §1; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "ref": "J_DEBUG",
   "axis": "Z",
   "current_value": null,
   "current_value_text": "[0数据] (MECH 现行模型 2.5400)",
   "target_value": 2.54,
   "current_margin": null,
   "current_worst": null,
   "target_margin": null,
   "target_worst": null,
   "crit": null,
   "current_verdict": "N/A",
   "target_verdict": "N/A",
   "owner": "本单不改 (座体高定档归 boss, OI-11)",
   "item": "D-5",
   "source": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1; MECH/service_port_check.py L126-L127",
   "evidence": "[0数据]"
  },
  {
   "ref": "J_UART",
   "axis": "X",
   "current_value": 2.54,
   "target_value": 4.07,
   "current_margin": 0.135,
   "current_worst": -0.165,
   "target_margin": 0.9,
   "target_worst": 0.6,
   "crit": 0.6,
   "current_verdict": "红",
   "target_verdict": "绿",
   "owner": "座体必须清空区 (结构件内腔)",
   "item": "U-1",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §1; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "ref": "J_UART",
   "axis": "Y",
   "current_value": 2.54,
   "target_value": 2.8,
   "current_margin": 0.77,
   "current_worst": 0.47,
   "target_margin": 0.9,
   "target_worst": 0.6,
   "crit": 0.6,
   "current_verdict": "红",
   "target_verdict": "绿",
   "owner": "座体必须清空区 (结构件内腔)",
   "item": "U-2",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L196; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §1; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "ref": "J_UART",
   "axis": "Z",
   "current_value": null,
   "current_value_text": "[0数据] (MECH 现行模型 2.5400)",
   "target_value": 2.54,
   "current_margin": null,
   "current_worst": null,
   "target_margin": null,
   "target_worst": null,
   "crit": null,
   "current_verdict": "N/A",
   "target_verdict": "N/A",
   "owner": "本单不改 (座体高定档归 boss, OI-11)",
   "item": "U-6",
   "source": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1; MECH/service_port_check.py L126-L127",
   "evidence": "[0数据]"
  }
 ],
 "clearance_x_tiers": [
  {
   "value": 1.775,
   "margin_cover_x": -1.5175,
   "worst_cover_x": -1.8175,
   "protrusion_per_side": 1.5175,
   "required_clearance_x": 6.61,
   "total_width_delta": 4.835,
   "no_interference_min": 4.81,
   "no_interference_delta": 3.035,
   "verdict": "红",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351",
   "evidence": "[实测]+[推算]"
  },
  {
   "value": 4.085,
   "margin_cover_x": -0.3625,
   "worst_cover_x": -0.6625,
   "protrusion_per_side": 0.3625,
   "required_clearance_x": 6.61,
   "total_width_delta": 2.525,
   "no_interference_min": 4.81,
   "no_interference_delta": 0.725,
   "verdict": "红",
   "source": "MECH/BOARD_ONEPASS_MECH_SYNC.md L561",
   "evidence": "[实测]+[推算]"
  },
  {
   "value": 4.81,
   "margin_cover_x": 0.0,
   "worst_cover_x": -0.3,
   "protrusion_per_side": 0.0,
   "required_clearance_x": 6.61,
   "total_width_delta": 1.8,
   "no_interference_min": 4.81,
   "no_interference_delta": 0.0,
   "verdict": "红",
   "source": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105",
   "evidence": "[实测]+[推算]"
  }
 ],
 "rework_items": [
  {
   "id": "D-1", "ref": "J_DEBUG", "name": "座体必须清空区 X 宽",
   "current_value": 1.775, "target_value": 6.61,
   "current_text": "1.7750 (X 142.063..143.838, 中心 142.9500)",
   "target_text": "6.6100 (X 139.6450..146.2550, 中心 142.9500)",
   "owner": "清空区 (结构件内腔)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §3; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "D-2", "ref": "J_DEBUG", "name": "座体必须清空区 Y 宽",
   "current_value": 2.54, "target_value": 2.8,
   "current_text": "2.5400 (Y 55.330..57.870, 中心 56.6000)",
   "target_text": "2.8000 (Y 55.2000..58.0000, 中心 56.6000)",
   "owner": "清空区 (结构件内腔)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L183; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §1; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "D-3", "ref": "J_DEBUG", "name": "罩开口 X 宽与位置",
   "current_value": 10.2, "target_value": 10.2,
   "current_text": "10.2000 (X 137.850..148.050, 中心 142.9500)",
   "target_text": "10.2000 (X 137.850..148.050, 一字不动)",
   "owner": "开口 (不改)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §1; §3",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "D-4", "ref": "J_DEBUG", "name": "罩开口 Y 宽与位置",
   "current_value": 4.6, "target_value": 4.6,
   "current_text": "4.6000 (Y 54.300..58.900, 中心 56.6000)",
   "target_text": "4.6000 (Y 54.300..58.900, 不改; 每边余量 0.9000, 最坏 0.6000 = CRIT, 零容差)",
   "owner": "开口 (口径待 main+boss 裁, OI-13)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §1",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "D-5", "ref": "J_DEBUG", "name": "座体真实高 h",
   "current_value": null, "target_value": 2.54,
   "current_text": "[0数据] (MECH 现行模型 2.5400)",
   "target_text": "2.5400 (沿用现行模型档; 若 boss 定 4.0000 档则 D-2 改 4.0000 且 D-4 开口 Y 改 5.8000)",
   "owner": "boss (OI-11)",
   "source": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1; MECH/service_port_check.py L126-L127",
   "evidence": "[0数据]"
  },
  {
   "id": "D-6", "ref": "J_DEBUG", "name": "座体选型 / keepout",
   "current_value": 5.08, "target_value": 5.08,
   "current_text": "[0数据] 无厂商 keepout 图纸; 官方 1x4 THT 座体本体 F.Fab X 5.0800 x 2.1000",
   "target_text": "5.0800 (座体本体 <= 5.0800 x 2.1000; 占位清空区按 D-1/D-2 开 6.6100 x 2.8000, 每边比座体本体多让 0.7650)",
   "owner": "座体选型 + 开模 (结构件侧)",
   "source": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L139; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §5",
   "evidence": "[实测]+[0数据]"
  },
  {
   "id": "D-7", "ref": "J_DEBUG", "name": "板侧铜箔落点 (居中解)",
   "current_value": 1.775, "target_value": 4.81,
   "current_text": "1.7750 (铜箔 X 142.0625..143.8375 x Y 56.1500..57.0500, 中心 (142.9500, 56.6000))",
   "target_text": "4.8100 (X 140.5450..145.3550 x Y 56.1000..57.1000, 中心锁 (142.9500, 56.6000); X 允许偏心 +-0.4475, Y 允许偏心 0.0000)",
   "owner": "板侧封装原点 (main)",
   "source": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L61; MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L98; MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §2.1",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "D-8", "ref": "J_DEBUG", "name": "板侧铜箔 (换不换)",
   "current_value": 1.775, "target_value": 4.81,
   "current_text": "自绘 SMD 占位 pitch 0.50, 4 脚, 铜箔 1.7750 x 0.9000",
   "target_text": "4.8100 (官方 P1.27 THT land, 铜箔 4.8100 x 1.0000)",
   "owner": "板侧铜箔 (main, B33_PIN_LAND_1P27)",
   "source": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63; MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L105",
   "evidence": "[实测]"
  },
  {
   "id": "U-1", "ref": "J_UART", "name": "座体必须清空区 X 宽",
   "current_value": 2.54, "target_value": 4.07,
   "current_text": "2.5400 (X 17.620..20.160, 中心 18.8900)",
   "target_text": "4.0700 (中心随落点: C1 17.9650 => X 15.9300..20.0000; C2 19.0350 => X 17.0000..21.0700; C3 18.9350 => X 16.9000..20.9700)",
   "owner": "清空区 (结构件内腔)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §2.1; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "U-2", "ref": "J_UART", "name": "座体必须清空区 Y 宽",
   "current_value": 2.54, "target_value": 2.8,
   "current_text": "2.5400 (Y 67.330..69.870, 中心 68.6000)",
   "target_text": "2.8000 (落点 C1/C3 => Y 67.2000..70.0000; 落点 C2 中心 68.4000 => Y 67.0000..69.8000 但开口装不下, 见 U-4)",
   "owner": "清空区 (结构件内腔)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L196; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §1; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "U-3", "ref": "J_UART", "name": "罩开口 X 宽与位置",
   "current_value": 10.2, "target_value": 10.2,
   "current_text": "10.2000 (X 13.790..23.990, 中心 18.8900)",
   "target_text": "10.2000 (X 13.790..23.990, 一字不动; 三候选开口 X 最坏余量 1.8400 >= CRIT)",
   "owner": "开口 (不改)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §1; §2",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "U-4", "ref": "J_UART", "name": "罩开口 Y 宽与位置 (分落点)",
   "current_value": 4.6, "target_value": 4.6,
   "current_text": "4.6000 (Y 66.300..70.900, 中心 68.6000)",
   "target_text": "4.6000 (落点 C1/C3 => Y 66.300..70.900 不动; 落点 C2 => 开口 Y 必须含 66.1000..70.7000, 即下移 0.2000 或宽放大到 5.0000)",
   "owner": "开口 (结构件侧; 选 C2 还是 C1/C3 归 main 的 OI-3)",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347; HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §0; §2",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "U-5", "ref": "J_UART", "name": "座体在罩内的平移量",
   "current_value": 18.89, "target_value": 18.935,
   "current_text": "现状清空区中心 X 18.8900",
   "target_text": "18.9350 (C1 17.9650 移 -0.9250; C2 19.0350 移 +0.1450; C3 18.9350 移 +0.0450)",
   "owner": "结构件侧 (落点归 main, OI-3)",
   "source": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §2.1; HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3",
   "evidence": "[推算]"
  },
  {
   "id": "U-6", "ref": "J_UART", "name": "座体真实高 h",
   "current_value": null, "target_value": 2.54,
   "current_text": "[0数据] (MECH 现行模型 2.5400)",
   "target_text": "2.5400 (沿用现行模型档, 与 D-5 同档同口径)",
   "owner": "boss (OI-11)",
   "source": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1; MECH/service_port_check.py L126-L127",
   "evidence": "[0数据]"
  },
  {
   "id": "U-7", "ref": "J_UART", "name": "座体选型 / keepout",
   "current_value": 2.64, "target_value": 2.64,
   "current_text": "[0数据] 无厂商 keepout 图纸; 官方 1x2 THT 座体本体 F.Fab 2.6400 x 2.2000",
   "target_text": "2.6400 (座体本体 <= 2.6400 x 2.2000; 占位清空区按 U-1/U-2 开 4.0700 x 2.8000, 每边比座体本体多让 0.7150)",
   "owner": "座体选型 + 开模 (结构件侧)",
   "source": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L118; MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §5",
   "evidence": "[实测]+[0数据]"
  },
  {
   "id": "U-8", "ref": "J_UART", "name": "板侧铜箔 (换不换)",
   "current_value": 0.775, "target_value": 2.27,
   "current_text": "自绘 SMD 占位 pitch 0.50, 2 脚, 铜箔 0.7750 x 0.9000",
   "target_text": "2.2700 (官方 P1x2 THT land, 铜箔 2.2700 x 1.0000; 若 OI-2 判不含则本行不执行, U-1~U-5 全部不执行)",
   "owner": "板侧铜箔 (main, OI-2)",
   "source": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63; MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L32",
   "evidence": "[实测]"
  },
  {
   "id": "U-9", "ref": "J_UART", "name": "落点的 Y 向可行域 (本单新算)",
   "current_value": 1.8, "target_value": 1.8,
   "current_text": "ISS-386 §2.1 只给了 X 向需求 4.0700, 未校 Y 向清空区放不放得进开口; 本单实算: 铜箔相对罩开口每边内缩必须 >= 1.8000",
   "target_text": "1.8000 (铜箔相对罩开口每边内缩量必须 >= 1.8000; C1/C3 允许中心偏心 0.0000, C2 内缩 1.6000 差 0.2000 不可行, X 向三候选全可行)",
   "owner": "板侧落点 (main, OI-3)",
   "source": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md §3.1; HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3; MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347",
   "evidence": "[实测]+[推算]"
  }
 ],
 "oi_answers": [
  {
   "id": "OI-2",
   "question": "B33_PIN_LAND_1P27 的范围含不含 J_UART",
   "decision_owner": "main",
   "decision": "not_decided_here",
   "structural_answer": "含 => J_UART 结构件同批返工 (清空区 2.5400x2.5400 -> 4.0700x2.8000, 中心随落点移 -0.9250/+0.1450/+0.0450), 且落点 C2 需同时改开口 Y (U-4); 不含 => J_UART 结构件零返工 (清空区保持 2.5400x2.5400), 但 J_UART 换不成官方 land, BOM/网表写的 1.27mm 实物排针仍落不进 0.50mm pitch 自绘占位 land (Delta pitch 0.77) => 结构件零返工 != 实物装配问题解决",
   "source": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md L63; MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346",
   "evidence": "[推算]+[实测]"
  },
  {
   "id": "OI-12",
   "question": "⑤ 罩住判据对 THT 排针是不是过严",
   "decision_owner": "main+boss",
   "decision": "not_decided_here",
   "structural_answer": "硬差额: 判据要求每边 0.9000, 官方 land courtyard 只给每边 0.6400 (J_DEBUG F.CrtYd 6.0900 vs 铜箔 4.8100; J_UART 退包络 3.5500 vs 铜箔 2.2700) => 每边差 0.2600, 清空区 X 总宽差 0.5200 (6.6100-6.0900 / 4.0700-3.5500). 路 A 判据不动 => 清空区 X 6.6100/4.0700, 每边比座体本体多让 0.7650/0.7150, 不改任何既有判据页, 代价是镜脚内腔变大+罩外观缝变大+工装按内腔走. 路 B 判据改名义余量口径 => 清空区 X 6.0100/3.4700, J_DEBUG 的 6.0100 比 courtyard 6.0900 还小 0.0800 反常消失, 代价是 FDM ±0.3000 公差不再扣除 (实际余量只剩 0.3000) 且本页 §1~§4 全部余量要重算, 且 J_UART 的 3.4700 正好等于 ISS-377 DP-1 那个数 (OI-14 同时消掉)",
   "source": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L140; HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md L63; MECH/service_port_check.py L126-L127",
   "evidence": "[推算]+[实测]"
  },
  {
   "id": "OI-13",
   "question": "Y 向零制造余量接受吗 (还是开口 Y 一起放大)",
   "decision_owner": "main+boss",
   "decision": "not_decided_here",
   "structural_answer": "硬事实: 罩开口 Y 4.6000 只容清空区 Y 2.8000 => 每边 0.9000 => 最坏 0.6000 = CRIT 恰好, 零余量. 更硬一条 (本单新算): Y 向铜箔中心允许偏心 = 0.0000 (铜箔相对开口每边内缩必须 >= 2 x 0.9000 = 1.8000, 而 J_DEBUG 与落点 C1/C3 的内缩恰好 1.8000) => 铜箔中心偏 1um 就装不下; 落点 C2 内缩 1.6000 差 0.2000 不可行. 路 A 接受零余量 => 开口零改动, 代价是偏心容差 0.0000 + 装配全靠人工对位. 路 B 开口 Y 放大 => 4.6000+2*Delta (Delta=0.5000 => 5.6000, 最坏 1.1000; Delta=0.6000 => 5.8000, 最坏 1.2000), 代价是罩外观缝/防水防尘/镜脚壁厚同批重做, 两件同批. 若 boss 定 h=4.0000 档 => 开口 Y 必需 5.8000, 一次改动同时解掉 OI-13 与落点 C2 的死结",
   "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347; MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352; MECH/service_port_check.py L126-L127",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "OI-14",
   "question": "ISS-377 §3.2 DP-1 的 3.4700 订正为 4.0700 吗",
   "decision_owner": "main",
   "decision": "not_decided_here",
   "structural_answer": "结构侧技术面自答: 现行判据链下 3.4700 不够, 差 0.6000. 3.4700 = 2.2700 + 2 x CRIT(0.6000) 是名义余量口径 => 最坏 0.6000 - 0.3000 = 0.3000 < CRIT 0.6000 => 不过阈; 全链口径需 2.2700 + 2 x (CRIT+TOL) = 4.0700 => 恰好过阈. 所以改件要求单必须按 4.0700 写 (本页 U-1 就是). 留给 main 的只剩: 订正块要不要往 ISS-377 老页落 (老页已签收, 本单零改). 注意与 OI-12 耦合: 若走 OI-12 路 B (名义余量口径) 则 3.4700 反而是对的 => 两条必须一起拍",
   "source": "MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md L166; MECH/service_port_check.py L126-L127",
   "evidence": "[推算]+[实测]"
  }
 ],
 "gate_chain_impact": [
  {"gate": "MECH/check_debug_seat_3d_fit.py", "rc": 1, "verdict": "红", "reason": "K3.3 页内 housing/opening 与真相页不一致 x4; K3.4/K3.5 三候选余量与实算不符", "need": "ISS-386 页机器块用 --emit 重出"},
  {"gate": "MECH/check_juart_1p27_clearance.py", "rc": 1, "verdict": "红", "reason": "J1/J2 页内余量与按真相页实读座体宽重算不符; J5 两件同向校验挂", "need": "ISS-374 页余量列重算"},
  {"gate": "MECH/check_connector_clearance_caliber.py", "rc": 1, "verdict": "红(基线就红)", "reason": "新增 K0 页内座体清空区与真相页不一致; K7 不通过文件由 2 个变 3 个 (新增真相页 md5)", "need": "ISS-377 页 §1 表同步 + 基线由 main 重签"},
  {"gate": "MECH/check_jdebug_1p27_clearance.py", "rc": 0, "verdict": "绿", "reason": "开口 X 取自 STRUCT_CROSSCHECK 页, 不吃真相页清空区", "need": "不动"},
  {"gate": "MECH/check_jdebug_arrangement_truth.py", "rc": 0, "verdict": "绿", "reason": "不依赖真相页清空区", "need": "不动"},
  {"gate": "MECH/check_onepass_mech_sync.py", "rc": 0, "verdict": "绿", "reason": "不读真相页", "need": "不动"},
  {"gate": "MECH/check_onepass_struct_crosscheck.py", "rc": 0, "verdict": "绿", "reason": "不吃真相页清空区", "need": "不动"},
  {"gate": "MECH/check_onepass_mech_release.py", "rc": 0, "verdict": "绿", "reason": "不依赖座体清空区", "need": "不动"},
  {"gate": "MECH/check_onepass_s10_led_spec_sync.py", "rc": 0, "verdict": "绿", "reason": "不影响 LED 规格同步", "need": "不动"},
  {"gate": "MECH/check_board_frame_coords.py", "rc": 0, "verdict": "绿", "reason": "板框问题不受结构件清空区影响", "need": "不动"}
 ],
 "decisions": {
  "clearance_x_tier_decision": "not_decided_here",
  "landing_point_decision": "not_decided_here",
  "seat_height_decision": "not_decided_here",
  "b33_scope_decision": "not_decided_here",
  "cover_criterion_decision": "not_decided_here",
  "y_zero_margin_decision": "not_decided_here",
  "dp1_correction_decision": "not_decided_here"
 },
 "open_items": {
  "OI-5": "J_DEBUG 的必须清空区 X 宽以 1.7750 / 4.0850 / 4.8100 哪个为准 归 main (目标值三档同 = 6.6100, 只改返工幅度)",
  "OI-3": "J_UART 落点三选一 归 main (本单新算: C2 的 Y 向差 0.2000 不可行)",
  "OI-2": "B33_PIN_LAND_1P27 含不含 J_UART 归 main (结构侧两条腿代价已算死)",
  "OI-11": "座体真实高 h = [0数据] 归 boss (X 向判决与 h 无关)",
  "OI-12": "⑤ 罩住判据对 THT 排针是否过严 (差 0.5200) 归 main + boss",
  "OI-13": "Y 向零制造余量接受吗 (偏心容差 0.0000) 归 main + boss",
  "OI-14": "ISS-377 DP-1 的 3.4700 订正为 4.0700 归 main (与 OI-12 必须一起拍)"
 },
 "degrade_plans": [
  {"id": "DP-1", "text": "按最坏值设计: J_DEBUG 清空区 X 取 6.6100; 返工幅度按 OI-5 三档分别是 +4.8350 / +2.5250 / +1.8000", "affects": "J_DEBUG"},
  {"id": "DP-2", "text": "按最坏值设计: J_UART 清空区 X 取 4.0700, 中心随落点; C2 需同时按 U-4 改开口 Y", "affects": "J_UART"},
  {"id": "DP-3", "text": "落点避开 C2: 选 C1 或 C3 则罩开口 Y 4.6000 一字不动 (C3 板侧余量 0.0447 最薄)", "affects": "J_UART"},
  {"id": "DP-4", "text": "改设计路径绕开 Y 向: 罩开口 Y 一并放大到 5.6000 (Delta=0.5000) 或 5.8000 (Delta=0.6000)", "affects": "J_DEBUG + J_UART"},
  {"id": "DP-5", "text": "实测样件兜底: 座体真实高 h 与型号 [0数据] => 按 Z 向保守上界出件, 装配前用 1 台样件实测占位与净距", "affects": "J_DEBUG + J_UART"},
  {"id": "DP-6", "text": "判据兜底: OI-12 未裁时结构件按 6.6100 开 (清空区是多挖一点不是少挖一点, 后道可修)", "affects": "J_DEBUG"}
 ],
 "evidence_whitelist": ["[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"]
}
```

<!-- MECH-DEBUG-SEAT-REWORK-SPEC-JSON-END -->

---

## ★§9 边界自证 (★逐条★)★

| ★边界★ | ★自证★ |
|---|---|
| ★零写板★ | 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 三项开工前后逐字相同 (★交卷页 B6 有前后对比★) ★ |
| ★零落表★ | 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` 三项开工前后逐字相同 ★ |
| ★零改既有闸 / 既有页面正文★ | 本单只新建本页 + 一个新闸 + 一页交卷页 ; ★沙盒预演改的是 `tmp/iss389_sbx/probe/` 里的副本, 真件 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 一个字节未动 ★ |
| ★零挂链★ | `grep -c check_debug_seat_rework_spec state/gate_check.py` = `0` ★ |
| ★零外发★ | 本单零对外沟通 ; 所有 `[0数据]` 处均给降级方案 (`DP-1`~`DP-6`) ★ |
| ★不代拍★ | `OI-5`/`OI-3`/`OI-2`/`OI-11`/`OI-12`/`OI-13`/`OI-14` 全部只登记 + 给代价 ; ★机器块 `decisions.*` 七项全是 `not_decided_here` ★ |
| ★不自签台账★ | `state/issue_log.yaml` 一个字节未动 (★签收归 main★) ★ |
| ★没写别人的分片★ | 只写 `state/fragments/mech.yaml` (★走 `state/frag_write.py`★) ★ |
| ★证据分级★ | 每条结论标五级之一 ★ |
