# ISS-356 · hw-lead · ★「板那一趟」封装真值基线 · ★★cont2 续做 (★上一趟被 50 分钟超时掐死, 读数都在盘, 交付物零★)★★

★**这是 cont2 (★cont1 于 08:47:16 被 runTimeout 掐死·★读数全在盘·交付物一件没写★)** ⇒ ★**本趟 = 把已经在盘的读数【落成三件交付物】, 不是从零重跑读数★** ★

★**必读**: ① 本任务书 ② 原任务书 `state/dispatch_briefs/ISS-356_hw_fp_truth_baseline.md` (F1~F17 + 交付物 1/2/3 + C1~C6 + 边界) ③ cont1 任务书 `state/dispatch_briefs/ISS-356_hw_fp_truth_baseline_cont1.md` (★它那三条订正**全部继续有效★★)

---

## ★★一 上一趟怎么死的 (★main 2026-11-23 08:5x 本机实读·不抄任何 agent 报告★) ★★

- ★**子会话**: `agent:hw-lead:subagent:d4cca1cc-d4ad-4406-a2c0-5ac56373893a` (sessionId `79729395-3ce6-4bcb-a7f5-6f9d814600dc`) ⇒ ★**07:57:13 起跑, 08:47:16 结束 = 恰好 50 分钟** ⇒ ★**被 main 派活时给的 `runTimeoutSeconds=3000` (50 分钟) 掐死** ⇒ 最后一句是「Found `Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm` — exactly matching the BQ25896 RTW package. **Now I have everything needed.**」⇒ ★**死在【刚把读数攒齐、还没开始写交付物】那一刻** ★
- ★**它在盘的东西 (★8 件读数, 都可用, 不用重跑★)**: `logs/iss356/board_footprints.json` (186 封装逐个解析) · `logs/iss356/lib_cand_geometry.json` (18 条库候选几何) · `logs/iss356/lib_cand_geometry_v2.json` (30 条) · `logs/iss356/probe_lib_fp.py` + `probe_lib_fp_v2.py` · `logs/iss356/f8_set_dump.txt` · `logs/iss356/parse_board.py` · `logs/iss356/target100_raw.txt` · `logs/iss356/board_fp_families.txt` ★
- ★**零交付物**: `HW/FP_TRUTH_BASELINE.md` · `HW/check_fp_truth_baseline.py` · 交卷页 ⇒ ★**三件都不在盘** + ★**分片命中 0** (`hw.yaml` 里 `iss356` = 0) ⇒ ★**⇒ 台账 status 仍保持 `fixing` (不落 open ⇒ 兄弟 job 不会重复派)★**

## ★★二 ★★本趟的第一条纪律: ★先落盘, 再继续 (★这一趟必须做到·否则再死一次还是零交付★)★★

★**上一趟的失败模式 = 把读数全攒在上下文里, 直到超时 ⇒ 上下文一没, 什么都没留下** ⇒ ★**本趟必须改成【增量落盘】★**:
1. ★**第一步就把 §1 族级映射表 + 闸脚本 (`HW/check_fp_truth_baseline.py`) 写出来落盘** (★哪怕 §2 逐 ref 表还没写完·也要先有这两件★) ⇒ ★**再死一次, 至少留得下骨架**
2. ★**§2 逐 ref 表 (`HW/FP_TRUTH_BASELINE.md` §2) 分批写** (★建议按族分批: 先 2 端子电阻电容 → 再 IC → 再连接器/座子 → 每批写完就 append 进页并落盘★)
3. ★**每写完一段, 跑一次 `python3 HW/check_fp_truth_baseline.py`** ⇒ 闸红了就地修, 不要攒到最后
4. ★**别把「找齐全部 100 件」当成开工前置** ⇒ ★**先把已知的落盘, 剩下的在 §5 写明「未做 + 续做入口」** (★原任务书那条「宁可交 40 件真件, 不要交 100 件假件」继续有效★)

## ★★三 ★★scope 订正: 这块板的靶子其实是 78 件, 不是 100 件 (★main 本机独立读 `HW/BOM_v1.csv` + 板文件★) ★★

★**main 实读**: BOM 218 行 = NET/TP 53 + 真实器件 165 ⇒ 必装 124 ⇒ ★**必装且 `footprint` 待定 = 100** ⇒ ★**按 `board` 列拆开: 「镜脚主 PCB」78 件 + 「镜框充电板」22 件** ★
★**并且: 那 78 件【全部在板面上真实存在】**(★main 用板文件的 Reference 属性逐个对过·78/78 命中★) ⇒ ★**⇒ 这块板(18092 走线那块的本体)的封装真值靶子 = 78 件; 那 22 件属【另一块板】(镜框充电板), 不在这块板面上 (板面 `grep BQ25896` = 0; `U_CHG` 是充电板件)★**
★**⇒ 本单交付口径 (★按这个做, 不要按 100 件硬凑★)**:
- ★**§2 逐 ref 表的必做范围 = 78 件 (镜脚主 PCB)** ⇒ **100% 做完这 78 件**
- ★**另立一节 §4「另一块板(镜框充电板)的 22 件封装真值债」** ⇒ 逐条列 ref + board 列 + 状态 ⇒ ★**只登记, 不展开查库 (★那不是这块板的事·★免得这一趟超时★)** ★
- ★**跨界 1 件要单独点名**: `C_VBUS_GND` / `C_VBUS_OUT` 的 BOM `board` 列写「镜框充电板」, ★**却出现在主 PCB 的板面上** ⇒ 这正是基线里「多余 2」差异的同源项 ⇒ ★**归老板那件 `C_VBUS_GND` 留位/下板 的答案, 本单只登记事实, 不代拍** ★

## ★★四 ★★main 的三条订正 (★继续有效·★且已被上一趟证明有效★) ★★

1. ★**KiCad 官方库计数**: `/home/yuewuya/kicad/AppDir/share/kicad/footprints/` = ★**155 个 `.pretty` 库目录**★ / ★**15,468 个 `.kicad_mod` 封装文件**★ ⇒ ★**一律按 155 / 15,468 写 (原任务书「15,777 个 .pretty 目录」是单位写错)** ★
2. ★**KiCad 10 官方库是 metric 后缀命名** ⇒ ★**每个 `lib:name` 必须逐个验 `.kicad_mod` 文件在盘 (不许只验库目录)** ⇒ ★**★main 已实测上一趟的两份候选表: `lib_cand_geometry.json` 18 条 + `lib_cand_geometry_v2.json` 30 条 ⇒ 48/48 文件真在盘, 且旧名一个都没混进去 ★★⇒ 你直接用这两份, 但落页时仍要自己 `test -f` 一遍并把结果贴进交卷页** ★
3. ★**单焊盘器件族**: 板面 186 个封装里 49 个只有 1 个焊盘 ⇒ 去掉 42 个 `TP_*` ⇒ ★**7 个真实器件只有 1 个焊盘**: `CHG_GND_STAR` · `C_KEY_CAM` · `C_KEY_PWR` · `C_KEY_VM` · `C_KEY_VP` · `R_BAT_DET_2` · `R_NTC_BAT` ⇒ ★**2 端子件只画 1 个 land ⇒ 装不上/装歪 ⇒ 必须进族表 + 「触发布局布线改动」栏 + §2 逐 ref 表** ★ ⇒ ★**自己重跑一遍实读 (别抄 main 这段) 并在交卷页点名** ★

## ★★五 交付物 (照原任务书, 但按 §三 的口径) ★★

1. ★**新建 `HW/FP_TRUTH_BASELINE.md`** (★本单新建·交卷时才有★): ★**§1 族级映射表** (★每族给目标 `lib:name`·★**不许拿「待定/TBD/待选型」当结论**★·★给不出来的要么写降级方案, 要么进 §3 删件候选★) · ★**§2 逐 ref 表** (★78 件做完·每行: ref / type / value / 必装-DNP / 现占位族 / 目标 `lib:name` / 库文件实存路径 + md5 / 焊盘数与网络核对结论 / 候选 OPN / 证据等级 / 是否触发布局布线改动★) · ★**§3 删件候选** (★只给候选与代价·不代拍★) · ★**§4 镜框充电板 22 件封装真值债 (只登记·不展开)** · ★**§5 已做/未做分界 + 续做入口** ★
2. ★**新建 `HW/check_fp_truth_baseline.py`** (★本单新建·交卷时才有★): **C1** 每个靶子 ref 都在页里且带目标 `lib:name` (★漏一个 = 红 + 点名★) · **C2** 每个 `lib:name` 的**封装文件真在盘** (★查 `.kicad_mod`·不是只查库目录★) · **C3** 每行证据等级非空 · **C4** 每行降级方案栏非空 · **C5** 正文禁「等原厂回信」类表述 · **C6** 件数字段自洽 ⇒ ★**输出带名单, 只报数量 ⇒ rc=1** ★ · ★**`--selftest` 反向用例 ≥5 条, 每条自证「红的是目标那一条, 其余仍绿」** (① 删页里某一行 ⇒ C1 红 ② 改某行 `lib:name` 成不存在的 ⇒ C2 红 ③ 清空证据等级 ⇒ C3 红 ④ 清空降级方案 ⇒ C4 红 ⑤ 正文塞「等原厂回信」⇒ C5 红 ⑥ 篡改件数字段 ⇒ C6 红) · ★**沙盒落项目盘 `tmp/`, 真件零污染** ★
3. ★**新建交卷页 `HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md`** (★本单新建·交卷时才有★): ★**B1~B6 六个 `##` 标题里必须分别出现: B1 `结论` · B2 `验收标准自评` · B3 `证据分级` · B4 `接口取值声明` · B5 `未决项与卡点` · B6 `自证复现命令`** ⇒ ★**`state/gate_check.py` 按标题关键词判块 ⇒ 缺一个 Q1 就掉 ⇒ 掉 Q1 不许怪别人★** + 页内引用路径逐个在盘 (MISS=0) + 板指纹前后双证 + ★**§B5 要写明两次死亡 (cont1 超时 50 分钟 / cont0 被 abort)★** + `state/fragments/hw.yaml` 分片登记 (★只走 `state/frag_write.py`★)

## ★★六 边界 (照原任务书·一条不许越★) ★★

★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` · 开工前 + 交卷后各打一次双证) ★ · ★**零落表** (不改网表/脚表/BOM/原理图/任何闸/别人的分片) ★ · ★**零外发 / 零采购 / 零联系供应商** (★不许写「等原厂回信」·查不到就写降级方案★) ★ · ★**不替老板拍板 · 不新增拍板项** (★`C_VBUS_GND` 留位、`U-1` 画哪块板、ESD 架构/型号轴 ⇒ 都不是你的项★) ★ · ★**证据分级必标** ★ · ★**写分片只用 `state/frag_write.py`** ★ · ★**只写 4 处 + `logs/iss356/`** ⇒ ★**若 `HW/FP_TRUTH_BASELINE.md` 或 `HW/check_fp_truth_baseline.py` 已存在且不是你写的 ⇒ 停下, 在交卷页写明「撞车」, 不要覆盖** ★
★**必跑 (原样输出贴进交卷页 B6)**: `python3 state/merge.py` (rc=0) · `python3 state/gate_check.py` (rc=0 · Q1 18/18) · `python3 HW/check_fp_truth_baseline.py` (rc=0) · `python3 HW/check_fp_truth_baseline.py --selftest` (rc=0 · 末行 ALL TESTS PASS) · `md5sum HW/PCB/demo_mainboard.kicad_pcb`
