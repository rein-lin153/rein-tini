# -*- coding: utf-8 -*-
"""
心语时光 - Gunicorn 配置文件
针对低配服务器优化（1 核 1GB 内存）
"""

import multiprocessing
import os

# 服务器套接字
bind = '127.0.0.1:8000'
backlog = 2048

# Worker 进程配置
# 公式: workers = (2 * CPU核心数) + 1
# 低配服务器建议: 2 个 worker
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
worker_class = 'sync'  # 同步 worker（内存占用最小）
worker_connections = 1000
max_requests = 1000  # 每个 worker 处理 1000 个请求后重启（防止内存泄漏）
max_requests_jitter = 50  # 随机抖动，避免所有 worker 同时重启
timeout = 30  # 超时时间（秒）
graceful_timeout = 30  # 优雅关闭超时
keepalive = 2  # Keep-Alive 连接时间

# 进程名称
proc_name = 'heartmoments'

# 守护进程（设为 False，由 systemd 管理）
daemon = False

# PID 文件
pidfile = '/var/www/heartmoments/gunicorn.pid'

# 日志配置
accesslog = '/var/www/heartmoments/logs/gunicorn_access.log'
errorlog = '/var/www/heartmoments/logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 性能优化
preload_app = True  # 预加载应用（节省内存）
sendfile = True  # 使用 sendfile 系统调用
reuse_port = True  # 允许多个进程绑定同一端口

# 安全设置
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 服务器钩子
def on_starting(server):
    """服务器启动时"""
    server.log.info("💖 心语时光正在启动...")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Bind: {bind}")

def on_reload(server):
    """服务器重载时"""
    server.log.info("💖 心语时光正在重载...")

def worker_int(worker):
    """Worker 被中断时"""
    worker.log.info("💖 Worker 正在关闭...")

def post_fork(server, worker):
    """Worker 进程 fork 后"""
    server.log.info(f"💖 Worker {worker.pid} 已启动")

def worker_abort(worker):
    """Worker 异常退出时"""
    worker.log.error(f"❌ Worker {worker.pid} 异常退出")

# 针对 1 核 1GB 内存的极限优化配置（可选）
# 如果服务器资源非常紧张，可以使用以下配置：
#
# workers = 1  # 只使用 1 个 worker
# threads = 2  # 使用线程模式
# worker_class = 'gthread'  # 线程 worker
# worker_tmp_dir = '/dev/shm'  # 使用内存作为临时目录

