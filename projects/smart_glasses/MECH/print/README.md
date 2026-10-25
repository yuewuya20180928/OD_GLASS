# P2S 打印包 (M-PRINT 的载体) — mech-lead 2026-10-25

> **本机无法打印/量测** (证据见 `ENV_PROBE.log`): 打印机 `192.168.1.68` 与本机 `192.168.2.4/24`
> 不同网段不可达; 无切片器; 无卡尺/千分尺/塞尺; 无 USB 串口。
> 所以这里交付的是 **可直接下片的 STL + 逐项测量清单**, 不是"已打印"。

## 文件

| 文件 | 说明 |
|---|---|
| `fit_coupon_340.stl` | **配合尺寸标定件** (150×90×22mm) — 一次打印拿到全部关键配合尺寸的实测值: 壁厚阶梯 / 间隙梳 / 螺钉柱 (含沿 Z 开槽版, 拉脱试样) / 配作孔 / 悬空角试样 / 标定块 / 波导卡槽间隙 |
| `temple_cage_340.stl` | **镜脚内腔检具** (60×123×28mm) — 电池槽 (340mAh 档 40.8×23.8×4.9) / 配作销 / 走线槽 6×2 / Type-C 面板 9.5×3.6 + 承力壁 1.5 |
| `optical_cage_TEMPLATE.stl` | **镜框光学舱托架模板** (40×22×30mm) — ⚠️ 走鹃Ⅱ 三维尺寸未到 (u1), 参数全 [推算] → **先别打**, 等 JBD 数据后重生成 |
| `gen_print_pack.py` | STL 生成器 (纯 numpy 自写几何, 本机无 CAD 库) — 每个尺寸都标了 v1.1 章节号 |
| `verify_pack.py` | **模型级自检**: 对 STL 做光线投射实测, 与标称值对表 (当前 **41/41 一致**) |
| `MEASURE_CHECKLIST.md` | **逐项测量清单**: 量哪里 / 用什么量 / 合格判据 / 记录格式 / 回填规则 (这是 M-PRINT 的执行书) |
| `ENV_PROBE.log` | 本机无法打印/量测的探测记录 |

## 一条命令复现

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/print/gen_print_pack.py     # 重新生成 3 个 STL
python3 MECH/print/verify_pack.py         # 模型自检 (41/41)
python3 MECH/fit_check.py                 # M-FIT 干涉检查 (设计态计算)
```

## ⚠️ 口径 (别把模型自检当成实测)

`verify_pack.py` 量的是 **STL 网格的几何真值**, 它证明的是 "v1.1 的数字被正确实体化了",
**不是** "打印出来的实物是多少毫米"。实物还有 FDM 工艺偏差 (孔径收缩 +0.1~0.2mm、层纹、
收缩率), 那一层只能靠 `MEASURE_CHECKLIST.md` 里的实物实测补上。
→ 所以 `state/measurements.yaml` 的 **M-PRINT 仍然是 [推算]/未测**, 阶段门 G2 不认 (符合设计意图)。

## 打印参数 (先定死, 否则数据不可比)

0.4 硬化钢喷嘴 / 层高 0.2mm / **PA-CF** (禁 PLA) / 4 圈壁 (0.8mm) / 目标 0 支撑 /
螺钉柱试样柱轴沿 Z (最不利工况) / 打印后静置 24h 再量 (PA-CF 吸湿)。
