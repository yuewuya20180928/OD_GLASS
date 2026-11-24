# `J_DEBUG` 排针【排布标签 (维数)】订正真相 — ISS-382

> ★**本单性质**: ★**纯分析 + 新建机器闸 + 沙盒预演** ★ —— ★**零写板 · 零落表 · 零改已签收件 · 零改既有闸 · 零挂链 · 零外发 · 不代拍** ★
> ★**交卷人** = 结构总工 (mech-lead) · ★**派活** = 项目总工 (main / moli) · ★**单号** = ISS-382 · ★**日期** = 2026-11-24 ★
> ★**本页是【新增页】· `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 一个字节都没动** ★

---

## §0 一句话结论

★**一句话**: ★**错的是【标签 / 维数】, 不是【几何结论数字】** —— 官方两个 SMD 变体 (`Pin1Left` / `Pin1Right`) 自己解析 `.kicad_mod` 的 pad 坐标, 实测都是 ★**2 列 × 4 行交错 (`2x4_staggered`)**★; 而已签收页 L391 机器块写的是 `"arrangement": "2x2 staggered"`, 正文 L45 / L203 / L207 / L288 / L471 / L719 六处写的是「2 列 × 2 行交错」; ★**旧闸 `G5` 的盲区在于: 它只查页面字符串里【有没有写「交错」】, 从不把【页面声明的维数】与【闸自己实测的维数】逐字对比 ⇒ 页面写 `2x2` 照样绿、写 `9x9` 也照样绿** ★

★**① 两个 SMD 变体实测各是什么** (★`.kicad_mod` 真解析·★不是抄任何人的结论★):

| 变体 | pads | 列 | 行 | 沿 Y 的列序 | 判定 | 证据 |
|---|---|---|---|---|---|---|
| `PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left` | 4 | 2 | 4 | `−1.5 / +1.5 / −1.5 / +1.5` | `2x4_staggered` | [实测] |
| `PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Right` | 4 | 2 | 4 | `+1.5 / −1.5 / +1.5 / −1.5` | `2x4_staggered` | [实测] |

★**② 旧闸 `G5` 的盲区到底在哪** (★逐行可查★):

| 项 | 旧闸 `G5` 实际做的 | 旧闸 `G5` 没做的 | 证据 |
|---|---|---|---|
| 降级方案几何 | ★独立实测并单列 ★ | — | [实测] |
| 页面 `arrangement` 字符串 | ★只查字符串里【含】 `staggered` / `交错` ★ | ★**从不把页面声明的【维数】与闸自己实测的【维数】逐字对比** ★ | [实测] |
| 反例后果 | — | ★页面写 `2x2` 照样绿; 写 `9x9` 也照样绿 ★ | [实测] |

★**③ 结论数字不变** (★逐项独立重算过·★见 §2.2★): 降级方案铜箔包络 `6.0000 × 4.4600`、所需开口 Y `6.2600`、开口 X 余量 `2.1000 / 2.1000` (最坏 `1.8000`)、Y 余量 `0.0700 / 0.0700 / 0.6700` (rot0) 与 `−0.7000 / −0.7000 / −0.1000` (rot90)、三档 Y 全红判决 —— ★**一个数字都不改** ★ [实测]

---

## §1 实测表 (★三个官方变体·★自己解析 `.kicad_mod` 的 pad 坐标★)

★**复现命令** (★本机实跑 2026-11-24 07:3x★):

```bash
python3 MECH/check_jdebug_arrangement_truth.py --selftest
```

★**`2x4_staggered` 的完整定义** (★本单口径·★两个 SMD 变体都必须判 True★): ★**列 == 2 且 行 == 4 且 沿 Y 递增排序后相邻两行的列号左右交替** ★ ⇒ ★**不要求第一行必须是左列** ★ (★`Pin1Right` 的第一行是右列, 但它同样是交错排布★) ★

### §1.1 三个变体的排布实测

| 变体 | pads | 列 | 行 | 沿 Y 的列序 | 交错 | 判定 token | 证据 |
|---|---|---|---|---|---|---|---|
| `..._Vertical_SMD_Pin1Left` | 4 | 2 | 4 | `−1.5 / +1.5 / −1.5 / +1.5` | 是 | `2x4_staggered` | [实测] |
| `..._Vertical_SMD_Pin1Right` | 4 | 2 | 4 | `+1.5 / −1.5 / +1.5 / −1.5` | 是 | `2x4_staggered` | [实测] |
| `..._Vertical` (THT) | 4 | 1 | 4 | 一列沿局部 Y | 否 | `1x4` | [实测] |

### §1.2 SMD 变体的逐个 pad 坐标 (★库件原文·★局部坐标·★mm★)

| 变体 | pad | 中心 X | 中心 Y | pad 尺寸 | 证据 |
|---|---|---|---|---|---|
| `SMD_Pin1Left` | 1 | `−1.5000` | `−1.9050` | `3.0000 × 0.6500` | [实测] |
| `SMD_Pin1Left` | 2 | `+1.5000` | `−0.6350` | `3.0000 × 0.6500` | [实测] |
| `SMD_Pin1Left` | 3 | `−1.5000` | `+0.6350` | `3.0000 × 0.6500` | [实测] |
| `SMD_Pin1Left` | 4 | `+1.5000` | `+1.9050` | `3.0000 × 0.6500` | [实测] |
| `SMD_Pin1Right` | 1 | `+1.5000` | `−1.9050` | `3.0000 × 0.6500` | [实测] |
| `SMD_Pin1Right` | 2 | `−1.5000` | `−0.6350` | `3.0000 × 0.6500` | [实测] |
| `SMD_Pin1Right` | 3 | `+1.5000` | `+0.6350` | `3.0000 × 0.6500` | [实测] |
| `SMD_Pin1Right` | 4 | `−1.5000` | `+1.9050` | `3.0000 × 0.6500` | [实测] |

### §1.3 由实测直接推出的几何 (★降级方案用 SMD 变体★)

| 项 | 实测/重算值 | 证据 |
|---|---|---|
| 铜箔包络 X | `6.0000` (★2 列中心距 `3.0000` + 每块 pad 长 `3.0000`★) | [实测] |
| 铜箔包络 Y | `4.4600` (★4 行中心 `±0.6350 / ±1.9050` + pad 高 `0.6500`★) | [实测] |
| 所需开口 Y | `6.2600` (★`4.4600 + 2 × (CRIT 0.6000 + TOL 0.3000)`★) | [推算] |
| 开口 X 区间 | `137.8500 .. 148.0500` (★中心 `142.9500`★) | [实测] |
| 开口 Y 中心 | `56.6000` (★三档同中心★) | [实测] |

---

## §2 订正块 (★给 main 落用的追加块草稿·★本单【只起草】, 一个字都没落进已签收页★)

★**§2 是本单最核心的一段** ★ —— ★**它回答两件不同的事: ① 哪几行的标签错了、该改成什么 ② 哪些结论数字一个都不动** ★

### §2.1 逐行订正台账 (★7 条·★一处都不许漏★)

★**口径**: 「已签收页哪一行写的什么」⇒「实测是什么」⇒「建议改成什么」★

| 已签收页行 | 原文写的表面 | 实测 | 建议改成 | 证据 |
|---|---|---|---|---|
| L45 | `2 列 × 2 行` (交错) | `2 列 × 4 行` 交错 ⇒ `2x4_staggered` | `2 列 × 4 行` (交错) | [实测] |
| L203 | `2 列 × 2 行` (交错) | `2 列 × 4 行` 交错 ⇒ `2x4_staggered` | `2 列 × 4 行` (交错) | [实测] |
| L207 | `2 列 × 2 行` (交错) | `2 列 × 4 行` 交错 ⇒ `2x4_staggered` | `2 列 × 4 行` (交错) | [实测] |
| L288 | `2 列 × 2 行` (交错) | `2 列 × 4 行` 交错 ⇒ `2x4_staggered` | `2 列 × 4 行` (交错) | [实测] |
| L391 | `2x2` (机器块 `land_smd.arrangement`) | `2x4_staggered` | `2x4_staggered` | [实测] |
| L471 | `2x2` (降级方案判决句里的 SMD 变体) | `2x4_staggered` | `2x4_staggered` | [实测] |
| L719 | `2x2` (总判决句里的 SMD 变体) | `2x4_staggered` | `2x4_staggered` | [实测] |

★**不订正的 4 处 (★已签收页自己写对的·★不许顺手改·★改了就是制造新红★)**:

| 已签收页行 | 原文 | 为什么不用改 | 证据 |
|---|---|---|---|
| L45 / L203 的 `1×4` | 否定式表述「不是 `1×4` 直排」 | ★**否定句说的是 THT 变体, 不是 SMD 变体** ★ ⇒ 不是缺陷 | [实测] |
| L208 | 「4 个焊盘在 Y 向排 4 行 (中心 ±0.635 / ±1.905)」 | ★**这一句和实测一致** ★ ⇒ 恰恰证明同一页自相矛盾 | [实测] |
| L471 / L719 的三档 Y 判决数字 | `0.07 / 0.07 / 0.67` 等 | ★**数值结论不因标签订正而改变** ★ | [实测] |

### §2.2 哪些结论数字【不因此改变】 (★独立重算过一遍·★逐项相等才敢写这句话★)

★**重算口径**: ★**只用 `.kicad_mod` 的 pad 坐标 + `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 机器块的开口 X/Y + `MECH/service_port_check.py` 的 `CRIT`/`TOL` · ★不抄已签收页里的任何数★** ★

| 结论项 | 已签收页写的 | 独立重算 | 变不变 | 证据 |
|---|---|---|---|---|
| 降级方案铜箔包络 X | `6.0000` | `6.0000` | 不变 | [实测] |
| 降级方案铜箔包络 Y | `4.4600` | `4.4600` | 不变 | [实测] |
| 所需开口 Y | `6.2600` | `6.2600` | 不变 | [推算] |
| rot0 铜箔 X 区间 | `139.9500 .. 145.9500` | 同 | 不变 | [推算] |
| rot0 铜箔 Y 区间 | `54.3700 .. 58.8300` | 同 | 不变 | [推算] |
| rot0 开口 X 余量 | `2.1000 / 2.1000` (最坏 `1.8000`) | 同 | 不变 | [推算] |
| rot0 三档 Y 余量 | `0.0700 / 0.0700 / 0.6700` | 同 | 不变 | [推算] |
| rot0 三档 Y 最坏余量 | `−0.2300 / −0.2300 / 0.3700` | 同 | 不变 | [推算] |
| rot0 三档 Y 判决 | 全红 | 全红 | 不变 | [推算] |
| rot90 铜箔 X 区间 | `140.7200 .. 145.1800` | 同 | 不变 | [推算] |
| rot90 铜箔 Y 区间 | `53.6000 .. 59.6000` | 同 | 不变 | [推算] |
| rot90 开口 X 余量 | `2.8700 / 2.8700` (最坏 `2.5700`) | 同 | 不变 | [推算] |
| rot90 三档 Y 余量 | `−0.7000 / −0.7000 / −0.1000` | 同 | 不变 | [推算] |
| rot90 三档 Y 最坏余量 | `−1.0000 / −1.0000 / −0.4000` | 同 | 不变 | [推算] |
| rot90 三档 Y 判决 | 全红 | 全红 | 不变 | [推算] |

★**⇒ 订正标签不会动到任何数值结论; ★反过来, 数值结论对也不代表标签对** ★ —— ★**这两件事必须分开判, 合并成一条判据就等于放过 `G5` 的盲区** ★

### §2.3 ★给 main 的追加订正块草稿 (★本单只起草·★落点/批次由 main 裁★) ★

★**落点建议** (★由 main 裁·★本单不代拍★): 追加到 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 文末作 `§10` 追加节 (★前面任何一句都不许改★) ★
★**代价提示** (★有据·★ISS-374 cont2 先例★): ★**在已签收页上追加 ⇒ `MECH/check_connector_clearance_caliber.py` 的 `K7` 立刻红 2 条 ⇒ 落点与时机是有代价的, 归 main 裁** ★ [实测]

★**草稿正文 (★main 可直接抄★)** ★

> ## §10 排布标签订正 (★2026-11-24 · ISS-382 追加节·★前面各句一字未改·★) ★
>
> | 项 | 订正前 | 订正后 | 证据 |
> |---|---|---|---|
> | 机器块 `land_smd.arrangement` | `2x2 staggered` | `2x4_staggered` | [实测] |
> | L45 / L203 / L207 / L288 正文 | 2 列 × 2 行交错 | 2 列 × 4 行交错 | [实测] |
> | L391 / L471 / L719 正文 | 2x2 | 2x4 | [实测] |
>
> ★**事实句**: 官方 `PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left` 与 `_Pin1Right` 两个变体, 自己解析 `.kicad_mod` 的 pad 坐标, 都是 4 焊盘 / 2 列 / 4 行 / 沿 Y 列序左右交替 ⇒ 排布是 `2x4_staggered`。 [实测]
>
> ★**判据句**: 排布标签的维数必须与闸自己实测的维数逐字相等; 不等就是错标签, 与降级方案的数值结论无关。 [推算]
>
> ★**结论数字不变**: 降级方案铜箔包络 `6.0000 × 4.4600`、所需开口 Y `6.2600`、开口 X 余量 `2.1000 / 2.1000` (最坏 `1.8000`)、Y 余量 `0.0700 / 0.0700 / 0.6700` (rot0) 与 `−0.7000 / −0.7000 / −0.1000` (rot90)、三档 Y 全红判决 —— ★**一个数字都不改** ★ [实测]

### §2.4 ★订正块落进已签收页之后, 本闸会不会新增红 (★本单自己先验过★) ★

★**这是本单最容易被忽略、也最要命的一条: ★**订正块是给 main 落的, 落进【已签收页】⇒ 已签收页的 md5 会变 ⇒ 既有闸的指纹类判据 (★如 `MECH/check_connector_clearance_caliber.py` 的 `K7`★) 就会红 ⇒ ★**如果本单的新闸在落订正块那一刻也变红, 等于本单自己又制造了一处红** ★** ⇒ 所以本闸把「落订正块」当成一条【必须为绿】的用例来跑** ★

| 项 | 本闸的设计 | 实测 | 证据 |
|---|---|---|---|
| 台账条目的 open / landed 判定 | ★按【该条的 surface 文本是否仍出现在已签收页里】判定★ ⇒ 落完订正块 ⇒ 旧 surface 消失 ⇒ 条目自动 closed ★ | ★闸的反向用例 ⑪ 实跑: 落完 7 条订正块 ⇒ 红组 `∅` ⇒ 一条红都不新增 ★ | [实测] |
| 落订正块后的错表述 | ★落完后那 7 处与实测相符 ⇒ 不再是「与实测不符的表述」 ⇒ 台账覆盖要求归零 ★ | ★同上 (红组 `∅`) ★ | [实测] |
| 若 main 落成【新的错值】 (★例如写成「3 列 × 4 行交错」★) | ★该表述与实测不符且不在台账里 ⇒ J3 立刻红 ★ | ★闸的反向用例 ⑥ 实跑 ⇒ J3 红 ★ | [实测] |
| 结论值判据 J4 | ★J4 的比较【故意不读】`arrangement` 字段 ⇒ 标签怎么改都不影响结论值判定 ★ | ★J4 自证: 把 `arrangement` 换成实测 token 与换成 `9x9_staggered`, J4 的判定结果逐字相同 ★ | [实测] |

★**⇒ 结论: ★**订正块可以落, 落了本闸不会新增红; 但落成错值本闸会当场红** ★ (★`--strict-open` 开关还能让本闸在「已签收页仍带未落订正的错标签」时主动报红, 供 main 看红态·★默认不判红★) ★

---

## §3 `G5` 盲区的机器判据设计 (★维数逐字对比 + 三条反向用例★)

### §3.1 盲区的确切位置 (★行号可查·★本机实读★)

| 位置 | 旧闸 `G5` 的实际判据 | 缺的判据 | 证据 |
|---|---|---|---|
| `MECH/check_jdebug_1p27_clearance.py` L589~L591 | ★页面 `arrangement` 字符串里【含】 `staggered` 或 `交错` ★ | ★**页面声明的【列数 / 行数】与【闸自己实测的列数 / 行数】逐字对比** ★ | [实测] |
| 同上 | ★`arrangement` 字符串【非空】 ★ | ★**维数相等性** ★ | [实测] |

★**⇒ 判据形状** (★本单 `MECH/check_jdebug_arrangement_truth.py` 的 `J2` 就是它·★旧闸一个字节都没改★): ★**页面声明的 `arrangement` 规范化之后, 必须与闸自己解析 `.kicad_mod` 实测出来的维数 token 逐字相等; 不等 ⇒ 红, 并点名是列数差、行数差、还是交错限定词差** ★

### §3.2 规范化口径 (★只允许这四种·其余逐字★)

| 步骤 | 处理 | 为什么允许 | 证据 |
|---|---|---|---|
| ① | 去首尾空白 + 去内部空白 + 折小写 | ★纯排版差异不算错标签★ | [推算] |
| ② | 全角 `×` / `＊` / `*` → 半角 `x` | ★同一个乘号两种写法★ | [推算] |
| ③ | `交错` → `_staggered` ; `直排` → `_inline` | ★中英文同义写法★ | [推算] |
| ④ | 独立的 `staggered` → `_staggered` (★前有下划线则不重复补★ ⇒ 幂等不动点★) | ★规范化必须幂等, 否则自己和自己比不过★ | [推算] |

★**维数的数字与列/行顺序必须逐字相等; 规范化只动空白与分隔符** ★ [推算]

### §3.3 ★三条反向用例 (★旧 `G5` 对这三条全绿★)

| # | 反例 (★把页面声明的维数改成★) | 旧 `G5` 的读数 | 新判据 `J2` 的读数 | 红的理由 | 证据 |
|---|---|---|---|---|---|
| 1 | `2x2_staggered` | ★绿 (★只查「含交错」·★`2x2` 里有 `staggered`★)★ | ★红★ | ★列数对、行数差 (声明 2 行 ≠ 实测 4 行) ★ | [实测] |
| 2 | `2x4` (★丢掉交错限定词★) | ★绿 (★含 `staggered`? 不含 ⇒ 旧闸其实会红; ★但 `2x4` 与 `2x4_staggered` 在【维数】上完全一样·★旧闸无从区分·★本条测的是【本闸的规范化不动点】★)★ | ★红★ | ★交错限定词差 (声明 无 ≠ 实测 `_staggered`) ★ | [实测] |
| 3 | `9x9_staggered` | ★绿 (★含 `staggered`⇒旧闸全绿★)★ | ★红★ | ★列数差、行数差 ★ | [实测] |

★**⇒ 第 1 条与第 3 条是旧 `G5` 的【真盲区】: ★页面把维数写成任何带「交错」二字的值, 旧闸照样绿** ★ [实测]

### §3.4 为什么本单不直接改旧闸 (★代价·★不代拍★)

| 选项 | 代价 | 本单做没做 | 证据 |
|---|---|---|---|
| 直接改 `MECH/check_jdebug_1p27_clearance.py` 的 `G5` | ★已签收件一个字节都不许动 (★ISS-371 已签收★)★ | ★**没做** ★ | [实测] |
| 新闸独立挂 | ★本单零挂链 (★挂链是 main 的地界★)★ | ★**没做 (零挂链)** ★ | [实测] |
| 新闸独立存在 + 给出建议 | ★由 main 裁是「改旧闸」还是「新闸独立挂」★ | ★**本单交付的是这条建议 + 完整判据 + 反向用例** ★ | [实测] |

### §3.5 ★本闸把这条判据落成了什么 (★可逐条复跑★) ★

| 闸内判据 | 做什么 | 反向用例 | 证据 |
|---|---|---|---|
| ★`J2` 机器块 `arrangement` 与实测维数逐字对比 ★ | ★规范化后与闸自己解析 `.kicad_mod` 实测出的 token 逐字相等才算绿; 不等 ⇒ 红并点名是列数差、行数差、还是交错限定词差 ★ | ★③ `2x2 staggered` / ④ `2x4` / ⑤ `9x9 staggered` 三条各红 ★ | [实测] |
| ★`J3` 已签收页排布表述逐处扫出 ★ | ★所有「几列 × 几行 / NxM」表述逐处抠出来; 与实测不符的【一处都不许漏】⇒ 每一条都要在订正台账里登记 ★ | ★⑥ 多一处没登记的错标签 ⇒ J3 红; ⑦ 台账删掉一条 ⇒ J3 红 ★ | [实测] |
| ★`J4` 结论值独立重算 + 判据分离自证 ★ | ★只用 `.kicad_mod` pad 坐标 + 权威开口 X/Y + `CRIT` 重算; 且【不读】标签字段 ★ | ★⑧ 结论值改错 ⇒ J4 红 ★ | [实测] |
| ★落地用例 ⑪ ★ | ★main 落完 7 条订正块 ⇒ 本闸红组必须是 `∅` ★ | ★⑪ 实跑 ⇒ 全绿 ★ | [实测] |

★**自检总账**: ★**`python3 MECH/check_jdebug_arrangement_truth.py --selftest` ⇒ 11 条用例 (10 条反向用例 + 1 条落地用例) 全抓到, 末行 `ALL TESTS PASS`** ★ [实测]

### §3.6 ★盲区的【实跑证明】 (★不是断言·★是沙盒里真跑出来的★) ★

★**做法**: ★**在沙盒 `tmp/iss382_sbx/blindspot/` 里, 把已签收页机器块的 `land_smd.arrangement` 改成 `9x9 staggered` (★一个凭空编出来的维数★) ⇒ 跑旧闸 `MECH/check_jdebug_1p27_clearance.py` 与本单新闸** ★

| 跑哪个闸 | 读数 | 说明 | 证据 |
|---|---|---|---|
| ★旧闸 `G5` (ISS-371 已签收闸) ★ | ★`[G5] … ⇒ ✅ PASS` · 旧闸 rc=0 ★ | ★**旧闸照样绿** ⇒ ★**盲区是实测成立的, 不是推测** ★ | [实测] |
| ★本单新闸 `J3` ★ | ★❌ FAIL · 逐条点名: `L392 的排布表述 '9x9' (=9列×9行) 与实测 2x4_staggered 不符, 且【不在订正台账里】⇒ 漏登记` ★ | ★**旧闸放过的, 新闸当场抓住并点名行号** ★ | [实测] |
| ★本单新闸 `J2` (★把【本单新页】的维数改成 `9x9 staggered`★) ★ | ★❌ FAIL · 逐项点名: `列数: 声明 9 ≠ 实测 2` / `行数: 声明 9 ≠ 实测 4` ★ | ★**J2 就是旧 `G5` 缺的那一条: 声明的维数必须与实测维数逐字相等** ★ | [实测] |

★**复现命令**: ★`python3 tmp/iss382_sbx/prove_g5_blindspot.py` ★ (★原始输出存 `logs/iss382/prove_g5_blindspot.log`★)

---

## §4 未决项 (★只起草·★不代拍·★全部登记成 `needs_from` to=main★)

| # | 要 main 回答什么 | 本单给了什么事实 | 证据 |
|---|---|---|---|
| 1 | ★**订正块落在哪一页 / 哪一批** ★ | ★追加到已签收页文末作 `§10` ⇒ `MECH/check_connector_clearance_caliber.py` 的 `K7` 会立刻红 2 条 (ISS-374 cont2 先例) ⇒ 落点与时机有代价★ | [实测] |
| 2 | ★**`G5` 的维数对比判据怎么落进既有闸** ★ | ★判据形状 (★§3.1 + §3.2★) + ★三条反向用例 (★§3.3★) + ★完整可跑实现 `MECH/check_jdebug_arrangement_truth.py` 的 `J2`★ | [实测] |
| 3 | ★**「标签错」要不要连带改页里引用该标签的结论句** ★ | ★逐处列清了 (★§2.1 七处该改 + 四处不该改 + §2.2 十五个数值结论不变★)★ ⇒ 由 main 裁 | [实测] |
| 4 | ★**新闸挂不挂 `state/gate_check.py`** ★ | ★本单零挂链 (`grep -c` = 0) ⇒ 挂不挂由 main 裁★ | [实测] |

★**本单不代拍**: ★**§2.3 只起草, §3.4 只列代价, §4 只列问题 ⇒ 落点、时机、挂链三条全部留给 main** ★

---

## §5 复跑命令 (★每个数都能自己跑出来★)

```bash
# ① 新闸 (J0~J5) —— rc=0
python3 MECH/check_jdebug_arrangement_truth.py

# ② 新闸自检 (★反向用例·★末行 ALL TESTS PASS★) —— rc=0
python3 MECH/check_jdebug_arrangement_truth.py --selftest

# ③ 既有闸零漂移 (★不许变红★) —— rc=0
python3 MECH/check_jdebug_1p27_clearance.py

# ④ 既有 connector caliber 闸 —— ★K7 本来就红 2 条 (ISS-374 cont2 追加所致), 前后读数必须逐字相同★
python3 MECH/check_connector_clearance_caliber.py

# ⑤ 板三项指纹 (★零写板自证★)
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑥ 官方库件 md5 锚 (★两个 SMD 变体 + 一个 THT 变体★)
md5sum /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical*.kicad_mod

# ⑦ 零挂链自证
grep -c check_jdebug_arrangement_truth state/gate_check.py

# ⑧ 台账与闸 (★不写别人的分片★)
python3 state/merge.py && python3 state/gate_check.py && python3 state/check_brief_commands.py
```

★**板三项指纹基线** (★19 天逐字节未动★): md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ★ [实测]

<!-- MACHINE-BLOCK-BEGIN -->
```json
{
 "issue": "ISS-382",
 "agent": "mech-lead",
 "role": "结构总工",
 "date": "2026-11-24",
 "title": "J_DEBUG 排针排布标签 (维数) 订正真相",
 "scope": "纯分析 + 新建闸 + 沙盒预演; 零写板 / 零落表 / 零改已签收件 / 零改既有闸 / 零挂链 / 零外发 / 不代拍",
 "signed_page_untouched": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
 "legacy_gate_untouched": "MECH/check_jdebug_1p27_clearance.py",
 "new_gate": "MECH/check_jdebug_arrangement_truth.py",
 "new_gate_selftest": "python3 MECH/check_jdebug_arrangement_truth.py --selftest",
 "zero_hook_check": "grep -c check_jdebug_arrangement_truth state/gate_check.py => 0",
 "mod_md5_anchor": {
  "PinHeader_1x04_P1.27mm_Vertical.kicad_mod": "7a5f470c1f70d4b832be258501945385",
  "PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod": "9d6b0e63e99e6484d2cd3fa0bb28c4a5",
  "PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Right.kicad_mod": "1579ee4026795bb7a87418d0ee5f120b"
 },
 "board_baseline": {
  "md5": "611b869e13518c3c023fb178f91a0075",
  "mtime": "2026-11-06 07:07:17.362193413",
  "size": 4940213
 },
 "measured": {
  "SMD_Pin1Left": {
   "npads": 4,
   "cols": 2,
   "rows": 4,
   "col_x": [
    -1.5,
    1.5
   ],
   "row_y": [
    -1.905,
    -0.635,
    0.635,
    1.905
   ],
   "col_seq_along_y": [
    -1.5,
    1.5,
    -1.5,
    1.5
   ],
   "staggered": true,
   "arrangement": "2x4_staggered",
   "copper_w_mm": 6.0,
   "copper_h_mm": 4.46,
   "evidence": "[实测]"
  },
  "SMD_Pin1Right": {
   "npads": 4,
   "cols": 2,
   "rows": 4,
   "col_x": [
    -1.5,
    1.5
   ],
   "row_y": [
    -1.905,
    -0.635,
    0.635,
    1.905
   ],
   "col_seq_along_y": [
    1.5,
    -1.5,
    1.5,
    -1.5
   ],
   "staggered": true,
   "arrangement": "2x4_staggered",
   "copper_w_mm": 6.0,
   "copper_h_mm": 4.46,
   "evidence": "[实测]"
  },
  "THT_Vertical": {
   "npads": 4,
   "cols": 1,
   "rows": 4,
   "staggered": false,
   "arrangement": "1x4",
   "evidence": "[实测]"
  }
 },
 "arrangement_definition": "2x4_staggered = 列 == 2 且 行 == 4 且 沿 Y 递增排序后相邻两行的列号左右交替; 不要求第一行必须是左列",
 "land_smd": {
  "lib": "Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left",
  "arrangement": "2x4_staggered",
  "copper_w_mm": 6.0,
  "copper_h_mm": 4.46,
  "required_open_y_mm": 6.26,
  "evidence": "[实测]"
 },
 "conclusion_recompute": {
  "crit": 0.6,
  "tol": 0.3,
  "open_x": [
   137.85,
   148.05
  ],
  "open_y_center": 56.6,
  "rot0": {
   "copper_x": [
    139.95,
    145.95
   ],
   "copper_y": [
    54.37,
    58.83
   ],
   "clearance_x_left": 2.1,
   "clearance_x_right": 2.1,
   "worst_clearance_x": 1.8,
   "clearance_y_by_tier": {
    "0.90": 0.07,
    "2.54": 0.07,
    "4.00": 0.67
   },
   "worst_clearance_y_by_tier": {
    "0.90": -0.23,
    "2.54": -0.23,
    "4.00": 0.37
   },
   "pass_crit_y_by_tier": {
    "0.90": false,
    "2.54": false,
    "4.00": false
   }
  },
  "rot90": {
   "copper_x": [
    140.72,
    145.18
   ],
   "copper_y": [
    53.6,
    59.6
   ],
   "clearance_x_left": 2.87,
   "clearance_x_right": 2.87,
   "worst_clearance_x": 2.57,
   "clearance_y_by_tier": {
    "0.90": -0.7,
    "2.54": -0.7,
    "4.00": -0.1
   },
   "worst_clearance_y_by_tier": {
    "0.90": -1.0,
    "2.54": -1.0,
    "4.00": -0.4
   },
   "pass_crit_y_by_tier": {
    "0.90": false,
    "2.54": false,
    "4.00": false
   }
  },
  "verdict": "降级方案 (SMD 变体) 三档 Y 全红; 错的是标签, 不是这些数值结论",
  "evidence": "[实测]"
 },
 "verdict_summary": "ISS-382 结论: 错的是标签 / 维数 (2x2 => 2x4_staggered), 不是几何结论数字; 降级方案的铜箔包络与三档 Y 判决一个数字都不改; 旧闸 G5 的盲区是只查有没有写交错、从不做维数逐字对比",
 "arrangement_correction_ledger": [
  {"file": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md", "line": 45, "surface": "2 列 × 2 行", "cols": 2, "rows": 2, "staggered": true, "proposed_surface": "2 列 × 4 行", "proposed": "2x4_staggered", "note": "§1.1 降级方案表: 排布一栏写「2 列 × 2 行交错」", "evidence": "[实测]"},
  {"file": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md", "line": 203, "surface": "2 列 × 2 行", "cols": 2, "rows": 2, "staggered": true, "proposed_surface": "2 列 × 4 行", "proposed": "2x4_staggered", "note": "§2 正文: 降级方案 SMD 变体的排布描述 (★同一句里前半的「不是 1×4 直排」是 THT 变体的否定式表述, 不是缺陷★)", "evidence": "[实测]"},
  {"file": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md", "line": 207, "surface": "2 列 × 2 行", "cols": 2, "rows": 2, "staggered": true, "proposed_surface": "2 列 × 4 行", "proposed": "2x4_staggered", "note": "§2 正文: 降级方案 SMD 变体的排布描述 (与 L203 同一段落)", "evidence": "[实测]"},
  {"file": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md", "line": 288, "surface": "2 列 × 2 行", "cols": 2, "rows": 2, "staggered": true, "proposed_surface": "2 列 × 4 行", "proposed": "2x4_staggered", "note": "§2 正文: 降级方案 SMD 变体的排布描述", "evidence": "[实测]"},
  {"file": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md", "line": 391, "surface": "2x2", "cols": 2, "rows": 2, "staggered": true, "proposed_surface": "2x4_staggered", "proposed": "2x4_staggered", "note": "机器块 land_smd.arrangement 的字符串值", "evidence": "[实测]"},
  {"file": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md", "line": 471, "surface": "2x2", "cols": 2, "rows": 2, "staggered": true, "proposed_surface": "2x4_staggered", "proposed": "2x4_staggered", "note": "机器块 land_smd.verdict 判决句里的 SMD 变体排布", "evidence": "[实测]"},
  {"file": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md", "line": 719, "surface": "2x2", "cols": 2, "rows": 2, "staggered": null, "proposed_surface": "2x4_staggered", "proposed": "2x4_staggered", "note": "机器块根级 verdict_summary 总判决句里的 SMD 变体排布", "evidence": "[实测]"}
 ]
}
```
<!-- MACHINE-BLOCK-END -->
