#!/usr/bin/env bash
# ISS-295 cont3 · 分片原子写 (只写 mech-lead 自己那一份)
set -euo pipefail
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

python3 state/frag_write.py --agent mech-lead \
  --add-artifact 'path=logs/iss295/cont3_acceptance.log kind=evidence version=iss295-cont3 summary="★ISS-295 cont3 续验原始日志 (2026-11-18 05:36 实跑): 六道闸 rc 原样 (新闸主模式 rc=0 + --selftest 7/7 rc=0 + check_onepass_mech_sync rc=0 + check_onepass_struct_crosscheck rc=0 + state/merge rc=0 + state/gate_check rc=0 Q1 18/18) + 受保护 5 件 md5 + 板 mtime 2026-11-06 07:07:17 + 分片 grep -c iss295 = 9★"'

python3 state/frag_write.py --agent mech-lead \
  --add-answer 'key=iss295_mech_struct_input_claims_and_freshness_gate_cont3_reverify to=main value="★mech-lead cont3 续验回执 (2026-11-18 05:4x)★: ISS-295 四件交付物全部在盘且一字未改 (CLAIMS 页 37114 B md5 e91a594a / 新闸 22628 B md5 ce4c772d / 交卷单 45718 B / 分片 grep -c iss295 = 9) ⇒ 六道闸全绿 (新闸 rc=0 + --selftest 7/7 rc=0) + merge rc=0 + gate_check rc=0 (Q1 18/18) ⇒ 板零写双证 (md5 611b869e + mtime 2026-11-06 07:07:17.362193413) ⇒ 两页留痕自证在交付后仍成立 (XCHK 老行区 L1~L2161 与 cont2 备份逐字节 IDENTICAL; MSYNC L1~L799 与 18:13 备份逐字节相同, L801~L828 本单订正覆盖表原样在位, L829 起是 ISS-296 的追加段) ⇒ ★交付后漂移归因: 网表/脚表/BOM 三件 md5 于 2026-11-18 00:21:08 被别的单 (hw-lead 侧合法落表) 改写, 本单对 HW/ 的写操作 = 0 次; check_onepass_struct_crosscheck.py 于 00:59 被别的单改 (本单零改, 改后仍 rc=0); state/gate_check.py 于 02:50 被 main 挂闸 (本单零改) ⇒ 三处都不是本单越界★ ⇒ main 已于 2026-11-17 20:0x 独立复验落 verified ⇒ 本单无待办, 只剩 B6.1 那 4 条几何取舍等 main→老板拍 (本单只列事实与代价, 一条都没代拍)★" ref="HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md §B7 · logs/iss295/cont3_acceptance.log"'

echo "--- 写完校验 ---"
grep -c iss295 state/fragments/mech.yaml
grep -n "iss295_mech_struct_input_claims_and_freshness_gate" state/fragments/mech.yaml | cut -c1-120
