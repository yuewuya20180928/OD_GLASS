# ISS-358 · mech-lead · ★★分片重名 key 清理 (★`pcb_outline_confirm` 一条 key 承载 5 个不同主题 ⇒ 合并后只认第一条 ⇒ 板框真值对下游不可见★)·纯分片·零写板★

★**题**: ★**`state/fragments/mech.yaml` 里 4 组 answers 用了同一个 key 登记了不同主题的答案** ⇒ ★**而合并器 `state/merge.py` 对「同一个 `_by` 的多条同 key answers」只认第一条** ⇒ ★**⇒ 后写的 3~4 条对下游【完全不可见】** ⇒ ★**其中最要命的一条是 `pcb_outline_confirm` ×5: 5 条讲的是 5 件完全不同的事 (板尺寸/镜脚内腔/摄像头安装/散热路径/M-FIT 结果) ⇒ 而这个 key 又正好被 `hw.yaml` 的 need `pcb_outline_confirm` (to=mech-lead) 和 `mech.yaml` 的 need `pcb_outline_confirm` (to=sw-lead) 同时问到** ⇒ ★**⇒ 板框/尺寸这条【老板正面临的轴】的真相, 在合并后的 STATE.yaml 里只剩第一条 (PCB 50×12mm 厚 0.8/1.0) 露脸** ⇒ ★**⇒ 这很可能就是「板框口径到处飘」的根源之一** ★

★**main 2026-11-23 09:1x 本机实读 (不抄任何 agent 报告)★**: ★**体检器 `state/check_frag_dup_keys.py --agent mech-lead`** ⇒ ★**高危 4 组**: `answers[pcb_outline_confirm]` **×5** · `answers[ntc_placement]` **×3** · `answers[iss219_mech_c7_sink_area_confirm]` **×2** · `answers[iss251_mech_service_port_pad_y_migrate]` **×2** ⇒ ★**另: 31 组 artifacts 重名 = 低危 (同一路径登记两次·不影响取值·可顺手清)** ★

★**本单只做 3 件 (★不许扩项·零写板·零落表·零外发★)★★

### (1) ★**4 组高危 answers 拆成语义独立的 key (★一条都不许删内容★)★★
- ★**做法**: ★**每条保留原 value 全文, 只换 key 名** ⇒ key 名要能自解释 (★例: `pcb_outline_confirm` ×5 ⇒ `pcb_outline_confirm_1_board_size` / `_2_cavity` / `_3_camera_mount` / `_4_thermal_path` / `_5_mfit_result`; `ntc_placement` ×3 ⇒ 按各自主题拆; 其余两组同理) ★
- ★**★关键**: ★**改 key 之前, 先查有没有 need 在问旧 key** (★`grep` 四个分片的 `needs_from`) ⇒ ★**有 need 在问的, 必须同时在新 key 下补一条 answer (★value 逐字照抄★) + 把那条 need 的 key 改成新 key (★或留一条指向新 key 的 need·★二选一·在交卷页写清★)** ⇒ ★**⇒ 不能出现「改完 key ⇒ 那个 need 没人答」的破口** ★
- ★**★`pcb_outline_confirm` 特别提醒**: ★**这 5 条里没有一条是「板框 U-1 的答案」** ⇒ ★**不许把它当板框答案用** (★板框 U-1 的真答案在 `DECISION_ONE_PAGER_2026-11-22.md` §⑥/§⑦ + `DECISION_INDEX_2026-11-18.md` §R·★与本单无关★) ★

### (2) ★**低危 31 组 artifacts 重名去重 (★只保留信息最全的一条·★其余写进交卷页的「已删重复登记」清单★)★★
- ★**判定**: 同一 `path` 多条 ⇒ ★**留 value/summary 最全的那条, 其余登记到交卷页 (★不许静默丢·★要能追回★)** ★

### (3) ★**自证 + 交卷 (★零写板★)★★
- ★**自检命令 (★交卷前跑, 原样输出贴进交卷页★)**: ★`python3 state/check_frag_dup_keys.py --agent mech-lead` ⇒ ★**rc=0 (高危 0 组)**, ★`python3 state/check_frag_dup_keys.py` ⇒ ★**全仓高危总数 = hw-lead 那几组 (★不在你地界·不许越界改★)** ★
- ★**必跑**: `python3 state/merge.py` (rc=0) · `python3 state/gate_check.py` (rc=0 · Q1 18/18) · `python3 state/frag_write.py --agent mech-lead --show` · `md5sum HW/PCB/demo_mainboard.kicad_pcb` (必须 `611b869e13518c3c023fb178f91a0075`)
- ★**交卷页**: `HANDOFF/2026-11-23_mech-lead_ISS358_分片重名key清理.md` (★B1~B6 六个 `##` 标题里必须分别出现: B1 `结论` · B2 `验收标准自评` · B3 `证据分级` · B4 `接口取值声明` · B5 `未决项与卡点` · B6 `自证复现命令`) + `state/fragments/mech.yaml` 分片 (★只走 `state/frag_write.py`★) + `logs/iss358/`

★**边界 (★一条不许越★)★★: ★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413`) · ★**零落表** (不改网表/脚表/BOM/原理图/任何闸) · ★**只写 `state/fragments/mech.yaml`** (★只走 `state/frag_write.py`·★**不许写 pm.yaml / hw.yaml / sw.yaml — 那是别人的地界★**) · ★**零外发/零采购** · ★**不替老板拍板 · 不新增拍板项** (★`pcb_outline_confirm` 那 5 条不是板框答案★) · ★**证据分级必标** · ★**不许改 `state/merge.py` / `state/gate_check.py` / `state/frag_write.py`** (★★**并发写的根治是「给 frag_write.py 加乐观并发断言」, 但那是 main 的地界·本单只清已攒下的重名, 不许自己改工具★**) · ★**不许改 `state/check_frag_dup_keys.py`** (★main 的工具·只读用★) ★
★**做不完不许假装做完**: 交卷页写清「已做 / 未做」分界 (逐组名单) ★
