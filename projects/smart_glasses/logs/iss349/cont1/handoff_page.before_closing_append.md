# ISS-349 · hw-lead 交卷页 · 「板侧项全集」页的生成器回归修复 (E-1 排针 land 那一条重跑不蒸发)

★派活方 = 项目总工 (main / moli) · 2026-11-23 01:4x · cron fb67af40 (队列自动派活)★
★执行 = 硬件总工 (hw-lead) · 2026-11-23 01:4x~02:0x · 工作目录 = `/home/yuewuya/.openclaw/workspace/projects/smart_glasses`★
★**零写板 · 零落表 · 零改网表/脚表/BOM/原理图/`.kicad_pro` · 零改既有闸判定逻辑 · 零外发 · 不代拍** ★
★**本单性质: 「板只改一次」那一趟开工前的【判据冻结类】⇒ 做完之后那一趟期间不许再动生成器 / 新闸 / 那一页** ★

---

## B0 · 派活复述与本单边界

★**病根 (★本机实读 + 实跑, 不抄任何 agent 报告★)★**: ISS-343 把 `B33_PIN_LAND_1P27` (E-1 排针 land 0.50→1.27) **手写**进了 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 §7 JSON 块 ⇒ ★**那一份是生成器 `state/_iss277_build_preflight.py` 的产物**★ ⇒ ★**下一次重跑生成器, 这一条【静默蒸发】** ⇒ 「板只改一次」那一趟的板侧项全集少一条 ⇒ ★**实物排针照样装不进 ⇒ 补做 = 板 md5 变第二次 (2-4 周 + ¥4-8K)** ★

★**本仓铁律本来就写着 (★是这一单没照做, 不是 agent 的错★)★**:
- `state/dispatch_briefs/ISS-304_hw_workpack_state_values_reanchor.md:52` 逐字: 「★**不许手改生成器产物**: ★**清单页 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) 是 `state/_iss277_build_preflight.py` 的产物 ⇒ 改它 ⇒ 等于下一次重跑就回退 ⇒ ★**必须改 sidecar / 生成器, 再重跑生成器** ★」
- `state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md:107` 逐字: 「★**不许改 `state/_iss277_build_preflight.py` 的取数逻辑 (★那部分已经对了★)** ★**只许改它允许的地方 = 加 E-1~E-6 那一条的读入 (★不许写死六条·从真源读★)** ★」
- ⇒ ★**E-1 本来就该长在生成器里** ⇒ ★**本单就是把这条路补上** ★
- ★**派单口径的漏项 (★main 自认★)**: ISS-343 的任务书 §1-① 写的是「★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` **追加一条 item**★」⇒ agent 照做 ⇒ ★**本单不把这一条算成 agent 的错** ★

★**★重跑不是假想, 是流程里写着的动作 (★本机实读★)★**: `state/_iss304_sync_state_baseline_md5.py:145` 逐字 → 「★★落表后重锚流程: ① `python3 state/_iss277_build_preflight.py` ② … ★★」⇒ ★**每次落表重锚都会触发这次蒸发** ★

★**本单不依赖老板拍板**: E-1 = main 2026-11-17 18:45 已拍死 (`state/fragments/pm.yaml` → key `main_e1_e2_board_side_rulings_20261117` → `decision` = 「E-1 = 按 1.27mm 排针定 + 板 land 并进那一趟重画」) ⇒ ★**纯技术活 · 零写板 · 现在就做完** ★

---

## B1 · 结论摘要

★**一句话结论**: ★**本单四件交付全部做完: E-1 那一条已经长在生成器里 (现状值全部现读) ⇒ 重跑不再蒸发; 页回到【表 33 == JSON 33 且 id 集合逐一相等】; 新闸 `HW/check_preflight_regen_idempotent.py` 四条判据 + 5 条反向用例 (含「板读改成 1.27 ⇒ 页里的现状值自己变」) 全绿; 既有闸一个都没被弄红** ★

| # | 交付物 | 落在哪 | 结果 |
|---|---|---|---|
| ① | ★**E-1 那一条搬进生成器** (★id / `source_iss` 与 ISS-343 已写的逐字一致★) | `state/_iss277_build_preflight.py:691` (9 元组) + `:228`~`:400` (四条真源读函数) | ★**通过** ★ · 现状值**全部现读** · 写死值 **0** 个 |
| ② | ★**重跑生成器 ⇒ 页回到同源** | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★由生成器产出·不是手改★) | ★**通过** ★ · §2 表 **33** 行 · §7 JSON **33** 条 · id 集合**逐一相等** · 其余 32 条**老字一字未删** |
| ③ | ★**新机器闸** (★4 条判据 + 5 条反向用例★) | `HW/check_preflight_regen_idempotent.py` (499 行) | ★**通过** ★ · `--selftest` 末行 `ALL TESTS PASS` · rc=0 |
| ④ | ★**交卷三件** | 本页 + `logs/iss349/` + `state/fragments/hw.yaml` | ★**通过** ★ |

★**★板面真相 (★本机实跑, ★不改一行字★)★**:
- `J_DEBUG` = **4 脚 / pitch 0.50** / 铜箔 X `142.0625..143.8375` × Y `56.1500..57.0500` (1.7750 × 0.9000) ★[实测]★
- `J_UART` = **2 脚 / pitch 0.50** / 铜箔 X `18.5025..19.2775` × Y `68.1500..69.0500` (0.7750 × 0.9000) ★[实测]★
- BOM / 网表侧写的是 **1.27mm** (`HW/BOM_v1.csv:71` = `J_DEBUG` / `:77` = `J_UART`; 网表 `HW/netlist_v1.csv:396` / `:399`) ⇒ **Δ pitch 0.77** ★[实测] (规格串) / 「实物落不进」= ★[推算]★
- ★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 全程逐字节未动 ⇒ 零写板** ★[实测]★

★**★本单最要紧的一句话 (★给 main 看★)★**: ★**从这一刻起, 「板只改一次」那一趟的全集页 = 生成器的输出 ⇒ 谁重跑都不会少一条; 而【有人手改页】这件事从此当场红 (新闸 C2), 【生成器里那条被删掉】也当场红 (新闸 C4)** ★

---

## B1-附 · main 三问逐条作答 (★逐字贴证据, 不讲道理★)

### ★Q① 「重跑会蒸发 B33」你是怎么复现的? (★贴证据★)

★**在沙盒副本上跑一次生成器 (★真页一个字没碰★) ⇒ 前后三项 + 差集 + diff 行数 如下 (★完整原文见 `logs/iss349/evidence/evaporation_repro.txt`★)**:

```
== 跑前(ISS-343 手改后的真页) ==            ← logs/iss349/evidence/page_BEFORE_ISS343_handedit.md
   md5          = 8ae70471604dcf447f43477dbada3f13
   §2 表行数    = 32  (唯一 id 32)
   §7 JSON 条数 = 33  (唯一 id 33)
   表 id 集合 == JSON id 集合 ? False        ← ★**已经写岔了**★

== 跑后(沙盒重跑·生成器里没有 B33) ==        ← tmp/iss349/run_repro/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
   md5          = 9f9743c81b977be802322b0966997ee2
   §2 表行数    = 32  (唯一 id 32)
   §7 JSON 条数 = 32  (唯一 id 32)
   表 id 集合 == JSON id 集合 ? True

★两组差集:
   只在跑前 §2 表里   : []
   只在跑后 §2 表里   : []
   只在跑前 §7 JSON里 : ['B33_PIN_LAND_1P27']    ← ★**B33 在跑后的差集里**★
   只在跑后 §7 JSON里 : []

★跑前的页 vs 跑后的页 · diff 行数 = 14
★(★除 B33 那 11 行消失外·其余 32 条老字一字未删★)
    --- BEFORE
    +++ AFTER
    @@ -541,11 +540,0 @@
    -    },
    -    {
    -      "id": "B33_PIN_LAND_1P27",
    -      "source_iss": "ISS-290",
    -      "title": "`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)",
    -      "current_state": "[实测] 板读 (bash state/pcbnew_py.sh): `J_DEBUG` = pitch 0.50 / 4 脚 / …",
    -      "action": "那一趟把 `J_DEBUG`(1×4) 与 `J_UART`(1×2) 的 land pitch 从 0.50 改成 1.27 …",
    -      "criterion": "bash state/pcbnew_py.sh -c \"import pcbnew;…\" ⇒ 期望读数: … = 1.27 …",
    -      "step": "S6",
    -      "blocked_by": "-",
    -      "evidence": "[实测]"
```

★**⇒ 三条硬结论 (★全部本机实跑★)**:
1. ★**跑前的页本来就【表 32 ≠ JSON 33】= 已经写岔了** ⇒ 页脚那句「页与 JSON 同源 ⇒ 不会写岔」是**假的** ★
2. ★**跑一次生成器 ⇒ `B33_PIN_LAND_1P27` 只在【跑前的 JSON】里、跑后的差集里 ⇒ 当场蒸发** ★
3. ★**diff = 14 行 (11 行 B33 + 3 行 diff 头) ⇒ 其余 32 条老字一字未删** ⇒ ★**这次重跑除了蒸发 B33 之外, 别的什么都没动** ★

### ★Q② 新闸的三条判据分别从盘面哪一段读? (★贴代码行号★)

★**闸文件 = `HW/check_preflight_regen_idempotent.py` (★499 行·★本单新建★)**

| 判据 | 实现位置 (★文件:行号★) | 读盘面的哪一段 | 失败判定条件 (★判红的行★) |
|---|---|---|---|
| ★**C1 表/JSON 同源** ★ | ★`HW/check_preflight_regen_idempotent.py:175` (`check_C1`) · 抓表 `:87` (`parse_page`: `^##\s*§2\b(.*?)^##\s*§3\b` 段内抓 `\| ★\*\*`id`\*\* ★ \|`) · 抓 JSON `:100` (页里**第一个** ```json 块·★与覆盖度闸 `load_items()` 同口径★) | ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`** 的 §2 表格行首 id 列 + §7 JSON 块的 `items[].id` ★ | ★`:189-190` 差集 `only_tbl` / `only_js` 非空 ⇒ ★`:191` 判红并**点名差集** ★; ★`:183-188` id 重复也判红 ★ |
| ★**C2 重跑幂等** ★ | ★`HW/check_preflight_regen_idempotent.py:200` (`check_C2`) · 沙盒建 `:129` (`make_sandbox`) · 真跑生成器 `:154` (`regen`: `PREFLIGHT_PROJ=<沙盒>` + `TMPDIR=<沙盒>/tmp`) | ★**真页** = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★`PREFLIGHT_CHECKLIST` 可覆盖★) · ★**重跑输出** = 沙盒里 `state/_iss277_build_preflight.py` 的产物 (★`PREFLIGHT_GEN_PROJ` 指出生成器与真源的出处★) ★ | ★`:211` `if a == b:` 为假 ⇒ ★`:217-224` 判红并**贴 unified diff + 两个 md5 + id 差集** ★; ★`:206` 生成器跑挂 ⇒ 判「★**闸崩**★」(★与「闸红」严格区分·rc=3★) ★ |
| ★**C3 来源在册** ★ | ★`HW/check_preflight_regen_idempotent.py:232` (`check_C3`) · `SOURCES` 的读法 `:109` (`read_coverage_sources`: 正则解析 `^SOURCES\s*=\s*\{(.*?)\}`) | ★**`HW/check_onepass_preflight_coverage.py`** 的 `SOURCES` 集合 (★**只读·一个字不许改**★) | ★`:239` `if s not in sources:` ⇒ ★`:241` 判红并**点名 `id=` 与 `source_iss=`** ★ |
| ★**C4 必需项在场 (★加严块★)** ★ | ★`HW/check_preflight_regen_idempotent.py:248` (`check_C4`) · 必需项清单 `:65` (`REQUIRED_ITEMS = ("B33_PIN_LAND_1P27",)`) | ★**同一份清单页** 的 §2 表 + §7 JSON (★id 出现与否★) | ★`:260` `if not where:` ⇒ ★`:262` 判红并**点名「必需板侧项缺失: B33_PIN_LAND_1P27 (★表里没有·JSON 里也没有★)」** ★ |

★**★为什么要有 C4 (★它是 R1 能被抓住的那一条·★不是装饰★)★**:
★**C1/C2 抓的是「页自己写岔了」; C4 抓的是「生成器里那条被删了 ⇒ 重跑之后页上也没了 ⇒ 表和 JSON 反而一致 ⇒ C1/C2 都看不出来」** ★
⇒ ★**删掉 `ITEMS_RAW` 里的 `B33` ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 表 32 == JSON 32 (C1 绿) 且 页 == 重跑输出 (C2 绿) ⇒ 只有 C4 能抓住** ★

### ★Q③ 你的反向用例把 B33 弄没之后, 闸红了没有? 点的是哪一行? (★三条例外逐条答★)

★**全绿**: ★**R1 / R2 / R3 三条都判红, 恢复原件后再跑一次判绿 (★不是永远红的闸★) ★** (`logs/iss349/run_iss349_full.log` ③ 段)

| 用例 | ★沙盒改了哪个文件的哪一行★ | ★闸 rc★ | ★闸输出里点名的内容 (★逐字★)★ | ★恢复原件后再跑一次★ |
|---|---|---|---|---|
| ★**R1** ★ | ★`tmp/iss349/regen_gate/selftest/state/_iss277_build_preflight.py` ★ —— 删掉 ★`ITEMS_RAW` 里 `B33_PIN_LAND_1P27` 那 3 行 (★id 行 + 字段行 + `S6` 行★) ⇒ 重跑 ⇒ 页回到 **32** 条 ★ | ★**rc=1 (判红)** ★ | ★`❌ 必需板侧项缺失: B33_PIN_LAND_1P27 (★表里没有·JSON 里也没有★) ⇒ ★**生成器里那条被删掉 / 页里那条被手改掉 ⇒ 命中这里** ★` ★ | ★rc=0 (全绿) ★ |
| ★**R2** ★ | ★`tmp/iss349/regen_gate/selftest/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ —— §7 JSON 块里 `B33_PIN_LAND_1P27` 的 `current_state` 中 ★`pitch 0.50` → `pitch 9.99`★ (★真值改成假值★) | ★**rc=1 (判红)** ★ | ★`❌ 真页 != 沙盒重跑输出 ⇒ ★**页与生成器不同源 (重跑会改页)★** ⇒ md5 06a730fed9d7283b03d4d7db0170d055 vs 581f116a6e41c6c7d6b9290874ade4c5` ★ (+ 贴了 diff) ★ | ★rc=0 (全绿) ★ |
| ★**R3** ★ | ★`tmp/iss349/regen_gate/selftest/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ —— §7 JSON 块里 `B33_PIN_LAND_1P27` 的 ★`source_iss`: `ISS-290` → `ISS-999`★ (★不在 `SOURCES` 里★) | ★**rc=1 (判红)** ★ | ★`❌ id=B33_PIN_LAND_1P27 的 source_iss='ISS-999' 不在覆盖度闸的 SOURCES 里 ⇒ 来源不明` ★ | ★rc=0 (全绿) ★ |

★**★外加第 4 条 (★任务书 §1① 明写要的那条: 「沙盒里把板读结果改成 1.27 ⇒ 页里的现状值跟着变 ⇒ 不是死值」★)★**:

| 用例 | ★沙盒改了哪个文件的哪一行★ | 结果 |
|---|---|---|
| ★**R4** ★ | ★`tmp/iss349/regen_gate/selftest/HW/PCB/demo_mainboard.kicad_pcb` ★ —— ★**用 pcbnew 把 `J_DEBUG` / `J_UART` 的 land pitch 从 0.50 挪成 1.27**★ (★只动沙盒的板·真板零写★) | ★改板 rc=0 · 生成器 rc=0 · ★**页里的现状值自己变成了 1.27**★ ⇒ ★`[实测] 板读 … `J_DEBUG` = pitch 1.27 / 4 脚 / 铜箔 X 142.0625..146.1475 × Y 56.1500..57.0500 (4.0850 × 0.9000); `J_UART` = pitch 1.27 / 2 脚 / 铜箔 X 18.5025..20.0475 × Y 68.1500..69.0500 (1.5450 × 0.9000); … ⇒ Δ pitch 0.00 ⇒ ★E-1 已落地 (板读 pitch == BOM/网表要求)★`★ ⇒ ★**不是死值**★ |

---

## B2 · 验收标准逐条自评

★**逐条 对照 `state/dispatch_briefs/ISS-349_hw_preflight_b33生成器回归_修复.md` 的 §1 四件交付 + §3 必跑命令★**

| # | 验收标准 (★任务书逐字★) | 判定 | 自证 (★本机实跑★) |
|---|---|---|---|
| 1 | §1① 把 E-1 补进**生成器** (★不是补进页★) | ★**通过** ★ | `state/_iss277_build_preflight.py:691` = 9 元组 `("B33_PIN_LAND_1P27", "ISS-290", PL["title"], PL["current_state"], PL["action"], PL["criterion"], "S6", "-", "[实测]")` |
| 2 | §1① `id` = `B33_PIN_LAND_1P27` (★与 ISS-343 已写进 JSON 的 id 一致·不许改·不许重名★) | ★**通过** ★ | 页 §7 JSON 里该 id 逐字一致; 重复 id = 0 (C1 的 `:183-188` 判据也在盯这件事) |
| 3 | §1① `source_iss` = `ISS-290` (★必须保持·否则覆盖度闸判「来源不明」★) | ★**通过** ★ | 新闸 C3 输出: 「33 条 item 的 source_iss 全在 SOURCES (11 个来源单) 里: ✔」 |
| 4 | §1① 格式照抄 `B01_REF_SUFFIX` / `B32_V2_NET_RENAME` 两条 (★9 元组★) | ★**通过** ★ | 生成器 `:691` 与 `:494`(`ITEMS_RAW`) 的其它条目同格式; 页 §7 JSON 该条 9 字段齐全非空 (覆盖度闸 P1 ✔) |
| 5 | §1① ★**九个字段的值不许写死现状**★: 板读 pitch 必须现读板 | ★**通过** ★ | `state/_iss277_build_preflight.py:228` `read_board_pin_land()` ⇒ `bash state/pcbnew_py.sh -c "import pcbnew;…"`; 实跑输出 `J_DEBUG|pitch=0.5000|npads=4|x0=142.0625|x1=143.8375|y0=56.1500|y1=57.0500` / `J_UART|pitch=0.5000|npads=2|x0=18.5025|x1=19.2775|y0=68.1500|y1=69.0500` |
| 6 | §1① BOM/网表里的 1.27 从 `HW/BOM_v1.csv` / `HW/netlist_v1.csv` 读 | ★**通过** ★ | `:280` `read_pin_land_spec()` ⇒ 实跑读到 `BOM_v1.csv:71` / `:77` + `netlist_v1.csv:396` / `:399`; ★**两处口径不一致 ⇒ 拒写页**★ |
| 7 | §1① 读不到 ⇒ **fail-closed 拒写页** (★与生成器现有两条真源读法同款纪律★) | ★**通过** ★ | 四处 `raise SystemExit(★…拒写页 (★fail-closed·不许猜★)…★)` (`:250` / `:286` / `:296` / `:307` / `:396` / `:401`) |
| 8 | §1① ★**不许把 `0.50` / `1.27` / 铜箔坐标写死成常量** ★ | ★**通过** ★ | 生成器里 `0.50` / `1.27` / `142.0625` 等**一个都不出现** (★数字全部来自 `read_board_pin_land()` / `read_pin_land_spec()`★); ★**R4 反证**: 沙盒板改成 1.27 ⇒ 页里现状值自己变 1.27 (§B1-附 Q③) ★ |
| 9 | §1② 跑 `python3 state/_iss277_build_preflight.py` (★cwd = 项目根★) | ★**通过** ★ | 已跑 1 次 (★正式页★) + 沙盒多次; 输出「★已写 … (33 条, 76862 字节)★」 |
| 10 | §1②★验收 1: §2 表行数 == §7 JSON 条数 == 33 且 **id 集合逐一相等** (★不许只比个数★) | ★**通过** ★ | 「§2 表行数 = 33 · 唯一 id = 33 / §7 JSON 条数 = 33 · 唯一 id = 33 / 两集合逐一相等 ? True / 只在表里 = [] · 只在 JSON 里 = []」 (`logs/iss349/run_iss349_full.log` ② 段) |
| 11 | §1②★验收 2: 除新增 `B33` 外其余 32 条**老字一字未删** ⇒ 逐行 diff | ★**通过** ★ | 改页前后的 diff = **4 处 / 10 行**: ①§2 表 +1 行 (B33) ②§4 步分布 S6 `9 → 10` ③§7 JSON 的 B33 `current_state` 一行 (★加了两处真源出处·其余 32 条一行未动★) ⇒ ★**删除行 = 0** ★ |
| 12 | §1②★验收 3: 若重跑导致别的行的现状值也变了 ⇒ 逐条列出 | ★**通过 (零变化)** ★ | ★**除了 B33 那一条, 其余 32 条逐字节相同 (diff 已贴)** ⇒ 无需列举「哪一行变了」 ★ |
| 13 | §1②★沙盒跑法 (★不许拿真页练手★) · 沙盒落项目盘 `tmp/iss349/` (★`/tmp` EDQUOT ★) | ★**通过** ★ | 沙盒 = `tmp/iss349/sb_base` / `tmp/iss349/regen_gate` / `tmp/iss349/run_repro`; ★**全程 `TMPDIR=$PROJ/tmp/iss349/tmpdir`★ ⇒ 零字节落 `/tmp` ★ |
| 14 | §1③ 新建 `HW/check_preflight_regen_idempotent.py` (★独立脚本 + 自测★) | ★**通过** ★ | 499 行; `--selftest` 末行 `ALL TESTS PASS` · rc=0 |
| 15 | §1③★判据 1: §2 表 id 集合 == §7 JSON id 集合 ⇒ 不等判红并**点名差集** | ★**通过** ★ | `check_C1` `:175`; 反证 = R1 (表与 JSON 一致时靠 C4, 差集点名路径由 `:191` 输出) |
| 16 | §1③★判据 2: 真页 == 生成器沙盒重跑输出 (★md5 相同 ⇒ 零行差异★) ⇒ 不等判红并**贴 diff** | ★**通过** ★ | `check_C2` `:200`; 实跑: 「真页 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 沙盒重跑输出 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 零行差异: ✔」; 反证 = R2 |
| 17 | §1③★判据 3: 每条 item 的 `source_iss` 必须仍在覆盖度闸 `SOURCES` 里 (★只读那个文件★) ⇒ 不在判红并**点名** | ★**通过** ★ | `check_C3` `:232` + `read_coverage_sources` `:109`; 反证 = R3 |
| 18 | §1③★方向纪律: 只许【加严】不许【放宽】 | ★**通过** ★ | ① `HW/check_onepass_preflight_coverage.py` **一个字节未改** ② `HW/check_workpack_state_values.py` **一个字节未改** ③ `state/gate_check.py` **一个字节未改** (★挂载行留给 main·见 §B4★) |
| 19 | §1③★反向用例 ≥3 条, 带 `--selftest`, 末行 `ALL TESTS PASS`, rc=0 | ★**通过 (5 条)** ★ | 正例 + R1 + R2 + R3 + R4 + 「恢复原件后再跑一次」 ⇒ 末行 `ALL TESTS PASS` · rc=0 |
| 20 | §1③★R1: 生成器 `ITEMS_RAW` 里删掉 `B33` ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸红并点名 | ★**通过** ★ | 见 §B1-附 Q③ (点名行原文已贴) |
| 21 | §1③★R2: 真页 JSON 里 `B33` 的 pitch 改成假值 `9.99` ⇒ 闸红 | ★**通过** ★ | 见 §B1-附 Q③ |
| 22 | §1③★R3: 某条 item 的 `source_iss` 改成不在 `SOURCES` 里的号 ⇒ 闸红并点名该 id | ★**通过** ★ | 见 §B1-附 Q③ |
| 23 | §1③ 三条例外验证完**恢复原件** ⇒ 判绿 (★闸不是永远红的★) | ★**通过** ★ | 自测最后一条: 「恢复原件后 · 再跑一次 ⇒ 闸绿 (★不是永远红的闸★)」 PASS |
| 24 | §1④ 交卷页 B0~B7 齐全 | ★**通过** ★ | 本页 |
| 25 | §1④ `logs/iss349/` (★新建 `run_iss349.sh` ⇒ 一条命令可复现全部读数★) | ★**通过** ★ | `logs/iss349/run_iss349.sh` + `logs/iss349/run_iss349_full.log` + `logs/iss349/evidence/` (3 件) |
| 26 | §1④ 分片只许走 `python3 state/frag_write.py --agent hw-lead` (★禁止 `open(p,"w")` 手写 YAML★) | ★**通过** ★ | 见 §B6 末 (★零手写 YAML★) |
| 27 | §3 必跑 ① 板指纹 (★前后双证★) | ★**通过** ★ | 前 `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` · 后**逐字相同** |
| 28 | §3 必跑 ② 新闸 `--selftest` (★末行 ALL TESTS PASS·rc=0★) + 新闸主模式 (★rc=0★) | ★**通过** ★ | 见 §B6 ② |
| 29 | §3 必跑 ③ 既有闸不许被本单弄红 (`check_onepass_preflight_coverage.py` / `check_workpack_state_values.py`) | ★**通过** ★ | 两个都 `✅ rc=0` (★见 §B6 ③★) |
| 30 | §3 必跑 ④ `python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0 且 **Q1 = 18/18** | ★**通过** ★ | 「【Q1 交付齐备率】 18/18 个必填验收块齐全」 · `GATE_RC=0` |
| 31 | §3★沙盒自测必须**端到端跑真生成器** (★不许只测纯函数★) | ★**通过** ★ | 自测 5 条用例里有 3 条真跑 `python3 state/_iss277_build_preflight.py` (★正例 / R1 / R4★) |
| 32 | §5⑤ 引用的每个文件路径都要 `[ -e ]` 查过 ⇒ 页内 MISS 行数 = 0 | ★**通过** ★ | 见 §B7 的 MISS 自检 (★MISS = 0★) |
| 33 | §2 边界: 零写板 / 零落表 / 零改网表·脚表·BOM·原理图·`.kicad_pro` / 零手改清单页 / 零改既有闸判定逻辑 / 零外发 / 不代拍 / 不落 `/tmp` | ★**通过** ★ | 见 §B7 |

★**★不通过项 = 0 · 未验项 = 0★**

---

## B3 · 证据分级

| # | 结论 | 证据等级 | 出处 (★在盘★) |
|---|---|---|---|
| 1 | 跑前的页 §2 表 32 行 / §7 JSON 33 条 ⇒ **表与 JSON 已经不同源** | ★**[实测]** ★ | `logs/iss349/evidence/evaporation_repro.txt` · 证据副本 `logs/iss349/evidence/page_BEFORE_ISS343_handedit.md` (md5 `8ae70471604dcf447f43477dbada3f13`) |
| 2 | 生成器重跑 ⇒ `B33_PIN_LAND_1P27` **当场蒸发** (差集 + diff 11 行) | ★**[实测]** ★ | 同上 (跑后 md5 `9f9743c81b977be802322b0966997ee2`) |
| 3 | 修完之后: 表 33 / JSON 33 / id 集合逐一相等 / 沙盒重跑 md5 == 真页 md5 | ★**[实测]** ★ | `logs/iss349/run_iss349_full.log` ②③ 段 · 真页 md5 `581f116a6e41c6c7d6b9290874ade4c5` |
| 4 | `J_DEBUG` / `J_UART` 板读 pitch 0.50 + 铜箔坐标 | ★**[实测]** ★ | `bash state/pcbnew_py.sh -c "import pcbnew;…"` (只读) · 生成器 `:228` |
| 5 | BOM / 网表写 1.27mm (`:71` / `:77` / `:396` / `:399`) ⇒ Δ pitch 0.77 | ★**[实测]** (规格串) ★ | `HW/BOM_v1.csv` · `HW/netlist_v1.csv` · 生成器 `:280` |
| 6 | 「实物 1.27mm 排针按现状落不进」 | ★**[推算]** ★ | 几何推断 (0.50 孔位 vs 1.27 排针) ⇒ ★**不是实测**★ |
| 7 | E-1 = 按 1.27mm 排针定 + 板 land 并进那一趟重画 (main 2026-11-17 18:45 已拍死) | ★**[实测]** (逐字引 pm.yaml) ★ | `state/fragments/pm.yaml` key `main_e1_e2_board_side_rulings_20261117` |
| 8 | 「原始 land pitch = 0.50mm」这个数**不随板变** (板那一趟做完它也不变) | ★**[实测]** (读 main 的裁决原文) ★ | 同上 (生成器 `:329` `read_e1_ruling_baseline()` · ★fail-soft★) |
| 9 | 板 md5 / mtime 全程逐字节未动 ⇒ **零写板** | ★**[实测]** ★ | `logs/iss349/run_iss349_full.log` ①⑦ 段 |
| 10 | 既有覆盖度闸 / ISS-289 闸 / `merge.py` / `gate_check.py` 全 rc=0, Q1 = 18/18 | ★**[实测]** ★ | 同上 ③④⑥ 段 |
| 11 | 沙盒 `make_sandbox` 装的文件清单 (生成器 + 全部真源 + `state/fragments/pm.yaml`) | ★**[实测]** ★ | `HW/check_preflight_regen_idempotent.py:129` |
| 12 | 「板那一趟做完之后, 覆盖度闸 P4 的覆盖令牌 `0.50` 仍在 B33 的 blob 里」 | ★**[推算]** (★已设计保证·未实测·因为板还没改★) ★ | 生成器 `:329` 把「原始值」从 main 的裁决原文现读 ⇒ ★**板改完重跑, 那一句还在** ★ |
| 13 | 1.27mm 排针的实物型号 / 厂牌 / 价格 | ★**[0数据]** ★ | ★**本单不查·不外发·不询价**★ (★本单不碰采购面★) |

---

## B4 · 接口取值声明 (interface_claims) + 新闸的 rc · 入参 · 白名单 · 给 main 的 gate_check 挂载行

### B4-0 · ★接口取值声明 (★本单声明的 4 条接口值·★供 main / SW / MECH 侧对齐用★)★

| key | 取值 | 谁在用 | 出处 (★本机实读★) |
|---|---|---|---|
| `preflight_item_b33_pin_land_pitch` | ★**板读现值 0.50mm ⇒ BOM/网表要求 1.27mm ⇒ Δ 0.77mm** ★ | ★**板那一趟 (S6)** ★ | `state/_iss277_build_preflight.py:228` (板读) + `:280` (BOM/网表读) ⇒ 页 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §7 `B33_PIN_LAND_1P27` |
| `preflight_item_b33_source_iss` | ★**`ISS-290`** ★ | ★**覆盖度闸 P4 的来源单全集** ★ | `HW/check_onepass_preflight_coverage.py:98` (`SOURCES` 含 `ISS-290`) ⇒ ★**不许改成别的号** ★ |
| `preflight_regen_gate_rc` | ★**0 = 全过 · 1 = 闸红 · 2 = 用法错 · 3 = 闸崩** ★ | ★**main 挂进 `state/gate_check.py` 之后** ★ | `HW/check_preflight_regen_idempotent.py:294` (`main`) + `:206` (闸崩) |
| `preflight_regen_gate_env` | ★**`PREFLIGHT_PROJ` / `PREFLIGHT_CHECKLIST` / `PREFLIGHT_GEN_PROJ` / `PREFLIGHT_SANDBOX`** ★ | ★**沙盒与反向用例** ★ | `HW/check_preflight_regen_idempotent.py:56`~`:61` |

★**★这 4 条值的口径 (★给别的总工看★)★**: ★**B33 那一条的现状值 = 【板读】⇒ 不许任何一方把它当常量抄走** ★ · ★**B33 的 id = `B33_PIN_LAND_1P27` = 【生成器里的条目 id】⇒ 页上那条与生成器那条必须同名同源** ★

### B4-1 · 闸文件

| 项 | 内容 |
|---|---|
| 路径 | `HW/check_preflight_regen_idempotent.py` (★499 行·本单新建★) |
| 主模式 | `python3 -B HW/check_preflight_regen_idempotent.py` ⇒ ★**rc=0 全过 / rc=1 闸红 / rc=2 用法错 / rc=3 闸崩**★ |
| 自测 | `python3 -B HW/check_preflight_regen_idempotent.py --selftest` ⇒ 末行 `ALL TESTS PASS` · **rc=0** |
| 辅助 | `python3 -B HW/check_preflight_regen_idempotent.py --makesandbox <目录>` (★只建沙盒·给 run 脚本用★) |
| 实测耗时 | ★**≈1.0 s** (★真跑一次生成器 + 一次沙盒复制·够挂门禁链★)★ |

### B4-2 · 入参 (★全是 env 覆盖·与覆盖度闸同款口径★)

| env | 默认 | 用途 |
|---|---|---|
| `PREFLIGHT_PROJ` | `HW/..` (★项目根★) | 闸读盘的根 |
| `PREFLIGHT_CHECKLIST` | `PROJ/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` | ★**被判的清单页**★ |
| `PREFLIGHT_GEN_PROJ` | `PROJ` | ★**生成器与真源的出处**★ (★R1 指向被改坏的沙盒★) |
| `PREFLIGHT_SANDBOX` | `PROJ/tmp/iss349/regen_gate` | ★**重跑沙盒的落点**★ (★项目盘·绝不落 `/tmp`★) |

### B4-3 · 白名单 (★闸只许碰这些·其余一律只读★)

| 类别 | 白名单 |
|---|---|
| ★**只读** ★ | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/check_onepass_preflight_coverage.py` (★只读它的 `SOURCES`★) · `HW/PCB/demo_mainboard.kicad_pcb` (★在沙盒里读★) · `HW/BOM_v1.csv` · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/SCHEMATIC_LANDING_V1_LANDED.md` · `state/fragments/pm.yaml` (★只读 main 的裁决原文★) |
| ★**只写 (★全在沙盒里★)** ★ | `PROJ/tmp/iss349/**` (★沙盒副本·含沙盒里的板·R4 改它★) |
| ★**真盘只读项 (★一个字都不许改★)** ★ | 板 / `.kicad_pro` / 网表 / 脚表 / BOM / 原理图 / `state/fragments/pm.yaml` / `state/fragments/mech.yaml` / `state/fragments/sw.yaml` / `state/issue_log.yaml` / `state/gate_check.py` / `HW/check_onepass_preflight_coverage.py` / `HW/check_workpack_state_values.py` |
| ★**本单真盘上唯一被写的两个文件** ★ | ① `state/_iss277_build_preflight.py` (★生成器本体★) ② `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★**由生成器产出·不是手改★★)★ |

### B4-4 · ★★给 main 的 `state/gate_check.py` 挂载行 (★那一行由 main 自己挂·本单一个字没动它★)★★

★**挂载点**: `state/gate_check.py:262` 的 `PINNED_MD5_GATES` 列表 (★现有 9 道: 钉板闸①~⑨★) ★
★**建议加的一行 (★原样抄·main 自己贴★)**:

```python
    (os.path.join(PROJ, "HW", "check_preflight_regen_idempotent.py"), "钉板闸⑩ 板侧项全集重跑幂等闸", ()),
```

★**说明 (★给 main 的三点提示★)**:
1. ★**位置**: 紧跟 `钉板闸⑨` (★`state/gate_check.py:271` 那行之后★) ⇒ 变成 **钉板闸⑩** ★
2. ★**为什么值得挂**: ★**它守的是「清单页 == 生成器产物」这条元不变量** ⇒ ★**谁手改页 / 谁删生成器里的条目 / 谁把 `source_iss` 改成不在册的号 ⇒ 当场红** ★
3. ★**代价**: ≈1.0 s/次 (★内部真跑一次生成器·沙盒在项目盘★) ⇒ ★**远小于其他闸** ★; ★**注意它会写 `PROJ/tmp/iss349/` (★沙盒·可随时清★) ⇒ 若 main 嫌 `tmp/` 脏, 可把 `PREFLIGHT_SANDBOX` 指到别的项目盘目录** ★

---

## B5 · 卡点 / 未决 (★本单无阻塞项·以下 3 条是给 main 的提示, 不是本单的未完成项★)

| # | 事项 | 性质 | ★建议 main 怎么处理★ |
|---|---|---|---|
| 1 | ★**覆盖度闸 P4 的覆盖令牌 `0.50`** ★ | ★**前向风险 (★本单已设计规避·但未实测★)★**: 作业包 §0.2 ③ 那一格写着「0.50→1.27mm」⇒ 覆盖度闸 P4 要求 `B33` 的 blob 里含 `0.50` 这个串。★**板那一趟把 land 改成 1.27 之后, 板读值就不再是 0.50** ⇒ ★**本单已把「原始 land pitch = 0.50mm」这一句做成【从 main 的裁决原文现读】(生成器 `:329`) ⇒ 那一句永远在 ⇒ 令牌不会消失** ★ | ★**不用动**·但★**板那一趟跑完、重跑生成器之后, 请 main 亲自核一眼覆盖度闸 P4 仍绿** ★ (★一行命令: `python3 -B HW/check_onepass_preflight_coverage.py`★) |
| 2 | ★**新闸 C4 的必需项清单是写死的** ★ | `REQUIRED_ITEMS = ("B33_PIN_LAND_1P27",)` (★`HW/check_preflight_regen_idempotent.py:65`★) ⇒ ★**以后再加板侧项, 必须往这个清单里加一行, 否则新闸抓不到「新增的那条被删掉」** ★ | ★**走【加严】流程**: 加板侧项 ⇒ 同一单里往 `REQUIRED_ITEMS` 加一行 + 跑 `--selftest` ★ |
| 3 | ★**生成器多了一条对 `state/fragments/pm.yaml` 的读** ★ | 读的是 main 的裁决原文 (★「原始 land pitch」那一句★) ⇒ ★**fail-soft**: 读不到 ⇒ 降级 (那句没进页) + 打印 ⚠ ⇒ ★**不会让生成器拒写页** ★ | ★**若 main 以后把那一句从 pm.yaml 里删了/改了 ⇒ 生成器会降级 (页上少那一句) ⇒ 覆盖度闸 P4 的 `0.50` 令牌就靠不住了** ⇒ ★**那时请 main 同步改覆盖度闸的令牌口径 (★那是覆盖度闸的地界·本单不许动★) ★ |

★**★本单无阻塞项·不依赖老板拍板·零外发★**

---

## B6 · 自证复现命令 (★命令原样输出★)

★**★一条命令复现全部读数: `bash logs/iss349/run_iss349.sh` (★完整日志 `logs/iss349/run_iss349_full.log`·★本节是它的关键段摘录★)★**

### ① 板指纹 (★前后双证★)

```
$ md5sum HW/PCB/demo_mainboard.kicad_pcb
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
$ stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800 4940213
★期望: md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413
```
★**(跑完再读一次: 逐字相同 ⇒ 零写板)**★

### ② 清单页 §2 表 vs §7 JSON 的 id 集合

```
§2 表行数 = 33 · 唯一 id = 33
§7 JSON 条数 = 33 · 唯一 id = 33
两集合逐一相等 ? True
只在表里 = [] · 只在 JSON 里 = []
B33_PIN_LAND_1P27 在表里 ? True · 在 JSON 里 ? True
--- rc=0 ---
```

### ③ 新闸自测 (★端到端跑真生成器★)

```
  PASS  正例 · 沙盒重跑 == 真页 (★零行差异·零蒸发★)
      ★生成器 rc=0 · 沙盒页 md5=581f116a6e41c6c7d6b9290874ade4c5 · 真页 md5=581f116a6e41c6c7d6b9290874ade4c5
  PASS  R1 · 生成器里删掉 B33 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸红并点名「B33 缺失」
      ★闸 rc 判红=True · 点名到 B33=True★
           ❌ 必需板侧项缺失: B33_PIN_LAND_1P27 (★表里没有·JSON 里也没有★) ⇒ ★**生成器里那条被删掉 / 页里那条被手改掉 ⇒ 命中这里** ★
  PASS  R2 · 真页 JSON 里 B33 的 pitch 改成假值 9.99 ⇒ 闸红 (★真页 != 重跑输出★)
      ★闸 rc 判红=True · C2 判红=True · 贴了 diff=True★
           ❌ 真页 != 沙盒重跑输出 ⇒ ★**页与生成器不同源 (重跑会改页)★** ⇒ md5 06a730fed9d7283b03d4d7db0170d055 vs 581f116a6e41c6c7d6b9290874ade4c5
  PASS  R3 · 真页 JSON 里 B33 的 source_iss 改成 ISS-999 (不在 SOURCES) ⇒ 闸红并点名
      ★闸 rc 判红=True · C3 判红=True · 点名到 B33+ISS-999=True★
           ❌ id=B33_PIN_LAND_1P27 的 source_iss='ISS-999' 不在覆盖度闸的 SOURCES 里 ⇒ 来源不明
  PASS  R4 · 沙盒里把板读结果改成 1.27 ⇒ 重跑 ⇒ 页里的现状值【自己】变成 1.27 (★不是死值★)
      ★改板 rc=0 · 生成器 rc=0 · 板读 1.27 ⇒ 页里跟上了=True★
           [实测] 板读 (bash state/pcbnew_py.sh): `J_DEBUG` = pitch 1.27 / 4 脚 / 铜箔 X 142.0625..146.1475 × Y 56.1500..57.0500 (4.0850 × 0.9000); `J_UART` = pitch 1.27 / 2 脚 / 铜箔 X 18.5025..20.0475 × Y 68.1500..69.0500 (1.5450 × 0.9000); BOM/网表写 1.27mm …
  PASS  恢复原件后 · 再跑一次 ⇒ 闸绿 (★不是永远红的闸★)
      ★生成器 rc=0 · 闸全绿=True★
------------------------------------------------------------------------------
  ALL TESTS PASS
--- rc=0 ---
```

### ③ 新闸主模式

```
  OK    C1 表/JSON 同源 (★id 集合逐个相等★)
         §2 表 33 行 (唯一 id 33) · §7 JSON 33 条 (唯一 id 33) · 集合逐一相等: ✔
  OK    C2 重跑幂等 (★真页 == 沙盒重跑输出★)
         真页 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 沙盒重跑输出 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 零行差异: ✔
  OK    C3 来源在册 (★source_iss ∈ 覆盖度闸 SOURCES★)
         33 条 item 的 source_iss 全在 SOURCES (11 个来源单) 里: ✔
  OK    C4 必需项在场 (★加严块★)
         必需项 1 个: ✔
         ✔ 必需板侧项在场: B33_PIN_LAND_1P27 (§2 表 + §7 JSON)
  ✅ rc=0: ★★页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场 ★★
--- rc=0 ---
```

### ④ 既有闸 (★本单一个字未改它们★)

```
$ python3 -B HW/check_onepass_preflight_coverage.py
  OK   P1 / P2 / P3 / P4 / P5 / P6
     ✔ 作业包 §0.2 ③ 的 ③ ⇒ 命中 ['B33_PIN_LAND_1P27'] (覆盖令牌 4 个全在)
     ✔ 受保护 5 件 md5 逐字节不变: ✔
  ✅ rc=0: ★★板侧项全集与作业包对齐, 现状值与盘面一致 ★★
--- rc=0 ---

$ python3 -B HW/check_workpack_state_values.py
  ✅ rc=0: ★★两份文档里的现状值 == 盘面实测, 且七类判据齐 ★★
--- rc=0 ---
```

### ⑤ 蒸发复现 (★沙盒里把生成器的 B33 那条删掉 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸红并点名★)

```
★已写 .../tmp/iss349/run_repro/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md (32 条, 73960 字节)
         真页 md5 = 9f9743c81b977be802322b0966997ee2 · 沙盒重跑输出 md5 = 9f9743c81b977be802322b0966997ee2 · 零行差异: ✔
  FAIL  C4 必需项在场 (★加严块★)
         必需项 1 个: ❌
    ❌ 必需板侧项缺失: B33_PIN_LAND_1P27 (★表里没有·JSON 里也没有★) ⇒ ★**生成器里那条被删掉 / 页里那条被手改掉 ⇒ 命中这里** ★
  ❌ rc=1: ★★闸红 (★上面点名的那几条就是不许过的那几条★) ★★
--- 闸 rc=1 (★非 0 = 判红·正是本单要的★) ---
```

### ⑥ 落表链

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-23T01:50:20+08:00)
--- rc=0 ---

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
【Q7 钉板 md5 闸链】 9/9 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
--- rc=0 ---
```

### ⑦ 生成器本体跑一次的原始输出 (★正式页★)

```
$ python3 state/_iss277_build_preflight.py
★真源读数: {'«R3_T»': '51', '«R3_O»': '40', '«R3_Z»': '40', …}
★ISS-349 · E-1 排针 land 真源读数: 板读 pitch = 0.50 · BOM/网表 = 1.27 · Δ = 0.77 · 原始 = 0.5
★已写 /home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md (33 条, 76862 字节)
★步分布: {'S1': 1, 'S2': 3, 'S3': 2, 'S4': 4, 'S5': 1, 'S6': 10, 'S7': 2, 'S8': 1, 'S9': 1, 'S10': 5, 'S11': 1, 'S12': 1, 'S13': 1}
★缺覆盖的步: []
```

---

## B7 · 边界自证 (★本单一页一页自检★)

### B7-1 · ★写了什么 (★真盘上本单只碰了这些★)

| 文件 | 动作 | 备注 |
|---|---|---|
| `state/_iss277_build_preflight.py` | ★**改** ★ | ★**本单的核心改动** ★: 加 4 个真源读函数 + `ITEMS_RAW` 加 1 条 9 元组 |
| `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` | ★**由生成器重跑产出** ★ | ★**不是手改** (★本单存在的全部理由就是不许手改它★) |
| `HW/check_preflight_regen_idempotent.py` | ★**新建** ★ | 新闸 (499 行) |
| `HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md` | ★**新建** ★ | 本页 |
| `logs/iss349/` | ★**新建** ★ | `logs/iss349/run_iss349.sh` · `logs/iss349/run_iss349_full.log` · `logs/iss349/evidence/` 3 件 |
| `tmp/iss349/` | ★**新建 (沙盒)** ★ | ★项目盘·可随时清★ |
| `state/fragments/hw.yaml` | ★**追加式** ★ | ★**只走 `python3 state/frag_write.py --agent hw-lead`·零 `open(p,"w")`★ ★ |

### B7-2 · ★没碰什么 (★任务书 §2 的边界·逐条自证★)

| ★不许做 ★ | 自证 |
|---|---|
| 写板 / 改板 / 重跑布线 | ★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 前后逐字相同** ★ · R4 改的板**只在沙盒里** |
| 改网表 / 脚表 / BOM / 原理图 / `.kicad_pro` | 覆盖度闸 P6 实跑: ★**受保护 5 件 md5 逐字节不变 ✔** ★ |
| ★**手改 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`** ★ | ★**本单对它的唯一一次写 = 跑生成器** ★ · 新闸 C2 以后每次都会验「页 == 生成器输出」 ⇒ ★**手改从此当场红** ★ |
| 改 `HW/check_onepass_preflight_coverage.py` 的判定逻辑 | ★**一个字节未改** (★新闸只读它的 `SOURCES`★) |
| 改 `state/gate_check.py` / `state/issue_log.yaml` / `state/fragments/pm.yaml` / `state/fragments/mech.yaml` / `state/fragments/sw.yaml` | ★**一个字节未改** (★`state/fragments/pm.yaml` 只被**读** (★裁决原文·fail-soft★)★) ★ |
| ★**沙盒 = `tmp/iss349/sb_base` / `tmp/iss349/regen_gate` / `tmp/iss349/run_repro` (★项目盘·可随时清★)·日志 = `logs/iss349/`·全程 `TMPDIR=$PROJ/tmp/iss349/tmpdir`** ★ ⇒ 零字节落 `/tmp` ★ |
| 外发任何邮件 / 询价 / 问询 / 采购 | ★**本单零外部动作·零外发** ★ |
| 替老板拍板 | ★**本单新增老板拍板项 = 0** ★ · E-1 是 main 2026-11-17 18:45 已拍死的 (★只引用不重拍★) |
| 不许把 `0.50` / `1.27` / 铜箔坐标写死成常量 | ★**生成器里一个都没有** (★全部现读★) · R4 反证 (★板读改 1.27 ⇒ 页里跟着变★) ★ |
| 不许替 main 签字 (`status` 改 `verified`) | ★**本单没写 `status`** ★ (★那是 main 的活★) |

### B7-3 · ★页内引用路径 MISS 自检 (★§5⑤·最近三轮全栽在这条上★)

```
$ cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
$ for p in <本页引用的每个路径>; do [ -e "$p" ] || echo "MISS $p"; done
★MISS 行数 = 0
```

★**本页引用的路径清单 (★逐个已查★)★**: `state/_iss277_build_preflight.py` · `state/_iss277_preflight_appendix.md` · `state/_iss304_ledger_fresh.py` · `state/_iss304_sync_state_baseline_md5.py` · `state/pcbnew_py.sh` · `state/merge.py` · `state/gate_check.py` · `state/frag_write.py` · `state/fragments/hw.yaml` · `state/fragments/pm.yaml` · `state/fragments/mech.yaml` · `state/fragments/sw.yaml` · `state/issue_log.yaml` · `state/dispatch_briefs/ISS-304_hw_workpack_state_values_reanchor.md` · `state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md` · `state/dispatch_briefs/ISS-349_hw_preflight_b33生成器回归_修复.md` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/check_preflight_regen_idempotent.py` · `HW/check_onepass_preflight_coverage.py` · `HW/check_workpack_state_values.py` · `HW/check_netlist_contradiction_r3.py` · `HW/check_pin_function_labels.py` · `HW/BOM_v1.csv` · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/SCHEMATIC_LANDING_V1_LANDED.md` · `logs/iss349/run_iss349.sh` · `logs/iss349/run_iss349_full.log` · `logs/iss349/evidence/page_BEFORE_ISS343_handedit.md` · `logs/iss349/evidence/evaporation_repro.txt` · `logs/iss349/evidence/mksandbox.sh` · `HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md` · `tmp/iss349/` · `tmp/iss349/sb_base/` · `tmp/iss349/regen_gate/` · `tmp/iss349/run_repro/` ★

### B7-4 · ★本单【判据冻结类】的交接口径 (★给 main 的一句话★)

★**板那一趟开工之后, 生成器 (`state/_iss277_build_preflight.py`) / 新闸 (`HW/check_preflight_regen_idempotent.py`) / 清单页 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) 这三件在本单之后不许再改** ★
⇒ ★**板那一趟期间它们给出的读数才有效** ★ ⇒ ★**板改完之后: 跑一次生成器 (让现状值自己变成 1.27) + 跑一次新闸 (C2 应当仍绿) + 跑一次覆盖度闸 (P4 应当仍绿·见 §B5-1★)** ★

---

★**★交卷人 = 硬件总工 (hw-lead) · 2026-11-23 02:0x · 本单零写板 · 零落表 · 零改既有闸判定逻辑 · 零外发 · 不代拍 ★★**

---

# ★★B6-终检 · cont1 追加小节 (★2026-11-23 03:5x · 上一轮 abort 掐在最后一步·本节补齐★) ★

> ★**本节是追加式 · §B0~§B7 老字一字未删** ★
> ★**权威任务书**: `state/dispatch_briefs/ISS-349_hw_preflight_b33生成器回归_cont1.md` ★
> ★**上一轮 (01:4x 派) 的会话在【最后一步】被 abort 掐死 ⇒ 产物其实已落盘, 只差「分片登记 + 终检」两件 ⇒ 本节就是那两件 ★**

## B6-终检-0 · 本续单做了什么 (★三件·逐条自评★)

| # | ★任务书要求 ★ | ★本轮实际做了什么 ★ | ★判定 ★ |
|---|---|---|---|
| 1 | ★**分片登记** ★ | ★**9 条** (2 个 artifact + 1 个 answer + 5 个 interface_claim + 1 个 logs artifact + 1 条 status·另 附项 1 走 `--set-json`) ★ —— ★**全部只走 `python3 state/frag_write.py --agent hw-lead`·零 `open(p,"w")`★** ★ | ✔ **通过** |
| 2 | ★**终检补跑** (★上一轮就死在这★) ★ | ★**新闸主模式 rc=0** ★ + ★**`--selftest` 末行 `ALL TESTS PASS` rc=0** ★ + ★**页内引用路径 MISS = 0** ★ ⇒ ★**原样输出全贴在本节** ★ | ✔ **通过** |
| 3 | ★**交 main 的 3 条 (§B5/B7-4 已写·复核一遍即可) + 附项 1** ★ | ★**§B5 三条复核完毕 (见 B6-终检-6)·§B7-4 口径一字不改 (见 B6-终检-5)** ★ + ★**附项 1 已改: `q3_storage_and_audio` 的 `item` 措辞「外挂 SPI-NOR 16-64MB」→「外挂 SPI-NOR ≥128 MiB (1 Gbit) 起」·只改这一句·`to`/`due`/`since`/`waiting_on` 与其余 240 条 `needs_from` 逐字未动** ★ | ✔ **通过** |

## B6-终检-1 · ★新闸主模式 (★原样输出★)★

```
$ cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
$ export TMPDIR=/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss349/tmpdir
$ python3 HW/check_preflight_regen_idempotent.py
==================================================================================================
  ISS-349 · 「板侧项全集」页【重跑不蒸发】闸 (★C1 表/JSON 同源 · C2 重跑幂等 · C3 来源在册 · C4 必需项★)
==================================================================================================
  PROJ      = /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  CHECKLIST = /home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
  GEN_PROJ  = /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  SANDBOX   = /home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss349/regen_gate
--------------------------------------------------------------------------------------------------
  OK    C1 表/JSON 同源 (★id 集合逐个相等★)
         §2 表 33 行 (唯一 id 33) · §7 JSON 33 条 (唯一 id 33) · 集合逐一相等: ✔
  OK    C2 重跑幂等 (★真页 == 沙盒重跑输出★)
         真页 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 沙盒重跑输出 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 零行差异: ✔
  OK    C3 来源在册 (★source_iss ∈ 覆盖度闸 SOURCES★)
         33 条 item 的 source_iss 全在 SOURCES (11 个来源单) 里: ✔
  OK    C4 必需项在场 (★加严块★)
         必需项 1 个: ✔
         ✔ 必需板侧项在场: B33_PIN_LAND_1P27 (§2 表 + §7 JSON)
--------------------------------------------------------------------------------------------------
  ✅ rc=0: ★★页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场 ★★
--- rc=0 ---
```
★**日志**: `logs/iss349/cont1/01_gate_main.log` ★

## B6-终检-2 · ★新闸自测 (★原样输出·末行 ALL TESTS PASS★)★

```
$ python3 HW/check_preflight_regen_idempotent.py --selftest
==================================================================================================
  ISS-349 · 「板侧项全集」页【重跑不蒸发】闸 (★C1 表/JSON 同源 · C2 重跑幂等 · C3 来源在册 · C4 必需项★)
==================================================================================================
  ★反向用例沙盒: /home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss349/regen_gate
--------------------------------------------------------------------------------------------------
  ★反向用例 (★端到端跑真生成器★):
  PASS  正例 · 沙盒重跑 == 真页 (★零行差异·零蒸发★)
      ★生成器 rc=0 · 沙盒页 md5=581f116a6e41c6c7d6b9290874ade4c5 · 真页 md5=581f116a6e41c6c7d6b9290874ade4c5
  PASS  R1 · 生成器里删掉 B33 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸红并点名「B33 缺失」
      ★闸 rc 判红=True · 点名到 B33=True★
           ❌ 必需板侧项缺失: B33_PIN_LAND_1P27 (★表里没有·JSON 里也没有★) ⇒ ★**生成器里那条被删掉 / 页里那条被手改掉 ⇒ 命中这里** ★
  PASS  R2 · 真页 JSON 里 B33 的 pitch 改成假值 9.99 ⇒ 闸红 (★真页 != 重跑输出★)
      ★闸 rc 判红=True · C2 判红=True · 贴了 diff=True★
           ❌ 真页 != 沙盒重跑输出 ⇒ ★**页与生成器不同源 (重跑会改页)★** ⇒ md5 06a730fed9d7283b03d4d7db0170d055 vs 581f116a6e41c6c7d6b9290874ade4c5
  PASS  R3 · 真页 JSON 里 B33 的 source_iss 改成 ISS-999 (不在 SOURCES) ⇒ 闸红并点名
      ★闸 rc 判红=True · C3 判红=True · 点名到 B33+ISS-999=True★
           ❌ 真页 != 沙盒重跑输出 ⇒ ★**页与生成器不同源 (重跑会改页)★** ⇒ md5 170fca80ea6c3cfd516f0b0c8dbe95b6 vs 581f116a6e41c6c7d6b9290874ade4c5 / ❌ ❌ id=B33_PIN_LAND_1P27 的 source_iss='ISS-999' 不在覆盖度闸的 SOURCES 里 ⇒ 来源不明
  PASS  R4 · 沙盒里把板读结果改成 1.27 ⇒ 重跑 ⇒ 页里的现状值【自己】变成 1.27 (★不是死值★)
      ★改板 rc=0 · 生成器 rc=0 · 板读 1.27 ⇒ 页里跟上了=True★
           [实测] 板读 (bash state/pcbnew_py.sh): `J_DEBUG` = pitch 1.27 / 4 脚 / 铜箔 X 142.0625..146.1475 × Y 56.1500..57.0500 (4.0850 × 0.9000); `J_UART` = pitch 1.27 / 2 脚 / 铜箔 X 18.5025..20.0475 × Y 68.1500..69.0500 (1.5450 × 0.9000); BOM/网表写 1.27mm (`HW/BOM_v1.csv:71` = `
  PASS  恢复原件后 · 再跑一次 ⇒ 闸绿 (★不是永远红的闸★)
      ★生成器 rc=0 · 闸全绿=True★
--------------------------------------------------------------------------------------------------
  ALL TESTS PASS
--- rc=0 ---
```
★**日志**: `logs/iss349/cont1/02_gate_selftest.log` ★

## B6-终检-3 · ★页内引用路径 MISS 自检 (★任务书 §5⑤·最近三轮全栽在这条上★)★

```
$ python3 logs/iss349/cont1/path_miss_check.py --page HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md --out logs/iss349/cont1/04_path_miss_final.txt
★ISS-349 cont1 · 交卷页引用路径 MISS 自检 (★任务书 §5⑤·最近三轮全栽在这条上★)
  被检页 = HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md
  被检路径数 = 41
  OK   HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md
  OK   HW/BOM_v1.csv
  OK   HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
  OK   HW/PCB/BOARD_ONEPASS_WORKPACKET.md
  OK   HW/PCB/demo_mainboard.kicad_pcb
  OK   HW/SCHEMATIC_LANDING_V1_LANDED.md
  OK   HW/check_netlist_contradiction_r3.py
  OK   HW/check_onepass_preflight_coverage.py
  OK   HW/check_pin_function_labels.py
  OK   HW/check_preflight_regen_idempotent.py
  OK   HW/check_workpack_state_values.py
  OK   HW/netlist_v1.csv
  OK   HW/netlist_v1_pins.csv
  OK   logs/iss349/evidence/evaporation_repro.txt
  OK   logs/iss349/evidence/mksandbox.sh
  OK   logs/iss349/evidence/page_BEFORE_ISS343_handedit.md
  OK   logs/iss349/run_iss349.sh
  OK   logs/iss349/run_iss349_full.log
  OK   state/_iss277_build_preflight.py
  OK   state/_iss277_preflight_appendix.md
  OK   state/_iss304_ledger_fresh.py
  OK   state/_iss304_sync_state_baseline_md5.py
  OK   state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md
  OK   state/dispatch_briefs/ISS-304_hw_workpack_state_values_reanchor.md
  OK   state/dispatch_briefs/ISS-349_hw_preflight_b33生成器回归_修复.md
  OK   state/frag_write.py
  OK   state/fragments/hw.yaml
  OK   state/fragments/mech.yaml
  OK   state/fragments/pm.yaml
  OK   state/fragments/sw.yaml
  OK   state/gate_check.py
  OK   state/issue_log.yaml
  OK   state/merge.py
  OK   state/pcbnew_py.sh
  ★MISS 行数 = 0
  --- rc=0 ---
```

★**日志**: `logs/iss349/cont1/04_path_miss_final.txt` · ★**自检脚本**: `logs/iss349/cont1/path_miss_check.py` (★从交卷页正文里抽路径 token·逐个 stat 在盘★) ★

## B6-终检-4 · ★交卷前必跑 (★merge / gate_check / 既有闸 / 板指纹★)★

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-23T03:51:19+08:00)
   产出 746 | 阻塞 43 (高危 33) | 未闭合需求 344 | 冲突 0 | 健康度 red
--- rc=0 ---

$ python3 state/gate_check.py
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 17/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md
   sw-lead    5/6  缺: ['B2']   交接单: 2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-23_mech-lead_ISS345_8脚本迁双口径.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1032 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    396 条

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 9/9 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 4 条
   · hw-lead: 179 条需求确实还没人答 (等另一个总工)
   · sw-lead: 交接单缺 [B2] 验收标准自评 (逐条 通过/不通过/未验)
   · sw-lead: 92 条需求确实还没人答 (等另一个总工)
   · mech-lead: 70 条需求确实还没人答 (等另一个总工)

==========================================================================
--- rc=0 ---
```

### ★★Q1 = 17/18 (★不是 18/18·但★**缺的不是本单**★)★★

★**缺的那 1 格 = `sw-lead` 的 `B2` ⇒ 与本单零关系** ★

| 项 | ★本机实读事实 ★ |
|---|---|
| ★**谁缺** ★ | `sw-lead` 5/6 (缺 `B2` = 「验收标准自评 (逐条 通过/不通过/未验)」) · ★**hw-lead 6/6 · 缺: 无** ★ |
| ★**缺在哪个文件** ★ | `HANDOFF/2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md` (★**1,203 B · mtime 2026-11-23 03:47**★) ⇒ ★**那是 main 在 03:47 预落的骨架** (★文件首行自述: 「★**骨架已由 main 预落·防中途死掉·内容由 sw-lead 填★」★) ★ |
| ★**为什么判缺** ★ | `state/gate_check.py:49` 的 B2 关键词表 = `["验收标准自评", "自评", "验收标准"]` ⇒ ★该骨架的 B2 标题写的是「## B2 改后措辞 (★3 条逐条对照 + 依据★)」·**三个关键词一个都不含** ⇒ 判缺 ★ |
| ★**为什么不回退** ★ | `state/gate_check.py:87` `pick_handoff()` 的规则 ③ (★2026-11-18 main 加的★): ★**自称 B 块结构 ⇒ 缺块就是【倒退】⇒ 不许回退到 7 天内齐备的老单来顶住齐备率** ★ ⇒ ★**这是闸的设计意图·不是 bug** ★ |
| ★**本单为什么不修** ★ | ★**`HANDOFF/` 下 sw-lead 的交接页不是本单的地界** ★ (★任务书 §2 边界: 「只写本单允许的文件·不碰别人的」★) ⇒ ★**本单一个字都没碰 sw-lead 的页** ★ ⇒ ★**这一格要 sw-lead 自己把 B2 填出来** ★ |

★**给 main 的一句话**: ★**Q1 从 18/18 掉到 17/18 的时刻 = 03:47 (main 预落 sw-lead ISS-350 骨架那一分钟)·不是本单造成的 (本单只写 hw.yaml + 本页 + logs/iss349/)·hw-lead 那一格 6/6 缺: 无 ⇒ 等 sw-lead 把 ISS-350 的 B2 填了就会回 18/18** ★

★**日志**: `logs/iss349/cont1/07_merge_gate_check.log` ★

### ★既有闸不许被本单弄红 (★本单一个字未改它们★)★

```
$ python3 HW/check_onepass_preflight_coverage.py
  OK   P1 / P2 / P3 / P4 / P5 / P6
     ✔ 作业包 §0.2 ③ 的 ③ ⇒ 命中 ['B33_PIN_LAND_1P27'] (覆盖令牌 4 个全在)
     ✔ 受保护 5 件 md5 逐字节不变: ✔
  ✅ rc=0: ★★板侧项全集与作业包对齐, 现状值与盘面一致 ★★
--- rc=0 ---

$ python3 HW/check_workpack_state_values.py
  ✅ rc=0: ★★两份文档里的现状值 == 盘面实测, 且七类判据齐 ★★
--- rc=0 ---
```

### ★板指纹 + 受保护 5 件 (★零写板 · 零落表 ★)★

```
$ md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800 4940213

$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
```
★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` ⇒ 与 2026-11-23 01:4x 那一轮开工前逐字节相同 ⇒ 零写板** ★
★**日志**: `logs/iss349/cont1/09_existing_gates_and_md5.log` ★

## B6-终检-5 · ★§B7-4 交接口径复核 (★一字不改·原样转述给 main★)★

★**§B7-4 原文 (★本轮只复核·一字未改★)**:

> ★**板那一趟开工之后, 生成器 (`state/_iss277_build_preflight.py`) / 新闸 (`HW/check_preflight_regen_idempotent.py`) / 清单页 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) 这三件在本单之后不许再改** ★
> ⇒ ★**板那一趟期间它们给出的读数才有效** ★ ⇒ ★**板改完之后: 跑一次生成器 (让现状值自己变成 1.27) + 跑一次新闸 (C2 应当仍绿) + 跑一次覆盖度闸 (P4 应当仍绿·见 §B5-1★)** ★

★**本轮复核结论**: ★**该口径本轮一字未改·且本轮已经把它写进 `state/fragments/hw.yaml` 的 interface_claim `iss349_preflight_regen_idempotent` 的 `note` 里 ⇒ merge 之后 main / SW / MECH 三侧都能在 STATE.yaml 里读到这条「判据冻结」口径 (★上一轮它只存在于本页正文·merge 读不到·这正是本续单存在的理由★)** ★

## B6-终检-6 · ★§B5 三条复核 (★给 main 的提示·不是本单的未完成项★)★

| # | §B5 原文要点 | ★本轮复核 (★本机实读★) ★ | ★本轮处置 ★ |
|---|---|---|---|
| 1 | ★**覆盖度闸 P4 的覆盖令牌 `0.50`** 是前向风险 ⇒ 已做成「从 main 裁决原文现读」⇒ 令牌不会消失 ★ | ★**本轮实跑覆盖度闸 P4: `✔ 作业包 §0.2 ③ 的 ③ ⇒ 命中 ['B33_PIN_LAND_1P27'] (覆盖令牌 4 个全在)` ⇒ 令牌现值仍在** ★ | ★**不用动** ★ · ★板那一趟跑完、重跑生成器之后 main 亲自核一眼 P4 仍绿 (★`python3 -B HW/check_onepass_preflight_coverage.py`★) ★ |
| 2 | ★**新闸 C4 的 `REQUIRED_ITEMS` 是写死的** ⇒ 以后再加板侧项必须同一单里往里加一行 + 跑 `--selftest` ★ | ★**本轮实读 `HW/check_preflight_regen_idempotent.py:65` ⇒ `REQUIRED_ITEMS = ("B33_PIN_LAND_1P27",)` (★1 项·与 §B7-4 的冻结口径一致·本轮未改★)** ★ | ★**走加严流程** ★ |
| 3 | ★**生成器多了一条对 `state/fragments/pm.yaml` 的读** (★fail-soft·读不到就降级并打 ⚠·不让生成器拒写页★) ★ | ★**本轮实跑生成器 rc=0 + 新闸 C3 `33 条 item 的 source_iss 全在 SOURCES (11 个来源单) 里: ✔` ⇒ 降级路径当前【未被触发】** ★ | ★**若 main 以后改了 pm.yaml 那一句 ⇒ 生成器降级 ⇒ 覆盖度闸 P4 的 `0.50` 令牌就靠不住了 ⇒ 那时 main 要同步改覆盖度闸的令牌口径 (★那是覆盖度闸的地界·本单不许动★)** ★ |

★**★§B5 三条本轮全部复核完毕 · 本单无阻塞项 · 不依赖老板拍板 · 零外发 ★★**

## B6-终检-7 · ★分片登记明细 (★9 条 + 附项 1★)★

★**写入通道**: ★**只有 `python3 state/frag_write.py --agent hw-lead` (★零 `open(p,"w")` 手写 YAML★)** ★

| # | 类别 | ★key / path ★ | ★落点 ★ |
|---|---|---|---|
| 1 | artifact | `HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md` (kind=handoff · v1.0) | `state/fragments/hw.yaml` → `artifacts` |
| 2 | artifact | `HW/check_preflight_regen_idempotent.py` (kind=gate · v1.0) | `state/fragments/hw.yaml` → `artifacts` |
| 3 | artifact | `logs/iss349/` (kind=log · v1.0) | `state/fragments/hw.yaml` → `artifacts` |
| 4 | answer | `iss349_preflight_b33_generator_fixed` → `to=main` | `state/fragments/hw.yaml` → `answers` |
| 5 | claim | `iss349_preflight_regen_idempotent` (★判据冻结口径★) | `state/fragments/hw.yaml` → `interface_claims` |
| 6 | claim | `preflight_regen_gate_rc` = `0 = 全过 · 1 = 闸红 · 2 = 用法错 · 3 = 闸崩` | `state/fragments/hw.yaml` → `interface_claims` |
| 7 | claim | `preflight_item_b33_pin_land_pitch` (板读 0.50 ⇒ BOM/网表 1.27 ⇒ Δ 0.77) | `state/fragments/hw.yaml` → `interface_claims` |
| 8 | claim | `preflight_item_b33_source_iss` = `ISS-290` | `state/fragments/hw.yaml` → `interface_claims` |
| 9 | claim | `preflight_regen_gate_env` (4 个 env) | `state/fragments/hw.yaml` → `interface_claims` |
| + | status | `phase=iss349-delivered` · `progress_pct=100` · `health=green` | `state/fragments/hw.yaml` → `status` |

★**★零重复 key 自证 (★本轮实跑★)★**: ★`iss349` 在改前命中 = 0 ★ ⇒ ★**6 个 key 各命中恰好 1 次** ★ (★`iss349_preflight_b33_generator_fixed`=1 · `iss349_preflight_regen_idempotent`=1 · `preflight_regen_gate_rc`=1 · `preflight_item_b33_pin_land_pitch`=1 · `preflight_item_b33_source_iss`=1 · `preflight_regen_gate_env`=1★) ★ ⇒ ★**没有新建第二条** ★

★**日志**: `logs/iss349/cont1/03_frag_write.log` · ★**登记脚本 (★可复现★)**: `logs/iss349/cont1/frag_write_iss349.sh` ★

## B6-终检-8 · ★附项 1 · `q3_storage_and_audio` 容量口径订正 (★同一分片·零写板★)★

### ★改了什么 (★只改这一句措辞★)★

| 项 | ★改前 ★ | ★改后 ★ |
|---|---|---|
| `item` | `Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR 16-64MB, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)` | `Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR ≥128 MiB (1 Gbit) 起, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)` |

### ★没改什么 (★本机实跑自证·逐字对照★)★

★**`needs_from` 241 条 ⇒ 改前 241 / 改后 241 (不增不减) · 逐条 diff = 只有 index 5 (`q3_storage_and_audio`) 的 `item` 一个字段变了** ★

```
[OK] needs_from 条目数 = 241 (改前 241 · 不增不减)
[OK] 目标条目 index = 5 · key = q3_storage_and_audio
[OK] 改动字段 = ['item'] (只有 item)
[OK] item 改前 = Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR 16-64MB, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)
[OK] item 改后 = Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR ≥128 MiB (1 Gbit) 起, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)
[OK] 字段 key         = 'q3_storage_and_audio' (逐字未动)
[OK] 字段 to          = 'boss' (逐字未动)
[OK] 字段 due         = '2026-10-27' (逐字未动)
[OK] 字段 since       = '2026-10-25' (逐字未动)
[OK] 字段 waiting_on  = 'boss' (逐字未动)
```

★**写入通道**: ★**`python3 state/frag_write.py --agent hw-lead --set-json logs/iss349/cont1/needs_from_after.json --set-field needs_from`** (★原子替换整段 `needs_from`·中间件由 `logs/iss349/cont1/q3_item_fix_prep.py` 生成并自检过「只有 item 变」★) ★
★**改前快照 (★可回滚★)**: `logs/iss349/cont1/hw.yaml.before_setjson` (★md5 `8ed849e3f7ee165f4db5ae64231d1917`★) ★
★**日志**: `logs/iss349/cont1/05_q3_item_fix_prep.log` · `logs/iss349/cont1/06_q3_item_fix_setjson.log` ★

### ★依据 (★证据分级标齐★)★

| ★依据 ★ | ★证据等级 ★ | ★出处 (★本机实读★) ★ |
|---|---|---|
| ★**flash ≥128MB 是 SW 总工在 ISS-080 锁死的硬约束** (★`rootfs ≤30MB` ⇒ 64MB SPI-NOR 装不下★) ★ | `[实测]` (★仓内既有台账逐字★) ★ | `HW/SCHEMATIC_V1.md:282` · `HW/SCHEMATIC_V1_1_CHANGELOG.md` C10 · `HW/SOC_PIN_BUDGET.md:71` (★「若外挂 → sw-lead §4.1 分区表要 ≥128MB SPI-NOR (64MB 实测 FAIL)」★) ★ |
| ★**Winbond 料号里的数字是 Mbit 不是 MB** ⇒ `W25Q64` = 64 Mbit = **8 MB** · `W25Q256` = 256 Mbit = **32 MB** ⇒ 老板拍板页现写的「16~64 MB」在【容量维度】和【料号维度】两层都错 ★ | `[官网]` (★料号密度线 8Mb~2Gb·W25Q256JV = 256 Mbit / 32 MB·V 2.7~3.6 V·与 `VDD_3V3_IO` 匹配★) ★ | `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md:165`~`:166` ★ |
| ★**ISS-346 机器判决: 5×4 容量矩阵 20/20 格跑通** ⇒ 64MB NOR 整列作废 (★rootfs 20/30/40/64 MB 四档全 FAIL★) ⇒ ≥128 MiB 起 | `[实测]` (★`flash_layout_check.py` 原始输出★) ★ | `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md` §B2-1/§B2-2 (★矩阵脚本 `SW/tools/gen_storage_capacity_matrix.py`★) ★ |
| ★**ISS-346 原文就点名要订正这一行** ⇒ 「★**顺带订正同一行的容量口径** ⇒ 现写「外挂 SPI-NOR 16~64 MB」⇒ 建议改为「**≥128 MiB (1 Gbit) 起的 SPI-NOR**」」 ★ | `[实测]` (★逐字★) ★ | `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md:340` ★ |

★**★这一句是【老板拍板页 §① 第 6 行】的口径来源 ⇒ 不改 ⇒ 老板看到的题面是错的 ⇒ 本单必须改** ★
★**★本单不替老板拍板**: ★**只把「容量下限」从错值订正成 ISS-080 已锁死的值 (★128MB 那道门槛早就有 SW 总工签过字★)·§B5 那条 `> 64 MiB ⇒ 必须 eMMC` 的口径冲突带 (★ISS-346 §B2-2 点名的「需总工/老板裁决」★) ★**本单一个字都没碰、也没替老板裁** ★** ★

## B6-终检-9 · ★本轮零写板 / 零落表 / 零改闸 / 零外发 自证 (★cont1 增量部分★)★

| ★不许做 ★ | ★自证 (★cont1 增量★) ★ |
|---|---|
| ★**写板 / 改板 / 重跑布线** ★ | ★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` ⇒ 与 01:4x 开工前逐字节相同** ★ (★本轮只在 `tmp/iss349/regen_gate/` 沙盒里跑过 R4 的改板★) ★ |
| ★**改网表 / 脚表 / BOM / 原理图 / `.kicad_pro`** ★ | ★**受保护 5 件 md5 逐字节不变 (★覆盖度闸 P6 + 现状值闸 V6 两道闸实跑确认✔★)** ★ |
| ★**手改 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`** ★ | ★**本轮对它的写 = 0 次** ★ (★只有新闸在沙盒里生成副本·真页 md5 `581f116a6e41c6c7d6b9290874ade4c5` 全程未变★) ★ |
| ★**改既有闸的判定逻辑** ★ | ★**`HW/check_onepass_preflight_coverage.py` / `HW/check_workpack_state_values.py` / `state/gate_check.py` 一个字节未改** ★ |
| ★**写别人的分片** ★ | ★**只写 `state/fragments/hw.yaml`** ★ (★`pm.yaml` / `mech.yaml` / `sw.yaml` / `issue_log.yaml` 只读未写★) ★ |
| ★**改 `state/issue_log.yaml`** ★ | ★**未改** ★ (★签收是 main 的活★) ★ |
| ★**外发任何邮件 / 询价 / 问询 / 采购** ★ | ★**本轮零外部动作·零外发** ★ ⇒ ★缺口全部【自己网上查/仓内实读】+ 标证据等级 (★附项 1 的三条依据全部是仓内逐字台账 + sw-lead 交卷页 + 官网料号口径·没有一条靠印象★) ★ |
| ★**替老板拍板** ★ | ★**本轮新增老板拍板项 = 0** ★ (★附项 1 只是把已锁死的容量下限写对·不是新决策★) ★ |
| ★**不许替 main 签字 (`status` 改 `verified`)** ★ | ★**本轮只把 `status.phase` 写成 `iss349-delivered`·`verified` 没碰** ★ |
| ★**沙盒 / 日志落 `/tmp`** ★ | ★**全程 `TMPDIR=$PROJ/tmp/iss349/tmpdir`·沙盒在 `tmp/iss349/`·日志在 `logs/iss349/`·零字节落 `/tmp`** ★ |

---

★**★交卷人 = 硬件总工 (hw-lead) · 2026-11-23 03:5x · ISS-349 cont1 (续单收尾) · 本单零写板 · 零落表 · 零改既有闸判定逻辑 · 零外发 · 不代拍 ★★**
★**★上一轮 (01:4x) 的交卷页内容一字未删; 本节是追加式补齐「分片登记 + 终检」两件 ★★**
