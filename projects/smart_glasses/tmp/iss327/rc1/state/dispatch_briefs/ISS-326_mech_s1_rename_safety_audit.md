# ISS-326 · mech-lead · ★★【S1 位号改名「MECH 侧」安全性体检】★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 14:1x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: mech-lead (结构总工) · ★**verify_by**: main · ★**单号**: ISS-326 · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯分析 + 沙盒实跑类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★
> ★**为什么是「MECH 侧」**: ★**SW 侧同款体检 ISS-321 已经做过了 (SW/tools/ 全部判据脚本) ⇒ SW 侧「改名会不会炸闸」这件事【有人管过了】★ ⇒ ★**但 MECH 侧【从来没有人做过】★** ★

---

## ★① 病灶 (★main 2026-11-18 14:0x 本机实读 · 不抄任何 agent 报告★)

★**背景**: ★**「板只改一次」那一趟 (S1 位号改名) 会把 218 个表侧真实器件里的 186 个加 `_1` 后缀** ★ ⇒ ★**MECH 域的判据脚本里有一批【硬编的位号字符串】⇒ 改名后那些脚本要么【崩】、要么【静悄悄不查了】** ★
★**⇒ 这就是 ISS-321 在 SW 侧发现的同一个病灶 (`timing_check.py` L1113 崩) 的 MECH 同型 —— 而 MECH 侧至今【零体检】** ★

★**main 本机实读的三个事实 (★都是本轮现读的★)**:

★**事实 ① — 改名表里哪些 ref 会变**: ★**`HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` §1 表 = 218 行 ⇒ 改名 186 / 不动 32** ★ (★main 用 python 解析该表逐行数出来的★)
★**这 186 个里, MECH 域硬编过的至少 18 个** ★:
★`J_DEBUG`→`J_DEBUG_1` · ★`J_UART`→`J_UART_1` · ★`J_USB_C`→`J_USB_C_1` · ★`J_CHG`→`J_CHG_1` · ★`CONN_CAM`→`CONN_CAM_1` · ★`CONN_LIGHT`→`CONN_LIGHT_1` · ★`D_LED_G`→`D_LED_G_1` · ★`R_LED_G`→`R_LED_G_1` · ★`D_LED_B`/`D_LED_R`/`R_LED_B`/`R_LED_R`/`TP_LED_B`/`TP_LED_R` 各加 `_1` · ★`R_SEL_D0_N`→`R_SEL_D0_N_1` · ★`R_SEL_D1_N`→`R_SEL_D1_N_1` ★
★**★不动的那 32 个里有 4 个是 `J_SOM_P1..P4` ⇒ ⇒ ★**`J_SOM_P1..P4` 不受影响** ★ (★这一点必须写清, 不许把 MECH 的 `SOM_REFS` 误报成风险★)

★**事实 ② — MECH 域哪些文件硬编了这些 ref (★main 全仓 grep 出来的, 逐文件列在下面§②-2★)**: ★**至少 10 个判据脚本 + 2 个工具脚本** ★

★**事实 ③ — ★★MECH 域【没有位号可达性闸】★★**: ★**`ls MECH/` 里没有任何 `reach` / `ref` / `drift` / `designator` 相关文件** ★ ⇒ ★**SW 侧有 `SW/tools/check_sw_ref_reachability.py` (ISS-318 建) ⇒ MECH 侧【连这层护栏都没有】** ★
★**★但要注意一个真实的覆盖边界 (★main 读源码确认★)**: ★**SW 那道闸的主扫描面是 `SW/*.md` (它的 `DOC_GLOB`) ⇒ 它【不覆盖 `MECH/*.py`】** ★ (★它的 `AUX_PY_DIRS` 只含 `SW/tools` / `state` / `HW`; `MECH` 只在 `AUX_MD_DIRS` 里 ⇒ **MECH 的 md 会被当「文档互引」分类, 但 MECH 的 py 完全不在扫描面**★) ⇒ ★**⇒ MECH 侧的 py 硬编码是【真空】, 本单要补的就是这块** ★

---

## ★② 要交的三件 (★每件都能独立验收★)

### ★②-1 · ★★「MECH 侧位号硬编码」全量清单 (★机器扫, 不许手抄★)

★**落点**: ★**`MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md`** ★ (★**新建**; ★`MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` 是 ISS-324 的, 只读·不许改★)

★**必须有一张表, 每行 = (文件 · 行号 · 硬编 ref · 改名后 ref · 命中上下文 · 失效形态)** ★:

| 列 | ★口径★ |
|---|---|
| 文件 + 行号 | ★**机器扫出来的, 逐条给行号★** |
| 硬编 ref | ★**原样字符串 (★可能是元组/列表/字符串常量, 不许只写名字★)** |
| 改名后 ref | ★**照 §1 表查出来 (★`不动` 也要列出来 —— 证明你查过了★)** |
| 命中上下文 | ★**那几行原文 (★判定「是判据」还是「只是文档叙述」★)** |
| ★**失效形态** ★ | ★**★三选一, 必须逐条判, 不许留空★** ★① `崩` (★`KeyError` / `TypeError` / `IndexError` ★) ★② `静悄悄不查了` (★判据分支再也匹配不上 ⇒ 【假绿】★ ⇒ ★这是最坏的一类★) ★③ `只是文档叙述` (★改了也不影响判据★) |

★**★三条硬要求★**:
1. ★**扫描面 = `MECH/**/*.py` (★递归, 不许只扫顶层★) + `MECH/**/*.md` 递归** ★ ⇒ ★**main 本轮实测顶层 `MECH/*.md` + `MECH/*.py` 里的位号字面量共 571 处 (★主文件前 5 名: `BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 174 / `BOARD_ONEPASS_MECH_SYNC.md` 129 / `ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` 120 / `BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 116 / `BOARD_ONEPASS_MECH_CLAIMS.md` 74★) ⇒ ★**你必须给出一个【递归全量】的数, 与 main 的顶层数对得上 (★对不上就说明漏了子目录★)** ★
2. ★**★必须把「判据脚本」和「一次性脚本 / 归档脚本」分开列** ★ ⇒ ★**`MECH/_apply_*.py` / `_frag_update_*.py` / `rebase_*.py` 这类【历史落地脚本】里的硬编 ref 【不需要改】(★它们跑完就没了★) ⇒ ★**列出来但标成「历史脚本 · 不改」**, 不许混进「要改」清单 ★
3. ★**★判据脚本里那些 `✓ 只在注释里` 的行必须单独标出来** ★ ⇒ ★**main 本轮在 ISS-320 交卷里已经见过同型事故 (`MECH/service_port_check.py` L51 的型号名在注释里, 被 md5 钉死 ⇒ 改不了·也不该改)** ★ ⇒ ★**注释里的 ref 名【不需要改】, 但必须在表里出现并写明「注释 · 无功能影响」★**

### ★②-2 · ★★「崩 / 假绿」逐条沙盒实证 (★★不许只做静态推断★★)

★**★main 已经在源码里看到两处【判据脚本真的会炸】的实例, 你必须把它们的真实失败形态跑出来★**:
- ★`MECH/check_board_frame_coords.py` L963~L964 用的是 ★**`fps.get(RES_REF)` / `fps.get(LED_REF)` (★安全·找不到返回 None★)** ⇒ ★**但 L999 是 ★`led = fps[LED_REF]` (★直接下标 ⇒ 改名后 KeyError★)** ⇒ ★**同一个文件里两种写法 ⇒ 一个崩一个不崩 ⇒ 崩溃点不在你以为的地方★**
- ★`MECH/check_onepass_struct_crosscheck.py` L1107 / L1129 是 ★**`if t["ref"] == "R_SEL_D0_N":` / `== "R_SEL_D1_N"` ⇒ 改名后【再也匹配不上】⇒ ★**不是崩, 是【那条判据从此不生效】= 假绿**** ★★

★**★沙盒怎么跑 (★不许碰项目真文件★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★沙盒 1: 把 MECH 域 + 网表 + 脚表复制到临时树, 在副本里做改名, 再跑副本里的脚本
# ★沙盒 2: 至少挑 3 个脚本 (★一个「会崩的」· 一个「会假绿的」· 一个「只是文档叙述的」★)
#        实跑【改名前】与【改名后】两遍 ⇒ 逐条贴 rc + 关键输出行 (★不是「通过/不通过」★)
```
★**★铁律: ★★沙盒只许写 `tmp/iss326/` + `logs/iss326/`★★** ⇒ ★**`MECH/**` / `HW/**` / `SW/**` 的真文件一个字不许动** ★ (★要验证「改名后」的行为, 就把脚本 + 它读的数据整棵树复制到沙盒里改★)

★**★反例必须自己抓 (★这是本单最值钱的一段★)**: ★**至少 4 条反向用例, 每条要贴「期望红/绿」与「实际红/绿」★** ⇒ ★**例如: ① 把 `R_SEL_D0_N` 改成别的名字 ⇒ 那条判据【必须变成不匹配】⇒ 你要证明它【红不出来】(假绿) ② 把 `D_LED_G` 改掉 ⇒ `fps[LED_REF]` 必须抛异常 ⇒ 你要贴出异常类型与那一行 ③ 改一个【不该改的】ref (★`J_SOM_P1` —— 它不改名★) ⇒ 闸必须【不受影响】⇒ 证明你没误伤 ④ 注释里的 ref 名改成别的 ⇒ 闸必须【不受影响】(★功能零变化★)** ★

### ★②-3 · ★★「MECH 侧位号可达性闸」设计稿 (★只给设计 + 反向用例, ★★不许挂进 `state/gate_check.py`★★)

★**★因为 SW 侧已经有同款 (`SW/tools/check_sw_ref_reachability.py`), MECH 侧要抄的应该是【那个闸的判据口径】, 而不是重写一个弱版★** ⇒ ★**你必须先读它的源码, 再写 MECH 版的设计稿★** ★
★**设计稿里必须包含**: ★① 扫描面 (★`MECH/**/*.py` + `MECH/**/*.md` 递归 · **不许只扫顶层**★) ★② 分类口径 (★照抄 SW 那道的 C1/C2/C14 三类 + 冻结注册表的建闸日基线机制★) ★③ **fail-closed 三条** (★照 SW 那道的口径: 取不准必须判红, 不许放宽成「取最近一条」★) ★④ 反向用例 ≥ 5 条 ★⑤ **基线数怎么定** (★SW 那道建闸日 `DESIGNATOR_MISSING` = 3 条 ⇒ MECH 版建闸日基线必须自己 fresh 测, 不许抄 3★) ★
★**★不许写 `state/gate_check.py` (★挂闸是 main 的机制地界★) ⇒ 只交设计稿 + 「建议挂进 `EXTRA_GATES` 的第几位 + 逐字写法」★**

---

## ★③ 交卷物 (4 件)

1. ★**主交付物** ★`MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` (★§0~§7 全填 · 占位符 0★)
2. ★**交卷单** ★`HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md` (★B0~B6 齐全★)
3. ★**证据目录** ★`logs/iss326/` (★逐条原始输出 · 沙盒脚本 · md5 前后快照★)
4. ★**分片** ★`state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写 · ★**禁 `open(p,"w")`**★ · artifacts / needs_from / interface_claims 各 ≥1 · status 换 ISS-326★)

---

## ★④ 边界 (★违反就是不合格★)

★**零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 一个字节不许动★) · ★**零改闸** (★`MECH/*.py` 一个字都不许改 —— 本单只出体检 + 设计稿★) · ★**零改既有文档正文** (★`MECH/**` 既有 md 只读★) · ★**沙盒只写 `tmp/iss326/` + `logs/iss326/`** ★ · ★**只写 `state/fragments/mech.yaml`** (★`hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节都不许碰★) · ★**零改 `state/gate_check.py`** (★挂闸归 main★) · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 · 需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** (★§2-3 只给设计稿 + 建议默认值 + 不拍的后果★) · ★**不自签 `state/issue_log.yaml`** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要查的行★)

---

## ★⑤ 交卷前必跑 (★原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py   # rc 必须 0
python3 MECH/check_board_frame_coords.py        # rc=0 (★改名前基线·沙盒里跑改名后那版★)
python3 MECH/check_onepass_mech_sync.py --selftest
python3 MECH/check_onepass_struct_crosscheck.py
python3 MECH/check_demo_struct_truth.py
python3 MECH/board_port_opening_s6_check.py
python3 MECH/jd_y0_feasibility.py
python3 MECH/service_port_check.py
python3 MECH/check_onepass_mech_release.py
python3 MECH/board_frame_feasibility.py --selftest
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
grep -cE "🔄|待填|PLACEHOLDER|施工中" MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md   # 期望 0
grep -c "iss326" state/fragments/mech.yaml                                       # 期望 >= 1
```

---

## ★⑥ 纪律 (★这项目的老教训·今天又踩过一遍★)

★**① 交卷单第一件事就是 `write` 建骨架** (★哪怕只写 3 行标题 + 交付物清单★) · ★**② 长任务一律 `nohup ... > logs/iss326/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**③ 单条 `exec` ≤ ~120 秒** (★★本机现在有两条 ISS-325 的沙盒臂在跑, 各自吃满一个核 ⇒ ★**你跑重活时会更慢 ⇒ 更要短轮询·不许前台长跑★**) · ★**④ 每 10 分钟至少一次写盘** · ★**⑤ 每落一件交付物就把 rc 追加进交卷单** · ★**⑥ 分片写完 `grep` 校验** · ★**⑦ ★★沙盒里做「改名后」的行为, 必须是把【脚本 + 它读的数据】整棵树复制过去再改 —— 不许在真文件上改·改完再改回来 (★那叫擦产物, 不叫验证★)★★**
