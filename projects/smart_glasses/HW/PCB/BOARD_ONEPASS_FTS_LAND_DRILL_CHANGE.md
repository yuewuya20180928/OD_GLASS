# 「板只改一次」那一趟 · 排针 land 【钻孔 `0.65 → 0.71`】这条板侧改动的同批完整性真相页 (ISS-391 · hw-lead · 2026-11-24)

> ★**本单性质**: ★**纯分析 + 新建真相页 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★
> ★**触发源**: ★**main 2026-11-24 11:2x~11:4x 本机实读** —— ★**本单 ISS-387 (`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md`) 查出的「落 `FTS` 时板上钻孔必须 `0.65 → 0.71`」, 在【「板只改一次」那一趟的作业包 §0.2 ③】与【预检清单 `B33_PIN_LAND_1P27`】里【一个字都没有】** ★
> ★⇒ ★**那一趟开工时, 改孔这个动作【不在清单上】⇒ 不在清单 = 没人做 = 板投出去才发现排针插不进 ⇒ 【板改两次】** ★

---

## §0 一句话结论 (★把「漏在哪、怎么补、谁补」说死★)

★★ **落 `FTS` 时, `J_DEBUG`/`J_UART` 的钻孔必须 `0.65 → 0.71`; 而这一条【现在既不在那一趟的作业包 §0.2 ③ 里, 也不在预检清单 `B33_PIN_LAND_1P27` 里】⇒ 必须补进同一批, 否则板改两次** ★★

★★**三条支线 (本单的核心发现)** ★★
| # | 发现 | 证据等级 | 本单态度 |
|---|---|---|---|
| ★0-① ★ | ★**落 FTS 的那一趟要换的是【THT 直插封装】, 而换封装那一刻【钻孔是继承库件默认值还是按厂件规格定】, 两件事是【同一个动作】** ⇒ ★**库件默认 `(drill 0.65)` 偏小 `0.06` mm ⇒ 必须显式改成 `Ø0.71`** ★ | ★`[实测]` (本机自解析 `.kicad_mod`) + `[官网]` (Samtec 官方推荐 PCB 图) ★ | ★**登记 (§4)** ★ |
| ★0-② ★ | ★**现有覆盖度闸 `HW/check_onepass_preflight_coverage.py` 的 P4 判的是「作业包 §0.2 ③ 的 `③` 这一项, 在清单页有没有对应 item」⇒ ★**不查 `③` 底下有几条子动作** ⇒ (`WP02_BINDING["③"]` = `(["B33_PIN_LAND_1P27"], [])` ⇒ **零个覆盖令牌**) ⇒ ★**「改孔」这条子动作漏了, P4 照样绿 ⇒ 【P4 绿 = 假绿 (第二次)】** ★ | ★`[实测]` (本机实读源码 L251~L258 / L315~L362) ★ | ★**登记 (§4 #4) · 本单零改那个闸 (它已签收)** ★ |
| ★0-③ ★ | ★**预检清单页是【生成器产物】** (`state/_iss277_build_preflight.py` 的 `build_pinland_item()` 长着 `B33_PIN_LAND_1P27`) ⇒ ★**手写进页里的话, 下一次重跑生成器就蒸发 ⇒ ISS-349 已经在这个坑上栽过一次 (原话: 「ISS-343 把 `B33_PIN_LAND_1P27` 手写进了本页 = 生成器产物 ⇒ 重跑就蒸发」)** ⇒ ★**所以「补登记」必须补在【生成器】里, 不是补在页里** ★ | ★`[实测]` (本机实读 `state/_iss277_build_preflight.py` L365~L400 / L689~L694) ★ | ★**登记 (§4 #6 · 本单零改生成器)** ★ |

★★**本单交的是「登记 + 闸」, 不是「改」** ★★
★**本单把该改的写成了 §4 的 5+1 条登记 (main 拿 §4 就能一次落干净), 并交了一个【能查出「没改」的机器闸】`HW/check_fts_land_drill_same_batch.py` (D1~D7) ⇒ ★**那一趟开工前, 只要 §4 没落, 这个闸当场红** ⇒ ★**清单漏项 = 可发现, 不再是「投出去才发现」** ★

---

## §1 两条数各自的出处 (★两个数必须来自【两个不同的来源】, 不许互相污染★)

### §1.1 官方那条: `Ø 0.71` (TYP) ⇒ 证据等级 `[官网]`

| 项 | 值 |
|---|---|
| ★**数值** ★ | ★**`0.71` mm (TYP)**, 原文逐字 **`.028 0.71 (TYP)`** (英寸 `.028″` = `0.7112 mm` ⇒ 官网取 `0.71`) ★ |
| ★**文档** ★ | ★**Samtec 官方推荐 PCB 图打印件 `FTS-1XX-XX-XX-DX-XX-FOOTPRINT` · REVISION N · 2014-06-10 · ECN-229757 · SHEET 1 / FIG 1 (直插 THT 孔位图)** ★ |
| ★**URL** ★ | ★`https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf` ★ |
| ★**本机落盘件** ★ | ★`tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf` ★ |
| ★**本机 md5** ★ | ★**`1cbe4a2bfa456d8fd030c8b76bdf8dd5`** ★ |
| ★**独立第二来源 (互证)** ★ | ★**Samtec 官网孔径表 `https://www.samtec.com/support/pcb-hole-sizes`: 「(.41) .016 Sq. → (.71) .028 Dia.」⇒ 方柱 lead `.016″` 对应的推荐孔径就是 `.028″ = Ø0.71`** ★`[官网]` ★ |
| ★**取证的诚实交代** ★ | ★**`www.samtec.com` 在本机一律 HTTP 429 (Cloudflare 1015) ⇒ 孔径表的文字是经搜索后端取得, 通道等级记 `[媒体]`, 内容出自 Samtec 官网 ⇒ URL 留档可复核; ★**但那份 PDF 是本机 `curl` 直连 `suddendocs.samtec.com` 亲自下载的 (HTTP 200 · md5 留档) ⇒ ★**最要紧的这条几何来源是「本机直取 + 有 md5」的** ★`[实测]` ★ |

★**复跑 (文字层逐字)** ★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
pdftotext -layout tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf - | grep -n "0.71"
md5sum tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf     # ⇒ 1cbe4a2bfa456d8fd030c8b76bdf8dd5
```

### §1.2 通用件那条: `0.65` ⇒ 证据等级 `[实测]`

| 项 | 值 |
|---|---|
| ★**数值** ★ | ★**`0.65` mm** (焊盘 `(size 1 1)` + `(drill 0.65)`; ★**J_DEBUG 4 个焊盘全 0.65 / J_UART 2 个焊盘全 0.65**) ★ |
| ★**库** ★ | ★`/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/` ★ |
| ★**件** ★ | ★`J_DEBUG` = `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` · md5 **`7a5f470c1f70d4b832be258501945385`** ★<br>★`J_UART` = `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` · md5 **`47bcbf6d0f267d543e50d4b2a8dfabf5`** ★ |
| ★**谁测的** ★ | ★**本机自解析 `.kicad_mod` (★不是抄 ISS-379/380/387 的结论★)** —— `tmp/iss387/measure_generic_part.py` (★在盘, 直接用, 别重写★) ★`[实测]` ★ |
| ★**族的辨析 (不许混)** ★ | ★**这是【KiCad 官方通用库件】, 不是【Samtec 厂件】** ⇒ ★**它身上的一切 (焊盘 `1.000` / 钻孔 `0.65` / courtyard) 都是第三方库件口径, 不是 FTS 厂件规格** ★`[实测]` ★ |

★**复跑** ★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 tmp/iss387/measure_generic_part.py          # ★钻孔 0.65 · 焊盘 1.000x1.000 · 铜箔 4.8100 / 2.2700★
md5sum /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x0{4,2}_P1.27mm_Vertical.kicad_mod
grep -o "(drill [0-9.]*)" /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod
```

### §1.3 差值

| 项 | 值 | 算式 |
|---|---|---|
| ★**差** ★ | ★**`0.06` mm** ★ | ★`0.71 − 0.65 = 0.06` ⇒ ★**通用库件偏小** (★每边 `0.03` mm★) ★`[推算]` ★ |

★★**⇒ 这两个数必须来自【两个不同的来源】才成立**: ★**`0.71` 是【厂件规格】(官网)**, `0.65` 是【库件默认】(本机实测) ⇒ ★**谁把 `0.65` 当成「厂件规格」写进任何文档, 就是把第三方库件的值冒充实测的厂件规格** ★

### §1.4 ★★现状板上的排针 land 【连钻孔都没有】★★ (★本机实读 · 这条决定了「改孔」到底是什么意思★)

★**本机实读 (`bash state/pcbnew_py.sh`)**: ★
```
J_DEBUG pad1..4  type=SMD(1)  size 0.2750 x 0.9000  drill 0.0000  at X 142.2/142.7/143.2/143.7 (pitch 0.50)
J_UART  pad1..2  type=SMD(1)  size 0.2750 x 0.9000  drill 0.0000  at X 18.64/19.14 (pitch 0.50)
FPID = '' (空)   ⇒ 板上这两个封装【不是】任何库件 (是本项目自绘的 SMD land)
```
★`[实测]` ★

★★**⇒ 这就把「改孔」这句话的准确含义钉死了** ★★
★**现在板上是【SMD 小焊盘、根本没有钻孔】⇒ 「`0.65 → 0.71`」不是「把板上已有的孔改大」, 而是: ★**E-1 那一趟换 THT 封装时, 新封装带进来的孔径默认是【库件的 `0.65`】, 必须被显式定成【厂件的 `Ø0.71`】** ★★ ⇒ ★**如果那一趟直接调用通用库件封装就重出板, 板上的孔就是 `0.65` ⇒ 排针插不进 ⇒ 板投出去才发现 ⇒ 板改第二次** ★

★**复跑** ★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print('; '.join('%s type=%d size=%.4fx%.4f drill=%.4f'%(f.GetReference(),p.GetAttribute(),pcbnew.ToMM(p.GetSize().x),pcbnew.ToMM(p.GetSize().y),pcbnew.ToMM(p.GetDrillSize().x)) for f in b.GetFootprints() if f.GetReference() in ('J_DEBUG','J_UART') for p in f.Pads()))"
```

---

## §2 「改孔」这条板侧动作的完整规格 (★这一段是本单最要紧的: 【同批】的粒度要说清★)

| 项 | 规格 | 证据等级 |
|---|---|---|
| ★**作用对象** ★ | ★**只有 `J_DEBUG` (4 位) 与 `J_UART` (2 位) 两件** ⇒ ★**不牵连板上任何别的器件** ★ | ★`[实测]` ★ |
| ★**作用对象是什么** ★ | ★**这两个位号在 E-1 那一趟要换的【THT 直插 1.27 mm 封装】** (★现状是本项目自绘 SMD land `0.2750×0.9000` · 无孔 · pitch `0.50`★) ⇒ ★**改孔 = 换封装这个动作里, 把新封装的 `drill` 从【库件默认 `0.65`】定成【厂件 `Ø0.71`】** ★ | ★`[实测]` (板读) + `[官网]` (厂件规格) + `[推算]` (动作定义) ★ |
| ★**改哪个值** ★ | ★**`drill`: `0.65` → `0.71` mm (每边 +`0.03`)** ⇒ ★**目标值 = `0.71`, 不是 `0.65`** ★ | ★`[官网]` + `[实测]` ★ |
| ★**改什么** ★ | ★**只改【孔径】; ★不改孔位** ⇒ ★**排距 (1.27 mm) 不动 · 一排孔中心跨距 (3.810 / 1.270) 不动 · 孔中心坐标不动** ⇒ ★**⇒ 改孔【不产生任何新的走线改动】, 只改板内孔径** ★ | ★`[推算]` (孔位由排距与跨距唯一决定, 孔径不进孔位) ★ |
| ★**不改什么 (铜箔)** ★ | ★**铜箔包络不动** ⇒ ★**焊盘 `1.000×1.000` 不动 ⇒ 沿脚排铜箔总宽 `4.8100` / `2.2700` 不动 ⇒ MECH 全链余量数不动 (详见 §6)** ★ | ★`[实测]` + `[推算]` ★ |
| ★**改孔顺序 (物理上不可分)** ★ | ★**换 THT 封装时, 焊盘阵列与孔径是【同一个封装定义里的同一组数据】⇒ 【换封装】这一个动作同时决定【排距】与【孔径】⇒ ★**技术上不可分批做** ★ | ★`[推算]` (封装 = 焊盘 + 孔 的同一份定义) ★ |
| ★**与 `E-1` 的 pitch 改动的关系** ★ | ★**同一项 `③` 的两条腿** ⇒ ★**详见 §5 (本单给结论 + 依据)★** ★ | ★`[推算]` ★ |
| ★**同批粒度 (★机器块里的三值枚举★)** ★ | ★**`same_batch_two_legs` (本单的技术结论) / `two_independent_actions` / `undecided`** ⇒ ★**本单给第一条; ★**【清单上写一条还是两条】这个措辞口径归 main (机器块 `same_batch_granularity_decision` = `not_decided_here`) ★ | ★`[推算]` (技术) + 不代拍 (口径) ★ |
| ★**落 FTS 那一刻还要一起落的** ★ | ★**① 孔径 `0.71` · ② 封装来源 (板上的封装 与 BOM 型号栏 必须指向同一家同型号 —— ISS-387 §5-③ 已登记的 A2/A4 缝) · ③ BOM `opn`/`footprint` 两栏 (见 §4 #5)** ★ | ★`[实测]` + `[官网]` ★ |

★**★不落 FTS, 只用通用库件行不行?** ★
★**行, 但必须把孔径显式改成 `0.71`**: ★**通用库件的排距 `1.27` 与 Samtec 厂件一致 (✓), 焊盘 `1.000` 是 IPC 口径的选择 (偏离 D-1, ISS-387 已登记), 唯独【钻孔 `0.65` 与厂件 `0.71` 冲突】⇒ ★**这一条不显式改, 就没有任何机器判据会拦它** ⇒ ★**这正是本单要补进清单的那一格** ★`[推算]` ★

---

## §3 现状差集表 (★逐条点名 5 处 (main 本机实读口径·本单自己复核过一遍)★)

| # | ★该补在哪★ | ★现状 (本机实读)★ | ★补的内容 (逐字见 §4)★ | ★缺了会怎样★ |
|---|---|---|---|---|
| ★**1** ★ | ★**`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §0.2 ③ 那一行的 `③` 那一项** ★ | ★**只写「land 0.50→1.27mm」**: ★`③` `J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm (★E-1·实物排针落不进·main 18:4x 裁决: 按 1.27 定, 板 land 改★) ★ | ★**补上「钻孔 `0.65 → 0.71`」这一腿**, 并写明它与 pitch 改动同属这一项、不可只做其一 ⇒ ★**文字见 §4 #1** ★ | ★**那一趟的执行清单上只有一条「改 pitch」⇒ 换封装时孔径继承了库件 `0.65` ⇒ 板投出去才发现排针插不进 ⇒ 【板改两次】** ★ |
| ★**2** ★ | ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` item `B33_PIN_LAND_1P27` 的【描述列】(标题 + 现状)** ★ | ★**标题只有 pitch**: ★`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm (E-1 · 实测排针落不进 · main 11-17 18:45 拍死); ★**现状列只讲板读 pitch 与铜箔, 一个「钻孔 / 孔径 / Ø」都没有** ★ | ★**补上 drill 的现状与期望** (`0.65` 现状 / `0.71` 期望 / 来源) ⇒ ★**文字见 §4 #2** ★ | ★**清单页是【验收凭据】: 它不写钻孔, 那一趟做完没人知道孔有没有改 ⇒ 改没改都没人查 ⇒ 同 #1 的后果** ★ |
| ★**3** ★ | ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` item `B33_PIN_LAND_1P27` 的【验收手段】列 (`criterion`)** ★ | ★**只给一条读 pitch 的命令**: ★`bash state/pcbnew_py.sh -c "…print('; '.join('%s land pitch = %.2f'…"` ⇒ 期望读数: J_DEBUG land pitch = 1.27 / J_UART land pitch = 1.27 ★ | ★**补一条【读钻孔直径】的验收命令** (★照 `tmp/iss387/measure_generic_part.py` 的形状写, 别自己编★) ⇒ ★**命令与期望读数见 §4 #3** ★ | ★**没有验收手段 = 改没改成没人知道 ⇒ 只能等板投出去、电子装不进去时才发现 ⇒ 【板改两次】** ★ |
| ★**4** ★ | ★**`HW/check_onepass_preflight_coverage.py` 的 `WP02_BINDING["③"]` 覆盖令牌** ★ | ★**`"③": (["B33_PIN_LAND_1P27"], [])` ⇒ 零个覆盖令牌** ★ ⇒ ★**P4 判的是「作业包 ③ 的 `③` 这一项, 在清单页有没有对应 item `B33_PIN_LAND_1P27`」⇒ ★**不查 `③` 底下有几条子动作** ⇒ ⇒ ★**「改孔」漏了 P4 照样绿 = 【假绿 (第二次)】** ★ | ★**★本单【不许改这个闸】(★它已签收 · 钉板闸④ · 已挂进门禁链★) ⇒ 只在 §4 登记「需要加什么覆盖令牌」+ 落 `needs_from` to=main ★** ★**建议值: 覆盖令牌补 `["0.71", "0.65"]` (★加严, 不放宽★) ⇒ 详见 §4 #4 的顺序说明** ★ | ★**假绿不落 ⇒ 这一格永远没人守 ⇒ 下一次再漏一条子动作还是绿的 ⇒ 纪律 ① 的执行体永远漏一格** ★ |
| ★**5** ★ | ★**`HW/BOM_v1.csv` L71 (`J_DEBUG`) / L77 (`J_UART`) 的 `opn` + `footprint` 两栏** ★ | ★**本机 csv 解析实测: `footprint` 栏 = 「待定」, `opn` 栏 = 【**空字符串**】(★**不是**「待定」·★ISS-387 §5-④ 那句「两栏现在都还是待定」在 `opn` 这一栏不准确 ⇒ 本单照实更正, 但不改 ISS-387 那页★); `evidence` 栏 = `[推算]`** ★ ⇒ ★**ISS-387 §6-③ 已给出候选值 + 偏离 D-1/D-2/D-3 登记, 但【本单零落表】** ★ | ★**登记「那一趟要落的栏位与值」**: `opn` = `FTS-104-01-F-S` / `FTS-102-01-F-S`; `footprint` = 指向【钻孔 `0.71`】的那个封装 (★封装来源归 main, 见 §4 #5★) + 孔径 `0.71` + 偏离登记 ⇒ ★**落表时机 = E-1 那一趟的同一次落表/重出** ★ | ★**落 FTS 那一刻封装来源与 BOM 型号栏不同源 ⇒ 同源纪律破 (ISS-387 `OI-387-3` 已算过: 投板后才发现 ⇒ 2-4 周返工) ⇒ 【板改第二次】** ★ |
| ★**6** ★ (★追加★) | ★**`state/_iss277_build_preflight.py` 的 `build_pinland_item()` (★预检清单页的【生成器】★)** ★ | ★**预检清单页 = 生成器产物; `B33_PIN_LAND_1P27` 长在生成器里 (L689~L694 + L365~L400), 现状值全部现读板** ⇒ ★**手写进页里的字, 下一次重跑生成器就【蒸发】(★ISS-349 已经在这个坑上栽过一次, 原话照抄见 §0-③★)** ★ | ★**★在生成器的 `build_pinland_item()` 里把 drill 的现状/期望/验收命令一起长出来 (★现状值照样现读板, 不许写死★) ⇒ 位置见 §4 #6** ★ | ★**补在页里而不补在生成器 ⇒ 重跑一次就没了 ⇒ §3 #2/#3 的登记【自动蒸发】⇒ ★**白补** ★ |

★★**⇒ 这 6 处的共同点 (★本单的判断依据★)**: ★**前 3 处是【那一趟要照着做的清单】, 第 4 处是【守住清单的闸】, 第 5 处是【落表时的同源纪律】, 第 6 处是【保证前 3 处不蒸发】⇒ ★**一处都不落, 改孔这条动作就还在「没人做」的状态** ★

---

## §4 「要 main 落什么」登记表 (★本单的交卷主体 · main 拿这一节就能一次落干净, 不用回头查★)

> ★**纪律**: ★**本单【零改既有页面正文】·【零改既有闸】·【零落表】⇒ 下面 6 条全部登记给 main; ★**谁落 = main (已签收件 + 落表通道都在 main 地界)** ★
> ★**每条都给了逐字文本** ⇒ ★**main 直接照抄即可, 不用再推敲措辞** ★

### ★#1 · 作业包 §0.2 ③ 的 `③` 那一项 (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L47★)★

★**现状 (逐字)** ★
```
③`J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm (★E-1·实物排针落不进·main 18:4x 裁决: 按 1.27 定, 板 land 改★)
```
★**建议改成 (逐字, 直接替换 `③` 那一项的正文)** ★
```
③`J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm + 钻孔 0.65→0.71mm (★ISS-391·落 FTS 必须用 Samtec 官方 Ø0.71 TYP (官网推荐 PCB 图 `.028 0.71 (TYP)`)·通用库件默认 (drill 0.65) 偏小 0.06·★同属这一项的两条腿, 不可只做其一★) (★E-1·实物排针落不进·main 18:4x 裁决: 按 1.27 定, 板 land 改★)
```
★**为什么本单不落** ★: ★**作业包是【已签收件】· 本单零改既有页面正文** ★
★**落下去之后必须一起看的** ★: ★**`wp02_tokens()` 会从 `③` 的原文里自动抽出「小数」当覆盖令牌 ⇒ 补上 `0.65` 与 `0.71` 之后, 现有 P4 会自动要求清单页 `B33_PIN_LAND_1P27` 里也能查到这两个数 ⇒ ★**⇒ §3 #2 / #3 必须同步落, 否则 P4 会当场红** (★那正是 P4 在干的事, 不是 bug★)** ★

### ★#2 · 预检清单 `B33_PIN_LAND_1P27` 的【描述列】(标题 + 现状)★

★**标题 (逐字, 替换现标题)** ★
```
`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm + 钻孔 Ø0.65→Ø0.71mm (★ISS-391·落 FTS 官方 Ø0.71 TYP·库件默认 0.65·不可只做 pitch★) (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)
```
★**现状列 (逐字, 在现文末尾追加)** ★
```
★**ISS-391 追加 [实测]**: 现状板上 `J_DEBUG`/`J_UART` 是自绘 SMD land (焊盘 0.2750×0.9000 · **无钻孔** · pitch 0.50); E-1 那一趟换 THT 1.27mm 封装时, 若直接调用通用库件 `Connector_PinHeader_1.27mm:PinHeader_1x0{4,2}_P1.27mm_Vertical`, 新封装带来的钻孔是 **(drill 0.65)** ⇒ 比 Samtec 官方 `Ø0.71 (TYP)` 小 0.06 ⇒ 方针排针插不进 ⇒ **故孔径必须在换封装这一次动作里定成 0.71** ⇒ 与 pitch 同属 ③, 不可只做其一
```
★**为什么本单不落** ★: ★**预检清单页是【已签收件】· 本单零改既有页面正文** ★
★**★必须落在【生成器】里, 不许只落在页里★** ⇒ 见 §4 #6 ★

### ★#3 · 预检清单 `B33_PIN_LAND_1P27` 的【验收手段】列 (`criterion`)★

★**在现文末尾追加 (逐字)** ★
```
; `bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print('; '.join('%s drill = %.2f'%(f.GetReference(), pcbnew.ToMM(p.GetDrillSize().x)) for f in b.GetFootprints() if f.GetReference() in ('J_DEBUG','J_UART') for p in f.Pads()))"` ⇒ 期望读数: J_DEBUG drill = 0.71 / J_UART drill = 0.71
```
★**为什么本单不落** ★: ★**同上 (已签收件 + 生成器产物)** ★
★**命令形状的出处** ★: ★**照 `tmp/iss387/measure_generic_part.py` 的 `GetDrillSize()` 口径写 (★ISS-387 已用同一口径自解析库件★), 不另编** ★

### ★#4 · 覆盖度闸 `WP02_BINDING["③"]` 的覆盖令牌 (★`HW/check_onepass_preflight_coverage.py` L254★)★

★**现状 (逐字)** ★
```python
"③": (["B33_PIN_LAND_1P27"], []),
```
★**建议改成 (逐字)** ★
```python
"③": (["B33_PIN_LAND_1P27"], ["0.71", "0.65"]),
```
★**为什么本单不落** ★: ★**★这个闸已签收 (钉板闸④) · 已挂进 `state/gate_check.py` · 本单【零改既有闸的判据/阈值】⇒ 只登记, 由 main 落** ★
★★**落之前必须知道的顺序 (★main 实读 `HW/check_onepass_preflight_coverage.py` L345~L362 得到★)** ★★
| 顺序 | 动作 | 现象 |
|---|---|---|
| ★1 ★ | ★**先改作业包 `③` 的文字 (§4 #1)** ★ | ★`wp02_tokens()` 自动把 `0.65` / `0.71` 抽成覆盖令牌 ⇒ ★**此时清单页还没写这两个数 ⇒ P4 红 (要求 `B33_PIN_LAND_1P27` 里查得到 `0.65` / `0.71`) ⇒ 这是 P4 在正确工作** ★ |
| ★2 ★ | ★**再改清单页 `B33_PIN_LAND_1P27` (§4 #2 / #3)** ★ | ★P4 转绿 ★ |
| ★3 ★ | ★**最后把令牌显式补进 `WP02_BINDING["③"]` (★可选但推荐★)** ★ | ★**作用 = 【加严】**: ★**即使以后作业包 `③` 的文字被改回去, P4 仍然要求清单页那条里查得到 `0.65` / `0.71` ⇒ ★**这一次是「加严」不是「放宽」** ★**⇒ 不落也不影响本单这一次的正确性 (第 1 步已经自动生效), 落了就多一道显式锁** ★ |

### ★#5 · BOM L71 / L77 的 `opn` + `footprint` 两栏 (★`HW/BOM_v1.csv`★)★

★**现状 (本机 csv 实测, ★列序见表头: 9=`footprint` / 10=`opn`★)** ★
★**`J_DEBUG` (L71) 与 `J_UART` (L77) 两行: `footprint` 栏 = 「**待定**」; `opn` 栏 = 【**空字符串**】(★**不是**「待定」·★ISS-387 §5-④ 写的是「两栏现在都还是待定」·★那一栏实际是空的 ⇒ 本单照实更正, 不改 ISS-387 那页·★[实测]★)** ★
★**那一趟要落的栏位与值 (★草案, 本单零落表★)** ★
| 行 | ref | `opn` | `footprint` | 备注 |
|---|---|---|---|---|
| ★L71 ★ | `J_DEBUG` | ★`FTS-104-01-F-S` (★Samtec · 4 位 1 排 直插 · 1.27 mm★) ★ | ★**指向【钻孔 `0.71`】的那个封装** ★ | ★+ 孔径 `0.71` + 偏离 D-1/D-2/D-3 登记 (ISS-387 §6-③) ★ |
| ★L77 ★ | `J_UART` | ★`FTS-102-01-F-S` (★Samtec · 2 位 1 排 直插 · 1.27 mm★) ★ | ★**同上** ★ | ★同 ★ |

★**★`footprint` 那一栏有一个还没定的岔 (★不代拍★)** ★★
★**通用库件的封装是 `(drill 0.65)` ⇒ 直接落库件名 = 落一个孔径不对的封装 ⇒ ★**要么【改用自建的 `drill 0.71` 封装】, 要么【用库件但把钻孔改掉】(★改库件会影响别的用户 ⇒ 宜做项目本地副本★) ⇒ ★**这是【封装来源】的选择, 归 main (ISS-387 `OI-387-3` 已登记的 A2/A4 缝)★** ★
★**为什么本单不落** ★: ★**BOM 是【落表】动作 · 落表时机 = E-1 那一趟的同一次落表/重出 (★落表时机本身也是 main 的口径★) ⇒ 本单零落表 ⇒ 只登记栏位与值** ★
★**代价** ★: ★**不落 ⇒ 落 FTS 那一刻封装来源与 BOM 型号栏不同源 ⇒ 同源纪律破 ⇒ 投板后才发现 ⇒ 2-4 周返工 (ISS-387 `OI-387-3` 已算过)** ★

### ★#6 · 预检清单的【生成器】`build_pinland_item()` (★`state/_iss277_build_preflight.py` L365~L400★)★

★**现状** ★: ★**`B33_PIN_LAND_1P27` 的 4 个字段由 `build_pinland_item()` 生成, 现状值全部【现读板】(★铁律 ①: 一律不许写死★); ⇒ ★**任何写在页里而不在生成器里的字, 重跑就蒸发** ★
★**要在生成器里一起长的三样** ★
| # | 落在生成器的哪一处 | 落什么 |
|---|---|---|
| ★6-a ★ | ★`build_pinland_item()` 的 `title` / `current_state` ★ | ★§4 #2 的两段逐字 ★ |
| ★6-b ★ | ★`build_pinland_item()` 的 `criterion` ★ | ★§4 #3 的追加段 ★ |
| ★6-c ★ | ★**`read_board_pin_land()` 的返回字典里加一个 `drill` 字段 (★现读板, 不写死★) ★** | ★**让「现状钻孔 = 0」这件事由板读给出, 而不是靠文字写死 ⇒ 铁律 ① 一致** ★ |

★**为什么本单不落** ★: ★**生成器是【已签收件】的产物链 · 本单零改既有页面/脚本正文 (★且生成器一改, 整页重跑 = 全页 md5 变, 影响面远超本单地界★) ⇒ 只登记** ★
★**为什么这条不能省** ★: ★**ISS-349 的原话: 「ISS-343 把 `B33_PIN_LAND_1P27` 手写进了本页 = 生成器产物 ⇒ 重跑就蒸发」⇒ ★**同一个坑, 同一个位号, 栽第二次就是明知故犯** ★

---

## §5 与 `E-1` 的关系: pitch 改 与 钻孔改 是不是同一项 `③` 的两条腿 (★本单给结论 + 依据★)

### ★§5.1 结论 ★

★★**结论: ★【是同一项 `③` 的两条腿】(机器块 `same_batch_granularity` = `same_item_two_legs`) ⇒ ★**并且必须是【同一个动作、同一次改板、同一条清单项】; 不许拆成两条可分开的动作** ★★

★**口径归属**: ★**「清单上写成一条还是两条」这个措辞口径 = main 的裁决 (机器块 `same_batch_granularity_decision` = `not_decided_here`); ★**本单给的是【技术判断】(是否可分) 与【依据】, 不是措辞裁决** ★

### ★§5.2 依据 (★四条, 逐条可核★)★

| # | 依据 | 证据等级 |
|---|---|---|
| ★**5-2-①** ★ | ★**两者作用在【同两个位号的同一块 THT 封装定义】上**: 排距是焊盘阵列的横向间距, 孔径是同一批焊盘自带的孔 ⇒ ★**换封装这一个动作同时决定两者 ⇒ 【技术上不可分批做】** ★ | ★`[推算]` (封装 = 焊盘 + 孔的同一份定义) ★ |
| ★**5-2-②** ★ | ★**两者都只影响 `J_DEBUG`/`J_UART` 两件, 不牵连任何别的器件、不动任何走线** (★孔位不动 ⇒ 走线不动★) ⇒ ★**「先做这个、过两天做那个」没有任何技术收益, 只有清单管理上的收益 ⇒ 而清单管理上的收益, 代价是【漏做】的风险** ★ | ★`[实测]` (板读: 只有这两个位号) + `[推算]` ★ |
| ★**5-2-③** ★ | ★**只做 pitch 不做 drill 的后果**: 板上得到 1.27 mm 排距 + `Ø0.65` 孔 ⇒ ★**Samtec 官方对 `.016″ (0.41 mm) 方针 lead` 的推荐孔径是 `Ø0.71` ⇒ 每边小 `0.03` mm ⇒ 排针插不进或插不稳** ⇒ ★**这一趟投出去的板, 在【电子装配那一刻】才暴露 ⇒ 【板改第二次】** ★ | ★`[官网]` + `[推算]` ★ |
| ★**5-2-④** ★ | ★**只做 drill 不做 pitch 的后果**: 排距仍 `0.50` ⇒ 实物 1.27 mm 排针根本落不进 (★这正是 `E-1` 的裁决依据★) ⇒ ★**同样板改第二次** ★ | ★`[实测]` (现状 pitch 0.50) + `[官网]` ★ |

### ★§5.3 若只做其一会怎样 (★代价, 逐条量化★)

| 情形 | 板子做完时的样子 | 暴露时机 | 代价 |
|---|---|---|---|
| ★**pitch 与 drill 都做** ★ | 1.27 mm 排距 + `Ø0.71` 孔 + 焊盘 `1.000` ⇒ ★**MECH 全链余量数一个都不用改 (见 §6)** ★ | —— | ★**零额外代价** ★ |
| ★**只做 pitch** ★ | 1.27 mm 排距 + `Ø0.65` 孔 | ★**电子装配时 (排针插不进) ⇒ 板投出去才发现** ★ | ★**板改第二次: 2-4 周 + 一批板的钱 (老板口径, ★`USER.md` 的「投板后改板 = 2-4 周 + ¥4-8K」·★[推算]·★具体金额本单不代估★)** ★ |
| ★**只做 drill** ★ | 0.50 mm 排距 + `Ø0.71` 孔 | ★**同上** ★ | ★**同上** ★ |
| ★**两条都漏 (= 今天的现状)** ★ | SMD 小焊盘, 无孔 | ★**同上** ★ | ★**同上** ★ |

★★**⇒ 结论的可执行形态** ★★
★**因为【不可分】+【拆开没有技术收益】+【拆开的唯一后果是漏做】⇒ ★**必须写成同一项的一条清单动作, 且【必须同一次改板落地】; ★**并且 —— 这是最要紧的一句 —— ★**必须有一条【能查出来「只做了一条」】的机器判据, 否则「写成一条」只是口头约定** ⇒ ★**本单交的那个闸 (`HW/check_fts_land_drill_same_batch.py` 的 D1/D2/D3) 就是这条判据** ★

---

## §6 对 MECH 侧的影响面 (★逐条点名哪些数【不动】★)

★★**一句话: ★**改钻孔【不改铜箔包络】⇒ MECH 判据链一个数都不用改 ⇒ 结构件【不必】因为这一趟再出件一次** ★★

★**为什么 (★机器可核的因果链★)**: ★**MECH 判据链吃的是【铜箔包络】, 而铜箔包络 = 【焊盘 (copper pad)】的几何; ★**钻孔在铜箔之内, 不改变铜箔的边界** ⇒ ★**改孔径只改【板内孔】, 不改【铜箔】⇒ MECH 的输入不变 ⇒ 输出全部不变** ★`[实测]` (焊盘 `1.000×1.000` 不动) + `[推算]` ★

### ★§6.1 ★**不受影响**的数名清单 (★机器块 `mech_unaffected_numbers` 的逐条来源★)★

| # | 数名 | 它是什么 | 为什么不动 | 证据等级 |
|---|---|---|---|---|
| ★1 ★ | ★**`4.8100`** ★ | ★`J_DEBUG` 沿脚排铜箔总宽 (跨距 `3.810` + 焊盘 `1.000`) ★ | ★**焊盘 `1.000` 不动 ⇒ 铜箔总宽不动** ★ | ★`[实测]` + `[推算]` ★ |
| ★2 ★ | ★**`2.2700`** ★ | ★`J_UART` 沿脚排铜箔总宽 (跨距 `1.270` + 焊盘 `1.000`) ★ | ★同上 ★ | ★`[实测]` + `[推算]` ★ |
| ★3 ★ | ★**`6.6100`** ★ | ★`J_DEBUG` 清空区 X 需求 (MECH `BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md`) ★ | ★**由 `4.8100` 推导 ⇒ 上游不动 ⇒ 不动** ★ | ★`[实测]` (谁吃这个数) + `[推算]` ★ |
| ★4 ★ | ★**`4.0700`** ★ | ★`J_UART` 清空区 X 需求 ★ | ★同上 ★ | ★`[实测]` + `[推算]` ★ |
| ★5 ★ | ★**`0.1350`** ★ | ★`J_UART` 罩住 X 名义余量 ★ | ★同上 ★ | ★`[实测]` + `[推算]` ★ |
| ★6 ★ | ★**`2.6950`** ★ | ★`J_DEBUG` 开口 X 余量 ★ | ★同上 ★ | ★`[实测]` + `[推算]` ★ |
| ★7 ★ | ★**`0.7700`** ★ | ★两件罩住 Y 余量 (吃 `copper.y = 1.0000`) ★ | ★**焊盘垂直分量 `1.0000` 不动** ★ | ★`[实测]` + `[推算]` ★ |
| ★8 ★ | ★**OI-5 三档 `1.7750`** ★ | ★清空区 X 候选档 1 ★ | ★同上 ★ | ★`[实测]` + `[推算]` ★ |
| ★9 ★ | ★**OI-5 三档 `4.0850`** ★ | ★清空区 X 候选档 2 ★ | ★同上 ★ | ★`[实测]` + `[推算]` ★ |
| ★10 ★ | ★**OI-5 三档 `4.8100`** ★ | ★清空区 X 候选档 3 (= 通用件铜箔宽) ★ | ★同上 ★ | ★`[实测]` + `[推算]` ★ |

★★**★成立条件 (★必须写下来, 否则这句话会变成一句口头结论★)★**: ★
★**① 焊盘 `1.000 × 1.000` 不动; ② 座体外形不动; ③ 孔位 (排距 1.27 / 跨距 3.810·1.270) 不动** ⇒ ★**本单只动【孔径】这一项 ⇒ 三条成立** ★
★★**★若条件破了怎么办 (★提前登记, 不留坑★)★**: ★**若 main 顺带把【焊盘直径】也改了 (★ISS-387 的偏离 D-1 就是这件事: 官方直插图不给焊盘直径, `1.000` 是 IPC 口径的选择★) ⇒ ★**MECH 全链余量数必须重算** (★每 `0.01` mm 焊盘变化 ⇒ `J_DEBUG` 清空区需求变 `0.01`, `J_UART` 罩住余量变 `0.005`·★ISS-387 §4.1-① 已算过★) ⇒ ★**那就不是本单的事了 ⇒ 归 main 拍 (ISS-387 `OI-387-1`)★** ★

### ★§6.2 与 OI-12 的关系 (★要说清「不受影响」的范围★)

★**OI-12 (「判据要求的清空区 `6.6100` 比 courtyard `6.0900` 还大 `0.5200` ⇒ 偏紧」) 这条结论的【对照物】是通用库件的 `F.CrtYd` ⇒ ⇒ 【改孔径】不影响它 (★`0.5200` 的两个数都不吃孔径★); ★**但若那一趟换成 Samtec 厂件封装, courtyard 变了 ⇒ 这条结论要重算 (★ISS-387 偏离 D-3 已登记★) ⇒ ⇒ ★**这一条不是「改孔」引起的, 是「换封装」引起的, 别混为一谈** ★`[实测]` + `[推算]` ★

---

## §7 复跑命令 + 机器块

### §7.1 复跑命令 (★每个数都能自己跑出来★)

★**前置**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses` · `export TMPDIR=$PWD/tmp` ★

| # | 命令 | 出什么 |
|---|---|---|
| 7-1 | ★`python3 tmp/iss387/measure_generic_part.py` ★ | ★**§1.2 的通用件整列** (钻孔 `0.65` · 焊盘 `1.000` · 铜箔 `4.8100`/`2.2700` · 两个 md5) ★ |
| 7-2 | ★`grep -o "(drill [0-9.]*)" /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x0{4,2}_P1.27mm_Vertical.kicad_mod` ★ | ★**§1.2 的 `(drill 0.65)` 逐字** ★ |
| 7-3 | ★`md5sum /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x0{4,2}_P1.27mm_Vertical.kicad_mod` ★ | ★**§1.2 的两个 md5** ★ |
| 7-4 | ★`pdftotext -layout tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf - \| grep -n "0.71"` ★ | ★**§1.1 的 `.028 0.71 (TYP)` 逐字** ★ |
| 7-5 | ★`md5sum tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf` ★ | ★**§1.1 的 `1cbe4a2b…`** ★ |
| 7-6 | ★`sed -n '149p' HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` ★ | ★**ISS-387 那条 `pad_drill` 行 (本单的触发源)** ★ |
| 7-7 | ★`sed -n '47p' HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ★ | ★**§3 #1 的现状 (作业包 §0.2 ③ 那一行)** ★ |
| 7-8 | ★`sed -n '63p' HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ | ★**§3 #2 / #3 的现状 (`B33_PIN_LAND_1P27` 那一行)** ★ |
| 7-9 | ★`grep -n "0\.65\|0\.71\|钻孔\|drill" HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ | ★**★确认排针改孔确实不在清单里 (命中的全是别的器件: `Q1` 的 `Package_TO_SOT_SMD` / `J_USB_C` 的 NPTH `Ø0.650`·`Ø0.762` / S10 重出钻孔)★** ★ |
| 7-10 | ★`grep -n "WP02_BINDING" -A 8 HW/check_onepass_preflight_coverage.py` ★ | ★**§3 #4 的现状 (`"③": (["B33_PIN_LAND_1P27"], [])`)** ★ |
| 7-11 | ★`sed -n '71p;77p' HW/BOM_v1.csv` ★ | ★**§3 #5 的现状 (`opn`/`footprint` 两栏 = 待定)** ★ |
| 7-12 | ★`bash state/pcbnew_py.sh -c "…(见 §1.4 的命令)…" ` ★ | ★**§1.4 的现状板读 (SMD · 无孔 · pitch 0.50)** ★ |
| 7-13 | ★`sed -n '365,400p;689,694p' state/_iss277_build_preflight.py` ★ | ★**§3 #6 的现状 (生成器里的 `build_pinland_item()` 与 `B33_PIN_LAND_1P27` 条目)** ★ |
| 7-14 | ★`grep -n "6\.6100\|4\.0700\|0\.1350\|2\.6950\|0\.7700\|OI-5\|OI-12" MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` ★ | ★**§6.1 的 MECH 侧各数** ★ |
| 7-15 | ★`python3 HW/check_fts_land_drill_same_batch.py` ★ | ★**本单新建闸 D1~D7** ★ |
| 7-16 | ★`python3 HW/check_fts_land_drill_same_batch.py --selftest` ★ | ★**闸自测 (≥8 条反向用例) ⇒ 末行 `ALL TESTS PASS`** ★ |
| 7-17 | ★`md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/BOARD_ONEPASS_WORKPACKET.md HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/check_onepass_preflight_coverage.py HW/check_fts_single_row_land_truth.py` ★ | ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文的指纹** ★ |
| 7-18 | ★`grep -c check_fts_land_drill_same_batch state/gate_check.py` ★ | ★**零挂链 ⇒ 必须是 `0`** ★ |

### §7.2 机器块 (★给下游闸读★)

```json
{
 "schema": "hw.fts.land_drill_change.v1",
 "issue": "ISS-391",
 "agent": "hw-lead",
 "updated": "2026-11-24",
 "truth_doc": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
 "board_write": "none",
 "table_write": "none",
 "existing_gate_change": "none",
 "existing_page_change": "none",
 "landing_part_decision": "not_decided_here",
 "same_batch_granularity_decision": "not_decided_here",
 "bom_landing_decision": "not_decided_here",
 "registration_owner_decision": "not_decided_here",
 "pad_diameter_decision": "not_decided_here",
 "drill_official": "0.71",
 "drill_generic": "0.65",
 "drill_target": "0.71",
 "drill_delta_mm": "0.06",
 "drill_sources": {
  "official": {
   "value": "0.71",
   "unit": "mm",
   "evidence": "[官网]",
   "quote": ".028 0.71 (TYP)",
   "doc": "Samtec RECOMMENDED PCB LAYOUT FOR FTS-1XX-XX-XX-DX-XX - SHEET 1 / FIG 1 (THT hole pattern)",
   "url": "https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf",
   "local_path": "tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf",
   "md5": "1cbe4a2bfa456d8fd030c8b76bdf8dd5",
   "cross_source": "https://www.samtec.com/support/pcb-hole-sizes -> (.41) .016 Sq. -> (.71) .028 Dia."
  },
  "generic": {
   "value": "0.65",
   "unit": "mm",
   "evidence": "[实测]",
   "lib": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty",
   "J_DEBUG": {"file": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod", "md5": "7a5f470c1f70d4b832be258501945385"},
   "J_UART": {"file": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod", "md5": "47bcbf6d0f267d543e50d4b2a8dfabf5"},
   "measured_by": "tmp/iss387/measure_generic_part.py",
   "note": "KiCad 官方通用库件, 不是 Samtec 厂件 => 它的 0.65 是库件默认值, 不是厂件规格"
  }
 },
 "board_current_land": {
  "J_DEBUG": {"mount": "SMD", "pad_size_mm": "0.2750x0.9000", "drill_mm": "0.0000", "pitch_mm": "0.50", "fp_id": "(空 = 非库件封装)", "evidence": "[实测]"},
  "J_UART": {"mount": "SMD", "pad_size_mm": "0.2750x0.9000", "drill_mm": "0.0000", "pitch_mm": "0.50", "fp_id": "(空 = 非库件封装)", "evidence": "[实测]"},
  "reading": "板上现状是自绘 SMD land (无钻孔) => 改孔 = E-1 那一趟换 THT 封装时把新封装带来的库件默认孔径 0.65 定成 0.71, 不是把板上已有的孔改大"
 },
 "affected_refs": ["J_DEBUG", "J_UART"],
 "drill_action": {
  "change": "drill 0.65 -> 0.71",
  "hole_position_unchanged": true,
  "copper_envelope_unchanged": true,
  "routing_impact": "none (孔位不动)",
  "refs_only": ["J_DEBUG", "J_UART"],
  "same_item_as_pitch_change": true,
  "split_technically_possible": false
 },
 "same_batch_granularity": "same_item_two_legs",
 "same_batch_granularity_allowed_values": ["same_item_two_legs", "two_independent_actions", "undecided"],
 "same_batch_granularity_basis": [
  "5-2-① 换封装这一个动作同时决定焊盘阵列间距与孔径 => 技术上不可分批做",
  "5-2-② 两者只影响 J_DEBUG/J_UART 两件, 不动走线 => 分批做没有技术收益, 只有漏做的风险",
  "5-2-③ 只做 pitch => 1.27 排距 + Ø0.65 孔 => 方针排针插不进 => 电子装配时才暴露 => 板改第二次",
  "5-2-④ 只做 drill => 排距仍 0.50 => 实物 1.27 排针落不进 => 板改第二次"
 ],
 "registration_gaps": [
  {"seq": 1, "file": "HW/PCB/BOARD_ONEPASS_WORKPACKET.md", "locator": "§0.2 ③ 那一行的 ③ 那一项 (L47)", "now": "只写 land 0.50->1.27mm", "missing": "钻孔 0.65->0.71 这一腿", "owner": "main", "why_not_here": "已签收件, 本单零改既有页面正文"},
  {"seq": 2, "file": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md", "locator": "item B33_PIN_LAND_1P27 的描述列 (title + current_state) (L63)", "now": "只讲 pitch 与铜箔, 无任何钻孔字样", "missing": "drill 现状 0.65 / 期望 0.71 / 来源", "owner": "main", "why_not_here": "已签收件, 本单零改既有页面正文"},
  {"seq": 3, "file": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md", "locator": "item B33_PIN_LAND_1P27 的验收手段列 (criterion) (L63)", "now": "只有一条读 land pitch 的命令", "missing": "一条读钻孔直径的验收命令 (照 tmp/iss387/measure_generic_part.py 形状)", "owner": "main", "why_not_here": "已签收件, 本单零改既有页面正文"},
  {"seq": 4, "file": "HW/check_onepass_preflight_coverage.py", "locator": "WP02_BINDING[\"③\"] (L254)", "now": "(\"③\": ([\"B33_PIN_LAND_1P27\"], [])) => 零个覆盖令牌 => P4 只查 item 存在, 不查子动作 => 假绿", "missing": "覆盖令牌建议补 [\"0.71\", \"0.65\"] (加严不放宽)", "owner": "main", "why_not_here": "已签收闸 (钉板闸④), 本单零改既有闸"},
  {"seq": 5, "file": "HW/BOM_v1.csv", "locator": "L71 (J_DEBUG) / L77 (J_UART) 的 opn + footprint 两栏 (列序 9=footprint / 10=opn)", "now": "footprint 栏 = 待定, opn 栏 = 空字符串 (ISS-387 5-④ 的「两栏都是待定」在 opn 栏不准确, 本单照实更正)", "missing": "opn = FTS-104-01-F-S / FTS-102-01-F-S; footprint = 指向钻孔 0.71 的封装; + 孔径 0.71 + 偏离 D-1/D-2/D-3 登记", "owner": "main", "why_not_here": "落表动作, 落表时机 = E-1 那一趟的同一次落表/重出"},
  {"seq": 6, "file": "state/_iss277_build_preflight.py", "locator": "build_pinland_item() (L365-L400) 与 B33_PIN_LAND_1P27 条目 (L689-L694)", "now": "预检清单页是生成器产物, 字段全现读板", "missing": "drill 现状/期望/验收命令必须在生成器里一起长出来, 否则重跑即蒸发 (ISS-349 同一位号已栽过一次)", "owner": "main", "why_not_here": "生成器是已签收链的产物, 本单零改既有脚本正文"}
 ],
 "mech_unaffected_numbers": [
  "4.8100",
  "2.2700",
  "6.6100",
  "4.0700",
  "0.1350",
  "2.6950",
  "0.7700",
  "OI-5:1.7750",
  "OI-5:4.0850",
  "OI-5:4.8100"
 ],
 "mech_unaffected_reason": "钻孔在铜箔之内, 不改变铜箔包络边界 => MECH 判据链吃的 copper.x/copper.y 输入不变 => 清空区需求/罩住余量/开口余量全部不变 => 结构件不必因这一趟再出件一次",
 "mech_unaffected_preconditions": [
  "焊盘 1.000 x 1.000 不动",
  "座体外形不动",
  "孔位 (排距 1.27 / 跨距 3.810 与 1.270) 不动"
 ],
 "mech_breaks_if_pad_changes": "若顺带把焊盘直径也改了 (偏离 D-1) => MECH 全链余量数必须重算 (每 0.01 mm 焊盘变化 => J_DEBUG 清空区需求变 0.01, J_UART 罩住余量变 0.005) => 归 main 拍 (ISS-387 OI-387-1)",
 "mech_oi12_note": "OI-12 的对照物是通用库件 F.CrtYd 6.0900 => 改孔径不影响它; 若那一趟换厂件封装则 courtyard 变 => OI-12 要重算 (偏离 D-3), 那是换封装引起的, 不是改孔引起的",
 "acceptance_commands": {
  "read_drill": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print('; '.join('%s drill = %.2f'%(f.GetReference(), pcbnew.ToMM(p.GetDrillSize().x)) for f in b.GetFootprints() if f.GetReference() in ('J_DEBUG','J_UART') for p in f.Pads()))\"",
  "expected_reading": "J_DEBUG drill = 0.71 / J_UART drill = 0.71",
  "read_land_pitch": "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print('; '.join('%s land pitch = %.2f'%(r,(lambda c:c[1]-c[0])(sorted(set(round(pcbnew.ToMM(p.GetPosition().x),4) for p in [f for f in b.GetFootprints() if f.GetReference()==r][0].Pads())))) for r in ('J_DEBUG','J_UART')))\"",
  "expected_pitch_reading": "J_DEBUG land pitch = 1.27 / J_UART land pitch = 1.27",
  "measure_generic_part": "python3 tmp/iss387/measure_generic_part.py"
 },
 "zero_perturbation_baseline": {
  "board_md5": "611b869e13518c3c023fb178f91a0075",
  "board_size": 4940213,
  "board_mtime": "2026-11-06 07:07:17.362193413",
  "netlist_md5": "6aee500e60ba0732f83a9cf557ba90ab",
  "pins_md5": "9174309df1ec9411ac8e8d9e80ee386a",
  "bom_md5": "5b9993992405904a60ac96a020b375d8",
  "workpacket_md5": "00b0ea5bae70b7f663b55b9b80014d03",
  "preflight_md5": "192873f6c977b376c28785824a82f9f1",
  "coverage_gate_md5": "fc37ea0eee9cea6a1f2b91e3d2f581dc",
  "iss387_gate_md5": "5b9570fd23d6dd7125876c9110085506",
  "iss387_truth_md5": "a2f78e769bbe9c27c44e728539206c04"
 },
 "decisions_not_made_here": [
  "landing_part_decision = not_decided_here (FTS 料号已拍, 但板侧 land 来源 A2/A4 的缝归 main)",
  "same_batch_granularity_decision = not_decided_here (技术结论 = same_item_two_legs; 清单上写成一条还是两条是 main 的措辞口径)",
  "bom_landing_decision = not_decided_here (落表时机与 footprint 栏指向哪个封装归 main)",
  "registration_owner_decision = not_decided_here (6 处登记全在 main 地界)",
  "pad_diameter_decision = not_decided_here (焊盘 1.000 是否维持 = ISS-387 OI-387-1)"
 ],
 "open_items": [
  "OI-391-1: 作业包 §0.2 ③ 的 ③ 那一条要不要补上「钻孔 0.65→0.71」这一腿 (逐字文本见 §4 #1) => to=main",
  "OI-391-2: 预检清单 B33_PIN_LAND_1P27 的描述列与验收手段列要不要补 (逐字文本见 §4 #2 / #3), 且必须同时补进生成器 (§4 #6) => to=main",
  "OI-391-3: 覆盖度闸 WP02_BINDING[\"③\"] 的覆盖令牌要不要补 [\"0.71\", \"0.65\"] (顺序见 §4 #4) => to=main",
  "OI-391-4: BOM L71/L77 的 opn/footprint 两栏落什么, 落表时机 = E-1 那一趟的同一次落表/重出 (§4 #5) => to=main",
  "OI-391-5: 同批粒度的清单措辞口径 (一条还是两条) => to=main"
 ]
}
```

---

## §8 · 追加式订正块 · ISS-396 (hw-lead · 2026-11-24 18:3x) · §4 #1/#2/#3/#6 已落位 · 机器块两枚 md5 基线随之刷新

> ★**本块是【追加式】(★老字一字未删 · 上面 §0~§7 与机器块除下表那两行外一个字没动★)** ★
> ★**为什么必须动那两行**: ★**闸 `HW/check_fts_land_drill_same_batch.py` 的 D6 拿【真文件 md5】与 `zero_perturbation_baseline` 里这两个键比** ⇒ ★**§4 #1/#2/#3 一落地, 老基线必然过期 ⇒ 不刷新 ⇒ 闸永远红 ⇒ 与本页自己写的「main 落完 §4 #1/#2/#3 ⇒ 同一条命令即转绿」自相矛盾** ⇒ ★**⇒ 故按【基线随合法落地刷新】的口径, 只刷新这两个键** ★
> ★**其余 7 个键 (板 / 网表 / 脚表 / BOM / 覆盖度闸 / ISS-387 闸 / ISS-387 真相页) 一个字节不许动** ⇒ ★**板三项指纹逐字节未动 (★`611b869e…` / `6aee500e…` / `9174309d…` / `5b999399…`★)** ★

| 键 | 旧值 (ISS-391 交卷时) | 新值 (ISS-396 落地后) | 为什么变 |
|---|---|---|---|
| `workpacket_md5` | `ae8ef08632cacd5f0aba53037d99bc95` | `00b0ea5bae70b7f663b55b9b80014d03` | ★**§4 #1 落地** (作业包 §0.2 ③ 的「③」那一项【追加】上「钻孔 `0.65→0.71`」这一腿 · 追加式 · 老字一字未删)★ |
| `preflight_md5` | `b5d8d5b94e09b011bb9f4bfd7ac10cde` | `192873f6c977b376c28785824a82f9f1` | ★**§4 #6 落地** (改生成器 `state/_iss277_build_preflight.py` ⇒ 重跑生成器 ⇒ 页自己变 · ★页里没手写一个字★)★ |

★**§4 六条登记的落地状态 (ISS-396 · 2026-11-24)**: ★

| # | 登记项 | 状态 |
|---|---|---|
| ★**#1** ★ | ★作业包 §0.2 ③ 的「③」那一项★ | ★**已落** (追加式 · 老字一字未删)★ |
| ★**#2** ★ | ★预检清单 `B33_PIN_LAND_1P27` 的描述列 (标题 + 现状列)★ | ★**已落** (在【生成器】里 ⇒ 页自己变)★ |
| ★**#3** ★ | ★`B33_PIN_LAND_1P27` 的验收手段列 (读钻孔直径的命令)★ | ★**已落** (在【生成器】里 ⇒ 页自己变)★ |
| ★**#4** ★ | ★覆盖度闸 `WP02_BINDING["③"]` 的覆盖令牌补 `["0.71", "0.65"]`★ | ★**未落** (★该闸已签收 · 本单零改既有闸判据 ⇒ 交 main 拍★) ⇒ ★**注意: §4 #1 落地后 `wp02_tokens()` 会自动抽出 `0.65`/`0.71` ⇒ P4 已经【自动】要求清单页 `B33_PIN_LAND_1P27` 里查得到这两个数 ⇒ 本次是【自动生效】, #4 只多一道显式锁** ★ |
| ★**#5** ★ | ★BOM L71/L77 的 `opn` + `footprint` 两栏★ | ★**未落** (★属【落表】⇒ 本单零落表 ⇒ 只出逐字改法 · 交 main★)★ |
| ★**#6** ★ | ★生成器 `build_pinland_item()` + `read_board_pin_land()` 加 `drill` 字段★ | ★**已落** (★现状钻孔现读板 · 不写死★)★ |

★**闸的判据一个字没动**: ★**D1~D7 的判据源码仍在 `HW/check_fts_land_drill_same_batch.py` 里逐字未改 (★md5 `dabc12000b6cecb1769bb16df09f1abb`★) ⇒ ★**变的只是它比对的两个基线值 (落地后的新值) ⇒ 闸仍然是同一道闸, 仍然是【改回去就红】** ★
