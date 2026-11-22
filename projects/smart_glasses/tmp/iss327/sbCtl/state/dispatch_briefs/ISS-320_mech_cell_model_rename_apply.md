# ISS-320 · mech-lead · 任务书 —— ★★【电芯型号订正【实做】: 把 ISS-319 查清的那 47 行里的 33 行【真改掉】, 只换型号名, 尺寸一个字不许动】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-320
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 09:1x** ★
> ★**性质**: ★**内部活 · 受限文本订正类 (★MECH 域 33 行 / 19 个文件·含 9 个脚本★) · 零写板 · 零落表 · 零重生成 · 零改闸 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★0 · ★为什么是这一单 (★main 09:1x 本机实读·不抄任何 agent 报告★) ★

★**① ISS-319 (verified · 本轮刚落地) 把影响面查清了**: ★**全量扫描 = 47 行 / 22 个活文件 (`.md` 13 文件 35 行 · `.py` 9 文件 12 行)**, 其中 ★**36 行「可改行」(口径行 + 脚本行) + 11 行「留证/对照行」(两型号并置 ⇒ 语义上是证据 ⇒ 一行都不许动)**★ ★

★**② main 已拍板 (★需求 `iss319_cell_model_rename_scope` ⇒ 现在就做★)**: ★**照现型号 `ICP582035PR-01` 下采购单 ⇒ 到货厚 6.40mm (不是 4.60mm) ⇒ 装不进 7.30mm 镜脚 ⇒ 电芯段 H 链最坏 −1.10mm ⇒ 这笔损失远大于任何文档订正本身 ⇒ 且它与 U-1 板框决策【完全无关】⇒ 可以并行走, 越早越省钱** ★

★**③ 官网读数 (★`[官网]`· renata.com 锂聚合物电池页·ISS-313 已核·零外发★)**:
```
Renata ICP422339PR     : 340 mAh / 4.6mm 厚 / 23.5 / 40.5   ← ★真型号 (项目一直按它的尺寸在算)★
Renata ICP582035PR-01  : 340 mAh / 6.4mm 厚 / 20.5 / 37     ← ★项目把 4.6×23.5×40.5 错挂在它名下★
```

★**④ 归属切分 (★本单只碰 MECH 域★)**: ★**HW 域那 3 行 (`HW/POWER_BUDGET_V3.md` L27/L259 · `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` L1046) 由 main 自己改 (★本机实读: 这两个文件没有被任何 md5 闸钉住·可安全改★) ⇒ ★**本单 = MECH 域 33 行 / 19 个 MECH 文件**★ ★

---

## ★1 · ★★本单的核心判据: 【只做一次全量字符串替换】(★最强判据·机器判★) ★★

★**允许的唯一改动** = 把 `ICP582035PR-01` 这个字符串替换成 `ICP422339PR` ★**其它任何字符都不许动** ★

★**⇒ 机器判据 (★照这个判, 别自己发明判法★)**: ★**每个改后文件 == 它的「改前内容做一次全量字符串替换」的期望版本 ⇒ 逐字节相同** ★
★**⇒ 最强的一条 (★这条不许绕过★)**: ★**每个改后文件里【除型号名之外】的所有数字序列必须与改前逐位相同 (★`4.60` / `23.50` / `40.50` / `340 mAh` / `4.38 cc` / `78 mAh/cc` / `0.87 W` / `1.258 Wh` / `260 Wh/kg` / `105.5 mm` / `7.3 mm` / `49.58` / `74.16` / `48.90` / `72.80` 等, 一个数都不许变★)** ⇒ ★**⇒ 「几何与重量结论零变化」这句话是机器判的, 不是人说的** ★

★**⇒ 扫完的期望读数 (★ISS-319 已给出机器判据★)**:
```bash
grep -rn "ICP582035PR-01" MECH/ --include="*.py" --include="*.md" \
  | grep -v "/tmp/\|\.trash/\|\.bak_\|ONETRIP_MECH_DIFF_OWNERSHIP.md" \
  | tee logs/iss320/cell_model_scan_after.txt
echo "命中行数 = $(wc -l < logs/iss320/cell_model_scan_after.txt)"   # ⇒ 期望 11 (只剩留证行)
echo "命中文件数 = $(awk -F: '{print $1}' logs/iss320/cell_model_scan_after.txt | sort -u | wc -l)"
```
★**★注意**: ★**`MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` (ISS-319 的交卷页) 必须排除在扫描之外** ★★ ⇒ ★**它自己逐字引用了 47 行的「现行 + 改后」两遍 ⇒ 不排除的话命中数会变成 119 (★ISS-319 已实测过这个坑★)★ ★**★同理, 本单自己的交卷页也要排除 (★命令里把你自己的文件加进排除列表★)★**

---

## ★2 · ★逐条清单在哪儿 (★别重扫·别手抄·直接用机器生成的表★) ★

★**权威表 (★ISS-319 机器生成·47 行一条不漏·逐字摘抄自活文件★)**:
- `logs/iss319/cell_rename_table.md` (★41,808 B·含「这行现在写的是什么 (逐字)」+「应该改成什么 (逐字改法)」+「数字指纹」+「改完会不会连带影响别的东西」四列★)
- `logs/iss319/cell_model_scan_raw.txt` (★基线扫描原始输出★)
- `HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md` §B1-2 (★47 行逐条改法全表★)
- `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` §2 (★影响面 / 分类 / 逐条改法★)

★**★11 行「留证/对照行」= 一行都不许动 (★这份清单就是护栏★)**:
```
MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md  L280 / L321 / L323 / L324 / L326 / L368   (6 行·两型号并置的对照语义)
MECH/MECH_BUDGET.md                       L867                                      (带日期的历史更正记录)
MECH/MECH_NEEDS_TRIAGE.md                 L163 / L362                               (官网规格对照行)
MECH/_close_iss065.py                     L66                                       (ISS-065 结案脚本的一次性结案说明)
MECH/iss065_check.py                      L486                                      (ISS-065 复算的 D-9 条发现记录)
```
★**⇒ 这 11 行改了就毁掉「官网实读到底哪个型号是多厚」的证据 ⇒ 判红要判在「这 11 行被动过」★**

★**★33 行「可改行」的分布 (★按上面的权威表逐条做, 一行不漏★)**:
| 类别 | 文件 | 行数 |
|---|---|---|
| ★口径行★ | `MECH/MECH_BUDGET.md` (8 行·★不含 L867★) · `MECH/PROTOTYPE_PLAN.md` (4) · `MECH/RELIABILITY_TEST_PLAN.md` (3) · `MECH/CLEARANCE_FIX.md` (2) · `MECH/STRUCT_REVIEW_ISS065.md` (2) · `MECH/SERVICE_PORT_ISS092.md` (1) · `MECH/SOC_CARRIER_EVAL.md` (1) · `MECH/BOARD_WIDTH_15MM.md` (1) · `MECH/print/MEASURE_CHECKLIST.md` (1) | ★**23** ★ |
| ★脚本行★ | `MECH/verify_budget.py` (2·纯注释) · `MECH/iss065_check.py` (1·`name` 字段显示用·逻辑只用 t/v/l/g) · `MECH/fit_check.py` (2·注释 + print 文案) · `MECH/fit_check_v3_30mm.py` (1·注释) · `MECH/carrier_eval.py` (1·「出处文案」第 2 元) · `MECH/board_width_15mm_check.py` (1·注释) · `MECH/service_port_check.py` (1·注释) · `MECH/print/gen_print_pack_revb.py` (1·「出处文案」第 3 元) | ★**10** ★ |
| 合计 | ★19 个 MECH 活文件★ | ★**33** ★ |

★**★脚本行的铁律 (★ISS-319 §B1-3 逐个脚本说过归属★)**: ★**`cell_thk` / `batt_thk` = 4.60 / 23.50 / 40.50 这几个常量属于 `ICP422339PR`, 不属于 `ICP582035PR-01` ⇒ ★**脚本算的几何一直是对的, 错的只是它引用的型号名 ⇒ ★只许改型号名, 那几个数一个字都不许动★** ★

★**★`MECH/print/gen_print_pack_revb.py` 的坑 (★ISS-319 实测更正★)**: ★**该脚本只写 4 个 `.stl` ⇒ 「打印包重出带上新型号」只对 stdout 成立 ⇒ ⇒ ★**真正要改的手工处是 `MECH/print/MEASURE_CHECKLIST.md` L221 (非生成) ⇒ ★**而且 `gen_print_pack_revb.py` 本单【不许跑】(★零重生成★)★**

---

## ★3 · ★作业清单 ★

★**① 改前基线 (★先把 7 道 MECH 闸的 rc 记下来, 逐条存原始输出★)**
```
MECH/board_frame_feasibility.py      MECH/check_onepass_mech_sync.py
MECH/check_onepass_struct_crosscheck.py  MECH/check_onepass_mech_release.py
MECH/check_board_frame_coords.py     MECH/check_mech_verdict_freshness.py
MECH/service_port_check.py
```
★**另: 改前 md5 全量记下来 (★19 个要改的文件 + 板 + 网表/脚表/BOM★)★**

★**② 实做 33 行替换 (★只换型号名★)** ⇒ ★**每个改后文件必须 == 「改前内容做一次全量替换」的期望版本 (★逐字节★)★ ★

★**③ 改后逐项自证 (★每条都要有原始输出文件, 不许只贴结论★)**
```
① 替换后基线扫描 ⇒ 命中行数 = 11 (★只剩留证行★) · 文件数与 §2 的留证行分布一致
② 11 行留证行逐条比对 ⇒ 与改前逐字节相同 (★机器判★)
③ 每个改后文件 == 期望版本 (★逐字节★) ⇒ 33 行一条不落
④ 数字指纹 ⇒ 每个改后文件里【除型号名外】的数字序列与改前逐位相同
⑤ 9 个改过的脚本 ⇒ 逐个跑它自己的闸 ⇒ rc 必须 0
⑥ 7 道 MECH 闸改后复跑 ⇒ rc 必须 0 (★逐条与改前基线对照·不许有红项变绿或变红★)
⑦ 板 md5 + mtime 交卷前后逐字节相同 (★零写板★)
⑧ 网表/脚表/BOM/原理图 md5 未变 (★零落表★)
```

★**★④ 若某道 MECH 闸因为【文档正文变了】而红 ⇒ ★不许改闸★ ⇒ 交 need 给 main (★「在产生点修·不许在产物上擦」★)★**

★**⑤ 官网证据 (★自己查·零外发★)**: ★**型号规格一律自己上 renata.com 官网查 ⇒ 标 `[官网]` ⇒ ★查不到就写降级方案 (★选官网参数直接满足的替代型号 / 改设计路径绕开★) ⇒ ★不许写「等原厂回信」★** ★

★**⑥ 交卷前必跑 (★输出原样贴进回复★)**
```
python3 state/merge.py && python3 state/gate_check.py     # rc 必须 0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb                     # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb               # 必须 = 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER" <你的交卷页>                 # 必须 = 0
```
★**并用 `state/frag_write.py --agent mech-lead` 原子写 `state/fragments/mech.yaml`** (★禁止 `open(p,"w")`★) ★

★**⑦ 时间预算纪律**: ★**每完成 §3 的一条就把结论回填进交卷页 (★哪怕是「未验, 原因 X」★) ⇒ ★**宁可交半成品页, 不许一页纸都不落** (★上一趟 ISS-317/318 就是死在没落纸上★)★ ★

---

## ★4 · ★边界 (★硬★) ★
- ★**零写板** (板 `HW/PCB/demo_mainboard.kicad_pcb` 一个字节不许动) ★
- ★**零落表** (不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 任何 `.kicad_sch` / 落表台账) ★
- ★**零重生成** (★`MECH/print/gen_print_pack_revb.py` / `verify_pack_revb.py` / 任何 `state/gen_*.py` 一个都不许跑★) ★
- ★**零改闸** (★`state/gate_check.py` / 任何 `check_*.py` / MECH 域那几个自检脚本 (★`MECH/iss065_check.py` / `MECH/board_width_15mm_check.py`★) 的判据方向一律不许改★) ★
- ★**只许改 §2 表里那 33 行 / 19 个 MECH 文件** ⇒ ★**其余一个字都不许动 (★特别是那 11 行留证行★)★ ★
- ★**不许改任何尺寸 / 重量 / 容量常量** (★`4.60` / `23.50` / `40.50` / `340` / `4.38` / `78` / `49.58` / `74.16` / `48.90` / `72.80` 等★) ★
- ★**HW 域那 3 行不许碰** (★那是 main 的活★) ★
- ★**零外发** (★不许发邮件/询价/问询/采购; 型号规格一律自己上官网查并标证据等级★) ★
- ★**不替老板拍板** · ★**不自签 issue_log** · ★**不许改 `state/issue_log.yaml`** ★

---

## ★5 · ★交卷格式 ★
- 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md` (★B0 一句话+清单 / B1 结论摘要 / B2 验收标准自评(逐条 通过|不通过|未验) / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令★)
- `MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md` (★新建: 33 行实做台账·每行「改前逐字 / 改后逐字 / 数字指纹 / 所属文件」★)
- `logs/iss320/` 原始输出 (★改前/改后 md5 · 逐字 diff · 33 行台账 · 扫描前后对比 · 9 个脚本 rc 前后对照 · 7 道闸 rc 前后对照★)
- `state/fragments/mech.yaml` (★只改自己那一份★)
