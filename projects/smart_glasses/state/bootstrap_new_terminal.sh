#!/usr/bin/env bash
# ★换终端自检 (只读, 不改任何文件) —— 配套 docs/CONTINUITY.md
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; PROJ="$(dirname "$HERE")"
ok=0; bad=0
chk(){ if eval "$2" >/dev/null 2>&1; then printf "  [OK ] %-38s %s\n" "$1" "${3:-}"; ok=$((ok+1)); else printf "  [缺 ] %-38s %s\n" "$1" "${3:-}"; bad=$((bad+1)); fi; }
echo "=== 环境体检 (换终端续传用) ==="
chk "python3" "python3 -V" "$(python3 -V 2>&1)"
chk "pyyaml" "python3 -c 'import yaml'" "pip install pyyaml"
chk "requests" "python3 -c 'import requests'" "pip install requests"
chk "numpy/onnx/onnxruntime" "python3 -c 'import numpy,onnx,onnxruntime'" "pip install numpy onnx onnxruntime"
chk "rknn-toolkit2 (conda env rknn)" "source ~/miniconda3/etc/profile.d/conda.sh && conda activate rknn && python -c 'import rknn'" "conda create -n rknn python=3.10 && pip install rknn-toolkit2==2.3.2"
COCO="${COCO_ROOT:-/work/object_detection/data/coco/raw}"   # ★本项目约定的 COCO_ROOT (以 SW/tools/rknn_bench.py 里的为准)
chk "COCO val2017 + 标注" "ls $COCO/annotations/instances_val2017.json >/dev/null 2>&1" "下载 COCO 2017 val (约 1GB), 可改 COCO_ROOT"
chk "模型 yolov5s-sim.onnx" "ls ~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx >/dev/null 2>&1" "sha256 前16位应为 20368be665f6f59a"
echo "--- 仓库自检 ---"
chk "四道门能跑 (merge/gate/issue/daily)" "cd $PROJ && python3 state/merge.py && python3 state/gate_check.py" ""
chk "对齐检查 (GitHub API 限流时可能非 0)" "cd $PROJ && python3 state/alignment_check.py 2>&1 | grep -q '本地未推'" ""
echo "--- 配置自检 ---"
chk "网关配置 ~/.openclaw/openclaw.json" "test -f ~/.openclaw/openclaw.json" "cp config/openclaw.json.template 后填真值"
for a in main hw-lead sw-lead mech-lead; do
  chk "agent 定义 agents.json ($a)" "test -f ~/.openclaw/agents/$a/agent/agents.json" "cp config/openclaw.agents.json 并改 workspace 绝对路径"
  chk "agent 岗位说明书 ($a)" "ls ~/.openclaw/workspace*/AGENTS.md >/dev/null 2>&1 || ls ~/.openclaw/agents/$a/AGENTS.md >/dev/null 2>&1" "cp config/agents/$a/AGENTS.md 到该 agent 的 workspace 根"
done
chk "cron 任务 (含 token 守护)" "test -f ~/.openclaw/cron/jobs.json" "按 config/cron_jobs.template.json 重建 6 条"
echo "--- 必读文档 ---"
for f in "docs/CONTINUITY.md" "docs/DECISIONS_DIGEST.md" "TASK_BOARD.md" "PROGRESS_SNAPSHOT.md"; do
  [ -f "$PROJ/$f" ] && echo "  [OK ] $f" || echo "  [缺 ] $f"
done
echo "=============================================="
echo "  通过 $ok 项 / 缺 $bad 项"
[ "$bad" -eq 0 ] && echo "  ✅ 可以直接续传: 先读 TASK_BOARD.md §1/§2/§3 + PROGRESS_SNAPSHOT.md" || echo "  ⚠️ 先按上面 [缺] 列表补齐 (缺项清单在 docs/CONTINUITY.md §2)"
