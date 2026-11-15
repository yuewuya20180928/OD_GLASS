# SW/DEMO_BOARD_60MS_VERDICT_PLAN.md — RK3572 端到端 60ms 硬指标: 生死判定链

> 版本 v1.0 (2026-11-15, ISS-210, sw-lead) · 上游件: `SW/DEMO_OD_TIMING_SPEC.md` v1.2 (★12 段★) ·
> `SW/RK3572_TARGET_COMPAT_V2.md` (ISS-207 v2, 板端验证包) · `SW/ISP_CAPABILITY_RESEARCH.md` + `.json` (ISS-124, ISP 反解) ·
> `HW/e2e_budget_rk3572.py` (端到端账本) · `SW/RKNN_BENCH.md` §4~§5 (S5/模式A/模式B 口径)
>
> ★**本单只写【判据链】, 不替老板拍板**: 60ms 生死怎么裁 / 换不换芯片 / 降不降帧 ⇒ **只列选项 + 代价**。
> ★**本单零外发**: 不发邮件 / 不询价 / 不采购 / 不联系任何供应商 (老板 2026-11-12 02:02) ⇒ 板端结论一律 **[0数据]**。
> ★**自证命令见 §6.4**; **边界见 §6.5**。

---

## 0. 一句话 + 两条路 (为什么这份文件存在)

**一句话**: ★**板到手 ⇒ 30 分钟出一条 PASS/FAIL + 数值 + 差多少; 板永不到 ⇒ 结论也已经写死 (见 §6)★** —— ★**不再留任何『等板』式的无判据挂起** ★

| 路 | 触发 | 产出 | 章节 |
|---|---|---|---|
| **路 A: 板到手** | 拿到一块**可达**的 RK3572 (任意型号/载板) | **30 分钟**出一条 60ms 生死判定 (PASS/FAIL/INDET + 数值 + 差多少) | ① ~ ④ |
| **路 B: 板永不到** | 板一直不可达 | **降级结论写死**: RK3572 判"未验证"而不是"已验证通过"; 60ms 生死按 §6.4 的**选项清单**由老板裁 | ⑥ |

★**为什么必须是两条路**: ★**板不可达这件事不许再当阻塞项** ⇒ 外部依赖一律换成【自己查的结果 + 证据等级 + 降级方案】★。

---

## 1. ① 前置 (P1~P6) —— ★直接引 ISS-207 v2, 本单不重写★

> 出处: `SW/RK3572_TARGET_COMPAT_V2.md` §5.1 (降级 A 自持验证包) + `SW/tools/rk3572_target_smoke.sh` (★已由 main 独立验收签字★)
> ⇒ **本节只列"跑什么 / 失败怎么办", 判据的完整版在 ISS-207 v2, 本单不重写、不改一个数**。

| # | 前置项 | 板端命令 (★照抄★) | 过了 | 不过怎么办 |
|---|---|---|---|---|
| **P1** | 板子身份 | `cat /proc/device-tree/compatible \| tr '\0' ' '` | 必须含 `rk3572` | 不含 ⇒ **不是 RK3572 板** ⇒ N1 不构成跨平台证据 ⇒ 停 |
| **P2** | runtime 版本 | `strings /usr/lib/librknnrt.so \| grep -i 'librknnrt version'` | 记进证据 | 记进证据 (不判死) |
| **P3** | lite2 版本 | `python3 -c "import rknnlite, importlib.metadata as m; print(m.version('rknn-toolkit-lite2'))"` | 记进证据 | 记进证据 |
| **P4** | 产物 + sha256 | `ls -l SW/artifacts/models/*.rknn && sha256sum SW/artifacts/models/*.rknn` | 文件在 | ⇒ 走 `SW/tools/rk3572_model_rebuild.sh` 重转 |
| **P5** | COCO 数据在位 | `ls /work/object_detection/data/coco/raw/val2017 \| wc -l; ls -l /work/object_detection/data/coco/raw/annotations/instances_val2017.json` | val2017 + annotations 都在 | ⇒ N2 无从判 ⇒ 精度项 [0数据] |
| **P6** | ★**板端不许重转**★ | `sha256sum <artifact>.rknn \| cut -d' ' -f1` vs 同目录 `.sha256` sidecar | **逐字相等** | 不等 ⇒ 产物被换过 ⇒ 停 (先查是谁换的) |

★**拷贝产物 (含 sidecar, 一套拷齐)★**:

```bash
mkdir -p /work/models && cp -a SW/artifacts/models/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn \
                            SW/artifacts/models/*.sha256 /work/models/
sha256sum /work/models/*.rknn | cut -d' ' -f1
```

★**P1~P6 全过 = "可以开始测了"; 任一项不过 = 按上表处置, 不许跳过往下跑**。

---

## 2. ② 板端 11+1 段打点 (★含新增的第 12 段 = ISP★)

> 段表真源 = `SW/DEMO_OD_TIMING_SPEC.md` §2 (★v1.2 已补到 **12 段**★) ⇒ 本节只写"板端要打哪几个点 + 怎么喂进判据"。

| 段 | 打点名 | 谁打 | ★**判据用哪个数**★ |
|---|---|---|---|
| 1 曝光 | `exposure_us` | sensor 驱动 | 单列 (不许并进 `t_capture`) |
| 2 采集 | `t_capture` | capture 线程 | 归因用 |
| ★**12 ISP** ★ | ★**`t_isp_hw` + `t_isp_total`** ★ | ★**rkisp 驱动 / rkaiq** ★ | ★**`t_isp_total` (管线可见) = 60ms 生死线上的那个数** ★ |
| 3 预处理 | `t_pre` | capture 线程 | 归因用 |
| 4 NPU 提交 | `t_sdk_total` | capture 线程 | 归因用 |
| 4a 纯 NPU | `t_npu` | ★**SDK 内部计数器** ★ | ★**T2 翻案条款 (≤ 20.33 ms)** ★ |
| 5 解码 | `t_decode` | post 线程 | 归因用 |
| 6 画框 | `t_draw` | post 线程 | 归因用 |
| 7 合成 | `t_compose` | post 线程 | ★**输出侧上限 10.09 ms (ISS-137)** ★ |
| 8 上屏 | `t_display` | DRM/KMS | ★**TX 物理下限 7.776 ms @1080p** ★ |
| 9 光机 | `S10` | — | ★**[0数据]** (软件打不到) ★ |
| 10 汇总 | `t_e2e_A_soft` | post 线程 | 终点 |
| 11 计数 | `frames_total` / `frames_dropped` / `npu_err` / `box_count` | post 线程 | 事实量 |

### 2.1 ★ISP 段怎么打 (★本单新增的那一段·板端最容易卡住的地方★)

| 项 | 内容 |
|---|---|
| ★**三个时间戳** ★ | `ts_isp_in` (帧交给 ISP / VICAP dequeue) · `ts_isp_hw_start` (ISP 硬件开始执行) · `ts_isp_out` (ISP **frame-done**, NV12 已交付用户态) |
| ★**两个数** ★ | `t_isp_total = ts_isp_out − ts_isp_in` (★**管线可见 ⇒ 判据用它**★) · `t_isp_hw = ts_isp_out − ts_isp_hw_start` (★**纯硬件 ⇒ 只做归因**★) |
| ★**为什么不能用 wall clock 包一次函数调用** ★ | ★**ISP 是异步流水**: 用户态根本没有"调用前/调用后"两个点可打 ⇒ 只能用**驱动/帧统计**上报的时间戳 ★ |
| ★**时钟域** ★ | 三个时间戳必须**都在 `CLOCK_MONOTONIC` 域** ⇒ 板端第一件事: 核对 VICAP buf timestamp 与 rkaiq/frame-done 的时钟源 (混了 `CLOCK_REALTIME` ⇒ 相减出来是垃圾 ⇒ 负值/几十秒 ⇒ 一眼看出不对) |
| ★**取不到 `ts_isp_hw_start` 怎么办** ★ | 该列留空 ⇒ `t_isp_hw` 报 **[0数据]** ⇒ ★**不许拿 `t_isp_total` 顶替它** (两个数不许合并成一个数) ★ |

```bash
media-ctl -p                                        # ISP 节点输入=全幅 2688×1520 / 输出=640×480@60 ?
cat /sys/kernel/debug/rkisp/*                      # ISP 实际生效的输入/输出尺寸与 scaling 配置
cat /proc/interrupts | grep -i isp                 # 跑 60s 数帧 ⇒ 实测吞吐 (帧数×单帧像素/时长)
```

★**吞吐判据 (ISS-124 判据 ②)**: 实测 **≥ 60 fps @ 全幅 2688×1520 输入** ⇒ **245.1 MP/s 被官方实现确认**。
★★**12M Pixel 是【单帧分辨率上限】, 不是【每秒能力】 ⇒ 不许用它推 MP/s** ★★ (ISS-124 已钉死)。

### 2.2 ★板端 CSV (照抄 `SW/DEMO_OD_TIMING_SPEC.md` §3.4, 17 列, 一行不换行)★

```
frame_idx,ts_capture,ts_isp_in,ts_isp_hw_start,ts_isp_out,ts_pre,ts_npu,ts_sdk_total,ts_decode,ts_draw,ts_compose,ts_display,exposure_us,queue_wait_ms,box_count,npu_err,frame_dropped
```

★**采样纪律**: **n ≥ 300 帧** (或跑满 60s) ⇒ n < 300 ⇒ **不作结论** (工具会直接判 INDET) ★

### 2.3 ★把 ISP 段喂进判据 (一条命令)★

```bash
python3 SW/tools/timing_check.py --isp-csv /work/logs/board_isp.csv --only F9_isp_budget
```

⇒ 出 **verdict (PASS/FAIL/INDET) + 余量/超出多少 ms + 代回 60ms 账本后的 e2e 模式A/模式B**。

---

## 3. ③ N1~N5 (rknn 加载 / 精度 / 纯 NPU / 温度与供电)

> 判据真源 = ISS-207 v2 §5.3 + `SW/RK3572_TARGET_BOARD_VERIFY.md` §4 ⇒ **本单不重写阈值, 只写"跑什么 + 结果怎么进 60ms 判定"**。

```bash
bash SW/tools/rk3572_target_smoke.sh          # ★板端一条命令⇒ N1~N5 逐条 PASS/FAIL/INDET + 数值 + 失败原因★
```

| # | 判据 | 通过线 | 不过 ⇒ 说明什么 | ⇒ 怎么进 60ms 判定 |
|---|---|---|---|---|
| **N1** | 能加载 | `load_rknn` ret == **0** (且 `init_runtime` == 0) | ★**跨平台兼容命题被否** (rk3576-target 产物 RK3572 runtime 不认) | ⇒ 走 §5 出路 3 (换 RK3576) |
| **N2** | 精度不塌 | 板端 F1 ≥ **0.2427** (PC 基线 0.2927 − 0.05) | 量化在不同 NPU 实现上有偏 ⇒ 反量化路径不对 | ⇒ 精度项 [0数据]/FAIL ⇒ **不影响 60ms 判定, 影响能不能上** |
| **N3** | NPU 耗时对得上 | `t_npu` ≤ **13.30 ms** [推算] | `t_npu` **> 20.33 ms ⇒ 命中老板 T2 翻案条款 ⇒ 60ms 硬指标不保** (ISS-129) | ★**直接进 §4 的 age 台阶 (差 0.01 ms 就可能掉一档 16.67 ms)** ★ |
| **N4** | 两个数都报 | `t_npu` **和** `t_sdk_total` 都有且**分开** | 只报一个 ⇒ 违反 SOUL.md 铁律 ⇒ 数不可用 | ⇒ 工具判 INDET, 不许合并 |
| **N5** | 散热/供电已记录 | `thermal_zone0` 温度 + `cpufreq` + 供电方式 | 没记 ⇒ N3 的数**没有可比性** | ★见 §3.1 ★ |

### 3.1 ★N5 (温度与降频) 怎么进 60ms 判定 (★ISS-210 补充项·老板点名的那一条★)

| 事实 | 对 60ms 的作用 | 判据里的位置 |
|---|---|---|
| SoC 降频 ⇒ **纯 NPU 变慢** | ★**age 是台阶函数**: `t_npu` 跨过 16.67 ms 边界 ⇒ `age` 从 2 跳 3 ⇒ **端到端直接多一整个帧周期 (+16.67 ms)** ⇒ ★"差 2 ms 可能等于差 17 ms" ★ | ★**N3 的数必须配 N5 的温度/频率一起报** ⇒ 不配 ⇒ N3 只作参考 |
| 满载温度 ⇒ 皮肤 43°C 红线 | ★**结论不翻案**: ISS-124 重估后满载 **10/10 档位仍超 43°C** (ISP 重估只让它更差 +3.0~+9.6°C) ⇒ ★**降帧/降载是温度杠杆, 不是延迟杠杆** (见 §5) | 属 §5 出路 1 的**真正收益**所在, 不是 60ms 的 |
| ISP 动态功耗 | 全幅 245.1 MP/s ⇒ **237.2 mW** [推算] (带 180.2~312.2) | ⇒ 若板端实测 SoC 轨差值 > **312 mW** ⇒ 皮肤重算要再上浮 (ISS-124 判据 ③) |

★**板端记录命令 (N5)★**:

```bash
cat /sys/class/thermal/thermal_zone*/temp ; cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq ; cat /sys/class/devices/platform/rknpu/load
```

---

## 4. ④ 60ms 硬指标判定 (模式A / 模式B, ★用【框龄 age】模型★)

### 4.1 ★铁律: 不许把环节相加 (★我们自己的铁律, 本单不违反★)

★**端到端不是"把各段耗时加起来"** ★ ⇒ 因为**帧是流水的**: `t5` 之后 post 线程可以与下一帧的 `t2~t4` 重叠 ⇒
★**端到端 = 曝光起点 → 显示帧就绪, 用【框龄 age】模型算, 不是各段求和** ★
⇒ 账本真源 = `HW/e2e_budget_rk3572.py` (T_FIXED 五段拆分 + age 台阶 + 模式A/模式B)。

### 4.2 算式 (★与 `HW/e2e_budget_rk3572.py` 同源, 逐位可复现★)

```
T_FIXED = 34.00  (曝光块 E+R+S3[ISP含缩放]=24.67 + 画框 1.00 + 显示输出侧 3.00 + 光机 5.00 + 残差 0.33)
T_od    = t_npu + POST_MS(5.6)
age     = ceil(T_od / 16.67)                       ← ★框龄台阶★
模式A (显示等 OD):   e2e = T_FIXED + T_od
模式B (异步 60fps):  e2e = T_FIXED + age × 16.67
★把 ISP 段当变量 X 代进去 (ISS-124 反解):
  模式A: X ≤ 60 − (T_FIXED − S3) − T_od = 60 − 26.00 − T_od
  模式B: X ≤ 60 − 26.00 − age × 16.67
```

### 4.3 ★ISP 段的判据线 (★四个数与 ISS-124 逐字一致★)

| 项 | 数 | 出处 |
|---|---|---|
| ★**模式A 生死线** ★ | **`t_isp_total` avg ≤ 15.10 ms** | `SW/ISP_CAPABILITY_RESEARCH.md` §② · `.json` (`modeA: 15.095`) |
| 模式B 上限 (前提 age=1) | `t_isp_total` p95 ≤ **17.33 ms** | 同上 (`.json` `modeB: 17.33`) |
| ★**现占位 8.00 ms 的余量** ★ | **+7.09 ms (模式A) / +9.33 ms (模式B)** | 同上 (`.json` `7.095` / `9.33`) |
| ★**精确反解值** ★ | 15.095 ms (同一次反解未舍入) | 与发布值差 **0.005 ms** ⇒ 远小于板端 0.01 ms 级分辨率 ⇒ **不改变任何结论** |

★**判定线取 ISS-124 的【发布值】 15.10 / 17.33 (逐字引用, 不许调松)★** ⇒ ★**60 ms 硬指标也不许调松** ★

### 4.4 ★判定怎么出 (机械可判, 一条命令)★

```bash
# ① ISP 段判据 (PASS/FAIL + 余量 + 代回账本后的 e2e)
python3 SW/tools/timing_check.py --isp-csv /work/logs/board_isp.csv --only F9_isp_budget
# ② 合成/上屏侧判据 (ISS-137: 输出侧总额 ≤ 10.09 ms ⇒ 合成段 ≤ 2.32 ms)
python3 HW/e2e_budget_rk3572.py --t-compose-ms <第7段实测值>
# ③ N1~N5 (含 N3 纯 NPU 与 N5 散热)
bash SW/tools/rk3572_target_smoke.sh
```

| 工具输出 | 含义 | 下一步 |
|---|---|---|
| `verdict = PASS` | ISP 段两个数都报、样本 n≥300、avg ≤ 15.10 ms | ⇒ ★**ISP 不是瓶颈** ⇒ 60ms 的成败只剩 N3 的纯 NPU 与显示输出侧 ★ |
| `verdict = FAIL` + `margin_ms < 0` | avg > 15.10 ms ⇒ **模式A 破线** | ⇒ ★**走 §5 出路** (ISP 侧只能降单帧处理量) ★ |
| `verdict = INDET` | 缺一个数 / n < 300 / 未实测 | ⇒ **不许下结论**, 补测 (板端结论一律 [0数据]) |

### 4.5 ★60ms 生死的完整判定链 (★四条全过 = 60ms 成立; 任一条不过 = 不成立★)

| # | 条件 | 通过线 | 谁判 |
|---|---|---|---|
| **1** | ★**ISP 段** (段 12) | `t_isp_total` avg ≤ **15.10 ms** (p95 ≤ 17.33 ms) | `timing_check.py` F9 |
| **2** | ★**纯 NPU** (段 4a) | `t_npu` ≤ **20.33 ms** (★**T2 翻案条款, 老板锁死**★); > 13.30 ms ⇒ 走 ISS-207 的 N3 | `rk3572_target_smoke.sh` N3 |
| **3** | ★**显示输出侧** (段 7+段 8) | 合计 ≤ **10.09 ms** (⇒ 合成段 ≤ **2.32 ms**, 已扣 TX 物理下限 7.776 ms @1080p) | `HW/e2e_budget_rk3572.py --t-compose-ms` |
| **4** | ★**框龄台阶** | `age = ceil(T_od/16.67)`; 模式B 成立的前提是 **age = 1** (T_od ≤ 16.67) | 账本 (`e2e_budget_rk3572.py`) |

★**模式A vs 模式B 怎么选 (★口径问题, 老板锁死项, 本单不裁★)★**: 模式A = 显示等 OD (显示帧率掉到 ~25fps, `SW/DISPLAY_MODE.md` 的 `wait_od`);
模式B = 异步 60fps (`async_latest`) ⇒ ★**现行 yolov5n@640 的 age = 2 ⇒ 模式B 本来就不成立 (67.34 ms), 与 ISP 无关** ★

---

## 5. ⑤ 三条出路 + 各自代价 (★只列, 不代决★)

| 出路 | 做什么 | 对 60ms 的作用 | 代价 | 出处 |
|---|---|---|---|---|
| **① 降 OD 负载** | 640×480@60 → **@30** | ★**降帧率不改善单帧延迟** ★ ⇒ 60ms 是**单帧**指标 ⇒ ★**这条救不了 62.7~65.7 ms** ★; ★**真正的作用是降功耗/降温** (NPU 与 ISP 占空比减半 ⇒ 皮肤 43°C 红线才有希望) ★ | ★**显示帧率锁死项要改写** (老板 10-29 已锁 60fps ⇒ **须老板拍板**) + **框龄模型要重算** (60→30fps ⇒ FRAME_MS 16.67→**33.34** ⇒ age 台阶整个换档) | `SW/RK3572_TARGET_BOARD_VERIFY.md` §4.1 |
| **② 换更小模型** | yolov5s@640 → **yolov5n@640** | ★**模式A [推算] 62.7~65.7 → 52.91 ms ✅** (RK3572 纯 NPU [推算] 13.305 ms, T_od 18.905, age 2) ⇒ ★**这是三条里唯一直接命中 60ms 的** ★ | ★**精度**: F1 0.2927 vs 0.3017 (召回低 0.0291) ⇒ 眼镜场景实拍未验 + ★**F1 0.2927 低于 0.30 门槛 (ISS-157 未决项 SW-Q5, 待老板拍板)** ★ + ★**ISP 段完全不受影响** (ISP 处理的是**全幅**输入, 与模型无关 ⇒ ★**ISP 若超标, 换模型救不了**) ★ | `SW/RKNN_BENCH.md` §4.3/§5.2 · ISS-157 |
| **③ 回 RK3576** | 主控换回 RK3576 | ★**模式A 55~57 ms ✅** (纯 NPU 15.4~17.4 ms, **公开实测·第三方** 口径) ⇒ ★**唯一有第三方实测背书的一条** ★ | ★**板面积装不下** (RK3576 74 分 ⇒ 须 PCB 厂确认 6 层板能否塞下) + **整链换 SoC ⇒ 重新出板** ⇒ ★**本单不许碰 PCB 布线/布局, 只报代价** ★ | `SW/RK3572_TARGET_BOARD_VERIFY.md` §4.1 |

### 5.1 ★三条出路的"有效性体检" (★避免拍板时踩坑★)

| 出路 | 能不能解决"纯 NPU 超标" | 能不能解决"ISP 段超标" | 能不能解决"显示输出侧超标" | 能不能解决"皮肤 43°C" |
|---|---|---|---|---|
| ① 降帧到 @30 | ✗ (单帧不变) | ✗ (单帧 ISP 处理量不变) | ✗ | ★**✅ 这是它真正的价值** ★ |
| ② 换 yolov5n@640 | ★**✅** | ✗ | ✗ | ◐ (占空比略降) |
| ③ 回 RK3576 | ★**✅** | ◐ (RK3576 ISP 16M Pixel 上限, 未反解过) | ◐ (同 SoC 同显示侧 ⇒ 不变) | ◐ (功耗更高 ⇒ 可能更差) |

★**⇒ 一句话**: ★**三条出路各自只解一类问题; 唯一能同时解"延迟 + 温度"的是 ②+③ 组合, 但代价最大** ★

### 5.2 ★640×480@30 降载模式下的新预算 (★ISS-210 补充项: 降帧后账本怎么换★)

| 项 | @60fps (现行锁定) | @30fps (降载) | 说明 |
|---|---|---|---|
| 帧周期 `FRAME_MS` | 16.67 | **33.34** | ★**age 台阶整个换档** ★ |
| `age` (T_od = 18.905) | 2 | **1** | ⇒ 模式B 的 `age×16.67` 换成 `age×33.34` |
| 模式A e2e | 52.91 ms (yolov5n@640) | **52.91 ms (不变)** | ★**模式A = T_FIXED + T_od, 与帧率无关** ⇒ ★**降帧不改善单帧延迟 (再确认一次)** ★ |
| 模式B e2e | 67.34 ms ❌ | 34.00 + 1×33.34 = **67.34 ms ❌** | 巧合相等, 但机理不同 |
| ISP 吞吐需求 | 245.1 MP/s (全幅 2688×1520@60) | **122.6 MP/s** | ⇒ ISP **功耗**减半 ([推算] 237.2 → ~118.6 mW) ⇒ 皮肤温度才有希望 |
| ★**结论** ★ | — | — | ★**降载 = 功耗/温度杠杆, 不是延迟杠杆** ⇒ ★**拍板时别把它当 60ms 的出路** ★ |

---

## 6. ⑥ 板永不到时的降级结论 (★写死: 不许留任何『等板』式挂起★)

### 6.1 ★三条链: 哪一段 [实测] / 哪一段 [推算] / 哪一段 [0数据]★

| 环节 | RK3576 (6 TOPS) | RK3572 (4 TOPS) | 证据等级 |
|---|---|---|---|
| 纯 NPU (S5, yolov5s@640 整链路上界) | **15.4 ~ 17.4 ms** | **23.1 ~ 26.1 ms** (× 6/4) | RK3576 = **[公开实测·第三方]** · RK3572 = **[推算]** (★**不保证等比**: 4 TOPS 标称 sparse INT8★) |
| T_od (= S5 + 5.6) | 21.0 ~ 23.0 ms | **28.7 ~ 31.7 ms** | [推算] |
| `age` (ceil(T_od/16.67)) | 2 | **2** | [推算] |
| ★**模式A e2e** ★ | ★**54.98 ~ 56.99 ms (≈ 55~57) ✅** ★ | ★**62.67 ~ 65.69 ms (≈ 62.7~65.7) ❌** ★ | RK3576 = [公开实测·第三方] 推算 · RK3572 = **[推算]** |
| 模式B e2e | 67.01 ms ❌ | 67.34 ms ❌ | [推算] ⇒ ★**模式B 与 ISP 无关, 本来就不成立** ★ |
| ★**板端一切** (ISP 段 / 纯 NPU 实测 / F1 实测 / 温度) | — | ★**[0数据]** ★ | ★**板不在本机 ⇒ 0 条 [实测]** ★ |
| ★**ISP 段上限** (判据线, 板永不到也照样有效) | — | **15.10 ms (模式A) / 17.33 ms (模式B)**; 现占位 8.00 ms ⇒ 余量 **+7.09 / +9.33 ms** | [推算] (ISS-124 反解) |

★**⇒ 降级结论 (板永不到时的**默认**结论, 老板可推翻)** ★:
1. ★**RK3572 的 60ms 硬指标在 yolov5s@640 下 [推算] 不成立** (模式A 62.7~65.7 ms ❌) ⇒ ★**不得对外宣称"RK3572 达标"** ★
2. ★**RK3572 换 yolov5n@640 ⇒ 模式A [推算] 52.91 ms ✅** ⇒ ★**这是板永不到时唯一有希望成立的一条** ⇒ ★**但 F1 0.2927 < 0.30 门槛 (ISS-157) 仍未决 ⇒ 须老板拍板** ★
3. ★**"RK3572 达标"这个结论永远不能在没有板端 [实测] 的情况下被写下** ⇒ 板永不到 ⇒ **状态 = 未验证**, 不是"已验证通过" ★
4. ★**ISP 段不构成阻塞**: 判据线 (15.10/17.33 ms) 已固化进 `SW/tools/timing_check.py`, 板一到手 **一条命令** 出 PASS/FAIL ★

### 6.2 ★老板级选项清单 (★只列, 不代决★ —— 三选一/多选由老板拍板★)

| # | 选项 | 60ms [推算] | 代价 | 谁拍板 |
|---|---|---|---|---|
| **O1** | RK3572 + yolov5n@640 (★产物 ISS-207 已备好) | 模式A **52.91 ms ✅** | F1 0.2927 (< 0.30, ISS-157) · 模式B ❌ | 老板 (精度门) |
| **O2** | RK3572 + yolov5s@640 (现状锁定 M1) | 模式A **62.7~65.7 ms ❌** | 破 60ms 硬指标 | 老板 (破线与否) |
| **O3** | RK3572 + 降帧 30fps | **不改善单帧延迟** | 只解功耗/温度 · 改 60fps 锁死项 · age 台阶换档 | 老板 (锁死项) |
| **O4** | 回 RK3576 | 模式A **55~57 ms ✅** (第三方实测口径) | 板面积装不下 · 重新出板 · 功耗更高 | 老板 + PCB 厂 |
| **O5** | 板永不到 ⇒ 按 §6.1 降级结论裁 (判"未验证") | — | 无 | 老板 (确认) |
| **O6** | 改 60ms 的口径 (A-soft vs A-hard / 是否含 S10) | — | 改口径 = 改验收定义 | 老板 (口径) |

★**sw-lead 的立场: 只提供上表的数字与代价, 不选** ★

### 6.3 ★★"rk3576-target 产物在 RK3572 上的兼容风险到底压在哪一环" (★ISS-210 补充项★)

| 环节 | 风险 | 判据 | 压在哪 |
|---|---|---|---|
| 编译期 | ★**官方根本没有 `rk3572` 这个 target** (2.3.2 与 2.5.0 均无) ⇒ 只能 `target_platform='rk3576'` 转 | 已 [官网]+[实测] 钉死 (ISS-207) | **已消除** (PC 侧) |
| ★**加载期** ★ | ★**RK3572 BSP runtime 认不认 rk3576-target 产物** ⇒ 官方无此口径 ⇒ **只能板端判** | ★**N1** (`load_rknn` ret == 0) | ★**★风险主压在这一环★** ★ |
| 初始化期 | 算子/DMA/内存布局在 RK3572 上不兼容 (`rknn_init_runtime` 失败) | N1 的第二返回值 | 同一环 |
| 数值期 | 反量化路径不同 ⇒ 精度偏 ⇒ F1 掉 | **N2** (F1 ≥ 0.2427) | 精度环 (不影响 60ms) |
| 性能期 | 纯 NPU 性能偏差 (4 TOPS 标称 sparse vs 实际) | **N3** (`t_npu` ≤ 13.30 / 20.33) | ★**T2 翻案条款这一环** ★ |

⇒ ★**一句话**: ★**兼容风险压【加载期】(N1), 60ms 生死压【性能期】(N3) + 【ISP 段】(§4 条件 1) ⇒ 这是两个不同的环, 不要混着判** ★

### 6.4 自证复现命令 (交卷自证, 输出原样贴进交卷件)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/timing_check.py                                  # rc=0 · SELFTEST 68/68 (含 13 条 ISP 判据用例)
python3 SW/tools/demo_timing_check.py                              # rc=0 · 23/23 (规格自检: 12 段 + ISP 打点名 + 判据线 + 17 列 CSV)
python3 SW/tools/demo_timing_check.py --selftest                   # rc=0 · 4/4 (检查器自身的反向用例)
python3 SW/tools/timing_check.py --only F9_isp_budget              # 无实测 ⇒ INDET + [0数据] (板端结论一律 [0数据])
python3 SW/tools/timing_check.py --isp-csv <board.csv> --only F9_isp_budget   # 喂板端 ISP 段 ⇒ PASS/FAIL + 差多少
bash SW/tools/rk3572_target_smoke.sh --dry-run                     # rc=0 (ISS-207 交的东西没被跑坏)
python3 SW/tools/isp_budget_solve.py                               # rc=0 (ISS-124 反解复现: 15.10 / 17.33 / 8.00 / +7.09 / +9.33)
python3 HW/e2e_budget_rk3572.py --selftest                         # rc=0 (账本自检)
python3 state/merge.py && python3 state/gate_check.py              # rc=0 · 【Q1】18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv           # 611b869e… / c78f9912… (逐字节未变)
```

### 6.5 边界声明 (本单做了什么 / 没做什么)

| 项 | 状态 |
|---|---|
| 本单**改**的件 | `SW/DEMO_OD_TIMING_SPEC.md` (§2 加第 12 段 ISP + §3.1 加 1 行字段 + §2.4 口径裁决 + §3.4 CSV 加 3 列) · `SW/tools/timing_check.py` (加 `F9_isp_budget` 判据 + 13 条自测) · ★**本文件** ★ · `HANDOFF/2026-11-15_sw-lead_ISS210_60ms判据链.md` · `state/fragments/sw.yaml` (只加 artifact/answer/claim) |
| ★**第 6 个件 (超出 ④ 清单, 但不改就破)★** | ★**`SW/tools/demo_timing_check.py`** (★规格自检器: CSV 表头基线 14 列 → **17 列** + 新增 3 条 ISP/12 段断言 ⇒ 23/23 rc=0★) —— ★**它是 §2 段表与 §3.4 CSV 表头的机械核对器 ⇒ 规格加了第 12 段而不同步它 ⇒ 它立刻变红 (19/20 rc=1) ⇒ 必须同步, 否则就是"把别人的件跑坏"★ |
| 本单**没碰**的件 | ★`SW/ISP_CAPABILITY_RESEARCH.md` / `.json` / `SW/tools/isp_budget_solve.py` / `SW/RK3572_TARGET_COMPAT_V2.md` (★ISS-124 / ISS-207 已验证件, 只引用★) · 板 / 网表 / 脚表 / 原理图 / 任何 `state/gen_*.py` · ★**PCB 布线/布局 (老板 11-11 10:07 口径)** ★ · `PROJECT_TRACKER.md` §0 锁死表 · 别的 agent 的分片 |
| 外部依赖 | ★**零外发** (不询价/不采购/不下单/不联系供应商) ⇒ 板端结论一律 **[0数据]** ⇒ ★**不许编板端数据** ★ |
| 决策权限 | ★**不替老板拍板** (60ms 生死怎么裁 / 换不换芯片 / 降不降帧) ⇒ §5 出路 + §6.2 选项清单**只列** ★ |
| 板端 [实测] 条数 | ★**0 条** (板不在本机) ★ ⇒ 本文件里凡是板端结论, 一律标 [0数据] |
