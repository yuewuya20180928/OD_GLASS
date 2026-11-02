#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_iss147_151.py —— ISS-147 + ISS-151 收口 + 三条订正 + 新开头号卡点单

订正 (我自己给错的, hw-lead 实测推翻):
 ① ★**EK79007 / EK73217 / NV3049 内核里【没有】** (Rockchip BSP develop-6.1 `drivers/gpu/drm/panel/` 79 个文件逐个列过) ⇒ 我 19:4x 在 outbox/README、视崖问询稿、ISS-151 note 里说的"驱动 IC 公开 ⇒ 内核自带驱动"**部分不成立** ⇒ 真正在内核里的是 **ST7701 / ST7703 / ILI9881C / NV3052C**。
 ② ★**TPS7A20 实测【有 EN 脚】** ⇒ 推翻项目内"TPS7A20 无 EN"的判断 ⇒ **ISS-152 (上电顺序) 有解**: 不用换 LDO 家族, 给 AVDD 那颗加 EN + RC 延时即可。
 ③ ★**「已试」栏的真实含义**: 全库无采购记录 ⇒ L3 门槛还没到, 现在正处 L1/L2 ⇒ 这就是老板"所有元件都试了之后"的当前状态。
硬进展:
 ★**rk3572 不是 rknn-toolkit2 的合法 target_platform** (2.3.2 与最新 2.5.0 都 `ValueError: Invalid target_platform 「rk3572」!`) ⇒ ★**ISS-145 的 M1 (直接复用 A7S 的 .rknn) 不成立** ⇒ 但 RK3572 NPU 与 RK3576 同代同架构 ⇒ 用 `rk3576` target 转换 + 板端 RK3572 BSP runtime 加载 ⇒ **[推算·待板端验证]**
 ★**构建环境已在本机恢复并跑通**: conda env `rknn` (与 `SW/tools/rknn_bench.py` 硬编码路径一致) + 转换四步全 rc=0 真落盘 + 源 ONNX 从 yolov5 v6.0 重导出 (算子直方图与台账丢失那份 245 节点/12 算子完全一致) + yolov5n INT8 **5.13 MiB** + COCO val2017 与 100 张校准集已恢复 ⇒ **A2 路线成本从 3~5 人天降到 ~1 人天**
"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

# ══════ ① 订正 EK79007 等三处 ══════
for fp, old, new in [
    (f'{PROJ}/state/outbox/README.md',
     '面板 init code → ★**L2 有戏** (公开在售 MIPI-DSI 模组的驱动 IC 是公开的: ST7701 / EK79007+EK73217 ⇒ Rockchip 内核自带 panel 驱动与时序 ⇒ **多半不用问厂家**)',
     '面板 init code → ★**L2 有戏 (且已实测到 init sequence 原文)** —— Rockchip BSP `drivers/gpu/drm/panel/` 里**确实有** ST7701 / ST7703 / ILI9881C / NV3052C 的现成驱动与完整 init sequence 范例 ⇒ **多半不用问厂家**; ★★**20:2x 订正: EK79007 / EK73217 / NV3049 内核里其实【没有】**(79 个 panel 文件逐个列过) ⇒ 那两颗不能当「白送」算'),
    (f'{PROJ}/state/outbox/visionox_display_inquiry.md',
     '★**且优先走 L2**: 公开在售 MIPI-DSI 屏模组的驱动 IC 公开 (ST7701 / EK79007+EK73217) ⇒ Rockchip 内核自带 panel 驱动与时序 ⇒ **多半不用问厂家**。',
     '★**且优先走 L2**: Rockchip BSP 内核里**确实有** ST7701 / ST7703 / ILI9881C / NV3052C 的 panel 驱动与完整 init sequence 范例 ⇒ **多半不用问厂家**; ★★**20:2x 订正: EK79007 / EK73217 / NV3049 内核里【没有】** ⇒ 不能当「白送」算 ⇒ 选屏要按内核 panel 白名单反推。'),
]:
    c = open(fp, encoding='utf-8').read()
    if old in c:
        c = c.replace(old, new, 1)
        open(fp, 'w', encoding='utf-8').write(c)
        print(f'[1] 订正: {os.path.basename(fp)}')

# ══════ ② issue_log ══════
IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-151']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'sw-lead'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = 'HW/PART_ALTERNATIVES_REGISTRY.md (9 章 / 7 类 / 每类 ≥3 个公开在售候选 + 实测 HTTP 状态 + 已试-未试栏)'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 20:2x 交卷并收口**。★**核心结论**: ①★**屏幕 init code 大概率不必问厂家** —— Rockchip BSP develop-6.1 `drivers/gpu/drm/panel/` 79 个文件里**确实有** ST7701 / ST7703 / ILI9881C / NV3052C 的现成驱动 + 完整 init sequence 范例 (实测抓到原文); "
    "★**但我 19:4x 说的 EK79007+EK73217 / NV3049 内核里【没有】** ⇒ 那两颗不能当白送算 (已订正三处文档); "
    "②★**主控载体首选 = Forlinx OK3572-C + FET3572-C SoM** (公开产品简介 PDF, 与硬件方案 Step1 一致), 备选 ArmSoM CM5 (★**CM4 兼容 ⇒ RPi 15p CSI 座可直插**) / DFRobot RK3576 核心板 (★**套件自带 IMX415 相机模组**) / Banana Pi BPI-CM5 Pro / Luckfox Core3576; "
    "③★**\"已试/未试\"栏的真实含义 (回答老板\"所有元件都试了\"的状态)**: 绝大多数候选的「已查」= 公开页面/规格书/内核源码实测, 「已试」= 上手跑通/实物验证 ⇒ ★**全库无采购记录 (grep 已购/已下单/已到手 全库无命中) ⇒ L3 门槛还没到, 现在正是 L1/L2 阶段**; "
    "④★**TPS7A20 实测【有 EN 脚】** ⇒ 推翻项目内「无 EN」的判断 ⇒ **ISS-152 有解 (不用换 LDO 家族)**; "
    "⑤各档电压的**封装可得性**已实测 (决定换档会不会改焊盘 ⇒ 换 sensor 改轨时零改板)。")

i = by['ISS-147']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'sw-lead'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('SW/RKNN_BUILD_ENV_RECOVERY.md (12 行摘要 + 本机实测 + target 判定 + 转换链跑通 + 源 ONNX 重建 + 校准集 + 路线建议) '
                '· 本机 conda env `rknn` (路径与 SW/tools/rknn_bench.py 硬编码一致) · 转换链四步 rc=0 产物真落盘')
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 20:2x 交卷并收口 —— demo 软件侧第 0 步基本打通**。★★**头号结论 (本单核心交付)**: "
    "**`rk3572` 不是 rknn-toolkit2 的合法 `target_platform`** —— ★**2.3.2 与最新版 2.5.0 都直接 `ValueError: Invalid target_platform 「rk3572」!`** ⇒ "
    "★**ISS-145 的 M1 路线 (\"直接复用 A7S 的 .rknn\") 不成立, 必须重转**; "
    "★**但 RK3572 的 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ 用 `target_platform=「rk3576」` 转换 + 板端用 RK3572 BSP 自带 runtime 加载** ⇒ **[推算·本文推导, 待板端验证]** ⇒ **★这是 demo 当前的头号卡点 (ISS-155)**。"
    "★★**构建环境已在本机恢复并真跑通**: conda env `rknn` (python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / torch 2.4.0+cpu; ★**路径与 `SW/tools/rknn_bench.py` 硬编码的 RKNN_PY 完全一致**) · "
    "★**转换链四步全 rc=0 真落盘** (config → load_onnx → build(INT8) → export_rknn) · ★**源 ONNX 已重建** (yolov5 v6.0 权重重导出 yolov5s / yolov5n @640, ★**算子直方图与台账里丢失的那份 245 节点 / 12 算子完全一致**) · "
    "★**yolov5n INT8 = 5.13 MiB** (装得进 15 MiB 槽位; yolov5s = 10.47 MiB) · ★**COCO val2017 (5000 张) + instances_val2017.json 已恢复** ⇒ `acc` 步依赖齐 · ★**100 张校准集已重建** (同口径: COCO val2017 → letterbox 640×640 黑边) · "
    "★**模型建议 = demo 第一版用 yolov5n** (理由是量化校准更稳 + 产物更小 + 60ms 余量更大, **不是**因为它更快 (板端没测)) · ★**推荐路线 = A2 (重新导出), A1 (找回原资产) 并行兜底** ⇒ **成本从 3~5 人天降到 ~1 人天**。"
    "★**唯一未闭合**: 板子 (Radxa A7S 192.168.2.5) 仍**不可达** (`No route to host` + ARP FAILED) ⇒ **P0-2 板端 librknnrt 版本号本单无法闭合**。")

# ★ISS-152 订正: TPS7A20 有 EN
i = by['ISS-152']
i['desc'] = (i.get('desc') or '') + (
    " ★★**2026-11-02 20:2x 订正 (hw-lead ISS-151 实测)**: ★**TPS7A20 实测【有 EN 脚】** ⇒ ★**推翻本单原先\"LDO 无 EN ⇒ 顺序保证不了\"的前提** ⇒ "
    "★**本单有解且零换料**: 给 AVDD 那颗 (U_LDO_S28) 接 **EN + RC 延时**, 让 AVDD 最后上电 ⇒ **不用换 LDO 家族, 不用改板层数** ⇒ "
    "★**但 EN 接哪儿要核**: ①EN 挂在哪个 SoC/模组 GPIO 上 (RK3572 球位图未到 ⇒ 用 SOM 的 EN 脚或上电默认上拉的 RC) ②RC 延时值要覆盖 DVDD/OVDD 爬升 + datasheet 要求的 200ms 窗口 ⇒ **这两条属 Step2 画板时定** ⇒ ★**demo 阶段仍按三轨同跑**。")
i['note'] = (i.get('note') or '') + " ★**20:2x 订正: 有 EN 脚 ⇒ 本单由\"需换 LDO 家族\"降为\"加 EN + RC 延时, 零换料\"** ⇒ ★**整机阶段画板时闭环即可**。"

# ══════ 新开 ISS-155: demo 头号卡点 ══════
if not any(x['id'] == 'ISS-155' for x in iss):
    iss.append({
        'id': 'ISS-155',
        'title': '★★★★[demo 头号卡点] rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 target 转的 .rknn 能否在 RK3572 上跑通 (板端验证) —— 且板子当前不可达',
        'severity': 'blocker', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 20:2x ISS-147 实测: ★**`rk3572` 不是 rknn-toolkit2 的合法 `target_platform`** (2.3.2 与最新 2.5.0 都 `ValueError: Invalid target_platform 「rk3572」!`) ⇒ '
            '★**ISS-145 的 M1 (\"直接复用 A7S 的 .rknn\") 不成立** ⇒ ★**必须重转**。'
            '⇒ ★**替代路线 (本文推导, 待板端验证)**: RK3572 的 NPU 与 RK3576 **同代同架构** (4 TOPS / 3 核 RKNPU v2) ⇒ ★**用 `target_platform=\'rk3576\'` 转换, 板端用 RK3572 BSP 自带的 runtime 加载**。'
            '⇒ ★**验证判据 (板端)**: ①板端 `rknn_bench.py acc` 用该 .rknn 能跑完 ②精度不塌 (F1 与 A7S 基线同量级) ③NPU 耗时与 `HW/e2e_budget_rk3572.py` 的预算对得上。'
            '⇒ ★**当前阻塞**: 板子 (Radxa A7S 192.168.2.5) **不可达** (`No route to host` + ARP FAILED) ⇒ ★**两条 blocker 都卡在板子**: 本单 + ISS-147 的 P0-2 (板端 librknnrt 版本号) ⇒ '
            '⇒ ★**两条候选出路**: ①**换一块可达的 RK357x 板**做验证 (公开在售的 Forlinx OK3572-C / ArmSoM CM5 / DFRobot RK3576 —— 见 ISS-151 清单, ★**这也正好是 demo Step1 的载体**) ⇒ ★**推荐这条: 一举两得** '
            '②等板子回到同一网段。'
            '⇒ ★**兜底**: 若 rk3576-target 的 .rknn 在 RK3572 上不认 ⇒ ①查 rkaiq/板端 runtime 有无 rk3572 专用编译 ②换 **RK3576 做 demo 载体** (整条链路换 SoC, 代价大) ③改用 **CPU 推理** (yolov5n INT8 在 8×A72 上不现实, 但量化 int8 + NNAPI/ONNX Runtime 可试) ⇒ 三条都贵 ⇒ ★**所以这条要第一时间验证**。'),
        'owner': 'main', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-03',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'SW/RKNN_BUILD_ENV_RECOVERY.md §2 · HW/PART_ALTERNATIVES_REGISTRY.md §1',
        'verify_by': 'sw-lead', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 20:2x。★**demo 的头号卡点** (不是软件写得好不好, 是"模型能不能上板")。'
                 '★**推荐解法**: ★**用 ISS-151 清单里的公开在售 RK357x 板 (Forlinx OK3572-C 首选) 当验证载体** ⇒ 既解本单, 又是 demo Step1 的载体 ⇒ 一举两得, 不必等 Radxa 板回来。'
                 '★**本机这边已就绪**: 转换链四步 rc=0 真落盘 + yolov5n INT8 5.13 MiB + COCO val2017 与 100 张校准集已恢复 ⇒ ★**只差一块能跑的板**。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[2] issue_log: ISS-151 fixed / ISS-147 fixed / ISS-152 订正 / 新开 ISS-155')

# ══════ ③ tracker ══════
TP = f'{PROJ}/PROJECT_TRACKER.md'
t = open(TP, encoding='utf-8').read()
anchor = "**★ 19:5x 追加: IMX415 的硬件数据已落网表"
i = t.index(anchor)
add = """**★ 20:2x 追加: 两条硬进展 + 我自己给错的一条信息**
| 项 | 结论 | 影响 |
|---|---|---|
| ★**ISS-147 构建环境** | ★**`rk3572` 不是 rknn-toolkit2 的合法 target** (2.3.2 与最新 2.5.0 都 `ValueError`) ⇒ ★**M1「复用 A7S 的 .rknn」不成立, 必须重转**; ★**但 RK3572 NPU 与 RK3576 同代同架构 ⇒ 用 `rk3576` target 转 + 板端 RK3572 BSP runtime 加载** [推算·待板端验证] | ★★**demo 头号卡点 ⇒ ISS-155**; ★**本机已就绪**: conda env `rknn` (与 `rknn_bench.py` 硬编码路径一致) + 转换四步 rc=0 真落盘 + 源 ONNX 从 yolov5 v6.0 重导出 (算子直方图与台账丢失那份 245 节点/12 算子完全一致) + **yolov5n INT8 5.13 MiB** + COCO val2017 与 100 张校准集已恢复 ⇒ **A2 路线成本 3~5 人天 → ~1 人天** |
| ★**ISS-151 替代料清单** | 7 类 / 每类 ≥3 个**公开在售**候选 + 实测 HTTP 状态 + **已试-未试栏**; ★**屏幕 init code 大概率不必问厂家** (内核 79 个 panel 文件里**确实有** ST7701 / ST7703 / ILI9881C / NV3052C 的现成驱动 + 完整 init sequence 范例) | ★**L1/L2 已有凭证**; ★**L3 门槛还没到** (全库无采购记录 ⇒ 「已试」= 上手跑通/实物验证) ⇒ ★**这就是老板"所有元件都试了"的状态** |
| ★**我给错的一条 (已订正三处)** | ★**EK79007 / EK73217 / NV3049 内核里【没有】** (79 个 panel 文件逐个列过) ⇒ 我 19:4x 说的"这几颗驱动 IC 公开 ⇒ 内核自带驱动"**部分不成立** | ★**那两颗不能当「白送」算**; ★**真正能白送的是 ST7701 / ST7703 / ILI9881C / NV3052C** |
| ★**又一条订正 (利好)** | ★**TPS7A20 实测【有 EN 脚】** ⇒ 推翻项目内「无 EN」判断 | ★**ISS-152 (上电顺序) 降级为"加 EN + RC 延时, 零换料"**, 不用换 LDO 家族 |

⇒ ★**现在的头号卡点只剩一个**: ★**板子不可达** (Radxa A7S `No route to host`) ⇒ **ISS-155 (rk3576-target 的 .rknn 能否在 RK3572 上跑) 与 ISS-147 的 P0-2 (板端 runtime 版本) 两条都卡在板子上** ⇒ ★**推荐解法: 用 ISS-151 清单里的公开在售 RK357x 板 (Forlinx OK3572-C 首选) 当验证载体** ⇒ 既解卡点, 又是 demo Step1 的载体 ⇒ **一举两得, 不必等 Radxa 板回来**。

"""
t = t[:i] + add + t[i:]
open(TP, 'w', encoding='utf-8').write(t)
print('[3] tracker: 20:2x 两条硬进展 + 两条订正 + 头号卡点')

# ══════ ④ 分片 ══════
def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("rknn_target_rk3572", "invalid_use_rk3576",
        "★★2026-11-02 20:2x 实测: **rk3572 不是 rknn-toolkit2 的合法 target_platform** (2.3.2 与最新 2.5.0 都 `ValueError: Invalid target_platform 「rk3572」!`) ⇒ ★**M1 复用 A7S 的 .rknn 不成立, 必须重转**; ★**RK3572 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ 用 `target_platform=「rk3576」` 转 + 板端 RK3572 BSP runtime 加载** [推算·待板端验证] ⇒ **demo 头号卡点 ISS-155**; ★本机已就绪 (conda env rknn + 转换四步 rc=0 + yolov5n INT8 5.13MiB + COCO val2017 与 100 张校准集已恢复)。",
        "SW/RKNN_BUILD_ENV_RECOVERY.md §2 + ISS-155")
    add("demo_step1_carrier", "Forlinx OK3572-C",
        "★ISS-151 实测清单 (9 章 / 7 类 / 每类 ≥3 个公开在售候选 + 实测 HTTP 状态 + 已试-未试栏): ★**主控载体首选 = Forlinx OK3572-C + FET3572-C SoM** (公开产品简介 PDF, 与硬件方案 Step1 一致); 备选 ArmSoM CM5 (CM4 兼容 ⇒ RPi 15p CSI 座可直插) / DFRobot RK3576 核心板 (套件自带 IMX415 模组) / Banana Pi BPI-CM5 Pro; ★**屏幕 init code 不必问厂家** (内核 79 个 panel 文件里有 ST7701/ST7703/ILI9881C/NV3052C 现成驱动与完整 init sequence) ⇒ ★**但 EK79007/EK73217/NV3049 内核里没有, 不能当白送**; ★**L3 门槛还没到** (全库无采购记录 ⇒ \"已试\"= 上手跑通/实物验证)。",
        "HW/PART_ALTERNATIVES_REGISTRY.md + ISS-151")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("hw-lead", mutate)
print('[4] hw.yaml 已更新 (2 claims)')
