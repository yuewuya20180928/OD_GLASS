★★**目标 (★内部活·原理图/网表侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把 `--expect-resolved` 剩下的 21 条未落表逐条归因, 把【不依赖老板拍板】的那批当场落表, 并出【V-2/V-3/V-4 一旦拍板即可一键落】的逐字清单** ★★
⇒ ★**目标状态: 21 条逐条有归因 + A 类落完 `--expect-resolved` 条数下降且全闸 rc=0 (含 `--selftest` 21/21 仍全过) + 交卷单里有一份【老板只回一个字母就能落地】的清单** ★★

★★**为什么是现在 (★main 2026-11-16 06:4x~06:5x 自己实跑, 不是抄交卷报告★)** ★★
· ★**main 实跑 `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, 21 条未落表** ★ (★条数与构成照抄 ISS-230 交卷: R2×11 / R3×4 / R4×2 / R7×1 / R8×1 / R9×1 / R10×1 ★)
· ★**main 实跑 `python3 HW/check_netlist_selfconsistency.py` ⇒ rc=0** ★ · ★**`--selftest` ⇒ rc=0, 21/21 全过** ★ (★含 ISS-230 新增的用例19/用例20★)
· ★**main 实跑四道尺子全绿**: `python3 state/check_netlist.py` rc=0 · `python3 state/check_netlist_pins.py` rc=0 · `python3 state/check_sch_erc.py` rc=0 (ERC=0) · `python3 state/check_sch_pinfull.py` rc=0 (★图上 584 脚 = 表里 584 脚 · K=0 · 218 器件/153 网★) ★
· ★**main 实测网表 md5 = `3215020b6d4120e1b7728227effdc6d3`** ★ (★脚表 `a600afae…` / BOM `92b51580…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…` ★)
· ★**这 21 条就是「原理图定稿」的最后一截** ★ ⇒ ★**老板 11-11 10:07 口径: 当前主线 = 原理图 demo 绘制 ⇒ 本单是主线正中央** ★

★★**三条老板待拍的值 (★现状照抄 ISS-230 作业包 v2, main 已核过原文★)** ★★
· ★**V-3 (BAT_DET 分压)**: 现状 = 网表 `R_BAT_DET_1/2` = 1M+1M 且 DNP; ★**ISS-223 已算出恒等式 `R_th/k = R_top` ⇒ A(2.0M+1.2M) 与 D(2.0M+1.0M) 的 R_top 都是 2.0M ⇒ 漏电误差项与比容差项完全相同 ⇒ 现有选项集是伪选择** ★ ⇒ ★**推荐新增方案 E = 100k + 60k + 100nF** (R_th 37.5k ⇒ t_settle 34ms; 漏电@1µA = 2.1%FS; 总误差 <2.9%FS; 代价 26.25µA / 110µW) ⇒ ★**等老板拍, 你不许拍** ★
· ★**V-4 (R_ILIM)**: 现状 390Ω 档; ★**ISS-230 作业包里 V-4 = 680Ω ±1% (单 pin 0.349A ⇒ 余量 1.43×)** ⇒ ★**等老板拍** ★
· ★**V-2**: ★**main 已核 ISS-230 交卷实测结论: 「V-2 的网表侧落表一条判据都转不绿」(实测 7→7) ⇒ R4/R9 读的是 `.kicad_pcb` ⇒ V-2 必须写成【网表侧落表 + 板侧那一趟】两段** ★ ⇒ ★**等老板拍 + 板侧那一趟排队中** ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**21 条逐条归因表 (★机器可读 CSV/MD 都行, 但必须逐条一行★)** ★
  ⇒ 每行: 条目 id (R2/R3/R4/R7/R8/R9/R10 的具体条目) → 归类 **A 可自主落 / B 等老板某个 V 值 / C 板侧排队** → 判据引用 (哪条 EXPECT / 哪条脚本 / 哪份文档) → 落表后的预期变化 (expect-resolved 条数 ↓几) ★
  ⇒ ★**A 类的判据必须写死 (★不许凭感觉★)**: ★**"若老板改了 V-2/V-3/V-4 中任意一个值, 这一条要不要回退?" ⇒ 要回退 ⇒ 归 B 类, 不许落** ★ ★
② ★**A 类当场落表 (★走 ISS-220 / ISS-223 已有的落表流程★)** ★
  ⇒ 落表范围: 网表 / 脚表 / BOM + ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★新段 + 单号 + 新旧 md5★)** + 门禁 md5 锚点同步 (★`HW/check_netlist_selfconsistency.py` 的 EXPECT 与 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 锚点表必须逐字一致★) ★
  ⇒ ★**落完必须实跑并贴输出**: `--expect-resolved` (条数应下降) · `python3 HW/check_netlist_selfconsistency.py` rc=0 · `--selftest` rc=0 且 **21/21 仍全过** ★ · 四道尺子全 rc=0 · ★**`python3 state/merge.py && python3 state/gate_check.py` rc=0 (Q1 18/18)** ★
  ⇒ ★**★反向自证 (必做★)**: 把 A 类落的那条改回旧值 ⇒ ★**必须重新红** ⇒ 证明「你真改了判据满足的东西, 不是把红灯调没」 ★
③ ★**【拍板即可一键落】清单 (★老板回一个字母就能落地★)** ★
  ⇒ 每个 V 值一节: ★**单条取值 + 文件 + 行号 + 旧值 + 新值 (逐字) + 影响面 5 维 (脚表会不会变 / BOM 会不会变 / 判据5 (A 组 20 条) 会不会变 / `--expect-resolved` 会少几条 / 板侧要连带改什么 (只列, 不许自己改板)) + 落完要跑哪几条命令 + 谁要重锚 (sw-lead 走 H-1 / mech-lead 走 H-1) + 新旧 md5 登记位** ★
  ⇒ ★**只列, 不许落** ★ ⇒ ★**三节都要标出【这一节会改哪一行网表 / 哪一个字段】★** ★
④ ★**交接单 + 分片** ★
  ⇒ ★**新建 `HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md`** (★B1~B6 六块齐全★) ★
  ⇒ ★**分片 `state/fragments/hw.yaml`** ⇒ ★**必须走 `python3 state/frag_write.py` 原子写 (★不许 `open(p,"w")`★)** ★ ⇒ ★**不许删别人的条目** ★

★★**★必须写进交接单的【下游连锁影响】★** ★★
· ★**你落表 ⇒ 网表/脚表 md5 会变 ⇒ SW 侧 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点与 MECH 侧 `MECH/HW_CROSS_REVIEW_TRIAGE.md` 锚点会按设计变红 ⇒ 你必须在交接单里写清【新旧 md5 + 落表单号 + 影响到的两处台账位置】(供 H-1 重锚)** ★
· ★**★但不许你自己去动那两份台账 (★那是 sw-lead / mech-lead 的地界★)★** ⇒ 走 `state/fragments/*.yaml` 登记 need ★
· ★**落表单号用 ISS-233** ★ (★sw-lead 走 H-1 时要靠这个单号在落表台账里查到★)

★★**边界 (★越界即无效★)** ★★
· ★**不许落任何 V 值 (V-2 / V-3 / V-4 老板都没拍) ⇒ 只出选项 + 逐字清单** ★
· ★**不许改板** (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` / 布线 / 布局 / 板框 一律不碰★) ⇒ ★**板侧 B-1~B-8 继续排队** ★
· ★**不改 `SW/`** · ★**不改 `MECH/`** (★except 登记 need★) ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别人的分片** ★
· ★**不发信 / 不联系供应商 / 不下采购单** ★ · ★**实物 [实测] = 0 条** ★
· ★**受保护 md5**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★**逐字节不变** ★; ★**网表 / 脚表 / BOM 只有本单合法落表时才允许变, 且必须在交接单里写清新旧值** ★
