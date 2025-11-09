# 502 错误快速修复指南

## 问题原因

502 Bad Gateway 错误通常是因为：
1. **数据库表不存在** - 新增的 `music` 表尚未创建
2. **应用启动失败** - 代码错误导致应用无法启动

## 快速修复步骤

### 步骤 1: 创建数据库表（最重要）

```bash
python scripts/create_music_table.py
```

如果脚本不存在或无法运行，手动创建：

```bash
python -m flask shell
```

在 Flask shell 中执行：

```python
from app import db
from app.models import Music
db.create_all()
exit()
```

### 步骤 2: 验证表已创建

```bash
python -m flask shell
```

```python
from sqlalchemy import inspect
from app.extensions import db

inspector = inspect(db.engine)
tables = inspector.get_table_names()
print('Tables:', tables)
print('Music table exists:', 'music' in tables)
```

应该看到 `Music table exists: True`

### 步骤 3: 重启应用

```bash
# 如果使用 systemd 服务
sudo systemctl restart heartmoments

# 如果使用 Gunicorn 直接运行
pkill -f gunicorn
gunicorn -w 2 -b 127.0.0.1:8000 wsgi:app
```

### 步骤 4: 检查日志

```bash
# 查看应用日志
tail -f logs/heartmoments.log

# 如果使用 systemd
journalctl -u heartmoments -f
```

## 如果问题仍然存在

### 方案 A: 临时禁用数据库功能

修改 `app/music/routes.py`，强制使用 JSON 索引：

```python
@bp.route('/list')
def get_music_list():
    """获取音乐列表（兼容播放器接口）"""
    try:
        # 暂时使用 JSON 索引
        music_index = get_music_index()
        music_folder = current_app.config['MUSIC_FOLDER']
        cover_folder = current_app.config['COVER_FOLDER']
        allowed_extensions = current_app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3'})
        
        songs = music_index.sync_with_filesystem(
            music_folder, cover_folder, allowed_extensions
        )
        
        music_list = []
        for song in songs:
            music_list.append({
                'id': song.get('id'),
                'title': song.get('title', '未知歌曲'),
                'artist': song.get('artist', '未知艺术家'),
                'filename': song.get('filename'),
                'cover': song.get('cover'),
                'url': song.get('url', f"/static/music/{song.get('filename')}")
            })
        
        music_list.sort(key=lambda x: x['title'])
        return jsonify(music_list)
    
    except Exception as e:
        current_app.logger.error(f'获取音乐列表失败: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500
```

### 方案 B: 检查导入错误

```bash
# 检查 Python 语法
python -c "from app.music import routes_api"
python -c "from app.music import models_db"
python -c "from app.models import Music"
```

如果有错误，查看具体错误信息。

### 方案 C: 检查数据库连接

```bash
python -m flask shell
```

```python
from app.extensions import db
db.engine.connect()
```

如果连接失败，检查数据库文件路径和权限。

## 验证修复

访问以下 URL 验证：

1. **播放器接口**：`http://localhost:5000/music/list`
   - 应该返回 JSON 格式的音乐列表

2. **管理接口**：`http://localhost:5000/music/api/music`
   - 应该返回分页的音乐列表

3. **管理页面**：`http://localhost:5000/music/admin/manager`
   - 应该显示管理界面（需要登录）

## 常见错误

### 错误: "no such table: music"

**解决**：运行 `python scripts/create_music_table.py`

### 错误: "Cannot import name 'Music'"

**解决**：检查 `app/models.py` 是否正确定义了 `Music` 类

### 错误: "database is locked"

**解决**：
- 检查是否有其他进程在使用数据库
- 重启应用
- 检查数据库文件权限

## 联系支持

如果问题仍未解决，请提供：
1. 错误日志 (`logs/heartmoments.log`)
2. 数据库表检查结果
3. Python 导入测试结果

