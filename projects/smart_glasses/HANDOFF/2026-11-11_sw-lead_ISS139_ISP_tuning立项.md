# 2026-11-11 sw-lead · ISS-139 ISP tuning 立项交卷

| 项 | 内容 |
|---|---|
| 作者 | 软件总工 (sw-lead) · 2026-11-11 19:1x |
| issue | **ISS-139** (owner=sw-lead · verify_by=main · severity=blocker · status 仍是 `fixing` —— ★**改状态是 main 的活**) |
| 交付物 | ★**立项书** `SW/ISP_TUNING_INITIATION_PLAN.md` · ★**机检脚本** `SW/tools/iq_coverage_check.py` · ★**本文** (含 §B 问询清单) |
| 边界 | ★**未联网** · ★**未联系任何供应商/服务商** · ★**未改任何既有文件** (含 `SW/DEMO_OD_PIPELINE_SPEC.md` 与全部 `HW/**`) |

---

## B1 结论摘要

1. ★**这笔账躲不掉**: 本机快照 `HW/_os_snapshots/rkaiq_iqfiles.json` (166 项) 实测 ⇒ ★**ar0234 = 0 命中 / ov04c10 = 0 命中** ⇒ ★**不管选 C 还是 D, tuning 都必须做** —— 与选路解耦, 可立即开工。
2. ★**最小账 = 两条, 不是一个**:
   - ★**demo 段 (路径 B / IMX415)**: **1~2 人日 + 1 次样机窗口 (灰卡/暗室 半天~1 天)** —— ★**因为现成 IQ 的 `sensor_calib.resolution` 明写 3840×2160 而我们走 1080p60 ⇒ 缺 mesh ⇒ "路径 B tuning = 0" 不成立**。
   - ★**整机段 (路径 A / AR0234CS)**: **1~2 人周 (5~10 人日) + 1~2 天暗室窗口**, 且**必须等镜头/模组定版**。
3. ★**谁来做**: 建议权重 **②模组厂随货 / ③第三方服务商 远低于 ①自研** (瓶颈是工具+环境+绑定关系, 不是算法) —— ★**但本单不替老板拍板**, §2 给三份可比较的账; ★**外发一律经项目总工**。
4. ★**验收写成"怎么量"**: 画质四问 (白平衡/色温/暗角/噪点) + ★**"OD 真正吃到的输入分布"** (ISP 输出 → 与板端逐字一致的预处理 → 与量化校准集同口径统计 → 端到端 F1 收口) —— ★**不看"出图好不好看"**。
5. ★**排期**: 与 ISS-144 并行不等 (★注: **ISS-144 现状是 deferred**, 老板 11-02 19:29 口径 demo sensor 改用 IMX415 ⇒ 本单天然分 demo 段 / 整机段); ★**标定窗口要占样机档期** (`HW/STEP1_LANDING_LIST.md` **F9 = 🔄 待清**, 清单里唯一一条以 ISP tuning 为名的项) ⇒ 已写 needs_from。
6. ★**一条额外发现 (口径级)**: OD 输入取自 NV12 的 **Y 平面** ⇒ ★**U/V 色度被丢掉** ⇒ ★**"出图色温好看" 与 "OD 输入分布合格" 不是同一件事**, 必须分开测 —— 否则 ISP 把画面调艳了而 OD 精度已经塌了, 看图是发现不了的。

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 (本单交付物自身的标准) | 判定 | 证据 |
|---|---|---|---|
| 1 | 立项书 6 节齐全 (工作量与前置条件 / 三条路线对比 / RK3572 专属风险 / 验收判据 / 排期账 / 与 OD 链路耦合) | ✅ **通过** | `SW/ISP_TUNING_INITIATION_PLAN.md` §1~§6 |
| 2 | "现成 IQ 覆盖表"机检脚本落盘, rc=0 | ✅ **通过** | `python3 SW/tools/iq_coverage_check.py` ⇒ 16/16 通过, rc=0 |
| 3 | 脚本 `--self-test` 含**反向用例** (改坏判据必须变红) | ✅ **通过** | 4 个反向用例全被抓住, rc=0 |
| 4 | 答掉 `SW/DEMO_OD_PIPELINE_SPEC.md` §7 附录 A 的 **P2-2** (imx415 / ov02b10 的具体文件与适用版本) | ✅ **通过** | 立项书 §7 |
| 5 | 要问模组厂/服务商的问题清单 5~8 条, **只起草不外发** | ✅ **通过** | 本文 §B-问题清单 (8 条) |
| 6 | 分片登记走 `state/frag_write.py` 原子写, **只新增不删改别人 key** | ✅ **通过** | `state/fragments/sw.yaml` (+3 artifacts / +4 needs_from / +3 interface_claims) |
| 7 | `state/merge.py` rc=0 且冲突 0 | ✅ **通过** | 见 §B6 |
| 8 | `state/gate_check.py` Q1 = 18/18 | ✅ **通过** | 见 §B6 |
| 9 | `HW/netlist_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` 一字未动 | ✅ **通过** | 见 §B6 (md5 c78f9912… / 611b869e…) |
| 10 | **板端实测** (真机出图 / 标定 / F1 复测) | ⚠️ **未验** | ★**Radxa 板不可达 ⇒ 板端相关一律 `[0数据]`**; 立项书 §4.2 B-5 的统计脚本**未写** (要板端帧) |
| 11 | **tuning 实际交付** (IQ 文件本体) | ❌ **不通过 (未做, 不在本单范围)** | 本单交的是**立项件**, 不是 tuning 产物; 触发条件见立项书 §5.2 S5 |

---

## B3 证据分级 (本单每个关键数字)

| 数字 | 值 | 等级 | 出处 |
|---|---|---|---|
| rkaiq 快照条目数 | 166 | `[实测]` | `HW/_os_snapshots/rkaiq_iqfiles.json` |
| ar0234 / ov04c10 命中数 | **0 / 0** | `[实测]` | 同上 (`SW/tools/iq_coverage_check.py` J1/J2) |
| ISP 代目录数 | **5** (`isp20/isp21/isp32/isp32_lite/isp3x`) | `[实测]` | 同上 (J3) —— ★**与 `HW/AR0234CS_RK3572_PORT_SPEC.md` 的 "6 个" 不一致 (文中只列 5 个) ⇒ 已点出, 按 5 个记** |
| imx415 / ov02b10 的 isp3x 文件 | 各 1 个 | `[实测·本机既有记录]` | `HW/IMX415_DEMO_SENSOR_FACTS.md §3.1` · `HW/AR0234CS_RK3572_PORT_SPEC.md` |
| imx415 其余 7 个 IQ 在 `isp20/` 且是 xml | 7 | `[实测·本机既有记录]` | 同上 |
| IQ 声明分辨率 (imx415) | **3840×2160** | `[实测·本机既有记录]` | `HW/IMX415_DEMO_SENSOR_FACTS.md §3.2` |
| 路径 B tuning 工作量 | **1~2 人日** | `[推算·既有记录]` | `HW/IMX415_DEMO_SENSOR_FACTS.md §3.3` |
| 路径 A tuning 工作量 | **1~2 人周 (5~10 人日)** | `[推算·既有记录]` | `HW/OPEN_SOURCE_AVAILABILITY.md §3.3` · `HW/AR0234CS_RK3572_PORT_SPEC.md C7` |
| 暗室 / 灰卡 / 标定板 | **本项目无设备与预算** | `[实测]` | `state/BOSS_DECISIONS_20261110.md:44` · `HW/EMC_PRECHECK.md:48` |
| RKISP Tuner 可得性 | 未知 | `[0数据]` | 本机无此工具, 未核其公开性 |
| 标定窗口 (demo / 整机) | 半天~1 天 / 1~2 天 | `[推算·本文推导]` | 本单 |
| 板端一切 (出图 / 标定 / F1) | — | `[0数据]` | Radxa 板不可达 |
| 服务商 / 模组厂报价 | — | `[0数据]` | 本项目无任何报价记录 ⇒ 金额一律待询价后回填 |

---

## B4 接口取值声明 (interface_claims — 已原子写进 `state/fragments/sw.yaml`)

| key | value | note | ref |
|---|---|---|---|
| `iss139_iq_coverage_snapshot` | `ar0234=0,ov04c10=0;有现成IQ:imx415=8(isp3x仅1)/imx327=1/imx464=1/os04a10=8/ov02b10=2(isp3x=1)/gc8034=3/sc200ai=4` | ★2026-11-11 本机快照 166 项实测 (basename 扁平清单 ⇒ 目录上下文已丢 ⇒ 未被既有记录写明目录的一律 [0数据]) | `HW/_os_snapshots/rkaiq_iqfiles.json` + `SW/tools/iq_coverage_check.py` |
| `iss139_tuning_effort_split` | `demo路径B=1~2人日(补1920x1080mesh+AE换算);整机路径A=5~10人日(1~2人周)` | ★demo 段不是 0: 现成 IQ 的 sensor_calib.resolution 锁 3840x2160 + mesh 文件名锁 3840_2160 ⇒ 1080p60 档缺 mesh | `HW/IMX415_DEMO_SENSOR_FACTS.md §3.1~§3.3` · `HW/OPEN_SOURCE_AVAILABILITY.md §3.3` |
| `iss139_tuning_device_window` | `demo=1次样机窗口(灰卡/暗室 半天~1天);整机=1~2天暗室窗口` | ★**占样机档期, 不占投板窗口** (`HW/STEP1_LANDING_LIST.md` F9 = 🔄 待清, "卡出图不卡板") ⇒ 板子回来后档期被占 ⇒ 1~2 人日会滑成 1~2 人周 | 本单 §5.3 |

★**未复用别人已有的 key** (`sensor_isp_tuning_status` / `sensor_isp_iq_available` / `imx415_iq_available` / `rkaiq_isp3x_iq_inventory` 都是 hw-lead 的) ⇒ ★**本单只新增 `iss139_*` 前缀的 3 条, 不改别人的 value** ⇒ merge 冲突 0。

★**needs_from (4 条, 全部给 main)**:
1. `iss139_f9_sample_window` ⇒ ★**把 `HW/STEP1_LANDING_LIST.md` F9 的状态/窗口(半天~1天)/责任人写进落地清单与项目计划表** (★本单不碰 `HW/**`)。
2. `iss139_pipeline_spec_effort_alignment` ⇒ ★**裁决 `SW/DEMO_OD_PIPELINE_SPEC.md` §7.2 ⑨ 行 (路径 B = 0~1 人天 "微调") 与本机既有记录 (1~2 人日 "补 mesh + AE 换算") 的口径差** ⇒ ★建议取 1~2 人日; ★**本单未改该文件** (DSI payload 口径 11-11 刚统一, 不许碰)。
3. `iss139_tisp_timing_point` ⇒ ★**`SW/DEMO_OD_TIMING_SPEC.md` 的 11 段接力表把 `t_capture` 定义为"曝光结束→帧落用户态", ★不含 ISP 算法耗时 ⇒ 建议增补 `t_isp` 打点** (★不改现有 9 个打点名与 CSV 表头); ★**本单未改该文件**。
4. `iss139_od_input_dist_script` ⇒ ★**立项书 §4.2 B 组的输入分布统计脚本还没写** (要板端帧) ⇒ 等板可达后另派, 或授权本单在下轮补。

---

## B5 未决项与卡点

| # | 未决项 | ★卡在谁手上 | 不解决的后果 |
|---|---|---|---|
| 1 | ★**§B-问题清单要不要发、发给谁 (模组厂 / 第三方服务商)** | ★**项目总工 / 老板** (外发一律经项目总工) | ②③ 两条低成本路线的报价与交期拿不到 ⇒ 路线权重只能停在纸面 |
| 2 | ★**暗室外委 + 灰卡/色卡采购预算** (自购小件那一档 ¥800-1500 里的"色卡") | ★**老板批预算** (老板 11-10 未批可靠性场地那一笔 ⇒ 同类先例) | 标定窗口排不进去 ⇒ S3 滑到整机段 ⇒ demo 段那 1~2 人日变成 1~2 人周 |
| 3 | ★**RKISP Tuner 从哪来** (本机没有, 公开性未核) | ★**瑞芯微 / RK3572 模组厂** (经项目总工) | 自研路线 (①) 的前提塌 ⇒ 只能走 ②③ |
| 4 | ★**镜头/模组定版** (整机段硬前置: IQ = sensor×镜头×模组 三者绑定) | ★**老板 / 采购** | 整机段 tuning 无法开始 (不是"慢一点", 是"不能开始") |
| 5 | ★**板子什么时候回 / 调试档期怎么占** | ★**HW (ISS-149/150/158) + 档期** | §4.2 的 B 组分布验收与 §5.2 的 S3 全部无法执行 ⇒ 板端相关全部 `[0数据]` |
| 6 | ★**rkaiq / BSP 版本冻结点** | ★**瑞芯微 / 模组厂** | 版本漂移 ⇒ IQ 可能要重调 (白做一遍) |
| 7 | ★**两处文档口径分歧待 main 裁决** (needs_from 2/3) | ★**main** | 排期账与时序口径继续两套并存 ⇒ 后面谁引用谁都可能引错 |

---

## B6 自证复现命令 (当场可跑)

```bash
cd projects/smart_glasses
python3 SW/tools/iq_coverage_check.py            # 覆盖表 + 16 项判据
python3 SW/tools/iq_coverage_check.py --self-test # 正向 16/16 + 反向 4/4
python3 state/merge.py                            # 状态源合并
python3 state/gate_check.py                       # 质量门 Q1
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
```

★**实测输出 (2026-11-11, 本机)**:

```
$ python3 SW/tools/iq_coverage_check.py
==> 16/16 项通过, 0 项失败
RC=0

$ python3 SW/tools/iq_coverage_check.py --self-test
[selftest] 快照: HW/_os_snapshots/rkaiq_iqfiles.json (166 项)
[selftest] 正向: 16/16 项通过 (期望全过)
[selftest] 反向用例 (期望每个都 '确实变红' —— rc=0 表示反向用例通过):
   [OK] R1 注入 ar0234cs IQ ⇒ J1:ar0234 / J2:ar0234=0 必须红
   [OK] R2 删掉全部 imx415 条目 ⇒ J1:imx415 必须红
   [OK] R3 删掉 isp3x 目录条目 ⇒ J3:isp-gen-dirs 与 J3b:isp3x-present 必须红
   [OK] R4 删掉 'imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json' ⇒ J5:attested-subset 必须红
[selftest] ✔ 正向 16/16 + 反向 4/4 全部通过
RC=0

$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-11T19:18:23+08:00)
   产出 171 | 阻塞 43 (高危 33) | 未闭合需求 100 | 冲突 0 | 健康度 red
MERGE_RC=0            # ★rc=0 且 冲突 0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无
   sw-lead    6/6  缺: 无   交接单: 2026-11-11_sw-lead_ISS191_复位P0方案.md
   mech-lead  6/6  缺: 无
GATE_RC=0            # ★Q1 18/18

$ md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
c78f991283cc82d56c8e3dd31657c785  HW/netlist_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
                                 # ★一字未动 (与基线 c78f9912… / 611b869e… 一致)
```

★**覆盖表要点 (机检输出节选)**: ★**ar0234 / ov04c10 = 无 (0 命中)** · imx415 = 8 个 (isp3x 仅 1 个 `imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json`, 其余 7 个在 isp20 且是 xml) · ov02b10 = 2 个 (`ov02b10_default_default.json` 在 isp3x) · ★**ISP 代目录 = 5 个** (与 `HW/AR0234CS_RK3572_PORT_SPEC.md` 写的 "6 个" 不一致 ⇒ 已点出)。

---

## ★B-问题清单 (给模组厂 / 第三方调像服务商) —— **只起草, 一条都没发; 外发一律经项目总工**

> ★**用法**: 本清单**同时**适用于 ②模组厂随货提供 IQ 与 ③第三方调像服务商两条路线 (方括号里标了问谁)。
> ★**背景给对方的一句话**: 我们是 RK3572 + 外购 camera 模组的一体式 AI 眼镜项目, 走 rkaiq/ISP3 (`isp3x` 代), 需要一份**与我们的 sensor × 镜头 × 模组绑定**的 ISP tuning 文件 (IQ)。

| # | 问题 | 问谁 | ★为什么必须问 (不答的后果) |
|---|---|---|---|
| **Q1** | ★**你们能否随货提供 ISP tuning (IQ) 文件?** 请明确: ①**格式 = rkaiq `iqfiles/isp3x/` 下的 json** (不是 `isp20/` 里的 xml —— 那是 ISP2.0 代, 我们是 ISP3) ②**是否包含 LSC/FEC/LDCH mesh 文件** ③文件名是否按 `<sensor>_<module>_<lens>.json` 命名 | ②模组厂 / ③服务商 | ★本机实测: 公开仓里 imx415 的 8 个 IQ 只有 **1 个在 isp3x**, 其余 7 个都在 **isp20** 且是 xml ⇒ ★**拿到 xml 等于没拿到** |
| **Q2** | ★**这份 IQ 是按哪个分辨率、哪个帧长、哪个曝光表标定的?** 请给: 标定分辨率 (我们走 **1920×1080@60**, binning 模式) · 行时间/帧长 (VMAX) · 曝光表 (`exposure_index`) 的适用帧长 | ②模组厂 / ③服务商 | ★本机实测: 公开的 imx415 IQ 头里 `sensor_calib.resolution` **明写 3840×2160** ⇒ ★**裁到 1080p60 不能直接用**; 且 VMAX 3165→1582 ⇒ **曝光表要重算** |
| **Q3** | ★**IQ 与我们自带的板子 (RK3572 + rkaiq 版本) 怎么对齐?** 请给: 需要的 **rkaiq / BSP 版本** · 是否需要你们出**同版本 rkaiq** · IQ 里的 `sensor` 名字段 (`base.sensor`) 该填什么 (我们驱动侧填 `ar0234cs` / `imx415`) | ②模组厂 / ③服务商 | ★**RK3572 专属 BSP/tuning 不公开** ⇒ 版本/命名对不上 = rkaiq 起不来 (驱动移植 C6 的 A4 判据) |
| **Q4** | ★**标定数据要不要我们提供?** 请明确流程: 我们提供 **均匀光源/灰卡/畸变网格** (或你们提供并指导), 标定当天的**场地、工装、采集方式**, 以及**我们要配合多少人天** | ③服务商 (②模组厂也要问) | ★决定"我们自己要干的量" (= 人天) ⇒ ★**这是本单唯一能把 §1 的 P3/P4/P5 变成确定数的入口** |
| **Q5** | ★**交付物形态与验收方法**: 交付 = ①json IQ ②**对应分辨率的 mesh** ③**曝光表/增益表** ④**标定报告** (含白平衡/色温/暗角/噪点的实测值)? ★**你们怎么判"合格"?** 我们要能复核 | ②模组厂 / ③服务商 | ★**没有验收方法 = 交了就信** ⇒ 我们要按 §4 的口径复核, ★不能拿"对方说合格"当验收 |
| **Q6** | ★**交期与工程支持窗口**: 交付需要多久? ★**标定/联调期间出问题, 谁响应、多快?** (我们板子回板后的调试档期是硬的) | ②模组厂 / ③服务商 | ★**联调期一旦没人响应, 样机窗口就白占** ⇒ 我们的样机档期是有限资源 |
| **Q7** | ★**费用与授权**: ①报价 (一次性? 每模组? 每批次?) ②★**IQ 文件的使用授权与归属** (能不能随我们的量产产品发布? 能不能给第三方代工厂?) ③是否与**起订量**挂钩 | ②模组厂 / ③服务商 | ★本项目**没有任何服务商报价记录** ⇒ ★**金额一律 `[0数据]`, 必须问出来**; ★授权归属影响量产, ★**不能等量产前才发现 IQ 不能随产品走** |
| **Q8** | ★**如果你们不给 IQ, 是否支持"我们自己做 + 你们支持"**? 具体: ①**RKISP Tuner 怎么获得** ②有没有**标定流程文档 / 培训 / 远程支持** ③能否**按我们自己的板子** (RK3572 + 我们的鱼眼镜头) 出方案 | ③服务商 / ②模组厂 | ★**兜底问题**: 万一②③都不成, ★**自研路线 (①) 的前提就落在"工具从哪来"** ⇒ ★**这条必须问, 否则自研路线是空中楼阁** |

★**已存在的相关草稿 (不重复)**: `state/outbox/onsemi_ar0234cs_query.md` (ISS-142, ★**未发**) 的第 ⑤ 条已经问过 onsemi "有没有现成 IQ 给 Rockchip ISP3" ⇒ ★**本清单是它的补集与加强版** (那份只问"有没有", ★本清单问的是"是什么格式/什么分辨率/怎么验收/多少钱/谁响应") ⇒ ★**建议 main 把两份合并后再发**。

---

## 边界声明 (本单没做、也不该由我做的事)

- ★**未联网** (未重抓 rkaiq / GitHub) ⇒ 版本信息只取**本机既有实测记录**, 其余 `[0数据]`。
- ★**未联系任何供应商 / 原厂 / 服务商** —— §B 清单**只起草**; ★**外发一律经项目总工**。
- ★**未改任何既有文件** —— 含 ★**`SW/DEMO_OD_PIPELINE_SPEC.md`** · ★**全部 `HW/**`** (含 F9) · `state/issue_log.yaml` (改 issue 状态是 main 的活) · ★**别人的分片**。
- ★**未写板端代码、未跑板端** ⇒ 板端一律 `[0数据]`。
- ★**未替老板拍板** —— §2 只给三份可比较的账 + 建议权重; ★**§B-问题清单的发送与否由项目总工/老板定**。
