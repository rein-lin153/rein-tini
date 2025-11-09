# 音乐系统快速开始指南

## 🚀 5 分钟快速开始

### 1. 设置环境变量

在项目根目录创建或更新 `.env` 文件：

```bash
ADMIN_UPLOAD_TOKEN=your-secret-token-here
```

### 2. 启动应用

```bash
flask run
```

### 3. 打开播放器

1. 访问 `http://localhost:5000`
2. 点击右下角的音乐按钮 🎵
3. 播放器窗口会自动打开

### 4. 上传音乐

1. 登录管理员账户
2. 点击用户菜单 → "上传音乐"
3. 选择 MP3 文件并上传
4. 播放器会自动刷新播放列表

## 📁 文件结构

```
app/
├── music/                    # 音乐模块（新增）
│   ├── __init__.py
│   ├── routes.py            # API 路由
│   ├── models.py            # 数据模型
│   └── utils.py             # 工具函数
├── static/
│   ├── music/               # 音乐文件目录
│   │   └── covers/          # 封面图片目录
│   ├── backgrounds/         # 背景图目录
│   ├── css/
│   │   ├── player.css       # 播放器样式（新增）
│   │   └── admin_upload.css # 上传页面样式（新增）
│   └── js/
│       ├── player.js        # 播放器逻辑（新增）
│       └── admin_upload.js  # 上传脚本（新增）
└── templates/
    ├── player.html          # 播放器页面（新增）
    └── admin/
        └── music_upload.html # 上传页面（新增）
```

## 🔗 主要路由

| 路由 | 方法 | 说明 |
|------|------|------|
| `/music/list` | GET | 获取音乐列表（JSON） |
| `/music/player` | GET | 播放器页面 |
| `/music/admin/upload` | GET | 上传页面（需登录） |
| `/music/upload` | POST | 上传音乐（需管理员权限） |
| `/music/<id>` | DELETE | 删除音乐（需管理员权限） |

## 🎵 播放器功能

- ✅ 播放/暂停
- ✅ 上一首/下一首
- ✅ 进度控制
- ✅ 音量控制
- ✅ 随机播放
- ✅ 循环播放
- ✅ 喜欢功能
- ✅ 播放列表
- ✅ 状态持久化

## 🔐 API 使用示例

### 获取音乐列表

```bash
curl http://localhost:5000/music/list
```

### 上传音乐

```bash
curl -X POST \
  -H "Authorization: Bearer your-token-here" \
  -F "file=@song.mp3" \
  -F "cover=@cover.jpg" \
  -F "title=歌曲标题" \
  -F "artist=艺术家" \
  http://localhost:5000/music/upload
```

## 🐛 常见问题

### 播放器无法打开

**解决方案：**
1. 检查浏览器是否阻止了弹窗
2. 检查 `/music/player` 路由是否正常
3. 查看浏览器控制台错误信息

### 播放列表为空

**解决方案：**
1. 检查 `app/static/music/` 目录是否存在
2. 检查目录中是否有 MP3 文件
3. 上传一些音乐文件

### 上传失败

**解决方案：**
1. 检查文件格式是否为 MP3
2. 检查文件大小是否超过 25MB
3. 检查管理员权限或令牌是否正确

## 📚 详细文档

- **完整文档**: `README_MUSIC_SYSTEM_NEW.md`
- **集成指南**: `INTEGRATION_GUIDE.md`
- **系统总结**: `MUSIC_SYSTEM_SUMMARY.md`

## ✨ 特性

### 独立播放器窗口
- 页面刷新不会中断播放
- 播放器可以固定在屏幕
- 状态自动保存和恢复

### 美观的 UI
- 情侣主题（粉色系）
- 樱花飘落动画效果
- 响应式设计

### 安全的上传
- 权限验证
- 文件类型验证
- 文件大小限制
- 安全的文件存储

## 🎉 开始使用

现在你可以：
1. 上传你喜欢的音乐
2. 在独立窗口中享受音乐
3. 即使刷新页面，音乐也不会中断

祝使用愉快！🎵

