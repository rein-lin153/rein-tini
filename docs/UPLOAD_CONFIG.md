# 文件上传配置说明

## 概述

本文档说明如何配置服务器以支持大文件上传，特别是音乐文件（最大 30MB）和背景图片（最大 5MB）。

## Flask 应用配置

应用配置文件 `app/config.py` 中已设置：

```python
MAX_CONTENT_LENGTH = 30 * 1024 * 1024  # 30MB
MAX_MUSIC_SIZE = 30 * 1024 * 1024      # 30MB
MAX_COVER_SIZE = 2 * 1024 * 1024       # 2MB
```

## Nginx 配置

如果使用 Nginx 作为反向代理，需要在 Nginx 配置文件中添加以下设置：

### 基本配置

在 `server` 或 `http` 块中添加：

```nginx
# 允许上传的最大文件大小（建议设置为 50MB 以留有余地）
client_max_body_size 50M;

# 请求体缓冲区大小
client_body_buffer_size 128k;

# 请求体临时文件路径
client_body_temp_path /tmp/nginx_upload;

# 超时设置
client_body_timeout 60s;
```

### 完整示例配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 文件上传大小限制
    client_max_body_size 50M;
    client_body_buffer_size 128k;
    client_body_timeout 60s;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # 静态文件直接由 Nginx 提供
    location /static {
        alias /path/to/your/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 上传文件路径
    location /uploads {
        alias /path/to/your/app/uploads;
        expires 7d;
    }
}
```

## Gunicorn 配置

如果使用 Gunicorn 作为 WSGI 服务器，在配置文件中添加：

```python
# gunicorn_config.py
# 限制请求行长度（可选）
limit_request_line = 4094

# 限制请求头字段数量（可选）
limit_request_fields = 100

# 限制请求头字段大小（可选）
limit_request_field_size = 8190

# 超时设置
timeout = 120
```

或在启动命令中指定：

```bash
gunicorn -w 4 -t 120 --limit-request-line 4094 --limit-request-fields 100 wsgi:app
```

## 环境变量配置

可以在 `.env` 文件中设置：

```bash
# 最大内容长度（字节）
MAX_CONTENT_LENGTH=31457280  # 30MB

# 最大音乐文件大小（字节）
MAX_MUSIC_SIZE=31457280  # 30MB

# 最大封面文件大小（字节）
MAX_COVER_SIZE=2097152  # 2MB
```

## 故障排查

### 问题：上传大文件时返回 413 错误

1. **检查 Nginx 配置**：
   ```bash
   # 检查当前配置
   nginx -T | grep client_max_body_size
   
   # 如果未设置或设置过小，修改配置文件后重启
   sudo nginx -s reload
   ```

2. **检查 Flask 配置**：
   - 确认 `MAX_CONTENT_LENGTH` 设置正确
   - 查看应用日志确认错误详情

3. **检查文件系统权限**：
   ```bash
   # 确保上传目录可写
   chmod 755 /path/to/uploads
   chown www-data:www-data /path/to/uploads
   ```

### 问题：上传超时

1. **增加超时时间**：
   - Nginx: `proxy_read_timeout 120s;`
   - Gunicorn: `timeout = 120`

2. **检查网络连接**：
   - 确认客户端到服务器的网络稳定
   - 检查是否有防火墙限制

## 测试

使用 curl 测试上传：

```bash
# 测试音乐上传（需要管理员 token）
curl -X POST http://your-domain.com/music/api/music \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@test.mp3" \
  -F "title=Test Song" \
  -F "artist=Test Artist"

# 测试背景上传（需要管理员 token）
curl -X POST http://your-domain.com/api/backgrounds \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@background.jpg"
```

## 安全建议

1. **限制上传文件类型**：后端已实现文件类型验证
2. **限制上传文件大小**：前端和后端都进行了大小检查
3. **使用 HTTPS**：生产环境务必使用 HTTPS
4. **定期清理**：定期清理临时文件和过期上传文件
5. **监控日志**：监控上传日志，及时发现异常

## 参考

- [Nginx client_max_body_size 文档](http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)
- [Flask MAX_CONTENT_LENGTH 文档](https://flask.palletsprojects.com/en/2.3.x/config/#MAX_CONTENT_LENGTH)
- [Gunicorn 配置文档](https://docs.gunicorn.org/en/stable/settings.html)

