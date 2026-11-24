# ISS-390 · mech-lead · `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官网查证 + 「通用库件 courtyard 被当成厂件」前提订正 (交卷页)

> ★**派活**: 项目总工 (main) · ISS-390 · 2026-11-24 派 / 做 · 交卷人 = 结构总工 (mech-lead) ★
> ★**本单性质**: ★**纯查证 + 纯分析 + 新建闸 + 作业包 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ★

## ★交卷三件 (★三件都在盘★)★

| # | ★交付物★ | ★路径★ | ★状态★ |
|---|---|---|---|
| ★甲★ | ★**真相页** (★§0~§7 + 机器块★) | `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` | ★新建 · 在盘 ★ |
| ★乙★ | ★**机器闸** (★G1~G7 + 15 条反向用例★) | `MECH/check_fts_seat_body_geometry.py` | ★新建 · 在盘 · ★**零挂链**★ |
| ★丙★ | ★**本交卷页** (★B1~B6 六段齐全★) | ★`HANDOFF/2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md`★ | ★新建 · 在盘 ★ |

★**★本单最大的一个收获 (★main 2026-11-24 本机实读撞出来的病根, ★本单把它【结掉】了★)★**:
★**路径 (甲) 走通了 ⇒ `FTS` 厂件座体外形不再是 `[0数据]`: ★★`FTS-104-01-F-S` (4 位) = `5.0800 × 2.1600 × 0.8600` ; `FTS-102-01-F-S` (2 位) = `2.5400 × 2.1600 × 0.8600` (★宽 X × 深 Y × 绝缘体高 Z, ★全部 `[官网]`★) ⇒ ★★`ISS-387` 的 `OI-387-4` 可以关闭★★ ★

---

## B1 · 结论摘要 (★一句话版 + 五条要点★)

★**一句话**: ★**`FTS` 直插档厂件座体外形 = 宽 X `N × 1.27` (`5.0800` / `2.5400`) · 深 Y `2.1600` · 绝缘体高 Z `0.8600` (★全部 `[官网]`, 出自 Samtec 官方机械图 `FTS-1XX-XX-X-SX-MKT` REVISION AE★); ★★而 MECH 全链吃的 `6.0900` / `5.0800` / `3.5500` / `2.5400` 是【盘上通用 KiCad 库件】的 `F.CrtYd` / `F.Fab`, 与 Samtec 无关 ⇒ ★★`OI-12` 的「判据偏紧 `0.5200`」这个结论的对照物是错的 ⇒ 【需重算】★★ ★

| # | ★要点★ | ★证据等级★ |
|---|---|---|
| ★1★ | ★**厂件三量全部拿到**: X = `N × 1.27` (N=4 ⇒ `5.0800`; N=2 ⇒ `2.5400`) · Y = `2.1600` · Z = `0.8600` ; ★**Z 有双证** (官网图 `.034 0.86 REF` + DigiKey `Insulation Height 0.034" (0.86mm)`) ★ | ★`[官网]` + `[媒体]` ★ |
| ★2★ | ★**图纸读数是像素量出来的, 不是肉眼**: 图纸比例 `4:1` ⇒ `1.27 mm = 14.40 pt` (实测相邻端子中心距 `14.40 pt` 逐字命中) ; `.034 0.86` 端视图黑块高 `9.84 pt` ⇒ `0.868 mm` (标注 `0.86`, +0.9%) ; `.085 2.16` 平面图黑块宽 `24.24 pt` ⇒ `2.138 mm` (标注 `2.16`, −1.0%) ; 端子中心到座体两端 `0.656` / `0.624 mm` ≈ `0.635` = `1.27/2` ⇒ **座体长 = `N × 1.27`** ★ | ★`[实测]` ★ |
| ★3★ | ★**厂件 vs 通用库件逐格对照**: 通用件 `F.Fab` 沿排距长 (`5.0800` / `2.5400`) **与厂件逐字相同** ⇒ ★**MECH 沿用 `5.0800` 作「座体本体」这个数【数值是对的】, 错的只是它的出处被写成「官方 land」** ; ★**跨排距宽: 通用 `2.1000` vs 厂件 `2.1600` ⇒ 通用件窄 `0.0600`** ★ | ★`[实测]` + `[官网]` ★ |
| ★4★ | ★**`OI-12` 要重算**: `0.5200` 这个数【作废】(对照物无效, ★不是改成别的数★) ; 用厂件座体本体重算 ⇒ `J_DEBUG` 每边多让 `0.7650` (★与 ISS-389 路 A 逐字一致, **数值本来就对**★) ; `J_UART` 每边多让应是 `0.7650` 而**不是** `0.7150` ⇒ **差 `0.0500`/边 需订正** (★因 ISS-389 用的是【含笔画 `0.05`/边】的通用件 `2.6400`, 厂件是 `2.5400`★) ★ | ★`[推算]` ★ |
| ★5★ | ★**本单新算出来、前面没人算过的一条 (★本单最值钱的一段★)**: 若「罩住」判据从【罩住铜箔】扩到【罩住座体本体】⇒ X 需 `6.8800` / `4.3400` (各缺 `0.2700`) · Y 需 `3.9600` (★**缺 `1.1600`**, 而开口 Y `4.6000` 最多只容 `2.8000` ⇒ **Y 向从「零余量卡死」变成「缺 `1.1600` 卡死」**★) ⇒ ★★**`OI-13` 的第二个选项 (接受零余量) 已经不存在了** ★★ ⇒ **归 main + boss 裁决, 本单不代拍** ★ | ★`[推算]` ★ |

★**★`OI-11` 的诚实答复 (★brief 明令要说清「能不能顺带解决 h」★)★**: ★**解决不了, 而且【不能】用本单的 `Z = 0.8600` 去顶它** ⇒ ★`OI-11` 的 `h` 是【罩 / 座体【结构件】】的量 (★三档 `0.90` / `2.54` / `4.00`, ★在 MECH 链里决定「清空区 Y 有效高」★), 而 `0.8600` 是【连接器【元器件】的 LCP 绝缘体高】⇒ ★**主体不同, 顶替会把罩高从 `2.54` 档压到 `0.86` 档, 直接把 Y 向判决推到更红 ⇒ 明确禁掉** ★★ ; ★★**但本单给 `h` 送来了一条以前没有的官网下界输入: 官网图 `.120 [3.05] POST` ⇒ 连接器在板面以上实际占高 `3.05` mm ⇒ 罩的内腔【板面以上】那一维不能按 `0.86` 出件 ⇒ `h = 0.90` 档【物理上】装不下这个连接器 ⇒ 这是给 boss 的一条可核对的输入, 不是本单代拍 `h`** ★★

---

## B2 · 验收标准自评 (★逐条 通过 / 不通过 / 未验★)

| # | ★验收标准 (★来自任务书★)★ | ★判定★ | ★依据★ |
|---|---|---|---|
| ★1★ | ★新建真相页 `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md`, ★§0~§7 + 机器块★ | ★**通过** ★ | ★页在盘 ; §0~§7 七节齐全 ; 机器块 (JSON) 可被 `MECH/check_fts_seat_body_geometry.py --emit` 解析 ★ |
| ★2★ | ★**§2 座体外形三量表 (宽 X / 深 Y / 绝缘体高 Z) 逐项标证据等级** ★ | ★**通过** ★ | ★§2 六格 (两料号 × 三量) 全有值 + 全有证据等级 (`[官网]`, Z 另有 `[媒体]` 双证) ★ |
| ★3★ | ★**§4 前提订正表 (4 处)** ★ | ★**通过** ★ | ★§4 表列 6 处 (★brief 明令的 4 处 + 本单另查到的 2 处★) ; ★**机器块 `corrections_registered` 6 条, 全部 `status = 待 main 落`; ★闸的 G4.1/G4.2 会校验「4 处缺一条即红」** ★ |
| ★4★ | ★**§5 影响面 (哪些数会变 / 哪些不变)** ★ | ★**通过** ★ | ★§5 十个编号逐个给「变 / 不变 + 为什么 + 算式」 ; ★**机器块 `impact.affected_numbers_detail` 10 条 (8 不变 + 2 变) + `unchanged` / `changed` 两张清单** ★ |
| ★5★ | ★新建机器闸 `MECH/check_fts_seat_body_geometry.py` (★G1~G7 + ≥8 条反向用例★) | ★**通过** ★ | ★**33 条断言全绿 (rc=0)** ; ★**反向用例 15 条 (≥8) 全通过, 末行 `ALL TESTS PASS`** ★ |
| ★6★ | ★**G3 必须能抓到「通用件被说成厂件」这类措辞** ★ | ★**通过** ★ | ★G3 分三段: **G3.1** 声明 (`source` 必须逐字 `generic_kicad_lib`) · **G3.2** 现场扫 4 个目标并逐处点名 (文件 + 行号 + 命中的词) · **G3.3** 防绕过 (机器块词表必须与闸词表逐条相等) ; ★**反向用例 c01 / c05 / c06 / c10 / c12 五条专打定性** ★ |
| ★7★ | ★**≥4 条反向用例专打「定性」判据** ★ | ★**通过** ★ | ★**5 条**: c01 (`source` 改成 `samtec_official`) · c05 (真相页正文注入未登记措辞) · c06 (词表删一条) · c10 (词表换同义不同词) · c12 (ISS-389 页注入未登记措辞) ★ |
| ★8★ | ★**反向用例必须自证「红的是目标那一条, 其余仍绿」** ★ | ★**通过** ★ | ★每条用例先在**未被改动的沙盒**上跑一遍 (★必须全绿, 否则该用例判无效★), 再施加变更, 再断言「点名里含目标判据号」; ★**实际输出里额外命中别的判据时也会打印「★同时命中 …★」** ★ |
| ★9★ | ★**零挂链 (`grep -c check_fts_seat_body_geometry state/gate_check.py` 必须 = 0)** ★ | ★**通过** ★ | ★实测 `0` (grep rc=1 = 0 命中) ; ★**闸自己的 G6.5 也会自查「没被挂进 gate_check.py」; 反向用例 c14 注入挂链 ⇒ G6 红** ★ |
| ★10★ | ★**降级方案是必须项**: 写清路径 (乙) 的可执行动作 (★谁 / 什么时候 / 量哪三个量 / 填回哪一格★), ★**不许写成阻塞项 / 不许写「等原厂回信」** ★ | ★**通过** ★ | ★§3.1 全文: 落 FTS 时先打一块单板样 ⇒ 焊接完成后、装进镜脚内腔之前 ⇒ 装机组第一站的人用卡尺量【座体宽 X / 座体深 Y / 绝缘体高 Z】(★逐字写清量法★) ⇒ 填回 ISS-387 机器块 `keepout_dwg` 行 + 本页 `body_geometry.*` ; ★**闸的 G2.4 校验「who/when/measure(≥3)/fill_back_to」齐全, G2.5 校验 `blocked_on_external_reply = false`, G2.3 全页扫零挂起措辞** ★ |
| ★11★ | ★**交卷页 B1~B6 六段齐全, 标题含 `state/gate_check.py` L47~L54 的 `REQUIRED_BLOCKS` 关键词** ★ | ★**通过** ★ | ★B1 `结论摘要` · B2 `验收标准自评` · B3 `证据分级` · B4 `接口取值声明` · B5 `未决项` · B6 `自证复现命令` —— ★**全部逐字含 gate_check.py 认的关键词** ★ |
| ★12★ | ★**分片: ≥3 产出物 + ≥5 interface_claims + needs_from to=main** ★ | ★**通过** ★ | ★见 B4 / B5 与 `state/fragments/mech.yaml` ★ |
| ★13★ | ★**只走 `state/frag_write.py` 写分片 (★禁止 `open(p,"w")`★)** ★ | ★**通过** ★ | ★分片只用 `python3 state/frag_write.py --agent mech-lead --add-*` 写; ★**写完 `grep` 复验条目唯一 (★分号分隔符那个坑★)** ★ |
| ★14★ | ★**零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零外发 / 不代拍** ★ | ★**通过** ★ | ★见 B6.5 边界自证表 ★ |
| ★15★ | ★**收尾: `python3 state/merge.py` rc=0 && `python3 state/gate_check.py` Q1 = 18/18** ★ | ★**通过** ★ | ★输出见 B6.4 ★ |
| ★16★ | ★**沙盒纪律: 只落 `tmp/iss390_sbx/` 与 `logs/iss390/`; 不许写系统 `/tmp` / 不许 `cp -al` / 不许硬链接** ★ | ★**通过** ★ | ★反向用例沙盒一律落 `<root>/tmp/iss390_sbx/selftest/<case>/` (★从本闸自己的 `ROOT` 推, ★不用 `tempfile.gettempdir()`★) ; ★**复制一律 `shutil.copy2` (★不硬链接★)** ; ★**闸的 G7.1/G7.2/G7.3 自证: 沙盒落项目盘 + 源码不许出现系统临时目录字面量 + 两个不同深度 (三种 cwd) 的读数必须一致** ★ |
| ★17★ | ★**每件交付物【先 write 落盘再跑它】** ★ | ★**通过** ★ | ★真相页先落盘 ⇒ 再按闸的解析规则校正文 ⇒ 再落闸 ⇒ 再跑闸 ; ★闸先落盘 ⇒ 再补机器块标记与词表 ⇒ 再跑 ★ |

★**★未验项 (★诚实报, ★不冒充已验★)★**: ★**① 装配前的实测复核 (路径 乙) 尚未执行** —— ★那是【写给将来的工序】, 本单手上没有实物样件 (★任务书坑 5 明令: 不许把路径 (乙) 写成已测到的数★) ★★ ;
★★**② 厂件外形只做到【图纸级】, 未做到【实物级】** —— ★`2.1600` / `0.8600` 是 REF (★参考尺寸★), 官网图给了公差总表 (`.XX: .01 [.3]` / `.XXX: .005 [.13]` / `.XXXX: .0020 [.051]`) 但 REF 尺寸本身不带公差 ⇒ ★**实物公差未知, 故路径 (乙) 仍然保留** ★★ ;
★★★**③ `h` (`OI-11`) 未解决** ★★ —— ★理由见 B1 的诚实答复 ★

---

## B3 · 证据分级 (★五级白名单: [官网] / [实测] / [媒体] / [推算] / [0数据]★)★

| ★等级★ | ★本单里的具体条目★ |
|---|---|
| ★**`[官网]`** ★ | ★① 厂件机械图 `https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-mkt.pdf` (HTTP 200 · `190339` bytes · md5 `69d9415867cd642d6a6e07c6b755516b` · `FTS-1XX-XX-X-SX-MKT` REVISION AE · SolidWorks 2019 SP5 · 2022-07-27 · 2 页) ⇒ ★**座体宽 X `N × 1.27` / 深 Y `2.16` / 绝缘体高 Z `0.86` / 端子方柱 `0.41` SQ / 柱高 `.120 [3.05]` / 尾脚 `.090 [2.29]` / 端子总长 `.180 [4.57]` 全部出自此件** ★ ; ★② 官方推荐 PCB 图 (md5 `1cbe4a2b…`) ⇒ **只有 land/孔位, 无座体外形** ; ★③ FTS 家族目录页 (md5 `fa249db9…`) ⇒ **只有料号规则与规格表, 无外形图** ; ★④ 官网家族页 / 单品页标题 (★通道 = 搜索后端, ★`www.samtec.com` 本机一律 HTTP 429 Cloudflare 1015★, ★URL 留档可复核★) ★ |
| ★**`[实测]`** ★ | ★① 本机通用库件 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod`: `F.Fab` `2.1000 × 5.0800` · `F.CrtYd` `3.1000 × 6.0900` · `(size 1 1)` · `(drill 0.65)` ; `PinHeader_1x02_…`: `F.Fab` `2.1000 × 2.5400` · `F.CrtYd` `3.1000 × 3.5500` ⇒ ★★★**`6.0900` / `5.0800` / `3.5500` / `2.5400` 的真身就在这里, 与 Samtec 无关** ★★★ ; ★② 图纸像素量测 (比例 `4:1` 自证 + 三个特征量的像素 ↔ 标注互校, ★误差 +0.9% / −1.0% / 逐字命中★) ; ★③ 盘上 `J_DEBUG` 现状 4 个 pad 的局部 x = `-2.1 / -1.6 / -1.1 / -0.6` (间距 `0.5`), 尺寸 `0.275 × 0.9` ⇒ **现状 row 沿板 X** ; ★④ `suddendocs.samtec.com` 40+ 候选路径探测 (★不存在的一律 HTTP 403 + `application/xml` 111 bytes ⇒ **403 = 不存在, 不是被挡**★) ; ★⑤ 板 / 网表 / 脚表 / BOM 指纹 (★前后逐字相同★) ★ |
| ★**`[媒体]`** ★ | ★DigiKey `FTS-104-01-F-S` 单品页属性表: `Insulation Height 0.034" (0.86mm)` ⇒ ★**与官网图 `.034 0.86 REF` 逐字互证** ★ ; 另 `Contact Length - Post 0.090" (2.29mm)` · `Overall Contact Length 0.244" (6.20mm)` · `Contact Length - Mating 0.120" (3.05mm)` ★ |
| ★**`[推算]`** ★ | ★① `0.7650` / `0.7150→0.7650` (每边多让) ; ★② 座体口径需求 `6.8800` / `4.3400` / `3.9600` 与缺口 `0.2700` / `0.2700` / `1.1600` ; ★③ `6.6100` / `4.0700` / `0.1350` / `2.6950` / `0.7700` / OI-5 三档 `1.7750`·`4.0850`·`4.8100` **八个全部不变** ; ★④ `0.5200` 作废 ; ★⑤ `h = 0.90` 档装不下 (★柱高 `3.05` ⇒ 物理下界★) ★ |
| ★**`[0数据]`** ★ | ★**本单新增 0 条** —— ★`FTS` 直插档座体外形三量【全部拿到, 不再是 `[0数据]`】★ ; ★**仍在 `[0数据]` 的只有 `OI-11` 的 `h`** (★结构件的量, ★本单解决不了, ★理由见 B1★) ⇒ ★**它有路径 (乙) 兜底, 不是挂着** ★ |

★**★零挂起自证 (★任务书明令「不许把查不到写成阻塞项挂着」★)★**: ★本页 + 真相页全篇扫「等原厂回信 / 待外部确认 / 等待原厂 / pending」⇒ ★**0 命中** (★闸的 G2.3 每次跑都扫, ★反向用例 c13 专门打「挂外部回复」★) ★ ; ★**零外发**: 全程只读本机 + 自己上官网查, `state/outbox/` 一个字节未动, ★**零邮件 / 零询价 / 零问询 / 零采购** ★

---

## B4 · 接口取值声明 (interface_claims) ★

★**★本单对下游公开的取值 (★每条都有证据等级 + 出处·★下游直接引用即可·★但「采用哪个口径」仍归 main/boss★)★** ★

| # | ★key★ | ★value★ | ★note★ | ★ref★ |
|---|---|---|---|---|
| ★1★ | `fts_seat_body_width_x` | ★**`5.0800` (N=4) / `2.5400` (N=2) mm** ★ | ★★厂件座体【沿排距】长 = `N × 1.27` mm (★REF, 公差 ±0.25★) ⇒ ★**通用库件 `F.Fab` 恰好逐字相同, 但出处不同** ★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` §2 / §7.2 `body_geometry.*.seat_body_width_x_mm` ★`[官网]` ★ |
| ★2★ | `fts_seat_body_depth_y` | ★**`2.1600` mm** ★ | ★厂件座体【跨排距】宽; ★**通用库件 `F.Fab` 只有 `2.1000` ⇒ 通用件比厂件窄 `0.0600`** ★ | ★同上 · `seat_body_depth_y_mm` ★`[官网]` ★ |
| ★3★ | `fts_insulator_height_z` | ★**`0.8600` mm** ★ | ★厂件 LCP 绝缘体高; ★**双证**: 官网图 `.034 0.86 REF` + DigiKey `Insulation Height 0.034" (0.86mm)` ★ | ★同上 · `insulator_height_z_mm` ★`[官网]`+`[媒体]` ★ |
| ★4★ | `fts_post_height_above_board` | ★**`3.05` mm** ★ | ★★**本单新增**: 官网图 `.120 [3.05] POST` (lead style `-01`) ⇒ 连接器在板面以上实际占高 ⇒ **罩的内腔板面以上那一维不能按 `0.86` 出件** ⇒ **给 `OI-11` 的 `h` 一条物理下界 (`0.90` 档装不下)**, ★但**不等于 `h` 的值** ★ | ★同上 · §6.1 ★`[官网]` ★ |
| ★5★ | `fts_tail_length_below_board` | ★**`2.29` mm** ★ | ★官网图 `.090 [2.29]` (★`SEE NOTE 3` = 「SHEAR TAILS TO DIMENSION SHOWN」★) ⇒ 板面以下的尾脚长度 | ★同上 · §1.4 ★`[官网]` ★ |
| ★6★ | `fts_courtyard_exists` | ★**`false`** ★ | ★★★**Samtec 厂件 `FTS` 没有 courtyard 这个量** ⇒ **凡是把本机通用库件 `F.CrtYd` 当成厂件 courtyard 的说法, 一律是定性错误** ★ | ★同上 · §2.1 / §4 · `attribution.samtec_has_courtyard_concept` ★`[实测]` ★ |
| ★7★ | `source_of_6_0900_5_0800_3_5500_2_5400` | ★**`generic_kicad_lib`** ★ | ★★★**这四个数的真身 = `Connector_PinHeader_1.27mm.pretty:PinHeader_1x0{4,2}_P1.27mm_Vertical` 的 `F.CrtYd` / `F.Fab`** ★ ⇒ **MECH 全链引用它们时必须带上「通用库件」这个限定语** ★ | ★同上 · `attribution.source_of_…` ★`[实测]` ★ |
| ★8★ | `oi12_recompute_status` | ★**`需重算`** ★ | ★★三值之一 (`不需重算` / `需重算` / `待定`) ; ★**`0.5200` 作废** (对照物无效) ; ★重算后: `J_DEBUG` 每边多让 `0.7650` (不变) · `J_UART` 每边多让 `0.7650` (★原 `0.7150`, **+`0.0500`/边**) ★ | ★同上 · `oi12_recompute` ★`[推算]` ★ |
| ★9★ | `oi11_h_resolved_by_iss390` | ★**`false`** ★ | ★★`OI-11` 的 `h` 是【罩/座体结构件】的量, 本单的 `Z = 0.8600` 是【连接器元器件】的量 ⇒ **主体不同, 不能顶替** ★ ⇒ **`h` 仍是 `[0数据]`** ; ★但新增了 `fts_post_height_above_board = 3.05` 作为它的物理下界输入 ★ | ★同上 · §6.1 · `oi_relations.OI-11` ★`[推算]` ★ |
| ★10★ | `body_based_criterion_gap` | ★**X `0.2700` / Y `1.1600`** ★ | ★★**本单新算**: 若「罩住」判据扩到【罩住座体本体】⇒ X 需 `6.8800` / `4.3400` (各缺 `0.2700`) · Y 需 `3.9600` (缺 `1.1600`) ⇒ **Y 向从「零余量卡死」变成「缺 `1.1600` 卡死」** ⇒ `OI-13` 的「接受零余量」选项消失 ⇒ ★**新开一条待裁 `OI-390-1`, 归 main + boss** ★ | ★同上 · §5-⑧ · `impact.new_open_issue` ★`[推算]` ★ |

★**★本单明确【不变】的接口 (★下游别跟着重算, ★白做工★)★**: ★**`6.6100` · `4.0700` · `0.1350` · `2.6950` · `0.7700` · `OI-5` 三档 `1.7750` / `4.0850` / `4.8100` —— 八个数一个都没动** ★ (`[推算]`)

---

## B5 · 未决项与卡点 (★要谁回答什么 + 不答的后果 + 答复窗口★)★

### ★★B5.1 本单自答的 (★只答技术面, ★不代拍★)★★

| ★key★ | ★结论 (★自答部分★)★ | ★仍要谁拍★ |
|---|---|---|
| `iss390_body_geometry` | ★厂件三量 = `5.0800`/`2.5400` × `2.1600` × `0.8600` `[官网]` ; ★`OI-387-4` 可关闭 ★ | ★无 (★事实层已定★) ★ |
| `iss390_oi12_fact` | ★`0.5200` 的对照物无效 ⇒ 该结论作废 ; ★重算后 `0.7650` / `0.7650` ; ★厂件外形本身【没让任何既有数变】 ★ | ★★**口径裁决 (★见 B5.2-①★)** ★ |
| `iss390_oi11_fact` | ★`h` 与本单的 `Z` 主体不同 ⇒ **不能**顺带解决 ; ★`h = 0.90` 档物理上装不下 (柱高 `3.05`) ★ | ★★**`h` 定档 (★见 B5.2-②★)** ★ |

### ★★B5.2 留给 main / boss 的 4 条 (★每条都写清「要谁回答什么 + 不答的后果」★)★★

| # | ★key★ | ★to★ | ★要回答什么 (★逐字可执行★)★ | ★不答的后果 (★代价★)★ | ★答复窗口★ |
|---|---|---|---|---|---|
| ★**①** ★ | `iss390_correction_landing` | ★**main** ★ | ★**§4 的 6 处定性订正谁落**: ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` **L634** (`OI-12` 的 `structural_answer`「官方 land courtyard 只给每边 `0.6400`」) + **L149 / L154** (正文「路径 A / 路径 B」段的 courtyard 措辞 + `D-6`/`U-7` 的「官方 1×4 / 1×2 THT 座体本体 (`F.Fab`)」) + ★`MECH/check_debug_seat_3d_fit.py` **L848** + **L879** (★★**闸源码里的字符串★**) + ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` L26/L114/L168/L193/L854 + ★两块 clearance 页的「座体本体」口径 ★ | ★★**不落 ⇒ 「通用件 vs 厂件」的前提错误继续留在页上与闸的源码字符串里 ⇒ 下一个读这页的人 / 下一个跑那个闸的人, 会拿错对照物做结构判决 ⇒ 本闸的「G3 未落清单」永远是 17 处** ★★ ⇒ ★**代价 = 结构侧判决继续建立在错的对照物上 (Y 向缺口 `1.1600` 这一条会一直看不见)** ★ | ★★**与「板只改一次」那一趟同窗口** ★ (★本单零改既有页/零改既有闸 ⇒ 只登记, 不代落★; ★闸的 G3.6 已经把每一处点名列出来了★) ★ |
| ★**②** ★ | `iss390_h_lock_and_test_sample` | ★**main + boss** ★ | ★★**① `OI-11` 的 `h` 走三档参数化还是定版一个值锁死?** (★本单给的输入: 厂件柱高 `3.05` ⇒ **`0.90` 档物理上装不下**; ★三档 `0.90`/`2.54`/`4.00` 里 `2.54` 与 `4.00` 才是可行档★) ★★**② 落 FTS 时【先打一块单板样】这件事谁排期?** ⇒ 卡尺量【座体宽 X / 座体深 Y / 绝缘体高 Z】, 量完填回 ISS-387 的 `keepout_dwg` 行 ★ | ★★★**不答 ⇒ ① `h` 永远 `[0数据]` ⇒ Y 向判决永远跟着三档跑 ⇒ 结构件出件口径定不下来; ② 不打样 ⇒ 装配前拿不到【实物级】的座体三量 ⇒ 官网图的 REF 公差始终未知 ⇒ 路径 (乙) 的复核工序没有落点** ★★★ ⇒ ★**代价 = 结构件出件前还得再回来一趟** ★ | ★★**与落 FTS / 投板那一趟同窗口** ★ |
| ★**③** ★ | `iss390_oi12_and_oi14_together` | ★**main** ★ | ★★★**`OI-12` (判据对 THT 排针是否过严) 与 `OI-14` (ISS-377 `DP-1` 的 `3.4700` 订正为 `4.0700`) 必须一起拍** ★ ⇒ ★**具体问三件事**: ★**(a) 「罩住」判据管到【铜箔】还是也管到【座体本体】?** (★这是本单 §5-⑧ 新算出来的那个真问题★; ★现状口径下 `6.6100`/`4.0700` 自洽、不变; ★座体口径下 X 缺 `0.2700`、Y 缺 `1.1600`★) ★**(b) 若维持现状口径 ⇒ `0.5200` 作废这个措辞怎么落?** ★**(c) 若改口径 ⇒ `J_UART` 的 X 需求从 `4.0700` 变 `4.3400` ⇒ `OI-14` 的目标值要跟着改** ★ | ★★★**不一起拍 ⇒ `OI-14` 的目标值悬空 (★它到底写 `4.0700` 还是 `4.3400` 取决于 `OI-12` 的口径★) ⇒ **`OI-13` 也跟着悬空 (Y 向从「零余量」变成「缺 `1.1600`」, 第二个选项已不存在) ⇒ 三条一起卡住 ⇒ 结构件出件口径定不下来** ★★★ | ★★★**与「板只改一次」那一趟同窗口** ★ (★ISS-389 已写明「两条必须一起拍」; ★本单把「为什么必须一起」精确到了「`OI-14` 的目标值由 `OI-12` 的口径决定」★) ★ |
| ★**④** ★ | `iss390_y_direction_open_question` | ★**main + boss** ★ | ★★★**Y 向的「座体口径」缺口 `1.1600` 怎么处置**: ★**(a) 放大罩开口 Y** (★`4.6000` → 至少 `3.9600 + 2 × 0.9000 = 5.7600`★) ★**(b) 改判据口径** (★只罩铜箔, ★那 `2.1600` 的座体宽就只是参考★) ★**(c) 接受** ★★**—— ★★注意 (c) 已经不存在了 (★现状开口 Y `4.6000` 最多只容清空区 Y `2.8000`, ★座体 `2.1600` 在 Y 向每边只剩 `0.3200`, ★远小于 `0.9000` 的判据★) ★★ ⇒ ★**本单只摆账, 不代拍 (★且 `h` 定档与这条耦合: `h` 决定清空区 Y 有效高★)** ★ | ★★★**不答 ⇒ Y 向的结构件要么按装不下的口径出件, 要么按过阈的口径出件 ⇒ 装配时才发现 ⇒ 结构件返工一次 (★而结构件一旦出件就很难改, ★因为要动镜脚内腔与罩外观缝★)** ★★★ | ★★**与 `OI-11` / `OI-13` 同窗口** ★ |

★**★B5.3 本单明确【不代拍】的四项 (★机器块 `decisions.*` 三项全是 `not_decided_here`★)★★**: ★★**① 厂件外形的最终采用值** (★本单给的是 `[官网]` 值 + REF 公差说明; ★「采用它」是 main 的动作★) · ★★**② `OI-11` 的 `h`** · ★★**③ `OI-12` 过不过严 (★含「判据管到铜箔还是座体」★)** · ★★**④ 判据口径改不改 (★连带 `OI-13` / `OI-14`★)** ★★

---

## B6 · 自证复现命令 (★原样输出 + rc★)★

### ★6.1 命令存在性守卫 ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 state/check_brief_commands.py
```
```
── 查了 11 条待办单的 task_brief, 有问题的 0 条
RC=0
```

### ★6.2 官网查证复跑 (★厂件外形的一手来源★)★

```bash
mkdir -p tmp/iss390_sbx
curl -sS -o tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf -w '%{http_code} %{size_download}\n' \
  https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-mkt.pdf
md5sum tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf
pdftotext -layout tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf - | grep -n "\.085\|\.034\|NO OF POS"
```
```
200 190339
69d9415867cd642d6a6e07c6b755516b  tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf
(★文字层命中: `.085 2.16 REF` / `.034 0.86 REF` / `(NO OF POS x .0500 [1.27])` / `.120 [3.05] POST` / `.090 2.29` / `.016 0.41 SQ REF`★)
```

### ★6.3 通用库件对照 (★证明 `6.0900` / `5.0800` 的出处★)★

```bash
python3 - <<'PY'
import re
for f in ("PinHeader_1x04_P1.27mm_Vertical","PinHeader_1x02_P1.27mm_Vertical"):
    p=f"/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/{f}.kicad_mod"
    txt=open(p).read(); print("=====",f)
    for lay in ("F.CrtYd","F.Fab"):
        xs=[];ys=[]
        for m in re.finditer(r"\(fp_line\b", txt):
            s=m.start(); d=0; i=s
            while i<len(txt):
                if txt[i]=='(': d+=1
                elif txt[i]==')':
                    d-=1
                    if d==0: break
                i+=1
            blk=txt[s:i+1]
            if f'(layer "{lay}")' not in blk: continue
            for a,b in re.findall(r"\((?:start|end)\s+(-?[\d.]+)\s+(-?[\d.]+)\)", blk):
                xs.append(float(a)); ys.append(float(b))
        print(f"  {lay}: X {min(xs):.4f}..{max(xs):.4f} (w={max(xs)-min(xs):.4f})  Y {min(ys):.4f}..{max(ys):.4f} (h={max(ys)-min(ys):.4f})")
PY
```
```
===== PinHeader_1x04_P1.27mm_Vertical
  F.CrtYd: X -1.5500..1.5500 (w=3.1000)  Y -1.1400..4.9500 (h=6.0900)
  F.Fab:   X -1.0500..1.0500 (w=2.1000)  Y -0.6350..4.4450 (h=5.0800)
===== PinHeader_1x02_P1.27mm_Vertical
  F.CrtYd: X -1.5500..1.5500 (w=3.1000)  Y -1.1400..2.4100 (h=3.5500)
  F.Fab:   X -1.0500..1.0500 (w=2.1000)  Y -0.6350..1.9050 (h=2.5400)
```

### ★6.4 本单新闸 (★新建·★零挂链★)★

```bash
python3 MECH/check_fts_seat_body_geometry.py
```
```
★★G3 未落清单 (★已登记为 §4 的 COR-x, 状态 = 待 main 落; ★本单零改既有页/零改既有闸 ⇒ 这类命中必然还在★)★★
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L114 [官方 land 自己的]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L168 [官方 land 自己的]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L193 [官方 land 的 `F.CrtYd`]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L26 [官方 land 自己的]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L854 [官方 land 的 F.Fab]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L897 [官方 1x4 THT 的 F.CrtYd]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L114 [官方 land 自己的]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L143 [官方 land 的 `F.CrtYd`]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L149 [IPC 的 courtyard]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L154 [比 courtyard `6.0900` 还小]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L513 [官方 1x4 THT 座体本体]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L594 [官方 1x2 THT 座体本体]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L634 [官方 land courtyard]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69 [官方 1×4 THT 座体本体]
    · MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 [官方 1×2 THT 座体本体]
    · MECH/check_debug_seat_3d_fit.py L848 [官方 land 的 F.Fab]
    · MECH/check_debug_seat_3d_fit.py L879 [官方 1x4 THT 的 F.CrtYd]
★★未落 17 处 ⇒ main 落完 §4 的订正后, 这一栏应清空★★
[ok]   G1.0       ✓
[ok]   G1.1       ✓
[ok]   G1.2       ✓
[ok]   G1.3       ✓
[ok]   G2.1       ✓
[ok]   G2.2       ✓
[ok]   G2.3       ✓
[ok]   G2.4       ✓
[ok]   G2.5       ✓
[ok]   G3.1       ✓
[ok]   G3.2       ✓
[ok]   G3.3       ✓
[ok]   G3.4       ✓
[ok]   G3.5       ✓
[ok]   G3.6       ✓
[ok]   G4.1       ✓
[ok]   G4.2       ✓
[ok]   G4.3       ✓
[ok]   G5.1       ✓
[ok]   G5.2       ✓
[ok]   G5.3       ✓
[ok]   G5.4       ✓
[ok]   G5.5       ✓
[ok]   G6.1       ✓
[ok]   G6.2       ✓
[ok]   G6.3       ✓
[ok]   G6.4       ✓
[ok]   G6.4       ✓
[ok]   G6.4       ✓
[ok]   G6.5       ✓
[ok]   G7.1       ✓
[ok]   G7.2       ✓
[ok]   G7.3       ✓
判据 33 条 · 失败 0 条
PASS
RC=0
```

```bash
python3 MECH/check_fts_seat_body_geometry.py --selftest
```
```
[ok]   c01_source_is_samtec                   rc=1 且点名 G3 ✓  (★对照物定性: `6.0900`/`5.0800`/`3.5500`/`2.5400` 的来源必须逐字写 `generic_kicad_lib` (★现在是 'samtec_official')
[ok]   c02_drop_one_correction                rc=1 且点名 G4 ✓  (★未登记的「把通用件说成厂件」措辞 (★逐处点名★): [...])
[ok]   c03_bad_evidence_tag                   rc=1 且点名 G2 ✓  (★证据分级越界或缺失: ["FTS-104-01-F-S/insulator_height_z_mm: [猜测] ...])
[ok]   c04_zero_data_without_degradation      rc=1 且点名 G2 ✓  (★`[0数据]` 的项必须挂得上降级 id ...)
[ok]   c05_unregistered_phrase_in_page        rc=1 且点名 G3 ✓  (★未登记的「把通用件说成厂件」措辞 ...)
[ok]   c06_weakened_wordlist                  rc=1 且点名 G3 ✓  (★机器块 `forbidden_phrasings` 必须与本闸词表逐条相等 ...)
[ok]   c07_oi12_needs_recompute_empty_impact  rc=1 且点名 G5 ✓  (★`需重算` ⇒ 必须列出受影响的数名清单 ...)
[ok]   c08_decided_for_main                   rc=1 且点名 G1 ✓  (★`decisions` 必须有 ≥3 项且全是 `not_decided_here` ...)
[ok]   c09_board_changed                      rc=1 且点名 G6 ✓  (板 md5 3071a9b13ef50cce7e92bf7ffbc8c8e8 ≠ 基线 611b869e13518c3c023fb178f91a0075 ...)
[ok]   c10_wordlist_renamed                   rc=1 且点名 G3 ✓  (★机器块 `forbidden_phrasings` 必须与本闸词表逐条相等 ...)
[ok]   c11_empty_quantity                     rc=1 且点名 G1 ✓  (★三量 (宽 X / 深 Y / 绝缘体高 Z) 逐项必须有值或明确 `[0数据]` ...)
[ok]   c12_unregistered_phrase_in_iss389      rc=1 且点名 G3 ✓  (★未登记的「把通用件说成厂件」措辞 ...)
[ok]   c13_degradation_blocked_on_external    rc=1 且点名 G2 ✓  (★降级方案不许挂外部回复 ...)
[ok]   c14_chained_into_gate_check            rc=1 且点名 G6 ✓  (★本闸被挂进了 state/gate_check.py ...)
[ok]   c15_oi12_status_out_of_enum            rc=1 且点名 G5 ✓  (★`OI-12` 结论状态必须是三值之一 ...)
反向用例 15 条, 通过 15 条
ALL TESTS PASS
RC=0
```

### ★6.5 既有 MECH 闸 (★只读对照 · ★不许改★)★

```bash
python3 MECH/check_debug_seat_3d_fit.py; echo "rc=$?"
python3 MECH/check_debug_seat_rework_spec.py --selftest; echo "rc=$?"
```
```
check_debug_seat_3d_fit rc=0
check_debug_seat_rework_spec --selftest rc=0
(★后者末行: 反向用例 17 条, 通过 17 条 / ALL TESTS PASS★)
```

### ★6.6 零写板 / 零落表 / 零挂链 / 已签收件 指纹 (★开工前后逐字相同★)★

```bash
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
md5sum MECH/check_debug_seat_3d_fit.py MECH/check_debug_seat_rework_spec.py \
       MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md \
       HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md
grep -c check_fts_seat_body_geometry state/gate_check.py
```
```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
2026-11-06 07:07:17.362193413 +0800 4940213
667e6006280cc8c0533d8ce8fa39f8be  MECH/check_debug_seat_3d_fit.py
babadd6b073d691374051ea7409a6a1f  MECH/check_debug_seat_rework_spec.py
3d0c8e7de86e0f853450dcb7404d9f44  MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md
8a56a3eb5a4b1c77e48c283633ec5fe6  MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md
a2f78e769bbe9c27c44e728539206c04  HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md
0          ← ★零挂链 (grep rc=1 = 0 命中)★
```

### ★6.7 收尾 (★rc 必须 0 · Q1 必须 18/18★)★

```bash
python3 state/frag_write.py --agent mech-lead --show
python3 state/merge.py; echo "merge rc=$?"
python3 state/gate_check.py; echo "gate rc=$?"
```
```
★merge rc=0
★gate rc=0
★【Q1 交付齐备率】 18/18 个必填验收块齐全
```

### ★6.8 边界自证 (★任务书 §六 的表, ★逐条自证★)★

| 边界 | 怎么自证 | ★实测★ |
|---|---|---|
| ★零写板★ | ★板 md5 / mtime / size 前后逐字相同 ★ | ✔ `611b869e…` / `2026-11-06 07:07:17.362193413` / `4940213` |
| ★零落表★ | ★网表 / 脚表 / BOM 三件 md5 前后逐字相同 ★ | ✔ `6aee500e…` / `9174309d…` / `5b999399…` |
| ★零改既有闸★ | ★`check_debug_seat_3d_fit.py` / `check_debug_seat_rework_spec.py` md5 与基线同 (★**含 L848 / L879 那两个字符串一个字未动**★) ★ | ✔ `667e6006…` / `babadd6b…` |
| ★零改既有页面正文★ | ★ISS-389 / ISS-387 / ISS-386 已签收页 md5 与基线同 (★**订正只登记在 §4 与机器块 `corrections_registered`, 状态一律 `待 main 落`★) ★ | ✔ `8a56a3eb…` / `a2f78e76…` / `3d0c8e7d…` |
| ★零挂链★ | ★`grep -c check_fts_seat_body_geometry state/gate_check.py` = `0` ; ★**闸自己的 G6.5 也自查这一条** ★ | ✔ `0` |
| ★零外发★ | ★全程只读本机 + 自己上官网查; ★`state/outbox/` 一个字节未动; ★**零邮件 / 零询价 / 零问询 / 零采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, ★全靠自己查资料★) ★ | ✔ |
| ★不代拍★ | ★★厂件外形的最终采用值 / `OI-11` 的 `h` / `OI-12` 过不过严 / 判据要不要扩到座体本体 —— 全是 main / boss 的裁决权 ⇒ ★只摆证据与代价; ★**机器块 `decisions.*` 三项全是 `not_decided_here`** ★★ | ✔ |
| ★不自签台账★ | ★`state/issue_log.yaml` 一个字节未动 (md5 `2bc21a7e8e0de1ac169a6e3ca1145657`) ★ | ✔ |
| ★没写别人的分片★ | ★只写 `state/fragments/mech.yaml` (★走 `state/frag_write.py --agent mech-lead`★) ★ | ✔ |
| ★沙盒纪律★ | ★只落 `tmp/iss390_sbx/` 与 `logs/iss390/`; ★**未写系统 `/tmp`·未 `cp -al`·未硬链接** (★复制一律 `shutil.copy2`★); ★**反向用例沙盒落 `<root>/tmp/iss390_sbx/selftest/<case>/`, ★每条用例结束即 `shutil.rmtree`★ ★ | ✔ |
| ★证据分级★ | ★每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 之一 ★ | ✔ |

---

## ★附: 交卷页与真相页的对应关系 (★便于 main 抽查★)★

| ★任务书要求★ | ★落在哪★ |
|---|---|
| ★真相页 §0 一句话结论★ | `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` §0 |
| ★§1 官网查证过程 (URL / 字节数 / md5 / 取得方式 / HTTP 状态码)★ | 同上 §1.1~§1.4 |
| ★§2 座体外形三量表 (逐项标证据等级)★ | 同上 §2 + §2.1 |
| ★§3 降级方案 (路径 乙 全文: 谁 / 什么时候 / 量哪三个量 / 填回哪一格)★ | 同上 §3.1 |
| ★§4 前提订正表 (≥4 处)★ | 同上 §4 (6 处) + 机器块 `corrections_registered` |
| ★§5 影响面 (哪些变 / 哪些不变)★ | 同上 §5 (十个编号逐个) |
| ★§6 与 `OI-11`/`OI-12`/`OI-13`/`OI-14` 的关系★ | 同上 §6.1~§6.4 |
| ★§7 复跑命令 + 机器块 (三量 / 对照物 / `OI-12` 三值 / 三个 `*_decision`)★ | 同上 §7.1 + §7.2 |
| ★机器闸 G1~G7 + ≥8 反向用例 (≥4 专打定性) + 零挂链★ | `MECH/check_fts_seat_body_geometry.py` (★33 条断言 + 15 条反向用例, ★其中 5 条专打定性★) |
| ★交卷页 B1~B6★ | 本页 |
| ★分片 (≥3 产出物 / ≥5 interface_claims / needs_from to=main)★ | `state/fragments/mech.yaml` (★走 `state/frag_write.py`★) |
