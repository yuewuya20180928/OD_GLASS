# ISS-315 · sw-lead 任务书 —— ★★【判据链收口: 把「链头落表单号交叉核对 (修法 B)」铺到硬保护路径 (★前置 = 先修 ISS-298 闸的沙盒夹具★) + 立「落表留痕义务」新闸 (★可挂不挂·挂闸由 main★)】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-315
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 判据修复类 + 闸新建类 (SW 侧)** ★
> ★**边界 (硬)**: ★**零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · 零改三个回归基线 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★1 · 病灶 (★ISS-312 已 verified · main 07:1x 本机复跑 `python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` ⇒ **rc=0 · 4/4**★) ★

★**ISS-312 把「链头落表单号」的洞堵在了【一条路径】上, 另一条路径还开着** ★

| 路径 | 修法 A (单号不唯一 ⇒ 判红) | 修法 B (单号 ↔ 独立信源交叉核对) | 现状 |
|---|---|---|---|
| ★**`check_r6_three_way()`** (★三向一致性那条★) | ★**有** ★ | ★**有** ★ | ★**已堵** ★ |
| ★**`check_r6_hard_protected()`** (★硬保护那条★) | ★**有** ★ | ★**★没有** ★ | ★**★还开着** ★ |

★**ISS-312 交卷单里写明的实测 (逐字)**: ★**「硬保护那条路径只加了 A, 没加 B —— 实测加了 B 会让链里那道 `check_onepass_sw_sync.py --selftest` 的第 ⑮ 条 (★合法改板正向放行★) 假红 15/16」★** ★
★**它为什么收回 B**: ★**按 ISS-309 的铁律「假伤修夹具、不许改判据」, 而那个夹具文件【不在本单可写范围】⇒ ⇒ 把 B 收回, 列为 need N-1 交 main 拍** ★

★**⇒ 本单 = 把 N-1 接住: ★**先修夹具, 再把 B 铺到硬保护路径**★ ⇒ ★**这正是「板只改一次」那一趟要用的判据 (板 md5 合法变更时, 这条路径不许漏放假单号)** ★

★**ISS-312 留的另外三条 need (本单一并接住)** ★
- ★**N-2**: ★**板那一趟必须留痕** —— 任何落表单要在 `state/issue_log.yaml` 里留【文件名 + 新 md5】★ ⇒ ★**这条义务【现在已生效】⇒ 主线重出网表 / 脚表 / BOM 那一趟的单号不留痕 ⇒ 开工前 SW 闸会红** ★ ⇒ ★**本单要把它做成一条【机器可判】的闸, 而不是一句口号** ★
- ★**N-3**: ★**挂闸裁决** —— 建议把新闸 + ISS-309 那条一起挂 `EXTRA_GATES` (★写法在 ISS-312 交卷单 B3.3★) ⇒ ★**本单只把写法写好交 main, ★**不许碰 `state/gate_check.py`** ★
- ★**N-4**: ★**「锚点副本跟到链头」可降级** (★B 已经把洞堵上了★) ⇒ ★**本单只要在交卷单里点一句「N-4 仍开着, 不影响本单结论」** ★

★**当前盘面基线 (★main 07:1x 本机实跑, ISS-312 交卷时同样数字★)★**: ★**`check_demo_panel_spec.py` 主模式 rc=0 · `--selftest` rc=0 (22/22) · `check_demo_panel_spec_r6_selftest.py` rc=0 (7/7) · `check_demo_panel_spec_r6_chainjudge_selftest.py` rc=0 (4/4) · `check_onepass_sw_sync.py --selftest` rc=0 (16/16) · timing 85/85 · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18 · Q7 9/9)** ★

---

## ★2 · 本单要做什么 (★3 件) ★

### ★① 先修 ISS-298 闸的沙盒夹具 (★假伤修夹具, ★**判据本体一个字不动**★) ★

★**病灶**: ★**`SW/tools/check_onepass_sw_sync.py --selftest` 的第 ⑮ 条 (★「合法改板正向放行」★) 在加了 B 之后假红 ⇒ ★**红在【夹具缺输入】, 不在【判据方向】** ★**
★**要做的**: ★**给那条夹具补上【独立信源】的输入 (★独立信源 = `state/issue_log.yaml` 里的真单号 + 该单的留痕行★) ⇒ 补完复跑 ⇒ 第 ⑮ 条必须回绿, 且 ★**其余 15 条的红绿分布一个字不许变** ★**
★**纪律**: ★**假伤修夹具, 不许改判据; 若补夹具补不回来 ⇒ 老老实实把「补不回来 + 为什么」写成交卷页的 need 交 main, 不许自己把红抹平** ★

### ★② 把修法 B 铺到硬保护路径 (★`check_r6_hard_protected()`★) ★

★**必须做到**: ★**硬保护路径上的链头单号也走【与独立信源交叉核对】⇒ 单号是假的 / 挂错单的 ⇒ 判红** ★
★**并交 ≥3 条新的反向用例 (★放在本单新建的 selftest 里, ★**不许动 ISS-312 刚立的那个 4/4 回归基线**★)**: ★**① 硬保护路径上链头单号改成【不存在的单号】⇒ 必须红 ② 换成【真实存在但对不上】的单号 ⇒ 必须红 ③ 原样不动 ⇒ 必须绿 (★不许把闸修成永远红★)** ★
★**★每条红用例都要带「不是巧合」自证**: ★**同一棵被改坏的树, 修前的判据判【绿】⇒ ⇒ 这条红只可能来自新加的 B ⇒ 并把这条自证写进交卷单** ★
★**★不许放宽 fail-closed 三条, 不许改判据方向, 不许为了让 `check_onepass_sw_sync.py --selftest` 变绿而放宽那条** ★

### ★③ 立「落表留痕义务」新闸 (★N-2 · ★可挂不挂★) ★

★**要判的东西**: ★**凡是 `state/issue_log.yaml` 里被当作【落表单】的条目 ⇒ 它必须留有【文件名 + 新 md5】的痕迹 ⇒ 缺痕迹 ⇒ 判红** ★
★**要交的**: ★**① 新闸脚本 (★放在 `SW/tools/` 下, ★**文件名你定★) ② 它自己的 `--selftest` (★≥4 条反向用例: ★缺文件名 ⇒ 红 / 缺新 md5 ⇒ 红 / md5 写的是改前的值 ⇒ 红 / 原样不动 ⇒ 绿★) ③ 挂进 `EXTRA_GATES` 的写法逐字给出 (★交 main, 本单不挂★)** ★
★**★关键纪律 (★本单最容易犯的一条★)**: ★**新闸在【当前盘面】必须 rc=0** ⇒ ★**若一建出来就红 ⇒ 那说明这条义务与现状不符 ⇒ 老老实实写 need 交 main 拍口径, ★**不许自己把判据放宽去凑绿** ★** ★
★**★另一条纪律**: ★**不许拿 issue_log 自己的副本互证 (★那还是自证★) ⇒ 真单号必须能在 `state/issue_log.yaml` 的【真条目】里查到, 就像 ISS-312 修法 B 那样★** ★

---

## ★3 · 交卷物 (4 件) ★

1. ★**新建** ★`HANDOFF/2026-11-18_sw-lead_ISS315_判据链收口.md` (★B1~B6 齐全 · 占位符 0 · ★**必含: ① 修夹具前后第 ⑮ 条的逐条读数 ② B 铺到硬保护路径后的新反向用例逐条判定 + 「不是巧合」自证 ③ 新闸的挂链写法 (★交 main★) ④ 新闸在当前盘面的 rc ⑤ 给 main 的 need (★含 N-2 的口径问题, 若新闸建出来就红★)** ★)
2. ★**新建** ★`SW/tools/` 下本单的新 selftest 脚本 (★★**文件名你定★ · ★**必须与 ISS-312 立的 `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` 分开, 不许覆盖它**★ · 改前若动了既有文件, 留 `.bak_iss315` 备份★) ★
3. ★**新建** ★`logs/iss315/` (★修夹具前后的原始输出 · 新反向用例的逐条判定 · 被测脚本与被测台账的 md5 前后值 ★)
4. ★**新建** ★`state/fragments/sw.yaml` 的本单条目 (★★**必须用 `python3 state/frag_write.py --agent sw-lead` 原子写 (★禁止 open(p,"w")★)★** · artifacts + needs_from · ★**只写自己那一份, 不碰 pm/hw/mech★** ★)

★**★另交**: ★**给 main 的 need 一行 (★need key + 一句话问法 + 不拍的后果★)** ★

---

## ★4 · 硬边界 (★违反即不算交卷★) ★

- ★**零写板**: 板 `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 (`611b869e13518c3c023fb178f91a0075`) + mtime (`2026-11-06 07:07:17`) 交卷前后逐字节相同 ⇒ **交卷页要贴这两个值** ★
- ★**零落表 / 零改网表真源**: ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/SCHEMATIC_LANDING_V1_LANDED.md` 一律不动** ★
- ★**★不许改 `state/gate_check.py`** (★挂不挂闸链由 main 拍★) ★
- ★**★不许改这三个回归基线**: ★**`SW/tools/check_demo_panel_spec_r6_selftest.py` (★ISS-309 立的 7/7★) · `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` (★ISS-312 立的 4/4★) · `SW/tools/check_demo_panel_spec.py` 的判据方向与 fail-closed 三条 (★只许【加】不许【改】★)** ★
- ★**★不许为了让闸变绿而改台账 / 改锚点副本 / 放宽判据 (★MEMORY 铁律: 排查类 bug 要修在产生点, 不许在产物上擦★)★** ★
  ⇒ ★**若加严之后现有链变红 ⇒ 【那说明它抓到了真的不一致】⇒ 老老实实把「红了 + 红了的原因 + 该由谁修」写成交卷页的 need, 不许自己把红抹平** ★
- ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ 外部依赖一律【自己网上查】+ 标证据等级 + 查不到就写降级方案** ★
- ★**不替老板拍板 · 不自签 issue_log** (★`state/issue_log.yaml` 只由 main 改★) ★
- ★**只写**: `SW/tools/` 下本单动的文件 + 备份 · `HANDOFF/` 本单交卷单 · `logs/iss315/` · `state/fragments/sw.yaml` (★经 frag_write.py★) ★

---

## ★5 · 交卷前必跑 (★把输出原样贴进回复★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss315_tmp      # ★本机 /tmp 有每用户配额, 不指会 EDQUOT 假红★
python3 SW/tools/check_demo_panel_spec.py                      # rc 必须 0
python3 SW/tools/check_demo_panel_spec.py --selftest           # rc 必须 0 · 22/22
python3 SW/tools/check_demo_panel_spec_r6_selftest.py          # rc 必须 0 · 7/7  (★回归基线·不许动★)
python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py  # rc 必须 0 · 4/4  (★ISS-312 刚立的·不许动★)
python3 SW/tools/check_onepass_sw_sync.py --selftest           # rc 必须 0 · 16/16 (★修夹具前后都要读一次并贴出来★)
python3 <你本单新建的落表留痕新闸脚本> --selftest   # rc 必须 0 (★用你实际建的脚本名·放在 SW/tools/ 下★)
python3 state/merge.py && python3 state/gate_check.py          # ★rc 必须 0 · Q1 必须 18/18★
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/tools/check_demo_panel_spec.py SW/tools/check_demo_panel_spec_r6_selftest.py SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb                   # ★零写板第二证 (mtime 必须还是 2026-11-06 07:07)★
```

★**★额外纪律 (★与所有派活单同款★)★**: ① ★**写分片必须用 `state/frag_write.py` (禁止 open(p,"w"))** ★ ② ★**只写本任务允许的文件, 不碰别人的** ★ ③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ ④ ★**不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ★ ⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
