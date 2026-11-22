★★★★【main 2026-11-23 00:5x · ★★PCB 线 · MECH 域 8 个判定脚本迁【双口径】 · 纯脚本改造 + 文档订正 + 机器闸 · 零写板 ★★】★★★★
★**8 个 MECH 判定脚本现在只认 60×30 / RK3576 一档, 而现役板是 160×100 / RK3572 ⇒ 板那一趟的判据读数全是另一块板的口径 ★**

★**派活方 = 项目总工 (main) · 2026-11-23 00:5x · cron fb67af40 (队列自动派活)★★**
★**来源 = main 2026-11-23 00:1x 已裁 (★`state/fragments/pm.yaml` → `answers` → key `iss342_geom_caliber_downstream_audit`★) + ISS-342 交回 main 的卡点 (★`HANDOFF/2026-11-22_mech-lead_ISS342_结构侧权威表口径漂移.md`§B5 ①★★**
★**工作目录 (★所有命令都在这里跑★)**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses`

---

## §0 事实 (★main 本机实读 + 实跑, 不抄任何 agent 报告★)

★**① main 2026-11-23 00:1x 的裁决原文 (★`pm.yaml` `iss342_geom_caliber_downstream_audit` 的 `value` 逐字★) ★**:
★**「① 下游 8 个脚本迁不迁? ⇒ ★**迁** (★`pinset2_mech_check.py` / `skeleton_section_check.py` / `fit_check_v3_30mm.py` / `fit_check.py` / `cross_review_check.py` / `board_frame_feasibility.py` / `board_port_opening_s6_check.py` / `jd_y0_feasibility.py`★) ⇒ ★**但迁法必须是【双口径】**: ★**每个脚本同时支持 60×30 / RK3576 与 160×100 / RK3572 两档 (默认档由 U-1 定) ⇒ 不许把 60×30 档删掉 (★它是历史口径·删了就等于抹掉 11-11 那一段的设计依据★) ★** ★」 ★**
★**「★**迁的时限**: ★**必须赶在板那一趟开工前** (★板那一趟里【不许临时改脚本】——判据在板那一趟期间必须冻结★) ⇒ ★**迁的时候顺带把 `MECH/BOARD_GEOM_CALIBER_STATUS.md` 的 scope A 真数同步订正 (★迁完文件集合又变了·计数必须等于盘面★) ★」 ★**
★**「★**为什么不能改成 160×100 单档**: ★**「这一趟画哪块物理产品」这个上位问题还没拍 (★ISS-341 的机器判决是「B160x100 = 改现役板一次」, 但那是【板框候选】的判决·不等于【产品形态】已定★) ⇒ ★**若现在就把脚本改成 160×100 单档, 老板一旦拍「画产品内板 60×30」, 脚本就又得改一遍 ⇒ 判据就变了 ⇒ 板那一趟的读数全部作废 ⇒ 直接违「板只改一次」★ ⇒ ★**双口径一次做完, 老板拍完只切默认档, 不动判据本体** ★」 ★**
★★**⇒ 三条硬要求, 一条都不许打折: ① 双口径 (两档都在, 60×30 档不许删) ② 默认档由 U-1 定 ⇒ **本单不许自己拍默认档** ③ 迁完 scope A 真数重算并订正清单页 ★★**

★**② 现状 (★main 本机实读 8 个脚本的常量定义★) ★**:
| 脚本 | 现在硬编了什么 | 有没有 B160x100 档 |
|---|---|---|
| ★`MECH/pinset2_mech_check.py` ★ | `PCB_L = 60.00` / `PCB_W = 30.00` (★第 61~62 行★) + RK3576 封装 | ★**无** (grep `B160x100` = 0 命中) ★ |
| ★`MECH/skeleton_section_check.py` ★ | `PCB_L = 60.00` / `PCB_W = 30.00` / `PCB_T = 1.00` (★第 53~55 行★) + RK3576 17.20×16.10 | ★**无** (0 命中) ★ |
| ★`MECH/fit_check_v3_30mm.py` ★ | 全文按「板宽 30mm / RK3576 基线」写 (★第 4 行 / 第 11 行 / 第 89 行 / 第 105 行 / 第 303 行★) | ★**无** (0 命中) ★ |
| ★`MECH/fit_check.py` ★ | ★**自己第 6 行就写着「本脚本基线已作废 —— 现行版是 `MECH/fit_check_v3_30mm.py`」★ ⇒ 它是历史脚本 | ★**无** (0 命中) ★ |
| ★`MECH/cross_review_check.py` ★ | `"board_w": 30.0` (★第 68 行★) + 板宽 12→30 的迁版史 (★第 26~29 行★) | ★**无** (0 命中) ★ |
| ★`MECH/board_frame_feasibility.py` ★ | ★**已有 `FRAMES` 三档表** (★第 100~130 行★): `B160x100` 160×100/8层/1.60 + `F30A` 60×30/6层/1.00 + `P60x15` 60×15/6层/1.00 | ★**有** (4 命中) ★ |
| ★`MECH/board_port_opening_s6_check.py` ★ | ★**已有三档 `frames` 表** (★第 389~395 行★): 台架板/60×30/60×15 | ★**有** (4 命中) ★ |
| ★`MECH/jd_y0_feasibility.py` ★ | ★**已有 `FRAMES` 三档表** (★第 166~182 行★): 台架板 160×100/8层/1.6 + 60×30 + 60×15 | ★**有** (5 命中) ★ |
★⇒ ★**3 个脚本已经有帧表 (★board_frame_feasibility / board_port_opening_s6_check / jd_y0_feasibility★), 5 个没有 (★pinset2_mech_check / skeleton_section_check / fit_check_v3_30mm / fit_check / cross_review_check★) ⇒ ★**你的工作量在【后者】, 前者只需核对现成的档位表对不对 (★★不许把已经对的东西重写一遍★) ★**

★**③ 为什么现在必须做 (★main 的读法★) ★**:
★**板那一趟 = 「板只改一次」那一趟 (★S1~S13 一次跑完·板 md5 只许变一次★) ⇒ ★**那一趟里【不许临时改脚本】(★判据在那一趟期间必须冻结★) ⇒ ★**所以这 8 个脚本的判据必须在【那一趟开工前】就定好 ⇒ 现在做, 不许拖到那一趟里 ★**

★**④ 谁在消费这 8 个脚本 (★main 实读, ★你改它们会连带影响下游闸的读数★) ★**:
- ★`MECH/check_board_frame_candidate_compat_gate.py` (★第 902~903 行★) 调 `board_frame_feasibility.py` + `pinset2_mech_check.py` ★
- ★`MECH/check_board_frame_coords.py` (★第 84 行 `S6_PATH`★) 读 `board_port_opening_s6_check.py` ★
- ★`MECH/check_onepass_mech_release.py` (★第 59 / 69 行★) 跑 `board_port_opening_s6_check.py` ★
- ★`MECH/check_demo_struct_truth.py` (★第 165 行 `load_module(...)`★) + `MECH/check_hinge_fpc_truth.py` 读 `hw_cross_review_check.py` (★**注意: 这是另一个文件, 不在你这 8 个里, ★**不许碰它**★ — 它被 `check_demo_struct_truth.py` 与 `MECH/cavity_recalc_check.py` 用 md5 钉住 (★`e521387b87b0fcdf9f22d56f14199967`★)) ★
- ★`MECH/check_board_geom_caliber_drift.py` (★ISS-342 你自己建的漂移闸★) 扫 `fit_check_v3_30mm.py` 等 → ★**你迁完, 它的 scope A / scope B 命中数会变 ⇒ ★**必须重跑并把新数字回填到 `MECH/BOARD_GEOM_CALIBER_STATUS.md` (★main 00:1x 已订正过一次: scope A 命中 24 / 不计入 5 / 真数 19 · scope B 107 处 33 文件 — ★**你迁完这些数会再变, 所以要在迁完【之后】重读, 不许沿用 main 00:1x 那组数★) ★**

★**⑤ `MECH/check_board_geom_caliber_drift.py` 的当前读数 (★main 本机实跑, 你交卷时要给迁移后的新读数★) ★**:
★**`python3 MECH/check_board_geom_caliber_drift.py` ⇒ rc=2 (★有漂移, 这是预期的: 脚本仍绑 60×30·迁完应当漂移减少★) · 输出末行「[DRIFT] 未声明口径漂移: 107 处 / 33 个文件」 ★**
★**`python3 MECH/check_board_geom_caliber_drift.py --selftest` ⇒ rc=0, 末行 `ALL TESTS PASS` (★6 个用例全 PASS★) ★**

★**⑥ 这条【不】依赖老板拍板 (★老板那 9 件还在队列里, 本单不许拿它当阻塞项★) ★**:
★**main 已裁「迁」且已裁「迁法 = 双口径」⇒ ★**默认档留哪个由 U-1 定, 但【双口径本身】现在就能做 ⇒ 本单现在就能做 (★做完只切默认档, 不动判据本体★) ★**

---

## §1 本单要交付什么 (★四件, 不许跑题★)

★**① 那 5 个没有帧表的脚本, 改成双口径 (★逐个改·不许用统一大重构·不许改判据方向★) ★**
- ★**目标**: 每个脚本都能按「60×30 / RK3576」与「160×100 / RK3572」两档跑出判据 ★
- ★**★**怎么改 (★main 已想清, 你照做★)★★:
  - ★**参照已经做对的 3 个脚本的现成范式** (★`MECH/board_frame_feasibility.py` 的 `FRAMES` 三档表 + `MECH/jd_y0_feasibility.py` 的 `FRAMES` 三档表★) ⇒ ★**不要自己发明新的档位表结构** ★
  - ★**★**默认档怎么定 (★本单最容易踩的坑★)★★: ★**本单【不许自己拍默认档】** ⇒ ★**默认档 = 【保持现状 = 60×30 / RK3576】** ★★ ⇒ ★**理由 (★main 原文: 「板那一趟里不许临时改脚本·判据在那一趟期间必须冻结」+「老板拍完只切默认档」★) ⇒ ★**现在切默认档 = 把判据变了 = 板那一趟读数作废 ⇒ 恰恰是 main 要避免的那件事 ★★** ⇒ ★**你要做的是【把第二档补齐 + 默认档保持不动】, 把「切默认档」写成一条命令/一个参数, 留给 U-1 拍完后 main 来切 ★**
  - ★**★**判定方向不许变 (★本项目铁律★)★★: ★**60×30 档的判据结论必须与现在【逐字一致】** ★ ⇒ ★**你必须给出迁移前后的同档对照读数 (★60×30 档: 逐项数值不变★) 作为证据 ⇒ ★**这就是「双口径一次做完, 老板拍完只切默认档」的可自证形式 ★**
  - ★**★**`fit_check.py` 单独处理 (★main 实读它第 6 行自己写着「本脚本基线已作废 —— 现行版是 `MECH/fit_check_v3_30mm.py`」★) ⇒ ★**它已被自己的横幅标作废 ⇒ ★**你要么给它补同样的双口径, 要么明确写「本脚本是历史脚本, 不迁, 但它的旧口径仍在漂移闸的扫描口径里 ⇒ 你要把这个事实登记进 `MECH/BOARD_GEOM_CALIBER_STATUS.md` 的处置表** ★ ⇒ ★**选哪个都行, 但必须【说清 + 给依据 + 不许默默跳过** ★
  - ★**★**`cross_review_check.py` 的特别提醒 (★main 实读★)★★: ★**它第 26~29 行还留着「板宽 12→30 的迁版史」, 而现役板是 160×100 ⇒ 它的 `"board_w": 30.0` 要能表达两档 ⇒ ★**注意别把它跟 `MECH/hw_cross_review_check.py` 搞混 (★两个不同文件, 后者被 md5 钉住, **不许碰**★) ★

★**② 迁完重跑漂移闸, 把新读数回填 `MECH/BOARD_GEOM_CALIBER_STATUS.md` (★追加式·老字一字不删★) ★**
- ★**main 00:1x 已订正过一组数 (scope A 命中 24 / 不计入 5 / 真数 19 · scope B 107 处 33 文件) ⇒ ★**迁完文件集合又变了 ⇒ 计数必须重新实读, 不许沿用 main 那组数 ★★**
- ★**★**计数口径的老坑 (★main 00:1x 原文★)★★: ★**「扫描命中数会被【扫描器自己】污染」⇒ 漂移闸写出来的页 + 闸自己的 `.pyc` 都会进 scope A ⇒ ★**每次新增扫描器/清单页, 计数必然 +1/+2 ⇒ 计数必须每次重读, 不能沿用上一轮的数 ★** ★★ + ★**「`__pycache__` 混进扫描口径」本项目已踩两次 (★ISS-339 删 `HW/__pycache__` · 这次 `MECH/__pycache__`★) ⇒ 扫描口径必须显式排除 `.pyc` + `.bak` ★**
- ★**⇒ 你的订正必须是【追加式新段】, 把旧的那组数保留为历史, 并写明「本组数 = 迁完 + 重读后的真值, 口径 = 排除 `.pyc`/`.bak`」 ★**

★**③ 把「默认档 = 60×30」这件事写成可自证的开关 (★留给 U-1 拍完后 main 切★) ★**
- ★**你必须给出一条**确切命令** (★如某个 `--frame` / env 参数★) 让 main 能在 U-1 拍完后【只切默认档、不动判据本体】 ★ ⇒ ★**并证明: 切之前 60×30 档读数与现状逐字一致, 切之后 160×100 档读数与现役板口径自洽 ★** ⇒ ★**★**不许自己切默认档★ ★**

★**④ 一道机器闸, 让「单口径脚本」以后进不了板那一趟 (★只读 + 反向用例★) ★**
- ★**新建 `MECH/check_mech_dual_caliber_gate.py` (★**新建**★) ★**
- ★**它必须: ① 扫 `MECH/` 下这 8 个脚本 (★名单写死成这 8 个具体文件名, ★不许扫全目录★) ⇒ ② 逐个断言「同时含 60×30 档 与 160×100 档的标识」⇒ ③ 断言「默认档 = 60×30 (即当前默认值不被偷偷改掉)」⇒ ④ 顺带断言 `MECH/hw_cross_review_check.py` 的 md5 仍是 `e521387b87b0fcdf9f22d56f14199967` (★它是被两个闸钉住的文件★) ★**
- ★**★**方向纪律 (★本项目铁律★)★★: ★**只许【加严】不许【放宽】** ★ ⇒ ★**不许改 `MECH/check_board_geom_caliber_drift.py` 的判据方向 (★那个闸的 `--selftest` 必须仍 末行 ALL TESTS PASS·6 个用例全 PASS★) ★**
- ★**★**反向用例 (★必须有, 否则闸是装饰★)★★: ★**在 `tmp/` 副本上把某一个脚本的 160×100 档标识删掉 ⇒ 你的闸必须判红并点名那个脚本名 ⇒ 恢复 ⇒ 判绿 ★**
- ★**★**沙盒纪律★: 反向用例只在 `tmp/` 副本上做 ⇒ ★**真件 8 个脚本一个字节都不许在反向用例里被动 ★**

---

## §2 边界 (★违反任一条 = 本单不成立★)

★**① 零写板**: `HW/PCB/demo_mainboard.kicad_pcb` md5 必须仍 = `611b869e13518c3c023fb178f91a0075`, mtime 仍 = `2026-11-06 07:07:17.362193413` ★ ⇒ ★**本单【不许】碰板** ★
★**② 零落表**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 逐字节不变; ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 一个字节不许碰** ★
★**③ 只许改这 8 个脚本 + `MECH/BOARD_GEOM_CALIBER_STATUS.md` (追加式) + 新建闸 + 交卷页 + 分片** ⇒ ★**其余 MECH 文件一个字节都不许动 (★特别是 `MECH/hw_cross_review_check.py` [md5 钉住] · `MECH/check_board_geom_caliber_drift.py` [判据方向不许动] · `MECH/check_board_frame_candidate_compat_gate.py` · `MECH/check_board_frame_coords.py` · `MECH/check_onepass_mech_release.py` · `MECH/check_demo_struct_truth.py` · `MECH/check_hinge_fpc_truth.py` · `MECH/cavity_recalc_check.py`★) ★**
★**④ 零改别人的分片**: ★**`state/fragments/pm.yaml` (main 的) / `hw.yaml` / `sw.yaml` 一个字节不许碰** ★ ⇒ ★**本单只许写 `state/fragments/mech.yaml` ★**
★**⑤ 零改 `HW/` 任何文件** (★`HW/check_s8_target_list.py` 等板侧判据一个字都不许动★) ★
★**⑥ 不许自己拍默认档** (★默认档 = 保持 60×30 现状·只提供切档开关·切档权归 U-1 拍完后 main★) ★
★**⑦ 不许删 60×30 档** (★它是历史口径·删了等于抹掉 11-11 那一段的设计依据★) ★
★**⑧ 不许外发**: ★**零邮件 / 零询价 / 零问询 / 零采购 ★** ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ★** ⇒ ★**没有「批一句可以发」这个选项 ★**
★**⑨ 不许替老板拍板**: ★**本单【不新增】任何老板拍板项 ★** ⇒ ★**U-1 (这一趟画哪块物理产品) 还在老板队列里 ⇒ 本单只做「两档都备好」, 不许替他定默认档 ★**
★**⑩ 引用零假引用**: 交卷页里引用的每个 `MECH/*` / `HW/*` / `state/*` / `logs/*` 文件必须逐个在盘 ⇒ ★**交卷前自检一次, 输出贴进 §B6 ★**

---

## §3 交卷物 (★N 件, 缺一件即不算交卷★)

★**① 交卷页 `HANDOFF/2026-11-23_mech-lead_ISS345_8脚本迁双口径.md` (★**新建**★) ⇒ ★**B1 结论摘要 / B2 验收标准逐条自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令 ★**六块齐全 (★`state/gate_check.py` 的 `REQUIRED_BLOCKS` 就是这 6 块 + 证据分级标签 `[实测]/[官方]/[推算]/[0数据]`★) ⇒ ★**先落骨架再填内容 (★先 write 六个标题, 再逐块填·★不许一次性 write 大段★) ★**
★**② 5 个脚本的双口径改造 (★落在真件★) + 3 个已有帧表脚本的核对结论 (★写进交卷页, 不许重写★) ★**
★**③ `MECH/BOARD_GEOM_CALIBER_STATUS.md` 的 scope A / scope B 真数追加式订正 (★老字一字不删·附老前缀 md5 前后对比 + `diff` 输出★) ★**
★**④ 新闸 `MECH/check_mech_dual_caliber_gate.py` + 它的反向用例读数 (★落在 `logs/iss345/`) ★**
★**⑤ `state/fragments/mech.yaml` 登记 (★**只走 `python3 state/frag_write.py --agent mech-lead`★·零重复 key★) ⇒ ★**`grep -c iss345 state/fragments/mech.yaml` ≥ 3 ★**
★**⑥ `logs/iss345/` 原始输出 (★机器生成的命令输出, 一条命令能复现★) ★**

★**★必跑命令 (★全部是本机实存路径, `state/check_brief_commands.py --brief-file` 已验 rc=0★)★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 MECH/check_board_geom_caliber_drift.py ; echo "DRIFT_RC=$?"
TMPDIR=$PWD/tmp python3 MECH/check_board_geom_caliber_drift.py --selftest ; echo "DRIFT_SELFTEST_RC=$?"
TMPDIR=$PWD/tmp python3 MECH/check_board_frame_candidate_compat_gate.py ; echo "COMPAT_RC=$?"
TMPDIR=$PWD/tmp python3 MECH/check_onepass_mech_release.py ; echo "MECHREL_RC=$?"
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```

★**★交卷前必须跑 (§2 边界自证 + 主线闸) ★★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"     # ★rc 必须 0★
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"   # ★rc 必须 0 且 Q1 = 18/18★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
md5sum MECH/hw_cross_review_check.py   # ★必须仍 = e521387b87b0fcdf9f22d56f14199967★
python3 state/frag_write.py --agent mech-lead --show | head -5
```
★**★回复 ≤ 500 字 + 4 行读数 (`DRIFT_SELFTEST_RC` / `COMPAT_RC` / `GATE_RC` / `BOARD_MD5`) + 迁完 scope A / scope B 的新计数 + 反向用例是否判红★★**

---

## §4 交卷时必须回答 main 的 4 个问题

★**① 「5 个没有帧表的脚本, 你每个的 160×100 档数据从哪来? (★台架板真实数 vs 推算, 逐条标证据等级★)」 ★**
★**② 「60×30 档迁移前后逐字一致的对照读数在哪? 逐个脚本给」 ★**
★**③ 「迁完 scope A / scope B 的新计数是多少? 与 main 00:1x 那组 (24/5/19 · 107 处 33 文件) 差在哪? 差的原因是文件集合变化还是脚本口径变化?」 ★**
★**④ 「切默认档的那条确切命令是什么? (★给 main 在 U-1 拍完后用★)」 ★**

★**★额外纪律 (★派活方统一加, 一条都不许少★)★★**:
★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★) ★**
★**② 只写本任务允许的文件, 不碰别人的 (★特别是 `state/fragments/pm.yaml` = main 的分片★) ★**
★**③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标 (★台架板几何必须是 [实测] + 出处, 不许 [推算] 糊过去★) ★**
★**④ 不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项 ★**
★**⑤ 交卷前跑 `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复 ★**
