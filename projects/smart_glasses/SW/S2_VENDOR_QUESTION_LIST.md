# S2 救砖链路 · RK3576 模组厂问询清单 (P1 / P2 / P3 / P4)

> **文件**: `SW/S2_VENDOR_QUESTION_LIST.md` **v2.0 (2026-11-01)** · ISS-123 (sw-lead)
> **上一版**: v1.0 (2026-10-30, ISS-120) —— 按 **ARS45 原厂** 口径写的, ★**整版作废**
> **性质**: ★ **给项目总工的外发草稿** —— sw-lead **不直接联系模组厂 / 原厂 / 供应商**
> **落点**: 拿到回复后, 由项目总工转录进 `SW/tools/s2_rescue_config.json` (每节都写了"填进哪个字段")
>
> **一句话**: ★ **基线已定 = 瑞芯微 RK3576** ⇒ 问询对象从"ARS45 原厂"变成"**RK3576 模组厂**";
> 每个问题都写死了"问什么 / 要什么格式回 / 回填哪个字段" —— 一次邮件问完, 回复能直接落到字段。

---

## 0. 使用说明 (给项目总工)

### 0.1 ★ 外发纪律

| # | 规则 |
|---|---|
| 1 | **sw-lead 不直接对外**。本文件是**草稿**, 外发由项目总工执行。 |
| 2 | ★ **ARS45 / AR9481 / 酷芯微 全部作废** (老板 10-29 19:20 拍板) ⇒ **`state/outbox/` 里的酷芯微代理线草稿一律不发**; 本清单的**对象、术语、格式**已全部改成 RK3576 模组厂口径。 |
| 3 | 本清单里已登记过的条目**不要重复问** —— 见 §6 "与既有 needs_from 的对应关系"。 |
| 4 | 回复**必须是书面的**(邮件正文或 PDF)。口头/会议结论请项目总工当场落成一段文字转录, 否则仍按 [0数据] 处理。 |
| 5 | 收到回复后: 填进 `SW/tools/s2_rescue_config.json` 对应字段 → 跑 §7 的回填自检 → 再跑 `--preflight` 复核。 |
| 6 | ★ **通用示例不是回复**。对方说"类似 RK3588 的那种做法"不算数, 要具体到 **VID:PID / 命令 / 分区名 / 数值 / 单位**。 |

### 0.2 ★ 口径基线 (v2.0 与 v1.0 的根本差别)

| # | 项 | v1.0 (作废) | **v2.0 (本版)** | 依据 |
|---|---|---|---|---|
| 1 | SoC 基线 | ARS45 (酷芯微) | ★**瑞芯微 RK3576** (FCCSP698L, 16.1×17.2mm, pitch 0.6, 698 球, 6 TOPS) | `PROJECT_TRACKER.md` §(1.46)/(1.47) · `HW/CHIP_SELECTION_DECISION.md` §0 (ISS-118 T4 翻案: RK3588 在 30mm 板宽内摆不下 ⇒ 换 RK3576) |
| 2 | 问询对象 | ARS45 原厂 / 方案商 | ★**RK3576 模组厂** (提供**这块板**的 BOOT 通路 / 分区表 / 存储配置的一方) | 芯片级参数公开, 但"**你这块板**"的差异是模组厂定的 |
| 3 | 术语 | "进 BOOT 模式" | ★ **Maskrom / Loader (Rockusb) / fastboot** 三态 + `SARADC_VIN0_BOOT` | 瑞芯微官方术语 (见 §5.1) |
| 4 | 下载工具 | "原厂下载工具" | ★ **`rkdeveloptool` (Linux/macOS) / `RKDevTool` (Windows) / `upgrade_tool`** | 瑞芯微开源工具链 (见 §5.2) |
| 5 | 分区表单位 | "★必须换算, 否则差 512 倍" | ★★ **变成必答题**: 问"**你们的 `parameter.txt` 用哪种方言?** 十六进制扇区 / 后缀 K-M-G / 其他" + "**1 扇区 = 多少字节?**" | 见 §4.3 —— **这是 ISS-123 的核心防错点** |
| 6 | 版本块 magic / 版本串前缀 | 隐含写死 `AR45` / `ARS45-SW ` | ★ **已抽成可配置** (`identity.version_block_magic` / `identity.version_str_prefix`), 本单已把默认值与**依据**写进配置 | ISS-123 · `SW/tools/s2_rescue_config.json` |

> ★ **仍待确认的一条 (不是分叉, 是要问的第一句)**: **模组厂到底提供的是核心板 (SOM) 还是整板/板级设计方?**
> —— 见 §5.3 的 A-1。若对方是**芯片原厂代理**而非模组厂, 本清单的 §1/§3/§4 需要转成"你们的参考设计是怎么做的"。
> **不脑补**: 本单按"**模组厂**"写, 并把 A-1 放在清单最前面问。

### 0.3 问询优先级

| 优先级 | 问什么 | 为什么急 |
|---|---|---|
| **P0** | §4 P4 (启动存储 + 分区表 + ★**单位**) + §2 P2 (下载工具) | 这两项不定, **板子回来了也刷不回去** ⇒ 量产一票否决项直接卡死 |
| **P1** | §3 P3 (USB 枚举特征 + ★专用 MaskROM USB 口) + §1 P1 (进 Maskrom/Loader 的硬件条件) | 这两项不定, **连"进没进下载态"都无法机械判定** ⇒ CB-01/BR-03~05 全判未验 |
| **P2** | §5 附加问题 (核心板 vs 整板 / 存储介质 / 固件包交付形式 / 校验与回滚) | 影响返修流程与产线工位设计 |

---

## 1. P1 · `BOOT_ENTER_SPEC` — 进 Maskrom / Loader (下载态) 的硬件条件

> **卡住什么**: `SW/S2_BOARD_TEST_CHECKLIST.md` §3 的全部时序/电平; BR-03 / BR-04 (进下载态); BR-05 (工具识别)。
> **needs_from key**: `fw_boot_entry_cond` (vendor) + `fw_boot_mode_hw` (hw-lead)
> **状态**: **[0数据]** —— 模组厂书面回复前一律留空。
> ★ **口径**: RK3576 的"BOOT"不是普通 GPIO, 是 **`SARADC_VIN0_BOOT`** (一个 ADC 引脚, 用**电压档位**选启动优先级) ⇒ 问题必须问**电压门限**, 不能只问"高低电平"。

### 1.1 问什么

**Q1.1** 进入 **Maskrom / Loader (Rockusb) 模式**的硬件触发条件:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | ★ 板上有几颗**下载态**入口? 分别叫什么丝印/位号? | 列出全部 (如 `MASKROM 按键` / `RECOVERY 按键` / `BOOT_SARADC_VIN0 测试点`) |
| b | ★ `SARADC_VIN0_BOOT` 这个引脚在**你们这块板**上怎么用? | 是否引出测试点? 位号/丝印? 是否与按键/跳帽关联? |
| c | ★★ **`SARADC_VIN0_BOOT` 的电压门限** | 各档位对应的**电压范围 (mV)** 与对应的**启动优先级/行为** (哪档 = 只读 SPI-NOR / 哪档 = eMMC 优先 / 哪档 = 强制 Maskrom) —— ★ 我们要照着这个值选**产线跳线/治具** |
| d | 触发流程: 断电状态按住哪个键? 顺序 (先按住 → 上电 / 上电后按住 → 再按 RESET)? | 逐字写清顺序 |
| e | **RESET 键**的脉冲宽度要求 | 最小/典型/最大 (ms) |
| f | BOOT 条件需要**保持多久** | 最小保持时间 (ms) |
| g | 是否支持**不按键**直接进 Maskrom | 有 / 无; 若有, 条件是什么 (拔存储? 短接某个点?) |
| h | 是否支持**已开机状态下**用软件进入 | 有 / 无 (例: U-Boot 里 `rockusb 0 mmc 0`) |
| i | ★★ **bootROM 的兜底行为**: 所有存储上都没有合法 bootloader 签名时, RK3576 会**自动进入 Maskrom** 吗? | 是 / 否 —— ★ 我们理解瑞芯微的通用行为是"是" (MaskROM 代码烧在芯片内部 ROM, 不可擦除), 但**你们这块板**有没有什么东西会**挡住**这条兜底路径 (例如 SPI-NOR 上写死了会跳过的引导、或某个硬件开关)? |
| j | 是否有**超时自动进下载态**的机制 | 有 / 无; 超时值 (s) |

**Q1.2** 关于**产线工位**的补充 (量产一票否决项的落地条件):

| # | 问什么 |
|---|---|
| a | 产线上推荐用哪种进下载态的方式? **跳线到测试点** / **按键组合** / **其它**? |
| b | 贵方板子上**是否已引出**该测试点或独立按键? 丝印/位号是什么? |
| c | 是否**必须**按住侧键才能进下载态? (★ 我们的侧键已被售后手势占用: 长按 3s = 显示版本号, 长按 10s = 关机 —— 若复用同一颗键, 用户误触就会把眼镜送进下载态) |

**Q1.3** 关于**校验与回滚** (和 S2 一起问, 一次问完):

| # | 问什么 |
|---|---|
| a | bootloader 启动时是否校验分区 CRC / SHA256? 不通过时**具体行为** (停住 / 回滚 / 停在下载态)? |
| b | **A/B 槽自动回滚**是否可配? **尝试次数阈值**是多少? |
| c | **secure boot / 镜像签名**是否启用? 密钥如何管理 (烧进 OTP / efuse / 还是软配置)? |

### 1.2 什么格式回 (要对方按这个格式回, 别让他写散文)

```
【Q1.1 进入 Maskrom / Loader (Rockusb)】
下载态入口清单            ____________ (按键/测试点/丝印/位号, 逐个列)
SARADC_VIN0_BOOT 是否引出   是 (位号____) / 否
SARADC_VIN0_BOOT 电压门限   档位1 ____mV→____ ; 档位2 ____mV→____ ; 档位3 ____mV→____
                            (请注明每档对应的启动优先级/行为)
进入下载态操作顺序        ____________ (例: 断电→按住 MASKROM→上电→见 RKDevTool
                            "Found One MASKROM device"→松手)
RESET 脉冲宽度 (ms)        最小____ 典型____ 最大____
BOOT 条件最小保持 (ms)      ____________
无需按键直接进 Maskrom     支持 / 不支持 (条件: ____________)
已开机能否软件进入          能 (命令____) / 不能
超时自动进下载态           支持 / 不支持, 超时____秒
★ bootROM 自动兜底进 Maskrom  是 / 否  (若"否", 请说明砖了如何恢复;
                            若"是", 请说明贵方板上有什么会挡住这条路径)

【Q1.2 产线工位】
推荐进下载态方式           跳线测试点 / 按键组合 / 其它____
测试点丝印/位号            ____________
是否已引出独立下载按键       是 (位号____) / 否
是否必须用侧键             是 / 否

【Q1.3 校验与回滚】
bootloader 分区校验        CRC / SHA256 / 无
校验失败行为               ____________
A/B 自动回滚               可配 / 不可配, 尝试次数阈值____
secure boot / 签名          启用 / 不启用, 密钥管理方式____________
```

### 1.3 拿到后填进 `s2_rescue_config.json` 的哪个字段

| 回复内容 | 填进字段 | 写法 |
|---|---|---|
| Q1.1 整体答复摘要 | `params.P1_BOOT_ENTER_SPEC.value` | 一段摘要字符串; 同时把 `params.P1_BOOT_ENTER_SPEC.status` 改成 **`DONE`**, 并加 `"source": "vendor-official"` |
| Q1.1a/b 下载态入口 | `boot_enter.boot_pin_name` | 字符串, 如 `"SARADC_VIN0_BOOT"` |
| Q1.1c 电压门限 | ★ **新增**: `boot_enter.boot_pin_level` (填 `"high"`/`"low"`/具体档位名) + `boot_enter.boot_voltage_mv` (对象: 档位→mV) | ★ **本项在 v1.0 里没有** —— RK3576 用 ADC 选档, 只记"高/低"不够 |
| Q1.1d/f 时序 | `boot_enter.keys` (数组) / `boot_enter.t0_hold_boot_ms` / `boot_enter.t1_reset_pulse_ms` / `boot_enter.t2_release_all_ms` | 整数, 单位 ms |
| Q1.1g/h 方式与超时 | `boot_enter.method` (`"A"` 跳线 / `"B"` 按键 / `"C"` 软件) + `boot_enter.t3_enum_timeout_s` | 字符串 / 整数秒 |
| Q1.2a/b 测试点 | `boot_enter.boot_pin_name` 注释 + 交接单 B5 转项目总工转 hw-lead (`fw_boot_mode_hw`) | — |
| Q1.3 校验/回滚 | 交接单 B5 转项目总工裁决 (影响 BR-11/BR-12 的预期行为) | — |

> ★ `boot_enter.t3_enum_timeout_s` 现在是 15, 那是 [推算] 值 (给 USB 枚举 + 工具握手留余量), **模组厂给了就改成对方的值**。

---

## 2. P2 · `DL_TOOL` — RK3576 下载工具与固件包

> **卡住什么**: BR-05 (工具识别) / BR-06 (全量刷写) —— **没工具, 板子回来了也刷不回去**。
> **needs_from key**: `fw_vendor_toolchain` (vendor)
> **状态**: **[0数据]**

### 2.1 问什么

**Q2.1** 下载工具本体:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | 你们推荐哪个工具? | `rkdeveloptool` (Linux/macOS) / `RKDevTool` (Windows) / `upgrade_tool` / 贵方封装版 —— 请给**准确名称 + 版本号** |
| b | **版本号与下载链接** | 精确版本 + 链接 (要能下到、能校验 sha256) |
| c | 支持**哪些平台** | Windows / Linux / macOS, 各版本号 |
| d | 是否**可脚本化批量刷写** (命令行) | 可 / 不可; 若是可, 请给**完整命令行示例** (含参数含义) |
| e | 支持的**存储类型** | eMMC / SPI-NOR / SPI-NAND / SD, 各自分区大小限制 |
| f | 刷写**前是否自动备份**现有分区 | 是 / 否; 若是, 备份文件放哪、怎么取回 |
| g | ★ 工具要**管理员权限**吗? (Linux 下 udev 规则要不要装?) | 要 / 不要; 若要, 请给 udev 规则文件 |

**Q2.2** 固件包与分区表:

| # | 问什么 |
|---|---|
| a | 固件包的**交付形式** (整包 `update.img`? 分区镜像? `loader` + 各分区?) —— 请给一份**实际的目录清单** |
| b | ★★ **官方分区表**的定义文件 (例: `parameter.txt`) 能否提供? ★ 请给出**对应贵方目标存储容量**的那一版 |
| c | ★★★ **`parameter.txt` 里 `CMDLINE: mtdparts=...` 的尺寸单位是哪一种? (三种可能, 请勾选一种并给一个例子行)** | ☐ 十六进制扇区 (`0x00002000@0x00004000(boot)`, 单位 = 扇区) ☐ 后缀 K/M/G (`8M@9M(boot)`, 单位 = 字节, M=MiB) ☐ 其它 (请贴一行例子 + 说明单位) —— ★ **并请注明: 1 扇区 = 多少字节?** |
| d | 分区**名称与顺序**、每个分区的**大小与对齐**、各分区对应的**镜像文件名** |
| e | **版本块 / 元数据分区** (保存固件版本串、SN、标定 ID 的那个分区) 在贵方分区表里叫什么? **格式**是什么 (二进制布局 / 文本)? 我们要在里面写版本信息 —— ★ **若贵方已有固定格式, 请给布局说明或样例** |
| f | 刷写后如何**回读校验**? 工具本身有没有校验命令? 返回码含义是什么? |
| g | ★ `parameter.txt` 里的 `MAGIC: 0x5041524B` 是什么字段? (★ **我们自己的版本块 magic 是另一回事**, 别混) | 请说明该字段含义与是否必填 |

**Q2.3** bootloader 与固件命名 (供追溯):

| # | 问什么 |
|---|---|
| a | `loader` / `MiniLoaderAll.bin` / `uboot` / `boot` / `recovery` / `rootfs` 各对应哪个分区? 命名规则与版本号格式? |
| b | 是否有**固件签名校验**; 我们自己编译的镜像能否被工具接受 (还是必须用贵方签名的包)? |
| c | ★ 我们改 **kernel / rootfs / app / model** 这几个分区时, 需要重刷哪几个? 需不需要连 `loader` 一起重刷? |

### 2.2 什么格式回

```
【Q2.1 工具】
工具名称             ____________
版本号               ____________
下载链接             ____________ (附 sha256)
支持平台             Windows____ / Linux____ / macOS____
可脚本化             可 / 不可
命令行示例           ____________ (完整命令 + 参数含义)
支持存储             eMMC / SPI-NOR / SPI-NAND / SD (各容量上限: ____________)
自动备份             是 / 否, 备份路径____________
需要管理员权限/udev   是 (规则文件____) / 否

【Q2.2 固件包与分区表】
固件包形式           整包 update.img / 分区镜像 / loader+分区 / 其它____
实际目录清单         (请直接贴 tree 输出)
官方分区表文件        文件名____________ (可提供? 是 / 否)
适用存储容量         ____________
★ mtdparts 尺寸单位   ☐十六进制扇区 ☐后缀K/M/G ☐其它____  (请贴一行例子)
★ 1 扇区 =           ____ 字节      ← ★ 必填
分区名称与顺序       (请贴表格: 名称 | 起始 | 大小 | 对齐 | 镜像文件名)
版本/元数据分区      名称____________, 大小____, 格式____________ (布局说明/样例)
回读校验             有 / 无, 命令____________, 返回码含义____________
parameter.txt MAGIC  含义____________, 是否必填____________

【Q2.3 命名与签名】
loader/MiniLoader/uboot 命名规则 ____________
固件签名校验         有 / 无; 自编镜像是否可被接受: 可 / 不可
改 kernel/rootfs/app/model 需重刷 ____ (是否需连 loader 一起)
```

### 2.3 拿到后填进 `s2_rescue_config.json` 的哪个字段

| 回复内容 | 填进字段 | 写法 |
|---|---|---|
| Q2.1 整体摘要 | `params.P2_DL_TOOL.value` + `status` → **`DONE`** + `"source": "vendor-official"` | 摘要字符串 |
| Q2.1a/c 工具名与版本 | `board_test.tools[].name` / `.version_cmd` | `{"name":"rkdeveloptool","version_cmd":["rkdeveloptool","--version"]}` 之类; 脚本会自动取版本, 取不到记 [0数据] |
| Q2.1d 全量刷写命令 | ★ `board_test.flash.cmd` | **argv 数组** (不走 shell 字符串): `["rkdeveloptool","db","loader.bin"]` + `["rkdeveloptool","wl","0","update.img"]` 两步 —— 占位符由我方脚本按现场替换 |
| Q2.1f 备份命令 | `board_test.flash.backup_cmd` | argv 数组; 无备份能力就填 `null` (脚本会跳过) |
| Q2.2a 固件包目录 | `partition_layout.partitions[].file` | 字符串 |
| ★★ Q2.2b/c 分区表 | ★ **整段替换** `partition_layout` + ★ **`sector_size`** + ★ **`vendor_size_unit`** + ★ **`provenance`** | ★ 见 §4.3 的四步换算法 —— **手抄必错 512 倍**, 走 `s2_partition_convert.py` |
| Q2.2e 回读校验 | ★ `board_test.verify.readback_cmd` + `board_test.verify.readback_target` | argv 数组 + 输出文件路径 |
| Q2.3 命名规则 | 交接单 B5 (影响 §3.5 追溯字段) | — |

---

## 3. P3 · `USB_PHY` — USB 下载通路 + 下载态枚举特征

> **卡住什么**: CB-01 (刷完重新枚举)、BR-05 (工具识别)、以及**整个 S2 链路能否成立** —— 若这块板没有可用的 USB Device 通路, 救砖链路从根上不成立。
> **needs_from key**: `fw_usb_boot_phy` (vendor) + `sw_usb_phy_spec` (vendor)
> **状态**: **[0数据]**

### 3.1 问什么

**Q3.1** 物理层:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | ★★ **这块板有没有"专用 MaskROM USB 口"?** | 有 / 无 —— ★ 瑞芯微的通用设计是"**Maskrom 模式只走专用 USB 口**", 而模组/载板常常**只把一个 USB 口引出来** ⇒ ★ **这是本项最高优先级的一条**: 若只有一个 USB 口, 它是不是 Maskrom 专用口? |
| b | 板上共引出几个 USB 口? 各自走 SoC 的哪个控制器/引脚? | 列出 (USB3 / USB2 OTG / USB2 host) |
| c | SoC 的 USB 控制器**有没有 Device 模式** (能枚举成 USB 从设备)? | 有 / 无; 是 OTG 还是纯 Host |
| d | **有没有独立的 USB Device PHY**? | 有 / 无 —— ★ 若"无", 救砖链路的**实现方式要整体重做** |
| e | 走的是 **USB 2.0 (FS/HS)** 还是 **USB 3.0**? | 明确速率 (★ Maskrom 走 USB2 还是 USB3, 请明确) |
| f | **VBUS** 的处理方式 | 芯片侧有没有 VBUS 检测脚? 母座 VBUS 直连还是经过电源开关/分压? |
| g | USB **D+/D−** 是否经过 ESD/滤波器件, 是否共用充电通路 | 简述 |
| h | ★ 我们会在**跨铰链**位置用 USB 做**救援/售后**通道 (量产态是镜脚有线) ⇒ 问: **跨铰链那段走的是哪个 USB 控制器? 能进 Maskrom 吗?** | 明确 |

**Q3.2** 协议与枚举特征 (★ 最关键, 要具体值):

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | 支持哪些**下载协议** | Rockusb / fastboot / DFU / 贵方私有 / 无 |
| b | ★★ **下载态的 USB VID:PID** | **精确到 4 位十六进制**, 并**分别给全三个态**: **Maskrom 态** / **Loader (Rockusb) 态** / **fastboot 态** —— ★ 这三个 PID 通常**不同** |
| c | **正常态**的 USB VID:PID (我们用它做"刷完后回到正常态"的比对基线) | 精确到 4 位十六进制 |
| d | USB **product / manufacturer** 字符串 (下载态与正常态) | 原文 |
| e | 下载态的 **Serial Number** 字符串格式 | (我们用它做板卡 SN 追溯) |
| f | 是否支持 **ADB**? | 支持 / 不支持; 若支持, 正常态能否连上 (我们有一个 `mode=prod` 时要"插线无 adb 设备"的安全规则) |
| g | ★ **`rkdeveloptool ld` 在你们这块板上的典型输出** | 请贴一行原文 (形如 `DevNo=1 Vid=0x____,Pid=0x____,LocationID=___ Maskrom`) —— ★ 这是我们做**机械判定**要匹配的串 |

**Q3.3** 枚举行为的边界条件 (不问清楚, 现场会翻车):

| # | 问什么 |
|---|---|
| a | 下载态是否**必须**同时满足 BOOT 条件 + 上电? 能否在**已开机状态**下用软件进入? |
| b | 从建立 BOOT 条件到 PC 上能枚举出设备, 典型/最大耗时? (我们用 15s 作超时, 是 [推算] 值) |
| c | USB 枚举**是否需要 VBUS 供电** (即必须插着 PC 才能进下载态)? |
| d | 有无**已知失败场景** (线材 / 供电 / 端口位置 / hub) 需要我们规避? |

### 3.2 什么格式回

```
【Q3.1 物理层】
★ 专用 MaskROM USB 口    有 / 无  (若"无", 板上唯一那个 USB 口是不是 Maskrom 口: 是/否)
板上 USB 口清单          口1: 控制器____ 引脚____ ; 口2: ... ; (共____个)
USB Device 模式         有 / 无 (OTG / 纯 Host)
独立 USB Device PHY     有 / 无            ← ★ 最高优先级
USB 速率                 USB2.0 FS / USB2.0 HS / USB3.0
Maskrom 态走 USB2 还是 USB3  ____
VBUS 处理                芯片侧有 VBUS 检测脚? 是 / 否; 母座 VBUS 直连 / 经开关 / 经分压
D+/D- 拓扑               ____________
跨铰链那段 USB           控制器____ ; 能进 Maskrom 吗: 能 / 不能

【Q3.2 协议与枚举特征】
下载协议                Rockusb / fastboot / DFU / 私有____ / 无
★ 下载态 VID:PID         Maskrom: ____:____   Loader: ____:____   fastboot: ____:____   其它: ____:____
正常态 VID:PID           ____:____
product 字符串 (下载态)   ____________
product 字符串 (正常态)   ____________
manufacturer             ____________
Serial Number 格式       ____________
ADB 支持                支持 / 不支持; prod 模式下能否连上: 能 / 不能
★ rkdeveloptool ld 典型输出  (请贴一行原文) ____________________

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
| ★ Q3.2b **下载态 VID:PID** | ★ `usb_signatures.entries[]` | **每个态一条**, 例: `{"vid":"2207","pid":"XXXX","label":"Maskrom 态 (模组厂给的)","source":"vendor-official"}` —— ★ `source` **只允许** `vendor-official` 或 `measured`; **绝不许留 `generic-example`** |
| Q3.2c 正常态 VID:PID | 无处可填 (它是**基线**, 由现场实测 `s2_step0_normal.json` 产出) | ★ 但**可以**先写进交接单 B5, 供现场比对参考 |
| Q3.2d/e 字符串 | 交接单 B5 (影响 CB-01 的判定细则) | — |
| Q3.2f ADB | `board_test.checks` 增补 `"adb_supported": true/false` (可选键) | — |
| Q3.3b 枚举耗时 | `boot_enter.t3_enum_timeout_s` | 整数秒 (把 15 这个 [推算] 值换成实测值) |
| ★ Q3.1d **无独立 PHY** | ★ **不填任何字段** —— 直接升级为**阻断项**, 转项目总工裁决 (救砖链路实现方式要整体重做) | — |

> ★ **回填后自检**: `python3 SW/tools/s2_board_judge.py --selftest` 里 T4 用例已验证 —— 命中 `generic-example` 签名时 CB-01 **判未验**, 不会被通用示例蒙混过关。

---

## 4. P4 · `BOOT_STORE` — 启动存储类型/容量 + 官方分区表 (★★ 单位是本项核心)

> **卡住什么**: 整个 §4 分区方案 + BR-06 (刷写) / BR-07 (回读) / CB-02 / CB-06; 也是 **SW/FLASH_AND_VERSION.md §4.1 推荐 C 的成立条件**。
> **needs_from key**: `fw_vendor_toolchain` (vendor) + `fw_boot_storage_bom` (hw-lead)
> **状态**: **[0数据]**
> ★★ **本项是 ISS-123 的核心**: 官方表按**扇区 (512B)** 计, 我方内部按**字节**计 ⇒ **差 512 倍**。这个错**不会报错**, 只会静默写错 ⇒ 已做成**机械守卫** (§4.3)。

### 4.1 问什么

**Q4.1** 存储本体:

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | 启动存储**类型** | eMMC / SPI-NOR / SPI-NAND / SD / UFS |
| b | **容量** | 明确值 (e.g. 16GB / 128MB) |
| c | 若是 eMMC | **颗粒型号**、**HS200/HS400** 速率档位 |
| d | 若是 SPI-NOR | **型号 + 容量** (我们 [推算] 这套分区表需要 **≥128MB**, 64MB 装不下 —— 请确认能不能给到 128MB) |
| e | ★ **rootfs 体积上限** | 多少 MB 以内必须用 NOR? 换芯后 rootfs 实际会多大? (这是选型的总分叉点) |
| f | 存储是**板载**还是**可更换模组**? | 板载 / 模组 (模组的话, 换存储要不要重新刷 loader?) |
| g | ★ **启动顺序 (boot priority)** | SPI-NOR / eMMC / SD 的优先级顺序, 以及 `SARADC_VIN0_BOOT` 电压档位怎么改这个顺序 |

**Q4.2** 分区表 (★ 本项的真正目的):

| # | 问什么 | 要的具体答案 |
|---|---|---|
| a | **官方分区表定义文件**能否提供 (例: `parameter.txt`)? | 请给**针对上面容量**的那一版 |
| b | ★★ **单位与方言** | ★ `mtdparts` 的尺寸是 **十六进制扇区** / **后缀 K/M/G** / 其它? ★ **1 扇区 = 多少字节?** |
| c | 分区**名称 / 顺序 / 大小 / 对齐** | 完整表 |
| d | 分区表里**有没有预留"版本/元数据"分区** | 名称 + 大小 + 格式 |
| e | bootloader / loader / u-boot / boot / recovery / rootfs / userdata 各对应哪个分区 | 对照表 |
| f | **A/B 双槽**是否支持? 分区名怎么带槽位 (后缀 `_a`/`_b` 还是别的)? | 方案 + 命名规则 |
| g | 官方**整包镜像**能否给出**分区级 CRC 表** (每分区 sha256) | 能 / 不能 |
| h | ★ 官方分区表的**对齐要求**是多少? (瑞芯微通用要求是 32KB/64 扇区) | 请给贵方这一版的要求 |

### 4.3 ★★★ 单位换算: 四步法 (★ 手抄必错 512 倍)

> **为什么要专门写一节**: 官方的 `parameter.txt` 里分区尺寸是**扇区**, 我方 `partition_layout.partitions[].size` 是**字节**。
> 转录时漏乘 512 ⇒ 整张表**差 512 倍**, 而**它不会报错** —— 表照样"合法", 照样能写进 flash 文件, 只是写出来的东西完全不是那回事。
> ⇒ **所以我方已经把这件事做成机械守卫**, 不靠人肉小心。

**★ 收到官方表后的四步 (一条命令, 别手抄)**:

```bash
cd projects/smart_glasses

# ① 先看这份 parameter.txt 是哪种方言 (工具会自己判, 并警告)
python3 SW/tools/s2_partition_convert.py --parse <vendor_parameter.txt> \
        --sector-size <对方给的扇区字节数> --out /tmp/partitions.json

# ② 把结果粘进 s2_rescue_config.json 的 partition_layout, 并**同时**填:
#      "sector_size":        <对方给的扇区字节数>     ★ 显式参数
#      "size_unit":          "bytes"                  ★ 我方内部单位恒为字节
#      "vendor_size_unit":   "sector" (十六进制扇区方言) / "bytes" (后缀方言)
#      "expected_total_bytes": <换算后的合计字节数>
#      "provenance": {"converted": true,
#                     "converted_with_sector_size": <同上>,
#                     "converted_total_bytes": <同上>}

# ③ 跑守卫 (rc=0 = 无问题; 有 error ⇒ 拒绝写入/拒绝判过)
python3 SW/tools/s2_partition_convert.py --check SW/tools/s2_rescue_config.json

# ④ 再跑判定器自测, 确认没有把既有判据改松
python3 SW/tools/s2_board_judge.py --selftest
```

**★ 守卫会机械拦住什么 (两条 512 倍反例, 都已固化成自测)**:

| 错法 | 症状 | 抓它的判据 |
|---|---|---|
| **A: 扇区数当字节直接填** (÷512) | 合计从 86 MiB 变成 ~172 KiB | `TOTAL_MISMATCH_EXPECTED` (合计 ≠ 声明值) + `ALIGN_VIOLATION` (2048 B 不是 4096 的倍数) + `SECTOR_TABLE_NOT_CONVERTED` |
| **B: 字节数当扇区数再乘 512** (×512) | 合计从 86 MiB 变成 ~44 GiB | `TOTAL_EXCEEDS_DEVICE` (合计 > 存储容量) |

⇒ 对应的自测用例: `python3 SW/tools/s2_partition_convert.py --selftest` (T3~T8) 与 `python3 SW/tools/s2_board_judge.py --selftest` (T8~T10)。

### 4.4 什么格式回

```
【Q4.1 存储】
类型                  eMMC / SPI-NOR / SPI-NAND / SD / UFS
容量                  ____________
eMMC 颗粒/速率         ____________ (若非 eMMC 可空)
SPI-NOR 型号+容量       ____________
rootfs 体积上限        ____________ MB
板载 / 可换模组        板载 / 模组
启动优先级             SPI-NOR→eMMC→SD? 或 ____________ ; 由 SARADC_VIN0_BOOT 电压档位决定?

【Q4.2 分区表】
官方分区表文件          文件名____________ (可提供? 是 / 否)
★ mtdparts 尺寸单位     ☐十六进制扇区 ☐后缀K/M/G ☐其它____  (请贴一行例子)
★ 1 扇区 =            ____ 字节        ← ★ 必填
分区表                  (请贴完整表: 名称 | 起始 | 大小 | 对齐 | 镜像文件名)
版本/元数据分区          名称____________, 大小____, 格式____________
loader/uboot/boot/recovery/rootfs 对应分区  ____________
A/B 双槽                支持 / 不支持; 命名规则____________
分区级 CRC 表            能 / 不能
分区对齐要求             ____________ (瑞芯微通用 32KB/64扇区?)

【Q4.3 容量冲突】
128MB 及以上 NOR 方案     有 / 无 (型号____________); 若只能 64MB, 可压缩的分区: ____________
是否走 eMMC              是 / 否; 若是, 能否给 eMMC 官方分区表: 能 / 不能
```

### 4.5 拿到后填进 `s2_rescue_config.json` 的哪个字段

| 回复内容 | 填进字段 | 写法 |
|---|---|---|
| Q4.1 整体摘要 | `params.P4_BOOT_STORE.value` + `status` → **`DONE`** + `"source": "vendor-official"` | 摘要字符串 |
| ★★ Q4.2 分区表 | ★ **整段替换** `partition_layout` | `device_total_size` (字节) / `align` / `erase_block` / `crc_slots[]` / `partitions[]` (每条: `name` / `size` / `file` / `crc_slot` / `slot`) |
| ★★ Q4.2b 单位 | ★ `partition_layout.sector_size` (整数, 显式) + `partition_layout.size_unit` (`"bytes"`) + `partition_layout.vendor_size_unit` (`"sector"` / `"bytes"`) + `partition_layout.expected_total_bytes` | ★ 见 §4.3 四步法 |
| ★★ Q4.2b 换算留痕 | ★ `partition_layout.provenance` | `{"converted": true, "converted_with_sector_size": <同上>, "converted_total_bytes": <同上>}` |
| ★ Q4.2 分区表来源标记 | ★ `partition_layout.source` | 改成 **`"vendor-official"`** —— ★ **不改这一行, CB-06 永远判未验** |
| Q4.2d 版本块分区 | `partition_layout.partitions[]` 里的 `version_block` 条目 (名字/大小) | — |
| Q4.2f A/B 命名 | `partition_layout.partitions[].slot` 的取名 (`"a"`/`"b"` 或对方规则) + `active_slot` | — |
| Q4.2h 对齐 | `partition_layout.align` (我方默认 4096; 官方若要求 32768 就按官方的) | — |
| Q4.3 容量结论 | 转项目总工裁决 (若结论是"必须 eMMC", 则**板宽 / 结构 / BOM 要连带重算** —— 这是 hw-lead 的活, 由项目总工转) | — |

---

## 5. 附加问题

### 5.1 RK3576 芯片级公开事实 (★ 提问的靶子 —— 不要让对方重复回答公开信息)

> 以下为 **[官方/公开文档]** 事实, 2026-11-01 独立查证。**用途是让我们知道该问什么**, 不是本项目的真值。

| 公开事实 | 出处 | 对我们的意义 |
|---|---|---|
| ★★ RK3576 上电时读 **`SARADC_VIN0_BOOT`** 引脚的**电压**来决定启动优先级, 并判断是否请求进 Maskrom | Flipper One 文档 (RK3576 MaskROM 专页) | ★★ **P1 的核心**: 问的是**电压门限**, 不是"高/低电平" —— 这是 RK3576 特有的、v1.0 清单里没有的一条 |
| ★★ RK3576 的 MaskROM 代码**烧在芯片内部 ROM, 不可擦除**; 所有存储上都没有合法 bootloader 签名时, **自动进 Maskrom** 等 PC 下发指令 | 同上 | ★★ 回答了 Q1.1i (bootROM 兜底) ⇒ **"砖了还能不能救"原则上能** —— 但要问"你们板上有没有东西挡住这条路径" |
| ★★ Maskrom 模式**只走专用 MaskROM USB 口** | 同上 | ★★ **P3 的核心**: 模组/载板常常只引一个 USB 口 ⇒ 必须问"你们这块板引出的那个口是不是 Maskrom 口" |
| ★ Maskrom 进入方式: 短接 `BOOT_SARADC_VIN0` 与 GND 后上电; 或按住 MASKROM/RECOVERY 键上电; 已开机时可按住 MASKROM 再短按 RESET | Boardcon EM3576 (RK3576 板) 用户手册 · KICKPI RK3576 wiki | 给了 P1 三种可选进法的**问法模板** (但**具体到你们这块板**仍要问) |
| 工具 = `rkdeveloptool` (Linux/macOS, 开源 `rockchip-linux/rkdeveloptool`) / `RKDevTool` (Windows GUI) / `upgrade_tool` (瑞芯微 Linux 版) | 瑞芯微开源仓库 + Debian manpages + 各板厂 wiki | ★ **P2 大概率不用问芯片级工具名**, 要问"**你们这块板**的固件包与分区表" |
| `rkdeveloptool` 命令: `ld` 列设备 / `db <loader>` 下载启动 / `wl <起始扇区> <镜像>` 写 / `rd` 复位 / `ef` 擦除 / `ppt` 打分区表 / `rfi` 读 flash 信息 | Debian manpages (rkdeveloptool(1)) | 直接可映射成 `board_test.flash.cmd` 的 argv 数组 |
| 典型用法: `rkdeveloptool db <loader.bin>` → `wl <起始扇区> <镜像>` → `rd` | 同上 + Bootlin 技术文 | ★ **`wl` 的第二个参数是**起始扇区** ⇒ 这就是"扇区"这个单位在**工具链**里的落点 —— 与 `parameter.txt` 的扇区单位**同源**, 再次说明单位必须显式 |
| 公开见过的下载态 VID:PID (VID 恒为 `0x2207`): `0x330c` (RK3399 Maskrom) / `0x350a` (RK3566) / `0x350b` (RK3568/RK3588 Maskrom) / `0x0011` (ROCK960) | 各板厂 wiki (PINE64 / Radxa / 96Boards / Kobol) | ★ **PID 随 SoC 与态而变**; ★★ **RK3576 自己的 PID 公开资料里查不到 ⇒ 必须问模组厂** (不要拿别家的抄进配置) |
| `rkdeveloptool ld` 输出形如 `DevNo=1 Vid=0x2207,Pid=0x350b,LocationID=501 Maskrom` | Radxa 社区 / PINE64 wiki | ★ 这就是我们**机械判定**要匹配的串 ⇒ 直接作为问询格式 (Q3.2g) |
| `parameter.txt` 的 `CMDLINE: mtdparts=rk29xxnand:0x00002000@0x00004000(uboot),...` 中**十六进制写法的单位是扇区, 1 扇区 = 512 字节**; 同族也有**后缀写法** `8M@9M(boot)` (单位 = 字节, M=MiB) | 九鼎 Rockchip 官方文档英译 · armsom · Vicharak RK3399 `parameter.txt` 实例 (三处独立一致) | ★★ **§4 的单位依据**; ★ 也说明**为什么单位是显式参数** —— 方言不同单位就不同 |
| 瑞芯微分区表要求: 每个分区**起始按 32KB (64 扇区) 对齐, 大小是 32KB 的整数倍** | armsom 引 Rockchip 官方 | §4.2h 的问法 + 守卫的对齐判据 |
| `parameter.txt` 里还有 `MAGIC: 0x5041524B` 字段 | Vicharak RK3399 `parameter.txt` 实例 | ★ 这是**瑞芯微 parameter 分区头部**的 magic, 与**我们自己的版本块 magic** 是两码事 ⇒ **别混** (P2 Q2.2g) |
| U-Boot 里 `rockusb 0 mmc 0` 可进 Rockusb (Loader) 态; fastboot 态可用 `fastboot -i 0x2207 devices` | PINE64 wiki · 瑞芯微 wiki | 进下载态的方式 C (软件触发) 的可行性 |

> ★ **这些公开值只能当"提问的靶子"**。配置里填的必须是**对方针对我们这块板给的**或**我们在自己板子上抓的** (`source` = `vendor-official` / `measured`)。

### 5.2 ★ 必问的 4 件事 (对象是模组厂, 不是芯片原厂)

| # | 问什么 | 为什么 |
|---|---|---|
| A-1 | ★★ 贵方提供的是**核心板 (SOM)** 还是**整板/板级设计方**? 若是核心板: 存储 / 下载态入口 / USB PHY **是不是板载在核心板上**? | ★ 决定 P1/P3/P4 到底是模组厂定还是我们自己在板子上做 —— ★ **也决定本清单该不该改问对象** |
| A-2 | 核心板的 **SPI-NOR / eMMC** 配置与容量, 以及**预烧**了什么 (loader? uboot? parameter.txt?) | 决定"拿到板子时能不能直接进下载态" |
| A-3 | 贵方提供的 **loader 文件**与**分区表**的对应关系, 以及我们**改 kernel/rootfs/app/model** 时需要重刷哪些分区 | ★ 决定 BR-06 的"全量刷写"到底刷哪几个分区 |
| A-4 | 下载态入口 (MASKROM / RECOVERY 按键 / SARADC 测试点) 是否在**核心板上引出** (位号)? 与我们侧键是否冲突? | 对应 Q1.2c (售后手势冲突) |

### 5.3 (v1.0 的"线路 B: ARS45 基线"整节作废)

> ~~线路 B: ARS45 基线必问的 4 件事~~ ⇒ **ARS45 / AR9481 / 酷芯微 已全部作废 (老板 10-29 19:20)**, 保留本节仅作留档, **任何对外发信都不得引用**。

---

## 6. 与既有 needs_from 的对应关系 (不要重复问)

> `state/fragments/sw.yaml` 里 sw-lead 已登记的对外需求 (全部 `waiting_on=vendor`, 经项目总工转达)。本清单是**这些需求的具体化**, 不是新需求。

| needs_from key | to | 本清单对应节 | 状态 |
|---|---|---|---|
| `fw_boot_entry_cond` | vendor | §1 (Q1.1 / Q1.3) | 已登记, due 2026-10-29 **已逾期** |
| `fw_vendor_toolchain` | vendor | §2 (Q2.1 / Q2.2) + §4 (Q4.2 分区表 + ★单位) | 已登记, due 2026-10-29 **已逾期** |
| `fw_usb_boot_phy` | vendor | §3 (Q3.1 / Q3.2) | 已登记, due 2026-10-29 **已逾期** |
| `sw_usb_phy_spec` | vendor | §3 (Q3.1f VBUS / Q3.1e 速率 / ★专用 Maskrom USB 口) | 已登记 (TBD-10 追加问), due 2026-10-29 **已逾期** |
| `fw_boot_storage_bom` | **hw-lead** | §4 (Q4.1 / Q4.3) | 已登记, due 2026-10-29 **已逾期** |
| `fw_boot_mode_hw` | **hw-lead** | §1 (Q1.2 测试点/独立按键) | 已登记, due 2026-10-29 **已逾期** |
| `fw_s2_test_gear` | **main** | 器材采购 (逻辑分析仪 / USB 协议分析仪 / SPI-NOR 空板) | 已登记, due 2026-10-29 **已逾期** |
| ★ `s2_vendor_inquiry_draft` | **main** | ★ **本文件就是这份草稿** —— 请项目总工按 §0.1 纪律外发 | ★ 本单 (ISS-123) 刷新 |

> ★ **同时提醒 hw-lead 侧**: `fw_boot_storage_bom` 与 `fw_boot_mode_hw` 是 **hw-lead 的活** (不是模组厂), 项目总工发信时可**并行**催这两条 —— 它们和 §1/§4 的模组厂回复是**互补**关系, 不互相等。
> ★★ **换芯带来的新连带** (需项目总工转 hw-lead): RK3576 的下载态入口是 **`SARADC_VIN0_BOOT`** 这个 **ADC 引脚** (不是普通 BOOT GPIO) ⇒ **载板上的测试点/跳线怎么引、电压怎么给**, 要 hw-lead 按 §1 Q1.1c 的门限设计 (目前 `boot_entry_hw = BOOT-static-strap+上电` 这条接口声明是按旧 SoC 写的, **需按 RK3576 重核**)。

---

## 7. 回填自检 (收到回复后照着跑)

```bash
cd projects/smart_glasses

# ① 参数齐备性 (期望 rc=0; 会逐条列出差的可执行件)
bash SW/tools/s2_board_run.sh --preflight --config SW/tools/s2_rescue_config.json

# ② 判定器自测 (期望 rc=0, 13/13 —— 含"通用示例不算证据"与 512 倍反例)
python3 SW/tools/s2_board_judge.py --selftest

# ③ ★ISS-123 分区表单位守卫 (期望 rc=0 = 无问题; 有 error ⇒ 拒绝写入)
python3 SW/tools/s2_partition_convert.py --check SW/tools/s2_rescue_config.json

# ④ 检查 4 个参数确实都 DONE 了 (期望 4 行全 DONE, 无 TODO)
python3 - <<'EOF'
import json
d = json.load(open('SW/tools/s2_rescue_config.json', encoding='utf-8'))
for k, v in d['params'].items():
    print(f"{k:<22} status={v.get('status'):<6} filled={v.get('value') not in (None,'',[],{})}")
EOF

# ⑤ ★ 检查 usb_signatures 里没有 generic-example (期望 0 行 generic-example)
python3 - <<'EOF'
import json
d = json.load(open('SW/tools/s2_rescue_config.json', encoding='utf-8'))
bad = [e for e in d['usb_signatures']['entries'] if e.get('source') == 'generic-example']
print("generic-example 条数 =", len(bad), "  (必须为 0)")
EOF

# ⑥ ★ 检查分区表已换真值 (期望 source 不是 placeholder-推算)
python3 -c "import json;print(json.load(open('SW/tools/s2_rescue_config.json'))['partition_layout']['source'])"

# ⑦ ★ 全链路自证 (一条命令; 期望 rc=0)
bash SW/tools/s2_iss123_verify.sh
```

---

## 8. 本清单的边界声明

| # | 声明 |
|---|---|
| 1 | ★ **sw-lead 不直接联系模组厂 / 原厂 / 供应商**。本文件是**草稿**, 外发由项目总工执行。 |
| 2 | ★ 本清单**不含任何编造的参数值**。§5.1 的公开事实全部标了出处, 且明确写了"**不能直接抄进配置**"。 |
| 3 | ★ 4 个 0 数据项在对方书面回复前, `SW/tools/s2_rescue_config.json` 里**一律 `value: null` / `status: "TODO"`** —— 不许先用公开值或通用示例顶上去。 |
| 4 | ★ v1.0 的"ARS45 基线 / 线路 B"整节**作废**, 保留仅作留档; **任何对外发信不得引用**。 |
| 5 | ★ 本清单**不拍板**任何选型 (存储类型 / 工具链 / 分区方案 / 版本块 magic 最终取值) —— 只把问题组织到能一次问完、能落地成字段。 |
| 6 | ★ **板端 S2 实测仍是 0 次** —— 本清单交付的是"怎么问 + 怎么问对对象", 不是"测过了"。 |
