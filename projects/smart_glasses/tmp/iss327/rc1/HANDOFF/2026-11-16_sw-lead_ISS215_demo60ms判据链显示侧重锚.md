# [sw-lead→PM] ISS-215 · demo 60ms 判据链「显示侧」重锚 (480×640) + 逐处定性表 + 机器门禁
- 发起方: sw-lead · 日期: 2026-11-16 · 单号 ISS-215 (内部活 · 不改网表/脚表/板/HW) · **零外发** (不发邮件/询价/问询/采购) · 板端 [实测] = **0 条** (板不在本机)
- 依据: `SW/DEMO_60MS_DISPLAY_REANCHOR_TRIAGE.md` (逐处定性表 23 处) · `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` (ISS-212 demo 屏真源) · `HW/e2e_budget_rk3572.py` (整机 1080p 口径权威源头, **只读引用, 本单一个字未改**)

## B1 结论摘要

① **60ms 判据链的显示侧已从「整机 1920×1080」重锚到「demo 屏 480×640」** ⇒ TX 物理下限 **7.776 → 2.304 ms** (口径 A; 口径 B = **2.048 ms**) · `t_compose` [推算] **3.0 → ~0.44 ms** (缩放律 **×4.32 → ÷6.75**, 2.07 Mpx → 0.307 Mpx) · 显示输出侧合计 [推算] **10.09 → ~2.75 ms** · 合成段上限 (余量) **2.32 → 7.79 ms** ⇒ ★**判据被算严的倍率 = (10.09−2.304)/(10.09−7.776) = 7.786/2.314 = 3.36×** ⇒ **`DEMO_OD_TIMING_SPEC.md` §3.3.1 表 A 的 yolov5n@640 行判定由「❌ 最坏情况不过 ⇒ 必须实测」翻成「✅ [推算] 最坏情况也过 ⇒ 显示侧不再是 60ms 账本的瓶颈」** ★

② **逐处定性表已出** ⇒ `SW/DEMO_60MS_DISPLAY_REANCHOR_TRIAGE.md`: ★**23 处** (grep 命中 `7.776|10.09|2.32|4.32|1920|1080`) = `DEMO_OD_TIMING_SPEC.md` 13 行 + `DEMO_BOARD_60MS_VERDICT_PLAN.md` 4 行 + `rknn_bench.py` 1 行 + `demo_timing_check.py` 5 行 ⇒ **判定四档: demo 活动口径 15 处 / 整机路线占位 8 处 / 历史留档 0 处 / 说明文字 0 处** ⇒ 数量与派活单给的 grep 计数**逐位对齐** (7.776 4 / 1920 6 / 10.09 4 / 2.32 3 / 4.32 4 / 7.776 2 / 10.09 3 / 2.32 2 / 4.32 5)

③ **★★★ 一个必须先说清的口径澄清: `10.09 ms` 不是 1080p 口径的数, 它是「显示输出侧总额上限」= 60ms 预算上限, 与分辨率无关 ⇒ 原样保留, 不重算、不作废 ★★★** ⇒ 依据 `HW/e2e_budget_rk3572.py` (只读): `T_FIXED_OTHER = 31.00 # 与显示分辨率无关的部分` · `display_out_max_for(s5, budget) = budget − T_FIXED_OTHER − (s5 + POST_MS)` ⇒ s5=13.31 时 = **10.09 ms** ⇒ ★**真正随分辨率变的只有 `compose_max_for` = 总额上限 − TX 下限 = 10.09 − 7.776 = 2.32 (整机) ⇒ demo = 10.09 − 2.304 = 7.786 ≈ 7.79 ms** ★★ (**与 ISS-212 Q-5「余量从 2.32 放宽到 7.79」逐位吻合**) ★★ ⇒ ★**所以判据被算严的根因就是「用整机的 TX 下限 7.776 去扣 demo 的预算」这一处口径混用** ★

④ **整机那套数一处没删, 全部显式分栏标注** ⇒ 处置规矩照 ISS-212 `SW/DEMO_PANEL_SPEC_TRIAGE.md` L-08/L-16 立的规矩办: **① 行级豁免标记** (含整机 token 的行必须带 `整机路线·暂缓` 等标注) + **② 块级分区标记** (`<!-- BEGIN 整机路线占位区 … -->` … `<!-- END … -->`) ⇒ `DEMO_OD_TIMING_SPEC.md` 新增 **2 个**整机占位区块 (整机 TX 推导 + 整机判据表 B, 逐字保留) · `DEMO_BOARD_60MS_VERDICT_PLAN.md` 新增 **1 个** (判据第 3 条的整机口径原值) ⇒ ★**不删、也不留着冒充 demo 口径** ★

⑤ **机器门禁已留** ⇒ `SW/tools/demo_timing_check.py` 扩了 **[ISS-215] 5 类 × 2 文件 = 11 条断言** + **反向用例 5 条** ⇒ `rc=0` (34/34) · `--selftest` **10/10** (改坏必变红) ⇒ ★**ISS-212 的门禁 `SW/tools/check_demo_panel_spec.py` rc=0 + selftest 8/8 未被本单改红** ★

## B2 验收标准自评

| 验收标准 | 自评 | 依据 |
|---|---|---|
| ① 逐处定性表四档齐全、无「待定」、数量与 grep 对得上 | ✅ 通过 | `SW/DEMO_60MS_DISPLAY_REANCHOR_TRIAGE.md` §1~§4 (23/23 行对上; §4 给了复核命令 + 改写前后计数) |
| ② 改写四处, 每一处能指回 ISS-212 的某一个数 | ✅ 通过 | §1/§2/§3 的「指回 ISS-212 的哪个数」列: 2.304 / 2.048 / 0.44 / 2.75 / 7.79 / ÷6.75 全部落到具体行 |
| ③ `rknn_bench.py` 只许改注记, S9 = 3.0 不许动 | ✅ 通过 | `SW/tools/rknn_bench.py` L258: `S9 = 3.0` **数值逐字节未动**, 只扩注记 (见 B5-③ 的连带影响) |
| ④ `demo_timing_check.py` 的 ×4.32 锚点改成 demo 口径 + 有反向用例 | ✅ 通过 | 检查 ⑭ 改为 `t_compose ∧ ÷6.75 ∧ 0.44`; 反例 4「把 ÷6.75 塞回 ×4.32」必红 |
| ⑤ 新增断言: demo 活动栏不许出现 7.776/10.09/2.32/4.32, 整机占位必须带显式标注且不在 demo 活动栏 | ✅ 通过 | `check_display_reanchor()` ⑳/㉑/㉒/㉓/㉔/㉕ + 反例 5/6/7/8 必红 |
| ⑥ 60ms 硬指标不许动 | ✅ 通过 | 一处未动 |
| ⑦ ISP 判据 15.10 / 17.33 不许调松 | ✅ 通过 | `DEMO_OD_TIMING_SPEC.md` 里两值原样; `demo_timing_check.py` 断言 ⑳ 原样 |
| ⑧ S9 = 3.0 数值不许动 | ✅ 通过 | 见 ③ |
| ⑨ 板端一切 = [0数据], 不许编板端时延数字 | ✅ 通过 | 新增的 demo 行全部标 [推算]; 「实测值仍是 [0数据]」原文保留; `demo_timing_check.py` 断言「本单未编造板端时延数字」仍 ✅ |
| ⑩ 新出现的数必须标证据等级 | ✅ 通过 | 定性表 §0 表 + 交卷件 B3 全部标档 |
| ⑪ 不许改 `HW/` 下任何文件 (含 `e2e_budget_rk3572.py`) | ✅ 通过 | mtime 仍 2026-11-11 05:37:08; md5 **7b820c14acfaee08a218cbf85557ef0b** (只读引用) |
| ⑫ 受保护 md5 逐字节不变 | ✅ 通过 | `HW/netlist_v1.csv`=c78f9912… · `HW/PCB/demo_mainboard.kicad_pcb`=611b869e… · `HW/PCB/demo_mainboard.kicad_pro`=3e504d2b… 三条与派活单给定值**逐位一致** |
| ⑬ 不许改 ISS-212 已交付的三件 (只引用) | ✅ 通过 | `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` · `SW/DEMO_PANEL_SPEC_TRIAGE.md` · `SW/tools/check_demo_panel_spec.py` **一字未动**; 其门禁仍 rc=0 / selftest 8/8 |
| ⑭ 不许改 `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 | ✅ 通过 | 一处未动; 分片只经 `state/frag_write.py --agent sw-lead` 原子写 |
| ⑮ 不许碰 PCB 布线/布局 | ✅ 通过 | 一处未动 |
| ⑯ 交卷前三条命令 rc 必须 0 | ✅ 通过 | 见 B6 |
| ⑰ 分片走 `state/frag_write.py` 原子写 (artifact/claim/need, need 一律 to: main) | ✅ 通过 | 见 B6 最后一条 |
| ★**板端实测** | ⚠️ **未验 / [0数据]** | ★**板与屏都不在本机 ⇒ 本单 [实测] = 脚本级/grep 级, 0 条实物测量** ⇒ **60ms 生死、t_compose / t_display 实测值一律待板端执行, 不是已验证** ★ |

## B3 证据分级

- **[实测]** (脚本级 / grep 级, 本单亲自跑): `python3 SW/tools/demo_timing_check.py` → **rc=0 / 34/34** · `--selftest` → **10/10** (含 ISS-215 反向用例 5 条全红) · `python3 SW/tools/check_demo_panel_spec.py` → **rc=0** · `--selftest` → **8/8** · `python3 state/merge.py` → **rc=0** · `python3 state/gate_check.py` → **rc=0 / Q1 18/18** · `md5sum` 三条受保护文件 → 与派活单给定值**逐位一致** · grep 命中计数 13/4/1/5 = **23** 处 · `HW/e2e_budget_rk3572.py` mtime = **2026-11-11 05:37:08** (未动)
- **[官网]** (本单**只引用** ISS-212 已发布的官方口径, 未重新外发、未重新查网): Waveshare 2.8" DSI LCD SKU 22028 **480×640 / 2-lane / 无 DCS init / I2C_B ≤100kHz** · 屏 MCU 0x45 · 触摸 GT911 0x14 ⇒ 出处 `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` §2/§3 (ISS-212 亲自拉取 RPi 官方 `panel-waveshare-dsi.c` commit `d8e5eb49991de6b8fa9231532a11036e24aa84de` 复核过)
- **[推算]** (全部写清推算过程): **2.304 ms** (口径 A: 2 lane × 2.0 Gbps × 80% = 3200 Mbps 有效 ⇒ 7.3728 Mbit/帧 ÷ 3200 Mbps) · **2.048 ms** (口径 B: 1.8 Gbps/lane × 2 lane × 100%) · **~0.44 ms** (按像素数线性缩放 ÷6.75: 2.0736 Mpx → 0.3072 Mpx) · **~2.75 ms** (0.44 + 2.304) · **7.79 ms** (10.09 − 2.304 = 7.786) · **3.36×** (7.786 / 2.314) · **−5.00 / 14.35 ms** (另两行合成段上限 = 原值 − 2.304) · **12.96 ms** (整机线性上界 = `T_DISPLAY_OUT` 3.00 × 4.32, 归整机路线占位) ⇒ ★**本单不为 demo 屏另编「线性上界」** (ISS-212 未发布该数 ⇒ 越权编数) ⇒ demo 栏改用 ISS-212 已发布的 ~2.75 ms 与 7.79 ms 余量做判据
- **[0数据]**: **板端一切** (t_compose / t_display / ISP / NPU 的实测值) · 60ms 生死的板端判定 · demo 屏逐帧延迟 S10 · 整机视涯侧一切 (整机路线·暂缓)
- **[媒体]**: **0 条**

## B4 接口取值声明 (interface_claims)

key `demo60_display_resolution`=`480x640` · `demo60_tx_floor_ms`=`2.304` · `demo60_tx_floor_ms_alt`=`2.048` · `demo60_t_compose_ms`=`0.44` · `demo60_display_out_ms`=`2.75` · `demo60_compose_headroom_ms`=`7.79` · `demo60_output_upper_bound_ms`=`10.09` · `demo60_scale_ratio`=`÷6.75` ⇒ ★**全部是新键, 与 ISS-212 的 `demo_panel_*` 键并存不冲突; 老共享键 `display_resolution` / `panel_init_sequence_source` / `demo_panel_tx_floor_ms` 一个字没改** ⇒ **不制造跨分片冲突** (merge 冲突仍 0) ★

## B5 未决项与卡点

① ★**`SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记仍是整机 1080p 原文** ⇒ 它**不在本单允许改的 4 个文件清单里** ⇒ 本单**未改** (只改了 `SW/tools/rknn_bench.py` 的同名注记) ⇒ ★**S9 数值 3.0 两边都没动 ⇒ 已发布的 21/21 + 9/9 锚点不受影响** ⇒ **口径注记两边措辞出现分叉, 请项目总工裁: 是否授权下一轮同步 RKNN_BENCH.md L273 的注记 (只改措辞, 不动数字)** ★
② ★**整机路线那套数 (7.776 / 12.96 / 2.32 / ×4.32) 现在只以「整机路线占位区」形式存在于这两份 md 里** ⇒ ★**`HW/e2e_budget_rk3572.py` 是它的权威源头 (整机 4-lane 口径) ⇒ demo 屏的 2-lane 账本目前没有对应的整机等价脚本** ⇒ **建议另立一个 demo 口径的预算脚本 (本单未做: 超出本单范围)** — 需项目总工决定是否立项 ★
③ ★**`HW/e2e_budget_rk3572.py --t-compose-ms` 的 DSI 带宽常量是 4-lane@2.0Gbps×80%, 对 2-lane demo 屏不适用** ⇒ `DEMO_OD_TIMING_SPEC.md` §3.3.1 已加注「板端实测值为准, 不许拿脚本常量当 demo 屏的真值」⇒ **但板端脚本本身还没出** — 需项目总工决定由谁补
④ ★**板未到 ⇒ 60ms 与显示侧全部未实测** ⇒ 本单的 2.304 / 0.44 / 2.75 / 7.79 **全是 [推算], 一条 [实测] 都没有** ⇒ **生死仍以板端实测为准**
⑤ ★**ISS-212 遗留、且本单无法闭合的**: 整机视涯侧 init 序列 / 时序 / DSC / 单色全彩 / 逐帧延迟仍 [0数据] (整机路线·暂缓, 不外发) ⇒ **不阻塞本单**
⑥ ★**demo 屏 (Waveshare 2.8") 无 TE 脚** ⇒ 撕裂只能靠"整帧提交"或帧率错开 ⇒ 本单未改这块 (ISS-212 已记)

## B6 自证复现命令 (输出原样)

```bash
$ python3 SW/tools/demo_timing_check.py
⇒ ISS-145 demo 端到端时序规格自检: 34/34  ⇒ rc=0   (含 [ISS-215] 11 条新断言全 ✅)
$ python3 SW/tools/demo_timing_check.py --selftest
⇒ 自检 (demo_timing_check): 10/10  ⇒ rc=0   (ISS-215 反向用例 5 条全红: 反例4/5/6/7/8)
$ python3 SW/tools/check_demo_panel_spec.py
⇒ ✅ ISS-212 demo 显示侧口径门禁: 全过 (R1~R6)  ⇒ rc=0
$ python3 SW/tools/check_demo_panel_spec.py --selftest
⇒ -- SELFTEST 8/8 通过 --  ⇒ rc=0
$ python3 state/merge.py
⇒ ✅ STATE.yaml 已刷新  ⇒ rc=0   (产出 244 | 阻塞 43 | 未闭合需求 150 | 冲突 0)
$ python3 state/gate_check.py
⇒ 【Q1 交付齐备率】 18/18 个必填验收块齐全  ⇒ rc=0
$ md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/e2e_budget_rk3572.py
⇒ c78f991283cc82d56c8e3dd31657c785  HW/netlist_v1.csv
⇒ 611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
⇒ 3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
⇒ 7b820c14acfaee08a218cbf85557ef0b  HW/e2e_budget_rk3572.py   ★整机 1080p 口径权威源头, 本单只读引用, mtime 仍 2026-11-11 05:37:08 ⇒ 一个字未动
$ for f in SW/DEMO_OD_TIMING_SPEC.md SW/DEMO_BOARD_60MS_VERDICT_PLAN.md SW/tools/rknn_bench.py SW/tools/demo_timing_check.py; do grep -n -E '7\.776|10\.09|2\.32|4\.32|1920|1080' "$f" | cut -d: -f1 | sort -n -u | wc -l; done
⇒ 13 / 4 / 1 / 5  = 23   (交卷前命中行数; 改写后必然变多 —— 门禁脚本本身必须写出被禁 token 才能判红, 详见定性表 §4.1)
$ python3 state/frag_write.py --agent sw-lead --add-artifact path=... --add-claim key=... --add-need key=... to=main
⇒ ✅ 已原子更新 (tmp + fsync + os.replace)  ⇒ 分片只经 frag_write.py 写, 未用 open(p,"w")
```

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)
- 对方: **无** (本单 0 次外发 · 0 次跨总工直接沟通 · 不联系任何供应商)
- ★**本单内部活**: 只改 SW/ 下 4 个文件 + 新增 1 个定性表 + 1 个交卷件 ⇒ **不涉及跨模块接口取值变更** ⇒ 无接口请求

## 待办: 需要项目总工做什么
1. ★**裁 B5-①**: 是否授权下一轮同步 `SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记 (只改措辞, **数字 3.0 不动**, 21/21 + 9/9 锚点不受影响)
2. ★**裁 B5-②**: 是否立项一个 **demo 口径 (2-lane @480×640)** 的预算脚本 (对应整机 `HW/e2e_budget_rk3572.py` 的 demo 等价件)
3. ★**裁 B5-③**: demo 口径的 `--t-compose-ms` 板端脚本由谁补 (整机那个 4-lane 常量对 demo 屏不适用)
4. ★**知会 B1-①**: **60ms 判据链第 3 条 (显示输出侧) 的判定方向变了** (整机口径 ❌ → demo 口径 ✅ [推算]) ⇒ **建议项目总工在 `PROJECT_TRACKER.md` §0 之外的判据视图里同步一版** (本单**未改** `PROJECT_TRACKER.md`, 那是项目总工的权限)

## 阻塞: 缺什么信息 (明确写"需要老板/原厂回答 X")
- ★**板未到** ⇒ 60ms / t_compose / t_display 的实测值一律 **[0数据]** ⇒ **本单所有数字都是 [推算]**
- ★**无板端外部阻塞** ⇒ 本单不依赖任何外部回信 ⇒ **不需要外发任何问询函**
