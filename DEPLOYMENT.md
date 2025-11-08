# 💖 心语时光 - 生产环境部署指南

本文档详细说明如何在 CentOS 7+ 服务器（1 核 1GB 内存）上部署心语时光应用。

---

## 📋 目录

1. [服务器准备](#服务器准备)
2. [安装依赖](#安装依赖)
3. [部署应用](#部署应用)
4. [配置 Gunicorn](#配置-gunicorn)
5. [配置 Nginx](#配置-nginx)
6. [配置 HTTPS](#配置-https)
7. [设置开机自启](#设置开机自启)
8. [配置备份](#配置备份)
9. [性能优化](#性能优化)
10. [故障排查](#故障排查)

---

## 服务器准备

### 1. 更新系统

```bash
sudo yum update -y
sudo yum install -y epel-release
```

### 2. 安装必要工具

```bash
sudo yum install -y git wget curl vim
```

### 3. 配置防火墙

```bash
# 开放 HTTP 和 HTTPS 端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 查看防火墙状态
sudo firewall-cmd --list-all
```

---

## 安装依赖

### 1. 安装 Python 3.6.8

```bash
# CentOS 7 自带 Python 3.6.8
python3 --version

# 如果没有，手动安装
sudo yum install -y python3 python3-devel
```

### 2. 安装 Nginx

```bash
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 3. 安装编译工具

```bash
# Pillow 需要的图片库
sudo yum install -y gcc libjpeg-devel zlib-devel
```

---

## 部署应用

### 1. 创建项目目录

```bash
sudo mkdir -p /var/www/heartmoments
sudo chown -R $USER:$USER /var/www/heartmoments
cd /var/www/heartmoments
```

### 2. 克隆或上传代码

```bash
# 方式 1: 使用 Git（推荐）
git clone https://github.com/yourname/heartmoments.git .

# 方式 2: 上传压缩包
# 将项目文件打包上传到服务器并解压
```

### 3. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. 安装 Python 依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**注意**：如果安装 Pillow 时遇到错误，请确保已安装 libjpeg-devel 和 zlib-devel。

### 5. 配置环境变量

```bash
# 复制示例配置
cp env.example .env

# 编辑配置文件
vim .env
```

**必须修改的配置项**：

```env
# 生成随机密钥
SECRET_KEY=$(python3 -c "import os; print(os.urandom(24).hex())")

# 情侣信息
COUPLE_NAME_1=Rein
COUPLE_NAME_2=Nana
TOGETHER_DATE=2023-01-14

# 环境
FLASK_ENV=production
```

### 6. 初始化数据库

```bash
# 创建数据库表
python scripts/init_db.py

# 创建管理员账户
python scripts/create_admin.py
```

### 7. 创建必要目录

```bash
mkdir -p uploads/photos uploads/thumbs uploads/backgrounds
mkdir -p logs backups instance
chmod 755 uploads logs backups instance
```

### 8. 测试应用

```bash
# 使用开发服务器测试
python app.py

# 访问 http://服务器IP:5000 测试
# 如果正常，按 Ctrl+C 停止
```

---

## 配置 Gunicorn

### 1. 测试 Gunicorn

```bash
gunicorn --bind 127.0.0.1:8000 wsgi:app
```

### 2. 配置 Systemd 服务

```bash
# 复制服务文件
sudo cp deployment/heartmoments.service /etc/systemd/system/

# 编辑服务文件（修改用户和路径）
sudo vim /etc/systemd/system/heartmoments.service
```

**修改以下内容**：

```ini
User=你的用户名
Group=你的用户组
WorkingDirectory=/var/www/heartmoments
Environment="PATH=/var/www/heartmoments/venv/bin"
ExecStart=/var/www/heartmoments/venv/bin/gunicorn \
    --config /var/www/heartmoments/deployment/gunicorn_config.py \
    wsgi:app
```

### 3. 启动服务

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start heartmoments

# 查看状态
sudo systemctl status heartmoments

# 设置开机自启
sudo systemctl enable heartmoments
```

### 4. 查看日志

```bash
# 实时查看日志
sudo journalctl -u heartmoments -f

# 查看最近 50 条日志
sudo journalctl -u heartmoments -n 50
```

---

## 配置 Nginx

### 1. 复制配置文件

```bash
sudo cp deployment/nginx.conf /etc/nginx/conf.d/heartmoments.conf
```

### 2. 编辑配置

```bash
sudo vim /etc/nginx/conf.d/heartmoments.conf
```

**修改以下内容**：

```nginx
server_name your-domain.com www.your-domain.com;  # 改为你的域名
root /var/www/heartmoments;  # 确认路径正确
```

### 3. 测试配置

```bash
sudo nginx -t
```

### 4. 重启 Nginx

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 5. 测试访问

访问 `http://你的域名` 或 `http://服务器IP`，应该能看到网站首页。

---

## 配置 HTTPS

### 1. 安装 Certbot

```bash
sudo yum install -y certbot python3-certbot-nginx
```

### 2. 获取证书

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

按提示输入邮箱并同意服务条款。

### 3. 测试自动续期

```bash
sudo certbot renew --dry-run
```

### 4. 配置自动续期

```bash
# 编辑 crontab
sudo crontab -e

# 添加以下行（每天凌晨 3 点检查续期）
0 3 * * * certbot renew --quiet
```

---

## 设置开机自启

```bash
# 启用所有服务
sudo systemctl enable nginx
sudo systemctl enable heartmoments

# 查看启动状态
sudo systemctl list-unit-files | grep enabled | grep -E '(nginx|heartmoments)'
```

---

## 配置备份

### 1. 设置脚本权限

```bash
chmod +x scripts/backup.sh scripts/restore.sh
```

### 2. 编辑备份脚本

```bash
vim scripts/backup.sh
```

修改项目路径（如果不是 `/var/www/heartmoments`）。

### 3. 测试备份

```bash
bash scripts/backup.sh
```

### 4. 配置自动备份

```bash
# 编辑 crontab
crontab -e

# 添加每日凌晨 3 点备份
0 3 * * * /var/www/heartmoments/scripts/backup.sh >> /var/www/heartmoments/logs/backup.log 2>&1
```

### 5. 备份到远程（可选）

如果有远程服务器或云存储，可以配置自动上传：

```bash
# 使用 rsync 上传到远程服务器
rsync -avz /var/www/heartmoments/backups/ user@remote:/backup/heartmoments/

# 或使用 rclone 上传到云存储（需先配置 rclone）
rclone copy /var/www/heartmoments/backups/ remote:heartmoments-backup/
```

---

## 性能优化

### 针对 1 核 1GB 服务器的优化

#### 1. Gunicorn 配置

编辑 `deployment/gunicorn_config.py`：

```python
# 极限配置（如果 2 worker 仍然卡顿）
workers = 1
threads = 2
worker_class = 'gthread'
worker_tmp_dir = '/dev/shm'  # 使用内存作为临时目录
```

#### 2. 系统优化

```bash
# 禁用不必要的服务
sudo systemctl disable postfix
sudo systemctl stop postfix

# 清理缓存
sudo yum clean all
```

#### 3. SQLite 优化

数据库已启用 WAL 模式，无需额外配置。如需进一步优化：

```bash
# 定期清理 WAL 文件
echo "PRAGMA wal_checkpoint(FULL);" | sqlite3 instance/heartmoments.db
```

#### 4. 图片优化建议

- 上传前手动压缩大图片
- 定期清理不需要的照片
- 考虑使用对象存储（七牛云、阿里云 OSS）

---

## 故障排查

### 问题 1: 502 Bad Gateway

**原因**：Gunicorn 未启动或端口不通

**解决**：

```bash
# 检查 Gunicorn 状态
sudo systemctl status heartmoments

# 查看日志
sudo journalctl -u heartmoments -n 50

# 检查端口
sudo lsof -i :8000

# 重启服务
sudo systemctl restart heartmoments
```

### 问题 2: 图片上传失败

**原因**：目录权限或 Nginx 配置问题

**解决**：

```bash
# 检查目录权限
ls -la uploads/

# 修复权限
chmod 755 uploads uploads/photos uploads/thumbs

# 检查 Nginx 配置
sudo nginx -t
```

### 问题 3: 数据库锁定

**原因**：并发写入冲突

**解决**：

```bash
# 确认 WAL 模式已启用
echo "PRAGMA journal_mode;" | sqlite3 instance/heartmoments.db
# 应显示 "wal"

# 如果不是，重新初始化
python scripts/init_db.py
```

### 问题 4: 内存不足

**原因**：Worker 数量过多

**解决**：

```bash
# 编辑 Gunicorn 配置
vim deployment/gunicorn_config.py

# 减少 worker 数量
workers = 1

# 重启服务
sudo systemctl restart heartmoments
```

### 问题 5: 静态文件 404

**原因**：Nginx 路径配置错误

**解决**：

```bash
# 检查路径
ls -la /var/www/heartmoments/app/static
ls -la /var/www/heartmoments/uploads

# 确认 Nginx 配置中的路径正确
sudo vim /etc/nginx/conf.d/heartmoments.conf

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 日常维护

### 查看应用状态

```bash
sudo systemctl status heartmoments nginx
```

### 查看日志

```bash
# 应用日志
tail -f logs/heartmoments.log

# Gunicorn 日志
tail -f logs/gunicorn_error.log

# Nginx 日志
sudo tail -f /var/log/nginx/heartmoments_error.log
```

### 更新代码

```bash
cd /var/www/heartmoments
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart heartmoments
```

### 数据库备份与恢复

```bash
# 手动备份
bash scripts/backup.sh

# 恢复备份
bash scripts/restore.sh backups/heartmoments_backup_YYYYMMDD_HHMMSS.tar.gz
```

---

## 监控建议

1. **服务器监控**：使用 `htop` 或 `glances` 监控资源使用
2. **应用监控**：定期检查日志文件
3. **磁盘监控**：定期清理备份和日志
4. **SSL 证书**：Certbot 会自动续期，但建议定期检查

---

## 技术支持

如有问题，请查看：

- 应用日志：`logs/heartmoments.log`
- Gunicorn 日志：`logs/gunicorn_error.log`
- Nginx 日志：`/var/log/nginx/heartmoments_error.log`
- 系统日志：`sudo journalctl -xe`

---

**祝部署顺利！ 💖**

