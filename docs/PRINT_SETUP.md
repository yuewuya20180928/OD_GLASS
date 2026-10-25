# 打印执行卡 (PRINTER_SETUP) — 老板 2026-10-25 19:23 指示

> 老板原话: "打印机跨网段后面再说, **当前先输出打印机能识别的配置文件即可**"
> 所以本包 = **打印机软件直接能认的文件** + **照着做就能出实测值的操作卡**。
> ⚠️ 本机**没有切片器、外网不通** → **G-code 必须在打印机软件里点一次"切片"生成**（这是所有切片器的正常流程）。

---

## 1. 你会拿到的 4 个文件

| 文件 | 给谁用 | 干什么 |
|---|---|---|
| `ars45_print_pack.3mf` | **Bambu Studio / OrcaSlicer** | 双击打开 → 2 个件已在里面, 单位=mm, 不用手动缩放 |
| `print_profile.json` | 同上 | 导入为打印配置 (层高/壁圈/支撑/温度 全预置) |
| `pa_cf_filament.json` | 同上 | 导入为耗材配置 (PA-CF 260/80℃) |
| `bambu_p2s_machine.json` | 同上 | 导入为机器配置 (P2S / 0.4 硬化钢喷嘴 / 256³) |

> 切片软件路径: Bambu Studio → `设置 → 导入配置` 选 JSON; OrcaSlicer 同理。
> **若你直接用打印机自带 App (Bambu Suite)**: 打开 3mf → 切一刀 → 开始。

---

## 2. 打印参数 (已预置, 依据 MECH_BUDGET v1.1 §5.4)

| 项 | 值 | 为什么 |
|---|---|---|
| 喷嘴 | 0.4 硬化钢 | |
| 层高 | **0.2mm** | 细层纹利于小特征 (但层间结合更弱) |
| 壁圈 | 4 圈 | 最小壁厚 0.8mm = 2×喷嘴, 低于会"搓条" |
| 支撑 | **tree (仅试样)** | 目标 0 支撑; 只有 fit_coupon 的螺钉柱试样要支撑, 支撑痕在 Z 向正好测层间拉脱 |
| 悬空阈值 | 45° | ≤45° 无支撑; >60° 必须拆件 |
| 温度 | 260 / 80℃ | **PA-CF, 不用 PLA** (PLA 55-60℃ 就软, 充电区温升直接变形) |
| Brim | 5mm 贴边 | PA-CF 收缩率 0.3%, 防翘边 |
| 耗材密度 | 1.18 g/cm³ | PA-CF |

---

## 3. ⚠️ 打印前必读: PA-CF 的层间结合只有 XY 面的 50-60%

这是**本项目最大的打印件风险**（MECH §5.4 原话）:

```
螺钉柱沿 Z 拉脱 = FDM 打印件最常见的失效模式
```

所以 fit_coupon 里专门放了**沿 Z 开槽的螺钉柱拉脱试样** —— 打印时**必须让它带支撑**（支撑痕在 Z 向，量拉脱力才有意义）。

---

## 4. 操作步骤

```
1. 打印机通电, 确认耗材是 PA-CF (不是 PLA!), 喷嘴是 0.4 硬化钢
2. Bambu Studio / OrcaSlicer 打开 PRINT/ars45_print_pack.3mf
3. 导入 print_profile.json + pa_cf_filament.json + bambu_p2s_machine.json
4. 摆放: fit_coupon 平放 (底面贴板); temple_cage 立放或平放按实际, 保证基准面贴板
5. 切片 → 检查预览: 层高 0.2 / 壁圈 4 / 支撑只在试样 / 温度 260-80
6. 打印
7. ★ 冷却后立刻量 → 按 MECH/print/MEASURE_CHECKLIST.md 的 41 项逐项量并填表
8. 把实测值回填 state/measurements.yaml 的 M-PRINT (kind 必须是 "实测")
9. 跑 python3 state/stage_gate.py → 看 G2 缺口有没有减少
```

---

## 5. 量完填哪里 (这一步不能省)

```
量完 → MECH/print/MEASURE_CHECKLIST.md 的表填好
     → state/measurements.yaml 的 M-PRINT (value=实测值, kind="实测", by=测的人, when=日期, evidence=清单路径)
     → HANDOFF/2026-10-25_mech-lead_空间预算.md 的 B2 自评表把"未验"改成"通过/不通过"
```

⚠️ **不许拿模型值冒充实测** —— `stage_gate.py` 只认 `kind == "实测"`, 推算值会被直接拒绝（这正是它存在的意义）。

---

## 6. 一键自检

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 PRINT/verify_print_pack.py     # 校验 3MF/JSON/STL 自洽 + 关键尺寸在范围内
```

---

## 7. 还没解决的 (不影响你打印, 但记着)

- **打印机网络**: 机器在 `192.168.1.68`, 本机在 `192.168.2.4/24` → 跨网段不可达 (ping 无响应, 990/8883/6000/4000 全 closed)。**你直接在打印机那侧用它的 App 打印就行**, 不用本机连。
- **量具**: 本机无卡尺/千分尺/塞尺 → 打印完在你手边量, 或借/买 (游标卡尺 0-150mm 即可, ¥30-80)。
- **G-code**: 本机无切片器 → 在打印机软件里点一次切片。
