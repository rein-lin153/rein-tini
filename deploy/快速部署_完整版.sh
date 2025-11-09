#!/bin/bash
# 心语时光 - 完整部署脚本（一键执行）
# 项目路径: /home/opc/rein-tini

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/home/opc/rein-tini"

echo "========================================="
echo "  心语时光 - 完整部署脚本"
echo "========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "$PROJECT_DIR/wsgi.py" ]; then
    echo -e "${RED}错误: 请确保项目位于 $PROJECT_DIR${NC}"
    exit 1
fi

cd $PROJECT_DIR

# ============================================
# Step 1: 检查系统环境
# ============================================
echo -e "${BLUE}[1/12] 检查系统环境...${NC}"
python3 --version || { echo -e "${RED}错误: 未安装 Python 3${NC}"; exit 1; }
echo -e "${GREEN}✓ Python 环境正常${NC}"

# ============================================
# Step 2: 安装系统依赖
# ============================================
echo -e "${BLUE}[2/12] 安装系统依赖...${NC}"
sudo yum install -y python3-devel gcc libjpeg-devel zlib-devel nginx > /dev/null 2>&1
echo -e "${GREEN}✓ 系统依赖已安装${NC}"

# ============================================
# Step 3: 配置环境变量
# ============================================
echo -e "${BLUE}[3/12] 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}创建 .env 文件...${NC}"
    cp env.example .env
    
    # 生成 SECRET_KEY
    SECRET_KEY=$(python3 -c "import os; print(os.urandom(24).hex())")
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
    
    # 设置数据库路径（绝对路径）
    sed -i "s|DATABASE_URI=sqlite:///instance/heartmoments.db|DATABASE_URI=sqlite:////home/opc/rein-tini/instance/heartmoments.db|" .env
    
    # 设置上传目录（绝对路径）
    sed -i "s|UPLOAD_FOLDER=uploads|UPLOAD_FOLDER=/home/opc/rein-tini/uploads|" .env
    
    # 设置生产环境
    sed -i "s|FLASK_ENV=development|FLASK_ENV=production|" .env
    sed -i "s|DEBUG=True|DEBUG=False|" .env
    
    echo -e "${YELLOW}⚠️  请手动编辑 .env 文件，修改以下配置：${NC}"
    echo "   - COUPLE_NAME_1: 你的名字"
    echo "   - COUPLE_NAME_2: 对方名字"
    echo "   - TOGETHER_DATE: 在一起的日期"
    echo ""
    echo "编辑命令: nano .env"
    echo ""
    read -p "按 Enter 继续（确保已修改配置）..."
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

# ============================================
# Step 4: 创建必要目录
# ============================================
echo -e "${BLUE}[4/12] 创建必要目录...${NC}"
mkdir -p instance uploads/photos uploads/thumbs logs backups
echo -e "${GREEN}✓ 目录创建完成${NC}"

# ============================================
# Step 5: 设置文件权限
# ============================================
echo -e "${BLUE}[5/12] 设置文件权限...${NC}"
sudo chown -R opc:opc $PROJECT_DIR
chmod 755 $PROJECT_DIR
chmod 755 instance uploads logs backups
chmod 755 uploads/photos uploads/thumbs
echo -e "${GREEN}✓ 权限设置完成${NC}"

# ============================================
# Step 6: 创建虚拟环境
# ============================================
echo -e "${BLUE}[6/12] 创建虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

# ============================================
# Step 7: 安装 Python 依赖
# ============================================
echo -e "${BLUE}[7/12] 安装 Python 依赖...${NC}"
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# ============================================
# Step 8: 初始化数据库
# ============================================
echo -e "${BLUE}[8/12] 初始化数据库...${NC}"
if [ ! -f "instance/heartmoments.db" ]; then
    python scripts/init_db.py
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
    
    echo ""
    echo -e "${YELLOW}现在创建管理员账号...${NC}"
    python scripts/create_admin.py
else
    echo -e "${GREEN}✓ 数据库已存在，跳过初始化${NC}"
fi

# ============================================
# Step 9: 配置 Systemd 服务
# ============================================
echo -e "${BLUE}[9/12] 配置 Systemd 服务...${NC}"
if [ -f "deploy/heartmoments.service" ]; then
    sudo cp deploy/heartmoments.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo -e "${GREEN}✓ Systemd 服务已配置${NC}"
else
    echo -e "${RED}错误: deploy/heartmoments.service 文件不存在${NC}"
    exit 1
fi

# ============================================
# Step 10: 配置 Nginx
# ============================================
echo -e "${BLUE}[10/12] 配置 Nginx...${NC}"
if [ -f "deploy/nginx.conf" ]; then
    sudo cp deploy/nginx.conf /etc/nginx/conf.d/heartmoments.conf
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
    
    echo -e "${YELLOW}当前服务器IP: $SERVER_IP${NC}"
    echo -e "${YELLOW}请确认 Nginx 配置中的 server_name${NC}"
    echo ""
    read -p "按 Enter 继续（稍后可以修改 /etc/nginx/conf.d/heartmoments.conf）..."
    
    # 测试 Nginx 配置
    if sudo nginx -t > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Nginx 配置正确${NC}"
    else
        echo -e "${RED}警告: Nginx 配置可能有误，请检查${NC}"
        sudo nginx -t
    fi
else
    echo -e "${RED}错误: deploy/nginx.conf 文件不存在${NC}"
    exit 1
fi

# ============================================
# Step 11: 配置防火墙
# ============================================
echo -e "${BLUE}[11/12] 配置防火墙...${NC}"
if sudo firewall-cmd --state > /dev/null 2>&1; then
    sudo firewall-cmd --permanent --add-service=http > /dev/null 2>&1
    sudo firewall-cmd --reload > /dev/null 2>&1
    echo -e "${GREEN}✓ 防火墙已配置${NC}"
else
    echo -e "${YELLOW}防火墙未运行，跳过${NC}"
fi

# ============================================
# Step 12: 启动服务
# ============================================
echo -e "${BLUE}[12/12] 启动服务...${NC}"

# 启动 Gunicorn
echo "启动 Gunicorn..."
sudo systemctl start heartmoments
sudo systemctl enable heartmoments

# 检查 Gunicorn 状态
if sudo systemctl is-active --quiet heartmoments; then
    echo -e "${GREEN}✓ Gunicorn 服务已启动${NC}"
else
    echo -e "${RED}错误: Gunicorn 启动失败${NC}"
    echo "查看日志: sudo journalctl -u heartmoments -n 50"
    exit 1
fi

# 启动 Nginx
echo "启动 Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# 检查 Nginx 状态
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx 服务已启动${NC}"
else
    echo -e "${RED}错误: Nginx 启动失败${NC}"
    echo "查看日志: sudo tail -f /var/log/nginx/error.log"
    exit 1
fi

# ============================================
# 部署完成
# ============================================
echo ""
echo -e "${GREEN}========================================="
echo "  部署完成！"
echo "=========================================${NC}"
echo ""

# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')

echo -e "${GREEN}访问地址: http://$SERVER_IP${NC}"
echo ""
echo "服务状态："
echo "  - Gunicorn: $(sudo systemctl is-active heartmoments)"
echo "  - Nginx: $(sudo systemctl is-active nginx)"
echo ""
echo "常用命令："
echo "  查看服务状态: sudo systemctl status heartmoments"
echo "  查看日志: tail -f logs/gunicorn-error.log"
echo "  重启服务: sudo systemctl restart heartmoments"
echo "  重启 Nginx: sudo systemctl restart nginx"
echo ""
echo -e "${YELLOW}提醒：${NC}"
echo "  1. 确保已修改 .env 文件中的情侣信息"
echo "  2. 确保已创建管理员账号"
echo "  3. 如有域名，修改 Nginx 配置中的 server_name"
echo "  4. 建议配置 HTTPS（使用 Certbot）"
echo ""


