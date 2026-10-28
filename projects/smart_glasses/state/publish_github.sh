#!/bin/bash
# ★GitHub 同步脚本 (OD_GLASS) —— 项目总工维护
# 流程: 刷新生成物 → rsync 项目库 → 拷贝 docs/config 映射件 → **真值反查脱敏** → commit → push → 用 GitHub API 验 blob SHA
# 纪律: ① 仓库公开, 推前必须过真值反查 (命中 0 才推) ② 验证不许用 raw.githubusercontent (CDN 缓存旧版)
set -u
# ★并发锁: 多个来源 (我手动 / cron 自动 / 队列) 同时推同一棵树会撞 git 锁 → 用 flock 串行化
LOCK=/tmp/od_glass_publish.lock
exec 9>"$LOCK"
flock -w 120 9 || { echo "❌ 拿不到发布锁 (另一个发布在跑), 跳过"; exit 0; }
WS=/home/yuewuya/.openclaw/workspace
PROJ=$WS/projects/smart_glasses
PUB=/tmp/od_glass_publish
REPO=yuewuya20180928/OD_GLASS
MSG="${1:-自动同步: 状态刷新}"

cd "$PROJ" || exit 1

# ---- 1. 刷新生成物 ----
# ★2026-10-28 加固: 生成器失败必须**当场报错并退出**, 不能吞掉错误继续推。
#   事故: gen_todo.py 有语法错误时, `>/dev/null 2>&1` 把错误吞了, 文档没更新但脚本继续跑,
#   结果**推的是旧文档却以为刷新了** ⇒ 老板在 GitHub 上看到过期数据而无人知道。
#   ⇒ 统一: 失败即退出 (set -e 之外再加显式检查), 且失败时把 stderr 原文打出来。
gen() {  # gen <说明> <命令...>
  local desc="$1"; shift
  local err
  if ! err=$("$@" 2>&1 >/dev/null); then
    echo "[1] ❌ 生成失败: $desc"
    echo "$err" | head -20
    echo "[1] ★已中止发布 —— 不推陈旧文档 (修好后重跑)"
    exit 1
  fi
  echo "[1] $desc 已刷新"
}
gen "TODO.md"                    python3 state/gen_todo.py
gen "门禁快照"                    python3 state/daily_check.py
gen "docs/PROJECT_STATUS.md + docs/OPEN_ISSUES.md" python3 state/gen_publish_docs.py --out "$PROJ/docs"
gen "docs/START_HERE.md (接手指南)" python3 state/gen_start_here.py
gen "STATUS_SUMMARY.md (一页看懂)" python3 state/gen_status_summary.py
gen "STATE.yaml"                 python3 state/merge.py

# ---- 2. 发布树 ----
if [ ! -d "$PUB/.git" ]; then
  rm -rf "$PUB"; mkdir -p "$PUB"; cd "$PUB"
  git init -q -b main
  git remote add origin git@github.com:$REPO.git
fi
cd "$PUB" || exit 1
# ★从远端 rehydrate (机器重启会清空 /tmp → 发布树会变空仓库; 每次先拉回远端状态)
# ★★2026-10-28 18:3x 加固: 原写法 `git fetch -q ... 2>/dev/null && git reset ...` —
#   **fetch 失败时错误被吞掉, 脚本继续跑** ⇒ rsync --delete 把发布树覆盖成只有新内容
#   ⇒ 随后 commit+push 会把**远端全部历史压成一个新 commit** (历史丢失!)
#   ⇒ 现在: fetch 失败 = **中止发布** (宁可今天不推, 也不能毁历史)
if ! git fetch -q origin main 2>/tmp/_fetch_err.log; then
  echo "[2] ❌ 从远端 rehydrate 失败 —— ★中止发布 (避免把远端历史压扁)"
  echo "--- fetch 错误 ---"
  head -10 /tmp/_fetch_err.log 2>/dev/null
  echo "[2] ★网络恢复后重跑即可; 本次未推送任何内容"
  exit 1
fi
git reset -q --hard origin/main 2>/dev/null || { echo "[2] ❌ reset 失败, 中止"; exit 1; }
# ★检查要用 HEAD (不是 main 分支) —— fetch 后 `git reset --hard origin/main` 才把 HEAD 指过去;
#   查 main 分支会在"本地分支还没跟上"时误判为空 (2026-10-28 18:4x 实测踩中: fetch 其实成功了)
if [ -z "$(git rev-parse HEAD 2>/dev/null)" ]; then
  echo "[2] ❌ rehydrate 后仍无 commit —— 中止发布 (★绝不能推一个空历史的仓库)"
  exit 1
fi
echo "[2] rehydrate OK: HEAD = $(git rev-parse --short HEAD)"
# git 身份 (新仓库没有身份 → commit 会失败)
git config user.name "yuewuya20180928"
git config user.email "yuewuya20180928@users.noreply.github.com"

# ★排除运行时垃圾 (BOOTSTRAP.md 是 runtime 在 cwd 生成的通用提示, 不是项目文件;
#   .openclaw/ 是 runtime 状态) —— 上一版它被推上了 GitHub 公开发布树
# ★备份目录清理 (源树与发布树都要清): rsync 的 --delete **不会删被 exclude 保护的目标端文件**
#   → 之前推过一次 .v11_backup/ 与 HW/.iss075_bak/ (公开仓库里不该有)
find "$PROJ" -maxdepth 3 \( -name '.*_bak' -o -name '*_backup' -o -name '.*_backup' \) -type d -exec rm -rf {} + 2>/dev/null
find "$PUB" -maxdepth 5 \( -name '.*_bak' -o -name '*_backup' -o -name '.*_backup' \) -type d -exec rm -rf {} + 2>/dev/null
rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' \
      --exclude 'BOOTSTRAP.md' --exclude '.openclaw' --exclude 'workspace-state.json' \
      --exclude '*.tmp' --exclude '.DS_Store' \
      --exclude '.*_bak' --exclude '*_backup' --exclude '.*_backup' --exclude '.bak_*' \
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
cp "$PROJ/docs/START_HERE.md" docs/START_HERE.md
cp "$PROJ/state/STATUS_DIGEST.md" docs/STATUS_DIGEST.md
cp "$PROJ/CERT_CHECKLIST.md" docs/CERT_CHECKLIST.md
cp "$PROJ/DECISIONS.md" docs/DECISIONS.md
cp "$PROJ/DECISION_TABLE_Q1_Q4_Q17.md" docs/DECISION_TABLE_Q1_Q4_Q17.md
cp "$PROJ/FRAMEWORK_SCOPE.md" docs/FRAMEWORK_SCOPE.md
cp "$PROJ/INTERFACES.md" docs/INTERFACES.md
cp "$PROJ/PRINT/PRINTER_SETUP.md" docs/PRINT_SETUP.md
cp "$PROJ/STRESS_TEST_2026-10-25.md" docs/STRESS_TEST_2026-10-25.md
cp "$PROJ/STATUS_SUMMARY.md" docs/STATUS_SUMMARY.md
# 发布树 .gitignore (防垃圾再进来)
cat > .gitignore <<'GITIGNORE'
__pycache__/
*.pyc
.DS_Store
*.tmp
state/.lastgood/
BOOTSTRAP.md
.openclaw/
workspace-state.json
GITIGNORE
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
# ★被跟踪过的运行时垃圾要显式 untrack (rsync 排除 = 保护不被删, 所以它会留在仓库里)
for junk in projects/smart_glasses/BOOTSTRAP.md projects/smart_glasses/.openclaw/workspace-state.json; do
  git rm -q --cached --ignore-unmatch "$junk" 2>/dev/null
  rm -f "$junk" 2>/dev/null
done
git add -A
if git diff --cached --quiet; then
  echo "[5] 无变化 (跳过 push)"
else
  git commit -q -m "$MSG" && git push -q origin main && echo "[5] 已 push: $(git rev-parse --short HEAD)"
fi

# ---- 6. 验证 (① 远端 SHA == 本地 HEAD (不需要 API, 免限流) ② blob SHA 逐个比, API 限流时跳过) ----
echo "[6] 远端 SHA 校验 (ls-remote, 不吃 API 限流)"
REMOTE_SHA=$(git ls-remote origin main | cut -f1)
LOCAL_SHA=$(git rev-parse HEAD)
if [ "$REMOTE_SHA" = "$LOCAL_SHA" ]; then
  echo "  ✅ 远端 main = 本地 HEAD = ${LOCAL_SHA:0:8} → 推送已落地"
else
  echo "  ❌ 远端 ${REMOTE_SHA:0:8} != 本地 ${LOCAL_SHA:0:8}"
  exit 1
fi

python3 - "$PUB" "$REPO" <<'PY'
import json, os, subprocess, sys, urllib.request, time
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
         "projects/smart_glasses/HW/SCHEMATIC_V1.md"]
ok = bad = 0
for f in files:
    if not os.path.exists(os.path.join(pub, f)):
        print(f"  ⏭  {f} (本地没有, 跳过)")
        continue
    local = subprocess.run(["git", "-C", pub, "rev-parse", f"HEAD:{f}"], capture_output=True, text=True).stdout.strip()
    # ★权威基准 = git 协议的远端树 (origin/main:<file>), 不吃 CDN/API 缓存, 也不吃 API 限流
    tree = subprocess.run(["git", "-C", pub, "rev-parse", f"origin/main:{f}"], capture_output=True, text=True).stdout.strip()
    try:
        # ★加 cache-buster: GitHub contents API 会缓存刚推的文件的 blob sha
        #   (2026-10-27 实测: 推送后 contents API 返回上一版的 sha → 误报 3 个文件不一致;
        #    git ls-remote + git rev-parse origin/main:<file> 与加 _= 后重查都证明远端是对的)
        remote = gh(f"/contents/{f}?ref=main&_={int(time.time()*1000)}").get("sha", "")
    except Exception as e:
        msg = str(e)
        if "403" in msg or "rate limit" in msg.lower():
            print(f"  ⏭  {f} (API 限流 → 用 git 远端树判定)")
            same = (local == tree and local != "")
            ok += same
            bad += (not same)
            print(f"  {'✅' if same else '❌'} {f}  local={local[:8]} tree={tree[:8]} (git 协议)")
            continue
        print(f"  ❌ {f} → API 取不到: {e}")
        bad += 1
        continue
    same = (local == remote == tree)
    ok += same
    bad += (not same)
    print(f"  {'✅' if same else '❌'} {f}  local={local[:8]} api={remote[:8]} tree={tree[:8]}")
if ok == 0 and bad == 0:
    print("验证: 逐文件 blob SHA 校验已跳过 (GitHub API 限流) —— 远端一致性由上面的 ls-remote 硬校验保证")
else:
    print(f"验证: {ok} 一致 / {bad} 不一致")
sys.exit(1 if bad else 0)
PY
