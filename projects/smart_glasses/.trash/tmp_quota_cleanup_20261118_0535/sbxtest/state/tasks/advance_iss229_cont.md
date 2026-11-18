★★**目标 (★同单续做 · 只补最后一步 · 不许重做已落盘的东西★)** ★★
★**ISS-229 (充电皮肤温度按改正系数重算 + MECH 闸 G5b/C21 重锚) 的 ① ~ ⑥ 你上一轮已经全部落盘了 ⇒ ★**本轮只补 ④ 分片 + 把门禁实跑输出贴回交接单** ★★

★★**main 2026-11-16 06:4x 实测的现状 (★你不用再找, 也不用重做★)** ★★
· ★**① 已落**: `MECH/hinge_power_calc.py` (06:09) · `MECH/hinge_power_calc.json` (06:10) · `MECH/HINGE_POWER_CALC.md` (06:23) ⇒ ★**新系数 `ICHG_FACTOR_VBAT_370 = 1.216` / `ICHG_FACTOR_VBAT_420 = 1.071` / `ICHG_FACTOR = 1.216`, 旧值 0.822 只留痕不参与计算** ★
· ★**② 已落**: `MECH/FPC_FAB_NOTES.md` (06:23, 同型旧数清理) ★
· ★**③ 已落**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` (06:23, G5b/C21 重锚) ★
· ★**④ 已落**: 交接单 `HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md` (38046 B, 06:25) ★
· ★**★唯一缺的**: ⑤ **分片 `state/fragments/mech.yaml` 一个字节都没写** (★mtime 仍是 05:27 = 上一单 ISS-227 的时刻★) ⇒ ★**这是本轮唯一的活** ★
· ★**main 自己实跑的三道闸 (★已全绿, 不用你再证明一遍, 但你要把输出贴回交接单★)**:
  · `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0, 23/23 组检查通过, FAIL 0 组** ★
  · `python3 MECH/cavity_recalc_check.py` ⇒ ★**22/22** ★
  · `python3 MECH/verify_budget.py` ⇒ ★**rc=0 门禁绿** ★

★★**你要做的 (★两件, 少一件即无效★)** ★★
① ★**写分片 `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py` 原子写, ★不许 `open(p,"w")`★)** ★
  ⇒ ★**artifact**: 本单 3 个产物 (`MECH/hinge_power_calc.py` · `MECH/hinge_power_calc.json` · `MECH/HINGE_POWER_CALC.md`) + 交接单 ★
  ⇒ ★**claim**: ①「充电皮肤温度按改正系数 1.216 重算后的结论 + 旧值 0.822 作废留痕」②「MECH 闸 G5b/C21 已重锚到 ISS-223 的网表 md5」 ★
  ⇒ ★**answer**: ★**回掉本单对应的未闭合 need (若有)** ★
  ⇒ ★**needs_from**: ★**给 main 的: 充电皮肤温度新口径是否影响任何【整机阶段】的判据 (只登记, 不改别人的件)** ★ ⇒ ★**给 sw-lead / hw-lead 的: 若有★** ★
  ⇒ ★**不许删别人的条目** ★
② ★**把门禁实跑输出贴回交接单 (★三道闸 + `--selftest` 若有★)** ★
  ⇒ ★**并在交接单里确认两条**: ★**① 「42.14°C 是按 0.822 算的 ⇒ 作废 ⇒ 无有效数字」这句已逐字留痕** ★ ; ★**② 新系数 1.216 的来源 (★自己复算一遍, 写出算式与代入值, ★不许只抄 JSON★)** ★

★★**边界 (★越界即无效★)** ★★
· ★**不许重做 ①②③④ (★重做会覆盖已落盘的正确数★)** ⇒ ★**只允许新增, 不许改写已落的 4 个文件的内容 (除非是错值, 若是错值必须先在交接单里写清)** ★
· ★**不改 `HW/` · 不改 `SW/`** ★ · ★**不碰 PCB 布线 / 布局 / 板框** ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别人的分片** ★
· ★**不发信 / 不联系供应商 / 不下采购单** ★ · ★**实物 [实测] = 0 条 (本机物理上做不到实测)** ★
· ★**阈值一个不许动**: 皮肤 43 °C / 端件 60 °C / `cavity_req` 4.50 / `CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00 ★
