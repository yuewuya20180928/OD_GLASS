# ISS-353 · 逐条处置清单 (★机器生成 · 数据源: 闸 --json + 补丁脚本 REPLACEMENTS★)

生成时间: 2026-11-23 (sw-lead · ISS-353 cont1) · 闸: `SW/tools/check_rk3572_target_caliber.py` (v2.0)

闸当前读数: 扫面文件 1997 · 命中 338 行 · **结论矛盾 16** · 结论待裁 6 · 历史叙述 316

---


## A. 「结论矛盾(要处置)」逐条处置表 (16 条)

| # | 文件:行 | 规则 | 原文片段 (截 120 字) | 处置类别 | 处置内容 |
|---|---|---|---|---|---|
| 1 | `HW/STEP1_LANDING_LIST.md` L203 | A2 | \| **S1** \| ★**target 兼容性验证**（`rk3572` 非合法 target ⇒ 用 `rk3576` 转） \| 🔴 **卡板子** ⇒ ★**主板回来后第一件事**（ISS-155） \| | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #1: Step1 落地清单 S1: 转换 target 改口径 |
| 2 | `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` L307 | A1 | \| 编译期 \| ★**官方根本没有 `rk3572` 这个 target** (2.3.2 与 2.5.0 均无) ⇒ 只能 `target_platform='rk3576'` 转 \| 已 [官网]+[实测] 钉死 (ISS-207) \| | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #2: 60ms 判决页 编译期行: 转换 target 改口径 |
| 3 | `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` L308 | A1 | \| ★**加载期** ★ \| ★**RK3572 BSP runtime 认不认 rk3576-target 产物** ⇒ 官方无此口径 ⇒ **只能板端判** \| ★**N1** (`load_rknn` ret == 0) \| ★**★ | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #3: 60ms 判决页 加载期行: 补 rk3572-target 分支 |
| 4 | `SW/DEMO_OD_PIPELINE_SPEC.md` L15 | A1 | \| 2 \| ★★**"板端模型可直接复用 A7S 的 .rknn 产物" 不成立** —— 实测 `rk3572` **不是任何已发布版 rknn-toolkit2 的合法 target_platform** (2.3.2 与 2.5.0  | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #4: OD pipeline spec 结论表第 2 行: 转换 target 改口径 |
| 5 | `SW/DEMO_OD_PIPELINE_SPEC.md` L143 | A1 | \| ★★**`target_platform` (★写死)** \| ★★**只能用 `'rk3576'`** —— ★**`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 target** (2.3.2 与最新 2.5 | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #5: OD pipeline spec §2.3 target_platform 写死行: 改写为 rk3572 |
| 6 | `SW/DEMO_OD_PIPELINE_SPEC.md` L184 | A1 | \| **P0-1** \| ★**rknn-toolkit2 2.3.2 的 `target_platform` 是否含 `rk3572`** \| `SW/RKNN_BENCH.md` §5 只证过 **含 `rk3576`** (`rknn | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #6: OD pipeline spec P0-1 行: 阻塞状态降级 (toolkit2 限定) |
| 7 | `SW/MODEL_RELEASE_LIST.md` L85 | A1 | \| ★**根因** \| ★**无板** —— `192.168.2.5` 不可达 (ping 100% 丢包 + ARP `INCOMPLETE`); 且 `rk3572` 不是合法 target ⇒ 板端要加载的必须是用 `rk3576` | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #8: 模型发布清单 根因行: 转换 target 改口径 |
| 8 | `SW/RK3572_TARGET_BOARD_VERIFY.md` L7 | A1 | > `target_platform` ⇒ 必须用 `target_platform='rk3576'` 转换)。但**剩下的那条死结**—— | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #9: 板端验证单 摘要行: 转换 target 改口径 |
| 9 | `SW/RKNN_BUILD_ENV_RECOVERY.md` L17 | A2 | \| 3 \| ★★ **但 RK3572 的 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ 用 `target_platform='rk3576'` 转换, 板端用 RK3572 BSP 自带 ru | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #10: 构建环境恢复 §0 摘要第 3 行: 前提反证 + 转换 target 改口径 |
| 10 | `SW/RKNN_BUILD_ENV_RECOVERY.md` L246 | C1 | 1. ★★ **`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform`** —— 从 2.2.0 到最新 2.5.0 全部拒绝, **不存在"升级到某版本就有 rk3572"这个选项**。 | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #11: 构建环境恢复 §2.2 结论 1: 结论限定在 toolkit2 家族内 |
| 11 | `SW/RKNN_BUILD_ENV_RECOVERY.md` L247 | A1 | 2. ★★ **⇒ ISS-145 §1 的 M1 路线 ("直接复用 A7S 的 .rknn 产物") 前提不成立** —— 那个 .rknn 是 `target_platform='rk3576'` 编译出来的, 即使它能被 RK357 | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #12: 构建环境恢复 §2.2 结论 2: 「没有 rk3572 编译目标」加限定 |
| 12 | `SW/RKNN_BUILD_ENV_RECOVERY.md` L248 | A1 | 3. ★**替代路线: 用 `target_platform='rk3576'` 转换** —— 理由是 RK3572 的 NPU 与 RK3576 **同代同架构**, 但这是**推算, 不是实测**, 必须板端验证 (见 §2.4.3) | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #13: 构建环境恢复 §2.2 结论 3: 替代路线标注取代 |
| 13 | `SW/RKNN_BUILD_ENV_RECOVERY.md` L262 | A2 | > ★**这些是"支持用 rk3576 target 转换"的**依据**, 不是"rk3572 = rk3576"的证据**。 | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #14: 构建环境恢复 §2.4 引述行: 依据降为历史 |
| 14 | `SW/RKNN_BUILD_ENV_RECOVERY.md` L801 | A1 | \| **1** \| §1 M1 = "直接复用 A7S 的 .rknn, 零转换成本" \| ★**前提不成立** (§2.2: rk3572 非法 target) ⇒ **必须重转** \| ★**改 M1 定义为"用 rk3576 targ | D3 越权·交 main 裁 (附逐字替换文本) | 补丁 #15: 构建环境恢复 §6 降级表 M1 行: 目标 target 改口径 |
| 15 | `state/fragments/hw.yaml` L5226 | E1 | Invalid target_platform 「rk3572」!`) ⇒ ★**M1 复用 A7S 的 .rknn 不成立, 必须重转**; ★**RK3572 NPU 与 RK3576 同代同架构 | D3' 别人分片·交 main 转 hw-lead | 追加一条切题取代标记 (文本见交卷页 §B1.3 / 分片 need `iss353_need_hw_ledger_supersede`) |
| 16 | `state/fragments/hw.yaml` L5227 | A2 | (4 TOPS / 3 核 RKNPU v2) ⇒ 用 `target_platform=「rk3576」` 转 + 板端 RK3572 BSP runtime 加载** [推算·待板端验证] ⇒ | D3' 别人分片·交 main 转 hw-lead | 追加一条切题取代标记 (文本见交卷页 §B1.3 / 分片 need `iss353_need_hw_ledger_supersede`) |

## B. 「结论待裁(交 main 裁)」清单 (6 条) —— ISS-155 状态标签, ★sw-lead 不代拍★

| 文件:行 | 原文片段 | 说明 |
|---|---|---|
| `SW/RK3572_TARGET_BOARD_VERIFY.md` L3 | > 版本: v1.0 (2026-11-06) · owner: sw-lead · 对应 issue: ISS-155 (demo 头号卡点) / ISS-147 (P0-1) | ISS-155 的定位 = 只有老板能改的状态标签 ⇒ 不判红, 但点名 |
| `SW/RK3572_TARGET_COMPAT_V2.md` L3 | > 版本: **v2.0** (2026-11-15) · ★**v2.1 追加 (2026-11-23 · ISS-353) ⇒ 见 §7**★ · owner: sw-lead · 对应 issue: **ISS-2 | ISS-155 的定位 = 只有老板能改的状态标签 ⇒ 不判红, 但点名 |
| `SW/RK3572_TARGET_COMPAT_V2.md` L400 | \| `SW/RK3572_TARGET_COMPAT_V2.md` L3 \| 结论待裁 (ISS-155 定位) \| ★**ISS-155 是否从「demo 头号卡点」降为「转换链已通 / 板端待板」= 交 main 裁 | ISS-155 的定位 = 只有老板能改的状态标签 ⇒ 不判红, 但点名 |
| `SW/research/ISS250_r6_复核记录.md` L5 | \| 单号 \| ★**ISS-250** (★根因单 ISS-155 · open · blocker · demo 头号卡点★) \| | ISS-155 的定位 = 只有老板能改的状态标签 ⇒ 不判红, 但点名 |
| `SW/tools/check_rknn_target_compat.py` L7 | ★ISS-155 (demo 头号卡点) 的核心事实是「rk3572 不是 rknn-toolkit2 的合法 target」★ | ISS-155 的定位 = 只有老板能改的状态标签 ⇒ 不判红, 但点名 |
| `state/fragments/hw.yaml` L5228 | **demo 头号卡点 ISS-155**; ★本机已就绪 (conda env rknn + 转换四步 rc=0 + yolov5n INT8 5.13MiB + COCO val2017 与 | ISS-155 的定位 = 只有老板能改的状态标签 ⇒ 不判红, 但点名 |

## C. 越权条目的逐字替换文本 (15 条补丁 / 覆盖 14 条命中行)

### 补丁 #1 — `HW/STEP1_LANDING_LIST.md`

- **理由**: Step1 落地清单 S1: 转换 target 改口径
- **旧片段** (替换前, 须精确命中且唯一):

```
★**target 兼容性验证**（`rk3572` 非合法 target ⇒ 用 `rk3576` 转）
```

- **新片段** (替换后):

```
★**target 兼容性验证**（★toolkit2 侧 `rk3572` 非合法 target ⇒ 转换链走 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`★） ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #2 — `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md`

- **理由**: 60ms 判决页 编译期行: 转换 target 改口径
- **旧片段** (替换前, 须精确命中且唯一):

```
★**官方根本没有 `rk3572` 这个 target** (2.3.2 与 2.5.0 均无) ⇒ 只能 `target_platform='rk3576'` 转
```

- **新片段** (替换后):

```
★**toolkit2 (2.3.2 与 2.5.0) 都没有 `rk3572` 这个 target** ⇒ ★**转换链走 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`** (config rc=0 [实测]) ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #3 — `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md`

- **理由**: 60ms 判决页 加载期行: 补 rk3572-target 分支
- **旧片段** (替换前, 须精确命中且唯一):

```
★**RK3572 BSP runtime 认不认 rk3576-target 产物** ⇒ 官方无此口径 ⇒ **只能板端判**
```

- **新片段** (替换后):

```
★**RK3572 BSP runtime 认不认 rk3572-target 产物** (★主路线; rk3576-target 已降为次要路线①★) ⇒ 官方无此口径 ⇒ **只能板端判** ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #4 — `SW/DEMO_OD_PIPELINE_SPEC.md`

- **理由**: OD pipeline spec 结论表第 2 行: 转换 target 改口径
- **旧片段** (替换前, 须精确命中且唯一):

```
⇒ ★**必须用 `target_platform='rk3576'` 重转** (RK3572/RK3576 同代 RKNPU v2; ★**但算力不等 4 vs 6 TOPS ⇒ 板端待验**)
```

- **新片段** (替换后):

```
⇒ ★**必须重转, 但转换 target 改为 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`** (★ISS-263 实测 config rc=0 / 转换 rc=0 / 产物 249,360 B md5 97a34fff0b855b92681f26627dba5354; ★2026-11-23 ISS-353 复跑逐字节一致★) · ★**板端接受性仍 [0数据] ⇒ 板端待验**★ ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #5 — `SW/DEMO_OD_PIPELINE_SPEC.md`

- **理由**: OD pipeline spec §2.3 target_platform 写死行: 改写为 rk3572
- **旧片段** (替换前, 须精确命中且唯一):

```
★★**只能用 `'rk3576'`** —— ★**`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 target** (2.3.2 与最新 2.5.0 都抛 `ValueError: Invalid target_platform 'rk3572'!`) ⇒ ★**在 RK3572 上也必须用 `target_platform='rk3576'` 转** (RK3572/RK3576 同代 RKNPU v2); ★**但算力不等 (4 vs 6 TOPS) ⇒ 该 .rknn 在 RK3572 上的表现板端待验**
```

- **新片段** (替换后):

```
★★**只能用 `'rk3572'`** —— ★**`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 target** (2.3.2 与最新 2.5.0 都抛 `ValueError: Invalid target_platform 'rk3572'!`) ⇒ ★**转换链改走 rknn3-toolkit 1.2.0, 其 `config(target_platform='rk3572')` rc=0** (★ISS-263 实测 / ★2026-11-23 ISS-353 复跑 rc=0★); ★**板端接受性仍 [0数据] ⇒ 该 .rknn 在 RK3572 上的表现板端待验** ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #6 — `SW/DEMO_OD_PIPELINE_SPEC.md`

- **理由**: OD pipeline spec P0-1 行: 阻塞状态降级 (toolkit2 限定)
- **旧片段** (替换前, 须精确命中且唯一):

```
⇒ ★**"升级到某版本就有 rk3572"这个选项不存在** ⇒ 本行不再是 [待核], 而是**已定的阻塞** ⇒ 替代路线见 ISS-155。
```

- **新片段** (替换后):

```
⇒ ★**"升级到某版本就有 rk3572"这个选项不存在** (★**限定在 toolkit2 家族内**★) ⇒ ★**v2.1 订正 (2026-11-23 · ISS-353): 本行的"已定的阻塞"已降级 —— 转换链已通 (rknn3-toolkit 1.2.0 支持 `target_platform='rk3572'`, [实测]) ⇒ 剩下的只是板端接受性 [0数据]**★ ⇒ 替代路线见 ISS-155。
```

### 补丁 #7 — `SW/DEMO_OD_PIPELINE_SPEC.md`

- **理由**: OD pipeline spec P0-1 行: 2026-11-02 替代路线标注取代
- **旧片段** (替换前, 须精确命中且唯一):

```
★★**ISS-155 已钉的替代路线 (2026-11-02)**: ★**用 `target_platform='rk3576'` 转, 板端用 RK3572 BSP 自带的 runtime 加载** (RK3572 与 RK3576 **同代同架构**: 3 核 RKNPU v2)
```

- **新片段** (替换后):

```
★★**ISS-155 当时钉的替代路线 (2026-11-02)**: ★**用 `target_platform='rk3576'` 转, 板端用 RK3572 BSP 自带的 runtime 加载** (RK3572 与 RK3576 **同代同架构**: 3 核 RKNPU v2 — ★该前提已被 ISS-250 官方反证★) ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #8 — `SW/MODEL_RELEASE_LIST.md`

- **理由**: 模型发布清单 根因行: 转换 target 改口径
- **旧片段** (替换前, 须精确命中且唯一):

```
且 `rk3572` 不是合法 target ⇒ 板端要加载的必须是用 `rk3576` target 转的产物
```

- **新片段** (替换后):

```
且 ★**toolkit2 侧 `rk3572` 不是合法 target ⇒ 板端要加载的必须是 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'` 产物**★ ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #9 — `SW/RK3572_TARGET_BOARD_VERIFY.md`

- **理由**: 板端验证单 摘要行: 转换 target 改口径
- **旧片段** (替换前, 须精确命中且唯一):

```
> `target_platform` ⇒ 必须用 `target_platform='rk3576'` 转换)。但**剩下的那条死结**——
```

- **新片段** (替换后):

```
> `target_platform` ⇒ ★**v2.1 订正 (2026-11-23 · ISS-353): 转换 target 已改为 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'` (config rc=0 [实测])**★ ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★)。但**剩下的那条死结**——
```

### 补丁 #10 — `SW/RKNN_BUILD_ENV_RECOVERY.md`

- **理由**: 构建环境恢复 §0 摘要第 3 行: 前提反证 + 转换 target 改口径
- **旧片段** (替换前, 须精确命中且唯一):

```
★★ **但 RK3572 的 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ 用 `target_platform='rk3576'` 转换, 板端用 RK3572 BSP 自带 runtime 加载**
```

- **新片段** (替换后):

```
★★ **但 RK3572 的 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ 用 `target_platform='rk3576'` 转换, 板端用 RK3572 BSP 自带 runtime 加载** (★v2.1 订正 2026-11-23 ISS-353: 该前提已被 ISS-250 官方反证 (RK3576=6 TOPS / RK3572=RKNN3-native) ⇒ 转换链已改走 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`★) ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #11 — `SW/RKNN_BUILD_ENV_RECOVERY.md`

- **理由**: 构建环境恢复 §2.2 结论 1: 结论限定在 toolkit2 家族内
- **旧片段** (替换前, 须精确命中且唯一):

```
★★ **`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform`** —— 从 2.2.0 到最新 2.5.0 全部拒绝, **不存在"升级到某版本就有 rk3572"这个选项**。
```

- **新片段** (替换后):

```
★★ **`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform`** —— 从 2.2.0 到最新 2.5.0 全部拒绝, **不存在"升级到某版本就有 rk3572"这个选项** (★**限定在 toolkit2 家族内** ★v2.1 订正 2026-11-23 ISS-353: rknn3-toolkit 1.2.0 的 `config(target_platform='rk3572')` rc=0 [实测], 官方 README「Supported Platforms」明列 RK3572 [官网]★) ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #12 — `SW/RKNN_BUILD_ENV_RECOVERY.md`

- **理由**: 构建环境恢复 §2.2 结论 2: 「没有 rk3572 编译目标」加限定
- **旧片段** (替换前, 须精确命中且唯一):

```
因为**根本没有 `rk3572` 这个编译目标**。⇒ **必须重转**。
```

- **新片段** (替换后):

```
因为**根本没有 `rk3572` 这个编译目标** (★v2.1 订正 2026-11-23 ISS-353: ★这句现在只对 toolkit2 家族成立 —— rknn3-toolkit 1.2.0 有 rk3572 编译目标 [官网]+[实测]★)。⇒ **必须重转** (★转换 target = rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`★) ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #13 — `SW/RKNN_BUILD_ENV_RECOVERY.md`

- **理由**: 构建环境恢复 §2.2 结论 3: 替代路线标注取代
- **旧片段** (替换前, 须精确命中且唯一):

```
3. ★**替代路线: 用 `target_platform='rk3576'` 转换** —— 理由是 RK3572 的 NPU 与 RK3576 **同代同架构**, 但这是**推算, 不是实测**, 必须板端验证 (见 §2.4.3)。
```

- **新片段** (替换后):

```
3. ★**替代路线: 用 `target_platform='rk3576'` 转换** —— 理由是 RK3572 的 NPU 与 RK3576 **同代同架构**, 但这是**推算, 不是实测**, 必须板端验证 (见 §2.4.3)。 ★**v2.1 订正 (2026-11-23 · ISS-353): 该替代路线已被 ISS-263 取代 ⇒ 主路线 = rknn3-toolkit 1.2.0 + `target_platform='rk3572'` (config rc=0 [实测]); 「同代同架构」前提已被 ISS-250 官方反证**★ ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #14 — `SW/RKNN_BUILD_ENV_RECOVERY.md`

- **理由**: 构建环境恢复 §2.4 引述行: 依据降为历史
- **旧片段** (替换前, 须精确命中且唯一):

```
> ★**这些是"支持用 rk3576 target 转换"的**依据**, 不是"rk3572 = rk3576"的证据**。
```

- **新片段** (替换后):

```
> ★**这些是"支持用 rk3576 target 转换"的**依据**, 不是"rk3572 = rk3576"的证据**。 ★**v2.1 订正 (2026-11-23 · ISS-353): 这组依据属于【历史】—— 主路线已改为 rknn3-toolkit 1.2.0 + `target_platform='rk3572'`**★ ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

### 补丁 #15 — `SW/RKNN_BUILD_ENV_RECOVERY.md`

- **理由**: 构建环境恢复 §6 降级表 M1 行: 目标 target 改口径
- **旧片段** (替换前, 须精确命中且唯一):

```
★**改 M1 定义为"用 rk3576 target 重转 yolov5n"**, 转换成本 ≈ 0.5 人天 (本单已做完 80%)
```

- **新片段** (替换后):

```
★**改 M1 定义为"用 rk3576 target 重转 yolov5n"** (★v2.1 订正 2026-11-23 ISS-353: M1 的目标 target 已改为 rknn3-toolkit 1.2.0 + `target_platform='rk3572'`★), 转换成本 ≈ 0.5 人天 (本单已做完 80%) ★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★
```

## D. 应用方式

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
# ① 先 dry-run (只校验, 不改任何文件)
python3 logs/iss353/apply_caliber_dispositions.py
# ② 真改 (逐条原子写; 旧片段不唯一 ⇒ 整体中止)
python3 logs/iss353/apply_caliber_dispositions.py --apply
# ③ 复跑闸 (期望: 本单可处置 0 条 / 越权剩 2 条 [hw.yaml, 属 hw-lead 地界])
python3 SW/tools/check_rk3572_target_caliber.py
```
