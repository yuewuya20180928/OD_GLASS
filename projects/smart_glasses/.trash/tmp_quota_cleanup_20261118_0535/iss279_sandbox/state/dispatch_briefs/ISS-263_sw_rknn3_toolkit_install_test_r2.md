# ISS-263 · sw-lead 任务书 (第 2 趟·收尾写卷) —— rknn3-toolkit 1.2.0 安装实测 + `config(target_platform='rk3572')` 实跑

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 03:2x · ★**job**: cron `fb67af40` (ARS45 队列自动派活 · 第 3 趟)
> ★**权威任务书 = `state/dispatch_briefs/ISS-263_sw_rknn3_toolkit_install_test.md` (★逐字读完再动手★)** ⇒ ★**本文件只加"第 2 趟的收尾范围 + 已在盘的实测结果", 不改任务书内容★**
> ★**本单 = 内部活 · 软件/工具链侧 · 不是 PCB 布线/布局类 · 不是老板级拍板★**
> ★**零外发邮件 · 零采购 · 不联系任何供应商 · 不下单 · 不替老板拍路线★**

---

## ① ★为什么有第 2 趟 (★main 本机实跑核对, 不是抄交卷报告★)

★**第 1 趟的会话被 harness 掐死了**: `agent:sw-lead:subagent:b765bfb4` (taskName `queue_iss263`) 02:33:53 → 02:56:07 (runtimeMs 1332293 ≈ 22 分钟), 终止原因 = ★**"This operation was aborted"** (★父 cron 收摊把子会话一起 abort★) ⇒ ★**技术活干完了, 但"写卷"没写完★**

★**★已经在盘上的东西 (★main 03:1x 本机实测, 一条都不用重做★)**:

| 项 | 盘上实测值 |
|---|---|
| 独立环境 | ★**`/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22) 已建成★** · `pip 26.3` · ★**`rknn3-toolkit 1.2.0` 已装 (VERSION file = rknn3-toolkit 1.2.0, dist version = 1.2.0)★** · `numpy 2.2.6` · `torch 2.4.0+cpu` · `onnx 1.23.2` · `onnxruntime 1.23.2` |
| toolkit2 旧环境 | ★**`/home/yuewuya/miniconda3/envs/rknn` 未被污染 (独立 env, 另起目录)★** |
| `config(target_platform='rk3572')` | ★**`CONFIG_OK target=rk3572 elapsed=0.019s` (rc=0)★** (★日志: `logs/iss263/config_probe.log`★) |
| ★**反向自证 (错 target 必报错)★** | ★**`config(target_platform='rk3576')` ⇒ `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ★** ⇒ ★**证明 target 参数真被读了, 不是 import 成功就算★** |
| ★**转换实跑 (3 次读数)★** | ★**`target_platform='rk3572'` ⇒ 3 次全部 rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0★** · 产出 `yolov5n_heads_int8_rk3572_run{1,2,3}.rknn` = ★**249360 B · md5 `97a34fff0b855b92681f26627dba5354` (三次逐字节一致, 可复现)★** · `t_total` = ★**33.389 / 34.108 / 41.672 s ⇒ min 33.389 / avg 36.390 / max 41.672 s★** (★日志: `logs/iss263/convert_rk3572_3runs.log`★) |
| ★**全模型 (yolov5s@640) 额外证据★** | ★**`yolov5s_full_int8_rk3572.rknn` = 339992 B · md5 `e8927025d8d0494a1a949802bbac7a1f` · t_build 73.924 s / t_total 74.314 s ★** (★日志: `logs/iss263/extra_probe.log`★) |
| 门禁 (装完照跑) | ★**G1 `check_demo_panel_spec.py` ⇒ G1_RC=0 (R1~R7 全过) · G2 `timing_check.py` ⇒ G2_RC=0 (SELFTEST 71/71) · G3 `merge.py` ⇒ G3_MERGE_RC=0** (★日志: `logs/iss263/gates.log`★) |
| 已写的脚本 | `SW/tools/iss263_rknn3_wheel_fetch.sh` · `SW/tools/iss263_rknn3_install.sh` · `SW/tools/iss263_rknn3_install_step2.sh` · `SW/tools/iss263_rknn3_convert.py` · `SW/tools/iss263_config_probe.py` · `SW/tools/iss263_extra_probe.py` · `SW/tools/iss263_gates.sh` |

★**⇒ 第 2 趟 = ★只干"把上面这些写成卷 + 补两个尾巴", 不许重下 wheel / 不许重装 / 不许重转模型★**

---

## ② ★本趟唯一没做完的三件事 (★这是你的全部工作范围★)

### ★① 补上「往返自证」(★唯一的真尾巴★)
★**`logs/iss263/extra_probe.log` 里这一步炸了 (★原文★)**:
```
>>> rc = r2.load_rknn(RKNX)
TypeError: RKNN.load_rknn() missing 1 required positional argument: 'weight_path'
```
⇒ ★**要么按正确签名重跑一次 (★`load_rknn(path, weight_path=...)` 或按 `help()`/inspect 的真签名调, ★**不许改判据糊过去**★), 要么如实写"往返自证未过 + 原文 + 原因" ★**
★**这是 ISS-155 blocker 的关键一环 (★"转出来的 .rknn 真能被读回来吗"★) ⇒ ★**优先补这一条★**

### ★② 交卷单写满 (★现在是骨架, B1~B6 全是 `(填)`★)
`HANDOFF/2026-11-17_sw-lead_ISS263_rknn3_toolkit安装实测与rk3572转换.md` ⇒ ★**B1~B6 六块齐全, 标题要含 gate_check 认的语义关键词 (★B1 含"结论" · B2 含"验收标准自评" · B3 含"证据分级" · B4 含"接口取值" · B5 含"未决/卡点" · B6 含"复现命令"★)** ⇒ ★**所有数字从 `logs/iss263/*.log` 原样贴, 零转录误差★**

★**B1 结论行必须写死这一句 (★main 定的口径, 不许含糊★)**:
> ★**转换链已通 (rknn3-toolkit 1.2.0 + target_platform='rk3572' 实跑 3 次全 rc=0, 产出 .rknn 249360 B / md5 97a34fff…, 耗时 33.389/34.108/41.672 s); ★板端接受性仍是 [0数据] (板不可达 ⇒ 主机侧跑通 ≠ RK3572 板端跑通)★**

### ★③ 剩下两个交卷物
- ★**`SW/RK3572_TARGET_COMPAT_V2.md` §5/§6.3 实测栏追加** (★只追加, 老字不许删★) ⇒ ★**写清: 装上了没有 / config 过了没有 / 转换耗时 3 次读数 / 板端仍是 [0数据]★**
- ★**分片**: `state/fragments/sw.yaml` (★**只走 `python3 state/frag_write.py --agent sw-lead` 原子写**★ · ★**现在 grep iss263 = 0, 一条都没登记★**)

---

## ③ ★时间预算 (★硬纪律★)

| 段 | 时长 | 做什么 |
|---|---|---|
| P0 | ≤2 min | 读权威任务书 + 读 `logs/iss263/*.log` (★**不许重跑重下★**) |
| P1 | ≤8 min | ★**补往返自证 (★长命令后台跑: `nohup ... &` + 轮询日志★)★** |
| P2 | ≤6 min | 交卷单 B1~B6 写满 (★原始日志贴进去★) |
| P3 | ≤3 min | `SW/RK3572_TARGET_COMPAT_V2.md` 追加 + 分片 |
| P4 | ≤3 min | 验收 rc 原样贴 + 交卷 |

★**总预算 ≤22 分钟, 到点就交卷 (★如实写"没做完的部分", 不许空交★)**

---

## ④ 验收 (★本机实跑, 原样输出★)

```
/home/yuewuya/miniconda3/envs/rknn3/bin/python -c "from rknn.api import RKNN; print('rknn3-toolkit 1.2.0 ok')"
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_config_probe.py   ⇒ rk3572 rc=0 且 rk3576 必须报错 (反向自证)
python3 SW/tools/check_demo_panel_spec.py               ⇒ rc=0 (★不许被本单弄红★)
python3 SW/tools/timing_check.py                        ⇒ rc=0 (★71/71, 不许掉★)
python3 state/merge.py && python3 state/gate_check.py   ⇒ rc=0 (★Q1 18/18★)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
  ⇒ e06c1dd633566aa44732762c2ff99d1c / 287e7861a0d1007748d92d9fbecdd490 / 94642d07a69e8d60dd2af57f69b93607
    / 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b   (★逐字节不变★)
```

★**受保护 5 件 md5 现值 = main 03:1x 实测值 (★你跑完要逐字节对上★)**

---

## ⑤ 边界 (★违反即交卷无效★)

- ★**零外发** (★只允许下载官方 wheel; ★一次邮件都不许发, 不许联系任何供应商/原厂★) · ★**零采购 · 零下单** (★不许提「买块 RK3572 板」★)
- ★**不许污染 toolkit2 2.3.2 环境** (★装完必须出示旧环境未变的证据★)
- ★**不许重下 wheel / 重装 / 重转模型** (★第 1 趟已装好, 产物 md5 已记在案★)
- ★**不碰 `HW/` / `MECH/` / 网表 / 脚表 / BOM / 板 / `.kicad_pro`**
- ★**不替老板拍路线** (★路线① rk3576-target 维持现状 / 路线② rknn3-toolkit / 路线③ 降 OD 负载或换芯片 = 老板拍★ ⇒ ★**你只交付「路线②的实测结论」, 选哪条不许你代拍★**)
- ★**不自签 `state/issue_log.yaml`** (★verify 留给 main★)
- ★**不许拿「我装好了」当结论, 要拿 rc + 报错原文 + 3 次耗时读数当结论★**

## ⑥ ★给 main 的 (★两条★)

1. ★**ISS-155 的 blocker 状态可以改写成「转换链已通 / 板端待板」** ⇒ ★**实测读数原样报给 main (★上面 §① 表里的数一个都不许改★)★**
2. ★**若往返自证这步补不上 ⇒ 就把"补不上"的原文与原因写进交卷单** ⇒ ★**不许含糊过去, 也不许因此拖住本单★**

★**额外纪律 (★通用, 三条都要守★)**:
① ★**写分片必须用 `python3 state/frag_write.py --agent sw-lead` (禁止 `open(p,"w")`)★**
② ★**只写本任务允许的文件, 不碰别人的★**
③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标★**
④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项★**
⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复★**
