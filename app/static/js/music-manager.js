/**
 * 音乐管理页面脚本
 */

class MusicManager {
    constructor() {
        this.adminToken = document.getElementById('adminToken').value;
        this.currentPage = 1;
        this.perPage = 20;
        this.currentQuery = '';
        this.selectedIds = new Set();
        this.hasShownEmptyMessage = false;
        
        this.init();
    }
    
    init() {
        // 绑定事件
        this.bindEvents();
        
        // 加载音乐列表
        this.loadMusicList();
    }
    
    bindEvents() {
        // 搜索
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.search();
            }
        });
        
        searchBtn.addEventListener('click', () => {
            this.search();
        });
        
        // 上传
        const submitUploadBtn = document.getElementById('submitUploadBtn');
        submitUploadBtn.addEventListener('click', () => {
            this.uploadMusic();
        });
        
        // 封面预览
        const coverFileInput = document.getElementById('coverFileInput');
        coverFileInput.addEventListener('change', (e) => {
            this.previewCover(e.target.files[0], 'coverPreview');
        });
        
        const editCoverInput = document.getElementById('editCoverInput');
        editCoverInput.addEventListener('change', (e) => {
            this.previewCover(e.target.files[0], 'editCoverPreview');
        });
        
        // 编辑
        const submitEditBtn = document.getElementById('submitEditBtn');
        submitEditBtn.addEventListener('click', () => {
            this.updateMusic();
        });
        
        // 批量删除
        const batchDeleteBtn = document.getElementById('batchDeleteBtn');
        batchDeleteBtn.addEventListener('click', () => {
            this.batchDelete();
        });
        
        // 导出 CSV
        const exportBtn = document.getElementById('exportBtn');
        exportBtn.addEventListener('click', () => {
            this.exportCSV();
        });
        
        // Modal 关闭时重置表单
        const uploadModal = document.getElementById('uploadModal');
        uploadModal.addEventListener('hidden.bs.modal', () => {
            document.getElementById('uploadForm').reset();
            document.getElementById('coverPreview').innerHTML = '';
            document.getElementById('uploadProgress').style.display = 'none';
        });
        
        const editModal = document.getElementById('editModal');
        editModal.addEventListener('hidden.bs.modal', () => {
            document.getElementById('editForm').reset();
            document.getElementById('editCoverPreview').innerHTML = '';
        });
    }
    
    async loadMusicList(page = 1, query = '') {
        try {
            this.currentPage = page;
            this.currentQuery = query;
            
            const params = new URLSearchParams({
                page: page,
                per_page: this.perPage
            });
            
            if (query) {
                params.append('q', query);
            }
            
            const response = await fetch(`/music/api/music?${params.toString()}`);
            const data = await response.json();
            
            // 检查响应状态
            if (!response.ok && response.status >= 500) {
                // 服务器错误（5xx），显示错误信息
                const errorMsg = data.error || `HTTP ${response.status}: 获取音乐列表失败`;
                throw new Error(errorMsg);
            }
            
            // 4xx 错误（如权限问题），如果有数据仍然显示
            if (!response.ok && (!data.items || data.items.length === 0)) {
                const errorMsg = data.error || `HTTP ${response.status}: 获取音乐列表失败`;
                this.showToast(errorMsg, 'error');
                this.renderMusicList([]);
                this.renderPagination({ total: 0, page: 1, per_page: 20, pages: 0 });
                return;
            }
            
            // 正常情况：显示数据（即使为空列表）
            this.renderMusicList(data.items || []);
            this.renderPagination(data);
            
            // 如果没有数据，显示提示（仅在第一次加载时）
            if (data.total === 0 && this.currentPage === 1 && !this.hasShownEmptyMessage) {
                this.showToast('暂无音乐文件，请上传音乐', 'info');
                this.hasShownEmptyMessage = true;
            }
            
        } catch (error) {
            console.error('加载音乐列表失败:', error);
            this.showToast('加载音乐列表失败: ' + error.message, 'error');
        }
    }
    
    renderMusicList(items) {
        const container = document.getElementById('musicListContainer');
        
        if (items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-music"></i>
                    <h4>暂无音乐</h4>
                    <p>点击"上传音乐"按钮添加音乐</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = items.map(music => `
            <div class="music-manager-card" data-music-id="${music.id}">
                <div class="d-flex align-items-center gap-3">
                    <div class="form-check">
                        <input class="form-check-input music-checkbox" 
                               type="checkbox" 
                               value="${music.id}"
                               onchange="musicManager.toggleSelect(${music.id})">
                    </div>
                    <div class="music-cover-thumb">
                        ${music.cover 
                            ? `<img src="${music.cover}" alt="封面" class="music-cover-thumb">`
                            : `<i class="fas fa-music"></i>`
                        }
                    </div>
                    <div class="music-info flex-grow-1">
                        <div class="music-title">${this.escapeHtml(music.title)}</div>
                        <div class="music-artist">${this.escapeHtml(music.artist)}</div>
                        <div class="music-meta">
                            <span>${this.formatFileSize(music.file_size)}</span>
                            ${music.duration ? `<span> • ${this.formatDuration(music.duration)}</span>` : ''}
                            <span> • ${this.formatDate(music.uploaded_at)}</span>
                        </div>
                    </div>
                    <div class="music-status ${music.enabled ? 'enabled' : 'disabled'}">
                        ${music.enabled ? '启用' : '禁用'}
                    </div>
                    <div class="music-actions">
                        <button class="btn btn-action btn-play" onclick="musicManager.playMusic(${music.id})" title="播放">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn btn-action btn-download" onclick="musicManager.downloadMusic(${music.id})" title="下载">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-action btn-edit" onclick="musicManager.editMusic(${music.id})" title="编辑">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-action btn-delete" onclick="musicManager.deleteMusic(${music.id})" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    renderPagination(data) {
        const pagination = document.getElementById('pagination');
        
        if (data.pages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // 上一页
        html += `
            <li class="page-item ${data.page === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="musicManager.loadMusicList(${data.page - 1}, '${this.currentQuery}'); return false;">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // 页码
        for (let i = 1; i <= data.pages; i++) {
            if (i === 1 || i === data.pages || (i >= data.page - 2 && i <= data.page + 2)) {
                html += `
                    <li class="page-item ${i === data.page ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="musicManager.loadMusicList(${i}, '${this.currentQuery}'); return false;">
                            ${i}
                        </a>
                    </li>
                `;
            } else if (i === data.page - 3 || i === data.page + 3) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        // 下一页
        html += `
            <li class="page-item ${data.page === data.pages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="musicManager.loadMusicList(${data.page + 1}, '${this.currentQuery}'); return false;">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        pagination.innerHTML = html;
    }
    
    search() {
        const query = document.getElementById('searchInput').value.trim();
        this.loadMusicList(1, query);
    }
    
    async uploadMusic() {
        const form = document.getElementById('uploadForm');
        const musicFileInput = document.getElementById('musicFileInput');
        const coverFileInput = document.getElementById('coverFileInput');
        const titleInput = document.getElementById('titleInput');
        const artistInput = document.getElementById('artistInput');
        const orderInput = document.getElementById('orderInput');
        const enabledInput = document.getElementById('enabledInput');
        const uploadProgress = document.getElementById('uploadProgress');
        const submitBtn = document.getElementById('submitUploadBtn');
        
        if (!musicFileInput.files[0]) {
            this.showToast('请选择音乐文件', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', musicFileInput.files[0]);
        
        if (coverFileInput.files[0]) {
            formData.append('cover', coverFileInput.files[0]);
        }
        
        if (titleInput.value.trim()) {
            formData.append('title', titleInput.value.trim());
        }
        
        if (artistInput.value.trim()) {
            formData.append('artist', artistInput.value.trim());
        }
        
        formData.append('order', orderInput.value || '0');
        formData.append('enabled', enabledInput.value);
        
        // 显示进度条
        uploadProgress.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner"></span> 上传中...';
        
        try {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    uploadProgress.querySelector('.progress-bar').style.width = percent + '%';
                }
            });
            
            xhr.addEventListener('load', () => {
                uploadProgress.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-upload"></i> 上传';
                
                if (xhr.status === 201) {
                    try {
                        const music = JSON.parse(xhr.responseText);
                        this.showToast('上传成功！', 'success');
                        
                        // 关闭 Modal
                        const uploadModal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
                        uploadModal.hide();
                        
                        // 刷新列表
                        this.loadMusicList(this.currentPage, this.currentQuery);
                        
                        // 通知播放器刷新
                        this.notifyPlayerRefresh();
                    } catch (e) {
                        console.error('解析响应失败:', e);
                        this.showToast('上传成功，但解析响应失败', 'warning');
                    }
                } else {
                    // 尝试解析错误响应
                    let errorMsg = '上传失败';
                    try {
                        const error = JSON.parse(xhr.responseText);
                        errorMsg = error.error || errorMsg;
                    } catch (e) {
                        // 如果不是 JSON，可能是 HTML 错误页面
                        if (xhr.responseText.includes('<!DOCTYPE')) {
                            errorMsg = `上传失败: HTTP ${xhr.status} (服务器返回了错误页面，可能是 CSRF 或权限问题)`;
                        } else {
                            errorMsg = `上传失败: HTTP ${xhr.status}`;
                        }
                    }
                    this.showToast(errorMsg, 'error');
                }
            });
            
            xhr.addEventListener('error', () => {
                this.showToast('上传失败: 网络错误', 'error');
                uploadProgress.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-upload"></i> 上传';
            });
            
            xhr.open('POST', '/music/api/music');
            xhr.setRequestHeader('Authorization', 'Bearer ' + this.adminToken);
            xhr.send(formData);
            
        } catch (error) {
            this.showToast('上传失败: ' + error.message, 'error');
            uploadProgress.style.display = 'none';
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-upload"></i> 上传';
        }
    }
    
    async editMusic(musicId) {
        try {
            const response = await fetch(`/music/api/music/${musicId}`, {
                headers: {
                    'Authorization': 'Bearer ' + this.adminToken
                }
            });
            
            if (!response.ok) {
                throw new Error('获取音乐信息失败');
            }
            
            const music = await response.json();
            
            // 填充表单
            document.getElementById('editMusicId').value = music.id;
            document.getElementById('editTitleInput').value = music.title;
            document.getElementById('editArtistInput').value = music.artist;
            document.getElementById('editOrderInput').value = music.order;
            document.getElementById('editEnabledInput').value = music.enabled ? 'true' : 'false';
            
            // 显示封面
            const coverPreview = document.getElementById('editCoverPreview');
            if (music.cover) {
                coverPreview.innerHTML = `<img src="${music.cover}" alt="封面" class="cover-preview">`;
            } else {
                coverPreview.innerHTML = '';
            }
            
            // 显示 Modal
            const editModal = new bootstrap.Modal(document.getElementById('editModal'));
            editModal.show();
            
        } catch (error) {
            this.showToast('获取音乐信息失败: ' + error.message, 'error');
        }
    }
    
    async updateMusic() {
        const musicId = document.getElementById('editMusicId').value;
        const titleInput = document.getElementById('editTitleInput');
        const artistInput = document.getElementById('editArtistInput');
        const orderInput = document.getElementById('editOrderInput');
        const enabledInput = document.getElementById('editEnabledInput');
        const coverFileInput = document.getElementById('editCoverInput');
        const submitBtn = document.getElementById('submitEditBtn');
        
        if (!titleInput.value.trim() || !artistInput.value.trim()) {
            this.showToast('请填写标题和艺术家', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('title', titleInput.value.trim());
        formData.append('artist', artistInput.value.trim());
        formData.append('order', orderInput.value || '0');
        formData.append('enabled', enabledInput.value);
        
        if (coverFileInput.files[0]) {
            formData.append('cover', coverFileInput.files[0]);
        }
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner"></span> 保存中...';
        
        try {
            const xhr = new XMLHttpRequest();
            
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    this.showToast('更新成功！', 'success');
                    
                    // 关闭 Modal
                    const editModal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                    editModal.hide();
                    
                    // 刷新列表
                    this.loadMusicList(this.currentPage, this.currentQuery);
                    
                    // 通知播放器刷新
                    this.notifyPlayerRefresh();
                } else {
                    const error = JSON.parse(xhr.responseText);
                    this.showToast('更新失败: ' + (error.error || '未知错误'), 'error');
                }
                
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-save"></i> 保存';
            });
            
            xhr.addEventListener('error', () => {
                this.showToast('更新失败: 网络错误', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-save"></i> 保存';
            });
            
            xhr.open('PUT', `/music/api/music/${musicId}`);
            xhr.setRequestHeader('Authorization', 'Bearer ' + this.adminToken);
            xhr.send(formData);
            
        } catch (error) {
            this.showToast('更新失败: ' + error.message, 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-save"></i> 保存';
        }
    }
    
    async deleteMusic(musicId) {
        if (!confirm('确定要删除这首音乐吗？此操作不可恢复。')) {
            return;
        }
        
        try {
            const response = await fetch(`/music/api/music/${musicId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': 'Bearer ' + this.adminToken
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || '删除失败');
            }
            
            this.showToast('删除成功！', 'success');
            
            // 刷新列表
            this.loadMusicList(this.currentPage, this.currentQuery);
            
            // 通知播放器刷新
            this.notifyPlayerRefresh();
            
        } catch (error) {
            this.showToast('删除失败: ' + error.message, 'error');
        }
    }
    
    async batchDelete() {
        if (this.selectedIds.size === 0) {
            this.showToast('请选择要删除的音乐', 'warning');
            return;
        }
        
        if (!confirm(`确定要删除选中的 ${this.selectedIds.size} 首音乐吗？此操作不可恢复。`)) {
            return;
        }
        
        try {
            const response = await fetch('/music/api/music/batch-delete', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + this.adminToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ids: Array.from(this.selectedIds)
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || '批量删除失败');
            }
            
            const result = await response.json();
            this.showToast(`成功删除 ${result.total_deleted} 首音乐`, 'success');
            
            // 清空选择
            this.selectedIds.clear();
            this.updateBatchDeleteButton();
            
            // 刷新列表
            this.loadMusicList(this.currentPage, this.currentQuery);
            
            // 通知播放器刷新
            this.notifyPlayerRefresh();
            
        } catch (error) {
            this.showToast('批量删除失败: ' + error.message, 'error');
        }
    }
    
    toggleSelect(musicId) {
        const checkbox = document.querySelector(`input[type="checkbox"][value="${musicId}"]`);
        const card = checkbox.closest('.music-manager-card');
        
        if (checkbox.checked) {
            this.selectedIds.add(musicId);
            card.classList.add('selected');
        } else {
            this.selectedIds.delete(musicId);
            card.classList.remove('selected');
        }
        
        this.updateBatchDeleteButton();
    }
    
    updateBatchDeleteButton() {
        const batchDeleteBtn = document.getElementById('batchDeleteBtn');
        if (this.selectedIds.size > 0) {
            batchDeleteBtn.style.display = 'inline-block';
            batchDeleteBtn.innerHTML = `<i class="fas fa-trash"></i> 批量删除 (${this.selectedIds.size})`;
        } else {
            batchDeleteBtn.style.display = 'none';
        }
    }
    
    playMusic(musicId) {
        // 通知播放器播放指定音乐
        if (window.embeddedMusicPlayer) {
            window.embeddedMusicPlayer.loadTrackById(musicId);
            window.embeddedMusicPlayer.audio.play();
        } else {
            this.showToast('播放器未加载', 'warning');
        }
    }
    
    downloadMusic(musicId) {
        const url = `/music/api/music/download/${musicId}?attachment=true`;
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', '');
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    async exportCSV() {
        try {
            const response = await fetch(`/music/api/music?page=1&per_page=1000${this.currentQuery ? '&q=' + encodeURIComponent(this.currentQuery) : ''}`);
            if (!response.ok) {
                throw new Error('获取音乐列表失败');
            }
            
            const data = await response.json();
            
            // 生成 CSV
            const headers = ['ID', '标题', '艺术家', '文件名', 'URL', '封面', '时长', '文件大小', '排序', '状态', '上传时间'];
            const rows = data.items.map(music => [
                music.id,
                music.title,
                music.artist,
                music.filename,
                music.url,
                music.cover || '',
                music.duration || '',
                music.file_size || '',
                music.order,
                music.enabled ? '启用' : '禁用',
                music.uploaded_at
            ]);
            
            const csvContent = [
                headers.join(','),
                ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
            ].join('\n');
            
            // 下载 CSV
            const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `music_list_${new Date().toISOString().split('T')[0]}.csv`;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showToast('CSV 导出成功！', 'success');
            
        } catch (error) {
            this.showToast('导出失败: ' + error.message, 'error');
        }
    }
    
    previewCover(file, previewId) {
        if (!file) {
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById(previewId);
            preview.innerHTML = `<img src="${e.target.result}" alt="封面预览" class="cover-preview">`;
        };
        reader.readAsDataURL(file);
    }
    
    notifyPlayerRefresh() {
        // 通知播放器刷新列表
        localStorage.setItem('musicPlaylistRefresh', Date.now().toString());
        localStorage.removeItem('musicPlaylistRefresh');
        
        // 通过 postMessage 通知
        window.postMessage({
            type: 'refreshPlaylist',
            source: 'musicManager'
        }, '*');
    }
    
    // 工具函数
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatFileSize(bytes) {
        if (!bytes) return '未知';
        const mb = bytes / (1024 * 1024);
        return mb.toFixed(2) + ' MB';
    }
    
    formatDuration(seconds) {
        if (!seconds) return '未知';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    formatDate(dateString) {
        if (!dateString) return '未知';
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>${message}</span>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // 3秒后自动移除
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// 初始化
let musicManager;

// 初始化音乐管理器（可被外部调用）
function initMusicManager() {
    // 如果已经存在实例，先销毁
    if (musicManager) {
        // 清理事件监听器（如果需要）
        musicManager = null;
    }
    
    // 检查必要的元素是否存在
    const adminToken = document.getElementById('adminToken');
    if (!adminToken) {
        console.warn('音乐管理页面元素未找到，跳过初始化');
        return;
    }
    
    // 创建新实例
    musicManager = new MusicManager();
    
    // 将实例暴露到全局，方便调试
    window.musicManager = musicManager;
}

// DOMContentLoaded 时初始化（首次页面加载）
document.addEventListener('DOMContentLoaded', () => {
    initMusicManager();
});

// 监听页面加载事件（AJAX 导航后触发）
window.addEventListener('pageLoaded', (event) => {
    // 延迟一点时间，确保 DOM 已更新
    setTimeout(() => {
        initMusicManager();
    }, 100);
});

