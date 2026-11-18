【ARS45 · demo 主板 · I2C 地址表全量核对 + 网表注释订正 + 门禁化 (ISS-153)】

## 背景 (为什么现在做)
demo 主板网表已经按 **IMX415 camera 模组** 重画过一轮, 但 I2C 这条线上留着 **3 处已知过期/自相矛盾**的东西:

1. ★**地址注释过期**: `state/gen_netlist.py` 里 U_TEMP 那条注释 (★`gen_netlist.py:806` 附近) 仍写
   "IMX415 = 0x1a / AR0234CS = 0x10 / **桥接 0x50** / **充电 IC 0x12** / 光机 0x72 都不冲突"
   ⇒ ★**"充电 IC 0x12" 是错的** (BQ25896 实为 **0x6B**, `HW/INTERFACE_TABLE.md:138` V1.5 已订正);
   ⇒ ★**"桥接 0x50" 已作废** (随 RK3572 无 DP TX, 桥接整条删除)。
2. ★**I2C_A 上拉轨, 注释和实际 net 打架**: 实际 net 是 **2.2k → `RAIL_VDD_1V8_IO`** (camera 模组 FPC 上标 **I2C5 = 1.8V 域**),
   但网表 note 仍写 "**[VDD_3V3_IO]** I2C_A 上拉 … ★**上拉仍留 3.3V**" ⇒ ★**注释与实际 net 相反**
   ⇒ 这正是 ISS-159 的 F3 依据区列的 **C4 冲突**, 一直没收口。
3. ★**`HW/netlist_v1_pins.csv` 停在 11-03 00:50 的旧版** (TMP117 还是 4 脚 / 还挂在 I2C_A),
   而生成器 11-04 04:0x 已把 U_TEMP 改成 **官方 6 脚 WSON-6 + 挂 I2C_B** (ISS-178) ⇒ **脚级 csv 落后于生成器**。

⇒ 本单的根子: **"换 sensor 时 I2C 地址会变 ⇒ 每次换料必须重核整条总线的地址表"** —— 这次把它 **做成门禁**, 下次换料不会静默改地址。

## 你要交的 (3 件)
### ① `HW/I2C_ADDR_TABLE.md` —— I2C_A / I2C_B 两条总线的从设备全表
每行必须有: 总线 | 位号 | 器件 | 7-bit 地址 | **地址来源 (原厂 datasheet 型号 + 表号/页号)** | 上拉轨 | 电压域 | 与同总线其它设备是否冲突

待核清单 (★**逐个用原厂 datasheet 核, 不许照抄本单, 不许猜**):
| 器件 | 本单给的线索 (★都只是线索, 以你核到的 datasheet 为准) |
|---|---|
| camera (IMX415 模组) | 0x1a — `HW/IMX415_DEMO_SENSOR_FACTS.md:21,159` (两处独立来源) |
| 温度计 TMP117 (`U_TEMP`) | 0x48 — TI TMP117 datasheet (ADD0/ADDR1 默认); ★**注意它现在挂 I2C_B** |
| 充电 IC BQ25896 (`U_CHG`) | ★**0x6B** (TI BQ25896 datasheet) —— ★**不是 0x12**; ★**它在 CHG_BOARD (镜框充电板), 不是本板** ⇒ 请核清它**到底有没有挂在任一条 I2C 总线上** (STAT/PG 是 GPIO, 不是 I2C) |
| 光机 / 屏侧 MCU | 光机 0x72 (A/B 两条都预留, `HW/INTERFACE_TABLE.md:146-149`); 屏内 MCU 0x45 (`HW/PCB/PI5_DSI_22P_PINOUT.md:83`) |
| 桥接 (U_BRIDGE) | ★**已作废** —— 只在备注里写明"随 RK3572 无 DP TX 整条删除" + 依据 |
| AR0234CS (整机阶段) | 0x10 —— ★demo 不用, 只在备注里写 |

★**表尾必须给冲突检查结论**: 同一条总线上所有地址两两不同 (逐对列出比对结果)。

### ② 订正生成器里的过期注释 (★只改注释文字, 不改任何连接关系 / 脚号 / 网名 / 器件值)
- `state/gen_netlist.py`: "充电 IC 0x12" → 改成 **0x6B** (或按 ① 的核实结果改成"不在本板总线上"); "桥接 0x50" → 改成"已删除"
- ★**I2C_A 上拉那条 note**: 把 "[VDD_3V3_IO] … 上拉仍留 3.3V" 改成与实际 net 一致的 **1.8V 域** 口径 (实际是 `RAIL_VDD_1V8_IO`), 并写清依据 (camera 模组 FPC 标 I2C5 = 1.8V 域)
- ★**同一份注释在网表里出现不止一处** ⇒ **全部找出来一起改**
- 改完 **重跑生成器** ⇒ `HW/netlist_v1.csv` 跟着重生成
- ★**顺便把 `HW/netlist_v1_pins.csv` 重新生成** (`python3 state/gen_netlist_pins.py`) —— 它现在停在 11-03 00:50 的旧版 (TMP117 4 脚 / 挂 I2C_A), 与生成器不一致

### ③ 门禁: `state/check_netlist_pins.py` 加一条判据 (编号 C9)
**"I2C_A / I2C_B 上每个从设备的地址, 与 `HW/I2C_ADDR_TABLE.md` 一致; 且同总线地址唯一"**
⇒ 以后谁改了地址却没改表 ⇒ 门禁报错 (和 C6/C7/C8 一样的"内容存在性门禁"风格, 自己看该文件已有判据怎么写)。

## 硬要求
- ★**每个地址都要有原厂 datasheet 出处** (型号 + 表号/页号) ⇒ 没有出处的写 "**未查到**" + **试过的 URL + 失败原因** ⇒ ★**绝对不许猜**
- ★**网表是生成物** ⇒ 改生成器 → 重跑 ⇒ csv 跟着变 ⇒ ★**不许手改 csv**
- ★**只允许改这些**: `HW/I2C_ADDR_TABLE.md` (新建) · `state/gen_netlist.py` (**只改注释文字**) · `state/check_netlist_pins.py` (**只加 C9 判据**) · `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` (**生成物**) · `HANDOFF/2026-11-04_hw-lead_ISS153.md` (交卷说明) · `state/fragments/hw.yaml` (你自己的分片)
- ★**不许改**: `PROJECT_TRACKER.md` (★**§0 锁死表尤其不许动**) · `STATE.yaml` · `state/issue_log.yaml` (★**状态由项目总工改**) · 别的 agent 的分片 (`pm.yaml` / `sw.yaml` / `mech.yaml`) · `HW/PCB/LAYOUT_RULES.md` · `HW/PCB/STACKUP.md` · `HW/SCHEMATIC_V1_SPEC.json` · `HW/PCB/demo_mainboard.kicad_pcb`
- 不发邮件 / 不联系厂家 / 不下单 / 不询价 / 不写任何别的 agent 的分片

## 自证 (交卷时把命令 + 输出一起贴进 HANDOFF)
```
cd projects/smart_glasses
python3 state/gen_netlist.py            # 重生成网表 (rc=0)
python3 state/gen_netlist_pins.py       # 重生成脚级 csv (rc=0)
python3 state/check_netlist_pins.py     # ★新判据 C9 必须过 (rc=0)
python3 state/check_netlist.py          # ★全量门禁必须仍全绿 (rc=0, 不许把你的改动打成别的判据红)
python3 state/check_kicad_net.py        # ★网表↔板一致 (rc=0)
```
★**若你的改动把任何既有门禁打红 ⇒ 交卷无效** —— 自己修到绿。

## 验收标准
- [ ] `HW/I2C_ADDR_TABLE.md` 两条总线全表齐全, 每行有 datasheet 出处 + 冲突结论
- [ ] 生成器注释里不再出现 `0x12` / `桥接 0x50` / "上拉仍留 3.3V" (或已改成正确口径)
- [ ] `HW/netlist_v1_pins.csv` 与生成器同步 (TMP117 = 6 脚 / 挂 I2C_B)
- [ ] `check_netlist_pins.py` 里有 C9 判据且 rc=0
- [ ] `HANDOFF/2026-11-04_hw-lead_ISS153.md` 写清: 核了几个地址 / 订正了哪几处 / 哪些没查到 / 五条自证命令的 rc

## 汇报 (8~12 行)
核了几个地址 / 订正了哪几处 / 哪个没查到 (附试过的 URL) / C9 判据编号 / 五条自证命令的 rc
