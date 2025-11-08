#!/bin/bash
# 心语时光 - 备份脚本
# 自动备份数据库和上传文件

# 配置
PROJECT_DIR="/var/www/heartmoments"
BACKUP_DIR="${PROJECT_DIR}/backups"
DB_FILE="${PROJECT_DIR}/instance/heartmoments.db"
UPLOADS_DIR="${PROJECT_DIR}/uploads"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="heartmoments_backup_${DATE}"
RETENTION_DAYS=30

# 确保备份目录存在
mkdir -p "${BACKUP_DIR}"

echo "================================"
echo "💖 心语时光 - 开始备份"
echo "================================"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "备份名称: ${BACKUP_NAME}"
echo "================================"

# 创建临时目录
TEMP_DIR="/tmp/${BACKUP_NAME}"
mkdir -p "${TEMP_DIR}"

# 1. 备份数据库
echo "📦 正在备份数据库..."
if [ -f "${DB_FILE}" ]; then
    cp "${DB_FILE}" "${TEMP_DIR}/heartmoments.db"
    echo "✓ 数据库备份完成"
else
    echo "❌ 数据库文件不存在: ${DB_FILE}"
    exit 1
fi

# 2. 备份上传文件
echo "📦 正在备份上传文件..."
if [ -d "${UPLOADS_DIR}" ]; then
    cp -r "${UPLOADS_DIR}" "${TEMP_DIR}/"
    echo "✓ 上传文件备份完成"
else
    echo "⚠️  上传目录不存在，跳过"
fi

# 3. 备份环境配置（不包含敏感信息）
echo "📦 正在备份配置信息..."
if [ -f "${PROJECT_DIR}/.env.example" ]; then
    cp "${PROJECT_DIR}/.env.example" "${TEMP_DIR}/"
fi

# 4. 压缩备份
echo "🗜️  正在压缩备份文件..."
cd /tmp
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo "✓ 压缩完成，大小: ${BACKUP_SIZE}"

# 5. 清理临时文件
rm -rf "${TEMP_DIR}"

# 6. 删除过期备份
echo "🧹 正在清理过期备份 (保留 ${RETENTION_DAYS} 天)..."
find "${BACKUP_DIR}" -name "heartmoments_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete
REMAINING_COUNT=$(ls -1 "${BACKUP_DIR}"/heartmoments_backup_*.tar.gz 2>/dev/null | wc -l)
echo "✓ 当前保留备份数量: ${REMAINING_COUNT}"

echo "================================"
echo "✓ 备份完成！"
echo "================================"
echo "备份文件: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "文件大小: ${BACKUP_SIZE}"
echo "================================"

# 7. 可选：上传到远程服务器或云存储
# 示例：使用 rsync 上传到远程服务器
# rsync -avz "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" user@remote:/path/to/backup/

# 示例：使用 rclone 上传到云存储
# rclone copy "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" remote:heartmoments-backup/

exit 0

