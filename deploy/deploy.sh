#!/bin/bash
# HeartMoments 一键部署脚本
# 项目路径: /home/opc/rein-tini

set -e  # 遇到错误立即退出

echo "========================================="
echo "  心语时光 - 生产环境部署脚本"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/home/opc/rein-tini"

# 检查是否在正确的目录
if [ ! -f "$PROJECT_DIR/wsgi.py" ]; then
    echo -e "${RED}错误: 请确保项目位于 $PROJECT_DIR${NC}"
    exit 1
fi

cd $PROJECT_DIR

# Step 1: 检查 .env 文件
echo -e "${YELLOW}[1/9] 检查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    echo "请先复制 env.example 为 .env 并配置"
    exit 1
fi

# 检查 SECRET_KEY
if grep -q "SECRET_KEY=your-secret-key-here" .env; then
    echo -e "${RED}警告: 请修改 .env 中的 SECRET_KEY！${NC}"
    echo "运行: python3 -c \"import os; print(os.urandom(24).hex())\""
    exit 1
fi

echo -e "${GREEN}✓ 配置文件检查通过${NC}"

# Step 2: 创建必要的目录
echo -e "${YELLOW}[2/9] 创建必要目录...${NC}"
mkdir -p instance
mkdir -p uploads/photos
mkdir -p uploads/thumbs
mkdir -p logs
mkdir -p backups
echo -e "${GREEN}✓ 目录创建完成${NC}"

# Step 3: 设置权限
echo -e "${YELLOW}[3/9] 设置文件权限...${NC}"
chmod 755 $PROJECT_DIR
chmod 755 instance uploads logs backups
chmod 755 uploads/photos uploads/thumbs
chown -R opc:opc $PROJECT_DIR
echo -e "${GREEN}✓ 权限设置完成${NC}"

# Step 4: 创建虚拟环境（如果不存在）
echo -e "${YELLOW}[4/9] 检查虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境就绪${NC}"

# Step 5: 安装依赖
echo -e "${YELLOW}[5/9] 安装 Python 依赖...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# Step 6: 初始化数据库
echo -e "${YELLOW}[6/9] 初始化数据库...${NC}"
if [ ! -f "instance/heartmoments.db" ]; then
    python scripts/init_db.py
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
    echo -e "${YELLOW}请运行: python scripts/create_admin.py 创建管理员${NC}"
else
    echo -e "${GREEN}✓ 数据库已存在，跳过初始化${NC}"
fi

# Step 7: 安装 Systemd 服务
echo -e "${YELLOW}[7/9] 安装 Systemd 服务...${NC}"
if [ -f "deploy/heartmoments.service" ]; then
    sudo cp deploy/heartmoments.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo -e "${GREEN}✓ Systemd 服务已安装${NC}"
else
    echo -e "${RED}警告: deploy/heartmoments.service 文件不存在${NC}"
fi

# Step 8: 配置 Nginx
echo -e "${YELLOW}[8/9] 配置 Nginx...${NC}"
if [ -f "deploy/nginx.conf" ]; then
    sudo cp deploy/nginx.conf /etc/nginx/conf.d/heartmoments.conf
    echo -e "${YELLOW}请手动编辑 /etc/nginx/conf.d/heartmoments.conf${NC}"
    echo -e "${YELLOW}将 server_name 修改为你的域名或IP${NC}"
    echo -e "${GREEN}✓ Nginx 配置已复制${NC}"
else
    echo -e "${RED}警告: deploy/nginx.conf 文件不存在${NC}"
fi

# Step 9: 测试配置
echo -e "${YELLOW}[9/9] 测试配置...${NC}"
echo "测试 Nginx 配置..."
sudo nginx -t

echo ""
echo -e "${GREEN}========================================="
echo "  部署准备完成！"
echo "=========================================${NC}"
echo ""
echo "接下来的步骤："
echo ""
echo "1. 创建管理员账号："
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python scripts/create_admin.py"
echo ""
echo "2. 编辑 Nginx 配置："
echo "   sudo nano /etc/nginx/conf.d/heartmoments.conf"
echo "   (将 server_name 改为你的域名或IP)"
echo ""
echo "3. 启动服务："
echo "   sudo systemctl start heartmoments"
echo "   sudo systemctl restart nginx"
echo ""
echo "4. 设置开机自启："
echo "   sudo systemctl enable heartmoments"
echo "   sudo systemctl enable nginx"
echo ""
echo "5. 检查状态："
echo "   sudo systemctl status heartmoments"
echo "   sudo systemctl status nginx"
echo ""
echo "6. 浏览器访问："
echo "   http://你的服务器IP"
echo ""
echo -e "${YELLOW}如遇到问题，请查看日志：${NC}"
echo "   tail -f logs/gunicorn-error.log"
echo "   sudo journalctl -u heartmoments -f"
echo ""

