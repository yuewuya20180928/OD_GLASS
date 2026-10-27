# SW/ARS45_INT8_CHAIN.md — ARS45 板端 INT8 转换链 (B0~B9) 状态与解锁条件

> **单号**: ISS-087 (sw-lead, 2026-10-28) · 上游: ISS-037 §2.9 (原写"全部标 [0数据]")
> **本文件解决 ISS-087 的第 ② 项**: ARS45 板端 INT8 转换链 —— 把"骨架 + 全部 [0数据]"
> 改成"**10 步 (B0~B9) 逐条判定 + 每步的解锁条件 + 机器可复核**"。
> **配套工具**: `SW/tools/int8_chain.py` (readiness 报告 + 可跑步真跑出产物)
> **证据分级**: [实测] / [官方] / [推算] / [0数据]

---

## 1. 结论摘要

1. **10 步 (B0~B9) 里 2 步现在就能跑 (READY: B1 格式自检+PC冒烟 / B6 算子覆盖表), 4 步跑一半 (PARTIAL: B2 静态化 · B3 抽头 · B4 量化 · B9 登记), 4 步卡在外部 (BLOCKED: B0 工具链 / B5 导出+chip ID / B7 板端加载 / B8 打点)**; 加 `--build` 真跑时 READY 变 4 (B2/B3 也全跑);
   BLOCKED 的 5 步 = **B0 工具链 / B5 导出+chip ID / B7 板端加载 / B8 打点 / B4 量化器** ——
   **全部卡在"原厂交付工具链 + 有板"两件事上, 不是本机工程量**。**证据 [实测]**
2. **转换链的输入资产本身有问题**: 台账原"主模型候选" `yolov5s-sim_320_clean.onnx`
   **PC 侧推理就失败** (只改了输入 dim, 图内常量还是 640 尺度) → 已隔离;
   **唯一可用的 yolov5s ONNX 是 640 那份** (`yolov5s-sim.onnx`, 推理 OK)。**证据 [实测]**
3. **所以"转换链跑通"的真实前置是 3 件**: ① 许可干净且能推理的输入模型 (见 `SW/MODEL_LICENSE.md`);
   ② Art.Galaxy 工具链 (原厂 Q11); ③ ARS45 chip ID (原厂 Q9 第 5 条)。
   **本单把 ③ 之前的所有准备都做完了** (静态化 / 抽头 / 算子覆盖表 / 校准集检查 / 版本串 / 头校验器)。
4. **本机已具备的能力可直接复用**: A733 的 ACUITY 5 步流程 (import/quantize/export/validate/deploy)
   **脚本全在** (`~/Public/radxa_yolo/acuity_pipeline/p1~p5*.sh` —— ★ ISS-037 说 P3/P4 缺失, **实为存在**),
   工具链 (ACUITY 6.30.22 + VivanteIDE 5.11.0) 在本机可跑 → **若假设 H1 成立 (Art.Galaxy 与 ACUITY 同源),
   脚本结构 90% 可复用**。**证据 [实测]**

---

## 2. B0~B9 逐条状态 (机器判定)

> 复现: `python3 SW/tools/int8_chain.py` (readiness) · `--build` (真跑 B1/B2/B3 出产物)

| 步 | 内容 | 状态 | 本机实测 | 阻塞 / 解锁条件 |
|---|---|---|---|---|
| **B0** | Art.Galaxy 工具链到位 | ⛔ BLOCKED | 全盘探测无 `*galaxy*` 工具链; 环境变量 `ART_GALAXY_HOME/SDK` 未设 | **原厂未交付** (Q11) → 落地后设 `ART_GALAXY_HOME` 即自动识别 |
| **B1** | 输入格式 / opset 自检 | ✅ READY | `onnx.checker` 通过; ir=7; opset=14; producer=pytorch 1.10; 245 节点 / 12 算子类型; 无动态维 | — (但 Art.Galaxy 吃哪版 opset = [0数据], Q9) |
| **B1 附: PC 侧 1 帧推理冒烟** (C9, 链输入资产体检) | ✅/⛔ | 640 版 **OK** (输出 `[1,25200,85]` + 3 路 80/40/20); 320/416 版 **加载即失败** | 坏模型已隔离; 要 320/416 必须**从 checkpoint 重导出** (`code/yolov5su.pt`) |
| **B2** | 静态化 ONNX (固定输入 shape) | 🟡 PARTIAL (加 `--build` → ✅) | 本机可改写 (A733 同款方法) 并已实跑出 `_s640.onnx`; **但 320 那种"只改输入 dim"是错的** | 真静态化要用 **onnxsim** (本机无) 或**原厂工具链自带静态化** |
| **B3** | 摘 Detect 头 (后处理外移) | 🟡 PARTIAL (加 `--build` → ✅) | `onnx.utils.extract_model` 可跑 → 已实跑出 `_rt.onnx`; head = `['350','498','646']` (yolov5); yolox = `['798','824','850']` | 每家模型 head 名不同 → **逐模型核对**, 不能照抄 |
| **B4** | INT8 量化 (校准集 / 参数 / 量化器) | 🟡 PARTIAL | 校准集 **100 张** (要求 ≥100, A733 实测 6 张不够); `.quantize` 参数资产在; A733 方案 = `pcq` | **量化器本体需 Art.Galaxy** (方案名/校准接口/输出能否直通量化整数) = [0数据] (Q9); 眼镜场景校准集 = [0数据] |
| **B5** | 导出板端产物 + 文件头/chip ID | ⛔ BLOCKED | NBG 头校验器**已就绪** (magic `VPMN` / version / format / chip LE uint32 @ byte 8-11) | **ARS45 chip ID = [0数据]**; ⚠️ **A733 的 0x1000003B 不可套用** (套错 → 板端报 SRAM size 错, 已踩过 2 次) |
| **B6** | 算子覆盖表核对 | ✅ READY | 12 种算子 / 245 节点; **全部命中 A733 实测支持集** (Conv 60 / Sigmoid 60 / Mul 69 / Concat 17 / Add 10 / Slice 9 / Reshape 6 / MaxPool 3 / Transpose 3 / Sub 3 / Pow 3 / Resize 2) | Art.Galaxy 官方支持清单 = [0数据] (Q9 第 2 条) → 本表先当"风险清单"用 |
| **B7** | 板端加载 + 首帧 shape 对齐 | ⛔ BLOCKED | 判据已写死 (板端首帧输出 shape 必须与 PC 端逐路一致) | 无板 |
| **B8** | 纯 NPU vs SDK 总耗时 打点 | ⛔ BLOCKED | 打点口径与埋点表已写死 (见 §4) | 无板 + 原厂 SDK 打点接口 (Q8) |
| **B9** | 登记台账 + 精度评估 + 回归 | 🟡 PARTIAL | 离线可跑 R-01/R-02/R-03/R-14; 台账登记用 `model_asset_check.py --new`; 版本串格式已对齐 | 无板端产物 → R-04 起全不可跑; **板端模型台账条数 = 0** |

**汇总** (默认不带 `--build`): **READY 2 · PARTIAL 4 · BLOCKED 4** (共 10 步, B0~B9)
带 `--build` 真跑 (出产物): **READY 4 · PARTIAL 2 · BLOCKED 4**

---

## 3. 阻塞项的精确解锁条件 (写给项目总工转原厂)

| 阻塞步 | 必须由谁给什么 | 给了之后本机做什么 | 备注 |
|---|---|---|---|
| **B0** | **Art.Galaxy 工具链包 + 手册** (docker? SDK? 需不需要授权/NDA? 跑在 Linux x86 还是 Windows?) | 设 `ART_GALAXY_HOME` → B0 自动转 READY; 然后按手册把量化/导出命令接进本脚本 B4/B5 段 | Q11 追加第 10 条 |
| **B5** | **ARS45 的 chip ID + 板端文件头布局** (是否同 `VPMN` 头) + 导出命令 | 拿到产物 → `model_asset_check.py` 的 C5/C7 直接判; 版本串按 `model=<family>-int8-ag2-<sha8>` 生成 | Q9 追加第 5 条 |
| **B1/B6** | **支持的输入格式 + opset 范围 + 算子支持清单** | 把 B6 的"⚠️ 未在 A733 实测集内"升级成正式覆盖表 | Q9 追加第 1/2 条 |
| **B4** | **量化方案名 / 校准接口 / 输出能否直通量化整数** (不强制 FP32) | 接进 B4; 决定 tensor_to_fp 的 memcpy 量 (A733: INT8 输出可省 4×) | Q9 追加第 3 条 |
| **B7/B8** | **有板 + 板端 SDK 打点接口** | 跑首帧 shape 对齐 + 分段耗时 (min/avg/max/帧数) | Q8 + 投板 |

★ **本单不制造这 5 个数字** —— 它们是外部依赖, 本单只把它们变成**有名字、有责任人、有时限、可机械判状态**的条目。

---

## 4. B8 打点口径 (先写死, 板子回来直接用)

**铁律** (与 `SOUL.md` / AGENTS.md 一致): **纯 NPU 耗时 vs SDK 总耗时必须分开报**。
A733 实测: `vip_run_network` 27.19 ms vs `awnn_run` total 36.51 ms → 差值 9.29 ms 是 **INT8→FP32 软件反量化 (占 25%)**。

| 埋点 | 段 | 备注 |
|---|---|---|
| `t_capture` | sensor 曝光 → 帧到 CPU | 曝光时间单列 (光源/增益) |
| `t_pre` | 缩放 / 归一化 / 布局转换 | NCHW vs NHWC、RGB/BGR、mean/scale |
| **`t_npu`** | ★ **纯 NPU 推理** | 只算网络执行, 不含前后处理 |
| **`t_sdk_total`** | ★ **SDK 总耗时** | 含反量化 / 张量搬运 |
| `t_decode` | decode + NMS | 板端 CPU 解 3 路 head (与 `SW/SW_REQUIREMENTS.md` M5 decode 方案一致) |
| `t_draw` | 画框 | |
| `t_compose` | 叠加进显示帧 | |
| `t_display` | 送 MIPI-DSI → 光机 | 端到端预算的最后一跳 |

**每段必须给**: min / avg / max + **采样帧数** (单帧不算数)。端到端汇总回 `PROJECT_TRACKER.md` §3 预算表 (由项目总工汇总, sw-lead 只报自己那段)。

---

## 5. 工具链接入契约 (原厂把工具链给过来, 我们怎么接)

```
约定环境变量:
    ART_GALAXY_HOME   = 工具链根目录 (脚本据此探测 B0)
    ART_GALAXY_SDK    = 命令行工具目录 (pegasus 之类)
    ART_GALAXY_CHIP   = ARS45 chip ID (十六进制, 如 0x1000003B)  ← 由原厂给, 不许猜
约定命令接口 (本脚本 B4/B5 段待填):
    B2 静态化 : <工具链自带命令> <in.onnx> <out.onnx> --input-shape 1,3,<N>,<N>
    B4 量化   : <工具链自带命令> <model> <quant_scheme> <calib_dataset.txt>
    B5 导出   : <工具链自带命令> <model> <quant_scheme> <out.nb>
产物登记   : python3 SW/tools/model_asset_check.py --new <out.nb>   → 打印台账行骨架
板端校验   : model_asset_check.py 的 C5 (magic VPMN) / C6 (format) / C7 (chip) / C4 (15 MiB 槽位)
```

**A733 侧 5 步流程 ↔ ARS45 B0~B9 映射 (假设 H1 成立时的复用率)**:

| A733 (ACUITY, 本机已跑通) | ARS45 (Art.Galaxy) | 复用度 |
|---|---|---|
| P1 `pegasus_import` (+ onnxsim + 抽 3 路 head) | B2 + B3 | **结构可复用**, 命令要改 |
| P2 `pegasus_quantize` (pcq) | B4 | 方案名要原厂给 |
| P3 `pegasus_export_ovx_nbg` (v3) | B5 | **★ optimize flag 就是 chip ID 错的那次坑** |
| P4 `nbinfo` 验证输出格式 (INT8 vs FP32) | B5/B9 | 逻辑可复用 |
| P5 `scp` 到板端 + 跑 60 s 看 fps | B7/B8 | 逻辑可复用 |

**A733 侧资产 (本机实测存在, 可直接当模板)**: `~/Public/radxa_yolo/acuity_pipeline/p1_import.sh` · `p2_quantize.sh` ·
`p3_export_nbg.sh` · `p4_validate.sh` · `p5_deploy.sh` · `run_all.sh` (★ ISS-037 记"P3/P4 缺失" —— **实为存在, 已更正**)。

---

## 6. 校准集 (B4 的隐藏坑)

| 项 | 要求 | 现状 | 等级 |
|---|---|---|---|
| 张数 | **≥100 张** (A733 实测: 6 张不够用) | 100 张 ✔ | [实测] |
| 分布 | **眼镜场景** (佩戴视角、近距离、复杂背景、逆光) | **现存 100 张是 COCO 通用集 → 分布不符** | [0数据] |
| 采集 | 需样机 + 佩戴场景 | 待样机 | [0数据] |
| 归属 | 校准集也是资产 (R-7: 换量化参数 = 换模型) | 已登记 `MOD-YOLOV5S-320-CALIB-DATASET` | [实测] |

---

## 7. 0 数据清单 (本单不装作有数)

| 0 数据项 | 谁能解 | 什么时候 |
|---|---|---|
| Art.Galaxy 工具链 | 原厂 (Q11) | 资料同期 |
| ARS45 chip ID / 板端文件头布局 | 原厂 (Q9 第 5 条) | 资料同期 |
| Art.Galaxy 支持的 opset / 算子清单 | 原厂 (Q9 第 1/2 条) | 资料同期 |
| 量化方案名 / 输出能否直通量化整数 | 原厂 (Q9 第 3 条) | 资料同期 |
| ARS45 板端 INT8 模型 / 转换成功与否 | 工具链 + 板 | 投板后 |
| 纯 NPU 耗时 / SDK 总耗时 | 板端实测 | 投板后 |
| 量化精度损失实测数字 | 板端模型 | 投板后 |
| 眼镜场景校准集 | 样机 | EVT 前 |
| ONNX 口径 COCO 评估器 (R-08/R-09) | 我自己写 | 板子回来前 |

---

## 8. 自证复现命令 (B6)

```bash
cd projects/smart_glasses

# ① 转换链 readiness (10 步逐条判定 + 阻塞原因 + 解锁条件)
python3 SW/tools/int8_chain.py
# 预期: READY 2 · PARTIAL 4 · BLOCKED 4 (共 10 步); B0/B5/B7/B8 明确标 BLOCKED + 解锁条件

# ② 机读
python3 SW/tools/int8_chain.py --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['summary'])"

# ③ 真跑可跑步 (出产物到 /tmp, 不污染仓库)
python3 SW/tools/int8_chain.py --model /home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx \
        --input-size 640 --build
ls -la /tmp/ars45_int8_chain/

# ④ 坏模型复现 (链输入资产体检)
python3 SW/tools/int8_chain.py --model /home/yuewuya/.openclaw/workspace/yolov5s-sim_320_clean.onnx
# 预期: B1 = BLOCKED (链输入资产本身跑不起来)

# ⑤ 台账 + 放行门禁 (L 计数)
python3 SW/tools/model_asset_check.py
# 预期: 资产 11 条 · FAIL 0 · rc=0 · 量产放行阻断项 (L): 0 条

# ⑥ A733 参考链 (路线 A 模板全在)
ls ~/Public/radxa_yolo/acuity_pipeline/p{1,2,3,4,5}*.sh

# ⑦ 项目门禁
python3 state/merge.py && python3 state/gate_check.py
```
