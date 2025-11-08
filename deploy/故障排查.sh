#!/bin/bash
# 故障排查脚本 - 收集诊断信息

echo "==========================================="
echo "  心语时光 - 故障诊断信息收集"
echo "==========================================="
echo ""

# 颜色定义
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 服务状态
echo -e "${BLUE}=== 1. 服务状态 ===${NC}"
echo "--- Gunicorn ---"
sudo systemctl status heartmoments --no-pager | head -20
echo ""
echo "--- Nginx ---"
sudo systemctl status nginx --no-pager | head -20
echo ""

# 2. 最近的日志
echo -e "${BLUE}=== 2. 最近的日志 ===${NC}"
echo "--- Gunicorn 错误日志 ---"
tail -n 20 /home/opc/rein-tini/logs/gunicorn-error.log 2>/dev/null || echo "日志文件不存在"
echo ""
echo "--- Systemd 日志 ---"
sudo journalctl -u heartmoments -n 20 --no-pager
echo ""

# 3. 文件权限
echo -e "${BLUE}=== 3. 文件权限 ===${NC}"
echo "--- 项目目录 ---"
ls -la /home/opc/rein-tini/ | head -20
echo ""
echo "--- instance 目录 ---"
ls -la /home/opc/rein-tini/instance/
echo ""
echo "--- uploads 目录 ---"
ls -la /home/opc/rein-tini/uploads/
echo ""

# 4. Socket 文件
echo -e "${BLUE}=== 4. Socket 文件 ===${NC}"
ls -la /home/opc/rein-tini/*.sock 2>/dev/null || echo "Socket 文件不存在"
echo ""

# 5. 端口监听
echo -e "${BLUE}=== 5. 端口监听 ===${NC}"
sudo netstat -tlnp | grep -E "nginx|gunicorn|:80|:443"
echo ""

# 6. 磁盘空间
echo -e "${BLUE}=== 6. 磁盘空间 ===${NC}"
df -h
echo ""

# 7. 内存使用
echo -e "${BLUE}=== 7. 内存使用 ===${NC}"
free -h
echo ""

# 8. 进程信息
echo -e "${BLUE}=== 8. 运行进程 ===${NC}"
ps aux | grep -E "gunicorn|nginx" | grep -v grep
echo ""

# 9. SELinux 状态
echo -e "${BLUE}=== 9. SELinux 状态 ===${NC}"
getenforce
echo ""

# 10. 防火墙状态
echo -e "${BLUE}=== 10. 防火墙状态 ===${NC}"
sudo firewall-cmd --list-all 2>/dev/null || echo "Firewalld 未运行"
echo ""

# 11. Nginx 配置测试
echo -e "${BLUE}=== 11. Nginx 配置测试 ===${NC}"
sudo nginx -t
echo ""

# 12. 环境变量检查
echo -e "${BLUE}=== 12. 环境变量 ===${NC}"
if [ -f /home/opc/rein-tini/.env ]; then
    echo "FLASK_ENV=$(grep FLASK_ENV /home/opc/rein-tini/.env)"
    echo "DATABASE_URI=$(grep DATABASE_URI /home/opc/rein-tini/.env)"
    echo "UPLOAD_FOLDER=$(grep UPLOAD_FOLDER /home/opc/rein-tini/.env)"
else
    echo ".env 文件不存在！"
fi
echo ""

# 13. Python 版本
echo -e "${BLUE}=== 13. Python 版本 ===${NC}"
/home/opc/rein-tini/venv/bin/python --version
echo ""

echo "==========================================="
echo "  诊断信息收集完成"
echo "==========================================="
echo ""
echo "如果需要进一步帮助，请将以上信息提供给开发者。"

