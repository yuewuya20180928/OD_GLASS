★**ISS-283 · hw-lead 任务书 —— ★★【V-2 落表解锁 + W-4 写法A 落表 + G-5 亮度档落表】★★** ★ (main · 2026-11-17 10:1x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 10:1x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-283 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 落表链侧 · 三件**★ ⇒ ★**零写板 · 零改判据阈值 · 不替老板拍板**★

---

## ① 背景 (★main 本机实测, 原样 rc★)

★**老板 2026-11-17 09:49 拍板「按照你的建议执行」⇒ 8 条决策已落账** (★`state/fragments/pm.yaml` 的 `needs_from` 8 条 + 同 key 两条 ★) ⇒ ★**其中 3 件要你做** ★

★**A1 + A2 (V-3=E + V-4=680) 已经落了** ★: `python3 state/land_v_values.py --decision V-3=E --decision V-4=680 --apply --boss-decision "2026-11-17 A1 = E" --boss-decision "2026-11-17 A2 = 680"` ⇒ **rc=0** ⇒ 网表 L182/L183/L184 已落 `100k/60k/100nF` 必装 · L47/L48 已落 `680Ω ±1%` ⇒ 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (含老板凭据机器化留痕) ★

★**★ A3 (V-2=1) 落不下去 —— 这条是你要解的第一个死锁 ★★**:

```
$ python3 state/land_v_values.py --decision V-3=E --decision V-4=680 --decision V-2=1 --apply ...
★★ rc=1: 落表后有门禁不过 ⇒ 自动回滚: ★行号锚点守卫 (ISS-262 · 纯漂移自动重锚·期望 rc=0)★: rc=1
   ❌ d4_a417_value [netlist] ★行号没变 + 实体内容变了 (台账里那颗器件在本表里找不到了) ⇒ **红**: 器件被换/被删, 锚点已指向别的行★
   ❌ d4_a417_net / d4_a417_dnp / d4_a417_note / d9_esd_dual_claim   (★五条全在 L417 = D_ESD_USB_D 那行★)
✅ rc=0: 已从 state/.bak_land_v_values_v_20261117-095506 还原 7 个文件 (★工具自带回滚★)
```

★**根因 (★main 逐行读过 `HW/check_land_row_anchors.py` L390~L432★)**: ★**V-2 的落表动作 = 把 `D_ESD_USB_D` pad1 的网名由 `USB_D_P_SRC` 改成 `NET_USB_D_P_TYPEC`** ★ ⇒ ★**这改的是守卫的【实体身份 (ref + net)】⇒ 守卫判「器件被换/被删」⇒ RED ⇒ 落表器自回滚** ★
⇒ ★**不是落表内容错, 是【落表器 ↔ 行号锚点守卫】两个工具的接口没接上** ★
⇒ ★**★不准弱化守卫的 fail-closed 那几条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红)★** ★

---

## ② 要交的三件 (★每件都能独立验收★)

### ★B1 · ★★V-2 (A3 = 1) 落表解锁 (★最要紧★★)

★**目标**: ★**让「合法落表改 net 名」成为守卫认得的一条合法通道** ★ ⇒ ★**落完 V-2 后 `D_ESD_USB_D` pad1 的网名 = `NET_USB_D_P_TYPEC`, 而守卫判 PASS 并把 registry 的身份指纹同步更新** ★

★**建议做法 (★你比我有资格定细节, 但下面三条不许破★)**:
1. ★**合法通道的判据必须是【可机器查的授权证据】**: ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里能查到 (★落表单号 + 文件名 + 该行的旧身份 + 新身份★)** ★⇒ ★**查不到 ⇒ 仍 RED** ★
2. ★**不许把 RED 改成静默 PASS**: 合法通道必须**留痕** (★registry 里记「本次身份变更由哪个单号授权」★) ⇒ ★**台账被偷改 ⇒ 仍 RED (★守卫自带 `REGISTRY_SHA256` 防偷改, 那条不许动★)** ★
3. ★**不许放宽 fail-closed**: 链头不唯一 / 链断 / 链头无单号 ⇒ 仍红 ★

★**反向用例 (★至少 4 条, 每条都要贴原样 rc★)**:
| # | 构造 | 期望 |
|---|---|---|
| ① | ★**盘上网表那一行的 net 被改了, 但落表台账里查不到授权记录** ★ | **红** (★身份变了 + 无授权 ⇒ 仍红★) |
| ② | ★**落表台账里有授权记录 (单号 + 文件名 + 旧身份 + 新身份齐全) ⇒ 放行并同步 registry** ★ | **绿** |
| ③ | ★**授权记录里的单号在台账里查不到 / 四项不齐** ★ | **红** |
| ④ | ★**registry 被手改 (sha256 对不上)** ★ | **红** (★既有行为, 不许因本单破例★) |

★**交完 B1 后, 立刻真落 A3**:
```bash
python3 state/land_v_values.py --decision V-2=1 --apply --boss-decision "2026-11-17 A3 = 1"
```
⇒ ★**期望 rc=0** ⇒ ★**落完必须复跑: `HW/check_land_row_anchors.py` rc=0 (PASS=310 · DRIFT=0 · RED=0) · `HW/check_netlist_selfconsistency.py` rc=0 · `state/merge.py` + `state/gate_check.py` rc=0 · 受保护 5 件 md5 逐字节不变 (★板 `611b869e…` / `.kicad_pro 3e504d2b…` 尤其不许变★)** ★

### ★B2 · ★★W-4 (P4 / G-1) `Q_PG` 写法 A 落表 ★★

★**老板已拍**: ★**写法 A = S=BAT_SW / D=ON / G=PG** (★依据 ISS-244 实跑: 写法 A ⇒ PG 低时 VGS = −4.2V 导通 / PG 高时 −0.9V 关断 ⇒ 自洽; 写法 B ⇒ PG 高低都关 ⇒ 开机路径彻底不通★) ★

★**★但落的东西比「改 note」多一层 —— 这是 main 10:0x 读盘查出来的★★**:
| 项 | 盘上现状 | 写法 A 要求 |
|---|---|---|
| 落地件 | `DMP3098L` (SOT-23) ⇒ ★**引脚序 1=G / 2=S / 3=D**★ (`HW/check_part_selection_landed_crosscheck.py` L70) | — |
| pad1 | ★**PWR_ON (负载侧)**★ ⇒ 物理上是 **G 位** ⇒ ★**栅极接负载**★ | ★**pad1 = PWR_GOOD (G)**★ |
| pad2 | BAT_SW ⇒ 物理上是 **S 位** ✓ | BAT_SW (S) ✓ |
| pad3 | ★**PWR_GOOD (PG)**★ ⇒ 物理上是 **D 位** ⇒ ★**漏极接 PG**★ | ★**pad3 = PWR_ON (D)**★ |

⇒ ★**★所以 B2 = pad1 ↔ pad3 的网互换 (PWR_ON ↔ PWR_GOOD) + 三行 note 改写成写法 A + 脚表/网表/BOM/原理图同步 + 落表台账 + 锚点重锚★★**
⇒ ★**★连带 (★必须写进板那一趟的 S 步清单, 不许漏★): 板上的 Q_PG land 是按旧接法画的 ⇒ 「板只改一次」那一趟必须重画 Q_PG 的 3 根线 (★或改选 D-S-G 序器件 —— 那也是换封装, 同样是板那一趟★)★★**
⇒ ★**注意**: pad1↔pad3 互换 = ★**换 net ⇒ 又是【实体身份变了】⇒ B1 没做完之前 B2 也落不下去** ⇒ ★**⇒ B1 是 B2 的前置** ★

### ★B3 · ★★G-5 (P6 / W-6) LED 亮度档落表 ★★

★**老板已拍**: ★**选项 ② = 改 R 到 20 mA 档** ★ ⇒ ★**`R_LED_R` = 68Ω ±1% (红) · `R_LED_G` = 55Ω ±1% (绿)** ★
⇒ ★**★口径订正 (★main 主动纠正自己上一条消息, 你照 68/55Ω 做★)**: 我 09:4x 给老板写的「建议改 ≈150Ω」是 §A-补4 W-6 行的旧数 ⇒ ★**按 ISS-244 [官网] 级实测折算, 20mA 档的真值 = 红 68Ω / 绿 55Ω (150Ω 只有 ~5mA, 达不到老板批准的「20mA 档」)**★

★**连带 (★如实登记, 不许瞒★)**:
- ★**每颗功耗 2.2mW → 66mW (两颗 ≈ 0.13W 进电池账)** ★
- ★**亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级要重算 ⇒ 登记成 need 给 main (★你只登记, 不代拍★)** ★
- ★**这两个电阻的值会写进 BOM ⇒ 板那一趟要重出 BOM + 投产包 (★但 footprint 不变 ⇒ 不构成额外板改★)** ★

---

## ③ 必须一起更新的三处 (★漏一处 = 板那一趟白跑★)

★**落表完 + 落表台账写好之后, 把下面两条补进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★板侧项全集页★) ⇒ 并重跑覆盖度闸** ★:

| # | 补什么 | 为什么 |
|---|---|---|
| ① | ★**V-2 的网改名**: `D_ESD_USB_D` pad1 网名 `USB_D_P_SRC` → `NET_USB_D_P_TYPEC` ⇒ ★**板上的 footprint 焊盘网名必须同趟改**★ | ★落表器自己的警告: 「漏改 ⇒ 网表与板对不上」★ |
| ② | ★**Q_PG land 重画** (pad1↔pad3 互换) ⇒ 板那一趟的 S 步清单里要有它 | ★B2 的直接后果★ |
| ③ | ★**D− 侧 ESD 三件仍挂着** (R4×2 + R9): ① `D_ESD_USB_D` 只有 2 焊盘 ② D− 网 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 上无任何 ESD 位号 ③ `D_ESD_USB_D`→`J_USB_C` 板面距离 **47.99mm** > 3.0mm 判据 ⇒ ★**这三条现在是 G1a-4 的最后 4 条未落表项 (★板侧) ⇒ 板那一趟清掉它们, G1a-4 才转绿**★ | ★G1a-4 现在红的就是这 4 条★ |

⇒ ★**验收**: `python3 HW/check_onepass_preflight_coverage.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 (反向一条不许少)** ★

---

## ④ 必跑的命令 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/land_v_values.py --selftest                      # 落表器自测 (期望 rc=0)
python3 HW/check_land_row_anchors.py                            # 行号锚点守卫 (期望 rc=0 · PASS=310)
python3 HW/check_land_row_anchors.py --selftest                 # 期望 rc=0
python3 HW/check_netlist_selfconsistency.py                     # 期望 rc=0 (现状守卫)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # 期望 rc=1 (★还剩板侧那几条★)
python3 HW/check_onepass_preflight_coverage.py                  # 期望 rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest       # 期望 rc=0
python3 state/merge.py && python3 state/gate_check.py           # 期望 rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv \
       HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 + .kicad_pro 必须逐字节不变 (611b869e… / 3e504d2b…)★★
```

## ⑤ 交卷物 (★5 件★)

1. ★**交卷单 `HANDOFF/2026-11-17_hw-lead_ISS282_V2解锁与W4G5落表.md`** (★B1~B6 六块齐全 + 三件落表各一段原样 rc★) ★
2. ★**B1 的守卫改动** (★`HW/check_land_row_anchors.py` + 它的 `REGISTRY_SHA256` 同步 + 反向用例 4 条★) ★
3. ★**三件落表的台账痕迹** (★`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 新段 + 老板凭据 + 新旧 md5★) ★
4. ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 追加 §③ 三条 + 覆盖度闸复跑记录** ★
5. ★**分片** `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead` 原子写★) ★

## ⑥ 边界 (★违反就是不合格★)

★零写板 (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 一个字节不许动★) · ★零改既有判据阈值 · ★**不许弱化行号锚点守卫的 fail-closed 三条** ★ · ★不碰 `MECH/` / `SW/` 的分片与文件 (★只交叉引用★) · ★零外发 · ★**不替老板拍板 (★ESD 型号轴 + D− 侧仍待拍, 你不许顺手选型★)** ★ · ★**不自签 issue_log** ★ · ★不许把整份大文件读进来 (★只 grep 你要改的那几行★)★

## ⑦ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss282/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验自己的 key 在不在 (★`frag_write.py` 无锁 ⇒ 并发写会 lost-update★)** ★

---

## ★⑩ 追加 (★main 2026-11-17 11:0x 本机实跑补记 · ★**追加式, 上面每一条老字一字未删**★) ★

★**背景**: ★**A1 (V-3=E) + A2 (V-4=680) 已于 2026-11-17 09:58:16 授权落表 (rc=0)** ⇒ ★**网表 / 脚表 / BOM 三件 md5 当场变了** ⇒ ★**⇒ 本单的三件落表 (A3 / B2 / B3) 一落, 这三件 md5 还会【再变一次】★** ⇒ ★**⇒ 下面这 4 条是【落表之后】的收口动作, 本单一起做掉, 不许留到板那一趟★**

### ★⑩.1 · `state/land_v_values.py --selftest` ⇒ **rc=1 (是崩, 不是红)** ★

★**main 原样实跑 (★10:5x★)**:
```
$ python3 state/land_v_values.py --selftest
  File ".../state/land_v_values.py", line 1896, in run_selftest
    plan12.apply_patches()
  File ".../state/land_v_values.py", line 1170, in replace_after
    raise RuntimeError(f"★旧值出现 {n} 次 (期望 {count} 次)")
RuntimeError: ★旧值出现 0 次 (期望 1 次)
```
★**根因**: ★**用例 12 硬套 V-3 / V-4 的补丁, 而这两个值【已经落过表了】⇒ 真盘里旧值出现 0 次 ⇒ 崩★**
★**收口**: ★**「已落过」检测要覆盖 V-3 / V-4** (★V-2 早有这两个没有★) ⇒ ★**用例 12 改成对【已落过】判红 ⇒ `--selftest` 回 rc=0★** ⇒ ★**★不许把用例 12 删掉 / 跳过 ⇒ 那是把判据拿掉, 不是修判据★**

### ★⑩.2 · `HW/check_onepass_preflight_coverage.py` ⇒ **rc=1 (P5 + P6 两条红)** ★

★**main 原样实跑 (★10:5x★)**:
```
  FAIL  P5
     ❌ B17_DNP_43: 盘面实测 = '零标记 40 颗', 但清单 current_state 里没有这个值 ⇒ 清单过期
     ❌ B03_ULDO_S28_PAD3: 盘面实测 = '18 条缺陷', 但清单 current_state 里没有这个值 ⇒ 清单过期
  FAIL  P6
     ❌ 网表 md5 2f17650cfbef48d5efd71821505c3343 ≠ 基线 e06c1dd633566aa44732762c2ff99d1c
     ❌ 脚表 md5 6ea65fecdf95902e47330083d140d455 ≠ 基线 287e7861a0d1007748d92d9fbecdd490
     ❌ BOM md5 ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd ≠ 基线 94642d07a69e8d60dd2af57f69b93607
```
★**收口**: ★**① P5 两个现状探针的期望值跟着盘面改** (★B17_DNP_43 = `零标记 40 颗` · B03_ULDO_S28_PAD3 = `18 条缺陷`★) ★**② P6 三个基线走 H-1 四项重锚** (★出处 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 的落表前后对照★) ⇒ ★**★板 `611b869e…` 与 `.kicad_pro 3e504d2b…` 两个基线本来就没变 ⇒ 一个字节都不许动★★** ★**③ 清单 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 追加 §③ 三条后, 覆盖度闸复跑 rc=0** ★

### ★⑩.3 · 一条不许踩的红线 (★本单自带的时序坑★) ★

★**本单的验收 rc 必须【在三件落表【之后】】再跑一遍** ⇒ ★**不许拿【落表之前】跑的 rc 当交卷证据** (★因为 md5 会变 ⇒ 拿旧 rc 交卷 = 交假证据★) ★

### ★⑩.4 · SW 侧那条红【不是你的活】 ★

★**`SW/tools/timing_check.py` ⇒ rc=1 (68/71 · 3 条红: 网表锚点 ×2 + F4' 期望 ×1) ⇒ 归新开的 ISS-285 (sw-lead)★** ⇒ ★**★不许你去改 `SW/` 的文件与分片★** ⇒ ★**你只交叉引用 (★它的任务书 = `state/dispatch_briefs/ISS-285_sw_landing_after_judgment_alignment.md`★)**
