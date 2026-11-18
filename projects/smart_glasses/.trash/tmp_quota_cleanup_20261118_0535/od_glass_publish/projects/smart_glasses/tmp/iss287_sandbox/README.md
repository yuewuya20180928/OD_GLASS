# ISS-287 沙盒 (tmp/iss287_sandbox) · README

- 单号: ISS-287 · owner: hw-lead · verify_by: main · 建档: 2026-11-17 13:39 · 末次更新: 2026-11-17 14:4x
- 用途: ★**「板只改一次」那一趟 (S1~S13) 的干跑沙盒** ★ —— 在**不动真盘板**的前提下, 先把「网表 → 原理图 → 板 → 布线 → Gerber」整条链跑一遍, 回答"能不能干跑 + 缺哪几个开关"。
- ★**本沙盒里的产物一律不许拷回真盘** ★ (真盘 `HW/PCB/demo_mainboard.kicad_pcb` 永远是唯一官方板)
- ★**本沙盒里的 `state/gen_*.py` 是只读副本, 一个字节都不许改** ★ (改了也不能回灌)

---

## 一、怎么复跑 (★命令可原样复制★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── 0) 建沙盒 (★只在第一次 / 想从头来时做; ★已有沙盒就别重建★) ──────────
mkdir -p tmp/iss287_sandbox
for d in HW state MECH SW config deploy; do cp -a "$d" tmp/iss287_sandbox/; done

# ── 1) 板侧: 只生成, 不布线 (★产物落沙盒, 不碰真盘板★) ─────────────────
cd tmp/iss287_sandbox
PCB_OUT="$PWD/HW/PCB/sandbox_gen_board.kicad_pcb" \
PCB_SKIP_ROUTE=1 \
python3 state/gen_pcb_netlist_board.py

# ── 2) 原理图侧整链 (★产物落沙盒: netlist / pins / BOM / kicad_sch★) ──────
python3 state/gen_netlist.py
python3 state/gen_netlist_pins.py
python3 state/gen_kicad_sch.py
python3 state/gen_bom.py

# ── 3) 读数 (★只读: 只 LoadBoard, 不 SaveBoard★) ─────────────────────────
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
bash state/pcbnew_py.sh tmp/iss287_sandbox/probe_readings.py \
     HW/PCB/demo_mainboard.kicad_pcb \
     tmp/iss287_sandbox/HW/PCB/sandbox_gen_board.kicad_pcb
bash state/pcbnew_py.sh tmp/iss287_sandbox/probe_refdiff2.py \
     tmp/iss287_sandbox/HW/PCB/sandbox_gen_board.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
bash state/pcbnew_py.sh tmp/iss287_sandbox/probe_refdiff3.py \
     HW/PCB/demo_mainboard.kicad_pcb tmp/iss287_sandbox/HW/PCB/sandbox_gen_board.kicad_pcb
bash state/pcbnew_py.sh tmp/iss287_sandbox/probe_refdiff4.py \
     HW/PCB/demo_mainboard.kicad_pcb tmp/iss287_sandbox/HW/PCB/sandbox_gen_board.kicad_pcb

# ── 4) S1 判据 (位号问号) —— ★原理图侧导出 BOM 再数问号行★ ──────────────
bash state/kicad.sh sch export bom tmp/iss287_sandbox/HW/PCB/demo_mainboard.kicad_sch \
     -o tmp/iss287_sandbox/s1_bom_export.csv
grep -c '?' tmp/iss287_sandbox/s1_bom_export.csv     # ★现状 = 0★

# ── 5) 真盘零写板自证 (★收工必跑★) ───────────────────────────────────────
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb        # ★期望仍是 2026-11-06 07:07:17★
```

⚠️`[实测]` **`state/pcbnew_py.sh` 必须用** —— 系统 python 直接跑会 `ModuleNotFoundError: pcbnew` (pcbnew 只在 KiCad AppImage 的 python 里)。

⚠️`[实测]` **长命令走 `nohup … > logs/iss287/x.log 2>&1 &` + 短轮询** (前台长跑 = 被掐的头号原因; 上一趟就是这么超时的)。

---

## 二、沙盒与真盘的差异清单 (★关键: 沙盒 ≠ 完全隔离★)

### 2.1 复制无损的部分 (★逐字节相同★)
| 文件 | 沙盒 md5 | 真盘 md5 | 判定 |
|---|---|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` (官方板副本) | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**逐字节相同 ⇒ 复制无损** ★ |
| `HW/netlist_v1.csv` | `37f62ac3f0b81d92ca7d48fdea717f07` | 同 | 同 (重生成后仍逐字节相同 ⇒ 链自洽) |
| `HW/netlist_v1_pins.csv` | `a4270120454aedf7a23c92cd8985c8a6` | 同 | 同 |
| `HW/BOM_v1.csv` | `5d02bece9477ffce5fbe0193c7d5cce4` | 同 | 同 |
| `HW/PCB/demo_mainboard.kicad_sch` (根页) | ★**`6de7c8fb7cc270726705dace1bf40acd`** (13:50 重生成) | ★**`ec4e3860d8627f04a573c35f71ac53b9`** | ★**md5 不同, 但内容相同 (只差 KiCad 每次重生成的 uuid), 文件大小都是 6809 B** ★ |

### 2.2 沙盒独有 (真盘没有的)
| 路径 | 说明 |
|---|---|
| `HW/PCB/sandbox_gen_board.kicad_pcb` (461766 B) | ★**沙盒生成板 (13:49) —— 不是官方板** ★ 185 个器件 / 832 焊盘 / 160.0×100.0mm / **DNP 标记已打 40 个位号** |
| `probe_readings.py` | 只读读数探针 (封装/位号/铜层/板框/DNP/unconnected) |
| `probe_refdiff.py` | 只读: 沙盒生成板 vs 官方板 最早版对比 |
| `probe_refdiff2.py` | 只读: 共同位号 / 值·封装差异 / 只在某一边 |
| `probe_refdiff3.py` | 只读: 位号差集 / 重复位号 / `_1` 后缀 / DNP 标记差异 ★(★差 1 = `C_VBUS_GND` 就是它查出来的★)★ |
| `probe_refdiff4.py` | 只读: 26 处 Value 差异明细 (封装名差异 vs 仅 Value 差异) |
| `s1_bom_export.csv` | S1 判据用 (kicad-cli 原理图 BOM 导出) |
| `state/` (36 个目录的副本) | 生成器 + 守卫脚本副本 ★**只读, 不许改** ★ |
| `MECH/ SW/ config/ deploy/` | 复制进来但本单没用到 (为「板那一趟」整树干跑预留) |

### 2.3 ★★沙盒 ≠ 完全隔离: 两个写穿点 (★都会落到**真机** `/tmp`★)★★
| # | 位置 | 行为 | 本趟实测 |
|---|---|---|---|
| 1 | `state/gen_pcb_netlist_board.py:536` | ★**写死** `out = "/tmp/_layout_done_drc.json"` ⇒ DRC 输出落真机 `/tmp` | ★**本趟未被写到** (`/tmp/_layout_done_drc.json` 不存在) ⇒ 因为 `_write_layout_done()` 第 523-525 行对**非官方板**提前 `return` ⇒ ★**沙盒臂里这条路是哑的; 一旦走"写正式板"臂就会踩到** ★ |
| 2 | `board_gen.log` 实跑输出 | ★`✓ 已备份: /tmp/board_last_good_sandbox_gen_board.kicad_pcb` ⇒ 备份路径同样落真机 `/tmp` | ★**本趟已被写到** (沙盒板的备份落在真机 /tmp) |

⇒ ★**结论: 沙盒隔离的是"真盘工程文件", 不是"真机文件系统"。/tmp 是共用的 ⇒ 「板那一趟」必须把 /tmp 写穿点写进任务书 (至少要确认它不污染真盘)**★

### 2.4 ★官方板 vs 沙盒生成板: 三个必须知道的差 (★不许抹平★)
1. ★**封装数 186 (官方) vs 185 (生成)**: 差 1 = ★**`C_VBUS_GND`** ★ —— 网表里它是 **CHG_BOARD 归属 + DNP**, 但官方板上**有实物封装 @ (107.70, 42.50) 且未打 DNP 标记** ⇒ ★**重跑生成器 ⇒ 它会从板上消失** ★
2. ★**26 处 Value 不同** (位号/封装名/数量全同, 只差 Value): 12 处官方板 Value 被塞了网名·功能描述 (如 `U_DCDC_VCORE` = "EN 输入 (高 = 使能)"), 14 处官方板是旧选型值 (如 `R_BAT_DET_1` 1M vs 网表 100k) ⇒ ★**重跑生成器 ⇒ 这 26 条全被覆盖** ★
3. ★**DNP 标记: 官方板 0 个 / 生成板 40 个** ⇒ ★**S7 的活就是把官方板这 40 个位号打上标记** ★ (★目标数字是 **40**, 不是 43 —— 43 是 12:30 那次落表之前的旧数★)

---

## 三、日志索引 (`logs/iss287/`)
| 文件 | 内容 |
|---|---|
| `copy.log` | 复制树 6 件全 `COPY_DONE rc=0` |
| `board_gen.log` | 沙盒出板 (185 器件 / 832 焊盘 / 判定全过 / RC=0) |
| `sch_chain.log` | 原理图侧整链 (gen_netlist → pins → kicad_sch → bom, 全 RC=0, ALLDONE) |
| `r3.log` | R3 自相矛盾门禁 (rc=1, findings 2: F2 J_CHG + F3 DNP 零标记 40) |
| `calib.log` | 板框口径闸 (沙盒根, 全过) |
| `calib_realdisk.log` | 板框口径闸 (真盘根, 封装 186 / 8 层 / 160.10×100.10 / S6 19-1-0) |
| `drc_official.log` | DRC 闸 (violations 0 / unconnected 45 / Gerber 32 / DRC_RC=0) |
| `onepass.log` | 「板只改一次」时序守卫 D0~D6 全过 (变更区 0 行) |
| `landrow.log` | 落表行号锚点守卫 (PASS=310 · DRIFT=0 · RED=0) |
| `merge.log` / `gate.log` / `issue_check.log` | 状态合并 / Q1 18-18 / 问题闭环 283 条 |
| `refdiff2.log` / `refdiff3.log` / `refdiff4.log` | ★**本 job (cont2) 新跑的 3 个只读差异探针** ★ |
| `s1_bom.log` | ★**本 job 新跑: kicad-cli sch export bom** ★ |
| `sandbox_pristine.md5` / `sandbox_pre_chain.md5` | 沙盒建档基线 / 跑链前基线 |

---

## 四、边界声明 (★本沙盒这一趟做到了什么 / 没做到什么★)
- ✅ **零写板**: 真盘官方板 md5 `611b869e…` / mtime `2026-11-06 07:07:17` 前后不变
- ✅ **零落表**: 网表/脚表/BOM md5 与落表台账登记值一致 (ISS-283 那次合法落表, 不是本单的锅)
- ✅ **零改生成器代码**: 沙盒里的 `state/gen_*.py` 与真盘逐字节相同, 一个字节没动
- ✅ **没跑布线臂**: 全程 `PCB_SKIP_ROUTE=1`
- ✅ **没把沙盒产物拷回真盘**
- ⚠️ **沙盒不是完全隔离**: 2 个 `/tmp` 写穿点 (见 §2.3)
