#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-316 · 差集对账脚本 (mech-lead) —— ★只读★

作用: 把 §4 的「结构侧同批件清单」与「HW 侧重出清单」按【同一个件/依赖/顺序口径】
      逐条对账, 输出三类差集 (D-1 口径不一样 / D-2 只在 MECH 侧 / D-3 只在 HW 侧)
      + D-4 依赖顺序打架。

★边界: 只读。零写板 · 零落表 · 零改闸 · 零改既有文档正文。
★取数: 36 档表的读数一律 import MECH/board_frame_feasibility.py (零自造零漂移)。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "MECH"))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "bff", os.path.join(ROOT, "MECH", "board_frame_feasibility.py")
)
bff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bff)

OUT = []
def p(s=""):
    OUT.append(s)
    print(s)

# ---------------------------------------------------------------- 1. 36 档表取数 (唯一数据源)
p("=" * 100)
p("[1] 36 档表的现读数 (来源: MECH/board_frame_feasibility.py --json, 阈值只读 service_port_check.py BASE/TOL/CRIT)")
p("=" * 100)
rows = bff.all_rows()
frames = bff.FRAMES

for f in frames:
    p(f"  帧 {f['fid']:<10} {f['name']:<34} {f['pcb_l']}×{f['pcb_w']} · native {f['native_layers']}层/{f['native_thk']}mm "
      f"· pinset_applicable={f['pinset_applicable']}")

p("")
p("  关键: 三个选项的【现役档】(native) 逐项读数 ——")
p("  %-10s %-6s %-6s %-8s %-9s %-9s %-8s %-8s %-8s %-9s %-8s" %
  ("frame", "thk", "cavity", "cav_marg", "v_margin", "v_worst", "l_margin", "holes", "p2_gap", "weight_g", "can_open"))
native = {}
for r in rows:
    native.setdefault(r["frame_id"], []).append(r)
for fid, lst in native.items():
    for r in lst:
        if r.get("native"):
            p("  %-10s %-6s %-6.2f %-8.2f %-9.2f %-9.2f %-8.2f %-8s %-8.2f %-9.3f %-8s" %
              (fid, r["thk"], r["cavity"], r["cavity_margin"], r["v_margin"], r["v_worst"],
               r["l_margin"], "OK" if r["holes"]["all_fit"] else "NG", r["p5"]["p2_gap"],
               r["weight_g"], "YES" if r["can_open"] else "NO"))
            p("      判红原因: %s" % (r["red_reasons"] or ["(无)"]))

p("")
p("  板重占比 (分母 = MECH/service_port_check.py BASE mass_total_lo/hi):")
lo = bff.BASE["mass_total_lo"]
hi = bff.BASE["mass_total_hi"]
p(f"      分母: {lo} ~ {hi} g")
for r in rows:
    if r.get("native"):
        p(f"      {r['frame_id']:<10} {r['weight_g']:.3f} g => 占整机 {r['weight_pct_lo']:.1f}% ~ {r['weight_pct_hi']:.1f}%")

p("")
p("  ★开口坐标在 36 档里是【帧无关】的 (三套框每一行都贴同一组) ⇒ 它是套A(F30A)帧的数:")
opens = set()
for r in rows:
    opens.add((round(r["open_x"][0], 3), round(r["open_x"][1], 3),
               round(r["open_y"][0], 3), round(r["open_y"][1], 3)))
for o in sorted(opens):
    p(f"      open_x {o[0]}..{o[1]} × open_y {o[2]}..{o[3]}   (共 {len(opens)} 组)")
for fid in ("B160x100", "F30A", "P60x15"):
    for r in rows:
        if r["frame_id"] == fid and r.get("native"):
            p(f"      {fid}: 开口落点距板端 {r['open_end_margin_x']:.2f} mm · open_at_board_end={r['open_at_board_end']}")
            break

# ---------------------------------------------------------------- 2. HW 侧清单 (只读解析)
p("")
p("=" * 100)
p("[2] HW 侧清单 (只读解析 HW/PCB/ONETRIP_REISSUE_MANIFEST.md)")
p("=" * 100)
hw_path = "HW/PCB/ONETRIP_REISSUE_MANIFEST.md"
hw_txt = open(hw_path, encoding="utf-8").read()
hw_main_rows = re.findall(r"^\| ★\*\*(\d+)\*\* ★ \| ★\*\*([^*]+)\*\* ★ \|", hw_txt, re.M)
p(f"  §3-1 主表行数 = {len(hw_main_rows)}")
for num, name in hw_main_rows:
    p(f"    #{num:<3} {name.strip()[:70]}")
p("  §4-4 归属表里 mech 那几行 (逐字):")
for line in hw_txt.splitlines():
    if line.strip().startswith("| ★**mech** ★") or line.strip().startswith("| ★**hw** ★") \
       or line.strip().startswith("| ★**sw** ★") or line.strip().startswith("| ★**main** ★"):
        p("    " + line.strip()[:260])
p("  §4-3 「同趟出」清单条数 = %d" % len(re.findall(r"^\| ★\*\*(\d+)\*\* ★ \| ★\*\*[^*]+", hw_txt.split("★4-3")[1], re.M)))

# ---------------------------------------------------------------- 3. MECH 侧清单 (本单 §3)
p("")
p("=" * 100)
p("[3] MECH 侧同批件清单 (本单 §3 · 逐件: 必须出 / 可后置 + 顺序位)")
p("=" * 100)
MECH_ITEMS = [
    # (id, 名称, 归属, 上游, 顺序位, 必须出?)
    ("M-01", "U-1 冻结记录 (帧 id + 板厚 + 层数 + 孔位口径)", "mech→main", "老板拍板", "⓪", True),
    ("M-02", "板框几何真源 BOARD_GEOM_30MM §1/§3", "mech", "U-1", "①", True),
    ("M-03", "骨架截面重做 (BOARD_GEOM_30MM §5 第2条)", "mech", "U-1", "①", True),
    ("M-04", "石墨片覆盖方案 (§5 第3条)", "mech", "U-1", "①", True),
    ("M-05", "板重账落 MECH_BUDGET §3 W5", "mech", "U-1", "①", True),
    ("M-05b", "W5 拆 FR4 行 + 元器件行 (口径由 main/hw 裁)", "mech+main", "U-1+BOM", "①", True),
    ("M-06", "三条开口认领句 MECHAIMS §1", "mech", "U-1", "②", True),
    ("M-07", "座体 6 组落位认领句 MECHAIMS §2", "mech", "U-1+原理图", "②", True),
    ("M-08", "S6 20 落位 × MECH 保留区 MECHAIMS §3", "mech", "U-1", "②", True),
    ("M-09", "开口几何真源 S6_WORKPACKET §1~§5", "mech", "U-1", "②", True),
    ("M-10", "帧口径机器块 S6_FRAME_CALIBER §1.2", "mech", "U-1", "②", True),
    ("M-11", "service_port_check.py 6 个帧相关常量", "mech", "U-1", "③", True),
    ("M-12", "check_onepass_struct_crosscheck.py FRAME 硬编码", "mech", "U-1", "③", True),
    ("M-13", "check_onepass_mech_sync.py 每条认领句帧标", "mech", "U-1", "③", True),
    ("M-14", "check_mech_verdict_freshness.py CANON 句", "mech", "U-1", "③", True),
    ("M-15", "jd_y0_feasibility + board_port_opening_s6_check 基准", "mech", "U-1", "③", True),
    ("M-16", "打印包改版五件几何", "mech", "U-1", "④", True),
    ("M-17", "治具/夹具几何 (套A)", "mech", "U-1", "④", True),
    ("M-18", "打印件实物 B1~B4", "mech", "U-1+ISS-040", "⑤", False),
    ("M-19", "骨架实物 / 石墨片裁切", "mech", "M-03/M-04", "⑤", False),
    ("M-20", "治具实物", "mech", "M-17", "⑤", False),
    ("M-21", "MEASURE_CHECKLIST §J 实测回填", "mech", "M-18", "⑤", False),
    ("M-22", "Type-C 第三档试样实测", "mech", "M-18", "⑤", False),
    ("M-23", "measurements.yaml M-PRINT/M-FIT/M-WEIGHT", "mech", "M-18", "⑤", False),
    ("M-24", "石墨/隔热垫/导热垫实测厚度回填", "mech", "M-19", "⑤", False),
]
must = [x for x in MECH_ITEMS if x[5]]
post = [x for x in MECH_ITEMS if not x[5]]
p(f"  必须同批出 = {len(must)} 件 · 可后置 = {len(post)} 件 · 合计 {len(MECH_ITEMS)} 件")
for x in must:
    p(f"    [必须] {x[0]:<7} {x[1][:56]:<58} 依赖={x[3]:<14} 序={x[4]}")
for x in post:
    p(f"    [可后置] {x[0]:<5} {x[1][:56]:<58} 依赖={x[3]:<14} 序={x[4]}")

# ---------------------------------------------------------------- 4. 差集
p("")
p("=" * 100)
p("[4] 交叉对账差集 (★这就是「板改第二次」的风险清单★)")
p("=" * 100)
D1 = [
    ("D-1-1", "mech 在这一趟的归属",
     "ONETRIP §4-4: mech = 不占本趟产物, 只关心 board_port_opening_s6_check.py 一个脚本",
     "MECH 侧实际 18 件要同批出 (含 6 道几何闸锚点 + 三条开口 + 座体6组 + S6 20落位 + 骨架 + 板重 + 打印包五件)",
     "HW 侧漏记约 17 件 ⇒ MECH 工作量被低估"),
    ("D-1-2", "HW 侧作业包里的【两处过期板宽】 (★不是两套口径并存★)",
     "HW 作业包 §7 P7 C1 行内 L659: 「板宽 15mm 是结构约束 (镜腿宽度)」 + §7 排序依据第 3 条 L668: 「C1/C2 的真实战场是【产品板 (60×15)】」 ⇒ ★这两行是 ISS-118/130 (老板 2026-10-29 19:16) 之前的旧板宽★",
     "MECH 现行口径 = 板宽 30.00 / 板长 60.00 / 板厚 1.00 (6 层) (MECH/BOARD_GEOM_30MM.md §1) ⇒ 15 是作废板宽",
     "★归类: 过期行 (待订正), 不是两边口径打架★ ⇒ 订正动作 = main 在 HW 域改那两行 (ISS-310 §D-4 已给逐字改法) ⇒ 老板照那两行拍会拍错 (把 30 缩回 15 = 推翻老板 10-29)",
     "★附: MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md §4.1 第 1/2 行引的旧行号 :301/:310 已漂为 L659/L668 ⇒ 一并订正 (MECH 域文件, 本单零改, 只回报)★"),
    ("D-1-3", "板重",
     "HW 侧无板重这个数",
     "MECH_BUDGET §3 W5 = 50×12×0.8 / 5-7 g (板框与重量两个数都过期); verify_budget.WEIGHT_ITEMS 同为 5.0-7.0",
     "现行 F30A FR4 净重 3.33 g ⇒ 差 1.67~3.67 g"),
    ("D-1-4", "MECH 域自己的【同一处过期字】 (★不是两边对立★)",
     "BOARD_FRAME_CALIBER §1.1 已登记「MECH 权威表主控没跟着换」(RK3576×14 / RK3572×0)",
     "MECH_BUDGET §1.3 主表 M1 行 = 60 × 15 × 1.0 / 1.67 cc ⇒ MECH 自己这边也挂着作废板宽 15",
     "★归类: 过期行 (待订正), 与 D-1-2 同一个病在自己这边★ ⇒ 交 need 给 main, 本单零改"),
    ("D-1-5", "开口坐标 (三套数)",
     "HW 作业包 §1 C-OPEN-1/2: 调试口 137.850..148.050 × 54.300..58.900 (帧 B160x100); UART 13.790..23.990 × 66.300..70.900 (帧 B160x100)",
     "36 档表 open_x/open_y = 49.21..59.41 × 7.835..12.435 (三框共用 ⇒ 是 F30A 帧的数); ISS-271/313 jd 区间 [1.665,11.730]/[48.290,51.090]/X[47.00,60.00] (F30A)",
     "同一组开口 3 套数 ⇒ 照任何一套开都会开错"),
    ("D-1-6", "板重占比的分母",
     "HW 侧不产这个数",
     "两套分母并存: service_port_check BASE mass_total_lo/hi = 48.90/72.80 vs MECH_BUDGET §3 合计 49.58-74.16 (315档) ⇒ 差 0.68/1.36 g",
     "同一占比在两个文件里算出两个数 ⇒ 受保护闸与被校核文档不同步 ⇒ 交 need"),
    ("D-1-7", "「板只改一次」的作用对象",
     "HW 侧: 板 md5 只允许变一次 ⇒ 约束现役板 B160x100 的文件",
     "MECH 侧 (ISS-310 §C-2 B3): 换框 ≠ 板改第二次 ⇒ 约束产品板这条线上板 md5 只出一次",
     "同一句老板的话两边约束对象不同 ⇒ 拍板页必须写死"),
]
D2 = [
    ("D-2-1", "M-01 U-1 冻结判据本身", "HW 只把它排在「老板 P7」, 没有判据", "拍完没法机器判「冻结了没有」⇒ 板 md5 第二次变"),
    ("D-2-2", "M-06/M-09 三条开口几何真源 (MECH 侧 3 页)", "HW 只把坐标【抄】进作业包 §3-S6 ⇒ 抄件不是真源", "帧一改 ⇒ HW 抄件与 MECH 真源分叉 ⇒ 防漂闸红"),
    ("D-2-3", "M-07 座体 6 组落位认领句", "HW 只写了罩子, 没有 6 组落位认领", "座体占位与板上落位对不上 ⇒ 探针/连接器够不着"),
    ("D-2-4", "M-15 jd_y0/jd_x0 合法区间 + jd_y0_feasibility.py", "HW 清单没有这个判据", "焊盘阵列 Y 起点没人判 ⇒ 开口 Y 无基准"),
    ("D-2-5", "M-11~M-15 MECH 6 道几何闸的常量锚点", "HW 的 9 道钉板 md5 闸只钉板 md5, 不钉 MECH 几何常量 ⇒ 两套基线", "板一改 MECH 侧 6 道闸可能红, 而 HW 清单里没这一项 ⇒ 收尾清单不完整"),
    ("D-2-6", "M-03/M-04 骨架截面 + 石墨覆盖", "HW 清单没有「骨架」这个件 (它不是板的产物)", "30mm 下全部候选超预算 4.08 g/对 vs 3 g + 石墨 2.16 g/对 > W11 2 g ⇒ 板画出来装不进骨架 ⇒ 板改第二次"),
    ("D-2-7", "M-16/M-17 打印包改版五件 + 治具", "HW 清单完全没有「打印包/治具」", "开口几何定了但没实物 ⇒ 产线装前压针跑不通; 治具基准不同批 ⇒ 板装不进笼"),
    ("D-2-8", "M-05 板重账 (MECH_BUDGET §3 W5 + verify_budget)", "HW 不产 MECH 的重量表", "整机质量预算按旧板算 ⇒ 重量账不平"),
    ("D-2-9", "电芯采购口径 (ICP422339PR vs ICP582035PR-01)", "不在任何板那一趟清单里 (采购侧的事)", "照现型号买 ⇒ 厚 6.40 而非 4.60 ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm ⇒ 比任何文档订正都贵"),
]
D3 = [
    ("D-3-1", "网表 + 脚表 (①条件步)", "网表/脚表是 hw 地界, 本单零落表", "M-07 座体落位依赖网表位号 ⇒ 改名 (_1 后缀) 时 MECH 认领句要同步改"),
    ("D-3-2", "原理图 11 页 + .kicad_pro (③)", "原理图是 hw 地界", "J_DEBUG 脚数 (1×4 vs 模型 2×5) 来自原理图 ⇒ 脚数不定 ⇒ 开口 X/Y 全不定"),
    ("D-3-3", "BOM (⑤ 板之后)", "BOM 是 hw 地界", "M-05 重量账要与 BOM 对表; ISS-311 地雷2: 板侧 ref 改名 ⇒ gen_bom.py 按精确 ref 读板静默失效 ⇒ MECH 的器件重量来源链断"),
    ("D-3-4", "投产包 74 件 (⑥)", "MECH 不产", "M-16/M-17 的打印件与治具【不在 74 件里】⇒ 投产包齐了不等于装配能跑"),
    ("D-3-5", "落表台账 (⑦ main)", "main 地界", "U-1 冻结记录与落表台账是两本账 ⇒ 必须写清 U-1 记录落在哪本"),
    ("D-3-6", "旧 md5 引用点清理 (主表 #25 全仓 grep)", "MECH 不产", "9 道钉板闸里有 2 道在 MECH 域 ⇒ #25 归属口径打架 (小)"),
]
D4 = [
    ("D-4-1", "U-1 在不在硬顺序第一位",
     "HW 硬顺序 = 网表→原理图→板→BOM→投产包; 主表第 1 行是网表, 没有「板框冻结」",
     "MECH 顺序 = U-1→认领句/开口几何/座体/jd区间→板S6→MECH 6闸重锚→打印包五件→实物",
     "★最贵的一条★: 按 HW 顺序 S1~S8 可在 U-1 未拍时开工 ⇒ 板 md5 先变一次 ⇒ 拍完框再变一次 ⇒ 破功"),
    ("D-4-2", "MECH 侧 17 件在归属表里的位置",
     "归属表写 mech = 不占本趟产物 ⇒ 全部排在板那一趟之后",
     "M-06/M-07/M-08 是 S6 的【输入】⇒ 顺序倒置",
     "要么板先按旧坐标画 (拍完框要重画 = 板改第二次), 要么认领句先改 (与 HW 抄件分叉) ⇒ 二选一, 不能各留一半"),
    ("D-4-3", "打印包与板框的关系",
     "HW 清单里没有打印包 ⇒ 无冲突记录",
     "M-16/M-17 吃开口坐标 + 套A孔位 ⇒ 吃 U-1",
     "选 F30A ⇒ 打印包本来就是 60×30 套A ⇒ 不用重生成 (反而对齐); 选 B160x100 ⇒ 整包作废 ⇒ U-1 一拍, 工作量差一个量级"),
    ("D-4-4", "板重账与板的下游",
     "HW: 板→BOM→投产包",
     "MECH: U-1→板重→MECH_BUDGET §3 合计→verify_budget.py (门禁锚点 DOC_WEIGHT)",
     "板重一改脚本必须同批改否则门禁红 ⇒ 与 §5-2 的 +0.73g 订正是同一类结构"),
]
for tag, lst in (("D-1 两边都提到但口径不一样", D1),
                 ("D-2 只在 MECH 侧出现", D2),
                 ("D-3 只在 HW 侧出现", D3),
                 ("D-4 依赖顺序打架", D4)):
    p(f"  --- {tag} ({len(lst)} 条) ---")
    for row in lst:
        p(f"    {row[0]:<8} {row[1]}")
        for extra in row[2:]:
            p(f"             · {extra}")
p("")
p(f"  ★差集合计 = {len(D1)} + {len(D2)} + {len(D3)} + {len(D4)} = {len(D1)+len(D2)+len(D3)+len(D4)} 条")
p("  ★分类说明: D-1 里 D-1-2 与 D-1-4 严格说是【过期行 (待订正)】, 不是【两边口径打架】")
p("  ★⇒ 真正的「两边口径不一致」= %d 条 + 2 条过期行 = %d 条" % (len(D1) - 2, len(D1)))
p("  ★★读差集的一条纪律 (ISS-310 点名过): HW 作业包 L659/L668 的「板宽 15mm / 产品板 (60×15)」是")
p("     【作废板宽】, 不是「HW 侧在用 P60x15 那一套框」⇒ ★别把它当成真的口径打架★")

# ---------------------------------------------------------------- 5. 依赖排序出处
p("")
p("=" * 100)
p("[5] 依赖排序的依据出处 (逐条, 只读实读)")
p("=" * 100)
EVID = [
    ("HW 硬顺序", "HW/PCB/ONETRIP_REISSUE_MANIFEST.md §4-2"),
    ("HW 依赖图", "HW/PCB/ONETRIP_REISSUE_MANIFEST.md §4-1"),
    ("HW 同趟出清单", "HW/PCB/ONETRIP_REISSUE_MANIFEST.md §4-3"),
    ("HW 归属表", "HW/PCB/ONETRIP_REISSUE_MANIFEST.md §4-4"),
    ("板 md5 只允许变一次 (变更次数 ≤ 1)", "HW/PCB/BOARD_ONEPASS_WORKPACKET.md §6.2 / BOARD_ONEPASS_COMMIT_ORDER.md"),
    ("若在 S10 之后才拍 ⇒ 板 md5 第二次变 ⇒ 只改一次破功", "HW/PCB/BOARD_ONEPASS_WORKPACKET.md §7 排序依据"),
    ("板框三选一与两套口径的并列", "MECH/BOARD_FRAME_DECISION_INPUT.md §A / §D-3"),
    ("MECH 6 道几何闸的常量锚点", "MECH/BOARD_FRAME_DECISION_INPUT.md §B-4 + MECH/BOARD_GEOM_30MM.md §6b"),
    ("8 项结构侧在册值 (板长/宽/厚/孔位/净空/开口/三链/md5)", "MECH/MECH_NEEDS_TRIAGE.md §7.1"),
    ("33 条与板那一趟直接相关的待答输入", "MECH/MECH_NEEDS_TRIAGE.md §7"),
    ("冻结闸 need key proto_pcb_freeze_gate", "MECH/MECH_NEEDS_TRIAGE.md §7.2 第 3 行 + state/fragments/mech.yaml needs_from"),
    ("ISS-027 四批 + P-2 冻结点", "HANDOFF/2026-10-29_mech-lead_原型制作计划_ISS027.md B1 结论摘要 + §B5 P-2 + MECH/PROTOTYPE_PLAN.md §1.1/§5.3"),
    ("检修口打印包改版五件排 B2", "DECISIONS.md 2026-10-30 项目总工条目 (引 ISS-092 I-7)"),
    ("帧 id 唯一权威表 + SoM 承载区占位", "HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES + §3"),
]
for name, src in EVID:
    p(f"    {name:<52} ← {src}")

# ---------------------------------------------------------------- 6. 零写板双证
p("")
p("=" * 100)
p("[6] 零写板双证 (md5 + mtime)")
p("=" * 100)
import subprocess
for cmd in (["md5sum", "HW/PCB/demo_mainboard.kicad_pcb",
                     "MECH/service_port_check.py", "MECH/board_frame_feasibility.py"],
            ["stat", "-c", "%y %n", "HW/PCB/demo_mainboard.kicad_pcb"]):
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    for line in out.strip().splitlines():
        p("    " + line)

with open("logs/iss316/diff_reconciliation_raw.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
p("")
p("★原始输出已落 logs/iss316/diff_reconciliation_raw.txt")
