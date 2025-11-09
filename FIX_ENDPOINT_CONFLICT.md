# 修复端点冲突问题

## 问题描述

错误信息：
```
AssertionError: View function mapping is overwriting an existing endpoint function: music.delete_music
```

## 原因

有两个路由函数都注册了同一个端点 `music.delete_music`：

1. `app/music/routes.py` 中的 `delete_music` 函数
   - 路由：`@bp.route('/<int:song_id>', methods=['DELETE'])`
   - 端点：`music.delete_music`

2. `app/music/routes_api.py` 中的 `delete_music` 函数
   - 路由：`@bp.route('/api/music/<int:music_id>', methods=['DELETE'])`
   - 端点：`music.delete_music`

虽然路由路径不同，但 Flask 使用函数名作为端点名，所以两个函数都注册为 `music.delete_music`，导致冲突。

## 解决方案

已删除 `app/music/routes.py` 中的旧 `delete_music` 函数，因为：

1. 新的 API 在 `routes_api.py` 中，功能更完整
2. 新的 API 路径更清晰：`/music/api/music/<id>`
3. 新的 API 使用数据库，而旧的 API 使用 JSON 索引

## 修复后的路由

### 删除音乐（新 API）

```
DELETE /music/api/music/<music_id>
Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
```

### 兼容性

- 旧的 `DELETE /music/<song_id>` 路由已移除
- 所有删除操作应使用新的 API：`DELETE /music/api/music/<music_id>`
- 管理界面已更新为使用新 API

## 验证修复

1. **重启应用**：
```bash
sudo systemctl restart heartmoments
# 或
pkill -f gunicorn
gunicorn -w 2 -b 127.0.0.1:8000 wsgi:app
```

2. **测试应用启动**：
```bash
python scripts/fix_502_error.py
```

应该看到：
```
✅ 应用可以正常创建
```

3. **测试删除 API**：
```bash
curl -X DELETE "http://localhost:5000/music/api/music/1" \
  -H "Authorization: Bearer changeme123"
```

## 其他可能的路由冲突

如果还有其他路由冲突，检查方法：

```bash
# 检查所有路由函数名
grep -r "def.*music" app/music/

# 检查所有路由定义
grep -r "@bp.route" app/music/
```

## 预防措施

1. **使用不同的函数名**：如果需要在同一个蓝图中定义相似功能，使用不同的函数名
2. **使用不同的蓝图**：将不同功能分离到不同的蓝图
3. **使用 endpoint 参数**：在 `@bp.route` 中指定 `endpoint` 参数

例如：
```python
@bp.route('/old-path', endpoint='old_delete_music')
def delete_music_old():
    pass

@bp.route('/new-path', endpoint='new_delete_music')
def delete_music_new():
    pass
```

## 相关文件

- `app/music/routes.py` - 旧路由（已移除 delete_music）
- `app/music/routes_api.py` - 新 API 路由
- `app/music/__init__.py` - 蓝图初始化

