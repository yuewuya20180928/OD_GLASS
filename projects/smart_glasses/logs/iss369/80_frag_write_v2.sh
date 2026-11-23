#!/usr/bin/env bash
# ★ISS-369 · 第三次会话 (2026-11-24) 的分片写入★★
# ★只走 state/frag_write.py 的原子写·只写自己的分片 state/fragments/hw.yaml★
# ★★不写 --status ⇒ 不覆盖别的单 (当前 status 块属 ISS-376 cont2 等后开的单·不是本单的)★★
set -euo pipefail
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

echo "=== 写前 md5 ==="
md5sum state/fragments/hw.yaml
stat -c '%y %s' state/fragments/hw.yaml

python3 state/frag_write.py --agent hw-lead \
 --add-answer 'key=iss369_libid_reverify_20261124 to=main value="★ISS-369 第三次会话 (2026-11-24 04:0x) 的二次独立复核★ (★背景: 本单 2026-11-23 22:34 已交卷·派活书那句「三件交付物一个都不在盘上」是 20:34 那一刻的快照·cont1 趟已做完⇒ 本次不重做交付物·只做独立复核+补一处真实缺口★). ★独立复核结论 (★全部本机实跑·不采信上一趟自述★): ① v2_indep_board_probe.py 用 pcbnew 直读真板 ⇒ 186 封装 / lib_id 非空 0 / GetFPIDAsString() 唯一值 = "" / 总焊盘 834; ② v2b_write_mechanism.py 复现写盘机制 ⇒ E1 python API 只改 1 行 (187044 行→差异 1 行) · E2 文本层 (footprint Lib:Name) 可用 · E3 (footprint NAME (lib A B)) 与 E4a (footprint NAME (lib_id A:B)) ★LoadBoard 返回 None = 整板报废★ · E4c 裸封装名会把封装名当库名 · E8 库名指向不存在的库板仍能加载; ③ v3_indep_targets_verify.py 自己解析页两张表 + 自己 test -f + 重算 md5 ⇒ 90+96 = 186 与板面逐件相等 (不缺不漏) + 94/94 个 .kicad_mod 在盘且 md5 对得上 + 库根 155 个 .pretty / 15468 个 .kicad_mod; ④ 自己用真闸 state/check_pcb_nets.py 跑沙盒五轮 ⇒ S0~S4 的 C4 全部 = 158 且 S0≡S3 · S1≡S2 ⇒ ★写库名对 C1/C2/C3/C4 的贡献 = 0★. ★★补的一处真实缺口: 页 §5 的 W-2 原写「5 只按键的 2 脚 vs 4 焊盘」, 漏了上游真正要拍的那条「5 只按键 3N vs 1.5N」 (上游 iss364_k3_button_3n_vs_1p5n · 矩阵 §㉞-1 第 10 项·★上游标注「卡·时限型·须在 S10 开工前」★) ⇒ 已改成上游口径两个分支 + 误触代价 + 补 §5 编号对照 (本页 W-1~W-5 vs 上游 K1/K2/K4 vs 矩阵「老板 W-1/W-2」) ⇒ 只登记不代拍. ★边界复查: 板 md5/mtime/size + 网表/脚表/BOM md5 + 9 个既有闸脚本 md5 + 6 个既有页面 md5 全部与 20:11 基线逐行相同 ⇒ 零写板·零落表·零改既有闸·零改既有页面·零挂链." ref="HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md §B5.1.1 §B6-9 · logs/iss369/6x-7x 留证"' \
 --add-need 'key=iss369_button_3n_vs_1p5n_s10_blocker to=main item="★ISS-369 §5 W-2 的上游原始待拍板面第 10 项 `iss364_k3_button_3n_vs_1p5n` (★矩阵 §㉞-1·★标注「卡·时限型·须在 S10 开工前」★) ★本单只登记不代拍★ ⇒ 要 main / 老板拍: 5 只按键 (SW_BOOT/SW_KEY_PWR/SW_KEY_VM/SW_KEY_VP/SW_RST) 走 (a) 保留 3N ⇒ 官方 SW_Push_1P1T_NO_CK_KMR2 4 焊盘 (焊盘号 1,1,2,2) ⇒ 网表与脚表要给这 5 只补 2 个具名脚 (属腿 B 的活·本单零落表) ⇒ C3 绿; 还是走 (b) 改 1.5N ⇒ 换 2 焊盘按键封装 (SW_SPST_B3U-1000P md5 749f20c5ab898069ade01682274c7bbf / SW_SPST_CK_KXT3 md5 bed9b3b110e52e4ffcdc18240ef7a47c·★两者本机实测在盘★) ⇒ C3 绿但按动力度 3N→1.5N ⇒ 误触风险上升 (矩阵 §⑮~⑲ 选 3N 的理由就是防误触). ★★不拍的后果: 走 (a) 而网表没补脚 ⇒ C3 当场红「板 4 脚 / 网表 2 脚」(沙盒实测不符 3 件 = SW_BOOT/SW_KEY_PWR/SW_RST) ⇒ 那一趟交不出可投产的板★★" since=2026-11-24' \
 --add-claim 'key=iss369_libid_w2_button_force_gap_fixed value=fixed note="★ISS-369 页 §5 W-2 的口径缺口已补 (2026-11-24 03 补)★ ⇒ 原写「2 脚 vs 4 焊盘」漏了上游真正待拍项「5 只按键 3N vs 1.5N」 ⇒ 已按上游 iss364_k3_button_3n_vs_1p5n 改成 (a) 保留 3N (网表/脚表补 2 个具名脚·腿 B 的活) / (b) 改 1.5N (换 2 焊盘件 + 误触代价) 两个分支·只登记不代拍; 并加 §5 编号对照防止 main 把本页 W-1~W-5 与上游 K1/K2/K4 或矩阵「老板 W-1/W-2」读混. ★只改本单自己的两页 (作业包页 + 交卷页)·既有页一个字节未动★" ref="HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md §5"'

echo "=== 写后 md5 ==="
md5sum state/fragments/hw.yaml
stat -c '%y %s' state/fragments/hw.yaml
