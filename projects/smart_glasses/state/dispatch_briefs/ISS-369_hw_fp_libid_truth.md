★**任务书全文**: `state/dispatch_briefs/ISS-369_hw_fp_libid_truth.md` ★
★**题**: ★**把「板面 186 个封装的库名 0/186 全空」这条【S10 那一跳的报废风险】做成【写盘作业包 + 沙盒可达性证明 + 一条几何闸】** ★★
★**类别**: ★**纯作业包 + 沙盒 + 新建闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板** ★★
★**★派活依据 (★main 2026-11-23 17:5x 本机实读·不抄任何 agent 报告★)**:
★**① ISS-361 (hw-lead) 实测**: ★**板面 186 个封装 · 库名 (`GetFPIDAsString()`) 唯一值 = `''` ⇒ 板是【自绘通用占位】, 不是「库名写错」** ★
★**② ISS-363 (sw-lead) 交卷**: ★**「板面 186 个封装库封装名 0/186 非空 ⇒ S10 那一跳必须先把『板面补库封装名』排进板那一趟」** ★ ⇒ ★**这条现在是【无人认领】的⇒ 最贵的一条** ★
★**③ ISS-364 (hw-lead) 交卷**: ★**90 件换封装作业包 (每件 12 字段: 目标 `lib:name` + `.kicad_mod` 实存路径 + md5 + 目标几何 + 几何 Δ + 要重接的 net) 已在 `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` §1** ★
★**④ main 独立复核 (★用真闸代码重算★)**: ★**真网表 C4 = 158 ⇒ 腿 B(网表节点具名)后 C4 = 68 ⇒ 四桶 TP42 / DNP26 / 靶内77 / 缺口13 = 158 ⇒ 腿 B 后靶内与缺口双双归零** ★
★**⇒ 结论 (★main 综合★)**: ★**「C4 = 68」只由【腿 B】达成; 【腿 A】(换官方 land) 对 C4 贡献实测为 0 ⇒ 而腿 A 才是换封装的本体 ⇒ ⇒ 「换封装」这一跳与「库封装名」这一跳【是同一件事的两半】, 缺任一半那一趟都交不出可投产的板** ★★
★**★为什么必须现在做 (★main 17:5x 本机实读★)**: ★**「板只改一次」那一趟开工当天, 若 186 个封装仍全是空库名的自绘占位 ⇒
① 换官方 land 时【写不进 `lib_id`】⇒ 装配厂/贴片厂拿不到正确封装 ⇒ 板做出来是错的 ② 换了 land 却没写库名 ⇒ **BOM 与板面对不上** ⇒ C1/C3 在那一趟会红
③ 板 md5 第二次变 ⇒ 整趟白跑** ★ ⇒ ★**所以这是【板那一趟之前必须收口的前置件】★★

★**本单交付物 (★3 件·不许扩项★)**:
★**① 一页** ★**新建** `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` ★★
  · §0 口径与读数 (★每个数字写清「哪个脚本产出·怎么复跑」★)
  · §1 板面现状: ★**186 个封装 · 库名全空 (★`GetFPIDAsString()` 唯一值 = `''`·实读★) · 每个封装当前是「自绘占位」还是「已落 land」·分类计数** ★
  · §2 ★**写盘机制 (★本机 KiCad 实测·不许抄文档★)**: ★**板文件里封装库名存在哪个字段 · 两种写法 (`lib_id` 字符串 vs `(lib "名称" "昵称")`) 在本机 KiCad 10.0.8 的行为 · 换 land 时【库名与 land 一起替换】的写法 · 换完板文件里哪些字段会变 (fp_line/fp_text/pad ...)·给出可复跑的最小样例** ★
  · §3 ★**目标清单**: ★**90 件 (★ISS-364 §1 那 12 字段·★你要自己复核·不许照抄★) + 其余 96 件 (TP 42 / DNP 26 / 靶内 22 / 缺口 1·腿 B 后的残差·★按同一口径逐件给目标 `lib:name` 或写明「不需要写」并给理由★)** ★
  · §4 ★**「写库名会不会改语义」的判定**: ★**对 C1/C2/C3/C4 各有什么影响 (★尤其: 库名不参与网表推导 ⇒ C4 不该变★)·用沙盒实测给出** ★
  · §5 未决项 (★只登记·不代拍★): ★**`D_ESD_USB_D` 2 脚 vs 3 脚 (W-1/W-2) · 5 只按键 3N vs 1.5N · `C_VBUS_GND` 留位还是下板** ★
★**② 沙盒可达性证明 + 一条机器闸** ★
  · ★**沙盒**: ★**在 `tmp/` 的板副本上做「90 件换官方 land + 同时写 `lib_id`」⇒ 用真闸 `state/check_pcb_nets.py` 跑 C1/C2/C3/C4 ⇒ 证明【C4 不变 (158 → 158)·C1/C2/C3 不因写库名而变红】★ ⇒ **这是「写库名不改变电气语义」的可复跑证明** ★
  · ★**新建** `HW/check_fp_libid_truth.py` (★判据: ★**① 板面每个【要写库名的】封装 `lib_id` 非空 ② 指向本机 KiCad 库根下真实存在的 `.kicad_mod` ③ 该 `.kicad_mod` 的 pad 数 == 板上该封装的 pad 数 ④ 几何 Δ 在容差内 (★容差值写在脚本里·不许拍脑袋★) ⑤ 内容级判定·**不挂 md5** ⑥ 证据等级五级白名单 ⑦ 正文零挂起措辞 ⑧ 沙盒在项目盘 `tmp/`★) ★
    · ★**`--selftest` 反向用例 ≥ 6 条·每条自证「红的是目标那一条, 其余仍绿」** ★
★**③ 交卷页 + 分片 + 留证** ★
  · ★**交卷页** ★**新建** `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md` (★B1~B6 六段齐全 + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★)
  · ★**分片** `state/fragments/hw.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ 写前后各记一次 md5 基线 · ★期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖★
  · ★**留证** `logs/iss369/` (★基线 md5 / 实算脚本 / 沙盒 C1~C4 读数 / selftest 全量输出 / 闸复跑输出★)

★**边界 (★逐条·不许越★)**:
★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413` · 开工前 + 交卷后各打一次双证★ ⇒ **换 land 只许在 `tmp/` 的副本上做** ★
★**零落表** (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · `state/issue_log.yaml` 一字不改★) ★
★**零改既有闸**: ★**`HW/check_fp_truth_baseline.py` · `HW/check_fp_truth_coverage_gap.py` · `HW/check_fp_truth_land_swap.py` ·
`HW/check_onepass_preflight_coverage.py` · `HW/check_onepass_s10_manifest.py` · `state/check_pcb_nets.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一字不改** ★
★**零改既有页面**: ★**`HW/FP_TRUTH_BASELINE.md` · `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` · `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` ·
`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `state/board_trip_baseline_20260723.txt` 老字一字不许删/不许改** ★
★**零挂链** (★本单的新闸也不挂★) ★
★**零外发 / 零采购 / 零联系供应商** ★ **不替老板拍板** (★只登记+给代价+给会红哪道闸★) ★ **不写别人的分片** (★只写 `state/fragments/hw.yaml`★) ★ **不改 `PROJECT_TRACKER.md` §0** ★
★**证据分级必标** (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ★
★**单条 `exec` ≤ ~120 秒 · 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** ★

★**必跑命令 (★全部真实存在·main 2026-11-23 17:5x 本机实测过★)**:
```
bash state/pcbnew_py.sh state/check_pcb_nets.py           # ★C1~C4 真闸·要 KiCad python★
python3 HW/check_fp_truth_baseline.py                     # ★既有闸·读完须仍 rc=0★
python3 HW/check_fp_truth_coverage_gap.py                 # ★既有闸·读完须仍 rc=0★
python3 HW/check_fp_truth_land_swap.py                    # ★ISS-364 的闸·只读用★
python3 HW/check_onepass_preflight_coverage.py            # ★既有闸·读完须仍 rc=0★
python3 HW/check_fp_libid_truth.py                       # ★本单新建★
python3 HW/check_fp_libid_truth.py --selftest
python3 state/merge.py
python3 state/gate_check.py
python3 state/frag_write.py --agent hw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```
★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**:
① 页存在且非空 ② 板面 186 个封装逐个实测 (库名 / pad 数 / 是否自绘占位) ③ 写盘机制写明【本机 KiCad 实测】(★不是文档转述★) ④ 目标清单 90 + 96 逐件给目标 `lib:name` 或「不需要写 + 理由」 ⑤ 每个 `.kicad_mod` 实测在盘 + md5 对得上 ⑥ 沙盒: 换 land + 写库名后 **C4 仍是 158** (★不变★) ⑦ 沙盒: C1/C2/C3 不因写库名而变红 ⑧ 新闸 rc=0 ⑨ `--selftest` ≥6/6 且每条自证「只红目标那条」 ⑩ 沙盒在项目盘 `tmp/` ⑪ 板 md5/mtime 逐字节未变 ⑫ 网表/脚表/BOM md5 逐字节未变 ⑬ 既有闸脚本一个字节未改 ⑭ 既有页面老字逐字节未变 ⑮ `merge.py` rc=0 且 `gate_check.py` rc=0 (★Q1 = 18/18★) ⑯ 证据等级全在五级白名单 ⑰ 正文零挂起措辞 ⑱ 分片写入只走 `state/frag_write.py` ⑲ 交卷页 B1~B6 齐全 + `logs/iss369/` 留证在盘 (≥ 10 件) ⑳ 回滚说明在盘 (★沙盒怎么复原·真件零改动如何自证★)
★**收工后按老规矩回卷**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★ ★
