#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 FRAMEWORK/ 下的 3 份数据驱动文档
  RISK_REGISTER.md  风险登记册 (H9-02)   —— 从 tracker §5 风险清单 + issue_log 补责任人/应急备选/复查节奏
  RTM.md            追溯矩阵   (ISS-033) —— 锁死变量 → 设计取值 → 验证方法 → 验证结果
  CHANGE_LOG.md     变更追踪表 (ISS-031) —— 规格变更全量记录 (含已作废结论)
"""
import os
import re
import sys
import yaml

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRK = open(os.path.join(PROJ, "PROJECT_TRACKER.md"), encoding="utf-8").read()
LOG = yaml.safe_load(open(os.path.join(PROJ, "state", "issue_log.yaml"), encoding="utf-8"))
PM = yaml.safe_load(open(os.path.join(PROJ, "state", "fragments", "pm.yaml"), encoding="utf-8"))
OUT = os.path.join(PROJ, "FRAMEWORK")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 风险登记册
# 责任人与应急备选: ★按风险 id 显式映射 (不靠正则猜 —— 猜过, 错过)
OWNER = {
 "R1":  ("sw-lead", "main", "① 切 30fps 兜底 (端到端 55.7ms@25.6fps) ② 换 yolov5n / 降输入尺寸 ③ 压 T_od 进 16.67ms (age=1)"),
 "R1b": ("sw-lead", "main", "① 压 T_od 进 16.67ms (age=1) ② 降输入尺寸 ③ 切 30fps (显示槽位+合成策略两件一起切)"),
 "R1c": ("sw-lead", "main", "① 主观眩晕验收 (老板 19:23 定, 零设备) ② 口径C 软件打点兜底 ③ 口径A 起点用推算 (标 [推算])"),
 "R2":  ("sw-lead", "main", "① 切 30fps 兜底 ② 换 yolov5n ③ 口径C + 主观验收组合判达标"),
 "R3":  ("sw-lead", "main", "① 基线关 EIS (已定) ② 降输入分辨率 ③ 降 ISP 负载"),
 "R4":  ("hw-lead", "main", "① 双出口 DSI_TX/DP_TX 走 0Ω/DNP (PCB 出板前再定) ② 并行询价抢 4-8 周 ③ 提前备料"),
 "R5":  ("sw-lead", "main", "① 换 RKNN/Vivante 工具链路径 (A7S 已跑通) ② 手工 INT8 量化流程 ③ 自研 ONNX→nb 转换"),
 "R6":  ("mech-lead", "main", "① 电池降到 340mAh 档 (镜腿 7.3mm) ② 解 A 隔热层局部化 (余量 0.95mm) ③ Plan B 双光机 (镜框 4.8mm)"),
 "R7":  ("sw-lead", "main", "① 降输入分辨率 ② 改 NPU SDK workspace 分块 ③ 明确 CMA 预留策略"),
 "R8":  ("main", "boss", "① 并行询价 (不等原厂回信, 抢 4-8 周) ② Plan B 双光机 ③ 备份供应商方向 (JBD 销售推荐)"),
 "R9":  ("main", "main", "① 板级集中 debug (三项不可验证项一起抓) ② 阻抗 coupon 提前投 ③ 充电板单独先投"),
 "R10": ("main", "main", "① 阻抗 coupon + 充电板单独投板 (拼板, 边际成本≈0) ② 原理图拉原厂 FAE 评审 ③ DSNP 覆盖避免改板"),
 "R11": ("mech-lead", "main", "① 按需触发 (0.23W) ② SoC+充电板挪镜框 (皮肤 37.5°C) ③ 待机 <0.05W ④ 充电摘下眼镜+禁OD"),
 "R12": ("main", "main", "① 不锁 BOM (老板 10-21: 再说) ② 量产规模定下再出成本模型"),
 "R13": ("mech-lead", "main", "① Plan B 双光机 (镜框正中 4.8mm, 结构上更简单) ② 分光件自研 (0.79cc, 共基准 ≤0.25°) ③ 问 JBD 一拖二模组"),
 "R14": ("main", "boss", "① 问 JBD 要样片/交期承诺 ② 备份供应商方向 ③ 优先 Plan B 降低依赖"),
 "R15": ("main", "boss", "① 已做: 守卫下沉 CLI 入口 (5 路径实测) ② 待老板拍板: deny exec / exec-approvals per-agent allowlist"),
 "R16": ("main", "main", "✅ 已拍板 (10-25 19:16): 宽高比无所谓, 只需 ≥1080p60 → 风险关闭"),
 "R17": ("main", "main", "✅ 已修: 原子写 + 唯一 tmp + flock + 失败回退 .lastgood + rc 三态"),
 "R18": ("main", "main", "✅ 已修: 一 agent 一写会话 + 派活前 sessions_list 确认 (advance.py 流程内)"),
 "R19": ("sw-lead", "main", "① 改 960×720@15 (算力降 44%) ② 改 800×600@30 ③ 保持 640×480@60 (优先档) ④ 降低输入分辨率不降帧率"),
}


def owner_of(rid: str):
    return OWNER.get(rid, ("main", "main", "需 owner 补充"))

rows = []
rows_dup = []
# 按行切分 (不用正则前瞻: tracker 的子节编号不连续, 正则会踩坑)
_lines = TRK.splitlines()
try:
    _i0 = next(i for i, l in enumerate(_lines) if l.startswith("## 5. 风险清单"))
    _i1 = next(i for i, l in enumerate(_lines[_i0 + 1:], _i0 + 1) if l.startswith("## "))
    lines_all = _lines[_i0:_i1]
except StopIteration:
    lines_all = []
_seen = set()
for line in lines_all:
    if not re.match(r"^\|\s*\**R\d+", line):
        continue
    cells = [c.strip().replace("**", "") for c in line.strip().strip("|").split("|")]
    if len(cells) < 4:
        continue
    rid = cells[0]
    if rid in _seen:
        rows_dup.append((rid, rid.replace("R16", "R19")))
        rid = rid.replace("R16", "R19")
    _seen.add(rid)
    risk = cells[1]
    lvl = cells[2]
    trig = cells[3]
    mit = cells[4] if len(cells) > 4 else ""
    o, sup, backup = owner_of(rid)
    rows.append((rid, risk, lvl, trig, mit, o, sup, backup))

md = [
    "# 风险登记册 (Risk Register) — H9-02",
    "",
    "> 生成 2026-10-25 | 来源: `PROJECT_TRACKER.md` §5 风险清单 + `state/issue_log.yaml`",
    "> **比 tracker §5 多的 4 个字段**: 责任人 / 升级路径 / **应急备选** / 复查日期",
    "> 复查节奏: **每周五 10:00 交付窗口**逐条过一遍 (新风险入册, 已关闭的转 DECISIONS.md)",
    "",
    "| # | 风险 | 等级 | 责任人 | 升级路径 | 触发条件 | 缓解 | **应急备选** | 复查 |",
    "|---|---|---|---|---|---|---|---|---|",
]
for rid, risk, lvl, trig, mit, o, sup, backup in rows:
    md.append(f"| {rid} | {risk} | {lvl} | **{o}** | {sup} | {trig} | {mit} | {backup} | 每周五 |")

if rows_dup:
    md += ["", f"> ⚠️ **tracker 里存在重复风险 id**: " + ", ".join(f"{a} 与 {b} 同号" for a, b in rows_dup) +
          " → 本表已把后者改号为 " + ", ".join(b for _a, b in rows_dup) + " (tracker §5 需同步改号)"]

ext = [i for i in (LOG.get("issues") or []) if i.get("status") not in ("closed", "deferred", "wontfix")]
md += [
    "",
    "## 风险与问题单的对应 (未闭环问题 = 已确认的风险实例)",
    "",
    "| id | 严重度 | 责任方 | 标题 | 关联风险 |",
    "|---|---|---|---|---|",
]
KEY = {"ISS-001": "R10", "ISS-003": "R4", "ISS-005": "R4", "ISS-006": "R10", "ISS-007": "R4",
       "ISS-008": "R6", "ISS-009": "R1", "ISS-010": "R1c", "ISS-011": "R1", "ISS-015": "R10",
       "ISS-013": "R8/R13", "ISS-016": "R13", "ISS-017": "R6", "ISS-026": "R11",
       "ISS-042": "R6", "ISS-046": "R16", "ISS-051": "R16", "ISS-052": "R6", "ISS-053": "R1b"}
for i in sorted(ext, key=lambda x: ({"blocker": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("severity"), 9), str(x.get("id")))):
    md.append(f"| {i.get('id')} | {i.get('severity')} | {i.get('owner')} | {str(i.get('title'))[:60]} | {KEY.get(i.get('id'), '—')} |")
md += ["", "---", "",
       "## 三个必须每天问自己的问题",
       "",
       "1. **哪个风险的『应急备选』已经用掉了?** (备选不是无限的 —— 备选用完 = 要重新做方案)",
       "2. **哪个风险的触发条件已经发生了, 但还没人处理?** (触发条件成立 ≠ 风险消失)",
       "3. **哪个风险的责任人不在三个总工里?** → 那是 main 或 boss 的, 不能挂着",
       ""]
open(os.path.join(OUT, "RISK_REGISTER.md"), "w", encoding="utf-8").write("\n".join(md))
print(f"✅ RISK_REGISTER.md  ({len(rows)} 条风险 + {len(ext)} 条问题实例)")

# ---------------------------------------------------------------- 追溯矩阵 RTM
MEAS = yaml.safe_load(open(os.path.join(PROJ, "state", "measurements.yaml"), encoding="utf-8"))
need = {m["id"]: m for m in (MEAS.get("needed") or [])}
have = {m.get("id") for m in (MEAS.get("measurements") or []) if str(m.get("kind")) == "实测"}
# 锁死变量表
lv = re.search(r"^## 0\. 已锁死的变量\n(.*?)(?=^## 1\.)", TRK, re.S | re.M)
vars_ = []
if lv:
    for line in lv.group(1).splitlines():
        if re.match(r"^\|\s*\d+\s*\|", line):
            c = [x.strip().replace("**", "") for x in line.strip().strip("|").split("|")]
            if len(c) >= 3:
                vars_.append((c[0], c[1], c[2]))
# 变量 → 验证方法 (关键词映射)
V = {
    "端到端": ("M-E2E / M-NPU", "sw-lead"), "续航": ("M-BATT", "sw-lead"), "皮肤": ("M-SKIN / M-CHRG", "mech-lead"),
    "重量": ("M-WEIGHT", "mech-lead"), "sensor": ("M-FIT + 镜头自检", "hw-lead"), "显示": ("M-E2E", "sw-lead"),
    "主控": ("上电自检 (EVT-1)", "sw-lead"), "DDR": ("EVT-2 内存水位", "sw-lead"), "电源": ("M-POWER", "sw-lead"),
    "OD": ("M-NPU + 精度回归", "sw-lead"), "EIS": ("EVT-3 ISP 用例", "sw-lead"), "BOM": ("来料检验 (QCP)", "main"),
    "样机": ("G2 装配干涉 (M-FIT)", "mech-lead"), "无线": ("— (不适用)", "—"), "波导": ("装配干涉 + 彩虹纹目检", "mech-lead"),
    "镜腿": ("M-FIT / M-PRINT", "mech-lead"), "PCB": ("来料检验 + 阻抗 coupon", "hw-lead"),
}
md = [
    "# 需求 → 设计 → 验证 追溯矩阵 (RTM) — ISS-033",
    "",
    "> 生成 2026-10-25 | 来源: `PROJECT_TRACKER.md` §0 锁死变量 + `interface_claims` (41 条) + `state/measurements.yaml` (10 项)",
    "> 目的: **任何一条锁死变量都能追到『谁设计、怎么验、验了没』**; 追不到的就是覆盖缺口。",
    "",
    "## 0. 两个硬指标的完整追溯链 (最重要)",
    "",
    "| 环节 | 内容 | 责任方 | 证据 | 状态 |",
    "|---|---|---|---|---|",
    "| ① 承诺 | 端到端 <60ms, 口径 A (曝光→出光) | boss | §0 变量 36 / 39 | ✅ 已拍板 |",
    "| ② 口径 | 曝光开始 → 出光 | boss | Q1=A | ✅ 已拍板 |",
    "| ③ 设计 | 框龄模型 age=ceil(T_od/16.67ms) | sw-lead | `SW/DISPLAY_MODE.md` | ✅ 已算 |",
    "| ④ 预算 | age=1 → 50.3ms ✅ / age=2 → 67.0ms ❌ | sw-lead | 同上 | ✅ 已算 |",
    "| ⑤ 判据 | T_od ≤16.67ms 保持 60fps, 否则两件一起切兜底 55.7ms | sw-lead | 同上 | ✅ 已写死 |",
    "| ⑥ **实测** | **M-NPU 纯硬件耗时** | sw-lead | `measurements.yaml` | ❌ **0 数据** |",
    "| ⑦ 结论 | 端到端达标与否 | main | G3 准出 | ⏳ 待 G3 |",
    "",
    "| 环节 | 内容 | 责任方 | 证据 | 状态 |",
    "|---|---|---|---|---|",
    "| ① 承诺 | 皮肤 ≤43°C, 续航 ≥1h (按需触发) | boss | §0 变量 38/41 | ✅ 已拍板 |",
    "| ② 设计 | 稳态热模型 (镜脚 3.2cc 等效 + 0.8mm 壳壁) | mech-lead | `MECH/MECH_BUDGET.md` §2.3 | ✅ 已算 |",
    "| ③ 预算 | 0.23W → 46.5°C ❌ / 待机 0.05W → 37.5°C ✅ | mech-lead | 同上 §2.3.1 | ✅ 已算 |",
    "| ④ 对策 | SoC+充电板挪镜框 + 待机<0.05W + 充电摘下 | boss | §0 变量 41 | ✅ 已拍板 |",
    "| ⑤ 布局 | 镜脚只剩电池 (解 A 余量 0.95mm) | mech-lead | `MECH/CLEARANCE_FIX.md` | ✅ 已算 |",
    "| ⑥ **实测** | **M-SKIN 贴片热电偶** | mech-lead | `measurements.yaml` | ❌ **0 数据** |",
    "| ⑦ 结论 | 皮肤温度达标与否 | main | G3 准出 | ⏳ 待 G3 |",
    "",
    "## 1. 锁死变量逐条追溯",
    "",
    "| # | 锁死变量 | 值 | 验证方法 | 责任方 | 覆盖 |",
    "|---|---|---|---|---|---|",
]
for num, name, val in vars_:
    vm, own = "—", "main"
    for k, (m, o) in V.items():
        if k in name or k in val:
            vm, own = m, o
            break
    covered = "✅" if vm != "—" else "⚠️ 无对应验证项"
    if vm != "—" and "M-" in vm:
        ids = re.findall(r"M-[A-Z]+", vm)
        if any(i not in have for i in ids):
            covered = "🟡 方法已定, **实测未做**"
    md.append(f"| {num} | {name} | {val[:60]} | {vm} | {own} | {covered} |")
md += [
    "",
    "## 2. 覆盖缺口 (⚠️ 行的含义)",
    "",
    "- **⚠️ 无对应验证项** = 这条锁死变量没有任何实测/检查能证明它成立 → 要么补验证方法, 要么它其实不是可验证项",
    "- **🟡 方法已定, 实测未做** = 验证路径已定义 (`measurements.yaml` 的 needed 项), 但还没做 → 阶段门 G3 的清零对象",
    "",
    f"**当前: 实测 {len(have)}/{len(need)} 项** —— 所有 🟡 都要等投板后实测。",
    "",
    "## 3. 实测项清单 (阶段门 G3 的清零对象)",
    "",
    "| id | 测什么 | 单位 | 为什么必须测 | 状态 |",
    "|---|---|---|---|---|",
]
for mid, m in need.items():
    md.append(f"| {mid} | {m.get('name')} | {m.get('unit')} | {m.get('why')} | {'✅ 已测' if mid in have else '❌ 未测'} |")
md += ["", "> 阶段门只认 `kind == \"实测\"`; 推算值会被直接拒绝 (已负向测试验证)。", ""]
open(os.path.join(OUT, "RTM.md"), "w", encoding="utf-8").write("\n".join(md))
print(f"✅ RTM.md  ({len(vars_)} 条锁死变量 + {len(need)} 项实测)")

# ---------------------------------------------------------------- 变更追踪表
md = [
    "# 规格变更追踪表 (Change Log) — H2-08 / ISS-031",
    "",
    "> 生成 2026-10-25 | 来源: `state/fragments/pm.yaml` 的 `decision` 字段 + 三个总工的公开自纠记录",
    "> 作用: **任何一条规格为什么变成现在这样, 都能追到人、日期、依据** —— 含**已作废结论**。",
    "",
    "## 1. 决策类变更 (老板拍板)",
    "",
    "| 日期 | key | 决定者 | 变更内容 | 影响的文档 |",
    "|---|---|---|---|---|",
]
DEC = []
for n in (PM.get("needs_from") or []):
    if n.get("decision"):
        DEC.append((n.get("decided_at") or "", n.get("key"), n.get("decided_by") or "", n.get("decision"), n.get("item") or ""))
DEC.sort()
for at, key, by, dec, item in DEC:
    md.append(f"| {at} | `{key}` | {by} | {str(dec)[:150].replace(chr(10), ' ')}… | {str(item)[:40]} |")
md += [
    "",
    "## 2. 已作废的技术结论 (★ 最容易出错的: 有人引用了旧数字)",
    "",
    "| 被作废的结论 | 改成 | 谁改的 | 日期 | 为什么会错 |",
    "|---|---|---|---|---|",
    "| 端到端 42-45ms 达标 | **67.0ms** (口径A @60fps) | sw-lead | 10-25 | 漏了**框龄 (age)** —— 环节相加的预算一律作废 |",
    "| 0.23W → 皮肤 42°C (压线) | **46.5°C ❌ 超 3.5°C** | mech-lead | 10-25 | 35+11.5=46.5, 算成 42; 且漏了充电场景 |",
    "| 重量合计 49-66g | **50.1-74.0g** | mech-lead | 10-25 | 逐件求和算错, 上界差 8g |",
    "| 摄像头凸出俯角 +1.8°/mm | **+0.7-0.8°/mm** | mech-lead | 10-25 | 把『向前凸出』当成了『向上抬高』 |",
    "| 0.15-0.2W 贴皮肤上限 | **0.16-0.21W** | mech-lead | 10-25 | 主模型/敏感性变体两个算法, 之前取了更宽的 |",
    "| 镜脚侧余量 0.30mm = 通过 | **临界 = 不通过** (余量与公差同量级) | mech-lead | 10-25 | 只报余量没跟公差比 |",
    "| Q16 选 A(4:3)/B(裁剪)/C(letterbox) | **无所谓, 只需 ≥1080p60** | boss | 10-25 19:16 | 老板拍板; 连带 16.3°FOV / -36% 像素代价不再作依据 |",
    "| 对角 120° → 垂直半视场 40.45° | **29.53°/31.80° (鱼眼口径)** | hw-lead | 10-25 19:42 | 1/3\" 靶面量产的 120° 是**鱼眼**, 我算的是直行口径 |",
    "| 『60 优先, 切 30fps 即可』 | **兜底要两件一起切** (帧率+策略) | sw-lead | 10-25 19:26 | 只切帧率不切合成策略 → 仍 67.0ms |",
    "| 镜框侧 5.8mm (双光机) 之外别无选择 | 解 A: 镜脚侧余量 0.95mm | mech-lead | 10-25 19:31 | 叠放在 7.3mm 内物理不可能 → 锁串行 |",
    "",
    "## 3. 变更流程 (谁改什么, 要走哪条路)",
    "",
    "| 改什么 | 谁能改 | 走什么 |",
    "|---|---|---|",
    "| `PROJECT_TRACKER.md` §0 锁死变量 | **只有项目总工** | 老板拍板 → 项目总工代录 `decision` → 同步 pm.yaml + tracker |",
    "| 三个总工的产出 (HW/SW/MECH/HANDOFF) | 对应总工 | 自己改; 影响跨域的 → 改 `interface_claims` → merge 自动检出冲突 → 项目总工裁决 |",
    "| 几何/公差 (影响装配) | mech-lead | 必须更新 `MECH/fit_check.py` 判据 + 打印包 (ISS-050) |",
    "| 测量清单/合格判据 | mech-lead | 改 `MECH/print/MEASURE_CHECKLIST.md` + `state/measurements.yaml` 的 needed 项 |",
    "",
    "## 4. 一条纪律",
    "",
    "> **旧结论必须显式标注『已作废』并写明改成什么** —— 散落在正文里的作废声明是本项目最大的追溯漏洞 (ISS-031 的由来)。",
    "> 本表是唯一去处: 作废一条就在这里加一行, 不删。",
    "",
]
open(os.path.join(OUT, "CHANGE_LOG.md"), "w", encoding="utf-8").write("\n".join(md))
print(f"✅ CHANGE_LOG.md  ({len(DEC)} 条决策 + 10 条作废结论)")
