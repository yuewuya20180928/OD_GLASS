# ISS-376 · hw-lead · 「板那一趟」`J_DEBUG` 换官方 1×4 THT land 的**落位可行性**穷举（现位放不进 ⇒ 挪哪 / 挪多大）· 纯分析 + 沙盒预演 + 新建闸 · 零写板

★★**题**: ★**ISS-373 (★2026-11-23 23:38 交卷·2026-11-24 00:5x 已签收 verified★) 的沙盒实测已经把「那一趟换 91 件」这条路【卡死在一个具体的物理点上】: ★**官方 1.27mm 4×THT land 放不进 `J_DEBUG` 现位** ⇒ ★**4 个 0.65 钻孔与板面既有过孔冲突 ⇒ DRC `hole_to_hole` 由 0 变 4** ★ ⇒ ★**⇒ 这一单 = 把「挪哪 / 挪多大 / 挪完还剩什么」这三个问题【用机器算出来】, 交 main 裁「那一趟换不换 land」** ★★

★**原任务书全文 (★判据/边界/交付物定义全部仍有效·必读★)**: ★**本单无原任务书 (★这是新开单·下面 §二 就是完整任务书★)** ★

---

## ★★一 背景 (★main 2026-11-23 23:2x~2026-11-24 00:5x 本机实读 + 本机实算 · **不抄任何 agent 报告** · 每条都可复跑★) ★★

★**★① `J_DEBUG` 现位 (板读) ★★**: ★**封装原点 `(144.3000, 58.0000)` · orient `0.0` · 4 个 pad 全 SMD `0.2750 × 0.9000` 全 `shape=1 (RECT)` · pad X = `142.2000 / 142.7000 / 143.2000 / 143.7000` (★pitch `0.5000`★) · net = `JTAG_TCK` / `JTAG_TMS` / `JTAG_TDI` / `JTAG_TDO` · 铜箔 X `142.0625..143.8375` (宽 `1.7750`) × Y `56.1500..57.0500` (`0.9000`) · fab 名义 `6.00 × 4.00` (★F.Fab 层 bbox 实读 X `141.2500..147.3500` × Y `55.9500..60.0500`★)** ★

★**★② 官方 1×4 THT land 实读 (★读盘上 `.kicad_mod`·不抄文档★) ★★**: ★`/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ⇒ ★**pad "1" `thru_hole rect` (at `0 0`) size `1 × 1` drill `0.65` · pad "2" `thru_hole circle` (at `0 1.27`) · pad "3" `thru_hole circle` (at `0 2.54`) · pad "4" `thru_hole circle` (at `0 3.81`) · ⇒ 四个 pad 沿【局部 Y】排 ⇒ 局部 Y 跨度 `3.81`; `F.CrtYd` `fp_rect` (`-1.55 -1.14` .. `1.55 4.95`) = `3.10 × 6.09`; `F.Fab` 线框 X `-1.05..1.05` / Y `-0.635..4.445` = `2.10 × 5.08`** ★

★**★③ 板面 DRC 约束 (★读 `HW/PCB/demo_mainboard.kicad_pro` 的 `board.design_settings.rules`·真值★) ★★**: ★**`min_hole_to_hole` = `0.25` · `min_hole_clearance` = `0.25` · `min_through_hole_diameter` = `0.3` · `min_via_diameter` = `0.5` · `min_via_annular_width` = `0.1` · `min_track_width` = `0.2`** ★

★**★④ ★★ISS-373 沙盒 S2b 实测到的【那一趟换 91 件】的物理死结★★**: ★**PTH pad1 (`144.3000, 58.0000`) vs via `JTAG_TDO` (`143.7000, 57.9500`) 孔净距 `0.1271` (★要求 ≥ `0.25`★) · PTH pad3 (`146.8400, 58.0000`) vs via `XTAL_OUT` (`146.9500, 57.9500`) 孔净距 `0.0000`** ⇒ ★**⇒ `hole_to_hole` 违规由 `0` → `4`** ★ ⇒ ★**这两个过孔的坐标我本机 00:4x 实读过 (★`bash state/pcbnew_py.sh` 读 via 位置★): `XTAL_OUT` 在 `(142.2000, 53.2000)` 与 `(146.9500, 57.9500)` · `JTAG_TDO` 在 `(143.7000, 57.9500)` 与 `(142.4500, 54.7000)` · `JTAG_TCK` 在 `(138.7000, 54.7000)` · `JTAG_TMS` 在 `(145.2000, 54.9500)` 与 `(147.2000, 54.4500)` · `XTAL_IN` 在 `(141.2000, 58.9500)` ⇒ 全部 via 直径 `0.6000` / 钻孔 `0.3000`★**

★**★⑤ ISS-373 沙盒实测的另两条硬读数 (★你【不要重做】·直接用★) ★★**:
- ★**新 land 的铜箔 X 宽 = `4.8100`** (★`3 × 1.27 + 1.00`★) —— 官方 4 个 1.00 宽 THT pad 的铜箔包络 ⇒ ★**比现位 `1.7750` 宽出 `3.0350`** ★
- ★**落盘后 KiCad 连通性重建把 63 段 `JTAG_TDO` 走线改归 `JTAG_TCK`** (★S1: `JTAG_TCK` 34 段 / `JTAG_TDO` 63 段 ⇒ S2b: `JTAG_TCK` 97 段 / `JTAG_TDO` 0 段★) ⇒ ★**⇒ 那 4 条 JTAG 走线的端点脱网 ⇒ 必须重接** ★

★**★⑥ 方向侧的结构侧账 (★ISS-371 已算·你只需知道结论·不许改它的地界★) ★★**: ★**`J_DEBUG` 换官方 land 后: 必须清空区 X 宽 `4.0850 → 4.8100` · 最外侧焊盘每边超出清空区 `0.3625` ⇒ 铜箔进清空区 · 但方向仍过 `CRIT` `0.60` (余量 `3.99×`)** ⇒ ★**⇒ 板侧落位挪动【不会】把结构侧方向推翻 (★方向本来就没红★) ⇒ 你这一单要回答的是【板侧能不能挪得下 + 挪完还剩什么】, 不是【结构侧行不行】** ★

---

## ★★二 你这一单要交的东西 (★两件 + 交卷页 + 分片★) ★★

★**① ★新建★ 一页 `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` (★本单产出物★)** ⇒ ★**必须含 (★每个数带复跑命令·★别只给结论·★给出「可行区」而不是「一个点」★)**:

1. ★**§0 一句话结论 + 三问回答**: ★**(a) 现位能不能放下? (b) 挪得下吗? (c) 挪完那一趟还剩几件没解决?** ★
2. ★**§1 「放不下」的量化账**: ★**① 现位 (origin `(144.3000, 58.0000)`, rot `0`) 的逐 pad 冲突表 (★每个 pad: 坐标 · 钻孔 `0.65` · 与哪个 via / 哪个 pad 冲突 · 孔净距实测值 · 要求 ≥ `0.25` · 差多少★) · ② 与官方 land 局部坐标 (pad1 `(0,0)` / pad2 `(0,1.27)` / pad3 `(0,2.54)` / pad4 `(0,3.81)`) 的换算关系 (★rot `0` / `90` / `270` 三种朝向各自的 pad 绝对坐标★) ★**
3. ★**§2 落位可行域穷举 (★本单正题★)**: ★**在 `J_DEBUG` 周边逐个候选落位 (★由你自己定候选网格·但必须写清网格步长与覆盖范围★) 上, 对每个候选算: ★① 四个 THT 孔与板面【所有 via 孔 + 所有已有 THT 孔】的孔净距 (★要求 ≥ `0.25`★) ② 铜箔包络 (X `4.8100` 宽) 与板面既有过孔铜箔/走线的净距 ③ fab 外框 (`5.08 × 2.10` rot90 / `2.10 × 5.08` rot0) 与板边/板框的关系 ④ 三个朝向各自的最优候选 (★坐标 + 余量 + 代价★)** ⇒ ★**⇒ 交付的是【可行区】(★哪一段区间放得下★) + 【最优落点】(★带余量★), 不是单一坐标★** ★
4. ★**§3 挪完还剩什么 (★代价账★)**: ★**① 为放下它, 必须挪/让开的板面既有对象清单 (★过孔 `XTAL_OUT` / `JTAG_TDO` / `XTAL_IN` / 走线段 / 其他器件·逐项给坐标 + 为什么非挪不可★) ② 每挪一件的连带代价 (★走线要重画多少段? 那 4 条 JTAG 走线脱网怎么接? 开口净宽受不受影响?·★只算不拍★) ③ 与 §2 可行域的关系 (★存在一个【一个都不用挪】的落点吗?★)** ★
5. ★**§4 未决项 (★只登记不代拍★)**: ★**逐条写清「要谁回答什么」★** ⇒ ★**至少要含: ★**① 「那一趟换不换 land (90 件 vs 91 件)」⇒ 归 main 裁 (★你只给落位侧的代价账★) ② 要不要挪 `XTAL_OUT` / `JTAG_TDO` 过孔 ⇒ 归 main + 板侧结构侧 ③ 「挪落位」会不会把调试口罩开口挤掉 ⇒ 归 mech-lead (★你只给几何量★)****
6. ★**§5 复跑命令** + ★**§6 边界自证** ★

★**② ★新建★ 一条闸 `HW/check_jdebug_land_fit.py` (★本单产出物★)** ⇒ 判据 **L0~L8** (★每条 fail-closed★):
| # | 判据 | ★**不许写死的**★ |
|---|---|---|
| L0 | ★**官方 1×4 THT land 的 pad 坐标 / 形状 / 钻孔 / fab / courtyard 必须与盘上 `.kicad_mod` 实读一致** (★自己解析★) ★ | ★不许把 `3.81` / `0.65` / `4.8100` 写死成常量 ★ |
| L1 | ★**板面 DRC 的 `min_hole_to_hole` / `min_hole_clearance` 必须从 `.kicad_pro` 实读** (★真值 `0.25`·★不许写死★) ★ | |
| L2 | ★**§2 可行域表逐格与闸自己实算一致** (★孔净距 / 净距 / fab / 余量★) ★ | |
| L3 | ★**§1 冲突表逐条可复算** (★现位 pad ↔ via 的孔净距★) ★ | |
| L4 | ★**三个朝向 (rot 0 / 90 / 270) 的坐标换算必须由脚本自己算** (★不许手算旋转矩阵·★用 `FOOTPRINT.SetOrientationDegrees` 在真 board 上算★) ★ | |
| L5 | ★**§2 必须给出【区间/可行区】而不只是【一个点】** ⇒ ★**只给一个坐标 ⇒ 红** (★防"就试了一个点就下结论"★) ★ | |
| L6 | ★**§3 的代价清单每条必须带坐标** ⇒ ★**只写"要挪过孔"不带坐标 ⇒ 红** ★ | |
| L7 | ★**板面零写板自证** (★md5 / mtime / size 三项 == `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`★) ★ | |
| L8 | ★**证据等级五级白名单 + 零挂起措辞 + 判据句/事实句分开 + 零挂链** (★自证 `grep -c check_jdebug_land_fit state/gate_check.py` == 0★) ★ | ★挂不挂归 main★ ★ |

★**★必须带 `--selftest` (★≥8 条反向用例·每条自证「红的是目标那一条, 其余仍绿」★)★★** ★**其中 ≥2 条针对本单最核心的病根 (★"只试一个落点就宣布不可行 / 可行"★)★**: ★**① 把 §2 可行域表的区间改成单个点 ⇒ L5 红 ② 把 §1 里某条冲突的孔净距改小 ⇒ L3 红 (★证明闸真在读你自己的数★) ③ 把 L0 的期望 land 几何篡改 ⇒ L0 红** ★

★**③ 沙盒预演 (★只落 `tmp/iss376_sbx/` + `logs/iss376/`★)**: ★**用 `bash state/pcbnew_py.sh` (★本机 KiCad 10.0.8★) 在【板副本】上做, 真板零改动★** ⇒ ★**S0**: 现位基线 (★四个 SMD pad 坐标 + 铜箔宽 + 净距, 用来证明你的读数脚本跟板面对得上★) · ★**S1**: 官方 land 装现位 (★rot `0`·rot `90`·rot `270` 各一次★) 实测孔净距 (★必须能重现 `0.1271` 与 `0.0000` 这两个数·★对不上就停下查你的脚本★) · ★**S2**: 候选落位扫描 (★按你自己定的网格★) 出可行域 · ★**S3**: 最优落点实测 (★装上去实测孔净距 + 铜箔净距 + DRC `hole_to_hole` 类计数·★真板副本的 DRC 跑法可参考 `state/kicad.sh pcb drc --output <json> --severity-error --severity-warning --format json <板副本>★)** ★

★**★沙盒纪律 (★一条不许破★)★★**: ★**副本只落 `tmp/iss376_sbx/`** · ★**不许写真板** (★板 md5 开工前/交卷后各打一次★) · ★**不许跑会重铸随机 UUID 的门禁去"验"板** (★`state/check_sch_pinfull.py` / `state/check_sch_erc.py` 内部会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 重铸 UUID ⇒ 任何 md5 比对都失效 ⇒ **板 md5 只能在你自己的脚本前后打, 不能跑完门禁再打**★) ★

★**④ 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md` (★本单产出物★)**: ★**B1~B6 六段齐全 + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★** ⇒ ★**§B5 要写明「本单是 ISS-373 交卷后开的续单 (★ISS-373 已签收 verified★)」** ★

★**⑤ 分片 `state/fragments/hw.yaml`**: ★**只走 `python3 state/frag_write.py --agent hw-lead`** (★写前写后各记一次 md5·期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」·不许静默覆盖★) ⇒ ★**登记: 产出物 (★那页 + 那闸 + 交卷页★) + 3 条 `interface_claims` (★现位落位账 / 可行域区间 / 最优落点★) + 1 条 `needs_from` (★要 main 裁「那一趟换不换 land (90 vs 91)」·**key 要唯一**★) ★**

---

## ★★三 边界 (★一条不许越★) ★★

★**零写板** (★真板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次★) ★
★**零落表** (★`HW/netlist_v1.csv` md5 `6aee500e60ba0732f83a9cf557ba90ab` · `HW/netlist_v1_pins.csv` md5 `9174309df1ec9411ac8e8d9e80ee386a` · `HW/BOM_v1.csv` md5 `5b9993992405904a60ac96a020b375d8` 一律只读★) ★
★**零改既有闸** (★`HW/check_onepass_s10_swap_set_truth.py` (★ISS-373 已签收件★) · `HW/check_fp_libid_truth.py` (★ISS-369 已签收件★) · `HW/check_onepass_preflight_coverage.py` · `HW/check_pcb_nets.py` · `MECH/check_jdebug_1p27_clearance.py` (★ISS-371 已签收件★) · `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ★
★**零改既有页面正文** (★`HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` (★ISS-373 已签收件★) · `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` (★ISS-369 已签收件★) · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★ISS-371 已签收件★) —— ★**本单只新写一页 + 一条闸, 既有页面一个字都不许动**★ ⇒ ★**要订正既有页面的部分 ⇒ 写成「追加式订正块」放进【你自己那一页】的 §4, 由 main 决定要不要往既有页面落★**) ★
★**零挂链** (★本单新闸【不许】挂进 `state/gate_check.py`★) ★
★**只写自己的分片 `state/fragments/hw.yaml`** ★
★**沙盒只落 `tmp/iss376_sbx/` + `logs/iss376/`** ★
★**不代老板拍板** · **不代 main 拍** (★「那一趟换不换 land」是 main 的裁决权 ⇒ 你只给落位侧的代价账与可行域★) ★
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 ⇒ **全靠自己查·查不到写降级方案·不许写「等原厂回信」**★) ★
★**不自签 `state/issue_log.yaml`** (★台账由 main 签收★) ★
★**零推 GitHub** (★由独立的 5 小时同步 job 负责★) ★

---

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 HW/check_jdebug_land_fit.py                    # 新闸 ⇒ rc=0
python3 HW/check_jdebug_land_fit.py --selftest          # 新闸自测 ⇒ rc=0 (末行 ALL TESTS PASS)
python3 HW/check_onepass_s10_swap_set_truth.py         # ★ISS-373 那条闸必须仍然 rc=0 (零漂移自证)★
python3 HW/check_fp_libid_truth.py                      # ★ISS-369 那条闸必须仍然 rc=0 (零漂移自证)★
python3 state/merge.py                                 # rc=0
python3 state/gate_check.py                            # rc=0 (★Q1 必须 18/18★)
python3 state/check_brief_commands.py                  # rc=0
grep -c check_jdebug_land_fit state/gate_check.py      # ⇒ 0 (零挂链自证)
md5sum HW/PCB/demo_mainboard.kicad_pcb                 # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb        # 必须 2026-11-06 07:07:17.362193413 4940213
```
★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ★
★**收工后回卷 (★按老规矩★)**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」★)★ ★

---

## ★★五 你必须自己复算、**不许抄**的数 (★我已算过一遍, 但你要自己重跑并贴你的输出★) ★★

1. ★**现位 `J_DEBUG` 的四个 pad 坐标 + 铜箔 X 宽** (★期望: pad X `142.2000 / 142.7000 / 143.2000 / 143.7000` · Y 都 `56.6000` · 铜箔 X `142.0625..143.8375` 宽 `1.7750`★)
2. ★**官方 land 三个朝向下的四个 pad 绝对坐标** (★用 `FOOTPRINT.SetOrientationDegrees` 在真 board 上算·**不许手算旋转矩阵**★)
3. ★**现位 rot 90 装上去之后, 四个 THT 孔与 `JTAG_TDO`@`(143.7000, 57.9500)` / `XTAL_OUT`@`(146.9500, 57.9500)` 的孔净距** (★期望能重现 `0.1271` 与 `0.0000`·★对不上就停下查你的脚本★)
4. ★**落位可行域** (★自己定网格·自己算·自己贴输出★)
5. ★**最优落点 + 余量 + 代价清单** (★逐件带坐标★)

★**★主命令 (★本机实测存在, 你自己再验一遍★) ★★**:

```bash
# 现位 J_DEBUG 逐 pad + 铜箔 (★本机 KiCad 10.0.8★)
bash state/pcbnew_py.sh -c "
import pcbnew
b = pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb')
f=[x for x in b.GetFootprints() if x.GetReference()=='J_DEBUG'][0]
print('origin', pcbnew.ToMM(f.GetPosition().x), pcbnew.ToMM(f.GetPosition().y), 'rot', float(f.GetOrientation()))
for p in sorted(f.Pads(), key=lambda p: pcbnew.ToMM(p.GetPosition().x)):
    print('  pad',p.GetPadName(),'X=%.4f'%pcbnew.ToMM(p.GetPosition().x),'Y=%.4f'%pcbnew.ToMM(p.GetPosition().y),'shape',p.GetShape(),'net',p.GetNetname())
"

# 附近所有过孔 (★用于算孔净距★)
bash state/pcbnew_py.sh -c "
import pcbnew
b = pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb')
for t in b.GetTracks():
    if t.GetClass()=='PCB_VIA':
        p=t.GetPosition(); x,y=pcbnew.ToMM(p.x),pcbnew.ToMM(p.y)
        if 138<x<150 and 52<y<62: print('via %.4f %.4f net %s'%(x,y,t.GetNetname()))
"

# 官方 land 实读 (★读盘上 .kicad_mod, 不抄文档★)
grep -nE '\(pad "|thru_hole|drill|fp_rect|\(at ' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod | head -40

# 板 DRC 孔约束 (★真值从 .kicad_pro 读★)
python3 -c "import json;r=json.load(open('HW/PCB/demo_mainboard.kicad_pro'))['board']['design_settings']['rules'];print({k:r[k] for k in ('min_hole_to_hole','min_hole_clearance','min_through_hole_diameter','min_via_diameter','min_track_width')})"

# ISS-373 的沙盒工具 (★可直接复用·读它的做法别改它的文件★)
ls -la tmp/iss373_sbx/tools/
```

★**★最后一句纪律 (★main 2026-11-24 01:0x 追加★)★★**: ★**本单的价值不在于「给一个落点」, 而在于【给出【可行区】+【挪完还剩什么】这两样机器算出来的东西】⇒ ★★所以: 第一个工具调用就应该是【写落位扫描脚本】, 不是读文档★★ ⇒ ★**且【重活】(扫描) 与【交付物】(页/闸/交卷页) 不许同趟**: ★★先把扫描结果落盘到 `logs/iss376/` ⇒ 再写页 ⇒ 再写闸 ⇒ 最后交卷页 + 分片 ⇒ ★★每一步都先落盘, 别攒到最后一次写 (★你这一趟有一条约 16 分钟的硬墙★) ★★**★** ★**并且: 你算出来的数如果和我上面给的不一样, 【以你本机复算的为准】, 但你必须在交卷页里写清差在哪、为什么差** ★
