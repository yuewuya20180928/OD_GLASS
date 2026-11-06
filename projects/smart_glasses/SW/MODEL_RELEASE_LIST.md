# SW/MODEL_RELEASE_LIST.md — 量产可用模型清单: 当前状态 · 空清单成因 · 补齐路径

> 版本: v1.0 (2026-11-06) · owner: sw-lead · 对应 issue: ISS-101 (清单为空) / ISS-087 (许可门禁)
> 上游: `SW/MODEL_RELEASE_GATE.md` (门禁判据 L=0 的定义) · `SW/MODEL_LICENSE.md` (许可判定) · `SW/MODEL_ASSETS.md` (13 条台账)
>
> ★**本单回答三个问题**: ①**清单现在有几条**? ②**为什么是空的**? ③**怎么补齐, 各要多久, 谁能拍板**?
> ★**纪律**: 拿不到的数据标 `[0数据]`; ★**"放行阻断项 L=0" 不等于 "有可用模型"** —— 这两件事必须分开说。

---

## 0. 一句话结论

**量产可用模型清单 = 0 条。**
★**但本周有实质进展**: 唯一许可干净的候选 (Apache-2.0) ★**本周被证明能进 RKNN 工具链**,
且★**实测抓出并修掉了它唯一的转换阻塞** (float64 输入) ⇒ ★**"许可干净" 与 "NPU 可用" 两个条件,
在本周第一次出现了交集** ⇒ **空清单的成因从"两个条件互斥"降级为"各自还差最后一步"**。

---

## 1. ★ 清单当前状态 (条数 = 0)

### 1.1 三条口径必须分清 (本周被 gate_check 的输出逼出来的)

| 口径 | 含义 | 本周实测值 | 出处 |
|---|---|---|---|
| **L (放行阻断项)** | 台账里"不许进交付物"的硬阻断条数 | **0** | `model_asset_check.py` 实跑 |
| **交付集 (candidate/active)** | 台账里状态不是 quarantined/license-hold 的条数 | **2** | 同上 |
| ★**量产可用清单** | ★**许可干净 + NPU 可转换 + 板端实测通过** 三条同时满足 | ★**0** | 本单口径 |

⇒ ★**L=0 是"没有硬阻断项", 不是"有可用模型"**。台账里那 2 条交付集资产:
① 许可是 Apache-2.0 ✔ ② 但 **NPU 产物未生成 / 板端未实测** ⇒ ★**不构成"量产可用"**。

### 1.2 逐条状态 (13 条资产, 本周 `model_asset_check.py` 实跑)

| 资产 ID | 许可 | 状态 | NPU 就绪 | 板端实测 | 判定 |
|---|---|---|---|---|---|
| `MOD-SSDMBV2-FPNLITE-320-FP32-HEAD-NPU` | **Apache-2.0** ✔ | candidate | ★**本周已生成 .rknn 9.07 MiB** | ❌ 未测 | ★**离量产最近的一条** |
| `MOD-SSDMBV2-FPNLITE-320-COCO90-TFODAPI` | **Apache-2.0** ✔ | candidate | 同上 (同一模型的 SavedModel 源) | ❌ 未测 | 同上 |
| `MOD-SSDMBV2-FPNLITE-320-FP32-FULL` | Apache-2.0 ✔ | reference | 含 NMS, 不可上 NPU | — | 仅参考 |
| `MOD-YOLOV5S-640-ARS45-SRC` | **AGPL-3.0** ✘ | **licensing-hold** | — | — | 禁入交付物 |
| `MOD-YOLOV8S-COCO80-ONNX` | **AGPL-3.0** ✘ | **licensing-hold** | — | — | 禁入交付物 |
| `MOD-YOLOV5S-320-INT8` / `-DUP` | AGPL-3.0 | quarantined | — | — | C1 文件不存在 |
| `MOD-YOLOV8S-COCO80-NB` | AGPL-3.0 | quarantined | — | — | C1 文件不存在 |
| `MOD-YOLOV5S-A733-NB-BASELINE` | AGPL-3.0 | quarantined | — | — | C1 文件不存在 |
| `MOD-YOLOV5S-320-QUANT-PARAM` | AGPL-3.0 | reference | — | — | C1 文件不存在 (需重建) |
| `MOD-YOLOV5S-320-CALIB-DATASET` | AGPL-3.0 | reference | 100 张 (★**1 个空文件**) | — | ★见 §4.2 |
| `MOD-YOLOV8S-SCENEFT-NB` (+ 其余) | — | reference | — | — | — |

**汇总 (本周实测)**: 资产 **13** 条 · FAIL **12** · WARN **12** · 重复组 **1** ·
交付集 **2** · licensing-hold **2** · quarantined **4** · reference **5** · **L = 0** ·
★**交付集里 NPU 就绪且有实测精度的产物 = 2 条** (Apache-2.0 那两条)。

---

## 2. ★★★ 空清单的成因 (4 条, 按本周新信息重排)

### 成因 1 — ~~"唯一许可干净候选转不了"~~ ★**本周被证伪** (降级)

| 项 | 内容 |
|---|---|
| ~~旧结论~~ | ISS-101 原判: Apache-2.0 候选 (TF OD API SSD-MobileNetV2-FPNLite) 的 **NPU 可转换性 = 0 数据** ⇒ 唯一许可干净的模型进不了 NPU |
| ★**本周实测 (2026-11-06)** | ★**用 `rknn-toolkit2 2.3.2` 实跑该候选 (head 子图)**: `config(target_platform='rk3576')` **rc=0** · `load_onnx` **rc=0** ⇒ ★**它能进 RKNN 工具链** |
| ★**为什么以前是 0 数据** | ★**因为当时用的是 Art.Galaxy (原厂工具链), 而基线已换 SoC** —— ISS-101 是 10-27 登记的, 那时基线还是 ARS45 (非 Rockchip) ⇒ ★**用错了工具链** ⇒ ★**换 RK3572 后, 正确的编译工具就是 `rknn-toolkit2`** (瑞芯微自家) |
| ⇒ **现状** | ★**这条成因作废**。真因数 = **成因 2** |

### 成因 2 — ★★ Apache-2.0 候选的 ONNX **输入是 float64** ⇒ RKNN 量化器直接拒收 (本周抓出并修掉)

| 项 | 内容 |
|---|---|
| ★**现象 (实测)** | `build(do_quantization=True)` → **`E RKNN: Not Support Dtype: 2. please check precision!`** ⇒ build rc≠0 |
| ★**根因 (实测定位)** | 该 head 子图的 **graph input `input_tensor` 的 `elem_type = 2` (float64)**, 而 RKNN 量化器只接受 float32/int8 口径 |
| ★**证据** | `onnx.load(...)` 读 `graph.input[0].type.tensor_type.elem_type` → **2 = FLOAT64**; ★**其余张量全是 float32 (241 个 initializer) 或 bool (12 个)** ⇒ ★**只有输入这一处** |
| ★**影响面** | ★**这是 `SW/MODEL_RELEASE_GATE.md` §C9/C10 那类缺陷的一个新实例** —— C9 (PC 侧推理冒烟) **只查"能不能推理", 不查 dtype 是否被 NPU 编译器接受** ⇒ ★**C9 判定"好模型", 但 NPU 编译器拒收** ⇒ ★**门禁漏判** |
| ★**修法 (实测有效)** | 把 graph input 的 `elem_type` 由 **2 → 1 (float32)** (权重与计算图一字未动) ⇒ ★**`build` rc=0** |
| ★**修完的产物** | `/tmp/apache_ssd_rk3576_int8.rknn` · **9,513,373 B = 9.07 MiB** (装得进 15 MiB 板端槽位) · sha16 `cc8f51113e559544` · `build` 耗时 **51.7s** |
| ⇒ **现状** | ★**这条成因在本周已闭合到"PC 侧全通"** ⇒ 只剩 **板端** (成因 3) |

### 成因 3 — ★★ 板端 INT8 产物 = 0 个 / 板端实测 = 0 次 (未变, 一票否决)

| 项 | 内容 | 证据 |
|---|---|---|
| 板端 `.rknn` 产物 | **0 个** | [实测] 台账无板端产物条目 |
| 板端 INT8 精度 | **0 次** | [0数据] |
| 板端纯 NPU 耗时 (S5) | **0 次** | [0数据] |
| ★**根因** | ★**无板** —— `192.168.2.5` 不可达 (ping 100% 丢包 + ARP `INCOMPLETE`); 且 `rk3572` 不是合法 target ⇒ 板端要加载的必须是用 `rk3576` target 转的产物 ⇒ ★**"能不能加载"本身就是未验证命题** (ISS-155) | [实测] + [实测] |
| ⇒ **现状** | ★**仍是主因**, 已升级为需要老板/硬件侧解锁的卡点 (见 §3 路径 A) | — |

### 成因 4 — ★ AGPL 商用路径未拍板 (不阻塞 Apache-2.0 路线, 但阻塞 yolov5 路线)

| 项 | 内容 |
|---|---|
| 现状 | 2 条 AGPL 资产置 **licensing-hold** (禁入交付物); 采购决策 = **boss**, 走项目总工 (`SW-MODEL-B2-ISS101-RU1`, 至今未回) |
| 成本 [推算] | 一次性 US$5k-50k + 年费 US$2k-20k/型号, 周期 4-12 周, 官方无公开价 [0数据] |
| ⇒ **现状** | ★**不阻塞 Apache-2.0 路线** ⇒ 但 ★**如果最终选 yolov5 路线 (demo 首选, F1 0.2927 已实测), 就是硬阻塞** ⇒ ★**这是一个"路线选择 ⇒ 许可决策"的依赖链, 不是孤立的许可问题** |

---

## 3. ★★ 补齐路径 (3 条, 带判定口径与时限)

### 路径 A — ★用 Apache-2.0 候选走通到底 (本周推荐, 因为前提已证伪)

| 步 | 动作 | 判定口径 | 谁 | 时限 |
|---|---|---|---|---|
| A1 | ★**已实测**: float64 → float32 修 input dtype, `rknn-toolkit2 2.3.2` `build` rc=0, 产物 9.07 MiB | ✅ **达成** (本周 11-06) | sw-lead | **已完成** |
| A2 | **板端加载 + 精度** | `load_rknn` rc=0 **且** 板端 F1 ≥ **PC 侧 F1 − 0.05** | sw-lead | ★**等板** (路径 B 的板) |
| A3 | **板端纯 NPU 耗时** | `t_npu` 与 `t_sdk_total` **都报**; `t_npu` ≤ **13.30ms** [推算] (RK3576 基线 8.87 × 6/4) | sw-lead | ★**等板** |
| A4 | **回流台账**: 修 C9 门禁加"输入 dtype 必须 float32"判据 + 登记新资产 ID (sha256 `cc8f51113e559544`) | 台账条数 +1, C9 判据 +1 | sw-lead | A2/A3 后 |
| ★**风险** | ★**Apache-2.0 候选的精度基线弱于 yolov5n** (F1 0.2927 是 yolov5n 的数; 本单在 PC 侧尚未对 Apache-2.0 候选做完整体精度评测) ⇒ ★**若 A2/A3 过了但精度不足 0.25 (demo 线) ⇒ 这条路仍通不了 demo** ⇒ **必须补 PC 侧精度基线** | — | sw-lead | 本周补 |

### 路径 B — ★★ 拿到一块能启动的 RK3572 板 (A2/A3 的共同前置, 也是 ISS-155 的前置)

| 项 | 内容 |
|---|---|
| ★**推荐** | **Forlinx OK3572-C** (ISS-151 清单里已有, **且它同时是 demo Step1 的载体** ⇒ 一举两得) |
| 次选 | 等 Radxa A7S 回到同网段 (装 sshpass 顺手做) |
| ★**注意** | ★**"rk3576 产物能否在 RK3572 上加载"是跨平台命题 ⇒ 用 RK3576 板测不构成证据** |
| ⇒ **时限** | 采购/借板排期由项目总工与老板定 ⇒ **sw-lead 不下单** |

### 路径 C — AGPL 商用 (yolov5 路线的前置, 待 boss 拍板)

| 项 | 内容 |
|---|---|
| 决策 | 采购 Enterprise License vs 走 Apache-2.0 栈 ⇒ **boss 拍板**, 走项目总工 (`SW-MODEL-B2-ISS101-RU1`) |
| ★**新信息 (本周)** | ★**路径 A 的前提已被证伪并推进到"PC 侧全通"** ⇒ ★**"路径1 (采购) 与路径2 (换栈) 并行准备"的建议里, 路径2 的工程可行性显著上升** ⇒ ★**建议 boss 在拍板时把这条新信息一并纳入** |
| 时限 | ★**晚于投板就白跑一轮** (换模型 = 换图 = 重跑裁图+量化) ⇒ **须在投板前定** |

---

## 4. ★★ 本周另查实的 3 个真缺陷 (都可复现)

### 4.1 ★ 台账 C2/C3 与实物不符 ⇒ 须登记新资产 ID

| 项 | 内容 |
|---|---|
| 现象 | `MOD-YOLOV5S-640-ARS45-SRC` 的 C2 (大小) 与 C3 (sha256[:16]) 两项都 ❌: 台账记 **29,337,706 B / 20368be665f6f59a**, 实物 **29,365,856 B / 1e2c716bd16ed9d3** |
| 原因 | 重建件与丢失原件**不是逐字节同一份** (onnxsim/torch 版本差异导致节点名与常量编码不同) |
| ⇒ 处置 | 按台账自己的纪律 ("**版本只认 sha256**") ⇒ ★**重建件必须登记为新资产 ID, 不能冒充 `MOD-YOLOV5S-640-ARS45-SRC`** ⇒ 本周已登记新资产 |

### 4.2 ★★ 校准集里有 1 个 0 字节空文件 ⇒ 实跑只吃 99 张 (静默掉样本, 不报错)

| 项 | 内容 |
|---|---|
| 现象 | `~/Public/radxa_yolo/calib_yolov5_100/` 共 **100** 个 jpg, 但 `000000010583.jpg` 是 **0 字节** ⇒ `rknn_bench.py` 实跑报 "**99 张**" |
| ★**为什么要紧** | ★**校准集少 1 张不会报错** ⇒ 量化结果照常产出 ⇒ **门禁显示绿灯, 但量化少了 1 张的代表性** ⇒ 与 ISS-157 (cut 模型缓存不失效) 是**同一类病**: "**静默出错的绿灯**" |
| 本周处置 | 已用 COCO val2017 重生成 **100 张 320×320** 校准集到 `/tmp/apache_calib320/` 供 Apache-2.0 候选 build 用 ⇒ ★**原目录的空文件待补** (已登记 need) |

### 4.3 ★ C9 门禁漏判: "PC 侧能推理" ≠ "NPU 编译器能收"

| 项 | 内容 |
|---|---|
| 现象 | Apache-2.0 候选 **通过 C9 (PC 侧推理冒烟)**, 但 `build` 阶段被 RKNN 以 "Not Support Dtype: 2" 拒收 |
| ⇒ 结论 | ★**C9 必须加一条: graph input 的 `elem_type` 必须是 float32 (1)** —— 不然门禁会给出"这个模型好着呢"的假绿灯 |
| ⇒ 处置 | 已登记进台账更新项 (§3 路径 A4) |

---

## 5. ★ 硬指标数字 (报告用)

| 指标 | 本周实测 | 等级 |
|---|---|---|
| **量产可用模型清单条数** | **0** | [实测] |
| 台账资产条数 | **13** (FAIL 12 / WARN 12 / 重复组 1) | [实测] |
| 交付集条数 / licensing-hold / quarantined / reference | **2 / 2 / 4 / 5** | [实测] |
| 放行阻断项 L | **0** | [实测] |
| ★**许可干净候选的 NPU 可转换性** | ★**PC 侧已通**: config rc=0 · load_onnx rc=0 · build rc=0 (51.7s) · 产物 **9.07 MiB** | ★**[实测]** |
| ★**同一候选的板端可转换性** | **0 次** (无板) | **[0数据]** |
| 板端 INT8 模型数 / 板端精度 / 板端 S5 | **0 / 0 / 0** | [0数据] |
| AGPL 采购决策 | **未拍板** (待 boss) | [0数据] |

---

## 6. 自证复现命令 (一条命令)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 台账状态 (L 计数 + 交付集 + licensing-hold)
~/miniconda3/envs/rknn/bin/python SW/tools/model_asset_check.py
# ② Apache-2.0 候选的 NPU 可转换性 (config + load_onnx + build)
#    ★注意: 原始 head 子图的 graph input 是 float64 ⇒ 必须先改成 float32 (见 §2 成因 2)
~/miniconda3/envs/rknn/bin/python - <<'PY'
import onnx
from onnx import TensorProto
p="SW/artifacts/models/ssd_mbv2_fpnlite_320_fp32_head_npu.onnx"
m=onnx.load(p)
print("原始 input elem_type =", m.graph.input[0].type.tensor_type.elem_type, "(2=float64)")
for i in m.graph.input:
    i.type.tensor_type.elem_type = TensorProto.FLOAT
onnx.save(m,"/tmp/apache_ssd_head_f32in.onnx"); print("已改 float32 -> /tmp/apache_ssd_head_f32in.onnx")
PY
~/miniconda3/envs/rknn/bin/python -c "
import sys; sys.path.insert(0,'/home/yuewuya/miniconda3/envs/rknn/lib/python3.10/site-packages')
from rknn.api import RKNN
r=RKNN(verbose=False); print('config', r.config(target_platform='rk3576'))
print('load ', r.load_onnx(model='/tmp/apache_ssd_head_f32in.onnx'))
print('build', r.build(do_quantization=True, dataset='/tmp/apache_calib320/dataset.txt'))
print('export', r.export_rknn('/tmp/apache_ssd_rk3576_int8.rknn'))
"
ls -la /tmp/apache_ssd_rk3576_int8.rknn   # 9,513,373 B = 9.07 MiB
```

---

> **本单纪律声明**: 本单**未修改** `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `HW/` / `MECH/` /
> 网表 / 板文件 / 任何既有 SW 脚本; **未联系任何供应商**; **未下单**;
> 板端相关数字一律标 **[0数据]**; PC 侧结论标 **[实测]** 并附复现命令。
