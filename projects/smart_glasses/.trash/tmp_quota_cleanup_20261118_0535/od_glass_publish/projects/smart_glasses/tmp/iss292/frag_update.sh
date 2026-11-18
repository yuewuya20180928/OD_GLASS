#!/bin/bash
# ★ISS-292 · 分片登记 (★走 state/frag_write.py 的原子写★)
set -e
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

python3 state/frag_write.py --agent hw-lead \
  --add-need 'key=iss292_generator_realigned to=main since=2026-11-17 item="★清单页生成器已与盘面页对齐 (★need iss289_preflight_generator_stale 闭合★): state/_iss277_build_preflight.py 改成 ★现状值一律从真源读★ (R3-A4 三个数 ← check_netlist_contradiction_r3.py 的实跑输出; 脚表缺陷条数 ← check_pin_function_labels.py 的实跑输出; 落表事件 ← 落表台账) ⇒ ★不许写死★; ★补齐 B32_V2_NET_RENAME (★清单页 31 → 32 条★)★; ★条目 id B17_DNP_43 保留不改名 (★id 里的 43 是历史命名 · 值已按落表链头前移★)★; ★追加式订正块 (ISS-283 §3-追加 + ISS-289 §附录 + state_baseline 登记表) 搬进 sidecar state/_iss277_preflight_appendix.md ⇒ 重跑不许冲掉★ ⇒ ★★重跑后清单页 md5 逐字节相同 (159bf20fe71c36e48292f39dafc46a35) ⇒ 作业包 md5 也不变★★ ⇒ ★★页回退这条路已经堵死★ ★"'

python3 state/frag_write.py --agent hw-lead \
  --add-need 'key=iss292_s1_ref_source_pointer_fixed to=main since=2026-11-17 item="★作业包 §3-S1 的位号真源指针已改对 (★need iss289_s1_specjson_devices_missing 闭合★): 老字 器件位号真源 = HW/SCHEMATIC_V1_SPEC.json (devices 段的 186 个 ref) ★原样保留一字未删★, 追加式订正写进作业包 §8.3.1 ⇒ ★改指 HW/netlist_v1_pins.csv (★218 器件 / 584 脚 · 本机实读★)★; ★为什么原指针失效已写进订正句: 该 JSON 顶层只有 meta / counts / connections / power_rails / display_select / testpoints / undrawable 七个键, 没有 devices 段 ⇒ 照字面实现会找不到真源★ ★"'

python3 state/frag_write.py --agent hw-lead \
  --add-need 'key=iss292_reanchor_written_into_closeout to=main since=2026-11-17 item="★动板那趟的收工清单已写成强制项 (★need iss289_state_baseline_reanchor_after_board_run 闭合★): 作业包新增 §8.3.2 收工清单 ⇒ ★F-1 收工后同一次做完三步 (重跑生成器 → 同一次重锚两份文档的 state_baseline 写死期望值 → 新闸 HW/check_workpack_state_values.py 跑绿)★; ★最危险四条的重锚值写全 (W11/C04 封装 186 ⇒ 185 · W09_SAME_PAD_NET 同号异网 3 ⇒ 0 · W12/C03 156 ⇒ 155 或 156 · W18 1 ⇒ 157 或 156)★; ★F-3 警告: 不许为了让闸绿而把 C_VBUS_GND 装回板上 ⇒ 那会直接毁掉 §3-S2 的 C1 多余 0 ⇒ 代价 2-4 周 + ¥4-8K★ ★"'

python3 state/frag_write.py --agent hw-lead \
  --add-need 'key=iss292_preflight_s6_sources_gap to=main since=2026-11-17 item="★清单页 §6 的来源单全集里还没有 ISS-283 (★但 §2 表里已经有 source_iss=ISS-283 的 B32_V2_NET_RENAME★) ⇒ 机器闸 check_onepass_preflight_coverage.py 自己的 SOURCES 已含 ISS-283 (★P4 绿★) ⇒ ★只是页面文案与实际来源集不一致★ ⇒ ★本单故意没改这一行 (★改了页 md5 就变 ⇒ 违反重跑幂等的硬判据★)★ ⇒ 登记给下一趟顺手带上 ★"'

python3 state/frag_write.py --agent hw-lead \
  --add-need 'key=iss292_c_vbus_gnd_decision_still_open to=main since=2026-11-17 item="★C_VBUS_GND 留不留仍是老板 / PM 域★: 本单只交事实与代价 (★§3-S2 的判据是 C1 多余 0 ⇒ 它必须下板 ⇒ 官方板封装数 186 ⇒ 185★) ⇒ ★不替老板拍板 · 不自签 issue_log★ ⇒ ★★但请注意: 那一趟收工后若有人为让闸绿而把它装回去 ⇒ 直接毁掉 §3-S2 ⇒ 2-4 周 + ¥4-8K★★ ★"'

python3 state/frag_write.py --agent hw-lead \
  --add-artifact 'path="state/_iss277_build_preflight.py" kind=tool version=iss292-r1 updated_at=2026-11-17 summary="★清单页生成器 (★主改动★): 现状值一律从真源读 (R3-A4 ← check_netlist_contradiction_r3.py / 脚表缺陷条数 ← check_pin_function_labels.py / 落表事件 ← 落表台账) ⇒ 不许写死; 补齐 B32_V2_NET_RENAME (32 条); 条目 id B17_DNP_43 保留; 追加式订正块从 sidecar 搬运; sidecar 缺失 ⇒ 拒写页 (fail-closed); PREFLIGHT_PROJ 可指向沙盒"' \
  --add-artifact 'path="state/_iss277_preflight_appendix.md" kind=spec version=iss292-r1 updated_at=2026-11-17 summary="★追加式订正块 sidecar (★生成器的第二个输入★): ISS292:S3_APPENDIX = ISS-283 的 §③-1~§③-3 三条 (插在 §3 末尾); ISS292:ISS289_APPENDIX = ISS-289 的 §附录 + state_baseline 登记表 (29 条) (追加在页尾) ⇒ 只许往后追加, 生成器只搬运不改一个字; 其 expect 是漂移闸的期望值, 故意不随盘面自动更新 ⇒ 盘面一变闸当场红 ⇒ 那时同一次重锚"' \
  --add-artifact 'path="state/_iss277_preflight_README.md" kind=doc version=iss292-r1 updated_at=2026-11-17 summary="★生成器维护说明: 输入 / 输出 / 真源三件套 (★读什么从哪读干什么用读不到怎么办★) + 三条铁律 + 幂等自检命令 + 沙盒跑法 + 4 条反向用例在证明什么 + 维护时最容易踩的三个坑 + 收工重锚指向作业包 §8.3.2"' \
  --add-artifact 'path="HW/PCB/BOARD_ONEPASS_PREFLIGHT.md" kind=spec version=iss292-r1 updated_at=2026-11-17 summary="★清单页 (★生成器重跑后逐字节不变★): md5 159bf20fe71c36e48292f39dafc46a35 与 ISS-289 交卷时相同 ⇒ 重跑幂等; 32 条 (含 B32_V2_NET_RENAME); B17_DNP_43 的三个数与脚表缺陷条数现在由真源读出"' \
  --add-artifact 'path="HW/PCB/BOARD_ONEPASS_WORKPACKET.md" kind=spec version=iss292-r1 updated_at=2026-11-17 summary="★作业包追加式订正 §8.3 (★老字一字未删★): §8.3.1 §3-S1 位号真源指针改指 HW/netlist_v1_pins.csv (218 器件) + 原指针失效原因; §8.3.2 板那一趟的收工清单 (F-1 同一次重锚三步 / F-2 最危险四条重锚值 / F-3 不许为让闸绿把 C_VBUS_GND 装回板上 / F-4 其余 21 条); §8.3.3 生成器与盘面页同源的登记"' \
  --add-artifact 'path="HANDOFF/2026-11-17_hw-lead_ISS292_清单页生成器对齐.md" kind=handoff version=iss292-r1 updated_at=2026-11-17 summary="★ISS-292 交卷单: B0 基线 / B1 病灶逐条带行号 / B2 生成器改动 (真源读数 + sidecar + B32 + id 不改名) / B3 重跑幂等硬判据实测 (页 md5 逐字节相同) / B4 作业包 §8.3 追加式订正 / B5 4 条反向用例原样 rc / B6 回归 8 条 rc + 板 md5+mtime 双重自证"' \
  --add-artifact 'path="tmp/iss292/reverse_tests.py" kind=probe version=iss292-r1 updated_at=2026-11-17 summary="★反向用例: ① 沙盒模拟又一次合法落表 ⇒ R3-A4 跟着变 (50/39/39) ② 生成器写死旧值 ⇒ 页回退 + 新闸 rc=1 ③ 正向对照 ⇒ 页零变化 + 闸 rc=0 ④ sidecar 缺失 ⇒ 拒写页; 全过才 rc=0; 只动沙盒, 真盘零写"'

python3 state/frag_write.py --agent hw-lead \
  --add-claim 'key=iss292_generator_idempotent value="★清单页生成器重跑幂等: 跑前后 HW/PCB/BOARD_ONEPASS_PREFLIGHT.md md5 逐字节相同 (159bf20fe71c36e48292f39dafc46a35)★" note="★现状值全部从真源读 (R3-A4 / 脚表缺陷条数 / 落表台账事件) + 追加式订正块走 sidecar 只搬运 ⇒ 谁跑生成器都不会再把 ISS-283 / ISS-289 的订正冲掉★ ref=logs/iss292/reverse_tests.log + logs/iss292/b6_gates1.log"'

python3 state/frag_write.py --agent hw-lead \
  --status 'phase=P1 progress_pct=100 health=green summary="★ISS-292 交卷完成 (2026-11-17 18:0x): 清单页生成器 state/_iss277_build_preflight.py 已与盘面页对齐 ⇒ ★重跑幂等 (页 md5 159bf20fe71c36e48292f39dafc46a35 跑前跑后逐字节相同·作业包也不变)★ ⇒ ★页回退这条路已堵死★; 现状值一律从真源读 (R3-A4 ← check_netlist_contradiction_r3.py · 脚表缺陷条数 ← check_pin_function_labels.py · 落表事件 ← 落表台账) 不许写死; 补齐 B32_V2_NET_RENAME (31→32 条); 条目 id B17_DNP_43 保留改名禁止 (id 里的 43 是历史命名); 追加式订正块搬进 sidecar state/_iss277_preflight_appendix.md (缺失即拒写页·fail-closed); 作业包追加式订正 §8.3 (S1 位号真源指针改指 netlist_v1_pins.csv 218 器件 + 收工清单强制项与最危险四条重锚值 + 不许为让闸绿把 C_VBUS_GND 装回板上); 4 条反向用例全过 (落表链头前跳⇒R3-A4 跟着变 / 写死旧值⇒页回退且闸 rc=1 / 正向对照⇒零变化且闸 rc=0 / sidecar 缺失⇒拒写); 回归 8 条 rc 全 0 (workpack_state_values +selftest 10/10 · onepass_preflight_coverage +selftest 11/11 · board_frame_caliber · merge · gate_check Q1 18/18 · issue_check); 零写板 (md5+mtime 双重自证 板 mtime 仍 2026-11-06 07:07:17) 零落表 零外发 不替老板拍板 不自签 issue_log; 给 main 5 条 need★"'

echo "=== 校验 ==="
grep -c "iss292" state/fragments/hw.yaml
grep -n "iss292" state/fragments/hw.yaml | head -20
