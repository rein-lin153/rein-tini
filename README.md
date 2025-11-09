# 💖 心语时光 (HeartMoments)

一个轻量、浪漫、为情侣打造的专属纪念网站 ✨

[![Python Version](https://img.shields.io/badge/python-3.6.8-blue.svg)](https://python.org)
[![Flask Version](https://img.shields.io/badge/flask-1.1.4-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 🌟 项目简介

**心语时光** 是一个专为情侣设计的纪念网站，帮助记录你们的美好瞬间：

- 📅 **在一起天数**自动计算与纪念日倒计时
- 📸 **精美相册**支持批量上传、自动压缩、懒加载
- ✍️ **情侣日记**记录生活点滴，支持图文混排
- 💬 **甜蜜留言板**随时留下爱的话语
- 🎨 **浪漫主题**粉紫渐变、心形漂浮、柔和动画
- 📱 **移动优先**完美适配手机与平板
- 🚀 **轻量高效**可在 1 核 1GB 服务器流畅运行

---

## 🎯 核心特性

### 功能特性
✅ 简单安全的双用户登录系统  
✅ 首页展示在一起天数、纪念日倒计时、最新照片  
✅ 相册支持批量上传、自动生成缩略图、瀑布流展示  
✅ 日记支持富文本编辑、图片插入、时间线展示  
✅ 留言板支持 Markdown 渲染与回复  
✅ 纪念日管理（相识日、确定关系日等）  
✅ RESTful API 接口，方便扩展  
✅ 站点设置（自定义背景、标题）  

### 性能特性
⚡ SQLite WAL 模式提升并发性能  
⚡ 图片自动压缩（75% 质量）与缩略图生成  
⚡ 前端懒加载与分页，减少流量消耗  
⚡ Gunicorn + Nginx 反向代理架构  
⚡ 静态资源缓存优化  
⚡ 内存占用 < 200MB（含 2 个 worker）  

### 安全特性
🔒 bcrypt 密码哈希加密  
🔒 CSRF 防护与会话管理  
🔒 XSS 防护（Bleach 净化）  
🔒 文件上传白名单与 MIME 验证  
🔒 速率限制防止暴力破解  

---

## 📋 系统要求

### 最低配置
- **操作系统**: CentOS 7+ / Ubuntu 18.04+ / Debian 9+
- **CPU**: 1 核
- **内存**: 1 GB
- **磁盘**: 10 GB 可用空间
- **Python**: 3.6.8+
- **Nginx**: 1.14+（可选但推荐）

### 推荐配置
- **CPU**: 2 核
- **内存**: 2 GB
- **磁盘**: 20 GB SSD

---

## 📚 文档

- [上传配置说明](docs/UPLOAD_CONFIG.md) - Nginx 和 Gunicorn 配置，文件大小限制设置
- [测试清单](docs/TESTING.md) - 完整的回归测试步骤和验证方法

## 🚀 快速开始

### 1. 克隆项目

```bash
# 如果还未创建项目，请先创建目录
mkdir -p /var/www/heartmoments
cd /var/www/heartmoments

# 将项目文件放置到此目录
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或者 Windows: venv\Scripts\activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用 vim/vi
```

**必须修改的配置项**：
```env
SECRET_KEY=your-random-secret-key-here  # 使用 python -c "import os; print(os.urandom(24).hex())" 生成
COUPLE_NAME_1=Rein
COUPLE_NAME_2=Nana
TOGETHER_DATE=2023-01-14  # 在一起的日期
```

### 4. 初始化数据库

```bash
# 运行初始化脚本
python scripts/init_db.py

# 创建管理员账户
python scripts/create_admin.py
# 按提示输入用户名和密码
```

### 5. 启动开发服务器

```bash
# 开发模式启动（仅用于测试）
python app.py

# 访问 http://localhost:5000
```

---

## 📦 生产部署

### 方法一：使用 Gunicorn + Nginx（推荐）

#### Step 1: 配置 Gunicorn

```bash
# 测试 Gunicorn 启动
gunicorn -w 2 -b 127.0.0.1:8000 wsgi:app

# 如果正常，按 Ctrl+C 停止
```

#### Step 2: 配置 Systemd 服务

```bash
# 复制服务文件
sudo cp deployment/heartmoments.service /etc/systemd/system/

# 编辑服务文件，修改路径
sudo nano /etc/systemd/system/heartmoments.service

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start heartmoments

# 设置开机自启
sudo systemctl enable heartmoments

# 查看状态
sudo systemctl status heartmoments
```

#### Step 3: 配置 Nginx

```bash
# 复制配置文件
sudo cp deployment/nginx.conf /etc/nginx/sites-available/heartmoments

# 创建软链接
sudo ln -s /etc/nginx/sites-available/heartmoments /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### Step 4: 配置 SSL（可选但推荐）

```bash
# 安装 Certbot
sudo yum install certbot python3-certbot-nginx  # CentOS
# 或 sudo apt install certbot python3-certbot-nginx  # Ubuntu

# 获取证书
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 配置说明

### 环境变量（.env 文件）

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `SECRET_KEY` | Flask 密钥（用于会话加密） | 无 | ✅ |
| `DATABASE_URI` | 数据库连接字符串 | `sqlite:///instance/heartmoments.db` | ❌ |
| `COUPLE_NAME_1` | 第一个人的名字 | Rein | ✅ |
| `COUPLE_NAME_2` | 第二个人的名字 | Nana | ✅ |
| `TOGETHER_DATE` | 在一起的日期 (YYYY-MM-DD) | 2023-01-14 | ✅ |
| `UPLOAD_FOLDER` | 上传文件保存路径 | `uploads` | ❌ |
| `MAX_CONTENT_LENGTH` | 最大上传大小（字节） | 5242880 (5MB) | ❌ |
| `PHOTOS_PER_PAGE` | 相册每页显示数量 | 20 | ❌ |
| `POSTS_PER_PAGE` | 日记每页显示数量 | 10 | ❌ |

### Gunicorn 配置

编辑 `deployment/gunicorn_config.py`：

```python
# 低配服务器（1 核 1GB）
workers = 2
worker_class = 'sync'
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
```

### Nginx 配置要点

```nginx
# 客户端最大上传大小
client_max_body_size 10M;

# Gzip 压缩
gzip on;
gzip_types text/css application/javascript image/svg+xml;

# 静态文件缓存
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

## 🧪 运行测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 显示详细输出
pytest -v

# 显示测试覆盖率
pytest --cov=app tests/
```

---

## 🔐 安全建议

在上线前，请完成以下检查：

1. ✅ 修改 `.env` 中的 `SECRET_KEY` 为随机值
2. ✅ 创建强密码的管理员账户（至少 12 位）
3. ✅ 配置 HTTPS（使用 Let's Encrypt）
4. ✅ 设置 Nginx 的 `client_max_body_size` 限制
5. ✅ 配置防火墙（仅开放 80/443 端口）
6. ✅ 定期备份数据库与上传文件
7. ✅ 修改 SSH 默认端口并禁用密码登录
8. ✅ 检查 uploads 目录权限（不可直接执行脚本）

详见 [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md)

---

## 🗄️ 数据备份与恢复

### 自动备份

```bash
# 编辑 crontab
crontab -e

# 添加每日凌晨 3 点备份任务
0 3 * * * /var/www/heartmoments/scripts/backup.sh
```

### 手动备份

```bash
# 运行备份脚本
bash scripts/backup.sh

# 备份文件保存在 backups/ 目录
# 格式: heartmoments_backup_YYYYMMDD_HHMMSS.tar.gz
```

### 恢复数据

```bash
# 运行恢复脚本
bash scripts/restore.sh backups/heartmoments_backup_20250108_030000.tar.gz
```

---

## 📊 性能优化

### 针对 1 核 1GB 服务器的优化建议

1. **Gunicorn Workers 设置**
   ```bash
   # 使用 2 个 worker（公式：2 * CPU核心数 + 1）
   workers = 2
   ```

2. **SQLite 优化**
   ```sql
   PRAGMA journal_mode=WAL;  -- 提高并发
   PRAGMA synchronous=NORMAL;  -- 平衡性能与安全
   PRAGMA cache_size=-64000;  -- 64MB 缓存
   ```

3. **图片压缩设置**
   - 缩略图宽度：300px
   - 原图最大宽度：1200px
   - JPEG 质量：75%

4. **浏览器缓存**
   - 静态资源：30 天
   - 图片资源：7 天

5. **禁用不必要的服务**
   ```bash
   # 停止不需要的服务释放内存
   sudo systemctl stop postfix
   sudo systemctl disable postfix
   ```

---

## 🛠️ 常见问题

### Q1: 上传图片失败？
**A**: 检查 `uploads/` 目录权限：
```bash
chmod 755 uploads
chmod 755 uploads/photos uploads/thumbs
chown -R your-user:your-user uploads/
```

### Q2: 数据库锁定错误？
**A**: 确保开启了 WAL 模式：
```bash
python scripts/init_db.py  # 重新初始化会自动开启
```

### Q3: Gunicorn 启动失败？
**A**: 检查端口占用：
```bash
sudo lsof -i :8000  # 查看 8000 端口
sudo kill -9 <PID>  # 杀死占用进程
```

### Q4: Nginx 502 错误？
**A**: 检查 Gunicorn 是否运行：
```bash
sudo systemctl status heartmoments
sudo journalctl -u heartmoments -n 50  # 查看日志
```

### Q5: 内存占用过高？
**A**: 减少 Gunicorn worker 数量：
```python
# deployment/gunicorn_config.py
workers = 1  # 极限情况使用单 worker
```

---

## 📚 进阶使用

### 切换到 MySQL/PostgreSQL

1. 修改 `.env` 中的 `DATABASE_URI`：
   ```env
   # MySQL
   DATABASE_URI=mysql+pymysql://user:password@localhost/heartmoments
   
   # PostgreSQL
   DATABASE_URI=postgresql://user:password@localhost/heartmoments
   ```

2. 安装对应驱动：
   ```bash
   pip install pymysql  # MySQL
   # 或
   pip install psycopg2-binary  # PostgreSQL
   ```

3. 重新初始化数据库：
   ```bash
   python scripts/init_db.py
   ```

### 自定义主题

编辑 `app/static/css/main.css` 修改配色：

```css
:root {
    --primary-color: #F7D6E0;  /* 浅粉 */
    --secondary-color: #E8D0FF;  /* 浅紫 */
    --accent-color: #FFB6C1;  /* 亮粉 */
    --text-dark: #333333;
}
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 💌 鸣谢

感谢所有为本项目做出贡献的开发者！

**特别感谢**：
- Flask 社区
- Bootstrap 团队
- 所有开源软件的维护者

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: support@heartmoments.example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourname/heartmoments/issues)

---

<p align="center">
  Made with ❤️ for couples around the world
</p>

<p align="center">
  ⭐ 如果这个项目对你有帮助，请给一个星标！ ⭐
</p>

