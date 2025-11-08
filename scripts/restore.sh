#!/bin/bash
# 心语时光 - 恢复脚本
# 从备份文件恢复数据

# 配置
PROJECT_DIR="/var/www/heartmoments"
DB_FILE="${PROJECT_DIR}/instance/heartmoments.db"
UPLOADS_DIR="${PROJECT_DIR}/uploads"

# 检查参数
if [ -z "$1" ]; then
    echo "用法: $0 <备份文件路径>"
    echo "示例: $0 backups/heartmoments_backup_20250108_030000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

# 检查备份文件是否存在
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ 错误: 备份文件不存在: ${BACKUP_FILE}"
    exit 1
fi

echo "================================"
echo "💖 心语时光 - 开始恢复"
echo "================================"
echo "备份文件: ${BACKUP_FILE}"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================"

# 确认操作
read -p "⚠️  警告: 此操作将覆盖现有数据，是否继续？(yes/NO): " confirm
if [ "$confirm" != "yes" ]; then
    echo "已取消恢复操作"
    exit 0
fi

# 备份当前数据（以防万一）
SAFETY_BACKUP="/tmp/heartmoments_safety_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
echo "🔒 创建安全备份..."
mkdir -p /tmp/safety_backup
if [ -f "${DB_FILE}" ]; then
    cp "${DB_FILE}" /tmp/safety_backup/
fi
if [ -d "${UPLOADS_DIR}" ]; then
    cp -r "${UPLOADS_DIR}" /tmp/safety_backup/
fi
tar -czf "${SAFETY_BACKUP}" -C /tmp safety_backup
rm -rf /tmp/safety_backup
echo "✓ 安全备份已保存至: ${SAFETY_BACKUP}"

# 解压备份文件
TEMP_DIR="/tmp/restore_$(date +%s)"
mkdir -p "${TEMP_DIR}"
echo "📦 正在解压备份文件..."
tar -xzf "${BACKUP_FILE}" -C "${TEMP_DIR}"

# 查找解压后的目录
BACKUP_CONTENT=$(ls -1 "${TEMP_DIR}" | head -1)
RESTORE_FROM="${TEMP_DIR}/${BACKUP_CONTENT}"

if [ ! -d "${RESTORE_FROM}" ]; then
    echo "❌ 错误: 无效的备份文件格式"
    rm -rf "${TEMP_DIR}"
    exit 1
fi

# 恢复数据库
if [ -f "${RESTORE_FROM}/heartmoments.db" ]; then
    echo "🗄️  正在恢复数据库..."
    mkdir -p "${PROJECT_DIR}/instance"
    cp "${RESTORE_FROM}/heartmoments.db" "${DB_FILE}"
    chmod 644 "${DB_FILE}"
    echo "✓ 数据库恢复完成"
else
    echo "⚠️  备份中未找到数据库文件"
fi

# 恢复上传文件
if [ -d "${RESTORE_FROM}/uploads" ]; then
    echo "📁 正在恢复上传文件..."
    rm -rf "${UPLOADS_DIR}"
    cp -r "${RESTORE_FROM}/uploads" "${UPLOADS_DIR}"
    chmod -R 755 "${UPLOADS_DIR}"
    echo "✓ 上传文件恢复完成"
else
    echo "⚠️  备份中未找到上传文件目录"
fi

# 清理临时文件
rm -rf "${TEMP_DIR}"

echo "================================"
echo "✓ 恢复完成！"
echo "================================"
echo "安全备份保存在: ${SAFETY_BACKUP}"
echo "如果恢复出现问题，可使用此备份还原"
echo "================================"

# 重启服务（可选）
if command -v systemctl &> /dev/null; then
    read -p "是否重启应用服务？(y/N): " restart
    if [ "$restart" = "y" ] || [ "$restart" = "Y" ]; then
        echo "🔄 正在重启服务..."
        sudo systemctl restart heartmoments
        echo "✓ 服务已重启"
    fi
fi

exit 0

