# [sw-lead→PM] RKNN 转换链实测 + RK3576 端到端 ≤60ms 判定

- **发起方**: sw-lead (软件总工)
- **日期**: 2026-10-29
- **结论**: **RK3576 端到端 ≤60ms (口径 A) = PASS (有条件)** —— 但**只能走"模式 A (显示等 OD, 显示帧率 ~25fps)"**; **若坚持 60fps 显示则 FAIL (67.0ms, age 台阶)**。RKNN 转换链本身**通得过** (INT8 产物 10.45 MiB, 装得进 15 MiB 板端槽位), 但踩到 **3 个坑**, 其中 1 个是致命的 (不切后处理 ⇒ INT8 一个检测都出不来)。
- **依据**: `projects/smart_glasses/SW/RKNN_BENCH.md` (完整报告) + `projects/smart_glasses/SW/tools/rknn_bench.py` (一条命令可复现) + 第三方公开实测 (airockchip/rknn_model_zoo 性能表 + PhotonVision RKNN Benchmarks)

---

## B1 结论摘要

1. **RKNN 转换链通得过 [实测]**: rknn-toolkit2 2.3.2 + `target_platform='rk3576'`, 我们的 `yolov5s-sim.onnx` (sha16 `20368be665f6f59a`, 与台账一致) **一次转成, 零报错**。INT8 (`w8a8/normal/channel`) 产物 **10,958,444 B = 10.45 MiB** ⇒ **装得进**板端 15 MiB model 槽位 (余量 4.5 MiB)。build(100 张校准) 41.5 s。**⇒ RK3576 的"资料充足"判据在转换链这一维度过关, 这一点比 ARS45 强得多。**
2. **端到端 ≤60ms = PASS (有条件) [推算]**: 代入第三方公开实测的 RK3576 yolov5s@640 INT8 整链路 **17.39 ms** (保守, 同款 SiLU 结构) / **15.38 ms** (relu 变体) ⇒ 纯 NPU S5 ≤ 17.4 ms < 模式 A 达标阈值 **20.33 ms** ⇒ **口径 A 端到端 54.98 ~ 56.99 ms ✅**, 显示帧率 24.7~26.0 fps。**★ 与老板 10-25 已授权的兜底方案 (55.7 ms @ 25.6 fps) 完全一致 ⇒ 切 RK3576 不会让延迟更糟。**
3. **★ 但 60fps 显示在 RK3576 + 640×640 下达不成 [推算]**: T_od = 21~23 ms 落在 **age=2** 档 ⇒ 模式 B (异步 60fps) 端到端 **67.01 ms ❌** (超 7.0 ms)。这是 R1b 台阶效应的直接后果 —— **"差 0.01 ms" = "差 16.67 ms"**。要保 60fps 必须把 S5 压到 **≤10.67 ms** (换 yolov5n: 8.87 ms ✅ 或降到 ~320 分辨率)。
4. **★★ RKNN 这条路最大的坑: INT8 量化会把"输出张量"废掉 [实测]**: 未切后处理的模型输出 `output` (1,25200,85) 把**像素尺度坐标** (−6.8…706.9) 与 **0~1 概率**混在**同一个 int8 张量** ⇒ 量化步长 = 706.9/127 ≈ **5.57** ⇒ 概率被量化成 0/±5.57 ⇒ **INT8 模型 0 个检测 (F1=0)**, 而同样输入下 FP32 ONNX 完全正常。**解法: 用 `cut_postprocessor.py` 把后处理切掉, 只留 3 路 raw head, CPU 侧解码** —— 这正是 10-28 那套工具的用武之地 (本模型实测转换 0 报错)。
5. **★ 板端实测: 本单一次都没做 [0数据]**: 本机无 RK3576 板 (`adb devices` 空 / 无 RK 设备树)。**所有端到端数字都是 [推算], 不是 [实测]**。投板后第一件事就是打 **S5 (纯 NPU 耗时)**, 判据 **≤ 20.33 ms**。

---

## B2 验收标准自评

| # | 验收标准 (任务书) | 自评 | 依据 |
|---|---|---|---|
| 1 | 装 rknn-toolkit2 (pip / 官方 git) | ✅ 通过 | 报告 §2.2 —— 本机 conda env `rknn` 已装 **rknn-toolkit2 2.3.2** (python 3.10.20 / onnx 1.14.1 / numpy 1.26.4), `target_platform` 支持列表含 **rk3576** (`rknn/api/rknn.py:89`) |
| 2 | 转我们的 YOLOv5 INT8 → RKNN | ✅ 通过 | §3.2.1 —— 一次转成, 零报错; 产物 10.45 MiB; build 41.5 s |
| 3 | 遇到 NPU 不支持的算子用 `cut_postprocessor.py` 处理 | ✅ 通过 (情况反转: 本模型**不需要**切, 但**必须切**才能保住精度) | §3.2.2 + §3.2.4 坑 3 —— 本模型 245 节点 12 类算子全是 NPU 友好的 (无 NMS/TopK/Range) ⇒ 转换零报错; **但 INT8 输出张量量程混装 ⇒ 必须切后处理 + CPU 解码, 否则 F1=0** |
| 4 | 转换成功与否 | ✅ 通过 (成功) | §3.2.1 |
| 5 | 单帧推理耗时 | ⚠️ **未验 (板端)** / 🟡 仿真值已出 | §3.3 —— 板端 [0数据] (无板); PC 仿真器 383.26 ms/帧 (min 380.25 / max 387.45 / n=20) = **[推算·仿真]**, ★**已实证它不是 NPU 吞吐代理** (与公开第三方板端值差 ~20~30×) ⇒ **报告里明确标注"板端实测未做"** |
| 6 | COCO val2017 上的 F1 (与 10-28 同口径) | ✅ 通过 | §3.4 —— 与 `SW/tools/eval_od_accuracy.py` 严格同口径 (逐类 IoU 0.5 贪心匹配 / score≥0.3 / 同一批图 / 同一套匹配器) |
| 7 | 不许把仿真值当实测值报 | ✅ 通过 | §0 / §3.3.1 / §5 —— 仿真值单独命名 `sim_latency_ms`, 端到端计算里**默认不采用**, 只有显式 `--use-sim-as-npu` 才进 (且强制标 [推算·仿真]) |
| 8 | 端到端预算重算 (口径 A, 框龄台阶保留) | ✅ 通过 | §4 —— 口径 A (曝光→出光) 未改; `age = ceil(T_od/16.67)` 台阶函数保留, 并给出完整台阶表 |
| 9 | 端到端结论明确 (pass/fail/unknown 三选一 + 依据) | ✅ 通过 | §5.1 —— **PASS (有条件)**, 三条条件 + 依据 + "若坚持 60fps 则 FAIL" 的对照 |
| 10 | 转换若失败要如实写失败原因 | ✅ 通过 (转换成功, 但**踩坑如实写全**) | §3.2.4 —— 3 个坑 (onnx.mapping / simulator 不吃 load_rknn / INT8 输出量程混装) 全部给了现象+解法+复现 |
| 11 | 一条命令复算出报告里的数字 | ✅ 通过 | §7 —— `rknn_bench.py all` 一条命令跑完 探针→校准集→转换→仿真→精度→端到端 |
| 12 | 每个数字标 [实测]/[推算·仿真]/[0数据] | ✅ 通过 | §6 证据分级汇总 (实测 22 项 / 公开实测·第三方 5 项 / 官方 3 项 / 推算 14 项 / 0数据 4 项) |
| 13 | 写分片用 `frag_write.py` 原子写 | ✅ 通过 | 见本单 §"写分片" 与 B6 |
| 14 | 不碰 HW/ MECH/ PROJECT_TRACKER/ DECISIONS/ issue_log / 别人的分片 | ✅ 通过 | 本单只写 `SW/RKNN_BENCH.md` + `SW/tools/rknn_bench.py` + `state/fragments/sw.yaml` + 本交接单 |
| 15 | 未联系任何供应商/原厂 | ✅ 通过 | 只查了公开资料 (model_zoo README / PhotonVision 文档), 无任何外发 |
| 16 | 板端实测 NPU 耗时 (任务书隐含) | ❌ **不通过 (无板)** | §2.1 —— 本机无 RK3576 板 ⇒ 该项 [0数据]; 已转为"投板后第一件事"的 P0 清单 (§5.3) |

---

## B3 证据分级

| 等级 | 条目 | 关键数字 |
|---|---|---|
| **[实测]** | RKNN INT8 转换 | 成功 / rc=0 / 10,958,444 B (10.45 MiB) / build 41.46 s / 4 条 dtype 告警 |
| **[实测]** | 3 个坑 | ① `onnx.mapping` AttributeError ② simulator 不吃 `load_rknn` ③ INT8 输出量程混装 ⇒ F1=0 |
| **[实测]** | 模型台账核对 | sha16 `20368be665f6f59a` 与 `SW/MODEL_ASSETS.md` 一致; 245 节点 / 12 类算子 |
| **[实测]** | 算子普查 | Mul 69 / Conv 60 / Sigmoid 60 / Concat 17 / Add 10 / Slice 9 / Reshape 6 / MaxPool 3 / Transpose 3 / Sub 3 / Pow 3 / Resize 2; NMS/TopK/Range = **0** |
| **[实测]** | ★ 输入域校准 | 0-255 喂 ⇒ COCO 图139 top-100 **maxIoU = 0.000**; RGB/255 喂 ⇒ **maxIoU = 0.956, 85/100 IoU≥0.5** ⇒ 模型真实输入域 = **RGB /255** |
| **[实测]** | ★ head 是 pre-sigmoid | head obj 值域 −21.3…+10.9, cls −37.2…+10.3, bbox −9.8…+11.3; 只有 `output` 张量是解码后的 |
| **[实测]** | ★ raw head 解码公式 | `s=sigmoid(raw[0:4])`; `cx=(s0*2-0.5+gx)*stride`; `w=(s2*2)²*anchor_w`; `obj=sigmoid(raw4)`; `cls=sigmoid(raw5:)` ⇒ 与 ONNX `output` 逐元素吻合 (cx/cy max_abs_diff **6.0e-05**, w/h = **0**) |
| **[实测]** | RKNN 工具链重排输出顺序 | 切版模型 `outs[0]` 是 40×40 的 498 而不是 80×80 的 350 ⇒ **必须按 spatial 尺寸认头** |
| **[实测]** | 精度 | INT8 (RKNN simulator) vs FP32 (onnxruntime) 同口径, 见 §3.4 表 |
| **[实测]** | 仿真器耗时 | min 380.25 / avg 383.26 / max 387.45 / p50 383.19 ms (n=20) ⇒ **实证它不是 NPU 吞吐代理** |
| **[公开实测·第三方]** | model_zoo 性能表 (RK3576@single_core) | yolov5s **57.5 FPS = 17.39 ms** / yolov5s_relu **65.0 FPS = 15.38 ms** / yolov5n **112.7 FPS = 8.87 ms**; RK3588 yolov5s_relu 66.1 FPS = 15.13 ms |
| **[公开实测·第三方]** | PhotonVision (Orange Pi 5 / RK3588) | YOLOv5 Total Time = **15034 ± 1734 µs** (= 66.5 FPS) ⇒ 与上表 RK3588 值吻合 **0.6%** ✔ |
| **[官方]** | rknn-toolkit2 2.3.2 | 支持 `target_platform='rk3576'`; 板端 runtime = rknn-toolkit-lite2; 官方文档: simulator 仅用于功能验证 |
| **[推算]** | 端到端全部数字 | 模式 A 54.98~56.99 ms ✅ / 模式 B 67.01 ms ❌ / 台阶表 / 阈值 20.33 ms 与 10.67 ms / 光机容忍度 7.93 ms |
| **[0数据]** | 板端 NPU 耗时 / 板端 INT8 精度 / 光机逐帧延迟 S10 / RK3576 实际频率与温度 | — |

> ⚠️ **诚实声明**: model_zoo 性能表是**通过搜索引擎快照读到的** (本机直连 `raw.githubusercontent.com` 与 `github.com` 均超时) ⇒ 归类为 **[公开实测·第三方]** 而非 [官方]。本单**没有**任何 RK3576 板端实测数据。

---

## B4 接口取值声明 (已登记进 `state/fragments/sw.yaml` 的 `interface_claims`)

| key | value (短规范值) | note |
|---|---|---|
| `rknn_yolov5_int8_ms` | `17.4ms-3p` | RK3576 上 yolov5s@640 INT8 的**纯 NPU 耗时上界** = 17.39 ms (model_zoo 57.5 FPS 整链路上界)。**不是我们的板端实测** (板端 = [0数据]) ⇒ 值后缀 `-3p` 表示第三方来源 |
| `rknn_e2e_60ms_verdict` | `pass-conditional` | RK3576 端到端 ≤60ms (口径 A) = **PASS (有条件)**: 必须走模式 A (显示等 OD, ~25fps) + S5 ≤ 20.33 ms + 光机 S10 ≤ 7.93 ms。**若要求 60fps 显示 ⇒ fail (67.0 ms)** |
| `rknn_model_size` | `10.45MiB` | RKNN INT8 产物大小 (含 15 MiB 板端槽位 ⇒ 装得下, 余 4.5 MiB) |
| `rknn_toolkit_version` | `rknn-toolkit2-2.3.2` | PC 侧转换工具链版本 (支持 target_platform=rk3576) |
| `rknn_quant_cfg` | `w8a8/normal/channel` | 量化配置 (100 张 COCO val 校准, letterbox 640×640 黑边) |
| `rknn_output_decode` | `cut-heads+cpu-decode` | ★ 板端**必须**切掉后处理, 只留 3 路 raw head, CPU 侧解码 (sigmoid + grid + anchor); **不许用 `output` 张量** (int8 量程混装 ⇒ 概率全废) |
| `rknn_model_input_domain` | `RGB/255` | ★ 模型输入域 = RGB、值域 [0,1] (uint8/255); **不是 0-255**。A733 板端 `yolov5_pre_process_bgr.cpp` 传 0-255 —— 那是给 A733 int8 量化模型用的, **移植时不能照抄** |
| `rknn_cfg_mean_std` | `mean=0,std=255` | 板端/PC 侧喂**图像域 0-255**, 由模型内建的预处理除 255 (实测: 这样才 F1=0.33; 喂 /255 或 std=1 都 F1=0) |
| `rknn_board_out_dtype` | `int8` | RKNN 把输入/输出 dtype 从 float32 改成 int8 (转换器 4 条告警) ⇒ 板端 runtime 要显式处理 (want_float / 自反量化) |
| `rknn_e2e_modeA_threshold` | `npu<=20.33ms` | 模式 A (显示等 OD) 口径 A 达 60ms 的纯 NPU 上限 |
| `rknn_e2e_modeB_60fps_threshold` | `npu<=10.67ms` | 模式 B (异步 60fps) 口径 A 达 60ms 的纯 NPU 上限 (age=1) |

---

## B5 未决项与卡点

| # | 需要谁回答什么 | 期望时限 | 走谁 | 阻塞什么 |
|---|---|---|---|---|
| 1 | **项目总工/老板: 拿一块 RK3576 板 (哪怕是开发板) 给软件侧** —— 板端 S5 实测是"切不切芯片"这个决策点唯一的缺口 | **2026-11-05** (11-12 决策点前一周) | 项目总工 (采购/渠道) | §5.1 的条件 C2; 板端 INT8 精度; 端到端实测验收 |
| 2 | **项目总工裁决: 显示帧率目标是否接受降到 ~25fps** (RK3576 + 640×640 下 60fps 达不成, 67.0 ms) —— 老板 10-25 拍的是 "60fps 优先, 兜底 30fps", 而 RK3576 只能到 ~25fps | 2026-11-08 | 项目总工 → 老板 | Q17 的兜底值要不要从 30fps 改成 25fps |
| 3 | **项目总工裁决: 要不要走"保 60fps"路线 (换 yolov5n 或降分辨率到 ~320)** —— 代价是精度 (yolov5n 比 yolov5s 少 ~4 个点 mAP50) 或改锁定变量 "OD 640×480" | 2026-11-08 | 项目总工 → 老板 | §5.2 |
| 4 | **项目总工转达: A7S 封档项目区的 `eval_tta_yolov5s_onnx.py` 的 `decode_yolov5_raw_outputs()` 对本模型是错的** (它假设 head 已 sigmoid ⇒ 按它解出来 63.9% 的 anchor 会被判 score>0.3 ⇒ F1=0)。那个文件在 `/home/yuewuya/Public/radxa_yolo/code/` (A7S 项目区, **不是本项目**), 本单**没有改它** | 2026-11-05 | 项目总工 (转 A7S 封档项目负责人) | A733 侧的历史评估结论是否需要重算 |
| 5 | **项目总工转达: `eval_od_accuracy.py` 的注释/skill 里若引用了 "yolov5 期望 0-255" 要改** —— 本单实测该模型的输入域是 **RGB/255** | 2026-11-05 | 项目总工 | 后续复用者的坑 |
| 6 | **项目总工: AR9481 放弃后, RK3576 是否就是唯一备选?** 本单只证明了 RK3576 的**转换链 + 端到端可达性**, 不等于选型最终结论 (功耗/封装/ISP/显示接口本单没碰) | 2026-11-10 | 项目总工 | 11-12 决策 |
| 7 | **板端实测清单已列 (§5.3)**: S5 (P0) / 端到端高速摄影实测 (P0) / SDK 总耗时 vs 纯 NPU (P1) / 模式 A 显示帧率 (P1) / 板端 INT8 精度 (P1) | 板子到位后 1 周内 | sw-lead | 交卷验收 |

> **不阻塞**: ARS45 方向的任何事 (本单完全不依赖酷芯微)。

---

## B6 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace-sw/projects/smart_glasses

# B6-1 ★ 一条命令复现本单全部数字 (探针→校准集→转换→仿真→精度→端到端)
#      预计耗时 ~6 min (300 张 COCO 精度评估走 PC 仿真器, 约 380 ms/帧)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py all --images 300

# B6-2 只要端到端判定 (秒级, 不需要跑仿真)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py e2e

# B6-3 只要精度 + FP32 基线 (量化损失)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py acc --images 300 --fp32-baseline

# B6-4 演示"坑 3": 不切后处理的完整模型 (INT8 概率全废 ⇒ F1=0)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py acc --images 30 --no-cut

# B6-5 机读输出
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py all --json

# B6-6 状态源合并 (期望 rc=0) + 质量门 (期望 Q1 18/18)
python3 state/merge.py
python3 state/gate_check.py

# B6-7 单独跑"切后处理"那一步 (复用 10-28 的 cut_postprocessor.py)
/home/yuewuya/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py cut
```

---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)

- **对方**: 无 (本单不需要别的模块配合; 全部产出在 SW 域内)
- **我的需求**: —
- **我的假设 (如果对方不回应, 我会按这个做)**: 板端 S5 未实测前, **端到端结论一律按 [推算] 标注**, 且**不把任何未经板端实测的数字写进"已达标"的结论**。

---

## 待办: 需要项目总工做什么

1. **拿一块 RK3576 板** (11-05 前) —— 这是唯一能把"切不切"从推算变成实测的动作。
2. **裁决显示帧率目标** (§B5 #2) 与 "保 60fps" 路线 (#3)。
3. **把 §B5 #4/#5 转给 A7S 封档项目负责人** (decode 假设错误会误导后续复用)。
4. 本单结论可直接进 11-12 决策材料: **"RK3576 的转换链与延迟可达性已验证; 延迟不劣于已授权的兜底方案; 唯一代价是显示帧率 ~25fps 而非 60fps。"**

## 阻塞: 缺什么信息

- **板端 NPU 耗时 S5 = [0数据]** (无板) ⇒ 端到端判定是 [推算] 而非 [实测]。
- **板端 INT8 量化后的实际 F1 = [0数据]** (仿真器给出的 INT8 结果只保证"图跑通", 不等于板端数值; RKNN 官方文档也只保证 simulator 用于功能验证)。
- **光机逐帧延迟 S10 = [0数据]** (走鹃Ⅱ 未公开) ⇒ 模式 A 的光机容忍度 7.93 ms 是推算。
- **RK3576 实际 NPU 频率 / 温度 / 功耗 = [0数据]** (本单不测, 也不该由软件侧推算)。
