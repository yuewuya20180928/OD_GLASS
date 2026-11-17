# `state/_iss277_build_preflight.py` · 清单页生成器维护说明 (★ISS-292 · 2026-11-17·hw-lead★)

> ★**一句话**: ★**这个脚本生成「板只改一次」那一趟的板侧项全集页 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`** ★
> ★**2026-11-17 之前它比盘面页旧 ⇒ 谁跑一次谁把 ISS-283 / ISS-289 的订正全冲掉 ⇒ ISS-292 把它与盘面页对齐 (★重跑幂等·页零变化★)** ★

---

## ★① 输入 / 输出 / 真源 (★三件套★)

| # | 角色 | 件 | 说明 |
|---|---|---|---|
| ★1 ★ | ★**输出** ★ | ★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ | ★**本脚本只写这一个文件** (★零写板 · 零落表 · 不碰网表/脚表/BOM ★) ★ |
| ★2 ★ | ★**输入 (代码内)** ★ | ★**本脚本里的 `ITEMS_RAW` 表** ★ | ★**32 条板侧项 · 每条固定 9 个字段** (`id` / `source_iss` / `title` / `current_state` / `action` / `criterion` / `step` / `blocked_by` / `evidence`) ⇒ §2 表格行与 §7 JSON 条目由它同源生成 ★ |
| ★3 ★ | ★**输入 (sidecar)** ★ | ★**`state/_iss277_preflight_appendix.md`** ★ | ★**两块【追加式订正块】**: ① `ISS292:S3_APPENDIX` (★ISS-283 落表带来的 §③-1~§③-3 三条·插在 §3 末尾★) ② `ISS292:ISS289_APPENDIX` (★ISS-289 的 §附录 + `state_baseline` 登记表·追加在页尾★) ⇒ ★**本脚本只搬运, 一个字都不改 ★** ★ |
| ★4 ★ | ★**输入 (真源读数)** ★ | ★**见下面 §②** ★ | ★**现状值一律从真源读, 一律不许写死** ★ |

★**★⇒ 生成器自己 + sidecar + 真源 = 三件套; 缺任何一件都不许写页 (★fail-closed★)★★ ★**

---

## ★② 真源清单 (★读什么 · 从哪读 · 干什么用 · 读不到怎么办★)

| 读数 | 真源 (★本机实跑★) | 干什么用 | 读不到怎么办 |
|---|---|---|---|
| ★**R3-A4 三个数** (★`MAIN_PCB且DNP` / `在板上` / `零标记`★) | ★`python3 HW/check_netlist_contradiction_r3.py` ★ | ★`B17_DNP_43` 的 `current_state` (★★不许写死 51/40/40★★) ★ | ★**拒写页 (rc≠0)** ★ |
| ★**脚表缺陷条数** (★总数 / 功能缺陷 / 串号 / 缺脚 / md5 台账对账★) | ★`python3 HW/check_pin_function_labels.py` ★ | ★`B03_ULDO_S28_PAD3` 的 `current_state` + `criterion` (★★不许写死 18 / 15 / 14 / 1 / 3★★) ★ | ★**拒写页 (rc≠0)** ★ |
| ★**最近一次「删了 N 行 DNP」的落表事件** (★时间 / V 标签 / N★) | ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md`** (★每条落表链的「落表时间」+ 拍板表里「删 DEMO_DNP N 行」★) ★ | ★`B17_DNP_43` 的落表事件注记 (★「54/43/43 → 51/40/40」那一句★) ⇒ ★**注记里的历史数也是算出来的 (★`落表后 = 落表前 − N`★), 不是写死的** ★ | ★**降级成中性注记 + 打印告警** (★fail-soft: 页照写, 但那一行不再带历史数★) ★ |
| ★**ISS-289 那批的脚表功能缺陷基线** | ★**sidecar 的 `state_baseline` 登记表 (`C06_B03_DEFECT_COUNT` 的 `anchor`) ★** | ★判断「脚表功能缺陷本批未变」这句注记还成不成立 (★变了就换成「本批已变」★) ★ | ★**注记降级成中性措辞** ★ |

★**★为什么状态类读数全部走【闸的输出】而不是自己重算★**: ★**自己重算一套 = 与闸脱钩 = 文档与闸各说各话 = 同一个病的第八个变体★★ ⇒ ★**一律读闸的原始输出, 闸改了就跟着改 ★** ★

---

## ★③ 三条铁律 (★改这个脚本时一条都不许破★)

1. ★**现状值一律从真源读, 一律不许写死** ★ ⇒ 写死在代码里的现状数字 = 下次落表就过期 = 页回退 = 新闸当场红
2. ★**追加式订正块不许被重跑冲掉** ★ ⇒ §③-1~§③-3 与 §附录 + `state_baseline` 登记表一律走 sidecar (★只搬运★) ⇒ ★**sidecar 缺失 ⇒ 脚本拒写页 (fail-closed) ★**
3. ★**页与 JSON 同源** ★ ⇒ §2 表格行与 §7 JSON 条目由同一份 `ITEMS_RAW` 生成
   - ★**唯一的例外**: `TABLE_ROW_OVERRIDES` 里那 3 行 (★`B32_V2_NET_RENAME` / `B11_Q_PG_LAND` / `B30_LED_BRIGHTNESS`★) —— ★**这 3 行的表格文字与 JSON 字段的 `★` 排版位置不同 (★ISS-283 手工订正的痕迹★) ⇒ 表格行按盘上原样保留 (★老字一字未删★), JSON 按字段生成** ★

---

## ★④ 怎么跑 / 怎么自证幂等★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★跑一次 (★只写清单页一个文件★)
python3 state/_iss277_build_preflight.py

# ★★幂等自检 (★本单的核心验收·★跑前后页必须逐字节相同★)★★
md5sum HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/PCB/BOARD_ONEPASS_WORKPACKET.md
python3 state/_iss277_build_preflight.py
md5sum HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/PCB/BOARD_ONEPASS_WORKPACKET.md
# ★期望: 两个 md5 跑前跑后【逐字节相同】★★

# ★★机器闸 (★现状值漂移当场红★)★★
python3 HW/check_workpack_state_values.py        ; echo "rc=$?"   # 期望 rc=0
python3 HW/check_onepass_preflight_coverage.py    ; echo "rc=$?"   # 期望 rc=0
```

★**★沙盒跑法 (★反向用例要用·★真盘零写★)★★**: `PREFLIGHT_PROJ=<沙盒根> python3 state/_iss277_build_preflight.py`
★**★⇒ 沙盒根里必须有**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `HW/check_netlist_contradiction_r3.py` / `HW/check_pin_function_labels.py` / `HW/SCHEMATIC_LANDING_V1_LANDED.md` / `state/_iss277_build_preflight.py` / `state/_iss277_preflight_appendix.md` ★

---

## ★⑤ 反向用例怎么跑★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 tmp/iss292/reverse_tests.py      # ★4 条全过才 rc=0★
```

★**★四条用例在证明什么 (★别删★)** ★
| # | 构造 | 期望 | 证明的是 |
|---|---|---|---|
| ① | ★沙盒里模拟又一次合法落表 (★台账链头前跳 + DNP 集合改一行★) ★ | ★R3-A4 跟着变 (★51/40/40 ⇒ 50/39/39★) ★ | ★**现状值真源读·不是写死** ★ |
| ② | ★把生成器的 R3-A4 改回写死 54/43/43 ★ | ★页回退 + 新闸 rc=1 (★V2 红★) ★ | ★**闸真在读页 (★不是摆设★)** ★ |
| ③ | ★正向对照 ★ | ★页零变化 + 新闸 rc=0 ★ | ★**幂等** ★ |
| ④ | ★sidecar 缺失 ★ | ★生成器拒写 (★rc≠0 · 页一个字节没动★) ★ | ★**追加式订正块丢不了** ★ |

---

## ★⑥ 维护时最容易踩的三个坑★

1. ★**改了 `ITEMS_RAW` 里的现状值措辞 ⇒ 闸 V2 (追加式自证) 会红** ★ ⇒ ★**现状值型措辞不许手改, 让脚本从真源算; 真要改措辞 = 走【追加式订正】(★在 sidecar 后面加, 老字不许删★)★★ ★
2. ★**改了 sidecar 里 `state_baseline.entries[].expect` 的值 ⇒ 必须【两份文档同时改】★★ ⇒ 清单页那份在 sidecar, 作业包那份在 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §8.2.5 ⇒ ★**两份必须逐字一致 (★闸 V1 判这个★)** ★
3. ★**动板那一趟收工后, 有一批期望值必然变红 (★那是【现状值漂了】, 不是【板改坏了】★)** ⇒ ★**重锚步骤已经写进作业包 §8.3.2 的收工清单 (★强制项 F-1~F-4★) ⇒ 照它做, 尤其: ★★不许为了让闸绿而把 `C_VBUS_GND` 装回板上★★ ★**

---

## ★⑦ 本文件的边界 (★与交卷单一致★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**只写清单页一个文件** · ★**零外发** · ★**不替老板拍板** (★`C_VBUS_GND` 留不留 = 老板/PM 域★) ★
★**交卷单**: `HANDOFF/2026-11-17_hw-lead_ISS292_清单页生成器对齐.md` ★
