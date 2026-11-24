# ISS-387 · hw-lead · 「板只改一次」那一趟的 `J_DEBUG` / `J_UART` 单排直插**原厂 land 几何官网查证** + 与盘上通用封装逐项对比 + 对 MECH 3D 判据链的传感到影响面

★**本单性质**: ★**纯查证 + 纯分析 + 新建文档/闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

---

## ★★一 · 为什么是这一单 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**① 决策页已经【改写】了 A2 的默认建议, 但【那条改写自己开的口子】至今没人补★**
★`DECISION_ONE_PAGER_2026-11-22.md` §㊳ 的 **发现二** (★main 2026-11-24 08:3x 签收 ISS-383 时独立复核推翻 ISS-383 §0-2「两家的 1.27 mm 都没有单排」★) ⇒ ★**Samtec 【FTS】系列有单排直插 1.27mm**: `FTS-104-01-F-S` (4 位 1 排 直插) / `FTS-102-01-F-S` (2 位 1 排 直插) (★Mouser + DigiKey 参数表双源 + Samtec 官网 FTS 家族页「FTS - .050" (1,27mm) Low Profile, .016" (.41mm) Square Post Terminal Strip, **Single Row**」★) ⇒ ★**板侧真值档 (1×4 单排直插) 有现成可采购件** ★
★★ ★**但同一条 §㊳ A2 自己写了三个不许跳过的字** ★★:
```
★**但铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认** (★FTS 的 post 是 .016″ (.41mm) 方柱,
与 FTSH 的 .41 mm 不同族, **不许拿 FTSH 的铜箔数顶替**) ★★
```
⇒ ★**⇒ 【料号】main 已拍; 【land 几何】官方明文要求「官网单品页二次确认」 ⇒ 至今 0 人做** ★

★**② main 本机实读: `FTS-104-01-F-S` 这个料号在 HW / MECH / SW 三个域的页面里【命中 0 次】** ★
```
$ grep -rn "FTS-104-01-F-S" HW/ MECH/ SW/     ⇒ (0 命中)
⇒ ★**全项目没有任何一页写下了 FTS 单排件的官方 land 几何** ★
```
★**③ 后果比「少一页文档」严重: MECH 侧那一整条 3D 判决链的铜箔宽, 读的是【通用 KiCad 库件】, 不是【那颗 FTS 厂件】★**
★`MECH/check_debug_seat_3d_fit.py` L98~L101 (★main 本机实读★):
```python
KICAD_LIB = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty"
FOOTPRINT_FILE = {
    "J_DEBUG": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
    "J_UART":  "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
}
```
★⇒ ★**那两颗件的铜箔宽 `4.8100` / `2.2700` (= 官方 1.27mm THT 通用件 land) 就是 MECH 全部 3D 余量数的输入** ★
★⇒ ★**而 §㊳ A2 现在指向的厂件是 Samtec FTS (post .016″/.41mm 方柱) ⇒ 若 FTS 原厂 land 的铜箔宽 ≠ 通用件 ⇒ MECH 的 `6.6100` / `4.0700` / `2.6950` / `0.1350` 全线要重算** ⇒ ★★**⇒ 这就是「板只改一次」那一趟最该先钉死的那一个数: 铜箔宽一变, 结构件出件口径整个变** ★★

★**④ 本单地界: 查【厂件官网/官网单品页/分销参数表】里的 land 几何** ⇒ ★**零外发** ★ (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)

---

## ★★二 · 本单要交 3 件 (★三件都要在盘 + 交卷页 B1~B6 齐全★) ★★

1. ★**`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md`** (★真相页★)
2. ★**`HW/check_fts_single_row_land_truth.py`** (★新闸 · 零挂链★)
3. ★**`HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md`** (★交卷页 · B1~B6★)

### ★★① 真相页 `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` ★★
★**§0 一句话结论** (★把「能不能落板」这件事说死★) ★
★**§1 查证方法与证据分级** (★每条结论标 `[官网]` / `[媒体]` / `[实测]` / `[推算]` / `[0数据]`★) ★
★**§2 `FTS-104-01-F-S` (4 位) 官网单品页逐项抄录** ★
★**§3 `FTS-102-01-F-S` (2 位) 官网单品页逐项抄录** ★
★**§4 与盘上【通用 KiCad 库件】逐项对比表** (★★**必须逐项列, 不许只写结论**★★) ★
★**§5 与 §㊳ A2 / §㊳ A4 / ISS-379 / ISS-380 / ISS-383 的关系与影响面** (★谁在用这个数★) ★
★**§6 降级方案** (★★**查不到就写降级方案, 不许挂起**★★) ★
★**§7 复跑命令 + 机器块** (★机器块给下游闸读★) ★

★**§2/§3 必须逐项抄录的字段 (★每项都要有值或 `[0数据]` + 降级方案, 不许留空★)**:
| 字段 | 说明 | ★为什么必须★ |
|---|---|---|
| `post_size` | ★方针尺寸 (★§㊳ A2 说是 `.016″`/.41mm 方柱 ⇒ **你要去官网单品页确认这个数, 不许抄决策页★**) ★ | ★**决定座体真实高 h 与 Y 向余量 (OI-11)★** |
| `copper_x_width` | ★**原厂 land 的铜箔 X 宽 (mm) —— 本单最要紧的一个数** ★ | ★**MECH 全链 3D 余量的输入 (见 §一③)★** |
| `pad_drill` | 焊盘尺寸 / 钻孔直径 | ★决定能否用盘上通用封装 (`1.000×1.000` / `0.65`) ★ |
| `seat_height` | 座体高 h | ★OI-11 (归 boss) 的实测输入 ★ |
| `pitch` | 排距 (须核 = 1.27mm) | ★B-2 / E-1 口径★ |
| `positions_rows` | 位数 / 排数 (★须核是不是 1 排!) ★ | ★ISS-383 §0-2 已被推翻过一次 ⇒ **不许靠猜** ★ |
| `mount_style` | THT / SMT | ★决定能不能走「单排直插」档 ★ |
| `mating_footprint` | ★原厂推荐 PCB footprint 名/图 (★Samtec 官网常有 land pattern 图 / PDF 机械图★) ★ | ★**本单的核心交付** ★ |
| `keepout_dwg` | ★厂商 keepout / 机械图来源 (★官网 PDF / 3D 模型★) ★ | ★OI-10 要的「厂商 keepout 图纸从哪里补」 ★ |
| `datasheet_url` | 官网单品页 / 数据表直链 | ★留档可复核 ★ |

★**§4 对比表必须有的列**: ★`字段` · ★`FTS 厂件 (官网)` · ★`盘上通用 KiCad 库件 (本机实测)` · ★`一致?` · ★**`若不一致 ⇒ 影响哪条判据`** ★
★**盘上通用件自己实测 (不许抄)**: `Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 与 `..._1x02_...` ⇒ ★**自己解析 pad 尺寸/钻孔/铜箔包络**, 别抄 ISS-379/380 的结论 ★

★**§5 影响面必须点名这几条 (★本单的「为什么要做」就在这里★)**:
★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 的 `6.6100` / `4.0700` / `2.6950` / `0.1350` / `0.7700` (★**全链输入 = 铜箔宽**★) · ★`MECH/check_debug_seat_3d_fit.py` L491 / L683~L686 / L746 (★**写死 `4.81` / `2.27` 的那几行★**) · ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 的 **OI-5** (清空区 X 三档 `1.7750`/`4.0850`/`4.8100`) · ★**ISS-383 §2 的 D-1/U-1 判定** (★已被 main 推翻过一次, ★**FTS 与 FTSH 是不同族, 不许拿 FTSH 的数顶替 FTS**★) · ★**BOM 型号栏** (★`HW/BOM_v1.csv` 的 J_DEBUG / J_UART 行, ★**本单零落表, 只给草案★**) ★

### ★★② 新闸 `HW/check_fts_single_row_land_truth.py` ★★
★**零挂链** (★`state/gate_check.py` 命中必须 = 0 ★ — 挂链是 main 的地界★) ★
★**判据 K0~K6 建议 (★fail-closed · 每条判据都要有反向用例★)**:
- ★**K0** 真相页在盘 + 机器块在盘 + 页里**没有**空字段 (★`[0数据]` 允许, ★**空字符串不允许**★) ★
- ★**K1** `positions_rows` 必须是 1 排 (★**这一条是本单最容易翻车的地方**: ★FTSH 是 2 排, ★**FTS 是 1 排, 族不同**★ ⇒ 页里若写成 2 排必须判红★) ★
- ★**K2** `copper_x_width` 与 `copper_y_width` 必须与**从厂商 land 实测/抄录**的值一致 (★不许写死 ⇒ 闸自己从真相页机器块读, ★**改页即红**★) ★
- ★**K3** ★**★本单的命门★**: 真相页里 `copper_x_width` 的值若**不等于**盘上通用 KiCad 库件实测的铜箔宽 ⇒ ★**必须显式登记「与通用件不一致」这个事实 + 影响面清单里点名 MECH 那几行** ⇒ ★**没登记就判红** (★**不许默默写一个不同的数**★) ★
- ★**K4** ★**不许拿 FTSH 的数顶替 FTS** ⇒ ★**页里若出现 `FTSH-` 料号与 FTS 料号混用 ⇒ 判红** ★
- ★**K5** 证据分级白名单 (★`[官网]`/`[媒体]`/`[实测]`/`[推算]`/`[0数据]`★) + ★**零挂起措辞** (★「等原厂回信」/「待外部确认」/「等回复」/「pending reply」/「待确认」等语境判红★) ★
- ★**K6** 板三项指纹未动 (★md5 + mtime + size★) + ★**零落表** (★网表/脚表/BOM 三件 md5 与基线同★) ★
★**`--selftest` 至少 8 条反向用例**, ★**其中至少 2 条专打本单的命门**: ★① 页面把 `positions_rows` 从 1 改成 2 ⇒ 必须 K1 红 ★② 页面把 `copper_x_width` 改成一个**与通用件不同的数** 却**没登记影响面** ⇒ 必须 K3 红 ★
★**★本单的 `--selftest` 必须【与环境无关】★** (★★**见 §四的坑: 现役 `SW/tools/check_debug_pin_order_contract.py` 就是栽在这里★★)

### ★★③ 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md` ★★
★**B1~B6 六段齐全** (★**闸认这六段, 缺一段就红**★) + ★**B6 必须贴必跑命令的原样输出 + rc** ★

---

## ★★三 · 分片 ★★
★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ★
★**产出物 ≥3 条 + `interface_claims` ≥5 条 + `needs_from` (★`to=main`★) ★**
★**★`needs_from` 必须逐条写清「要谁回答什么 + 代价」, 不许只写「请裁决」★**

---

## ★★四 · ★★本单必跑的坑 (★main 本机实测踩过, 你不要重踩★) ★★

★★**坑 1 ★★ `--selftest` 必须与环境无关 (★★**现役 `SW/tools/check_debug_pin_order_contract.py` 今天实测栽在这里: ★**默认 `/tmp` ⇒ 10/11 FAIL; `TMPDIR=$PWD/tmp` ⇒ 11/11 PASS** ⇒ ★**⇒ 你的沙盒目录必须放在【项目盘】且深度要能被 `__file__` 反推对, 不许依赖系统 `/tmp` 的深度**★ ★★) ★★

★★**坑 2 ★★ 官网/分销页可能拿不到 (★**查不到就写 `[0数据]` + **降级方案**, ★**不许写「等原厂回信」/「待外部确认」**★) ⇒ ★**降级方案至少给这三条里的一条**: ★① 选【官网参数直接满足的替代型号】★ ② 改【用盘上通用 KiCad 库件 land 并显式登记该偏离】★ ③ 【实测样件】复现路径 ★

★★**坑 3 ★★ `state/frag_write.py --add-*` 的分隔符是【空格】不是【分号】** (★`shlex.split()` 切参数 ⇒ 任务书示例里的 `path=…;summary=…` 会把整串吞进 `path` ⇒ **写出畸形条目却照样打印「✅ 已原子更新」**★) ⇒ ★**写完必须 `grep` 复验条目唯一, 不许只信它打印的那行** ★

★★**坑 4 ★★ 「官方 PDF 机械图」很可能本机没有解析器** ⇒ ★**你只准把官网上的**文字参数**抄进页里 + 标注证据等级; ★**不许把 PDF 里的图当已核实几何**★ ⇒ ★**几何要么来自官网文字/表格, 要么标 `[0数据]`** ★

---

## ★★五 · 必跑命令 (★全部实测存在的真命令 ★· 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 命令存在性守卫 (★派活前 main 已跑过 rc=0, 你开工再跑一遍★)
python3 state/check_brief_commands.py

# ② 本单新闸 (★你自己写的, 裸跑 + selftest★)
python3 HW/check_fts_single_row_land_truth.py
python3 HW/check_fts_single_row_land_truth.py --selftest

# ③ 盘上通用 KiCad 库件自己实测 (★★不许抄结论, 自己解析 .kicad_mod★★)
python3 state/check_footprint_geom.py

# ④ 已签收的相关闸 (★只读, 用来对照口径·不许改★)
python3 HW/check_debug_uart_seat_alignment.py
python3 HW/check_debug_uart_seat_alignment.py --selftest
python3 HW/check_debug_uart_seat_truth.py

# ⑤ MECH 侧 3D 闸 (★只读, 用来点名「哪几行吃铜箔宽」★)
python3 MECH/check_debug_seat_3d_fit.py
python3 MECH/check_debug_seat_3d_fit.py --selftest

# ⑥ 板 / 三表 指纹 (★开工前后各打一次, 逐项对比★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑦ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/frag_write.py --agent hw-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

★★**基线 (★main 2026-11-24 09:1x 本机实跑, 你自己再核一遍★)** ★★
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
⇒ ★**板 18 天逐字节未动 ⇒ G1 仍开, 不许投板** ★
gate_check.py ⇒ rc=0 · 【Q1 交付齐备率】18/18 · 【Q7 钉板 md5 闸链】10/10 道绿
```

---

## ★★六 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★零改既有闸/既有页面正文★ | ★`MECH/check_debug_seat_3d_fit.py` / `HW/check_debug_uart_seat_alignment.py` / `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 等 md5 与基线同★ |
| ★零挂链★ | ★`grep -c check_fts_single_row_land_truth state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机 + 自己上网查; ★`state/outbox/` 一个字节未动★ |
| ★不代拍★ | ★页里没有「已决定 / 应采用」式裁决语; ★`landing_part_decision = not_decided_here` 这类机器块要有★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/hw.yaml`★ |
| ★证据分级★ | ★每条结论标五级之一★ |
