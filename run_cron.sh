#!/usr/bin/env bash
# cron 入口 wrapper
# 用法: run_cron.sh pipeline | refresh
#
# cron 默认环境非常简陋 (无 PATH 无 HOME 无 locale),
# 这里显式提供运行所需的一切, 并把 stdout/stderr 写到日志文件。
set -euo pipefail

PROJECT_DIR="/Users/nextderboy/Projects/商标数据"
LOG_DIR="$PROJECT_DIR/cron_logs"
mkdir -p "$LOG_DIR"

# 完整 PATH: homebrew (python3, lark-cli, postgres), 用户 bin
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Users/nextderboy/.local/bin"
export HOME="/Users/nextderboy"
# 中文路径需要 UTF-8 locale
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

cd "$PROJECT_DIR"
# shellcheck disable=SC1091
source venv_lark/bin/activate

ACTION="${1:-}"
if [[ -z "$ACTION" ]]; then
    echo "用法: $0 pipeline|refresh" >&2
    exit 1
fi

DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/${ACTION}_${DATE}.log"

# 写头部信息到日志
{
    echo "===== $ACTION 开始 $(date '+%Y-%m-%d %H:%M:%S') ====="
    echo "PWD: $(pwd)"
    echo "PYTHON: $(which python3)"
    echo "LARK-CLI: $(which lark-cli 2>/dev/null || echo NOT_FOUND)"
    echo ""
} >> "$LOG_FILE"

case "$ACTION" in
    pipeline)
        # 日常增量: 飞书 → DB → 匹配 → 推送
        python3 lark_pipeline.py >> "$LOG_FILE" 2>&1
        RC=$?
        ;;
    refresh)
        # 周度全量: 重查所有公司的 USPTO 商标 → 推送品牌依赖表
        python3 lark_refresh_brands.py >> "$LOG_FILE" 2>&1
        RC=$?
        ;;
    *)
        echo "未知 action: $ACTION (支持 pipeline / refresh)" >&2
        exit 1
        ;;
esac

{
    echo ""
    echo "===== $ACTION 结束 $(date '+%Y-%m-%d %H:%M:%S') RC=$RC ====="
} >> "$LOG_FILE"

# 保留最近 30 天的日志
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true

exit $RC
