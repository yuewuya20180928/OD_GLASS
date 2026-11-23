# ISS-355 · sw-lead · ★转换脚本迁主路线 (rknn3-toolkit 1.2.0 + target_platform='rk3572')·纯脚本·零写板★

★**题**: ISS-353 (★已由 main 2026-11-23 05:3x 签收·机器判决★) 把【口径】清干净了 (★全仓 16 条旧结论: 15 条文档类已由 main 一键补丁清掉 · 剩 2 条在 hw.yaml, 归 hw-lead★) ⇒ ★**但【实现】还没改**: 任何人按现在的脚本重跑, 拿到的仍是 `target_platform='rk3576'` 的产物 ⇒ ★**口径清了 ≠ 实现改了** ⇒ ★**这就是 ISS-353 §B7 残留表里那条 `iss353_need_followup_convert_script_rk3572` (登记为 to=main, 等 main 确认优先级) ⇒ 本单就是它★**

★**当前真值 (★别再自己查一遍, 直接用★)**:
- ★**toolkit2 (2.3.2 / 2.5.0) 不支持 `rk3572` target** ⇒ [官网]+[实测] ⇒ 转换链要用 **rknn3-toolkit 1.2.0** (ISS-263 实测: `config(target_platform='rk3572')` rc=0 · 转换 rc=0 · 跨 3 会话 9/9 产物逐字节相同 · 249360 B)
- ★**rknn3-toolkit 1.2.0 支持 `rk3572`** ⇒ [实测] ⇒ ★**转换链这一环已通 (不是「应该行」)★**
- ★**板端接受性仍 [0数据]** ⇒ 降级 A/B/C 已在 ISS-353 交卷页 §B3 写死 (板到手 ⇒ `SW/tools/rk3572_rknn3_board_smoke.sh` 一条命令出 PASS/FAIL)

---

## ★★本单只做 3 件 (★不许扩项★) ★★

### (1) ★**`SW/tools/rk3572_model_rebuild.sh` 迁主路线 (★默认路线必须改, 不许只加注释★)★**

- ★**读现在的实现 (★自己实读, 别抄交卷页★)**: L13 / L86 / L136 三处写死 toolkit2 + `target_platform='rk3576'` ⇒ 说清每一处当前干什么用 (★三处的角色可能不同: 一处是装环境、一处是转模型、一处是拷产物★)
- ★**处置**: ★**默认路线改成 rknn3-toolkit 1.2.0 + `target_platform='rk3572'`** (★可用环境变量切回旧链, 但**默认值必须是新链**★) ⇒ ★**旧链保留为「次要路线①」并标明它的代价 (板端 runtime 是否认 rk3576-target 产物 = [0数据])★**
- ★**★关键坑 (★ISS-353 已点出·必须处理★)**: ★**rknn3-toolkit 1.2.0 的产物是 `.rknn` + `.weight` 两件套** ⇒ ★**只拷 `.rknn` 一定失败** ⇒ 脚本的拷贝段必须两件套一起拷 (★或明写「只拷 .rknn 会失败, 两件套必须同时到位」★)

### (2) ★**`SW/RKNN_BENCH.md` §5 追加式订正 (★只许追加/改写被点名的那几行·老字别删★)★**

- 写清 §5 现在的 target 口径 (★实读★) + 新主路线 + 旧链的定位与代价 + 产物两件套的注意事项
- ★**不许删老行** (★老口径保留作历史留档 + 取代标记★)

### (3) ★**新建机器闸 (★只读·文件名路径你自己定·放 `SW/tools/` 下★) + `--selftest` 反向用例★**

★**它要断言的 (★每条都要能当场判红★)**:
1. ★**扫全仓: 凡仍把「用 `rk3576` 转」当【当下执行口径】的 ⇒ 逐条点名 (文件 + 行号 + 原文片段) ⇒ 输出必须带名单, 只报数量 ⇒ rc=1** ★ (★注意区分【历史叙述(可留)】与【当下执行口径(要处置)】· ★ISS-353 的闸 `SW/tools/check_rk3572_target_caliber.py` 已有一套 F1~F8 规则可复用·**别重造一套冲突的**★★)
2. ★**断言 `SW/tools/rk3572_model_rebuild.sh` 的默认路线 = rknn3-toolkit 1.2.0 + `rk3572`** (★不许靠注释糊弄 ⇒ 机器读脚本里的默认值★)
3. ★**断言 `.rknn` + `.weight` 两件套的拷贝逻辑在位** (★不许只拷 `.rknn`★)
4. ★**反向用例 (必须有·不许只跑正向★)**: 在 `tmp/` 副本上把默认 target 改回 `rk3576` ⇒ 闸必须**判红并点名该脚本** ⇒ 恢复 ⇒ 判绿
5. ★**`--selftest` 末行 `ALL TESTS PASS`** ★

---

## ★★边界 (★一条都不许越★) ★★

- ★**零写板**: `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 必须是 `611b869e13518c3c023fb178f91a0075` / mtime 必须是 `2026-11-06 07:07:17.362193413` ⇒ ★**开工前 + 交卷后各打一次, 双证贴 §B6** ★
- ★**零落表**: 不改网表 / 脚表 / BOM / 原理图 / 任何闸的判据方向 / `state/fragments/pm.yaml` / `state/fragments/hw.yaml` / `state/fragments/mech.yaml` / `state/issue_log.yaml` (★自签 issue_log 是 main 的地界★)
- ★**只写**: `SW/tools/rk3572_model_rebuild.sh` + `SW/RKNN_BENCH.md` 的追加段 + 新建的闸脚本 + `SW/tools/` 下新增文件 + `HANDOFF/2026-11-23_sw-lead_ISS355_*.md` + `logs/iss355/` + `state/fragments/sw.yaml` (★只走 `state/frag_write.py`★)
- ★**零外发 / 零采购 / 零联系供应商** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★) ⇒ ★**`state/outbox/` 里的草稿一律不发, 只作资料留档** ★
- ★**不许提「买一块 RK3572 板/开发板」** (★老板 2026-11-04 19:10 指示★)
- ★**不替老板拍板** · ★**不新增拍板项** (★ISS-155 的台账标签 = 交 main 裁, 不是你的项★)
- ★**证据分级必标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ ★**不许把 [推算] 写成 [实测]** ★
- ★**不许改既有闸的判据方向** · ★**不许动 `state/gate_check.py`** · ★**不许动 `state/merge.py`** ★

---

## ★★必跑项 (★交卷前跑, 把原样输出贴进交卷页 §B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 state/merge.py            # rc 必须 0
python3 state/gate_check.py        # rc 必须 0 · Q1 必须 18/18
python3 state/frag_write.py --agent sw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```
★**本单自带的闸**: `python3 <你定的那支闸>.py --selftest` ⇒ 末行 `ALL TESTS PASS` ★

★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS355_转换脚本迁主路线.md` (★B0~B7 七块齐全 + 页内引用路径逐个在盘 (MISS = 0) + 板指纹前后双证 + §B6 原样输出★)

★**参考**: `HANDOFF/2026-11-23_sw-lead_ISS353_rk3572目标口径清账.md` (★口径真值 + 板端降级 A/B/C★) · `SW/RK3572_TARGET_COMPAT_V2.md` §8 (★v2.1 追加段★) · `SW/tools/check_rk3572_target_caliber.py` (★F1~F8 规则可复用★) · `SW/tools/iss263_rknn3_convert.py` + `SW/tools/iss263_rknn3_install.sh` (★rknn3-toolkit 1.2.0 的现成安装/转换脚本·★别重写★)
