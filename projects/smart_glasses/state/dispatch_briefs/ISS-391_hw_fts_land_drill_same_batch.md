# ISS-391 · hw-lead · 「板只改一次」那一趟的排针 land 【`0.65 → 0.71` 钻孔这一条板侧改动还没进作业包/预检清单】⇒ 把它补进去 (★纯分析 + 改文档 + 新建闸 · 零写板 · 零落表·零改既有闸★)

★**本单性质**: ★**纯分析 + 作业包 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【板侧作业包同批完整性层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★
★★**★本单为什么必须做 (★main 本机实读 · 不抄任何 agent 报告★) ★★** ★★

★**① 今日 11:1x, ISS-387 (★你自己交的单★) 查出一件【全项目都还没登记】的板侧改动**: ★**落 `FTS` 时, 板上钻孔必须 `0.65 → 0.71`** ★
★**② 但 main 本机实读: 【「板只改一次」那一趟的作业包 §0.2 ③ 板侧改动清单 + 预检清单 `B33_PIN_LAND_1P27` 里, 只有「land pitch 0.50→1.27mm」这一条, 【没有「钻孔 0.65→0.71」这一条】** ★
★**③ ⇒ ★★**那一趟开工时, 改孔这个动作【不在清单上】⇒ 不在清单 = 没人做 = 板投出去才发现排针插不进 ⇒ 【板改两次】** ★★**
★**④ 而那两条「板只改一次」的纪律恰恰是靠【清单齐不齐】来保证的** (★`HW/check_onepass_preflight_coverage.py` 的 P4 覆盖度判据就是逐条查「板侧改动清单每一项在清单页都有对应 item」★) ⇒ ★★**清单少一条 = P4 闸查不出来 = 纪律 ① 的执行体漏了一格** ★★

---

## ★★一 · 本单的地界事实 (★main 本机实读 · 逐条给了出处★) ★★

### ★★① ISS-387 查出的「改孔」这条板侧改动 (★逐字★) ★★

★**`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` L149 (★`pad_drill_vs_generic` 行★)**: ★
> ★`pad_drill` (钻孔) | ★**`Ø 0.71` (TYP)** ★`[官网]` | ★`0.65`** ★`[实测]` | ★★**不一致 (差 `0.06` mm, 通用件偏小)** ★★ | ★★**【板侧要改的一个动作】**: 孔径 `0.65 → 0.71` ⇒ ★**孔位 (排距/跨距) 不动 ⇒ MECH 全部余量数不动** (铜箔包络只看焊盘, 不看钻孔) ★★ ⇒ ★**但这一改是【板侧改板】, 必须与「板只改一次」那一趟同批** ★

★**main 本机独立复核 (★不是抄 ISS-387★)**: ★**本机 KiCad 库件 `Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 与 `.../PinHeader_1x02_P1.27mm_Vertical.kicad_mod` ⇒ 焊盘 `(size 1 1)` + 钻孔 `(drill 0.65)`** ⇒ ★★**⇒ `0.65` 确实是【盘上通用库件】的钻孔, 而 `0.71` 是 Samtec 官方推荐的 (`Ø 0.71 TYP`, 官网推荐 PCB 图 FIG 1 文字层逐字 `.028 0.71 (TYP)`) ⇒ ★**这两个数必须是【两处不同的来源】, 且【改孔动作必须进那一趟的清单】** ★★

### ★★② 「板只改一次」那一趟的板侧改动清单现在写了什么 (★main 本机实读★) ★★

★**`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L47 (★§0.2 ③ 那一行逐字★)**: ★
> ★**③** ★ | ★**`J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm (★E-1·实物排针落不进·main 18:4x 裁决: 按 1.27 定, 板 land 改★)** ★

★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` L63 (★item `B33_PIN_LAND_1P27` 逐字★)**: ★
> ★`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm (E-1 · 实测排针落不进 · main 11-17 18:45 拍死) | ★**S6** ★ | - | [实测] 板读 … ⇒ Δ pitch 0.77 ⇒ 实物 1.27mm 排针落不进; ★**E-1 裁决原文记的原始 land pitch = 0.50mm** …★ | ★`bash state/pcbnew_py.sh -c "import pcbnew;…"` ⇒ 期望读数: J_DEBUG land pitch = 1.27 / J_UART land pitch = 1.27★

★**main 本机实读结果 (★两条负面证据, 这就是本单的病灶★)**: ★
★**· `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 全文里, 【与 `J_DEBUG`/`J_UART` 相关的钻孔/孔径/`Ø` 一个字都没有】** (★grep `0.65` / `0.71` / `drill` / `钻孔` / `Ø` ⇒ 命中的全是别的器件 (★`Q1` 的 `Package_TO_SOT_SMD` / `J_USB_C` 的 NPTH `Ø0.650`/`Ø0.762` / S10 重出钻孔★) ⇒ ★**排针改孔这条不在预检清单里**★) ★
★**· `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 里 `0.71` 出现 0 次; `0.65` 只出现在 `J_USB_C` 的 NPTH 语境 (`Ø0.650`/`Ø0.762`) ⇒ ★**排针改孔这条也不在作业包 §0.2 ③ 里**★)

### ★★③ 覆盖度闸 P4 现在为什么查不出来 (★main 本机实读源码★) ★★

★**`HW/check_onepass_preflight_coverage.py` L233~L262 (ISS-343 加严段) 逐字**: ★
> ★★**病根**: 原 P4 只查「位号在不在清单里」+「来源单在不在全集里」⇒ ★**一条【不带新位号】的板改** (★同一个 `J_DEBUG`/`J_UART` 的 land pitch 从 0.50 改成 1.27★) ⇒ **天生查不出** ⇒ ★**P4 绿 = 假绿** ★ … ★**不许把 7 项写死成一个常量数组糊弄过去** ⇒ ★**7 项的【原文】从作业包现场解析** ★ … ★**覆盖判定 = 「绑定的清单 item 必须【真实存在】」+「绑定的 item 里必须能查到该子项的【覆盖令牌】」** ⇒ ★**作业包改了 (加子项/改子项/删子项/把零板改项改成板改) ⇒ 本判据当场红** ★

★**★`WP02_BINDING` 表 (★L254~L262★) 的 `③` 这一行**: ★`"③": (["B33_PIN_LAND_1P27"], [])` ★
★**★⇒ main 本机实读结论: P4 判的是【"作业包 §0.2 ③ 的 ③这一项 在清单页有对应 item `B33_PIN_LAND_1P27`"】⇒ ★**但【③ 这一项底下有几条子动作 (pitch 改 / 钻孔改 / 座体外形 / BOM 型号栏)】P4 完全不查 ⇒ ⇒ 【改孔这条子动作漏了, P4 照样绿】⇒ ★★**P4 绿 = 假绿 (第二次)** ★★**

---

## ★★二 · 本单要交 3 件 (★三件都要在盘 + 交卷页 B1~B6 齐全★) ★★

### ★★① ★新建★ 真相页 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` (★新建 · 纯分析 · 零写板★) ★★
★★**★★§0 一句话结论**: ★**落 `FTS` 时排针要改孔 `0.65 → 0.71`; 这一条【现在不在那一趟的作业包 §0.2 ③ 里, 也不在预检清单 `B33_PIN_LAND_1P27` 里】⇒ 必须补进同一批, 否则板改两次** ★★
★★**§1 两条数各自的出处** (★官方 `Ø0.71 TYP` 逐字 + 库件 `(drill 0.65)` 逐字 + 各自的 md5/路径 + 差 `0.06`★) ⇒ ★**证据分级: 官方那条 `[官网]`, 库件那条 `[实测]`** ★
★★**§2 「改孔」这条板侧动作的完整规格** (★改哪个 net/哪个 footprint 的哪条 drill / 改 0.65→0.71 / 【孔位 (排距/跨距) 不动】/ 【铜箔包络不动 ⇒ MECH 余量数不动】/ 只影响 `J_DEBUG` 与 `J_UART` 两件 / 与 `E-1` 的 pitch 改动是【同一个动作的两条腿】还是【两条独立动作】★) ⇒ ★**这一段是本单最要紧的: 【同批】的粒度要说清 (★是「同一次落表/重出」还是「同一次改板」★) ★**
★★**§3 现状差集表** (★逐条列: 「该改什么」/「现在登记在哪 (作业包 §0.2 ③ 的哪一条 / 预检清单的哪个 item)」/「缺的是哪一格」/「缺了会怎样」★) ⇒ ★★**必须逐条点名这 5 处 (★main 本机实读·你是自己写, 别只抄我这段★)★★**:
| ★#★ | ★该补在哪★ | ★现状★ | ★补的内容★ |
|---|---|---|---|
| ★1 ★ | ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §0.2 ③ 的 `③` 那一项 ★ | ★只写「land pitch 0.50→1.27mm」 ★ | ★**补上「钻孔 0.65→0.71」这一腿** (★**并说明它与 pitch 改动同属这一项, 不可只做其一★**) ★ |
| ★2 ★ | ★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` item `B33_PIN_LAND_1P27` 的描述列 ★ | ★只写 pitch + 期望读数 ★ | ★**补上 drill 期望读数** (★`J_DEBUG`/`J_UART` 各自改孔后的钻孔直径 ★) ★ |
| ★3 ★ | ★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` item `B33_PIN_LAND_1P27` 的【验收手段】列 ★ | ★给的是 `bash state/pcbnew_py.sh -c "…land pitch = …"` ★ | ★**补一条【读钻孔直径】的验收命令** (★★**照 ISS-387 的 `tmp/iss387/measure_generic_part.py` 形状写, 别自己编★**) ★ |
| ★4 ★ | ★`HW/check_onepass_preflight_coverage.py` 的 `WP02_BINDING["③"]` 覆盖令牌 ★ | ★`("③": (["B33_PIN_LAND_1P27"], []))` ⇒ **零个覆盖令牌** ★ | ★★**★本单【不许改这个闸】(★它已签收·`钉板闸④`·挂进门禁链★) ⇒ 只在 §4 登记「需要加什么覆盖令牌」+ 落 `needs_from` to=main ⇒ ★★不许自己动它★★ ★** |
| ★5 ★ | ★`HW/BOM_v1.csv` L71 / L77 (★`J_DEBUG` / `J_UART` 两行的 `opn`/`footprint` 栏★) ★ | ★都是「待定」 ★ | ★**登记: ISS-387 已给出候选值 (`FTS-104-01-F-S` / `FTS-102-01-F-S` + land + 偏离登记), 但【落表是那一趟的动作】⇒ 本单零落表 ⇒ 只登记「那一趟要落的栏位与值」** ★ |
★★**§4 「要 main 落什么」的登记表** (★逐条: 哪个文件 / 哪个位置 / 要写什么 / 谁落 / 为什么本单不落 (★零改已签收件/零落表★)★) ⇒ ★★**这是本单的交卷主体: main 拿这一节就能一次落干净, 不用再回头查** ★★
★★**§5 与 `E-1` 的关系**: ★**pitch 0.50→1.27 与 drill 0.65→0.71 是【同一项 `③` 的两条腿】(★结论 + 依据 + 若只做其一会怎样★) ★** ★★**★这一条是本单的核心判断, 你必须自己给结论并给依据 (★不许含糊成「建议一起做」★) ★★**
★★**§6 对 MECH 侧的影响面**: ★**逐条点名哪些数【不动】(`4.8100`/`2.2700`/`6.6100`/`4.0700`/`0.1350`/`2.6950`/`0.7700`/`OI-5` 三档 `1.7750`/`4.0850`/`4.8100`·★**因为钻孔不进铜箔包络★**) ⇒ ★**★这一段是「结构件不必因此再返工一次」的机器可核依据★ ★**
★★**§7 复跑命令 + 机器块** (★机器块必须含: 两处数值与各自出处 / 差集 5 条的逐条定位 / 「同批粒度」结论 (三值: 同一项两腿 / 两条独立动作 / 待定) / `*_decision` 字段全是 `not_decided_here`★)

### ★★② 新建机器闸 `HW/check_fts_land_drill_same_batch.py` (★新建 · 零挂链 ★) ★★
★**零挂链** (★`grep -c check_fts_land_drill_same_batch state/gate_check.py` 必须 = 0 · ★挂链是 main 的地界★) ★
★**判据 (★fail-closed · 每条都要有反向用例★)**:
| 判据 | ★判什么★ |
|---|---|
| ★**D1** ★ | ★**改孔这一条板侧动作, 必须能在【作业包 §0.2 ③ 的 `③` 那一项原文】里查到** (★★**不许写死成一个常量数组糊弄过去 ⇒ 必须【现场解析作业包原文】★★⇒ ★与 ISS-343 对 P4 的纪律同一条★) ★ |
| ★**D2** ★ | ★**同理, 必须能在【预检清单 `B33_PIN_LAND_1P27` 的描述列】里查到** ⇒ ★**不许只查作业包 (★两处都要, 少一处 = 那一趟照样漏★) ★ |
| ★**D3** ★ | ★**`B33_PIN_LAND_1P27` 的【验收手段】列里必须有一条【读钻孔直径】的验收命令** ⇒ ★**缺 ⇒ 判红 (★理由: 没有验收手段 = 改没改成没人知道★) ★ |
| ★**D4** ★ | ★**两端数字必须自洽**: 真相页机器块里登记的 `drill_official` / `drill_generic` / `drill_target` 三者, 必须满足 ★**`drill_target == drill_official`** 且 ★**`drill_target != drill_generic`** 且 ★**`drill_generic` == 本机库件实测值 (`0.65`)★** ⇒ ★**任一不成立 ⇒ 判红** (★★**这一条是防「真相页自己写错了目标值」的护栏★★) ★ |
| ★**D5** ★ | ★**影响面**: 机器块里必须列出【MECH 侧不受影响的数名清单】(★从真相页 §6 机器块读, 不许写死★) ⇒ ★**空 ⇒ 判红** (★理由: 「结构件不必返工」这条结论没有落点 = 没算过★) ★ |
| ★**D6** ★ | ★**零扰动**: 板三项指纹未动 + 零落表 (网表/脚表/BOM md5 同基线) + ★**零挂链** + ★**已签收闸 md5 同基线** (★含 `HW/check_onepass_preflight_coverage.py`★) ★ |
| ★**D7** ★ | ★**本闸自己环境无关** (★沙盒落项目盘 · 两个不同深度读数必须一致★) ⇒ ★★**你自己就是执行环境一致性的人 ⇒ 你自己环境敏感 ⇒ 这条判据就没人信★★ ★★ |
★★**★`--selftest` ≥ 8 条反向用例**, ★**至少 4 条专打上面 4 条判据**: ★**① 把作业包 §0.2 ③ 里的「钻孔」两个字删掉 (★在沙盒副本上★) ⇒ 必须 D1 红** ★ **② 把 `B33_PIN_LAND_1P27` 描述列里的钻孔字样删掉 ⇒ 必须 D2 红** ★ **③ 把 `B33_PIN_LAND_1P27` 验收手段列里那条读钻孔的命令删掉 ⇒ 必须 D3 红** ★ **④ 把机器块里的 `drill_target` 改成 `0.65` (= 通用件值) ⇒ 必须 D4 红** ★★**★反向用例必须自证「红的是目标那一条, 其余仍绿」★ ★★
★★**★★必踩的坑 (★main 本机实测★)★★**: ★★**D1/D2 这两条【现场解析】的实现方式, 有两条路, 你必须自己选一条并说清: (甲) 【读真文件】⇒ 改文件就红 (★ISS-343 的做法·★优点=改了就红★) ; (乙) 【读环境变量指定的副本】⇒ 只在自测里能验 (★★**但那样【真实盘上的清单缺了】这件事就【测不出来】★★ ⇒ ⇒ ★★**本单【必须用 (甲)】★★ ⇒ ★★**★且 (甲) 的实现【不许破坏真文件】⇒ 你的 `--selftest` 必须在【沙盒副本】上改, 改完还原, ★★**跑完自测后必须复验真文件 md5 未变★ ★★ ★★**

### ★★③ 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md` (★新建★) ★★
★**B1~B6 六段齐全** (★**`state/gate_check.py` 的 `pick_handoff` 取最新一份评分; ★若最新一份自称 B 块结构但缺块 ⇒ 【不许回退】⇒ 真倒退 ⇒ Q1 立刻掉★ ⇒ ★★**你这份一旦自称 B1~B6, 六段就必须真齐全, 不许缺一块★★ ★★)
★★**★B1~B6 的标题必须含 gate_check.py 认的关键词 (★main 本机实读 `state/gate_check.py` L47~L54 的 `REQUIRED_BLOCKS`★)★★ ★★
| 块 | ★标题里必须出现★ |
|---|---|
| B1 | ★`结论摘要` (或 `结论` / `一句话`) ★ |
| B2 | ★`验收标准自评` (或 `自评` / `验收标准`) ★ |
| B3 | ★`证据分级` (或 `证据等级` / `证据`) ★ |
| B4 | ★`接口取值声明` (或 `接口声明` / `interface_claims` / `接口请求`) ★ |
| B5 | ★`未决项` (或 `卡点` / `阻塞` / `待办`) ★ |
| B6 | ★`自证复现命令` (或 `复现` / `复现命令` / `自证`) ★

---

## ★★三 · 分片 ★★
★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ★
★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main`)★** ★
★★**★`needs_from` 必须逐条写清「要谁回答什么 + 代价」, 不许只写「请裁决」★** ★
★★**★本单至少要有这三条 need (★照抄底稿即可·★你可以在此基础上补★)★★ ★★
★**① §4 那 5 处补登记谁落 (★其中【作业包 §0.2 ③】与【预检清单 `B33_PIN_LAND_1P27`】是【已签收件】· 【`HW/check_onepass_preflight_coverage.py` 的 `WP02_BINDING["③"]` 覆盖令牌】是【已签收闸】· 【BOM L71/L77】要落表 ⇒ ★★**这四处全是 main 地界 ⇒ 归 main** ★★ ⇒ ★★**代价: 不落 ⇒ 那一趟开工时改孔不在清单 ⇒ 板投出去才发现排针插不进 ⇒ 【板改两次】(★2-4 周 + 一批板的钱·★ISS-387 已算过同量级的代价★)★** ★★ ★
★**② 「pitch 改 + 钻孔改 是不是同一项的两条腿」这个判断归谁拍 (★本单会给结论 + 依据, 但【同批粒度】是 main 的口径★ ⇒ ★**归 main** ★★ ⇒ ★★**代价: 不拍 ⇒ 两处清单可能各写一条 ⇒ 那一趟的执行清单出现两条可分开的动作 ⇒ 有人只做其一时, 没有任何机器判据能发现★ ★★ ★
★**③ `J_DEBUG`/`J_UART` 的 BOM `opn`/`footprint` 两栏 (★BOM L71/L77·★现值「待定」·★ISS-387 已给候选值 + 偏离登记★) 归谁落表 ⇒ ★**归 main** ★★ ⇒ ★★**代价: 不落 ⇒ 落 FTS 那一刻封装来源与 BOM 型号栏不同源 ⇒ 同源纪律破 (★ISS-387 的 `OI-387-3` 已算过: 投板后才发现 ⇒ 2-4 周返工★)★** ★★ ★
★★坑 (★main 本机实测过的★) ★★**: ★**`state/frag_write.py --add-*` 的分隔符是【空格】不是【分号】** (★`shlex.split()` 切参数 ⇒ 写成 `path=…;summary=…` 会把整串吞进 `path` ⇒ **写出畸形条目却照样打印「✅ 已原子更新」**★) ⇒ ★**写完必须 `grep` 复验条目唯一, 不许只信它打印的那行** ★

---

## ★★四 · ★★本单必跑的坑 (★main 本机实测踩过, 你不要重踩★) ★★

★★**坑 1 ★★ 「先验证后写盘」是上一趟的死法** ⇒ ★**【每一件交付物: 先 write 落盘, 再跑它】⇒ 绝不许攒完所有验证再一次性写★** ★
★★**坑 2 ★★ 沙盒必须落项目盘** ⇒ ★**不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★** ★
★★**坑 3 ★★ 本单是【改文档的单】, 不是【只读的单】** ⇒ ★★**你改的是【新页 + 新闸】; 但【作业包 / 预检清单 / 覆盖度闸 / BOM / 板 / 网表 / 脚表】一个都不许你改 (★前三个是已签收件, 后三个是那一趟的动作★) ⇒ ★★**你要做的是【把该改的写成【给 main 的登记】+【一个能查出「没改」的机器闸】】, 不是【自己改】★★ ★★ ★
★★**坑 4 ★★ 别为了「让闸变绿」去改基线** ⇒ ★**「板只改一次」铁律: 板 md5 当天变更是【合法】的 (走合法改板通道) ⇒ 那 2 道「钉板 md5 闸」当天转红是【正常】⇒ ★★但【绝不许】为了「让闸变绿」去改板 / 改闸里的基线 / 放宽判据 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★★ ★★** ★★**正确做法: 读那道红闸的详情, 按【合法改板通道】落台账, 让判决源跟着板走★** ★
★★**坑 5 ★★ 「板 mtime 变了」这种告警要看清楚是谁的板** ⇒ ★★**你跑闸时若看到 `板 mtime=2026-11-24 … ≠ 基线`, 先确认那是【沙盒副本】还是【真板】⇒ ★★**真板 mtime 仍是 `2026-11-06 07:07:17.362193413`·★别去追一个不存在的「板被写过」★★ ★★**

---

## ★★五 · 必跑命令 (★全部实测存在的真命令 ★· 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ① 命令存在性守卫 (★派活前 main 已跑过 rc=0, 你开工再跑一遍★)
python3 state/check_brief_commands.py

# ② ★★本单的地界事实: 你要先自己复核, 不许只抄本 brief★★
sed -n '149p' HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md   # ★ISS-387 的 pad_drill 行★
sed -n '47p' HW/PCB/BOARD_ONEPASS_WORKPACKET.md                    # ★§0.2 ③ 板侧改动清单★
sed -n '63p' HW/PCB/BOARD_ONEPASS_PREFLIGHT.md                     # ★item B33_PIN_LAND_1P27★
grep -n "WP02_BINDING" -A 10 HW/check_onepass_preflight_coverage.py
grep -o "(drill [0-9.]*)" /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod
grep -n "0\.65\|0\.71\|钻孔\|drill" HW/PCB/BOARD_ONEPASS_PREFLIGHT.md   # ★确认排针改孔确实不在清单里★

# ③ 本单新闸 (★你自己写的★)
python3 HW/check_fts_land_drill_same_batch.py
python3 HW/check_fts_land_drill_same_batch.py --selftest

# ④ 既有闸 (★只读对照, 不许改★)
python3 HW/check_onepass_preflight_coverage.py
python3 HW/check_fts_single_row_land_truth.py --selftest
python3 HW/check_juart_land_fit.py

# ⑤ 板读 (★照 ISS-387 的形状, 自己写一个读钻孔的★)
bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetParent().GetReference(),p.GetDrillSize().x) for f in b.GetFootprints() if f.GetReference() in ('J_DEBUG','J_UART') for p in f.Pads()])"

# ⑥ 板 / 三表 指纹 (★开工前后各打一次★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑦ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/frag_write.py --agent hw-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

★★**基线 (★main 2026-11-24 11:2x~11:4x 本机实跑, 你自己再核一遍★) ★★**
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
网表 6aee500e60ba0732f83a9cf557ba90ab · 脚表 9174309df1ec9411ac8e8d9e80ee386a · BOM 5b9993992405904a60ac96a020b375d8
state/gate_check.py md5 = 5f370bb8cf828473e70ccc5d6412da98 · merge.py = c9191025020fefd9b475e2573a335815 · frag_write.py = 3b383a52b4fa540f1d16a2c6f3811de8
merge.py      ⇒ rc=0 (产出 839 | 阻塞 43 | 冲突 0)
gate_check.py ⇒ rc=0 (【Q1】18/18 · 【Q7】钉板 md5 闸链 10/10 · 缺口 3 条)
★已签收件 (★本单零改, 收尾时逐个 md5 复验★):
  HW/PCB/BOARD_ONEPASS_WORKPACKET.md · HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
  HW/check_onepass_preflight_coverage.py · HW/check_fts_single_row_land_truth.py
  HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md · HW/BOM_v1.csv (L71/L77 不许动★)
★可复用的既有测钻孔脚本 (★在盘, 直接用, 别重写★): tmp/iss387/measure_generic_part.py
```

---

## ★★六 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同 (★**含 BOM L71/L77 两行的 `opn`/`footprint` 栏不许动★**) ★ |
| ★零改既有闸★ | ★`HW/check_onepass_preflight_coverage.py` / `HW/check_fts_single_row_land_truth.py` md5 与基线同★ (★**含 `WP02_BINDING` 不许动★**) |
| ★零改既有页面正文★ | ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` md5 与基线同★ (★**补登记只写在你的新页 §4 + needs_from, 不落进这些文件★**) |
| ★零挂链★ | ★`grep -c check_fts_land_drill_same_batch state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机; ★`state/outbox/` 一个字节未动; ★**零邮件/零询价/零问询/零采购**★ |
| ★不代拍★ | ★★**那 5 处补登记归谁落 / 「同批粒度」是同一项两腿还是两条独立动作 / BOM 两栏落什么 —— 全是 main 的裁决权 ⇒ ★★你只摆证据与代价, 不写「应该 X」★★ ⇒ ★机器块里要有 `*_decision = not_decided_here` 这类字段★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/hw.yaml`★ |
| ★沙盒纪律★ | ★只落 `tmp/iss391_sbx/` 与 `logs/iss391/`; ★不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ |
| ★证据分级★ | ★每条结论标五级之一★ |
