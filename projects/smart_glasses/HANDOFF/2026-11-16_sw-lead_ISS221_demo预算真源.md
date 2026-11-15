# [sw-lead→PM] ISS-221 · demo 预算真源脚本 (2 通道 @480×640) + 判据链换真源 + 机器门禁

- 发起方: sw-lead
- 日期: 2026-11-16
- 结论: **demo 屏 (2-lane @480×640) 有了自己的 60ms 预算真源脚本 `SW/tools/demo_e2e_budget.py`** ⇒ demo 判据链里的每一个预算数 (TX 物理下限 / 合成段上限 / 显示输出侧 / 60ms 全链路余量) **不再从整机脚本减出来, 改为由 demo 脚本算出** ⇒ 机器门禁 `SW/tools/demo_timing_check.py` 新增 **17 条 ISS-221 断言** (锚点区块逐项比对 + 整机 4-lane 指纹扫描 + 判据工具必须是 demo 脚本 + 「表 A」逐行比对) ⇒ **改坏必红 (7 条反向用例全抓到)** ⇒ 板端 [实测] = **0 条**, 屏侧全部 [推算]
- 依据:
  - `SW/tools/demo_e2e_budget.py` (新建, 33823 B, md5 `ee64b86a945fd857044484c1d16d3a63`)
  - `SW/tools/demo_timing_check.py` (加 ISS-221 门禁, md5 `a6e891f1f22a7831fe99fa2650639d7a`)
  - `SW/DEMO_OD_TIMING_SPEC.md` (md5 `576d239138565b1112a827f9f983f839`) · `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` (md5 `226da72bfd3cdba2fe63cfa3d82fa3e3`)
  - `SW/RKNN_BENCH.md` §4.1 L273 (S9 注记同步, md5 `ed080fa0188d91a2cacf27c8073a3155` → `46ac25e1eb96ee296e60cb37485524f9`)
  - 只读引用 (本单一个字没动): `HW/e2e_budget_rk3572.py` md5 `7b820c14acfaee08a218cbf85557ef0b` (mtime 2026-11-11 05:37)

---

## ★0. 本单是【续做】: 上一轮 (`agent:sw-lead:subagent:6da17eee`) 超时死了, 盘上留了半成品

★**main 2026-11-16 04:1x 的转述我逐条自己核过 (开工前), 结论如下 (以盘上实况为准)**:

| 交付物 | 上一轮留的状态 (2026-11-16 03:5x 实测) | 本单处置 |
|---|---|---|
| ① `SW/tools/demo_e2e_budget.py` | **已在盘** (33823 B, mtime 02:22:59) ⇒ **不是半成品, 是完整件** | **不重写**。实跑 rc=0 / `--selftest` 31/31 全过; 另**独立手算复核**了算术 (见 B1-②) ⇒ 保留原样, 只在交接单里登记 |
| ② 两份规格文件换数 | **已在盘** (02:23:20 / 02:23:32) ⇒ 已换成脚本输出 | **不重写**。新增门禁逐项比对 → **11/11 项全对上 + 「表 A」3 行全对上** |
| ③ `SW/tools/demo_timing_check.py` 门禁 | mtime 02:26:07 ⇒ ★**只写了常量、没写检查函数** ⇒ 门禁是**空的** (跑出来 34/34 里 **一条 ISS-221 断言都没有**) ⇒ **等于没做** | ★**本单补齐**: 新增 `check_demo_budget_source()` + 7 条反向用例 ⇒ 34/34 → **51/51**, `--selftest` 10/10 → **18/18** |
| ④ 交接单 + 分片 | **HANDOFF 缺 / `state/fragments/sw.yaml` mtime = 01:58 (没写)** | **本单补齐** ⇒ 见 §B6-⑧ 的两条验盘命令 |
| ⑤ `SW/RKNN_BENCH.md` §4.1 L273 | mtime 2026-11-12 02:25:56 ⇒ **没动** | **本单同步** (ISS-215 交接单 B5-① 请求授权的那一行) ⇒ md5 前后对照见 §B6-⑦ |

### ★0.1 上一轮留的**两个真毛病** (本单已修, 记录在案)

★**毛病 1 — ③ 的门禁是空壳 (不是"半成品", 是"没做")**:
上一轮在 `demo_timing_check.py` 里写了 `DEMO_BUDGET` / `ANCHOR_BEGIN` / `ANCHOR_END` / `MACHINE_DSI_FINGERPRINTS` / `MACHINE_SCRIPT_INVOKE` / `MACHINE_EXEMPT_MARKERS` 六个常量 (L42~L66), **然后就没了** ——
`grep -n 'ISS-221' SW/tools/demo_timing_check.py` 在写检查函数之前只有**常量定义处**命中 ⇒ 门禁**从来没生效过** ⇒ ★**「换屏 / 改分辨率 / 改通道数时, 没有人拦得住又拿整机常量扣 demo 预算」这个洞, 上一轮并没有堵上**。

★**毛病 2 — 那半个常量里有一个会让门禁【对正确文档误报红】的真错**:
上一轮写的 `MACHINE_DSI_FINGERPRINTS = ["4-lane", "4 通道", "@2.0Gbps", "80% 效率"]` ——
★**`"@2.0Gbps"` 与 `"80% 效率"` 根本不是整机指纹**: ★**demo 口径 A 本身就是「2 通道 × 2.0 Gbps × 80% 效率」** (ISS-212 §2 定版, `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` L67) ⇒
照抄成门禁, 会把**完全正确的** `SW/DEMO_OD_TIMING_SPEC.md` **L230**「demo 活动口径: 2-lane D-PHY@2.0Gbps × 80% = 3200 Mbps 有效」判成红。
⇒ ★**本单改成只收能唯一指向整机 4-lane 账本的写法**: `["4-lane", "4 lane", "4 通道", "6400 Mbps"]` (6400 Mbps = 4×2.0×0.8, 整机 4-lane 有效带宽; demo 口径 A 是 3200 Mbps, 两者不撞)。

---

## B1 结论摘要

**① demo 屏有了自己的预算真源脚本, 而且口径是分层的** ★[实测·本机脚本]
`SW/tools/demo_e2e_budget.py` 把「整机同源常量」和「demo 专属常量」**物理隔开**, 两类不许混:
- **(A) 整机同源常量 (只引用, 不重算整机的账)**: `T_FIXED_OTHER = 31.00 ms` (= 曝光块 24.67 + 画框 1.00 + 光机 5.00 + 反解余量 0.33) · `POST_MS = 5.60` · `FRAME_MS = 16.67` · 显示输出侧占位 `S9 = 3.00` (只做缩放基准) —— ★**与 `HW/e2e_budget_rk3572.py` 同名同值** (逐项核对过: 该文件 L35/37/51/53/55/57 一致)
- **(B) demo 专属常量 (本脚本的真源)**: 480×640 (307200 px) · **DSI 通道数 = 2** · RGB888 24 bit/px · 口径 A = 2.0 Gbps/通道 × 80% · 口径 B = 1.8 Gbps/通道 × 100% · 每帧固定开销 = 0 bit · 缩放除数 6.75 · 60ms 硬预算
- ★**本脚本源码里零整机 DSI 常量** (自带「源码泄漏扫描」, 反向用例盯着)

**② 我把上一轮的算术独立手算复核了一遍 (不信脚本自证)** ★[实测·本机手算 vs 脚本输出]
| 量 | 手算 | 脚本输出 | 一致 |
|---|---|---|---|
| demo TX (口径 A) | 480×640×24 = 7372800 bit ÷ (2×2.0Gbps×80% = 3.2Gbps) = **2.3040 ms** | 2.304 | ✅ |
| demo TX (口径 B) | 7372800 ÷ (2×1.8Gbps×100% = 3.6Gbps) = **2.0480 ms** | 2.048 | ✅ |
| 缩放除数 | 2073600 ÷ 307200 = **6.75** | 6.75 | ✅ |
| t_compose [推算] | 3.00 ÷ 6.75 = **0.4444 → 0.44 ms** | 0.44 | ✅ |
| 显示输出侧 [推算] | 0.4444 + 2.304 = **2.7484 → 2.75 ms** | 2.75 | ✅ |
| 输出侧总额上限 (yolov5n@640) | 60 − 31.00 − (13.31 + 5.60) = **10.09 ms** | 10.09 | ✅ |
| 合成段上限 (yolov5n@640) | 10.09 − 2.304 = **7.786 → 7.79 ms** | 7.79 | ✅ |
| 全链路 60ms 余量 (yolov5n@640) | 60 − 52.66 = **7.34 ms** | 7.34 | ✅ |
★**8 项全对** ⇒ 上一轮的脚本**算术是对的**, 不是空壳。

**③ 「拿整机常量扣 demo 预算」这个洞, 现在有脚本+门禁堵着** ★[实测·本机脚本]
- 换屏 / 改分辨率 / 改通道数 ⇒ **只改 `demo_e2e_budget.py` 的输入** (命令行 `--lanes / --lane-rate-gbps / --width / --height` 也有) ⇒ demo 账**自己重算**, 不再从整机账减
- 上一轮 ISS-215 的扣法 vs 本单的扣法: ★**整机口径 10.09 − 7.776 = 2.32 ms** vs ★**demo 口径 10.09 − 2.304 = 7.79 ms** ⇒ ★**同一个数, 判严了 3.36 倍** (7.79/2.32 = 3.358; TX 本身 7.776/2.304 = **3.375×**)
- ⇒ ★**ISS-215 交卷里写的「10.09 ms 是『输出侧总额上限』, 与分辨率无关, 根因是用整机 TX 下限 7.776 去扣 demo 预算 (倍率 3.36×)」这条结论, 本单把它从「一次性人工修正」升级成「脚本 + 机器门禁」**

**④ 交付物 ③ 的门禁: 34/34 → 51/51, `--selftest` 10/10 → 18/18, ISS-215 那 5 条反向用例一条没被改红** ★[实测·本机脚本]
新增 **17 条 ISS-221 断言** (2 个全局 + 7×2 文档级 + 1 跨文档):
| 断言 | 作用 |
|---|---|
| demo 真源脚本可执行且算得出账 | 脚本没了/炸了 ⇒ 门禁直接红, **不许静默跳过** |
| demo 真源脚本源码零整机 DSI 常量 | 复用脚本自己的 `source_leak_anomalies()` |
| 有成对的「demo 预算真源锚点」分区标记 | 锚点区块不许被删 |
| ★**锚点区块逐项 == demo 真源脚本输出** | ★**核心里的一条**: 11 项逐项比, 容差 0.005 ms ⇒ **手抄错 0.01 ms 就红** |
| 锚点区块项齐全 (11 项) | 少写一行蒙混过关也不行 |
| ★**demo 活动口径零「整机 4-lane DSI」指纹** | 扫 `4-lane / 4 lane / 4 通道 / 6400 Mbps` (整机占位区 + 行级豁免标记除外) |
| ★**判据工具是 demo 真源脚本** | demo 活动口径里不许拿 `HW/e2e_budget_rk3572.py` 当判据工具 (整机脚本自己的 `--selftest` 行除外) |
| 引用了 demo 真源脚本 | 两份文档都必须真引用它 |
| ★**「表 A — demo 活动口径」逐行 == 真源输出** | ★**锚点对了、表里手抄错了也红** (3 行 × 4 列) |
| 两份文档的锚点区块逐项一致 | 不许一份改了另一份没改 |

**⑤ 交付物 ⑤: `SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记已同步 (ISS-215 交接单 B5-① 请求授权的那一行)** ★[实测·本机文件]
★**只改那一行注记**: `S9 = 3.0` 这个数值**一个字没动**; 周边 `S3 = 8.0 / S4 = 1.0 / S6 = 2.0 / S7 = 3.0 / S8 = 1.0 / S10 = 5.0` 与模式 A/B 公式行 (24.67 / 33.67 / 16.67) **逐字节未动** (diff 只出 1 行, 文件总行数 666 → 666)。
★**改后与 `SW/tools/rknn_bench.py` L258 (ISS-215 改过的那份同名注记) 口径一致**: 两侧现在都写「demo 活动口径 TX 物理下限 = 2.304 ms @480×640 (2-lane; 口径 A) / 2.048 ms (口径 B) + 整机路线·暂缓 @1080p = 7.776ms + S9 = 3.0 数值不许动」。

---

## B2 验收标准自评

| 验收标准 (任务书原文) | 自评 | 依据 |
|---|---|---|
| ① `SW/tools/demo_e2e_budget.py` 新建, 输入 demo 屏参数 (宽/高/通道数/lane 速率/每帧 payload+post 固定开销), 输出 TX 下限 / compose 上限 / 显示输出侧上限 / 全链路 60ms 余量 | ✅ 通过 | §B1-①②; rc=0 + `--selftest` 31/31; 命令行支持 `--lanes / --lane-rate-gbps / --width / --height / --overhead-bits / --t-compose-ms / --t-display-ms` |
| ① 口径写清: 哪些是整机同源常量, 哪些是 demo 专属 | ✅ 通过 | 脚本 §1 表头「(A) 整机同源常量 / (B) demo 专属常量」+ 每个常量行尾标注出处; 门禁断言「源码零整机 DSI 常量」 |
| ① 带 `--selftest` 反向用例 (改坏必红) | ✅ 通过 | 31/31: 好样本零异常 + **9 种改坏** + **1 种源码污染** 全抓到 |
| ① 不许把整机 4-lane 常量写死进本脚本冒充 demo 真源 | ✅ 通过 | 源码泄漏扫描 0 项 + 反向用例「源码污染能抓住」 |
| ② 两份规格文件里的 demo 数字换成脚本输出, 不许硬抄, 必须能追到脚本 | ✅ 通过 | 两份文件都有「demo 预算真源锚点 (ISS-221)」区块 (11 项) + 每项标源 `SW/tools/demo_e2e_budget.py`; ★**门禁逐项比对 11/11 + 「表 A」3 行全对上** |
| ② 整机路线占位区的数一个不许删 (ISS-212 L-08/L-16: 行级豁免标记 + 块级分区标记两套机制不变) | ✅ 通过 | `DEMO_OD_TIMING_SPEC.md` 整机占位区 **BEGIN=3 END=3** (本单前也是 3/3) · `DEMO_BOARD_60MS_VERDICT_PLAN.md` **BEGIN=1 END=1** ⇒ **块级分区标记未动**; 行级豁免标记机制仍在 (ISS-215 那 10 条断言全过) |
| ③ 机器门禁扩项: demo 判据链引用的数 == demo 预算脚本输出, 且不许出现「整机 4-lane DSI 带宽常量」这类引用 | ✅ 通过 | §B1-④ (17 条新断言); **真实文件改坏必红实测**: 把锚点里 `2.304` 改成 `2.400` ⇒ rc=1 且报「文档 2.4 ≠ 真源 2.304」+「两份文档锚点区块逐项一致」双红 ⇒ 还原后 md5 `-c` OK 且 rc=0 |
| ③ 反向用例 (改坏必红) | ✅ 通过 | 新增 7 条 (反例 9~15) + ISS-215 那 5 条 + ISS-145 那 4 条, **共 18/18** |
| ④ 交接单 `HANDOFF/2026-11-16_sw-lead_ISS221_demo预算真源.md` (B1~B6 六块齐全) | ✅ 通过 | 本文件 |
| ④ 分片 `state/fragments/sw.yaml` 必须走 `python3 state/frag_write.py` 原子写 | ✅ 通过 | §B6-⑧ 两条验盘命令输出原样 |
| ⑤ 收口 ISS-215 遗留分叉: `SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记, 只许改那一行注记, S9 = 3.0 与周边数字一个不许动, 改完 md5 前后对照 | ✅ 通过 | §B6-⑦: `diff` 只出 **1 行** (273c273), 总行数 666→666, 周边 S1~S10 与公式数字逐字节一致; md5 `ed080fa0…` → `46ac25e1…` |
| 不许改 `HW/` 下任何文件 | ✅ 通过 | `HW/e2e_budget_rk3572.py` md5 `7b820c14acfaee08a218cbf85557ef0b` **未变** (mtime 仍 2026-11-11 05:37) ⇒ 只读引用 |
| 不许改 `SW/DEMO_OD_PIPELINE_SPEC.md` | ✅ 通过 | md5 `fc42880ff4317cc989f440cf55d56872` (mtime 仍 2026-11-15 23:58) ⇒ **未动** |
| 不许改 `SW/RKNN_BENCH.md` 里除 §4.1 L273 以外的任何内容 | ✅ 通过 | `diff` 只出 1 行 |
| 不许改 `SW/tools/rknn_bench.py` | ✅ 通过 | md5 `b788b5cfe22fe6517c681ef0574dd980` (mtime 仍 2026-11-16 01:54) ⇒ **未动** |
| 不许改 `MECH/` 下任何文件 / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 | ✅ 通过 | 本单只写了 `state/fragments/sw.yaml` (自己那一份) + 本交接单 + 上面 4 个件; `MECH/` 与 `state/issue_log.yaml` 本单**零写入** (mtime 未变) |
| 板端 [实测] = 0 条, 全部预算数标 [推算] | ✅ 通过 | 本单**零板端数据**; 屏侧全部 [推算]; 标 [实测] 的只有「本机脚本 / 本机文件实读」 |
| 不许编造板端时延数字 / 不许把整机 1080p 的数当 demo 的数写进任何文件 | ✅ 通过 | demo 活动口径里的数全部由脚本算; 整机数 (7.776 / 2.32 / 4.32 / 12.96 / 1080p) **全部留在「整机路线占位区」**且带行级豁免标记, 门禁逐项核过 |
| 零外发 | ✅ 通过 | 本单**零外发** (不发邮件 / 不询价 / 不采购 / 不联系供应商); 缺口用本机文件 + 本机脚本自证 |
| 不许自签 issue_log (status 留给 main 落 verified) | ✅ 通过 | 本单**未写** `state/issue_log.yaml` ⇒ ISS-221 的 status 留给 main |
| `python3 SW/tools/demo_e2e_budget.py` rc=0 | ✅ 通过 | §B6-① |
| `python3 SW/tools/demo_e2e_budget.py --selftest` rc=0 | ✅ 通过 | §B6-② (31/31) |
| `python3 SW/tools/demo_timing_check.py` rc=0 | ✅ 通过 | §B6-③ (51/51) |
| `python3 SW/tools/demo_timing_check.py --selftest` rc=0 (ISS-215 那 5 条不许被改红) | ✅ 通过 | §B6-④ (18/18, ISS-215 反例 5~8 全绿) |
| `python3 SW/tools/check_demo_panel_spec.py` rc=0 | ❌ **不通过 (★开工前就红, 非本单所致★)** | ★见 §B5-①: 唯一红项是 R6「受保护文件 md5 变了」× 2 (`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv`) ⇒ **根因 = hw-lead 2026-11-16 02:32 的 ISS-220 落表第 1 批重新落表** ⇒ ISS-212 时期钉的 md5 基线过期 ⇒ ★**本单没碰过 HW/ 任何文件, 也没碰过该门禁读的任何一个文件** (§B5-① 有 mtime + md5 + 对照实验三重证据) ⇒ ★**只报不改 (该门禁不在本单允许清单内, HW/ 更是禁改区)** |
| `python3 SW/tools/check_demo_panel_spec.py --selftest` rc=0 | ✅ 通过 | §B6-⑤ (8/8) ⇒ **该门禁的检查器自身是好的**, 红的只是被钉死的 md5 基线 |
| `python3 state/merge.py && python3 state/gate_check.py` rc=0 且【Q1 交付齐备率】18/18 | ✅ 通过 | §B6-⑥ |
| 分片真在盘 (`stat` mtime 本轮之后 + `grep -c 'iss221' > 0`) | ✅ 通过 | §B6-⑧ 两条命令原样贴出 |

---

## B3 证据分级

| 结论 | 等级 | 依据 |
|---|---|---|
| demo TX 物理下限 = 2.304 ms (口径 A) / 2.048 ms (口径 B) | **[推算]** | 一帧 payload 7372800 bit ÷ 链路有效带宽 (3200 / 3600 Mbps); ★**板端 DSI 实测 = [0数据]** ⇒ 口径 A 的 80% 效率是**行业通用假设**, 不是本项目实测 |
| 缩放除数 6.75 / t_compose ~0.44 ms / 显示输出侧 ~2.75 ms | **[推算]** | 沿用 ISS-212 已发布口径 (2.0736 Mpx → 0.3072 Mpx); ★**沿用理由与已知瑕疵写在脚本 §1.1, 不偷改** |
| 输出侧总额上限 10.09 / 合成段上限 7.79 / 全链路余量 7.34 ms | **[推算]** | 60 − T_FIXED_OTHER(31.00) − (S5 + POST 5.60); S5 是 RK3576 公开实测按 TOPS 比折算 (ISS-137/ISS-215 已发布) |
| 输出侧总额上限与显示分辨率**无关** | **[推算]** | 它只由 60ms 账本其余部分决定 (S5 + POST + 固定块), 与屏参数无关 ⇒ 换屏时**只有合成段上限会变** |
| 整机 1080p 口径 7.776 / 2.32 / 4.32 / 12.96 | **[推算]** | `HW/e2e_budget_rk3572.py` (只读引用, 未改) |
| demo 屏 lane 数 = 2 / 分辨率 480×640 / 2.0 Gbps×80% / 1.8 Gbps | **[官方]** | ISS-212 已发布的 Waveshare 2.8" (SKU 22028) 口径 (官方 wiki + 官方驱动 `panel-waveshare-dsi.c` + 官方 dtbo) |
| 板端一切时延 (t_compose / t_display / t_npu / S10 …) | **[0数据]** | ★**板与屏都不在本机** ⇒ 本单零板端数据 |
| 脚本行为 / 门禁行为 / 文件 md5 / 行号 / diff | **[实测]** | 本机实跑 (§B6 全部命令输出原样) |

★**结论稳健性 (脚本自检 G7 守着)**: t_compose 估算取 ×0.5 / ×1 / ×2 三档, 全链路余量分别 7.57 / 7.35 / 6.91 ms ⇒ **全 > 0** ⇒ ★**口径瑕疵 (沿用 ISS-212 的 S9 缩放基准) 不改变 60ms 生死判定**。

★**已知口径瑕疵 (诚实记录, 本单不擅改)**: 整机账本里 `T_DISPLAY_OUT = 3.00` 是【整机 800×600 基线】的值且 = 合成 + 桥接余量 + TX 下限; 要严格拆开 demo 侧合成, 得用**整机 4 通道 DSI 常量** ⇒ ★**本脚本按纪律【不许引入整机 DSI 常量】⇒ 只能沿用 ISS-212 已发布口径** ⇒ 写在脚本 §1.1 + §4, 并用上面的三档敏感性证明**判定不翻**。

---

## B4 接口取值声明 (interface_claims)

| key | value (短规范值) | note | 登记位置 |
|---|---|---|---|
| `demo_budget_source_script` | `SW/tools/demo_e2e_budget.py` | demo 屏 (2 通道 @480×640) 的 60ms 预算**真源脚本**; 换屏只改它的输入 | 本单分片 `interface_claims` |
| `demo_tx_floor_ms` | `2.304/2.048` | demo TX 物理下限 (口径 A/口径 B); ★**只对 2-lane @480×640 有效**, 换屏须重算 | 本单分片 `interface_claims` |
| `demo_display_out_cap_ms` | `10.09` | 输出侧总额上限 (yolov5n@640), **与显示分辨率无关** | 本单分片 `interface_claims` (沿用 ISS-215 同值 ⇒ 不产生冲突) |
| `demo_compose_cap_ms` | `7.79` | demo 合成段上限 (yolov5n@640) = 10.09 − 2.304 | 本单分片 `interface_claims` (沿用 ISS-215 同值 ⇒ 不产生冲突) |
| `demo_e2e_margin_ms` | `7.34` | ★**ISS-221 新增**: 全链路 60ms 预算余量 (yolov5n@640) | 本单分片 `interface_claims` |

★**与别人的接口值不冲突**: `demo_display_out_cap_ms` / `demo_compose_cap_ms` 两个值与 ISS-215 已发布值**逐位相同** ⇒ 合并器不会报冲突。
★**需要 main 知道的**: `demo_e2e_margin_ms` 是**新 key**, 之前没有 ⇒ 谁在用 demo 60ms 判据的, 可以直接引用。

---

## B5 未决项与卡点

**① ★`check_demo_panel_spec.py` 的 R6 红项: 开工前就红, 根因在 hw-lead 的落表, 本单只报不改** ★[实测·本机文件]
- 现象: `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=1, 2 项不通过**:
  - `R6 受保护文件 md5 变了: HW/netlist_v1.csv (13f59a43dbd35dc6cb16e897c8c891ab ≠ c78f991283cc82d56c8e3dd31657c785)`
  - `R6 受保护文件 md5 变了: HW/netlist_v1_pins.csv (a600afae493f5a7a6c55f46ad35ac89c ≠ 4814617e22b567d76164e56bc5e39dc8)`
- ★**三重证据「不是本单造成的」**:
  1. ★**时间线**: 两个网表 mtime = **2026-11-16 02:32:07** (hw-lead 的 ISS-220「落表第 1 批」, 交接单 mtime 02:39) ⇒ ★**早于本单开工 (03:51) 1 小时 19 分**; 本单第一次写盘是 03:54
  2. ★**该门禁读的 6 个文件, 本单一个都没动** (`SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` 11-15 23:58 / `SW/DEMO_PANEL_SPEC_TRIAGE.md` 11-16 00:02 / `SW/DEMO_OD_PIPELINE_SPEC.md` 11-15 23:58 / `HW/netlist_v1.csv` 11-16 **02:32** / `HW/netlist_v1_pins.csv` 11-16 **02:32** / `HW/PCB/demo_mainboard.kicad_pcb`)
  3. ★**同类红项在 `timing_check.py` 上也是同一根因** (65/68, 3 项 FAIL: 「网表锚点 md5 c78f9912…」「I2C 注记误差」「F3 网表自带的 t_r 注记 2380ns」) ⇒ ★**本单把 `SW/RKNN_BENCH.md` 换回改前版本再跑, 结果一模一样 (65/68)** ⇒ 零关联
- ★**处置**: 本单**不动** `HW/` (硬边界) 也**不动** `SW/tools/check_demo_panel_spec.py` (不在本单允许清单) ⇒ ★**只报** ⇒ 见 §「待办」。

**② ★`demo_e2e_budget.py` 的口径沿用瑕疵 (ISS-212 遗留, 不擅改)** ★[推算]
严格拆 demo 侧合成段需要整机 4 通道 DSI 常量, 与本单的「不许引入整机 DSI 常量」硬纪律冲突 ⇒ 沿用 ISS-212 已发布口径 ⇒ 已用三档敏感性证明**判定不翻** ⇒ **不阻塞本单**, 但换屏 / 换分辨率时建议 main 拍一次板是否重定口径。

**③ ★板端 [实测] = 0 条 (本单结构性缺口, 不是本单能补的)** ★[0数据]
板与屏都不在本机 ⇒ 屏侧一切是 [推算] ⇒ ★**生死判定必须等板端两个点: 第 7 段 `t_compose` + 第 8 段 `t_display`** ⇒ 命令已备好 (§B6-① 的第 4 条用法)。

**④ ★ISS-221 不自签**: `state/issue_log.yaml` 本单**零写入** ⇒ ISS-221 的 `status` 请 main 落 `verified`。

---

## B6 自证复现命令 (输出原样)

### ① `python3 SW/tools/demo_e2e_budget.py` ⇒ rc=0
### ② `python3 SW/tools/demo_e2e_budget.py --selftest` ⇒ rc=0 (31/31, 9 种改坏 + 1 种源码污染全抓到)
### ③ `python3 SW/tools/demo_timing_check.py` ⇒ rc=0 (51/51, 含本单新增 17 条 ISS-221 断言)
### ④ `python3 SW/tools/demo_timing_check.py --selftest` ⇒ rc=0 (18/18, ISS-215 那 5 条一条没被改红)
### ⑤ `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=1 (★开工前就红, 根因 = hw-lead 02:32 重新落表 ⇒ 见 B5-①★)**
### ⑤' `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ rc=0 (8/8)
### ⑥ `python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0, 【Q1 交付齐备率】18/18
### ⑦ `SW/RKNN_BENCH.md` §4.1 L273 md5 前后对照 + diff 只出 1 行
### ⑧ ★分片真在盘 (mtime 本轮之后 + `grep -c 'iss221'` > 0)

★**板端代入命令 (板子接上后直接用)**:
```bash
python3 SW/tools/demo_e2e_budget.py --t-compose-ms <第7段实测值> --t-display-ms <第8段实测值>
python3 SW/tools/demo_e2e_budget.py --lanes 4 --lane-rate-gbps 2.0    # 换屏试算
```

---

## 本单改了什么 (清单)

| 文件 | 动作 | md5 变化 |
|---|---|---|
| `SW/tools/demo_e2e_budget.py` | ★**上一轮已建, 本单未改** | `ee64b86a945fd857044484c1d16d3a63` (未动) |
| `SW/tools/demo_timing_check.py` | ★**加 ISS-221 门禁** (17 条断言 + 7 条反向用例 + `check_demo_budget_source()` + `_good221_doc()`) | 上一轮 `d1f9…` (02:26 版) → `a6e891f1f22a7831fe99fa2650639d7a` |
| `SW/DEMO_OD_TIMING_SPEC.md` | ★**上一轮已换数, 本单未改** (只做过一次「改坏必红」实验并**按 md5 `-c` 还原**) | `576d239138565b1112a827f9f983f839` (未动) |
| `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` | ★**上一轮已换数, 本单未改** | `226da72bfd3cdba2fe63cfa3d82fa3e3` (未动) |
| `SW/RKNN_BENCH.md` | ★**只改 §4.1 L273 那一行注记** (S9 = 3.0 与周边数字一个没动) | `ed080fa0188d91a2cacf27c8073a3155` → `46ac25e1eb96ee296e60cb37485524f9` |
| `HANDOFF/2026-11-16_sw-lead_ISS221_demo预算真源.md` | ★**本单新建** | — |
| `state/fragments/sw.yaml` | ★**本单用 `state/frag_write.py` 原子写** | — |
| `HW/e2e_budget_rk3572.py` | ★**只读引用, 一个字节没动** | `7b820c14acfaee08a218cbf85557ef0b` (未动) |
| `SW/DEMO_OD_PIPELINE_SPEC.md` · `SW/tools/rknn_bench.py` · `MECH/` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` · `state/outbox/` | ★**零改动** | — |

---

## ★边界审计 (本单自证: 哪些文件我写了 / 哪些我一个字节没动)

★**本单真正写过的文件 (精确 mtime, 全部落在我这一轮 03:52~04:00 的窗口里)**:
| 文件 | mtime | 说明 |
|---|---|---|
| `SW/tools/demo_timing_check.py` | 03:54:44 | ★**加 ISS-221 门禁** |
| `SW/DEMO_OD_TIMING_SPEC.md` | 03:54:49 | ★**只是「改坏必红」实验时临时改坏又还原** ⇒ md5 `576d239138565b1112a827f9f983f839` **与本单开工时逐字节相同** (md5sum -c 已验) |
| `SW/RKNN_BENCH.md` | 03:55:40 | ★**只改 §4.1 L273 那一行注记** |
| `HANDOFF/2026-11-16_sw-lead_ISS221_demo预算真源.md` | 03:56:33 | ★**本单新建** |
| `state/fragments/sw.yaml` | 03:57:38 | ★**本单用 `state/frag_write.py` 原子写** |
| `SW/tools/demo_e2e_budget.py` | **02:22:59** | ★**上一轮留的, 本单一字未改** |
| `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` | **02:23:32** | ★**上一轮留的, 本单一字未改** |

★**硬边界逐项 md5 核对 (禁改区全部逐字节未动)**:
| 文件 | md5 | 判定 |
|---|---|---|
| `HW/e2e_budget_rk3572.py` | `7b820c14acfaee08a218cbf85557ef0b` | ★**与 ISS-215 交接单里已发布的基线逐字节相同** (mtime 仍 2026-11-11 05:37) ⇒ **HW/ 本单零改动** ✓ |
| `SW/DEMO_OD_PIPELINE_SPEC.md` | `fc42880ff4317cc989f440cf55d56872` | 未动 (mtime 仍 2026-11-15 23:58) ✓ |
| `SW/tools/rknn_bench.py` | `b788b5cfe22fe6517c681ef0574dd980` | 未动 (mtime 仍 2026-11-16 01:54) ✓ |
| `PROJECT_TRACKER.md` | — | 未动 (mtime 仍 2026-11-11 08:38) ✓ |
| `MECH/` · `state/outbox/` · 别人的分片 | — | 未动 ✓ |

★**请 main 注意一个「假阳性」风险**: 本单执行期间 (03:51~04:00) ★**hw-lead / mech-lead / main 三个会话正在并行写盘** ⇒ 全仓 `find -newermt '03:51'` 会捞出 `HW/PCB/*` (4 个) · `MECH/*` (2 个) · `state/fragments/mech.yaml` · `state/fragments/pm.yaml` · `state/issue_log.yaml` · `DECISION_PENDING_2026-11-16.md` 等 ⇒ ★**这些不是本单写的** (本单是 subagent, 写盘工具调用只有上表 7 个路径) ⇒ ★**验本单边界时请按上表的 md5 核, 不要按 mtime 扫全仓**。

---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)

★**本单不需要**跟 hw-lead / mech-lead 对齐接口 ⇒ ① 本单**不碰 HW/** ⇒ ② 屏参数 (2-lane @480×640) 是 ISS-212 已发布口径 ⇒ ③ S9 注记同步是 ISS-215 交接单 **B5-① 已请求授权**、本单任务书也明确授权 ⇒ 无接口请求。

---

## 待办: 需要项目总工做什么

1. ★**ISS-221 status 落 `verified`** (本单不自签; `state/issue_log.yaml` 本单零写入)。
2. ★**请裁定 `check_demo_panel_spec.py` 的 R6 md5 基线过期问题** (B5-①): `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 在 hw-lead ISS-220 落表第 1 批 (2026-11-16 02:32) 换了内容 ⇒ ISS-212 时期钉的 md5 基线 (`c78f9912…` / `4814617e…`) 过期 ⇒ ★**该门禁现在恒红, 会掩盖以后真正的红灯** ⇒ 请让 hw-lead 或 main 确认「这两个网表的新 md5 是新基线」后刷新 `SW/tools/check_demo_panel_spec.py` 的 `PROTECTED_MD5` (★**该文件不在 sw-lead 的允许清单内, 本单不越权改**)。⇒ 同一根因也影响 `SW/tools/timing_check.py` 的 3 项 FAIL。
3. ★**请确认 demo 60ms 判据链已换真源**: `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` 的判据工具已是 `SW/tools/demo_e2e_budget.py` (不再是整机脚本) ⇒ 板端接上后直接用 §B6 末尾那条命令代入。

---

## 阻塞: 缺什么信息

- ★**板端 [实测]**: 缺第 7 段 `t_compose` 与第 8 段 `t_display` 两个实测值 ⇒ 没有它们, demo 屏侧全部只能停在 [推算] ⇒ ★**生死判定 (60ms 成立与否) 板子接上才有答案**。
- ★**demo 屏 DSI 实测效率**: 口径 A 的 80% 链路效率是**行业通用假设**, 本项目**没有板端实测** ⇒ 板端接上后建议用 `--lane-rate-gbps / --lanes` 试算, 或直接代入实测。
- 其余: 无 (本单能做的都做完了)。
