#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/_iss131_frag_write.py · main 自办 ISS-131 的分片登记 (★走 frag_write.py 原子写·零外发★)"""
import subprocess
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANSWER = (
    "key=iss131_rk3572_caliber_selfchecked to=main value=\""
    "ISS-131 已按老板 2026-11-12 02:02「不再发信·全靠自己查资料」口径自办完 ★零写板·零落表·零外发★ "
    "⇒ ★【球位号 11/11 与官方 datasheet 逐条对上】(★含 A22/B22/A23/B23 四条「同球双名」·官方 L1789 逐字 ⇒ 一个 4-lane 口可配 2×2 的物理证据★) "
    "★【CSI】官方 §1.2.7 逐字 Support 2 MIPI CSI-2 interfaces · Two 4 data lanes of D-PHY v1.2 · Each interface may be configured as 2x2 data lanes port "
    "⇒ ★我方网表只用 CSI_D0 一路 4 lane ⇒ 「2 接口 vs 4 口」对我方板无约束★ "
    "★【ISP 12M】官方 §1.2.8 逐字 One channel ISP,12M pixels · Maximum input:4096x3072 ⇒ 4096×3072=12.58 Mpixel ⇒ 「12M」是【单帧分辨率上限】不是 MP/s "
    "⇒ ★我方 1080p60 在分辨率维度不卡[官方] ★ "
    "★【ISP MP/s = [0数据]】datasheet 全文检索不到 ⇒ ★换芯到 RK3572 后这条缺口没变好也没变坏 ⇒ 降级方案: ①官方 TRM (本机无·需联网·标[官网]) "
    "②板端实测 (ISS-210 已把 60ms 判据链+ISP 段打点备好) ③在此之前任何 MP/s 数字只能标[推算]并写清推算链★\" "
    "ref=\"HW/RK3572_INQUIRY_CALIBER_V2.md + state/_iss131_crosscheck_rk3572_caliber.py (★rc=0★)\""
)

ART1 = (
    "path=HW/RK3572_INQUIRY_CALIBER_V2.md summary=\"ISS-131 · RK3572 口径版 R-GEO 问询 · 自查版(不发信) · 6,007 B · "
    "★球位号 11/11 + CSI 口径 + ISP 12M + MP/s [0数据] + One channel ISP⇒只能 1 路(★唯一带推算成分的硬约束·待复验★)★\" kind=doc version=v2"
)

ART2 = (
    "path=state/_iss131_crosscheck_rk3572_caliber.py summary=\"ISS-131 机器可复核交叉核对脚本 · rc=0 · ★只读·零写板·零落表★ · "
    "读网表 + FET3572C_PIN_TABLE + 官方 datasheet txt 三方对拍\" kind=script version=v1"
)

NEED = (
    "key=iss131_mp_s_throughput_still_zero_data to=main item=\""
    "★ISS-131 遗留: RK3572 ISP 的 MP/s 吞吐上限仍是 [0数据] ⇒ 降级方案两条: ①官方 TRM (本机只留 datasheet V1.1·无 TRM·需联网查·标[官网]) "
    "②板端实测 (ISS-210 已把 60ms 判据链+ISP 段打点备好) ⇒ ★在拿到其中之一前·任何 MP/s 数字只能标[推算]并写清推算链·不许拿经验值冒充实测★\" "
    "since=2026-11-18"
)

cmd = [
    "python3", "state/frag_write.py", "--agent", "main",
    "--add-answer", ANSWER,
    "--add-artifact", ART1,
    "--add-artifact", ART2,
    "--add-need", NEED,
]
r = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True)
print(r.stdout[-3000:])
print(r.stderr[-2000:])
print("rc=", r.returncode)
