# S2 救砖链路 · 板端实测执行清单 (EVT-8 / BR-01)

> **文件**: `SW/S2_BOARD_TEST_CHECKLIST.md` v1.0 (2026-10-30) · ISS-120 (sw-lead)
> **上游**: `SW/FLASH_AND_VERSION.md` §4.5 (S2 可执行实测方案, ISS-080) + `SW/EVT_TEMPLATE.md` §11 (EVT-8 / BR-01)
> **配套**: `SW/S2_VENDOR_QUESTION_LIST.md` (原厂问询) + `SW/tools/s2_board_run.sh` (一条命令跑测) + `SW/tools/s2_board_judge.py` (CB-01~09 机械判定)
>
> **一句话**: **本清单把 ISS-080 的"方案"变成"投板那天照着勾的东西"** —— 每一条都写死「执行前置 / 判定口径 / 记录字段 / 谁判过」, 勾完就出 BR-01 结论。

---

## 0. 状态与口径 (先读这一段)

| 项 | 值 |
|---|---|
| 本清单对应可判项 | **EVT-8 / BR-01** (量产一票否决项, G4 / 量产放行前置) |
| 板端实测次数 | **0 次** —— 本清单**一份都还没勾** |
| 4 个 0 数据项 | `P1_BOOT_ENTER_SPEC` / `P2_DL_TOOL` / `P3_USB_PHY` / `P4_BOOT_STORE` 全 **[0数据]** (原厂书面回复前一律留空) |
| 判定三态 | ✅ 通过 / ❌ 不通过 / ⚠️ 未验 (机械规则见 EVT §11.4) |
| 判过权 | **项目总工 (main)** —— 修复人不能自验 (`state/issue_log.yaml` ISS-120 `verify_by=main`) |
| 量产红线 | BR-01 判 ⚠️未验 或 ❌ 的板 **不得进产线 / 不得交付**; 整批未验 → 不得量产 |

### 0.1 ★ 三条不可绕过的纪律 (沿用 ISS-080 口径)

1. **通用示例不是真值。** `SW/tools/s2_rescue_config.example.json` 里那 3 条 `source=generic-example` 的 USB 签名 (TI DFU / STM32 DFU / Linux gadget) 是**别的平台**的示例。板端配置 `SW/tools/s2_rescue_config.json` 的 `usb_signatures.entries` **故意留空** —— 在拿到原厂 VID:PID 前, 探针只会判 `NOT_IDENTIFIED`, **判不出就判不出, 不许猜**。
2. **[推算] 占位不是实测。** `partition_layout` 现在是 [推算] 占位表。**P4 未填时 CB-02 / CB-06 一律判"未验"** —— 拿占位表判回读 CRC 通过 = 拿推算冒充实测。
3. **没数据 ≠ 没问题。** 任何一项缺有效实测数据 → BR-01 **最高只能判 ⚠️未验**, 并写明缺哪项、什么时候补测。

### 0.2 ★ 口径变更提示 (投板前必须先解决, 否则本清单白勾)

> **ISS-119 (2026-10-29) 把 SoC 基线从 ARS45 换成了 RK3588** (RK3576 为可机械触发的翻转后手; 定案书 `HW/CHIP_SELECTION_DECISION.md`, **verify_by=boss, 待老板点头**)。
>
> ⇒ 本清单与 `SW/FLASH_AND_VERSION.md` §4.5 里写的 "ARS45" 字样**口径已不一致**, 影响三处:
> 1. **P2/P3 问谁变了** —— 原厂从 ARS45 供应商变成瑞芯微 (RK3588) 链路 → 问询清单 §5 已按两种口径分叉写, **项目总工裁决走哪条**。
> 2. **版本块 magic / 版本串前缀** —— `flash_writer.py` 里写死 `magic == "AR45"`、版本串行首 `ARS45-SW `, 是按 ARS45 定的。换芯后**要不要沿用** 是个决策, 不由本单拍板 (见交接单 B5-1)。
> 3. **P4 分区表口径变了** —— RK3588 用 `parameter.txt` 定义分区 (不是我们 [推算] 的自定义表) → 占位表必然要整段替换。
>
> ⇒ **投板前必须先关掉这个口径问题**, 否则现场勾完的勾, 对着的是一块已经不在计划内的板。

---

## 1. 一条命令跑测 (投板那天就用这个)

```bash
cd projects/smart_glasses

# ① 投板前: 查参数齐不齐 (期望 rc=0; 差哪几个会逐条列出)
bash SW/tools/s2_board_run.sh --preflight --config SW/tools/s2_rescue_config.json

# ② 现场: 一条命令跑完整条 S2 (自动落盘全部证据 + 自动出 BR-01 判定)
bash SW/tools/s2_board_run.sh \
     --config SW/tools/s2_rescue_config.json \
     --evidence-dir SW/artifacts/s2/<板SN>_<日期> \
     --current-ma <电流表读数>

# ③ 只跑某一步 (现场卡住了想单点重跑时)
bash SW/tools/s2_board_run.sh --config ... --evidence-dir <dir> --only step2

# ④ ★ 出了故障, 先抓现场 (串口日志 / 下载工具版本 / 电流表读数)
bash SW/tools/s2_board_run.sh --config ... --evidence-dir <dir> --only forensics
```

| 退出码 | 含义 | 现场动作 |
|---|---|---|
| 0 | BR-01 判 ✅ (CB 9/9 全过) | 交项目总工签"判过" |
| 1 | BR-01 判 ❌ (至少 1 条 CB 不通过) | 按 §5 决策树走, **不许"多刷几次试试"** |
| 2 | BR-01 判 ⚠️未验 (有项没实测数据) | **该板不得进产线**; 补测后再判 |
| 3 | 参数不全 / 环境错误 | 4 个 0 数据项没到位 → 看 `SW/S2_VENDOR_QUESTION_LIST.md` |
| 4 | 脚本自身自检失败 | 停手报项目总工, 别在坏脚本上跑板子 |

> ★ 步骤 1 (进 BOOT) 是**唯一需要人工介入**的一步: 脚本会提示操作员按 §3 的 SOP 操作后回车确认。其余步骤全自动。
> ★ **失败现场自动抓**: 任一步失败 → 自动采串口日志 + 下载工具版本 + 电流表读数, 落 `s2_forensics.json` + `s2_forensics_serial.log`。
> ★ 电流表读数**没有仪器就读不到** → 记 `[0数据]` 并提示人工补, **脚本绝不编一个数**。

---

## 2. 前置条件 (工位准备表) —— 全勾了才允许开跑

### 2.1 器材

| ☐ | 项 | 判据 | 谁判过 | 记录字段 |
|---|---|---|---|---|
| ☐ | 被测板 (EVT 样机) | 板卡丝印 SN 与 `board_test.board_sn` 一致 | 执行人自检 + 项目总工复核 | `board_test.board_sn` / 证据目录名 |
| ☐ | Type-C **数据线** ×1 | 不是充电线 (能跑 `lsusb` 枚举) | 执行人 | 照片 / 备注 |
| ☐ | USB-TTL 串口线 + 笔记本 | 能看 U-Boot / kernel 串口输出 | 执行人 | `board_test.serial.device` + `baud` |
| ☐ | 电流表 (mA 档) | 能读整机电流 (刷写时峰值电流高) | 执行人 | `--current-ma` 传值 |
| ☐ | 跳线夹 / 测试夹 | 够方式 A (BOOT 测试点拉有效电平) | 执行人 | — |
| ☐ | 下载工具 (P2 指定) | 命令能在 PATH 里跑起来 | 执行人 | `s2_forensics.json` → `download_tool_versions[]` |
| ☐ | 逻辑分析仪 (可选) | 想留 `s2_boot_timing.png` 波形证据就必须要 | hw-lead 配合 | `s2_boot_timing.png` |

### 2.2 软件 / 数据

| ☐ | 项 | 判据 | 谁判过 | 记录字段 |
|---|---|---|---|---|
| ☐ | S2 配置 4 个参数齐 | `params.P1..P4` 的 `value` 非空 **且** `status=DONE` | 项目总工 (转录原厂回复) | `SW/tools/s2_rescue_config.json` |
| ☐ | 分区表已换真值 | `partition_layout.source` ≠ `placeholder-推算` | 项目总工 | 同上 |
| ☐ | USB 签名表已换真值 | `usb_signatures.entries` 每条 `source` ∈ {`vendor-official`, `measured`}, **无 `generic-example`** | 项目总工 | 同上 |
| ☐ | 板端自检 6 项命令已配 | `board_test.selftest.{ddr,sensor,i2c,npu,od,version}` 全非空 | sw-lead | 同上 |
| ☐ | 工厂标定台账已建 | `board_test.checks.calib_ledger` 有该 SN 的标定 ID | 项目总工 (标定工位) | 同上 |
| ☐ | 正常态基线已采 | `s2_step0_normal.json` 有 `vidpid` | 执行人 | `s2_step0_normal.json` |

### 2.3 人员

| ☐ | 项 | 判据 | 谁判过 |
|---|---|---|---|
| ☐ | 执行人 (sw-lead 或受训工程师) | `board_test.operator` 填了 | 项目总工 |
| ☐ | 硬件配合 (hw-lead) | BOOT/RESET 通路确认 + 必要时抓波形 | 项目总工 |
| ☐ | 裁决 (项目总工) | S2 失败升级 S3 / S4 由他裁决, **sw-lead 不自行升级** | — |
| ☐ | 验证 (项目总工) | 判 BR-01 是否真过 | — |

---

## 3. 进 BOOT 模式 SOP (唯一的纯人工步骤)

> 出处: `SW/FLASH_AND_VERSION.md` §4.5.2。**具体电平/时序数值待 P1** —— 现在全是 **[0数据]**。

| 方式 | 操作 | 适用前提 | 风险 | 建议 |
|---|---|---|---|---|
| **A. BOOT 测试点 + RESET 键** | 断电 → 短接 BOOT 测试点到有效电平 → 上电 → 按 RESET → 释放 | HW-22 预留了 BOOT 测试点 | 产线要带跳线夹; 用户做不了 | ⭐ **产线/返修工位首选** |
| **B. 按键组合** | 按住 BOOT 键 + 按 RESET (顺序/时长待 P1) | 原厂 bootloader 支持 | 与售后手势可能冲突 | 次选, 仅当 P1 明确支持 |
| **C. USB 触发** | 插线瞬间主机侧拉信号 | 原厂支持 | 依赖 PC 端工具行为, 不可控 | 不作产线依赖 |

**通用时序骨架** (t* 单位 ms, **数值待 P1**):

```
  t0      设备上电
  t0+t1   建立 BOOT 条件 (★ 必须在 RESET 之前就位)
  t0+t1+t2   按下 RESET (脉冲宽 t3)
  t0+t1+t2+t4   释放 BOOT 条件 (★ 部分平台要求 RESET 上升沿后仍保持 ≥ t4)
  t0+t1+t2+t4+t5 设备开始 USB 枚举 (超时 t_enum_timeout, 建议 ≥15s)
```

| 时序参数 | 含义 | 取值 | 证据等级 |
|---|---|---|---|
| `t1` | 上电 → 建立 BOOT 条件的窗口 | 待 P1 | **[0数据]** |
| `t2` | 建立 BOOT → 按 RESET 的间隔 | 待 P1 | **[0数据]** |
| `t3` | RESET 按键脉冲宽度 | 待 P1 (常见 100ms 量级) | **[0数据]** + [推算](量级) |
| `t4` | RESET 释放后 BOOT 条件保持时间 | 待 P1 | **[0数据]** |
| `t_enum_timeout` | 枚举超时 | 15s | [推算] (给 USB 枚举 + 工具握手留余量) |
| `boot_pin_level` | BOOT 引脚有效电平 | 待 P1 (高/低有效不确定) | **[0数据]** |

**★ 售后手势冲突检查 (每次投板都要确认一遍)**:
`FRAMEWORK/AFTERSALES.md` 已占用侧键两个手势 —— **长按 10s = 关机** / **长按 3s = 显示版本号**。
若 BOOT 组合复用同一颗侧键, 3s 与 10s 在时间轴上重叠, 必须让 bootloader 做长按阈值分层, 否则用户误触就"看着像砖"。
⇒ **建议 BOOT 走方式 A (独立测试点/跳线), 不复用侧键**; 必须用键时, BOOT 键必须是独立按键。

**"我真的进了 BOOT" 的 3 条独立证据**:

| 证据 | 内容 | 怎么取 | 强度 | 本清单对应 |
|---|---|---|---|---|
| **E1** 枚举特征 | BOOT 态 USB VID:PID 与正常态**不同** | `boot_rescue_probe.py` / 原厂工具列设备 | ⭐⭐⭐ 最强 | CB-01 / BR-05 |
| **E2** 日志特征 | 串口出现 `bootloader` / `u-boot` / `fastboot` / `dfu` / `download mode` | 串口 / `dmesg` | ⭐⭐ | 辅助 |
| **E3** 引脚电平 | BOOT 引脚实测电平 = 有效电平, RESET 脉冲符合时序 | 万用表 / 逻辑分析仪 | ⭐⭐ | 硬件侧 (L2) |

> **判据**: E1 与 E2/E3 **至少一条成立**, 且 **E1 成立时才算"确定进 BOOT"**; E2 单独成立只判 `BOOT_SUSPECTED_BY_LOG`, **不算过** (探针对此返回 rc=1, 防止用日志猜)。

---

## 4. CB-01 ~ CB-09 机械判据 (9 条, 逐条勾)

> 判据与 `SW/EVT_TEMPLATE.md` §11.2 一一对应。**判过标准全部是机械判, 不含主观判断。**
> 记录字段里的文件名 = `s2_board_run.sh` 自动落盘的文件, 判定器 `s2_board_judge.py` 直接读它们。

### CB-01 · 设备重新枚举回正常态

| 项 | 内容 |
|---|---|
| **执行前置** | ① 全量刷写已成功 (BR-06 通过) ② 正常态基线 `s2_step0_normal.json` 已采 ③ 板子已重新插线 |
| **判定口径** | 刷完后 VID:PID 与**正常态基线一致** (`s2_step5_reenum.json.vidpid` == `s2_step0_normal.json.vidpid`) **且** `matched_boot` 为空 (**不匹配任何 BOOT 签名**) ⇒ ✅; VID:PID 变了 ⇒ ❌; 仍匹配 BOOT 签名 ⇒ ❌; 证据缺失 ⇒ ⚠️未验; ★ 命中 `source=generic-example` 的通用示例 ⇒ ⚠️未验 (**通用示例不算证据**) |
| **记录字段** | `s2_step5_reenum.json`: `vidpid` / `matched_boot[]` (含 `source`) / `adb_devices[]` ; 对照 `s2_step0_normal.json`: `vidpid` |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-02 · 版本块 magic + bootable + payload CRC

| 项 | 内容 |
|---|---|
| **执行前置** | ① 已把整片 flash 回读到本地文件 (BR-07) ② 真实分区表已填 (P4 `status=DONE`, `partition_layout.source` ≠ `placeholder-推算`) |
| **判定口径** | `s2_step3_verify.json` 里 `CB-02a` magic == `AR45` (或换芯后新定值) **且** `CB-02b` bootable 置位 (擦除态 `0xFF` 不算 bootable) **且** `CB-02c` payload CRC 一致 ⇒ ✅; 任一 FAIL ⇒ ❌; 证据缺失 ⇒ ⚠️未验 |
| **记录字段** | `s2_step3_verify.json` → `checks[]` 中 `CB-02a` / `CB-02b` / `CB-02c` 三项的 `result` + `detail` |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-03 · 版本串 6 分项齐全 + 5 条校验规则

| 项 | 内容 |
|---|---|
| **执行前置** | ① 板子能进系统 ② `board_test.selftest.version` 已配 ③ 板上模型文件路径已配 (`model_path`) |
| **判定口径** | `s2_step4_selftest.json.version_string` 逐条过 §3.1.3 的 5 条规则: ①行首 `ARS45-SW ` + 合法 semver ②`sn=` 非空且与板卡丝印一致 ③`model=` 的 sha8 == **板上模型文件实测** sha256 前 8 ④`boot/kern/rootfs/app/model/isp` 6 分项全非空 ⑤`mode=` 与期望一致 ⇒ 全过才 ✅; 任一违反 ⇒ ❌; ★ 拿不到板上模型文件 sha256 ⇒ 第 ③ 条判 ⚠️未验 (**不许拿版本串里写的 sha8 反推自己**) |
| **记录字段** | `s2_step4_selftest.json`: `version_string` / `model_sha8` / `version_source` ; 判定器逐条结果在 `s2_br01_verdict.json` → `cbs[CB-03].rules[]` (含 `id` / `result` / `detail`) |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-04 · 启动自检 6 项

| 项 | 内容 |
|---|---|
| **执行前置** | ① 板子能进系统 ② `board_test.selftest` 的 6 条命令已配且在板上可执行 (默认经 `adb shell` 转发) |
| **判定口径** | 6 项**全过**才 ✅: ①DDR 自检 ②sensor 枚举 ③光机 I2C 应答 ④NPU 模型加载 ⑤OD 跑通 1 帧 ⑥版本块回显。判定细则: 命令 rc≠0 ⇒ ❌; **rc=0 但输出为空 ⇒ ❌** (防止"命令跑了但什么都没干"被当成过); 命令未配 ⇒ ⚠️未验 (**不许跳过**) |
| **记录字段** | `s2_step4_selftest.json` → `selftest.{ddr,sensor,i2c,npu,od,version}.{status,detail}` |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-05 · 重启 3 次自启动

| 项 | 内容 |
|---|---|
| **执行前置** | ① 刷回成功 ② `board_test.reboot.cmd` 已配 (默认 `adb reboot`) ③ `board_test.reboot.wait_cmd` 已配 (否则只能判"命令已发出", 进系统与否靠串口首行人工确认) |
| **判定口径** | `s2_step6_reboot.json.attempts[]` 共 3 条, `ok=true` 且 `panic=false` **3/3** ⇒ ✅; 任一次 kernel panic ⇒ ❌; 不足 3 次 ⇒ ⚠️未验 |
| **记录字段** | `s2_step6_reboot.json`: `attempts[].{n,ok,panic,wait_s}` / `passed` |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-06 · 分区回读 CRC = 写入镜像 CRC

| 项 | 内容 |
|---|---|
| **执行前置** | ① 已回读整片 flash ② ★ **P4 已填且分区表是真实值** (占位表 ⇒ 本条强制判未验) |
| **判定口径** | `s2_step3_verify.json` 里 6 个 CRC 槽 (`boot`/`kern`/`rootfs`/`app`/`model`/`isp`) **全部一致** ⇒ ✅; 任一不一致 ⇒ ❌; ★ P4 未填 ⇒ ⚠️未验 (**不许拿 [推算] 占位表判过**) |
| **记录字段** | `s2_step3_verify.json` → `checks[]` 中 `CB-06*` 各项的 `result` + `detail` (含回读值 vs 版本块值) |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-07 · 标定 ID 与出厂台账一致

| 项 | 内容 |
|---|---|
| **执行前置** | ① 工厂标定台账已建 (EVT §11.8 BR-R4) ② `board_test.checks.calib_ledger` 已填该 SN 的标定 ID ③ 版本串能读到 |
| **判定口径** | 版本串 `calib=` 与台账**字符串完全一致** ⇒ ✅; 不一致 ⇒ ❌ (F6: **返修最大的坑** —— 刷完画质退化); 台账未建 ⇒ ⚠️未验 |
| **记录字段** | `s2_step4_selftest.json.version_string` 里的 `calib=` vs `board_test.checks.calib_ledger` |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-08 · mode 位正确

| 项 | 内容 |
|---|---|
| **执行前置** | ① 版本串能读到 ② 刷完后重新枚举时采过 `adb devices` |
| **判定口径** | 版本串 `mode=` 与期望一致 **且** (期望 = `prod` 时) 插线 `adb devices` **无设备** (adbd 已关) ⇒ ✅; mode 不符 ⇒ ❌; prod 下仍有 adb 设备 ⇒ ❌; 未采 adb ⇒ ⚠️未验 |
| **记录字段** | `s2_step4_selftest.json.version_string` 的 `mode=` + `s2_step5_reenum.json.adb_devices[]` |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

### CB-09 · 日志无错误码

| 项 | 内容 |
|---|---|
| **执行前置** | ① 板端日志已抓 (`s2_step4_selftest.log`) ② 扫描覆盖完整日志 |
| **判定口径** | 全量日志中**不出现** `E_MODEL_MISMATCH` / `E_CALIB_MISSING` / `E_VER_*` / `E_SN_MISMATCH` ⇒ ✅; 出现任一 ⇒ ❌; 没扫 ⇒ ⚠️未验 |
| **记录字段** | `s2_step4_selftest.json` → `log_scan.{scanned_lines,errors[]}` ; 原始日志 `s2_step4_selftest.log` |
| **谁判过** | 执行: sw-lead · **判定: 项目总工** |

---

## 5. BR-01 ~ BR-12 用例 (12 条, 逐条勾)

> 状态列一律 **[待实测]** —— **没有一条跑过板端**。这是投板后的执行清单, 不是成绩单。

### BR-01 · S2 全链路 (总判定项)

| 项 | 内容 |
|---|---|
| **执行前置** | CB-01 ~ CB-09 的执行前置全部满足 |
| **判定口径** | **CB-01 ~ CB-09 全 ✅ (9/9)** 且每项都有 `[实测]` 数据 + 数据文件路径 ⇒ BR-01 ✅; 任一 ⚠️未验 ⇒ 最高 ⚠️未验; 任一 ❌ ⇒ ❌ |
| **记录字段** | `s2_br01_verdict.json` (判定器自动出) + ①`s2_step0_normal.json` ②`s2_step1_boot.json` ③`s2_step2_flash.log` ④`s2_step3_verify.json` ⑤`s2_step4_selftest.log` ⑥`s2_boot_timing.png` |
| **谁判过** | **项目总工** (`verify_by=main`) |

### BR-02 · 正常态基线采集

| 项 | 内容 |
|---|---|
| **执行前置** | 板子正常开机、未进 BOOT |
| **判定口径** | 基线文件存在 **且** 有非空 `vidpid` ⇒ 通过; 基线缺失 ⇒ 未验 (**没有基线, 后面 CB-01 无从比对**) |
| **记录字段** | `s2_step0_normal.json`: `vidpid` / `devices[]` |
| **谁判过** | 执行: sw-lead |

### BR-03 · 方式 A 进 BOOT (跳线 + RESET)

| 项 | 内容 |
|---|---|
| **执行前置** | P1 已填 (电平/时序) · 方式 A 测试点可用 |
| **判定口径** | **E1 成立** (枚举特征变了) ⇒ 通过; 仅 E2 (日志) ⇒ 不算过 (判未验); E1/E2/E3 全无 ⇒ 失败, 走 §6 决策树第 1 行 |
| **记录字段** | `s2_step1_boot.json`: `verdict` / `matched[]` / `log_hits[]` (+ `s2_boot_timing.png` 波形, 若有逻辑分析仪) |
| **谁判过** | 执行: sw-lead · 硬件配合: hw-lead |

### BR-04 · 方式 B 进 BOOT (按键组合)

| 项 | 内容 |
|---|---|
| **执行前置** | ★ **仅当 P1 明确支持按键组合才跑** (否则标 ⬜ 依赖 P1, 不算失败) |
| **判定口径** | 同 BR-03 (E1 成立才算过) |
| **记录字段** | 同 BR-03 |
| **谁判过** | 执行: sw-lead |

### BR-05 · 工具识别

| 项 | 内容 |
|---|---|
| **执行前置** | P2 已填 (工具到位) · 工具命令能在 PATH 跑 |
| **判定口径** | 原厂工具 (或 fastboot / DFU) **列出该板且行数 = 1** ⇒ 通过; 列出 0 个或 >1 个 ⇒ 失败 (走 §6 决策树第 2 行) |
| **记录字段** | `s2_step1_boot.json`: `raw` (工具原始输出) / `rc` / `boot_markers_hit[]` ; 工具版本见 `s2_forensics.json` → `download_tool_versions[]` |
| **谁判过** | 执行: sw-lead |

### BR-06 · 全量刷写

| 项 | 内容 |
|---|---|
| **执行前置** | P2 已填 · 镜像齐备 · 真实分区表已填 (P4) · ⚠️ **刷写前先备份当前分区表** (若工具支持读回) |
| **判定口径** | 工具报**全部成功、无失败分区** ⇒ 通过; 有失败分区 ⇒ 失败 (**不自动重试** —— 半写状态未知 → 全量重刷, 仍失败 → 走 §6 决策树第 3 行) |
| **记录字段** | `s2_step2_flash.log` (工具原始日志, 含分区级结果) + `s2_step2_flash.json`: `cmd` / `rc` / `log_bytes` / `ok` |
| **谁判过** | 执行: sw-lead |

### BR-07 · 回读校验

| 项 | 内容 |
|---|---|
| **执行前置** | BR-06 通过 · 回读通道可用 (`board_test.verify.readback_cmd`) |
| **判定口径** | `flash_writer.py verify` 全过 ⇒ 通过; 有不一致 ⇒ 失败 (走 §6 决策树第 4 行) |
| **记录字段** | `s2_step3_verify.json`: `result` + `checks[]` (每项 `name` / `result` / `detail`) |
| **谁判过** | 执行: sw-lead |

### BR-08 · 版本串校验

| 项 | 内容 |
|---|---|
| **执行前置** | 板子能进系统 · `selftest.version` 已配 |
| **判定口径** | 版本串 6 分项齐全 + §3.1.3 的 5 条规则全过 ⇒ 通过 (细则见 CB-03) |
| **记录字段** | `s2_step4_selftest.json.version_string` / `model_sha8` ; 判定器逐条结果 `s2_br01_verdict.json` → `cbs[CB-03].rules[]` |
| **谁判过** | 执行: sw-lead |

### BR-09 · 启动自检

| 项 | 内容 |
|---|---|
| **执行前置** | `selftest` 6 条命令已配 |
| **判定口径** | 6/6 全过 ⇒ 通过 (细则见 CB-04: rc=0 但输出为空 ⇒ ❌) |
| **记录字段** | `s2_step4_selftest.json.selftest.*.{status,detail}` |
| **谁判过** | 执行: sw-lead |

### BR-10 · 重启 3 次

| 项 | 内容 |
|---|---|
| **执行前置** | BR-09 通过 · `reboot.cmd` + `reboot.wait_cmd` 已配 |
| **判定口径** | 3/3 进系统, 0 次 kernel panic ⇒ 通过 (细则见 CB-05) |
| **记录字段** | `s2_step6_reboot.json.attempts[]` |
| **谁判过** | 执行: sw-lead |

### BR-11 · 【负向】断电原子性

| 项 | 内容 |
|---|---|
| **执行前置** | ★ **破坏性用例** —— 需项目总工单独批准在样机上做 (可能真砖) · 建议在"刷写不进去也不影响其它板"的样机上做 |
| **判定口径** | 写到一半拔电 ×3 (分别断在 bootloader / rootfs / 版本块 payload) → 上电后**不启动** **且** 回读 verify 判**未生效** ⇒ 通过 (说明"先内容后标志"在板端也成立); 若半写状态被误判成已生效 ⇒ ❌ (★ 这是批量刷砖风险, ISS-080 的 L1 仿真抓出 4 个同类 bug 的同源问题) |
| **记录字段** | 3 份 verify JSON (`s2_step3_verify_<断点>.json`) + 每次上电的串口首行日志 |
| **谁判过** | 执行: sw-lead · **批准: 项目总工** |

### BR-12 · 【负向】标定丢失

| 项 | 内容 |
|---|---|
| **执行前置** | ★ **破坏性用例** —— 刷一个不含标定 ID 的镜像 (会暂时丢失标定) · 需从标定台账恢复 |
| **判定口径** | 启动自检报 `E_CALIB_MISSING` **且拒绝进入 OD** ⇒ 通过; 静默用错标定继续跑 ⇒ ❌ (F6 防线破了) |
| **记录字段** | `s2_step4_selftest.log` 里的 `E_CALIB_MISSING` 行 + OD 未启动的证据 |
| **谁判过** | 执行: sw-lead · **批准: 项目总工** |

---

## 6. 失败决策树 (S2 → S3 → S4) —— ★ 连挂 2 次必须升级

> 出处: `SW/EVT_TEMPLATE.md` §11.5 + `SW/FLASH_AND_VERSION.md` §4.5.7。

| 现象 (哪条挂了) | 最可能原因 | 立即动作 | **上限** |
|---|---|---|---|
| **进不了 BOOT** (CB-01 前就卡住, E1/E2/E3 全无) | BOOT 通路/时序错 (P1 未确认) / BOOT 引脚电平不对 | 换方式 A / B 各试一次; 用逻辑分析仪抓 BOOT/RESET 波形 | S2 重试 **≤2 次** |
| **枚举了但工具不认** (BR-05) | 协议不匹配 (P3) / 线不是数据线 / 工具版本不对 | 换线换口; 核对工具版本; 走另一条分支 (原厂工具 / fastboot / DFU) | ≤2 次 |
| **识别了但写不进去** (BR-06) | 存储类型与分区表不匹配 (P4) / 中途断电 (F2) | **不自动重试** (半写状态未知) → 全量重刷 | ≤2 次 |
| **刷完起不来** (CB-02/04/05 挂) | bootloader 校验失败 / 分区表错 (P4) / magic 缺失 | 跑回读校验判定"是否未生效"; 是 → 重刷; 否 → **升级 S3** | ≤2 次 |
| **起来了但画质退化** (CB-07 挂) | **标定数据丢失 (F6)** —— 返修最大的坑 | 从工厂标定台账按 SN 恢复标定 → 重刷 | 按 `SW/FLASH_AND_VERSION.md` §5.2 第 5 步 |
| **起来了但 OD 不出框** (CB-03/04/09 挂) | 模型 hash / 格式版本不匹配 (F4) | 重刷 + 核对 `model=` 版本串 | 按 F4 处置 |

### 🔴 硬规则

> **S2 连续失败 2 次 → 必须升级 S3 (JTAG), 不得"多刷几次试试"。**
> 半写状态反复覆盖会制造更复杂的问题。
> **升级 S3 / 判 S4 返厂由项目总工裁决, sw-lead 不自行升级。**
> **S2 全链路失败 = 该板判返厂 (S4), 不得进产线。**

| ☐ | 升级动作 | 谁批 | 记录 |
|---|---|---|---|
| ☐ | S2 失败第 1 次 | — | 失败现象 + 命中决策树哪一行 + 现场证据路径 |
| ☐ | S2 失败第 2 次 → **申请升级 S3 (JTAG)** | **项目总工** | 申请理由 + 前 2 次的失败记录 |
| ☐ | S3 也失败 → 申请 S4 (返厂) | **项目总工** | S3 失败证据 |
| ☐ | 判 S4 返厂 | **项目总工** | 该板 SN + 返修单号 |

---

## 7. 记录字段清单 (证据文件 + 谁采 + 何时采)

| 序号 | 文件 | 内容 | 生成/采集人 | 采集时间 | 大小 |
|---|---|---|---|---|---|
| 1 | `s2_step0_normal.json` | 正常态 USB 枚举基线 (VID:PID + product) | sw-lead (自动) | | |
| 2 | `s2_step1_boot.json` | BOOT 态证据 (E1 枚举特征 + E2 日志) | sw-lead (自动) | | |
| 3 | `s2_step2_flash.log` | 下载工具刷写日志 (含分区级结果) | sw-lead (自动) | | |
| 3b | `s2_step2_flash.json` | 刷写结果摘要 (cmd / rc / ok) | sw-lead (自动) | | |
| 4 | `s2_step3_verify.json` | 版本块回读校验 (CB-02 / 06 / 07) | sw-lead (自动) | | |
| 5 | `s2_step4_selftest.log` | 板端自检原始输出 | sw-lead (自动) | | |
| 5b | `s2_step4_selftest.json` | 板端自检 + 版本串 + 模型 sha8 + 日志扫描 (机器可读) | sw-lead (自动) | | |
| 6 | `s2_step5_reenum.json` | 刷完后重新枚举 (VID:PID / BOOT 签名 / adb) | sw-lead (自动) | | |
| 7 | `s2_step6_reboot.json` | 重启 3 次结果 | sw-lead (自动) | | |
| 8 | `s2_br01_verdict.json` | ★ CB-01~09 + BR-01 总判定 | sw-lead (自动) | | |
| 9 | `s2_boot_timing.png` | BOOT/RESET 时序波形截图 | hw-lead (人工, 逻辑分析仪) | | |
| 10 | `s2_forensics.json` | 失败现场: 下载工具版本 + 电流表读数 + 串口日志索引 | sw-lead (自动) | | |
| 11 | `s2_forensics_serial.log` | 失败现场: 串口原始日志 | sw-lead (自动) | | |

> ★ EVT §11.7 原清单的 6 个文件名**全部保留** (序号 1~6), 本单新增的是 3b / 5b / 6 / 7 / 8 / 10 / 11。

---

## 8. 判定栏 (三态, 交卷时填)

| 判定 | ☐ | 规则 |
|---|---|---|
| ✅ 通过 | ☐ | CB-01 ~ CB-09 **全部 ✅ (9/9)**, 且每项有 `[实测]` 数据 + 数据文件路径 |
| ❌ 不通过 | ☐ | 至少 1 项 ❌ (写明子编号 + 实测值 + 违反哪条标准 + 已走 §6 哪条处置) |
| ⚠️ 未验 | ☐ | 存在无有效实测数据的项 (写明子编号 + 原因 + 补测时间); **★ 此状态下该板不得进产线** |

### 追溯 (BR-01 通过后必填, EVT §11.4 R6)

| 字段 | 值 |
|---|---|
| 板卡 SN | |
| 证据目录路径 | |
| 刷入的版本串 | |
| 下载工具 + 版本 | |
| 刷回日期 | |
| 执行人 | |
| **判过人 (项目总工)** | |

---

## 9. 本清单的遗留缺口 (投板前必须关掉)

| # | 缺口 | 卡住谁 | 需要谁 | 期望时限 |
|---|---|---|---|---|
| C-1 | **4 个 0 数据项 (P1~P4) 全未填** | §3 全部时序/电平、BR-03~07 全部 | 项目总工 → 原厂 | 见 `SW/S2_VENDOR_QUESTION_LIST.md` |
| C-2 | **下载工具未到位** (即使参数齐了, 没工具跑不了 BR-05/06) | BR-05 / BR-06 | 项目总工 (经 vendor) | 同上 |
| C-3 | **板端自检 6 项的命令未配** (`board_test.selftest.*`) | CB-04 / BR-09 | sw-lead (投板前, 需板端可执行环境信息) | 投板前 |
| C-4 | **工厂标定台账未建** | CB-07 / BR-12 | 项目总工 (标定工位) | 标定工位上线前 |
| C-5 | **★ 换芯口径未裁决** (ISS-119: RK3588 基线待老板点头) —— 版本块 magic / 版本串前缀 / 分区表口径全部要跟着改 | §3 / CB-02 / CB-03 / CB-06 全线 | **项目总工 + 老板** | **投板前** |
| C-6 | 板端回读通道未定 (CB-02/CB-06 靠它) | CB-02 / CB-06 / BR-07 | sw-lead + 项目总工 | 投板前 |

---

## 10. 相关文件索引

| 文件 | 作用 |
|---|---|
| `SW/FLASH_AND_VERSION.md` §4.5 | S2 救砖链路方案 (ISS-080) —— 本清单的判据来源 |
| `SW/EVT_TEMPLATE.md` §11 | EVT-8 / BR-01 可判项 —— 本清单对应 EVT 报告的 §11 |
| `SW/S2_VENDOR_QUESTION_LIST.md` | 原厂问询清单 (P1~P4) —— C-1 / C-2 的解法 |
| `SW/tools/s2_board_run.sh` | ★ 一条命令跑测 (含失败现场取证) |
| `SW/tools/s2_board_judge.py` | ★ CB-01~09 机械判定器 (三态, 缺数据必判未验) |
| `SW/tools/s2_board_selftest.sh` / `.py` | 板端自检 6 项 (CB-04) |
| `SW/tools/s2_rescue_config.json` | ★ 板端实跑配置 (P1~P4 落点 + 板端工位参数) |
| `SW/tools/s2_selftest.sh` | 无板先验 (L0/L1) —— ISS-080 交付, 仍应保持 rc=0 |
