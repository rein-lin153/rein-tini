# 测试清单与步骤

## 概述

本文档提供完整的回归测试清单，用于验证音乐管理和背景管理功能在 AJAX 导航下的正常工作。

## 测试环境准备

1. **启动应用**：
   ```bash
   # 开发环境
   flask run
   
   # 生产环境
   gunicorn -w 4 -t 120 wsgi:app
   ```

2. **确保数据库已初始化**：
   ```bash
   python scripts/init_db.py
   ```

3. **准备测试文件**：
   - 小 MP3 文件（< 5MB）
   - 大 MP3 文件（> 30MB，用于测试文件大小限制）
   - 小背景图片（< 1MB）
   - 大背景图片（> 5MB，用于测试文件大小限制）

## 测试用例

### A. AJAX 导航初始化测试

#### A1. 音乐管理页面初始化

**测试步骤**：
1. 打开浏览器，访问首页
2. 打开浏览器开发者工具（F12），切换到 Console 标签
3. 点击导航栏的"主题管理"（原"音乐管理"）
4. 观察 Console 输出

**预期结果**：
- ✅ 不应出现 "音乐管理页面元素未找到，跳过初始化" 警告
- ✅ 应看到 "音乐管理器初始化成功" 的调试信息
- ✅ 音乐列表应自动加载并显示
- ✅ 无需手动刷新页面

**验证命令**（浏览器 Console）：
```javascript
// 检查音乐管理器是否已初始化
console.log(window.musicManager);

// 检查事件监听器
console.log('Music manager initialized:', !!window.musicManager);
```

#### A2. 背景管理页面初始化

**测试步骤**：
1. 在主题管理页面，点击"背景管理"标签页
2. 观察 Console 输出

**预期结果**：
- ✅ 不应出现 "背景管理页面元素未找到，跳过初始化" 警告
- ✅ 应看到 "背景管理器初始化成功" 的调试信息
- ✅ 背景列表应自动加载并显示
- ✅ 默认背景应自动加载并显示

**验证命令**（浏览器 Console）：
```javascript
// 检查背景管理器是否已初始化
console.log(window.backgroundManager);

// 检查事件监听器
console.log('Background manager initialized:', !!window.backgroundManager);
```

#### A3. 页面刷新后初始化

**测试步骤**：
1. 在主题管理页面，按 F5 刷新页面
2. 观察 Console 输出

**预期结果**：
- ✅ 音乐列表应在页面加载后立即显示
- ✅ 不应出现初始化失败的警告
- ✅ 所有功能应正常工作

### B. 文件上传测试

#### B1. 音乐上传 - 正常文件

**测试步骤**：
1. 在音乐管理页面，点击"上传音乐"
2. 选择一个小于 30MB 的 MP3 文件
3. 填写歌曲信息（标题、艺术家）
4. 点击"上传"按钮
5. 观察上传进度和结果

**预期结果**：
- ✅ 前端应显示上传进度条
- ✅ 上传成功后应显示成功提示
- ✅ 音乐列表应自动刷新，新上传的音乐应出现在列表中
- ✅ 不应出现 413 错误

**验证命令**（curl）：
```bash
# 替换 YOUR_ADMIN_TOKEN 和 test.mp3 为实际值
curl -X POST http://localhost:5000/music/api/music \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@test.mp3" \
  -F "title=Test Song" \
  -F "artist=Test Artist" \
  -v
```

#### B2. 音乐上传 - 超大文件（前端校验）

**测试步骤**：
1. 在音乐管理页面，点击"上传音乐"
2. 选择一个大于 30MB 的 MP3 文件
3. 观察错误提示

**预期结果**：
- ✅ 前端应立即显示错误提示："文件大小 (XX.XXMB) 超过限制 (30.00MB)，请压缩或更换文件"
- ✅ 不应发起上传请求
- ✅ 不应出现 413 错误（因为前端已拦截）

#### B3. 音乐上传 - 超大文件（后端校验）

**测试步骤**：
1. 使用 curl 或 Postman 直接发送大于 30MB 的文件
2. 观察响应

**预期结果**：
- ✅ 后端应返回 413 错误
- ✅ 响应应为 JSON 格式：`{"success": false, "error": "文件过大", "message": "...", "max_bytes": 31457280}`
- ✅ 不应返回 HTML 错误页面

**验证命令**（curl）：
```bash
# 创建一个大于 30MB 的测试文件（需要先创建）
dd if=/dev/zero of=large.mp3 bs=1M count=35

# 尝试上传
curl -X POST http://localhost:5000/music/api/music \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@large.mp3" \
  -F "title=Large File" \
  -v
```

#### B4. 背景上传 - 正常文件

**测试步骤**：
1. 在背景管理页面，点击"上传背景"
2. 选择一个小于 5MB 的 JPG 或 PNG 图片
3. 点击"上传"按钮
4. 观察上传进度和结果

**预期结果**：
- ✅ 前端应显示上传进度条
- ✅ 上传成功后应显示成功提示
- ✅ 背景列表应自动刷新
- ✅ 新上传的背景应出现在列表中

**验证命令**（curl）：
```bash
curl -X POST http://localhost:5000/api/backgrounds \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@background.jpg" \
  -v
```

#### B5. 背景上传 - 超大文件（前端校验）

**测试步骤**：
1. 在背景管理页面，点击"上传背景"
2. 选择一个大于 5MB 的图片文件
3. 观察错误提示

**预期结果**：
- ✅ 前端应立即显示错误提示："文件大小 (XX.XXMB) 超过限制 (5.00MB)，请压缩或更换文件"
- ✅ 不应发起上传请求

### C. 错误处理测试

#### C1. postMessage 异常处理

**测试步骤**：
1. 打开浏览器开发者工具
2. 在 Console 中运行：
   ```javascript
   // 模拟 message port 关闭错误
   Promise.reject(new Error('The message port closed before a response was received'))
     .catch(err => console.log('Caught:', err));
   ```
3. 上传一首音乐
4. 观察 Console 输出

**预期结果**：
- ✅ 不应出现未捕获的 Promise 拒绝错误
- ✅ postMessage 失败时应使用 localStorage 事件作为回退
- ✅ 不应影响正常功能

#### C2. 413 错误 JSON 响应

**测试步骤**：
1. 使用 curl 发送超大文件请求
2. 检查响应内容类型

**预期结果**：
- ✅ 响应 Content-Type 应为 `application/json`
- ✅ 响应体应为 JSON 格式
- ✅ 不应返回 HTML 错误页面

**验证命令**（curl）：
```bash
curl -X POST http://localhost:5000/music/api/music \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@large.mp3" \
  -v 2>&1 | grep -i "content-type"
```

### D. 日志测试

#### D1. 上传日志记录

**测试步骤**：
1. 上传一首音乐
2. 查看服务器日志

**预期结果**：
- ✅ 日志应记录：`音乐上传请求: 文件名=xxx.mp3, 来源IP=xx.xx.*.*`
- ✅ 上传成功后应记录：`音乐上传成功: xxx.mp3 (ID: x)`
- ✅ IP 地址应脱敏处理（只显示前两段）

#### D2. 初始化日志记录

**测试步骤**：
1. 通过 AJAX 导航进入主题管理页面
2. 查看浏览器 Console

**预期结果**：
- ✅ 应看到详细的初始化日志，包括 URL、时间戳、选择器信息
- ✅ 初始化失败时应记录详细的调试信息

## 浏览器测试步骤

### 1. Chrome/Edge 测试

1. **打开开发者工具**：
   - 按 F12 或右键 -> 检查
   - 切换到 Console 标签

2. **测试 AJAX 导航**：
   - 点击导航栏的"主题管理"
   - 观察 Console 输出
   - 验证音乐列表是否自动加载

3. **测试文件上传**：
   - 尝试上传正常大小的文件
   - 尝试上传超大文件
   - 观察错误提示

4. **测试错误处理**：
   - 检查是否有未捕获的错误
   - 检查 postMessage 异常是否被正确处理

### 2. Firefox 测试

1. **打开开发者工具**：
   - 按 F12
   - 切换到 Console 标签

2. **重复 Chrome 测试步骤**

### 3. Safari 测试

1. **启用开发者工具**：
   - 偏好设置 -> 高级 -> 显示开发菜单
   - 开发 -> 显示 Web 检查器

2. **重复 Chrome 测试步骤**

## 性能测试

### 1. 大文件上传性能

**测试步骤**：
1. 上传一个接近 30MB 的 MP3 文件
2. 测量上传时间
3. 观察服务器资源使用情况

**预期结果**：
- ✅ 上传应在合理时间内完成（< 60 秒，取决于网络速度）
- ✅ 服务器内存使用应稳定
- ✅ 不应出现超时错误

### 2. AJAX 导航性能

**测试步骤**：
1. 多次点击导航栏切换页面
2. 观察页面加载时间
3. 检查内存泄漏

**预期结果**：
- ✅ 页面切换应流畅
- ✅ 不应出现内存泄漏
- ✅ 初始化时间应 < 500ms

## 回归测试清单

- [ ] A1. 音乐管理页面 AJAX 初始化
- [ ] A2. 背景管理页面 AJAX 初始化
- [ ] A3. 页面刷新后初始化
- [ ] B1. 音乐上传 - 正常文件
- [ ] B2. 音乐上传 - 超大文件（前端校验）
- [ ] B3. 音乐上传 - 超大文件（后端校验）
- [ ] B4. 背景上传 - 正常文件
- [ ] B5. 背景上传 - 超大文件（前端校验）
- [ ] C1. postMessage 异常处理
- [ ] C2. 413 错误 JSON 响应
- [ ] D1. 上传日志记录
- [ ] D2. 初始化日志记录

## 故障排查

### 问题：音乐列表不显示

**检查清单**：
1. 检查 Console 是否有错误
2. 检查网络请求是否成功
3. 检查数据库表是否存在
4. 检查管理员权限

**解决方案**：
```bash
# 检查数据库表
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(db.engine.table_names())"

# 重新初始化数据库
python scripts/init_db.py
```

### 问题：上传返回 413 错误

**检查清单**：
1. 检查 Nginx 配置中的 `client_max_body_size`
2. 检查 Flask 配置中的 `MAX_CONTENT_LENGTH`
3. 检查文件实际大小

**解决方案**：
```bash
# 检查 Nginx 配置
nginx -T | grep client_max_body_size

# 修改 Nginx 配置后重启
sudo nginx -s reload
```

### 问题：postMessage 错误

**检查清单**：
1. 检查是否有浏览器扩展干扰
2. 检查错误处理代码是否正确
3. 检查 localStorage 是否可用

**解决方案**：
- 禁用浏览器扩展后重试
- 检查全局错误处理器是否正确设置

## 参考

- [上传配置文档](UPLOAD_CONFIG.md)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Nginx 文档](http://nginx.org/en/docs/)

