★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**TPS7A20 族 7 颗 LDO 的引脚功能名串号** (脚表里 pin4(IN) 被写成 "EN (pin3)" · pin5(散热焊盘) 被写成 "GND (pin2)") ★**和**★**U_LDO_S28 整颗缺 pin3(EN) 脚** ★**收成【可落表的逐行改法映射 + 一个独立机器门禁】**★ ⇒ ★**脚表 35 行逐脚对账表 + 根因定性 + 改法映射 v1 + 独立门禁 (带反向用例) + 落表时机建议 (交 main)**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 10:5x~11:0x 自己逐行实测, 不是推测★)** ★★
· ★**本轮 advance.py 的 internal 段是空的** (sw-lead=ISS-172 fixing 且会话在跑 · mech-lead=ISS-238 fixing 且会话在跑 · ★**hw-lead=ISS-237 已于 10:13 交卷, 名额空出来**★) ⇒ ★**这条是 main 自己挖出来的真病灶**
· ★**ISS-237 交卷报告里那句「网表里 7 颗 TPS7A20 的 EN 脚一行都没有 ⇒ 全表关断」是错的** (★main 实测: 网表 L102/L112/L122/L132/L142/L152 **都有 EN 行**⇒ 6/7 有 EN★) ⇒ ★**真问题另有两处, 就是本单** ★
· ★**顺带说一句纪律**: ★**派活时把结论核到行号是值的** ⇒ 本单所有结论都给了行号, 你也要逐条自己复核, ★**不许照抄 main 的结论当作你的发现**★ ★

★★**① 脚表逐脚对账表 (★必交·35 行=7 颗×5 脚★)** ★★
· ★**做成一张表**: 位号 × pin1/pin2/pin3/pin4/pin5 × 【官方功能名 (1=OUT·2=GND·3=EN·4=IN·5=散热焊盘→GND)】× 【脚表当前 value】× 【判定: 对/错/缺】 ★
· ★**7 颗 = `U_LDO_S28` / `U_LDO_S18B` / `U_LDO_S12` / `U_LDO_L33` / `U_LDO_L18` / `U_LDO_IO33` / `U_LDO_IO18`** (★自己从 `HW/netlist_v1_pins.csv` 复核一遍, 别只抄这串★)
· ★**每行都要带**: 官方功能名 + 出处 (★TI TPS7A20 datasheet · 仓库内已有 `HW/CORE_MODULE_SELECTION.md` L15 与 `HW/POWER_RAIL_SPEC.md` L41 两处记录★) + 证据等级 ★**★去 ti.com 自己复核一次 (自己查, 不许发信) ⇒ 标 [官网]★** ★
· ★**判定口径不许自己放宽**: 「脚表 value 与官方功能名不一致」= 错; 「该脚在脚表里不存在」= 缺; ★**不许因为「语义差不多」判成对** ★

★★**② 根因定性 (★要查到代码行★)** ★★
· ★**必须自己读 `state/gen_netlist_pins.py`** (★它自己文档里就写明「从 `.csv` 取每个 (ref, net) 的元信息 (value/footprint/dnp/evidence/page/board/conn_id)」, L228 是 `"value": cell(m, "value")`★) ⇒ ★**证明/推翻「同 (ref, net) 多行 ⇒ metadata 被复制给同网每一个脚」这个假设** ★
  · ★**如果推翻** ⇒ 给出真根因 (★行号 + 可复现的最小例子★) ★
  · ★**如果成立** ⇒ 给出【改法候选 ≥2 个】 (★例: ① 索引键从 (ref, net) 改成 (ref, pin) ② CSV 里 pin4 那行改成与 EN 行同形态 + value 写成 "IN (pin4)" ③ 在脚表生成时按 .net 的 pin 反查原始行★) ★**每个候选都要给: 改哪里(文件+行号) · 改了之后脚表长什么样 · 会不会影响别的 584 脚 · 风险** ★
· ★**顺带把 26 组同网多脚列出来** (★main 已实测出 14 颗器件名单, ★**自己重扫一遍, 不许照抄★**) ⇒ ★**逐组判: 语义无害 / 语义错** ⇒ **只有 TPS7A20 那 7 组是语义错 (J_CHG pin9/pin10 是措辞差)** ⇒ ★**不许把 26 组都说成 bug** ★
· ★**解释清楚一件事**: ★**为什么 `state/check_sch_pinfull.py` 的「584=584」抓不到这些** ⇒ 因为 ★**原理图符号脚数与脚表脚数同源派生 (都由 `state/gen_netlist.py` 生成) ⇒ 一起错就一起过** ★ ⇒ ★**所以新门禁不能只查脚数, 得查【脚的功能名】** ★

★★**③ 改法映射 v1 (★交 main 排期落表, 本轮不许写盘★)** ★★
· ★**逐行写清**: 改哪个文件哪一行 → 改成什么 → 依据(官方 pinout + 仓库哪处记录) → 改完脚表那几行长什么样 ★
  · ★**必须覆盖两条**: ① 7 颗的 pin4/pin5 功能名串号怎么改 ② ★**U_LDO_S28 缺的 pin3(EN) 怎么补** (★两个选项都要给: **A** 在生成器里去掉 `if ref != "U_LDO_S28"` 例外, 让它也发 EN 行 (DNP 器件 ⇒ 无电气影响, 脚表与实体脚数一致) · **B** 保持不发, 但脚表/文档里明确写「DNP · 本体只有 4 脚列入脚表」+ 理由 ⇒ ★**两个选项各给代价, 不许代拍**★) ★
· ★**落表影响面必须写**: 改完网表/脚表 md5 会变 ⇒ ★**MECH `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 + SW `SW/SW_MD5_BASELINE_LEDGER.md` §1 两个锚点要 H-1 重锚** ⇒ ★**本轮别动那两份台账 (那是别人的文件), 只在交卷单里点名** ★
· ★**别忘了脚数**: ★**补 U_LDO_S28 的 EN 脚 ⇒ 脚表从 584 → 585** ⇒ ★**`state/check_sch_pinfull.py` 的基线数会变** ⇒ ★**这属于「落表批次」的事, 本单只在改法映射里写清楚, 不许自己改基线** ★

★★**④ 独立机器门禁 (★新建, 不许依赖受保护脚本★)** ★★
· ★**新建** `HW/check_pin_function_labels.py` ⇒ 至少 4 类检查: ★
  ① ★**TPS7A20 族每颗每脚**: 脚集完整 (5 脚全在) + 脚表 value 必须体现官方功能名 (OUT/GND/EN/IN/散热焊盘) ⇒ ★**逐脚点名, 报「位号.脚号」** ★
  ② ★**同一器件内不许两个脚共用同一个功能名** (★对 TPS7A20 这条现在会红: pin3/pin4 都叫 "EN (pin3)" · pin2/pin5 都叫 "GND (pin2)"★) ⇒ ★**这条不许对无源件误报 (R/C 的 value 本来就重复)** ⇒ **限死在 IC 类** ★
  ③ ★**官方 pinout 表不许被改软**: 门禁内置/读取的那份 pinout 必须与出处一致 (★出处写清 TI TPS7A20 datasheet + 仓库两处记录★) ⇒ 篡改它必须红 ★
  ④ ★**受保护文件 md5 未变** (网表/脚表/BOM/板/`.kicad_pro` 五个值写在脚本里, ★**不许改脚本里的基线值来凑绿**★) ★
· ★**三种运行模式都要有 (★这是本单的核心交付, 缺一不可★)**: ★
  · ★**默认 (无参数)** ⇒ ★**rc=1** (★缺陷还在 ⇒ 该红★) + 打印已知缺陷清单 + ★**首行必须写明「当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿」** ★
  · ★**`--expect-known`** ⇒ ★**rc=0** (★已知缺陷清单与快照逐条一致 ⇒ 绿★) + ★**清单多一条/少一条/变一条都要红** ★
  · ★**`--selftest`** ⇒ ★**rc=0** + ★**≥6 条反向用例** (★建议: 把某颗的 pin4 改回 "EN (pin3)" ⇒ 仍被点名 · 删掉清单里一条 ⇒ `--expect-known` 红 · 篡改 pinout 表 ⇒ 红 · 把 pin4 改成 "IN (pin4)" ⇒ 该条从清单里消失且 `--expect-known` 红 · 篡改受保护 md5 基线 ⇒ 红 · 把 IC 限制放宽到无源件 ⇒ 红★) ★
  · ★**★每条反向用例必须自证「它真的改到了目标」★** ⇒ ★**不许写一条永远绿着的假用例 (★ISS-227 / ISS-221 同款教训: 「有断言」≠「断言有效」★)** ★
· ★**不许把判据放宽成「脚表里没有 IN 就当没有 IN」** ⇒ ★**底线: 7 颗 LDO 的 5 个脚必须齐全且功能名对得上官方 pinout** ★

★★**⑤ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★**新建** `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` ⇒ 35 行逐脚对账表 + 根因定性 + 26 组同网多脚清单与定性 + 改法映射 v1 (含 U_LDO_S28 补脚的 A/B 两案) + 落表时机与 H-1 重锚影响面 + 官方 pinout 出处 + 证据分级 ★
2. ★**新建** `HW/check_pin_function_labels.py` (★默认 / `--expect-known` / `--selftest` 三模式★)
3. ★**新建** `HANDOFF/2026-11-16_hw-lead_ISS239_TPS7A20引脚功能名串号与缺EN脚.md` (★B1~B6 六块齐全★)
4. `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead --add-artifact path=… summary=… --add-claim key=… value=… --add-need key=… to=main item=…` 原子写; ★**只加, 不许删改别人的 key**★)
5. ★**可选**: 在 ★**/tmp 副本** (★`cp -a` 整棵树, ★**别只 cp 几个文件 — 上一轮踩过: 副本被掐死那轮弄脏, 只还原了 5 个源文件就拿去做落表测试★) 上跑一遍生成器 ⇒ 把「改后 35 行」的实跑输出贴进 ① ★**真盘不许动** ★

★★**⑥ 验收标准 (★机械可判, 不许含糊★)** ★★
· `python3 HW/check_pin_function_labels.py` ⇒ ★**rc=1** 且 ★**它点名的清单 = main 实测的那 14 处串号 (7 颗 × pin4+pin5) + U_LDO_S28 缺 pin3** (★多报/少报都算不通过★) ⇒ ★**首行有「当前基线 = 已知缺陷 ⇒ rc=1 属预期」那句** ★
· `python3 HW/check_pin_function_labels.py --expect-known` ⇒ ★**rc=0** ★
· `python3 HW/check_pin_function_labels.py --selftest` ⇒ ★**rc=0** 且 ★**≥6/6** ★
· `python3 HW/check_step1_parts_spec.py` ⇒ ★**rc=0** (C1~C8 8/8, ★**ISS-237 刚立的闸, 不许被本单改红★★) · `--selftest` ⇒ rc=0 (T1~T8)
· `python3 state/check_sch_pinfull.py` ⇒ ★**rc=0** (★**584=584 —— 本单不许改脚数基线**★) · `python3 state/check_netlist.py` ⇒ rc=0 · `python3 state/check_netlist_pins.py` ⇒ rc=0 · `python3 state/check_sch_erc.py` ⇒ rc=0 (ERC=0)
· `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 且 ★**【Q1】18/18** ★
· ★**`md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro` ⇒ 与 `34132f7e…` / `b21b743a…` / `c195a117…` / `611b869e…` / `3e504d2b…` 逐字节一致** ★ (★自己先 md5sum 复核一遍再报★)
· ★**零外发** · ★**实物 [实测] = 0 条** (★板不在本机★) · ★**没碰 PCB 布线/布局/板框** · ★**没改 PROJECT_TRACKER.md §0** · ★**没改 `state/issue_log.yaml`** (★verify_by = main★) · ★**没写别人的分片** · ★**没碰 `SW/` 与 `MECH/` 任何文件** ★

★★**⑦ 边界与并发纪律 (★10:5x~11:0x 实测实况★)** ★★
· ★**mech-lead 名额在跑 ISS-238 (走鹃旧口径 C1 门禁红) ⇒ 它在动 `MECH/` 下 4 个文件 + 新建门禁 ⇒ ★**你一个 MECH/ 文件都不许碰** ★
· ★**sw-lead 名额在跑 ISS-172 (负载开关 U_PWR_SW / U_EN_SW 选型证据矩阵) ⇒ ★**你一个 SW/ 文件都不许碰** ★
· ★**不许改这些 (受保护 / 被锚定)**: `state/gen_netlist.py` · `state/gen_netlist_pins.py` (★**真盘不许改, 只许在 /tmp 副本上预演★**) · `state/check_netlist.py` · `state/check_netlist_pins.py` · `state/check_sch_erc.py` · `state/check_sch_pinfull.py` · `HW/check_step1_parts_spec.py` · `HW/check_netlist_selfconsistency.py` · `MECH/check_demo_struct_truth.py` · ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 板 / `.kicad_pro` / `HW/STEP1_PARTS_SPEC.md` / `HW/PART_ALTERNATIVES_REGISTRY.md`** (★**这两个 md 是 ISS-237 刚落的, 本单只在交卷单里"引用"它们, 不许改★**) ★
· ★**不许代拍 V-2 / V-3 / V-4** (★落表器 `state/land_v_values.py` 在, 但★**本单不落任何 V 值★**) ★
· ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**官方资料自己上 ti.com 查, 每条标 [官网]/[实测]/[媒体]/[推算]/[0数据]; 查不到就写 [0数据] + 降级方案, 不许编, 也没有「批一句可以发」这个选项** ★
· ★**交卷前把 ISS-237 那句错话也一并更正** (★在交卷单 B5 里写一句: 「ISS-237 交卷单的 M4『7 颗 TPS7A20 的 EN 一行都没有 ⇒ 全表关断』经 main 实测不成立, 真病灶是本单这两条」★) ★
