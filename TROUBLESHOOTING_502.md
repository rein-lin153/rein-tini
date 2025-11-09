# 502 Bad Gateway 错误排查指南

## 问题描述

修改代码后，重启应用出现 502 Bad Gateway 错误。

## 可能的原因

### 1. 数据库表不存在

**问题**：新增的 `Music` 数据库表尚未创建，导致应用启动或运行时出错。

**解决方案**：

```bash
# 创建数据库表
python scripts/create_music_table.py
```

或者手动创建：

```bash
python -m flask shell
```

```python
from app import db
from app.models import Music
db.create_all()
```

### 2. 导入错误

**问题**：新添加的模块导入失败。

**检查方法**：

```bash
# 检查 Python 语法
python -m py_compile app/music/routes_api.py
python -m py_compile app/music/models_db.py
python -m py_compile app/models.py
```

### 3. 循环导入

**问题**：模块之间存在循环导入。

**检查**：查看 `app/music/__init__.py` 是否正确导入。

### 4. 应用启动失败

**检查日志**：

```bash
# 查看应用日志
tail -f logs/heartmoments.log

# 查看 Gunicorn 错误日志（如果使用）
tail -f logs/gunicorn-error.log
```

### 5. 数据库连接问题

**问题**：数据库连接失败。

**检查**：
- 数据库文件是否存在
- 数据库文件权限是否正确
- 数据库路径配置是否正确

## 快速修复步骤

### 步骤 1: 创建数据库表

```bash
python scripts/create_music_table.py
```

### 步骤 2: 检查应用启动

```bash
# 直接运行应用（开发模式）
python app.py
```

查看是否有错误信息。

### 步骤 3: 检查 Gunicorn（如果使用）

```bash
# 检查 Gunicorn 服务状态
systemctl status heartmoments

# 查看错误日志
journalctl -u heartmoments -n 50
```

### 步骤 4: 回退到 JSON 索引（临时方案）

如果数据库表创建有问题，可以临时禁用数据库功能：

修改 `app/music/routes.py` 中的 `/music/list` 接口，强制使用 JSON 索引：

```python
@bp.route('/list')
def get_music_list():
    """获取音乐列表（兼容播放器接口）"""
    try:
        # 暂时禁用数据库，使用 JSON 索引
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

## 验证修复

### 1. 检查数据库表

```bash
python -m flask shell
```

```python
from app.models import Music
from app.extensions import db
from sqlalchemy import inspect

inspector = inspect(db.engine)
tables = inspector.get_table_names()
print('Tables:', tables)
print('Music table exists:', 'music' in tables)
```

### 2. 测试 API 接口

```bash
# 测试列表接口
curl http://localhost:5000/music/list

# 测试管理接口
curl http://localhost:5000/music/api/music
```

### 3. 检查应用日志

查看日志文件，确认没有错误：

```bash
tail -f logs/heartmoments.log
```

## 常见错误信息

### 错误 1: "no such table: music"

**原因**：数据库表不存在

**解决**：运行 `python scripts/create_music_table.py`

### 错误 2: "Cannot import name 'Music'"

**原因**：导入错误

**解决**：检查 `app/models.py` 是否正确定义了 `Music` 模型

### 错误 3: "Circular import"

**原因**：循环导入

**解决**：检查 `app/music/__init__.py` 的导入顺序

### 错误 4: "OperationalError: database is locked"

**原因**：数据库被锁定

**解决**：
- 检查是否有其他进程在使用数据库
- 重启应用
- 检查 SQLite WAL 模式是否启用

## 预防措施

1. **创建数据库表**：在部署前运行 `python scripts/create_music_table.py`
2. **测试启动**：在部署前测试应用启动
3. **查看日志**：定期查看应用日志，及时发现问题
4. **备份数据库**：在修改前备份数据库

## 联系支持

如果问题仍未解决，请提供：
1. 错误日志（`logs/heartmoments.log`）
2. Gunicorn 错误日志（如果使用）
3. 数据库表检查结果
4. 应用启动测试结果

