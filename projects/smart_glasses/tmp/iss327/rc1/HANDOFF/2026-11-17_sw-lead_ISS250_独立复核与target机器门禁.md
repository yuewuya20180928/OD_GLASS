# HANDOFF · ISS-250 · sw-lead 交卷单 —— 第 5 轮·独立复核 + target 事实闸 (★事实/产物侧★)

| 项 | 值 |
|---|---|
| **单号** | ★**ISS-250** (★第 5 轮 · 本轮不是重开单: 是【把题面结论自己重测一遍】+【把事实钉成可复跑的机器闸】+【把 RK3572 产物从易失的 /var/tmp 归档到仓库】★) ★ |
| **owner** | ★**sw-lead** (软件总工) ★ |
| **verify_by** | ★**main** (项目总工) ★ |
| **交卷时刻** | ★**2026-11-17 05:2x (GMT+8)** ★ |
| **根因单** | ★**ISS-155** (open · blocker · demo 头号卡点) ★ |
| **地界 (本轮只动这些)** | ★**① `SW/research/ISS250_rknn_toolkit2_target_查证表.md` (★只【追加】E-30~E-36 一节, 老字零删除★) · ② 本交接单 · ③ `SW/research/ISS250_r5_复现包.md` (新) · ④ `SW/tools/check_rknn_target_compat.py` (新 · 事实闸) · ⑤ `SW/artifacts/models/rk3572_rknn3/` (新 · RK3572 产物落盘归档) · ⑥ `logs/iss250_r5/` (新 · 原始日志) · ⑦ `state/fragments/sw.yaml` (★走 `state/frag_write.py` 原子写★)** ★ |
| **零外发** | ★**本单零外发**: 不发信 / 不询价 / 不问询 / 不采购 / 不联系任何供应商 ⇒ ★**只 GET 官方公开页面 (GitHub raw + GitHub API) + 只在本机实跑** ★ |
| **实物 [实测]** | ★**本机实跑 5 组 (枚举×3 + 门禁×2) + 产物字节级检查×2 对 + 归档 sha256 校验×4** ⇒ ★**板端 0 条 (板不可达, 这一层本轮不假装)** ★ |
| **不代拍** | ★**板到底用 rk3572 还是 rk3576 = 老板级 ⇒ 本单只给「哪个能用 + 代价」, 不代拍** ★ |

---

## B1 结论摘要 (★一句话 + 拆解★)

★**一句话**: ★**题面「rk3572 不是 rknn-toolkit2 合法 target」本轮独立复核成立 (不是抄别人结论); ★并且本轮把这条事实链补出了三个以前没被写成判据的硬结论 (两条工具链合法 target 交集 = ∅ / 两代产物容器 magic 不同 / 「升级 toolkit2 就有 rk3572」这条路截至今天仍关闭), 外加一个可复跑的【事实闸】与一份抗 /var/tmp 的 RK3572 产物归档。★**

| 序 | 结论 | 关键数字 | 判定 |
|---|---|---|---|
| **①** | ★**题面结论成立: `rknn-toolkit2 2.3.2` 的合法 target 恰好 11 个 = `rv1103` `rv1103b` `rv1106` `rv1106b` `rv1126b` `rk2118` `rk3562` `rk3566` `rk3568` ★**`rk3576`**★ `rk3588` ⇒ `rk3572` / `rk3572b` 双双 `ValueError`★ | ★**本轮自写脚本 `SW/research/enum_target_r5.py`, 30 候选全跑完, 耗时 0.317 s** ★ | ★**✅ [实测]** ★ |
| **②** | ★**新结论: `rknn3-toolkit 1.2.0` 的合法 target 全集 = 7 个 = `gongga2` `rk1820` `rk1828` `rk182x` `rk1860` `rk186x` ★**`rk3572`**★ ⇒ ★**它拒绝 `rk3576` / `rk3588` / 全部 `rk356x` / 全部 `rv11xx` (与 toolkit2 正好相反)★** ⇒ ★**★官方 README 只写「Supported Platforms: RK1820/RK1828/RK3572」, 这个可编程的 target 全表是本机枚举出来的 (以前盘上没有)★** ★ | ★**30 候选 0.287 s + 补测 `rk182x`/`rk1860`/`rk186x` ⇒ 7/7 全 `ret=0`** ★ | ★**✅ [实测]** ★ |
| **③** | ★**★新结论 (根因级): 两条工具链的合法 target 交集 = ∅ (空集) ⇒ 路线① (rk3576 产物) 与 路线② (rk3572 产物) 在【产物层面不可互换】★ ⇒ ★**板端验的时候必须先说清自己验的是哪一代产物, 否则 runtime 报「格式不认识」会被误判成「模型不对」★** ★ | ★**11 ∩ 7 = ∅ (集合运算, 脚本判据 G5)★** | ★**✅ [实测]** ★ |
| **④** | ★**★新结论 (根因级): 两代产物的容器格式不同 —— toolkit2 产物 magic = `RKNN` (0x524B4E4E, 单文件, 内嵌 JSON 明写 `"target_platform":["rk3576"]` / `"version":"2.3.2"`); rknn3 产物 magic = `RKNX` (0x524B4E58) + 伴生权重 `RKNX-W` (两件套) ⇒ ★**板端跑 RK3572 产物要的是【RKNN3 代 runtime】, 不是 RKNN2 的 `librknnrt`; 且 `.rknn` + `.weight` 必须一起拷, 少一个必失败★** ★ | ★**2 个 magic + 2 个文件头 hexdump (本轮 xxd 实测)★** | ★**✅ [实测]** ★ |
| **⑤** | ★**「升级 rknn-toolkit2 就能拿到 rk3572」这条路, 截至 2026-11-17 05:1x 仍然关闭**: toolkit2 最新 release 仍 `v2.5.0` (published 2026-10-20), release notes 全文无 RK3572 字样; rknn3-toolkit 最新 release 仍 `v1.2.0` (published 2026-11-05) ⇒ ★**RK3572 的官方路径只有 rknn3-toolkit 一条** ★ | ★**2 次 GitHub API 实抓 (releases 列表)★** | ★**✅ [官网]** ★ |
| **⑥** | ★**本轮新产出【事实闸】`SW/tools/check_rknn_target_compat.py`**: 12 条判据 (版本×2 / 合法集×2 / ★**互斥不变量**★ / 容器 magic×2 / md5 锚点 / sha256 sidecar 自洽 / ★**板端接受性恒为 NOT_VERIFIED★**) ⇒ ★**rc=0 (9 PASS / 0 FAIL / 3 NOTE)· 反向自证把产物 magic 改坏 ⇒ rc=1 (G6 变红) ⇒ 判据跟盘上真值走, 不是摆设** ★ | ★**正向 rc=0 · 反向 rc=1 (两轮都实跑, 日志在盘)★** | ★**✅ [实测]** ★ |
| **⑦** | ★**RK3572 产物已从易失的 `/var/tmp` 归档进仓库**: `SW/artifacts/models/rk3572_rknn3/` = heads 版 (`.rknn` 249,360 B + `.weight` 1,960,448 B) + 整模型版 (`.rknn` 339,992 B + `.weight` 7,353,856 B) + 各自 `.sha256` sidecar + `.meta.json` (记 toolchain / 源 ONNX md5 / 三次 build 耗时 / md5 锚点 / ★**板端接受性 = NOT_VERIFIED [0数据]★**) ⇒ ★**sha256 sidecar 自洽 4/4 OK** ★ | ★**4 个文件 + 2 sidecar + 2 meta.json★** | ★**✅ [实测]** ★ |
| **⑧** | ★**板端接受性仍 = [0数据] (板不可达)** ⇒ ★**但本单不把它挂成「等外部回复」**: ★**板到手后的两段式验法已写好** —— ① 先用【官方预转换模型】(RKNN3_SDK/rknn3_models/v1.2.0, 云盘访问码 `rknn`) 验「板端 RKNN3 Runtime 本身能不能跑」, ② 再上我们自己的 rk3572 产物 (`.rknn` + `.weight` 两件套) ⇒ ★**两段各出 1 份日志 + 1 份失败归属结论 (runtime 层 / 模型层), 不许把 runtime 不支持误判成模型不对** ★ | ★**官方 README「Cloud Drive Resources」段 (web_fetch 实抓)★** | ★**✅ [官网] + 板端 [0数据]★** ★ |

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

### 2.1 本轮任务书 (ISS-250 第 5 轮) 要求的 4 件交付物

| 序 | 要求 | 本轮实测结果 | 判定 |
|---|---|---|---|
| **V-1** | ★**① 查证表: 一个表, 每行 = 「查了什么 / 去哪查 / 结论 / 证据等级」, 至少覆盖 ①版本与 target 列表 ②rk3572 在不在 ③若不是, rk3576 是不是 / rk3572 走哪条路 ④能不能自编 toolkit2★** ★ | ★**表已在盘 (`SW/research/ISS250_rknn_toolkit2_target_查证表.md`, 现 36 行查证记录: E-01~E-21 + 本轮 E-30~E-36)★** ⇒ ★**本轮补的 7 行 (E-30~E-36) 覆盖: ①① ③④ 全部; ④「能不能自编」也已由前几轮 E-07 落定 (★rknn3-toolkit = 预编译 wheel, 不是源码可编★)** ★ | ★**✅ 通过** ★ |
| **V-2** | ★**② ≥2 条降级方案 (各带量化代价 + 启用条件 + 谁拍)★** ★ | ★**表内已有 8 条降级候选 (并行会话补齐, 含代价/前提/谁拍三列, 本轮未动)⇒ 本轮补的是【降级方案的量化代价底座】: 路线② 的下载/安装成本已由 ISS-263 实测填实 (转换 33.389/34.108/41.672 s, 产物 md5 3 次一致)★** | ★**✅ 通过 (主线已在盘, 本轮补量化底座)★** ★ |
| **V-3** | ★**③ 板端可达时的执行清单: 一条命令 + 逐条步骤 + 量化判据 (转换耗时 / 精度掉点 / 首个推理耗时)★** ★ | ★**一条命令 = `bash SW/tools/rk3572_target_smoke.sh --artifact … --expect-sha256 … --images 300 --out … --power-note …` (★本机 `--dry-run` 可先跑, rc=0 只打印板端将执行的每一条命令★)⇒ 判据 N1~N5 量化: ★**N1 `load_rknn` ret==0 且 `init_runtime` ret==0 · N2 F1 ≥ 0.2427 · N3 纯 NPU ≤ 13.30 ms [推算] / 13.30<t_sdk≤20.33 ⇒ INDET / >20.33 ⇒ 命中 T2 · N4 纯硬件与 SDK 总耗时必须分开报 · N5 散热/频率/供电三项齐全**★ ⇒ **本轮新增路线②分支 (官方垫刀模型先验 runtime) + 两件套必拷** ★ | ★**✅ 通过** ★ |
| **V-4** | ★**④ 交卷单 + 分片 + (若产出新门禁) 机器门禁★** ★ | ★**交卷单 = 本文件 (B1~B6 齐全) · 分片 = 走 `state/frag_write.py --agent sw-lead` 原子写 · 机器门禁 = 本轮新增 `SW/tools/check_rknn_target_compat.py` (rc=0 + 反向 rc=1)** ★ | ★**✅ 通过** ★ |

### 2.2 本轮自加的 3 条 (★因为第 4 轮同类缺口吃过亏★)

| 序 | 自加要求 | 实测结果 | 判定 |
|---|---|---|---|
| **S-1** | ★**第 1 分钟先落盘骨架 (★上一轮死因 = 10 分钟全攒内存被 timeout 掐死★)** ★ | ★**05:07:33 先落交卷单骨架 (1,433 B) 再查; 每抓到一条立刻写进盘上的表 (E-30~E-36 逐条 append, 不是攒到最后)** ★ | ★**✅ 通过** ★ |
| **S-2** | ★**本轮结论必须可被【别人 30 秒自己复现】⇒ 复现包 + 原始日志齐全★** ★ | ★**`SW/research/ISS250_r5_复现包.md` (4 条命令) + `logs/iss250_r5/` 5 份原样日志 (枚举×3 + 门禁×2)★** | ★**✅ 通过** ★ |
| **S-3** | ★**本机产出的 RK3572 产物不许留在易失的 /var/tmp★** ★ | ★**已归档 `SW/artifacts/models/rk3572_rknn3/` + sha256 sidecar 4/4 OK + meta.json (含板端接受性 = NOT_VERIFIED, 防止后人误当「板端已验」)** ★ | ★**✅ 通过** ★ |

---

## B3 证据分级 (★实测 / 官网 / 推算 / 0数据★)

| 序 | 结论 | 证据等级 | 出处 (可点开) |
|---|---|---|---|
| **1** | ★**toolkit2 2.3.2 合法 target = 11 个, 不含 rk3572 / rk3572b** ★ | ★`[实测]` ★ | ★`logs/iss250_r5/enum_toolkit2_rknn_env.log` + `SW/research/enum_target_r5.py`★ |
| **2** | ★**rknn3-toolkit 1.2.0 合法 target = 7 个, 含 rk3572, 不含 rk3576** ★ | ★`[实测]` ★ | ★`logs/iss250_r5/enum_rknn3_env.log` + `enum_rknn3_legalset.log`★ |
| **3** | ★**两条线合法 target 交集 = ∅ ⇒ 路线①②产物不可互换** ★ | ★`[实测]` ★ | ★同上 + 门禁判据 G5 (`logs/iss250_r5/gate_run.log`)★ |
| **4** | ★**两代产物容器 magic 不同 (`RKNN` vs `RKNX` + `RKNX-W`); toolkit2 产物内嵌 `target_platform:["rk3576"]`** ★ | ★`[实测]` ★ | ★本机 xxd/strings 实测 + 门禁 G6/G7★ |
| **5** | ★**toolkit2 最新 release 仍 v2.5.0 (2026-10-20) 且 notes 无 RK3572; rknn3 最新 release 仍 v1.2.0 (2026-11-05)** ★ | ★`[官网]` ★ | ★GitHub API `repos/airockchip/rknn-toolkit2/releases` + `…/rknn3-toolkit/releases` (web_fetch 实抓 2026-11-17 05:1x)★ |
| **6** | ★**RKNN3 板端栈 = RKNN3 Runtime + RKNN3-Toolkit Lite; RK3572 = 非协处理器模式 (NPU 在 SoC 内, 模型直接跑在板上); 官方导出产物 = `.rknn` + `.weight` 两件** ★ | ★`[官网]` ★ | ★`https://raw.githubusercontent.com/airockchip/rknn3-toolkit/master/README.md` (web_fetch, 13,925 B 全文)★ |
| **7** | ★**官方提供预转换模型包 `RKNN3_SDK/rknn3_models/v1.2.0` (云盘, 访问码 `rknn`) ⇒ 可作板端「垫刀模型」** ★ | ★`[官网]` ★ | ★同 README「Cloud Drive Resources」段★ |
| **8** | ★**rknn3 转 rk3572 的耗时与可复现性: t_total 33.389 / 34.108 / 41.672 s (build 33.231 / 34.035 / 41.595 s), 3 次产物 md5 完全一致 `97a34fff…`** ★ | ★`[实测]` ★ | ★`logs/iss263/convert_rk3572_3runs.log` (ISS-263 原始日志)★ |
| **9** | ★**★板端接受性 (RK3572 能不能吃这个 .rknn)★** ★ | ★**`[0数据]` (★板不可达 ⇒ 本轮明确写「未验」, 不许含糊成「应该可以」★)** ★ | ★**板端日志 0 条 (本机无板)** ★ |
| **10** | ★**板端纯 NPU 耗时能否落在 13.30 ms 内 (60 ms 硬线相关)★** ★ | ★`[推算]` (★沿用 `HW/e2e_budget_rk3572.py` 预算口径, 板端实测出来之前只是推算★)** ★ | ★**板端未测 ⇒ N3 判据保持「INDET 分档」而不是给一个假数** ★ |

---

## B4 接口取值声明 (interface_claims)

```yaml
iss250_rknn3572_target_status:
  value: >-
    ★rk3572【不存在】于 rknn-toolkit2 (本机 2.3.2 实测合法 11 个, 官方最新 v2.5.0 notes 亦无 RK3572);
    ★RK3572 的官方路径 = rknn3-toolkit 1.2.0 + target_platform='rk3572' (本机已装, config() rc=0, 已转出 .rknn + .weight)。
  evidence: ★[实测] (两条 env 各枚举 30 候选) + [官网] (GitHub releases / README)
  ref: SW/research/ISS250_rknn_toolkit2_target_查证表.md (E-02/E-03/E-13/E-21 + 本轮 E-30/E-31)

iss250_toolchain_target_mutex:
  value: >-
    ★两条工具链的合法 target 集合【交集 = ∅】(toolkit2 的 11 个 ∩ rknn3 的 7 个 = 空)
    ⇒ ★路线① (rk3576 产物) 与 路线② (rk3572 产物) 不可互相顶替; 板端验时必须声明验的是哪一代产物。
  evidence: ★[实测]
  ref: SW/tools/check_rknn_target_compat.py (判据 G5) · logs/iss250_r5/gate_run.log

iss250_artifact_container_generation:
  value: >-
    ★toolkit2 产物 = 单文件 magic 'RKNN', 内嵌 JSON target_platform=["rk3576"], version="2.3.2";
    ★rknn3 产物 = 两件套 magic 'RKNX' + 'RKNX-W' ⇒ ★板端 RK3572 要 RKNN3 代 runtime, 且两件套必须一起拷。
  evidence: ★[实测] (xxd / strings)
  ref: SW/tools/check_rknn_target_compat.py (判据 G6/G7) · SW/artifacts/models/rk3572_rknn3/*.meta.json

iss250_board_acceptance:
  value: '★NOT_VERIFIED [0数据] ★— 板不可达; 本单只证明【转得出来】, 不证明【板端吃不吃】。板到手后按两段式验法执行。'
  evidence: ★[0数据]
  ref: SW/research/ISS250_r5_复现包.md §6 (N1~N5) · HANDOFF/2026-11-17_sw-lead_ISS250_独立复核与target机器门禁.md (B6)

iss250_gates:
  value: >-
    ★两条闸, 口径不同, 互补不重叠:
    ① 【文档完备性闸】python3 SW/tools/check_iss250_rknn_target_gate.py ⇒ rc=0 (查证行/命题覆盖/降级代价与谁拍/无「等回信」措辞/板端清单在位)
    ② 【事实产物闸】python3 SW/tools/check_rknn_target_compat.py ⇒ rc=0 (本轮新产出: 实跑两条工具链 + 产物容器字节 + md5/sha256 锚点 + 板端恒 NOT_VERIFIED); --selftest ⇒ rc=0 (改坏产物 ⇒ 闸红 rc=1)
  evidence: ★[实测]
  ref: SW/tools/check_iss250_rknn_target_gate.py · SW/tools/check_rknn_target_compat.py · logs/iss250_r5/gate_run.log · logs/iss250_r5/gate_selftest.log
```

---

## B5 未决项与卡点 (★需要谁回答什么★)

| 序 | 未决 / 卡点 | 现状 (不挂成等外部回复) | 要谁答 | 建议 |
|---|---|---|---|---|
| **O-1** | ★**板端接受性 = [0数据]** ★ | ★**板不可达 ⇒ 已给可执行清单 + 两段式验法 + 垫刀模型路径; 不写「等板子回来再说」** ★ | ★**main 派板 → sw-lead 执行** ★ | ★**板到手当天先跑两段式: 官方垫刀模型 → 我们的 rk3572 产物** ★ |
| **O-2** | ★**现在有两条闸 (文档完备性闸 + 本轮事实产物闸), 谁是权威?** ★ | ★**两条都 rc=0, 口径不重叠 (一个查文档, 一个查事实与产物字节)** ★ | ★**main** ★ | ★**建议两条都留, 但对外口径以【事实产物闸】为准 (它对着盘上真值跑, 文档闸只保证写得齐)** ★ |
| **O-3** | ★**本单期间发现【同一查证表被两个 sw-lead 会话同时写】(并行会话写 E-13~E-21, 本轮写 E-30~E-36) ⇒ 交卷单也出了两份** ★ | ★**本轮已避让: ID 用 E-30 起不撞号, 追加不改老字, 两份交卷单文件名不同且互相引用** ★ | ★**main (派活侧)** ★ | ★**建议同一 issue 同时只派一个 sw-lead 会话; 确实要并行, 规定【ID 段位 + 只许追加不许重写】** ★ |
| **O-4** | ★**板到底用 rk3572 还是 rk3576** ★ | ★**本单只给「哪个能用 + 代价」: rk3572 官方路径已通到【转得出来】, 但板端接受性未验 + RK3572 从 V1.0.4 起官方仍标 Beta; rk3576 路径本机成熟 (产物在盘 + PC F1 = 0.29265) 但板端接受性同样未验** ★ | ★**★老板 (★我不代拍★)** ★ | ★**板端实测数据出来后再拍; 在此之前任何一边的「能跑」都不许当成结论** ★ |
| **O-5** | ★**RK3572 产物的源 ONNX (`model_heads.onnx`, 7,520,239 B, sha16 `adac68f888bf61c2`) 仍只在 `/var/tmp/iss263_rknn3/work/`** ★ | ★**本轮只归档了【产物】(含 meta.json 记源 md5 / sha16), 源 ONNX 未归档 (★7.5 MB, 是否入库请你拍★)** ★ | ★**main** ★ | ★**建议把源 ONNX 一并归档进 `SW/artifacts/models/rk3572_rknn3/`, 否则产物只能【验】不能【重转】** ★ |

---

## B6 自证复现命令 (★本机全部已实跑, 贴原文★)

```bash
# ① 本轮新产出的【事实产物闸】⇒ 期望 rc=0
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_rknn_target_compat.py
#   实测输出 (原样, logs/iss250_r5/gate_run.log):
#     [PASS] G1   toolkit2 版本 == 2.3.2
#     [PASS] G2   toolkit2 合法 target 集合 == 期望 11 个
#     [NOTE] G2b  toolkit2 对 rk3572 的态度   (rk3572 ∈ 合法集 = False ; rk3572b ∈ 合法集 = False)
#     [PASS] G3   rknn3-toolkit 版本 == 1.2.0
#     [PASS] G4   rknn3 合法 target 集合 == 期望 7 个
#     [NOTE] G4b  rknn3 对 rk3576 / rk3588 的态度 (两者 ∈ 合法集 = False)
#     [PASS] G5   ★互斥不变量★: 两条工具链合法 target 交集 == 空集   (交集 = ∅)
#     [PASS] G6   toolkit2 产物容器 == b'RKNN' 且内嵌 target_platform == [rk3576]
#     [PASS] G7   rknn3 产物容器 == b'RKNX' 且伴生 .weight == b'RKNX-W' (两件套缺一不可)
#     [PASS] G8   rknn3 产物 md5 锚点 == 3 次转换实测一致值 (97a34fff…)
#     [PASS] G8b  落盘归档 sha256 sidecar 自洽 (两件套都在) (OK ; OK)
#     [NOTE] G9   ★板端接受性 = 未验★   BOARD_ACCEPTANCE = NOT_VERIFIED [0数据]
#     SUMMARY: 12 条判据, 9 PASS, 0 FAIL, 3 NOTE (NOTE 不等于绿)

# ② 反向自证 ⇒ 期望 rc=0 (内部把产物 magic 改坏 ⇒ 闸必须红 rc=1)
python3 SW/tools/check_rknn_target_compat.py --selftest
#   实测 (logs/iss250_r5/gate_selftest.log): 改坏后 rc = 1 (期望 1) ⇒ [SELFTEST] PASS 判据抓得住坏产物

# ③ 两条工具链的合法 target 全集 (自己枚举, 不抄文档)
/home/yuewuya/miniconda3/envs/rknn/bin/python  SW/research/enum_target_r5.py   # ⇒ ACCEPTED_COUNT: 11
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/research/enum_target_r5.py   # ⇒ ACCEPTED_COUNT: 4 (30 候选内) + 补测 ⇒ 全集 7

# ④ 两代产物容器 magic (根因级证据)
xxd -l 16 SW/artifacts/models/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn  # ⇒ 524b4e4e = 'RKNN'
xxd -l 16 SW/artifacts/models/rk3572_rknn3/yolov5n-sim_heads_rk3572_int8_heads.rknn      # ⇒ 524b4e58 = 'RKNX'
xxd -l 16 SW/artifacts/models/rk3572_rknn3/yolov5n-sim_heads_rk3572_int8_heads.weight     # ⇒ 524b4e582d57 = 'RKNX-W'

# ⑤ 归档 sha256 自洽
cd SW/artifacts/models/rk3572_rknn3 && sha256sum -c *.sha256

# ⑥ 板端清单 (板未到时先 dry-run ⇒ rc=0, 只打印板端将执行的每一条命令)
bash SW/tools/rk3572_target_smoke.sh --artifact ./yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn \
  --expect-sha256 $(awk '{print $1}' yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn.sha256) \
  --images 300 --out ./evidence/ISS250_$(date +%Y%m%d) --power-note "<供电方式>"
```

---

## ★验收 rc 汇总 (2026-11-17 05:1x~05:2x · 本机实跑 · 原文贴盘 `logs/iss250_r5/acceptance_rc.log`)★

| # | 命令 | rc | 关键输出 |
|---|---|---|---|
| **1** | ★`python3 SW/tools/check_rknn_target_compat.py` ★ | ★**0** ★ | ★`SUMMARY: 12 条判据, 9 PASS, 0 FAIL, 3 NOTE` + `BOARD_ACCEPTANCE = NOT_VERIFIED [0数据]`★ |
| **2** | ★`python3 SW/tools/check_rknn_target_compat.py --selftest` ★ | ★**0** ★ | ★`改坏后 rc = 1 (期望 1)` ⇒ `[SELFTEST] PASS 判据抓得住坏产物`★ |
| **3** | ★`python3 SW/tools/check_iss250_rknn_target_gate.py` (★并行会话的文档完备性闸, 本轮复跑确认没被我的追加弄红★) ★ | ★**0** ★ | ★`G4_no_wait_for_reply … 0 处` + `G5_board_checklist_present 在位` ⇒ `PASS (rc=0)`★ |
| **4** | ★`python3 state/merge.py` ★ | ★**0** ★ | ★`STATE.yaml 已刷新` · 产出 438 / 阻塞 43 / 未闭合需求 252 / 冲突 0★ |
| **5** | ★`python3 state/gate_check.py` ★ | ★**0** ★ | ★`Q1 18/18` + `Q2 3/3` + `Q3 sw-lead 230 条`★ |
| **6** | ★`python3 state/issue_check.py` ★ | ★**0** ★ | ★`问题闭环门全过`★ |
| **7** | ★`(cd SW/artifacts/models/rk3572_rknn3 && sha256sum -c *.sha256)` ★ | ★**0** ★ | ★**4 个文件全 OK** (两件套都在)★ |
| **8** | ★**受保护 5 件 md5 (交卷前后逐字节不变)** ★ | ★**—** ★ | ★网表 `e06c1dd6…` · 脚表 `287e7861…` · BOM `94642d07…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` (★与 main ISS-263 verify 时逐字一致★)★ |
| **9** | ★**本交卷单 B1~B6 机器判定** ★ | ★**6/6** ★ | ★`B1~B6 全 True` + `evidence_tags = [实测, 官方, 推算, 0数据] (4/4)`★ |

---

## 交卷单 (★交付物 / 边界 / 下一步★)

### 交付物清单 (本单新增或修改)

| 文件 | 状态 | 内容 |
|---|---|---|
| ★`HANDOFF/2026-11-17_sw-lead_ISS250_独立复核与target机器门禁.md` ★ | ★**新** ★ | ★本交卷单 (B1~B6 齐全)★ |
| ★`SW/tools/check_rknn_target_compat.py` ★ | ★**新** ★ | ★事实产物闸 (12 条判据 + `--selftest` 反向自证)★ |
| ★`SW/research/ISS250_r5_复现包.md` ★ | ★**新** ★ | ★4 条命令复现入口 + 原始日志清单 + 板端清单 (N1~N5)★ |
| ★`SW/artifacts/models/rk3572_rknn3/` ★ | ★**新** ★ | ★RK3572 产物归档 (2 组两件套 + sha256 sidecar + meta.json), ★**抗 /var/tmp 被清**★ |
| ★`logs/iss250_r5/` ★ | ★**新** ★ | ★枚举×3 + 门禁×2 + ★**`acceptance_rc.log` (9 条验收命令 rc 汇总)★** 原始日志★ |
| ★`SW/research/ISS250_rknn_toolkit2_target_查证表.md` ★ | ★**追加一节 (E-30~E-36), 老字零删除** ★ | ★本轮 7 条独立复核证据 + 机器闸引用★ |
| ★`state/fragments/sw.yaml` ★ | ★**追加** ★ | ★走 `python3 state/frag_write.py --agent sw-lead …` 原子写★ |

### 边界 (本单做了什么 / 没做什么)

· ★**零外发**: 零邮件 / 零询价 / 零问询 / 零采购 / 零原厂问询 ⇒ ★**只 GET 官方公开页面 (GitHub raw + GitHub API) + 只在本机实跑** ★
· ★**没碰 `HW/` 与 `MECH/` 任何文件 · 没碰板 / PCB 布线 / 布局** ★
· ★**没改 `PROJECT_TRACKER.md` §0 · 没自签 `state/issue_log.yaml` (verify 留给 main)** ★
· ★**没替老板拍板**: ★**板用 rk3572 还是 rk3576 仍是老板级决定; 本单只给「哪个能用 + 代价」** ★
· ★**没把板端结论含糊掉**: ★**板端 = [0数据] 明写在 B1⑧ / B3⑨ / G9 判据 / 产物 meta.json 四处** ★
· ★**没覆盖并行会话的成果**: ★**本轮对 `SW/research/ISS250_rknn_toolkit2_target_查证表.md` 只追加不重写, ID 用 E-30 起避让; 并行会话的交卷单与文档完备性闸原样保留** ★

### 下一步 (谁在什么时候做什么)

| 谁 | 什么时候 | 做什么 |
|---|---|---|
| ★**main** ★ | ★**本单 verify 时** ★ | ★**跑两条闸** (`check_iss250_rknn_target_gate.py` + `check_rknn_target_compat.py`) ⇒ 都 rc=0 才算过; ★**并裁一下 O-2 (两条闸的权威口径) 与 O-3 (同一 issue 并行派活纪律)** ★ |
| ★**sw-lead** ★ | ★**板到手当天** ★ | ★**按两段式验法跑板端清单**: ① 官方垫刀模型验 RKNN3 Runtime ② 我们的 rk3572 产物 (.rknn + .weight 两件套) ⇒ 出 2 份日志 + 1 份失败归属结论 (runtime 层 / 模型层) ★ |
| ★**main** ★ | ★**板端数据出来后** ★ | ★**把 ISS-155 的 blocker 口径改成实测结论 (转换链已通 / 板端接受性已验或已否)**, ★**并把「rk3572 vs rk3576」的取舍连同代价表交老板拍** ★ |
| ★**sw-lead** ★ | ★**O-5 获准后** ★ | ★**把源 ONNX 归档进 `SW/artifacts/models/rk3572_rknn3/`, 让 RK3572 产物从【只能验】变成【能重转】** ★ |

---

> ★**本单零外发 · 未碰 HW/ 与 MECH/ · 未改 PROJECT_TRACKER.md §0 · 未自签 issue_log · 未替老板拍板** ★
> ★**交卷人**: sw-lead (软件总工) · ★**交卷时刻**: 2026-11-17 05:2x (GMT+8) · ★**verify_by**: main ★
