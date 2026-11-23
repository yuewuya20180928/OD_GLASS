# ISS-371 · mech-lead · ★「板那一趟」`J_DEBUG` 排针 land 改 1.27mm 后的结构侧净距真相 · ★★cont1 续做 (★上一趟 21:31 failed·那页已落·闸/交卷页/分片零★)★★

★**这是 cont1 续做派活 (★不是从零重开★)** ⇒ ★**上一趟 (2026-11-23 21:2x 派) 的子会话于 21:31:03 failed (★sessions_list status=failed·transcript 末写 21:31:03·**没有更新的续跑 sessionId** ⇒ 按 main 的「三与」判据 = 真死·不是假死★)** ★

★**原任务书全文 (★判据/边界/交付物定义全部仍有效·必读★)**: `state/dispatch_briefs/ISS-371_mech_jdebug_127_land_clearance_truth.md` ★

---

## ★★一 已在盘的 (★不要重跑·直接用★) ★★

| 东西 | 路径 | 大小 | 状态 |
|---|---|---|---|
| ★**净距真相页** ★ | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` | 44,332 B (21:30:47) | ★**在盘·21 个章节·别重写·先读它**★ |

★**⇒ 你要补的只剩**: ★**① 新建机器闸 `MECH/check_jdebug_1p27_clearance.py` ② 交卷页 `HANDOFF/2026-11-23_mech-lead_ISS371_JDEBUG排针1.27净距真相.md` ③ `state/fragments/mech.yaml` 分片登记 (只走 `state/frag_write.py`)** ⇒ ★**并把已落那页里【已算出的数】核一遍对不对 (★见下面第二节 main 的独立复核★), 对不上就改页, 别将错就错** ★

## ★★二 main 已核实的订正 (★2026-11-23 22:0x 本机独立复核·照这个写★) ★★

★**① `J_DEBUG` 换官方 1.27 mm land 后的净距账 (★已落那页的主结论·main 复核成立★)**: ★**清空区 X 宽 4.0850 → 4.8100** ⇒ ★**现页四处数各偏乐观 0.3625 mm** ⇒ ★**最外侧焊盘每边超出清空区 0.3625 mm ⇒ 铜箔直接进清空区** ⇒ ★**但方向仍过 `CRIT` 0.60 (余量 3.99×)** ⇒ ★**⇒ 这一条必须并进「板只改一次」那一趟同批改, 不许只改 `J_DEBUG` 一个** ★
★**② 别把「方向仍过 CRIT」写成「合格」** ⇒ ★**净距方向过阈 ≠ 铜箔不进清空区** ⇒ ★**你交卷页要把这两句分开写 (★方向过阈是判据; 进清空区是事实·两者同时成立·不许混成一句「OK」★)** ★
★**③ KiCad 10 官方库 = 155 个 `.pretty` 库目录 / 15,468 个 `.kicad_mod` 封装文件** ⇒ ★**库名是 metric 后缀命名** (`Resistor_SMD:R_0402_1005Metric` 等·旧名按字面找不到文件) ⇒ ★**你页里凡引用 `.kicad_mod` 的, 逐个 `test -f` 验文件在盘 + 记 md5** ★
★**④ `J_DEBUG` 的板侧项已在 ISS-343 `B33_PIN_LAND_1P27` (★11-17 已拍改 land 到 1.27★)** ⇒ ★**你交的是【结构侧净距真相】, 不要重复发明板侧项编号** ★

## ★★三 边界 (★一条不许越·与原任务书相同★) ★★

★**零写板** (板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`) · ★**零落表** · ★**零改既有闸 / 零改既有页面正文** (★`MECH/BOARD_ONEPASS_*` 其它页一个字都不许动★) · ★**零外发** (★全靠自己查·查不到写降级方案·不许写「等原厂回信」★) · ★**不代老板拍板** · ★**只写自己的分片 `state/fragments/mech.yaml` (只走 `state/frag_write.py`·写前写后各记一次 md5·期间被别人改过 ⇒ 停下并在交卷页写明, 不许静默覆盖)** · ★**新建的闸不许挂 `state/gate_check.py`** · ★**沙盒只落 `tmp/iss371/` + `logs/iss371/`** · ★**不自签 `state/issue_log.yaml`** ★

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 MECH/check_jdebug_1p27_clearance.py
python3 MECH/check_jdebug_1p27_clearance.py --selftest
python3 state/merge.py          # rc=0
python3 state/gate_check.py      # rc=0 · Q1 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```
★**交卷页**: `HANDOFF/2026-11-23_mech-lead_ISS371_JDEBUG排针1.27净距真相.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「上一趟 21:31 failed + 本趟从已落那页续做」** ★
★**收工后回卷**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (★逐条写清「要谁回答什么」★)★ ★
