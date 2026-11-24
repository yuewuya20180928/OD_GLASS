# ISS-396 · hw-lead · 「板只改一次」那一趟的 FTS 排针【改孔 `0.65 → 0.71`】还没进作业包 / 预检清单 ⇒ 把 ISS-391 交回的 §4 登记项一次性落到位

> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-396 · ★**零外发** ★
> ★**性质**: ★**纯分析 + 登记落盘 (改文档/生成器) + 新建闸 · 零写板 · 零落表 · 零改既有闸的判据 · 零改已签收页正文 · 零挂链** ★
> ★**主线**: 绘制 PCB 图 ⇒ 合「板只改一次」纪律 ① (先派纯分析 / 作业包类) ★

---

## ★1 · 题 (★main 本机实读 · 不抄任何 agent 报告★)

★★**闸红着 (本轮 18:1x 实跑)**: ★

```
python3 HW/check_fts_land_drill_same_batch.py
⇒ rc=1 · 4/7 条绿 · D1/D2/D3 红
  [D1] RED  作业包 §0.2 ③ 的「③」那一项原文里【查不到「钻孔」这件事】(也查不到目标孔径 0.71)
  [D2] RED  预检清单 B33_PIN_LAND_1P27 的【描述列】(json 项 / 表格行) 里【查不到「钻孔」】
  [D3] RED  B33_PIN_LAND_1P27 的【验收手段列】里【没有一条读钻孔直径的命令】
  [D4] GREEN 两端数字自洽  [D5] GREEN MECH 侧不受影响  [D6] GREEN 零写板  [D7] GREEN cwd 无关
```
★**留证**: `state/.verify/fb67_1815/check_fts_land_drill_same_batch.py.log` (main 18:1x 实跑) ★

★★**权威登记单已经在盘, 不用你再设计**: ★**`HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md`** (★ISS-391 交卷页·★§3 = 5 处差集表·★§4 = 5+1 条逐字登记★) ⇒ ★**你这一趟 = 把 §4 落到位, 不许自己另写一套口径** ★

★★**为什么这条值钱**: 落 `FTS` 那一刻, 孔径是【继承库件默认 `0.65`】还是【按厂件规格定 `Ø0.71`】= 同一个动作 ⇒ ★**不显式改 ⇒ 投出去排针插不进 ⇒ 板改两次** ★

---

## ★2 · ★★本单必须避开的三个坑 (★全部出自 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` §0-②/§0-③·逐字依据在页上★) ★★

| # | 坑 | 本单怎么避 |
|---|---|---|
| ★**A** ★ | ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 是【生成器产物】** (`state/_iss277_build_preflight.py` 的 `build_pinland_item()` 长着 `B33_PIN_LAND_1P27`) ⇒ ★**手写进页里的话, 下一次重跑生成器就蒸发** (★ISS-343 在这个坑上栽过一次★) ★ | ★**补登记必须补在【生成器】里** ⇒ 改 `state/_iss277_build_preflight.py` ⇒ **重跑生成器** ⇒ 页自己变 ⇒ ★**不许手写页** ★ |
| ★**B** ★ | ★**`HW/check_onepass_preflight_coverage.py` 的 P4 只判「作业包 §0.2 ③ 的 `③` 在清单页有没有对应 item」⇒ 不查 `③` 底下有几条子动作 ⇒ (`WP02_BINDING["③"]` = `(["B33_PIN_LAND_1P27"], [])` ⇒ **零个覆盖令牌**) ⇒ ★**「改孔」漏了 P4 照样绿 ⇒ P4 绿 = 假绿 (第二次)** ★ | ★**该闸【已签收】⇒ 本单【不许改它的判据/源码】** ⇒ §4 #4 属于 main 的重签地界 ⇒ ★**你只把「P4 是假绿」这条事实 + 逐字改法写进交卷页交 main 拍, 一条都不代拍** ★ |
| ★**C** ★ | ★**§4 #5 (BOM `opn`/`footprint` 两栏) 属【落表】** ⇒ 落表 = 改网表/脚表/BOM ⇒ = 改板 ⇒ 违「板只改一次」纪律 ★ | ★**只给逐字改法 (哪一行哪一栏改成什么), 不许真落表** ⇒ 落表由 main 在那一趟统一走「合法改板通道」(ISS-297) ★ |

---

## ★3 · 交付物 (★四件 · 缺一件 = 不算交卷★)

### ★3-1 · 作业包侧登记 (★§4 #1★)
★**文件**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §0.2 ③ 那一行的 `③` 那一项 ★
★**做法**: ★**照 §4 #1 的逐字原文补上「钻孔 `0.65 → 0.71`」这一腿**, 并写明它与 pitch 改动同属这一项、不可只做其一 ⇒ **追加式订正, 老字一字未删** ★
★**自证**: ★改前 / 改后该文件的 md5 + 行号 + 「改了哪一行」★

### ★3-2 · 预检清单侧登记 (★§4 #2 / #3 / #6★)
★**改生成器, 不改页**: `state/_iss277_build_preflight.py` 的 `B33_PIN_LAND_1P27` 项 ⇒ ★**描述列补 drill 现状 `0.65` / 期望 `0.71` / 来源 (厂件规格 vs 库件默认) · 验收手段列补一条真能读钻孔直径的命令** (★命令必须是【真能跑出钻孔直径】的, 不许写一句自然语言·★`bash state/pcbnew_py.sh` 那条读板的路子见 §4 #3 逐字★) ★
★**重跑生成器** ⇒ `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 自己变 ⇒ ★**页里不许手写** ★
★**回填前先备份** (★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 现值 md5 记进交卷页·备份放 `tmp/iss396/`★) ★

### ★3-3 · §4 #5 的逐字改法 (★只出改法, 不落表★)
★BOM `opn` / `footprint` 两栏该填什么、依据哪一条官网证据 (★`[官网]` 那一格在 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` §1·★原文照抄★) ⇒ ★**交 main 拍, 不许自己改 BOM** ★

### ★3-4 · 新建机器闸 `HW/check_fts_land_drill_same_batch_sbx.py` (★可选但强烈建议★)
★**为什么要新建**: 既有闸 `HW/check_fts_land_drill_same_batch.py` 判的是【文档里有没有这句话】⇒ ★**它管不了「生成器重跑之后这句话还在不在」** ⇒ ★**生成器一改, 手写/漏写都可能 ⇒ 需要一道判【生成器产物 == 页】的闸** ★
★**判据建议**: ★① 生成器重跑两次 ⇒ 产物 md5 幂等 (⇒ 不许漂) ★② 页里 B33 的描述列/验收手段列含 drill 目标值与读孔命令 (⇒ §3-2 没被回退) ★③ 改生成器不许把 P4 的覆盖令牌搞丢 (★`WP02_BINDING["③"]` 仍含 `B33_PIN_LAND_1P27`·★不许顺手改 P4 判据本身★) ★④ 板三项指纹零扰动 ★⑤ `--selftest` ≥6 条反向用例 (★含: 把生成器里的 drill 文本删掉 ⇒ 必须变红 · 把页手改成有 drill 而生成器没有 ⇒ 必须变红 (★防「只改页」★) · 正向对照: 生成器有 ⇒ 绿★) ★
★**零挂链**: ★**本闸不许挂进 `state/gate_check.py`** (★挂不挂 = main 的地界★) ★

---

## ★4 · 验收命令 (★全部本机实跑 · 交卷时把输出贴进回复★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_fts_land_drill_same_batch.py          # ★必须 rc=0 且 7/7 (改前 4/7)★
python3 HW/check_onepass_preflight_coverage.py          # ★必须 rc=0 (不许因改页/改生成器而变红★
python3 HW/check_onepass_commit_order.py                # ★必须 rc=0★
python3 HW/check_preflight_regen_idempotent.py          # ★必须 rc=0 (★路径在 HW/ 下, 不在 state/ 下★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb          # ★板三项逐字节未动 (基线 md5 611b869e13518c3c023fb178f91a0075 / mtime 2026-11-06 07:07:17 / size 4940213)★
python3 state/merge.py && python3 state/gate_check.py  # ★rc 必须 0 · Q1 必须 18/18★
grep -c "iss396" state/fragments/hw.yaml                # ★必须 ≥1 (分片登记)★
```

★**板三项基线 md5** (★只读比对, 不许改★): 板 `611b869e13518c3c023fb178f91a0075` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` ★

---

## ★5 · 边界自证 (★逐条自证 · 写进交卷页★)

| 边界 | 要求 |
|---|---|
| ★**零写板** ★ | 板 `.kicad_pcb` / `.kicad_pro` 一个字节不许动 |
| ★**零落表** ★ | 网表 / 脚表 / BOM / 原理图真源一个字节不许动 (§4 #5 只出改法) |
| ★**零改既有闸判据** ★ | `HW/check_fts_land_drill_same_batch.py` / `HW/check_onepass_preflight_coverage.py` 源码不许动 (§4 #4 交 main) |
| ★**零改已签收页正文** ★ | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 只许【追加式订正块】+ 生成器重跑 ⇒ 老字一字未删 (★用 md5 前缀比对自证★) |
| ★**零挂链** ★ | 新闸不许进 `state/gate_check.py` |
| ★**零外发** ★ | 不发任何邮件 / 询价 / 问询 / 采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 查不到就写降级方案 ⇒ **没有「等一句可以发」这个选项** |
| ★**不代拍** ★ | §4 #4 / #5 的取舍交 main ⇒ 每条带「问法 + 不答后果 + 建议默认值」 |
| ★**不自签 issue_log** ★ | `state/issue_log.yaml` 一个字节不许动 (★签收是 main 的活★) |
| ★**只写自己分片** ★ | 只写 `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead`★) ⇒ `sw.yaml` / `mech.yaml` / `pm.yaml` 一个字节不许碰 |
| ★**沙盒只落项目盘** ★ | 临时产物只写 `tmp/iss396/` · 留证只写 `logs/iss396/` ⇒ **不许往系统 `/tmp` 写** (★本机 `/tmp` 配额打满 ⇒ 写那儿会出假读数 rc=120★) |

---

## ★6 · 落盘顺序 (★按 LESSONS.md L-13「先落盘, 再继续」· 宁可交半成品, 不要交零成品★)

1. ★**≤6 min**: 写 `tmp/iss396/plan.md` (★把 §4 的 5+1 条逐条抄成【改哪一行 · 改成什么 · 依据哪一行】的施工单★) ⇒ ★**这一步落盘 = 本单已经有产出** ★
2. ★**≤12 min**: 改 `state/_iss277_build_preflight.py` (★先备份到 `tmp/iss396/`★) ⇒ 重跑生成器 ⇒ 页自己变 ⇒ ★**这一步落盘 = 主体产出** ★
3. ★**≤8 min**: 改 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §0.2 ③ (★追加式★)
4. ★**≤8 min**: 跑 §4 的 5 条验收命令 ⇒ 落 `logs/iss396/verify.log`
5. ★**≤8 min**: (可选) 新建 `HW/check_fts_land_drill_same_batch_sbx.py` + `--selftest`
6. ★**≤8 min**: 写交卷页 `HANDOFF/2026-11-24_hw-lead_ISS396_FTS改孔登记落盘.md` (★B1 结论摘要 / B2 验收自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项 / B6 复现命令 + rc★) ⇒ 写分片 ⇒ 贴 rc 收工

---

## ★7 · 交卷消息必须含 (★缺一条算没交★)

★① 板三项指纹改前/改后逐字相同 ★② `HW/check_fts_land_drill_same_batch.py` 由 4/7 → **7/7 rc=0** 的输出原文 ★③ 生成器改动的前后 md5 + 页重跑前后的 md5 + 「页里老字一字未删」的 md5 前缀比对 = True ★④ §4 #4 / #5 的**逐字改法 + 不答后果 + 建议默认值** (★一条都不代拍★) ★⑤ `--selftest` 末行 `ALL TESTS PASS` (若建了新闸) ★⑥ `merge.py` rc=0 + `gate_check.py` rc=0 + Q1 18/18 ★⑦ 证据分级表 (★每一格标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★)
