# ISS-326 · mech-lead · ★★【cont1 续做 · 扫描已做完, 补实证与设计稿】★★

> ★**这是续做, 不是从零重做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 14:5x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: mech-lead (结构总工) · ★**verify_by**: main · ★**单号**: ISS-326 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯分析 + 沙盒实跑类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★

---

## ★★★【★★先读这一段: 上一趟扫描已经做完了 ★★★】★★★

★**★上一趟 (14:23~14:27) 的会话被父 cron run 连带 abort, 但 【扫描这一段已经做完了】★★** ⇒ ★**★你的活是从「有清单」走到「有实证 + 有设计稿」, 不许重扫★ ★**

★**★main 14:5x 本机实读 (★不抄任何 agent 报告★) —— 上一趟留下的产物 (★全部可复用★)★★**:

| 产物 | ★读数★ | ★**它已经答了什么** ★ |
|---|---|---|
| ★`logs/iss326/iss326_scan_mech_refs.py` ★ | 13,682 B | ★**扫描脚本** ★ |
| ★`logs/iss326/mech_ref_hits.tsv` ★ | ★**577,679 B · 1,935 行 · 63 个 distinct 文件** ★ | ★**逐命中表**: `file / line / hit_kind / file_class / ref / new_ref / move / context` ★ ⇒ ★**★清单这一半【已经做完】★** ★ |
| ★`logs/iss326/mech_ref_universe.json` ★ | 41,049 B | ★**改名真集 + 保持集** (★dict 4 键: `count` / `keep` / `move` / `universe`★) ★ |
| ★`logs/iss326/iss326_reconcile_counts.py` + `iss326_reconcile2.py` ★ | 2,722 B + 3,015 B | ★**对账脚本** (★顶层 vs 递归两个口径★) ★ |
| ★`logs/iss326/reconcile_counts_raw.txt` ★ | 3,858 B | ★**对账读数 (★见下★)** ★ |
| ★`logs/iss326/scan_raw.txt` / `scan_stdout.txt` ★ | 4,837 B 各 | ★**扫描原始输出** ★ |

★**★★main 已核的关键对账读数 (★这是你这一趟的起点★)★★**:
★**扫描面 = 顶层 (`MECH/*.md` + `MECH/*.py`) = 递归 (`MECH/**/*.md` + `MECH/**/*.py`) ⇒ 文件数都是 112 ⇒ 两者【相同】⇒ ★**MECH 域没有子目录里的 md/py·所以「递归全量」这个口径【已经满足】★ ★**
★**口径A (精确真集命中·出现次数) = 1,934** ★ · ★**口径B (精确真集命中·命中行数) = 1,282** ★ · ★**口径C (形状像位号 token·次数) = 7,553** ★
★**★⇒ ★**这三个数与 main 上一轮自己 grep 出来的「顶层 571 处」差很多 ⇒ ★**★说明「571」那个数用的是【另一种口径】(★main 当时数的是 `MECH/*.md` + `MECH/*.py` 里的特定前缀白名单命中★) ⇒ ★★你的 1,934 是【精确真集】口径 ⇒ ★★【两个数口径不同, 不是矛盾, 但交卷页必须把口径写清楚★】⇒ ★**main 的 571 是【前缀白名单】口径, 你的 1,934 是【精确真集】口径 ⇒ ★**★交卷页必须两个都给, 并说明差在哪★★ ★**

★**★TOP 文件 (口径A)★**: `BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 189 · `ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` 151 · `BOARD_ONEPASS_MECH_SYNC.md` 134 · `BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 130 · `USB_HINGE_STRUCTURE.md` 120 · `BOARD_ONEPASS_MECH_CLAIMS.md` 81 · `BOARD_PORT_OPENING_S6_WORKPACKET.md` 68 · `HINGE_FPC_GEOMETRY_TRUTH.md` 64
★**★口径C 的 TOP 里有三个【main 上一轮没预料到的】**: `MECH/cavity_recalc_check.py` 497 (★口径A=0★) · `MECH/verify_budget.py` 397 (★A=7★) · `MECH/iss065_check.py` 315 (★A=31★) ⇒ ★**这三份是【形状像位号但不在真集里】的 ⇒ 它们【不在改名风险面】, 但【长成位号样】⇒ 交卷页要说明「口径C 与口径A 的差 = 假阳性的规模」★ ★**

---

## ★★① 上一趟已经做完的 (★不许重做★) ★★

★**★① 全量命中表 (`mech_ref_hits.tsv`, 1,935 行) ★★ — ★**不许重扫** ★
★**★② 改名真集 (`mech_ref_universe.json`) ★★ — ★**不许重算** ★
★**★③ 三个口径的对账读数 (`reconcile_counts_raw.txt`) ★★ — ★**不许重跑** ★

---

## ★② 这一趟真正要做的三件 (★核心是「崩 vs 假绿」的实证★)

### ★②-1 · ★★「崩 / 假绿」逐条沙盒实证 (★★不许只做静态推断★★)

★**★main 已经在源码里看到两处【真的会出事的点】, 你必须把它们的真实失败形态跑出来★**:
- ★**`MECH/check_board_frame_coords.py` L963~L964 用的是 `fps.get(RES_REF)` / `fps.get(LED_REF)` (★安全·找不到返回 None★) ⇒ ★**但 L999 是 `led = fps[LED_REF]` (★直接下标 ⇒ 改名后 KeyError★) ⇒ ★**同一个文件里两种写法 ⇒ 崩溃点不在直觉上** ★
- ★**`MECH/check_onepass_struct_crosscheck.py` L1107 / L1129 是 `if t["ref"] == "R_SEL_D0_N":` / `== "R_SEL_D1_N"` ⇒ 改名后【再也匹配不上】⇒ ★**不是崩, 是【那条判据从此不生效】= 假绿**** ★★

★**★沙盒怎么跑 (★不许碰项目真文件★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★沙盒 1: 把 MECH 域 + 它读的网表/脚表整棵树复制到 tmp/iss326/ 下
# ★沙盒 2: 在沙盒副本里做「改名」—— ★★★只改【脚本里硬编的 ref 字符串】, 不许改真件★★
# ★沙盒 3: 在沙盒副本里跑【改名前】与【改名后】两遍 ⇒ 逐条贴 rc + 关键输出行
# ★★铁律: 要验证「改名后」的行为, 就把脚本 + 它读的数据整棵树复制过去再改
#        —— 不许在真文件上改、改完再改回来 (★那叫擦产物, 不叫验证★)★★
```
★**★至少挑 3 个脚本 (★一个「会崩的」· 一个「会假绿的」· 一个「只是文档叙述的」★) 实跑两遍★**

★**★反例必须自己抓 (★这是本单最值钱的一段★)**: ★**至少 4 条反向用例, 每条贴「期望红/绿」与「实际红/绿」★** ⇒ 例如:
★**① 把 `R_SEL_D0_N` 改成别的名字 ⇒ 那条判据【必须变成不匹配】⇒ 你要证明它【红不出来】(假绿) ★**
★**② 把 `D_LED_G` 改掉 ⇒ `fps[LED_REF]` 必须抛异常 ⇒ 你要贴出异常类型与那一行 ★**
★**③ 改一个【不该改的】ref (★`J_SOM_P1` —— ★它在改名表的【不动的 32 个】里★) ⇒ 闸必须【不受影响】⇒ 证明你没误伤 ★**
★**④ 注释里的 ref 名改成别的 ⇒ 闸必须【不受影响】(★功能零变化★) ⇒ 证明「注释里的 ref【不需要改】」这条结论 ★**

### ★②-2 · ★★把命中表升级成【可用的清单】 (★不重扫, 只做分类与归并★)

★**★`mech_ref_hits.tsv` 已经有 `file_class` / `move` 两列 ⇒ 你要做的是【把 1,935 行归并成【按文件的处置表】】★★**
★**★每行 = (文件 · 硬编 ref · 改名后 ref · 命中上下文 · ★**失效形态**★)** ★
★**★失效形态三选一, 必须逐条判, 不许留空★**:
| 形态 | ★含义★ |
|---|---|
| ★**`崩`** ★ | ★`KeyError` / `TypeError` / `IndexError` ⇒ 脚本直接挂 ★ |
| ★**`静悄悄不查了`** ★ | ★判据分支再也匹配不上 ⇒ 【假绿】⇒ ★**★这是最坏的一类⇒ 必须排在前面★★** ★ |
| ★**`只是文档叙述`** ★ | ★改了也不影响判据 (★含注释里的 ref 名★) ★ |

★**★★三条硬要求★★**:
1. ★**★判据脚本 和 一次性/归档脚本 必须分开列★** ⇒ ★**`MECH/_apply_*.py` / `_frag_update_*.py` / `rebase_*.py` 这类【历史落地脚本】里的硬编 ref 【不需要改】(★它们跑完就没了★) ⇒ ★**列出来但标成「历史脚本 · 不改」**, 不许混进「要改」清单 ★
2. ★**★注释里的 ref 名必须单独标出来 (「注释 · 无功能影响」)★** ⇒ ★**main 上一轮已经在 ISS-320 交卷里见过同型事故 (`MECH/service_port_check.py` L51 的型号名在注释里, 被 md5 钉死 ⇒ 改不了·也不该改)** ★
3. ★**★`file_class` 这一列要核一遍★** ⇒ ★**main 抽查了第一行: `MECH/BOARD_FRAME_DECISION_INPUT.md:79` 命中 `TP_DSI_CK_N` · `file_class=文档` · `move=改名` ⇒ 分类口径对得上 ⇒ ★**但 1,935 行里有没有【判据脚本被误标成文档】的, 你要自己核★ ★

### ★②-3 · ★★「MECH 侧位号可达性闸」设计稿 (★只给设计 + 反向用例, ★★不许挂进 `state/gate_check.py`★★)

★**★因为 SW 侧已经有同款 (`SW/tools/check_sw_ref_reachability.py`), MECH 侧要抄的应该是【那个闸的判据口径】, 而不是重写一个弱版★** ⇒ ★**你必须先读它的源码, 再写 MECH 版的设计稿★** ★
★**设计稿里必须包含**: ★① 扫描面 (★`MECH/**/*.py` + `MECH/**/*.md` 递归 · **不许只扫顶层**★) ★② 分类口径 (★照抄 SW 那道的 C1/C2/C14 三类 + 冻结注册表的建闸日基线机制★) ★③ **fail-closed 三条** (★照 SW 那道的口径: 取不准必须判红, 不许放宽成「取最近一条」★) ★④ 反向用例 ≥ 5 条 ★⑤ **基线数怎么定** (★SW 那道建闸日 `DESIGNATOR_MISSING` = 3 条 ⇒ MECH 版建闸日基线必须自己 fresh 测, **不许抄 3**★) ★
★**★不许写 `state/gate_check.py` (★挂闸是 main 的机制地界★) ⇒ 只交设计稿 + 「建议挂进 `EXTRA_GATES` 的第几位 + 逐字写法」★**

---

## ★③ 交卷物 (4 件)

1. ★**主交付物** ★`MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` (★§0~§7 全填 · 占位符 0★)
2. ★**交卷单** ★`HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md` (★B0~B6 齐全★)
3. ★**证据目录** ★`logs/iss326/` (★★已有 8 件, 续做时【追加】不许覆盖★ ★)
4. ★**分片** ★`state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写 · ★**禁 `open(p,"w")`**★ · artifacts / needs_from / interface_claims 各 ≥1 · status 换 ISS-326★)

★**★主交付物 §0 必须写清「上一趟已做完什么 / 这一趟补了什么」 (★给下一个接手的人看·★也证明你没有重做★)** ★

---

## ★④ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**零改闸** (★`MECH/*.py` 一个字都不许改 —— 本单只出体检 + 设计稿★) · ★**零改既有文档正文** (★`MECH/**` 既有 md 只读★) · ★**沙盒只写 `tmp/iss326/` + `logs/iss326/`** ★ · ★**只写 `state/fragments/mech.yaml`** ★ · ★**零改 `state/gate_check.py`** ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★ · ★**不许把整份大文件读进来** (★只 grep 你要查的行★)
★**★★★⇒ ★★沙盒里做「改名后」的行为, 必须把【脚本 + 它读的数据】整棵树复制过去再改 —— 不许在真文件上改·改完再改回来 (★那叫擦产物, 不叫验证★)★★ ★**

---

## ★⑤ 交卷前必跑 (★原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py
python3 MECH/check_board_frame_coords.py
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

## ★⑥ 纪律 (★这项目的老教训·今天连踩两遍★)

★**① ★★先落盘, 再干活★★** (★上一趟被 abort ⇒ ★**这一趟第一件事就是 `write` 建交卷页骨架 + 把 §0 的「上一趟已做完什么」写出来★) ★ · ★**② 长任务一律 `nohup ... > logs/iss326/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**③ 单条 `exec` ≤ ~120 秒** ★ · ★**④ 每 10 分钟至少一次写盘** · ★**⑤ 分片写完 `grep` 校验** · ★**⑥ ★★沙盒脚本跑之前, 先 `find <沙盒root> -type l` 确认没有软链 (★兄弟 job 那趟就是栽在软链写穿真件上·★虽说是 SW 侧的事, 但这条纪律一样适用·★不许重蹈★)★★ ★**
