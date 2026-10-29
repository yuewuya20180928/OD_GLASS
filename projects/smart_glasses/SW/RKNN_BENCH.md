# SW/RKNN_BENCH.md —— RKNN 转换链实测 + RK3576 端到端 ≤60ms 判定

> **产出方**: 软件总工 (sw-lead) · **日期**: 2026-10-29 · **对应 issue**: ISS-XXX (待项目总工补号)
> **派活方**: 项目总工 (main) · 2026-10-29 00:28
> **本单一句话**: 老板 10-28 19:05 拍板"ARS45 资料拿不到就切备选芯片", 选型报告 (`HW/SOC_BACKUP_TOP5.md`) 结论 RK3576 是唯一"算力+资料"双达标候选 —— 但 **端到端 ≤60ms 在 RK3576 上没有任何厂商公开实测值** ⇒ **只能靠实测**。本单去测它。
> **★ 本单完全不依赖酷芯微**, 全部在 PC 上做, 不等代理消息 ⇒ 目的是让 11-12 决策点变成**纯数据决策**。

---

## 0. 结论速览 (TL;DR)

| 项 | 值 | 证据等级 |
|---|---|---|
| RKNN INT8 转换 (target=rk3576) | **✅ 成功** (零报错), 产物 **10.09 MiB** (切后处理版, ≤15 MiB 板端槽位) | **[实测]** |
| 转换耗时 | load 0.17s + build(INT8 量化, 100 张校准) **36.2 s** | **[实测]** |
| NPU 单帧耗时 (纯 NPU, S5) | **本单未实测 (无板)**; 第三方 RK3576 公开实测锚点 **15.4~17.4 ms** (yolov5s@640 INT8 整链路上界) | **[0数据]** (我们自己的板) + **[公开实测·第三方]** |
| RKNN PC 仿真器耗时 | **334.5 ms/帧** (min 327.8 / avg 334.5 / max 342.3 / n=20) —— ★★ **不是 NPU 吞吐代理, 不许进预算** | **[推算·仿真]** |
| COCO val2017 F1 (INT8, 293 张) | **F1 = 0.3139** (P 0.3723 / R 0.2713) | **[实测]** |
| COCO val2017 F1 (FP32 同口径基线) | **F1 = 0.3182** (P 0.3742 / R 0.2767) ⇒ **INT8 量化损失 F1 −0.0043 (−1.4%)** | **[实测]** |
| **RK3576 端到端 ≤60ms (口径 A)** | **PASS (有条件)** —— 但**只能走"模式 A (显示等 OD, 显示帧率 ~25fps)"**; **要保 60fps 显示 ⇒ FAIL (67.0ms)** | **[推算]** |

> ★ **一句话给老板**: **"切到 RK3576 不会让端到端更糟"** —— RK3576 的可达状态 (55~57ms @ ~25fps) 与老板 10-25 已授权的兜底方案 (55.7ms @ 25.6fps) **完全一致**; 但 **"60fps 显示"这个目标在 RK3576 + 640×640 下达不成** (age 台阶 ⇒ 67.0ms), 要 60fps 就必须把 NPU 压到 **≤10.67ms** (降分辨率或换 yolov5n)。

---

## 1. 背景与方法沿用

### 1.1 沿用 10-28 那套方法 (不重写)

本单**沿用** sw-lead 2026-10-28 已做过的同类实测 (Apache-2.0 候选 → TF → ONNX → 切掉 74.7% NMS 后处理 → 静态 shape → 299 节点 / max_abs_diff=0 / COCO F1=0.4346), 脚本全部在库:

| 脚本 | 作用 | 本单是否复用 |
|---|---|---|
| `SW/tools/cut_postprocessor.py` | 把 NMS/TopK/Range 等 NPU 不友好算子从图里剪掉 (反向可达性剪图), 后处理外移到 CPU | ⚠️ **建了但本模型用不上** (见 §3.2.2) |
| `SW/tools/fix_static_shape.py` | 把动态 shape 固化成静态 shape (NPU 编译器要求静态输入) | ✅ 复用 (本模型本来就是静态 640×640) |
| `SW/tools/eval_od_accuracy.py` | COCO val2017 上的逐类 IoU 贪心匹配 → P/R/F1 (IoU=0.5, score≥0.3, **非官方 mAP**) | ✅ **同口径复用** (本单 `rknn_bench.py` 的匹配器逐行照抄它) |
| `SW/tools/int8_chain.py` | ARS45/Art.Galaxy 侧的 B0~B9 转换链 readiness 驱动器 | ❌ **不复用** (平台不同: Art.Galaxy ≠ RKNN) |
| `SW/tools/license_probe.py` | 模型许可证探测 | ❌ 本单不需要 (许可问题 10-28 已闭, 见 §1.3) |

### 1.2 RKNN 工具链 vs Art.Galaxy (为什么 RKNN 这条路确实"资料充足")

| 维度 | ARS45 (Art.Galaxy) | RK3576 (RKNN-Toolkit2) |
|---|---|---|
| 工具链可得性 | ❌ 原厂未交付 (Q9/Q11 未答) | ✅ **官方 pip 包, 本机已有 2.3.2** |
| 板端运行时 | ❌ 未知 | ✅ `rknn-toolkit-lite2` |
| PC 侧仿真推理 | ❌ 无 | ✅ simulator (`init_runtime()` 无 target) |
| 量化 | `pcq` (A733 经验) | ✅ `w8a8 / normal / channel` + 校准集 |
| 算子支持清单 | ❌ [0数据] | ✅ 官方文档 + 实测转换器报错信息 |
| **本单结论** | 转不了 | **转成了** —— RKNN 这条路的**资料维度确实过关** |

### 1.3 模型来源与许可

| 项 | 值 | 证据 |
|---|---|---|
| 模型 | `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx` | [实测] |
| 台账 ID | `MOD-YOLOV5S-640-ARS45-SRC` (`SW/MODEL_ASSETS.md` §1.2) | — |
| sha256[:16] | `20368be665f6f59a` —— **与台账一致** ✔ | [实测] |
| 输入 / 输出 | 输入 `images [1,3,640,640]`; 输出 `output[1,25200,85]` + `350[1,3,80,80,85]` + `498[1,3,40,40,85]` + `646[1,3,20,20,85]` | [实测] |
| 节点 / 算子 | 245 节点 / 12 类算子 (Mul 69, Conv 60, Sigmoid 60, Concat 17, Add 10, Slice 9, Reshape 6, MaxPool 3, Transpose 3, Sub 3, Pow 3, Resize 2) | [实测] |
| 许可 | **AGPL-3.0** (`SW/MODEL_LICENSE.md` §1.2) ⇒ 商用阻断项 **L4** 未闭 | [实测·溯源] |
| ★ 本单不改许可 | 换芯片 ≠ 换模型许可; **AGPL 阻断项在 RK3576 上原样存在** | — |

---

## 2. 环境与工具链 (实测)

### 2.1 板端实测: 本单**未做** (⚠️ 关键声明)

| 项 | 结果 | 证据 |
|---|---|---|
| 本机架构 | `x86_64` (Ubuntu 26.04, kernel 7.0.0) | [实测] |
| `adb devices` | **空** —— 无任何 RK 设备 | [实测] |
| `/proc/device-tree/compatible` | 不存在 (非 RK 设备树) | [实测] |
| **板端 NPU 耗时** | **[0数据] —— 本单没有 RK3576 板, 板端一次都没测过** | — |
| 本单能做的 | PC 侧**转换** + **仿真推理** + **精度** + **产物大小** | — |

> ★ **本报告里所有"端到端"数字都是 [推算]**, 不是 [实测]。**板端实测的第一件事就是打 S5 (纯 NPU 耗时)** (见 §5.3)。

### 2.2 PC 侧环境 [实测]

| 项 | 值 |
|---|---|
| 工具链 | **rknn-toolkit2 2.3.2** (`/home/yuewuya/miniconda3/envs/rknn`) |
| Python / onnx / numpy | 3.10.20 / 1.14.1 / 1.26.4 |
| `target_platform` | **`rk3576`** ✅ (2.3.2 的支持列表含 rk3576, 见 `rknn/api/rknn.py:89`) |
| 校准集 | 100 张 COCO val jpg (`~/Public/radxa_yolo/calib_yolov5_100`) → letterbox 640×640 (黑边) → `/tmp/rknn_bench/calib/` + `dataset.txt` |
| 复现脚本 | `SW/tools/rknn_bench.py` (一条命令跑完, 见 §7) |

---

## 3. ① RKNN 转换链实测

### 3.1 流程与命令

```bash
cd projects/smart_glasses
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py all
```

内部等价于:

```python
r = RKNN(verbose=False)
r.config(target_platform='rk3576', quantized_dtype='w8a8',
         quantized_algorithm='normal', quantized_method='channel',
         optimization_level=3)
r.load_onnx('~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx')
r.build(do_quantization=True, dataset='/tmp/rknn_bench/dataset.txt')
r.export_rknn('/tmp/rknn_bench/yolov5s_rk3576_int8.rknn')
```

> ★ **步间依赖**: `r.build(dataset=...)` 依赖 `calib` 步生成的
> `/tmp/rknn_bench/dataset.txt` ⇒ 脚本里 `convert` / `sim` / `acc` 三步在缺该文件时
> **会自动先跑 `calib`** (ISS-113, 2026-10-29 修) ⇒ §7 的每条命令都能在干净机器上独立跑。
> 详见 **§7.1 步间依赖表**。

### 3.2 转换结果

#### 3.2.1 产物 [实测]

| 项 | 值 |
|---|---|
| **转换** | **✅ 成功** (rc=0, 零报错) |
| 产物 (切后处理版, **板端真正能用的那个**) | `/tmp/rknn_bench/yolov5s_rk3576_int8_heads.rknn` |
| **产物大小 (切后处理版)** | **10,575,159 B = 10.09 MiB** |
| 产物 (完整模型版, 仅供参考) | `/tmp/rknn_bench/yolov5s_rk3576_int8_full.rknn` = 10,958,444 B = 10.45 MiB |
| 板端 model 槽位上限 | 15,728,640 B (15 MiB, `SW/FLASH_AND_VERSION.md` §4.1) |
| **装得下吗** | **✅ 装得下** (10.09 / 15 = 67%) |
| 量化参数 | `w8a8` / `normal` (min-max) / `channel` (per-channel) |
| load / build | 0.17s / **36.2 s** (100 张校准图) |
| 附: FP16 对照 (不量化) | 18,355,755 B = 17.51 MiB → **超 15 MiB 槽位** ⇒ **只有 INT8 版本可用** |
| 量化器告警 | `build: found outlier value ... model.0.conv.weight abs_mean 1.47 / abs_std 2.85 / outlier 28.488` (首层权重的离群值, 可能影响量化精度 —— 但实测 F1 只掉 0.0043, 影响可忽略) |

> ★ **这条本身就是个结论**: RK3576 上的 yolov5s INT8 产物 **10.45 MiB**, 与 ARS45 侧的 15 MiB 槽位预算**兼容** (ARS45 侧 `yolov5s-sim.quantize` 620 KB 是不含权重的小表, 不能比)。

#### 3.2.2 算子覆盖: 本模型**不需要** `cut_postprocessor.py` [实测]

| 算子 | 出现次数 | RKNN 2.3.2 转 rk3576 |
|---|---|---|
| Mul / Conv / Sigmoid / Concat / Add / Slice / Reshape / MaxPool / Transpose / Sub / Pow / Resize | 69/60/60/17/10/9/6/3/3/3/3/2 | ✅ **全部接受, 转换零报错** |
| NonMaxSuppression / TopK / Range / NonZero | **0** | — (本模型是 yolov5 **RT 抽取版**, 后处理本来就不在图里) |

> ⇒ **`cut_postprocessor.py` 在 RKNN 这条路上暂时用不上** —— 但它**必须留着**: 见 §3.2.4, 真正需要它的是另一种模型 (带内嵌 NMS 的导出件)。

#### 3.2.3 ★★ 转换器的 3 条告警 (板端必须知道) [实测]

```
build: The default input  dtype of 'images' is changed from 'float32' to 'int8' in rknn model for performance!
build: The default output dtype of 'output' is changed from 'float32' to 'int8' ...
build: The default output dtype of '350' / '498' / '646' is changed from 'float32' to 'int8' ...
```

⇒ **板端 runtime 拿到的输入/输出都是 int8 量化张量**, 不是 float32。板端代码必须显式处理 (要 float 就 `want_float=1`, 或自己按 scale 反量化)。**这是板端第一号返工点**。

#### 3.2.4 ★★★ 本单实测到的三个"坑" (都有复现命令)

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| **1** | **`onnx.mapping` AttributeError** | `load_onnx` 直接报 `AttributeError: module 'onnx' has no attribute 'mapping'` —— rknn-toolkit2 2.3.2 内部调 `onnx.mapping`, 而 `onnx/__init__.py` **不自动 import 这个子模块** | **加一行 `import onnx.mapping`** (在 `import rknn.api` 之前)。本脚本已内置 (`SW/tools/rknn_bench.py` 第 60 行) |
| **2** | **simulator 不吃 `load_rknn()` 的模型** | `init_runtime: RKNN model that loaded by 'load_rknn' not support inference on the simulator` | 必须 **`load_onnx()` + `build()` 在同一个 session 里**, 然后 `init_runtime()` (无 target = simulator)。`load_rknn()` 只能给真板用 |
| **3** | ★★ **INT8 输出张量的"量程混装"会把概率量化坏** | `output` 张量 (1,25200,85) 把**像素尺度坐标** (范围 −6.8 … 706.9) 和 **0~1 的概率** 混在**同一个 int8 张量**里 ⇒ 量化步长 = 706.9/127 ≈ **5.57** ⇒ 概率被量化成 0 或 ±5.57 ⇒ **检测结果直接报废** | **必须把后处理从图里切出去** (只留 3 路 raw head, CPU 侧解码) —— 这正是 `cut_postprocessor.py` 的用武之地。详见 §3.4 |

> ★ 坑 3 是本单**最有价值的发现之一**: 它解释了为什么"直接转 yolov5 ONNX 就能用"是错的, 也是 RKNN 这条路真正的坑在哪。

### 3.3 NPU 单帧耗时 —— ★★ 本单没有板, 只有仿真值

#### 3.3.1 仿真器耗时 [推算·仿真] (★ 不许当实测用)

| 指标 | 值 (切后处理版) | 值 (完整模型版) |
|---|---|---|
| min | 327.77 ms | 380.25 ms |
| avg | **334.48 ms** | 383.26 ms |
| max | 342.27 ms | 387.45 ms |
| p50 | 333.71 ms | 383.19 ms |
| 采样 | n = 20 帧 (同一输入, 预热 1 帧后计时) | n = 20 帧 |

> ★★ **必须说清楚**: rknn-toolkit2 的 PC simulator 是 **用 x86 CPU 模拟 NPU 执行量化图**, 它**不是 NPU 吞吐的代理**。本机实测: 同一模型 simulator ≈ **383 ms/帧**, 而 RK3576 的公开第三方实测是 **十几 ms 量级** ⇒ **相差 ~20~30 倍**。
> ⇒ **本报告的延迟预算里没有采用这个值**, 也不许别人把它当 "NPU 耗时" 填进去。脚本里它被单独命名为 `sim_latency_ms`, 且只有显式加 `--use-sim-as-npu` 才会进 e2e 计算 (且强制标 [推算·仿真])。

#### 3.3.2 仿真器 vs ONNX FP32 的一致性 [实测]

max_abs_diff (5 张 COCO 图, INT8 RKNN simulator vs ONNX FP32 / onnxruntime):

| 输出 | max_abs_diff (逐图) | 说明 |
|---|---|---|
| `output` (25200×85, 已解码) | 260 / 423 / 444 / 379 / 331 | ★ **大是必然的** —— 见坑 3 (int8 量程混装), **不是"模型坏了"** |
| `350` (80×80 head, pre-sigmoid logits) | 9.6 / 13.2 / 13.9 / 12.3 / 14.1 | INT8 量化的正常误差 (head 值域 ±41 ⇒ 步长 0.16) |
| `498` / `646` | 6.1~10.7 / 5.0~9.5 | 同上 |

> ★ **口径提醒 (SOUL.md 铁律)**: 纯 NPU 耗时 (S5) 与 SDK 总耗时 (含反量化 S6) 必须分开报。A733 上 SDK 总耗时比纯 NPU 高 **25%** (27.19 → 36.51 ms), 因为 SDK 强制 INT8→FP32 反量化。**RKNN 侧同理**: 本模型 4 个输出张量共 **2,142,000 个元素**, 若板端要 float 输出, 反量化开销不容忽视 ⇒ **板端应优先用 int8 输出 + 自己反量化**。

### 3.4 精度 (COCO val2017)

#### 3.4.2 精度结果 [实测] (COCO val2017, 293 张有标注图, 同口径)

| 模型 | P | R | **F1** | TP / FP / FN |
|---|---|---|---|---|
| **RKNN INT8 (rk3576, 切后处理版, PC simulator)** | 0.3723 | 0.2713 | **0.3139** | 583 / 983 / 1566 |
| ONNX FP32 (onnxruntime CPU, 同一批图 + 同一套解码) | 0.3742 | 0.2767 | **0.3182** | — |
| **INT8 量化损失** | −0.0019 | −0.0055 | **−0.0043 (相对 −1.4%)** | — |

★ **三条要点**:
1. **INT8 量化几乎无损** (F1 只掉 0.0043) ⇒ **"RKNN 这条路精度上过关"**。这是本单对选型最有利的一个数据点。
2. **量产放行门 G3 (F1 ≥ 0.30) 过了, 但余量很薄 (0.3139 vs 0.30, 只富余 0.0139)** ⇒ ⚠️ **风险**: 0.30 这个门限是从 TF OD API (SSD-MobileNetV2-FPNLite) 的配方继承过来的; 换成 yolov5s@640 后应当**重新定门限** (建议项目总工与项目总工定的 G3 门限一起重估)。
3. ★ **同口径对比 10-28**: 10-28 那次是 TF OD API SSD-MobileNetV2-FPNLite@320, **F1 = 0.4346** (300 张); 本次 yolov5s@640 的 **0.3139** 数值上更低 —— 但**模型与分辨率都不同** (yolov5s@640 的框更小更密, 在 IoU 0.5 的逐类匹配下更吃亏), **不能直接比高低**; 只能比"同一模型 INT8 vs FP32 的差" = **0.0043**。

#### 3.4.3 ⚠️ 不切后处理会怎样 (坑 3 的实证) [实测]

| 变体 | INT8 结果 |
|---|---|
| **切掉后处理** (只留 3 路 raw head, CPU 解码) | **F1 = 0.3139** ✅ |
| **不切** (用完整模型, 输出 `output` 张量) | **0 张检出 / F1 = 0.0000** ❌ (TP=0, FP=0) —— 同一批图、同一个 FP32 ONNX 参考是正常的 |

复现: `python3 SW/tools/rknn_bench.py acc --images 30 --no-cut`

#### 3.4.1 ★★ 评测口径校准 (本单踩的第二个大坑)

| 发现 | 证据 |
|---|---|
| ★ **模型输入是 RGB /255, 不是 0-255** | 用 0-255 喂 ⇒ COCO 图 139 的 top-100 检测 **maxIoU = 0.000** (全错); 改成 RGB/255 ⇒ **maxIoU = 0.956, 85/100 个检测 IoU ≥ 0.5** (对上了 GT 的 tv) [实测] |
| ★ **3 路 head (350/498/646) 是 pre-sigmoid 的原始 conv 输出** | head[...,4] (obj) 值域 −21.3 … +10.9, head[...,5:85] (cls) −37.2 … +10.3, head[...,0:4] (bbox) −9.8 … +11.3 —— 都不是 0~1 / 像素。**只有第 0 个输出 `output` 是解码后的** (obj∈[0,1], bbox∈[−6.8, 706.9] 像素) [实测] |
| ★ **`/home/yuewuya/Public/radxa_yolo/code/eval_tta_yolov5s_onnx.py` 的 `decode_yolov5_raw_outputs()` 对本模型是错的** | 它假设 head 已是 "0-1 的 obj/cls + 像素 xywh" ⇒ 按它解出来 63.9% 的 anchor 会被判为 score>0.3 (2073 个假框/图) ⇒ **F1 = 0**。这条要提给项目总工 (该文件在 A7S 封档项目区, 不属于本项目) |
| ★ A733 板端 `yolov5_pre_process_bgr.cpp` 传 uint8 0-255 | 那是给 **A733 的 int8 量化模型**用的 (量化吸收了 scale), 与 **FP32 ONNX 不是一回事** ⇒ 移植到 RK3576 时**不能照抄** |

**本单最终采用的评测口径** (与 `SW/tools/eval_od_accuracy.py` 严格同口径 ⇒ 可与 10-28 那次对比):
`letterbox(640×640, 黑边) → RGB → /255 → NCHW` → RKNN INT8 → 取 `output` 张量 → `score = obj × cls.max` → `score ≥ 0.3` → per-class NMS (IoU 0.45) → 逐类 IoU 0.5 贪心匹配 → P/R/F1。

---

## 4. ② 端到端预算重算 (口径 A, 曝光→出光)

### 4.1 沿用的延迟模型 (口径不改)

来源: `SW/SW_REQUIREMENTS.md` §10.2 · `SW/DISPLAY_MODE.md` §1.3 · `PROJECT_TRACKER.md` §3.3 · `DECISION_TABLE_Q1_Q4_Q17.md` §1.2

```
P60  = 16.67 ms   sensor 帧周期 @60fps
E    = 8.3  ms    曝光积分
R    = 8.3  ms    读出
S3   = 8.0  ms    ISP (含缩放)              ⇒ 曝光块 E+R+S3 = 24.67 ms  ★不可协商
S4   = 1.0  ms    预处理 (letterbox + 布局 + 归一化)
S5   = ???? ms    纯 NPU 推理               ← 本单要测的那一段
S6   = 2.0  ms    反量化 (A733 上占 SDK 总耗时 25% ⇒ 保守取 2ms)
S7   = 3.0  ms    decode + NMS (CPU)
S8   = 1.0  ms    画框
S9   = 3.0  ms    显示 TX (DSI TX / DP→DSI 桥)
S10  = 5.0  ms    光机逐帧延迟  ★[0数据] (走鹃Ⅱ 未公开逐帧延迟; 按目标值占位)

T_od = S4 + S5 + S6 + S7 = S5 + 6 ms

模式 A (显示等 OD, age=0):  e2e = 24.67 + T_od + 9                = T_od + 33.67
模式 B (异步, 显示不等 OD):  e2e = age×16.67 + 16.67 + S3 + 9     = (age+1)×16.67 + 17
                             age = ceil(T_od / 16.67)   ← ★台阶函数
```

### 4.2 NPU 耗时的取值来源 (★ 证据分级)

| 候选 | 值 | 证据等级 | 说明 |
|---|---|---|---|
| **我们自己的 RK3576 板** | **[0数据]** | — | **本单无板** |
| RK3576 yolov5s (SiLU) 640 INT8 = **57.5 FPS** | **17.39 ms** | **[公开实测·第三方]** | 官方 `airockchip/rknn_model_zoo` README 性能表 (RK3576@single_core)。★ 口径 = **整链路 FPS** ⇒ 可当作 **纯 NPU 的上界** |
| RK3576 yolov5s_relu 640 INT8 = **65.0 FPS** | **15.38 ms** | **[公开实测·第三方]** | 同上 (relu 变体, 比 SiLU 快 ~12%) |
| RK3576 yolov5n 640 INT8 = **112.7 FPS** | **8.87 ms** | **[公开实测·第三方]** | 同上 (换模型路线) |
| RKNN PC simulator | 383 ms | **[推算·仿真]** | ★ **不采用** (§3.3.1) |

**一致性交叉验证 (重要)**: 同一张官方表里 **RK3588 yolov5s_relu = 66.1 FPS = 15.13 ms**, 与本项目台账里的 "RK3588 = 15.1 ms" **吻合**; 而 PhotonVision 在 Orange Pi 5 (RK3588) 上实测的 YOLOv5 "Total Time" = **15034 ± 1734 µs (= 66.5 FPS)** —— 两者吻合到 **0.6%** ✔ ⇒ 这张表的口径可信。

> ⚠️ **证据分级诚实说明**: model_zoo 的性能表我是**通过搜索引擎快照读到的** (本机直连 `raw.githubusercontent.com` 超时, `github.com` 也超时) ⇒ 归类为 **[公开实测·第三方]** 而非 [官方]。

### 4.3 代入后的端到端 [推算]

| NPU 候选 | S5 | T_od | age | **模式 A (显示等 OD)** | 显示帧率 | **模式 B (异步 60fps)** |
|---|---|---|---|---|---|---|
| RK3576 yolov5s (SiLU) 17.39ms | 17.39 | 23.39 | 2 | **56.99 ms ✅** | **24.7 fps** | **67.01 ms ❌** |
| RK3576 yolov5s_relu 15.38ms | 15.38 | 21.38 | 2 | **54.98 ms ✅** | 26.0 fps | **67.01 ms ❌** |
| RK3576 yolov5n 8.87ms | 8.87 | 14.87 | 1 | **48.47 ms ✅** | 31.4 fps | **50.34 ms ✅ (60fps 保住了)** |

#### 4.3.1 台阶表 (NPU 耗时 → 端到端) [推算]

| S5 (ms) | T_od | age | 模式 A | 判定 | 模式 B (60fps) | 判定 |
|---|---|---|---|---|---|---|
| ≤ 10.67 | ≤ 16.67 | 1 | 50.34 ms | ✅ | **50.34 ms** | ✅ **60fps 保得住** |
| 10.67 ~ 16.67 | 16.67 ~ 22.67 | 2 | 50.34 ~ 56.34 | ✅ | **67.01 ms** | ❌ **超 7.0ms** |
| 16.67 ~ 20.33 | 22.67 ~ 26.33 | 2 | 56.34 ~ 59.93 | ✅ | 67.01 ms | ❌ |
| 20.33 ~ 26.33 | 26.33 ~ 32.33 | 2 | 59.93 ~ 65.93 | ❌ | 67.01 ms | ❌ |
| 26.33 ~ 33.33 | 32.33 ~ 39.33 | 3 | 65.93 ~ 72.93 | ❌ | **83.68 ms** | ❌❌ |

### 4.4 两个关键阈值 (给老板的"达标条件")

| 条件 | 阈值 | 推导 |
|---|---|---|
| **模式 A 达标** | **S5 ≤ 20.33 ms** | 60 − 24.67 (曝光块) − 9 (画框+TX+光机) − 6 (S4/S6/S7) |
| **模式 B 保持 60fps 达标** | **S5 ≤ 10.67 ms** | 16.67 (P60) − 6 (S4/S6/S7) |
| 光机 S10 的容忍度 (模式 A, S5=17.39) | **S10 ≤ 7.93 ms** | 60 − 24.67 − 23.39 − 1 (画框) − 3 (TX) |

> ★ **R1b 台阶效应仍然成立且是决定性的**: S5 从 10.67 涨到 10.68 ms, 端到端在模式 B 下就从 50.34 跳到 67.01 ms —— **"差 0.01ms" = "差 16.67ms"**。

---

## 5. 最终结论: RK3576 能否满足端到端 ≤60ms?

### 5.1 判定

> ## **PASS (有条件)** —— 但**必须放弃"60fps 显示"**

**依据**:
1. [公开实测·第三方] RK3576 上 yolov5s@640 INT8 的整链路 = **15.4~17.4 ms** ⇒ 纯 NPU S5 ≤ 17.4 ms, 低于模式 A 达标阈值 **20.33 ms**。
2. [推算] 代入口径 A (曝光→出光, 老板 10-25 19:16 锁死) ⇒ **模式 A 端到端 55.0 ~ 57.0 ms ≤ 60 ms** ✔, 显示帧率 **24.7 ~ 26.0 fps**。
3. [推算] **模式 B (异步 60fps) = 67.01 ms ❌** —— 因为 T_od=21~23ms 落在 age=2 档, 跨过 16.67ms 台阶。**这一条与老板 10-25 已经授权的兜底方案 (55.7ms @ 25.6fps) 完全一致** ⇒ **切到 RK3576 不会让延迟更糟**。

**条件 (三条都必须成立)**:
| # | 条件 | 怎么确认 |
|---|---|---|
| C1 | 走**模式 A** (显示等 OD), 显示帧率降到 ~25fps | 软件配置项 (`SW/DISPLAY_MODE.md` 的 `async_latest` ↔ `wait_od` 可切换, 已实现) |
| C2 | 板端实测 **S5 ≤ 20.33 ms** | ★ **投板后第一件事**; 本单无板, 这条是 [0数据] |
| C3 | 光机逐帧延迟 **S10 ≤ 7.93 ms** | ★ [0数据] (走鹃Ⅱ 未公开); 需高速摄影/示波器 |

### 5.2 若坚持 60fps 显示 ⇒ **FAIL**, 除非改模型/改分辨率

| 路线 | S5 | 端到端 (模式 B, 60fps) | 代价 |
|---|---|---|---|
| yolov5s @640 (现状) | 15.4~17.4 ms | **67.01 ms ❌** | 无 |
| **yolov5n @640** | 8.87 ms | **50.34 ms ✅** | 换模型 ⇒ **精度要重评** (yolov5n 比 yolov5s 少 ~4 个点 mAP50) |
| **yolov5s @320** (降分辨率) | ~4~5 ms (估) | **50.34 ms ✅** | ★ **改锁定变量 "OD 640×480"** ⇒ 需老板拍板; 小目标漏检上升 |

### 5.3 板端实测清单 (投板后第一件事, 按优先级)

| 优先级 | 测什么 | 判据 | 为什么 |
|---|---|---|---|
| **P0** | 纯 NPU 耗时 S5 (min/avg/max, ≥100 帧) | **≤ 20.33 ms** | 决定 60ms 能不能成立 (C2) |
| P0 | 端到端实测 (曝光→出光, 高速摄影 ≥240fps) | ≤ 60 ms | 老板硬指标的唯一验收口径 |
| P1 | SDK 总耗时 vs 纯 NPU (分开报) | — | SOUL.md 铁律; RKNN 的 2.14M 元素反量化开销 |
| P1 | 显示帧率 (模式 A 下) | ≥ 24 fps | 模式 A 的硬代价 |
| P1 | INT8 输出量化的实际精度 (板端跑 COCO 抽 200 张) | F1 ≥ 0.30 (量产门 G3) | 坑 3 的量化损失只有板端能定 |
| P2 | 内存占用 (RK3576 DDR 比 512MB 大, 不是瓶颈) | — | — |

---

## 6. 证据分级汇总

| 等级 | 本单条目 | 代表条目 |
|---|---|---|
| **[实测]** | 26 项 | RKNN 转换成功 / 产物 10.09 MiB (切版) + 10.45 MiB (完整版) / build 36.2s / 4 条 dtype 告警 / 量化器 outlier 告警 / 3 个坑的复现 / simulator 334ms (作为"仿真器不是 NPU 代理"的证据) / **INT8 F1=0.3139 vs FP32 F1=0.3182 (损失 0.0043)** / **不切后处理 F1=0** / 模型输入 = RGB/255 (maxIoU 0.000 → 0.956) / head 是 pre-sigmoid / raw head 解码公式与 `output` 逐元素吻合 (6e-05) / RKNN 会重排输出顺序 / op 普查 245 节点 12 算子 / 校准集 100 张 |
| **[公开实测·第三方]** | 5 项 | model_zoo RK3576 yolov5s 57.5 FPS / yolov5s_relu 65.0 FPS / yolov5n 112.7 FPS / RK3588 yolov5s_relu 66.1 FPS / PhotonVision RK3588 YOLOv5 15.034±1.734 ms |
| **[官方]** | 3 项 | rknn-toolkit2 2.3.2 支持 target_platform 含 rk3576 (`rknn/api/rknn.py:89`) / RKNN 板端运行时 = rknn-toolkit-lite2 / 官方文档: simulator 仅用于功能验证 |
| **[推算]** | 16 项 | 全部端到端数字 (模式 A / 模式 B / age 台阶表 / 两个阈值 / 光机容忍度 / 三档 NPU 候选的 e2e) |
| **[0数据]** | 5 项 | **板端 NPU 耗时** / **板端 INT8 精度** / 光机逐帧延迟 S10 / RK3576 实际频率与温度 (DVFS) / RK3576 实际功耗 |

---

## 7. 复现命令 (B6)

> ★ **本节列的每条命令都能在干净机器上独立跑通** (ISS-113, 2026-10-29 项目总工登记 → sw-lead 修)。
>
> **步间依赖 (已修)**: `convert` / `sim` / `acc` 三步做 **INT8 量化**,
> `rknn.build(dataset=...)` 需要 `calib` 步生成的 `/tmp/rknn_bench/dataset.txt`。
> 旧版这里是**裸 `assert`** ⇒ 干净机器上直接跑 `acc` 会崩成 `AssertionError`
> (RKNN 原始报错: `build: Dataset file /tmp/rknn_bench/dataset.txt not found!`)。
> ★ **现在: 缺 `dataset.txt` 时脚本自动先跑 `calib`** (日志打印
> `[dep] ⚠ ... 自动先跑 calib 步`), **不再抛 AssertionError**;
> 想看"缺依赖"的**明确报错** (而不是自动补跑), 加 `--no-auto-calib`:
> ```bash
> /home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py acc --no-auto-calib
> # ⇒ 打印「缺少量化校准集清单: /tmp/rknn_bench/dataset.txt … 二选一: 1) 先跑 calib 步 …」
> #    并以 rc=1 退出 (不是崩栈)
> ```

### 7.1 步间依赖表 (★ 2026-10-29 实测自愈)

| 步 | 依赖 | 干净机器直接跑的结果 |
|---|---|---|
| `probe` | 无 | ✅ 秒级 |
| `e2e` | 无 (纯算式) | ✅ 秒级 |
| `calib` | 校准集源目录 `~/Public/radxa_yolo/calib_yolov5_100` (100 张 jpg) | ✅ 写出 `/tmp/rknn_bench/dataset.txt` |
| `convert` | `dataset.txt` | ✅ **自动补跑 calib** |
| `sim` | `dataset.txt` | ✅ **自动补跑 calib** |
| `acc` | `dataset.txt` + COCO `val2017` + `instances_val2017.json` | ✅ **自动补跑 calib** |

> ★ **WORK=/tmp/rknn_bench 会被系统清理, 重跑需重新 calib**
> `/tmp` 是系统临时目录: 重启 / 清缓存 / tmpwatcher 都可能把它清掉。
> 被清掉后 `convert` / `sim` / `acc` 会**自动重新 calib** (多花约 20 s: 100 张 640×640 letterbox),
> **不影响任何结论数字** (校准集是固定的那 100 张, 量化参数不变)。
> ★ 就算只清掉一半 (`dataset.txt` 还在, 但它引用的 png 没了), 脚本也会识别出来并**重新 calib**
> (检测逻辑: `dataset.txt` 存在 **且** 它引用的每一张 png 都还在 ⇒ 才算可用)。
> ★ 若连**校准集源目录** `~/Public/radxa_yolo/calib_yolov5_100` 也没有了,
> 那 `convert` / `sim` / `acc` 只能等资料到位 —— 此时脚本打印**明确报错**
> («校准集源目录不存在: …» / «校准集源目录里没有 jpg: …») 并 **rc=1** 退出, 不是崩栈。
> ★ `probe` / `e2e` 两步**不依赖任何中间产物**, 任何时候都能跑。

### 7.2 命令清单

```bash
cd /home/yuewuya/.openclaw/workspace-sw/projects/smart_glasses

# 一条命令跑完全部 (探针 → 校准集 → 转换 → 仿真 → 精度 → 端到端)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py all

# 只要环境 / 模型 / 算子普查 (秒级, 无依赖)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py probe

# 只要端到端判定 (秒级, 无依赖)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py e2e

# 只要精度 (含 FP32 基线) —— ★ 干净机器可直接跑 (缺 dataset.txt 会自动先 calib)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py acc --images 300 --fp32-baseline

# 只要 RKNN INT8 产物 (切后处理版, 板端真正能用的那个) —— ★ 干净机器可直接跑 (自动 calib)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py convert

# 只要仿真一致性 + 仿真耗时 —— ★ 干净机器可直接跑 (自动 calib)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py sim

# §3.3.2 的 max_abs_diff 表是在**完整模型**上测的 ⇒ 必须加 --no-cut
# (默认的切后处理版只有 3 路输出, ONNX 参考有 4 路 ⇒ 形状对不上 ⇒ diff 列表为空;
#  这是**既有行为**, 与 ISS-113 的步间依赖修复无关)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py sim --no-cut

# 手动跑 calib 步 (单独跑; 之后 convert/sim/acc 就不用再等自动补跑)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py calib

# 机读输出 (★ stdout 纯净 ⇒ 可直接 json.load / jq; 进度条与诊断信息走 stderr)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py all --json

# 状态源合并 + 质量门
python3 state/merge.py          # 期望 rc=0
python3 state/gate_check.py      # 期望 Q1 18/18
```

### 7.3 退出码

| rc | 含义 |
|---|---|
| 0 | 本机可执行部分全过 |
| 1 | 有失败 (含**前置条件不满足**: 缺校准集 / 缺数据目录 / 缺 `dataset.txt` 且已关掉自动补跑) |
| 2 | 用法错 (缺环境 / 参数不合法) |

