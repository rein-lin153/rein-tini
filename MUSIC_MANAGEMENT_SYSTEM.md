# 音乐管理系统 - 完整实现文档

## 📋 变更摘要

### 新增文件
- `app/models.py` - 添加了 `Music` 数据库模型
- `app/music/models_db.py` - 音乐数据库管理器
- `app/music/routes_api.py` - 新的 REST API 路由
- `app/templates/admin/music_manager.html` - 音乐管理界面
- `app/static/css/music-manager.css` - 管理界面样式
- `app/static/js/music-manager.js` - 管理界面脚本
- `scripts/repair_index.py` - 修复索引脚本
- `scripts/migrate_music_to_db.py` - 迁移脚本

### 修改文件
- `app/config.py` - 添加了 `ALLOWED_MUSIC_EXT`, `ALLOWED_IMAGE_EXT` 别名，更新 `MAX_MUSIC_SIZE` 为 30MB
- `app/music/__init__.py` - 导入新的 `routes_api` 模块
- `app/music/routes.py` - 更新 `/music/list` 接口以支持数据库，添加管理页面路由
- `app/music/utils.py` - 更新文件保存函数，添加音频时长检测和文件删除函数
- `app/templates/base.html` - 更新管理员菜单链接
- `app/static/js/player-embedded.js` - 添加 `loadTrackById` 方法

### 未修改文件（保持兼容）
- 播放器相关文件保持不变，继续使用 `/music/list` 接口
- 播放器样式和逻辑保持不变

## 🚀 集成步骤

### 1. 数据库迁移

#### 创建 Music 表

```bash
# 在 Flask shell 中运行
python -m flask shell

# 然后执行
from app import db
from app.models import Music
db.create_all()
```

或者使用迁移脚本：

```bash
python scripts/migrate_music_to_db.py
```

#### 从 JSON 索引迁移数据（如果存在）

如果项目之前使用 JSON 索引，运行迁移脚本：

```bash
python scripts/migrate_music_to_db.py
```

### 2. 配置检查

确保 `app/config.py` 中包含以下配置：

```python
MUSIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music')
COVER_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music', 'covers')
ALLOWED_MUSIC_EXTENSIONS = {'mp3'}
ALLOWED_COVER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_MUSIC_SIZE = 30 * 1024 * 1024  # 30MB
MAX_COVER_SIZE = 2 * 1024 * 1024   # 2MB
ADMIN_UPLOAD_TOKEN = os.environ.get('ADMIN_UPLOAD_TOKEN', 'changeme123')
```

### 3. 安装依赖（可选）

如果需要音频时长检测功能，安装 `mutagen`：

```bash
pip install mutagen
```

### 4. 确保目录存在

系统会自动创建必要的目录，但可以手动创建：

```bash
mkdir -p app/static/music/covers
```

### 5. 修复索引（如果从旧系统迁移）

运行修复脚本扫描文件系统并创建数据库记录：

```bash
python scripts/repair_index.py
```

## 🔌 API 接口

### 获取音乐列表（分页、搜索）

```
GET /music/api/music?page=1&per_page=20&q=search_term
```

**Query Parameters:**
- `page`: 页码（默认 1）
- `per_page`: 每页数量（默认 20，最大 100）
- `q`: 搜索关键词（可选，模糊搜索 title/artist）

**Response:**
```json
{
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5,
  "items": [
    {
      "id": 1,
      "title": "歌曲名",
      "artist": "艺术家",
      "filename": "song.mp3",
      "cover": "/static/music/covers/song.jpg",
      "url": "/static/music/song.mp3",
      "duration": 180.5,
      "file_size": 5242880,
      "order": 0,
      "enabled": true,
      "uploaded_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 获取单条音乐记录

```
GET /music/api/music/<id>
```

### 上传音乐

```
POST /music/api/music
Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: 音乐文件（MP3，必需）
- `cover`: 封面文件（可选，JPG/PNG/WEBP）
- `title`: 歌曲标题（可选）
- `artist`: 艺术家（可选）
- `enabled`: 是否启用（可选，默认 true）
- `order`: 排序顺序（可选，默认 0）

### 更新音乐

```
PUT /music/api/music/<id>
Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
Content-Type: multipart/form-data 或 application/json
```

### 删除音乐

```
DELETE /music/api/music/<id>
Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
```

### 批量删除

```
POST /music/api/music/batch-delete
Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
Content-Type: application/json

Body: {
  "ids": [1, 2, 3]
}
```

### 下载音乐

```
GET /music/api/music/download/<id>?attachment=true
Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN> (可选)
```

## 🧪 测试命令

### 1. 列表接口

```bash
curl -s "http://localhost:5000/music/api/music?page=1&per_page=10" | jq .
```

### 2. 上传音乐

```bash
curl -X POST "http://localhost:5000/music/api/music" \
  -H "Authorization: Bearer changeme123" \
  -F "file=@/path/to/song.mp3" \
  -F "cover=@/path/to/cover.jpg" \
  -F "title=Love Song" \
  -F "artist=Us"
```

### 3. 更新音乐

```bash
curl -X PUT "http://localhost:5000/music/api/music/1" \
  -H "Authorization: Bearer changeme123" \
  -F "title=Updated Title" \
  -F "artist=Updated Artist"
```

### 4. 替换封面

```bash
curl -X PUT "http://localhost:5000/music/api/music/1" \
  -H "Authorization: Bearer changeme123" \
  -F "cover=@/path/to/newcover.jpg"
```

### 5. 删除音乐

```bash
curl -X DELETE "http://localhost:5000/music/api/music/1" \
  -H "Authorization: Bearer changeme123"
```

### 6. 下载音乐

```bash
curl -O "http://localhost:5000/music/api/music/download/1?attachment=true" \
  -H "Authorization: Bearer changeme123"
```

### 7. 批量删除

```bash
curl -X POST "http://localhost:5000/music/api/music/batch-delete" \
  -H "Authorization: Bearer changeme123" \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3]}'
```

## 🔒 安全注意事项

1. **上传令牌**: 生产环境务必更改 `ADMIN_UPLOAD_TOKEN`，不要使用默认值 `changeme123`
2. **文件大小限制**: 默认限制为 30MB（音乐）和 2MB（封面），可在配置中调整
3. **文件类型验证**: 仅允许 MP3 格式的音乐文件和 JPG/PNG/WEBP 格式的封面
4. **路径安全**: 使用 `secure_filename` 和 UUID 前缀防止路径遍历攻击
5. **原子写入**: 所有文件操作使用临时文件 + 重命名，确保原子性
6. **权限检查**: 所有管理操作都需要管理员权限或有效的上传令牌

## 🔄 兼容性

### 播放器兼容性

- 播放器继续使用 `/music/list` 接口，该接口已更新为从数据库读取
- 如果数据库不可用，会自动回退到 JSON 索引
- 播放器只显示 `enabled=true` 的音乐

### 向后兼容

- 旧的 JSON 索引文件保留作为备份
- 可以从 JSON 索引迁移到数据库
- 文件系统扫描功能可以修复索引

## 📝 使用说明

### 管理界面

1. 登录管理员账户
2. 点击用户菜单 → "音乐管理"
3. 在管理界面中可以：
   - 查看所有音乐（分页、搜索）
   - 上传新音乐（支持封面）
   - 编辑音乐元数据
   - 删除音乐
   - 批量删除
   - 导出 CSV
   - 下载音乐文件

### 播放器集成

播放器会自动从 `/music/list` 接口加载音乐列表，只显示启用的音乐。上传新音乐后，播放器会自动刷新列表。

## 🐛 故障排查

### 数据库表不存在

运行数据库迁移：
```bash
python -m flask shell
from app import db
from app.models import Music
db.create_all()
```

### 音乐列表为空

1. 检查文件是否在 `app/static/music/` 目录
2. 运行修复脚本：`python scripts/repair_index.py`
3. 检查数据库中的记录：`Music.query.all()`

### 上传失败

1. 检查文件大小是否超过限制（30MB）
2. 检查文件格式是否为 MP3
3. 检查上传令牌是否正确
4. 查看服务器日志

### 播放器不显示音乐

1. 检查音乐是否启用（`enabled=true`）
2. 检查 `/music/list` 接口是否返回数据
3. 检查浏览器控制台错误

## 🔙 回滚建议

如果出现问题，可以：

1. **恢复 JSON 索引**：如果之前使用 JSON 索引，可以恢复 `instance/music_index.json`
2. **禁用数据库**：修改 `app/music/routes.py` 中的 `/music/list` 接口，强制使用 JSON 索引
3. **恢复旧的上传接口**：如果需要，可以恢复旧的 `/music/upload` 接口

## 📚 附加功能

### CSV 导出

管理界面提供 CSV 导出功能，导出当前筛选/页的音乐列表，包含下载 URL。

### 音频时长检测

如果安装了 `mutagen` 库，系统会自动检测音频文件的时长。

### 封面自动压缩

上传的封面图片会自动压缩到最大 800x800 像素，减少存储空间。

### 封面使用检测

删除封面时，系统会检查是否有其他记录使用同一封面，仅当无人使用时才删除文件。

## 🎨 界面特点

- 情侣主题设计（柔粉色、圆角、阴影）
- 响应式设计（支持移动设备）
- AJAX 单页风格（无需整页刷新）
- 实时进度显示（上传进度）
- Toast 通知（操作反馈）

## 📞 支持

如有问题，请查看：
- 服务器日志：`logs/heartmoments.log`
- 浏览器控制台：F12 开发者工具
- 数据库记录：使用 Flask shell 查询

