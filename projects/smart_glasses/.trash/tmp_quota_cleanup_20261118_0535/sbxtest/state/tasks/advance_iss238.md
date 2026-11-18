★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**`MECH/display_biosafety_v2_check.py` C1 那盏红灯转绿**★ ⇒ ★**拆成「4 处假阳性 + 1 处真漏标」分别处理**★ ⇒ ★**文档侧补标 + 判据侧放宽提案 (交 main) + 一个不依赖受保护脚本的新机器门禁 (带反向用例)**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 10:4x 自己实跑, 不是推测★)** ★★
· ★**main 把全仓 47 个 check 脚本逐个实跑了一遍** (★`state/check_footprint_geom.py` 那个 ModuleNotFoundError 是 main 用错入口 (它要 `bash state/pcbnew_py.sh …`), 实跑 rc=0 几何全对 ⇒ **不是缺陷, 不许去"修"它**★) ⇒ ★**真抓到 1 盏隐形红: `MECH/display_biosafety_v2_check.py` rc=1** ★
· ★**红灯原文 (逐字)**: `[C1] 走鹃旧口径收口 (5 份旧文档) FAIL` · `活动口径 = 5 (必须 0) ; 历史沿革 = 31` · `违规行: MECH/MECH_BUDGET.md:71, :94, :849, :880, :944` (★C2/C3/C4/C5 全 PASS★) ★
· ★**判据怎么算的 (脚本实读)**: `MECH/display_biosafety_v2_check.py` L40 `MARKER = "已作废 (2026-11-15, ISS-134 V2)"` ⇒ L95~120 `check_c1()`: 行内含「走鹃」且★**不含这个单一字符串**★⇒ 记「活动口径」⇒ FAIL; 含 ⇒ 记「历史沿革」⇒ 允许 ★
· ★**main 逐行读了那 5 行 ⇒ 4 处假阳性 + 1 处真漏标** (★逐条原文在 issue 的 desc 里, 自己再去盘上核对一遍, 不许照抄★)
· ★**这盏红不在 daily_check 链上** (★`grep -n "display_biosafety" state/daily_check.py` ⇒ 0 命中★) ⇒ ★**巡检看不见 ⇒ 「走鹃旧口径已收口」这句话现在没有机器背书** ★

★★**① 文档侧补标 (★主修复·不许删改实测原文★)** ★★
· ★**只许动 `MECH/MECH_BUDGET.md` 的那 5 行 (L71 / L94 / L849 / L880 / L944)★** ⇒ ★**逐字追加 canonical 标注 `已作废 (2026-11-15, ISS-134 V2)` (脚本认的就是这一串)★**
· ★**L71 / L94 / L849 / L944 = 假阳性**: 它们★**已经带了作废标注**★ (ISS-222 · C-6 落地形态) ⇒ ★**canonical 标注是【追加】(两个标注并存), 语义真实**: 走鹃Ⅱ 2.9 mm 光束口径★**自 ISS-134 V2 (11-15) 起即作废**★ ⇒ ★**不许因为"已经有标注了"就跳过这 4 行** ★
· ★**L880 = 真漏标**: 这行★**一个作废标注都没有**★ ⇒ ★**除了补标注, 还要把行内「走鹃Ⅱ 口径 14×10×6」明确写成历史口径 (加限定语), 让它自己站得住** ★
· ★**绝对不许**: ★**删行 / 删数值 / 改口径内容 / 改 M6 W4 等表里的任何数字**★ ⇒ ★**删掉 = 失去「当初为什么这么选」的留痕 (★本项目的判据本体只许加不许放宽★)** ★
· ★**不许改**: `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (md5 96239070… · C5 硬判据) · `MECH/JBD_ROLE_NARROWING.md` (md5 bda4a294…) · `MECH/display_biosafety_v2_check.py` (md5 29c77fc3… · ★**在 `MECH/check_demo_struct_truth.py` 的受保护清单里**★) · `MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md` 的 33 行定性表 (★**C4 查它: 33 行 + 分布 21/6/3/2/1 ⇒ 不许改结构/分布, 不许增删行★) ★
· ★**改 `MECH/MECH_BUDGET.md` 前先查锚点**: ★**main 已实测: 全仓没有任何地方锚着 `MECH_BUDGET.md` 的 md5 (grep `1b4ae5d8…` ⇒ 0 命中) ⇒ 不需要走 H-1 重锚**★ ⇒ ★**但你改之前自己再 grep 一次 (★万一并发会话刚加了锚点★)** ★

★★**② 判据侧放宽提案 (★只出文档, 不许改受保护脚本★)** ★★
· ★**新建** `MECH/DISPLAY_BIOSAFETY_V2_MARKER_POLICY_PROPOSAL.md` ⇒ ★**写清三件事**: ★**① 病灶**: MARKER 只认单一字符串 ⇒ 作废标注形态每多一种就再打红一次 (★ISS-222 形态已经打过一次★) ★**② 建议口径** (★给 2~3 个可选方案, 不许只给一个★): 例如 ① 改成 regex「已作废」+ (日期 或 ISS 号) 任意一种都算历史沿革 ② 改成「已作废」或「作废」或「历史沿革」或「旧口径」四选一 ③ 维持单一字符串 + 加一条"新增作废标注形态必须同步进 MARKER 清单"的流程约束 ★**③ 每条建议都要给反向用例设计** (★怎么证明放宽后仍能抓住真漏标★): 例如 ★**「把 L880 的标注删掉 ⇒ 必须红」/「把某行的标注换成另一种形态 ⇒ 按你建议的口径应该红还是绿, 说清楚」** ★
· ★**★不许自己改 `MECH/display_biosafety_v2_check.py`★** ⇒ ★**放宽判据要走 H-1 重基线 (改脚本 + md5 台账 + 反向用例 + 留痕), 那是 main 的活** ★ ⇒ ★**本单只交提案** ★
· ★**提案里必须写明一条底线**: ★**放宽的只是「什么算作废标注」, 不许放宽成「有走鹃字样就算过」⇒ 裸走鹃命中必须仍然是红** ★

★★**③ 新机器门禁 (★不许靠受保护脚本, 新建一个★)** ★★
· ★**新建** `MECH/check_zoujuan_marker_consistency.py` ⇒ ★**至少查 5 条**: ★
  ① **5 份旧文档里含「走鹃」的行必须全部带 canonical MARKER** (活动口径 = 0) ⇒ 逐行点名
  ② ★**canonical MARKER 串本身必须存在于文档里** (★否则门禁自己失效了都没人知道★)
  ③ ★**`MECH/MECH_BUDGET.md` 里不许出现【无标注的裸走鹃命中】** (★L880 这类 = 真漏标★)
  ④ ★**「作废标注形态」清单**: 把当前盘上实际出现过的作废标注形态 (★ISS-134 V2 串 / ISS-222 串 / 裸「已作废」/ 其它你扫到的★) 列成清单 ⇒ ★**与提案文件里的清单对得上** (★两份不许各写各的★)
  ⑤ ★**受保护文件 md5 未变** (★`display_biosafety_v2_check.py` 29c77fc3… · `DISPLAY_BIOSAFETY_CRITERIA_V2.md` 96239070… · `JBD_ROLE_NARROWING.md` bda4a294… · `check_demo_struct_truth.py` fa9b59e5…★)
· ★**rc=0 = 全过; 任一条不过 ⇒ rc=1 并点名是哪一条** ⇒ ★**必须支持 `--selftest`, ★≥5 条反向用例★ (★建议: 删掉 L880 的标注 ⇒ ③ 红 · 删掉某行的 canonical 标注 ⇒ ① 红 · 把 canonical 标注串从脚本/文档里删掉 ⇒ ② 红 · 篡改提案清单使其与文档形态对不上 ⇒ ④ 红 · 篡改判据文件 ⇒ ⑤ 红★) ★
· ★**★反向用例必须自证「它真的改到了目标」★** ⇒ ★**不许写一条永远绿着的假用例 (★ISS-227 同款教训: 「有断言」≠「断言有效」★)** ★

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★**改** `MECH/MECH_BUDGET.md` (★只动那 5 行, 只加标注/限定语★)
2. ★**新建** `MECH/DISPLAY_BIOSAFETY_V2_MARKER_POLICY_PROPOSAL.md` (★判据侧放宽提案 + 反向用例设计★)
3. ★**新建** `MECH/check_zoujuan_marker_consistency.py` (★门禁 + `--selftest`★)
4. ★**新建** `HANDOFF/2026-11-16_mech-lead_ISS238_走鹃旧口径C1门禁红.md` (★B1~B6 六块齐全★)
5. `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写: 只加 artifact/claim/answer; ★**不许删改别人的 key**★)

★★**⑤ 验收标准 (★机械可判, 不许含糊★)** ★★
· `python3 MECH/display_biosafety_v2_check.py` ⇒ **rc=0** 且 ★**5/5 全 PASS (含 C1 活动口径 = 0)**★
· `python3 MECH/display_biosafety_v2_check.py --selftest` ⇒ **rc=0** (★它自己那 5 个用例★)
· `python3 MECH/check_zoujuan_marker_consistency.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 且 ≥5/5**
· `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0** (★23/23 · 受保护 md5 一个没变★)
· `python3 MECH/cavity_recalc_check.py` ⇒ **rc=0** (★23/23★)
· `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 且 ★**【Q1】18/18**★
· ★**`md5sum MECH/display_biosafety_v2_check.py MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md MECH/JBD_ROLE_NARROWING.md MECH/check_demo_struct_truth.py` ⇒ 与上面写的 4 个值逐字节一致** ★
· ★**零外发** · ★**实物 [实测] = 0 条** (★板不在本机★) · ★**没碰 PCB 布线/布局/板框** · ★**没改 PROJECT_TRACKER.md §0** · ★**没改 `state/issue_log.yaml`** (★verify_by = main★) · ★**没写别人的分片** ★

★★**⑥ 边界提醒 (★并发实况·10:5x 实测★)** ★★
· ★**hw-lead 名额在跑 ISS-237 (P2 屏口径收死) ⇒ 它在动 `HW/STEP1_PARTS_SPEC.md` / `HW/PART_ALTERNATIVES_REGISTRY.md` / `HW/check_step1_parts_spec.py` / `HW/netlist_v1*.csv` ⇒ ★**你一个 HW/ 文件都不许碰** ★
· ★**sw-lead 名额在跑 ISS-172 (负载开关选型证据) ⇒ ★**你一个 SW/ 文件都不许碰** ★
· ★**板 md5 `611b869e…` / `.kicad_pro` `3e504d2b…` / 网表 `34132f7e…` / 脚表 `b21b743a…` ⇒ 交卷时逐字节不变** ★
