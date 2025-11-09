# 音乐管理系统集成检查清单

## ✅ 前置检查

- [ ] 确认项目使用 SQLAlchemy 数据库
- [ ] 确认 `app/extensions.py` 中有 `db` 实例
- [ ] 确认 `app/__init__.py` 中已初始化数据库
- [ ] 确认 `app/config.py` 中包含数据库配置

## 📦 文件检查

### 新增文件
- [ ] `app/models.py` - 包含 `Music` 模型
- [ ] `app/music/models_db.py` - 音乐数据库管理器
- [ ] `app/music/routes_api.py` - REST API 路由
- [ ] `app/templates/admin/music_manager.html` - 管理界面
- [ ] `app/static/css/music-manager.css` - 管理界面样式
- [ ] `app/static/js/music-manager.js` - 管理界面脚本
- [ ] `scripts/repair_index.py` - 修复索引脚本
- [ ] `scripts/migrate_music_to_db.py` - 迁移脚本
- [ ] `scripts/create_music_table.py` - 创建表脚本

### 修改文件
- [ ] `app/config.py` - 添加了配置项
- [ ] `app/music/__init__.py` - 导入 routes_api
- [ ] `app/music/routes.py` - 更新列表接口
- [ ] `app/music/utils.py` - 更新工具函数
- [ ] `app/templates/base.html` - 更新菜单链接
- [ ] `app/static/js/player-embedded.js` - 添加 loadTrackById

## 🗄️ 数据库检查

- [ ] 运行 `python scripts/create_music_table.py` 创建表
- [ ] 检查数据库中的 `music` 表是否存在
- [ ] 检查表结构是否正确（id, title, artist, filename, cover, url, duration, file_size, order, enabled, uploaded_at, updated_at）

## ⚙️ 配置检查

- [ ] `MUSIC_FOLDER` 配置正确
- [ ] `COVER_FOLDER` 配置正确
- [ ] `ALLOWED_MUSIC_EXTENSIONS` 包含 `{'mp3'}`
- [ ] `ALLOWED_COVER_EXTENSIONS` 包含 `{'jpg', 'jpeg', 'png', 'webp'}`
- [ ] `MAX_MUSIC_SIZE` 设置为 30MB
- [ ] `MAX_COVER_SIZE` 设置为 2MB
- [ ] `ADMIN_UPLOAD_TOKEN` 已设置（生产环境请更改默认值）

## 📁 目录检查

- [ ] `app/static/music/` 目录存在
- [ ] `app/static/music/covers/` 目录存在
- [ ] 目录权限正确（可读写）

## 🔌 API 测试

### 基础接口
- [ ] `GET /music/api/music` - 获取列表（无需认证）
- [ ] `GET /music/api/music?page=1&per_page=10` - 分页
- [ ] `GET /music/api/music?q=search` - 搜索
- [ ] `GET /music/api/music/1` - 获取单条记录

### 管理接口（需要认证）
- [ ] `POST /music/api/music` - 上传音乐
- [ ] `PUT /music/api/music/1` - 更新音乐
- [ ] `DELETE /music/api/music/1` - 删除音乐
- [ ] `POST /music/api/music/batch-delete` - 批量删除
- [ ] `GET /music/api/music/download/1` - 下载音乐

### 兼容接口
- [ ] `GET /music/list` - 播放器接口（应返回启用的音乐）

## 🎨 界面测试

- [ ] 访问 `/music/admin/manager` 显示管理界面
- [ ] 上传音乐文件功能正常
- [ ] 上传封面功能正常
- [ ] 编辑音乐功能正常
- [ ] 删除音乐功能正常
- [ ] 批量删除功能正常
- [ ] 搜索功能正常
- [ ] 分页功能正常
- [ ] CSV 导出功能正常
- [ ] 下载功能正常

## 🎵 播放器测试

- [ ] 播放器能正常加载音乐列表
- [ ] 播放器只显示启用的音乐
- [ ] 上传新音乐后播放器自动刷新
- [ ] 播放器播放功能正常
- [ ] 播放器控制功能正常

## 🔒 安全测试

- [ ] 未认证用户无法上传音乐
- [ ] 未认证用户无法删除音乐
- [ ] 未认证用户无法编辑音乐
- [ ] 无效 token 无法访问管理接口
- [ ] 文件类型验证正常（仅允许 MP3）
- [ ] 文件大小限制正常（30MB）
- [ ] 路径安全（防止路径遍历）

## 🐛 错误处理

- [ ] 文件不存在时返回 404
- [ ] 文件过大时返回错误
- [ ] 文件类型错误时返回错误
- [ ] 权限不足时返回 403
- [ ] 服务器错误时返回 500
- [ ] 错误信息清晰明确

## 📊 数据迁移（如果需要）

- [ ] 如果使用 JSON 索引，运行迁移脚本
- [ ] 检查迁移后的数据完整性
- [ ] 验证播放器仍能正常加载音乐

## 🚀 部署检查

- [ ] 生产环境更改 `ADMIN_UPLOAD_TOKEN`
- [ ] 检查文件存储路径权限
- [ ] 检查数据库连接配置
- [ ] 检查日志文件路径
- [ ] 检查静态文件服务配置

## 📝 文档检查

- [ ] 阅读 `MUSIC_MANAGEMENT_SYSTEM.md`
- [ ] 阅读 API 文档
- [ ] 阅读测试命令
- [ ] 阅读安全注意事项

## ✅ 完成检查

- [ ] 所有功能测试通过
- [ ] 所有安全检查通过
- [ ] 播放器兼容性确认
- [ ] 文档完整
- [ ] 代码无错误（linter 检查通过）

---

## 🔧 故障排查

如果遇到问题，请检查：

1. **数据库表不存在**
   - 运行 `python scripts/create_music_table.py`

2. **音乐列表为空**
   - 运行 `python scripts/repair_index.py`
   - 检查文件是否在 `app/static/music/` 目录

3. **上传失败**
   - 检查文件大小是否超过限制
   - 检查文件格式是否为 MP3
   - 检查上传令牌是否正确
   - 查看服务器日志

4. **播放器不显示音乐**
   - 检查音乐是否启用（`enabled=true`）
   - 检查 `/music/list` 接口是否返回数据
   - 检查浏览器控制台错误

5. **权限问题**
   - 检查用户是否为管理员
   - 检查上传令牌是否正确
   - 检查 session 是否有效

---

## 📞 支持

如有问题，请查看：
- 服务器日志：`logs/heartmoments.log`
- 浏览器控制台：F12 开发者工具
- 数据库记录：使用 Flask shell 查询

