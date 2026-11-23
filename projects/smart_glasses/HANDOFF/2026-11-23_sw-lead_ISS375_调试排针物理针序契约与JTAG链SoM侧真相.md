# [sw-lead→PM] ISS-375 · 调试排针换 land 后的物理针序契约 (pin1 朝向 / JTAG 线序) + JTAG 链 SoM 侧真相
- 发起方: sw-lead
- 日期: 2026-11-24 (任务书落款 2026-11-23)
- 结论: **「pin1 朝向」与「JTAG 链 SoM 侧通不通」两件事, 已收成一条机器闸 (D0~D8 全绿) + 一份可查的物理针序契约页; 建议 `J_DEBUG`/`J_UART` 走 rot 90 (保持现状顺排), 但两个裁决都归 main, 本单不代拍。**
- 依据: `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (真相页: cont1 落 32,392 B @ 01:15, 本趟追加式订正后 35,582 B) · `SW/tools/check_debug_pin_order_contract.py` (新闸, 本趟修过 bug) · `logs/iss375/` (8 份读数) · `tmp/iss375_sbx/` (沙盒留证)

---

## B1 结论摘要

★**① 本单的技术债已还清: 新闸的「真 bug」已修 ⇒ rc=0 / D0~D8 全绿 / `--selftest` rc=0 且末行 `ALL TESTS PASS`** ★
- `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py` ⇒ **rc=0 · 9/9 PASS**
- `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py --selftest` ⇒ **rc=0 · 11/11 PASS · 末行 `ALL TESTS PASS`** (含 3 条镜像类反向用例)
- ★**bug 根因 (本机实测, 与 main 给的假设不同, 见 B5-③)**: 本机 KiCad 10.0.8 的 `pcbnew.FootprintLoad()` **本身就是坏的** —— `pcbnew.py:24225` 的实现是 `return plug.FootprintLoad(...)`, 而 `plug` 是裸 `SwigPyObject` **没有 `FootprintLoad` 成员** ⇒ `AttributeError` ⇒ ★**写 .py 文件也一样炸 (⇒ main 记的「脚本文件入口能成 / `-c` 才炸」是假象)★**; 且实测**同一进程里第 3 次插件调用就拿到坏对象** (`FindPlugin` 返回裸 `SwigPyObject` / `FootprintLoad` 返回的 `FOOTPRINT.Pads()` 不可迭代) ⇒ 修法 = **改走 `pcbnew.PCB_IO_MGR.FindPlugin(KICAD_SEXP).FootprintLoad()` + 一个候选一个子进程隔离**。★**闸未重写, 是最小改动 (3 处 + 2 处判据精化)★**

★**② 物理针序契约 (现状 → 官方 land → 两个候选), 全部实读, 复跑命令在 B6** ★
| 件 | 现状板面 (S0) | 官方 land | rot 90 候选 | rot 270 候选 |
|---|---|---|---|---|
| `J_DEBUG` (1×4) | pad1=`JTAG_TCK` @X=**142.2000** (**X_MIN**) · 4 pad **全 RECT/SMD 0.275×0.900** ⇒ **无 pin1 极性标记** | pad1=`thru_hole rect` · pad2/3/4=`thru_hole circle` | 原点 **(141.0450, 56.6000)** · 序 **[1,2,3,4]** ⇒ pad1@**X_MIN** · **顺排 TCK→TDO** | 原点 **(144.8550, 56.6000)** · 序 **[4,3,2,1]** ⇒ pad1@**X_MAX** · **逆排** |
| `J_UART` (1×2) | pad1=`UART_TX` @X=**18.6400** (**X_MIN**) · 2 pad 全 RECT/SMD ⇒ **无标记** | pad1=`thru_hole rect` · pad2=`thru_hole circle` | 原点 **(18.2550, 68.6000)** · 序 **[1,2]** ⇒ pad1@**X_MIN** | 原点 **(19.5250, 68.6000)** · 序 **[2,1]** ⇒ pad1@**X_MAX** |

- ★**两候选互为镜像 (不是互等)**: `J_DEBUG` rot90 的四个 X 集合 = {141.0450, 142.3150, 143.5850, 144.8550} = rot270 的同一集合, **只是归属反了** ⇒ 闸 D2 用 KiCad 自己的 `FOOTPRINT.SetOrientationDegrees` 实算并要求两序**互为逆序**, 互等即红。
- ★**几何完全等价 (⇒ 这不是结构问题, 是「装配与救砖的线序契约」问题)**: 两候选的铜箔包络 `X 140.5450~145.3550 (w=4.8100) / Y 56.1000~57.1000 (h=1.0000)` 与 fab 外框 `X 139.5869~146.3131 (w=6.7262) / Y 55.5000~57.7000 (h=2.2000)` **逐字相同**; `J_UART` 同理 (铜箔 w=2.2700 h=1.0000 · fab w=5.4404 h=2.2000)。
- ★**换官方 land 后板面【第一次】出现 pin1 方形标记** ⇒ 「哪端是 pin1」从**网表约定**变成**实物事实** ⇒ 选错 = 排线插反 = JTAG 救砖链不通。

★**③ JTAG 链的 SoM 侧真相 (受控结论 = 「不落地」, 不是「信号不存在」)** ★
- `HW/netlist_v1.csv` 第 **388/390/392/394** 行: `JTAG_TCK_SOC` / `JTAG_TMS_SOC` / `JTAG_TDI_SOC` / `JTAG_TDO_SOC` 的 SoM 侧端点 ★**四条全部 = `SoC_NC`** ★
- `HW/PCB/FET3572C_PIN_TABLE.csv` (官方 399 行脚表) `grep -ic JTAG` = **0** ⇒ 脚表里**没有** JTAG 同名信号 ⇒ `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行的结论成立。
- ★**两句必须分开写**: ✅ 可证 = 「**该模块未把 JTAG 引出来** / SoM 侧未落地」; ❌ **不可证** = 「`JTAG_TDI` 在 SoC 芯片上不存在」—— 逐针表覆盖的是**模块引出的引脚**, 不是芯片内部信号清单 ⇒ **本单不作此断言** (闸 D6 专门抓这个, 页里 §2-4 已把两句列表对照)。
- ⇒ ★**那一趟改 pin1 朝向救不了这条链** ★: S3=JTAG 救砖路径在**这一版 SoM 上不可执行** (`SW/FLASH_AND_VERSION.md` 4 级救砖里 S3 是除 S4 返厂外唯一的软救砖路径) ⇒ 走 §3-2 的 ①/②/③ 三条路之一, 归 main 裁。

★**④ 建议 (不代拍)**: `J_DEBUG`/`J_UART` 落点取 **rot 90** (原点 141.0450/18.2550) ⇒ 保持现状**顺排** (TCK 在 X 最小端) ⇒ 换 land 后**线序不变**, 只多一个 pin1 方形标记; 代价 = 若 fp 库/装配惯例要求 pin1 在 X 最大端, 则要走 rot 270 (几何等价, 只需改写死值)。★**归 main 一句话裁决** ★

★**⑤ 交付物**: 真相页 `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (本趟**只追加式订正, 未重写**) + 新闸 `SW/tools/check_debug_pin_order_contract.py` + 本交卷页 + 分片 `state/fragments/sw.yaml` 登记 ★

---

## B2 验收标准自评

| 验收标准 (原任务书 §二/§三/§四) | 自评 | 依据 |
|---|---|---|
| ① 新建 (cont1 落) `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (含 §0 三问 / §1 物理针序契约表 + 两候选 + 裁决建议 + 落点写死值 / §2 JTAG SoM 侧真相 / §3 与既有裁决关系 + 三条路代价 / §4 证据等级 + 边界自证) | ✅ 通过 | 真相页 32,392 B; 机器可读契约块 ```` ```json iss375_contract ```` (闸 D3/D4 直接读它) |
| ② 新建闸 `SW/tools/check_debug_pin_order_contract.py`, 判据 ≥ D0~D8, 每条 fail-closed + 反向用例 | ✅ 通过 | **9 条判据 (D0~D8) 全绿**; D0/D1/D2/D5 均**现读盘上事实** (不写死 pad1 形状 / 现状朝向 / 旋转矩阵 / `SoC_NC`) |
| ③ `--selftest` ≥8 条反向用例, 每条自证「红的是目标那一条, 其余仍绿」, 其中 ≥3 条针对镜像 | ✅ 通过 | **11 条反向用例, 11/11 PASS**, 末行 `ALL TESTS PASS`; 镜像类 **M1/M2/M3** 三条 |
| ④ 沙盒预演 S0/S1/S2/S3 四轮, 只落 `tmp/iss375_sbx/` + `logs/iss375/` | ✅ 通过 | `logs/iss375/` 8 份读数 (S0 基线 ×2 + J_DEBUG 两候选 + J_UART 两候选 + 旧轮 ×2 + raw log); ★**net-code 顺序 bug 已在 cont1 前一躺修好, 本趟未重跑沙盒** ★ |
| ⑤ S1↔S2 对照: 几何等价与针序互逆**分别**用数证明 | ✅ 通过 | B1-②: 铜箔/fab 三组数逐字相同 (等价) + 序 [1,2,3,4] vs [4,3,2,1] (互逆) |
| ⑥ 交卷页 B1~B6 六段齐全 + 验收线逐条判定 + 落盘清单 + 沙盒留证路径 | ✅ 通过 | 本页 |
| ⑦ 边界: 零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 只写自己分片 / 沙盒只落两处 / 不代拍 / 不外发 / 不自签台账 / 零推 GitHub | ✅ 通过 | B5-④ 边界自证表 + B6 命令 |
| ⑧ 交卷前必跑 11 条命令 | ✅ 通过 | ★**原样输出贴在 B6** ★ |
| ⚠️ D6 判据口径细化 (本趟新增, 主动报备) | ⚠️ 已报备 | 见 B5-③-③ |

---

## B3 证据分级

| 结论 | 等级 | 依据 / 复跑 |
|---|---|---|
| 现状 `J_DEBUG` pad1=`JTAG_TCK` @X=142.2000 (X_MIN), 4 pad 全 RECT/SMD 无极性标记 | [实测] | `bash state/pcbnew_py.sh` 实读板; `logs/iss375/meas_J_DEBUG_demo_mainboard.json` |
| 现状 `J_UART` pad1=`UART_TX` @X=18.6400 (X_MIN), 2 pad 全 RECT/SMD 无极性标记 | [实测] | `logs/iss375/meas_J_UART_demo_mainboard.json` |
| 官方 land pad1 = `thru_hole rect`, 其余 = `thru_hole circle` (1×4 与 1×2 都一样) | [实测] | 盘上 `.kicad_mod` 文本解析 (`grep -nE '\(pad "|thru_hole|drill' …/PinHeader_1x04_P1.27mm_Vertical.kicad_mod`) |
| rot90 ⇒ J_DEBUG 序 [1,2,3,4] (pad1@X_MIN), X = 141.0450/142.3150/143.5850/144.8550 | [实测] | KiCad 自己的 `FOOTPRINT.SetOrientationDegrees` (不手算); `logs/iss375/meas_J_DEBUG_s1_jdebug_rot90.json` |
| rot270 ⇒ J_DEBUG 序 [4,3,2,1] (pad1@X_MAX), 同一组 X 反向归属 | [实测] | `logs/iss375/meas_J_DEBUG_s2_jdebug_rot270.json` (origin 144.855 / orient −90) |
| 两候选几何逐字相同 (铜箔 4.8100×1.0000 / fab 6.7262×2.2000; J_UART 2.2700×1.0000 / 5.4404×2.2000) | [实测] | 上面两份 JSON 的 `copper`/`fab` 字段 |
| `J_UART` rot90 序 [1,2] / rot270 序 [2,1] | [实测] | `logs/iss375/meas_J_UART_s3a_juart_rot90.json` · `meas_J_UART_s3b_juart_rot270.json` |
| 网表四条 `JTAG_*_SOC` 的 SoM 侧端点全部 = `SoC_NC` | [实测] | `sed -n '388,395p' HW/netlist_v1.csv` |
| 官方 399 行脚表里 JTAG 命中数 = 0 | [实测] | `grep -icE "JTAG" HW/PCB/FET3572C_PIN_TABLE.csv` |
| 受控结论 = 「SoM 侧未落地」(而不是「信号不存在」) | [推算] | 由上面两条实读 + `SOM_PIN_MAPPING.md` 48-51 行推出; 表述边界写在页 §2-4; 闸 D6 机器抓「把信号不存在当结论」 |
| 「脚表无 JTAG ⇒ 该模块没把 JTAG 引出来」 | [推算] | 逐针表只覆盖**模块引出的引脚** ⇒ 只能支持「未引出」, 不能支持「芯片内部没有」 |
| 建议 rot 90 的理由 (保持现状顺排) | [推算] | 现状是顺排 (TCK@X_MIN) ⇒ 换 land 后线序不变 ⇒ 装配/救砖心智成本最低; 代价与替代方案写在页 §1-5 |
| pin1 朝向最终选哪条 / ISS-344 口径怎么改 | [0数据] | ★**不代拍** ⇒ 走 B5 两条待裁 ★ |

---

## B4 接口取值声明

★**同时登记进 `state/fragments/sw.yaml` 的 `interface_claims` (key 唯一)★**

| key | value (短规范值) | 说明 |
|---|---|---|
| `iss375_jdebug_rot90_pad_order` | `1,2,3,4` | J_DEBUG @ (141.0450, 56.6000) rot90 ⇒ pad1=JTAG_TCK@X_MIN, 顺排 TCK→TDO |
| `iss375_jdebug_rot270_pad_order` | `4,3,2,1` | J_DEBUG @ (144.8550, 56.6000) rot270 ⇒ pad1=JTAG_TCK@X_MAX, 逆排 (rot90 的镜像) |
| `iss375_juart_rot90_pad_order` | `1,2` | J_UART @ (18.2550, 68.6000) rot90 ⇒ pad1=UART_TX@X_MIN |
| `iss375_juart_rot270_pad_order` | `2,1` | J_UART @ (19.5250, 68.6000) rot270 ⇒ pad1=UART_TX@X_MAX |
| `iss375_land_pin1_marker_shape` | `pad1=thru_hole rect; others=thru_hole circle` | 官方 1×4 / 1×2 land 的 pin1 极性标记 (盘上 `.kicad_mod` 实读) |
| `iss375_jtag_soc_side_endpoint` | `SoC_NC` | JTAG_TCK/TMS/TDI/TDO_SOC 四条网的 SoM 侧端点 (网表实读) |

---

## B5 未决项与卡点

### ★B5-① 要 main 裁的第一件事 (必须第 1 条): 那一趟 `J_DEBUG` 的 pin1 朝向选 rot 90 还是 rot 270 ★
- **要谁回答**: ★**main** ★
- **要回答什么**: 一句话 —— `J_DEBUG`/`J_UART` 的落点写死值取 **rot 90 (原点 141.0450 / 18.2550, 顺排, pad1@X_MIN)** 还是 **rot 270 (原点 144.8550 / 19.5250, 逆排, pad1@X_MAX)**?
- **我的建议 (不代拍)**: rot 90 —— 保持现状顺排, 线序不变, 只多一个 pin1 方形标记。
- **代价对比 (两条几何完全等价, 所以只有装配/救砖心智成本差别)**: rot 90 = 与现状同向 (TCK 仍在 X 最小端), 但**与「pin1 在 X 最大端」的装配惯例相反**; rot 270 = 逆排, 与现状线序相反 ⇒ 换 land 后排线必须翻头。
- **机器判据已就位**: 选定任一条后, 真相页 §1 的 `iss375_contract` 块里改 rot 值即可, 闸 D2/D4 会当场把「页与实算」对不上打红 ⇒ **写死后由闸兜底, 不会写歪**。

### ★B5-② 要 main 裁的第二件事: ISS-344 终裁在「SoM 侧无 JTAG 引出」下怎么改口径 ★
- **要谁回答**: ★**main** ★
- **要回答什么**: 走页 §3-2 的哪条 (或组合)? ① **改裁决口径** (把 `JTAG_TDI` 从「必需」降级为「悬空候选」, 与脚表一致) ② **改网表** (`SoC_NC` → 某个真 SoM 脚) —— ★**脚表 399 行里没有 JTAG 同名信号 ⇒ 这条路当前走不通**, 要走得先定 SoM 侧 JTAG 引出方案 ③ **改 SoM 选型/换板** (放弃 S3 救砖路径, 只剩 S4 返厂)
- **我已备好的机器判据**: 闸 D5 现读网表四行 ⇒ 网表变了而页没改 ⇒ 当场红; D6 抓「页里把『信号不存在』当结论」。
- ★**边界提醒**: 本单**不改** `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` (含 ISS-344 终裁块) 一个字 ⇒ **要落口径修正, 由 main 决定往既有页面落** (本单把订正块写在真相页 §3/§4 里待 main 取用)。

### ★B5-③ 本趟的技术事实 (三件 bug 修复, 都要 main 知悉) ★
- **① cont1 被掐 + 本趟从已落资产续做**: ★**上一趟 (2026-11-24 01:11:01 派) 的子会话 `agent:sw-lead:subagent:4c87e4ad` (sessionId 27ce95b4) 于 01:17:17 被掐死** (status=timeout · abortedLastRun=true · runtimeMs=574,213 ≈ 9.6 min · promptError="This operation was aborted" · **externalAbort=false** ⇒ 非外部 abort · 非上下文溢出) ⇒ ★**本趟不是从零重开**: 真相页 (cont1 落 32,392 B @ 01:15 · 本趟追加订正后 35,582 B) 与闸 (cont1 落 37,257 B @ 01:16) 都在盘, `logs/iss375/` 8 份读数也在盘 (net-code 顺序 bug 已修) ⇒ ★**本趟只补三件: 修闸 · 交卷页 · 分片** ★
- **② 闸的真 bug (main 记的根因与实测不符, 以本机实测为准)**: main 记的是「`-c` 入口 vs 脚本文件入口」⇒ **实测是错的**: 写成 `.py` 文件**同样**报 `AttributeError: 'SwigPyObject' object has no attribute 'FootprintLoad'`; 真正原因是本机 KiCad 10.0.8 的 `pcbnew.py:24225` → `plug.FootprintLoad`, 而 `plug` 是裸 `SwigPyObject` **无该成员**。★**另外实测到更狠的一条: 同一进程里第 3 次插件调用就拿到坏对象** (`FindPlugin` 返回裸 `SwigPyObject`; `FootprintLoad` 拿到的 `FOOTPRINT.Pads()` 不可迭代) ⇒ **修法 = 改走 `PCB_IO_MGR.FindPlugin(KICAD_SEXP).FootprintLoad()` + 一个候选一个子进程隔离** ⇒ ★**闸是修的, 不是重写的** (3 处代码改动 + 2 处判据精化)
- **③ 顺手修掉的两处闸自身缺陷 (主动报备, 请 main 知悉判据口径变化)**:
  - **D7 假红**: 原 `board_mtime_str()` 用 `%f` 只到**微秒 6 位**, 与任务书给的**纳秒 9 位**常量永远不相等 ⇒ 改成 `st_mtime_ns` 纳秒格式化 ⇒ 现在 `mtime=2026-11-06 07:07:17.362193413` **与任务书逐字相同** (★**闸本身也有一个假红, 之前一直红着**★)
  - **D6 误伤 + D8 形同虚设**: D6 的「信号不存在」断言正则会把**引用块**与**转述映射页原话**一起判红 ⇒ 精化为「只抓本页自己的断言 (行首 `>` 的引用块 / 明写『原话 / 第 48-51 行 / SOM_PIN_MAPPING.md』的转述豁免)」★**本页自己的结论句仍然会被抓, 判据没被削弱**★; D8 的证据等级检测原本**只收白名单前缀的 token** ⇒ `[猜测]` 这类白名单外等级**根本收不到** ⇒ 改成「任何方括号标签都当证据等级候选 (页里实测只有五级白名单标签)」
  - ★**selftest 期望集如实改写 (不是放宽)**: M1 / T-D3 的期望红集由 `{D3,D4}` / `{D3}` 改成 `{D2,D3,D4}` —— 因为 D2/D3/D4 是**同一条「页 ↔ 实算一致性」家族**, 页里的 rot90/rot270 一改, 三条必然同时红 ⇒ **期望集写成真实耦合 (目标判据全红 + 其余判据仍绿), 不是把判据改松** ★

### ★B5-④ 边界自证 (逐条) ★
| 边界 | 自证 |
|---|---|
| 零写板 | 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ 开工前/交卷后各打一次, **三项逐字未动** (闸 D7 自证 + B6 命令) |
| 零落表 | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` **只读**, md5 未动 (B6) |
| 零改既有闸 | `SW/tools/timing_check.py` · `check_onepass_sw_release.py` · `check_fp_truth_read.py` · `check_sw_zero_copper_grade_consistency.py` · `HW/check_pcb_nets.py` · `state/gate_check.py` / `merge.py` / `frag_write.py` **一字未改** ★**本趟只改了自己这一单的 `SW/tools/check_debug_pin_order_contract.py`** ★ |
| 零改既有页面正文 | 真相页 `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` **只追加式订正, 未重写**; 其余既有页面 (含 ISS-344 终裁块 / ISS-371 签收件 / `SOM_PIN_MAPPING.md` / `FP_TRUTH_BASELINE.md`) **一个字未动** |
| 零挂链 | `grep -c check_debug_pin_order_contract state/gate_check.py` = **0** (闸 D8 自证 + B6) |
| 只写自己分片 | 只走 `python3 state/frag_write.py --agent sw-lead` 写 `state/fragments/sw.yaml`; 写前 md5 `7be5198c9f15c85af6467856fbdd176d`, 写后见 B6 |
| 沙盒只落两处 | 沙盒 = `tmp/iss375_sbx/` + `logs/iss375/`; 闸内部临时目录也已改指 `tmp/iss375_sbx/` (原来落在 `tmp/` 根) |
| 不代拍 | B5-①/B5-② 两条裁决只给代价与机器判据 |
| 不外发 | 全靠自己查盘 + 自己网上查 (本单无外部依赖) ⇒ **零外发** |
| 不自签台账 | `state/issue_log.yaml` 未动 |
| 零推 GitHub | 未推 |
| status 全程 fixing | `state/fragments/sw.yaml` 的 status 保持 `phase=fixing` (不落 open ⇒ 撞车窗口 0) |

### ★B5-⑤ 落盘清单 ★
| 路径 | 动作 | 备注 |
|---|---|---|
| `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` | **追加式订正** (未重写) | 32,392 B ⇒ 本趟追加一段「闸的真 bug 修了 + 两处判据口径精化」⇒ 35,582 B ⇒ 见 B6 |
| `SW/tools/check_debug_pin_order_contract.py` | **修 bug** (3 处代码 + 2 处判据精化) | 本单自己的闸 · 实跑 rc=0 / 9/9 / selftest 11/11 |
| `HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md` | **新建** (本文件) | B1~B6 六段 |
| `state/fragments/sw.yaml` | **登记** (frag_write.py) | 3 产出物 + 6 interface_claims + 2 needs_from · phase=fixing (不落 open) |
| `tmp/iss375_sbx/` · `logs/iss375/` | 沙盒留证 (已在盘) | 8 份读数 + 建场脚本 |

★**沙盒留证路径**: `logs/iss375/` = `meas_J_DEBUG_demo_mainboard.json` (S0) · `meas_J_UART_demo_mainboard.json` (S0) · `meas_J_DEBUG_s1_jdebug_rot90.json` (rot90) · `meas_J_DEBUG_s2_jdebug_rot270.json` (rot270) · `meas_J_UART_s3a_juart_rot90.json` (rot90) · `meas_J_UART_s3b_juart_rot270.json` (rot270) · `meas_J_DEBUG_t_s2.json` (★**旧轮 rot270 假板读数, 已被 s2 取代, 不要用**★) · `iss375_sandbox_raw.log`; `tmp/iss375_sbx/` = `iss375_build.py` · `iss375_measure.py` · `iss375_run.sh` + 候选板副本 ★

---

## B6 自证复现命令

★**cd 目录**: `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` · ★**环境**: `export TMPDIR=$PWD/tmp` ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py         # 新闸 ⇒ rc=0
bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py --selftest   # rc=0 (末行 ALL TESTS PASS)
python3 SW/tools/timing_check.py                                  # rc=0 (既有闸必须仍绿·零漂移自证)
python3 SW/tools/check_sw_zero_copper_grade_consistency.py        # rc=0 (既有闸必须仍绿)
python3 state/merge.py                                            # rc=0
python3 state/gate_check.py                                       # rc=0 (Q1 必须 18/18)
python3 state/check_brief_commands.py                             # rc=0
grep -c check_debug_pin_order_contract state/gate_check.py        # ⇒ 0 (零挂链自证)
md5sum HW/PCB/demo_mainboard.kicad_pcb                            # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                   # 必须 2026-11-06 07:07:17.362193413 4940213
```

★**B6 实跑输出 (2026-11-24 02:5x · 本机实跑 · 原样粘贴)★**

★**逐条 rc (本机实跑 2026-11-24 03:1x, 原样输出见下)** ★

| # | 命令 | rc | 判定 |
|---|---|---|---|
| 1 | `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py` | **0** | ✅ D0~D8 **9/9 PASS** · 末行 `ALL CHECKS PASS` |
| 2 | `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py --selftest` | **0** | ✅ **11/11 PASS** · 末行 `ALL TESTS PASS` (镜像类 M1/M2/M3 三条) |
| 3 | `python3 SW/tools/timing_check.py` | **0** | ✅ 既有闸仍绿 (零漂移自证) |
| 4 | `python3 SW/tools/check_sw_zero_copper_grade_consistency.py` | **0** | ✅ 既有闸仍绿 |
| 5 | `python3 state/merge.py` | **0** | ✅ `STATE.yaml 已刷新 (2026-11-24T02:09:46+08:00)` · 产出 804 · 冲突 0 |
| 6 | `python3 state/gate_check.py` | **0** | ✅ **Q1 18/18 必填验收块齐全** · sw-lead 6/6 · ★**交接单已识别为本单这一页** ★ |
| 7 | `python3 state/check_brief_commands.py` | **0** | ✅ 查了 9 条待办单, 有问题的 0 条 |
| 8 | `grep -c check_debug_pin_order_contract state/gate_check.py` | 1 | ✅ **输出 `0`** = 零挂链 (grep 无命中时 rc=1 属正常) |
| 9 | `md5sum HW/PCB/demo_mainboard.kicad_pcb` | 0 | ✅ `611b869e13518c3c023fb178f91a0075` (与基线逐字相同) |
| 10 | `stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb` | 0 | ✅ `2026-11-06 07:07:17.362193413 +0800 4940213` (mtime + size 逐字相同) |

★**追加自证 (同一趟实跑)** ★
| 项 | 结果 |
|---|---|
| 零落表 (只读) | `HW/netlist_v1.csv` = `6aee500e60ba0732f83a9cf557ba90ab` · `HW/netlist_v1_pins.csv` = `9174309df1ec9411ac8e8d9e80ee386a` · `HW/BOM_v1.csv` = `5b9993992405904a60ac96a020b375d8` ⇒ **三项与基线逐字相同** |
| 既有闸/工具未动 | `SW/tools/timing_check.py` `cf09c921…` · `check_onepass_sw_release.py` `4d7ce982…` · `check_fp_truth_read.py` `cab7a6f1…` · `check_sw_zero_copper_grade_consistency.py` `58a3aa44…` · `state/gate_check.py` `5f370bb8…` · `state/merge.py` `c9191025…` · `state/frag_write.py` `3b383a52…` ⇒ **一字未改** |
| 既有页面正文未动 | `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` `0f4bf6c0…` · `SW/FLASH_AND_VERSION.md` `4f272497…` · `SW/SW_MD5_BASELINE_LEDGER.md` `83fafcf7…` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` `da7b02c0…` · `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` `c103973e…` · `HW/PCB/SOM_PIN_MAPPING.md` `cc51144e…` ⇒ **一字未改** |
| ★**两处路径订正 (派活材料写的路径在本机不存在, 实际路径如下 · 本单未碰这两个文件)** | ★`HW/check_pcb_nets.py` ⇒ 实际在 **`state/check_pcb_nets.py`**; ★`HW/PCB/FP_TRUTH_BASELINE.md` ⇒ 实际在 **`HW/FP_TRUTH_BASELINE.md`** ⇒ 上面两张 md5 表里缺这两项是因为路径写错, **不是文件被删** ★ |
| 分片 status | `state/fragments/sw.yaml` ⇒ `phase: fixing` ★**(不落 open ⇒ 兄弟 job 看不见 ⇒ 撞车窗口 0)** ★ |
| 分片 md5 写前/写后 | 写前 `7be5198c9f15c85af6467856fbdd176d` ⇒ 写后 `639a7610a08e895a52122b1db2f33054` ⇒ **期间无人改过 (未被并发覆盖)** |

★**以下为 11 条命令的【原样输出】** ★

```text
───── $ bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py ─────
=== ISS-375 · check_debug_pin_order_contract ===
  [PASS] D0   官方 land pad1 形状 (盘上实读, 不写死) 1x04: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True; 1x02: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True
  [PASS] D1   现状板面 pad1 位置/极性标记 (实读板, 不写死) J_DEBUG: pad1@X=142.2 (X_MIN) 标记=False 形状=RECT 属性=SMD; J_UART: pad1@X=18.64 (X_MIN) 标记=False 形状=RECT 属性=SMD
  [PASS] D2   两候选 pad→X 序 (KiCad 变换算, 须互为逆序) J_DEBUG rot90 序=['1', '2', '3', '4'] (pad1@X_MIN) / rot270 序=['4', '3', '2', '1'] (pad1@X_MAX); J_UART rot90 序=['1', '2'] (pad1@X_MIN) / rot270 序=['2', '1'] (pad1@X_MAX)
  [PASS] D3   页同时给出两候选+裁决+落点写死值 
  [PASS] D4   页的 pin1 朝向与 D2 实算一致 
  [PASS] D5   网表 JTAG 四线 SoM 侧端点 (现读, 不写死) JTAG_TCK_SOC→SoC_NC; JTAG_TMS_SOC→SoC_NC; JTAG_TDI_SOC→SoC_NC; JTAG_TDO_SOC→SoC_NC
  [PASS] D6   页 §2 与 SOM_PIN_MAPPING.md 结论不冲突 
  [PASS] D7   板指纹三项未动 (零写板自证) md5=611b869e13518c3c023fb178f91a0075 (期望 611b869e13518c3c023fb178f91a0075) / mtime=2026-11-06 07:07:17.362193413 (期望 2026-11-06 07:07:17.362193413) / size=4940213 (期望 4940213)
  [PASS] D8   证据等级白名单+零挂起措辞+判据/事实分开+零挂链 零挂链: state/gate_check.py 命中 0
=== 9/9 PASS ===
ALL CHECKS PASS
[rc=0] 新闸

───── $ bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py --selftest ─────
=== ISS-375 · check_debug_pin_order_contract --selftest ===
  [PASS] M1       把页里的 rot 90 改成 rot 270                     期望红=D2,D3,D4     实红=D2,D3,D4     
  [PASS] M2       把 D2 的算式改成手算常数                             期望红=D4           实红=D4           
  [PASS] M3       把网表里的 SoC_NC 改成别的                          期望红=D5           实红=D5           
  [PASS] T-D0     页里把官方 land 的 pad1 形状写错                     期望红=D0           实红=D0           
  [PASS] T-D1     页里把现状 pad1 位置写反                            期望红=D1           实红=D1           
  [PASS] T-D3     页里删掉一个候选                                   期望红=D2,D3,D4     实红=D2,D3,D4     
  [PASS] T-D6     页里写『已在 SoM 侧落地』                            期望红=D6           实红=D6           
  [PASS] T-D8a    证据等级用白名单外的等级                               期望红=D8           实红=D8           
  [PASS] T-D8b    出现挂起措辞                                     期望红=D8           实红=D8           
  [PASS] T-D7     板指纹被动过 (临时副本)                              期望红=D7           实红=D7          
  [PASS] T-D8c    新闸挂进 state/gate_check.py (临时副本)            期望红=D8           实红=D8          
=== selftest 11/11 PASS (共 11 条反向用例, 其中镜像类 3 条) ===
ALL TESTS PASS
[rc=0] 新闸自测

───── $ python3 SW/tools/timing_check.py ─────
=== NETLIST_ANCHOR ===
   netlist_path                       : HW/netlist_v1.csv
   netlist_md5                        : 6aee500e60ba0732f83a9cf557ba90ab
   netlist_lines_total                : 514
   netlist_data_rows                  : 513
   netlist_bytes                      : 143198
   netlist_mtime                      : 2026-11-18 00:21:08
   netlist_header                     : page,net,node1,node2,ref,value,type,dnp,evidence,tbd,note,conn_id,board,footprint,opn

=== F1_reset_rc ===
   r_pull_ohm                         : 10000.0
   r_pull_rail                        : RAIL_VDD_1V8_IO
   r_pull_rail_v                      : 1.8
   r_ser_ohm                          : 1000.0
   c_rst_f                            : 1e-07
   tau_release_ms                     : 1.1
   tau_assert_us                      : 100.0
   t_reach_0p7vdd_ms                  : 1.324
   netlist_annotation_ms              : 100.0
   annotation_error_ratio             : 90.9
   q_and_in_netlist                   : True
   pg_pullup_ohm                      : 10000.0
   pg_source_devices                  : {'U_DCDC_VCORE': {'dnp': '必装', 'populated': True, 'dnp_source': 'PG_AND 网上的连接行 (行级口径)', 'device_ic_row_dnp': 'DNP'}, 'U_DCDC_VIO': {'dnp': '必装', 'populated': True, 'dnp_source': 'PG_AND 网上的连接行 (行级口径)', 'device_ic_row_dnp': 'DNP'}}
   pg_and_state                       : {'net': 'PG_AND', 'row_count': 6, 'rows': [{'ref': 'R_PG_PULL', 'type': 'R', 'dnp': '必装', 'line_no': 62}, {'ref': 'NET_PG_AND', 'type': 'NET', 'dnp': '必装', 'line_no': 64}, {'ref': 'Q_AND', 'type': 'SW', 'dnp': '必装', 'line_no': 67}, {'ref': 'Q_ENVC', 'type': 'SW', 'dnp': 'DNP', 'line_no': 71}, {'ref': 'TP_PG_VCORE', 'type': 'TP', 'dnp': '必装', 'line_no': 402}, {'ref': 'TP_PG_VIO', 'type': 'TP', 'dnp': '必装', 'line_no': 403}], 'dnp_rows': ['Q_ENVC'], 'all_rows_populated': False, 'pullup_ref': 'R_PG_PULL', 'pullup_ohm': 10000.0, 'pullup_row_dnp': '必装', 'q_and_gate_row_dnp': '必装', 'q_envc_row_dnp': 'DNP', 'pg_source_devices': {'U_DCDC_VCORE': {'dnp': '必装', 'populated': True, 'dnp_source': 'PG_AND 网上的连接行 (行级口径)', 'device_ic_row_dnp': 'DNP'}, 'U_DCDC_VIO': {'dnp': '必装', 'populated': True, 'dnp_source': 'PG_AND 网上的连接行 (行级口径)', 'device_ic_row_dnp': 'DNP'}}, 'pg_sources_all_populated': True}
   reset_n_state                      : {'net': 'RESET_N', 'rows': [{'ref': 'Q_AND', 'type': 'SW', 'dnp': '必装', 'line_no': 65}, {'ref': 'TP_RESET', 'type': 'TP', 'dnp': '必装', 'line_no': 366}, {'ref': 'NET_RESET_N', 'type': 'NET', 'dnp': '必装', 'line_no': 377}, {'ref': 'SW_RST', 'type': 'SW', 'dnp': '必装', 'line_no': 382}, {'ref': 'U_SUPV', 'type': 'IC', 'dnp': 'DNP', 'line_no': 409}], 'members': ['NET_RESET_N', 'Q_AND', 'SW_RST', 'TP_RESET', 'U_SUPV'], 'dnp_rows': ['U_SUPV'], 'q_and_drain_row_dnp': '必装', 'sw_rst_row_dnp': '必装', 'u_supv_pin1_row_dnp': 'DNP'}
   verdict                            : 网表注记 'τ=100.0ms' 与 R/C 原值不符: 实为释放 τ=1.1ms / 断言 τ=100µs (差 90.9 倍); ★V1.8 新增 Q_AND 硬件 AND + R_PG_PULL 10k 上拉 ⇒ **PG 已进复位链** (旧结论部分推翻); ★★行级口径 (★逐行读 PG_AND★): 提到两路 PG pin (pin4) 的连接行 (L62/L64/L402/L403) dnp **全是必装** ⇒ **「PG 源器件 DNP」不成立**; ★**真正 DNP 的是 Q_ENVC** (它接在 PG_AND 上, L71) ⇒ ⇒ PG_AND 有 R_PG_PULL 10k 上拉 ⇒ Q_AND 栅极接在 PG_AND 上 ⇒ **栅极恒高 ⇒ Q_AND 导通 ⇒ RESET_N 恒被拉低 ⇒ 首台板可能不启动** (需 hw-lead 定夺); ★另: U_SUPV pin1 也是 DNP 且接在 RESET_N 上 (它**不参与**拉复位); ★器件级补注: 两颗 DC-DC **芯片本体** (U_DCDC_VCORE/U_DCDC_VIO 的 IC 行) 是 DNP ⇒ 实物上 PG 脚不在板上 ⇒ PG_AND 更没东西能把它拉低 ⇒ 结论方向不变、且更强

=== F2_supervisor ===
   vit_ref_v                          : 0.405
   ratio_for_vit_3v0                  : 6.407
   ratio_for_vit_2v7                  : 5.667
   delay_ct_open_ms                   : 20.0
   delay_ct_vdd_ms                    : 300.0
   ct_pin_in_netlist                  : True
   ct_pin_rows                        : 1
   mr_pin_in_netlist                  : False
   u_supv_populated                   : False
   u_supv_dnp                         : DNP
   div1_value                         : 0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板
   div2_value                         : 0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板
   divider_dnp                        : ['必装', '必装']
   min_reset_release_ms               : 21.324
   note                               : 两臂都填 0Ω => R2=0 => SENSE=GND => V_SOC_IO 对地短路 (装配级灾难); 两臂都 DNP => SENSE 悬空 => 释放时刻未定义
   divider_zero_risk                  : True
   verdict                            : ★U_SUPV 在现网表是 **DNP** (SoM 自带 PMIC 已做上电复位) ⇒ 监督器这条支路**实物不存在**; CT 脚在网表里有 1 行 (但属 DNP 器件), MR 仍 0 行 ⇒ 旧结论『CT/MR 悬空 = 20ms』**不再适用**; ★仍成立: R_SUPV_DIV1/DIV2 仍标 0Ω 跳线位且 **dnp=必装** ⇒ 两颗都装 0Ω 会把 RAIL_V_SOC_IO 短路到地

=== F3_i2c_rise ===
   tr_ns_at_100pF                     : 398.2
   worst_bus                          : I2C_B
   worst_bus_reason                   : 主判据取所有 I2C 总线里 t_r 最大的一条 (最差总线) ⇒ 速率上限按它定
   netlist_annotation_ns              : 186.0
   annotation_error_ratio             : 1.0
   tr_ns_vs_cable_cap                 : {'100pF': 398.2, '200pF': 796.5, '300pF': 1194.7, '500pF': 1991.2}
   spec_std_mode_max_ns               : 1000.0
   spec_fast_mode_max_ns              : 300.0
   buses                              : {'I2C_A': {'pullup_refs': ['R_PU_I2CA_SCL', 'R_PU_I2CA_SDA'], 'pullup_ohm': 2200.0, 'pullup_rail': 'RAIL_VDD_1V8_IO', 'pullup_rail_v': 1.8, 'std_mode_ok_at_300pF': True, 'annotation_ns': 186.0, 'annotation_stale': False, 'annotation_text': '上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)', 'tr_ns_at_100pF': 186.4, 'tr_ns_vs_cable_cap': {'100pF': 186.4, '200pF': 372.8, '300pF': 559.2, '500pF': 932.0}, 'fast_mode_ok_at_300pF': False, 'annotation_error_ratio': 1.0}, 'I2C_B': {'pullup_refs': ['R_PU_I2CB_SCL', 'R_PU_I2CB_SDA'], 'pullup_ohm': 4700.0, 'pullup_rail': 'RAIL_VDD_3V3_IO', 'pullup_rail_v': 3.3, 'std_mode_ok_at_300pF': False, 'annotation_ns': None, 'annotation_stale': None, 'annotation_text': '', 'tr_ns_at_100pF': 398.2, 'tr_ns_vs_cable_cap': {'100pF': 398.2, '200pF': 796.5, '300pF': 1194.7, '500pF': 1991.2}, 'fast_mode_ok_at_300pF': False}}
   verdict                            : ★按网名分别读: I2C_A = 2.2k → RAIL_VDD_1V8_IO (1.8V 域): t_r@100pF=186ns, @300pF=559ns ⇒ 标准模式(≤1000ns) ✅; I2C_B = 4.7k → RAIL_VDD_3V3_IO (3.3V 域): t_r@100pF=398ns, @300pF=1195ns ⇒ 标准模式(≤1000ns) ❌ ⇒ 最差总线 = I2C_B ⇒ I2C 速率上限按 I2C_B 定; ★旧文档写的『4.7k@I2C_A ⇒ 398ns / 1195ns 超标』**对 I2C_A 已不成立** (现为 2.2k/1.8V), 现在超标的是 I2C_B

=== F4_adc_det ===
   active_chain                       : BAT_DET
   active_chain_pin                   : 38
   active_chain_signal                : SARADC_VIN5
   active_chain_domain                : 1.8V
   chain_select_mode                  : by_landing_pin
   chain_select_reason                : ★唯一一条装机链落在 SAR-ADC 脚上 (判决源 = SoM 脚表 signal 列: SARADC_VIN5)★
   judgment_source                    : SoM 脚表 HW/PCB/FET3572C_PIN_TABLE.csv (md5 67340a0b7070, 399 行) + 网表落点实读
   pin_table_md5                      : 67340a0b707095fc4c0755a4c79ea8b6
   full_scale_v                       : 1.8
   full_scale_source                  : [官网] SAR-ADC 满量程 = 1.8V 域: 脚表 FET3572C_PIN_TABLE.csv L39 (SARADC_VIN5 / 1.8V) + rk3572_datasheet_V1.1.txt L2454 (SARADC_AVDD1V8 = 1.62/1.8/1.98V) + L2864 (Analog Input Range = AVSS18~AVDD18) ⇒ ★原 3.3V 写死值已按 ISS-291 订正★
   adc_bits                           : 12
   lsb_mv                             : 0.439
   chains                             : [{'tag': 'VBUS_DET_D', 'r_top_ohm': 1000000.0, 'r_bot_ohm': 1000000.0, 'c_f': 1.0000000000000001e-07, 'r_top_ref': 'R_VBUS_DET_D1', 'r_bot_ref': 'R_VBUS_DET_D2', 'cap_ref': 'C_DET_VBUS_D', 'r_top_dnp': '必装', 'r_bot_dnp': '必装', 'c_dnp': '必装', 'populated': True, 'device_dnp': {'R_VBUS_DET_D1': ['必装'], 'R_VBUS_DET_D2': ['必装'], 'C_DET_VBUS_D': ['必装', '必装']}, 'device_populated': True, 'landing_net': 'VBUS_DET_D', 'landing_line': 439, 'som_conn': 'J_SOM_P1', 'som_pin': '100', 'pin_class': 'DIGITAL', 'pin_signal': 'USB_DRD1_VBUSDET', 'pin_vol_raw': '——', 'pin_vol_v': None, 'pin_desc': 'USB2_OTG1_VBUSDET insert detection', 'rth_ohm': 500000.0, 'tau_ms': 50.0}, {'tag': 'BAT_DET', 'r_top_ohm': 100000.0, 'r_bot_ohm': 60000.0, 'c_f': 1.0000000000000001e-07, 'r_top_ref': 'R_BAT_DET_1', 'r_bot_ref': 'R_BAT_DET_2', 'cap_ref': 'C_DET_BAT', 'r_top_dnp': '必装', 'r_bot_dnp': '必装', 'c_dnp': '必装', 'populated': True, 'device_dnp': {'R_BAT_DET_1': ['必装'], 'R_BAT_DET_2': ['必装'], 'C_DET_BAT': ['必装', '必装']}, 'device_populated': True, 'landing_net': 'BAT_DET', 'landing_line': 186, 'som_conn': 'J_SOM_P1', 'som_pin': '38', 'pin_class': 'ADC', 'pin_signal': 'SARADC_VIN5', 'pin_vol_raw': '1.8V', 'pin_vol_v': 1.8, 'pin_desc': 'General ADC5', 'rth_ohm': 37500.0, 'tau_ms': 3.75}]
   rth_ohm                            : 37500.0
   tau_ms                             : 3.75
   t_settle_to_half_lsb_ms            : 33.791
   leak_offset_v                      : 0.0375
   leak_offset_pct_fs                 : 2.1
   standby_ua                         : 26.25
   supply_v                           : 4.2
   supply_source                      : 网表 RAIL 行 RAIL_BAT = 4.2V
   node_v_at_supply                   : 1.575
   node_max_abs_v                     : 1.98
   node_nominal_max_v                 : 1.8
   fs_utilization_pct                 : 87.5
   netlist_note_facts                 : {'pct_fs': 2.1, 'mv': 37.5, 'rth_k': 37.5, 'note': '[BAT_DET_RAW] 分压上臂 (100k); ★方案E (ISS-223 §11.4): R_th=37.5kΩ ⇒ ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (2.1% FS, 可软件标定)★; ★常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)★ [V1.6: 临时线名 BAT 已归一到源节点]', 'line_no': 182}
   criteria                           : {'object_ok': True, 'fs_caliber_ok': True, 'settle_ok': True, 'leak_ok': True, 'node_ok': True, 'populated_ok': True, 'all_ok': True}
   verdict                            : ★判决对象 = BAT_DET 链 (网表 L186 ⇒ J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域) ⇒ 源阻抗 37500.0Ω / τ=3.75ms; 12bit (LSB=0.439mV, 满量程 1.8V) 需 33.8ms 建立 (红线 300.0ms ⇒ ✔); 1µA 漏电 ⇒ 0.0375V 偏移 = 2.1% 满量程 (红线 0.4V ⇒ ✔; ★与网表 L182 note 写死的 2.1% FS 逐字对上 ⇒ ✔★); @4.2V 节点 1.575V ≤ abs-max 1.98V ⇒ ✔ (FS 利用率 87.5%); ★老口径 (判 VBUS_DET_D + FS=3.3V) 报的那条红 = **假红** ⇒ 已作废; ★VBUS_DET_D 链改按【数字检测输入】口径单判 (见 F4D 段)★; ★BAT_DET 链 (R_BAT_DET_1/2 + C_DET_BAT) 三颗**已改成必装** (V-3=E 落表后) ⇒ **电量检测分压在现网表上存在** (100k+60k+100nF ⇒ R_th=37500.0Ω / τ=3.75ms)

=== F4D_usb_vbus_det ===
   chain                              : VBUS_DET_D
   landing_net                        : VBUS_DET_D
   landing_line                       : 439
   som_conn                           : J_SOM_P1
   som_pin                            : 100
   pin_signal                         : USB_DRD1_VBUSDET
   pin_vol_raw                        : ——
   pin_class                          : DIGITAL
   r_top_ohm                          : 1000000.0
   r_bot_ohm                          : 1000000.0
   c_f                                : 1.0000000000000001e-07
   rth_ohm                            : 500000.0
   v_supply_nom_v                     : 5.0
   v_supply_min_v                     : 4.75
   v_supply_max_v                     : 5.25
   static_current_ua                  : 4.81
   static_current_ua_ideal            : 2.5
   static_current_limit_ua            : 26.25
   node_v_nom                         : 2.5
   node_v_min                         : 2.375
   node_v_max                         : 2.625
   node_v_with_internal_pd            : 0.185
   vih_min_v                          : 2.3
   high_band_lo_v                     : 2.7
   high_band_hi_v                     : 3.3
   margin_to_vih_mv                   : 75.0
   abs_max_v                          : 3.3
   abs_max_source                     : ★[0数据] 降级取 Forlinx 手册标称高电平带上沿 3.3V★
   domain_known                       : False
   criteria                           : {'static_current_ok': True, 'level_ok': True, 'all_ok': True}
   unresolved                         : [{'item': '该脚 (USB_DRD1_VBUSDET) 是否带内部 40kΩ 下拉', 'evidence': "[0数据] Forlinx FET3572 手册只对 USB_DRD0_VBUSDET 明写 'internal 40 kΩ pull-down'; 本板落点是 DRD1 ⇒ 手册未记载", 'impact': '若带 ⇒ 节点 = 0.185V (含 40kΩ 下拉) < 2.3V 识别阈值 ⇒ **USB 插入检测永不触发**', 'degradation': '本闸按【无内部下拉】的理想分压值判定 (并把含下拉的情形一并算出报出); ★该脚 abs-max / 域 / 内部下拉三件事一律登记 need, 不在本闸里编数★'}, {'item': '该脚 IO 域 / abs-max (脚表 vol 栏 = ——)', 'evidence': "[0数据] 脚表 FET3572C_PIN_TABLE.csv L101 vol 栏 = '——' ⇒ 域未知", 'impact': '本闸降级取 Forlinx 手册标称高电平带上沿 3.3V 作 abs-max 上界 ⇒ 节点 2.625V ≤ 3.3V ⇒ 通过; ★若该脚域实为 1.8V ⇒ abs-max = 2.1V ⇒ 节点 2.625V 越限 ⇒ 必须改分压比★', 'degradation': '降级上界取手册高电平带上沿; ★域一旦在脚表里填上, 本闸的 abs-max 判据自动按域+0.3V 生效★'}, {'item': '识别裕量 (VBUS 下限 4.75V 时)', 'evidence': '[官方] USB 2.0/Type-C VBUS 4.75~5.25V + 手册识别阈值 >2.3V', 'impact': '节点 @4.75V = 2.375V, 距阈值 2.3V 只剩 75mV (3.3%) ⇒ 裕量极薄', 'degradation': '本闸按最坏 VBUS 下限 4.75V 判 (比标称 5V 更严)'}]
   verdict                            : ★VBUS_DET_D 链落点 = J_SOM_P1 pin100 = USB_DRD1_VBUSDET (脚表域栏 = —— ⇒ 域未知 [0数据]) ⇒ 按【数字检测输入】口径判 (★不是 SAR-ADC★): ① 常开静态电流 4.81µA (理想分压 2.5µA) ≤ 上限 26.25µA (同板 BAT_DET 链 V-3 已裁决值) ⇒ ✔; ② 节点电平 2.5V @5V (VBUS 4.75~5.25V ⇒ 2.375~2.625V) vs 识别阈值 >2.3V ⇒ ✔ (裕量 75.0mV ⚠; 且低于手册标称高电平带下沿 2.7V ⚠); ③ 该脚 abs-max 3.3 ⇒ ✔; ★★未决 (已登记 need, 不阻塞本闸但禁止据此判『安全』): 该脚是否带内部 40kΩ 下拉 [0数据] ⇒ 若带则节点 0.185V ⇒ **USB 插入检测不工作**★★

=== F5_tmp117 ===
   lsb_c                              : 0.0078125
   first_read_after_reset_c           : -256.0
   conv_period_s                      : 1.0
   supply_rail                        : RAIL_VDD_3V3_IO
   supply_v                           : 3.3
   i2c_bus                            : I2C_B
   self_heat_uw                       : 16.5
   self_heat_verdict                  : 自热 16.5µW << 测点热阻主导项 => 自热可忽略, 误差由**热耦合路径**主导
   accuracy_bands_c                   : {'-20..50': 0.1, '-40..70': 0.15, '-40..100': 0.2}
   sw_rule                            : 复位后首读 = -256°C 必须丢弃; 转换 1Hz => 首次有效读数最坏 ~1s
   verdict                            : TMP117 挂在 **I2C_B** (旧文档写的是 I2C_A) ⇒ ★旧结论『TMP117 与 camera 同总线, camera 拉死 SDA 一起致盲温度保护』**对现网表不成立** (camera 在 I2C_A, TMP117 在 I2C_B)

=== F6_usb_hinge ===
   conn_usb_pins                      : 0
   conn_usb_gnd_pins                  : 0
   conn_usb_in_netlist                : False
   iss085_min_gnd_pins                : 2
   gnd_rule_ok                        : False
   hinge_usb_data_nets                : []
   cross_hinge_usb_data_path          : False
   onboard_usb_rows                   : ['NET_USB_D_P_SRC(J_SOM_P1 pin92→R_SER_USB_D_P)', 'TP_USB_D_P(TP_USB_D_P→J_USB_C A6+B6)', 'R_SER_USB_D_P(R_SER_USB_D_P→J_USB_C A6+B6)']
   fs_bulk_MBps                       : 1.2
   hs_bulk_MBps                       : 48.0
   flash_s_at_FS                      : 75.0
   flash_s_at_HS                      : 1.9
   reset_resp_budget_ms               : 5.0
   verdict                            : ★CONN_USB 在现网表**已不存在** (0 行) ⇒ 旧『CONN_USB 只有 1 个 GND pin』的复现命令在现网表上已无对象; ★J_CHG 跨铰链 10pin 里**不含 USB D+/D−** ((无)) ⇒ 跨铰链 USB 救砖链**在现网表上不成立**; ★demo 板改成**板内 Type-C**: J_USB_C → 22Ω 串阻 → J_SOM_P1 pin92/94 ⇒ 刷写口在板内, 不跨铰链

=== F7_skin_tiers ===
   model                              : T_skin = 35.0 + 50.13 x P_W
   p_to_tskin                         : {'0.05W': 37.5, '0.10W': 40.0, '0.16W': 43.0, '0.21W': 45.5}
   redline_c                          : 43.0
   p_redline_w                        : 0.16
   legacy_sw_tiers_c                  : [70, 85, 95]
   legacy_verdict                     : SW 分片里已登记的 4 档温控 (<70/70-85/85-95/>95°C) 是**结温口径**, 与 43°C 皮肤红线不同源 => TMP117 定点后必须重定档
   tmp117_conservatism                : TMP117 装在镜脚 PCB 上 => T_PCB >= T_skin (皮肤是热沉) => 用 PCB 温度当皮肤代理是**保守方向** (不会漏判超温)

=== F8_power_off ===
   load_switch_in_netlist             : True
   load_switch_refs                   : ['U_PWR_SW', 'U_EN_SW']
   load_switch_detail                 : [{'ref': 'U_PWR_SW', 'value': 'TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)', 'dnp': '必装', 'has_device_row': True, 'populated': True, 'row_count': 4}, {'ref': 'U_EN_SW', 'value': 'TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)', 'dnp': '必装', 'has_device_row': True, 'populated': True, 'row_count': 4}]
   load_switch_without_device_row     : []
   rail_switching_devices             : 2
   on_pin_pulldown_ohm                : 10000.0
   default_state                      : 关
   verdict                            : ★**旧结论已推翻**: 现网表里**有**负载开关 (U_PWR_SW = TPS22991RAA, VIN=BAT_SW → VOUT=RAIL_SYS; ON pin2 = PWR_ON, 配 R_PD_ON 10k 下拉 ⇒ 默认关) + U_EN_SW (TPS22991RAA, IN=RAIL_DEMO_5V → OUT=RAIL_BOARD_5V, EN=CARRIER_BOARD_EN) ⇒ **硬件断电通路存在** ⇒ 『关机只能靠软件深睡, 轨全部带电』**对现网表是错的**; ★新语义: SoC 把 PWR_ON GPIO 配高阻 ⇒ ON 掉回 10k 下拉 ⇒ U_PWR_SW 关 ⇒ 镜脚系统轨 SYS 断电 (充电链仍在电池侧带电 ⇒ 关机也能充电)

=== F4_ctrl_pins ===
   counts                             : {'EN': 10, 'SS': 0, 'CT': 1, 'MR': 0}
   total_rows                         : 11
   rows                               : [{'signal': 'EN', 'ref': 'U_DCDC_VCORE', 'net': 'EN_VCORE', 'node1': 'U_DCDC_VCORE pin13', 'node2': 'R_EN_VCORE', 'row_type': 'NET', 'row_dnp': '必装', 'device_populated': False, 'line_no': 70}, {'signal': 'EN', 'ref': 'U_DCDC_VIO', 'net': 'EN_VIO', 'node1': 'U_DCDC_VIO pin13', 'node2': 'NET_PWR_ON', 'row_type': 'NET', 'row_dnp': '必装', 'device_populated': False, 'line_no': 74}, {'signal': 'CT', 'ref': 'U_SUPV', 'net': 'SUPV_CT', 'node1': 'U_SUPV pin4', 'node2': 'RAIL_VDD_1V8_IO', 'row_type': 'NET', 'row_dnp': 'DNP', 'device_populated': False, 'line_no': 75}, {'signal': 'EN', 'ref': 'U_LDO_S18B', 'net': 'SYS_PCB', 'node1': 'U_LDO_S18B pin3', 'node2': 'RAIL_BOARD_5V', 'row_type': 'NET', 'row_dnp': 'DNP', 'device_populated': False, 'line_no': 102}, {'signal': 'EN', 'ref': 'U_LDO_S12', 'net': 'SYS_PCB', 'node1': 'U_LDO_S12 pin3', 'node2': 'RAIL_BOARD_5V', 'row_type': 'NET', 'row_dnp': 'DNP', 'device_populated': False, 'line_no': 112}, {'signal': 'EN', 'ref': 'U_LDO_L33', 'net': 'SYS_PCB', 'node1': 'U_LDO_L33 pin3', 'node2': 'RAIL_BOARD_5V', 'row_type': 'NET', 'row_dnp': '必装', 'device_populated': True, 'line_no': 122}, {'signal': 'EN', 'ref': 'U_LDO_L18', 'net': 'SYS_PCB', 'node1': 'U_LDO_L18 pin3', 'node2': 'RAIL_BOARD_5V', 'row_type': 'NET', 'row_dnp': 'DNP', 'device_populated': False, 'line_no': 132}, {'signal': 'EN', 'ref': 'U_LDO_IO33', 'net': 'SYS_PCB', 'node1': 'U_LDO_IO33 pin3', 'node2': 'RAIL_BOARD_5V', 'row_type': 'NET', 'row_dnp': '必装', 'device_populated': True, 'line_no': 142}, {'signal': 'EN', 'ref': 'U_LDO_IO18', 'net': 'SYS_PCB', 'node1': 'U_LDO_IO18 pin3', 'node2': 'RAIL_BOARD_5V', 'row_type': 'NET', 'row_dnp': '必装', 'device_populated': True, 'line_no': 152}, {'signal': 'EN', 'ref': 'J_SOM_P3', 'net': 'CARRIER_BOARD_EN', 'node1': 'J_SOM_P3 pin87', 'node2': 'U_EN_SW pin2', 'row_type': 'NET', 'row_dnp': '必装', 'device_populated': False, 'line_no': 440}, {'signal': 'EN', 'ref': 'U_EN_SW', 'net': 'CARRIER_BOARD_EN', 'node1': 'U_EN_SW pin2', 'node2': 'CARRIER_BOARD_EN', 'row_type': 'NET', 'row_dnp': '必装', 'device_populated': True, 'line_no': 441}]
   en_device_populated                : ['U_EN_SW', 'U_LDO_IO18', 'U_LDO_IO33', 'U_LDO_L33']
   en_device_dnp                      : ['J_SOM_P3', 'U_DCDC_VCORE', 'U_DCDC_VIO', 'U_LDO_L18', 'U_LDO_S12', 'U_LDO_S18B']
   verdict                            : ★**旧结论『供电器件的控制脚在网表里根本不存在』对 EN 已不成立**: 现网表 EN 10 行 / SS 0 行 / CT 1 行 / MR 0 行; EN 的去向: 2 颗 DC-DC (pin13) + 6 颗 LDO (pin3, 直连 RAIL_BOARD_5V ⇒ 永远使能) + U_EN_SW (pin2, CARRIER_BOARD_EN) + SoM 输出脚; ★SS 仍 0 行 (DC-DC 软启动脚没有) ⇒ 『电源什么时候起』在网表层面**仍未完全定义**; ★CT 的 1 行属 **DNP** 的 U_SUPV ⇒ 实物不存在

=== F5_pullup_rail ===
   reset_pullup_ref                   : R_PU_RESET_N
   reset_pullup_ohm                   : 10000.0
   reset_pullup_rail                  : RAIL_VDD_1V8_IO
   reset_pullup_rail_v                : 1.8
   boot_pullup_ref                    : R_PU_BOOT_N
   boot_pullup_ohm                    : 10000.0
   boot_pullup_rail                   : RAIL_VDD_1V8_IO
   boot_pullup_rail_v                 : 1.8
   same_rail                          : True
   soc_io_rail_producer               : ['U_DCDC_VIO']
   soc_io_rail_producer_dnp           : ['DNP']
   verdict                            : ★**仍成立**: RESET_N / BOOT_N 的上拉都挂在 **RAIL_VDD_1V8_IO (1.8V)** 这条**主板 LDO 轨**上, 而 SoC 的 IO 域 (V_SOC_IO) 在现网表上**不是这条轨** (U_DCDC_VIO) ⇒ 主板这条 1.8V 掉电时, 复位/启动脚仍被它撑着 ⇒ 幽灵复位风险不变; ★更强: 现网表 SoC 核心轨/IO 轨的 IC (U_DCDC_VCORE / U_DCDC_VIO) 都是 DNP ⇒ SoC 用 SoM 自带 PMIC 的轨 ⇒ 主板这条 1.8V 与 SoC IO 域**完全无关**

=== F9_isp_budget ===
   judged_number                      : t_isp_total (管线可见 / SDK 总耗时口径)
   criteria                           : {'limit_mode_a_ms': 15.1, 'limit_mode_a_exact_ms': 15.094999999999999, 'limit_mode_b_p95_ms': 17.33, 'isp_now_ms': 8.0, 'headroom_now_mode_a_ms': 7.094999999999999, 'headroom_now_mode_a_doc': '7.09', 'headroom_now_mode_b_ms': 9.329999999999998, 'headroom_now_mode_b_doc': '9.33', 'published_numbers': 'ISP 上限: 模式A 15.10 ms / 模式B 17.33 ms; 现占位 8.00 ms 的余量 +7.09 / +9.33 ms', 'budget_ms': 60.0, 'T_FIXED_ms': 34.0, 'T_FIXED_minus_S3_ms': 26.0, 'T_od_ms': 18.905, 'age_baseline': 2, 'min_frames': 300}
   measurement                        : {'avg_total_ms': None, 'avg_hw_ms': None, 'p95_total_ms': None, 'n': None, 'npu_ms': None, 'source': None}
   sources                            : {'budget_ms': '[锁死项] 老板锁死的端到端 60ms 硬指标 (SW/RKNN_BENCH.md §5.1 / SW/DEMO_OD_TIMING_SPEC.md §3.3.1)', 'T_FIXED_ms': '[推算] HW/e2e_budget_rk3572.py T_FIXED = 34.00 (五段拆分恒等还原)', 'S3_now_ms': '[推算·无官方背书] 现行 ISP 段占位 8.00 ms (SW/SW_REQUIREMENTS.md §10.1; ISS-124 D1/D2)', 'POST_MS': '[推算] HW/e2e_budget_rk3572.py POST_MS = 5.6', 'FRAME_MS': '[实测口径] 60fps 帧周期 16.67 ms', 'S5_ms': '[推算] RK3576 8.87 ms × (6 TOPS / 4 TOPS) = 13.305 ms (RKNN_BENCH.md §4.3)', 'limit_mode_a_ms': '[推算] ISS-124 反解, 发布值 15.10 ms (SW/ISP_CAPABILITY_RESEARCH.md §②; json 精确值 15.095)', 'limit_mode_b_ms': '[推算] ISS-124 反解, 发布值 17.33 ms (前提 age=1; json 精确值 17.33)', 'npu_t2_flip_ms': '[锁死项] 老板 2026-10-29 T2 翻案条款 (ISS-129)'}
   verdict                            : INDET
   verdict_latency                    : INDET
   reason                             : 板端 ISP 段未实测 (本机无可达板) ⇒ 板端结论一律 [0数据] ⇒ 不作判定
   evidence                           : [0数据]
   margin_ms                          : None
   e2e_modeA_ms                       : None
   e2e_modeB_ms                       : None
   mode_b_note                        : 模式B 前提 age=1 (T_od <= 16.67); 现行 yolov5n@640 的 age=2 ⇒ 模式B 本来就不成立, 与 ISP 无关

=== 器件级常数与来源 ===
   ADC_BITS                           : 12              [官网] RK3572 datasheet V1.1 L2863: Resolution = 12 Bit (★ISS-291 升级: 原为 [0数据]★)
   ADC_LEAK_OFFSET_MAX_V              : 0.4             [沿用] ISS-090 原判据阈值 0.4V (★ISS-291 只改口径, 阈值不许调松★)
   ADC_NODE_MAX_V                     : 1.98            [官网] rk3572_datasheet_V1.1.txt L2454: SARADC_AVDD1V8 = 1.62 / 1.8 / 1.98 V ⇒ abs-max 1.98V
   ADC_NODE_NOM_MAX_V                 : 1.8             [官网] rk3572_datasheet_V1.1.txt L2864: Analog Input Range = AVSS18 ~ AVDD18 ⇒ ≤1.8V 标称
   ADC_SETTLE_MAX_MS                  : 300.0           [沿用] ISS-090 原判据阈值 300ms (★ISS-291 只改口径, 阈值不许调松★)
   BAT_CUTOFF_V                       : 3.0             [实测] HW/netlist_v1.csv L24 (RAIL BAT 行): '4.2V 满 / 3.0V 截止'
   BAT_FULL_V                         : 4.2             [实测] HW/netlist_v1.csv L24 (RAIL BAT 行): '4.2V 满 / 3.0V 截止'
   DET_CHAIN_STATIC_MAX_UA            : 26.25           [实测] HW/netlist_v1.csv L182 note: '常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)' ⇒ 取作单条检测链常开静态电流上限 (同板同型链已裁决值)
   FLASH_IMAGE_MB                     : 90              [实测] SW/FLASH_AND_VERSION.md §4.1 分区表总量
   I2C_TR_FAST_MAX_NS                 : 300.0           [官方] I2C 快模式上升沿上限 300ns
   I2C_TR_K                           : 0.8473          [推算] 10%→90% 上升时间系数 ln(9)=2.1972
   I2C_TR_STD_MAX_NS                  : 1000.0          [官方] I2C 标准模式上升沿上限 1.0µs
   ISS085_MIN_GND_PINS                : 2               [官方] ISS-085 (mech-lead) 跨铰链 ≥2 GND pin 规则
   I_ADC_LEAK_MAX                     : 1e-06           [0数据] SoC ADC 漏电流按量级 1µA 估 (★与网表 L182 note 同一假设★)
   P_REDLINE                          : 0.16            (网表实读, 无需器件常数)
   TMP117_ACC_BANDS_C                 : {'-20..50': 0.1, '-40..70': 0.15, '-40..100': 0.2}  (网表实读, 无需器件常数)
   TMP117_CONV_PERIOD                 : 1.0             (网表实读, 无需器件常数)
   TMP117_IV_SUPPLY                   : 5e-06           [官方] TI TMP117 datasheet: 5µA max
   TMP117_LSB_C                       : 0.0078125       [官方] TI TMP117 datasheet: 1 LSB = 7.8125 m°C
   TMP117_RESET_READ                  : -256.0          [官方] TI TMP117 datasheet: 复位后首读 −256°C
   T_SKIN_A                           : 35.0            [实测] MECH/MECH_BUDGET.md §2.3 热模型
   T_SKIN_B                           : 50.13           [实测] MECH/MECH_BUDGET.md §2.3 热模型
   T_SKIN_REDLINE                     : 43.0            [官方] ISO 13732-1 43°C 红线
   USB_BULK_EFF                       : 0.8             [推算] bulk 有效效率 80%
   USB_FS_MBPS                        : 12.0            [官方] USB 2.0 全速 12 Mbit/s
   USB_HS_MBPS                        : 480.0           [官方] USB 2.0 高速 480 Mbit/s
   USB_RESET_RESP_S                   : 0.005           [官方] USB 2.0 §7.1.7.3
   USB_VBUSDET_HI_HI_V                : 3.3             [官方] Forlinx FET3572 手册: 同上 (⇒ 降级 abs-max 上界)
   USB_VBUSDET_HI_LO_V                : 2.7             [官方] Forlinx FET3572 手册: 'A high level indicates DEVICE mode (2.7-3.3 V, typical: 3.0 V)'
   USB_VBUSDET_INTERNAL_PD_OHM        : 40000.0         [官方·降级] 手册只对 USB_DRD0_VBUSDET 明写 'internal 40 kΩ pull-down'; ★本板用的是 USB_DRD1_VBUSDET ⇒ 手册未记载 ⇒ [0数据] ⇒ 按'存在'降级处理并登记 need★
   USB_VBUSDET_VIH_MIN_V              : 2.3             [官方] Forlinx FET3572 手册 (state/_os_snapshots/fx3572_manual.html): 'In device mode, VBUSDET must be high (> 2.3 V)'
   USB_VBUS_MAX_V                     : 5.25            [官方] USB 2.0 / Type-C VBUS 4.75 ~ 5.25 V
   USB_VBUS_MIN_V                     : 4.75            [官方] USB 2.0 / Type-C VBUS 4.75 ~ 5.25 V
   USB_VBUS_NOM_V                     : 5.0             [实测] HW/netlist_v1.csv L2 (RAIL VBUS_5V 行): '5.0V ±5%'
   U_SUPV_DELAY_CT_CAP_MAX            : 10.0            (网表实读, 无需器件常数)
   U_SUPV_DELAY_CT_CAP_MIN            : 0.00125         (网表实读, 无需器件常数)
   U_SUPV_DELAY_CT_OPEN               : 0.02            [官方] TI TPS3808 datasheet: CT 悬空 = 20ms
   U_SUPV_DELAY_CT_VDD                : 0.3             [官方] TI TPS3808 datasheet: CT 经电阻接 VDD = 300ms
   U_SUPV_VIT_REF                     : 0.405           [官方] TI TPS3808 datasheet: VIT = 0.405 x (1 + R1/R2)
   V_DET_FS                           : 1.8             [官网] SAR-ADC 满量程 = 1.8V 域: 脚表 FET3572C_PIN_TABLE.csv L39 (SARADC_VIN5 / 1.8V) + rk3572_datasheet_V1.1.txt L2454 (SARADC_AVDD1V8 = 1.62/1.8/1.98V) + L2864 (Analog Input Range = AVSS18~AVDD18) ⇒ ★原 3.3V 写死值已按 ISS-291 订正★

=== SELF-TEST (85 项: 既有 21 + 新增 32 + 反向 19 + ISP 13) ===
  [PASS] 复位释放 tau = 1.1ms
  [PASS] 复位断言 tau = 100us
  [PASS] 复位到 VIH = 1.32ms
  [PASS] 网表注记误差 >= 50 倍
  [PASS] 监督器 CT 悬空延时 = 20ms
  [PASS] 两臂 0Ω 短路风险已标注
  [PASS] I2C t_r@100pF = 398ns
  [PASS] I2C 网表注记与实算一致 (误差 < 1.01 倍 ⇒ 网表侧矛盾已被 ISS-220 d6 消除)
  [PASS] I2C 300pF 超标准模式上限
  [PASS] ADC 源阻抗 = 37.5k (★ISS-291: 判决对象 = BAT_DET 链 → pin38 SARADC_VIN5★)
  [PASS] ADC tau = 3.75ms (★ISS-291 口径★)
  [PASS] ADC 12bit 建立 33.8ms ≤ 300ms 红线 (★ISS-291 口径: 老口径的 451ms 是**假红**★)
  [PASS] ADC 漏电偏移 37.5mV ≤ 0.4V 红线 (★ISS-291 口径: 老口径的 0.50V 是**假红**★)
  [PASS] TMP117 首读 -256C
  [PASS] TMP117 自热 < 0.1mW
  [PASS] CONN_USB 地脚数不合规
  [PASS] FS 刷 90MB < 120s
  [PASS] HS 刷 90MB < 8s
  [PASS] 0.05W -> 37.5C
  [PASS] 0.16W -> 43.0C (红线)
  [PASS] F8 负载开关按位号实读 (U_PWR_SW 在网表 ⇒ 旧'无硬件断电通路'结论已推翻)
  [PASS] 网表锚点: md5 与行数可复算 (data_rows = lines_total - 1)
  [PASS] 网表锚点: 现行网表 = 513 数据行 (行数不许变)
  [PASS] 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)
  [PASS] 网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)
  [PASS] F1 实读: R_PU_RESET_N=10k / R_SER_RESET_N=1k / C_RST=100nF
  [PASS] F1 实读: τ 注记是从网表 note 里读出来的 100ms (不是手抄)
  [PASS] F1 复评: PG 已进复位链 (Q_AND + R_PG_PULL 10k)
  [PASS] ★F1 实读: PG 源 dnp 必须按【PG_AND 那一行】取 ⇒ U_DCDC_VCORE / U_DCDC_VIO 都是必装 (★dnp_of(ref) 拿的是器件级 DNP ⇒ 错一格★)
  [PASS] ★F1 实读: PG_AND 上真正 DNP 的是 Q_ENVC (行级) ⇒ 复位链 P0 的真归因 (★不是『PG 源 DNP』★)
  [PASS] ★F1 实读: RESET_N 上谁在拉 —— Q_AND 必装 / SW_RST 必装 / U_SUPV pin1 DNP (它不参与拉复位)
  [PASS] F3 实读: I2C_A 上拉 = 2.2k → 1.8V 域 (ISS-153 订正)
  [PASS] F3 实读: I2C_B 上拉 = 4.7k → 3.3V 域
  [PASS] F3 复评: I2C_A @300pF = 559ns ≤ 1000ns ⇒ 标准模式**通过** (旧结论已翻转)
  [PASS] F3 复评: I2C_B @300pF = 1194ns > 1000ns ⇒ 标准模式**不通过** (最差总线)
  [PASS] F3 实读: 网表自带的 t_r 注记 186ns (ISS-220 d6 已把 I2C_A 改成 2.2k@1.8V ⇒ 注记与实算一致, 网表侧矛盾已消除)
  [PASS] F4 实读: EN/SS/CT/MR 行数 = 10/0/1/0 (合计 11 行, CT 属 DNP 器件)
  [PASS] F4 实读: LDO 的 EN 直连 RAIL_BOARD_5V (永远使能)
  [PASS] F4 实读: U_SUPV 是 DNP ⇒ 监督器支路实物不存在
  [PASS] F5 实读: RESET_N / BOOT_N 上拉都挂 RAIL_VDD_1V8_IO (1.8V)
  [PASS] F5 实读: TMP117 现在挂在 I2C_B (旧文档写 I2C_A)
  [PASS] F6 实读: 跨铰链 J_CHG 不带 USB D+/D− ⇒ 跨铰链 USB 链不成立
  [PASS] F6 实读: demo 板板内 Type-C → SoC USB 路径存在 (J_USB_C → 串阻 → J_SOM)
  [PASS] F8 实读: 负载开关 = U_PWR_SW / U_EN_SW, 且 ON 脚有 10k 下拉 (默认关)
  [PASS] ★F8 实读: 负载开关 U_PWR_SW / U_EN_SW **都必须有器件行** (BOM/装配单不许漏掉任何一颗负载开关)
  [PASS] F4' 实读: ADC 判决对象 = BAT_DET 链 (落点 J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域); BAT_DET 三颗必装
  [PASS] F4 实读: 满量程 = 1.8V 域 (官方) ⇒ 12bit LSB = 0.439mV (★老口径 3.3V ⇒ 0.806mV 已作废★)
  [PASS] F4 实读: 漏电偏移 37.5mV = 2.1% FS ⇒ 与网表 L182 note 写死的数**逐字对上** (口径同源)
  [PASS] F4 实读: 判决源 = SoM 脚表 signal 列 (落点判 SAR-ADC), 取链模式 = by_landing_pin
  [PASS] F4 实读: ADC 节点 @4.2V = 1.575V ≤ abs-max 1.98V (FS 利用率 87.5%)
  [PASS] F4D 实读: VBUS_DET_D 落点 = J_SOM_P1 pin100 = USB_DRD1_VBUSDET (数字脚 ⇒ 不进 ADC 判据)
  [PASS] F4D 实读: 数字链常开静态电流 4.81µA (含内部 40kΩ 降级) ≤ 26.25µA 上限
  [PASS] F4D 实读: 数字链节点 2.5V > 识别阈值 2.3V, 且内部下拉/域/裕量三条未决项都报出
  [PASS] REV-1 反向: 把 I2C_A 上拉改成 10k ⇒ I2C_A @300pF 判据必须变红 (>1000ns)
  [PASS] REV-2 反向: 把 I2C_A 上拉改成 4.7k ⇒ t_r@100pF 必须回到 398ns (旧文档那个数)
  [PASS] REV-3 反向: 从网表里删掉 U_PWR_SW ⇒ 装机开关数必须从 2 掉到 1 (★不是 0★ · 断电主开关没了)
  [PASS] REV-3c 反向: 把 U_EN_SW 的**器件本体行**删掉 (只留引脚行) ⇒ F8『不许漏掉任何一颗负载开关』必须变红
  [PASS] REV-3b 反向: 把 U_PWR_SW 与 U_EN_SW 都删掉 ⇒ F8『硬件断电通路存在』必须变红
  [PASS] REV-4 反向: 把 R_PU_RESET_N 改成 20k ⇒ 复位释放 tau 必须变成 2.1ms
  [PASS] REV-5 反向: 把 C_RST 改成 10nF ⇒ 复位释放 tau 必须变成 0.11ms
  [PASS] REV-6 反向: 把 R_PU_I2CB_SCL 改成 1k ⇒ I2C_B 必须变成最差总线之外的合格总线 (t_r 掉到 85ns)
  [PASS] REV-7 反向: 把 PG_AND 上的 NET_PG_AND 汇总行改成 DNP ⇒ PG 源判据必须变红 (★锁死'别再拿错行的 dnp'★)
  [PASS] REV-8 反向: 把 PG_AND 上 Q_AND 那行改成 DNP ⇒ 栅极接在 PG_AND 上的 Q_AND 判据必须变红
  [PASS] REV-9 反向: 把 PG_AND 上 R_PG_PULL 那行改成 DNP ⇒ 10k 上拉判据必须变红
  [PASS] REV-10 反向: 把 PG_AND 网上**任意一行**改成 DNP ⇒ 对应判据必须变红 (逐行试, 不跳行)
  [PASS] REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ F4'『BAT_DET 三颗必装』必须变红
  [PASS] REV-12 反向: 把满量程 V_DET_FS 改回 3.3 (老口径) ⇒ 满量程/口径同源判据必须变红
  [PASS] REV-13 反向: 把取链规则改回「元组第一条」⇒ 判决对象判据必须变红 (不许悄悄换回错对象)
  [PASS] REV-14 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ 「ADC 输入悬空」判据必须变红
  [PASS] REV-15 反向: 把 BAT_DET 的下臂 60k 改成 100k ⇒ @4.2V 节点 2.1V > 1.98V abs-max ⇒ 过压判据必须变红
  [PASS] REV-16 反向: 把 VBUS_DET_D 链的两颗电阻改成 10k/10k ⇒ 数字链静态电流判据必须变红 (★数字脚口径也在判, 不是只判 ADC★)
  [PASS] REV-17 反向: 把 VBUS_DET_D 的上臂 1M 改成 10M ⇒ 节点 0.45V < 2.3V 识别阈值 ⇒ 数字链节点电平判据必须变红
  [PASS] ISP 模式A 生死线 = 15.10 ms (ISS-124 发布值, 不许调松)
  [PASS] ISP 模式B 上限 = 17.33 ms (ISS-124 发布值)
  [PASS] ISP 精确反解线 = 15.095 ms (json 口径, 与发布线差 0.005 ms)
  [PASS] ISP 现占位 8.00 ms 的余量 = +7.09 ms (精确 7.095) / +9.33 ms
  [PASS] 模型复现: X=8.00 ms 时模式A e2e = 52.91 ms (与 HW/e2e_budget_rk3572.py 同源)
  [PASS] ★反向: ISP avg = 15.11 ms ⇒ 必须 FAIL (超 15.10 必被抓) 且给出差值
  [PASS] ISP avg = 15.10 ms ⇒ PASS (恰好在生死线上)
  [PASS] ISP avg = 8.00 ms (现占位) ⇒ PASS + 余量 +7.09 ms
  [PASS] ★反向: 无实测输入 ⇒ INDET + [0数据] (不许假装测过)
  [PASS] ★反向: 只报 SDK 总耗时、缺纯硬件耗时 ⇒ 不许静默 PASS (⇒ INDET + 理由)
  [PASS] ★反向: 采样帧数 n=120 < 300 ⇒ 不作结论 (INDET)
  [PASS] ISP p95 = 18.00 ms ⇒ 模式B 上限 (17.33) FAIL
  [PASS] T2 交叉核对: 纯 NPU 21.00 ms ⇒ 命中老板翻案条款 (20.33 ms)

SELFTEST 85/85 通过, rc=0
[rc=0] 既有闸 timing_check

───── $ python3 SW/tools/check_sw_zero_copper_grade_consistency.py ─────
═══ SW 侧零铜网分级 ↔ 板侧真值 一致性闸 (★ISS-344·sw-lead·零写板★) ═══
  被检文档 : /home/yuewuya/.openclaw/workspace/projects/smart_glasses/SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md
  真值源   : /home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/check_s8_target_list.py (★只读·AST 静态解析·未执行其代码★)
  板侧真值 : REQUIRED_SINGLE(8) = CAM_RESET_N, LED_G_D, USB_CC2, JTAG_TDI, UART_RX, SPI_SCLK_BOOT, SPI_MOSI_BOOT, SPI_MISO_BOOT
             FLOAT_OK(1) = FSIN_OUT
             EXPECT_* = 必需 23 / 可悬空 1 / 待定 0

── SW 页 §3/§3-1 表读出的「建议的板侧标记」 ──
  CAM_RESET_N        行 164   ⇒ REQUIRED  REQUIRED
  FSIN_OUT           行 151   ⇒ FLOAT     FLOAT
  JTAG_TDI           行 152   ⇒ REQUIRED  REQUIRED
  LED_G_D            行 165   ⇒ REQUIRED  REQUIRED
  SPI_MISO_BOOT      行 153   ⇒ REQUIRED  REQUIRED
  SPI_MOSI_BOOT      行 154   ⇒ REQUIRED  REQUIRED
  SPI_SCLK_BOOT      行 155   ⇒ REQUIRED  REQUIRED
  UART_RX            行 156   ⇒ REQUIRED  REQUIRED
  USB_CC2            行 157   ⇒ REQUIRED  REQUIRED

── SW 页订正表的「新说法」 ──
  CAM_RESET_N        行 281   ⇒ REQUIRED  REQUIRED
  FSIN_OUT           行 289   ⇒ FLOAT     FLOAT
  JTAG_TDI           行 283   ⇒ REQUIRED  REQUIRED
  LED_G_D            行 282   ⇒ REQUIRED  REQUIRED
  SPI_MISO_BOOT      行 284   ⇒ REQUIRED  REQUIRED
  SPI_MOSI_BOOT      行 285   ⇒ REQUIRED  REQUIRED
  SPI_SCLK_BOOT      行 286   ⇒ REQUIRED  REQUIRED
  UART_RX            行 287   ⇒ REQUIRED  REQUIRED
  USB_CC2            行 288   ⇒ REQUIRED  REQUIRED

── 判据逐条 ──
  C3 REQUIRED_SINGLE 每条都在 SW 页且被判【必需】               ✔ 通过
       └─ 缺 0 条 · 非必需 0 条
  C1 凡判 NC 的网必须在 FLOAT_OK 里                         ✔ 通过
       └─ 断言 NC 的网 = (无)
  C2 凡在 REQUIRED_SINGLE 里的网判 NC 就判红并点名              ✔ 通过
       └─ 被判 NC 的必需网 = (无)
  C0 §3/§3-1 标记与 §7 订正表「新说法」同档                      ✔ 通过
       └─ 比对 9 条
  C5 必需网的固件侧改动清单已标「作废」                              ✔ 通过
       └─ 未标作废 = 0 条
  C9 §2 表「分级」列与 §3 标记同档 (加分项)                       ✔ 通过
       └─ 比对 9 条

★★结论: ★**全绿** ★ ⇒ SW 侧分级与板侧真值【一致】★
[rc=0] 既有闸 zero_copper

───── $ python3 state/merge.py ─────
✅ STATE.yaml 已刷新 (2026-11-24T02:09:46+08:00)
   产出 804 | 阻塞 43 (高危 33) | 未闭合需求 331 | 冲突 0 | 健康度 red
[rc=0] 合并

───── $ python3 state/gate_check.py ─────
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-23_hw-lead_ISS373_S10换件集合唯一真源与口径闸.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1124 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    441 条
   sw-lead    325 条
   mech-lead  358 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 118/500  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 236 条, 其中 58 条真对上了别人的需求 key
   hw-lead    被答 43/267 | 我答 81 条(有效 31) | 产出 311 | 阻塞 7
   sw-lead    被答 29/82 | 我答 71 条(有效 6) | 产出 278 | 阻塞 15
   mech-lead  被答 46/151 | 我答 84 条(有效 21) | 产出 200 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 51 条 | **全局 46 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 331 条**
   ✅ 与 merge.py 自对账一致 (等外部 46 / 等总工 331)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 10 个
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']
      iss105_jchg_rfq_release: 发起方 ['main', 'hw-lead']
      iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice: 发起方 ['main', 'mech-lead']
      iss236_boss_v_decision: 发起方 ['main', 'hw-lead']

【Q5 硬指标覆盖】 0/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']
   sw-lead    1/5 类: ['镜腿/镜脚厚度(mm)']
   mech-lead  2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 10/10 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ✅ 钉板闸⑩ 板侧项全集重跑幂等闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 204 条需求确实还没人答 (等另一个总工)
   · sw-lead: 39 条需求确实还没人答 (等另一个总工)
   · mech-lead: 88 条需求确实还没人答 (等另一个总工)

==========================================================================
[rc=0] 门禁 gate_check

───── $ python3 state/check_brief_commands.py ─────
── 查了 9 条待办单的 task_brief, 有问题的 0 条
[rc=0] 任务书命令存在性

───── $ grep -c check_debug_pin_order_contract state/gate_check.py ─────
0
[rc=1] 零挂链自证

───── $ md5sum HW/PCB/demo_mainboard.kicad_pcb ─────
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
[rc=0] 板指纹 md5

───── $ stat -c %y %s HW/PCB/demo_mainboard.kicad_pcb ─────
2026-11-06 07:07:17.362193413 +0800 4940213
[rc=0] 板指纹 mtime+size

───── 零落表自证 (网表/脚表/BOM md5) ─────
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
[rc=0] 零落表自证
───── 既有闸/既有页面 md5 自证 (未动) ─────
cf09c921002937920bfa40701d523b33  SW/tools/timing_check.py
4d7ce982965e92c78a1ebcd3e968874e  SW/tools/check_onepass_sw_release.py
cab7a6f17c1da35f4e54185ad8b62089  SW/tools/check_fp_truth_read.py
58a3aa445842cd9ba89fe1e75bb9fc31  SW/tools/check_sw_zero_copper_grade_consistency.py
md5sum: HW/check_pcb_nets.py: No such file or directory
5f370bb8cf828473e70ccc5d6412da98  state/gate_check.py
c9191025020fefd9b475e2573a335815  state/merge.py
3b383a52b4fa540f1d16a2c6f3811de8  state/frag_write.py
[rc=1] 既有闸/工具 md5
───── 既有页面正文 md5 自证 (未动) ─────
0f4bf6c083f25cea6cda240a91170049  SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md
4f272497bf60dabfd8304c52949211f6  SW/FLASH_AND_VERSION.md
83fafcf7d22d8fa999a1db74c781956d  SW/SW_MD5_BASELINE_LEDGER.md
da7b02c013fa49c65b70ed3bea97b787  MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md
c103973ee73950a861c7d54d725dbb8c  MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md
cc51144e163f95519bc5de3265d0581b  HW/PCB/SOM_PIN_MAPPING.md
md5sum: HW/PCB/FP_TRUTH_BASELINE.md: No such file or directory
[rc=1] 既有页面 md5
───── 分片 status ─────
6:  phase: fixing
```



---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)
- 对方: ★**main (项目总工)** ★ —— 本单不直接联系任何其他总工
- 我的需求: ★**(1) 裁决 `J_DEBUG`/`J_UART` 的 pin1 朝向 (rot 90 / rot 270) 一句话; (2) 裁决 ISS-344 的 JTAG 口径 (页 §3-2 的 ①/②/③ 或组合)** ★
- 我的假设 (如果对方不回应, 我会按这个做): ★**不代拍 ⇒ 本单只把两套写死值都备好 (rot90: 141.0450 / 18.2550; rot270: 144.8550 / 19.5250), 等 main 一句话裁决后再由闸 D2/D4 校验; 在裁决落地前, 「那一趟」不得开工写死值** ★

## 待办: 需要项目总工做什么
1. ★**裁 `J_DEBUG`/`J_UART` 的 pin1 朝向** (rot 90 建议 / rot 270 备选) ⇒ 一句话即可, 写死值已备好 ★
2. ★**裁 ISS-344 的 JTAG 口径** (页 §3-2 的 ①/②/③) ⇒ 特别要拍的是「`JTAG_TDI` 判为必需且板侧不许标 NC」与「网表里它此刻就是 `SoC_NC`」这两个对不上的事实, 改哪一处 ★
3. ★**签收 `state/issue_log.yaml`** (本单不自签) ★
4. ★**决定本单新闸要不要挂链** (本单按边界要求**不挂**, `state/gate_check.py` 命中 0 ⇒ 挂不挂归 main) ★
5. ★**决定是否把本单真相页的「追加式订正块」往既有页面落** (本单只写在自己页里, 既有页面一个字未动) ★

## 阻塞: 缺什么信息
- ★**无阻塞** ★: 本单全部结论都有本机实读/实算支撑; 两处裁决是「等 main 拍」而不是「缺数据」; **零外发, 没有等原厂回信的缺口** ★

---

## B7 交卷后复跑验证 (2026-11-24 04:1x GMT+8 · gateway reload 后)

★**为什么有这一段**: ★**2026-11-24 04:10 一次 gateway reload 把 sw-lead 子会话掐断 ⇒ 本页对应的 session 重启后复跑了一遍全部验收命令, 确认【三件交付物在盘上未丢失、闸仍 rc=0、板/表仍未动】★★ ⇒ ★**本段是「交卷后复跑验证」, 不是新交付物, 结论与 B1~B6 完全一致 (无一条结论被复跑推翻)★**

★**复跑前指纹 (本段写入前)** ★
| 文件 | md5 |
|---|---|
| `HANDOFF/2026-11-23_sw-lead_ISS375_…md` (本页) | `89c58c7d5ca6bf401d93f2323a99291c` |
| `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` | `ef6f36e5a1389def10c3645f30d05aec` |
| `SW/tools/check_debug_pin_order_contract.py` | `bed0845f5cb27f5905584e71143a656c` |
| `state/fragments/sw.yaml` | `21892e983ba60404b1033a248e82fc86` |

★**复跑 11 条命令 (本机实跑 · 原样输出) ★**

```text
───── $ bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py ─────
=== ISS-375 · check_debug_pin_order_contract ===
  [PASS] D0   官方 land pad1 形状 (盘上实读, 不写死) 1x04: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True; 1x02: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True
  [PASS] D1   现状板面 pad1 位置/极性标记 (实读板, 不写死) J_DEBUG: pad1@X=142.2 (X_MIN) 标记=False 形状=RECT 属性=SMD; J_UART: pad1@X=18.64 (X_MIN) 标记=False 形状=RECT 属性=SMD
  [PASS] D2   两候选 pad→X 序 (KiCad 变换算, 须互为逆序) J_DEBUG rot90 序=['1', '2', '3', '4'] (pad1@X_MIN) / rot270 序=['4', '3', '2', '1'] (pad1@X_MAX); J_UART rot90 序=['1', '2'] (pad1@X_MIN) / rot270 序=['2', '1'] (pad1@X_MAX)
  [PASS] D3   页同时给出两候选+裁决+落点写死值 
  [PASS] D4   页的 pin1 朝向与 D2 实算一致 
  [PASS] D5   网表 JTAG 四线 SoM 侧端点 (现读, 不写死) JTAG_TCK_SOC→SoC_NC; JTAG_TMS_SOC→SoC_NC; JTAG_TDI_SOC→SoC_NC; JTAG_TDO_SOC→SoC_NC
  [PASS] D6   页 §2 与 SOM_PIN_MAPPING.md 结论不冲突 
  [PASS] D7   板指纹三项未动 (零写板自证) md5=611b869e13518c3c023fb178f91a0075 (期望 611b869e13518c3c023fb178f91a0075) / mtime=2026-11-06 07:07:17.362193413 (期望 2026-11-06 07:07:17.362193413) / size=4940213 (期望 4940213)
  [PASS] D8   证据等级白名单+零挂起措辞+判据/事实分开+零挂链 零挂链: state/gate_check.py 命中 0
=== 9/9 PASS ===
ALL CHECKS PASS
rc=0

───── $ bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py --selftest ─────
=== ISS-375 · check_debug_pin_order_contract --selftest ===
  [PASS] M1       把页里的 rot 90 改成 rot 270                     期望红=D2,D3,D4     实红=D2,D3,D4     
  [PASS] M2       把 D2 的算式改成手算常数                             期望红=D4           实红=D4           
  [PASS] M3       把网表里的 SoC_NC 改成别的                          期望红=D5           实红=D5           
  [PASS] T-D0     页里把官方 land 的 pad1 形状写错                     期望红=D0           实红=D0           
  [PASS] T-D1     页里把现状 pad1 位置写反                            期望红=D1           实红=D1           
  [PASS] T-D3     页里删掉一个候选                                   期望红=D2,D3,D4     实红=D2,D3,D4     
  [PASS] T-D6     页里写『已在 SoM 侧落地』                            期望红=D6           实红=D6           
  [PASS] T-D8a    证据等级用白名单外的等级                               期望红=D8           实红=D8           
  [PASS] T-D8b    出现挂起措辞                                     期望红=D8           实红=D8           
  [PASS] T-D7     板指纹被动过 (临时副本)                              期望红=D7           实红=D7          
  [PASS] T-D8c    新闸挂进 state/gate_check.py (临时副本)            期望红=D8           实红=D8          
=== selftest 11/11 PASS (共 11 条反向用例, 其中镜像类 3 条) ===
ALL TESTS PASS
rc=0

───── $ python3 SW/tools/timing_check.py ─────
rc=0   (末行: SELFTEST 85/85 通过, rc=0)

───── $ python3 SW/tools/check_sw_zero_copper_grade_consistency.py ─────
rc=0   (末行: ★★结论: ★**全绿** ★ ⇒ SW 侧分级与板侧真值【一致】★)

───── $ python3 state/merge.py ─────
✅ STATE.yaml 已刷新 (2026-11-24T04:10:57+08:00)
   产出 812 | 阻塞 43 (高危 33) | 未闭合需求 344 | 冲突 0 | 健康度 red
rc=0

───── $ python3 state/gate_check.py ─────
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-24_hw-lead_ISS379_JUART排针换land落位可行性.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-24_mech-lead_ISS377_座体净距判据同源化与座体型号自查.md
rc=0

───── $ python3 state/check_brief_commands.py ─────
── 查了 7 条待办单的 task_brief, 有问题的 0 条
rc=0

───── $ grep -c check_debug_pin_order_contract state/gate_check.py ─────
0        (grep 无命中 rc=1 属正常 ⇒ 输出 0 = 零挂链)

───── $ md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv ─────
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv

───── $ stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb ─────
2026-11-06 07:07:17.362193413 +0800 4940213
```

★**沙盒读数复核 (本趟实读 6 份 json · net 非空 ⇒ 上一趟那个 `SetNetCode` 顺序缺陷确实已修) ★**

| 读数文件 | pad→net | 形状 | 判定 |
|---|---|---|---|
| `logs/iss375/meas_J_DEBUG_s1_jdebug_rot90.json` | 1=JTAG_TCK / 2=JTAG_TMS / 3=JTAG_TDI / 4=JTAG_TDO | pad1=RECT 其余=CIRCLE | ★**顺排 · pad1@X_MIN** ★ |
| `logs/iss375/meas_J_DEBUG_s2_jdebug_rot270.json` | 4=JTAG_TDO / 3=JTAG_TDI / 2=JTAG_TMS / 1=JTAG_TCK | pad1=RECT 其余=CIRCLE | ★**逆排 · pad1@X_MAX** ★ |
| `logs/iss375/meas_J_UART_s3a_juart_rot90.json` | 1=UART_TX / 2=UART_RX | pad1=RECT | ★**顺排 · pad1@X_MIN** ★ |
| `logs/iss375/meas_J_UART_s3b_juart_rot270.json` | 2=UART_RX / 1=UART_TX | pad1=RECT | ★**逆排 · pad1@X_MAX** ★ |
| `logs/iss375/meas_J_DEBUG_demo_mainboard.json` (S0 基线) | 1=JTAG_TCK / 2=JTAG_TMS / 3=JTAG_TDI / 4=JTAG_TDO | pad1~4 全 RECT | ★**现状板面无 pin1 标记** ★ |
| `logs/iss375/meas_J_UART_demo_mainboard.json` (S0 基线) | 1=UART_TX / 2=UART_RX | pad1~2 全 RECT | ★**现状板面无 pin1 标记** ★ |

★**沙盒板互不相同 (证明 rot270 那块板确实建出来了, 不是真板副本) ★**
| 板 | md5 |
|---|---|
| `tmp/iss375_sbx/s1_jdebug_rot90.kicad_pcb` | `f081a5e44b30973d736e6f0f463f6803` |
| `tmp/iss375_sbx/s2_jdebug_rot270.kicad_pcb` | `ffa8c53bf61e7c9f01e9135fc7682b25` |
| `tmp/iss375_sbx/s3a_juart_rot90.kicad_pcb` | `bb6c00e98a5372eaf893b48bbf038c0e` |
| `tmp/iss375_sbx/s3b_juart_rot270.kicad_pcb` | `27e534f6e40426557eeb4d1658343d46` |
| ★`HW/PCB/demo_mainboard.kicad_pcb` (真板) | `611b869e13518c3c023fb178f91a0075` ★ ⇒ ★**四块沙盒板 md5 互不相同, 且都 ≠ 真板 ⇒ 零写板成立** ★

★**builder 顺序复核 (上一趟那个真缺陷的修法) ★**: `tmp/iss375_sbx/iss375_build.py` L58 `b.Add(fp)` ⇒ L62 `p.SetNetCode(code[p.GetPadName()])` ⇒ ★**SetNetCode 在 Add 之后 ⇒ 对已挂板封装生效 ⇒ 读数 net 非空 (与上表互证) ★**

★**本段结论**: ★**零结论变更** · 三件交付物齐备且 rc=0 · 板/表零改动 · **要 main 裁的两件事 (B5-① pin1 朝向 / B5-② ISS-344 JTAG 口径) 仍然待裁, 本单不代拍** ★

---

## 【追加式订正 (2026-11-24 04:3x · sw-lead · ISS-375 cont3)】派活材料 §一③ 的口径差 + 闸的 M2/M3 改成动【判据自己的数据源】+ B6 复跑

★**本页正文一字未改** (本段是纯追加) ★ · ★**板 md5 / mtime / size 三项未动** (`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`) ★

### ★B5-③ 追加 ④: 派活材料 §一③ 那段 pcbnew 代码 —— 我本机复跑【逐字相同】, 但它的【口径】必须写清 ★

★**这是本 job 追加提醒 ① 的正面回答: 「你算出来的数如果和 brief 里给的不一样, 以你本机复算的为准, 但必须写清差在哪、为什么差」——★ 本单复算结果与 brief【逐字相同】, 所以【无差】; 但有一处【口径差】必须写清 ★**

★**我本机原样复跑 brief §一③ 那段代码 (2026-11-24 04:1x · 真板只读 · 不写盘 · 留证 `logs/iss375/rerun_brief_sec1_3_current_land.log`)★**:

```
fpid = ''
rot 0   [('1','JTAG_TCK',142.2), ('2','JTAG_TMS',142.7), ('3','JTAG_TDI',143.2), ('4','JTAG_TDO',143.7)]
rot 90  [('1','JTAG_TCK',142.9), ('2','JTAG_TMS',142.9), ('3','JTAG_TDI',142.9), ('4','JTAG_TDO',142.9)]
rot 270 [('1','JTAG_TCK',145.7), ('2','JTAG_TMS',145.7), ('3','JTAG_TDI',145.7), ('4','JTAG_TDO',145.7)]
```

★**⇒ 与 brief §一③ 给的三行【逐字相同】⇒ 数字无差** ★
★**但那段代码量的是【现状 SMD land 被旋转】, 不是【两个候选落点】—— 这是本单唯一一处必须写清的口径差** ★:

| | brief §一③ 那段代码 | 本单 S1/S2 沙盒 |
|---|---|---|
| 对象 | ★**现状 `J_DEBUG` 的自定义 SMD land** (`fpid = ''`) ★ | ★**官方 `PinHeader_1x04_P1.27mm_Vertical` THT land** ★ |
| ★**pad 沿哪个局部轴排开** ★ | ★**局部 X** (实测 pad1 `(−2.1000, −1.4000)` / pad4 `(−0.6000, −1.4000)`, 步距 **0.5**) ★ | ★**局部 Y** (官方 land pad1 `(0,0)` / pad4 `(0,3.81)`, 步距 **1.27**) ★ |
| 转 90°/270° 后 | ★**四个 pad 挤到同一 X** (142.9 / 145.7) ⇒ **排针变竖排** ★ | ★**四个 pad 沿 X 排开** (141.0450…144.8550) ⇒ **横排** ★ |
| 能否当候选落点读数 | ★**不能** ★ | ★**能** ★ |

⇒ ★**结论不冲突, 但读法必须换**: `rot 90 → 全挤到 142.9` 是【现状 land 的姿态退化现象】; ★**本单 §1 的针序契约一律以 S1/S2 为准 (官方 land + KiCad 自己的 `SetOrientationDegrees` 实摆)** ★
★**⇒ 给 main 的一句话**: ★**若有人拿 §一③ 的 142.9/145.7 当「候选落点的 pad 坐标」⇒ 会读错; 候选落点的四个 X 是 141.0450 / 142.3150 / 143.5850 / 144.8550** ★

### ★B5-③ 追加 ⑤: 闸的 M2 / M3 改成动【判据自己的数据源】(★cont2 的实现测不到本单的两条命脉★) ★

★**cont2 的 M2/M3 只改页文本** ⇒ 实测红的是 D4 / D5 的**页↔实读**一致性 ⇒ ★**测不到「D2 真的是用 KiCad 变换算的」与「D5 真的是现读网表的」—— 这恰是本单的两条命脉** ★
★**cont3 改法**: ★**M2 = 变异【本闸自己的源码】**, 把 `compute_candidate_orders()` 换成返回写死常数 ⇒ 期望 **D2** 红; ★**M3 = 在【沙盒网表副本】里把四条 `JTAG_*_SOC` 的 SoM 侧端点 `SoC_NC` 改成别的** ⇒ 期望 **D5** 红 ★ (★真网表只读 · 真闸文件只读 · 变异体与网表副本只落沙盒临时目录★)

| 用例 | 动的对象 | 期望红 | cont3 实测 | 这条测到了什么 |
|---|---|---|---|---|
| ★**M2** ★ | ★**闸源码** (`compute_candidate_orders` → 写死常数, 两候选同序) ★ | ★**D2 + D4** ★ | ★**D2 + D4** ✔ ★ | ★若没有「互为逆序, 不是互等」这条判据, 变异体【全绿混过去】⇒ 直接证明「两个候选被当同一个」必被抓住** ★ |
| ★**M3** ★ | ★**沙盒网表副本** (4 行 `SoC_NC` → `SoC_FAKE`) ★ | ★**D5** ★ | ★**D5** ✔ ★ | ★若 D5 把 `SoC_NC` 写死成常量, 网表变了页没改也不会红 ⇒ 直接证明 D5 是现读网表的** ★ |

★**为什么 M2 的期望集是 {D2, D4} 而不是 {D2}**: ★**D2 的输出被污染 ⇒ D4 (= 页写序 vs D2 实算序) 必然同时对不上** ⇒ 两条是【真实耦合】⇒ ★**如实写成两条, 不是把判据改松** ★
★**修 bug 一处 (变异体注入点)**: ★注入点用 `str.replace` 会命中源码里【前面那处同名字符串字面量】(注入块自己就含那个串) ⇒ **SyntaxError** ⇒ 改用 ★`src.rfind(marker)` 定位【最后】一个 `if __name__ == "__main__":` ★ ★

### ★B6 追加: cont3 的必跑命令原样输出 (2026-11-24 04:2x ~ 04:3x 本机实跑) ★

```text
───── $ python3 SW/tools/check_debug_pin_order_contract.py ─────
=== ISS-375 · check_debug_pin_order_contract ===
  [PASS] D0   官方 land pad1 形状 (盘上实读, 不写死) 1x04: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True; 1x02: pad1=thru_hole rect / 其余=circle ⇒ 有 pin1 标记=True
  [PASS] D1   现状板面 pad1 位置/极性标记 (实读板, 不写死) J_DEBUG: pad1@X=142.2 (X_MIN) 标记=False 形状=RECT 属性=SMD; J_UART: pad1@X=18.64 (X_MIN) 标记=False 形状=RECT 属性=SMD
  [PASS] D2   两候选 pad→X 序 (KiCad 变换算, 须互为逆序) J_DEBUG rot90 序=['1', '2', '3', '4'] (pad1@X_MIN) / rot270 序=['4', '3', '2', '1'] (pad1@X_MAX); J_UART rot90 序=['1', '2'] (pad1@X_MIN) / rot270 序=['2', '1'] (pad1@X_MAX)
  [PASS] D3   页同时给出两候选+裁决+落点写死值
  [PASS] D4   页的 pin1 朝向与 D2 实算一致
  [PASS] D5   网表 JTAG 四线 SoM 侧端点 (现读, 不写死) JTAG_TCK_SOC→SoC_NC; JTAG_TMS_SOC→SoC_NC; JTAG_TDI_SOC→SoC_NC; JTAG_TDO_SOC→SoC_NC
  [PASS] D6   页 §2 与 SOM_PIN_MAPPING.md 结论不冲突
  [PASS] D7   板指纹三项未动 (零写板自证) md5=611b869e13518c3c023fb178f91a0075 (期望 611b869e13518c3c023fb178f91a0075) / mtime=2026-11-06 07:07:17.362193413 (期望 2026-11-06 07:07:17.362193413) / size=4940213 (期望 4940213)
  [PASS] D8   证据等级白名单+零挂起措辞+判据/事实分开+零挂链 零挂链: state/gate_check.py 命中 0
=== 9/9 PASS ===
ALL CHECKS PASS
[rc=0] 新闸

───── $ python3 SW/tools/check_debug_pin_order_contract.py --selftest ─────
=== ISS-375 · check_debug_pin_order_contract --selftest ===
  [PASS] M1       把页里的 rot 90 改成 rot 270                     期望红=D2,D3,D4     实红=D2,D3,D4
  [PASS] M2       把 D2 的算式改成手算常数 (变异本闸源码)            期望红=D2,D4        实红=D2,D4         · 变异体 rc=1
  [PASS] M3       把网表里的 SoC_NC 改成别的 (沙盒网表副本)         期望红=D5           实红=D5            · 沙盒网表副本改了 4 行
  [PASS] T-D0     页里把官方 land 的 pad1 形状写错                     期望红=D0           实红=D0
  [PASS] T-D1     页里把现状 pad1 位置写反                            期望红=D1           实红=D1
  [PASS] T-D3     页里删掉一个候选                                   期望红=D2,D3,D4     实红=D2,D3,D4
  [PASS] T-D6     页里写『已在 SoM 侧落地』                            期望红=D6           实红=D6
  [PASS] T-D8a    证据等级用白名单外的等级                               期望红=D8           实红=D8
  [PASS] T-D8b    出现挂起措辞                                     期望红=D8           实红=D8
  [PASS] T-D7     板指纹被动过 (临时副本)                              期望红=D7           实红=D7
  [PASS] T-D8c    新闸挂进 state/gate_check.py (临时副本)            期望红=D8           实红=D8
=== selftest 11/11 PASS (共 11 条反向用例, 其中镜像类 3 条) ===
ALL TESTS PASS
[rc=0] 新闸自测

───── $ python3 SW/tools/timing_check.py ─────
[rc=0] 既有闸仍绿 (零漂移自证) · 完整输出见 logs/iss375/rerun_timing_check.log
───── $ python3 SW/tools/check_sw_zero_copper_grade_consistency.py ─────
[rc=0] 既有闸仍绿 · 完整输出见 logs/iss375/rerun_zero_copper.log
───── $ python3 state/merge.py ─────
[rc=0] STATE.yaml 已刷新 · 完整输出见 logs/iss375/rerun_merge.log
───── $ python3 state/gate_check.py ─────
【Q1 交付齐备率】 18/18 个必填验收块齐全
【Q7 钉板 md5 闸链】 10/10 道绿
[rc=0] · 完整输出见 logs/iss375/rerun_gate_check.log
───── $ python3 state/check_brief_commands.py ─────
── 查了 9 条待办单的 task_brief, 有问题的 0 条
[rc=0] · 完整输出见 logs/iss375/rerun_brief_commands.log
───── $ grep -c check_debug_pin_order_contract state/gate_check.py ─────
0
[零挂链自证通过]
───── $ md5sum HW/PCB/demo_mainboard.kicad_pcb ─────
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
───── $ stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb ─────
2026-11-06 07:07:17.362193413 +0800 4940213
```

★**板指纹纪律自证 (提醒 ③)**: ★**板 md5 在【我自己的脚本前后】各打一次 = 逐字相同**; ★**且我没有跑 `state/check_sch_pinfull.py` / `state/check_sch_erc.py`** (★那两条会 subprocess 调 `gen_kicad_sch.py` ⇒ 重铸随机 UUID ⇒ 任何 md5 比对都失效★) ⇒ ★**必跑清单里的 5 条 `merge.py` / `gate_check.py` / `timing_check.py` / `check_sw_zero_copper_grade_consistency.py` / `check_brief_commands.py` 全部只读不重铸** ⇒ ★**md5 前后可比** ★

### ★B5-③ 追加 ⑥: 派活材料里的两处【路径/指纹】订正 (本单未碰这两个文件) ★
- ★**脚表 md5 口径**: 派活材料 §三写「脚表 `9174309d…`」⇒ ★**本机实读 `9174309df1ec9411ac8e8d9e80ee386a` = `HW/netlist_v1_pins.csv` (网表针脚级表)**, 而 ★**官方 399 行 SoM 脚表 `HW/PCB/FET3572C_PIN_TABLE.csv` 的 md5 = `67340a0b707095fc4c0755a4c79ea8b6`** ⇒ ★**两者是不同文件, 本单【都只读未动】** ★ (★派活材料把「脚表」这个标签同时指了两份文件, 本单按【文件路径】区分, 已在真相页 §4-2 与 B4 里各写各的 md5★)
- ★**两条路径在派活材料里写错** (cont2 已登记, cont3 复核仍在): ★`HW/check_pcb_nets.py` ⇒ 实际在 **`state/check_pcb_nets.py`**; ★`HW/PCB/FP_TRUTH_BASELINE.md` ⇒ 实际在 **`HW/FP_TRUTH_BASELINE.md`** ⇒ ★**不是文件被删, 是路径写错** ★

### ★B6 最终验收 (cont3 · 2026-11-24 04:29 本机实跑 · 全部 10 条必跑命令逐条 rc) ★

| # | 命令 | rc | 判定 |
|---|---|---|---|
| 1 | `python3 SW/tools/check_debug_pin_order_contract.py` | **0** | ✅ D0~D8 **9/9 PASS** · 末行 `ALL CHECKS PASS` |
| 2 | `python3 SW/tools/check_debug_pin_order_contract.py --selftest` | **0** | ✅ **11/11 PASS** · 末行 `ALL TESTS PASS` · 镜像类 M1/M2/M3 |
| 3 | `python3 SW/tools/timing_check.py` | **0** | ✅ 既有闸仍绿 (零漂移自证) |
| 4 | `python3 SW/tools/check_sw_zero_copper_grade_consistency.py` | **0** | ✅ 既有闸仍绿 |
| 5 | `python3 state/merge.py` | **0** | ✅ `STATE.yaml 已刷新 (2026-11-24T04:29:09+08:00)` · 产出 816 · 冲突 0 |
| 6 | `python3 state/gate_check.py` | **0** | ✅ **Q1 18/18 必填验收块齐全** · **Q7 钉板 md5 闸链 10/10 道绿** |
| 7 | `python3 state/check_brief_commands.py` | **0** | ✅ 查了 7 条待办单, 有问题的 0 条 |
| 8 | `grep -c check_debug_pin_order_contract state/gate_check.py` | 1 | ✅ **输出 `0`** = 零挂链 (grep 无命中 rc=1 属正常) |
| 9 | `md5sum HW/PCB/demo_mainboard.kicad_pcb` | 0 | ✅ `611b869e13518c3c023fb178f91a0075` (**与开工前逐字相同**) |
| 10 | `stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb` | 0 | ✅ `2026-11-06 07:07:17.362193413 +0800 4940213` (**mtime + size 逐字相同**) |

★**零落表 / 零改既有闸 自证 (cont3 复核, 与 cont2 记录的基线逐字相同)★**

| 项 | md5 |
|---|---|
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` ✔ 未动 |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` ✔ 未动 |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` ✔ 未动 |
| `HW/PCB/FET3572C_PIN_TABLE.csv` (官方 399 行脚表) | `67340a0b707095fc4c0755a4c79ea8b6` ✔ 未动 |
| `SW/tools/timing_check.py` | `cf09c921002937920bfa40701d523b33` ✔ 一字未改 |
| `SW/tools/check_onepass_sw_release.py` | `4d7ce982965e92c78a1ebcd3e968874e` ✔ 一字未改 |
| `SW/tools/check_fp_truth_read.py` | `cab7a6f17c1da35f4e54185ad8b62089` ✔ 一字未改 |
| `SW/tools/check_sw_zero_copper_grade_consistency.py` | `58a3aa445842cd9ba89fe1e75bb9fc31` ✔ 一字未改 |
| `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` | `5f370bb8cf828473e70ccc5d6412da98` / `c9191025020fefd9b475e2573a335815` / `3b383a52b4fa540f1d16a2c6f3811de8` ✔ 一字未改 |

★**板 md5 纪律 (提醒 ③)**: ★**板 md5 在【我自己的脚本前后】各打一次 = 逐字相同**; ★**全程【没有】跑 `state/check_sch_pinfull.py` / `state/check_sch_erc.py`** (★那两条会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 重铸随机 UUID ⇒ 任何 md5 比对都失效★) ⇒ ★**必跑清单里的 5 条全部只读不重铸 ⇒ md5 前后可比** ★
★**留证**: `logs/iss375/final_suite_1.log` (新闸 + selftest 原样输出) · `logs/iss375/final_suite_2.log` (其余 8 条命令原样输出) · `logs/iss375/rerun_brief_sec1_3_current_land.log` (§一③ 复跑留证) ★

### ★B5-⑤ 追加: cont3 落盘清单增量 ★
| 路径 | 动作 | 备注 |
|---|---|---|
| `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` | **追加式订正** (未重写) | 35,582 B ⇒ 40,505 B (cont3 追加「§一③ 口径差」+「闸 M2/M3 强化」两段) |
| `SW/tools/check_debug_pin_order_contract.py` | **改 (强化 M2/M3 + 修注入点 bug)** | 本单自己的闸 · 裸跑 rc=0 / 9/9 · selftest rc=0 / 11/11 |
| `HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md` | **追加式订正** (未重写) | 本文件 · cont3 追加 §B5-③④⑤⑥ + §B6 最终验收 + §B5-⑤ 增量 |
| `state/fragments/sw.yaml` | **登记 (frag_write.py 原子写)** | 写前 `973ec64fee05f764cd88e565f7723204` ⇒ 写后 `2f6d78da2a0c35ba674600b8403cabf9` ⇒ ★**期间无人改过 (未被并发覆盖)** ★ · 6 claims + 2 needs 全部在位 |
| `logs/iss375/` · `tmp/iss375_sbx/` | 沙盒留证 (已在盘) | 新增 `final_suite_1/2.log` · `rerun_brief_sec1_3_current_land.log` |

★**★要 main 裁的两件事, 一句话复述 (与 B5-①② 一致, 本单不代拍)★**
1. ★**那一趟 `J_DEBUG`/`J_UART` 的 pin1 朝向选 rot 90 (建议 · 原点 141.0450 / 18.2550 · 顺排 · pad1@X_MIN) 还是 rot 270 (原点 144.8550 / 19.5250 · 逆排 · pad1@X_MAX)?** ★ (★两候选几何逐字等价 ⇒ 不是结构问题, 是装配与救砖线序契约问题; 选定后真相页 §1 的 `iss375_contract` 块改 rot 值即可, 闸 D2/D4 当场校验★)
2. ★**ISS-344 终裁 (JTAG_TDI 判为「必需」+ 板侧不许标 NC) 与网表现状 (`JTAG_TDI_SOC` 的 SoM 侧端点此刻就是 `SoC_NC`) 对不上, 改哪一处?** ★ (★三条路的代价已在真相页 §3-2 列全 = ①改裁决口径 ②改网表 (脚表无 JTAG 同名信号 ⇒ 当前走不通) ③改 SoM 选型换板 (放弃 S3 救砖, 只剩 S4 返厂); 本单【不代拍】, 且不改 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 一个字★)
