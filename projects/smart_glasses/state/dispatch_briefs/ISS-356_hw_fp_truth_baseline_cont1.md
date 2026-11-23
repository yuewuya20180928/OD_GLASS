# ISS-356 · hw-lead · ★「板那一趟」封装真值基线 · ★★cont1 续做 (上一趟被掐死)★★ · 纯分析/作业包 · 零写板

★**这不是从零重开** ★ ⇒ ★**上一趟 (2026-11-23 07:4x 派) 的子会话被掐死了, 但读数有一部分在盘** ⇒ ★**本单 = 从已在盘的读数续做, 不是从零★** ★

★**★原任务书全文**: `state/dispatch_briefs/ISS-356_hw_fp_truth_baseline.md` ⇒ ★**必读一遍** (★它给的 F1~F17 事实表 + 交付物 1/2/3 + C1~C6 判据 + 边界·★全部仍然有效★) ⇒ ★**本任务书只追加【死亡登记】+【本趟要补什么】+【main 的三条订正】, 不改原任务书的任何判据★** ★

---

## ★★一 上一趟怎么死的 (★main 2026-11-23 07:5x 本机实读, 不抄任何 agent 报告★) ★★

- ★**子会话**: `agent:hw-lead:subagent:88277b45-3ee3-49f3-9c03-27f1f66f448a` (sessionId `0381eeb2-80ee-4e53-b44b-8e7e057a09d4`) ⇒ ★**07:50:08 被 abort (transcript 末行 = `toolResult: Aborted`; sessions_list 报 status=timeout / abortedLastRun=true)★** ⇒ ★**它最后一句是「Critical finding — 2-terminal parts with only 1 board pad. Let me verify this systematically.」⇒ 死在【刚发现、还没落盘】的那一刻** ★
- ★**它在盘的东西 (只有两件)**: `logs/iss356/board_fp_families.txt` (07:44) · `logs/iss356/target100_raw.txt` (07:44) ⇒ ★**零交付物**: `HW/FP_TRUTH_BASELINE.md` / `HW/check_fp_truth_baseline.py` / 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md` ★**三个都不在盘** ⇒ ★**分片命中 0** ★
- ★**台账**: `ISS-356` 的 status **保持 `fixing`** (★不落 open ⇒ 兄弟 job fb67af40 / 775d9893 的 `advance.py --json` 看不见本单 ⇒ 不会重复派★) ⇒ ★**owner = hw-lead, due 2026-11-25** ★

## ★★二 本趟要补什么 (★交付物与判据照原任务书, 这里只列清单★) ★★

★**交付物 1** `HW/FP_TRUTH_BASELINE.md` (★新建页★): §1 族级映射表 (★每族给出目标 `lib:name`·**不许拿「待定/TBD/待选型」当结论**★) · §2 逐 ref 表 (★每行: ref / type / value / 必装-DNP / 现占位族 / 目标 `lib:name` / **库文件实存路径 + md5** / 焊盘数与网络核对结论 / 候选 OPN / 证据等级 / 是否触发布局布线改动★) · §3 删件候选 (★只给候选与代价·不代拍★)
★**交付物 2** `HW/check_fp_truth_baseline.py` (★新建闸★): **C1** 每个「必装 且非 NET/TP 且 footprint 待定」的 ref 都在页里且带目标 `lib:name` (★漏一个 = 红 + 点名★) · **C2** 每个 `lib:name` 的**封装文件真在盘** (★查 `.kicad_mod` 文件·不是只查库目录!★) · **C3** 每行证据等级非空 · **C4** 每行降级方案栏非空 (★查不到的件不许空着★) · **C5** 正文禁「等原厂回信」类表述 · **C6** 件数字段自洽 ⇒ ★**输出必须带名单, 只报数量 ⇒ rc=1** ★ ⇒ ★**`--selftest` 反向用例 ≥5 条, 每条自证「红的是目标那一条, 其余仍绿」** (① 删页里某一行 ⇒ C1 红 ② 改某行 `lib:name` 成不存在的 ⇒ C2 红 ③ 清空证据等级 ⇒ C3 红 ④ 清空降级方案 ⇒ C4 红 ⑤ 正文塞「等原厂回信」⇒ C5 红 ⑥ 篡改件数字段 ⇒ C6 红) ⇒ ★**沙盒必须落项目盘 `tmp/`, 真件零污染** ★
★**交付物 3** 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md` (★**B1~B6 齐全, 六个 `##` 标题里必须分别出现: B1 `结论` · B2 `验收标准自评` · B3 `证据分级` · B4 `接口取值声明` · B5 `未决项与卡点` · B6 `自证复现命令`** ⇒ ★**`state/gate_check.py` 按标题关键词判块 ⇒ 缺一个 Q1 就掉 ⇒ 掉 Q1 不许怪别人★**) + 页内引用路径逐个在盘 (MISS=0) + 板指纹前后双证 + `state/fragments/hw.yaml` 分片登记 (★只走 `state/frag_write.py`★)

## ★★三 ★★★main 的三条订正 (★2026-11-23 07:5x 本机实读·★这一趟照旧任务书写就会错的三个点★)★★★ ★★

### ★订正①: KiCad 官方库的数量口径写错了 (★单位错·不是数错★) ★

★**原任务书 F11 写「15,777 个 `.pretty` 目录」⇒ main 本机实读是: **★`ls /home/yuewuya/kicad/AppDir/share/kicad/footprints/*.pretty | wc -l` = **155**★ (库目录数) ⇒ `find ... -name '*.kicad_mod' | wc -l` = **15,468**★ (封装文件数) ⇒ ★**⇒ 15,777 是把【封装文件数】写成了【.pretty 目录数】⇒ 基线页/交卷页里一律按「155 个库目录 / 15,468 个封装文件」写★**

### ★订正②: ★★KiCad 10 官方库是【metric 后缀命名】⇒ 旧名按字面找不到文件★★ ★

★**main 本机逐个 `test -f` 实测 (库路径 = `/home/yuewuya/kicad/AppDir/share/kicad/footprints/<Lib>.pretty/<name>.kicad_mod`)★:

| 任务书里的例名 | 真名 (在盘) | 旧名按字面 |
|---|---|---|
| `Resistor_SMD:R_0402` | ★`Resistor_SMD:R_0402_1005Metric`★ | ★**不存在**★ |
| `Capacitor_SMD:C_0402` | ★`Capacitor_SMD:C_0402_1005Metric`★ | ★**不存在**★ |
| `Capacitor_SMD:C_0603` | ★`Capacitor_SMD:C_0603_1608Metric`★ | ★**不存在**★ |
| `Capacitor_SMD:C_0805` | ★`Capacitor_SMD:C_0805_2012Metric`★ | ★**不存在**★ |
| `LED_SMD:LED_0805` | ★`LED_SMD:LED_0805_2012Metric`★ | ★**不存在**★ |
| `Inductor_SMD:L_0805` | ★`Inductor_SMD:L_0805_2012Metric`★ | ★**不存在**★ |
| `Button_Switch_SMD:SW_SPST` | ★无裸名 ⇒ 具体是 `SW_SPST_B3S-1000` / `SW_SPST_B3S-1100` 等型号★ | ★**不存在**★ |
| `Diode_SMD:D_SOD-523` / `D_SOD-123` | ★裸名存在 (这俩是例外)★ | 在盘 |

★**⇒ 硬要求**: ★**基线页里每一个 `lib:name` 都必须逐个验【`.kicad_mod` 文件】在盘 (不是只验 `.pretty` 库目录在盘)** ⇒ ★**否则那一趟画出去的板会指向不存在的封装 ⇒ 型号一落又得返工 (板 md5 变第二次)** ★ ⇒ ★**main 的签收闸里有这条机器判据 (逐个文件查), 查不到 = 拒签** ★

### ★订正③: ★★单焊盘器件族 (★main 本机实读板文件; ★上一趟 agent 最后一句的发现, 但它被掐死了 ⇒ 结论要你自己重证一次★)★★

★**板面 186 个封装按 pad 编号集合聚类 (main 实读)**: `('1','2')` × **107** · `('1',)` × **49** · `('1'..'5')` × 6 · `('1','2','3')` × 4 · (`1`..`99` 大连接器族) × 4+1+1 · `('1','2','3','4')` × 3 · `('1'..'6')` × 2 · `('2'..'6')` × 2 · `('13','14','15','4')` × 2 · `('1','4','5','6')` × 1 · `('2'..'7')` × 1 · `('1','2','4','5')` × 1 · `('1','6')` × 1 ★
★**⇒ 49 个单焊盘封装里, 42 个是 `TP_*` 测试点 ⇒ 剩下 7 个是【真实器件却只有 1 个焊盘】**: ★`CHG_GND_STAR` · `C_KEY_CAM` · `C_KEY_PWR` · `C_KEY_VM` · `C_KEY_VP` · `R_BAT_DET_2` · `R_NTC_BAT`★ ⇒ ★**2 端子件只画了 1 个 land ⇒ 装不上/装歪 ⇒ 必须进族级映射表与「触发布局布线改动」栏** ★
★**要求**: ★**这 7 个 ref 你要自己重跑一遍实读 (别抄我这段) 并在交卷页点名**: 现在几个焊盘 / 应是几个 / 属于哪一族 / 换封装后是否触发布局改动 ★

## ★★四 边界 (★照原任务书·一条不许越★) ★★

★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 逐字节不变 · 开工前 + 交卷后各打一次双证) ★ · ★**零落表** (不改网表/脚表/BOM/原理图/任何闸/别人的分片) ★ · ★**零外发 / 零采购 / 零联系供应商** (★不许写「等原厂回信」·查不到就写降级方案★) ★ · ★**不替老板拍板 · 不新增拍板项** ★ · ★**证据分级必标** (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) ★ · ★**写分片只用 `state/frag_write.py`** ★ · ★**只写 4 处 + logs**: `HW/FP_TRUTH_BASELINE.md` · `HW/check_fp_truth_baseline.py` · 交卷页 · `state/fragments/hw.yaml` · `logs/iss356/` ★ · ★**不许改 `state/gate_check.py`** (★本单闸挂不挂链 = main 地界, 你只交脚本与路径 + 建议★)

## ★★五 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 state/merge.py                 # rc=0
python3 state/gate_check.py             # rc=0 · Q1 必须 18/18
python3 HW/check_fp_truth_baseline.py   # rc=0
python3 HW/check_fp_truth_baseline.py --selftest   # rc=0 · 末行 ALL TESTS PASS
md5sum HW/PCB/demo_mainboard.kicad_pcb  # 必须 611b869e13518c3c023fb178f91a0075
```
★**做不完 100 件不许假装做完**: ★**交卷页写清「已做 / 未做」分界 (逐 ref 名单) + 未做部分的续做入口 (★下一步从哪个族开始★) ⇒ ★**宁可交 40 件真件, 不要交 100 件假件**★ ★
★**并发写盘**: ★**若 `HW/FP_TRUTH_BASELINE.md` 或 `HW/check_fp_truth_baseline.py` 已存在且不是你写的 ⇒ ★**停下, 在交卷页写明「撞车」, 不要覆盖别人的内容**★ ★
