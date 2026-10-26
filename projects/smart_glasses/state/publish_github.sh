#!/bin/bash
# ★GitHub 同步脚本 (OD_GLASS) —— 项目总工维护
# 流程: 刷新生成物 → rsync 项目库 → 拷贝 docs/config 映射件 → **真值反查脱敏** → commit → push → 用 GitHub API 验 blob SHA
# 纪律: ① 仓库公开, 推前必须过真值反查 (命中 0 才推) ② 验证不许用 raw.githubusercontent (CDN 缓存旧版)
set -u
WS=/home/yuewuya/.openclaw/workspace
PROJ=$WS/projects/smart_glasses
PUB=/tmp/od_glass_publish
REPO=yuewuya20180928/OD_GLASS
MSG="${1:-自动同步: 状态刷新}"

cd "$PROJ" || exit 1

# ---- 1. 刷新生成物 ----
python3 state/gen_todo.py        >/dev/null 2>&1 && echo "[1] TODO.md 已刷新"
python3 state/daily_check.py     >/dev/null 2>&1
python3 state/gen_publish_docs.py --out "$PROJ/docs" >/dev/null 2>&1 && echo "[1] docs/PROJECT_STATUS.md + docs/OPEN_ISSUES.md 已刷新"
python3 state/merge.py            >/dev/null 2>&1

# ---- 2. 发布树 ----
if [ ! -d "$PUB/.git" ]; then
  rm -rf "$PUB"; mkdir -p "$PUB"; cd "$PUB"
  git init -q -b main
  git remote add origin git@github.com:$REPO.git
fi
cd "$PUB" || exit 1
# ★从远端 rehydrate (机器重启会清空 /tmp → 发布树会变空仓库; 每次先拉回远端状态)
git fetch -q origin main 2>/dev/null && git reset -q --hard origin/main 2>/dev/null
# git 身份 (新仓库没有身份 → commit 会失败)
git config user.name "yuewuya20180928"
git config user.email "yuewuya20180928@users.noreply.github.com"

rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
      "$PROJ/" projects/smart_glasses/

# ---- 3. docs / config 映射件 ----
mkdir -p docs config/agents/main
cp "$WS/AGENTS.md" config/agents/main/AGENTS.md
[ -f "$PROJ/REPO_README.md" ] && cp "$PROJ/REPO_README.md" README.md
for a in hw-lead sw-lead mech-lead; do
  [ -f "/home/yuewuya/.openclaw/workspace-$a/AGENTS.md" ] && cp "/home/yuewuya/.openclaw/workspace-$a/AGENTS.md" "config/agents/$a/AGENTS.md"
done
cp "$PROJ/TODO.md" docs/TODO.md
cp "$PROJ/docs/PROJECT_STATUS.md" docs/PROJECT_STATUS.md
cp "$PROJ/docs/OPEN_ISSUES.md" docs/OPEN_ISSUES.md
cp "$PROJ/state/STATUS_DIGEST.md" docs/STATUS_DIGEST.md
cp "$PROJ/CERT_CHECKLIST.md" docs/CERT_CHECKLIST.md
cp "$PROJ/DECISIONS.md" docs/DECISIONS.md
cp "$PROJ/DECISION_TABLE_Q1_Q4_Q17.md" docs/DECISION_TABLE_Q1_Q4_Q17.md
cp "$PROJ/FRAMEWORK_SCOPE.md" docs/FRAMEWORK_SCOPE.md
cp "$PROJ/INTERFACES.md" docs/INTERFACES.md
cp "$PROJ/PRINT/PRINTER_SETUP.md" docs/PRINT_SETUP.md
cp "$PROJ/STRESS_TEST_2026-10-25.md" docs/STRESS_TEST_2026-10-25.md
cp "$PROJ/STATUS_SUMMARY.md" docs/STATUS_SUMMARY.md
# 框架文档 (若项目树里有 FRAMEWORK/ 则整目录带过去)
[ -d "$PROJ/FRAMEWORK" ] && rsync -a --delete "$PROJ/FRAMEWORK/" docs/FRAMEWORK/

# ---- 4. ★真值反查脱敏 (仓库公开, 命中 0 才准推) ----
python3 - "$PUB" <<'PY'
import json, os, sys, re
pub = sys.argv[1]
truths = []
cfgp = os.path.expanduser("~/.openclaw/openclaw.json")
try:
    cfg = json.load(open(cfgp, encoding="utf-8"))
    def walk(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and len(v) >= 20 and re.search(r"(token|apikey|secret|password)", k, re.I):
                    truths.append((p + "/" + k, v))
                else:
                    walk(v, p + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{p}[{i}]")
    walk(cfg)
except Exception as e:
    print("⚠️ 读不到 openclaw.json:", e)
# agent 目录里的 auth profile 也取真值
for p in ("/home/yuewuya/.openclaw/agents/main/agent/auth-profiles.json",):
    try:
        d = json.load(open(p, encoding="utf-8"))
        def w2(o, pre=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and len(v) >= 20 and re.search(r"(key|token|secret)", k, re.I):
                        truths.append((pre + "/" + k, v))
                    else:
                        w2(v, pre + "/" + k)
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    w2(v, f"{pre}[{i}]")
        w2(d)
    except Exception:
        pass
hits = []
for root, dirs, files in os.walk(pub):
    dirs[:] = [d for d in dirs if d != ".git"]
    for f in files:
        p = os.path.join(root, f)
        try:
            data = open(p, "rb").read().decode("utf-8", "ignore")
        except Exception:
            continue
        for name, t in truths:
            if t and t in data:
                hits.append((os.path.relpath(p, pub), name))
print(f"真值反查: {len(truths)} 条凭据真值 × 整棵发布树 → 命中 {len(hits)}")
for h in hits[:10]:
    print("   ❌ 命中:", h)
sys.exit(1 if hits else 0)
PY
if [ $? -ne 0 ]; then
  echo "❌ 真值反查有命中, 拒绝推送"
  exit 1
fi
echo "[4] 真值反查 0 命中 ✅"

# ---- 5. commit + push ----
git add -A
if git diff --cached --quiet; then
  echo "[5] 无变化 (跳过 push)"
else
  git commit -q -m "$MSG" && git push -q origin main && echo "[5] 已 push: $(git rev-parse --short HEAD)"
fi

# ---- 6. 验证 (用 GitHub API 比 blob SHA, 不用 raw.githubusercontent) ----
python3 - "$PUB" "$REPO" <<'PY'
import json, os, subprocess, sys, urllib.request
pub, repo = sys.argv[1], sys.argv[2]
def gh(path):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}{path}",
                                 headers={"User-Agent": "openclaw-verify"})
    return json.load(urllib.request.urlopen(req, timeout=30))
files = ["docs/PROJECT_STATUS.md", "docs/OPEN_ISSUES.md", "docs/TODO.md",
         "projects/smart_glasses/PROJECT_TRACKER.md",
         "projects/smart_glasses/state/issue_log.yaml",
         "projects/smart_glasses/HW/SCHEMATIC_V1_SPEC.json",
         "projects/smart_glasses/state/check_netlist.py",
         "docs/STATUS_SUMMARY.md", "projects/smart_glasses/STATUS_SUMMARY.md",
         "projects/smart_glasses/HW/ONLINE_FINDINGS_2026-10-26.md",
         "README.md", "projects/smart_glasses/REPO_README.md",
         "HW/SCHEMATIC_V1.md"]
ok = bad = 0
for f in files:
    if not os.path.exists(os.path.join(pub, f)):
        print(f"  ⏭  {f} (本地没有, 跳过)")
        continue
    local = subprocess.run(["git", "-C", pub, "rev-parse", f"HEAD:{f}"], capture_output=True, text=True).stdout.strip()
    try:
        remote = gh(f"/contents/{f}?ref=main").get("sha", "")
    except Exception as e:
        print(f"  ❌ {f} → API 取不到: {e}")
        bad += 1
        continue
    same = local == remote
    ok += same
    bad += (not same)
    print(f"  {'✅' if same else '❌'} {f}  local={local[:8]} remote={remote[:8]}")
print(f"验证: {ok} 一致 / {bad} 不一致")
sys.exit(1 if bad else 0)
PY
