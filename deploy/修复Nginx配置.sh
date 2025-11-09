#!/bin/bash
# 修复 Nginx 配置 - 解决默认欢迎页面问题

set -e

echo "========================================="
echo "  修复 Nginx 配置"
echo "========================================="
echo ""

cd /home/opc/rein-tini

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: 检查 Gunicorn
echo -e "${YELLOW}[1/5] 检查 Gunicorn 服务...${NC}"
if sudo systemctl is-active --quiet heartmoments; then
    echo -e "${GREEN}✓ Gunicorn 正在运行${NC}"
else
    echo -e "${YELLOW}启动 Gunicorn...${NC}"
    sudo systemctl start heartmoments
    sleep 2
    if sudo systemctl is-active --quiet heartmoments; then
        echo -e "${GREEN}✓ Gunicorn 已启动${NC}"
    else
        echo -e "${RED}✗ Gunicorn 启动失败${NC}"
        echo "查看日志: sudo journalctl -u heartmoments -n 50"
        exit 1
    fi
fi

# 检查 Socket 文件
if [ -S "/home/opc/rein-tini/heartmoments.sock" ]; then
    echo -e "${GREEN}✓ Socket 文件存在${NC}"
else
    echo -e "${RED}✗ Socket 文件不存在${NC}"
    exit 1
fi

# Step 2: 配置 Nginx
echo ""
echo -e "${YELLOW}[2/5] 配置 Nginx...${NC}"
if [ -f "deploy/nginx.conf" ]; then
    sudo cp deploy/nginx.conf /etc/nginx/conf.d/heartmoments.conf
    echo -e "${GREEN}✓ 配置文件已复制${NC}"
else
    echo -e "${RED}✗ deploy/nginx.conf 文件不存在${NC}"
    exit 1
fi

# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}' || echo "localhost")
echo "服务器IP: $SERVER_IP"

# 修改 server_name
sudo sed -i "s/server_name _;/server_name $SERVER_IP localhost;/" /etc/nginx/conf.d/heartmoments.conf
echo -e "${GREEN}✓ server_name 已设置为: $SERVER_IP localhost${NC}"

# Step 3: 禁用默认站点
echo ""
echo -e "${YELLOW}[3/5] 禁用默认 Nginx 站点...${NC}"
if [ -f "/etc/nginx/conf.d/default.conf" ]; then
    sudo mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak
    echo -e "${GREEN}✓ 默认配置已备份为 default.conf.bak${NC}"
else
    echo -e "${YELLOW}默认配置文件不存在，跳过${NC}"
fi

# Step 4: 测试配置
echo ""
echo -e "${YELLOW}[4/5] 测试 Nginx 配置...${NC}"
if sudo nginx -t > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Nginx 配置正确${NC}"
else
    echo -e "${RED}✗ Nginx 配置有误${NC}"
    sudo nginx -t
    exit 1
fi

# Step 5: 重启 Nginx
echo ""
echo -e "${YELLOW}[5/5] 重启 Nginx...${NC}"
sudo systemctl restart nginx
sleep 2

if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx 已重启${NC}"
else
    echo -e "${RED}✗ Nginx 启动失败${NC}"
    sudo systemctl status nginx
    exit 1
fi

# 验证
echo ""
echo -e "${YELLOW}验证配置...${NC}"
sleep 2

RESPONSE=$(curl -s http://localhost 2>/dev/null | head -5)

if echo "$RESPONSE" | grep -q "Welcome to nginx"; then
    echo -e "${RED}✗ 仍然显示 Nginx 欢迎页面${NC}"
    echo "可能的原因："
    echo "  1. 还有其他配置文件在拦截请求"
    echo "  2. 需要检查 /etc/nginx/nginx.conf"
    echo ""
    echo "请检查: ls -la /etc/nginx/conf.d/"
    exit 1
elif echo "$RESPONSE" | grep -q "html\|<!DOCTYPE"; then
    echo -e "${GREEN}✓ 配置成功！网站正常响应${NC}"
    echo ""
    echo "访问测试:"
    curl -s http://localhost | head -10
else
    echo -e "${YELLOW}⚠ 响应内容异常，请手动检查${NC}"
    echo "响应内容:"
    echo "$RESPONSE"
fi

echo ""
echo -e "${GREEN}========================================="
echo "  修复完成！"
echo "=========================================${NC}"
echo ""
echo "访问地址: http://$SERVER_IP"
echo "本地测试: curl http://localhost"
echo ""
echo "如果还有问题，请查看："
echo "  - Nginx 错误日志: sudo tail -f /var/log/nginx/error.log"
echo "  - Gunicorn 日志: tail -f /home/opc/rein-tini/logs/gunicorn-error.log"
echo ""


