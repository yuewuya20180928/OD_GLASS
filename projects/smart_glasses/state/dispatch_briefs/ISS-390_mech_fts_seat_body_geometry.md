# ISS-390 · mech-lead · `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官网查证 + 「通用库件 courtyard 被当成厂件」这条前提订正 + 降级方案 · 零写板 · 零落表

★**本单性质**: ★**纯查证 + 纯分析 + 新建闸 + 作业包 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【结构侧真值层】· 纯查证不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★
★★**★本单为什么必须做 (★main 本机实读 · 不抄任何 agent 报告★) ★★** ★★

★**① ISS-387 (★hw-lead · 今日 11:1x 已交卷★) 把一条【结构侧必须知道、但至今是 `[0数据]`】的数留在了明处**: ★**`FTS` 直插档的【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官方尺寸 = `[0数据]`** ★
★**② 同一单还实测出: MECH 整条 3D 判决链吃的 `4.8100` / `2.2700` / `F.CrtYd 6.0900` / `F.Fab 5.0800` ★全是【盘上通用 KiCad 库件】的数, 不是厂件的数** (★Samtec 直插档 FIG 1 的文字层一共只有 4 个标注, 【没有座体外形标注】★) ★
★**③ ⇒ 而 ISS-389 (★你 30 分钟前交的那份改件要求单★) 的 `OI-12` 结构侧答复里, 把 `6.0900` 写成了「★官方 land courtyard★」** ⇒ ★★**那是一个前提错误: 它拿通用件的 courtyard 当厂件的 courtyard 去比 ⇒ 「判据偏紧 `0.5200`」这个结论的对照物是错的 ⇒ 厂件外形一旦补上, 这个结论必须重算** ★★
★**④ ISS-387 的真相页【已经把这条活指派给你了】**: `OI-387-4: FTS 直插档座体外形 (宽/深) 官方尺寸 = [0数据] ⇒ 走 §6-④ 降级 (官网 3D/CAD 下载 或 实测样件) ⇒ to=mech-lead` ⇒ ★★**⇒ 本单就是去把这条 `[0数据]` 变成一个有证据等级的数 (或一条写死的降级方案), 并把 ③ 的前提订正掉** ★★

---

## ★★一 · 本单的地界事实 (★main 本机实读 · 逐条给了出处★) ★★

### ★★① `6.0900` / `5.0800` 是【通用件】的数, 不是厂件的数 ★★

★**ISS-387 真相页 `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` L154 (逐字)**: ★
> ★`keepout_dwg` | 来源已知 (打印件 + 官网 3D 下载); ★**直插档外形尺寸 `[0数据]`** ★ | ★`F.CrtYd` `3.100 × 6.090` / `3.100 × 3.550`; `F.Fab` 体 `2.100 × 5.080` / `2.100 × 2.540` ★**[实测]** | ★**通用件的 courtyard 不是厂件 keepout** ★ | ★**MECH §3 用的 `F.CrtYd 6.0900` / `F.Fab 5.0800` 就是这个通用件的数** ⇒ ★**OI-12 (判据要求的清空区 `6.6100` 比 courtyard 还大 `0.5200`) 这个「偏紧」结论, 也是拿通用件的 courtyard 比的 ⇒ ★**换成厂件后 courtyard 变了, 这个结论要重算** ★

★**main 本机独立复核 (★不是抄 ISS-387★)**: `MECH/check_debug_seat_3d_fit.py` **L848** 与 **L879** 两行都写着「★而★**官方 land** 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200★」 ⇒ ★★**⇒ 前提错误已经从【ISS-389 的答复页】扩散到【MECH 闸的源码字符串】里了 ⇒ 本单必须把这两处一起点名** ★★

★**main 本机独立复核 (★通用件到底是谁★)**: 本机 KiCad 库件 `Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 与 `.../PinHeader_1x02_P1.27mm_Vertical.kicad_mod` ⇒ 焊盘 `(size 1 1)` + 钻孔 `(drill 0.65)` ⇒ ★★**⇒ `6.0900` / `5.0800` 的来源 = 这两个库件的 `F.CrtYd` / `F.Fab` (第三方库件 / IPC 口径), 与 Samtec 无关** ★★

### ★★② ISS-389 的 `OI-12` 答复原文 (★你交的那份·逐字★) ★★

★**`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` L634 (机器块 `OI-2`/`OI-12` 的 `structural_answer` 字段)**: ★
> ★「硬差额: 判据要求每边 0.9000, ★**官方 land courtyard 只给每边 0.6400** (J_DEBUG F.CrtYd 6.0900 vs 铜箔 4.8100; J_UART 退包络 3.5500 vs 铜箔 2.2700) => 每边差 0.2600, 清空区 X 总宽差 0.5200 (6.6100-6.0900 / 4.0700-3.5500). 路 A 判据不动 => 清空区 X 6.6100/4.0700, 每边比座体本体多让 0.7650/0.7150, 不改任何既有判据页, 代价是镜脚内腔变大+罩外观缝变大+工装按内腔走. 路 B 判据改名义余量口径 => 清空区 X 6.0100/3.4700, J_DEBUG 的 6.0100 比 courtyard 6.0900 还小 0.0800 反常消失, 代价是 FDM ±0.3000 公差不再扣除 (实际余量只剩 0.3000) 且本页 §1~§4 全部余量要重算, 且 J_UART 的 3.4700 正好等于 ISS-377 DP-1 那个数 (OI-14 同时消掉)」

★**⇒ ★★「官方 land courtyard」这 6 个字是本单的【订正对象】★★** (★**但注意: 数值本身没算错 —— 错的是【对照物是谁】的定性★) ★★

### ★★③ ISS-387 §6-④ 已经写好的两条降级路径 (★你照着走, 不许另造★) ★★

★**`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` L239 (逐字)**: ★
> ★**降级路径 (两条, 按优先级)**: ★**(甲)** 官网单品页的 **3D 模型 / CAD 下载** (官网「2D view may not be representative… 请以 3D preview 或 CAD download 为准」那段免责文字本身, 就说明官网有 3D/CAD 下载件) ⇒ ★**用它量座体外形 (宽 X / 深 Y / 高 Z) 补 `keepout_dwg`**; ★**(乙)** **实测样件复现路径**: 落 FTS 时先打一块单板样, 用卡尺量【座体宽 X / 座体深 Y / 绝缘体高 Z】三个量, 回填 `keepout_dwg` ⇒ ★**这两条都不许写成「等原厂回信」/「待外部确认」** ★

★**⇒ ⇒ 【路径 (甲) 是本单的主动作】(★自己上官网查, ★★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★★) ⇒ 【路径 (乙) 是路径 (甲) 查不到时的降级】(★写清【落 FTS 时先打一块单板样, 卡尺量哪三个量、量完填回哪一格】★) ★★**

★**★已知的环境事实 (★main 本机实测, 免得你白试★) ★★**: ★**`www.samtec.com` 在本机一律返回 HTTP 429 (Cloudflare error 1015 rate_limited) —— `curl` 与 `web_fetch` 各试 5 次 (含 30s/60s 退避) 全部被挡 ⇒ 单品页 / 家族页 / 孔径表这三类【网页文字】是通过搜索后端 (★tavily★) 取到的 ⇒ 证据等级记 `[官网]` (内容出自 Samtec 官网) 但【来源通道】记等价通道, 可复核性靠 URL 留档** ⇒ ★★**但两份 PDF (`suddendocs.samtec.com` 的 FTS 目录页 + 官方推荐 PCB 图打印件) 是本机 `curl` 直连取得的 (HTTP 200, 有 md5) ⇒ ★★**你要找的 3D/CAD 下载件大概率也在 `suddendocs.samtec.com` 域下 ⇒ 优先试那条直连通道** ★★

---

## ★★二 · 本单要交 3 件 (★三件都要在盘 + 交卷页 B1~B6 齐全★) ★★

### ★★① 新建真相页 `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` (★新建·纯分析·零写板★) ★★
★★**★★§0 一句话结论**: ★**`FTS` 直插档座体外形 (宽 X / 深 Y / 绝缘体高 Z) 现在是多少 (或按哪条降级路走) + 现有 `6.0900`/`5.0800` 是谁家的数 + 因此 `OI-12` 的 `0.5200` 结论要不要重算** ★★
★★**§1 官网查证过程** (★每个 URL + 每个字节数/md5 + 取得方式 (直连/搜索后端) + HTTP 状态码★) ⇒ ★**不许写「官网打不开」就交差**
★★**§2 座体外形三量表** (★宽 X / 深 Y / 绝缘体高 Z·**逐项标 `[官网]` / `[媒体]` / `[推算]` / `[0数据]`**★) ⇒ ★**查不到就写 `[0数据]` + 走 §3 降级, 不许留空, 不许写「待原厂回信」**
★★**§3 降级方案** (★路径 (甲) 查不到时的路径 (乙) 全文: ★**落 FTS 时先打一块单板样, 卡尺量【座体宽 X / 座体深 Y / 绝缘体高 Z】三个量, 回填 `keepout_dwg`**★ ⇒ ★**写成【谁在什么时候量哪三个量、量完填回哪一格】的可执行动作, 不是一句「实测」**)
★★**§4 前提订正表** (★逐条列: 哪一页/哪一行的哪个说法要改成什么措辞★) ⇒ ★**最少覆盖这 4 处**:
| ★位置★ | ★现在的说法★ | ★订正成什么★ |
|---|---|---|
| ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` L634 (`OI-12` 的 `structural_answer`) ★ | ★「★官方 land courtyard★ 只给每边 0.6400」 ★ | ★「★通用 KiCad 库件 (★`PinHeader_1x0{4,2}_P1.27mm_Vertical`★) 的 `F.CrtYd` 只给每边 0.6400」 + ★补一句「厂件 courtyard 未取得 ⇒ 见 §3 降级」★ |
| ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` L149 / L154 (正文「路径 B」段) ★ | ★「比 courtyard `6.0900` 还小 `0.0800`」/「courtyard 给的每边余量 `0.6400`」 ★ | ★同上加限定语 (★**数值不改, 只改定性★**) ★ |
| ★`MECH/check_debug_seat_3d_fit.py` **L848** ★ | ★「★而★**官方 land** 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ …」 ★ | ★**源码字符串里的定性也要订正** ⇒ ★★**但本单【不许改这个闸】(★它已签收★) ⇒ 只在 §4 登记「该字符串需订正」+ 落 `needs_from` to=main ⇒ ★★不许自己动它★★ ★ |
| ★`MECH/check_debug_seat_3d_fit.py` **L879** ★ | ★「★事实: ★**官方 1x4 THT** 的 F.CrtYd 只有 6.0900 X, …」 ★ | ★同上 ★ |
★★**§5 影响面**: ★**若厂件外形 ≠ 通用件外形 ⇒ `6.6100` / `4.0700` / `0.1350` / `2.6950` / `0.7700` / `OI-5` 三档 `1.7750`/`4.0850`/`4.8100` 这几个数里, 有几个会跟着变, 有几个不会 ⇒ 逐个说清 (★**这是本单最值钱的一段**)**
★★**§6 与 `OI-11` / `OI-12` / `OI-13` / `OI-14` 的关系**: ★**逐条说明「本单的结果会让哪条 OI 的哪一侧代价发生变化 / 不变」** ⇒ ★**`OI-11` (座体真实高 `h` = `[0数据]`) 与本单的关系要说清: `h` 是 Z 向, 本单查的是 X/Y/Z 三个量 ⇒ 能不能顺带解决 `h`? 解决不了就明说** ★
★★**§7 复跑命令 + 机器块** (★机器块必须含: 三量 (或 `[0数据]` + 降级 id) · 对照物是谁 (通用件 vs 厂件) · `OI-12` 结论是否需重算 (三值: 不需/需/待定) · 三个 `*_decision` 字段全是 `not_decided_here`★)

### ★★② 新建机器闸 `MECH/check_fts_seat_body_geometry.py` (★新建·零挂链★) ★★
★**零挂链** (★`grep -c check_fts_seat_body_geometry state/gate_check.py` 必须 = 0 · ★挂链是 main 的地界★) ★
★**判据 (★fail-closed · 每条都要有反向用例★)**:
| 判据 | ★判什么★ |
|---|---|
| ★**G1** ★ | ★真相页机器块存在且三量 (宽 X / 深 Y / 绝缘体高 Z) **逐项有值或明确 `[0数据]`** ⇒ ★**不许缺项/空串** ★ |
| ★**G2** ★ | ★**每项证据等级 ∈ 五级白名单** (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ⇒ ★**且 `[0数据]` 的每一项都必须能在一份【降级方案表】里查到自己的降级 id** ⇒ ★**不许「0数据但没降级」** ★ |
| ★**G3** ★ | ★**对照物定性**: 机器块里必须显式写明 `6.0900` / `5.0800` / `3.5500` / `2.5400` 是★**通用库件**★的数 (★`source = generic_kicad_lib` 之类★) ⇒ ★**不许出现「官方 land courtyard / 官方 1x4 THT」这种把通用件说成厂件的措辞 (★扫本单真相页 + ISS-389 页 + 既有 MECH 闸源码里的这几处字符串★) ⇒ ★**判红并点名是哪一处** ★ |
| ★**G4** ★ | ★**订正登记**: §4 的 4 处订正必须**逐条登记** (★哪一行 / 原措辞 / 新措辞 / 状态 `待 main 落`★) ⇒ ★**4 处缺一条即红** ⇒ ★**这样 main 签收时一眼知道还差哪几处没落** ★ |
| ★**G5** ★ | ★**影响面**: 机器块里 `OI-12` 的结论状态必须是三值之一 (★`不需重算` / `需重算` / `待定`★) ⇒ ★**且若为 `需重算` ⇒ 必须列出受影响的数名清单 (★从 §5 机器块读, 不许写死★) ⇒ ★**不许空** ★ |
| ★**G6** ★ | ★**零扰动**: 板三项指纹未动 + 零落表 (网表/脚表/BOM md5 同基线) + ★**零挂链** ★ |
| ★**G7** ★ | ★**本闸自己环境无关** (★沙盒落项目盘 · 两个不同深度读数必须一致★) ⇒ ★★**你自己就是执行环境一致性的人 ⇒ 你自己环境敏感 ⇒ 这条判据就没人信★★ ★★ |
★★**★`--selftest` ≥ 8 条反向用例**, ★**至少 4 条专打上面 4 条定性判据**: ★**① 把 `6.0900` 的 `source` 从 `generic_kicad_lib` 改成 `samtec_official` ⇒ 必须 G3 红** ★ **② 删掉 §4 订正表里的一处 ⇒ 必须 G4 红** ★ **③ 把某一项的证据等级改成六级之外的词 ⇒ 必须 G2 红** ★ **④ 把 `[0数据]` 项的降级 id 删掉 ⇒ 必须 G2 红** ★★**★反向用例必须自证「红的是目标那一条, 其余仍绿」★ ★★
★★**★必踩的坑 (★main 本机实测★)★**: ★**沙盒临时目录必须落【项目盘】(★`tmp/` 下面★) 且深度要能被 `__file__` 反推对 ⇒ ★**不许依赖系统 `/tmp` 的深度** ⇒ ★**最稳的写法: 沙盒路径从【本闸自己的 `ROOT`】推出来, 而不是从 `tempfile.gettempdir()`** ★★

### ★★③ 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md` (★新建★) ★★
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
★**① §4 那 4 处定性订正谁落 (★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` L634/L149/L154 + `MECH/check_debug_seat_3d_fit.py` L848/L879★) ⇒ ★**归 main** ★★(★本单零改既有页/零改既有闸 ⇒ 只登记, 不代落★) ⇒ ★**代价: 不落 ⇒ 「官方 vs 通用件」的前提错误继续留在页上与闸的源码字符串里 ⇒ 老板/下一个读这页的人会拿错对照物做结构判决** ★★ ★
★**② 厂件座体外形若最终只能走降级 (乙) (实测样件卡尺) ⇒ 【打样件】这件事归谁排期 / 归谁出量 ⇒ ★**归 main + boss** ★★(★路径 (乙) 有一道前置: 【落 FTS 时先打一块单板样】⇒ 这是投板前的一次额外动作, 不打样就永远拿不到 Z 向的 `h` ⇒ `OI-11` 就永远 `[0数据]`★) ★★ ★
★**③ `OI-12` (判据对 THT 排针是否过严) 与 `OI-14` (ISS-377 `DP-1` 的 `3.4700` 订正为 `4.0700`) 必须一起拍 (★本单 §6 会给出各自的前置状态★) ⇒ ★**归 main** ★★(★ISS-389 已写明「两条必须一起拍」★) ⇒ ★★ ★
★★坑 (★main 本机实测过的★) ★★**: ★**`state/frag_write.py --add-*` 的分隔符是【空格】不是【分号】** (★`shlex.split()` 切参数 ⇒ 写成 `path=…;summary=…` 会把整串吞进 `path` ⇒ **写出畸形条目却照样打印「✅ 已原子更新」**★) ⇒ ★**写完必须 `grep` 复验条目唯一, 不许只信它打印的那行** ★

---

## ★★四 · ★★本单必跑的坑 (★main 本机实测踩过, 你不要重踩★) ★★

★★**坑 1 ★★ 「先验证后写盘」是上一趟的死法 (★ISS-389 cont1 就死在这★)** ⇒ ★**【每一件交付物: 先 write 落盘, 再跑它】⇒ 绝不许攒完所有验证再一次性写★** ★
★★**坑 2 ★★ 沙盒必须落项目盘** ⇒ ★**不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★** ★
★★**坑 3 ★★ 查官网卡住时** ⇒ ★**先换通道 (`suddendocs.samtec.com` 直连 / 搜索后端), 再走降级 (乙) ⇒ ★★**不许把「查不到」写成阻塞项挂着**, 不许写「等原厂回信」** ★★
★★**坑 4 ★★ 别为了「让闸变绿」去改基线** ⇒ ★**「板只改一次」铁律: 板 md5 当天变更是【合法】的 (走合法改板通道) ⇒ 那 2 道「钉板 md5 闸」当天转红是【正常】⇒ ★★但【绝不许】为了「让闸变绿」去改板 / 改闸里的基线 / 放宽判据 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★★ ★★** ★★**正确做法: 读那道红闸的详情, 按【合法改板通道】落台账, 让判决源跟着板走★** ★
★★**坑 5 ★★ 本单是【纯查证】, 不是一个「实测」单** ⇒ ★**你手上没有实物样件 ⇒ 路径 (乙) 是【写给将来的动作】, 不是【你今天能做的测量】⇒ ★★**不许把路径 (乙) 写成你已经测到的数★ ★★**

---

## ★★五 · 必跑命令 (★全部实测存在的真命令 ★· 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ① 命令存在性守卫 (★派活前 main 已跑过 rc=0, 你开工再跑一遍★)
python3 state/check_brief_commands.py

# ② ★★本单的地界事实: 你要先自己复核, 不许只抄本 brief★★
sed -n '154p' HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md     # ★通用件 vs 厂件 keepout★
sed -n '239p' HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md     # ★§6-④ 两条降级路径★
sed -n '634p' MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md         # ★OI-12 结构侧答复原文★
sed -n '848p;879p' MECH/check_debug_seat_3d_fit.py                  # ★闸源码里那两处「官方 land」★
grep -o "(drill [0-9.]*)" /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod

# ③ ★★官网查证 (★自己上官网, 不许外发·不许等人回信★★)
curl -sS -o tmp/iss390_sbx/fts_catalog.pdf -w '%{http_code} %{size_download}\n' https://suddendocs.samtec.com/catalog_english/fts.pdf
curl -sS -o tmp/iss390_sbx/fts-1xx-xx-xx-dx-xx-footprint.pdf -w '%{http_code} %{size_download}\n' https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf
pdftotext -layout tmp/iss390_sbx/fts-1xx-xx-xx-dx-xx-footprint.pdf - | head -60
# ★★3D/CAD 下载件: 优先试 suddendocs 域下的直链; 单品页若 429 ⇒ 换搜索后端取文字 + URL 留档★★

# ④ 本单新闸 (★你自己写的★)
python3 MECH/check_fts_seat_body_geometry.py
python3 MECH/check_fts_seat_body_geometry.py --selftest

# ⑤ 既有 MECH 闸 (★只读对照, 不许改★)
python3 MECH/check_debug_seat_3d_fit.py
python3 MECH/check_debug_seat_rework_spec.py --selftest

# ⑥ 板 / 三表 指纹 (★开工前后各打一次★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑦ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/frag_write.py --agent mech-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

★★**基线 (★main 2026-11-24 11:2x~11:4x 本机实跑, 你自己再核一遍★) ★★**
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
网表 6aee500e60ba0732f83a9cf557ba90ab · 脚表 9174309df1ec9411ac8e8d9e80ee386a · BOM 5b9993992405904a60ac96a020b375d8
state/gate_check.py md5 = 5f370bb8cf828473e70ccc5d6412da98 · merge.py = c9191025020fefd9b475e2573a335815 · frag_write.py = 3b383a52b4fa540f1d16a2c6f3811de8
merge.py      ⇒ rc=0 (产出 839 | 阻塞 43 | 冲突 0)
gate_check.py ⇒ rc=0 (【Q1】18/18 · 【Q7】钉板 md5 闸链 10/10)
★已签收件 (★本单零改, 收尾时逐个 md5 复验★):
  MECH/check_debug_seat_3d_fit.py · MECH/check_debug_seat_rework_spec.py · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md
  MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md · HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md
★可复用的既有 PDF (★在盘, 直接用, 别重下★): tmp/iss387/fts_catalog.pdf · tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf
  ★★(★若 tmp/iss387/ 已被清 ⇒ 从 suddendocs 域重下, md5 期望: fts_catalog.pdf = fa249db9454f92c77d7e0a5ef62a0ba6 · footprint.pdf = 1cbe4a2bfa456d8fd030c8b76bdf8dd5★)★★
```

---

## ★★六 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★零改既有闸★ | ★`MECH/check_debug_seat_3d_fit.py` / `MECH/check_debug_seat_rework_spec.py` md5 与基线同★ (★**含 L848 / L879 那两个字符串不许动★**) |
| ★零改既有页面正文★ | ★ISS-389 / ISS-387 / ISS-386 已签收页 md5 与基线同★ (★**订正只登记, 不落**★) |
| ★零挂链★ | ★`grep -c check_fts_seat_body_geometry state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机 + 自己上官网查; ★`state/outbox/` 一个字节未动; ★**零邮件/零询价/零问询/零采购**★ |
| ★不代拍★ | ★★**厂件外形的最终值 / `OI-11` 的 `h` / `OI-12` 过不过严 / `OI-14` 改不改 —— 全是 main / boss 的裁决权 ⇒ ★★你只摆证据与代价, 不写「应该 X」★★ ⇒ ★机器块里要有 `*_decision = not_decided_here` 这类字段★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/mech.yaml`★ |
| ★沙盒纪律★ | ★只落 `tmp/iss390_sbx/` 与 `logs/iss390/`; ★不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ |
| ★证据分级★ | ★每条结论标五级之一★ |
