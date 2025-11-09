# 当前项目说明 (Current Project Snapshot)

## 摘要

**心语时光 (HeartMoments)** 是一个基于 Flask 的情侣纪念网站，提供相册、日记、留言板、音乐管理和背景管理功能。项目使用 Python 3.6.8+、Flask 1.1.4、SQLite 数据库，部署在 Gunicorn + Nginx 架构上。目前最紧急的问题是需要确保文件上传功能在各种场景下的稳定性和错误处理完善性，特别是大文件上传时的 413 错误处理和 AJAX 导航下的页面初始化问题。

---

```json
{
  "name": "心语时光 (HeartMoments)",
  "short_description": "一个轻量、浪漫、为情侣打造的专属纪念网站，支持相册、日记、留言板、音乐管理和背景管理功能",
  "tech_stack": {
    "frontend": ["Bootstrap 5", "JavaScript (ES6+)", "AJAX", "HTML5", "CSS3"],
    "backend": ["Flask 1.1.4", "Python 3.6.8+", "SQLAlchemy 1.3.24", "Flask-Login", "Flask-WTF", "Flask-Limiter"],
    "database": ["SQLite3 (WAL模式)"],
    "devops": ["Gunicorn", "Nginx", "Systemd", "Python-dotenv"],
    "other": ["Pillow 8.4.0 (图片处理)", "bleach 3.3.0 (XSS防护)", "markdown 3.3.4", "bcrypt 3.2.0 (密码加密)", "pytz 2021.3 (时区处理)"]
  },
  "run_info": {
    "prerequisites": ["Python 3.6.8+", "pip", "virtualenv (可选)", "Nginx 1.14+ (生产环境)", "Gunicorn (生产环境)"],
    "env_files": ".env (从 env.example 复制)",
    "start_commands": [
      "python app.py (开发环境)",
      "gunicorn -w 2 -b 127.0.0.1:8000 wsgi:app (生产环境)",
      "sudo systemctl start heartmoments (Systemd服务)"
    ],
    "build_commands": [
      "pip install -r requirements.txt",
      "python scripts/init_db.py (初始化数据库)",
      "python scripts/create_admin.py (创建管理员账户)"
    ]
  },
  "repo_tree_summary": [
    {"path": "app/__init__.py", "purpose": "Flask应用工厂，初始化扩展和蓝图"},
    {"path": "app/config.py", "purpose": "配置文件，支持开发/测试/生产环境"},
    {"path": "app/models.py", "purpose": "数据库模型定义（User, Post, Photo, Comment, Anniversary, SiteSetting, Music, Background）"},
    {"path": "app/extensions.py", "purpose": "Flask扩展实例（db, login_manager, csrf, limiter）"},
    {"path": "app/auth/routes.py", "purpose": "用户认证路由（登录/登出）"},
    {"path": "app/main/routes.py", "purpose": "主页面路由（首页、设置）"},
    {"path": "app/album/routes.py", "purpose": "相册路由（展示、上传）"},
    {"path": "app/post/routes.py", "purpose": "日记路由（CRUD）"},
    {"path": "app/message/routes.py", "purpose": "留言板路由"},
    {"path": "app/api/routes.py", "purpose": "RESTful API路由（状态、日记、照片、纪念日、背景管理）"},
    {"path": "app/music/routes.py", "purpose": "音乐管理页面路由"},
    {"path": "app/music/routes_api.py", "purpose": "音乐管理API路由（上传、更新、删除）"},
    {"path": "app/music/utils.py", "purpose": "音乐处理工具函数（文件保存、封面处理、音频时长获取）"},
    {"path": "app/music/models_db.py", "purpose": "音乐数据库管理器"},
    {"path": "app/admin/routes.py", "purpose": "管理员路由（用户管理、音乐上传）"},
    {"path": "app/static/js/main.js", "purpose": "主JavaScript文件（AJAX导航、全局错误处理）"},
    {"path": "app/static/js/music-manager.js", "purpose": "音乐管理器前端逻辑"},
    {"path": "app/static/js/background-manager.js", "purpose": "背景管理器前端逻辑"},
    {"path": "app/static/js/player.js", "purpose": "音乐播放器前端逻辑"},
    {"path": "app/templates/base.html", "purpose": "基础模板（导航、footer）"},
    {"path": "app/templates/index.html", "purpose": "首页模板"},
    {"path": "app/templates/admin/music_manager.html", "purpose": "音乐管理页面模板"},
    {"path": "wsgi.py", "purpose": "WSGI入口文件（Gunicorn使用）"},
    {"path": "app.py", "purpose": "开发服务器入口文件"},
    {"path": "requirements.txt", "purpose": "Python依赖清单"},
    {"path": "env.example", "purpose": "环境变量配置示例"},
    {"path": "scripts/init_db.py", "purpose": "数据库初始化脚本"},
    {"path": "scripts/create_admin.py", "purpose": "创建管理员账户脚本"},
    {"path": "deploy/nginx.conf", "purpose": "Nginx配置文件"},
    {"path": "deploy/heartmoments.service", "purpose": "Systemd服务单元文件"},
    {"path": "docs/FIXES_SUMMARY.md", "purpose": "修复总结文档"},
    {"path": "docs/TESTING.md", "purpose": "测试清单文档"}
  ],
  "api_endpoints": [
    {
      "path": "/api/status",
      "method": "GET",
      "purpose": "获取站点状态信息（在一起天数、纪念日倒计时等）",
      "auth": "无需认证",
      "sample_request": null,
      "sample_response": {
        "status": "ok",
        "couple_names": ["Rein", "Nana"],
        "together_date": "2025-02-20",
        "days_together": 365,
        "next_anniversary": {
          "name": "一周年",
          "date": "2026-02-20",
          "days_left": 365
        }
      }
    },
    {
      "path": "/api/posts",
      "method": "GET",
      "purpose": "获取日记列表（分页）",
      "auth": "公开（未登录只返回公开日记）",
      "sample_request": {"page": 1, "per_page": 10},
      "sample_response": {
        "posts": [{"id": 1, "title": "标题", "body": "内容...", "author": "Rein", "created_at": "2025-01-01T00:00:00"}],
        "pagination": {"page": 1, "per_page": 10, "total": 100, "pages": 10}
      }
    },
    {
      "path": "/api/posts/<int:post_id>",
      "method": "GET",
      "purpose": "获取单篇日记",
      "auth": "公开（私密日记需要登录）",
      "sample_request": null,
      "sample_response": {
        "id": 1,
        "title": "标题",
        "body": "完整内容",
        "author": "Rein",
        "is_private": false,
        "created_at": "2025-01-01T00:00:00"
      }
    },
    {
      "path": "/api/photos",
      "method": "GET",
      "purpose": "获取照片列表（分页）",
      "auth": "公开",
      "sample_request": {"page": 1, "per_page": 20},
      "sample_response": {
        "photos": [{"id": 1, "filename": "photo.jpg", "url": "/uploads/photos/photo.jpg", "thumb_url": "/uploads/thumbs/thumb_photo.jpg"}],
        "pagination": {"page": 1, "per_page": 20, "total": 50}
      }
    },
    {
      "path": "/api/upload",
      "method": "POST",
      "purpose": "API图片上传（用于富文本编辑器）",
      "auth": "需要登录",
      "sample_request": {"file": "multipart/form-data"},
      "sample_response": {
        "success": true,
        "photo_id": 1,
        "url": "/uploads/photos/photo.jpg",
        "thumb_url": "/uploads/thumbs/thumb_photo.jpg"
      }
    },
    {
      "path": "/api/backgrounds",
      "method": "GET",
      "purpose": "获取背景列表",
      "auth": "公开",
      "sample_request": null,
      "sample_response": {
        "backgrounds": [{"id": 1, "filename": "bg1.jpg", "url": "/uploads/backgrounds/bg1.jpg", "is_default": true}]
      }
    },
    {
      "path": "/api/backgrounds",
      "method": "POST",
      "purpose": "上传背景图片（管理员）",
      "auth": "管理员权限或Bearer Token",
      "sample_request": {"file": "multipart/form-data", "Authorization": "Bearer <ADMIN_UPLOAD_TOKEN>"},
      "sample_response": {
        "id": 1,
        "filename": "bg1.jpg",
        "url": "/uploads/backgrounds/bg1.jpg",
        "is_default": false
      }
    },
    {
      "path": "/api/backgrounds/<int:bg_id>",
      "method": "DELETE",
      "purpose": "删除背景（管理员）",
      "auth": "管理员权限或Bearer Token",
      "sample_request": {"Authorization": "Bearer <ADMIN_UPLOAD_TOKEN>"},
      "sample_response": {"success": true}
    },
    {
      "path": "/api/backgrounds/<int:bg_id>/default",
      "method": "PUT",
      "purpose": "设置默认背景（管理员）",
      "auth": "管理员权限或Bearer Token",
      "sample_request": {"Authorization": "Bearer <ADMIN_UPLOAD_TOKEN>"},
      "sample_response": {"id": 1, "is_default": true}
    },
    {
      "path": "/api/backgrounds/default",
      "method": "GET",
      "purpose": "获取默认背景",
      "auth": "公开",
      "sample_request": null,
      "sample_response": {"id": 1, "url": "/uploads/backgrounds/bg1.jpg", "is_default": true}
    },
    {
      "path": "/music/api/music",
      "method": "GET",
      "purpose": "获取音乐列表（分页、搜索）",
      "auth": "公开（非管理员只返回启用的音乐）",
      "sample_request": {"page": 1, "per_page": 20, "q": "搜索关键词"},
      "sample_response": {
        "total": 100,
        "page": 1,
        "per_page": 20,
        "pages": 5,
        "items": [{"id": 1, "title": "歌曲名", "artist": "艺术家", "url": "/static/music/song.mp3", "duration": 180.5}]
      }
    },
    {
      "path": "/music/api/music",
      "method": "POST",
      "purpose": "上传音乐文件（管理员）",
      "auth": "管理员权限或Bearer Token",
      "sample_request": {"file": "multipart/form-data", "cover": "multipart/form-data (可选)", "title": "歌曲标题", "artist": "艺术家", "Authorization": "Bearer <ADMIN_UPLOAD_TOKEN>"},
      "sample_response": {
        "id": 1,
        "title": "歌曲名",
        "artist": "艺术家",
        "filename": "song.mp3",
        "url": "/static/music/song.mp3",
        "duration": 180.5
      }
    },
    {
      "path": "/music/api/music/<int:music_id>",
      "method": "PUT",
      "purpose": "更新音乐元数据（管理员）",
      "auth": "管理员权限或Bearer Token",
      "sample_request": {"title": "新标题", "artist": "新艺术家", "enabled": true, "Authorization": "Bearer <ADMIN_UPLOAD_TOKEN>"},
      "sample_response": {"id": 1, "title": "新标题", "artist": "新艺术家"}
    },
    {
      "path": "/music/api/music/<int:music_id>",
      "method": "DELETE",
      "purpose": "删除音乐（管理员）",
      "auth": "管理员权限或Bearer Token",
      "sample_request": {"Authorization": "Bearer <ADMIN_UPLOAD_TOKEN>"},
      "sample_response": {"success": true}
    }
  ],
  "database_schema": {
    "tables": [
      {
        "name": "users",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "username", "type": "String(64)", "notes": "用户名，唯一，索引"},
          {"name": "password_hash", "type": "String(128)", "notes": "密码哈希"},
          {"name": "display_name", "type": "String(64)", "notes": "显示名称"},
          {"name": "avatar", "type": "String(256)", "notes": "头像路径"},
          {"name": "is_admin", "type": "Boolean", "notes": "是否为管理员"},
          {"name": "created_at", "type": "DateTime", "notes": "创建时间"},
          {"name": "last_login", "type": "DateTime", "notes": "最后登录时间"}
        ]
      },
      {
        "name": "posts",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "title", "type": "String(128)", "notes": "标题"},
          {"name": "body", "type": "Text", "notes": "内容"},
          {"name": "author_id", "type": "Integer", "notes": "外键->users.id"},
          {"name": "created_at", "type": "DateTime", "notes": "创建时间，索引"},
          {"name": "updated_at", "type": "DateTime", "notes": "更新时间"},
          {"name": "is_private", "type": "Boolean", "notes": "是否私密"},
          {"name": "mood", "type": "String(32)", "notes": "心情标签"}
        ]
      },
      {
        "name": "photos",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "filename", "type": "String(256)", "notes": "原图文件名"},
          {"name": "thumb_filename", "type": "String(256)", "notes": "缩略图文件名"},
          {"name": "caption", "type": "String(256)", "notes": "图片描述"},
          {"name": "uploader_id", "type": "Integer", "notes": "外键->users.id"},
          {"name": "created_at", "type": "DateTime", "notes": "创建时间，索引"},
          {"name": "width", "type": "Integer", "notes": "原图宽度"},
          {"name": "height", "type": "Integer", "notes": "原图高度"},
          {"name": "file_size", "type": "Integer", "notes": "文件大小（字节）"},
          {"name": "location", "type": "String(128)", "notes": "拍摄地点"}
        ]
      },
      {
        "name": "comments",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "body", "type": "Text", "notes": "评论内容"},
          {"name": "author_id", "type": "Integer", "notes": "外键->users.id"},
          {"name": "created_at", "type": "DateTime", "notes": "创建时间，索引"},
          {"name": "post_id", "type": "Integer", "notes": "外键->posts.id (可选)"},
          {"name": "photo_id", "type": "Integer", "notes": "外键->photos.id (可选)"},
          {"name": "parent_id", "type": "Integer", "notes": "外键->comments.id (回复功能)"},
          {"name": "is_private", "type": "Boolean", "notes": "是否私密留言"}
        ]
      },
      {
        "name": "anniversaries",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "name", "type": "String(64)", "notes": "纪念日名称"},
          {"name": "date", "type": "Date", "notes": "日期，索引"},
          {"name": "recurrence", "type": "String(16)", "notes": "年度/一次性"},
          {"name": "description", "type": "Text", "notes": "描述"},
          {"name": "created_at", "type": "DateTime", "notes": "创建时间"}
        ]
      },
      {
        "name": "site_settings",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "key", "type": "String(64)", "notes": "配置键，唯一，索引"},
          {"name": "value", "type": "Text", "notes": "配置值"},
          {"name": "updated_at", "type": "DateTime", "notes": "更新时间"}
        ]
      },
      {
        "name": "music",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "title", "type": "String(256)", "notes": "歌曲标题，索引"},
          {"name": "artist", "type": "String(128)", "notes": "艺术家，索引"},
          {"name": "filename", "type": "String(256)", "notes": "文件名，唯一，索引"},
          {"name": "cover", "type": "String(256)", "notes": "封面文件路径"},
          {"name": "url", "type": "String(512)", "notes": "音乐文件URL"},
          {"name": "duration", "type": "Float", "notes": "时长（秒）"},
          {"name": "file_size", "type": "Integer", "notes": "文件大小（字节）"},
          {"name": "order", "type": "Integer", "notes": "排序顺序，索引"},
          {"name": "enabled", "type": "Boolean", "notes": "是否启用，索引"},
          {"name": "uploaded_at", "type": "DateTime", "notes": "上传时间，索引"},
          {"name": "updated_at", "type": "DateTime", "notes": "更新时间"}
        ]
      },
      {
        "name": "backgrounds",
        "columns": [
          {"name": "id", "type": "Integer", "notes": "主键"},
          {"name": "filename", "type": "String(256)", "notes": "文件名，唯一，索引"},
          {"name": "url", "type": "String(512)", "notes": "背景图片URL"},
          {"name": "file_size", "type": "Integer", "notes": "文件大小（字节）"},
          {"name": "width", "type": "Integer", "notes": "图片宽度"},
          {"name": "height", "type": "Integer", "notes": "图片高度"},
          {"name": "is_default", "type": "Boolean", "notes": "是否为默认背景，索引"},
          {"name": "uploaded_at", "type": "DateTime", "notes": "上传时间，索引"},
          {"name": "updated_at", "type": "DateTime", "notes": "更新时间"}
        ]
      }
    ]
  },
  "known_bugs": [
    {
      "id": "ajax-init-retry",
      "title": "AJAX导航下页面初始化可能失败",
      "severity": "medium",
      "description": "在AJAX导航切换页面时，音乐管理器和背景管理器的初始化可能因为DOM元素尚未加载完成而失败。已实现延迟重试机制（最多重试2次，间隔200ms），但在某些情况下仍可能失败。",
      "repro_steps": [
        "1. 打开浏览器，访问首页",
        "2. 点击导航栏的'主题管理'",
        "3. 快速切换到'背景管理'标签页",
        "4. 观察Console是否有初始化失败警告"
      ],
      "expected_behavior": "页面切换后，管理器和列表应自动加载并显示",
      "actual_behavior": "偶尔出现初始化失败，需要手动刷新页面",
      "logs_or_errors": [
        "[timestamp] 音乐管理页面初始化检查失败: { selector: '#music-list', exists: false }",
        "[timestamp] 背景管理页面初始化检查失败: { selector: '#background-list', exists: false }"
      ],
      "files_changed_recently": [
        "app/static/js/music-manager.js",
        "app/static/js/background-manager.js",
        "app/static/js/main.js"
      ],
      "what_i_tried": [
        "实现了元素存在性检查和延迟重试机制",
        "添加了防止重复绑定的机制",
        "支持content:loaded和pageLoaded事件",
        "添加了详细的调试日志"
      ]
    },
    {
      "id": "file-upload-413",
      "title": "大文件上传413错误处理需要完善",
      "severity": "high",
      "description": "虽然已经实现了前端和后端的文件大小检查，但在某些边界情况下（如Nginx配置不一致、网络中断等），413错误可能无法正确返回JSON格式的响应，导致前端无法正确显示错误信息。",
      "repro_steps": [
        "1. 配置Nginx的client_max_body_size为10MB",
        "2. 配置Flask的MAX_CONTENT_LENGTH为30MB",
        "3. 尝试上传15MB的文件",
        "4. 观察错误响应格式"
      ],
      "expected_behavior": "应返回JSON格式的错误响应，包含详细的错误信息",
      "actual_behavior": "在某些情况下可能返回HTML格式的错误页面",
      "logs_or_errors": [
        "413 Request Entity Too Large (HTML响应而非JSON)",
        "Nginx直接返回413错误，未到达Flask应用"
      ],
      "files_changed_recently": [
        "app/__init__.py",
        "app/music/routes_api.py",
        "app/api/routes.py",
        "deploy/nginx.conf"
      ],
      "what_i_tried": [
        "实现了前端文件大小检查",
        "实现了后端请求大小提前检查",
        "改进了413错误处理器，返回JSON格式",
        "更新了Nginx配置（client_max_body_size 50MB）"
      ]
    },
    {
      "id": "postmessage-error",
      "title": "postMessage异常处理可能不够健壮",
      "severity": "low",
      "description": "虽然已经添加了try-catch错误处理和localStorage事件回退方案，但在某些浏览器扩展环境下，postMessage可能仍然抛出异常，影响用户体验。",
      "repro_steps": [
        "1. 安装某些浏览器扩展（如广告拦截器）",
        "2. 打开音乐播放器",
        "3. 在音乐管理页面上传新音乐",
        "4. 观察Console是否有postMessage错误"
      ],
      "expected_behavior": "postMessage失败时应静默处理，使用localStorage事件回退",
      "actual_behavior": "偶尔仍会出现postMessage相关错误",
      "logs_or_errors": [
        "Failed to execute 'postMessage' on 'Window': Invalid target origin",
        "Message port closed (可能是浏览器扩展)"
      ],
      "files_changed_recently": [
        "app/static/js/music-manager.js",
        "app/static/js/player.js",
        "app/static/js/admin_upload.js",
        "app/static/js/main.js"
      ],
      "what_i_tried": [
        "添加了try-catch错误处理",
        "实现了localStorage事件回退方案",
        "添加了window.opener存在性检查",
        "添加了浏览器扩展错误的过滤"
      ]
    },
    {
      "id": "database-table-check",
      "title": "数据库表存在性检查可能不够及时",
      "severity": "medium",
      "description": "在音乐和背景管理API中，虽然实现了ensure_backgrounds_table()和表存在性检查，但在某些情况下（如数据库迁移、表删除等），检查可能不够及时，导致503错误。",
      "repro_steps": [
        "1. 删除music或backgrounds表",
        "2. 访问音乐或背景管理API",
        "3. 观察错误响应"
      ],
      "expected_behavior": "应自动创建缺失的表，或返回清晰的错误信息",
      "actual_behavior": "可能返回503错误，提示表不存在",
      "logs_or_errors": [
        "Music table does not exist. Please run: python scripts/create_music_table.py",
        "Backgrounds table does not exist, attempting to create..."
      ],
      "files_changed_recently": [
        "app/music/routes_api.py",
        "app/api/routes.py"
      ],
      "what_i_tried": [
        "实现了ensure_backgrounds_table()函数",
        "添加了表存在性检查",
        "尝试自动创建缺失的表"
      ]
    }
  ],
  "test_and_ci": {
    "has_tests": true,
    "how_to_run_tests": "pytest (运行所有测试) 或 pytest tests/test_auth.py (运行特定测试文件)",
    "ci_service": null
  },
  "last_commits": [
    {
      "sha": "760edac21f2b5267c2b50a3c8e488c7a582f99f5",
      "date": "2025-11-09 17:07:07 +0700",
      "message": "Enhance file upload handling and documentation"
    },
    {
      "sha": "573ccc03e272b4213d2f7187df3a8d5c02fc02e3",
      "date": "2025-11-09 16:54:05 +0700",
      "message": "Implement default background handling and enhance music upload error management"
    },
    {
      "sha": "76456f726cf1ee51244ccab3a71848628264529c",
      "date": "2025-11-09 16:45:54 +0700",
      "message": "Enhance error handling and CSRF protection in API routes"
    },
    {
      "sha": "e28297bc495b71ae6f956a1e6df6e2bc22288035",
      "date": "2025-11-09 16:40:13 +0700",
      "message": "Enhance background management with database validation and error handling"
    },
    {
      "sha": "f4cc49a9f934348c6923cc92b5b8b06686134d13",
      "date": "2025-11-09 16:31:33 +0700",
      "message": "Add background management functionality"
    }
  ],
  "attachments": {
    "important_files": [
      {
        "path": "app/__init__.py",
        "content_snippet": "@app.errorhandler(413)\n    def request_entity_too_large(error):\n        if is_api_request():\n            max_bytes = app.config.get('MAX_CONTENT_LENGTH', 30 * 1024 * 1024)\n            return jsonify({\n                'success': False,\n                'error': '文件过大',\n                'message': f'上传的文件超过了允许的大小限制 (最大 {max_bytes / (1024 * 1024):.2f}MB)',\n                'max_bytes': max_bytes\n            }), 413\n        return render_template('errors/413.html'), 413"
      },
      {
        "path": "app/music/routes_api.py",
        "content_snippet": "# 提前检查请求大小（如果可用）\n        max_content_length = current_app.config.get('MAX_CONTENT_LENGTH', 30 * 1024 * 1024)\n        if hasattr(request, 'content_length') and request.content_length:\n            if request.content_length > max_content_length:\n                current_app.logger.warning(f'请求内容长度超过限制: {request.content_length} bytes (最大: {max_content_length} bytes)')\n                return jsonify({\n                    'success': False,\n                    'error': '文件过大',\n                    'message': f'文件大小超过限制 (最大 {max_content_length / (1024 * 1024):.2f}MB)',\n                    'max_bytes': max_content_length\n                }), 413"
      },
      {
        "path": "app/models.py",
        "content_snippet": "class Music(db.Model):\n    \"\"\"音乐模型\"\"\"\n    \n    __tablename__ = 'music'\n    \n    id = db.Column(db.Integer, primary_key=True)\n    title = db.Column(db.String(256), nullable=False, index=True)\n    artist = db.Column(db.String(128), nullable=False, index=True)\n    filename = db.Column(db.String(256), nullable=False, unique=True, index=True)\n    cover = db.Column(db.String(256))\n    url = db.Column(db.String(512), nullable=False)\n    duration = db.Column(db.Float)\n    file_size = db.Column(db.Integer)\n    order = db.Column(db.Integer, default=0, index=True)\n    enabled = db.Column(db.Boolean, default=True, index=True)\n    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)\n    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)"
      }
    ],
    "env_example": "SECRET_KEY=your-secret-key-change-this-in-production\nFLASK_ENV=production\nFLASK_APP=wsgi.py\nDATABASE_URI=sqlite:////home/opc/rein-tini/instance/heartmoments.db\nCOUPLE_NAME_1=Rein\nCOUPLE_NAME_2=Tini\nTOGETHER_DATE=2025-02-20\nUPLOAD_FOLDER=uploads\nMAX_CONTENT_LENGTH=5242880\nPHOTOS_PER_PAGE=20\nPOSTS_PER_PAGE=10\nADMIN_UPLOAD_TOKEN=changeme123",
    "error_log_snippet": null
  },
  "priority": "fix-critical-bugs-then-deploy",
  "notes_for_next_engineer": "项目已基本稳定，主要问题集中在文件上传错误处理和AJAX导航初始化。建议优先修复大文件上传413错误的处理逻辑，确保Nginx和Flask配置一致。然后优化AJAX导航下的页面初始化，考虑使用MutationObserver监听DOM变化。测试时注意检查浏览器Console和网络请求，特别关注413错误和初始化失败的情况。如需更多信息，请查看docs/FIXES_SUMMARY.md和docs/TESTING.md文档。"
}
```

---

**建议**：修复这些bug预计需要约 2000-3000 tokens。如果遇到新的错误日志或问题，请及时更新known_bugs列表。建议在修复前先运行完整的测试套件（pytest）确保现有功能正常。

