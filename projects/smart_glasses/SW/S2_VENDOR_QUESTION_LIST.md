# S2 救砖链路 · 原厂问询清单 (P1 / P2 / P3 / P4)

> **文件**: `SW/S2_VENDOR_QUESTION_LIST.md` v1.0 (2026-10-30) · ISS-120 (sw-lead)
> **性质**: ★ **给项目总工的外发草稿** —— sw-lead **不直接联系原厂 / 供应商 / 模组厂**。
> **用途**: 把 S2 救砖链路的 4 个 [0数据] 参数项, 变成**一次邮件能问完、且回复能直接落到配置文件字段**的问询。
> **落点**: 拿到回复后, 由项目总工转录进 `SW/tools/s2_rescue_config.json` (字段映射见每节的"填进哪个字段")。
>
> **一句话**: **每个问题都写死了"问什么 / 要什么格式回 / 回填哪个字段"** —— 避免来回追问, 也避免回复收到却落不了地。

---

## 0. 使用说明 (给项目总工)

### 0.1 ★ 外发纪律

| # | 规则 |
|---|---|
| 1 | **sw-lead 不直接对外**。本文件是**草稿**, 外发由项目总工执行 (沿用 `state/fragments/sw.yaml` 里 `waiting_on=vendor` 的既有登记方式)。 |
| 2 | 本清单里已登记过的条目**不要重复问** —— 见 §6 "与既有 needs_from 的对应关系"。 |
| 3 | 回复**必须是书面的**(邮件正文或 PDF)。口头/会议结论请项目总工当场落成一段文字转录, 否则仍按 [0数据] 处理。 |
| 4 | 收到回复后: 填进 `SW/tools/s2_rescue_config.json` 对应字段 → 跑 §7 的回填自检 → 再跑 `--preflight` 复核。 |
| 5 | ★ **通用示例不是回复**。对方说"类似 RK3588 的那种做法"不算数, 要具体到 **VID:PID / 命令 / 分区名 / 数值**。 |

### 0.2 ⚠️ ★ 换芯口径分叉 (发信前必须先定)

> ISS-119 (2026-10-29) 把 SoC 基线从 ARS45 换成了 **RK3588** (RK3576 为可机械触发的翻转后手; 定案书 `HW/CHIP_SELECTION_DECISION.md`; **verify_by=boss, 待老板点头**)。
>
> ⇒ **问谁、问什么, 取决于最终基线**。本清单因此**分两条线**, 请项目总工选一条 (或两线并问, 但要标明):

| | **线路 A: RK3588 基线** (ISS-119 定案方向) | **线路 B: ARS45 基线** (若翻案 / 老板另定) |
|---|---|---|
| 问谁 | **模组厂 / 板级设计方** (不是瑞芯微芯片厂 —— 芯片级参数公开, 但**你这块板的** BOOT 通路、分区表、存储配置是模组厂定的) | ARS45 原厂 / 方案商 |
| §1 P1 问谁 | 模组厂 (硬件) | 原厂 |
| §2 P2 问谁 | 模组厂 (工具与固件包) | 原厂 |
| §3 P3 问谁 | 模组厂 (你这块的枚举特征) | 原厂 |
| §4 P4 问谁 | 模组厂 (存储与分区表) | 原厂 |
| 额外必问 (§5) | **① 核心板 vs 整板 ② 存储介质 ③ 电源/BOOT 引脚 ④ 固件包交付形式** | ① 存储 ② 分区表 ③ 校验/回滚 ④ 工具版本 |
| 公开可查的部分 | ★ 芯片级工具链是**公开的** (见 §5.1) ⇒ 问询重点应放在**"你这块板"的差异**, 不要让对方重复回答公开信息 | 几乎全要问 |

### 0.3 问询优先级

| 优先级 | 问什么 | 为什么急 |
|---|---|---|
| **P0** | §4 P4 (启动存储 + 分区表) + §2 P2 (下载工具) | 这两项不定, **板子回来了也刷不回去** ⇒ 量产一票否决项直接卡死 |
| **P1** | §3 P3 (USB 枚举特征) + §1 P1 (BOOT 进入条件) | 这两项不定, **连"进没进 BOOT"都无法机械判定** ⇒ CB-01/BR-03~05 全判未验 |
| **P2** | §5 附加问题 | 影响返修流程与产线工位设计 |

---

## 1. P1 · `BOOT_ENTER_SPEC` — 进 BOOT/下载模式的硬件条件

> **卡住什么**: `SW/S2_BOARD_TEST_CHECKLIST.md` §3 的全部时序/电平; BR-03 / BR-04 (进 BOOT); BR-05 (工具识别)。
> **needs_from key**: `fw_boot_entry_cond` (vendor) + `fw_boot_mode_hw` (hw-lead)
> **状态**: **[0数据]** —— 原厂书面回复前一律留空。

### 1.1 问什么

**Q1.1** 贵方设备进入**下载/BOOT 模式**的**硬件触发条件**是什么？请逐项回答:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | BOOT 引脚 (或 Recovery 按键) 的**有效电平** | 高有效 / 低有效; 该引脚在芯片侧的**确切引脚名** (如 `BOOT`, `GPIOX_n`) |
| b | 进入下载模式需要**按住哪个键**、**按多久**、**与上电/复位的先后顺序** | 具体按键组合 + **时长 (ms)** + 顺序 (先按住再上电? 还是上电后按住再按复位?) |
| c | BOOT 条件必须**保持多久** | 从建立 BOOT 条件到松手之间的最小保持时间 (ms) |
| d | **RESET 键**的脉冲宽度要求 | 最小/典型/最大 (ms) |
| e | 是否支持**不按键**直接进下载模式 | 有 / 无; 若有, 条件是什么 |
| f | 是否有**超时自动进下载模式**的机制 | 有 / 无; 超时值 (s) |
| g | 芯片的 **bootROM** 是否在启动失败时**自动回落**到下载模式 | 是 / 否 (这决定"板子砖了还能不能救" —— **这是本项最关键的一条**) |

**Q1.2** 关于**产线工位**的补充 (量产一票否决项的落地条件):

| # | 问什么 |
|---|---|
| a | 产线上推荐用哪种进下载模式的方式？**跳线到测试点** / **按键组合** / **其它**？ |
| b | 贵方板子上**是否已引出**该测试点 (test point) 或独立按键？丝印/位号是什么？ |
| c | 是否**必须**按住侧键才能进下载模式？（★ 我们的侧键已被售后手势占用: 长按 3s = 显示版本号, 长按 10s = 关机 —— 若复用同一颗键, 用户误触就会把眼镜送进下载模式） |

**Q1.3** 关于**校验与回滚** (和 S2 一起问, 一次问完):

| # | 问什么 |
|---|---|
| a | bootloader 启动时是否校验分区 CRC / SHA256？不通过时**具体行为**是什么 (停住 / 回滚 / 停在下载模式)? |
| b | **A/B 槽自动回滚**是否可配？**尝试次数阈值**是多少？ |
| c | **secure boot / 镜像签名**是否启用？密钥如何管理 (烧进 OTP / efuse / 还是软配置)? |

### 1.2 什么格式回 (要对方按这个格式回, 别让他写散文)

> 建议在邮件里**直接把下面这张表贴给对方**, 让他在表格里填。

```
【Q1.1 进 BOOT/下载模式】
项                     贵方回答 (请填具体值)
BOOT 引脚名             ____________
BOOT 有效电平           高有效 / 低有效
进入下载的按键组合       ____________ (例: 按住 REC + 按 RESET)
按住时长 (ms)           ____________
RESET 脉冲宽度 (ms)     最小____ 典型____ 最大____
BOOT 条件最小保持 (ms)   ____________
无需按键直接进下载       支持 / 不支持 (若支持, 条件: ____________)
超时自动进下载          支持 / 不支持, 超时____秒
bootROM 启动失败回落下载  是 / 否  (★ 若是"否", 请说明砖了如何恢复)

【Q1.2 产线工位】
推荐进下载方式           跳线测试点 / 按键组合 / 其它____
测试点丝印/位号          ____________
是否已引出独立下载按键    是 (位号____) / 否
是否必须用侧键            是 / 否

【Q1.3 校验与回滚】
bootloader 分区校验       CRC / SHA256 / 无
校验失败行为              ____________
A/B 自动回滚              可配 / 不可配, 尝试次数阈值____
secure boot / 签名         启用 / 不启用, 密钥管理方式____________
```

### 1.3 拿到后填进 `s2_rescue_config.json` 的哪个字段

| 回复内容 | 填进字段 | 写法 |
|---|---|---|
| Q1.1 整体答复摘要 | `params.P1_BOOT_ENTER_SPEC.value` | 一段摘要字符串; 同时把 `params.P1_BOOT_ENTER_SPEC.status` 改成 **`DONE`**, 并加 `"source": "vendor-official"` |
| Q1.1a BOOT 引脚名 | `boot_enter.boot_pin_name` | 字符串, 如 `"BOOT"` |
| Q1.1a 有效电平 | `boot_enter.boot_pin_level` | `"high"` / `"low"` |
| Q1.1b 按键组合 | `boot_enter.keys` | 数组, 如 `["BOOT", "RESET"]` |
| Q1.1b/c 时序 | `boot_enter.t0_hold_boot_ms` (按住时长) / `boot_enter.t1_reset_pulse_ms` (RESET 脉冲) / `boot_enter.t2_release_all_ms` (BOOT 条件保持) | 整数, 单位 ms |
| Q1.1e/f 方式与超时 | `boot_enter.method` (`"A"` 跳线 / `"B"` 按键 / `"C"` USB) + `boot_enter.t3_enum_timeout_s` | 字符串 / 整数秒 |
| Q1.2a/b 测试点 | `boot_enter.boot_pin_name` 注释 + 交接单 B5 转项目总工转 hw-lead (`fw_boot_mode_hw`) | — |
| Q1.3 校验/回滚 | 交接单 B5 转项目总工裁决 (影响 BR-11/BR-12 的预期行为) | — |

> ★ `boot_enter.t3_enum_timeout_s` 现在是 15, 那是 [推算] 值 (给 USB 枚举 + 工具握手留余量), **原厂给了就改成对方的值**。

---

## 2. P2 · `DL_TOOL` — 原厂下载工具

> **卡住什么**: BR-05 (工具识别) / BR-06 (全量刷写) —— **没工具, 板子回来了也刷不回去**。
> **needs_from key**: `fw_vendor_toolchain` (vendor)
> **状态**: **[0数据]**

### 2.1 问什么

**Q2.1** 下载工具本体:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | 工具**名称** | 例: `RKDevTool` / `rkdeveloptool` / `upgrade_tool` / 贵方自研名 |
| b | **版本号** | 精确版本 + **下载链接** (要能下到、能校验 sha256) |
| c | 支持**哪些平台** | Windows / Linux / macOS, 各版本号 |
| d | 是否**可脚本化批量刷写** (命令行) | 可 / 不可; 若是可, 请给**完整命令行示例** (含参数含义) |
| e | 支持的**存储类型** | eMMC / SPI-NOR / SPI-NAND / SD 卡, 各自分区大小限制 |
| f | 刷写**前是否自动备份**现有分区 | 是 / 否; 若是, 备份文件放哪、怎么取回 |

**Q2.2** 固件包与分区表:

| # | 问什么 |
|---|---|
| a | 固件包的**交付形式** (整包 update.img? 分区镜像? loader + 各分区?) —— 请给一份**实际的目录清单** |
| b | **官方分区表**的定义文件 (例: `parameter.txt`) 能否提供？★ 请给出**对应贵方目标存储容量**的那一版 |
| c | 分区**名称与顺序**、每个分区的**大小与对齐**、各分区对应的**镜像文件名** |
| d | **版本块 / 元数据分区** (保存固件版本串、SN、标定 ID 的那个分区) 在贵方分区表里叫什么？**格式**是什么 (二进制布局 / 文本)? 我们要在里面写版本信息 |
| e | 刷写后如何**回读校验**? 工具本身有没有校验命令? 返回码含义是什么? |

**Q2.3** bootloader 与固件命名 (供追溯):

| # | 问什么 |
|---|---|
| a | bootloader / SPL / u-boot 的**文件命名规则**与版本号格式 |
| b | 是否有**固件签名校验**; 我们自己编译的镜像能否被工具接受 (还是必须用贵方签名的包)? |

### 2.2 什么格式回

```
【Q2.1 工具】
工具名称            ____________
版本号              ____________
下载链接            ____________ (附 sha256)
支持平台            Windows____ / Linux____ / macOS____
可脚本化            可 / 不可
命令行示例          ____________ (完整命令 + 参数含义)
支持存储            eMMC / SPI-NOR / SPI-NAND / SD (各容量上限: ____________)
自动备份            是 / 否, 备份路径____________

【Q2.2 固件包与分区表】
固件包形式          整包 update.img / 分区镜像 / loader+分区 / 其它____
实际目录清单        (请直接贴 tree 输出)
官方分区表文件      文件名____________ (可提供? 是 / 否)
适用存储容量        ____________
分区名称与顺序      (请贴表格: 名称 | 大小 | 对齐 | 镜像文件名)
版本/元数据分区     名称____________, 格式: 二进制 / 文本, 布局说明____________
回读校验            有 / 无, 命令____________, 返回码含义____________

【Q2.3 命名与签名】
bootloader/SPL/u-boot 命名规则 ____________
固件签名校验        有 / 无; 自编镜像是否可被接受: 可 / 不可
```

### 2.3 拿到后填进 `s2_rescue_config.json` 的哪个字段

| 回复内容 | 填进字段 | 写法 |
|---|---|---|
| Q2.1 整体摘要 | `params.P2_DL_TOOL.value` + `status` → **`DONE`** + `"source": "vendor-official"` | 摘要字符串 |
| Q2.1a/c 工具名与版本 | `board_test.tools[].name` / `.version_cmd` | `{"name":"RKDevTool","version_cmd":["RKDevTool","--version"]}` 之类; 脚本会自动取版本, 取不到记 [0数据] |
| Q2.1d 全量刷写命令 | ★ `board_test.flash.cmd` | **argv 数组** (不走 shell 字符串): `["rkdeveloptool","wl","0","update.img"]` —— 占位符由我方脚本按现场替换 |
| Q2.1f 备份命令 | `board_test.flash.backup_cmd` | argv 数组; 无备份能力就填 `null` (脚本会跳过) |
| Q2.2a 固件包目录 | `board_test.selftest` 之外的镜像路径 —— 由 sw-lead 落进 `partition_layout.partitions[].file` | 字符串 |
| Q2.2b/c 分区表 | ★ **整段替换** `partition_layout` (`device_total_size` / `align` / `crc_slots` / `partitions[]`) + 把 `partition_layout.source` 改成 **`"vendor-official"`** | ★ **这一步不做, CB-02/CB-06 永远判未验** |
| Q2.2d 版本块分区 | `partition_layout.partitions[]` 里 `version_block` 那条 (名字/大小) + 交接单转项目总工 (二进制布局要不要照抄) | — |
| Q2.2e 回读校验 | ★ `board_test.verify.readback_cmd` + `board_test.verify.readback_target` | argv 数组 + 输出文件路径 |
| Q2.3 命名规则 | 交接单 B5 (影响 §3.5 追溯字段) | — |

---

## 3. P3 · `USB_PHY` — USB 下载能力 + BOOT 态枚举特征

> **卡住什么**: CB-01 (刷完重新枚举)、BR-05 (工具识别)、以及**整个 S2 链路能否成立** —— 若这块板没有可用的 USB Device 通路, 救砖链路从根上不成立。
> **needs_from key**: `fw_usb_boot_phy` (vendor) + `sw_usb_phy_spec` (vendor)
> **状态**: **[0数据]**

### 3.1 问什么

**Q3.1** 物理层:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | SoC 的 USB 控制器**有没有 Device 模式** (能枚举成 USB 从设备)? | 有 / 无; 是 OTG 还是纯 Host |
| b | **有没有独立的 USB Device PHY**? | 有 / 无 —— ★ 若"无", 那 Type-C 母座只能走充电/host, 救砖链路的**实现方式要整体重做**, 这是最高优先级的一条 |
| c | 走的是 **USB 2.0 (FS/HS)** 还是 **USB 3.0**? | 明确速率 |
| d | **VBUS** 的处理方式 | 芯片侧有没有 VBUS 检测脚? Type-C 母座的 VBUS 是直连还是经过电源开关/分压检测? (我们板级已发现 SoC 侧无 VBUS 线, 需原厂确认是否必须) |
| e | USB **D+/D−** 是否经过 ESD/滤波器件, 是否共用充电通路 | 简述 |

**Q3.2** 协议与枚举特征 (★ 最关键, 要具体值):

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | 支持哪些**下载协议** | fastboot / DFU / UF2 / Rockusb / 贵方私有 / 无 |
| b | ★ **BOOT/下载态的 USB VID:PID** | **精确到 4 位十六进制**, 并注明是 **Maskrom 态** 还是 **Loader 态** 还是 **fastboot 态** —— 这几个态 PID 通常**不同**, 请**分别给全** |
| c | **正常态**的 USB VID:PID (我们用它做"刷完后回到正常态"的比对基线) | 精确到 4 位十六进制 |
| d | USB **product / manufacturer 字符串** (下载态与正常态) | 原文 |
| e | 下载态的 **Serial Number** 字符串格式 | (我们用它做板卡 SN 追溯) |
| f | 是否支持 **ADB**? | 支持 / 不支持; 若支持, 正常态能否连上 (我们有一个 `mode=prod` 时要"插线无 adb 设备"的安全规则) |

**Q3.3** 枚举行为的边界条件 (不问清楚, 现场会翻车):

| # | 问什么 |
|---|---|
| a | 下载态是否**必须**同时满足 BOOT 条件 + 上电? 能否在**已开机状态**下用软件进入? |
| b | 从建立 BOOT 条件到 PC 上能枚举出设备, 典型需要多久? 最大多久? (我们用 15s 作超时, 是 [推算] 值) |
| c | USB 枚举**是否需要 VBUS 供电** (即必须插着 PC 才能进下载态)? |
| d | 有无**已知失败场景** (线材 / 供电 / 端口位置 / hub) 需要我们规避? |

### 3.2 什么格式回

```
【Q3.1 物理层】
USB Device 模式        有 / 无 (OTG / 纯 Host)
独立 USB Device PHY    有 / 无            ← ★ 最高优先级
USB 速率                USB2.0 FS / USB2.0 HS / USB3.0
VBUS 处理               芯片侧有 VBUS 检测脚? 是 / 否; 母座 VBUS 直连 / 经开关 / 经分压
D+/D- 拓扑              ____________

【Q3.2 协议与枚举特征】
下载协议                fastboot / DFU / UF2 / Rockusb / 私有____ / 无
BOOT 态 VID:PID         Maskrom: ____:____   Loader: ____:____   fastboot: ____:____   其它: ____:____
正常态 VID:PID          ____:____
product 字符串 (下载态)  ____________
product 字符串 (正常态)  ____________
manufacturer            ____________
Serial Number 格式      ____________
ADB 支持                支持 / 不支持; prod 模式下能否连上: 能 / 不能

【Q3.3 边界条件】
必须同时满足 BOOT+上电  是 / 否; 已开机能否软件进入: 能 / 否
典型枚举耗时 / 最大耗时  ____秒 / ____秒
是否需要 VBUS 供电       是 / 否
已知失败场景与规避       ____________
```

### 3.3 拿到后填进 `s2_rescue_config.json` 的哪个字段

| 回复内容 | 填进字段 | 写法 |
|---|---|---|
| Q3.1/Q3.2 整体摘要 | `params.P3_USB_PHY.value` + `status` → **`DONE`** + `"source": "vendor-official"` | 摘要字符串 |
| ★ Q3.2b **BOOT 态 VID:PID** | ★ `usb_signatures.entries[]` | **每个态一条**, 例: `{"vid":"2207","pid":"350b","label":"Maskrom 态 (对方给的)","source":"vendor-official"}` —— ★ `source` **只允许** `vendor-official` 或 `measured`; **绝不许留 `generic-example`** |
| Q3.2c 正常态 VID:PID | 无处可填 (它是**基线**, 由现场实测 `s2_step0_normal.json` 产出) | ★ 但**可以**先写进交接单 B5, 供现场比对参考 |
| Q3.2d/e 字符串 | 交接单 B5 (影响 CB-01 的判定细则) | — |
| Q3.2f ADB | `board_test.checks` 增补 `"adb_supported": true/false` (可选键) | — |
| Q3.3b 枚举耗时 | `boot_enter.t3_enum_timeout_s` | 整数秒 (把 15 这个 [推算] 值换成实测值) |
| ★ Q3.1b **无独立 PHY** | ★ **不填任何字段** —— 直接升级为**阻断项**, 转项目总工裁决 (救砖链路实现方式要整体重写) | — |

> ★ **回填后自检**: `python3 SW/tools/s2_board_judge.py --selftest` 里 T4 用例已验证 —— 命中 `generic-example` 签名时 CB-01 **判未验**, 不会被通用示例蒙混过关。

---

## 4. P4 · `BOOT_STORE` — 启动存储类型/容量 + 官方分区表

> **卡住什么**: 整个 §4 分区方案 + BR-06 (刷写) / BR-07 (回读) / CB-02 / CB-06; 也是 **SW/FLASH_AND_VERSION.md §4.1 推荐 C 的成立条件**。
> **needs_from key**: `fw_vendor_toolchain` (vendor) + `fw_boot_storage_bom` (hw-lead)
> **状态**: **[0数据]**

### 4.1 问什么

**Q4.1** 存储本体:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | 启动存储**类型** | eMMC / SPI-NOR / SPI-NAND / SD / UFS |
| b | **容量** | 明确值 (e.g. 16GB / 128MB) |
| c | 若是 eMMC | **颗粒型号**、**HS200/HS400** 速率档位 |
| d | 若是 SPI-NOR | **型号 + 容量** (我们 [推算] 得出这套分区表需要 **≥128MB**, 64MB 装不下 —— 请确认能不能给到 128MB) |
| e | ★ **rootfs 体积上限** | 多少 MB 以内必须用 NOR? 换芯后 rootfs 实际会多大? (这是选型的总分叉点) |
| f | 存储是**板载**还是**可更换模组**? | 板载 / 模组 (模组的话, 换存储要不要重新刷 bootloader?) |

**Q4.2** 分区表 (★ 本项的真正目的):

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | **官方分区表定义文件**能否提供 (例: `parameter.txt`)? | 请给**针对上面容量**的那一版 |
| b | 分区**名称 / 顺序 / 大小 / 对齐** | 完整表 |
| c | 分区**单位** | 扇区 (512B) / KB / MB —— ★ 必须明确, 我们 [推算] 的表按字节算的, 单位错了整段错 |
| d | 分区表里**有没有预留"版本/元数据"分区** | 名称 + 大小 + 格式 |
| e | bootloader / SPL / u-boot / boot / recovery / rootfs 各对应哪个分区 | 对照表 |
| f | **A/B 双槽**是否支持? 分区名怎么带槽位 (后缀 `_a`/`_b` 还是别的)? | 方案 + 命名规则 |
| g | 官方**整包镜像**能否给出**分区级 CRC 表** (每分区 sha256) | 能 / 不能 |

**Q4.3** 与我们现有方案的冲突 (直接把已知结论摆出来, 让对方一次答清):

> 我们按 §4.1 的"条件式推荐 C" (rootfs 只读 + app/model A/B 双槽) 算过容量:
> **bootloader 1 + kernel 8 + rootfs 30 + app 8×2 + model 15×2 + isp 1 = 90MB**
> ⇒ **64MB SPI-NOR 装不下**, 容量下限升到 **≥128MB**。
>
> **Q4.3a** 贵方是否有 **128MB 及以上** 的 SPI-NOR 方案? 若只能给 64MB, 哪些分区可以压缩/合并?
> **Q4.3b** 若走 eMMC, 容量普遍 8GB 起 —— 那 [推算] 的 90MB 分区表需要按 eMMC 的 `parameter.txt` 重排, 贵方能否直接提供 eMMC 的官方分区表?

### 4.2 什么格式回

```
【Q4.1 存储】
类型                  eMMC / SPI-NOR / SPI-NAND / SD / UFS
容量                  ____________
eMMC 颗粒/速率         ____________ (若非 eMMC 可空)
SPI-NOR 型号+容量       ____________
rootfs 体积上限        ____________ MB
板载 / 可换模组        板载 / 模组

【Q4.2 分区表】
官方分区表文件          文件名____________ (可提供? 是 / 否)
分区单位                扇区512B / KB / MB      ← ★ 必填
分区表                  (请贴完整表: 名称 | 起始 | 大小 | 对齐 | 镜像文件)
版本/元数据分区          名称____________, 大小____, 格式____________
bootloader/SPL/u-boot 对应分区  ____________
A/B 双槽                支持 / 不支持; 命名规则____________
分区级 CRC 表            能 / 不能

【Q4.3 容量冲突】
128MB 及以上 NOR 方案     有 / 无 (型号____________); 若只能 64MB, 可压缩的分区: ____________
是否走 eMMC              是 / 否; 若是, 能否给 eMMC 官方分区表: 能 / 不能
```

### 4.3 拿到后填进 `s2_rescue_config.json` 的哪个字段

| 回复内容 | 填进字段 | 写法 |
|---|---|---|
| Q4.1 整体摘要 | `params.P4_BOOT_STORE.value` + `status` → **`DONE`** + `"source": "vendor-official"` | 摘要字符串 |
| ★ Q4.2 分区表 | ★ **整段替换** `partition_layout` | `device_total_size` (字节) / `align` / `erase_block` / `crc_slots[]` / `partitions[]` (每条: `name` / `size` / `file` / `crc_slot` / `slot`) |
| ★ Q4.2 来源标记 | ★ `partition_layout.source` | 改成 **`"vendor-official"`** —— ★ **不改这一行, CB-06 永远判未验** |
| Q4.2d 版本块分区 | `partition_layout.partitions[]` 里的 `version_block` 条目 (名字/大小) | — |
| Q4.2f A/B 命名 | `partition_layout.partitions[].slot` 的取名 (`"a"`/`"b"` 或对方规则) + `active_slot` | — |
| Q4.3 容量结论 | 转项目总工裁决 (若结论是"必须 eMMC", 则**板宽 / 结构 / BOM 要连带重算** —— 这是 hw-lead 的活, 由项目总工转) | — |

> ★ **单位陷阱**: 官方 `parameter.txt` 的分区大小通常以**扇区 (512B)** 计, 而我们 `partition_layout.partitions[].size` 是**字节**。转录时**必须换算**, 否则整张表错 512 倍。

---

## 5. 附加问题 (换芯后必须补问的)

### 5.1 RK3588 线路的公开信息 (★ 芯片级工具链是公开的 —— 不要让对方重复回答)

> 以下为 **[官方/公开文档]** 事实, 已在 2026-10-29 独立查证。**用途是让我们知道该问什么**, 不是本项目的真值。

| 公开事实 | 出处 | 对我们的意义 |
|---|---|---|
| 瑞芯微 USB 下载工具 = **`rkdeveloptool`** (Linux/macOS, 开源 `rockchip-linux/rkdeveloptool`) + **`RKDevTool`** (Windows) | 瑞芯微开源仓库 + ROCK 5 官方 wiki | ★ **P2 大概率不用问芯片级工具名**, 要问的是"**你们这块板**的固件包与分区表" |
| 典型用法: `rkdeveloptool db <loader.bin>` → `wl <起始扇区> <镜像>` → `rd` (复位) | 同上 | 直接可映射成 `board_test.flash.cmd` 的 argv 数组 |
| Maskrom 态枚举示例: **VID 0x2207**, PID **0x330c** (RK3399) / **0x350a** (RK3566) / **0x350b** (RK3588 ROCK 5B) —— **PID 随 SoC/态而变** | 各板厂 wiki (PINE64 / Radxa / Bootlin) | ★ **P3 必须问"你这块板"的实际 PID**, 且**三个态要分别给**; 公开值**不能直接抄进配置** |
| fastboot 态: `fastboot -i 0x2207 devices` (VID 0x2207, PID 0x0006 见于瑞芯微 wiki) | 瑞芯微 wiki | 备选分支 T2 的可行性 |
| Maskrom 的两个 USB 控制请求 `0x471` (载 SRAM) / `0x472` (载 DRAM) | Bootlin 技术文 | 理解"bootROM 兜底"机制 —— 对应 Q1.1g |
| 分区表用 `parameter.txt` (`TYPE: GPT` + `CMDLINE: mtdparts=...`) | 瑞芯微 SDK / 板厂文档 | ★ **P4 的单位陷阱来源** (扇区 512B) |
| U-Boot 里 `rockusb 0 mmc 0` 可进 Loader 态 | PINE64 wiki | 方式 C (USB 触发) 的可行性 |

> ★ **这些公开值只能当"提问的靶子"**。配置里填的必须是**对方针对我们这块板给的**或**我们在自己板子上抓的** (`source` = `vendor-official` / `measured`)。

### 5.2 线路 A (RK3588 基线) 必问的 4 件事

| # | 问什么 | 为什么 |
|---|---|---|
| A-1 | 贵方提供的是**核心板 (SOM)** 还是**整板**? 若是核心板: 存储/BOOT 按键/USB PHY **是不是板载在核心板上**? | ★ 决定 P1/P3/P4 到底是模组厂定还是我们自己在板子上做 —— **这直接决定问谁** |
| A-2 | 核心板的 **SPI-NOR / eMMC** 配置与容量, 以及**预烧**了什么 (loader? uboot? parameter.txt?) | 决定"拿到板子时能不能直接进下载模式" |
| A-3 | 贵方提供的 **loader 文件**与**分区表**的对应关系, 以及我们**改 kernel/rootfs/app/model** 时需要重刷哪些分区 | ★ 决定 BR-06 的"全量刷写"到底刷哪几个分区 |
| A-4 | BOOT/Recovery 按键是否在核心板上引出 (位号)? 与我们侧键是否冲突? | 对应 Q1.2c (售后手势冲突) |

### 5.3 线路 B (ARS45 基线) 必问的 4 件事

| # | 问什么 |
|---|---|
| B-1 | 存储介质与容量 (对 Q4.1) |
| B-2 | 官方分区表 + 版本块格式 (对 Q4.2) |
| B-3 | bootloader 校验机制 + A/B 回滚阈值 + secure boot (对 Q1.3) |
| B-4 | 下载工具版本 + 固件包交付形式 (对 Q2) |

---

## 6. 与既有 needs_from 的对应关系 (不要重复问)

> `state/fragments/sw.yaml` 里 sw-lead 已登记的对外需求 (全部 `waiting_on=vendor`, 经项目总工转达)。本清单是**这些需求的具体化**, 不是新需求。

| needs_from key | to | 本清单对应节 | 状态 |
|---|---|---|---|
| `fw_boot_entry_cond` | vendor | §1 (Q1.1 / Q1.3) | 已登记, due 2026-10-29 **已逾期** |
| `fw_vendor_toolchain` | vendor | §2 (Q2.1 / Q2.2) + §4 (Q4.2 分区表) | 已登记, due 2026-10-29 **已逾期** |
| `fw_usb_boot_phy` | vendor | §3 (Q3.1 / Q3.2) | 已登记, due 2026-10-29 **已逾期** |
| `sw_usb_phy_spec` | vendor | §3 (Q3.1c VBUS / Q3.1d 速率) | 已登记 (TBD-10 追加问), due 2026-10-29 **已逾期** |
| `fw_boot_storage_bom` | **hw-lead** | §4 (Q4.1 / Q4.3) | 已登记, due 2026-10-29 **已逾期** |
| `fw_boot_mode_hw` | **hw-lead** | §1 (Q1.2 测试点/独立按键) | 已登记, due 2026-10-29 **已逾期** |
| `fw_s2_test_gear` | **main** | 器材采购 (逻辑分析仪 / USB 协议分析仪 / SPI-NOR 空板) | 已登记, due 2026-10-29 **已逾期** |

> ★ **同时提醒 hw-lead 侧**: `fw_boot_storage_bom` 与 `fw_boot_mode_hw` 是 **hw-lead 的活** (不是原厂), 项目总工发信时可**并行**催这两条 —— 它们和 §1/§4 的原厂回复是**互补**关系, 不互相等。

---

## 7. 回填自检 (收到回复后照着跑)

```bash
cd projects/smart_glasses

# ① 参数齐备性 (期望 rc=0; 会逐条列出差的可执行件)
bash SW/tools/s2_board_run.sh --preflight --config SW/tools/s2_rescue_config.json

# ② 判定器自测 (期望 rc=0, 6/6 —— 含"通用示例不算证据"这条反例)
python3 SW/tools/s2_board_judge.py --selftest

# ③ 检查 4 个参数确实都 DONE 了 (期望 4 行全 DONE, 无 TODO)
python3 - <<'EOF'
import json
d = json.load(open('SW/tools/s2_rescue_config.json', encoding='utf-8'))
for k, v in d['params'].items():
    print(f"{k:<22} status={v.get('status'):<6} filled={v.get('value') not in (None,'',[],{})}")
EOF

# ④ ★ 检查 usb_signatures 里没有 generic-example (期望 0 行 generic-example)
python3 - <<'EOF'
import json
d = json.load(open('SW/tools/s2_rescue_config.json', encoding='utf-8'))
bad = [e for e in d['usb_signatures']['entries'] if e.get('source') == 'generic-example']
print("generic-example 条数 =", len(bad), "  (必须为 0)")
EOF

# ⑤ ★ 检查分区表已换真值 (期望 source 不是 placeholder-推算)
python3 -c "import json;print(json.load(open('SW/tools/s2_rescue_config.json'))['partition_layout']['source'])"
```

---

## 8. 本清单的边界声明

| # | 声明 |
|---|---|
| 1 | ★ **sw-lead 不直接联系原厂 / 供应商 / 模组厂**。本文件是**草稿**, 外发由项目总工执行。 |
| 2 | ★ 本清单**不含任何编造的参数值**。§5.1 的公开事实全部标了出处, 且明确写了"**不能直接抄进配置**"。 |
| 3 | ★ 4 个 0 数据项在对方书面回复前, `SW/tools/s2_rescue_config.json` 里**一律 `value: null` / `status: "TODO"`** —— 不许先用公开值或通用示例顶上去。 |
| 4 | §0.2 的**换芯分叉**是本清单的前置条件 —— 分叉没定就发信, 问错对象, 白等一轮。 |
| 5 | 本清单**不拍板**任何选型 (存储类型 / 工具链 / 分区方案) —— 只把问题组织到能一次问完、能落地成字段。 |
