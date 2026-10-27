# SW/MODEL_ASSETS.md — 模型资产登记与 INT8 量化管理

| 项 | 值 |
|---|---|
| **文档** | `SW/MODEL_ASSETS.md` |
| **版本** | v1.0 (2026-10-27) |
| **归属** | 软件总工 (sw-lead) |
| **来源 issue** | **ISS-037**「模型资产与 INT8 量化管理缺失 (权重是资产, 现在散在 sw 需求里)」· owner=sw-lead · reporter=main · due=2026-10-29 |
| **上游真源** | `PROJECT_TRACKER.md` §7 可复用资产 / §3 端到端预算 / §5 风险 R5 |
| **本域真源** | `SW/SW_REQUIREMENTS.md` (M3/M4/M5 模块 + M4-R1~R6 验收标准) / `SW/FLASH_AND_VERSION.md` (§2.3 模型版本块 / §4.1 分区表) |
| **机械复核** | `python3 SW/tools/model_asset_check.py` (rc=0 / 放行阻断项 L 计数) |
| **证据分级** | `[实测]` 本机跑出来的 · `[官方]` 原厂书面/官网 · `[推算]` 由实测/官方推导 · `[0数据]` 拿不到 |

---

## B1 结论摘要

1. **模型资产从"散在需求里"变成"有台账、有机器复核"**: 登记 **10 条**资产 (3 条 ARS45 候选 + 7 条 A733 参考), 全部带 `sha256[:16]` / 大小 / 许可 / 格式版本 / 状态; 复核脚本 `SW/tools/model_asset_check.py` 一次跑完 **10 条资产 × 60 项判定**, rc=0。**证据 [实测]**

2. **★ 发现 3 个"名字骗人"的资产 (同名不同内容)**: 三份都叫 `yolov5s-sim` 的 ONNX 体积完全相同 (29,337,706 B) 但 **sha256 三者互不相同**, 输入分辨率分别是 **320 / 320 / 640**; 其中 `_clean` 与 `_v2` **逐字节完全相同** (sha256 `340978ec59391f69`) → 文件名里的 "v2" 不代表版本差异。**这直接证明"模型必须有唯一 ID + sha256, 路径和文件名都不能当版本"**。证据 [实测]

3. **★ 许可栏是空的 —— 这是量产阻断项**: 3 条 yolov5s-sim 系 ONNX 的 `metadata_props` **一个字段都没有** (无 license / author / version) → 许可 **[0数据]**; 唯一带许可的是 `yolov8s.onnx` = **AGPL-3.0** → 商用须向 Ultralytics 采购商业许可。工具输出 **2 条放行阻断项 (L1 许可未知 + L4 AGPL 商用受限)**。**不解决 → 量产评审不许过**。证据 [实测]

4. **★ 本地有 2 条 .nb 资产是死的 (chip ID 错)**: `yolov8s_coco80.nb` 与 `acuity_pipeline/network_binary.nb` 的 NBG 头 byte 8-11 = **0x10000020**, 而 A733 真实 chip ID 是 **0x1000003B** → 板端加载后报 SRAM size 错。已标 `state=quarantined` 隔离, 不进任何流程。本地**可用**的 .nb 只有 3 条 (全在 `yolov8s_scene_ft*` 系列)。证据 [实测] (A733 历史踩坑见 §2.6)

5. **★ ARS45 板端模型资产 = 0 个 (板端产物 0/0 数据)**: 没有板、没有 Art.Galaxy 工具链、没有 ARS45 chip ID → 本单交付的是**台账 + 流程 + 回归门禁**, **不是**"模型已转换"。A733 侧完整可复现的 5 步量化流程 (`p1_import`→`p5_deploy`) 本机**全部可跑**, 作为 ARS45 的方法论模板已登记 (§2.3)。证据 [实测] + [0数据]

---

## B2 验收标准自评

| 验收标准 (ISS-037 task_brief) | 自评 | 依据章节 | 说明 |
|---|---|---|---|
| ① 当前模型清单 (来源/版本/许可/大小) | ✅ **通过** | §1.2 / §1.3 / §1.4 | 10 条资产逐条给出来源路径 / sha256[:16] / 字节数 / 许可 / 输入输出 shape / 算子类型 / NBG 头字段; 台账与 `model_asset_check.py` 的 MANIFEST 逐字段一致 (可 diff) |
| ② INT8 量化流程与工具 | ✅ **通过** (ARS45 段为 ⚠️ 未验) | §2.1~§2.10 | 工具链盘点 (本机实测)、A733 已跑通的 5 步流程、量化类型选择、校准集要求、NBG 头三件套铁律、Art.Galaxy 适配清单 (10 条待原厂回答)、算子覆盖表模板 |
| ③ 量化精度损失评估方法 | ✅ **通过** (方法已定, 数据 0) | §3.1~§3.8 | L0~L4 五层评估金字塔、量化器健康度 3 指标、obj head 专项、5 条量化判据门限表、COCO 评测集与工具链、板端实测项 (0 数据项单列) |
| ④ 模型更新后的回归验证要求 | ✅ **通过** | §4.1~§4.7 | R-01~R-14 回归用例矩阵 (含判据/工具/失败处置)、版本串绑定、不通过禁止刷写、变更记录模板 |

**未达标/未验项 (不粉饰)**:

| 项 | 状态 | 为什么 | 影响 |
|---|---|---|---|
| ARS45 板端 INT8 模型 | ⚠️ **0 数据** | 无板 + 无 Art.Galaxy 工具链 + 无 ARS45 chip ID | §2.9 的转换流程是**骨架**, 跑不出东西; 转换成功与否由 Q9/Q11 答 |
| 量化精度损失实测数字 | ⚠️ **0 数据** | 无 ARS45 板端模型, 无从量化 | §3 全部是**方法 + 判据**, 数值栏全空; 等 §2.9 跑通后回填 |
| yolov5s-sim 系 ONNX 的许可 | ⚠️ **[0数据]** | onnx 无 metadata; 源文件在个人 workspace, 无 LICENSE 文件 | **量产阻断项 L1**, 需项目总工向原厂/来源方问 |
| A733 参考资产能否用于 ARS45 | ⚠️ **[推算]** | Art.Galaxy 与 VeriSilicon ACUITY/VIPLite 是否同源**未验证** | §2.2 列为假设 H1, 需 Q9 确认; 若不同源, §2.3 流程需重做 (脚本结构可复用) |
| `p3_export_nbg.sh` 缺失 | ⚠️ **[实测] 缺件** | `acuity_pipeline/` 下只有 `p1/p2/p5` + `00_env`, **P3 (export nbg) 与 P4 脚本不在本机** | §2.3 标注 P3/P4 为"历史记录, 需从原 A733 工程找回"; 找回后补进台账 |

---

## B3 证据分级

| 结论 | 等级 | 出处 |
|---|---|---|
| 10 条资产的大小 / sha256[:16] / 存在性 | **[实测]** | `python3 SW/tools/model_asset_check.py` (2026-10-27 本机跑) |
| `yolov5s-sim` 三份文件 sha256 互不相同、两份逐字节相同 | **[实测]** | 同上, C3 + C8 |
| `yolov5s-sim` 输入分辨率 320 / 320 / 640 | **[实测]** | onnx `graph.input` shape, 同上 C7 |
| yolov5s-sim ONNX 的 `metadata_props` 为空 (许可未知) | **[实测]** | onnx `metadata_props` 长度 = 0 |
| `yolov8s.onnx` license = AGPL-3.0 | **[实测]** | onnx `metadata_props["license"]` |
| 2 条 .nb 的 chip ID = 0x10000020 (错), 3 条 = 0x1000003B (对) | **[实测]** | NBG 头 byte 8-11 解析 (小端 uint32) |
| NBG 头布局 (magic/version/format/chip) | **[实测]** | 本机 5 份 .nb 全部命中 `VPMN` + format=2 |
| 板端 model_a/model_b 槽位 = 15 MiB | **[官方·本域]** | `SW/FLASH_AND_VERSION.md` §4.1 + `SW/tools/s2_rescue_config.example.json` (15,728,640 B) |
| A733 上 INT8 .nb 的收益 (FPS 10.4→13.19, tensor_to_fp 40.56→13.98 ms) | **[实测·历史]** | A733 工程记忆 2026-08-07 00:50 (v24 pipeline) |
| A7S 上 INT8 把 obj head 压扁 (sigmoid 最大值 0.46) | **[实测·历史]** | `SW/SW_REQUIREMENTS.md` §5 M4 备注 |
| ACUITY 6.30.22 / VivanteIDE 5.11.0 / 7.4 GB docker rootfs 在本机 | **[实测]** | `ls /home/yuewuya/miniconda3/envs/acuity` + `Public/radxa_yolo/acuity_rootfs` |
| 校准集 100 张 COCO 图在 `/home/yuewuya/Public/radxa_yolo/calib_yolov5_100` | **[实测]** | `ls` 计数 = 100 |
| COCO val2017 5000 张 + `instances_val2017.json` 在 `/work/object_detection/data/coco/raw/` | **[实测]** | `ls` 计数 + 文件存在 |
| ARS45 用的是 Art.Galaxy 工具链 | **[官方·转述]** | `PROJECT_TRACKER.md` §2.1 / Q9 / Q11 (原厂书面资料**尚未到手**) |
| Art.Galaxy 与 VeriSilicon ACUITY/VIPLite 同源 | **[推算] 假设 H1, 未验证** | 酷芯微 ARS45 = "自研第四代 NPU" + 官网不提工具链 → 只能假设, §2.10 列成待确认问题 |
| ARS45 的 NBG/模型文件格式与 chip ID | **[0数据]** | 无板、无资料 |
| yolov5s INT8 在 ARS45 上的耗时 | **[0数据]** | 原厂从没公开跑过 YOLO (tracker 已知卡点) |

---

## B4 接口取值声明 (interface_claims)

> 已同步登记进 `state/fragments/sw.yaml` 的 `interface_claims`。`value` 一律短规范值。

| key | value | 说明 (note) |
|---|---|---|
| `model_asset_id_scheme` | `MOD-<FAMILY>-<VER>-<RES>` | 模型唯一 ID 规则; 例 `MOD-YOLOV5S-320-INT8`。版本只认 sha256[:16], 不认文件名 |
| `model_asset_slot_budget` | `15MiB` | 板端 model_a/model_b 单槽上限 (15,728,640 B), 来源 FLASH_AND_VERSION §4.1 |
| `model_asset_registry_tool` | `SW/tools/model_asset_check.py` | 台账机器复核入口; rc=0 = 台账与实物一致 |
| `model_asset_release_gate` | `L=0` | 量产放行判据: 放行阻断项计数必须为 0 (L1 许可未知 / L2 超槽 / L3 chip ID / L4 AGPL) |
| `model_version_string_fmt` | `yolov5s-int8-ag2-<sha8>` | 与 FLASH_AND_VERSION §2.5.1 一致, 不改; `<sha8>` = 板端模型文件 sha256 前 8 位 |
| `model_calib_min_images` | `100` | INT8 校准集最少张数 (A733 实测: 6 张不够用) |
| `model_quant_scheme` | `pcq` | A733 侧真正 INT8 的量化方案名 (per-channel symmetric affine); Art.Galaxy 侧方案名 [0数据] |
| `model_regression_gate` | `R-01..R-14` | 模型变更后必跑的回归用例编号集合; 全过才允许刷板 |

---

## 1. 模型资产清单 (验收①)

### 1.1 登记规则 (为什么要有台账)

| 规则 | 内容 | 依据 |
|---|---|---|
| **R-1 唯一 ID** | 每个模型文件一个 `MOD-<FAMILY>-<VER>-<RES>` ID; 同一内容**不得**有两个 ID | §1.4 实测: 同名文件 sha256 不同 |
| **R-2 版本只认 sha256** | 版本标识 = 文件 `sha256[:16]`, **文件名里的 v2/clean/final 一律不作数** | §1.4 实测: `_clean` 与 `_v2` 逐字节相同 |
| **R-3 必填字段** | 来源路径 / 大小 / sha256 / 许可 / 格式与格式版本 / 状态 / 角色 / 备注 | ISS-037 验收① |
| **R-4 许可不许空** | 许可未知必须显式写 `[0数据]`, 并生成放行阻断项 L1 | §1.5 |
| **R-5 状态机** | `candidate`(PC 侧源) → `active`(板端在用) → `quarantined`(判死) / `reference`(他项目参考) | §1.2 |
| **R-6 板端产物单独登记** | PC 侧源 (ONNX/PT) 与板端产物 (NBG/Art.Galaxy 格式) **分开登记** —— 容量门禁只管板端产物 | §1.6 |
| **R-7 量化参数也是资产** | `.quantize` / 校准集 / 量化脚本 **必须与权重同批登记** —— 换量化参数 = 换模型 | §2.4 |

### 1.2 主台账 (唯一真源 = `SW/tools/model_asset_check.py` 的 `MANIFEST`)

> 下表与脚本里的 `MANIFEST` **逐字段一致**; 改一个必须改另一个 (脚本自检会 diff 大小/sha256)。

| ID | 平台 | 状态 | 格式 | 来源路径 | 大小 (B) | sha256[:16] | 许可 | 备注 |
|---|---|---|---|---|---|---|---|---|
| ~~MOD-YOLOV5S-320-INT8~~ | candidate | **quarantined** | ONNX | `~/.openclaw/workspace/yolov5s-sim_320_clean.onnx` | 29,337,706 | `340978ec59391f69` | **AGPL-3.0** | ★ **已判死 (2026-10-28)**: C9 冒烟实测 onnxruntime 加载即失败 (只改输入 dim, 图内常量仍 640 尺度) → 模型本身是坏的; 许可 = AGPL-3.0 (溯源见 `SW/MODEL_LICENSE.md` §1) |
| MOD-YOLOV5S-320-INT8-DUP | candidate | **quarantined** | ONNX | `~/.openclaw/workspace/yolov5s-sim_320_v2.onnx` | 29,337,706 | `340978ec59391f69` | **AGPL-3.0** | ★ 与上一条**逐字节相同** → 台账去重, 只留一条 (同因同坏) |
| **MOD-YOLOV5S-640-ARS45-SRC** | candidate | **licensing-hold** | ONNX | `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx` | 29,337,706 | `20368be665f6f59a` | **AGPL-3.0** | ★ **唯一实测可推理的 yolov5s ONNX (640)** —— C9 冒烟 OK; 血缘: ultralytics/yolov5 v6.0 → onnxsim → 抽 3 路 head; 旧 ID `MOD-YOLOV5S-320-INT8-ACUITY` 名不副实 (ID 写 320 实为 640) → 已由本条取代 |
| **MOD-YOLOV8S-COCO80-ONNX** | candidate | **licensing-hold** | ONNX | `/work/object_detection/yolov8s_coco80/workspace/yolov8s.onnx` | 44,842,647 | `111da30a25b6c585` | **AGPL-3.0** | ★ 备选主模型; opset 13 / 263 节点 / 17 算子类型; 输入 `[1,3,640,640]`; C9 冒烟 OK; **未采购 Enterprise 前禁入交付物** |
| **MOD-SSDMBV2-FPNLITE-320-COCO90-TFODAPI** | candidate | **candidate** | SavedModel | `/work/object_detection/pretrained/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8` | 9,640,645 (saved_model.pb) | — | **Apache-2.0** | ★ **交付集里唯一许可干净的候选** (TF OD API, pipeline.config `num_classes: 90` → COCO 可用 80 类); ⚠️ NPU 可转换性 = [0数据] |
| MOD-YOLOV8S-COCO80-NB | A733-ref | **quarantined** | NBG | `/work/object_detection/yolov8s_coco80/workspace/yolov8s_coco80.nb` | 8,450,776 | `7fa016615610adaa` | — | ★ chip ID **0x10000020 (错)** → 板端不可加载 |
| MOD-YOLOV8S-SCENEFT-NB | A733-ref | reference | NBG | `/work/object_detection/yolov8s_scene_ft/deploy/yolov8s_scene_ft.nb` | 12,559,680 | `6ac6975036524637` | — | ★ chip **0x1000003B ✓**, format 2 ✓; 板端实测可加载 (2026-08-17); 12.0 MiB ≤ 15 MiB ✓ |
| MOD-YOLOV8S-SCENEFT-V2-NB | A733-ref | reference | NBG | `/work/object_detection/yolov8s_scene_ft_v2/deploy/yolov8s_scene_ft_v2.nb` | 7,873,008 | `e8a53286029272a4` | — | chip ✓; 7.5 MiB, 本地最小可用 NBG |
| MOD-YOLOV5S-A733-NB-BASELINE | A733-ref | **quarantined** | NBG | `~/Public/radxa_yolo/acuity_pipeline/model/wksp_nbg_unify/network_binary.nb` | 6,479,672 | `e6827040cb29c60d` | — | ★ chip ID **0x10000020 (错, `--optimize v3` flag 造成)** |
| MOD-YOLOV5S-320-QUANT-PARAM | A733-ref | reference | quantize | `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim_320.quantize` | 620,518 | `c1d884d2f196fe45` | — | ★ **量化参数表本身就是资产**: per-tensor `asymmetric_affine`, `qtype=i8`, rtne 舍入 |
| MOD-YOLOV5S-320-CALIB-DATASET | A733-ref | reference | dir | `~/Public/radxa_yolo/calib_yolov5_100` | 100 张 jpg | — | — | ★ **校准集**: A733 实测 6 张不够, 现存 100 张 (COCO val) |

**★ ARS45 板端产物登记条数 = 0** —— 因为还没有板、还没有 Art.Galaxy 工具链、还没有 ARS45 的 chip ID (全部 [0数据])。

### 1.3 非 OD 模型 (不刷板, 但要登记)

| 类别 | 位置 | 用途 | 状态 |
|---|---|---|---|
| ISP 参数集 | 板端 `isp` 分区 (1 MiB) | ISP 标定参数, **不是模型但同属"参数资产"** | 已由 `SW/FLASH_AND_VERSION.md` §3 管 (`calib=ISP-CALIB-0003-r2`) |
| 版本块 (version block) | 板端 32 KiB 独立分区 | 6 分项版本串, 含 `model=` 字段 | 已由同文档管 |
| EfficientDet / SSD (TF OD API) | `/work/object_detection/pretrained/` | 上一项目的 **x86 基准**模型 (D1 mAP@0.5=0.5056), **不上板** | 仅作精度参考基线, 不登记为 ARS45 候选 |

### 1.4 ★ "名字骗人"的三条实测 (为什么 R-1/R-2 是硬规则)

```
$ ls -la ~/.openclaw/workspace/yolov5s-sim_320_clean.onnx \
          ~/.openclaw/workspace/yolov5s-sim_320_v2.onnx \
          ~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx
-rw-r--r-- 29337706  yolov5s-sim_320_clean.onnx     sha256[:16]=340978ec59391f69
-rw-r--r-- 29337706  yolov5s-sim_320_v2.onnx        sha256[:16]=340978ec59391f69   ← 同上, 逐字节相同
-rw-r--r-- 29337706  .../acuity_pipeline/model/yolov5s-sim.onnx
                                                  sha256[:16]=20368be665f6f59a   ← 同体积, 不同内容
输入 shape: [1,3,320,320] / [1,3,320,320] / [1,3,640,640]
```

| 发现 | 后果 | 对策 |
|---|---|---|
| `_clean` 与 `_v2` **逐字节相同** | 文件名声称的两个版本实为一个 → 谁也不知道板上是哪版 | R-2: 版本只认 sha256 |
| 三份**体积完全相同**但 sha256 不同 | 体积不能当版本标识 (体积只反映 initializer 个数) | R-2 同上 |
| 同名 `yolov5s-sim` 却是 **320 与 640 两种输入** | 转换时拿错文件 → 板端 shape 不匹配, 推理结果全错且不报错 | R-1 + 转换脚本**固定 sha256 校验** (§2.3 P1 前置检查) |

### 1.5 ★ 许可栏 (量产放行阻断项) —— ISS-087 修订版

> **判定口径 (2026-10-28 起)**: **"许可未判定" 才是阻断项**; "`metadata_props` 为空" 只是取数方式问题。
> 台账新增 `license_state` (`permissive` / `agpl-granted` / `agpl-no-grant` / `unknown`) 与 `license_grant` (Enterprise 授权号)。
> **完整判定证据链 / 采购与法务路径 / 成本区间 → `SW/MODEL_LICENSE.md`**。

| 资产 | 许可 | license_state | 商用结论 | 等级 |
|---|---|---|---|---|
| MOD-YOLOV5S-320-INT8 (+DUP) | **AGPL-3.0** | agpl-no-grant | ⚠️ 已隔离 (模型是坏的); 许可本身同下 | [实测·溯源] + [官方] |
| MOD-YOLOV5S-640-ARS45-SRC | **AGPL-3.0** | agpl-no-grant | ⚠️ AGPL 强 copyleft: 商用须采购 **Enterprise License**, 否则不得随闭源固件分发 | [实测·溯源] + [官方] |
| MOD-YOLOV8S-COCO80-ONNX | **AGPL-3.0** (metadata 原值) | agpl-no-grant | ⚠️ 同上 → 采购 Enterprise License 或改用 Apache-2.0 栈 | [实测] + [官方] |
| MOD-YOLOV8S-SCENEFT*.NB / MOD-YOLOV5S-A733-NB-BASELINE / *.quantize | **AGPL-3.0** (继承上游) | agpl-no-grant | 派生资产继承上游许可 | [推算] |
| **MOD-SSDMBV2-FPNLITE-320-COCO90-TFODAPI** | **Apache-2.0** | permissive | ✅ 商用无附加义务 | [官方] |

**阻断项定义 (新)**:

| 阻断项 | 定义 | 现状 |
|---|---|---|
| **L1** | 许可**未判定** (台账 `expected_license` 为空) | **0** ✅ (原: 1 条 [0数据]) |
| **L2** | 板端产物超 15 MiB 槽位 | 0 ✅ |
| **L3** | chip ID 与目标 NPU 不符 | 0 ✅ |
| **L4** | AGPL-3.0 且**无** Enterprise 授权记录 → 商用受阻 | **0** ✅ (2 条 AGPL 资产已置 `licensing-hold` 禁入交付物; 采购后填 `license_grant` 即复活) |
| **L5** | 交付集资产 PC 侧推理冒烟失败 (C9) → 模型本身是坏的 | 0 ✅ |

**处置 (不自行外发, 走项目总工)**:
1. **L1 已闭合**: `yolov5s-sim` 系许可由 [0数据] **判定为 AGPL-3.0** (证据链: `SW/MODEL_LICENSE.md` §1.2, 一条命令 `python3 SW/tools/license_probe.py` 可复现)。
2. **L4 待老板拍板**: 采购 Enterprise License (预算量级 10⁴–10⁵ USD [推算], 无公开价 [0数据]) **或** 改用 Apache-2.0 栈 (YOLOX-s / PP-YOLOE / TF OD API) —— **不采购则商用受阻** (AGPL §6 要求随硬件分发即提供完整对应源码, 与闭源固件直接冲突)。
3. **替代路线**: 原厂 (酷芯微) 若能提供**许可由原厂承担**的官方预编译模型 → 最省事 (已列入 Q9 追加问题)。⚠️ 但 A733 那份官方 .nb 实测**类别映射错 → 422 false positive**, 官方资产也要跑回归 (§4)。

### 1.6 容量门禁 (板端槽位)

| 项 | 值 | 依据 |
|---|---|---|
| 板端 `model_a` / `model_b` 单槽 | **15 MiB = 15,728,640 B** | `SW/FLASH_AND_VERSION.md` §4.1 推荐 C 分区表 + `SW/tools/s2_rescue_config.example.json` |
| A/B 双槽合计 | 30 MiB | 同上 |
| 门禁作用对象 | **只管板端产物** (`.nb` / Art.Galaxy 格式), 不管 PC 侧 ONNX | ONNX 不刷板 |
| 现状 | 本地 3 条可用 .nb 全部 ≤ 15 MiB (7.5 / 12.0 MiB) ✓ | [实测] |

⚠️ **与 §4.1 的耦合**: model 15×2 + app 8×2 + kernel 8 + rootfs 30 + boot 1 + isp 1 = **90 MB** → 64 MB SPI-NOR **装不下**, flash 容量下限 **≥128 MB** (`interface_claims.flash_capacity_floor`, 已登记)。**模型体积是这条容量线的组成部分**: 若换 yolov8s (44.8 MB 源文件, 量化后 NBG 未实测) → 槽位与 flash 容量都要重算。

---

## 2. INT8 量化流程与工具 (验收②)

### 2.1 两条路线 (必须分开写, 不能混)

| | **路线 A: ACUITY/VIVANTE (A733 已跑通)** | **路线 B: Art.Galaxy (ARS45 目标)** |
|---|---|---|
| 工具链 | VeriSilicon **ACUITY Toolkit 6.30.22** (Pegasus) + **VivanteIDE 5.11.0** cmdtools | **Art.Galaxy** (酷芯微自研, 名称出自 tracker §2.1/Q9/Q11) |
| 本机可用性 | ✅ **完全可用** (conda env + docker rootfs + cmdtools 都在) | ❌ **本机没有, 且原厂资料未到** → [0数据] |
| 输入 | ONNX (静态 shape) | 未知 [0数据] |
| 输出 | `.nb` (NBG, magic `VPMN`) + `.json` + `.data` + `.quantize` | 未知 [0数据] |
| 板端运行时 | `awnn_create` / `vip_run_network` / `awnn_run` | 未知 (大概率同名同源, **假设 H1**) |
| 现状 | **可复现** (§2.3 5 步) | **只有骨架** (§2.9) |

> ★ **假设 H1**: Art.Galaxy 与 VeriSilicon ACUITY/VIPLite 同源或派生 (依据: 酷芯微官网只提"自研第四代 NPU", 未提工具链; 两种 NBG 都用 `VPMN` 头 + 同一套 `awnn` API 命名习惯)。**假设 H1 未验证** —— §2.10 列成 Q9 的追加问题。**若 H1 成立**, §2.3 的脚本结构可 90% 复用; **若不成立**, 只复用流程骨架 (P1 静态化 → P2 量化 → P3 导出 → P4 算子覆盖核对 → P5 部署), 具体命令全部要按原厂手册重写。

### 2.2 工具链资产盘点 (本机实测, 2026-10-27)

| 工具 | 位置 | 版本 | 状态 |
|---|---|---|---|
| ACUITY Toolkit (conda env) | `/home/yuewuya/miniconda3/envs/acuity` (`acuity-6.30.22.dist-info`, Author=Verisilicon) | **6.30.22** | ✅ 可用 |
| ACUITY 命令行工具 | `.../envs/acuity/acuity_command_line_tools/` (`pegasus.py`, `setup.py`, `tools/`) | — | ✅ 可用 |
| VivanteIDE cmdtools | `~/Public/radxa_yolo/acuity_rootfs` (docker rootfs, **7.0 GB**)<br>`.../root/Vivante_IDE/VivanteIDE5.11.0/cmdtools/` | **5.11.0** | ✅ 可用 (含 `common/cfg/VIP9000NANODI_PID0X1000003B.config`) |
| 量化 pipeline 脚本 | `~/Public/radxa_yolo/acuity_pipeline/` (`00_env/p1_import/p2_quantize/p5_deploy`) | — | ⚠️ **P3 (export nbg) / P4 缺失** |
| 量化产物 | `.../model/yolov5s-sim_320.{json,data,quantize}` | — | ✅ 齐全 (已登记 §1.2) |
| 校准集 | `~/Public/radxa_yolo/calib_yolov5_100/` | 100 张 | ✅ |
| **Art.Galaxy** | — | — | ❌ **不存在 [0数据]** |

### 2.3 ★ A733 已跑通的 5 步流程 (路线 A, 可复现 → ARS45 的模板)

```
ONNX (静态 shape)
   │ P1  import      : onnxsim 静态化 → 抽 3 路 Detect head → pegasus_import → config_yml 写 mean/scale
   ▼  *.json + *.data + *_inputmeta.yml + *_postprocess_file.yml
   │ P2  quantize    : pegasus_quantize.sh <model> <pcq|uint8|int16|bf16>  →  *.quantize
   ▼
   │ P3  export nbg  : gen_nbg (VivanteIDE cmdtools)  →  network_binary.nb      ★ 本机脚本缺失
   ▼
   │ P4  核对        : NBG 头 (magic/format/chip) + 算子覆盖表 + 输入 shape    ★ 本机脚本缺失
   ▼
   │ P5  deploy      : scp → /etc/npu/.../model.nb → 重启 service → 60 s 稳态 fps/tensor_to_fp 打点
   ▼
板端 awnn_create → vip_run_network (纯 NPU) → awnn_run total (SDK 总) → tensor_to_fp (反量化)
```

**P1 (import) 关键动作** — `~/Public/radxa_yolo/acuity_pipeline/p1_import.sh`:
1. `onnxsim` 把动态 shape 收敛成静态 (A733 用 `1,3,640,640`) —— **转换工具要求静态 shape**
2. `onnx_extract.py` 抽出 3 路 Detect head 输出 (把后处理从图里摘掉, 留给 C++)
3. `pegasus_import.sh` 生成 `.json` + `.data`
4. `config_yml.py` 注入 `mean/scale` + `preproc_type` + postproc 配置
5. `dataset.txt` = 校准图清单 (A733 用 100 张)

**★ P1 必须加的前置检查 (ARS45 适配时补上)**: 转换前**校验输入 ONNX 的 sha256 == 台账登记值**。§1.4 实测证明同名不同内容的文件至少存在 3 份 —— 拿错文件转换出来的东西**不报错, 板端 shape 不匹配, 框全错但没人知道**。

**P2 (quantize)** — `p2_quantize.sh`:
- 可选量化类型: `uint8` / `int16` / `pcq` / `bf16`
- ★ **A733 最终选 `pcq` (per-channel symmetric affine)** —— 这才是**真正的 INT8**; `uint8` 是逐 tensor 非对称
- 产物 `*.quantize` 是纯 YAML, 记录每层 `qtype / quantizer / rounding / scale / zero_point / max_value / min_value` → **这份文件就是量化资产** (R-7)

**P5 (deploy) 关键动作**: 备份板端旧 .nb → scp 新 .nb → 杀旧进程 → 启动 → **抓 60 s 稳态 fps 与 `tensor_to_fp` 打点** (A733 这套打点方法 = tracker §7 点名的"最值钱的可复用资产")。

### 2.4 量化参数 / 校准集要求

| 项 | 要求 | 依据 |
|---|---|---|
| 校准集张数 | **≥ 100 张** | A733 实测: 只有 6 张时量化质量不够, 补到 100 张 (`calib_yolov5_100`) [实测·历史] |
| 校准集来源 | 与部署场景分布一致 (眼镜场景 = 第一人称、宽 FoV、近距离、大逆光) | [推算] —— ⚠️ 当前 100 张是 **COCO val** 通用集, **与眼镜场景分布不符** → 需自建眼镜场景校准集 (≥100 张), 列入 §6 待办 |
| 校准集来源必须登记 | 路径 + 张数 + sha256[:16] 进台账 (R-7) | §1.2 已有 A733 版 |
| 量化方案 | `pcq` (逐通道对称) | §2.3 P2 [实测·历史] |
| 舍入 | `rtne` (round-to-nearest-even) | `.quantize` 文件 `rounding: rtne` [实测] |
| 量化范围 | 见 `max_value` / `min_value`; 逐层不同 | `.quantize` 实测 (例: `@attach_350/out0_0` scale=0.08542, zero_point=64) |

### 2.5 ★ NBG 头三件套铁律 (踩过两次, 写进规范)

```
offset 0  : 4 bytes  magic = "VPMN"
offset 4  : uint16   version
offset 6  : uint16   format version   (1 = VIPLite 2.0.3.2 ABI / 2 = 2.0.10.x ABI)
offset 8  : uint32   target chip ID    (小端)
```

| 铁律 | 内容 | 依据 |
|---|---|---|
| **NBG-1** | ★ **chip ID 必须等于目标 NPU 的真实 chip ID** (A733 = `0x1000003B`)。传 `--optimize v3` 或 `--optimize a733` 会输出 `0x10000020` → 板端加载后报 **SRAM size 错**, 白干几小时 | A733 实测 [实测·历史] |
| **NBG-2** | 正确 flag 是**完整 chip ID**: `--optimize VIP9000NANODI_PID0X1000003B`; 不能用 SoC 名 | 同上 |
| **NBG-3** | **不要手 hexedit chip ID**: 改了头, NBG 内部 SRAM 配置仍按旧 chip 生成 → 不一致照样炸 | 同上 |
| **NBG-4** | chip ID 错了**不要怀疑 format version**: 曾误判 3 天 (真凶是 chip ID 不是 format) | 同上 |
| **NBG-5** | gen_nbg 缺 VXC shader compiler 时, 用 `VIV_VX_ENABLE_SAVE_NETWORK_BINARY=1` + `VIV_VX_SAVE_NETWORK_BINARY_PATH=<path>` 跳过 verify 直接出 .nb | A733 实测 [实测·历史] |
| **NBG-6** | `VSIMULATOR_CONFIG` 必须设成与目标 NPU 匹配的 cfg (A733 = `VIP9000NANODI_PLUS_PID0X1000003B`) | 同上 |

**→ 对 ARS45 的直接含义**: 转换完的板端文件头里会带 ARS45 的 chip ID 与格式版本, **这两个值现在都不知道 [0数据]** → 必须随模型一起登记进台账 (R-3), 并且**每次换模型都要重验** (§4 R-03)。

### 2.6 ★ 板端输出三段口径 (A733 实测, 跨芯片必须统一口径)

| 段 | A733 实测 (INT8 .nb) | 说明 |
|---|---|---|
| `vip_run_network` (纯 NPU) | 26.40 ms (v24 pipeline) | 硬件段 |
| `tensor_to_fp` (INT8→FP32 反量化) | **13.98 ms** (memcpy 10.65 + 2.70 + 0.63) | ★ 软件段, 不是硬件 |
| `awnn_run` total | **47.5 ms** | SDK 总耗时 |
| FPS | **13.19** (基线 FP32 10.4) | 稳态 60 s |

| 结论 | 等级 |
|---|---|
| **纯 NPU 耗时与 SDK 总耗时必须分开报**, 否则跨芯片横评会得出错误结论 | [实测·历史] + tracker §5 铁律 |
| ★ 若 ARS45 强制 FP32 输出 → 端到端多 ~7.3 ms, 框龄 age 跨台阶 (16.67 ms 一档) → **直接击穿端到端预算** | [推算] (tracker §5 已算过) |
| → **Q8/Q9 必须问清"输出能否直通量化整数"** | 见 §6 |

### 2.7 算子覆盖表 (转换后必交, 模板)

> **要求**: 每次转换交一张表, 列出 ONNX 里出现的**每一个算子**与工具链的覆盖情况。**任一算子未覆盖 = 该模型不可用** (必须改图或换模型), 不许"转换成功"就算过。

| 算子 | 出现次数 (MOD-YOLOV5S-320-INT8) | Art.Galaxy 覆盖 | 备注 |
|---|---|---|---|
| Conv | 60 | ⬜ 待确认 | 主算子 |
| Mul | 69 | ⬜ | |
| Sigmoid | 60 | ⬜ | ★ 与 obj head 相关 (§3.6) |
| Concat | 17 | ⬜ | |
| Add | 10 | ⬜ | |
| Slice | 9 | ⬜ | |
| Reshape | 6 | ⬜ | |
| MaxPool | 3 | ⬜ | |
| Transpose | 3 | ⬜ | |
| Sub | 3 | ⬜ | |
| Pow | 3 | ⬜ | |
| Resize | 2 | ⬜ | ★ 前后处理可能落在图里 → 直接影响框坐标映射 |

**[实测]** 上表算子统计来自 `model_asset_check.py` 的 onnx 解析 (`yolov5s-sim_320_clean.onnx`: 245 节点 / 12 类算子)。
⚠️ 备选 `yolov8s.onnx` 多了 5 类算子: `Softmax / Gather / Div / Shape / Split / Constant` (17 类) → **工具链覆盖难度更高**, 选模型时要把算子覆盖当成一条评分项。

### 2.8 转换流程的验收判据 (M4 验收, 摘自 SW_REQUIREMENTS §5)

| 验收标准 | 判据 | 本单状态 |
|---|---|---|
| M4-R1 ONNX → 板端格式转换成功 | 转换不报错 + 板端能加载并跑出结果 | ⚠️ ARS45 侧 0 数据 (无工具链) |
| M4-R5 转换脚本可复现 | **一条命令**从登记的 ONNX (sha256 锁定) 复现出板端模型 | ✅ 路线 A 脚本在位 (§2.3); 路线 B 待写 |
| M4-R6 模型文件大小与加载耗时 | 记录体积 + **冷启动加载耗时** (影响开机时间) | ⚠️ 0 数据 |
| **新增 (本单)** | 转换产物登记进 §1.2 台账 + 板端文件头字段登记 | ✅ 模板已定义 (§1.2 R-3) |

### 2.9 ★ ARS45 转换流程骨架 (路线 B, 全部标 [0数据])

> **诚实声明**: 以下每一步都是**待填的骨架**, 不是"已跑通"。ARS45 侧目前 **0 次转换、0 个板端产物、0 ms 耗时**。

| 步 | 动作 | 待原厂回答才能定 | 状态 |
|---|---|---|---|
| B0 | 取 Art.Galaxy 工具链 + 文档 (Q11) | 提供形式 (docker? SDK? NDA?) | ⬜ [0数据] |
| B1 | 确认输入格式 (ONNX? 自己的 pb?) + 支持的 opset | Q9 | ⬜ [0数据] |
| B2 | 静态化 ONNX (固定 shape = 板端 OD 输入尺寸) | 板端输入尺寸 (候选 640×480 上采样?) | ⬜ 待 §6 定 |
| B3 | 摘掉 Detect 后处理 (留 3 路 head) → 走 C++ decode | 与 `SW/SW_REQUIREMENTS.md` M5 decode 方案一致 | ⬜ 待 B1 |
| B4 | 量化 (方案名/校准接口/张数要求) | Q9 | ⬜ [0数据] |
| B5 | 导出板端格式 + 记录头部字段 (格式版本 + chip ID) | 头字段布局是否同 NBG | ⬜ [0数据] |
| B6 | 算子覆盖表核对 (§2.7) | Q9 | ⬜ [0数据] |
| B7 | 板端加载 + 首帧输出 shape 与 PC 端对齐 | — | ⬜ 无板 |
| B8 | 纯 NPU 耗时 vs SDK 总耗时 打点 (口径写死) | Q8 | ⬜ 无板 |
| B9 | 登记进台账 (§1.2) + 跑 §3 精度评估 + §4 回归 | — | ⬜ 无板 |

> ★ **ISS-087 (2026-10-28) 已把上表的"全部 [0数据]"改成逐条机器判定** → 详见 **`SW/ARS45_INT8_CHAIN.md`**:
> READY 4 / PARTIAL 3 / BLOCKED 5 (共 9 步), 每步带阻塞原因与解锁条件; 驱动器 `SW/tools/int8_chain.py`。

### 2.10 追加到 Q9 的 10 条 (模型转换专项, 走项目总工转原厂)

| # | 问题 | 为什么问 (依据) |
|---|---|---|
| 1 | Art.Galaxy 的输入格式支持哪些 (ONNX 版本/opset 范围)? | B1/B2 [0数据] |
| 2 | yolov5s 的 12 类算子 (Conv/Sigmoid/Mul/Concat/Slice/Resize/Pow/Sub/...) 哪些覆盖? 哪些不支持要改图? | §2.7 算子覆盖表 |
| 3 | 支持哪些量化方案 (逐通道对称 / 逐 tensor 非对称 / int16 / bf16)? **输出能否直通量化整数而不强制 FP32?** | §2.3 P2 + §2.6 (反量化占 25%) |
| 4 | 校准集最少张数与推荐分布? 支持逐层校准吗? | §2.4 |
| 5 | 板端模型文件头的字段布局 (有无 chip ID / 格式版本)? **ARS45 的 chip ID 是多少?** | §2.5 NBG-1 (★ 决定转换能否上板) |
| 6 | Art.Galaxy 是否与 VeriSilicon ACUITY/VIPLite 同源? **若同源, 能否复用 A733 的 p1/p2 脚本?** | §2.1 假设 H1 (直接决定 §2.3 复用率) |
| 7 | 官方是否提供**预编译的 yolov5 板端模型**? 其许可与类别映射是否正确? | §1.5 替代路线 (A733 官方 .nb 实测类别映射错) |
| 8 | 转换产物的大小上限? (板端槽位 15 MiB) | §1.6 |
| 9 | 冷启动加载耗时 (影响开机时间) | M4-R6 |
| 10 | 工具链在什么平台跑 (Linux x86? Windows? 需不需要 NDA/授权)? | B0 采购/排期 |

---

## 3. 量化精度损失评估方法 (验收③)

### 3.1 为什么必须有这一步 (不是为了"好看", 是因为真的会坏)

| 教训 | 现象 | 等级 |
|---|---|---|
| **A7S: obj head 被压扁** | yolov5 INT8 后 obj 的 sigmoid **最大值只有 0.46** → 量化把 obj head 压扁 → `obj × cls_prob` 乘积卡阈值 → **系统性漏检**。A7S 的解法是给 cylindrical 类单独走 `cls_prob` 路径 + 0.40 阈值 —— 但那是**场景定制**, 本项目做 80 类通用模型 **不搬** | [实测·历史] |
| **A733: 官方 .nb 类别映射错** | 官方 `yolov5s_rt_uint8_a733.nb` 可加载、但**类别映射错 → 422 false positive** → "官方资产"也要跑回归 | [实测·历史] |
| **A733: 框位置不准 ≠ 代码 bug** | 训练数据 200 张连续帧的 person 框都标在同一位置 → 模型学到"人永远在正中" → **模型质量问题, 不是解码 bug** | [实测·历史] |
| **结论** | 量化后**必须做逐类阈值回归**, 不许直接沿用 FP32 的 0.55/0.60 | [实测·历史] + `SW/SW_REQUIREMENTS.md` §5 M4 |

### 3.2 L0~L4 五层评估金字塔

| 层 | 名称 | 回答什么问题 | 判据 | 数据来源 |
|---|---|---|---|---|
| **L0** | 文件/头级 | 刷进板子的到底是不是这版? 格式对不对? | sha256 一致 / 头字段正确 / ≤15 MiB | §1 台账 + `model_asset_check.py` |
| **L1** | 量化参数级 | 量化器本身健不健康? | §3.3 三指标 | `.quantize` 文件解析 |
| **L2** | 张量数值级 | 每一层输出偏了多少? | 逐层余弦相似度 / 相对误差 / 直方图 | PC 端 reference 模型逐层对比 |
| **L3** | 业务级 | 检测还准吗? 阈值要不要重调? | mAP 差值 + 逐类阈值回归 + 框 IoU 匹配率 | COCO val2017 5000 张 (本地已有) |
| **L4** | 系统级 | 上板后还跑得动吗? | 纯 NPU / SDK 总 / fps / 内存 | 板端打点 (无板 → [0数据]) |

### 3.3 L1 量化器健康度 (3 个指标, 全部可离线算)

| 指标 | 怎么算 | 判据 | 说明 |
|---|---|---|---|
| **饱和率 (clipping ratio)** | 对每层权重与激活, 统计落在量化区间外的样本占比 | 权重 **< 0.1%**; 激活 **< 1%** | ★ 饱和高 = 量化把值截断了 → 精度掉得快。**这是 INT8 最常见的失效模式** |
| **零分布健康度** | 看 `zero_point` 是否贴近分布中位; per-channel scale 的离散度 | `zero_point` 落在 `[min,max]` 中段; 同层各通道 scale 极差 **< 10×** | 极差过大 = 通道间尺度失衡 → per-channel 也救不了 |
| **敏感层标记** | 取 L2 里相对误差最大的 top-10 层 | 列出清单, 单独看这些层 | 典型敏感层: 第一个 Conv / 最后一层 obj head / 小分辨率层的 skip 拼接 |

**判据来源**: 阈值取自通用量化实践 [推算]; **A733 的 `.quantize` 实测值可作对照基线** (例: `@attach_350/out0_0` scale=0.08542, zero_point=64, max=5.411, min=-16.371) [实测]。

### 3.4 L2 张量数值级对比 (逐层)

对每一层输出张量 `T_ref` (FP32 reference) 与 `T_q` (INT8 反量化后):

| 指标 | 定义 | 判据 |
|---|---|---|
| 余弦相似度 | `cos(T_ref, T_q)` | **≥ 0.999** |
| 相对 L2 误差 | `‖T_ref − T_q‖₂ / ‖T_ref‖₂` | **≤ 1%** (敏感层 ≤ 3%) |
| 直方图 KL 散度 | 32 桶归一化直方图的 KL | **≤ 0.01** (敏感层 ≤ 0.05) |
| 符号一致性 | 符号相同的元素占比 | **≥ 99.5%** |

⚠️ **口径纪律**: 对比必须在**同一批输入**上做 (同一批 5000 张 COCO val 或固定 200 张回归集), 且**必须用板端实际的量化参数** (即 `.quantize` 里的 scale/zero_point), 不能用 PC 端随手 re-quantize 的结果代替 —— 否则测的不是板上的东西。

### 3.5 L3 业务级 (最重要的一层)

| 指标 | 怎么算 | 判据 | 备注 |
|---|---|---|---|
| **mAP@0.5 差值** | FP32 vs INT8, 同一 COCO val2017 5000 张, 同一 NMS 参数 | **Δ ≤ 0.02** (绝对) | 通用模型的门限 |
| **mAP@0.5:0.95 差值** | 同上 | **Δ ≤ 0.03** | 更严, 反映框质量 |
| **逐类 AP 差值** | 80 类逐类算 Δ | **任何一类 Δ > 0.10 → 判不通过** | ★ 总体 mAP 会把个别类崩掉掩盖掉 |
| **框集合匹配率** | 同一张图, INT8 框 vs FP32 框, 按 IoU≥0.5 匹配 | **≥ 95%** | 直接对应"框会不会跳" |
| **obj head 最大值分布** | 统计 N 张图上 obj sigmoid 的最大值分布 | **P50 ≥ 0.9, P1 ≥ 0.5** | ★ 直接盯 A7S 那个失效模式 (INT8 后 max 只有 0.46) |
| **逐类阈值回归** | 80 类逐类扫阈值 (0.20~0.80 步进 0.05), 找每类最优阈值 | 每类给出**建议阈值 + 该阈值下的 mAP** | ★ **不许沿用 FP32 的 0.55/0.60**; 走通用逐类回归, **不抄 A7S 的 cylindrical 特殊路径** |

**评测集与工具 (本机已有 [实测])**:

| 资源 | 路径 | 规模 |
|---|---|---|
| COCO val2017 图像 | `/work/object_detection/data/coco/raw/val2017/` | **5000 张** |
| COCO 标注 | `/work/object_detection/data/coco/raw/annotations/instances_val2017.json` | 标准 instances |
| 评测脚本 | `/work/object_detection/evaluate_odapi.py` / `evaluate_pycocotools.py` | 已有 (TF OD API 口径) |

⚠️ **口径提醒**: 现有 `evaluate_odapi.py` 是 **TF OD API** 的评估器, 我们要评的是 **yolov5/yolov8 的 ONNX** → 需要一个 ONNX 版评估器 (onnxruntime 跑 FP32 reference + 解析 3 路 head + 复用现有 decode/NMS)。**这是一个明确的后续开发项** (§6 T-3), 不是"跑一下就有数"。

### 3.6 ★ obj head 专项 (A7S 失效模式的定点检查)

| 检查 | 方法 | 判据 |
|---|---|---|
| obj head 动态范围 | 取 3 路 head 里 obj 那一列, 统计 FP32 下的 max/min | FP32 max ≥ 0.95 (否则参考模型本身就不行, 不是量化问题) |
| INT8 后是否被压扁 | 同上, 用板端量化参数反量化 | **max ≥ 0.85**; 若 < 0.6 → **判不通过** (A7S 的 0.46 就是这个数) |
| 乘积是否还能过阈 | 统计 `obj × cls_prob` 的分布与过阈比例 | 过阈比例与 FP32 差 **≤ 2 个百分点** |
| 补救路径 (只准走通用路) | ① 换 per-channel 量化 ② 提高该层校准精度 ③ 逐类阈值回归 | ⚠️ **不许**用 A7S 的"特定类走 cls_prob 路径" (与 80 类通用模型定位冲突, `SW/SW_REQUIREMENTS.md` §13.3 已定) |

### 3.7 L4 板端系统级 (无板 → 全部 [0数据])

| 项 | 判据 | 现状 |
|---|---|---|
| 纯 NPU 耗时 (`vip_run_network` 等价打点) | 记录 min/avg/max + 采样帧数 | ⬜ [0数据] |
| SDK 总耗时 | 同上; **必须与纯 NPU 分开报** | ⬜ [0数据] |
| 反量化段耗时 | 是否存在; 若存在占多少 % | ⬜ [0数据] (A733 参考: 13.98/47.5 = **29%**) |
| 稳态 fps | 60 s 稳态均值 | ⬜ [0数据] (A733 参考: 13.19) |
| 端到端框龄 age | `ceil(T_od / P)`, P = 显示帧周期 | ⬜ [0数据]; **台阶效应**: 纯 NPU 跨过 16.67 ms → age 2→3 → 端到端 +16.67 ms |
| 内存 | 模型加载后的常驻增量 | ⬜ [0数据] |
| 冷启动加载耗时 | M4-R6 | ⬜ [0数据] |

### 3.8 量化放行判据 (汇总表)

> **全部通过**才允许把该模型登记为 `state=active` 并刷板。任一 ❌ → 该模型 `state=quarantined`, 并在台账 `note` 写明失败项与实测值。

| # | 判据 | 门限 | 层级 |
|---|---|---|---|
| Q-1 | sha256 与台账一致 + 板端文件头字段已登记 | 完全一致 | L0 |
| Q-2 | 板端产物 ≤ 15 MiB | ≤ 15,728,640 B | L0 |
| Q-3 | 饱和率 | 权重 < 0.1%, 激活 < 1% | L1 |
| Q-4 | 逐层余弦相似度 / 相对 L2 误差 | ≥ 0.999 / ≤ 1% | L2 |
| Q-5 | mAP@0.5 与 @0.5:0.95 差值 | Δ ≤ 0.02 / Δ ≤ 0.03 | L3 |
| Q-6 | 逐类 AP 差值 | 任一类 Δ > 0.10 → 不通过 | L3 |
| Q-7 | obj head INT8 后最大值 | ≥ 0.85 (FP32 ≥ 0.95) | L3 |
| Q-8 | 逐类阈值回归已完成并落表 | 80 类全覆盖 | L3 |
| Q-9 | 纯 NPU 耗时与 SDK 总耗时分别记录 (min/avg/max + 帧数) | 有数即可 | L4 |
| Q-10 | 许可状态 | 无 L1/L4 阻断项 | §1.5 |

---

## 4. 模型更新后的回归验证要求 (验收④)

### 4.1 触发条件 (以下任一变化 → **必须**跑全量回归)

| # | 触发 | 为什么 |
|---|---|---|
| T1 | 换权重 (新训练 / 新导出 ONNX) | 检测能力变了 |
| T2 | **换量化参数 / 换校准集 / 换量化方案** | ★ 换量化参数 = 换模型 (R-7) |
| T3 | 换输入分辨率或输入布局 (NCHW↔NHWC) | ★ A733 实测踩过: 按 NCHW 读 → max_person 全 0 |
| T4 | 换板端格式版本 / 换工具链版本 / 换 chip ID | ★ A733 实测踩过: format/chip 不匹配 → 加载失败或 SRAM 错 |
| T5 | 换输出解码方式 (3 路 head ↔ 单 output0) | 输出布局变了, 索引公式要重写 |
| T6 | 换类别集合 (80 类 ↔ 子集) | 阈值表与类别映射全部作废 |
| T7 | 换 NPU runtime / SDK 版本 | 量化输出与反量化行为可能变 |
| T8 | 只改阈值 / NMS 参数 | 也要跑 L3 (属于回归的一部分) |

### 4.2 ★ 回归用例矩阵 R-01~R-14

| # | 回归项 | 判据 | 工具 / 怎么判 | 失败怎么办 |
|---|---|---|---|---|
| **R-01** | 台账一致性 | sha256 / 大小 / 路径 / 许可 / 状态 全部与台账一致; 无重复 ID | `python3 SW/tools/model_asset_check.py` → rc=0 | 台账错 → 改台账; 实物错 → 重新入库 |
| **R-02** | 放行阻断项 | L 计数 = **0** | 同上 (输出末尾"量产放行阻断项 (L)") | L1 → 补许可; L4 → 走商业许可采购 |
| **R-03** | 板端文件头 | magic / format / **chip ID** 与目标 NPU 一致 | `model_asset_check.py` C5~C7 | chip 错 → **不许刷板**, 回 §2.5 重新导出 |
| **R-04** | 容量 | 板端产物 ≤ 15 MiB | 同上 C4 | 超 → 换小模型 / 缩输入 (会动端到端预算, 需重算) |
| **R-05** | 加载 | 板端 `awnn_create` 成功, 输出 tensor 的 **shape 与 PC 端一致** | 板端加载日志 | shape 不一致 → **T3/T5 变了, 索引公式要重写** |
| **R-06** | 数值一致性 | 同一批图, 板端输出 vs PC 端 ONNX 输出: 逐层余弦 ≥ 0.999 / 相对 L2 ≤ 1% | §3.4 | 不达标 → 回 §3.3 查饱和率 |
| **R-07** | 量化器健康度 | 饱和率 / 零分布 / 敏感层清单 达标 | §3.3 | 不达标 → 换校准集 / 换量化方案 |
| **R-08** | 精度 (总体) | mAP@0.5 Δ ≤ 0.02; mAP@0.5:0.95 Δ ≤ 0.03 | §3.5 (COCO val 5000 张) | 超 → 回 §3.6 查 obj head |
| **R-09** | 精度 (逐类) | 80 类逐类 Δ; 任一类 Δ > 0.10 → 不通过 | §3.5 | 不通过 → 该类单独处理 (换数据/换阈值), 不许整体放行 |
| **R-10** | 阈值回归 | 逐类建议阈值表已更新并落盘; **obj head INT8 后 max ≥ 0.85** | §3.6 | 不过 → 走通用补救 (per-channel / 校准 / 逐类阈值), **不抄 A7S 场景定制** |
| **R-11** | 性能 | 纯 NPU 耗时 + SDK 总耗时分别记录 (min/avg/max + 帧数); 稳态 fps | 板端打点 (v31/A7S 方法论复用) | 超预算 → 回 §5 收敛路径 (yolov5n / 512 / INT8 直通) |
| **R-12** | 端到端 | 框龄 age 重算; 端到端仍 < 60 ms (按 Q1 口径) | `SW/SW_REQUIREMENTS.md` §3 预算表 | 跨台阶 → 降 OD 帧率或换模型 (需老板拍板) |
| **R-13** | 版本串绑定 | 板端 `model=` 版本串 = `yolov5s-int8-ag2-<sha8>`, 且 `<sha8>` == 板端模型文件 sha256 前 8 位; 6 分项齐全 | `SW/FLASH_AND_VERSION.md` §2.5.1 F4 / `E_MODEL_MISMATCH` | 不一致 → `E_MODEL_MISMATCH`, 刷写流程要拦下 |
| **R-14** | 刷写与回滚 | 模型走 **app/model A/B 双槽** (§4.1 推荐 C); 断电注入后能回滚到旧槽 | `SW/FLASH_AND_VERSION.md` §4.5 / `SW/tools/flash_writer.py` | 回滚失败 → 停止刷写, 查 §4.5 |

### 4.3 ★ 版本串与 sha 的绑定关系 (防"刷错模型")

```
/etc/version 里的 model= 字段   =  yolov5s-int8-ag2-<sha8>
                                          │              │
                                          │              └ = 板端 model 文件 sha256 的前 8 位
                                          └ = 板端模型格式版本 (Art.Galaxy 格式版本, 必填, 不能省)

校验规则 (FLASH_AND_VERSION §2.5.1 F4):
  ① model= 字段非空                 → 否则 E_VER_INCOMPLETE
  ② <sha8> == 板端模型文件 sha256[:8] → 否则 E_MODEL_MISMATCH
  ③ boot/kern/rootfs/app/model/isp 6 个字段全部非空
```

> ★ **`<fmtver>` (这里是 `ag2`) 是必填项**: 依据 A7S 教训 —— 板端模型格式版本变了但文件名/版本串没变 → 加载的是旧格式, 行为无法区分。**格式版本进版本串, 是 A733/A7S 踩坑换来的**。

### 4.4 无板阶段的回归 (现在能做 / 现在不能做)

| 能做 (现在) | 不能做 (等板) |
|---|---|
| R-01 / R-02 台账与许可 | R-03 板端文件头校验 (无板端产物) |
| R-04 容量 (PC 侧估算) | R-05 加载与 shape 对齐 |
| **L0/L1/L2 离线量化评估** (有 ONNX + 量化参数即可) | R-06 板端 vs PC 端数值一致性 |
| **L3 离线精度评估** (COCO val 5000 张本地已有) | R-11 / R-12 性能与端到端 |
| R-13 版本串格式检查 (离线生成 + 校验) | R-14 刷写与回滚 |
| — | **板端实测 0 次** |

### 4.5 回归不通过时的决策树

```
回归不过
 ├─ R-01/R-02 (台账/许可)  → 不是模型问题: 补台账 / 补许可 → 不许刷板
 ├─ R-03 (chip ID / 格式)  → 回 §2.5 重导 (别手 hexedit)
 ├─ R-06/R-07 (数值/饱和率) → 换校准集 / 换量化方案 (pcq ↔ per-channel) / 缩输入
 ├─ R-08/R-09 (精度)       → ① 查 obj head (§3.6) ② 逐类阈值回归 ③ 换回 FP32? (★ 不行: 端到端预算不够, 需算)
 ├─ R-10 (阈值)            → 走通用逐类阈值表 (不许抄 A7S 场景定制)
 └─ R-11/R-12 (性能/端到端) → 回 §5 收敛路径: ① INT8 直通 ② yolov5n ③ 512 输入 ④ 降 OD 帧率 (需 Q2 拍板)
```

### 4.6 变更记录模板 (每次模型更新留档)

```markdown
### 模型变更 MC-<YYYYMMDD>-<NN>
- 日期 / 执行人:
- 变更类型: T1 权重 / T2 量化参数 / T3 输入尺寸 / T4 格式版本 / T5 解码 / T6 类别 / T7 runtime / T8 阈值
- 旧: <旧资产 ID>  sha256[:16]=<....>  版本串 model=yolov5s-int8-ag2-<sha8>
- 新: <新资产 ID>  sha256[:16]=<....>  版本串 model=yolov5s-int8-ag2-<sha8>
- 触发原因:
- 回归结果: R-01 ✓ / R-02 ✓ / R-03 ... R-14 ...   (逐条写 通过/不通过/未验 + 数值)
- 量化评估: mAP@0.5 Δ=<..>  mAP@0.5:0.95 Δ=<..>  逐类最大 Δ=<..>  obj head max=<..>
- 性能: 纯 NPU <min/avg/max ms, n帧>  SDK 总 <...>  fps=<..>
- 放行判定: L=<n>  → 通过 / 不通过 (原因)
- 复现命令: <一条命令>
```

### 4.7 回归用例与 SW 既有文档的对应 (不重复造轮子)

| 本单 | 对应既有文档 | 关系 |
|---|---|---|
| R-01/R-02/R-13 | `SW/FLASH_AND_VERSION.md` §2.5.1 (版本块 5 条校验) / §3.2 | 复用校验规则 |
| R-03/R-04 | `SW/FLASH_AND_VERSION.md` §4.1 (分区表) | 复用 15 MiB 槽位 |
| R-05/R-11 | `SW/SW_REQUIREMENTS.md` §6.1 (线程模型, A7S 架构 A) / §6 打点方法 | 复用打点方法 |
| R-06~R-10 | `SW/SW_REQUIREMENTS.md` §5 (M4 模型转换) | 扩展 M4 验收 |
| R-14 | `SW/FLASH_AND_VERSION.md` §4.5 (S2 救砖) + `SW/tools/flash_writer.py` | 复用刷写/回滚工具 |
| 端到端预算 | `SW/SW_REQUIREMENTS.md` §3 (预算表) / `PROJECT_TRACKER.md` §3 | **不改** 端到端口径 |

---

## 5. 本单 0 数据清单 (明确标出来, 不装作有数)

| # | 0 数据项 | 为什么拿不到 | 谁来解 | 期望时限 |
|---|---|---|---|---|
| Z1 | ARS45 板端 INT8 模型 | 无板 + 无 Art.Galaxy | 项目总工 → 原厂 (Q9/Q11) | 与原厂资料同期 |
| Z2 | Art.Galaxy 工具链 | 原厂未提供 | 项目总工 → 原厂 | 同上 |
| Z3 | ARS45 的 chip ID / 模型文件头布局 | 无板无资料 | 项目总工 → 原厂 (Q9 追加第 5 条) | 同上 |
| Z4 | yolov5s INT8 在 ARS45 上的纯 NPU 耗时 / SDK 总耗时 | 原厂从没公开跑过 YOLO | 项目总工 → 原厂 (Q8) + 投板实测 | 投板后 |
| Z5 | yolov5s-sim 系 ONNX 的许可 | 本机无 LICENSE 文件, onnx 无 metadata | 项目总工 → 来源方/原厂 | **量产评审前 (阻断 L1)** |
| Z6 | Art.Galaxy 是否与 ACUITY 同源 (假设 H1) | 未验证 | 项目总工 → 原厂 (Q9 追加第 6 条) | 与 Q9 同批 |
| Z7 | 眼镜场景校准集 (≥100 张) | 本机只有 COCO 通用集 | sw-lead (可自建, 但需采集) | EVT 前 |
| Z8 | ONNX 口径的 COCO 评估器 (yolov5/yolov8) | 现有 `evaluate_odapi.py` 是 TF OD API 口径 | sw-lead | 板子回来前 |
| Z9 | P3 (export nbg) / P4 (算子核对) 脚本 | 本机缺失 | sw-lead 从 A733 工程找回 | 下周 |
| Z10 | yolov5s-sim 系 ONNX 的来源链路 (谁导出、基于什么权重) | 无来源记录 | sw-lead 查 / 项目总工问 | 下周 |

---

## 6. 未决项与卡点

| # | 未决 | 需要谁回答 | 走谁 | 期望时限 |
|---|---|---|---|---|
| U1 | **Q9 追加 10 条** (工具链 / 算子覆盖 / 量化方案 / 校准 / chip ID / 同源性 / 官方预编译模型 / 体积上限 / 加载耗时 / 平台) | 原厂 | **项目总工** (外发一律经项目总工) | 2026-10-29 |
| U2 | yolov5s-sim 的**来源与许可** (阻断 L1) | 来源方 / 原厂 | **项目总工** | 2026-10-29 (量产评审前) |
| U3 | yolov8s 的 **AGPL-3.0 商业许可**采购 (阻断 L4) | 老板 + 采购 | **项目总工** | 选型拍板时 |
| U4 | **ARS45 OD 输入尺寸** (640×480? 320×320? 512?) | 端到端预算 + ISP 缩放链路共同决定 | 项目总工裁决 (我给约束) | 与 Q1/Q17 同批 |
| U5 | 眼镜场景校准集采集 (≥100 张) | 需样机 + 场景 | sw-lead 自建 | EVT 前 |
| U6 | ONNX 口径 COCO 评估器 | 我自己写 | sw-lead | 板子回来前 |
| U7 | 官方预编译板端模型是否可用 (许可 + 类别映射) | 原厂 | 项目总工 | 与 U1 同批 |

**我的假设 (如果对方不回应, 我会按这个做)**:
- U1/U2/U3 无回应 → **默认按"许可未清 = 不许量产"处理**; 主模型候选保持在 `state=candidate`, 不推进到 `active`。
- U4 无回应 → 默认 **OD 输入 640×480 (与锁定的 ISP 缩放链一致)**, 转换时按 640 静态化; 若板端 NPU 跑不动 → 走 §5 收敛路径 (缩输入 / 换 yolov5n)。
- U7 无回应 → 默认**不使用官方预编译模型**, 一律走自转 + 全量回归。

---

## 7. 自证复现命令 (B6)

```bash
# 一条命令复核本文全部关键数字 (台账 11 条 × 检查项 + 放行阻断项计数)
cd projects/smart_glasses && python3 SW/tools/model_asset_check.py
# 预期 (2026-10-28 实跑): rc=0 · 资产 11 条 · FAIL 0 · 重复组 1 · **量产放行阻断项 L=0**
#       交付集 1 条 (Apache-2.0) | licensing-hold 2 条 (AGPL) | quarantined 4 条 | reference 4 条
#       L1 许可未判定 0 · L2 超槽 0 · L3 chip ID 0 · L4 AGPL 0 (AGPL 资产已禁入交付物) · L5 坏模型 0

# 许可溯源 (ISS-087 新增: 把 [0数据] 变成有物证的判定)
python3 SW/tools/license_probe.py
# 预期: yolov5s-sim 系 3 份 → AGPL-3.0 (证据: 本机文档 + pip 包许可 + checkpoint 命名空间)

# 转换链 readiness (ISS-087 新增: B0~B9 逐条判定)
python3 SW/tools/int8_chain.py
# 预期: READY 4 · PARTIAL 3 · BLOCKED 5 (共 9 步)

# 机读输出 (给 CI / 门禁用)
python3 SW/tools/model_asset_check.py --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['assets']),'assets,',len(d['release_blockers']),'blockers, ship=',d['ship_set'])"

# 单条资产细查
python3 SW/tools/model_asset_check.py --id MOD-YOLOV5S-640-ARS45-SRC

# 新模型入库 (打印台账行骨架 + 头部信息 + 许可判定)
python3 SW/tools/model_asset_check.py --new /path/to/new_model.onnx

# 项目状态门禁 (ISS-037 自证)
cd projects/smart_glasses && python3 state/merge.py && python3 state/gate_check.py
```

**本文关键数字的出处 (逐条可追)**:

| 数字 | 出处 |
|---|---|
| 11 条资产 / sha256 / 大小 | `model_asset_check.py` 输出 (2026-10-28 实跑) |
| 三份 `yolov5s-sim` 输入 320/320/640 | 同上 C7 |
| 许可 AGPL-3.0 (yolov5s 系由 [0数据] 判定而来) | 同上 C5 + `SW/tools/license_probe.py` |
| 320/416 版模型 PC 侧推理失败 (C9) | 同上 C9 (onnxruntime 冒烟) |
| chip ID 0x10000020 vs 0x1000003B | 同上 C7 |
| 算子 12 类 / 245 节点 | onnx 解析 (`n_op_types` / `n_nodes`) |
| 校准集 100 张 | 同上 C4 (目录计数) |
| 15 MiB 槽位 | `SW/tools/s2_rescue_config.example.json` + `SW/FLASH_AND_VERSION.md` §4.1 |
| COCO val 5000 张 + instances json | `ls /work/object_detection/data/coco/raw/` |
| ACUITY 6.30.22 / VivanteIDE 5.11.0 在本机 | `ls /home/yuewuya/miniconda3/envs/acuity` + `~/Public/radxa_yolo/acuity_rootfs` |
| A733 数值 (13.19 fps / 13.98 ms tensor_to_fp / obj 0.46) | A733 工程记忆 + `SW/SW_REQUIREMENTS.md` §5 M4 |

---

*本单只交付: 台账 (含机器复核) + 量化流程 + 精度评估方法 + 回归门禁。*
*★ 不交付: "模型已转换" —— ARS45 板端模型 0 个, 转换 0 次, 板端实测 0 次。*
*端到端预算 / 锁定变量 / 分区表**一字未改**; 本单只新增 `SW/MODEL_ASSETS.md` 与 `SW/tools/model_asset_check.py` 两个文件。*
