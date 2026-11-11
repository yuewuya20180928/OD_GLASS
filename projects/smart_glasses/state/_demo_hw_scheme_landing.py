#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""demo_hw_scheme_landing.py —— 硬件方案定案落 tracker + issue_log + 分片"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
# ★★★**ISS-186 口径钉死 (2026-11-11, 项目总工 main)** ★★★
# ★**本脚本是【落账器】⇒ 重跑它 = 把它写的字串灌回 PROJECT_TRACKER.md**
# ⇒ ★**所以这里的每一个 payload 数字都必须是对的** ⇒ ★**原来写 373 Mbps (偏小 8.0×)
#   会把 ISS-186 订正过的 5 处全部重新灌回错数** ⇒ ★**已订正为 2986**
# ★**口径**: payload = 宽×高×24×60 (RGB888 24bpp) ⇒ 1920×1080@60 = 2985.98 Mbps ≈ 2986 Mbps ⇒ 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径 (TX 物理下限 7.776ms = 2986/60/6400) ⇒ ★**ISS-186 订正**
# ★**不许重跑本脚本**: 它是 2026-11-02 的一次性落账器 (无幂等护栏) ⇒ 重跑会重复追加

sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

# ───────────── tracker ─────────────
P = f'{PROJ}/PROJECT_TRACKER.md'
s = open(P, encoding='utf-8').read()

# 变量 44 追加具体决定
anchor = "| **44** | ★**demo 硬件形态 (已定, 不是待拍板)**"
i = s.index(anchor)
end = s.index("\n", i)
line44 = s[i:end]
add44 = (" | ★★**2026-11-02 19:4x 方案定案** (`HW/DEMO_BOARD_HW_DECISION.md`): "
 "①**主控 = RK3572 核心板 (SOM) 焊/插在主板上** ⇒ 主板**不碰 SoC 球位图** (★**TBD-01 对 demo 板不再是阻塞**) "
 "②**sensor 模组 (IMX415) ↔ 主板 = 板内 FPC 座 0.5mm/24p, 2-lane CSI (MIPI 收端 D2/D3 预留 DNP, 原网表即此形态)** "
 "③**屏幕模组 (视涯 0.49\" + 驱动板) ↔ 主板 = 板内 FPC 座 0.5mm/20p, 4-lane DSI (2986Mbps 负载, demo 不需要 DSC)** "
 "④**I2C 分离**: camera=I2C_A, display=I2C_B ⑤**demo 直接 USB-C 5V 供电, 不装电池/不上充电链** (充电链属整机阶段的镜框充电板) "
 "⑥**Step1 = 用公开 SBC (Forlinx OK3572-C 等) 当载体, 零 PCB 先跑链路; Step2 = 自研主板承接产品形态** "
 "⑦**厂家专属信息全部写进采购硬判据** (camera 模组随货给 1080p60 寄存器表/AC 耦合是否内置/供电; 屏模组随货给 init code + DSI 时序 + DDC 地址) ⇒ ★**不用发任何问询函**")
s = s[:end] + add44 + s[end:]

anchor2 = "#### (1.60) ★★★★ 2026-11-02 19:29: demo 判据收敛成两条"
sec = """#### (1.61) ★★★★ 2026-11-02 19:4x: **demo 硬件方案定案** (老板 19:35「最高优先级是敲定硬件方案」)

> **落账**: ★**`HW/DEMO_BOARD_HW_DECISION.md`** (新建, 项目总工定案) · 网表已同步 (`state/gen_netlist.py`: HINGE 只剩充电链两个连接器, **CONN_CAM / CONN_LIGHT 改 MAIN_PCB = 板内 FPC 座**) · `state/check_netlist.py` 判据同步 (14 条: 「跨铰链 4 个连接器标 HINGE」→「**camera/display FPC 座在主板 + 充电链连接器仍属铰链**」, ★**判据强度不放松, 是换判据不是删判据**) · §0 变量 44 补具体决定 · ISS-149 fixed / ISS-150 open

**★ 老板问的三件事, 直接给答案**:
| 问题 | ★**决定** | 关键依据 |
|---|---|---|
| **sensor 和主板怎么连** | ★**sensor 模组 (IMX415+镜头+支架) 带 0.5mm/24p FPC 出线 ↔ 主板板内 FPC 座**; **2-lane CSI** (1080p60 RAW10 = 1.244Gbps ⇒ 2 lane @700Mbps/lane 够) + MCLK + SCCB + RESET + 3 轨电源 + GND; AC 耦合**优先模组内置**(写进采购判据), 主板侧位保留 | 原网表**本来就是 2-lane 必装 + D2/D3 预留 DNP** ⇒ 决策与网表一致, 无需改; IMX415 数据来源 10/10 (零移植零自研 tuning) |
| **主控芯片在主板上怎么放** | ★**不放裸芯片 ⇒ 用 RK3572 核心板 (SOM) 焊/插在主板上**; 布局: SOM 居中偏一侧、散热面朝下导热垫、**camera/display 两个 FPC 座放在 SOM 同侧或相邻侧** ⇒ MIPI 差分走线短直 ≤60mm、不跨分割、100Ω 差分; ★**主板因此完全绕开 SoC 球位图 ⇒ TBD-01 对 demo 板不再是阻塞** | RK3572 球位图官方未到; ★**RK357x 核心板/载板公开有货且公开原理图** (Forlinx OK3572-C / ArmSoM RK3576 / DFRobot) ⇒ 走开源渠道, 不用发问询函 |
| **屏幕模组和主板怎么连** | ★**视涯 0.49" 1920×1080 面板 + 驱动板 = 一个屏模组, 带 0.5mm/20p FPC 出线 ↔ 主板板内 FPC 座**; **4-lane DSI** (1920×1080@60 RGB888 ≈ 2986Mbps ⇒ 4-lane 绰绰有余, **demo 不需要 DSC**) + DDC + 3.3V/5V + EN + GND; ★**init code + DSI 时序 + DDC 地址 = 采购硬判据 (随货必须给) ⇒ 主板侧只需加一个 panel 节点 (公开框架) ⇒ 不用发问询函** | 带宽账; 老板 19:25③ + 规则④ |

**★ 主板最小集 (demo)**: SOM + USB-C 5V 输入 + 3.3V + 三路 sensor/panel LDO + **camera FPC 座 (0.5mm 24p)** + **display FPC 座 (0.5mm 20p)** + I2C_A/I2C_B + 调试 (USB-UART + JTAG) + BOOT/RESET + LED + (DNP) 充电位。

**★ 两步走 (不冲突)**: ★**Step1 = 用公开 SBC 当载体, 零 PCB, 本周就能跑软件链路** (依赖 ISS-147 构建环境 + ISS-145 规格) ⇒ ★**Step2 = 自研主板 (一块板 + 两模组 + FPC) 承接产品形态** ⇒ ★**"敲定硬件方案"与"尽快出画面"不冲突**。

**★ 画板前必须闭合 3 件 (都不许发问询函)**: ①IMX415 电源轨与 1080p60 模式 (公开 datasheet + BSP 驱动 + 模组随货寄存器表 ⇒ ISS-148) ②RK3572 SOM 的**引脚定义** (模组厂公开规格/原理图; 拿不到就换一家模组厂, **不换主控**) ③面板 init code + DSI 时序 (采购硬判据)。

"""
s = s.replace(anchor2, sec + anchor2, 1)
open(P, 'w', encoding='utf-8').write(s)
print('[tracker] 变量 44 补充 + (1.61) 定案节 已写入')

# ───────────── issue_log ─────────────
IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-149']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'hw-lead'
i['fix_ref'] = ('HW/DEMO_BOARD_HW_DECISION.md (定案 + 三个问题的答案 + 两块 FPC 针位总表 + 采购硬判据) · '
                'state/gen_netlist.py (HINGE 只剩 J_CHG/CONN_USB; CONN_CAM/CONN_LIGHT → MAIN_PCB) · '
                'state/check_netlist.py (14 条判据同步: camera/display 在主板 + 充电链仍铰链)')
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:4x 项目总工已定案并落网表** (老板 19:35「最高优先级是敲定硬件方案」) ⇒ 三个问题都有答案: "
    "①sensor 模组 ↔ 主板 = **板内 FPC 座 0.5mm/24p + 2-lane CSI** (原网表即 2-lane 必装 + D2/D3 预留 ⇒ 无需改); "
    "②**主控用 RK3572 核心板 (SOM) 焊/插主板** ⇒ 主板不碰 SoC 球位图 ⇒ ★**TBD-01 对 demo 板不再阻塞**; "
    "③屏幕模组 (视涯 0.49\" + 驱动板) ↔ 主板 = **板内 FPC 座 0.5mm/20p + 4-lane DSI** (2986Mbps ⇒ 不需 DSC), "
    "**init code/时序 = 采购硬判据** ⇒ 不用发问询函。"
    "★**网表已同步并全绿**: gen_netlist / gen_kicad_net / gen_netlist_pins / gen_bom rc=0; check_netlist 31 条全过 (14 条换成新口径); check_kicad_net 5 条全过; gate_check rc=0。"
    "★**留给 Step2 的尾巴**: FPC 具体料号/针数最终确认 (现网表仍用 40p/16p 旧针位, 多余脚标 NC/预留) + 三条 sensor 轨按 IMX415 重核 (ISS-150) + SOM 引脚定义来源 (公开渠道)。")

i = by['ISS-150']
i['note'] = (i.get('note') or '') + (
    " ★**19:4x 补充**: 电源轨重核的依据 = `HW/DEMO_BOARD_HW_DECISION.md` §1 (IMX415 三轨: 数字/IO/模拟, 具体电压以公开 datasheet 为准 ⇒ 等 ISS-148 的 facts) + "
    "★**2-lane 不用改** (原网表已 2-lane 必装) ⇒ ★**本单剩两件事**: ①三条轨按 IMX415 重核 (改 `HW/SCHEMATIC_V1_SPEC.json` 的 power_rails = 真源) "
    "②1080p60 输出模式定案 (sensor 侧窗口化 vs ISP 侧裁) + I2C 上拉电压按各自 IO 轨。")

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[issue_log] ISS-149 fixed / ISS-150 note 更新')

# ───────────── 分片 ─────────────
def mutate(d):
    arts = d.setdefault("artifacts", [])
    for a in arts:
        if a.get("path") == "HW/DEMO_BOARD_HW_DECISION.md":
            a.update({"summary": "demo 板硬件方案定案 (项目总工, 19:4x): ①sensor 模组↔主板=板内 FPC 0.5mm/24p + 2-lane CSI ②主控=RK3572 核心板(SOM) 焊主板 ⇒ 绕开 SoC 球位图(TBD-01 不再阻塞) ③屏模组↔主板=板内 FPC 0.5mm/20p + 4-lane DSI + init code 走采购硬判据; 含两块 FPC 针位总表 + 主板最小集 + 网表改动 N1~N7 + 画板前闭合 3 件事 + Step1 用公开 SBC 零 PCB 先跑", "updated_at": "2026-11-02", "version": "1.0"})
            break
    else:
        arts.append({"path": "HW/DEMO_BOARD_HW_DECISION.md", "kind": "spec", "version": "1.0", "updated_at": "2026-11-02",
                     "summary": "demo 板硬件方案定案: 三问三答 (sensor/主板 FPC 24p 2-lane · 主控用 RK3572 SOM · 屏模组 FPC 20p 4-lane) + 针位总表 + 网表改动 + Step1 公开 SBC 先跑"})
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("demo_board_form", "main+SOM+2FPC",
        "★2026-11-02 19:4x demo 硬件方案定案: 主板一块 = RK3572 核心板(SOM) + camera FPC 座(0.5mm/24p, 2-lane CSI) + display FPC 座(0.5mm/20p, 4-lane DSI) + USB-C 5V 供电(不装电池/不上充电链); ★**camera/display 由 HINGE 改 MAIN_PCB (板内 FPC, 不跨铰链)**; ★**Step1 = 公开 SBC 零 PCB 先跑链路, Step2 = 自研主板**; ★init code/寄存器表 = 采购硬判据 ⇒ 不发问询函。",
        "HW/DEMO_BOARD_HW_DECISION.md + PROJECT_TRACKER.md#(1.61)")
    add("demo_csi_lanes", "2lane",
        "★demo 相机链路 **2-lane** (原网表即 2-lane 必装 + D2/D3 预留 DNP ⇒ 与决策一致无需改): 1080p60 RAW10 = 1.244Gbps ⇒ 2 lane @ ~700Mbps/lane (RK3572 CSI D-PHY 2.5Gbps/lane); FPC 针位目标 0.5mm/24p。",
        "HW/DEMO_BOARD_HW_DECISION.md §1 + §4")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d

update_fragment("hw-lead", mutate)
print('[分片] hw.yaml 已更新 (artifact + 2 claims)')
