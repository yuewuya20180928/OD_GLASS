# ROUND_LOG_main · 2026-11-24 13:1x · ISS-387 / ISS-389 两单独立复核签收 + 11 条 main 地界待裁项已裁 + ISS-391 按 L-27 不签

★**job**: main (ARS45 项目总工) · webchat 会话 (★由兄弟 job 5bd48f25 的进展播报触发★)
★**签收闸**: `state/_apply_20260724_1310_main_sign_iss387_389.py` (★fail-closed★)
★**备份** (★脚本现场取 `time.strftime` ⇒ 真实 stamp `20261124_1310`★): `state/issue_log.yaml.bak_20261124_1310_main_sign_iss387_389` ·
`DECISION_ONE_PAGER_2026-11-22.md.bak_20261124_1310_main_sign_iss387_389` · `state/LESSONS.md.bak_20261124_1310_main_l29` ·
`MEMORY.md.bak_20261124_1310_main_l29_pointer`

---

## ★★一 · 板面 (本机实读) ★★

★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` (纳秒级) ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

---

## ★★二 · 两单签收 (main 本机独立复核·不抄 agent 报告) ★★

| 单 | owner | 闸 | 裸跑 | `--selftest` | 交付物 |
|---|---|---|---|---|---|
| ISS-387 | hw-lead | `HW/check_fts_single_row_land_truth.py` | rc=0 | rc=0 `ALL TESTS PASS` | 真相页 50,714 B + 交卷页 26,363 B |
| ISS-389 | mech-lead | `MECH/check_debug_seat_rework_spec.py` | rc=0 | rc=0 `ALL TESTS PASS` | 真相页 65,851 B + 交卷页 40,225 B |

★两闸连跑 3 次末行逐字相同 · 两闸零挂链 · 零落表 · 零改既有页面正文 ★

---

## ★★三 · ★★main 本机独立复核: ISS-387 的核心数字自己算 (不抄页面) ★★

```
★自己解析 PinHeader_1x04_P1.27mm_Vertical.kicad_mod:
  pads=4 / drill=0.65 / 焊盘 1.000×1.000 / 沿脚排 y = 0, 1.27, 2.54, 3.81
  ⇒ 铜箔沿脚排总宽 = 3.810 + 1.000 = 4.8100                          ✓
★自己解析 PinHeader_1x02_P1.27mm_Vertical.kicad_mod:
  pads=2 / drill=0.65
  ⇒ 铜箔沿脚排总宽 = 1.270 + 1.000 = 2.2700                          ✓
⇒ MECH 全链 3D 余量数的输入本机复算逐字命中
⇒ 「孔径 0.65→0.71 不动铜箔包络 ⇒ MECH 七个数一个都不用改」成立
```

---

## ★★四 · ★★main 自己的发现 (ISS-387 与 ISS-391 两页都没算这一格) ★★

★**官方 `Ø0.71` 配通用件 `1.000×1.000` 焊盘 ⇒ 环宽 (annular ring) 从 `0.1750` 降到 `0.1450` mm** ★
★**本板 `.kicad_pro` 的 DRC 规则表里与环宽相关的只有 `min_via_annular_width 0.1` (过孔环宽) ⇒ THT 焊盘环宽【无独立判据】⇒ 0.145 触不到板 DRC** ⇒
★**⇒ 它是【制程能力】问题, 不是 DRC 问题** ⇒ ★**全仓 (HW/ MECH/ state/) 实查: 没有任何一处记录本板厂的最小环宽/工艺能力** ⇒
★**⇒ 「0.145 能不能做」当前【无据可判】⇒ 那一趟投板前必须坐实, 否则投完板才发现 ⇒ 板改第二次** ⇒ 已登记 `iss387_main_rilim_ring_width_fab_capability` ★

---

## ★★五 · ★★11 条 main 地界待裁项已裁 (一件没代老板拍板) ★★

★**A 组 · ISS-387 (4 条)**: A1 焊盘维持 `1.000×1.000` (★附前置条件 = 环宽先过制程确认★) · A2 改孔与那一趟同批 · A3 用通用件 land + BOM 等价替代 + 显式偏离登记 (★官方直插图不给铜箔焊盘直径 ⇒ 「原厂铜箔宽」根本没数★) · A4 座体外形走双轨降级 (甲 官网量 / 乙 1 台样件实测) ⇒ 归 mech-lead, 与那一趟同批

★**C 组 · ISS-389 (7 条)**: C1 OI-2 含 `J_UART` (★「不含 ⇒ 零返工」是假选项: 实物仍装不上★) · C2 OI-3 不重开落点, 但把顺序钉死 (老板答板框 → 落点 → 结构件 → 板改+布线+Gerber) · C3 OI-5 取 `4.8100` (★本轮与 ISS-387 闭合★) · C4 OI-12 路 A (★路 B 已可判死: `6.0100` < courtyard `6.0900` + 公差不扣★) · C5 OI-13 路 B (开口 Y `≥ 5.6000` 或 `5.8000`) · C6 OI-14 订正为 `4.0700` (★与 OI-12 同源, 一起拍★) · C7 OI-1 已被 C3/C4/C6 闭合 ⇒ 从「待拍板」降级为「执行口径」⇒ 不再依赖板框第一问

★**老板域 (未代拍)**: OI-1 (已实质闭合) · OI-11 座体真实高 `h` (★X 向与 h 无关 ⇒ 不卡那一趟; 若定 `4.0000` ⇒ 开口 Y `5.8000` ⇒ 与 C5 同一处改动★)

---

## ★★六 · ★★ISS-391 本轮【不签收】(L-27 判据) ★★

★**owner 会话还在跑**: 真相页 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` 12:49:22 仍被改 (hw-lead 会话 12:50 仍 running) ⇒ ★**此时签 ⇒ 签收指纹当场过期 (今天已在 ISS-381/382/384 上栽过一次)** ⇒ 等 owner 收工后再签 ★
★**交付物本身无缺陷**: 新闸裸跑 rc=1 而 `--selftest` rc=0 末行 `ALL TESTS PASS` ⇒ ★**这个 rc=1 是【闸按设计判红】**: D1/D2/D3 抓的正是「`钻孔 0.65→0.71` 还没进作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」⇒ ⇒ **这道闸必须留在零挂链状态: 挂进去 = 假红** ⇒ 挂链时机 = 与 §4 登记同批 (★L-29★) ★

---

## ★★七 · 落记录 (全部追加式·老字一字未删) ★★

★`state/issue_log.yaml` (ISS-387/389 签收 + ISS-391 不签留痕) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊶** · `state/LESSONS.md` **L-29** · `state/fragments/pm.yaml` (13 条答案) · `MEMORY.md` (L-29 指针)

---

## ★★八 · 最终读数 (本机实跑) ★★

★板三项未动 · 网表/脚表/BOM/`gate_check.py`/`merge.py`/`frag_write.py`/五个已签收页逐字节未动 · 两个新闸 rc=0 · 11 道扫描面闸全 rc=0 ·
`merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=1 (19 条既有逾期老账) · `stage_gate.py` rc=1 (G1 仍开, 按设计就该红) ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 未代老板拍板** ★


---

## ★★九 · ★★订正节 (★2026-11-24 14:2x main 本机复核 · 追加式 · ★上面第八节之前的文字一个字未删★) ★★

★**★① 章节号撞号 (★我 13:1x 那一轮的自伤★)★**
★**实况**: 一页 `DECISION_ONE_PAGER_2026-11-22.md` 上出现**两个** `## ★★㊶` ⇒ ★**行 1318 = 兄弟 job fb67af40 于 10:2x 写的 (在先) · 行 1420 = 我 13:1x 写的 (在后)** ★
★**根因**: ★**13:1x 那一轮落盘前【没有扫已用章节号】⇒ 直接取「下一个号」⇒ 撞上了兄弟 job 半小时前刚写的那个号** ⇒ ★**⇒ 与 L-28 (幂等 key 撞名必须报错退出) 同族: 【取号/取 key 这类操作, 必须先查重】** ★
★**★处置 (★追加式·★兄弟 job 那段一个字未动★)★**: ★**① 我那一段改号为 `§㊷` (★`㊷` 全页未用·★实读确认 0 命中★) ⇒ ② 标题行下方就地插一行订正说明 (老字一字未删) ⇒ "
③ 段内全部「§㊶」自指同步改为「§㊷」 (★★本轮实读: 段内正文自指 = 0 处·★实际只改了标题行 + pm.yaml 的 15 条 ref★) ⇒ ④ `state/fragments/pm.yaml` 里本轮 15 条答案的 `ref` 字段中的「§㊶」同步改为「§㊷」** ★
★**★⇒ 兄弟 job 那一段 `§㊶` (10:2x) 的内容是「队列真空 → 槽位被占」的根因订正, 与我这一段 (ISS-387/389 签收 + 11 条待裁项) 【互不引用·互不覆盖】⇒ 两段都有效** ★
★**★⇒ 已登记为 LESSONS **L-30** (★main 独占写★)** ★ ★

★**★② 备份 stamp 写错 (★第八节第 5~7 行★)★**
★**老字写的是**: `★备份★ (★脚本现场取 time.strftime ⇒ 真实 stamp 20261124_1310★)` ⇒ ★**★实盘是 `20261124_1300`** (★脚本用 `time.strftime` 现场取·★是我写 round log 时手打了 1310★) ⇒
★**★⇒ 实盘三个备份的真实文件名 (★逐个 ls 确认★)★**: `state/issue_log.yaml.bak_20261124_1300_main_sign_iss387_389` · `DECISION_ONE_PAGER_2026-11-22.md.bak_20261124_1300_main_sign_iss387_389` · `state/LESSONS.md.bak_20261124_1300_main_l29` · ★**`MEMORY.md.bak_20261124_1300_main_l29_pointer`** ★
★**⇒ 另注: 一页的备份是 11:23:51 那一份 (`…_20261124_1300_…` 之前另有 11:23 的旧备份) ⇒ ★**本轮改号用的新备份 = `…_bak_20261124_1420_main_secnum_fix`** ★ ★

★**★③ pm.yaml 条数写错 (★第七节末行★)★**
★**老字写的是**: `state/fragments/pm.yaml (13 条答案)` ⇒ ★**★实盘 = 15 条** (★137 → 152★) ⇒ ★**明细 (★15 条全列, 供对账★)★**:
★`iss387_main_rilim_ring_width_fab_capability` (待补项) · `iss387_main_oi1_pad_1x1_maintained` · `iss387_main_oi2_drill_change_same_batch` · `iss387_main_oi3_footprint_source_generic_plus_deviation` · `iss387_main_oi4_seat_outline_two_track` ·
★`iss389_main_oi2_scope_includes_juart` · `iss389_main_oi3_landing_order` · `iss389_main_oi5_pick_4810` · `iss389_main_oi12_criterion_stays_route_a` · `iss389_main_oi13_open_y_enlarge` · `iss389_main_oi14_dp1_correction_4070` · `iss389_main_oi1_formal_confirm_4070` ·
★`iss391_main_gap_registration_same_batch` · `iss391_main_gate_hook_with_registration` · `main_owner_must_freeze_deliverables_after_handoff` ★
★**⇒ 与「11 条 main 地界待裁项」的关系 (★两数不同, 不是矛盾★)★**: ★**「11 条」= ISS-387 的 4 条 (OI-1~4) + ISS-389 的 7 条 (OI-2/3/5/12/13/14 + OI-1) ⇒ 这是【题面】的 11 条** ⇒ "
★**「15 条」= 11 条题面裁决 + 3 条 main 自立项 (① 环宽/制程能力待补项 ② ISS-391 §4 三处登记的落法 ③ ISS-391 新闸的挂链时机) + 1 条跨单通用纪律 (交卷后冻结交付物) ⇒ 这是【落表条数】** ⇒ ⇒ **两个数都对, 但老字没写清关系, 已在此补明** ★ ★

★**★④ 本轮订正自身也守纪律 (★自曝★)★**: ★**零写板 (板三项未动) · 零落表 · 零改既有闸 · 零改兄弟 job 的页面正文 (★只动我自己刚写的标题行与自指★) · 零外发 · 未代老板拍板** ★
