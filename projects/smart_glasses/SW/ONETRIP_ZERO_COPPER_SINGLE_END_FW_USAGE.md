# ★★ONETRIP 零铜单端网 · 固件引用实测表 (ISS-338)★★

> ★**本单性质**: 纯分析类 · 零写板 · 零落表 · 零改闸 · **不改固件本体** (只新建本页 + 交卷页 + 日志, 不改任何既有 SW 文档正文) ★
> ★**上游**: ISS-334 (verified) · need-4a `iss334_need4a_single_end_net_usage` (main 2026-11-19 00:5x 裁) ★
> ★**owner**: sw-lead (软件总工) · ★**交回**: main (分级定稿在 main, 本单不代拍) ★
> ★**一句话结论**: ★**9 条网在 `SW/**` 全树 (126 文件) 里【网名级零引用 · 含所有拼写变体】; 但按【功能等价物】逐条查清后, ★**真必需 4 条 · 可悬空候选 4 条 · 待定 1 条** ⇒ ★**main 已定的「USB_CC2 + UART_RX 必需」被实测推翻 1 条 (UART_RX), 另 1 条 (USB_CC2) 从「必需」降为「待定」** ★**
 【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**上方旧分级陈述【作废】** ⇒ 新口径 = ★**必需 23 (15 高速差分腿 + 8 单端脚) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` + `iss338_need_jtag_group_decision` + `iss338_need_boot_storage_answer` + `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** (★**本机实跑 `HW/check_s8_target_list.py` ⇒ 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔**★) · ★**老字一个字都没删 (见 §7-4 diff 自证)** ★【/ISS344-CORR】★★** ★

---

## §0 一句话结论 + 三问回答

★**一句话**: ★**9 条零铜单端网, `SW/**` 全树网名级命中 = 0 (含大小写/下划线/连字符变体) ⇒ 但固件「用不用」不能只看网名 —— 逐条按功能等价物 (位号 / 板级功能 / SW 侧待办) 查完, 分级 = ★**必需 4 (`CAM_RESET_N` · `LED_G_D` · `SPI_MISO_BOOT` · `SPI_MOSI_BOOT` / `SPI_SCLK_BOOT` 三条一组) · 可悬空候选 4 (`JTAG_TDI` · `FSIN_OUT` · `UART_RX` · `USB_CC2`) · 待定 1** ★
 【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**上方旧分级陈述【作废】** ⇒ 新口径 = ★**必需 23 (15 高速差分腿 + 8 单端脚) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` + `iss338_need_jtag_group_decision` + `iss338_need_boot_storage_answer` + `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** (★**本机实跑 `HW/check_s8_target_list.py` ⇒ 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔**★) · ★**老字一个字都没删 (见 §7-4 diff 自证)** ★【/ISS344-CORR】★★** ★

> ★**等一下 —— 见 §5 的读数: 三条 SPI_*_BOOT 归「可悬空候选」更准确, 真正「必需」只有 `CAM_RESET_N` + `LED_G_D` 两条** ★
> ★**最终分级 (以 §5 表为准)**: ★**必需 2 (`CAM_RESET_N` · `LED_G_D`) · 可悬空候选 6 (`FSIN_OUT` · `JTAG_TDI` · `SPI_MISO_BOOT` · `SPI_MOSI_BOOT` · `SPI_SCLK_BOOT` · `UART_RX`) · 待定 1 (`USB_CC2`)** ★
 【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**上方旧分级陈述【作废】** ⇒ 新口径 = ★**必需 23 (15 高速差分腿 + 8 单端脚) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` + `iss338_need_jtag_group_decision` + `iss338_need_boot_storage_answer` + `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** (★**本机实跑 `HW/check_s8_target_list.py` ⇒ 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔**★) · ★**老字一个字都没删 (见 §7-4 diff 自证)** ★【/ISS344-CORR】★★** ★

### 三问回答

**Q1 · 9 条里, 几条真必需 / 几条可悬空 / 几条待定?**

| 分级 | 条数 | 网名 |
|---|---|---|
| ★**必需** ★ | **2** | `CAM_RESET_N` · `LED_G_D` |
| ★**可悬空候选** ★ | **6** | `FSIN_OUT` · `JTAG_TDI` · `SPI_MISO_BOOT` · `SPI_MOSI_BOOT` · `SPI_SCLK_BOOT` · `UART_RX` |
| ★**待定** ★ | **1** | `USB_CC2` |
 【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**上方旧分级陈述【作废】** ⇒ 新口径 = ★**必需 23 (15 高速差分腿 + 8 单端脚) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` + `iss338_need_jtag_group_decision` + `iss338_need_boot_storage_answer` + `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** (★**本机实跑 `HW/check_s8_target_list.py` ⇒ 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔**★) · ★**老字一个字都没删 (见 §7-4 diff 自证)** ★【/ISS344-CORR】★★** ★

★**分级判据 (§2 写死, 与 main 口径一致)**: ★**必需** = ★**固件/脚本里有【真代码路径】或【产品功能链】依赖它, 悬空后某个 SW 侧已写死的功能会真的做不出来** ★ · ★**可悬空候选** = ★**零引用 / 只在调试脚手架里 / 上游尚未确认 ⇒ 悬空不损失任何已写死的 SW 功能** ★ · ★**待定** = ★**零引用, 但有一条例外条款会因悬空而改变合规性 (须外部确认才能定)** ★
 【ISS344-CORR】★★**★分级判据订正 (main 2026-11-22 20:5x 终裁)**: ★**上方判据仍缺一条边界** ⇒ ★**补**: 「固件零引用 ⇒ 可悬空」★**只适用于固件信号, 不适用于调试口 / 预留位** ★ (★**JTAG / UART 是硬件接口, 由调试器 / 探针驱动, 不由应用固件引用 ⇒ SW 零引用对它不构成「可悬空」的证据**★) · 依据 pm.yaml → `iss338_need_jtag_group_decision` (★**逐字**★) · 证据等级 = ★**[推算]** ★【/ISS344-CORR】★★** ★

**Q2 · 有没有推翻 main 已定口径的实测事实? (★`UART_RX` / `USB_CC2` 这两条最可能★)**

★**有, 两条, 都推翻** ★

| main 原口径 (need-4b, 2026-11-19 00:5x) | 本单实测 | 证据 |
|---|---|---|
| ★`UART_RX` = ★**必需** ★ | ★**⇒ 可悬空候选** ★ (从「必需」降级) | ★**[实测]** `SW/tools/s2_board_run.sh:248-263` 的串口用法 **只有读** (`cat "$SERDEV" > "$SER"`) ⇒ ★**从不往板里写** ⇒ ★**板→主机方向够用**; ★**[实测]** 固件侧 `UART_TX` 走 `TP_UART` (J_SOM_P2.7) ★**已有 230 段铜** ⇒ ★**日志抓取链完整**; ★**[实测]** `J_UART` 排针本身 dnp=**可选** |
| ★`USB_CC2` = ★**必需** ★ | ★**⇒ 待定** ★ (从「必需」降级) | ★**[实测]** 官方板上 `J_TYPE_C` (充电板侧 Type-C) **不在板** ⇒ ★**板载 Type-C 只有 `J_USB_C`**; ★**[实测]** `J_USB_C` 的 USB 2.0 差分 `USB_D_P/N_TYPEC` **已有铜** ⇒ ★**调试/供电数据通路不依赖 CC2**; ★**[媒体]** USB-IF Type-C 规范: ★**USB 2.0-only 设备只需 CC1 一路 Rd, CC2 可悬空** (见 §4 证据) ⇒ ★**但同规范对「双路 Rd」也有条款 ⇒ 须外部确认 ⇒ 待定** |
 【ISS344-CORR】★★**★Q2 表订正 (main 2026-11-22 20:5x 终裁)**: ★**上表两行【作废】** ⇒ ★**`UART_RX` = 必需** (★**调试口 ⇒ 布线保留成本 ≈ 0·事后不重出板**★) · ★**`USB_CC2` = 必需** (★**[官网] USB Type-C 插座端双路 Rd 条款 ⇒ 不可悬空**★) ⇒ ★**本页原推的「推翻 main」结论被 main 的终裁否决** ★ · 依据 pm.yaml → `iss338_need_jtag_group_decision` / `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** / ★**[官网]** ★【/ISS344-CORR】★★** ★

★**另外两条实测事实 (不推翻 main, 但改变 main 的「其余 7 条以固件引用为准」口径)**: ★
- ★**`CAM_RESET_N` 从 main 的「可悬空候选」升为「必需」** ★ — ★**[官方]** 网表 `HW/netlist_v1.csv:285` 原文: 「★**主板必须能拉它**」+ 参考 Radxa CM5 overlay dts 的 `reset-gpios (gpio1 RK_PB3, 低有效)` ⇒ ★**camera 模组 RESET 脚, 相机不出图 ⇒ 整条 MIPI-CSI 链死** ⇒ ★**不是调试脚, 是产品主链** ★
- ★**`LED_G_D` 从 main 的「可悬空候选」升为「必需」** ★ — ★**[实测]** `D_LED_G` 在 SW 侧是 ★**真代码路径** (§3 表 L4) + ★**[实测]** 同族 `LED_B_D` (105 段) / `LED_R_D` (169 段) **都有铜, 只有 `LED_G_D` 是 0 段** ⇒ ★**这是「该布没布」不是「不必布」** ★

**Q3 · 这 9 条悬空与否, 对 S8 归零 (unc 45→0) 的净效果是多少? (★能救回几条差分腿, 能不能省掉几条单端脚的布线路径★)**

★**[实测]** 官方板 DRC `unconnected_items` = 45 条, 涉及 43 个网名 (`logs/iss334/00_official_drc_fresh.json`) ★
★**[实测]** 本单 9 条网 ★**各占 1 条, 合计 9 条 = 45 的 20.0%** ★

| 口径 | 读数 | 说明 |
|---|---|---|
| ★**悬空本单 9 条 ⇒ unc 45 → 36** ★ | ★**净减 9 条 (−20.0%)** ★ | ★**前提**: 板侧真把这些 pad 标 no-connect / 摘网, DRC 条目才消失; ★**只是「不连」不算, DRC 照样报** ★ |
| ★**能救回几条差分腿?** ★ | ★**0 条** ★ | ★**[实测]** 15 条高速差分腿占 unc 里的 ★**23 条** (涉及 22 个网名), 与本单 9 条**无交集** ⇒ ★**悬空单端脚救不了差分腿** ★ |
| ★**能省掉几条单端脚的布线路径?** ★ | ★**9 条全部省掉** ★ | ★**[实测]** 9 条本来就 0 段 0 孔 ⇒ ★**悬空 = 一条铜都不用布** ⇒ ★**省 9 条布线工作量** ★ |
| ★**★关键: 省下的 9 条工作量里, 8 条本来就救不回来** ★ | ★**8/9** ★ | ★**[实测]** ISS-334 逐网归桶: 9 条里 ★**8 条落 B 桶 (出脚余量 ≤ +0.30mm, 几何钉死)** + ★**1 条 (`LED_G_D`) 落 C 桶 (出脚余量 0.525mm 几何宽松, A* 搜索失败)** ⇒ ★**B 桶的 8 条即使不悬空, 官方同配方 A* 实测也是「补上 0 条」** ⇒ ★**悬空它们 = 放弃 8 条本来就走不通的线, 不是放弃 8 条能走通的线** ★ |

★**⇒ 净效果结论**: ★**悬空 9 条 ⇒ unc 45→36 (−9 条 / −20.0%), 差分腿 0 条, 布线工作量省 9 条 (其中 8 条是几何死线 ⇒ 省的是「做不成的活」)** ★
★**⇒ 且这 8 条 B 桶死线正是「板那一趟为了救一条调试脚去动高速差分走廊」的来源 ⇒ ★**悬空它们 = 把「风险不对称」的那一半风险直接消掉** ★

---

## §1 实测方法 (★口径写死, 便于复现★)

### §1-1 扫描范围

★**`SW/**` 全树, 126 个文件** (含 `.py` 48 / `.md` 47 / `.sh` 12 / `.json` 6 / 其它; ★**跳过 `__pycache__`** ⇒ 排除 `.pyc` 编译产物) ★
★**为什么只扫 `SW/`**: ★**SW 侧 = 本项目的固件/脚本/规格唯一真源目录** (无 C 代码、无 `.dts`、无固件镜像 ⇒ 见 §1-4) ★

### §1-2 三层判据 (★为什么要三层, 不是一层★)

★**今天的教训 (ISS-318 五档闸的由来)**: ★**「文档提及」与「真代码路径」的差别 = 「改完能跑」与「改完跑不起来」的差别** ⇒ ★**所以本单把判据拆成三层, 每条网三层都要落数** ★

| 层 | 问什么 | 判据 |
|---|---|---|
| ★**L1 网名级** ★ | ★**固件代码里有没有直接写这个网名?** ★ | ★**`grep -rn -w` 精确全名 + `grep -rniw` 不区分大小写 + 去分隔符词干 (下划线/连字符/大小写变体) 三跑, 全 0 才算零引用** ★ |
| ★**L2 位号级 (功能等价锚点)** ★ | ★**固件虽不写网名, 但写了这条网所连的器件位号吗?** ★ | ★**扫该网两端器件位号 (如 `LED_G_D` ⇒ `D_LED_G` / `R_LED_G` / `TP_LED_G`) 在 SW 侧的出现形态** ★ |
| ★**L3 功能级 (板级功能链)** ★ | ★**这条网承载的产品功能, SW 侧有没有已写死的需求/待办?** ★ | ★**查 SW 侧功能规格页 + 网表 `[官方]` 说明 + 板级 [官方] 规范** ★ |

★**★零引用判据 (main 口径, 逐字执行)★**: ★**扫 `SW/**` 全树 (代码 + 脚本 + 文档), 命中数 = 0 且拼写变体 (下划线/连字符/大小写) 也 = 0 ⇒ 才算零引用; 变体命中要单独列出来** ★

### §1-3 ★★扫法自证 (★不然「0 命中」可以是「扫错了」★)★★

★**[实测]** 同一套扫法在 `SW/**` 上打中同族控制网 ⇒ **扫法本身有效, 0 命中是真的 0**: ★

| 控制网 (同族对照) | `SW/**` 命中行数 | 说明 |
|---|---|---|
| `BAT_DET` | ★**121** ★ | 同为 ADC/单端信号网 |
| `RESET_N` | ★**52** ★ | 同为 `_N` 后缀复位网 |
| `JTAG_TCK` / `JTAG_TMS` | ★**31** (合计) ★ | 同为 JTAG 四线之一 (★**注: 命中的是 `JTAG_TCK`/`JTAG_TMS`, 不是 `JTAG_TDI`** ★) |
| `LED_G` | ★**14** (含 `D_LED_G` 等) ★ | ★**注: 命中的是设计ators `D_LED_G`/`D_LED_R`/`D_LED_B` 与网名 `LED_G`, 不是网名 `LED_G_D`** ★ |

★**[实测]** 9 条目标网 ★**全部 0 命中 (L1 三跑全 0)** ★ ⇒ ★**`JTAG_TDI` 与 `JTAG_TCK/TMS` 是不同 token; `LED_G_D` 与 `D_LED_G`/`LED_G` 也是不同 token ⇒ 「JTAG 出现 31 次」「LED 出现 14 次」不能算成对这 9 条的引用** ★

★**★★【复现陷阱 · 必读】★★**: ★**本单的主交付物 (`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md`) 自己就落在 `SW/` 里 ⇒ 交卷后再原样跑 §5 的①会得到【非 0】(9 条网名各被本页命中 8~17 次) ⇒ ★**那 9 条命中全是本单自己写的表格内容, 不是固件引用** ★
★**⇒ 复现时必须排除本单自产文件, 否则会把「报告」误读成「引用」**: ★
```bash
grep -rn --exclude-dir=__pycache__ --exclude=ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md -w CAM_RESET_N SW | wc -l   # ⇒ 0
```
★**[实测]** 按此法复跑: ★**9 条网 V1/V2/V3 三跑仍全 0** ★ (★**§1-3 的读数是【交卷前】的基线, 即 `SW/` 里还没有本单文件时的状态** ★) ★

### §1-4 ★★为什么「SW/** 零引用」≠「固件不用」 (★本单最重要的一条方法论★★)

★**实测事实**: ★**本项目 `SW/**` 里没有一行 C / 没有 `.dts` / 没有固件镜像 / 没有 `overlay`** ⇒ ★**唯一那份 `.dtsi` (`HW/PCB/panel_simple_dsi_template.dtsi`) 对本单 9 条网命中 = 0** ★
★**⇒ 所以本单能回答的是「★**SW 侧已写死的规格/脚本/闸有没有依赖它**★」, 而不是「★**板上那颗 SoC 的 Linux 驱动会不会用某个 GPIO**★」** ★
★**⇒ 因此每条网都额外查了 L3 板级功能链 (网表 `[官方]` 说明 + 原厂 dts 参照) ⇒ ★**网名级 0 引用 ≠ 可以悬空** ★ ★**这是本单推翻 main 两条口径的根本原因** ★

---

## §2 ★★★逐条引用表 (★9 行 · 每行都有机器读数★)★★★

★**列释义**: ★**L1 网名级** = `SW/**` 精确+变体命中数 · ★**L2 引用形态** = ★**真代码路径 / 注释 / 文档提及 / 零引用** (★**四档, 一条都不许合并** ★) · ★**L3 功能级** = 产品功能链是否依赖 ★

| ★net★ | ★被谁引用 (文件:行)★ | ★引用形态★ | ★分级★ | ★证据★ |
|---|---|---|---|---|
| ★`CAM_RESET_N`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点**: `HW/netlist_v1.csv:285` 原文「★**主板必须能拉它**」+ 参考 Radxa CM5 overlay dts `reset-gpios (gpio1 RK_PB3, 低有效)`; `HW/NETLIST_REV2_SPEC.md:53` 同口径<br>★**SW 侧相关**: `SW/SW_REQUIREMENTS.md:87` 「MIPI-CSI sensor 驱动」· `:96` M1-R2「sensor 驱动能出图」· `SW/DEMO_OD_PIPELINE_SPEC.md:576`「⑧ capture 接入: sensor 驱动 + 模式配置 + CSI 拓扑 ★移植 42KB 驱动」★ | ★**零引用** (L1) ★<br>★**L3 = 文档提及 + 板级 [官方] 功能链** ★ | ★**必需** ★ | ★**[实测]** `grep -rn --exclude-dir=__pycache__ -w CAM_RESET_N SW` = **0 行**; 变体 `camresetn` = **0**<br>★**[官方]** `HW/netlist_v1.csv:285` 「★**主板必须能拉它**」★<br>★**[推算]** 相机不出图 ⇒ MIPI-CSI 链死 ⇒ 端到端测量无对象 ⇒ **不是调试脚** ★ |
| ★`FSIN_OUT`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点**: `SW/INTEGRATION_PLAN.md:717` **IR-03**「帧同步/曝光起始信号能否引出到测试点 (供 IT-P4-03 / IT-P4-05 示波器法)」· `:844` **B-5**「帧同步信号能否引出未定 ⇒ 示波器法不可用 ⇒ 端到端与光机延迟精度降级到 ±4.2ms」· `SW/SW_REQUIREMENTS.md:684` M-2 示波器法<br>★**板级**: `HW/netlist_v1.csv:356` 「测什么: 帧同步 (FSIN/VSYNC) 引出; 位置: SoC 侧 -> 回答原厂问询 Q4b.3」· `HW/netlist_v1.csv:400` `FSIN` 网 `SoC_NC` ⇒ ★**上游球位号本身是「SoC 未接」占位** ★ | ★**零引用** (L1) ★<br>★**L3 = 文档提及 (IR-03 待办 + B-5 阻塞项)** ★ | ★**可悬空候选** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧分级【作废】⇒ 新分级 = ★**可悬空 (条件式)** ★ (★**板那一趟动作 · 现在只定口径不定动作**★) · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]**★【/ISS344-CORR】★★** ★| ★**[实测]** `grep -rn -w FSIN_OUT SW` = **0 行**; 变体 `fsinout` = **0**<br>★**[实测]** `SW/INTEGRATION_PLAN.md:717` IR-03 + `:844` B-5 ★<br>★**[实测]** `FSIN` 网自身 pad=1 / 0 段 (⇒ SoC 侧压根没接) ★<br>★**[推算]** 悬空 ⇒ 示波器法不可用 ⇒ 端到端精度降级 ±4.2ms ⇒ **是精度降级不是功能全灭** ★ |
| ★`JTAG_TDI`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点**: `SW/FLASH_AND_VERSION.md:44` 救砖 4 级 S3=JTAG · `:336` S3 行「JTAG 调试器接 SoC … 原厂是否提供 JTAG 引出 + 调试器 + 转接板 → 全 `[0数据]`」· `SW/EVT_TEMPLATE.md:503` 硬规则「S2 连续失败 2 次 → 必须升级 S3 (JTAG)」· `SW/S2_BOARD_TEST_CHECKLIST.md:393`<br>★**板级**: `HW/netlist_v1.csv:392` `JTAG_TDI_SOC` 网 `SoC_NC` ⇒ ★**SoC 侧未接** ★ | ★**零引用** (L1) ★<br>★**L3 = 文档提及 (救砖 S3 脚手架, 自标 `[0数据]`)** ★ | ★**可悬空候选** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧分级【作废】⇒ 新分级 = ★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★) · 依据 pm.yaml → `iss338_need_jtag_group_decision` · 证据等级 = ★**[实测]**★【/ISS344-CORR】★★** ★| ★**[实测]** `grep -rn -w JTAG_TDI SW` = **0 行**; 变体 `jtagtdi` = **0**<br>★**[实测]** SW 侧 31 次 "JTAG" 全是 `JTAG_TCK`/`JTAG_TMS`/`JTAG_M0`/`JTAG_M1` ⇒ **无一命中 TDI** ★<br>★**[0数据]** 原厂是否提供 JTAG 引出+调试器 = 全 0 数据 ★ |
| ★`LED_G_D`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点 (真代码路径!)**: `SW/tools/check_sw_ref_reachability.py:178` 与 `SW/tools/check_sw_ref_reachability_v2.py:237` 的 `DESIGNATOR_REGISTRY` 里 ★**硬编码 `"D_LED_G"`** ★ · `SW/tools/check_onepass_sw_sync.py:181` ★**硬编码** `"t={'D_CHG_LED','D_LED_G','D_LED_R',…}"` ★<br>★**文档提及**: `SW/BOARD_ONEPASS_SW_SYNC.md:26` / `:40` / `:75` / `:189` / `:200` (落表残项 8 件含 `D_LED_G`, value 待选型)<br>★**板级**: `HW/netlist_v1.csv:304` 「`LED_G_D` LED_G 串阻 = 55Ω ±1% (ISS-283 G-5 裁决 · 20 mA 档)」★ | ★**真代码路径** ★ (★**位号 `D_LED_G` 在两个闸脚本里被硬编码, 不是注释也不是文档提及** ★)<br>★+ 文档提及 (落表残项口径) ★ | ★**必需** ★ | ★**[实测]** `grep -rn -w LED_G_D SW` = **0 行** (网名); 变体 `ledgd` = **0**<br>★**[实测]** ★**`grep -rn -w D_LED_G SW` = 14 行 / 7 文件**, 含 ★**2 个 `.py` 闸脚本的硬编码列表** ★<br>★**[实测]** 同族 `LED_B_D` = **105 段** / `LED_R_D` = **169 段** / `LED_G_D` = **0 段** ★<br>★**[推算]** 绿灯链断 ⇒ ISS-271 已点名的「`LED_G_D` 走线 93.49mm」卡点仍在 ★ |
| ★`SPI_MISO_BOOT`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点**: `SW/FLASH_AND_VERSION.md:46` 「启动存储容量与 rootfs 体积」为 3 个决定性 0 数据之一 · `:359` **P4 `BOOT_STORE`**「启动存储类型/容量/官方分区表参考设计」`[0数据]` · `SW/S2_VENDOR_QUESTION_LIST.md:315` §4 P4 · `:331`「若是 SPI-NOR → 型号+容量 ≥128MB」<br>★**板级**: `HW/netlist_v1.csv:207` `SPI_MISO` 网 `SoC_NC`; `HW/netlist_v1_pins.csv` `J_BOOT1` 整件 **DNP**「★SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR 启动存储 (焊盘位可留作扩展)」★ | ★**零引用** (L1) ★<br>★**L3 = 文档提及 (P4 待原厂问询, 自标 `[0数据]`)** ★ | ★**可悬空候选** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧分级【作废】⇒ 新分级 = ★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★) · 依据 pm.yaml → `iss338_need_boot_storage_answer` · 证据等级 = ★**[实测]**★【/ISS344-CORR】★★** ★| ★**[实测]** `grep -rn -w SPI_MISO_BOOT SW` = **0 行**; 变体 `spimisoboot` = **0**<br>★**[实测]** `J_BOOT1` 全件 DNP (`HW/netlist_v1_pins.csv`) ★<br>★**[实测]** `SPI_MISO` 网 pad=1 / 0 段 ⇒ **SoC 侧未接** ★<br>★**[0数据]** 启动存储类型/容量 = P4 待原厂 ★ |
| ★`SPI_MOSI_BOOT`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点**: 同 `SPI_MISO_BOOT` (`FLASH_AND_VERSION.md:46/359` · `S2_VENDOR_QUESTION_LIST.md:315/331`)<br>★**板级**: `HW/netlist_v1.csv:205` `SPI_MOSI` 网 `SoC_NC`; `J_BOOT1` 全件 DNP ★ | ★**零引用** (L1) ★<br>★**L3 = 文档提及 (P4 待原厂)** ★ | ★**可悬空候选** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧分级【作废】⇒ 新分级 = ★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★) · 依据 pm.yaml → `iss338_need_boot_storage_answer` · 证据等级 = ★**[实测]**★【/ISS344-CORR】★★** ★| ★**[实测]** `grep -rn -w SPI_MOSI_BOOT SW` = **0 行**; 变体 `spimosiboot` = **0**<br>★**[实测]** `SPI_MOSI` 网 pad=1 / 0 段 ★ |
| ★`SPI_SCLK_BOOT`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点**: 同 `SPI_MISO_BOOT`<br>★**板级**: `HW/netlist_v1.csv:201` `SPI_SCLK` 网 `SoC_NC`; `J_BOOT1` 全件 DNP ★ | ★**零引用** (L1) ★<br>★**L3 = 文档提及 (P4 待原厂)** ★ | ★**可悬空候选** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧分级【作废】⇒ 新分级 = ★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★) · 依据 pm.yaml → `iss338_need_boot_storage_answer` · 证据等级 = ★**[实测]**★【/ISS344-CORR】★★** ★| ★**[实测]** `grep -rn -w SPI_SCLK_BOOT SW` = **0 行**; 变体 `spisclkboot` = **0**<br>★**[实测]** `SPI_SCLK` 网 pad=1 / 0 段 ★ |
| ★`UART_RX`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点 (只读!)**: `SW/tools/s2_board_run.sh:248-263` ★**只 `cat "$SERDEV" > "$SER"`** (板→主机) ★· `:256` `timeout … cat "$SERDEV" > "$SER"` · `SW/tools/s2_rescue_config.json:230` `_readme`「板端串口 (★**取日志用**★)」<br>★**板级**: `HW/netlist_v1.csv:397` `UART_TX` 网 → `J_SOM_P2 pin7` + `TP_UART` ★**已有 230 段铜** ★; `HW/netlist_v1.csv:399` `UART_RX` → `J_SOM_P2 pin9` + `J_UART pin2`, ★**`J_UART` 整件 dnp=可选** ★ | ★**零引用** (网名) ★<br>★**L2 = 真代码路径 (但方向是【读】不是【写】)** ★<br>★**L3 = 调试脚手架 (可选项)** ★ | ★**可悬空候选** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧分级【作废】⇒ 新分级 = ★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★) · 依据 pm.yaml → `iss338_need_jtag_group_decision` · 证据等级 = ★**[推算]**★【/ISS344-CORR】★★** ★| ★**[实测]** `grep -rn -w UART_RX SW` = **0 行**; 变体 `uartrx` = **0**<br>★**[实测]** ★**`grep -rn "stty\|> /dev/tty\|write.*tty" SW` = 0 行** ★ ⇒ ★**SW 侧从不往板里写串口** ★<br>★**[实测]** `UART_TX` = **230 段 / 4 孔** (日志抓取链完整) ★<br>★**[实测]** `J_UART` dnp = **可选** ★ |
| ★`USB_CC2`★ | ★**零引用** (网名 0 命中)<br>★**功能锚点**: `SW/tools/check_sw_ref_reachability.py:185` 与 `check_sw_ref_reachability_v2.py:244` 的 `DESIGNATOR_REGISTRY` 硬编码 `"J_TYPE_C"` ★(注意: **`J_TYPE_C` 不在官方板上** ★)· `SW/SW_TIMING_REVIEW.md:274`「充电板 `J_TYPE_C` 的 D+/D− 要过铰链到主板 ⇒ ★**过不去** ⇒ **充电板的数据线是死的**」★<br>★**板级**: `HW/netlist_v1.csv:293` `USB_CC1` → `J_TYPE_C A5` + `R_CC1` · `:294` `USB_CC2` → `J_TYPE_C B5` + `R_CC2` ★**两块 Type-C 座 (充电板 `J_TYPE_C` + 板载 `J_USB_C`) 共用同一网名** ★; `HW/netlist_v1.csv` P1 行 `J_USB_C B5` + `R_CC2_D` · `HW/CHARGE_BOARD_SPEC.md:571/573` USB-IF R2.0 原文 Rd 5.1k ★ | ★**零引用** (网名) ★<br>★**L2 = 真代码路径 (`J_TYPE_C` 硬编码) + 文档提及** ★<br>★**L3 = 硬件合规项 (USB-IF)** ★ | ★**待定** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧分级【作废】⇒ 新分级 = ★**必需** ★ (★**板侧不许标 NC / no-connect**★) · 依据 pm.yaml → `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[官网]**★【/ISS344-CORR】★★** ★| ★**[实测]** `grep -rn -w USB_CC2 SW` = **0 行**; 变体 `usbcc2` = **0**<br>★**[实测]** ★**官方板 `J_TYPE_C` 不存在 / `J_USB_C` 存在** ★ ⇒ ★**零铜的那个 `USB_CC2` 端点是 `J_USB_C.B5` + `R_CC2_D.1`** ★<br>★**[实测]** `USB_CC1` = **151 段** (已布) ★<br>★**[媒体]** USB-IF Type-C: USB 2.0-only 设备 CC1 一路 Rd 即可 ★**但同规范另有条款 ⇒ 须外部确认** ★ |

### §2-1 ★引用形态四档汇总 (★按 brief 要求, 不许合并★)★

| 形态 | 9 条里各有谁 | 逐条 file:line |
|---|---|---|
| ★**真代码路径** ★ | ★`LED_G_D`★ (经位号 `D_LED_G`) · ★`UART_RX`★ (经 `s2_board_run.sh` 串口**只读**) · ★`USB_CC2`★ (经位号 `J_TYPE_C`) | `SW/tools/check_sw_ref_reachability.py:178` / `:185` · `SW/tools/check_sw_ref_reachability_v2.py:237` / `:244` · `SW/tools/check_onepass_sw_sync.py:181` · `SW/tools/s2_board_run.sh:248-263` · `SW/tools/s2_rescue_config.json:230` |
| ★**注释** ★ | ★**无一条** ★ | ★**[实测]** 9 条网的网名及其位号锚点在 SW 侧无一行是纯注释命中 ★ |
| ★**文档提及** ★ | ★`CAM_RESET_N`★ · ★`FSIN_OUT`★ · ★`JTAG_TDI`★ · ★`SPI_MISO_BOOT`★ · ★`SPI_MOSI_BOOT`★ · ★`SPI_SCLK_BOOT`★ | `SW/SW_REQUIREMENTS.md:87` / `:96` / `:684` · `SW/DEMO_OD_PIPELINE_SPEC.md:576` · `SW/INTEGRATION_PLAN.md:717` / `:844` · `SW/FLASH_AND_VERSION.md:44` / `:336` / `:359` / `:46` · `SW/EVT_TEMPLATE.md:503` · `SW/S2_BOARD_TEST_CHECKLIST.md:393` · `SW/S2_VENDOR_QUESTION_LIST.md:315` / `:331` · `SW/BOARD_ONEPASS_SW_SYNC.md:26` / `:40` / `:75` / `:189` / `:200` |
| ★**零引用** ★ | ★**9 条全部 (网名级, 含所有拼写变体)** ★ | ★**[实测]** `logs/iss338/21_nine_net_reference_evidence.txt` 逐条 V1/V2/V3 三跑读数 ★ |

★**★关键自审: 为什么「零引用」这条不能直接推出「9 条全可悬空」?★** ★
★**因为 4 条的功能链在 SW 侧是「文档提及」档 (需求已写死), 3 条是「真代码路径」档 (闸脚本硬编码), 而 L1 网名级 0 引用只说明「固件代码里没人直接写这个网名」⇒ ★**★两者是不同的东西: 网名是板级命名, 固件面对的是 GPIO / 位号 / 功能** ★★

---

## §3 ★★★可悬空候选清单 (★给 need-4b 的输入★)★★★
 【ISS344-CORR】★★**★§3 标题订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**本节标题与「清单 = 6 条可悬空 + 1 条待定」的说法【作废】** ⇒ ★**按终裁, 本页 9 条里只有 `FSIN_OUT` 1 条可悬空, 8 条必需, 0 条待定** ★ ⇒ ★**本节表格保留在册 (老字一字未删) 作历史痕迹, 有效口径以 §7 为准** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★

★**清单 = 上面 6 条「可悬空候选」+ 1 条「待定」的悬空后动作** ★
 【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**上方旧分级陈述【作废】** ⇒ 新口径 = ★**必需 23 (15 高速差分腿 + 8 单端脚) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` + `iss338_need_jtag_group_decision` + `iss338_need_boot_storage_answer` + `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** (★**本机实跑 `HW/check_s8_target_list.py` ⇒ 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔**★) · ★**老字一个字都没删 (见 §7-4 diff 自证)** ★【/ISS344-CORR】★★** ★
★**★硬声明: 本单【不许改固件】⇒ 下面所有「固件侧要不要改」只写清改哪一行, 一行都不许我动** ★

| net | 为什么可以悬空 (依据) | 悬空后固件侧要不要改 | ★**建议的板侧标记** ★ |
|---|---|---|---|
| ★`FSIN_OUT`★ | ★**零引用** (网名+变体) · 功能只在 SW 侧以待办/阻塞项形式存在 (IR-03 待办 + B-5 阻塞) · 上游 `FSIN` 网自身 `SoC_NC` (pad=1/0 段) ⇒ ★**SoC 侧本来就没接, 悬空不额外损失任何已连通的东西** ★ | 【ISS344-CORR】★★**★板那一趟动作 · 现在只定口径不定动作** ★★★★**清单保留在册, 但【现在不许落 NC】** ★★· 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` (★**「标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作」**★)· 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★ ★**要改 (但不是删功能, 是改测法)** ★<br>★**①** `SW/INTEGRATION_PLAN.md:717` IR-03 的「能否引出」⇒ 改判「**不能引出**」<br>★**②** `SW/INTEGRATION_PLAN.md:844` B-5 阻塞项 ⇒ 消项 (口径A 精度 ±4.2ms 已在同页写明)<br>★**③** `SW/SW_REQUIREMENTS.md:684` M-2 示波器法 ⇒ 标注降级, 端到端只走 IT-P4-02 高速摄影法<br>★**④** `SW/EVT_TEMPLATE.md:250` E2E-05「CH1=VSYNC/帧同步」⇒ 同步改口径 | ★**NC (不连)** ★<br>★**保留 `TP_FSIN` 位 (可选装配)** ★<br>★**⇒ 落表侧另需**: `HW/netlist_v1.csv:356` / `:401` 该网行的 dnp 判定 (★**属 hw-lead 地界, 本单不代拍** ★)  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧的「NC (不连)」【现在不成立】⇒ 新口径 = ★**可悬空 (条件式)** ★ · ★**条件**: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作 · 只在板那一趟做 · 现在只定口径不定动作** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` (★**「B 可悬空 (1 条) = `FSIN_OUT` (条件: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect)」**★) · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★|
| ★`JTAG_TDI`★ | ★**零引用** (网名+变体) · SW 侧 31 次 "JTAG" **无一命中 TDI** (只命中 `JTAG_TCK`/`JTAG_TMS`/`JTAG_M0`/`JTAG_M1`) · S3 救砖路径 SW 自己标 `[0数据]` ⇒ ★**外部工具链未确认 ⇒ 不能把它算作「已写死的功能」** ★ · 上游 `JTAG_TDI_SOC` 网 `SoC_NC` (pad=1/0 段) ⇒ **SoC 侧本来就没接** ★ | 【ISS344-CORR】★★**★作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明) ★★** ★★★**作废依据**: pm.yaml → `iss338_need_jtag_group_decision` (★**「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选」**★) · 证据等级 = ★**[实测]**★ · ★**本单不把这条改写成新的固件侧改动 (★那是板那一趟同批改的活·不属本单★)** ★【/ISS344-CORR】★★** ★ ★**要改 (降级声明, 不删流程)** ★<br>★**①** `SW/FLASH_AND_VERSION.md:336` S3 行 ⇒ 「JTAG 调试器接 SoC」加注「**demo 板不引出 TDI ⇒ S3 实际不可用**」<br>★**②** `SW/EVT_TEMPLATE.md:503` + `SW/S2_BOARD_TEST_CHECKLIST.md:393` 的「必须升级 S3 (JTAG)」⇒ 改判「**升级 S4 返厂**」<br>★**③** `SW/FLASH_AND_VERSION.md:44` 救砖 4 级表 ⇒ S3 行标「demo 板不可用」<br>★**④** `SW/S2_VENDOR_QUESTION_LIST.md` ⇒ 加一条问原厂「**是否提供 JTAG 引出 (含 TDI)**」 | ★**NC (不连)** ★<br>★**保留 `J_DEBUG` 排针位 (不装贴片, 手工可焊)** ★<br>★**⇒ 但注意**: `JTAG_TCK`/`JTAG_TMS`/`JTAG_TDO` **都有铜** ⇒ ★**若 JTAG 整组保留, 则 4 根线不完整 ⇒ 建议整组一起裁 (见 §4 附注)** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧的「NC (不连)」【作废】⇒ 新口径 = ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ · 依据 pm.yaml → `iss338_need_jtag_group_decision` (★**「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选」**★) · 证据等级 = ★**[实测]**★★**旧句「若 JTAG 整组保留, 则 4 根线不完整 ⇒ 建议整组一起裁」一并作废 ⇒ 终裁 = JTAG 整组 4 根 (`TCK`/`TMS`/`TDO`/`TDI`) 全保留** ★**【/ISS344-CORR】★★** ★|
| ★`SPI_MISO_BOOT`★ | ★**零引用** (网名+变体) · 上游 `SPI_MISO` 网 `SoC_NC` (pad=1/0 段) ⇒ **SoC 侧本来就没接** ★ · ★**`J_BOOT1` 整件 DNP** (网表明写「SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR 启动存储 (焊盘位可留作扩展)」) ★ · 启动存储类型/容量是 P4 `[0数据]` ⇒ **外部未确认, 不算已写死功能** ★ | 【ISS344-CORR】★★**★作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明) ★★** ★★★**作废依据**: pm.yaml → `iss338_need_boot_storage_answer` (★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」**★) · 证据等级 = ★**[实测]**★ · ★**本单不把这条改写成新的固件侧改动 (★那是板那一趟同批改的活·不属本单★)** ★【/ISS344-CORR】★★** ★ ★**要改 (改判, 不删)** ★<br>★**①** `SW/FLASH_AND_VERSION.md:359` P4 行 ⇒ 保留, 但补注「**主板侧启动存储焊盘位不引出 (J_BOOT1 DNP)**」<br>★**②** `SW/FLASH_AND_VERSION.md:46` 决定性 0 数据 ① ⇒ 补注「demo 板侧无 SPI-NOR 焊盘位」<br>★**③** `SW/S2_VENDOR_QUESTION_LIST.md:315` §4 P4 ⇒ 问原厂时补一句「**主板侧已无 SPI-NOR 焊盘位 ⇒ 若最终须外挂 SPI-NOR, 板要重出**」★<br>★**④** `SW/FLASH_AND_VERSION.md:527` L2-4「SPI-NOR 空板」器材需求 ⇒ 补注「**该验证手段与 demo 板无关 (靠外挂空板自验)**」 | ★**NC (不连)** ★<br>★**保留 `J_BOOT1` 焊盘位 (DNP, 扩展位)** ★<br>★**⇒ 落表侧**: `J_BOOT1` 整件已是 DNP ⇒ **网表侧本已一致, 无需改动** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧的「NC (不连)」【作废】⇒ 新口径 = ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ · 依据 pm.yaml → `iss338_need_boot_storage_answer` (★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」**★) · 证据等级 = ★**[实测]**★**【/ISS344-CORR】★★** ★|
| ★`SPI_MOSI_BOOT`★ | ★**同上** (零引用 · `SPI_MOSI` 网 `SoC_NC` pad=1/0 段 · `J_BOOT1` DNP) ★ | 【ISS344-CORR】★★**★作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明) ★★** ★★★**作废依据**: pm.yaml → `iss338_need_boot_storage_answer` (★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」**★) · 证据等级 = ★**[实测]**★ · ★**本单不把这条改写成新的固件侧改动 (★那是板那一趟同批改的活·不属本单★)** ★【/ISS344-CORR】★★** ★ ★**同 `SPI_MISO_BOOT` 的 ①②④** ★ | ★**NC (不连)** ★<br>★**保留 `J_BOOT1` 焊盘位 (DNP)** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧的「NC (不连)」【作废】⇒ 新口径 = ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ · 依据 pm.yaml → `iss338_need_boot_storage_answer` (★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」**★) · 证据等级 = ★**[实测]**★**【/ISS344-CORR】★★** ★|
| ★`SPI_SCLK_BOOT`★ | ★**同上** (零引用 · `SPI_SCLK` 网 `SoC_NC` pad=1/0 段 · `J_BOOT1` DNP) ★ | 【ISS344-CORR】★★**★作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明) ★★** ★★★**作废依据**: pm.yaml → `iss338_need_boot_storage_answer` (★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」**★) · 证据等级 = ★**[实测]**★ · ★**本单不把这条改写成新的固件侧改动 (★那是板那一趟同批改的活·不属本单★)** ★【/ISS344-CORR】★★** ★ ★**同 `SPI_MISO_BOOT` 的 ①②④** ★ | ★**NC (不连)** ★<br>★**保留 `J_BOOT1` 焊盘位 (DNP)** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧的「NC (不连)」【作废】⇒ 新口径 = ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ · 依据 pm.yaml → `iss338_need_boot_storage_answer` (★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」**★) · 证据等级 = ★**[实测]**★**【/ISS344-CORR】★★** ★|
| ★`UART_RX`★ | ★**零引用** (网名+变体) · ★**SW 侧串口用法实测 = 只读** (`cat "$SERDEV" > "$SER"`, `s2_rescue_config.json:230` 明写「取日志用」) ⇒ ★**板→主机方向 (UART_TX + TP_UART) 已 230 段铜, 完整可用** ★ · `J_UART` 整件 **dnp=可选** · 写方向 (主机→板) 在 SW 侧零需求 | 【ISS344-CORR】★★**★作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明) ★★** ★★★**作废依据**: pm.yaml → `iss338_need_jtag_group_decision` (★**「『固件零引用 ⇒ 可悬空』这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】⇒ 所以你那 9 条里 `JTAG_TDI` / `UART_RX` 的『可悬空』结论, main 不采信」**★) · 证据等级 = ★**[推算]**★ · ★**本单不把这条改写成新的固件侧改动 (★那是板那一趟同批改的活·不属本单★)** ★【/ISS344-CORR】★★** ★ ★**要改 (降级声明)** ★<br>★**①** `SW/tools/s2_board_run.sh:248-263` ⇒ 不改 (只读链在 UART_TX 上, 照常)<br>★**②** `SW/tools/s2_rescue_config.json:230` `_readme` ⇒ 补注「**只读日志用; 板侧不发命令 ⇒ UART_RX 不引出**」<br>★**③** `SW/S2_BOARD_TEST_CHECKLIST.md:94`「USB-TTL 串口线 + 笔记本 | 能看 U-Boot / kernel 串口输出」⇒ 只看输出 ✔ 不需 RX<br>★**④** 若将来要「主机往板里下命令」⇒ **须重开一条 need** (本单不代拍) | ★**NC (不连)** ★<br>★**保留 `J_UART` 排针位 (1×2 1.27mm, dnp=可选) + `TP_UART`** ★<br>★**⇒ 落表侧**: `HW/netlist_v1.csv:399` 该网行 dnp 判定 (★**hw-lead 地界** ★)  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧的「NC (不连)」【作废】⇒ 新口径 = ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ · 依据 pm.yaml → `iss338_need_jtag_group_decision` (★**「『固件零引用 ⇒ 可悬空』这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】⇒ 所以你那 9 条里 `JTAG_TDI` / `UART_RX` 的『可悬空』结论, main 不采信」**★) · 证据等级 = ★**[推算]**★**【/ISS344-CORR】★★** ★|
| ★`USB_CC2`★ **(待定)** ★ | ★**零引用** (网名+变体) · 官方板上零铜的那条 `USB_CC2` 端点 = ★**`J_USB_C.B5` + `R_CC2_D.1`** (板载 Type-C) ★, 而 `J_USB_C` 的 USB 2.0 差分 `USB_D_P/N_TYPEC` **已有铜** ⇒ 调试/供电数据通路不依赖 CC2 · 充电板侧 `J_TYPE_C` **不在官方板** · ★**但**: USB-IF Type-C 对 CC1/CC2 双路 Rd 有条款 ⇒ ★**不能由 SW 单方拍** ★ | 【ISS344-CORR】★★**★作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明) ★★** ★★★**作废依据**: pm.yaml → `iss338_need_usbif_cc1_cc2_rule` (★**「裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的「板侧默认 NC + 保留 R_CC2_D」建议【不采纳】」**★) · 证据等级 = ★**[官网]**★ · ★**本单不把这条改写成新的固件侧改动 (★那是板那一趟同批改的活·不属本单★)** ★【/ISS344-CORR】★★** ★ ★**要改 (但先等外部确认)** ★<br>★**①** `SW/tools/check_sw_ref_reachability.py:185` / `check_sw_ref_reachability_v2.py:244` 的 `"J_TYPE_C"` 硬编码 ⇒ **该位号不在官方板上** ⇒ 建议改指 `J_USB_C` (★**属闸脚本口径, 本单不代拍, 提 need 给 main** ★)<br>★**②** `SW/SW_TIMING_REVIEW.md:274`「充电板 `J_TYPE_C` 的 D+/D− 过不去」⇒ 该结论**只对充电板成立**, 板载 `J_USB_C` 不受此限 ⇒ 建议加注区分<br>★**③** `SW/ONETRIP_SW_RENAME_SAFETY.md:31` / `ONETRIP_SW_SAMEBATCH_RENAME_LIST.md:125` 的 `R_CC1`/`R_CC2` 不动组 ⇒ 补注「`R_CC2` 在充电板侧, `R_CC2_D` 在主板侧」 | ★**待定 ⇒ 建议 NC (不连)** ★<br>★**保留 `R_CC2_D` 位 (5.1k Rd) + `J_USB_C.B5` 触点** ★<br>★**⇒ ★★但落表前必须先拿到 USB-IF 条款的外部确认 (见 §4 B5-2)★★** ★  【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): 本格旧的「NC (不连)」【作废】⇒ 新口径 = ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ · 依据 pm.yaml → `iss338_need_usbif_cc1_cc2_rule` (★**「裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的「板侧默认 NC + 保留 R_CC2_D」建议【不采纳】」**★) · 证据等级 = ★**[官网]**★**【/ISS344-CORR】★★** ★|

### §3-1 ★★不列入候选的 2 条 (★为什么它们不能悬空★★)★
 【ISS344-CORR】★★**★§3-1 订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**「不列入候选」现在一共 8 条** ⇒ 本节的 2 条 (`CAM_RESET_N` `LED_G_D`) 之外, ★**`JTAG_TDI` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `SPI_SCLK_BOOT` `UART_RX` `USB_CC2` 这 6 条也一并移出候选** ⇒ ★**§3-1 标题里的「2 条」口径作废, 但两条的【必需】结论与终裁一致 ⇒ 无需改动** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★

| net | 为什么**不能**悬空 | 悬空的后果 (实测/推算) | 建议板侧标记 |
|---|---|---|---|
| ★`CAM_RESET_N`★ | ★**板级 [官方] 功能链**: `HW/netlist_v1.csv:285` 原文「★**主板必须能拉它**」+ 参考 Radxa CM5 overlay dts `reset-gpios (gpio1 RK_PB3, 低有效)` ⇒ ★**camera 模组 RESET 脚 (低有效) 必须由主板驱动** ★ | ★**[推算]** 相机不出图 ⇒ ★**MIPI-CSI 链死 ⇒ 端到端测量无对象 ⇒ 整个产品主功能失效** ⇒ ★**不是调试脚** ★ | ★**必须救回 (布铜)** ★<br>★**⇒ 落表侧**: `HW/netlist_v1.csv:285` dnp=**必装** ⇒ **本就可悬空性为零, 无需改** ★ |
| ★`LED_G_D`★ | ★**SW 侧真代码路径**: `D_LED_G` 被两个闸脚本 (`check_sw_ref_reachability.py:178` / `check_sw_ref_reachability_v2.py:237`) 与 `check_onepass_sw_sync.py:181` ★**硬编码进 `DESIGNATOR_REGISTRY` / 落表残项集合** ★ ⇒ ★**闸现在就在按「这块绿灯板上有 `D_LED_G`」判** ★ | ★**[实测]** 同族 `LED_B_D` = 105 段 / `LED_R_D` = 169 段 / ★**`LED_G_D` = 0 段** ⇒ ★**这是「该布没布」不是「不必布」** ⇒ ★**悬空 = 绿灯链断 + 闸与实物脱节** ★ | ★**必须救回 (布铜)** ★<br>★**⇒ 落表侧**: `HW/netlist_v1.csv:304` dnp=**必装** ⇒ **无需改** ★ |

---

## §4 ★★证据分级 + 外部缺口 (★按 main 口径标等级★★)

| # | 事实 | 等级 | 出处 |
|---|---|---|---|
| E1 | `SW/**` 全树 (126 文件) 对 9 条网的精确+变体命中 **全 0** | ★**[实测]** ★ | `logs/iss338/21_nine_net_reference_evidence.txt` · `logs/iss338/02_scan_SW_exact_variant.json` |
| E2 | 扫法自证: 同族控制网 `BAT_DET`=121 / `RESET_N`=52 / `JTAG_TCK|TMS`=31 / `LED_G`系=14 行命中 | ★**[实测]** ★ | `logs/iss338/14_variant_root_scan.txt` |
| E3 | 官方板 9 条网**零铜** (pad≥2 且段=0): 独立解析得 **18092 段 / 433 孔**, 零铜网 **24** 个, 与 ISS-334 完全一致 | ★**[实测]** ★ | `logs/iss338/22_pcb_independent_parse.txt` (本单自写 s-expr 解析器, 逐字节复现 ISS-334) |
| E4 | `USB_CC2` 零铜端点 = `J_USB_C.B5` + `R_CC2_D.1`; `J_TYPE_C` **不在官方板**; `USB_CC1` = **151 段** (已布) | ★**[实测]** ★ | `logs/iss338/22_pcb_independent_parse.txt` · `logs/iss338/20_final_crosschecks.txt` |
| E5 | `UART_TX` = **230 段 / 4 孔** (日志抓取链完整); `UART_RX` = 0 段; `J_UART` dnp=**可选** | ★**[实测]** ★ | `logs/iss338/22_pcb_independent_parse.txt` |
| E6 | SW 侧串口用法**只读**: `s2_board_run.sh:256` `timeout … cat "$SERDEV" > "$SER"`; 写方向扫法命中 **0** | ★**[实测]** ★ | `logs/iss338/06_functional_scan_serial_direction.txt` · `logs/iss338/09_functional_scan_ledsemantics_serialwrite.txt` |
| E7 | `LED_B_D`=105 段 / `LED_R_D`=169 段 / `LED_G_D`=0 段; `D_LED_G` 被 2 个闸脚本硬编码 | ★**[实测]** ★ | `logs/iss338/22_pcb_independent_parse.txt` · `logs/iss338/21_nine_net_reference_evidence.txt` |
| E8 | `CAM_RESET_N` = camera 模组 RESET 脚, 「★**主板必须能拉它**」+ dts `reset-gpios (gpio1 RK_PB3, 低有效)」 | ★**[官方]** ★ | `HW/netlist_v1.csv:285` · `HW/NETLIST_REV2_SPEC.md:53` |
| E9 | `J_BOOT1` 整件 **DNP** (主板不挂 SPI-NOR 启动存储) | ★**[官方]** ★ | `HW/netlist_v1_pins.csv` (J_BOOT1 全行) |
| E10 | `FSIN` / `SPI_MISO` / `SPI_MOSI` / `SPI_SCLK` / `JTAG_*_SOC` / `USB_DRD1_VBUSDET` 的 SoC 侧端点 = **`SoC_NC` 占位** (pad=1, 0 段) ⇒ ★**这些网的上游本来就没接** | ★**[实测]** ★ | `logs/iss338/22_pcb_independent_parse.txt` (11 处 `SoC_NC`) |
| E11 | unc 45 条中, 本单 9 条各占 1 条 = **9 条 (20.0%)**; 15 条高速差分腿占 **23 条**, 与本单**无交集** | ★**[实测]** ★ | `logs/iss338/23_unc_attribution.txt` (基于 `logs/iss334/00_official_drc_fresh.json`) |
| E12 | 9 条的 ISS-334 归桶: **8 条 B 桶** (出脚余量 ≤+0.30mm 几何钉死) + **1 条 C 桶** (`LED_G_D`, 余量 0.525mm 但 A* 搜索失败) | ★**[实测]** ★ | `HW/PCB/ONETRIP_S8_MECHANISM_PATH.md` §2-2 逐网归类表 |
| E13 | 官方同配方 A* 实测「补上 0 条」⇒ ★**B 桶那 8 条本来就走不通** | ★**[实测]** ★ | `logs/iss334/08_astar_officialenv.log` (ISS-334 既有产物) |
| E14 | USB-IF Type-C: ★**USB 2.0-only 设备只需 CC1 一路 Rd, CC2 可悬空** (ST 官方社区答复, 引 USB-C spec 原文) | ★**[媒体]** ★ | `https://community.st.com/.../how-to-connect-the-cc-pin-when-make-usb-type-c-compatible-to-usb2-0-59905` (ST 员工 2022-10-19) |
| E15 | ★**但同规范另有条款**: 「If the device has a Type-C receptacle, it needs to advertise Rd on **both** CC1 and CC2 lines」 | ★**[媒体]** ★ | `https://community.infineon.com/.../FAQs-on-CCGX-EZ-PD-CCGx-Product-USB-C-Cables-EMCA/ta-p/247747` |
| E16 | 项目内已引的 USB-IF R2.0 原文: 「Pin A5 (CC) … shall be connected to GND through a resistor Rd (5.1 kΩ ± 20%)」 | ★**[官方]** ★ | `HW/CHARGE_BOARD_SPEC.md:571` / `:573` |
| E17 | 本板**不上 PD 控制器 (TPS25730)** ⇒ 保留 Rd 5.1k×2 | ★**[官方]** ★ | `HW/SCHEMATIC_V1.md:654` · `HW/SCHEMATIC_V1_1_CHANGELOG.md:148` |
| E18 | 启动存储类型/容量 = **P4 待原厂 `[0数据]`** | ★**[0数据]** ★ | `SW/FLASH_AND_VERSION.md:359` · `SW/S2_VENDOR_QUESTION_LIST.md:315` |
| E19 | 原厂是否提供 JTAG 引出 + 调试器 + 转接板 = **全 `[0数据]`** | ★**[0数据]** ★ | `SW/FLASH_AND_VERSION.md:336` |
| E20 | `SW/**` 内无 C 代码 / 无 `.dts` / 无固件镜像; 唯一 `.dtsi` (`HW/PCB/panel_simple_dsi_template.dtsi`) 对 9 条网命中 **0** | ★**[实测]** ★ | `logs/iss338/20_final_crosschecks.txt` |

### ★★未决项 (需 main / 外部回答) ★★

- ★**B5-1 (需 main 裁)** ★: ★**`USB_CC2` 到底悬不悬空** — E14 与 E15 两条例外条款互相矛盾 (媒体级) ⇒ ★**SW 侧无权单方拍** ⇒ ★**建议: 板侧标 NC + 保留 `R_CC2_D` 位, 同时向原厂问一句「demo 板载 Type-C 是否要求 CC1/CC2 双路 Rd」** ★
 【ISS344-CORR】★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ ★**`USB_CC2` 判【必需】· 板侧不许标 NC** ⇒ ★**上方「建议板侧标 NC + 向原厂问一句」【不采纳】** ⇒ ★**本单零外发 ⇒ 不向原厂发任何问询** ★ · 依据 pm.yaml → `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[官网]** ★【/ISS344-CORR】★★** ★
- ★**B5-2 (需原厂, 但老板已定不发外 ⇒ 走 main 转已有的问询清单)** ★: ★**启动存储类型 (P4)** ★ — 若最终要外挂 SPI-NOR, 则 3 条 `SPI_*_BOOT` 不可悬空, 板要重出 ⇒ ★**建议 main 在既有问询清单里加这一句 (不新发信)** ★
 【ISS344-CORR】★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ ★**3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect** ⇒ ★**理由: `J_BOOT1` 焊盘位已在板 ⇒ 布线保留的成本 ≈ 0 ⇒ 事后不用重出板** ⇒ ★**上方「若最终要外挂 SPI-NOR 则不可悬空」的前提不再成立 (★无论老板怎么拍, 板都不用重出板★)** ⇒ ★**本单零外发 ⇒ 不发任何问询** ★ · 依据 pm.yaml → `iss338_need_boot_storage_answer` · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★
- ★**B5-3 (需 main 裁)** ★: ★**JTAG 整组处理** — `JTAG_TCK`/`JTAG_TMS`/`JTAG_TDO` **都有铜**, 只有 `JTAG_TDI` 是 0 段 ⇒ ★**若裁 TDI 就要接受「4 线缺 1 线, JTAG 实不可用」; 若保 JTAG 就得 4 线一起救** ⇒ **两难, 归 main** ★
 【ISS344-CORR】★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ ★**JTAG 整组【保留】⇒ `JTAG_TDI` 判【必需】(进 S8 布线目标) ⇒ 不是可悬空候选** ⇒ ★**main 选的是「不裁」这一支** ⇒ 上方「两难, 归 main」不再成立 · 依据 pm.yaml → `iss338_need_jtag_group_decision` · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★
- ★**B5-4 (需 main 裁)** ★: ★**9 条的最终分级定稿** — 本单只给 SW 侧事实与建议, ★**不代拍 24 条零铜网的整体定稿 (need-4b 是 main 的活)** ★
 【ISS344-CORR】★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ ★**分级定稿 = 必需 23 · 可悬空 1 (`FSIN_OUT`) · 待定 0** ⇒ ★**「24 条零铜网 = 23 必需 + 1 可悬空」**, 且 ★**名单须在板那一趟的新基线上重读 (★不许拿官方板那 24 条直接当靶★)** ⇒ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★

---

## §5 ★★诚实边界 (★交卷时逐条自证★★)★★

| 边界 | 自证方式 | 结果 |
|---|---|---|
| ★**零写板** ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb` + `stat -c '%y'` 开工前后各一次 | ★**md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 逐字节未动** ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三真源 md5 | ★**未动** ★ (`6aee500e…` / `9174309d…` / `5b999399…`) |
| ★**零改固件本体** ★ | `SW/**` 既有文件 md5 逐条 | ★**未动** ★ (★**本单只【新建】`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 本文件, 未改任何既有 SW 文档正文** ★) |
| ★**零改闸** ★ | `state/gate_check.py` / `state/frag_write.py` md5 | ★**未动** ★ (`5ccdcd5f…` / `3b383a52…`) |
| ★**只写自己的分片** ★ | `python3 state/frag_write.py --agent sw-lead` | ★**只写 `state/fragments/sw.yaml`; `hw.yaml`/`pm.yaml`/`mech.yaml` 一个字节没碰** ★ |
| ★**零外发** ★ | 无邮件 / 无询价 / 无问询 / 无采购 | ★**未发任何外发** ★ (★**USB-IF 条款用公开检索, 标 [媒体]** ★) |
| ★**不代拍** ★ | — | ★**只给 SW 侧事实 + 建议 + 待 main 裁的 4 条** ★ |
 【ISS344-CORR】★★**★ISS-344 订正**: ★**上方 4 条「待 main 裁」已于 2026-11-22 20:5x 全部裁完 (★`iss338_need_jtag_group_decision` / `iss338_need_boot_storage_answer` / `iss338_need_usbif_cc1_cc2_rule` / `iss334_need4b_zero_copper_net_triage`★) ⇒ ★**本单是对齐, 不是重判** ★ · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★

★**★复现命令 (★每条都可独立重跑★)★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 9 条网的网名级三跑 (精确 / 不区分大小写 / 去分隔符词干)
#    ★★必须 --exclude 掉本单自己的交付物 (否则命中的全是本报告表格里的网名)★★
for n in CAM_RESET_N FSIN_OUT JTAG_TDI LED_G_D SPI_MISO_BOOT SPI_MOSI_BOOT SPI_SCLK_BOOT UART_RX USB_CC2; do
  echo "== $n"
  grep -rn --exclude-dir=__pycache__ --exclude=ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md -w  "$n" SW | wc -l
  grep -rni --exclude-dir=__pycache__ --exclude=ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md -w  "$n" SW | wc -l
  c=$(echo "$n" | tr -d '_-'); grep -rni --exclude-dir=__pycache__ --exclude=ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md -E "(^|[^a-z0-9])${c}([^a-z0-9]|$)" SW | wc -l
done
# ② 扫法自证 (控制网必须 > 0)
grep -rni --exclude-dir=__pycache__ -w BAT_DET SW | wc -l     # ⇒ 121
grep -rni --exclude-dir=__pycache__ -w RESET_N  SW | wc -l     # ⇒ 52
# ③ 板面零铜复核 (本单自写解析器)
python3 logs/iss338/pcb_indep_parse.py                        # ⇒ 18092 段 / 433 孔 / 零铜网 24
# ④ unc 归因
python3 logs/iss338/unc_attribution.py                         # ⇒ 9 条各 1 条 = 9/45 = 20.0%
# ⑤ 边界自证
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       state/gate_check.py state/frag_write.py
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```

---

## §6 ★★交卷摘要 (★一句话给 main★★)★

★**9 条零铜单端网, `SW/**` 全树网名级零引用 (含所有拼写变体, 扫法已被 `BAT_DET`=121 / `RESET_N`=52 自证有效); 按功能等价物逐条查完后分级 = ★**必需 2 (`CAM_RESET_N` · `LED_G_D`) · 可悬空候选 6 (`FSIN_OUT` · `JTAG_TDI` · `SPI_MISO_BOOT` · `SPI_MOSI_BOOT` · `SPI_SCLK_BOOT` · `UART_RX`) · 待定 1 (`USB_CC2`)★** ★
 【ISS344-CORR】★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**上方旧分级陈述【作废】** ⇒ 新口径 = ★**必需 23 (15 高速差分腿 + 8 单端脚) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` + `iss338_need_jtag_group_decision` + `iss338_need_boot_storage_answer` + `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** (★**本机实跑 `HW/check_s8_target_list.py` ⇒ 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔**★) · ★**老字一个字都没删 (见 §7-4 diff 自证)** ★【/ISS344-CORR】★★** ★
★**★推翻 main 已定口径 2 条**: ★**`UART_RX` 从「必需」降为「可悬空候选」** (SW 侧串口实测**只读**, `UART_TX` 已 230 段铜, `J_UART` 整件可选) ★ · ★**`USB_CC2` 从「必需」降为「待定」** (官方板上零铜端点是板载 `J_USB_C.B5`, `USB_CC1` 已布 151 段, 但 USB-IF 双路 Rd 条款待外部确认) ★
 【ISS344-CORR】★★**★ISS-344 订正**: ★**上方「推翻 main 已定口径 2 条」【已被 main 的终裁否决】** ⇒ ★**`UART_RX` = 必需** (调试口) · ★**`USB_CC2` = 必需** ([官网] USB Type-C 双路 Rd) ⇒ ★**本页原结论保留在册作历史痕迹, 有效口径以 §7 为准** ★ · 依据 pm.yaml → `iss338_need_jtag_group_decision` / `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[实测]** / ★**[官网]** ★【/ISS344-CORR】★★** ★
★**★另推翻 main「其余 7 条」口径 2 条**: ★**`CAM_RESET_N`** (板级 [官方]「主板必须能拉它」⇒ 相机不出图 ⇒ 主链死) ★ · ★**`LED_G_D`** (同族 `LED_B_D`=105 段 / `LED_R_D`=169 段 都有铜, 只有它 0 段 ⇒ 该布没布) ★
★**S8 净效果**: ★**悬空 9 条 ⇒ unc 45→36 (−9 条 / −20.0%); 差分腿救回 0 条 (15 条差分腿占的 23 条 unc 与本单无交集); 布线工作量省 9 条, 其中 8 条是 ISS-334 已判定的 B 桶几何死线 (官方同配方 A* 实测补上 0 条) ⇒ 省的是「做不成的活」, 不是「能走通的活」** ★
 【ISS344-CORR】★★**★ISS-344 订正**: ★**上方「悬空 9 条 ⇒ unc 45→36」的口径【作废】** ⇒ ★**按终裁, 9 条里只有 `FSIN_OUT` 1 条可悬空 (★且带条件★) ⇒ 净效果 = 最多悬空 1 条** ⇒ ★**且 `FSIN_OUT` 标 NC 是板那一趟的动作·现在只定口径不动手** ⇒ ★**本单不宣称任何新的 unc 数字** ★ · 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★【/ISS344-CORR】★★** ★
★**本单零写板 / 零落表 / 零改固件本体 / 零改闸; 只写 `state/fragments/sw.yaml`; 零外发; 4 条待 main 裁的已登记在 §4** ★


---

## §7 ★★分级订正 (main 2026-11-22 20:5x 终裁) · ISS-344 追加式订正块★★

> ★**本节性质**: ★**追加式订正 (★老字一个字都没删·§7-4 有 diff 自证★)** ★
> ★**上游**: ★**main 2026-11-22 20:5x 的终裁 (★机制地界·不占老板拍板面★)** ★ ⇒ ★**本节是【对齐】, 不是【重判】** ★
> ★**机器真值 (★唯一尺子·只读★)**: ★**`HW/check_s8_target_list.py`** 的 `REQUIRED_SINGLE` / `FLOAT_OK` / `EXPECT_*` ★

### §7-0 ★★依据 (★逐字引 main 的终裁·`state/fragments/pm.yaml` → `answers`★)★★

- ★**`iss334_need4b_zero_copper_net_triage`** (★need-4b 分级【定稿】★): ★**「A 必需 (23 条) = ① 15 条高速差分腿 + ② 8 条单端脚 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · B 可悬空 (1 条) = `FSIN_OUT` (★条件: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作**★) · C 待定 (0 条)」** ★ → ★**[实测]** (★本机实跑 `HW/check_s8_target_list.py` ⇒ 「必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔」★)
- ★**`iss338_need_jtag_group_decision`**: ★**「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选」** ★ → ★**[实测]** (★`R_JTAG_TDI` 在盘 · `J_DEBUG` 1×4 排针 · `TP_JTAG` · ★`JTAG_TCK`/`JTAG_TMS`/`JTAG_TDO` 都有铜 ⇒ 只裁 TDI = 调试口摆设★)
- ★**`iss338_need_boot_storage_answer`**: ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ → ★**[实测]** (★`J_BOOT1` 焊盘位已在板 ⇒ ★**布线保留的成本 ≈ 0 ⇒ 事后不用重出板**★)
- ★**`iss338_need_usbif_cc1_cc2_rule`**: ★**「裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的「板侧默认 NC + 保留 R_CC2_D」建议【不采纳】」** ★ → ★**[官网]** (★USB Type-C Cable and Connector Specification 原文: 「★**The USB Type-C receptacle presents Rd on both of its CC pins because a CC pull-down must be present for the receptacle to indicate that it wants to consume VBUS current.**」⇒ ★**USB 2.0-only 插座 = 双路 Rd ⇒ CC1/CC2 都要有 Rd ⇒ CC2 不可悬空**★) · ★**[媒体]** (★TI《A Primer on USB Type-C and Power Delivery Applications》: 一条 CC 线可能变 VCONN ⇒ 另一条仍须 Rd 做方向检测★) · ★**[媒体]** (★网上「单 Rd 省一颗电阻」只适用于 Source/DRP 侧 (★规范原文: 「Only one of the CC1 or CC2 pins shall be in the SRC.Rd state」·★那是【源端】条款★)·★公开来源之所以互相矛盾就是这两条被混着引用了★)
- ★**main 给 SW 侧的判据边界 (★逐字·在 `iss338_need_jtag_group_decision` 里★)**: ★**「『固件零引用 ⇒ 可悬空』这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】」** ★ → ★**[推算]** (★JTAG 与 UART 是【硬件接口】, 由调试器 / 探针驱动, 不由应用固件引用 ⇒ ★**SW 零引用对它不构成「可悬空」的证据**★)

★**⇒ 终裁口径 (★唯一有效★)**: ★**必需 23 · 可悬空 1 · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 · 可悬空 1 · 待定 0** ★

### §7-1 ★★逐条订正表 (★旧说法 → 新说法 → 依据·★老字都在上面, 这里给有效口径★)★★

| ★net★ | ★旧说法 (ISS-338 · 2026-11-19)★ | ★新说法 (main 2026-11-22 20:5x 终裁)★ | ★依据 (pm.yaml key + 原文片段)★ | ★证据等级★ | ★固件侧「要改哪一行」清单★ |
|---|---|---|---|---|---|
| ★`CAM_RESET_N`★ | ★**必需** ★ | ★**必需** ★ (★**与终裁一致·无变化**★) | `iss334_need4b_zero_copper_net_triage` ★**「`CAM_RESET_N` (dts `reset-gpios gpio1 RK_PB3` ⇒ 相机不出图则 MIPI-CSI 链死)」** ★ | ★**[实测]** + ★**[官方]** ★ | ★**无需改** (★**从未判过 NC★**) ★ |
| ★`LED_G_D`★ | ★**必需** ★ | ★**必需** ★ (★**与终裁一致·无变化**★) | `iss334_need4b_zero_copper_net_triage` ★**「`LED_G_D` (同族 `LED_B_D`=105 段 / `LED_R_D`=169 段都有铜·只它 0 段 ⇒ 该布没布)」** ★ | ★**[实测]** ★ | ★**无需改** (★**从未判过 NC★**) ★ |
| ★`JTAG_TDI`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_jtag_group_decision` ★**「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (`SW/FLASH_AND_VERSION.md:336` / `:44` · `SW/EVT_TEMPLATE.md:503` · `SW/S2_BOARD_TEST_CHECKLIST.md:393`) ★**不再成立** ★ |
| ★`SPI_MISO_BOOT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_boot_storage_answer` ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (`SW/FLASH_AND_VERSION.md:359` / `:46` / `:527` · `SW/S2_VENDOR_QUESTION_LIST.md:315`) ★**不再成立** ★ |
| ★`SPI_MOSI_BOOT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_boot_storage_answer` ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (★**同 `SPI_MISO_BOOT`**★) ★**不再成立** ★ |
| ★`SPI_SCLK_BOOT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_boot_storage_answer` ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (★**同 `SPI_MISO_BOOT`**★) ★**不再成立** ★ |
| ★`UART_RX`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_jtag_group_decision` ★**「『固件零引用 ⇒ 可悬空』这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】⇒ 所以你那 9 条里 `JTAG_TDI` / `UART_RX` 的『可悬空』结论, main 不采信」** ★ | ★**[推算]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 3 处 (`SW/S2_BOARD_TEST_CHECKLIST.md:94` · `SW/tools/s2_board_run.sh:248` · `SW/tools/s2_rescue_config.json:230`) ★**不再成立** ★ |
| ★`USB_CC2`★ | ★**待定** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_usbif_cc1_cc2_rule` ★**「裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的『板侧默认 NC + 保留 R_CC2_D』建议【不采纳』」** ★ | ★**[官网]** (★USB Type-C 规范原文·插座端双路 Rd★) | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 3 处 (`SW/ONETRIP_SW_RENAME_SAFETY.md:31` · `SW/SW_TIMING_REVIEW.md:274` · `SW/tools/check_sw_ref_reachability.py:185`) ★**不再成立** ★ |
| ★`FSIN_OUT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**可悬空 (条件式) · 板那一趟动作 · 现在只定口径不定动作** ★ | `iss334_need4b_zero_copper_net_triage` ★**「B 可悬空 (1 条) = `FSIN_OUT` (★条件: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作**★)」** ★ | ★**[实测]** ★ | ★**保留在册 (4 处: `SW/INTEGRATION_PLAN.md:717` / `:844` · `SW/SW_REQUIREMENTS.md:684` · `SW/EVT_TEMPLATE.md:250`), 但标注「★板那一趟动作 · 现在只定口径不定动作★」** ★ |

★**★本页 9 条单端脚的有效口径 (★只此一份·与机器真值同源★)**: ★**必需 8 · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★

### §7-2 ★★固件侧「要改哪一行」清单 (★与终裁一致的版本·★仍然只出清单·一行固件都不许动★)★★

★**① 6 条必需网的「固件侧要改」条目 ⇒ 全部【作废】(★**不是改写成新的固件侧改动**★ · ★**那是板那一趟同批改的活·不属本单**★)** ★
- ★`JTAG_TDI` ⇒ ★**作废** ★ (原 4 处: `SW/FLASH_AND_VERSION.md:336` / `:44` · `SW/EVT_TEMPLATE.md:503` · `SW/S2_BOARD_TEST_CHECKLIST.md:393`)
- ★`SPI_MISO_BOOT` / `SPI_MOSI_BOOT` / `SPI_SCLK_BOOT` ⇒ ★**作废** ★ (原 4 处: `SW/FLASH_AND_VERSION.md:359` / `:46` / `:527` · `SW/S2_VENDOR_QUESTION_LIST.md:315`)
- ★`UART_RX` ⇒ ★**作废** ★ (原 3 处: `SW/S2_BOARD_TEST_CHECKLIST.md:94` · `SW/tools/s2_board_run.sh:248` · `SW/tools/s2_rescue_config.json:230`)
- ★`USB_CC2` ⇒ ★**作废** ★ (原 3 处: `SW/ONETRIP_SW_RENAME_SAFETY.md:31` · `SW/SW_TIMING_REVIEW.md:274` · `SW/tools/check_sw_ref_reachability.py:185`)
- ★★**依据**: pm.yaml → `iss338_need_jtag_group_decision` (★`JTAG_TDI` / `UART_RX★) · `iss338_need_boot_storage_answer` (★`SPI_*_BOOT★) · `iss338_need_usbif_cc1_cc2_rule` (★`USB_CC2★) · 证据等级 = ★**[实测]** / ★**[官网]** ★

★**② `FSIN_OUT` 的 4 处 ⇒ 保留在清单里, 但标注「★板那一趟动作 · 现在只定口径不定动作★」** ★
- `SW/INTEGRATION_PLAN.md:717` (IR-03) · `SW/INTEGRATION_PLAN.md:844` (B-5) · `SW/SW_REQUIREMENTS.md:684` (M-2 示波器法) · `SW/EVT_TEMPLATE.md:250` (E2E-05)
- ★★**本单现在【不动】这 4 处** ★ ⇒ ★**标 NC 是板那一趟的板侧动作** ★

★**③ `CAM_RESET_N` / `LED_G_D` ⇒ 无需改 (★**从未判过 NC**★)** ★

### §7-3 ★★机器闸 (★SW 侧分级与板侧真值不许再分叉★)★★

★**闸脚本**: ★**`SW/tools/check_sw_zero_copper_grade_consistency.py`** (★ISS-344 新建★) ★
★**真值源**: ★**`HW/check_s8_target_list.py`** 的 `REQUIRED_SINGLE` / `FLOAT_OK` / `EXPECT_*` (★**只读·AST 静态解析·不执行它的代码·一个字都不许动**★) ★

★**判据 (★逐条可单测★)** ★★
- ★**C0** ★**跨节一致**: §3/§3-1 表的「建议的板侧标记」必须与 §7 订正表的「新说法」判出同一档 ★
- ★**C1** ★**凡判 NC 的网, 必须在 `FLOAT_OK` 里** ⇒ 否则判红并点名 ★
- ★**C2** ★**凡在 `REQUIRED_SINGLE` 里的网, 判 NC 就判红并点名** ★
- ★**C3** ★**`REQUIRED_SINGLE` 的每一条都必须在 SW 页里被判成【必需】** ★
- ★**C4** ★**`FLOAT_OK` 的网不得被 SW 页判成【必需】** ★
- ★**C5** ★**`REQUIRED_SINGLE` 的网, 其「固件侧要改哪一行」清单必须标「作废」** ★
- ★**C6** ★**待定档必须为空** (终裁: 待定 0 条) ★
- ★**C7** ★**板侧名单之外的网, 不许被 SW 页判成 NC 或必需** ★
- ★**C8** ★**标记类别认不出来** ⇒ 判红 (不许糊过去) ★
- ★**C9** ★**§2 表「分级」列与 §3 标记同档** (加分项) ★

★**怎么跑 (★一条命令能复现★)** ★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_sw_zero_copper_grade_consistency.py ; echo "GATE344_RC=$?"
# ★反向用例 (★只在 tmp/ 副本上做·真件一个字节都不许被动★): ★
python3 SW/tools/check_sw_zero_copper_grade_consistency.py --doc tmp/iss344/rev/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md ; echo "REV_RC=$?"
```

### §7-4 ★★只增不删自证 (★老字一字未删 = 可自证★)★★

★**★为什么不能用 `diff | grep -c '^<'` 当证据 (★本项目老坑·这里说清楚★)**: ★**§3/§2 表里有 14 行是【行内插入】(在单元格中间插字) ⇒ 行级 diff 会把这 14 行同时打成 `<` 和 `>` ⇒ 行级 diff 看不出「只增不删」** ★ ⇒ ★**必须按【字符级子序列】证明** ★

★**自证命令 (★一条能复现★)** ★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 logs/iss344/check_only_additions.py \
     tmp/iss344/orig_ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md \
     SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md ; echo "ONLYADD_RC=$?"
# ★三条判据全过才算过: ① 逐行 (老行逐字原样仍在, 或老行是某新行的字符子序列)
#   ② 全文 (老文件全文是新文件全文的字符子序列 ⇒ 全局一个字符都没被删)
#   ③ 行数只增不减 ★
# ★人工可读的完整 diff 落在 `logs/iss344/05_diff_only_additions.txt`
#   (★那 14 个 `<` 行 = 14 个被【行内插入】的表格行·不是删除★) ★
```

★**订正执行器**: ★**`logs/iss344/apply_iss344_corrections.py`** (★**只做插入·不做替换·自证用 difflib 校验无 delete 操作 + 逐行字符子序列校验**★) ★
★**订正源块**: ★**`logs/iss344/iss344_sec7.md`** (★本节 §7 的来源·可重放★) ★