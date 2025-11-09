# 音乐系统集成指南

## 🎯 快速开始

### 1. 环境准备

确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建或更新 `.env` 文件：

```bash
# 管理员上传令牌（生产环境请更改！）
ADMIN_UPLOAD_TOKEN=your-secret-token-here

# 其他配置...
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

### 3. 启动应用

```bash
flask run
```

或使用开发服务器：

```bash
python app.py
```

### 4. 测试播放器

1. 访问 `http://localhost:5000`
2. 点击右下角的音乐按钮 🎵
3. 播放器窗口应该打开
4. 如果播放列表为空，请先上传音乐

## 📁 目录结构

系统会自动创建以下目录：

```
app/
├── static/
│   ├── music/           # 音乐文件目录
│   │   └── covers/      # 封面图片目录
│   └── backgrounds/     # 背景图目录
└── music/               # 音乐模块
    ├── __init__.py
    ├── routes.py
    ├── models.py
    └── utils.py

instance/
└── music_index.json     # 音乐索引文件（自动创建）
```

## 🔧 配置说明

### 配置文件 (`app/config.py`)

主要配置项：

```python
# 音乐文件夹
MUSIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music')
COVER_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music', 'covers')
BACKGROUND_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'backgrounds')

# 文件限制
ALLOWED_MUSIC_EXTENSIONS = {'mp3'}  # 仅支持 MP3
MAX_MUSIC_SIZE = 25 * 1024 * 1024   # 25MB
MAX_COVER_SIZE = 2 * 1024 * 1024    # 2MB

# 管理员令牌
ADMIN_UPLOAD_TOKEN = os.environ.get('ADMIN_UPLOAD_TOKEN', 'changeme123')
```

### 环境变量

在 `.env` 文件中可以覆盖以下配置：

- `ADMIN_UPLOAD_TOKEN` - 管理员上传令牌
- `MAX_MUSIC_SIZE` - 最大音乐文件大小（字节）
- `MAX_COVER_SIZE` - 最大封面文件大小（字节）

## 📤 上传音乐

### 方法 1：通过网页上传（推荐）

1. 登录管理员账户
2. 点击用户菜单 → "上传音乐"
3. 选择 MP3 文件
4. 可选：上传封面图片
5. 可选：填写歌曲标题和艺术家（如果不填，将从文件名提取）
6. 点击上传

### 方法 2：使用 API（命令行）

```bash
# 使用令牌
curl -X POST \
  -H "Authorization: Bearer your-token-here" \
  -F "file=@song.mp3" \
  -F "cover=@cover.jpg" \
  -F "title=歌曲标题" \
  -F "artist=艺术家" \
  http://localhost:5000/music/upload
```

### 方法 3：手动放置文件

1. 将 MP3 文件放入 `app/static/music/` 目录
2. 可选：将封面图片放入 `app/static/music/covers/` 目录
3. 文件名格式推荐：`艺术家 - 歌曲名.mp3`
4. 封面文件名应与音乐文件名相同（扩展名不同）

## 🎵 播放器使用

### 打开播放器

- 点击主站点右下角的音乐按钮 🎵
- 或直接访问 `http://localhost:5000/music/player`

### 播放器功能

- **播放/暂停**：点击中间的播放按钮
- **上一首/下一首**：点击两侧的按钮
- **进度控制**：点击进度条跳转到指定位置
- **音量控制**：点击音量按钮或拖动音量滑块
- **随机播放**：点击随机按钮
- **循环播放**：点击循环按钮（无循环/列表循环/单曲循环）
- **喜欢**：点击心形按钮
- **播放列表**：点击列表按钮查看所有歌曲

### 状态持久化

播放器会自动保存以下状态：
- 当前播放的歌曲
- 播放进度
- 音量设置
- 播放模式（随机/循环）
- 喜欢的歌曲

即使关闭播放器窗口，下次打开时会自动恢复。

## 🔐 安全说明

### 上传权限

1. **管理员登录**：登录管理员账户后可以通过网页上传
2. **API 令牌**：使用 `Authorization: Bearer <token>` 头进行 API 上传

### 文件验证

- 仅支持 MP3 格式的音乐文件
- 文件大小限制：25MB
- 封面文件大小限制：2MB
- 文件名自动安全处理

### 生产环境建议

1. **更改默认令牌**：务必在 `.env` 中设置强密码的 `ADMIN_UPLOAD_TOKEN`
2. **使用 HTTPS**：生产环境应使用 HTTPS
3. **限制上传频率**：可以考虑添加速率限制
4. **定期备份**：定期备份音乐文件和索引文件

## 🐛 故障排查

### 播放器无法打开

**问题**：点击音乐按钮后没有反应

**解决方案**：
1. 检查浏览器是否阻止了弹窗
2. 查看浏览器控制台是否有错误
3. 检查 `/music/player` 路由是否正常

### 播放列表为空

**问题**：播放器显示"播放列表为空"

**解决方案**：
1. 检查 `app/static/music/` 目录是否存在
2. 检查目录中是否有 MP3 文件
3. 检查文件权限（确保可读）
4. 查看服务器日志

### 上传失败

**问题**：上传音乐时出错

**解决方案**：
1. 检查文件格式是否为 MP3
2. 检查文件大小是否超过 25MB
3. 检查管理员权限或令牌是否正确
4. 查看服务器日志 (`logs/heartmoments.log`)

### 播放状态未恢复

**问题**：关闭播放器后，下次打开时没有恢复播放状态

**解决方案**：
1. 检查浏览器是否允许 localStorage
2. 检查浏览器是否在隐私模式下运行
3. 清除浏览器缓存后重试

## 🔄 从旧系统迁移

### 迁移音乐文件

1. 将旧的音乐文件从 `app/static/music/` 复制到新目录（如果路径相同，无需操作）
2. 将旧的封面文件从 `app/static/music/covers/` 复制到新目录
3. 访问 `/music/list` API 或播放器，系统会自动扫描并索引文件

### 清理旧文件

在确认新系统工作正常后，可以删除以下旧文件：

- `app/templates/main/music-player.html`
- `app/templates/main/music_upload.html`
- `app/static/js/music-player.js`（可选）
- `app/static/css/music-player.css`（可选）

## 📚 API 文档

### 获取音乐列表

```
GET /music/list
```

返回：JSON 数组，包含所有音乐的元数据

### 上传音乐

```
POST /music/upload
Headers: Authorization: Bearer <token>
Form Data:
  - file: 音乐文件（MP3）
  - cover: 封面文件（可选，JPG/PNG/WEBP）
  - title: 歌曲标题（可选）
  - artist: 艺术家（可选）
```

返回：JSON 对象，包含上传后的音乐信息

### 删除音乐

```
DELETE /music/<id>
Headers: Authorization: Bearer <token>
```

返回：JSON 对象，包含删除结果

## 🎨 自定义样式

### 修改播放器主题

编辑 `app/static/css/player.css`，修改 CSS 变量：

```css
:root {
    --primary-pink: #ffd6e8;  /* 主色调 */
    --light-pink: #ffeef7;     /* 浅粉色 */
    --accent-pink: #ff9ec5;    /* 强调色 */
    /* ... */
}
```

### 禁用樱花飘落

在 `app/static/js/player.js` 中注释掉樱花初始化：

```javascript
// this.initSakura();  // 注释掉这一行
```

## 🚀 性能优化

### 文件索引

系统使用 JSON 文件存储音乐索引，首次加载时会扫描文件系统。如果音乐文件很多，可以考虑：

1. 使用数据库存储索引（需要修改 `app/music/models.py`）
2. 添加缓存机制
3. 异步加载播放列表

### 静态文件服务

生产环境建议使用 Nginx 等 Web 服务器直接服务静态文件，而不是通过 Flask。

## 📞 技术支持

如有问题，请：

1. 查看服务器日志：`logs/heartmoments.log`
2. 查看浏览器控制台
3. 检查网络请求（开发者工具）
4. 参考 `README_MUSIC_SYSTEM_NEW.md` 获取详细信息

## 📄 更新日志

### v2.0.0 (新系统)
- ✅ 全新的独立播放器窗口
- ✅ 改进的上传界面
- ✅ 状态持久化
- ✅ 樱花飘落动画效果
- ✅ 更好的错误处理
- ✅ 安全的文件上传

### v1.0.0 (旧系统)
- 基础播放器功能
- iframe 嵌入播放器
- 简单的上传功能

