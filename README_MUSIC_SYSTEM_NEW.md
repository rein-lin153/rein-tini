# 新音乐播放系统 - 实现文档

## 📋 变更摘要

### 删除的旧实现
- 删除了 `app/main/routes.py` 中的 `/music-player` 和 `/music/upload-page` 路由
- 删除了 `app/api/routes.py` 中的 `/api/music/list` 和 `/api/music/upload` 路由
- 从 `app/templates/base.html` 移除了旧的 iframe 播放器
- 旧播放器模板和静态文件已不再使用（可选择性删除）

### 新增的文件
1. **后端模块** (`app/music/`)
   - `__init__.py` - 蓝图初始化
   - `routes.py` - REST API 路由
   - `models.py` - 音乐索引管理（JSON 文件存储）
   - `utils.py` - 文件保存和验证工具

2. **前端文件**
   - `app/templates/player.html` - 独立播放器窗口页面
   - `app/templates/admin/music_upload.html` - 管理员上传页面
   - `app/static/css/player.css` - 播放器样式（情侣主题 + 樱花飘落）
   - `app/static/css/admin_upload.css` - 上传页面样式
   - `app/static/js/player.js` - 播放器逻辑
   - `app/static/js/admin_upload.js` - 上传脚本

3. **配置文件更新**
   - `app/config.py` - 添加音乐相关配置
   - `app/__init__.py` - 注册音乐蓝图，修复目录创建

## 🎯 实现方案说明

### 选择的方案：独立播放器窗口（选项 2）

**为什么选择独立窗口？**
1. **最小侵入性**：不需要修改现有页面的导航逻辑
2. **真正持久**：独立窗口的生命周期独立于主窗口，页面刷新不会中断播放
3. **用户体验好**：播放器可以固定在屏幕，不受主窗口影响
4. **实现简单**：使用 `window.open()` 即可实现，无需复杂的 SPA 改造

**工作原理：**
- 主站点右下角显示"打开音乐播放器"按钮
- 点击按钮打开独立窗口（`/music/player`）
- 播放器窗口使用 localStorage 保存播放状态
- 主窗口和播放器窗口通过 `postMessage` 通信
- 即使主窗口刷新，播放器窗口继续播放

### 备选方案：SPA 改造（可选）

如果将来需要将站点改造为 SPA，可以参考 `app/static/js/main.js` 中已实现的 AJAX 导航功能。但当前实现使用独立窗口，已经完美解决了"页面刷新不中断播放"的问题。

## 🚀 集成说明

### 1. 配置文件设置

在 `.env` 文件中设置管理员上传令牌：

```bash
ADMIN_UPLOAD_TOKEN=your-secret-token-here
```

**重要**：生产环境请务必更改默认令牌！

### 2. 目录结构

系统会自动创建以下目录：
- `app/static/music/` - 音乐文件目录
- `app/static/music/covers/` - 封面图片目录
- `app/static/backgrounds/` - 背景图目录
- `instance/` - 音乐索引文件（`music_index.json`）

### 3. 蓝图注册

音乐模块已在 `app/__init__.py` 中自动注册：

```python
from app.music import bp as music_bp
app.register_blueprint(music_bp)
```

### 4. 路由列表

#### 音乐播放相关
- `GET /music/list` - 获取音乐列表（JSON）
- `GET /music/player` - 独立播放器页面

#### 管理员功能
- `GET /music/admin/upload` - 上传页面（需登录 + 管理员）
- `POST /music/upload` - 上传音乐（需管理员权限或令牌）
- `DELETE /music/<id>` - 删除音乐（需管理员权限或令牌）
- `GET /music/backgrounds` - 获取背景图列表
- `POST /music/backgrounds/upload` - 上传背景图

### 5. 模板集成

#### base.html 更新
- 移除了旧的 iframe 播放器
- 添加了"打开音乐播放器"浮动按钮
- 更新了上传音乐链接指向新路由

#### 导航栏更新
- 管理员菜单中的"上传音乐"链接已更新为 `/music/admin/upload`

## 📝 API 使用说明

### 获取音乐列表

```bash
curl http://localhost:5000/music/list
```

返回格式：
```json
[
  {
    "id": 1,
    "title": "歌曲名",
    "artist": "艺术家",
    "filename": "song.mp3",
    "cover": "/static/music/covers/song.jpg",
    "url": "/static/music/song.mp3"
  }
]
```

### 上传音乐（使用令牌）

```bash
curl -X POST \
  -H "Authorization: Bearer your-token-here" \
  -F "file=@song.mp3" \
  -F "cover=@cover.jpg" \
  -F "title=歌曲标题" \
  -F "artist=艺术家" \
  http://localhost:5000/music/upload
```

### 上传音乐（管理员登录）

如果已登录管理员账户，可以通过 session 验证：

```bash
# 在浏览器中登录后，使用浏览器的开发者工具发送请求
# 或使用带 Cookie 的 curl 请求
```

## 🎨 前端特性

### 播放器功能
- ✅ 播放/暂停
- ✅ 上一首/下一首
- ✅ 进度条控制
- ✅ 音量控制
- ✅ 随机播放
- ✅ 循环播放（无/列表/单曲）
- ✅ 喜欢功能
- ✅ 播放列表
- ✅ 封面显示
- ✅ 状态持久化（localStorage）
- ✅ 播放进度恢复

### UI 特性
- ✅ 情侣主题（粉色系）
- ✅ 樱花飘落动画效果
- ✅ 响应式设计（支持移动端）
- ✅ 毛玻璃效果
- ✅ 平滑动画过渡

## 🔒 安全与权限

### 上传权限验证
1. **令牌验证**：使用 `Authorization: Bearer <token>` 头
2. **Session 验证**：管理员登录后可通过 session 验证
3. **文件验证**：
   - 仅支持 MP3 格式
   - 文件大小限制：25MB
   - 封面大小限制：2MB
   - 文件名安全处理（`secure_filename`）

### 文件存储
- 使用 UUID 前缀避免文件名冲突
- 原子写入（先写临时文件，再重命名）
- 路径白名单验证
- 文件类型严格验证

## 🧪 测试步骤

### 1. 启动应用

```bash
# 设置环境变量
export ADMIN_UPLOAD_TOKEN=test123
export FLASK_ENV=development

# 启动 Flask
flask run
```

### 2. 测试播放器

1. 访问 `http://localhost:5000`
2. 点击右下角的音乐按钮
3. 播放器窗口应该打开
4. 播放列表应该自动加载
5. 测试播放、暂停、上一首、下一首等功能

### 3. 测试上传

1. 登录管理员账户
2. 访问 `http://localhost:5000/music/admin/upload`
3. 选择 MP3 文件上传
4. 可选：上传封面图片
5. 点击上传
6. 播放器应该自动刷新播放列表

### 4. 测试 API

```bash
# 获取音乐列表
curl http://localhost:5000/music/list

# 上传音乐（使用令牌）
curl -X POST \
  -H "Authorization: Bearer test123" \
  -F "file=@test.mp3" \
  -F "title=测试歌曲" \
  -F "artist=测试艺术家" \
  http://localhost:5000/music/upload
```

### 5. 测试持久播放

1. 打开播放器窗口
2. 播放一首歌曲
3. 刷新主窗口（F5）
4. 播放器窗口应该继续播放，不受影响

## 🐛 已知问题与限制

### 浏览器兼容性
- 独立窗口功能在所有现代浏览器中支持良好
- `postMessage` API 需要同源策略
- localStorage 在所有现代浏览器中支持

### 自动播放限制
- 浏览器可能阻止自动播放（需要用户交互）
- 播放器会在用户点击播放按钮后开始播放

### 文件大小限制
- 音乐文件：最大 25MB
- 封面文件：最大 2MB
- 可在 `app/config.py` 中调整

## 📚 后续改进建议

### 1. 迷你控制器（可选）
可以在主窗口添加一个迷你播放控制器，显示当前播放的歌曲信息，通过 `postMessage` 与播放器窗口通信。

### 2. SPA 改造（可选）
如果需要将整个站点改造为 SPA，可以：
1. 使用 Turbolinks 或类似的库
2. 或者使用 React/Vue 等框架
3. 播放器可以作为全局组件内嵌在所有页面

### 3. 音频可视化
可以添加音频频谱可视化效果，使用 Web Audio API。

### 4. 歌词显示
可以添加歌词显示功能，支持 LRC 格式。

## 🔧 故障排查

### 播放器无法打开
- 检查浏览器是否阻止了弹窗
- 检查 `/music/player` 路由是否正常
- 查看浏览器控制台错误信息

### 上传失败
- 检查文件格式是否为 MP3
- 检查文件大小是否超过限制
- 检查管理员权限或令牌是否正确
- 查看服务器日志

### 播放列表为空
- 检查 `app/static/music/` 目录是否存在
- 检查目录中是否有 MP3 文件
- 检查文件权限
- 查看服务器日志

### 播放状态未恢复
- 检查浏览器是否允许 localStorage
- 检查 localStorage 中是否有 `musicPlayerState`
- 清除浏览器缓存后重试

## 📞 支持

如有问题，请检查：
1. 服务器日志 (`logs/heartmoments.log`)
2. 浏览器控制台
3. 网络请求（开发者工具）

## 📄 许可证

本项目遵循原有项目的许可证。

