# 🚀 部署配置文件说明

本目录包含生产环境部署所需的所有配置文件。

## 📁 文件清单

| 文件 | 说明 | 使用方法 |
|-----|------|---------|
| `heartmoments.service` | Systemd 服务配置 | 复制到 `/etc/systemd/system/` |
| `nginx.conf` | Nginx 服务器配置 | 复制到 `/etc/nginx/conf.d/` |
| `deploy.sh` | 自动部署脚本 | `bash deploy.sh` |
| `快速部署命令.sh` | 一键部署命令集合 | 逐行执行或全部执行 |
| `故障排查.sh` | 诊断信息收集脚本 | `bash 故障排查.sh` |

---

## 🎯 快速部署步骤

### 方式 1：使用自动部署脚本（推荐）

```bash
cd /home/opc/rein-tini
bash deploy/deploy.sh
```

### 方式 2：手动执行命令

```bash
# 1. 进入项目目录
cd /home/opc/rein-tini

# 2. 配置 .env 文件（如果还没有）
cp env.example .env
nano .env  # 修改 SECRET_KEY 等配置

# 3. 安装依赖
source venv/bin/activate
pip install -r requirements.txt

# 4. 初始化数据库
python scripts/init_db.py
python scripts/create_admin.py

# 5. 复制服务配置
sudo cp deploy/heartmoments.service /etc/systemd/system/
sudo cp deploy/nginx.conf /etc/nginx/conf.d/heartmoments.conf

# 6. 修改 Nginx 配置中的域名/IP
sudo nano /etc/nginx/conf.d/heartmoments.conf
# 将 server_name 改为你的域名或IP

# 7. 启动服务
sudo systemctl daemon-reload
sudo systemctl start heartmoments
sudo systemctl enable heartmoments
sudo nginx -t && sudo systemctl restart nginx

# 8. 检查状态
sudo systemctl status heartmoments
sudo systemctl status nginx
```

---

## 🔍 配置文件详解

### 1. heartmoments.service

**Systemd 服务单元文件**，定义如何运行 Gunicorn。

**关键配置**：
- `User=opc` - 运行用户
- `WorkingDirectory=/home/opc/rein-tini` - 工作目录
- `--workers 2` - 2个工作进程（适合1GB内存）
- `--bind unix:...heartmoments.sock` - 使用 Unix Socket

**修改建议**：
- 如果内存充足，可增加 workers 数量
- 如果需要远程调试，可改用 TCP 端口：`--bind 127.0.0.1:8000`

### 2. nginx.conf

**Nginx 反向代理配置**，处理静态文件和请求转发。

**关键配置**：
- `server_name _` - 需要改为你的域名或IP
- `/static/` - 静态文件路径
- `/uploads/` - 上传文件路径
- `proxy_pass` - 转发到 Gunicorn Socket

**必须修改**：
```nginx
server_name your-domain.com;  # 或 IP 地址
```

### 3. deploy.sh

**自动化部署脚本**，执行以下操作：
1. 检查配置文件
2. 创建必要目录
3. 设置文件权限
4. 安装依赖
5. 初始化数据库
6. 配置服务

### 4. 快速部署命令.sh

**命令集合**，适合直接复制粘贴执行。

### 5. 故障排查.sh

**诊断工具**，收集以下信息：
- 服务状态
- 日志输出
- 文件权限
- 网络端口
- 系统资源

---

## 🛠️ 常见操作

### 重启服务

```bash
sudo systemctl restart heartmoments
sudo systemctl restart nginx
```

### 查看日志

```bash
# Gunicorn 日志
tail -f /home/opc/rein-tini/logs/gunicorn-error.log

# Systemd 日志
sudo journalctl -u heartmoments -f

# Nginx 日志
sudo tail -f /var/log/nginx/heartmoments_error.log
```

### 更新代码

```bash
cd /home/opc/rein-tini
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart heartmoments
```

### 备份数据

```bash
# 手动备份
cp /home/opc/rein-tini/instance/heartmoments.db \
   /home/opc/rein-tini/backups/heartmoments_$(date +%Y%m%d).db

# 使用备份脚本
bash /home/opc/rein-tini/scripts/backup.sh
```

---

## ⚠️ 重要注意事项

### 1. 文件权限

确保以下目录可写：
```bash
chmod 755 /home/opc/rein-tini/instance
chmod 755 /home/opc/rein-tini/uploads
chmod 755 /home/opc/rein-tini/logs
```

### 2. SELinux 配置

如果遇到权限问题，可能需要配置 SELinux：

```bash
# 临时禁用（测试用）
sudo setenforce 0

# 永久配置
sudo setsebool -P httpd_can_network_connect 1
sudo chcon -R -t httpd_sys_content_t /home/opc/rein-tini/app/static
sudo chcon -R -t httpd_sys_content_t /home/opc/rein-tini/uploads
```

### 3. 防火墙配置

确保开放 HTTP/HTTPS 端口：

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 4. 数据库路径

`.env` 文件中的数据库路径**必须使用绝对路径**：

```bash
DATABASE_URI=sqlite:////home/opc/rein-tini/instance/heartmoments.db
#                    ^ 注意这里是 4 个斜杠
```

---

## 🐛 故障排查

### 问题：502 Bad Gateway

**可能原因**：
1. Gunicorn 未启动
2. Socket 文件不存在或权限错误
3. SELinux 阻止

**解决方案**：

```bash
# 检查服务状态
sudo systemctl status heartmoments

# 检查 socket 文件
ls -la /home/opc/rein-tini/heartmoments.sock

# 查看日志
sudo journalctl -u heartmoments -n 50

# 运行诊断脚本
bash deploy/故障排查.sh
```

### 问题：静态文件 404

**解决方案**：

```bash
# 检查路径权限
namei -l /home/opc/rein-tini/app/static

# 确保所有父目录可访问
chmod 755 /home
chmod 755 /home/opc
chmod 755 /home/opc/rein-tini
```

### 问题：上传图片失败

**解决方案**：

```bash
# 创建目录
mkdir -p /home/opc/rein-tini/uploads/photos
mkdir -p /home/opc/rein-tini/uploads/thumbs

# 设置权限
chmod -R 755 /home/opc/rein-tini/uploads
chown -R opc:opc /home/opc/rein-tini/uploads
```

---

## 📞 获取帮助

1. 查看详细部署文档：`../生产环境配置_自定义路径.md`
2. 运行诊断脚本：`bash deploy/故障排查.sh`
3. 查看应用日志：`tail -f /home/opc/rein-tini/logs/gunicorn-error.log`

---

**更新时间**：2025-01-08  
**项目路径**：`/home/opc/rein-tini`  
**用户**：`opc`

