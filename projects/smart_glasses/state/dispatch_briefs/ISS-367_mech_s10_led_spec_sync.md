★**任务书全文**: `state/dispatch_briefs/ISS-367_mech_s10_led_spec_sync.md` ★
★**题**: ★**把「换官方 0805」这一跳在【结构侧】留下的两处未收口项做成【同趟重算 + 定点改写 + 一条机器闸】** ★★
★**类别**: ★**纯文档定点改写 + 新建闸 + 沙盒重算 · 零写板 · 零落表 · 零改既有闸 · 零外发 · 不代老板拍板** ★★
★**派活依据 (★main 2026-11-23 17:5x 本机实读·不抄任何 agent 报告★)**: ★**ISS-365 (mech-lead, 17:1x 交卷)** 主笔自查出
★**「`D_LED_G` 换官方 0805 后 `led_space` 铜箔相对原点偏移变 ⇒ 两条可放行带 + 可落位块数全变 (1992→2183, 带 A 宽 −0.875),
且 sweep 不再单调 (clr=0.5 的 2197 < clr=0.2 的 2253) ⇒ 既有页 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2 那句
「块数不变」的后半句【作废】, 必须同趟重算** ★ ⇒ ★**ISS-365 交卷页明确写了「E-9 剩下两处仍归 main 派活, 本单不代拍」** ★
⇒ ★**那两处 = ① `MECH/BOARD_ONEPASS_MECH_SYNC.md` 的机器块 ② `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格** ★
★**main 已独立复核过的数 (★只认这三个, 其余自己重算★)**: ★**可落位块数 1992 → 2183 (+191)** · ★**两条整高自由带 X 1.550..3.450 / 72.540..73.660
→ 2.225..3.250 / 73.215..74.385 (带 A 宽 −0.875)** · ★**clr sweep 1992/2016/2031/2075 → 2183/2241/2253/2197 ⇒ 非单调** ★
★**为什么必须现在做**: ★**「板只改一次」那一趟开工当天, 这两处如果不先改口径 ⇒ 那一趟按旧数布局 ⇒ LED 落位超框 / 结构件装不下
⇒ 板 md5 第二次变 ⇒ 整趟白跑** ★ ⇒ ★**所以这是【板那一趟之前必须收口的前置件】★★

★**本单交付物 (★3 件·不许扩项★)**:
★**① 一页** ★**新建** `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` ★★
  · §0 口径与读数 (★每个数字写清「哪个脚本产出·怎么复跑」★)
  · §1 漂移本体: 现占位 land vs 目标 0805 的几何对照 (★读 `.kicad_mod` 实测, 不抄台账★) + 两条可放行带 + 块数 + sweep (含非单调证据)
  · §2 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块: ★**该改哪一行·改成什么·逐字给出 (★追加式或定点替换·★不许重排整页★)★**
  · §3 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格: ★**改前值 / 改后值 / 依据 / 会连带影响哪几项 (★只给建议, 不代拍★)★**
  · §4 同趟重算清单: ★**那一趟开工当天 MECH 侧必须重新跑的几项 + 各自命令 + 期望读数区间★**
  · §5 未决项 (★只登记·不代拍★): `D_LED_G` 结构光孔有/无 (★老板项 U-365-3★) / 按键 3N vs 1.5N (★老板项★)
★**② 一条机器闸** ★**新建** `MECH/check_onepass_s10_led_spec_sync.py` ★★
  · 判据 (★内容级·**不挂 md5**·★文档改一个字就重判★★):
    - **L0** 基准块存在且合法
    - **L1** ★**页里写的【可落位块数 / 两条可放行带 / sweep】四组数 == 脚本自己实算的数** ★ (★实算源 = 本机 KiCad 库里的 0805 `.kicad_mod` + 板面现占位 land★)
    - **L2** ★**sweep 非单调 (clr=0.5 的值 < clr=0.2 的值) 必须被显式承认** ★ (★若页里写「单调」⇒ 红★)
    - **L3** `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块里那块数 == §1 的数 (★两处不许打架★)
    - **L4** ★**证据等级五级白名单** ( `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ 写 `[官方]` = 红 )
    - **L5** 正文零挂起措辞 (★禁「等原厂回信 / 等供应商确认 / 待外部回复」★ ⇒ 老板 2026-11-12 02:02 政策★)
    - **L6** 沙盒在项目盘 `tmp/` (★不写 /tmp★)
  · ★**`--selftest` 反向用例 ≥ 6 条·每条自证「红的是目标那一条, 其余仍绿」★** (①改块数 ②把「单调」写回页里 ③改 MECH_SYNC 机器块的数 ④清空证据等级 ⑤塞挂起措辞 ⑥把沙盒路径指到 /tmp)
★**③ 交卷页 + 分片 + 留证** ★
  · ★**交卷页** ★**新建** `HANDOFF/2026-11-23_mech-lead_ISS367_S10换封装LED窗口规格同趟重算.md` (★B1~B6 六段齐全 + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★)
  · ★**分片** `state/fragments/mech.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ 写前后各记一次 md5 基线 · ★期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖★
  · ★**留证** `logs/iss367/` (★基线 md5 / 实算脚本 / selftest 全量输出 / 闸复跑输出★)

★**★定点改写授权 (★main 授权·★只有这两处·★其余老字一字不许动★)**:
★**允许改**: ★**① `MECH/BOARD_ONEPASS_MECH_SYNC.md` 里与 `D_LED_G` / `led_space` / 可放行带 / 块数 有关的【那几行 + 机器块对应字段】** ★
　　　　　 ★**② `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 里【LED 窗口规格那几行】** ★
★**不许改**: ★**上面两页的其余任何一行** ★ ⇒ ★**改前 md5 逐字节留证 + 改后逐行 diff + 一键回滚说明 (★原文与新文都留在 `logs/iss367/`★)★ ★
★**不许改**: ★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (★ISS-365 那一轮已改过 §3.2 · 本单不许再动★)★** ★
★**不许改**: ★**`MECH/check_onepass_s10_fp_swap_impact.py` (★ISS-365 的闸·本单只用它·不改它★)· `MECH/check_onepass_struct_crosscheck.py` · `MECH/check_onepass_mech_sync.py` ·
`MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` ★**
★**边界**: ★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413` · 开工前 + 交卷后各打一次双证★) ★
★**零落表** (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · `state/issue_log.yaml` 一字不改★) ★
★**零外发 / 零采购 / 零联系供应商** (★不发邮件·不询价·不下采购单★) ★
★**不替老板拍板** (★`D_LED_G` 光孔有/无 = 老板项 · 只登记两路的结构代价与要红的闸★) ★
★**不写别人的分片** (★只写 `state/fragments/mech.yaml`★) ★ **不改 `PROJECT_TRACKER.md` §0 锁死表** ★
★**证据分级必标** (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ★
★**单条 `exec` ≤ ~120 秒 · 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** ★

★**必跑命令 (★全部真实存在·main 2026-11-23 17:5x 本机实测过★)**:
```
python3 MECH/check_onepass_s10_fp_swap_impact.py          # ★ISS-365 的闸·只读用·不改它★
python3 MECH/check_onepass_mech_sync.py                   # ★既有闸·读完须仍 rc=0★
python3 MECH/check_onepass_struct_crosscheck.py           # ★既有闸·读完须仍 rc=0★
python3 MECH/check_board_frame_coords.py                  # ★既有闸·读完须仍 rc=0★
python3 MECH/check_demo_struct_truth.py                   # ★既有闸·读完须仍 rc=0★
python3 MECH/check_onepass_s10_led_spec_sync.py           # ★本单新建★
python3 MECH/check_onepass_s10_led_spec_sync.py --selftest
python3 state/merge.py
python3 state/gate_check.py
python3 state/frag_write.py --agent mech-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```
★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**:
① 页存在且非空 ② 四个数 (块数 / 两条带 / sweep) 与脚本实算一致 ③ sweep 非单调被显式承认 ④ MECH_SYNC 机器块与页一致 ⑤ 证据等级全在五级白名单 ⑥ 正文零挂起措辞 ⑦ 新闸 rc=0 ⑧ `--selftest` ≥6/6 且每条自证「只红目标那条」 ⑨ 沙盒在项目盘 `tmp/` ⑩ 两处定点改写之外老字逐字节未变 (★diff 留证★) ⑪ `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 逐字节未变 ⑫ 既有闸脚本一个字节未改 ⑬ 板 md5/mtime 逐字节未变 ⑭ 网表/脚表/BOM md5 逐字节未变 ⑮ `merge.py` rc=0 且 `gate_check.py` rc=0 (★Q1 = 18/18★) ⑯ 既有 4 道 MECH 闸读完仍全 rc=0 ⑰ 分片写入只走 `state/frag_write.py` ⑱ 交卷页 B1~B6 齐全 ⑲ `logs/iss367/` 留证在盘 (≥ 10 件) ⑳ 一键回滚说明在盘 (★改前/改后原文 + 回滚命令★)
★**收工后按老规矩回卷**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★ ★
