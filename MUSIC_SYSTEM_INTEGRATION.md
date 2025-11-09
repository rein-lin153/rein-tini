# 音乐播放系统集成指南

## 📦 已完成的功能

### ✅ 后端功能

1. **配置文件更新** (`app/config.py`)
   - 添加 `MUSIC_FOLDER` 和 `COVER_FOLDER` 配置
   - 添加音乐文件格式和大小限制配置
   - 添加封面文件格式和大小限制配置

2. **API 接口** (`app/api/routes.py`)
   - `GET /api/music/list` - 获取音乐列表（包含封面信息）
   - `POST /api/music/upload` - 上传音乐文件（仅管理员）

3. **目录管理** (`app/__init__.py`)
   - 自动创建音乐和封面目录

### ✅ 前端功能

1. **播放器组件** (`app/templates/main/music-player.html`)
   - 独立的 iframe 播放器页面
   - 支持封面显示
   - 播放列表功能
   - 状态持久化

2. **上传页面** (`app/templates/main/music_upload.html`)
   - 拖拽上传支持
   - 上传进度显示
   - 封面预览
   - 自动刷新播放列表

3. **播放器逻辑** (`app/static/js/music-player.js`)
   - LocalStorage 状态保存
   - 播放进度恢复
   - 封面显示支持
   - 播放列表刷新功能

4. **导航优化** (`app/static/js/main.js`)
   - AJAX 无刷新导航
   - 保持播放器不中断

## 🚀 使用步骤

### 1. 确保目录存在

系统会自动创建以下目录：
- `app/static/music/` - 音乐文件目录
- `app/static/music/covers/` - 封面图片目录

### 2. 上传音乐文件

**方法一：通过管理页面上传（推荐）**

1. 登录管理员账户
2. 点击用户菜单 → "上传音乐"
3. 选择音乐文件和封面（可选）
4. 点击上传

**方法二：手动放置文件**

1. 将音乐文件放入 `app/static/music/` 目录
2. （可选）将封面图片放入 `app/static/music/covers/` 目录
3. 封面文件名应与音乐文件名相同（扩展名不同）
   - 例如：`song.mp3` 对应 `song.jpg`

### 3. 文件命名规则

**音乐文件**：
- 推荐格式：`艺术家 - 歌曲名.mp3`
- 示例：`周杰伦 - 告白气球.mp3`
- 如果不使用 " - " 分隔，文件名将作为歌曲标题

**封面文件**：
- 文件名应与音乐文件相同（扩展名不同）
- 示例：`周杰伦 - 告白气球.jpg` 对应 `周杰伦 - 告白气球.mp3`
- 支持格式：JPG、PNG、WEBP

### 4. 访问播放器

播放器会自动显示在页面顶部（如果 `ENABLE_BACKGROUND_MUSIC=True`）

## 🔧 配置说明

### 环境变量

在 `.env` 文件中可以配置：

```env
# 启用背景音乐
ENABLE_BACKGROUND_MUSIC=True

# 音乐文件大小限制（字节，默认 50MB）
MAX_MUSIC_SIZE=52428800

# 封面文件大小限制（字节，默认 5MB）
MAX_COVER_SIZE=5242880
```

### 配置文件

在 `app/config.py` 中已配置：

```python
# 音乐文件配置
MUSIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music')
COVER_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music', 'covers')
ALLOWED_MUSIC_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
ALLOWED_COVER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_MUSIC_SIZE = 50 * 1024 * 1024  # 50MB
MAX_COVER_SIZE = 5 * 1024 * 1024   # 5MB
```

## 📁 文件结构

```
app/
├── static/
│   ├── music/                    # 音乐文件目录
│   │   ├── song1.mp3            # 音乐文件
│   │   ├── song2.mp3
│   │   └── covers/              # 封面目录
│   │       ├── song1.jpg        # 封面图片
│   │       └── song2.png
│   ├── css/
│   │   └── music-player.css     # 播放器样式
│   └── js/
│       └── music-player.js      # 播放器逻辑
├── templates/
│   ├── main/
│   │   ├── music-player.html    # 播放器页面（iframe）
│   │   └── music_upload.html    # 上传页面
│   └── base.html                # 基础模板
├── api/
│   └── routes.py                # API 路由
├── main/
│   └── routes.py                # 页面路由
└── config.py                    # 配置文件
```

## 🎨 UI 特性

### 播放器样式

- **位置**：固定在页面顶部
- **样式**：渐变背景、圆角卡片、柔和阴影
- **封面**：50x50px 圆角缩略图
- **动画**：波形动画、按钮悬停效果
- **响应式**：适配移动设备

### 上传页面样式

- **拖拽上传**：支持拖拽文件到上传区域
- **进度显示**：实时显示上传进度
- **封面预览**：上传前预览封面图片
- **友好提示**：清晰的成功/错误提示

## 🔒 权限控制

### API 权限

- `GET /api/music/list` - 公开访问
- `POST /api/music/upload` - 仅管理员

### 页面权限

- `/music/upload-page` - 仅管理员

## 💾 状态持久化

### LocalStorage 存储

播放器状态自动保存到 LocalStorage：

```javascript
{
  currentTrackIndex: 0,      // 当前歌曲索引
  currentTime: 120.5,        // 播放进度（秒）
  isPlaying: true,           // 是否正在播放
  volume: 0.7,               // 音量（0-1）
  timestamp: 1234567890      // 时间戳
}
```

### 状态恢复

- 页面刷新后自动恢复播放状态
- 恢复播放进度和音量设置
- 如果之前正在播放，会尝试继续播放（可能受浏览器自动播放策略影响）

## 🐛 常见问题

### 1. 播放器不显示

**原因**：`ENABLE_BACKGROUND_MUSIC` 未启用

**解决**：在 `.env` 中设置 `ENABLE_BACKGROUND_MUSIC=True`

### 2. 音乐无法播放

**原因**：
- 音乐文件不存在
- 文件格式不支持
- 浏览器自动播放策略限制

**解决**：
- 检查音乐文件是否在正确目录
- 检查文件格式是否支持
- 用户需要手动点击播放按钮（浏览器安全策略）

### 3. 上传失败

**原因**：
- 文件过大
- 格式不支持
- 权限不足

**解决**：
- 检查文件大小是否超过限制
- 检查文件格式是否支持
- 确保已登录管理员账户

### 4. 封面不显示

**原因**：
- 封面文件不存在
- 文件名不匹配
- 文件格式不支持

**解决**：
- 检查封面文件是否在 `covers/` 目录
- 检查文件名是否与音乐文件匹配
- 检查文件格式是否支持

## 📊 API 文档

### 获取音乐列表

**请求**：
```
GET /api/music/list
```

**响应**：
```json
{
  "success": true,
  "music_list": [
    {
      "filename": "song.mp3",
      "title": "歌曲标题",
      "artist": "艺术家",
      "url": "/static/music/song.mp3",
      "cover": "/static/music/covers/song.jpg"
    }
  ],
  "count": 1
}
```

### 上传音乐

**请求**：
```
POST /api/music/upload
Content-Type: multipart/form-data

Form Data:
- music_file: 音乐文件（必需）
- cover_file: 封面图片（可选）
```

**响应**：
```json
{
  "success": true,
  "message": "上传成功",
  "filename": "song.mp3",
  "cover": "/static/music/covers/song.jpg",
  "url": "/static/music/song.mp3"
}
```

**错误响应**：
```json
{
  "success": false,
  "error": "错误信息"
}
```

## 🎯 最佳实践

### 1. 文件命名

- 使用清晰的命名规则：`艺术家 - 歌曲名.mp3`
- 避免特殊字符和空格
- 使用统一的文件格式

### 2. 封面图片

- 推荐尺寸：500x500px 或更大
- 推荐格式：JPG（文件较小）或 PNG（透明背景）
- 确保图片清晰，适合作为缩略图

### 3. 音乐文件

- 推荐格式：MP3（兼容性最好）
- 推荐比特率：128-192 kbps（平衡质量和文件大小）
- 文件大小控制在 10MB 以内（加载更快）

### 4. 性能优化

- 限制音乐文件数量（建议不超过 100 首）
- 使用适当的文件压缩
- 定期清理未使用的文件

## 🔄 更新日志

### v1.0.0 (2025-01-XX)

- ✅ 初始版本发布
- ✅ 音乐播放器功能
- ✅ 音乐上传功能
- ✅ 封面支持
- ✅ 状态持久化
- ✅ AJAX 导航
- ✅ 管理员权限控制

## 📝 待优化功能

- [ ] 音乐播放历史记录
- [ ] 收藏功能
- [ ] 播放模式（单曲循环、随机播放等）
- [ ] 歌词显示
- [ ] 音乐搜索功能
- [ ] 播放统计
- [ ] 音乐分类/标签
- [ ] 批量上传功能

## 📞 技术支持

如有问题，请：

1. 检查浏览器控制台错误信息
2. 检查服务器日志
3. 检查网络请求响应
4. 参考 `README_MUSIC_SYSTEM.md` 文档

---

**注意**：音乐文件版权归原作者所有，请确保上传的音乐文件有合法使用权。

