# HW/AR0234CS_OPEN_SOURCE_FACTS.md —— AR0234CS 四个未知量的开源检索结论 (U1/U2/U3/U4)

| 项 | 内容 |
|---|---|
| 作者 | **hw-lead (硬件总工)** |
| 日期 | 2026-11-02 |
| 触发 | 老板 2026-11-02 19:25 指示: **不发任何邮件给任何厂家, 不做问询函; 先查开源渠道; 查一圈还有问题 ⇒ 直接放弃该方案/该物料, 考虑友商替换** |
| 本单范围 | AR0234CS 原计划发邮件问厂家的 4 个未知量, 各走一轮**开源**检索 ⇒ 给结论 (查到 / 查不到) + 证据 URL + 具体行/表/数值 + 查不到时的处置 |
| ★**纪律** | ★**不发邮件 / 不联系代理 / 不发帖问厂家** —— 本单 0 次对外通信, 全部证据来自公开可下载的第三方镜像与公开网页 |
| ★**不许写"应该可以"** | 查不到就写查不到; 查到了就给具体数值与页码, 不给形容词 |
| 写入范围 | 仅本文件 + `state/fragments/hw.yaml` (用 `state/frag_write.py` 原子写)。**未改** `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `HW/OPEN_SOURCE_AVAILABILITY.md` / `HW/AR0234CS_RK3572_PORT_SPEC.md` / `state/gen_netlist.py` / `HW/netlist_v1.csv` / `HW/POWER_BUDGET_V3.md` |
| ★**与 19:29 指示的关系 (必读, 免得误读)** | ★老板 **19:29** 那条 ("demo 不考虑功耗, sensor 只要能输出 1920×1080@60 的规格, 只考虑规格和数据来源是否充足") 收敛的是 **★demo sensor 的选型判据** (⇒ demo sensor 已定 **IMX415**, AR0234CS 留给整机方案)。★**本单不是 demo sensor 选型**, 而是 **AR0234CS 整机方案的硬件数据补全** (ISS-148 的 U1/U2/U3/U4), 任务书明确要求 4 个全查且 U1 优先 ⇒ ★**U1 (裸片功耗) 与 U3 (CRA) 查到的数据对 demo 路径确实没用, 但对整机路径直接有用**: ①**U1 直接决定 `HW/POWER_BUDGET_V3.md` 里那条 "0.92W ⇒ 拒绝 AR0234CS" 的否决理由成不成立** (§2.3) ②**U3 决定整机镜头是直线镜还是鱼眼 + ISP 校正** (§4.2)。★**若只看 demo 路径, 本文件 §2 (U1) 与 §4 (U3) 可直接跳过, §3 (U2) 与 §5 (U4) 才是 demo 也要用到的板级硬约束。** |
| 上游依据 | `HW/AR0234CS_RK3572_PORT_SPEC.md` §5 (卡点 R2/R3/R4) · `HW/OPEN_SOURCE_AVAILABILITY.md` (D1~D5 快照, 已有的结论不重复查) · `HW/SENSOR_SELECTION.md` §B4 (AR0234CS 官方口径: **CRA 0 数据 / 裸片功耗 0 数据 / 模拟轨清单 0 数据**) |
| 证据等级 | `[官方]` = onsemi 公开 datasheet 原文 (页码+表号+数值) · `[第三方]` = 模组厂/代理公开 spec · `[推算]` = 我从官方数据做的算术推导 (方法写明) · `[待核]` = 仍缺 |

---

## 0. 一句话结论 + 判定表

★**四个未知量全部用公开渠道查到了 (U3 只查到了曲线, 推荐镜头清单没查到), 换料触发条件不成立 ⇒ AR0234CS 保留。**

| 未知量 | 结论 | 关键数字 | 换料? | 处置 |
|---|---|---|---|---|
| **U1 ★★★ 裸片 active 功耗 @1920×1200@60** | ★**查到** | datasheet Table 1: **<395 mW @120 FPS, Full Resolution** (Typ) · Table 16 分轨工作电流 (MIPI 120fps): 合计 **Typ 372.6 mW / Max 646.4 mW** | **不换料** | ★**60 fps 无单独电流行** ⇒ 取 **上界 = 120 fps 行 (Typ 372.6 / Max 646.4 mW)** 做预算 (帧率与数据率均减半 ⇒ 单调更低) |
| **U2 ★★ VDD_IO 绝对最大额定值** | ★**查到** | Table 14: **VSUPPLY (All Supplies) −0.3 … 4.5 V** ⇒ VDD_IO abs-max = **4.5 V** (3.3V 上拉不伤 VDD_IO 轨) **但** Table 14 同表 `VIN DC Input Voltage = VDD_IO + 0.3 V = 3.1 V` ⇒ ★**3.3 V 上拉超 VIN 绝对最大额定值 0.2 V** | **不换料 (改设计)** | ★**I2C_A 上拉 3.3V → 2.8V (SENSOR_VDD_IO 轨)**, 改 **0 颗新器件** (只改上拉网络顶网); 同总线 5 个从设备逐个核 VIH (清单见 §3.3) |
| **U3 ★ CRA / 光学规格** | ★**部分查到** | Table 1: **Chief Ray Angle = 0° 或 28°** (两个 PN 变体!) · Table 2 全部 20 个 PN 按 `28`/`00` 分两族 · Figure 19 (p.23) 给出 **28° 变体的完整 CRA-vs-像高表: 角落 27.97° @ 像高 100% (3.396 mm = 对角半长)** · **AND9658-D 存在但内容在付费墙后 ⇒ 推荐镜头清单 + CRA 容差带 查不到** | **不换料** | ★**120° 只能鱼眼 + ISP 鱼眼校正** (老板 10-25 预设处置, 现由数据确认, 不再是"默认兜底") ★**PN 变体 (0° / 28°) 必须随镜头一起定**, 不定镜头不定 PN |
| **U4 ★ 有无独立模拟轨 (VAA 类)** | ★**查到 (比预期多)** | Table 5 引脚表: **VAA (2.8V, 4 ball) / VAA_PIX (2.8V, 4 ball) / VAA_PHY (2.8V, 1 ball)** + **VDDIO_PHY (1.8V only, 1 ball)** + VDD/VDD_PHY/VDD_DATA (1.2V) + VDD_IO (1.8/2.8V) · Note 10: **"VDDIO_PHY should be connected to 1.8 V only"** | **不换料** | ★**网表缺一条 VDDIO_PHY 1.8V 轨** (现只有 3 条) 且 ★**CONN_CAM 18p 已 18/18 占满, 加不出第 4 条轨** ⇒ **必须拍板 (连接器 18p→20p / 铰链侧本地生 1.8V / 放弃 2.8V VDD_IO 改 1.8V 但会打断 TMP117)** |

★**本单顺带查出 4 个"投板后必然要改"的问题** (详见 §5): ①I2C 地址注释 0x36→**0x10** (★**DT 侧已由并发任务改对, 剩 `netlist_v1.csv` row 153 注释没改**) ②I2C 上拉 3.3V 超 VIN 绝对最大额定值 ③**缺 VDDIO_PHY 1.8V 轨 + 铰链连接器无空脚** ④`netlist_v1.csv` 里 SENSOR_VDD_IO 在 pin16 的 value 字段还残留 "1.8V"。

---

## 1. 检索范围与用过的检索式

### 1.1 用过的检索式 (全部公开渠道, 0 次对外通信)

| # | 检索式 / 访问路径 | 目的 | 结果 |
|---|---|---|---|
| Q1 | `AR0234CS datasheet power consumption active mW 1920x1200 60fps` | U1 裸片功耗 | ★**首轮返回全垃圾** (搜索 provider 给了 RocketReach/Pink Floyd 等无关结果) ⇒ 弃用泛搜索, 改直取已知 URL |
| Q2 | `onsemi AR0234CS image sensor datasheet electrical characteristics VDD_IO absolute maximum rating` | U2 abs-max + 找 datasheet 镜像 | ★**命中 datasheet 正文片段** (Table 7 / Table 4 电气规格表) ⇒ 定位到两个可下载镜像 |
| Q3 | `AR0234 Sensor Optical Specifications AND9658-D-AR0234CS-OS` (scribd doc 947060899) | U3 AND9658-D | ★文档**存在** (标题/摘要公开) ★**正文在付费墙后, 取不到数值** |
| Q4 | `AR0234 global shutter camera module 0.92 W power consumption e-CAM217_CUMI0234_MOD` | U1 模组级交叉验证 | ★**命中 e-CAM 公开 spec 页**: 0.92 W 属**模组级 (含板载 ISP)** |
| Q5 | `onsemi AR0234CS orderable parts Active status product page` | U3 PN 变体在售状态 | ★命中 onsemi 产品页 JSON-LD `offers` (12 个 orderable part) |
| Q6 | `ar0234-rpi-driver ar0234-overlay.dts` (raw.githubusercontent) | U2/U4 电压假设 + I2C 地址交叉验证 | ★**命中 overlay 原文** (I2C 地址 0x10 / 三路 supply 2.8-1.8-1.2) |
| Q7 | `onsemi AR0234 AND9658 optical specifications document download` | U3 换路径再试 | ★无新公开源 ⇒ AND9658-D 正文判 **查不到** |

### 1.2 直接访问的公开 URL (成功)

| URL | 得到什么 | 状态 |
|---|---|---|
| `https://sunnywale.com/uploadfile/2022/0222/AR0234CS-D-Awin.PDF` | ★**AR0234CS/D datasheet, Rev 0 (March 2020)** — 全文 | HTTP 200, 468 314 B, sha256 `9db816dd…784d7f8` |
| `https://datasheet.lcsc.com/datasheet/pdf/bc2f0aa7c21d135010e4c1bb2abf3bd0.pdf?productCode=C5207402` | ★**AR0234CS/D datasheet, Rev 3 (Sept 2020)** — 全文 (★**本单主要引用版本**) | HTTP 200, 437 119 B, sha256 `61d55222…13dc0` |
| `https://www.onsemi.com/products/sensors/image-sensors/ar0234cs` | 产品页 (JSON-LD offers 列出 12 个 orderable part; 表 "Products: 12 / Orderable Parts: 12") | HTTP 200 (web_fetch; curl 被 Akamai 403) |
| `https://openipc.org/cameras/sensors/ar0234/` | 公开规格库条目 (2.3MP / 3µm / 1/2.6" / Global / 120fps / In production) | HTTP 200 |
| `https://raw.githubusercontent.com/Kurokesu/ar0234-rpi-driver/master/README.md` | 驱动能力 (2/4-lane ≤900 Mbps/lane, 1920×1200@120fps, 960×600@237fps) | HTTP 200 |
| `https://raw.githubusercontent.com/Kurokesu/ar0234-rpi-driver/main/ar0234-overlay.dts` | ★I2C 地址 `reg = <0x10>` + 三路 supply 电压假设 | HTTP 200 |
| `https://www.e-consystems.com/camera-modules/ar0234-global-shutter-camera-module.asp` | ★模组级 0.92 W + "dedicated Image Signal Processor (ISP)" + 1920×1200@60 | HTTP 200 |
| `https://www.ti.com/product/TPS7A20` | LDO 选型约束 (Iout max 0.3 A, Vout 档位含 1.2/1.8/2.8 V, 全部 X2SON) | HTTP 200 |

### 1.3 直接访问但**失败**的路径 (记录, 避免下轮重复)

| 路径 | 失败原因 | 影响 |
|---|---|---|
| `https://www.onsemi.com/pdf/datasheet/ar0234cs-d.pdf` (onsemi 官网 PDF) | **Akamai 403** (curl 与 web_fetch 均被拦); onsemi.com `/download/data-sheet/pdf/...` 302 跳到需登录的 technical-documentation | ★**onsemi 官网 PDF 直链取不到 ⇒ 走 LCSC / sunnywale 两个授权分销镜像** (同一 Publication Order Number: AR0234CS/D, 内容一致) |
| `https://www.mouser.com/datasheet/2/308/AR0234CS-1851120.pdf` | Mouser 反爬 (返回 "Please enable JS") | 改走 LCSC 镜像 |
| `https://www.scribd.com/document/947060899/AND9658-D-AR0238CS-OS` | **Scribd 付费墙 + fetch 超时** | ★**AND9658-D 正文数值查不到** (U3 唯一没拿到的部分) |
| `https://www.arducam.com/arducam-2mp-global-shutter-mipi-camera-module-with-on-semi-ar0234-sensor-p2373.html` | Cloudflare 403 | 改用 e-CAM + onsemi + openipc |
| `https://www.lcsc.com/product-detail/C5207402_...` (LCSC 商品页) | 页面 JS 渲染, 抓不到正文 | ★**但 LCSC 的 datasheet 镜像 (`datasheet.lcsc.com`) 可直接下载 ⇒ 不影响** |
| `https://www.onsemi.cn/pdf/datasheet/ar0234cs-d.pdf` | 跳转超限 | 同 1.3 第 1 行 |
| `raw.githubusercontent.com/.../ar0234.c` | fetch 超时 (42KB) | ★**驱动 .c 正文没读到** ⇒ U2 的电压假设改用 overlay + datasheet 原文交叉 (已足够) |

### 1.4 检索到的 datasheet 物理定位方法 (可复现)

```bash
cd /tmp/ar0234
curl -sSL -o lcsc.pdf  "https://datasheet.lcsc.com/datasheet/pdf/bc2f0aa7c21d135010e4c1bb2abf3bd0.pdf?productCode=C5207402"
curl -sSL -o sun.pdf   "https://sunnywale.com/uploadfile/2022/0222/AR0234CS-D-Awin.PDF"
pdftotext -layout lcsc.pdf lcsc.txt      # 全文 1483 行
pdftotext -layout sun.pdf  sun.txt       # 全文 1455 行 (Rev 0)
# 页码定位:
for p in $(seq 1 24); do
  pdftotext -layout -f $p -l $p lcsc.pdf - | grep -q "ABSOLUTE MAXIMUM RATINGS" && echo "p$p ABS MAX"
done
```
★**Rev 3 (2020-09) 与 Rev 0 (2020-03) 是同一份 Publication Order Number (AR0234CS/D) 的两个版本, 内容有差异** (见 §2.1 U1 与 §4 U3) ⇒ **本单一切引用以 Rev 3 为准, Rev 0 仅用于交叉验证。**

---

## 2. U1 ★★★ 裸片 active 功耗 @1920×1200@60

### 2.1 结论: ★**查到** —— 但 datasheet 给的是 **120 FPS 档**, 不是 60 FPS 档

★**证据 A (Table 1, p.1, Rev 3, 2020-09) —— 抬头栏是 "Typical Value"**:
```
Table 1. KEY PERFORMANCE PARAMETERS
 Parameter                       | Typical Value
 ...
 Supply Voltage
   I/O                            | 1.8 or 2.8 V
   Digital                        | 1.2 V
   Analog                         | 2.8 V
 Operational Power Consump-      | <395 mW at 120 FPS, Full Resolution
 tion
```
- URL: `https://datasheet.lcsc.com/datasheet/pdf/bc2f0aa7c21d135010e4c1bb2abf3bd0.pdf?productCode=C5207402`
- 页码/表号: **p.1 / Table 1**
- 提取文本 (Rev 3, `pdftotext -layout` 第 60 行): `Operational Power Consump-              <395 mW at 120 FPS, Full Resolution`

★**证据 B (Table 1, p.1, Rev 0, 2020-03)** —— 同一行在旧版是 **<420 mW**:
- URL: `https://sunnywale.com/uploadfile/2022/0222/AR0234CS-D-Awin.PDF`
- 提取文本 (Rev 0, 第 58 行): `Operational Power Consump-              <420 mW`
- ⇒ ★**两版差 25 mW ⇒ 本单一律用 Rev 3 的 395 mW。**

★**证据 C (Table 16, p.18, Rev 3) —— 分轨工作电流, 这是可复算的硬数据**:
```
 Table 16. OPERATING CURRENT CONSUMPTION FOR MIPI OUTPUT
 (VAA = VAA_PIX = VDD_IO = VAA_PHY = 2.8 V; VDD = VDD_PHY = VDD_DATA = 1.2 V;
  VDDIO_PHY = 1.8 V; PLL Enabled and PIXCLK = 90 MHz; TA = 25 °C; CLOAD = 10 pF)
   Symbol                  Parameter                            Condition              Typ    Max   Unit
  IDD_PHY +      Digital Operating Current   MIPI, Streaming, Full Resolution 120 fps   155   250   mA
  IDD_DATA +
      IDD
     IDD_IO       I/O Digital Operating Current   MIPI, Streaming, Full Resolution 120 fps   0.2   1     mA
  IDDIO_PHY       I/O PHY Digital Operating Current  MIPI, Streaming, Full Resolution 120 fps  10    12    mA
  IAA_PHY +      Analog Operating Current        MIPI, Streaming, Full Resolution 120 fps   55    102   mA
      IAA
    IAA_PIX       Pixel Supply Current           MIPI, Streaming, Full Resolution 120 fps   5     13    mA
```

★**我的复算** (方法: 每轨 `V × I` 求和; 这是 `[推算]`, 但输入全是 `[官方]`, 算术可复核):

| 轨 | 电压 | Typ (mA) | → Typ (mW) | Max (mA) | → Max (mW) |
|---|---|---|---|---|---|
| VDD + VDD_PHY + VDD_DATA (数字+MIPI) | 1.2 V | 155 | 186.0 | 250 | 300.0 |
| VDD_IO (I/O 数字) | 2.8 V | 0.2 | 0.56 | 1 | 2.8 |
| VDDIO_PHY (I/O PHY) | 1.8 V | 10 | 18.0 | 12 | 21.6 |
| VAA + VAA_PHY (模拟) | 2.8 V | 55 | 154.0 | 102 | 285.6 |
| VAA_PIX (像素) | 2.8 V | 5 | 14.0 | 13 | 36.4 |
| **合计 (裸片, 1920×1200, MIPI 120fps)** | | | **372.6 mW** | | **646.4 mW** |

★**自洽校验**: 372.6 mW (Typ) < 395 mW (Table 1 抬头) ✔ —— **表 1 的 "<395 mW" 与 Table 16 分轨求和一致, 互为佐证**。
★**第二个自洽校验**: 各轨 Max 求和 = 250+1+12+102+13 = 378 mA < Table 14 的 `ISUPPLY Total Power Supply Current Max 400 mA` ✔ —— 再次互证。
★**第三层交叉 (模组级)**: e-CAM217_CUMI0234_MOD 公开 spec **0.92 W** (`https://www.e-consystems.com/camera-modules/ar0234-global-shutter-camera-module.asp`, 抓取到的原文含 "has a dedicated Image Signal Processor (ISP)") ⇒ **0.92 W 是"模组 = 裸片 + 板载 ISP + 镜头座 + 模组板级"的合计, 不是裸片。**

### 2.2 ★ 60 fps 怎么取数 (诚实说明 datasheet 没给 60 fps 电流行)

★**datasheet 没有 60 fps 的工作电流行。** 全部电流表只有两档:
- **Table 16 (p.18)**: MIPI, Full Resolution, **120 fps**
- **Table 15 (p.17)**: **Parallel** output, Full Resolution, **30 fps** (条件同 2.8V/1.2V/1.8V, CLOAD 10 pF)

★**Table 3 (p.2) 证明 60 fps 是 datasheet 承认的模式**:
```
 Table 3. FRAME RATES FOR MASTER, AUTOMATIC TRIGGER AND MULTI-SENSOR SYNC MODE
   Resolution      Interface   Frame Rate (frames per second)
   Full_Resolution  MIPI        120
   1920x1200                    60
                             30
                    Parallel    30
   2x2_Binning      MIPI        237
   960x600                      120
                             60
                    Parallel    30
```
(Table 4 "PULSE TRIGGER MODE": Full_Resolution 1920×1200 MIPI = 60 / 30 fps; Parallel = 30 fps —— **60 fps 在两种触发模式下都被 datasheet 承认**。)

★**取数处置 (本项目采用, 写死进预算)**:

| 口径 | 值 | 依据 | 用途 |
|---|---|---|---|
| ★**预算上界 (Typ)** | **≤ 372.6 mW** (表头口径 ≤ 395 mW) | 60 fps 的帧率与数据率均为 120 fps 的一半 (1920×1200×10bit×60 = 1.382 Gbps vs 120fps 4-lane 时 2.764 Gbps) ⇒ 读出与 PHY 动态功耗单调更低; 模拟/像素偏置 (IAA 55 mA + IAA_PIX 5 mA) 基本与帧率无关 (对照 Table 15 @30fps: IAA 50 mA vs Table 16 @120fps: 55 mA, 只差 10%) | 整机功耗/续航预算 |
| ★**预算上界 (Max, 最坏角)** | **≤ 646.4 mW** | 同上, 用 Table 16 Max 列求和 | 散热/降额/电池最坏情况 |
| **中值估计** | **~300 mW (Typ)** | `[推算]` 用 Table 15 (30 fps) 与 Table 16 (120 fps) 两点对帧率线性插值 (帧率减半 ⇒ 动态项减半, 偏置项不变) | 规划用, **不得当实测值** |

★**为什么这个上界是安全的 (不是"应该可以")**:
1. 帧率↑ ⇒ 每秒读出的像素数↑ ⇒ 数字动态功耗↑ ⇒ 60 fps 的数字动态项**严格小于** 120 fps 行;
2. 模拟/像素偏置项与帧率无关, 用 120 fps 行的值是**保守偏大**;
3. 本项目 60 fps 用 **2-lane** (datasheet 120 fps 满帧默认 4-lane, 见 Table 1 "Frame Rate: Full resolution 120fps (4-lane MIPI), Default" 与 Table 19 "Data bit rate max 900 Mb/s"), 总线数据量与 lane 数同时下降 ⇒ PHY 动态功耗进一步降低;
4. ⇒ **用 120 fps 行的 372.6 / 646.4 mW 做 60 fps 上界, 在物理上成立, 不是拍脑袋。**

★**60 fps 的精确值仍然记为 `[待核]`** —— 只有实测能闭合 (EVT 阶段用电流表测 60 fps 三条轨即可, 见 §7-④)。

### 2.3 ★★ 由此产生的口径修正 (必须让 PM 知道, 但不由我改 POWER_BUDGET)

`HW/POWER_BUDGET_V3.md` 第 405 行现记:
> `| 20 | sensor 0.92 W 模组级是**拒绝理由** (非接受值) | **不变** (V3 下并入则整机 1.54 W → 整机上界 112.2°C = 整机方案否决) | **不变** | §9-2 |`

★**这条的"0.92 W"是 e-CAM 模组级 (含板载 ISP), 而本项目的架构是"AR0234CS 裸片 + RK3572 做 ISP"** (RK3572 rkisp3, 见 `HW/AR0234CS_RK3572_PORT_SPEC.md` §2 C5/C6)。
⇒ **本项目 sensor 侧的净增功耗应该是裸片数 (0.373 W Typ / 0.646 W Max), 不是 0.92 W**; 0.92 W 里的 ISP 那一块在 RK3572 那边另算。
⇒ ★**"0.92 W ⇒ 96°C 皮肤 ⇒ 拒绝 AR0234CS"这条否决理由, 在本项目架构下口径不成立 ⇒ 需要 PM 按裸片数重算散热与续航。**
⇒ ★**我没有改 `HW/POWER_BUDGET_V3.md` (超出本单写入范围) —— 已按 state 协议登记 `needs_from` 给 PM (见 §7-①)。**

---

## 3. U2 ★★ VDD_IO 绝对最大额定值 (决定 I2C_A 上拉能不能留 3.3V)

### 3.1 结论: ★**查到 —— 而且结论比"3.3V 能不能留"更狠: 3.3V 上拉在 sensor 侧是超绝对最大额定值的**

★**证据 (Table 14, p.17, Rev 3) —— ABSOLUTE MAXIMUM RATINGS 全表**:
```
 Table 14. ABSOLUTE MAXIMUM RATINGS
   Symbol      Parameter                                  Min      Max    Unit
  VSUPPLY     Power Supply Voltage (All Supplies)        −0.3     4.5     V
   ISUPPLY    Total Power Supply Current                   −      400     mA
    IGND      Total Ground Current                         −      400     mA
     VIN      DC Input Voltage                           −0.3   VDD_IO + 0.3  V
    VOUT      DC Output Voltage                          −0.3   VDD_IO + 0.3  V
    TSTG      Storage Temperature (Note 16)               −40    +125     °C
```

| 问 | 答 | 依据 |
|---|---|---|
| VDD_IO 轨本身的绝对最大额定值 | ★**4.5 V** (所有供电轨统一一行 VSUPPLY) ⇒ **3.3 V 上拉不会伤 VDD_IO 这条轨** | Table 14, p.17 |
| ★**但 I2C 引脚 (SDATA/SCLK) 上的直流电压上限** | ★**VIN max = VDD_IO + 0.3 V = 2.8 + 0.3 = 3.1 V** ⇒ **3.3 V 上拉把 SDA/SCLK 拉到 3.3 V, 超绝对最大额定值 0.2 V** | Table 14, p.17 |
| 上拉电阻允许值 | **1.5 kΩ ~ 4.7 kΩ** (`SDATA Pull-up Resistor RSD`), datasheet 建议 **1.5 kΩ 到 VDD_IO** | Table 6, p.13 |
| I2C 电平门限 | **VIH = VDD_IO × 0.7 = 1.96 V / VIL = VDD_IO × 0.3 = 0.84 V**; Table 6 Note 3 说明时序按 **VIHmin = 0.9×VDD_IO = 2.52 V / VILmax = 0.1×VDD_IO = 0.28 V** | Table 13 (p.16) + Table 6 Note 3 (p.13) |
| 灌电流能力 | @2.8 V: **IOL max 9 mA / IOH max 12 mA**; @1.8 V: 7 mA | Table 13, p.16 |
| ★**注意区分: 别把 AR0237CS 的数搬过来** | ★AR0237CS (1/2.7", **另一个器件**) 的 abs-max 表有独立行 `VDD_IO_MAX = 4 V` / `VAA_MAX = 4 V` / `VAA_PIX_MAX = 4 V`。**AR0234CS 没有这一行, 它用统一的 VSUPPLY 4.5 V 行 + VIN = VDD_IO+0.3 行。** 搜索引擎很容易把 AR0237CS 的 PDF 混进来, 抄错就会得出"VDD_IO abs-max = 4 V"的错误结论 | 交叉核对两份 datasheet |
| 官方 I2C 地址 | ★**默认从地址 0x20 (写) / 0x21 (读) ⇒ 7-bit = 0x10**; 拉高 **SADDR** 可选 **0x30 (写) / 0x31 (读) ⇒ 7-bit = 0x18**; 也可用 **R0x31FC** 改写 | datasheet 正文 p.11 (Rev 3, 第 553~559 行) |
| ★公开 RPi 驱动的地址 | ★`ar0234@10` / `reg = <0x10>` ⇒ **与 datasheet 一致 (7-bit 0x10)** | `raw.githubusercontent.com/Kurokesu/ar0234-rpi-driver/main/ar0234-overlay.dts` |
| ★**本项目现状 (部分已改, 仍有一处错)** | ★`HW/AR0234CS_RK3572_PORT_SPEC.md` §3 的 DT **已改对** (`reg = <0x10>; /* ★★★ 本单实测 3 个来源一致 = 0x10 (E2) */`, 19:59 由并发任务改) ⇒ ★**DT 侧没问题了**; ★**但 `HW/netlist_v1.csv` row 153 (TMP117 那条) 的 note 仍写 "与 sensor 0x36 / 桥接 0x50 / 充电 IC 0x12 / 光机 0x72 都不冲突"** ⇒ ★**这处注释还是 OV04C10 时代的, 会误导后续核地址冲突的人**; ★`HW/SCHEMATIC_V1.md` 的 "sensor 0x36" 字样同理 | 本地文件 grep (2026-11-02 20:05 复核) |

### 3.2 ★ 处置: I2C_A 上拉 **3.3 V → 2.8 V**, 且 **0 颗新器件**

★**为什么必须改 (不是"保守起见")**: VDD_IO = 2.8 V 时, Table 14 的 `VIN ≤ VDD_IO + 0.3 = 3.1 V` 是**绝对最大额定值**; 3.3 V 上拉 ⇒ 长期超出 0.2 V ⇒ 属"违反绝对最大额定值", 不是"余量偏小"。
★**怎么改 (零 BOM 增量)**: 上拉电阻顶网从 `RAIL_VDD_3V3_IO` 换到 **`RAIL_SENSOR_VDD_IO`**。
- `RAIL_SENSOR_VDD_IO` = 2.8 V, 由 **U_LDO_S28B (TPS7A20-28)** 在 **MAIN_PCB (P1)** 产生 (`netlist_v1.csv`: `P1,SENSOR_VDD_IO,RAIL_SENSOR_VDD_IO,U_LDO_S28B,...TPS7A20-28,IC`)。
- 上拉电阻 `R_PU_I2CA_SCL` / `R_PU_I2CA_SDA` 也在 **MAIN_PCB (P2)** ⇒ ★**同一块板、同一处, 只改一个 net 名, 不动器件、不动连接器、不动跨铰链走线**。
- ★上拉阻值保持 **4.7 kΩ** (datasheet Table 6 允许 1.5~4.7 kΩ 的上限值; 灌电流 = 2.8 V / 4.7 kΩ = 596 µA ≪ IOL max 9 mA ✔)。

### 3.3 ★ 同总线从设备逐个核 VIH (老板指定的"核同总线从设备"清单 —— 5 个)

★**降上拉 = 把总线高电平从 3.3 V 降到 2.8 V ⇒ 风险方向反过来了: 现在要核的是"从设备能不能把 2.8 V 认成高电平" (VIH), 不是"会不会被打坏"。**

| # | 从设备 | 地址 | 供电 | 核什么 | 状态 |
|---|---|---|---|---|---|
| 1 | **AR0234CS** (U1, 跨铰链) | 0x10 | 2.8 V (VDD_IO) | VIH = 0.7×2.8 = **1.96 V** ✔ 2.8 V 够; VIL = 0.84 V ✔; IOL 9 mA vs 596 µA ✔ ⇒ **通过** | `[官方]` Table 13 + Table 6 ✔ |
| 2 | **TMP117** (U_TEMP, 主板) | 0x48 | **3.3 V** (RAIL_VDD_3V3_IO) | ★**TMP117 的 VIH 通常按 0.7×VDD 定义 ⇒ 3.3 V 供电时 VIH ≈ 2.31 V > 2.8 V? 否, 2.8 > 2.31 ✔**; 但 **必须以 TI TMP117 datasheet 实测/规格行核对, 不采信"通常"** | `[待核]` —— 需 TI TMP117 datasheet 的 VIH 规格行 |
| 3 | **桥接 IC** | 0x50 | 见网表 | 同上 (VIH 门限 vs 2.8 V) | `[待核]` —— 具体型号未定 ⇒ 无 datasheet 可核 |
| 4 | **充电 IC** | 0x12 | 见网表 | ⚠️注: `HW/SCHEMATIC_V1.md` L649 记 "充电 IC 的 I2C 本板自闭环 (不跨铰链)" ⇒ **若充电 IC 实际不在 I2C_A 上, 本条可删** ⇒ 先确认拓扑 | `[待核]` —— 拓扑待确认 |
| 5 | **光机** | 0x72 | 见网表 | ⚠️注: `HW/SCHEMATIC_V1.md` L291/292 显示光机在 **I2C_B** (总线 B, 主板侧) ⇒ **大概率不在 I2C_A 上 ⇒ 本条可删** ⇒ 先确认拓扑 | `[待核]` —— 拓扑待确认 |
| 6 | **RK3572 侧** (I2C0/I2C1, GPIO0_B0/B1) | — | ★**GPIO0 所属 VCCIO 域电压未从 datasheet 定死** | ★RK3572 的 abs-max 表把 **VCCIO1_VCC 归在 "1.8V only GPIO supply voltage (max 1.98 V)"** 一栏, 而 I2C0/I2C1 脚 (GPIO0_B0/B1) 落在 **VCCIO1 分组的 GPIO0 组** ⇒ ★**若属实, SoC 侧 GPIO0 绝对最大只允许 1.98 V, 则 3.3 V 与 2.8 V 上拉都超 SoC 侧 abs-max ⇒ 整个 I2C_A 电平域要重新设计 (不是只改上拉)** | ★★**`[待核]` 高优先 —— 见 §7-②, 这条可能比 sensor 侧更硬** |

★**推论 (若第 6 条坐实)**: I2C_A 的正确解法可能是 **整条总线降到 1.8 V** (VDD_IO 也改 1.8 V, 上拉 1.8 V) 或 **加电平转换**, 而不是停在 2.8 V。★**⇒ U2 的最终值取决于第 6 条, 我不把它写成"已闭环"。**

---

## 4. U3 ★ CRA / 光学规格

### 4.1 结论: ★**部分查到** —— CRA 数值与整条曲线都拿到了; **唯一没拿到的是 AND9658-D 的"推荐镜头清单 + CRA 容差带"**

★**证据 A (Table 1, p.1, Rev 3)**: `Chief Ray Angle    0° or 28°` ⇒ ★**AR0234CS 有两个 CRA 变体, 是不同 PN, 不是同一料的两档规格。**

★**证据 B (Table 2, p.2, Rev 3) —— AVAILABLE PART NUMBERS, 20 个 PN 按 CRA 分两族**:
```
 Table 2. AVAILABLE PART NUMBERS
   Part Number                    Product Description                  Orderable Product Attribute Description
 AR0234CSSM28SUKA0−CP             2.3MP 1/2.6", Mono, 28° CRA         CSP Chip Tray with Protective Film
 AR0234CSSM28SUKA0−CR             2.3MP 1/2.6", Mono, 28° CRA         CSP Chip Tray without Protective Film
 AR0234CSSM28SUKA0−CP1            2.3MP 1/2.6", Mono, 28° CRA         CSP Chip Tray with Protective Film Low MOQ
 AR0234CSSM28SUD20                2.3MP 1/2.6", Mono, 28° CRA         Bare Die
 AR0234CSSM28SUKAH3−GEVB          2.3MP 1/2.6", Mono, 28° CRA         Demo Headboard
 AR0234CSSM00SUKA0−CP             2.3MP 1/2.6", Mono, 0° CRA          CSP Chip Tray with Protective Film
 ... (同上五行, 00 族)
 AR0234CSSC28SUKA0−CP             2.3MP 1/2.6", RGB, 28° CRA          CSP Chip Tray with Protective Film
 ... (同上五行, 28 族)
 AR0234CSSC00SUKA0−CP             2.3MP 1/2.6", RGB, 0° CRA           CSP Chip Tray with Protective Film
 ... (同上五行, 00 族)
 NOTE:   Please check with an ON Semiconductor sales representative for availability of these parts.
```
★**PN 编码规律 (可复用)**: `AR0234CS` + `S` + `M`(Mono)/`C`(RGB) + **`28`/`00`** + `SUKA0`(CSP 托盘) / `SUD20`(Bare Die) / `SUKAH3-GEVB`(Demo Headboard) ⇒ **`28`/`00` 就是 CRA 变体位**。
★**Rev 0 (2020-03) 与 Rev 3 (2020-09) 的差异 (关键)**: Rev 0 里 **0° 族全部带 `-E` 后缀 = "Engineering Samples"** (如 `AR0234CS3M00SUKA0-CP-E`, `AR0234CS3C00SUKA0-CP-E`), 且 28° 族多一个 `-CR1`; **Rev 3 把 0° 族的 `-E` 去掉 ⇒ 0° 变体从"工程样品"变成可订料**。
★**onsemi 官网产品页 JSON-LD `offers`** (12 个 orderable part) 里同时出现 `AR0234CSSM28SUKA0-CP` (28°) 与 `AR0234CSSC00SUKA0-CP` / `AR0234CSSC00SUD20` (0°) ⇒ **两个 CRA 变体都在售**。

★**证据 C (Figure 19, p.23, Rev 3 & Rev 0) —— 28° 变体的完整 CRA-vs-像高表**:
```
                                                   Image Height    CRA
                                          (%)      (mm)    (deg)
                                            0      0.000     0
                                            5      0.170     1.61
                                           10      0.340     3.20
                                           15      0.509     4.79
                                           20      0.679     6.36
                                           25      0.849     7.91
                                           30      1.019     9.45
                                           35      1.189     10.97
                                           40      1.358     12.46
                                           45      1.528     13.93
                                           50      1.698     15.38
                                           55      1.868     16.79
                                           60      2.038     18.18
                                           65      2.208     19.54
                                           70      2.377     20.86
                                           75      2.547     22.15
                                           80      2.717     23.39
                                           85      2.887     24.60
                                           90      3.057     25.77
                                           95      3.226     26.90
                                          100      3.396     27.97
                            Figure 19. Chief Ray Angle − 285
```
★**读表要点 (硬件判定用)**:
- 图横轴 "Image Height (%)" 0→100 对应 **0 → 3.396 mm**。3.396 mm = **对角线的一半** (AR0234CS 对角 6.79 mm, `HW/SENSOR_SELECTION.md` §B4: 5.760×3.600 mm, 对角 6.79 mm) ⇒ **这条曲线的横轴其实是"到角落的径向距离", 100% 点 = 图像对角最角落** ⇒ 角落 CRA = **27.97°**。
- ⇒ **28° 变体: 角落主光线入射角 ≈ 28°, 沿半径平滑单调上升 (0 → 27.97°), 无突变** ⇒ 这条曲线可直接交给镜头厂做匹配。
- ★**`[推算]` 变体归属**: 该曲线峰值 27.97° ≈ 28° ⇒ **这条是 28° 变体的曲线; 0° 变体的曲线不在公开 datasheet 里** (全文只有 Figure 19 这一个 CRA 图, 见 §1 抓取的图注清单 Figure 1~19)。
- ★`[待核]` **AND9658-D**: 文档确实存在 —— Scribd 公开条目 `https://www.scribd.com/document/947060899/AND9658-D-AR0234CS-OS`, 标题 "AR0234 Sensor Optical Specifications", 摘要公开写明含 "optical specifications ... chief ray angle ... **recommended lenses, CRA tolerances**, and spectral characteristics" ⇒ ★**存在性确认, 但正文 (推荐镜头表 + CRA 容差带 + 推荐光圈/畸变指标) 在付费墙后 ⇒ 判"查不到"**。★按老板的规矩: **不发问询函, 不追 AND9658-D**。

★**证据 D (生态交叉验证, 第三方) —— 120° 直线镜的可行性**:
- `https://ca.finance.yahoo.com/news/vadzo-imaging-introduces-bolt-234cgs-140000424.html` (Vadzo 官方新闻稿转载): "The Bolt-234CGS ships with a **default S-Mount (M12) lens at 74 degree DFOV**" ⇒ ★**工业界把 AR0234 配的默认镜头是 74° DFOV, 不是 120°**。
- `https://www.e-consystems.com/camera-modules/ar0234-global-shutter-camera-module.asp`: 同样 "interchangeable M12 (S-mount) lens", 模组默认也是 S-Mount 口径。
- ⇒ **[推算]**: 28° CRA 的 sensor 配 74° 级 S-Mount 镜头是生态默认; 要做 **116.75° / 120° 对角 FOV** 的**直线镜**, 角落主光线入射角会远超 28° ⇒ **CRA 失配 ⇒ 角落阴影/色偏/串扰 ⇒ 直线镜方案不成立**。

### 4.2 处置: ★**走鱼眼 + ISP 鱼眼校正** (老板 10-25 预设处置) —— 但现在有数据, 不再是"默认兜底"

| 项 | 判定 |
|---|---|
| 120° 对角 FOV 能否配**直线镜** | ★**不能** (角落 CRA 需求 ≫ 28°, 与 74° DFOV 生态默认值一致) |
| 120° 对角 FOV 配**鱼眼** | ★**走鱼眼 + ISP 鱼眼校正** (老板 10-25 原则) ⇒ **处置与老板预设一致, 且由数据确认** |
| ★**PN 变体怎么选 (0° 还是 28°)** | ★**必须与最终镜头一起定**: 0° 族对应"主光线近乎垂直入射"的镜头形式 (近远心/鱼眼式布置), 28° 族对应普通直线镜头。⇒ **镜头定版 ⇒ 同时定 PN**。★**注意: 0° 变体在 Rev 0 (2020-03) 还是 "Engineering Samples" (-E), Rev 3 (2020-09) 才变成可订 ⇒ 采购窗口要按 Rev 3 的 PN 列表核 (onsemi 官网 12 个 orderable part 里已含 0° 族)** |
| ★**CRA 容差带 (±多少度算匹配)** | ★**查不到** (在 AND9658-D 付费墙后) ⇒ **处置: 按业界通用 ±3° 带做设计裕量, 并把"镜头厂提供 CRA 曲线 (随镜头一起给)" 写进镜头 RFQ 硬判据** —— ★**这是问镜头厂 (我们自己的镜头供应商), 不是问 onsemi ⇒ 不违反老板的禁令** |
| ★**ISP 侧** | 鱼眼校正 (dewarping) 预算进 RK3572 rkisp3 —— 与 `HW/AR0234CS_RK3572_PORT_SPEC.md` §2 C5 (rkisp3 format/帧率协商) 同批做, **不额外加料** |

---

## 5. U4 ★ 有无独立模拟轨 (VAA 类) —— ★**查到, 而且比预期多一条轨**

### 5.1 结论: ★**有, 共 5 组供电; 我们网表只有 3 组 ⇒ 缺 1 组 (VDDIO_PHY 1.8V), 且连接器已占满**

★**证据 (Table 5, p.8~p.9, Rev 3) —— PIN DESCRIPTIONS − 83-BALL CSP PACKAGE**:
```
   Name          CSP Ball                    Type      Description
   VAA           A10, B1, G2, G7             Power     Analog Power (2.8 V)
   VAA_PHY       F8                          Power     Analog PHY power supply. Analog power supply for the serial interface (2.8 V).
   VDD_PHY       C8                          Power     MIPI Power Supply (1.2 V)
   VDDIO_PHY     D10                         Power     I/O Power Supply (1.8 V)
   VDD           A4, A8, A12, B10, D7, E1, G8 Power    Digital Power (1.2 V)
   VDD_DATA      F11                         Power     MIPI PHY Power (1.2 V)
   VAA_PIX       B8, C2, G1, G9              Power     Pixel Power (2.8 V)
   VDD_IO        A7, B4, B5, B11, D3, D6, F1, G12  Power  I/O supply power (1.8 V or 2.8 V)
   AGND          A9, C3, G3, G6              Power     Analog GND
   DGND          A2 A3, A6, B2, C1, C5, D8, D9, E2, E8, F2, F9, G10   Power  Digital GND
   GNDIO_PHY     B12, E7                     Power     Connect to DGND.
   CAP_1UF_PHY   F12                         Power     External bypass capacitor for MIPI Regulator
   RSVD          F10                         Input     Must be connected with 1.5 kΩ resistor between this pin and DGND.
   Reserved      A11, B9                     N/A       Reserved (do not connect)
   TEST          F5                          Input     Manufacturing test enable pin (connect to DGND)
   SADDR         A5                          Input     Two-Wire Serial address select
   SCLK          F6                          Input     Two-Wire Serial clock input
   SDATA         E6                          I/O       Two-Wire Serial data I/O
```

★**Block Diagram 的供电分组 (Figure 2/3, p.5~6) + Note 8/9/10/19**:
```
 Notes:
  6. ON Semiconductor recommends that 0.1 mF and 10 mF decoupling capacitors for each power supply are mounted as close as
     possible to the pad. ... Refer to the AR0234CS demo headboard schematics for circuit recommendations.
  7. ON Semiconductor recommends that analog power planes be placed in a manner such that coupling with the digital power
     planes is minimized.
  8. It is recommended that VDD_PHY and VDD_DATA are tied to VDD (1.2 V).
  9. It is recommended that VAA_PHY is connected to 2.8 V.
 10. VDDIO_PHY should be connected to 1.8 V only.
 ...
 19. The following supply rails can be connected together.
     1. VDD, VDD_PHY and VDD_DATA
     2. VDD_IO and VDDIO_PHY if 1.8 VDC each
     3. VAA, VAA_PHY and VAA_PIX
```
★**Table 22 POWER-UP SEQUENCE (p.20, Rev 3) —— 上电时序也是硬要求**:
```
  SN  Definition                                  Symbol  Min    Typ   Max  Unit
   1  VAA/VAA_PIX/VAA_PHY to VDDIO                 t1       0     100     −   ms
   2  VDDIO to VDDIO_PHY                           t2       0     100     −   ms
   3  VDDIO_PHY to VDD/VDD_PHY                     t3       0     100     −   ms
   4  VDD/VDD_PHY to VDD_DATA                      t4       0     100     −   ms
   5  Xtal Settle Time (Component Dependent)        tx       −      30     −   ms
   6  Hard Reset                                   t5       1       −     −   ms
   7  Internal Initialization                      t6   160000       −     −   EXTCLK
   8  PLL Lock Time                                t7       1       −     −   ms
 23. VDD and VDD_DATA can be tied together (t4 becomes '0' in this case).
 24. VAA/VAAPIX/VAA_PHY can be tied together.
```
★**Table 23 POWER-DOWN SEQUENCE (p.21) + Figure 16 (p.21)**: 断电顺序 = 上电逆序 (VDD_DATA → VDD/VDD_PHY → VDDIO_PHY → VDDIO → VAA 族)。

★**表 13 DC ELECTRICAL CHARACTERISTICS (p.16) 的供电电压表 (交叉确认)**:
```
  VDD       Core Digital Voltage      1.14   1.2    1.26   V
  VDD_IO    I/O Digital Voltage       1.7/2.5 1.8/2.8 1.9/3.1  V
  VDDIO_PHY I/O Power Supply          1.7     1.8    1.9    V
  VAA       Analog Voltage            2.5     2.8    3.1    V
  VAA_PIX   Pixel Supply Voltage      2.5     2.8    3.1    V
  VDD_PHY   MIPI Supply Voltage       1.14    1.2    1.26   V
  VDD_DATA  MIPI Supply Voltage       1.14    1.2    1.26   V
  VAA_PHY   MIPI Supply Voltage       2.5     2.8    3.1    V
```

### 5.2 ★★ 与本项目网表逐条对照 —— **查出 2 个板级硬伤**

`HW/netlist_v1.csv` 现状 (grep `SENSOR_` 轨):

| datasheet 轨 | 电压 | 本项目网表 | 状态 |
|---|---|---|---|
| VDD + VDD_PHY + VDD_DATA | 1.2 V | `RAIL_SENSOR_CORE` (U_LDO_S12, TPS7A20-12) → CONN_CAM pin17 | ✔ **Note 8 + Note 19.1 允许并轨, 现状正确** |
| VAA + VAA_PHY + VAA_PIX | 2.8 V | `RAIL_SENSOR_AVDD` (U_LDO_S28, TPS7A20-28) → CONN_CAM pin15 | ✔ **Note 19.3 允许并轨, 现状正确** |
| VDD_IO | 1.8 或 2.8 V | `RAIL_SENSOR_VDD_IO` (U_LDO_S28B, TPS7A20-28) → CONN_CAM pin16 | ✔ 存在 (2.8 V) |
| ★**VDDIO_PHY** | ★**1.8 V (only)** | ★**网表里没有** | ★★**缺一条轨** |
| AGND / DGND | — | `GND` 单一网络 + pin18 独立回流地 | ⚠️ Note 5 "Analog and digital grounds need to be connected at a **single point**" ⇒ 需确认单点连接方案 (布局级) |

★**硬伤 ① —— VDDIO_PHY 缺轨, 且不能并到 VDD_IO**:
- Note 19.2 明确写: `VDD_IO and VDDIO_PHY if 1.8 VDC each` ⇒ **只有 VDD_IO 也是 1.8 V 时两者才可并**。
- 我们 VDD_IO = 2.8 V ⇒ **VDDIO_PHY 必须单独一条 1.8 V**; Note 10 更狠: `VDDIO_PHY should be connected to 1.8 V only` ⇒ **并到 2.8 V 是明确违规** (且 Table 13 给 VDDIO_PHY 只有 1.7~1.9 V 窗口)。
- ★**这一条对功耗有实测影响**: Table 16 里 IDDIO_PHY @1.8 V typ 10 mA / max 12 mA = 18 / 21.6 mW —— 数字不大, 但 **VDDIO_PHY 未供电时 MIPI PHY 的 I/O 不工作 ⇒ sensor 根本不出图** ⇒ **不补这条轨 = 板子直接废**。

★**硬伤 ② —— CONN_CAM 18p 已 18/18 占满, 加不出第 4 条 sensor 轨** (跨铰链连接器):
```
 pin1  CSI_D0_CK_P        pin10 CSI_D0_D3_P
 pin2  CSI_D0_CK_N        pin11 CSI_MCLK
 pin3  CSI_D0_D0_P        pin12 CSI_RESET_N
 pin4  CSI_D0_D0_N        pin13 I2C_A_SCL
 pin5  CSI_D0_D1_P        pin14 I2C_A_SDA
 pin6  CSI_D0_D1_N        pin15 SENSOR_AVDD (2.8 V)
 pin7  CSI_D0_D2_P        pin16 SENSOR_VDD_IO (2.8 V)
 pin8  CSI_D0_D2_N        pin17 SENSOR_CORE (1.2 V)
 pin9  CSI_D0_D3_P        pin18 GND (跨铰链回流地, 独立 pin)
```
⇒ **18 脚全占**。三条候选出路 (★都不是我能单方面定的, 见 §7-③):

| 方案 | 做法 | 代价 | 风险 |
|---|---|---|---|
| **A** | 跨铰链连接器 **18p → 20p** (加 1.8 V PHY 轨 + 1 备用) | ★**连接器 + 铰链 FPC + 两侧板改版 + BOM 增** | ★**改连接器 = 结构/机电/PCB 三方协同 + 重投板风险**; 但最干净 |
| **B** | 铰链侧 (camera 板) **本地生成 1.8 V** (从已有 2.8 V 轨再降压, 或从 SYS 轨) | ★**camera 板加 1 颗 LDO + 去耦**; 跨铰链脚数不变 | 需确认 camera 板上有什么轨可用; 多一颗 LDO = 多一个噪声源 (TPS7A20 7 µVrms, 可接受) |
| **C** | **把 VDD_IO 也改成 1.8 V** ⇒ VDD_IO + VDDIO_PHY 并成一条 1.8 V (Note 19.2) | ★**零新增连接器脚; 零新增 LDO** | ★**I2C_A 整条总线必须降到 1.8 V** ⇒ **TMP117 供电 3.3 V (VIH≈2.31 V) 认不了 1.8 V 高电平 ⇒ 要么给 TMP117 换 1.8 V 供电, 要么加电平转换** ⇒ 影响面反而更大 |
| ★**D (不可行, 已用官方数据排除)** | 把 VDDIO_PHY 并到 VDD_IO (2.8 V) | 0 | ★**Note 10 + Table 13 明确违规 (VDDIO_PHY 窗口只有 1.7~1.9 V)** ⇒ 直接排除, 不用再讨论 |

★**我的推荐 (供老板拍板)**: **方案 B** —— 理由: ①跨铰链 18p→20p 动的是机械最脆的一环 (铰链寿命/FPC 弯折半径), 收益只是多一条 1.8 V; ②方案 C 波及 I2C_A 全总线 (TMP117 + 可能的光机/充电 IC), 连带风险比加一颗 LDO 大; ③camera 板上加一颗 TPS7A20-18 (X2SON, 与板上其它 LDO **同封装 ⇒ 换料不换板**, 与 `netlist_v1.csv` 里 "TPS7A20 全部固定档共用 X2SON 封装" 的既有结论一致) 成本与风险都可控。
★**但 B 的前提 (camera 板上能拿到什么轨) 我没查** ⇒ 列为 `[待核]` §7-③。

★**另两条器件级硬要求 (datasheet 明写, 网表未见)**:
- `RSVD` (F10) = **必须用 1.5 kΩ 电阻接在 RSVD 与 DGND 之间** (Table 5) ⇒ 网表里要加一颗 1.5 k。
- `CAP_1UF_PHY` (F12) = **MIPI 内部稳压器外部旁路电容, 1 µF** ⇒ 网表里要加一颗 1 µF (注意: **不是** 10 µF 体电容)。
- `TEST` (F5) = **接 DGND**; `Reserved` (A11, B9) = **不接**。
- `SADDR` (A5) = 决定 I2C 地址 (拉高 ⇒ 0x18, 拉低 ⇒ 0x10) ⇒ ★**必须明确接法, 否则地址不定 ⇒ 驱动枚举不到** (★**注: DT 侧的 0x36 已被并发任务改对, 但这条 SADDR 接法 + netlist row 153 注释还没人动 ⇒ 地址这块仍剩半条尾巴**)。

### 5.3 ★ 上电/断电时序 (datasheet Table 22/23) —— 本项目现状缺口

★datasheet 要求 5 条轨**按序**上电 (各步间 0~100 ms, 典型 100 ms), 断电逆序。
本项目现状: 三条 sensor 轨 (SENSOR_CORE / SENSOR_AVDD / SENSOR_VDD_IO) 全部从 `RAIL_SYS` 直接来, **网表里没有 sensor 轨之间的时序控制元件** (`netlist_v1.csv` 里 `EN_*` / `PG_*` 只出现在 P8 (SoC 电源域), 没有 sensor 轨的) ⇒ ★**上电顺序目前是"随机" (三条 LDO 各自使能) ⇒ 与 Table 22 不符**。
★**Table 22 的 Min = 0 ms** ⇒ 三条轨**同时**上电在 min 栏是允许的 (间隔下限为 0), 但 **Note 8/23 允许的并轨数决定了不能全并**: VDD 族与 VAA 族可各并成一轨, 但 **VDDIO (2.8 V) 必须在 VAA 族之后 (t1), VDDIO_PHY 在 VDDIO 之后 (t2), VDD/VDD_PHY 在 VDDIO_PHY 之后 (t3)** ⇒ ★**最低限度仍需保证 "模拟 2.8 V 先、数字 1.2 V 后" 的顺序**。
⇒ ★**处置: 加一个 RC 延时 + 使能链 (或用 SoC GPIO 拉 EN 顺序) 实现 "VAA族 → VDD_IO → VDDIO_PHY → VDD族"** —— 这是 §7-③ 的第二个待拍板项 (属于原理图改动, 我不出图, 只给约束)。

---

## 6. §③ 友商候选排序 —— ★**本轮不触发 (U1 查到了)**

★**触发条件**: "若 U1 查不到 ⇒ 给友商候选排序 + 推荐"。★**U1 查到了 (datasheet Table 1 + Table 16) ⇒ 不触发换料 ⇒ AR0234CS 保留, 不做替换。**
★**下面这张表按老板的要求保留存档** (万一后续 EVT 实测推翻 60 fps 预算, 备用), 候选池 = IMX415 / OV02B10 / AR0521 / OV9281 / OG02B10 / OG02C10, 筛子三条 = ①≥1920×1080@60 ②Rockchip BSP 有驱动 ③rkaiq isp3x 有现成 IQ。

| 候选 | ① ≥1080p60 | ② Rockchip BSP 驱动 | ③ rkaiq isp3x IQ | ★**卡在哪一条** | 结论 |
|---|---|---|---|---|---|
| **IMX415** | ✔ 3840×2160 (远超) | ✔ `imx415.c` (Rockchip 参考 sensor) | ✔ 有 | ★**都不卡, 但卡在硬指标之外**: 1/1.8" 靶面太大 (对角 ~7.4 mm), 做不出 116.75° 对角 FOV 的镜头 (焦距算下来太短) + **滚动快门** (装在镜框上沿刚性绑定, 俯仰时直立物体会斜切 ⇒ YOLO 框错位) | ★**最接近但仍否** (靶面 + 快门) |
| **AR0521** | ✔ 2592×1944@60 | ✔ `ar0521.c` | ✘ 无 IQ | ★**卡快门**: electronic rolling shutter + global reset, **不是全局快门** ⇒ 直接否 | 否 |
| **OV9281** | ✘ 1280×800@120 | ✔ `ov9281.c` | ✘ 无 IQ | ★**卡分辨率**: 1280×800 低于 1920×1080 | 否 |
| **OV02B10** | ✘ 1600×1200**@30** | ✔ `ov02b10.c` | ✔ 有 IQ | ★**卡帧率** (30 fps, 不到 60) + 靶面 1/5" 太小 ⇒ 焦距算不出来 | 否 |
| **OG02B10 / OG02C10** | ★**本单未查** (不在 `HW/OPEN_SOURCE_AVAILABILITY.md` §2.1 表内) | ★**未查** | ★**未查** | ★**本单未做独立核实** ⇒ 不给结论 (不写"应该可以") | ★`[待核]` — 若 U1 被推翻需补查 |
| **OV04C10 (原 C 路)** | ✔ 2688×1520@60 / 1920×1080@80 | ✘ | ✘ | ★**全网 0 个仓库 (D4=0)** ⇒ 驱动从零写 + 等豪威给寄存器表 | 否 (原判) |

★**老板提醒 (本轮再次确认)**: ★**这些候选里没有一个同时满足 "≥1080p60 + 全局快门 + 有现成驱动 + 有现成 IQ"** ⇒ **即使 U1 真出问题, 正确动作也是做一次驱动移植 (5.5 人日, `HW/AR0234CS_RK3572_PORT_SPEC.md` §2 C1~C6 已算清), 而不是带一个不可知的功耗上板。**

---

## 7. [待核] 清单 (本单遗留, 按优先级)

| # | 优先级 | 待核项 | 为什么没在本单闭合 | 归谁 | 怎么闭 |
|---|---|---|---|---|---|
| ① | ★★★ | **整机散热/续航按"裸片 0.373 W Typ / 0.646 W Max"重算** (替换 `HW/POWER_BUDGET_V3.md` §9-2 里的 "0.92 W 模组级") —— 0.92 W 含模组板载 ISP, 本项目 ISP 在 RK3572 上 ⇒ 口径不同 | ★`HW/POWER_BUDGET_V3.md` **在本单禁写范围**内 | **PM** (needs_from 已登记) | PM 复算 POWER_BUDGET_V3 §9-2 + MECH 皮肤温度判据; 若过 ⇒ AR0234CS 的"拒绝理由"撤销 |
| ② | ★★★ | **RK3572 GPIO0 (I2C0_SCL=GPIO0_B0 / I2C0_SDA=GPIO0_B1, 球位 1K21 / U32) 所属 VCCIO 域的电压** —— RK3572 abs-max 表把 VCCIO1_VCC 列在 "1.8V only GPIO supply voltage (max 1.98 V)" 一栏, 而 GPIO0 组紧跟 VCCIO1_VCC ⇒ ★**若属实, 3.3 V 与 2.8 V 上拉都超 SoC 侧 abs-max, I2C_A 电平域要整体重设计** | ★本单检索范围是 **AR0234CS** 的 4 个未知量; RK3572 的 bank 归属需查 Rockchip 完整 IO domain 表 (本地 `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` 是 pdftotext 转出的**扁平引脚表**, 没有 bank↔GPIO 对照表, 只能靠引脚表顺序推断 ⇒ 不能当结论) | **hw-lead + sw-lead** | ★查 Rockchip 官方 RK3572 IO domain / VCCIO 分组表 (或 BSP `rk3572.dtsi` 的 `io-domains`/`pinctrl` 里的 `rockchip,pins` + 原理图 VCCIO 供电网名) ⇒ ★**这条不核, U2 的最终改法不能定稿** |
| ③ | ★★★ | **VDDIO_PHY 1.8 V 轨怎么供 (方案 A 20p 连接器 / 方案 B 铰链侧本地 LDO / 方案 C VDD_IO 改 1.8 V)** —— ★**且 CONN_CAM 18p 已 18/18 占满** | ★属**跨专业拍板** (连接器 = 结构/机电, LDO = 电源, I2C = 板级), hw-lead 不能单方定 | **老板 / PM + mech-lead** | ★老板拍板选 A/B/C; 选 B 需 mech-lead 给出 camera 板可用供电轨清单 |
| ④ | ★★★ | **60 fps 裸片实测功耗** (datasheet 无 60 fps 电流行, 只有上界) | ★只有实测能闭合 | hw-lead | EVT: 断 3 条轨 (1.2 V / 2.8 V VDD_IO / 2.8 V VAA族 / **+1.8 V VDDIO_PHY**) 分别串表测 60 fps 与 120 fps, 记录 Typ/Max |
| ⑤ | ★★ | **sensor 轨上电时序** (Table 22: VAA族 → VDD_IO → VDDIO_PHY → VDD族, 各 0~100 ms) 怎么实现 (RC 延时 / SoC GPIO 拉 EN) | ★需原理图级方案 (本单只出事实) | hw-lead | 出 EN 链方案 (用 TPS7A20 的 EN 脚 + RC 或 GPIO) |
| ⑥ | ★★ | **I2C_A 同总线 5 个从设备的 VIH vs 2.8 V** (TMP117 / 桥接 / 充电 IC / 光机 / RK3572) | ★桥接/充电 IC/光机型号未定, 无 datasheet 可核; 且要先确认后两个是否真在 I2C_A 上 | hw-lead + sw-lead | 逐个查各自 datasheet 的 VIH 规格行 (★注意 TMP117 若改 1.8 V 供电需重核) |
| ⑦ | ★★ | **I2C 地址收尾**: ★**DT 侧已改对** (`AR0234CS_RK3572_PORT_SPEC.md` §3 `reg = <0x10>`, 19:59 并发任务已改) ⇒ ★**剩 `netlist_v1.csv` row 153 的 note 仍写 "sensor 0x36" 要改** + **明确 `SADDR` (A5) 硬件接法** (拉低 = 0x10 / 拉高 = 0x18) | ★`HW/netlist_v1.csv` 与 `HW/SCHEMATIC_V1.md` **在本单禁写范围**内 | **项目总工 / sw-lead** | 改 netlist row 153 注释 0x36→0x10 + 原理图加 SADDR 接地电阻 + R_PU_I2CA 顶网 3.3V→2.8V |
| ⑧ | ★★ | **netlist 数据修正**: `netlist_v1.csv` 中 `P5,SENSOR_VDD_IO,...,CONN_CAM pin16,...,1.8V,NET` 的 **value 字段仍是 "1.8V"** (轨实际 2.8 V) —— 换料时残留 | ★`HW/netlist_v1.csv` **在本单禁写范围**内 | **项目总工 / gen_netlist** | 改 `state/gen_netlist.py` 里的 value 来源, 重生成 |
| ⑨ | ★ | **镜头厂提供 CRA 曲线 (随镜头一起) + CRA 容差带** (因 AND9658-D 拿不到) | ★**问的是我们自己的镜头供应商, 不是 onsemi ⇒ 不违反老板禁令** | pm-lead / mech-lead | ★写进镜头 RFQ 硬判据: "提供所选镜头在 1/2.6" (AR0234CS) 靶面上的 **CRA-vs-像高曲线 + 该镜头的角畸变/相对照度** |
| ⑩ | ★ | **PN 变体 (0° / 28°) 随镜头一起定** + 确认 0° 族在 onsemi 12 个 orderable part 内的具体料号与交期 | ★取决于镜头定版 | pm-lead | 镜头定版当天下 PN; 采购按 Rev 3 的 20 个 PN 表核 |
| ⑪ | ★ | **AND9658-D 正文 (推荐镜头清单 + CRA 容差带)** | ★**Scribd 付费墙; 且按老板规矩不发问询函** ⇒ **判定: 永久放弃该文档, 用 §4.2 的替代路径 (镜头厂曲线 + 业界 ±3°)** | — | ★**已放弃, 不再追** |
| ⑫ | ★ | **OG02B10 / OG02C10 两条候选的 ①②③ 筛核** | ★U1 查到了, 本轮不触发; 且这两条不在 `HW/OPEN_SOURCE_AVAILABILITY.md` §2.1 表内 | hw-lead | 仅当 U1 被实测推翻时才补查 |

★**合规备注 (必须记录)**: AR0234CS/D datasheet 正文页脚带 **"CONFIDENTIAL AND PROPRIETARY — NOT FOR PUBLIC RELEASE"** 字样 (每页均有), ★**但该文件由 onsemi 的授权分销商 (LCSC / Sunnywale / Mouser / DigiKey) 公开分发**, 且 onsemi 官网产品页亦公开挂出该文档 ⇒ ★**属"公开可得的 datasheet", 本单据此取证合规; 但本文件只引用数值与页码, 不转载正文, 不外发该 PDF。**

---

## 8. 复算与复现

```bash
cd /tmp/ar0234
# ① 取 Rev 3 (主引)
curl -sSL -o lcsc.pdf "https://datasheet.lcsc.com/datasheet/pdf/bc2f0aa7c21d135010e4c1bb2abf3bd0.pdf?productCode=C5207402"
# ② 取 Rev 0 (交叉)
curl -sSL -o sun.pdf  "https://sunnywale.com/uploadfile/2022/0222/AR0234CS-D-Awin.PDF"
# ③ 转文本并定位
pdftotext -layout lcsc.pdf lcsc.txt
grep -n "Operational Power Consumption"          lcsc.txt   # → 第 60 行: <395 mW at 120 FPS
grep -n -A16 "ABSOLUTE MAXIMUM RATINGS"          lcsc.txt   # → 第 1043~1052 行
grep -n -A14 "OPERATING CURRENT CONSUMPTION FOR MIPI" lcsc.txt
grep -n "Chief Ray Angle"                         lcsc.txt
grep -n -A25 "AVAILABLE PART NUMBERS"             lcsc.txt
grep -n "VDDIO_PHY should be connected"            lcsc.txt
grep -n -A12 "POWER-UP SEQUENCE"                   lcsc.txt
# ④ 功耗复算 (§2.1): 1.2*155 + 2.8*0.2 + 1.8*10 + 2.8*55 + 2.8*5 = 372.6 mW (Typ)
#                1.2*250 + 2.8*1   + 1.8*12 + 2.8*102 + 2.8*13 = 646.4 mW (Max)
```

**本单产出物**: 本文件 + `state/fragments/hw.yaml` (原子写)。★**未改**: `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `HW/OPEN_SOURCE_AVAILABILITY.md` / `HW/AR0234CS_RK3572_PORT_SPEC.md` / `state/gen_netlist.py` / `HW/netlist_v1.csv` / `HW/POWER_BUDGET_V3.md`。

**证据等级**: datasheet 数值/表号/页码 = `[官方]` · e-CAM / Vadzo / openipc / RPi 驱动 = `[第三方]` · 我的算术 (求和/插值/对角线换算) = `[推算]` (方法已写明) · 仍缺 = `[待核]`。
