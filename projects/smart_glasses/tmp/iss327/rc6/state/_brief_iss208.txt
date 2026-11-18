★**目标 (★内部活·不是原厂的事·不是 PCB 布线/布局类★)**: 把 ★**ISS-134 遗留的 33 处「走鹃」活动口径一次性收口**★ (★mech-lead 你自己在 ISS-134 交卷里登记的 need `iss134_mech_close_legacy_zoujuan_refs`★) ⇒ 并且把 ★**光生物安全 V2 里「结构侧真正能兜住的那几条」落进结构真源**★ (★最关键是 C-4/C-5: 入眼 2000 cd/m² ⇒ 波导眼盒面积 A_e ≤ 62 mm² (≈8×7.7 mm) ⇒ 直接夹住镜框上沿厚度 + 鼻梁区光件空间★) ⇒ ★**零外发, 查不到就写降级方案** ★

★★**为什么是现在 (★main 2026-11-15 21:4x 实测, 不是推测★)** ★★
· ★**实测**: `grep -rc "走鹃" MECH/*.md` ⇒ ★**7 个文件有命中**: `MECH/MECH_BUDGET.md` 21 处 · `MECH/PROTOTYPE_PLAN.md` 6 处 · `MECH/SOC_CARRIER_EVAL.md` 3 处 · `MECH/STRUCT_REVIEW_ISS065.md` 2 处 · `MECH/CLEARANCE_FIX.md` 1 处 = ★**旧文档合计 33 处**★; ★**另两份是历史语境** (`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` 4 处 · `MECH/JBD_ROLE_NARROWING.md` 12 处) ⇒ ★**要收的是前 5 份的 33 处** ★
· ★**现行口径 (ISS-134 已闭死, 你不许改它, 只许引用)**: ★**「波导必须找 JBD」不成立** (公开在售/量产 ≥11 家) ⇒ 旧文档里「波导 = JBD」的活动口径就是**错口径**, 留着会让后面的镜框/光机设计照着错的做
· ★**ISS-134 的 6 条判据已经落盘** (`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md`) ⇒ ★**你的活是【让它变成结构侧的真源约束】, 不是再写一遍判据** ★

★★**① 收口 33 处 (★逐处定性, 一处都不许漏★)** ★★
· ★**每处必须定性成两类之一**: **(a) 活动口径 (还在陈述现状)** ⇒ ★**必须改写成现行口径** (★波导 ≠ JBD 专属; 波导供应商公开在售 ≥11 家; 光生物安全改走 IEC 62471-7:2023 大光源辐亮度体系, 旧口径 LED 点光源 Exempt 1.0 W/m² 已作废★); **(b) 历史沿革 (记录当时状态)** ⇒ ★**保留原文, 但必须加「★已作废 (2026-11-15, ISS-134 V2)★」标注 + 一句话说明作废原因** ★
· ★**不许用批量替换一刀切** ⇒ ★**不许把历史沿革段落里的「走鹃」也改成新口径 (那是篡改历史)** ⇒ ★**必须逐处定性 + 出表** ★
· ★**不许删段落** ⇒ 只许改写 / 加标注
· ★**5 份旧文档里与「走鹃」绑在一起的其他旧数字 (若存在)** ⇒ ★**只在交卷件里列出来 + 登记 need 给 main**, 不许顺手改 (★只报不改, 由 main 裁★)

★★**② 把眼盒约束落进结构真源 (★本单最值钱的一条★)** ★★
· ★**要落的数 (ISS-134 V2 已定, [推算])**: `L_eye,max = 0.1234 / A_e` ⇒ ★**A_e=150 mm² → 823 cd/m² · 64 → 1928 · 25 → 4936** ⇒ ★**要入眼 2000 cd/m² ⇒ A_e ≤ 62 mm² (≈8×7.7 mm)** (★出处: `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` 的 C-4 / C-5★)
· ★**要做的事**: ★**先判定「结构侧真源」是哪个/哪几个文件 (自己查, 要给出理由) ⇒ 把眼盒面积约束 + 它夹住的镜框上沿厚度 / 鼻梁区空间写进去 ⇒ 写成【下一单能直接引用的约束条目】** ★
· ★**不许自己放宽或收紧 62 mm² 这个数** ⇒ ★**它来自 V2 判据 (公式 + 面板 3000 cd/m² + η=1.83%) ⇒ 你只许引用与落位** ★
· ★**若结构侧真源里有跟 62 mm² 冲突的既有尺寸** ⇒ ★**只报不改 + 登记 need 给 main** ⇒ ★**冲突要算出来 (冲突量多少 mm / mm²)** ★
· ★**不许写「波导还没定型所以这条先不管」** ⇒ ★**V2 已明确: 占位件必须 FOV 可变 ⇒ 眼盒是硬约束, 不是待定项** ★

★★**③ 机器门禁 (★本单必须留一个能自动复核的东西★)** ★★
· ★**新建** `MECH/display_biosafety_v2_check.py` (★新建★) ⇒ 至少查: ①**旧文档 5 份里的「走鹃」命中数** (★**活动口径必须 = 0**; ★历史沿革允许保留, 但脚本输出必须能一眼看出「活动口径 0 / 历史沿革 N」★) ②**眼盒约束条目是否已落在结构真源里** (★关键词 + 数值 `62` 都要命中★) ③**V2 判据 6 条的关键量是否被结构侧引用** (★引用即可, 不许复制改写★) ⇒ ★**rc=0 = 全过; 任何一条不过 ⇒ rc=1 并点名是哪一条** ⇒ ★**脚本要支持 `--selftest` (★至少 3 个用例: 故意塞一条活动口径 ⇒ 必须被抓★)** ★
· ★**不许改** `MECH/hinge_usb_check.py` · `MECH/service_port_check.py` · `MECH/hw_cross_review_check.py` (★md5 不许变★)

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★新建★ `MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md` — ①**33 处逐处定性表** (文件 + 行号 + 原句摘要 + 类别(活动/历史) + 处置) ②**眼盒约束落位说明** (落到哪个结构真源 + 为什么是它 + 引用了 V2 的哪条) ③**与结构真源的冲突项 (若有) + need 登记** ④证据分级 ⑤复现命令 ⑥边界
2. ★**改写后的 5 份旧文档**: `MECH/MECH_BUDGET.md` · `MECH/PROTOTYPE_PLAN.md` · `MECH/SOC_CARRIER_EVAL.md` · `MECH/STRUCT_REVIEW_ISS065.md` · `MECH/CLEARANCE_FIX.md` (★只许改「走鹃」相关处 + 加作废标注, 其余段落一字不动★)
3. ★新建★ `MECH/display_biosafety_v2_check.py`
4. ★新建★ `HANDOFF/2026-11-15_mech-lead_ISS208_走鹃旧口径收口与眼盒约束落地.md` — 交卷报告 (★≤25 行★)
5. ★**必要时** `state/fragments/mech.yaml` (走 `state/frag_write.py`; ★只许新增条目, 不许删改别人的 key★)

★★**⑤ 验收自证 (交卷前跑, 把输出贴进回复)** ★★
```
python3 MECH/display_biosafety_v2_check.py            # rc=0
python3 MECH/display_biosafety_v2_check.py --selftest  # rc=0
python3 MECH/hinge_usb_check.py                        # rc=0 (不许变红)
python3 MECH/service_port_check.py                    # rc=0 (不许变红)
python3 state/merge.py                                # rc 必须 0
python3 state/gate_check.py                           # rc=0, 【Q1】必须 18/18
grep -rc "走鹃" MECH/*.md                              # 逐行定性表见交卷件
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb MECH/hinge_usb_check.py MECH/service_port_check.py
```
★**md5 期望 (不许变)**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` · `MECH/hinge_usb_check.py` `3425bc141508de8a35f34c7cf7b803e8` · `MECH/service_port_check.py` `9b24bf985764880f0105aee677fba6a8` ★
★**并发提示 (★2026-11-15 21:4x 实测★)**: 同一时刻可能有 3 个 agent 在跑 ⇒ ★**`state/merge.py` 若报 rc=2 (并发写 STATE.yaml 冲突) ⇒ 等 30 秒重跑一次; 重跑仍红就如实报, 不要死磕** ★

★★**⑥ 边界 (不许越)** ★★
· ★**不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ ★**查不到就标 [0数据] + 写降级方案** ★
· ★**不许改判据**: `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (★只许引用, 不许改一个字★) · `MECH/JBD_ROLE_NARROWING.md` (★只许引用★) ⇒ ★**判据阈值一条不许松** ★
· ★**不许碰 PCB 布线 / 布局** (★老板 2026-11-11 10:07 主线★) · `HW/` 下任何文件 · `SW/` 下任何文件 · `state/issue_log.yaml` (★改 issue 状态是 main 的活★) · **别人的分片** · `PROJECT_TRACKER.md` §0 · `state/outbox/` 下任何草稿 (★只留档, 永不发★)
· ★**实物 [实测] = 0 条** (本机无样件 / 无量具) ⇒ 所有数值要么 [官网] / [推算] / [0数据]
· ★**交卷 ≤ 25 行** ★
