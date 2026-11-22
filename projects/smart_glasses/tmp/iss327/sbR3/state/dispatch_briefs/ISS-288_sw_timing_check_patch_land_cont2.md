# ISS-288 · sw-lead 任务书 —— ★★【cont2 · 只干一件事: 把交卷单 §1~§8 的「待写」填完】★★ (★零写板 · 零落表 · 零改判据脚本★)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 15:0x** ★ · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-288 (cont2) · ★**零外发** ★
> ★**本单性质**: ★**内部活 · SW 侧 · 纯补交卷类** ★ ⇒ ★**零写板 · 零落表 · 零改 `SW/tools/timing_check.py`** ★
> ★**前置**: ★**cont1 两条会话 (`agent:sw-lead:subagent:2c3ec2ed` 14:32~14:37 done·aborted / `agent:sw-lead:subagent:b3f37a1f` 14:32~14:41 timeout) 都中途死掉** ⇒ ★**分片那条已经落盘了, 交卷单那条没落** ⇒ ★**本单只补交卷单这一件** ★

---

## ① 定位 (★main 15:0x 本机实跑, 不抄任何交卷报告★)

★**上一趟 cont1 已经把「活」干完了, 只差把结果写进账本**:

| 项 | main 15:0x 实测 | 判定 |
|---|---|---|
| ★**补丁本体** ★ | ★**`SW/tools/timing_check.py` md5 = `68c4becffe6bcd708e388dba9d18a505`** ★ | ★**= ISS-285 交卷单里写死的「套用后期望 md5」逐字一致** ★ ⇒ ★**补丁已落盘** ★ |
| ★**补丁效果** ★ | ★**`python3 SW/tools/timing_check.py` ⇒ 末行 `SELFTEST 72/72 通过, rc=0`** ★ (★开工前是 rc=1 · 68/71 三条红★) | ★**三条红已全部转绿** ★ |
| ★**交卷单** ★ | ★**`HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` = 1787 B · 68 行 · §1~§8 全是「★(填: 待写)★」(★`grep -c 待写` = 8 条命中★)** ★ | ★**没写** ★ ⇒ ★**本单就干这一件** ★ |
| ★**分片** ★ | ★**`state/fragments/sw.yaml` 里 `iss288` key = 6 处命中** ★(= claim `iss288_sw_timing_check_patch_landed` / claim `iss288_timing_check_patch_landed_chainhead_source` / claim `iss288_selftest_72_72_green_and_prefix_bugfix` / artifact `SW/patches/ISS-288_timing_check_land/verify_iss288_land.py` 等★) | ★**cont1 的第 2 件已交付** ★ ⇒ ★**你只核, 不要重复写** ★ |
| ★**验证脚本** ★ | ★**`SW/patches/ISS-288_timing_check_land/verify_iss288_land.py` = 19868 B (★14:55 mtime★)** ★ | ★**在盘, 你跑一遍贴 rc** ★ |
| ★**改前快照** ★ | ★**`logs/iss288/timing_check.py.BEFORE` (101521 B) + `logs/iss288/20_REPRO_BEFORE_timing_check.log` (★rc=1 · 68/71 3 条红★) + `logs/iss288/12_patch.diff`** ★ | ★**改前证据都在盘, 直接引用, 不许自己编「改前是什么」** ★ |
| ★**受保护 5 件** ★ | 板 `611b869e…` · `.kicad_pro` `3e504d2b…` · 网表 `37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…` ⇒ ★**零写板 · 零落表 仍成立** ★ | ✔ |

★**⇒ 结论: 机器证据齐, 账目没入 ⇒ 本单 = 「把已经跑出来的东西写成交卷单」, 不是「再干一遍」** ★

---

## ② 你要交的东西 (★**就 1 件**, 都不许动 `timing_check.py`★)

1. ★**填完交卷单** ★**`HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md`** ⇒ ★**在已有骨架上把 §1~§8 的「★(填: 待写)★」全部填满, 一处都不许留** ★ ⇒ ★**交卷前必须 `grep -c "待写" <该文件>` = 0** ★ ⇒ 每段内容必须来自**本机实跑输出** (★不许凭印象写★):
   - ★**§1 B1**: ★**网表锚点 ×2 改成「落表台账链头口径」** ⇒ ★**贴你改动的实际代码位置 (行号) + 改前/改后判据文本 + 实跑 rc** ★
   - ★**§2 B1-bugfix**: ★**md5 前缀比对口径 bug** (★12 位前缀 vs 32 位 md5★) ⇒ ★**贴改前为什么会恒红 + 改后怎么比 + 实跑 rc** ★
   - ★**§3 B2**: ★**F4' 期望随落表更新** (★BAT_DET 三颗 DNP→必装★) ⇒ ★**贴改前值 / 改后值 / 依据 (落表台账哪一条)** ★
   - ★**§4 B3**: ★**自测新增用例 (REV-11)** ⇒ ★**贴用例原文 + 它抓的是哪个回归** ★
   - ★**§5 B4**: ★**回归前后 rc 对照表** ⇒ ★**改前 `rc=1 · 68/71` + 改后 `rc=0 · 72/72`, 两行都贴** ★ ★**+ 受保护 5 件 md5 前后对照** ★
   - ★**§6 B5**: ★**边界自检** (★零写板 / 零落表 / 零外发 / 未自签 issue_log★) + **B6 留痕 / 分片 / need** ★
   - ★**§7 证据分级**: ★**每条结论标 [实测] / [源码] / [推算] / [0数据]** ★
   - ★**§8**: ★**零外发声明 + 不替老板拍板 + 不自签 issue_log** ★
2. ★**分片只做「核对 + 补漏」**: ★**先 `grep -n "iss288" state/fragments/sw.yaml` 看现有 6 处** ★ ⇒ ★**缺的才用 `python3 state/frag_write.py --agent sw-lead` 补 (★禁止 `open(p,"w")`★)** ⇒ ★**不许写 `hw.yaml` / `mech.yaml` / `pm.yaml`** ★
3. ★**一次回填验证**: ★**把交卷单里引用的每条命令都自己再跑一遍, 把原样输出贴进去** ★ (★不要贴「我上趟跑过」★)

★**★不许做的事 (★写死了★)**: ★**不许改 `SW/tools/timing_check.py` 一个字节** ★ (★它已经是对的: md5 `68c4becf…` + `72/72 rc=0`★) · ★**不许改 `SW/tools/check_demo_panel_spec.py`** (★ISS-284/275 的成果★) · ★**不许碰 `SW/SW_MD5_BASELINE_LEDGER.md`** · ★**不许写板 / 落表 / 外发 / 自签 issue_log** ★

---

## ③ 验收命令 (★本机实跑, rc 原样贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/timing_check.py                    # rc=0 · SELFTEST 72/72 (★现状已是这个值, 不许变★)
python3 SW/patches/ISS-288_timing_check_land/verify_iss288_land.py   # ★cont1 留的验证脚本, 贴原样 rc★)
python3 SW/tools/check_demo_panel_spec.py            # rc=0 (★ISS-284/275 的成果, 只许只读★)
python3 SW/tools/check_demo_panel_spec.py --selftest # rc=0 (★只许只读★)
python3 HW/check_step1_parts_spec.py                 # rc=0 (★只读★)
python3 state/merge.py                               # rc=0
python3 state/gate_check.py                          # rc=0 (★Q1 18/18★)
python3 state/issue_check.py                         # rc=0
```

★**受保护 5 件 md5 (跑前跑后逐字节相同, 原样贴进交卷单)**: ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`** ★

---

## ④ 边界 (★逐条自证, 写进交卷单 B5★)

- ★**零写板** (板 md5 + mtime 双重自证) · ★**零落表** (网表/脚表/BOM 三个 md5 不变)
- ★**零改 `SW/tools/timing_check.py`** (★它已经是对的★) · ★**零改既有 SW 判据脚本**
- ★**零外发** (★不许发邮件 / 不许联系供应商 / 不许下采购单★)
- ★**不自签 issue_log** (★verify_by = main★) · ★**只写自己的分片** ★
- ★**实物 [实测] = 0 条** (★本机无板端实测 ⇒ 不许编★)
- ★**并发提示**: ★**hw-lead 的 ISS-289 与 mech-lead 的 ISS-290 此刻在飞 ⇒ `HW/` 与 `MECH/` 那边有人写 ⇒ 你只读它们, 只写 `HANDOFF/` + 你自己的分片 (+ `SW/` 下你被允许的文件)** ★

---

## ⑤ 执行纪律 (★这项目的老教训, 上一趟就是死在这里★)

★**① 交卷单骨架已经在盘 (★本单不新建, 直接在原文件上填★) ⇒ ★**每填完一节就立刻写盘一次**, 不许攒到最后一次性写** ★
★**② 长任务一律 `nohup ... > logs/iss288/xx.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★
★**③ 单条 `exec` ≤ ~120 秒** ★
★**④ 每 10 分钟至少一次写盘** ★
★**⑤ 分片写完 `grep` 校验** ★
★**⑥ 上下文被压缩 (compaction) 不许当成「做完了」** ⇒ ★**每次压缩后第一件事: `grep -c "待写" HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md`** ⇒ ★**不为 0 就接着填** ★
