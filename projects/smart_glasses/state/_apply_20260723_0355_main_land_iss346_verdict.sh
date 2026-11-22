#!/usr/bin/env bash
# ★main 2026-11-23 03:5x · 把 ISS-346 的机器判决裁进 pm.yaml (★main 自己的分片·走 frag_write.py·零手写 YAML★)
set -euo pipefail
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

SPEC='key=iss346_q3_storage_tier_verdict_20261123 to=boss value="★★【main 裁 · 2026-11-23 03:5x · ISS-346 签收后】★★ ★**Q3 存储轴 = 【分档】, 不再是「卡 / 不卡」二元题** ★ ★**[实测] 机器判决 (5×4 矩阵 20/20 格 · failures=0 · 生成器 SW/tools/gen_storage_capacity_matrix.py 裸跑 rc=0)**: ① 只 ADB push 档 (demo) ⇒ 板侧零动作 ⇒ 不卡 ② 外挂 SPI-NOR 档 ⇒ J_BOOT1 焊盘位已在板 (6 pad @126.3,58) + 4 条 0Ω 串阻位必装 ⇒ PCB 层零动作 ⇒ 台架板档与产品板档都不卡 ③ eMMC 档 ⇒ 板宽 12→15 mm ⇒ 台架板档 B160x100 (160 mm 宽) 板面代价≈0 ⇒ 不卡 (时限型降为建议型) ⇒ ★**只有产品板档 F30A 60×30 / P60x15 才卡 (时限型)**★ ★ ★**⇒ 建议默认值栏改成「仅 eMMC 档需赶在板那一趟开工前进网表; SPI-NOR 档与只 ADB push 档板侧零动作, 零代价」⇒ ⇒ Q3 不再以「整卡」形式占着板那一趟的阻塞位**★ ★**容量口径订正 (ISS-346 B7-1)**: 原写「外挂 SPI-NOR 16~64 MB」⇒ ★**作废**⇒ 改「★**≥128 MiB (1 Gbit) 起的 SPI-NOR**★」★ (★依据: ISS-080 已锁死 flash ≥128MB · 且 Winbond 料号里的数字是 Mbit 不是 MB (W25Q64 = 8 MB)★) ★ ★**iss338_need_boot_storage_answer 措辞 3 条订正 (ISS-346 B7-2)**: ① 「3 条 SPI_*_BOOT」⇒ ★**4 条**★ (SPI_SCLK_BOOT / SPI_CSn_BOOT / SPI_MOSI_BOOT / SPI_MISO_BOOT = 网表 L202 / L204 / L206 / L208) ② 「外挂 SPI-NOR ⇒ 板要重出」⇒ ★**不成立**★ (走 J_BOOT1 焊盘位 ⇒ 板侧零动作 ⇒ 不重出板; 只有「主板上焊 SPI-NOR 芯片」才需要改板, 而该路已被网表明写「不画存储芯片」否掉) ③ 问原厂那一句改成「★主板侧 J_BOOT1 焊盘位与 4 条 SPI 走线已在板 (只 pin5/pin6 的 CONN 位 DNP); 请确认 SoM 侧是否引出这 4 条 SPI boot pin (我方网表侧记为 SoC_NC)★」 ★ ★**音频轴 (ISS-346 B7-3)**: 只登记一条「★音频轴与存储轴互不依赖 (存储轴的任何结论都不受音频决策影响)★」⇒ ★**音频做不做本单不判 / 不建议 / 不代拍**★ ★ ★**★本条不替老板拍板★** ⇒ 老板拍板页 `DECISION_ONE_PAGER_2026-11-22.md` §① 第 6 行 (Q3) 的「卡不卡」栏与「建议默认值」栏已按上列订正 (main 2026-11-23 03:5x 追加式) ★" ref="SW/STORAGE_CAPACITY_MATRIX.md · HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md · logs/iss346/matrix_cells.json (20 格 · failures=0) · DECISION_ONE_PAGER_2026-11-22.md §① 第 6 行 + §⑨"'

python3 state/frag_write.py --agent main --add-answer "$SPEC"
echo "--- 落盘复核 ---"
python3 - <<'EOF'
import yaml
d = yaml.safe_load(open('state/fragments/pm.yaml'))
ks = [e.get('key') for e in d.get('answers', [])]
print('answers 条数 =', len(ks), '| 零重复 =', len(ks) == len(set(ks)))
print('新条目在盘 =', 'iss346_q3_storage_tier_verdict_20261123' in ks)
EOF
