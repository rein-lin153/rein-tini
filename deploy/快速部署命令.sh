#!/bin/bash
# 快速部署命令 - 直接复制粘贴执行

cd /home/opc/rein-tini

# 1. 安装依赖并初始化
source venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py

# 2. 创建管理员（需要交互）
python scripts/create_admin.py

# 3. 复制配置文件
sudo cp deploy/heartmoments.service /etc/systemd/system/
sudo cp deploy/nginx.conf /etc/nginx/conf.d/heartmoments.conf

# 4. 重新加载 systemd
sudo systemctl daemon-reload

# 5. 启动服务
sudo systemctl start heartmoments
sudo systemctl enable heartmoments

# 6. 测试并重启 Nginx
sudo nginx -t && sudo systemctl restart nginx

# 7. 检查状态
echo "========================================="
echo "检查服务状态..."
echo "========================================="
sudo systemctl status heartmoments --no-pager
sudo systemctl status nginx --no-pager

echo ""
echo "========================================="
echo "检查 socket 文件..."
echo "========================================="
ls -la /home/opc/rein-tini/heartmoments.sock

echo ""
echo "========================================="
echo "部署完成！"
echo "访问: http://$(curl -s ifconfig.me)"
echo "========================================="

