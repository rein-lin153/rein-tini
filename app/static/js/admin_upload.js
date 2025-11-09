/**
 * 管理员音乐上传脚本
 */

document.addEventListener('DOMContentLoaded', function() {
    const musicUploadArea = document.getElementById('musicUploadArea');
    const coverUploadArea = document.getElementById('coverUploadArea');
    const musicFileInput = document.getElementById('musicFile');
    const coverFileInput = document.getElementById('coverFile');
    const musicFileName = document.getElementById('musicFileName');
    const coverPreview = document.getElementById('coverPreview');
    const uploadForm = document.getElementById('musicUploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadResult = document.getElementById('uploadResult');
    const musicProgressContainer = document.getElementById('musicProgressContainer');
    const musicProgressBar = document.getElementById('musicProgressBar');
    const adminToken = document.getElementById('adminToken').value;
    
    // 音乐文件选择
    musicFileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // 验证文件类型
            if (!file.name.toLowerCase().endsWith('.mp3')) {
                showResult('仅支持 MP3 格式', 'danger');
                musicFileInput.value = '';
                return;
            }
            
            // 验证文件大小 (25MB)
            if (file.size > 25 * 1024 * 1024) {
                showResult('文件过大，最大 25MB', 'danger');
                musicFileInput.value = '';
                return;
            }
            
            musicFileName.innerHTML = `
                <i class="fas fa-check-circle text-success"></i> 
                <strong>${file.name}</strong> 
                <span class="text-muted">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            `;
        }
    });
    
    // 封面文件选择
    coverFileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // 验证文件类型
            const allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp'];
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(fileExt)) {
                showResult('封面仅支持 JPG, PNG, WEBP 格式', 'danger');
                coverFileInput.value = '';
                return;
            }
            
            // 验证文件大小 (2MB)
            if (file.size > 2 * 1024 * 1024) {
                showResult('封面文件过大，最大 2MB', 'danger');
                coverFileInput.value = '';
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                coverPreview.innerHTML = `
                    <img src="${e.target.result}" class="cover-preview" alt="封面预览">
                    <p class="text-muted small mt-2">${file.name}</p>
                `;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // 拖拽上传
    [musicUploadArea, coverUploadArea].forEach(area => {
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', function(e) {
            e.preventDefault();
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                if (area === musicUploadArea) {
                    musicFileInput.files = files;
                    musicFileInput.dispatchEvent(new Event('change'));
                } else {
                    coverFileInput.files = files;
                    coverFileInput.dispatchEvent(new Event('change'));
                }
            }
        });
    });
    
    // 表单提交
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!musicFileInput.files[0]) {
            showResult('请选择音乐文件', 'danger');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', musicFileInput.files[0]);
        
        if (coverFileInput.files[0]) {
            formData.append('cover', coverFileInput.files[0]);
        }
        
        const title = document.getElementById('songTitle').value.trim();
        const artist = document.getElementById('songArtist').value.trim();
        
        if (title) {
            formData.append('title', title);
        }
        if (artist) {
            formData.append('artist', artist);
        }
        
        // 显示上传进度
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 上传中...';
        musicProgressContainer.style.display = 'block';
        musicProgressBar.style.width = '0%';
        
        // 使用 XMLHttpRequest 来显示上传进度
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                musicProgressBar.style.width = percentComplete + '%';
            }
        });
        
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.id) {
                        showResult('上传成功！播放列表已更新。', 'success');
                        // 重置表单
                        uploadForm.reset();
                        musicFileName.innerHTML = '';
                        coverPreview.innerHTML = '';
                        musicProgressContainer.style.display = 'none';
                        
                        // 通知播放器刷新列表
                        notifyPlayerRefresh();
                    } else {
                        showResult('上传失败：' + (response.error || '未知错误'), 'danger');
                    }
                } catch (e) {
                    showResult('上传失败：服务器响应格式错误', 'danger');
                }
            } else {
                try {
                    const response = JSON.parse(xhr.responseText);
                    showResult('上传失败：' + (response.error || '服务器错误'), 'danger');
                } catch (e) {
                    showResult('上传失败：服务器错误 (HTTP ' + xhr.status + ')', 'danger');
                }
            }
            
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-upload"></i> 上传音乐';
            musicProgressContainer.style.display = 'none';
        });
        
        xhr.addEventListener('error', function() {
            showResult('上传失败：网络错误', 'danger');
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-upload"></i> 上传音乐';
            musicProgressContainer.style.display = 'none';
        });
        
        xhr.open('POST', '/music/upload');
        xhr.setRequestHeader('Authorization', 'Bearer ' + adminToken);
        xhr.send(formData);
    });
    
    function showResult(message, type) {
        uploadResult.textContent = message;
        uploadResult.className = 'alert alert-' + type + ' mt-4';
        uploadResult.style.display = 'block';
        
        setTimeout(function() {
            uploadResult.style.display = 'none';
        }, 5000);
    }
    
    function notifyPlayerRefresh() {
        // 通过 localStorage 事件通知播放器刷新
        const event = new Event('storage');
        localStorage.setItem('musicPlaylistRefresh', Date.now().toString());
        localStorage.removeItem('musicPlaylistRefresh');
        
        // 通过 postMessage 通知播放器窗口（如果打开）
        window.postMessage({
            type: 'refreshPlaylist',
            source: 'adminUpload'
        }, '*');
        
        // 如果播放器窗口存在，直接通知
        if (window.musicPlayerWindow && !window.musicPlayerWindow.closed) {
            window.musicPlayerWindow.postMessage({
                type: 'refreshPlaylist',
                source: 'adminUpload'
            }, '*');
        }
    }
});

