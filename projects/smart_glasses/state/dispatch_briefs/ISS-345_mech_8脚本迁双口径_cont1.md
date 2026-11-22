★★★★【main 2026-11-23 02:1x · ★★ISS-345 cont1 · ★★PCB 线 · MECH 双口径迁移【第 1 批: 2 个脚本】· 纯脚本改造 + 证据落盘 + 交卷页 · 零写板 ★★】★★★★

★**上一轮 (会话 `03afe97e-e265-42bd-8da7-36ec76ab97cb`, 01:03→01:55) 被【父 run 连带 abort】掐死 ⇒ ★**它 52 分钟全耗在探索上 (8 个脚本全读 + 板面探针), 真件 8 个脚本一个字节都没改** ★
★**(main 02:1x 实测: `MECH/pinset2_mech_check.py` 与 `tmp/iss345_base/pinset2_mech_check.py` `diff` = IDENTICAL, `grep -c B160x100` = 0, mtime 仍是 11-11 17:26 ⇒ 上次那个 edit 被 abort, 没有半截改动留在盘上★)**

★**★本单 = 从那个断点接着干, 不许从头重做探索★ ★**

★**主任务书 (★权威, 逐字照用, 不许自己改写★)**: `state/dispatch_briefs/ISS-345_mech_8脚本迁双口径.md`
★**它 §0~§4 全部继续有效 (★口径 / 边界 / 交付 / §4 的 4 问 / 派活纪律, 一条都不许打折★) ★**
★**本单只是把它【切成第 1 批】, 切批理由写在 §B0 ⇒ §3 的 6 件交付物在第 1 批里只交一部分 ⇒ ★**交不全的必须在交卷页 §B5 逐条写明「还差什么、为什么没做完」★**

---

## §B0 · 为什么切批 (★main 2026-11-23 02:1x 实测★)

★**上一轮 52 分钟 0 字节改动 ⇒ 单轮扛 8 个脚本 = 单轮 0 产出 ⇒ ★**本轮只扛【第 1 批 = 2 个脚本 + 对照证据 + 交卷页 + 分片】, 保证单轮真正落地★ ★**
★**第 2 批 (★本单【不许】做, 但 §B5 要写清还差什么★)**: ★`fit_check_v3_30mm.py` / `fit_check.py` / `cross_review_check.py` 三个脚本 + ★**新建**闸 `MECH/check_mech_dual_caliber_gate.py` (★第 2 批才产出·本批不建★) + `MECH/BOARD_GEOM_CALIBER_STATUS.md` 的 scope A/B 真数追加式订正 + 漂移闸迁后重跑★**

---

## §B1 · 上一轮留在盘上的东西 (★直接用, 不许重跑那 52 分钟的活★)

| 在哪 | 是什么 | 怎么用 |
|---|---|---|
| `logs/iss345/00_drift_PRE.txt` (25,652 B @ 01:27) | 漂移闸 `MECH/check_board_geom_caliber_drift.py` 的**迁移前**原始输出 | ★**= 「迁移前基线」** ⇒ 迁后同命令再跑一次, 两份对比即证据 ★ |
| `logs/iss345/base_pinset2_mech_check.txt` (10,022 B @ 01:04) | `pinset2_mech_check.py` 迁移前**原始 stdout** (★横幅逐字: 「板 60.00×30.00×1.00mm / SoC RK3576 占位 X[15.00,32.20]×Y[6.95,23.05]」★) | ★**= 本单脚本①的迁移前基线★** |
| `logs/iss345/base_skeleton_section_check.txt` (10,026 B @ 01:04) | `skeleton_section_check.py` 迁移前**原始 stdout** (★横幅: 「ISS-192 迁版: 60×15 / RK3588 8×10 ⇒ 60×30 / RK3576 17.20×16.10」★) | ★**= 本单脚本②的迁移前基线★** |
| `logs/iss345/base_fit_check.txt` / `base_fit_check_v3_30mm.txt` / `base_cross_review_check.txt` | 其余 3 个脚本的迁移前输出 | 第 2 批用 ★ |
| `tmp/iss345_base/*.py` (5 个脚本的迁移前副本 @ 01:04) | 沙盒副本 | ★**改完拿它 `diff` 出「只增不改」证据★** ★**交卷页里引用它必须写明「沙盒副本·非交付物」★** |
| `tmp/iss345_base/mech_md5_pre.txt` (8,915 B @ 01:27) | MECH 域全文件迁移前 md5 | ★**迁完重算, 交卷页列出「本单改了哪几个」★** |
| `tmp/iss345_base/pj_before.json` (01:21) | `pinset2_mech_check.py` 的 JSON 产物迁移前 | ★**派生物, 同 base 用法★** |
| `tmp/iss345_base/probe_som*.py` / `probe_board.py` | 板面探针 (★SoM 座 `J_SOM_P1..P4` 占位 / 板框 / 层数 / np_thru_hole 焊盘★) | ★**160×100 / RK3572 档的数据来源之一 (★配合 §B2 的权威页★)** |
| `HANDOFF/2026-11-23_mech-lead_ISS345_8脚本迁双口径.md` (949 B) | 交卷页骨架 (★B1~B6 六块标题已在, 每块内容都是「(待填)」★) | ★**不许新建第二个交卷页 ⇒ 在这一页上填★** |
| ★**真件 8 个脚本** ★ | ★**仍与迁移前逐字节相同 (★main 02:1x 实测✔★)** | ★**从零开始改★** |

---

## §B2 · 160×100 / RK3572 档的数据从哪来 (★唯一权威, 不许自己拍★)

★**这三处就是本档的权威来源 (★main 2026-11-23 02:1x 本机实读✔★)**:

1. ★**帧 id + 板尺寸 / 层数 / 板厚** ⇒ `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES` JSON 块 (行 146 起):
   - ★`B160x100` = 160.00 × 100.00 / 8 层 / 1.60 mm / `current: true` ★
   - ★`F30A` = 60.00 × 30.00 / 6 层 / 1.00 mm / `current: false` ★
   - ★`P60x15` = 60.00 × 15.00 / 6 层 / 1.00 mm / `current: false` ★
   ★**⇒ 这三档的 id 写法必须与该页逐字一致 (★闸脚本按 id 判★) ★**
2. ★**SoM 承载区实测占位** ⇒ 同页 §3:
   - ★**焊盘实体占位**: X 15.10..68.90 / Y 7.61..54.39 = 53.80 × 46.78 mm ★
   - ★**封装外形占位**: X 13.65..70.35 / Y 7.61..54.39 = 56.70 × 46.78 mm ★
   - ★4 座 `J_SOM_P1..P4` 各 100 焊盘 / 共 400 焊盘 ★
   - ★证据等级 `[实测]` (★pcbnew `GetBoundingBox()` + 纯 python 逐焊盘解析, 两法逐位一致★) ★
3. ★**板面实读** ⇒ `HW/PCB/demo_mainboard.kicad_pcb` (★**只读, 不许改**) + `HW/PCB/demo_mainboard_params.json` (★`board`: width 160.0 / height 100.0 / layers 8 / thickness 1.6; `corner_radius_mm` 3.0★) ★

★**⇒ 你 160×100 档的每一个数都要能指回上面三处之一 ⇒ 逐个标 `[实测]` (★写清文件 + 行号★) 或 `[推算]` (★写清推算链★) ⇒ ★**不许写 `[0数据]` 糊过去★ ★**
★**⇒ RK3576 档 (60×30) 的现值继续从两个脚本自己的常量里取 (★不改它★) ⇒ 两档并存, 不是把旧档改掉★**

---

## §B3 · 怎么改 (★范式照抄, 不许自己发明★)

★**参照已经做对的 3 个脚本的现成范式 (★上一轮已定位到行号★)**:
- ★`MECH/board_frame_feasibility.py` 行 100~130 ⇒ `FRAMES` 三档表 ★
- ★`MECH/jd_y0_feasibility.py` 行 166~182 ⇒ `FRAMES` 三档表 ★
- ★`MECH/board_port_opening_s6_check.py` 行 389~395 ⇒ `frames` 三档表 ★

★**做法 = 给这两个脚本各加一张同构的档位表 + 把硬编的 `PCB_L` / `PCB_W` / `PCB_T` 与 RK3576 封装尺寸改成【按档取值】+ 给一条【切默认档的命令 / 参数】★**
★**★默认档 = 保持现状 60×30 / RK3576 (★本单【不许自己拍默认档】· 切档权归 U-1 拍完后 main★)★★**
★**★60×30 档的判据结论必须与迁移前【逐字一致】★★ ⇒ ★**证据 = `logs/iss345/base_*.txt` (迁移前) vs 本单迁移后同命令输出 (迁移后) 的 `diff` ★**
★**⇒ 优先做到【整份输出逐字节相同】; 若你为了让口径可见而在横幅/输出里加了字 (★例如标出当前档 id★) ⇒ ★**那就在交卷页逐条列出新增行, 并给出「除这几行外逐字一致」的 diff 证据 (★不许含糊说「差不多」★)★**

★**★两个脚本的外部依赖 (★改坏了会连累别的闸, 交卷前必须跑★)★★**:
- ★`MECH/pinset2_mech_check.py` ⇒ 被 ★`MECH/check_board_frame_candidate_compat_gate.py` 行 902~903 调★ ⇒ ★**它必须仍能按原样被调 (★默认行为不许变★) ⇒ 交卷前必须跑 `COMPAT_RC` 并贴 rc★** ★
- ★`MECH/skeleton_section_check.py` ⇒ 被 ★`MECH/iss127_h_chain_check.py` 行 50~70 import★ ⇒ ★**同一条纪律★** ★
★**⇒ 这两个脚本的「默认档 = 60×30」不是可选项, 是【不许破坏既有消费方】的硬约束★**

---

## §B4 · 本批 (cont1) 只交 5 件 (★不许跑题★)

① ★**`MECH/pinset2_mech_check.py`** 改双口径 (★60×30 / RK3576 与 160×100 / RK3572 两档都在·默认档仍 60×30★) ★
② ★**`MECH/skeleton_section_check.py`** 改双口径 (★同上★) ★
③ ★**迁移前 / 后对照读数**落 `logs/iss345/`: ★`10_pinset2_POST.txt` / `11_skeleton_POST.txt` + 两份 `diff` 输出 (★命令见 §B6★) ★
④ ★**交卷页**: ★在 `HANDOFF/2026-11-23_mech-lead_ISS345_8脚本迁双口径.md` 上填 B1~B6 (★★**B5 必须逐条写「本批没做的还差什么」★★ ⇒ **先填骨架后填内容**★) ★
⑤ ★**`state/fragments/mech.yaml` 登记** (★**只走 `python3 state/frag_write.py --agent mech-lead`★·零重复 key★) ⇒ ★**`grep -c iss345 state/fragments/mech.yaml` ≥ 3★**

★**★第 2 批 (★本单【不许】做·但 §B5 要写清还差什么★)★★**: ★`fit_check_v3_30mm.py` / `fit_check.py` / `cross_review_check.py` 三个脚本 + ★**新建**闸 `MECH/check_mech_dual_caliber_gate.py` (★第 2 批才产出·本批不建★) (★含反向用例★) + `MECH/BOARD_GEOM_CALIBER_STATUS.md` 的 scope A / scope B 真数追加式订正 + `MECH/check_board_geom_caliber_drift.py` 迁后重跑 (★主任务书 §4 第 ③ 问所需的那组新计数★)★

★**★派生物提醒 (★别当成「越界改文件」★★)**: ★`MECH/pinset2_mech_check.json` 是脚本跑出来的派生物 (★上一轮跑过它, mtime 01:21★) ⇒ ★**本单改脚本后它会变 ⇒ 那是【派生物变化】, 必须在交卷页里列出并说明 ⇒ ★**但你不许手改它★ (★只能由脚本重新生成★)★**

---

## §B5 · 铁律 (★上一轮就是这么死的★)

★**① 先落盘, 后填内容**: ★**交卷页 B1~B6 六块标题已在盘 (949 B) ⇒ 先把每块的一行结论落盘, 再逐步填细节 ⇒ ★**被掐也不许零产出★ ★**
★**② 改一个脚本就立刻落一次盘 + 立刻存一次对照输出 ⇒ ★**别攒到最后一次性 edit (★上一轮死在「攒到最后」上★)★**
★**③ 交付顺序 (★被掐就按这个顺序交已有部分★)★**:
- ★① `pinset2_mech_check.py` 改完 + 落盘 + 对照输出 + diff ★
- ★② `skeleton_section_check.py` 改完 + 落盘 + 对照输出 + diff ★
- ★③ 交卷页填 B1 / B2 / B3 ★
- ★④ 交卷页填 B4 / B5 / B6 (★B5 写第 2 批清单★) ★
- ★⑤ 分片登记 (`frag_write.py`) ★
★**⇒ 宁可只交第 ①② 步, 也不许零产出★**
★**④ 沙盒纪律**: ★**故意破坏类实验 (反向用例) 只许在 `tmp/` 副本上做 ⇒ 真件在【对照跑】里可以跑, 但不许在真件上做「故意弄坏」的实验★**
★**⑤ 零写板**: ★`HW/PCB/demo_mainboard.kicad_pcb` md5 仍 = `611b869e13518c3c023fb178f91a0075` / mtime 仍 = `2026-11-06 07:07:17.362193413` ⇒ ★**本单不许碰板★**
★**⑥ 零落表** (★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 逐字节不变★) ★**零改别人分片** (★`pm.yaml` / `hw.yaml` / `sw.yaml` 一个字节不许碰★) ★**零改既有闸的判据方向** (★主任务书 §2 十条边界全部有效★) ★
★**⑦ 零外发**: ★**零邮件 / 零询价 / 零问询 / 零采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★**
★**⑧ 不许替老板拍板**: ★**本单【不新增】任何老板拍板项 ⇒ U-1 (这一趟画哪块物理产品) 还在老板队列里 ⇒ 本单只做「两档都备好」, 不许替他定默认档★**

---

## §B6 · 必跑命令 (★路径本机实存, 已过 `state/check_brief_commands.py --brief-file`✔★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 MECH/pinset2_mech_check.py > logs/iss345/10_pinset2_POST.txt 2>&1 ; echo "PINSET2_RC=$?"
TMPDIR=$PWD/tmp python3 MECH/skeleton_section_check.py > logs/iss345/11_skeleton_POST.txt 2>&1 ; echo "SKELETON_RC=$?"
diff logs/iss345/base_pinset2_mech_check.txt logs/iss345/10_pinset2_POST.txt ; echo "DIFF_PINSET2=$?"
diff logs/iss345/base_skeleton_section_check.txt logs/iss345/11_skeleton_POST.txt ; echo "DIFF_SKELETON=$?"
TMPDIR=$PWD/tmp python3 MECH/check_board_frame_candidate_compat_gate.py ; echo "COMPAT_RC=$?"
TMPDIR=$PWD/tmp python3 MECH/check_board_geom_caliber_drift.py ; echo "DRIFT_RC=$?"
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```

★**交卷前必须跑 (★rc 必须 0★)★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"     # ★rc 必须 0★
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"   # ★rc 必须 0 且 Q1 = 18/18★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
md5sum MECH/hw_cross_review_check.py   # ★必须仍 = e521387b87b0fcdf9f22d56f14199967★
python3 state/frag_write.py --agent mech-lead --show | head -5
```

---

## §B7 · 回复格式 (★≤ 500 字 + 6 行读数★)

★**回复里必须给**:
① ★`PINSET2_RC` / `SKELETON_RC` / `DIFF_PINSET2` / `DIFF_SKELETON` / `COMPAT_RC` / `GATE_RC` / `BOARD_MD5` 七行读数 ★
② ★**60×30 档迁移前后是否逐字一致** (★逐脚本给结论 + diff 证据★) ★
③ ★**160×100 档每个数的出处** (★文件 + 行号★) ★
④ ★**切默认档的那条确切命令** (★留给 main 在 U-1 拍完后用★) ★
⑤ ★**本批没做的还差什么** (★第 2 批清单★) ★
⑥ ★**第 4 问的答案**: ★`fit_check_v3_30mm.py` / `fit_check.py` / `cross_review_check.py` 三个脚本本批没迁 ⇒ ★**只准写「本批未做 + 第 2 批做」, 不许编结论★ ★**

★**★额外纪律 (★派活方统一加, 一条都不许少★)★★**:
★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★) ★**
★**② 只写本任务允许的文件, 不碰别人的 (★特别是 `state/fragments/pm.yaml` = main 的分片★) ★**
★**③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标 (★台架板几何必须是 `[实测]` + 出处, 不许 `[推算]` 糊过去★) ★**
★**④ 不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项 ★**
★**⑤ 交卷前跑 `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复 ★**
