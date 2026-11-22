#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 18:4x · job 775d9893「ARS45 继续执行后继计划」
★(1) 按【全仓钉板 md5 清单】给三个域各开一条单 (★MECH 2 道 / HW 6 道 / SW 1 道)★ —— 目标: 板那一趟合法改板当天, 这些闸红的是「板被换了」而不是「板改坏了」★
★(2) 把 main 对 E-1 / E-2 两条板侧取舍的裁决写进 pm.yaml (★唯一真源★)★
★**纪律: 三个任务书由同一份清单生成 (★不许各写各的★) ★**
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
PM = os.path.join(HERE, "fragments", "pm.yaml")
GATES_JSON = os.path.join(HERE, "board_md5_pinned_gates.json")
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


SHAPE = """```yaml
# ★★照 ISS-284 (SW 侧已跑通) 的 reboard 原子映射, 不许自创形状★★
reboard: null                     # 还没发生过合法改板 ⇒ 纯 md5 硬保护 (盘上 ≠ 基线 ⇒ 红)
reboard: {by: <单号>, file: <文件名>, prev_md5: <改前>, md5: <改后>}
                                   # ★一个原子映射: 四项缺一 ⇒ 整条记录无效 ⇒ 红★
                                   # ★且四项必须能在落表台账里查到 (单号 + 文件名 + 新旧 md5)★
                                   # ★判据方向不许变: 盘上 ≠ 链头 ⇒ 红 (合法改板只让链头前移)★
                                   # ★fail-closed 三条一条不许动: 链头不唯一 / 链断 / 链头无单号 ⇒ 红★
```"""

COMMON = """
## ② 每个域要做的三件 (★逐条照做, 不许自创口径★)

1. ★**把该域里【每一道钉着板 md5 的闸】改成读台账口径** ★
   - ★**判决源**: 板 / `.kicad_pro` 的 md5 判定 ⇒ ★**优先读落表台账链头** (`HW/SCHEMATIC_LANDING_V1_LANDED.md`) ★
   - ★**合法改板**: 若台账里有【本单号 + 文件名 + 改前 md5 + 改后 md5】齐全的记录 ⇒ ★**盘上 md5 == 记录里的新 md5 ⇒ 放行** ★ ⇒ ★**记录缺失 / 四项不齐 / 盘上 ≠ 记录 ⇒ 红** ★
   - ★**★`reboard: null` (还没发生过合法改板) ⇒ 仍按纯 md5 硬保护判 (盘上 ≠ 基线 ⇒ 红)** ★ ⇒ ★**不许为了「将来会改」就把基线放松** ★
2. ★**★判据强度不许减 (逐条对照★)**:
   | 原来 | 改完必须仍然 | 不许 |
   |---|---|---|
   | 盘上 ≠ 基线 ⇒ 红 | ★**盘上 ≠ 链头且无合法记录 ⇒ 红** ★ | 不许改成「取最近一条就绿」 |
   | 基线写死 | ★**基线仍是 append-only 的历史事实** ★ | 不许改基线来「让它绿」 |
   | (无) | ★**新增 fail-closed 三条** ★ | 链头不唯一 / 链断 / 链头无单号 ⇒ **仍红** |
3. ★**反向用例 ≥4 条 (每条贴原样 rc★)**:
   | # | 构造 | 期望 |
   |---|---|---|
   | ① | ★**台账里有合法改板记录 (四项齐全) 且盘上 == 新 md5** ★ | ★**绿** (★这就是「合法改板」的样子★) ★ |
   | ② | ★**只改了基线里的 md5, 没有台账记录** ★ | ★**红** (★这就是「挖坑」, 必须堵死★) ★ |
   | ③ | ★**台账记录四项不齐 (缺单号 / 缺前后 md5 / 文件名对不上)** ★ | ★**红** ★ |
   | ④ | ★**台账里有记录但盘上 md5 ≠ 记录里的新 md5** ★ | ★**红** (★合法改板 ≠ 随便改★) ★ |
   | ⑤ | ★**链头不唯一 / 链断 / 链头无单号** ★ | ★**红** (★fail-closed 不许动★) ★ |

## ③ 必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
%s
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py   # 期望 rc=0 / rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ★★板 611b869e… / .kicad_pro 3e504d2b… 一个字节不许变 (本单零写板)★★
```

## ④ 交卷物 (★3 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_%s_ISS%s_合法改板通道.md` (★B1~B6 齐全★) ★
2. ★**该域每一道闸的改动 + 反向用例** ★
3. ★**分片** `state/fragments/%s.yaml` (★走 `state/frag_write.py --agent %s` 原子写 + grep 校验★) ★

## ⑤ 边界 (★违反就是不合格★)

★**零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 一个字节不许动★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 台账本体 (★只读★)** ★ · ★**不许动别域的闸** ★ · ★**不许放宽 fail-closed 三条** ★ · ★零外发 · ★**不替老板拍板** ★ · ★**不自签 issue_log** ★

## ⑥ 纪律

★**交卷单第一件事就是 `write` 建骨架** ★ · ★**长任务 `nohup` 后台 + 短轮询** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**分片写完 `grep` 校验自己的 key 在不在** ★
"""

E12 = """### ★★main 对 E-1 / E-2 的裁决 (★2026-11-17 18:4x·★这两条归 main, 不归老板★)★★

| # | 事实 | ★**裁决** ★ |
|---|---|---|
| ★**E-1** ★ | ★**BOM/网表写「1.27mm 排针」, 板上 land 实测 0.50mm pitch (Δ0.77) ⇒ 实物排针落不进** ★ · ★**BOM 那两行的备注自己写着「型号/间距/引脚编号【待结构与装配复核】」(★证据等级 [推算]★)** ★ | ★**★按 1.27mm 排针定 ⇒ 板 land 要改成 1.27mm ⇒ 并进「板只改一次」那一趟同一次做★** ★ ⇒ ★**理由**: ① `J_DEBUG` 是 JTAG 调试口 / `J_UART` 是 UART 口 ⇒ ★**0.5mm 单排不是常规可手插排针, 探针与杜邦线都插不上 ⇒ 「改料号到 0.5mm」这条路等于把调试口做成摆设 ⇒ 否决** ★ ② BOM 备注已写「待结构与装配复核」⇒ ★**本次复核的结论就是「1.27mm 成立, 所以 land 画错了」** ★ ③ ★**改 land 会动那 6 个焊盘 ⇒ 它们的走线本来就要在那一趟重布 ⇒ 与「unconnected 45→0」同一次做完, 不额外增加板改次数** ★ ⇒ ★**另: 改完必须用 `MECH/check_onepass_struct_crosscheck.py` (N2/N3/N4 净距核对) 复验一遍, 不许压 SoM 座** ★ |
| ★**E-2** ★ | ★**`HW/PCB/demo_mainboard_params.json` 的 `corner_radius_mm: 3.0` 是【死参数】: 板框实测 R=0.00, 且 `state/gen_pcb_netlist_board.py` 的 `add_outline()` 根本不读它** ★ | ★**★按【口径改板读 · 零板改】落: 把 params 里那个值改成与板框实测一致 (R=0.00) 或直接删掉这个死参数 + 在页里注明「板框无圆角」★** ⇒ ★**3.0 圆角【不】并进那一趟** ★ ⇒ ★**理由: 圆角对功能零影响, 而那一趟已经装了 5+ 项板改 (Q_PG 三根线 / D_ESD_USB_D 2→3 脚 + 挪位 / 位号 _1 后缀 / C_VBUS_GND 下板 / R4·R9 落表 / E-1 排针 land) ⇒ 再加一项只增风险; 哪天要圆角, 单独一次小改** ★ ⇒ ★**★但死参数必须清掉 (留着 = 下一个人会以为板框有 3.0 圆角)★★** ★ |

⇒ ★**两条合计: 板那一趟的板改清单再 +1 项 (E-1 的排针 land 重画), 但仍只改一次板; E-2 零板改 ⇒ 只清参数** ★
"""

NEW_ISSUES = [
    # (id, owner, domain_label, files, brief_name)
    ("ISS-296", "mech-lead", "MECH", "MECH/check_board_frame_coords.py (C4)<br>MECH/check_demo_struct_truth.py (G5b 的 `MD5_EXPECTED`)",
     "mech-lead", "2026-11-17_mech-lead_ISS296_合法改板通道.md"),
    ("ISS-297", "hw-lead", "HW", "HW/check_fsin_rootcause.py<br>HW/check_g1a7_selection_landed.py<br>HW/check_onepass_commit_order.py<br>HW/check_onepass_preflight_coverage.py<br>HW/check_pin_function_labels.py<br>HW/check_workpack_state_values.py",
     "hw-lead", "2026-11-17_hw-lead_ISS297_合法改板通道.md"),
    ("ISS-298", "sw-lead", "SW", "SW/tools/check_onepass_sw_sync.py",
     "sw-lead", "2026-11-17_sw-lead_ISS298_合法改板通道.md"),
]


def main() -> int:
    gates = json.load(open(GATES_JSON, encoding="utf-8"))
    # ---------- 任务书 ----------
    for iid, owner, dom, files, agent, fn in NEW_ISSUES:
        body = f"""★**{iid} · {owner} 任务书 —— ★★【{dom} 侧 {len(files.split('<br>'))} 道闸: 建「合法改板」通道 (★板那一趟改板当天不许集体假红★)】★★** ★ (main · 2026-11-17 18:4x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 18:4x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: {owner} · ★**verify_by**: main · ★**单号**: {iid} · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 门禁机制收口 · ★★零写板 · 零落表★★** ★

---

## ① 病灶 (★main 18:3x 真扫全仓, 原样★)

★**全仓有 9 道闸硬钉着板 md5 `611b869e…`; 板那一趟 (S1~S13) 合法改板当天, 它们会一起红** ★
⇒ ★**而这些红的真实含义是「板被换了」, 不是「板改坏了」** ⇒ ⇒ ★**现场极可能误读成后者 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★
⇒ ★**★本单域内要补通道的闸 (共 {len(files.split('<br>'))} 道)★**:
{files}

★**★全仓清单 (★机器生成, 可复核★)★**: ★**`state/board_md5_pinned_gates.md`** ★ (★生成脚本 `state/_gen_board_md5_pinned_gates.py` · 另有机器可读 JSON `state/board_md5_pinned_gates.json`★) ★
⇒ ★**别的域的闸由别的单管 (★MECH 侧 = ISS-296 · SW 侧 = ISS-298★) ⇒ ★**你只许改自己域里的文件** ★

★**★口径已被证明可行 (★不是猜的★)**: ★**`SW/tools/check_demo_panel_spec.py` 在 ISS-284 转成台账口径后, 它已经不再硬钉板 md5 ⇒ 那份清单里根本找不到它** ★ ⇒ ★**⇒ 「不硬钉」不是靠把断言删掉, 是靠判决源换成【落表台账 + 合法改板记录】** ★
⇒ ★**★通道形状 (★照 ISS-284 已跑通的口径, 不许自创★)★**:
{SHAPE}

{E12}
## ② 每个域要做的三件 (★逐条照做, 不许自创口径★)

1. ★**把该域里【每一道钉着板 md5 的闸】改成读台账口径** ★
   - ★**判决源**: 板 / `.kicad_pro` 的 md5 判定 ⇒ ★**优先读落表台账链头** (`HW/SCHEMATIC_LANDING_V1_LANDED.md`) ★
   - ★**合法改板**: 若台账里有【本单号 + 文件名 + 改前 md5 + 改后 md5】齐全的记录 ⇒ ★**盘上 md5 == 记录里的新 md5 ⇒ 放行** ★ ⇒ ★**记录缺失 / 四项不齐 / 盘上 ≠ 记录 ⇒ 红** ★
   - ★**★`reboard: null` (还没发生过合法改板) ⇒ 仍按纯 md5 硬保护判 (盘上 ≠ 基线 ⇒ 红)** ★ ⇒ ★**不许为了「将来会改」就把基线放松** ★
2. ★**★判据强度不许减 (逐条对照★)**:
   | 原来 | 改完必须仍然 | 不许 |
   |---|---|---|
   | 盘上 ≠ 基线 ⇒ 红 | ★**盘上 ≠ 链头且无合法记录 ⇒ 红** ★ | 不许改成「取最近一条就绿」 |
   | 基线写死 | ★**基线仍是 append-only 的历史事实** ★ | 不许改基线来「让它绿」 |
   | (无) | ★**新增 fail-closed 三条** ★ | 链头不唯一 / 链断 / 链头无单号 ⇒ **仍红** |
3. ★**反向用例 ≥4 条 (每条贴原样 rc★)**:
   | # | 构造 | 期望 |
   |---|---|---|
   | ① | ★**台账里有合法改板记录 (四项齐全) 且盘上 == 新 md5** ★ | ★**绿** (★这就是「合法改板」的样子★) ★ |
   | ② | ★**只改了基线里的 md5, 没有台账记录** ★ | ★**红** (★这就是「挖坑」, 必须堵死★) ★ |
   | ③ | ★**台账记录四项不齐 (缺单号 / 缺前后 md5 / 文件名对不上)** ★ | ★**红** ★ |
   | ④ | ★**台账里有记录但盘上 md5 ≠ 记录里的新 md5** ★ | ★**红** (★合法改板 ≠ 随便改★) ★ |
   | ⑤ | ★**链头不唯一 / 链断 / 链头无单号** ★ | ★**红** (★fail-closed 不许动★) ★ |

## ③ 必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
{chr(10).join('python3 %s ; echo "rc=$?"' % f.split(' (')[0] for f in files.split('<br>'))}
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py   # 期望 rc=0 / rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ★★板 611b869e… / .kicad_pro 3e504d2b… 一个字节不许变 (本单零写板)★★
```

## ④ 交卷物 (★3 件★)

1. ★**交卷单** `HANDOFF/{fn}` (★B1~B6 齐全★) ★
2. ★**该域每一道闸的改动 + 反向用例** ★
3. ★**分片** `state/fragments/{agent}.yaml` (★走 `state/frag_write.py --agent {agent}` 原子写 + grep 校验★) ★

## ⑤ 边界 (★违反就是不合格★)

★**零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 一个字节不许动★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 台账本体 (★只读★)** ★ · ★**不许动别域的闸** ★ · ★**不许放宽 fail-closed 三条** ★ · ★零外发 · ★**不替老板拍板** ★ · ★**不自签 issue_log** ★

## ⑥ 纪律

★**交卷单第一件事就是 `write` 建骨架** ★ · ★**长任务 `nohup` 后台 + 短轮询** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**分片写完 `grep` 校验自己的 key 在不在** ★
"""
        open(os.path.join(HERE, "dispatch_briefs", fn), "w", encoding="utf-8").write(body)

    # ---------- pm.yaml: E-1 / E-2 裁决 ----------
    shutil.copy2(PM, PM + ".bak_20261117_1845_main_e1_e2")
    d = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    nf = d.setdefault("needs_from", [])
    have = {n.get("key") for n in nf}
    E = {
        "key": "main_e1_e2_board_side_rulings_20261117",
        "to": "main",
        "item": ("★★【ISS-290 的 E-1 / E-2 两条板侧取舍 ⇒ main 已拍死 (★2026-11-17 18:4x·★归 main 不归老板★)】★★ "
                 "★**E-1 排针 pitch**: BOM/网表写 1.27mm 排针, 板上 land 实测 0.50mm (Δ0.77) ⇒ 实物落不进; BOM 那两行自己写着「待结构与装配复核」([推算]) ⇒ "
                 "★**裁决 = 按 1.27mm 定 ⇒ 板 land 改成 1.27mm ⇒ 并进「板只改一次」那一趟同一次做** (★理由: 0.5mm 单排不是常规可手插排针, 探针/杜邦线插不上 ⇒ 「改料号到 0.5mm」等于把调试口做成摆设 ⇒ 否决; 且那 6 个焊盘的走线本来就要在那一趟重布 ⇒ 不额外增加板改次数★; "
                 "改完须用 `MECH/check_onepass_struct_crosscheck.py` N2/N3/N4 复验净距, 不许压 SoM 座★) ★ "
                 "★**E-2 corner_radius**: `HW/PCB/demo_mainboard_params.json` 的 `corner_radius_mm: 3.0` 是死参数 (板框实测 R=0.00, `gen_pcb_netlist_board.py` 的 `add_outline()` 根本不读) ⇒ "
                 "★**裁决 = 口径改板读 · 零板改: 把 params 那个值改成与实测一致 (R=0.00) 或删掉 + 页里注明「板框无圆角」; 3.0 圆角【不】并进那一趟** (★理由: 圆角对功能零影响, 而那一趟已装 5+ 项板改 ⇒ 再加只增风险; 哪天要圆角单独一次小改★; ★**但死参数必须清掉 — 留着 = 下一个人会以为板框有 3.0 圆角★)★"),
        "since": TODAY,
        "decision": ("★**E-1 = 按 1.27mm 排针定 + 板 land 并进那一趟重画** ★ + ★**E-2 = 零板改, 清死参数, 圆角不并进那一趟** ★ ⇒ "
                     "★**⇒ 板那一趟的板改清单 = Q_PG 三根线重画 + D_ESD_USB_D 2→3 脚并挪到 ≤3.0mm + 位号 _1 后缀 + C_VBUS_GND 下板 + R4/R9 落表 + E-1 排针 land 重画 ⇒ 板 md5 只变一次** ★"),
        "decided_at": "2026-11-17 18:45",
        "decided_by": "main (项目总工 · ★几何/规格取舍归 main★)",
    }
    if E["key"] not in have:
        nf.append(E)
    d["updated_at"] = "2026-11-17 18:45"
    d["updated_by"] = "main"
    open(PM, "w", encoding="utf-8").write(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100))

    # ---------- 给已存在的 ISS-296 补: 全仓清单 + E-1/E-2 裁决 ----------
    raw0 = open(LOG, encoding="utf-8").read()
    b0 = yaml.safe_load(raw0) or {}
    m0 = {it["id"]: it for it in b0.get("issues", [])}
    if "ISS-296" in m0:
        l0 = raw0.split("\n")
        s0 = e0 = None
        for i, ln in enumerate(l0):
            if ln.startswith("- id: "):
                if s0 is not None:
                    e0 = i
                    break
                if ln[len("- id: "):].strip() == "ISS-296":
                    s0 = i
        if e0 is None:
            e0 = len(l0)
        blk = l0[s0:e0]
        tb = m0["ISS-296"].get("task_brief") or ""
        if "全仓清单" not in tb:
            blk[0:0] = []  # no-op
            tb_add = ("\n\n---\n\n## ★★⑭ 追加 (★2026-11-17 18:4x main 实扫全仓·★你的活是【全仓 9 道闸】里的一格★)★★\n\n"
              "★**★全仓清单 (★机器生成, 可复核★)★**: ★**`state/board_md5_pinned_gates.md`** ★ (★生成脚本 `state/_gen_board_md5_pinned_gates.py` · 机器可读 JSON `state/board_md5_pinned_gates.json`★)\n"
              "⇒ ★**全仓共 9 道闸硬钉板 md5 `611b869e…`**: ★**HW 6 道** (`check_fsin_rootcause` · `check_g1a7_selection_landed` · `check_onepass_commit_order` · `check_onepass_preflight_coverage` · `check_pin_function_labels` · `check_workpack_state_values`) + "
              "★**MECH 2 道** (★你这一单★) + ★**SW 1 道** (`SW/tools/check_onepass_sw_sync.py`) ⇒ ★**HW 侧 = ISS-297 (hw-lead) · SW 侧 = ISS-298 (sw-lead)·★**\n"
              "⇒ ★**★口径已被证明可行 (★不是猜的★)**: `SW/tools/check_demo_panel_spec.py` 在 ISS-284 转成台账口径后**已不再硬钉板 md5** ⇒ ★**全仓清单里根本找不到它** ⇒ ★**⇒ 「不硬钉」不是靠删断言, 是靠判决源换成【落表台账 + 合法改板记录】** ★\n"
              "⇒ ★**★建议 (★main 18:4x 实跑得出的★)**: 你的【收工清单强制项】那一段, ★**把「收工后同一次重锚」的对象从【MECH 两道闸】扩成【全仓 9 道闸】** ★ ⇒ ★**否则 HW/SW 侧的闸在收工那天照样红, 一半收工清单等于没写** ★\n"
              + E12 + "\n")
            ki = [j for j, ln in enumerate(blk) if ln.strip().startswith("task_brief:")][0]
            import json as _j
            blk[ki] = "  task_brief: %s" % _j.dumps(tb + tb_add, ensure_ascii=False)
            nt = m0["ISS-296"].get("note") or ""
            if "全仓清单" not in nt:
                while blk and blk[-1].strip() == "":
                    blk.pop()
                blk.append("  main_supplement: %s" % _j.dumps(
                  "★**2026-11-17 18:4x main 补充**: ① 全仓清单 `state/board_md5_pinned_gates.md` (★9 道闸, HW 6 / MECH 2 / SW 1★) "
                  "② ★**建议把「收工后同一次重锚」的对象从 MECH 两道扩成全仓 9 道** ★ ③ E-1/E-2 两条板侧取舍的 main 裁决 (★E-1 = 按 1.27mm 排针定 + 板 land 并进那一趟; E-2 = 零板改 + 清死参数★)",
                  ensure_ascii=False))
            l0[s0:e0] = blk
            open(LOG, "w", encoding="utf-8").write("\n".join(l0))
            print("✔ ISS-296 已补: 全仓清单 + E-1/E-2 + 收工清单扩到 9 道")

    # ---------- issue_log: 开三条单 ----------
    raw = open(LOG, encoding="utf-8").read()
    before = yaml.safe_load(raw) or {}
    bmap = {it["id"]: it for it in before.get("issues", [])}
    for iid, *_ in NEW_ISSUES:
        if iid in bmap:
            if iid == "ISS-296":
                print("✔ ISS-296 已存在 (另一路已开同题) ⇒ 不重复开")
                continue
            print("❌ %s 已存在" % iid)
            return 2
    lines = raw.split("\n")
    out = []
    for iid, owner, dom, files, agent, fn in NEW_ISSUES:
        if iid in bmap:
            continue
        n = len(files.split("<br>"))
        out.append("- id: %s" % iid)
        out.append("  title: %s" % q(
            "★★[主线内·%s 侧·门禁机制收口·内部活] ★★【%s 侧 %d 道闸: 建「合法改板」通道】★★ ⇒ ★**全仓 9 道闸硬钉板 md5 `611b869e…`; 板那一趟合法改板当天它们会一起红** ★ "
            "⇒ ★**而那些红的真实含义是「板被换了」, 不是「板改坏了」⇒ 现场极可能误读 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ "
            "⇒ ★**口径已被 ISS-284 证明可行** (★SW 侧那道转成台账口径后就不再硬钉, 全仓清单里根本找不到它★) ⇒ ★**照 reboard 原子映射 {by,file,prev_md5,md5} + 四项缺一⇒红 + 与台账链头一致** ★ "
            "⇒ ★**判据不许松: 盘上 ≠ 链头且无合法记录 ⇒ 仍红; fail-closed 三条一条不许动** ★" % (dom, dom, n)))
        out.append("  severity: high")
        out.append("  owner: %s" % q(owner))
        out.append("  reporter: main")
        out.append("  raised: %s" % q(TODAY))
        out.append("  due: %s" % q("2026-11-20"))
        out.append("  status: %s" % q("open"))
        out.append("  external: false")
        out.append("  need_keys: []")
        out.append("  fix_ref: null")
        out.append("  verify_by: main")
        out.append("  verify_result: null")
        out.append("  verify_date: null")
        out.append("  note: %s" % q(
            "2026-11-17 18:4x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 18:3x 真扫全仓生成的清单** ★\n"
            "⇒ ★**任务书 `state/dispatch_briefs/%s`** ★\n"
            "⇒ ★**全仓清单 (机器生成)**: `state/board_md5_pinned_gates.md` + `.json` (★生成脚本 `state/_gen_board_md5_pinned_gates.py`★) ★\n"
            "⇒ ★**本域要补通道的闸 (%d 道)**: %s ★\n"
            "⇒ ★**边界**: 零写板 · 零落表 · 不许改落表台账本体 (只读) · 不许动别域的闸 · 不许放宽 fail-closed 三条 · 零外发 · 不替老板拍板 · 不自签 issue_log ★" % (fn, n, files)))
        out.append("  dispatched_at: null")
        out.append("  task_brief: %s" % q(open(os.path.join(HERE, "dispatch_briefs", fn), encoding="utf-8").read()))
        out.append("")
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(out) + "\n"
    shutil.copy2(LOG, LOG + ".bak_20261117_1845_main_open296_297_298")
    open(LOG, "w", encoding="utf-8").write(text)

    after = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    amap = {it["id"]: it for it in after.get("issues", [])}
    ok = True
    for iid, it in bmap.items():
        a = amap.get(iid, {})
        for k, v in it.items():
            if a.get(k) != v:
                print("❌", iid, k)
                ok = False
    for iid, owner, dom, files, agent, fn in NEW_ISSUES:
        it = amap[iid]
        print("  %s -> %s owner=%s gates=%d brief=%d B" % (iid, it["status"], it["owner"], len(files.split("<br>")), len(it.get("task_brief") or "")))
    print("  其余 issue 逐字相同 =", ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
