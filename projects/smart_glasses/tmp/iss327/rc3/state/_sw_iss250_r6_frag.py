#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-250 第6轮 · sw-lead 分片落盘 (★走 state/frag_write.py CLI 原子写★)"""
import subprocess
import sys
import os

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FRAG = os.path.join(ROOT, "state/frag_write.py")

CLAIMS = [
    ("iss250_r6_board_reachability",
     "★[实测] 板端可达性实测 (2026-11-17 05:3x~05:4x, sw-lead): 本机此刻【没有任何可执行板端验真的通道】⇒ 板端接受性仍 [0数据]★ —— 证据: ① ip link show enp4s0 ⇒ 'Device does not exist' (TOOLS.md 记录 A7S 板挂的就是这条有线 LAN) ② 192.168.2.0/24 与 192.168.71.0/24 两网段全段 TCP 22/5555 扫描 ⇒ 只开出本机自己 (.2.3 / .71.4) + 网关, 无任何第三方主机 ③ getent hosts radxa-cubie-a7s.local ⇒ rc=2 无解析 ④ adb 未安装, lsusb 只有 BT + RTL8152 网卡。★⇒ 「板不可达」从断言变成【实测 + 根因】: 板端 N1 的客观前置分三类 = ① 板没做出来 (PCB 布线中) ② 板没接网/没通电 (物理动作, 零采购) ③ 板端 runtime 没装 (★完全在自己手里, clone 官方公开仓库即可★) ⇒ ③ 不许再被写成阻塞项★",
     "logs/iss250_r6/board_reach_probe.log (命令 + 输出原文) · ★零外发·未碰 HW/MECH★"),
    ("iss250_r6_sim_accuracy_two_chains",
     "★[实测·模拟器口径] 板不可达时「精度掉点」今天就有数了: 两套 toolkit 都自带 NPU 模拟器 (init_runtime(target=None); 源码实读 envs/rknn/.../rknn/api/rknn.py:283 与 envs/rknn3/.../rknn/api/rknn.py:424, docstring 原文 'default is None, means simulator')★ ⇒ n=30 张同图同预处理实测 (vs FP32 onnxruntime 参考): rknn3-1.2.0/target=rk3572 逐 head 余弦 0.999511/0.999603/0.999671 (min 0.999040/0.999243/0.999269), rel-L2 0.031296/0.028152/0.025289, 检测级 (top-100, conf 0.75) 匹配 48.67/59.77, 平均 IoU 0.756215; 对照 toolkit2-2.3.2/target=rk3576 余弦 0.999524/0.999628/0.999697, rel-L2 0.030780/0.027073/0.023915, IoU 0.772955 ⇒ ★★两条路线的量化掉点基本一致 (逐 head 余弦差 <0.0001) ⇒ 「rknn3/rk3572 的量化质量不劣于 toolkit2/rk3576」有了板端之外的第一个数★★ ★★口径警告: 模拟器 ≠ 板端 NPU (rknn3 的 simulate_lut=True 更接近但不等价, 该档 build 本轮未跑完 ⇒ [0数据]), 板端 N1/N2 才是终判; 模拟器耗时 271.96/317.39 ms 每张是 CPU 耗时, 不可当板端耗时★",
     "logs/iss250_r6/sim_accuracy.json + sim_accuracy_*.log · 脚本 SW/tools/iss250_r6_sim_accuracy.py (4 步分进程: 两套 toolkit 的 import 名都叫 rknn, 同进程会互相覆盖)"),
    ("iss250_r6_rknn3_runtime_public_source",
     "★[官网] 路线② 的板端 runtime = 官方【公开仓库】⇒ 零采购零外发 ⇒ 这一格不是阻塞项★: 官方 README 首段 'RKNN3 Runtime: On-board runtime library providing C/C++ programming interfaces' ⇒ 路径 github.com/airockchip/rknn3-toolkit/tree/main/rknn3-runtime (★就在同一个公开仓库里★); 同仓另有 rknn3-toolkit-lite (板端 Python 接口) 与 rkllm3-server; GitHub 搜 org:airockchip+rknn3 ⇒ total_count=2 ⇒ ★⇒ clone + ./build-linux.sh -t rk3572 -a aarch64 就能出 librknn3_api.so + librknn3_api_native.so (RK3572 走 native 库, 不是 rkcp)★ ⇒ 不需要向任何外部方要东西, 不许写成 needs_from",
     "raw.githubusercontent.com/airockchip/rknn3-toolkit/main/README.md (抓 2026-11-17 05:23 GMT+8) + api.github.com/search/repositories?q=org:airockchip+rknn3"),
    ("iss250_r6_simulator_constraint",
     "★[实测] 模拟器有一条硬约束 (踩到才知道): 两套 toolkit 都拒绝把 load_rknn 载入的模型跑模拟器 —— 原文 'RKNN model that loaded by load_rknn not support inference on the simulator, please set target first! If you really want to inference on the simulator, use load_xxx & build instead of load_rknn!' ⇒ 想拿模拟器掉点必须同会话 load_onnx → build → init_runtime(target=None) (本轮 build 48.579 s (rknn3/rk3572) / 34.780 s (toolkit2/rk3576), 与 ISS-263 的 33.231/34.035/41.595 s 同量级 ⇒ 复现一致) ⇒ ★别再试「拿盘上归档的 .rknn 直接跑模拟器」★",
     "logs/iss250_r6/sim_accuracy_*.log · SW/tools/iss250_r6_sim_accuracy.py"),
]

ARTIFACTS = [
    ("SW/research/ISS250_r6_复核记录.md", "research",
     "ISS-250 第6轮 12 行查证记录 (R6-01~R6-12): 板端可达性实测 / 官方 release 复查 / 模拟器掉点 / 模拟器硬约束 / runtime 公开来源 / 降级方案代价底座 / 板端清单 P0~P5 / 缺口 G-1~G-5"),
    ("SW/tools/iss250_r6_sim_accuracy.py", "tool",
     "掉点实测脚本 (4 步分进程 ref/sim_build×2/cmp) —— 两套 toolkit 的 import 名都叫 rknn 故不能同进程; 实测 build 48.579 s / 34.780 s; 输出逐 head 余弦 + rel-L2 + 检测级 conf 0.25/0.5/0.75"),
    ("HANDOFF/2026-11-17_sw-lead_ISS250_第6轮_板可达性实测与模拟器掉点.md", "handoff",
     "第6轮交卷单 (B1~B6 齐全): 三条新增事实 + 12 行查证 + 板端清单 P0~P5 + 缺口 G-1~G-5; ★板端接受性仍 [0数据], 未替老板拍板★"),
]

ANSWER = ("iss250_r6_supplement",
          "★ISS-250 第6轮 (sw-lead, 2026-11-17 05:2x~06:0x) 三条新增事实, 请 main 复验时一并看★: ① 【板端可达性实测】= 不通且根因定位 (本机无 enp4s0 网卡 + 两网段全段 TCP 扫无第三方主机 + mDNS 无解析 + 无 adb/USB) ⇒ 板端 N1 仍 [0数据], 但它的前置只有两类需要别人 (① 板没做出来 ② 板没接网通电), 而板端 runtime 自己就能装 (官方公开仓库) ⇒ 这一格不许再挂成「等外部回复」② 【板不可达时「精度掉点」今天就有数】: 两套 toolkit 自带 NPU 模拟器 (init_runtime(target=None)), 实测两条路线量化掉点基本一致 (逐 head 余弦差 <0.0001, 检测级 IoU 0.756 vs 0.773) ⇒ 「rknn3/rk3572 的量化质量不劣于 toolkit2/rk3576」有了板端之外的第一个数 (★模拟器口径, 非板端真值★) ③ 【板端 runtime 官方公开仓库】⇒ 零采购零外发。★★本轮刻意没把 12 行查证追加进共享查证表 (并行会话正在写同一文件, 追加会互相覆盖) ⇒ 落在 SW/research/ISS250_r6_复核记录.md (R6-01~R6-12), 要并表请 main 或下一轮唯一写会话做★",
          "HANDOFF/2026-11-17_sw-lead_ISS250_第6轮_板可达性实测与模拟器掉点.md · SW/research/ISS250_r6_复核记录.md · logs/iss250_r6/")

STATUS = ("delivered", "100", "绿",
          "★ISS-250 第5轮 (独立复核侧) + 第6轮 (板可达性实测 + 模拟器掉点) 交卷 (2026-11-17 05:2x~06:0x, sw-lead) ★ 第6轮三条新事实: ① 板端可达性实测 = 不通且根因定位 (无 enp4s0 + 两网段全段扫无第三方主机 + mDNS 无解析 + 无 adb/USB) ⇒ 板端接受性仍 [0数据], 其前置只有「板没做出来」「板没接网通电」两类需要别人, 板端 runtime 自己就能装 (官方公开仓库) ⇒ 不许挂等外部回复 ② 板不可达时「精度掉点」今天就有数: 两套 toolkit 自带 NPU 模拟器, 实测两路线量化掉点基本一致 (逐 head 余弦差 <0.0001) ⇒ 路线② 量化质量不劣于路线① (★模拟器口径, 非板端真值★) ③ 板端 runtime 官方公开仓库 ⇒ 零采购。★ 边界: 零外发 · 未碰 HW/ 与 MECH/ · 未改 PROJECT_TRACKER §0 · 未自签 issue_log · 未替老板拍板 (rk3572 vs rk3576 仍是老板级) · 本轮未追加共享查证表 (避免与并行会话互相覆盖, 12 行落在 SW/research/ISS250_r6_复核记录.md)★")


def main():
    args = [sys.executable, FRAG, "--agent", "sw-lead"]
    for k, v, note in CLAIMS:
        args += ["--add-claim", 'key=%s value="%s" note="%s"' % (k, v, note)]
    for path, kind, summary in ARTIFACTS:
        args += ["--add-artifact", 'path=%s kind=%s summary="%s"' % (path, kind, summary)]
    key, value, ref = ANSWER
    args += ["--add-answer", 'key=%s to=main value="%s" ref="%s"' % (key, value, ref)]
    phase, pct, health, summary = STATUS
    args += ["--status", 'phase=%s progress_pct=%s health=%s summary="%s"' % (phase, pct, health, summary)]
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout[-3000:])
    if r.returncode != 0:
        print("STDERR:", r.stderr[-3000:])
        sys.exit(r.returncode)
    print("FRAG WRITE rc=0")


if __name__ == "__main__":
    main()
