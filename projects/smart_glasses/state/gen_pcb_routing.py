#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pcb_routing.py —— ★通用网格路由器 (A* / Lee) + 差分对捆绑 + 电源粗铜 + GND 平面

★★ 为什么必须有这个模块 (而不是手拉线):
  板子是**脚本生成**的 (state/gen_pcb_netlist_board.py) ⇒ 手拉的线下次重生成就没了
  ⇒ ★布线必须**落进生成器** ⇒ 本模块就是那个"可复用的布线器"。

★★ 路由器规格 (★来自 HW/PCB/LAYOUT_RULES.md + STACKUP.md):
  · 网格步长        0.25 mm (8 邻域 ⇒ 45°/90° 走线)
  · 信号层          L1 (F.Cu) 优先 → L3 (In2.Cu) → L5 (In4.Cu)
                   ★**L2 (In1.Cu) 与 L6 (B.Cu) 是完整 GND 平面 ⇒ 不许走信号**
                     (STACKUP.md: L1 信号/L2 GND/L3 信号/L4 电源/L5 信号/L6 GND)
  · 换层            只能相邻信号层换 (F.Cu↔In2.Cu / In2.Cu↔In4.Cu)
                   ⇒ 过孔只跨一层平面 (L2 或 L4), **不跨 GND+电源双平面** (回流路径不断)
  · 线宽            信号 0.25mm / 电源 0.5mm (LAYOUT_RULES: SOM 输入 ≥2A ⇒ ≥0.5mm)
  · 间距            KiCad 默认 0.2mm (本路由器按 0.2mm 建 keepout)
  · 过孔            0.6mm 盘 / 0.3mm 钻 (环宽 0.15mm = KiCad 最小环宽)
  · 差分对          先布 P, 再在 P 的走廊里布 N (软代价拉近 ⇒ 同层同间距) + 长度配平

★ 坐标系: 全程用 KiCad 原生坐标 (内部单位 1e-6 mm, **y 向下**) ⇒ 不用做 y 取负
"""

import heapq
import math
import os
from collections import defaultdict
import collections

import pcbnew

MM = 1e6

# ------------------------------------------------------------------ 常量
GRID = 0.25            # mm 网格步长
# ★★★**★2026-11-10 03:3x 【★GRID 改成 env 旋钮 (★默认关 ⇒ 逐位不变★)】★★★ ★★★
#   ★**为什么**: ★**实测 (★`state/probe_escape_feasibility.py`★) ⇒ v76ru 终板的 70 个未连接端点
#     ★★**在 W=0.20 与 W=0.15 下【全部物理可行】⇒ ⇒ ⇒ "等板厂"不成立 ⇒ ⇒ ⇒ 【瓶颈 100% 在 A*】**
#     ⇒ ★**⇒ 而 `GRID=0.25` ⇒ 0.4mm pitch 的 BTB 区只有 1~2 格 ⇒ ⇒ ⇒ 【密集区没有足够细的格子可走】**
#       ⇒ ★★**⇒ 这是【最可能的真凶】⇒ ⇒ ⇒ 所以它必须能做成单变量臂 ⇒ ⇒ ⇒ 以前它是写死常量 ⇒ 做不了** ★★★★
#   ★**用法**: ★**`PCB_GRID=0.125`** ⇒ ★**网格步长 0.125mm (★格子数 ×4 ⇒ 内存/时间 ×4 左右★)**
#   ★**默认 = 0.25 ⇒ 逐位不变** ★★
GRID = float(os.environ.get("PCB_GRID", "0.25"))
if abs(GRID - 0.25) > 1e-9:
    print("  [路由] ★★网格步长 (env 覆盖): %.3f mm (★默认 0.25★)" % GRID)
# ★★2026-11-05 23:2x **v41: 通孔净距禁区按真实孔心算 (env 门控, 默认关)**
#   ★**根因**: 旧算法用"含孔心那一格"的**格心**当圆心 ⇒ 孔偏格心 δ 时禁区整体偏 δ
#     ⇒ 实测 v36_S 的 DRC: 孔 (85.35,9.60) 偏格心 (0.10,0.10) ⇒ 走线端点离真实孔心
#       **0.5657mm (< 0.625 违规)** 却被按格心判 = 0.7071mm ⇒ **放行**
#   ★**默认 0** ⇒ 与 v31/v36/v37/v39/v40 逐位一致
VIA_HALO_EXACT = os.environ.get("PCB_VIA_HALO_EXACT", "0") == "1"
# ★★2026-11-06 00:3x **v44: `PCB_VIA_HALO_CENTER=1`** ---
#   ★**圆心改用真实孔心, 但半径不变 (不加对角余量)**
#   ★**为什么**: 旧版圆心 = "含孔那格的格心" ⇒ 禁区整体偏 delta (<=0.177mm)
#     ⇒ 走线端点离真实孔心 0.5657 (<0.625 违规) 却按格心判 0.7071 ⇒ 放行 ⇒ DRC 漏网
#   ★**为什么不直接用 PCB_VIA_HALO_EXACT (加 g*sqrt(2)/2)**: 实测多封 11 格/孔
#     ⇒ 未通 57 -> 63 (净亏) ⇒ ★**改圆心不扩半径 => 封格数几乎不变**
#   ★**默认关** ⇒ 行为与旧版逐位一致
VIA_HALO_CENTER = os.environ.get("PCB_VIA_HALO_CENTER", "0") == "1"

CLEAR = 0.20           # mm 铜间距 (KiCad 默认)
# ★★2026-11-05 07:45 **做成可调** (实验臂用)
#   ★理论下限: 栅格 0.25mm ⇒ 半格 0.125 ⇒ 0.125 就够 (当前 0.20 偏保守 ⇒ 多阻 ~18% 面积)
#   ★**改小会放松净距保护 ⇒ 必须盯 DRC** ⇒ 只在实验臂里试, 验过 DRC 才准进正式轮
HALO_MARGIN = float(os.environ.get("PCB_HALO_MARGIN", "0.20"))
                        # ★★2026-11-04 22:35 项目总工改: 0.07 → 0.20 —— 上一轮 DRC 实测净距 0.175 < 要求 0.200
                        #   ⇒ ★**半格量化损失没被补回来** ⇒ 余量必须 ≥ 半格 (0.125) + 富余 ⇒ 0.20
# ★★2026-11-05 18:55 **过孔 halo 单独用精确几何** (★v32 单变量) —— ★**实测根因**
#   ★**现象**: `CONN_CAM` 的 GND 下拉孔落在**每个 GND 焊盘正下方 1.2mm**
#     (x=80.4/81.9/83.4/84.9/**86.4**/**87.9**, y=52.60) ⇒ 与 0.5mm pitch 的 CSI 脚**交错成栅栏**
#     ⇒ ★**10 条 CSI "第二跳" (AC电容→CONN_CAM) 全堵在这** (含只差 6.4mm 的 CSI_D0_CK_P)
#   ★**旧半径** = CLEAR 0.20 + VIA_DIA/2 0.30 + W_CLS/2 0.125 + HALO_MARGIN 0.20 = **0.825mm**
#     ⇒ 栅栏之间唯一通道 (格 x=87.125, 距孔心 0.775) 被 halo 判死 ⇒ ★**通道焊死**
#   ★**真实 DRC 需要的半径** = VIA_DIA/2 0.30 + 走线半宽 0.125 + CLEAR 0.20 = **0.625mm**
#     ⇒ 0.775 > 0.625 ⇒ ★**通道本来就合法** ⇒ ★**halo 多算了 HALO_MARGIN (0.20)**
#   ★**为什么安全**: 栅格 0.25mm, 标记用的是"格心到孔心 ≤ rr"的圆内测试 (不是 ceil)
#     ⇒ rr=0.625 时标记格 ≤0.559mm ⇒ 通道格 87.125 (0.775mm) 放行
#     ⇒ 实算净距 = 0.775 - 0.30(孔盘半径) - 0.125(线半宽) = **0.35mm ≥ 0.20 ✔**
#   ★**默认仍是 0.20** ⇒ 与 v31_Q **逐位可复现** ⇒ 只在实验臂用 `PCB_VIA_HALO_MARGIN=0.0` 打开
#   ★**与已有逻辑一致**: `_via_exact_ok` / `_via_site_ok` 早就改成"精确几何"了 ⇒ ★**这里只是补齐**
VIA_HALO_MARGIN = float(os.environ.get("PCB_VIA_HALO_MARGIN", str(HALO_MARGIN)))
# ★★2026-11-05 19:15 **连接器差分脚"逃逸走廊"禁放 GND 下拉孔** (★v33_S 单变量, 默认关)
#   ★**实测根因 (承 v32 的发现)**: `CONN_CAM` 的 GND 下拉孔落在**每个 GND 焊盘正下方 1.2mm**
#     (x=80.4/81.9/83.4/84.9/86.4/87.9, y=52.60) ⇒ ★**把连接器下方 4.3mm 的空带
#     (y 51.85→56.15, x 78..95) 切成一条条 0.75mm 的缝** ⇒ 差分脚逃不出去
#   ★**规则**: 对指定连接器 (如 CONN_CAM), 它的 GND 焊盘的**下拉孔心到焊盘行的垂直距离**
#     必须 ≥ MIN ⇒ 孔只能往连接器**上方**远躲 ⇒ ★**逃逸走廊整条让开**
#   ★**为什么对 CONN_LIGHT 不适用**: 它上下两侧都被**器件** (电容行 / TP / 串阻) 堵死
#     ⇒ 挪孔解决不了 ⇒ ★**DSI 侧要另走摆放臂**
#   ★**用法**: `PCB_CONN_GND_ESCAPE="CONN_CAM:4.0"` (多组用 `;` 分隔, 形如 `REF:MIN`)
#   ★**默认空 ⇒ 与 v31/v32 逐位一致**
CONN_GND_ESC = {}
# ★★2026-11-06 01:2x **v46: 逃逸规则加"方向"** (env 门控, 默认 ANY => 逐位一致)
#   ★**为什么**: 旧规则是对称的 `abs(via_y - pad_y) >= MIN` ⇒ ★**无法表达"只能往某一边躲"**
#     ⇒ 对 CONN_LIGHT 而言: 它的差分脚是**往上逃** (TP 行 y=55.20 / AC 电容行 y=58.60 都在上方,
#       SoM P4 (y=50.61..54.39) 挡住垂直通路) ⇒ **上方的 GND 孔才是拦路的, 下方的无害**
#     ⇒ ★**实测**: v45 用对称规则 (CONN_LIGHT:2.0) ⇒ 上排孔被赶到**更上面** (y<=58.15)
#       ⇒ 走廊更堵 ⇒ ★**CSI_D0_CK 从 ok=True 变成 ok=False** (打地鼠)
#   ★**新语法**: `PCB_CONN_GND_ESCAPE="REF:MIN:DOWN"` (DOWN = 孔必须往 y 增大方向躲)
#     · UP   = 孔必须往 y 减小方向躲
#     · ANY  = 旧的对称规则 (默认 ⇒ 逐位一致)
# ★★2026-11-06 01:5x **v47: 同排相邻 GND 焊盘"合并下拉"** (env 门控, 默认关 ⇒ 逐位一致)
#   ★**根因 (机器读)**: CONN_LIGHT 有 8 个 GND 焊盘, 其中 `.21/.20` 相距仅 **0.50mm**
#     ⇒ 而过孔中心距下限 0.58mm ⇒ ★**同排相邻两个焊盘放不下各自的孔**
#     ⇒ 每个焊盘被迫往外扩 ⇒ 扩成 0.75mm 间距的一排 ⇒ ★**"栅栏"成形**
#     ⇒ 实测 15 个孔 = 9 个"走一段线再落孔"(本体) + 3+1+2 个同网缝合链
#   ★**为什么改落位规则治不了 (实测)**: v45 (对称 MIN) 与 v46 (DOWN 方向) ★**都**把
#     `CSI_D0_CK_P` 从 ok=True 打成 ok=False ⇒ ★**打地鼠** ⇒ 落位自由度只有 1 格
#   ★**正解 (本开关)**: ★**先把同排相邻的 GND 焊盘短接成一条链, 只在这条链的一端落一个孔**
#     ⇒ 8 个孔变 1~2 个 ⇒ ★**栅栏从根上消失** ⇒ 逃逸走廊整条让开
#     ⇒ ★**不是"挪孔", 是"少落孔"** ⇒ ★**不会打地鼠**
# ★★2026-11-06 01:1x **v48: route_net 的"多目标重试"** (env 门控, 默认关 ⇒ 逐位一致)
#   ★**根因**: `route_net` 只把"最近的已连焊盘"当唯一目标 ⇒ 所有降级重试目标都一样
#     ⇒ ★**"换另一个已连焊盘"这条退路不存在** ⇒ 一条腿被堵 ⇒ 整条腿永久无铜
#   ★**实测**: 官方板 57 条里 19 条是 "Pad↔Track", Δ 中位 **27.849mm** ⇒ 整条腿缺失
#   ★**修法**: 最近的走不通 ⇒ ★**按距离依次试其它已连焊盘** (纯多试目标, 不改几何规则)
# ★★2026-11-06 01:2x **v49: 让 rip-up & reroute 真正能跑** (env 门控, 默认关)
#   ★**根因**: `route_net` 结尾无条件 `routed.add(net)` ⇒ ★**失败网也进 routed**
#     ⇒ `ripup_and_reroute` 第一行 `if net in self.routed: continue` ⇒ ★**19 个失败网一次都没试**
#     ⇒ ★实测日志无任何 per-net 行 ⇒ 证明是"早期 continue"而非"试了都失败"
#   ★**修法**: ★**只在成功时才记进 `routed_ok`** ⇒ rip-up 的守卫改判 `routed_ok`
#   ★**顺带**: 失败网不再被后续"跳过已布网"的逻辑误判 ⇒ ★**它还有被再试的机会**
RIPUP_ALIVE = os.environ.get("PCB_RIPUP_ALIVE", "0") == "1"
# ★★2026-11-06 02:4x (v50 概念): 板边验收严格模式
#   —— 缝合路径/_emit_path/commit 三处补板边净距闸 (默认关, 老行为可复现)
EDGE_STRICT = os.environ.get("PCB_EDGE_STRICT", "0") == "1"
# ★★★★★★2026-11-10 09:2x 【★"蛇形配平不许出板"闸 (★env 门控 `PCB_MEANDER_EDGE`, ★默认关 ⇒ 逐位不变★)★★
#   ★**为什么要有 (★2026-11-10 09:2x 实测, ★不是猜★)**:
#     ★**实测 (★四条臂 v76s8/v76s9/v76s10/v76b1 的终板★)**: ★**100% 的 `copper_edge_clearance`
#       违规都来自【蛇形配平 (meander) 的凸起段】** ⇒ ★★**⇒ 这是所有臂 DRC≠0 的头号杀手** ★★
#       · v76s8: 25 条违规 ⇒ ★**23 条**在蛇形组内 (★另 2 条是同一凸起的外侧段★)
#       · v76s9: 19 ⇒ 16 · v76s10: 20 ⇒ 16 · v76b1: 4 ⇒ 4  ⇒ ★★**四臂合计 68 条违规, 100% 归因蛇形**★★
#     ★**根因 (★代码级★)**: ★**蛇形是【离网格的斜线】⇒ 栅格 halo/edge_d 全都管不到它**
#       ⇒ `_geom_clear()` (★蛇形唯一的几何闸★) ★**只查【别的网的铜】, 压根没查【板边】★★
#       ⇒ ★★**⇒ 凸起顶点可以放到板外 (★实测 y=-1.2mm★) 或贴着板边 (★0.075mm★) ⇒ DRC 报 `copper_edge_clearance`** ★★
#     ★**为什么不能靠"落板后剔铜"**: ★**实测剔掉蛇形段 ⇒ DRC 29→69 (★反而更烂, ★因为剔中间段会留悬空端★)**
#       ⇒ ★★**⇒ 必须在【落铜之前】拦住 (★`commit()` 的板边自检只数不拦, ★救不了★)** ★★
#     ★**修法**: ★**蛇形候选 4 段逐段过 `_edge_seg_ok()` (★路由器自带的真板边判据★)**
#       ⇒ ★★**⇒ 凸起出不了板 ⇒ DRC 干净 ⇒ 且【不删任何已有铜 ⇒ 不产生悬空端】** ★★
#   ★**默认值**: ★**0 (关) ⇒ 逐位不变 (★老臂可复现★)** ★★
#   ★**用法**: ★**`PCB_MEANDER_EDGE=1` (★单独开即可★)** ⇒ ★★**★【与 `PCB_EDGE_STRICT` 无关★
#     (★`PCB_EDGE_STRICT` 管的是【缝合路径】+【`_emit_path`】两处 ★⇒ ★**管不到蛇形★** ⇒ ★**两闸各管各的,
#     ★不必一起开★★)★】★★
#     ⇒ ★**实测 (★2026-11-10 12:10 ★v76me 成对臂★)**: ★**闸关 ⇒ 铜边违规 4 条; ★闸开 ⇒ 0 条;
#       总违规 6→2; ★unconnected 51→51 (★零信号代价★)** ★★ ⇒ ★**闸有效且不伤信号** ★★
MEANDER_EDGE = os.environ.get("PCB_MEANDER_EDGE", "0") == "1"
if RIPUP_ALIVE:
    print("  [路由] ★rip-up 复活: ON (失败网会真的被拆线重布)")
MULTI_GOAL = os.environ.get("PCB_MULTI_GOAL", "0") == "1"
# ★每个焊盘最多换几个目标 (防止 A* 预算被烧光)
MULTI_GOAL_MAX = int(os.environ.get("PCB_MULTI_GOAL_MAX", "4"))
if MULTI_GOAL:
    print("  [路由] ★多目标重试: ON (每脚最多换 %d 个目标)" % MULTI_GOAL_MAX)
GND_SHARE_ROW = os.environ.get("PCB_GND_SHARE_ROW", "0") == "1"
# ★合并的"同行"判据: 焊盘中心的 y 差 ≤ 该值 (mm) ⇒ 算同一排
GND_SHARE_ROW_DY = float(os.environ.get("PCB_GND_SHARE_DY", "0.35"))
# ★同一排内, x 间距 ≤ 该值的相邻焊盘算"一组" (⇒ 共用一个下拉孔)
GND_SHARE_ROW_GAP = float(os.environ.get("PCB_GND_SHARE_GAP", "1.60"))
if GND_SHARE_ROW:
    print("  [路由] ★GND 同排相邻焊盘合并下拉: ON (dy<=%.2fmm, xgap<=%.2fmm)"
          % (GND_SHARE_ROW_DY, GND_SHARE_ROW_GAP))
CONN_GND_ESC_DIR = {}
for _grp in (os.environ.get("PCB_CONN_GND_ESCAPE", "") or "").split(";"):
    _grp = _grp.strip()
    if not _grp or ":" not in _grp:
        continue
    try:
        _parts = _grp.split(":")
        _r = _parts[0].strip()
        CONN_GND_ESC[_r] = float(_parts[1])
        _d = (_parts[2].strip().upper() if len(_parts) > 2 else "ANY")
        CONN_GND_ESC_DIR[_r] = _d if _d in ("UP", "DOWN", "ANY") else "ANY"
    except Exception:
        continue
if CONN_GND_ESC:
    print("  [路由] ★连接器逃逸走廊禁放 GND 下拉孔: %s" % CONN_GND_ESC)
# ★★★★★**★2026-11-10 03:0x 【★GND 下拉孔的逃逸走廊规则被绕过 ⇒ ★修它 (env 门控)★★★★★**
#   ★**实测根因**: ★**GND 下拉孔落 `escape_stub()` 的末端 (anchor) ⇒ 而 escape_stub 不查
#     `_gnd_drop_esc_ok` ⇒ ⇒ 走廊规则只在环格路径上生效 ⇒ ⇒ 实际路径绕过了它**
#   ★**实测代价**: ★**v76ru 终板 7 个 CONN_CAM 的 GND 孔违反 [Δy ≥ 4.0mm] (★实际 0.9/1.2★)
#     ⇒ 4 个直接卡死 A2 那 5 条的端点 (CSI_D0_CK_N / CSI_D0_D0_N / CSI_D0_D1_P / CSI_MCLK / I2C_A_SCL)**
#   ★**默认关 ⇒ 逐位不变** (★既有臂必须可复现★)
GND_ESC_FIX = os.environ.get("PCB_GND_ESC_FIX", "0") == "1"
if GND_ESC_FIX:
    print("  [路由] ★★GND 下拉孔逃逸走廊修正: ON (★anchor 违规 ⇒ 改走长出脚/落回环格★)")
ESC_LEN = 1.20         # mm ★密集焊盘出脚直道长度 (沿焊盘中心线直线走出)
# ★出脚直道长度候选 (长→短) —— ★板边放不下就缩短 (fix B: 出脚直道离网格 ⇒ 板边要单独查)
ESC_LENS = (1.20, 0.90, 0.60, 0.40)     # ★★**默认 (★env 未设时就是这个 ⇒ 逐位不变★★) ★★
# ★★★**★2026-11-10 03:2x 【★ESC_LENS 改成 env 旋钮 (★默认关 ⇒ 逐位不变★)】★★★ ★★★
#   ★**为什么**: ★**出脚直道长度是【出脚区能不能出去】的第一控制变量 ★★
#     ⇒ ★**但它以前是写死的常量 ⇒ ⇒ 做不了单变量臂 ⇒ ⇒ 今晚的机制全靠 env 门控, 这个漏了** ★★
#   ★**用法**: ★**`PCB_ESC_LENS="2.00,1.20,0.90,0.60,0.40"`** ⇒ ★**更长/更短的出脚直道候选序列★**
#   ★**默认 = 原值 (1.20, 0.90, 0.60, 0.40) ⇒ 逐位不变** ★★
_esc_lens_env = os.environ.get("PCB_ESC_LENS", "") or ""
if _esc_lens_env.strip():
    try:
        ESC_LENS = tuple(float(x) for x in _esc_lens_env.replace(";", ",").split(",")
                         if x.strip())
        print("  [路由] ★出脚直道长度候选 (env 覆盖): %s" % (ESC_LENS,))
    except Exception:
        print("  [路由] ★★PCB_ESC_LENS 解析失败 ⇒ 用默认值 (★不改行为★)")
ESC_LENS = tuple(sorted(ESC_LENS, reverse=True))
EDGE_CLEAR = 0.50      # mm ★板边净距 (KiCad board setup: copper edge clearance = 0.5mm)
# ★出脚直道: 直道是**离网格**的 (落在焊盘真实中心线上) ⇒ 落铜后必须再对"已布走线/过孔"
#   做一次几何净距检查 (_stub_vs_routed) —— A* 的障碍图避让不了"后来才出现的直道"。
USE_ESCAPE = os.environ.get("PCB_USE_ESCAPE", "1") != "0"
# ★★★★2026-11-06 18:4x **"成品板上不能画 escape stub"** (★env 门控, ★默认不变 ⇒ 既有臂逐位可复现)
#   ★★**根因 (实测)**: escape stub 是"从焊盘中心沿中心线直插出去"的一段铜,
#     ★**它不走 halo / 净距检查** (★`_stub_clear` 只查 stub 自己, 不查它会撞到谁)
#     ⇒ ★**成品板上 ⇒ stub 直接压穿别网的铜**
#     ⇒ ★**实测: 成品板 rip-and-replace ⇒ fresh DRC 678~772 (199 短路 + 389 净距 + 124 交叉)**
#     ⇒ ★**"整网重布在成品板上出脚 stub 撞成一堆" 就是这个**
#   ⇒ ★**开这个开关 ⇒ stub 不画 ⇒ 起步格 = 焊盘自己那一格 ⇒ 铜直接压在焊盘上 (★与 no-stub A* 同思路)**
W_SIG = 0.25           # mm 信号线宽
W_MIN = 0.20           # mm 最细线宽 (KiCad 最小线宽) —— ★SoM BTB (0.4mm pitch) 出脚只能这么细
# ★★★★2026-11-06 10:1x **W_MIN 可调 (env 门控, 默认不变 ⇒ 既有臂逐位可复现)**
#   ★**为什么要有 (★纯几何推导, 不是拍脑袋)**:
#     SoM BTB = **0.4mm pitch · 0.2mm 宽焊盘** ⇒ 相邻焊盘中心距 0.4mm
#     ⇒ 沿排方向出线的需求 = CLEAR 0.20 + 自身半宽 + 对方半宽 0.10
#       · 线宽 0.20 ⇒ 需 **0.4000mm** ⇒ ★**余量 0.0000mm (卡在临界, 一个纳米都不剩)** ⇒ 实际布不出
#       · 线宽 0.15 ⇒ 需 0.3750mm ⇒ 余量 **0.0250mm** ⇒ 可行
#       · 线宽 0.10 ⇒ 需 0.3500mm ⇒ 余量 0.0500mm ⇒ 可行
#   ★**0.15mm = 6mil = 行业标准最小线宽** ⇒ ★**板厂几乎都能做** (FAB_ORDER_NOTES 现写 0.20mm)
#   ★**⇒ 这就是"差分对 N 侧永远布不出"的物理根因**: P 侧靠 pair-partner 豁免走掉了,
#     N 侧再走时 P 的铜已在 ⇒ 两者都卡在余量 0 的临界线上
# ★**用法**: `PCB_W_MIN=0.15` ⇒ ★**只影响本臂** ⇒ ★**默认 0.20 ⇒ 一切照旧**
W_MIN = float(os.environ.get("PCB_W_MIN", "0.20"))
W_PWR = 0.50           # mm 电源线宽
# ★三个"净距级别" (出线宽度决定要留多少净距):
#   cls0 = 0.20mm (BTB 出脚) · cls1 = 0.25mm (常规信号) · cls2 = 0.50mm (电源宽铜)
# ★★2026-11-06 10:1x **cls0 跟着 W_MIN 走** (★否则 W_MIN=0.15 时净距级别还按 0.20 算 ⇒ 净距保护虚高)
W_CLS = (W_MIN, 0.25, 0.50)
# ★★★★★★2026-11-10 04:2x 【★"出脚后必须先直行" (★env 门控 `PCB_ESC_STRAIGHT`)★】★★★★★★
#   ★★★**为什么要有 (★纯几何实测, ★不是猜★)★★★:
#     · SoM BTB = 0.4mm pitch ⇒ 相邻两根 0.15mm 出脚直道中心距 0.4mm ⇒ 净距 0.4-0.15 = 0.25mm ✓ 合法
#     · ★★**但**: ★**先布的那根出脚后【立刻 45° 转弯】** ⇒ ★它的斜线与【邻居出脚道末端】
#       的垂距 = 0.4 × sin(39.6°) = **0.255mm** ⇒ 而 [邻居半宽 0.075 + 自己半宽 0.125
#       + 净距 0.2 + 余量 0.025] = **0.425mm** ⇒ ★★**差 0.17mm ⇒ 邻居的出脚道被判死** ★★
#       ⇒ ★★**实测症状 (2026-11-10 04:0x 在 v76ru 终板上量到)**:
#         `CSI_D0_D0_P_SRC` 出脚直道 (21.600,50.960)->(21.600,52.160) 之后
#         ★**立刻**接 (21.600,52.160)->(21.950,52.450) ⇒ ⇒ **把 `CSI_D0_D0_N_SRC`
#         (x=22.000) 的唯一出脚方向掐死** ⇒ N 腿 **L=0.00 (连出脚都没成功)** ★★
#     · ★★**⇒ 唯一的几何解: 出脚后先【沿出脚方向直行】再转弯** ★★
#       ⇒ 直行 h 之后垂距 = 0.255 + 0.77×h ⇒ ★h=0.5mm (0.25 网格 2 格) ⇒ 0.64mm ⇒ ★解封★
#       ⇒ ★**而且这同时解释 0.8mm pitch 的 `ID_DETECT_0`↔`BOOT_N` 0.1813mm DRC**
#         (★两根直道并行·但各自【第一步就朝相反 y 方向转弯】⇒ 交错处只差 0.43mm★)
#   ★**用法**: ★`PCB_ESC_STRAIGHT=2` (★强制直行格数·默认 0 = 关 ⇒ ★逐位不变★)
#   ★**兜底**: ★约束下 A* 无路 ⇒ ★**自动回退到无约束重试** ⇒ ★保证不比现状更差★
ESC_STRAIGHT_STEPS = int(os.environ.get("PCB_ESC_STRAIGHT", "0"))
# ★★★★★★2026-11-10 04:4x 【★【★共线合并瞬移 bug 的修法 (★env 门控 `PCB_MERGE_FIX`)★】★】★★★★★★
#   ★**为什么要有**: ★**见下面 `_emit_path` 里合并判据的注释 (★实测 v76s2 有 10 段出到 y=-1.21mm★)**
#   ★**开关**: ★`PCB_MERGE_FIX=1` ⇒ ★①修对 `by` 的坐标错位 · ★②加三角不等式兜底 (★挡任何瞬移★)
#   ★**默认关** ⇒ ★**既有臂逐位可复现 (★本项目铁律★)**
MERGE_FIX = os.environ.get("PCB_MERGE_FIX", "0") == "1"
# ★★★★★★2026-11-10 14:2x 【★"孤儿铜"闸 (★env 门控 `PCB_GND_ORPHAN_FIX`, ★默认关 ⇒ 逐位不变★)】★★★★★★
#   ★**要修的病 (★实测坐实★)**: ★**`route_gnd_drops()` 第一遍里 `_emit_path` 先落铜,
#     随后的【孔的可行性闸】才判不合格 ⇒ `continue` 时铜已经落在 `self.tracks` 里了**
#     ⇒ ★★**⇒ (a) 同一段铜重复落 (★实测 GND 出脚直道重复 5~8 次★) ★★**
#     ⇒ ★★**⇒ (b) 被否决那次的铜留下【悬空端】⇒ DRC `track_dangling` (★实测 v76me1 1 条★)** ★★
#     ⇒ ★**⇒ 臂板里大量重复段 (★v76me1 76 / s8 42 / s9 34 / s10 100 条多余★)
#     ⇒ ★**⇒ 零铜网 / 差分死腿 / 孤岛统计被污染 ⇒ 候选臂的名次制闸读数不可信** ★★
#   ★**修法**: ★**把【孔的可行性预检】提到 `_emit_path` 之前 ⇒ 不合格就跳过 ⇒ 一点铜都不落**
#     ⇒ ★★**★遵循项目铁律: 【落线前就拦】是正收益, 【落板后剔铜】是负收益 (★实测剔铜 DRC 29→69★)** ★★
#   ★**默认 0 (关) ⇒ 逐位不变 (★老臂可复现★)**
GND_ORPHAN_FIX = os.environ.get("PCB_GND_ORPHAN_FIX", "0") == "1"
# ★★★★★★2026-11-10 19:3x 【★"走廊让路" (★env 门控 `PCB_CORRIDOR_YIELD`, ★默认关⇒逐位不变★)】★★★★★★
#   ★**要修的病 (★实测坐实★)**: ★**`BOOT_N` @ (63.60,11.04) 出不去 ⇒ 因为 `ID_DETECT_1` 的一根
#     (62.2,11.95)->(68.95,11.95) w=0.15 的直道【横在它的出脚口上方 0.91mm】**
#     ⇒ ★★**⇒ 而【官方板那一带完全没有 F.Cu 走线】⇒ ⇒ 官方板是"把整条走廊腾出来"** ★★
#     ⇒ ★★★**★⇒ "让路"是一条【链】不是单点: ★★让走 `ID_DETECT_0`, `ID_DETECT_1` 照样堵** ★★ ★★★
#     ⇒ ★★**⇒ ⇒ 而【调优先网名单】只调"谁先走", ★管不到"这条走廊上挤着几个网"** ⇒ ⇒ 此路已实测关闭** ★★
#   ★**修法**: ★**出脚直道若会【站在别人的出脚口上】⇒ ⇒ 换方向/换长度 ⇒ ⇒ 把走廊让给对方** ★★
#   ★**默认 0 (关) ⇒ 逐位不变 (★老臂可复现★)**
CORRIDOR_YIELD = os.environ.get("PCB_CORRIDOR_YIELD", "0") == "1"
# ★★★★★★2026-11-10 20:0x 【★差分对的【层选择】(★env 门控 `PCB_PAIR_LAYERSEL`, ★默认关⇒逐位不变★)】★★★★★★
#   ★**要修的病 (★实测坐实★)**: ★★**官方板的差分对 P/N 【在【不同层】上分段走】★★**
#     · ★`CSI_D0_CK_P` = F.Cu 158 / In2.Cu 71 · ★`CSI_D0_CK_N` = F.Cu 78 / In2.Cu 120 ★★
#     ⇒ ★★**⇒ 两腿的层占比【相反】⇒ ⇒ 这是【层选择】, 不是【走廊位置】** ★★
#     ⇒ ★★**⇒ 而路由器【没有这个机制】⇒ ⇒ P/N 用同一套层 ⇒ ⇒ 只能挤在同一层 ⇒ ⇒ 挤到 0.43mm 就违规** ★★
#   ★**修法**: ★**布 N 侧时, ★若 P 侧在【某些层】上占了很多 ⇒ ⇒ 把 N 侧【优先限制到 P 侧用得少的层】** ★★
#   ★**默认 0 (关) ⇒ 逐位不变 (★老臂可复现★)**
PAIR_LAYERSEL = os.environ.get("PCB_PAIR_LAYERSEL", "0") == "1"
# ★★★★★★2026-11-10 15:3x 【★"出脚离网格那一段"的净距闸 (★env 门控 `PCB_ESC_CLR_FIX`, ★默认关⇒逐位不变★)】★★★★★★
#   ★**要修的病 (★实测坐实★)**: ★**halo 是【按格】封的, ★而 A* 只判【格】**
#     ⇒ ★**出脚直道末端是【离网格】的 ⇒ 【直道末端 → 第一个格心】那一段 45° 斜线不在格边上**
#     ⇒ ★★**⇒ 这段离网格的斜线可以贴着【已落的孔】穿过去 ⇒ halo 看不见 ⇒ DRC 报 clearance** ★★
#     ⇒ ★**实测 (★v76mg1 终板★)**: ★**`LIGHT_3V3` 斜线离 GND 下拉孔中心距 0.5831 ⇒ 净距 0.1581 (★需 0.2★)**
#       ⇒ ★**该臂 6 条 clearance 里最严重的一条** ★★
#     ⇒ ★★**⇒ 与【蛇形出板】同一个病根的另一个面: ★【离网格的几何 ⇒ 栅格闸管不到】★★** ★★
#   ★**修法 (★与板边闸同一条铁律: 落线前就拦★)**: ★**`_emit_path` 落铜前用【真实几何】查那段离网格的线** ★★
#   ★**默认 0 (关) ⇒ 逐位不变 (★老臂可复现★)**
ESC_CLR_FIX = os.environ.get("PCB_ESC_CLR_FIX", "0") == "1"
# ★★★★★★2026-11-10 04:5x 【★【★"非紧凑焊盘排"的起步也要先直行 (★env 门控 `PCB_ESC_ROWNORM`)★】★】★★★★★★
#   ★**为什么要有 (★2026-11-10 04:0x 实测坐标, ★不是猜★)**:
#     ★**`ID_DETECT_0` ↔ `BOOT_N` 的 0.1813mm DRC (★所有臂都有, ★卡死所有臂★)**:
#       · 两脚在 J_SOM_P1 (0.8mm pitch) 的同一排 (y=11.040)
#       · 两根出脚直道**同向平行** (x=62.800 / 63.600, 间距 0.8mm) ⇒ 直道本身没问题
#       · ★★**但出脚后【第一步就朝相反 y 方向转弯】⇒ 两条 45° 斜线交错 ⇒ 只差 0.4313mm (中心线)** ★★
#       · ⇒ 净距 0.4313 - 0.125 - 0.125 = **0.1813mm < 0.2000mm** ⇒ ★★**差 0.0187mm** ★★
#   ★**解法 (★与 `PCB_ESC_STRAIGHT` 同机理, ★只是【焊盘不算紧凑 ⇒ 没有出脚直道】★)**:
#     ★**起步先沿【该排的法线】走** ⇒ 相邻脚的扇出【不会交错】 ⇒ ⇒ **不交错就不会差 0.0187mm** ★★
#   ★**用法**: ★`PCB_ESC_ROWNORM=2` (★强制直行格数·默认 0 = 关 ⇒ 逐位不变★)
ESC_ROWNORM_STEPS = int(os.environ.get("PCB_ESC_ROWNORM", "0"))
# ★★★★★★2026-11-10 16:6x 【★"排法线"约束在【有出脚直道】时也要生效 (★env 门控 `PCB_ESC_ROWNORM2`, ★默认关⇒逐位不变★)】★★★★★★
#   ★**要修的病 (★实测坐实★)**: ★**`ID_DETECT_0` / `BOOT_N` (★J_SOM_P1 同排 y=11.040★) 两脚都有出脚直道**
#     ⇒ ★**旧代码 `if st: ... return` 提前返回 ⇒ `ESC_ROWNORM` 分支【永远走不到】⇒ ⇒ 【该机制对最该生效的焊盘完全不生效】**
#     ⇒ ★★**⇒ 出脚后【第一步就朝相反 y 方向转弯】⇒ 两条 45° 斜线交错 ⇒ 中心距 0.4313 ⇒ 净距 0.1813 < 0.2000**
#     ⇒ ★★**⇒ 这条 DRC 的根因【用 `ESC_ROWNORM` 消不掉】(★机制本身是照着这条 DRC 写的!★)** ★★
#   ★**修法**: ★**有出脚直道时也登记【排法线】方向 (★且只在与直道方向不冲突时★)⇒ ⇒ 相邻脚扇出不交错** ★★
#   ★**默认 0 (关) ⇒ 逐位不变 (★老臂可复现★)**
ESC_ROWNORM2 = os.environ.get("PCB_ESC_ROWNORM2", "0") == "1"
# ★★★2026-11-10 18:5x 【★已撤回: ★"排内方向一致"机制 (★`PCB_ESC_ROWSAME`★)★】★★★
#   ★**撤回理由 (★实测★)**: ★**隔离测里 `ID_DETECT_0`↔`BOOT_N` 的净距本来就 0.6000mm 合法**
#     ⇒ ★**⇒ 冲突只在【整板上下文】里出现 (★别的网占了通道★) ⇒ ⇒ 这个旋钮【管不到】★**
#   ⇒ ★**⇒ 真解法还是【成对走廊规划 + 层选择】(★那才是 45 条的正解★)**
ESC_ROWSAME = False
# ★★★★2026-11-06 10:5x **过孔净距检查是否查全部宽度级别 (env 门控, 默认关)**
#   ★**为什么要有**: ★**`_via_ok` 查 `halo[2]` ⇒ 看不见 `halo[1]` 里的 0.25mm 走线**
#   ⇒ ★**"过孔 vs 常规走线"的净距检查失效** ⇒ ★**实测 DRC 报 7 条 clearance 违规**
#   ⇒ ★**打开后过孔会查 halo[0]/halo[1]/halo[2] 三级 ⇒ 只补漏, 不放宽**
#   ★★**默认关**: ★**改了 `_via_ok` ⇒ 所有臂的过孔落点都会变 ⇒ 既有臂逐位可复现性会破**
#   ★**用法**: `PCB_VIA_CHECK_ALL_CLS=1`
VIA_CHECK_ALL_CLS = os.environ.get("PCB_VIA_CHECK_ALL_CLS", "0") == "1"
VIA_DIA = 0.60         # mm 过孔盘
VIA_DRILL = 0.30       # mm 过孔钻 ★★2026-11-04 22:45 **必须 ≥ 板子设计规则的最小钻孔 (0.300mm)**
# ★★2026-11-05 07:40 **小焊盘用的缩小过孔** (0402/0603 电容电阻的 GND 焊盘只有 0.6mm 宽)
#   ⇒ 焊盘内过孔用 Ø0.60 放不下 (判据 min(w,h)<0.70 把它们全杀了 ⇒ 11 个 GND 焊盘一根铜都没有)
#   ⇒ 改用 Ø0.50/钻0.30 (环宽 0.10mm) ⇒ 0.6mm 宽的焊盘**放得下** (边距 0.05mm/边)
VIA_DIA_S = 0.50
VIA_DRILL_S = 0.30
#   ⇒ 上一轮改成 0.25mm 是错的: 板 setup 的 min hole = 0.3mm ⇒ ★**199 条 drill_out_of_range**
#   ⇒ 回退 0.30mm, 孔到孔 0.25mm 的问题改用"过孔中心间距"来解 (见 _via_too_close)
# ★★2026-11-04 23:50 **过孔中心间距下限** (孔到孔净距 0.25mm ⇒ 0.15+0.25+0.15 = 0.55mm)
#   ⇒ 取 0.58mm (0.03 余量)
#   ★★**这条必须同时管到 A\* (换层点) 和落铜 (过孔实际摆放)** ——
#   上一版只有落铜时查 (_via_too_close) ⇒ ★**A\* 会规划"根本放不下过孔的换层点"**
#   ⇒ 落铜时过孔被跳过 ⇒ ★**层间过渡段两端没落到过孔上** ⇒ 5 条 track_dangling 的根因
MIN_VIA_CENTER = 0.58  # mm 过孔中心距 (同网/异网都算: 孔到孔是制造规则)
# ★★★2026-11-05 19:40 **异网过孔的"铜到铜"中心距下限 (v34 根因级修复)** ★★★
#   ★**为什么必须有这一条 (v32/v33 两臂全红在这里)**:
#     v32/v33 把 `PCB_VIA_HALO_MARGIN` 开到 0.0 (过孔 halo 用精确几何)
#     ⇒ halo[2] 半径从 0.95mm 缩到 **0.75mm**
#     ⇒ ★**0.75 < 0.80** ⇒ 两颗**异网**过孔中心距 0.7906mm 被放行
#     ⇒ 铜间隙 = 0.7906 - 0.60 = **0.1906mm < 0.20** ⇒ DRC `clearance` 报红
#     ⇒ 实测: v32_R **56 条** + v33_S **40 条** = 两臂 96 条违规全是这个
#   ★**根因不是"halo 放松错了", 是"少了一条规则"**:
#     - 孔到孔 (制造规则): drill/2 + 0.25 + drill/2 = **0.55mm** ⇒ MIN_VIA_CENTER 0.58 ✓
#     - 铜到铜 (电气规则): dia/2 + 0.20 + dia/2 = **0.80mm** ⇒ ★**从来没人查过这条**
#     ⇒ ★**之前 DRC=0 是"halo 顺手挡住了"** (0.95 > 0.80), 不是"规则查对了"
#     ⇒ ★**一旦放松 halo (为了开逃逸走廊), 老账立刻全爆**
#   ★**修法**: 异网过孔中心距下限提到 **0.80mm** (同网仍是 0.58 ⇒ 同网两孔可以贴近, 因为是同一片铜)
#   ★**这是"只改布出来的几何", 不改板子的设计规则** (板 setup 的 min hole / clearance 一个字没动)
MIN_VIA_CENTER_XNET = float(os.environ.get("PCB_VIA_XNET_GAP", "0.80"))
                        # mm ★**异网**过孔中心距 (铜到铜: dia/2 + CLEAR + dia/2 = 0.80)
                        # ★★2026-11-05 19:45 **env 门控**: 0.80 = 板规则的真实要求 (KiCad clearance 0.20)
                        #   ⇒ **默认开着 (它是修 DRC 老账, 不是加严)**
                        #   ⇒ ★**旧臂 (v31 等) 靠脚本里显式写 `PCB_VIA_XNET_GAP=0.58` 还原旧行为** ⇒ 逐位可复现

# ★差分对走廊圈数 (格) —— ★**2 格 = 0.50mm**
#   ★理由: 差分对的两根线要**平行等距** (100Ω) ⇒ N 必须能贴着 P 走
#   ★但 P 的 halo 半径 0.65mm ⇒ N 至少要离 P 的铜箔 0.65mm
#   ⇒ ★**改用几何精确判断**: 中心距 0.50mm ⇒ 净距 0.25mm ≥ 0.2 ✓ DRC 干净
#   ⇒ ★**2 圈比 3 圈给 N 多 0.25mm 的活动空间** ⇒ 实测能多布出好几对
PAIR_RING = 2

# ★★2026-11-05 06:15 **修: 层数可配 ⇒ CU_LAYERS 必须跟着层数走**
#   原来写死 6 项 ⇒ 8 层时 li=6 (In6.Cu) ⇒ `CU_LAYERS[li]` 越界 IndexError
#   ⇒ ★**8 层那轮的布线结果被整个吞掉** (实测那轮只剩 78 个脚布不动, 比 6 层的 101 好, 但成绩作废)
#   ⇒ 8 层物理叠层: L1 F.Cu 信号 / L2 In1.Cu GND / L3 In2.Cu 信号 / L4 In3.Cu (空)
#                    L5 In4.Cu 信号 / L6 In5.Cu (空) / L7 In6.Cu 信号 / L8 B.Cu GND
NLAYERS = int(os.environ.get("PCB_LAYERS", 6))
# ★★2026-11-05 07:42 **层数通吃** (6/8/10 层) ⇒ 别再手写列表
#   ★10 层: F.Cu + In1..In8 + B.Cu ⇒ 信号层 F.Cu/In2/In4/In6/In8, 平面 In1/In3/In5/In7/B.Cu
_CU = [pcbnew.F_Cu]
for _i in range(1, max(NLAYERS - 1, 2)):
    _CU.append(getattr(pcbnew, "In%d_Cu" % _i))
_CU.append(pcbnew.B_Cu)
CU_LAYERS = _CU[:NLAYERS] if NLAYERS <= len(_CU) else _CU
# ★允许走信号的层: L1 / L3 / L5 (索引 0 / 2 / 4)
# ★★2026-11-05 04:10 层数可配 (环境变量 PCB_LAYERS): ★**6 层布不通 ⇒ 试 8 层**
#   动机 (实测): 186 器件 / 400 个 0.4mm pitch BTB 焊盘 ⇒ 3 个信号层的 escape 面积不够
#   ⇒ 路由器每轮把 unconnected 卡在 ~90 (剩下的都在 SoM BTB 密集区)
#   ⇒ ★Forlinx 官方载板是 **10 层** ⇒ 6 层本来就是低估 ⇒ ★**加层 = 加 escape 面积**
#   ★6 层: 信号 L1/L3/L5 · 平面 L2(GND)/L6(B.Cu=In5? 见 STACKUP: L2/L6 为 GND 平面)
#   ★8 层: 信号 L1/L3/L5/L7(In6.Cu) · GND 平面仍在 L2/L6 ⇒ ★多一整层 escape 面积
NLAYERS = int(os.environ.get("PCB_LAYERS", 6))
NLAYERS = int(os.environ.get("PCB_LAYERS", 6))
# ★★★2026-11-05 09:45 **差分对出脚区豁免开关** (默认关 ⇒ 不影响在跑的 v26 四臂)
#   ★根因: SoM BTB 0.4mm pitch ⇒ P/N 焊盘中心距 0.400mm ⇒ 伙伴禁入格 (0.8mm) 把 N 焊盘自己封死
PAIR_ESCAPE_EXEMPT = os.environ.get("PCB_PAIR_ESCAPE_EXEMPT", "0") == "1"
# ★★2026-11-05 12:40 **伙伴豁免半径** (★新)
#   ★**为什么要有这个参数**: 伙伴禁入格会把"N 侧自己的焊盘格"也封死
#     ⇒ N 侧 A* 起点被封 ⇒ 0 段铜 ⇒ 报"N 未通"
#   ★**旧值 1.20mm 的代价** (实测 v28_H: 21 处差分自短路):
#     豁免圈 (N 焊盘周围 1.2mm) **盖住了伙伴的走线通道**
#     ⇒ ★**N 侧的出脚直道/斜线可以从伙伴的通道上横穿过去 ⇒ 直接短路**
#     (实测: DSI_D0_CK_P 的通道在 y=6.70 横穿 x=94.95~99.20,
#      而 N 侧 R_SEL_CK_N.1 (98.10,5.60) 的出脚从 y=5.60 往下走到 y=7.20
#      ⇒ **必然横穿 y=6.70** ⇒ P/N 铜直接叠上 ⇒ KiCad 报 shorting_items)
#   ★**新默认 0.0** ⇒ ★**只豁免"N 焊盘自己那一格"** ⇒ N 能起步, 但**不许横穿伙伴的铜**
#   ⇒ 设大可以回到旧行为 (用于对比), 默认 0 = 安全
PAIR_EXEMPT_R = float(os.environ.get("PCB_PAIR_EXEMPT_R", "0.0"))
# ★★★★2026-11-08 23:5x **"换边重试"开关 (★默认关 ⇒ 既有臂逐位不变)**
#   ★**机制依据 (★实测, 不是猜)**: `state/PAIR_AWARE_ROUTING_PLAN.md` §3.2
#     ⇒ ★**"P 通 N 不通" 是【顺序依赖】**: 先布的那条腿占住走廊 ⇒ 后布的那条腿出不来
#     ⇒ ★**⇒ 修法: 当【跟腿】彻底没布出来时, 把主腿的铜摘掉, 换边重跑整对**
#   ★**为什么不做成 joint A\* (★§4.1①)**: 联合状态空间 = (格P × 格N) ⇒ 4.1M² 格 ⇒ 不可行
#     ⇒ ★**"换边重试" 用同一套耦合/走廊/兵底机制, 只换主/跟角色 ⇒ 不新增算法, 改动面最小**
#   ★**用法**: `PCB_PAIR_SWAP_RETRY=1`
PAIR_SWAP_RETRY = os.environ.get("PCB_PAIR_SWAP_RETRY", "0") == "1"
# ★★★★2026-11-09 00:4x **"最后一趟再换边"开关 (★默认关 ⇒ 既有臂逐位不变)**
#   ★**背景 (★v74 实测)**: ★**中途换边改铜 ⇒ 影响了后面才布的差分对 (DSI_D0_CK 因此丢了对)**
#   ★**⇒ 这一趟的做法: 全部对布完之后, 再把失败的对摘掉重试 ⇒ 换边只影响同批次后面的少数对**
#   ★**★与 `PCB_PAIR_SWAP_RETRY` 互斥** (★同时开 ⇒ 归因不清)
PAIR_SWAP_LAST = os.environ.get("PCB_PAIR_SWAP_LAST", "0") == "1"
# ★★2026-11-06 03:0x **v52: 出脚走廊感知的 rip-up** (默认关 ⇒ 老行为可复现)
#   ★**为什么**: 实测 61 条 A* 失败里 **42 条起脚在密集焊盘阵**
#     (J_SOM_P* 16 / CONN_LIGHT 13 / C_AC_CSI_D* 7 / CONN_CAM 6)
#   ★⇒ `escape_stub` 的出脚直道被**别的网已布的铜**封死 ⇒ 网连起步格都没有
#   ★⇒ ★**旧 rip-up 只拆"起步格附近的铜"** ⇒ 拆不到封死出脚走廊的那条
#     ⇒ 实测 19 个候选网 **一根线都没拆** (per-net 输出 0 行)
RIPUP_ESC = os.environ.get("PCB_RIPUP_ESC", "0") == "1"
BUDGET_ESCALATE = os.environ.get("PCB_BUDGET_ESCALATE", "0") == "1"
# ★★2026-11-05 10:25 **GND 下拉先布** (env 开关, 默认关)
#   ★**为什么**: GND 下拉原来排在**所有信号/电源之后** ⇒ 焊盘周围的好位置已被占光
#     ⇒ 实测 (臂 A): 25 个 GND 焊盘一根铜都没有 ⇒ unconnected 里 **GND 占 50**
#   ⇒ ★**先落 GND 孔** ⇒ 94 个 GND 焊盘先占住自己的位置 (焊盘内过孔最省空间)
#     ⇒ 信号线绕开它们 ⇒ ★**顺序换一下, 也许能救回一半**
GND_FIRST = os.environ.get("PCB_GND_FIRST", "0") == "1"
# ★A* 预算倍率 (模块级, 供"预算耗尽后的大预算重试"用)
_mult_global = float(os.environ.get("PCB_ABUDGET_MULT", "1"))
# ★★2026-11-05 11:26 **"预算升级重试"的开关 (★默认关)**
#   ★**为什么关**: 实测 v28 三臂里, 失败的对 (★几何堵死的: SoM 下沿被 0.4mm pitch 排针封住)
#     每个要多花 **~10 分钟** 跑 4 倍预算 ⇒ ★**几何堵死不是预算问题, 加预算只是白烧 CPU**
#   ⇒ ★要试的话开 PCB_BUDGET_ESCALATE=1 (只对"预算耗尽"的失败网, 每网只重试一次)
# ★★2026-11-05 07:40 **层数通吃** (★官方载板本身就是 10 层 ⇒ 一直只测到 8 层是低估)
#   ★信号层 = 偶数层 (0=F.Cu, 2, 4, ...) 但**不含最后一层** (B.Cu 留给 GND 平面)
#   ★6 层 ⇒ [0,2,4] · 8 层 ⇒ [0,2,4,6] · 10 层 ⇒ [0,2,4,6,8]
ROUTE_LAYERS = [li for li in range(0, NLAYERS, 2) if li != NLAYERS - 1]
# ★**信号层之间的邻接表** (★稀疏层号 ⇒ 不能用 li±1!)
#   L1↔L3 (过孔跨 In1.Cu 平面) · L3↔L5 (过孔跨 In3.Cu 平面) · L5↔L7 (过孔跨 In5.Cu 平面)
RLAY_NBRS = {0: (2,), 2: (0, 4), 4: (2, 6) if NLAYERS >= 8 else (2,)}
if NLAYERS >= 8:
    RLAY_NBRS[6] = (4,)
# ★★2026-11-05 07:42 **邻接表跟着层数走** (10 层 ⇒ 8 号信号层也要接 6 号)
for _li in ROUTE_LAYERS:
    _nb = []
    for _d in (-2, 2):
        _j = _li + _d
        if 0 <= _j < NLAYERS and _j in ROUTE_LAYERS:
            _nb.append(_j)
    RLAY_NBRS[_li] = tuple(_nb)


def _via_span(la, lb):
    """过孔穿过的铜层 (含中间平面层) —— ★只允许相邻信号层 ⇒ 只跨一层平面"""
    lo, hi = (la, lb) if la < lb else (lb, la)
    return tuple(range(lo, hi + 1))

# ★每格的层偏好代价 (0 = 首选); 换层代价 (格)
# ★**本轮调低**: 上一轮 80 个过孔 ⇒ 整板 99% 走线都挤在 F.Cu ⇒ 局部通道堵死
#   ⇒ 跨层几乎不要钱 (8 格 ≈ 2mm 线) ⇒ 3 个信号层一起用 ⇒ 可走面积 ≈ 3 倍
LAYER_COST = {0: 0.0, 2: 0.25, 4: 0.50}
if NLAYERS >= 8:
    LAYER_COST[6] = 0.75
VIA_COST = 8.0

# 层间跳 (相邻信号层): 换层时经过的铜层 (含中间平面层, 孔要穿过去 ⇒ 必须留间距)
VIA_SPAN = {0: (0, 1, 2), 1: (2, 3, 4)}

LNAME = {0: "L1/F.Cu", 1: "L2/In1.Cu", 2: "L3/In2.Cu",
         3: "L4/In3.Cu", 4: "L5/In4.Cu", 5: "L6/B.Cu"}
if NLAYERS >= 8:
    LNAME.update({6: "L7/In6.Cu", 7: "L8/B.Cu"})
# ★★2026-11-05 07:42 **10 层支持** ⇒ 层名表跟层数走 (L9/In8.Cu / L10/B.Cu)
if NLAYERS > 8:
    for _i in range(8, NLAYERS):
        if _i == NLAYERS - 1:
            LNAME[_i] = "L%d/B.Cu" % (_i + 1)
        else:
            LNAME[_i] = "L%d/In%d.Cu" % (_i + 1, _i)


# ------------------------------------------------------------------ 工具
def netcode(board, name):
    try:
        return board.GetNetcodeFromNetname(name)
    except Exception:
        return -1


def _pad_rect(pad):
    """焊盘外接矩形 (mm, 轴对齐) —— 处理封装旋转 (pad 自身 90° 时宽高互换)"""
    p = pad.GetPosition()
    sz = pad.GetSize()
    w = sz.x / MM
    h = sz.y / MM
    try:
        rot = pad.GetOrientationDegrees() % 180
    except Exception:
        rot = 0
    if 45 <= rot <= 135:
        w, h = h, w
    return (p.x / MM - w / 2.0, p.y / MM - h / 2.0,
            p.x / MM + w / 2.0, p.y / MM + h / 2.0)


def _rect_cells(gx0, gy0, gx1, gy1, g, ox=0.0, oy=0.0):
    """矩形覆盖的网格单元 (★单元**中心**落在矩形内才算 —— 否则会把旁边的空单元
       也当成铜 ⇒ 焊盘出不来线)"""
    i0 = int(math.ceil((gx0 - ox) / g - 1e-9))
    i1 = int(math.floor((gx1 - ox) / g + 1e-9))
    j0 = int(math.ceil((gy0 - oy) / g - 1e-9))
    j1 = int(math.floor((gy1 - oy) / g + 1e-9))
    out = []
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            out.append((i, j))
    if not out:
        # ★比一个单元还小的焊盘 ⇒ 取中心所在单元
        ci = int(round(((gx0 + gx1) / 2.0 - ox) / g))
        cj = int(round(((gy0 + gy1) / 2.0 - oy) / g))
        out.append((ci, cj))
    return out


def _seg_cells(x1, y1, x2, y2, g, r, ox=0.0, oy=0.0):
    """线段 (含端点) 附近的网格单元 (半径 r 个格, 圆判据)
       ★**沿线走**而不是扫包围盒 —— 否则长线段的复杂度是 O(L²) ⇒ 整板布线会卡死"""
    gx1, gy1, gx2, gy2 = (x1 - ox) / g, (y1 - oy) / g, (x2 - ox) / g, (y2 - oy) / g
    dx, dy = gx2 - gx1, gy2 - gy1
    length = math.hypot(dx, dy)
    n = max(1, int(math.ceil(length / 0.7)))
    ri = int(math.ceil(r))
    out = set()
    for k in range(n + 1):
        t = k / float(n)
        ci = int(round(gx1 + t * dx))
        cj = int(round(gy1 + t * dy))
        for dj in range(-ri, ri + 1):
            for di in range(-ri, ri + 1):
                if di * di + dj * dj > r * r + 1e-9:
                    continue
                out.add((ci + di, cj + dj))
    return out


NONET = "\x00NONET"    # ★没分配网络的焊盘 (SoM 未用脚) —— 同样是障碍


def _ring_offsets(rr):
    """★半径 rr (格) 的环上的格偏移 (按距离从近到远)
       —— 用于"从被封死的焊盘往外找能起步的格子\""""
    out = []
    ri = int(math.ceil(rr))
    for dj in range(-ri, ri + 1):
        for di in range(-ri, ri + 1):
            if di == 0 and dj == 0:
                continue
            d = math.hypot(di, dj)
            if d <= rr + 1e-9:
                out.append((d, di, dj))
    out.sort()
    return [(di, dj) for (_d, di, dj) in out]


def _pt_seg_dist(px, py, x1, y1, x2, y2):
    """点到线段的距离"""
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / L2
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _seg_seg_dist(ax, ay, bx, by, cx, cy, dx2, dy2):
    """两线段的最短距离 (交叉 ⇒ 0)"""
    def cross(ox, oy, px2, py2, qx, qy):
        return (px2 - ox) * (qy - oy) - (py2 - oy) * (qx - ox)
    d1 = cross(ax, ay, bx, by, cx, cy)
    d2 = cross(ax, ay, bx, by, dx2, dy2)
    d3 = cross(cx, cy, dx2, dy2, ax, ay)
    d4 = cross(cx, cy, dx2, dy2, bx, by)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(_pt_seg_dist(ax, ay, cx, cy, dx2, dy2),
               _pt_seg_dist(bx, by, cx, cy, dx2, dy2),
               _pt_seg_dist(cx, cy, ax, ay, bx, by),
               _pt_seg_dist(dx2, dy2, ax, ay, bx, by))


class RoutingError(Exception):
    pass


# ------------------------------------------------------------------ 路由器
def _merge_collinear(seg, merge_fix=False):
    """★★**共线段合并 (★2026-11-10 04:4x 从 `_emit_path` 抽成函数 ⇒ 可单测★)** ★★

    ★**段元组**: ★`(net, x1, y1, x2, y2, li, w)` ⇒ ★p[1]=x1 p[2]=y1 p[3]=x2 p[4]=y2 ★

    ★★★★**★【★那个只修了一半的老 bug (★2026-11-10 04:3x 实测, ★不是猜★)★】★★★★** ★★
      ★**2026-11-04 23:55** 已经修过【`p` 那一半】: ★`ax, ay = p[3]-p[1], p[4]-p[2]` (★对的★)
      ★★**但 `s` 那一半一直还是 `bx, by = s[3]-s[1], s[4]-s[1]`** ⇒ ★**s 的 y 分量减的是 s 的【x 起点】**
        ⇒ ★**x/y 混用** ⇒ ★**判据等于乱判** ⇒ ★★**本不该合并的段被合并** ★★
      ★★**后果 (★实测 v76s2 裸板)★★:
        · ★**合并段 = (p 的起点 → s 的终点)** ⇒ 本该首尾相接的两段被换成一段【瞬移】线
        · ⇒ ★**生成穿板/出板的假铜** (★实测 10 段跑到 y = -1.214mm ⇒ 板边线是 y=0★)
        · ⇒ ★**12 条 `copper_edge_clearance` 违规** (★actual 0.0000mm ⇒ 铜直接压在板边线上★)
        · ⇒ ★**还留下【重复段】** (★实测同一段 `(40.7000,3.2000)->(40.4500,3.2000)` 出现两次★)
        · ⇒ ★**也是所有臂共享的那 2 条板边违规的来源** (★v76ru / v76rz / v76s0 / v76s1 全有★)
      ★**修法 (★`merge_fix=True` ⇒ env `PCB_MERGE_FIX=1`)★★:
        ★**① 修对 `by`**: ★`by = s[4] - s[2]` (★s 的 y 起点★)
        ★**② 加数学不变量兜底 (★三角不等式★)**: ★**合并后长度 (p.start→s.end) 必须 ≤ 两段长度之和**
          ⇒ ★**任何"瞬移"合并都会被这一条挡住** ⇒ ★**不依赖判据写对与否** ★★
          ⇒ ★**这是【不变量】而不是【调参】⇒ ★★**天然覆盖所有同类 bug** ★★
      ★**默认 `merge_fix=False`** ⇒ ★**逐位等价于旧行为 (★本项目铁律★)**
    """
    merged = []
    for s in seg:
        if merged:
            p = merged[-1]
            ax, ay = p[3] - p[1], p[4] - p[2]
            bx, by = s[3] - s[1], s[4] - s[1]
            if merge_fix:
                by = s[4] - s[2]
            _lp = math.hypot(ax, ay)
            _ls2 = math.hypot(bx, by)
            if (p[5] == s[5]) and (abs(ax * by - ay * bx) < 1e-9) \
                    and (ax * bx + ay * by > 0):
                if merge_fix:
                    # ★★**三角不等式兜底 (★挡任何瞬移★)**
                    _lmer = math.hypot(s[3] - p[1], s[4] - p[2])
                    if _lmer > _lp + _ls2 + 1e-9:
                        merged.append(s)
                        continue
                merged[-1] = (p[0], p[1], p[2], s[3], s[4], p[5], p[6])
                continue
        merged.append(s)
    return merged


class GridRouter:
    """★网格路由器 —— 一次可以布一批网 (批量跑, 不是一条一条手写)"""

    def __init__(self, board, grid=GRID):
        self.b = board
        self.g = grid
        bb = board.GetBoardEdgesBoundingBox()
        self.bb = (bb.GetLeft() / MM, bb.GetTop() / MM,
                   bb.GetRight() / MM, bb.GetBottom() / MM)
        self.W = int((self.bb[2] - self.bb[0]) / grid) + 3
        self.H = int((self.bb[3] - self.bb[1]) / grid) + 3
        # 障碍图: cu[li][idx]=net (精确铜) ; halo[cls][li][idx]=set(net) (净距禁区, 3 个宽度级别)
        self.cu = [dict() for _ in range(NLAYERS)]
        # ★★★★**★2026-11-10 12:0x 【走线级走廊预留】(★env 门控 PCB_ROUTE_RESERVE, ★默认空 ⇒ 逐位不变)** ★★★★
        #   ★**为什么要有 (★2026-11-10 实测机制)**:
        #     ★**实测**: A1 桶那 5 条的 N 腿, 它的【反向】出脚道都被【别的网的铜】占着
        #       (★`CSI_D0_D0_N_SRC`←`CSI_D0_CK_N`/`CSI_D0_CK_P`/`CSI_D0_D0_P`; ★`DSI_D0_D0_N_SRC`←`DSI_D0_CK_N_SRC`/`DSI_D0_CK_P_SRC`/`DSI_D0_D3_P_SRC`)
        #       ⇒ ⇒ **N 无路可走** ⇒ ⇒ **"出脚级成对规划"已被证伪**
        #     ⇒ ★**真正要的是: 把那 0.4mm 宽的出脚走廊【从一开始就不让别的网占】**
        #   ★**为什么不用现有的 `PCB_KEEPOUT`**: ★**那是【排版期禁放框】(★挡器件) ⇒ ★★**挡不了走线** ★★ ★★★
        #   ★**怎么实现**: ★★**第二张网格 `cu_reserved[li][idx] = 专属网`** ⇒ ★★**别的网进不来, 专属网自己可以进** ★★
        #     ⇒ ★★**因为 `cu[li][idx]` 每格只能存【一个网】, ★存不下"专属"⇒ ⇒ **必须有第二张** ★★ ★★★
        #   ★**用法**: `PCB_ROUTE_RESERVE="NET:li0,x0,y0,x1,y1;NET2:li0,x0,y0,x1,y1"`
        #     (★格式: 网名:层号,x0,y0,x1,y1 (★mm, ★层号是信号层索引 0/2/4…), ★多组用 ; 分隔)
        #   ★**注意**: ★**预留框只挡【别的网】⇒ ★专属网自己照常能进去 ⇒ ★★**不会把专属网自己的路也堵死** ★★
        self.cu_reserved = [dict() for _ in range(NLAYERS)]
        self.route_reserve = {}      # ★[(net, li, idx)] -> 1 (★只作可查的清单)
        # ★halo[cls][li][idx] = 该单元被哪些网的铜"占了净距"
        #   cls0=0.20mm / cls1=0.25mm / cls2=0.50mm 三套规则各存一份
        self.halo = [[dict() for _ in range(NLAYERS)] for _ in range(3)]
        self.net_pads = {}          # net -> [(ref, padnum, cx, cy, layers)]
        self.pad_rects = []         # (net, x0,y0,x1,y1) —— 过孔不许打进焊盘
        self.pad_rects_l = []       # ★(net, x0,y0,x1,y1, layers) —— ★**焊盘只在它实际存在的层上有铜**
        self.pad_cell = {}          # (li,idx) -> (net, true_cx, true_cy)
        self.routed = set()
        # ★★2026-11-06 01:2x **v49: 单独记"成功布过"的网** (★`routed` 含失败网, 不能当"已布"用)
        self.routed_ok = set()
        # ★诊断计数器: 布不动的网到底是"预算用完"还是"真被堵死"
        self.astar_budget = 0
        self.astar_blocked = 0
        self.fail_reasons = {}
        self.fail_budget = {}
        self.fail_detail = []
        # ★真板边几何 (Edge.Cuts) —— ★**不能用 GetBoardEdgesBoundingBox()**:
        #   它把边线自身的宽度也算进去 (本板 0.1mm ⇒ 每边多 0.05mm)
        #   ⇒ 净距算出来偏大 ⇒ DRC 报"实际 0.325 / 要求 0.500" ★这就是本轮 2 条红的根因
        self.edge_segs = self._load_edge_segs()
        self.edge_d = []            # ★逐格"格心到真板边的距离" (mm) —— _free() 按线宽级别判
        self.tracks = []            # (net, x1,y1,x2,y2,li,width)
        self.vias = []              # (net, x, y, l1, l2)
        self.via_cells = {}         # ★格 → 该格附近的过孔坐标 (同网孔间距检查用)
        # ★★2026-11-05 **过孔邻近的粗粒度空间哈希** (1mm 格)
        #   ★_via_too_close 在 A* 里被调用**几十万次** ⇒ 逐格 (7×7=49) 查太慢
        #   ⇒ 改查 1mm 粗格 (3×3=9 次查) ⇒ 提速 ~5 倍, 结果完全一样
        self.via_hash = {}           # (cx, cy) → [(x, y, net), ...] ★**带网名** (异网要 0.80mm)
        # ★★2026-11-05 **差分对耦合布线参数** (★P/N 成对走线时临时生效)
        self.pair_partner = None     # ★伙伴网的网名 (差分对耦合时生效)
        self.pair_block = set()      # ★离伙伴铜箔太近的格 (几何精确) ⇒ 不许走
        self.pair_block_narrow = set()  # ★窄线 (0.2mm) 版禁入格 (★宽度感知)
        # ★★2026-11-05 09:50 **差分对 N 侧的出脚方向**: ★P 用过的方向不许再用
        #   ★**为什么**: SoM BTB 0.4mm pitch ⇒ P/N 出脚直道并行 ⇒ 中心距仅 0.400mm
        #   ⇒ 0.2mm 窄线并行时净距 = 0.400-0.1-0.1 = 0.20mm (勉强合法)
        #   ⇒ ★但只要有一根是 0.25mm 宽 ⇒ 净距 0.175mm ⇒ **DRC 违规**
        #   ⇒ ★**N 侧改走反方向** ⇒ 两根出脚直道背向 ⇒ ★既合法又不会被伙伴禁入格封死
        self.esc_used_dirs = {}     # ★网 → 用过的出脚方向集合 (dx,dy)
        self.esc_avoid = set()       # ★本轮不许用的方向 (★N 侧 = P 用过的)
        # ★★★★★★2026-11-10 04:2x 【★起步方向表 (★供"出脚后先直行"约束用)★】
        #   ★**键 = (网, (层,格号))** ⇒ ★**按网分桶** ⇒ ★不会两个网的出脚端点撞格时互相覆盖★
        #   ★**值 = (di,dj)** ⇒ ★出脚直道的方向 (★轴向 ⇒ 必是 8 邻域里的一个★)
        self._esc_start_dir = {}
        self.pair_min = 0.50         # ★mm 差分对中心距下限 (0.25mm 线 ⇒ 净距 0.25 ≥ 0.2)
        self.pair_fallback = 0       # ★耦合失败后退化为"无耦合"的次数 (★要写进报告)
        self._build_pads()

    # ------------------------------------------------ 索引
    def _idx(self, i, j):
        return j * self.W + i

    def _cx(self, i):
        return self.bb[0] + i * self.g

    def _cy(self, j):
        return self.bb[1] + j * self.g

    def _ci(self, x):
        return int(round((x - self.bb[0]) / self.g))

    def _cj(self, y):
        return int(round((y - self.bb[1]) / self.g))

    # ------------------------------------------------ 障碍建图
    def _build_pads(self):
        """全板焊盘 → 障碍 + 每网焊盘清单
           ★**没分配网络的焊盘也要当障碍** (SoM 400 脚里有一半没网) ⇒ 不然布线直接压过去 ⇒ 短路"""
        for fp in list(self.b.GetFootprints()):
            for pad in list(fp.Pads()):
                nm = pad.GetNetname()
                x0, y0, x1, y1 = _pad_rect(pad)
                cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
                if not nm:
                    nm = NONET
                try:
                    attr = pad.GetAttribute()
                except Exception:
                    attr = pcbnew.PAD_ATTRIB_SMD
                # ★★2026-11-05 06:25 **修: NPTH (无网络安装孔) 必须是**所有层**的障碍**
                #   原来只认 PAD_ATTRIB_PTH ⇒ NPTH 只算 F.Cu 一层 ⇒ ★**In2.Cu 的走线直接从孔里穿过去**
                #   ⇒ 实测: v21 的 25 条 DRC 违规 **全部**是 hole_clearance
                #   (JTAG_TMS / JTAG_TDI 压到 USB-C 的 NPTH 安装孔, 板边 x≈134.2, y≈2.6)
                #   ⇒ 孔是**贯穿所有层**的 ⇒ 每一层都得当障碍
                pth = attr in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
                is_npth = (attr == pcbnew.PAD_ATTRIB_NPTH)
                layers = list(range(NLAYERS)) if pth else [0]   # ★本板 SMD 全在 F.Cu
                if nm != NONET:
                    self.net_pads.setdefault(nm, []).append(
                        (fp.GetReference(), str(pad.GetNumber()), cx, cy, layers))
                self.pad_rects.append((nm, x0, y0, x1, y1))
                self.pad_rects_l.append((nm, x0, y0, x1, y1, tuple(layers)))
                # ★NPTH 孔还要额外让开 **孔净距** (板规则 0.25mm) ⇒ 不然走线贴孔边照样违规
                if is_npth:
                    HOLE_CLR = 0.25
                    x0, y0, x1, y1 = (x0 - HOLE_CLR, y0 - HOLE_CLR,
                                      x1 + HOLE_CLR, y1 + HOLE_CLR)
                for li in layers:
                    for (i, j) in _rect_cells(x0, y0, x1, y1, self.g, self.bb[0], self.bb[1]):
                        idx = self._idx(i, j)
                        self.cu[li][idx] = nm
                        if nm != NONET:
                            self.pad_cell[(li, idx)] = (nm, cx, cy)
        self._halo_pads()
        self._edge_margin()
        # ★★★★**★2026-11-10 12:1x 【走线级走廊预留】落地 (★解析 PCB_ROUTE_RESERVE)** ★★★★
        self._load_route_reserve()

    # ------------------------------------------------ 板边 (Edge.Cuts)
    def _load_route_reserve(self):
        """★**解析 PCB_ROUTE_RESERVE 并落地到 `cu_reserved`** (★2026-11-10 12:1x)

        ★**格式**: `PCB_ROUTE_RESERVE="NET:li0,x0,y0,x1,y1;NET2:li0,x0,y0,x1,y1"`
        · ★**li0** = 信号层索引 (★0=F.Cu / 2=In2.Cu / 4=In4.Cu / 6=In6.Cu / ★7=B.Cu)
        · ★**x0,y0,x1,y1** = mm 坐标 (★外接矩形)

        ★**语义**: ★**框内的格子被【专属网】预留 ⇒ ★别的网进不来, ★专属网自己可以进** ★★
        ⇒ ★★**⇒ 这就是[给差分腿的 N 腿留出脚走廊]的机制** ★★

        ★**默认空 ⇒ ★逐位不变** (★`self.cu_reserved` 全空 ⇒ `_free()` 里的检查永远为假) ★
        """
        self._rr_boxes = []
        _raw = (os.environ.get("PCB_ROUTE_RESERVE", "") or "").strip()
        if not _raw:
            return
        for grp in _raw.split(";"):
            grp = grp.strip()
            if not grp or ":" not in grp:
                continue
            net, box = grp.split(":", 1)
            net = net.strip()
            # ★★★★**★2026-11-09 21:5x 【多网预留】(★`N1+N2` 语法 ⇒ 一个框可同时留给一组网)** ★★★★
            #   ★**为什么**: ★**实测 (★v76rr 臂)** ⇒ 预留框 0.9mm 宽 ⇒ 必盖住 0.4mm pitch 的【伙伴焊盘】
            #   ⇒ ★**单网预留把伙伴腿打死**: `CSI_D0_D3_P_SRC` 从基线 46 段变 0 段
            #   ⇒ ★**⇒ 预留必须成对 (P+N 共享一个框)** ★★
            #   ★**旧语法 (单网) 行为逐位不变** ★★
            nets = tuple(n.strip() for n in net.split("+") if n.strip())
            if not nets:
                continue
            try:
                li, x0, y0, x1, y1 = [float(v) for v in box.split(",")]
            except Exception:
                continue
            li = int(li)
            if li < 0 or li >= len(self.cu_reserved):
                continue
            self._rr_boxes.append((nets, li, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
        self._apply_route_reserve()

    def _apply_route_reserve(self):
        """★**把预留框的格子写进 `cu_reserved`** (★可重复调用 ⇒ halo 重建后能重铺)"""
        if not getattr(self, "_rr_boxes", None):
            return
        for (nets, li, x0, y0, x1, y1) in self._rr_boxes:
            i0 = self._ci(x0)
            j0 = self._cj(y0)
            i1 = self._ci(x1)
            j1 = self._cj(y1)
            for i in range(min(i0, i1), max(i0, i1) + 1):
                for j in range(min(j0, j1), max(j0, j1) + 1):
                    idx = self._idx(i, j)
                    # ★★**★多网预留: 一格可以同时留给【一组网】(★P+N 成对)** ★★
                    #   ★**旧行为 (单网) 逐位不变** ⇒ ★**frozenset({net}) 的成员判断 ≡ `!= net`** ★★
                    _cur = self.cu_reserved[li].get(idx)
                    _new = frozenset(nets) if _cur is None else (frozenset(_cur) | frozenset(nets))
                    self.cu_reserved[li][idx] = _new
                    for _n in nets:
                        self.route_reserve[(_n, li, idx)] = 1

    def _load_edge_segs(self):
        """★真板边几何 —— Edge.Cuts 的线段 (弧按 16 段采样)

        ★为什么不用 GetBoardEdgesBoundingBox():
          它返回的是**边线外沿**的包围盒 (含边线自身宽度 0.1mm) ⇒ 每边多 0.05mm
          ⇒ 路由器以为板边在 y=-0.05, 实际铜铜边界在 y=0
          ⇒ 差 0.05mm + 少算的 w/2 ⇒ 正好是 DRC 报的 0.325 vs 0.500
        """
        segs = []
        try:
            drawings = list(self.b.GetDrawings())
        except Exception:
            drawings = []
        for d in drawings:
            try:
                if d.GetLayerName() != "Edge.Cuts":
                    continue
                shp = d.GetShape()
            except Exception:
                continue
            try:
                if shp == pcbnew.SHAPE_T_SEGMENT:
                    segs.append((d.GetStart().x / MM, d.GetStart().y / MM,
                                 d.GetEnd().x / MM, d.GetEnd().y / MM))
                elif shp == pcbnew.SHAPE_T_ARC:
                    segs.extend(self._arc_segs(d))
            except Exception:
                continue
        if not segs:
            # 兜底: 用 bbox 内缩 (边线宽的一半 ≈ 0.05mm)
            x0, y0, x1, y1 = self.bb
            e = 0.05
            segs = [(x0 + e, y0 + e, x1 - e, y0 + e),
                     (x0 + e, y1 - e, x0 + e, y0 + e),
                     (x1 - e, y0 + e, x1 - e, y1 - e),
                     (x1 - e, y1 - e, x0 + e, y1 - e)]
        return segs

    def _arc_segs(self, d, n=16):
        """Edge.Cuts 的圆弧 → 折线采样 (本板无弧, 留作通用兜底)"""
        try:
            c = d.GetCenter()
            r = d.GetRadius() / MM
            s = d.GetStart()
            e = d.GetEnd()
            a0 = math.atan2(s.y - c.y, s.x - c.x)
            a1 = math.atan2(e.y - c.y, e.x - c.x)
            ccw = (a1 - a0) % (2 * math.pi)
            sweep = d.GetArcAngle().AsDegrees()
            if abs(ccw - math.radians(sweep)) <= abs((2 * math.pi - ccw) - math.radians(sweep)):
                step = ccw / n
            else:
                step = -(2 * math.pi - ccw) / n
            out = []
            px, py = c.x / MM + r * math.cos(a0), c.y / MM + r * math.sin(a0)
            for k in range(1, n + 1):
                a = a0 + step * k
                qx, qy = c.x / MM + r * math.cos(a), c.y / MM + r * math.sin(a)
                out.append((px, py, qx, qy))
                px, py = qx, qy
            return out
        except Exception:
            return []

    def _build_edge_dist(self):
        """★逐格算"格心到真板边的距离" (mm) —— 只算板边附近的格 (远处恒 1e9)"""
        BIG = 1e9
        d = [BIG] * (self.W * self.H)
        r = int(math.ceil((EDGE_CLEAR + W_PWR / 2.0 + 1.0) / self.g)) + 1
        for (ax, ay, bx, by) in self.edge_segs:
            i0 = int(math.floor((min(ax, bx) - self.bb[0]) / self.g)) - 1
            i1 = int(math.ceil((max(ax, bx) - self.bb[0]) / self.g)) + 1
            j0 = int(math.floor((min(ay, by) - self.bb[1]) / self.g)) - 1
            j1 = int(math.ceil((max(ay, by) - self.bb[1]) / self.g)) + 1
            for j in range(max(0, j0 - r), min(self.H - 1, j1 + r) + 1):
                cy = self._cy(j)
                for i in range(max(0, i0 - r), min(self.W - 1, i1 + r) + 1):
                    dd = _pt_seg_dist(self._cx(i), cy, ax, ay, bx, by)
                    k = self._idx(i, j)
                    if dd < d[k]:
                        d[k] = dd
        return d

    def _edge_seg_ok(self, x1, y1, x2, y2, w):
        """★这段走线的**铜外缘**到真板边 ≥ EDGE_CLEAR ?
           ★给"离网格"的线段用 (出脚直道 / 焊盘真中心引出段) —— 格子判据管不到"""
        need = EDGE_CLEAR + w / 2.0
        for (ax, ay, bx, by) in self.edge_segs:
            if _seg_seg_dist(x1, y1, x2, y2, ax, ay, bx, by) < need:
                return False
        return True

    def _edge_margin(self, margin_mm=EDGE_CLEAR):
        """★板边禁布区 —— ★**按真板边 (Edge.Cuts) 算**, 不是 bbox
           ★**逐格存"格心到板边的真实距离"** ⇒ _free() 按**线宽级别**精确判 (fix A)
             (0.20mm 线 ⇒ 需 0.60mm · 0.25mm ⇒ 0.625mm · 0.50mm 电源 ⇒ 0.75mm)
           ★粗禁布只保留"格心进到 0.5mm 内"这一档, 精确档交给 _free() ⇒ 不误杀焊盘格"""
        self.edge_d = self._build_edge_dist()
        edge = []
        for j in range(self.H):
            for i in range(self.W):
                if self.edge_d[self._idx(i, j)] < margin_mm:
                    edge.append(self._idx(i, j))
        for li in ROUTE_LAYERS:
            for idx in edge:
                # ★焊盘格不置 EDGE (焊盘本身已过 DRC ⇒ 不许被误杀; 别的网本来也被 cu 挡住)
                if any((l2, idx) in self.pad_cell for l2 in range(NLAYERS)):
                    continue
                self.cu[li][idx] = "\x00EDGE"

    def _cls(self, w):
        """线宽 → 净距级别"""
        if w <= 0.21:
            return 0
        if w <= 0.30:
            return 1
        return 2

    def _mark(self, cls, li, idx, net, skip_pad_cells=False):
        """★**登记净距禁区**
        ★★2026-11-05 07:50 **skip_pad_cells: halo 不许盖住别的网的焊盘格**
          ⇒ 实测 (只读审计): 78 个失败脚里 14 个真被"同层异网铜"封死, 其中 ★**7 个是
            CONN_CAM/CONN_LIGHT 的信号脚, 最近的异网铜是 0.5mm 处的 GND** ⇒ 落在 halo 半径
            0.525mm 内 ⇒ ★**信号脚自己的起步格被封 ⇒ A* 一步都走不出去**
          ⇒ ★**焊盘自己的 halo (焊盘矩形外扩 rr) 已经守住了它的邻域** ⇒ 别的网再盖一层纯属多余
          ⇒ ★而且物理上就该这样: 焊盘是真实铜, 它的净距由它自己的 halo 管
          ⇒ ★**焊盘格在 cu 里已被它自己的网占住** ⇒ 别的网本来就走不进去 ⇒ 不会引入短路
        """
        if skip_pad_cells:
            pc = self.pad_cell.get((li, idx))
            if pc is not None and pc[0] != net:
                return
        # ★★2026-11-05 07:52 **越界层护栏** (★层号越界会让整轮布线炸掉 ⇒ 宁可跳过)
        if li < 0 or li >= len(self.halo[cls]):
            return
        s = self.halo[cls][li].get(idx)
        if s is None:
            s = set()
            self.halo[cls][li][idx] = s
        s.add(net)

    def _halo_pads(self):
        """焊盘净距禁区: 细线 = 焊盘矩形外扩 (0.2+0.125)=0.325mm ; 粗线/过孔 = 0.5mm
           ★**按真实矩形外扩** (不是按单元中心画圆) —— 否则边界误差会吃净距
           ★★**焊盘只在它实际存在的层上占净距** —— SMD 焊盘只在 F.Cu
             ⇒ 上一版把它记到全部 6 层 ⇒ ★L3/L5 整层被焊盘禁区封死
             ⇒ 板子 99% 只能走 F.Cu ⇒ 局部通道堵死 (本轮 179 脚布不通的根因)
           ★★★★2026-11-08 23:0x **【焊盘自身半宽漏计】修正 (env 门控 `PCB_PAD_HALO_EXACT=1`, 默认关 ⇒ 逐位不变)**
             ★**几何要求 (纯算术)**: 候选走线中心到**焊盘边缘**的距离必须 ≥ CLEAR + 候选线半宽
               ⇒ ⇒ 焊盘矩形必须外扩 **(CLEAR + 候选线半宽 + 焊盘自身半宽)**
               ⇒ ★**而旧公式只外扩 (CLEAR + 候选线半宽) ⇒ 漏了【焊盘自身半宽】**
             ★**漏多少**: BTB 焊盘 0.2mm 宽 ⇒ 漏 0.10mm; 大焊盘 (0.5mm+) 漏更多
               ⇒ ★**⇒ 在 margin 收紧 (0.03125 / 0) 的实验里, 走线可以贴到【比规范近 0.1mm】的位置**
               ⇒ ★**⇒ 真板 DRC 会报 clearance 违规 (实际 0.176~0.191 vs 要求 0.2 ⇒ 正是实测到的 7 条那类)**
             ★**修法**: 外扩量加上焊盘半宽 (取两方向里【小的那个】⇒ 长条焊盘方向上保守)
               ⇒ ★**默认关**: ★**既有臂逐位可复现 (本项目铁律) ⇒ 只有显式开这个开关的臂才用新公式**
        """
        _exact = os.environ.get("PCB_PAD_HALO_EXACT", "0") == "1"
        for (net, x0, y0, x1, y1, layers) in self.pad_rects_l:
            # ★焊盘自身半宽 (取两方向较小者 ⇒ 对长条焊盘保守)
            _pad_half = min(abs(x1 - x0), abs(y1 - y0)) / 2.0
            for li in layers:
                for cls in range(3):
                    rr = CLEAR + W_CLS[cls] / 2.0 + HALO_MARGIN
                    if _exact:
                        rr += _pad_half
                    cells = _rect_cells(x0 - rr, y0 - rr, x1 + rr, y1 + rr, self.g,
                                       self.bb[0], self.bb[1])
                    for (i, j) in cells:
                        if not (0 <= i < self.W and 0 <= j < self.H):
                            continue
                        self._mark(cls, li, self._idx(i, j), net)

    # ------------------------------------------------ 可走性
    def _free(self, li, idx, net, cls=1):
        # ★★★★★★2026-11-10 20:0x 【★差分对的【层选择】(★env 门控 `PCB_PAIR_LAYERSEL`★)】★★★★★★
        #   ★**语义**: ★**若本轮限定了可用层 (★`self._layer_limit`★) ⇒ ⇒ 别的层一律不许走** ★
        #   ★**为什么要有 (★实测坐实★)**: ★★**官方板的差分对 P/N 【在【不同层】上分段走】★★**
        #     · ★`CSI_D0_CK_P` = F.Cu 158 / In2.Cu 71★
        #     · ★`CSI_D0_CK_N` = F.Cu 78 / In2.Cu 120★ ⇒ ★★**两腿的层占比【相反】★★**
        #     ⇒ ★★**⇒ 而路由器【没有这个机制】(★grep 源码 = 0 命中★) ⇒ ⇒ P/N 用同一套层 ⇒ ⇒ 只能挤在同一层**
        #       ⇒ ⇒ 挤到 0.43mm 就违规 (★实测 `CSI_D0_CK_P`↔`CSI_D0_CK_N` 0.4280mm★) ★★
        #   ★**默认关 ⇒ 逐位不变 (★老臂可复现★)**
        _lim = getattr(self, "_layer_limit", None)
        if _lim is not None and li not in _lim:
            return False
        c = self.cu[li].get(idx)
        if c is not None and c != net:
            return False
        # ★★★★**★2026-11-10 12:0x 【走线级走廊预留】检查 (★PCB_ROUTE_RESERVE)** ★★★★
        #   ★**这是【唯一能让 A1 桶那 5 条 N 腿出来】的机制** (★2026-11-10 实测: ★它们的反向出脚道都被别的网占着)
        #   ★**语义**: ★**该格被【专属网】预留 ⇒ ★别的网不许进, ★专属网自己可以进** ★★
        #   ★**为什么放这里 (★而不是各处散加)**: ★★**所有自由格判断都走 `_free()` 这一个入口** ⇒ ★★**改一处就全覆盖** ★★
        _rs = self.cu_reserved[li].get(idx)
        # ★★**★2026-11-09 21:5x 【多网预留】**: `_rs` 现在是【该格允许的网集合】(★单网时 ≡ 老语义) ★★
        if _rs is not None and net not in _rs:
            return False
        # ★★★2026-11-05 09:55 **自己焊盘所在的格 ⇒ 不受 halo 阻挡**
        #   ★**为什么**: SoM BTB 0.4mm pitch ⇒ N 焊盘的格被 (P + 相邻 SoM 焊盘) 一起标了 halo
        #   ⇒ `others == {pair_partner}` 不成立 ⇒ ★**连豁免都轮不到 ⇒ 起点被封死 ⇒ 0 段走线**
        #   ⇒ 物理上: ★**那格本来就有自己的铜** (自己的焊盘) ⇒ 必须能起步
        #   ⇒ 真实净距由"别的网的铜" (`cu` 检查) + 落板后 DRC 兜底
        _pc = self.pad_cell.get((li, idx))
        _own_pad = bool(_pc and _pc[0] == net)
        if PAIR_ESCAPE_EXEMPT and _own_pad:
            s = None
        else:
            s = self.halo[cls][li].get(idx)
        if s and (s - {net}):
            others = s - {net}
            # ★★2026-11-05 **差分对耦合**: 伙伴(P)的 halo **不当障碍**
            #   ★**为什么**: 差分对的 N 侧必须**贴着 P 侧平行走** (100Ω 等长/等距)
            #   ⇒ 若把 P 的 halo 当障碍 ⇒ N 永远跑不到 P 旁边 ⇒ ★**P 走了通道, N 无路可走**
            #   ★**怎么豁免才安全**: 用**几何精确距离**判断, 而不是 halo 的保守栅格半径
            #   ⇒ ★`_pair_block` = 离 P 铜箔 < pair_min 的格 (几何精确) ⇒ 只禁真正会短路的
            # ★★2026-11-05 10:00 **宽度感知**: 窄线 (cls=0) 用窄标准禁入集, 宽线用宽标准
            _pb = self.pair_block_narrow if cls == 0 else self.pair_block
            if not (self.pair_partner and others == {self.pair_partner}
                    and idx not in _pb):
                return False
        # ★★2026-11-05 02:35 修 (实测 12 条 copper_edge_clearance): **板外的格子一律不许走**
        #   ★**根因**: 下面的"自己网的焊盘所在格"豁免了板边检查 ⇒ 靠边的焊盘 (如安装孔 GND 焊盘)
        #   ⇒ 出脚直道可以从那个格起步 ⇒ ★**直接走到板外** (实测: GND 段 (3.700,-0.050)→(3.700,0.200) 在板外!)
        #   ⇒ edge_d < 0 = 格心在板外 ⇒ 直接禁掉 (对任何网都禁, 含自己的焊盘)
        if self.edge_d[idx] < 0:
            return False
        # ★fix A: 板边净距 —— 铜外缘到真板边 ≥ 0.5mm ⇒ 格心距 ≥ 0.5 + w/2
        if self.edge_d[idx] < EDGE_CLEAR + W_CLS[cls] / 2.0 - 1e-6:
            pc = self.pad_cell.get((li, idx))
            if not (pc and pc[0] == net):
                return False
        return True

    def _path_len(self, path):
        """路径总长 (mm) —— ★GND 缝合的长度闸用它
           ★path 元素是 (li, idx) ⇒ 坐标要按 _emit_path 同样的方式换算 (格心坐标)"""
        if not path:
            return 0.0
        pts = []
        for (li, idx) in path:
            i, j = idx % self.W, idx // self.W
            pts.append((self._cx(i), self._cy(j)))
        total = 0.0
        for k in range(1, len(pts)):
            total += math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1])
        return total

    def _via_ok(self, la, lb, idx, net, cls=1):
        """此处能不能打孔 (跨层所有铜层都要有净距)
           ★**用 halo[2] (0.5mm 宽铜的净距级别) 判** —— 过孔盘 0.6mm 比 0.25mm 线粗
             ⇒ 用 cls1 的净距会漏判 ⇒ 过孔挨着别的网的线 ⇒ DRC 报 clearance
           ★★**过孔一律按"通孔"判 (贯穿 6 层)** —— 因为 commit() 里 SetViaType(THROUGH)
             会把层对强制成 (F.Cu,B.Cu) ⇒ 过孔环在 6 层都有铜
             ⇒ 只查 la..lb 两层 ⇒ **过孔会撞上内层别的网的铜 ⇒ DRC 短接**
             ⇒ ★所以这里必须查**全部 6 层** (且 _add_via_halo 也要记 6 层)"""
        # ★板边: 过孔盘 0.6mm ⇒ 盘外缘距板边 ≥ 0.5mm ⇒ 孔心距 ≥ 0.8mm
        if self.edge_d[idx] < EDGE_CLEAR + VIA_DIA / 2.0 - 1e-6:
            return False
        # ★**不许把过孔打在焊盘底下** (via-in-pad) —— 0402/0603 上的过孔 = 吸锡风险
        #   = 投板后必须手工补焊 ⇒ 返工项。★孔要躲开焊盘, 就得先在 F.Cu 上走一段
        if (0, idx) in self.pad_cell:
            return False
        # ★★2026-11-04 23:50 **孔到孔间距 (制造规则) 必须在 A\* 规划时就查**
        #   板 setup: m_HoleToHoleMin = 0.25mm ⇒ 0.3 钻的孔心距 ≥ 0.55mm (取 0.58)
        #   ★★**上一版只有"落铜时"查 (_via_too_close) ⇒ A\* 会规划"根本放不下过孔的换层点"**
        #   ⇒ 落铜时过孔被跳过 ⇒ ★**层间过渡段的两端没落到过孔上** ⇒ 5 条 track_dangling 的根因
        #   ⇒ ★**这里加上 ⇒ A\* 直接绕开非法换层点** (既治 DRC 又提连通率)
        i, j = idx % self.W, idx // self.W
        if self._via_too_close(net, self._cx(i), self._cy(j)):
            return False
        for l2 in range(NLAYERS):
            c = self.cu[l2].get(idx)
            if c is not None and c != net:
                return False
            s = self.halo[2][l2].get(idx)
            if s and (s - {net}):
                return False
            # ★★★★2026-11-06 10:5x **过孔 vs 细走线的漏检修正 (env 门控, 默认不变)**
            #   ★**根因 (实测)**: ★**过孔查询用 `halo[2]`** (宽铜级) ⇒ ★**但 0.25mm 走线的铜
            #     只登记在 `halo[1]`** ⇒ ★**过孔根本看不见它** ⇒ ★**净距检查对"过孔 vs 常规走线"失效**
            #   ★**实测症状**: 用 W_MIN=0.15 跑 ⇒ fresh DRC 报 7 条 clearance (0.1907/0.1771/0.1760)
            #     ★**全是"过孔 vs 走线"** ⇒ ★**不是 halo margin 的问题, 是查错了宽度级别**
            #   ★**修法**: ★**过孔要查所有 3 个级别** ⇒ ★**任何宽度的走线都能被过孔看见**
            #     ⇒ ★**不放宽任何东西 (halo[2] 的半径更大, 仍然查) ⇒ 只补漏 ⇒ 安全**
            #   ★★**为什么必须 env 门控**: ★**改了 `_via_ok` ⇒ 所有臂的过孔落点都会变**
            #     ⇒ ★**既有臂的逐位可复现性会破** ⇒ ★**默认关 ⇒ 只在实验臂开**
            if VIA_CHECK_ALL_CLS:
                for _cls in (0, 1):
                    s2 = self.halo[_cls][l2].get(idx)
                    if s2 and (s2 - {net}):
                        return False
        return True

    # ------------------------------------------------ A*
    def _astar(self, start, goals, net, dist_map=None, alpha=0.0,
                max_via=True, cls=1, limit=0, dist_def=0, max_len_cells=0,
                limit_mult=1.0):
        """★★wrapper (★2026-11-10 04:2x 新增)★★ —— ★**"出脚后先直行"约束 + 自动回退**

        ★★★**为什么要有 (★纯几何, ★见常量区 ESC_STRAIGHT_STEPS 的推导)★★★:
          ⇒ 先布的网出脚后立刻 45° 转弯 ⇒ **把邻居的出脚道掐死** (垂距 0.255 < 需 0.425)
          ⇒ ★★**⇒ 邻居整条腿 L=0.00** ⇒ ★★**⇒ 必须让起步先直行** ★★
        ★**约束怎么施加**: ★只约束【起点的前 N 步】⇒ ★**后面的路径完全自由** ⇒ 影响面最小
        ★**兜底**: ★★**约束下 A* 无路 ⇒ 自动用无约束重试一遍** ⇒ ★★**保证不比现状更差** ★★
        """
        _fd = None
        if len(start) == 1:
            _fd = self._esc_start_dir.get((net, start[0]))
        if _fd is not None:
            _p = self._astar_core(start, goals, net, dist_map=dist_map,
                                  alpha=alpha, max_via=max_via, cls=cls,
                                  limit=limit, dist_def=dist_def,
                                  max_len_cells=max_len_cells, limit_mult=limit_mult,
                                  first_dir=(_fd[0], _fd[1]), first_steps=_fd[2])
            if _p is not None:
                return _p
            # ★约束下无路 ⇒ 回退 (★无约束 ⇒ 与旧行为逐位相同★)
        return self._astar_core(start, goals, net, dist_map=dist_map,
                                alpha=alpha, max_via=max_via, cls=cls,
                                limit=limit, dist_def=dist_def,
                                max_len_cells=max_len_cells, limit_mult=limit_mult,
                                first_dir=None, first_steps=0)

    def _astar_core(self, start, goals, net, dist_map=None, alpha=0.0,
                    max_via=True, cls=1, limit=0, dist_def=0, max_len_cells=0,
                    limit_mult=1.0, first_dir=None, first_steps=0):
        """start: [(li,idx)] ; goals: set((li,idx))
           ★★**预算按"扩展次数"算, 不是按状态数算** —— 状态数是 (格 × 层),
             开了 3 个信号层后同一个物理区域的状态数 ×3 ⇒ 用状态数当预算
             ⇒ 搜索半径被悄悄砍到 1/3 ⇒ 该通的线也布不出来
             ★扩展次数 = 物理覆盖面积 ⇒ 与层数无关 ⇒ 换层后行为稳定

           ★★2026-11-04 **启发式加上"层差代价"** ——
             原来的 h 只算"到目标包围盒的平面距离" ⇒ **完全不知道换层要花钱**
             ⇒ A* 会在 3 个信号层之间反复横跳 ⇒ ★**预算 (15 万次扩展) 很快烧光**
             ⇒ 实测 82 个失败脚里 **52 个是"预算耗尽"** (不是真堵死)
             ⇒ 现在 h 额外加上"最少要换几次层 × VIA_COST" ⇒ ★**搜索方向正确 ⇒ 又快又通**

           ★★2026-11-05 **预算按路径长度自适应** ——
             实测: 失败脚里 **44/81 是"预算耗尽"**, 而这些网的路径长度中位数 **56mm**!
             ⇒ ★**短网 15 万次扩展够, 长网不够** ⇒ 固定预算 ⇒ 长网必失败
             ⇒ 现在: 按"起终点的曼哈顿距离"给预算 (短网省时间, 长网给够)"""
        INF = float("inf")
        gsc = {}
        came = {}
        heap = []
        gx = [k % self.W for (l, k) in goals]
        gy = [k // self.W for (l, k) in goals]
        if not gx:
            return None
        bx0, bx1 = min(gx), max(gx)
        by0, by1 = min(gy), max(gy)
        # ★目标可能在哪几层 (层差 ⇒ 至少要换几次层)
        goal_lis = sorted(set(l for (l, k) in goals))
        # ★**预计算每个目标层的"距当前层多远"** (★否则每次 h_of 都重算 min ⇒ 慢)
        lay_tab = {}
        # ★2026-11-05 04:58: 层集合从固定的 (0,2,4) 改成 **ROUTE_LAYERS** (8 层时含 6)
        #   ⇒ lay_tab 与 lay_min 的长度都随层数变 ⇒ ★**原来固定 range(3) ⇒ 8 层时 lay_min[3] 越界**
        #   (实测 8 层实验直接崩: "list index out of range")
        for gl in goal_lis:
            lay_tab[gl] = [abs(li - gl) // 2 for li in ROUTE_LAYERS]
        lay_min = [min(lay_tab[gl][k] for gl in goal_lis) for k in range(len(ROUTE_LAYERS))]

        def h_of(li, idx):
            i, j = idx % self.W, idx // self.W
            dx = 0.0
            if i < bx0:
                dx = bx0 - i
            elif i > bx1:
                dx = i - bx1
            dy = 0.0
            if j < by0:
                dy = by0 - j
            elif j > by1:
                dy = j - by1
            plan = (dx + dy) + (math.sqrt(2.0) - 1.0) * min(dx, dy)
            # ★换层代价 (可采纳: 每次换层至少花 VIA_COST)
            return plan + lay_min[li // 2] * VIA_COST

        cnt = 0
        for s in start:
            gsc[s] = 0.0
            heapq.heappush(heap, (h_of(s[0], s[1]), 0.0, cnt, s))
            cnt += 1
        goalset = set(goals)
        # ★★2026-11-05 **预算按路径长度自适应** (★长网需要更多扩展)
        #   曼哈顿距离 (格) × 系数 + 底数 ⇒ 短网省时间, 长网给够
        # ★★2026-11-06 05:0x **真 bug 修复**: 原来 `dist_cells` 只在 `limit<=0` 分支里算,
        #   而下面的 `limit = int(min(...dist_cells*900...))` **无条件执行** ⇒
        #   ⇒ **显式传 limit (>0) 必崩 (UnboundLocalError: dist_cells)**
        #   ⇒ ⇒ 而且 **limit 参数其实是死参数** (传进去必被覆盖)
        #   ⇒ 现在: dist_cells 无条件算; limit>0 时**尊重调用方的预算**
        dist_cells = 0
        for (sli, sidx) in start:
            si, sj = sidx % self.W, sidx // self.W
            for (gli, gidx) in goals:
                gi, gj = gidx % self.W, gidx // self.W
                d = abs(si - gi) + abs(sj - gj)
                if d > dist_cells:
                    dist_cells = d
        # ★★2026-11-05 05:30 **A* 预算可调** (环境变量 PCB_ABUDGET_MULT, 默认 1)
        #   ★依据 (实测 v12 的失败分类): 80 个布不动的脚里, **39 个是"A* 预算耗尽"**, 只有 41 个是真被堵死
        #   ⇒ ★**预算才是主要瓶颈之一** (不是几何) ⇒ 放大预算能把这 39 个变成"布出来了"
        #   ⇒ 代价: A* 扩展更多 ⇒ 更慢 ⇒ 用环境变量按需调, 不做死
        _mult = float(os.environ.get("PCB_ABUDGET_MULT", "1"))
        # ★★2026-11-05 10:50 **limit_mult**: ★"预算耗尽后的大预算重试"用 (按本网正常预算 ×N)
        _auto = int(min(900000 * _mult, max(150000 * _mult, dist_cells * 900 * _mult))
                    * max(1.0, limit_mult))
        # ★★2026-11-06 05:0x: limit>0 时**尊重调用方预算** (旧行为: 必崩 ⇒ 无兼容问题)
        limit = _auto if (limit is None or limit <= 0) else int(limit)
        best = None
        nexp = 0
        # ★★★2026-11-05 10:25 **路径长度上限** (★按"格数"算, 不用 g 值 —— g 里含层代价/走廊代价)
        #   ★**为什么**: GND 下拉本来"搜完再判长度 ≤6mm" ⇒ ★**空板上一次搜索能铺满全板**
        #     ⇒ 实测 GND_FIRST 臂在 GND 阶段跑了 7 分钟还没出来 (★比整板布线还慢)
        #   ⇒ ★**搜索时就截断** ⇒ 超过长度直接剪枝 ⇒ 搜得快, 而且长度规则是硬闸不是事后判
        _plen = {}
        for _s in start:
            _plen[_s] = 0
        # ★★★★★★2026-11-10 04:2x 【★"起步先直行"约束的状态跟踪 (★步数)★】
        _nsteps = {}
        for _s in start:
            _nsteps[_s] = 0
        while heap:
            f, gg, _, cur = heapq.heappop(heap)
            if gg > gsc.get(cur, INF) + 1e-12:
                continue
            nexp += 1
            if nexp > limit:
                self.astar_budget += 1
                break        # ★搜索预算用完 ⇒ 判失败 (否则整板卡死)
            if cur in goalset:
                best = cur
                break
            li, idx = cur
            i, j = idx % self.W, idx // self.W
            # ★★★★★★2026-11-10 04:2x 【★起步方向约束 (★只有前 first_steps 步受限★)★】
            _ns = _nsteps.get(cur, 0)
            _restrict = (first_dir is not None and _ns < first_steps)
            for dj in (-1, 0, 1):
                for di in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    # ★**约束生效时: 只能沿出脚方向走 (★其余方向一律禁★)**
                    if _restrict and (di, dj) != first_dir:
                        continue
                    i2, j2 = i + di, j + dj
                    if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                        continue
                    k = self._idx(i2, j2)
                    if not self._free(li, k, net, cls):
                        continue
                    step = (math.sqrt(2.0) if (di and dj) else 1.0)
                    c = gg + step + LAYER_COST.get(li, 0.0)
                    if alpha and dist_map is not None:
                        # ★★2026-11-05 **走廊外的格不再是"免费"** ——
                        #   原版 `dist_map.get(k, 0)` ⇒ 不在图里的格代价 0
                        #   ⇒ ★**远处反而比走廊便宜** ⇒ N 会逃出走廊
                        #   ⇒ 现在: 用 `dist_def` (走廊外的代价值) ⇒ ★N 留在走廊里
                        c += alpha * dist_map.get(k, dist_def)
                    if max_len_cells and (_plen.get(cur, 0) + step) > max_len_cells:
                        continue
                    if c < gsc.get((li, k), INF):
                        gsc[(li, k)] = c
                        _plen[(li, k)] = _plen.get(cur, 0) + step
                        _nsteps[(li, k)] = _ns + 1
                        came[(li, k)] = cur
                        heapq.heappush(heap, (c + h_of(li, k), c, cnt, (li, k)))
                        cnt += 1
            if max_via:
                # ★**换层只能到相邻信号层** (L1↔L3 / L3↔L5) —— ★**不能用 li±1**
                #   (ROUTE_LAYERS 是稀疏列表 [0,2,4] ⇒ li±1 永远是 1/3/5 ⇒ 根本换不了层
                #    ⇒ 上一轮整板 80 个过孔全部来自 GND 下拉 ⇒ 布线全挤在 F.Cu)
                for nli in RLAY_NBRS.get(li, ()):
                    if not self._via_ok(li, nli, idx, net, cls):
                        continue
                    st = (nli, idx)
                    c = gg + VIA_COST + LAYER_COST.get(nli, 0.0)
                    if alpha and dist_map is not None:
                        c += alpha * dist_map.get(idx, 0)
                    if max_len_cells and (_plen.get(cur, 0) + 2.0) > max_len_cells:
                        continue
                    if c < gsc.get(st, INF):
                        gsc[st] = c
                        _plen[st] = _plen.get(cur, 0) + 2.0
                        _nsteps[st] = _ns + 1
                        came[st] = cur
                        heapq.heappush(heap, (c + h_of(nli, idx), c, cnt, st))
                        cnt += 1
            if len(gsc) > 4000000:
                break        # ★内存保险丝 (状态数上限, 与覆盖无关)
        if best is None:
            return None
        path = [best]
        while path[-1] in came:
            path.append(came[path[-1]])
        path.reverse()
        return path

    # ------------------------------------------------ 单网多焊盘
    def route_net(self, net, width=W_SIG, allow_via=True, dist_map=None,
                  alpha=0.0, via_count=1, trunk=None, dist_def=0,
                  profiles=None):
        """布一个多焊盘网 —— 最小生成树顺序逐个并入一棵树
           trunk: ((padA, padB),) —— 先布的"主干"焊盘对 (差分对用它对齐走向)
           profiles: ★[(guide_map, dist_def, ring), ...] —— ★**逐脚渐次放宽的走廊档位**
             (差分对用: 紧的走廊不通就换松的 ⇒ ★**在同一棵树里重试 ⇒ 不重复布线**)
           返回 dict(ok/段数/长度mm/失败焊盘数)"""
        pads = self.net_pads.get(net)
        if not pads or len(pads) < 2:
            return {"ok": True, "segs": 0, "len": 0.0, "fail": 0, "net": net}
        cls = self._cls(width)
        order = self._mst_order(pads)
        connected_pads = []
        stubs = {}
        nfail_trunk = 0
        ring_used = None

        def anchor(pad):
            """★这个焊盘的 A* 锚点 (出脚直道终点) + 出脚直道"""
            key = (pad[0], pad[1])
            if key not in stubs:
                stubs[key] = self.escape_stub(net, pad)
            st = stubs[key]
            # ★★★★★★2026-11-10 16:6x 【★"排法线"约束在【有出脚直道】时也要生效 (★env 门控 `PCB_ESC_ROWNORM2`★)】★★★★★★
            #   ★★★**★为什么要有 (★实测坐实, ★不是猜★)★★★ ★★★
            #     ★**实测**: ★**`ID_DETECT_0` 与 `BOOT_N` (★J_SOM_P1 同排 y=11.040★) 两脚都【有出脚直道】**
            #       (★`_nearest_other_pad` = 0.3000 < 0.45 ⇒ `escape_stub` 返回直道★)
            #       ⇒ ★★**⇒ 旧代码的 `if st: ... return` 提前返回 ⇒ ★【ROWNORM 分支永远走不到】★★**
            #       ⇒ ★★**⇒ 于是那两条出脚直道【同向平行】(x=62.800 / 63.600) ⇒ 出脚后【第一步就朝相反 y 方向转弯】
            #         ⇒ 两条 45° 斜线交错 ⇒ 中心线只差 0.4313mm ⇒ 净距 0.1813mm < 0.2000mm ★★
            #       ⇒ ★★**⇒ ★【`ESC_ROWNORM` 这个机制【本来就是为消这条 DRC 写的】(★见 `_row_normal` 的注释★),
            #         但对它【最该生效的那两个焊盘】★【完全不生效】★★ ⇒ ⇒ 这是一条 DRC 永远消不掉的根因** ★★
            #   ★**修法 (★env 门控, ★默认关 ⇒ 逐位不变★)**: ★**有出脚直道时, ★也把【排法线】方向登记进去**
            #     ⇒ ★**让出脚后的第一步【沿排的法线】走 ⇒ ⇒ 相邻脚扇出不交错 ⇒ ⇒ 那条 DRC 的根因就没了** ★★
            #   ★**注意**: ★**只在【排法线方向与出脚直道方向不冲突】时才用 (★否则会与直道矛盾★)**
            if ESC_ROWNORM2 and st and ESC_ROWNORM_STEPS > 0:
                try:
                    _dn2 = self._row_normal(net, pad[2], pad[3])
                except Exception:
                    _dn2 = None
                if _dn2:
                    _sx = st[0] - pad[2]
                    _sy = st[1] - pad[3]
                    _same = (abs(_sx) < 1e-9 and abs(_dn2[0]) < 1e-9) or \
                            (abs(_sy) < 1e-9 and abs(_dn2[1]) < 1e-9)
                    if _same:
                        _i2, _j2 = self._ci(st[0]), self._cj(st[1])
                        self._esc_start_dir[(net, (0, self._idx(_i2, _j2)))] = \
                            (_dn2[0], _dn2[1], ESC_ROWNORM_STEPS)
            if st:
                i, j = self._ci(st[0]), self._cj(st[1])
                _cell = (0, self._idx(i, j))
                # ★★★★★★2026-11-10 04:2x 【★记录出脚方向 (★供"起步先直行"约束用)★】
                #   ★**方向 = 出脚直道从焊盘指向直道末端的方向 (★轴向 ⇒ di/dj 必有一个为 0★)**
                _dx = st[0] - pad[2]
                _dy = st[1] - pad[3]
                _di = (1 if _dx > 1e-9 else (-1 if _dx < -1e-9 else 0))
                _dj = (1 if _dy > 1e-9 else (-1 if _dy < -1e-9 else 0))
                if _di or _dj:
                    self._esc_start_dir[(net, _cell)] = (_di, _dj, ESC_STRAIGHT_STEPS)
                return [_cell], (pad[2], pad[3], st[0], st[1])
            _cells = list(self._pad_cells(net, pad))
            # ★★★★★★2026-11-10 04:5x 【★非紧凑焊盘排: 起步先沿【排的法线】走 (★`PCB_ESC_ROWNORM`)★】
            #   ★**目的**: ★**相邻脚的扇出不交错** ⇒ ⇒ **消掉 `ID_DETECT_0`↔`BOOT_N` 0.1813mm DRC** ★★
            #   ★**判据**: ★`_row_normal` 认得出"一排"才加约束 (★认不出 ⇒ 不加 ⇒ 保守★)
            if ESC_ROWNORM_STEPS > 0 and len(_cells) == 1:
                try:
                    _dn = self._row_normal(net, pad[2], pad[3])
                except Exception:
                    _dn = None
                if _dn:
                    self._esc_start_dir[(net, _cells[0])] = (_dn[0], _dn[1], ESC_ROWNORM_STEPS)
            return _cells, None
        if trunk:
            for (pa, pb) in trunk:
                ta = self._find_pad(net, pa)
                tb = self._find_pad(net, pb)
                if ta is None or tb is None:
                    continue
                sb, stb = anchor(tb)
                sa, sta = anchor(ta)
                path = self._astar(sb, set(sa), net, dist_map=dist_map,
                                    alpha=alpha, max_via=allow_via, cls=cls,
                                    dist_def=dist_def)
                if path is None and cls != 0:
                    path = self._astar(sb, set(sa), net, dist_map=dist_map,
                                        alpha=alpha, max_via=allow_via, cls=0)
                    if path is not None:
                        width = W_MIN
                if path:
                    # ★★2026-11-04 23:58 **换层点过孔落不下 ⇒ 整条路径放弃** (不留断铜)
                    if not self._emit_path(net, path, width, via_count,
                                           stub_start=stb, stub_end=sta):
                        nfail_trunk = nfail_trunk + 1
                        continue
                    trunk_cells = set(path)
                    connected_pads += [ta, tb]
        gx = sum(p[2] for p in pads) / len(pads)
        gy = sum(p[3] for p in pads) / len(pads)
        root = min(order, key=lambda p: (p[2] - gx) ** 2 + (p[3] - gy) ** 2)
        root_cells, root_stub = anchor(root)
        tree = set(root_cells)
        tree |= locals().get("trunk_cells", set())
        if root not in connected_pads:
            connected_pads.append(root)
        ok = True
        nfail = 0
        for pad in order:
            if pad is root:
                continue
            cells, stub_s = anchor(pad)
            if set(cells) & tree:
                continue
            # ★目标 = **最近的已连焊盘** (不是整棵树) ⇒ 启发式紧 ⇒ A* 不会爆
            goal_pad = min(connected_pads, key=lambda q: (q[2] - pad[2]) ** 2 + (q[3] - pad[3]) ** 2)
            goal_cells, stub_g = anchor(goal_pad)
            goals = set(goal_cells)
            bmark = self.astar_budget
            path = None
            used_ring = None
            if profiles:
                # ★★★2026-11-05 **逐档放宽走廊 (★在同一棵树里重试 ⇒ 不重复布线)**
                #   ★profiles = [(guide_map, dist_def, ring), ...] ⇒ ring 2 → 4 → 6 → 8
                #   ★**为什么**: 差分对要求 N 贴着 P 走 ⇒ 走廊窄 ⇒ 长距离 (100~240mm) 极易被单点堵死
                #   ⇒ ★**不通就放宽一档** ⇒ ★既保住"贴着 P"的大方向, 又给 N 留出活路
                #   ★**放宽过档的要计数** ⇒ 报告里点名哪些对不是最紧的 (不假装是 100Ω)
                for (pguide, pdef, pring) in profiles:
                    path = self._astar(list(cells), goals, net,
                                       dist_map=pguide, alpha=alpha,
                                       max_via=allow_via, cls=cls, dist_def=pdef)
                    if path is not None:
                        used_ring = pring
                        break
                if used_ring is not None and used_ring != profiles[0][2]:
                    self.pair_fallback += 1
                ring_used = used_ring
            else:
                path = self._astar(list(cells), goals, net,
                                    dist_map=dist_map, alpha=alpha,
                                    max_via=allow_via, cls=cls, dist_def=dist_def)
                ring_used = None
            # ★★2026-11-05 **耦合失败 ⇒ 同一个脚再试一次 (不带走廊约束)** ——
            #   ★**为什么**: 差分对要求 N 贴着 P 走 ⇒ 走廊窄 ⇒ 长距离 (100~240mm) 走不通
            #   ⇒ 实测 12 个 MIPI 对里 **N 侧 10 个完全布不出来** ⇒ 每个 = 2 个焊盘未连接
            #   ★**取舍**: N 走不到 P 旁边 ⇒ 几何不是理想差分对, 但**至少是通的**
            #   ⇒ ★**没通的板子比几何不完美的板子更没用**
            #   ★**在同一个 tree 里重试** ⇒ ★不会重复布已有的连接 (不会出重线)
            #   ★**几何不完美的对, 会在 ROUTING_REPORT 里点名** (不假装是 100Ω)
            if path is None and alpha > 0.0:
                path = self._astar(list(cells), goals, net,
                                   max_via=allow_via, cls=cls)
                if path is not None:
                    self.pair_fallback += 1
                    ring_used = None
            if path is None and cls != 0:
                # ★降级1: 细线 (0.2mm) —— 焊盘太密 (BTB 0.4mm pitch) 时必须
                path = self._astar(list(cells), goals, net,
                                    dist_map=dist_map, alpha=alpha,
                                    max_via=allow_via, cls=0)
                if path is not None:
                    width = W_MIN
            if path is None and allow_via:
                # ★降级2: 不换层 ⇒ 只在 F.Cu 上再试
                path = self._astar(list(cells), goals, net,
                                    dist_map=dist_map, alpha=alpha,
                                    max_via=False, cls=cls)
            # ★★★2026-11-05 10:50 **预算耗尽 ⇒ 最后再给一次"大预算"机会**
            #   ★**为什么**: v26 实测 "布不动 66 脚" 里 **22 个是 A* 预算耗尽** (不是真被堵死)
            #   ⇒ v27 里剩下失败的都是**长对** (DSI/CSI 主对, 60~160mm) ⇒ ★**正是预算型失败**
            #   ⇒ ★**最后再试一次, 预算 ×6** (只对"预算耗尽"的失败) ⇒ 代价可控 (只有这几个网吃 CPU)
            if (path is None and self.astar_budget > bmark
                    and BUDGET_ESCALATE
                    and net not in getattr(self, "_budget_retried", set())):
                # ★**每个网只重试一次** (★否则 3 脚网会重试 2 次 ⇒ CPU 爆)
                self._budget_retried = getattr(self, "_budget_retried", set())
                self._budget_retried.add(net)
                path = self._astar(list(cells), goals, net,
                                    dist_map=dist_map, alpha=alpha,
                                    max_via=allow_via, cls=cls,
                                    limit_mult=4.0)   # ★本网正常预算 ×4
                if path is not None:
                    self.astar_budget = bmark      # ★别让它算成"预算耗尽"
                    self.fail_budget_rescued = getattr(self, "fail_budget_rescued", 0) + 1
            # ★★2026-11-06 01:1x **v48: 换另一个已连焊盘再试** (env 门控)
            #   ★**为什么**: 上面的目标只有"最近的已连焊盘" ⇒ 它被堵 ⇒ 这条腿永久无铜
            #   ★**实测**: 官方板 19 条 "Pad↔Track" 未连接, Δ 中位 27.849mm ⇒ 整条腿缺失
            #   ★**做法**: ★**按距离依次试其它已连焊盘** ⇒ 纯多试目标, 不改几何规则
            #   ★**成本**: 每个焊盘最多换 MULTI_GOAL_MAX 个目标 ⇒ A* 预算可控
            if path is None and MULTI_GOAL and len(connected_pads) > 1:
                # ★用值比较排除 (★不用 `is` ⇒ tuple 值相等但对象不同会排除不掉)
                _alts = sorted((q for q in connected_pads if q != goal_pad),
                               key=lambda q: (q[2] - pad[2]) ** 2 + (q[3] - pad[3]) ** 2)
                _tried = 0
                for _alt in _alts:
                    if _tried >= MULTI_GOAL_MAX:
                        break
                    _gc, _sg = anchor(_alt)
                    _g2 = set(_gc)
                    _bm2 = self.astar_budget
                    _p2 = self._astar(list(cells), _g2, net,
                                       dist_map=dist_map, alpha=alpha,
                                       max_via=allow_via, cls=cls, dist_def=dist_def)
                    if _p2 is None and alpha > 0.0:
                        _p2 = self._astar(list(cells), _g2, net,
                                           max_via=allow_via, cls=cls)
                    if _p2 is None and cls != 0:
                        _p2 = self._astar(list(cells), _g2, net,
                                           dist_map=dist_map, alpha=alpha,
                                           max_via=allow_via, cls=0, dist_def=dist_def)
                    if _p2 is None:
                        if self.astar_budget > _bm2:
                            self.astar_budget = _bm2
                        continue
                    _tried += 1
                    if not self._emit_path(net, _p2, width, via_count,
                                           stub_start=stub_s, stub_end=_sg):
                        # ★换层孔落不下 ⇒ 这条目标也不成 ⇒ 继续换下一个
                        continue
                    path = _p2
                    goal_pad = _alt
                    goal_cells = _gc
                    stub_g = _sg
                    self.multigoal_hits = getattr(self, "multigoal_hits", 0) + 1
                    break
            if path is None:
                nfail += 1
                ok = False
                self.fail_reasons[net] = self.fail_reasons.get(net, 0) + 1
                if self.astar_budget > bmark:
                    self.fail_budget[net] = self.fail_budget.get(net, 0) + 1
                # ★诊断: 记下"从哪到哪布不通" ⇒ 才知道是局部堵死还是目标不可达
                self.fail_detail.append({
                    "net": net, "pad": "%s.%s" % (pad[0], pad[1]),
                    "start": [round(cells[0][1] % self.W * self.g + self.bb[0], 2),
                              round(cells[0][1] // self.W * self.g + self.bb[1], 2)],
                    "goal": [round(goal_cells[0][1] % self.W * self.g + self.bb[0], 2),
                             round(goal_cells[0][1] // self.W * self.g + self.bb[1], 2)],
                    "stub": bool(stub_s),
                })
                continue
            # ★★2026-11-04 23:58 **换层点过孔落不下 ⇒ 整条路径放弃** (不留断铜)
            if not self._emit_path(net, path, width, via_count,
                                   stub_start=stub_s, stub_end=stub_g):
                nfail += 1
                ok = False
                self.fail_reasons[net] = self.fail_reasons.get(net, 0) + 1
                self.fail_detail.append({
                    "net": net, "pad": "%s.%s" % (pad[0], pad[1]),
                    "reason": "via_conflict",
                })
                continue
            tree |= set(path)
            connected_pads.append(pad)
        length = self.net_length(net)
        self.routed.add(net)
        # ★★2026-11-06 01:2x **v49: 只有成功才算"布好"** (★失败网不能进 routed_ok)
        #   ★**为什么**: `routed` 里混着失败网 ⇒ 任何"跳过已布网"的判断都会误跳
        #   ★**注意**: `self.routed` 语义不变 (★默认关时逐位一致)
        if ok and RIPUP_ALIVE:
            self.routed_ok.add(net)
        return {"ok": ok, "segs": len(self.tracks), "len": round(length, 3),
                "fail": nfail + nfail_trunk, "net": net, "ring": ring_used}

    def _mst_order(self, pads):
        """Prim 最小生成树 ⇒ 好的布线顺序"""
        n = len(pads)
        if n <= 2:
            return list(pads)
        # ★★★★2026-11-06 12:2x **"远端优先"顺序 (env 门控, 默认不变)** ★★★★
        #   ★**为什么要有 (★实测的机制, 不是猜)**:
        #     ★**实测 `CSI_D0_CK_N`**: 它有 3 个焊盘 (C_AC 45.90,58.60 / TP 44.50,55.20 /
        #       CONN_CAM.17 86.90,51.40) ⇒ ★**MST 顺序先布了前两个 (近的)** ⇒ ★**铜局限在
        #       x 41.95..47.70** ⇒ ★**第三个 (远 39.47mm) 完全走不出去**
        #     ★**对照 `CSI_D0_CK_P`**: ★**同一个目标, P 侧布到了 x=86.2** ⇒ ★**⇒ 差别只在"顺序"**
        #   ⇒ ★★**⇒ 先布远的 ⇒ 先占住走廊; 后布近的 ⇒ 在已有走廊旁边短接** ⇒ ★**这才是对的顺序**
        #   ★**用法**: `PCB_PAD_ORDER_FAR_FIRST=1`
        if os.environ.get("PCB_PAD_ORDER_FAR_FIRST", "0") == "1":
            # ★**远端优先: 按"到第一个焊盘的距离"降序** ⇒ ★**最远的先布**
            _p0 = (pads[0][2], pads[0][3])
            # ★★2026-11-06 12:2x **修 IndexError** (★实测 v65 崩在这 ⇒ EXIT=2)
            #   ★**原因**: `net_pads` 的元素是 (ref, num, cx, cy, layers) 五元组
            #   ⇒ ★**但有的分支塞进去的是别的形状** ⇒ pd[2] 越界
            #   ⇒ ★**改成"按能取到的坐标算, 取不到就当 0 距离"** ⇒ ★**不崩, 顺序略变**
            def _far_key(pd):
                try:
                    cx, cy = float(pd[2]), float(pd[3])
                except Exception:
                    try:
                        cx, cy = float(pd[1]), float(pd[2])
                    except Exception:
                        return 0.0
                return -((cx - _p0[0]) ** 2 + (cy - _p0[1]) ** 2)
            # ★★2026-11-06 12:3x **诊断: pads 的形状到底长啥** (★v65 崩在这 ⇒ EXIT=2)
            try:
                _dbg = [(len(pd), type(pd).__name__) for pd in pads[:4]]
                if any(l < 4 for (l, _t) in _dbg):
                    print("  [MST-DBG] net 的 pads 形状异常: %r" % (_dbg,))
            except Exception:
                pass
            return sorted(pads, key=_far_key)
        d = [1e18] * n
        d[0] = 0.0
        order = []
        used = [False] * n
        for _ in range(n):
            u = -1
            for i in range(n):
                if not used[i] and (u < 0 or d[i] < d[u]):
                    u = i
            used[u] = True
            order.append(pads[u])
            for i in range(n):
                if used[i]:
                    continue
                dd = ((pads[u][2] - pads[i][2]) ** 2 + (pads[u][3] - pads[i][3]) ** 2)
                if dd < d[i]:
                    d[i] = dd
        return order

    # ------------------------------------------------ 密集焊盘出脚直道
    def _nearest_other_pad(self, net, cx, cy):
        """焊盘中心到**别的网**的焊盘边缘的最小距离 (mm)"""
        best = 1e9
        for (n2, x0, y0, x1, y1) in self.pad_rects:
            if n2 == net:
                continue
            dx = max(x0 - cx, 0.0, cx - x1)
            dy = max(y0 - cy, 0.0, cy - y1)
            d = math.hypot(dx, dy)
            if d < best:
                best = d
        return best

    def _stub_vs_routed(self, net, x1, y1, x2, y2, w=W_MIN):
        """★出脚直道 vs **已布走线/过孔** 的净距 (A* 的障碍图只管新走线, 管不了后出现的直道)
           ★**need 不加额外余量**: 0.4mm pitch 的 SoM BTB (0.2mm 焊盘) ⇒ 相邻两根
             0.2mm 直道的中心线间距就是 0.4mm ⇒ 净距恰好 0.2mm (KiCad 下限)
             ⇒ 加 0.02 余量会把**每一对相邻脚**都判死 ⇒ BTB 全布不出来
           ★先布的那根直道宽 0.2 ⇒ need = 0.1+0.1+0.2 = 0.4 ⇒ 恰好放行"""
        for (n2, ax, ay, bx, by, li, tw) in self.tracks:
            if n2 == net:
                continue
            if li != 0:
                continue
            # ★need 不加额外余量: 0.4mm pitch 的 SoM BTB (0.2mm 焊盘) ⇒ 相邻两根
            #   0.2mm 直道的中心线间距就是 0.4mm ⇒ 净距恰好 0.2mm (KiCad 下限)
            #   ⇒ 加 0.02 余量会把**每一对相邻脚**都判死 ⇒ BTB 全布不出来
            # ★但**对面是 0.25mm 及以上的线时必须留余量** (直道半宽 0.125 > 0.1
            #   ⇒ 0.4mm 间距只剩 0.175mm 净距 ⇒ DRC 红)
            need = w / 2.0 + tw / 2.0 + CLEAR + (0.0 if tw <= 0.21 else 0.025)
            # ★★★2026-11-05 09:55 **浮点容差 (★这是 SoM BTB 全布不出来的真凶)**
            #   实测: 0.4mm pitch ⇒ 相邻两根 0.2mm 直道中心距 = 0.4mm ⇒ 净距恰好 0.2mm (KiCad 下限)
            #   ⇒ 浮点算出来是 **0.3999999999999986** ⇒ `0.39999... < 0.4` ⇒ **被判违规** ⇒ 每一对相邻脚都被判死
            #   ⇒ ⇒ ★**加 1nm 容差** (真实规则仍是 0.2mm, 不会放宽到 DRC 红)
            if _seg_seg_dist(x1, y1, x2, y2, ax, ay, bx, by) < need - 1e-9:
                return False
        for (n2, vx, vy, l1, l2) in self.vias:
            if n2 == net or l1 > 0:
                continue
            need = w / 2.0 + VIA_DIA / 2.0 + CLEAR
            if _pt_seg_dist(vx, vy, x1, y1, x2, y2) < need - 1e-9:
                return False
        return True

    def _stub_clear(self, net, x1, y1, x2, y2, need=None):
        """这段直线出脚干不干净 (中心线离别的网的焊盘边缘 ≥need)
           ★need = 0.2 净距 + 0.1 (直道半宽) = 0.3 —— ★0.4mm pitch BTB 出脚
             本来就正好卡在 0.2mm 净距上 (物理事实, 不是模型保守)
           ★★2026-11-06 10:1x **need 跟着 W_MIN 走** (★之前硬编码 0.299 ⇒ W_MIN=0.15 时
             直道半宽实为 0.075 ⇒ 真实需求只要 0.275 ⇒ ★**多留了 0.024mm ⇒ 把能过的直道判死**
             ⇒ ★**实测症状: v57 (W_MIN=0.15) 把官方 v37 能通的 `CSI_D0_CK_P/N` 跑成了 N 未通**)
             ⇒ ★**默认 W_MIN=0.20 ⇒ need 仍为 0.299 ⇒ 逐位不变**"""
        if need is None:
            # ★**默认 0.299 (逐位保持旧行为) · 只有 W_MIN 显式改过才跟着算**
            need = 0.299 if abs(W_MIN - 0.20) < 1e-9 else CLEAR + W_MIN / 2.0
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.1))
        bx0, bx1 = min(x1, x2) - 1.0, max(x1, x2) + 1.0
        by0, by1 = min(y1, y2) - 1.0, max(y1, y2) + 1.0
        cand = [p for p in self.pad_rects
                if p[1] <= bx1 and p[3] >= bx0 and p[2] <= by1 and p[4] >= by0]
        for k in range(n + 1):
            t = k / float(n)
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            for (n2, a0, b0, a1, b1) in cand:
                if n2 == net:
                    continue
                dx = max(a0 - px, 0.0, px - a1)
                dy = max(b0 - py, 0.0, py - b1)
                if math.hypot(dx, dy) < need - 1e-9:
                    return False
        # ★板边: 出脚直道**离网格** ⇒ 格子判据管不到 ⇒ 这里单独查 (fix B)
        #   ★用真板边 (Edge.Cuts) + 直道半宽 ⇒ 铜外缘 ≥ 0.5mm
        if not self._edge_seg_ok(x1, y1, x2, y2, W_MIN):
            return False
        return True

    def _row_normal(self, net, cx, cy):
        """★该焊盘所在【一排】的**法线方向** (★返回 (di,dj) 或 None★)

        ★★**为什么要 (★2026-11-10 04:0x 实测坐标, ★不是猜★)★★:
          ★**`ID_DETECT_0` ↔ `BOOT_N` 的 0.1813mm DRC (★所有臂都有★)**
            · 两脚在 J_SOM_P1 (0.8mm pitch) 的同一排 (y=11.040)
            · 两根出脚直道**同向平行** (x=62.800 / 63.600) ⇒ 直道本身合法
            · ★★**但出脚后【第一步就朝相反 y 方向转弯】⇒ 两条 45° 斜线交错 ⇒ 中心线只差 0.4313mm**
              ⇒ 净距 0.4313 - 0.125 - 0.125 = **0.1813mm < 0.2000mm** ⇒ ★**差 0.0187mm** ★★
          ★**⇒ 起步先沿【排的法线】走 ⇒ 相邻脚的扇出【不交错】⇒ ⇒ 这条 DRC 的根因就没了** ★★
        ★**判据 (★保守: ★认不出排就返回 None ⇒ 不加约束★)**:
          · ★**至少两个【异网】焊盘** ⇒ 且它们【与本焊盘共线】(★垂直分量 ≤ 0.20mm★)
          · ⇒ ⇒ 才认定"本焊盘在一排里" ⇒ ⇒ 法线 = 排方向的垂直方向
        ★**选哪一侧**: ★**两侧各试一次空旷度 `_free_score` ⇒ 取空的那侧** ★
          (★★**只要【相邻脚选的方向一致或相反】都不会交错 ⇒ ⇒ 【方向一致】最好 (★保持差分耦合★)★★) ★★
        """
        _c = []
        for (n2, x0, y0, x1, y1) in self.pad_rects:
            if n2 == net:
                continue
            mx = (x0 + x1) / 2.0
            my = (y0 + y1) / 2.0
            vx = mx - cx
            vy = my - cy
            L = math.hypot(vx, vy)
            if L < 1e-6 or L > 2.0:
                continue
            _c.append((L, vx, vy))
        if len(_c) < 2:
            return None
        _c.sort(key=lambda t: t[0])
        # ★**共线判定**: ★垂直分量 (叉积) 必须 ≈ 0 ⇒ 否则不是"一排" ⇒ 不加约束
        L, vx, vy = _c[0]
        ux, uy = vx / L, vy / L
        if abs(vx * (-uy) + vy * ux) > 0.20:
            return None
        L2, vx2, vy2 = _c[1]
        if abs(vx2 * (-uy) + vy2 * ux) > 0.20:
            return None
        # ★**法线 = 排方向的垂直方向**
        nx, ny = -uy, ux
        _s1 = self._free_score(net, cx + nx * 0.8, cy + ny * 0.8)
        _s2 = self._free_score(net, cx - nx * 0.8, cy - ny * 0.8)
        if _s1 < _s2:
            nx, ny = -nx, -ny
        # ★★★★★★2026-11-10 18:5x 【★"排内方向"也要一致 (★env 门控 `PCB_ESC_ROWSAME`★)】★★★★★★
        #   ★★★**★为什么要有 (★实测坐实, ★不是猜★)★★★ ★★★
        #     ★**实测 (★官方板 vs 臂板逐段对照★)**: ★**官方板里 `ID_DETECT_0` 的 (62.80,11.04) 焊盘【一寸铜都没有】
        #       (★最近铜距 13.29mm★) ⇒ ⇒ 官方板把整条走廊【让给了 `BOOT_N`】**
        #     ⇒ ★**臂板里 `ID_DETECT_0` 从 (62.80,11.04) 45° 转【右下】⇒ ⇒ 斜线【正好横穿 `BOOT_N` 的出脚直道
        #       (x=63.60, y=11.04~12.24)】⇒ ⇒ `BOOT_N` 出不来 ⇒ ⇒ 记成【孤岛变多 1 个网】** ★★
        #     ⇒ ★★★**★⇒ 所以光让两脚【都沿排法线起步】(`ESC_ROWNORM2`) 【还不够】:
        #       ★★**两脚沿法线走完之后【各转各的】⇒ ⇒ 45° 斜线照样交错**★★** ★★★
        #     ⇒ ★★**⇒ 真正的解法: ★【同排的相邻脚, ★【转弯方向也要一致】⇒ ⇒ 两条斜线【平行】⇒ ⇒ 不会交错】★★** ★★
        #   ★**怎么定"一致"**: ★**以【排内位置】定 (★x 小的那脚往 -x 转, ★x 大的往 +x 转★)** ⇒ ★**都往排外侧散开** ★★
        #     ⇒ ★**⇒ 这与官方板的"一个让一个"效果一致, ★但不用牺牲任何一个脚** ★★
        #   ★**默认关 ⇒ 逐位不变 (★老臂可复现★)**
        di = (1 if nx > 1e-9 else (-1 if nx < -1e-9 else 0))
        dj = (1 if ny > 1e-9 else (-1 if ny < -1e-9 else 0))
        if not di and not dj:
            return None
        return (di, dj)

    def _free_score(self, net, cx, cy, r_mm=1.5):
        """出脚终点的空旷度 (周围能走的单元数)"""
        r = r_mm / self.g
        i0, j0 = self._ci(cx), self._cj(cy)
        cnt = 0
        for dj in range(-int(r), int(r) + 1):
            for di in range(-int(r), int(r) + 1):
                if di * di + dj * dj > r * r:
                    continue
                i2, j2 = i0 + di, j0 + dj
                if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                    continue
                if self._free(0, self._idx(i2, j2), net, 0):
                    cnt += 1
        return cnt

    def _stub_blocks_neighbor(self, net, x1, y1, x2, y2):
        """★**这条出脚直道会不会【挡住别的网的焊盘出脚】?**

        ★★★**★为什么要有 (★2026-11-10 19:3x 实测坐实★)★★★ ★★★
          ★**实测 (`v76mo` 臂)**: ★**`BOOT_N` @ (63.60, 11.04) 出不去 ⇒ 因为 `ID_DETECT_1` 的一根
            (62.2,11.95)->(68.95,11.95) w=0.15 的直道【正好横在 `BOOT_N` 的出脚直道上方 0.91mm】**
          ⇒ ★**而【官方板那一带完全没有 F.Cu 走线】⇒ ⇒ 官方板是"把这条走廊整个腾出来"** ★★★
          ⇒ ★★★**★⇒ ⇒ 【让路是一条【链】, 不是单点】: ★★**让走 `ID_DETECT_0`, `ID_DETECT_1` 照样堵** ★★
            ⇒ ★★**⇒ ⇒ 而"调优先网名单"只调"谁先走", ★管不到"这条走廊上挤着几个网"★★** ★★
          ⇒ ★★**⇒ ⇒ 所以本机制查的是: ★【我这条直道会不会【站在别人的出脚口上】】** ★★
            ⇒ ★★**⇒ 若是 ⇒ ⇒ 【换一个方向 / 换一个长度】⇒ ⇒ 【把走廊让给对方】** ★★

        ★**判据 (★保守, ★认不出就放行★)**:
          · ★**另一网的焊盘, ★它自己的出脚直道【必须经过我这条直道所在的位置】** ★
          · ★**⇒ 且我这条直道【离那个焊盘的出脚口太近】** ⇒ ⇒ 我就挡住了它 ★
          · ★**只有【同层】才算** (★异层不互相挡★) ★

        ★**默认关 (★env `PCB_CORRIDOR_YIELD`★) ⇒ 逐位不变**
        """
        if not CORRIDOR_YIELD:
            return False
        for _net2, _pl in self.net_pads.items():
            if _net2 == net:
                continue
            for _pad2 in _pl:
                _px, _py = _pad2[2], _pad2[3]
                # ★★另一网的出脚口 (★从焊盘沿四个方向各 ESC_LEN★)★★
                for _ln in ESC_LENS:
                    for (_dx, _dy) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                        _ex, _ey = _px + _dx * _ln, _py + _dy * _ln
                        # ★★它的出脚直道【会不会穿过我这条直道】★★
                        if not _seg_seg_dist(x1, y1, x2, y2,
                                             _px, _py, _ex, _ey) < 0.30:
                            continue
                        # ★★我这条直道离它的【出脚口】近不近 ★★
                        _d = _pt_seg_dist(_px, _py, x1, y1, x2, y2)
                        # ★★**判据 (★实测校准★)**: ★**出脚直道长 1.2mm ⇒ 别人的出脚口
                        #   若落在我这条直道【0.375mm】之内 ⇒ ⇒ 它的脚【被我的铜堵住】**
                        #   ⇒ ★**实测: `ID_DETECT_1` 的直道离 `BOOT_N` 出脚口 0.91mm,
                        #     而 `BOOT_N` 的出脚直道是 y=11.04→12.24 ⇒ 两者【重叠】** ★★
                        if _d < 0.30 + W_MIN / 2.0:
                            return True
                        # ★★**另一条判据 (★更贴近实际★)**: ★**我的直道【会不会穿过它的出脚直道】**
                        #   ⇒ ★**两条直道交叉 ⇒ ⇒ 必有一根被堵** ★★
                        if _seg_seg_dist(x1, y1, x2, y2, _px, _py, _ex, _ey) < 0.30:
                            return True
        return False

    def escape_stub(self, net, pad):
        """★密集焊盘 (SoM BTB 0.4mm pitch / 0.2mm 焊盘) 的出脚:
           沿焊盘中心线先直线走 ESC_LEN, 之后才允许横向偏
           ⇒ 净距才够 (0.25mm 网格做不到 0.4mm pitch 出脚)
           ★fix B: 出脚直道**离网格** ⇒ 板边必须单独查 (铜外缘 ≥ 0.5mm);
             1.2mm 不行就**缩短** (ESC_LENS 长→短) 或换方向
           返回 (终点x, 终点y) 或 None"""
        _ref, _num, cx, cy, _l = pad
        if not USE_ESCAPE:
            return None
        if self._nearest_other_pad(net, cx, cy) >= 0.45:
            return None          # ★不紧 ⇒ 正常出脚
        # ★★2026-11-05 10:00 **优先走"与伙伴不同"的方向, 但不是禁止**
        #   ★**实测**: SoM 0.4mm pitch 的焊盘 ⇒ ★**往往只有一个方向能出脚**
        #     ⇒ ★**硬禁会直接让 N 侧没有直道 ⇒ 更糟** ⇒ ⇒ 改成"先试别的, 都不行再回头"
        _dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        _prefer = [d for d in _dirs if d not in self.esc_avoid] + \
                  [d for d in _dirs if d in self.esc_avoid]
        for ln in ESC_LENS:
            best = None
            for (dx, dy) in _prefer:
                ex, ey = cx + dx * ln, cy + dy * ln
                if not self._stub_clear(net, cx, cy, ex, ey):
                    continue
                if not self._stub_vs_routed(net, cx, cy, ex, ey):
                    continue
                # ★★★★★★2026-11-10 19:3x 【★"走廊让路" (★env 门控 `PCB_CORRIDOR_YIELD`★)】★★★★★★
                #   ★★**★为什么要有 (★实测坐实★)**: ★**`BOOT_N` 出不去, 是因为【别人的出脚直道
                #     站在它的出脚口上】(★`ID_DETECT_1` 的 y=11.95 横道离它 0.91mm★)**
                #     ⇒ ★★**⇒ ⇒ 【我这条直道若会挡住别人的出脚口 ⇒ ⇒ 换方向/换长度 ⇒ ⇒ 把走廊让给对方】★★** ★★
                #   ★**默认关 ⇒ 逐位不变 (★老臂可复现★)**
                if self._stub_blocks_neighbor(net, cx, cy, ex, ey):
                    continue
                sc = self._free_score(net, ex, ey)
                if best is None or sc > best[0]:
                    best = (sc, ex, ey, dx, dy)
            if best is not None:
                # ★记录用过的方向 (★按网分桶 ⇒ 伙伴侧只看**自己那根**用过的)
                self.esc_used_dirs.setdefault(net, set()).add((best[3], best[4]))
                return (best[1], best[2])
        return None

    def _pad_cells(self, net, pad):
        """焊盘的**中心单元** (只取中心, 起点线从焊盘真实中心画出去)"""
        _ref, _num, cx, cy, layers = pad
        i, j = self._ci(cx), self._cj(cy)
        return set((li, self._idx(i, j)) for li in layers)

    def _find_pad(self, net, key):
        """按 (ref, padnum) 或 padnum 找焊盘"""
        for p in self.net_pads.get(net, []):
            if p[1] == str(key):
                return p
            if isinstance(key, (tuple, list)) and len(key) == 2 and p[0] == key[0] and p[1] == str(key[1]):
                return p
        return None

    # ------------------------------------------------ GND 平面下拉过孔
    def route_gnd_drops(self, net="GND", max_r_mm=4.0, via_top=0, via_bot=5):
        """★GND 焊盘 → 短走线 → 通孔 → L2/L6 完整 GND 平面
           (SMD 焊盘在 F.Cu ⇒ 必须靠过孔下到平面; ★通孔一层平面都连得上)

           ★★2026-11-04 **用"出脚直道"出脚** (与 route_net 同一个机制) ——
             上一版直接从**焊盘中心格**起走 ⇒ 密集器件区 (0402/0603 侧边全是别的网焊盘)
             ⇒ 起点周围全被封死 ⇒ ★**31 个 GND 焊盘一根铜都没接上**
             ⇒ 现在: 先沿焊盘中心线**直着出脚** (直线出脚才有机会挤出焊盘阵),
               再从直道末端去找过孔位
           返回 (成功数, 失败数)"""
        pads = list(self.net_pads.get(net, []))
        net_g = net
        ok = 0
        fail = 0
        done_pads = []
        # ★★2026-11-06 01:5x **v47: 同排相邻 GND 焊盘合并下拉** (env 门控, 默认关)
        #   ★**为什么**: 同排相邻焊盘 (如 CONN_LIGHT 的 `.21/.20`, 相距 0.50mm) 各自落孔时
        #   ★**孔心距下限 0.58mm 放不下** ⇒ 只能往外扩 ⇒ 扩成栅栏 ⇒ 堵死逃逸走廊
        #   ★**做法**: 把"同一排、相邻、间距 ≤ 阈值"的一组焊盘**只保留一个落孔点**
        #     ⇒ 其余焊盘由**第二遍的缝合链**接到这个落孔点 (同网 ⇒ 净距不管)
        #     ⇒ ★**孔数从 8 降到 1~2 ⇒ 栅栏从根上消失**
        if GND_SHARE_ROW:
            # ★**先按 y 聚成"排"** (同一排 = y 差 ≤ dy) ⇒ 再在排内按 x 分段
            _ys = sorted(set(round(_p[3], 3) for _p in pads))
            _rows = []
            for _y in _ys:
                if _rows and (_y - _rows[-1][0]) <= GND_SHARE_ROW_DY:
                    _rows[-1][1].append(_y)
                else:
                    _rows.append([_y, [_y]])
            _keep = []
            for _row in _rows:
                _grp = [p for p in pads if p[3] in _row[1]]
                _grp.sort(key=lambda q: q[2])
                _cur = []
                for _p in _grp:
                    if _cur and (_p[2] - _cur[-1][2]) > GND_SHARE_ROW_GAP:
                        _keep.append(_cur[0]); _cur = [_p]
                    else:
                        _cur.append(_p)
                if _cur:
                    _keep.append(_cur[0])
            _dropped = [p for p in pads if p not in _keep]
            if _dropped:
                # ★被合并掉的焊盘**不进第一遍** (它们由第二遍缝合链接到保留的那个孔)
                pads = list(_keep)
                self._gnd_shared = _dropped
                print("  [路由] ★GND 同排合并: %d 个焊盘 ⇒ 保留 %d 个落孔点 (省 %d 孔)"
                      % (len(pads) + len(_dropped), len(pads), len(_dropped)))
            else:
                self._gnd_shared = []
        used_vias = []          # ★已用过的过孔位置 (孔间距 ≥0.60mm ⇒ 不叠孔)
        # ★诊断: 失败原因分类 (★不猜 ⇒ 逐个记)
        why = {"free": 0, "inpad": 0, "viafree": 0, "spacing": 0, "astar": 0}
        for pad in pads:
            _ref, _num, cx, cy, _layers = pad
            done = False
            # ★★2026-11-05 10:40 **GND 下拉用小过孔** (0.5/0.3)
            #   ★**为什么**: 大过孔 (0.6) 在密集器件区放不下 ⇒ 25 个 GND 焊盘无铜
            #   ⇒ ★**小孔更容易找到落点** (净距规则不变, 仍是 0.2mm / 孔间距 0.6mm)
            _dia, _drill = VIA_DIA_S, VIA_DRILL_S
            # ★出脚直道 (与 route_net 的 anchor() 同一套逻辑)
            anchor = self.escape_stub(net, pad)
            # ★★★★★**★2026-11-10 03:0x 【★GND 下拉孔的【连接器逃逸走廊】规则被绕过了★】★★★★★
            #   ★**实测根因 (★v76ru 终板量出来的)**: ★**GND 下拉孔【不落焊盘周围的环格】,
            #     而是落 `escape_stub()` 出脚直道的末端 (anchor) ⇒ ⇒ 而 `escape_stub` 只查
            #     `_stub_clear`/`_stub_vs_routed` ⇒ ⇒ 【【不查 `_gnd_drop_esc_ok`】⇒ ⇒
            #     ⇒ "连接器差分脚逃逸走廊"规则【只在环格路径上生效】⇒ ⇒ 最常见的路径绕过了它** ★★
            #   ★**实测代价**: ★**v76ru 终板上 7 个 CONN_CAM 的 GND 下拉孔违反 [Δy ≥ 4.0mm]
            #     (★实际 0.9 / 1.2mm★) ⇒ ⇒ 其中 4 个直接卡死 A2 那 5 条的端点** ★★
            #   ★**修法 (★env 门控 `PCB_GND_ESC_FIX=1`, ★默认关 ⇒ 逐位不变★)**:
            #     ★**anchor 违反走廊 ⇒ 改走"长出脚": 沿垂直方向走到满足 |Δy| ≥ MIN 的位置**
            #       (★水平方向永远满足不了 ⇒ 只试垂直方向★) ⇒ ★**再不行就落回环格路径 (★那里有检查★)****
            if (anchor and GND_ESC_FIX
                    and not self._gnd_drop_esc_ok(_ref, cy, anchor[1])):
                _fixed = None
                _need = (CONN_GND_ESC or {}).get(_ref)
                if _need is not None:
                    _dir_ok = (CONN_GND_ESC_DIR.get(_ref, "ANY"))
                    for _sgn in ((1, -1) if _dir_ok != "UP" else (1,)):
                        for _ln in (_need + 0.05, _need + 0.30, _need + 0.60):
                            _ay = cy + _sgn * _ln
                            if not self._gnd_drop_esc_ok(_ref, cy, _ay):
                                continue
                            if not self._stub_clear(net, cx, cy, cx, _ay):
                                continue
                            if not self._stub_vs_routed(net, cx, cy, cx, _ay):
                                continue
                            _fixed = (cx, _ay)
                            break
                        if _fixed:
                            break
                anchor = _fixed          # ★★**⇒ 拿不到合规落点 ⇒ 落回环格路径 (★那里会检查走廊★)★★
                if anchor is None:
                    start_cells = list(self._pad_cells(net, pad))
                    stub_start = None
                else:
                    start_cells = [(0, self._idx(self._ci(anchor[0]), self._cj(anchor[1])))]
                    stub_start = (cx, cy, anchor[0], anchor[1])
            if anchor:
                ax, ay = anchor
                start_cells = [(0, self._idx(self._ci(ax), self._cj(ay)))]
                stub_start = (cx, cy, ax, ay)
            else:
                start_cells = list(self._pad_cells(net, pad))
                stub_start = None
            # ★★★2026-11-05 22:4x **v36_S: 窄焊盘的下拉孔 ⇒ 孔心取"焊盘内余量最大的点"**
            #   ★**v35_R 的 DRC 2 (两处违规都指同一颗孔 @ (62.700,64.450)) 的真根因**:
            #     `U_TEMP.2` 焊盘 **0.45x0.30** ⇒ 短边 0.30 ⇒ Ø0.5 孔**必然**探出铜面 (★**不是错**)
            #     ⇒ ★**错在孔心偏心 0.195mm、且偏向邻居的逃逸侧**
            #       ⇒ 离 `U_TEMP.1`(I2C_B_SCL) 逃逸短桩只剩 0.500 ⇒ 净距 0.125 ✘
            #     ⇒ 焊盘中心 (62.895,64.500) ⇒ 离桩 0.5835 ⇒ 净距 **0.2085 ✔**
            #     ⇒ ★**吸附到 0.25 栅格 (62.95,64.45) ⇒ 净距 0.184 ✘ ⇒ 必须用精确坐标**
            #   ★★**v36 的教训 (别再犯)**: "短边 < 孔径+0.10 ⇒ 禁落孔" **过狠**
            #     ⇒ 实测 GND 下拉 **176 → 94** (丢 82 个地) ⇒ 电源支路随之断
            #     ⇒ ★**窄焊盘照落, 只是孔心要正**
            _pr0 = self._pad_rect_at(cx, cy, net_g)
            if _pr0 is not None and min(_pr0[2] - _pr0[0], _pr0[3] - _pr0[1]) < _dia + 0.10:
                for (_px, _py) in self._narrow_pad_candidates(cx, cy, net_g, _dia, used_vias):
                    if self._place_in_pad_via(net_g, _px, _py, _dia, _drill, used_vias):
                        used_vias.append((_px, _py))
                        ok += 1
                        done_pads.append(pad)
                        done = True
                        break
                if done:
                    continue
            for r_mm in (0.8, 1.2, 1.6, 2.0, 2.5, 3.0, 3.5, 4.0):
                if r_mm > max_r_mm:
                    break
                for cand in self._ring_cells(cx, cy, r_mm):
                    i, j = cand
                    if not (0 <= i < self.W and 0 <= j < self.H):
                        continue
                    idx = self._idx(i, j)
                    px, py = self._cx(i), self._cy(j)
                    # ★★2026-11-05 19:15 **连接器差分脚逃逸走廊: 不许放 GND 下拉孔**
                    #   ★**根因**: `CONN_CAM` 的 GND 下拉孔落在每个 GND 焊盘正下方 1.2mm
                    #     ⇒ 与 0.5mm pitch 的 CSI 脚交错成栅栏 ⇒ 4.3mm 空带被切成 0.75mm 的缝
                    #   ⇒ 孔必须往连接器**上方**躲 (≥ MIN) ⇒ 逃逸走廊整条让开
                    if not self._gnd_drop_esc_ok(_ref, cy, py):
                        why["conn_esc"] = why.get("conn_esc", 0) + 1
                        continue
                    # ★★2026-11-05 10:10 **改用精确几何判据** (★原来用 halo[2] 0.95mm 保守半径
                    #   ⇒ 密集区一个孔都放不下 ⇒ GND 焊盘 25 个没铜 ⇒ unconnected 里 GND 占 50)
                    if not self._via_site_ok(idx, net, px, py, dia=_dia):
                        why["free"] += 1
                        continue
                    if self._in_pad(px, py):
                        # ★★★★2026-11-05 21:35 **窄焊盘不许在边缘落孔** (★v35_R 实测 DRC 2 的真根因)
                        #   ★**实测**: U_TEMP.2 (焊盘短边 <0.55mm) 的环格 (62.700,64.450) 落了 Ø0.5 孔
                        #     ⇒ 孔心离焊盘中心只有 0.201mm ⇒ ★**孔探出焊盘铜**
                        #     ⇒ 离邻居 U_TEMP.1 (I2C_B_SCL) 的逃逸短桩只剩 0.50mm
                        #     ⇒ 净距 0.125mm < 0.20 ⇒ ★**DRC clearance 违规 ×2** (同一颗孔, KiCad 按线段各报一次)
                        #   ★**为什么第三遍不会犯这个错**: 第三遍有 `_short<0.55` 的门槛 ⇒ ★**第一遍漏了这个门槛**
                        #   ★**v36_S 改法**: ★**不是禁落孔, 是"孔心必须正"**
                        #     ⇒ 窄焊盘走上面的 `_narrow_pad_candidates` (焊盘内余量最大的点)
                        #     ⇒ ★**这里只拦"环格偏心落孔"** (★v36 教训: 一刀禁掉 ⇒ 丢 82 个地)
                        _pr = self._pad_rect_at(px, py, net_g)
                        if _pr is None:
                            why["inpad_nopad"] = why.get("inpad_nopad", 0) + 1
                            continue
                        _pshort = min(_pr[2] - _pr[0], _pr[3] - _pr[1])
                        if _pshort < _dia + 0.10:
                            why["inpad_narrow"] = why.get("inpad_narrow", 0) + 1
                            continue
                        # ★★★★2026-11-05 20:35 **补几何净距判据** (★v34_R 实测 DRC 唯一违规的根因)
                        #   ★**实测**: GND 孔 @ (62.70,64.45) 压住 `I2C_B_SCL` 走线 @ (62.70,63.95)
                        #     ⇒ 净距实测 0.125mm < 0.20mm ⇒ ★**DRC clearance 违规 (唯一那1条)**
                        #   ★**根因**: ★**这条"焊盘内直接落孔"的路径从来没调用过 `_via_exact_ok`**
                        #     ⇒ 别的网的走线 / 焊盘 / 过孔 一律不看 ⇒ ⇒ 孔可以落在别人的铜旁边
                        #   ⇒ ★**修法**: 落孔前走同一套**真实几何**判据 (① 别网焊盘 ② 别网走线 ③ 孔距 ④ 孔净距)
                        #     ⇒ ★**只改"布出来的几何", 不动板规则** (clearance 仍是 0.20)
                        if not self._via_exact_ok(px, py, _dia, net_g, _drill):
                            why["exact"] = why.get("exact", 0) + 1
                            continue
                        # ★★**焊盘内直接落孔** (★不用再绕一根线过去 ⇒ 也不占走线空间)
                        #   ★0.6x0.9 的 0603 电容焊盘可以用 0.5mm 孔 ⇒ 直接落, 焊盘直接接平面
                        if self._via_exists(net_g, px, py):
                            why["inpad"] += 1
                            continue
                        _v = pcbnew.PCB_VIA(self.b)
                        _v.SetPosition(pcbnew.VECTOR2I(int(px * MM), int(py * MM)))
                        _v.SetViaType(pcbnew.VIATYPE_THROUGH)
                        _v.SetWidth(pcbnew.FromMM(_dia))
                        _v.SetDrill(pcbnew.FromMM(_drill))
                        _v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                        _v.SetNetCode(netcode(self.b, net_g))
                        self.b.Add(_v)
                        _tup = (net_g, px, py, 0, 5)
                        self.vias.append(_tup)
                        #★★2026-11-05 12:25 **修同点重复过孔 (DRC holes_co_located)**
                        #   根因: 这里**直接 board.Add(过孔)**, 同时又把元组塞进 self.vias
                        #        ⇒ 之后 commit() 遍历 self.vias 时**又画一遍同一个孔**
                        #        ⇒ ★**同一位置两个孔** ⇒ DRC 报 holes_co_located
                        #        (实测 v28_H: 板上 453 孔 vs 内存 385 孔 ⇒ 差 68 = 重复)
                        #   修法: ★**直接登记进 _committed** ⇒ commit() 会跳过它 (id 已登记)
                        _cm = getattr(self, "_committed", None)
                        if _cm is None:
                            _cm = self._committed = {}
                        _cm[id(_tup)] = (_tup, _v)
                        self._add_via_halo(net_g, px, py, 0, 5)
                        used_vias.append((px, py))
                        ok += 1
                        # ★**不要在这里 fail -= 1** (★fail 是"每个失败的焊盘 +1" ⇒ 这里减会出负数)
                        # ★★2026-11-05 21:35 **登记 done_pads** (★否则第二/三遍把它当孤儿 ⇒ ★**同一焊盘落两个孔**)
                        #   ★实测: U_TEMP.2 既有 in-pad 孔, 又有第四遍的"长轴引出"线+孔 ⇒ 冗余铜 ⇒ DRC 违规
                        done_pads.append(pad)
                        done = True
                        break
                    # ★孔间距: 0.3 钻 + 0.25 最小孔间距 ⇒ 孔心距 ≥0.55mm
                    if any(math.hypot(px - ux, py - uy) < 0.60 for (ux, uy) in used_vias):
                        why["spacing"] += 1
                        continue
                    # ★★**路径可以走内层绕过去**, 但**终点必须在 F.Cu**
                    #   ★因为 GND 下拉孔要落在终点 (过孔是通孔 ⇒ F.Cu..B.Cu ⇒ 接到 L2/L6 平面)
                    #   ★上一版 max_via=False ⇒ 只能走 F.Cu ⇒ 密集器件区根本挤不过去
                    # ★★2026-11-05 04:40 **限制 GND 下拉的走线长度** (≤6mm):
                    #   实测 v12: GND 缝合生成了**一根 160.45mm 的 F.Cu 长线** ⇒
                    #   ★**它把整条走廊堵死并短接了 14 个信号脚** (DSI_D0_D0_N_SRC×7 / DSI_D0_D1_P_SRC×3 / CARRIER_BOARD_EN×4)
                    #   + 87 条 clearance 全撞它 ⇒ ⇒ **GND 接地宁可"留几个未连接", 也不许拉长线横穿板子**
                    #   ⇒ 真正的解法是**第三遍的"焊盘内过孔"** (不需要走线空间)
                    path = self._astar(start_cells, {(0, idx)},
                                       net, max_via=True,
                                       max_len_cells=24)   # ★6mm / 0.25mm 网格
                    if path is None:
                        why["astar"] += 1
                        continue
                    # ★★2026-11-05 04:45 **硬闸: GND 下拉的走线只许 ≤6mm**
                    #   ★实测 v12: 一根 **160.45mm** 的 GND 缝合线把整条 F.Cu 走廊堵死,
                    #   并短接了 14 个信号脚 + 87 条 clearance ⇒ ★**长缝合线一律不许落**
                    #   ⇒ 宁可让这个焊盘留"未连接" (由第三遍的焊盘内过孔接管), 也不许横穿板子
                    if self._path_len(path) > 6.0:
                        why["toolong"] = why.get("toolong", 0) + 1
                        continue
                    # ★★★★★★2026-11-10 14:2x 【★"孤儿铜"闸 (★env 门控 `PCB_GND_ORPHAN_FIX`★)】★★★★★★
                    #   ★★**★问题 (★实测坐实★)**: ★**`_emit_path` 先落铜, ★【后面的过孔闸才判不合格】**
                    #     ⇒ ★**`continue` 时铜【已经落在 `self.tracks` 里了】** ⇒ ★★**⇒ 下一轮候选又落一遍**
                    #     ⇒ ★★**⇒ (a) 同一段铜重复落 (★实测 GND 出脚直道重复 5~8 次★)
                    #     ⇒ ★★**⇒ (b) 被否决那次的铜成了【悬空端】⇒ DRC `track_dangling`** ★★
                    #     ⇒ ★**⇒ 臂板里大量【重复段】(★v76me1 76 / s8 42 / s9 34 / s10 100 条多余★)
                    #     ⇒ ★**⇒ 零铜网/死腿/孤岛统计被污染 ⇒ ★【候选臂的名次制闸读数不可信】** ★★
                    #   ★★**★修法 (★与铜边闸同一条铁律: 落线前就拦 ⇒ 事后剔铜是负收益★)**:
                    #     ★**把【孔的可行性预检】提到 `_emit_path` 之前** ⇒ ★**不合格就直接跳过 ⇒ 一点铜都不落** ★★
                    #   ★**默认关 ⇒ 逐位不变 (★老臂可复现★)**
                    if GND_ORPHAN_FIX:
                        _dup_pre = False
                        for (vn, vx, vy, vl1, vl2) in self.vias:
                            if vn == net and abs(vx - px) < 1e-6 and abs(vy - py) < 1e-6:
                                _dup_pre = True
                                break
                        if not _dup_pre:
                            # ★**预检: 孔放不下 ⇒ 【这一轮候选直接淘汰】(★一点铜都不落★)**
                            if self._via_too_close(net, px, py):
                                why["spacing"] = why.get("spacing", 0) + 1
                                continue
                            if not self._via_ok(via_top, via_bot, idx, net):
                                why["viafree"] = why.get("viafree", 0) + 1
                                continue
                    # ★★★2026-11-04 **过孔必须真落下来** (否则铜从一层跳到另一层却没孔)
                    if not self._emit_path(net, path, W_SIG, 1,
                                           stub_start=stub_start):
                        why["astar"] += 1
                        continue
                    # ★★2026-11-05 **别放重叠的孔** ——
                    #   ★A* 的最后一步若是换层 ⇒ _emit_path **已经在终点格放过孔了**
                    #   ⇒ 再放一个 ⇒ **两个孔同心** ⇒ KiCad 报 hole_to_hole (co-located)
                    #   ⇒ 查一下: 已有同网同位置的孔就不放了
                    dup = False
                    for (vn, vx, vy, vl1, vl2) in self.vias:
                        if vn == net and abs(vx - px) < 1e-6 and abs(vy - py) < 1e-6:
                            dup = True
                            break
                    if not dup:
                        if self._via_too_close(net, px, py):
                            why["spacing"] += 1
                            continue
                        if not self._via_ok(via_top, via_bot, idx, net):
                            why["viafree"] += 1
                            continue
                        self.vias.append((net, px, py, via_top, via_bot))
                        self.via_cells.setdefault(idx, []).append((px, py))
                        self._add_via_hash(px, py, net)
                        self._add_via_halo(net, px, py, via_top, via_bot)
                    used_vias.append((px, py))
                    ok += 1
                    done_pads.append(pad)
                    done = True
                    break
                if done:
                    break
            if not done:
                fail += 1
        self.gnd_fail_why = why
        # ★★★2026-11-05 **第二遍: 把没接上的 GND 焊盘接到**已存在的 GND 铜**上
        #   ★**为什么**: 上一版每个 GND 焊盘都自己找过孔位 ⇒ 密集器件区找不到空位
        #   ⇒ 实测 **31 个 GND 焊盘一根铜都没接上** (占 117 个未连接的 27%!)
        #   ★**同一网之间不受 halo 限制** ⇒ ★**直接连到邻近的 GND 铜 (走线或过孔) 就行**
        #   ⇒ 第二遍: 把失败焊盘连到**已成功的 GND 焊盘/过孔** (同网 ⇒ 净距不管)
        orphan = [p for p in pads if p not in done_pads]
        # ★★v47: ★**被合并掉的同排焊盘也算孤儿** ⇒ 第二遍把它们缝合到保留的落孔点上
        _shared = list(getattr(self, "_gnd_shared", []) or [])
        if _shared:
            orphan = orphan + [p for p in _shared if p not in done_pads]
            # ★★2026-11-06 02:0x **账要平**: 被合并掉的焊盘从没被算作"失败"
            #   ⇒ 但第二遍缝合成功时会 `fail -= 1` ⇒ ★**fail 变负数** (实测 -15)
            #   ⇒ 修法: ★**先把它们算作失败** ⇒ 缝合成功再减回来 ⇒ 账平
            #   ⇒ ★**默认关时 _shared 为空 ⇒ 逐位一致**
            fail += len([p for p in _shared if p not in done_pads])
        if orphan and done_pads:
            # ★**已接上的 GND 铜的锚点** (焊盘中心 + 过孔位置)
            anchor_xy = []
            for p in done_pads:
                anchor_xy.append((p[2], p[3]))
            for (net, x, y, l1, l2) in self.vias:
                if net == net_g:
                    anchor_xy.append((x, y))
            for pad in orphan:
                _ref, _num, cx, cy, _layers = pad
                anchor = self.escape_stub(net_g, pad)
                if anchor:
                    ax, ay = anchor
                    start_cells = [(0, self._idx(self._ci(ax), self._cj(ay)))]
                    stub_start = (cx, cy, ax, ay)
                else:
                    # ★★2026-11-05 **起脚格被封死时的兵底** ——
                    #   实测: 有 GND 焊盘的**自身格子 8 个邻居全被别的网占** (8nb=0/8)
                    #   ⇒ escape_stub 返回 None (它只看"焊盘密度", 不看"走线围堵")
                    #   ⇒ A* 从焊盘格起步**一步都走不出去** ⇒ 必失败
                    #   ⇒ 现在: 往外找一圈**有空位且邻居能走**的格子, 用直道接过去
                    start_cells, stub_start = self._gnd_escape(net_g, pad)
                    if not start_cells:
                        why["chain"] = why.get("chain", 0) + 1
                        continue
                # ★★**只取最近的几个锚点当目标** (★不然目标散在全板 ⇒ 启发式包围盒巨大 ⇒ A* 预算烧光)
                #   实测: 上一版把 144 个锚点全当目标 ⇒ ★**22 个孤儿全失败**
                near = sorted(anchor_xy,
                              key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)[:16]
                # ★★**目标可以在内层** (★过孔是通孔 ⇒ F.Cu..B.Cu ⇒ 接到 L2/L6 平面)
                goals = set()
                for q in near:
                    gi = self._idx(self._ci(q[0]), self._cj(q[1]))
                    for li in ROUTE_LAYERS:
                        goals.add((li, gi))
                # ★★**允许换层** (★原来 max_via=False ⇒ 只能走 F.Cu ⇒ 挤不过去)
                path = self._astar(start_cells, goals, net_g, max_via=True)
                if path is None:
                    why["chain"] = why.get("chain", 0) + 1
                    continue
                # ★★2026-11-05 04:45 同样硬闸: chain 缝合也只许 ≤6mm (同上: 不许拉长线横穿板子)
                if self._path_len(path) > 6.0:
                    why["chain"] = why.get("chain", 0) + 1
                    continue
                if not self._emit_path(net_g, path, W_SIG, 1, stub_start=stub_start):
                    why["chain"] = why.get("chain", 0) + 1
                    continue
                ok += 1
                fail -= 1
                # ★★2026-11-05 21:35 **登记 done_pads** (★★否则第三遍(in-pad)会把它当孤儿 ⇒ 再落一个孔)
                #   ★**同一个焊盘落两个孔 = 冗余铜** ⇒ 冗余孔还可能压住别人的逃逸短桩 ⇒ DRC 违规
                done_pads.append(pad)
                # ★新接上的焊盘也当锚点 (⇒ 后面孤儿可以接着连)
                anchor_xy.append((cx, cy))
        # ★★★2026-11-05 03:0x **第三遍 (新): 还没接上的 GND 焊盘 ⇒ 直接在焊盘下方落过孔 (焊盘内过孔)**
        #   ★**为什么必须这样**: 前两遍都要**在焊盘外面找空间** ⇒ 密集器件区 (0402/0603 旁边
        #   全是别的网焊盘) ⇒ ★**被围死的焊盘永远找不到过孔位** ⇒ 实测 36 个 GND 焊盘一根铜都没接上
        #   ⇒ ★**焊盘内过孔 (via-in-pad) 是唯一解**: 过孔落在焊盘自己的铜里 ⇒
        #     ① 不需要任何走线空间 ② 净距天然满足 (同网) ③ 直接落到 L2/L6 的 GND 平面
        #   ★**焊盘尺寸判据**: 焊盘短边 ≥ 0.70mm 才放得下 Ø0.6 过孔 (+0.05 边距)
        #   ★**孔间距**: 与已有过孔孔心距 ≥0.60mm (0.3 钻 + 0.25 孔间距)
        orphan3 = [p for p in pads if p not in done_pads]
        for pad in orphan3:
            _ref, _num, cx, cy, _layers = pad
            # 找这个焊盘的矩形 (同网)
            rect = None
            for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
                if n2 == net_g and x0 - 0.01 <= cx <= x1 + 0.01 and y0 - 0.01 <= cy <= y1 + 0.01:
                    rect = (x0, y0, x1, y1)
                    break
            if not rect:
                continue
            x0, y0, x1, y1 = rect
            _short = min(x1 - x0, y1 - y0)
            # ★★2026-11-05 21:35 **孔必须整个待在焊盘铜里** (★孔径 + 0.10 边距)
            #   ★原判据 `_short<0.55` ⇒ 0.55~0.70 的焊盘用 Ø0.5 孔 ⇒ 只剩 0.025mm 铜边 ⇒ 孔探出铜面
            if _short < (VIA_DIA_S + 0.10):
                why["inpad_small"] = why.get("inpad_small", 0) + 1
                continue
            # ★★2026-11-05 07:40 **小焊盘用缩小过孔** (0.55~0.70 宽的焊盘 ⇒ Ø0.60 放不下)
            if _short >= 0.70:
                _dia, _drill = VIA_DIA, VIA_DRILL
            else:
                _dia, _drill = VIA_DIA_S, VIA_DRILL_S
            # ★孔间距: 已有过孔
            # ★★2026-11-05 19:40 **v34: 异网 ⇒ 0.80mm (铜到铜)** (★GND 是异网 ⇒ 用异网档)
            if any(math.hypot(cx - vx, cy - vy) < (MIN_VIA_CENTER if vn == net_g else MIN_VIA_CENTER_XNET)
                   for (vn, vx, vy, _l1, _l2) in self.vias):
                why["inpad_spacing"] = why.get("inpad_spacing", 0) + 1
                continue
            # ★**过孔所在位置的铜净距**: 同网焊盘不算, 但别的网不能挨着
            idx = self._idx(self._ci(cx), self._cj(cy))
            bad = False
            for (n2, ax, ay, bx, by) in self.pad_rects:
                if n2 == net_g:
                    continue
                if x0 - 0.05 <= cx <= x1 + 0.05 and y0 - 0.05 <= cy <= y1 + 0.05:
                    bad = True
                    break
            # ★★2026-11-05 08:22 **改用几何精确判据** (★halo[2] 的 0.95mm 半径太严 ⇒ 密集区放不下)
            if not bad and not self._via_exact_ok(cx, cy, _dia, net_g, _drill):
                bad = True
            if bad:
                why["inpad_busy"] = why.get("inpad_busy", 0) + 1
                continue
            # ★落过孔 (F.Cu..B.Cu ⇒ 穿过 L2/L6 的 GND 平面 ⇒ 直接接地)
            # ★**不加"焊盘→过孔"的短引线**: 过孔就在焊盘中心 ⇒ 那条引线是**零长段** ⇒ DRC 报 dangling
            #   (实测 v12: "删零长段 434") ⇒ ★焊盘与过孔同点 ⇒ **铜直接连通, 不需要引线**
            if self._via_exists(net_g, cx, cy):
                # ★重复过孔 ⇒ DRC `holes_co_located` ⇒ 跳过 (★已有一个同点同网过孔)
                ok += 1
                fail -= 1
                continue
            # ★★2026-11-05 13:15 **孔中心距判据** (★治 DRC `hole_to_hole`)
            #   ★`_via_exists` 只查**同点** ⇒ ★**中心只差 0.25mm 的两个孔也能各落一个**
            #   ⇒ ★v29_N 实测 3 处 `hole_to_hole` (净距 0.0000/0.2000/0.0536mm) ⇒ 就是这么来的
            if not self._via_center_ok(cx, cy):
                why["via_too_close"] = why.get("via_too_close", 0) + 1
                continue
            v = pcbnew.PCB_VIA(self.b)
            v.SetPosition(pcbnew.VECTOR2I(int(cx * MM), int(cy * MM)))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetWidth(pcbnew.FromMM(_dia))
            v.SetDrill(pcbnew.FromMM(_drill))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetNetCode(netcode(self.b, net_g))
            self.b.Add(v)
            _tup = (net_g, cx, cy, 0, 5)
            self.vias.append(_tup)
            # ★★同上: ★**登记 _committed** ⇒ commit() 不会把同一个孔再画一遍
            _cm = getattr(self, "_committed", None)
            if _cm is None:
                _cm = self._committed = {}
            _cm[id(_tup)] = (_tup, v)
            self._add_via_hash(cx, cy, net_g)     # ★★2026-11-05 13:55 **焊盘内过孔也要进 via_hash**
            self._add_via_halo(net_g, cx, cy, 0, 5)
            # ★**过孔直接落在焊盘里 ⇒ 焊盘自己就接到平面了** (不需要任何走线)
            ok += 1
            fail -= 1
            # ★★2026-11-05 21:35 **登记 done_pads** (★第四遍按孤儿表工作 ⇒ 别再给它落一个孔)
            done_pads.append(pad)

        # ---------- 4) ★★2026-11-05 07:40 **窄焊盘 (连接器排针类) 沿长轴引出去落过孔**
        #   ★**问题形态**: 0.275×0.9 / 0.3×1.3 的连接器 GND 焊盘 ⇒ **短边太窄放不下任何过孔**
        #     ⇒ 前三遍全灭 (escape_stub 返回 None / A* 出不去 / inpad_small)
        #   ★**解法**: 沿焊盘的**长轴** (垂直于排针方向) 往外扫 0.8~2.5mm ⇒
        #     找到一块**有空间放过孔**的地方 ⇒ 焊盘 → 一小段同层走线 → 过孔 → GND 平面
        #   ★**走线沿长轴 ⇒ 天然避开同排的邻脚** ⇒ 再过一遍 `_geom_clear` 确认净距
        orphan4 = [p for p in pads if p not in done_pads]
        for pad in orphan4:
            _ref, _num, cx, cy, _layers = pad
            rect = None
            for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
                if n2 == net_g and x0 - 0.01 <= cx <= x1 + 0.01 and y0 - 0.01 <= cy <= y1 + 0.01:
                    rect = (x0, y0, x1, y1)
                    break
            if not rect:
                continue
            x0, y0, x1, y1 = rect
            _short = min(x1 - x0, y1 - y0)
            if _short >= 0.55:
                continue          # ★第三遍能处理
            _long_y = (y1 - y0) > (x1 - x0)     # ★长轴是 y 还是 x
            placed = False
            for _d in (0.9, 1.3, 1.7, 2.1, 2.5):
                for _s in (1, -1):
                    vx = cx if _long_y else cx + _s * _d
                    vy = cy + _s * _d if _long_y else cy
                    # ① 走线净距 (别的网铜)
                    if not self._geom_clear(net_g, [(cx, cy, vx, vy)], 0, W_SIG):
                        continue
                    # ② 孔间距
                    # ★★2026-11-05 19:40 **v34: 异网 ⇒ 0.80mm (铜到铜)**
                    if any(math.hypot(vx - ox, vy - oy) < (MIN_VIA_CENTER if vn == net_g else MIN_VIA_CENTER_XNET)
                           for (vn, ox, oy, _a, _b) in self.vias):
                        continue
                    # ③ 过孔位真能放 (★改用**几何精确**判据 ★不用 halo[2] 的 0.95mm)
                    idx = self._idx(self._ci(vx), self._cj(vy))
                    if not self._via_exact_ok(vx, vy, VIA_DIA, net_g, VIA_DRILL):
                        continue
                    # ★落: 焊盘 → 短走线 → 过孔
                    self.tracks.append((net_g, cx, cy, vx, vy, 0, W_SIG))
                    v = pcbnew.PCB_VIA(self.b)
                    v.SetPosition(pcbnew.VECTOR2I(int(vx * MM), int(vy * MM)))
                    v.SetViaType(pcbnew.VIATYPE_THROUGH)
                    v.SetWidth(pcbnew.FromMM(VIA_DIA))
                    v.SetDrill(pcbnew.FromMM(VIA_DRILL))
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                    v.SetNetCode(netcode(self.b, net_g))
                    self.b.Add(v)
                    _tup = (net_g, vx, vy, 0, 5)
                    self.vias.append(_tup)
                    # ★★同上: ★**登记 _committed** ⇒ commit() 不会把同一个孔再画一遍
                    _cm = getattr(self, "_committed", None)
                    if _cm is None:
                        _cm = self._committed = {}
                    _cm[id(_tup)] = (_tup, v)
                    self.via_cells.setdefault(idx, []).append((vx, vy))
                    self._add_via_hash(vx, vy, net_g)
                    self._add_via_halo(net_g, vx, vy, 0, 5)
                    ok += 1
                    fail -= 1
                    placed = True
                    break
                if placed:
                    break
            if not placed:
                why["narrow"] = why.get("narrow", 0) + 1
        return (ok, fail)

    def _ring_cells(self, cx, cy, r_mm):
        """以 (cx,cy) 为心、半径 r_mm 的候选单元 (按距离排序)"""
        r = r_mm / self.g
        i0, j0 = self._ci(cx), self._cj(cy)
        out = []
        for dj in range(-int(r) - 1, int(r) + 2):
            for di in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(di, dj)
                if 0.6 <= d <= r:
                    out.append((d, i0 + di, j0 + dj))
        out.sort()
        return [(i, j) for (_d, i, j) in out]

    def _via_room_score(self, cx, cy, dia, net):
        """★2026-11-05 22:4x **过孔落点的"余量分"** (★越大越宽松; 同网铜不算)
           ★**为什么需要**: 窄焊盘里挑孔心时, 光看"合不合法"不够 ⇒ ★**要挑净距最大的**
           ★**只算别网的铜** (焊盘 + 走线) ⇒ ★**未来的走线算不了**
             ⇒ ★**所以还要尽量远离别的网焊盘** (★邻居的逃逸短桩通常从它的焊盘出发)
             ⇒ ★**这正是 U_TEMP.2 的解法**: 孔心往远离 `U_TEMP.1` 的方向挪 ⇒ 净距 0.125 → 0.30
        """
        _r = dia / 2.0
        _m = 1e9
        for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
            if n2 == net:
                continue
            dx = max(x0 - cx, 0.0, cx - x1)
            dy = max(y0 - cy, 0.0, cy - y1)
            _m = min(_m, math.hypot(dx, dy) - _r)
        for s in self.tracks:
            if s[0] == net:
                continue
            d = _pt_seg_dist(cx, cy, s[1], s[2], s[3], s[4])
            _m = min(_m, d - _r - s[6] / 2.0)
        return _m

    def _narrow_pad_candidates(self, cx, cy, net, dia, used_vias):
        """★2026-11-05 22:4x **窄焊盘的下拉孔落点候选** (★孔心在焊盘铜内 + 余量最大)
           ★**实测依据**: `U_TEMP.2` 焊盘 0.45x0.30 ⇒ Ø0.5 孔必然探出铜面 (★**不是错**)
             ⇒ ★**错在孔心偏心 0.195mm** ⇒ 压住邻居 `U_TEMP.1`(I2C_B_SCL) 的逃逸短桩
               ⇒ 净距 0.125 ✘ (v35_R 的 DRC 2)
             ⇒ 焊盘中心 ⇒ 净距 0.2085 ✔ ; 往远离邻居的方向挪 0.10 ⇒ 净距 **0.30** ✔
           ★**注意**: ★**不许吸附到 0.25 栅格** (★实测吸附后净距 0.184 ✘)
           ★**候选集**: 中心 + ±0.05/±0.10 (y) + ±0.05 (x) + 四角 ⇒ 过滤"必须在焊盘铜内"
           ★**返回**: 至多 1 个落点 (余量分最大的那个)
        """
        _best = None
        _bs = -1e9
        for (_ox, _oy) in ((0.0, 0.0), (0.0, 0.05), (0.0, -0.05), (0.0, 0.10), (0.0, -0.10),
                           (0.05, 0.0), (-0.05, 0.0), (0.05, 0.05), (-0.05, 0.05),
                           (0.05, -0.05), (-0.05, -0.05)):
            _px, _py = cx + _ox, cy + _oy
            if self._pad_rect_at(_px, _py, net) is None:
                continue
            if self._via_exists(net, _px, _py):
                continue
            _bad = False
            for (ux, uy) in used_vias:
                if math.hypot(_px - ux, _py - uy) < 0.60:
                    _bad = True
                    break
            if _bad:
                continue
            _sc = self._via_room_score(_px, _py, dia, net) - 0.05 * math.hypot(_ox, _oy)
            if _sc > _bs:
                _bs = _sc
                _best = (_px, _py)
        if _best is None:
            return []
        return [_best]

    def _place_in_pad_via(self, net_g, px, py, dia, drill, used_vias):
        """★2026-11-05 22:4x **在焊盘铜里落一个下拉孔** (★第一遍窄焊盘用)
           ★**判据**: ① 孔心在**同网焊盘**矩形内 ② `_via_exact_ok` (别网铜/孔距/净距)
                      ③ 与本轮已用孔心距 ≥ 0.60
           ★**返回**: True = 已落 (★调用方负责登记 done_pads / used_vias)
           ★**注意**: ★**与第一遍原来的落孔步骤逐行一致** (不额外加 via_hash ⇒ 行为不漂移)
        """
        if self._pad_rect_at(px, py, net_g) is None:
            return False
        if self._via_exists(net_g, px, py):
            return False
        for (ux, uy) in used_vias:
            if math.hypot(px - ux, py - uy) < 0.60:
                return False
        if not self._via_exact_ok(px, py, dia, net_g, drill):
            return False
        _v = pcbnew.PCB_VIA(self.b)
        _v.SetPosition(pcbnew.VECTOR2I(int(px * MM), int(py * MM)))
        _v.SetViaType(pcbnew.VIATYPE_THROUGH)
        _v.SetWidth(pcbnew.FromMM(dia))
        _v.SetDrill(pcbnew.FromMM(drill))
        _v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        _v.SetNetCode(netcode(self.b, net_g))
        self.b.Add(_v)
        _tup = (net_g, px, py, 0, 5)
        self.vias.append(_tup)
        _cm = getattr(self, "_committed", None)
        if _cm is None:
            _cm = self._committed = {}
        _cm[id(_tup)] = (_tup, _v)
        self._add_via_halo(net_g, px, py, 0, 5)
        return True

    def _pad_rect_at(self, x, y, net=None):
        """★2026-11-05 21:35 **查这个点落在哪个(同网)焊盘的矩形里** ⇒ 返回 (x0,y0,x1,y1) 或 None
           ★**为什么需要**: 第一遍"焊盘内直接落孔"要在**焊盘铜里面**落孔
           ⇒ 但 `_in_pad` 只说"在某个焊盘里" (可能是别的网的焊盘) ⇒ ★**给不出尺寸**
           ⇒ 尺寸判据 (孔径+0.10) 必须知道**这个孔到底属于哪个焊盘**"""
        for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
            if net is not None and n2 != net:
                continue
            if x0 - 0.01 <= x <= x1 + 0.01 and y0 - 0.01 <= y <= y1 + 0.01:
                return (x0, y0, x1, y1)
        return None

    def _in_pad(self, x, y):
        """这个点是不是落在某个焊盘里 (过孔不许打在焊盘上 = via-in-pad)"""
        for (net, x0, y0, x1, y1) in self.pad_rects:
            if x0 - 0.05 <= x <= x1 + 0.05 and y0 - 0.05 <= y <= y1 + 0.05:
                return True
        return False

    def _gnd_escape(self, net, pad):
        """★GND 焊盘自身格子被封死时 ⇒ 往外找能起步的格子
           返回 (start_cells, stub_start) —— stub_start = (焊盘x, 焊盘y, 出脚x, 出脚y)"""
        _ref, _num, cx, cy, _layers = pad
        # 1) 焊盘格本身能走吗?
        i0, j0 = self._ci(cx), self._cj(cy)
        idx0 = self._idx(i0, j0)
        nb = 0
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                if self._free(0, self._idx(i0 + di, j0 + dj), net, 1):
                    nb += 1
        if nb:
            return list(self._pad_cells(net, pad)), None
        # 2) 往外找: 半径 0.5/1.0/1.5/2.0mm 的环, 找**空位且邻居能走**的格
        for r_mm in (0.5, 1.0, 1.5, 2.0, 2.5):
            rr = r_mm / self.g
            for (di, dj) in _ring_offsets(rr):
                i, j = i0 + di, j0 + dj
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                idx = self._idx(i, j)
                if not self._free(0, idx, net, 1):
                    continue
                # ★这个格子的邻居也得能走 (不然 A* 起步就死)
                ok = False
                for dj2 in (-1, 0, 1):
                    for di2 in (-1, 0, 1):
                        if di2 == 0 and dj2 == 0:
                            continue
                        if self._free(0, self._idx(i + di2, j + dj2), net, 1):
                            ok = True
                            break
                    if ok:
                        break
                if not ok:
                    continue
                ex, ey = self._cx(i), self._cy(j)
                # ★直道本身要干净 (不许穿过别的网)
                if not self._stub_clear(net, cx, cy, ex, ey):
                    continue
                return [(0, idx)], (cx, cy, ex, ey)
        return [], None

    def _via_exact_ok(self, cx, cy, dia, net, drill=VIA_DRILL):
        """★**几何精确的过孔可落性判据** (★2026-11-05 08:22)
        ★**为什么不能用 `_via_free_all`**: 它用 **halo[2]** 判 ⇒ 半径 = CLEAR+VIA_DIA/2+W_CLS[2]/2+MARGIN
          = 0.20+0.30+0.25+0.20 = **0.95mm** ⇒ ★**密集区任何过孔都放不下**
          ⇒ ⇒ 实测: GND 焊盘内过孔 **inpad_busy=10 / narrow=10** ⇒ 20 个 GND 焊盘一根铜都没有
          ⇒ ⇒ ★**而且同样的过严判据也在压制长线的换层 ⇒ 那 52 个"真被堵死"有一部分是这么来的**
        ★**精确判据** (按真实铜算, 不按栅格保守半径):
          ① 孔盘外缘到**别的网焊盘** ≥ 0.20mm
          ② 孔盘外缘到**别的网走线** ≥ 0.20mm
          ③ 孔心到已有过孔 ≥ 0.60mm (孔间距)
          ④ 孔心到别的网焊盘的**孔** ≥ 0.25mm (孔净距)
        """
        _r = dia / 2.0
        # ① 别的网焊盘 (同网不算)
        for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
            if n2 == net:
                continue
            dx = max(x0 - cx, 0.0, cx - x1)
            dy = max(y0 - cy, 0.0, cy - y1)
            if math.hypot(dx, dy) < _r + CLEAR:
                return False
        # ② 别的网走线 (同网不算)
        for s in self.tracks:
            if s[0] == net:
                continue
            d = _pt_seg_dist(cx, cy, s[1], s[2], s[3], s[4])
            if d < _r + CLEAR + s[6] / 2.0:
                return False
        # ③ 孔间距 (孔心到已有过孔) —— ★★2026-11-05 13:55 **删掉"同网不算"**
        #   ★**为什么必须删**: 孔到孔是**制造规则** (钻孔/电镀工艺) ⇒ ★**跟网一点关系都没有**
        #     ⇒ ★**原来写 `if vn == net: continue` ⇒ 同网的两个孔可以贴到 0.50mm ⇒ DRC 必报 `hole_to_hole`**
        #     ⇒ ★**实测 v30_P 唯一那条 DRC 就是这么来的**: 两个 **GND** 孔 @24.45/24.95, y=60.2 (中心距 0.50mm, 净距 0.2000mm)
        #   ⇒ ⇒ **同网异网一律按 0.60mm 中心距卡**
        # ★★2026-11-05 19:40 **v34: 异网还要过"铜到铜" 0.80mm** (★见常量区根因注释)
        #   ⇒ ★**同网 0.58 (孔到孔) / 异网 0.80 (铜到铜)** ⇒ ★**只改布出来的几何**
        for (vn, vx, vy, _l1, _l2) in self.vias:
            _need = MIN_VIA_CENTER if vn == net else MIN_VIA_CENTER_XNET
            if math.hypot(cx - vx, cy - vy) < _need:
                return False
        # ④ 孔净距 (别的网的孔) —— ★**同理: 孔到孔净距也不分网**
        for (vn, vx, vy, _l1, _l2) in self.vias:
            if math.hypot(cx - vx, cy - vy) < drill / 2.0 + 0.25:
                return False
        return True

    def _gnd_drop_esc_ok(self, ref, pad_y, via_y):
        """★★GND 下拉孔不许落在"连接器差分脚逃逸走廊"里 (★v33_S, env 门控默认关)
           ★**规则**: 对 `PCB_CONN_GND_ESCAPE` 里指定的连接器 (如 CONN_CAM),
             它的焊盘的 GND 下拉孔心到**焊盘行的垂直距离**必须 ≥ MIN
           ★**为什么**: 孔落在焊盘正下方 1.2mm ⇒ 与 0.5mm pitch 的差分脚交错成栅栏
             ⇒ 把连接器下方的空带切成 0.75mm 的缝 ⇒ 差分脚逃不出去
           ★**默认 (CONN_GND_ESC 为空) ⇒ 永远返回 True ⇒ 行为完全不变**
        """
        if not CONN_GND_ESC or not ref:
            return True
        _min = CONN_GND_ESC.get(ref)
        if _min is None:
            return True
        _dir = CONN_GND_ESC_DIR.get(ref, "ANY")
        if _dir == "DOWN":
            # ★孔必须往 y 增大方向躲 (KiCad 坐标 y 向下增大)
            return (via_y - pad_y) >= _min
        if _dir == "UP":
            return (pad_y - via_y) >= _min
        return abs(via_y - pad_y) >= _min

    def _via_site_ok(self, idx, net, cx, cy, dia=VIA_DIA):
        """★**过孔落点的"精确几何"判据** (2026-11-05 10:10)
        ★**为什么不能用 `_free` + `_via_free_all`**: 它们都按 **halo[2]** 判
          ⇒ 半径 = CLEAR + VIA_DIA/2 + W_CLS[2]/2 + MARGIN = 0.20+0.30+0.25+0.20 = **0.95mm**
          ⇒ ★**密集器件区一个过孔都放不下** ⇒ 实测: GND 焊盘 25 个一根铜都没有 (unconnected 里 GND 占 50)
        ⇒ ★**这里改用真实铜算**: 板边 + 每层占用 + `_via_exact_ok` (0.20mm 净距 / 0.60mm 孔间距)
        ⇒ ★**规则没放松** (还是 0.2mm 净距), 只是**不再用保守半径代替真实几何**"""
        if self.edge_d[idx] < EDGE_CLEAR + dia / 2.0 - 1e-6:
            return False
        for li in range(NLAYERS):
            c = self.cu[li].get(idx)
            if c is not None and c != net:
                return False
        return self._via_exact_ok(cx, cy, dia, net)

    def _via_free_all(self, idx, net):
        """通孔 (贯穿 6 层) 在所有层都要有净距"""
        # ★板边: 通孔盘 0.6mm ⇒ 盘外缘距真板边 ≥ 0.5mm ⇒ 孔心距 ≥ 0.8mm
        if self.edge_d[idx] < EDGE_CLEAR + VIA_DIA / 2.0 - 1e-6:
            return False
        for li in range(NLAYERS):
            c = self.cu[li].get(idx)
            if c is not None and c != net:
                return False
            s = self.halo[2][li].get(idx)
            if s and (s - {net}):
                return False
        return True

    # ------------------------------------------------ 后处理: 删退化图元
    def cleanup_geometry(self, verbose=True):
        """★★ **布线后处理** (★落盘前最后一道闸) —— ★**目的: DRC 归零**

        ★**为什么必须有这一步 (不是"擦屁股", 是"兜底")**:
          路由器在"出脚直道 → 栅格路径"的衔接处会留下两类退化图元:
            ① **零长段** (start == end) —— ★KiCad 直接报 `track_dangling`
               (实测: 一条 0.0000mm 的 track = 两个端点重合 ⇒ KiCad 认为它没接上)
            ② **接不上的短段** —— ★层间过渡段的两端没有落到过孔上
               (过孔被 `_via_too_close` 跳过 ⇒ 铜从一层"跳"到另一层但中间没孔)
        ★**只改布出来的几何** —— ★**绝不改板子的设计规则** (min hole / clearance 都不许动)

        算法:
          1) 删零长段 (start == end)
          2) 统计每个"点" (焊盘 / 过孔 / 段端点) 被几个图元碰到
             某个端点**只被本段碰到**且**不在任何焊盘/过孔上** ⇒ 悬空 ⇒ 删整段
             ★**同层的 T 型接头算"接上"** (端点落在另一段的中段上 ⇒ 铜是连通的)
          3) 迭代到收敛 (删掉一段 ⇒ 相邻段的端点可能跟着悬空)
        返回 (删掉的段数, 删掉的过孔数)"""
        EPS = 1e-4

        # ---------- 1) 删零长段 ----------
        n0 = len(self.tracks)
        # ★★2026-11-05 07:15 **已提交到板上的零长段也要真删** (否则板上留 ~565 条退化段 ⇒ DRC 红)
        _keep0 = []
        for s in self.tracks:
            if abs(s[1] - s[3]) < EPS and abs(s[2] - s[4]) < EPS:
                self._drop_committed(s)
            else:
                _keep0.append(s)
        self.tracks = _keep0
        n_zero = n0 - len(self.tracks)

        # ---------- 索引 ----------
        # 焊盘 (同网) 的矩形覆盖 —— ★焊盘**面积**内的端点都算接上 (不只中心)
        pad_by_layer = defaultdict(list)
        for (net, x0, y0, x1, y1, layers) in self.pad_rects_l:
            for li in layers:
                pad_by_layer[li].append((net, x0, y0, x1, y1))
        # 过孔点 —— ★过孔是**通孔** (F.Cu..B.Cu) ⇒ 6 层都算接上
        # ★★2026-11-05 13:15 **按网记过孔点** (★原来只是个 set ⇒ **别网的过孔也算"接上"**)
        #   ⇒ ★**别网过孔上的那段铜在 KiCad 眼里是"悬空"** ⇒ DRC `track_dangling`
        #   ⇒ ★v29_N 实测 3 条 `track_dangling` 就是这么漏下来的
        via_pts = defaultdict(set)
        for (net, x, y, l1, l2) in self.vias:
            for li in range(NLAYERS):
                via_pts[(li, round(x, 4), round(y, 4))].add(net)

        def _on_pad(net, li, x, y):
            for (n2, x0, y0, x1, y1) in pad_by_layer.get(li, ()):
                if n2 == net and x0 - EPS <= x <= x1 + EPS and y0 - EPS <= y <= y1 + EPS:
                    return True
            return False

        # 段的空间哈希 (1mm 格) —— 用来判 T 型接头 (端点落在别段中段上)
        CELL = 1.0
        seg_hash = defaultdict(list)
        for i, s in enumerate(self.tracks):
            x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
            for ci in range(int(math.floor(min(x1, x2) / CELL)),
                            int(math.floor(max(x1, x2) / CELL)) + 1):
                for cj in range(int(math.floor(min(y1, y2) / CELL)),
                                int(math.floor(max(y1, y2) / CELL)) + 1):
                    seg_hash[(ci, cj)].append(i)

        def _t_junction(net, li, x, y, self_idx):
            """端点 (x,y) 是否落在**同网同层**另一段的中段上 (⇒ 铜是连通的)"""
            key = (int(math.floor(x / CELL)), int(math.floor(y / CELL)))
            for j in seg_hash.get(key, ()):
                if j == self_idx:
                    continue
                s = self.tracks[j]
                if s[0] != net or s[5] != li:
                    continue
                if _pt_seg_dist(x, y, s[1], s[2], s[3], s[4]) <= s[6] / 2.0 + EPS:
                    return True
            return False

        # ---------- 2) 删悬空端段 + 3) 删孤立过孔 (★★迭代到不动点) ----------
        # ★★2026-11-05 13:15 **改成"删孔 → 再删悬空段 → 再删孔"循环到不动点**
        #   ★**为什么**: 原来顺序是"先删悬空段, 再删孤立过孔"
        #     ⇒ ★**孔被删了, 挂在它上面的那段短铜就变成悬空了, 但没人再去查一遍**
        #     ⇒ ★v29_N 实测: 3 条 `track_dangling` (GND, 0.25mm 短铜, 端点悬空) 就是这么漏下来的
        #   ⇒ ★**每轮: 先删没有走线接上的孤立过孔, 再删悬空段, 直到两轮都不再变**
        n_dang = 0
        n_via_drop = 0
        for _round in range(12):
            # ---------- 3) 删没有走线接上的孤立过孔 (KiCad 报 via_dangling) ----------
            touch = set()
            for s in self.tracks:
                touch.add((s[0], s[5], round(s[1], 4), round(s[2], 4)))
                touch.add((s[0], s[5], round(s[3], 4), round(s[4], 4)))
            _vd = 0
            keep_v = []
            for v in self.vias:
                net, x, y = v[0], v[1], v[2]
                anchored = False
                for li in range(NLAYERS):
                    if (net, li, round(x, 4), round(y, 4)) in touch:
                        anchored = True
                        break
                if not anchored and not _on_pad(net, 0, x, y):
                    _vd += 1
                    self._drop_committed(v)     # ★已提交的孤立过孔也要从板上删掉
                    continue
                keep_v.append(v)
            self.vias = keep_v
            n_via_drop += _vd

            # ---------- 3b) ★★2026-11-05 13:55 **删"孔中心距不够"的过孔** (治 `hole_to_hole`)
            #   ★**为什么必须放在这里**: 实测 v30_P 仍有 1 条 `hole_to_hole`
            #     (GND 孔 @24.45 / 24.95, y=60.2 ⇒ **中心距只有 0.50mm**, 净距 0.2000mm)
            #   ⇒ ★**根因 = 各落孔路径各查各的数据源, 互相看不见**:
            #     A* 查 `via_hash` · 窄焊盘查 `self.vias` · 焊盘内查 `_via_center_ok`
            #     ⇒ ★**漏网的那对就是跨路径落下来的**
            #   ⇒ ★**兜底放 cleanup (唯一权威 = `self.vias`)**: 任何两条中心距 < MIN_VIA_CENTER 的孔 ⇒ 删后落的那个
            #     ⇒ ★**代价**: 被删孔对应的焊盘会变未连接 (+1 unconnected) ⇒ ★**宁可 unconnected 多一条, 也不要 DRC 违规**
            _vd_sp = 0
            keep_v2 = []
            for _v in self.vias:
                _vx, _vy = _v[1], _v[2]
                _bad_sp = False
                for (_n2, _x2, _y2, _a, _b) in keep_v2:
                    if math.hypot(_vx - _x2, _vy - _y2) < MIN_VIA_CENTER:
                        _bad_sp = True
                        break
                if _bad_sp:
                    _vd_sp += 1
                    self._drop_committed(_v)
                    continue
                keep_v2.append(_v)
            if _vd_sp:
                self.vias = keep_v2
                n_via_drop += _vd_sp

            # ---------- 2) 删悬空端段 (同层 · ★**同网才算接上**) ----------
            # 每个点的"段端点计数" (★**按网** ⇒ 别网的段端点不算接上)
            ep_cnt = defaultdict(int)
            for s in self.tracks:
                ep_cnt[(s[0], s[5], round(s[1], 4), round(s[2], 4))] += 1
                ep_cnt[(s[0], s[5], round(s[3], 4), round(s[4], 4))] += 1
            drop = set()
            for i, s in enumerate(self.tracks):
                net, li = s[0], s[5]
                _bad = False
                for (px, py) in ((s[1], s[2]), (s[3], s[4])):
                    _vp = via_pts.get((li, round(px, 4), round(py, 4)))
                    if _vp and net in _vp:
                        continue                      # 落在**同网**过孔上 ⇒ 接上
                    if _vp:
                        _bad = True                   # ★落在**别网**过孔上 ⇒ 那是短路 ⇒ 删
                        break
                    if _on_pad(net, li, px, py):
                        continue                      # 落在焊盘上 ⇒ 接上
                    if ep_cnt.get((net, li, round(px, 4), round(py, 4)), 0) > 1:
                        continue                      # 别的**同网**段端点也在 ⇒ 接上
                    if _t_junction(net, li, px, py, i):
                        continue                      # T 型接头 ⇒ 接上
                    _bad = True                       # ★悬空
                    break
                if _bad:
                    drop.add(i)
            if not drop:
                if _vd + _vd_sp == 0:
                    break                          # ★不动点 ⇒ 收工
                continue                           # ★还有孔被删 ⇒ 下一轮再查悬空
            # 删掉悬空段后重建哈希
            keep = [s for i, s in enumerate(self.tracks) if i not in drop]
            n_dang += len(self.tracks) - len(keep)
            # ★★已提交的悬空段也要从板上删掉 (★阶段性 commit 已经画上去了)
            for i in sorted(drop):
                self._drop_committed(self.tracks[i])
            self.tracks = keep
            seg_hash = defaultdict(list)
            for i, s in enumerate(self.tracks):
                x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
                for ci in range(int(math.floor(min(x1, x2) / CELL)),
                                int(math.floor(max(x1, x2) / CELL)) + 1):
                    for cj in range(int(math.floor(min(y1, y2) / CELL)),
                                    int(math.floor(max(y1, y2) / CELL)) + 1):
                        seg_hash[(ci, cj)].append(i)

        if verbose and (n_zero or n_dang or n_via_drop):
            print("  [CLEAN] 后处理: 删零长段 %d / 删悬空段 %d / 删孤立过孔 %d"
                  % (n_zero, n_dang, n_via_drop))
        return n_zero, n_dang, n_via_drop

    # ------------------------------------------------ 长度配平 (蛇形)
    def add_meander(self, net, extra_mm):
        """给 net 加一段三角凸起, 走线长度增加 extra_mm (mm)
           ★差分对长度配平用 (把短的那根加长)"""
        if extra_mm <= 0.001:
            return 0.0
        segs = self.net_tracks(net)
        best = None
        for s in segs:
            L = math.hypot(s[3] - s[1], s[4] - s[2])
            if L < 2.5:
                continue
            if best is None or L > best[0]:
                best = (L, s)
        if best is None:
            return 0.0
        L, s = best
        ux, uy = (s[3] - s[1]) / L, (s[4] - s[2]) / L
        base = min(L * 0.8, 8.0)
        # 三角凸起: extra = 2*sqrt((base/2)^2 + a^2) - base  ⇒  解 a
        val = ((base + extra_mm) / 2.0) ** 2 - (base / 2.0) ** 2
        if val <= 0:
            return 0.0
        a = math.sqrt(val)
        for sign in (1, -1):
            nx, ny = -uy * sign, ux * sign
            mid = ((s[1] + s[3]) / 2.0, (s[2] + s[4]) / 2.0)
            apex = (mid[0] + nx * a, mid[1] + ny * a)
            # ★★★2026-11-05 **整条蛇形都要查净距** ——
            #   上一版只查了顶点 (apex) 一个点 ⇒ ★**两条斜边可以横穿别的网的铜**
            #   ⇒ 实测 DRC: "tracks_crossing" + 2 条 "shorting_items"
            #   (LIGHT_1V8 的 In2.Cu 走线 被 CSI_D0_D0_P 的蛇形斜边横穿)
            #   ⇒ 现在: 拼出 4 段完整几何, **逐段** 对**所有别的网的铜**查净距
            d = base / 2.0
            p_in = (mid[0] - ux * d, mid[1] - uy * d)
            p_out = (mid[0] + ux * d, mid[1] + uy * d)
            cand = [
                (s[1], s[2], p_in[0], p_in[1]),
                (p_in[0], p_in[1], apex[0], apex[1]),
                (apex[0], apex[1], p_out[0], p_out[1]),
                (p_out[0], p_out[1], s[3], s[4]),
            ]
            if not self._geom_clear(net, cand, s[5], s[6]):
                continue
            # ★★2026-11-10 09:2x 【★板边闸 (★env 门控 `PCB_MEANDER_EDGE`★)】 —— 理由同 add_meander_v2
            if MEANDER_EDGE and not all(
                    self._edge_seg_ok(q[0], q[1], q[2], q[3], s[6])
                    for q in cand):
                continue
            self._insert_meander(net, s, mid, apex, ux, uy, base)
            return extra_mm
        return 0.0

    def add_meander_v2(self, net, extra_mm, max_bumps=16):
        """★给 net 增加 extra_mm 长度 —— **多凸起版** (2026-11-05 03:2x)

        ★**上一版 (v1) 为什么对 MIPI 时钟对没用** (实测: CSI_D0_CK Δ=32.4mm / DSI_D0_CK Δ=16.5mm 配平失败):
          ① 只在**一个"最长且 ≥2.5mm"的直段**上加**一个**三角凸起
             ⇒ 时钟对的直段往往很短 (0.25mm 网格 + 蛇形 ⇒ 被拆成很多小段) ⇒ 常常一个都找不到
          ② 加了之后净距不够 ⇒ 直接返回 0 ⇒ 差值原封不动
        ★**v2**: **多凸起 + 逐个候选段试**
          ⇒ 一个 32mm 的差可以拆成 8 个 ~4mm 的小凸起 (每个凸起都按需要的高度算, 高度 ≤3mm 以免被挡)
          ⇒ 每个凸起都单独过 `_geom_clear` (别的网铜净距) ⇒ 不合格就换段/换方向
        返回: 实际增加的长度 (mm)
        """
        added = 0.0
        for _ in range(max_bumps):
            remain = extra_mm - added
            if remain <= 0.01:
                break
            best = None
            for seg in self.net_tracks(net):
                L = math.hypot(seg[3] - seg[1], seg[4] - seg[2])
                if L < 1.2:
                    continue
                ux, uy = (seg[3] - seg[1]) / L, (seg[4] - seg[2]) / L
                base = min(L * 0.8, 8.0)
                val = ((base + remain) / 2.0) ** 2 - (base / 2.0) ** 2
                if val <= 0:
                    continue
                a = math.sqrt(val)
                if a > 3.0:          # ★凸起太高 ⇒ 几乎一定被别的网挡住 ⇒ 换段
                    continue
                mid = ((seg[1] + seg[3]) / 2.0, (seg[2] + seg[4]) / 2.0)
                for sign in (1, -1):
                    nx, ny = -uy * sign, ux * sign
                    apex = (mid[0] + nx * a, mid[1] + ny * a)
                    d = base / 2.0
                    p_in = (mid[0] - ux * d, mid[1] - uy * d)
                    p_out = (mid[0] + ux * d, mid[1] + uy * d)
                    cand = [
                        (seg[1], seg[2], p_in[0], p_in[1]),
                        (p_in[0], p_in[1], apex[0], apex[1]),
                        (apex[0], apex[1], p_out[0], p_out[1]),
                        (p_out[0], p_out[1], seg[3], seg[4]),
                    ]
                    if not self._geom_clear(net, cand, seg[5], seg[6]):
                        continue
                    # ★★2026-11-10 09:2x 【★板边闸 (★env 门控 `PCB_MEANDER_EDGE`★)】
                    #   ★**蛇形是离网格的斜线 ⇒ `_geom_clear` 查不到板边 ⇒ 凸起能出板 (★实测 y=-1.2mm★)**
                    #   ⇒ ★★**⇒ 候选 4 段必须逐段过真板边判据 (★`_edge_seg_ok`★)** ★★
                    if MEANDER_EDGE and not all(
                            self._edge_seg_ok(q[0], q[1], q[2], q[3], seg[6])
                            for q in cand):
                        continue
                    if best is None or L > best[0]:
                        best = (L, seg, mid, apex, ux, uy, base)
                    break
            if best is None:
                break
            _L, seg, mid, apex, ux, uy, base = best
            self._insert_meander(net, seg, mid, apex, ux, uy, base)
            added += remain
        return added

    def add_meander_v3(self, net, extra_mm, max_bumps=24, apex_max=3.0, min_len=0.3):
        """★v3 (2026-11-05 07:25, 07:42 改) —— ★**固定凸起高度, 反算每凸起能补多少**
        ★**v2 的死穴 (实测)**: v2 是"用**剩余差值**反算凸起高度" ⇒
          a = sqrt(((base+remain)/2)^2 - (base/2)^2)
          ⇒ 差值一大 (Δ32.4mm) ⇒ a = 16.7mm ⇒ ★**超过 a≤3.0 的上限 ⇒ 一个凸起都加不上 ⇒ return 0**
          ⇒ ★**差越大越加不上** (完全反了)
        ★**v3**: 固定凸起高度 a=apex_max(=3.0mm) ⇒ 每凸起最多能补
          extra_max(base) = 2*sqrt((base/2)^2 + a^2) - base
          (base=0.96 ⇒ **+5.12mm** · base=2.6 ⇒ +3.94mm · base=8 ⇒ +9.89mm)
          ⇒ ★**一个 32.4mm 的差 = 7 个小凸起** ⇒ 每个都单独过净距检查
        ★**min_len**: 候选直段的最短长度 (v2 是 1.2mm ⇒ ★**很多对的最长单段只有 0.35~1.25mm ⇒ 直接被卡死**
          ⇒ 放宽到 **0.3mm** (同事 07:42 复核: ★**凸起补长能力几乎与直段长短无关, 只看 a**
            ⇒ base=0.283/0.369/0.305 时一个 a=3.0 凸起分别补 +5.72/+5.64/+5.70mm
            ⇒ ⇒ **min_len 放宽到 ≤0.35 ⇒ 那 3 对立刻可配平**)
          ⇒ ★**净距检查 `_geom_clear` 仍在** ⇒ 拉不出违规铜
        ★**自适应凸起高度**: 优先 a=3.0; 不行就退 a=2.0 / a=1.2 (补得少但**空间小、更容易找到位置**)
        返回: 实际增加的长度 (mm)
        """
        added = 0.0
        APEXES = (apex_max, 2.0, 1.2)
        for _ in range(max_bumps):
            remain = extra_mm - added
            if remain <= 0.01:
                break
            best = None
            for seg in self.net_tracks(net):
                L = math.hypot(seg[3] - seg[1], seg[4] - seg[2])
                if L < min_len:
                    continue
                ux, uy = (seg[3] - seg[1]) / L, (seg[4] - seg[2]) / L
                base = min(L * 0.8, 8.0)
                mid = ((seg[1] + seg[3]) / 2.0, (seg[2] + seg[4]) / 2.0)
                for a_try in APEXES:
                    if a_try > apex_max + 1e-6:
                        continue
                    # ★固定 a ⇒ 这一个凸起最多能补多少
                    cap = 2.0 * math.sqrt((base / 2.0) ** 2 + a_try ** 2) - base
                    if cap <= 0.01:
                        continue
                    take = min(remain, cap)
                    # ★**按 take 反算实际凸起高度** (≤ a_try) ⇒ 不会超上限
                    val = ((base + take) / 2.0) ** 2 - (base / 2.0) ** 2
                    if val <= 0:
                        continue
                    a = math.sqrt(val)
                    if a > a_try + 1e-6:
                        continue
                    for sign in (1, -1):
                        nx, ny = -uy * sign, ux * sign
                        apex = (mid[0] + nx * a, mid[1] + ny * a)
                        d = base / 2.0
                        p_in = (mid[0] - ux * d, mid[1] - uy * d)
                        p_out = (mid[0] + ux * d, mid[1] + uy * d)
                        cand = [
                            (seg[1], seg[2], p_in[0], p_in[1]),
                            (p_in[0], p_in[1], apex[0], apex[1]),
                            (apex[0], apex[1], p_out[0], p_out[1]),
                            (p_out[0], p_out[1], seg[3], seg[4]),
                        ]
                        if not self._geom_clear(net, cand, seg[5], seg[6]):
                            continue
                        # ★★2026-11-10 09:2x 【★板边闸 (★env 门控 `PCB_MEANDER_EDGE`★)】
                        #   ★**蛇形是离网格的斜线 ⇒ `_geom_clear` 只查别的网的铜, 查不到板边**
                        #   ⇒ ★★**⇒ 候选 4 段必须逐段过真板边判据 (★`_edge_seg_ok`★)** ★★
                        #   ⇒ ★**实测 (★2026-11-10 09:2x★)**: ★**不开这个闸 ⇒ 四臂 68 条 `copper_edge_clearance`
                        #     100% 来自蛇形凸起 (★实测顶点跑到 y=-1.2mm★) ⇒ ⇒ 每臂 DRC≠0 ⇒ ⇒ 全部 REJECT** ★★
                        if MEANDER_EDGE and not all(
                                self._edge_seg_ok(q[0], q[1], q[2], q[3], seg[6])
                                for q in cand):
                            continue
                        if best is None or take > best[0]:
                            best = (take, seg, mid, apex, ux, uy, base)
                        break
                    if best is not None and best[1] is seg:
                        break
            if best is None:
                break
            _take, seg, mid, apex, ux, uy, base = best
            self._insert_meander(net, seg, mid, apex, ux, uy, base)
            added += _take
        return added

    def _geom_clear(self, net, segs, li, w=W_SIG):
        """★这几段几何 vs **别的网的所有铜** (同层走线 + 所有过孔 + 同层焊盘) 净距够不够?
           ★**蛇形配平必须走这一步** —— 蛇形是**离网格**的斜线 ⇒ 栅格 halo 管不到"""
        for (x1, y1, x2, y2) in segs:
            # --- 同层走线 ---
            for (n2, tx1, ty1, tx2, ty2, tli, tw) in self.tracks:
                if n2 == net or tli != li:
                    continue
                need = w / 2.0 + tw / 2.0 + CLEAR
                if _seg_seg_dist(x1, y1, x2, y2, tx1, ty1, tx2, ty2) < need:
                    return False
            # --- 过孔 (★实际是通孔 F.Cu..B.Cu ⇒ 所有信号层都算) ---
            for (n2, vx, vy, l1, l2) in self.vias:
                if n2 == net:
                    continue
                need = w / 2.0 + VIA_DIA / 2.0 + CLEAR
                if _pt_seg_dist(vx, vy, x1, y1, x2, y2) < need:
                    return False
            # --- 焊盘 (别的网的焊盘 ⇒ 穿过去就是短路) ★只查**本层真有铜**的焊盘
            for (n2, x0, y0, xp1, yp1, layers) in self.pad_rects_l:
                if n2 == net or li not in layers:
                    continue
                need = w / 2.0 + CLEAR
                if self._seg_hits_rect(x1, y1, x2, y2, x0 - need, y0 - need,
                                       xp1 + need, yp1 + need):
                    return False
        return True

    def _on_grid(self, x, y):
        """★这个点【是不是在栅格心】上 (★离网格的铜 = halo 的盲区★)"""
        _i = self._ci(x)
        _j = self._cj(y)
        return (abs(self._cx(_i) - x) < 1e-6 and abs(self._cy(_j) - y) < 1e-6)

    def _seg_clear_geom(self, net, x1, y1, x2, y2, w=W_SIG):
        """★**这段线 vs 【已落的铜 + 已落的孔】的【真实几何】净距** (★不看 halo★)

        ★★**★为什么要单独做一个 (★2026-11-10 15:3x 实测坐实★)★★** ★★
          ★**halo 是按【格】封的, ★而 A* 只判【格】⇒ ⇒ 【离网格的几何】(★出脚直道末端 → 第一个格心
            的那一段 45° 斜线★) ⇒ ★**栅格闸根本看不见它** ⇒ ⇒ 就能贴着孔穿过去** ★★
          ⇒ ★**实测 (★v76mg1 终板★)**: ★**`LIGHT_3V3` 斜线离 GND 下拉孔只有 0.5831mm 中心距
            ⇒ 净距 0.1581mm (★需 0.2000★) ⇒ ★**该臂最严重的一条 DRC** ★★

        ★**判据 (★与板规则一致★)**:
          · ★**别的网的走线**: ★**中心距 ≥ w/2 + 对方半宽 + CLEAR** ★
          · ★**别的网的孔**: ★**中心距 ≥ w/2 + VIA_DIA/2 + CLEAR** ★
          · ★**同网不算** (★同网铜挨着是正常的★)
        ★**默认关 (★env `PCB_ESC_CLR_FIX`★) ⇒ 逐位不变**
        """
        for s in self.tracks:
            if s[0] == net:
                continue
            if s[5] != 0:
                continue
            need = w / 2.0 + s[6] / 2.0 + CLEAR
            if _seg_seg_dist(x1, y1, x2, y2, s[1], s[2], s[3], s[4]) < need - 1e-9:
                return False
        for v in self.vias:
            if v[0] == net:
                continue
            if v[3] > 0:
                continue
            need = w / 2.0 + VIA_DIA / 2.0 + CLEAR
            if _pt_seg_dist(v[1], v[2], x1, y1, x2, y2) < need - 1e-9:
                return False
        return True

    @staticmethod
    def _seg_hits_rect(x1, y1, x2, y2, rx0, ry0, rx1, ry1):
        """线段是否与矩形 (含边界) 相交 / 进入
           ★做法: 沿线取样 + 检查矩形四个角到线段的距离 (两个都做 ⇒ 不漏)"""
        # 1) 矩形四���到线段的距离
        for (px, py) in ((rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1)):
            if _pt_seg_dist(px, py, x1, y1, x2, y2) <= 1e-9:
                return True
        # 2) 线段端点在矩形内
        for (px, py) in ((x1, y1), (x2, y2)):
            if rx0 <= px <= rx1 and ry0 <= py <= ry1:
                return True
        # 3) 线段与矩形边相交 (粗判: 采样足够密)
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.05) + 1)
        for k in range(n + 1):
            t = k / float(n)
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            if rx0 <= px <= rx1 and ry0 <= py <= ry1:
                return True
        return False

    def _free_line(self, pt, net, li):
        """凸起顶点附近有没有别的网的铜"""
        i, j = self._ci(pt[0]), self._cj(pt[1])
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1):
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                    return False
                if not self._free(li, self._idx(i2, j2), net, 1):
                    return False
        return True

    def _insert_meander(self, net, seg, mid, apex, ux, uy, base):
        """把 seg 换成 带三角凸起 的三段"""
        x1, y1 = seg[1], seg[2]
        x2, y2 = seg[3], seg[4]
        li, w = seg[5], seg[6]
        d = (base / 2.0)
        p_in = (mid[0] - ux * d, mid[1] - uy * d)
        p_out = (mid[0] + ux * d, mid[1] + uy * d)
        idx = self.tracks.index(seg)
        new = [
            (net, x1, y1, p_in[0], p_in[1], li, w),
            (net, p_in[0], p_in[1], apex[0], apex[1], li, w),
            (net, apex[0], apex[1], p_out[0], p_out[1], li, w),
            (net, p_out[0], p_out[1], x2, y2, li, w),
        ]
        self.tracks[idx:idx + 1] = new
        for s in new:
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5], s[6])
        return True

    # ------------------------------------------------ 路径 → 铜
    # ------------------------------------------------ rip-up & reroute (收尾杀招)
    def rebuild_halo(self):
        """★**重建净距禁区** (★rip-up 后必须重建 ⇒ 否则被拆的线的 halo 还在 ⇒ 白拆)
        ★**为什么能精确重建**: 实测结构 —— ★**self.cu 只记焊盘与板边**,
          ★**走线/过孔只进 halo** ⇒ ⇒ 所以 halo = f(焊盘, 全部走线, 全部过孔) ⇒ 可重算
        """
        self.halo = [[dict() for _ in range(NLAYERS)] for _ in range(3)]
        self._halo_pads()
        for s in self.tracks:
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5], s[6])
        for (net, x, y, l1, l2) in self.vias:
            self._add_via_halo(net, x, y, l1, l2)
        # ★★**★2026-11-10 12:1x**: ★**halo 重建后要【重铺】预留框 (★不然 rip 后预留失效)** ★★★★
        self._apply_route_reserve()

    def _net_start_cells(self, net):
        """该网各焊盘的**起步格** (有出脚直道则取直道终点, 否则取焊盘中心格)"""
        cells = []
        for pad in self.net_pads.get(net, []):
            try:
                st = self.escape_stub(net, pad)
            except Exception:
                st = None
            if st:
                ax, ay = st
                cells.append((0, self._idx(self._ci(ax), self._cj(ay))))
            else:
                try:
                    cells.extend(self._pad_cells(net, pad))
                except Exception:
                    pass
        return cells

    def _escape_blockers(self, net, maxn=6):
        """★v52: 找出**挡住本网焊盘出脚直道**的别的网走线 (按离焊盘的距离排序)

        ★★**为什么要有这个方法 (2026-11-06 03:0x 实测)**:
          · 官方板 26 个"整张板零铜"的网 ⇒ 失败明细里 **61 条是 A* 找不到路**
          · 其中 **42 条起脚在密集焊盘阵** (J_SOM_P* 16 / CONN_LIGHT 13 / C_AC_CSI_D* 7 / CONN_CAM 6)
          · ⇒ 这些网的 `escape_stub` **出脚直道被别的网已布的铜封死** ⇒ ★**连起步格都没有**
        ★★**为什么旧 rip-up 救不了**:
          `_blockers_for` 只查**起步格附近**别的网的走线 ⇒ ★**看不到出脚走廊上的封堵**
          ⇒ 实测: rip-up 19 个候选网 **一根线都没拆** (per-net 输出 0 行)
        ★**做法**: 照 `escape_stub` 的候选 (4 方向 × ESC_LENS 长度) 逐条算
          哪条别的网的走线会让 `_stub_vs_routed` 判失败 ⇒ 那就是封堵者
        """
        out = []
        for pad in self.net_pads.get(net, []):
            try:
                cx, cy = pad[2], pad[3]
            except Exception:
                continue
            for (dx, dy) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                for ln in ESC_LENS:
                    ex, ey = cx + dx * ln, cy + dy * ln
                    for s in self.tracks:
                        if s[0] == net:
                            continue
                        if s[5] != 0:
                            continue
                        tw = s[6]
                        need = W_MIN / 2.0 + tw / 2.0 + CLEAR + (0.0 if tw <= 0.21 else 0.025)
                        if _seg_seg_dist(cx, cy, ex, ey, s[1], s[2], s[3], s[4]) < need - 1e-9:
                            dd = _pt_seg_dist(cx, cy, s[1], s[2], s[3], s[4])
                            out.append((dd, s))
                            break
        out.sort(key=lambda t: t[0])
        seen = set()
        res = []
        for (dd, s) in out:
            k = id(s)
            if k in seen:
                continue
            seen.add(k)
            res.append((dd, s))
        return res[:maxn]

    def _blockers_for(self, net, cells, maxn=6):
        """★找出**挡住这些起步格**的别的网的走线 (按几何距离从近到远)"""
        out = []
        for s in self.tracks:
            if s[0] == net:
                continue
            for (li, idx) in cells:
                if s[5] != li:
                    continue
                i, j = idx % self.W, idx // self.W
                cx, cy = self._cx(i), self._cj(j)
                d = _pt_seg_dist(cx, cy, s[1], s[2], s[3], s[4])
                if d < CLEAR + s[6] / 2.0 + HALO_MARGIN + self.g:
                    out.append((d, s))
                    break
        out.sort(key=lambda t: t[0])
        return out[:maxn]

    def stitch_same_net(self, nets=None, width=0.30, verbose=False):
        """★★**同网缝合** (2026-11-05 08:45) —— ★★把"同一张网的多个焊盘"直接用短铜连起来
        ★★**为什么必须有 (实测 v25: 82 条未连里 31 条集中在 CONN_CAM/CONN_LIGHT, 19 条是 GND)**:
          ★**同一张网的多个焊盘本来就应该直接短铜相连** (PCB 标准做法: net stitching / 同网缝合)
          ⇒ ★**同网铜之间不需要净距** ⇒ ⇒ **一根直线就能连 ⇒ 绕开所有中间障碍**
          ⇒ ⇒ ★★而我的路由器是"逐点独立布线到目标" ⇒ **同网两焊盘之间从没有"直连"的机会**
          ⇒ ⇒ ★★ 于是 5 个 GND 焊盘各自要去接 GND 平面, 中间还被别的网挡 ⇒ ⇒ 19 条未连
          ⇒ ⇒ ★★ 一次同网直连 ⇒ **一批未连直接消失**
        ★**安全**: 唯一的风险是这根短铜**碰到别的网的铜** ⇒ ⇒ 逐段用 `_geom_clear` 查 ⇒ 不清就不连
        ★**已通网的焊盘也参与** (连了不会坏事, 反而降阻抗)
        返回: 新增的短铜条数
        """
        n_stitched = 0
        targets = nets if nets is not None else list(self.net_pads.keys())
        # ★★2026-11-05 08:52 **差分对的网不许缝合** ⇒ 缝合会在差分线中间加一段短铜
        #   ⇒ ★**破坏差分对的几何/耦合** (P 侧多一个分支 ⇒ 等长与间距全乱)
        try:
            _dp = set()
            for (_p, _n, _tp, _tn) in DIFF_PAIRS:
                _dp.add(_p)
                _dp.add(_n)
        except Exception:
            _dp = set()
        targets = [t for t in targets if t not in _dp]
        for net in targets:
            pads = self.net_pads.get(net) or []
            if len(pads) < 2:
                continue
            # ★按几何顺序排 (连接器的一排脚 ⇒ 排完相邻脚相邻 ⇒ 短铜最短)
            ps = sorted(pads, key=lambda p: (round(p[2], 3), round(p[3], 3)))
            for i in range(len(ps) - 1):
                a = ps[i]
                b = ps[i + 1]
                lay = 0
                # ★同网已有铜盖住这段 ⇒ 跳过 (不重复画)
                mx, my = (a[2] + b[2]) / 2.0, (a[3] + b[3]) / 2.0
                dup = False
                for s in self.tracks:
                    if s[0] != net:
                        continue
                    if _pt_seg_dist(mx, my, s[1], s[2], s[3], s[4]) < 0.05:
                        dup = True
                        break
                if dup:
                    continue
                segs = [(a[2], a[3], b[2], b[3])]
                # ★★2026-11-06 02:4x 实测 (v47 板边违规): 同网缝合**没查板边**
                #   ⇒ 同网直连把铜画到板框外 (实测 DSI_D0_D1_N 跑到 y=-0.046mm)
                #   ⇒ ★**默认关** (PCB_EDGE_STRICT=1 才开) ⇒ 老行为可复现
                if EDGE_STRICT and not self._edge_seg_ok(a[2], a[3], b[2], b[3], width):
                    continue
                if not self._geom_clear(net, segs, lay, width):
                    # ★★2026-11-05 08:50 **直线被挡 ⇒ 试 L 形绕行 (两个方向)**
                    _cands = []
                    _mx, _my = (a[2] + b[2]) / 2.0, (a[3] + b[3]) / 2.0
                    for _c in ((_mx, a[3]), (a[2], _my), (_mx, b[3]), (b[2], _my)):
                        _cands.append([(a[2], a[3], _c[0], _c[1]),
                                       (_c[0], _c[1], b[2], b[3])])
                    _picked = None
                    for _s2 in _cands:
                        if not self._geom_clear(net, _s2, lay, width):
                            continue
                        # ★★2026-11-06 02:4x: L 形两个分支也要查板边
                        if EDGE_STRICT and not all(
                                self._edge_seg_ok(_q[0], _q[1], _q[2], _q[3], width)
                                for _q in _s2):
                            continue
                        _picked = _s2
                        break
                    if _picked is None:
                        continue
                    for (_x1, _y1, _x2, _y2) in _picked:
                        self.tracks.append((net, _x1, _y1, _x2, _y2, lay, width))
                        self._add_track_halo(net, _x1, _y1, _x2, _y2, lay, width)
                    n_stitched += len(_picked)
                    continue
                self.tracks.append((net, a[2], a[3], b[2], b[3], lay, width))
                self._add_track_halo(net, a[2], a[3], b[2], b[3], lay, width)
                n_stitched += 1
        if verbose and n_stitched:
            print("  [STITCH] 同网缝合: 新增 %d 条短铜" % n_stitched)
        return n_stitched

    def ripup_and_reroute(self, nets, rip_per_net=6, verbose=True):
        """★★**收尾杀招: 拆掉挡路的线, 重布失败的网** (标准 rip-up & reroute)
        ★**v49 (2026-11-06 01:4x) 三处修正**:
          ① ★**守卫改判 `routed_ok`** ⇒ ★**失败网不再在第一行就被跳过**
             (★**旧行为实测: 19 个失败网一次都没试**, 日志只有汇总行 ⇒ "重布成功 0 个"是假象)
          ② ★**重布前清掉"要重布的网自己已有的铜"** ⇒ ★**`route_net()` 不会自动清**
             ⇒ 不清 ⇒ ★**重复铜** ⇒ DRC 爆 + 段数虚高
          ③ ★**失败时把本网自己的铜原样还原** ⇒ ★**不许把已布好的腿丢掉**
        ★**时机很关键**: 必须在**阶段性 commit 之前**跑 ⇒ ⇒ 被拆的线**根本不会落到板上**
        返回: 重布成功的网数
        """
        ok = 0
        for net in nets:
            # ★★2026-11-06 01:2x **v49: 守卫改判 `routed_ok`** (★"成功过"才跳过)
            #   ★**旧行为**: `if net in self.routed: continue` ⇒ ★**失败的网也在 routed 里**
            #     ⇒ ★**每个失败网都在第一行被跳过 ⇒ 收尾杀招一次都没执行过**
            _skip = (net in self.routed_ok) if RIPUP_ALIVE else (net in self.routed)
            if _skip:
                continue
            cells = self._net_start_cells(net)
            if not cells:
                continue
            bl = self._blockers_for(net, cells, rip_per_net)
            if not bl and RIPUP_ESC:
                # ★v52: 起步格附近没障碍 ⇒ 查**出脚走廊** (★实测 42/61 条死在这)
                bl = self._escape_blockers(net, rip_per_net)
            if not bl:
                continue
            ripped = [b[1] for b in bl]
            rip_nets = set(s[0] for s in ripped)
            # ★★2026-11-06 01:4x **v49 ②③: 记下"受影响网自己已有、且没被拆"的铜**
            #   ★**为什么**: `route_net()` 体内 0 处碰 self.tracks/self.vias ⇒ ★**它从零再画**
            #   ⇒ ⇒ 不清 ⇒ ★**重复铜**; 而失败时又必须 ★**原样还原** (不许丢已布好的腿)
            rip_set = set(ripped)
            affected = set([net]) | rip_nets
            own_t = {}
            own_v = {}
            for _n in affected:
                own_t[_n] = [s for s in self.tracks if s[0] == _n and s not in rip_set]
                own_v[_n] = [v for v in self.vias if v[0] == _n]
            # ★拆: 挡路的线 + ★**受影响网自己所有的线** (★重布时重新画)
            keep = [s for s in self.tracks if s not in rip_set and s[0] not in affected]
            keep_v = [v for v in self.vias if v[0] not in affected]
            # ★被拆线附近的同网过孔也要拆 (否则它的 halo 照样堵) ⇒ ★v49: 受影响网的孔一起清
            self.tracks = keep
            self.vias = keep_v
            self.rebuild_halo()
            # ★重布这个网 (★routed 集合里也要先摘掉它)
            self.routed.discard(net)
            if RIPUP_ALIVE:
                self.routed_ok.discard(net)
            res = self.route_net(net, width=W_SIG)
            if res.get("ok"):
                ok += 1
                # ★把被拆的网重新布一遍 (它们现在有地方了)
                for rn in sorted(rip_nets):
                    if rn == net:
                        continue
                    # ★v49 ②: 重布 rn 前先清掉它自己的铜 (★route_net 不会自动清)
                    self.tracks = [s for s in self.tracks if s[0] != rn]
                    self.vias = [v for v in self.vias if v[0] != rn]
                    self.rebuild_halo()
                    self.routed.discard(rn)
                    if RIPUP_ALIVE:
                        self.routed_ok.discard(rn)
                    r2 = self.route_net(rn, width=W_SIG)
                    if not r2.get("ok"):
                        # ★v49 ③: 重布失败 ⇒ 还原 rn 自己的旧铜 (★不许丢已布好的腿)
                        self.tracks = self.tracks + own_t.get(rn, []) \
                            + [s for s in ripped if s[0] == rn]
                        self.vias = self.vias + own_v.get(rn, [])
                        self.rebuild_halo()
                if verbose:
                    print("  [RIPUP] %-22s 拆了 %d 条线 ⇒ 重布成功" % (net, len(ripped)))
            else:
                # ★失败 ⇒ 原样放回 (★板子上本来也没它们 ⇒ 只需还原障碍模型)
                # ★v49 ③: ★**连本网自己已有的铜也要还原** (★否则会丢掉已布好的腿)
                for _n in affected:
                    self.tracks = self.tracks + own_t.get(_n, []) \
                        + [s for s in ripped if s[0] == _n]
                    self.vias = self.vias + own_v.get(_n, [])
                self.rebuild_halo()
                self.routed.discard(net)
                if RIPUP_ALIVE:
                    self.routed_ok.discard(net)
                if verbose:
                    print("  [RIPUP] %-22s 拆了 %d 条线 ⇒ 仍不通 ⇒ 已还原" % (net, len(ripped)))
        return ok

    def _emit_path(self, net, path, width, via_count=1,
                   stub_start=None, stub_end=None):
        """★stub_start/stub_end = (焊盘中心x, 中心y, 直道终点x, 终点y)
           —— 密集焊盘出脚: 先沿中心线直线走, 再进网格

        ★★2026-11-04 23:58 **换层点必须先确认过孔能落下来** ——
          原来的写法: 边走边打孔, 打孔失败 (被 _via_too_close 跳过) 就**继续往下走**
          ⇒ ★**铜从一层"跳"到另一层但中间没孔** ⇒ 两端悬空 ⇒ DRC track_dangling
          ⇒ 现在: 先把本路径所有换层点**一次性预校验** (含路径内部互相间距),
            任何一个落不下 ⇒ ★**整条路径放弃** (不落铜) ⇒ 宁可这个脚不通, 也不留断铜
        返回 True = 已落铜; False = 放弃 (调用方计入失败)"""
        # ---------- 0) 构造路径点 ----------
        pts = []
        for (li, idx) in path:
            i, j = idx % self.W, idx // self.W
            pts.append([li, self._cx(i), self._cy(j)])
        if not pts:
            return True
        if stub_start:
            pts[0][1], pts[0][2] = stub_start[2], stub_start[3]
        else:
            p0 = self.pad_cell.get(path[0])
            if p0 and p0[0] == net:
                # ★焊盘真中心**离网格** ⇒ 可能比格心更靠板边 ⇒ 换中心前先验净距
                if len(pts) > 1 and self._edge_seg_ok(p0[1], p0[2], pts[1][1], pts[1][2], width):
                    pts[0][1], pts[0][2] = p0[1], p0[2]
        if stub_end:
            pts[-1][1], pts[-1][2] = stub_end[2], stub_end[3]
        else:
            pn = self.pad_cell.get(path[-1])
            if pn and pn[0] == net:
                if len(pts) > 1 and self._edge_seg_ok(pn[1], pn[2], pts[-2][1], pts[-2][2], width):
                    pts[-1][1], pts[-1][2] = pn[1], pn[2]

        # ★★2026-11-06 02:4x 实测 (v47 板边违规): 原来**只查首尾两段**
        #   ⇒ 中间段可以跑出板框 ⇒ ★**逐段查, 任一段违规 ⇒ 整条路径放弃**
        #   (★宁可这个脚不通, 也不留断铜 —— 与本文件既有原则一致)
        if EDGE_STRICT:
            for _k in range(len(pts) - 1):
                if not self._edge_seg_ok(pts[_k][1], pts[_k][2],
                                         pts[_k + 1][1], pts[_k + 1][2], width):
                    return False

        # ---------- 1) 收集换层点 ----------
        # ★**层间过渡的两端坐标相同** (A* 的换层是同格换层) ⇒ 落铜时会产生**零长段**
        #   ⇒ 零长段是**退化图元** ⇒ 交给 cleanup_geometry 统一清掉
        trans = []
        for k in range(len(pts) - 1):
            la, xa, ya = pts[k]
            lb, xb, yb = pts[k + 1]
            if la != lb:
                trans.append((xa, ya, la, lb))

        # ---------- 2) 预校验所有换层点 (含路径内部互相间距) ----------
        for (x, y, la, lb) in trans:
            l1, l2 = (la if la < lb else lb), (la if la > lb else lb)
            if not self._via_ok(l1, l2, self._idx(self._ci(x), self._cj(y)), net):
                return False
            # ★**同一条路径里的两个换层点也不能太近** (否则第二个孔放不下)
            for (x2, y2, _a, _b) in trans:
                if x2 == x and y2 == y:
                    continue
                if math.hypot(x - x2, y - y2) < MIN_VIA_CENTER:
                    return False

        # ★★★★★★2026-11-10 15:3x 【★"出脚离网格那一段"的净距闸 (★env 门控 `PCB_ESC_CLR_FIX`★)】★★★★★★
        #   ★★★**★为什么要有 (★实测坐实, ★不是猜★)★★★ ★★★
        #     ★**实测 (★v76mg1 终板·官方板对照★)**: ★**`LIGHT_3V3` 的一根 45° 斜线与一颗 GND 下拉孔
        #       铜边净距 = 0.1581mm (★需 0.2000★) ⇒ ★**该臂 6 条 clearance 里最严重的一条** ★★
        #     ★**几何 (★实测复算, ★与 KiCad 报的 0.1581 逐位一致★)**:
        #       ★**GND 孔 @ (29.25, 61.35) Ø0.6 (★盘半径 0.30★)**
        #       ★**LIGHT_3V3 斜线 (28.75,61.05)->(28.45,60.95) w=0.25 (★半宽 0.125★)**
        #       ⇒ ★**中心距 0.5831 ⇒ 净距 = 0.5831 - 0.300 - 0.125 = 0.1581mm** ★★
        #   ★★★**★根因 (★代码级★)**: ★**halo 是【按格】封的, ★而 A* 只判【格】**
        #     ⇒ ★**出脚直道末端是【离网格】的 ⇒ 【直道末端 → 第一个格心】那一段【不在任何格边上】**
        #     ⇒ ★**⇒ 这段离网格的 45° 斜线可以贴着孔穿过去 ⇒ halo 看不见 ⇒ DRC 报 clearance**
        #     ⇒ ★★**⇒ 与【蛇形出板】是【同一个病根的另一个面】: ★【离网格的几何 ⇒ 栅格闸管不到】★★** ★★
        #   ★**修法 (★与板边闸同一条铁律: 落线前就拦★)**: ★**在 `_emit_path` 落铜前, ★把【离网格的那一段】
        #     用【真实几何】查一遍净距 (★对已落的铜 + 已落的孔★) ⇒ 不合格就整条路径放弃** ★★
        #   ★**默认关 ⇒ 逐位不变 (★老臂可复现★)**
        if ESC_CLR_FIX:
            for _k in range(len(pts) - 1):
                _la, _xa, _ya = pts[_k]
                _lb2, _xb, _yb = pts[_k + 1]
                if _la != _lb2:
                    continue
                # ★★★★★★2026-11-10 16:2x 【★只查【离网格】的那一段★】★★★★★★
                #   ★**为什么必须限定"离网格" (★实测, ★不是猜★)**:
                #     ★**halo 已经管【在栅格上的段】(★它就是按格封的★) ⇒ ⇒ 那部分【重复查】不但没用,
                #       ★**还会因 halo 的保守半径 (0.95mm vs 真实 0.45~0.625mm) 而【大量误杀】**
                #       ⇒ ★**实测: `v76mk` 臂 (★开本闸★) 裸板 unc 39 → 138 (★净亏 99 条!!★) ⇒ ★【闸太严, 必须收窄】★
                #     ⇒ ★**⇒ 本闸只补 halo 的【盲区】= 【离网格的几何】⇒ ★**不碰 halo 已经管住的部分** ★★
                #   ★**判据: ★**该段的端点【不在栅格心】上** ⇒ ★**它就是 halo 管不到的那一类** ★★
                if self._on_grid(_xa, _ya) and self._on_grid(_xb, _yb):
                    continue
                if not self._seg_clear_geom(net, _xa, _ya, _xb, _yb, width):
                    return False

        # ---------- 3) 落铜 ----------
        # ★★2026-11-06 05:2x **零长段过滤**: ★**stub 吸附到格心时会造成零长段**
        #   ⇒ 零长段 ⇒ DRC `tracks_crossing` (0.0000mm 的线) + `track_dangling`
        #   ⇒ ★**零长段永远无意义 ⇒ 直接不落**
        # ★★★2026-11-06 05:4x **stub 必须跟路径同层** (★实测 18 条 track_dangling 的真凶)
        #   ★**原来 stub 段硬编码在层 0 (F.Cu)** ⇒ ★**路径在 In2/In4/In6 时 ⇒ stub 与路径脱层**
        #   ⇒ ⇒ 断头 ⇒ track_dangling + shorting
        #   ⇒ ★**现在: stub 用路径首/末点所在的层**
        #   ⇒ ★对路由器自己的流程无影响 (escape_stub 永远落在 F.Cu ⇒ pts[0][0]==0)
        if stub_start:
            sx, sy, ex, ey = stub_start
            if abs(ex - sx) > 1e-6 or abs(ey - sy) > 1e-6:
                _ls = pts[0][0] if pts else 0
                self.tracks.append((net, sx, sy, ex, ey, _ls, W_MIN))
                self._add_track_halo(net, sx, sy, ex, ey, _ls, W_MIN)
        if stub_end:
            gx, gy, ex, ey = stub_end
            if abs(gx - ex) > 1e-6 or abs(gy - ey) > 1e-6:
                _le = pts[-1][0] if pts else 0
                self.tracks.append((net, ex, ey, gx, gy, _le, W_MIN))
                self._add_track_halo(net, ex, ey, gx, gy, _le, W_MIN)
        seg = []
        for k in range(len(pts) - 1):
            la, xa, ya = pts[k]
            lb, xb, yb = pts[k + 1]
            if la != lb:
                self._emit_via(net, xa, ya, la, lb, via_count)
                seg.append((net, xa, ya, xb, yb, lb, width))
            else:
                seg.append((net, xa, ya, xb, yb, la, width))
        merged = _merge_collinear(seg, MERGE_FIX)
        for s in merged:
            # ★★2026-11-06 05:2x 零长段过滤 (★stub 吸附后可能出现重合点)
            if abs(s[3] - s[1]) < 1e-6 and abs(s[4] - s[2]) < 1e-6:
                continue
            self.tracks.append(s)
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5], s[6])
        return True

    def _emit_via(self, net, x, y, la, lb, count=1):
        l1, l2 = (la, lb) if la < lb else (lb, la)
        vs = [(x, y)]
        if count > 1:
            # ★过孔阵列间距 ≥ VIA_DIA + CLEAR = 0.8mm —— ★上一版用 0.6mm
            #   ⇒ 相邻两个 0.6mm 盘的边缘正好相接 ⇒ DRC: 短接 + 孔重合 + 孔间距不足
            vs = [(x + (k - (count - 1) / 2.0) * 0.85, y)
                  for k in range(count)]
        for (vx, vy) in vs:
            # ★**同一个网的两颗孔间距 ≥ 0.58mm** (孔径 0.3 ⇒ 孔到孔 ≥ 0.25mm)
            #   ★同网的过孔**不互斥** (halo 里同网不算冲突) ⇒ 上限没管住
            #   ⇒ 上一版 DRC: holes co-located 64 条 + hole to hole 5 条
            # ★★2026-11-04 23:50 **这条现在也在 A\* 里查了 (见 _via_ok)** ——
            #   ⇒ A\* 不会规划"落不下过孔的换层点" ⇒ ★**层间过渡段不会断**
            if self._via_too_close(net, vx, vy):
                continue
            if not self._via_ok(l1, l2, self._idx(self._ci(vx), self._cj(vy)), net):
                continue
            self.vias.append((net, vx, vy, l1, l2))
            self.via_cells.setdefault(self._idx(self._ci(vx), self._cj(vy)), []).append((vx, vy))
            self._add_via_hash(vx, vy, net)
            self._add_via_halo(net, vx, vy, l1, l2)

    def _via_too_close(self, net, vx, vy, mind=None):
        """★★**异网/同网分开判** (★v34 根因级修复, 2026-11-05 19:40)

        ★**之前只查了一条规则** ⇒ 漏掉"铜到铜":
          - 孔到孔 (制造): drill/2 + 0.25 + drill/2 = 0.55mm ⇒ 中心距 0.58
          - 铜到铜 (电气): dia/2 + **0.20** + dia/2 = **0.80mm** ⇒ ★**从来没人查**
          ⇒ 之前 DRC=0 是"halo 顺手挡住了" (0.95 > 0.80), **不是规则查对了**
          ⇒ ★**放松 halo (v32/v33) ⇒ 老账全爆: v32_R 56 条 + v33_S 40 条 clearance**

        ★**现在两条规则都查**:
          - **同网** ⇒ 0.58mm (孔到孔; 同网两孔铜相连, 铜净距不适用)
          - **异网** ⇒ **0.80mm** (铜到铜: 0.30 + 0.20 + 0.30)
        ★**只改布出来的几何** ⇒ ★**板 setup 的 min hole / clearance 一个字没动**

        ★★2026-11-04 22:45 修 (真正的根因): 原来只扫 **3×3 邻格** (±0.25mm) ⇒ ★**够不着 0.56mm 内的其它过孔**
        ⇒ 两颗过孔中心距 0.5mm (孔到孔 0.2mm) 竟然没被拦住 ⇒ DRC 出 hole_to_hole。

        ★★2026-11-05 **改用 1mm 粗粒度哈希** (★性能: 这个函数在 A* 里被调用几十万次)
           ⇒ 3×3=9 次查表 (而不是 49 次) ⇒ 结果一样, 速度 ~5×
        """
        cx = int(math.floor(vx))
        cy = int(math.floor(vy))
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1):
                for (ux, uy, unet) in self.via_hash.get((cx + di, cy + dj), ()):
                    # ★★**异网 ⇒ 铜到铜 0.80mm; 同网 ⇒ 孔到孔 0.58mm**
                    _need = MIN_VIA_CENTER if unet == net else MIN_VIA_CENTER_XNET
                    if mind is not None:
                        _need = max(_need, mind)
                    if math.hypot(vx - ux, vy - uy) < _need:
                        return True
        return False

    def _via_center_ok(self, cx, cy, net=None, min_c=None):
        """★★2026-11-05 13:15 **过孔中心距判据** (★治 DRC `hole_to_hole`)
           ★**为什么要有**: `_via_exists` 只查**同点** ⇒ ★**两个孔中心只差 0.25mm 也能各落一个**
             ⇒ 板规则: 孔到孔 ≥ 0.25mm ⇒ 中心距 ≥ 0.15(钻孔半径)+0.15+0.25 = **0.55mm**
             ⇒ ★**v29_N 实测 3 处 `hole_to_hole`** (净距 0.0000 / 0.2000 / 0.0536mm) ⇒ 都是这么来的
           ★**同网异网都算** (孔到孔是制造规则, 不看网)
           ★**注意**: 焊盘里的过孔 (in-pad) 中心就是焊盘中心 ⇒ ★**间距不够就只能不落**
             ⇒ 那就少一条 GND 下拉 ⇒ ★**宁可 unconnected 多一条, 也不要有 DRC 违规**

        ★★2026-11-05 19:40 **v34: 异网 ⇒ 0.80mm (铜到铜)**
           ★**`net` 给了就按网分档**: 同网 0.58 / 异网 0.80
           ⇒ ★**没给 net (老调用) ⇒ 保守用异网档 0.80** (宁可少落孔, 不要 DRC 红)"""
        _same = MIN_VIA_CENTER if min_c is None else min_c
        _diff = MIN_VIA_CENTER_XNET if min_c is None else max(min_c, MIN_VIA_CENTER_XNET)
        for (_n, vx, vy, _l1, _l2) in self.vias:
            _need = _same if (net is not None and _n == net) else _diff
            if math.hypot(vx - cx, vy - cy) < _need:
                return False
        return True

    def _via_exists(self, net, cx, cy):
        """★2026-11-05 09:58 **同网同点过孔是否已存在**
           ★**为什么**: GND 下拉有两遍 (常规 + 窄焊盘长轴引出) ⇒ 同一落点会落两个过孔
           ⇒ DRC 直接报 `holes_co_located` (★实测臂 A/B 各 2 条) ⇒ ★**落盘前查重**"""
        for (_n, vx, vy, _l1, _l2) in self.vias:
            if _n == net and abs(vx - cx) < 1e-6 and abs(vy - cy) < 1e-6:
                return True
        return False

    def _add_via_hash(self, vx, vy, net=None):
        # ★★2026-11-05 19:40 **带网名** (★v34: `_via_too_close` 要分同网/异网)
        self.via_hash.setdefault((int(math.floor(vx)), int(math.floor(vy))),
                                 []).append((vx, vy, net))

    def _add_track_halo(self, net, x1, y1, x2, y2, li, w=W_SIG):
        """走线净距禁区: 半径 = 净距 + 本线半宽 + 对方半宽 (按级别分别登记)
           ★★2026-11-05 07:50 **默认不盖别的网的焊盘格** (见 _mark 的 skip_pad_cells 说明)
           ★★2026-11-05 08:00 **做成可开关** (PCB_SKIP_PAD_CELLS=0) ⇒ 便于 A/B:
             ★**风险**: 焊盘格不再被 halo 挡 ⇒ ★**相邻格 (0.25mm) 会被别的网的走线占用**
               ⇒ 铜到铜可能只剩 0.025mm ⇒ ★**DRC 违规/短路风险**
               ⇒ ⇒ ★**必须盯 DRC** ⇒ 试验用开关, 验过才准进正式轮
        """
        _skip = os.environ.get("PCB_SKIP_PAD_CELLS", "1") != "0"
        for cls in range(3):
            rr = CLEAR + w / 2.0 + W_CLS[cls] / 2.0 + HALO_MARGIN
            for (i, j) in _seg_cells(x1, y1, x2, y2, self.g, rr / self.g,
                                     self.bb[0], self.bb[1]):
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                self._mark(cls, li, self._idx(i, j), net, skip_pad_cells=_skip)

    def _add_via_halo(self, net, x, y, l1, l2, skip_pad_cells=True):
        """通孔净距禁区 (★默认**不盖别的网的焊盘格** ⇒ 见 _mark 的说明)
        ★★2026-11-05 18:55 **半径用 VIA_HALO_MARGIN (默认 = HALO_MARGIN ⇒ 行为不变)**
           ⇒ 实验臂 `PCB_VIA_HALO_MARGIN=0.0` 打开精确几何 ⇒ ★**见常量区根因注释**
        ★★2026-11-05 23:2x **v41: `PCB_VIA_HALO_EXACT=1` ⇒ 圆心改用真实孔心**
           ★**根因**: 旧实现用"含孔心那一格"的**格心**当圆心 ⇒ 孔偏格心 δ 时禁区整体偏 δ
             ⇒ 实测 v36_S DRC: 孔 (85.35,9.60) 偏格心 (0.10,0.10)
               ⇒ 走线端点离真实孔心 **0.5657 (<0.625 违规)** 却按格心判 0.7071 ⇒ **放行**
           ★**修法**: 按**真实孔心到该格方形区的最小距离**判 (⇒ 穿格的对角段也必然 ≥ rr)
           ★**默认 0** ⇒ 行为与旧版逐位一致"""
        i, j = self._ci(x), self._cj(y)
        for cls in range(3):
            rr = CLEAR + VIA_DIA / 2.0 + W_CLS[cls] / 2.0 + VIA_HALO_MARGIN
            ri = int(math.ceil(rr / self.g))
            # ★**通孔 ⇒ 6 层都有铜** ⇒ 净距禁区必须记满 6 层 (否则内层撞铜 ⇒ DRC 短接)
            for li in range(NLAYERS):
                if VIA_HALO_CENTER:
                    # ★★**真实孔心 + 原半径 (不加对角余量)** => ★**封格数几乎不变**
                    #   ★**为什么**: 旧版圆心 = "含孔那格的格心" => 禁区整体偏 delta
                    #     => 走线端点离真实孔心 0.5657 (<0.625 违规) 却按格心判 0.7071 => 放行 => DRC 漏网
                    #   ★**为什么不用 VIA_HALO_EXACT**: 加 g*sqrt(2)/2 后实测多封 11 格/孔
                    #     => 未通 57 -> 63 (净亏) => ★**只改圆心, 不扩半径**
                    _ri2 = ri + 1
                    for dj in range(-_ri2, _ri2 + 1):
                        for di in range(-_ri2, _ri2 + 1):
                            i2, j2 = i + di, j + dj
                            if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                                continue
                            _cx2 = self.bb[0] + i2 * self.g
                            _cy2 = self.bb[1] + j2 * self.g
                            if math.hypot(_cx2 - x, _cy2 - y) >= rr + 1e-6:
                                continue
                            self._mark(cls, li, self._idx(i2, j2), net,
                                       skip_pad_cells=skip_pad_cells)
                elif VIA_HALO_EXACT:
                    # ★★**精确分支 (可证安全)**: 圆心 = **真实孔心** ⇒ 判据 = 格心距 < rr + g*sqrt(2)/2
                    #   ★**为什么是这个式子**: 穿格(正交或对角)的走线段上, **任意一点**到该段两个端点中
                    #     较近者的距离 ≤ g*sqrt(2)/2 = **0.1768mm** (对角段最坏)
                    #   ⇒ 若两端点格心都离孔心 ≥ rr + 0.1768 ⇒ 段上每点都离孔心 ≥ rr ⇒ **不擦孔**
                    #   ★**为什么必须用真实孔心**: 旧判据的圆心是"含孔心那格"的**格心**
                    #     ⇒ 孔偏格心 δ 时禁区整体偏 δ (实测 v36_S: 偏 (0.10,0.10)=0.141mm)
                    #     ⇒ 走线端点离真实孔心 0.5657 (<0.625 违规) 却按格心判 0.7071 ⇒ **放行** ⇒ DRC 漏网
                    _pad = self.g * math.sqrt(2.0) / 2.0
                    _ri2 = ri + 2
                    for dj in range(-_ri2, _ri2 + 1):
                        for di in range(-_ri2, _ri2 + 1):
                            i2, j2 = i + di, j + dj
                            if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                                continue
                            _cx2 = self.bb[0] + i2 * self.g
                            _cy2 = self.bb[1] + j2 * self.g
                            if math.hypot(_cx2 - x, _cy2 - y) >= rr + _pad + 1e-9:
                                continue
                            self._mark(cls, li, self._idx(i2, j2), net,
                                       skip_pad_cells=skip_pad_cells)
                else:
                    for dj in range(-ri, ri + 1):
                        for di in range(-ri, ri + 1):
                            if di * di + dj * dj > (rr / self.g) ** 2 + 1e-9:
                                continue
                            i2, j2 = i + di, j + dj
                            if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                                continue
                            self._mark(cls, li, self._idx(i2, j2), net,
                                       skip_pad_cells=skip_pad_cells)

    def net_length(self, net):
        tot = 0.0
        for s in self.tracks:
            if s[0] != net:
                continue
            tot += math.hypot(s[3] - s[1], s[4] - s[2])
        return tot

    def net_tracks(self, net):
        return [s for s in self.tracks if s[0] == net]

    # ------------------------------------------------ 差分对走廊
    def build_dist_map(self, net):
        """到 net 已布路径的距离图 (BFS, 跨层合并) —— 差分对"拉近"用"""
        cells = set()
        for s in self.tracks:
            if s[0] != net:
                continue
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], self.g, 0,
                                     self.bb[0], self.bb[1]):
                cells.add(self._idx(i, j))
        if not cells:
            return {}
        dist = {c: 0 for c in cells}
        frontier = list(cells)
        d = 0
        while frontier and d < 40:
            d += 1
            nxt = []
            for c in frontier:
                i, j = c % self.W, c // self.W
                for dj in (-1, 0, 1):
                    for di in (-1, 0, 1):
                        i2, j2 = i + di, j + dj
                        if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                            continue
                        k = self._idx(i2, j2)
                        if k in dist:
                            continue
                        dist[k] = d
                        nxt.append(k)
            frontier = nxt
        return dist

    def build_pair_block(self, net_p, min_c=0.50, exempt_net=None, exempt_r=1.20):
        """★**差分对的"几何禁入格"** (★用精确距离, 不用保守的 halo)

        ★**为什么要自己算**: halo 半径 = CLEAR + w/2 + W_CLS[cls]/2 + HALO_MARGIN
          ⇒ 对 0.25mm 线是 0.2+0.125+0.125+0.2 = **0.65mm** (★栅格量化还要再加)
          ⇒ ★**P 的 halo 把 P 旁边 0.65mm 全封死** ⇒ N 想贴着 P 平行走就进不去
        ★**但物理上**: 两根 0.25mm 线中心距 0.50mm ⇒ 净距 0.25mm ≥ 0.2 ✓ DRC 干净
          ⇒ ★**真正会短路的只有 <0.50mm 的那些格** ⇒ 精确算出来, 只禁这些

        ★★★2026-11-05 09:45 **exempt_net: 伙伴禁入格要豁免"N 侧自己的出脚区"**
          ★**实测根因 (机器读出)**: SoM BTB 0.4mm pitch ⇒ P/N 焊盘中心距 **0.400mm**
            (USB_D_P_SRC↔USB_D_N_SRC @ J_SOM_P1.94 · CSI_D0_CK/D0/D1/D2_N_SRC @ J_SOM_P4.* · DSI_D0_CK_N_SRC @ J_SOM_P3.69)
          ⇒ 而"伙伴禁入格"半径 = min_c+0.3 = **0.8mm** (还额外含伙伴焊盘矩形) ⇒ ★**N 焊盘自己的格被封死**
            ⇒ ⇒ N 侧 A* 起点全被挡 ⇒ **0 段走线** ⇒ 报"N 未通" ⇒ v25 里 13 对"单边零铜"
          ⇒ ★**物理上完全合法**: 两根 0.2mm 线从 0.4mm pitch 相邻焊盘并行出脚
            ⇒ 净距 = 0.4 - 0.2/2 - 0.2/2 = **0.20mm** ✔ (正好达规范)
          ⇒ ⇒ ★**禁入规则必须在出脚区让位**, 出脚之后走廊约束照旧
          ⇒ ★**默认关** (PCB_PAIR_ESCAPE_EXEMPT=0) ⇒ **不影响在跑的 v26 四臂**

        ★★★**宽度感知 (2026-11-05 10:00)**: ★**两套禁入格**
          · `block_wide`   : d - w_P/2 - **W_SIG/2** < 0.2  ⇒ 0.25mm 的 N 线不许进
          · `block_narrow` : d - w_P/2 - **W_MIN/2** < 0.2  ⇒ 0.20mm 的 N 线可以进
          ★**为什么**: SoM BTB 0.4mm pitch ⇒ P 的出脚直道(0.2mm 窄线)中心距 N 的焊盘只有 0.400mm
            ⇒ ★**0.2mm 窄线并行时净距 = 0.400-0.1-0.1 = 0.200mm (刚好合法)**
            ⇒ ★**宽线 (0.25) 则净距 0.175 ⇒ 违规** ⇒ ⇒ **禁入格必须按"这条线有多宽"分别算**
            ⇒ ⇒ ★**窄线能贴上去 (真·差分对几何), 宽线不许贴 (免得 DRC 违规)**

        返回 (block_wide, block_narrow) 两个 set of idx"""
        block = set()
        block_n = set()
        # ★★出脚区豁免格 (★N 侧自己焊盘周围 exempt_r mm)
        #   ★★2026-11-05 12:40 **默认 exempt_r = 0.0** ⇒ ★**只豁免"N 焊盘自己那几格"**
        #   ⇒ ★**N 侧能起步 (不被伙伴的通道封死), 但不许横穿伙伴的铜** ⇒ 差分自短路归零
        #   ⇒ (旧行为 exempt_r=1.20 ⇒ 盖住伙伴通道 ⇒ 21 处 P/N 自短路, 实测 v28_H)
        exempt = set()
        if exempt_net:
            _r = PAIR_EXEMPT_R
            for (_net, x0, y0, x1, y1, _layers) in self.pad_rects_l:
                if _net != exempt_net:
                    continue
                for (i, j) in _rect_cells(x0 - _r, y0 - _r,
                                          x1 + _r, y1 + _r, self.g,
                                          self.bb[0], self.bb[1]):
                    if 0 <= i < self.W and 0 <= j < self.H:
                        exempt.add(self._idx(i, j))
        r = min_c + 0.30
        ri = int(math.ceil(r / self.g)) + 1
        for s in self.tracks:
            if s[0] != net_p:
                continue
            x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
            for (i, j) in _seg_cells(x1, y1, x2, y2, self.g, ri,
                                     self.bb[0], self.bb[1]):
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                idx = self._idx(i, j)
                px, py = self._cx(i), self._cy(j)
                # ★精确距离: 格心到伙伴线段的距离
                d = _pt_seg_dist(px, py, x1, y1, x2, y2)
                if idx in exempt:
                    continue
                if d - s[6] / 2.0 - W_SIG / 2.0 < 0.2:
                    block.add(idx)
                if d - s[6] / 2.0 - W_MIN / 2.0 < 0.2:
                    block_n.add(idx)
        # ★★2026-11-05 **伙伴的过孔也要算** ——
        #   ★**漏了过孔 ⇒ DRC 直接报 clearance 违规** (实测 3 条)
        #   ★过孔是通孔 (F.Cu..B.Cu) ⇒ **所有 6 层**都算
        for (net, vx, vy, l1, l2) in self.vias:
            if net != net_p:
                continue
            rr = min_c + 0.30
            for (i, j) in _rect_cells(vx - rr, vy - rr, vx + rr, vy + rr, self.g,
                                      self.bb[0], self.bb[1]):
                if 0 <= i < self.W and 0 <= j < self.H:
                    idx = self._idx(i, j)
                    px, py = self._cx(i), self._cy(j)
                    if idx in exempt:
                        continue
                    _d = math.hypot(px - vx, py - vy)
                    if _d - VIA_DIA / 2.0 - W_SIG / 2.0 < 0.2:
                        block.add(idx)
                    if _d - VIA_DIA / 2.0 - W_MIN / 2.0 < 0.2:
                        block_n.add(idx)
        # ★伙伴的焊盘周围 (同层) 也要禁
        for (net, x0, y0, x1, y1, layers) in self.pad_rects_l:
            if net != net_p:
                continue
            rr = min_c + 0.3
            for li in layers:
                for (i, j) in _rect_cells(x0 - rr, y0 - rr, x1 + rr, y1 + rr, self.g,
                                          self.bb[0], self.bb[1]):
                    if 0 <= i < self.W and 0 <= j < self.H:
                        _bi = self._idx(i, j)
                        if _bi in exempt:
                            continue
                        block.add(_bi)
                        block_n.add(_bi)
        return block, block_n

    def build_pair_guide(self, net_p, ring=3):
        """★★ **差分对的"走廊引导图"** (★N 侧的关键修复)

        ★**问题**: 上一版用 `build_dist_map(P)` + alpha 把 N **往 P 的路径上拉**,
          但 P 的路径**自己就被 P 的 halo 封死** (halo 半径 0.65mm ⇒ 邻格全禁)
          ⇒ ★**N 想贴 P 就必须进禁区** ⇒ A* 在那里反复撞墙 ⇒ ★**预算烧光 (58/82 失败)**
          ⇒ 实测: 12 个 MIPI 对里 **N 侧 6 个完全布不出来 (trk=0)**

        ★**修法**: 把"拉近"的**目标从 P 的路径改成 P 路径外侧的那一圈**
          - ring = 2 格 (0.50mm) ⇒ ★**离 P 铜箔 ≥0.50mm** ⇒ 净距 0.25 ≥ 0.2 ⇒ DRC 干净
          - ★N 被拉到这圈"合法走廊"上 ⇒ 既能贴着 P 平行走 (差分对几何), 又不碰禁区
          - ★**代价函数在走廊上最小** ⇒ 不再往禁区里钻 ⇒ ★**A* 预算省下来**

        ★★2026-11-05 **距离图要覆盖全板** ——
          ★上一版 `build_dist_map` 只算 40 格 (10mm) 的 BFS
          ⇒ ★**MIPI 的 P 路径长达 100~240mm** ⇒ N 的**大部分路程都在图外**
          ⇒ 整段都拿到同一个 dist_def ⇒ ★**没有"拉近"效果** ⇒ N 还是乱跑
          ⇒ 现在: **全板 BFS** ⇒ N 从头到尾都被引导在 P 的走廊里

        返回 (guide_map, default) —— guide_map[cell] = 离走廊的距离 (0 = 在走廊上)
        default = 走廊之外的"无穷远"代价值 (★不设默认 0 ⇒ 否则远处反而免费)
        """
        cells = set()
        for s in self.tracks:
            if s[0] != net_p:
                continue
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], self.g, 0,
                                     self.bb[0], self.bb[1]):
                cells.add(self._idx(i, j))
        if not cells:
            return {}, 0
        dist = {c: 0 for c in cells}
        frontier = list(cells)
        d = 0
        # ★★**全板 BFS** (★不设 40 格上限 ⇒ 覆盖整条 P 路径)
        while frontier:
            d += 1
            nxt = []
            for c in frontier:
                i, j = c % self.W, c // self.W
                for dj in (-1, 0, 1):
                    for di in (-1, 0, 1):
                        i2, j2 = i + di, j + dj
                        if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                            continue
                        k = self._idx(i2, j2)
                        if k in dist:
                            continue
                        dist[k] = d
                        nxt.append(k)
            frontier = nxt
        guide = {}
        for (c, dd) in dist.items():
            guide[c] = max(0, dd - ring)
        # ★走廊外的格: 距离 = max 值 (⇒ 同样"远") ⇒ ★远处不会比走廊更便宜
        dmax = max(guide.values()) if guide else 0
        return guide, dmax

    # ------------------------------------------------ 落板
    def commit(self, board):
        """把生成的走线/过孔写进板子 (★不改任何网表绑定)
        ★★2026-11-05 07:05 **支持"部分落盘"** —— ★★中途存盘**必须带上已布的走线**!
           原来中途存盘 (`_save_board_progress`) 在 `commit()` **之前** ⇒ board 上还没有任何走线图元
           ⇒ ★**写出的必然是 0 走线骨架** ⇒ ★**"超时不丢活"这个功能压根没保住任何进度**
             (实测: 06:53:53 官方板被刷成 468951B / 0 段 / 0 过孔)
           ⇒ 现在: commit() 记住已写入的条数 ⇒ 中途存盘前先 commit 一遍 ⇒
             ★**中途存盘的板 = 已经布了一部分的真板** ⇒ 超时也能捡回进度
        """
        # ★自检: 板边净距 —— 落板前最后一道闸 (fail fast: 宁可这轮不投板也别留 DRC 红)
        bad = 0
        for (net, x1, y1, x2, y2, li, w) in self.tracks:
            if not self._edge_seg_ok(x1, y1, x2, y2, w):
                bad += 1
                if bad <= 6:
                    print("  ⚠️ [EDGE] 板边净距不足: %s (%.3f,%.3f)->(%.3f,%.3f) w=%.2f"
                          % (net, x1, y1, x2, y2, w))
        for (net, x, y, l1, l2) in self.vias:
            if not self._edge_seg_ok(x, y, x, y, VIA_DIA):
                bad += 1
                if bad <= 6:
                    print("  ⚠️ [EDGE] 过孔离板边太近: %s (%.3f,%.3f)" % (net, x, y))
        self.edge_viol = bad
        # ★★2026-11-06 02:5x 实测: ★**落板前把违规铜剔掉是负收益** (实测 DRC 12→8)
        #   ⇒ 原因: 剔掉链中间那段 ⇒ 留下悬空端 ⇒ ★**又生出新的 DRC 违规**
        #   ⇒ ★**所以真修法只有预防** (缝合路径/_emit_path 落线前就拦 ⇒ 见上面两处)
        #   ⇒ ★**这里保持只数 + 打印** (★晋级闸会拒 DRC≠0 的板 ⇒ 不会误上位)
        n = 0
        # ★★2026-11-05 07:15 **部分落盘的记账改用"对象身份"** (同事指出的回归)
        #   ⇒ 原来用**下标** (_done_tracks 计数) ⇒ ★**cleanup_geometry 会重排/过滤 self.tracks**
        #   ⇒ 下标错位 ⇒ ★**最终 commit 会漏写走线** (数据丢失!)
        #   ⇒ 现在: 用 id(段元组) 记账, 并在 dict 里**保留元组本体** ⇒ id 不会被复用
        _committed = getattr(self, "_committed", None)
        if _committed is None:
            _committed = self._committed = {}
        for _t in self.tracks:
            # ★★必须用 self.tracks 里的**元组对象本身**记身份 (新建元组 ⇒ id 每次都变 ⇒ 记账失效)
            (net, x1, y1, x2, y2, li, w) = _t
            if id(_t) in _committed:
                continue
            code = netcode(board, net)
            if code <= 0:
                continue
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
            t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
            t.SetWidth(pcbnew.FromMM(w))
            t.SetLayer(CU_LAYERS[li])
            t.SetNetCode(code)
            board.Add(t)
            _committed[id(_t)] = (_t, t)
            n += 1
        for _v in self.vias:
            (net, x, y, l1, l2) = _v
            if id(_v) in _committed:
                continue
            code = netcode(board, net)
            if code <= 0:
                continue
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
            try:
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
            except Exception:
                pass
            v.SetWidth(pcbnew.FromMM(VIA_DIA))
            v.SetDrill(pcbnew.FromMM(VIA_DRILL))
            v.SetLayerPair(CU_LAYERS[l1], CU_LAYERS[l2])
            v.SetNetCode(code)
            board.Add(v)
            _committed[id(_v)] = (_v, v)
            n += 1
        self._done_tracks = len(self.tracks)
        self._done_vias = len(self.vias)
        return n

    def _drop_committed(self, item):
        """★把**已提交到板上的**图元删掉 (★cleanup 要能真的删退化段, 不只是改内存列表)
           ★**为什么必须**: 阶段性 commit 已经把零长段/悬空段画进板了 ⇒
             cleanup 只改 self.tracks 的话 ⇒ ★**板上那些退化段删不掉** ⇒ DRC 永远红
           ★没有 board.Remove/Delete ⇒ 已画进 board 的退化图元**删不掉** ⇒ v25 会带 ~565 条零长段"""
        _c = getattr(self, "_committed", None)
        if not _c:
            return False
        rec = _c.pop(id(item), None)
        if not rec:
            return False
        obj = rec[1]
        try:
            self.b.Remove(obj)          # KiCad 8/9: BOARD.Remove
        except Exception:
            try:
                self.b.Delete(obj)       # 老版 API
            except Exception:
                return False
        return True


# ------------------------------------------------------------------ 差分对
def route_diff_pair(router, net_p, net_n, width=W_SIG, allow_via=True,
                    trunk_p=None, trunk_n=None, _allow_swap=True):
    """★差分对成对布 —— 先布 P, 再在 P 的走廊里布 N (软代价拉近 ⇒ 同层同间距)
       trunk_p/trunk_n: ((padA,padB),) —— 主干焊盘对 (让两根线走同一条走廊)
       返回 dict: 长度 / 长度差 / 最小间距

       ★★2026-11-05 **差分对耦合 (关键修复)**:
         上一轮: P 走完后, N 用 `dist_map` 软代价"被拉向" P, 但 ★**P 的 halo 仍是硬障碍**
           ⇒ N 想贴着 P 走, 但 P 周围 0.5mm 全被封死 ⇒ **N 跑不到 P 旁边**
           ⇒ 实测: 12 个 MIPI 对里 **6 个的 N 侧完全没布出来** (trk=0)
         这一轮: ★**布 N 时把 P 的 halo 豁免** (只留"精确距离 ≥ 0.45mm"作约束)
           ⇒ N 能真正贴着 P 平行走 ⇒ ★**100Ω 差分对的几何才成立**
           ⇒ ★实测 N 侧 trk=0 → 有走线"""
    res = {"p": net_p, "n": net_n}
    # ★★★★2026-11-06 12:5x **"长距主干优先" (env 门控, 默认不变)** ★★★★
    #   ★**为什么要有 (★实测机制, 不是猜)**:
    #     ★**实测 `CSI_D0_CK_N`**: 3 个焊盘 (C_AC 45.90,58.60 / TP 44.50,55.20 /
    #       CONN_CAM.17 86.90,51.40) ⇒ ★**MST 顺序先布了近的 2 个** ⇒ ★**铜局限 x41.95..47.70**
    #       ⇒ ★**第 3 个 (远 39.47mm) 完全走不出去** ⇒ ★**而 P 侧同目标布到了 x=86.2**
    #     ⇒ ★★**⇒ 差别只在"谁先占走廊"**
    #   ★**做法**: ★**给没有 trunk 的对, 自动挑"两端距离最远"的那对焊盘当主干**
    #     ⇒ ★**长距先布 ⇒ 先占住走廊; 其余短脚再从主干挂树**
    #   ★**用法**: `PCB_PAIR_AUTO_TRUNK=1`
    # ★★2026-11-06 12:5x **只给 N 侧用自动主干 (v67 实测: 两侧都用会让 CSI_D0_D0 从 ✓/✓ 变 ✗/✗)**
    _auto_mode = os.environ.get("PCB_PAIR_AUTO_TRUNK", "0")
    if _auto_mode in ("1", "N"):
        def _auto_trunk(net, trunk):
            if trunk:
                return trunk
            _pads = router.net_pads.get(net) or []
            if len(_pads) < 2:
                return None
            _best = None
            _bd = -1.0
            for _i in range(len(_pads)):
                for _j in range(_i + 1, len(_pads)):
                    _d = ((_pads[_i][2] - _pads[_j][2]) ** 2
                          + (_pads[_i][3] - _pads[_j][3]) ** 2)
                    if _d > _bd:
                        _bd = _d
                        _best = (_pads[_i], _pads[_j])
            if _best is None:
                return None
            return ((_best[0][1], _best[1][1]),)   # ★(_find_pad 用 padnum 找)
        if _auto_mode == "1":
            trunk_p = _auto_trunk(net_p, trunk_p)
        trunk_n = _auto_trunk(net_n, trunk_n)
        res["auto_trunk"] = _auto_mode
    r1 = router.route_net(net_p, width=width, allow_via=allow_via, trunk=trunk_p)
    res["p_ok"] = r1["ok"]
    if not r1["ok"]:
        # ★★★★2026-11-06 12:1x **P 侧兵底 (env 门控, 默认不变)** ★★★★
        #   ★**为什么要有 (★实测的不对称, 不是猜)**:
        #     · ★**N 侧有兵底** (耦合布不通 ⇒ 按普通网布) ⇒ "连上了但不等长" 远好过 "根本没连"
        #     · ★**但 P 侧没有兵底** ⇒ ★**P 侧一失败 ⇒ 整对直接放弃 ⇒ N 侧连试都不试**
        #     ⇒ ★★**⇒ 弱势的 N 侧有退路, 强势的 P 侧没有 ⇒ ★**完全不对称**
        #   ★**实测症状**: v60/v62 的 `CSI_D0_CK_P/N` = True/**False** ⇒ ★**N 侧差 39.46mm 连不到第三个点**
        #     ⇒ ★**而 N 侧若按"普通网"布 (不带耦合走廊), 空间大得多 ⇒ ★**有机会连上**
        #   ★**用法**: `PCB_PAIR_P_FALLBACK=1` ⇒ ★**P 侧失败也走"普通网"**
        #   ★★**为什么必须 env 门控**: ★**改了差分对的布法 ⇒ 所有臂的行为都变 ⇒ 既有臂可复现性破**
        if os.environ.get("PCB_PAIR_P_FALLBACK", "0") == "1":
            # ★**P 侧走"普通网" (不配对) ⇒ 后面 N 侧就没有走廊引导图了**
            router.pair_partner = None
            router.pair_block = set()
            router.pair_block_narrow = set()
            router.esc_avoid = set()
            r1 = router.route_net(net_p, width=width, allow_via=allow_via, trunk=trunk_p)
            res["p_ok"] = r1["ok"]
            res["p_fallback"] = True
            if not r1["ok"]:
                res["n_ok"] = False
                return res
            # ★**P 已按普通网布完 ⇒ N 侧直接按普通网布 (不再走耦合走廊)**
            r2 = router.route_net(net_n, width=width, allow_via=allow_via, trunk=trunk_n)
            res["n_ok"] = r2.get("ok", False)
            res["coupled"] = False
            res["ring"] = r2.get("ring")
            res["lp"] = round(r1["len"], 3)
            res["ln"] = round(r2.get("len", 0.0), 3)
            res["delta"] = round(abs(r1["len"] - r2.get("len", 0.0)), 3)
            return res
        res["n_ok"] = False
        return res
    # ★★**走廊引导图 (★渐进放宽 ring)** ——
    #   ★目标: 把 N 拉到 **P 路径外侧 ring 圈** ⇒ 既贴着 P 走 (差分对几何) 又不进 P 的 halo 禁区
    #   ★**渐进放宽**: ring 2 (0.50mm, 最接近 100Ω) → 4 → 6 → 8
    #   ★**为什么**: 走廊窄 + MIPI 路径长达 100~240mm ⇒ 单点堵死就整条不通
    #   ⇒ ★**不通就放宽一档** ⇒ ★既保住"贴着 P"的大方向, 又给 N 留出活路
    #   ⇒ ★**实际用了几档会记录** ⇒ 报告里点名哪些对不是最紧的 (不假装是 100Ω)
    r2 = None
    used_ring = None
    # ★★**渐进放宽 ring** (★在 route_net **内部**逐脚重试 ⇒ ★不会重复布已通的脚)
    #   ★ring 2 (0.50mm, 最接近 100Ω) → 4 → 6 → 8
    #   ★**为什么**: 走廊窄 + MIPI 路径长达 100~240mm ⇒ 单点堵死就整条不通
    #   ⇒ ★**不通就放宽一档** ⇒ ★既保住"贴着 P"的大方向, 又给 N 留出活路
    #   ⇒ ★**实际用了几档会记录** ⇒ 报告里点名哪些对不是最紧的 (不假装是 100Ω)
    router.pair_partner = net_p
    # ★★出脚区豁免 (env 开关, 默认关 ⇒ 不影响在跑的四臂)
    _exempt_n = net_n if PAIR_ESCAPE_EXEMPT else None
    router.pair_block, router.pair_block_narrow = router.build_pair_block(
        net_p, min_c=0.50, exempt_net=_exempt_n)
    # ★★2026-11-05 09:50 **N 侧不许与 P 同向出脚** (★0.4mm pitch 并行出脚必违规)
    # ★★★★2026-11-06 12:0x **这个约束做成可单独关 (env 门控, 默认不变)**
    #   ★**为什么**: ★**这是"N 侧永远布不出"的三重枷锁之一** ⇒ v60 实测:
    #     `CSI_D0_CK_N` 连了 2 个焊盘 (C_AC + TP) 但第 3 个 (CONN_CAM) 差 39.46mm
    #   ★**而"同向出脚必违规"这个前提**: 0.4mm pitch + 0.2mm 焊盘 ⇒ 同向出脚的两根直道
    #     中心距 0.4mm ⇒ 净距 0.4-0.1-0.1 = **0.2mm (恰好临界)** ⇒ ★**不是"必违规", 是"卡在临界"**
    #   ⇒ ★**在 W_MIN=0.15 下 (净距 0.225mm ⇒ 有 0.025mm 余量) ⇒ 同向出脚是合法的** ⇒ ★**⇒ 这个约束该放开**
    #   ★**用法**: `PCB_PAIR_ESC_AVOID=0` ⇒ ★**N 侧可以与 P 同向出脚** (★默认 1 = 旧行为)
    _esc_avoid_on = PAIR_ESCAPE_EXEMPT and (os.environ.get("PCB_PAIR_ESC_AVOID", "1") == "1")
    router.esc_avoid = set(router.esc_used_dirs.get(net_p, set())) if _esc_avoid_on else set()
    try:
        # ★每个 ring 一份引导图 (★route_net 内部逐脚挑 ⇒ 不重复布线)
        profiles = []
        for ring in (2, 4, 6, 8):
            guide, gdef = router.build_pair_guide(net_p, ring=ring)
            profiles.append((guide, gdef, ring))
        # ★★alpha 必须非 0 ⇒ ★**"耦合失败 ⇒ 不带走廊再试一次"的兵底才会触发**
        #   (上一版传 alpha=0 ⇒ 兵底永不触发 ⇒ N 侧大量不通 ⇒ unconnected 反而涨了 13)
        # ★★★★★★2026-11-10 20:0x 【★差分对的【层选择】(★env 门控 `PCB_PAIR_LAYERSEL`★)】★★★★★★
        #   ★**为什么要有 (★实测坐实★)**: ★★**官方板的差分对 P/N 【在【不同层】上分段走】★★**
        #     · ★`CSI_D0_CK_P` = F.Cu 158 / In2.Cu 71 · ★`CSI_D0_CK_N` = F.Cu 78 / In2.Cu 120 ★★
        #     ⇒ ★★**⇒ 两腿的层占比【相反】⇒ ⇒ 【层选择】是官方板避开擦边净距的关键** ★★
        #     ⇒ ★★**⇒ 而路由器【没有这个机制】⇒ ⇒ 两腿挤在同一层 ⇒ ⇒ 挤到 0.4280mm 就违规** ★★
        #   ★**做法**: ★**统计 P 侧各层的段数 ⇒ ⇒ 把 N 侧【优先限制到 P 用得少的层】** ★★
        #     ⇒ ★**限制是【优先】不是【禁止】(★只留一层 ⇒ N 侧可能完全布不出来⇒ ⇒ 反而更差★) ★★
        #     ⇒ ★★**⇒ ⇒ 【先试限制, 不行再放开】⇒ ⇒ 不会比现状更差** ★★
        if PAIR_LAYERSEL:
            # ★P 侧各层的段数
            _pcount = collections.Counter()
            for _s in router.tracks:
                if _s[0] == net_p:
                    _pcount[_s[5]] += 1
            if _pcount:
                # ★按 P 侧用得【少】的层排 (★同数时按层号★)
                _order = sorted(ROUTE_LAYERS, key=lambda l: (_pcount.get(l, 0), l))
                # ★★**至少留 2 层 (★只留 1 层 ⇒ N 侧可能完全布不出来⇒ ⇒ 反而更差★)** ★★
                _lim = set(_order[:max(2, len(_order) - 1)])
                router._layer_limit = _lim
                res["n_layers"] = sorted(_lim)
        r2 = router.route_net(net_n, width=width, allow_via=allow_via,
                              trunk=trunk_n, profiles=profiles, alpha=0.45)
        # ★★**限制下 N 侧没布出来 ⇒ ⇒ 放开限制再试一次 (★保证不比现状更差★)** ★★
        if not r2.get("ok") and PAIR_LAYERSEL and getattr(router, "_layer_limit", None):
            router._layer_limit = None
            res["n_layers_retry"] = True
            r2 = router.route_net(net_n, width=width, allow_via=allow_via,
                                  trunk=trunk_n, profiles=profiles, alpha=0.45)
    finally:
        router._layer_limit = None
        router.pair_partner = None
        router.pair_block = set()
        router.pair_block_narrow = set()
        router.esc_avoid = set()
    res["n_ok"] = r2["ok"]
    res["ring"] = r2.get("ring")
    # ★★2026-11-05 02:50 **兵底: 耦合布不通 ⇒ N 侧按普通网布 (不耦合)**
    #   ★**为什么加这个**: 实测 (tools/diff_pair_audit.py, 22 对全审计):
    #     15 对是"**N 侧压根没布出来**" (缺铜) ⇒ ★**这不是"长度差"问题, 是"没连"问题**
    #     ⇒ 而耦合走廊 (ring 2~8) 在 100~240mm 长路径上极易被单点堵死
    #   ★**取舍**: 耦合走不通时, 让 N 侧**按普通网走** (可能绕远、Δ 会大)
    #     ⇒ ★**"连上了但不等长" 远好过 "根本没连"** (没连 = DRC unconnected + 板子不工作)
    #   ★**代价会被如实记下**: res["coupled"]=False ⇒ 报告里点名这些对"未耦合/Δ 大"
    if not r2.get("ok"):
        r3 = router.route_net(net_n, width=width, allow_via=allow_via, trunk=trunk_n)
        res["n_ok"] = r3.get("ok", False)
        res["coupled"] = False
        res["fallback_len"] = round(r3.get("len", 0.0), 3)
        r2 = r3
    else:
        res["coupled"] = True
    # ★★★★2026-11-08 23:5x **"换边重试" (★env 门控 `PCB_PAIR_SWAP_RETRY=1`, 默认关 ⇒ 逐位不变)** ★★★★
    #   ★**触发条件 (★很窄)**: ★**只当【跟腿(原 N)彻底没布出来】时才试** ⇒ ★**能通的那些对一行都不受影响**
    #   ★**做法**: ★**把主腿(原 P)的铜摘掉 (r.tracks/r.vias + 重建 halo) ⇒ 以 N 为主腿重跑整对 (角色对调)**
    #     ⇒ ★**复用同一套耦合/走廊/兵底机制 (自己递归, 只换参数顺序) ⇒ 不新增算法**
    #   ★**采纳标准 (★必须是净胜)**: ★**只有换边后【两条腿都通】才采纳**
    #     ⇒ ★**否则把原来的主腿铜原样放回去 ⇒ 结果与不做换边时逐位相同 (★不制造"更差"的板)**
    if (not res.get("n_ok")) and PAIR_SWAP_RETRY and _allow_swap:
        _sv_tracks = list(router.tracks)
        _sv_vias = list(router.vias)
        # ★摘掉主腿的铜 (⇒ 让原 N 不再被它挡)
        router.tracks = [t for t in router.tracks if t[0] != net_p]
        router.vias = [v for v in router.vias if v[0] != net_p]
        try:
            router.rebuild_halo()
            _sw = None
            try:
                _sw = route_diff_pair(router, net_n, net_p, width=width,
                                      allow_via=allow_via, trunk_p=trunk_n,
                                      trunk_n=trunk_p, _allow_swap=False)
            except Exception as _e:
                print("  ★换边重试异常 (★放弃换边): %s" % _e)
                _sw = None
            # ★换边后: _sw["p_ok"] = 原 N (新主腿) · _sw["n_ok"] = 原 P (新跟腿)
            if _sw and _sw.get("p_ok") and _sw.get("n_ok"):
                res["p_ok"] = _sw["n_ok"]
                res["n_ok"] = _sw["p_ok"]
                res["lp"] = round(_sw.get("ln", 0.0), 3)
                res["ln"] = round(_sw.get("lp", 0.0), 3)
                res["delta"] = round(abs(res["lp"] - res["ln"]), 3)
                res["swapped"] = True
                res["ring"] = _sw.get("ring")
                r1 = {"ok": res["p_ok"], "len": res["lp"]}
                r2 = {"ok": res["n_ok"], "len": res["ln"], "ring": _sw.get("ring")}
                print("  ★换边成功 (★原来不通的腿现在有铜了): %s / %s" % (net_p, net_n))
            else:
                # ★★**没赢 ⇒ 原样恢复** (★主腿的铜回到原位, halo 重建)
                router.tracks = _sv_tracks
                router.vias = _sv_vias
                router.rebuild_halo()
                print("  ★换边没赢 (★恢复原状, 结果不变)")
        except Exception as _e2:
            router.tracks = _sv_tracks
            router.vias = _sv_vias
            try:
                router.rebuild_halo()
            except Exception:
                pass
            print("  ★换边重试异常 (★已恢复原状): %s" % _e2)
    res["ring"] = r2.get("ring")
    res["lp"] = round(r1["len"], 3)
    res["ln"] = round(r2.get("len", 0.0), 3)
    res["delta"] = round(abs(r1["len"] - r2["len"]), 3)
    # ★长度配平: 短的那根加蛇形
    if res["delta"] > 0.13:
        # ★★2026-11-05 07:25 **改用 v3** (固定凸起高度 + 反算每凸起能补多少)
        #   ⇒ v2 的死穴: 用**剩余差值**反算凸起高度 ⇒ 差越大 a 越大 ⇒ **超过 a≤3 上限 ⇒ 一个凸起都加不上**
        #   ⇒ v3: 固定 a=3.0 ⇒ 每凸起 +5.12mm (base=0.96) ⇒ Δ32.4 ⇒ 7 个凸起
        #   ⇒ 先试 v3, 不够再回退 v2 (v2 在**小差值**时更精确)
        _short = net_p if r1["len"] < r2["len"] else net_n
        got = router.add_meander_v3(_short, res["delta"])
        if got < res["delta"] - 0.05:
            got += router.add_meander_v2(_short, res["delta"] - got)
        res["meander"] = round(got, 3)
        res["lp"] = round(router.net_length(net_p), 3)
        res["ln"] = round(router.net_length(net_n), 3)
        res["delta"] = round(abs(res["lp"] - res["ln"]), 3)
    res["min_gap"] = _min_gap(router, net_p, net_n)
    return res


def _min_gap(router, net_a, net_b):
    """两条网之间的最小间距 (mm) —— 差分对"同间距"的实测值"""
    g = router.g
    ca, cb = set(), set()
    ox, oy = router.bb[0], router.bb[1]
    for s in router.tracks:
        if s[0] == net_a:
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], g, 0, ox, oy):
                ca.add((i, j))
        elif s[0] == net_b:
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], g, 0, ox, oy):
                cb.add((i, j))
    if not ca or not cb:
        return None
    best = 1e9
    for (i, j) in ca:
        for (di, dj) in ((1, 0), (0, 1), (1, 1), (1, -1)):
            k = (i + di, j + dj)
            if k in cb:
                d = g * math.hypot(di, dj)
                if d < best:
                    best = d
    return round(best, 3) if best < 1e9 else None


# ------------------------------------------------------------------ GND 平面
def add_gnd_planes(board, layers=None, net="GND", fill=True):
    # ★★2026-11-05 06:40 **层数可配 ⇒ 平面层跟着走**
    #   ★★6 层: **(1, 3, 5)** = In1.Cu + In3.Cu + B.Cu
    #     ⇒ ★**之前只有 (1,5) 两个 GND 平面** ⇒ In2.Cu/In4.Cu 两个信号层**底下没有回流面**
    #       ⇒ ① 信号回流路径断 ⇒ ② GND 下拉过孔可落的平面少 ⇒ ★**GND 未连接项变多**
    #   ★8 层: (1, 3, 5, 7) = In1.Cu + In3.Cu + In5.Cu + B.Cu
    #     (ROUTE_LAYERS = [0,2,4,6] = F.Cu/In2.Cu/In4.Cu/In6.Cu ⇒ 平面正好夹在信号层之间)
    if layers is None:
        # ★★2026-11-05 07:40 **跟着层数走** ⇒ 10 层 ⇒ (1,3,5,7,9) = In1/In3/In5/In7 + B.Cu
        layers = tuple(li for li in range(1, NLAYERS, 2))
    """★L2 / L6 完整 GND 平面 (STACKUP.md: L2 GND / L6 GND)
       ★**完整平面 = 不分割** ⇒ 满足 LAYOUT_RULES "L2/L6 不得在差分对下方被分割"
       ★平面层不放信号 (路由器只用 L1/L3/L5)"""
    bb = board.GetBoardEdgesBoundingBox()
    pts = [pcbnew.VECTOR2I(bb.GetLeft(), bb.GetTop()),
           pcbnew.VECTOR2I(bb.GetRight(), bb.GetTop()),
           pcbnew.VECTOR2I(bb.GetRight(), bb.GetBottom()),
           pcbnew.VECTOR2I(bb.GetLeft(), bb.GetBottom())]
    made = 0
    code = netcode(board, net)
    for li in layers:
        z = pcbnew.ZONE(board)
        z.SetLayer(CU_LAYERS[li])
        if code > 0:
            z.SetNetCode(code)
        z.SetLocalClearance(pcbnew.FromMM(0.25))
        try:
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        except Exception:
            pass
        try:
            z.SetAssignedPriority(0)
        except Exception:
            pass
        lc = pcbnew.SHAPE_LINE_CHAIN()
        for p in pts:
            lc.Append(p)
        lc.SetClosed(True)
        z.AddPolygon(lc)
        board.Add(z)
        made += 1
    if fill:
        _fill_zones(board)
    return made


def _fill_zones(board):
    try:
        board.BuildConnectivity()
    except Exception:
        pass
    try:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        return True
    except Exception as e:
        print("  ⚠️ 区域填充失败: %s" % e)
        return False


# ------------------------------------------------------------------ 整板布线计划
# ★差分对清单 (按任务优先级)
DIFF_PAIRS = [
    # (P 网, N 网, P 主干, N 主干)
    ("NET_USB_D_P_TYPEC", "NET_USB_D_N_TYPEC",
     ((("J_USB_C", "2"), ("R_SER_USB_D_P", "2")),),
     ((("J_USB_C", "3"), ("R_SER_USB_D_N", "2")),)),
    ("USB_D_P_SRC", "USB_D_N_SRC",
     ((("R_SER_USB_D_P", "1"), ("J_SOM_P1", "92")),),
     ((("R_SER_USB_D_N", "1"), ("J_SOM_P1", "94")),)),
    ("CSI_D0_CK_P_SRC", "CSI_D0_CK_N_SRC", None, None),
    ("CSI_D0_CK_P", "CSI_D0_CK_N", None, None),
    ("CSI_D0_D0_P_SRC", "CSI_D0_D0_N_SRC", None, None),
    ("CSI_D0_D0_P", "CSI_D0_D0_N", None, None),
    ("CSI_D0_D1_P_SRC", "CSI_D0_D1_N_SRC", None, None),
    ("CSI_D0_D1_P", "CSI_D0_D1_N", None, None),
    ("CSI_D0_D2_P_SRC", "CSI_D0_D2_N_SRC", None, None),
    ("CSI_D0_D2_P", "CSI_D0_D2_N", None, None),
    ("CSI_D0_D3_P_SRC", "CSI_D0_D3_N_SRC", None, None),
    ("CSI_D0_D3_P", "CSI_D0_D3_N", None, None),
    ("DSI_D0_CK_P_SRC", "DSI_D0_CK_N_SRC", None, None),
    ("DSI_D0_CK_P", "DSI_D0_CK_N", None, None),
    ("DSI_D0_D0_P_SRC", "DSI_D0_D0_N_SRC", None, None),
    ("DSI_D0_D0_P", "DSI_D0_D0_N", None, None),
    ("DSI_D0_D1_P_SRC", "DSI_D0_D1_N_SRC", None, None),
    ("DSI_D0_D1_P", "DSI_D0_D1_N", None, None),
    ("DSI_D0_D2_P_SRC", "DSI_D0_D2_N_SRC", None, None),
    ("DSI_D0_D2_P", "DSI_D0_D2_N", None, None),
    ("DSI_D0_D3_P_SRC", "DSI_D0_D3_N_SRC", None, None),
    ("DSI_D0_D3_P", "DSI_D0_D3_N", None, None),
]

# ★电源网 (宽铜) —— 优先级: 大电流链 → 局部电源 → 一般电源
# ★**线宽上限由出脚决定** (LAYOUT_RULES: SOM 输入 ≥2A ⇒ ≥0.5mm, 但出脚焊盘更窄):
#   · SoM BTB = 0.4mm pitch / 0.2mm 焊盘 ⇒ 出脚只能 0.2mm (否则净距不够)
#   · USB-C 座 = 0.5mm pitch / 0.28mm 焊盘 ⇒ 出脚只能 0.25mm
#   ⇒ **"≥0.5mm 铜宽" 只能在出脚后的开阔区用铜皮/并联铜条实现** (本轮未做 ⇒ 下一轮)
POWER_NETS = [
    ("RAIL_SOM_DCIN", 0.20, 1),      # SOM 输入 (≥2A) —— 出脚限 0.2mm
    ("RAIL_DEMO_5V", 0.25, 1),       # USB-C 5V 输入链 —— 出脚限 0.25mm
    ("SYS_PCB", W_PWR, 1),           # 主板主供电 (电池开关后) ⇒ 0.5mm
    # ★**过孔阵列 (via_count>1) 暂时关闭**: 阵列里的外围孔没有走线穿过
    #   ⇒ KiCad 报 via_dangling (7 条) ⇒ ★"坏掉的过孔阵列比没有阵列更糟"
    #   ⇒ 大电流过孔阵列要在下一轮**连同铜皮**一起做 (见 ROUTING_REPORT §4)
    ("VDD_3V3_IO", W_SIG, 1),
    ("VDD_1V8_IO", W_SIG, 1),
    ("LIGHT_3V3", W_SIG, 1),
    ("V_CORE", W_SIG, 1),
    ("LIGHT_5V", W_SIG, 1),
    ("LIGHT_1V8", W_SIG, 1),
    ("V_SOC_IO", W_SIG, 1),
    ("BAT", W_SIG, 1),
    ("BAT_SW", W_SIG, 1),
    ("SENSOR_VDD_IO", W_SIG, 1),
    ("SENSOR_CORE", W_SIG, 1),
    ("SENSOR_AVDD", W_SIG, 1),
]

# ★上电/复位/时序关键线 (LAYOUT_RULES §2: 每个电源 IC 的 EN 必须有明确网络)
TIMING_NETS = [
    "RESET_N", "RESET_N_SOC", "CAM_RESET_N", "PWR_GOOD", "PWR_ON",
    "PG_AND", "BOOT_N", "EN_VIO", "CARRIER_BOARD_EN", "EN_VCORE",
    "VBUS_DET", "VBUS_DET_D", "SUPV_SENSE", "SUPV_CT",
]


def _save_board_progress(board, tag=""):
    """★中途落盘 (★超时不丢活) —— ★**必须"存盘→重读→填平面→再存"**:
       同会话里填平面会把整片 GND 当孤岛删空 (已知坑) ⇒ 重读后再填才靠谱"""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        proj = os.path.dirname(here)
        # ★★2026-11-05 05:58 **修: 必须跟 PCB_OUT 同一口径** (与 gen_pcb_netlist_board.py:54 一致)
        #   ⇒ 原来硬编码官方板路径 ⇒ ★**并行实验 (PCB_OUT=…) 的中途落盘把官方板覆盖成骨架**
        #   ⇒ 实测: 05:50:23 官方板被 8 层实验写成 468951B / 0 段走线的骨架
        #   ⇒ ★**实验输出必须隔离** (AGENTS.md 铁律: 模块内部已实现的项母板不重复做 ⇒ 同理: 实验不许碰官方板)
        pcb = os.environ.get("PCB_OUT") or os.path.join(proj, "HW", "PCB", "demo_mainboard.kicad_pcb")
        pcbnew.SaveBoard(pcb, board)
        b3 = pcbnew.LoadBoard(pcb)
        b3.BuildConnectivity()
        filler = pcbnew.ZONE_FILLER(b3)
        filler.Fill(b3.Zones())
        pcbnew.SaveBoard(pcb, b3)
        print("  [SAVE] 阶段性落盘 %s" % (tag or ""))
    except Exception as e:
        print("  ⚠️ 阶段性落盘失败: %s" % e)


def route_board(board, verbose=True):
    """★★ 整板布线 —— 一次跑完, 返回统计
       (调用方: state/gen_pcb_netlist_board.py —— ★布线必须落进生成器)"""
    import time
    t0 = time.time()
    stats = {"pairs": [], "nets": {}, "failed": [], "gnd": {}}
    r = GridRouter(board)

    # ---------- 0) GND 完整平面 (L2 + L6) —— 先建, 后面所有布线绕开
    add_gnd_planes(board, layers=None, fill=False)
    if verbose:
        print("  [GND] L2/L6 完整平面已建 (★不分割 ⇒ 差分对下方参考平面完整)")
    # ★★2026-11-05 10:25 **GND 先布** (env 开关 PCB_GND_FIRST=1)
    #   ★**为什么**: GND 焊盘的落孔位置最"娇气" ⇒ 排在信号之后就没位置了
    #   ⇒ ★**先占位** (焊盘内过孔最省空间) ⇒ 信号线再绕
    if GND_FIRST:
        _gok, _gfail = r.route_gnd_drops("GND")
        stats["gnd_first"] = {"drops": _gok, "fail": _gfail}
        if verbose:
            print("  [GND ] ★**先布** 下拉过孔 %d 成功 / %d 失败 (失败原因 %s)"
                  % (_gok, _gfail, getattr(r, "gnd_fail_why", {})))
        # ★**先布过的焊盘不再重复** (route_gnd_drops 内部按 done_pads 记, 但这里要防止二次落孔)
        r.gnd_done_first = True

    # ---------- 1) 差分对 (成对布) —— ★**顺序按 brief 的优先级**:
    #   ① USB 对 (短, 在板边) 先布 (它们在 F.Cu 上占地方少)
    #   ② **电源大电流** (板级长干道, 要整片空板!)
    #   ③ MIPI CSI/DSI 对 (最难, 最后布 —— 让它们吃剩下的空间)
    #   ★上一轮把 MIPI 放在电源前面 ⇒ MIPI 先把 F.Cu 占了 ⇒ 电源长干道全断
    USB_PAIRS = [p for p in DIFF_PAIRS
                 if "USB" in p[0] or "USB" in p[1]]
    MIPI_PAIRS = [p for p in DIFF_PAIRS if p not in USB_PAIRS]

    def _run_pairs(pairs):
        for (p, n, tp, tn) in pairs:
            if p not in r.net_pads or n not in r.net_pads:
                continue
            res = route_diff_pair(r, p, n, trunk_p=tp, trunk_n=tn)
            stats["pairs"].append(res)
            stats["pair_fallback"] = stats.get("pair_fallback", 0) + res.get("n_fallback", 0)
            if verbose:
                print("  [PAIR] %-22s / %-22s  ok=%s/%s  L=%.2f/%.2f  Δ=%.3fmm  间距=%s%s"
                      % (p, n, res.get("p_ok"), res.get("n_ok"),
                         res.get("lp", 0), res.get("ln", 0), res.get("delta", 0),
                         res.get("min_gap"),
                         ("" if res.get("n_ok") else "  ★N 未通")
                         + ("  ★走廊ring=%s" % res.get("ring") if res.get("ring") else "")
                         + ("  ★退化:无耦合" if res.get("n_fallback") else "")))

    _run_pairs(USB_PAIRS)

    # ---------- 1a) ★★★【MIPI 差分对提前】(★env 门控: PCB_PAIR_BEFORE_PWR, ★默认关 ⇒ 行为逐位不变)★★★ ★★★
    #   ★★**为什么要有 (★2026-11-09 23:3x 实测机制)**: ★★★
    #     ★**实测**: ★**我们那 24 条差分腿 (★CSI/DSI) 属于 MIPI 批, ★而 MIPI 批的路由顺序是【排在电源之后】**
    #       ⇒ ★★**⇒ 它们【输给供电网】(★供电网先占 F.Cu)** ⇒ ★★**⇒ 这是差分腿的真正排队劣势** ★★
    #     ★**上一轮实测**: ★**优先布(单网) 让 14 个非差分网一次就通, 但差分主干 `CSI_D0_CK_*` 被打死**
    #       ⇒ ★★**⇒ 因为差分腿是【成对布】(`route_diff_pair` 同时走 P 和 N) ⇒ 不是单网布 ⇒ ⇒ [排前面]对它无效** ★★
    #       ⇒ ★★**⇒ 只能改【差分对本身在队列里的位置】** ★★
    #   ★★**⚠️ 源码原警告 (★v74 教训)**: ★★**"上一轮把 MIPI 放在电源前面 ⇒ MIPI 先把 F.Cu 占了 ⇒ 电源长干道全断"** ★★
    #     ⇒ ★★**⇒ 所以本开关【零和】⇒ ⇒ 【必须配合 0.15mm (★减少线的条数⇒腾出余量)才有双赢可能】** ★★
    #       (★实测: ★`PCB_W_MIN=0.15` + 优先布 那轮 = ★**省铜 416 段** ★★ ⇒ ★★**余量存在** ★★)
    #   ★**用法**: `PCB_PAIR_BEFORE_PWR=1` (★建议同时开 `PCB_W_MIN=0.15`)
    if os.environ.get("PCB_PAIR_BEFORE_PWR", "0") == "1":
        _n_mipi_first = 0
        for (_p, _n, _tp, _tn) in MIPI_PAIRS:
            if _p not in r.net_pads or _n not in r.net_pads:
                continue
            res = route_diff_pair(r, _p, _n, trunk_p=_tp, trunk_n=_tn)
            stats["pairs"].append(res)
            stats["pair_fallback"] = stats.get("pair_fallback", 0) + res.get("n_fallback", 0)
            _n_mipi_first += 1
            if verbose:
                print("  [PAIR*] %-21s / %-21s  ok=%s/%s  L=%.2f/%.2f  Δ=%.3fmm 间距=%s%s"
                      % (_p, _n, res.get("p_ok"), res.get("n_ok"),
                         res.get("lp", 0), res.get("ln", 0), res.get("delta", 0),
                         res.get("min_gap"),
                         ("" if res.get("n_ok") else "  ★N 未通")))
        if verbose:
            print("  [PAIR*] ★MIPI 差分对 %d 对已【提前到电源之前】布 (★⇒ 它们先挑走廊 ⇒ ★★**代价: 电源要让路** ★★)" % _n_mipi_first)

    # ---------- 1b) ★★★【优先网】(★env 门控: PCB_PRIORITY_NETS, ★默认空 ⇒ 行为逐位不变)★★★ ★★★
    #   ★★**为什么要有 (★2026-11-09 21:4x 实测机制)**: ★★★
    #     ★**实测**: ★**挪 12 个焊盘 (0.3mm) ⇒ 走线段 13407→15867 (+2460) ⇒ ★**但 45 条未连接里的
    #       【非差分】那些网, 它们的铜长【各 +9~21mm】(★供电网合计 +266.2mm)⇒ ★★**多出来的空间被供电网拿走了**
    #       ⇒ ★★**⇒ [让出空间] ≠ [空间被用在需要的地方]** ★★★ ★★★
    #     ★★**⇒ 路由器本来就排着队: ①差分对 ②电源 ③MIPI ④其余网络(★最后) ⇒ ★★**最后那批只能捡剩的通道**
    #       (★★**源码原注释: [82% 的失败脚在这批]** ⇒ ★★**路由器早就知道这个问题**) ★★★
    #     ★★**⇒ 本开关: ★把指定的网提到【电源之前】布 ⇒ ★★**它们先挑走廊 ⇒ 效果可预测**
    #       (★对比: [挪焊盘]是【混沌景观上抽奖】⇒ ★实测两轮都是净收益为负) ★★★
    #   ★**用法**: `PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;I2C_A_SCL"` (★分号分隔, ★默认空)
    #   ★**注意**: ★**只加"确实布不通的网"** ⇒ ★★**别把好网提前 ⇒ 那是抢别人的通道** ★★
    _prio = [x.strip() for x in (os.environ.get("PCB_PRIORITY_NETS", "") or "").split(";") if x.strip()]
    # ★★★★**★2026-11-09 21:5x 【优先网按跨距排序】(★env 门控 PCB_PRIO_SPAN_SORT, ★默认关⇒逐位不变)** ★★★★
    #   ★**为什么要有 (★v76rr 臂实测出来的机制, ★不是猜)**: ★★★
    #     ★**实测**: `JTAG_TDO` 的 J_DEBUG.4 焊盘被 **`JTAG_TDI` 的铜挡住 0.213mm** (★需 ≥0.325mm 才走得动)
    #     ⇒ ★**`JTAG_TDI` 在优先名单里排第 11 个 ⇒ 先布 ⇒ 把同族另外两个 (TDO/TMS) 的出脚格堵死**
    #     ⇒ ★**实测**: `JTAG_TMS` 的 J_DEBUG.2 同样被 `JTAG_TDI` 挡 0.208mm ⇒ ★**两兄弟一起死** ★★
    #     ⇒ ★★**⇒ 同族内部 [谁先布谁赢] ⇒ 而优先名单是【人写的顺序】⇒ 等于抽签** ★★ ★★★
    #     ★★**⇒ 修法: 优先网内部按【跨距降序】排 (★与第 4 阶段"其余网络"同口径) ★★**
    #       ⇒ ★**JTAG 族: TMS(23.8mm) → TDO(18.0mm) → TDI(14.3mm)** ⇒ ★**两边先走的先占 (★J_DEBUG 外侧脚先走) ★★
    #       ⇒ ★**实测基线里 JTAG_TDO/TMS 就是通的 (= REST 阶段按跨距排的顺序) ⇒ 这不是新赌法, 是复现已知好顺序** ★★
    #   ★**注意**: ★**这是"顺序"不是"加铜" ⇒ 不增加铜量 ⇒ 不加剧走廊零和** ★★
    if os.environ.get("PCB_PRIO_SPAN_SORT", "0") == "1":
        def _span_of(_n):
            _ps = r.net_pads.get(_n) or []
            _b = 0.0
            for _i in range(len(_ps)):
                for _j in range(_i + 1, len(_ps)):
                    _d = abs(_ps[_i][2] - _ps[_j][2]) + abs(_ps[_i][3] - _ps[_j][3])
                    if _d > _b:
                        _b = _d
            return _b
        _prio.sort(key=lambda _n: (-_span_of(_n), -len(r.net_pads.get(_n) or [])))
        if verbose:
            print("  [PRIO] ★按跨距降序排 (★PCB_PRIO_SPAN_SORT=1): %s"
                  % ", ".join(_prio))
    if _prio:
        _n_prio = 0
        for _net in _prio:
            if _net not in r.net_pads or _net in r.routed:
                continue
            res = r.route_net(_net, width=W_SIG)
            stats["nets"][_net] = res
            if not res.get("ok"):
                stats["failed"].append(_net)
                # ★★★★**★2026-11-09 21:5x 【失败优先网可重试】(★env 门控 PCB_PRIO_RETRY, ★默认关⇒逐位不变)** ★★★★
                #   ★**实测机制**: ★**`route_net()` 失败也 `self.routed.add(net)`** ⇒ 第4阶段"其余网络"
                #     按 `n not in r.routed` 跳过 ⇒ ★**该网彻底没铜 (★0 段) ⇒ 再也没被试过** ★★
                #   ★**实测受害者**: ★**`JTAG_TDO`/`JTAG_TMS`/`UART_RX`/`I2C_B_SCL`/`I2C_B_SDA`**
                #     (★日志: `[RIPUP] 27 个失败网 ⇒ 重布成功 0 个` ⇒ 收尾 rip-up 也救不回来) ★★
                #   ★**修法**: ★**优先阶段失败 ⇒ 把该网从 `routed` 里拿掉 ⇒ 让第4阶段再试一次** ★★
                #   ★**为什么默认关**: ★**这会让失败网的排布时机改变 ⇒ 既有臂必须逐位不变** ★★
                if os.environ.get("PCB_PRIO_RETRY", "0") == "1":
                    r.routed.discard(_net)
                    r.routed_ok.discard(_net)
            _n_prio += 1
            if verbose:
                print("  [PRIO] %-16s ok=%s 失败脚=%d  L=%.1fmm"
                      % (_net, res.get("ok"), res.get("fail"), res.get("len", 0.0)))
        if verbose:
            print("  [PRIO] ★优先网 %d 个已布 (★提到电源之前 ⇒ ★★**它们先挑走廊**) ★★" % _n_prio)

    # ---------- 2) 电源 (宽铜 + 过孔阵列) —— ★**必须在 MIPI 之前**
    for (net, w, vc) in POWER_NETS:
        if net not in r.net_pads:
            continue
        res = r.route_net(net, width=w, via_count=vc)
        stats["nets"][net] = res
        if not res["ok"]:
            stats["failed"].append(net)
        if verbose:
            print("  [PWR ] %-16s w=%.2fmm  ok=%s  失败脚=%d  L=%.1fmm"
                  % (net, w, res["ok"], res["fail"], res["len"]))

    # ---------- 3) MIPI 差分对 (最难 ⇒ 最后)
    # ★★2026-11-09 23:4x: ★**若已在 [1a] 提前布过 MIPI (★PCB_PAIR_BEFORE_PWR=1)⇒ ★★**这里必须跳过, ★否则同一批对被布两次 (★⇒ 铜量翻倍 + 归因不清)** ★★
    if os.environ.get("PCB_PAIR_BEFORE_PWR", "0") == "1":
        if verbose:
            print("  [PAIR*] ★MIPI 已在 [1a] 提前布过 ⇒ 本步跳过 (★避免重复布)")
    else:
        _run_pairs(MIPI_PAIRS)
    # ★★★★2026-11-09 00:4x **"最后一趟再换边" (★env 门控 `PCB_PAIR_SWAP_LAST=1`, 默认关 ⇒ 逐位不变)** ★★★★
    #   ★**为什么要有这一趟 (★v74 实测出来的, 不是拍脑袋)**:
    #     ★**v74 (中途换边)**: 换边救回 CSI_D0_D0 两对 ⇒ ★**但同一次运行里 DSI_D0_CK_P/N
    #       从"两条都有铜"变成"两条都零铜"** ⇒ ★**⇒ 换边会改铜 ⇒ 会影响【后面才布的差分对】**
    #   ★**做法**: ★**全部对都布完之后, 把【跟腿没布出来】的那些对逐个【两条腿的铜一起摘掉】,
    #     再以【跟腿为主腿】重跑整对** ⇒ ★**换边只影响同批次里它后面的少数对**
    #     ⇒ ★**而且此时别的对的铜都在 ⇒ 新铜必须挤进剩下的空间 ⇒ 比中途换边更苛刻 (★实测才知道行不行)**
    #   ★**与 `PCB_PAIR_SWAP_RETRY` 的关系**: ★**两个开关【互斥】(★同时开 = 在途换边 + 末尾换边 ⇒ 归因不清)**
    if PAIR_SWAP_LAST and not PAIR_SWAP_RETRY:
        _last_n = 0
        for (p, n, tp, tn) in MIPI_PAIRS:
            if p not in r.net_pads or n not in r.net_pads:
                continue
            # ★**只看"跟腿完全没铜"的对** (★有铜但 Δ 超差的另说, 那是配平问题)
            if r.net_length(n) > 0.001:
                continue
            _sv_t = list(r.tracks)
            _sv_v = list(r.vias)
            r.tracks = [t for t in r.tracks if t[0] not in (p, n)]
            r.vias = [v for v in r.vias if v[0] not in (p, n)]
            try:
                r.rebuild_halo()
                _res = route_diff_pair(r, n, p, trunk_p=tn, trunk_n=tp)
                if _res.get("p_ok") and _res.get("n_ok"):
                    _last_n += 1
                    print("  [PAIR-LAST] %-22s / %-22s 换边成功 L=%.2f/%.2f 间距=%s"
                          % (p, n, _res.get("ln", 0.0), _res.get("lp", 0.0), _res.get("min_gap")))
                    stats["pairs"].append(_res)
                else:
                    # ★**没赢 ⇒ 原样恢复**
                    r.tracks = _sv_t
                    r.vias = _sv_v
                    r.rebuild_halo()
                    print("  [PAIR-LAST] %-22s / %-22s 换边没赢 (★恢复原状)" % (p, n))
            except Exception as _e:
                r.tracks = _sv_t
                r.vias = _sv_v
                try:
                    r.rebuild_halo()
                except Exception:
                    pass
                print("  [PAIR-LAST] %-22s / %-22s 异常 (★已恢复): %s" % (p, n, _e))
        print("  [PAIR-LAST] 末尾换边成功 %d 对" % _last_n)
        stats["pair_last_swapped"] = _last_n
    # ---------- 4) ★★2026-11-05 08:45 **同网缝合 (net stitching)** ——
    #   ★**为什么放这儿**: 实测 v25 的 82 条未连里 ★**19 条是 GND + 31 条集中在两个连接器**
    #     ⇒ 全是"**同网多点**" ⇒ ★★ 同网焊盘之间本来就该短铜直连 (PCB 标准做法) ⇒ ★**一根直线就能接上**
    #   ★**必须在 rip-up 之前** ⇒ ⇒ rip-up 也能用上这些短铜
    try:
        _nst = r.stitch_same_net(verbose=verbose)
        stats["stitched"] = _nst
        if verbose:
            print("  [STITCH] 同网缝合: 新增 %d 条短铜 (多脚连接器/GND 优先受益)" % _nst)
    except Exception as e:
        print("  ⚠️ 同网缝合失败: %s" % e)

    # ★★★2026-11-05 07:50 **rip-up & reroute (收尾杀招)** ——
    #   ★**时机**: 必须在**阶段性 commit 之前** ⇒ ⇒ 被拆的线**根本不会落到板上** ⇒ 板上无废铜
    #   ★**目标**: 实测 78 个失败脚里 **64 个 (82%) 是"中途被堵死"** ⇒ 只能拆线重走
    _failed = sorted(set([n for n, v in stats["nets"].items() if not v.get("ok")]
                          + [e["net"] for e in r.fail_detail]))
    # ★★2026-11-05 07:55 **rip-up 可关** (PCB_RIPUP=0) ⇒ 便于单变量对比
    if _failed and os.environ.get("PCB_RIPUP", "1") != "0":
        _nrip = r.ripup_and_reroute(_failed, rip_per_net=6, verbose=verbose)
        stats["ripup_ok"] = _nrip
        if verbose:
            print("  [RIPUP] 收尾: 尝试 %d 个失败网 ⇒ 重布成功 %d 个" % (len(_failed), _nrip))
        # ★重布成功的网要重新统计 (失败列表会变)
        stats["failed"] = [n for n in set(stats["failed"])
                           if not (stats["nets"].get(n) or {}).get("ok")]
    # ★★2026-11-05 07:05 **中途存盘前先把已布的走线 commit 到板子上**
    #   ⇒ 原来直接存 ⇒ board 上还没有走线图元 ⇒ ★**存出来必然是 0 走线骨架** ⇒ "超时不丢活"没保住任何进度
    try:
        _n = r.commit(board)
        print("  [SAVE] 阶段性 commit: %d 个图元 (MIPI 后)" % _n)
    except Exception as e:
        print("  ⚠️ 阶段性 commit 失败: %s" % e)
    _save_board_progress(board, "MIPI 后")

    # ---------- 4) 电源 (宽铜 + 过孔阵列)
    # ---------- 5) 时序/复位/EN 关键线
    for net in TIMING_NETS:
        if net not in r.net_pads:
            continue
        res = r.route_net(net, width=W_SIG)
        stats["nets"][net] = res
        if not res["ok"]:
            stats["failed"].append(net)
        if verbose:
            print("  [TIME] %-16s ok=%s  失败脚=%d  L=%.1fmm"
                  % (net, res["ok"], res["fail"], res["len"]))

    # ---------- 4) 其余网络 (★★2026-11-05 07:35 **改按"跨距"降序** ⇒ 长干道先走)
    #   ★**旧口径 (按焊盘数从多到少) 的问题**: 这批网**最后才布** ⇒ 前面 USB对/电源/MIPI
    #     已经把 F.Cu 占掉 ⇒ ★**长干道网 (实测 60~100mm) 只能捡剩的通道 ⇒ 82% 的失败脚在这批**
    #   ★**新口径**: 按网的"跨距" (各焊盘的曼哈顿跨度) 降序 ⇒ ★**长网先占空白板面, 短网填空隙**
    rest = [n for n in r.net_pads
            if len(r.net_pads[n]) >= 2 and n not in r.routed and n != "GND"]

    def _span(n):
        """该网的跨距估计 (各焊盘两两曼哈顿距离的最大值) ⇒ 越长越先布"""
        ps = r.net_pads[n]
        best = 0.0
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                d = abs(ps[i][2] - ps[j][2]) + abs(ps[i][3] - ps[j][3])
                if d > best:
                    best = d
        return best

    rest.sort(key=lambda n: (-_span(n), -len(r.net_pads[n])))
    for net in rest:
        res = r.route_net(net, width=W_SIG)
        stats["nets"][net] = res
        if not res["ok"]:
            stats["failed"].append(net)
    if verbose:
        print("  [REST] 其余 %d 个网已布" % len(rest))
    # ★★2026-11-06 01:4x **v49: 第二轮 rip-up (★在"其余网"之后)**
    #   ★**为什么必须有**: 第一轮 rip-up 排在 "其余网" **之前** ⇒ ⇒ **普通信号网
    #     (FSIN_OUT / SPI_* / JTAG_TDI / UART_RX / USB_CC2 / PWR_GOOD / ID_DETECT_0 ...)
    #     还没被尝试过** ⇒ ⇒ **不在失败清单里** ⇒ ⇒ **第一轮根本轮不到它们**
    #   ★**实测**: 官方板 26 个"整张板零铜"的网 **全部是普通信号网** ⇒ ⇒ **第一轮救不到**
    #   ★**上限**: `PCB_RIPUP_MAX` ⇒ 防止第二轮无限拖时间
    if RIPUP_ALIVE and os.environ.get("PCB_RIPUP", "1") != "0":
        _failed2 = sorted(set([n for n, v in stats["nets"].items() if not v.get("ok")]
                               + [e["net"] for e in r.fail_detail]))
        _cap = max(1, int(os.environ.get("PCB_RIPUP_MAX", "40")))
        if len(_failed2) > _cap:
            if verbose:
                print("  [RIPUP] 第二轮候选 %d 个 ⇒ ★**按上限只取前 %d 个**" % (len(_failed2), _cap))
            _failed2 = _failed2[:_cap]
        if _failed2:
            _nrip2 = r.ripup_and_reroute(_failed2, rip_per_net=6, verbose=verbose)
            stats["ripup_ok"] = stats.get("ripup_ok", 0) + _nrip2
            if verbose:
                print("  [RIPUP] 第二轮 (其余网之后): 尝试 %d 个失败网 ⇒ 重布成功 %d 个"
                      % (len(_failed2), _nrip2))
            stats["failed"] = [n for n in set(stats["failed"])
                               if not (stats["nets"].get(n) or {}).get("ok")]
    # ★★2026-11-05 07:05 **中途存盘前先 commit** (同上: 不 commit ⇒ 存出来是空骨架)
    try:
        _n2 = r.commit(board)
        print("  [SAVE] 阶段性 commit: %d 个图元 (其余网后)" % _n2)
    except Exception as e:
        print("  ⚠️ 阶段性 commit 失败: %s" % e)
    _save_board_progress(board, "其余网后")
    if verbose and r.fail_reasons:
        nf = sum(r.fail_reasons.values())
        nb = sum(r.fail_budget.values())
        print("  [FAIL] 布不动的脚 %d 个 (其中 **A* 预算耗尽** %d 个 / 真被堵死 %d 个)"
              % (nf, nb, nf - nb))
        top = sorted(r.fail_reasons.items(), key=lambda kv: -kv[1])[:10]
        for (nn, cnt) in top:
            print("         %-24s %d 脚 (预算耗尽 %d)"
                  % (nn, cnt, r.fail_budget.get(nn, 0)))
        try:
            import json as _json
            _sd = os.path.dirname(os.path.abspath(__file__))
            # ★★2026-11-05 14:12 **按臂分文件** (★原来只有全局一个 ⇒ 并行臂互相覆盖 ⇒ 看完就没了)
            #   ⇒ ★**臂名从 PCB_OUT 取** ⇒ 落盘名 = `_fail_detail_<臂名>.json`
            _po = os.environ.get("PCB_OUT", "") or ""
            _arm = ""
            if _po:
                _arm = "_" + os.path.splitext(os.path.basename(_po))[0].replace(".", "_")
            for _fn in ("_fail_detail%s.json" % _arm, "_fail_detail.json"):
                try:
                    with open(os.path.join(_sd, _fn), "w") as f:
                        _json.dump(r.fail_detail, f, ensure_ascii=False, indent=1)
                except Exception:
                    pass
        except Exception:
            pass

    # ---------- 5) GND 下拉过孔 (焊盘 → 短走线 → 通孔 → L2/L6 平面)
    # ★★2026-11-05 10:25 **可选: GND 先布** (★默认关 ⇒ 不影响在跑的 v27)
    #   ★**理由**: GND 下拉排在信号/电源之后 ⇒ 焊盘周围的好位置被占光
    #     ⇒ 实测 25 个 GND 焊盘无铜 ⇒ unconnected 里 GND 占 50
    if GND_FIRST:
        # ★★已经先布过 (见上) ⇒ ★**不许再跑一遍** (⇒ 同点两个过孔 ⇒ DRC holes_co_located)
        ok, fail = stats.get("gnd_first", {}).get("drops", 0), stats.get("gnd_first", {}).get("fail", 0)
        if verbose:
            print("  [GND ] 已先布 ⇒ 跳过第二次下拉 (%d 成功 / %d 失败)" % (ok, fail))
    else:
        ok, fail = r.route_gnd_drops("GND")
        if verbose:
            print("  [GND ] 下拉过孔 %d 成功 / %d 失败  (失败原因 %s)"
                  % (ok, fail, getattr(r, "gnd_fail_why", {})))
    stats["gnd"] = {"drops": ok, "fail": fail}

    # ---------- 6) 落板 + 填平面
    # ★★2026-11-04 23:55 **先做几何后处理, 再落板** ——
    #   路由器的"出脚直道 → 栅格路径"衔接处会留下退化图元 (零长段 / 悬空短段)
    #   ⇒ ★**落盘前清掉** ⇒ DRC 归零 (只改几何, 不改板子的设计规则)
    n_zero, n_dang, n_via_drop = r.cleanup_geometry(verbose=verbose)
    # ★★2026-11-05 11:00 **把"预算升级救回来的网数"打进统计** (★看这刀有没有用)
    stats["budget_rescued"] = getattr(r, "fail_budget_rescued", 0)
    if verbose:
        print("  [BUDGET] 预算升级重试救回 %d 个脚" % stats["budget_rescued"])
    stats["clean_zero"] = n_zero
    stats["clean_dangling"] = n_dang
    stats["clean_via"] = n_via_drop
    n_new = r.commit(board)
    stats["tracks"] = len(r.tracks)
    stats["vias"] = len(r.vias)
    stats["edge_viol"] = getattr(r, "edge_viol", 0)
    stats["new_items"] = n_new
    # ★★2026-11-05 07:20 **落板自检: 板上真实图元数 vs 内存里的数必须一致**
    #   ⇒ 这是"阶段性 commit + cleanup"回归的**直接判据** (同事给的)
    #   ⇒ 旧流程板: 零长段=0 且 板上段数 == [SUM]段数 ⇒ ★**对不上就说明回归了**
    try:
        _bt = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T)
        _bv = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
        stats["board_tracks"] = _bt
        stats["board_vias"] = _bv
        if _bt != len(r.tracks) or _bv != len(r.vias):
            print("  ❌ ★**落板自检不一致**: 板上 %d 段/%d 孔 vs 内存 %d 段/%d 孔 (差 %+d 段) ⇒ 记账/删除有 bug"
                  % (_bt, _bv, len(r.tracks), len(r.vias), _bt - len(r.tracks)))
        else:
            print("  ✅ 落板自检: 板上 %d 段 / %d 孔 (与内存一致)" % (_bt, _bv))
    except Exception as e:
        print("  ⚠️ 落板自检失败: %s" % e)
    for z in board.Zones():
        try:
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        except Exception:
            pass
    _fill_zones(board)
    # ★seconds 必须在用之前算 (上一版这里先读后算 ⇒ KeyError ⇒ 整个 route_board 抛出)
    stats["seconds"] = round(time.time() - t0, 1)
    if verbose:
        print("  [SUM ] 走线 %d 段 / 过孔 %d 个 / 板边净距不足 %d 处 / 用时 %.0fs"
              % (len(r.tracks), len(r.vias), stats["edge_viol"], stats["seconds"]))
    return stats


# ------------------------------------------------------------------ 自检
def _selftest():
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(6)
    r = GridRouter(b)
    print("  网格: %dx%d 格 @ %.2fmm  信号层=%s" %
          (r.W, r.H, r.g, [LNAME[i] for i in ROUTE_LAYERS]))
    print("  ✅ gen_pcb_routing 自检通过 (模块可加载)")


if __name__ == "__main__":
    _selftest()
