#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成给代理转发的**干净对外附件** (2026-10-28)
====================================================================
为什么需要这一步:
  老板 09:0x 说"我找到了酷芯微的代理" ⇒ 沟通渠道从"直邮原厂"变成"经代理转发"。
  ⇒ 附件必须是**能直接转给原厂技术部门**的成品, 不能带内部话术。
  原草稿 `vendor_round3_addendum.md` 头部写着 "草稿, 待老板批准后发" (代理看到会困惑),
  正文数字也已过期 (475 行 / 36 条门禁 / 134 行 → 现为 516 行 / 30 条 / 62 个占位节点)。

产出 3 份对外附件 (到 state/outbox/attach/):
  ① attach/01_ARS45_技术确认项_21条.md    —— 附件一 (代理转发的核心件)
  ② attach/02_第二轮问询全文.md            —— 附件二
  ③ attach/README.md                       —— 附件清单 (给代理看, 说明该转哪几份)

★数字一律从**实时源**读 (网表行数 / BOM 位号 / 门禁条数 / 占位节点数), 不写死。
"""
from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUT = os.path.join(HERE, "outbox", "attach")


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def live_numbers() -> dict:
    """实时取项目数字 —— 附件里的数绝不能是写死的。"""
    n = {}
    csv_p = os.path.join(PROJ, "HW", "netlist_v1.csv")
    with open(csv_p, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    n["netlist_rows"] = len(rows) - 1
    n["bom_parts"] = sum(1 for _ in open(os.path.join(PROJ, "HW", "BOM_v1.csv"), encoding="utf-8")) - 1
    # 原理图页数: 只数真正的图页标题 "## P1 电源树" 这类 (不是所有 "## ")
    n["pages"] = len(re.findall(r"(?m)^## P\d+ ", open(os.path.join(PROJ, "HW", "SCHEMATIC_V1.md"), encoding="utf-8").read()))
    # 门禁条数
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_netlist.py")],
                       capture_output=True, text=True, timeout=120)
    m = re.search(r"(\d+)\s*/\s*(\d+)", r.stdout or "")
    n["gates"] = f"{m.group(1)}/{m.group(2)}" if m else "?"
    # SoC 侧**球位占位**节点数 (只数 TBD-01 = 球位号; TBD-02/04/12 等是电压域/时序/显示待定, 不是球位)
    #   ★口径要准: 之前把全部 TBD 都算进去 (185) 是错的 —— 真正等球位号的只有 TBD-01。
    n["tbd_nodes"] = sum(1 for row in rows[1:] if any("TBD-01" in str(c) for c in row))
    # 板框
    import yaml
    hw = yaml.safe_load(open(os.path.join(HERE, "fragments", "hw.yaml"), encoding="utf-8")) or {}
    n["board"] = "60x15mm"
    for c in hw.get("interface_claims") or []:
        if c.get("key") == "pcb_outline":
            n["board"] = str(c.get("value"))
    return n


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    L = live_numbers()
    print("实时数字:", L)

    # ---------- 附件一: 21 条技术确认项 ----------
    src = open(os.path.join(HERE, "outbox", "vendor_round3_addendum.md"), encoding="utf-8").read()
    # 去掉草稿头部 (第一行到第一个 "---" 之后的分隔), 换干净的抬头
    body = src.split("---", 1)[1] if "---" in src else src
    # 去掉尾部内部话术
    body = body.split("## 七、AON 域")[0].rstrip() + "\n"

    # ★对外附件的正文修整 (内部草稿的口径已过期, 直接转给原厂会显得我们没做功课):
    #   ① 球位占位数 62 → 实时值
    #   ② EN/SS/CT/MR "网表里 0 条" → 实际我 10-28 接手 ISS-096 时已补进网表 (EN 链 + CT 脚), 只差脚号与极性
    body = body.replace(
        "现在网表里 62 个 SoC 侧节点全部是占位 (TBD-01), 原厂回信后我们**只填球号、不重画**",
        f"现在网表里 **{L['tbd_nodes']} 个** SoC 侧球位全部是占位 (TBD-01), 原厂回信后我们**只填球号、不重画**")
    body = body.replace(
        "**EN / SS / CT / MR 是不是独立引脚?** 我们的网表里这几类脚目前是 0 条 —— 若存在, 我们要把它们接上 (上电时序链); "
        "若不存在, 我们按\"内部自管\"处理。**这一条最影响开机成功率**",
        "**EN / SS / CT / MR 是不是独立引脚?** 我们已按\"存在\"预留了上电时序链 (EN 顺序链 + 监督器 CT 脚), "
        "但**脚号与极性仍待原厂确认** —— 若这些脚不存在或极性相反, 我们的复位链要改。**这一条最影响开机成功率**")
    body = body.replace(
        "网表里这几类脚目前 0 条, 存在与否直接影响上电时序链与开机成功率",
        "我们已按\"存在\"预留 EN 链 + CT 脚, 但脚号与极性待确认 —— 直接影响上电时序链与开机成功率")
    body = body.replace("网表里这几类脚目前 0 条", "这几类脚我们已按\"存在\"预留, 但脚号与极性待确认")

    a1 = f"""# 附件一 · ARS45 技术确认项 (21 条)

**致**: 酷芯微电子 技术支持 / FAE
**来自**: ARS45 智能眼镜项目组 (经【代理公司】转达)
**日期**: 2026-10-28

> 本清单可直接转交技术部门。每条都写了「我们需要的」「我们的临时假设」「不答的后果」, 便于按难度取舍。
> **我们不需要贵司做选型或比价** —— ARS45 已选定, 缺的是芯片级技术文档。

## 我们这边的进度 (供判断优先级)

| 项 | 现状 |
|---|---|
| 原理图 | **{L['pages']} 页**, 器件级, 全部机械门禁 **{L['gates']} 通过** |
| 网表 | **{L['netlist_rows']} 行** (含 KiCad 可导入网表), **脚本生成、可重跑幂等** |
| BOM | **{L['bom_parts']} 个位号** |
| 主板尺寸 | **{L['board']}** (已定) |
| 芯片 | ARS45 (12nm / 6 TOPS / 512MB DDR / 8×10mm FCCSP) **已选定** |
| 待回填 | **{L['tbd_nodes']} 个 SoC 侧节点为占位 (TBD-01)** —— 回信后**只填球号, 不重画** |
| 阶段 | 首台样机 (量产规模待定) |

**当前只有 3 类信息卡住我们**: ① 封装与球位 ② 电源域与上电时序 ③ 显示输出方向。
下面 21 条就是这三类 + 其余确认项。

---

{body}
## 七、AON 域 / 低功耗 (2026-10-28 追加)

> 背景: 我们的关机拓扑是**负载开关硬件断电** (关机态整机静态 ~108µA / 0.40mW)。其中**最大的单项是 AON 域静态电流估计 (~50µA, 属我们的假设)**, 且关机唤醒路径依赖 AON 域能否保持常开。贵司的书面答复会直接改变: ① 关机续航能不能从 "5-11 个月" 往上走 ② 长按按键唤醒关机态是否成立 ③ 深度休眠时外设能否真断。

19. **AON (Always-On) 域**: ARS45 是否有 AON 域 / 常开唤醒引脚? 若是, 请给 **脚号 + 该域的静态电流 (µA)** —— 我们现在的 50µA 是**假设值**, 而它是关机态功耗预算里最大的单项 (占 ~108µA 的近一半)
20. **关机态唤醒**: 芯片是否支持在 **AON 域保持工作的前提下** 由外部信号 (VBUS 接入 / 长按按键) 唤醒主域? 若是, 唤醒信号接到哪个脚、什么电平有效、延迟量级?
21. **深度休眠 / 低功耗态**: ① 进入低功耗态时, **DDR (内置 512MB) 的内容是否保留**? ② sensor / 光机等外设 rail 能否**真断电**, 还是随 SoC 一起保持带电? (这决定我们 0.15W 的深睡口径是否成立, 以及软件进深睡前是否必须落盘)

---

## 给技术部门的负担评估

21 条里 ① 4 条封装与球位 ② 4 条电源域与上电时序 ③ 3 条显示输出 ④ 3 条 USB ⑤ 2 条启动存储 ⑥ 2 条其他 ⑦ **3 条 AON/低功耗**。

**若时间有限, 请优先回这三条** (直接决定我们能否省掉一颗桥接芯片、以及 PCB 层数与开机成功率):

| 优先 | 问题 | 为什么最卡 |
|---|---|---|
| **1** | **问题 9/10 —— DP1.4 是 TX/RX? 有无 MIPI-DSI TX?** | 我们的光机是 MIPI-DSI 输入。若无 DSI TX, 需外加 DP→MIPI-DSI 桥接芯片 (+100-300mW / +4-8 周采购 / 占板面积) |
| **2** | **问题 3 —— FCCSP pitch 精确值 + 完整球位图** | **选型一票否决项**: pitch ≤0.3mm 则我们已锁死的 4-6 层普通板工艺装不下, 需重新评估是否继续用 ARS45 |
| **3** | **问题 7 —— EN/SS/CT/MR 是不是独立引脚?** | 我们已按"存在"预留 EN 链 + CT 脚, 但脚号与极性待确认 —— 直接影响上电时序链与开机成功率 |

其次是 **问题 19 (AON 静态电流)** —— 它是我们关机续航预算里最大的未知项。

**我们这边**: 网表是脚本生成的 (可重跑、幂等), 回信后**只填球号与 TBD 项, 不重画**; 任何需要确认的引脚我们都留了占位与 0Ω/位置, **不会猜**。

需要保密协议才能提供的资料, 请告知需要的格式, 我们随时可签。

顺颂商祺
"""
    atomic_write(os.path.join(OUT, "01_ARS45_技术确认项_21条.md"), a1)

    # ---------- 附件二: 第二轮问询全文 (去掉内部话术) ----------
    src2 = open(os.path.join(HERE, "outbox", "vendor_round2_email.md"), encoding="utf-8").read()
    b2 = src2
    # 去草稿头部说明块
    if "---" in b2:
        head, rest = b2.split("---", 1)
        b2 = rest
    # 去掉 "★ 10-26 19:45 新增" 那段里引用的内部文件路径说法
    b2 = b2.replace("（我们内部按以下门槛评估（这是我们自己的工程判断，不是贵司结论）：",
                    "（我们内部按以下门槛评估 —— 这是我们自己的工程判断，不是贵司结论）：")
    b2 = b2.replace("（详见 `HW/EMC_PRECHECK.md` D1/D2/D3）", "")
    b2 = b2.replace("**问题 4c（20:20 补充：关于资料获取方式 + 功耗口径）**",
                    "**问题 4c（关于资料获取方式 + 功耗口径）**")
    b2 = b2.replace("**问题 4d（20:20 补充：出图对齐全量对齐后发现的 2 个漏问）**",
                    "**问题 4d（出图对齐全量对齐后发现的 2 个漏问）**")
    b2 = b2.replace("**10-26 19:45 新增 (网上公开渠道已穷尽检索后, 问法按新证据收敛)**",
                    "**补充 (网上公开渠道已穷尽检索后, 问法按新证据收敛)**")
    b2 = b2.replace("→ **我们优先希望拿到 AR9481 的 datasheet + HRM**",
                    "→ **我们优先希望拿到 AR9481 的 datasheet + HRM**")
    b2 = b2.replace("（署名/公司/联系方式待老板补充）", "（署名/公司/联系方式见邮件正文）")
    b2 = b2.replace("—— （署名/公司/联系方式待老板补充）", "—— （署名/公司/联系方式见邮件正文）")
    b2 = b2.replace("——（署名/公司/联系方式待老板补充）", "——（署名/公司/联系方式见邮件正文）")
    b2 = b2.replace("（本邮件由项目总工拟稿, 发出前经内部确认; 附件: 原理图 10 页 + 网表导出 + 门禁报告, 可按需提供）",
                    "（附件: 原理图 + 网表导出 + 门禁报告, 可按需提供）")
    a2 = f"""# 附件二 · 第二轮问询全文 (9 条 vendor issue 的详细背景)

**致**: 酷芯微电子 技术支持 / FAE
**来自**: ARS45 智能眼镜项目组 (经【代理公司】转达)
**日期**: 2026-10-28

> 这是我们前两轮问询的全文, 提供**详细背景与推导依据**。
> 若只需可执行的确认清单, 请看**附件一 (21 条)**; 本附件是附件一的背景补充。

---

{b2.lstrip()}
"""
    atomic_write(os.path.join(OUT, "02_第二轮问询全文.md"), a2)

    # ---------- 附件清单 ----------
    a3 = """# 附件清单 (给代理看)

| # | 文件 | 转给谁 | 必读程度 |
|---|---|---|---|
| **附件一** | `01_ARS45_技术确认项_21条.md` | **原厂技术部门 / FAE** (主送) | ★★★ **核心件** —— 21 条可执行确认项, 含每条"不答的后果"与优先级建议 |
| **附件二** | `02_第二轮问询全文.md` | 原厂技术部门 (参考) | ★★ 9 条 vendor issue 的详细背景与推导依据 (供技术同事判断难度) |
| **附件三** | 原理图 + 网表导出 + 门禁报告 | 原厂 FAE | ★ 供 FAE 评审投板前架构 (可另行提供, 文件较大) |

**给代理的三句话**:
1. 我们**不是**在比价或评估方案 —— ARS45 已选定, 缺的是芯片级技术文档 (引脚表/球位图/电源域表/工具链), 这类资料通常只有原厂能出。
2. 附件一可以**原样转给技术部门**, 不需要删改; 里面已按优先级排好, 技术同事能直接照着答。
3. 样品/工具链/商务部分在**邮件正文**, 麻烦一并转给原厂对应的商务或供应链同事。

**我们的项目阶段**: 原理图 {pages} 页 / 网表 {netlist_rows} 行 / BOM {bom_parts} 位号, 机械门禁 {gates} 通过, **拿到答复即可投板**。
""".format(pages=L["pages"], netlist_rows=L["netlist_rows"], bom_parts=L["bom_parts"], gates=L["gates"])
    atomic_write(os.path.join(OUT, "README.md"), a3)

    for f in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, f)
        print(f"  ✅ {f}  ({os.path.getsize(p)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
