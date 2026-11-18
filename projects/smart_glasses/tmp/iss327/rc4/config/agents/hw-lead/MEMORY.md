# MEMORY.md — 硬件总工 (hw-lead) 长期记忆

> 本项目信息真源在共享库: `projects/smart_glasses/PROJECT_TRACKER.md`
> 这个文件只记**本角色自己的**结论/教训/未了事项。

## 角色
🔧 硬件总工 — ARS45 智能眼镜项目
(职责见 `AGENTS.md`)

## 我的工作区
- 产出区: `projects/smart_glasses/HW/`
- 共享库: `projects/smart_glasses/` (软链到 `~/.openclaw/workspace/projects/smart_glasses`)

## 上级
项目总工 = `agent:main:main` (moli)

---

## 2026-10-25 首轮: 硬件模块拆解

**产出**:
- `projects/smart_glasses/HW/HARDWARE_BREAKDOWN.md` (26 模块 + 3 卡点展开)
- `projects/smart_glasses/HANDOFF/2026-10-25_hw-lead_硬件模块拆解.md`

**我自己的结论 (后续开工按这个走)**:

1. **卡点 A (显示接口未确认) 的原理图对策已定**: 光机侧连接器**定死** (MIPI-DSI + I2C + 电源 + RESET), SoC 侧同时留 DSI_TX / DP_TX **双出口**, 用 0Ω/DNP 决定走哪条 → 原理图阶段不锁死任何一条路。
   - 若 ARS45 **既无 DSI TX 也无 DP TX** → 不是加颗桥芯片的事, 是显示链不成立 → 架构级上报。
2. **FCCSP 逃线的真实判据是球间距 (pitch), 不是封装尺寸**: pitch ≥0.4mm → 常规 4-6 层可行 / 0.35mm → 极限 / ≤0.3mm → 必须 HDI, 与"4-6 层"锁死冲突 = 一票否决。**pitch 应写进 SoC 选型条款。**
3. **有无桥接芯片 = 电池容量档位问题, 不只是 BOM 问题**: 无桥 → 340~575mAh; 有桥 → 575~675mAh (1S 3.7V, 整机 0.95~2.0W 推算)。→ 必须尽早给 mech-lead 做空间验证。
4. **新发现的 tracker 漏项**: 启动存储 / 固件分区 (rootfs + yolov5 权重 + ISP/NPU 固件) 从未列入 BOM。无无线 + Q3 未答 → 需要确认 ARS45 是否内置 boot storage。**未擅自加 BOM, 已列交接单。**
5. **建议预留 (1 台样机也值得)**: 电源开关 (硬断电) + 电流采样 (不用拆眼镜就能测功耗曲线) + 1-2 LED + 2 按键焊盘 + 各电源轨测试点。

**我的未了事项 (下次开工先查)**:
- 等 datasheet → 电源域表 / 引脚图 / pitch / 显示 TX 章节
- 等 mech-lead → 镜脚空间预算 → 定桥接芯片放主板 (B1) 还是小板 (B2)
- 等老板 → Q16 宽高比 A/B/C 拍板 / Q3 模型存哪 / Q4 续航口径 / 音频是否做

**纪律提醒**: 本文所有数字均为推算或引用 tracker 推算值, **无一条实测**; 拿不到就标"未确认", 不拿经验值冒充实测。

---
