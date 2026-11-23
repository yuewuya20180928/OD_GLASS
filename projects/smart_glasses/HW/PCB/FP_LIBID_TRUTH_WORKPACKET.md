# HW/PCB · ISS-369 · 「板那一趟」板面 186 封装库名写盘作业包

> ★**单号**: ISS-369 · ★**owner**: hw-lead (硬件总工) · ★**性质**: 纯作业包 + 沙盒 + 新建闸 · ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板**★
> ★**本单只做 3 件**: ① 本页 (`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md`) · ② 一条机器闸 `HW/check_fp_libid_truth.py` (L0~L8 + `--selftest`) · ③ 交卷页 + 分片 + 留证
> ★**本单要解决的问题**: ★**板面 186 个封装的库封装名 0/186 非空 ⇒ S10「换封装真值」那一跳的真值源【不存在】⇒ 这一跳必须排在「板那一趟」里先收口**★
> ★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md` · ★**留证**: `logs/iss369/` · ★**沙盒**: `tmp/iss369/`
> ★**本页所有数字由生成器 `logs/iss369/build_fp_libid_workpacket.py` 从真源实算生成** ⇒ 零转述误差; 每个数字的复跑命令见 §0 的「怎么复跑」栏。
> ★**上一趟 (2026-11-23 20:10 派) 的子会话在 20:52:45 被 abort, 死在【对 4.9 MB 板文件做整体 diff】那一刻** ⇒ ★**本趟从已落盘的读数续做, 不重跑那几项重读** ⇒ 详见交卷页 §B5。

<!-- BEGIN ISS369 库封装名写盘基准块 -->
```json
{
 "issue": "ISS-369",
 "owner": "hw-lead",
 "doc": "HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md",
 "gate": "HW/check_fp_libid_truth.py",
 "note": "★本块由 logs/iss369/build_fp_libid_workpacket.py 从真源实算生成; 闸 L0 校验它是合法 JSON, L1 校验 counts 与脚本实算逐项相等, L2 校验 §3.1 (90 件) / §3.2 (96 件) 两张表的件数与本块逐件相等, L4 逐个 test -f 验 .kicad_mod 在盘 + md5, L5 校验几何与容差",
 "counts": {
  "board_footprints": 186,
  "libid_empty": 186,
  "libid_named": 0,
  "board_pads_total": 834,
  "lib_dirs": 155,
  "lib_mods": 15468,
  "target_total": 90,
  "inter_total": 77,
  "gap_total": 13,
  "rest_total": 96,
  "write_total": 94,
  "write_90": 90,
  "write_96": 4,
  "nowrite_total": 92,
  "c4_total": 158,
  "four_buckets": {
   "TP": 42,
   "DNP": 26,
   "靶内": 77,
   "缺口": 13
  },
  "rest96_buckets": {
   "TP": 42,
   "DNP": 37,
   "靶内-非C4": 1,
   "缺口-非C4": 12,
   "其它": 4
  },
  "r96_in_c4": 68,
  "r96_not_in_c4": 28,
  "sandbox_rounds": 5,
  "sandbox_c4_all": 158,
  "padeq_equivalent": 4,
  "kicad_version": "10.0.8",
  "pad_count_changes": 7
 },
 "write_targets": {
  "C_AC_CSI_D0_CK_N": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_CK_P": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D0_N": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D0_P": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D1_N": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D1_P": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D2_N": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D2_P": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D3_N": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_AC_CSI_D0_D3_P": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_BULK_LIGHT_3V3": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_BULK_VDD_1V8_IO": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_BULK_VDD_3V3_IO": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_DET_BAT": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_DET_VBUS_D": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_HF_LIGHT_3V3": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_HF_VDD_1V8_IO": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_HF_VDD_3V3_IO": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_KEY_PWR": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_KEY_VM": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_KEY_VP": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_RST": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_SW_IN": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_SW_OUT": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_TEMP": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "C_VBUS_DEMO": {
   "libname": "Capacitor_SMD:C_0603_1608Metric",
   "path": "Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod",
   "md5": "0641b49cd03997f007054fc64a50c3e3",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.55,
   "bucket": "靶内"
  },
  "D_LED_G": {
   "libname": "LED_SMD:LED_0805_2012Metric",
   "path": "LED_SMD.pretty/LED_0805_2012Metric.kicad_mod",
   "md5": "7616eddd0b9951dec0bf5bdfc3df0a77",
   "pads_n": 2,
   "fab_w": 2.0,
   "fab_h": 1.2,
   "center": 1.875,
   "bucket": "靶内"
  },
  "D_LED_R": {
   "libname": "LED_SMD:LED_0603_1608Metric",
   "path": "LED_SMD.pretty/LED_0603_1608Metric.kicad_mod",
   "md5": "ac369a6895f54b78d16871a76dc9d08e",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.8,
   "center": 1.575,
   "bucket": "靶内"
  },
  "R_BAT_DET_1": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_BAT_DET_2": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_CC1_D": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_CC2_D": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_EN_VCORE": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_JTAG_TCK": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_JTAG_TDI": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_JTAG_TDO": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_JTAG_TMS": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_KEY_CAM": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_KEY_PWR": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_KEY_VM": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_KEY_VP": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_LED_G": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_LED_R": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PD_ON": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PG_PULL": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_BOOT_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_I2CA_SCL": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_I2CA_SDA": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_I2CB_SCL": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_I2CB_SDA": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_ID0": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_ID1": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_PG": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_PU_RESET_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_CK_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_CK_P": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D0_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D0_P": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D1_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D1_P": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D2_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D2_P": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D3_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SEL_D3_P": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_CSI_MCLK": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_FSIN": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_RESET_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_SPI_CSn": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_SPI_MISO": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_SPI_MOSI": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_SPI_SCLK": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_USB_D_N": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SER_USB_D_P": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SUPV_DIV1": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_SUPV_DIV2": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_VBUS_DET_D1": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "R_VBUS_DET_D2": {
   "libname": "Resistor_SMD:R_0603_1608Metric",
   "path": "Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod",
   "md5": "fa9f0fce044a12e2a675c087b781ae3d",
   "pads_n": 2,
   "fab_w": 1.6,
   "fab_h": 0.825,
   "center": 1.65,
   "bucket": "靶内"
  },
  "CHG_GND_STAR": {
   "libname": "TestPoint:TestPoint_Pad_D1.0mm",
   "path": "TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod",
   "md5": "cea8eb3ba9b799767624661848b00243",
   "pads_n": 1,
   "fab_w": 0.0,
   "fab_h": 0.0,
   "center": 0.0,
   "bucket": "缺口"
  },
  "D_ESD_CAM": {
   "libname": "Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm",
   "path": "Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod",
   "md5": "0edfa97bd7bd277f3c05acf2bee23892",
   "pads_n": 2,
   "fab_w": 1.0,
   "fab_h": 0.6,
   "center": 0.7,
   "bucket": "缺口"
  },
  "D_ESD_DEMO": {
   "libname": "Diode_SMD:D_SOD-323",
   "path": "Diode_SMD.pretty/D_SOD-323.kicad_mod",
   "md5": "bce0278c9b9af83e2de3cd130e6c04ed",
   "pads_n": 2,
   "fab_w": 1.8,
   "fab_h": 1.4,
   "center": 2.1,
   "bucket": "缺口"
  },
  "D_ESD_USB_D": {
   "libname": "Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm",
   "path": "Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod",
   "md5": "0edfa97bd7bd277f3c05acf2bee23892",
   "pads_n": 2,
   "fab_w": 1.0,
   "fab_h": 0.6,
   "center": 0.7,
   "bucket": "缺口"
  },
  "FB_DEMO": {
   "libname": "Inductor_SMD:L_0805_2012Metric",
   "path": "Inductor_SMD.pretty/L_0805_2012Metric.kicad_mod",
   "md5": "4e67ede5911eab38accb2ef9e57de79c",
   "pads_n": 2,
   "fab_w": 2.0,
   "fab_h": 0.9,
   "center": 2.125,
   "bucket": "缺口"
  },
  "Q_AND": {
   "libname": "Package_TO_SOT_SMD:SOT-23",
   "path": "Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod",
   "md5": "f8754f4dc2887bbe66484114fa63ee44",
   "pads_n": 3,
   "fab_w": 0.0,
   "fab_h": 0.0,
   "center": 2.102,
   "bucket": "缺口"
  },
  "Q_ENVC": {
   "libname": "Package_TO_SOT_SMD:SOT-23",
   "path": "Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod",
   "md5": "f8754f4dc2887bbe66484114fa63ee44",
   "pads_n": 3,
   "fab_w": 0.0,
   "fab_h": 0.0,
   "center": 2.102,
   "bucket": "缺口"
  },
  "Q_PG": {
   "libname": "Package_TO_SOT_SMD:SOT-23",
   "path": "Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod",
   "md5": "f8754f4dc2887bbe66484114fa63ee44",
   "pads_n": 3,
   "fab_w": 0.0,
   "fab_h": 0.0,
   "center": 2.102,
   "bucket": "缺口"
  },
  "SW_BOOT": {
   "libname": "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2",
   "path": "Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod",
   "md5": "460d6f7d3529096429408f78ed206fe7",
   "pads_n": 4,
   "fab_w": 4.2,
   "fab_h": 2.8,
   "center": 4.401,
   "bucket": "缺口"
  },
  "SW_KEY_PWR": {
   "libname": "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2",
   "path": "Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod",
   "md5": "460d6f7d3529096429408f78ed206fe7",
   "pads_n": 4,
   "fab_w": 4.2,
   "fab_h": 2.8,
   "center": 4.401,
   "bucket": "缺口"
  },
  "SW_KEY_VM": {
   "libname": "Button_Switch_SMD:SW_SPST_B3U-1000P",
   "path": "Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod",
   "md5": "749f20c5ab898069ade01682274c7bbf",
   "pads_n": 2,
   "fab_w": 3.0,
   "fab_h": 2.5,
   "center": 3.4,
   "bucket": "缺口"
  },
  "SW_KEY_VP": {
   "libname": "Button_Switch_SMD:SW_SPST_B3U-1000P",
   "path": "Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod",
   "md5": "749f20c5ab898069ade01682274c7bbf",
   "pads_n": 2,
   "fab_w": 3.0,
   "fab_h": 2.5,
   "center": 3.4,
   "bucket": "缺口"
  },
  "SW_RST": {
   "libname": "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2",
   "path": "Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod",
   "md5": "460d6f7d3529096429408f78ed206fe7",
   "pads_n": 4,
   "fab_w": 4.2,
   "fab_h": 2.8,
   "center": 4.401,
   "bucket": "缺口"
  },
  "J_SOM_P1": {
   "libname": "Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm",
   "path": "Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod",
   "md5": "6afd4648ced47278611e6ab4859510e9",
   "pads_n": 100,
   "fab_w": 22.6,
   "fab_h": 2.88,
   "center": 19.841,
   "bucket": "其它"
  },
  "J_SOM_P2": {
   "libname": "Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm",
   "path": "Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod",
   "md5": "6afd4648ced47278611e6ab4859510e9",
   "pads_n": 100,
   "fab_w": 22.6,
   "fab_h": 2.88,
   "center": 19.841,
   "bucket": "缺口-非C4"
  },
  "J_SOM_P3": {
   "libname": "Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm",
   "path": "Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod",
   "md5": "6afd4648ced47278611e6ab4859510e9",
   "pads_n": 100,
   "fab_w": 22.6,
   "fab_h": 2.88,
   "center": 19.841,
   "bucket": "其它"
  },
  "J_SOM_P4": {
   "libname": "Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm",
   "path": "Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod",
   "md5": "6afd4648ced47278611e6ab4859510e9",
   "pads_n": 100,
   "fab_w": 22.6,
   "fab_h": 2.88,
   "center": 19.841,
   "bucket": "缺口-非C4"
  }
 },
 "nowrite_refs": {
  "BT_432243": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "CONN_CAM": {
   "bucket": "其它",
   "code": "RWA"
  },
  "CONN_LIGHT": {
   "bucket": "缺口-非C4",
   "code": "RL"
  },
  "C_BULK_LIGHT_1V8": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_BULK_SENSOR_AVDD": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_BULK_SENSOR_CORE": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_BULK_SENSOR_VDD_IO": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_BULK_V_CORE": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_BULK_V_SOC_IO": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_HF_LIGHT_1V8": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_HF_SENSOR_AVDD": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_HF_SENSOR_CORE": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_HF_SENSOR_VDD_IO": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_HF_V_CORE": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_HF_V_SOC_IO": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_KEY_CAM": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_SUPV": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_VBUS_GND": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_XTAL_IN": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "C_XTAL_OUT": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "D_ESD_LIGHT": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "D_LED_B": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "J_BOOT1": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "J_CHG": {
   "bucket": "其它",
   "code": "RWA"
  },
  "J_DEBUG": {
   "bucket": "靶内-非C4",
   "code": "RWA"
  },
  "J_UART": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "J_USB_C": {
   "bucket": "缺口-非C4",
   "code": "RL"
  },
  "Q1": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "Q2": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "R_ID_JMP0": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "R_ID_JMP1": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "R_LED_B": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "R_NTC_BAT": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "R_TS_PULL": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "SW_KEY_CAM": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "TP_BAT": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_BAT_CHG": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_BOOT": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_CSI_CK_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_CSI_CK_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_CSI_D0_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_CSI_D0_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_CK_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_CK_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D0_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D0_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D1_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D1_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D2_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D2_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D3_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_DSI_D3_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_FSIN": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_I2CA_SCL": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_I2CA_SDA": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_I2CB_SCL": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_I2CB_SDA": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_ID": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_JTAG": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_KEY_PWR": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_KEY_VM": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_KEY_VP": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_LED_B": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_LED_G": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_LED_R": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_LIGHT_3V3": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_MCLK": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_PG": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_PG_VCORE": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_PG_VIO": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_RESET": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_SYS": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_UART": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_USB_D_N": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_USB_D_P": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_VCORE": {
   "bucket": "TP",
   "code": "RTP"
  },
  "TP_VIO": {
   "bucket": "TP",
   "code": "RTP"
  },
  "U_BATPROT": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "U_DCDC_VCORE": {
   "bucket": "缺口-非C4",
   "code": "RWA"
  },
  "U_DCDC_VIO": {
   "bucket": "缺口-非C4",
   "code": "RWA"
  },
  "U_EN_SW": {
   "bucket": "缺口-非C4",
   "code": "RWA"
  },
  "U_LDO_IO18": {
   "bucket": "缺口-非C4",
   "code": "RWA"
  },
  "U_LDO_IO33": {
   "bucket": "缺口-非C4",
   "code": "RWA"
  },
  "U_LDO_L18": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "U_LDO_L33": {
   "bucket": "缺口-非C4",
   "code": "RWA"
  },
  "U_LDO_S12": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "U_LDO_S18B": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "U_LDO_S28": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "U_PWR_SW": {
   "bucket": "缺口-非C4",
   "code": "RWA"
  },
  "U_SUPV": {
   "bucket": "DNP",
   "code": "RNP"
  },
  "U_TEMP": {
   "bucket": "缺口-非C4",
   "code": "RL"
  },
  "X1": {
   "bucket": "DNP",
   "code": "RNP"
  }
 }
}
```
<!-- END ISS369 库封装名写盘基准块 -->

## §0 口径与读数 (★本机实跑 · 每个数字都能被本表某一行的命令复现★)

| # | 项 | 实测 | 口径 (哪个脚本产出) | 怎么复跑 |
|---|---|---|---|---|
| 1 | ★**板面封装总数**★ | ★**186**★ | 纯文本读板 (`tmp/iss369/tools/parse_board.py`) + KiCad python 读板 (`tmp/iss369/tools/board_probe.py`) 两口径互校 | `python3 tmp/iss369/tools/parse_board.py` |
| 2 | ★**库封装名非空数**★ | ★**0 / 186**★ (★`GetFPIDAsString()` 唯一值 = `''`★) | KiCad 10.0.8 python API 逐个封装读 (`tmp/iss369/tools/board_probe.py`) | `bash state/pcbnew_py.sh tmp/iss369/tools/board_probe.py` |
| 3 | ★**板面连「厂商封装号」栏都没有**★ | ★**`(property "Footprint" …)` 命中 0 / 186**★ ⇒ 板面【连一个封装身份字段都没有】 | 同上 (纯文本正则) | `grep -c '(property "Footprint"' HW/PCB/demo_mainboard.kicad_pcb` |
| 4 | ★**板面 186 件的形态分类**★ | ★**自绘通用占位 183 / 已落 land 3**★ (★已落 land = `U_TEMP` · `CONN_LIGHT` · `J_USB_C`·按原厂图纸自绘, 有 courtyard★) | 判据: 焊盘尺寸单一 + 4 条 fp_line + 无 courtyard + 无丝印 ⇒ 自绘通用占位 | `python3 tmp/iss369/tools/classify.py` |
| 5 | ★**板面焊盘总数**★ | ★**834**★ | 括号配平切块数 (★含焊盘名为空的 NPTH 固定孔★) | `python3 tmp/iss369/tools/padeq_rot_np.py` |
| 6 | ★**本机 KiCad 官方库规模**★ | ★**155 个 `.pretty` 库目录 / 15,468 个 `.kicad_mod` 封装文件**★ | `ls -d $LIBROOT/*.pretty \| wc -l` + `find $LIBROOT -name '*.kicad_mod' \| wc -l` | 同左 |
| 7 | ★**库封装命名口径**★ | ★**metric 后缀命名**★: `R_0402_1005Metric` / `C_0603_1608Metric` / `LED_0805_2012Metric` / `L_0805_2012Metric` / `SW_SPST_B3S-1000`; ★**例外**: `D_SOD-323` / `D_SOD-123` 是裸名★ | 本机官方库实测 | `ls /home/yuewuya/kicad/AppDir/share/kicad/footprints/Resistor_SMD.pretty \| head` |
| 8 | ★**C4 占位脚号件数**★ | ★**158**★ | `state/check_pcb_nets.py` 的 C4 口径 (网表节点串是 bare ⇒ 焊盘号按行序占位) | `bash state/pcbnew_py.sh state/check_pcb_nets.py` |
| 9 | ★**C4 四桶 (ISS-361 同口径)**★ | ★**TP 42 / DNP 26 / 靶内 77 / 缺口 13 = 158**★ | 分桶优先级 TP ⇒ DNP ⇒ 其余归缺口 | `python3 tmp/iss369/tools/buckets.py` |
| 10 | ★**本单的对象 90 件**★ | ★**靶内 77 + 缺口 13 = 90**★ | 交集 + 缺口 并集 (与 ISS-361 / ISS-364 同口径) | 同上 |
| 11 | ★**其余 96 件**★ | ★**186 − 90 = 96**★ (★68 件在 C4 里 = TP 42 + DNP 26 · 28 件不在 C4★) | 同上 | 同上 |
| 12 | ★**本单要写库名的件数**★ | ★**94**★ (90 件换 land + 写库名 · 4 件 `J_SOM_P1~P4` 只写库名不动铜箔) | 本单实算 | `python3 logs/iss369/build_fp_libid_workpacket.py` |
| 13 | ★**本单不写库名的件数**★ | ★**92**★ (TP 42 / DNP 37 / 已落 land 3 / 选型未定 10) | 同上 | 同上 |
| 14 | ★**逐焊盘几何等价的官方件**★ | ★**全库 15,468 个 `.kicad_mod` 穷举 ⇒ 只有 4 / 186 件有几何等价件**★ (★`J_SOM_P1~P4`·各 2 个候选·旋转 180°·容差 0.05/0.05/0.10 mm★) ⇒ ★**其余 182 件【写官方库名 = 假身份】**★ | 逐焊盘 (含 NPTH) 几何等价穷举 | `python3 tmp/iss369/tools/padeq_rot_np.py` |
| 15 | ★**写盘机制**★ | ★**库封装名存在 `(footprint "…")` 那一行的字符串里; 本机 KiCad 10.0.8 只认 `"Lib:Name"` 字符串写法**★ | 本机实测 E1~E9 (见 §2) | `bash state/pcbnew_py.sh tmp/iss369/tools/mech_probe2.py` |
| 16 | ★**沙盒五轮读数**★ | ★**S0/S1/S2/S3/S4 的 C4 全部 = 158**★ ⇒ ★**写库名这一腿对 C4 的贡献 = 0**★ | 真闸 `state/check_pcb_nets.py` 的真代码 (只把 NET 常量指向副本) | `bash state/pcbnew_py.sh tmp/iss369/tools/sandbox_libid.py` |
| 17 | ★**写库名的字节级影响**★ | ★**只改 `(footprint "…")` 那一行, 其它一个字节都不动**★ (S0→S3 加 94 行 / 删 94 行, 差分行全部是封装节点名行) | 逐行差分 | `python3 tmp/iss369/tools/sandbox_diff.py` |
| 18 | ★**板指纹 (开工前 = 交卷后)**★ | ★**`611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B**★ | `md5sum` + `stat` | `md5sum HW/PCB/demo_mainboard.kicad_pcb` |

★**§0 的 18 行读数全部复现自同一批真源文件; 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 全程逐字节未变**★。

## §1 板面现状: 186 个封装 · 库名全空 (★实读★)

★**一句话**: ★**板面 186 个封装, 库封装名 0/186 非空; 连 `property "Footprint"` 这个厂商封装号栏也是 0/186**★ ⇒ ★**板是【自绘通用占位】, 不是「库名写错」**★ ⇒ ★**这一趟要做的是【把身份补上】, 不是【把写错的字改对】**★。

### §1.1 库名与非空率

| 项 | 实测 [实测] |
|---|---|
| 板面封装总数 | **186** |
| `GetFPIDAsString()` 非空 | **0** (★唯一值 = `''`★) |
| `GetFPID().GetUniStringLibId()` 非空 | **0** (★唯一值 = `''`★) |
| `GetFPID().GetLibItemName()` 非空 | **0** (★唯一值 = `''`★) |
| 文本层 `(footprint "…")` 首行 | ★**186 个全是 `(footprint ""` (空串)★** |
| `(property "Footprint" …)` | **0 / 186** (★板面连厂商封装号都没记★) |
| 板面焊盘总数 | **834** (★含焊盘名为空的 NPTH 固定孔★) |

### §1.2 形态分类 (★每个封装是「自绘占位」还是「已落 land」★)

| 分类 | 件数 | 判据 | 这 186 件的 ref |
|---|---|---|---|
| ★**自绘通用占位**★ | ★**183**★ | 焊盘尺寸单一 + 4 条 `fp_line` + 无 courtyard + 无丝印层 ⇒ 同一块「通用占位模板」复制出来的 | (除下列 3 件外的全部) |
| ★**已落 land (按原厂图纸自绘)**★ | ★**3**★ | 有 `F.CrtYd` courtyard + 焊盘尺寸多样 | `U_TEMP` (TI DRV0006B WSON-6) · `CONN_LIGHT` (Hirose FH12-22S) · `J_USB_C` (GCT USB4105-16P) |

★**为什么这件事必须现在做 (★不改板就白跑那一趟★)**:

1. ★**换官方 land 时写不进 `lib_id` ⇒ 装配厂/贴片厂拿不到正确封装 ⇒ 板做出来是错的**★ (★本单 §2 实测: 库名只认 `(footprint "Lib:Name")` 那一行, 换 land 与写库名是【同一个动作】的两半★)
2. ★**换了 land 却没写库名 ⇒ BOM 与板面对不上 ⇒ C1/C3 在那一趟会红**★
3. ★**板 md5 第二次变 ⇒ 整趟白跑**★ ⇒ ⇒ ★**写库名这一腿必须与换 land 【同一次】做完, 不能拖到下一趟**★

### §1.3 ★板面 186 个封装逐个实测 (★一 ref 一行·不重不漏★)

| ref | 库封装名 | 焊盘数 | 焊盘尺寸 (mm) | fab 外框 (mm) | 中心距 (mm) | 形态 | 本单动作 |
|---|---|---|---|---|---|---|---|
| `BT_432243` | ★**空**★ | 2 | 0.600x0.900 | 3.000×3.000 | 2.200 | 自绘通用占位 | **不写** |
| `CHG_GND_STAR` | ★**空**★ | 1 | 0.600x0.900 | 4.000×5.000 | 0.000 | 自绘通用占位 | **写** `TestPoint:TestPoint_Pad_D1.0mm` |
| `CONN_CAM` | ★**空**★ | 31 | 0.275x0.900 | 17.600×4.000 | 15.000 | 自绘通用占位 | **不写** |
| `CONN_LIGHT` | ★**空**★ | 22 | 0.300x1.300 | 14.200×5.700 | 10.500 | ★**已落 land**★ | **不写** |
| `C_AC_CSI_D0_CK_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_CK_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D0_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D0_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D1_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D1_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D2_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D2_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D3_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_AC_CSI_D0_D3_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_BULK_LIGHT_1V8` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_BULK_LIGHT_3V3` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_BULK_SENSOR_AVDD` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_BULK_SENSOR_CORE` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_BULK_SENSOR_VDD_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_BULK_VDD_1V8_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_BULK_VDD_3V3_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_BULK_V_CORE` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_BULK_V_SOC_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_DET_BAT` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_DET_VBUS_D` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_HF_LIGHT_1V8` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_HF_LIGHT_3V3` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_HF_SENSOR_AVDD` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_HF_SENSOR_CORE` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_HF_SENSOR_VDD_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_HF_VDD_1V8_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_HF_VDD_3V3_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_HF_V_CORE` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_HF_V_SOC_IO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_KEY_CAM` | ★**空**★ | 1 | 0.600x0.900 | 1.800×1.000 | 0.000 | 自绘通用占位 | **不写** |
| `C_KEY_PWR` | ★**空**★ | 1 | 0.600x0.900 | 1.800×1.000 | 0.000 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_KEY_VM` | ★**空**★ | 1 | 0.600x0.900 | 1.800×1.000 | 0.000 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_KEY_VP` | ★**空**★ | 1 | 0.600x0.900 | 1.800×1.000 | 0.000 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_RST` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_SUPV` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_SW_IN` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_SW_OUT` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_TEMP` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_VBUS_DEMO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Capacitor_SMD:C_0603_1608Metric` |
| `C_VBUS_GND` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_XTAL_IN` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `C_XTAL_OUT` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `D_ESD_CAM` | ★**空**★ | 2 | 0.600x0.900 | 2.700×1.600 | 2.300 | 自绘通用占位 | **写** `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` |
| `D_ESD_DEMO` | ★**空**★ | 2 | 0.600x0.900 | 2.700×1.600 | 2.300 | 自绘通用占位 | **写** `Diode_SMD:D_SOD-323` |
| `D_ESD_LIGHT` | ★**空**★ | 2 | 0.600x0.900 | 2.700×1.600 | 2.300 | 自绘通用占位 | **不写** |
| `D_ESD_USB_D` | ★**空**★ | 2 | 0.600x0.900 | 2.700×1.600 | 2.300 | 自绘通用占位 | **写** `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` |
| `D_LED_B` | ★**空**★ | 2 | 0.600x0.900 | 2.700×1.600 | 2.300 | 自绘通用占位 | **不写** |
| `D_LED_G` | ★**空**★ | 2 | 0.600x0.900 | 2.700×1.600 | 2.300 | 自绘通用占位 | **写** `LED_SMD:LED_0805_2012Metric` |
| `D_LED_R` | ★**空**★ | 2 | 0.600x0.900 | 2.700×1.600 | 2.300 | 自绘通用占位 | **写** `LED_SMD:LED_0603_1608Metric` |
| `FB_DEMO` | ★**空**★ | 2 | 0.550x0.900 | 2.000×1.600 | 1.000 | 自绘通用占位 | **写** `Inductor_SMD:L_0805_2012Metric` |
| `J_BOOT1` | ★**空**★ | 6 | 0.275x0.900 | 6.000×4.000 | 2.500 | 自绘通用占位 | **不写** |
| `J_CHG` | ★**空**★ | 2 | 0.275x0.900 | 6.000×4.000 | 0.500 | 自绘通用占位 | **不写** |
| `J_DEBUG` | ★**空**★ | 4 | 0.275x0.900 | 6.000×4.000 | 1.500 | 自绘通用占位 | **不写** |
| `J_SOM_P1` | ★**空**★ | 100 | 0.200x0.700 | 22.600×3.200 | 19.840 | 自绘通用占位 | **写** `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` |
| `J_SOM_P2` | ★**空**★ | 100 | 0.200x0.700 | 22.600×3.200 | 19.840 | 自绘通用占位 | **写** `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` |
| `J_SOM_P3` | ★**空**★ | 100 | 0.200x0.700 | 22.600×3.200 | 19.840 | 自绘通用占位 | **写** `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` |
| `J_SOM_P4` | ★**空**★ | 100 | 0.200x0.700 | 22.600×3.200 | 19.840 | 自绘通用占位 | **写** `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` |
| `J_UART` | ★**空**★ | 2 | 0.275x0.900 | 6.000×4.000 | 0.500 | 自绘通用占位 | **不写** |
| `J_USB_C` | ★**空**★ | 18 | 0.300x1.150 | ★无 (F.Fab 层无外框)★ | 7.500 | ★**已落 land**★ | **不写** |
| `Q1` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `Q2` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `Q_AND` | ★**空**★ | 3 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **写** `Package_TO_SOT_SMD:SOT-23` |
| `Q_ENVC` | ★**空**★ | 3 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **写** `Package_TO_SOT_SMD:SOT-23` |
| `Q_PG` | ★**空**★ | 3 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **写** `Package_TO_SOT_SMD:SOT-23` |
| `R_BAT_DET_1` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_BAT_DET_2` | ★**空**★ | 1 | 0.600x0.900 | 1.800×1.000 | 0.000 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_CC1_D` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_CC2_D` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_EN_VCORE` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_ID_JMP0` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `R_ID_JMP1` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `R_JTAG_TCK` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_JTAG_TDI` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_JTAG_TDO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_JTAG_TMS` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_KEY_CAM` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_KEY_PWR` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_KEY_VM` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_KEY_VP` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_LED_B` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `R_LED_G` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_LED_R` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_NTC_BAT` | ★**空**★ | 1 | 0.600x0.900 | 1.800×1.000 | 0.000 | 自绘通用占位 | **不写** |
| `R_PD_ON` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PG_PULL` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_BOOT_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_I2CA_SCL` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_I2CA_SDA` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_I2CB_SCL` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_I2CB_SDA` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_ID0` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_ID1` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_PG` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_PU_RESET_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_CK_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_CK_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D0_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D0_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D1_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D1_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D2_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D2_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D3_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SEL_D3_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_CSI_MCLK` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_FSIN` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_RESET_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_SPI_CSn` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_SPI_MISO` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_SPI_MOSI` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_SPI_SCLK` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_USB_D_N` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SER_USB_D_P` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SUPV_DIV1` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_SUPV_DIV2` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_TS_PULL` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **不写** |
| `R_VBUS_DET_D1` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `R_VBUS_DET_D2` | ★**空**★ | 2 | 0.600x0.900 | 1.800×1.000 | 1.600 | 自绘通用占位 | **写** `Resistor_SMD:R_0603_1608Metric` |
| `SW_BOOT` | ★**空**★ | 2 | 0.600x0.900 | 3.000×3.000 | 2.200 | 自绘通用占位 | **写** `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` |
| `SW_KEY_CAM` | ★**空**★ | 2 | 0.600x0.900 | 3.000×3.000 | 2.200 | 自绘通用占位 | **不写** |
| `SW_KEY_PWR` | ★**空**★ | 2 | 0.600x0.900 | 3.000×3.000 | 2.200 | 自绘通用占位 | **写** `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` |
| `SW_KEY_VM` | ★**空**★ | 2 | 0.600x0.900 | 3.000×3.000 | 2.200 | 自绘通用占位 | **写** `Button_Switch_SMD:SW_SPST_B3U-1000P` |
| `SW_KEY_VP` | ★**空**★ | 2 | 0.600x0.900 | 3.000×3.000 | 2.200 | 自绘通用占位 | **写** `Button_Switch_SMD:SW_SPST_B3U-1000P` |
| `SW_RST` | ★**空**★ | 2 | 0.600x0.900 | 3.000×3.000 | 2.200 | 自绘通用占位 | **写** `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` |
| `TP_BAT` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_BAT_CHG` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_BOOT` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_CSI_CK_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_CSI_CK_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_CSI_D0_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_CSI_D0_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_CK_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_CK_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D0_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D0_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D1_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D1_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D2_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D2_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D3_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_DSI_D3_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_FSIN` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_I2CA_SCL` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_I2CA_SDA` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_I2CB_SCL` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_I2CB_SDA` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_ID` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_JTAG` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_KEY_PWR` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_KEY_VM` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_KEY_VP` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_LED_B` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_LED_G` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_LED_R` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_LIGHT_3V3` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_MCLK` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_PG` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_PG_VCORE` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_PG_VIO` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_RESET` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_SYS` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_UART` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_USB_D_N` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_USB_D_P` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_VCORE` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `TP_VIO` | ★**空**★ | 1 | 0.180x0.900 | 1.400×1.400 | 0.000 | 自绘通用占位 | **不写** |
| `U_BATPROT` | ★**空**★ | 6 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `U_DCDC_VCORE` | ★**空**★ | 4 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **不写** |
| `U_DCDC_VIO` | ★**空**★ | 4 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **不写** |
| `U_EN_SW` | ★**空**★ | 4 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **不写** |
| `U_LDO_IO18` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `U_LDO_IO33` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `U_LDO_L18` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `U_LDO_L33` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `U_LDO_S12` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `U_LDO_S18B` | ★**空**★ | 5 | 0.600x0.900 | 4.940×5.000 | 5.476 | 自绘通用占位 | **不写** |
| `U_LDO_S28` | ★**空**★ | 4 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **不写** |
| `U_PWR_SW` | ★**空**★ | 4 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **不写** |
| `U_SUPV` | ★**空**★ | 4 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **不写** |
| `U_TEMP` | ★**空**★ | 6 | 0.450x0.300 | 2.500×2.250 | 2.344 | ★**已落 land**★ | **不写** |
| `X1` | ★**空**★ | 3 | 0.600x0.900 | 4.000×5.000 | 4.883 | 自绘通用占位 | **不写** |

## §2 写盘机制 (★本机 KiCad 10.0.8 实测 · 不许抄文档★)

★**KiCad 版本**: `10.0.8` (★`pcbnew.GetBuildVersion()` 实测★) · ★**库根**: `/home/yuewuya/kicad/AppDir/share/kicad/footprints`★

### §2.1 库封装名存在板文件哪个字段

★**答案**: 板文件里每个封装块的第一行 —— `(footprint "<库封装名>")` 的那个字符串 —— 就是 KiCad 的 `FPID` (库标识 + 封装名) 字段。★**本板 186 个全是 `(footprint ""` (空串) ⇒ 库名 0/186 非空**★。

```
  (footprint ""                       ← ★本板现状: 库封装名字段是空的★
    (layer "F.Cu")
    (uuid "01490acf-2e7f-4052-9ac4-a94f45e7f7cf")
    (at 93.3 38.6)
    (property "Reference" "C_BULK_SENSOR_CORE")
    (property "Value" "10µF")
    ... (pad / fp_line / fp_text ...) ...
  )
```

### §2.2 两种写法在本机的行为 (★实测 E1~E9 · 逐条可复跑★)

| 实验 | 写法 / 动作 | 本机实测结果 [实测] | 结论 |
|---|---|---|---|
| **E1** | python API `f.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", "C_0603_1608Metric"))` + `SaveBoard()` | ★整份文件只改了 **1 行**: `(footprint ""` → `(footprint "Capacitor_SMD:C_0603_1608Metric"`★; 重新加载后 `GetFPIDAsString()` = `Capacitor_SMD:C_0603_1608Metric` | ★**API 路径与文本路径等价, 且只动一行**★ |
| **E2** | 文本层写 `(footprint "Lib:Name"` | ★重新加载后 `GetFPIDAsString()` = `Capacitor_SMD:C_0603_1608Metric` · `GetUniStringLibId()` = 同值 · `GetLibItemName()` = `C_0603_1608Metric` · 焊盘数 2★ | ★**`"Lib:Name"` 字符串写法【本机可用】★** |
| **E3 / E4a** | 文本层写 `(footprint "NAME" (lib "LIB" "NAME")` | ★**`LoadBoard()` 直接返回 `None` (整板读不回来)**★ | ★**本机 KiCad 10.0.8 【不接受】这个写法★ ⇒ 写了 = 板文件报废**★ |
| **E4b** | 文本层写 `(footprint "NAME" (lib_id "LIB:NAME")` | ★**`LoadBoard()` 直接返回 `None`**★ | ★**同上, 不可用★** |
| **E4c** | 文本层写 `(footprint "C_0603_1608Metric"` (★裸封装名, 无库前缀★) | ★加载 OK (186 个封装都在) · 但 `GetUniStringLibId()` = `C_0603_1608Metric` (★把封装名当成了库名★) · `GetLibItemName()` = 同值 | ★**能读, 但装配厂拿不到「哪个库」⇒ 不可用★** |
| **E6 / E7** | E1 之后的整份文件逐行差分 + 该封装全部属性前后对比 | ★差分 **5 行** (★只有封装节点名那一行变★) · ★**焊盘 (号/网名/尺寸/位置) · bbox · fp_line 数 · uuid · Value · 层 · 位置 全部逐项相同**★ | ★**写库名不动任何铜箔/几何**★ |
| **E8** | 把库名指向不存在的库 (`NoSuchLib_XYZ:NoSuchFootprint_XYZ`) | ★`LoadBoard()` **正常** · `GetFPIDAsString()` = `NoSuchLib_XYZ:NoSuchFootprint_XYZ` | ★**板文件不会因为库名不存在而报错**★ ⇒ ★**这就是为什么必须有机器闸去 `test -f` 验封装文件在盘**★ |
| **E9** | 写 1 个之后统计全板 | ★空库名块 **186 → 185** · 具名块 **0 → 1** ⇒ ★**其余 185 个封装一个字节没被动**★ | ★**可以逐个写, 不必整板重写**★ |

### §2.3 ★「换 land 时把库名与 land 一起替换」的写法 (★本单作业包采用的那一种★)

★**做法 (★文本层·纯 python·零 pcbnew 依赖★)**:

```bash
# ★换 land + 写库名 = 对同一个封装块做两件事★
#   ① 删掉该封装块里板面自绘的 pad 与 F.Fab 外框
#   ② 插入目标 .kicad_mod 的 pad 块 (逐块换新 uuid + 按脚表重挂 net)
#   ③ 插入目标 .kicad_mod 的 F.Fab 外框 (fp_line / fp_rect)
#   ④ 把封装块第一行改成 (footprint "<Lib:Name>")
# ★★ ①②③ 与 ④ 【必须同一次做完】 ⇒ 板 md5 只变一次 ★★
```

★**逐件可复跑的实现**: `tmp/iss369/tools/sandbox_libid.py` 的 `build_legA_board()` (★换 land★) 与 `write_libids()` (★写库名★); ★**本单只把它们跑在 `tmp/iss369/sbx/` 的副本上, 真板零改动**★。

### §2.4 ★换完板文件里哪些字段会变★

| 字段 | 换 land + 写库名 后 | 证据 |
|---|---|---|
| `(footprint "…")` 那一行 | ★**变** (写上 `Lib:Name`)★ | E6/E7 逐行差分 |
| `pad` 块 (号 / 尺寸 / 位置 / 形状 / 层 / net) | ★**变** (整块换成官方 land 的)★ | 沙盒 S1 vs S0 |
| `F.Fab` 的 `fp_line` / `fp_rect` | ★**变** (整块换成官方件的)★ | 沙盒 S1 vs S0 |
| `uuid` | ★**变** (新块必须换新 uuid, 否则 KiCad 会认成同一个对象)★ | E1/E6 |
| `(property "Reference")` / `(property "Value")` | ★**不变**★ | E6/E7 属性逐项相同 |
| 走线 / 铜皮 / 网络表 | ★**不变** (换 land 不动 net 归属)★ | 沙盒 C4 恒 158 |
| ★**只写库名时 (零几何改动)**★ | ★**只有 `(footprint "…")` 那一行变, 其余全部逐字节不变**★ | 沙盒 S3 vs S0 差分 |

## §3 目标清单 (★90 件 + 96 件 = 186 件·一 ref 一件·不重不漏★)

★**写盘动作只有两种**: ★**写** (板面 `(footprint "…")` 写上 `Lib:Name`) 与 ★**不写** (写任何官方库名都是【假身份】: 板面铜箔与库件对不上)★。

★**判定口径 (★同一条口径贯穿两张表★)**:

1. ★**换 land 的 90 件 ⇒ 必须同时写库名**★ (★换 land 而不写库名 = 装配厂拿不到封装 + BOM 与板面对不上★)
2. ★**不动 land 的件 ⇒ 只有在【逐焊盘几何与官方件等价】时才写库名**★ (★本机全库穷举 ⇒ 只有 4 件合格★)
3. ★**其余 ⇒ 不写**, 并写清理由 (★型号/封装未选定 ⇒ 写库名 = 替老板拍板选型★)

### §3.1 表 A · 90 件 (★靶内 77 + 缺口 13 · 换官方 land + 同时写库名 · 12 字段★)

| ref | 桶 | 现占位几何 [实测] | 目标 `lib:name` | `.kicad_mod` 实存路径 + md5 | 目标几何 [实测] | 几何 Δ | pad↔net 序要改哪几条 | 要重接的 net 名单 | 腿 B 具名脚清单 (bare → `pinN`) | 证据等级 | 降级方案 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `C_AC_CSI_D0_CK_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_CK_N_SRC`, `CSI_D0_CK_N` | `C_AC_CSI_D0_CK_N` → `C_AC_CSI_D0_CK_N pin1` (net `CSI_D0_CK_N_SRC`); `C_AC_CSI_D0_CK_N` → `C_AC_CSI_D0_CK_N pin2` (net `CSI_D0_CK_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_CK_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_CK_P_SRC`, `CSI_D0_CK_P` | `C_AC_CSI_D0_CK_P` → `C_AC_CSI_D0_CK_P pin1` (net `CSI_D0_CK_P_SRC`); `C_AC_CSI_D0_CK_P` → `C_AC_CSI_D0_CK_P pin2` (net `CSI_D0_CK_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D0_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D0_N_SRC`, `CSI_D0_D0_N` | `C_AC_CSI_D0_D0_N` → `C_AC_CSI_D0_D0_N pin1` (net `CSI_D0_D0_N_SRC`); `C_AC_CSI_D0_D0_N` → `C_AC_CSI_D0_D0_N pin2` (net `CSI_D0_D0_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D0_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D0_P_SRC`, `CSI_D0_D0_P` | `C_AC_CSI_D0_D0_P` → `C_AC_CSI_D0_D0_P pin1` (net `CSI_D0_D0_P_SRC`); `C_AC_CSI_D0_D0_P` → `C_AC_CSI_D0_D0_P pin2` (net `CSI_D0_D0_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D1_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D1_N_SRC`, `CSI_D0_D1_N` | `C_AC_CSI_D0_D1_N` → `C_AC_CSI_D0_D1_N pin1` (net `CSI_D0_D1_N_SRC`); `C_AC_CSI_D0_D1_N` → `C_AC_CSI_D0_D1_N pin2` (net `CSI_D0_D1_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D1_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D1_P_SRC`, `CSI_D0_D1_P` | `C_AC_CSI_D0_D1_P` → `C_AC_CSI_D0_D1_P pin1` (net `CSI_D0_D1_P_SRC`); `C_AC_CSI_D0_D1_P` → `C_AC_CSI_D0_D1_P pin2` (net `CSI_D0_D1_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D2_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D2_N_SRC`, `CSI_D0_D2_N` | `C_AC_CSI_D0_D2_N` → `C_AC_CSI_D0_D2_N pin1` (net `CSI_D0_D2_N_SRC`); `C_AC_CSI_D0_D2_N` → `C_AC_CSI_D0_D2_N pin2` (net `CSI_D0_D2_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D2_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D2_P_SRC`, `CSI_D0_D2_P` | `C_AC_CSI_D0_D2_P` → `C_AC_CSI_D0_D2_P pin1` (net `CSI_D0_D2_P_SRC`); `C_AC_CSI_D0_D2_P` → `C_AC_CSI_D0_D2_P pin2` (net `CSI_D0_D2_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D3_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D3_N_SRC`, `CSI_D0_D3_N` | `C_AC_CSI_D0_D3_N` → `C_AC_CSI_D0_D3_N pin1` (net `CSI_D0_D3_N_SRC`); `C_AC_CSI_D0_D3_N` → `C_AC_CSI_D0_D3_N pin2` (net `CSI_D0_D3_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_AC_CSI_D0_D3_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_D0_D3_P_SRC`, `CSI_D0_D3_P` | `C_AC_CSI_D0_D3_P` → `C_AC_CSI_D0_D3_P pin1` (net `CSI_D0_D3_P_SRC`); `C_AC_CSI_D0_D3_P` → `C_AC_CSI_D0_D3_P pin2` (net `CSI_D0_D3_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_BULK_LIGHT_3V3` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `LIGHT_3V3`, `GND` | `C_BULK_LIGHT_3V3` → `C_BULK_LIGHT_3V3 pin1` (net `LIGHT_3V3`); `C_BULK_LIGHT_3V3` → `C_BULK_LIGHT_3V3 pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_BULK_VDD_1V8_IO` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `VDD_1V8_IO`, `GND` | `C_BULK_VDD_1V8_IO` → `C_BULK_VDD_1V8_IO pin1` (net `VDD_1V8_IO`); `C_BULK_VDD_1V8_IO` → `C_BULK_VDD_1V8_IO pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_BULK_VDD_3V3_IO` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `VDD_3V3_IO`, `GND` | `C_BULK_VDD_3V3_IO` → `C_BULK_VDD_3V3_IO pin1` (net `VDD_3V3_IO`); `C_BULK_VDD_3V3_IO` → `C_BULK_VDD_3V3_IO pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_DET_BAT` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `BAT_DET`, `GND` | `C_DET_BAT` → `C_DET_BAT pin1` (net `BAT_DET`); `C_DET_BAT` → `C_DET_BAT pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_DET_VBUS_D` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `GND`, `VBUS_DET_D` | `C_DET_VBUS_D` → `C_DET_VBUS_D pin1` (net `GND`); `C_DET_VBUS_D` → `C_DET_VBUS_D pin2` (net `VBUS_DET_D`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_HF_LIGHT_3V3` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `LIGHT_3V3`, `GND` | `C_HF_LIGHT_3V3` → `C_HF_LIGHT_3V3 pin1` (net `LIGHT_3V3`); `C_HF_LIGHT_3V3` → `C_HF_LIGHT_3V3 pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_HF_VDD_1V8_IO` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `VDD_1V8_IO`, `GND` | `C_HF_VDD_1V8_IO` → `C_HF_VDD_1V8_IO pin1` (net `VDD_1V8_IO`); `C_HF_VDD_1V8_IO` → `C_HF_VDD_1V8_IO pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_HF_VDD_3V3_IO` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `VDD_3V3_IO`, `GND` | `C_HF_VDD_3V3_IO` → `C_HF_VDD_3V3_IO pin1` (net `VDD_3V3_IO`); `C_HF_VDD_3V3_IO` → `C_HF_VDD_3V3_IO pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_KEY_PWR` | 靶内 | 焊盘 1 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 0.000 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +1 · Δfab -0.200×-0.200 mm · Δ中心距 +1.550 mm | 目标件焊盘 `2` 板面没有 ⇒ 补 (net 待重接); ★焊盘数 1→2 ⇒ 板面要补 1 个焊盘 | `KEY_PWR` | `C_KEY_PWR` → `C_KEY_PWR pin1` (net `KEY_PWR`); ★补行★ net `GND` · node1 `C_KEY_PWR pin2` | [实测]+[推算] | ★焊盘数 1→2 ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动; 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 0.000→1.550 mm, Δ+1.550) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_KEY_VM` | 靶内 | 焊盘 1 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 0.000 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +1 · Δfab -0.200×-0.200 mm · Δ中心距 +1.550 mm | 目标件焊盘 `2` 板面没有 ⇒ 补 (net 待重接); ★焊盘数 1→2 ⇒ 板面要补 1 个焊盘 | `KEY_VOL_M` | `C_KEY_VM` → `C_KEY_VM pin1` (net `KEY_VOL_M`); ★补行★ net `GND` · node1 `C_KEY_VM pin2` | [实测]+[推算] | ★焊盘数 1→2 ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动; 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 0.000→1.550 mm, Δ+1.550) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_KEY_VP` | 靶内 | 焊盘 1 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 0.000 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +1 · Δfab -0.200×-0.200 mm · Δ中心距 +1.550 mm | 目标件焊盘 `2` 板面没有 ⇒ 补 (net 待重接); ★焊盘数 1→2 ⇒ 板面要补 1 个焊盘 | `KEY_VOL_P` | `C_KEY_VP` → `C_KEY_VP pin1` (net `KEY_VOL_P`); ★补行★ net `GND` · node1 `C_KEY_VP pin2` | [实测]+[推算] | ★焊盘数 1→2 ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动; 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 0.000→1.550 mm, Δ+1.550) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_RST` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RESET_N_SOC`, `GND` | `C_RST` → `C_RST pin1` (net `RESET_N_SOC`); `C_RST` → `C_RST pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_SW_IN` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `BAT_SW`, `GND` | `C_SW_IN` → `C_SW_IN pin1` (net `BAT_SW`); `C_SW_IN` → `C_SW_IN pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_SW_OUT` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `SYS`, `GND` | `C_SW_OUT` → `C_SW_OUT pin1` (net `SYS`); `C_SW_OUT` → `C_SW_OUT pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_TEMP` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `VDD_3V3_IO`, `GND` | `C_TEMP` → `C_TEMP pin1` (net `VDD_3V3_IO`); `C_TEMP` → `C_TEMP pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `C_VBUS_DEMO` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.200×-0.200 mm · Δ中心距 -0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RAIL_DEMO_5V`, `GND` | `C_VBUS_DEMO` → `C_VBUS_DEMO pin1` (net `RAIL_DEMO_5V`); `C_VBUS_DEMO` → `C_VBUS_DEMO pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.550 mm, Δ-0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `D_LED_G` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 2.700×1.600 mm · 中心距 2.300 mm | `LED_SMD:LED_0805_2012Metric` | `LED_SMD.pretty/LED_0805_2012Metric.kicad_mod` md5 `7616eddd0b9951dec0bf5bdfc3df0a77` | 焊盘数 2 · fab 外框 2.000×1.200 mm · 中心距 1.875 mm | Δ焊盘数 +0 · Δfab -0.700×-0.400 mm · Δ中心距 -0.425 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `LED_G_D`, `GND` | `D_LED_G` → `D_LED_G pin1` (net `LED_G_D`); `D_LED_G` → `D_LED_G pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.300→1.875 mm, Δ-0.425) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `D_LED_R` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 2.700×1.600 mm · 中心距 2.300 mm | `LED_SMD:LED_0603_1608Metric` | `LED_SMD.pretty/LED_0603_1608Metric.kicad_mod` md5 `ac369a6895f54b78d16871a76dc9d08e` | 焊盘数 2 · fab 外框 1.600×0.800 mm · 中心距 1.575 mm | Δ焊盘数 +0 · Δfab -1.100×-0.800 mm · Δ中心距 -0.725 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `LED_R_D`, `GND` | `D_LED_R` → `D_LED_R pin1` (net `LED_R_D`); `D_LED_R` → `D_LED_R pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.300→1.575 mm, Δ-0.725) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_BAT_DET_1` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `BAT_DET`, `BAT` | `R_BAT_DET_1` → `R_BAT_DET_1 pin1` (net `BAT_DET`); `R_BAT_DET_1` → `R_BAT_DET_1 pin2` (net `BAT`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_BAT_DET_2` | 靶内 | 焊盘 1 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 0.000 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +1 · Δfab -0.200×-0.175 mm · Δ中心距 +1.650 mm | 目标件焊盘 `2` 板面没有 ⇒ 补 (net 待重接); ★焊盘数 1→2 ⇒ 板面要补 1 个焊盘 | `BAT_DET` | `R_BAT_DET_2` → `R_BAT_DET_2 pin1` (net `BAT_DET`); ★补行★ net `GND` · node1 `R_BAT_DET_2 pin2` | [实测]+[推算] | ★焊盘数 1→2 ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动; 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 0.000→1.650 mm, Δ+1.650) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_CC1_D` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `GND`, `USB_CC1` | `R_CC1_D` → `R_CC1_D pin1` (net `GND`); `R_CC1_D` → `R_CC1_D pin2` (net `USB_CC1`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_CC2_D` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `USB_CC2`, `GND` | `R_CC2_D` → `R_CC2_D pin1` (net `USB_CC2`); `R_CC2_D` → `R_CC2_D pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_EN_VCORE` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `EN_VCORE`, `VDD_1V8_IO` | `R_EN_VCORE` → `R_EN_VCORE pin1` (net `EN_VCORE`); `R_EN_VCORE` → `R_EN_VCORE pin2` (net `VDD_1V8_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_JTAG_TCK` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `JTAG_TCK_SOC`, `JTAG_TCK` | `R_JTAG_TCK` → `R_JTAG_TCK pin1` (net `JTAG_TCK_SOC`); `R_JTAG_TCK` → `R_JTAG_TCK pin2` (net `JTAG_TCK`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_JTAG_TDI` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `JTAG_TDI_SOC`, `JTAG_TDI` | `R_JTAG_TDI` → `R_JTAG_TDI pin1` (net `JTAG_TDI_SOC`); `R_JTAG_TDI` → `R_JTAG_TDI pin2` (net `JTAG_TDI`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_JTAG_TDO` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `JTAG_TDO_SOC`, `JTAG_TDO` | `R_JTAG_TDO` → `R_JTAG_TDO pin1` (net `JTAG_TDO_SOC`); `R_JTAG_TDO` → `R_JTAG_TDO pin2` (net `JTAG_TDO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_JTAG_TMS` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `JTAG_TMS_SOC`, `JTAG_TMS` | `R_JTAG_TMS` → `R_JTAG_TMS pin1` (net `JTAG_TMS_SOC`); `R_JTAG_TMS` → `R_JTAG_TMS pin2` (net `JTAG_TMS`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_KEY_CAM` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `KEY_CAM`, `VDD_3V3_IO` | `R_KEY_CAM` → `R_KEY_CAM pin1` (net `KEY_CAM`); `R_KEY_CAM` → `R_KEY_CAM pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_KEY_PWR` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `KEY_PWR`, `VDD_3V3_IO` | `R_KEY_PWR` → `R_KEY_PWR pin1` (net `KEY_PWR`); `R_KEY_PWR` → `R_KEY_PWR pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_KEY_VM` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `KEY_VOL_M`, `VDD_3V3_IO` | `R_KEY_VM` → `R_KEY_VM pin1` (net `KEY_VOL_M`); `R_KEY_VM` → `R_KEY_VM pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_KEY_VP` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `KEY_VOL_P`, `VDD_3V3_IO` | `R_KEY_VP` → `R_KEY_VP pin1` (net `KEY_VOL_P`); `R_KEY_VP` → `R_KEY_VP pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_LED_G` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `LED_G`, `LED_G_D` | `R_LED_G` → `R_LED_G pin1` (net `LED_G`); `R_LED_G` → `R_LED_G pin2` (net `LED_G_D`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_LED_R` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `LED_R`, `LED_R_D` | `R_LED_R` → `R_LED_R pin1` (net `LED_R`); `R_LED_R` → `R_LED_R pin2` (net `LED_R_D`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PD_ON` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `PWR_ON`, `GND` | `R_PD_ON` → `R_PD_ON pin1` (net `PWR_ON`); `R_PD_ON` → `R_PD_ON pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PG_PULL` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `PG_AND`, `VDD_1V8_IO` | `R_PG_PULL` → `R_PG_PULL pin1` (net `PG_AND`); `R_PG_PULL` → `R_PG_PULL pin2` (net `VDD_1V8_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_BOOT_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `BOOT_N`, `VDD_1V8_IO` | `R_PU_BOOT_N` → `R_PU_BOOT_N pin1` (net `BOOT_N`); `R_PU_BOOT_N` → `R_PU_BOOT_N pin2` (net `VDD_1V8_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_I2CA_SCL` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `I2C_A_SCL`, `VDD_1V8_IO` | `R_PU_I2CA_SCL` → `R_PU_I2CA_SCL pin1` (net `I2C_A_SCL`); `R_PU_I2CA_SCL` → `R_PU_I2CA_SCL pin2` (net `VDD_1V8_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_I2CA_SDA` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `I2C_A_SDA`, `VDD_1V8_IO` | `R_PU_I2CA_SDA` → `R_PU_I2CA_SDA pin1` (net `I2C_A_SDA`); `R_PU_I2CA_SDA` → `R_PU_I2CA_SDA pin2` (net `VDD_1V8_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_I2CB_SCL` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `I2C_B_SCL`, `VDD_3V3_IO` | `R_PU_I2CB_SCL` → `R_PU_I2CB_SCL pin1` (net `I2C_B_SCL`); `R_PU_I2CB_SCL` → `R_PU_I2CB_SCL pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_I2CB_SDA` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `I2C_B_SDA`, `VDD_3V3_IO` | `R_PU_I2CB_SDA` → `R_PU_I2CB_SDA pin1` (net `I2C_B_SDA`); `R_PU_I2CB_SDA` → `R_PU_I2CB_SDA pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_ID0` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `ID_DETECT_0`, `VDD_3V3_IO` | `R_PU_ID0` → `R_PU_ID0 pin1` (net `ID_DETECT_0`); `R_PU_ID0` → `R_PU_ID0 pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_ID1` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `ID_DETECT_1`, `VDD_3V3_IO` | `R_PU_ID1` → `R_PU_ID1 pin1` (net `ID_DETECT_1`); `R_PU_ID1` → `R_PU_ID1 pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_PG` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `VDD_3V3_IO`, `PWR_GOOD` | `R_PU_PG` → `R_PU_PG pin1` (net `PWR_GOOD`); `R_PU_PG` → `R_PU_PG pin2` (net `VDD_3V3_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_PU_RESET_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RESET_N`, `VDD_1V8_IO` | `R_PU_RESET_N` → `R_PU_RESET_N pin1` (net `RESET_N`); `R_PU_RESET_N` → `R_PU_RESET_N pin2` (net `VDD_1V8_IO`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_CK_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_CK_N_SRC`, `DSI_D0_CK_N` | `R_SEL_CK_N` → `R_SEL_CK_N pin1` (net `DSI_D0_CK_N_SRC`); `R_SEL_CK_N` → `R_SEL_CK_N pin2` (net `DSI_D0_CK_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_CK_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_CK_P_SRC`, `DSI_D0_CK_P` | `R_SEL_CK_P` → `R_SEL_CK_P pin1` (net `DSI_D0_CK_P_SRC`); `R_SEL_CK_P` → `R_SEL_CK_P pin2` (net `DSI_D0_CK_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D0_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D0_N_SRC`, `DSI_D0_D0_N` | `R_SEL_D0_N` → `R_SEL_D0_N pin1` (net `DSI_D0_D0_N_SRC`); `R_SEL_D0_N` → `R_SEL_D0_N pin2` (net `DSI_D0_D0_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D0_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D0_P_SRC`, `DSI_D0_D0_P` | `R_SEL_D0_P` → `R_SEL_D0_P pin1` (net `DSI_D0_D0_P_SRC`); `R_SEL_D0_P` → `R_SEL_D0_P pin2` (net `DSI_D0_D0_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D1_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D1_N_SRC`, `DSI_D0_D1_N` | `R_SEL_D1_N` → `R_SEL_D1_N pin1` (net `DSI_D0_D1_N_SRC`); `R_SEL_D1_N` → `R_SEL_D1_N pin2` (net `DSI_D0_D1_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D1_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D1_P_SRC`, `DSI_D0_D1_P` | `R_SEL_D1_P` → `R_SEL_D1_P pin1` (net `DSI_D0_D1_P_SRC`); `R_SEL_D1_P` → `R_SEL_D1_P pin2` (net `DSI_D0_D1_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D2_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D2_N_SRC`, `DSI_D0_D2_N` | `R_SEL_D2_N` → `R_SEL_D2_N pin1` (net `DSI_D0_D2_N_SRC`); `R_SEL_D2_N` → `R_SEL_D2_N pin2` (net `DSI_D0_D2_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D2_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D2_P_SRC`, `DSI_D0_D2_P` | `R_SEL_D2_P` → `R_SEL_D2_P pin1` (net `DSI_D0_D2_P_SRC`); `R_SEL_D2_P` → `R_SEL_D2_P pin2` (net `DSI_D0_D2_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D3_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D3_N_SRC`, `DSI_D0_D3_N` | `R_SEL_D3_N` → `R_SEL_D3_N pin1` (net `DSI_D0_D3_N_SRC`); `R_SEL_D3_N` → `R_SEL_D3_N pin2` (net `DSI_D0_D3_N`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SEL_D3_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `DSI_D0_D3_P_SRC`, `DSI_D0_D3_P` | `R_SEL_D3_P` → `R_SEL_D3_P pin1` (net `DSI_D0_D3_P_SRC`); `R_SEL_D3_P` → `R_SEL_D3_P pin2` (net `DSI_D0_D3_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_CSI_MCLK` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `CSI_MCLK_SRC`, `CSI_MCLK` | `R_SER_CSI_MCLK` → `R_SER_CSI_MCLK pin1` (net `CSI_MCLK_SRC`); `R_SER_CSI_MCLK` → `R_SER_CSI_MCLK pin2` (net `CSI_MCLK`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_FSIN` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `FSIN_OUT`, `FSIN` | `R_SER_FSIN` → `R_SER_FSIN pin1` (net `FSIN_OUT`); `R_SER_FSIN` → `R_SER_FSIN pin2` (net `FSIN`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_RESET_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RESET_N`, `RESET_N_SOC` | `R_SER_RESET_N` → `R_SER_RESET_N pin1` (net `RESET_N`); `R_SER_RESET_N` → `R_SER_RESET_N pin2` (net `RESET_N_SOC`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_SPI_CSn` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `SPI_CSn`, `SPI_CSn_BOOT` | `R_SER_SPI_CSn` → `R_SER_SPI_CSn pin1` (net `SPI_CSn`); `R_SER_SPI_CSn` → `R_SER_SPI_CSn pin2` (net `SPI_CSn_BOOT`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_SPI_MISO` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `SPI_MISO`, `SPI_MISO_BOOT` | `R_SER_SPI_MISO` → `R_SER_SPI_MISO pin1` (net `SPI_MISO`); `R_SER_SPI_MISO` → `R_SER_SPI_MISO pin2` (net `SPI_MISO_BOOT`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_SPI_MOSI` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `SPI_MOSI`, `SPI_MOSI_BOOT` | `R_SER_SPI_MOSI` → `R_SER_SPI_MOSI pin1` (net `SPI_MOSI`); `R_SER_SPI_MOSI` → `R_SER_SPI_MOSI pin2` (net `SPI_MOSI_BOOT`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_SPI_SCLK` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `SPI_SCLK`, `SPI_SCLK_BOOT` | `R_SER_SPI_SCLK` → `R_SER_SPI_SCLK pin1` (net `SPI_SCLK`); `R_SER_SPI_SCLK` → `R_SER_SPI_SCLK pin2` (net `SPI_SCLK_BOOT`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_USB_D_N` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `USB_D_N_SRC`, `NET_USB_D_N_TYPEC` | `R_SER_USB_D_N` → `R_SER_USB_D_N pin1` (net `USB_D_N_SRC`); `R_SER_USB_D_N` → `R_SER_USB_D_N pin2` (net `NET_USB_D_N_TYPEC`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SER_USB_D_P` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `USB_D_P_SRC`, `NET_USB_D_P_TYPEC` | `R_SER_USB_D_P` → `R_SER_USB_D_P pin1` (net `USB_D_P_SRC`); `R_SER_USB_D_P` → `R_SER_USB_D_P pin2` (net `NET_USB_D_P_TYPEC`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SUPV_DIV1` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `V_SOC_IO`, `SUPV_SENSE` | `R_SUPV_DIV1` → `R_SUPV_DIV1 pin1` (net `V_SOC_IO`); `R_SUPV_DIV1` → `R_SUPV_DIV1 pin2` (net `SUPV_SENSE`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; BOM OPN = RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_SUPV_DIV2` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `SUPV_SENSE`, `GND` | `R_SUPV_DIV2` → `R_SUPV_DIV2 pin1` (net `SUPV_SENSE`); `R_SUPV_DIV2` → `R_SUPV_DIV2 pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; BOM OPN = RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_VBUS_DET_D1` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RAIL_DEMO_5V`, `VBUS_DET_D` | `R_VBUS_DET_D1` → `R_VBUS_DET_D1 pin1` (net `RAIL_DEMO_5V`); `R_VBUS_DET_D1` → `R_VBUS_DET_D1 pin2` (net `VBUS_DET_D`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `R_VBUS_DET_D2` | 靶内 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 1.800×1.000 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.600×0.825 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.200×-0.175 mm · Δ中心距 +0.050 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `VBUS_DET_D`, `GND` | `R_VBUS_DET_D2` → `R_VBUS_DET_D2 pin1` (net `VBUS_DET_D`); `R_VBUS_DET_D2` → `R_VBUS_DET_D2 pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.600→1.650 mm, Δ+0.050) ⇒ 走线端点跟着挪; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `CHG_GND_STAR` | 缺口 | 焊盘 1 个 · 0.600x0.900 mm · fab 外框 4.000×5.000 mm · 中心距 0.000 mm | `TestPoint:TestPoint_Pad_D1.0mm` | `TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod` md5 `cea8eb3ba9b799767624661848b00243` | 焊盘数 1 · fab 外框 0.000×0.000 mm · 中心距 0.000 mm | Δ焊盘数 +0 · Δfab 不适用 (目标件 F.Fab 层无外框) · Δ中心距 +0.000 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `GND` | `CHG_GND_STAR` → `CHG_GND_STAR pin1` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 0.000→0.000 mm, Δ+0.000) ⇒ 走线端点跟着挪; BOM OPN = [0数据]; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `D_ESD_CAM` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 2.700×1.600 mm · 中心距 2.300 mm | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | `Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod` md5 `0edfa97bd7bd277f3c05acf2bee23892` | 焊盘数 2 · fab 外框 1.000×0.600 mm · 中心距 0.700 mm | Δ焊盘数 +0 · Δfab -1.700×-1.000 mm · Δ中心距 -1.600 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `GND`, `CSI_D0_CK_P` | `D_ESD_CAM` → `D_ESD_CAM pin1` (net `GND`); `D_ESD_CAM` → `D_ESD_CAM pin2` (net `CSI_D0_CK_P`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.300→0.700 mm, Δ-1.600) ⇒ 走线端点跟着挪; BOM OPN = TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `D_ESD_DEMO` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 2.700×1.600 mm · 中心距 2.300 mm | `Diode_SMD:D_SOD-323` | `Diode_SMD.pretty/D_SOD-323.kicad_mod` md5 `bce0278c9b9af83e2de3cd130e6c04ed` | 焊盘数 2 · fab 外框 1.800×1.400 mm · 中心距 2.100 mm | Δ焊盘数 +0 · Δfab -0.900×-0.200 mm · Δ中心距 -0.200 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RAIL_DEMO_5V`, `GND` | `D_ESD_DEMO` → `D_ESD_DEMO pin1` (net `RAIL_DEMO_5V`); `D_ESD_DEMO` → `D_ESD_DEMO pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.300→2.100 mm, Δ-0.200) ⇒ 走线端点跟着挪; BOM OPN = PESD5V0S1BA (Nexperia SOD-323 2-lead · VRWM 5V · VBR 6V min · IEC 61000-4-2 >30kV); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `D_ESD_USB_D` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 2.700×1.600 mm · 中心距 2.300 mm | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | `Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod` md5 `0edfa97bd7bd277f3c05acf2bee23892` | 焊盘数 2 · fab 外框 1.000×0.600 mm · 中心距 0.700 mm | Δ焊盘数 +0 · Δfab -1.700×-1.000 mm · Δ中心距 -1.600 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `USB_D_P_SRC`, `GND` | `D_ESD_USB_D` → `D_ESD_USB_D pin1` (net `NET_USB_D_P_TYPEC`); `D_ESD_USB_D` → `D_ESD_USB_D pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.300→0.700 mm, Δ-1.600) ⇒ 走线端点跟着挪; BOM OPN = TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `FB_DEMO` | 缺口 | 焊盘 2 个 · 0.550x0.900 mm · fab 外框 2.000×1.600 mm · 中心距 1.000 mm | `Inductor_SMD:L_0805_2012Metric` | `Inductor_SMD.pretty/L_0805_2012Metric.kicad_mod` md5 `4e67ede5911eab38accb2ef9e57de79c` | 焊盘数 2 · fab 外框 2.000×0.900 mm · 中心距 2.125 mm | Δ焊盘数 +0 · Δfab +0.000×-0.700 mm · Δ中心距 +1.125 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RAIL_DEMO_5V`, `GND` | `FB_DEMO` → `FB_DEMO pin1` (net `RAIL_DEMO_5V`); `FB_DEMO` → `FB_DEMO pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 1.000→2.125 mm, Δ+1.125) ⇒ 走线端点跟着挪; BOM OPN = BLM21PG221SN1D (Murata BLM21PG 0805 2012 metric · 220Ω ±25%@100MHz · 2000mA · DCR 45mΩ max); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `Q_AND` | 缺口 | 焊盘 3 个 · 0.600x0.900 mm · fab 外框 4.000×5.000 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3 · fab 外框 0.000×0.000 mm · 中心距 2.102 mm | Δ焊盘数 +0 · Δfab 不适用 (目标件 F.Fab 层无外框) · Δ中心距 -2.781 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `RESET_N`, `GND`, `PG_AND` | `Q_AND` → `Q_AND pin1` (net `RESET_N`); `Q_AND` → `Q_AND pin2` (net `GND`); `Q_AND` → `Q_AND pin3` (net `PG_AND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 4.883→2.102 mm, Δ-2.781) ⇒ 走线端点跟着挪; BOM OPN = AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `Q_ENVC` | 缺口 | 焊盘 3 个 · 0.600x0.900 mm · fab 外框 4.000×5.000 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3 · fab 外框 0.000×0.000 mm · 中心距 2.102 mm | Δ焊盘数 +0 · Δfab 不适用 (目标件 F.Fab 层无外框) · Δ中心距 -2.781 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `PG_AND`, `GND`, `EN_VCORE` | `Q_ENVC` → `Q_ENVC pin1` (net `PG_AND`); `Q_ENVC` → `Q_ENVC pin2` (net `GND`); `Q_ENVC` → `Q_ENVC pin3` (net `EN_VCORE`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 4.883→2.102 mm, Δ-2.781) ⇒ 走线端点跟着挪; BOM OPN = AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `Q_PG` | 缺口 | 焊盘 3 个 · 0.600x0.900 mm · fab 外框 4.000×5.000 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3 · fab 外框 0.000×0.000 mm · 中心距 2.102 mm | Δ焊盘数 +0 · Δfab 不适用 (目标件 F.Fab 层无外框) · Δ中心距 -2.781 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `PWR_ON`, `BAT_SW`, `PWR_GOOD` | `Q_PG` → `Q_PG pin1` (net `PWR_GOOD`); `Q_PG` → `Q_PG pin2` (net `BAT_SW`); `Q_PG` → `Q_PG pin3` (net `PWR_ON`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 4.883→2.102 mm, Δ-2.781) ⇒ 走线端点跟着挪; BOM OPN = DMP3098L (Diodes Inc SOT23 3-pin · −30V · RDS(on) 98mΩ typ@-4.5V · IDSS ≤800nA); 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `SW_BOOT` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 3.000×3.000 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4 · fab 外框 4.200×2.800 mm · 中心距 4.401 mm | Δ焊盘数 +2 · Δfab +1.200×-0.200 mm · Δ中心距 +2.201 mm | ★焊盘数 2→4 ⇒ 板面要补 2 个焊盘 (焊盘号 `1` / `2` 在目标件里各出现两次 ⇒ 机械脚·按 KiCad 规则同号焊盘必须同网) | `BOOT_N`, `GND` | `SW_BOOT` → `SW_BOOT pin1` (net `BOOT_N`); `SW_BOOT` → `SW_BOOT pin2` (net `GND`) | [实测]+[推算] | ★焊盘数 2→4 ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动; 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.200→4.401 mm, Δ+2.201) ⇒ 走线端点跟着挪; BOM OPN = [0数据]; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `SW_KEY_PWR` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 3.000×3.000 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4 · fab 外框 4.200×2.800 mm · 中心距 4.401 mm | Δ焊盘数 +2 · Δfab +1.200×-0.200 mm · Δ中心距 +2.201 mm | ★焊盘数 2→4 ⇒ 板面要补 2 个焊盘 (焊盘号 `1` / `2` 在目标件里各出现两次 ⇒ 机械脚·按 KiCad 规则同号焊盘必须同网) | `KEY_PWR`, `GND` | `SW_KEY_PWR` → `SW_KEY_PWR pin1` (net `KEY_PWR`); `SW_KEY_PWR` → `SW_KEY_PWR pin2` (net `GND`) | [实测]+[推算] | ★焊盘数 2→4 ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动; 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.200→4.401 mm, Δ+2.201) ⇒ 走线端点跟着挪; BOM OPN = [0数据]; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `SW_KEY_VM` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 3.000×3.000 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_SPST_B3U-1000P` | `Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod` md5 `749f20c5ab898069ade01682274c7bbf` | 焊盘数 2 · fab 外框 3.000×2.500 mm · 中心距 3.400 mm | Δ焊盘数 +0 · Δfab +0.000×-0.500 mm · Δ中心距 +1.200 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `KEY_VOL_M`, `GND` | `SW_KEY_VM` → `SW_KEY_VM pin1` (net `KEY_VOL_M`); `SW_KEY_VM` → `SW_KEY_VM pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.200→3.400 mm, Δ+1.200) ⇒ 走线端点跟着挪; BOM OPN = [0数据]; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `SW_KEY_VP` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 3.000×3.000 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_SPST_B3U-1000P` | `Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod` md5 `749f20c5ab898069ade01682274c7bbf` | 焊盘数 2 · fab 外框 3.000×2.500 mm · 中心距 3.400 mm | Δ焊盘数 +0 · Δfab +0.000×-0.500 mm · Δ中心距 +1.200 mm | 无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变) | `KEY_VOL_P`, `GND` | `SW_KEY_VP` → `SW_KEY_VP pin1` (net `KEY_VOL_P`); `SW_KEY_VP` → `SW_KEY_VP pin2` (net `GND`) | [实测]+[推算] | 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.200→3.400 mm, Δ+1.200) ⇒ 走线端点跟着挪; BOM OPN = [0数据]; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |
| `SW_RST` | 缺口 | 焊盘 2 个 · 0.600x0.900 mm · fab 外框 3.000×3.000 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4 · fab 外框 4.200×2.800 mm · 中心距 4.401 mm | Δ焊盘数 +2 · Δfab +1.200×-0.200 mm · Δ中心距 +2.201 mm | ★焊盘数 2→4 ⇒ 板面要补 2 个焊盘 (焊盘号 `1` / `2` 在目标件里各出现两次 ⇒ 机械脚·按 KiCad 规则同号焊盘必须同网) | `RESET_N`, `GND` | `SW_RST` → `SW_RST pin1` (net `RESET_N`); `SW_RST` → `SW_RST pin2` (net `GND`) | [实测]+[推算] | ★焊盘数 2→4 ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动; 本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 2.200→4.401 mm, Δ+2.201) ⇒ 走线端点跟着挪; BOM OPN = [0数据]; 若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算] |

★**90 件小结 [实测]**: 目标库件共 **11** 个不同的 `.kicad_mod`; ★**其中 7 件的焊盘数会变** (板面脚数 → 目标脚数) ⇒ 这 7 件换完 land 后 C3「焊盘数 == 网表推出的脚数」会由绿转红, ★**必须与腿 B 的具名脚改名同时做**★ (★C3 红 = 脚表没跟着改★)。

### §3.2 表 B · 96 件 (★其余 186 − 90 · 逐件给「写什么」或「为什么不写」★)

| ref | 桶 | 动作 | 目标 `lib:name` (或「不需要写」) | `.kicad_mod` 实存路径 + md5 | 理由 | 证据等级 |
|---|---|---|---|---|---|---|
| `BT_432243` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「★板文件封装: 2 焊盘 (432243 3.7V ≥420mAh)」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `CONN_CAM` | 其它 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「待定」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `CONN_LIGHT` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | 板面已按原厂图纸落了 land (有 courtyard) ⇒ 不是占位; 但本机官方件与板面**几何不等价** (板面 22 焊盘 0.30x1.30mm (RPi CM5IO 抄件·无壳体固定柱); 官方 FH12-22S 带 2 个固定柱焊盘 ⇒ 24 焊盘; 官方 Connector_FFC-FPC:Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal 实测 24 焊盘 vs 板面 22) ⇒ 写该库名 = 板面铜箔与库件对不上 (假身份) ⇒ 不写; 建议改用 property 'Footprint' 记原厂封装号 (登记·不代拍) | [实测] |
| `C_BULK_LIGHT_1V8` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_BULK_SENSOR_AVDD` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_BULK_SENSOR_CORE` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_BULK_SENSOR_VDD_IO` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_BULK_V_CORE` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_BULK_V_SOC_IO` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_HF_LIGHT_1V8` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_HF_SENSOR_AVDD` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_HF_SENSOR_CORE` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_HF_SENSOR_VDD_IO` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_HF_V_CORE` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_HF_V_SOC_IO` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_KEY_CAM` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_SUPV` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_VBUS_GND` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_XTAL_IN` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `C_XTAL_OUT` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `D_ESD_LIGHT` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「★板文件封装: 2 焊盘 (ESD 阵列 [待选型])」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `D_LED_B` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `J_BOOT1` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `J_CHG` | 其它 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「待定」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `J_DEBUG` | 靶内-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「待定」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `J_SOM_P1` | 其它 | **写** | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | `Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod` md5 `6afd4648ced47278611e6ab4859510e9` | 板面铜箔已就是该官方封装 (逐焊盘实测: 焊盘数 100=100 · 尺寸 0.200x0.700 全同 · 位置/中心距 Δ<=0.001mm · 相对官方件旋转 180°) ⇒ 写 lib_id 零铜箔改动, 只补上『这块 land 是谁』的身份 ⇒ 写 | [实测] |
| `J_SOM_P2` | 缺口-非C4 | **写** | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | `Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod` md5 `6afd4648ced47278611e6ab4859510e9` | 板面铜箔已就是该官方封装 (逐焊盘实测: 焊盘数 100=100 · 尺寸 0.200x0.700 全同 · 位置/中心距 Δ<=0.001mm · 相对官方件旋转 180°) ⇒ 写 lib_id 零铜箔改动, 只补上『这块 land 是谁』的身份 ⇒ 写 | [实测] |
| `J_SOM_P3` | 其它 | **写** | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | `Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod` md5 `6afd4648ced47278611e6ab4859510e9` | 板面铜箔已就是该官方封装 (逐焊盘实测: 焊盘数 100=100 · 尺寸 0.200x0.700 全同 · 位置/中心距 Δ<=0.001mm · 相对官方件旋转 180°) ⇒ 写 lib_id 零铜箔改动, 只补上『这块 land 是谁』的身份 ⇒ 写 | [实测] |
| `J_SOM_P4` | 缺口-非C4 | **写** | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | `Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod` md5 `6afd4648ced47278611e6ab4859510e9` | 板面铜箔已就是该官方封装 (逐焊盘实测: 焊盘数 100=100 · 尺寸 0.200x0.700 全同 · 位置/中心距 Δ<=0.001mm · 相对官方件旋转 180°) ⇒ 写 lib_id 零铜箔改动, 只补上『这块 land 是谁』的身份 ⇒ 写 | [实测] |
| `J_UART` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=可选 ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `J_USB_C` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | 板面已按原厂图纸落了 land (有 courtyard) ⇒ 不是占位; 但本机官方件与板面**几何不等价** (板面 16 焊盘 @0.50mm pitch (GCT 原厂图纸 Rev B3·只留 16 信号焊盘); 官方件另含 2x Ø0.65mm 壳体固定孔 + 接地焊盘 ⇒ 22 焊盘; 官方 Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal 实测 22 焊盘 vs 板面 16) ⇒ 写该库名 = 板面铜箔与库件对不上 (假身份) ⇒ 不写; 建议改用 property 'Footprint' 记原厂封装号 (登记·不代拍) | [实测] |
| `Q1` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「SON-8 Q3, 3.3 x 3.3 mm」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `Q2` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「SON-8 Q3, 3.3 x 3.3 mm」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `R_ID_JMP0` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `R_ID_JMP1` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `R_LED_B` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `R_NTC_BAT` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `R_TS_PULL` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「待定」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `SW_KEY_CAM` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「★板文件封装: 2 焊盘 (按键 (待选型))」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `TP_BAT` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_BAT_CHG` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_BOOT` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_CSI_CK_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_CSI_CK_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_CSI_D0_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_CSI_D0_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_CK_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_CK_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D0_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D0_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D1_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D1_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D2_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D2_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D3_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_DSI_D3_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_FSIN` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_I2CA_SCL` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_I2CA_SDA` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_I2CB_SCL` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_I2CB_SDA` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_ID` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_JTAG` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_KEY_PWR` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_KEY_VM` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_KEY_VP` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_LED_B` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_LED_G` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_LED_R` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_LIGHT_3V3` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_MCLK` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_PG` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_PG_VCORE` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_PG_VIO` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_RESET` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_SYS` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_UART` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_USB_D_N` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_USB_D_P` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_VCORE` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `TP_VIO` | TP | **不写** | ★**不需要写**★ | — | 测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; 板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 (容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 ⇒ 不写 | [实测] |
| `U_BATPROT` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「★板文件封装: 6 焊盘 (BQ2970)」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `U_DCDC_VCORE` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「VQFN-16 RGT, 3.00 x 3.00 mm, 带散热焊盘」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `U_DCDC_VIO` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「VQFN-16 RGT, 3.00 x 3.00 mm, 带散热焊盘」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `U_EN_SW` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `U_LDO_IO18` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「X2SON (DQN) 1.0 x 1.0 mm」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `U_LDO_IO33` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「X2SON (DQN) 1.0 x 1.0 mm」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `U_LDO_L18` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「X2SON (DQN) 1.0 x 1.0 mm」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `U_LDO_L33` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「X2SON (DQN) 1.0 x 1.0 mm, 0.4 mm max height, no-lead」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `U_LDO_S12` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「X2SON (DQN) 1.0 x 1.0 mm」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `U_LDO_S18B` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「X2SON (DQN) 1.0 x 1.0 mm」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `U_LDO_S28` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「★板文件封装: 4 焊盘 (GND (pin2))」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `U_PWR_SW` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] |
| `U_SUPV` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「★板文件封装: 4 焊盘 (CT 脚 (阈值/延时选择))」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |
| `U_TEMP` | 缺口-非C4 | **不写** | ★**不需要写**★ | — | 板面已按原厂图纸落了 land (有 courtyard) ⇒ 不是占位; 但本机官方件与板面**几何不等价** (板面 6 焊盘 @0.65mm pitch 无散热焊盘 (TI DRV0006B); 官方 WSON-6-1EP 带 EP ⇒ 9 焊盘; 官方 Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm 实测 9 焊盘 vs 板面 6) ⇒ 写该库名 = 板面铜箔与库件对不上 (假身份) ⇒ 不写; 建议改用 property 'Footprint' 记原厂封装号 (登记·不代拍) | [实测] |
| `X1` | DNP | **不写** | ★**不需要写**★ | — | BOM 记 dnp=DNP ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「★板文件封装: 3 焊盘 (晶振焊盘位 (不装))」⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写 | [实测] |

★**96 件小结 [实测]**: 写 **4** 件 (★全是 `J_SOM_P1~P4`·逐焊盘几何等价·铜箔零改动·旋转 180°★) · 不写 **92** 件 (★TP 42 + DNP 37 + 已落 land 3 + 选型未定 10★)。

### §3.3 ★件数对账 (★90 / 96 / 186 / C4 158 四桶·四行互相加得起来★)

| 口径 | 件数 | 算式 | 谁产出 |
|---|---|---|---|
| 板面封装总数 | **186** | 板面实测 | `tmp/iss369/tools/board_probe.py` |
| ★**本单对象 (表 A)**★ | **90** | ★**靶内 77 + 缺口 13 = 90**★ | `tmp/iss369/tools/buckets.py` (★与 ISS-361 / ISS-364 同口径★) |
| ★**其余 (表 B)**★ | **96** | 186 − 90 = 96 | 同上 |
| C4 占位脚号件数 | **158** | ★**TP 42 + DNP 26 + 靶内 77 + 缺口 13 = 158**★ | `state/check_pcb_nets.py` + ISS-361 四桶 |
| C4 里的豁免件 (TP + DNP) | 68 | 42 + 26 | 同上 |
| 不在 C4 的板面器件 | 28 | 186 − 158 = 28 | 同上 |
| 本单要写库名 | **94** | 90 (表 A) + 4 (表 B 的 `J_SOM_P1~P4`) | 本单实算 |
| 本单不写库名 | **92** | 186 − 94 = 92 | 本单实算 |

★**96 的分桶 (★本单脚本实算·与任务书括注的对账见下★)**:

| 桶 | 件数 | 名单 |
|---|---|---|
| TP | 42 | `TP_BAT` · `TP_BAT_CHG` · `TP_BOOT` · `TP_CSI_CK_N` · `TP_CSI_CK_P` · `TP_CSI_D0_N` · `TP_CSI_D0_P` · `TP_DSI_CK_N` · `TP_DSI_CK_P` · `TP_DSI_D0_N` · `TP_DSI_D0_P` · `TP_DSI_D1_N` · `TP_DSI_D1_P` · `TP_DSI_D2_N` · `TP_DSI_D2_P` · `TP_DSI_D3_N` · `TP_DSI_D3_P` · `TP_FSIN` · `TP_I2CA_SCL` · `TP_I2CA_SDA` · `TP_I2CB_SCL` · `TP_I2CB_SDA` · `TP_ID` · `TP_JTAG` · `TP_KEY_PWR` · `TP_KEY_VM` · `TP_KEY_VP` · `TP_LED_B` · `TP_LED_G` · `TP_LED_R` · `TP_LIGHT_3V3` · `TP_MCLK` · `TP_PG` · `TP_PG_VCORE` · `TP_PG_VIO` · `TP_RESET` · `TP_SYS` · `TP_UART` · `TP_USB_D_N` · `TP_USB_D_P` · `TP_VCORE` · `TP_VIO` |
| DNP | 37 | `BT_432243` · `C_BULK_LIGHT_1V8` · `C_BULK_SENSOR_AVDD` · `C_BULK_SENSOR_CORE` · `C_BULK_SENSOR_VDD_IO` · `C_BULK_V_CORE` · `C_BULK_V_SOC_IO` · `C_HF_LIGHT_1V8` · `C_HF_SENSOR_AVDD` · `C_HF_SENSOR_CORE` · `C_HF_SENSOR_VDD_IO` · `C_HF_V_CORE` · `C_HF_V_SOC_IO` · `C_KEY_CAM` · `C_SUPV` · `C_VBUS_GND` · `C_XTAL_IN` · `C_XTAL_OUT` · `D_ESD_LIGHT` · `D_LED_B` · `J_BOOT1` · `J_UART` · `Q1` · `Q2` · `R_ID_JMP0` · `R_ID_JMP1` · `R_LED_B` · `R_NTC_BAT` · `R_TS_PULL` · `SW_KEY_CAM` · `U_BATPROT` · `U_LDO_L18` · `U_LDO_S12` · `U_LDO_S18B` · `U_LDO_S28` · `U_SUPV` · `X1` |
| 靶内-非C4 | 1 | `J_DEBUG` |
| 缺口-非C4 | 12 | `CONN_LIGHT` · `J_SOM_P2` · `J_SOM_P4` · `J_USB_C` · `U_DCDC_VCORE` · `U_DCDC_VIO` · `U_EN_SW` · `U_LDO_IO18` · `U_LDO_IO33` · `U_LDO_L33` · `U_PWR_SW` · `U_TEMP` |
| 其它 | 4 | `CONN_CAM` · `J_CHG` · `J_SOM_P1` · `J_SOM_P3` |

★**★ 96 与 90 的差在哪 (★任务书要求写清·别另立口径★) ★**:

- ★**90 件 = C4 四桶里的【靶内 77】+【缺口 13】= 158 里要被收口的那 90 个**★ ⇒ 它们是 ★**C4 占位脚号的持有者**★ ⇒ 换 land + 写库名之后, 它们的**铜箔**变、**网表具名**变 (腿 B), ★**但 C4 读数不变**★ (见 §4)。
- ★**96 件 = 186 − 90 = 【C4 里被豁免的 68 件 (TP 42 + DNP 26)】+【不在 C4 的 28 件】**★ ⇒ ★**这 96 件的 C4 Δ 恒为 0 (它们本来就不在 158 名单里)**★ ⇒ ★**写不写库名都动不了 C4**★。
- ★**⇒ 两张表对 C4 的贡献差 = 0**★ ⇒ ★**C4 恒 158, 「写库名」这一腿对 C4 的贡献 = 0**★ (★沙盒五轮实测见 §4.1★)。

★**★ 与任务书括注「TP 42 / DNP 26 / 靶内 22 / 缺口 1」的对账 (★本单如实写清·不改口径★) ★**:

- ★**TP 42** ⇒ 与本单实算【逐件相等】★ (42 个测试焊盘, 一件不多一件不少)。
- ★**DNP 26** ⇒ ★**是【C4 四桶里的 DNP 26】, 与本单实算逐件相等**★; ★**但 96 桶里的 DNP 是 37 件**★ (★= C4 的 DNP 26 + 不在 C4 的 DNP 11★) ⇒ 两个「DNP」的口径不同, ★**本单在表 B 里按【板面 + BOM】分桶写 37, 在本节对账里按【C4 四桶】写 26, 两处都标了口径★★。
- ★**「靶内 22 + 缺口 1 = 23」** ⇒ ★**这不是本板 96 的分桶, 而是【ISS-356 靶子 100 减 C4 158】的差**★: 77 (靶内·在 C4) + **22** (充电板那 22 件·不在本板) + **1** (`J_DEBUG`·在板·不在 C4) = 100 ⇒ ★**那 23 件里的 22 件根本不在本板 186 里, 1 件 (`J_DEBUG`) 在表 B 的「靶内-非C4」桶里**★。
- ★**⇒ 任务书那四个数之和 = 91 ≠ 96**★ ⇒ ★**本单不拿它当件数口径, 一律按【脚本实算】: 90 = 靶内 77 + 缺口 13 (主线, 与 ISS-361 / ISS-364 完全一致) · 96 = 186 − 90**★ ⇒ ★**这条口径差异已列入交卷页「要 main 裁的事」第 1 条**★。

## §4 ★「写库名会不会改语义」的判定 (★沙盒实测 · C1/C2/C3/C4 逐条★)

### §4.0 两张表的件数对账摘要 (★任务书要求的 §4 两张表口径, 与 §3.3 同源★)

| 表 | 件数 | 对 C4 的贡献 |
|---|---|---|
| §3.1 表 A (90 件) | **90** | ★**ΔC4 = 0**★ (★腿 A 换 land 实测 Δ0·写库名实测 Δ0★) |
| §3.2 表 B (96 件) | **96** | ★**ΔC4 = 0**★ (★这 96 件本就不在 C4 的 158 名单里★) |
| ★**合计**★ | **186** | ★**ΔC4 = 0 ⇒ C4 恒 158**★ |

### §4.1 沙盒五轮 (★真闸 `state/check_pcb_nets.py` 的真代码给出★)

| 轮次 | 板副本 | rc | C1 | C2 | C3 | ★**C4**★ | 库名非空 |
|---|---|---|---|---|---|---|---|
| ★**S0 基线** (真板 + 真网表) | `HW/PCB/demo_mainboard.kicad_pcb (★真板★)` | 1 | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482 | ✅ C2 U_TEMP: 板 6 脚 / 网表 6 脚 | ✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个 | ★**158**★ | 0 / 186 |
| ★**S1** 换 90 件 land, ★**不写库名**★ | `tmp/iss369/sbx/board_legA_only.kicad_pcb` | 1 | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 486 | ✅ C2 U_TEMP: 板 6 脚 / 网表 6 脚 | ❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 7 个 | ★**158**★ | 0 / 186 |
| ★**S2** 换 90 件 land + ★**同时写 94 件库名**★ | `tmp/iss369/sbx/board_legA_plus_libid.kicad_pcb` | 1 | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 486 | ✅ C2 U_TEMP: 板 6 脚 / 网表 6 脚 | ❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 7 个 | ★**158**★ | 94 / 186 |
| ★**S3** ★**只写库名, 零几何改动**★ | `tmp/iss369/sbx/board_libid_only.kicad_pcb` | 1 | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482 | ✅ C2 U_TEMP: 板 6 脚 / 网表 6 脚 | ✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个 | ★**158**★ | 94 / 186 |
| ★**S4** 反向对照: 写 90 件库名, ★**不换 land**★ | `tmp/iss369/sbx/board_libid_no_landswap.kicad_pcb` | 1 | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482 | ✅ C2 U_TEMP: 板 6 脚 / 网表 6 脚 | ✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个 | ★**158**★ | 90 / 186 |

★**逐条判定 (★结论★)**:

| 判据 | 写库名对它的影响 | 依据 |
|---|---|---|
| ★**C1** (焊盘级等价: ref+焊盘号 → 网络) | ★**Δ = 0**★ ⇒ ★**S1 与 S2 的 C1 读数逐字相同**★ (★S1 与 S2 只差 `lib_id` 那一行★) | 沙盒 S1 vs S2 |
| ★**C2** (U_TEMP 脚数) | ★**Δ = 0**★ ⇒ 五轮全 ✅ | 沙盒五轮 |
| ★**C3** (器件焊盘数 == 网表推出的脚数) | ★**Δ = 0**★ ⇒ ★**S1 与 S2 的 C3 读数逐字相同**★ (★S1 与 S2 只差 `lib_id` 那一行★); ★**但「换 land」这一腿本身会把 C3 弄红 7 件**★ | 沙盒 S1 vs S2 + S0 vs S3 |
| ★**C4** (占位脚号器件数) | ★**Δ = 0**★ ⇒ ★**五轮 C4 全部 = 158**★ ⇒ ★**写库名这一腿对 C4 的贡献 = 0**★ | 沙盒五轮 |

★**★ 关键结论 (★这是本单要证明的那一条★) ★**:

> ★**「换 land」与「写库名」是同一件事的两半。**★
> ★**- 腿 A (换官方 land): 沙盒 S1 实测 ΔC4 = 0, ΔC3 = −7 件 (7 件焊盘数变了), ΔC1 不变**★
> ★**- 腿 B (网表节点具名): 那才是让 C4 从 158 变 68 的那一腿 (ISS-364 实测 ΔC4 = −90)**★
> ★**- 本单的「写库名」这一腿: S0→S3 / S1→S2 / S0→S4 三组对照, C1/C2/C3/C4 读数逐字不变 ⇒ ΔC4 = 0**★
> ★**⇒ 「写库名」不改变电气语义; 它只补【身份】, 让装配厂/BOM 对得上板面**★
> ★**⇒ ★**别把「换 land 会让 C4 降下来」当预期**★ —— ★**C4 = 158 是写库名这一腿跑完之后的正确读数**★ (★与 ISS-361 实测的「腿 A 对 C4 贡献 = 0」一致★)

### §4.2 字节级证据 (★写库名只改一行★)

| 对照 | A md5 | B md5 | 加/删行数 | ★**差分行全部是封装节点名行**★ |
|---|---|---|---|---|
| S0_vs_S3_只写库名 | `611b869e13518c3c` | `a50049032e3b1911` | +94 / −94 | ★**是**★ |
| S1_vs_S2_换land加库名 | `0bb30c2642a1cab3` | `f49cf5cbe1ced840` | +94 / −94 | ★**是**★ |
| S0_vs_S4_反向对照 | `611b869e13518c3c` | `37e3e4a0a16297cb` | +90 / −90 | ★**是**★ |

★**⇒ 只写库名 (S0→S3) 的 94 个加行与 94 个删行, 逐行都是 `(footprint "…")` 那一行 ⇒ 焊盘/走线/铜皮/net/uuid 一个字节都没动**★。

### §4.3 写库名【本身】会不会改 C1/C2/C3/C4 —— 逐条结论

- ★**C1**: 板面每个焊盘的 (ref, 焊盘号) → net 归属, ★**写库名一个字节都不改焊盘与 net**★ ⇒ ★**C1 不可能因为写库名而变**★ (★S1/S2 对照实测逐字相同★)。
- ★**C2**: U_TEMP 脚数, 同上 ⇒ 不变。
- ★**C3**: 器件焊盘数 vs 网表推出的脚数, 同上 ⇒ 不变 (★C3 在 S1/S2 里红是因为【换 land】改了焊盘数, 不是因为写库名★)。
- ★**C4**: 网表节点串是不是 bare, ★**完全由 `HW/netlist_v1.csv` 决定, 板在它之后才被读**★ ⇒ 写库名 ⇒ ★**C4 恒 158**★。

## §5 未决项 (★只登记 · 给代价 · 给会红哪道闸 · 不代老板拍板★)

| # | 未决项 | 分叉 | 代价 | 会红哪道闸 | 本单的处理 | 证据 |
|---|---|---|---|---|---|---|
| W-1 | ★`D_ESD_USB_D` 最终 2 脚还是 3 脚★ | (a) 2 脚 (b) 3 脚 | (b) ⇒ 板面多一个焊盘 + 走线重画 + 该 net 要重接 | ★**C3** (焊盘数 != 网表脚数) + **C1** (焊盘级等价)★ | ★**本单按 ISS-364 台账的 2 脚件 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 写目标; 板面现状也是 2 脚 ⇒ Δ焊盘数 = 0; 若改走 3 脚 ⇒ 须重跑本表与 §4 沙盒**★ | [实测]+[推算] |
| W-2 | ★5 只按键 (`SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST`) 的 2 脚 vs 4 焊盘★ | (a) 2 脚 (只焊两脚) (b) 4 焊盘 (按官方 `SW_Push_1P1T_NO_CK_KMR2` 含 2 个机械焊盘) | (b) ⇒ 板面每只多 2 个焊盘 + 孔位/丝印要复核 + 装配要多压 2 个脚 | ★**C3** (7 件里 3 只是按键) + **C1**★ | ★**本单按 ISS-364 台账的 4 焊盘件写目标; 板面现状 2 脚 ⇒ Δ焊盘数 = +2; 若老板定 2 脚 ⇒ 目标件要换, 几何 Δ 要重算**★ | [实测]+[推算] |
| W-3 | ★`C_VBUS_GND` 留位还是下板★ | (a) 留位 (b) 下板 | (a) ⇒ 板面多 2 个空焊盘, 但 BOM 与板面对不上 (★C1 现在就报「多 2」★) (b) ⇒ 板 md5 再变一次 (★与「板只改一次」冲突★) | ★**C1** (多 2 个焊盘)★ | ★**本单: 不写库名** (BOM 记 dnp=DNP 且 footprint 栏 = 待定 ⇒ 写库名 = 替老板拍板) ⇒ ★**登记 + 给代价, 等老板定**★ | [实测] |
| W-4 | ★`J_SOM_P1~P4` 写哪个 DF40 变体★ | (a) `Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` (b) `Hirose_DF40HC(3.0)-100DS-0.4V_2x50_P0.4mm` | ★**两个变体的焊盘几何逐件等价 (实测 Δpad = 0.000 mm, 旋转 180°) ⇒ 选哪个都不改铜箔**★; 差别在【壳体高度 3.0 mm 的 HC 版本】⇒ ★**是结构高度问题, 不是电气问题**★ | ★**本单两个闸都不红**★ (几何等价) ⇒ ★**选型 = 老板拍板**★ | ★**本单写 (a) 并登记 (b) 为等效候选; 若改写 (b) ⇒ 板面铜箔零改动, 只改 `lib_id` 那一行**★ | [实测]+[推算] |
| W-5 | ★`U_TEMP` / `CONN_LIGHT` / `J_USB_C` 三件已落 land 的封装身份怎么记★ | (a) 写官方库名 (b) 用 `property "Footprint"` 记原厂封装号 | (a) ⇒ ★**假身份** (★官方件与板面几何不等价: `U_TEMP` 6 脚 vs 官方 9 脚 (带散热焊盘) · `CONN_LIGHT` 22 脚 vs 官方 24 脚 (带 2 个固定柱) · `J_USB_C` 18 脚 vs 官方 22 脚 (带 2 个 Ø0.65 壳体固定孔 + 接地焊盘)★) (b) ⇒ 板面零改动, 装配厂照原厂封装号取件 | ★**本单新建的闸不判这三件**★ | ★**本单: 不写库名, 登记「用 `property \"Footprint\"` 记原厂封装号」的建议 (不代拍)**★ | [实测] |

## §6 复跑命令 + 本单的边界

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ★§0 的读数逐条复跑★
python3 tmp/iss369/tools/parse_board.py          # 板面 186 封装纯文本解析
bash state/pcbnew_py.sh tmp/iss369/tools/board_probe.py   # 库名 0/186 非空 (GetFPIDAsString)
python3 tmp/iss369/tools/buckets.py              # 90 / 96 分桶 + C4 四桶
python3 tmp/iss369/tools/verify_targets.py       # ★94 个目标 .kicad_mod 逐个 test -f + md5★
python3 tmp/iss369/tools/padeq_rot_np.py          # 全库 15468 件逐焊盘几何等价穷举
bash state/pcbnew_py.sh tmp/iss369/tools/mech_probe2.py   # §2 写盘机制 E4~E9
bash state/pcbnew_py.sh tmp/iss369/tools/sandbox_libid.py # ★§4 沙盒五轮 C1~C4★
python3 tmp/iss369/tools/sandbox_diff.py         # §4.2 字节级差分

# ★本单新建的机器闸★
python3 HW/check_fp_libid_truth.py               # 正常跑 ⇒ rc=0
python3 HW/check_fp_libid_truth.py --selftest    # 反向用例 ⇒ rc=0

# ★板面逐封装判定 (那一趟换完 land + 写完库名之后, main 用这条验收)★
python3 HW/check_fp_libid_truth.py --mode board --board tmp/iss369/sbx/board_legA_plus_libid.kicad_pcb
```

★**本单的边界 (★逐条自证·交卷页 §B5 有逐条双证★)**:

| 边界 | 自证方式 |
|---|---|
| ★**零写板**★ | 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B, 开工前 = 交卷后 |
| ★**零落表**★ | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` md5 开工前 = 交卷后 |
| ★**零改既有闸**★ | `HW/check_fp_truth_baseline.py` · `HW/check_fp_truth_coverage_gap.py` · `HW/check_fp_truth_land_swap.py` · `HW/check_onepass_preflight_coverage.py` · `HW/check_onepass_s10_manifest.py` · `state/check_pcb_nets.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一个字节未改 |
| ★**零改既有页面**★ | `HW/FP_TRUTH_BASELINE.md` · `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` · `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `state/board_trip_baseline_20260723.txt` 老字未改 |
| ★**零挂链**★ | 本单的新闸 ★**没有**挂进 `state/gate_check.py` (★挂链是 main 的地界·本单只交脚本与路径 + 建议★) |
| ★**零外发 / 零采购**★ | 本单没有任何出网请求; 查不到的部分一律写降级方案 |
| ★**不代老板拍板**★ | §5 的 5 条全部是「登记 + 给代价 + 给会红哪道闸」; 未决项一条没替老板定 |
| ★**只写自己的分片**★ | 只写 `state/fragments/hw.yaml`, 只走 `state/frag_write.py` |
| ★**不自签 `state/issue_log.yaml`**★ | 一个字没动 |
| ★**沙盒只落 `tmp/iss369/` + `logs/iss369/`**★ | 沙盒板副本在 `tmp/iss369/sbx/`; 留证在 `logs/iss369/` |

## §7 ★回滚说明 (★沙盒怎么复原 · 真件零改动怎么自证★)

| 对象 | 怎么复原 | 自证命令 |
|---|---|---|
| ★**真板** ★`HW/PCB/demo_mainboard.kicad_pcb`★ | ★**本单从未写过它 ⇒ 无需复原**★ (★所有写盘动作都发生在 `tmp/iss369/sbx/` 的副本上★) | ★**`md5sum HW/PCB/demo_mainboard.kicad_pcb`** ⇒ 必须仍是 `611b869e13518c3c023fb178f91a0075`; ★**`stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb`** ⇒ 必须仍是 `2026-11-06 07:07:17.362193413` / `4940213`★ |
| ★**沙盒板副本** (4 个)★ | ★**删掉 `tmp/iss369/sbx/` 整个目录即可复原**★ (★它们只被读·从未被当真件★); 要重跑沙盒: `bash state/pcbnew_py.sh tmp/iss369/tools/sandbox_libid.py` ★(会重新生成这 4 个副本 + 两份留证 json)★ | `ls -l tmp/iss369/sbx/` + `md5sum tmp/iss369/sbx/*.kicad_pcb` (★副本的 md5 与真板不同是正常的·它们就是变更后的板★) |
| ★**留证** `logs/iss369/`★ | 只增不改 ⇒ 无需回滚; 若要重跑某一项, 按 §6 的命令重跑并覆盖同名文件 | `ls -l logs/iss369/` |
| ★**本单新建的页** `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md`★ | ★**整页删掉即可**★ (★它是纯新建文件·不覆写任何既有页★); 要重建: `python3 logs/iss369/build_fp_libid_workpacket.py` | `md5sum HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` |
| ★**本单新建的闸** `HW/check_fp_libid_truth.py`★ | ★**删掉即可**★ (★★它【没有】挂进 `state/gate_check.py` ⇒ 删了不会影响既有门禁链★★) | `grep -c check_fp_libid_truth state/gate_check.py` ⇒ 必须 = **0** |
| ★**分片** `state/fragments/hw.yaml`★ | 用 `state/frag_write.py` 把本单新增的条目删掉 (★只走原子写★); 本单只新增·未改既有条目 ⇒ 删掉新增条目即回到开工前状态 | `md5sum state/fragments/hw.yaml` (★开工前 = `8305a9b2c3240ca2c9b4b2cb659971fe`·见交卷页 §B5★) |

★**★ 真件零改动的总自证 (★一行命令·交卷页 §B5 贴原样输出★) ★**:

```bash
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
```

