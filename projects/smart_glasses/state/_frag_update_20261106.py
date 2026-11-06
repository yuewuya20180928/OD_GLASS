#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-06 周更新 · sw-lead 分片写入 (★唯一合法入口 = state/frag_write.py)
=====================================================================
★纪律:
  - 只走 `python3 state/frag_write.py --agent sw-lead ...`
  - ★禁止 open(path,"w") 直写分片 (并发下合并器读到半截 ⇒ 整个域从快照里静默消失)
  - --add-need 不支持 due/waiting_on 字段 ⇒ needs_from 整段用 --set-json 写
    (先读现状 → 追加 → 整段回写, 不丢旧条目)
"""
import json
import os
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FW = os.path.join(PROJ, "state", "frag_write.py")
FRAG = os.path.join(PROJ, "state", "fragments", "sw.yaml")


def run(args, label):
    cmd = [sys.executable, FW, "--agent", "sw-lead"] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJ)
    tail = (r.stdout or "").strip().splitlines()
    print("[%s] rc=%d %s" % (label, r.returncode, tail[-1] if tail else (r.stderr or "").strip()[:300]))
    if r.returncode != 0:
        print("   STDERR:", (r.stderr or "")[:500])
    return r.returncode


SUMMARY = (
    "11-06 周更新: 交三件可判定产出 + 四个硬指标复测。①ISS-145: 新交 SW/DEMO_OD_TIMING_SPEC.md "
    "(端到端时序口径规格: 口径A 起点=曝光积分开始/终点=光机出光, 显式分 A-soft(plane commit 返回, 软件能打) 与 "
    "A-hard(含面板内部延迟 S10, 软件打不到, [0数据]) 两层防偷换终点; 11 段接力表写死 '谁(P/T/K/H)在什么时刻做什么'+"
    "取哪个时间戳+含/不含什么; 时钟基准统一 CLOCK_MONOTONIC 并显式禁用 CLOCK_REALTIME; 9 打点取自 ARS45_INT8_CHAIN §4 "
    "一字不改名; 曝光时长与队列等待各自单列; CSV 表头 14 列一行不换行) + 自检器 SW/tools/demo_timing_check.py "
    "(selftest 4/4 rc=0 含 3 条反例, 对规格文档 20/20 rc=0; ★自检当场抓到并修掉我自己两个真缺陷: CSV 表头被换行 + "
    "反例变异是子串空操作)。②ISS-147/ISS-155: 新交 SW/RK3572_TARGET_BOARD_VERIFY.md (板端验证步骤 + 可执行判定口径: "
    "P1~P6 前置 + 步骤 0~5 + 判据 N1~N5 五条[能加载/精度不塌 F1>=0.2427/NPU 耗时对得上 <=13.30ms 推算阈值且 "
    ">20.33ms 命中老板 T2 翻案/两个数都报/散热已记] + 三种结局各自出路; 判定线在板子到手前定死不许事后调)。"
    "★本周实测: rk3572 在 rknn-toolkit2 2.3.2 上仍抛 ValueError: Invalid target_platform 'rk3572'! (两个 conda env "
    "各复现一次, rk3576/rk3588 rc=0) ⇒ '升级 toolkit 就有 rk3572' 这条路彻底不存在; PC 侧转换链复跑 rc=0 "
    "(yolov5n@640: load 0.18s + build(INT8) 38.2s, 产物 4,989,367B=4.76MiB, w8a8/channel/rk3576); acc 步 281 张 "
    "COCO val2017 ⇒ TP=494 FP=765 FN=1623 ⇒ P=0.3924 R=0.2333 F1=0.2927, 与 11-02 基线逐位一致 (缓存键含指纹修复有效)。"
    "★板端实测仍 0 次: 板子 192.168.2.5 ping 100% 丢包 + ARP INCOMPLETE, 本机无 sshpass ⇒ 已升级为需要老板/硬件侧解锁的卡点 "
    "(推荐用 ISS-151 清单里的 Forlinx OK3572-C, 一举两得=验证载体+demo Step1 载体; ★N1 是跨平台命题, 用 RK3576 板测不构成证据)。"
    "③ISS-087/ISS-101: 量产可用模型清单当前状态=空(0 条), 成因与补齐路径见 SW/MODEL_RELEASE_LIST.md。★本周实测 "
    "model_asset_check: 资产 13 条 / FAIL 12 / WARN 12 / 交付集 2 条 / licensing-hold 2 / quarantined 4 / 放行阻断项 L=0 "
    "(★L=0 不等于有可用模型)。★★本周抓到 3 个真缺陷: (a) 唯一许可干净候选 (Apache-2.0 SSD-MBv2-FPNLite head 子图) 用 "
    "rknn-toolkit2 2.3.2 实跑 config rc=0 + load_onnx rc=0 ⇒ '它转不了'这个前提被证伪 (ISS-101 是 10-27 登记的, 那时基线还是 "
    "ARS45 非 Rockchip ⇒ 用错了工具链); ★但 build 阶段被 'Not Support Dtype: 2' 拒收 ⇒ 根因实测定位 = 该子图 graph input 的 "
    "elem_type=2 (float64) ⇒ 改成 float32 后 build rc=0, 产物 9,513,373B=9.07MiB, sha16 cc8f51113e559544 ⇒ "
    "'许可干净'与'NPU 可用'两个条件本周第一次出现交集, 空清单成因从'互斥'降级为'各自还差最后一步'; (b) ★★校准集 "
    "~/Public/radxa_yolo/calib_yolov5_100 有 1 个 0 字节空文件 (000000010583.jpg) ⇒ 实跑只吃 99 张而非 100 张, 静默掉样本不报错; "
    "(c) 台账 C2/C3 与实物不符 (重建 yolov5s ONNX sha16=1e2c716bd16ed9d3 vs 台账 20368be665f6f59a) ⇒ 按'版本只认 sha256'纪律须登记新资产 ID。"
    "★另发现 Apache-2.0 候选的输入布局是 (1,320,3,320) 而非常规 NHWC (1,320,320,3) ⇒ 板端喂数必须按此布局, 已写进文档。"
    "★ISS-080 S2 救砖: PC 侧先验本周复跑全绿 (s2_iss123_verify 15/15 rc=0 · s2_selftest 10/10 rc=0 · judge 13/13 rc=0 · "
    "e2e 14/14 rc=0 · run --selftest rc=0) 但★板端实测 0 次, 量产一票否决项未解除, P1~P4 四个 [0数据] 仍未填 ⇒ 已写成 "
    "why-not-closable + 新 due。"
)

# ── ① 状态 ──
run(["--status",
     'phase=P2(方案设计) progress_pct=78 health=yellow summary="%s"' % SUMMARY],
    "status")

# ── ② answers (回答别人给的 key) ──
run(["--add-answer",
     'key=iss148_rk3572_gpio0_vccio_domain_check to=hw-lead '
     'value="RK3572 datasheet p.39 Table 3-1/3-2 实测(渲染图非扁平文本): VCCIO1_VCC 属 1.8V/3.3V 组(PMUIO1+VCCIO1~6, '
     'abs-max 3.63V, 推荐 2.7/3.3/3.6V); 1.8V-only 组只有 PMUIO0_VCC1V8+VCCIO0_VCC1V8(max 1.98V); VCCIO7_VCC 单列 '
     '1.2/1.8V(max 1.98V) => 原「VCCIO1 属 1.8V only, GPIO0 只允许 1.98V, 整条 I2C_A 电平域要重设计「是 pdftotext 多行单元格错位造成的"
     '排版假象, 结论作废; 但 datasheet 无 GPIO bank->VCCIO 对照表, GPIO0_B0/B1 具体挂哪个 VCCIO 组仍[0数据], 需 SoM(FET3572-C) '
     'IO 域文档或 BSP dtsi 佐证 => 本条从「数据全无「降级为「只剩 bank->VCCIO 映射这一个问题「" '
     'ref="HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §5 + HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png"'],
    "answer:hw-lead")

run(["--add-answer",
     'key=demo_od_p0_1_rk3572_target to=main '
     'value="CLOSED (2026-11-06 复验): rknn-toolkit2 2.3.2 config(target_platform=rk3572) 仍抛 ValueError: Invalid '
     'target_platform rk3572!, 同进程 rk3576/rk3588 rc=0, 两个 conda env 各复现一次 => rk3572 不是任何已发布版 toolkit2 的合法 '
     'target, 不存在升级就能支持的路径; 唯一可行 = target_platform=rk3576 转换 + 板端 RK3572 BSP runtime 加载; PC 侧本周复跑 rc=0 '
     '(yolov5n@640 -> 4.76MiB, build 38.2s) 且 F1=0.2927 与 11-02 基线逐位一致; 剩下的「rk3576 产物能否在 RK3572 上跑通「是板端实测 = '
     '[0数据] (板子 192.168.2.5 不可达), 已交 SW/RK3572_TARGET_BOARD_VERIFY.md 的步骤+判据 N1~N5" '
     'ref="SW/RK3572_TARGET_BOARD_VERIFY.md §0/§2/§4 + SW/RKNN_BUILD_ENV_RECOVERY.md §2"'],
    "answer:main/p0-1")

run(["--add-answer",
     'key=demo_od_p0_3_build_env to=main '
     'value="CLOSED (2026-11-06 复跑 rc=0): conda env ~/miniconda3/envs/rknn (python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / '
     'numpy 1.26.4 / protobuf 4.25.4 / torch 2.4.0+cpu) 仍可用, 与 rknn_bench.py 硬编码路径一致, 仓库脚本零改动可跑; 转换链四步全 rc=0: '
     'config / load_onnx / build(INT8 38.2s) / export_rknn; 源 ONNX 重建件在 ~/Public/rknn_assets/{yolov5n,yolov5s}-sim.onnx '
     '(245 节点, 3 路 head 输出名 350/498/646); 校准集 /tmp/rknn_bench/dataset.txt 99 张自动补跑生成; ★唯一遗留缺陷: 校准集源目录有 1 个 '
     '0 字节空文件(000000010583.jpg) 致实跑只吃 99 张, 已登记待补" '
     'ref="SW/RKNN_BUILD_ENV_RECOVERY.md §1 + SW/RK3572_TARGET_BOARD_VERIFY.md §2"'],
    "answer:main/p0-3")

run(["--add-answer",
     'key=model_license_yolov5sim to=main '
     'value="★更新 (2026-11-06): yolov5s/yolov5n-sim 系许可判定维持 AGPL-3.0 (7 环物证, SW/MODEL_LICENSE.md §1.2); 台账侧 2 条置 '
     'licensing-hold 禁入交付物 (model_asset_check 实跑: licensing-hold 2 条 = MOD-YOLOV5S-640-ARS45-SRC + '
     'MOD-YOLOV8S-COCO80-ONNX, 放行阻断项 L=0); ★但「唯一许可干净候选转不了「这个前提本周被证伪: Apache-2.0 的 '
     'SSD-MBv2-FPNLite head 子图用 rknn-toolkit2 2.3.2 实跑 config rc=0 + load_onnx rc=0 => 它能进 RKNN 工具链, 卡点在 build(量化) 与板端; '
     '★build 的真阻塞也已定位并修掉: 该子图 graph input 的 elem_type=2(float64) 被 RKNN 量化器拒收 (Not Support Dtype: 2), 改成 float32 '
     '后 build rc=0 产物 9.07MiB; 采购决策仍待 boss (SW-MODEL-B2-ISS101-RU1 未回)" '
     'ref="SW/MODEL_RELEASE_LIST.md §2/§3 + SW/MODEL_LICENSE.md §1.2"'],
    "answer:main/license")

# ── ③ interface_claims (规范短值) ──
run(["--add-claim",
     'key=od_e2e_timing_caliber '
     'value="A=曝光积分开始->光机出光; 分 A-soft(plane commit 返回, 软件可打)/A-hard(+面板内部延迟 S10, [0数据]); '
     '时钟=CLOCK_MONOTONIC; 9打点取自 ARS45_INT8_CHAIN §4; 单帧不算数(n>=300)" '
     'note="ISS-145 11-06 SW/DEMO_OD_TIMING_SPEC.md §1/§2/§3.4"'],
    "claim:od_e2e_timing_caliber")

run(["--add-claim",
     'key=rknn_target_platform_supported '
     'value="rk3572=非法(ValueError); rk3576=合法; rk3588=合法" '
     'note="ISS-147/ISS-155 11-06 实测 rknn-toolkit2 2.3.2, 两个 conda env 复现"'],
    "claim:rknn_target_platform")

run(["--add-claim",
     'key=prod_ready_model_count value="0" '
     'note="ISS-087/101 11-06 实测 model_asset_check: 资产13/交付集2/L=0 但量产可用清单为空 (许可干净候选 PC 侧已通, 未过板端)"'],
    "claim:prod_ready_model_count")

run(["--add-claim",
     'key=calib_dataset_count value="99" '
     'note="★11-06 实测: 源目录 100 张里有 1 个 0 字节空文件(000000010583.jpg) => 实跑只吃 99 张, 静默掉样本, 待补"'],
    "claim:calib_dataset_count")

run(["--add-claim",
     'key=s2_board_test_pass_count value="0" '
     'note="★ISS-080/120 11-06: 板端实测 0 次 (板子 192.168.2.5 不可达); PC 侧先验 15/15+10/10+13/13+14/14 全 rc=0 但不代表板端通过"'],
    "claim:s2_board_test_pass")

run(["--add-claim",
     'key=rknn_ssd_apache2_input_layout value="(1,320,3,320)" '
     'note="★11-06 实测: Apache-2.0 候选的 RKNN 输入布局是 (1,320,3,320), 喂常规 NHWC (1,320,320,3) 会报 shape wrong"'],
    "claim:apache_input_layout")

# ── ⑤ artifacts ──
run(["--add-artifact",
     'path=SW/DEMO_OD_TIMING_SPEC.md kind=文档 version=v1.0 '
     'summary="★ISS-145 新增: demo 端到端时序口径规格 v1.0 (口径A 起点=曝光积分开始/终点=光机出光, 显式分 A-soft/A-hard 两层防偷换终点; '
     '11 段接力表写死 谁(P/T/K/H)在什么时刻做什么+取哪个时间戳+含/不含什么; CLOCK_MONOTONIC 统一时钟+禁 REALTIME; 9 打点取自 '
     'ARS45_INT8_CHAIN §4; 曝光时长与队列等待各自单列; CSV 表头 14 列一行不换行; 验收判据 9 条; demo 阶段 60ms 不设门限) — 板端时延数字一律 [0数据]"'],
    "artifact:timing_spec")

run(["--add-artifact",
     'path=SW/tools/demo_timing_check.py kind=代码 version=v1.0 '
     'summary="★ISS-145 新增: 时序规格自检器 (机械核对 20 项: 打点名齐全/汇总项/时钟基准/报数字段/采样帧数/CSV 表头 14 列/口径A 两层/'
     'S10 [0数据]/曝光单列/A733 铁律三数/11 段/t0..t9/60ms 不设门限/t_compose 关键未知数/判据 9 条/与上游 §4 一致/未编造板端数字) + '
     '--selftest 4/4 rc=0 含 3 条反例 (缺打点名/错时钟/编 S10 必被抓到)"'],
    "artifact:timing_check")

run(["--add-artifact",
     'path=SW/RK3572_TARGET_BOARD_VERIFY.md kind=文档 version=v1.0 '
     'summary="★ISS-147/ISS-155 新增: rk3576-target .rknn 在 RK3572 上的板端验证步骤 + 可执行判定口径 v1.0 (前置 P1~P6; 步骤 0~5 含环境/散热取证 '
     '与产物 sha256 搬运不许板端重转; 判据 N1~N5: 能加载/F1>=0.2427 不塌/纯NPU<=13.30ms 推算阈值且 >20.33ms 命中 T2 翻案/两个数都报/散热已记; '
     '三种结局各自出路; 判定线在板子到手前定死; ★板端结果 = [0数据], 本单只交步骤不交结论)"'],
    "artifact:rk3572_target_verify")

run(["--add-artifact",
     'path=SW/MODEL_RELEASE_LIST.md kind=文档 version=v1.0 '
     'summary="★ISS-087/ISS-101 新增: 量产可用模型清单的当前状态(条数=0)+空清单成因(4 条, 含本周证伪的旧成因)+补齐路径(3 条带判定口径与时限); '
     '附 13 条资产逐条状态与本周实测 (model_asset_check: 资产13/FAIL12/WARN12/交付集2/licensing-hold2/quarantined4/L=0) + '
     'Apache-2.0 候选 rknn-toolkit2 实跑 config rc=0/load_onnx rc=0/build rc=0 (float64 输入根因已定位并修掉) + 校准集 1 个空文件缺陷"'],
    "artifact:model_release_list")

# ── ④ needs_from: 整段写 (--add-need 不支持 due/waiting_on) ──
import yaml  # noqa: E402
with open(FRAG, encoding="utf-8") as f:
    frag = yaml.safe_load(f)
needs = list(frag.get("needs_from") or [])
before = len(needs)
existing = {n.get("key") for n in needs}

NEW_NEEDS = [
    {
        "key": "rk3572_board_for_target_verify",
        "to": "main",
        "item": ("★ISS-155 头号卡点解锁: 需一块能启动的 RK3572 板/模组 (推荐 ISS-151 清单里的 Forlinx OK3572-C, "
                 "一举两得: 既是本条验证载体又是 demo Step1 载体) + 板端 RKNN runtime 版本号 (librknnrt.so) + 可达入口"
                 "(本机无 sshpass); PC 侧已全做完 (转换 rc=0 / 4.76MiB / F1 0.2927), 板子到手后一条命令+5 条判定即结案; "
                 "★N1 是「rk3576 产物能否在 RK3572 上加载「的跨平台命题, 用 RK3576 板测不构成证据"),
        "since": "2026-11-06",
        "due": "2026-11-13",
        "waiting_on": "agent",
    },
    {
        "key": "model_release_gate_boss_decision",
        "to": "main",
        "item": ("★ISS-101/ISS-087 仍等 boss 拍板 (外发一律经你): (a) 采购 Ultralytics Enterprise License 还是走 Apache-2.0 栈; "
                 "★本周新信息: Apache-2.0 候选 (SSD-MBv2-FPNLite head) 用 rknn-toolkit2 2.3.2 实跑 config rc=0 + load_onnx rc=0, "
                 "且其 float64 输入根因已定位并修掉 (build rc=0, 产物 9.07MiB) ⇒ 「唯一许可干净候选转不了「的前提已被证伪, "
                 "路径2 (换 Apache-2.0 栈) 的工程可行性显著上升; (b) 是否同意继续用本机 RKNN 工具链跑完该候选的 PC 侧精度基线与板端验证 "
                 "(R-U6 同类请求, 不占板子)"),
        "since": "2026-11-06",
        "due": "2026-11-13",
        "waiting_on": "boss",
    },
    {
        "key": "visionox_panel_init_code_gate",
        "to": "main",
        "item": ("★ISS-145/ISS-179 的显示侧硬前置仍未解锁: 视涯 0.49「 1920x1080 面板 init code + 时序 + DSC 需求 + 单色/全彩, "
                 "问询草稿 state/outbox/visionox_display_inquiry.md 未发; ★老板 11-02 定: 不发邮件给厂家, 走「先查开源/现货, "
                 "查不到才放弃该物料换友商「 ⇒ 请转 hw-lead 做公开渠道检索 (ISS-148 同款打法); 不解决则 demo 阶段2 (屏上出图) 无法验收, "
                 "我这边端到端时序规格只能停在 A-soft"),
        "since": "2026-11-06",
        "due": "2026-11-13",
        "waiting_on": "agent",
    },
    {
        "key": "calib_dataset_empty_file_fix",
        "to": "main",
        "item": ("★ISS-147 侧小缺陷 (我自己能补但要占时间): 校准集源目录 ~/Public/radxa_yolo/calib_yolov5_100 有 1 个 0 字节空文件 "
                 "(000000010583.jpg) ⇒ rknn_bench 实跑只吃 99 张而非 100 张 (静默掉样本, 不报错); 已用 COCO val2017 重生成 100 张 "
                 "320x320 校准集到 /tmp/apache_calib320/ 供 Apache-2.0 候选 build 用; 请项目总工决定是补回原文件还是把台账口径改成「99 张「"),
        "since": "2026-11-06",
        "due": "2026-11-13",
        "waiting_on": "agent",
    },
]
added = 0
for n in NEW_NEEDS:
    if n["key"] in existing:
        print("skip (已存在):", n["key"])
        continue
    needs.append(n)
    added += 1
print("needs_from: %d -> %d (新增 %d)" % (before, len(needs), added))
tmp_json = "/tmp/_sw_needs_20261106.json"
with open(tmp_json, "w", encoding="utf-8") as f:
    json.dump(needs, f, ensure_ascii=False, indent=1)
run(["--set-json", tmp_json, "--set-field", "needs_from"], "set:needs_from")
print("done")
