# SW/RK3572_TARGET_COMPAT_V2.md — RK3572 目标兼容性 v2.0 (官方口径 + 可执行验证包)

> 版本: **v2.0** (2026-11-15) · owner: sw-lead · 对应 issue: **ISS-207** / ISS-155 (demo 头号卡点) / ISS-147 (P0-1)
> 上游 (**只读引用, 本单未改一字**): `SW/RK3572_TARGET_BOARD_VERIFY.md` (v1.0, 2026-11-06) · `SW/RKNN_BUILD_ENV_RECOVERY.md` (2026-11-02)
> 本单配套交付: `SW/tools/rk3572_target_smoke.sh` (板端验证包 = 降级 A+C) · `SW/tools/rk3572_model_rebuild.sh` (PC 侧重建 = 降级 B)
>
> ★**本单回答什么**: v1.0 把这条卡点写成「等一块能跑的板」。按老板 **2026-11-12 02:02** 新口径
> (外部依赖不许挂着当阻塞项), 本单把它改成三件**本机可交付**的东西:
> **① 官方口径自己查** · **② 板端到手 30 分钟跑完的验证包** · **③ PC 侧产物的可重建路径**。
> ⇒ **板端结论一律 [0数据]** (本机无板); 本机跑出来的标 [实测]; 官方页面抓到的标 [官网]。

---

## 0. 结论摘要 (结论先行)

| # | 命题 | 结论 | 证据等级 |
|---|---|---|---|
| 1 | ★**最新 rknn-toolkit2 版本号** | **v2.5.0** (发布 2026-10-20) —— **没有比它更新的版本** | **[官网]** |
| 2 | ★**v2.5.0 的合法 `target_platform` 列表含 `rk3572` 吗** | **不含**。官方 README 的 Support Platform 8 个系列里没有 RK3572; release notes 全文无 rk3572; 本机 2.3.2 官方库自打印的 11 项合法 target 里也没有 | **[官网] + [实测]** |
| 3 | ⇒ **"升级 toolkit 就有 rk3572 target" 这条路** | **不存在**。⇒ 只能 `target_platform='rk3576'` 转 | **[官网] + [实测]** |
| 4 | ★**RK3572 BSP runtime 认不认 rk3576-target 产物** | ★**官方无此口径** ⇒ 命题判 **(b)** ⇒ 只能标 **[0数据]**, 走降级 A/B/C | **[0数据]** (检索范围见 §3) |
| 5 | ★**本机转换链是死是活** | ★**活的** —— 修正 2026-11-15 21:4x 的判断: `conda` 不在 PATH ≠ 环境没了; `/home/yuewuya/miniconda3/envs/rknn/bin/python` 在, **rknn-toolkit2 2.3.2** 在 ⇒ 本单**已实跑出产物并落盘项目库** | **[实测]** |
| 6 | ★**v1.0 §2 产物清单** | **在本机已失效** (产物写在 `/tmp/rknn_bench/`, 会被清) ⇒ 本单已重建并落盘 `SW/artifacts/models/` + `.sha256` sidecar | **[实测]** |
| 7 | ★**卡点还剩什么** | 只剩一个**物理事实**: 板子不在本机 (板端结论 [0数据]); **"怎么验、怎么重建、怎么判 PASS/FAIL" 本单已全部固化成脚本** | **[实测]** |

★**一句话**: 官方口径查完了 —— **没有 rk3572 target, 官方也没写"rk3576-target 产物能在 RK3572 上跑"**;
但**验证包 + 重建路径本机已经跑通**, 板子一到手就是**一条命令出 PASS/FAIL**。

---

## 1. ① 查证表 (官方口径 · 每条: 结论 + 证据等级 + 出处 + 复算依据)

| # | 命题 | 结论 | 证据等级 | 出处 (URL / 章节) | 我的复算依据 |
|---|---|---|---|---|---|
| 1.1 | 最新 rknn-toolkit2 版本号 | **v2.5.0**, `published_at 2026-10-20T08:35:48Z`; 再往前是 v2.3.2 (2025-04-09) | **[官网]** | `https://api.github.com/repos/airockchip/rknn-toolkit2/releases?per_page=10` | `curl -sS "https://api.github.com/repos/airockchip/rknn-toolkit2/releases?per_page=1"` → tag_name |
| 1.2 | PyPI 上的最新版 | **2.5.0** (`release_url: .../rknn-toolkit2/2.5.0/`); 官方 README 自己也写 `Latest version:v2.5.0` | **[官网]** | `https://pypi.org/pypi/rknn-toolkit2/json` · `.../v2.5.0/README.md` | 抓 JSON 的 `info.release_url` / `info.version` |
| 1.3 | ★**v2.5.0 官方支持平台列表 (Support Platform)** | `RK3588 Series` / `RK3576 Series` / `RK3566-RK3568 Series` / `RK3562 Series` / `RV1103/RV1106` / `RV1103B/RV1106B` / `RV1126B` / `RK2118` —— **★没有 RK3572** | **[官网]** | `https://raw.githubusercontent.com/airockchip/rknn-toolkit2/v2.5.0/README.md` §Support Platform | 逐行读原文字符串, `rk3572` 出现 **0** 次 |
| 1.4 | ★**v2.5.0 release notes / CHANGELOG 有没有 rk3572** | **没有**。新增项只涉及: 模型加密、RV1126B/RK3562 的 mini-runtime、QAT 稀疏推理、算子扩充、RK2118 算子、内存泄漏修复 —— **全篇无 rk3572** | **[官网]** | GitHub release `v2.5.0` body + README §CHANGELOG | 全文检索 `rk3572` → 0 命中 |
| 1.5 | ★**2.3.2 官方库自身给出的合法 target 全集** | `['rk3566','rk3568','rk3588','rv1103','rv1106','rk3562','rk3576','rv1103b','rv1106b','rk2118','rv1126b']` —— **★没有 rk3572** | **[实测]** | 官方库自己的报错串 (`rknn_base.py` 打印 "valid values are [...]") | `RKNN(verbose=True).config(target_platform=None)` ⇒ 抛 ValueError 并打印全集 (本机 22:0x 复跑) |
| 1.6 | `config(target_platform='rk3572')` | `ValueError: Invalid target_platform 'rk3572'!` | **[实测]** | 本机 `rknn/api/rknn_base.py:896` | `/home/yuewuya/miniconda3/envs/rknn/bin/python -c "from rknn.api import RKNN; RKNN(verbose=False).config(target_platform='rk3572')"` |
| 1.7 | `config(target_platform='rk3576')` | **rc=0** (合法) | **[实测]** | 同上 | 同进程同参数换 `rk3576` |
| 1.8 | ★**2.5.0 那个 whl 里的合法 target 全集 (二进制取证)** | **本机取不到** —— PyPI whl 37.7 MB, 本机下载实测 6.6 KB/s, 20 分钟只下了 0.8 MB ⇒ 放弃; 用 1.3/1.4 的官方列表兜底 | **[0数据]** | — | 下载日志 `/tmp/iss207_wl.log` |
| 1.9 | 官方 **rknn_model_zoo** 支持平台 | `RK3562 / RK3566 / RK3568 / RK3576 / RK3588 / RV1126B` (+ limited `RV1103/RV1106`) —— **无 RK3572** | **[官网]** | `https://raw.githubusercontent.com/airockchip/rknn_model_zoo/master/README.md` | 同 1.3 的检索法 |
| 1.10 | 官方 **rknpu2** (runtime 仓, README 已注明迁到 `rknn-toolkit2/tree/master/rknpu2`) 支持平台 | `RK3566/RK3568` / `RK3588/RK3588S` / `RV1103/RV1106` / `RK3562` —— **无 RK3572** | **[官网]** | `https://raw.githubusercontent.com/airockchip/rknpu2/master/README.md` | 同上 |
| 1.11 | 官方文档目录里有没有 RK3572 专章 | `doc/EN` + `doc/CN` 共 12 个 PDF: `01 SDK 快速入门` / `02 SDK 开发指南` / `03 Toolkit Python API` / `04 Toolkit Lite Python API` / `05 Runtime C API` / `06 算子支持与约束` (另有 RK2118 与 RV1106/RV1103 两份快速入门) —— **★没有 RK3572 专章** | **[官网]** | `https://api.github.com/repos/airockchip/rknn-toolkit2/git/trees/master?recursive=1` | 树里 `doc/` 全量列出 |
| 1.12 | RK3572 这颗芯片存在吗 | 存在: 2026-05 发布, 8nm, 2×A73 + 6×A53, **4 TOPS NPU** (INT4/8/16, FP4/8/16, BF16, W4A16), Mali-G310 v2, Linux 6.12 BSP (Forlinx OK3572-C) | **[媒体]** | SBCwiki `sbcwiki.com/docs/soc-manufacturers/rockchip/rk3572` · linuxgizmos · Forlinx 官方产品页 `forlinx.net/single-board-computer/rk3572-dev-kit-ok3572-c-180.html` | 三家独立来源交叉, 数值一致 (4 TOPS) |
| 1.13 | ★**"RK3572 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2)" 是官方结论吗** | ★**不是**。官方 RKNN 支持平台表 **没有把 RK3572 列进去**, 官方文档也**没有**说它与 RK3576 同代。⇒ ISS-155 里这句是**我们自己的 [推算]**, 本单**没能升级成官方依据** | **[0数据]** | 反证见 1.3 / 1.9 / 1.10 / 1.11 | 检索全部官方面, 无正面表述 |
| 1.14 | ★**RK3572 BSP 的 `librknnrt` 认不认 rk3576-target 产物** | ★**官方无此口径** ⇒ 命题 **(b)** | **[0数据]** | 检索范围见 §3 | 同上 |
| 1.15 | ★**本机转换链实际可用性** | ★**可用**: `/home/yuewuya/miniconda3/envs/rknn/bin/python` (Python 3.10.22) + `rknn-toolkit2 2.3.2` + onnx 1.16.1 + numpy 1.26.4 + opencv-headless | **[实测]** | 本机 `pip list` | `/home/yuewuya/miniconda3/envs/rknn/bin/python -c "import importlib.metadata as m; print(m.version('rknn-toolkit2'))"` → 2.3.2 |
| 1.16 | ★**产物可重建性 (本机实跑)** | `rknn_bench.py convert --onnx yolov5n-sim.onnx` ⇒ rc=0, 产物 **4,989,367 B (4.76 MiB)**, load 0.13s + build(INT8) 25~26s, 校准 99 张, 量化 `w8a8/normal/channel`, `target_platform=rk3576` | **[实测]** | `/tmp/iss207_convert.log` | 本单实跑 (见 §6) |
| 1.17 | ★**PC 侧精度基线复现** | COCO val2017 **281 张** (有标注的) → `TP=494 FP=765 FN=1623` → **P=0.39237 R=0.23335 F1=0.29265** ⇒ 与 v1.0 §0-3 记录的 0.2927 **逐位一致** | **[实测]** | `/tmp/iss207_acc.log` | 本单实跑 `rknn_bench.py acc --images 300` |
| 1.18 | ★**`.rknn` 是否逐字节可复现** | ★**否**。同工具链 (2.3.2) + 同源 ONNX **连转三次 ⇒ 三个不同 sha256** (`1c5ff7ba…` / `d33689b9…` / `dec2e404…`), 但**字节数恒为 4,989,367 B**; 差异集中在文件 **2.75~3.0 MB 区段** (98,230 B ≈ 3.2%), 而 **PC 侧精度两次独立跑出完全相同的 F1=0.29265402843601895** ⇒ ★**数值口径可复现, 字节级不可复现** ⇒ **sha256 只能在"拷贝那一刻"生成并随产物落盘 (sidecar), 不能拿历史常量当身份锚** | **[实测]** | 见 §6.3 | 本单连跑三次重建脚本 + 两次 acc 步对比 |

---

## 2. ② 兼容矩阵 (最新版 × target_platform 列表 × 含 rk3572)

| toolkit 版本 | 发布日 | 官方 Support Platform (README) | 合法 `target_platform` 全集 | 含 `rk3572`? | `config('rk3572')` | 证据等级 |
|---|---|---|---|---|---|---|
| 2.2.0 / 2.3.0 | — | 同族列表 (8 系列) | 未逐版取证 | **否** | 上游实测 ValueError | [官网] + [实测·上游] |
| **2.3.2** | 2025-04-09 | 同族列表 (8 系列) | **11 项** (库自打印, 见 §1.5) | **否** | `ValueError: Invalid target_platform 'rk3572'!` | **[实测]** (本机 22:0x 复跑) |
| **2.5.0 (★最新)** | **2026-10-20** | RK3588 / RK3576 / RK3566-68 / RK3562 / RV1103-06 / RV1103B-06B / RV1126B / RK2118 —— **无 RK3572** | **[0数据]** (whl 二进制未取到, 见 §1.8) | **否** | 上游实测 ValueError; release notes + README 无 rk3572 | **[官网]** + [实测·上游] |
| 未来版本 | — | — | — | 只要官方 Support Platform 不加 RK3572 就还是否 | — | [推算] |

★**口径纪律落地**: "**最新版本号**" (v2.5.0, [官网]) 与 "**它的合法 target 列表**" (2.5.0 = [0数据] / 2.3.2 = [实测]) **分开写, 各标等级**;
★**新版本号 ≠ 支持 rk3572** —— 本单**没有**把"2.5.0 是最新"当成"2.5.0 支持 rk3572"来交卷。

★**持续监控 (一条命令, 官方层, 不需要任何人回复)**:

```bash
curl -sS "https://api.github.com/repos/airockchip/rknn-toolkit2/releases?per_page=3" \
  | grep -E '"tag_name"|"published_at"'
curl -sS "https://raw.githubusercontent.com/airockchip/rknn-toolkit2/master/README.md" \
  | grep -iA10 "Support Platform" | grep -i "rk3572"    # ★有输出 = 官方加支持了
```

---

## 3. ② "RK3572 BSP runtime 认不认 rk3576-target 产物" 的官方依据 / 无依据

**判定: (b) 官方无此口径 ⇒ [0数据] ⇒ 只能靠板端实测 (N1) 回答。**

### 3.1 检索范围 (全部官方面, 零外发)

| 面 | URL | 结果 |
|---|---|---|
| RKNN-Toolkit2 README (v2.5.0 + master) | `raw.githubusercontent.com/airockchip/rknn-toolkit2/{v2.5.0,master}/README.md` | 无 RK3572 |
| GitHub Releases (v2.5.0 body) | `api.github.com/repos/airockchip/rknn-toolkit2/releases` | 无 RK3572 |
| 官方文档目录 (12 个 PDF) | `api.github.com/.../git/trees/master?recursive=1` (`doc/CN`, `doc/EN`) | 无 RK3572 专章 |
| RKNN Model Zoo README | `raw.githubusercontent.com/airockchip/rknn_model_zoo/master/README.md` | 无 RK3572 |
| RKNPU2 (runtime/驱动仓) README | `raw.githubusercontent.com/airockchip/rknpu2/master/README.md` | 无 RK3572 |
| PyPI 包元数据 | `pypi.org/pypi/rknn-toolkit2/json` | 无 RK3572 |

### 3.2 为什么这个命题**在官方层不可能**被正面回答 (⇒ 只能实测)

> 官方**根本没有 `rk3572` 这个编译目标** ⇒ **不存在"官方为 RK3572 编译出来的 .rknn"**可以拿来对比
> ⇒ "rk3576-target 的产物能不能被 RK3572 的 runtime 接受" **在官方文档里没有对应条目**,
> **只可能由板端 `load_rknn` 的返回值回答** (= 判据 N1)。

⇒ 所以本单把这条写成: **转换工具链侧合法** (rk3576 是官方合法 target, [官网]) + **板端接受性未知** ([0数据]) ⇒ 风险 R1 保留, 但**它不再是"阻塞项"**, 因为验证包已经就绪 (降级 A/C)。

### 3.3 同代跨芯片复用的现有依据等级 (不许升级)

| 说法 | 现在是什么等级 | 本单能不能升级 |
|---|---|---|
| "RK3572 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2)" | **[推算]** (ISS-155 自推) | **不能** —— 官方无对应表述 (§1.13) |
| "4 TOPS NPU" | **[媒体]** (SBCwiki / linuxgizmos / Forlinx) | 媒体级, 官方产品页未直接引用 |
| "官方 RKNN 支持 RK3572" | **不存在此说法** | — |
| "官方 RKNN 不支持 RK3572" | **[官网]** (README Support Platform + Model Zoo + rknpu2 三处都没有) | ✔ 已坐实 |

---

## 4. ④ 与 v1.0 (`SW/RK3572_TARGET_BOARD_VERIFY.md`) 的逐条差异 (只报差异, **未改 v1.0 一个字**)

| # | v1.0 位置 | v1.0 说法 | v2.0 的实测/官方口径 | 差异性质 |
|---|---|---|---|---|
| D1 | §0-2 / §2 | 产物在 `/tmp/rknn_bench/`; "**产物必须在下板前先拷到项目库**" | ★**本机 `SW/artifacts/models/` 当时只有两个 ssd onnx** ⇒ v1.0 §2 清单**在本机已不可用**; 本单已重建 + 落盘 + `.sha256` sidecar | **补坑 (v1.0 自己写下的坑, 已修)** |
| D2 | §3 步骤 3 | 命令带 `--rknn ./xxx.rknn` 参数 | ★**`SW/tools/rknn_bench.py` 根本没有 `--rknn` 这个参数** ⇒ argparse 直接 rc=2 退出 | **修正 (命令不可执行)** |
| D3 | §3 步骤 3 | 打算在板端跑 `python3 SW/tools/rknn_bench.py acc` | ★**`rknn_bench.py` 顶部 `_ensure_env()` 强制要 rknn-toolkit2** (板端只有 lite2) ⇒ **板端跑不了这一步** | **修正 (板端路径不成立)** |
| D4 | §3 步骤 4 | "必须报 t_npu 与 t_sdk_total 两个数" | ★**lite2 只能给 `t_sdk_total`**; 纯 NPU 要 C API `RKNN_QUERY_PERF_DETAIL` ⇒ 验证包用 `--npu-ms` 显式传入, 没传就标 INDET | **补可采集方法** |
| D5 | §4 N3 | 通过线 `t_npu ≤ 13.30 ms` (无采集路径 ⇒ 不可判) | v2.0 加**可判口径**: `t_sdk_total ≤ 13.30 ⇒ PASS` (因为 `t_npu ≤ t_sdk_total`); `13.30 < t_sdk_total` ⇒ **INDET 而不是 FAIL** (不许用 SDK 总耗时冒充 NPU 耗时) | **收紧口径 + 防误判** |
| D6 | §4 | 5 条判定只写在文档里 | ★**固化成脚本判据**: `rk3572_target_smoke.sh` 输出 PASS/FAIL/INDET + 数值 + 失败原因 + `summary.json` | **新增 (降级 C)** |
| D7 | §1 P1~P6 | 6 条前置条件 (人工核对) | ★**脚本自动核对** P1~P6 (含 device-tree / librknnrt 版本 / lite2 / sha256 / COCO 数据集) | **自动化** |
| D8 | §0-1 / §2.3 | "升级 toolkit 就有 rk3572 这条路彻底不存在" (证据 = 本机实测) | ★**升级为官方口径**: README Support Platform + release notes + Model Zoo + rknpu2 四处官方面都没有 RK3572 | **证据等级升级 [实测] → [官网]+[实测]** |
| D9 | §6 | 卡点 = "需要老板/硬件侧解锁" | ★**按老板 2026-11-12 02:02**: 外部依赖不许挂着当阻塞项 ⇒ 卡点只剩"板子不在本机"这一物理事实, 且**怎么验已固化成一条命令** | **口径变更** |
| D10 | §3 步骤 0.3 | 要求记散热/频率/供电 (人工) | ★**固化成 N5**: 脚本自动读 `thermal_zone0` + `cpufreq` + `--power-note` | **自动化** |
| D11 | §2 | PC 基线 F1 = 0.2927 | ★**本机复跑仍是 0.29265** (TP=494 FP=765 FN=1623, 281 张) ⇒ 基线有效 | **复验通过** |
| D12 | §2 | 产物大小 4,989,367 B (2026-11-06) | ★**本机重建后字节数完全相同** (4,989,367 B) ⇒ 大小可复现; 但 **sha256 不可复现** (§1.18) ⇒ 身份锚改成"拷贝那一刻的 sidecar" | **新增口径** |

---

## 5. ③ 降级方案 (查不到时的必须项 —— 这次两条都没查到官方口径, 所以三个降级全上)

### 5.1 降级 A —— 自持验证包 (`SW/tools/rk3572_target_smoke.sh`)

★**"必须实测"变成"拿到任意一块 RK357x 板就能自动跑完"**:

1. **P1~P6 自动核对**: ①`/proc/device-tree/compatible` 含 `rk3572` ②`librknnrt.so` 版本 ③板端 `rknn-toolkit-lite2` ④产物在位+大小 ⑤COCO val2017 + `instances_val2017.json` ⑥**产物 sha256 == sidecar** (板端**不许重转**, 脚本里**没有任何** convert/build 路径)
2. **精度步**: 内置 lite2 评测器 (与 `SW/tools/rknn_bench.py` acc 步**同口径**: 逐类 IoU 贪心匹配, score_thr 0.3, nms_iou 0.45, eval_iou 0.5, 同一套 COCO 前 N 张; 解码用的 grid/anchor **已在本机对 ONNX initializer 逐位核对**)
3. **耗时采样**: 逐帧 `t_sdk_total` (min/avg/max/p90) + 可选纯 NPU (`--npu-ms`)
4. **输出**: N1~N5 逐条 **PASS / FAIL / INDET + 数值 + 失败原因**, 落 `summary.json` / `acc.json` / `acc.log`
5. ★**本机 `--dry-run` rc=0** (只做本地检查 + 打印板端将执行的每一条命令)

### 5.2 降级 B —— PC 侧一键重建 (`SW/tools/rk3572_model_rebuild.sh`)

`找 python (conda env / 系统 python / 新建 venv+pip) → 转 yolov5n@640 → **落盘 `SW/artifacts/models/`** → 写 `.sha256` sidecar → 与参考 sha 比对`
★**本机已实跑 rc=0**: 产物 `SW/artifacts/models/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn` (4,989,367 B) + `.sha256` sidecar + `.meta.json` (记录源权重 sha16 / 指纹 / target_platform)。

### 5.3 降级 C —— 判据固化 (5 条判据 = 脚本里的可执行判据, 不是文档里的一段话)

| 判据 | 机器判定 | 通过线 | 失败原因会打印什么 |
|---|---|---|---|
| **N1** | `load_rknn` ret + `init_runtime` ret | 都是 0 | ★"跨平台兼容命题被否" + 错误串落 `acc.log` |
| **N2** | acc 步 F1 | ≥ **0.2427** (= PC 基线 0.2927 − 0.05) | 掉多少 + 量化偏差结论 |
| **N3** | 纯 NPU 时间 (或 `t_sdk_total` 保守判) | `t_npu ≤ 13.30 ms` [推算] | `13.30 < t_sdk_total ≤ 20.33` ⇒ **INDET** + 要怎么取纯 NPU; `> 20.33` ⇒ 提示命中 **T2 翻案条件** |
| **N4** | 纯硬件 vs SDK 总耗时**分开报** | 两个数都有 | 缺纯 NPU ⇒ INDET, **不许合并成一个数** (SOUL.md 铁律) |
| **N5** | 散热/频率/供电已记录 | 三项都在证据里 | 缺 ⇒ N3 的数没有可比性 |

★**三种结局照旧** (v1.0 §4.1): ✅ 全过 ⇒ rk3576-target 路线成立 · ⚠️ N1 过但 N3 不行 ⇒ 命中 T2, 降 OD 负载 / 回 RK3576 · ❌ N1 不过 ⇒ 换 SoC 或找 RK3572 专用 BSP。

---

## 6. ⑥ 复现命令 (本机, 全部已实跑)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 官方口径自查 (零外发, 只 GET 官方页面)
curl -sS "https://api.github.com/repos/airockchip/rknn-toolkit2/releases?per_page=3" | grep -E '"tag_name"|"published_at"'
curl -sS "https://raw.githubusercontent.com/airockchip/rknn-toolkit2/v2.5.0/README.md" | grep -iA10 "Support Platform"
/home/yuewuya/miniconda3/envs/rknn/bin/python -c "
from rknn.api import RKNN
try: RKNN(verbose=False).config(target_platform='rk3572', quantized_dtype='w8a8')
except Exception as e: print('rk3572 ->', e)          # ★Invalid target_platform
print('rk3576 ->', RKNN(verbose=False).config(target_platform='rk3576', quantized_dtype='w8a8'))"

# ② 板端验证包 (本机无板 ⇒ --dry-run rc=0)
bash SW/tools/rk3572_target_smoke.sh --dry-run

# ③ PC 侧一键重建 (本机已实跑 rc=0)
bash SW/tools/rk3572_model_rebuild.sh --dry-run     # 只打印命令
bash SW/tools/rk3572_model_rebuild.sh                # 真跑: 转 → 落盘 → sha256
bash SW/tools/rk3572_model_rebuild.sh --with-acc     # 顺带复现 F1 基线

# ④ 板子到手后 (在板上, 项目根目录)
bash SW/tools/rk3572_target_smoke.sh \
  --artifact ./yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn \
  --expect-sha256 $(awk '{print $1}' yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn.sha256) \
  --images 300 --out ./evidence/ISS207_$(date +%Y%m%d) --power-note "<供电方式>"
```

### 6.3 本单实跑记录 ([实测], 2026-11-15)

| 项 | 值 |
|---|---|
| 转换 | rc=0 · 产物 4,989,367 B (4.76 MiB) · load 0.13 s + build(INT8) 25~26 s · 校准 99 张 · `w8a8/normal/channel` · `target_platform=rk3576` |
| 落盘 | `SW/artifacts/models/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn` (+ `.sha256` + `.meta.json`) |
| PC 精度 | 281 张 · TP=494 FP=765 FN=1623 · **P=0.39237 R=0.23335 F1=0.29265** (与 v1.0 基线逐位一致) |
| ★可复现性 | 同 2.3.2 **连转三次** ⇒ 三个 sha256 (`1c5ff7ba…`/`d33689b9…`/`dec2e404…`), **字节数恒为 4,989,367 B**; 差异集中在 2.75~3.0 MB 区段 (98,230 B ≈ 3.2%); **两次独立 acc 步 F1 完全相同 (0.29265402843601895)** ⇒ 数值可复现 / 字节不可复现 ⇒ 身份锚 = 拷贝那一刻的 sidecar |
| 板端 | **[0数据]** —— 本机无板, 未跑过 1 次 |
| ★验证包鲁棒性自测 | 在**非板子**的本机上跑实跑模式 (不带 `--dry-run`) ⇒ P1/P2/P3 判 FAIL 并打印原因, N1~N3 判 INDET, `summary.json` 正常落盘, **rc=1** (不假装通过) ⇒ **板端判定逻辑可执行** |

---

## 7. ⑦ 边界 (本单做了什么 / 没做什么)

**没做** (纪律):
- ★**没外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 全部官方信息**自己 GET 官方页面**; 查不到的标 [0数据] + 写降级方案 ⇒ **没有"等原厂回信"这个选项**。
- ★**没改**: `SW/RK3572_TARGET_BOARD_VERIFY.md` (只引用 + §4 逐条差异) · `SW/RKNN_BUILD_ENV_RECOVERY.md` (只引用) · `SW/RKNN_BENCH.md` · `SW/tools/rknn_bench.py` · `SW/tools/timing_check.py` · `SW/ISP_CAPABILITY_RESEARCH.{md,json}` · `SW/tools/isp_budget_solve.py` · `HW/**` (含 `HW/POWER_BUDGET_V3.md`、网表、板、原理图) · `state/gen_*.py` · `state/outbox/**` · `PROJECT_TRACKER.md` §0 · `state/issue_log.yaml` · **别人的分片**。
- ★**没碰 PCB 布线 / 布局** (老板 2026-11-11 10:07 主线: 先原理图)。
- ★**没写任何板端结论为 [实测]** —— 本机无板, 板端一律 [0数据]; [实测] 只用于本机实跑出来的东西 (dry-run rc、转换、精度、sha256、官方库自打印的 target 列表)。

**本单新增文件** (全部新建, 无覆盖):

| 文件 | 类型 | 说明 |
|---|---|---|
| `SW/RK3572_TARGET_COMPAT_V2.md` | 文档 | 本文件 (官方口径 + 兼容矩阵 + 差异 + 降级 + 复现) |
| `SW/tools/rk3572_target_smoke.sh` | 工具 | 板端一次性验证包 (降级 A + C), `--dry-run` rc=0 |
| `SW/tools/rk3572_model_rebuild.sh` | 工具 | PC 侧一键重建 (降级 B), `--dry-run` rc=0 |
| `SW/artifacts/models/*.rknn` (+ `.sha256` / `.meta.json`) | 产物 | 重建出来的 yolov5n heads INT8 产物 (落项目库, 不留 /tmp) |
| `HANDOFF/2026-11-15_sw-lead_ISS207_rk3572target与验证包.md` | 交接单 | ≤25 行交卷报告 |

**残留风险 (未消除, 但不再是"卡点")**:
- **R1** 板端 `load_rknn` 是否接受 rk3576-target 产物 ⇒ **[0数据]**, 待板子 (验证包已就绪: `bash SW/tools/rk3572_target_smoke.sh` 一条命令出 PASS/FAIL)。
- **R2** 若 R1 为否 ⇒ 出路三条 (RK3576 载板 / RK3572 模组厂一手 BSP / CPU 推理), 代价见 v1.0 §4.1 —— **本单不预判, 不替硬件侧决策**。

> **本单纪律声明**: 本单**未联系任何供应商**; **未下单**; **未修改**上表以外任何既有文件;
> 板端结果一律 **[0数据]**; 所有本机数字标 **[实测]** 并给复现命令; 所有官方页面抓取标 **[官网]** 并给 URL。
