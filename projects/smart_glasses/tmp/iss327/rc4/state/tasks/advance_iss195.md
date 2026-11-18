【项目总工派活 · 后继计划 · 闭环 ISS-195】你是硬件总工 (agent=`hw-lead`)。

★★**第一步 (★不许跳过★)**: ★**本文件往下第 ★★`任务书原文 (advance.py 给的 brief 全文)`★★ 那一段, 就是 `state/advance.py --json` 给你这单的 brief 原文, ★**一字未改★** ⇒ ★**照它做, 不要自己另写一套** ★★

★★**本单的真实状态 (★main 2026-11-15 20:5x 逐个文件实测, 不是推测★)** ★★:
★**① 上一次派活 (2026-11-12 03:2x) 的会话已死 (status=failed), 交卷没人落账 ⇒ 停在 `fixing` 3.5 天 (★同病第 11~13 次复发★)**
★**② 半交卷 —— 产物已经在盘上, 别重做**:
  · ✅ `HW/iss121_mic_magnet_check.py` mtime **2026-11-12 03:43:43** (★第 171~173 行已写「PIN-SET-2 孔位 = 现行 60×30 板 /
    套 A (ISS-194 仲裁定版)」★ · 第 189 行「J_CHG 座体 keep-out (现行 60×30 板)」★)
  · ✅ `HW/iss121_mic_magnet_check.json` mtime **2026-11-12 03:43:07**
★**③ 你这单真正缺的 (★只做这些★)**:
  · ❌ **`HW/ISS121_MIC_MAGNET_POSITION.md` mtime 2026-11-01 23:50 = 一字未动 ⇒ 三处 15mm 老口径还在** ⇒ 本单的三处里【文档那处】没做
  · ❌ 没有交卷报告 (`HANDOFF/` 里没有 ISS-195 的单子) ⇒ ❌ `state/fragments/hw.yaml` 没登记本单
  · ❌ 没有跑三闸自证 / 没写 PASS-FAIL-余量数字的结论段
★**④ 你要交的形状**: ★**脚本侧已按套A 改过 ⇒ 你要做的是【核对脚本算出来的数字 + 把结论写进 .md + 交卷 + 登记】** ★
★**⑤ 一条硬要求**: ★**你自己重跑一遍 `python3 HW/iss121_mic_magnet_check.py` 看它现在的读数 (★别照抄 main 的转述★)**,
★**读数若与脚本里写的不一致 ⇒ 以你实跑的为准, 并在交卷报告里点出来** ★

★**纪律 (★一条都不许破★)** ★★:
① ★**写分片必须走 `state/frag_write.py`** (★禁止 `open(p,"w")`★)
② ★**只写本单允许的文件, 不碰别人的分片** (★hw.yaml / sw.yaml / mech.yaml 各归各的★)
③ ★**证据分级必标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ ★**查不到就写 `[0数据]` + 降级方案, 不许编** ★
④ ★**不许外发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)
   ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ ★**没有「批一句可以发」这个选项** ★
⑤ ★**交卷前跑**: `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★【Q1】必须 18/18★)
   ⇒ ★**把输出原样贴进回复** ★
⑥ ★**不许改 `state/issue_log.yaml` 的 status** (★那是 main 的活★) · ★**不许改 `PROJECT_TRACKER.md` §0 锁死表** ★
⑦ ★**主线口径 (★老板 2026-11-11 10:07★)**: 当前主线 = ★**硬件原理图 demo 绘制** ★ ⇒
   ★**不许碰 PCB 布线 / 布局 / 逃线 / 层数** ★
⑧ ★**不许整文件读大文件** (★只许 `grep` / `sed -n` 取你要改的那几行★) ★
⑨ ★**交卷 ≤ 25 行** (★结论先行 + 逐条复现命令输出 + 缺口清单★) ★


================== `任务书原文 (advance.py 给的 brief 全文)` ==================

★**目标**: 把 `HW/iss121_mic_magnet_check.py` / `.json` / `HW/ISS121_MIC_MAGNET_POSITION.md` 里★**引 15mm 老口径孔位**的三处, ★**按现行 60×30 板 + 套A 孔位重算** ⇒ 给出麦克风磁体/麦克风的孔壁净空与最小间距的 PASS/FAIL 与余量数字。

★**为什么现在做 (★main 2026-11-11 20:2x 独立复算, 不是推测★)**:
· ISS-194 (孔位表 套B ⇒ 套A) 交卷后, 扫出三处仍引 15mm 老口径: `HW/iss121_mic_magnet_check.py`:171 · `HW/iss121_mic_magnet_check.json`:189 · `HW/ISS121_MIC_MAGNET_POSITION.md`:161
· ★**main 独立复算**: 麦 M1 封装 **2.90 × 1.60mm**, 中心 **(5.00, 12.00)** ⇒ 到 S1 压紧螺钉孔的孔壁净空:
  套B (S1 y=2.50) ⇒ dy=9.50 ⇒ **≈8.14mm** · 套A (S1 y=10.00) ⇒ dy=2.00 ⇒ **≈1.26mm**
  ⇒ ★**余量掉了一大截, 但仍不重叠、结论方向不变** ⇒ ★**结论要按现行孔位重算, 不能沿用 15mm 老口径** ★
· ★**为什么不在 ISS-194 里顺手改**: ★**那三个文件是 ISS-121 的地界** ⇒ ISS-194 的 brief 明确只写 `HW/pcb60x30_check.py` + `.json` ⇒ 越界 ⇒ ★**另开本单** ★

★**做法**: ① ★**先读 `MECH/BOARD_GEOM_30MM.md` §4 (结构侧定版孔位, main 已验收签字)** + `HW/pcb60x30_check.py` 的 HOLES 表 (★套A: S1 (8.00,10.00) ⌀1.40 / S2 (52.00,20.00) ⌀1.40 / P1 (8.00,15.00) ⌀2.00 / P2 (52.00,15.00) ⌀2.00★) ⇒ ★**别用 15mm 老口径** ★② ★**按那个脚本自己的公式** 重算麦 M1 封装与孔的孔壁净空 + 与其它件的最小间距 ③ ★**改这三处** (★只改引用/数字, 不许改判据阈值★) ④ 重跑该脚本, 给出 PASS/FAIL 与余量数字

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 HW/iss121_mic_magnet_check.py     # rc 与输出贴出来 (★新旧净空两个数都要给★)
python3 state/merge.py                     # rc 必须 0 (冲突 0)
python3 state/gate_check.py                # Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv   # 必须一字未变 (611b869e…)
```
★**交卷 ≤ 15 行** (结论先行; ★**明确写 PASS 还是 FAIL + 余量多少 mm★; ★**若 FAIL ⇒ 只报给 main 裁决, 不许自行改孔位或改判据** ★)

★**边界 (不许越)**
· ★**只写**: `HW/iss121_mic_magnet_check.py` + `HW/iss121_mic_magnet_check.json` + `HW/ISS121_MIC_MAGNET_POSITION.md` + `HANDOFF/` 下交卷报告 + ★**必要时** `state/fragments/hw.yaml` (走 `state/frag_write.py`; ★**只许新增/订正本单相关条目★)
· ★**不许碰**: `HW/pcb60x30_check.py` / `HW/pcb60x30_check.json` (★那是 ISS-194 的地界, 已定版★) · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · 任何 `state/gen_*.py` · `PROJECT_TRACKER.md` §0 · **别人的分片** · `state/issue_log.yaml` (★**改 issue 状态是 main 的活**)
· ★**不许联系供应商/原厂** (外发一律经项目总工) · ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标
· ★**不许改判据阈值来让自己变绿** (★降级等于伪造验收★)
