#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_e1_e2_e3.py —— 采纳 hw-lead ISS-144 实测, 更正三处硬伤 (E1 空仓 / E2 I2C 地址 / E3 RK3572 DTS 公开)

E1 ★`opensource206/UC788_AR0234_SENSOR_TO_RK3588` 实测是**空仓** (只有 LICENSE 35149B + README 82B, size=14KB) ⇒
   我 19:20 那版规格与 `HW/OPEN_SOURCE_AVAILABILITY.md` 里"★RK3588 同族 bringup 最贴近"的断言**不成立** ⇒ 更正。
E2 ★AR0234CS 的 I2C 地址 = **0x10** (`ar0234@10 { compatible = "onnn,ar0234cs"; reg = <0x10>; }`, 实拉 RPi overlay 核过)
   ⇒ 我 19:20 那版写的 0x36 (抄了网表里给 OV04C10 的旧注释) **错** ⇒ 网表注释也要改。
E3 ★`rk3572.dtsi` 在 **rockchip-linux/kernel `develop-6.12` 分支公开** (实测 200, 文件头为 Rockchip copyright; 6.1/6.6 = 404)
   ⇒ TBD-01 虽仍缺"球号", 但**逻辑拓扑/节点名/ISP 链路/regulator phandle 全有公开来源** ⇒ L1 网上找能覆盖大部分。
"""
import os
import re
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

FIX_NOTE = ("★**2026-11-02 19:5x 采纳 hw-lead 实测订正三处 (main 复核过)**: "
            "**E1** `opensource206/UC788_AR0234_SENSOR_TO_RK3588` 实测是**空仓** (LICENSE 35149B + README 82B, size=14KB) ⇒ ★**\"RK3588 同族 bringup 最贴近\"这个断言不成立** —— "
            "真正能抄的是 RPi 版 (ar0234.c 42761B, GPL-2.0) + Jetson 版 (`ar0234_mode_tbls.h` 5915B = 最干净复用资产), 骨架从 Rockchip BSP `ov02b10.c` 抄; "
            "**E2** ★**AR0234CS 的 I2C 地址 = 0x10** (实拉 RPi overlay: `ar0234@10 { compatible = \"onnn,ar0234cs\"; reg = <0x10>; }`) ⇒ ★**我 19:20 那版写的 0x36 是错的** (抄了网表里 OV04C10 的旧注释) ⇒ 网表注释一并改; "
            "**E3** ★**`rk3572.dtsi` 在 rockchip-linux/kernel `develop-6.12` 分支公开** (实测 200, 文件头 Rockchip copyright; 6.1/6.6=404) ⇒ TBD-01 虽仍缺球号, 但**逻辑拓扑/节点名/ISP 链路/regulator phandle 全有公开来源** (L1 网上找能覆盖大部分)。")

# ══════ ① 网表注释: sensor 0x36 → 正确地址 ══════
GEN = f'{PROJ}/state/gen_netlist.py'
s = open(GEN, encoding='utf-8').read()
old = '"WSON-2 2×2mm); I2C_A 从设备地址 0x48, 与 sensor 0x36 / 桥接 0x50 / 充电 IC 0x12 / "'
new = ('"WSON-2 2×2mm); I2C_A 从设备地址 0x48, ★**11-02 19:5x 订正**: sensor 地址随换料变 —— '
       'IMX415 = **0x1a** / AR0234CS = **0x10** (实拉 RPi overlay 核过; ★**旧注释写的 0x36 是 OV04C10 的, 已作废**) / '
       '桥接 0x50 / 充电 IC 0x12 / "')
assert old in s, '网表 I2C 注释没找到'
s = s.replace(old, new, 1)
open(GEN, 'w', encoding='utf-8').write(s)
print('[1] gen_netlist.py: I2C 注释 0x36 → (IMX415 0x1a / AR0234CS 0x10)')

# ══════ ② OPEN_SOURCE_AVAILABILITY.md: E1 更正 + 补 E2/E3 ══════
OS = f'{PROJ}/HW/OPEN_SOURCE_AVAILABILITY.md'
t = open(OS, encoding='utf-8').read()
old1 = "· ★`opensource206/UC788_AR0234_SENSOR_TO_RK3588` (★**RK3588 同族 bringup**) ⇒ ★**最贴近 (同 ISP3 代, 同 SoC 家族)**"
new1 = ("· ★`opensource206/UC788_AR0234_SENSOR_TO_RK3588` ⇒ ★★**2026-11-02 19:5x 实测订正: 这是个「空仓」** (只有 LICENSE 35149B + README **82B**, size=14KB) "
        "⇒ ★**不能抄, \"RK3588 同族 bringup 最贴近\"这个判断不成立**; ★**真正能抄的是上面两条 GPL-2.0 的** (RPi 版完整驱动 + Jetson 版 `ar0234_mode_tbls.h`; 骨架从 Rockchip BSP `ov02b10.c` 抄)")
if old1 in t:
    t = t.replace(old1, new1, 1)
    print('[2] OPEN_SOURCE_AVAILABILITY.md: E1 空仓订正已写')
else:
    print('[2] ⚠️ 没找到 E1 那句, 跳过 (可能已被 hw-lead 改过)')
if 'AR0234CS 的 I2C 地址' not in t:
    t = t.rstrip() + ("\n\n---\n\n"
      "### ★★2026-11-02 19:5x 实测补记 (hw-lead ISS-144 交卷, main 复核过)\n"
      "| 项 | 结论 | 证据 |\n|---|---|---|\n"
      "| ★**E1** | `opensource206/UC788_AR0234_SENSOR_TO_RK3588` = **空仓** (LICENSE 35149B + README 82B) ⇒ 不能抄 | GitHub API 实拉 |\n"
      "| ★**E2** | ★**AR0234CS 的 I2C 地址 = 0x10** (★**不是 0x36** —— 0x36 是 OV04C10 的旧注释) | RPi overlay 实拉: `ar0234@10 { compatible = \"onnn,ar0234cs\"; reg = <0x10>; }` |\n"
      "| ★**E3** | ★**`rk3572.dtsi` 在 `rockchip-linux/kernel` 的 `develop-6.12` 分支公开** (6.1/6.6 = 404) ⇒ TBD-01 缺的只是\"球号\", 逻辑拓扑/节点名/ISP 链路/regulator phandle 全有公开来源 | raw.githubusercontent 实拉 (文件头为 Rockchip copyright) |\n"
      "| ★**E4** | ISP3 支持 **GRBG** (media-ctl 格式要写 `SRGGB10_1X10`) | `isp/common.h` `RAW_GRBG` + `isp_params_v3x.c` 映射 |\n"
      "| ★**E5** | AR0234CS 驱动移植工作量 **≈7 人日** (不是 5.5) —— 涨点: CCI→regmap 重写 24 处 / 增益 0x30BA 按 pixclk 分档 / rkisp3 format 改 4 处 | hw-lead ISS-144 规格 §2 |\n")
    print('[2] OPEN_SOURCE_AVAILABILITY.md: E1~E5 补记已写')
open(OS, 'w', encoding='utf-8').write(t)

# ══════ ③ issue_log: ISS-144 以 hw-lead 版为准 + 记录订正 ══════
IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}
i = by['ISS-144']
i['fix_ref'] = ('HW/AR0234CS_RK3572_PORT_SPEC.md (★**hw-lead 19:5x 交卷版, 250 行/6 章, 6 仓库逐个实拉验证** —— 以此版为准) · '
                 'HW/OPEN_SOURCE_AVAILABILITY.md §E1~E5 实测补记 · HW/DEMO_BOARD_HW_DECISION.md')
i['note'] = (i.get('note') or '') + " " + FIX_NOTE + (
    " ★**工作量更正: 5.5 → ≈7 人日** (C1~C6; tuning C7 另计 1~2 人周) ⇒ ★**路径A 比路径B 晚 15~21 人天 (≈3~4 周)**。"
    " ★**验收门槛更正 (重要)**: ★**A1~A3 (enumerate / media-ctl / 抓 60 帧 RAW) 不需要 tuning 可独立过 ⇒ demo 门槛应定在 A1~A3, 别把 A4/A5 (卡 C7) 当门槛**。"
    " ★**路径判断**: 路径B 能把\"出画面\"从 AR0234CS 身上挪开约 5~10 天, ★**但买的是时间不是结论** (IMX415/OV02B10 的指标一个都不满足 AR0234CS) ⇒ ★**整机阶段仍要回到 AR0234CS**; ★**真瓶颈始终是面板 init code** (与 sw-lead 判断一致)。"
    " ★**规格里 4 条待核是 L4 级 (只有走采购咨询才问得到)**: fine exposure 寄存器 / 完整 pinout 与电源域 / VDD_IO abs max / CRA / 现成 IQ ⇒ 按老板 19:45 阶梯, 它们**排在最后**。")
# ★I2C 地址注释订正登记
if not any(x['id'] == 'ISS-153' for x in iss):
    iss.append({
        'id': 'ISS-153',
        'title': '★★订正: AR0234CS 的 I2C 地址是 0x10 (不是 0x36) + IMX415 是 0x1a ⇒ 网表注释已改, 但要连带核 TMP117/充电IC/光机 地址表',
        'severity': 'medium', 'source_blocker': None, 'source_agent': 'main',
        'desc': ("★2026-11-02 19:5x hw-lead 实测 (main 复核): AR0234CS = **0x10** (RPi overlay 实拉), IMX415 = **0x1a**; "
                  "⇒ ★**网表里 I2C_A 那行注释原写 'sensor 0x36' (那是 OV04C10 的), 已订正** (生成器改了, 网表是生成物)。"
                  "★**但要注意**: 换 sensor 时 **I2C 地址会变** ⇒ ★**每次换 sensor 都要重核整条 I2C_A 总线的地址表** "
                  "(TMP117 0x48 / 充电 IC 0x12 / 光机 0x72 / 桥接 0x50 —— ★**桥接位已随 RK3572 无 DP TX 整条删除**, 实际在用的是 TMP117 + 充电IC + 光机)。"),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-06',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'state/gen_netlist.py (I2C_A 注释) · HW/AR0234CS_RK3572_PORT_SPEC.md §1',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:5x。★**低危但会咬人**: 地址冲突的表征是\"I2C 读不到\"而不是\"编译不过\" ⇒ **每次换 sensor 必须重核地址表**。'),
        'dispatched_at': None,
    })
yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[3] issue_log: ISS-144 订正已记 + 新开 ISS-153')

# ══════ ④ tracker: 更正 (1.55)/(1.56) 里的 RK3588 断言 + 补 E3 ══════
TP = f'{PROJ}/PROJECT_TRACKER.md'
t = open(TP, encoding='utf-8').read()
t = t.replace('+ ★`opensource206/UC788_AR0234_SENSOR_TO_RK3588` 的 **RK3588 同族 bringup**',
              '+ ★**RPi 版 + Jetson 版 (`ar0234_mode_tbls.h`)**', 1)
t = t.replace('+ Jetson Orin 版 + ★**RK3588 同族 bringup `opensource206/UC788_AR0234_SENSOR_TO_RK3588`**) ⇒ ★**RK3588 那份最贴近 (同 ISP3 代, 同 SoC 家族)**',
              '+ Jetson Orin 版 (★**`ar0234_mode_tbls.h` 是最干净的可复用资产**) ⇒ ★★**2026-11-02 19:5x 实测订正: `opensource206/UC788_AR0234_SENSOR_TO_RK3588` 是空仓, 不能抄**', 1)
t = t.replace('| ★**社区公开实现** | ★**0 个仓库** | ★**20 个** (含 GPL-2.0 完整 V4L2 驱动 + DT overlay + ★**RK3588 同族 bringup**) |',
              '| ★**社区公开实现** | ★**0 个仓库** | ★**20 个** (含 GPL-2.0 完整 V4L2 驱动 + DT overlay + Jetson 版 mode_tbls; ★★19:5x 订正: 那个\"RK3588 同族 bringup\"仓实测是**空仓**) |', 1)
t = t.rstrip() + ("\n\n### ★★2026-11-02 19:5x 三条实测订正 (hw-lead ISS-144 交卷, main 复核过)\n"
  "| 代号 | 订正 | 影响 |\n|---|---|---|\n"
  "| **E1** | ★`opensource206/UC788_AR0234_SENSOR_TO_RK3588` = **空仓** (LICENSE + README 82B) ⇒ 真正能抄的是 **RPi 版 (ar0234.c 42KB, GPL-2.0) + Jetson 版 (`ar0234_mode_tbls.h`)**, 骨架从 Rockchip BSP `ov02b10.c` 抄 | ★**\"最贴近的移植起点\"判断作废**; 移植路径不变但工作量 ↑ |\n"
  "| **E2** | ★**AR0234CS 的 I2C 地址 = 0x10** (不是 0x36 —— 0x36 是 OV04C10 的旧注释); IMX415 = **0x1a** | ★**网表注释已订正** (ISS-153); ★**每次换 sensor 要重核整条 I2C 地址表** |\n"
  "| **E3** | ★**`rk3572.dtsi` 在 `rockchip-linux/kernel` 的 `develop-6.12` 分支公开** (6.1/6.6 = 404) | ★**TBD-01 只缺\"球号\"**, 逻辑拓扑/节点名/ISP 链路/regulator phandle 全有公开来源 ⇒ **L1 网上找能覆盖大部分**; demo 用 SOM 本就绕开了它 |\n")
open(TP, 'w', encoding='utf-8').write(t)
print('[4] tracker: E1/E2/E3 订正已写')

# ══════ ⑤ 分片: 工作量与地址 fact ══════
def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("sensor_port_effort_ar0234cs", "7人日+1~2人周",
        "★ISS-144 规格 (hw-lead 19:5x 交卷版, main 复核): AR0234CS→RK3572 rkisp3 **能出 RAW ≈7 人日** (C1~C6; ★比初估 5.5 多 1.5 天: CCI→regmap 重写 24 处 / 增益 0x30BA 按 pixclk 分档 / rkisp3 format 改 4 处), tuning 另计 1~2 人周 ⇒ ★**路径A 比路径B 晚 15~21 人天 (≈3~4 周)**。★**验收门槛 = A1~A3 (enumerate/media-ctl/抓 60 帧 RAW), 这三条不需要 tuning 可独立过** ⇒ 别把 A4/A5 当 demo 门槛。",
        "HW/AR0234CS_RK3572_PORT_SPEC.md §2/§4")
    add("sensor_i2c_addr_map", "IMX415=0x1a/AR0234CS=0x10",
        "★**19:5x 实测订正**: AR0234CS = **0x10** (RPi overlay 实拉: ar0234@10, compatible \"onnn,ar0234cs\"), IMX415 = **0x1a** ⇒ ★**网表原注释 'sensor 0x36' 是 OV04C10 的, 已改** ⇒ ★**每次换 sensor 必须重核整条 I2C_A 地址表** (TMP117 0x48 / 充电IC 0x12 / 光机 0x72; 桥接位 0x50 已随 RK3572 无 DP TX 删除)。",
        "ISS-153 + HW/AR0234CS_RK3572_PORT_SPEC.md §1")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("hw-lead", mutate)
print('[5] hw.yaml 已更新 (2 claims)')
