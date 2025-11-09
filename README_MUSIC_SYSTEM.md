# 音乐播放系统使用说明

## 📋 功能概述

这是一个完整的音乐播放系统，包括：

- 🎵 **音乐播放器**：固定在页面顶部，支持封面显示、播放控制、播放列表
- 📤 **音乐上传**：管理员可以上传音乐文件和封面图片
- 💾 **状态持久化**：播放状态自动保存到 LocalStorage，页面刷新后恢复
- 🔄 **持久播放**：使用 iframe + AJAX 导航，页面跳转时音乐不中断

## 🚀 快速开始

### 1. 目录结构

```
app/
├── static/
│   ├── music/              # 音乐文件目录
│   │   └── covers/         # 封面图片目录
│   ├── css/
│   │   └── music-player.css
│   └── js/
│       └── music-player.js
├── templates/
│   ├── main/
│   │   ├── music-player.html    # 播放器页面（iframe）
│   │   └── music_upload.html    # 上传页面
│   └── base.html
├── api/
│   └── routes.py           # 音乐API路由
└── config.py               # 配置文件
```

### 2. 配置说明

在 `config.py` 中已配置：

```python
# 音乐文件配置
MUSIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music')
COVER_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music', 'covers')
ALLOWED_MUSIC_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
ALLOWED_COVER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_MUSIC_SIZE = 50 * 1024 * 1024  # 50MB
MAX_COVER_SIZE = 5 * 1024 * 1024   # 5MB
```

### 3. API 接口

#### 获取音乐列表

```
GET /api/music/list
```

响应示例：
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

#### 上传音乐

```
POST /api/music/upload
Content-Type: multipart/form-data

Form Data:
- music_file: 音乐文件（必需）
- cover_file: 封面图片（可选）
```

**权限要求**：仅管理员可访问

响应示例：
```json
{
  "success": true,
  "message": "上传成功",
  "filename": "song.mp3",
  "cover": "/static/music/covers/song.jpg",
  "url": "/static/music/song.mp3"
}
```

## 🎨 功能特性

### 1. 播放器功能

- ✅ 播放/暂停控制
- ✅ 上一首/下一首
- ✅ 播放进度条
- ✅ 音量控制
- ✅ 播放列表
- ✅ 封面显示
- ✅ 波形动画

### 2. 持久播放

- ✅ 使用 iframe 独立运行播放器
- ✅ AJAX 导航，页面跳转不刷新
- ✅ LocalStorage 状态保存
- ✅ 自动恢复播放进度

### 3. 上传功能

- ✅ 拖拽上传
- ✅ 文件大小验证
- ✅ 上传进度显示
- ✅ 封面预览
- ✅ 自动刷新播放列表

## 📝 使用指南

### 管理员上传音乐

1. 登录管理员账户
2. 点击用户菜单 → "上传音乐"
3. 选择音乐文件（MP3、WAV、OGG、M4A、FLAC）
4. （可选）选择封面图片（JPG、PNG、WEBP）
5. 点击"上传音乐"
6. 上传成功后，播放列表自动更新

### 文件命名建议

**音乐文件**：
- 格式：`艺术家 - 歌曲名.mp3`
- 示例：`周杰伦 - 告白气球.mp3`
- 如果不使用 " - " 分隔，文件名将作为歌曲标题

**封面文件**：
- 自动匹配：封面文件名应与音乐文件名相同（扩展名不同）
- 示例：`周杰伦 - 告白气球.jpg` 对应 `周杰伦 - 告白气球.mp3`
- 或通过上传页面同时上传封面

## 🔧 技术实现

### 前端

- **播放器**：HTML5 Audio API + JavaScript
- **状态管理**：LocalStorage
- **导航**：AJAX + History API
- **UI框架**：Bootstrap 5 + 自定义CSS

### 后端

- **框架**：Flask
- **文件存储**：本地文件系统
- **权限控制**：Flask-Login
- **API格式**：JSON

### 持久播放机制

1. **iframe 隔离**：播放器运行在独立 iframe 中
2. **AJAX 导航**：拦截内部链接，使用 AJAX 加载内容
3. **状态保存**：播放进度、当前歌曲、音量等保存到 LocalStorage
4. **状态恢复**：页面加载时自动恢复播放状态

## 🐛 故障排查

### 播放器不显示

1. 检查 `ENABLE_BACKGROUND_MUSIC` 配置是否为 `True`
2. 检查浏览器控制台是否有错误
3. 检查 `/api/music/list` API 是否正常响应

### 音乐无法播放

1. 检查音乐文件是否在 `app/static/music/` 目录
2. 检查文件格式是否支持
3. 检查浏览器是否允许自动播放（可能需要用户交互）

### 上传失败

1. 检查文件大小是否超过限制
2. 检查文件格式是否支持
3. 检查管理员权限
4. 检查服务器日志

### 封面不显示

1. 检查封面文件是否在 `app/static/music/covers/` 目录
2. 检查封面文件名是否与音乐文件名匹配
3. 检查文件扩展名是否支持

## 📚 相关文件

- `app/config.py` - 配置文件
- `app/api/routes.py` - API 路由
- `app/main/routes.py` - 页面路由
- `app/templates/main/music-player.html` - 播放器页面
- `app/templates/main/music_upload.html` - 上传页面
- `app/static/js/music-player.js` - 播放器逻辑
- `app/static/css/music-player.css` - 播放器样式

## 🎯 下一步优化建议

1. 添加音乐播放历史记录
2. 添加收藏功能
3. 添加播放模式（单曲循环、随机播放等）
4. 添加歌词显示
5. 添加音乐搜索功能
6. 添加播放统计

## 📞 支持

如有问题，请检查：
1. 浏览器控制台错误信息
2. 服务器日志
3. 网络请求响应

---

**注意**：音乐文件版权归原作者所有，请确保上传的音乐文件有合法使用权。

