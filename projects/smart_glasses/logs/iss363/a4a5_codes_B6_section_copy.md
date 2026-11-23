## B6 · 未决项 / 建议挂法

### B6-0 · 【已完成的附带小订正 (main 2026-11-23 16:58 派单 · 只影响自己分片 · 不改 ISS-363 结论)】

★**已在本分片给 `iss306_boss_letters_count_n4` 补现码标注 (SD-1/LS-1)** ★

- ★**落点**: 只写 `state/fragments/sw.yaml` (★只走 `state/frag_write.py` 的 `update_fragment` 原子写★) ⇒ ★**未碰 pm.yaml / hw.yaml / mech.yaml**★ · 未写板 · 未落表 · 未改闸 · 未改本 claim 的结论与计数 · 未代老板拍板 ★
- ★**`md5sum state/fragments/sw.yaml` 前后值** ★:
  - ★前 = `c2e0d43ff440903dd9514a0bd6684453` (mtime `2026-11-23 15:05:42.811656838`)★ · ★后 = `1cc5b77394f4a1754dcabe116210abe6` (mtime `2026-11-23 17:00:23.981365031`)★ ★(changed=True)★
- ★**改了什么 (全为追加 · 原文字一字未删)** ★:
  1. ★`value` 末尾 +=「③/④ 的 A4 / A5 是【旧表码】· 现码 = 关机语义签收 `SD-1` · 负载开关 `TPS22991RAA` 追认 `LS-1` ⇒ 回旧码白回一次」+ 落表器 `state/land_v_values.py:2786` 的 `A_ITEM = {A1:V-3, A2:V-4, A3:V-2, A4:V-5, A5:V-6}` ⇒ 回「A4」= `Q_PG` 写法 (V-5) · 回「A5」= LED 亮度档 (V-6) ⇒ rc=2 零写盘 或落错项★ ★
  2. ★`note` 末尾 += 现码对照 (★「① A4/A5 关机语义+负载开关选型追认」= 旧表码 ⇒ 关机语义 = `SD-1` (need `boss_shutdown_semantics_and_loadswitch_20261117` 第①问) · 负载开关追认 = `LS-1` (同 need 第②问) ⇒ 老板回函先跑 `python3 state/board_decision_reply_mapper.py --reply "<原文>"` ⇒ 撞码当场拒收★) ★
  3. ★`ref` 末尾 += 出处 (★`state/board_decision_reply_mapper.py` --list 第 5/6 条 = SD-1/LS-1 · `state/land_v_values.py:2786` A_ITEM 映射★) ★
- ★**结论/计数未动 (自检 9/9 PASS)** ★: N = 4 仍成立 · 严格分层 (卡 G1a 两条红 = ①+③ · 只卡板那一趟开工 = ②+④) 一字未动 · 「与 N=4 逐条对齐」原句仍在 ⇒ ★**本订正只补码名, 不改任何判据方向, 不代老板拍板** ★
- ★**diff 面**: `diff` 前后备份 (★`tmp/iss363_sbx/sw.yaml.bak_pre_iss363_a4a5_codes`★) ⇒ ★**只落在该 claim 的 value/note/ref 三个字段 · 净增 9 行 · 零删除行** ★ (证据 `logs/iss363/a4a5_codes_apply.out`)
- ★**零写板 / 零落表自证 (前后逐字节一致)** ★: 板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` · issue_log `f9af1787db70064acfa6f7114f39b4ff` · pm/hw/mech 三分片 md5 未变 (证据 `logs/iss363/a4a5_codes_md5_pre.out` / `a4a5_codes_md5_post.out`)
- ★**未跑 `state/merge.py`** ★: 本单边界「只写 `state/fragments/sw.yaml`」⇒ ★STATE.yaml 快照留给 main 签收 ISS-363 时统一刷新 (避免与其他 lane 并发写快照)★ ⇒ ★**main 签收时跑一次 `python3 state/merge.py` 即可看到本条现码标注** ★
- ★**分片重名自检**: `python3 state/check_frag_dup_keys.py` ⇒ sw-lead 高危 **0** 组 (低危 30 组为既有 artifacts 重名, 与本次改动无关) ★

### B6-1 · 未决项 (★本单未动 · 待 main 拍★)

1. ★**同一分片里还有 3 处旧码未带现码** ★: `interface_claims[iss306_b5_g1a8_external_verdict]` (★其 note 已有「不能回裸字母 A4/A5」+ 落表器映射警告, 但【缺现码 SD-1/LS-1】★) · `interface_claims[iss306_rerun_0535_n4_reconfirmed]` · `artifacts[HANDOFF/2026-11-18_sw-lead_ISS306_G1a两条红溯源.md]` 的 summary (★该页正文 15 处 A4/A5 · 零现码标注★) ⇒ ★**建议同轮追加式补齐, 免得同一分片里两套码并存** ⇒ ★**本单按 main 指派只改 1 条 claim, 其余一律未动 · 是否开补丁待 main 决定** ★
2. ★**「标注写在产生点」的落地面** ★: 本次标注写在分片 claim (★`state/fragments/sw.yaml` ★) ⇒ 属产生点, 不会被整块重写冲掉 ⇒ ★**`config/agents/main/MEMORY.md` 的实时块每 10 分钟被 `board_progress.py` 整块重写 ⇒ 不在那类块里放标注** ★ (★main 今天踩过的坑, 写这页备忘★)
