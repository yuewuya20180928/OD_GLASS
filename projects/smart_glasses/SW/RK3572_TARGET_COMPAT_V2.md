# SW/RK3572_TARGET_COMPAT_V2.md — RK3572 目标兼容性 v2.0 (官方口径 + 可执行验证包)

> 版本: **v2.0** (2026-11-15) · ★**v2.1 追加 (2026-11-23 · ISS-353) ⇒ 见 §8**★ · owner: sw-lead · 对应 issue: **ISS-207** / ISS-155 (demo 头号卡点 · ★该定位是否降级 = 交 main 裁★) / ISS-147 (P0-1)
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
| 3 | ⇒ **"升级 toolkit 就有 rk3572 target" 这条路** | ★**v2.1 订正 (2026-11-23 · ISS-353): 「不存在 ⇒ 只能 `target_platform='rk3576'` 转」已被取代** —— ★**toolkit2 (2.3.2 / 2.5.0) 不支持 rk3572 target [官网]+[实测] ⇒ 转换链要用 rknn3-toolkit 1.2.0 (其 `config(target_platform='rk3572')` rc=0 [实测])**★ · ★**已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用★** | **[官网] + [实测]** |
| 4 | ★**RK3572 BSP runtime 认不认 rk3572-target / rk3576-target 产物** | ★**官方无此口径** ⇒ 命题判 **(b)** ⇒ 只能标 **[0数据]**, 走降级 A/B/C (★v2.1 订正: 主路线已改为 rknn3-toolkit 1.2.0 的 rk3572-target ⇒ 板端要验的是 rk3572-target 产物; rk3576-target 已降为次要路线①★) · ★**已被 ISS-353 (2026-11-23) 订正·本条 [0数据] 判定不变·原句保留作历史留档**★ | **[0数据]** (检索范围见 §3) |
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

> 官方 rknn-toolkit2 侧**根本没有 `rk3572` 这个编译目标** ⇒ **不存在"官方用 toolkit2 为 RK3572 编译出来的 .rknn"**可以拿来对比 · ★**已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用**★
> ★**v2.1 订正 (2026-11-23 · ISS-353)**: ★官方 **rknn3-toolkit 1.2.0 侧有** `rk3572` 编译目标 (README「Supported Platforms: RK1820 / RK1828 / RK3572」[官网] · CHANGELOG V1.0.4「Added RK3572 platform support (Beta)」[官网]) ⇒ 「官方没有 RK3572 的编译目标」这句**只对 toolkit2 家族成立**★ (★官方 model zoo 仍无现成 .rknn 可对比, 这条不变 [0数据]★) · ★**已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·本条保留作历史留档·结论不再引用**★
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

### 5.4 ★追加 (ISS-263 · 2026-11-17 · 路线② `rknn3-toolkit 1.2.0` 实测栏)★

★**本段是追加, §5.1~§5.3 一个字没删没改** ★ ⇒ ★**§5.3 的 N1~N5 判据原样继续有效, 本段只是把路线② (换用官方 rknn3-toolkit 1.2.0 + `target_platform='rk3572'`) 的实测结果填进来** ★

| 必答项 (本单口径) | 实测结果 | 等级 |
|---|---|---|
| ★**装上了没有** ★ | ★**装上了**: 独立 conda env `/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22 / pip 26.3), `rknn3-toolkit 1.2.0` (VERSION file = rknn3-toolkit 1.2.0, dist version = 1.2.0) · ★**toolkit2 2.3.2 旧环境 `/home/yuewuya/miniconda3/envs/rknn` 装前装后 pip list 逐行相同 ⇒ 未污染** ★ | ★[实测] ★ |
| ★**config 过了没有** ★ | ★**过了**: `config(target_platform='rk3572')` ⇒ `CONFIG_OK target=rk3572 elapsed=0.019s` (rc=0) · ★**反向自证: 错 target `rk3576` ⇒ `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ⇒ target 参数真被读了** ★ | ★[实测] ★ |
| ★**转换耗时 3 次读数** ★ | ★**`t_total` = 33.389 / 34.108 / 41.672 s ⇒ min 33.389 / avg 36.390 / max 41.672 s (n=3, target_platform=rk3572)** ★ · 3 次 `rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0` · 产物 249360 B, md5 `97a34fff0b855b92681f26627dba5354` (三次逐字节一致) | ★[实测] ★ |
| ★**板端仍是 [0数据]** ★ | ★★**[0数据] —— 仍是 0** ★★: `init_runtime(target='rk3572', core_mask=RKNN3_NPU_CORE_0)` ⇒ rc=**-1**, SDK 原文 `RKNN3 init failed. error code: RKNN3_ERR_DEVICE_UNAVAILABLE` + `adb: unable to connect for root: no devices/emulators found`; `list_devices() = []` ⇒ **本机 0 台 RK3572 设备** ⇒ ★**§5.3 的 N1 (load_rknn ret + init_runtime ret 都=0) 仍判不了, 板端接受性一个数都没有** ★ | ★[0数据] ★ |

★**★往返自证 (★本单补, 对 §5.3 的 N1 是主机侧的一半★)** ★:
★**`load_rknn` 真签名 = `load_rknn(self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)`** ★ ⇒ ★**`export_rknn` 一次产出 `.rknn` + 同名 `.weight` 两个文件 (本单实测 `.rknn` 249360 B + `.weight` 1960448 B), 只传 `model_path` 会报 `TypeError: RKNN.load_rknn() missing 1 required positional argument: 'weight_path'`** ★
⇒ ★**按真签名配上传回 ⇒ `rc_load_rknn = 0` (heads + 整模型两个产物都是), 再 `export_rknn` 出来 md5 与原文件完全一致 (`REEXPORT_MD5_MATCH_ORIG = True`)** ★
★**⇒ 路线②的主机侧结论 = 「转换链已通」 (config 过 / 3 次 rc=0 / 产物可复现 / 能读回来); 板端那一半仍是 [0数据]** ★

★**本段口径纪律**: ★**上面的 33.389~41.672 s 是「主机侧一次 ONNX→.rknn 转换耗时」, 不是板端 e2e 延迟, 不许与 §5.3 的 N3 (`t_npu ≤ 13.30 ms` / `t_sdk_total ≤ 20.33 ms`) 混用或直接比大小** ★ (★SOUL.md: 跨口径对比必须统一, 否则结论是错的★)

### 5.5 ★追加 (ISS-263 第4趟 · 2026-11-17 · 独立复验 + 转换耗时口径订正)★

★**本段是追加, §5.1~§5.4 一个字没删没改** ★ ⇒ ★**§5.4 的结论方向不变 (转换链已通 / 板端 [0数据]), 本段只做两件事: ①把上一趟的结论独立复跑一遍 ②把「转换耗时」这个数的隐含前提补出来** ★

★**★订正 (★本段唯一的口径变化★)** ★:

★**§5.4 那行「转换耗时 3 次读数 = 33.389 / 34.108 / 41.672 s」是真读数, 但它带着一个 §5.4 没写出来的前提: 【当时机器闲】** ★
★**第4趟把这条拆成 3 个会话 × 共 9 次读数 (★故意先并发争抢再干净重跑, 这样才能定位变量★)** ★:

| 会话 | 时刻 | 主机条件 | 3 次 t_total (s) | min / avg / max (s) | 产物 md5 |
|---|---|---|---|---|---|
| ★A (第3趟 · 原读数) ★ | 02:51 | 轻负载 (无并发) | 33.389 / 34.108 / 41.672 | 33.389 / 36.390 / 41.672 | `97a34fff…5354` |
| ★B (第4趟 · 故意争抢) ★ | 05:13 | ★**并发跑了门禁脚本 ⇒ 抢 CPU** ★ | 68.810 / 51.040 / 59.832 | 51.040 / 59.894 / 68.810 | `97a34fff…5354` |
| ★C (第4趟 · 干净重跑) ★ | 05:16 | ★**机器上只有 openclaw gateway 常驻, 无自己的并发** ★ | 49.148 / 54.950 / 44.050 | ★**44.050 / 49.383 / 54.950** ★ | `97a34fff…5354` |
| ★**9 次全体** ★ | — | — | — | ★**min 33.389 / avg 48.555 / max 68.810** ★ | ★**9/9 逐字节相同** ★ |

★**归因**: ★**逐次算过 t_build / t_total = 98.9~99.8% ⇒ 耗时几乎全在 INT8 校准 + 图优化 (纯 CPU-bound)** ★; ★**会话B 比 会话C 慢 1.10~1.56× 而产物 md5 一模一样 ⇒ 变量是主机 CPU, 不是工具链不确定性** ★
★**⇒ 引用纪律 (★本段新增★)**: ★**报「一次转换多少秒」必须同时给出「当时主机负载」; 保守引用取会话C (干净口径 44.050 / 49.383 / 54.950 s), 理论下界取会话A (33.389 / 36.390 / 41.672 s); 不许单报一个数当稳定值** ★

★**复验结果 (★本趟本机实跑, 13/14 条与上一趟一字不差★)** ★:

| 必答项 | 本趟独立复跑结果 | 等级 |
|---|---|---|
| ★**装上了没有** ★ | ★**装上了**: `VERSION file = rknn3-toolkit 1.2.0` / `dist version = 1.2.0` · 独立 env `/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22) · wheel md5 重算 = `a972e03af94fd18e21f026558735b28d` (102657410 B, 与官方发布页同) · toolkit2 旧 env `rknn-toolkit2 2.3.2` / `numpy 1.26.4` / `onnx 1.16.1` 与基线逐行相同 ⇒ 未污染** ★ | ★[实测] ★ |
| ★**config 过了没有** ★ | ★**过了**: `CONFIG_OK target=rk3572 elapsed=0.018s` (rc=0) · ★**反向自证: 错 target `rk3576` ⇒ 同一句 `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` (一字不差) ⇒ target 参数真被读了** ★ | ★[实测] ★ |
| ★**转换耗时 3 次读数** ★ | ★**§5.5 开头那张表 = 9 次读数 (3 会话) ; 引用口径见上** ★ · 9 次全部 `rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0` · 产物 249360 B, md5 `97a34fff0b855b92681f26627dba5354` ★**跨 3 会话 9/9 逐字节一致** ★ | ★[实测] ★ |
| ★**往返自证** ★ | ★**`load_rknn(model_path, weight_path)` rc=0 ×2 (0.002s / 0.004s) + `REEXPORT_MD5_MATCH_ORIG = True` ×2 (heads 249360 B + 整模型 339992 B)** ★ | ★[实测] ★ |
| ★**板端仍是 [0数据]** ★ | ★★**[0数据] —— 仍是 0** ★★: `init_runtime(target='rk3572', core_mask=RKNN3_NPU_CORE_0)` ⇒ rc=**-1**, SDK 原文 `RKNN3 init failed. error code: RKNN3_ERR_DEVICE_UNAVAILABLE` + `adb: unable to connect for root: no devices/emulators found`; `list_devices() = []` ⇒ ★**§5.3 的 N1 仍判不了, 板端接受性一个数都没有** ★ | ★[0数据] ★ |
| ★**门禁** ★ | ★**`check_demo_panel_spec.py` G1_RC=0 (R1~R7 全过) · `timing_check.py` G2_RC=0 (SELFTEST 71/71) · `state/merge.py` + `state/gate_check.py` G3_MERGE_RC=0 / G3_GATE_RC=0, 【Q1】18/18, 【Q2】3/3 · 受保护 5 件 md5 逐字节不变** ★ | ★[实测] ★ |

★**本段口径纪律 (★补 §5.4 那句纪律★)**: ★**① 上面的秒数是「主机侧一次 ONNX→.rknn 转换耗时」, 不是板端 e2e 延迟, 不许与 §5.3 的 N3 (`t_npu ≤ 13.30 ms` / `t_sdk_total ≤ 20.33 ms`) 混用或直接比大小** ★
★**② 本趟新增: 该耗时是 CPU-bound 量 (t_build 占 98.9~99.8%), 引用时必须带「当时主机负载」这个前提** ★
★**③ 板端结论本段一个字没放宽: 转换链已通 ≠ RK3572 板端能跑** ★

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

### 6.4 ★追加 (ISS-263 · 2026-11-17 · 路线② `rknn3-toolkit 1.2.0` 实跑记录)★

★**本段是追加, §6.3 原表一个单元格没删没改** ★

| 项 | 值 |
|---|---|
| 装环境 | 独立 conda env `/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22 / pip 26.3) · `rknn3-toolkit 1.2.0` · numpy 2.2.6 · torch 2.4.0+cpu · onnx 1.23.2 · onnxruntime 1.23.2 · ★**toolkit2 旧 env `/home/yuewuya/miniconda3/envs/rknn` (rknn-toolkit2 2.3.2) 未被污染** ★ |
| wheel | 官方 `rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl` 102,657,410 B · md5 `a972e03af94fd18e21f026558735b28d` (拼装后本机重算一致 ⇒ 校验过才装) · 7 路 range 并发 + 断点续传, 00:50:29→01:11:03 拉完 (≈20.6 min, 平均 ≈83 KB/s) |
| ★**config** ★ | ★**`config(target_platform='rk3572')` ⇒ rc=0, `CONFIG_OK target=rk3572 elapsed=0.019s`** ★ · ★**反向自证 `rk3576` ⇒ `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572`** ★ |
| ★**转换 (3 次, target_platform=rk3572)** ★ | ★**`t_total` = 33.389 / 34.108 / 41.672 s ⇒ min 33.389 / avg 36.390 / max 41.672 s** ★ · 3 次全 `rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0` · 产物 `yolov5n_heads_int8_rk3572_run{1,2,3}.rknn` = **249360 B · md5 `97a34fff0b855b92681f26627dba5354` (三次逐字节一致)** ★ |
| 整模型 (yolov5s@640) | `yolov5s_full_int8_rk3572.rknn` = 339992 B · md5 `e8927025d8d0494a1a949802bbac7a1f` (+ 同名 `.weight` 7353856 B) · t_build 73.924 s / t_total 74.314 s |
| ★**往返自证** ★ | ★**`load_rknn(model_path, weight_path)` ⇒ rc=0 (两个产物都是) · 再 `export_rknn` md5 与原文件完全一致 (`REEXPORT_MD5_MATCH_ORIG = True`)** ★ · ★**真签名 `load_rknn(self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)`** ★ |
| ★**板端** ★ | ★★**[0数据] —— 仍是 0** ★★: `init_runtime(target='rk3572', core_mask=RKNN3_NPU_CORE_0)` ⇒ rc=**-1** / `RKNN3_ERR_DEVICE_UNAVAILABLE` / `adb: no devices/emulators found` / `list_devices() = []` |
| 门禁 | `check_demo_panel_spec.py` ⇒ G1_RC=0 (R1~R7 全过) · `timing_check.py` ⇒ G2_RC=0 (SELFTEST 71/71) · `state/merge.py` + `state/gate_check.py` ⇒ G3_MERGE_RC=0 / G3_GATE_RC=0 · 受保护 5 件 md5 装前=装后=交卷复测 三处逐字节一致 |
| 原始日志 | `logs/iss263/` 11 件: `rknn3_download.log` · `install.log` · `install_step2.log` · `install_step2b.log` · `baseline_env.log` · `config_probe.log` · `convert_rk3572_probe.log` · `convert_rk3572_3runs.log` · `extra_probe.log` · `gates.log` · `roundtrip_probe.log` |
| 交卷单 | `HANDOFF/2026-11-17_sw-lead_ISS263_rknn3_toolkit安装实测与rk3572转换.md` |

★**复现命令 (ISS-263 追加, 与 §6 的 ①②③④ 并列)** ★:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# 装好后的 env 直接可用 (★不重下 wheel / 不重装★)
/home/yuewuya/miniconda3/envs/rknn3/bin/python -c "from rknn.api import RKNN; print('rknn3-toolkit 1.2.0 ok')"
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_config_probe.py       # ⇒ rk3572 rc=0 且 rk3576 报错
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_roundtrip_probe.py   # ⇒ 往返自证 + 板端不可达证据
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_rknn3_convert.py    # ⇒ 3 次转换读数
bash SW/tools/iss263_gates.sh                                                      # ⇒ G1/G2/G3 + 受保护 5 件 md5
```

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

---

### 6.5 ★追加 (ISS-263 第4趟 · 2026-11-17 · 独立复验的复现命令与原始日志落点)★

★**本段是追加, §6.1~§6.4 一个字没删没改** ★

★**本趟新落盘的原始日志 (★`logs/iss263/` 下, 零转录误差★)** ★:

| 文件 | 内容 |
|---|---|
| `logs/iss263/config_probe_r3.log` | ★config 正/反向自证复跑 (rk3572 rc=0 / 0.018s · rk3576 ValueError)★ |
| `logs/iss263/roundtrip_probe_r3.log` | ★往返自证复跑 (rc_load_rknn=0 ×2 · REEXPORT_MD5_MATCH_ORIG=True ×2 · 板端 rc=-1 · list_devices=[])★ |
| `logs/iss263/convert_rk3572_3runs_r3.log` | ★转换会话B (争抢口径) 3 次读数★ |
| `logs/iss263/convert_rk3572_3runs_r3_clean.log` | ★转换会话C (干净口径) 3 次读数 ★ |
| `logs/iss263/gates_r3.log` | ★门禁复跑 (G1/G2/G3 rc + 受保护 5 件 md5 + G5/G6 pip list)★ |
| `logs/iss263/gate_full_r3.log` | ★`gate_check.py` 全量输出 (Q1 18/18 · Q2 3/3 · Q6 通过)★ |

★**复现命令 (★第4趟实际敲过的★)** ★:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① config 正/反向自证 (⇒ config_probe_r3.log)
./../../miniconda3/envs/rknn3/bin/python SW/tools/iss263_config_probe.py
# ② 往返自证 + 板端探测 (⇒ roundtrip_probe_r3.log)
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_roundtrip_probe.py
# ③ 转换 3 次 (⇒ convert_rk3572_3runs_r3_clean.log; ★测耗时时请确保机器上没有别的重活★)
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_rknn3_convert.py
# ④ 门禁 (⇒ gates_r3.log + gate_full_r3.log)
bash SW/tools/iss263_gates.sh
python3 state/merge.py && python3 state/gate_check.py
```

★**交卷单**: `HANDOFF/2026-11-17_sw-lead_ISS263_rknn3_toolkit安装实测与rk3572转换.md` (★§4 是第4趟的独立复验记录, 含 3 会话 × 9 读数的耗时口径订正★)


---

## 8. ★v2.1 (2026-11-23 · ISS-353)★ — 目标口径清账 (★追加段, §0~§7 一个字没删没改★; ★本段即 sw-lead 分片 refs 里说的「§7」, 因老文件本身已有一节「§7 ⑦ 边界」⇒ 追加段顺延为 §8★)

> ★**本段是追加** ★: §0~§6 (含 ISS-263 的 §5.4 / §6.5 追加段) **零删除**;
> 本单只**改写 §0 摘要表第 3/4 行与 §3.2 一行** (★这三行被闸点名, 原文保留 + 追加订正标记★),
> 其余一个字没动。★**闸**: `SW/tools/check_rk3572_target_caliber.py` (只读, 带 `--selftest` 反向用例)。

### 8.1 ★当前真值三句 (★机器读分片时不会去看上下文 ⇒ 这三句必须自足★)★

| # | 命题 | 当前真值 | 证据等级 |
|---|---|---|---|
| ① | **toolkit2 (2.3.2 / 2.5.0) 支不支持 rk3572 target** | ★**不支持** —— 官方 rknn-toolkit2 README「Support Platform」8 个系列 (RK3588 / RK3576 / RK3566-68 / RK3562 / RV1103-06 / RV1103B-06B / RV1126B / RK2118) **无 RK3572**; 本机 2.3.2 库自打印 11 项合法 target **无 rk3572**; `config(target_platform='rk3572')` 抛 `ValueError` ⇒ ★**所以转换链要用 rknn3-toolkit 1.2.0**★ | ★**[官网] + [实测]**★ |
| ② | **rknn3-toolkit 1.2.0 支不支持 `target_platform='rk3572'`** | ★**支持** —— 官方 rknn3-toolkit README「Supported Platforms: RK1820 / RK1828 / RK3572」+「Non-coprocessor mode (RK3572): The NPU is integrated inside the SoC」; CHANGELOG V1.0.4「Added RK3572 platform support (Beta)」; 本机 `config(target_platform='rk3572')` **rc=0**, 反向 `rk3576` 抛 `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ⇒ ★**转换链这一环已通** (不是"应该行": 实测 rc=0 + 产物逐字节可复现)★ | ★**[官网] + [实测]**★ |
| ③ | **板端 (RK3572) 接受性** | ★**仍 [0数据]** —— 本机 0 台 RK3572 设备 (`list_devices()=[]` · `init_runtime` rc=**-1**); 目标板 192.168.2.5 ping 100% 丢包 + ARP `INCOMPLETE` ⇒ ★**降级方案 = 板到手一条命令出 PASS/FAIL** (`SW/tools/rk3572_rknn3_board_smoke.sh`) ⇒ ★**板不来 ⇒ demo 路线【不被这条卡住】, 卡的是"验收何时做", 不是"能不能做"**★ | ★**[0数据]**★ |

★**一句话口径 (给搜索/给机器)**:
`rk3572 ⇒ 转换链走 rknn3-toolkit 1.2.0 + target_platform='rk3572' [实测]; 板端接受性 [0数据] ⇒ 板到手一条命令出 PASS/FAIL`

### 8.2 本单复跑读数 (★2026-11-23 04:5x · 自跑 · 原始日志见 logs/iss353/★)

| 项 | 读数 | 落盘 |
|---|---|---|
| `config(target_platform='rk3572')` (rknn3-toolkit 1.2.0) | ★**rc=0** · elapsed 0.015 s★ | `logs/iss353/config_probe_rknn3_rerun.log` |
| `config(target_platform='rk3576')` (反向自证) | ★**抛 `ValueError: Unsupported target_platform 'rk3576'`** (报错串里**含 rk3572** ⇒ target 参数真被读了)★ | 同上 |
| 转换 1 次 (`target_platform='rk3572'`) | ★**rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0** · `t_total=51.445 s` (cfg 0.014 / load 0.238 / build 51.174 / export 0.019) · 产物 **249,360 B** · md5 **`97a34fff0b855b92681f26627dba5354`** (与 ISS-263 三次逐字节一致)★ | `logs/iss353/convert_rk3572_rerun.log` |
| 板端不可达复证 | ★`list_devices()=[]` · `init_runtime` rc=**-1** · 192.168.2.5 ping 100% 丢包 · ARP `INCOMPLETE` ⇒ 板端接受性仍 **[0数据]**★ | `logs/iss353/board_unreachable_rerun.log` |
| 官方口径复证 (自跑 curl, 只 GET 官方 raw, 零外发) | ★rknn-toolkit2 README「Support Platform」无 RK3572 · rknn3-toolkit README「Supported Platforms」含 RK3572 · CHANGELOG V1.0.4「Added RK3572 platform support (Beta)」· rknn3_model_test_demo README: **RK3572 = `librknn3_api.so` + `librknn3_api_native.so`**, RK3576/RK3588 = `librknn3_api.so` + `librknn3_api_rkcp.so` ⇒ ★官方把两者分成两条 runtime, 无互换表述**★ | `logs/iss353/official/` + `logs/iss353/official_lookup_rerun.log` |

### 8.3 ★官方层: RK3572 与 RK3576 的关系 (★官方无互换表述 ⇒ 跨芯片接受性只能标 [0数据]★)★

| 面 | 官方原文 (★2026-11-23 本单实抓, 见 `logs/iss353/official/`★) | 等级 |
|---|---|---|
| rknn3-toolkit README · Supported Platforms | `RK1820` / `RK1828` / **`RK3572`** | **[官网]** |
| rknn3-toolkit README · Deployment Modes | `Non-coprocessor mode (RK3572): The NPU is integrated inside the SoC; models run directly on the board.` | **[官网]** |
| rknn3-toolkit README · Note | `For RK3588/RK3576/... series ... please refer to: https://github.com/airockchip/rknn-toolkit2` ⇒ ★RK3576 归 toolkit2 家族, RK3572 归 RKNN3 家族★ | **[官网]** |
| rknn3_model_test_demo README · Libraries | `RK3576 / RK3588: librknn3_api.so + librknn3_api_rkcp.so` / `RK3572: librknn3_api.so + librknn3_api_native.so` ⇒ ★**两条 runtime, 官方无互换表述**★ | **[官网]** |
| rknn-toolkit2 README · Support Platform | 8 系列, **无 RK3572** ⇒ ★「toolkit2 不支持 rk3572」在官方层成立★ | **[官网]** |
| rknn3-toolkit CHANGELOG | V1.0.4 `Added RK3572 platform support (Beta)` · V1.2.0 `Added MatMul APIs for RK3572` / `Improved LLM support on RK3572` | **[官网]** |

⇒ ★**结论**: 跨芯片接受性 (「rk3576-target 的 .rknn 能不能在 RK3572 上跑」) 官方层 **[0数据]**,
★**唯一能回答它的是板端 N1** (`load_rknn` + `init_runtime` 返回值) ⇒ 走 §8.4 降级 A/B/C。

### 8.4 ★板端依赖降级 A / B / C (★不许只写"等板子"★)★

| 档 | 触发条件 | 动作 | 判据 | 代价 |
|---|---|---|---|---|
| ★**降级 A (主)** ★ | 板到手 | ★**一条命令**: `bash SW/tools/rk3572_rknn3_board_smoke.sh --rknn <x.rknn> --weight <x.weight> --expect-sha256 <sha> --expect-weight-sha256 <sha> --power-note "<供电>" --out ./evidence/`★ (★本机 `--dry-run` rc=0 已验★) | ★**N1** `load_rknn`+`init_runtime` 都 =0 · ★**N2** 精度不塌 (对照 `SW/RKNN_BENCH.md` §3.2.2 的 PC 基线) · ★**N3** NPU 耗时对得上 `HW/e2e_budget_rk3572.py` 的预算 (★纯硬件耗时与 SDK 总耗时**分开报**, SOUL.md 铁律★) · ★**N4** 纯 NPU 耗时用 C API `RKNN_QUERY_PERF_DETAIL` 取, 取不到判 INDET 不许顶替 · ★**N5** 散热/频率/供电已记录 | 板到手 + 一次板端作业 (★**0 采购: 不买板, 用手上板 / demo 板 / 借板★**) |
| ★**降级 B** ★ | 板不来 (★当前状态★) | ★**demo 阶段不停** —— 用 rknn3-toolkit 产物继续推 PC 侧链路 (转换 rc=0 / 产物 249,360 B / md5 逐字节可复现 已在本单坐实); ★**板端验收登记为「待板」, 不是「待外部回复」** (★零外发, 不许发信/询价/问询★) | 转换链本机可复现 (已过) | ★**残留**: 板端 N1~N5 一个数都没有 ⇒ 该项在台账里**只能是 [0数据]**, 不许写成"应该没问题" |
| ★**降级 C** ★ | 板端拒收 (假设, N1 = FAIL) | ★**三档 (只列代价与启用条件, 不替老板拍)** ★**C1** 查板端 runtime / rkaiq 有无 rk3572 专用编译 (官方 README 已把 RK3572 单列为 `librknn3_api_native.so` ⇒ 优先查这条) → 代价 **板端软件作业, 0 元** · ★**C2** 换 SoC (RK3576 载板) → 代价 **改板 + 改固件 + 重转 + 重验 (人天级)** · ★**C3** CPU 推理兜底 (ONNXRuntime) → 代价 **性能不达标 (端到端 <60 ms 硬指标大概率破)**, 只保功能 | 按 §5.3 的 N1~N5 | ★**排序理由**: C1 代价最小且有官方依据 ⇒ 先查 C1; C2/C3 都要老板拍, sw-lead 不代拍 |

### 8.5 ★本单处置台账 (★闸点名的条目逐条落定★)★

| 文件:行 | 判定 | 处置 | 通道 |
|---|---|---|---|
| `SW/RK3572_TARGET_COMPAT_V2.md` L3 | 结论待裁 (ISS-155 定位) | ★**ISS-155 是否从「demo 头号卡点」降为「转换链已通 / 板端待板」= 交 main 裁** (本单不代拍) ⇒ 本行标签**原样保留** | 本单可处置 |
| `SW/RK3572_TARGET_COMPAT_V2.md` L20 | 结论矛盾 | ★**改写成当前真值** (§0 摘要表第 3 行, 原文保留 + 订正 + 取代标记) | 本单可处置 |
| `SW/RK3572_TARGET_COMPAT_V2.md` L21 | 结论矛盾 | ★**改写** (§0 摘要表第 4 行, 补 rk3572-target 分支; [0数据] 判定不变) | 本单可处置 |
| `SW/RK3572_TARGET_COMPAT_V2.md` L96 | 结论矛盾 | ★**改写** (§3.2: 「没有 rk3572 编译目标」限定在 toolkit2 家族内) | 本单可处置 |
| `state/fragments/sw.yaml` (旧条目) | 结论矛盾 | ★**台账追加式** ⇒ 本单新增分片条自带取代标记 ⇒ 后条取代前条 (闸规则 F5) | 本单可处置 |
| 其余 15 条 (HW/STEP1_LANDING_LIST.md · SW/DEMO_BOARD_60MS_VERDICT_PLAN.md · SW/DEMO_OD_PIPELINE_SPEC.md · SW/MODEL_RELEASE_LIST.md · SW/RK3572_TARGET_BOARD_VERIFY.md · SW/RKNN_BUILD_ENV_RECOVERY.md) | 结论矛盾 | ★**越权 (不在 ISS-353 允许写范围) ⇒ 交 main 裁**; 逐字替换文本见交卷页 §B1.2, 一键补丁 `logs/iss353/apply_caliber_dispositions.py` | 越权·交 main 裁 |

### 8.6 ★残留项 (★口径清了 ≠ 实现改了 ★)★

- ★**转换脚本仍是 toolkit2 + rk3576** ★: `SW/tools/rk3572_model_rebuild.sh` (L13/L86/L136) 与 `SW/RKNN_BENCH.md` §5 仍在用 `target_platform='rk3576'`。
  ⇒ 那是**脚本现状陈述** (闸判「历史叙述(可留)」), 但★**它意味着"主路线 = rk3572-target"还没落到脚本上**★
  ⇒ **后续单 (sw-lead) 应给重建/bench 脚本加 rknn3-toolkit + rk3572 分支** ⇒ **交 main 裁排期**, 本单不代拍、不改脚本。
- ★**板端接受性 [0数据]** ★: 降级 A 未触发前, N1~N5 一个数都没有 ⇒ 台账里只能写 [0数据]。
