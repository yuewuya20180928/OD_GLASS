# SW/MODEL_LICENSE.md — 模型许可判定 · 采购/法务路径 · 成本区间

> **单号**: ISS-087 (sw-lead, 2026-10-28) · 上游单: ISS-037 (模型资产登记与 INT8 量化管理)
> **本文件解决 ISS-087 的第 ① 项**: 模型许可 (原 L1 "许可 [0数据]" + L4 "AGPL 商用受限")
> **唯一真源**: 许可判定结果同步在 `SW/tools/model_asset_check.py` 的 `MANIFEST` (§1.2 台账)
> **证据分级**: [实测] = 本机跑出来的 · [官方] = 上游官方页面/仓库元数据 · [推算] = 推导 · [0数据] = 拿不到
> **边界**: 本单**没有**联系 Ultralytics / 任何供应商; 一切外发经**项目总工**。

---

## 1. 结论: 许可判定 (把 [0数据] 变成有物证的判定)

### 1.1 三条判定 (一句话版)

| 资产 | 原判定 | **新判定** | 依据 | 等级 |
|---|---|---|---|---|
| `yolov5s-sim` 系 3 份 ONNX (320×2 + 640×1) | **[0数据]** (metadata_props 全空) | **AGPL-3.0** | 血缘断到 `github.com/ultralytics/yolov5` (上游仓库 LICENSE = AGPL-3.0) | [实测·本机文档] + [官方] |
| `yolov8s.onnx` (640) | AGPL-3.0 (metadata 原值) | **AGPL-3.0** (不变) | `metadata_props.license` 原值 | [实测] |
| A733 侧派生的 4 条 `.nb` / `.quantize` | 无许可字段 | **AGPL-3.0** (继承上游) | 派生自 yolov8s / yolov5s | [推算] |
| `ssd_mobilenet_v2_fpnlite_320x320` (TF OD API) | 未登记 | **Apache-2.0** | `tensorflow/models` 的 `/research` 子目录 | [官方] |

> ★ **判定口径变更 (重要)**: 从 ISS-087 起, **"许可未判定" 才是阻断项**;
> "`metadata_props` 为空" 只是**取数方式**的问题 —— 两者不再混记。
> 台账新增 `license_state` 字段: `permissive` / `agpl-granted` / `agpl-no-grant` / `unknown`。

### 1.2 证据链 (可一条命令复现)

```
$ python3 SW/tools/license_probe.py
```

**证据链 (yolov5s-sim 系, 从产物倒推到上游):**

| 环 | 物证 | 出处 | 等级 |
|---|---|---|---|
| ① | 文件名 `yolov5s-sim*.onnx` 的 `-sim` = **onnxsim 产物** (A733 pipeline `p1_import.sh` 明写 `python3 -m onnxsim yolov5s.onnx yolov5s-sim.onnx --input-shape 1,3,640,640`) | `~/Public/radxa_yolo/acuity_pipeline/p1_import.sh` | [实测·本机脚本] |
| ② | **上游是谁**: Rockchip 官方 model zoo `examples/yolov5/README.md` 原文: "git clone https://github.com/ultralytics/yolov5.git" + "本文下载模型为 **v6.0 版本的 yolov5s.onnx**" + 紧跟 onnxsim 命令 | `~/Downloads/radxa/awnpu_model_zoo-v0.9.0-20260116-83a67d4b/examples/yolov5/README.md` | [实测·本机文档] |
| ③ | 产物与上游的 **sha 链**: 本机 `yolov5s_rt.onnx` (3 路 head 抽取版) 与 zoo 发布的 `examples/yolov5/convert_model/yolov5s_rt.onnx` **逐字节相同** (sha256 `fe69cda1852c7867…`, 28,930,936 B) | `sha256sum` 双向比对 | [实测] |
| ④ | ONNX **initializer 命名** `model.0.conv.weight` / `model.2.cv1.conv.weight` = Ultralytics YOLOv5 模块路径 (自研实现不可能这么写) | onnx 图解析 | [实测] |
| ⑤ | 同族 checkpoint `~/Public/radxa_yolo/code/yolov5su.pt` 的 pickle 命名空间 = `ultralytics.nn.modules.{Conv,C3,SPPF,Detect}` + 配置路径 `/usr/src/app/ultralytics/models/v5/yolov5s.yaml` (**Ultralytics 官方 Docker 镜像内路径**) | torch zip 内 data.pkl 字符串扫描 | [实测] |
| ⑥ | 本机安装的 `ultralytics 8.4.80` 包 METADATA: `License: AGPL-3.0` + 随包 LICENSE = AGPL-3.0 全文 (34,523 B) | `pip show` / dist-info | [实测] |
| ⑦ | **上游仓库许可**: `api.github.com/repos/ultralytics/yolov5` → `license.spdx_id = AGPL-3.0`; `ultralytics/ultralytics` 同 | GitHub API (2026-10-28 抓取) | [官方] |

**结论**: `yolov5s-sim` 系 = **Ultralytics YOLOv5 v6.0 COCO 预训练权重导出物** → **AGPL-3.0**。
`yolov8s.onnx` 的 `metadata_props` 自带 `license = "AGPL-3.0 License (https://ultralytics.com/license)"`, 由 ⑥⑦ 同源印证。

### 1.3 ★ 顺带查出: 台账里的"主模型候选"是**坏的**

| 资产 | 实测 | 判定 |
|---|---|---|
| `yolov5s-sim_320_clean.onnx` / `_v2.onnx` (台账原"主模型候选", 输入 320) | `onnxruntime` **加载即失败**: `Node (Concat_527) Op (Concat) ShapeInferenceError: Inferred=10 Declared=20` | **已隔离 (quarantined)** |
| `yolov5s-sim_416.onnx` (A733 当年做的 416 变体) | 同类错误 (`Inferred=13 Declared=20`) | 同因同病 (未登记) |
| `yolov5s-sim.onnx` (640, A733 侧) | `onnxruntime @640` **推理 OK**, 输出 `[1,25200,85]` + 3 路 80/40/20 网格 | **唯一可用的 yolov5s ONNX** |

**根因**: 有人只把 ONNX 的**输入 dim** 改成 320/416, 图内 **Reshape/anchor 常量仍是 640 尺度** → 模型内部自相矛盾。
`make_416_onnx.py` 里那行 `if arr.size == 5 and arr[1] == 3 and arr[2] == 85` 匹配到的是 anchor 常量 `[1,3,85,H,W]`, 与真正的网格常量不是同一批 → 实际改写 0 处 (脚本自己打印 "Changes made: 0 (expected 3)")。

**对策 (已落进工具)**: `SW/tools/model_asset_check.py` 新增 **C9 = PC 侧 1 帧推理冒烟** (onnxruntime)。
交付集里的模型 C9 失败 = **新增阻断项 L5**。→ 坏模型不会再被拿去投板。

**正确做法**: 要 320/416 就**从 checkpoint 用正确 `imgsz` 重新导出**, 不要改 ONNX 的输入 dim。
本机可用 checkpoint: `~/Public/radxa_yolo/code/yolov5su.pt` (Ultralytics YOLOv5s, 80 类)。

---

## 2. AGPL-3.0 对本项目的具体约束 (法务口径)

### 2.1 官方原文 (2026-10-28 抓取, `https://www.ultralytics.com/license`)

| 官网分类 | 原文要点 | 我们的场景 |
|---|---|---|
| **需要 Enterprise License** | "Any commercial product or service" · "Proprietary / closed-source software" · "**Embedded deployments in hardware, edge devices, robotics, cameras, or appliances**" · "**Using custom-trained or fine-tuned YOLO models in a proprietary or commercial setting**" | ★ ARS45 = 嵌入式硬件 + 闭源固件 + 商用 → **正中靶心** |
| **AGPL-3.0 可用** | "Open-source applications where you can **publicly release the full source code**" · "Evaluating Ultralytics YOLO in a fully open-source environment" | 我们是闭源量产产品 → **不适用** |
| Enterprise 权益 | 商用 / 私有部署 / 自有修改归属 / 定制条款 / 专属支持 / **需年度付费** | 采购即解除 AGPL 义务 |

### 2.2 AGPL-3.0 对我们意味着什么 (条款映射)

| 条款 | 内容 | 对 ARS45 的后果 |
|---|---|---|
| §6 (分发非源码形式) | 分发二进制必须**同时以 AGPL-3.0 提供完整对应源码** | 眼镜固件 = 闭源产品 → 与 AGPL 分发义务**直接冲突** |
| §13 (网络交互) | 允许用户通过网络与修改版交互 → 必须提供修改版源码 | 我们是**离线设备**, §13 不触发; 真正的约束在 §6 (随硬件分发) |
| "衍生作品"边界 | 固件与权重是"独立作品"还是"单一作品"存在法律争议 | Ultralytics 官方立场 = **自定义训练/微调模型在商用场景也需 Enterprise** → **按最严口径处理** (风险下限) |
| 自训练权重 | 即便用我们的场景数据重训, 官方仍视为受 AGPL 约束 | 不能靠"自己训一遍"绕开 → [官方] 见上表第 3 行 |

> **法务判断 (供公司律师复核, 本单不替法务下结论)**:
> 若不采购, 合规的 AGPL 路线只有一条 —— **把整个眼镜固件 (含训练脚本、配置、权重) 以 AGPL-3.0 开源发布**。
> 与"量产优先 + 闭源 + 竞品可见"的项目定位冲突 → **不采购 = 商用受阻**。
> 采购则把义务换成合同义务 (付钱、受限范围、审计条款) —— **这是采购/法务路径存在的唯一理由**。

---

## 3. 采购 / 法务路径 (三条, 附成本区间与时限)

> ★ 外发一律经**项目总工**; sw-lead 不直接联系 Ultralytics 或任何供应商。

### 路径 1: 采购 Ultralytics Enterprise License (保留 Ultralytics 模型)

| 步骤 | 动作 | 责任 | 交付物 |
|---|---|---|---|
| 1 | 官网 request form 提交询价 (公司主体 / 部署形态 / 机型数 / 地域 / 期限 / 是否含定制训练) | **项目总工**外发 | 询价回执 |
| 2 | 收到报价 → 法务审合同要点: ①**允许的部署形态** (嵌入式硬件/白标/OEM) ②**可部署设备数/机型数** ③**地域与期限** ④**是否覆盖自训练/微调权重** ⑤**衍生模型归属** ⑥**SLA 与审计条款** ⑦**是否与我们的芯片/模组供应商条款冲突** | 法务 + 项目总工 | 合同评审意见 |
| 3 | 老板拍板 → 采购 → 拿到**授权书编号** | 老板 / 采购 | Enterprise License + 授权号 |
| 4 | 授权号登记进台账 (`license_grant` 字段) → `license_state` 改 `agpl-granted` → **L4 自动清零** | sw-lead | 台账更新 + 授权书扫描件 |
| 5 | 合规动作: 固件里标注第三方许可声明 (NOTICE 文件), 保留 Ultralytics 商标使用边界 | sw-lead | `THIRD_PARTY_LICENSES/` |

**成本区间**:

| 项 | 数值 | 等级 | 说明 |
|---|---|---|---|
| Ultralytics 官方公开价 | **无公开价** (官网 Enterprise 全部 "Get a quote") | **[0数据]** | 只有报价制; 官网唯一公开价是**平台订阅** Pro $29/席/月, 且**不含** Enterprise License |
| 授权形态 | 官方定性: "could be a one-time fee or a subscription model, depending on deployment scale, integration level, and support requirements" | **[官方·定性]** | 无金额 |
| **立项预算区间** | 一次性授权 **US$5,000 – 50,000** + 年费 **US$2,000 – 20,000 / 型号 / 部署规模**; 总预算按 **10⁴ – 10⁵ USD 量级**预留; 大型 OEM 报价可上探 10⁵ – 10⁶ USD | **[推算]** | 推导依据: ①同厂平台订阅价目体系 (Pro $29/席/月 [官方]) ②嵌入式 AI SDK/模型商用授权的同类市场量级 ③官网"随规模浮动"定性。**这是为立项用的量级估计, 不是报价** —— 唯一准确数字必须靠 quote |
| 时限 | 询价→合同→到账 **典型 4 – 12 周** [推算] | [推算] | 含法务往返; 合同审查是主要变量 |

### 路径 2: 不采购 → 换许可干净的模型栈 (零许可成本, 工程成本转移)

| 候选 | 许可 | 本机/可获得性 | NPU 转换可行性 | 备注 |
|---|---|---|---|---|
| **YOLOX-s** (80 类 COCO) | **Apache-2.0** [官方, GitHub spdx_id] | 官方 release `yolox_s.onnx` (0.1.1rc0); ★ **本机下载卡在 3.48 MB 停滞** → 需换网络环境 | **[0数据]**; 但 **Rockchip 官方 model zoo 已有 `examples/yolox/` 完整 NPU 转换配方 + 板端 C++** (head 抽取 `['798','824','850']` + import/quantize/export + pre/post cpp) → **同族 NPU 上已被原厂走通** [实测·本机文档] | **首选** (许可干净 + 80 类 + 有现成转换范式) |
| **PP-YOLOE-s / RT-DETR-r** (80 类) | Apache-2.0 [官方] | 需下载 | [0数据] | 备选 |
| **TF OD API SSD-MobileNetV2-FPNLite 320×320** (pipeline.config `num_classes: 90` → COCO 可用 80 类) | **Apache-2.0** [官方] | **本机已有** (`/work/object_detection/pretrained/...`) | [0数据] (TF SavedModel → ONNX → Art.Galaxy **三段都没跑过**) | **已登记为交付集里唯一许可干净的候选** (MOD-SSDMBV2-FPNLITE-320-COCO90-TFODAPI) —— 但它只是"许可路径的起点", **不是**承诺的主模型 |
| **自训 (permissive 框架)** | 取决于框架 | 需 COCO + 算力 | [0数据] | 训练成本 (算力+标注) 通常高于一次性授权费 |
| 原厂 (酷芯微) model zoo 预编译模型 | 由原厂承担 | 取决于原厂是否提供 | [0数据] | ★ 若原厂能提供**许可由原厂负责**的官方模型, 这是最省事的路线 → **已列入 U1 追加问题** |

**成本**: 许可成本 **US$0**; 工程成本 = 重导出 + 重新走 B0~B9 + 重新跑精度评估/回归 (人日估算 **3–8 人日**, 不含 NPU 侧调试) [推算]。
**风险**: Art.Galaxy 对 YOLOX 系算子 (exp_/grid/anchor 计算类) 的支持 = **[0数据]** —— 若不支持, 需退到 "NPU 上只跑 3 路 head + 板端 CPU decode" 的做法 (与 A733 yolov5 路线同构), 该路线**已有 A733 实测先例**。

### 路径 3: 不采购 + 不换栈 → **不进量产评审** (兜底结论)

- 结论写死: **任何以 Ultralytics 权重 (yolov5s / yolov8s 系) 构成的交付物, 在未取得 Enterprise 授权前不得对外销售**。
- 当前台账里 2 条 AGPL 资产已置 `licensing-hold` (禁入交付物), 一旦 boss 拍板采购, 改 `license_grant` 即可复活。

### 3.1 三条路径对比 (给老板/项目总工拍板用)

| | 路径 1 采购 | 路径 2 换栈 | 路径 3 不动 |
|---|---|---|---|
| 许可成本 | 10⁴–10⁵ USD [推算] | 0 | 0 (但**违约风险**) |
| 周期 | 4–12 周 [推算] | 3–8 人日 + NPU 验证周期 | — |
| 主模型成熟度 (A733 复用度) | **高** (现成 yolov5s 链, A733 实测) | 中 (YOLOX 有现成配方, 但未在 ARS45 验证) | 高 |
| 商用合规 | ✅ 合同义务 | ✅ 无义务 | ❌ **AGPL 违约** |
| 板端模型现状 | 0 个 | 0 个 | 0 个 |

> **sw-lead 的建议 (不替老板拍板)**: 路径 2 与路径 1 **并行准备** ——
> 路径 1 的成本只有 quote 才知道, 但**等待期不产生任何工程进展**;
> 路径 2 的第一步 (取 YOLOX-s 权重 + 走 B0~B9) **不依赖任何外部回复**, 板子回来即可跑。
> 采购/不采购的决定请在**投板前**给出, 否则转换链会白跑一轮。

---

## 4. 门禁口径 (ISS-037 §1.5 → ISS-087 修订)

| 阻断项 | 定义 (新) | 判定方式 | 现状 |
|---|---|---|---|
| **L1** | **许可未判定** (台账 `expected_license` 为空) | `license_state == unknown` | **0** ✅ (原: 1 条 [0数据]) |
| **L2** | 板端产物超 15 MiB 槽位 | `.nb` 字节数 | 0 ✅ |
| **L3** | chip ID 与目标 NPU 不符 | NBG 头 byte 8-11 | 0 ✅ (交付集无板端产物) |
| **L4** | **AGPL-3.0 且无 Enterprise 授权记录** → 商用受阻 | `license_state == agpl-no-grant` **且资产在交付集** | **0** ✅ (2 条 AGPL 资产已置 `licensing-hold` 禁入交付物) |
| **L5** | 交付集资产 PC 侧推理冒烟失败 (模型本身坏的) | C9 onnxruntime 1 帧 | 0 ✅ |

**放行判据**: `python3 SW/tools/model_asset_check.py` → **量产放行阻断项 (L) = 0** (2026-10-28 实跑 rc=0)。
**★ 但 L=0 ≠ 可以量产**: 当前交付集里只有 1 条 Apache-2.0 候选且其 NPU 可行性 = [0数据];
**ARS45 板端 INT8 模型仍然是 0 个** (见 `SW/ARS45_INT8_CHAIN.md`)。

---

## 5. 证据分级总表

| 结论 | 等级 | 出处 |
|---|---|---|
| `yolov5s-sim` 系上游 = ultralytics/yolov5 v6.0 release | [实测·本机文档] | Rockchip model zoo `examples/yolov5/README.md` (本机) |
| 本机 `yolov5s_rt.onnx` 与 zoo 发布物逐字节相同 (sha `fe69cda1…`) | [实测] | `sha256sum` |
| ONNX initializer 命名 = Ultralytics 模块路径 | [实测] | onnx 图解析 |
| `yolov5su.pt` pickle 命名空间 = `ultralytics.nn.modules.*` + `/usr/src/app/ultralytics/...` | [实测] | torch zip data.pkl 扫描 |
| 本机 `ultralytics 8.4.80` 包许可 = AGPL-3.0 (随包 LICENSE 全文) | [实测] | dist-info METADATA + licenses/LICENSE |
| `ultralytics/yolov5` / `ultralytics/ultralytics` 仓库许可 = AGPL-3.0 | [官方] | GitHub API spdx_id (2026-10-28) |
| 嵌入式硬件/商用/自训练模型 → 需 Enterprise License | [官方] | ultralytics.com/license (2026-10-28) |
| Enterprise License **无公开价** | [0数据] | 官网 pricing 页全部 "Get a quote" |
| Enterprise 定价 "随规模浮动, 可一次性或订阅" | [官方·定性] | GitHub Discussions #7440 (Ultralytics 员工回复) |
| 采购预算量级 10⁴–10⁵ USD | [推算] | 由上两条 + 同类授权市场量级推导; **非报价** |
| YOLOX = Apache-2.0 | [官方] | GitHub API spdx_id (2026-10-28) |
| `tensorflow/models` 的 `/research` (含 object_detection) = Apache-2.0 | [官方] | 仓库 LICENSE 原文 (2026-10-28 读取) |
| Rockchip model zoo 已有 **YOLOX 的 NPU 完整转换配方** | [实测·本机文档] | `examples/yolox/` (README + convert_model + 板端 cpp) |
| 320/416 版 yolov5s ONNX 加载即失败 | [实测] | onnxruntime 冒烟 (2026-10-28) |
| 640 版 yolov5s ONNX 推理正常 | [实测] | onnxruntime 冒烟 (2026-10-28) |
| Art.Galaxy 对 YOLOX 系算子支持 | [0数据] | 原厂未答 (Q9) |
| Ultralytics Enterprise 真实报价 / 合同条款 | [0数据] | 未询价 (外发经项目总工) |

---

## 6. 未决项 (需要谁回答什么)

| # | 未决 | 需要谁 | 走谁 | 时限 |
|---|---|---|---|---|
| **L-U1** | **拍板: 采购 Enterprise License 还是换 Apache-2.0 栈?** (成本/周期/复用度三选一) | boss | **项目总工** | 投板前 |
| **L-U2** | Enterprise License **报价** (部署设备数/机型/地域/期限/是否含自训练权重) | Ultralytics (报价) | **项目总工** (唯一外发口) | 拍板后立即 |
| **L-U3** | 合同条款要点 (可部署形态 / 设备数 / 衍生模型归属 / SLA / 审计) | 法务 | 项目总工 | 报价到货后 2 周 |
| **L-U4** | 原厂 (酷芯微) 是否提供**许可由原厂承担**的官方预编译 OD 模型? (若提供 → 最省事路径) | 原厂 | **项目总工** (Q9 追加第 7 条) | 2026-10-29 |
| **L-U5** | YOLOX-s 权重在本机网络下载卡在 3.48 MB → 是否走内网镜像/公司代理下载 | boss/IT | 项目总工 | 换栈决定后立即 |
| **L-U6** | AGPL-3.0 义务在本项目的确切边界 (固件+权重是否构成单一作品) | 法务 | 项目总工 | 与 L-U3 同批 |

**我的假设 (若无人回应, 我按这个做)**:
- **L-U1 无回应** → 默认 **不采购** (公司目前无此预算科目, 且采购周期 4–12 周会卡住投板) → 执行**路径 2**: 交付集只放许可干净的模型, AGPL 资产维持 `licensing-hold`。
- **L-U2/L-U3 无回应** → 不影响工程: 路径 2 的准备 (取权重、走 B0~B9) 不依赖报价。
- **L-U4 无回应** → 默认**不使用原厂预编译模型** (A733 官方 .nb 实测类别映射错 → 422 false positive, 官方资产也要跑全量回归)。
- **L-U5 无回应** → 默认用本机已有的 Apache-2.0 TF OD API 候选顶位做转换链演练, 同时登记 YOLOX 为首选 (权重未入库前不进台账, 免得 C1 假失败)。

---

## 7. 自证复现命令 (B6)

```bash
cd projects/smart_glasses

# ① 许可溯源 (把 [0数据] 变成有物证的判定) —— 一条命令复现本文全部证据链
python3 SW/tools/license_probe.py
# 预期: 3 份 yolov5s-sim 判定 = AGPL-3.0 (证据: 本机文档 + pip 包 + checkpoint 命名空间)

# ② 台账 + 放行门禁 (L 计数)
python3 SW/tools/model_asset_check.py
# 预期: 资产 11 条 · FAIL 0 · rc=0 · 量产放行阻断项 (L): 0 条
#        交付集 1 条 | licensing-hold 2 条 | quarantined 4 条 | reference 4 条

# ③ 机读 (给 CI)
python3 SW/tools/model_asset_check.py --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['assets']),'assets,',len(d['release_blockers']),'blockers, ship=',d['ship_set'])"

# ④ 坏模型复现 (C9): 320 版加载即失败
python3 SW/tools/model_asset_check.py --id MOD-YOLOV5S-320-INT8
# 预期: C9 = ★ PC 侧 1 帧推理失败 (ShapeInferenceError) + state=quarantined

# ⑤ 好模型复现: 640 版推理 OK
python3 SW/tools/model_asset_check.py --id MOD-YOLOV5S-640-ARS45-SRC

# ⑥ 官方许可条款 (复核由项目总工决定)
curl -s https://api.github.com/repos/ultralytics/yolov5 | python3 -c "import json,sys; print(json.load(sys.stdin)['license'])"
curl -s https://www.ultralytics.com/license | grep -io "Enterprise License" | head -3

# ⑦ 项目门禁
python3 state/merge.py && python3 state/gate_check.py
```
