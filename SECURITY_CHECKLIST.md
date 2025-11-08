# 🔒 心语时光 - 安全检查清单

在将应用部署到生产环境之前，请逐项完成以下安全检查。

---

## ✅ 上线前必做（8 项核心检查）

### 1. 修改 SECRET_KEY

**重要性**：⭐⭐⭐⭐⭐

- [ ] 在 `.env` 文件中设置强随机 `SECRET_KEY`
- [ ] 确保 SECRET_KEY 至少 32 字符
- [ ] 从未提交 SECRET_KEY 到 Git 仓库

**生成方法**：

```bash
python3 -c "import os; print(os.urandom(24).hex())"
```

---

### 2. 创建强密码管理员账户

**重要性**：⭐⭐⭐⭐⭐

- [ ] 管理员密码至少 12 位
- [ ] 包含大小写字母、数字和特殊符号
- [ ] 不使用常见密码（如 admin123、password）
- [ ] 定期更换密码（建议每 3 个月）

**密码强度测试**：

```bash
# 使用 create_admin.py 时会提示密码强度
python scripts/create_admin.py
```

---

### 3. 配置 HTTPS（SSL/TLS）

**重要性**：⭐⭐⭐⭐⭐

- [ ] 使用 Let's Encrypt 免费证书
- [ ] 配置 HTTP 自动跳转 HTTPS
- [ ] 启用 HSTS（HTTP Strict Transport Security）
- [ ] 测试 SSL 配置（使用 SSL Labs）

**配置方法**：

```bash
sudo certbot --nginx -d your-domain.com
```

**验证**：访问 https://www.ssllabs.com/ssltest/ 测试

---

### 4. 限制文件上传大小

**重要性**：⭐⭐⭐⭐

- [ ] Flask 配置 `MAX_CONTENT_LENGTH = 5MB`
- [ ] Nginx 配置 `client_max_body_size 10M`
- [ ] 验证文件类型白名单（仅允许图片）
- [ ] 启用文件 MIME 类型检查

**检查配置**：

```python
# app/config.py
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
```

```nginx
# deployment/nginx.conf
client_max_body_size 10M;
```

---

### 5. 配置防火墙

**重要性**：⭐⭐⭐⭐

- [ ] 仅开放 80（HTTP）和 443（HTTPS）端口
- [ ] 关闭不必要的服务端口
- [ ] 禁用 ping（可选）
- [ ] 配置 fail2ban 防止暴力破解

**命令**：

```bash
# 开放端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 查看开放端口
sudo firewall-cmd --list-all
```

---

### 6. 设置文件权限

**重要性**：⭐⭐⭐⭐

- [ ] 数据库文件权限 644
- [ ] 上传目录权限 755
- [ ] 配置文件权限 600（包含敏感信息）
- [ ] 脚本文件可执行权限 755

**命令**：

```bash
chmod 644 instance/heartmoments.db
chmod 755 uploads uploads/photos uploads/thumbs
chmod 600 .env
chmod 755 scripts/*.sh
```

---

### 7. 启用日志与监控

**重要性**：⭐⭐⭐⭐

- [ ] 配置应用日志（已在 config.py 中设置）
- [ ] 配置 Nginx 访问日志
- [ ] 配置 Gunicorn 日志
- [ ] 定期查看日志文件

**查看日志**：

```bash
# 应用日志
tail -f logs/heartmoments.log

# Nginx 日志
sudo tail -f /var/log/nginx/heartmoments_access.log

# Gunicorn 日志
sudo journalctl -u heartmoments -f
```

---

### 8. 定期备份数据

**重要性**：⭐⭐⭐⭐⭐

- [ ] 配置自动备份（cron job）
- [ ] 测试备份恢复流程
- [ ] 备份保留至少 30 天
- [ ] 异地备份（上传到云存储）

**配置自动备份**：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 3 点备份
0 3 * * * /var/www/heartmoments/scripts/backup.sh
```

---

## 🔒 进阶安全措施（推荐）

### 9. 修改 SSH 端口

- [ ] 修改默认 SSH 端口（22 -> 其他）
- [ ] 禁用 root SSH 登录
- [ ] 仅允许密钥登录（禁用密码）
- [ ] 配置 SSH 登录失败次数限制

**配置**：

```bash
sudo vim /etc/ssh/sshd_config

# 修改以下配置
Port 2222  # 改为非标准端口
PermitRootLogin no
PasswordAuthentication no

# 重启 SSH
sudo systemctl restart sshd
```

---

### 10. 配置速率限制

- [ ] 登录失败限制（已在代码中实现）
- [ ] API 请求频率限制（已在代码中实现）
- [ ] Nginx 连接数限制
- [ ] 使用 fail2ban 防护

**Nginx 限制示例**：

```nginx
# 限制请求速率
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

location /auth/login {
    limit_req zone=login burst=3;
    proxy_pass http://heartmoments_app;
}
```

---

### 11. 数据库安全

- [ ] SQLite 文件不可通过 Web 访问
- [ ] 启用 WAL 模式（已自动配置）
- [ ] 定期备份数据库
- [ ] 考虑迁移到 MySQL/PostgreSQL（可选）

**验证 WAL 模式**：

```bash
echo "PRAGMA journal_mode;" | sqlite3 instance/heartmoments.db
# 应输出 "wal"
```

---

### 12. 上传文件安全

- [ ] 文件类型白名单验证
- [ ] MIME 类型检查
- [ ] 文件扩展名验证
- [ ] 图片内容验证（magic bytes）
- [ ] 文件重命名（UUID）

**已实现**：在 `app/album/image_handler.py` 中。

---

### 13. XSS 防护

- [ ] 使用 Bleach 净化用户输入
- [ ] Markdown 渲染安全配置
- [ ] 模板自动转义（Jinja2 默认启用）
- [ ] CSP（Content Security Policy）头部

**检查**：代码中已使用 `bleach.clean()` 处理用户输入。

---

### 14. CSRF 防护

- [ ] Flask-WTF CSRF 保护已启用
- [ ] 所有表单包含 CSRF token
- [ ] API 接口使用 token 或 session 验证

**验证**：模板中使用 `{{ form.hidden_tag() }}`。

---

### 15. 隐藏敏感信息

- [ ] 关闭 DEBUG 模式（生产环境）
- [ ] 隐藏服务器版本信息
- [ ] 自定义错误页面（不泄露堆栈信息）
- [ ] 移除测试账户

**Nginx 隐藏版本**：

```nginx
# nginx.conf
server_tokens off;
```

---

### 16. 更新依赖包

- [ ] 定期更新 Python 依赖
- [ ] 检查安全漏洞（pip-audit）
- [ ] 订阅安全公告

**检查安全漏洞**：

```bash
pip install pip-audit
pip-audit
```

---

## 📋 安全审计清单

### 环境变量安全

- [ ] `.env` 文件不在 Git 仓库中
- [ ] `.env` 文件权限为 600
- [ ] SECRET_KEY 使用随机生成值
- [ ] 数据库密码复杂度符合要求

### 网络安全

- [ ] 仅开放必要端口
- [ ] 配置 HTTPS
- [ ] 启用防火墙
- [ ] 配置 fail2ban

### 应用安全

- [ ] 关闭 DEBUG 模式
- [ ] CSRF 保护已启用
- [ ] XSS 防护已配置
- [ ] 文件上传验证完善
- [ ] 速率限制已启用

### 服务器安全

- [ ] 系统已更新到最新
- [ ] SSH 配置安全
- [ ] 用户权限最小化
- [ ] 日志记录完善

### 数据安全

- [ ] 密码使用 bcrypt 哈希
- [ ] 数据库定期备份
- [ ] 备份异地存储
- [ ] 备份恢复流程已测试

---

## 🚨 应急响应

### 发现安全漏洞时

1. **立即隔离**：停止受影响的服务
   ```bash
   sudo systemctl stop heartmoments
   ```

2. **评估影响**：检查日志确定影响范围
   ```bash
   sudo journalctl -u heartmoments -n 500
   ```

3. **修复漏洞**：更新代码或配置

4. **恢复服务**：测试后重新上线
   ```bash
   sudo systemctl start heartmoments
   ```

5. **通知用户**：如涉及数据泄露，通知受影响用户

---

## 📞 安全资源

- **OWASP Top 10**：https://owasp.org/www-project-top-ten/
- **Flask 安全最佳实践**：https://flask.palletsprojects.com/en/latest/security/
- **Let's Encrypt**：https://letsencrypt.org/
- **SSL Labs 测试**：https://www.ssllabs.com/ssltest/

---

## ✅ 最终确认

部署前，请确认以下所有项目：

- [ ] SECRET_KEY 已修改为强随机值
- [ ] 管理员密码符合强度要求
- [ ] HTTPS 已配置并正常工作
- [ ] 防火墙已配置（仅开放 80/443）
- [ ] 文件权限已正确设置
- [ ] 自动备份已配置并测试
- [ ] 日志系统正常工作
- [ ] 所有安全功能已启用（CSRF、XSS 防护等）

**签名确认**：

- 检查人：__________
- 检查日期：__________
- 部署环境：__________

---

**安全无小事，定期审计很重要！💪**

**建议每季度重新检查一次本清单。**

