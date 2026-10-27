# SW/MODEL_RELEASE_GATE.md — 量产放行门 (L=0) 判定标准 + 量产可用模型清单

> **单号**: ISS-101 (sw-lead, 2026-10-28, 项目总工 00:5x 代登记) · 承接 ISS-087
> **一句话**: **"放行阻断项 L=0" 与 "有可用模型" 是两件事** ——
> L=0 只说明**交付集里没有未解决的许可/容量/chip/模型完整性阻断项**;
> 而**量产可用模型清单 (能真上板、真出框的 OD 模型) 现在 = 空 (0 个)**。
> 本文把这两件事的口径、判据、谁在什么时候查写死, 防止 "L=0" 被当成 "可以量产了"。
> **证据分级**: [实测] / [官方] / [推算] / [0数据]

---

## 1. 两个清单, 不要混

| 清单 | 定义 | 判据 | 现状 (2026-10-28) |
|---|---|---|---|
| **① 交付集 (ship set)** | 台账里 `state ∈ {candidate, active}` 的资产 = **准备进 ARS45 交付物**的模型 | `model_asset_check.py` 的 `ship_set` | **1 条** (`MOD-SSDMBV2-FPNLITE-320-COCO90-TFODAPI`, Apache-2.0) |
| **② 量产可用模型清单** | **真的能上板出框**的 OD 模型 = 有板端产物 + 板端实测通过 + 许可闭环 + 回归全过 | 见 §3 四条 | **0 条** ❌ |

**放行阻断项 L (① 的门禁) = 0** ⇒ ① 里没有"卡死"的东西;
但 ① 里的模型**能不能上板**是另一条链 (板端产物 → 板端实测), 那条链现在一环没走完 ⇒ **② = 0**。

> ★ **不要用 "L=0" 当 "可以量产了" 的证据**。2026-10-28 之前, `model_asset_check.py` 打印的是
> "→ ✅ 可进量产评审", 这句话**过强** → 本单已改成 "✅ 放行阻断项已清零 (★不等于有可用模型)",
> 并加了一行显式提示指向本文。

---

## 2. 放行阻断项 L1~L5 (判定标准, 与工具逐条对应)

| 阻断项 | 定义 | 机器判据 (在哪一行代码) | 谁负责消 | 现状 |
|---|---|---|---|---|
| **L1** | **许可未判定** (台账 `expected_license` 为空) | `count_release_blockers()` → `license_state == unknown` | sw-lead (溯源) | **0** ✅ |
| **L2** | 板端产物超 15 MiB 槽位 (刷不进) | C4: `.nb` 字节数 > 15,728,640 | sw-lead + hw-lead (flash 容量) | **0** ✅ |
| **L3** | chip ID 与目标 NPU 不符 (板端加载报 SRAM size 错) | C7: NBG 头 byte 8-11 (LE uint32) | 原厂给 ARS45 chip ID | **0** ✅ (交付集无板端产物) |
| **L4** | **AGPL-3.0 且无 Enterprise 授权记录** → 商用受阻 | `license_state == ungranted` | 老板拍板 + 采购 (经项目总工) | **0** ✅ (2 条 AGPL 资产在 `licensing-hold` 禁入交付物) |
| **L5** | **交付集模型 PC 侧推理冒烟失败** (模型本身是坏的) | C9: onnxruntime 建 session + 跑 1 帧 | sw-lead (重导出) | **0** ✅ |

**判定口径两条铁律** (ISS-087 修订):
1. **"许可未判定" 才是阻断项; "`metadata_props` 为空" 不是** —— 后者只是取数方式问题 (可溯源判定)。
2. **L 只统计交付集 (candidate/active)**; `reference` / `quarantined` / `licensing-hold` 不进交付集,
   但**必须单独列出** (工具输出里有 "licensing-hold 禁入交付物" 与 "quarantined 已判死" 两段) —— 不许静默消失。

---

## 3. 量产可用模型清单 = 0 (为什么 L=0 却还是 0 个可用模型)

一个模型要进**② 量产可用模型清单**, 四条必须同时成立:

| # | 条件 | 判据 | 现状 |
|---|---|---|---|
| 1 | **许可闭环** | 许可已知 **且** (宽松许可 或 有 Enterprise 授权号) | 交付集那 1 条 Apache-2.0 ✔; 两条 AGPL ✖ (licensing-hold) |
| 2 | **有板端产物** | 台账里有对应的板端格式资产 (NBG / Art.Galaxy 格式) 且 ≤ 15 MiB 且 chip ID 匹配 | **✖ ARS45 板端产物 = 0 个** (转换 0 次) |
| 3 | **板端实测通过** | 板端加载 OK + 首帧输出 shape 与 PC 端逐路一致 + 分段耗时 (纯 NPU / SDK 总耗时) 实测值 | **✖ 无板, 实测 0 次** |
| 4 | **回归全过** | `SW/MODEL_ASSETS.md` §4.2 的 R-01~R-14 全过 (含量化精度评估) | **✖ R-04 起全部不可跑** (无板端产物) |

**唯一许可干净的候选 (Apache-2.0) 卡在哪**:
`MOD-SSDMBV2-FPNLITE-320-COCO90-TFODAPI` (TF OD API SSD-MobileNetV2-FPNLite 320×320, `num_classes: 90` → 可用 80 类)
卡在条件 2/3/4 —— **TF SavedModel → ONNX → Art.Galaxy 三段都没跑过** = [0数据]。
⇒ 已登记为 blocker **`SW-MODEL-B2`** (severity=high)。

**唯一实测可推理的 yolov5s 资产** (`MOD-YOLOV5S-640-ARS45-SRC`, 640×640, onnxruntime 冒烟 OK)
卡在条件 1 —— **AGPL-3.0, 未采购 → 禁入交付物**。

> ⇒ **"许可干净" 与 "NPU 可用" 两个条件在本地暂无交集** —— 这就是 ISS-101 的核心内容。

### 补齐路径 (三条, 与 `SW/MODEL_LICENSE.md` §3 一致)

| 路径 | 补齐哪个条件 | 需要什么 | 成本 | 时限 |
|---|---|---|---|---|
| **A 采购 Enterprise** | 条件 1 | 老板拍板 → 项目总工询价 → 合同 → 授权号填 `license_grant` | 10⁴–10⁵ USD [推算] | 4–12 周 [推算] |
| **B 换 Apache-2.0 栈** | 条件 1 (+ 条件 2 靠新转换) | YOLOX-s 权重 (Apache-2.0, 80 类; Rockchip model zoo 已有同族 NPU 转换配方) → 走 B0~B9 | 许可 0 + 3–8 人日 [推算] | 取决于 Art.Galaxy 工具链 |
| **C 等原厂预编译模型** | 条件 1 (原厂承担) | 原厂提供许可由原厂负责的官方模型 | 0 | 原厂回复 |

**三条路径都还缺同一个东西: Art.Galaxy 工具链 + ARS45 chip ID (条件 2/3)** —— 这是唯一的公共前置。

---

## 4. 量产评审放行检查表 (谁在什么时候查什么)

| 阶段 | 检查 | 工具/判据 | 责任人 | 通过判据 |
|---|---|---|---|---|
| **每次模型入库** | 台账字段完整 + 许可已判定 + 冒烟通过 | `model_asset_check.py --new <file>` + C5/C9 | sw-lead | C1~C9 全 ✅, L 计数不增 |
| **每次转换产物入库** | 容量 + 头字段 + chip ID + 版本串 sha 绑定 | C4/C5/C6/C7 + `model=<family>-int8-ag2-<sha8>` | sw-lead | ≤15 MiB, magic `VPMN`, chip 匹配, sha8 一致 |
| **投板前** | 交付集门禁 | `python3 SW/tools/model_asset_check.py` → **L=0** | sw-lead → 项目总工 | L=0 **且** ② 清单非空 |
| **投板前** | 转换链就绪 | `python3 SW/tools/int8_chain.py` → BLOCKED 步清零 | sw-lead | B0/B4/B5/B7/B8 不再 BLOCKED |
| **板子回来后** | 板端实测 (加载 / shape / 分段耗时) | B7 + B8 打点表 (`SW/ARS45_INT8_CHAIN.md` §4) | sw-lead | 首帧 shape 逐路一致; 每段给 min/avg/max + 帧数 |
| **板子回来后** | 精度 + 回归 | `SW/MODEL_ASSETS.md` §3 + §4 (R-01~R-14) | sw-lead | 全过 |
| **量产评审** | ★ **同时查 L=0 与 ② 清单非空** | 两个判据缺一不可 | 项目总工 | 两张表都过 |

> ★ **新增一条门禁**: 以前只看 L 计数; 从 ISS-101 起, 量产评审必须**同时**看 "L=0" 与 "量产可用模型清单非空"。
> 理由: L 只管交付集里的**静态属性** (许可/容量/chip/完整性), 不管**动态属性** (能不能上板出框)。

---

## 5. 自证复现命令

```bash
cd projects/smart_glasses

# ① 放行门禁 (L 计数) —— 预期 L=0, rc=0
python3 SW/tools/model_asset_check.py
# 预期: 资产 11 条 · FAIL 0 · 交付集 1 条 | licensing-hold 2 条 | quarantined 4 条 | reference 4 条
#       量产放行阻断项 (L): 0 条 → ✅ 放行阻断项已清零 (★不等于有可用模型)

# ② 量产可用模型清单 = 空 的依据 (交付集候选的 NPU 可转换性 = 0 数据)
python3 SW/tools/model_asset_check.py --json | python3 -c "
import json,sys; d=json.load(sys.stdin)
print('交付集:', d['ship_set']); print('禁入交付物:', d['licensing_hold']); print('阻断项:', len(d['release_blockers']))"

# ③ 转换链就绪度 (B0/B5/B7/B8 仍 BLOCKED ⇒ 条件 2/3 未满足)
python3 SW/tools/int8_chain.py | tail -8
# 预期: READY 2 · PARTIAL 4 · BLOCKED 4 (共 10 步); BLOCKED: ['B0','B5','B7','B8']

# ④ 项目门禁
python3 state/merge.py && python3 state/gate_check.py
```
