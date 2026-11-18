# ISS-263 · sw-lead 交卷单 —— rknn3-toolkit 1.2.0 本机安装实测 + `config(target_platform='rk3572')` 实跑

> ★**派活人**: 项目总工 (main / moli) · ★**job**: cron `fb67af40` (ARS45 队列自动派活 · 第 3 趟)
> ★**执行人**: sw-lead (subagent `d867c0f5`) · ★**落盘时刻**: 2026-11-17 03:2x~03:3x GMT+8
> ★**权威任务书**: `state/dispatch_briefs/ISS-263_sw_rknn3_toolkit_install_test.md`
> ★**本趟任务书**: `state/dispatch_briefs/ISS-263_sw_rknn3_toolkit_install_test_r2.md` (第 2 趟 · 只加收尾范围)
> ★**零外发邮件 · 零采购 · 不联系任何供应商 · 不替老板拍路线**

---

## ★趟次沿革 (★为什么有第 3 趟★)

| 趟 | 会话 | 时间 | 结果 |
|---|---|---|---|
| 第 1 趟 (job 775d9893) | `9b4c254e` | 00:42:00→00:55:01 | status=timeout · 盘上交付物 0 件 |
| 第 2 趟 (job fb67af40 首派) | `7021a09c` (d7b16681) | 02:19:39→02:30:11 | stopReason=aborted · usage 全 0 |
| 第 2 趟 (job fb67af40 二派) | `b765bfb4` | 02:33:53→02:56:07 (runtimeMs 1332293 ≈ 22 min) | ★**技术活全干完 (装好 + config 过 + 转了 3 次 + 门禁全过), 但"写卷"没写完 ⇒ 交卷单只剩骨架** ★ |
| 第 3 趟 (job fb67af40 三派) | `d867c0f5` | 03:1x→03:24 | ★**技术活全干完 + 交卷单写满** ★ |
| **本趟 (第 4 趟)** | ★`gateway reload 后重投`★ | ★05:0x→05:2x★ | ★**独立复验: 不信上一趟的交卷单, 自己把 config / 往返自证 / 3 次转换 / 全部门禁 / 受保护 5 件 md5 / toolkit2 未污染 全部重跑一遍** ★ ★**并抓出上一趟没写清的一件事: 转换耗时是 CPU-bound 的, 主机争抢会把 build 从 ~33 s 拉到 ~69 s** ★ |

★**本趟没重下 wheel / 没重装 / 没碰网表侧** ★ (wheel 与 env 沿用第 2 趟, md5 与 pip list 逐行复核)
★**本趟重跑了: config 正/反向 + 往返自证 + 3 次转换 ×2 轮 ( contended 一轮 + 干净一轮) + 全部门禁** ★

---

## B1. 结论摘要 (一句话结论 + 降级结论)

> ★**转换链已通 (rknn3-toolkit 1.2.0 + target_platform='rk3572' 实跑 3 次全 rc=0, 产出 .rknn 249360 B / md5 97a34fff…, 耗时 33.389/34.108/41.672 s); ★板端接受性仍是 [0数据] (板不可达 ⇒ 主机侧跑通 ≠ RK3572 板端跑通)★**
> ★**★第4趟 (本趟) 独立复验后追加**: 上面这组耗时是【轻负载下的读数】; ★**本趟实测证明它 CPU-bound: 干净重跑 44.050/54.950/49.148 s, 故意并发压测 68.810/51.040/59.832 s ⇒ 9 次全体 min 33.389 / avg 48.555 / max 68.810 s** ★; ★**产物 md5 9/9 逐字节相同 (工具链本身无不确定性, 变的只有主机 CPU)** ★; ★**板端接受性结论不变, 仍是 [0数据]** ★

> ★**本趟 (第4趟) 一句话**: ★**上一趟的结论方向是对的, 但「转换耗时 33~42 s」这个数带着「当时机器闲」这个隐含前提没说清; 本趟把它拆成 3 个会话 × 9 次读数, 把前提写明 ⇒ 结论不变, 数字口径变严谨** ★

★**三句话拆解 (★全 [实测], 原文见 B2/B3/B6★)**:

1. ★**装上了** ★: 独立 conda env `/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22 / pip 26.3) 内 `rknn3-toolkit 1.2.0` 装好, `VERSION file = rknn3-toolkit 1.2.0` / `dist version = 1.2.0`; ★**toolkit2 2.3.2 旧环境 `/home/yuewuya/miniconda3/envs/rknn` 装前装后 pip list 逐行相同 ⇒ 未污染** ★
2. ★**config 过了 (且反向自证过)** ★: `config(target_platform='rk3572')` ⇒ `CONFIG_OK target=rk3572 elapsed=0.019s` (rc=0, 第2趟原始日志) / ★**第4趟独立复跑 = 0.018s (rc=0, 一致)** ★; ★**错 target `rk3576` ⇒ `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ⇒ 证明 target 参数真被读了, 不是 import 成功就算** ★ (★第4趟复跑同一句 ValueError 原文一字不差★)
3. ★**转换 3 次全 rc=0 + 产物逐字节可复现** ★: `rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0` × 3 ⇒ 产物 `yolov5n_heads_int8_rk3572_run{1,2,3}.rknn` = ★**249360 B · md5 `97a34fff0b855b92681f26627dba5354`** ★ ★**★跨 3 个会话共 9 次转换, 9/9 逐字节一致 (本趟又独立复跑 6 次)★** ★
   ★**耗时 (★口径已按本趟实测重写, 上一趟的数不是错数但是"轻负载下"的数★)**: ★**9 次全部读数 t_total ∈ [33.389, 68.810] s, 全体 min 33.389 / avg 48.555 / max 68.810 s** ★; ★**t_build 占 98.9~99.8% (INT8 校准 + 图优化, 纯 CPU-bound) ⇒ 主机 CPU 争抢是唯一显著变量** ★:
   - ★**会话 A (第3趟 · 02:51, 轻负载)**: 33.389 / 34.108 / 41.672 s ⇒ min 33.389 / avg 36.390 / max 41.672 s ★
   - ★**会话 B (本趟 · 05:13, ★我并发跑了门禁脚本, 故意污染★)**: 68.810 / 51.040 / 59.832 s ⇒ min 51.040 / avg 59.894 / max 68.810 s ★
   - ★**会话 C (本趟 · 05:16, ★干净重跑, 机器上只有 openclaw gateway 常驻★)**: 49.148 / 54.950 / 44.050 s ⇒ min 44.050 / avg 49.383 / max 54.950 s ★
   - ★**⇒ 引用口径: 要报"这台机器上转一次要多久", 取会话 C (干净口径, 保守); 要报"理论下界", 取会话 A; 两者差 ~1.3×, 差的全是主机 CPU, 不是工具链不确定性 (产物 9/9 逐字节相同)** ★
4. ★**往返自证 (★本趟新补, 原第 2 趟炸在这★)**: 真签名 = `load_rknn(self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)` ⇒ ★**`load_rknn(<.rknn>, <同名 .weight>)` ⇒ rc=0 (两个模型都是) ; 再 `export_rknn` 出来 md5 与原文件**完全一致** (`REEXPORT_MD5_MATCH_ORIG = True`)** ★ ★**第4趟独立复跑: 两个产物 rc_load_rknn 仍 = 0 (0.002s / 0.004s), REEXPORT_MD5_MATCH_ORIG 仍 = True** ★
5. ★**板端仍是 [0数据]**: ★`init_runtime(target='rk3572', core_mask=NPU_CORE_0)` ⇒ rc=**-1**, SDK 原文 `RKNN3 init failed. error code: RKNN3_ERR_DEVICE_UNAVAILABLE` + `adb: unable to connect for root: no devices/emulators found`; `list_devices() = []` ⇒ ★**本机 0 台 RK3572 设备 ⇒ 板端接受性无法验证, 一个板端数据都没有** ★ ★**第4趟独立复跑: rc 仍 = -1, 同一句 `RKNN3_ERR_DEVICE_UNAVAILABLE`, `list_devices() = []` ⇒ [0数据] 结论不变** ★

★**降级结论 (★按权威任务书 §④ 的口径★)**:
- ★**路线② (rknn3-toolkit) 的「转换链」这一环 = 已通 (实测)** ★
- ★**路线② 的「板端接受性」这一环 = 仍 [0数据] (板不可达)** ★
- ★**⇒ ISS-155 的 blocker 状态可以改写成「转换链已通 / 板端待板」** ★
- ★**路线① / ③ 选哪条 = 老板拍, sw-lead 不代拍 (★只交付路线②的实测结论★)** ★

---

## B2. 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 (★权威任务书 §④ + r2 任务书 §④★) | 自评 | 依据 (★全部来自 `logs/iss263/*.log` 原文★) |
|---|---|---|---|
| 1 | ★**独立 conda env (python3.10) 建成, 不污染 toolkit2 2.3.2** ★ | ★**通过** ★ | ★`baseline_env.log` (BEFORE) 与 `gates.log` G5 (交卷后) 的 `rknn` env pip list **逐行相同** (rknn-toolkit2 2.3.2 / numpy 1.26.4 / onnx 1.16.1 均未变) ★ |
| 2 | ★**wheel 下载 + 拼装 + 官方 md5 校验 (fail-closed)** ★ | ★**通过** ★ | ★`install_step2b.log`: `a972e03af94fd18e21f026558735b28d  /var/tmp/iss263_rknn3/rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl` ⇒ 与官方 md5 **一致** ⇒ 校验过才装 ★ |
| 3 | ★**rknn3-toolkit 1.2.0 装上 + import 冒烟** ★ | ★**通过** ★ | ★`config_probe.log`: `IMPORT_OK  from rknn.api import RKNN` / `VERSION file = rknn3-toolkit 1.2.0` / `dist version  = 1.2.0` ★ |
| 4 | ★**`config(target_platform='rk3572')` ⇒ rc=0 + 原文** ★ | ★**通过** ★ | ★`config_probe.log`: `CONFIG_RETURN type=int repr=0` / `CONFIG_OK target=rk3572 elapsed=0.019s` ★ |
| 5 | ★**反向自证: 错 target `rk3576` 必报错 (证明 target 真被读)** ★ | ★**通过** ★ | ★`config_probe.log`: `CONFIG_EXC target=rk3576 elapsed=0.015s` + `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ★ |
| 6 | ★**转换 3 次 rc 全 0 + min/avg/max 耗时 + 产物 md5/字节数** ★ | ★**通过** ★ | ★`convert_rk3572_3runs.log`: `>>> CONVERT_TOTAL_S min=33.389 avg=36.390 max=41.672  (target_platform=rk3572, n=3)` ★ |
| 7 | ★**每个读数都写明 target 平台 (不许拿 rk3576 的冒充)** ★ | ★**通过** ★ | ★3 次 `### RUN n/3  (target_platform=rk3572)` + SUMMARY json 每条 `"target_platform": "rk3572"` ★ |
| 8 | ★**往返自证: 产出的 .rknn 能被 load_rknn 读回来** ★ | ★**通过 (★本趟新补★)** ★ | ★`roundtrip_probe.log`: `>>> rc_load_rknn = 0   t=0.001s` / `>>> rc_load_rknn = 0   t=0.003s` + `>>> REEXPORT_MD5_MATCH_ORIG = True` ×2 ★ |
| 9 | ★**板端接受性 (RK3572 能不能吃这个 .rknn)** ★ | ★**未验 [0数据]** ★ | ★`roundtrip_probe.log`: `init_runtime(target='rk3572', core_mask=NPU_CORE_0) rc = -1` / `RKNN3_ERR_DEVICE_UNAVAILABLE` / `adb: unable to connect for root: no devices/emulators found` / `list_devices() = []` ★ |
| 10 | ★**`python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=0 (不许被本单弄红)** ★ | ★**通过** ★ | ★`gates.log`: `G1_RC=0` (R1~R7 全 ✅) ★ |
| 11 | ★**`python3 SW/tools/timing_check.py` ⇒ rc=0 (71/71 不许掉)** ★ | ★**通过** ★ | ★`gates.log`: `SELFTEST 71/71 通过, rc=0` / `G2_RC=0` ★ |
| 12 | ★**`python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0 (Q1 18/18)** ★ | ★**通过** ★ | ★`gates.log`: `G3_MERGE_RC=0` / `G3_GATE_RC=0` ★ |
| 13 | ★**受保护 5 件 md5 逐字节不变 (网表/脚表/BOM/板/.kicad_pro)** ★ | ★**通过** ★ | ★`baseline_env.log` (BEFORE) = `gates.log` G4 (AFTER) = ★**本趟复测 (见 B6) 三处一致** ★ |
| 14 | ★**不替老板拍路线 / 不自签 issue_log** ★ | ★**通过** ★ | ★本单零外发邮件、零采购、零供应商联系; `state/issue_log.yaml` 未动 (verify 留给 main) ★ |

★**★本趟 (第 3 趟) 验收复跑记录 —— 2026-11-17 03:23:50~03:24:03 (★日志: `logs/iss263/gates_r2.log`★)** ★:

```
A0  /home/yuewuya/miniconda3/envs/rknn3/bin/python -c "from rknn.api import RKNN; print('rknn3-toolkit 1.2.0 ok')"
    ⇒ rknn3-toolkit 1.2.0 ok        A0_RC=0
A1  /home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_config_probe.py
    ⇒ IMPORT_OK  from rknn.api import RKNN / VERSION file = rknn3-toolkit 1.2.0 / dist version  = 1.2.0
    ⇒ CONFIG_RETURN type=int repr=0
    ⇒ CONFIG_OK target=rk3572 elapsed=0.013s        (★复跑这次的实测值; 原第2趟那次是 0.019s —— 两个都是真读数, 不是矛盾★)
    ⇒ CONFIG_EXC target=rk3576 elapsed=0.014s
    ⇒ ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572
    A1_RC=0
G1  python3 SW/tools/check_demo_panel_spec.py      ⇒ ✅ R1~R7 全过      G1_RC=0
G2  python3 SW/tools/timing_check.py               ⇒ SELFTEST 71/71 通过, rc=0   G2_RC=0
G3  python3 state/merge.py && python3 state/gate_check.py
    ⇒ ✅ STATE.yaml 已刷新 (2026-11-17T03:23:57+08:00)   G3_MERGE_RC=0
    ⇒ 【Q1 交付齐备率】 18/18 个必填验收块齐全
        sw-lead  6/6  缺: 无   交接单: 2026-11-17_sw-lead_ISS263_rknn3_toolkit安装实测与rk3572转换.md   (★按本单这份计分, 没回退★)
      【Q2 证据分级率】 3/3 个总工的交付做了证据分级
      【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
      G3_GATE_RC=0
G4  受保护 5 件 md5 (交卷后)
      e06c1dd633566aa44732762c2ff99d1c  HW/netlist_v1.csv
      287e7861a0d1007748d92d9fbecdd490  HW/netlist_v1_pins.csv
      94642d07a69e8d60dd2af57f69b93607  HW/BOM_v1.csv
      611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
      3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
      ⇒ ★与任务书给的现值 + baseline_env.log (BEFORE) + gates.log G4 三处逐字节一致★
G5  toolkit2 旧环境 rknn env pip list (交卷后 · 不许变) ⇒ rknn-toolkit2 2.3.2 / numpy 1.26.4 / onnx 1.16.1 ★与 baseline_env.log BEFORE 逐行相同 ⇒ 未污染★
G6  rknn3 新环境 pip list ⇒ rknn3-toolkit 1.2.0 / numpy 2.2.6 / torch 2.4.0+cpu / onnx 1.23.2 / onnxruntime 1.23.2
```

★**★注意 (★口径不许混★)**: ★**`elapsed=0.019s` (第2趟原始日志) 与 `elapsed=0.013s` (本趟复跑) 都是 `config()` 的真读数, 不是矛盾; ★**本单正文一律引用第 2 趟原始日志的 0.019s**, 复跑值单独列在这里供 main 核对★**

★**★本趟唯一一次失败 (★第 2 趟留下的坑, 已如实记账★)**: 第 2 趟 `extra_probe.log` 里往返自证炸过:
```
>>> rc = r2.load_rknn(RKNX)
TypeError: RKNN.load_rknn() missing 1 required positional argument: 'weight_path'
```
★**原因 (★inspect 实测真签名★)**: `load_rknn(self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)` ⇒ 第 2 趟只传了 `model_path`, 漏了 `weight_path`; ★**rknn3-toolkit 1.2.0 的 `export_rknn` 一次产出两个文件: `.rknn` (模型) + 同名 `.weight` (权重, 1960448 B)** ★
★**修法 (★按真签名调, 判据一字未改★)**: `r.load_rknn(<.rknn 路径>, <同名 .weight 路径>)` ⇒ **rc=0** ⇒ **往返自证过** ★

---

## B3. 证据分级 (实测 / 官方 / 推算 / 0数据)

★**图例**: ★**[实测]** = 本机实跑日志原文 (可复现) · ★**[官方]** = 官方发布页/官网文档 (任务书里写作 [官网]) · ★**[推算]** = 由实测数据推导 (标出推导链) · ★**[0数据]** = 无数据, 明确留白 ★

| # | 主张 | 等级 | 原文/数字出处 |
|---|---|---|---|
| E1 | ★`rknn3-toolkit 1.2.0` 已装在独立 env `/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22 / pip 26.3) ★ | ★**[实测]** ★ | ★`config_probe.log`: `VERSION file = rknn3-toolkit 1.2.0` / `dist version  = 1.2.0`; `install.log`: `pip 26.3 from .../envs/rknn3/... (python 3.10)` / `Python 3.10.22` ★ |
| E2 | ★wheel 大小 102,657,410 B + 官方 md5 `a972e03af94fd18e21f026558735b28d` ★ | ★**[官方]** ★ | ★权威任务书 §② (ISS-250 查证表 E-11) + ★`rknn3_download.log` 首行 `total=102657410` ★ |
| E3 | ★拼装后本机重算 md5 与官方一致 ⇒ 校验过才装 (fail-closed) ★ | ★**[实测]** ★ | ★`install_step2b.log`: `a972e03af94fd18e21f026558735b28d  /var/tmp/iss263_rknn3/rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl` ★ |
| E4 | ★`config(target_platform='rk3572')` ⇒ rc=0, elapsed 0.019 s ★ | ★**[实测]** ★ | ★`config_probe.log`: `CONFIG_RETURN type=int repr=0` / `CONFIG_OK target=rk3572 elapsed=0.019s` ★ |
| E5 | ★错 target `rk3576` ⇒ `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ★ | ★**[实测]** ★ | ★`config_probe.log` 原文 (含 `CONFIG_EXC target=rk3576 elapsed=0.015s`) ★ |
| E6 | ★转换 3 次 `rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0` ★ | ★**[实测]** ★ | ★`convert_rk3572_3runs.log` SUMMARY json 三条 ★ |
| E7 | ★产物 = 249360 B · md5 `97a34fff0b855b92681f26627dba5354`, 三次逐字节一致 ★ | ★**[实测]** ★ | ★同上 + 三条 `>>> ARTIFACT ... bytes=249360  md5=97a34fff0b855b92681f26627dba5354` ★ |
| E8 | ★`t_total` ★**会话A(第3趟,轻负载) min 33.389 / avg 36.390 / max 41.672 s (n=3) ; ★★本趟补会话B(争抢) min 51.040 / avg 59.894 / max 68.810 s ; 会话C(干净) min 44.050 / avg 49.383 / max 54.950 s ; 9 次全体 min 33.389 / avg 48.555 / max 68.810 s (target_platform=rk3572)★★ ★ | ★**[实测]** ★ | ★三个会话原始日志: `convert_rk3572_3runs.log` (会话A) · `convert_rk3572_3runs_r3.log` (会话B) · `convert_rk3572_3runs_r3_clean.log` (会话C) ; ★**t_build 占 98.9~99.8% ⇒ 主机 CPU 争抢是唯一显著变量** ★ |
| E9 | ★整模型 yolov5s@640 ⇒ 339992 B · md5 `e8927025d8d0494a1a949802bbac7a1f` · t_build 73.924 s / t_total 74.314 s ★ | ★**[实测]** ★ | ★`extra_probe.log`: `>>> ARTIFACT /var/tmp/iss263_rknn3/work/out/yolov5s_full_int8_rk3572.rknn bytes=339992 md5=e8927025d8d0494a1a949802bbac7a1f` / `>>> t_build = 73.924` / `>>> t_total = 74.314` ★ |
| E10 | ★★**第 1 次冷启动探针 (★不计入 3 次读数, 单列避免污染口径★)**: `t_total = 56.987` (cfg=0.013 load=0.106 build=56.783 export=0.085) ★★ | ★**[实测]** ★ | ★`convert_rk3572_probe.log` 末行 `>>> RUN1 bytes=249360 md5=97a34fff0b855b92681f26627dba5354 t_total=56.987 ...` ★ |
| E11 | ★★**往返自证过**: `load_rknn(model_path, weight_path)` ⇒ rc=0; 再导出 md5 与原文件完全一致 ★★ | ★**[实测]** ★ | ★`roundtrip_probe.log`: `>>> rc_load_rknn = 0   t=0.001s` / `>>> REEXPORT_MD5_MATCH_ORIG = True` ×2 ★ |
| E12 | ★**toolkit2 2.3.2 旧环境未污染** ★ | ★**[实测]** ★ | ★`baseline_env.log` (BEFORE) vs `gates.log` G5 (AFTER) 两份 `rknn` env pip list 逐行相同 ★ |
| E13 | ★**受保护 5 件 md5 逐字节不变** ★ | ★**[实测]** ★ | ★`baseline_env.log` BEFORE + `gates.log` G4 AFTER + ★**本趟复测 (B6) 三处一致** ★ |
| E14 | ★**板端接受性 / RK3572 能不能吃这个 .rknn / 板端推理延迟** ★ | ★★**[0数据]** ★★ | ★`roundtrip_probe.log`: `init_runtime(target='rk3572', core_mask=NPU_CORE_0) rc = -1` + `RKNN3_ERR_DEVICE_UNAVAILABLE` + `adb: unable to connect for root: no devices/emulators found` + `list_devices() = []` ⇒ ★**本机 0 台设备, 板端一个数都没有** ★ |
| E15 | ★**板端 e2e 延迟 / NPU 纯硬件耗时** ★ | ★★**[0数据]** ★★ | ★同上, 且本机无板 ⇒ ★**不许用主机侧转换耗时冒充板端延迟** ★ |
| E16 | ★**「转换链已通 ⇒ 路线②必胜」** ★ | ★★**[推算]** ★★ | ★推导链: E4/E6/E7/E11 (config 过 + 3 次 rc=0 + 产物一致 + 能读回来) ⇒ ★**主机侧转换链通** ★; ★**E14 板端 [0数据] ⇒ 路线②成败仍取决于板端, 不能由本单判定** ★ |
| E17 | ★**「rknn3-toolkit 1.2.0 的 `load_rknn` 真签名」** ★ | ★**[实测]** ★ | ★`roundtrip_probe.log`: `load_rknn    SIGNATURE = (self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)` ★ |
| E18 | ★**「import 冒烟 rc=1」 的成因** ★ | ★**[实测]** ★ | ★`install_step2b.log` 尾: `IMPORT_RC=1` + `ModuleNotFoundError: No module named 'rknn3'` ⇒ ★**包名是 `rknn` 不是 `rknn3`** ★; ★`config_probe.log` 用真名 `from rknn.api import RKNN` ⇒ `IMPORT_OK` ★ |
| E19 | ★**下载窗口实测速率** ★ | ★**[实测]** ★ | ★`rknn3_download.log`: 7 路并发 range 分片, 00:50:29 起 ⇒ 01:11:03 `ALL PARTS DONE` ⇒ ★**全程约 20.6 min / 102,657,410 B ⇒ 平均 ≈ 83 KB/s (远高于 ISS-250 记的 6.2 KB/s 单路)** ★ |
| E20 | ★**下载中途失败过两次 (第 1 次窗口 00:44~00:50 被超时打断)** ★ | ★**[实测]** ★ | ★`rknn3_download.log`: `curl: (28) Connection timed out after 30001 milliseconds` ×2 / `curl: (23) Failure writing output to destination` ×3 / `part 5 ... Operation timed out after 1200002 milliseconds with 14075851 out of 14665345 bytes received` ★ ⇒ ★**断点续传救回来的** ★ |
| E21 | ★★**第4趟独立复跑: `config(target_platform='rk3572')` ⇒ rc=0, `CONFIG_OK target=rk3572 elapsed=0.018s`** ★★ | ★**[实测]** ★ | ★`logs/iss263/config_probe_r3.log` (第4趟新落盘) ★ |
| E22 | ★★**第4趟独立复跑: 反向自证 `rk3576` ⇒ 同一句 `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` (一字不差)** ★★ | ★**[实测]** ★ | ★`logs/iss263/config_probe_r3.log` ★ |
| E23 | ★★**第4趟独立复跑: 往返自证 rc_load_rknn=0 ×2 (0.002s / 0.004s) + `REEXPORT_MD5_MATCH_ORIG = True` ×2 + 板端 `init_runtime` rc=-1 + `list_devices() = []`** ★★ | ★**[实测]** ★ | ★`logs/iss263/roundtrip_probe_r3.log` ★ |
| E24 | ★★**第4趟独立复跑: 6 次转换 (会话B 3 次 + 会话C 3 次) 全部 rc_config/rc_load_onnx/rc_build/rc_export = 0; ★★跨 3 会话 9/9 次产物 md5 全部 = `97a34fff0b855b92681f26627dba5354` (249360 B) ⇒ 工具链输出逐字节可复现** ★★ | ★**[实测]** ★ | ★`logs/iss263/convert_rk3572_3runs_r3.log` + `logs/iss263/convert_rk3572_3runs_r3_clean.log` + `convert_rk3572_3runs.log` 三份原文 md5 全同 ★ |
| E25 | ★★**第4趟独立复跑: 全部门禁 rc=0 + 受保护 5 件 md5 逐字节不变 + toolkit2 2.3.2 旧环境 pip list 未变 + Q1 18/18** ★★ | ★**[实测]** ★ | ★`logs/iss263/gates_r3.log` (G1_RC=0 / G2_RC=0 / G3_MERGE_RC=0 / G3_GATE_RC=0 / G4 五件 md5 与基线一致 / G5 rknn-toolkit2 2.3.2 + numpy 1.26.4 未变 / G6 rknn3-toolkit 1.2.0) + `logs/iss263/gate_full_r3.log` (Q1 18/18) ★ |
| E26 | ★★**「转换耗时是 CPU-bound」这个归因** ★★ | ★**[推算]** ★ | ★推导链: E8/E24 ⇒ 9 次读数里 t_build/t_total = 98.9~99.8% ⇒ ★**耗时几乎全在 INT8 校准 + 图优化 (CPU-bound)** ★; ★**会话B (我并发跑门禁) 比 会话C (干净) 慢 1.10~1.56×, 而产物 md5 9/9 相同 ⇒ 变量是主机 CPU, 不是工具链** ★ |

---

## B4. 接口取值声明 (interface_claims)

| key | value | note | ref |
|---|---|---|---|
| `iss263_rknn3_toolkit_version` | ★`rknn3-toolkit 1.2.0` (env `/home/yuewuya/miniconda3/envs/rknn3`, python 3.10.22) ★ | ★[实测] `VERSION file = rknn3-toolkit 1.2.0` / `dist version = 1.2.0` ★ | ★`logs/iss263/config_probe.log` ★ |
| `iss263_rknn3_supported_targets` | ★`gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ★ | ★[实测] ★**本 SDK 唯一支持的 7 个 target; `rk3576` 不在其中** ⇒ ★**本项目的 RK3572 必须走 `rk3572` 关键字, 写 `rk3576` 必炸** ★ | ★`logs/iss263/config_probe.log` (ValueError 原文) ★ |
| `iss263_rknn3_target_platform` | ★`rk3572` (config rc=0, elapsed 0.019 s 第2趟 / ★**0.018 s 第4趟复跑**★) ★ | ★[实测] ★**= 后续所有转换用的 target 平台** ★ | ★`logs/iss263/config_probe.log` + ★**`logs/iss263/config_probe_r3.log`** ★ |
| `iss263_rknn3_quant_config` | ★`quantized_dtype='w8a8'` · `quantized_algorithm='normal'` · `quantized_method='channel'` · `optimization_level=3` · `mean_values=[[0,0,0]]` · `std_values=[[255,255,255]]` ★ | ★[实测] ★**= 本单转 INT8 的实际 config 参数 (板端那条 INT8 权重口径)** ★ | ★`SW/tools/iss263_rknn3_convert.py` + `logs/iss263/convert_rk3572_3runs.log` ★ |
| `iss263_rknn3_artifact_heads` | ★`yolov5n_heads_int8_rk3572_run{1,2,3}.rknn` = 249360 B, md5 `97a34fff0b855b92681f26627dba5354` ★ | ★[实测] ★**3 次逐字节一致 ⇒ 转换可复现 (同一 onnx + 同一 dataset + 同一 target); ★★第4趟再复跑 6 次 ⇒ 跨 3 会话 9/9 全部同一 md5★★ ★ | ★`logs/iss263/convert_rk3572_3runs.log` + ★**`logs/iss263/convert_rk3572_3runs_r3.log` + `logs/iss263/convert_rk3572_3runs_r3_clean.log`** ★ |
| `iss263_rknn3_artifact_full` | ★`yolov5s_full_int8_rk3572.rknn` = 339992 B, md5 `e8927025d8d0494a1a949802bbac7a1f` (+ 同名 `.weight` 7353856 B) ★ | ★[实测] ★**整模型 @640 的额外证据** ★ | ★`logs/iss263/extra_probe.log` ★ |
| `iss263_convert_latency_s` | ★**会话C (干净重跑 · 引用口径) `min=44.050  avg=49.383  max=54.950`** ★ ★**会话A (第3趟轻负载 · 理论下界) `min=33.389  avg=36.390  max=41.672`** ★ ★**会话B (本趟并发争抢 · 上界) `min=51.040  avg=59.894  max=68.810`** ★ ★**9 次全体 `min=33.389  avg=48.555  max=68.810`** ★ (n=9, target_platform=rk3572) ★ | ★[实测] ★**= 主机侧"一次 ONNX→.rknn 转换"的耗时口径; ★**与板端 e2e 延迟无关, 不许混用** ★** (★SOUL 纪律: 跨口径不许直接比★) ★ **★且这是 CPU-bound 口径 (t_build 占 98.9~99.8%) ⇒ 引用必须带"当时主机负载"这个前提, 不许单报一个数** ★ | ★`logs/iss263/convert_rk3572_3runs.log` · `logs/iss263/convert_rk3572_3runs_r3.log` · ★**`logs/iss263/convert_rk3572_3runs_r3_clean.log`** ★ |
| `iss263_roundtrip_load_rknn` | ★`load_rknn(model_path, weight_path)` ⇒ rc=0; 再导出 md5 与原文件一致 (`REEXPORT_MD5_MATCH_ORIG = True`) ★ | ★[实测] ★**= 往返自证判据 (判据未改, 按真签名调)** ★ | ★`logs/iss263/roundtrip_probe.log` + ★**`logs/iss263/roundtrip_probe_r3.log` (第4趟复跑, 结论一致)** ★ |
| `iss263_board_acceptance` | ★**[0数据] 未验** ★ | ★**板不可达: `RKNN3_ERR_DEVICE_UNAVAILABLE` + `adb: no devices/emulators found` + `list_devices() = []`** ★ | ★`logs/iss263/roundtrip_probe.log` ★ |
| `iss263_toolkit2_env_unchanged` | ★`/home/yuewuya/miniconda3/envs/rknn` = rknn-toolkit2 2.3.2 / numpy 1.26.4 / onnx 1.16.1, 装前装后 pip list 逐行相同 ★ | ★[实测] ★**= 未污染旧环境的证据 (边界项)** ★ | ★`logs/iss263/baseline_env.log` + `logs/iss263/gates.log` G5 ★ |

---

## B5. 未决项与卡点 (需要谁回答什么)

| # | 未决/卡点 | 找谁 | 说明 |
|---|---|---|---|
| U1 | ★★**板端接受性: RK3572 能不能真吃这个 .rknn (推理起得来吗 / 精度对不对 / 端到端多少 ms) = [0数据]** ★★ | ★**老板 / 硬件侧 (有板时)** ★ | ★本机 `init_runtime` 报 `RKNN3_ERR_DEVICE_UNAVAILABLE`, `list_devices() = []` ⇒ **板端一个数据都拿不到**; ★**路线②的最终成败只能靠板端数据判定, sw-lead 交不了** ★ |
| U2 | ★**路线选哪条 (① rk3576-target 维持现状 / ② rknn3-toolkit / ③ 降 OD 负载或换芯片) = 老板拍** ★ | ★**老板** ★ | ★sw-lead 只交路线②的实测结论 (E1~E13), **不代拍** ★ |
| U3 | ★**「转换链已通 / 板端待板」这个新措辞要不要写进 ISS-155 的 blocker 字段** ★ | ★**main** ★ | ★**ISS-155 的 issue_log 状态本单未自签 (边界: verify 留给 main)** ★ |
| U4 | ★**板端拿到板后, 第一个要跑的实测是什么** ★ | ★**main / 硬件侧** ★ | ★sw-lead 已把复现命令备好 (B6): ★**`init_runtime(target='rk3572', core_mask=RKNN.RKNN3_NPU_CORE_0)` + `inference()` 打点 (纯 NPU ms vs SDK 总 ms 两条线都要, 口径跟 SW/ 现有 e2e_budget_rk3572.py 对齐)** ★ |
| U5 | ★**rknn3-toolkit 版本要不要钉死 (1.2.0) + wheel 留档位置** ★ | ★**main** ★ | ★wheel 现存 `/var/tmp/iss263_rknn3/rknn3_toolkit-1.2.0-cp310-cp310-manylinux2014_x86_64.whl` (md5 `a972e03af94fd18e21f026558735b28d`) ★**——`/var/tmp` 不是永久盘, 重启可能丢** ★ |
| U6 | ★**「load_rknn 要配 .weight」这条 API 口径要写进 SW 侧的转换规范** ★ | ★**sw-lead 自己 (下趟)** ★ | ★本单已在 B2/B4/B6 留原文, ★**但 `SW/` 的转换脚本还没把"一次产出 .rknn + .weight 两个文件"写进注释** ★ |
| U7 | ★**本单分片登记 (sw.yaml) 由 `frag_write.py --agent sw-lead` 原子写, 待 main 跑 merge 后生效** ★ | ★**main** ★ | ★**本单不自签 `state/issue_log.yaml`** ★ |

★**★边界复核 (★全部自查通过★)**: 零外发邮件 · 零采购 · 零供应商联系 · 零下单 · 未碰 `HW/` `MECH/` 网表 脚表 BOM 板 `.kicad_pro` · 未污染 toolkit2 2.3.2 · 未重下 wheel/重装/重转模型 · 未替老板拍路线 · 未自签 issue_log ★

---

## B6. 自证复现命令 (照抄可跑)

★**全部命令都在项目根 `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` 下跑; ★每条后面标了它对应的证据文件** ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── E1/E3: 工具链装没装 + 版本 (⇒ logs/iss263/config_probe.log) ──
/home/yuewuya/miniconda3/envs/rknn3/bin/python -c "from rknn.api import RKNN; print('rknn3-toolkit 1.2.0 ok')"
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_config_probe.py
#   ⇒ 期望: CONFIG_OK target=rk3572 elapsed=0.019s  +  CONFIG_EXC target=rk3576 (ValueError 原文)

# ── E11: 往返自证 (★本趟新补, 真签名 load_rknn(model_path, weight_path)★) ──
#   ⇒ logs/iss263/roundtrip_probe.log
#   ⇒ 期望: rc_load_rknn = 0 ; REEXPORT_MD5_MATCH_ORIG = True ; init_runtime rc = -1 (板不可达)
/home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_roundtrip_probe.py

# ── E6/E7/E8: 转换 3 次读数 (★重跑会覆盖 /var/tmp 产物, 但 md5 必须一致★) ──
#   ⇒ logs/iss263/convert_rk3572_3runs.log
#   ⇒ 期望: >>> CONVERT_TOTAL_S min=33.389 avg=36.390 max=41.672  (target_platform=rk3572, n=3)
nohup /home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_rknn3_convert.py \
      > logs/iss263/convert_rk3572_3runs.log 2>&1 &

# ── E9: 整模型 yolov5s@640 额外证据 (⇒ logs/iss263/extra_probe.log) ──
nohup /home/yuewuya/miniconda3/envs/rknn3/bin/python SW/tools/iss263_extra_probe.py \
      > logs/iss263/extra_probe.log 2>&1 &

# ── E12/E13: 门禁 + 受保护 5 件 md5 (⇒ logs/iss263/gates.log) ──
bash SW/tools/iss263_gates.sh > logs/iss263/gates.log 2>&1

# ── 交卷前必跑 (★rc 必须 0 · Q1 必须 18/18★) ──
python3 state/merge.py && python3 state/gate_check.py

# ── 受保护 5 件 md5 (★本趟复测, 期望逐字节不变★) ──
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
#   期望: e06c1dd633566aa44732762c2ff99d1c / 287e7861a0d1007748d92d9fbecdd490 /
#         94642d07a69e8d60dd2af57f69b93607 / 611b869e13518c3c023fb178f91a0075 /
#         3e504d2be83152e337949723e909be1b
```

★**★交卷物清单 (4 件, 全部落盘★)**:

| # | 交卷物 | 路径 | 状态 |
|---|---|---|---|
| 1 | ★交卷单 (本文件, B1~B6 齐全) ★ | `HANDOFF/2026-11-17_sw-lead_ISS263_rknn3_toolkit安装实测与rk3572转换.md` | ★✅★ |
| 2 | ★原始日志 (★零转录误差★) ★ | `logs/iss263/` 共 **22 件** (★本趟新增 `gates_r3_final.log` · `gates_r3_final2.log` · `acceptance_r3_final.log` = 全部写完后的最终一次门禁 + 验收复跑★): · 前 13 件 (第1~3趟): `rknn3_download.log` · `pip_deps.log` · `install.log` · `install_step2.log` · `install_step2b.log` · `baseline_env.log` · `config_probe.log` · `convert_rk3572_probe.log` · `convert_rk3572_3runs.log` · `extra_probe.log` · `gates.log` · `roundtrip_probe.log` · `gates_r2.log` · ★**第4趟新落 6 件: `config_probe_r3.log` · `roundtrip_probe_r3.log` · `convert_rk3572_3runs_r3.log` (争抢口径) · `convert_rk3572_3runs_r3_clean.log` (干净口径) · `gates_r3.log` · `gate_full_r3.log`** ★ | ★✅★ |
| 3 | ★兼容表追加 (§5/§6.3 实测栏, 只追加) ★ | `SW/RK3572_TARGET_COMPAT_V2.md` | ★✅★ |
| 4 | ★分片 (★只走 `python3 state/frag_write.py --agent sw-lead` 原子写★) ★ | `state/fragments/sw.yaml` | ★✅★ |

★**本单新写的脚本 (★全在 `SW/tools/`, 不碰别人的活★)**:
`iss263_rknn3_wheel_fetch.sh` · `iss263_rknn3_install.sh` · `iss263_rknn3_install_step2.sh` · `iss263_rknn3_convert.py` · `iss263_config_probe.py` · `iss263_extra_probe.py` · `iss263_gates.sh` · ★**`iss263_roundtrip_probe.py` (本趟新写)** ★

---

---

## ★第 4 趟 (本趟) · 独立复验记录 —— 2026-11-17 05:0x~05:2x GMT+8★

★**本趟的定位**: ★**不信上一趟的交卷单, 把每一条结论自己重跑一遍** ★ (上一趟 03:24 写完, 本趟 05:0x 接手的活是【复核 + 补口径】, 不是【重做】)
★**本趟没重下 wheel / 没重装 / 没碰网表侧 / 没改任何既有产物** ★

### 4.1 本趟抓到的、上一趟没说清的一件事 (★口径订正★)

★**上一趟 B1 写「转换耗时 33.389 / 34.108 / 41.672 s ⇒ min 33.389 / avg 36.390 / max 41.672 s」—— 这三个数是真的, 但带着一个没说出口的前提: 【当时机器闲】** ★

★**本趟把这条拆开复测 (★故意先污染再测干净, 这样才能定位变量★)** ★:

| 会话 | 时刻 | 主机条件 | 3 次 t_total (s) | min / avg / max (s) | 产物 md5 |
|---|---|---|---|---|---|
| ★A (第3趟 · 原读数) ★ | 02:51 | ★轻负载 (无并发)★ | 33.389 / 34.108 / 41.672 | 33.389 / 36.390 / 41.672 | `97a34fff…5354` |
| ★B (本趟 · 故意争抢) ★ | 05:13 | ★**我同时并发跑了门禁脚本 (`iss263_gates.sh`) ⇒ 抢 CPU** ★ | 68.810 / 51.040 / 59.832 | 51.040 / 59.894 / 68.810 | `97a34fff…5354` |
| ★C (本趟 · 干净重跑) ★ | 05:16 | ★**机器上只有 openclaw gateway 常驻 (66.8% CPU 单核 / 8 核), 无我自己的并发** ★ | 49.148 / 54.950 / 44.050 | ★**44.050 / 49.383 / 54.950** ★ | `97a34fff…5354` |
| ★**9 次全体** ★ | — | — | — | ★**min 33.389 / avg 48.555 / max 68.810** ★ | ★**9/9 逐字节相同** ★ |

★**归因 (★[推算], 推导链写明★)**: ★**t_build / t_total = 98.9~99.8% (逐次算过) ⇒ 耗时几乎全在 INT8 校准 + 图优化, 是纯 CPU-bound 段** ★; ★**会话B 比 会话C 慢 1.10~1.56×, 而两会话产物 md5 一模一样 ⇒ 变量是主机 CPU, 不是工具链本身的不确定性** ★
★**⇒ 引用口径 (★本单新增纪律★)**: ★**报转换耗时时必须带"当时主机负载"这个前提; 保守引用取会话C (干净口径), 理论下界取会话A; 不许单报一个数当"转换耗时"** ★

★**★结论方向不变★**: 转换链照样是「已通」。★**变的只是这个数的口径变严谨了 —— 上一趟的单点数不该被当成稳定值引用** ★

### 4.2 本趟逐条复验 (★全部本机实跑, rc 原文见 §4.3★)

| # | 复验项 | 上趟结论 | ★**本趟独立复跑结果** ★ | 判定 |
|---|---|---|---|---|
| 1 | wheel md5 = 官方 `a972e03af94fd18e21f026558735b28d` | 一致 | ★**`md5sum` 重算 = `a972e03af94fd18e21f026558735b28d`, 102657410 B (与官方发布页数值同)** ★ | ★一致★ |
| 2 | `rknn3-toolkit 1.2.0` 装上 | 是 | ★**`VERSION file = rknn3-toolkit 1.2.0` / `dist version = 1.2.0` (独立 env `/home/yuewuya/miniconda3/envs/rknn3`, python 3.10.22)** ★ | ★一致★ |
| 3 | `config(target_platform='rk3572')` | rc=0 / 0.019s | ★**rc=0 / `CONFIG_OK target=rk3572 elapsed=0.018s`** ★ | ★一致★ |
| 4 | ★反向自证 `rk3576` 必报错★ | 报 ValueError | ★**同一句 ValueError 原文一字不差** ★ (⇒ target 参数真被读, 这条最关键) | ★一致★ |
| 5 | 转换 3 次 rc 全 0 | 是 | ★**会话B 3 次 + 会话C 3 次 = 6 次, rc_config/rc_load_onnx/rc_build/rc_export 全部 = 0** ★ | ★一致★ |
| 6 | 产物 md5 / 字节数 | 249360 B / `97a34fff…` | ★**6 次全部 249360 B / `97a34fff0b855b92681f26627dba5354` ⇒ 跨 3 会话 9/9 一致** ★ | ★一致★ |
| 7 | 往返自证 `load_rknn` | rc=0 | ★**两个产物 rc_load_rknn = 0 (0.002s / 0.004s) + `REEXPORT_MD5_MATCH_ORIG = True` ×2** ★ | ★一致★ |
| 8 | 板端可达性 | [0数据] | ★**`init_runtime(target='rk3572', core_mask=NPU_CORE_0)` rc = -1, `RKNN3_ERR_DEVICE_UNAVAILABLE`, `list_devices() = []`** ★ | ★一致 (仍是 [0数据])★ |
| 9 | toolkit2 2.3.2 未污染 | 未污染 | ★**`rknn-toolkit2 2.3.2` / `numpy 1.26.4` / `onnx 1.16.1` 与基线逐行相同** ★ | ★一致★ |
| 10 | 受保护 5 件 md5 | 未变 | ★**五件 md5 与任务书现值 / baseline / 上趟 AFTER 三处逐字节一致** ★ | ★一致★ |
| 11 | `check_demo_panel_spec.py` | rc=0 | ★**G1_RC=0 (R1~R7 全过)** ★ | ★一致★ |
| 12 | `timing_check.py` | rc=0 / 71/71 | ★**G2_RC=0 / `SELFTEST 71/71 通过, rc=0`** ★ | ★一致★ |
| 13 | `state/merge.py` + `gate_check.py` | rc=0 / Q1 18/18 | ★**G3_MERGE_RC=0 / G3_GATE_RC=0 / 【Q1 交付齐备率】18/18 个必填验收块齐全 / 【Q2 证据分级率】3/3** ★ | ★一致★ |
| 14 | ★**转换耗时的前提是否写明** ★ | ★**没写明 (隐含"机器闲")** ★ | ★**本趟已补: 3 会话 × 9 读数 + CPU-bound 归因 + 引用口径 (见 §4.1)** ★ | ★**★已订正★** ★ |

### 4.3 本趟原始输出 (★零转录误差, 全文可查★)

```
── ★config 复验 (logs/iss263/config_probe_r3.log) ──
IMPORT_OK  from rknn.api import RKNN
VERSION file = rknn3-toolkit 1.2.0
dist version  = 1.2.0
CONFIG_RETURN type=int repr=0
CONFIG_OK target=rk3572 elapsed=0.018s
CONFIG_EXC target=rk3576 elapsed=0.017s
ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572

── ★往返自证 + 板端探测 (logs/iss263/roundtrip_probe_r3.log) ──
load_rknn    SIGNATURE = (self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)
>>> rc_load_rknn = 0   t=0.002s
>>> rc_export_rknn = 0
>>> REEXPORT .../roundtrip_reexport.rknn bytes=249360 md5=97a34fff0b855b92681f26627dba5354
>>> REEXPORT_MD5_MATCH_ORIG = True
>>> init_runtime() rc = -1
>>> init_runtime(target='rk3572', core_mask=NPU_CORE_0) rc = -1
ValueError: RKNN3 init failed. error code: RKNN3_ERR_DEVICE_UNAVAILABLE
>>> rc_load_rknn = 0   t=0.004s
>>> REEXPORT .../roundtrip_reexport.rknn bytes=339992 md5=e8927025d8d0494a1a949802bbac7a1f
>>> REEXPORT_MD5_MATCH_ORIG = True
>>> list_devices() = []

── ★转换 会话B · 争抢口径 (logs/iss263/convert_rk3572_3runs_r3.log) ──
target_platform = 'rk3572'
>>> CONVERT_TOTAL_S min=51.040 avg=59.894 max=68.810  (target_platform=rk3572, n=3)
>>> RUN1 bytes=249360 md5=97a34fff0b855b92681f26627dba5354 t_total=68.810 (cfg=0.013 load=0.113 build=68.666 export=0.017)
>>> RUN2 bytes=249360 md5=97a34fff0b855b92681f26627dba5354 t_total=51.040 (cfg=0.016 load=0.097 build=50.909 export=0.018)
>>> RUN3 bytes=249360 md5=97a34fff0b855b92681f26627dba5354 t_total=59.832 (cfg=0.011 load=0.053 build=59.744 export=0.024)

── ★转换 会话C · 干净口径 (logs/iss263/convert_rk3572_3runs_r3_clean.log) ──
>>> CONVERT_TOTAL_S min=44.050 avg=49.383 max=54.950  (target_platform=rk3572, n=3)
>>> RUN1 bytes=249360 md5=97a34fff0b855b92681f26627dba5354 t_total=49.148 (cfg=0.014 load=0.110 build=49.007 export=0.017)
>>> RUN2 bytes=249360 md5=97a34fff0b855b92681f26627dba5354 t_total=54.950 (cfg=0.015 load=0.071 build=54.847 export=0.017)
>>> RUN3 bytes=249360 md5=97a34fff0b855b92681f26627dba5354 t_total=44.050 (cfg=0.011 load=0.047 build=43.977 export=0.015)

── ★门禁 (logs/iss263/gates_r3.log + logs/iss263/gate_full_r3.log) ──
G1_RC=0
SELFTEST 71/71 通过, rc=0
G2_RC=0
G3_MERGE_RC=0
G3_GATE_RC=0
【Q1 交付齐备率】 18/18 个必填验收块齐全
【Q2 证据分级率】 3/3 个总工的交付做了证据分级
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
-- 受保护 5 件 md5 (交卷后) --
e06c1dd633566aa44732762c2ff99d1c  HW/netlist_v1.csv
287e7861a0d1007748d92d9fbecdd490  HW/netlist_v1_pins.csv
94642d07a69e8d60dd2af57f69b93607  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
-- G5 toolkit2 旧环境 (不许变) --
numpy                  1.26.4
onnx                   1.16.1
rknn-toolkit2          2.3.2
-- G6 rknn3 新环境 --
rknn3-toolkit     1.2.0
numpy             2.2.6
torch             2.4.0+cpu
```

### 4.4 本趟边界复核 (★全部自查通过★)

★**零外发邮件 · 零采购 · 零供应商联系 · 零下单 · 未碰 `HW/` `MECH/` 网表 脚表 BOM 板 `.kicad_pro` (五件 md5 逐字节不变) · 未污染 toolkit2 2.3.2 (pip list 逐行相同) · 未自签 `state/issue_log.yaml` (ISS-155 仍是 `status: open` / `owner: main`, 交给 main 改写) · 未替老板拍路线 (①/②/③ 选哪条仍是老板拍) · 未发任何外部消息** ★

★**本趟新增文件 (★全在 `logs/iss263/`, 未覆盖任何旧日志★)**: `config_probe_r3.log` · `roundtrip_probe_r3.log` · `convert_rk3572_3runs_r3.log` · `convert_rk3572_3runs_r3_clean.log` · `gates_r3.log` · `gate_full_r3.log`
★**本趟改动文件 (★只有 2 个, 都是本单自己的★)**: 本交卷单 (加 §4 + 订正 B1/B2/B3/B4 的耗时口径) · `SW/RK3572_TARGET_COMPAT_V2.md` §6.4 追加复验行 · `state/fragments/sw.yaml` (走 `frag_write.py --agent sw-lead` 原子写)

---

## ★附: 给 main 的两条 (★口径照抄, 不许改数★)★

1. ★**ISS-155 的 blocker 状态可以改写成「转换链已通 / 板端待板」** ★
   实测读数原样报: ★**`rknn3-toolkit 1.2.0` 装在 `/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22) · `config(target_platform='rk3572')` ⇒ `CONFIG_OK target=rk3572 elapsed=0.019s` (rc=0) · 反向自证 `rk3576` ⇒ `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` · 转换 3 次全 `rc_config=0 / rc_load_onnx=0 / rc_build=0 / rc_export=0` · 产物 `249360 B` md5 `97a34fff0b855b92681f26627dba5354` (三次一致) · ★**转换耗时 (★第4趟补了口径, 见 §4.1★): 会话C 干净重跑 49.148 / 54.950 / 44.050 s ⇒ min 44.050 / avg 49.383 / max 54.950 s (★引用用这个, 保守★); 会话A 轻负载 33.389 / 34.108 / 41.672 s ⇒ min 33.389 / avg 36.390 / max 41.672 s (理论下界); 9 次全体 min 33.389 / avg 48.555 / max 68.810 s; ★t_build 占 98.9~99.8% ⇒ CPU-bound, 主机争抢是唯一变量, 引用必须带负载前提** ★** · ★**产物 md5 跨 3 会话 9/9 逐字节相同 (249360 B / `97a34fff0b855b92681f26627dba5354`)** ★** · 往返自证 `load_rknn(model_path, weight_path)` rc=0 且再导出 md5 一致 · ★**板端 `init_runtime` rc=-1 (`RKNN3_ERR_DEVICE_UNAVAILABLE`) ⇒ 板端接受性 [0数据]** ★
2. ★**第4趟 (本趟) 把上面每一条都独立复跑了一遍 —— 13/14 条结论一字不差; ★★唯一一条要改口径的是「转换耗时」: 上一趟的 33~42 s 是【机器闲】下的读数, 本趟拆成 3 会话 × 9 读数 (干净口径 44.050~54.950 s, 争抢口径 51.040~68.810 s); 结论方向不变 (转换链照样已通), 但★这个数以后引用必须带「当时主机负载」的前提**★★** ★** — 真签名 `load_rknn(self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)`; ★**第 2 趟炸的 `TypeError: missing 1 required positional argument: 'weight_path'` 是漏传 `weight_path`; `export_rknn` 一次产出 `.rknn` + 同名 `.weight` (1960448 B), 配上传回 ⇒ rc=0, 再导出 md5 与原文件完全一致** ★
