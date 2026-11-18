#!/usr/bin/env bash
# ISS-305 v2 · 下游传播闭环核对 (★只读·不改任何工程文件★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 99
echo "=== [09-1] 交付页 三代读数 (登记 / 我复验时 / 现在) ==="
echo "-- 登记值 (issue_log ISS-131 note) --"
grep -n "RK3572_INQUIRY_CALIBER_V2.md" state/issue_log.yaml | head -3 | cut -c1-200
echo "-- 我复验时 (8,863 B 版 = main 改前备份) --"
stat -c '%s B  %y  %n' HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow
md5sum HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow
echo "-- 现在 (main 追加 §5 后) --"
stat -c '%s B  %y  %n' HW/RK3572_INQUIRY_CALIBER_V2.md
md5sum HW/RK3572_INQUIRY_CALIBER_V2.md
echo "-- diff 摘要 (改前备份 vs 现版) --"
diff HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow HW/RK3572_INQUIRY_CALIBER_V2.md | grep -c "^[<>]"
echo "   ↑ 改动行数 (删除 3 行 + 新增 48 行 ⇒ append-only + 3 处指向注记 + 1 处措辞订正)"

echo
echo "=== [09-2] 交付页现版: B5-2 (判据非排他) 有没有补口径说明? ==="
grep -nE "排他|±3|窗口|非排他|真判别|_iss305_ball_truth_parser" HW/RK3572_INQUIRY_CALIBER_V2.md ; echo "grep rc=$? (1=零命中 ⇒ 未补口径说明)"

echo
echo "=== [09-3] 宽版 over-claim 原文 在盘上还剩几处 (排除 .trash/.bak/issue_log/frag/handoff) ==="
grep -rn "多摄像头方案在 RK3572 上不成立" --include="*.md" . 2>/dev/null | grep -v "\.trash" | grep -v "\.bak" | grep -v "^\./HANDOFF/" | grep -v "^\./state/fragments" | grep -v "^\./state/issue_log" | cut -c1-220

echo
echo "=== [09-4] 交付页 §5-3 声称的两处下游订正 (DECISION_INDEX §D / DECISION_PENDING §A-补29) 实况 ==="
echo "-- DECISION_PENDING_2026-11-16.md §A-补29 起 (L1603..EOF) 命中 ISP/多摄/收窄 的行数 --"
sed -n '1603,$p' DECISION_PENDING_2026-11-16.md | grep -cE "ISP|多摄|收窄"; echo "   ↑ 0 ⇒ §A-补29 是 ESD 节, 没有 ISP 收窄内容"
echo "-- DECISION_INDEX_2026-11-18.md §D 起 (L89..EOF) 命中 ISP/多摄/One channel 的行数 --"
sed -n '89,$p' DECISION_INDEX_2026-11-18.md | grep -cE "ISP 处理|多摄|One channel"; echo "   ↑ 0 ⇒ §D 是 ESD 节, 没有 ISP 收窄内容"
echo "-- DECISION_PENDING_2026-11-16.md L1573 (★§A-补28 里那条老字★) 原文 --"
sed -n '1573p' DECISION_PENDING_2026-11-16.md | cut -c1-400
echo "-- TASK_BOARD.md 是否已记收窄 --"
grep -n "实时 ISP 处理路数" TASK_BOARD.md | cut -c1-160

echo
echo "=== [09-5] main 的 ISS-131 verify_result 说 n1/n2「另开单」⇒ 台账里有没有对应单? ==="
grep -nE "parse_rk3572_datasheet|rk3572_pins\.csv.*修|排他归属|ball_truth|_iss131_crosscheck.*换判据" state/issue_log.yaml | cut -c1-200
echo "grep rc=$? (1=零命中 ⇒ 台账里没有对应的新单)"

echo
echo "=== [09-6] B5-7 (字节数登记过期) 修没修? ==="
echo "-- issue_log ISS-131 note 里 交付页 字节数 --"
grep -n "RK3572_INQUIRY_CALIBER_V2.md.*6,007 B" state/issue_log.yaml | cut -c1-160
grep -n "6,007 B" state/issue_log.yaml | cut -c1-160 | head -3
echo "-- DECISION_PENDING 里 ISS-131 行的字节数 --"
sed -n '1545p' DECISION_PENDING_2026-11-16.md | grep -o "RK3572_INQUIRY_CALIBER_V2.md.*字节\|(6,007 B)" | head -2

echo
echo "=== [09-7] 交付页现版 F 判据复检: 全篇 [实测] / 实测 逐行 ==="
grep -n "实测" HW/RK3572_INQUIRY_CALIBER_V2.md | cut -c1-200
echo "-- 命中行数 --"; grep -c "实测" HW/RK3572_INQUIRY_CALIBER_V2.md
echo "-- 真·证据等级标签 [实测] 出现处 (应只有: L29 订正注记 + L110 零声明) --"
grep -n "\[实测\]" HW/RK3572_INQUIRY_CALIBER_V2.md | cut -c1-160
