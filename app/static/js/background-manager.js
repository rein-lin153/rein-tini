/**
 * 背景管理页面脚本
 */

class BackgroundManager {
    constructor() {
        this.adminToken = document.getElementById('adminToken').value;
        this.init();
    }
    
    init() {
        // 绑定事件
        this.bindEvents();
        
        // 加载背景列表
        this.loadBackgrounds();
        this.loadDefaultBackground();
    }
    
    bindEvents() {
        // 上传背景
        const submitBtn = document.getElementById('submitBackgroundUploadBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => {
                this.uploadBackground();
            });
        }
        
        // 背景预览
        const fileInput = document.getElementById('backgroundFileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.previewBackground(e.target.files[0]);
            });
        }
        
        // Modal 关闭时重置表单
        const uploadModal = document.getElementById('uploadBackgroundModal');
        if (uploadModal) {
            uploadModal.addEventListener('hidden.bs.modal', () => {
                document.getElementById('uploadBackgroundForm').reset();
                document.getElementById('backgroundPreview').innerHTML = '';
                document.getElementById('backgroundUploadProgress').style.display = 'none';
            });
        }
    }
    
    async loadBackgrounds() {
        try {
            const response = await fetch('/api/backgrounds');
            const data = await response.json();
            
            if (!response.ok) {
                // 如果是 503 错误，说明表不存在，显示友好提示
                if (response.status === 503) {
                    console.warn('数据库表不存在，需要初始化');
                    this.showToast('数据库表不存在，请运行: python scripts/init_db.py', 'warning');
                } else {
                    throw new Error(data.error || '获取背景列表失败');
                }
            }
            
            this.renderBackgroundList(data.backgrounds || []);
            
        } catch (error) {
            console.error('加载背景列表失败:', error);
            this.showToast('加载背景列表失败: ' + error.message, 'error');
            // 显示空列表
            const container = document.getElementById('backgroundListContainer');
            if (container) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-image"></i>
                        <p>加载失败，请刷新页面重试</p>
                    </div>
                `;
            }
        }
    }
    
    async loadDefaultBackground() {
        try {
            const response = await fetch('/api/backgrounds/default');
            const data = await response.json();
            
            // 即使响应不是 200，也要尝试渲染（可能是 200 但返回空数据）
            if (response.ok || response.status === 200) {
                this.renderDefaultBackground(data);
            } else {
                throw new Error(data.error || '获取默认背景失败');
            }
            
        } catch (error) {
            console.error('加载默认背景失败:', error);
            const preview = document.getElementById('defaultBackgroundPreview');
            if (preview) {
                preview.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-image"></i>
                        <p>未设置默认背景</p>
                    </div>
                `;
            }
        }
    }
    
    renderBackgroundList(backgrounds) {
        const container = document.getElementById('backgroundListContainer');
        if (!container) return;
        
        if (backgrounds.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-image"></i>
                    <h4>暂无背景</h4>
                    <p>点击"上传背景"按钮添加背景</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = backgrounds.map(bg => `
            <div class="background-item ${bg.is_default ? 'is-default' : ''}" data-bg-id="${bg.id}">
                <div class="background-item-image">
                    <img src="${bg.url}" alt="背景" loading="lazy">
                    ${bg.is_default ? '<div class="default-badge"><i class="fas fa-star"></i> 默认</div>' : ''}
                </div>
                <div class="background-item-info">
                    <div class="background-item-name">${this.escapeHtml(bg.filename)}</div>
                    <div class="background-item-meta">
                        ${bg.width && bg.height ? `<span>${bg.width} × ${bg.height}</span>` : ''}
                        ${bg.file_size ? `<span> • ${this.formatFileSize(bg.file_size)}</span>` : ''}
                        <span> • ${this.formatDate(bg.uploaded_at)}</span>
                    </div>
                </div>
                <div class="background-item-actions">
                    ${!bg.is_default ? `
                        <button class="btn btn-sm btn-pink-gradient" onclick="backgroundManager.setDefault(${bg.id})" title="设为默认">
                            <i class="fas fa-star"></i> 设为默认
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-danger" onclick="backgroundManager.deleteBackground(${bg.id})" title="删除">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderDefaultBackground(background) {
        const preview = document.getElementById('defaultBackgroundPreview');
        if (!preview) return;
        
        if (!background || !background.url) {
            preview.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-image"></i>
                    <p>未设置默认背景</p>
                </div>
            `;
            return;
        }
        
        preview.innerHTML = `
            <div class="default-background-display">
                <img src="${background.url}" alt="默认背景" class="default-background-image">
                <div class="default-background-info">
                    <div class="default-background-name">${this.escapeHtml(background.filename)}</div>
                    ${background.width && background.height ? `
                        <div class="default-background-meta">${background.width} × ${background.height}</div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    async uploadBackground() {
        const fileInput = document.getElementById('backgroundFileInput');
        const submitBtn = document.getElementById('submitBackgroundUploadBtn');
        const progressBar = document.getElementById('backgroundUploadProgress');
        
        if (!fileInput.files[0]) {
            this.showToast('请选择背景图片', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        // 显示进度条
        progressBar.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 上传中...';
        
        try {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    progressBar.querySelector('.progress-bar').style.width = percent + '%';
                }
            });
            
            xhr.addEventListener('load', () => {
                progressBar.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-upload"></i> 上传';
                
                if (xhr.status === 201) {
                    try {
                        const background = JSON.parse(xhr.responseText);
                        this.showToast('上传成功！', 'success');
                        
                        // 关闭 Modal
                        const uploadModal = bootstrap.Modal.getInstance(document.getElementById('uploadBackgroundModal'));
                        uploadModal.hide();
                        
                        // 刷新列表
                        this.loadBackgrounds();
                        this.loadDefaultBackground();
                        
                        // 更新页面背景（如果当前是默认背景）
                        this.updatePageBackground();
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
                            errorMsg = `上传失败: HTTP ${xhr.status} (服务器返回了错误页面)`;
                        } else {
                            errorMsg = `上传失败: HTTP ${xhr.status}`;
                        }
                    }
                    this.showToast(errorMsg, 'error');
                }
            });
            
            xhr.addEventListener('error', () => {
                this.showToast('上传失败: 网络错误', 'error');
                progressBar.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-upload"></i> 上传';
            });
            
            xhr.open('POST', '/api/backgrounds');
            xhr.setRequestHeader('Authorization', 'Bearer ' + this.adminToken);
            xhr.send(formData);
            
        } catch (error) {
            this.showToast('上传失败: ' + error.message, 'error');
            progressBar.style.display = 'none';
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-upload"></i> 上传';
        }
    }
    
    async setDefault(bgId) {
        if (!confirm('确定要将此背景设为默认背景吗？')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/backgrounds/${bgId}/default`, {
                method: 'PUT',
                headers: {
                    'Authorization': 'Bearer ' + this.adminToken
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || '设置失败');
            }
            
            const background = await response.json();
            this.showToast('已设置为默认背景！', 'success');
            
            // 刷新列表和预览
            this.loadBackgrounds();
            this.loadDefaultBackground();
            
            // 更新页面背景
            this.updatePageBackground();
            
        } catch (error) {
            this.showToast('设置失败: ' + error.message, 'error');
        }
    }
    
    async deleteBackground(bgId) {
        if (!confirm('确定要删除此背景吗？此操作不可恢复。')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/backgrounds/${bgId}`, {
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
            
            // 刷新列表和预览
            this.loadBackgrounds();
            this.loadDefaultBackground();
            
        } catch (error) {
            this.showToast('删除失败: ' + error.message, 'error');
        }
    }
    
    previewBackground(file) {
        if (!file) {
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('backgroundPreview');
            preview.innerHTML = `
                <div class="background-preview-image">
                    <img src="${e.target.result}" alt="预览" class="img-fluid rounded">
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }
    
    async updatePageBackground() {
        // 更新页面背景（如果当前是默认背景）
        try {
            const response = await fetch('/api/backgrounds/default');
            if (response.ok) {
                const background = await response.json();
                if (background && background.url) {
                    // 可以在这里添加更新页面背景的逻辑
                    // 例如：document.body.style.backgroundImage = `url(${background.url})`;
                }
            }
        } catch (error) {
            console.error('更新页面背景失败:', error);
        }
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
let backgroundManager;

// 初始化背景管理器（可被外部调用）
function initBackgroundManager() {
    // 检查必要的元素是否存在
    const adminToken = document.getElementById('adminToken');
    const backgroundPanel = document.getElementById('background-panel');
    
    if (!adminToken || !backgroundPanel) {
        console.warn('背景管理页面元素未找到，跳过初始化');
        return;
    }
    
    // 如果已经存在实例，先销毁
    if (backgroundManager) {
        backgroundManager = null;
    }
    
    // 创建新实例
    backgroundManager = new BackgroundManager();
    
    // 将实例暴露到全局，方便调试
    window.backgroundManager = backgroundManager;
}

// DOMContentLoaded 时初始化（首次页面加载）
document.addEventListener('DOMContentLoaded', () => {
    initBackgroundManager();
});

// 监听页面加载事件（AJAX 导航后触发）
window.addEventListener('pageLoaded', (event) => {
    // 延迟一点时间，确保 DOM 已更新
    setTimeout(() => {
        initBackgroundManager();
    }, 100);
});

// 监听标签页切换事件
document.addEventListener('DOMContentLoaded', () => {
    const backgroundTab = document.getElementById('background-tab');
    if (backgroundTab) {
        backgroundTab.addEventListener('shown.bs.tab', () => {
            // 切换到背景管理标签页时，初始化或刷新
            setTimeout(() => {
                if (!backgroundManager) {
                    initBackgroundManager();
                } else {
                    backgroundManager.loadBackgrounds();
                    backgroundManager.loadDefaultBackground();
                }
            }, 100);
        });
    }
});

