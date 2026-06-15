#!/bin/bash
# 高岸ERP — 数据库备份脚本
# 使用: ./scripts/backup.sh
# 建议添加到 crontab: 0 3 * * * /app/scripts/backup.sh

set -e

# 配置
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_FILE="${DB_FILE:-./gaoan_erp.db}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

# 1. SQLite 数据库备份（文件级）
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "${BACKUP_DIR}/gaoan_erp_${TIMESTAMP}.db"
    echo "✅ 数据库备份: gaoan_erp_${TIMESTAMP}.db"
    # 压缩
    gzip -f "${BACKUP_DIR}/gaoan_erp_${TIMESTAMP}.db"
    echo "✅ 已压缩: gaoan_erp_${TIMESTAMP}.db.gz"
else
    echo "⚠ 数据库文件不存在: $DB_FILE"
fi

# 2. 上传文件备份
if [ -d "./uploads" ]; then
    tar -czf "${BACKUP_DIR}/uploads_${TIMESTAMP}.tar.gz" ./uploads/
    echo "✅ 上传文件备份: uploads_${TIMESTAMP}.tar.gz"
fi

# 3. 日志备份
if [ -d "./logs" ]; then
    tar -czf "${BACKUP_DIR}/logs_${TIMESTAMP}.tar.gz" ./logs/
    echo "✅ 日志备份: logs_${TIMESTAMP}.tar.gz"
fi

# 4. 清理过期备份
if [ "$RETENTION_DAYS" -gt 0 ]; then
    find "$BACKUP_DIR" -name "gaoan_erp_*.db.gz" -mtime "+$RETENTION_DAYS" -delete
    find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime "+$RETENTION_DAYS" -delete
    find "$BACKUP_DIR" -name "logs_*.tar.gz" -mtime "+$RETENTION_DAYS" -delete
    echo "✅ 已清理 ${RETENTION_DAYS} 天前的备份"
fi

echo ""
echo "📊 备份统计:"
ls -lh "${BACKUP_DIR}/" 2>/dev/null | tail -5
echo ""
echo "✨ 备份完成: ${TIMESTAMP}"
