# 项目状态快照 (自动生成)
> 生成时间: **2026-11-11 15:26** | 数据源: `projects/smart_glasses/STATE.yaml` + `state/issue_log.yaml` + 各门禁实时输出
> 本文件由脚本生成, **数字与真源一致** (不是手写)。
## 1. 一屏总览
```
产出 162 | 阻塞 43 (高危 33) | 未闭合需求 87 | 冲突 0 | 健康度 red
```
## 2. 交付质量门 (Q1-Q5)
```
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-11_hw-lead_ISS186_DSI_payload_订正.md   ★按 2026-11-11_hw-lead_ISS186_DSI_payload_订正.md 计分 (最新一份 2026-11-11_hw-lead_ISS189_DSI_payload_收尾.md 缺 ['B3', 'B4'])
   sw-lead    6/6  缺: 无   交接单: 2026-11-11_sw-lead_ISS190_时序复评_网表锚定.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-06_mech-lead_周更新.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '推算', '0数据', '0 数据']

【Q3 接口声明率】 全员 interface_claims 共 480 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    189 条
   sw-lead    107 条
   mech-lead  184 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 56/217  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 61 条, 其中 58 条真对上了别人的需求 key
   hw-lead    被答 23/71 | 我答 34 条(有效 31) | 产出 61 | 阻塞 7
   sw-lead    被答 9/59 | 我答 3 条(有效 3) | 产出 45 | 阻塞 15
   mech-lead  被答 24/87 | 我答 24 条(有效 24) | 产出 46 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 79 条 | **全局 70 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 87 条**
   ✅ 与 merge.py 自对账一致 (等外部 70 / 等总工 87)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 9 个
      q1_latency_scope: 发起方 ['main', 'sw-lead']
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q17_display_fps: 发起方 ['main', 'sw-lead']
      q18_highspeed_cam: 发起方 ['main', 'sw-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']

【Q5 硬指标覆盖】 2/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    1/5 类: ['端到端延迟(ms)']
   sw-lead    4/5 类: ['功耗(W)', '皮肤温度(°C)', '镜腿/镜脚厚度(mm)', '端到端延迟(ms)']
   mech-lead  4/5 类: ['功耗(W)', '皮肤温度(°C)', '镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 30 条需求确实还没人答 (等另一个总工)
   · sw-lead: 25 条需求确实还没人答 (等另一个总工)
   · mech-lead: 27 条需求确实还没人答 (等另一个总工)

==========================================================================
```
## 3. 问题闭环门
```
==========================================================================
问题闭环门 · Issue Gate
==========================================================================
登记问题 188 条 | 状态: closed=97 deferred=14 verified=42 fixed=6 open=26 fixing=3
  ├─ 内部可自行推进: 159 条 | 外部依赖 (等老板/原厂/JBD): 29 条
  ├─ 逾期未闭环: 32 条
  └─ 未闭环 blocker 级: 8 条

【问题清单】(按 severity + 逾期排)
  🔴 ISS-002  closed    owner=boss       due=2026-10-26   [外部]
       Q1 端到端口径 + Q4 续航口径 待拍板
  🔴 ISS-012  closed    owner=boss       due=2026-10-26   [外部]
       Q1 60ms 口径 + Q17 显示帧率 待拍板 → 达标结论定不下来
  🔴 ISS-014  closed    owner=boss       due=2026-10-26   [外部]
       散热 43°C 红线不达标 (0.23W→46.5°C) → 需 SoC/充电板挪出镜脚
  🔴 ISS-018  closed    owner=boss       due=2026-10-27   [外部]
       Q16 sensor 宽高比 A/B/C 拍板 (卡 sensor 选型 + 镜头畸变预算)
  🔴 ISS-010  closed    owner=boss       due=2026-10-28   [外部]
       光机逐帧延迟 0 数据 (软件打不了点, 需高速摄影/示波器)
  🔴 ISS-078  closed    owner=hw-lead    due=2026-10-28  
       ★板宽/逃线/叠层复核 (官网 宽度≤8mm 硬约束 + FCCSP pitch 推断 0.4-0.5mm) —— 可能推翻 12m
  🔴 ISS-081  closed    owner=hw-lead    due=2026-10-28  
       球数预算 + 最小引脚集分析 (证明封装/球数不是风险, 只剩映射问题) + 8x10 FCCSP 在 pitch 0.3/0.4/
  🔴 ISS-001  closed    owner=vendor     due=2026-10-29   [外部]
       原厂纸面资料 7 天未回 (第一轮 10-21 发出; 显示接口/电源域/FCCSP pinout/启动存储)
  🔴 ISS-003  closed    owner=vendor     due=2026-10-29   [外部]
       Q16 显示 TX 接口未确认 → 是否要加桥接芯片
  🔴 ISS-005  closed    owner=vendor     due=2026-10-29   [外部]
       ARS45 显示输出接口未确认 → 原理图只能留双出口
  🔴 ISS-006  closed    owner=vendor     due=2026-10-29   [外部]
       FCCSP 球间距未知 → 逃线/叠层给不出 (已升级为选型一票否决)
  🔴 ISS-007  closed    owner=vendor     due=2026-10-29   [外部]
       电源域电压/电流上限未知 → 电压域清单写不出
  🔴 ISS-008  closed    owner=vendor     due=2026-10-29   [外部]
       HW-03 启动存储/固件分区方案未定 (tracker 漏项)
  🔴 ISS-009  closed    owner=vendor     due=2026-10-29   [外部]
       NPU 纯硬件耗时未知 → 框龄 age 算不准 (±16.67ms 台阶)
  🔴 ISS-011  closed    owner=vendor     due=2026-10-29   [外部]
       NPU 输出是否强制 FP32 未知 → 端到端多 7.3ms 风险
  🔴 ISS-015  closed    owner=vendor     due=2026-10-29   [外部]
       PCB 板宽跟 FCCSP pitch 走 + 启动存储未知 → 板宽定不下来
  🔴 ISS-074  verified  owner=main       due=2026-10-29  
       ★开始画硬件原理图 V1 (8 页图页 + 完整 netlist + KiCad 可导入 .net) —— 球位号统一用 TBD 占
  🔴 ISS-083  closed    owner=main       due=2026-10-29  
       ★显示 TX 公开渠道穷举 (AR9481 模组厂/模组规格书/公开板卡 + 酷芯模组供应商) —— 不等原厂也能判 DSI TX 
  🔴 ISS-147  verified  owner=main       due=2026-11-04  
       ★★★[demo P0] 恢复 RKNN 构建环境 + 证明 rk3572 是 rknn-toolkit2 2.3.2 的合法 ta
  🔴 ISS-148  closed    owner=main       due=2026-11-04  
       ★★[硬件] AR0234CS 硬件数据 (U2 VDD_IO abs max / U4 有无独立模拟轨) + ★demo sens
  🔴 ISS-158  closed    owner=main       due=2026-11-04  
       ★★★[demo 头号硬件阻塞] 三件前置选型 (camera 模组 / 屏模组 / RK3572 核心板) ⇒ 主板照它们画 (★
  🔴 ISS-182  closed    owner=main       due=2026-11-04  
       ★★★[投板级 · 已修] 网表 4 处致命缺陷 + 导出器"幽灵分裂网" bug + VBUS 分压失效
  🔴 ISS-013  deferred  owner=jbd        due=2026-11-05   [外部]
       波导未选型 → 缺 2D 外形图/容差角/彩虹纹 → 镜框不能开工
  🔴 ISS-144  deferred  owner=main       due=2026-11-05  
       ★★★★[demo 关键路径 #1] AR0234CS → RK3572 rkisp3 驱动移植 (★先出规格, 不出代码)
  🔴 ISS-145  verified  owner=sw-lead    due=2026-11-05  
       ★★★★[demo 关键路径 #2] demo 板 OD 管线打通规格: yolov5n INT8 → RKNN → 画框 → 视涯
  🔴 ISS-149  closed    owner=main       due=2026-11-05  
       ★★★[硬件优先] demo 硬件形态落地: 一块主板 + **IMX415 sensor 模组** + 屏幕驱动板模组 + FPC
  🔴 ISS-165  closed    owner=main       due=2026-11-05  
       ★★★[硬件 A2 段 · 最后一块] SOM 座 (4×100pin/0.4mm BTB) + SoC 节点改挂 + ★CARRI
  🔴 ISS-166  closed    owner=main       due=2026-11-05  
       ★★★[P0 · 短路级] 网表连接器脚位: 一个脚挂多个网 (CONN_CAM 12 处 / CONN_LIGHT 9 处) ⇒ 
  🔴 ISS-167  closed    owner=main       due=2026-11-05  
       ★★★[P0 · 假绿] 板生成器按 CSV 行序给焊盘编号 ⇒ 连接器脚位全错; 等价性门禁比集合 ⇒ 报绿
  🔴 ISS-168  closed    owner=main       due=2026-11-05  
       ★★★[P0] RK3572 与 RK3576 引脚功能不同 ⇒ 上一版 SoM 引脚分配表作废 (226/398 脚球号不同)
  🔴 ISS-170  closed    owner=main       due=2026-11-05  
       ★★★[demo 板可制造性] 显示器 FPC 座: 屏侧 40p/0.5mm 与原厂排线主板侧 39p/0.3mm 矛盾 ⇒ 画 
  🔴 ISS-175  closed    owner=main       due=2026-11-05  
       ★★★[选型变更 · 老板拍板] demo 屏换 ≤3 寸 (原 Radxa Display 8HD = 8.0" 太��) ⇒ 背
  🔴 ISS-183  closed    owner=main       due=2026-11-06  
       ★★★[投板级 P0 · 已修待验] SoM 的 7 个 DCIN 脚落在孤岛网 `RAIL_SOM_DCIN` ⇒ 板上**没有到
  🔴 ISS-184  closed    owner=main       due=2026-11-07  
       ★★★[网表级 P0 · 已修待验] `.net` 导出器把「只在 node 串里出现、ref 列里没有」的器件(J_SOM_P2 
  🔴 ISS-181  deferred  owner=hw-lead    due=2026-11-08  
       ★★★[最高优先级 · 老板 11-04 19:10 指示] 自研 demo 主板: 从骨架布到**可下单** (unconnect
  🔴 ISS-162  verified  owner=main       due=2026-11-13  
       ★★★[硬件 · 画板前必须] 网表按真实器件规格重出: FPC 座 31p/0.3mm + 40p/0.5mm + SOM 400
  🔴 ISS-119  fixed     owner=main       due=2026-11-05   ⏰逾期
       ★★换芯定案 + 迁移方案 (A7/A8): 选哪颗 + 网表/原理图/BOM 重做清单 + 为 RK3588 预留的可执行后手
       ❌ ★逾期★ due=2026-11-05 已过, 仍 fixed
  🔴 ISS-139  open      owner=main       due=2026-11-05   ⏰逾期
       ★★[内部, 与选谁无关] ISP tuning 立项: 两个候选 sensor 都没有现成 IQ 文件 ⇒ 这笔账必须自己排
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🔴 ISS-155  open      owner=main       due=2026-11-06   ⏰逾期
       ★★★★[demo 头号卡点] rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 targe
       ❌ ★逾期★ due=2026-11-06 已过, 仍 open
  🔴 ISS-160  open      owner=main       due=2026-11-06   ⏰逾期
       ★★★[自己画图] demo 主板图纸链: KiCad 10 工具链(免 root AppImage) + 参数化生成器 + DRC
       ❌ ★逾期★ due=2026-11-06 已过, 仍 open
  🟠 ISS-039  closed    owner=boss       due=2026-10-27   [外部]
       【缺清单】认证与合规要求未梳理 (含光生物安全) —— 需老板定销售区域
  🟠 ISS-046  closed    owner=boss       due=2026-10-27   [外部]
       ★FOV 与俯角正面冲突: 对角 100° → 垂直半视场仅 30.3°, 俯角 32° 时正前方掉出画面
  🟠 ISS-019  closed    owner=main       due=2026-10-28  
       桥接芯片并行询价 (不等原厂回信, 抢 4-8 周采购周期)
  🟠 ISS-026  closed    owner=mech-lead  due=2026-10-28  
       可靠性测试方案缺失 (跌落/扭转/弯折/汗液/盐雾/UV 全 0)
  🟠 ISS-058  closed    owner=mech-lead  due=2026-10-28  
       ★打印包按 Rev A 参考实现重生成 (verify_pack 38/46 → 46/46) —— 否则量出来的尺寸对不上解 A 
  🟠 ISS-077  closed    owner=hw-lead    due=2026-10-28  
       功耗预算 V3: 按官网 250mW 口径重算 (媒体 300mW → 官网 250mW, 差 20%) + V_CORE 上界按 
  🟠 ISS-075  closed    owner=hw-lead    due=2026-10-28  
       审 8 页图页 + 补器件级细节 (P1 充电链 ESD/π滤波/MOSFET, P7 LED 限流/按键消抖) —— 上一版 27
  🟠 ISS-088  closed    owner=hw-lead    due=2026-10-28  
       ★审原理图 V1.1 (9 页 + 24 条门禁 + BOM 295 位号) —— V1.1 增量由项目总工自产, 验证人必须是 h
  🟠 ISS-021  closed    owner=main       due=2026-10-29  
       缺系统架构图 / 尺寸堆叠图 / 电源拓扑图 (现在全是文字表)
  🟠 ISS-022  closed    owner=hw-lead    due=2026-10-29  
       EMC 预评估缺失 (只有 HW-25 一条 ESD 器件)
  🟠 ISS-023  closed    owner=hw-lead    due=2026-10-29  
       可靠性设计评审缺失 (降额/应力/MTBF 全空)
  🟠 ISS-028  closed    owner=sw-lead    due=2026-10-29  
       缺 EVT 报告模板 + 软硬件联调计划 (G3 无载体)
  🟠 ISS-042  closed    owner=mech-lead  due=2026-10-29  
       镜脚侧装配余量临界 (前后余 0.30mm vs FDM 公差 ±0.2-0.3mm) → 叠放模型实际不通过
  🟠 ISS-044  closed    owner=sw-lead    due=2026-10-29  
       Q17=60fps 的达标判定条件已写死: M-NPU ≤16.67ms (age=1) 才成立, 否则自动切 30fps
  🟠 ISS-045  closed    owner=hw-lead    due=2026-10-29  
       sensor 选型解冻 (Q16 已拍板: 只需 ≥1920×1080@60fps) —— 立即启动
  🟠 ISS-050  closed    owner=mech-lead  due=2026-10-29  
       打印包需按解 A 修订几何 (电池座 4.90→4.75 非对称 + 0.8 顶板 + 配作孔 ⌀2.0→⌀2.4)
  🟠 ISS-051  closed    owner=hw-lead    due=2026-10-29  
       镜头选型目标改为 对角 FOV 120° (垂直半视场 40.3°) + 俯角 ≤25°
  🟠 ISS-054  closed    owner=hw-lead    due=2026-10-29  
       原理图可画部分落地: 顶层接口定义 + 低速接口 + 外围 IC 选型 (全部不等原厂)
  🟠 ISS-055  closed    owner=hw-lead    due=2026-10-29  
       ★用官方口径 <300mW 重算整机功耗预算 —— 可能翻案 46.5°C 的散热结论
  🟠 ISS-056  closed    owner=sw-lead    due=2026-10-29  
       ★ISP 缩放必须整幅 scale, 禁用 ROI 裁剪 (ROI 会把对角 FOV 从 120° 砍到 85.61°)
  🟠 ISS-057  closed    owner=hw-lead    due=2026-10-29  
       ★先画 AR9481 同 Die 参考版原理图 (每脚标证据等级) —— 出图周期从 1-2 周压到 2-3 天
  🟠 ISS-067  closed    owner=hw-lead    due=2026-10-29  
       R-F1 3.3V 轨拓扑裁决落地 (UVP 抬 3.5V + 3.3V 改供 + 评估不牺牲容量的替代方案)
  🟠 ISS-068  closed    owner=hw-lead    due=2026-10-29  
       可靠性证据缺口收口 (15/15 器件 Absolute Maximum Ratings 逐个核 + 实测项挂样机 + FIT 数据
  🟠 ISS-084  closed    owner=mech-lead  due=2026-10-29  
       SoC 载板化/模组化的结构与代价评估 (把 引脚映射 风险从项目级压到载板级) + 兜底 SoC 路线 (用现成模组做 EVT 验
  🟠 ISS-087  verified  owner=sw-lead    due=2026-10-29  
       模型许可未清 (L1 许可[0数据] + L4 AGPL-3.0 商用受限) + ARS45 板端模型 0 个 → 量产评审放行门禁
  🟠 ISS-090  verified  owner=sw-lead    due=2026-10-29  
       ★软件侧交叉评审 (时序/信号/电源时序) + TMP117 测点物理位置 + 跨铰链 USB 烧录可行性
  🟠 ISS-101  verified  owner=sw-lead    due=2026-10-29  
       ★模型许可: 唯一许可干净候选 (Apache-2.0) 的 NPU 可转换性 = 0 数据 → 量产可用模型清单为空
  🟠 ISS-110  verified  owner=sw-lead    due=2026-10-29  
       ★RKNN 转换链实测 (RK3576 资料维度实测 + 端到端 ≤60ms 判定) —— 已交付并验收
  🟠 ISS-053  closed    owner=sw-lead    due=2026-10-30  
       ★鱼眼 + 不裁剪 的副作用: 检测框在图像上是弯的, SW 必须做'检测框反投影到真实方位角'
  🟠 ISS-115  closed    owner=hw-lead    due=2026-10-31  
       ★选型情报检索: TOP10 国内厂商名单 + 每家 TOP1~5 候选 + 逐项证据 (只交证据, 不打分)
  🟠 ISS-146  verified  owner=boss       due=2026-11-03   [外部]
       ★★[等老板一句] demo 板形态: 模组+转接板 (我的建议) 还是 自制整板? —— 决定 PCB 与周期
  🟠 ISS-142  deferred  owner=boss       due=2026-11-04   [外部]
       ★[外发待放行] onsemi AR0234CS 问询草稿已写好 (pinout/电源域/CRA/lane 速率/功耗/驱动) ⇒ 
  🟠 ISS-151  verified  owner=main       due=2026-11-04  
       ★★[硬件优先] 替代料候选清单: 每类物料 ≥3 个公开在售替代品 + 来源/规格/数据来源评分 ⇒ 让「都试过了」可核查
  🟠 ISS-040  deferred  owner=boss       due=2026-11-05   [外部]
       打印与量测条件不具备 (打印机跨网段不可达 + 无切片器/量具) → M-PRINT 卡死
  🟠 ISS-049  closed    owner=hw-lead    due=2026-11-05  
       PCB 定位方式变更 + 骨架长度上限 (来自 ISS-042 解 A) —— 需 hw-lead 改孔位
  🟠 ISS-080  verified  owner=sw-lead    due=2026-11-05  
       S2 救砖链路 (进 BOOT 模式 → 厂商下载工具识别 → 刷回来) 必须实测 —— 量产一票否决项
  🟠 ISS-082  closed    owner=main       due=2026-11-05  
       ★电源域不确定性吸收进选件 (6 路 LDO 改用可编程 TPS7A20 一颗覆盖 1.2-5.5V + DC-DC 大裕量 + P
  🟠 ISS-094  closed    owner=main       due=2026-11-05  
       ★投板前网表要做 pin-centric 重整 (现在 CSV 是『连接清单』模型, KiCad 网表要的是『每引脚一行』)
  🟠 ISS-112  closed    owner=hw-lead    due=2026-11-05  
       ★BQ25896 封装 footprint 落库 (WQFN RTW 24pin 4×4mm) + 充电板面积重算 (+7mm²)
  🟠 ISS-114  verified  owner=main       due=2026-11-05  
       ★★换芯片选型总单: 国内 TOP10 厂商 × TOP1~5 芯片 × 9 项打分 (老板 10-29 09:59 改令) —— 
  🟠 ISS-138  verified  owner=boss       due=2026-11-05   [外部]
       ★★★[要老板一句拍板] sensor 模式选路: OV04C10 @1080p60 ⇒ 镜头/FOV/角分辨率/快门 四个代价要选
  🟠 ISS-150  closed    owner=main       due=2026-11-05  
       ★★★[硬件优先 #3] demo sensor 换 IMX415 ⇒ 网表三条电源轨要重核 + 1080p60 输出模式定案
  🟠 ISS-157  closed    owner=main       due=2026-11-05  
       ★★[软件] rknn_bench.py 的 cut 模型缓存不失效 ⇒ 换模型重测会静默跑出上一个模型的数字 (实测两次结果逐字节
  🟠 ISS-159  closed    owner=hw-lead    due=2026-11-05  
       ★★[demo] 画板前致命项清零 F4~F12 (★照 EN 那个 P0 的教训: 漏到投板后 = 2~4 周返工)
  🟠 ISS-164  verified  owner=main       due=2026-11-05  
       ★★[等老板一句] demo 精度验收线: yolov5n F1 0.2927 差 0.0073 不达 0.30 门槛, 换 yol
  🟠 ISS-137  verified  owner=main       due=2026-11-06  
       ★★[可执行, 一行代码的活] 把「显示合成段」从 T_FIXED 里单独打点 —— 它是 RK3572 + 1920×1080 下
  🟠 ISS-140  closed    owner=main       due=2026-11-06  
       ★★[老板已拍板 D 的直接后果] sensor 换 AR0234CS ⇒ 网表电源域改造 (VDD_IO 1.8→2.8V) + 
  🟠 ISS-176  closed    owner=main       due=2026-11-06  
       ★★[显示接口重画] 显示器座换 Pi5 同规 22 位/0.5mm (吃 Waveshare 15→22 线) + 屏的控制 I2
  🟠 ISS-179  verified  owner=sw-lead    due=2026-11-06  
       ★★[手机测端到端] 显示画面烧帧计数器/时间码 + 手机慢动作测端到端延时作业指引
  🟠 ISS-141  deferred  owner=hw-lead    due=2026-11-07  
       ★★整机功耗账重算: OV04C10 155mW → AR0234CS (裸片功耗 [0数据]) ⇒ 皮肤温度 43°C 结论要重判
  🟠 ISS-178  closed    owner=main       due=2026-11-07  
       ★★[自查抓到] TMP117 被当成 4 脚器件画的 ⇒ **脚号与原厂完全对不上** (已改成官方 WSON-6)
  🟠 ISS-062  verified  owner=hw-lead    due=2026-11-09  
       R-GEO-2 四问转原厂/镜头厂 (边缘畸变区是检测价值最高处 / 4-lane MIPI / ISP 吞吐余量 98.1% / 
  🟠 ISS-099  verified  owner=hw-lead    due=2026-11-09  
       ★J_CHG 选型与 FPC 加工图要求 (触点额定 ≥0.35A / 分段铜厚 固定段2oz·弯折段1oz / 内层地 keep-
  🟠 ISS-108  closed    owner=hw-lead    due=2026-11-12  
       ★备选 SoC 选型: 老板 10-29 00:49 改令 (跳过酷芯微选型) ⇒ 扩到 TOP5 厂家 × TOP3 = 15 候
  🟠 ISS-154  deferred  owner=hw-lead    due=2026-11-12  
       ★★[整机阶段] AR0234CS 的 VDDIO_PHY 1.8V 轨缺失 + CONN_CAM 18p 占满 ⇒ 不供电就出不了
  🟠 ISS-187  verified  owner=main       due=2026-11-12  
       ★ISS-137 护栏两个洞 (M2 默认参数踢 TX / M3 无护栏钉 TX 绝对值) ⇒ 加护栏⑧⑨⑩ ⇒ ★已做完, 待 s
  🟠 ISS-052  closed    owner=mech-lead  due=2026-11-13  
       结构侧: 镜头镜筒/窗口/高度需求 (可不等镜头定档就开模) + 俯角收窄到 ≤25-28°
  🟠 ISS-085  verified  owner=mech-lead  due=2026-11-13  
       ★USB 跨铰链方案落地 (Type-C 留镜框充电板 + USB 差分跨铰链到镜脚主 PCB) + 跨铰链 USB 可靠性要求 +
  🟠 ISS-089  closed    owner=mech-lead  due=2026-11-13  
       ★硬件交叉评审 (机械/热/装配) —— 以 V1.1 的 9 页为输入, 挑出会打回来重画的点
  🟠 ISS-091  verified  owner=mech-lead  due=2026-11-13  
       ★跨铰链充电电流 1.0-1.5A 的载流/压降/发热核算 + J_CHG (1×10) 机械可行性 (MECH-B7 的后续)
  🟠 ISS-096  verified  owner=main       due=2026-11-13  
       ★复位释放时刻不由已画器件决定: 监督器只监督 V_SOC_IO 不监督 V_CORE, DC-DC 的 PG 只到测试点不参与复位
  🟠 ISS-098  verified  owner=main       due=2026-11-13  
       ★SoC 侧没有 USB VBUS 连接 (网表只有 D+/D−) ⇒ USB 枚举前提缺失, S2 救砖链路成立性未验; 且 CO
  🟠 ISS-100  verified  owner=mech-lead  due=2026-11-13  
       ★板宽 12mm → 15mm 的结构侧连带 (镜脚腔体/骨架长度/PCB 定位孔位/面积缺口 300mm² 复核)
  🟠 ISS-107  closed    owner=mech-lead  due=2026-11-13  
       ★更正 mech-lead 分片 pcb_mounting 旧取值 (2xM1.2+1x⌀2.0H7 → PIN-SET-2: 2x
  🟠 ISS-171  verified  owner=main       due=2026-11-13  
       ★★[IC 规格落定] 三个"我的假设"被原厂 datasheet 推翻 (已改网表) + 5 条仍未查到
  🟠 ISS-185  verified  owner=mech-lead  due=2026-11-13  
       ★ISS-107 同型问题 (第二面): 没有对手方的过期值 —— 本域 8 条 claim 的值停留在 10-28 基线, 合并器
  🟠 ISS-186  verified  owner=hw-lead    due=2026-11-13  
       ★DSI payload 8× 口径差: 6 处「373/246 Mbps」实为 2986/1475 Mbps ⇒ 依据虚到 8 倍
  🟠 ISS-190  verified  owner=sw-lead    due=2026-11-13  
       ★SW 侧时序/电源评审与机械复核器口径漂移 ⇒ SW_TIMING_REVIEW 锚在 476 行旧网表 (现行 513 行) ⇒
  🟠 ISS-191  fixing    owner=sw-lead    due=2026-11-13  
       ★P0 (来自 ISS-190 复评): 首台板可能因 RESET_N 恒低而无法启动 —— PG_AND 只剩 10k 上拉, 无
  🟠 ISS-192  fixing    owner=mech-lead  due=2026-11-13  
       ★★结构侧(MECH)机械复核器全线仍钉在已作废的 12/15mm 板宽 ⇒ 现在的绿灯不是关于现行板子说的(pinset2_mec
  🟠 ISS-143  closed    owner=mech-lead  due=2026-11-16  
       ★★结构侧新口径: 边框遮挡角必须进 FOV 余量账 (凹进 1.0mm = 1.91° 遮挡, 吃掉"正前方那一侧") ⇒ 镜框上
  🟠 ISS-120  verified  owner=sw-lead    due=2026-11-30  
       ★S2 救砖链路板端实测 (量产一票否决项) —— 方案+自检已闭环 (ISS-080), 待 EVT 有板后真跑 (EVT-8/B
  🟠 ISS-156  open      owner=main       due=2026-11-04   ⏰逾期
       ★★[demo 供应链] 自研主板的三件前置选型: camera 模组 / 屏模组 / RK3572 核心板 (★主板的 FPC 座
       ❌ ★逾期★ due=2026-11-04 已过, 仍 open
  🟠 ISS-038  open      owner=boss       due=2026-11-05   ⏰逾期 [外部]
       【缺角色】工业设计 (ID/CMF/佩戴舒适度) 无人负责 —— 需老板拍板是否加第 4 个总工
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-041  open      owner=boss       due=2026-11-05   ⏰逾期 [外部]
       ★★[当前 demo 板] 测试条件缺失 ⇒ G3 那一关不可判通过 (★2026-11-04 09:57 起: 不含热电偶/假皮肤
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-060  open      owner=boss       due=2026-11-05   ⏰逾期 [外部]
       产品件三条几何待老板裁决 (压垫吸收量零余量 / 非对称方向 / 压垫槽区板厚小于 FDM 最小壁) —— 打印包转绿不等于解 A 
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-063  open      owner=boss       due=2026-11-05   ⏰逾期 [外部]
       显示端 120 度到 30 度的映射方式 (看得广但糊 vs 看得清但窄) —— 120 度这个卖点对用户可见吗
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-097  fixed     owner=main       due=2026-11-05   ⏰逾期
       ★"关机"语义: 硬件断电通路 (负载开关) + 真关机拓扑 + 功耗预算 V3
       ❌ ★逾期★ due=2026-11-05 已过, 仍 fixed
  🟠 ISS-102  open      owner=main       due=2026-11-05   ⏰逾期
       ★[待原厂] 追加问 4 条: AON 域静态电流 / USB VBUS detect 脚 / TPS62130A PG 极性 / 
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-106  open      owner=boss       due=2026-11-05   ⏰逾期 [外部]
       ★新增渠道: 经酷芯微代理转达 (老板 10-28 找到代理) —— 代理信 + 3 份可转发附件已就绪
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-116  fixed     owner=main       due=2026-11-05   ⏰逾期
       ★★工作方式改造: 老板任务先落 GitHub 总表 + token 守护 (老板 10-29 09:59 亲自要求)
       ❌ ★逾期★ due=2026-11-05 已过, 仍 fixed
  🟠 ISS-122  fixing    owner=main       due=2026-11-05   ⏰逾期
       ★★BGA 逃线层数: ★两套模型结论相反 (9 层 vs 3 层) ⇒ 破没破 4-6 层锁是 [0数据] 不是结论 —— 必须问
       ❌ ★逾期★ due=2026-11-05 已过, 仍 fixing
  🟠 ISS-124  open      owner=main       due=2026-11-05   ⏰逾期
       ★★[待瑞芯微/RK3576 模组厂] ISP MP/s 吞吐上限 + ISP 动态功耗 vs 吞吐曲线 (2 问, 一票否决级的剩
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-126  open      owner=main       due=2026-11-05   ⏰逾期
       ★★板厚档位未定 ⇒ 检修口净空只有 4.90 那一档过 (1.22mm 档净空 4.48 破 4.50 硬要求)
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-127  open      owner=main       due=2026-11-05   ⏰逾期
       ★★★脱模斜度致镜脚 H 链最坏 −0.577mm ⇒ 几何上做不出来 (不是余量紧张, 是不可行) —— 量产架构必须改
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-128  open      owner=main       due=2026-11-05   ⏰逾期
       ★★主控换 RK3572 ⇒ 板面积账 + 逃线层数全部重算 (封装 FCCSP550L 14.3×15.5mm / 550 球, 
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-129  open      owner=main       due=2026-11-05   ⏰逾期
       ★★★RK3572 (4 TOPS) 板端纯 NPU 实测 ⇒ 端到端 60ms 硬指标生死判定 (★T2 翻案条件推算已命中)
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-130  open      owner=main       due=2026-11-05   ⏰逾期
       ★★★RK3572 功耗 670mW (原厂口径) vs 贴皮肤 43°C 红线 —— 从「待定」变「可判」
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-169  open      owner=main       due=2026-11-05   ⏰逾期
       ★★[demo 板可制造性] demo 主板的边界已定 (Type-C 供电 · 不装电池 · 板上只有这一块) + SoM 座的 
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟠 ISS-132  fixed     owner=main       due=2026-11-06   ⏰逾期
       ★★★[决定性] 视涯 0.49" 1920×1080 是单色还是全彩? —— 这题决定产品定义 (检测框能不能上色)
       ❌ ★逾期★ due=2026-11-06 已过, 仍 fixed
  🟠 ISS-133  open      owner=main       due=2026-11-06   ⏰逾期
       ★★★显示架构变更: '屏' ≠ '光机' ⇒ 必须新增一级耦合光学 ⇒ 镜框光学腔体/分光器/整机空间全部重算
       ❌ ★逾期★ due=2026-11-06 已过, 仍 open
  🟠 ISS-172  open      owner=main       due=2026-11-06   ⏰逾期
       ★★[选型待裁] 负载开关 U_PWR_SW / U_EN_SW: 原厂在售型号的判据互斥 (RON vs IQ vs 反向阻断)
       ❌ ★逾期★ due=2026-11-06 已过, 仍 open
  🟠 ISS-118  fixed     owner=hw-lead    due=2026-11-09   ⏰逾期
       ★板宽 15mm → 30mm 的硬件连带重算 (板框/网表/面积/逃线/跨铰链排布) —— 老板 10-29 19:16 放宽
       ❌ ★逾期★ due=2026-11-09 已过, 仍 fixed
  🟡 ISS-020  closed    owner=main       due=2026-10-28  
       PRD 补完: REQ/REQUIREMENTS.md 还是草稿 (子模块需求待填/验收标准待填)
  🟡 ISS-031  closed    owner=main       due=2026-10-28  
       规格变更追踪表缺失 (作废结论散在正文, 追溯不到谁改的)
  🟡 ISS-032  closed    owner=main       due=2026-10-28  
       风险登记册缺失 (tracker §5 是清单, 不是矩阵)
  🟡 ISS-061  closed    owner=sw-lead    due=2026-10-28  
       ISP 整幅 scale 收口后的三处文档同步 (CR-1 网格链 / CR-2 标定表加 f_out+(ox,oy) / CR-3
  🟡 ISS-064  closed    owner=mech-lead  due=2026-10-28  
       MECH_BUDGET §2.3/§2.3.1 数字同步 (46.5°C → 41.6-42.6°C 口径 + 镜腿内发热量口径 +
  🟡 ISS-070  closed    owner=sw-lead    due=2026-10-28  
       两处旧命名 + M1-R2 裸 1080p 语义张力 (sensor 必须支持全幅输出模式 → 升为 Q24 选型硬约束)
  🟡 ISS-071  closed    owner=sw-lead    due=2026-10-28  
       全幅口径的尾巴清理 (3 处): 内存规划表按全幅重算 + Q10 原厂问法改全幅 + §3.3 吞吐段与 S1 依据表述
  🟡 ISS-029  closed    owner=sw-lead    due=2026-10-29  
       USB 固件烧录 + 版本管理 + 回滚 缺失 (无线 OTA 不做, 但返修必需)
  🟡 ISS-030  closed    owner=main       due=2026-10-29  
       接口定义文档不完整 (41 条 claims 是'取值', 不是'接口规格')
  🟡 ISS-034  closed    owner=main       due=2026-10-29  
       外部方管理域缺失 (原厂/JBD/PCB厂 是关键路径, 但没框架)
  🟡 ISS-072  closed    owner=mech-lead  due=2026-10-29  
       新电池容量口径的落地 (厚度映射表加 315/387 两行 + 旧 8.7-11.2mm 作废 + 2.6 散热口径 + 3 重量表
  🟡 ISS-093  verified  owner=main       due=2026-10-29  
       ★充电板 (镜框) 的完整原理图页未画全 —— 现在主网表里只有 Type-C + BQ25896 的子集
  🟡 ISS-104  verified  owner=sw-lead    due=2026-10-29  
       ★术语统一: 关机(真断电) / 待机(深度休眠 0.15W, ~9.3h) —— SW 侧 API 与省电策略语义要跟上
  🟡 ISS-117  verified  owner=sw-lead    due=2026-10-31  
       ★RKNN_BENCH §3.3.1/§3.3.2 的数字在干净机上复算不出来 (383.26ms vs 实测 354.51ms) 
  🟡 ISS-004  deferred  owner=jbd        due=2026-11-05   [外部]
       波导未选型 (等 JBD) → 卡镜框打印开工
  🟡 ISS-016  deferred  owner=jbd        due=2026-11-05   [外部]
       走鹃Ⅱ 长宽高未知 → 光机位姿/干涉检查做不了
  🟡 ISS-043  closed    owner=hw-lead    due=2026-11-05  
       充电状态读取接口未确认 → 充电时禁 OD 门禁可能无法实现
  🟡 ISS-048  deferred  owner=jbd        due=2026-11-05   [外部]
       光生物安全所需的光机参数缺失 (LED 波长/亮度/光通量/辐亮度) —— 已并入 JBD 问询草稿
  🟡 ISS-065  closed    owner=mech-lead  due=2026-11-05  
       结构侧 5 条书面建议的落地评估 (镜腿内发热量口径 / 鼻梁也适用 43°C / 上下分壳后镜腿 35.1-35.3°C / 新容
  🟡 ISS-079  closed    owner=hw-lead    due=2026-11-05  
       情报检索: 采用 ARS45 的 AI 翻译眼镜拆解 + 港交所招股书直链 (封装/走线/供应链/交付)
  🟡 ISS-086  closed    owner=main       due=2026-11-05  
       netlist 收尾: NTC 改数字温度计 (I2C_A 第 4 个从设备) + USB 跨铰链保护件 (ESD/共模扼流/端接)
  🟡 ISS-105  closed    owner=hw-lead    due=2026-11-05  
       ★更正 hw-lead 分片过期值 (pcb_outline 仍 50×12 / chg_input_limit 仍 1.07-1.
  🟡 ISS-111  closed    owner=hw-lead    due=2026-11-05  
       ★[ISS-068 拆出] EVT 可靠性实测项清单 (跌落/振动/弯折/热) —— 文件缺失, 补交
  🟡 ISS-123  verified  owner=sw-lead    due=2026-11-05  
       ★S2 救砖链路全套装按 ARS45 写死 (magic AR45 / 版本串 ARS45-SW / parameter.txt 扇
  🟡 ISS-173  closed    owner=main       due=2026-11-05  
       ★★★[demo 能不能看见屏幕] 显示器背光需 12.8V@200mA ⇒ 5V 输入必须加 12V BOOST (且会撑爆 US
  🟡 ISS-153  closed    owner=hw-lead    due=2026-11-06  
       ★★订正: AR0234CS 的 I2C 地址是 0x10 (不是 0x36) + IMX415 是 0x1a ⇒ 网表注释已改, 
  🟡 ISS-121  verified  owner=hw-lead    due=2026-11-09  
       ★MEMS 麦克风与检修口磁铁的磁场/位置复核 (ISS-092 I-5/I-6) —— 磁铁 N35 ⌀4×1 在 40mm 外对
  🟡 ISS-152  closed    owner=hw-lead    due=2026-11-12  
       ★★[硬件] IMX415 上电顺序 (DVDD→OVDD→AVDD) 与 AVDD typ 2.9V: 现网表三轨同起 + LDO
  🟡 ISS-177  deferred  owner=main       due=2026-11-12  
       ★★[整机屏 · 已暂缓] 问视崖 SY049 有无非 DSC 模式版本 —— ★**视崖已不用 ⇒ 本单降级 deferred**
  🟡 ISS-017  verified  owner=mech-lead  due=2026-11-13  
       P2S 打印件实测尺寸 0 件 (AGENTS.md 要求未满足) + 彩虹纹指标缺失
  🟡 ISS-024  verified  owner=mech-lead  due=2026-11-13  
       材料选型与表面耐受缺失 (汗液/化妆品/酒精/UV 全未考虑)
  🟡 ISS-025  fixed     owner=mech-lead  due=2026-11-13  
       结构 DFM 评审缺失 (P2S 打印件 → 量产开模件的可制造性差异)
  🟡 ISS-027  closed    owner=mech-lead  due=2026-11-13  
       原型制作计划缺失 (几批打样/每批验证什么/不通过怎么回滚)
  🟡 ISS-047  verified  owner=mech-lead  due=2026-11-13  
       结构侧需复核: 『对角半角』与『垂直半视场』两个口径混用 (MECH §1.5 那张 ≤40° 的表)
  🟡 ISS-092  verified  owner=mech-lead  due=2026-11-13  
       ★镜脚末端检修口 (J_DEBUG/J_UART 够不着 → 排针装上也用不了) 的开孔/盖板方案落到 MECH 尺寸链
  🟡 ISS-188  verified  owner=sw-lead    due=2026-11-13  
       ★★DSI payload 8× 口径差 【第 6 处·收尾】: `SW/DEMO_OD_PIPELINE_SPEC.md:322`
  🟡 ISS-189  verified  owner=hw-lead    due=2026-11-13  
       ★★DSI payload 8× 口径差 【第 8/9 处·收尾】: `HW/STEP1_LANDING_LIST.md:42` +
  🟡 ISS-103  deferred  owner=mech-lead  due=2026-11-16  
       ★镜框开导光孔/导光柱 (充电灯装充电板靠 Type-C 座, 老板拍板关机时充电灯要亮)
  🟡 ISS-095  open      owner=main       due=2026-11-05   ⏰逾期
       ★[待 TI 确认] BQ25896 的 VSYS 脚是否必须接 —— 决定'电池挪镜框'回退分支要不要多两根电源 pin
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟡 ISS-109  open      owner=main       due=2026-11-05   ⏰逾期
       ★R-GEO 六问全 0 答复: ISP 吞吐余量 1.9% vs 50.7% 完全相反 (一票否决级) + 采集链/散热结论都不能
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟡 ISS-125  open      owner=main       due=2026-11-05   ⏰逾期
       ★R-GEO 六问的其余五问要按 RK3576 口径重写问询 (问 01/02/04/05/06 仍是 0 答复)
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟡 ISS-131  open      owner=main       due=2026-11-05   ⏰逾期
       ★★ISS-124/125 问询口径改 RK3572 (ISP 16M→12M, CSI 3×→2×) + 球位号问询对象改瑞芯微/
       ❌ ★逾期★ due=2026-11-05 已过, 仍 open
  🟡 ISS-134  open      owner=main       due=2026-11-06   ⏰逾期
       ★★JBD 角色收窄为波导 + ISS-016 作废 + ISS-048 光生物安全口径整个变了 (LED 点光源 → OLED 面
       ❌ ★逾期★ due=2026-11-06 已过, 仍 open
  🟡 ISS-136  open      owner=main       due=2026-11-06   ⏰逾期
       ★★J_CHG 跨铰链 pin map 与 CHARGE_BOARD_SPEC.md §5 漂移 (spec 是旧的, 网表是对的)
       ❌ ★逾期★ due=2026-11-06 已过, 仍 open
  🟡 ISS-174  open      owner=main       due=2026-11-06   ⏰逾期
       ★★[demo 触控收不到中断] display 触控的 TP_INT (pin26) 没接到 SoM 任何脚 ⇒ 触控中断收不到
       ❌ ★逾期★ due=2026-11-06 已过, 仍 open
  🟡 ISS-059  closed    owner=mech-lead  due=2026-10-28  
       打印包 P 表口径漂移 + verify_pack 文案过时 + 测量清单要区分两类孔 (mech-lead 交卷自查发现的 3 个
  🟡 ISS-069  closed    owner=sw-lead    due=2026-10-28  
       需求条目旧链路命名对齐 (SW_REQUIREMENTS 3.1 职责行 + M2-R1/M2-R3 + DISPLAY_MODE 
  🟡 ISS-073  closed    owner=sw-lead    due=2026-10-28  
       显示帧 buffer 与合成帧两行加注 (800x600 = 老板锁死的显示分辨率, 不是旧链路) —— 不许按 640x480 重
  🟡 ISS-033  closed    owner=main       due=2026-10-29  
       需求→设计→验证 追溯矩阵 (RTM) 缺失
  🟡 ISS-035  closed    owner=main       due=2026-10-29  
       来料检验 + 整机测试项 (QCP) 缺失
  🟡 ISS-036  closed    owner=main       due=2026-10-29  
       售后支持/故障诊断缺失
  🟡 ISS-037  verified  owner=sw-lead    due=2026-10-29  
       模型资产与 INT8 量化管理缺失 (权重是资产, 现在散在 sw 需求里)
  🟡 ISS-113  verified  owner=sw-lead    due=2026-11-05  
       ★RKNN_BENCH 的 B6 复现缺陷: `acc` 步单独跑会崩 (依赖 calib 步的 dataset.txt)
  🟡 ISS-066  deferred  owner=mech-lead  due=2026-11-16  
       测量清单补 H14 (temple_cage 上的 ⌀2.4 PCB 定位间隙孔独立量测行) + measurements.yaml
  🟡 ISS-076  deferred  owner=mech-lead  due=2026-11-16  
       新容量口径的尾巴 3 处 (3.1 对标表重量分两配置 / verify_budget.py 的 DOC_WEIGHT 同步 / 1

❌ 违规 32 条
```
## 4. 阶段门 (G0-G4)
```
==========================================================================
阶段门 · Stage Gate —— 项目有序推进的唯一依据
==========================================================================

【G0】纸面冻结 (需求/口径/方案定型)  —  ✅ 通过   缺 0 项
      为什么要这一关: 所有数字还停在推算层; 这一关锁死口径, 后面才不会整体返工

【G1】原理图 / PCB 定稿  —  ⏸️  当前关   缺 1 项
      为什么要这一关: ARS45 纸面资料必须齐全, 否则画出来是废纸 (pitch 装不下 = 直接否决选型)
      ▸ 缺实测数据 (1):
          - PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)

【G2】结构样机装配 (打印件 + 电池 + 光机位姿)  —  ⏸️  已延后 (当期不做)   缺 3 项
      为什么要这一关: 镜框/镜脚装不装得下, 只有打出来才知道; 0 件实测 = 这一关不能过
      ★延后理由: 老板 11-02 19:25「硬件优先, **结构不考虑**」(结构单冻结不投人; demo 形态 = 一块主板 + sensor 模组 + 屏幕模组 + 板内 FPC, 跨铰链取消, 不装电池) + 11-04 10:09「打印环境暂时不需要」⇒ ★**整关挪到整机阶段**; 触发重开: ① 波导/光机/镜框路线定下来 ② 老板重新要结构样机
      ▸ 问题单未闭环 (3):
          - ISS-004 [deferred] 波导未选型 (等 JBD) → 卡镜框打印开工
          - ISS-013 [deferred] 波导未选型 → 缺 2D 外形图/容差角/彩虹纹 → 镜框不能开工
          - ISS-016 [deferred] 走鹃Ⅱ 长宽高未知 → 光机位姿/干涉检查做不了
      ▸ 本关内已延后的实测项 (3):
          - M-PRINT P2S 打印件实测尺寸 (关键配合尺寸) → 延后: 整机阶段 (结构开工时)
          - M-FIT 电池 / PCB / 光机 装配干涉检查 → 延后: 整机阶段 (结构开工时)
          - M-WEIGHT 整机实测重量 → 延后: 整机阶段 (结构开工时)

【G3】上电联调 + 硬指标实测  —  ⏳ 未到   缺 4 项
      为什么要这一关: 两个硬指标 (端到端 60ms / 皮肤 43°C) 至今 0 实测; 这一关不过, 项目没有交付物
      ▸ 缺实测数据 (4):
          - M-NPU NPU 纯硬件耗时 (yolov5 INT8 单帧, 不含前后处理) (ms)
          - M-E2E 端到端实测 (按 Q1 拍板的口径) (ms)
          - M-POWER 整机功耗 (持续满载 / 待机 两档) (W)
          - M-DIZZY 眩晕/拖影主观验收 (连续快速头部转动 + 快速走动 + 视线切换, 观察 5 分钟) (主观)
      ▸ 本关内已延后的实测项 (1):
          - M-BATT 续航实测 (按 Q4 拍板的口径) → 延后: 整机阶段 (demo 板没有电池)

【G4】体验验收 (DoD 全过)  —  ⏳ 未到   缺 49 项
      为什么要这一关: 所有问题单关闭 + 质量门全绿 + DoD 清单逐条签
      ▸ 问题单未闭环 (49):
          - ISS-004 [deferred] 波导未选型 (等 JBD) → 卡镜框打印开工
          - ISS-013 [deferred] 波导未选型 → 缺 2D 外形图/容差角/彩虹纹 → 镜框不能开工
          - ISS-016 [deferred] 走鹃Ⅱ 长宽高未知 → 光机位姿/干涉检查做不了
          - ISS-025 [fixed] 结构 DFM 评审缺失 (P2S 打印件 → 量产开模件的可制造性差异)
          - ISS-038 [open] 【缺角色】工业设计 (ID/CMF/佩戴舒适度) 无人负责 —— 需老板拍板是否
          - ISS-040 [deferred] 打印与量测条件不具备 (打印机跨网段不可达 + 无切片器/量具) → M-PRI
          - ISS-041 [open] ★★[当前 demo 板] 测试条件缺失 ⇒ G3 那一关不可判通过 (★202
          - ISS-048 [deferred] 光生物安全所需的光机参数缺失 (LED 波长/亮度/光通量/辐亮度) —— 已并
          ... 另 41 条

⏸  延后到整机/量产阶段的实测项 (**没删, 只是不在当期验收范围**):
    - M-SKIN: 整机/量产阶段做贴皮肤稳态温度 (43°C 是 ISO 13732-1 烧伤红线) —— 触发: 整机样机贴皮肤测试
    - M-CHRG: 整机/量产阶段做充电场景皮肤温度 (推算 75.1°C 属烫伤风险) —— 触发: 同上
    - M-OPTIC: 光机逐帧延迟绝对值 —— 老板 10-25 决定不采购高速相机/示波器, 改由 M-DIZZY (主观) 替代

▶ 当前在 **G1 原理图 / PCB 定稿**, 还差 **1** 项才能进下一关 (G2 结构样机装配 (打印件 + 电池 + 光机位姿))
   ★**已跳过延后关**: G2 (当期不做, 缺口 3 项留着, 到整机阶段回来)
```
## 5. 执行就绪度 (组织与机制)
```
==============================================================================
  执行就绪度体检 · Readiness  (机械判定, 不凭印象)
==============================================================================

【全局机制】❌ 未就绪 (1 项不过)
   ✅ 共享状态源可用 (merge rc=0)
   ✅ gate ↔ merge 自动对账一致
   ❌ 问题闭环门 0 违规
        issue_check rc=1 (字段/状态机/验证分离/逾期/双向覆盖)
   ✅ 阶段门可判 (G0-G4)
   ✅ 每日巡检可跑 (漂移检测)
   ✅ 推进器可算下一步
   ✅ 手动看板可出图
   ✅ 框架裁剪基线存在 (74 条)
   ✅ 星型守卫在 CLI 入口
   ✅ 分片原子写工具可用

【项目总工 (main / moli)】❌ 未就绪 (3 项不过)
   ❌ AGENTS.md 存在且有职责清单
        /home/yuewuya/.openclaw/workspace/AGENTS.md
   ✅ 写入边界明确 (不许改什么)
   ❌ 交付质量标准在位 (B1-B6 + 证据分级 + 自证)
        缺块即退回, 交接单模板 v2
   ❌ 禁横向直聊已写明
        硬规则写进 AGENTS.md
   ✅ 项目专属 skill 已装
   ✅ 分片非空且有 status/artifacts
   ✅ 外部等待已标 waiting_on+due
   ✅ 决策包 (Q1/Q4/Q17)
   ✅ 外发草稿已就绪 (只备不发)

【硬件总工 (hw-lead)】❌ 未就绪 (4 项不过)
   ❌ AGENTS.md 存在且有职责清单
        /home/yuewuya/.openclaw/workspace-hw/AGENTS.md
   ❌ 写入边界明确 (不许改什么)
        禁止项写进每次启动都读的 AGENTS.md
   ❌ 交付质量标准在位 (B1-B6 + 证据分级 + 自证)
        缺块即退回, 交接单模板 v2
   ❌ 禁横向直聊已写明
        硬规则写进 AGENTS.md
   ✅ 项目专属 skill 已装
   ✅ 分片非空且有 status/artifacts
   ✅ 外部等待已标 waiting_on+due
   ✅ 硬件模块拆解 + 电源树
   ✅ EMC 预评估 (画板前)

【软件总工 (sw-lead)】❌ 未就绪 (4 项不过)
   ❌ AGENTS.md 存在且有职责清单
        /home/yuewuya/.openclaw/workspace-sw/AGENTS.md
   ❌ 写入边界明确 (不许改什么)
        禁止项写进每次启动都读的 AGENTS.md
   ❌ 交付质量标准在位 (B1-B6 + 证据分级 + 自证)
        缺块即退回, 交接单模板 v2
   ❌ 禁横向直聊已写明
        硬规则写进 AGENTS.md
   ✅ 项目专属 skill 已装
   ✅ 分片非空且有 status/artifacts
   ✅ 外部等待已标 waiting_on+due
   ✅ 软件需求拆解 + 延迟预算
   ✅ EVT 模板 + 联调计划

【结构总工 (mech-lead)】❌ 未就绪 (4 项不过)
   ❌ AGENTS.md 存在且有职责清单
        /home/yuewuya/.openclaw/workspace-mech/AGENTS.md
   ❌ 写入边界明确 (不许改什么)
        禁止项写进每次启动都读的 AGENTS.md
   ❌ 交付质量标准在位 (B1-B6 + 证据分级 + 自证)
        缺块即退回, 交接单模板 v2
   ❌ 禁横向直聊已写明
        硬规则写进 AGENTS.md
   ✅ 项目专属 skill 已装
   ✅ 分片非空且有 status/artifacts
   ✅ 外部等待已标 waiting_on+due
   ✅ 空间预算 + 散热模型
   ✅ 打印包 + 测量清单

── 项目级终判 ───────────────────────────────────────────────────────
  📄 纸面阶段 (G0 纸面冻结 / G1 原理图 / G2 结构样机准备): ❌ 机制有未过项
     → 判据: 4 个角色机制全绿 + 质量门/问题门/阶段门/推进器可用 + 框架裁剪基线在位
     → 当前卡点: 老板 7 条决策 + 原厂/JBD 外部; 内部可自行推进 70 条
  🔧 样机阶段 (G3 上电联调 + 硬指标实测): ❌ 不就绪
     → 实测 0/4 项 (另有 7 项已延后到整机阶段) | 无板 / 无打印环境 / 无独立验证方
     → 阶段门判:    ★**已跳过延后关**: G2 (当期不做, 缺口 3 项留着, 到整机阶段回来)

  结论: **四个角色已具备执行条件** (职责/边界/交付标准/协作机制/质量门/推进器 全部到位)。
        **但"执行"只能推进到纸面阶段** —— G3 需要的实物/设备/实测一条都没有。
==============================================================================
```
## 6. Agent 配置审计 (能否开工)
```
==============================================================================
  Agent 配置审计 · 能否开工
==============================================================================

【A 配置本身】✅ 2/2 通过

【B Agent 定义】✅ 20/20 通过

【C Workspace】✅ 12/12 通过

【D Skill 加载】✅ 12/12 通过

【E 通信拓扑】✅ 13/13 通过

【F 三层守卫】✅ 8/8 通过

【G 运行时能力】✅ 14/14 通过

✅ 结论: **81/81 项配置全部满足开工条件**
   4 个 agent 可正常 spawn / 读 skill / 写分片 / 跑门禁; 三层守卫在位; 巡检与推进 cron 在位。
==============================================================================
```
## 7. 决策与需求账
- 老板已拍板决策 **0** 条 → `docs/DECISIONS.md`
- 需求总数 **244** 条 (已答 157 / 未闭合 87)
- 冲突 0 · 门禁违规 0

## 8. 未闭环的高危问题
| id | 责任方 | due | 标题 |
|---|---|---|---|
| ISS-074 | main | 2026-10-29 | ★开始画硬件原理图 V1 (8 页图页 + 完整 netlist + KiCad 可导入 .net) —— 球位号统一用 TBD 占位, 原厂回信后只填球号 |
| ISS-147 | main | 2026-11-04 | ★★★[demo P0] 恢复 RKNN 构建环境 + 证明 rk3572 是 rknn-toolkit2 2.3.2 的合法 target —— 不解决这条, 软件侧一步都动不了 |
| ISS-119 | main | 2026-11-05 | ★★换芯定案 + 迁移方案 (A7/A8): 选哪颗 + 网表/原理图/BOM 重做清单 + 为 RK3588 预留的可执行后手 |
| ISS-139 | main | 2026-11-05 | ★★[内部, 与选谁无关] ISP tuning 立项: 两个候选 sensor 都没有现成 IQ 文件 ⇒ 这笔账必须自己排 |
| ISS-145 | sw-lead | 2026-11-05 | ★★★★[demo 关键路径 #2] demo 板 OD 管线打通规格: yolov5n INT8 → RKNN → 画框 → 视涯 049 显示 |
| ISS-155 | main | 2026-11-06 | ★★★★[demo 头号卡点] rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 target 转的 .rknn 能否在 RK3572 上跑通 (板端验证) —— 且板子当前不可达 |
| ISS-160 | main | 2026-11-06 | ★★★[自己画图] demo 主板图纸链: KiCad 10 工具链(免 root AppImage) + 参数化生成器 + DRC 门禁(已 rc=0) ⇒ 剩下: 原理图/密集布线/打样 |
| ISS-162 | main | 2026-11-13 | ★★★[硬件 · 画板前必须] 网表按真实器件规格重出: FPC 座 31p/0.3mm + 40p/0.5mm + SOM 400 脚 BTB + 电源输入改 5-13V |
| ISS-087 | sw-lead | 2026-10-29 | 模型许可未清 (L1 许可[0数据] + L4 AGPL-3.0 商用受限) + ARS45 板端模型 0 个 → 量产评审放行门禁 |
| ISS-090 | sw-lead | 2026-10-29 | ★软件侧交叉评审 (时序/信号/电源时序) + TMP117 测点物理位置 + 跨铰链 USB 烧录可行性 |
| ISS-101 | sw-lead | 2026-10-29 | ★模型许可: 唯一许可干净候选 (Apache-2.0) 的 NPU 可转换性 = 0 数据 → 量产可用模型清单为空 |
| ISS-110 | sw-lead | 2026-10-29 | ★RKNN 转换链实测 (RK3576 资料维度实测 + 端到端 ≤60ms 判定) —— 已交付并验收 |
| ISS-146 | boss | 2026-11-03 | ★★[等老板一句] demo 板形态: 模组+转接板 (我的建议) 还是 自制整板? —— 决定 PCB 与周期 |
| ISS-151 | main | 2026-11-04 | ★★[硬件优先] 替代料候选清单: 每类物料 ≥3 个公开在售替代品 + 来源/规格/数据来源评分 ⇒ 让「都试过了」可核查 |
| ISS-156 | main | 2026-11-04 | ★★[demo 供应链] 自研主板的三件前置选型: camera 模组 / 屏模组 / RK3572 核心板 (★主板的 FPC 座由模组倒逼) |
| ISS-038 | boss | 2026-11-05 | 【缺角色】工业设计 (ID/CMF/佩戴舒适度) 无人负责 —— 需老板拍板是否加第 4 个总工 |
| ISS-041 | boss | 2026-11-05 | ★★[当前 demo 板] 测试条件缺失 ⇒ G3 那一关不可判通过 (★2026-11-04 09:57 起: 不含热电偶/假皮肤, 老板已定 demo 板不考虑温度) |
| ISS-060 | boss | 2026-11-05 | 产品件三条几何待老板裁决 (压垫吸收量零余量 / 非对称方向 / 压垫槽区板厚小于 FDM 最小壁) —— 打印包转绿不等于解 A 收口 |
| ISS-063 | boss | 2026-11-05 | 显示端 120 度到 30 度的映射方式 (看得广但糊 vs 看得清但窄) —— 120 度这个卖点对用户可见吗 |
| ISS-080 | sw-lead | 2026-11-05 | S2 救砖链路 (进 BOOT 模式 → 厂商下载工具识别 → 刷回来) 必须实测 —— 量产一票否决项 |
| ISS-097 | main | 2026-11-05 | ★"关机"语义: 硬件断电通路 (负载开关) + 真关机拓扑 + 功耗预算 V3 |
| ISS-102 | main | 2026-11-05 | ★[待原厂] 追加问 4 条: AON 域静态电流 / USB VBUS detect 脚 / TPS62130A PG 极性 / BQ25896 VSYS 是否必接 |
| ISS-106 | boss | 2026-11-05 | ★新增渠道: 经酷芯微代理转达 (老板 10-28 找到代理) —— 代理信 + 3 份可转发附件已就绪 |
| ISS-114 | main | 2026-11-05 | ★★换芯片选型总单: 国内 TOP10 厂商 × TOP1~5 芯片 × 9 项打分 (老板 10-29 09:59 改令) —— 正式弃用酷芯微 |
| ISS-116 | main | 2026-11-05 | ★★工作方式改造: 老板任务先落 GitHub 总表 + token 守护 (老板 10-29 09:59 亲自要求) |
| ISS-122 | main | 2026-11-05 | ★★BGA 逃线层数: ★两套模型结论相反 (9 层 vs 3 层) ⇒ 破没破 4-6 层锁是 [0数据] 不是结论 —— 必须问 PCB 厂 DFM 报告 |
| ISS-124 | main | 2026-11-05 | ★★[待瑞芯微/RK3576 模组厂] ISP MP/s 吞吐上限 + ISP 动态功耗 vs 吞吐曲线 (2 问, 一票否决级的剩余部分) |
| ISS-126 | main | 2026-11-05 | ★★板厚档位未定 ⇒ 检修口净空只有 4.90 那一档过 (1.22mm 档净空 4.48 破 4.50 硬要求) |
| ISS-127 | main | 2026-11-05 | ★★★脱模斜度致镜脚 H 链最坏 −0.577mm ⇒ 几何上做不出来 (不是余量紧张, 是不可行) —— 量产架构必须改 |
| ISS-128 | main | 2026-11-05 | ★★主控换 RK3572 ⇒ 板面积账 + 逃线层数全部重算 (封装 FCCSP550L 14.3×15.5mm / 550 球, 比 RK3576 小) |
| ISS-129 | main | 2026-11-05 | ★★★RK3572 (4 TOPS) 板端纯 NPU 实测 ⇒ 端到端 60ms 硬指标生死判定 (★T2 翻案条件推算已命中) |
| ISS-130 | main | 2026-11-05 | ★★★RK3572 功耗 670mW (原厂口径) vs 贴皮肤 43°C 红线 —— 从「待定」变「可判」 |
| ISS-138 | boss | 2026-11-05 | ★★★[要老板一句拍板] sensor 模式选路: OV04C10 @1080p60 ⇒ 镜头/FOV/角分辨率/快门 四个代价要选一边 |
| ISS-164 | main | 2026-11-05 | ★★[等老板一句] demo 精度验收线: yolov5n F1 0.2927 差 0.0073 不达 0.30 门槛, 换 yolov5s 过线但 60ms 退到 62.67~64.18ms ⇒ 两条路都不平 |
| ISS-169 | main | 2026-11-05 | ★★[demo 板可制造性] demo 主板的边界已定 (Type-C 供电 · 不装电池 · 板上只有这一块) + SoM 座的 pin1 排向待查证 + 15 个器件的封装脚号待落定 |
| ISS-132 | main | 2026-11-06 | ★★★[决定性] 视涯 0.49" 1920×1080 是单色还是全彩? —— 这题决定产品定义 (检测框能不能上色) |
| ISS-133 | main | 2026-11-06 | ★★★显示架构变更: '屏' ≠ '光机' ⇒ 必须新增一级耦合光学 ⇒ 镜框光学腔体/分光器/整机空间全部重算 |
| ISS-137 | main | 2026-11-06 | ★★[可执行, 一行代码的活] 把「显示合成段」从 T_FIXED 里单独打点 —— 它是 RK3572 + 1920×1080 下 60ms 成败的关键未知数 |
| ISS-172 | main | 2026-11-06 | ★★[选型待裁] 负载开关 U_PWR_SW / U_EN_SW: 原厂在售型号的判据互斥 (RON vs IQ vs 反向阻断) |
| ISS-179 | sw-lead | 2026-11-06 | ★★[手机测端到端] 显示画面烧帧计数器/时间码 + 手机慢动作测端到端延时作业指引 |
| ISS-062 | hw-lead | 2026-11-09 | R-GEO-2 四问转原厂/镜头厂 (边缘畸变区是检测价值最高处 / 4-lane MIPI / ISP 吞吐余量 98.1% / scaler 能否填黑边) |
| ISS-099 | hw-lead | 2026-11-09 | ★J_CHG 选型与 FPC 加工图要求 (触点额定 ≥0.35A / 分段铜厚 固定段2oz·弯折段1oz / 内层地 keep-out / pin10 改 NTC 专用回流) |
| ISS-118 | hw-lead | 2026-11-09 | ★板宽 15mm → 30mm 的硬件连带重算 (板框/网表/面积/逃线/跨铰链排布) —— 老板 10-29 19:16 放宽 |
| ISS-187 | main | 2026-11-12 | ★ISS-137 护栏两个洞 (M2 默认参数踢 TX / M3 无护栏钉 TX 绝对值) ⇒ 加护栏⑧⑨⑩ ⇒ ★已做完, 待 sw-lead 复验 |
| ISS-085 | mech-lead | 2026-11-13 | ★USB 跨铰链方案落地 (Type-C 留镜框充电板 + USB 差分跨铰链到镜脚主 PCB) + 跨铰链 USB 可靠性要求 + 连接器 pin/型号/pitch 结构复核 |
| ISS-091 | mech-lead | 2026-11-13 | ★跨铰链充电电流 1.0-1.5A 的载流/压降/发热核算 + J_CHG (1×10) 机械可行性 (MECH-B7 的后续) |
| ISS-096 | main | 2026-11-13 | ★复位释放时刻不由已画器件决定: 监督器只监督 V_SOC_IO 不监督 V_CORE, DC-DC 的 PG 只到测试点不参与复位, 9 颗供电器件的 EN/SS 与监督器 CT 脚在网表里根本没有 |
| ISS-098 | main | 2026-11-13 | ★SoC 侧没有 USB VBUS 连接 (网表只有 D+/D−) ⇒ USB 枚举前提缺失, S2 救砖链路成立性未验; 且 CONN_USB 只有 1 个 GND pin (违反 ISS-085 自定规则) |
| ISS-100 | mech-lead | 2026-11-13 | ★板宽 12mm → 15mm 的结构侧连带 (镜脚腔体/骨架长度/PCB 定位孔位/面积缺口 300mm² 复核) |
| ISS-171 | main | 2026-11-13 | ★★[IC 规格落定] 三个"我的假设"被原厂 datasheet 推翻 (已改网表) + 5 条仍未查到 |
| ISS-185 | mech-lead | 2026-11-13 | ★ISS-107 同型问题 (第二面): 没有对手方的过期值 —— 本域 8 条 claim 的值停留在 10-28 基线, 合并器静默放过 |
| ISS-186 | hw-lead | 2026-11-13 | ★DSI payload 8× 口径差: 6 处「373/246 Mbps」实为 2986/1475 Mbps ⇒ 依据虚到 8 倍 ⇒ 下次有人拿它反推 TX 下限, 7.776ms 会塌成 ~0.97ms |
| ISS-190 | sw-lead | 2026-11-13 | ★SW 侧时序/电源评审与机械复核器口径漂移 ⇒ SW_TIMING_REVIEW 锚在 476 行旧网表 (现行 513 行) ⇒ F4/F8 结论已被现网表推翻 ⇒ timing_check.py 实读网表 (现为手抄常量 + 假绿自测) |
| ISS-191 | sw-lead | 2026-11-13 | ★P0 (来自 ISS-190 复评): 首台板可能因 RESET_N 恒低而无法启动 —— PG_AND 只剩 10k 上拉, 无人拉低 ⇒ Q_AND 栅极恒高 ⇒ 导通 ⇒ RESET_N 恒被拉到地 |
| ISS-192 | mech-lead | 2026-11-13 | ★★结构侧(MECH)机械复核器全线仍钉在已作废的 12/15mm 板宽 ⇒ 现在的绿灯不是关于现行板子说的(pinset2_mech_check rc=0 但那是块不存在的板) + PIN-SET-2 孔位 Y 在 hw-lead 自己两个产物里差 7.50mm(打印包已按套A做出, 若 PCB 按套B钻则装不进骨架) ⇒ 迁到 60×30 + 仲裁成一份权威表 |
| ISS-120 | sw-lead | 2026-11-30 | ★S2 救砖链路板端实测 (量产一票否决项) —— 方案+自检已闭环 (ISS-080), 待 EVT 有板后真跑 (EVT-8/BR-01) |
