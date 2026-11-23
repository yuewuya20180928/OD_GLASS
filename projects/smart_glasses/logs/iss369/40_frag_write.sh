#!/usr/bin/env bash
# ISS-369 · 分片写入 (★只走 state/frag_write.py 的原子写·只写自己的分片 state/fragments/hw.yaml★)
# 写前/写后 md5 由交卷页 §B5 贴原样输出
set -euo pipefail
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

echo "=== 写前 md5 ==="
md5sum state/fragments/hw.yaml
stat -c '%y %s' state/fragments/hw.yaml

python3 state/frag_write.py --agent hw-lead \
 --add-artifact 'path=HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md kind=workpacket version=1.0 updated_at=2026-11-23 summary="★ISS-369 板面 186 封装库封装名写盘作业包 (新建·纯新增·不覆写任何既有页)★ §0 18 行口径与读数 (每个数字写清哪个脚本产出·怎么复跑) + §1 板面现状 (库名 0/186 非空·自绘占位 183 / 已落 land 3·§1.3 逐个实测 186 行) + §2 写盘机制 (本机 KiCad 10.0.8 实测 E1~E9·只认 (footprint Lib:Name) 一行) + §3 目标清单 (§3.1 90 件 12 字段 + §3.2 96 件逐件写/不写 + §3.3 件数对账) + §4 写库名不改语义 (沙盒五轮 C4 恒 158) + §5 未决项 5 条 + §6 复跑命令与边界 + §7 回滚说明"' \
 --add-artifact 'path=HW/check_fp_libid_truth.py kind=gate version=1.0 updated_at=2026-11-23 summary="★ISS-369 新建机器闸 (零挂链·不在 state/gate_check.py 里)★ 计划模式 L0~L8 (L1 件数脚本实算 / L4 逐个 test -f 验 .kicad_mod 在盘 + md5 / L5 几何与容差 pos 0.05 size 0.05 cen 0.10 fab 0.35 mm / L6 证据五级白名单 / L7 零挂起措辞 / L8 沙盒五轮 C4 恒 158 ⇒ 写库名对 C4 贡献 0) + 板面模式 B0~B5 (逐封装 lib_id 非空 / 库件在盘 / 焊盘数一致 / 几何容差 / 不该写的 92 件仍为空) + --selftest 11/11 全过"' \
 --add-artifact 'path=HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md kind=handoff version=1.0 updated_at=2026-11-23 summary="★ISS-369 交卷页 (B1~B6 六块齐全 + 验收线 20 条逐条判定 + 落盘清单 + 沙盒留证路径 + 回滚说明)★"' \
 --add-artifact 'path=logs/iss369/ kind=evidence version=1.0 updated_at=2026-11-23 summary="★ISS-369 留证目录★ 基线 md5 (00_) + 沙盒五轮 C1~C4 读数 (10_/11_/12_) + 94 个目标库件逐个 test -f + md5 复核 (20_) + 全库 15468 件逐焊盘几何等价穷举含 NPTH (21_) + 作业包生成器实算快照 (22_) + 闸复跑输出 (4x_) + 全套实算脚本 (scripts/)"' \
 --add-answer 'key=iss369_libid_write_pack to=main value="★ISS-369 交卷★ 板面 186 个封装库封装名 0/186 非空 ⇒ 本单交【写盘作业包 + 沙盒可达性证明 + 一条机器闸】三件. ★核心结论 (实测): ① 库名只存在于 (footprint Lib:Name) 那一行, 本机 KiCad 10.0.8 实测 (footprint NAME (lib A B)) 与 (footprint NAME (lib_id A:B)) 两种写法 LoadBoard 直接返回 None ⇒ 写了 = 板文件报废 ⇒ 只能写节点名一行; ② 全库 155 个 .pretty / 15468 个 .kicad_mod 逐焊盘几何等价穷举 ⇒ 只有 4/186 件 (J_SOM_P1~P4) 有几何等价件 ⇒ 其余 182 件写官方库名 = 假身份 ⇒ 不写; ③ 本单要写库名 94 件 (90 件换 land + 同时写 + 4 件只写身份) 不写 92 件; ④ 沙盒五轮 (S0 基线 / S1 换 land 不写名 / S2 换 land 加写名 / S3 只写名 / S4 反向对照) C4 全部 = 158 且 C1/C2/C3 逐字相同 ⇒ 写库名这一腿对 C4 的贡献 = 0 (别当预期换 land 会让 C4 降下来); ⑤ 板 md5 全程 611b869e13518c3c023fb178f91a0075 未动, 所有写盘动作只发生在 tmp/iss369/sbx/ 副本上." ref="HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md §1 §2 §3 §4 · logs/iss369/10_sandbox_readings.json"' \
 --add-answer 'key=iss369_libid_96_vs_90_reconcile to=main value="★ISS-369 件数口径对账 (要 main 裁的一条)★ 主线口径不动: 90 = 靶内 77 + 缺口 13 (与 ISS-361 四桶 / ISS-364 台账完全一致), 96 = 186 - 90. ★但任务书 §3 括注写的 TP 42 / DNP 26 / 靶内 22 / 缺口 1 之和 = 91 ≠ 96★ ⇒ 本单已逐条查清: TP 42 与脚本实算逐件相等; DNP 26 是【C4 四桶里的 DNP 26】, 而 96 桶里的 DNP 实算是 37 (= C4 的 26 + 不在 C4 的 11); 而 靶内 22 + 缺口 1 = 23 是【ISS-356 靶子 100 减 C4 158】的差 (充电板 22 件不在本板 + 在板的 J_DEBUG 1 件), 与本板 96 的分桶不是一回事. ⇒ 本单 96 的分桶一律按脚本实算给 (TP 42 / DNP 37 / 靶内-非C4 1 / 缺口-非C4 12 / 其它 4), 并在页 §3.3 把两种口径逐条对上 ⇒ ★要 main 确认: 任务书那处括注按【笔误】归档, 还是按【另一套口径】另有含义★." ref="HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md §3.3"' \
 --add-claim 'key=iss369_libid_gate_hooks value=not_hooked note="★ISS-369 新建闸 HW/check_fp_libid_truth.py 的挂链状态 = not_hooked★ ⇒ 不在 state/gate_check.py / state/daily_check.py / 任何 EXTRA_GATES 里 ⇒ 零挂链 ⇒ 挂不挂由 main 在签收时定 (链机制是 main 的地界). ★建议挂链时机: 板那一趟 (换 land + 写库名) 做完之后 ⇒ 挂上后本闸成为板面库封装名的常驻守卫. ★零挂链自证: grep -c check_fp_libid_truth state/gate_check.py = 0." ref=""' \
 --add-claim 'key=iss369_libid_write_is_legb_independent value=true note="★写库名这一腿与【腿 B 具名脚】互相独立★ ⇒ 实测: 沙盒 S1/S2 (只差 lib_id 一行) 的 C1/C2/C3/C4 读数逐字相同, S0/S3/S4 同 ⇒ 写库名不会替腿 B 减掉任何 C4 ⇒ C4 从 158 到 68 仍然只能靠腿 B (网表节点具名) ⇒ 板那一趟必须【换 land + 写库名 + 腿 B 具名脚】三件同批做, 拆批 ⇒ 板 md5 多变一次." ref="HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md §4"' \
 --add-claim 'key=iss369_libid_kicad_write_syntax value=lib_id_string_only note="★本机 KiCad 10.0.8 (pcbnew.GetBuildVersion() 实测) 写库封装名的唯一可用写法 = 改 (footprint Lib:Name) 那一行★ ⇒ (footprint NAME (lib LIB NAME)) 与 (footprint NAME (lib_id LIB:NAME)) 两种写法实测 LoadBoard() 返回 None (整板读不回来) ⇒ 写了 = 板报废 ⇒ 严禁使用. ★另: 库名指向不存在的库时板文件仍能正常加载 (E8) ⇒ 这就是必须用机器闸逐个 test -f 验 .kicad_mod 的原因." ref="HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md §2.2"' \
 --add-need 'key=iss369_taskbook_96_bucket_arithmetics to=main item="★ISS-369 任务书 §3 括注「其余 96 件 (TP 42 / DNP 26 / 靶内 22 / 缺口 1)」四个数之和 = 91 ≠ 96★ ⇒ 要 main 确认按【笔误】归档 (本单已按脚本实算给 96 的分桶并在页 §3.3 逐条对账), 还是那处另有一套含义需要本单补. ★本单不另立口径: 90 = 靶内 77 + 缺口 13 这条主线与 ISS-361 / ISS-364 完全一致★." since=2026-11-23' \
 --add-need 'key=iss369_jsom_df40_variant_choice to=main item="★ISS-369 未决项 W-4 要 main 拍板: J_SOM_P1~P4 这 4 件写哪个 DF40 变体 (a) Hirose_DF40C-100DS-0.4V_2x50_P0.4mm (b) Hirose_DF40HC(3.0)-100DS-0.4V_2x50_P0.4mm★ ⇒ 两个变体的焊盘几何逐件等价 (实测 Δpad = 0.000 mm, 旋转 180 度, 容差 0.05/0.05/0.10 mm) ⇒ 选哪个都不改铜箔 ⇒ 这是【壳体高度 3.0 mm 的结构问题】不是电气问题 ⇒ 本单写 (a) 并把 (b) 登记为等效候选, 不代拍. ★顺带请 main 确认这 4 件要不要进板那一趟 (它们不在 ISS-364 的 90 件换 land 名单里, 但本单认为应该写库名)." since=2026-11-23' \
 --status 'phase=iss369-board-libid-write-workpacket progress_pct=100 health=green summary="★ISS-369: 板面 186 封装库名 0/186 全空 ⇒ 交【写盘作业包 (90 + 96 逐件) + 沙盒五轮可达性证明 (C4 恒 158 ⇒ 写库名对 C4 贡献 0) + 机器闸 L0~L8/B0~B5 + selftest 11/11】★ 零写板 (md5 611b869e13518c3c023fb178f91a0075 未动) · 零落表 · 零挂链★"'

echo "=== 写后 md5 ==="
md5sum state/fragments/hw.yaml
stat -c '%y %s' state/fragments/hw.yaml
