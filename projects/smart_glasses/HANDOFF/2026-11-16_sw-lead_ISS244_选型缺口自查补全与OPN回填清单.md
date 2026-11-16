# ISS-244 交卷单 · ISS-241 选型缺口 G-1~G-10 逐条自查补全 + 22 件 OPN 回填清单

> 作者: sw-lead (软件总工) · 2026-11-16 · 交卷给 main / 项目总工
> 上游: `HW/PART_SELECTION_MATRIX_2026-11-16.md` (ISS-241 矩阵, 本单**只引用不改**) · `HW/check_part_selection_matrix.py` (ISS-241 门禁, 本单**只读不改**)
> ★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) · ★**实物 [实测] = 0 条** (本机无板)
> ★**本单不改网表 / 脚表 / BOM 一个字 · 不碰 PCB 布线 / 布局 / 板框 · 不改 ISS-241 矩阵正文与门禁 · 不替老板拍板 · `state/issue_log.yaml` 不自改**

---

## B1 结论摘要 (给 main / 项目总工看这一段就够)

★**一句话**: ISS-241 登记的 10 条选型缺口 **本轮逐条自查完毕** —— 4 条重点缺口 (G-5 / G-3+G-4 / G-10 / G-1) 从「描述性缺口」升级成 **带官方出处 + 可复跑算式 + 可量化代价** 的条目; 其余 6 条写成「已转单 / 已闭合 + 出处」不重复论证; 另交 **22 件 OPN 回填清单** (只出清单, **一字未落表**)。

★**本轮拿到的四个新结论** (全部只出依据 + 代价, **一条未代拍**):

| 缺口 | 本轮结论 | 证据等级 |
|---|---|---|
| **G-5** LED 亮度账不匹配 | ★**1 mA 工作点的 LED 亮度只有 20 mA 标称值的 4.8%~7.2% = 暗 14~21 倍** (Kingbright 厂商 PDF 的 Iv-vs-If 归一化曲线数字化, **四颗料互相印证**: 5.10 / 5.10 / 4.77 / 5.24 / 7.19 %) ⇒ 红 ≈ 11 mcd typ / 绿 ≈ 0.7~0.9 mcd typ / 充电灯 ≈ 5.5 mcd typ。电流账比 ISS-241 写的更宽: 1 kΩ @3.3 V ⇒ 红 1.35 mA / 绿 1.10 mA / Vf 取 2.5 V max 时只剩 **0.80 mA** | [官网]+[推算] |
| **G-3 + G-4** 高速差分对单边 ESD | ★**业界通行 = 差分对正负两根都要护 + 紧贴连接器** (TI `SLVAF82B` 原文「the diodes are connected to **each data line**」+「place the diodes **as close to the source of ESD**, in this case the connector」; Würth `ANP002` Fig.9/11: 单通道器件也是 D+/D− 各一颗)。本板实测: CSI-2 的 5 对差分共 10 条线里 **9 条裸奔**, USB **D− 裸奔**。★**代价不在结电容**: USB 2.0 判据 Cd<4 pF ⇒ 双通道 `TPD2E2U06` 1.5 pF typ / 1.9 pF max 达标 ⇒ 代价 = 焊盘 +1 / +4 与面积 (×15) | [官网]+[实测] |
| **G-1** Q_PG 源漏拓扑 | ★**两种写法的电学后果都算出来了**: 写法A (S=BAT_SW / D=ON / G=PG) ⇒ PG 低 VGS = **−4.2 V** 导通 (|VGS(th)max| 2.4 V) / PG 高 VGS = **−0.9 V** 关断 (|VGS(th)min| 1.4 V) ⇒ **逻辑自洽**; 写法B (网表 note 首句直译 S=ON / D=BAT_SW) ⇒ 上电 ON 被 10 kΩ 下拉到 0 V ⇒ VGS = **0 V** 不导通, PG 高时 VGS = **+3.3 V** 反向偏置 ⇒ **PG 高低都关 ⇒ 开机路径彻底不通** ⇒ **note 首句与 note 正文自述的「正解」互斥, 首句必须改**。连带: 写法A 需要器件引脚序 = **D-S-G**, 而 SOT-23 库标准序是 **G/S/D** ⇒ 要么选 D-S-G 序器件, 要么重画 land | [官网]+[实测] |
| **G-10** 分压最终阻值 | ★**官方公式与三档候选表都做出来了**: TI `TPS3808G01` §7.3.1 + Figure 7-1 ⇒ **V_IT = (1 + R1/R2) × 0.405 V**, **R1 + R2 = 4 MΩ** ⇒ 轨 3.3 V ⇒ 3.480 M / 549 k (触发 2.9722 V); 轨 1.8 V ⇒ 3.010 M / 1.000 M (1.6240 V); 轨 1.2 V ⇒ 2.490 M / 1.500 M (1.0773 V), 各带误差带。★**但真正的阻塞不是阻值算不出**: `U_SUPV` 三行 **DNP** 且产生被监控轨的 `U_DCDC_VIO` 也 **DNP** ⇒ **分压两臂装上只会把 RAIL_V_SOC_IO 短路到地** ⇒ 建议 **两臂随 U_SUPV 一并置 DNP** | [官网]+[推算] |

★**★一个必须让 main 知道的并发事实**: 本单生成期间 (**2026-11-16 15:45:45 实测**) `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` **被另一个落表批次改过** ⇒ `C_REGN` 的 BOM value 已从「[待选型] 1µF」变成「4.7 µF ±10% (10 V)」且 opn 已填 ⇒ **G-6 当场闭合**, 该件不再进落表批次。
⇒ 本单的件数控写成**双源**: **登记范围 = 22** (ISS-241 矩阵基准块的 `expected_refs`, 登记事实) / **当前待落 = 21** (BOM 实跑, 盘上事实), 两个数都注明来源与时点。
⇒ ★**本单门禁的 C5 就是按这个口径写的**: 登记范围内的一件被并发落掉而又不写落表证据 ⇒ **红** (锚点过期 ⇒ 红 ⇒ 走 H-1 重锚 + 留痕, **不许把红灯调没**)。**本轮实测确实红了一次** (见 B5 备注)。

★**留 main / 老板拍 6 项 (本单一条未代拍)**: ① V-2 ESD 方案二选一 ② V-3 ③ V-4 ④ G-1 源漏写法 ⑤ G-10 要不要恢复独立欠压监督 ⑥ LED 亮度档。

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 | 判定 | 依据 |
|---|---|---|---|
| A1 | 新建收口页 `HW/PART_SELECTION_GAPS_CLOSEOUT.md`, 一张表每条缺口一行, 列 = 缺口/归谁/本轮自查结果/证据等级/出处/降级方案/还差什么/状态 | ✅ 通过 | 收口页 §2, 10 行 × 8 栏齐全 |
| A2 | G-1~G-10 **十条全部**在收口页出现, 一条不许漏 | ✅ 通过 | 门禁 C1 (机器判) |
| A3 | 每条必须带 **状态 + 证据等级 + 出处 + 降级方案** 四栏, 任一栏空 = 红 | ✅ 通过 | 门禁 C2 (机器判) |
| A4 | 证据等级只能是 `[官网]/[实测]/[媒体]/[推算]/[0数据]` 白名单 | ✅ 通过 | 门禁 C3 (机器判); 反向用例 M3 (写 `[官方]` ⇒ 红) |
| A5 | 不许出现「等回复 / 等原厂回信 / 待供应商确认」这类挂起措辞 | ✅ 通过 | 门禁 C4 (机器判); 反向用例 M4 |
| A6 | OPN 回填清单 22 件全在 (BOM 待选型∩必装 − U_PWR_SW, **自己跑 csv 统计**) | ✅ 通过 (双源口径) | 门禁 C5; §7 件数统计: 登记范围 22 / 当前待落 21 / 已被并发落掉 C_REGN |
| A7 | 清单每行必须带非空的「落表锚点」 | ✅ 通过 | 门禁 C6; 反向用例 M6 |
| A8 | 每条缺口必须**真查**, 不许把 ISS-241 原文抄一遍交差 | ✅ 通过 | §3 四条重点缺口各有独立的新查证 (厂商 PDF 数字化 / 官方 app note / 电学推演 / 官方公式反推) |
| A9 | G-5 的 PDF 与数字化脚本必须**落盘**, 出处可复核 | ✅ 通过 | `state/.cache_iss244/led/` 5 份原厂 PDF + `extract_ivif.py` + 5 份 `ivif_*.json`; `--selftest` 2/2 |
| A10 | 四条重点缺口只出依据 + 代价, **不代拍** | ✅ 通过 | 收口页 §2 状态列全部写「需老板拍」; 本单无任何一条被代决 |
| A11 | 独立机器门禁 ≥ 6 条断言, `--selftest` ≥ 5 条反向用例, 每条自证「真的改到了目标」 | ✅ 通过 (7 条断言 / 8 条反向用例) | 门禁 C0~C6 + M1~M8, 每条自证三件事: 变异落到副本 / 目标那条变红 / 其余仍绿 |
| A12 | 验收命令全 rc=0: ISS-241 门禁 + `--selftest` + merge/gate_check + 本单门禁 + `--selftest` | ✅ 通过 | B5 原样输出 (全 rc=0) |
| A13 | 零外发 | ✅ 通过 | 全部资料来自 web_search / web_fetch / 带 `--max-time` 的 curl + `pdftotext` 实读 |
| A14 | 不改网表 / 脚表 / BOM / 板 / ISS-241 矩阵与门禁 | ✅ 通过 | B6 边界审计 (含并发落表的归属说明) |
| A15 | 落表锚点不写死行号 | ✅ 通过 | 锚点 = `ref + net` + 当刻行号, 并注明「行号会随落表漂移」 |
| A16 | 实物 `[实测]` = 0 条 | ✅ 通过 | 本机无板; 所有 `[实测]` 都是**文件 / 网表 / 板文件实读**与**脚本实跑** |
| A17 | 分片必须走 `state/frag_write.py` 原子写, 不许手改 yaml | ✅ 通过 | 全部增量走 `state/frag_write.py`; 一次就地订正走 `frag_write.update_fragment` (同一原子写路径) |
| A18 | `state/issue_log.yaml` 不自改 (verify 留给 main) | ✅ 通过 | 本单零写入 |

**自评结论: 18/18 全部通过。**

---

## B3 证据分级 (实测 / 官方 / 推算 / 0数据)

| 级别 | 本单条目 | 说明 |
|---|---|---|
| **[官网]** | G-1 (AO3407A + DMP3098L 原厂手册) · G-3 / G-4 (TI `SLVAF82B` + Würth `ANP002` + TI `TPD2E2U06` / `TPDxE05U06`) · G-5 (Kingbright 5 份原厂数据手册) · G-10 (TI `TPS3808` SBVS050N Rev. N) · G-6 (TI BQ25896 SLUSC76C pin22, 引自 ISS-241) | 厂商/半导体公司官方文档原件, 全部落盘可 `pdftotext` 复核 |
| **[实测]** | G-2 / G-7 / G-8 (板文件与 BOM 实读) · G-3 / G-4 的「只护一边」事实 (网表实读) · G-5 的 1 kΩ 事实 (网表实读) · G-9 (csv 实跑) · G-10 的 dnp 事实 (网表实读) · OPN 清单的 22 行锚点 (网表/脚表/BOM 现算) | ★**本机无板 ⇒ 这里的「实测」= 文件/网表/板文件实读 + 脚本实跑, 不是实物测量**; 实物 `[实测]` = **0 条** |
| **[推算]** | G-5 的绝对亮度 (mcd) 与电流 · G-10 的 E96 候选阻值与误差带 · G-1 的 VGS 极性推演 | 算式/脚本可复跑 (`supv_divider_solve.py`, `extract_ivif.py`) |
| **[0数据]** | `KP-2012SGC` 自身曲线 (其 V.18B 数据手册的曲线是**位图**, 文本层抓不到 ⇒ 绿灯的 1 mA 档用同厂同尺寸绿 `AP2012CGCK` 的曲线做**代理**并已写明) · D-S-G 引脚序的 P-MOS 在售件 (G-1 降级①) · 双通道低容值件的非 TI 厂家数据 (G-4 降级③) · `TPS3808G01` 的轨标称 (TBD-02 三选一未定) | 每条 [0数据] 都配了降级方案, **没有一条挂成「等回复」** |
| **[媒体]** | 本单 **0 条** | 未采用媒体二手转述作结论 |

**★未采用的做法 (自证)**: 凡是要数字的地方, 一律回到厂商 PDF 文本层 / 网表原文 / 脚本实跑, 没有一处用「业内一般认为」填空。

---

## B4 接口取值声明 (interface_claims)

本单登记 5 条 interface_claim + 1 条 answer (全部走 `state/frag_write.py`, 只写 sw-lead 自己的分片):

| key | value | 落点 |
|---|---|---|
| `iss244_g5_led_brightness_1ma` | 1 mA 工作点只有 20 mA 标称亮度的 4.8%~7.2% (暗 14~21 倍); 红 AA1608SURSK ≈11 mcd typ @1.35 mA / 绿 KP-2012SGC ≈0.7~0.9 mcd typ @1.10 mA / 充电灯 APT1608SURCK ≈5.5 mcd typ | 收口页 §3.1 |
| `iss244_g1_qpg_vgs_truth` | 写法A (S=BAT_SW/D=ON/G=PG) 逻辑自洽; 写法B (note 首句直译) ⇒ VGS=0 V 不导通 + PG 高 VGS=+3.3 V 反向偏置 ⇒ 开机路径彻底不通 | 收口页 §3.3 |
| `iss244_g10_supv_divider_official` | V_IT=(1+R1/R2)×0.405 V, R1+R2=4 MΩ + 三档 E96 候选阻值与误差带 | 收口页 §3.4 |
| `iss244_g3g4_esd_single_sided_basis` | 差分对正负两根都要护 + 紧贴连接器; USB 2.0 Cd<4 pF 判据; 本板 CSI-2 十条线里九条裸奔 / USB D− 裸奔 | 收口页 §3.2 |
| `iss244_opn_backfill_22_rows` | 登记范围 22 / 当前待落 21 / C_REGN 已被并发落掉; 每行带 ref+net 锚点 + land 要不要改 + 谁拍 + 状态 | 收口页 §4 |
| answer `iss244_gaps_closeout` → main | 本单交卷摘要 + 6 项待拍 + 「请落 verified」请求 | 本交卷单 |

★**跨域一致性**: 本单**没有新增任何与别人同 key 的 claim** ⇒ merge.py 的 interface_claims 冲突检测**零新增冲突** (merge rc=0)。

---

## B5 验收命令实跑输出 (原样, 不剪)

> 复现脚本: `bash state/.cache_iss244/run_acceptance.sh` (原始输出同时落盘在 `state/.cache_iss244/acceptance_output.txt`)

```text
### ① ISS-241 门禁 (上游, 本单不许把它改红)
[check_part_selection_matrix] 门禁检查: HW/PART_SELECTION_MATRIX_2026-11-16.md
  [PASS] C0 — 基准块 JSON 解析通过
  [PASS] C1 — 覆盖 22/22 位号 (含任务书枚举的 20 个全齐)
  [PASS] C2 — 候选完整性: 每件 ≥2 候选且各栏非空
  [PASS] C3 — 封装兼容性: 每件有结论+理由+pads_required
  [PASS] C4 — 证据/降级/推荐: 每件齐全
  [PASS] C5 — 证据等级白名单: 全部合法
  [PASS] C6 — 空话检查: 无空候选/无已定型式空话
  [PASS] C7 — 无越界位号 (OUT_OF_SCOPE ['U_EN_SW', 'U_PWR_SW'] 全部不在册)
[check_part_selection_matrix] PASS — 选型证据矩阵门禁全过 (8/8)
rc=0

### ①b ISS-241 门禁 --selftest
[PASS] M1 删掉一个位号 (Q_PG) — C1 变红 (共 2 条: C1,C7) [落盘回读复核同红]
[PASS] M2 把某件候选清空 (AO3400A 的 pn) — C2 变红 (共 2 条: C2,C6) [落盘回读复核同红]
[PASS] M3 把某件降级方案删空 (D_ESD_USB_D) — C4 变红 (共 1 条: C4) [落盘回读复核同红]
[PASS] M4 塞一个越界位号 (U_PWR_SW) — C7 变红 (共 2 条: C1,C7) [落盘回读复核同红]
[PASS] M5 证据等级写成非法词 [官方] — C5 变红 (共 1 条: C5) [落盘回读复核同红]
[PASS] M6 删掉封装兼容性结论 (Q_ENVC) — C3 变红 (共 1 条: C3) [落盘回读复核同红]
[PASS] M7 把推荐项 why 清空 (Q_PG) — C4 变红 (共 1 条: C4) [落盘回读复核同红]
[PASS] M8 破坏 baseline JSON — C0 变红 (共 1 条: C0) [落盘回读复核同红]
[PASS] M9 把某件候选降到 1 个 (Q_AND) — C2 变红 (共 1 条: C2) [落盘回读复核同红]
selftest: 9/9
[check_part_selection_matrix] PASS — 反向用例 9/9 全抓到
rc=0

### ② merge + gate_check (Q1)
merge rc=0
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-16_hw-lead_ISS242_网表板第3轮自相矛盾3条.md   ★按 2026-11-16_hw-lead_ISS242_网表板第3轮自相矛盾3条.md 计分 (最新一份 2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md 缺 ['B1', 'B2', 'B4', 'B5'])
   sw-lead    6/6  缺: 无   交接单: 2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
gate rc=0

### ③ 本单门禁
=== ISS-244 选型缺口自查补全 + OPN 回填清单 · 机器门禁 ===
OPN 清单应覆盖件数 (ISS-241 登记范围, 从矩阵基准块读) = 22
其中当前仍待落 (HW/BOM_v1.csv 实跑 待选型∩必装 − 越界件) = 21
[PASS] C0
[PASS] C1
[PASS] C2
[PASS] C3
[PASS] C4
[PASS] C5
[PASS] C6
--- 7/7 PASS ---
rc=0

### ④ 本单门禁 --selftest
[PASS] M1 删掉一条缺口 (G-7) → 期望 C1 红
      变异落地(探针 'G-7' 在副本里)=True · 目标 C1 变红=True · 其余 check 仍绿=True
[PASS] M2 某条缺口降级方案清空 → 期望 C2 红
      变异落地(探针 'G-3' 在副本里)=True · 目标 C2 变红=True · 其余 check 仍绿=True
[PASS] M3 证据等级写成 [官方] → 期望 C3 红
      变异落地(探针 '[官方]' 在副本里)=True · 目标 C3 变红=True · 其余 check 仍绿=True
[PASS] M5 清单里删一件 (D_ESD_CAM) → 期望 C5 红
      变异落地(探针 'D_ESD_CAM' 在副本里)=True · 目标 C5 变红=True · 其余 check 仍绿=True
[PASS] M6 某行落表锚点清空 → 期望 C6 红
      变异落地(探针 'Q_PG' 在副本里)=True · 目标 C6 变红=True · 其余 check 仍绿=True
[PASS] M8 已被别的批次落掉的件清空 landed_note → 期望 C5 红
      变异落地(探针 'C_REGN' 在副本里)=True · 目标 C5 变红=True · 其余 check 仍绿=True
[PASS] M4 正文塞一句挂起措辞 → 期望 C4 红
      变异落地(探针 '等原厂回信' 在副本里)=True · 目标 C4 变红=True · 其余 check 仍绿=True
[PASS] M7 破坏基准块 JSON → 期望 C0 红 (且 C1~C6 一致地红 = fail-closed)
      变异落地=True · 目标 C0 变红=True · 其余 check 一致地红(fail-closed)=True
--- SELFTEST 8/8 ---
rc=0

### ⑤ LED 曲线数字化自证 (--selftest)
[PASS] led_aa1608sursk.pdf p3  自证 S1/S2/S3 = [True, True, True]
      If=1.0   mA -> Iv_norm=0.051
      If=1.1   mA -> Iv_norm=0.0563
      If=1.2   mA -> Iv_norm=0.0616
      If=1.3   mA -> Iv_norm=0.0668
      If=1.5   mA -> Iv_norm=0.0774
      If=2.0   mA -> Iv_norm=0.0969
      迹线覆盖 If = [0.384, 30.016] mA, 内点占比 0.6188
[PASS] led_aph1608surck.pdf p3  自证 S1/S2/S3 = [True, True, True]
      If=1.0   mA -> Iv_norm=0.0477
      If=1.1   mA -> Iv_norm=0.053
      If=1.2   mA -> Iv_norm=0.0582
      If=1.3   mA -> Iv_norm=0.0635
      If=1.5   mA -> Iv_norm=0.074
      If=2.0   mA -> Iv_norm=0.1003
      迹线覆盖 If = [0.32, 30.08] mA, 内点占比 0.6282
--- SELFTEST 2/2 ---
rc=0

### ⑥ G-10 分压候选表
=== ISS-244 G-10 · TPS3808G01 分压候选 (公式: V_IT = (1 + R1/R2) x 0.405V, R1+R2 = 4MΩ) ===
窗口假设: 触发点 = 轨标称 x 90% (轨电压跌 -10% 报欠压); 电阻 1%; 阈值精度 typ ±1.5% / max ±3.5%; 迟滞 1.5%

轨标称    V_IT     R1(上)       R2(下)       E96 R1    E96 R2    E96后V_IT  误差带
-------------------------------------------------------------------------------
3.3    2.970    3454545     545455      3.480M    549k      2.9722    2.8108~3.1378 V
1.8    1.620    3000000     1000000     3.010M    1.000M    1.6240    1.5359~1.7145 V
1.2    1.080    2500000     1500000     2.490M    1.500M    1.0773    1.0188~1.1373 V

★ 结论口径 (只出依据, 不代拍):
  ① 公式与元件约束全部来自 TI 官方手册 (§7.3.1 + Figure 7-1), 可复核;
  ② 三个候选值对应网表 L84 原文的三个候选轨电压 (3.3 / 1.8 / 1.2 V);
rc=0

### ⑦ 件数双源统计
ISS-241 登记范围 = 22
当前仍待落 = 21
已被并发落表落掉 = ['C_REGN']

### ⑧ 受保护文件 md5 (交卷前后逐字节未变)
611c3ba3db3dc7de7213063375b96d01  HW/netlist_v1.csv
ef436a37412ac9b6eac3c9f41f1edca4  HW/netlist_v1_pins.csv
2a7305741134788dfee9f13f34c656b4  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
da609d7d1844617cdb1e4f425b8b052c  HW/PART_SELECTION_MATRIX_2026-11-16.md
fb286e5f4834fcda045bf8e7bcfecfdf  HW/check_part_selection_matrix.py
```

★**关于 ⑧ 的诚实说明 (不粉饰)**: 板 `611b869e…` 与 `.kicad_pro` `3e504d2b…` 与项目台账里记录的基线**逐字节一致** ⇒ 板侧零改动 ✔; ISS-241 矩阵与门禁脚本是本单开工时的值 ⇒ 零改动 ✔。
★**网表 / 脚表 / BOM 的 md5 与 ISS-235 记录的基线 (`34132f7e…` / `b21b743a…` / `c195a117…`) 不同** —— ★**这不是本单改的**: 三个文件的 mtime 都是 **2026-11-16 15:45:45** (早于本单最后一次生成), 改动内容是 `C_REGN` 的 BOM value/opn 与 `U_SUPV` 相关的落表内容, 与 **ISS-243「C_REGN 官方值落表」批次**完全吻合 ⇒ **归属另一个并发落表批次**。本单对这三个文件**全程只读** (`build_closout.py` 只写收口页; 门禁脚本只读 + selftest 只在内存副本上变异)。

★**本轮门禁确实红过一次 (如实记)**: 并发落表 (15:45:45) 发生后, 本单门禁的 C5 立刻变红 (「OPN 回填清单出现越界件 C_REGN」+「件数 = 22 (BOM 实跑应为 21)」) ⇒ ⇒ 按 **ISS-225 的 H-1 重锚纪律**处理: 把 C5 改成**双源判定** (登记范围 + 当前待落), 清单保留 `C_REGN` 行并写 `landed_note` 落表证据, 同时更新 G-6/G-9 的正文与分片里的口径 ⇒ **重跑后 7/7 绿**。★**没有把红灯调没, 是把判据改成双源并留痕**。

---

## B6 边界自证 + 留给 main 的待拍项

### B6.1 边界逐条自证

| 边界 | 自证方式 | 结果 |
|---|---|---|
| **零外发** | 全部资料来自 `web_search` / `web_fetch` / 带 `--max-time` 的 `curl` + `pdftotext` 实读; **未发任何邮件 / 询价 / 问询 / 采购** | ✔ |
| **不改网表 / 脚表 / BOM** | 本单只读; 落表清单只给 `ref+net` 锚点 | ✔ (并发落表的改动归属见 B5 说明) |
| **不改 ISS-241 矩阵正文与门禁脚本** | 两个文件只读; md5 = `da609d7d…` / `fb286e5f…` | ✔ |
| **不碰 PCB 布线 / 布局 / 板框** | 板文件零写入; 板 md5 = `611b869e…` (与项目台账基线一致) | ✔ |
| **不写别的 agent 的分片** | 只写 `state/fragments/sw.yaml` (sw-lead 自己的), 全程走 `state/frag_write.py` 原子写 | ✔ |
| **不替老板拍板** | V-2 / V-3 / V-4 / G-1 / G-10 / LED 亮度档 全部只出依据 + 代价; 收口页状态列写「需老板拍」 | ✔ |
| **实物 [实测] = 0 条** | 本机无板; `[实测]` 全部是文件/网表/板文件实读与脚本实跑 | ✔ |
| **`state/issue_log.yaml` 不自改** | 零写入 ⇒ verify 留给 main | ✔ |
| **不改 `PROJECT_TRACKER.md` §0** | 零写入 | ✔ |

### B6.2 留给 main / 老板的待拍项 (本单一条未代拍)

| # | 待拍项 | 本单给的依据 | 代价 | 建议归口 |
|---|---|---|---|---|
| **P1** | **V-2 ESD 方案二选一**: 保持单边 / 改板加双边 (USB 用双通道件, CSI-2 用 6 通道件) | TI `SLVAF82B` §3.2/§4 + Würth `ANP002` Fig.9/11 + 本板实测 9 条 CSI 线与 D− 裸奔 | 单边 = 一次 ESD 就可能打死相机链路或唯一的刷写口; 双边 = 焊盘 +1/+4 与面积 ×15 (结电容不涨) | PM → 老板 |
| **P2** | **V-3** | (ISS-241 登记的 V-3 项, 本单未新增依据) | — | PM → 老板 |
| **P3** | **V-4** | (ISS-241 登记的 V-4 项, 本单未新增依据) | — | PM → 老板 |
| **P4** | **G-1 源漏写法**: 写法A (S=BAT_SW) 还是写法B (note 首句直译) | 两份原厂手册的 VGS 极性/阈值 + 两种写法的电学推演 | 写法B ⇒ 开机路径彻底不通 (PG 高低都关) ⇒ 板装出来开不了机; 写法A ⇒ 需 D-S-G 引脚序器件或重画 land | main / PM |
| **P5** | **G-10 要不要恢复独立欠压监督** | TI `TPS3808G01` 官方公式 + 三档 E96 候选阻值与误差带 | 不恢复 ⇒ 两臂随 U_SUPV 一并 DNP (零改动, 顺带解掉 ISS-190 的短路风险, 代价 = 放弃主板侧独立欠压监督); 恢复 ⇒ 轨标称 (TBD-02) 必须先定 + 加 U_SUPV 器件行 + 误差带要并进欠压策略 | main / PM |
| **P6** | **LED 亮度档**: 接受暗 (降级①) / 改 R 到 20 mA 档 (降级②) / PWM 调光 (降级③) | 厂商曲线数字化 (四颗料互证) + 电流账 | ① = 指示灯白天看不见; ② = 红 68 Ω / 绿 55 Ω + 功耗 2.2 mW→66 mW (两颗 ≈0.13 W 进电池账) + 亮度 ×14 ⇒ **眼旁光源的 IEC 62471 分级要重算**; ③ = 硬件改动 + 与 60 fps 帧预算耦合 (属 SW 侧) | PM / 结构 → 老板 |

### B6.3 请 main 做的三件事

1. **落 verified**: `state/issue_log.yaml` 的 ISS-244 请 main 落账 (本单**不自签**)。
2. **排落表批次**: 收口页 §4 的 22 行清单 (其中 21 行待落, `C_REGN` 行已被并发落掉) ⇒ 请并进落表器或另起一个落表批次; ★**落表时以 `ref + net` 锚点定位, 行号会随落表漂移**。
3. **把 P1~P6 并进 `DECISION_PENDING_2026-11-16.md`** ⇒ 尤其 **P4 (G-1)** 与 **P1 (V-2)**, 这两条直接影响首台板能不能开起来。

### B6.4 本单改了什么 (清单)

| # | 文件 | 动作 |
|---|---|---|
| 1 | `HW/PART_SELECTION_GAPS_CLOSEOUT.md` | ★**新建** (收口页: §0~§8, 含 10 行缺口表 + 22 行 OPN 清单 + 出处表 S1~S12 + 复现命令 + 机器可读基准块) |
| 2 | `HW/check_part_selection_gaps.py` | ★**新建** (C0~C6 六条断言 + `--selftest` 八条反向用例) |
| 3 | `state/.cache_iss244/` | ★**新建** (证据落盘: 5 份 Kingbright PDF + 2 份 TI ESD PDF + TI TPS3808 PDF + AO3407A/DMP3098L PDF + 数字化脚本 + 分压算式脚本 + 收口页生成器 + 验收脚本 + 本次输出) |
| 4 | `HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md` | ★**新建** (本文件) |
| 5 | `state/fragments/sw.yaml` | 只加 3 条 artifact + 5 条 interface_claim + 1 条 answer; 一次就地订正 (并发落表导致的口径变陈旧) —— 全部走 `state/frag_write.py` 原子写 |

★**没有改**: 网表 / 脚表 / BOM / 板 / `.kicad_pro` / ISS-241 矩阵与门禁 / `PROJECT_TRACKER.md` / `state/issue_log.yaml` / 别的 agent 的分片。


---

## §7 ★第 2 轮 (2026-11-17 05:0x) · 落表后回归 + H-1 重锚第 1 跳

> ★**追加式**: 第 1 轮 (2026-11-16 15:59) 的 B1~B6 **一个字没删、没改**; 本节是第 2 轮的增量。

### §7.1 触发原因 (为什么这一轮存在)

- 第 1 轮交卷后, **板侧又落了一批选型件**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 的落盘时刻 = **2026-11-16 22:25:14** (第 1 轮那批是 15:45) ⇒ ISS-241 登记范围 **22 件**里 **14 件已落表 / 8 件仍待落** (第 1 轮是 1 件已落 / 21 件待落)。
- ⇒ 本单门禁 **C5 按设计变红** (14 件「不在 BOM 待选型集合但清单没写 landed_note」) ⇒ ★**这是锚点过期, 不是红灯被调没** ⇒ 走 **H-1 重锚第 1 跳**: 重算 `landed_note` + 重判十条缺口的盘上状态 + 留痕。
- ★**开跑前的实测** (2026-11-17 05:0x): `python3 HW/check_part_selection_gaps.py` ⇒ **rc=1, 6/7 PASS, C5 红 14 条** ⇒ 这是本轮开工时盘上的真实状态, 不是推测。

### §7.2 本轮做了什么 (三件新的实质活)

1. **落表后回归** (新增 `state/.cache_iss244/post_landing.py`, 只读) ⇒ 把「**板占位 land (pad→net)** ↔ **落地器件引脚序** ↔ **网表 note 定的端子角色**」三方逐件交叉核对。
   ★**这是第 1 轮问不出来的问题**: 第 1 轮时料还没落, 只能问「land 几何对不对」; 料落了之后才第一次能问「★装上去引脚还对不对得上★」⇒ **查出 3 条实物级 P0**。
2. **十条缺口按盘上真值重判** (收口页 §5.3) ⇒ G-4 / G-10 从「还没选的缺口」变成「**已落地的装机缺口**」; G-6 闭合; G-1 从「note 措辞矛盾」升级成「实物级 P0」。
3. **门禁加 C7 + 两条新反向用例** ⇒ 把落表后回归表**锁进机器门禁** (每件已落表的件都必须有一行 + 判定 + 出处 + 有引脚序不符就必须有修法) ⇒ 防止这一节以后被人悄悄删掉。

### §7.3 ★三条 P0 (板那一趟必须同批改, 否则板子出来就是坏的)

| # | 位号 | 事实 (逐条实读) | 后果 | ★最小修法★ | 归谁 |
|---|---|---|---|---|---|
| **P0-a** | `Q_PG` | ① 网表 L58/L59/L60 note 定的角色 = **S=ON / D=BAT_SW / G=PG** ⇒ 这是 ISS-244 §3.3 的**写法B**: 上电 ON 被 10 kΩ 拉到 0 V ⇒ Vgs=0 ⇒ 不导通; PG 高时 Vgs=+3.3 V 反向偏置 ⇒ **开机路径彻底不通** ② 落地件 `DMP3098L` 引脚序 = **1=G / 2=S / 3=D** ③ 占位 land = pad1=PWR_ON / pad2=BAT_SW / pad3=PWR_GOOD | 首台板**开不了机** (插电也不开) | ★**写法A (S=BAT_SW / D=ON / G=PG) 是唯一电学自洽的一套** ⇒ land 目标 = **pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D)** ⇒ **只需把两个外侧 pad 对调, pad2 不动** + 网表 note 角色措辞同批改成写法A | 落表批次 (note) + hw-lead (land) + PM/老板 (写法拍板) |
| **P0-b** | `Q_AND` | ① 网表 note 角色**是对的** (D=RESET_N / S=GND / G=PG_AND) ② 落地件 `AO3400A` 引脚序 = **1=G / 2=S / 3=D** ③ 占位 land = pad1=RESET_N / pad2=GND / pad3=PG_AND ⇒ 装上去 = **栅极接 RESET_N、漏极接 PG_AND** | 复位链的**硬件 AND 门不成立** (PG_AND 灌进漏极, RESET_N 接栅极) | land 目标 = **pad1=PG_AND(G) / pad2=GND(S) / pad3=RESET_N(D)** ⇒ 同样**两个外侧 pad 对调** | hw-lead (land) |
| **P0-c** | `D_ESD_CAM` | ① 落地件 `TPD1E05U06DPYR`: TI `SLVSBO7O` Table 4-1 原文 **pin1=I/O / pin2=GND** ② 占位 land = **pad1=GND / pad2=CSI_D0_CK_P** ⇒ **正好相反** | ESD 器件对**正向** ESD 失效 (I/O 脚接地 ⇒ 到地无通路) + **CSI lane 的负向摆幅被内部二极管钳到 GND 附近** ⇒ 跨铰链 CSI 时钟线既没保护又被钳 | land 目标 = **pad1=CSI_D0_CK_P(I/O) / pad2=GND** ⇒ 两个 pad 对调 (ISS-241 §3 候选1 栏已预告过) | hw-lead (land) |

★**另两条「不是 P0 但必须同批」**: ① `R_SUPV_DIV1/2` 已落成 **0 Ω 跳线且 dnp=必装**, 而 `U_SUPV` 三行 dnp=**DNP** ⇒ **装 0 Ω = 把 `V_SOC_IO` 短路到地** ⇒ 建议随 `U_SUPV` 一并置 DNP (G-10 降级①, 零成本); ② `D_ESD_TC` 落的是 **3 通道** `SP0503BAHT`, 而网表只接了 1 个通道 (USB_VBUS_RAW) + GND ⇒ **另 2 通道闲置** ⇒ Type-C 的 D+/D− 仍未被覆盖。

★**顺带订正第 1 轮的一个降级**: 第 1 轮 G-1 的降级①写「写法A 需要 D-S-G 引脚序器件, 在售件 [0数据]」⇒ ★**本轮实读证明: 用已落地的 G-S-D 器件 (`DMP3098L`) + 板侧对调两个外侧 pad 就够, 不需要买 D-S-G 器件**★。

★**本单仍然一条都没代拍**: V-2 / V-3 / V-4 / G-1 写法 / G-10 恢复不恢复监督器 / LED 亮度档 —— 全部只出依据 + 代价 + 最小修法 ⇒ 交 main / 老板拍。

### §7.4 验收命令实跑输出 (2026-11-17 05:0x 原样)

```
### ① ISS-241 门禁 (上游, 本单不许把它改红)
[check_part_selection_matrix] 门禁检查: HW/PART_SELECTION_MATRIX_2026-11-16.md
  [PASS] C0 — 基准块 JSON 解析通过
  [PASS] C1 — 覆盖 22/22 位号 (含任务书枚举的 20 个全齐)
  [PASS] C2 — 候选完整性: 每件 ≥2 候选且各栏非空
  [PASS] C3 — 封装兼容性: 每件有结论+理由+pads_required
  [PASS] C4 — 证据/降级/推荐: 每件齐全
  [PASS] C5 — 证据等级白名单: 全部合法
  [PASS] C6 — 空话检查: 无空候选/无已定型式空话
  [PASS] C7 — 无越界位号 (OUT_OF_SCOPE ['U_EN_SW', 'U_PWR_SW'] 全部不在册)
[check_part_selection_matrix] PASS — 选型证据矩阵门禁全过 (8/8)
rc=0

### ①b ISS-241 门禁 --selftest
[PASS] M1 删掉一个位号 (Q_PG) — C1 变红 (共 2 条: C1,C7) [落盘回读复核同红]
[PASS] M2 把某件候选清空 (AO3400A 的 pn) — C2 变红 (共 2 条: C2,C6) [落盘回读复核同红]
[PASS] M3 把某件降级方案删空 (D_ESD_USB_D) — C4 变红 (共 1 条: C4) [落盘回读复核同红]
[PASS] M4 塞一个越界位号 (U_PWR_SW) — C7 变红 (共 2 条: C1,C7) [落盘回读复核同红]
[PASS] M5 证据等级写成非法词 [官方] — C5 变红 (共 1 条: C5) [落盘回读复核同红]
[PASS] M6 删掉封装兼容性结论 (Q_ENVC) — C3 变红 (共 1 条: C3) [落盘回读复核同红]
[PASS] M7 把推荐项 why 清空 (Q_PG) — C4 变红 (共 1 条: C4) [落盘回读复核同红]
[PASS] M8 破坏 baseline JSON — C0 变红 (共 1 条: C0) [落盘回读复核同红]
[PASS] M9 把某件候选降到 1 个 (Q_AND) — C2 变红 (共 1 条: C2) [落盘回读复核同红]
selftest: 9/9
[check_part_selection_matrix] PASS — 反向用例 9/9 全抓到
rc=0

### ② merge + gate_check (Q1)
merge rc=0
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-17_hw-lead_ISS268_板只改一次作业包v3_§0两行口径订正.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-17_sw-lead_ISS270_SW侧外部依赖自查.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-17_mech-lead_ISS271_板侧开口S6认领与LED位置约束.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据', '0 数据']
gate rc=0

### ③ 本单门禁
=== ISS-244 选型缺口自查补全 + OPN 回填清单 · 机器门禁 ===
OPN 清单应覆盖件数 (ISS-241 登记范围, 从矩阵基准块读) = 22
其中当前仍待落 (HW/BOM_v1.csv 实跑 待选型∩必装 − 越界件) = 8
[PASS] C0
[PASS] C1
[PASS] C2
[PASS] C3
[PASS] C4
[PASS] C5
[PASS] C6
[PASS] C7
--- 8/8 PASS ---
rc=0

### ④ 本单门禁 --selftest
[PASS] M1 删掉一条缺口 (G-7) → 期望 C1 红
      变异落地(探针 'G-7' 在副本里)=True · 目标 C1 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M2 某条缺口降级方案清空 → 期望 C2 红
      变异落地(探针 'G-3' 在副本里)=True · 目标 C2 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M3 证据等级写成 [官方] → 期望 C3 红
      变异落地(探针 '[官方]' 在副本里)=True · 目标 C3 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M5 清单里删一件 (D_ESD_CAM) → 期望 C5 红
      变异落地(探针 'D_ESD_CAM' 在副本里)=True · 目标 C5 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M6 某行落表锚点清空 → 期望 C6 红
      变异落地(探针 'Q_PG' 在副本里)=True · 目标 C6 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M8 已被别的批次落掉的件清空 landed_note → 期望 C5 红
      变异落地(探针 'C_REGN' 在副本里)=True · 目标 C5 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M9 落表后回归表删掉一行 → 期望 C7 红
      变异落地(探针 'R_SUPV_DIV2' 在副本里)=True · 目标 C7 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M10 落表后回归表某件清空出处 → 期望 C7 红
      变异落地(探针 'C_REGN' 在副本里)=True · 目标 C7 变红=True · 其余 check 仍绿=True · 红因指名=True
[PASS] M4 正文塞一句挂起措辞 → 期望 C4 红
      变异落地(探针 '等原厂回信' 在副本里)=True · 目标 C4 变红=True · 其余 check 仍绿=True
[PASS] M7 破坏基准块 JSON → 期望 C0 红 (且 C1~C6 一致地红 = fail-closed)
      变异落地=True · 目标 C0 变红=True · 其余 check 一致地红(fail-closed)=True
--- SELFTEST 10/10 ---
rc=0

### ⑤ LED 曲线数字化自证 (--selftest)
[PASS] led_aa1608sursk.pdf p3  自证 S1/S2/S3 = [True, True, True]
      If=1.0   mA -> Iv_norm=0.051
      If=1.1   mA -> Iv_norm=0.0563
      If=1.2   mA -> Iv_norm=0.0616
      If=1.3   mA -> Iv_norm=0.0668
      If=1.5   mA -> Iv_norm=0.0774
      If=2.0   mA -> Iv_norm=0.0969
      迹线覆盖 If = [0.384, 30.016] mA, 内点占比 0.6188
[PASS] led_aph1608surck.pdf p3  自证 S1/S2/S3 = [True, True, True]
      If=1.0   mA -> Iv_norm=0.0477
      If=1.1   mA -> Iv_norm=0.053
      If=1.2   mA -> Iv_norm=0.0582
      If=1.3   mA -> Iv_norm=0.0635
      If=1.5   mA -> Iv_norm=0.074
      If=2.0   mA -> Iv_norm=0.1003
      迹线覆盖 If = [0.32, 30.08] mA, 内点占比 0.6282
--- SELFTEST 2/2 ---
rc=0

### ⑥ G-10 分压候选表
=== ISS-244 G-10 · TPS3808G01 分压候选 (公式: V_IT = (1 + R1/R2) x 0.405V, R1+R2 = 4MΩ) ===
窗口假设: 触发点 = 轨标称 x 90% (轨电压跌 -10% 报欠压); 电阻 1%; 阈值精度 typ ±1.5% / max ±3.5%; 迟滞 1.5%

轨标称    V_IT     R1(上)       R2(下)       E96 R1    E96 R2    E96后V_IT  误差带      
-------------------------------------------------------------------------------
3.3    2.970    3454545     545455      3.480M    549k      2.9722    2.8108~3.1378 V
1.8    1.620    3000000     1000000     3.010M    1.000M    1.6240    1.5359~1.7145 V
1.2    1.080    2500000     1500000     2.490M    1.500M    1.0773    1.0188~1.1373 V

★ 结论口径 (只出依据, 不代拍):
  ① 公式与元件约束全部来自 TI 官方手册 (§7.3.1 + Figure 7-1), 可复核;
  ② 三个候选值对应网表 L84 原文的三个候选轨电压 (3.3 / 1.8 / 1.2 V);
rc=0

### ⑦ 件数双源统计
ISS-241 登记范围 = 22
当前仍待落 = 8
已被并发落表落掉 = ['C_REGN', 'D_ESD_CAM', 'D_ESD_DEMO', 'D_ESD_TC', 'D_ESD_USB_D', 'D_TVS_VBUS', 'FB_DEMO', 'FB_VBUS', 'Q_AND', 'Q_CHG_LED', 'Q_ENVC', 'Q_PG', 'R_SUPV_DIV1', 'R_SUPV_DIV2']

### ⑦b 落表后回归 (三方交叉核对)
登记范围 22 件 / 仍待落 8 件 / 已落表 14 件
- C_REGN       4.7µF ±10%             – 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判 
- D_ESD_CAM    TPD1E05U06DPYR         ★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上 板侧改 land: pad1: GND → CSI_D0_CK_P; pad2: CSI_D0_CK_P → GND
      pad 1  net=GND            器件脚=I/O  网表角色=GND  MISMATCH
      pad 2  net=CSI_D0_CK_P    器件脚=GND  网表角色=I/O  MISMATCH
- D_ESD_DEMO   PESD5V0S1BA            – 双向件 ⇒ 极性无关, 不参与引脚序判定       
- D_ESD_TC     SP0503BAHT             – 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判 
- D_ESD_USB_D  TPD1E05U06DPYR         ✔ 引脚序与占位 land 对得上            
      pad 1  net=USB_D_P_SRC    器件脚=I/O  网表角色=I/O  OK
      pad 2  net=GND            器件脚=GND  网表角色=GND  OK
- D_TVS_VBUS   SMBJ5.0A               – 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判 
- FB_DEMO      BLM21PG221SN1D         – 无源件 / 不引脚序敏感 ⇒ 只差 land 几何 (G-7) 
- FB_VBUS      BLM31PG121SN1          – 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判 
- Q_AND        AO3400A                ★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上 板侧改 land: pad1: RESET_N → PG_AND; pad3: PG_AND → RESET_N
      pad 1  net=RESET_N        器件脚=G    网表角色=D    MISMATCH
      pad 2  net=GND            器件脚=S    网表角色=S    OK
      pad 3  net=PG_AND         器件脚=D    网表角色=G    MISMATCH
- Q_CHG_LED    2N7002                 – 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判 
- Q_ENVC       AO3400A                ✔ 引脚序与占位 land 对得上            
      pad 1  net=PG_AND         器件脚=G    网表角色=G    OK
      pad 2  net=GND            器件脚=S    网表角色=S    OK
      pad 3  net=EN_VCORE       器件脚=D    网表角色=D    OK
- Q_PG         DMP3098L               ★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上 板侧改 land: pad1: PWR_ON → PWR_GOOD; pad3: PWR_GOOD → PWR_ON  ★**同时网表 note 的角色必须同批改成写法A (S=BAT_SW / D=ON / G=PG)** ⇒ 否则按 note 的错角色排出来的 land 一样开机不通
      pad 1  net=PWR_ON         器件脚=G    网表角色=S    MISMATCH
      pad 2  net=BAT_SW         器件脚=S    网表角色=D    MISMATCH
      pad 3  net=PWR_GOOD       器件脚=D    网表角色=G    MISMATCH
- R_SUPV_DIV1  0Ω ±1% 跳线              ★P0 (装配级): 0 Ω 且必装 + U_SUPV DNP ⇒ 短路到地 (见拓扑备注) 
- R_SUPV_DIV2  0Ω ±1% 跳线              ★P0 (装配级): 0 Ω 且必装 + U_SUPV DNP ⇒ 短路到地 (见拓扑备注) 
rc=0

### ⑧ 受保护文件 md5 (本单只读不改)
e06c1dd633566aa44732762c2ff99d1c  HW/netlist_v1.csv
287e7861a0d1007748d92d9fbecdd490  HW/netlist_v1_pins.csv
94642d07a69e8d60dd2af57f69b93607  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
da609d7d1844617cdb1e4f425b8b052c  HW/PART_SELECTION_MATRIX_2026-11-16.md
fb286e5f4834fcda045bf8e7bcfecfdf  HW/check_part_selection_matrix.py
```

### §7.5 本轮改了什么 + 边界自证 (追加)

| # | 文件 | 动作 |
|---|---|---|
| 1 | `HW/PART_SELECTION_GAPS_CLOSEOUT.md` | **重生成** (生成器重跑 ⇒ `landed_note` 重算 + 新增 §5 落表后回归 (三方交叉核对表 + 三条 P0 + 十条缺口重判) + 出处表加 S13~S15 + 章节号顺移 §5→§9) |
| 2 | `HW/check_part_selection_gaps.py` | **加 C7** (落表后回归表: 已落表的件逐件有行 + 判定 + 出处 + 有引脚序不符必须有修法) + **加两条反向用例 M9/M10** + 其它用例的「红因指名」自证 (红的那一条必须指名道姓说是哪个目标) |
| 3 | `state/.cache_iss244/post_landing.py` | ★**新建** (落表后回归计算模块: 板文件 pad→net + 网表 note 角色 + 器件引脚序 三方交叉核对; 只读) |
| 4 | `state/.cache_iss244/mos/AO3400A.pdf` / `state/.cache_iss244/led/tpd4e05u06.pdf` | ★**新建** (厂商原厂手册, 带 `--max-time` 的 curl 落盘: AOS `AO3400A` 317,848 B / TI `SLVSBO7O` 2,801,483 B) ⇒ 引脚序证据落盘可复核 |
| 5 | `state/.cache_iss244/run_acceptance.sh` / `acceptance_output.txt` | 验收脚本更新 (加 ⑦b 落表后回归) + 本轮输出落盘 |
| 6 | `state/fragments/sw.yaml` | 只加 artifact + interface_claim + answer (走 `state/frag_write.py` 原子写) |

★**本轮只读、零改动**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` / `HW/PART_SELECTION_MATRIX_2026-11-16.md` / `HW/check_part_selection_matrix.py` —— 本单**只读不写** ⇒ 板 / 布线 / 布局 / 网表 / 脚表 / BOM **本单一个字节没动**。

★★**诚实订正 (2026-11-17 05:2x 自查时发现, 原措辞不准确)**: 原写「md5 与第 1 轮交卷时逐字节相同」**对 netlist / pins / BOM 三件不成立** —— 第 1 轮交卷时记录的是 `611c3ba3…` / `ef436a37…` / `2a730574…`, 而 §7.4 ⑧ 实测是 `e06c1dd6…` / `287e7861…` / `94642d07…` ⇒ **三件在第 1 轮交卷之后被改过**。归因: 那三个文件的 mtime = **2026-11-16 22:25:14** (= 板侧第二个并发落表批次, 落了 13 件选型件) ⇒ ★**改动归属那个批次, 不是本单**; 本单在这三个文件上**全程只读** (`build_closout.py` 只写收口页; 门禁只读 + selftest 只在内存副本上变异) ⇒ 本单零写入这一事实不受影响, 但「逐字节相同」的说法**已作废, 按本条为准**。
★板 / `.kicad_pro` / ISS-241 矩阵 / ISS-241 门禁四个文件的 md5 **与第 1 轮交卷时逐字节相同** (`611b869e…` / `3e504d2b…` / `da609d7d…` / `fb286e5f…`) ⇒ ★**板 / 布线 / 布局 / 上游矩阵与门禁: 零改动, 属实**。

★**边界**: 零外发 (本轮只用了 `curl --max-time` 下载厂商公开手册 + `pdftotext` 实读 + 本机文件实读) · 不改 `PROJECT_TRACKER.md` §0 · 不写别人的分片 · `state/issue_log.yaml` 零写入 (verify 留给 main) · **实物 [实测] = 0 条** (本机无板; 所有 [实测] 都是文件实读与脚本实跑)。

### §7.6 请 main 追加处理 (第 2 轮的增量)

1. **把 §7.3 三条 P0 派给板那一趟** (hw-lead) —— ★**P0-a / P0-b / P0-c 都是「两个外侧 pad 对调」级别的改动, 但不派下去就会做出一块开不了机 / 复位不灵 / CSI 没保护的板**★。
2. **P0-a 的写法拍板** (写法A vs 写法B) 仍然归 PM/老板 ⇒ ★**本单建议写法A, 但不代拍**★ ⇒ 落表批次在拍板前**不要**先改 note 的措辞 (先改了就把错角色固化成文字)。
3. **落表批次**: 收口页 §4 的 22 行清单里 **只剩 8 行还待落** (`D_CHG_LED` / `D_LED_G` / `D_LED_R` / `SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST`) ⇒ 请按这 8 行排批次, ★**其中 4 颗按键 + 2 颗 LED 的 footprint 占位仍要重画 (G-7) ⇒ 落表与 land 必须同批**★。
4. **`R_SUPV_DIV1/2` 随 `U_SUPV` 一并 DNP** (G-10 降级①) ⇒ 零成本动作, ★但要 main 拍 (本单不代拍)★。
