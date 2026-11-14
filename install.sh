#!/usr/bin/env bash
# qwork skill 一键安装/更新脚本（多 agent 目标）
# 用法:
#   交互选择: curl -fsSL https://gitee.com/GreatBigM/qwork-skill/raw/main/install.sh -o /tmp/install.sh && bash /tmp/install.sh
#   指定目标: curl -fsSL https://gitee.com/GreatBigM/qwork-skill/raw/main/install.sh | bash -s -- --target hermes,claude,zcode,dsh
#   全部目标: curl -fsSL https://gitee.com/GreatBigM/qwork-skill/raw/main/install.sh | bash -s -- --all
#   本仓安装: bash install.sh --local --target dsh      # 用当前 checkout，不克隆远端（开发/验证）
#   漂移校验: bash install.sh --check                   # 只对比安装副本与本仓清单，不写文件
# 等价于手动复制，不经过安全扫描。重复执行 = 更新（自动备份旧版 + 版本对比）
# 镜像: github.com/GreatBigM/qwork-skill（海外备选）
set -euo pipefail

REPO_URL="https://gitee.com/GreatBigM/qwork-skill.git"
SKILL_NAME="qwork"

# ── 安装面单一清单（拷贝与 --check 共用；README / SKILL 的清单以此为准）──
INSTALL_FILES=(SKILL.md SCHEMA.md CHANGELOG.md)
INSTALL_DIRS=(templates references examples)
LOCAL_OVERLAY="references/local"   # 本机扩展：升级时保留，不随上游覆盖

usage() {
    cat <<'EOF'
用法: install.sh [--target a,b] [--all] [--local] [--check]
  --target  指定目标（逗号分隔: hermes / claude / codex / zcode / dsh）
  --all     安装到全部检测到的 agent
  --local   用当前 checkout 安装（开发/验证用，不克隆远端）
  --check   只校验已安装副本与本仓清单是否一致，不写文件
EOF
}

get_version() { grep -m1 '^version:' "$1" 2>/dev/null | sed 's/^version:[[:space:]]*//' | tr -d '"'\'' ' || true; }
version_gt() { [ "$1" != "$2" ] && [ -n "$2" ] && [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]; }

# ─── 参数解析 ──────────────────────────────────────────────────────
TARGET_ARG=""
ALL_FLAG=0
WANT_TARGET=0
USE_LOCAL=0
MODE="install"
for a in "$@"; do
    if [ "$WANT_TARGET" -eq 1 ]; then TARGET_ARG="$a"; WANT_TARGET=0; continue; fi
    case "$a" in
        --target=*) TARGET_ARG="${a#*=}" ;;
        --target) WANT_TARGET=1 ;;   # 空格形式：--target hermes,claude
        --all) ALL_FLAG=1 ;;
        --local) USE_LOCAL=1 ;;
        --check) MODE="check" ;;
        -h|--help) usage; exit 0 ;;
        *) echo "❌ 未知参数: $a" >&2; usage >&2; exit 1 ;;
    esac
done
if [ "$WANT_TARGET" -eq 1 ]; then
    echo "❌ --target 缺参数（用法：--target hermes,claude 或 --target=hermes,claude）" >&2
    exit 1
fi

# ─── 目标探测：检测本机已安装的 agent ───────────────────────────────
detect_targets() {
    TARGETS=()   # 格式: 名称|目录|CLI
    if [ -x "$(command -v hermes 2>/dev/null)" ]; then TARGETS+=("hermes|${HOME}/.hermes/skills|Hermes"); fi
    if [ -x "$(command -v claude 2>/dev/null)" ]; then TARGETS+=("claude|${HOME}/.claude/skills|Claude Code"); fi
    if [ -x "$(command -v codex 2>/dev/null)" ]; then TARGETS+=("codex|${HOME}/.codex/skills|Codex"); fi
    if [ -d "${HOME}/.zcode" ]; then TARGETS+=("zcode|${HOME}/.zcode/skills|ZCode"); fi
    if [ -x "$(command -v dsh 2>/dev/null)" ]; then TARGETS+=("dsh|${HOME}/.dsh/skills|DeepSeek Harness"); fi
    # Cursor 用 skills-cursor 插件结构，暂不支持；其余 agent 未探测到
    if [ "${#TARGETS[@]}" -eq 0 ]; then
        TARGETS+=("hermes|${HOME}/.hermes/skills|Hermes(默认)")
    fi
}

# ─── 单目标安装（版本对比 + 备份 + 拷贝 + 保留本机扩展）────────────
install_one() {
    local label="$1" dest="$2"
    local dest_dir; dest_dir="$(dirname "$dest")"
    local bak=""

    echo ""
    echo "── 安装到 ${label} (${dest}) ──"
    mkdir -p "$dest_dir"

    if [ -f "${dest}/SKILL.md" ]; then
        local old_v; old_v="$(get_version "${dest}/SKILL.md")"
        if [ -n "$old_v" ] && [ -n "$NEW_VERSION" ]; then
            if version_gt "$NEW_VERSION" "$old_v"; then
                echo "    发现新版本: v${old_v} → v${NEW_VERSION}，正在升级..."
            elif [ "$old_v" = "$NEW_VERSION" ]; then
                echo "    已是最新版本 v${NEW_VERSION}（重新安装，旧版备份保留）"
            else
                echo "    本地 v${old_v} 高于源 v${NEW_VERSION}（开发版，覆盖安装）"
            fi
        fi
        # 备份必须落在 skills 扫描根之外：agent 按「含 SKILL.md 的目录」发现技能、不看目录名，
        # 备份留在扫描根内会被当成第二个同名技能加载（重名歧义 → 静默跳过其一）
        local bak_dir="${dest_dir%/skills}/skills-backup"
        mkdir -p "$bak_dir"
        bak="${bak_dir}/${SKILL_NAME}.bak.$(date +%Y%m%d%H%M%S)"
        echo "    备份旧版到 ${bak}"
        mv "$dest" "$bak"
    else
        echo "    首次安装 v${NEW_VERSION}"
    fi

    mkdir -p "$dest"
    local f d
    for f in "${INSTALL_FILES[@]}"; do
        [ -f "${SRC}/${f}" ] && cp "${SRC}/${f}" "${dest}/"
    done
    for d in "${INSTALL_DIRS[@]}"; do
        [ -d "${SRC}/${d}" ] && cp -R "${SRC}/${d}" "${dest}/"
    done

    if [ -n "$bak" ] && [ -d "${bak}/${LOCAL_OVERLAY}" ]; then
        mkdir -p "${dest}/${LOCAL_OVERLAY}"
        cp -R "${bak}/${LOCAL_OVERLAY}/." "${dest}/${LOCAL_OVERLAY}/"
        echo "    保留本机扩展 ${LOCAL_OVERLAY}/（来自备份）"
    fi
    echo "    ✅ ${label}: ${SKILL_NAME} v${NEW_VERSION} 已安装"
}

# ─── 单目标校验（安装副本 vs 源清单，不写文件）──────────────────────
check_one() {
    local label="$1" dest="$2"
    local problems=0 f d out dst_v

    echo ""
    echo "── 校验 ${label} (${dest}) ──"
    if [ ! -f "${dest}/SKILL.md" ]; then
        echo "    ✗ 未安装"
        return 1
    fi

    for f in "${INSTALL_FILES[@]}"; do
        [ -f "${SRC}/${f}" ] || continue
        if ! cmp -s "${SRC}/${f}" "${dest}/${f}"; then
            echo "    ✗ ${f} 缺失或内容不一致"
            problems=$((problems + 1))
        fi
    done
    for d in "${INSTALL_DIRS[@]}"; do
        [ -d "${SRC}/${d}" ] || continue
        out="$(diff -rq --exclude=local "${SRC}/${d}" "${dest}/${d}" 2>&1 || true)"
        if [ -n "$out" ]; then
            printf '%s\n' "$out" | sed 's/^/    ✗ /'
            problems=$((problems + 1))
        fi
    done

    dst_v="$(get_version "${dest}/SKILL.md")"
    if [ -n "$dst_v" ] && [ "$dst_v" != "$NEW_VERSION" ]; then
        echo "    ✗ 版本不一致：已装 v${dst_v}，源 v${NEW_VERSION}"
        problems=$((problems + 1))
    fi

    if [ "$problems" -eq 0 ]; then
        echo "    ✅ 一致 v${dst_v}"
        return 0
    fi
    return 1
}

# ─── 主流程 ────────────────────────────────────────────────────────
TMP=""
cleanup() { [ -z "${TMP}" ] || rm -rf "${TMP}"; return 0; }
trap cleanup EXIT

if [ "$USE_LOCAL" -eq 1 ]; then
    SRC="$(cd "$(dirname "$0")" && pwd)"
    [ -f "${SRC}/SKILL.md" ] || { echo "❌ --local 需在本仓内执行（${SRC} 无 SKILL.md）" >&2; exit 1; }
    echo "==> 使用本地 checkout: ${SRC}"
else
    TMP="$(mktemp -d)"
    echo "==> 克隆仓库（--depth 1）..."
    git clone --depth 1 "${REPO_URL}" "${TMP}/repo" >/dev/null 2>&1 || {
        echo "❌ 克隆失败，请检查网络或仓库地址"; exit 1; }
    SRC="${TMP}/repo"
    echo "    远端版本 v$(get_version "${SRC}/SKILL.md")"
fi
NEW_VERSION="$(get_version "${SRC}/SKILL.md")"

detect_targets

echo ""
echo "==> 检测到本机 agent:"
for i in "${!TARGETS[@]}"; do
    name="${TARGETS[$i]%%|*}"; dir="${TARGETS[$i]#*|}"; dir="${dir%%|*}"
    state="➕ 未安装"
    [ -f "${dir}/${SKILL_NAME}/SKILL.md" ] && state="✅ 已装 v$(get_version "${dir}/${SKILL_NAME}/SKILL.md")"
    echo "    [$((i+1))] ${TARGETS[$i]##*|}  (${dir})  ${state}"
done

# ─── 目标选择 ──────────────────────────────────────────────────────
SELECTED=()
if [ "$ALL_FLAG" -eq 1 ]; then
    SELECTED=("${TARGETS[@]}")
elif [ -n "$TARGET_ARG" ]; then
    IFS=',' read -ra want <<< "$TARGET_ARG"
    for w in "${want[@]}"; do
        for t in "${TARGETS[@]}"; do
            [ "${t%%|*}" = "$w" ] && SELECTED+=("$t")
        done
    done
    [ "${#SELECTED[@]}" -eq 0 ] && { echo "❌ 未知目标: $TARGET_ARG（可用: hermes/claude/codex/zcode/dsh）"; exit 1; }
elif [ -t 0 ]; then
    # 交互模式（stdin 是终端）
    echo ""
    read -rp "选择目标（逗号分隔如 1,2 / 1-3 / 回车=全部 / q=退出）: " choice
    if [ "${choice,,}" = "q" ]; then echo "已取消"; exit 0; fi
    if [ -z "$choice" ]; then
        SELECTED=("${TARGETS[@]}")
    else
        IFS=', ' read -ra parts <<< "$choice"
        for p in "${parts[@]}"; do
            if [[ "$p" =~ ^[0-9]+-[0-9]+$ ]]; then
                a="${p%-*}"; b="${p#*-}"
                for ((n=a; n<=b; n++)); do
                    [ "$n" -ge 1 ] && [ "$n" -le "${#TARGETS[@]}" ] && SELECTED+=("${TARGETS[$((n-1))]}")
                done
            elif [[ "$p" =~ ^[0-9]+$ ]] && [ "$p" -ge 1 ] && [ "$p" -le "${#TARGETS[@]}" ]; then
                SELECTED+=("${TARGETS[$((p-1))]}")
            fi
        done
        [ "${#SELECTED[@]}" -eq 0 ] && { echo "❌ 无效选择"; exit 1; }
    fi
else
    # 管道模式（stdin 非终端）: 默认全部
    echo ""
    echo "==> 非交互模式（管道执行），默认安装到全部目标"
    SELECTED=("${TARGETS[@]}")
fi

# ─── 执行安装 / 校验 ───────────────────────────────────────────────
FAIL=0
for t in "${SELECTED[@]}"; do
    name="${t%%|*}"; rest="${t#*|}"; dir="${rest%%|*}"; label="${t##*|}"
    dest="${dir}/${SKILL_NAME}"
    if [ "$MODE" = "check" ]; then
        check_one "$label" "$dest" || FAIL=1
    else
        install_one "$label" "$dest"
    fi
done

echo ""
if [ "$MODE" = "check" ]; then
    if [ "$FAIL" -eq 0 ]; then
        echo "✅ 校验通过：安装副本与 ${SRC} 清单一致"
    else
        echo "✗ 存在漂移（见上）。重跑 install.sh 覆盖安装可修复；本机扩展 references/local/ 会被保留。"
        exit 1
    fi
else
    echo "✅ ${SKILL_NAME} v${NEW_VERSION} 安装完成！"
    echo "   - Hermes: 新会话自动加载，当前会话 /reload-skills 生效"
    echo "   - Claude Code / Codex / ZCode / DeepSeek Harness(dsh): 新会话自动加载"
    echo ""
    echo "快速开始：在项目代码仓创建 0_workbench/ 结构，按 change 四要素驱动任务"
    echo "本机扩展：把个人实践放 references/local/（升级保留，不随上游覆盖）"
    echo "校验漂移：bash install.sh --check"
    echo "更新：重跑本脚本即升级（自动备份旧版到 <tool 根>/skills-backup/，扫描根之外）"
    echo "指定目标：bash install.sh --target hermes,claude,zcode,dsh  或  --all"
fi
