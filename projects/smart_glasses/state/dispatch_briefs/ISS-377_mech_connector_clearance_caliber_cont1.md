# ISS-377 · mech-lead · ★★cont1 续做: 把【座体净距判据同源化】那张表落成三件交付物 ★★ (★事实已查·★16 分钟墙内先落页再落闸★)

★**这是 cont1 续做 (★上一趟 02:51 那趟被 16 分钟墙掐死·★只落了事实文件·★三件交付物零★) ⇒ 先实读这两份 brief (★按顺序★)**:
① ★**本 cont1 brief (★先读这份★)**: `state/dispatch_briefs/ISS-377_mech_connector_clearance_caliber_cont1.md`
② ★**原任务书 (★判据/边界/交付物定义全部仍有效·必读★)**: `state/dispatch_briefs/ISS-377_mech_connector_clearance_caliber.md`

★**★★已在盘 (直接用·★别重查★)★**: `logs/iss377/board_connectors.json` (3,563 B @11-24 02:42) ⇒ ★**座体真实型号的实查结果已经在那里面了 ⇒ 直接用它落表, 别再上网/再翻手册** ★

★**★你要交的三件 (★顺序很重要·★先落页再落闸·★16 分钟墙★)★★
1. ★**新建★ 一页 `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` ⇒ ★**本单正题: 把「座体净距判据」统一成【一张表】** (★`J_DEBUG` 铜箔支配 vs `J_UART` 座体支配 ⇒ 两条口径同源化·★不许各算各的★) + ★**座体真实型号** (★从 `board_connectors.json` 取·★标证据等级★) ★
2. ★**新建★ 一条闸 `MECH/check_connector_clearance_caliber.py` ⇒ 判据 **K0~K8** (★每条 fail-closed·每条带反向用例·★`--selftest` 末行 ALL TESTS PASS★) ⇒ ★**★闸不许挂 `state/gate_check.py`** (★挂链是 main 的地界·★你只交脚本与路径 + 建议★) ★
3. ★**新建★ 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS377_座体净距判据同源化与座体型号自查.md` ⇒ ★**B1~B6 六段齐全, 且【六个 `##` 标题必须含 gate_check 要的关键词】(★上一批单踩过这个坑·★一次写对★)★ ★
   - `## B1 结论摘要` · `## B2 验收标准自评` · `## B3 证据分级` · `## B4 接口取值声明` · `## B5 未决项与卡点` · `## B6 自证复现命令` ⇒ ★**gate_check 的判据是「全文标题里出现该关键词即可」** ★
   ★**★§B5 必须写明: 「上一趟 02:51 被 16 分钟墙掐死 + 本趟从已落 board_connectors.json 续做」★** ★
4. ★**分片登记** `state/fragments/mech.yaml` ⇒ ★**只走 `python3 state/frag_write.py --agent mech-lead` (★禁止 `open(p,"w")`★)·写前写后各记一次 md5·★期间若被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」·不许静默覆盖★** ★

★**边界 (★一条不许越·★与原任务书相同★)**: ★**零写板** (板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213) · 零落表 · 零改既有闸 / 零改既有页面正文 (★`MECH/BOARD_ONEPASS_*` 其它页一个字都不许动★) · 零外发 (★全靠自己查·查不到写降级方案·不许写「等原厂回信」★) · 不代老板拍板 · 不自签 `state/issue_log.yaml` · 沙盒只落 `tmp/iss377/` + `logs/iss377/` ★
★**★时间提醒 (★16 分钟墙·★上一趟就是被它掐死的★)**: ★**先落①页 (占大头) ⇒ 再落②闸 ⇒ 再落③交卷页 ⇒ 最后写分片 + 贴 rc ⇒ 四步做完就收工·★别加戏·★别重查型号★** ★
★**收工后回卷**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (★逐条写清「要谁回答什么」★) ★
