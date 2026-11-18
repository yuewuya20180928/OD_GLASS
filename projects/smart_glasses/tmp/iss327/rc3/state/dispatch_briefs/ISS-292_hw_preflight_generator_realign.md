# ISS-292 · hw-lead 任务书 —— ★★【清单页生成器与盘面页对齐 (★跑一次生成器 = 把订正全冲掉·卡动板那趟开工★)】★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 16:0x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-292 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · PCB 线·纯生成器对齐 + 作业包指针订正类** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM 真源** ★
> ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律** ★ (★本单只动生成器与作业包文本, 不动板★)

---

## ★① 病灶 (★main 16:0x 本机实读, 逐条带行号, 不抄交卷报告★)

### ★①-1 · 生成器比盘面页旧 ⇒ **谁跑一次, 谁把 ISS-283/ISS-289 的订正全冲掉**

| 位置 | 现状逐字 | 盘面页 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) 真值 |
|---|---|---|
| ★`state/_iss277_build_preflight.py:110` ★ | ★`"[实测] R3-A4: MAIN_PCB且DNP 54 颗 · 在板上 43 颗 · 零标记 43 颗"`★ | ★**51 / 40 / 40** ★ (★三次合法落表 09:58 · 12:16 · 12:30 把 `BAT_DET` 三颗改成必装★) |
| ★`state/_iss277_build_preflight.py:26` ★ | ★`"[实测] 脚表 15 条缺陷 (14 串号 + 1 缺脚); …"`★ | ★**18 条** ★ |
| ★`state/_iss277_build_preflight.py:108` ★ | ★条目 id = `B17_DNP_43` (★名字里带 43★)★ | ★**条目 id 不许改 (★它被别处引用★), 只许订正它的【值】★** |
| ★缺项 ★ | ★**生成器里没有 `B32_V2_NET_RENAME` 这一条** ★ | ★**盘面页已有 (ISS-283 落的 V-2 网改名条目)** ★ |

★**⇒ 现在这两份东西【同源关系断了】: 盘面页是手工订正后的最新值, 生成器还是旧值 ⇒ ★**跑一次生成器 = 页回退到过期值 = 把 ISS-283/ISS-289 的订正全冲掉**★ ★**

★**★而且这不是「文档脏」, 是【它会当场打红新闸】★★**: ★**新闸 `HW/check_workpack_state_values.py` 的 V1~V7 就是比对「作业包/清单页里的现状值 == 盘面实测」⇒ 生成器一跑, 页回退 ⇒ 闸当场红 (★这是闸在正常工作★) ⇒ ★**⇒ 而且这个红会出现在【动板那一趟已经开工之后】⇒ 那时候有人会去「改板凑绿」⇒ 代价 2-4 周 + ¥4-8K** ★**

### ★①-2 · 作业包 §3-S1 的位号真源指针失效 (★照字面实现找不到真源★)

★**ISS-289 交卷单登记的 need `iss289_s1_specjson_devices_missing` 的原文事实 (★main 本机复验★)**:
★**§3-S1 写「器件位号真源 = `HW/SCHEMATIC_V1_SPEC.json` (devices 段的 186 个 ref)」 ⇒ ★盘上这个 JSON 顶层只有 `meta` / `counts` / `connections` / `power_rails` / `display_select` / `testpoints` / `undrawable` 七个键, 【没有 `devices`】★ ⇒ 照字面实现会找不到真源 ⇒ ★实际真源是 `HW/netlist_v1_pins.csv` (218 器件)★**

### ★①-3 · 「动板那趟收工后重锚」还没进任何清单 (★红会被误读成「板改坏了」★)

★**need `iss289_state_baseline_reanchor_after_board_run` 的原文 (★main 本机复验★)**: ★**29 条登记里只有 4 条走台账口径, 其余 25 条是写死的现状值 ⇒ 落表/动板后必然有一批红 ⇒ ⇒ 「收工后同一次重锚 + 新闸跑绿」必须写成【那一趟收工清单里的强制项】★ ⇒ ★**最危险三条: `W11`/`C04` (封装 186 ⇒ 185) · `W09_SAME_PAD_NET` (同号异网 3 ⇒ 0) · `W12`/`C03` (156 ⇒ 155 或 156) + `W18` (1 ⇒ 156 或 157)** ★**

---

## ★② 根因一句话: 【同源关系断了 —— 盘面页靠手工订正往前走, 生成器没跟上 ⇒ 谁跑谁回退★】

★**这与 ISS-273/275/286/288 是同一个病的第七个变体: ★**判决源与产物脱钩 ⇒ 一次「重跑」动作就把最新状态抹掉★ ★**

---

## ★③ 要交的几件 (★每件都能独立验收★)

### ★B1 · 生成器与盘面页对齐 (★★重跑必须【幂等】: 重跑后盘面页不得回退★)

1. ★**`state/_iss277_build_preflight.py` 的 R3-A4 那条值必须改成 51 / 40 / 40** ★ ⇒ ★**且值不许再写死** ⇒ ★**改成从真源读** (★落表台账链头 / 盘面实测: `HW/check_netlist_contradiction_r3.py` 的 R3-A4 读数 + `HW/netlist_v1_pins.csv` 缺陷条数) ★ ⇒ ★**这样下次落表/动板后, 跑一次就是新值, 不用人来改★ ★
2. ★**脚表缺陷条数那条 (★现写 15 条★) 改成从真源读** ⇒ ★**盘面现值 18 条, 但不许写死 18, 要能自己算出来** ★
3. ★**补 `B32_V2_NET_RENAME` 这一条** (★ISS-283 落的 V-2 网改名条目 ⇒ 盘面页已有 ⇒ 生成器补齐后两边同源★) ★
4. ★**条目 id `B17_DNP_43` 不许改名** (★名字里的 43 会被别处引用★) ⇒ ★**只许订正它的【值】, 并在旁边注明「id 里的 43 是历史命名, 值已按落表链头前移」** ★

### ★B2 · 重跑幂等 (★★这是本单的核心验收, 不是 B1 的附属★★)

★**★硬判据 (★main 会照这条复验★)★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/PCB/BOARD_ONEPASS_WORKPACKET.md   # 跑前
python3 state/_iss277_build_preflight.py                                        # ★重跑生成器★
md5sum HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/PCB/BOARD_ONEPASS_WORKPACKET.md   # 跑后
```
★**⇒ 跑后必须满足【二者之一】, 都不许是「页变了」** ★
- ★**要么**: 两个 md5 与跑前**逐字节相同** (★零变化 = 最干净★) ★
- ★**要么**: 只有 `B32` 那一条**新增**, 且 ★**ISS-283/ISS-289 的九处追加式订正 anchor 一处不少、一字不删** (★用 ISS-289 §B1.3 那套 anchor 自证法自证★) ★
- ★**★绝不许**: 页里的 51/40/40 变回 54/43/43 · 18 条变回 15 条 · 任何一条 anchor 消失 ★

### ★B3 · §3-S1 位号真源指针改对 (★作业包侧★)

★**把 §3-S1 里「器件位号真源 = `HW/SCHEMATIC_V1_SPEC.json` (devices 段的 186 个 ref)」改成指向真实存在的真源 (`HW/netlist_v1_pins.csv`, ★218 器件★) ⇒ ★**按追加式订正 (★老字不删★)★ ⇒ ★**并把「为什么原指针失效 (★该 JSON 没有 devices 段★)」写进订正句★ ★

### ★B4 · 「收工后重锚」写成收工清单的强制项 (★作业包侧★)

★**在作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的收工清单里加一条【强制项】: 「★收工后同一次重锚两份文档的 state_baseline 写死期望值 + 新闸 `HW/check_workpack_state_values.py` 跑绿★」⇒ ★**并把最危险三条的重锚值写全 (W11/C04 · W09_SAME_PAD_NET · W12/C03 + W18) ★ ⇒ ★**再写一句警告: ★**「★不许为了让闸绿而把 `C_VBUS_GND` 装回板上 ⇒ 那会直接毁掉 §3-S2 的『C1 多余 0』★」★★ ★

### ★B5 · 反向用例 (★≥3 条, 每条贴原样 rc★)

| # | 构造 | 期望 |
|---|---|---|
| ① | ★**在沙盒里把落表台账链头往前跳一跳 (模拟又一次合法落表) ⇒ 重跑生成器, R3-A4 的数必须跟着变 (不许还是旧数)** ★ | ★**数变了** ★ |
| ② | ★**把生成器里的 R3-A4 值改回 54/43/43 ⇒ 重跑后盘面页必须回退 ⇒ 新闸 `check_workpack_state_values.py` 必须变红 (证明闸真在读)** ★ | ★**红** ★ |
| ③ | ★**正向对照: 一切如常 ⇒ 重跑生成器后盘面页零变化 + 新闸 rc=0** ★ | ★**绿 + 零变化** ★ |

### ★B6 · 回归 (★别的闸一条不许红★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_workpack_state_values.py;          echo "rc=$?"   # 期望 rc=0
python3 HW/check_workpack_state_values.py --selftest; echo "rc=$?"  # 期望 rc=0 (★条数只许增不许减★)
python3 HW/check_onepass_preflight_coverage.py;      echo "rc=$?"   # 期望 rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest; echo "rc=$?"
python3 HW/check_board_frame_caliber.py;             echo "rc=$?"   # 期望 rc=0
python3 state/merge.py;                              echo "rc=$?"   # 期望 rc=0
python3 state/gate_check.py;                         echo "rc=$?"   # 期望 rc=0 (Q1 18/18)
python3 state/issue_check.py;                        echo "rc=$?"   # 期望 rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… / 网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece… 必须逐字节不变★★
# ★★板 mtime 仍须是 2026-11-06 07:07:17 (★双重证明: md5 + mtime★)★★
```

---

## ★④ 交卷物 (★4 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_hw-lead_ISS292_清单页生成器对齐.md` (★B1~B6 六块齐全 + 反向用例原样 rc★) ★
2. ★**改动**: `state/_iss277_build_preflight.py` (★主改动★) + `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的追加式订正 (★§3-S1 指针 + §收工清单强制项★) ★
3. ★**沙盒 README** (★把「生成器输入/输出/真源」三件套写清 ⇒ 下一个人才知道怎么维护★) ★
4. ★**分片** `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead` 原子写 ⇒ ★**写完 `grep` 校验 `iss292` 在不在★**) ★

---

## ★⑤ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `state/gen_netlist.py` / `state/land_v_values.py`** ★ · ★**不许改 `HW/check_workpack_state_values.py` (★那是 ISS-289 的闸, 本单不许碰★)** ★ · ★**不许碰 `SW/` 与 `MECH/`** ★ · ★**零外发** · ★**不替老板拍板** (★`C_VBUS_GND` 留不留 = 老板/PM 域, 本单只交事实与代价★) · ★**不自签 issue_log** ★

★**★边界里最容易踩的一条 (★ISS-289 交卷单自己发现的副作用, 照抄提醒★)★**: ★**`HW/check_onepass_preflight_coverage.py` 每次跑都会重生成 `HW/PCB/` 下 4 个辅助文件 (`_frame_reference.kicad_pcb` / `STACKUP.md` / `GEN_SELF_CHECK.txt` / `LAYOUT_RULES.md`) ⇒ 它们的 mtime 会变 (内容逐字相同) ⇒ ★**判「有没有偷改板」必须看【官方板那两个文件的 md5 + mtime】, 不能看目录★ ★

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss292/x.log 2>&1 &` + 短轮询** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★

★**★本单为什么现在派 (★main 16:0x 实查★)★**: ★**ISS-289 已由 main 复验落 verified ⇒ hw-lead 名额空出来; sw-lead 名额被 ISS-291 占着 (★在飞★) · mech-lead 名额被 ISS-290 占着 (★在飞★) ⇒ ★**本单是此刻唯一能合法派给 hw-lead 的活★ ★**

★**★为什么它必须赶在「板只改一次」那一趟之前★**: ★**那一趟一开工, 生成器就可能被再跑一次 ⇒ 页回退 ⇒ 新闸红 ⇒ ⇒ 而那时红会被误读成「板改坏了」⇒ ⇒ 有人会去改板凑绿 ⇒ ★**最坏 = 把 `C_VBUS_GND` 装回板上 = 2-4 周 + ¥4-8K 返工**★ ⇒ ★**⇒ 生成器对齐 + 收工重锚清单, 必须在开工前落地** ★
