# ISS-257 · hw-lead 任务书 (续做第 1 轮) —— G1a-7 落表已生效, 收尾 + 修红

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-16 21:1x · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**本单 = 内部活 · 原理图主线内 · 不是 PCB 布线/布局类 · 不是老板级拍板**
> ★**零外发 · 零采购 · 不联系任何供应商 · 不下单**

---

## ① 上一轮到底发生了什么 (★main 21:1x 本机实跑, 不是猜★)

**好消息 (你的落表成功了)**:
- `HW/BOM_v1.csv` 里「必装 ∩ value 含 `[待选型]`」= **0 件** ⇒ ★**`state/check_stage_g1a.py` 的 G1a-7 已经 ✅** ★
- 6 条生成命令全 rc=0 · 脚数 584 / 器件 218 / K=0 没变 · 板 `611b869e…` + `.kicad_pro` `3e504d2b…` 没动 ✔

**坏消息 (两条, 都得你收尾)**:

### ★① P0: 你把落表链的【证据等级词表】写错了 ⇒ `state/check_netlist.py` 由绿转红 (G1a-5 现在 ❌)

```
$ python3 state/check_netlist.py        ⇒ rc=1
  ❌ 证据等级合法 (7 档)
       非法值 ['[官网]']
```

★**根因**: 网表 (落表链) 自己的词表是 **`state/check_netlist.py` L30 的 8 档**, 里面是 **`[官方]`**, **没有 `[官网]`** ⇒ ★**你写进网表 evidence 列的 29 行 `[官网]` 全部非法** ⇒ ★**⇒ 修法只有一条: 改回 `[官方]` (落表链词表) ⇒ 在 `state/gen_netlist.py` 真源里改, 不许手改 CSV** ★

★**为什么这条重要 (别当成小事)**: ★**G1a-5 = 原理图定稿的尺子** ⇒ ★**它红 ⇒ 原理图定稿门就红** ⇒ ★**而且 ② 选型类 (BOM/选型矩阵) 用的是老板政策的 5 档 `[官网]/[实测]/[媒体]/[推算]/[0数据]` ⇒ 两套词表并存 ⇒ 本单只许改【落表链那一套】(= `[官方]`), 选型类那一套一个字不许动** ★

★**顺手**: BOM 的 evidence 列现在也是混的 (`[官方]` 45 + `[官网]` 12) ⇒ ★**你把真源里的 `[官网]` 改回 `[官方]` 并重生成 ⇒ BOM 自动统一 ⇒ 不用手改 BOM** ★

### ★② 交付物 5 件只交了 1 件 (落表本身), 缺 4 件

★**上一轮会话 `agent:hw-lead:subagent:ea25d3e9` status=timeout (20:53) ⇒ 收尾没交** ⇒ ★**盘上现状 (main 21:1x 实测)**:
- ❌ `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里**没有 §18** (落表台账没登记新 md5)
- ❌ `HW/check_g1a7_selection_landed.py` **不在盘上** (新门禁没建)
- ❌ `HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md` **不在盘上** (交卷单没写)
- ❌ `state/fragments/hw.yaml` 里**没有本单的分片** (claim/artifact/need 一条没登记)
- ⚠️ **台账没登记 ⇒ 生产链 ① 网表准入红**: `state/chain_gate.py` 报「网表 md5 `7dcf251a10ce…` ≠ 台账最新登记 `16ac89f77c25…` ⇒ 落表没进台账」⇒ ★**你补 §18 就是这条红的修法** ★

---

## ② 本轮要交的 5 件 (★一件一件来, 每件落盘就刷盘★)

### ① (P0) 修红: 证据等级词表改回 `[官方]` + 重生成链

1. ★**在 `state/gen_netlist.py` 真源里**把 evidence 写成 `[官网]` 的那 29 行改成 **`[官方]`** (★**只改 evidence 文字** · value/opn/footprint/dnp/net 一律不许动★)
2. ★**按硬顺序重生成 6 件** (★**板那条不许跑** ★ — `bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py` = 板侧 = PCB 类 = 排队不派★):
```
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py
```
3. ★**修完立刻验**: `python3 state/check_netlist.py` ⇒ ★**必须 rc=0** ★ ⇒ `python3 state/check_stage_g1a.py` ⇒ ★**G1a-5 回到 ✅** ★ (★**G1a-4 / G1a-8 仍红是正常的** — 前者等老板 A1/A2/A3, 后者等老板审阅 ISS-097★)

### ② 落表台账 §18 (`HW/SCHEMATIC_LANDING_V1_LANDED.md`)

★**沿用 §17 的格式**: 改了哪一行 (行号 + 改前/改后) · 跑了哪条命令 + 输出行 · ★**每个产物的新旧 md5 写在同一行 (四字段齐全: 单号 / 文件名 / 新 md5 / 旧 md5)** ★ · 反向用例清单 · 没落的那几条 + 为什么 ★
★**这一段是 chain_gate ① 网表准入转绿的钥匙 ⇒ 优先写它** ★

### ③ 新门禁 `HW/check_g1a7_selection_landed.py` (+ `--selftest`)

★**★这个文件现在盘上没有 ⇒ 你要先新建 ⇒ 跑它之前报 `No such file` 是正常的 (那是你要交付的东西, 不是路径写错)★**
★**判据**: ① 必装 ∩ `[待选型]` = 0 ② 14 个位号逐个点名: value 非空 / **不含占位词** / opn 非空 ③ 脚数仍是 584 / 器件 218 / K=0 ④ 板 + `.kicad_pro` md5 逐字节不变 ⇒ ★**反向用例 ≥6 条** (把某个 value 改回 `[待选型]` ⇒ 必须红; 删一个位号 ⇒ 必须红; 改脚数 ⇒ 必须红; ★**把某个 evidence 改成 `[官网]` ⇒ 必须红 (本轮 P0 的教训必须进闸!)★** …)

### ④ 交卷单 `HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md`

★**B1 病灶 / B2 改了什么 / B3 落表台账 / B4 反向自证 / B5 门禁原样输出 / B6 边界自审** ★

### ⑤ 分片 `state/fragments/hw.yaml`

★**只走 `python3 state/frag_write.py --agent hw-lead` 原子写** ★ · ★**只加本单的 key** ★ · ★**不许碰 `sw.yaml` / `mech.yaml` / `pm.yaml`** ★
★**必须含 2 条 need 给 sw-lead / mech-lead** (★**新 md5 + 台账 §18 行号 + 文件名**★) ⇒ ★**main 下一轮派 H-1 重锚 (SW 的 R6 / MECH 的 G5b+C21) ⇒ 本轮你不要碰 SW/ MECH/ 的台账** ★
★**另加 1 条 need 给 main**: ★**`U_PWR_SW` 落成 `TPS22991RAA` 是决策页 §A5/§Q2 的建议默认 ⇒ 待老板一句追认** ★ (★**不许自己把这条从老板清单里划掉★**)

---

## ③ 验收 (★main 会照这几条独立复跑, 原样贴 rc★)

```
python3 state/check_netlist.py                # ★必须 rc=0 (本轮 P0)★
python3 state/check_netlist_pins.py           # rc=0
python3 state/check_sch_erc.py                # rc=0 (ERC=0)
python3 state/check_sch_pinfull.py            # rc=0 (584=584 · K=0)
python3 state/check_stage_g1a.py              # rc=1 (★G1a-5 ✅ / G1a-7 ✅ · G1a-4+G1a-8 仍红是预期★)
python3 state/check_stage_g1a.py --selftest   # rc=0 (★不许少用例★)
python3 HW/check_g1a7_selection_landed.py     # rc=0 (★本轮新门禁★)
python3 HW/check_g1a7_selection_landed.py --selftest   # rc=0 (★反向用例全抓到★)
python3 HW/check_netlist_selfconsistency.py   # rc=0
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★仍 18 条, 一条不许上升★)
python3 HW/check_netlist_contradiction_r3.py  # rc=1 (★FINDINGS 仍 = 2 (F2+F3)★)
python3 HW/check_netlist_contradiction_r3.py --selftest       # rc=0 (★12/12 不许少★)
python3 HW/check_part_selection_matrix.py     # rc=0 (8/8)
python3 state/merge.py && python3 state/gate_check.py        # rc=0 (★Q1 18/18★)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ★前三个会变 (本轮修红所致) ★后两个必须逐字节不变: 611b869e… / 3e504d2b… ★
```

★**反向自证 (必做, 三步沙盒法)**: 把改动的几行改回旧值 ⇒ 重生成 ⇒ ★**新门禁必须 rc=1** ⇒ 装回 ⇒ rc=0 ⇒ ★**证明判据真在被读, 不是把红灯调没** ★

---

## ④ 边界 (★违反即本单作废★)

★**零外发** (不连任何供应商 · 不发邮件 · 不下单) · ★**零 clone / 零 pip install / 零大文件下载** (★本机 ≈6 KB/s ⇒ 98 MB 要 4.6 小时 ⇒ 一律不许下★) · ★**零实物** ([实测] 条数 = 0) ·
★**不碰板 / 布线 / 布局 / 板框 / 焊盘号 / 封装号** ⇒ ★**板 + `.kicad_pro` 必须逐字节不变** ★
★**不许落 V-2 / V-3 / V-4** (★老板 A1/A2/A3★) ⇒ ★**尤其 R_SUPV_DIV1/2 的最终阻值与 R_ILIM 档位一个字不许碰** ★
★**不许碰 `SW/` `MECH/` 的文件与分片** · ★**不改 `state/issue_log.yaml`** (status 留给 main) · ★**不改 `PROJECT_TRACKER.md`** · ★**不碰 `DECISION_PENDING_2026-11-16.md`** ·
★**不改判据阈值** · ★**不改 `state/check_sch_erc.py` / `check_sch_pinfull.py`** · ★**不许自签 verified** · ★**不许为了过闸而用占位词糊弄 (假绿铁律)** ★

---

## ⑤ 时间纪律 (★本项目 11-16 实测出来的铁律★)

★**你这一轮有 90 分钟, 但别把成果攒在内存里**★:
· ★**第 1 步就把 §18 落表台账写进 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 并落盘** (★那是 chain_gate ① 转绿的钥匙★);
· ★**每落一个文件就刷一次盘**; ★**交卷单写一半也算交卷** (宁可交半份带 rc 的, 不要交一份没落盘的);
· ★**沙盒反向自证放最后** (它最费时间, 但它是「判据不是摆设」的唯一证据);
· ★**若时间不够 ⇒ 交「修红 + 已重生成 + §18 + 门禁 + 交卷单草稿」**, 并在交卷单里写明还差什么 ⇒ ★**不许硬撑到超时被掐, 那样一个字都不留** ★

★**遇到任何「必须老板拍」的岔路 ⇒ 不要停: 选那个**不代拍**的分支继续做, 并把它登记成 need 交 main。 ★

---

## ⑥ 额外纪律 (★项目总工统一口径★)

① 写分片必须用 `state/frag_write.py` (禁止 `open(p,"w")`) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标 (★**报告/交卷单散文里用这 5 档; 网表 CSV 的 evidence 列用落表链自己的 `[官方]` — 两套词表各归各, 见 §①①★) ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ⑤ 交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复
