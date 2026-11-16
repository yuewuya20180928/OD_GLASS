# ISS-250 · rknn-toolkit2 target 合法性查证表 (RK3572 是否可用)

> ★**本文件是活文档, 边查边写** (★上一轮 10 分钟全攒在内存里被 timeout 掐死 ⇒ 本轮每抓到一条立刻落盘★)
> ★**owner**: sw-lead (软件总工) · ★**verify_by**: main (项目总工) · ★**单号**: ISS-250 (owner=main, blocker) · ★**根因单**: ISS-155 ★
> ★**开工**: 2026-11-16 19:4x (GMT+8) · ★**零外发** (不发信 / 不询价 / 不问询 / 不采购) · ★**板不可达时挂「板不可达」, 不挂「等外部回复」** ★

## 查证表 (★每行 = 查了什么 / 去哪查 / 结论 / 证据等级★)

| # | 查了什么 | 去哪查 (URL 或本机路径) | 结论 | 证据等级 |
|---|---|---|---|---|
| **E-01** | 本机 rknn-toolkit2 版本 | `/home/yuewuya/miniconda3/envs/rknn/lib/python3.10/site-packages/rknn/VERSION` + `rknn_toolkit2-2.3.2.dist-info/METADATA` | ★**2.3.2** (★wheel: `cp310-cp310-manylinux_2_17_x86_64`, installer=`pip`, 无 `direct_url.json` ⇒ 第三方源安装) ★ | ★`[实测]` ★ |
| **E-02** | toolkit2 支持的 target 列表 (实测枚举) | 本机 `RKNN().config(target_platform=…)` 逐个探测 (★28 个候选, 全跑完★) | ★**合法 target 恰好 11 个**: `rv1103` · `rv1103b` · `rv1106` · `rv1106b` · `rv1126b` · `rk2118` · `rk3562` · `rk3566` · `rk3568` · `rk3576` · `rk3588` (★每个都 `config()` 返回 ret=0★) ⇒ ★**`rk3572` 不在其中** ★ | ★`[实测]` (★本机实跑, 28/28 候选全枚举, 无一漏★) ★ |
| **E-03** | rk3572 是否在 target 列表中 | 同上 | ★**不在** ⇒ `config(target_platform='rk3572')` 抛 ★**`ValueError: Invalid target_platform 'rk3572'!`★ (★抛在 `rknn/api/rknn_base.py:896` 的 `RKNNBase.config`★) ⇒ ★**本机实测复现 ISS-207 / ISS-147 的结论, 不是转述★ ★ | ★`[实测]` ★ |
| **E-04** | rk3576 是否在 target 列表中 | 同上 | ★**在** ⇒ `config(target_platform='rk3576')` → ★**ret=0 (接受)★** ⇒ ★**唯一同代可走的 target** ★ | ★`[实测]` ★ |
| **E-05** | 被拒 target 的完整名单 (反证枚举不是漏测) | 同上 | ★**被拒 16 个**: `rk1808` `rk3399pro` `rv1109` `rv1126` `rk2108` ★**`rk3572`** `rk3572b` `rk3516` `rk3506` `rv1210` `rv1209` `rk1806` `rk3399` `rk3288` `rk3568b` `rv1103c` ⇒ ★**尤其 `rk3572b` 也被拒** (★⇒ 不存在"b 变体"后门★) ★ | ★`[实测]` ★ |
| **E-05b** | 官方 GitHub README / release notes 对 RK3572 的口径 (★rknn-toolkit2 侧★) | `https://raw.githubusercontent.com/airockchip/rknn-toolkit2/master/README.md` (★抓取 2026-11-16 20:0x★) | ★**rknn-toolkit2 的 README 里【没有 RK3572 字样】** ⇒ ★**官方口径 = rknn-toolkit2 这条线不管 RK3572** (★与 E-02 实测的 11 个合法 target 列表完全一致: 里面有 `rk3576`, 没有 `rk3572`★) | ★`[官方]` ★ |
| **E-06** | ★**`rknn3-toolkit` 是否存在且官方** ★ | ★**GitHub API `repos/airockchip/rknn3-toolkit` + `raw.githubusercontent.com/.../README.md` + `CHANGELOG.md` (★抓取 2026-11-16 20:05~20:10 GMT+8★)** ★ | ★**存在, 且是 Rockchip 官方口径** ★: ★**仓库 `airockchip/rknn3-toolkit` (★173★ / 20 fork, created 2026-01-30, pushed 2026-11-05, lang=Python★) · ★**README 首句: 「RKNN3 SDK provides the complete software stack for deploying AI models on RK1820/RK1828/**RK3572**」★ · ★**「Supported Platforms: RK1820 / RK1828 / RK3572」★ · ★**「Non-coprocessor mode (RK3572): The NPU is integrated inside the SoC; models run directly on the board.」★ · ★**CHANGELOG V1.0.4: 「Added RK3572 platform support (Beta)」★ · ★**V1.2.0: 「Added MatMul APIs for RK3572」/「Improved LLM support on RK3572」/「Fixed a memory leak issue on RK3572」★** ★ ⇒ ★**★RK3572 官方适配存在, 且是 NPU 集成在 SoC 内的非协处理器模式★** ★ | ★`[官方]` (★URL + 抓取时间见 E-06b★) ★ |
| **E-06b** | ★**`rknn3-toolkit` 的【官方性】证据链 (★别只凭一个仓库名就信★)** ★ | ★**GitHub API: `users/airockchip/repos` (★28 个仓库★) + `orgs/rockchip-linux/repos` (★11 个★) + `search/repositories?q=rknn3-toolkit`★** ★ | ★**`airockchip` = Rockchip 官方 AI 账号 (★个人账号形态, 不是 org★)**: ★**同一账号下同时托管 `rknn-toolkit2` (★**3549★**★) · `rknn_model_zoo` (★2906★) · `rknn-llm` (★1771★) · `librga` (★603★) · `rknn-toolkit` (★57★) · `rknpu`/`rknpu2` (★25/19★) · `rknn3-model-zoo` (★166★) · `rknn3-toolkit` (★173★)· ★**`rockchip-linux` org 只有 11 个仓库, 内含 `rknn-toolkit2` 但【★只有 2024-03-25 的旧快照, 无 rknn3★】** ⇒ ★**官方仓库 = `airockchip/*` 这条线 (`rockchip-linux/rknn-toolkit2` 是老镜像)★** ★ · ★**GitHub 全站搜 `rknn-toolkit3` ⇒ total_count = 0 (★⇒ 没有这个包名★)** ★ · ★**PyPI 探测: `rknn3-toolkit` ⇒ HTTP 404 · `rknn-toolkit3` ⇒ HTTP 404 · `rknn-toolkit` ⇒ HTTP 404 · `rknn-toolkit2` ⇒ HTTP 200 (★唯一在 PyPI 上的★)** ★ | ★`[实测]` (★本机 curl 打的 GitHub API / PyPI★) ★ |
| **E-07** | ★**toolkit 是二进制 wheel 还是源码可编** ★ | ★**GitHub API `contents/rknn3-toolkit/packages` + `contents/rknn3-toolkit` (★抓取 2026-11-16 20:10★)** ★ | ★**`rknn3-toolkit/` 下只有 3 个子目录: `docker/` · `examples/` · `packages/` — 【★没有源码树★】** ⇒ ★**`packages/` 里只有 4 个【预编译 wheel】+ `requirements_cp310-1.2.0.txt` + `requirements_cp312-1.2.0.txt` + `md5sum.txt`: `rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl` (★**102,657,410 B ≈ 98 MB★**) · `cp312-manylinux2014_x86_64` (≈97 MB) · `cp310-macosx_13_0_arm64` (≈97 MB) · `cp312-macosx_13_0_arm64` (≈97 MB) ⇒ ★**★是二进制 wheel 发行, 不是源码可编★ (★仓库里没有可编的 Python/C++ 源码, 只有 wheel★)** ★ · ★**官方 md5 (`packages/md5sum.txt`): cp310-linux = `a972e03af94fd18e21f026558735b28d` ★ / cp312-linux = `532bcb4416dc4083ce8eb717ff95928f` ★** ★ · ★**支持 Python: 3.10 / 3.12** (★README「Supported Python Versions」★) ⇒ ★**本机 conda env `rknn` 正是 python3.10 ⇒ wheel 版本对得上** ★ | ★`[官方]` ★ |
| **E-08** | ★**RK3572 是否要走别的路径 (★与 rknn-toolkit2 的关系★)** ★ | ★**README「Notes」段 + README「Supported Platforms」段的交叉指路 + CHANGELOG (★抓取 2026-11-16 20:10★)** ★ | ★**官方把两条线【分工切开, 不是竞争关系】**: ★**rknn3-toolkit 覆盖 RK1820 / RK1828 / RK3572** ★ ⇒ ★**rknn-toolkit2 覆盖 RK3588/RK3576/RK3568/RK3566/RK3562 / RV1103/RV1106 / RV1103B/RV1106B / RV1126B / RK2118 (★README 明文指路★)** ★ ⇒ ★**★RK3572 的官方路径 = rknn3-toolkit, 不是 rknn-toolkit2★** ★ · ★**★但官方同时写死一句硬约束 (README「Notes」段): 「RKNN3-Toolkit is **not compatible** with RKNN-Toolkit and RKNN-Toolkit2.」⇒ 【★不能装在同一个环境里, 要换就得【独立 conda env】★】★** ★ | ★`[官方]` ★ |
| **E-09** | ★**版本 / 发布节奏 / 与本机 2.3.2 的版本关系** ★ | ★**GitHub API `repos/airockchip/rknn3-toolkit/releases` (★抓取 2026-11-16 20:06★)** ★ | ★**4 个 release (★全部非 prerelease★)**: ★**`v1.2.0` (★published 2026-11-05T05:01:38Z, name「v1.2.0」★) · `V1.1.0` (★2026-08-26, name「RKNN3 SDK V1.1.0」★) · `V1.0.4` (★2026-06-01, name「RKNN3 Toolkit V1.0.4」★) · `V1.0.0` (★2026-01-30, name「RKNN3 Toolkit V1.0.0」★)** ★ ⇒ ★**★版本线是「RKNN3 Toolkit 1.x」, 与 rknn-toolkit2 的「2.x」是【两套独立编号】⇒ 不存在「3 比 2 新所以要换」这层关系★** ★ · ★**RK3572 从 `V1.0.4` (2026-06-01) 起进 (★标 Beta★), 到 `v1.2.0` (2026-11-05) 已补 MatMul / LLM 支持 + 修内存泄漏 ⇒ ★**到 v1.2.0 为止 RK3572 仍没摘 Beta 标签 (★README 仍写「Beta」的是 V1.0.4 那条 changelog 原文, ★主 README 的「Supported Platforms」段没写 Beta★)** ★ | ★`[官方]` ★ |
| **E-10** | ★**安装方式 / 依赖** ★ | ★**`packages/requirements_cp310-1.2.0.txt` (★抓取 2026-11-16 20:11★)** ★ | ★**依赖清单 (★官方 requirements★)**: ★`protobuf>=4.21.6,<=6.33.6` · `psutil>=5.9.0` · `ruamel.yaml>=0.17.21` · `scipy>=1.12.0` · `tqdm>=4.64.1` · `opencv-python>=4.8` · `fast-histogram>=0.11` · ★**`numpy>=2.0`**★ · `pillow` · `sentencepiece` · `safetensors` · ★**`torch>=2.2`**★ · `datasets` · `tabulate` · `pandas>=2.1` · `prettytable` · `onnx>=1.16` · `onnxruntime>=1.22.0` ★ ⇒ ★**★关键: `numpy>=2.0` + `torch>=2.2` ⇒ 与 rknn-toolkit2 2.3.2 的依赖栈【很可能冲突】, 这与 README「not compatible」口径吻合★** ★ | ★`[官方]` ★ |
| **E-11** | ★**★rknn3-toolkit 本机能不能装 (`pip install` 实测)** ★ | ★**本轮【不做】: 下载受限 (★实测见 E-12★)** ★ | ★**`[0数据·受下载速率限制]`** — ★**本轮禁止下载 wheel / 禁止 clone 仓库 / 禁止 pip install** (★下载是最贵的坑★) ⇒ ★**本机能否装 = 未验, 列为待办 (★见 E-12 ④步★)** ★ | ★`[0数据·受下载速率限制]` ★ |
| **E-12** | ★**实测 `config(target_platform='rk3572')` 在 rknn3-toolkit 下能不能过** ★ | ★**同上 (★须先装上 rknn3-toolkit 1.2.0 才谈得上实跑★)** ★ | ★**`[0数据·受下载速率限制]`** — ★**官方 wheel `rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl` = 102,657,410 B (≈98 MB, 见 E-07) · 官方 md5 (cp310-linux) = `a972e03af94fd18e21f026558735b28d`** ★ · ★**下载速率本机实测 (2026-11-16 20:1x, 7 路 range 并发): 合计 ≈ 43.5 KB/s ⇒ 单路 ≈ 6.2 KB/s ⇒ 单路全量 ≈ 4.6 h / 7 路并发全量 ≈ 0.47 h ⇒ 本轮一律不下载** ★ · ★**依赖冲突 (E-10): `numpy>=2.0` + `torch>=2.2` ⇒ 与 rknn-toolkit2 2.3.2 栈冲突 ⇒ 必须【独立 conda env (python3.10)】(与 E-08「not compatible」口径一致)★** ★ ⇒ ★**待办 (★不属本轮★): ① 下 wheel + md5 校验 ② 建独立 conda env (python3.10) ③ 装依赖 ④ `config(target_platform='rk3572')` 实跑 + 记 min/avg/max** ★ | ★`[0数据·受下载速率限制]` ★ |

## 降级方案 (★各带量化代价 + 启用条件 + 谁拍★)

★**三条路线互斥 · 本单只列「代价 + 启用条件 + 谁拍」, ★不替老板拍板 (★见交卷单 B8 / 未决项 O-1★)** ★

| 路线 | 做什么 | 量化代价 | 启用条件 | 谁拍 |
|---|---|---|---|---|
| **① rk3576-target (维持现状)** | ★**继续用本机已装 rknn-toolkit2 2.3.2 (E-01) + `target_platform='rk3576'` (E-04 实测 ret=0)** ⇒ 产物已在盘: `SW/artifacts/models/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn` (4,989,367 B) + `.sha256` + `.meta.json`★ | ★**新增下载 = 0 B** · 转换 build(INT8) 25~26 s (已实跑) · PC F1 = 0.29265 (281 张, 已实跑) · ★**板端 runtime 接受性 = `[0数据]` (板不可达) ⇒ 风险 R1: 若 N1 FAIL 则整条路线作废**★ | ★**板端 N1 (`load_rknn` + `init_runtime` 都 ret == 0) 通过** ★ | ★**main (项目总工) 先验 · 涉 60ms 生死 ⇒ 老板** ★ |
| **② rknn3-toolkit 1.2.0 (官方 RK3572 路径)** | ★**独立 conda env (python3.10) 装 `rknn3_toolkit-1.2.0-cp310-…whl` ⇒ 跑 `config(target_platform='rk3572')` ⇒ 官方 RK3572 适配 (E-06/E-08)★** | ★**wheel 102,657,410 B (≈98 MB) + 新建独立 env (`numpy>=2.0` / `torch>=2.2`, E-10) ⇒ 与 toolkit2 2.3.2 栈冲突 (E-08「not compatible」) ⇒ 现 env 不能复用** · ★**下载 ≈ 0.47 h (7 路并发实测速率) ~ 4.6 h (单路)★** · ★**RK3572 自 V1.0.4 起仍是 Beta (E-09) ⇒ 精度/耗时无任何现成基线, 须从零建判据**★ | ★**老板批准「新建独立 conda env + 投下载窗口」· 且路线① 的 N1 FAIL** ★ | ★**老板 (★新增 env / 占资源 / 是否切官方 RKNN3 栈★)** ★ |
| **③ 降 OD 负载 / 回 RK3576 (换 SoC)** | ★**不追 RK3572 工具链: 降 OD 负载 (640×480@30) 或换回 RK3576** ★ | ★**板级改版 + 重新打样 (周期以周计) · 60 ms 余量按 RK3576 实测链重算 (纯 NPU 15.4~17.4 ms / 模式A 55~57 ms)**★ | ★**路线① N1 FAIL 且 路线② 不可行 / 不被批准** ★ | ★**老板 (★换芯片 = 商务决策★)** ★ |

★**三条路线共用同一套板端判据 = 现有 `SW/tools/rk3572_target_smoke.sh` 的 N1~N5 (★阈值见下一节★) ⇒ ★换路线不换判据★** ★
★**路线① 与 路线② 的判据差异只有一处: 路线② 的产物由 rknn3-toolkit 生成 ⇒ N6 (产物由哪条工具链生成) 必须写进 `.meta.json`, 否则 N1 失败时无法区分是「跨芯片不接受」还是「工具链不对」★** ★

## 板端可达时的执行清单 (★一条命令 + 逐条步骤 + 量化判据★)

★**一条命令 (★板端, 在项目根目录执行★)** ★
```bash
cd <项目根> && bash SW/tools/rk3572_target_smoke.sh \
  --artifact ./yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn \
  --expect-sha256 $(awk '{print $1}' yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn.sha256) \
  --images 300 --out ./evidence/ISS250_$(date +%Y%m%d) --power-note "<供电方式>"
```
★**本机可先跑 `--dry-run` (rc=0, 只打印板端将执行的每一条命令) ⇒ 板到手前命令就绪, 不用现写** ★

★**逐条步骤 (P1~P6 前置 + N1~N5 判定, 全部由脚本自动跑; 下表只列每步在验什么)** ★
| 步 | 在验什么 | 判据 (★量化★) |
|---|---|---|
| **P1** | 板型对不对 | ★`/proc/device-tree/compatible` 含 `rk3572`★ |
| **P2** | 板端 runtime 版本 | ★`librknnrt.so` 版本已记录 (★与 PC 侧 toolkit 版本对得上才继续★)★ |
| **P3** | 板端有 toolkit-lite2 | ★`rknn-toolkit-lite2` 存在★ |
| **P4** | 产物在位 | ★`.rknn` 存在且大小 = 4,989,367 B★ |
| **P5** | 校准集在位 | ★COCO val2017 + `instances_val2017.json`★ |
| **P6** | 产物同一性 | ★**产物 sha256 == sidecar** (★板端【不许重转】, 脚本里无任何 convert/build 路径★)★ |
| **N1** | ★**跨平台接受性 (本单最要紧的一条)**★ | ★`load_rknn` ret == 0 **且** `init_runtime` ret == 0 ⇒ 路线①成立; 否则 ⇒ 路线①作废 (转 ② / ③)★ |
| **N2** | 精度 | ★F1 ≥ **0.2427** (= PC 基线 0.2927 − 0.05)★ |
| **N3** | 纯 NPU 耗时 | ★`t_npu ≤ 13.30 ms` [推算]★; ★`13.30 < t_sdk_total ≤ 20.33` ⇒ **INDET** (★要纯 NPU 的数, 不许拿 SDK 总耗时顶★); ★`> 20.33` ⇒ ★**命中老板 T2 翻案条件 (纯 NPU S5 > 20.33 ms ⇒ 60 ms 不可保)**★ |
| **N4** | 口径纪律 | ★**纯硬件耗时与 SDK 总耗时必须分开报, 两个数都要**★ (★缺纯 NPU ⇒ INDET, 不许合并成一个数★) |
| **N5** | 可比性 | ★散热 / 频率 / 供电三项都在证据里★ (★缺 ⇒ N3 的数没有可比性★) |

★**三种结局 (★判据不变, 结论不同★)** ★
· ★**✅ 全过** ⇒ 路线①成立, 60 ms 硬线继续按 `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` 判
· ★**⚠️ N1 过但 N3 不行** ⇒ ★**命中 T2** ⇒ 降 OD 负载 / 回 RK3576 (路线③)
· ★**❌ N1 不过** ⇒ ★**路线①作废** ⇒ 走路线② (rknn3-toolkit) 或 路线③ (换 SoC)

★**走路线② 时的额外前置 (★本轮只列, 不执行★)**: ★独立 conda env (python3.10) + wheel md5 校验 `a972e03af94fd18e21f026558735b28d` + `config(target_platform='rk3572')` 实跑 ⇒ 这三步没做完, 路线② 连「能不能装」都还是 `[0数据]`★** ★

---

> ★**本表最后更新**: 2026-11-16 20:2x (sw-lead · 第 4 轮收尾) · ★**E-11 / E-12 本轮改为 `[0数据·受下载速率限制]`** (★不下载 / 不 clone / 不 pip install★) · ★**降级方案与板端清单于本轮补齐 (★上一轮因超时未落盘★)** ★
