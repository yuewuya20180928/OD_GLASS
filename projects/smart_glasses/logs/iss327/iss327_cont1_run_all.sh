#!/usr/bin/env bash
# iss327_cont1_run_all.sh —— ISS-327 cont1 · 三棵沙盒的闸链实跑 + 注册表重建 (★只写 logs/iss327/ + tmp/iss327/★)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
P=$PWD

echo "########## ① 对照组 sbCtl (★整树真拷贝·零改名·闸副本真文件★) ##########"
bash logs/iss327/iss327_run_gates.sh "$P/tmp/iss327/sbCtl" logs/iss327/12_sbCtl CTL

echo ""
echo "########## ② sbR0 (★五侧改名 + SW 文档未同步 + 旧注册表★) ##########"
bash logs/iss327/iss327_run_gates.sh "$P/tmp/iss327/sbR0" logs/iss327/13_sbR0 R0

echo ""
echo "########## ③ sbR3 (★五侧改名 + SW 文档已同步 + 旧注册表★) ##########"
bash logs/iss327/iss327_run_gates.sh "$P/tmp/iss327/sbR3" logs/iss327/14_sbR3 R3

echo ""
echo "########## ④ sbR0 → 重建注册表 ⇒ sbR1 ##########"
( cd "$P/tmp/iss327/sbR0" && python3 SW/tools/check_sw_ref_reachability.py --freeze-registry ) > logs/iss327/15_sbR0_freeze_stdout.txt 2>&1
echo "freeze rc=$? · stdout → logs/iss327/15_sbR0_freeze_stdout.txt"
python3 logs/iss327/iss327_apply_registry.py "$P/tmp/iss327/sbR0" logs/iss327/15_sbR0_freeze_stdout.txt
bash logs/iss327/iss327_run_gates.sh "$P/tmp/iss327/sbR0" logs/iss327/16_sbR1 R1

echo ""
echo "########## ⑤ sbR3 → 重建注册表 ⇒ sbR2 ##########"
( cd "$P/tmp/iss327/sbR3" && python3 SW/tools/check_sw_ref_reachability.py --freeze-registry ) > logs/iss327/17_sbR3_freeze_stdout.txt 2>&1
echo "freeze rc=$? · stdout → logs/iss327/17_sbR3_freeze_stdout.txt"
python3 logs/iss327/iss327_apply_registry.py "$P/tmp/iss327/sbR3" logs/iss327/17_sbR3_freeze_stdout.txt
bash logs/iss327/iss327_run_gates.sh "$P/tmp/iss327/sbR3" logs/iss327/18_sbR2 R2

echo ""
echo "########## 全部跑完 ##########"
date '+%F %T %Z'
