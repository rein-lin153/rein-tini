/**
 * 音乐上传工具函数
 * 统一处理音乐文件上传逻辑
 */

/**
 * 上传音乐文件
 * @param {Object} options 上传选项
 * @param {File} options.musicFile - 音乐文件
 * @param {File} [options.coverFile] - 封面文件（可选）
 * @param {string} [options.title] - 歌曲标题（可选）
 * @param {string} [options.artist] - 艺术家（可选）
 * @param {string} [options.order] - 排序（可选）
 * @param {boolean} [options.enabled] - 是否启用（可选）
 * @param {string} [options.token] - 管理员令牌（可选）
 * @param {Function} options.onProgress - 进度回调函数 (percent) => {}
 * @param {Function} options.onSuccess - 成功回调函数 (data) => {}
 * @param {Function} options.onError - 错误回调函数 (error) => {}
 * @param {Function} [options.onStart] - 开始上传回调函数 () => {}
 * @param {Function} [options.onFinish] - 完成回调函数 () => {}
 * @param {number} [options.timeout] - 超时时间（毫秒），默认 5 分钟
 * @param {string} [options.endpoint] - API 端点，默认 '/music/upload'
 */
function uploadMusicFile(options) {
    const {
        musicFile,
        coverFile = null,
        title = '',
        artist = '',
        order = '0',
        enabled = true,
        token = null,
        onProgress,
        onSuccess,
        onError,
        onStart = () => {},
        onFinish = () => {},
        timeout = 5 * 60 * 1000, // 5 分钟
        endpoint = '/music/upload' // 默认端点
    } = options;
    
    // 强制使用 /music/upload 端点，防止误用 /music/api/music
    endpoint = '/music/upload';

    // 验证必需参数
    if (!musicFile) {
        onError('请选择音乐文件');
        return;
    }

    // 客户端文件大小检查
    const maxMusicSize = window.APP_CONFIG?.MAX_MUSIC_SIZE || window.APP_CONFIG?.MAX_CONTENT_LENGTH || (30 * 1024 * 1024); // 默认 30MB
    if (musicFile.size > maxMusicSize) {
        const maxSizeMB = (maxMusicSize / (1024 * 1024)).toFixed(2);
        const fileSizeMB = (musicFile.size / (1024 * 1024)).toFixed(2);
        onError(`文件大小 (${fileSizeMB}MB) 超过限制 (${maxSizeMB}MB)，请压缩或更换文件`);
        return;
    }

    // 检查封面文件大小（如果提供了封面）
    if (coverFile) {
        const maxCoverSize = window.APP_CONFIG?.MAX_COVER_SIZE || (2 * 1024 * 1024); // 默认 2MB
        if (coverFile.size > maxCoverSize) {
            const maxCoverSizeMB = (maxCoverSize / (1024 * 1024)).toFixed(2);
            const coverFileSizeMB = (coverFile.size / (1024 * 1024)).toFixed(2);
            onError(`封面文件大小 (${coverFileSizeMB}MB) 超过限制 (${maxCoverSizeMB}MB)，请压缩或更换文件`);
            return;
        }
    }

    // 构建 FormData
    const formData = new FormData();
    formData.append('file', musicFile);

    if (coverFile) {
        formData.append('cover', coverFile);
    }

    if (title.trim()) {
        formData.append('title', title.trim());
    }

    if (artist.trim()) {
        formData.append('artist', artist.trim());
    }

    if (order) {
        formData.append('order', order);
    }

    if (enabled !== undefined) {
        formData.append('enabled', enabled);
    }

    // 如果提供了 token，添加到 FormData 或 Header
    if (token) {
        formData.append('token', token);
    }

    // 调用开始回调
    onStart();

    // 创建 XHR 请求
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.timeout = timeout;

    // 上传进度
    xhr.upload.addEventListener('progress', function (ev) {
        if (ev.lengthComputable && onProgress) {
            const percent = (ev.loaded / ev.total) * 100;
            onProgress(percent);
        }
    });

    // 请求完成
    xhr.addEventListener('load', function () {
        onFinish();

        let data = {};
        try {
            data = JSON.parse(xhr.responseText || '{}');
        } catch (err) {
            onError('上传失败：服务端返回非 JSON 响应');
            return;
        }

        // 检查响应状态（200 或 201 都视为成功）
        if (xhr.status >= 200 && xhr.status < 300) {
            // 成功响应（200 或 201）
            // 注意：/music/upload 返回 200，/music/api/music 可能返回 201
            onSuccess(data);
        } else {
            // 错误响应
            let errorMsg = '上传失败';
            try {
                const contentType = xhr.getResponseHeader('Content-Type') || '';
                if (contentType.includes('application/json')) {
                    errorMsg = data.error || data.message || errorMsg;
                    
                    // 特殊处理 413 错误
                    if (xhr.status === 413) {
                        const maxSizeMB = (maxMusicSize / (1024 * 1024)).toFixed(2);
                        errorMsg = `文件过大：文件大小超过服务器限制 (${maxSizeMB}MB)`;
                        if (data.max_bytes) {
                            errorMsg += `。最大允许: ${(data.max_bytes / (1024 * 1024)).toFixed(2)}MB`;
                        }
                    }
                } else if (xhr.responseText && xhr.responseText.includes('<!DOCTYPE')) {
                    // HTML 错误页面
                    if (xhr.status === 413) {
                        const maxSizeMB = (maxMusicSize / (1024 * 1024)).toFixed(2);
                        errorMsg = `文件过大：文件大小超过服务器限制 (${maxSizeMB}MB)。请检查 Nginx 或其他代理服务器的 client_max_body_size 配置。`;
                    } else {
                        errorMsg = `上传失败: HTTP ${xhr.status} (服务器返回了错误页面)`;
                    }
                } else {
                    errorMsg = `上传失败: HTTP ${xhr.status}`;
                }
            } catch (e) {
                console.error('解析错误响应失败:', e);
                if (xhr.status === 413) {
                    const maxSizeMB = (maxMusicSize / (1024 * 1024)).toFixed(2);
                    errorMsg = `文件过大：文件大小超过服务器限制 (${maxSizeMB}MB)`;
                } else {
                    errorMsg = `上传失败: HTTP ${xhr.status}`;
                }
            }
            onError(errorMsg);
        }
    });

    // 网络错误
    xhr.addEventListener('error', function () {
        onFinish();
        onError('上传失败：网络错误或连接被重置');
    });

    // 超时
    xhr.addEventListener('timeout', function () {
        onFinish();
        onError('上传失败：上传超时');
    });

    // 发送请求（端点已在函数开头强制设置为 /music/upload）
    xhr.open('POST', endpoint, true);
    
    // 如果提供了 token，添加到 Header（优先使用 Header）
    if (token) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + token);
    }
    
    xhr.send(formData);
}

