# 项目状态快照 (自动生成)
> 生成时间: **2026-11-24 15:31** | 数据源: `projects/smart_glasses/STATE.yaml` + `state/issue_log.yaml` + 各门禁实时输出
> 本文件由脚本生成, **数字与真源一致** (不是手写)。
## 1. 一屏总览
```
产出 858 | 阻塞 43 (高危 33) | 未闭合需求 377 | 冲突 0 | 健康度 red
```
## 2. 交付质量门 (Q1-Q5)
```
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1239 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    482 条
   sw-lead    356 条
   mech-lead  401 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 155/582  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 243 条, 其中 58 条真对上了别人的需求 key
   hw-lead    被答 56/292 | 我答 86 条(有效 31) | 产出 335 | 阻塞 7
   sw-lead    被答 41/104 | 我答 72 条(有效 6) | 产出 294 | 阻塞 15
   mech-lead  被答 58/186 | 我答 85 条(有效 21) | 产出 214 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 51 条 | **全局 46 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 377 条**
   ✅ 与 merge.py 自对账一致 (等外部 46 / 等总工 377)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 10 个
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']
      iss105_jchg_rfq_release: 发起方 ['main', 'hw-lead']
      iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice: 发起方 ['main', 'mech-lead']
      iss236_boss_v_decision: 发起方 ['main', 'hw-lead']

【Q5 硬指标覆盖】 0/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']
   sw-lead    0/5 类: []
   mech-lead  1/5 类: ['镜腿/镜脚厚度(mm)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 10/10 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ✅ 钉板闸⑩ 板侧项全集重跑幂等闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 216 条需求确实还没人答 (等另一个总工)
   · sw-lead: 49 条需求确实还没人答 (等另一个总工)
   · mech-lead: 111 条需求确实还没人答 (等另一个总工)

==========================================================================
```
## 3. 问题闭环门
```
==========================================================================
问题闭环门 · Issue Gate
==========================================================================
登记问题 389 条 | 状态: closed=97 deferred=15 verified=249 open=16 fixed=6 fixing=6
  ├─ 内部可自行推进: 358 条 | 外部依赖 (等老板/原厂/JBD): 31 条
  ├─ 逾期未闭环: 19 条
  └─ 未闭环 blocker 级: 10 条

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
  🔴 ISS-119  verified  owner=main       due=2026-11-05  
       ★★换芯定案 + 迁移方案 (A7/A8): 选哪颗 + 网表/原理图/BOM 重做清单 + 为 RK3588 预留的可执行后手
  🔴 ISS-139  verified  owner=sw-lead    due=2026-11-05  
       ★★[内部, 与选谁无关] ISP tuning 立项: 两个候选 sensor 都没有现成 IQ 文件 ⇒ 这笔账必须自己排
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
  🔴 ISS-162  verified  owner=main       due=2026-11-13  
       ★★★[硬件 · 画板前必须] 网表按真实器件规格重出: FPC 座 31p/0.3mm + 40p/0.5mm + SOM 400
  🔴 ISS-207  verified  owner=sw-lead    due=2026-11-18  
       ★★★★[demo 头号卡点·自己查版] ISS-155 拆块: rknn-toolkit2 最新版到底支不支持 rk3572 ta
  🔴 ISS-181  deferred  owner=hw-lead    due=2026-11-20  
       ★★★[最高优先级 · 老板 11-04 19:10 指示] 自研 demo 主板: 从骨架布到**可下单** (unconnect
  🔴 ISS-263  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·软件/工具链侧·demo 头号卡点·内部活] ★★★★[ISS-155 blocker 的 E-11/E-12] ★*
  🔴 ISS-353  verified  owner=sw-lead    due=2026-11-24  
       ★★[★新主线·PCB 线·模型链·rk3572 目标口径清账·纯口径·零写板] ★★【ISS-263 (2026-11-17) 已
  🔴 ISS-160  open      owner=main       due=2026-11-20   ⏰逾期
       ★★★[自己画图] demo 主板图纸链: KiCad 10 工具链(免 root AppImage) + 参数化生成器 + DRC
       ❌ ★逾期★ due=2026-11-20 已过, 仍 open
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
  🟠 ISS-122  deferred  owner=main       due=2026-11-05  
       ★★BGA 逃线层数: ★两套模型结论相反 (9 层 vs 3 层) ⇒ 破没破 4-6 层锁是 [0数据] 不是结论 —— 必须问
  🟠 ISS-124  verified  owner=sw-lead    due=2026-11-05  
       ★★[待瑞芯微/RK3576 模组厂] ISP MP/s 吞吐上限 + ISP 动态功耗 vs 吞吐曲线 (2 问, 一票否决级的剩
  🟠 ISS-127  verified  owner=mech-lead  due=2026-11-05  
       ★★★脱模斜度致镜脚 H 链最坏 −0.577mm ⇒ 几何上做不出来 (不是余量紧张, 是不可行) —— 量产架构必须改
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
  🟠 ISS-132  verified  owner=main       due=2026-11-06  
       ★★★[决定性] 视涯 0.49" 1920×1080 是单色还是全彩? —— 这题决定产品定义 (检测框能不能上色)
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
  🟠 ISS-118  verified  owner=hw-lead    due=2026-11-09  
       ★板宽 15mm → 30mm 的硬件连带重算 (板框/网表/面积/逃线/跨铰链排布) —— 老板 10-29 19:16 放宽
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
  🟠 ISS-191  verified  owner=sw-lead    due=2026-11-13  
       ★P0 (来自 ISS-190 复评): 首台板可能因 RESET_N 恒低而无法启动 —— PG_AND 只剩 10k 上拉, 无
  🟠 ISS-192  verified  owner=mech-lead  due=2026-11-13  
       ★★结构侧(MECH)机械复核器全线仍钉在已作废的 12/15mm 板宽 ⇒ 现在的绿灯不是关于现行板子说的(pinset2_mec
  🟠 ISS-194  verified  owner=hw-lead    due=2026-11-13  
       ★★PIN-SET-2 孔位表【套B ⇒ 套A】: hw-lead 自己 5 个产物里 4 个写套A, 只有 pcb60x30_ch
  🟠 ISS-198  verified  owner=hw-lead    due=2026-11-13  
       ★★[主线内·原理图侧·内部活] `PIN_REALITY_GAP.md` 里 29 个 `[0数据]` 的真实脚数 ⇒ 根因 = 
  🟠 ISS-205  verified  owner=sw-lead    due=2026-11-14  
       ★★[主线内·原理图侧·内部活] ★★KiCad 导出 BOM 里 186 个位号带 `?` (★板厂看到的位号与丝印对不上★) ⇒
  🟠 ISS-143  closed    owner=mech-lead  due=2026-11-16  
       ★★结构侧新口径: 边框遮挡角必须进 FOV 余量账 (凹进 1.0mm = 1.91° 遮挡, 吃掉"正前方那一侧") ⇒ 镜框上
  🟠 ISS-211  verified  owner=hw-lead    due=2026-11-18  
       ★★[主线内·原理图/网表侧·内部活] 现行网表自身 4 处自相矛盾 (I2C_A 上拉行 vs 器件行 / BAT_DET 分压链
  🟠 ISS-212  verified  owner=sw-lead    due=2026-11-18  
       ★★★[demo 头号路径·自己查版·软件/显示侧] demo 显示侧口径重锚到 Waveshare 2.8" (480×640 ·
  🟠 ISS-307  verified  owner=hw-lead    due=2026-11-18  
       ★★[主线内·选型研究类·内部活] ★★【板那一趟的 ESD 选型轴: 老板 ①② 两个字母 (W-2 补不补 D− / W-1b·
  🟠 ISS-308  verified  owner=hw-lead    due=2026-11-18  
       ★★[主线内·分析/作业包类·内部活] ★★【「板那一趟 S8 (unconnected 45 → 0)」的可达性判决书: 残余 2
  🟠 ISS-102  verified  owner=main       due=2026-11-19  
       ★[待原厂] 追加问 4 条: AON 域静态电流 / USB VBUS detect 脚 / TPS62130A PG 极性 / 
  🟠 ISS-172  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·硬件选型/官方口径侧·内部活] ★**负载开关 U_PWR_SW / U_EN_SW 选型证据矩阵** (★网表 L5
  🟠 ISS-209  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构侧·内部活] 正中区光学腔体按眼盒 A_e ≤ 62 mm² + d=15–20mm 重排 (★ISS-208 §
  🟠 ISS-210  verified  owner=sw-lead    due=2026-11-19  
       ★★★[demo 头号卡点·自己查版·续] ISS-129/155 收口: 端到端 60ms 生死判定链 (补 ISP 段打点 + 
  🟠 ISS-213  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构侧·内部活] 结构侧 54 项交叉复核逐条定性 (17 条 FAIL 挂在 rc=0 且不在每日巡检链上 ⇒ 隐形
  🟠 ISS-214  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] 网表/规格自身矛盾第 2 轮 (USB 串阻双值 / P9 页 21p vs 22p / S
  🟠 ISS-215  verified  owner=sw-lead    due=2026-11-19  
       ★★★[demo 头号路径·自己查版·软件/时序侧] demo 板 60ms 生死判定链的显示侧口径重锚: 从退役的整机 1920×
  🟠 ISS-216  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构侧·内部活] MECH_BUDGET 充电耗散口径统一: 线性充电 IC 0.8W → 板上真实 buck (BQ
  🟠 ISS-217  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] 12 组网表/规格自相矛盾 (ISS-211 四条 + ISS-214 八条) ⇒ 汇成【整
  🟠 ISS-218  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构侧·内部活] 打印包第三档试样落地 (10.50×4.80 FDM 直成型 + 10.25×4.55 金属·CNC
  🟠 ISS-219  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构侧·内部活] 镜框正中区第 2 轮重排: C-6 分光件按 A_e≤62mm² 放大 (光束 8.885 ⇒ 平板
  🟠 ISS-220  verified  owner=hw-lead    due=2026-11-19  
       ★★★[主线内·原理图/网表侧·内部活] 【整链重出 第 2 步 · 原理图侧落表执行】把 ISS-217 作业包 28 条里「不依
  🟠 ISS-221  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·软件/时序侧·内部活] demo 屏 (2-lane@480×640) 自己的 60ms 预算真源脚本 `SW/too
  🟠 ISS-222  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构侧·内部活] ISS-219 的 C-6 / C-7 / C-8 三条「只报不改」落进结构真源: C-6 分光件 
  🟠 ISS-223  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] ISS-220 收尾 (补落 3 条分片声明) + 落表第 2 批 (★V-1 已由项目总工
  🟠 ISS-224  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构侧·内部活] `MECH/check_demo_struct_truth.py` 三组失配的再基线化: ISS-2
  🟠 ISS-225  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·软件/工具链侧·内部活] SW 侧 md5 基线过期 (`SW/tools/check_demo_panel_spec
  🟠 ISS-226  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·软件/光生物安全判据侧·内部活] 光生物安全的「出瞳白场辐亮度最大值」在 SW 侧亮度控制策略里可判化: 蓝光通道占比
  🟠 ISS-227  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构/热路口径侧·内部活] ISS-222 产物的 C-7b 物理口径错修正: P3 把「镜框上沿 120×30 打印
  🟠 ISS-228  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·硬件选型/官方口径侧·内部活] RK3572 GPIO0 (I2C0_SCL=GPIO0_B0 球 1K21 / I2
  🟠 ISS-229  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构/热路侧·内部活] 充电时皮肤侧温度【按改正后的系数】重算 (★0.822 是倒方向的旧值 ⇒ 「390Ω 档 4
  🟠 ISS-230  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] 落表第 3 批【逐字改法映射 v2】(★把 21 条未落表从「等老板拍板」变成「拍完就落」★
  🟠 ISS-231  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·软件/门禁侧·内部活] SW 侧 R6 锚点重锚 (★ISS-223 落表后【按设计】变红的一盏灯, 走 ISS-22
  🟠 ISS-232  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] 板↔网表【焊盘级等价】门禁红的 2 处「多余」(C_VBUS_GND pad1=GND / 
  🟠 ISS-233  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] `--expect-resolved` 21 条未落表 ⇒ 逐条归因 + 【不依赖老板拍板的
  🟠 ISS-234  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·软件/接口侧·内部活] 【关机 / 待机 / 关机充电指示灯】三条口径 ⇒ 出【真断电 vs 深睡关机 × demo 
  🟠 ISS-235  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·软件/接口侧·内部活] ★**ISS-233 落表把 SW 侧 3 条断言打成过期红** ⇒ 订正 `timing_c
  🟠 ISS-236  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] ★**把 ISS-233 的【拍板即落清单】做成参数化【一键落表器】(V-2 / V-3 /
  🟠 ISS-237  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] ★**P2 屏口径自相矛盾** (STEP1_PARTS_SPEC.md §0/§3 = 4
  🟠 ISS-238  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构/判据侧·内部活] ★★`MECH/display_biosafety_v2_check.py` C1 红灯 (走
  🟠 ISS-239  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表侧·内部活] ★**TPS7A20 族 7 颗 LDO 的引脚功能名在脚表里串号** (★pin4 的 I
  🟠 ISS-240  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·结构/判据侧·内部活] ★★跨铰链 FPC 几何账【三套口径】互相打架 (★脚本「收敛版」= 硬编码 16p/20p 
  🟠 ISS-257  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/选型侧·落表执行·内部活] ★★G1a-7「选型已落表」: ★**BOM 里 14 件必装器件 value 至
  🟠 ISS-260  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·原理图/网表/选型侧·工具自测·内部活] ★★★**`state/land_v_values.py` 的 V-2 落表
  🟠 ISS-265  verified  owner=hw-lead    due=2026-11-19  
       ★★★[★新主线·PCB 侧·布线死因·内部活] ★★★**7 条布线臂全打死同样 3 条差分腿 ⇒ 布局级线索 ⇒ 出【根因对照表
  🟠 ISS-283  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·HW/落表侧·内部活] ★★【三件落表 + 一个工具接口死锁】★★ ★**B1: V-2 (A3) 落表被行号锚点守卫
  🟠 ISS-284  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·门禁/台账机制·内部活] ★★【P10 落地: SW 台账 `hard_protected` 怎么合法跟上「
  🟠 ISS-288  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·门禁口径收口·内部活] ★★【把 ISS-285 设计好的补丁真正落进 `SW/tools/timing_c
  🟠 ISS-310  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·板框口径对照类·内部活] ★★【板框口径「两套并存」的代价对照 + 机器可判的可行域表 ⇒ 交 main
  🟠 ISS-311  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·HW 侧·产出链重出清单类·内部活] ★★【「板只改一次」那一趟要重出哪些件: C1 焊盘级等价差 2 个 (网表 4
  🟠 ISS-312  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·判据修复类·内部活] ★★【ISS-309 的 need 落地 (★main 已拍板: 修法 A+B 都要★
  🟠 ISS-313  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·需求闭环类·内部活] ★★【MECH 域 needs 184 条四分类处置 (waiting_on 空 
  🟠 ISS-314  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·HW 侧·口径收口 + 沙盒预演类·内部活] ★★【「板只改一次」那一趟的 S1 位号改名口径收口: 作业包 §5「网
  🟠 ISS-315  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·判据修复 + 新闸新建类·内部活] ★★【判据链收口: 把 ISS-312 收回去的「修法 B (链头落表单
  🟠 ISS-316  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·输入包 + 决策一页类·内部活] ★★【「板只改一次」那一趟的结构侧输入包: ①板框冻结闸 U-1 的【
  🟠 ISS-317  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·HW 侧·可执行清单 + 判据设计类·内部活] ★★【「板只改一次」那一趟的 S1 位号改名: 把 ISS-314 的
  🟠 ISS-318  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·判据新建 + 挂链体检类·内部活] ★★【「板只改一次」那一趟的 SW 侧: ①把那 95 处位号引用做成【
  🟠 ISS-319  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·对账 + 影响面类·内部活] ★★【「板只改一次」那一趟的 MECH 侧: ①把 ISS-316 的 2
  🟠 ISS-320  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·受限文本订正类·内部活] ★★【电芯型号订正【实做】: 把 ISS-319 查清的那 47 行里的 33
  🟠 ISS-321  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·纯分析 / 作业包 / 判据设计类·内部活] ★★【「板只改一次」那一趟的 SW 侧: S1 位号改名 (五
  🟠 ISS-322  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·HW 侧·布线归零作业包 + 死因逐条登记类·内部活] ★★【「板只改一次」那一趟的 S8 (布线归零 unconne
  🟠 ISS-323  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·逐字可执行清单类·内部活] ★★【「板只改一次」那一趟的 SW 侧: 7 件必须同批改的活 (ISS-321
  🟠 ISS-324  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·落位口径 + 候选坐标类·内部活] ★★【`D_LED_G` 落位口径一页 (G12 的前置): 93.
  🟠 ISS-325  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·PCB 线·沙盒预演 / 作业包类·内部活] ★★【「板只改一次」那一趟的 S8 前置: 「左上布局」21 器件 (1
  🟠 ISS-326  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·判据安全性体检类·内部活] ★★【S1 位号改名「MECH 侧」安全性体检: MECH 域 10+ 个判
  🟠 ISS-327  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·沙盒验证 + 当天 SOP 类·内部活] ★★【S1 位号改名「SW 侧」改名后【闸链复活】验证: 在沙盒里
  🟠 ISS-241  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·硬件选型/官方口径侧·内部活·排队] ★★BOM 里 value 仍写「待选型」的必装器件 = **21 件** (★
  🟠 ISS-242  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·原理图/网表侧·内部活] ★★网表/板 第 3 轮自相矛盾 3 条 (★main 2026-11-16 13:4x 本
  🟠 ISS-243  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·原理图/网表侧·内部活] ★★ISS-241 交卷的 4 条落表前置 (L1~L4) 收口: ① **L1/G-6 `
  🟠 ISS-244  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·硬件选型/官方口径侧·内部活] ★★ISS-241 缺口登记 G-1~G-10 的**自查补全** (★老板 2026
  🟠 ISS-245  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·跨域重锚·内部活] ★★ISS-243 落表把网表/脚表 md5 换掉 ⇒ **SW 侧 §1 锚点当场过期
  🟠 ISS-246  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·跨域重锚·内部活] ★★ISS-243 落表把网表/脚表 md5 换掉 ⇒ **MECH 侧 §3.1 
  🟠 ISS-247  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·原理图/网表侧·内部活] ★★ISS-242 F1 落表作业包 v1 (★**只出作业包 + 沙盒实跑, 真盘零写入*
  🟠 ISS-249  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·原理图/网表侧·落表执行·内部活] ★★ISS-247 的 F1 落表作业包 → 真落进真源 (★`state/gen
  🟠 ISS-250  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·demo 头号卡点·内部活] ★★ISS-155: 「rk3572 不是 rknn-toolkit2 合法 
  🟠 ISS-262  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·原理图/网表侧·落表防假绿·内部活] ★★★**落表链没有「行号漂移」判据 ⇒ V-3 落表 (删 3 行 DNP) 
  🟠 ISS-266  verified  owner=hw-lead    due=2026-11-20  
       ★★★[★新主线·PCB 侧·作业包·内部活] ★★★**出「板只改一次」作业包 v3 (★位号改名 + 板侧同步 B-1~B-8 
  🟠 ISS-268  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·PCB 侧·口径订正·内部活] ★★「板只改一次」作业包 v3 (`HW/PCB/BOARD_ONEPASS_WORK
  🟠 ISS-269  verified  owner=hw-lead    due=2026-11-20  
       ★★★[★新主线·PCB 侧·生成器侧·内部活] ★★★**「板只改一次」那三个会让那一趟白做的生成器坑** (★X-3: `gen
  🟠 ISS-271  verified  owner=mech-lead  due=2026-11-20  
       ★★[★主线内·MECH 侧·板侧认领·内部活] ★★**板那一趟 (S1~S13) 的 MECH 侧两个「无人认领」** ★ ① 
  🟠 ISS-274  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·PCB 线·纯分析+作业包订正类] ★★**「板只改一次」那一趟的【板框/坐标系口径】收口** ★★ ⇒ 现役板实测 
  🟠 ISS-275  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·门禁机制类] ★★**SW 侧 R6 判决源同构收口 (镜像 MECH 侧 ISS-273 已证机制)** 
  🟠 ISS-276  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·纯分析+规格页订正类] ★★**「板只改一次」那一趟的 MECH 侧【坐标系归一 + 收掉 ISS-27
  🟠 ISS-277  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·PCB 线·纯分析+作业包订正+机器闸类] ★★「板只改一次」那一趟的【板侧漏项覆盖度收口】★★ ⇒ ★**作业包 v
  🟠 ISS-278  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·纯分析+规格页订正+机器闸类] ★★「板只改一次」那一趟的【MECH 侧板侧输入收口】★★ ⇒ ★**I
  🟠 ISS-279  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·纯分析+作业包订正+机器闸类] ★★「板只改一次」那一趟的【SW 侧板侧输入收口】★★ ⇒ ★**ISS-2
  🟠 ISS-280  verified  owner=hw-lead    due=2026-11-20  
       ★★[★新主线·PCB 线·纯分析+作业包订正+机器闸类] ★★「板只改一次」的【提交时序守卫】★★ ⇒ ★**作业包 v3 §0/
  🟠 ISS-281  verified  owner=hw-lead    due=2026-11-20  
       ★★[★主线·PCB 线·纯规格+作业包追加式订正+机器闸类] ★★「板只改一次」的【S10 投产包 md5 清单落地】★★ ⇒ ★
  🟠 ISS-282  verified  owner=hw-lead    due=2026-11-20  
       ★★[★主线·PCB 线·纯规格+作业包追加式订正+机器闸类] ★★「板只改一次」的【`FSIN_OUT` 根因订正 + 布线前置闸
  🟠 ISS-287  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·PCB 线·板那一趟·前置准备·内部活] ★★【「板只改一次」那一趟的 A 类步【沙盒干跑可行性探针】】★★ ⇒ ★*
  🟠 ISS-289  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·PCB 线·纯规格订正+机器闸类·内部活] ★★【动板前: 把作业包 §3 里【全部现状值型判据】对回盘面实测】★★ 
  🟠 ISS-290  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·板那一趟·结构侧交叉核对·内部活] ★★【「板只改一次」那一趟: ① S6 的 20 个目标落位 × M
  🟠 ISS-291  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·ADC 判据口径收口+机器闸类·内部活] ★★【SW 侧 ADC 判据的【判决对象 + 满量程口径】双错】★
  🟠 ISS-292  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·PCB 线·纯生成器对齐+作业包指针订正类·内部活] ★★【清单页生成器 `state/_iss277_build_p
  🟠 ISS-293  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·复评文档口径收口 + 机器闸类·内部活] ★★【`SW/SW_TIMING_REVIEW.md` 停在 IS
  🟠 ISS-294  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·规格补缺 + 机器闸类·内部活] ★★【`J_USB_C` 缺一条结构边开口规格 (★座体 `F.Fab
  🟠 ISS-295  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·结构输入一次性收口 + 过期结论防漂闸·内部活] ★★【① MECH 两页对同一件事【两种说法】: `B
  🟠 ISS-296  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·闸机制类·内部活] ★★【MECH 两道闸把【板 md5】写死成「硬保护基线」⇒ 板那一趟合法改板一次后
  🟠 ISS-297  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·HW 侧·门禁机制收口·内部活] ★★【HW 侧 6 道闸: 建「合法改板」通道】★★ ⇒ ★**全仓 9 道闸硬钉板
  🟠 ISS-298  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·门禁机制收口·内部活] ★★【SW 侧 1 道闸: 建「合法改板」通道】★★ ⇒ ★**全仓 9 道闸硬钉板
  🟠 ISS-299  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·HW 侧·重锚类·零写板] ★★【H-1 重锚第 2 跳: 让 9 道「钉板 md5 闸」里唯一红的那一道能挂进门禁链
  🟠 ISS-300  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·准出闸类·零写板] ★★【「板只改一次」那一趟的 MECH 侧【准出汇总闸】: 一条命令出「S6 重出板
  🟠 ISS-302  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·落表链侧·内部活] ★★【落表: `C_SYS` / `SYS_CHG` 必装 + note 追加式订正 + BOM 
  🟠 ISS-303  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·闸机制类·内部活] ★★【MECH 侧 N6 只认【硬基线】不认【合法落表跳】⇒ 00:21 ISS-3
  🟠 ISS-304  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·HW 侧·现状值重锚类·内部活] ★★【钉板闸⑥ 作业包现状值闸: 00:21 ISS-302 合法落表一次 ⇒ 页面
  🟠 ISS-306  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·开工前置·溯源类·内部活] ★★【板那一趟开工前置: G1a 剩下两条红 (G1a-4 落表未清零 + G1a-8 关
  🟠 ISS-328  verified  owner=hw-lead    due=2026-11-20  
       ★补一条【真能构成对照】的右上臂 (R_SEL_* 挪右上) + 在官方链同配方下复测 TP no-op (⇒ 给 ISS-325 
  🟠 ISS-332  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·判据收紧类·内部活] 第 8 道闸 (SW 位号引用可达性) 的 C1/C7/C8/C13 四条【洗白面】·
  🟠 ISS-333  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·闸实现类·内部活] MECH 侧位号可达性闸 · 从【设计稿】到【可直接挂的闸】的实现单 (★零改 st
  🟠 ISS-334  verified  owner=hw-lead    due=2026-11-20  
       ★★[★新主线·PCB 线·机制级·纯分析+作业包类·内部活] ★★**零铜网「换机制」路线: 成对走廊 / 换层绕开 / 路由器本
  🟠 ISS-335  verified  owner=sw-lead    due=2026-11-20  
       ★★[★新主线·PCB 线·纯新建闸类·内部活] ★★**「板只改一次」那一趟的【SW 侧准出汇总闸】** (★对标 MECH 侧 
  🟠 ISS-336  verified  owner=mech-lead  due=2026-11-20  
       ★★[★新主线·PCB 线·纯新建闸类·内部活] ★★**「板只改一次」那一趟的【板框冻结闸 U-1 机器闸实现】** (★ISS-
  🟠 ISS-337  verified  owner=hw-lead    due=2026-11-20  
       ★★[★新主线·PCB 线·纯分析+沙盒类·内部活] ★★**段数追平根因定位: 现生成器 stage-1 只出 ~2.5K 段 v
  🟠 ISS-338  verified  owner=sw-lead    due=2026-11-20  
       ★★[★新主线·PCB 线·纯分析类·内部活] ★★**ISS-334 need-4a: 官方板 24 个零铜网里的 9 条单端低速
  🟠 ISS-339  verified  owner=hw-lead    due=2026-11-23  
       ★★[★新主线·PCB 线·纯分析+新建闸类·零写板] ★★【板那一趟 S8 布线归零的两把尺子: ① 【可比性前置闸】(main 
  🟠 ISS-340  verified  owner=hw-lead    due=2026-11-23  
       ★★[★新主线·PCB 线·纯分析+新建判别闸·零写板] ★★【板↔网表 C1 红根因归属判定: chain_gate ③ PCB 
  🟠 ISS-341  verified  owner=mech-lead  due=2026-11-23  
       ★★[★新主线·PCB 线·纯分析+新建判定闸·零写板] ★★【「板那一趟」画哪块板: U-1 板框冻结三候选 (B160x100 
  🟠 ISS-342  verified  owner=mech-lead  due=2026-11-23  
       ★★[★新主线·PCB 线·结构侧口径漂移·纯分析+文档订正+机器闸类·零写板] ★★【C6: `MECH/BOARD_GEOM_3
  🟠 ISS-343  verified  owner=hw-lead    due=2026-11-24  
       ★★[★新主线·PCB 线·板侧项全集漏项·纯分析+文档订正+机器闸·零写板] ★★【E-1 排针 land 0.50→1.27mm
  🟠 ISS-344  verified  owner=sw-lead    due=2026-11-24  
       ★★[★新主线·PCB 线·固件侧分级口径对账·纯分析+文档订正+机器闸·零写板] ★★【ISS-338 §3 表的 6 条「NC 
  🟠 ISS-345  verified  owner=mech-lead  due=2026-11-24  
       ★★[★新主线·PCB 线·MECH 域判据迁双口径·纯脚本改造+文档订正+机器闸·零写板] ★★【8 个 MECH 判定脚本迁【双
  🟠 ISS-354  verified  owner=hw-lead    due=2026-11-24  
       ★★[★新主线·PCB 线·demo 主板可制造性收口·纯查证·零写板] ★★【ISS-169 (open, owner=main)
  🟠 ISS-348  fixed     owner=main       due=2026-11-25  
       ★★[★基础设施·跨 job·内部活·零写板] ★★【/tmp 是带 userquota 的 tmpfs (7.5G) 而用户配额已
  🟠 ISS-349  verified  owner=hw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·板侧项全集页被手改·生成器重跑会蒸发 E-1·纯脚本改造+新建机器闸·零写板] ★★【把 `B33_PI
  🟠 ISS-352  verified  owner=mech-lead  due=2026-11-25  
       ★★[★新主线·PCB 线·MECH 域判定脚本迁双口径·第 2 批·零写板] ★★【ISS-345 cont1 (第 1 批 2 
  🟠 ISS-356  verified  owner=hw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·「板那一趟」封装真值基线 (100 件必装器件的占位封装 → 真库封装映射)·纯分析/作业包·零写板] 
  🟠 ISS-357  verified  owner=sw-lead    due=2026-11-25  
       ★★[主线内·SW 侧·需求闭环类·内部活] ★★【SW 域 needs 144 条四分类处置 (waiting_on 空 118 
  🟠 ISS-361  verified  owner=hw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·「板那一趟」封装真值覆盖缺口·纯分析+文档+机器闸·零写板] ★★【ISS-356 交卷的「封装真值基线
  🟠 ISS-362  verified  owner=sw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·SW 侧「S10 换封装真值」那一跳的影响面·纯分析+沙盒预演+机器闸·零写板] ★★【「板只改一次」那
  🟠 ISS-363  verified  owner=sw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·SW 侧「S10 换封装真值」收口·纯分析+新建闸+沙盒预演·零写板] ★★【ISS-362 (sw-l
  🟠 ISS-364  verified  owner=hw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·HW 侧「S10 换封装真值」收口·纯分析+作业包+新建闸+沙盒可达性证明·零写板] ★★【ISS-36
  🟠 ISS-365  verified  owner=mech-lead  due=2026-11-25  
       ★★[★新主线·PCB 线·MECH 侧「S10 换封装真值」影响面·纯分析+新建闸+沙盒重判·零写板] ★★【ISS-290 (m
  🟠 ISS-366  verified  owner=hw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·网表侧·「板那一趟」S10 同批的【网表硬缺陷】补行作业包·纯作业包+沙盒+新建闸·零写板·零落表] ★
  🟠 ISS-367  verified  owner=mech-lead  due=2026-11-25  
       ★★[★新主线·PCB 线·MECH 侧·「板那一趟」S10 换官方 0805 后的【LED 窗口规格同趟重算】·纯文档定点改写+新
  🟠 ISS-368  verified  owner=sw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·SW 侧·「板那一趟」SW09 清单第 9 条的【三处同批落地】补丁·纯作业包+沙盒 dry-run+新
  🟠 ISS-370  verified  owner=sw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·SW 侧「腿 B 网表节点具名」对 SW 判据链的影响面·纯分析+作业包+新建闸+沙盒预演·零写板] ★
  🟠 ISS-369  verified  owner=hw-lead    due=2026-11-26  
       ★★[★新主线·PCB 线·HW 侧·「板那一趟」S10 的【板面库封装名 0/186 全空】写盘作业包·纯作业包+沙盒+新建闸·零
  🟠 ISS-371  verified  owner=mech-lead  due=2026-11-26  
       ★★[★新主线·PCB 线·结构侧·「板那一趟」`J_DEBUG` 排针 land 改 1.27mm 后的净距真相·纯分析+文档订正
  🟠 ISS-372  verified  owner=sw-lead    due=2026-11-26  
       ★★[★新主线·PCB 线·SW 侧·「板那一趟」S9 换基线 · SW 侧板 md5 引用面清账 + 一条「钉板 md5 闸清单」
  🟠 ISS-373  verified  owner=hw-lead    due=2026-11-26  
       ★★[★新主线·PCB 线·HW 侧·「板那一趟」S10 换件集合的【唯一真源】+ 一条「集合口径」机器闸·纯分析+作业包+新建闸+
  🟠 ISS-374  verified  owner=mech-lead  due=2026-11-26  
       ★★[★新主线·PCB 线·结构侧·「板那一趟」`J_UART` 排针 land 改 1.27mm 的结构侧净距真相 (ISS-37
  🟠 ISS-375  verified  owner=sw-lead    due=2026-11-26  
       ★★[★新主线·PCB 线·SW 侧·「板那一趟」`J_DEBUG`/`J_UART` 排针换 land 后的【物理针序契约】(pi
  🟠 ISS-376  verified  owner=hw-lead    due=2026-11-26  
       ★★[★新主线·PCB 线·HW 侧·「板那一趟」`J_DEBUG` 换官方 1×4 THT land 的**落位可行性**穷举（现
  🟠 ISS-377  verified  owner=mech-lead  due=2026-11-26  
       ★★[新主线·PCB 线·结构侧·「板那一趟」] 座体净距判据**同源化** (`J_DEBUG` 铜箔支配 vs `J_UART`
  🟠 ISS-378  verified  owner=sw-lead    due=2026-11-26  
       ★★[新主线·PCB 线·SW 侧·「板那一趟」] `J_DEBUG`/`J_UART` 排针换 land 后的**固件影响面清单*
  🟠 ISS-379  verified  owner=hw-lead    due=2026-11-26  
       ★★[★新主线·PCB 线·HW 侧·「板那一趟」] `J_UART` (1×2) 换官方 P1.27 THT land 的**落位
  🟠 ISS-380  verified  owner=hw-lead    due=2026-11-26  
       ★★[★新主线·PCB 线·HW 侧·「板那一趟」] `J_DEBUG` / `J_UART` 座体的【厂商具体型号 + 座体真实高
  🟠 ISS-155  open      owner=main       due=2026-11-27  
       ★★★★[demo 头号卡点] rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 targe
  🟠 ISS-381  verified  owner=sw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·SW 侧·「板那一趟」] 布线验收线之【零假连通】自检闸: 每条必需网按预期拓扑逐条列铜 (★纯分析+新
  🟠 ISS-382  verified  owner=mech-lead  due=2026-11-27  
       ★★[★新主线·PCB 线·MECH 侧·纯分析+新建闸·零写板] `J_DEBUG` 已签收真相页的 `2x2` 排布标签与实测矛
  🟠 ISS-383  verified  owner=hw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·HW 侧·纯分析+新建闸·零写板] 座体选型的【四方对齐作业包】: 候选件真实规格 / 库封装可得性 /
  🟠 ISS-384  verified  owner=hw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·HW 侧·纯文档+新建闸·零写板] 「板只改一次」那一趟的【充电电流档位活值口径收口】: 把 0.822
  🟠 ISS-385  verified  owner=sw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·SW 侧·纯分析+新建闸·零写板] EVT `PWR-05` 充电电流判据与现行 `R_ILIM` 体系
  🟠 ISS-386  verified  owner=mech-lead  due=2026-11-27  
       ★★[★新主线·PCB 线·MECH 侧·纯分析+新建闸+沙盒·零写板] 「板只改一次」那一趟的 `J_DEBUG` + `J_UA
  🟠 ISS-387  verified  owner=hw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建闸·零写板] 「板只改一次」那一趟的 `J_DEBUG`/`J_UART`
  🟠 ISS-388  fixing    owner=sw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·SW 侧·纯分析+新建闸·零写板] 两道【已签收 verified】的 SW 闸今天实测【真的坏了】⇒ 
  🟠 ISS-389  verified  owner=mech-lead  due=2026-11-27  
       ★★[★新主线·PCB 线·MECH 侧·纯分析+作业包+新建闸·零写板] `J_DEBUG`/`J_UART` 两连接器的【座体 
  🟠 ISS-390  fixing    owner=mech-lead  due=2026-11-27  
       ★★[★新主线·PCB 线·MECH 侧·纯查证+新建闸·零写板] `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高
  🟠 ISS-391  fixing    owner=hw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·HW 侧·纯分析+作业包+新建闸·零写板] 「板只改一次」那一趟的排针 land 【`0.65 → 0.
  🟠 ISS-392  fixing    owner=sw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·SW 侧·纯分析+新建真相页+新建闸·零写板] SW 域【门禁链覆盖率 + 第三道病闸基线漂移】⇒ 把「
  🟠 ISS-393  fixing    owner=mech-lead  due=2026-11-27  
       ★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建闸·零写板] 「通用库件 courtyard 被当成厂件」
  🟠 ISS-394  fixing    owner=hw-lead    due=2026-11-27  
       ★★[★新主线·PCB 线·HW 侧·纯分析+新建真相页+新建闸·零写板] 座体选型结论【只写在 issue_log 里, 没落到活
  🟠 ISS-120  verified  owner=sw-lead    due=2026-11-30  
       ★S2 救砖链路板端实测 (量产一票否决项) —— 方案+自检已闭环 (ISS-080), 待 EVT 有板后真跑 (EVT-8/B
  🟠 ISS-347  fixed     owner=main       due=2026-11-30  
       ★★[★主线·派活/门禁机制侧·内部活·零写板] ★★【`state/advance.py --apply` 的落盘路径一直是坏的:
  🟠 ISS-038  open      owner=boss       due=2026-11-18   ⏰逾期 [外部]
       【缺角色】工业设计 (ID/CMF/佩戴舒适度) 无人负责 —— 需老板拍板是否加第 4 个总工
       ❌ ★逾期★ due=2026-11-18 已过, 仍 open
  🟠 ISS-041  open      owner=boss       due=2026-11-18   ⏰逾期 [外部]
       ★★[当前 demo 板] 测试条件缺失 ⇒ G3 那一关不可判通过 (★2026-11-04 09:57 起: 不含热电偶/假皮肤
       ❌ ★逾期★ due=2026-11-18 已过, 仍 open
  🟠 ISS-060  open      owner=boss       due=2026-11-18   ⏰逾期 [外部]
       产品件三条几何待老板裁决 (压垫吸收量零余量 / 非对称方向 / 压垫槽区板厚小于 FDM 最小壁) —— 打印包转绿不等于解 A 
       ❌ ★逾期★ due=2026-11-18 已过, 仍 open
  🟠 ISS-063  open      owner=boss       due=2026-11-18   ⏰逾期 [外部]
       显示端 120 度到 30 度的映射方式 (看得广但糊 vs 看得清但窄) —— 120 度这个卖点对用户可见吗
       ❌ ★逾期★ due=2026-11-18 已过, 仍 open
  🟠 ISS-097  fixed     owner=boss       due=2026-11-18   ⏰逾期 [外部]
       ★"关机"语义: 硬件断电通路 (负载开关) + 真关机拓扑 + 功耗预算 V3
       ❌ ★逾期★ due=2026-11-18 已过, 仍 fixed
  🟠 ISS-106  open      owner=boss       due=2026-11-18   ⏰逾期 [外部]
       ★新增渠道: 经酷芯微代理转达 (老板 10-28 找到代理) —— 代理信 + 3 份可转发附件已就绪
       ❌ ★逾期★ due=2026-11-18 已过, 仍 open
  🟠 ISS-116  fixed     owner=boss       due=2026-11-18   ⏰逾期 [外部]
       ★★工作方式改造: 老板任务先落 GitHub 总表 + token 守护 (老板 10-29 09:59 亲自要求)
       ❌ ★逾期★ due=2026-11-18 已过, 仍 fixed
  🟠 ISS-156  open      owner=main       due=2026-11-19   ⏰逾期
       ★★[demo 供应链] 自研主板的三件前置选型: camera 模组 / 屏模组 / RK3572 核心板 (★主板的 FPC 座
       ❌ ★逾期★ due=2026-11-19 已过, 仍 open
  🟠 ISS-126  open      owner=main       due=2026-11-20   ⏰逾期
       ★★板厚档位未定 ⇒ 检修口净空只有 4.90 那一档过 (1.22mm 档净空 4.48 破 4.50 硬要求)
       ❌ ★逾期★ due=2026-11-20 已过, 仍 open
  🟠 ISS-128  open      owner=main       due=2026-11-20   ⏰逾期
       ★★主控换 RK3572 ⇒ 板面积账 + 逃线层数全部重算 (封装 FCCSP550L 14.3×15.5mm / 550 球, 
       ❌ ★逾期★ due=2026-11-20 已过, 仍 open
  🟠 ISS-129  open      owner=main       due=2026-11-20   ⏰逾期
       ★★★RK3572 (4 TOPS) 板端纯 NPU 实测 ⇒ 端到端 60ms 硬指标生死判定 (★T2 翻案条件推算已命中)
       ❌ ★逾期★ due=2026-11-20 已过, 仍 open
  🟠 ISS-130  open      owner=main       due=2026-11-20   ⏰逾期
       ★★★RK3572 功耗 670mW (原厂口径) vs 贴皮肤 43°C 红线 —— 从「待定」变「可判」
       ❌ ★逾期★ due=2026-11-20 已过, 仍 open
  🟠 ISS-133  open      owner=main       due=2026-11-20   ⏰逾期
       ★★★显示架构变更: '屏' ≠ '光机' ⇒ 必须新增一级耦合光学 ⇒ 镜框光学腔体/分光器/整机空间全部重算
       ❌ ★逾期★ due=2026-11-20 已过, 仍 open
  🟠 ISS-169  open      owner=main       due=2026-11-20   ⏰逾期
       ★★[demo 板可制造性] demo 主板的边界已定 (Type-C 供电 · 不装电池 · 板上只有这一块) + SoM 座的 
       ❌ ★逾期★ due=2026-11-20 已过, 仍 open
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
  🟡 ISS-134  verified  owner=mech-lead  due=2026-11-06  
       ★★JBD 角色收窄为波导 + ISS-016 作废 + ISS-048 光生物安全口径整个变了 (LED 点光源 → OLED 面
  🟡 ISS-136  verified  owner=hw-lead    due=2026-11-06  
       ★★J_CHG 跨铰链 pin map 与 CHARGE_BOARD_SPEC.md §5 漂移 (spec 是旧的, 网表是对的)
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
  🟡 ISS-025  verified  owner=mech-lead  due=2026-11-13  
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
  🟡 ISS-193  verified  owner=hw-lead    due=2026-11-13  
       ★【内部活·不是原厂的事】29 个器件真实脚数查不到 ⇒ 根因是 BOM 没定 opn/封装 ⇒ 定封装 ⇒ 脚数自动补齐 ⇒ 选项
  🟡 ISS-195  verified  owner=hw-lead    due=2026-11-13  
       ★【ISS-194 的连带账·真影响】麦 M1 到 S1 压紧螺钉孔的孔壁净空随套A 从 ≈8.14mm 掉到 ≈1.26mm ⇒ 
  🟡 ISS-196  verified  owner=sw-lead    due=2026-11-13  
       ★【内部活·不是原厂的事】两条逾期 6 天的 P0 needs_from 前提已被实测推翻 ⇒ rknn 工具链/构建环境/模型 s
  🟡 ISS-197  verified  owner=mech-lead  due=2026-11-13  
       ★【内部活·不是原厂的事】套A 孔位已落地 ⇒ 结构侧 5 处记录还停在「套B 仍是活口径」⇒ 口径收敛 + 3 条未决项(骨架超重
  🟡 ISS-200  verified  owner=mech-lead  due=2026-11-13  
       ★★J_CHG pin map 在结构侧还有 2 处第二口径 ⇒ `state/fragments/mech.yaml` 的 `in
  🟡 ISS-201  verified  owner=sw-lead    due=2026-11-13  
       ★★★[demo OD 关键路径·台账治理] 模型资产台账登的是【原件】, 磁盘上是【重建件】 ⇒ `probe` 永远打「台账一致
  🟡 ISS-206  verified  owner=mech-lead  due=2026-11-13  
       ★★[主线内·接口契约侧·内部活] ★★结构侧 J_CHG 旧口径一次性收口 (★第 3 套 pin map `8p@0.5` +

  🟡 ISS-199  verified  owner=hw-lead    due=2026-11-14  
       ★★J_CHG pin map 在 HW 侧还有 4 处第二口径 (ISS-136 只改了 §5.2 一张表) ⇒ §5.1 过铰链
  🟡 ISS-202  verified  owner=mech-lead  due=2026-11-14  
       ★★J_CHG pin map 在结构侧还有 5 处第二口径 (ISS-200 只改了 §5.2 + `j_chg_pin_map`
  🟡 ISS-203  verified  owner=mech-lead  due=2026-11-14  
       ★★★[假判据·ISS-197 遗留 L1/L5/L6] 结构侧两个机械复核器还钉在 15mm 板宽 ⇒ `MECH/hw_cros
  🟡 ISS-204  verified  owner=hw-lead    due=2026-11-14  
       ★★[主线内·原理图侧·内部活] `J_SOM_P2.pin7` 官方默认功能 = `PWM0_CH1_M0`, 我们拿它当 `UA
  🟡 ISS-103  deferred  owner=mech-lead  due=2026-11-16  
       ★镜框开导光孔/导光柱 (充电灯装充电板靠 Type-C 座, 老板拍板关机时充电灯要亮)
  🟡 ISS-174  verified  owner=hw-lead    due=2026-11-18  
       ★★[demo 触控收不到中断] display 触控的 TP_INT (pin26) 没接到 SoM 任何脚 ⇒ 触控中断收不到
  🟡 ISS-208  verified  owner=mech-lead  due=2026-11-18  
       ★★[主线内·显示侧·内部活] ISS-134 遗留: 旧 MECH 文档 33 处「走鹃」活动口径收口 + 光生物安全 V2 的眼
  🟡 ISS-095  verified  owner=main       due=2026-11-19  
       ★[待 TI 确认] BQ25896 的 VSYS 脚是否必须接 —— 决定'电池挪镜框'回退分支要不要多两根电源 pin
  🟡 ISS-131  verified  owner=main       due=2026-11-19  
       ★★ISS-124/125 问询口径改 RK3572 (ISP 16M→12M, CSI 3×→2×) + 球位号问询对象改瑞芯微/
  🟡 ISS-253  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·H-1 重锚·内部活] ★★`MECH/check_demo_struct_truth.py` 因 IS
  🟡 ISS-254  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·H-1 重锚·内部活] ★★`SW/tools/check_demo_panel_spec.py` rc=1
  🟡 ISS-255  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·门禁侧·口径缺陷·内部活] ★★`state/chain_gate.py` 的【新鲜度】判据用 mtime ⇒ ★**
  🟡 ISS-256  verified  owner=main       due=2026-11-19  
       ★★[主线内·门禁侧·口径缺陷·内部活] ★★★**`.kicad_sch` 的 md5 永久不可当锚点** ★ ⇒ ★**任何以「
  🟡 ISS-258  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·H-1 重锚·内部活] ★★`SW/tools/check_demo_panel_spec.py` rc=1
  🟡 ISS-259  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·H-1 重锚·内部活] ★★`MECH/check_demo_struct_truth.py` rc=2
  🟡 ISS-285  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·判据口径收口·内部活] ★★【落表之后: SW 侧三道判据过期】★★ ★**`SW/tools/timing
  🟡 ISS-286  verified  owner=mech-lead  due=2026-11-19  
       ★★[主线内·MECH 侧·门禁机制收口·内部活] ★★【MECH 侧坐标归一闸 `MECH/check_board_frame_c
  🟡 ISS-301  verified  owner=hw-lead    due=2026-11-19  
       ★★[主线内·HW 侧·复核类+残余事实类·零写板] ★★【复核 main 自产的 `HW/TI_POWER_FACTS.md` 四
  🟡 ISS-309  verified  owner=sw-lead    due=2026-11-19  
       ★★[主线内·SW 侧·闸缺陷归因类·内部活] ★★【SW 侧 R6 判决源专项反向用例「5/7」红 ⇒ 查清 R4 与 R5a 各
  🟡 ISS-248  verified  owner=sw-lead    due=2026-11-20  
       ★★[主线内·SW 侧·判据口径收口·内部活] ★★`SW/tools/timing_check.py --reverse-demo
  🟡 ISS-251  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·MECH 侧·口径收口·内部活] ★★mech-lead 自己登记给 main 的 3 条「只报不改 ⇒ 现在授权改」
  🟡 ISS-264  verified  owner=mech-lead  due=2026-11-20  
       ★★[主线内·结构侧·口径收口·内部活] ★★`MECH/service_port_check.py` 三处常量还停在旧 15mm 
  🟡 ISS-270  verified  owner=sw-lead    due=2026-11-20  
       ★★[★主线内·SW 侧·政策落地·内部活] ★★**老板 2026-11-12 02:02「不再发信, 全靠自己查资料」的第 ② 
  🟡 ISS-272  verified  owner=sw-lead    due=2026-11-20  
       ★★[门禁/运维侧·独立复核·内部活] ★★**独立复核 main 亲手改的 `state/delivery_truth.py` 口
  🟡 ISS-305  verified  owner=hw-lead    due=2026-11-20  
       ★★[主线内·HW 侧·独立复验类·内部活] ★★【ISS-131「问询口径改 RK3572 (ISP 16M→12M / CSI 
  🟡 ISS-267  verified  owner=mech-lead  due=2026-11-21  
       ★★[主线内·结构侧·板侧开口约束·纯分析·内部活] ★★检修口/调试口 `jd_y0` 的合法区间只剩 [3.57, 12.13]
  🟡 ISS-273  verified  owner=mech-lead  due=2026-11-21  
       ★★[主线内·MECH 侧·门禁机制收口·内部活] ★★**网表/脚表 md5 锚点已跳 6 跳 ⇒ 「一落表就红, 必人工重锚」*
  🟡 ISS-350  verified  owner=sw-lead    due=2026-11-24  
       ★★[★新主线·PCB 线·存储轴 Q3 分档口径写回 SW 侧·纯口径·零写板] ★★【ISS-346 已签收 ⇒ Q3 从「整卡
  🟡 ISS-351  verified  owner=hw-lead    due=2026-11-24  
       ★★[★新主线·PCB 线·存储轴旧口径清账·纯口径·零写板] ★★【ISS-346 + ISS-350 连续两单把存储轴口径从「整
  🟡 ISS-346  verified  owner=sw-lead    due=2026-11-25  
       ★★[★新主线·PCB 线·存储轴 Q3 分档可判·纯分析+机器矩阵+一页决策口径·零写板] ★★【把 Q3「模型/rootfs 怎
  🟡 ISS-355  verified  owner=sw-lead    due=2026-11-25  
       ★★[★模型链·实现侧·纯脚本·零写板] ★★【ISS-353 已签收 ⇒ 口径清了, 但【实现】没改: `SW/tools/rk3
  🟡 ISS-358  verified  owner=mech-lead  due=2026-11-25  
       ★★[★主线内·机制侧·分片卫生类·内部活] ★★【`state/fragments/mech.yaml` 有 4 组 answer
  🟡 ISS-359  verified  owner=hw-lead    due=2026-11-25  
       ★★[★主线内·机制侧·分片卫生类·内部活] ★★【`state/fragments/hw.yaml` 有 2 组 answers 
  🟡 ISS-252  fixed     owner=main       due=2026-11-18   ⏰逾期
       ★★[主线内·原理图侧·阶段门口径·内部活] ★★**G1「原理图定稿 / PCB 定稿」拆关** ⇒ 新闸 `state/chec
       ❌ ★逾期★ due=2026-11-18 已过, 仍 fixed
  🟡 ISS-109  open      owner=main       due=2026-11-19   ⏰逾期
       ★R-GEO 六问全 0 答复: ISP 吞吐余量 1.9% vs 50.7% 完全相反 (一票否决级) + 采集链/散热结论都不能
       ❌ ★逾期★ due=2026-11-19 已过, 仍 open
  🟡 ISS-125  open      owner=main       due=2026-11-19   ⏰逾期
       ★R-GEO 六问的其余五问要按 RK3576 口径重写问询 (问 01/02/04/05/06 仍是 0 答复)
       ❌ ★逾期★ due=2026-11-19 已过, 仍 open
  🟡 ISS-330  fixed     owner=main       due=2026-11-22   ⏰逾期
       ★把「MECH 侧位号可达性闸」挂进 `state/gate_check.py` (★设计稿已在盘·★owner=main·★改闸不
       ❌ ★逾期★ due=2026-11-22 已过, 仍 fixed
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
  🟡 ISS-329  verified  owner=main       due=2026-11-21  
       ★4 个生成器产物被闸脚本无条件重写 ⇒ mtime 证据链被污染 (★复发型·ISS-280 之后第二次★)·★定终局方案★
  🟡 ISS-261  verified  owner=main       due=2026-11-22  
       ★★[门禁侧·口径缺陷·内部活] ★★`state/delivery_health.py` 的【口径①】把 `delivery.mo
  🟡 ISS-360  verified  owner=mech-lead  due=2026-11-25  
       ★★[★主线内·口径订正类·文档一行·零写板] ★★【`MECH/BOARD_FRAME_FREEZE_DECISION_PACK.

❌ 违规 19 条
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
      ▸ ★G1a 原理图定稿 (★独立闸★): ❌ 还差 2 条: G1a-4, G1a-8
          ★**G1 的缺口是 PCB 的 (unconnected) ⇒ 原理图侧的真相在这一行** ★
          - G1a-4 落表已清零 (翻面口径) ⇒ rc=1 (python3 HW/check_netlist_selfconsistency.py --expect-resolved) ⇒ ★R4 未落表: D_ESD_USB_D 仍然只有 2 个焊盘 (D+ + G
          - G1a-8 关机语义 + 负载开关选型已决 ⇒ ISS-097=fixed · ISS-172=verified

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

【G4】体验验收 (DoD 全过)  —  ⏳ 未到   缺 43 项
      为什么要这一关: 所有问题单关闭 + 质量门全绿 + DoD 清单逐条签
      ▸ 问题单未闭环 (43):
          - ISS-004 [deferred] 波导未选型 (等 JBD) → 卡镜框打印开工
          - ISS-013 [deferred] 波导未选型 → 缺 2D 外形图/容差角/彩虹纹 → 镜框不能开工
          - ISS-016 [deferred] 走鹃Ⅱ 长宽高未知 → 光机位姿/干涉检查做不了
          - ISS-038 [open] 【缺角色】工业设计 (ID/CMF/佩戴舒适度) 无人负责 —— 需老板拍板是否
          - ISS-040 [deferred] 打印与量测条件不具备 (打印机跨网段不可达 + 无切片器/量具) → M-PRI
          - ISS-041 [open] ★★[当前 demo 板] 测试条件缺失 ⇒ G3 那一关不可判通过 (★202
          - ISS-048 [deferred] 光生物安全所需的光机参数缺失 (LED 波长/亮度/光通量/辐亮度) —— 已并
          - ISS-060 [open] 产品件三条几何待老板裁决 (压垫吸收量零余量 / 非对称方向 / 压垫槽区板厚小
          ... 另 35 条

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

【硬件总工 (hw-lead)】❌ 未就绪 (5 项不过)
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
   ❌ 外部等待已标 waiting_on+due
        等老板/原厂/JBD 必标 (漏标: ['iss236_boss_v_decision', 'iss260_boss_a3_arch_and_model'])
   ✅ 硬件模块拆解 + 电源树
   ✅ EMC 预评估 (画板前)

【软件总工 (sw-lead)】❌ 未就绪 (5 项不过)
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
   ❌ 外部等待已标 waiting_on+due
        等老板/原厂/JBD 必标 (漏标: ['iss191_boss_pick_fix_option', 'iss191_boss_q_envc_unify', 'iss191_boss_r_pg_pull_dnp', 'iss234_boss_pick_5q', 'iss250_pick_downgrade_route', 'iss250_n3_threshold_recheck'])
   ✅ 软件需求拆解 + 延迟预算
   ✅ EVT 模板 + 联调计划

【结构总工 (mech-lead)】❌ 未就绪 (5 项不过)
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
   ❌ 外部等待已标 waiting_on+due
        等老板/原厂/JBD 必标 (漏标: ['iss209_mech_d_value_decision'])
   ✅ 空间预算 + 散热模型
   ✅ 打印包 + 测量清单

── 项目级终判 ───────────────────────────────────────────────────────
  📄 纸面阶段 (G0 纸面冻结 / G1 原理图 / G2 结构样机准备): ❌ 机制有未过项
     → 判据: 4 个角色机制全绿 + 质量门/问题门/阶段门/推进器可用 + 框架裁剪基线在位
     → 当前卡点: 老板 9 条决策 + 原厂/JBD 外部; 内部可自行推进 268 条
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
- 老板已拍板决策 **2** 条 → `docs/DECISIONS.md`
- 需求总数 **645** 条 (已答 268 / 未闭合 377)
- 冲突 0 · 门禁违规 0

## 8. 未闭环的高危问题
| id | 责任方 | due | 标题 |
|---|---|---|---|
| ISS-074 | main | 2026-10-29 | ★开始画硬件原理图 V1 (8 页图页 + 完整 netlist + KiCad 可导入 .net) —— 球位号统一用 TBD 占位, 原厂回信后只填球号 |
| ISS-147 | main | 2026-11-04 | ★★★[demo P0] 恢复 RKNN 构建环境 + 证明 rk3572 是 rknn-toolkit2 2.3.2 的合法 target —— 不解决这条, 软件侧一步都动不了 |
| ISS-119 | main | 2026-11-05 | ★★换芯定案 + 迁移方案 (A7/A8): 选哪颗 + 网表/原理图/BOM 重做清单 + 为 RK3588 预留的可执行后手 |
| ISS-139 | sw-lead | 2026-11-05 | ★★[内部, 与选谁无关] ISP tuning 立项: 两个候选 sensor 都没有现成 IQ 文件 ⇒ 这笔账必须自己排 |
| ISS-145 | sw-lead | 2026-11-05 | ★★★★[demo 关键路径 #2] demo 板 OD 管线打通规格: yolov5n INT8 → RKNN → 画框 → 视涯 049 显示 |
| ISS-162 | main | 2026-11-13 | ★★★[硬件 · 画板前必须] 网表按真实器件规格重出: FPC 座 31p/0.3mm + 40p/0.5mm + SOM 400 脚 BTB + 电源输入改 5-13V |
| ISS-207 | sw-lead | 2026-11-18 | ★★★★[demo 头号卡点·自己查版] ISS-155 拆块: rknn-toolkit2 最新版到底支不支持 rk3572 target + RK3572 runtime 认不认 rk3576-target 产物 + 板端到手 30 分钟可跑的验证包 |
| ISS-160 | main | 2026-11-20 | ★★★[自己画图] demo 主板图纸链: KiCad 10 工具链(免 root AppImage) + 参数化生成器 + DRC 门禁(已 rc=0) ⇒ 剩下: 原理图/密集布线/打样 |
| ISS-263 | sw-lead | 2026-11-20 | ★★[主线内·软件/工具链侧·demo 头号卡点·内部活] ★★★★[ISS-155 blocker 的 E-11/E-12] ★**官方独立工具链 `rknn3-toolkit 1.2.0` 本机安装实测 + `config(target_platform='rk3572')` 实跑 + 一次完整模型转换** ★★ ⇒ ★**把「RK3572 的 .rknn 到底能不能转出来」从 [0数据] 变成有实测数** ★ |
| ISS-353 | sw-lead | 2026-11-24 | ★★[★新主线·PCB 线·模型链·rk3572 目标口径清账·纯口径·零写板] ★★【ISS-263 (2026-11-17) 已实测 `rknn3-toolkit 1.2.0` 支持 `config(target_platform='rk3572')` rc=0 (错 target `rk3576` 反而抛 ValueError 且报错原文含 `rk3572`) ⇒ ★**「rk3572 不是合法 target ⇒ 只能用 rk3576 target 转」这条路线已经过时** ⇒ ★**但全仓口径仍大面积停在旧口径** ⇒ 本单 = ① 全仓清账 (比名单·不许只报数) ② 板端接受性 [0数据] 的自研降级方案 (★不许用「买块 RK3572 板」来解·老板 2026-11-04 19:10 指示★) ③ 给 main 一条结案建议 (ISS-155 的 blocker 能不能降)】★★ ★**只改口径·不动板·不落表·不新增拍板项·零外发**★ |
| ISS-087 | sw-lead | 2026-10-29 | 模型许可未清 (L1 许可[0数据] + L4 AGPL-3.0 商用受限) + ARS45 板端模型 0 个 → 量产评审放行门禁 |
| ISS-090 | sw-lead | 2026-10-29 | ★软件侧交叉评审 (时序/信号/电源时序) + TMP117 测点物理位置 + 跨铰链 USB 烧录可行性 |
| ISS-101 | sw-lead | 2026-10-29 | ★模型许可: 唯一许可干净候选 (Apache-2.0) 的 NPU 可转换性 = 0 数据 → 量产可用模型清单为空 |
| ISS-110 | sw-lead | 2026-10-29 | ★RKNN 转换链实测 (RK3576 资料维度实测 + 端到端 ≤60ms 判定) —— 已交付并验收 |
| ISS-146 | boss | 2026-11-03 | ★★[等老板一句] demo 板形态: 模组+转接板 (我的建议) 还是 自制整板? —— 决定 PCB 与周期 |
| ISS-151 | main | 2026-11-04 | ★★[硬件优先] 替代料候选清单: 每类物料 ≥3 个公开在售替代品 + 来源/规格/数据来源评分 ⇒ 让「都试过了」可核查 |
| ISS-080 | sw-lead | 2026-11-05 | S2 救砖链路 (进 BOOT 模式 → 厂商下载工具识别 → 刷回来) 必须实测 —— 量产一票否决项 |
| ISS-114 | main | 2026-11-05 | ★★换芯片选型总单: 国内 TOP10 厂商 × TOP1~5 芯片 × 9 项打分 (老板 10-29 09:59 改令) —— 正式弃用酷芯微 |
| ISS-124 | sw-lead | 2026-11-05 | ★★[待瑞芯微/RK3576 模组厂] ISP MP/s 吞吐上限 + ISP 动态功耗 vs 吞吐曲线 (2 问, 一票否决级的剩余部分) |
| ISS-127 | mech-lead | 2026-11-05 | ★★★脱模斜度致镜脚 H 链最坏 −0.577mm ⇒ 几何上做不出来 (不是余量紧张, 是不可行) —— 量产架构必须改 |
| ISS-138 | boss | 2026-11-05 | ★★★[要老板一句拍板] sensor 模式选路: OV04C10 @1080p60 ⇒ 镜头/FOV/角分辨率/快门 四个代价要选一边 |
| ISS-164 | main | 2026-11-05 | ★★[等老板一句] demo 精度验收线: yolov5n F1 0.2927 差 0.0073 不达 0.30 门槛, 换 yolov5s 过线但 60ms 退到 62.67~64.18ms ⇒ 两条路都不平 |
| ISS-132 | main | 2026-11-06 | ★★★[决定性] 视涯 0.49" 1920×1080 是单色还是全彩? —— 这题决定产品定义 (检测框能不能上色) |
| ISS-137 | main | 2026-11-06 | ★★[可执行, 一行代码的活] 把「显示合成段」从 T_FIXED 里单独打点 —— 它是 RK3572 + 1920×1080 下 60ms 成败的关键未知数 |
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
| ISS-194 | hw-lead | 2026-11-13 | ★★PIN-SET-2 孔位表【套B ⇒ 套A】: hw-lead 自己 5 个产物里 4 个写套A, 只有 pcb60x30_check.py + 它的 .json 写套B (S1 y=2.5 / S2 y=27.5, 孔壁距边只剩 1.80mm) ⇒ 而那份 .json 是 ISS-118 的验收产物 ⇒ 若 PCB 按套B 钻, 螺钉与打印包笼孔差 7.50mm ⇒ 板装不进骨架 |
| ISS-198 | hw-lead | 2026-11-13 | ★★[主线内·原理图侧·内部活] `PIN_REALITY_GAP.md` 里 29 个 `[0数据]` 的真实脚数 ⇒ 根因 = `state/gen_kicad_sch.py` 的三张查找表 (★不在 BOM★) ⇒ 补表 ⇒ 降到下限 3 (★老板【选项③ 真实器件全貌】的内部一半输入★) |
| ISS-205 | sw-lead | 2026-11-14 | ★★[主线内·原理图侧·内部活] ★★KiCad 导出 BOM 里 186 个位号带 `?` (★板厂看到的位号与丝印对不上★) ⇒ ★★真根因已实测钉死 = 【KiCad 判「已标注」的条件是位号末字符为数字】⇒ ★★解法 = 给位号加 `_1` 数字后缀 (★★不是去掉下划线 —— 实测去下划线无效且会让位号不可读★★) ⇒ 改在生成器里★★ |
| ISS-038 | boss | 2026-11-18 | 【缺角色】工业设计 (ID/CMF/佩戴舒适度) 无人负责 —— 需老板拍板是否加第 4 个总工 |
| ISS-041 | boss | 2026-11-18 | ★★[当前 demo 板] 测试条件缺失 ⇒ G3 那一关不可判通过 (★2026-11-04 09:57 起: 不含热电偶/假皮肤, 老板已定 demo 板不考虑温度) |
| ISS-060 | boss | 2026-11-18 | 产品件三条几何待老板裁决 (压垫吸收量零余量 / 非对称方向 / 压垫槽区板厚小于 FDM 最小壁) —— 打印包转绿不等于解 A 收口 |
| ISS-063 | boss | 2026-11-18 | 显示端 120 度到 30 度的映射方式 (看得广但糊 vs 看得清但窄) —— 120 度这个卖点对用户可见吗 |
| ISS-097 | boss | 2026-11-18 | ★"关机"语义: 硬件断电通路 (负载开关) + 真关机拓扑 + 功耗预算 V3 |
| ISS-106 | boss | 2026-11-18 | ★新增渠道: 经酷芯微代理转达 (老板 10-28 找到代理) —— 代理信 + 3 份可转发附件已就绪 |
| ISS-116 | boss | 2026-11-18 | ★★工作方式改造: 老板任务先落 GitHub 总表 + token 守护 (老板 10-29 09:59 亲自要求) |
| ISS-211 | hw-lead | 2026-11-18 | ★★[主线内·原理图/网表侧·内部活] 现行网表自身 4 处自相矛盾 (I2C_A 上拉行 vs 器件行 / BAT_DET 分压链全 DNP 但 SoC ADC 脚必装 / U_EN_SW 无器件本体行 ⇒ BOM 登记成 NET / USB D− 无 ESD 而器件自称双通道) ⇒ 出落表规格 + 机器门禁 (不改网表·不改板) |
| ISS-212 | sw-lead | 2026-11-18 | ★★★[demo 头号路径·自己查版·软件/显示侧] demo 显示侧口径重锚到 Waveshare 2.8" (480×640 · 2-lane · 无需 DCS init · I2C_B ≤100kHz) + 逐处定性表 + 机器门禁 (SW 侧对 demo 屏至今零提及) |
| ISS-307 | hw-lead | 2026-11-18 | ★★[主线内·选型研究类·内部活] ★★【板那一趟的 ESD 选型轴: 老板 ①② 两个字母 (W-2 补不补 D− / W-1b·W-1c 真 OPN 型号轴) 现在拍不了, 因为没有候选集 ⇒ 本单用【官网】证据把两条路径各交一份候选集 + 落位可行性 + 量化代价 ⇒ 让老板只需回【need key + 决策码】就能一次拍完】★★ ⇒ ★**纯分析/选型研究类 · 零写板 · 零落表 · 零改闸 · 零改网表 · 零外发 · 不替老板拍板** ★ |
| ISS-308 | hw-lead | 2026-11-18 | ★★[主线内·分析/作业包类·内部活] ★★【「板那一趟 S8 (unconnected 45 → 0)」的可达性判决书: 残余 22 网名逐条归 5 桶 (老板字母 / GND 卡死 / 差分 N 腿互掐 / 让路闸靶子 / 其它) ⇒ 交出【老板还差 N 个字母 (N 必须是具体数字)】+【现在就能做的技术活清单】+【S6 落位增补表草案】】★★ ⇒ ★**纯分析/作业包类 · 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板** ★ |
| ISS-102 | main | 2026-11-19 | ★[待原厂] 追加问 4 条: AON 域静态电流 / USB VBUS detect 脚 / TPS62130A PG 极性 / BQ25896 VSYS 是否必接 |
| ISS-156 | main | 2026-11-19 | ★★[demo 供应链] 自研主板的三件前置选型: camera 模组 / 屏模组 / RK3572 核心板 (★主板的 FPC 座由模组倒逼) |
| ISS-172 | sw-lead | 2026-11-19 | ★★[主线内·硬件选型/官方口径侧·内部活] ★**负载开关 U_PWR_SW / U_EN_SW 选型证据矩阵** (★网表 L50 value 栏至今是「[待选型] …」⇒ 主板 BOM 出不来 OPN★) ⇒ ≥3 候选 × `HW/POWER_SHUTDOWN_V3.md §2` 八条判据逐条对照 + RCB 缺口做实 + 降级方案 + 机器门禁 |
| ISS-209 | mech-lead | 2026-11-19 | ★★[主线内·结构侧·内部活] 正中区光学腔体按眼盒 A_e ≤ 62 mm² + d=15–20mm 重排 (★ISS-208 §1.7 X-2 自己点名的下一单★) |
| ISS-210 | sw-lead | 2026-11-19 | ★★★[demo 头号卡点·自己查版·续] ISS-129/155 收口: 端到端 60ms 生死判定链 (补 ISP 段打点 + 判据固化 + 板永不到时的降级结论) |
| ISS-213 | mech-lead | 2026-11-19 | ★★[主线内·结构侧·内部活] 结构侧 54 项交叉复核逐条定性 (17 条 FAIL 挂在 rc=0 且不在每日巡检链上 ⇒ 隐形) + demo 板当前成立的真缺陷收口 + 机器门禁 (PCB 布线/布局 6 条只定性排队不许修) |
| ISS-214 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] 网表/规格自身矛盾第 2 轮 (USB 串阻双值 / P9 页 21p vs 22p / SARADC 满量程 / BAT_DET 漏电 / USB D− 无 ESD / ICHG 系数方向反 / NET-LED board 列) ⇒ 出落表规格 v2 + 扩机器门禁 (不改网表·不改板·不改生成器·零外发) |
| ISS-215 | sw-lead | 2026-11-19 | ★★★[demo 头号路径·自己查版·软件/时序侧] demo 板 60ms 生死判定链的显示侧口径重锚: 从退役的整机 1920×1080 (TX 7.776ms / 输出侧 10.09ms / 合成段 2.32ms) 改到 demo 屏现行 480×640 (TX 2.304ms / 输出侧 ~2.75ms / 余量 7.79ms) ⇒ 判据被算严了 3.4 倍 ⇒ 逐处定性 + 改写 + 机器门禁 |
| ISS-216 | mech-lead | 2026-11-19 | ★★[主线内·结构侧·内部活] MECH_BUDGET 充电耗散口径统一: 线性充电 IC 0.8W → 板上真实 buck (BQ25896) 0.45-0.57W ⇒ 文档 §2.1/§2.3.1/§3 + verify_budget.py 常量 + 门禁锚点对齐 + 新增 --selftest 口径自检 (端件 108°C / P_max 0.21W / 必须金属热路) |
| ISS-217 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] 12 组网表/规格自相矛盾 (ISS-211 四条 + ISS-214 八条) ⇒ 汇成【整链重出 第 1 步 · 原理图侧落表作业包 v1】+ 3 项补差 (imp 字段拆分 / ESD 阈值 5→3.0mm / π 滤波拓扑 + J_CHG 位号双义) + 门禁扩到"作业包漏一条就红" (不改网表·不改板) |
| ISS-218 | mech-lead | 2026-11-19 | ★★[主线内·结构侧·内部活] 打印包第三档试样落地 (10.50×4.80 FDM 直成型 + 10.25×4.55 金属·CNC · 两档并行试样已被判死) ⇒ 加工规格 + 加工余量 + 测量清单 + 生成器/自检落项 (既有 93/93 + 38/38 必须仍全绿) + 端件金属热路 u8 参数化重量账模板 (不预扣 §3) |
| ISS-219 | mech-lead | 2026-11-19 | ★★[主线内·结构侧·内部活] 镜框正中区第 2 轮重排: C-6 分光件按 A_e≤62mm² 放大 (光束 8.885 ⇒ 平板对角 15.39 / 棱镜 ≥9×9×5) + C-7 面板 468mW vs 腔体 50°C (81.20°C ⇒ 需 4669mm² 散热面 ⇒ 金属热路方案) + C-C/X-3 鼻梁热路径 54.33°C 与「不进皮肤热路径」口径修正 + 铝 6063 k=237→201 官方保守口径统一 + 机器门禁 (不改 HW·不碰 PCB 布线布局·不预扣 §3 重量) |
| ISS-220 | hw-lead | 2026-11-19 | ★★★[主线内·原理图/网表侧·内部活] 【整链重出 第 2 步 · 原理图侧落表执行】把 ISS-217 作业包 28 条里「不依赖 6 条待裁 V-1~V-6」的条目真的落进真源 (SPEC.json / gen_netlist.py / gen_schematic_pages.py / CHARGE_BOARD_SPEC.md 等) + 重生成网表/脚表 + 让机器门禁的「未落表条数」实打实下降 (50 → N) + 逐条标出哪些条目落表后需要板侧同步 (★允许改真源 = 这是主线核心★ · 不许碰板/PCB 布线布局 · 不许代拍 V-1~V-6) |
| ISS-221 | sw-lead | 2026-11-19 | ★★[主线内·软件/时序侧·内部活] demo 屏 (2-lane@480×640) 自己的 60ms 预算真源脚本 `SW/tools/demo_e2e_budget.py` + 把 demo 判据链的数字从「整机脚本减出来的」换成「demo 真源算出来的」 + 机器断言 (判据链不许再引用整机 4-lane 常量) + 收口 SW/RKNN_BENCH.md 的 S9 注记分叉 (不改 HW·不改任何板端实测数字) |
| ISS-222 | mech-lead | 2026-11-19 | ★★[主线内·结构侧·内部活] ISS-219 的 C-6 / C-7 / C-8 三条「只报不改」落进结构真源: C-6 分光件 11×11×1.5 + 2×9×9×5 (0.9697cc / W4 3.68-7.36g) 替换旧 M6 14×10×6 + C-8 t_s=6.0 与 45° 平板竖向投影不自洽 ⇒ 自己实算 t_s 并重算三档 T=18/21/23 + C-7 集热面 3600mm² 可行性自己实算 + 机器门禁扩项 (不改 HW·不碰 PCB 布线布局·不预扣 §3 重量) |
| ISS-223 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] ISS-220 收尾 (补落 3 条分片声明) + 落表第 2 批 (★V-1 已由项目总工裁: USB 串阻 = 22Ω±1% ⇒ d5 + 补差A 值迁移 20 条★) + 修 ISS-217 作业包 F-1~F-5 五处 + V-3 的 RK3572 SARADC_VIN5 官方参数自查 (★把 BAT_DET 分压比从「拍不了」变成「可拍」★) |
| ISS-224 | mech-lead | 2026-11-19 | ★★[主线内·结构侧·内部活] `MECH/check_demo_struct_truth.py` 三组失配的再基线化: ISS-220 落表让 `PIN-MISMATCH` 由 FAIL 变 PASS (= 真修复, FAIL 17→16) + 网表/脚表 md5 随落表变 ⇒ G1/G1b/G5b 旧锚点失效 ⇒ 重锚 + 留痕 + 保住「不许把红灯调没」不变量 + 把「受保护 md5」升级成「真源 md5 + 落表台账核对」 |
| ISS-225 | sw-lead | 2026-11-19 | ★★[主线内·软件/工具链侧·内部活] SW 侧 md5 基线过期 (`SW/tools/check_demo_panel_spec.py` R6 恒红) ⇒ 重锚 + 落表台账对账 (镜像 MECH C21) + 同根因全清单 + 反向用例 + 留痕 |
| ISS-226 | sw-lead | 2026-11-19 | ★★[主线内·软件/光生物安全判据侧·内部活] 光生物安全的「出瞳白场辐亮度最大值」在 SW 侧亮度控制策略里可判化: 蓝光通道占比上限 25% (名义 8.26%) 落进策略 + 亮度 API 蓝通道占比可标定量 + 机器门禁 + 反向用例 |
| ISS-227 | mech-lead | 2026-11-19 | ★★[主线内·结构/热路口径侧·内部活] ISS-222 产物的 C-7b 物理口径错修正: P3 把「镜框上沿 120×30 打印件顶面」当成与铝条同温的集热面 (R 398.9 vs 47.6 K/W, 差 8.4 倍 ⇒ 实算腔体 53.60 °C ❌) ⇒ 集热面改铝制背板 + 三档重算 + 门禁 + 留痕 |
| ISS-228 | sw-lead | 2026-11-19 | ★★[主线内·硬件选型/官方口径侧·内部活] RK3572 GPIO0 (I2C0_SCL=GPIO0_B0 球 1K21 / I2C0_SDA=GPIO0_B1 球 U32) → VCCIO 供电组官方映射自查 ⇒ 让「I2C_A 上拉最终电压域」可拍 (★回掉 hw.yaml 逾期 13 天的 need `iss148_rk3572_gpio0_vccio_domain_check`★) |
| ISS-229 | mech-lead | 2026-11-19 | ★★[主线内·结构/热路侧·内部活] 充电时皮肤侧温度【按改正后的系数】重算 (★0.822 是倒方向的旧值 ⇒ 「390Ω 档 42.14°C」无有效数字★ ⇒ 直接改写 V-4 建议默认值★) + 附带 MECH 闸 G5b/C21 重锚 (ISS-223 落表后锚点过期) |
| ISS-230 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] 落表第 3 批【逐字改法映射 v2】(★把 21 条未落表从「等老板拍板」变成「拍完就落」★: V-3 13 条 + V-2 4 条 + V-4 1 条) + 修 §7 充电板清单的非法 CSV + 加 F-3 加强型断言 + 标作废一处过期温度结论 |
| ISS-231 | sw-lead | 2026-11-19 | ★★[主线内·软件/门禁侧·内部活] SW 侧 R6 锚点重锚 (★ISS-223 落表后【按设计】变红的一盏灯, 走 ISS-225 台账 H-1 流程★) ⇒ 收口 `check_demo_panel_spec.py` 的 rc=1 (基线红 ⇒ selftest 只有 15/16) |
| ISS-232 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] 板↔网表【焊盘级等价】门禁红的 2 处「多余」(C_VBUS_GND pad1=GND / pad2=VBUS_5V_CHG) ⇒ 定位根因 + 给网表侧逐字修法 (★板侧不许碰★) |
| ISS-233 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] `--expect-resolved` 21 条未落表 ⇒ 逐条归因 + 【不依赖老板拍板的那批当场落表】 + 出【V-2/V-3/V-4 拍板即可一键落】的逐字清单 ⇒ 把原理图定稿的最后一截推完 |
| ISS-234 | sw-lead | 2026-11-19 | ★★[主线内·软件/接口侧·内部活] 【关机 / 待机 / 关机充电指示灯】三条口径 ⇒ 出【真断电 vs 深睡关机 × demo 板 vs 整机】两套可落表方案 + 硬件最小需求 (负载开关选型判据) + 功耗账 + 机器门禁 ⇒ 给老板一页可拍 (★与 ISS-097 / ISS-172 同批★) |
| ISS-235 | sw-lead | 2026-11-19 | ★★[主线内·软件/接口侧·内部活] ★**ISS-233 落表把 SW 侧 3 条断言打成过期红** ⇒ 订正 `timing_check.py` F8 / REV-3 + `check_demo_panel_spec.py` REV-12 (★订正不是放宽★) + 每条补反向自证 ⇒ SW 门禁回全绿 |
| ISS-236 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] ★**把 ISS-233 的【拍板即落清单】做成参数化【一键落表器】(V-2 / V-3 / V-4)** ⇒ ★**老板拍板 = 一条命令落表 (默认 dry-run·不落任何值)** ★ + 出【原理图定稿收口清单】(★还差什么才能定稿★) |
| ISS-237 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] ★**P2 屏口径自相矛盾** (STEP1_PARTS_SPEC.md §0/§3 = 40p/8HD/12V BOOST vs §6 S1 + 现行网表 = 22p/Waveshare 2.8") ⇒ 收死 P2 + 清残留 + M1~M11 落成约束 × 网表逐条对账 + 机器门禁 |
| ISS-238 | mech-lead | 2026-11-19 | ★★[主线内·结构/判据侧·内部活] ★★`MECH/display_biosafety_v2_check.py` C1 红灯 (走鹃旧口径 活动口径=5) ⇒ 4 处假阳性 (判据只认单一标注串) + 1 处真漏标 (L880) ⇒ 文档侧补标 + 判据侧放宽提案 + 新机器门禁 |
| ISS-239 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表侧·内部活] ★**TPS7A20 族 7 颗 LDO 的引脚功能名在脚表里串号** (★pin4 的 IN 被写成 "EN (pin3)" · pin5 的散热焊盘被写成 "GND (pin2)" ⇒ 脚表上看不到 IN 脚★) + ★**U_LDO_S28 整颗缺 pin3(EN) 脚** ⇒ 35 行逐脚对账 + 根因定性 + 逐行改法映射 + 独立机器门禁 |
| ISS-240 | mech-lead | 2026-11-19 | ★★[主线内·结构/判据侧·内部活] ★★跨铰链 FPC 几何账【三套口径】互相打架 (★脚本「收敛版」= 硬编码 16p/20p ⇒ 而网表真源已是 camera 31p/**0.3mm** + display 22p/0.5mm · ★脚本把 camera 按 0.5mm 算 ⇒ 声明版 31.5mm 高估 6.2mm · ★`CROSS_LINKS` 里的 `CONN_USB` 在网表里【一行都没有】(demo 板 USB-C = `J_USB_C` 在主板·不跨铰链) ⇒ 径向占位按 4 条链算 4.4mm·真实 3 条 = 3.75mm · ★`MECH/check_demo_struct_truth.py` G7 把分片 claim `mech_hinge_stack_fixed_mm` = **25.00** 当现行值钉死 (★而 25.00 = 16p@0.5+20p@0.5+4p@0.5+10p@0.5, 与真值 25.3mm 构成完全不同 = 两个不同的错凑出的巧合★) · ★正文 `MECH/USB_HINGE_STRUCTURE.md` L90/L91/L96 还写着 `CONN_CAM (40p)` / `CONN_LIGHT (40p*)` / 「网表值列根本没写 pin 数」⇒ 而网表 L237 早写明 22p@0.5mm ⇒ 脚本 §4 只查关键词 + 4.4/25.0 两个数 ⇒ 这 3 处旧口径【隐形通过】★) ⇒ 三口径收口 + 逐条改法映射 (只报不改网表/板) + 新建独立机器门禁 (带反向用例) |
| ISS-257 | hw-lead | 2026-11-19 | ★★[主线内·原理图/选型侧·落表执行·内部活] ★★G1a-7「选型已落表」: ★**BOM 里 14 件必装器件 value 至今写「[待选型]」(D_ESD_CAM/D_ESD_DEMO/D_ESD_TC/D_ESD_USB_D/D_TVS_VBUS/FB_DEMO/FB_VBUS/Q_AND/Q_CHG_LED/Q_ENVC/Q_PG/R_SUPV_DIV1/R_SUPV_DIV2/U_PWR_SW) ⇒ 落成真型号 + 重生成链 (网表→脚表→BOM→原理图) ⇒ `state/check_stage_g1a.py` 的 G1a-7 转绿** ★★(★**证据矩阵已在盘: `HW/PART_SELECTION_MATRIX_2026-11-16.md` 22/22**★) |
| ISS-260 | hw-lead | 2026-11-19 | ★★[主线内·原理图/网表/选型侧·工具自测·内部活] ★★★**`state/land_v_values.py` 的 V-2 落表路径在 ISS-257 落表后已失效** ★★(★`--decision V-2=1` ⇒ **rc=3**「旧值出现 0 次 (期望 1 次)」⇒ 决策页承诺的「A1+A2+A3 一并拍 ⇒ 一条命令 ⇒ 15 条一次落」**A3 那格当场失败**★) ★ + ★★**补 `--selftest` (★本项目所有闸都有, 只有落表器没有 ⇒ 上游落表把锚点打漂这类漂移没有任何机器会主动报★)★ + ★★**出 A3/W-1 语义冲突的选项表 (★「光把锚点改回去」是错的:会把 ISS-257 刚落下的真型号覆盖成判据串 ⇒ G1a-7 刚转绿被自己 undo★)★** |
| ISS-265 | hw-lead | 2026-11-19 | ★★★[★新主线·PCB 侧·布线死因·内部活] ★★★**7 条布线臂全打死同样 3 条差分腿 ⇒ 布局级线索 ⇒ 出【根因对照表 + 布局修正规格页 + 布线可行性预判】(★纯分析·零写板★)** ★ |
| ISS-283 | hw-lead | 2026-11-19 | ★★[主线内·HW/落表侧·内部活] ★★【三件落表 + 一个工具接口死锁】★★ ★**B1: V-2 (A3) 落表被行号锚点守卫拦死, 必须解锁** ★ (★根因 = V-2 落表动作 = 把 `D_ESD_USB_D` pad1 的网名 `USB_D_P_SRC` 改成 `NET_USB_D_P_TYPEC` ⇒ 改的是守卫的【实体身份 (ref+net)】⇒ 判 RED ⇒ 落表器自动回滚★) ★ ★★ **B2: W-4 (P4/G-1) `Q_PG` 写法 A 落表** ★ (★S=BAT_SW / D=ON / G=PG★ ⇒ ★**并且 pad1↔pad3 的网要互换**★ ⇒ ★DMP3098L 引脚序 1=G/2=S/3=D★ ⇒ ★**板那一趟必须重画 Q_PG 的 land**★) ★ ★★ **B3: G-5 (P6/W-6) LED 亮度档落表** ★ (★R_LED_R 1k→68Ω · R_LED_G 1k→55Ω = 20mA 档★) ★★ ★(★老板 2026-11-17 09:49「按照你的建议执行」⇒ 这 8 条已落账★) ★ |
| ISS-284 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·门禁/台账机制·内部活] ★★【P10 落地: SW 台账 `hard_protected` 怎么合法跟上「板只改一次」】★★ ★⇒ ★**老板 2026-11-17 09:49 拍板 = 方案 ② (保留纯 md5 + 显式单号背书的合法改板动作)** ★ ⇒ ★**自带一条缝必须一起堵**: 「单号与 md5 可各自独立编辑 ⇒ 有缝 ⇒ 必须做成【一个字段两个值】且台账里查得到」★ ⇒ ★**三条红线一条不许动** (不许「随手改 md5 就绿」/ 不许放宽「盘上≠链头⇒红」/ 不许把「取不准」放宽成「取最近一条」★ ★ |
| ISS-288 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·门禁口径收口·内部活] ★★【把 ISS-285 设计好的补丁真正落进 `SW/tools/timing_check.py`】★★ ⇒ ★**ISS-285 当时判定「情形一: ISS-283 未落 verified」⇒ 只出设计不落补丁★ ⇒ 现在情形二成立 (ISS-283 已于 12:30:23 落表并 verified) ⇒ 补丁必须落地** ★ ⇒ ★**当前 3 条红 (★main 14:0x 实跑★)**: ① 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 ② 网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账 ③ F4' 实读: BAT_DET 三颗全 DNP (★落表后已改必装 ⇒ 该期望过期★) ⇒ SELFTEST 68/71 · rc=1★ ★ |
| ISS-310 | mech-lead | 2026-11-19 | ★★[主线内·MECH 侧·板框口径对照类·内部活] ★★【板框口径「两套并存」的代价对照 + 机器可判的可行域表 ⇒ 交 main/老板一次拍 U-1 / P7】★★ ⇒ ★**纯分析/作业包类 · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★ |
| ISS-311 | hw-lead | 2026-11-19 | ★★[主线内·HW 侧·产出链重出清单类·内部活] ★★【「板只改一次」那一趟要重出哪些件: C1 焊盘级等价差 2 个 (网表 480 / 板上 482) + 投产包原理图源文件 11 个不一致 ⇒ 交一张逐件的【重出清单 + 顺序 + 同趟出 + 验收判据】作业包】★★ ⇒ ★**纯分析 / 作业包类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★ |
| ISS-312 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·判据修复类·内部活] ★★【ISS-309 的 need 落地 (★main 已拍板: 修法 A+B 都要★): 权威判据 `check_demo_panel_spec.py` 对【链头落表单号】只查「非空」⇒ 改坏单号判绿 ⇒ 修判据 + 3 条新反向用例 (★真单号假不了★)】★★ ⇒ ★**判据修复类 · 零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · 零外发 · 不替老板拍板** ★ |
| ISS-313 | mech-lead | 2026-11-19 | ★★[主线内·MECH 侧·需求闭环类·内部活] ★★【MECH 域 needs 184 条四分类处置 (waiting_on 空 113 / agent 34 / boss 20 / vendor 10 / jbd 6) ⇒ 把机检缺口清单那条「108 条没人答」+ 「16 条外部依赖挂着」两笔老账一次清掉】★★ ⇒ ★**需求闭环类 · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★ |
| ISS-314 | hw-lead | 2026-11-19 | ★★[主线内·HW 侧·口径收口 + 沙盒预演类·内部活] ★★【「板只改一次」那一趟的 S1 位号改名口径收口: 作业包 §5「网表/脚表/BOM 逐字节不变」与 §3-S1「板侧 156 个封装位号加 `_1`」★**自相矛盾** ⇒ C1 从「多余 2」变成「缺失 350 · 多余 352」⇒ 交一份【口径决策包 + 沙盒预演实测】★★ ⇒ ★**纯分析 / 作业包类 + 沙盒预演 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★ |
| ISS-315 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·判据修复 + 新闸新建类·内部活] ★★【判据链收口: 把 ISS-312 收回去的「修法 B (链头落表单号 ↔ 独立信源交叉核对)」铺到 `check_r6_hard_protected()` 硬保护路径 (★前置 = 先修 ISS-298 闸的沙盒夹具★) + 立「落表留痕义务」机器可判新闸 (★可挂不挂·挂闸由 main★)】★★ ⇒ ★**判据修复类 + 闸新建类 · 零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · 零外发 · 不替老板拍板** ★ |
| ISS-316 | mech-lead | 2026-11-19 | ★★[主线内·MECH 侧·输入包 + 决策一页类·内部活] ★★【「板只改一次」那一趟的结构侧输入包: ①板框冻结闸 U-1 的【决策一页 + 机器可判判据】(★板框是所有其它拍的输入★) ②结构侧那一趟要【同批出】的件清单 + 与 HW 侧清单的【交叉对账差集】(★= 「板改第二次」的风险清单★) ③两处既有文档订正的逐字改法 (★电芯型号错配 + 检修口盖板 +0.73g★)】★★ ⇒ ★**纯分析 / 作业包类 · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零重生成 · 零外发 · 不替老板拍板** ★ |
| ISS-317 | hw-lead | 2026-11-19 | ★★[主线内·HW 侧·可执行清单 + 判据设计类·内部活] ★★【「板只改一次」那一趟的 S1 位号改名: 把 ISS-314 的「口径决策包」升级成【三侧同口径的逐条改名清单 + NC 白名单撞死的三选项 + BOM 证据回填兜底的机器可判判据】★★ ⇒ ★**纯分析 / 作业包 / 判据设计类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★ |
| ISS-318 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·判据新建 + 挂链体检类·内部活] ★★【「板只改一次」那一趟的 SW 侧: ①把那 95 处位号引用做成【机器可判的重命名影响面闸】 ②把 ISS-315 新立的两道闸 + ISS-312/ISS-309 的两道 selftest 的【挂链前体检】做完 (★ISS-309 那道从 11-17 拖到现在还没挂★)】★★ ⇒ ★**判据新建 + 判据修复类 · 零写板 · 零落表 · 零改 `state/gate_check.py` (★挂闸是 main 的机制地界★) · 零外发** ★ |
| ISS-319 | mech-lead | 2026-11-19 | ★★[主线内·MECH 侧·对账 + 影响面类·内部活] ★★【「板只改一次」那一趟的 MECH 侧: ①把 ISS-316 的 26 条差集【逐条落到 owner + 落表批次 + 验收判据】 ②电芯型号订正的【真实影响面是 47 行 / 19 个活文件 / 3 个脚本】(★ISS-316 只点了 MECH_BUDGET 的 8 行★)】★★ ⇒ ★**纯分析 / 对账 / 作业包类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★ |
| ISS-320 | mech-lead | 2026-11-19 | ★★[主线内·MECH 侧·受限文本订正类·内部活] ★★【电芯型号订正【实做】: 把 ISS-319 查清的那 47 行里的 33 行【真改掉】(MECH 域 19 个文件·含 9 个脚本) —— 只把 `ICP582035PR-01` 替换成 `ICP422339PR`, ★**一个尺寸/重量/容量常量都不许动** · 11 行留证/对照行一行都不许碰 ★**】★★ ⇒ ★**受限文本订正类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零外发 · 不替老板拍板** ★ ⇒ ★**为什么现在做 (★main 已拍★)**: 照现型号采购 ⇒ 到货厚 6.40mm (不是 4.60) ⇒ 装不进 7.30mm 镜脚 ⇒ 电芯段 H 链最坏 −1.10mm ⇒ ★**这笔比文档订正本身更贵, 且与 U-1 板框决策完全无关 ⇒ 可并行走, 越早越省钱**★ |
| ISS-321 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·纯分析 / 作业包 / 判据设计类·内部活] ★★【「板只改一次」那一趟的 SW 侧: S1 位号改名 (五侧同口径 · 186 个要改) 到底会不会把 SW 侧的 12 道判据脚本炸掉 —— 逐条实测 + 逐条逐字改法 + 执行顺序表】★★ ⇒ ★**纯分析 / 作业包 / 判据设计类 · 零写板 · 零落表 · 零改闸 · 沙盒只写 tmp/ + logs/iss321/** ★ |
| ISS-322 | hw-lead | 2026-11-19 | ★★[主线内·HW 侧·布线归零作业包 + 死因逐条登记类·内部活] ★★【「板只改一次」那一趟的 S8 (布线归零 unconnected 45 → 0): 45 条逐条死因登记 + 23 条高速 DSI/CSI 腿的几何可布性判定 + 逐条修法/落表批次/验收命令作业包】★★ ⇒ ★**纯分析 / 作业包 / 判据设计类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM/原理图真源** ★ |
| ISS-323 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·逐字可执行清单类·内部活] ★★【「板只改一次」那一趟的 SW 侧: 7 件必须同批改的活 (ISS-321 执行顺序表 #1~#7) 做成【逐字可执行清单】: 每件给 改哪个文件 / 改前逐字 / 改后逐字 / 行号锚点 / 验收命令 / 归属 / 不改的后果 / 时序】★★ ⇒ ★**纯分析 / 作业包 / 判据设计类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★ |
| ISS-324 | mech-lead | 2026-11-19 | ★★[主线内·MECH 侧·落位口径 + 候选坐标类·内部活] ★★【`D_LED_G` 落位口径一页 (G12 的前置): 93.492727mm 复算与根因分解 + 双板框假设坐标空间 + 出光孔有孔/无孔两假设 + G-5 亮度档事实订正 + ≥3 个候选落位点 + 给 hw-lead 的 `PCB_PART_POS` 候选行 + 机器可判判据建议】★★ ⇒ ★**纯分析 / 作业包 / 判据设计类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★ |
| ISS-325 | hw-lead | 2026-11-19 | ★★[主线内·PCB 线·沙盒预演 / 作业包类·内部活] ★★【「板只改一次」那一趟的 S8 前置: 「左上布局」21 器件 (10×R_SEL_* + 10×TP_DSI_*) 钉位沙盒预演 —— 把 ISS-322 的处方第一次真正单变量实跑一遍 (三方对照 unc / 网名集合差集 / 名单制闸 / 段内 P-N 翻转) ⇒ 回答「S8 归零到底可达不可达」】★★ ⇒ ★**纯沙盒预演 · 零写板 · 零落表 · 零改闸 · 零改生成器代码** ★ |
| ISS-326 | mech-lead | 2026-11-19 | ★★[主线内·MECH 侧·判据安全性体检类·内部活] ★★【S1 位号改名「MECH 侧」安全性体检: MECH 域 10+ 个判据脚本硬编了 218 行改名表里 186 个待改名 ref 中的至少 18 个 (J_DEBUG/J_UART/J_USB_C/J_CHG/CONN_CAM/CONN_LIGHT/D_LED_G/R_LED_G/R_SEL_D0_N/R_SEL_D1_N …) ⇒ 区分【崩】(check_board_frame_coords.py L999 `fps[LED_REF]` 直接下标) vs 【假绿】(check_onepass_struct_crosscheck.py L1107/L1129 `t["ref"] == "R_SEL_D0_N"` 改名后永不匹配) ⇒ 再补 MECH 域【从没有过】的位号可达性闸设计稿 (只给设计, 不挂链)】★★ ⇒ ★**纯体检 + 沙盒实证 · 零写板 · 零落表 · 零改闸** ★ |
| ISS-327 | sw-lead | 2026-11-19 | ★★[主线内·SW 侧·沙盒验证 + 当天 SOP 类·内部活] ★★【S1 位号改名「SW 侧」改名后【闸链复活】验证: 在沙盒里把整棵树改名后跑完 10 道 SW 闸 ⇒ 交【改名前 / 改名后·重建注册表前 / 改名后·重建注册表后】三列读数表 +「板那一趟」当天的 SW 侧可执行 SOP (每步命令 + 期望读数 + 回滚三档) + 「真隐患不许被 --freeze-registry 洗白」的反向用例 + 判据设计稿 (只给设计, 不挂链)】★★ ⇒ ★**纯沙盒验证 · 零写板 · 零落表 · 零改闸** ★ |
| ISS-126 | main | 2026-11-20 | ★★板厚档位未定 ⇒ 检修口净空只有 4.90 那一档过 (1.22mm 档净空 4.48 破 4.50 硬要求) |
| ISS-128 | main | 2026-11-20 | ★★主控换 RK3572 ⇒ 板面积账 + 逃线层数全部重算 (封装 FCCSP550L 14.3×15.5mm / 550 球, 比 RK3576 小) |
| ISS-129 | main | 2026-11-20 | ★★★RK3572 (4 TOPS) 板端纯 NPU 实测 ⇒ 端到端 60ms 硬指标生死判定 (★T2 翻案条件推算已命中) |
| ISS-130 | main | 2026-11-20 | ★★★RK3572 功耗 670mW (原厂口径) vs 贴皮肤 43°C 红线 —— 从「待定」变「可判」 |
| ISS-133 | main | 2026-11-20 | ★★★显示架构变更: '屏' ≠ '光机' ⇒ 必须新增一级耦合光学 ⇒ 镜框光学腔体/分光器/整机空间全部重算 |
| ISS-169 | main | 2026-11-20 | ★★[demo 板可制造性] demo 主板的边界已定 (Type-C 供电 · 不装电池 · 板上只有这一块) + SoM 座的 pin1 排向待查证 + 15 个器件的封装脚号待落定 |
| ISS-241 | sw-lead | 2026-11-20 | ★★[主线内·硬件选型/官方口径侧·内部活·排队] ★★BOM 里 value 仍写「待选型」的必装器件 = **21 件** (★ESD 阵列 ×4 · π 滤波磁珠 ×2 · TVS ×1 · MOS ×4 · LED ×3 · 按键 ×5 · 电容 ×1★) ⇒ 主板 BOM 出不来 OPN (★**排除 `U_PWR_SW`/`U_EN_SW` = ISS-172 在办 · 排除 40 条 DNP · 排除 R/C 通用品★) ⇒ ≥2 候选 × 官方参数 + 在售型号 + **封装必须落在板文件现有 2/3 焊盘占位上** + 降级方案 + 机器门禁 |
| ISS-242 | hw-lead | 2026-11-20 | ★★[主线内·原理图/网表侧·内部活] ★★网表/板 第 3 轮自相矛盾 3 条 (★main 2026-11-16 13:4x 本机自验★) —— ① C_VBUS_OUT/C_VBUS_GND 两颗 2 脚电容各落进 3 个网 (导出后一脚悬空) ② J_CHG 位号撞车 (网表 = 1×10p@0.5mm 铰链 FPC 座 · 脚表 17 行; 板文件上同位号 = 封装名空 + 仅 2 焊盘 + 仅 1 条 fp_line 的 SoM BTB 占位) ③ 板文件 41 颗 MAIN_PCB+DNP 位号零 DNP 标记 (exclude_from_* = 0 处) ⇒ 贴片厂会当必装贴 |
| ISS-243 | hw-lead | 2026-11-20 | ★★[主线内·原理图/网表侧·内部活] ★★ISS-241 交卷的 4 条落表前置 (L1~L4) 收口: ① **L1/G-6 `C_REGN` = 1µF → 4.7µF(10V) 官方值订正** (★TI BQ25896 pin22 原文要求 4.7µF ⇒ 网表 L44/L45 + 脚表 + BOM 三处★) · ② **L2/G-2 三件 MOS 的占位 pad↔pin 映射表** (★实测 `Q_AND`=D/S/G · `Q_ENVC`=G/S/D · `Q_PG`=S/D/G ⇒ SOT-23 库序 G/S/D ⇒ 必重画 land★) · ③ **L3 `D_ESD_CAM` pad1=GND 与另两件反序 ⇒ 单向 ESD 件会接错** · ④ **L4/G-8 充电板侧 6 件器件 footprint 全「待定」** (★`D_ESD_TC`/`FB_VBUS`/`D_TVS_VBUS`/`Q_CHG_LED`/`D_CHG_LED`/`C_REGN`★) ⇒ **L1 直接落表 (官方值, 无需拍板) + L2/L3/L4 出逐字改法映射 (只报不改板)** |
| ISS-244 | sw-lead | 2026-11-20 | ★★[主线内·硬件选型/官方口径侧·内部活] ★★ISS-241 缺口登记 G-1~G-10 的**自查补全** (★老板 2026-11-12 02:02 政策: 不再发信 · 全靠自己查资料★ ⇒ 每条要么补上证据, 要么写清降级方案, 不许挂「等回复」★) + ★**21 件 OPN 回填清单** (每件: 落表时要改哪几行 · 需不需要改 footprint · 谁拍) ⇒ ★**G-5 LED 1mA 工作点亮度 / G-3·G-4 差分单边 ESD / G-10 分压阻值 / G-1 Q_PG 源漏拓扑 四条最需要自查★** |
| ISS-245 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·跨域重锚·内部活] ★★ISS-243 落表把网表/脚表 md5 换掉 ⇒ **SW 侧 §1 锚点当场过期** ⇒ `SW/tools/check_demo_panel_spec.py` rc=1 (R6 两条红) + `SW/tools/timing_check.py` rc=1 (69/71) ⇒ **按 H-1 流程重锚** |
| ISS-246 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·跨域重锚·内部活] ★★ISS-243 落表把网表/脚表 md5 换掉 ⇒ **MECH 侧 §3.1 锚点当场过期** ⇒ `MECH/check_demo_struct_truth.py` rc=1 (21/23, G5b/C21 两组红) ⇒ **按 H-1 流程重锚** |
| ISS-247 | hw-lead | 2026-11-20 | ★★[主线内·原理图/网表侧·内部活] ★★ISS-242 F1 落表作业包 v1 (★**只出作业包 + 沙盒实跑, 真盘零写入**★) —— `C_VBUS_OUT`/`C_VBUS_GND` 两颗 2 脚电容的 node2 写错 ⇒ 导出后一脚悬空 / 串联对地混在一颗上 ⇒ ★**改法落在 `state/gen_netlist.py` L369/L381 两行** (★真源改法, 不许手改 CSV★) |
| ISS-249 | hw-lead | 2026-11-20 | ★★[主线内·原理图/网表侧·落表执行·内部活] ★★ISS-247 的 F1 落表作业包 → 真落进真源 (★`state/gen_netlist.py` 两行 node2: L381 `C_VBUS_OUT`→`VBUS_5V_F1` · L393 `C_VBUS_OUT`→`VBUS_5V_CHG`★) ⇒ 一颗 2 脚电容只落 2 个网 (★现在一颗落 3 个网 = 导出后一脚悬空★) ⇒ 重生成 6 件生成物 ⇒ `HW/check_iss247_f1_landed.py` 从 rc=1 转 rc=0 + 落表台账新段 (单号 ISS-249) + 反向自证 (★板零改动·不碰 V-2/V-3/V-4★) |
| ISS-250 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·demo 头号卡点·内部活] ★★ISS-155: 「rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 target 转的 .rknn 能否在 RK3572 上跑通 (板端验证) —— 且板子当前不可达」⇒ ★**不许挂「等板子 / 等回复」** ⇒ 自己查 (rknn-toolkit2 各版本 target 列表 / 官方 model zoo / Rockchip 文档) + 标证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据]) + ≥2 条降级方案 (各带量化代价) + 板可达时的【一条命令 + 执行清单】+ 交接单 + 分片 |
| ISS-262 | hw-lead | 2026-11-20 | ★★[主线内·原理图/网表侧·落表防假绿·内部活] ★★★**落表链没有「行号漂移」判据 ⇒ V-3 落表 (删 3 行 DNP) 会让所有行号锚点 -3 而门禁照样绿** ★★(★依据: hw-lead 自己的 need `iss230_row_shift_false_green`「V-2 落表后有 4 条锚点换了行照样绿, 门禁不会提醒」★ + ISS-249 交卷单 §B4「行号漂移撞车 1 处」★) ⇒ ★**给落表器/门禁加行号锚点断言 (漂移必报 + 内容变必红) + 出 V-3/V-4 同批落表次序与重基线清单** ★ |
| ISS-266 | hw-lead | 2026-11-20 | ★★★[★新主线·PCB 侧·作业包·内部活] ★★★**出「板只改一次」作业包 v3 (★位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出, 每步带闸 + 卡点表★)** ★ |
| ISS-268 | hw-lead | 2026-11-20 | ★★[主线内·PCB 侧·口径订正·内部活] ★★「板只改一次」作业包 v3 (`HW/PCB/BOARD_ONEPASS_WORKPACKET.md`) §0 那张「一句话结论」表有 ★**两行口径漂移**★: ① ★**「卡在老板的」那一行的 A1/A2/A3 三个拍板码与全项目权威映射【写反了】**(★权威 = A1=V-3 BAT_DET · A2=V-4 R_ILIM · A3=V-2 USB ESD★) ★ ② ★**「不用任何人就能走的」那一行把 S4 (★卡 W-1/W-2 的步★) 算成自由步, 且漏了 S6/S7/S13**★ ⇒ ★**而老板此刻正站在「回一句 A1/A2/A3 就能解锁落表」的门口** ★★ |
| ISS-269 | hw-lead | 2026-11-20 | ★★★[★新主线·PCB 侧·生成器侧·内部活] ★★★**「板只改一次」那三个会让那一趟白做的生成器坑** (★X-3: `gen_pcb_netlist_board.py:591` 层数默认 **6** 而盘上板是 **8 铜层** ⇒ 重出板会掉层★ · ★X-4: 生成器里 DNP 零命中 ⇒ **43 个 DNP 位号零标记**★ · ★B-2: `value_of` 取 CSV 第一行 ⇒ 板上 `U_EN_SW` 的 Value 陈旧★) ⇒ 生成器侧先修掉 + 独立机器闸 (★零写板·零落表·零改网表真源★) |
| ISS-271 | mech-lead | 2026-11-20 | ★★[★主线内·MECH 侧·板侧认领·内部活] ★★**板那一趟 (S1~S13) 的 MECH 侧两个「无人认领」** ★ ① ★**检修口/调试口开口没挂进作业包 S6** (★ISS-267 交卷单 B5 第 3 条点名的★) ② ★**`D_LED_G` 物理位置** (★S8 布线归零卡点 · `LED_G_D` 走线 93.49mm ⇒ 要么挪 LED 要么改网表 · 归谁 = mech + 老板★) ⇒ ① 出板侧开口 S6 规格页 (机算 · 板框三套 × 开口可行性) ② 出 LED 位置的机械约束条件 (★只给条件, 不定坐标★) |
| ISS-274 | hw-lead | 2026-11-20 | ★★[主线内·PCB 线·纯分析+作业包订正类] ★★**「板只改一次」那一趟的【板框/坐标系口径】收口** ★★ ⇒ 现役板实测 160.10×100.10mm/8层/186封装, 而 MECH 侧两套窗口是 60×30 套A 坐标 ⇒ ★**搬���现役板会压住 `J_SOM_P3` 的 10 个 DSI 焊盘 / `J_SOM_P1` 的 56 个焊盘** ★ ⇒ ★**S6 的 20 个 ref 里 19 个已在目标位 (真实位移只有 `R_SEL_D3_P` 一处), 作业包「21 个」是重复计数** ★ ⇒ ★**照错坐标系开工 = 板 md5 变第二次 = 留证链/Gerber/投产包全白跑** ★ |
| ISS-275 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·门禁机制类] ★★**SW 侧 R6 判决源同构收口 (镜像 MECH 侧 ISS-273 已证机制)** ★★ ⇒ ★**R6 现在仍判「盘上 md5 == 域侧锚点副本」⇒ 上游每合法落一次表 = 域侧副本当场过期 = 门禁红 = 再开一条人工重锚单** ★ ⇒ ★**锚点已跳 6 跳 (ISS-220→223→233→243→249→257) ⇒ 11-17 05:0x 那一轮白跑了一整轮** ★ ⇒ ★**合法落表不再红, 而「悄悄换真源」仍然红** ★ |
| ISS-276 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·纯分析+规格页订正类] ★★**「板只改一次」那一趟的 MECH 侧【坐标系归一 + 收掉 ISS-273 留下的三条】** ★★ ⇒ ★**ISS-271/267 的两个窗口是 60×30 套A 坐标 ⇒ 搬到现役 160×100 台架板会压住 SoM 座 (`J_SOM_P3` 10 焊盘 / `J_SOM_P1` 56 焊盘)** ★ ⇒ ★**另: main 开的 need `iss273_h1_anchor_single_source` 实测仍 pending (答案 key 不配对 ⇒ 永不闭合)** ★ |
| ISS-277 | hw-lead | 2026-11-20 | ★★[主线内·PCB 线·纯分析+作业包订正+机器闸类] ★★「板只改一次」那一趟的【板侧漏项覆盖度收口】★★ ⇒ ★**作业包 v3 是 11-17 01:2x 的, 那之后 ISS-239/241/244/247/276 又各自发现了板侧项, 作业包一条没跟 ⇒ 且没有任何一道闸能发现「某项只在交卷单里、没进作业包」** ★ ⇒ ★**⇒ 那一趟漏做一项 = 板 md5 变第二次 = 留证链/Gerber/投产包/盖章全白跑** ★ |
| ISS-278 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·纯分析+规格页订正+机器闸类] ★★「板只改一次」那一趟的【MECH 侧板侧输入收口】★★ ⇒ ★**ISS-276 已把坐标归一到 B160x100 帧, 但 4 条板侧输入还悬着: 检修口/调试口必须拆两条 (盘上相距 123.6mm, 合并差 116.017mm) / 座体真实高度 [0数据] ⇒ 开口 Y 一切数建在 2.54 假设上 / LED 光孔 [0数据] / 连接器参数与落表板对不上** ★ ⇒ ★**⇒ 照现状开那一趟 = 开口位置按合并的错值写 = 板改第二次** ★ |
| ISS-279 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·纯分析+作业包订正+机器闸类] ★★「板只改一次」那一趟的【SW 侧板侧输入收口】★★ ⇒ ★**ISS-277 = HW 侧 · ISS-278 = MECH 侧 · 这一条 = SW 侧 (第三条腿), 目前没人认领** ★ ⇒ ★**★板那一趟一旦改板, SW 侧门禁【当场必红】且【无路可走】★★ ⇒ ★**SW 台账 `hard_protected` 钉的板/.kicad_pro 走【纯 md5 比对】, 不在落表台账链头机制内 ⇒ 板一改就红; 而手改 md5 正是 ISS-273/ISS-275 花大力气堵掉的「悄悄换真源」漏洞 ⇒ ★**⇒ 不先做这一单, 那一趟落地当天 SW 侧必然二选一: 假红 或 挖坑** ★ |
| ISS-280 | hw-lead | 2026-11-20 | ★★[★新主线·PCB 线·纯分析+作业包订正+机器闸类] ★★「板只改一次」的【提交时序守卫】★★ ⇒ ★**作业包 v3 §0/§6.1 把【会产出留证产物的步 S9/S10/S12/S13】和【只改板的步 S1/S2/S3/S6/S7】混进了同一个「不投板也能做完」的集合, 且 §6.1 断言「拍完只重跑 S8 之后的链, 板本体不用再改」★★ ⇒ ★**但 §6.2 自己写着 S4 (ESD 封装/位置/网表) 也要改板 ⇒ 照字面执行 = 板 md5 变两次 + Gerber/留证链/盖章/发布全白跑 ⇒ 破「板只改一次」铁律** ★ ⇒ ★**⇒ 本单 = 把它一般化 + 给它一道机器闸 (板 md5 变更次数 ≤ 1)** ★ |
| ISS-281 | hw-lead | 2026-11-20 | ★★[★主线·PCB 线·纯规格+作业包追加式订正+机器闸类] ★★「板只改一次」的【S10 投产包 md5 清单落地】★★ ⇒ ★**作业包 §3-S10 的量化判据写着「板统计里的 md5 == S6 重出后的板 md5」, 但盘上 `HW/PCB/production/doc/board-stats.txt` 是 KiCad 统计报告导出 (1435 B), `grep -ci md5` = 0 ⇒ 那个字段【根本不存在】⇒ S10 无判可依** ★ ⇒ ★**⇒ S10 是「板改完最后一次」的留证/投产步, 而投产包(73 文件) 与板之间目前【没有任何内容级绑定】** ★ ⇒ ★**chain_gate 只判 mtime(产物不比板旧) ⇒ 板改一次, 旧 Gerber 只要 mtime 刷新就能冒充新货** ★ ⇒ ★**⇒ ISS-280 的 D6「留证绑定」需要「产物绑定到哪一版板」, 而盘上没有任何文件能声明这件事** ★ ⇒ ★**⇒ 本单 = 造一份【投产包清单文件】的格式契约 + 一道内容级机器闸 (零写板 · 零跑 gen_production_pack.sh)** ★ |
| ISS-282 | hw-lead | 2026-11-20 | ★★[★主线·PCB 线·纯规格+作业包追加式订正+机器闸类] ★★「板只改一次」的【`FSIN_OUT` 根因订正 + 布线前置闸】★★ ⇒ ★**决策页 §A-补13 把「`FSIN_OUT` 逃逸方向」派给 main 自查, main 本轮自查完 = 盘上写着的根因【是错的】** ★ ⇒ ★**盘上写的是「疑似逃逸方向 bug (两者竖直对齐, 逃逸口互挡)」(作业包 §6.2 S8 行 + ISS-265 §6 桶B-26)★** ⇒ ★**main 本机实跑三条独立实测全部指向【布线排队顺序】: ① 两个焊盘到最近异网焊盘边缘 1.1500/1.3528mm ≫ 0.45 ⇒ 根本不走 `escape_stub()` ⇒ 「逃逸方向」不成立 ② 逐网忽略法: 只忽略 `VDD_3V3_IO` ⇒ A→B 直线净距 0.439 ≥ 0.395 ⇒ PASS ⇒ 唯一挡路者是 `VDD_3V3_IO` (它在 `POWER_NETS` 里 = 第 2 步布, 而 `FSIN_OUT` 第 4 步才布 ⇒ 后挑走廊只剩窄缝) ③ 沙盒 DRC: pristine 0违规/45未连 ⇒ 手工布线后连上 (45→44) 但 18 违规 ⇒ 手工补线不是出路** ★ ⇒ ★**且该根因【早就被实测解过】: `LANE_CONFLICT_WORKLIST.md` L260 实测 `PCB_PRIORITY_NETS` 让 `FSIN_OUT` 一次就通 ★★L=3.0mm = 那条直线★★ (路由器源码 L4790 的用法示例里就写着 `FSIN_OUT`)★** ⇒ ★**⇒ 直接后果: `FSIN_OUT` 从【会改板/要老板拍】那一类里划掉 ⇒ 不进「A 类步」⇒ 老板那一趟要拍的东西【少一条】(好消息) ⇒ 但它没消失, 挪到【布线臂 env 配置】⇒ 「布线 45→0」那一趟仍必须把它布通** ★ ⇒ ★**⇒ 本单 = 订正根因 + 追加式订正作业包 + 一道可复现的机器闸 (零写板 · 零跑布线臂)★** ★ |
| ISS-287 | hw-lead | 2026-11-20 | ★★[主线内·PCB 线·板那一趟·前置准备·内部活] ★★【「板只改一次」那一趟的 A 类步【沙盒干跑可行性探针】】★★ ⇒ ★**零写板 · 零落表 · 零改生成器代码**★ ⇒ ★**用实跑回答「那一趟能不能在真盘外先跑一遍」= 能/不能 + 缺哪几个开关**★ ⇒ ★**答案 = 「板那一趟」任务书的写法依据**★ (★那一趟现在卡在老板 2 条拍板: W-2 · `D_LED_G` 外露★) |
| ISS-289 | hw-lead | 2026-11-20 | ★★[主线内·PCB 线·纯规格订正+机器闸类·内部活] ★★【动板前: 把作业包 §3 里【全部现状值型判据】对回盘面实测】★★ ⇒ ★**S7 的「DNP 43 全标」已过期 ⇒ 真值 40** ★ (★因 2026-11-17 09:58 + 12:16 + 12:30 三次合法落表把 BAT_DET 三颗 DNP→必装★) ⇒ ★**★S7 的验收目标是「零标记数 = 0」⇒ 照 43 走 = 要么验收假红, 要么为了凑 43 把刚落表的三颗必装改回 DNP ⇒ ★★等于把老板拍板 undo★★** ★ ⇒ ★**作业包共 6 处 43 过期 (§3-S7 标题/量化判据×2/§3 表 S7 行/§4 验收表 S1~S7 行/§2 X-2 坑行) + ISS-287 另两条差异 (封装 185 vs 186 / 官方板 `_1` 后缀位号 1 个)** ⇒ ⇒ ★**必加一道闸: 作业包 + 清单页的现状值 == 盘面实测 (★不许只加 DNP 一条★)** ★ |
| ISS-290 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·板那一趟·结构侧交叉核对·内部活] ★★【「板只改一次」那一趟: ① S6 的 20 个目标落位 × MECH 保留区 逐个交叉核对 + ② 座体类器件 (J_DEBUG/J_UART/J_USB_C/J_CHG/J_SOM_P1..P4) 的【选型 ↔ land pattern ↔ 结构占位】三方对照 (★重点: 排针 pitch 1.27 mm vs 板读 0.50 mm ⇒ 实物排针落不进★) + ③ `corner_radius` 3.0 vs 0.0 的贴角 keep-out 口径】★★ ⇒ ★**零写板 · 零落表 · 零改 `HW/` · 零改既有 MECH 判据脚本**★ ⇒ ★**产出 = 一份交叉核对表 + 一道机器闸 + 一份「必须在那一趟一起改」的清单 (★可直接进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`★)**★ |
| ISS-291 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·ADC 判据口径收口+机器闸类·内部活] ★★【SW 侧 ADC 判据的【判决对象 + 满量程口径】双错】★★ ⇒ ★**满量程**: 脚本写死 `DEVICE["V_DET_FS"] = 3.3` (3.3V 域) vs 官方 `SARADC_VIN5` = **1.8V 域** (`FET3572C_PIN_TABLE.csv:39` 实测 + `rk3572_datasheet_V1.1.txt:2454/2863/2864` 官网) ⇒ ★**漏电偏移 %FS: 网表 note 写 2.1% vs SW 闸算 15.2% (差 7 倍, 同一分压链两个数)★** ⇒ ★**判决对象**: F4 取链规则 = 「元组顺序第一条 populated」⇒ 判的是 `VBUS_DET_D` (→ `J_SOM_P1 pin100` = `USB_DRD1_VBUSDET` **数字脚**) ⇒ ★**真 ADC 链 `BAT_DET` (→ `J_SOM_P1 pin38` = `SARADC_VIN5`) 一条判据都没有**★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM 真源**★ ⇒ ★**产出 = 口径改对 (FS 1.8V + 取链按「落点是不是 ADC 脚」) + 反向用例 + 与网表 note 逐字对齐 (2.1% FS) + 硬件后果只登记 need 不自己改**★ |
| ISS-292 | hw-lead | 2026-11-20 | ★★[主线内·PCB 线·纯生成器对齐+作业包指针订正类·内部活] ★★【清单页生成器 `state/_iss277_build_preflight.py` 与盘面页脱钩 ⇒ 跑一次 = 把 ISS-283/ISS-289 的订正全冲掉】★★ ⇒ ★**生成器仍写 R3-A4「54/43/43」+ 脚表「15 条缺陷」+ 缺 `B32_V2_NET_RENAME`, 而盘面页已是 51/40/40 + 18 条**★** ⇒ ★**本单 = 生成器改成从真源读 (★不许再写死★) + 重跑幂等 硬判据 (★重跑后盘面页要么零变化, 要么只多 B32 一条且九处订正 anchor 一处不少★) + 作业包 §3-S1 位号真源指针改对 (`SCHEMATIC_V1_SPEC.json` 无 devices 段 ⇒ 真源 = `HW/netlist_v1_pins.csv`) + 「收工后重锚」写成收工清单强制项**★ ⇒ ★**零写板 · 零落表**★ |
| ISS-293 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·复评文档口径收口 + 机器闸类·内部活] ★★【`SW/SW_TIMING_REVIEW.md` 停在 ISS-291 之前的旧口径 ⇒ 判决对象仍写 `VBUS_DET_D` (实为 USB 数字检测脚) + 满量程隐含 3.3V (官方 1.8V 域) + 「BAT_DET 三颗全 DNP」(09:58 落表后已必装) + §7-4 那条 P0 整条不成立】★★ ⇒ ★**照它判「ADC 链不合格 ⇒ 改板」⇒ 板白改第二遍** ★ ⇒ ★**本单 = 按真值订正 6 处 + 新建一道「文档不许再漂」的机器闸 (★纯文档 + 闸·零写板·零落表·零改网表真源★)** ★ |
| ISS-294 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·规格补缺 + 机器闸类·内部活] ★★【`J_USB_C` 缺一条结构边开口规格 (★座体 `F.Fab` Y 下沿 = 0.000 = 板边 ⇒ 插头从板边进出, 但 MECH 规格页 + 两道 MECH 闸里【只有】检修口/调试口两条开口·第三边完全不存在★)】★★ ⇒ ★**结构件没有这条开口 ⇒ USB-C 插头根本插不进去 ⇒ 板装上了也用不了** ★ ⇒ ★**本单 = 补第三条开口规格 (含固定孔清空区) + 把两道闸从「条数断言」改成【集合 + 两两不相同】(★合并禁令不许松★) + ≥4 条反向用例 (★纯 MECH 侧·零写板·零落表·零改网表★)** ★ |
| ISS-295 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·结构输入一次性收口 + 过期结论防漂闸·内部活] ★★【① MECH 两页对同一件事【两种说法】: `BOARD_ONEPASS_STRUCT_CROSSCHECK.md` L68/L175/L188/L1816 仍写「结构侧缺一条边开口规格 (缺口)」, 而 `BOARD_ONEPASS_MECH_SYNC.md` L550 已改成「边开口规格已补」⇒ 机器闸 N3b 只比两页机器块的 openings 矩形 ⇒ 叙事文字漂移 = 绿灯 (SW 侧 ISS-293 刚栽过同一种坑) ② 结构侧输入散成 4 条 need ⇒ 「板只改一次」那一趟开工时结构件必然缺料】★★ ⇒ ★**本单 = 一份「可直接抄进作业包 §3-S6 的结构侧输入认领句全表」 + 一道「过期结论不许再漂」的机器闸 (★纯 MECH 侧文档 + 闸·零写板·零落表·不替老板拍板★)** ★ |
| ISS-296 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·闸机制类·内部活] ★★【MECH 两道闸把【板 md5】写死成「硬保护基线」⇒ 板那一趟合法改板一次后 ⇒ 这两道闸必假红 ⇒ 而收工验收时的假红会被误读成「板改坏了」⇒ 板白改第二遍】★★ ⇒ ★**本单 = 把 SW 侧 ISS-284 已验证的「合法改板」机制 (reboard 四项原子记录 + 落表台账链头 + fail-closed 四条) 接到 MECH 侧两道闸 + 把 MECH 侧「收工后同一次重锚」写成收工清单强制项 + ≥4 条反向用例 (★纯 MECH 侧·零写板·零落表·零改网表★)** ★ |
| ISS-297 | hw-lead | 2026-11-20 | ★★[主线内·HW 侧·门禁机制收口·内部活] ★★【HW 侧 6 道闸: 建「合法改板」通道】★★ ⇒ ★**全仓 9 道闸硬钉板 md5 `611b869e…`; 板那一趟合法改板当天它们会一起红** ★ ⇒ ★**而那些红的真实含义是「板被换了」, 不是「板改坏了」⇒ 现场极可能误读 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ ⇒ ★**口径已被 ISS-284 证明可行** (★SW 侧那道转成台账口径后就不再硬钉, 全仓清单里根本找不到它★) ⇒ ★**照 reboard 原子映射 {by,file,prev_md5,md5} + 四项缺一⇒红 + 与台账链头一致** ★ ⇒ ★**判据不许松: 盘上 ≠ 链头且无合法记录 ⇒ 仍红; fail-closed 三条一条不许动** ★ |
| ISS-298 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·门禁机制收口·内部活] ★★【SW 侧 1 道闸: 建「合法改板」通道】★★ ⇒ ★**全仓 9 道闸硬钉板 md5 `611b869e…`; 板那一趟合法改板当天它们会一起红** ★ ⇒ ★**而那些红的真实含义是「板被换了」, 不是「板改坏了」⇒ 现场极可能误读 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ ⇒ ★**口径已被 ISS-284 证明可行** (★SW 侧那道转成台账口径后就不再硬钉, 全仓清单里根本找不到它★) ⇒ ★**照 reboard 原子映射 {by,file,prev_md5,md5} + 四项缺一⇒红 + 与台账链头一致** ★ ⇒ ★**判据不许松: 盘上 ≠ 链头且无合法记录 ⇒ 仍红; fail-closed 三条一条不许动** ★ |
| ISS-299 | hw-lead | 2026-11-20 | ★★[主线内·HW 侧·重锚类·零写板] ★★【H-1 重锚第 2 跳: 让 9 道「钉板 md5 闸」里唯一红的那一道能挂进门禁链】★★ ⇒ ★**第 5 道 `HW/check_pin_function_labels.py` 现在 rc=1 (18 条既有缺陷 = 15 条脚表功能缺陷 + 3 条 `MD5_CHANGED`·基线常量还停在 ISS-257 旧值·真盘自 ISS-283 落表起已变) ⇒ 且它的 `--selftest` 也是 rc=1 (T5/T11「前提不成立: 正常基线本应干净」)⇒ 它是 9 道里唯一「自检也不绿」的一道** ⇒ ⇒ ★**main 因此不能把它挂进 `state/gate_check.py` 的 `EXTRA_GATES` (挂上去链当场红) ⇒ 「9 道闸通道齐 = 板那一趟开工前最后一道硬前置」现在卡在它身上** ★ ⇒ ★**本单 = 把 `PROTECTED_MD5` 里网表/脚表/BOM 三个基线重锚到 ISS-283 落表后的真盘实测值 + `MD5_ANCHOR_CHAIN` 追加第 2 跳 (★重锚的是【脚本里的基线常量】·不是那三个文件本身★) + 目标读数 「缺陷 18→15 · `--expect-known` rc=0 · `--selftest` rc=0」** ★ ⇒ ★**附带一条小修: ISS-297 交卷单标题不含 `gate_check.py` 标准 B2/B3/B4 关键词 ⇒ 最新一份自己评不满 6/6 (现在靠回退到 ISS-283 计分) ⇒ 末尾追加 3 行标准标题行 (只追加·不许改老字)** ★ ⇒ ★**纯重锚类·零写板·零落表·不碰 `state/gate_check.py`** ★ |
| ISS-300 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·准出闸类·零写板] ★★【「板只改一次」那一趟的 MECH 侧【准出汇总闸】: 一条命令出「S6 重出板后能不能出 Gerber」的结构侧结论】★★ ⇒ ★**那一趟当天 MECH 侧必跑 6 道闸 (main 21:3x 实跑今天全 rc=0): `MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `MECH/check_onepass_mech_sync.py` · `MECH/check_onepass_struct_crosscheck.py` · `MECH/board_port_opening_s6_check.py` · `MECH/check_mech_verdict_freshness.py`** ⇒ ★**现在这 6 道是人工一条条跑 ⇒ 漏一条就没人知道 ⇒ 而这 6 道里有 2 道是【钉板 md5 闸】(板那一趟当天必然从绿转红·只有合法改板通道能走绿·ISS-296 已把通道建好) ⇒ 当天最容易误读成「板改坏了」⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ ⇒ ★**本单 = 新建一道 fail-closed 汇总闸 `MECH/check_onepass_mech_release.py` (逐条打印每道 rc + 汇总 rc + 脚本不存在/跑不起来/超时一律算红 + 必须点名是哪一道红了) + ≥3 条反向用例 (沙盒里把任一道弄红 ⇒ 汇总必红且点名) + `--selftest` 模式** ★ ⇒ ★**纯门禁类·零写板·零落表·不许改那 6 道闸本体·不许改 `state/gate_check.py` (挂闸是 main 的活)** ★ |
| ISS-302 | hw-lead | 2026-11-20 | ★★[主线内·落表链侧·内部活] ★★【落表: `C_SYS` / `SYS_CHG` 必装 + note 追加式订正 + BOM 加 20 µF (ISS-095 的同批动作)】★★ ⇒ ★**TI 官网逐字 (bq25896 SLUSC76C §7): "Connect a 20uF closely to the SYS pin."** ⇒ ★**现状: 网表 L498/L499 仍 DNP + note 里留着已过期的「VSYS 不接 (NC)」裁决 + BOM 无那颗 20µF** ★ ⇒ ★**★CHG_BOARD 没有 PCB 文件 ⇒ 装不装都在同一次布局里落 ⇒ 不构成「板改第二次」** ★ |
| ISS-303 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·闸机制类·内部活] ★★【MECH 侧 N6 只认【硬基线】不认【合法落表跳】⇒ 00:21 ISS-302 合法落表一次 ⇒ MECH 侧准出汇总闸当场转红 ⇒ 「板只改一次」那一趟的结构侧准出被一个假红挡住 ⇒ 现场极可能误读成「板改坏了」】★★ ⇒ ★**本单 = 把 N6 的判决源从【硬基线常量】换成【硬基线 ∪ 落表台账登记值】(★只读台账, 不许把新 md5 写死★) + fail-closed 三条不许动 + 反向用例 ≥ 5 条 (★纯 MECH 侧·零写板·零落表·零改网表★)** ★ |
| ISS-304 | hw-lead | 2026-11-20 | ★★[主线内·HW 侧·现状值重锚类·内部活] ★★【钉板闸⑥ 作业包现状值闸: 00:21 ISS-302 合法落表一次 ⇒ 页面里那 4 条 md5 现值没跟上 ⇒ Q7 钉板 md5 闸链 8/9 ⇒ 「板只改一次」那一趟不许开工】★★ ⇒ ★**本单 = 让那 4 条 `fresh` 原句跟上盘面 + 幂等不许破 (★重跑生成器 ⇒ 页 md5 相同★) + 口径「走落表台账为准, 不写死」(★ISS-283 ⑩-b 早就定过★) · 纯文档/闸侧 · 零写板 · 零落表** ★ |
| ISS-306 | sw-lead | 2026-11-20 | ★★[主线内·开工前置·溯源类·内部活] ★★【板那一趟开工前置: G1a 剩下两条红 (G1a-4 落表未清零 + G1a-8 关机语义已决) 到底卡在老板身上 还是 卡在过期判据身上?】★★ ⇒ ★**本单 = 把这 2 条红逐条归类 (R3/R4×2/R9 + ISS-097 代理判据) + 交一份「板那一趟开工前老板还差 N 个字母 (N 必须是具体数字) + 每条卡在哪一步 + 不拍的后果」的清单★★ ⇒ 纯分析/溯源 · 零写板 · 零落表 · 零改闸 · 零外发 · 不替老板拍板** ★ |
| ISS-328 | hw-lead | 2026-11-20 | ★补一条【真能构成对照】的右上臂 (R_SEL_* 挪右上) + 在官方链同配方下复测 TP no-op (⇒ 给 ISS-325 的 P-1「20→10 删不删」补读数) |
| ISS-332 | sw-lead | 2026-11-20 | ★★[主线内·SW 侧·判据收紧类·内部活] 第 8 道闸 (SW 位号引用可达性) 的 C1/C7/C8/C13 四条【洗白面】· 复现 + 收紧方案 (★零改真件闸★) |
| ISS-333 | mech-lead | 2026-11-20 | ★★[主线内·MECH 侧·闸实现类·内部活] MECH 侧位号可达性闸 · 从【设计稿】到【可直接挂的闸】的实现单 (★零改 state/gate_check.py·★挂闸由 main 执行★) |
| ISS-334 | hw-lead | 2026-11-20 | ★★[★新主线·PCB 线·机制级·纯分析+作业包类·内部活] ★★**零铜网「换机制」路线: 成对走廊 / 换层绕开 / 路由器本体 (★ISS-325 左上臂 + ISS-328 右上臂 双双 REJECT ⇒ 「挪器件位置」这条路已死 ⇒ 归零只剩机制级 / 老板口径 / 路由器本体三条)★★ ⇒ ★**本单 = 机制级那条: ① 零铜网 0 号清单 (fresh 机器读数) ② 逐网死因归类 (三桶 + 反向用例) ③ 候选臂设计 (含【对照有效性自检】+【可比性自检】) ④ 逐字作业包 (板那一趟照着跑·板 md5 只变一次) ★★★** (★零写板·零落表·零改闸·零改生成器·零外发·不代拍★) |
| ISS-335 | sw-lead | 2026-11-20 | ★★[★新主线·PCB 线·纯新建闸类·内部活] ★★**「板只改一次」那一趟的【SW 侧准出汇总闸】** (★对标 MECH 侧 ISS-300 的 `MECH/check_onepass_mech_release.py` · ★SW 侧【零个】对标物 ⇒ 「SW 侧能不能出 Gerber」今天在 SW 域【没有任何机器答案】★) ★★ ⇒ ★**本单 = ① SW 侧 10 道必跑闸的清单页 (★ISS-321 实测表 + 链外 4 道★) ② fail-closed 汇总闸本体 (★脚本不存在/跑不起来/超时/rc≠0 ⇒ 一律汇总红 + 清单完备性★) ③ 反向用例 (★沙盒副本·真件零碰★) ④ 板那一趟当天 SW 侧的逐字 SOP ⑤ 给 main 的一行挂链写法 (★本单自己不改 `state/gate_check.py`★) ★【纯新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改 gate_check.py】★★ |
| ISS-336 | mech-lead | 2026-11-20 | ★★[★新主线·PCB 线·纯新建闸类·内部活] ★★**「板只改一次」那一趟的【板框冻结闸 U-1 机器闸实现】** (★ISS-316 §2 已把 C1~C7 七条判据 + RC-1~RC-6 六条反向用例的设计稿全部出好 · ★main 已于 2026-11-18 09:4x 把决策码 M-B18 的 (a) 项裁成【路 B = 做成机器闸】 · ★但 `MECH/check_board_frame_freeze_gate.py` 至今【不存在】⇒ 裁了不做 = 裁了跟没裁一样★) ★★ ⇒ ★**本单 = ① 冻结闸本体 (★C1~C7 逐条照设计稿实现 · 阈值一律只读 `MECH/service_port_check.py` + `MECH/board_frame_feasibility.py` + `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:FRAMES`★) ② 六条反向用例 + 一条正向对照 (★沙盒副本·真件零碰★) ③ ★★C7 真源的实测纠正 (★ISS-316 §2 写「读 issue_log」⇒ ★★本机实读 issue_log 顶层零条 need 闭合记录 ⇒ ★真源是【分片侧】`needs_closed` (64 条) + `answers` (79 条)·★这正是 ISS-281 §3-S10 那一类「判据引用了盘上不存在的字段」的病★) ④ 一页说明 + 交卷页 + 「U-1 拍完之后这闸怎么变绿」的落表格式说明 ★【纯新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改 gate_check.py · 不代老板拍 U-1】★★ |
| ISS-337 | hw-lead | 2026-11-20 | ★★[★新主线·PCB 线·纯分析+沙盒类·内部活] ★★**段数追平根因定位: 现生成器 stage-1 只出 ~2.5K 段 vs 官方链 stage-1 ~17K 段 (差 ~7 倍) ⇒ 「同工艺才可比」这条前置至今没解★** ⇒ ★**本单 = ① 六层逐层拆解 (输入/配方env/生成器版本/网格/规则/后处理链) ② 官方链可复现性自检 ③ 判定「可恢复 or 不可恢复」 ④ 可恢复 ⇒ 沙盒恢复方案+读数 / 不可恢复 ⇒ 同工艺新基线的完整口径 (含段数区间自检脚本+反向用例) ⑤ 臂设计 (唯一变量 + 同工艺起跑线 + 不可比自检退出) ★★★** (★零写板·零落表·零改闸·零改真生成器·零外发·不代拍★) |
| ISS-338 | sw-lead | 2026-11-20 | ★★[★新主线·PCB 线·纯分析类·内部活] ★★**ISS-334 need-4a: 官方板 24 个零铜网里的 9 条单端低速脚, 固件到底用不用? (★`CAM_RESET_N`/`FSIN_OUT`/`JTAG_TDI`/`LED_G_D`/`SPI_*_BOOT`/`UART_RX`/`USB_CC2`★) ⇒ ★**这 9 条是 24 条零铜网里唯一有「悬空余地」的 (另 15 条是差分腿, 必须救回) ⇒ SW 侧至今零回答 ⇒ 本单 = 逐条引用表 (9 行·四档引用形态) + 可悬空候选清单 + 三问结论★** (★零写板·零落表·零改固件·零改闸·不代拍★) |
| ISS-339 | hw-lead | 2026-11-23 | ★★[★新主线·PCB 线·纯分析+新建闸类·零写板] ★★【板那一趟 S8 布线归零的两把尺子: ① 【可比性前置闸】(main 21:2x 已裁 need `iss337_band_truth_overrides_doc`: `compare_arm_official.py` 不用改代码 ⇒ 只需在它前面加一道可比性前置闸, 判据 = 归一化段数 [2300,3200] · 铜长 [4600,5900]mm · 过孔 [380,520] ⇒ 越界即拦) + ② 【S8 目标名单重读器】(main 21:2x 已裁 need `iss337_rereread_zerocopper_denominator`: 在那一趟的真实基线板上跑 unconnected 清单 ⇒ 得分母 N' ⇒ 逐条标 [必需/可悬空/待定] + 该网有没有铜)】★★ ★**板只改一次 ⇒ 这一趟没开工 ⇒ 本单只出【两把尺子】, 一个字节都不许碰板**★ ★**纯分析 / 新建闸类 · 零写板 · 零落表 · 零改闸 · 零重生成 · 零外发 · 不替老板拍板** ★ |
| ISS-340 | hw-lead | 2026-11-23 | ★★[★新主线·PCB 线·纯分析+新建判别闸·零写板] ★★【板↔网表 C1 红根因归属判定: chain_gate ③ PCB 准入 ❌ = C1 焊盘级等价 网表 480 / 板上(带网) 482 ⇒ 多余 2 (`C_VBUS_GND` pad1=GND · pad2=VBUS_5V_CHG) + 同号异网 3 (`Q_PG` pad1 应 PWR_GOOD 实际 PWR_ON · `Q_PG` pad3 应 PWR_ON 实际 PWR_GOOD · `D_ESD_USB_D` pad1 应 NET_USB_D_P_TYPEC 实际 USB_D_P_SRC) ⇒ ★逐条判 [A 网表侧错→改网表就够·板 md5 不用动] / [B 板侧错→必须动板·进板那一趟 B-清单] / [C 等老板拍板→进待拍板页] ★★】★★ ★**板只改一次 ⇒ 这一趟没开工 ⇒ 本单只出【归属判定 + 判别闸】, 一个字节都不许碰板**★ ★**纯分析 / 新建闸类 · 零写板 · 零改网表 · 零落表 · 零改闸 · 零重生成 · 零外发 · 不替老板拍板** ★ |
| ISS-341 | mech-lead | 2026-11-23 | ★★[★新主线·PCB 线·纯分析+新建判定闸·零写板] ★★【「板那一趟」画哪块板: U-1 板框冻结三候选 (B160x100 / F30A 60×30 / P60×15) × 现役板 的相容性机器判定 ⇒ 现役板 = 160×100 / 8 铜层 / 1.60mm / 186 封装 / RK3572-SOM 承载区 (J_SOM_P1..P4 占位 53.60×46.08mm) ⇒ 承载区高 46mm ≫ F30A 板高 30 (超 +16.08) ≫ P60×15 板高 15 (超 +31.08) ⇒ ②/③ 候选装不进现役板 ⇒ 拍 ②/③ = 【重画一块新板】而不是【改现役板一次】⇒ 「板只改一次」的口径会当场失效 ⇒ 须把「这一趟画哪块物理产品」(上位) 与「那块板用哪个框」(下位, U-1) 分两层分开】★★ ★**纯分析 / 新建闸类 · 零写板 · 零改既有 MECH 文件 · 零改 HW 文件 · 零落表 · 零重生成 · 零外发 · 不替老板拍板** ★ |
| ISS-342 | mech-lead | 2026-11-23 | ★★[★新主线·PCB 线·结构侧口径漂移·纯分析+文档订正+机器闸类·零写板] ★★【C6: `MECH/BOARD_GEOM_30MM.md` 自称「结构侧对 60×30mm 现行板的唯一权威几何口径」(60×30 / 6 层 / 1.00mm / 主控 RK3576 FCCSP698L), 而现役板 = 160×100mm / 8 铜层 / 1.60mm / 186 封装 / 主控 RK3572-SOM 直插 (承载区 53.80×46.78mm ⇒ 60×30 装不下, 高差 −16.78) ⇒ 该表已被 ISS-341 机器判决判为「重画一块新板」那一档的口径 ⇒ 它继续自称「唯一权威」= 整条链的静默投毒源 (★主板线 = 绘制 PCB 图, 「板只改一次」那一趟开工前每个 agent 都可能去读它★) ⇒ 交付: ① 漂移清单页 (MECH 域 21 个 RK3576 命中文件逐行定性) ② `MECH/BOARD_GEOM_30MM.md` 表头【追加式】订正 (老字一字不删) ③ 只读漂移检测闸 (含 --selftest) ④ 交卷页 B0~B7 ★★ |
| ISS-343 | hw-lead | 2026-11-24 | ★★[★新主线·PCB 线·板侧项全集漏项·纯分析+文档订正+机器闸·零写板] ★★【E-1 排针 land 0.50→1.27mm 补进「板侧项全集」页 + 作业包两处过期待拍状态订正 + 覆盖度闸补「作业包板改清单逐项对照」判据】★★ ★**E-1 = main 2026-11-17 18:45 已拍死 (归 main 不归老板) = 按 1.27mm 排针定 + 板 land 并进那一趟重画; 但 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 32 条板侧项里【没有这一条】(main 实跑: 1.27/pitch/排针/E-1/0.50 五个 marker 全不在 items 块里) ⇒ 覆盖度闸 P4 只查「位号在不在清单里」⇒ 这类【同一 J_DEBUG/J_UART 的 land pitch 改】天生查不出 ⇒ P4 绿灯 = 假绿 ⇒ 那一趟做完实物排针照样装不进 ⇒ 补做 = 板 md5 变第二次 = 留证链/Gerber/投产包/盖章全白跑一遍**★ |
| ISS-344 | sw-lead | 2026-11-24 | ★★[★新主线·PCB 线·固件侧分级口径对账·纯分析+文档订正+机器闸·零写板] ★★【ISS-338 §3 表的 6 条「NC (不连)」与 main 2026-11-22 20:5x 终裁逐条对账 + 订正 SW 页分级陈述 + 建「SW 分级 vs 板侧真值不许分叉」机器闸】★★ ★**终裁 = 必需 23 (含 8 条单端脚) / 可悬空 1 (FSIN_OUT) / 待定 0; 而 SW 页 §3 表仍把 JTAG_TDI / SPI_MISO_BOOT / SPI_MOSI_BOOT / SPI_SCLK_BOOT / UART_RX / USB_CC2 六条判成「NC (不连)」(main 实跑判定) ⇒ 这 6 条会带着矛盾进板那一趟**★ |
| ISS-345 | mech-lead | 2026-11-24 | ★★[★新主线·PCB 线·MECH 域判据迁双口径·纯脚本改造+文档订正+机器闸·零写板] ★★【8 个 MECH 判定脚本迁【双口径】(60×30/RK3576 与 160×100/RK3572 两档都留, 默认档保持 60×30 不动) + 迁完 scope A/B 真数重读并追加式订正清单页 + 建「单口径脚本进不了板那一趟」机器闸】★★ ★**main 2026-11-23 00:1x 已裁「迁, 但迁法必须是双口径, 不许删 60×30 档, 默认档由 U-1 定, 必须赶在板那一趟开工前」; 而现在 8 个脚本里有 5 个只认 60×30 一档 (main 实读: pinset2_mech_check / skeleton_section_check / fit_check_v3_30mm / fit_check / cross_review_check 的 160×100 命中全为 0)**★ |
| ISS-354 | hw-lead | 2026-11-24 | ★★[★新主线·PCB 线·demo 主板可制造性收口·纯查证·零写板] ★★【ISS-169 (open, owner=main) 暴露三件「板子还不能下单」的事至今没收口 ⇒ 本单 = ① **SoM 座 pin1「哪一排」公开资料无定论** ⇒ 出降级方案 + 下料前一票否决项 ② **5 个 ref / 4 类封装与脚号不自洽** (Q1 / Q2 / U_BATPROT / U_LDO_S28 / U_SUPV) ⇒ 查官方 datasheet + KiCad 官方库 ⇒ 出**板那一趟的改项清单** ③ **BOM 里 OPN 仍「待选型」** ⇒ 自己网上查官网 ⇒ 给候选 + 代价 (不代拍)】★★ ★**只出方案与清单·不动板·不改网表真源·不改脚表·不改 BOM·不重出 Gerber**★ |
| ISS-348 | main | 2026-11-25 | ★★[★基础设施·跨 job·内部活·零写板] ★★【/tmp 是带 userquota 的 tmpfs (7.5G) 而用户配额已被打满 ⇒ 任何写 /tmp 的作业都在 EDQUOT 上失败 (★实测: 连 14 KB 的 cp 都失败·dd 20M 失败·本 job 把 issue_check 输出重定向到 /tmp 时拿到 rc=120 + 0 字节 = 假读数★) ⇒ 占用大头 = /tmp/od_glass_publish 4.1G (5 小时 GitHub 同步 job 的发布暂存目录·01:15 还在被写 ⇒ 此刻正在跑·不许此刻动) + /tmp/adv_sandbox 680M (子 agent 正在用) ⇒ 建议: 发布暂存改落项目盘或推完即清 + 子 agent 沙盒改落项目盘 (本 job 的单测已改) + 门禁输出不许重定向到 /tmp】★★ |
| ISS-349 | hw-lead | 2026-11-25 | ★★[★新主线·PCB 线·板侧项全集页被手改·生成器重跑会蒸发 E-1·纯脚本改造+新建机器闸·零写板] ★★【把 `B33_PIN_LAND_1P27` (E-1 排针 land 0.50→1.27) 从「手改产物页」搬回生成器 `state/_iss277_build_preflight.py` ⇒ 重跑生成器 ⇒ §2 表 33 行 + §7 JSON 33 条 + id 集合逐一相等 ⇒ 新建 `HW/check_preflight_regen_idempotent.py` (表/JSON 同源 + 重跑幂等 + source_iss 在 SOURCES 内) + ≥3 条反向用例】★★ ★**main 2026-11-23 01:4x 实读: 页 §2 表 32 行 vs §7 JSON 33 条 (多出 `B33`) ⇒ 页与 JSON 已不同源; 生成器 ITEMS_RAW 只有 B01..B32 + sidecar 0 命中 ⇒ 重跑一次生成器 B33 即蒸发; ISS-292 交卷页写死的「页回退这条路已经堵死 (页 md5=159bf20f…)」现已失效 (现页 md5=8ae70471…) ⇒ 而 `state/_iss304_sync_state_baseline_md5.py:145` 的「落表后重锚流程 ①」每次都跑生成器 ⇒ E-1 会从「板只改一次」那一趟的板侧项全集里静默消失 ⇒ 实物排针照样装不进 ⇒ 补做 = 板 md5 变第二次**★ |
| ISS-352 | mech-lead | 2026-11-25 | ★★[★新主线·PCB 线·MECH 域判定脚本迁双口径·第 2 批·零写板] ★★【ISS-345 cont1 (第 1 批 2 脚本) 已由 main 2026-11-23 04:0x 签收 ⇒ 第 2 批 = 交卷页 §B5-2 自己列的那张清单: ① `fit_check_v3_30mm.py` / `fit_check.py` 二选一 说清 ② `cross_review_check.py` 迁双口径 (默认档逐字节不变) ③ 新建闸 `MECH/check_mech_dual_caliber_gate.py` (含反向用例) ④ `BOARD_GEOM_CALIBER_STATUS.md` scope A/B 追加式订正 ⑤ 漂移闸迁后重跑回填 + 三个既有帧表脚本核对结论】★★ ★**板那一趟开工前还差「MECH 域 8 个判定脚本迁双口径」这一件 ⇒ 本单就是它的下半程**★ |
| ISS-356 | hw-lead | 2026-11-25 | ★★[★新主线·PCB 线·「板那一趟」封装真值基线 (100 件必装器件的占位封装 → 真库封装映射)·纯分析/作业包·零写板] ★★【main 2026-11-23 07:5x 本机实读: BOM 165 件真实器件里 100 件必装器件的 footprint 栏 = 待定 (94 件连 OPN 也空) · 板面 186 个封装库名 100% 为空字符串 (全是自绘通用占位) · 原理图 218 个符号里 201 个 Footprint = TBD ⇒ 封装真值在源头就不存在 ⇒ 「板只改一次」那一趟画出去的板, 型号一落就得返工 (板 md5 变第二次) ⇒ 本单 = 把这条缺失的基线补出来: 族级映射表 + 逐 ref 表 + 删件候选 + 自带机器闸 · 零写板】★★ |
| ISS-357 | sw-lead | 2026-11-25 | ★★[主线内·SW 侧·需求闭环类·内部活] ★★【SW 域 needs 144 条四分类处置 (waiting_on 空 118 / to=hw-lead 17 / to=mech-lead 2 / agent 4 / boss 12 / vendor 8) ⇒ 把机检缺口清单那条「98 条没人答」+ 「8 条外发依赖挂着」两笔老账一次清掉】★★ ⇒ ★**与 MECH 域同型单 ISS-313 (verified) 同一口径** ★ |
| ISS-361 | hw-lead | 2026-11-25 | ★★[★新主线·PCB 线·「板那一趟」封装真值覆盖缺口·纯分析+文档+机器闸·零写板] ★★【ISS-356 交卷的「封装真值基线」只覆盖 「必装 ∩ 非 NET/TP ∩ footprint 栏=='待定'」这个口径 ⇒ 实测 78(镜脚主PCB) + 22(镜框充电板) = 100 件; 但「板那一趟」真正要收口的是「板上 158 个占位脚号器件」⇒ 两集合只交 77 ⇒ 差集 81 件 = TP_* 42 + DNP 26 + ★★13 件【真器件·必装·非 TP】★★ ⇒ 那 13 件的 BOM footprint 栏写的是描述串 (例 `Q_AND` = `★板文件封装: 3 焊盘 ([待选型] N-MOS (硬件 AND))`) ⇒ 被 ISS-356 那【一个条件】挡在门外 ⇒ 其中 12 件在 `HW/FP_TRUTH_BASELINE.md` 里【没有目标 lib:name】⇒ 且 9 件正是那一趟的 P0 改项 (Q_AND/Q_PG/Q_ENVC 的 D/S/G vs G/S/D 脚序 · D_ESD_CAM 脚序反 · D_ESD_USB_D 2→3 脚 · 5 件按键 land 外扩) ⇒ ★★而 `state/board_trip_baseline_20260723.txt` 的 C4 判据写的是「158 全部收敛」⇒ 用 ISS-356 的基线【永远凑不齐】⇒ 那条判据目前【不可能满足】而没有任何闸会发现 ⇒ ⇒ 那一趟照现状开工会带着 81 件未收敛的占位脚号出板 ⇒ 【改了板却没改封装】⇒ 改完还是错的 ⇒ 板 md5 第二次变】★★ ★**本单只出【一页 + 一条机器闸】, 把这条判据从【一句话】变成【可数·可点名·可机器判】(★四桶目标值: TP 42 / DNP 26 / 靶内 77 / 缺口 13★)· 零写板·零落表·零外发·不代老板拍板**★ |
| ISS-362 | sw-lead | 2026-11-25 | ★★[★新主线·PCB 线·SW 侧「S10 换封装真值」那一跳的影响面·纯分析+沙盒预演+机器闸·零写板] ★★【「板只改一次」那一趟 (S1~S13) 会【合法地】把三份真源 (网表/脚表/BOM) 的 md5 一起换掉; SW 侧 7 道闸 + 1 道准出汇总闸 + 8 条板侧输入清单全部盯着这些真源; 但【S10 换封装真值】这一跳与【S1 改名】那一跳【换的东西根本不是一类】⇒ 而 SW 侧现在【没有任何一份文件】说明这一跳会发生什么 ⇒ 且 SW 侧还挂着 8 条引着【过期 md5】的待办重锚 need ⇒ ★★⇒ 本单 = 把「S10 换封装」这一跳对 SW 侧的全部影响做成【一页 + 一道沙盒预演闸】, 让那一趟当天 SW 侧【红的每一条都能被解释】而不是【现场抓瞎】⇒ 最坏的结果是有人为「让闸变绿」去改真源/改锚点/放宽判据 ⇒ 那正是 ISS-273/275/284 三单花大力气堵掉的「悄悄换真源」漏洞】★★ ★**本单【不许】往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条 (★那是改那一趟的清单·归 main 裁★) · 零写板·零落表·零改既有闸·零改锚点 md5·零外发·不代拍**★ |
| ISS-363 | sw-lead | 2026-11-25 | ★★[★新主线·PCB 线·SW 侧「S10 换封装真值」收口·纯分析+新建闸+沙盒预演·零写板] ★★【ISS-362 (sw-lead) 已把「S10 换封装真值」这一跳对 SW 侧的影响面交卷 (H1/H3/H4 三条是【登记式绿】⇒ 它把三个缺口【登记】上了, 但没有任何闸去判) ⇒ 而「板只改一次」那一趟 S10 会【合法地】把三份真源 (网表/脚表/BOM) 的 md5 一起换掉 ⇒ 若清单里没有这一条 ⇒ 那一趟当天 SW 侧没人认领这一跳 ⇒ 红了没人解释 ⇒ 最坏的结果是有人为让闸绿去改锚点/改判据 ⇒ 那正是 ISS-273/275/284 三单花大力气堵掉的「悄悄换真源」漏洞】★★ ⇒ ★**本单 = ① SW09 (清单第 9 条) 的 9 字段草案 + 「三处同批落地」的补丁清单 (★真件零改★) ② 新建 `SW/tools/check_fp_truth_read.py` (★把 H1 从「登记」变成「有闸」· 双态判据·不挂链★) ③ 沙盒预演: 三处同批落地 ⇒ 10 道 SW 闸全绿 + 反证「只改一处 ⇒ H4 红 + F4 红」 ④ 一页 + 交卷页 + 分片 + 留证** ★【纯分析 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★ |
| ISS-364 | hw-lead | 2026-11-25 | ★★[★新主线·PCB 线·HW 侧「S10 换封装真值」收口·纯分析+作业包+新建闸+沙盒可达性证明·零写板] ★★【ISS-361 (hw-lead) 已把「封装真值覆盖缺口」查清 (90 件 = 靶内 77 + 缺口 13 · 四桶 TP 42/DNP 26/靶内 77/缺口 13 = 158) ⇒ 而 main 15:3x 落进 `state/board_trip_baseline_20260723.txt` 的《订正一》写着「C4 目标 = 68 ⇒ 须【换官方 land 90 件 + 网表节点具名 90 件】」⇒ ★★但这句「可达」没有任何沙盒证明 ⇒ ★★而它已经是那一趟的验收条件 ⇒ ⇒ 同一类坑刚在 15:3x 踩过一次(原口径「158 全随封装基线收敛」被沙盒实跑推翻: 换 land 根本不动 C4, 只有网表节点具名才动)★ ⇒ ⇒ 本单 = 把这句话做成可执行 + 可证伪】★★ ⇒ ★**本单 = ① 逐件 90 行可执行作业包 (现占位几何 / 目标 lib:name + .kicad_mod + md5 / 目标几何 / 几何 Δ / pad↔net 序 / 要重接的 net / 腿 B 具名脚清单) ② 一条机器闸 (判几何不判 lib:name 字符串 · 板面 186 个封装库名全空 ⇒ 判字符串是哑弹) ③ 沙盒可达性证明: 158 → ? (腿 A / 腿 B 各自的 ΔC4 + 能不能到 68 + 到不了时真实可达值与差距) ④ 一页 + 交卷页 + 分片 + 留证** ★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★ |
| ISS-365 | mech-lead | 2026-11-25 | ★★[★新主线·PCB 线·MECH 侧「S10 换封装真值」影响面·纯分析+新建闸+沙盒重判·零写板] ★★【ISS-290 (mech-lead) 已把「S6 的 20 个目标落位 × MECH 保留区」逐个交叉核对过 (最小净距 4.6500) · 但那些数全是按【当前板上自绘占位 land】算的 ⇒ 而那一趟 S10 要把 90 件换成官方封装 ⇒ 器件 fab 外框/中心距/本体都会变 ⇒ ★★main 本机实算: 20 个 S6 落位 = 10 个 `R_SEL_*` + 10 个 `TP_DSI_*` ⇒ ★★那 10 个 `R_SEL_*` 全落在 90 件里 ⇒ ⇒ 换封装 ⇒ 4.6500 那条净距结论的几何基线会漂 ⇒ 而本机没有一条闸会知道 ⇒ ★★⇒ 不查清 ⇒ 那一趟改完板才发现结构装不下 ⇒ 板 md5 变第二次 ⇒ 整趟白跑】★★ ⇒ ★**本单 = ① 敏感度逐件表 (现占位几何 / 目标封装几何 / Δ / 碰 MECH 哪一条 / 判定 / 重算后的数) ② 那 10 个 `R_SEL_*` 的专项 (换封装前后净距两列 + Δ + 要不要重排) ③ 负结论机器化 (座体类 6 组 + 10 个 `TP_DSI_*` 与 90 件交集 = ∅ ⇒ 不受 S10 影响) ④ 一条机器闸 + 沙盒三道 MECH 闸换封装前后的并排输出 + 一页 + 交卷页 + 分片 + 留证** ★【纯分析 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★ |
| ISS-366 | hw-lead | 2026-11-25 | ★★[★新主线·PCB 线·网表侧·「板那一趟」S10 同批的【网表硬缺陷】补行作业包·纯作业包+沙盒+新建闸·零写板·零落表] ★★【ISS-364 (hw-lead, 17:16 交卷) 挖出第 3 条新事实: 「4 件的 GND 脚在网表里根本不存在 (C_KEY_PWR / C_KEY_VM / C_KEY_VP / R_BAT_DET_2) ⇒ 光改名不够, 必须补 4 行」⇒ 同一根因早在 ISS-356 的 D1 查清并登记成 need `iss356_netlist_4rows_gnd_fix` (★`to` = 「落表批次」★) ⇒ ★★但那只是一张【排进那一趟的待办】, 不是一张【可执行作业包】★★ ⇒ ★★「板只改一次」那一趟开工当天, 这 4 行没有逐字改法 / 没有沙盒证明 / 没有回滚说明 ⇒ ⇒ 要么当天气到补 (★落表批次地界 · 现场改真源 = 违纪律★), 要么漏掉 ⇒ ★★板子做出来是: 3 颗 100nF 去耦电容接地端悬空 (去耦失效) + R_BAT_DET_2 是 BAT_DET 分压链下臂未接 GND (电池检测读数无意义) ⇒ 这是一张能出厂的坏板, 不是纸面瑕疵★★】★★ ⇒ ★★本单 = ① 4 行的逐字改法映射 (★网表哪一行 / 改成什么 / 脚表要不要同步 / 生成器要不要改★) ② 连带 ISS-364 挖出的第 6 条差异 `R_PU_PG` (板面 pad1/pad2 与脚表真值相反) 的逐字改法 ③ 沙盒实跑: 补 4 行 ⇒ C1/C3/C4 的 Δ + 板面 land 数从 1 变 2 ⇒ 证明【补行】这条路走得通 ④ 一条机器闸 (★判「这 4 件在网表里有没有 GND 脚」+「脚表与网表的脚数是否一致」·★不许判 md5★) ⑤ 一页 + 交卷页 + 分片 + 留证★ ★★【纯作业包 + 沙盒 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★ |
| ISS-367 | mech-lead | 2026-11-25 | ★★[★新主线·PCB 线·MECH 侧·「板那一趟」S10 换官方 0805 后的【LED 窗口规格同趟重算】·纯文档定点改写+新建闸+沙盒重算·零写板·零落表] ★★【ISS-365 (mech-lead) 交卷实测: `D_LED_G` 换官方 0805 后 `led_space` 铜箔相对原点偏移变 ⇒ 两条可放行带 + 可落位块数全变 (1992→2183, 带 A 宽 −0.875), 且 sweep 不再单调 (clr=0.5 的 2197 < clr=0.2 的 2253) ⇒ 既有页 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2 那句「块数不变」的后半句【作废】, 必须同趟重算 ⇒ ★★ISS-365 交卷页明写「E-9 剩下两处 (MECH_SYNC 机器块 + BOARD_PORT_OPENING_S6_FRAME_CALIBER 的 LED 窗口规格) 仍归 main 派活」★★】★★ ⇒ ★★本单 = ① 一页 (漂移本体 + 两处逐字改法 + 同趟重算清单) ② 一条机器闸 (L0~L6·判内容不判 md5·selftest ≥6/6) ③ 交卷页 + 分片 + 留证★ ★★【纯文档定点改写 + 新建闸 + 沙盒重算类 · 零写板 · 零落表 · 零改既有闸 · 零外发 · 不代老板拍板】★★ |
| ISS-368 | sw-lead | 2026-11-25 | ★★[★新主线·PCB 线·SW 侧·「板那一趟」SW09 清单第 9 条的【三处同批落地】补丁·纯作业包+沙盒 dry-run+新建闸·零写板·零落表] ★★【main 2026-11-23 16:58 已裁: 「加第 9 条」= 加, 但必须三处同批落地 (① `SW/BOARD_ONEPASS_SW_SYNC.md` 的 §2 表 + §2.1 分布表 + §6 JSON 块 ② `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` 的 H4-REG 三数字 8→9/0→1/4→新值 ③ 本单新闸 `SW/tools/check_fp_truth_read.py`); ★**真件落地 = main 的一键动作 (落表批次地界)** ⇒ 本单只交【幂等补丁 + 副本 dry-run 证明 + 回滚说明】· 真件零改★ ⇒ ★★「板只改一次」那一趟 (S1~S13) 会【合法地】把三份真源的 md5 一起换掉 ⇒ 若三处不同批落地 ⇒ 清单页说 9 条 / ISS-362 页说 8 条 / 闸按 8 条判 ⇒ 那一趟当天必然「清单与闸互相打脸」⇒ 最坏是有人为让闸绿去改锚点/改判据 (★正是 ISS-273/275/284 堵掉的漏洞★)★★】★★ ⇒ ★★本单 = ① 一页 (三处逐字规格 + 幂等性 + dry-run 证明 + 回滚) ② 幂等补丁脚本 (★默认干跑·只许写副本★) + 一条机器闸 (selftest ≥6/6) ③ 交卷页 + 分片 + 留证★ ★★【纯作业包 + 沙盒 dry-run + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板】★★ |
| ISS-370 | sw-lead | 2026-11-25 | ★★[★新主线·PCB 线·SW 侧「腿 B 网表节点具名」对 SW 判据链的影响面·纯分析+作业包+新建闸+沙盒预演·零写板] ★★【ISS-364 (hw-lead) 已把腿 B 的 200 条指令 (改名 196 + 补行 4) 做成逐条可执行作业包, 并用沙盒证明 C4 158→68 只靠腿 B (腿 A 换 land 贡献实测为 0); 而 main 2026-11-23 17:4x~17:5x 本机实跑发现: ★★把腿 B 的网表喂给 SW 侧闸, `SW/tools/timing_check.py` 从 85/85 全过掉到 70/85 (15 条红)★★ ⇒ 对照组 (同内容换路径) 85/85 ⇒ 是内容不是路径; 再拆: 只改名 = 14 条红 / 只补行 = 2 条红 (且那 2 条是【落表义务】不是语义破坏) ⇒ 根因 = 腿 B 把节点串从裸位号改成 `ref pinN`, 而 timing_check 的 `resolve_chain_landing()` 判中点网用的是【精确字符串相等】★ ⇒ ⇒ ★★不查清 ⇒ 那一趟开工当天 SW 门禁当场红 ⇒ 要么硬改闸 (把红项调没·正是 ISS-273/275/284 堵过的漏洞) 要么板 md5 变第二次 (违「板只改一次」)★★ ⇒ ★★本单 = ① 15 条红逐条表 (红因/归类/修法/自证回绿) ② 「腿 B ⇒ SW 侧必须同批改的活」逐件清单 (照 ISS-323 范本) ③ 一条机器闸 (含「语义红 vs 落表义务红 可分离」判据) + 沙盒三组对照预演 + 一页 + 交卷页 + 分片 + 留证** ★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★ |
| ISS-369 | hw-lead | 2026-11-26 | ★★[★新主线·PCB 线·HW 侧·「板那一趟」S10 的【板面库封装名 0/186 全空】写盘作业包·纯作业包+沙盒+新建闸·零写板·零落表] ★★【ISS-361 实测: 板面 186 个封装 · 库名 (`GetFPIDAsString()`) 唯一值 = `''` ⇒ 板是【自绘通用占位】; ISS-363 交卷: 「板面 186 个封装库封装名 0/186 非空 ⇒ S10 那一跳必须先把『板面补库封装名』排进板那一趟」; ISS-364 交卷: 90 件换封装作业包 (§1 每件 12 字段: 目标 lib:name + .kicad_mod 路径 + md5 + 几何 Δ) 已在盘; ★**main 独立重算 (真闸代码): 真网表 C4 = 158 ⇒ 腿 B 后 C4 = 68 ⇒ 四桶 TP42/DNP26/靶内77/缺口13 = 158 ⇒ 腿 A (换官方 land) 对 C4 贡献实测为 0**★ ⇒ ★★「换封装」与「补库封装名」是同一件事的两半: 缺任一半, 那一趟都交不出可投产的板 (装配厂拿不到正确封装 + BOM 与板面对不上 + 板 md5 第二次变)★★】★★ ⇒ ★★本单 = ① 一页 (板面现状 + 本机 KiCad 写盘机制实测 + 90+96 件目标清单 + 「写库名不改语义」的判定) ② 沙盒 (副本上换 land + 写 lib_id ⇒ 真闸 C1~C4 ⇒ C4 仍 158) + 一条几何闸 (selftest ≥6/6) ③ 交卷页 + 分片 + 留证★ ★★【纯作业包 + 沙盒 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★ |
| ISS-371 | mech-lead | 2026-11-26 | ★★[★新主线·PCB 线·结构侧·「板那一趟」`J_DEBUG` 排针 land 改 1.27mm 后的净距真相·纯分析+文档订正(追加式)+新建闸+沙盒预演·零写板] ★★【★main 2026-11-23 20:4x~20:5x 本机实算★: 现有四处 (HW 作业包 §C-SEAT-1 + MECH 三页 + 机器块) 同源推导写的「改 land 到 1.27 ⇒ 铜箔 X 宽 4.0850 / 单边间隙 3.0575 / 最坏 2.7575」, 而本机实读官方真 land `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 的 pad 是 1.0×1.0 (不是现页沿用的 0.275) ⇒ 铜箔 X 宽 = 3.81+1.0 = 4.8100 ⇒ Δ +0.7250 ⇒ ★★现页每个数都偏乐观 0.3625mm; 且清空区若仍按 4.0850 留, 最外侧焊盘每边越界 0.3625 ⇒ 铜箔直接进清空区⇒ 板只改一次那一趟开工前不算清 ⇒ 要么改结构件返工, 要么板 md5 变第二次⇒ 整趟白跑★★ ⇒ ★★本单 = ① 一页逐条量差表 (三档口径 × 每一项·每格带复跑命令) ② 一条【官方 land 实读 + 清空区不许越界 + 单边间隙对称且 ≥CRIT】的机器闸 ③ 追加式订正块 (老字一字不删·机器块只加字段不改旧字段值) + 降级方案 (SMD 2×2 交错变体) 整段重算 + 换型 (SMD占位→THT) 的环宽 [0数据] ④ 答掉 `hw.yaml` 里挂了没人答的 need `iss356_jdebug_mech_clearance_recheck` (to=mech-lead·since=2026-11-23)** ★【纯分析 + 文档订正 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★ |
| ISS-372 | sw-lead | 2026-11-26 | ★★[★新主线·PCB 线·SW 侧·「板那一趟」S9 换基线 · SW 侧板 md5 引用面清账 + 一条「钉板 md5 闸清单」自守闸·纯分析+作业包+新建闸+沙盒预演·零写板] ★★【★main 2026-11-23 20:4x~20:5x 本机实读★: SW 域 17 个活文件 / 57 处硬写旧板 md5 `611b869e…` (3 个判据脚本 + 14 个 .md); 而那张「钉板 md5 的闸清单」是 2026-11-17 20:49 生成的, 今天新造的 2 道 SW 闸 (ISS-363 17:27 / ISS-370 19:50) ★**既没进那张表、也没有合法改板通道**★ ⇒ 改板当天它们必红 (F5 判板 md5≠基线 ⇒ 红; G8 判板 md5≠受保护基线 ⇒ 红), 而红的真含义是「板被换了」不是「板改坏了」⇒ 现场极可能误读⇒ 去改板凑绿⇒ 板 md5 变第二次⇒ 整趟白跑 ★**⇒ 且那张表没有任何闸在守它新鲜 (本机实读: `state/gate_check.py` 零命中) ⇒ 下一道新闸再硬钉板 md5 时没人拦** ★★ ⇒ ★★另: 57 处不是同一种东西 —— 判据锚 (必须随板改) / 规格页引用 (那一趟随板改·平时不许动) / 历史留证 (★永远不许改★) 三类处置方式【完全相反】⇒ 「改板那天全仓 sed 替换一遍」是错的 (会把历史留证改成假记录) ⇒ 必须逐处分类 ★★ ⇒ ★★本单 = ① SW 域 57 处逐处清账 (哪处随板改 / 哪处永远不许改 / 哪处交 main) ② 一条【清单新鲜度 + 缺口登记】自守闸 (★「登记过的缺口」不红, 「没人知道的缺口」才红 ⇒ 下一个新闸当场被抓住★) ③ 一条「判据锚不许伪装成历史留证」的反向判据 ④ 答掉挂了两周的过期 need `iss249_kicad_sch_md5_not_anchor_sw` (★main 实测: 那两条门禁跑完 .kicad_sch md5 一字未变·且 SW 域对它的命中 = 0 ⇒ 两个前提一个不成立一个没落地★)** ★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★ |
| ISS-373 | hw-lead | 2026-11-26 | ★★[★新主线·PCB 线·HW 侧·「板那一趟」S10 换件集合的【唯一真源】+ 一条「集合口径」机器闸·纯分析+作业包+新建闸+沙盒预演·零写板] ★★【★main 2026-11-23 22:4x~23:0x 本机实算★: 「S10 那一趟换几件」在全项目同时活着【四套口径】—— ① `MECH/check_onepass_s10_fp_swap_impact.py` 实跑 ⇒ 90 (靶内 77 + 缺口 13) · ② `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §3.3 (ISS-369) ⇒ 90 / 96 / 186 / 158 · ③ `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` §1.6 (ISS-367) ⇒ ★**同一页里「90」与「91」并存** ★ · ④ `MECH/check_onepass_s10_led_spec_sync.py --compute` 实跑 ⇒ ★**`swap_all90_n: 91` (变量名叫 all90、值是 91)** ★ ⇒ ★★main 本机实算 (用 ① 与 ③ 各自的真函数): C4=158 · iss356=78 · inter=77 · gap=13 · `iss - inter - gap` = `['J_DEBUG']` (★**恰好一件★) ⇒ **90 = inter + gap · 91 = iss + gap** ★★ ⇒ ★★而 `J_DEBUG` 恰恰是那一趟【另一条腿要换 land】的那件 ★★ (★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (ISS-290 · step S6) 原文「`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm」+ 期望读数「J_DEBUG land pitch = 1.27」★) ⇒ ★★而 ISS-369 表 B 那行写「不写库名」的理由正是「本件不在 90 件换 land 名单里 ⇒ 本趟不动它的 land」★★ ⇒ ★★**若那一趟换 91 件 ⇒ 按 ISS-369 自己的 §2.3 (换 land 必须同时写库名) ⇒ 「写 94 / 不写 92」两个数也要跟着变** ★★ ⇒ ★**这一件换不换 land, 两条路的结构后果完全不同 ⇒ 是「板 md5 会不会变第二次」的开关** ★ ⇒ ★★**本单 = ① 一页集合真源 (四套口径逐条对表 + `J_DEBUG` 四条腿的完整账 + 两条路各自的联动手算式) ② 一条「集合口径」机器闸 (L0~L8 · 集合算法自算不许写死 90/91 · 差集必须恰为 1 件 · 页里两个数都要在) ③ 沙盒 S0/S1/S2 三轮 (90 件 vs 91 件各换一次, 报 C1~C4 + 段数/过孔/零铜网/单边零铜对 + `J_DEBUG` 换完的实测 land pitch/铜箔宽/fab) ④ 未决项只登记不代拍 (★「`J_DEBUG` 那一趟换不换 land」归 main 裁★)** ★ ★【纯分析 + 作业包 + 新建闸 + 沙盒预演类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★ |
| ISS-374 | mech-lead | 2026-11-26 | ★★[★新主线·PCB 线·结构侧·「板那一趟」`J_UART` 排针 land 改 1.27mm 的结构侧净距真相 (ISS-371 的姊妹件·同一条 `B33` 板侧项)·纯分析+文档订正(追加式)+新建闸+沙盒预演·零写板] ★★【★main 2026-11-23 22:4x~23:0x 本机实算★: ISS-371 (2026-11-23 22:4x 刚被 main 签收 verified) 交付了 `J_DEBUG` 这颗 1×4 排针的结构侧净距真相(一页 + 一条闸 `MECH/check_jdebug_1p27_clearance.py` · 本机 22:5x 实跑 rc=0 · 7/7 全绿), ★**但 `J_UART` 那颗 1×2 排针在同一条板侧项里结构侧一个字都没有**★ —— ★**① 同一条项点了两件★**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (ISS-290 · step S6) 原文「`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」+ 期望读数「J_DEBUG land pitch = 1.27 / J_UART land pitch = 1.27」 ⇒ ★**「换 1.27」板上落两件, 结构侧真相只做了一件**★ · ★**② ISS-371 的真相页对 `J_UART` 零覆盖★**: 本机实跑 `grep -c J_UART MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ⇒ **0** (★不是「提了一句」, 是整颗件没进这一页★) · ★**③ ISS-371 的闸也只认 1×4 那颗★**: 该闸常量 `THT_MOD_NAME = PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ⇒ ★**`J_UART` 那颗件的 land 改了, 这条闸不会红**★ ⇒ ★★**main 本机实算 (★读板 + 读盘上 `.kicad_mod` + 算★)★**: `J_UART` 现状 = 2 pad · pitch 0.50 · pad 0.275×0.900 · 铜箔 X **18.5025..19.2775 (宽 0.7750)** · fab 6.000×4.000 · net UART_TX/UART_RX ⇒ 官方 `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` 实读 = pad1 `thru_hole rect` (0 0) size 1 1 · pad2 `thru_hole circle` (0 1.27) size 1 1 ⇒ 摆成板上 X 向 1×2 后 ★**铜箔 X 宽 = 1.27 + 1.0 = 2.2700**★ · 座体必须清空区 (★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5 本机实读★) X **17.620..20.160 (宽 2.5400)** ⇒ ★★**每边余量 (2.5400 − 2.2700)/2 = 0.1350 < `CRIT` 0.60 (★`MECH/service_port_check.py` L127 真身★) ⇒ 铜箔进座体必须清空区**★★ (★现状每边 0.8825 ⇒ Δ −0.7475★ ⇒ ★**方向与 `J_DEBUG` 那颗【相反】** (★J_DEBUG 仍过 CRIT·余量 3.99×·ISS-371 已算★)★) ⇒ ★★**⇒ 那一趟若照 `B33` 把 `J_UART` 也换成官方 land ⇒ 结构件装不上 ⇒ 要么改结构件返工, 要么板 md5 变第二次 ⇒ 整趟白跑**★★ ⇒ ★★**本单 = ① 一页 `J_UART` 真相 (与 `J_DEBUG` 并排对照 · 现状/官方THT/官方SMD降级 三档量差 · 两个后果分开写 · 降级方案给代价不代拍) ② 一条 `J_UART` 专用闸 (J0~J8 · 官方land几何自算不许写死 · 两件方向结论必须并排出现 ⇒ 防「拿一颗的结论套另一颗」· ≥8 条反向用例含 2 条针对该病根) ③ 沙盒 S0/S1/S2/S3 四轮 (含 S3 反向对照轮: `J_DEBUG` 也换一次 ⇒ 证明两件方向确实不同, 若算出一样则停下报告不许硬写「过」)** ★ ★【纯分析 + 文档订正(追加式) + 新建闸 + 沙盒预演类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 (含 ISS-371 已签收件) · 零挂链 · 零外发 · 不代老板拍板】★★ |
| ISS-375 | sw-lead | 2026-11-26 | ★★[★新主线·PCB 线·SW 侧·「板那一趟」`J_DEBUG`/`J_UART` 排针换 land 后的【物理针序契约】(pin1 朝向 / JTAG 线序) + JTAG 链 SoM 侧真相·纯分析+文档+新建闸+沙盒预演·零写板] ★★【★main 2026-11-23 22:4x~23:1x 本机实读 + 本机实算★: ISS-371 (2026-11-23 22:4x 刚被 main 签收 verified) 自己已经在 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 点了这件事但只点到一半 —— 原文「★**① 居中解 rot 90° ⇒ 原点 (141.0450, 56.6000) ; ② 居中解 rot 270° ⇒ 原点 (144.8550, 56.6000) ★**两条都过 `CRIT` ; 但 ① 与 ② 的 pin1 朝向相反 (JTAG 线序要跟 hw-lead 对齐)** ★ · … ⇒ ★**板那一趟必须写死** ★」⇒ ★★**而「必须写死」的那件事, 全项目至今【没有任何一处】写死了** ★★ ⇒ ★**main 本机实跑 pcbnew 验过 (★用 KiCad 自己的 FOOTPRINT 变换·不是手算★)★**: rot 0 ⇒ pad abs X 142.2/142.7/143.2/143.7 (★现状顺排·TCK→TDO·★且现状【无 pin1 极性标记】·四 pad 全 RECT SMD·★所以今天「pin1 在哪」只是网表约定, 不是实物事实★) ; rot 90 ⇒ pad abs X 全 142.9 ; rot 270 ⇒ 全 145.7 ⇒ ★**配官方 land 的局部坐标 (pad1=(0,0)·pad2=(0,1.27)·pad3=(0,2.54)·pad4=(0,3.81)·轴向=局部 Y) ⇒ rot 90 ⇒ pad1 在 X 最小端 (顺排) ; rot 270 ⇒ pad1 在 X 最大端 (逆排) ⇒ 两候选互为镜像** ★ ⇒ ★**官方 land 自带 pin1 极性标记 (★本机实读 .kicad_mod★)**: pad "1" = `thru_hole rect` (★方形 = 行业标准 pin1 标记★) · pad "2"/"3"/"4" = `thru_hole circle` ⇒ ★**换官方 land 后板面【第一次】出现 pin1 标记 ⇒ 选错 = 实物排线插反 ⇒ JTAG 救砖链不通 ⇒ 而 `SW/FLASH_AND_VERSION.md` 的 4 级救砖里 S3 = JTAG 是【除返厂换板外】唯一的软救砖路径** ★ ⇒ ★★**更狠的一半: JTAG 链在 SoM 侧【今天就是断的】★★** (★本机实读 `HW/netlist_v1.csv` 第 388/390/392/394 行★) ⇒ `JTAG_TCK_SOC`/`JTAG_TMS_SOC`/`JTAG_TDI_SOC`/`JTAG_TDO_SOC` 四条网的 SoM 侧端点 ★**全部是 `SoC_NC`**★ ⇒ ★**且 `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行: 四条 JTAG 信号在官方 399 行脚表里【没有同名/后缀相同的信号】**★ ⇒ ★★**⇒ 与 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 ISS-344 终裁直接冲突** ★ (★终裁把 `JTAG_TDI` 判为「★**必需**★ (★进 S8 布线目标·★**板侧不许标 NC / no-connect**★)」, ★**而网表里它此刻就是 `SoC_NC`**★) ⇒ ★★**「那一趟选哪个 pin1 朝向」【救不了这条链】⇒ 这件事必须在【开工前】被看见, 不是板做完才发现** ★★ ⇒ ★★**本单 = ① 一页物理针序契约 (逐件给现状/官方标记/两候选朝向/四线物理线序/裁决建议+代价/落点写死值) ② 一条闸 (D0~D8 · 官方 land pad1 形状自算不许写死 · 两候选针序必须由 KiCad 自己的变换算出且互为逆序 · 页与闸不许各说各话 · 网表 SoC_NC 结论必须实读相等 · 零挂链) ③ 沙盒 S0~S3 (含 S1↔S2 的【几何完全等价】与【针序互为逆序】两件事分别用数证明)** ★ ★【纯分析 + 文档 + 新建闸 + 沙盒预演类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★ |
| ISS-376 | hw-lead | 2026-11-26 | ★★[★新主线·PCB 线·HW 侧·「板那一趟」`J_DEBUG` 换官方 1×4 THT land 的**落位可行性**穷举（现位放不进 ⇒ 挪哪 / 挪多大 / 挪完还剩什么）·纯分析+沙盒预演+新建闸·零写板] ★★【★main 2026-11-24 00:5x~01:0x 本机实读+本机实算 (★不抄任何 agent 报告★): ★**ISS-373 沙盒 S2b 实测: 官方 1.27mm 4×THT land 放不进 `J_DEBUG` 现位** ⇒ ★**PTH pad1 (144.3000,58.0000) vs via `JTAG_TDO` (143.7000,57.9500) 孔净距 `0.1271` (要求 ≥`0.25`) · PTH pad3 (146.8400,58.0000) vs via `XTAL_OUT` (146.9500,57.9500) 孔净距 `0.0000`** ⇒ ★**⇒ DRC `hole_to_hole` 由 `0` → `4`** ⇒ ★**⇒ 「那一趟换 91 件」这条路卡死在一个具体的物理点上** ⇒ ★**本单 = 把【挪哪 / 挪多大 / 挪完还剩什么】三个问题用机器算出来, 交 main 裁「那一趟换不换 land (90 件 vs 91 件)」**★ ★★★★**开单依据**: ① ★**ISS-373 (hw-lead) 已于 2026-11-24 00:5x 由 `state/_apply_20260724_0050_cronfb67_sign_iss373.py` 独立复核签收 verified (★37 条验收线全绿 + 自测 7/7★) ⇒ ★**hw-lead 槽位空出来** ★ ② ★**兄弟 job 775d9893 于 2026-11-24 00:24:07 被【cron 执行超时 (60 分钟硬墙·externalAbort=true)】掐死, 它的下一轮 01:24 才到 ⇒ ★**这一小时 hw-lead 无活可干** ★ ③ ★**ISS-373 的沙盒已把死结定位到具体坐标, 但「挪哪 / 挪多大 / 挪完还剩什么」这三问【全项目至今没有一份机器算出来的答案】⇒ ★**这是「板只改一次」那一趟开工前的必要前置** ★ ★★★★**类别**: ★**纯分析 + 沙盒预演 + 新建闸 · 零写板 · 零落表 · 零改既有闸/既有页面 · 新闸零挂链 · 不代拍** ★★ |
| ISS-377 | mech-lead | 2026-11-26 | ★★[新主线·PCB 线·结构侧·「板那一趟」] 座体净距判据**同源化** (`J_DEBUG` 铜箔支配 vs `J_UART` 座体支配 ⇒ 统一成一张表) + 座体真实型号**官网自查找证** (查不到 ⇒ 降级方案) |
| ISS-378 | sw-lead | 2026-11-26 | ★★[新主线·PCB 线·SW 侧·「板那一趟」] `J_DEBUG`/`J_UART` 排针换 land 后的**固件影响面清单** + ★★`ISS-344` 与「SoM 侧无 JTAG 引出」的**板侧口径冲突收敛** (官网自查证)★★ |
| ISS-379 | hw-lead | 2026-11-26 | ★★[★新主线·PCB 线·HW 侧·「板那一趟」] `J_UART` (1×2) 换官方 P1.27 THT land 的**落位可行性**穷举(现位放不下 ⇒ 挪哪 / 挪多大 / 挪完还剩什么)·纯分析+沙盒预演+新建闸·零写板] ★★【ISS-376 (`J_DEBUG` 1×4) 的对称件 · E-1 判定两件的 land pitch `0.50→1.27` 同一趟做完 ⇒ `J_UART` 这一半至今没人算过】★★ |
| ISS-380 | hw-lead | 2026-11-26 | ★★[★新主线·PCB 线·HW 侧·「板那一趟」] `J_DEBUG` / `J_UART` 座体的【厂商具体型号 + 座体真实高度 + 厂商 keepout 图纸】官网自查证 (★OI-10 + iss267 第①③条合并·纯分析/作业包类·零写板) ★★ |
| ISS-155 | main | 2026-11-27 | ★★★★[demo 头号卡点] rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 target 转的 .rknn 能否在 RK3572 上跑通 (板端验证) —— 且板子当前不可达 ★★【2026-11-23 07:3x main 裁决 · ★★降级 · 本单不再是 demo 头号卡点 · 余项 = 转换链已通 / 板端接受性 [0数据]·待板★★】★**老题面 (rk3576 target 那条问法) 保留作历史留档·结论不再引用** ★ |
| ISS-381 | sw-lead | 2026-11-27 | ★★[★新主线·PCB 线·SW 侧·「板那一趟」] 布线验收线之【零假连通】自检闸: 每条必需网按预期拓扑逐条列铜 (★纯分析+新建闸+沙盒预演·零写板) ★★ |
| ISS-382 | mech-lead | 2026-11-27 | ★★[★新主线·PCB 线·MECH 侧·纯分析+新建闸·零写板] `J_DEBUG` 已签收真相页的 `2x2` 排布标签与实测矛盾 (★实测是 2 列 × 4 行★) + 对应闸 `G5` 只查「有没有写交错」不查维数 (★真实盲区★) ★★ |
| ISS-383 | hw-lead | 2026-11-27 | ★★[★新主线·PCB 线·HW 侧·纯分析+新建闸·零写板] 座体选型的【四方对齐作业包】: 候选件真实规格 / 库封装可得性 / BOM 型号栏草案 / 三方口径闸 ★★ |
| ISS-384 | hw-lead | 2026-11-27 | ★★[★新主线·PCB 线·HW 侧·纯文档+新建闸·零写板] 「板只改一次」那一趟的【充电电流档位活值口径收口】: 把 0.822 旧系数从三份 HW 活文档清干净 + 补 R10 闸的判定面盲区 ★★ |
| ISS-385 | sw-lead | 2026-11-27 | ★★[★新主线·PCB 线·SW 侧·纯分析+新建闸·零写板] EVT `PWR-05` 充电电流判据与现行 `R_ILIM` 体系【不相容】的机器可判定化 ★★ |
| ISS-386 | mech-lead | 2026-11-27 | ★★[★新主线·PCB 线·MECH 侧·纯分析+新建闸+沙盒·零写板] 「板只改一次」那一趟的 `J_DEBUG` + `J_UART` 两连接器【座体 / 开口 / 清空区 三件合到一件答】 ★★ |
| ISS-387 | hw-lead | 2026-11-27 | ★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建闸·零写板] 「板只改一次」那一趟的 `J_DEBUG`/`J_UART` 单排直插【原厂 land 几何】官网查证 + 与盘上通用封装逐项对比 + 对 MECH 3D 判据链的传感到影响面 ★★ |
| ISS-388 | sw-lead | 2026-11-27 | ★★[★新主线·PCB 线·SW 侧·纯分析+新建闸·零写板] 两道【已签收 verified】的 SW 闸今天实测【真的坏了】⇒ 把「闸的失效」本身变成可判的 (★判据与环境耦合 + 账本与现实漂移★) ★★ |
| ISS-389 | mech-lead | 2026-11-27 | ★★[★新主线·PCB 线·MECH 侧·纯分析+作业包+新建闸·零写板] `J_DEBUG`/`J_UART` 两连接器的【座体 / 开口 / 清空区 三件合到一件】的结构侧收口作业包 ★★ |
| ISS-390 | mech-lead | 2026-11-27 | ★★[★新主线·PCB 线·MECH 侧·纯查证+新建闸·零写板] `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官网查证 + 「通用库件 courtyard 被当成厂件」这条前提订正 + 降级方案 ★★ |
| ISS-391 | hw-lead | 2026-11-27 | ★★[★新主线·PCB 线·HW 侧·纯分析+作业包+新建闸·零写板] 「板只改一次」那一趟的排针 land 【`0.65 → 0.71` 钻孔这一条板侧改动还没进作业包/预检清单】⇒ 把它补进去 (★纯分析 + 改文档 + 新建闸·零写板·零落表·零改既有闸★) ★★ |
| ISS-392 | sw-lead | 2026-11-27 | ★★[★新主线·PCB 线·SW 侧·纯分析+新建真相页+新建闸·零写板] SW 域【门禁链覆盖率 + 第三道病闸基线漂移】⇒ 把「板那一趟的 SW 侧护栏到底有几道真的在跑」变成机器可判 ★★ |
| ISS-393 | mech-lead | 2026-11-27 | ★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建闸·零写板] 「通用库件 courtyard 被当成厂件」这条前提错误的扩散面清账 + 判决链重算 ⇒ 把「换厂件之后哪些数要重算」变成机器可判 ★★ |
| ISS-394 | hw-lead | 2026-11-27 | ★★[★新主线·PCB 线·HW 侧·纯分析+新建真相页+新建闸·零写板] 座体选型结论【只写在 issue_log 里, 没落到活页面/已闭答案/未答 need/闸源码】⇒ 那条被推翻的结论现在是【活的】⇒ 把「结论被推翻后活副本必须被点名」变成机器可判 ★★ |
| ISS-120 | sw-lead | 2026-11-30 | ★S2 救砖链路板端实测 (量产一票否决项) —— 方案+自检已闭环 (ISS-080), 待 EVT 有板后真跑 (EVT-8/BR-01) |
| ISS-347 | main | 2026-11-30 | ★★[★主线·派活/门禁机制侧·内部活·零写板] ★★【`state/advance.py --apply` 的落盘路径一直是坏的: `state/dispatch_log.yaml` 顶层是 list ⇒ 旧代码 dl.setdefault('dispatches',[]) ⇒ AttributeError ⇒ 两个 cron job 的「派完标 fixing + 写派活日志」从来没自动跑通过 ⇒ 修 (两种形状都认 + 追加式写回 + 写回后自检) + 端到端单测 5/5 (含反向用例: 旧备份跑同一沙盒必须复现 AttributeError)】★★ |
