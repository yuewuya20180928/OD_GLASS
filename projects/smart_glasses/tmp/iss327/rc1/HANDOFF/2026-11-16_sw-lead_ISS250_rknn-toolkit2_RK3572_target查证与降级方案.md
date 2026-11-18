# HANDOFF · ISS-250 · sw-lead 交卷单 —— rknn-toolkit2 / RK3572 target 查证与降级方案

> ★**派活人**: 项目总工 (main / moli) · ★**执行人**: sw-lead (软件总工, subagent)
> ★**单号**: ISS-250 (★owner=main, severity=high, source_blocker=ISS-155 · ★根因单 ISS-155 = demo 头号卡点★)
> ★**权威任务书**: `state/dispatch_briefs/ISS-250_continue.md` · ★**本趟任务书**: 2026-11-16 19:19 派活 (★会话被 gateway reload 掐断后由本会话续做★)
> ★**落盘**: 2026-11-16 19:4x 起骨架 / ★**本轮续做落盘**: 2026-11-17 05:2x~06:0x GMT+8
> ★**零外发** (不发信 / 不询价 / 不问询 / 不采购 · 老板 2026-11-11 19:31 + 2026-11-12 02:02) · ★**板端 [实测] = 0 条** (板不可达)
> ★**同名已有交卷单**: `HANDOFF/2026-11-16_sw-lead_ISS250_查证表收尾与rknn3验证.md` (★20:17 那份, 本单是它的【续做 + 补证 + 收口】版, 不替代它, 两份并存★)

---

## B1. 结论摘要 (★一句话 + 拆解★)

> ★**ISS-155 这条 demo 头号卡点, 现在是「转换链已通 (官方 rknn3-toolkit 路线实测过) + 板端接受性待板」; 官方口径同时给出**反向**结论: 「rk3576 转出来的 .rknn 在 RK3572 上跑通」这件事, 官方既无先例、结构上也不对齐 ⇒ 路线① 只能当【先试】, 不能当【有官方背书的默认解】。★**

★**六条结论 (逐条带证据等级, 全文见 `SW/research/ISS250_rknn_toolkit2_target_查证表.md`★)**:

1. ★**命题① (target 列表有没有 rk3572) = 没有, 且官方最新版本也没有** ★ **[官网]+[实测]**
   · 本机 rknn-toolkit2 2.3.2 实测枚举 28 个候选 ⇒ 合法 11 个 (`rv1103/rv1103b/rv1106/rv1106b/rv1126b/rk2118/rk3562/rk3566/rk3568/rk3576/rk3588`), `rk3572` 与 `rk3572b` **双双被拒** (`ValueError: Invalid target_platform 'rk3572'!`, 抛点 `rknn/api/rknn_base.py:896`)
   · ★**本轮 (2026-11-17 05:1x) 补官方口径**: README 自报「Latest version: **v2.5.0**」, §Support Platform 明文 8 个系列 **无 RK3572**; v2.5.0 (2026-10-20) release notes 全 10 条 bullet **全篇无 rk3572**; 仓库 tree 1852 条路径 **0 条**含 `3572`; `doc/` 19 个 PDF (V2.5.0) **无 RK3572 专章**
   · ⇒ ★**「升级 toolkit 就有 rk3572」这条路被官方封死 (已证伪, 见降级候选 C1)★**

2. ★**命题② (官方有没有说 rk3576 的产物能在 RK3572 上跑) = 【官方层不存在这句话】⇒ [0数据]** ★
   · 检索面: `rknn-toolkit2` README+release notes+tree+doc · `rknn3-toolkit` README+tree+runtime demo README · `rknn` (RKNPU 驱动仓) README · 全部零外发 GET
   · ★**并且有三条【结构性反证】(本轮新查到, 比「没有这句话」更硬)★**:
     · **[官网]** RKNN3 README 明文把 **RK3576 写成「host SoC」** (给 RK1820/RK1828 当协处理器宿主的), 把 **RK3572 写成「NPU 集成在自己 SoC 内、模型直接跑在板上」** ⇒ ★**两者在官方世界观里不是同一角色的对端★**
     · **[官网]** 官方 runtime demo README 明文: **RK3576/RK3588 = `librknn3_api.so` + `librknn3_api_rkcp.so`**, 而 **RK3572 = `librknn3_api.so` + `librknn3_api_native.so`** ⇒ ★**即使在同一个 RKNN3 家族里, 板端库都分叉 ⇒ 结构上就不对齐★**
     · **[官网]** `airockchip/rknpu` README: RK3562/RK3566/RK3568/**RK3576**/RK3588/… 全部指向 **RKNPU2** ⇒ RK3572 不在 RKNPU2 名单 ⇒ ★**跨家族 (RKNPU2 格式 → RKNN3 runtime) 无任何官方支撑★**
   · ⇒ ★**路线① (rk3576-target 产物直接上板) = 零官方背书 + 结构反证 ⇒ 保留为「先试」, 不作默认解★**

3. ★**命题③ (RK3572 与 RK3576 的 NPU 差异) = 【不是同代同架构, 且算力差 33%】⇒ 官方反证 + 媒体实测** ★
   · **[官网]** RK3576 官方 Brief Datasheet V1.2 原文: 「NPU ● **6 TOPS@INT8**」(`rock-chips.com/uploads/pdf/2024.3.18/192/RK3576 Brief Datasheet V1.2-20240311.pdf`)
   · **[媒体]** RK3572 = **4 TOPS INT8** (linuxgizmos / SBCwiki / Forlinx 三家交叉一致; ★官方 PDF 本轮未取到 ⇒ 不升级为 [官网]★)
   · ⇒ ★**ISS-155 里那句「RK3572 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2)」被【再证伪一次】: RK3576 官方是 6 TOPS, 不是 4 TOPS; 两颗芯片分属 RKNN3/native 与 RKNN2/rkcp 两个家族★**
   · ★**★后果 (这条直接影响 60 ms 硬线, 必须让 main 知道)★**: N3 的通过线 `t_npu ≤ 13.30 ms` 是**按「RK3572 ≈ RK3576 的 13.305 ms」推算**来的 (`SW/DEMO_OD_TIMING_SPEC.md` / `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md`); 若 RK3572 的 NPU 算力只有 RK3576 的 2/3 ⇒ ★**同一产物在 RK3572 上的纯 NPU 耗时可能比 13.30 ms 高 ~50% ⇒ 13.30 ms 这条线必须在板端实测后重估, 不能当既定门槛用 [推算]★**

4. ★**命题④ (官方 model zoo 有没有 RK3572 预编译模型) = 【没有, 而且两个官方 zoo 都不提交 .rknn 二进制】⇒ [实测]** ★
   · `rknn3-model-zoo` 全量 tree **2602 条 / `.rknn` = 0 个**; `rknn_model_zoo` 全量 tree **1888 条 / `.rknn` = 0 个** (路径含 `3576`/`3572` 的也 = 0)
   · ⇒ ★**降级候选「直接用官方预编译模型」判死 (不是"难找", 是"不存在")★**

5. ★**路线② (官方 RK3572 路径) 的主机侧 = 已实跑通 (ISS-263 实测 + 本轮复核)** ★ **[实测]**
   · 独立 conda env `/home/yuewuya/miniconda3/envs/rknn3` (py3.10.22) 内 `rknn3-toolkit 1.2.0` 装好; ★**toolkit2 2.3.2 旧 env 装前装后 pip list 逐行相同 ⇒ 未污染★**
   · `config(target_platform='rk3572')` ⇒ **rc=0** (读数 0.019 s / 0.013 s / ★**本轮 0.001 s**★) · 反向自证 `rk3576` ⇒ **ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572**
   · 转换 3 次全 rc=0 ⇒ 产物 **249,360 B + 同名 `.weight` 1,960,448 B**, md5 `97a34fff…` (三次逐字节一致), `t_total` min 33.389 / avg 36.390 / max 41.672 s (★主机侧转换耗时, **不是板端延迟**★)
   · ★**板端接受性仍 [0数据]**: `init_runtime(target='rk3572')` ⇒ rc=**−1** / `RKNN3_ERR_DEVICE_UNAVAILABLE` / 0 台设备

6. ★**路线① 与路线② 的板端前置条件【不一样】(本轮新增, 之前没人写清)** ★ **[官网]+[实测]**
   · 路线①: 单个 `.rknn` + 板端 `rknn-toolkit-lite2` + `librknnrt.so`
   · ★**路线②: `.rknn` + `.weight` 两件套 + 板端 `librknn3_api.so` + `librknn3_api_native.so` (RK3572 专用 native 库, RK3576/RK3588 用的是 `rkcp`, 不通用) ⇒ 现有 `rk3572_target_smoke.sh` 的 P3 (要求 lite2) 对路线② 不适用 ⇒ 本轮补了配套脚本 `SW/tools/rk3572_rknn3_board_smoke.sh`★**

★**⇒ ISS-155 的 blocker 状态可以改写成「转换链已通 (官方 RKNN3 路线, 实测) / 板端接受性待板」; 路线选哪条 = 老板拍 (见 B5 未决项 O-1)★**

---

## B2. 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 (★权威任务书 §④★) | 自评 | 依据 |
|---|---|---|---|
| 1 | ★**查证表: 一行一条 (查了什么 / 去哪查 / 结论 / 证据等级 / 原文摘录)★** | ★**通过** ★ | `SW/research/ISS250_rknn_toolkit2_target_查证表.md` §1 = **21 条** (E-01~E-21, 含 E-05b/E-06b), 每行五要素齐全 ★门禁实测: `查证行 23 条, 缺证据等级 0 条`★ |
| 2 | ★**覆盖任务书点名的 4 条命题** ★ | ★**通过** ★ | ① = E-02/E-03/E-05/E-13 · ② = E-14/E-15/E-16/E-20 · ③ = E-19/E-15/E-20 · ④ = E-18 ★门禁实测: `4 条必答命题缺 0 条 ⇒ 全覆盖`★ |
| 3 | ★**降级方案 ≥2 条, 每条带量化代价** ★ | ★**通过 (8 条)** ★ | §2 = 任务书点名的 5 条候选 (C1~C5) **逐条判死/判活** + 本轮自己查出来的 3 条路线 (R1/R2/R3) ⇒ 每条都有「代价 / 启用前提 / 谁拍」三列非空 ★门禁实测: `降级方案 8 条 (要求 ≥2)` + `代价/谁拍/前提 列为空 0 条`★ |
| 4 | ★**板端可达时的执行清单: 一条命令 + 前置 + 判据 + 失败下一步** ★ | ★**通过 (两条分支)** ★ | §3 = 路线① (现有 `rk3572_target_smoke.sh`, `--dry-run` rc=0) + ★**路线② (本轮新增 `SW/tools/rk3572_rknn3_board_smoke.sh`, `--dry-run` rc=0 / 实跑模式在本机判 FAIL+INDET 且 rc=1, 不假装通过)★**; 判据 N1~N5 两分支通用; 每条 FAIL 都写了「下一步动作」 |
| 5 | ★**交接单 (B1~B6 六块齐全) + 分片 `state/fragments/sw.yaml` (走 frag_write.py) + 给 main 的 need** ★ | ★**通过** ★ | 本文件 (B1~B6) · 分片 = `python3 state/frag_write.py --agent sw-lead --add-claim/--add-artifact/--add-need` ★**未用 `open(p,"w")`★** · need = B5 的 O-4/O-5 |
| 6 | ★**可选第 5 件: 机器门禁 (每条有证据等级 + 降级 ≥2 + 判据不许写「等回信」) + `--selftest` 反向用例** ★ | ★**通过 (做了, 不跳过)** ★ | `SW/tools/check_iss250_rknn_target_gate.py`: 正向 **PASS rc=0** (8 项全绿) · `--selftest` **5/5 rc=0** (4 个反向用例各自报红 + 1 个正向用例全绿) |
| 7 | ★**零外发** ★ | ★**通过** ★ | 只 GET 官方页面 (api.github.com / raw.githubusercontent.com) · 零邮件 / 零询价 / 零问询 / 零采购 / 零原厂问询 |
| 8 | ★**实物 [实测] = 0 条 (板不可达), 不把推算写成实测** ★ | ★**通过** ★ | 板端相关结论一律 [0数据]; [实测] 只用于本机实跑 (config 正反两面 / tree 全量枚举 / 门禁自测) · [推算] 明确标出推导链 (13.30 ms 门槛那条) |
| 9 | ★**不许替老板拍板 (60 ms 门限挂不挂 / 换不换模型路线)** ★ | ★**通过** ★ | §2 只列 C4/C5 的「代价 + 启用前提 + 谁拍 = 老板」, 并标「sw-lead 只列不拍」; 推荐默认值写进 B5 O-1 但明确标「推荐 ≠ 已决定」 |
| 10 | ★**不改三道现有判据脚本 / 不碰 HW/ MECH/ issue_log / 不改 PROJECT_TRACKER §0 / 不写别人的分片** ★ | ★**通过** ★ | 本单只动: `SW/research/ISS250_rknn_toolkit2_target_查证表.md` (改) · `SW/tools/rk3572_rknn3_board_smoke.sh` (新) · `SW/tools/check_iss250_rknn_target_gate.py` (新) · 本交接单 (新) · `state/fragments/sw.yaml` (仅 sw-lead 自己那段, 走 frag_write.py) |
| 11 | ★**交卷前跑 `state/merge.py` (rc=0) && `state/gate_check.py` (Q1 18/18) 并贴输出** ★ | ★**通过** ★ | 输出贴在本次回复正文 (交卷自证段) |
| 12 | ★**交卷前跑 `check_demo_panel_spec.py` / `timing_check.py` (不许被本单弄红)** ★ | ★**通过** ★ | 输出贴在交卷自证段 (G1 rc=0 · G2 SELFTEST 71/71 rc=0) |

---

## B3. 证据分级 (★实测 / 官网 / 媒体 / 推算 / 0数据★)

★**图例**: ★**[实测]** = 本机实跑 (可复现) · ★**[官网]** = 官方仓库/官网文档 (带 URL) · ★**[媒体]** = 第三方媒体 · ★**[推算]** = 由实测推导 (标出推导链) · ★**[0数据]** = 无数据, 明确留白 ★

| # | 主张 | 等级 | 原文 / 数字出处 |
|---|---|---|---|
| E1 | toolkit2 合法 target 恰好 11 个, **无 rk3572 / rk3572b** | ★[实测]★ | 28 候选逐个 `config()`; 拒 `rk3572` 原文 `ValueError: Invalid target_platform 'rk3572'!` (`rknn/api/rknn_base.py:896`) |
| E2 | ★**官方最新版 toolkit2 = v2.5.0, 支持平台列表无 RK3572; release notes 全篇无 rk3572; 仓库 1852 条路径 0 处含 3572; doc/ 19 个 PDF 无 RK3572 专章** ★ | ★[官网]★ | `api.github.com/repos/airockchip/rknn-toolkit2/{readme,releases,git/trees/master?recursive=1}` (2026-11-17 05:1x 抓) |
| E3 | ★**官方层不存在「rk3576 的 .rknn 可在 RK3572 上跑」的表述** ★ | ★[0数据]★ | 检索面 = toolkit2 README/release notes/tree/doc + rknn3 README/tree/runtime demo + rknpu README (全零外发 GET) |
| E4 | ★**官方 RKNN3 README 把 RK3576 写成 host SoC (协处理器宿主), 把 RK3572 写成 NPU 集成在 SoC 内** ★ | ★[官网]★ | 「Coprocessor mode (RK1820/RK1828): Requires a host SoC (e.g., RK3588 / **RK3576**)…」 / 「Non-coprocessor mode (RK3572): The NPU is integrated inside the SoC…」 |
| E5 | ★**板端库分叉: RK3572 = `librknn3_api_native.so`, RK3576/RK3588 = `librknn3_api_rkcp.so`** ★ | ★[官网]★ | `rknn3-toolkit/rknn3-runtime/examples/rknn3_model_test_demo/README.md`「Libraries in install/…/lib」段 |
| E6 | ★**RKNN3 产物 = `.rknn` + `.weight` 两件套; 板端运行命令形态 = `rknn3_model_test <model> <weight> [core_mask] …`** ★ | ★[官网]★ | RKNN3 README「Typical Workflow」第 1 步 + runtime demo README 命令行参数表 |
| E7 | ★**官方两个 model zoo 都不提交 .rknn 二进制 (rknn3-model-zoo 2602 条 / 0 个; rknn_model_zoo 1888 条 / 0 个) ⇒ 「官方预编译模型」不存在** ★ | ★[实测]★ | GitHub API `git/trees/{main,master}?recursive=1` 全量枚举 (truncated=false) |
| E8 | ★**RK3576 = 6 TOPS@INT8 (官方 datasheet); RK3572 = 4 TOPS (三家媒体交叉) ⇒ 差 −33%** ★ | ★RK3576 = [官网] · RK3572 = [媒体]★ | `rock-chips.com/uploads/pdf/2024.3.18/192/RK3576 Brief Datasheet V1.2-20240311.pdf` · linuxgizmos / SBCwiki / Forlinx |
| E9 | ★**⇒ ISS-155「同代同架构 (4 TOPS/3 核 RKNPU v2)」被证伪 ⇒ N3 的 13.30 ms 门槛 (按 RK3572≈RK3576 推算) 必须在板端实测后重估** ★ | ★[推算]★ | 推导链: E8 (算力 2/3) + `SW/DEMO_OD_TIMING_SPEC.md` 的 13.305 ms 推算基数 ⇒ 同产物耗时可能 ×1.5 |
| E10 | ★**RK3572 不在 RKNPU2 名单 (RK3562/66/68/RK3576/RK3588/RV1103… 才在) ⇒ 跨家族复用无官方支撑** ★ | ★[官网]★ | `airockchip/rknpu` README |
| E11 | ★**rknn3-toolkit 1.2.0 已装独立 env; `config('rk3572')` rc=0; 反向自证 `config('rk3576')` 必报错; 转换 3 次 rc=0 产物 249,360 B md5 97a34fff…; t_total min 33.389/avg 36.390/max 41.672 s** ★ | ★[实测]★ | ISS-263 `logs/iss263/{config_probe,convert_rk3572_3runs,roundtrip_probe}.log` + ★**本轮 05:2x 复跑 config 正反两面 (rk3572 ret=0 0.001 s / rk3576 ValueError)★** |
| E12 | ★**两条工具链的合法 target 集合互斥** ★ | ★[实测]★ | 2.3.2: 收 rk3576 拒 rk3572 · 1.2.0: 收 rk3572 拒 rk3576/rk3588 (本轮 05:1x~05:3x 实跑) |
| E13 | ★**板端接受性 / 板端 F1 / 板端 e2e 延迟 / 板端纯 NPU 耗时** ★ | ★**[0数据]**★ | `init_runtime(target='rk3572')` rc=−1 / `RKNN3_ERR_DEVICE_UNAVAILABLE` / `list_devices()=[]` ⇒ 本机 0 台 RK3572 设备 |
| E14 | ★**「转换链已通 ⇒ 路线② 板端必通」** ★ | ★**[推算]★★ | 推导链: E11 (主机侧 rc=0) + E13 (板端 [0数据]) ⇒ 板端成败仍未定 |
| E15 | ★**「升级 toolkit 就能有 rk3572」** ★ | ★**[官网] 已证伪**★ | E2 (v2.5.0 仍无 rk3572) |

---

## B4. 接口取值声明 (interface_claims)

| key | value | note | ref |
|---|---|---|---|
| `iss250_rknn3572_target_status` | ★`rk3572` 在 rknn-toolkit2 2.3.2/2.5.0 的合法 target 列表中 **【不存在】**; 官方 RK3572 路径 = `rknn3-toolkit 1.2.0` + `target_platform='rk3572'` (★本机已装 + 实跑 rc=0★) ★ | ★[官网]+[实测] · toolkit2 侧实测拒 (rknn_base.py:896); rknn3 侧实测收 (rc=0) + 反向自证 rk3576 必报错 ⇒ 两集合互斥 ★ | `SW/research/ISS250_rknn_toolkit2_target_查证表.md` E-02/E-03/E-13/E-21 |
| `iss250_cross_chip_acceptance_status` | ★**官方层无口径 ⇒ [0数据]**; 结构上三条反证 (RK3576=host SoC / RK3572=native 库 / RK3572 不在 RKNPU2 名单) ⇒ 路线① 无官方背书 ⇒ 只能靠板端 N1 实测 ★ | ★[官网]+[0数据] ★ | 同上 E-14/E-15/E-16/E-20 |
| `iss250_npu_diff_3572_vs_3576` | ★**RK3576 = 6 TOPS@INT8 [官网]** (官方 Brief Datasheet V1.2) · ★**RK3572 = 4 TOPS [媒体]** (三家交叉) ⇒ ★**差 −33%; 「同代同架构」被证伪; 归族 = RKNN3/native vs RKNN2/rkcp★ ★ | ★[官网]+[媒体]+[推算] ★ | 同上 E-19 + `rock-chips.com/.../RK3576 Brief Datasheet V1.2-20240311.pdf` |
| `iss250_n3_threshold_status` | ★**`t_npu ≤ 13.30 ms` 这条线是 [推算] (基数 = RK3572 ≈ RK3576 的 13.305 ms), 在 E-19 新证据下必须【板端实测后重估】, 不得当既定通过线★** | ★[推算] · 后果 = 60 ms 硬线的验收线要重算 ⇒ 老板级 (见 B5 O-2) ★ | `SW/DEMO_OD_TIMING_SPEC.md` · `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` §O1 |
| `iss250_downgrade_routes` | ★**8 条**: C1 升级 toolkit 【❌判死·官方封死】 · C2 rk3576-target 直上板 【⚠️无官方背书·零新增成本·先试】 · C3 官方预编译模型 【❌判死·官方 zoo 里 0 个 .rknn】 · C4 换模型 M2 yolov5n@640 【✅判活·52.91 ms 推算·需重标定·不阻塞首台板】 · C5 改 60 ms 判据口径 【⚠️老板级·只列不拍】 · R1 = C2 的路线版 · R2 = 官方 rknn3 路线 (★主机侧已通, 板端 [0数据]★) · R3 = 降负载/回 RK3576 【板级改版·周级·商务决策】 ★ | ★[官网]+[实测]+[推算] ★ | 同上 §2 表 |
| `iss250_board_checklist` | ★**两条分支 + 一条命令 + N1~N5 判据**: 路线① `bash SW/tools/rk3572_target_smoke.sh --artifact … --expect-sha256 … --images 300 --out … --power-note …` (lite2) · ★**路线② (本轮新增) `bash SW/tools/rk3572_rknn3_board_smoke.sh --rknn … --weight … --expect-sha256 … --out …` (RKNN3 native 库 + 两件套)★** ★ | ★[实测] (两条 --dry-run 都 rc=0; 路线② 脚本在本机实跑 ⇒ P1/P3' FAIL + N1/N3 INDET + rc=1, 不假装通过) ★ | 同上 §3 + `SW/tools/rk3572_rknn3_board_smoke.sh` |
| `iss250_gate` | ★**机器门禁**: `python3 SW/tools/check_iss250_rknn_target_gate.py` ⇒ PASS rc=0 (8 项) ; `--selftest` ⇒ **5/5 rc=0** (4 反向用例 + 1 正向用例) ★ | ★[实测] ★ | `SW/tools/check_iss250_rknn_target_gate.py` |

---

## B5. 未决项与卡点 (★需要谁回答什么★)

| # | 未决项 / 卡点 | 现状 (★不写「等回信」★) | 谁能解 | 阻塞的是哪一步 |
|---|---|---|---|---|
| **O-1** | ★**路线选哪条 (R1 rk3576-target 先试 / R2 官方 rknn3 / R3 换 SoC)** ★ | ★**sw-lead 只列代价 + 量化, 不拍** ★ | ★**老板** (涉 demo 技术栈与 60 ms 生死) ★ | 阻塞: 板一通电后先跑哪条 (⇒ 但**不阻塞**准备工作: 两条命令都已就绪, 可按 N1 结果自动分流) ★ |
| **O-2** | ★**N3 的通过线 13.30 ms 是否还成立** ★ | ★**E-19 新证据 (RK3572 4 TOPS vs RK3576 6 TOPS) ⇒ 该线是 [推算], 板端实测后必须重估** ★ | ★**main 先验 + 老板拍** (60 ms 硬线是老板级) ★ | 阻塞: 板端 N3 的「通过/不通过」判定线 (⇒ **不阻塞** N1 的接受性判定) ★ |
| **O-3** | ★**demo 阶段到底挂不挂 60 ms 门限** ★ | ★**C5 = 只列选项 + 代价, 不拍** ★ | ★**老板** ★ | 阻塞: 验收判据的最终形态 (⇒ 与 O-2 一起拍) ★ |
| **O-4** | ★**板端 BSP 里有没有 RKNN3 runtime (`librknn3_api_native.so`) + lite3 评测器 + C API perf 采集** ★ | ★**本机 0 台设备 ⇒ [0数据]**; ★**官方 demo 已给出可直接用的路径: `./build-linux.sh -t rk3572 -a aarch64 -b Release` → `adb push` → `./rknn3_model_test <rknn> <weight> 0x1` ⇒ 路线② 不依赖 BSP 自带, 可自编译带上去★** ★ | ★**sw-lead 可自解 (板到手时自编译官方 demo) + 板侧配合 adb/ssh 通路** ★ | 阻塞: 路线② 的板端 N1 (⇒ **不阻塞** 路线①, 两条互不依赖) ★ |
| **O-5** | ★**板端可达性本身 (物理事实)** ★ | ★**本机 0 台 RK3572 设备 (实测 `list_devices()=[]`)** ⇒ ★**这是【板不可达】, 不是【等外部回复】⇒ 所有准备工作已做完, 板一到手就是一条命令出 PASS/FAIL★** ★ | ★**硬件/板侧** (★sw-lead 本机定不了, 也不该挂成阻塞项★) ★ | 阻塞: N1/N2/N3/N4/N5 五个板端判据 (★板端 [实测] 只能等这个物理事实, 但它【不是】"等回复"★) ★ |
| **O-6** | ★**是否把本单结论回写进 `SW/RK3572_TARGET_COMPAT_V2.md` 的 §1.3/§3.2 (命题②③ 的新证据)** ★ | ★**本轮【没改】那个文件** (它是 ISS-207/ISS-263 的受保护产出, 我只在查证表里写增量) ★ | ★**main 裁决** (或下一轮 sw-lead 单) ★ | 阻塞: 无 (只是台账同步, 不影响任何判据) ★ |

★**★给 main 的 need (★明确写清: 还差什么 / 谁能解 / 阻塞的是哪一步★)★** ★

| need key | to | item |
|---|---|---|
| `iss250_pick_downgrade_route` | main (→ 老板) | ★**路线 R1/R2/R3 三选一** (推荐默认值: ★**板一通电先跑 R1 的 N1 (零新增成本), N1 FAIL 立刻转 R2, R2 也不行才启 R3** ⇒ 但这是【推荐】, 不是【已决定】) · 依据与代价见 §2 ★ |
| `iss250_n3_threshold_recheck` | main (→ 老板) | ★**E-19 新证据 (RK3572 4 TOPS vs RK3576 6 TOPS) ⇒ N3 的 13.30 ms 通过线是 [推算], 板端实测后须重估** ⇒ 是否现在就把它降级为「观察项」, 还是等板端实测后再定 ★ |
| `iss250_rknn3_board_toolchain` | main (→ 板侧/硬件) | ★**板端 BSP 是否带 RKNN3 runtime (`librknn3_api_native.so`)?** ⇒ 不带也能走 (官方 `./build-linux.sh -t rk3572 -a aarch64` 自编译 + adb push) ⇒ ★**这条只影响路线② 的起步速度, 不构成阻塞; 板到手时 sw-lead 自解★** ★ |
| `iss250_sync_compat_v2` | main | ★**本轮的新证据 (E-14/E-15/E-16/E-19/E-20 + 门禁 + 路线② 板端脚本) 要不要回写 `SW/RK3572_TARGET_COMPAT_V2.md`** ⇒ 本轮【没动】那个文件 (边界内) ★ |

---

## B6. 自证复现命令 (★本机全部已实跑, 贴原文★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 查证表 + 降级方案 + 板端清单 (本单第 1~4 件交付物)
ls -la SW/research/ISS250_rknn_toolkit2_target_查证表.md
grep -c '^| \*\*E-' SW/research/ISS250_rknn_toolkit2_target_查证表.md   # ⇒ 21 条查证行
grep -c '^| \*\*[CR]' SW/research/ISS250_rknn_toolkit2_target_查证表.md # ⇒ 8 条降级方案

# ② 机器门禁 (可选第 5 件) ⇒ PASS rc=0
python3 SW/tools/check_iss250_rknn_target_gate.py
# ③ 门禁反向用例 ⇒ SELFTEST 5/5 rc=0
python3 SW/tools/check_iss250_rknn_target_gate.py --selftest

# ④ 本轮自己复跑的两条 config (正反两面) —— [实测] 读数来源
/home/yuewuya/miniconda3/envs/rknn/bin/python - <<'EOF'
from rknn.api import RKNN
for t in ('rk3572','rk3576'):
    try: print(t, '->', RKNN().config(target_platform=t))
    except Exception as e: print(t, '->', type(e).__name__, str(e).splitlines()[-1])
EOF
/home/yuewuya/miniconda3/envs/rknn3/bin/python - <<'EOF'
from rknn.api import RKNN
for t in ('rk3572','rk3576','rk3588'):
    try: print(t, '->', RKNN().config(target_platform=t))
    except Exception as e: print(t, '->', type(e).__name__, str(e).splitlines()[-1])
EOF

# ⑤ 板端清单: 本机先跑 dry-run (两条分支) ⇒ 都 rc=0
bash SW/tools/rk3572_target_smoke.sh --dry-run
bash SW/tools/rk3572_rknn3_board_smoke.sh --dry-run

# ⑥ 路线② 板端脚本的鲁棒性自测 (本机非板 ⇒ 必须 FAIL/INDET + rc=1, 不许假装通过)
bash SW/tools/rk3572_rknn3_board_smoke.sh \
  --rknn /var/tmp/iss263_rknn3/work/out/yolov5n_heads_int8_rk3572_run1.rknn \
  --weight /var/tmp/iss263_rknn3/work/out/yolov5n_heads_int8_rk3572_run1.weight \
  --expect-sha256 $(sha256sum /var/tmp/iss263_rknn3/work/out/yolov5n_heads_int8_rk3572_run1.rknn | awk '{print $1}') \
  --out /tmp/iss250_rknn3_selftest   # ⇒ P1/P3' FAIL + N1/N3 INDET + rc=1

# ⑦ 官方口径自查 (零外发, 只 GET 官方页面)
curl -sS "https://api.github.com/repos/airockchip/rknn-toolkit2/readme" | python3 -c "import sys,json,base64;print(base64.b64decode(json.load(sys.stdin)['content']).decode())" | grep -iA10 "Support Platform"
curl -sS "https://api.github.com/repos/airockchip/rknn3-toolkit/contents/rknn3-runtime/examples/rknn3_model_test_demo/README.md" | python3 -c "import sys,json,base64;print(base64.b64decode(json.load(sys.stdin)['content']).decode())" | grep -A6 "Libraries in"

# ⑧ 三道既有判据 + 合并/门禁 (不许被本单弄红)
python3 SW/tools/check_demo_panel_spec.py      # ⇒ rc=0
python3 SW/tools/timing_check.py               # ⇒ SELFTEST 71/71 rc=0
python3 state/merge.py && python3 state/gate_check.py   # ⇒ rc=0 (Q1 18/18)
```

★**★板一通电就跑这一条 (★路线② 官方命令形态, E-16 原文★)★**:
```bash
./build-linux.sh -t rk3572 -a aarch64 -b Release
adb push install/rknn3_model_test_Linux /userdata/
adb push yolov5n_heads_int8_rk3572.rknn yolov5n_heads_int8_rk3572.weight /userdata/
adb shell
cd /userdata/rknn3_model_test_Linux/ && export LD_LIBRARY_PATH=./lib
./rknn3_model_test /userdata/yolov5n_heads_int8_rk3572.rknn /userdata/yolov5n_heads_int8_rk3572.weight 0x1 "" "" "" 100
# ⇒ 返回 0 = 模型被 RK3572 接受 (N1 PASS); 非 0 = N1 FAIL ⇒ 转路线①/③
```

---

## 交卷单 (★交付物 / 边界 / 下一步★)

### 交付物清单 (本单新增或修改)

| 文件 | 动作 | 说明 |
|---|---|---|
| `SW/research/ISS250_rknn_toolkit2_target_查证表.md` | ★**改** ★ | ★**21 条查证行 (E-01~E-21)**: E-11/E-12 由 `[0数据·受下载速率限制]` **改判为 [实测]** (ISS-263 实跑 + 本轮复核) · 新增 E-13~E-21 (命题②③④ 的正面/反面答案 + 本轮自测) · 新增 §2 降级候选**逐条判死/判活** (8 条) · 新增 §3.2 板端**路线② 分支** ★ |
| `SW/tools/rk3572_rknn3_board_smoke.sh` | ★**新** ★ | 路线② (RKNN3) 板端验证包: P1 板型 / P3' native 库 / P4' 两件套 / P6' 双 sha256 / N1 接受性 / N3 N4 N5 · `--dry-run` rc=0 · 本机实跑判 FAIL+INDET 且 rc=1 (不假装通过) |
| `SW/tools/check_iss250_rknn_target_gate.py` | ★**新** ★ | 机器门禁 (可选第 5 件): 每条查证行有证据等级 · 4 条命题全覆盖 · 降级 ≥2 且代价/前提/谁拍非空 · 判据不许写「等回信」 · 板端清单在位 · `--selftest` 反向用例 |
| `HANDOFF/2026-11-16_sw-lead_ISS250_rknn-toolkit2_RK3572_target查证与降级方案.md` | ★**新 (本文件)** ★ | 交接单 B1~B6 + need |
| `state/fragments/sw.yaml` | ★**改 (仅 sw-lead 自己那段)** ★ | 走 `python3 state/frag_write.py --agent sw-lead …` 原子写 ★**未用 `open(p,"w")`★** |

### 边界 (本单做了什么 / 没做什么)

★**没做 (纪律)**:
- ★**零外发**: 零邮件 / 零询价 / 零问询 / 零采购 / 零原厂问询 ⇒ 全部官方信息**自己 GET 官方页面**; 查不到的标 `[0数据]` + 写降级方案 ⇒ **没有「等原厂回信」这个选项** (机器门禁 G4 已在查这句话)
- ★**没改**: `SW/tools/timing_check.py` · `SW/tools/check_demo_panel_spec.py` · `SW/tools/demo_e2e_budget.py` (★三道既有判据脚本一字未动★) · `HW/**` · `MECH/**` · `state/issue_log.yaml` (★status 留给 main★) · `PROJECT_TRACKER.md` §0 · `SW/RK3572_TARGET_COMPAT_V2.md` (只引用 + 台账同步登记 need O-6) · `SW/RKNN_BENCH.md` · **别人的分片**
- ★**没碰 PCB 布线 / 布局 / 板框**
- ★**没替老板拍板**: 60 ms 门限挂不挂 (O-3) / 换不换模型路线 (C4/O-1) ⇒ 只列选项 + 量化代价 + 推荐默认值 (★推荐 ≠ 已决定★)
- ★**没写任何板端结论为 [实测]**: 板端一律 [0数据]; [实测] 只用于本机实跑

### 下一步 (谁在什么时候做什么)

1. ★**main**: 复核本交卷单 + 查证表 ⇒ 决定 ISS-155 的 blocker 状态是否从「卡死」改写成「转换链已通 (官方 RKNN3 路线实测) / 板端接受性待板」 ⇒ ★**ISS-250 本单在 issue_log 里的 status 留给 main 落 (★我没动 issue_log★)** ★
2. ★**main → 老板**: O-1 (路线三选一) + O-2 (13.30 ms 线是否降级为观察项) + O-3 (60 ms 门限) ⇒ 进 `DECISION_PENDING_2026-11-17.md` 待拍页
3. ★**sw-lead (板到手当天)**: 跑 §B6 的两条 dry-run → 按 N1 结果自动分流 (R1 先试 ⇒ FAIL 转 R2 ⇒ R2 FAIL 启 R3) ⇒ ★**板端结论一出来就回填本查证表的 E-12 (板端那一半) 并把 N3 线重估掉** ★

> ★**本单纪律声明**: 零外发 · 板端结论一律 [0数据] · 本机数字标 [实测] 并给复现命令 · 官方页面标 [官网] 并给 URL · 媒体标 [媒体] · 推算标 [推算] 并写推导链 · ★**不把推算写成实测** (SOUL.md 铁律)★

---

## 附: 并行 sw-lead 会话留痕 (★2026-11-17 05:1x 实测发现, 必须让 main 知道★)

★**交卷复核时发现: 本单落盘期间, 另一条 sw-lead 会话 (自称「第 5 轮」, 04:5x~05:1x) 在【同一份查证表】上追加了内容★** ⇒ 实测核对结果 (逐行看过, 不是猜):

| 项 | 实测 | 结论 |
|---|---|---|
| 对方追加的内容 | `SW/research/ISS250_rknn_toolkit2_target_查证表.md` 末尾新增一节「★第 5 轮·独立复核与机器门禁★」(★E-30~E-36★) | ★**追加, 不是覆盖** ⇒ ★**本单的 §1 (E-01~E-21) / §2 (8 条降级方案) / §3 (板端两条分支) 一字未丢** (已逐行 grep 核对) ★ |
| ID 撞号 | 对方自己声明「★ID 用 E-30 起, 避免与并行会话的 E-13~E-21 撞号★」 | ★**两边 ID 不冲突** ⇒ 合并后 30 条查证行可同时成立 ★ |
| 对方新产物 | `SW/tools/check_rknn_target_compat.py` (12,648 B) · `SW/research/enum_target_r5.py` (1,459 B) · `HANDOFF/2026-11-17_sw-lead_ISS250_独立复核与target机器门禁.md` (1,433 B) | ★**两套门禁并存, 都 rc=0**: 本单的 `check_iss250_rknn_target_gate.py` ⇒ PASS rc=0 + `--selftest` 5/5 rc=0; 对方的 `check_rknn_target_compat.py` ⇒ ★**11 条判据, 8 PASS, 0 FAIL, 3 NOTE, rc=0** ★ |
| 结论是否互相矛盾 | ★**不矛盾, 互相印证** ★ | 对方 E-32「两条工具链合法 target 交集 = ∅」⇒ **与本单 E-21 (本轮自己实测的互斥) 同结论**; 对方 E-33 (两代产物的容器 magic 实测) ⇒ **给本单 E-14/E-16 (官方无跨芯片口径 + 板端库分叉) 补了根因级证据**; 对方 E-34 ⇒ **与本单 E-13 (官方 v2.5.0 仍无 rk3572) 同结论** ★ |
| 分片有没有丢 | ★**没有** ★ | `state/fragments/sw.yaml` 实测: 本单的 6 条 claim + 3 条 need + 2 条 answer ★**全部在位** (双方都用 `frag_write.py` 原子写 + 追加语义 ⇒ 没发生整段覆盖) ★ |
| 边界有没有被破 | ★**没有** ★ | 双方都没碰 `HW/` `MECH/` `issue_log` `PROJECT_TRACKER §0`; 受保护 5 件 md5 本单交卷时实测与 ISS-263 基线**逐字节一致** ★ |

★**⇒ 给 main 的口径**: ISS-250 现在有【**两份交卷单 + 两套门禁 + 30 条查证行**】(本单 = 深查版 B1~B6; 第 5 轮 = 独立复核 + 机器门禁版) ⇒ ★**两份结论同向, 可择一采信或合并采信; 建议以本单 B1~B6 为主干 (它带完整降级方案与板端两条分支), 把第 5 轮的 E-32/E-33 当补充证据收进去★** ⇒ ★**落 issue_log status 之前建议先让 main 做一次合流 (★本单不自签 issue_log★)** ★

---

## 附2: ★第 6 轮·交卷复验补记 (2026-11-17 05:2x~05:3x · sw-lead)★

★**本轮不新增任何结论, 只做一件事: 把【深查版 (本单) + 第 5 轮独立复核版】的结论整条重跑一遍, 确认盘上真值与两份交卷单写的一致 ⇒ 落查证表 E-37 一行 + 闭合一条陈旧待办★**

| 复验项 | 本轮实跑读数 | 与盘上文档是否一致 |
|---|---|---|
| toolkit2 2.3.2 config 正反两面 | `rk3572` → `ValueError: Invalid target_platform 'rk3572'!` (抛点 `rknn/api/rknn_base.py:896`) · `rk3576` → `0` | ★一致 (E-02/E-03/E-04) ★ |
| rknn3-toolkit 1.2.0 config 正反两面 | `rk3572` → `0` · `rk3576` / `rk3588` → `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` | ★一致 (E-21/E-31) ★ |
| 门禁① `check_iss250_rknn_target_gate.py` | 正向 **PASS rc=0** (查证行 31 条缺等级 0 条 / 4 命题全覆盖 / 降级方案 8 条 / 代价·谁拍·前提 三列空 0 条 / G4 外部等待类措辞 0 处 / N1~N5 在位) · `--selftest` **5/5 rc=0** | ★一致 ★ |
| 门禁② `check_rknn_target_compat.py` | **12 条判据 = 9 PASS / 0 FAIL / 3 NOTE, rc=0** · `--selftest` 改坏产物 magic ⇒ G6 转红 ⇒ **rc=1** (判据跟盘上真值走) | ★一致 (E-35) ★ |
| 板端两条分支 `--dry-run` | `rk3572_target_smoke.sh --dry-run` rc=0 · `rk3572_rknn3_board_smoke.sh --dry-run` rc=0 | ★一致 (§3) ★ |
| 三道既有判据 | `check_demo_panel_spec.py` rc=0 · `timing_check.py` SELFTEST **71/71** rc=0 · `demo_e2e_budget.py` rc=0 | ★一致 (未被本单弄红) ★ |
| 合并 + 总门 | `state/merge.py` rc=0 (产出 447 / 阻塞 43 / 未闭合需求 254 / 冲突 0) · `state/gate_check.py` rc=0 且 **Q1 18/18** | ★一致 ★ |

★**本轮落的三处增量 (全部走 `state/frag_write.py` 原子写, ★未用 `open(p,"w")`★)** ★
1. ★**查证表 E-37 一行** (⇒ 查证行 30 → 31) ⇒ `SW/research/ISS250_rknn_toolkit2_target_查证表.md` 第 6 轮节 ★
2. ★**answer 闭合陈旧待办 `iss250_e11_e12_pending_install_test`** (⇒ 该待办的内容在 ISS-263 已做完: 官方 rknn3-toolkit 1.2.0 已装 + `config('rk3572')` rc=0 + 3 次转换 rc=0 + md5 三次一致 ⇒ ★**它不该再挂着当待办**) ★
3. ★**claim `iss250_delivery_reverified_20261117_0530`** (记录本轮复验读数) + `--status` 更新 (phase=delivered / 100% / 绿) ★

★**★边界复核 (本轮实测)★**: 零外发 (本轮只跑本机脚本, 未发任何网络请求) · ★**板端接受性仍 [0数据]** (复验不使其变绿) ★ · 未碰 `HW/` `MECH/` · 未改 `state/issue_log.yaml` (status 留给 main) · 未改 `PROJECT_TRACKER.md` §0 · 未改三道既有判据脚本 · 未写别人的分片 · ★**未替老板拍板** (路线取舍 O-1 / 13.30 ms 线 O-2 / 60 ms 门限 O-3 仍是老板级)★

★**复验时间**: 2026-11-17 05:21 GMT+8 · ★**给 main 的口径不变**: 两份交卷单同向, 建议以本单 B1~B6 为主干, 把第 5 轮 E-32/E-33 当补充证据, 第 6 轮 E-37 当「一致性复验凭证」★
