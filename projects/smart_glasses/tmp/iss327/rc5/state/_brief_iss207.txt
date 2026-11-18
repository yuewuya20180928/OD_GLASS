★**目标 (★内部活·不是原厂的事·不是 PCB 布线/布局类★)**: 把 ★**ISS-155 (demo 头号卡点)**★ 从「**等一块能跑的板**」改成 ★**三件本机可交付的东西**: ①★**官方口径自己查**★ (rknn-toolkit2 最新版到底支不支持 `rk3572` target · RK3572 的 BSP runtime 在官方层认不认 `rk3576`-target 产出的 .rknn) ②★**板端到手 30 分钟跑完的验证包 (可执行脚本, 本机 `--dry-run` 必须 rc=0)**★ ③★**PC 侧产物的可重建路径 (含 sha256 + 落盘目录)**★ ⇒ ★**绝不外发, 查不到就写降级方案** ★

★★**为什么是现在 (★main 2026-11-15 21:4x 实测, 不是推测★)** ★★
· ★**原单的阻塞被写成了「等板子」** ⇒ ★**按老板 2026-11-12 02:02 新口径, 外部依赖不许挂着当阻塞项** ⇒ 必须换成【自己查的结果 + 证据等级 + 查不到就写降级方案】
· ★**本机现状 (★main 2026-11-15 21:4x 实测★)**: `python3 -c "import rknn_toolkit2"` ⇒ `ModuleNotFoundError` · `pip show rknn-toolkit2` ⇒ not found · `conda` ⇒ 不存在 ⇒ ⇒ ★**PC 侧这条转换链现在跑不起来 ⇒ 你不能靠「我再转一遍」交卷** ⇒ ⇒ **本单的价值在 ①②③ 的「可执行性」, 不在「再跑一遍」**
· ★**既有资料已经在盘上 (★先读, 别重做★)**: `SW/RK3572_TARGET_BOARD_VERIFY.md` (v1.0, 218 行, 已有前置条件 P1~P6 + 5 条判定) · `SW/RKNN_BUILD_ENV_RECOVERY.md` (911 行, P0-1 已闭死) · `SW/RKNN_BENCH.md` · `SW/tools/rknn_bench.py` ⇒ ★**你的活是【把 v1.0 升级成 v2.0 的「官方口径 + 可执行包」】, 不是重写一份**
· ★**v1.0 自己写下的一个坑 (★你要修★)**: v1.0 §0 第 2 条说 .rknn 产物在 `/tmp/rknn_bench/` ⇒ 「`/tmp` 会被系统清理 ⇒ 产物必须在下板前先拷到项目库 (`SW/artifacts/models/`)」⇒ ★**本机现在 `SW/artifacts/models/` 里没有 yolov5n 的 .rknn (main 实测: 只有两个 ssd onnx)** ⇒ ★**v1.0 的 §2 产物清单在本机已不可用 ⇒ 你必须给出「重建 + 落盘 + 校验」的完整可执行路径, 并在文档里把这一条标成 [0数据]**

★★**① 查 01a — 最新 rknn-toolkit2 到底支不支持 `rk3572` target (★自己查, 零外发★)** ★★
· ★**要查 [官网]**: Rockchip 官方 `rknn-toolkit2` 仓库发布说明 (GitHub releases) + PyPI 版本历史 + 官方 wiki 的 Support Platform 列表 ⇒ ★**找 2026-11 现在的最新版本号, 以及它的合法 `target_platform` 列表**
· ★**已实测的基线 (★main 2026-11-15 复核, 你不用重跑★)**: 2.3.2 与 2.5.0 都抛 `ValueError: Invalid target_platform 'rk3572'!`; 同进程 `rk3576` / `rk3588` rc=0 ⇒ ★**v1.0 的 P0-1 结论成立** ⇒ ★**你要查的是「有没有比 2.5.0 更新的版本加了 rk3572」**
· ★**口径纪律**: ★**「新版本号」≠「支持 rk3572」** ⇒ ★**必须把「最新版本号」和「它的合法 target 列表」分开写, 各标证据等级** ★
· ★**不许只回一句「官方没给」** ⇒ 必须给降级方案 (见 ③)

★★**② 查 01b — RK3572 BSP 的 runtime 认不认 `rk3576`-target 产出的 .rknn (★官方层依据★)** ★★
· ★**要查 [官网]**: Rockchip 官方 RK3572 BSP/SDK 的 `librknnrt` 版本说明 · 官方 `rknn_model_zoo` / `rknn-toolkit2` 仓库里关于「同代 NPU (RKNPU v2) 产物跨芯片复用」的说明 · 官方 wiki 的 RK3572 RKNN 章节
· ★**要判的命题 (★二选一, 必须给结论 + 等级★)**: ★**(a) 官方明确支持同代跨芯片复用 ⇒ 转换路径合法, 只差实测** / ★**(b) 官方无此口径 ⇒ 只能标 [0数据], 并给降级方案** ★
· ★**不许把「同代同架构 (4 TOPS / 3 核 RKNPU v2)」当成官方结论** ⇒ ★**那是我们自己的 [推算] (ISS-155 里已写) ⇒ 你要把它升级成官方依据; 升级不了就如实写 [0数据]** ★

★★**③ 降级方案 (★查不到时的必须项, 不是可选项★)** ★★
· **降级 A (自持验证包)**: ★**把「必须实测」变成「拿到任意一块 RK357x 板就能自动跑完」** ⇒ 见交付物 ②
· **降级 B (重建路径)**: ★**给出 PC 侧一键重建 (装工具链 → 转模型 → 落盘 → sha256) 的完整命令序列 + 落盘目录 + sha256 校验命令** ⇒ ★**让「产物没了」不再是坑**
· **降级 C (判据固化)**: ★**把 5 条判定口径写成脚本里的可执行判据 (★不许只是文档里的一段话★)** ⇒ ★**板子到手 ⇒ 跑一条命令 ⇒ 直接出 PASS/FAIL + 数值** ★

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★新建★ `SW/RK3572_TARGET_COMPAT_V2.md` — ①查证表 (每条: 结论 + ★**证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`**★ + 出处 URL/文档章节 + 你的复算依据) ②★**兼容矩阵**: 「最新 toolkit 版本 × target_platform 列表 × 是否含 rk3572」③「RK3572 runtime 认不认 rk3576-target 产物」的官方依据/无依据 ④与 v1.0 (`SW/RK3572_TARGET_BOARD_VERIFY.md`) 的逐条差异 (★**只报差异, 不许改 v1.0 的文件**★) ⑤降级 A/B/C ⑥复现命令 ⑦边界
2. ★新建★ `SW/tools/rk3572_target_smoke.sh` — ★**板端一次性验证包**: 前置条件 P1~P6 自动核对 (含 `/proc/device-tree/compatible` 含 rk3572 / `librknnrt.so` 版本 / 板端 lite2 / 产物 sha256 比对 / ★**不许板端重转**★) → 跑 `SW/tools/rknn_bench.py` 的 acc 步 → ★**按 5 条判据输出 PASS/FAIL + 数值 + 失败原因**★ ⇒ ★**必须支持 `--dry-run` (本机没板 ⇒ 只做本地可做的检查 + 打印将执行的板端命令, rc=0)** ★
3. ★新建★ `SW/tools/rk3572_model_rebuild.sh` — PC 侧一键重建 (装 rknn-toolkit2 → 转 yolov5n@640 → ★**产物落盘到 `SW/artifacts/models/` (不许留 /tmp)**★ → 打印 sha256 + 与旧基线 sha256 比对) ⇒ ★**必须支持 `--dry-run` (本机无 toolkit2 ⇒ 只打印将执行的命令, rc=0)** ★
4. ★新建★ `HANDOFF/2026-11-15_sw-lead_ISS207_rk3572target与验证包.md` — 交卷报告 (★≤25 行: 结论先行 + 兼容矩阵 + 降级 + 复现命令输出)
5. ★**必要时** `state/fragments/sw.yaml` (走 `state/frag_write.py`; ★只许新增条目, 不许删改别人的 key★)

★★**⑤ 验收自证 (交卷前跑, 把输出贴进回复)** ★★
```
bash SW/tools/rk3572_target_smoke.sh --dry-run     # rc=0
bash SW/tools/rk3572_model_rebuild.sh --dry-run    # rc=0
python3 state/merge.py                             # rc 必须 0
python3 state/gate_check.py                        # rc=0, 【Q1】必须 18/18
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb SW/tools/timing_check.py SW/tools/rknn_bench.py
```
★**md5 期望 (不许变)**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` · `SW/tools/timing_check.py` `cdc59f554fc6c82fe2588c2845b08977` · `SW/tools/rknn_bench.py` `46b17fca415fbcaae4ffa0c2843e7bf2` ★
★**并发提示 (★2026-11-15 21:4x 实测★)**: 同一时刻可能有 3 个 agent 在跑 ⇒ ★**`state/merge.py` 若报 rc=2 (并发写 STATE.yaml 冲突) ⇒ 等 30 秒重跑一次; 重跑仍红就如实报, 不要死磕** ★

★★**⑥ 边界 (不许越)** ★★
· ★**不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ ★**所有对外信息一律自己上网查官方页面, 查不到标 [0数据] + 写降级方案** ⇒ ★**没有「等原厂回信」这个选项** ★
· ★**不许改**: `SW/RK3572_TARGET_BOARD_VERIFY.md` (★只许引用与逐条对比★) · `SW/RKNN_BUILD_ENV_RECOVERY.md` (★只许引用★) · `SW/RKNN_BENCH.md` · `SW/tools/rknn_bench.py` · `SW/tools/timing_check.py` · `SW/ISP_CAPABILITY_RESEARCH.md` / `SW/ISP_CAPABILITY_RESEARCH.json` (★那是 ISS-124 的交卷件, 不许动★) · `SW/tools/isp_budget_solve.py` · `HW/` 下任何文件 (★`HW/POWER_BUDGET_V3.md` 是 hw-lead 地界, 只报不改★) · `HW/netlist_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · 任何 `state/gen_*.py` · `state/outbox/` 下任何草稿 (★只留档, 永不发★) · `PROJECT_TRACKER.md` §0 · **别人的分片** · `state/issue_log.yaml` (★改 issue 状态是 main 的活★)
· ★**不许碰 PCB 布线 / 布局** (★老板 2026-11-11 10:07 主线: 先原理图, PCB 布线类一律不派★)
· ★**本机无板 ⇒ 板端结论一律标 [0数据] 或 [推算], 不许写 [实测]** ⇒ ★**能写 [实测] 的只有本机实跑出来的东西 (e.g. `--dry-run` 的 rc 与输出、官方页面抓到的版本号与列表 (抓取本身算 [官网]))** ★
· ★**交卷 ≤ 25 行** (结论先行 + 兼容矩阵 + 降级 + 复现命令输出) ★
