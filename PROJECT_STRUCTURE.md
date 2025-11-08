# 心语时光 (HeartMoments) - 项目目录结构

```
HeartMoments/
│
├── app/                                # 应用主目录
│   ├── __init__.py                     # Flask 应用工厂，初始化扩展
│   ├── config.py                       # 配置类（开发/生产环境）
│   ├── models.py                       # 数据库模型（User, Post, Photo, Comment, Anniversary）
│   ├── extensions.py                   # Flask 扩展实例（db, login_manager, csrf）
│   │
│   ├── auth/                           # 认证蓝图
│   │   ├── __init__.py                 # 蓝图注册
│   │   ├── routes.py                   # 登录/登出路由
│   │   └── forms.py                    # 登录表单
│   │
│   ├── main/                           # 主页面蓝图
│   │   ├── __init__.py                 # 蓝图注册
│   │   ├── routes.py                   # 首页、设置页等路由
│   │   └── utils.py                    # 工具函数（日期计算）
│   │
│   ├── album/                          # 相册蓝图
│   │   ├── __init__.py                 # 蓝图注册
│   │   ├── routes.py                   # 相册展示、上传路由
│   │   ├── forms.py                    # 图片上传表单
│   │   └── image_handler.py            # 图片处理（缩略图生成、压缩）
│   │
│   ├── post/                           # 日记蓝图
│   │   ├── __init__.py                 # 蓝图注册
│   │   ├── routes.py                   # 日记 CRUD 路由
│   │   └── forms.py                    # 日记表单
│   │
│   ├── message/                        # 留言板蓝图
│   │   ├── __init__.py                 # 蓝图注册
│   │   ├── routes.py                   # 留言 CRUD 路由
│   │   └── forms.py                    # 留言表单
│   │
│   ├── api/                            # API 蓝图
│   │   ├── __init__.py                 # 蓝图注册
│   │   └── routes.py                   # RESTful API 接口
│   │
│   ├── templates/                      # Jinja2 模板
│   │   ├── base.html                   # 基础模板（导航、footer）
│   │   ├── index.html                  # 首页（Dashboard）
│   │   ├── login.html                  # 登录页面
│   │   │
│   │   ├── album/                      # 相册模板
│   │   │   ├── gallery.html            # 相册网格展示
│   │   │   ├── upload.html             # 上传页面
│   │   │   └── photo_detail.html       # 单张图片详情
│   │   │
│   │   ├── post/                       # 日记模板
│   │   │   ├── list.html               # 日记列表
│   │   │   ├── detail.html             # 日记详情
│   │   │   └── edit.html               # 编辑/新建日记
│   │   │
│   │   ├── message/                    # 留言板模板
│   │   │   └── board.html              # 留言板页面
│   │   │
│   │   └── settings/                   # 设置模板
│   │       └── index.html              # 站点设置页面
│   │
│   └── static/                         # 静态资源
│       ├── css/
│       │   ├── main.css                # 主样式表（浪漫主题）
│       │   └── animations.css          # 动画效果
│       │
│       ├── js/
│       │   ├── main.js                 # 主 JS 逻辑
│       │   ├── lazy-load.js            # 图片懒加载
│       │   └── countdown.js            # 倒计时动画
│       │
│       ├── img/                        # 默认图片资源
│       │   ├── heart.svg               # 心形图标
│       │   ├── default-bg.jpg          # 默认背景图
│       │   └── placeholder.png         # 占位图
│       │
│       └── music/                      # 背景音乐（可选）
│           └── .gitkeep
│
├── uploads/                            # 用户上传文件目录
│   ├── photos/                         # 原图
│   │   └── .gitkeep
│   ├── thumbs/                         # 缩略图
│   │   └── .gitkeep
│   └── backgrounds/                    # 自定义背景
│       └── .gitkeep
│
├── instance/                           # 实例文件夹（SQLite 数据库）
│   └── heartmoments.db                 # SQLite 数据库文件
│
├── tests/                              # 测试目录
│   ├── __init__.py
│   ├── conftest.py                     # pytest 配置
│   ├── test_auth.py                    # 认证测试
│   ├── test_models.py                  # 模型测试
│   ├── test_album.py                   # 相册测试
│   ├── test_utils.py                   # 工具函数测试
│   └── test_api.py                     # API 测试
│
├── scripts/                            # 运维脚本
│   ├── init_db.py                      # 数据库初始化脚本
│   ├── create_admin.py                 # 创建管理员账户
│   ├── backup.sh                       # 备份脚本
│   └── restore.sh                      # 恢复脚本
│
├── deployment/                         # 部署配置
│   ├── nginx.conf                      # Nginx 配置示例
│   ├── heartmoments.service            # Systemd 服务单元
│   └── gunicorn_config.py              # Gunicorn 配置
│
├── logs/                               # 日志目录
│   └── .gitkeep
│
├── .env.example                        # 环境变量示例文件
├── .gitignore                          # Git 忽略文件
├── requirements.txt                    # Python 依赖
├── app.py                              # 应用入口
├── wsgi.py                             # WSGI 入口（gunicorn）
├── README.md                           # 项目说明文档
├── DEPLOYMENT.md                       # 详细部署文档
├── SECURITY_CHECKLIST.md               # 安全检查清单
└── PROJECT_STRUCTURE.md                # 本文件：项目结构说明
```

## 文件数量统计

- Python 源码文件：约 35 个
- HTML 模板文件：约 12 个
- CSS/JS 文件：约 5 个
- 配置与脚本：约 8 个
- 文档文件：约 5 个

**总计：约 65 个文件**

## 核心模块说明

### 1. 应用工厂模式 (app/__init__.py)
- 使用 `create_app()` 工厂函数
- 支持多环境配置（开发/测试/生产）
- 集中注册蓝图和扩展

### 2. 数据库模型 (app/models.py)
- **User**: 用户表（支持双用户）
- **Post**: 日记表（支持图文）
- **Photo**: 照片表（原图+缩略图）
- **Comment**: 评论表（留言与回复）
- **Anniversary**: 纪念日表（支持年度循环）
- **SiteSetting**: 站点设置表（标题、背景等）

### 3. 蓝图架构
- **auth**: 用户认证（login/logout）
- **main**: 首页与设置
- **album**: 相册管理
- **post**: 日记管理
- **message**: 留言板
- **api**: RESTful API

### 4. 安全机制
- CSRF 保护（Flask-WTF）
- 密码哈希（bcrypt）
- XSS 防护（Bleach）
- 文件上传白名单验证
- 速率限制（Flask-Limiter）

### 5. 性能优化
- SQLite WAL 模式
- 图片自动压缩与缩略图
- 前端懒加载
- 静态资源浏览器缓存
- Gunicorn 多 worker（建议 2 个）

## 技术栈

- **后端**: Flask 1.1.4 + SQLite3
- **前端**: Bootstrap 5 + 自定义 CSS
- **服务器**: Gunicorn + Nginx
- **图片处理**: Pillow 8.4.0
- **Markdown**: bleach + markdown
- **测试**: pytest

