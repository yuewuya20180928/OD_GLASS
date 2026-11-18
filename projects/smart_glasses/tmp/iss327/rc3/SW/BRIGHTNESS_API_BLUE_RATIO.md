# SW/BRIGHTNESS_API_BLUE_RATIO.md —— 亮度 API 上的「可标定蓝通道占比量」 (ISS-226)

> **作者**: sw-lead (软件总工) · **日期**: 2026-11-16 · **版本**: v1.0 · **单号**: ISS-226
> **上游**: ★**ISS-134** (mech-lead 跨域 need `iss134_sw_blue_drive_ratio_cap`) ★ · **策略真源**: `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` (★本文件是它的 API 侧配套件★)
> **判据真源 (只读引用)**: `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §3 ② (蓝光占比上限, need 记作 §3.2) · §3 ⑥ (出瞳等效辐亮度折算, need 记作 §3.6)
>
> ★★**本文件只定义「接口 / 字段 / 标定方法」三件事** ★★
> ★★**本文件不含任何实测值** ★★ ⇒ ★**板端标定值 = `[0数据]`** ★★ (★板与屏不在本机★) ⇒ ★**任何人在本文件里填一个"看起来像实测"的数 ⇒ 门禁立刻红** ★★
> ★**零外发** · **本单实物 [实测] = 0 条** (★标 [实测] 的只允许是"本机脚本 / 本机文件实读"★)

---

## 0 一句话结论

★★**亮度 API 上留一个字段: `blue_channel_luminance_ratio_pct`** ★★ ——
★★**语义 = 面板蓝光通道辐亮度占白场辐亮度的百分比**, ★★**单位 %**, ★★**量程 [0, 25]** (★25% 是保守上限★), ★★**可标定** (★标定值从出厂标定表/实机标定表灌入★), ★★**板端当前 `status = uncalibrated` / `value = null`** ★★

⇒ ★**上游判据值一个不许动**: **上限 25%** · **名义 8.26%** (Y_B=0.0798 / 红 0.3850 / 绿 0.5017, 等辐射功率) · **出瞳 L_eye 1500 cd/m²** ★
⇒ ★**越限后果链**: L_eye > 1500 cd/m² ⇒ 掉出 IEC 62471 Exempt (RG0) 进 RG1 ⇒ 需要用户信息 / 标签说明 (★不是禁视警示, 那个要到 RG2 才有★) ★

---

## 1 这个量是什么 (语义定义)

| 项 | 定义 |
|---|---|
| **字段名** | ★`blue_channel_luminance_ratio_pct` ★ |
| **中文名** | 面板蓝光通道辐亮度占白场辐亮度百分比 |
| **分子** | 蓝光通道 (面板原色) 的辐亮度 |
| **分母** | 同工况下白场 (全白) 的总辐亮度 |
| **单位** | **%** (百分比, 一位小数; 内部建议存整数 ×10 即 per-mille, 避免浮点累积误差) |
| **量程** | **[0, 25]** ⇒ ★**25 是硬上限** (★不是"建议值"★) ★ |
| **名义值 (未标定时用)** | **8.26%** ★`[推算]`★ (DCI-P3 基色算: 0.0798 / (0.0798 + 0.3850 + 0.5017)) |
| **谁来测** | ★**不是 SW** ★ ⇒ ★**出瞳处光谱辐亮度实测** (★光谱辐射计 + 11 mrad 接受角, 见 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §3 ② / §3 ⑥ 的测量口径★) ⇒ **SW 只消费标定结果** |
| **谁来定上限** | ★**结构侧 (mech-lead)** ★ ⇒ SW 侧**只读引用 25%**, **不许自行放宽** |

★**为什么这个量必须放在 API 上而不是只写在文档里** ★:
★**(a) 它是运行时裁剪亮度码值的输入** ⇒ 没有它, SW 只能"要么全信面板 datasheet (没有), 要么拍一个常数" ⇒ **(b) 它必须能被第三方 (实验室 / 认证 / 售后) 灌值** ⇒ API 上没这个字段, 标定值就没地方落 ⇒ **(c) 它必须可被审计** ⇒ 谁灌的、什么时候灌的、什么依据, 要能查 ⇒ ★**所以它是 API 字段, 不是配置项, 更不是代码里的魔数** ★

---

## 2 接口定义 (SW 侧亮度 API)

> ★**实现状态**: ★**本单只交付定义, 不交付实现** ★ —— 整机面板 (视涯 0.49" SiOLED) 未定型, 亮度寄存器/码值空间均 `[0数据]`; demo 屏 (Waveshare 2.8" LCD) 只有单一背光码值, **没有逐通道码值** ⇒ **无蓝通道可设** ⇒ 该路线本字段登记 N/A (见 `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` §3.3)。

### 2.1 数据结构

```c
/* SW 侧显示亮度服务 (display brightness service) —— ISS-226 新增段
 * ★ 判据真源: MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md §3 ② (上限 25%) + §3 ⑥ (出瞳折算)
 * ★ 策略真源: SW/SW_BRIGHTNESS_CONTROL_POLICY.md
 * ★ 本段只定义接口; 实现等整机面板定型后再排 (整机路线·暂缓)
 */
#define ARS45_BLUE_RATIO_CAP_PCT        25      /* ★ 保守上限, 来自结构侧判据, SW 侧不许改 ★ */
#define ARS45_BLUE_RATIO_NOMINAL_PCT     826     /* ★ 名义 8.26% ×10 (per-mille) [推算] ★ */
#define ARS45_BLUE_RATIO_MAX_PERMILLE   250     /* ★ 量程上限 25.0% ×10 ★ */

typedef enum {
    ARS45_BLUE_RATIO_SRC_NONE      = 0,  /* ★ 未标定 ⇒ 用名义值 (降级 L-1) ★ */
    ARS45_BLUE_RATIO_SRC_LAB       = 1,  /* 出厂实验室标定 (出瞳光谱实测) */
    ARS45_BLUE_RATIO_SRC_FIELD     = 2,  /* 实机现场标定 */
    ARS45_BLUE_RATIO_SRC_DERIVED   = 3,  /* 由结构侧给定窗口反推 (降级 L-2) */
} ars45_blue_ratio_source_t;

typedef struct {
    /* ★★★ 本单新增的核心字段: 蓝通道辐亮度占白场辐亮度百分比 ★★★ */
    uint16_t blue_channel_luminance_ratio_pct_x10;  /* per-mille; 826 = 8.26% (名义值举例) */
    uint8_t  blue_channel_luminance_ratio_status;   /* ars45_blue_ratio_source_t */
    uint8_t  blue_channel_luminance_ratio_valid;    /* 0 = 不可信/未标定 */

    /* 标定元数据 (可审计: 谁灌的 / 何时 / 依据) */
    uint32_t blue_ratio_calib_id;                   /* 标定记录号 (单调递增) */
    uint32_t blue_ratio_calib_time_unix;            /* 标定时间 (UTC) */
    char     blue_ratio_calib_source[32];           /* 仪器 / 台架标识 */
    char     blue_ratio_calib_note[64];             /* 自由注记 (条件 / 测点 / 温度) */

    /* ★ 运行时上限 (由标定值 + 25% 上限反推, 见 §4) ★ */
    uint16_t luma_code_max;                         /* 白场亮度码值天花板 */
} ars45_display_brightness_t;
```

### 2.2 API 面

| API | 方向 | 语义 | 失败语义 |
|---|---|---|---|
| `ars45_display_get_brightness(ars45_display_brightness_t *out)` | 读 | 返回当前亮度状态 + ★**蓝通道占比量 (标定值 / 状态 / 元数据)** ★ | 出参置零 + 返回负值 |
| `ars45_display_set_brightness(uint16_t luma_code)` | 写 | 设定白场亮度码值 ⇒ ★**内部必须 clip 到 `luma_code_max`** ★ | 越界 ⇒ **夹紧并打点** (★不静默放过★) |
| `ars45_display_set_blue_ratio_calibration(const ars45_blue_ratio_calibration_t *cal)` | 写 (仅标定通路) | ★**灌标定值** ★ (★出厂/现场标定用★) | 参数非法 ⇒ 拒绝 + 保留旧值 |
| `ars45_display_get_blue_ratio_calibration(ars45_blue_ratio_calibration_t *out)` | 读 | 读回标定值 + 元数据 (★审计用★) | 同上 |

★**写接口的权限边界**: ★`set_blue_ratio_calibration` 走**标定通路** (★标定工装 / 产线 / 售后工具★), ★**不许普通应用调用** ⇒ ★**避免"运行时随手改标定值 ⇒ 放松上限"这条路** ★

### 2.3 标定值数据结构

```c
typedef struct {
    uint16_t ratio_pct_x10;                  /* ★ 标定出来的占比 (per-mille) ★ */
    uint32_t calib_id;
    uint32_t calib_time_unix;
    uint8_t  source;                         /* ars45_blue_ratio_source_t */
    char     instrument[32];                 /* 仪器标识 */
    char     note[64];
} ars45_blue_ratio_calibration_t;
```

★**本单板端这张表的内容 = `[0数据]`** ★ ⇒ ★**出厂表 (e.g. `/etc/ars45/display_calib.json`) 在本单里是空的, 不是"填了个 8.26 当实测"** ★

---

## 3 标定方法 (★只定义方法, 不许填实测值★)

### 3.1 标定怎么做 (来源: 结构侧判据的测量口径, ★只读引用★)

| 步 | 动作 | 依据 |
|---|---|---|
| **C-1** | ★**面板置于最坏工况**: 全白 / 100% APL / 90 Hz / 100% duty, 温度扫 -10 / 25 / 50 °C | `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §3 ① (怎么测) + §4 Z-4 |
| **C-2** | ★**出瞳面** (波导眼盒平面) 放光谱辐射计, 加 **11 mrad 接受角限孔**, 距出瞳 = 评估距离 (眼点距, 同类公开 18 mm) | 同上 §3 ⑤ (11 mrad / 评估距离) + §3 ⑥ (判据只锚出瞳) |
| **C-3** | 全谱扫描 380–780 nm | 同上 §3 ② (怎么测 ①) |
| **C-4** | 蓝光占比 = ★**460±20 nm 带内积分 ÷ 全谱积分** ★ | 同上 §3 ② (怎么测 ③) |
| **C-5** | ★**取全温区 / 全码值工况里的最大值** ⇒ 作为标定值 (★不是平均值★) | 同上 §3 ③-a (全温区最大值口径) |
| **C-6** | 把标定值 + 仪器 + 时间 + 工况注记写进标定表 ⇒ 灌进 API 的标定通路 | ★本文件 §2.3 ★ |

★**这套方法本身就是结构侧定的方法** ⇒ ★**SW 侧不重新发明测法, 只消费结果** ★

### 3.2 标定值不许手填 (★机器可判的一条★)

★**标定值只允许两条来源** ★:
① ★**实验室/现场台架的光谱辐亮度实测** ★ (★来源标记 `ARS45_BLUE_RATIO_SRC_LAB` / `_FIELD` + 仪器标识 + 时间戳★) ★
② ★**结构侧给定窗口反推** ★ (★来源标记 `_DERIVED`★)
⇒ ★**第三种情况 "有人在文档/代码里直接写一个百分数当标定值" = 不允许** (★哪怕写的是名义值 8.26% 也不行 —— 名义值只能由降级逻辑在运行时取, 不能冒充标定值★) ⇒ ★**门禁 C5 会红** ★

★**未标定时的行为 (降级 L-1)**: ★`status = ARS45_BLUE_RATIO_SRC_NONE` ⇒ ★**运行时按名义值 8.26% 反推码值天花板** ⇒ ★**偏保守 (名义 8.26% vs 上限 25%, 余量 3.03×) ⇒ 不会越限** ★

★**注意一个方向性**: ★**降级只会让 SW 更保守, 不会放松上限** ★ ⇒ ★**这是本设计的核心安全性质** ★

---

## 4 标定值 ⇒ 亮度码值天花板 (★反推公式, 只给方法, 不给数★)

```
★ 已知: 标定占比 r (%), 上限 C = 25%, 白场最坏工况下蓝通道码值占比 β
★ 求:   白场亮度码值天花板 luma_code_max

  约束 (最坏工况, 蓝通道码值随白场码值线性放大):
      r_actual(luma_code) = r · (luma_code / luma_code_max_panel) · β
      要求: r_actual ≤ C
  ⇒   luma_code ≤ C · luma_code_max_panel / (r · β)
```

| 符号 | 含义 | 来源 | 证据等级 |
|---|---|---|---|
| `r` | 标定出来的蓝通道占比 (per-mille → /1000 得 %) | 标定表 | `[实测]` (标定后) / `[推算]` (未标定时 = 8.26%) |
| `C` | 保守上限 **25%** | 结构侧判据 | `[推算]` (只读引用) |
| `luma_code_max_panel` | 面板亮度码值的物理满量程 | ★**面板 datasheet [0数据]** ★ (★视涯 datasheet 无亮度码值表★) | `[0数据]` |
| `β` | 白场最坏工况下蓝通道码值占白场码值的比例 | ★**整机面板驱动方案定, [0数据]** ★ | `[0数据]` |
| ⇒ `luma_code_max` | 白场亮度码值天花板 | ★**本单算不出数 (输入缺) ⇒ 不许编** ★ | ★`[0数据]`★ |

★**诚实结论**: ★**本单只能把这条反推关系写成公式与接口, 给不出数值** ★ ⇒ ★**因为两个关键输入 (面板码值满量程 / 蓝通道码值占比 β) 在整机面板定型前都是 `[0数据]`** ★ ⇒ ★**任何"我们算出来是 X%"的说法在本单都是编的** ★

★**降级 L-2**: ★**若 `r` 也不可用 (标定值被推翻) ⇒ 放弃自己算占比, 直接采用结构侧给定的 `luma_code_max`** ★ ⇒ ★**SW 侧退成"只认天花板, 不算占比"** ★

---

## 5 机器可读锚点 (门禁 `SW/tools/check_brightness_biosafety.py` 按本节复核)

```yaml
# BEGIN SW_BRIGHTNESS_API_ANCHORS
brightness_api:
  field: blue_channel_luminance_ratio_pct
  unit: percent
  range_min_pct: 0
  range_max_pct: 25
  nominal_pct: 8.26
  calibration:
    method: outpupil_spectral_band_integral
    band_nm: [440, 480]
    denominator: full_spectrum_380_780
    worst_case: max_over_temperature_and_code
  board_value: null
  board_status: uncalibrated
  board_evidence: "[0数据]"
# END SW_BRIGHTNESS_API_ANCHORS
```

★**门禁在本文件上核对什么 (C5)** ★:

| 序 | 核对项 | 红 ⇒ 说明 |
|---|---|---|
| ① | ★**字段名 `blue_channel_luminance_ratio_pct` 在本文件与策略锚点里都在** ★ | API 量被摘掉 ⇒ 红 |
| ② | ★**量程上限 == 25 且与策略锚点 `cap_pct` 一致** ★ | API 与策略各说各话 ⇒ 红 |
| ③ | ★**名义值 == 8.26** ★ | 名义值被改 ⇒ 红 |
| ④ | ★**标定方法四要素在位 (band 440–480 nm / 全谱积分 / 380–780 nm / 取最坏工况最大值)** ★ | 标定方法被删 ⇒ 红 |
| ⑤ | ★**`board_value` 仍是 `null` 且 `board_status` 仍是 `uncalibrated`** ★ | ★**有人手填了一个没来源的数 ⇒ 红** ★ |
| ⑥ | ★**本文件里不含任何"实测占比"式的具体数字** (★除 8.26% 名义值与 25% 上限外, 蓝通道占比不得出现第三个数★) ★ | 编造实测值 ⇒ 红 |
| ⑦ | ★**本文件缺失 ⇒ fail-closed 红** (★不许"文档没了就跳过"★) ★ | — |

---

## 6 与其它单的关系 / 边界

| 项 | 状态 |
|---|---|
| 结构侧判据 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` | ★**只读引用, 零写入** ★ |
| `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` | ★**同单产物 (策略侧)** ★ ⇒ ★**两者必须同改 (H-1 流程)** ★ |
| `SW/tools/check_brightness_biosafety.py` | ★**同单产物 (机器门禁)** ★ |
| demo 屏 (Waveshare 2.8" LCD) 亮度通路 | ★**只读引用** (`SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` §4.3, 单一背光码值 0xAB/0xAA) ⇒ ★**本单零写入** ★ |
| 整机面板亮度寄存器 / 码值空间 | ★`[0数据]` ★ ⇒ ★**本单只定义 API, 不写实现** ★ |
| `state/issue_log.yaml` | ★**零写入** (status 留给 main) ★ |

★**本单不实现任何亮度 API 代码** —— ★**理由: 整机面板未定型 (亮度寄存器 / 码值空间 / 蓝通道驱动方式全是 `[0数据]`), demo 屏无逐通道码值** ⇒ ★**现在写实现就是对着空气写, 后面必然返工** ★

---

## 7 自证复现命令

```bash
cd projects/smart_glasses
python3 SW/tools/check_brightness_biosafety.py             # rc=0
python3 SW/tools/check_brightness_biosafety.py --selftest  # rc=0
```
